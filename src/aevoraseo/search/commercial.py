"""
Commercial conversion journeys, call-to-action friction audits, and comparison page templates.
"""

import re
from typing import Any, Dict, List, Set
from urllib.parse import urlsplit

from .models import CommercialJourneyAnalysis, ComparisonSupportAnalysis

HIGH_INTENT_CTA_PATTERNS = [
    re.compile(r"\bbook\s+(?:appointment|consultation|demo|now|visit)\b", re.IGNORECASE),
    re.compile(r"\bschedule\s+(?:consultation|appointment|call|demo)\b", re.IGNORECASE),
    re.compile(r"\b(?:get|request)\s+(?:free\s+)?(?:quote|audit|estimate|proposal)\b", re.IGNORECASE),
    re.compile(r"\b(?:start|try)\s+(?:free\s+)?(?:trial|now)\b", re.IGNORECASE),
    re.compile(r"\b(?:order|buy)\s+now\b", re.IGNORECASE),
    re.compile(r"\bclaim\s+(?:offer|discount|spot)\b", re.IGNORECASE),
    re.compile(r"\benroll\s+(?:now|today)\b", re.IGNORECASE),
    re.compile(r"\bcall\s+(?:us|now|today|\d)\b", re.IGNORECASE),
]

GENERIC_CTA_PATTERNS = [
    re.compile(r"^click\s+here$", re.IGNORECASE),
    re.compile(r"^learn\s+more$", re.IGNORECASE),
    re.compile(r"^submit$", re.IGNORECASE),
    re.compile(r"^read\s+more$", re.IGNORECASE),
    re.compile(r"^more\s+info$", re.IGNORECASE),
    re.compile(r"^continue$", re.IGNORECASE),
    re.compile(r"^view\s+more$", re.IGNORECASE),
]

TRUST_SIGNALS_PATTERNS = [
    ("Customer reviews / ratings", re.compile(r"(?:★{3,5}|(?:[45]\.\d\s*/\s*5)|(?:rated\s+[45]\.\d)|(?:customer\s+reviews?)|(?:verified\s+patient\s+reviews?))", re.IGNORECASE)),
    ("Professional credentials", re.compile(r"(?:board\s+certified|licensed|dds|dmd|md|phd|certified\s+practitioner|years\s+of\s+experience)", re.IGNORECASE)),
    ("Satisfaction guarantee", re.compile(r"(?:money-back\s+guarantee|satisfaction\s+guarantee|warranty|risk-free)", re.IGNORECASE)),
    ("Security & privacy reassurance", re.compile(r"(?:hipaa\s+compliant|ssl\s+secured|safe\s+checkout|privacy\s+guaranteed|no\s+spam\s+promise)", re.IGNORECASE)),
    ("Client proof / logos", re.compile(r"(?:trusted\s+by|as\s+seen\s+on|featured\s+in|case\s+studies|our\s+clients)", re.IGNORECASE)),
]

BUYER_QUESTION_PATTERNS = [
    re.compile(r"how\s+much\s+(?:does|is|do)\b", re.IGNORECASE),
    re.compile(r"what\s+is\s+included\b", re.IGNORECASE),
    re.compile(r"how\s+long\s+does\s+it\s+take\b", re.IGNORECASE),
    re.compile(r"is\s+there\s+a\s+warranty\b", re.IGNORECASE),
    re.compile(r"what\s+happens\s+after\b", re.IGNORECASE),
    re.compile(r"do\s+you\s+offer\s+financing\b", re.IGNORECASE),
    re.compile(r"can\s+i\s+cancel\b", re.IGNORECASE),
    re.compile(r"how\s+do\s+i\s+get\s+started\b", re.IGNORECASE),
]

BOOKING_DOMAINS = ["calendly.com", "acuityscheduling.com", "hubspot.com/meetings", "tidycal.com", "zocdoc.com"]
WHATSAPP_PATTERNS = ["wa.me", "api.whatsapp.com", "whatsapp.com/send"]


