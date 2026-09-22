"""
Adversarial and security tests for search & commercial intelligence.
"""

from pathlib import Path

from aevoraseo.search.comparison import sanitize_csv_cell
from aevoraseo.search.intent import classify_search_intent, detect_cannibalization, extract_target_queries
from aevoraseo.search.local import audit_local_signals
from aevoraseo.search.models import PageIntentAnalysis, SearchCommercialAnalysisResult
from aevoraseo.search.reporter import export_reports


def test_sanitize_csv_formula_injection():
    dangerous_inputs = [
        "=cmd|'/c calc'!A0",
        "+cmd|'/c calc'!A0",
        "-cmd|'/c calc'!A0",
        "@SUM(1+1)*cmd|' /C calc'!A0",
        "\t=2+5",
        "\r=cmd",
    ]

    for payload in dangerous_inputs:
        sanitized = sanitize_csv_cell(payload)
        assert sanitized.startswith("'"), f"Failed to sanitize CSV injection payload: {payload}"

    safe_text = "Standard Normal Keyword Phrase"
    assert sanitize_csv_cell(safe_text) == safe_text


def test_intent_adversarial_malformed_html():
    malformed_html = """
    <<<>>><script type="application/ld+json">{broken json...}</script>
    <a href="javascript:void(0)" onclick="alert(1)">Click Me</a>
    <h1></h1>
    <title></title>
    """
    res = classify_search_intent(
        url="https://example.com/???///",
        title="",
        h1="",
        body_text=malformed_html,
        schema_types=[],
        cta_texts=[],
    )
    assert res.primary_intent in ("Informational", "Navigational", "Unknown")
    assert res.confidence >= 0.0


def test_local_signals_malformed_jsonld_and_cycles():
    broken_html = """
    <script type="application/ld+json">
    {"@type": "LocalBusiness", "name": "Test", "telephone": [123, null], "address": 456}
    </script>
    <script type="application/ld+json">
    [[[[broken
    </script>
    """
    res = audit_local_signals("https://example.com/clinic", broken_html)
    assert res.has_local_business_schema is True
    assert res.name == "Test"


def test_cannibalization_empty_or_single_page():
    assert detect_cannibalization([]) == []
    p = PageIntentAnalysis(url="https://example.com", title="", primary_intent="Informational")
    assert detect_cannibalization([p]) == []


def test_export_reports_with_adversarial_data(tmp_path: Path):
    result = SearchCommercialAnalysisResult(
        target_url="https://example.com/=cmd|'/c calc'!A0",
        brand_name="@EvilCorp",
        created_at="2026-09-22T00:00:00Z",
        pages_analyzed=1,
        page_intents=[
            {
                "url": "+calc",
                "primary_intent": "Transactional",
                "primary_target_query": "=SUM(A1:A10)",
                "secondary_queries": ["-attack", "@cmd"],
                "confidence": 0.9,
            }
        ],
        cannibalization_issues=[
            {
                "query": "=DDE('cmd';'/c calc';'__'!A0)",
                "intent": "Transactional",
                "risk_level": "HIGH",
                "similarity_score": 1.0,
                "competing_urls": ["https://example.com/1", "https://example.com/2"],
                "recommendation": "=HYPERLINK('http://evil.com','Click Me')",
            }
        ],
        local_signals=[],
        commercial_journeys=[],
        comparison_pages=[],
        score={"headline": 50.0, "confidence": "medium"},
    )

    export_reports(result, tmp_path, snapshot_id="adversarial_test")

    # Verify CSV files are properly neutralized
    page_intents_csv = (tmp_path / "page-intents.csv").read_text(encoding="utf-8-sig")
    assert "'=SUM(A1:A10)" in page_intents_csv or "'=SUM" in page_intents_csv
    assert "'+calc" in page_intents_csv

    cannibal_csv = (tmp_path / "cannibalization.csv").read_text(encoding="utf-8-sig")
    assert "'=DDE" in cannibal_csv
    assert "'=HYPERLINK" in cannibal_csv
