"""
Deterministic 4-dimension scoring engine for AevoraSEO Content & Optimization.
"""

from __future__ import annotations

from typing import Any, Dict, List
from .models import OptimizationScore


def calculate_optimization_score(
    title_audits: List[Dict[str, Any]],
    meta_audits: List[Dict[str, Any]],
    heading_audits: List[Dict[str, Any]],
    answer_opportunities: List[Dict[str, Any]],
    faq_opportunities: List[Dict[str, Any]],
    internal_links: List[Dict[str, Any]],
    orphan_pages: List[str],
    schema_recommendations: List[Dict[str, Any]],
    page_count: int,
) -> OptimizationScore:
    """
    Computes deterministic 0-100 score across 4 equal 25-point dimensions.
    """
    if page_count == 0:
        return OptimizationScore(
            headline=0.0,
            metadata_heading_score=0.0,
            content_quality_depth_score=0.0,
            internal_link_cluster_score=0.0,
            schema_structured_score=0.0,
            confidence="low",
            deductions=[{"dimension": "all", "points": 100.0, "reason": "No pages analyzed"}],
        )

    deductions: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # 1. Metadata & Heading Architecture (0 - 25.0)
    # -------------------------------------------------------------
    meta_heading = 25.0

    # Title audits
    bad_titles = sum(1 for t in title_audits if t.get("status") in ("missing", "too_short", "too_long") or t.get("keyword_stuffed"))
    if bad_titles > 0:
        pen = min(7.0, round((bad_titles / page_count) * 7.0, 1))
        meta_heading -= pen
        deductions.append({
            "dimension": "metadata_heading",
            "points": pen,
            "reason": f"{bad_titles} page(s) have suboptimal or keyword-stuffed titles.",
        })

    # Meta description audits
    bad_metas = sum(1 for m in meta_audits if m.get("status") in ("missing", "too_short", "too_long") or not m.get("has_cta"))
    if bad_metas > 0:
        pen = min(6.0, round((bad_metas / page_count) * 6.0, 1))
        meta_heading -= pen
        deductions.append({
            "dimension": "metadata_heading",
            "points": pen,
            "reason": f"{bad_metas} page(s) lack complete meta descriptions with actionable CTAs.",
        })

    # H1 counts
    bad_h1 = sum(1 for h in heading_audits if h.get("h1_count") != 1)
    if bad_h1 > 0:
        pen = min(6.0, round((bad_h1 / page_count) * 6.0, 1))
        meta_heading -= pen
        deductions.append({
            "dimension": "metadata_heading",
            "points": pen,
            "reason": f"{bad_h1} page(s) have missing or multiple H1 headings.",
        })

    # Heading hierarchy / skipped levels
    skipped_headings = sum(1 for h in heading_audits if h.get("has_skipped_levels") or h.get("empty_headings"))
    if skipped_headings > 0:
        pen = min(6.0, round((skipped_headings / page_count) * 6.0, 1))
        meta_heading -= pen
        deductions.append({
            "dimension": "metadata_heading",
            "points": pen,
            "reason": f"{skipped_headings} page(s) have skipped heading levels or empty headings.",
        })

    meta_heading = max(0.0, min(25.0, round(meta_heading, 1)))

    # -------------------------------------------------------------
    # 2. Content Quality & Answer Depth (0 - 25.0)
    # -------------------------------------------------------------
    content_depth = 25.0

    # Thin content or missing answer targets
    unanswered_targets = sum(1 for a in answer_opportunities if not a.get("is_answered"))
    if unanswered_targets > 0:
        pen = min(8.0, round(unanswered_targets * 1.5, 1))
        content_depth -= pen
        deductions.append({
            "dimension": "content_quality_depth",
            "points": pen,
            "reason": f"{unanswered_targets} query/definition opportunity(s) lack a direct answer box.",
        })

    # Unaddressed buyer objections / FAQs
    unaddressed_faq = len(faq_opportunities)
    if unaddressed_faq > 0:
        pen = min(5.0, round(unaddressed_faq * 1.0, 1))
        content_depth -= pen
        deductions.append({
            "dimension": "content_quality_depth",
            "points": pen,
            "reason": f"{unaddressed_faq} key buyer objection(s) lack dedicated FAQ coverage.",
        })

    content_depth = max(0.0, min(25.0, round(content_depth, 1)))

    # -------------------------------------------------------------
    # 3. Topic Cluster & Internal Link Health (0 - 25.0)
    # -------------------------------------------------------------
    link_cluster = 25.0

    # Orphan pages
    if orphan_pages:
        pen = min(9.0, round((len(orphan_pages) / page_count) * 9.0, 1))
        link_cluster -= pen
        deductions.append({
            "dimension": "internal_link_cluster",
            "points": pen,
            "reason": f"{len(orphan_pages)} orphan page(s) have 0 internal inbound links.",
        })

    # Internal link recommendation gaps
    orphan_recovery = sum(1 for r in internal_links if r.get("link_type") == "orphan_recovery")
    hub_spoke_gaps = sum(1 for r in internal_links if r.get("link_type") in ("hub_to_spoke", "spoke_to_hub"))
    if hub_spoke_gaps > 0:
        pen = min(8.0, round(hub_spoke_gaps * 1.0, 1))
        link_cluster -= pen
        deductions.append({
            "dimension": "internal_link_cluster",
            "points": pen,
            "reason": f"{hub_spoke_gaps} pillar-to-spoke internal link connection(s) are missing.",
        })

    # Generic anchor text warnings
    generic_anchors = sum(1 for r in internal_links if "generic" in r.get("rationale", "").lower())
    if generic_anchors > 0:
        pen = min(8.0, round(generic_anchors * 1.0, 1))
        link_cluster -= pen
        deductions.append({
            "dimension": "internal_link_cluster",
            "points": pen,
            "reason": f"{generic_anchors} internal link(s) use non-descriptive generic anchor text.",
        })

    link_cluster = max(0.0, min(25.0, round(link_cluster, 1)))

    # -------------------------------------------------------------
    # 4. Structured Data & Schema Coverage (0 - 25.0)
    # -------------------------------------------------------------
    schema_score = 25.0

    missing_schemas = sum(len(s.get("missing_schemas", [])) for s in schema_recommendations)
    if missing_schemas > 0:
        pen = min(15.0, round(missing_schemas * 3.0, 1))
        schema_score -= pen
        deductions.append({
            "dimension": "schema_structured",
            "points": pen,
            "reason": f"{missing_schemas} recommended schema block(s) are missing from intent-matched pages.",
        })

    schema_score = max(0.0, min(25.0, round(schema_score, 1)))

    # -------------------------------------------------------------
    # Final Calculation & Confidence
    # -------------------------------------------------------------
    headline = round(meta_heading + content_depth + link_cluster + schema_score, 1)

    if page_count >= 5:
        confidence = "high"
    elif page_count >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return OptimizationScore(
        headline=headline,
        metadata_heading_score=meta_heading,
        content_quality_depth_score=content_depth,
        internal_link_cluster_score=link_cluster,
        schema_structured_score=schema_score,
        confidence=confidence,
        deductions=deductions,
    )
