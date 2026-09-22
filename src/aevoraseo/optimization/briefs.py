"""
Grounded generation of content briefs, editorial outlines, and optimization roadmaps.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

from .models import (
    ContentBrief,
    EditorialOutline,
    OptimizationRoadmapItem,
)


def determine_target_word_count(intent: str, current_count: int) -> int:
    """
    Calibrate realistic target word count based on search intent and current page baseline.
    """
    intent_lower = intent.lower()
    if "informational" in intent_lower:
        base = 1200
    elif "commercial" in intent_lower:
        base = 1400
    elif "transactional" in intent_lower:
        base = 800
    elif "local" in intent_lower:
        base = 650
    else:
        base = 500

    if current_count > 0:
        return max(base, current_count + 350)
    return base


def generate_content_brief(
    url: str,
    title: str,
    h1: str,
    primary_query: str,
    secondary_queries: List[str],
    intent: str,
    current_word_count: int,
    recommended_schema: str = "Article",
    cluster_topic: str = "",
    internal_link_targets: Optional[List[Dict[str, str]]] = None,
) -> ContentBrief:
    """
    Synthesizes a structured content brief grounded in observed page signals.
    """
    target_words = determine_target_word_count(intent, current_word_count)
    query_title = primary_query.title() if primary_query else "Topic Overview"

    # Define required sections based on intent
    intent_lower = intent.lower()
    if "transactional" in intent_lower or "commercial" in intent_lower:
        required_sections = [
            f"Overview: Core Value of {query_title}",
            f"Key Capabilities & Specifications",
            f"Pricing & Implementation Process",
            f"Buyer FAQs & Guarantees",
            f"Next Steps & Consultation CTA",
        ]
        answer_targets = [
            f"What is {primary_query} and how does it solve buyer friction? (40-60 word answer box)",
            f"How much does {primary_query} cost or what are the engagement tiers? (Direct breakdown)",
        ]
    elif "local" in intent_lower:
        required_sections = [
            f"Local Service Overview: {query_title}",
            f"Service Area Coverage & Location Details",
            f"Why Choose Our Local Team",
            f"Local Client FAQs & Booking",
            f"Contact & Directions",
        ]
        answer_targets = [
            f"Where is the service available and how quickly can clients book? (40-60 word answer box)",
        ]
    else:
        # Informational default
        required_sections = [
            f"Introduction: Defining {query_title}",
            f"Comprehensive Breakdown & Core Principles",
            f"Step-by-Step Implementation Guide",
            f"Common Mistakes & Best Practices",
            f"Frequently Asked Questions",
        ]
        answer_targets = [
            f"Direct definition of {primary_query} placed immediately under H2 (40-60 words).",
            f"Step-by-step ordered list outlining the implementation workflow.",
        ]

    guidance = (
        f"Grounded editorial brief for '{url}'. Align content strictly with {intent} intent. "
        f"Avoid generic fluff or unverified superlative claims. Incorporate authoritative first-party "
        f"evidence, technical clarity, and direct answers for search and AI citation engines."
    )

    brief_id = f"brief_{re.sub(r'[^a-zA-Z0-9]', '_', urlsplit(url).path.strip('/') or 'home')}"

    return ContentBrief(
        brief_id=brief_id,
        url=url,
        primary_query=primary_query,
        secondary_queries=secondary_queries,
        search_intent=intent,
        target_word_count=target_words,
        required_sections=required_sections,
        direct_answer_targets=answer_targets,
        recommended_internal_links=internal_link_targets or [],
        recommended_schema=recommended_schema,
        editorial_guidance=guidance,
    )


def generate_editorial_outline(brief: ContentBrief) -> EditorialOutline:
    """
    Produces a detailed heading-by-heading editorial outline blueprint.
    """
    sections: List[Dict[str, Any]] = []
    total_sections = len(brief.required_sections)
    words_per_section = max(150, brief.target_word_count // max(1, total_sections))

    for idx, sec_title in enumerate(brief.required_sections):
        level = "h2"
        answer_box = None
        bullets = [
            f"Explain core concepts of {sec_title.lower()}.",
            f"Provide verifiable examples and specific implementation details.",
        ]

        if idx == 0 and brief.direct_answer_targets:
            answer_box = brief.direct_answer_targets[0]
            bullets.insert(0, "Lead immediately with a 40-60 word definition or summary paragraph.")
        elif idx == 1 and len(brief.direct_answer_targets) > 1:
            answer_box = brief.direct_answer_targets[1]

        sections.append({
            "level": level,
            "heading": sec_title,
            "target_words": words_per_section,
            "answer_box_target": answer_box,
            "bullet_points": bullets,
        })

    faq_items = [
        {
            "question": f"What is the most important factor when considering {brief.primary_query}?",
            "answer_blueprint": f"Concise 2-sentence explanation highlighting efficiency, verified outcomes, and technical precision.",
        },
        {
            "question": f"How does {brief.primary_query} compare to standard alternatives?",
            "answer_blueprint": f"Objective comparison focusing on implementation speed, long-term ROI, and maintenance overhead.",
        },
        {
            "question": f"How can users get started with {brief.primary_query}?",
            "answer_blueprint": f"Clear 3-step action roadmap directing users to the primary contact or enrollment mechanism.",
        },
    ]

    outline_id = f"outline_{brief.brief_id.removeprefix('brief_')}"
    h1_title = f"{brief.primary_query.title()}: Complete Guide & Strategy"

    return EditorialOutline(
        outline_id=outline_id,
        url=brief.url,
        h1_title=h1_title,
        sections=sections,
        faq_items=faq_items,
        cta_placement="Contextual mid-content recommendation and sticky mobile footer button.",
    )


def generate_optimization_roadmap(
    title_audits: List[Dict[str, Any]],
    heading_audits: List[Dict[str, Any]],
    answer_opportunities: List[Dict[str, Any]],
    faq_opportunities: List[Dict[str, Any]],
    orphan_pages: List[str],
    schema_recommendations: List[Dict[str, Any]],
    refresh_candidates: List[Dict[str, Any]],
) -> List[OptimizationRoadmapItem]:
    """
    Synthesizes a 30/60/90-day actionable roadmap prioritized by impact and dependencies.
    """
    items: List[OptimizationRoadmapItem] = []

    # -------------------------------------------------------------
    # 30-Day Plan: Critical Fixes, Metadata & Structure
    # -------------------------------------------------------------
    meta_fix_urls = [
        t["url"] for t in title_audits if t.get("status") in ("missing", "too_short", "too_long")
    ]
    if meta_fix_urls:
        items.append(
            OptimizationRoadmapItem(
                timeframe="30-day",
                phase_name="Metadata Foundation",
                action="Rewrite titles to 45-65 chars with brand placement and primary query alignment.",
                target_urls=meta_fix_urls[:5],
                expected_impact="HIGH",
                dependencies=["Crawl audit verification"],
            )
        )

    h1_fix_urls = [h["url"] for h in heading_audits if h.get("h1_count") != 1 or h.get("has_skipped_levels")]
    if h1_fix_urls:
        items.append(
            OptimizationRoadmapItem(
                timeframe="30-day",
                phase_name="Heading Hierarchy Remediation",
                action="Enforce single H1 and resolve skipped heading levels (e.g. H1->H3) across templates.",
                target_urls=h1_fix_urls[:5],
                expected_impact="HIGH",
                dependencies=["Template access"],
            )
        )

    if orphan_pages:
        items.append(
            OptimizationRoadmapItem(
                timeframe="30-day",
                phase_name="Orphan Page Recovery",
                action="Integrate orphan pages into site navigation and contextual in-body links.",
                target_urls=orphan_pages[:5],
                expected_impact="HIGH",
                dependencies=["Site architecture review"],
            )
        )

    # -------------------------------------------------------------
    # 60-Day Plan: Answer Depth, Objection Handling & Schema
    # -------------------------------------------------------------
    ans_urls = [a["url"] for a in answer_opportunities if not a.get("is_answered")]
    if ans_urls:
        items.append(
            OptimizationRoadmapItem(
                timeframe="60-day",
                phase_name="Direct Answer Engineering",
                action="Implement 40-60 word definition boxes and ordered lists under question headings.",
                target_urls=ans_urls[:5],
                expected_impact="HIGH",
                dependencies=["Metadata Foundation"],
            )
        )

    schema_urls = [s["url"] for s in schema_recommendations if s.get("missing_schemas")]
    if schema_urls:
        items.append(
            OptimizationRoadmapItem(
                timeframe="60-day",
                phase_name="Structured Data Deployment",
                action="Deploy intent-matched JSON-LD schemas (Article, Service, FAQPage, Product).",
                target_urls=schema_urls[:5],
                expected_impact="MEDIUM",
                dependencies=["Heading Hierarchy Remediation"],
            )
        )

    faq_urls = [f["url"] for f in faq_opportunities]
    if faq_urls:
        items.append(
            OptimizationRoadmapItem(
                timeframe="60-day",
                phase_name="Buyer Objection FAQs",
                action="Add dedicated FAQ accordions addressing pricing, guarantees, and support friction.",
                target_urls=faq_urls[:5],
                expected_impact="HIGH",
                dependencies=["Direct Answer Engineering"],
            )
        )

    # -------------------------------------------------------------
    # 90-Day Plan: Topic Clusters, Content Refresh & Link Compounding
    # -------------------------------------------------------------
    refresh_urls = [r["url"] for r in refresh_candidates if r.get("refresh_priority") in ("HIGH", "MEDIUM")]
    if refresh_urls:
        items.append(
            OptimizationRoadmapItem(
                timeframe="90-day",
                phase_name="Thin & Aging Content Refresh",
                action="Expand thin pages (<500 words) with updated data, case examples, and current year references.",
                target_urls=refresh_urls[:5],
                expected_impact="HIGH",
                dependencies=["Direct Answer Engineering"],
            )
        )

    items.append(
        OptimizationRoadmapItem(
            timeframe="90-day",
            phase_name="Topic Cluster & Internal Link Compounding",
            action="Build bidirectional hub-and-spoke internal links with descriptive keyword anchors.",
            target_urls=[t["url"] for t in title_audits[:5]],
            expected_impact="HIGH",
            dependencies=["Structured Data Deployment", "Thin & Aging Content Refresh"],
        )
    )

    return items
