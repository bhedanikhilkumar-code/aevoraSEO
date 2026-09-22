"""
Tests for search intent classification and target query extraction.
"""

import pytest
from aevoraseo.search.intent import (
    classify_search_intent,
    extract_target_queries,
)
from aevoraseo.search.models import SearchIntent


def test_classify_transactional_intent():
    url = "https://example.com/checkout"
    title = "Book Dental Implant Consultation | Example Dental"
    h1 = "Schedule Your Appointment"
    body = "Choose your preferred time slot and complete your booking online. Fast, secure checkout."
    schema_types = ["Service"]
    cta_texts = ["Book Consultation Now", "Secure Checkout"]

    result = classify_search_intent(
        url=url,
        title=title,
        h1=h1,
        body_text=body,
        schema_types=schema_types,
        cta_texts=cta_texts,
    )

    assert result.primary_intent == SearchIntent.TRANSACTIONAL.value
    assert "appointment" in result.primary_target_query.lower() or "consultation" in result.primary_target_query.lower()
    assert result.confidence >= 0.7


def test_classify_commercial_investigation_intent():
    url = "https://example.com/dental-implants-vs-dentures"
    title = "Dental Implants vs Dentures: Best Teeth Replacement Options"
    h1 = "Dental Implants vs Dentures Comparison"
    body = "Reviewing features, costs, pros and cons, and ratings between dental implants and removable dentures."
    schema_types = ["AggregateRating"]
    cta_texts = ["Read Full Review", "Compare Options"]

    result = classify_search_intent(
        url=url,
        title=title,
        h1=h1,
        body_text=body,
        schema_types=schema_types,
        cta_texts=cta_texts,
    )

    assert result.primary_intent == SearchIntent.COMMERCIAL_INVESTIGATION.value
    assert "dental implants" in result.primary_target_query.lower() or "dentures" in result.primary_target_query.lower()


def test_classify_informational_intent():
    url = "https://example.com/blog/how-to-care-for-implants"
    title = "How to Care for Dental Implants: Step-by-Step Guide"
    h1 = "How to Care for Dental Implants"
    body = "A comprehensive guide on daily hygiene, brushing techniques, and what to expect during recovery."
    schema_types = ["Article", "BlogPosting"]
    cta_texts = ["Read More", "Share Article"]

    result = classify_search_intent(
        url=url,
        title=title,
        h1=h1,
        body_text=body,
        schema_types=schema_types,
        cta_texts=cta_texts,
    )

    assert result.primary_intent == SearchIntent.INFORMATIONAL.value
    assert "care dental implants" in result.primary_target_query.lower() or "dental implants" in result.primary_target_query.lower()


def test_classify_local_intent():
    url = "https://example.com/locations/arlington-heights"
    title = "Dentist in Arlington Heights | Family & Emergency Clinic"
    h1 = "Arlington Heights Dental Clinic"
    body = "Visit our local clinic near me on Northwest Highway. Open Monday to Saturday with emergency directions."
    schema_types = ["LocalBusiness", "Dentist"]
    cta_texts = ["Call Us", "Get Directions"]

    result = classify_search_intent(
        url=url,
        title=title,
        h1=h1,
        body_text=body,
        schema_types=schema_types,
        cta_texts=cta_texts,
    )

    assert result.primary_intent == SearchIntent.LOCAL.value
    assert "arlington heights" in result.primary_target_query.lower()


def test_classify_navigational_intent():
    url = "https://example.com/about-us"
    title = "About Us | Acme Dental Group"
    h1 = "Our Company History & Leadership Team"
    body = "Learn about Acme Dental Group, our clinical directors, and our mission since 2010."
    schema_types = ["Organization"]
    cta_texts = ["Contact Team"]

    result = classify_search_intent(
        url=url,
        title=title,
        h1=h1,
        body_text=body,
        schema_types=schema_types,
        cta_texts=cta_texts,
    )

    assert result.primary_intent == SearchIntent.NAVIGATIONAL.value


def test_extract_target_queries():
    title = "Best AI Automation Agency in Chicago | Apex AI"
    h1 = "AI Automation Agency in Chicago"
    slug = "ai-automation-agency-chicago"
    desc = "We build custom AI agents and automation workflows for enterprise teams."

    primary, secondaries = extract_target_queries(title, h1, slug, desc)
    assert "ai" in primary.lower()
    assert "automation" in primary.lower()
    assert "agency" in primary.lower()
    assert len(secondaries) >= 1
