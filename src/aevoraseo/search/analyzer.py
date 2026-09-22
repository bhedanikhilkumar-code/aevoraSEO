"""
Search, Local & Commercial Intelligence Coordinator.
Analyzes crawl snapshots or target URLs to extract intent, detect cannibalization,
audit local visibility signals, and evaluate commercial conversion journeys.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlsplit

from ..review import selected_data
from .commercial import audit_comparison_support, audit_commercial_journey
from .intent import classify_search_intent, detect_cannibalization
from .local import audit_local_signals
from .models import (
    CommercialJourneyAnalysis,
    ComparisonSupportAnalysis,
    LocalSignalAnalysis,
    PageIntentAnalysis,
    SearchCommercialAnalysisResult,
)
from .reporter import export_reports
from .scoring import compute_search_commercial_score


def extract_page_html_and_metadata(page: Dict[str, Any]) -> Tuple[str, str, str, str, List[str], List[str]]:
    """
    Extracts (url, html, title, h1, schema_types, cta_texts) from a page record.
    """
    data, rendered = selected_data(page)
    url = page.get("final_url") or page.get("url") or ""

    html = page.get("html") or ""
    if not html and isinstance(data, dict):
        html = data.get("html") or ""

    # Title
    title = ""
    if isinstance(data, dict):
        title = data.get("title") or ""
    if not title and html:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r"<[^>]+>", " ", m.group(1)).strip()

    # H1
    h1 = ""
    if isinstance(data, dict):
        headings = data.get("headings") or {}
        h1s = headings.get("h1") or []
        if h1s:
            h1 = h1s[0]
    if not h1 and html:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        if m:
            h1 = re.sub(r"<[^>]+>", " ", m.group(1)).strip()

    # Schema types
    schema_types: List[str] = []
    if isinstance(data, dict):
        for s in data.get("schema") or []:
            if isinstance(s, dict) and "@type" in s:
                raw_t = s["@type"]
                if isinstance(raw_t, str):
                    schema_types.append(raw_t)
                elif isinstance(raw_t, list):
                    schema_types.extend([str(x) for x in raw_t if isinstance(x, str)])

    # CTA texts
    cta_texts: List[str] = []
    btn_matches = re.findall(r"<(?:button|a)[^>]*>(.*?)</(?:button|a)>", html, re.IGNORECASE | re.DOTALL)
    for b in btn_matches:
        clean_b = re.sub(r"<[^>]+>", " ", b).strip()
        if clean_b and len(clean_b) <= 40:
            cta_texts.append(clean_b)

    return url, html, title, h1, schema_types, cta_texts


def synthesize_recommendations(
    cannibalizations: List[Any],
    local_signals: List[LocalSignalAnalysis],
    commercial_journeys: List[CommercialJourneyAnalysis],
    comparison_pages: List[ComparisonSupportAnalysis],
    score: Any,
) -> List[str]:
    """Synthesizes actionable, evidence-based recommendations."""
    recs: List[str] = []

    # Cannibalization fixes
    for c in cannibalizations:
        if c.risk_level == "HIGH":
            recs.append(f"Resolve high-risk keyword cannibalization on '{c.query}': consolidate competing pages into primary canonical URL.")

    # Commercial CTA & friction fixes
    for comm in commercial_journeys:
        if comm.page_type in ("service_page", "lead_gen_page", "pricing_page"):
            if not comm.high_intent_ctas:
                recs.append(f"Add high-intent specific CTA to '{comm.url}' (e.g. 'Book Consultation' or 'Get Free Quote').")
            if not comm.trust_signals:
                recs.append(f"Position visible trust proof (reviews, ratings, or doctor/expert credentials) near CTAs on '{comm.url}'.")
            if not comm.has_phone_call_action and not comm.has_messaging_action:
                recs.append(f"Enable direct mobile communication on '{comm.url}' with clickable telephone (tel:) or WhatsApp button.")
            for issue in comm.friction_issues:
                if "form friction" in issue.lower():
                    recs.append(f"Shorten form fields on '{comm.url}' to reduce lead conversion friction.")

    # Local SEO fixes
    has_local_pages = any(loc.has_local_business_schema or loc.nap_present for loc in local_signals)
    if has_local_pages:
        missing_schema = [loc for loc in local_signals if loc.nap_present and not loc.has_local_business_schema]
        for m in missing_schema:
            recs.append(f"Add Schema.org LocalBusiness structured data with openingHours and geo coordinates to '{m.url}'.")

        missing_tels = [loc for loc in local_signals if loc.phone and not loc.has_clickable_tel]
        for mt in missing_tels:
            recs.append(f"Convert plain text phone number '{mt.phone}' on '{mt.url}' to clickable <a href='tel:...'> link.")

    # Buyer question support
    total_buyer_faqs = sum(len(c.buyer_questions_answered) for c in comparison_pages)
    if total_buyer_faqs < 2:
        recs.append("Add structured Buyer FAQ section answering common objections (pricing, process, turnaround, warranties).")

    return recs[:8]


def analyze_search_snapshot(
    snapshot_dir: Path,
    out_dir: Optional[Path] = None,
    brand: str = "",
) -> SearchCommercialAnalysisResult:
    """
    Analyzes an existing crawl snapshot directory for search intent, keyword cannibalization,
    local visibility signals, and commercial conversion friction.
    """
    snap_path = Path(snapshot_dir)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot directory does not exist: {snap_path}")

    summary: Dict[str, Any] = {}
    summary_file = snap_path / "summary.json"
    if summary_file.exists():
        try:
            summary = json.loads(summary_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    target_url = summary.get("url") or summary.get("seed_url") or ""
    brand_name = brand or summary.get("brand") or (urlsplit(target_url).hostname or "").removeprefix("www.")

    pages_raw: List[Dict[str, Any]] = []
    pages_file = snap_path / "pages.jsonl"
    if pages_file.exists():
        with pages_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        pages_raw.append(json.loads(line))
                    except Exception:
                        pass
    elif (snap_path / "crawl.sqlite3").exists():
        import sqlite3
        conn = sqlite3.connect(str(snap_path / "crawl.sqlite3"))
        try:
            cur = conn.cursor()
            rows = cur.execute("SELECT url, data_json, rendered_json, html FROM pages").fetchall()
            for url, data_str, rend_str, html in rows:
                p_dict = {"url": url, "html": html}
                if data_str:
                    try:
                        p_dict["data"] = json.loads(data_str)
                    except Exception:
                        pass
                if rend_str:
                    try:
                        p_dict["rendered"] = json.loads(rend_str)
                    except Exception:
                        pass
                pages_raw.append(p_dict)
        finally:
            conn.close()

    if not target_url and pages_raw:
        target_url = pages_raw[0].get("final_url") or pages_raw[0].get("url") or ""

    if not brand_name and target_url:
        brand_name = (urlsplit(target_url).hostname or "").removeprefix("www.")

    page_intents: List[PageIntentAnalysis] = []
    local_signals: List[LocalSignalAnalysis] = []
    commercial_journeys: List[CommercialJourneyAnalysis] = []
    comparison_pages: List[ComparisonSupportAnalysis] = []

    for page in pages_raw:
        url, html, title, h1, schema_types, cta_texts = extract_page_html_and_metadata(page)
        if not url:
            continue

        meta_desc = ""
        data, _ = selected_data(page)
        if isinstance(data, dict):
            meta_desc = data.get("description") or ""

        # 1. Classify search intent
        intent_analysis = classify_search_intent(
            url=url,
            title=title,
            h1=h1,
            body_text=html,
            schema_types=schema_types,
            cta_texts=cta_texts,
            meta_description=meta_desc,
        )
        page_intents.append(intent_analysis)

        # 2. Audit local signals
        local_analysis = audit_local_signals(url=url, html=html)
        local_signals.append(local_analysis)

        # 3. Audit commercial journey
        comm_analysis = audit_commercial_journey(url=url, html=html, primary_intent=intent_analysis.primary_intent)
        commercial_journeys.append(comm_analysis)

        # 4. Audit comparison support
        comp_analysis = audit_comparison_support(url=url, html=html, primary_intent=intent_analysis.primary_intent)
        comparison_pages.append(comp_analysis)

    # Cross-page keyword cannibalization
    cannibalizations = detect_cannibalization(page_intents)

    # Intent distribution
    intent_distribution: Dict[str, int] = {}
    for p in page_intents:
        intent_distribution[p.primary_intent] = intent_distribution.get(p.primary_intent, 0) + 1

    # Score calculation
    score = compute_search_commercial_score(
        page_intents=page_intents,
        cannibalizations=cannibalizations,
        local_signals=local_signals,
        commercial_journeys=commercial_journeys,
        comparison_pages=comparison_pages,
    )

    # Recommendations
    recommendations = synthesize_recommendations(
        cannibalizations=cannibalizations,
        local_signals=local_signals,
        commercial_journeys=commercial_journeys,
        comparison_pages=comparison_pages,
        score=score,
    )

    created_at = datetime.now(timezone.utc).isoformat()
    snap_id = summary.get("snapshot_id") or snap_path.name

    result = SearchCommercialAnalysisResult(
        target_url=target_url,
        brand_name=brand_name,
        created_at=created_at,
        pages_analyzed=len(page_intents),
        page_intents=[p.to_dict() for p in page_intents],
        cannibalization_issues=[c.to_dict() for c in cannibalizations],
        local_signals=[l.to_dict() for l in local_signals],
        commercial_journeys=[cj.to_dict() for cj in commercial_journeys],
        comparison_pages=[cp.to_dict() for cp in comparison_pages],
        score=score.to_dict(),
        intent_distribution=intent_distribution,
        recommendations=recommendations,
    )

    target_out = out_dir or snap_path
    export_reports(result, target_out, snapshot_id=snap_id)
    return result


def analyze_target_search(
    target: str,
    out_dir: Optional[Path] = None,
    brand: str = "",
) -> SearchCommercialAnalysisResult:
    """
    Main entrypoint: analyzes either a crawl snapshot directory or a live website URL.
    """
    target_path = Path(target)
    if target_path.exists() and target_path.is_dir():
        return analyze_search_snapshot(target_path, out_dir=out_dir, brand=brand)

    # If it's a URL or domain string, execute a crawl first
    from ..engine import crawl_site
    from ..network import SessionConfig

    url = target if "://" in target else f"https://{target}"
    host_slug = urlsplit(url).hostname or "target"
    crawl_out = out_dir or Path(f"search_{host_slug.removeprefix('www.').replace('.', '_')}")
    crawl_out.mkdir(parents=True, exist_ok=True)

    session_cfg = SessionConfig(profile="quick")
    crawl_site(url, crawl_out, session_cfg)
    return analyze_search_snapshot(crawl_out, out_dir=crawl_out, brand=brand)
