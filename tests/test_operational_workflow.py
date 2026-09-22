"""Unit tests for operational workflow, acceptance verification, and progress tracking."""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from aevoraseo.workflow import (
    verify_audit_acceptance,
    track_progress,
    run_operational_diagnostics,
)
from aevoraseo.cli import main as cli_main


def _create_mock_crawl(crawl_dir: Path, target: str = "https://example.com", server_errors: int = 0):
    crawl_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(crawl_dir / "crawl.sqlite3"))
    cur = conn.cursor()
    cur.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    cur.execute(
        "INSERT INTO meta VALUES ('config', ?)",
        (json.dumps({"config": {"start_urls": [target]}}),),
    )
    cur.execute("CREATE TABLE pages (url TEXT, status_code INTEGER, robots_noindex INTEGER)")
    cur.execute("INSERT INTO pages VALUES (?, 200, 0)", (target,))
    for i in range(server_errors):
        cur.execute("INSERT INTO pages VALUES (?, 500, 0)", (f"{target}/error-{i}",))
    conn.commit()
    conn.close()


def test_verify_audit_acceptance_resolved_and_unresolved():
    with tempfile.TemporaryDirectory() as tmpdir:
        crawl_dir = Path(tmpdir) / "crawl"
        _create_mock_crawl(crawl_dir, "https://example.com", server_errors=1)

        # Prior audit had 2 issues:
        # 1. "Internal Server Errors" -> still exists in crawl (500 error)
        # 2. "Missing Meta Descriptions" -> not flagged as an issue by default in empty mock
        prior_audit = {
            "target": "https://example.com",
            "created_at": "2026-09-20T12:00:00Z",
            "acceptance_checklist": [
                {
                    "issue_id": "CRIT-001",
                    "title": "Internal Server Errors (5xx)",
                    "priority": "P0",
                    "acceptance_criteria": "Zero 5xx responses",
                },
                {
                    "issue_id": "WARN-002",
                    "title": "Broken External Affiliate Redirects",
                    "priority": "P1",
                    "acceptance_criteria": "Resolve 301 redirect chains",
                },
            ],
        }

        result = verify_audit_acceptance(prior_audit, crawl_dir)
        assert result["total_items"] == 2
        assert result["resolved_count"] == 1
        assert result["unresolved_count"] == 1
        assert result["overall_status"] == "PARTIAL_PROGRESS"

        statuses = {item["id"]: item["status"] for item in result["items"]}
        assert statuses["CRIT-001"] == "UNRESOLVED"
        assert statuses["WARN-002"] == "RESOLVED"


def test_verify_audit_acceptance_all_resolved():
    with tempfile.TemporaryDirectory() as tmpdir:
        crawl_dir = Path(tmpdir) / "crawl"
        _create_mock_crawl(crawl_dir, "https://example.com", server_errors=0)

        prior_audit = {
            "acceptance_checklist": [
                {
                    "issue_id": "ISSUE-1",
                    "title": "Legacy HTTP URLs",
                    "priority": "P1",
                    "acceptance_criteria": "Migrate to HTTPS",
                }
            ]
        }

        result = verify_audit_acceptance(prior_audit, crawl_dir)
        assert result["total_items"] == 1
        assert result["resolved_count"] == 1
        assert result["unresolved_count"] == 0
        assert result["overall_status"] == "ALL_RESOLVED"


