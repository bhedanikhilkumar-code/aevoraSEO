"""
Tests for Topic Clusters, Internal Link graph, Orphans, and Content Refresh detection.
"""

from aevoraseo.optimization.analyzer import (
    analyze_topic_clusters,
    audit_internal_links_and_orphans,
    detect_content_gaps_and_refresh,
)
from aevoraseo.optimization.models import HeadingAudit
from aevoraseo.search.models import PageIntentAnalysis


def test_internal_links_and_orphans():
    pages = [
        {
            "url": "https://example.com/",
            "data": {
                "title": "Home",
                "links": [
                    {"url": "https://example.com/services", "anchor": "Services"},
                    {"url": "https://example.com/about", "anchor": "click here"},
                ],
            }
        },
        {
            "url": "https://example.com/services",
            "data": {
                "title": "Services",
                "links": [
                    {"url": "https://example.com/services/seo", "anchor": "SEO Audits"},
                ],
            }
        },
        {
            "url": "https://example.com/services/seo",
            "data": {
                "title": "SEO Audits",
                "links": [],
            }
        },
        {
            "url": "https://example.com/orphan-article",
            "data": {
                "title": "Orphan Article",
                "links": [],
            }
        },
    ]

    recs, orphans = audit_internal_links_and_orphans(pages, "https://example.com/")

    # Orphan page detection
    assert "https://example.com/orphan-article" in orphans
    assert "https://example.com/" not in orphans  # Root is excluded

    # Generic anchor detection
    generic_rec = next((r for r in recs if r.link_type == "generic_anchor_fix"), None)
    assert generic_rec is not None
    assert "click here" in generic_rec.recommended_anchor.lower()


def test_topic_cluster_analysis():
    pages = [
        {
            "url": "https://example.com/ai-agents",
            "data": {"title": "AI Agents Hub", "word_count": 2500},
        },
        {
            "url": "https://example.com/ai-agents/memory",
            "data": {"title": "Agent Memory", "word_count": 800},
        },
        {
            "url": "https://example.com/ai-agents/tools",
            "data": {"title": "Agent Tools", "word_count": 950},
        },
    ]
    page_intents = [
        PageIntentAnalysis("https://example.com/ai-agents", "Hub", "informational", [], "ai agents", [], {}, 0.9),
        PageIntentAnalysis("https://example.com/ai-agents/memory", "Memory", "informational", [], "agent memory", [], {}, 0.9),
        PageIntentAnalysis("https://example.com/ai-agents/tools", "Tools", "informational", [], "agent tools", [], {}, 0.9),
    ]

    clusters = analyze_topic_clusters(pages, page_intents)
    assert len(clusters) == 1
    c = clusters[0]
    assert c.pillar_url == "https://example.com/ai-agents"
    assert len(c.spoke_urls) == 2
    assert c.cluster_health_score > 0.0


def test_content_gaps_and_refresh():
    pages = [
        {
            "url": "https://example.com/thin-page",
            "data": {
                "title": "Old SEO Guide 2021",
                "word_count": 120,
                "main_text": "This is a brief guide from 2021 discussing basic SEO techniques.",
            }
        },
        {
            "url": "https://example.com/comprehensive",
            "data": {
                "title": "Modern Search Architecture",
                "word_count": 1600,
                "main_text": "Detailed modern guide.",
            }
        },
    ]
    heading_audits = [
        HeadingAudit("https://example.com/thin-page", 1, ["Title"], 0, 0, False, [], [], [], ""),
        HeadingAudit("https://example.com/comprehensive", 1, ["Title"], 3, 2, False, [], [], [], ""),
    ]
    page_intents = [
        PageIntentAnalysis("https://example.com/thin-page", "Old SEO", "informational", [], "seo guide", [], {}, 0.8),
        PageIntentAnalysis("https://example.com/comprehensive", "Modern", "informational", [], "search arch", [], {}, 0.9),
    ]

    gaps, refresh = detect_content_gaps_and_refresh(pages, page_intents, heading_audits)
    assert len(refresh) >= 1
    r = refresh[0]
    assert r.url == "https://example.com/thin-page"
    assert r.refresh_priority == "HIGH"
    assert any("thin content" in reason.lower() for reason in r.reasons)
    assert any("2021" in reason for reason in r.reasons)
