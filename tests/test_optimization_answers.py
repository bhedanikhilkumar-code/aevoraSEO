"""
Tests for direct answer opportunities, FAQ objection handling, and schema recommendations.
"""

from aevoraseo.optimization.analyzer import (
    detect_direct_answer_opportunities,
    detect_faq_and_objection_opportunities,
    recommend_schemas,
)
from aevoraseo.search.models import PageIntentAnalysis


def test_direct_answer_opportunity_detection():
    html = """
    <html>
        <body>
            <h1>Complete Guide to Autonomous AI Agents</h1>
            <h2>What is an Autonomous AI Agent?</h2>
            <p>An autonomous AI agent is a software entity capable of perceiving its environment, reasoning over state, formulating plans, and executing actions using external tools without direct turn-by-turn human intervention.</p>
            <h2>How to deploy an AI agent?</h2>
            <ol>
                <li>Define goal and evaluation criteria.</li>
                <li>Connect API tools and permissions.</li>
                <li>Run loop with automated safety verification.</li>
            </ol>
            <h2>Why choose multi-agent orchestration?</h2>
            <p>This is a very long section discussing historical paradigms of machine learning spanning back to 1950 with the Turing test, symbolic reasoning, and deep reinforcement learning that goes on for pages and pages without a concise summary box for users or search crawlers.</p>
        </body>
    </html>
    """
    pages = [{
        "url": "https://example.com/guide",
        "data": {
            "title": "Autonomous AI Agents",
            "headings": {
                "h1": ["Complete Guide to Autonomous AI Agents"],
                "h2": ["What is an Autonomous AI Agent?", "How to deploy an AI agent?", "Why choose multi-agent orchestration?"],
            },
        }
    }]
    html_by_url = {"https://example.com/guide": html}

    opps = detect_direct_answer_opportunities(pages, html_by_url)
    assert len(opps) >= 2

    def_opp = next((o for o in opps if "what is" in o.question_or_topic.lower()), None)
    assert def_opp is not None
    assert def_opp.opportunity_type == "definition"
    assert def_opp.is_answered is True

    proc_opp = next((o for o in opps if "how to" in o.question_or_topic.lower()), None)
    assert proc_opp is not None
    assert proc_opp.opportunity_type == "procedural_list"
    assert proc_opp.is_answered is True


def test_faq_and_objection_opportunities():
    pages = [
        {
            "url": "https://example.com/service/seo-audit",
            "data": {
                "title": "Professional SEO Audit Service",
                "main_text": "We provide comprehensive forensic SEO audits for enterprise platforms and SaaS systems.",
            }
        }
    ]
    page_intents = [
        PageIntentAnalysis(
            url="https://example.com/service/seo-audit",
            title="Professional SEO Audit Service",
            primary_intent="transactional",
            secondary_intents=["commercial_investigation"],
            primary_target_query="seo audit service",
            secondary_queries=[],
            intent_signals={},
            confidence=0.9,
        )
    ]

    faq_opps = detect_faq_and_objection_opportunities(pages, page_intents)
    assert len(faq_opps) >= 2
    f_types = {f.friction_type for f in faq_opps}
    assert "pricing" in f_types
    assert "guarantee" in f_types


def test_recommend_schemas():
    pages = [
        {
            "url": "https://example.com/blog/article-1",
            "data": {
                "title": "How to Build AI Agents",
                "schema_types": ["WebPage"],
                "headings": {"h1": ["How to Build AI Agents"], "h2": ["Step 1", "Step 2"]},
            }
        },
        {
            "url": "https://example.com/services/consulting",
            "data": {
                "title": "Enterprise AI Consulting",
                "schema_types": ["WebPage"],
                "headings": {"h1": ["Enterprise AI Consulting"], "h2": ["What is the fee?"]},
            }
        },
    ]
    page_intents = [
        PageIntentAnalysis(
            url="https://example.com/blog/article-1",
            title="How to Build AI Agents",
            primary_intent="informational",
            secondary_intents=[],
            primary_target_query="build ai agents",
            secondary_queries=[],
            intent_signals={},
            confidence=0.9,
        ),
        PageIntentAnalysis(
            url="https://example.com/services/consulting",
            title="Enterprise AI Consulting",
            primary_intent="transactional",
            secondary_intents=[],
            primary_target_query="enterprise ai consulting",
            secondary_queries=[],
            intent_signals={},
            confidence=0.9,
        ),
    ]

    recs = recommend_schemas(pages, page_intents)
    assert len(recs) == 2

    # Blog page should recommend Article
    assert "Article" in recs[0].recommended_schemas
    assert "Article" in recs[0].missing_schemas

    # Service page with question heading should recommend Service and FAQPage
    assert "Service" in recs[1].recommended_schemas
    assert "Service" in recs[1].missing_schemas
    assert "FAQPage" in recs[1].recommended_schemas
