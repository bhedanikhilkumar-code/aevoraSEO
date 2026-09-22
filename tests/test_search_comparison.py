"""
Tests for temporal snapshot comparison engine in search intelligence.
"""

import json
from pathlib import Path

from aevoraseo.search.comparison import compare_search_snapshots


def test_compare_search_snapshots(tmp_path: Path):
    snap1 = tmp_path / "snap1"
    snap2 = tmp_path / "snap2"
    out_diff = tmp_path / "diff"
    snap1.mkdir()
    snap2.mkdir()

    data1 = {
        "snapshot_id": "snap1",
        "target_url": "https://example.com",
        "score": {"headline": 60.0, "confidence": "medium"},
        "page_intents": [
            {"url": "https://example.com/page1", "primary_intent": "Informational", "primary_target_query": "dental implants"},
            {"url": "https://example.com/page2", "primary_intent": "Informational", "primary_target_query": "dental implants"},
        ],
        "cannibalization_issues": [
            {
                "query": "dental implants",
                "intent": "Informational",
                "risk_level": "HIGH",
                "competing_urls": ["https://example.com/page1", "https://example.com/page2"],
                "recommendation": "Consolidate pages",
            }
        ],
        "commercial_journeys": [
            {"url": "https://example.com/page1", "high_intent_ctas": [], "friction_issues": ["Missing CTA"], "trust_signals": []}
        ],
        "local_signals": [
            {"url": "https://example.com/page1", "has_local_business_schema": False, "has_clickable_tel": False}
        ],
    }

    data2 = {
        "snapshot_id": "snap2",
        "target_url": "https://example.com",
        "score": {"headline": 85.0, "confidence": "high"},
        "page_intents": [
            {"url": "https://example.com/page1", "primary_intent": "Transactional", "primary_target_query": "dental implants"},
            {"url": "https://example.com/page2", "primary_intent": "Informational", "primary_target_query": "dental implants cost"},
        ],
        "cannibalization_issues": [],  # Resolved!
        "commercial_journeys": [
            {
                "url": "https://example.com/page1",
                "high_intent_ctas": [{"text": "Book Consultation"}],
                "friction_issues": [],
                "trust_signals": ["Customer reviews / ratings"],
            }
        ],
        "local_signals": [
            {"url": "https://example.com/page1", "has_local_business_schema": True, "has_clickable_tel": True}
        ],
    }

    (snap1 / "search-commercial.json").write_text(json.dumps(data1), encoding="utf-8")
    (snap2 / "search-commercial.json").write_text(json.dumps(data2), encoding="utf-8")

    diff = compare_search_snapshots(snap1, snap2, out_dir=out_diff)

    assert diff.score_before == 60.0
    assert diff.score_after == 85.0
    assert diff.score_delta == 25.0
    assert len(diff.resolved_cannibalizations) == 1
    assert len(diff.new_cannibalizations) == 0
    assert len(diff.commercial_improvements) == 1
    assert len(diff.local_signal_changes) == 2
    assert diff.transition_summary["resolved_cannibalizations_count"] == 1

    # Check generated files
    assert (out_diff / "search_comparison.json").exists()
    assert (out_diff / "search_comparison.csv").exists()
    assert (out_diff / "search_comparison.md").exists()
    assert (out_diff / "search_commercial.sqlite3").exists()
