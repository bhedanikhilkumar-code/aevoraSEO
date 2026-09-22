"""
Tests for keyword cannibalization detection across internal URLs.
"""

from aevoraseo.search.intent import detect_cannibalization
from aevoraseo.search.models import PageIntentAnalysis


def test_detect_high_risk_cannibalization():
    p1 = PageIntentAnalysis(
        url="https://example.com/dental-implants",
        title="Dental Implants Arlington Heights",
        primary_intent="Transactional",
        primary_target_query="dental implants arlington heights",
        confidence=0.9,
    )
    p2 = PageIntentAnalysis(
        url="https://example.com/services/implant-dentist",
        title="Dental Implants Arlington Heights Service",
        primary_intent="Transactional",
        primary_target_query="dental implants arlington heights",
        confidence=0.85,
    )

    candidates = detect_cannibalization([p1, p2])
    assert len(candidates) == 1
    c = candidates[0]
    assert c.risk_level == "HIGH"
    assert c.similarity_score == 1.0
    assert "https://example.com/dental-implants" in c.competing_urls
    assert "https://example.com/services/implant-dentist" in c.competing_urls
    assert "consolidate" in c.recommendation.lower()


def test_detect_medium_risk_cannibalization():
    p1 = PageIntentAnalysis(
        url="https://example.com/teeth-whitening-cost",
        title="Teeth Whitening Cost and Pricing",
        primary_intent="Transactional",
        primary_target_query="teeth whitening cost pricing",
        confidence=0.85,
    )
    p2 = PageIntentAnalysis(
        url="https://example.com/professional-teeth-whitening",
        title="Professional Teeth Whitening Cost",
        primary_intent="Transactional",
        primary_target_query="teeth whitening cost",
        confidence=0.8,
    )

    candidates = detect_cannibalization([p1, p2])
    assert len(candidates) == 1
    c = candidates[0]
    assert c.risk_level in ("HIGH", "MEDIUM")
    assert c.similarity_score >= 0.70


def test_no_cannibalization_for_distinct_topics():
    p1 = PageIntentAnalysis(
        url="https://example.com/dental-implants",
        title="Dental Implants Arlington Heights",
        primary_intent="Transactional",
        primary_target_query="dental implants arlington heights",
        confidence=0.9,
    )
    p2 = PageIntentAnalysis(
        url="https://example.com/root-canal",
        title="Emergency Root Canal Treatment",
        primary_intent="Transactional",
        primary_target_query="emergency root canal treatment",
        confidence=0.88,
    )

    candidates = detect_cannibalization([p1, p2])
    assert len(candidates) == 0
