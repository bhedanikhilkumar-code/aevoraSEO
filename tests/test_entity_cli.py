"""
CLI integration tests for AevoraSEO entity and entity-compare commands.
"""

import json
from pathlib import Path
from unittest.mock import patch

from aevoraseo.cli import parser, main


def test_entity_cli_on_snapshot(tmp_path: Path, capsys):
    snap_dir = tmp_path / "snap"
    snap_dir.mkdir()
    page_data = {
        "url": "https://company.example.com",
        "data": {
            "title": "Company Home",
            "jsonld": [
                {
                    "@type": "Organization",
                    "name": "Acme Innovations",
                    "url": "https://company.example.com",
                    "sameAs": ["https://www.linkedin.com/company/acme-innovations"],
                }
            ],
        },
    }
    (snap_dir / "pages.jsonl").write_text(json.dumps(page_data) + "\n", encoding="utf-8")
    (snap_dir / "summary.json").write_text(json.dumps({"seed_url": "https://company.example.com"}), encoding="utf-8")

    out_dir = tmp_path / "entity_out"

    # Run terminal format
    with patch("sys.argv", ["aevoraseo", "entity", str(snap_dir), "--out", str(out_dir), "--format", "terminal"]):
        ret = main()
        assert ret == 0
        captured = capsys.readouterr().out
        assert "AevoraSEO Entity & Authority Intelligence" in captured
        assert "Acme Innovations" in captured

    # Run json format
    with patch("sys.argv", ["aevoraseo", "entity", str(snap_dir), "--out", str(out_dir), "--format", "json"]):
        ret = main()
        assert ret == 0
        captured = capsys.readouterr().out
        data = json.loads(captured)
        assert data["target_url"] == "https://company.example.com"
        assert len(data["nodes"]) >= 1

    # Run csv format
    with patch("sys.argv", ["aevoraseo", "entity", str(snap_dir), "--out", str(out_dir), "--format", "csv"]):
        ret = main()
        assert ret == 0
        captured = capsys.readouterr().out
        assert "entity_id,entity_type,canonical_name" in captured

    # Run markdown format
    with patch("sys.argv", ["aevoraseo", "entity", str(snap_dir), "--out", str(out_dir), "--format", "markdown"]):
        ret = main()
        assert ret == 0
        captured = capsys.readouterr().out
        assert "# AevoraSEO Entity, Authority & Knowledge Intelligence Report" in captured


def test_entity_compare_cli(tmp_path: Path, capsys):
    snap1 = tmp_path / "snap1"
    snap2 = tmp_path / "snap2"
    diff_out = tmp_path / "diff_out"
    snap1.mkdir()
    snap2.mkdir()

    d1 = {
        "target_url": "https://corp.example.com",
        "brand_name": "Corp",
        "created_at": "2026-09-01T00:00:00Z",
        "score": {"headline": 50.0, "confidence": "medium"},
        "nodes": [{"entity_id": "org:corp", "entity_type": "Organization", "canonical_name": "Corp"}],
        "conflicts": [],
        "same_as_links": [],
    }
    d2 = {
        "target_url": "https://corp.example.com",
        "brand_name": "Corp",
        "created_at": "2026-09-10T00:00:00Z",
        "score": {"headline": 70.0, "confidence": "high"},
        "nodes": [{"entity_id": "org:corp", "entity_type": "Organization", "canonical_name": "Corp"}],
        "conflicts": [],
        "same_as_links": [{"url": "https://www.wikidata.org/wiki/Q123", "platform": "Wikidata", "entity_name": "Corp", "is_valid_url": True, "is_high_authority": True}],
    }
    (snap1 / "entity-report.json").write_text(json.dumps(d1), encoding="utf-8")
    (snap2 / "entity-report.json").write_text(json.dumps(d2), encoding="utf-8")

    with patch("sys.argv", ["aevoraseo", "entity-compare", "--before", str(snap1), "--after", str(snap2), "--out", str(diff_out), "--format", "terminal"]):
        ret = main()
        assert ret == 0
        captured = capsys.readouterr().out
        assert "AevoraSEO Entity Evolution Diff" in captured
        assert "Score Delta: +20.0 points" in captured
