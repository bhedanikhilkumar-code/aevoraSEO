"""Comprehensive production hardening, adversarial security, and release tests for AevoraSEO."""

import csv
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from aevoraseo.cli import main as cli_main
from aevoraseo.engine import csv_value, write_csv, parse_sitemap
from aevoraseo.network import Config, addresses, normalize_url
from aevoraseo.unified_report import sanitize_csv_cell as unified_sanitize
from aevoraseo.entity.reporter import sanitize_csv_cell as entity_sanitize
from aevoraseo.search.comparison import sanitize_csv_cell as search_sanitize
from aevoraseo.optimization.reporter import sanitize_csv_cell as opt_sanitize
from aevoraseo.review import compare
from aevoraseo.workflow import run_operational_diagnostics, track_progress


# ============================================================================
# 1. Adversarial Security: Formula Injection Tests Across All Subsystems
# ============================================================================

@pytest.mark.parametrize(
    "payload",
    [
        "=1+1",
        "=cmd|' /C calc'!A0",
        "+100",
        "-50",
        "@SUM(A1:A10)",
        "\tmalicious_tab",
        "\rmalicious_cr",
        " =leading_space_formula",
        " +leading_space_formula",
    ],
)
def test_csv_formula_injection_defense_across_subsystems(payload):
    """Verify that every subsystem CSV sanitizer neutralizes spreadsheet execution triggers."""
    # 1. Engine CSV value
    sanitized_engine = csv_value(payload)
    assert sanitized_engine.lstrip().startswith("'") or not sanitized_engine.lstrip().startswith(("=", "+", "-", "@", "\t", "\r"))

    # 2. Unified Report CSV sanitizer
    sanitized_unified = unified_sanitize(payload)
    assert sanitized_unified.startswith("'")

    # 3. Entity Reporter CSV sanitizer
    sanitized_entity = entity_sanitize(payload)
    assert sanitized_entity.startswith("'")

    # 4. Search Reporter CSV sanitizer
    sanitized_search = search_sanitize(payload)
    assert sanitized_search.startswith("'")

    # 5. Optimization Reporter CSV sanitizer
    sanitized_opt = opt_sanitize(payload)
    assert sanitized_opt.startswith("'")


def test_write_csv_neutralizes_malicious_rows():
    """Verify engine write_csv outputs neutralized cells."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = Path(tmpdir) / "output.csv"
        rows = [
            {"name": "=cmd|' /C calc'!A0", "value": "+123", "normal": "safe text"},
            {"name": "@IMPORT('http://evil.com')", "value": "-999", "normal": "\tsecret"},
        ]
        write_csv(csv_file, ["name", "value", "normal"], rows)

        content = csv_file.read_text(encoding="utf-8-sig")
        lines = content.splitlines()
        assert len(lines) == 3

        # Read back with standard csv reader
        with csv_file.open(encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            read_rows = list(reader)

        assert read_rows[0]["name"].startswith("'")
        assert read_rows[0]["value"].startswith("'")
        assert read_rows[1]["name"].startswith("'")
        assert read_rows[1]["value"].startswith("'")


def test_comparison_csv_neutralizes_malicious_changes():
    """Verify comparison.csv neutralizes formula injection in page URLs and diff fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        b_dir = base / "before"
        a_dir = base / "after"
        out_dir = base / "out"
        b_dir.mkdir()
        a_dir.mkdir()

        # Seed summary.json with seed and snapshot_id
        (b_dir / "summary.json").write_text(
            json.dumps({"seed": "https://example.com", "snapshot_id": "snap-1", "pages": 1}),
            encoding="utf-8",
        )
        (a_dir / "summary.json").write_text(
            json.dumps({"seed": "https://example.com", "snapshot_id": "snap-2", "pages": 1}),
            encoding="utf-8",
        )
        (b_dir / "issues.json").write_text("[]", encoding="utf-8")
        (a_dir / "issues.json").write_text("[]", encoding="utf-8")

        # Seed pages with malicious diff contents
        (b_dir / "pages.jsonl").write_text(
            json.dumps({"url": "https://example.com/test", "status": 200, "data": {"title": "Normal Title"}}) + "\n",
            encoding="utf-8",
        )
        (a_dir / "pages.jsonl").write_text(
            json.dumps({"url": "https://example.com/test", "status": 200, "data": {"title": "=CMD|' /C calc'!A0"}}) + "\n",
            encoding="utf-8",
        )

        compare(b_dir, a_dir, out_dir, format="csv")

        csv_path = out_dir / "comparison.csv"
        assert csv_path.is_file()
        content = csv_path.read_text(encoding="utf-8-sig")
        # Ensure the malicious title has been prefixed with single quote
        assert "'=CMD" in content


# ============================================================================
# 2. Network Security: SSRF, Private IP, and Scheme Blocking
# ============================================================================

@pytest.mark.parametrize(
    "private_url",
    [
        "http://127.0.0.1",
        "http://10.0.0.1",
        "http://192.168.1.100",
        "http://172.16.0.1",
        "http://169.254.169.254",  # AWS/GCP metadata service
        "http://localhost",
    ],
)
def test_private_ip_blocking_in_network(private_url):
    """Verify that private and loopback IPs are blocked by default with SSRF defense."""
    with pytest.raises(ValueError, match="private_or_nonpublic_address"):
        addresses(private_url, allow_private=False)


