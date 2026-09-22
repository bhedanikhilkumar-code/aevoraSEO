"""
Tests for content brief generation, editorial outlines, and optimization roadmaps.
"""

from aevoraseo.optimization.briefs import (
    determine_target_word_count,
    generate_content_brief,
    generate_editorial_outline,
    generate_optimization_roadmap,
)


def test_target_word_count_scaling():
    assert determine_target_word_count("informational", 0) == 1200
    assert determine_target_word_count("informational", 1000) == 1350
    assert determine_target_word_count("commercial", 0) == 1400
    assert determine_target_word_count("transactional", 0) == 800
    assert determine_target_word_count("local", 0) == 650


def test_generate_content_brief_and_outline():
    brief = generate_content_brief(
        url="https://example.com/ai-agents",
        title="Autonomous AI Agents Strategy",
        h1="Autonomous AI Agents Strategy",
        primary_query="autonomous ai agents",
        secondary_queries=["ai agent architecture", "agentic workflows"],
        intent="informational",
        current_word_count=450,
        recommended_schema="Article",
    )

    assert brief.primary_query == "autonomous ai agents"
    assert brief.search_intent == "informational"
    assert brief.target_word_count >= 800
    assert len(brief.required_sections) >= 4
    assert len(brief.direct_answer_targets) >= 1
    assert brief.recommended_schema == "Article"

    outline = generate_editorial_outline(brief)
    assert outline.url == "https://example.com/ai-agents"
    assert "Autonomous Ai Agents" in outline.h1_title
    assert len(outline.sections) == len(brief.required_sections)
    assert len(outline.faq_items) >= 2
    assert outline.sections[0]["answer_box_target"] is not None


def test_generate_optimization_roadmap():
    title_audits = [{"url": "https://example.com/p1", "status": "too_short"}]
    heading_audits = [{"url": "https://example.com/p1", "h1_count": 0, "has_skipped_levels": True}]
    answer_opps = [{"url": "https://example.com/p2", "is_answered": False}]
    faq_opps = [{"url": "https://example.com/p3"}]
    orphan_pages = ["https://example.com/orphan"]
    schema_recs = [{"url": "https://example.com/p1", "missing_schemas": ["Article"]}]
    refresh = [{"url": "https://example.com/p4", "refresh_priority": "HIGH"}]

    roadmap = generate_optimization_roadmap(
        title_audits=title_audits,
        heading_audits=heading_audits,
        answer_opportunities=answer_opps,
        faq_opportunities=faq_opps,
        orphan_pages=orphan_pages,
        schema_recommendations=schema_recs,
        refresh_candidates=refresh,
    )

    assert len(roadmap) >= 5
    timeframes = {item.timeframe for item in roadmap}
    assert "30-day" in timeframes
    assert "60-day" in timeframes
    assert "90-day" in timeframes
