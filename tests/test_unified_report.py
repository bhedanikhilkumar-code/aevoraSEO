"""Unit tests for unified cross-subsystem reporting."""

import json
import sqlite3
import tempfile
from pathlib import Path

from aevoraseo.unified_report import (
    IssuePriority,
    PrioritizedIssue,
    UnifiedAuditReport,
    generate_unified_report,
    render_terminal_report,
    render_markdown_report,
    render_html_report,
    render_json_report,
    export_evidence_csv,
    sanitize_csv_cell,
)
from aevoraseo.cli import main as cli_main


def test_sanitize_csv_cell_formula_injection():
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_cell("-2+3") == "'-2+3"
    assert sanitize_csv_cell("@SUM(1,2)") == "'@SUM(1,2)"
    assert sanitize_csv_cell("\tTabbed") == "'\tTabbed"
    assert sanitize_csv_cell("Normal text") == "Normal text"
    assert sanitize_csv_cell("") == ""
    assert sanitize_csv_cell(None) == ""


def test_generate_unified_report_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        report = generate_unified_report(Path(tmpdir), target="https://example.com")
        assert isinstance(report, UnifiedAuditReport)
        assert report.target == "https://example.com"
        assert len(report.subsystem_scores) >= 5
        assert len(report.prioritized_issues) > 0
        assert "days_1_30" in report.roadmap_30_60_90


def test_generate_unified_report_with_databases():
    with tempfile.TemporaryDirectory() as tmpdir:
        crawl_dir = Path(tmpdir)

        # 1. crawl.sqlite3 with 5xx error
        conn = sqlite3.connect(str(crawl_dir / "crawl.sqlite3"))
        cur = conn.cursor()
        cur.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
        cur.execute("INSERT INTO meta VALUES ('config', ?)", (json.dumps({"config": {"start_urls": ["https://testsite.com"]}}),))
        cur.execute("CREATE TABLE pages (url TEXT, status_code INTEGER, robots_noindex INTEGER)")
        cur.execute("INSERT INTO pages VALUES ('https://testsite.com', 200, 0)")
        cur.execute("INSERT INTO pages VALUES ('https://testsite.com/err', 500, 0)")
        cur.execute("INSERT INTO pages VALUES ('https://testsite.com/dead', 404, 0)")
        conn.commit()
        conn.close()

        # 2. aeo.sqlite3 with evaluation
        conn = sqlite3.connect(str(crawl_dir / "aeo.sqlite3"))
        cur = conn.cursor()
        cur.execute("CREATE TABLE aeo_snapshots (overall_score REAL, dimensional_scores TEXT, created_at TEXT)")
        cur.execute("INSERT INTO aeo_snapshots VALUES (75.5, '{}', '2026-09-22T00:00:00Z')")
        cur.execute("CREATE TABLE aeo_page_evaluations (direct_answer_present INTEGER)")
        cur.execute("INSERT INTO aeo_page_evaluations VALUES (0)")
        conn.commit()
        conn.close()

        # 3. entities.sqlite3
        conn = sqlite3.connect(str(crawl_dir / "entities.sqlite3"))
        cur = conn.cursor()
        cur.execute("CREATE TABLE entity_snapshots (overall_score REAL, total_entities INTEGER, sameas_count INTEGER, created_at TEXT)")
        cur.execute("INSERT INTO entity_snapshots VALUES (82.0, 5, 2, '2026-09-22T00:00:00Z')")
        cur.execute("CREATE TABLE entity_conflicts (id TEXT)")
        cur.execute("INSERT INTO entity_conflicts VALUES ('conf-1')")
        conn.commit()
        conn.close()

        report = generate_unified_report(crawl_dir)
        assert report.target == "https://testsite.com"
        assert report.overall_score is not None

        # Check issues contain P0 (5xx error or entity conflict)
        p0_issues = [i for i in report.prioritized_issues if i.priority == IssuePriority.P0]
        assert len(p0_issues) >= 1

        # Check renderers
        term = render_terminal_report(report)
        assert "AEVORASEO UNIFIED CLIENT AUDIT REPORT" in term
        assert "SUBSYSTEM SCORECARD:" in term

        md = render_markdown_report(report)
        assert "# AevoraSEO Unified Client Audit Report:" in md
        assert "## Subsystem Scorecard" in md

        html_out = render_html_report(report)
        assert "<!DOCTYPE html>" in html_out
        assert "AevoraSEO Client Audit" in html_out

        js = render_json_report(report)
        data = json.loads(js)
        assert data["target"] == "https://testsite.com"
        assert len(data["prioritized_issues"]) >= 2

        # CSV export
        csv_files = export_evidence_csv(report, crawl_dir / "exports")
        assert len(csv_files) == 2
        for f in csv_files:
            assert Path(f).is_file()


def test_cli_report_terminal(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        ret = cli_main(["report", tmpdir, "--target", "https://example.com", "--format", "terminal"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "AEVORASEO UNIFIED CLIENT AUDIT REPORT" in captured.out


def test_cli_report_json(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        ret = cli_main(["report", tmpdir, "--target", "https://example.com", "--format", "json"])
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["target"] == "https://example.com"
        assert "prioritized_issues" in data


def test_cli_report_markdown(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        ret = cli_main(["report", tmpdir, "--target", "https://example.com", "--format", "markdown"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "# AevoraSEO Unified Client Audit Report:" in captured.out


def test_cli_report_csv(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        ret = cli_main(["report", tmpdir, "--out", tmpdir, "--format", "csv"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "Exported 2 CSV files" in captured.out
        assert (Path(tmpdir) / "audit-issues.csv").is_file()
        assert (Path(tmpdir) / "audit-scorecard.csv").is_file()