@pytest.mark.parametrize(
    "invalid_url",
    [
        "file:///etc/passwd",
        "gopher://evil.com/",
        "ftp://example.com/file",
        "javascript:alert(1)",
        "http://",
        "not-a-url",
    ],
)
def test_config_rejects_unsafe_schemes_and_invalid_urls(invalid_url):
    """Verify Config rejects non-http/https schemes and malformed URLs."""
    with pytest.raises(ValueError):
        Config(url=invalid_url)


# ============================================================================
# 3. XML / Sitemap Security & XXE Protection
# ============================================================================

def test_parse_sitemap_rejects_xxe_and_dtd():
    """Verify parse_sitemap blocks XXE entity injection and DOCTYPE declarations."""
    xxe_payload = b"""<?xml version="1.0"?>
    <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>&xxe;</loc></url>
    </urlset>"""

    with pytest.raises(ValueError, match="Sitemap DTD/entities are not supported"):
        parse_sitemap(xxe_payload)


def test_parse_sitemap_handles_null_bytes_and_valid_xml():
    """Verify parse_sitemap sanitizes null bytes and extracts URLs safely."""
    valid_payload = b"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://example.com/page-1\x00</loc></url>
      <url><loc>https://example.com/page-2</loc></url>
    </urlset>"""

    kind, urls = parse_sitemap(valid_payload)
    assert kind == "urlset"
    assert len(urls) == 2
    assert urls[0]["loc"] == "https://example.com/page-1"
    assert urls[1]["loc"] == "https://example.com/page-2"


# ============================================================================
# 4. SQLite Concurrency & Windows Connection Cleanups
# ============================================================================

def test_sqlite_connection_hygiene_and_immediate_file_release():
    """Verify that SQLite files can be immediately unlinked/reopened without locking errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_concurrency.sqlite3"

        # Create, populate, and close cleanly
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, title TEXT)")
            conn.execute("INSERT INTO records VALUES (1, 'Initial Record')")
            conn.commit()
        finally:
            conn.close()

        # Operational diagnostics checks integrity
        diag = run_operational_diagnostics(Path(tmpdir))
        assert diag["status"] == "HEALTHY"
        assert diag["databases_inspected"] == 1
        assert diag["database_integrity"][0]["integrity"] == "PASS"

        # Immediately delete the file: on Windows, this would fail with PermissionError if connection was leaked
        db_path.unlink()
        assert not db_path.exists()


# ============================================================================
# 5. Performance & Scalability: Multi-Snapshot Chronological Trajectory
# ============================================================================

def test_track_progress_ten_snapshots_performance():
    """Verify tracking progress across 10 chronological snapshots operates smoothly and accurately."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        snap_dirs = []

        # Build real minimal crawl snapshots matching the schema consumed by
        # generate_unified_report().  Each snapshot has progressively fewer 5xx
        # pages so the unified technical score improves chronologically.
        for i in range(10):
            s_dir = base / f"snap_{i:02d}"
            s_dir.mkdir()
            conn = sqlite3.connect(str(s_dir / "crawl.sqlite3"))
            try:
                cur = conn.cursor()
                cur.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
                cur.execute(
                    "INSERT INTO meta VALUES ('config', ?)",
                    (json.dumps({"config": {"start_urls": ["https://scaling-test.com"]}}),),
                )
                cur.execute(
                    "CREATE TABLE pages ("
                    "url TEXT PRIMARY KEY, status_code INTEGER, robots_noindex INTEGER"
                    ")"
                )
                cur.execute(
                    "INSERT INTO pages VALUES ('https://scaling-test.com', 200, 0)"
                )
                # Errors decrease from 9 down to 0, producing a strictly
                # improving technical score in the unified report.
                for err_idx in range(9 - i):
                    cur.execute(
                        "INSERT INTO pages VALUES (?, 500, 0)",
                        (f"https://scaling-test.com/err-{err_idx}",),
                    )
                conn.commit()
            finally:
                conn.close()
            snap_dirs.append(s_dir)

        progress = track_progress(snap_dirs)
        assert progress["snapshots_evaluated"] == 10
        assert len(progress["timeline"]) == 10
        assert progress["trajectory"] == "IMPROVING"
        assert progress["score_delta"] is not None
        assert progress["score_delta"] > 0


# ============================================================================
# 6. CLI Parity Smoke Tests Across Subsystems
# ============================================================================

@pytest.mark.parametrize(
    "subcommand_args",
    [
        ["--help"],
        ["doctor"],
        ["report", "--help"],
        ["audit-verify", "--help"],
        ["progress", "--help"],
        ["agent", "list", "--format", "json"],
        ["agent", "detect", "--format", "json"],
    ],
)
def test_cli_subcommand_dispatch_smoke(subcommand_args):
    """Verify that all core and operational subcommands execute without unhandled exceptions."""
    try:
        ret = cli_main(subcommand_args)
        assert ret in (0, None)
    except SystemExit as exc:
        assert exc.code == 0