def test_verify_audit_acceptance_fallbacks():
    with tempfile.TemporaryDirectory() as tmpdir:
        crawl_dir = Path(tmpdir) / "crawl"
        _create_mock_crawl(crawl_dir, "https://example.com")

        # Test prioritized_issues fallback
        audit_with_issues = {
            "prioritized_issues": [
                {
                    "id": "P0-01",
                    "title": "Fix Database Timeout",
                    "priority": "P0",
                    "acceptance_check": "No 504 timeouts",
                }
            ]
        }
        res1 = verify_audit_acceptance(audit_with_issues, crawl_dir)
        assert res1["total_items"] == 1
        assert res1["resolved_count"] == 1

        # Test findings fallback
        audit_with_findings = {
            "findings": [
                {
                    "code": "MISSING_H1",
                    "title": "Missing Primary H1",
                    "priority": "P1",
                    "acceptance_check": "Add H1 tag",
                }
            ]
        }
        res2 = verify_audit_acceptance(audit_with_findings, crawl_dir)
        assert res2["total_items"] == 1

        # Test non-existent crawl directory
        with pytest.raises(ValueError):
            verify_audit_acceptance(audit_with_issues, Path(tmpdir) / "nonexistent")


def test_track_progress_multiple_snapshots():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        dir1 = base / "snap1"
        dir2 = base / "snap2"

        # snap1 has 3 server errors (lower score)
        _create_mock_crawl(dir1, "https://example.com", server_errors=3)
        # snap2 has 0 server errors (higher score)
        _create_mock_crawl(dir2, "https://example.com", server_errors=0)

        progress = track_progress([dir1, dir2])
        assert progress["snapshots_evaluated"] == 2
        assert len(progress["timeline"]) == 2
        assert progress["score_delta"] is not None
        assert progress["score_delta"] > 0
        assert progress["trajectory"] == "IMPROVING"


def test_track_progress_validation_error():
    with pytest.raises(ValueError):
        track_progress([Path("/non/existent/path/12345")])


def test_run_operational_diagnostics():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)
        db_file = ws / "test.sqlite3"
        conn = sqlite3.connect(str(db_file))
        conn.execute("CREATE TABLE sample (id INT)")
        conn.commit()
        conn.close()

        diag = run_operational_diagnostics(ws)
        assert Path(diag["workspace"]).resolve() == ws.resolve()
        assert diag["databases_inspected"] == 1
        assert diag["status"] == "HEALTHY"
        assert diag["database_integrity"][0]["integrity"] == "PASS"
        assert diag["free_disk_space_gb"] > 0


def test_cli_audit_verify(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        crawl_dir = Path(tmpdir) / "crawl"
        _create_mock_crawl(crawl_dir, "https://example.com", server_errors=0)

        audit_json = Path(tmpdir) / "audit.json"
        audit_json.write_text(
            json.dumps({
                "target": "https://example.com",
                "acceptance_checklist": [
                    {
                        "issue_id": "SEC-01",
                        "title": "Vulnerable SSL Ciphers",
                        "priority": "P0",
                        "acceptance_criteria": "Disable TLS 1.0",
                    }
                ]
            }),
            encoding="utf-8"
        )

        ret = cli_main(["audit-verify", "--audit", str(audit_json), "--crawl", str(crawl_dir), "--format", "terminal"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "AevoraSEO Audit Acceptance Verification" in captured.out
        assert "ALL_RESOLVED" in captured.out

        ret_json = cli_main(["audit-verify", "--audit", str(audit_json), "--crawl", str(crawl_dir), "--format", "json"])
        assert ret_json == 0
        captured_json = capsys.readouterr()
        data = json.loads(captured_json.out)
        assert data["overall_status"] == "ALL_RESOLVED"


def test_cli_progress(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        dir1 = base / "snap1"
        dir2 = base / "snap2"
        _create_mock_crawl(dir1, "https://example.com", server_errors=1)
        _create_mock_crawl(dir2, "https://example.com", server_errors=0)

        ret = cli_main(["progress", "--crawls", str(dir1), str(dir2), "--format", "terminal"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "AevoraSEO Historical Progress Tracking" in captured.out

        ret_json = cli_main(["progress", "--crawls", str(dir1), str(dir2), "--format", "json"])
        assert ret_json == 0
        captured_json = capsys.readouterr()
        data = json.loads(captured_json.out)
        assert data["snapshots_evaluated"] == 2
        assert data["trajectory"] in ["IMPROVING", "STABLE"]
