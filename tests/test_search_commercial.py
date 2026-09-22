"""
Tests for commercial conversion journeys, CTA friction, and comparison decision support.
"""

from aevoraseo.search.commercial import (
    audit_comparison_support,
    audit_commercial_journey,
)


def test_audit_commercial_journey_strong_ctas_and_trust():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Dental Implants Service</title></head>
    <body>
        <h1>Permanent Dental Implants</h1>
        <p>Rated 4.9/5 by 350+ verified patient reviews. Board certified oral surgeons.</p>
        <p>Includes 100% satisfaction guarantee and lifetime implant warranty.</p>
        <a class="btn btn-primary" href="/book">Book Dental Implant Consultation</a>
        <a href="tel:+18475550199">Call Us Now</a>
        <a href="https://wa.me/18475550199">Chat on WhatsApp</a>
        <p>Starting at $1,499 with 0% financing available.</p>
    </body>
    </html>
    """

    res = audit_commercial_journey(
        url="https://example.com/dental-implants",
        html=html,
        primary_intent="Transactional",
    )

    assert res.page_type == "service_page"
    assert len(res.high_intent_ctas) >= 1
    assert any("Book Dental Implant Consultation" in c["text"] for c in res.high_intent_ctas)
    assert res.has_phone_call_action is True
    assert res.has_messaging_action is True
    assert len(res.trust_signals) >= 2
    assert res.pricing_transparency == "transparent_pricing"
    assert len(res.friction_issues) == 0


def test_audit_commercial_journey_high_friction_and_weak_ctas():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Our Services</title></head>
    <body>
        <h1>Medical Consultation</h1>
        <button>Click Here</button>
        <button>Learn More</button>
        <button>Submit</button>
        <form action="/submit" method="POST">
            <input type="text" name="name" />
            <input type="text" name="email" />
            <input type="text" name="phone" />
            <input type="text" name="company" />
            <input type="text" name="budget" />
            <input type="text" name="notes" />
            <input type="text" name="referral" />
            <input type="submit" value="Send Form" />
        </form>
    </body>
    </html>
    """

    res = audit_commercial_journey(
        url="https://example.com/services/consultation",
        html=html,
        primary_intent="Transactional",
    )

    assert len(res.generic_ctas) >= 2
    assert any("High form friction" in issue for issue in res.friction_issues)
    assert any("Missing direct mobile communication" in issue for issue in res.friction_issues)
    assert any("Missing trust proof" in issue for issue in res.friction_issues)


def test_audit_comparison_support():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>HubSpot vs Salesforce Comparison</title></head>
    <body>
        <h1>HubSpot vs Salesforce: 2026 In-Depth Comparison</h1>
        <table>
            <tr><th>Feature</th><th>HubSpot</th><th>Salesforce</th></tr>
            <tr><td>Ease of Use</td><td>High</td><td>Moderate</td></tr>
            <tr><td>Setup Time</td><td>Days</td><td>Months</td></tr>
        </table>
        <h2>Frequently Asked Buyer Questions</h2>
        <p>How much does it cost? HubSpot starts at $50/mo while Salesforce requires custom quotes.</p>
        <p>Is there a warranty? Both offer 30-day trial guarantees.</p>
        <p>How do I get started with onboarding?</p>
    </body>
    </html>
    """

    res = audit_comparison_support(
        url="https://example.com/vs/hubspot-vs-salesforce",
        html=html,
        primary_intent="Commercial Investigation",
    )

    assert res.is_comparison_page is True
    assert res.has_comparison_table is True
    assert len(res.buyer_questions_answered) >= 2
