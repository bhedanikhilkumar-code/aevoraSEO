"""
Tests for Title, Meta Description, and Heading Architecture audits.
"""

from aevoraseo.optimization.analyzer import (
    audit_headings,
    audit_meta_descriptions,
    audit_titles,
)


def test_title_audit_optimal():
    pages = [{
        "url": "https://example.com/ai-agents",
        "data": {
            "title": "Autonomous AI Agents Strategy Guide & Workflow | Aevora",
            "headings": {"h1": ["Autonomous AI Agents Strategy"]},
            "meta_description": "Comprehensive guide to autonomous AI agent workflows.",
        }
    }]
    audits = audit_titles(pages, brand="Aevora")
    assert len(audits) == 1
    a = audits[0]
    assert a.status == "optimal"
    assert a.brand_detected is True
    assert a.brand_position == "end"
    assert a.keyword_stuffed is False
    assert a.query_overlap is True


def test_title_audit_too_short_and_missing():
    pages = [
        {"url": "https://example.com/short", "data": {"title": "Short", "headings": {"h1": ["Short"]}}},
        {"url": "https://example.com/empty", "data": {"title": "", "headings": {"h1": ["Empty"]}}},
    ]
    audits = audit_titles(pages, brand="Aevora")
    assert audits[0].status == "too_short"
    assert audits[1].status == "missing"


def test_title_audit_too_long_and_stuffed():
    pages = [{
        "url": "https://example.com/stuffed",
        "data": {
            "title": "SEO Agency SEO Services Best SEO Expert SEO Consultant Pakistan Agency Aevora",
            "headings": {"h1": ["SEO Agency Pakistan"]},
        }
    }]
    audits = audit_titles(pages, brand="Aevora")
    a = audits[0]
    assert a.status == "too_long"
    assert a.keyword_stuffed is True
    assert "repetitive" in a.recommendation.lower()


def test_meta_description_audit():
    pages = [
        {
            "url": "https://example.com/page1",
            "data": {
                "title": "Dental Implants",
                "meta_description": "Discover permanent dental implants in Lahore with guaranteed precision. Book your consultation today with our board-certified experts.",
            }
        },
        {
            "url": "https://example.com/page2",
            "data": {
                "title": "Teeth Whitening",
                "meta_description": "Teeth whitening services.",
            }
        },
        {
            "url": "https://example.com/page3",
            "data": {
                "title": "Root Canal",
                "meta_description": "",
            }
        },
    ]
    audits = audit_meta_descriptions(pages, brand="Clinic")
    assert len(audits) == 3

    assert audits[0].status == "optimal"
    assert audits[0].has_cta is True
    assert "book" in audits[0].cta_phrases or "discover" in audits[0].cta_phrases

    assert audits[1].status == "too_short"
    assert audits[1].has_cta is False

    assert audits[2].status == "missing"


def test_heading_audit_single_and_skipped():
    html_normal = """
    <html>
        <body>
            <h1>Primary Guide Title</h1>
            <h2>Section One</h2>
            <p>Content</p>
            <h3>Subsection 1.1</h3>
            <p>Content</p>
            <h2>Section Two</h2>
        </body>
    </html>
    """

    html_skipped = """
    <html>
        <body>
            <h1>Primary Guide Title</h1>
            <h3>Direct Subheading without H2</h3>
            <p>Content</p>
            <h4>Sub-subheading without H3</h4>
            <h2></h2>
        </body>
    </html>
    """

    pages = [
        {
            "url": "https://example.com/normal",
            "data": {
                "headings": {"h1": ["Primary Guide Title"], "h2": ["Section One", "Section Two"], "h3": ["Subsection 1.1"]}
            }
        },
        {
            "url": "https://example.com/skipped",
            "data": {
                "headings": {"h1": ["Primary Guide Title"], "h2": [""], "h3": ["Direct Subheading without H2"], "h4": ["Sub-subheading without H3"]}
            }
        },
    ]
    html_by_url = {
        "https://example.com/normal": html_normal,
        "https://example.com/skipped": html_skipped,
    }

    audits = audit_headings(pages, html_by_url)
    assert len(audits) == 2

    # Normal
    assert audits[0].h1_count == 1
    assert audits[0].has_skipped_levels is False
    assert len(audits[0].empty_headings) == 0

    # Skipped
    assert audits[1].h1_count == 1
    assert audits[1].has_skipped_levels is True
    assert len(audits[1].empty_headings) >= 1
    assert len(audits[1].skipped_hierarchy_issues) >= 1