def extract_cta_elements(html: str) -> List[Dict[str, str]]:
    """Extract buttons, links styled as buttons, and form submit actions."""
    ctas: List[Dict[str, str]] = []

    # 1. <button> tags
    button_regex = re.compile(r"""<button[^>]*>(.*?)</button>""", re.IGNORECASE | re.DOTALL)
    for match in button_regex.finditer(html):
        text = re.sub(r"<[^>]+>", " ", match.group(1)).strip()
        if text and len(text) <= 60:
            ctas.append({"text": text, "type": "button"})

    # 2. <input type="submit|button">
    input_regex = re.compile(r"""<input[^>]*type\s*=\s*['"](?:submit|button)['"][^>]*value\s*=\s*['"]([^'"]+)['"]""", re.IGNORECASE)
    for match in input_regex.finditer(html):
        text = match.group(1).strip()
        if text:
            ctas.append({"text": text, "type": "input_submit"})

    # 3. <a ... class="...btn|cta|button...">
    link_cta_regex = re.compile(r"""<a\s+[^>]*class\s*=\s*['"][^'"]*(?:btn|cta|button|btn-primary)[^'"]*['"][^>]*href\s*=\s*['"]([^'"]*)['"][^>]*>(.*?)</a>""", re.IGNORECASE | re.DOTALL)
    for match in link_cta_regex.finditer(html):
        href = match.group(1).strip()
        text = re.sub(r"<[^>]+>", " ", match.group(2)).strip()
        if text and len(text) <= 60:
            ctas.append({"text": text, "href": href, "type": "link_button"})

    return ctas


def audit_commercial_journey(
    url: str,
    html: str,
    primary_intent: str,
) -> CommercialJourneyAnalysis:
    """
    Audits commercial conversion journey, CTA friction, trust proofs, and pricing transparency.
    """
    parsed = urlsplit(url)
    path = parsed.path.lower()

    # Determine page type
    if "/vs/" in path or "-vs-" in path or "comparison" in path or "alternatives" in path:
        page_type = "comparison_page"
    elif "/pricing" in path or "/plans" in path or "/cost" in path:
        page_type = "pricing_page"
    elif "/product" in path or "/shop" in path or "/cart" in path:
        page_type = "product_page"
    elif "/service" in path or "/dental-" in path or "/implant" in path or "/treatment" in path:
        page_type = "service_page"
    elif "/contact" in path or "/quote" in path or "/book" in path or "/consultation" in path:
        page_type = "lead_gen_page"
    elif primary_intent in ("Transactional", "Commercial Investigation"):
        page_type = "service_page"
    else:
        page_type = "content_page"

    raw_ctas = extract_cta_elements(html)
    high_intent: List[Dict[str, str]] = []
    generic: List[Dict[str, str]] = []

    for cta in raw_ctas:
        text = cta["text"]
        is_high = any(p.search(text) for p in HIGH_INTENT_CTA_PATTERNS)
        is_gen = any(p.search(text) for p in GENERIC_CTA_PATTERNS)

        if is_high:
            high_intent.append(cta)
        elif is_gen:
            generic.append(cta)
        elif len(text.split()) >= 2:
            # Multi-word action buttons default to positive consideration
            high_intent.append(cta)

    # Check direct communication channels
    has_phone = bool(re.search(r"""href\s*=\s*['"]tel:""", html, re.IGNORECASE))
    has_whatsapp = any(w in html.lower() for w in WHATSAPP_PATTERNS)
    has_booking = any(d in html.lower() for d in BOOKING_DOMAINS) or "calendar" in html.lower()

    # Trust signals
    trust_signals: List[str] = []
    for label, pat in TRUST_SIGNALS_PATTERNS:
        if pat.search(html):
            trust_signals.append(label)

    # Friction audit
    friction_issues: List[str] = []
    form_matches = re.findall(r"""<form[^>]*>(.*?)</form>""", html, re.IGNORECASE | re.DOTALL)
    for form_content in form_matches:
        inputs = re.findall(r"""<(?:input|select|textarea)\b[^>]*>""", form_content, re.IGNORECASE)
        # Filter out hidden or csrf tokens
        visible_inputs = [i for i in inputs if not re.search(r"""type\s*=\s*['"]hidden['"]""", i, re.IGNORECASE)]
        if len(visible_inputs) > 5:
            friction_issues.append(f"High form friction: form contains {len(visible_inputs)} visible input fields (recommend <= 4)")

    if page_type in ("service_page", "lead_gen_page", "pricing_page", "product_page"):
        if not raw_ctas and not has_phone and not has_booking:
            friction_issues.append("Missing primary call-to-action: no buttons or direct conversion links found")
        if not has_phone and not has_whatsapp:
            friction_issues.append("Missing direct mobile communication: neither clickable phone (tel:) nor WhatsApp link detected")
        if not trust_signals:
            friction_issues.append("Missing trust proof near conversion points: no visible reviews, credentials, or guarantees")

    # Pricing transparency
    pricing_transparency = "no_pricing_info"
    if re.search(r"""[\$€£₹]\s*\d+(?:,\d{3})*(?:\.\d{2})?""", html) or re.search(r"""(?:pkr|usd|eur|gbp)\s*\d+""", html, re.IGNORECASE):
        pricing_transparency = "transparent_pricing"
    elif "request quote" in html.lower() or "custom pricing" in html.lower() or "contact for pricing" in html.lower():
        pricing_transparency = "custom_quote"

    return CommercialJourneyAnalysis(
        url=url,
        page_type=page_type,
        cta_count=len(raw_ctas),
        high_intent_ctas=high_intent,
        generic_ctas=generic,
        friction_issues=friction_issues,
        trust_signals=trust_signals,
        has_phone_call_action=has_phone,
        has_messaging_action=has_whatsapp,
        has_booking_action=has_booking,
        pricing_transparency=pricing_transparency,
    )


