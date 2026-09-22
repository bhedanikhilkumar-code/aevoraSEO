"""
Unit tests for AevoraSEO Temporal Entity Comparison Engine.
"""

import json
from pathlib import Path

from aevoraseo.entity.comparison import compare_entity_snapshots


def test_entity_snapshot_comparison(tmp_path: Path):
    snap1 = tmp_path / "snap1"
    snap2 = tmp_path / "snap2"
    out_dir = tmp_path / "diff_out"
    snap1.mkdir()
    snap2.mkdir()

    # Snapshot 1: 1 org, 1 conflict, score 45.0
    snap1_data = {
        "target_url": "https://test.example.com",
        "brand_name": "TestCorp",
        "created_at": "2026-09-01T12:00:00Z",
        "score": {
            "headline": 45.0,
            "confidence": "medium",
            "identity_completeness": 15.0,
            "entity_consistency": 15.0,
            "authority_footprint": 5.0,
            "topical_expert_depth": 10.0,
        },
        "nodes": [
            {
                "entity_id": "org:testcorp",
                "entity_type": "Organization",
                "canonical_name": "TestCorp",
                "attributes": {"url": "https://test.example.com"},
            }
        ],
        "conflicts": [
            {
                "conflict_id": "conflict:missing_page_about",
                "conflict_type": "MISSING_REQUIRED_PAGE",
                "severity": "LOW",
                "entity_name": "Website",
                "description": "Missing /about page",
            }
        ],
        "same_as_links": [],
    }

    # Snapshot 2: Added founder Person, resolved missing /about conflict, added LinkedIn, score 75.0
    snap2_data = {
        "target_url": "https://test.example.com",
        "brand_name": "TestCorp",
        "created_at": "2026-09-15T12:00:00Z",
        "score": {
            "headline": 75.0,
            "confidence": "high",
            "identity_completeness": 25.0,
            "entity_consistency": 25.0,
            "authority_footprint": 13.0,
            "topical_expert_depth": 12.0,
        },
        "nodes": [
            {
                "entity_id": "org:testcorp",
                "entity_type": "Organization",
                "canonical_name": "TestCorp",
                "attributes": {"url": "https://test.example.com", "foundingDate": "2021"},
            },
            {
                "entity_id": "person:founder_jane",
                "entity_type": "Person",
                "canonical_name": "Jane Founder",
                "attributes": {"jobTitle": "CEO"},
            },
        ],
        "conflicts": [],
        "same_as_links": [
            {
                "url": "https://www.linkedin.com/company/testcorp",
                "platform": "LinkedIn",
                "entity_name": "TestCorp",
                "is_valid_url": True,
                "is_high_authority": True,
                "found_on_url": "https://test.example.com/about",
            }
        ],
    }

    (snap1 / "entity-report.json").write_text(json.dumps(snap1_data), encoding="utf-8")
    (snap2 / "entity-report.json").write_text(json.dumps(snap2_data), encoding="utf-8")

    diff = compare_entity_snapshots(snap1, snap2, out_dir=out_dir)

    assert diff.score_before == 45.0
    assert diff.score_after == 75.0
    assert diff.score_delta == +30.0
    assert diff.confidence_before == "medium"
    assert diff.confidence_after == "high"

    assert len(diff.added_entities) == 1
    assert diff.added_entities[0]["canonical_name"] == "Jane Founder"

    assert len(diff.resolved_conflicts) == 1
    assert diff.resolved_conflicts[0]["conflict_id"] == "conflict:missing_page_about"

    assert len(diff.added_same_as) == 1
    assert diff.added_same_as[0]["platform"] == "LinkedIn"

    assert (out_dir / "entity-diff.json").exists()
    assert (out_dir / "entity-diff.md").exists()
    assert (out_dir / "entities.sqlite3").exists()
