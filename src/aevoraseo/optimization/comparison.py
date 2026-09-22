"""
Snapshot comparison for AevoraSEO Content & Optimization Intelligence.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .analyzer import analyze_target_optimization
from .models import (
    OptimizationDiff,
    OptimizationResult,
)
from .persistence import save_optimization_diff


def _extract_page_issue_keys(result_dict: Dict[str, Any]) -> Dict[str, List[str]]:
    """Helper to extract active issues per URL."""
    issues_by_url: Dict[str, List[str]] = {}

    for t in result_dict.get("title_audits", []):
        u = t.get("url", "")
        if t.get("status") in ("missing", "too_short", "too_long"):
            issues_by_url.setdefault(u, []).append(f"Title {t.get('status')}")
        if t.get("keyword_stuffed"):
            issues_by_url.setdefault(u, []).append("Title keyword stuffed")

    for m in result_dict.get("meta_audits", []):
        u = m.get("url", "")
        if m.get("status") in ("missing", "too_short", "too_long"):
            issues_by_url.setdefault(u, []).append(f"Meta description {m.get('status')}")
        if not m.get("has_cta"):
            issues_by_url.setdefault(u, []).append("Meta description lacks CTA")

    for h in result_dict.get("heading_audits", []):
        u = h.get("url", "")
        if h.get("h1_count") == 0:
            issues_by_url.setdefault(u, []).append("Missing H1")
        elif h.get("h1_count") > 1:
            issues_by_url.setdefault(u, []).append(f"Multiple H1s ({h.get('h1_count')})")
        if h.get("has_skipped_levels"):
            issues_by_url.setdefault(u, []).append("Skipped heading levels")

    for o in result_dict.get("orphan_pages", []):
        issues_by_url.setdefault(o, []).append("Orphan page (0 internal links)")

    return issues_by_url


def compare_optimization_snapshots(
    before_path: Path,
    after_path: Path,
    out_dir: Optional[Path] = None,
) -> OptimizationDiff:
    """
    Compares two optimization snapshots and calculates delta metrics, resolved issues,
    new defects, and topic cluster improvements.
    """
    before_path = Path(before_path)
    after_path = Path(after_path)

    # 1. Resolve 'before' result
    if before_path.is_file() and before_path.suffix == ".json":
        before_res = json.loads(before_path.read_text(encoding="utf-8"))
    else:
        before_res = analyze_target_optimization(str(before_path)).to_dict()

    # 2. Resolve 'after' result
    if after_path.is_file() and after_path.suffix == ".json":
        after_res = json.loads(after_path.read_text(encoding="utf-8"))
    else:
        after_res = analyze_target_optimization(str(after_path)).to_dict()

    score_before = before_res.get("score", {}).get("headline", 0.0)
    score_after = after_res.get("score", {}).get("headline", 0.0)
    score_delta = round(score_after - score_before, 1)

    dimension_deltas = {
        "metadata_heading_delta": round(
            after_res.get("score", {}).get("metadata_heading_score", 0.0)
            - before_res.get("score", {}).get("metadata_heading_score", 0.0),
            1,
        ),
        "content_quality_depth_delta": round(
            after_res.get("score", {}).get("content_quality_depth_score", 0.0)
            - before_res.get("score", {}).get("content_quality_depth_score", 0.0),
            1,
        ),
        "internal_link_cluster_delta": round(
            after_res.get("score", {}).get("internal_link_cluster_score", 0.0)
            - before_res.get("score", {}).get("internal_link_cluster_score", 0.0),
            1,
        ),
        "schema_structured_delta": round(
            after_res.get("score", {}).get("schema_structured_score", 0.0)
            - before_res.get("score", {}).get("schema_structured_score", 0.0),
            1,
        ),
    }

    # Track resolved vs new issues
    before_issues = _extract_page_issue_keys(before_res)
    after_issues = _extract_page_issue_keys(after_res)

    resolved_issues: List[Dict[str, Any]] = []
    new_issues: List[Dict[str, Any]] = []

    all_urls = set(before_issues.keys()).union(after_issues.keys())
    for u in all_urls:
        b_set = set(before_issues.get(u, []))
        a_set = set(after_issues.get(u, []))

        resolved = b_set - a_set
        for r in resolved:
            resolved_issues.append({"url": u, "issue": r, "status": "resolved"})

        introduced = a_set - b_set
        for i in introduced:
            new_issues.append({"url": u, "issue": i, "status": "new_defect"})

    # Answer opportunities delta
    before_ans = {a.get("question_or_topic", "") for a in before_res.get("direct_answer_opportunities", [])}
    after_ans = {a.get("question_or_topic", "") for a in after_res.get("direct_answer_opportunities", [])}
    new_answers = [
        a for a in after_res.get("direct_answer_opportunities", [])
        if a.get("question_or_topic") not in before_ans
    ]

    # Cluster evolution
    before_clusters = {c.get("cluster_id"): c for c in before_res.get("topic_clusters", [])}
    after_clusters = {c.get("cluster_id"): c for c in after_res.get("topic_clusters", [])}
    cluster_evolution = []
    for cid, ac in after_clusters.items():
        bc = before_clusters.get(cid)
        if bc:
            delta_health = round(ac.get("cluster_health_score", 0.0) - bc.get("cluster_health_score", 0.0), 1)
            cluster_evolution.append({
                "cluster_id": cid,
                "topic": ac.get("topic_name"),
                "before_health": bc.get("cluster_health_score", 0.0),
                "after_health": ac.get("cluster_health_score", 0.0),
                "health_delta": delta_health,
                "spokes_count_change": len(ac.get("spoke_urls", [])) - len(bc.get("spoke_urls", [])),
            })
        else:
            cluster_evolution.append({
                "cluster_id": cid,
                "topic": ac.get("topic_name"),
                "before_health": 0.0,
                "after_health": ac.get("cluster_health_score", 0.0),
                "health_delta": ac.get("cluster_health_score", 0.0),
                "spokes_count_change": len(ac.get("spoke_urls", [])),
                "state": "new_cluster",
            })

    transitions = {
        "resolved_issues_count": len(resolved_issues),
        "new_issues_count": len(new_issues),
        "new_answer_opportunities_count": len(new_answers),
        "clusters_tracked": len(after_clusters),
        "orphan_pages_before": len(before_res.get("orphan_pages", [])),
        "orphan_pages_after": len(after_res.get("orphan_pages", [])),
    }

    created_at = datetime.now(timezone.utc).isoformat()
    diff = OptimizationDiff(
        before_snapshot_id=before_path.name,
        after_snapshot_id=after_path.name,
        target_url=after_res.get("target_url", str(after_path)),
        created_at=created_at,
        score_before=score_before,
        score_after=score_after,
        score_delta=score_delta,
        confidence_before=before_res.get("score", {}).get("confidence", "low"),
        confidence_after=after_res.get("score", {}).get("confidence", "low"),
        transition_summary=transitions,
        dimension_deltas=dimension_deltas,
        resolved_issues=resolved_issues,
        new_issues=new_issues,
        new_answer_opportunities=new_answers,
        cluster_evolution=cluster_evolution,
    )

    if out_dir:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        db_path = out_dir / "content_optimization.sqlite3"
        save_optimization_diff(db_path, diff)

        (out_dir / "optimization-diff.json").write_text(
            json.dumps(diff.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )

        from .reporter import generate_diff_markdown_report
        (out_dir / "optimization-diff.md").write_text(
            generate_diff_markdown_report(diff), encoding="utf-8"
        )

    return diff
