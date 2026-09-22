"""
Tests for SQLite persistence and snapshot comparison in Content Optimization.
"""

import json
from pathlib import Path

from aevoraseo.optimization.comparison import compare_optimization_snapshots
from aevoraseo.optimization.models import (
    ContentBrief,
    DirectAnswerOpportunity,
    HeadingAudit,
    MetaDescriptionAudit,
    OptimizationResult,
    OptimizationScore,
    TitleAudit,
    TopicCluster,
)
from aevoraseo.optimization.persistence import (
    init_optimization_db,
    load_optimization_snapshot,
    save_optimization_snapshot,
)


def _make_dummy_result(target_url: str, headline_score: float) -> OptimizationResult:
    score = OptimizationScore(
        headline=headline_score,
        metadata_heading_score=20.0,
        content_quality_depth_score=20.0,
        internal_link_cluster_score=20.0,
        schema_structured_score=20.0,
        confidence="high",
        deductions=[],
    )
    return OptimizationResult(
        target_url=target_url,
        brand_name="TestBrand",
        created_at="2026-09-22T12:00:00Z",
        pages_analyzed=3,
        score=score.to_dict(),
        title_audits=[
            TitleAudit("https://example.com/p1", "Page One", 8, "too_short", True, "end", False, "page one", True, "Fix").to_dict()
        ],
        meta_audits=[
            MetaDescriptionAudit("https://example.com/p1", "Desc", 4, "too_short", False, [], "page one", True, "Fix").to_dict()
        ],
        heading_audits=[
            HeadingAudit("https://example.com/p1", 1, ["Heading"], 2, 1, False, [], [], [], "OK").to_dict()
        ],
        direct_answer_opportunities=[
            DirectAnswerOpportunity("https://example.com/p1", "What is P1?", "definition", "40-60 word answer box", None, False, "Draft", 0.8).to_dict()
        ],
        faq_opportunities=[],
        internal_link_recommendations=[],
        orphan_pages=["https://example.com/orphan"],
        topic_clusters=[
            TopicCluster("cluster_topic", "Topic", "https://example.com/p1", ["https://example.com/p2"], 85.0, [], 0.85).to_dict()
        ],
        schema_recommendations=[],
        content_briefs=[
            ContentBrief("brief_p1", "https://example.com/p1", "page one", [], "informational", 1200, ["Sec 1"], ["Target 1"], [], "Article", "Guide").to_dict()
        ],
        editorial_outlines=[],
        content_gaps=[],
        refresh_candidates=[],
        roadmap_items=[],
        recommendations=[{"timeframe": "30-day", "action": "Fix metadata", "impact": "HIGH", "target_urls": ["https://example.com/p1"]}],
    )


def test_sqlite_persistence_roundtrip(tmp_path: Path):
    db_file = tmp_path / "content_optimization.sqlite3"
    init_optimization_db(db_file)

    res = _make_dummy_result("https://example.com", 80.0)
    save_optimization_snapshot(db_file, res, "snap_001")

    loaded = load_optimization_snapshot(db_file, "snap_001")
    assert loaded is not None
    assert loaded["snapshot_id"] == "snap_001"
    assert loaded["target_url"] == "https://example.com"
    assert loaded["score"]["headline"] == 80.0
    assert len(loaded["page_audits"]) == 1
    assert len(loaded["answer_opportunities"]) == 1
    assert len(loaded["topic_clusters"]) == 1
    assert len(loaded["content_briefs"]) == 1
    assert "https://example.com/orphan" in loaded["orphan_pages"]


def test_compare_optimization_snapshots(tmp_path: Path):
    before_file = tmp_path / "before.json"
    after_file = tmp_path / "after.json"

    res_before = _make_dummy_result("https://example.com", 65.0)
    res_after = _make_dummy_result("https://example.com", 85.0)

    # In 'after', mark title as optimal and remove orphan
    res_after.title_audits[0]["status"] = "optimal"
    res_after.orphan_pages = []

    before_file.write_text(json.dumps(res_before.to_dict()), encoding="utf-8")
    after_file.write_text(json.dumps(res_after.to_dict()), encoding="utf-8")

    diff_out = tmp_path / "diff_out"
    diff = compare_optimization_snapshots(before_file, after_file, out_dir=diff_out)

    assert diff.score_before == 65.0
    assert diff.score_after == 85.0
    assert diff.score_delta == 20.0
    assert len(diff.resolved_issues) >= 1

    # Check saved artifacts in diff_out
    assert (diff_out / "content_optimization.sqlite3").exists()
    assert (diff_out / "optimization-diff.json").exists()
    assert (diff_out / "optimization-diff.md").exists()
