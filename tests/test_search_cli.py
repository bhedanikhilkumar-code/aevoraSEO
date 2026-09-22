"""
Tests for search and commercial CLI commands.
"""

import json
from pathlib import Path
from unittest.mock import patch
from aevoraseo.cli import parser, main


def test_cli_search_command_snapshot(tmp_path: Path, capsys):
    snap_dir = tmp_path / "snap"
    snap_dir.mkdir()
    out_dir = tmp_path / "out"

    pages_data = [
        {
            "final_url": "https://example.com/",
            "data": {
                "title": "Acme Dental Care",
                "headings": {"h1": ["Acme Dental Clinic"]},
                "schema": [{"@type": "LocalBusiness", "name": "Acme Dental", "telephone": "847-555-0100"}],
            },
            "html": "<html><title>Acme Dental Care</title><h1>Acme Dental Clinic</h1><a href='tel:8475550100'>Call Us</a></html>",
        },
        {
            "final_url": "https://example.com/services/implants",
            "data": {
                "title": "Dental Implants Service",
                "headings": {"h1": ["Dental Implants Treatment"]},
                "schema": [{"@type": "Service", "name": "Dental Implants"}],
            },
            "html": "<html><title>Dental Implants Service</title><h1>Dental Implants Treatment</h1><a class='btn' href='/book'>Book Consultation</a></html>",
        },
    ]

    with (snap_dir / "pages.jsonl").open("w", encoding="utf-8") as f:
        for p in pages_data:
            f.write(json.dumps(p) + "\n")
    (snap_dir / "summary.json").write_text(json.dumps({"seed_url": "https://example.com/"}), encoding="utf-8")

    # Run terminal format
    with patch("sys.argv", ["aevoraseo", "search", str(snap_dir), "--out", str(out_dir), "--format", "terminal"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "AevoraSEO Search, Local & Commercial Intelligence Engine" in captured
    assert "Search & Commercial Visibility Score" in captured

    assert (out_dir / "search-commercial.json").exists()
    assert (out_dir / "search-commercial.md").exists()
    assert (out_dir / "page-intents.csv").exists()
    assert (out_dir / "cannibalization.csv").exists()
    assert (out_dir / "search_commercial.sqlite3").exists()

    # Run json format
    with patch("sys.argv", ["aevoraseo", "search", str(snap_dir), "--out", str(out_dir), "--format", "json"]):
        exit_code = main()
        assert exit_code == 0
        captured = capsys.readouterr().out
        data = json.loads(captured)
        assert data["target_url"] == "https://example.com/"
        assert len(data["page_intents"]) >= 1

    # Run commercial alias
    with patch("sys.argv", ["aevoraseo", "commercial", str(snap_dir), "--out", str(out_dir), "--format", "terminal"]):
        exit_code = main()
        assert exit_code == 0


def test_cli_search_compare_command(tmp_path: Path, capsys):
    snap1 = tmp_path / "s1"
    snap2 = tmp_path / "s2"
    out_diff = tmp_path / "diff"
    snap1.mkdir()
    snap2.mkdir()

    data = {
        "snapshot_id": "s1",
        "target_url": "https://example.com",
        "score": {"headline": 70.0, "confidence": "high"},
        "page_intents": [],
        "cannibalization_issues": [],
        "commercial_journeys": [],
        "local_signals": [],
    }

    (snap1 / "search-commercial.json").write_text(json.dumps(data), encoding="utf-8")
    data["snapshot_id"] = "s2"
    data["score"]["headline"] = 80.0
    (snap2 / "search-commercial.json").write_text(json.dumps(data), encoding="utf-8")

    with patch("sys.argv", ["aevoraseo", "search-compare", "--before", str(snap1), "--after", str(snap2), "--out", str(out_diff), "--format", "terminal"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "AevoraSEO Search & Commercial Evolution Diff" in captured
    assert "+10.0 points" in captured