def audit_comparison_support(
    url: str,
    html: str,
    primary_intent: str,
) -> ComparisonSupportAnalysis:
    """
    Audits whether comparison and commercial investigation pages offer
    thorough decision support, feature matrices, and buyer FAQ coverage.
    """
    parsed = urlsplit(url)
    path = parsed.path.lower()
    is_comparison = "/vs/" in path or "-vs-" in path or "comparison" in path or "alternatives" in path or "versus" in path

    # Check for feature comparison tables
    has_table = "<table" in html.lower()

    # Extract evaluated alternatives / brand mentions
    alternatives: List[str] = []
    vs_matches = re.findall(r"""([a-zA-Z0-9\s]{3,20})\s+vs\.?\s+([a-zA-Z0-9\s]{3,20})""", html, re.IGNORECASE)
    for m1, m2 in vs_matches:
        cand1, cand2 = m1.strip(), m2.strip()
        if cand1 and cand1 not in alternatives:
            alternatives.append(cand1)
        if cand2 and cand2 not in alternatives:
            alternatives.append(cand2)

    # Buyer questions answered
    buyer_questions: List[str] = []
    for pat in BUYER_QUESTION_PATTERNS:
        match = pat.search(html)
        if match:
            # Capture the sentence or snippet
            start = max(0, match.start() - 10)
            end = min(len(html), match.end() + 60)
            snippet = re.sub(r"<[^>]+>", "", html[start:end]).strip()
            buyer_questions.append(snippet[:80])

    return ComparisonSupportAnalysis(
        url=url,
        is_comparison_page=is_comparison,
        has_comparison_table=has_table,
        alternatives_evaluated=alternatives[:5],
        buyer_questions_answered=buyer_questions[:5],
    )
