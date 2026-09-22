"""
Deterministic 0–100 AevoraSEO Search & Commercial Visibility Scoring Model.
"""

from typing import Any, Dict, List

from .models import (
    CannibalizationCandidate,
    CommercialJourneyAnalysis,
    ComparisonSupportAnalysis,
    LocalSignalAnalysis,
    PageIntentAnalysis,
    SearchCommercialScore,
)


def compute_search_commercial_score(
    page_intents: List[PageIntentAnalysis],
    cannibalizations: List[CannibalizationCandidate],
    local_signals: List[LocalSignalAnalysis],
    commercial_journeys: List[CommercialJourneyAnalysis],
    comparison_pages: List[ComparisonSupportAnalysis],
) -> SearchCommercialScore:
    """
    Computes a deterministic 0–100 score across 4 distinct 25-point dimensions:
    1. Intent & Query Targeting (0-25)
    2. Commercial Journey & CTA Readiness (0-25)
    3. Local Visibility & Service-Area Signals (0-25)
    4. Comparison & Buyer Decision Support (0-25)
    """
    contributing_factors: Dict[str, float] = {}
    deductions: List[str] = []

    # -------------------------------------------------------------
    # Dimension 1: Intent & Query Targeting (0 - 25)
    # -------------------------------------------------------------
    d1 = 0.0
    if page_intents:
        # High confidence in intent classification
        avg_confidence = sum(p.confidence for p in page_intents) / len(page_intents)
        d1 += min(8.0, avg_confidence * 8.0)

        # Non-generic primary target queries
        specific_queries = sum(1 for p in page_intents if p.primary_target_query and p.primary_target_query != "general")
        ratio = specific_queries / len(page_intents)
        d1 += min(9.0, ratio * 9.0)
    else:
        d1 += 0.0

    # Cannibalization deductions
    cannibalization_points = 8.0
    for c in cannibalizations:
        if c.risk_level == "HIGH":
            cannibalization_points -= 4.0
            deductions.append(f"High-risk keyword cannibalization on '{c.query}' across {len(c.competing_urls)} URLs (-4.0)")
        elif c.risk_level == "MEDIUM":
            cannibalization_points -= 2.0
            deductions.append(f"Moderate keyword overlap on '{c.query}' (-2.0)")

    d1 += max(0.0, cannibalization_points)
    contributing_factors["intent_query_targeting"] = round(min(25.0, max(0.0, d1)), 1)

    # -------------------------------------------------------------
    # Dimension 2: Commercial Journey & CTA Readiness (0 - 25)
    # -------------------------------------------------------------
    d2 = 0.0
    if commercial_journeys:
        # High-intent specific CTAs
        pages_with_high_cta = sum(1 for c in commercial_journeys if c.high_intent_ctas)
        high_cta_ratio = pages_with_high_cta / len(commercial_journeys)
        d2 += min(9.0, high_cta_ratio * 9.0)

        # Trust proofs present
        pages_with_trust = sum(1 for c in commercial_journeys if c.trust_signals)
        trust_ratio = pages_with_trust / len(commercial_journeys)
        d2 += min(6.0, trust_ratio * 6.0)

        # Direct communication channels (phone, WhatsApp, booking)
        direct_channels = sum(1 for c in commercial_journeys if c.has_phone_call_action or c.has_messaging_action or c.has_booking_action)
        direct_ratio = direct_channels / len(commercial_journeys)
        d2 += min(5.0, direct_ratio * 5.0)

        # Low form friction / clear next steps
        friction_penalties = sum(len(c.friction_issues) for c in commercial_journeys)
        friction_points = max(0.0, 5.0 - (friction_penalties * 1.5))
        d2 += friction_points
        for c in commercial_journeys:
            for issue in c.friction_issues:
                if len(deductions) < 8:
                    deductions.append(f"{c.url}: {issue}")
    else:
        d2 += 0.0

    contributing_factors["commercial_journey_cta"] = round(min(25.0, max(0.0, d2)), 1)

    # -------------------------------------------------------------
    # Dimension 3: Local Visibility & Service-Area Signals (0 - 25)
    # -------------------------------------------------------------
    d3 = 0.0
    has_local_intent = any(p.primary_intent == "Local" or "Local" in p.secondary_intents for p in page_intents)
    pages_with_local_schema = sum(1 for l in local_signals if l.has_local_business_schema)
    pages_with_nap = sum(1 for l in local_signals if l.nap_present)
    pages_with_click_tel = sum(1 for l in local_signals if l.has_clickable_tel)
    pages_with_map = sum(1 for l in local_signals if l.has_map_embed_or_link)
    has_service_areas = any(len(l.service_areas_declared) > 0 for l in local_signals)

    if pages_with_local_schema:
        d3 += 10.0
    elif has_local_intent:
        deductions.append("Local search intent detected but LocalBusiness schema is missing (-10.0)")

    if pages_with_nap:
        d3 += 5.0
    if pages_with_click_tel or pages_with_map:
        d3 += 5.0
    if has_service_areas:
        d3 += 5.0

    # If site is not a local business and has no local intent, normalize fairly
    if not has_local_intent and not pages_with_local_schema:
        # Default baseline for purely national/digital services
        d3 = 15.0  # Fair neutral baseline for non-local websites
        contributing_factors["local_visibility_signals"] = 15.0
    else:
        contributing_factors["local_visibility_signals"] = round(min(25.0, max(0.0, d3)), 1)

    # -------------------------------------------------------------
    # Dimension 4: Comparison & Buyer Decision Support (0 - 25)
    # -------------------------------------------------------------
    d4 = 0.0
    buyer_questions_count = sum(len(c.buyer_questions_answered) for c in comparison_pages)
    if buyer_questions_count >= 3:
        d4 += 10.0
    elif buyer_questions_count > 0:
        d4 += 5.0
    else:
        deductions.append("Missing buyer question / FAQ coverage addressing purchase objections (-5.0)")

    # Pricing transparency
    pricing_transparency_types = {c.pricing_transparency for c in commercial_journeys}
    if "transparent_pricing" in pricing_transparency_types:
        d4 += 8.0
    elif "custom_quote" in pricing_transparency_types:
        d4 += 5.0

    # Comparison support
    has_comparison = any(c.is_comparison_page or c.has_comparison_table for c in comparison_pages)
    if has_comparison:
        d4 += 7.0
    else:
        # If site has alternative evaluations or multi-tier services
        d4 += 3.0

    contributing_factors["comparison_buyer_support"] = round(min(25.0, max(0.0, d4)), 1)

    # -------------------------------------------------------------
    # Total Score & Confidence
    # -------------------------------------------------------------
    headline = sum(contributing_factors.values())
    headline = round(min(100.0, max(0.0, headline)), 1)

    page_count = len(page_intents)
    if page_count >= 5:
        confidence = "high"
    elif page_count >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return SearchCommercialScore(
        headline=headline,
        intent_query_targeting=contributing_factors["intent_query_targeting"],
        commercial_journey_cta=contributing_factors["commercial_journey_cta"],
        local_visibility_signals=contributing_factors["local_visibility_signals"],
        comparison_buyer_support=contributing_factors["comparison_buyer_support"],
        contributing_factors=contributing_factors,
        deductions=deductions[:10],
        confidence=confidence,
    )
