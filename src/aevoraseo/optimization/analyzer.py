"""
Core orchestration and audit analysis algorithms for AevoraSEO Content & Optimization.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from aevoraseo.aeo.questions import is_question_text
from aevoraseo.evidence import selected_data
from aevoraseo.network import normalize_url
from aevoraseo.search.intent import (
    clean_tokens,
    classify_search_intent,
    extract_target_queries,
)

from .briefs import (
    generate_content_brief,
    generate_editorial_outline,
    generate_optimization_roadmap,
)
from .models import (
    ContentBrief,
    ContentGap,
    ContentRefreshCandidate,
    DirectAnswerOpportunity,
    EditorialOutline,
    FAQOpportunity,
    HeadingAudit,
    InternalLinkRecommendation,
    MetaDescriptionAudit,
    OptimizationResult,
    OptimizationRoadmapItem,
    OptimizationScore,
    SchemaRecommendation,
    TitleAudit,
    TopicCluster,
)
from .persistence import save_optimization_snapshot
from .reporter import (
    generate_csv_reports,
    generate_markdown_report,
)
from .scoring import calculate_optimization_score

CTA_VERBS = {
    "get", "learn", "discover", "explore", "read", "find", "shop", "book",
    "call", "start", "contact", "see", "check", "try", "schedule", "register",
    "join", "order", "view", "request", "download",
}

GENERIC_ANCHORS = {
    "click here", "read more", "learn more", "here", "link", "page", "this",
    "more", "website", "details", "info", "continue",
}

DATED_YEAR_REGEX = re.compile(r"\b(201\d|202[0-3])\b")


def audit_titles(pages: List[Dict[str, Any]], brand: str = "") -> List[TitleAudit]:
    """
    Audits page titles for length, brand placement, primary query alignment, and keyword stuffing.
    """
    audits: List[TitleAudit] = []
    brand_lower = brand.lower().strip()

    for page in pages:
        url = page.get("url", "")
        d, _ = selected_data(page)
        title = d.get("title", "").strip()
        length = len(title)

        if not title:
            status = "missing"
            rec = "Add a unique, descriptive title tag (45-65 characters) with primary topic and brand name."
        elif length < 30:
            status = "too_short"
            rec = f"Expand title tag from {length} chars to 45-65 chars incorporating target keyword modifier."
        elif length > 70:
            status = "too_long"
            rec = f"Shorten title tag from {length} chars to <= 65 chars to prevent SERP truncation."
        else:
            status = "optimal"
            rec = "Title tag length is within optimal SERP display range."

        # Brand placement detection
        brand_detected = False
        brand_pos = "none"
        if brand_lower:
            if brand_lower in title.lower():
                brand_detected = True
                # Check position
                if re.search(r"[-|—•]\s*" + re.escape(brand_lower), title.lower()):
                    brand_pos = "end"
                elif title.lower().startswith(brand_lower):
                    brand_pos = "start"
                else:
                    brand_pos = "middle"

        # Query alignment
        h1_text = (d.get("headings", {}).get("h1") or [""])[0]
        slug = urlsplit(url).path.strip("/").split("/")[-1] if urlsplit(url).path.strip("/") else ""
        primary_query, _ = extract_target_queries(title, h1_text, slug, d.get("meta_description", ""))
        query_tokens = clean_tokens(primary_query)
        title_tokens = clean_tokens(title)
        query_overlap = any(t in title_tokens for t in query_tokens) if query_tokens else True

        # Keyword stuffing detection: repeating word sequences or repeated token > 2 times
        keyword_stuffed = False
        counts: Dict[str, int] = {}
        for token in title_tokens:
            counts[token] = counts.get(token, 0) + 1
            if counts[token] >= 3:
                keyword_stuffed = True
                break

        if keyword_stuffed:
            rec = f"Remove repetitive keywords ('{token}') from title to avoid search engine spam flags."
        elif not query_overlap and primary_query != "general":
            rec = f"Align title tag with primary page topic query '{primary_query}'."

        audits.append(
            TitleAudit(
                url=url,
                title=title,
                length=length,
                status=status,
                brand_detected=brand_detected,
                brand_position=brand_pos,
                keyword_stuffed=keyword_stuffed,
                primary_query=primary_query,
                query_overlap=query_overlap,
                recommendation=rec,
            )
        )

    return audits


def audit_meta_descriptions(pages: List[Dict[str, Any]], brand: str = "") -> List[MetaDescriptionAudit]:
    """
    Audits meta descriptions for length, actionable CTA phrasing, and primary query relevance.
    """
    audits: List[MetaDescriptionAudit] = []

    for page in pages:
        url = page.get("url", "")
        d, _ = selected_data(page)
        desc = d.get("meta_description", "").strip()
        length = len(desc)

        if not desc:
            status = "missing"
            rec = "Add a compelling meta description (120-160 characters) with an actionable call-to-action."
        elif length < 70:
            status = "too_short"
            rec = f"Expand meta description from {length} chars to 120-160 chars with value proposition."
        elif length > 165:
            status = "too_long"
            rec = f"Trim meta description from {length} chars to <= 160 chars to avoid truncation in snippets."
        else:
            status = "optimal"
            rec = "Meta description length is well within optimal display limits."

        # Actionable CTA detection
        desc_words = {w.strip(".,!?").lower() for w in desc.split()}
        detected_ctas = sorted(desc_words.intersection(CTA_VERBS))
        has_cta = len(detected_ctas) > 0

        # Query alignment
        title_text = d.get("title", "")
        h1_text = (d.get("headings", {}).get("h1") or [""])[0]
        slug = urlsplit(url).path.strip("/").split("/")[-1] if urlsplit(url).path.strip("/") else ""
        primary_query, _ = extract_target_queries(title_text, h1_text, slug, desc)
        query_tokens = clean_tokens(primary_query)
        desc_tokens = clean_tokens(desc)
        query_overlap = any(t in desc_tokens for t in query_tokens) if query_tokens else True

        if not has_cta and desc:
            rec += " Include an active CTA verb (e.g., 'Discover', 'Explore', 'Get Started', 'Learn')."

        audits.append(
            MetaDescriptionAudit(
                url=url,
                description=desc,
                length=length,
                status=status,
                has_cta=has_cta,
                cta_phrases=detected_ctas,
                primary_query=primary_query,
                query_overlap=query_overlap,
                recommendation=rec.strip(),
            )
        )

    return audits


def audit_headings(pages: List[Dict[str, Any]], html_by_url: Dict[str, str]) -> List[HeadingAudit]:
    """
    Audits heading architecture: single H1 enforcement, logical sequence, and question headings.
    """
    audits: List[HeadingAudit] = []

    for page in pages:
        url = page.get("url", "")
        d, _ = selected_data(page)
        headings = d.get("headings", {})
        h1_list = [h.strip() for h in headings.get("h1", [])]
        h1_count = len(h1_list)
        h2_list = [h.strip() for h in headings.get("h2", [])]
        h3_list = [h.strip() for h in headings.get("h3", [])]

        skipped_issues: List[str] = []
        empty_headings: List[str] = []
        question_headings: List[str] = []

        # Check empty headings
        for lvl, items in headings.items():
            for it in items:
                if not it.strip():
                    empty_headings.append(f"Empty <{lvl}> tag detected")

        # Check DOM sequence if HTML available
        html = html_by_url.get(url, "")
        if html:
            try:
                soup = BeautifulSoup(html, "html.parser")
                all_h = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
                prev_lvl = 0
                for h in all_h:
                    cur_lvl = int(h.name[1])
                    h_text = h.get_text(" ", strip=True)
                    if not h_text:
                        continue
                    if prev_lvl > 0 and cur_lvl > prev_lvl + 1:
                        skipped_issues.append(f"Skipped level: <h{prev_lvl}> followed directly by <h{cur_lvl}> ('{h_text[:40]}')")
                    prev_lvl = cur_lvl

                    is_q, _ = is_question_text(h_text)
                    if is_q or h_text.endswith("?"):
                        question_headings.append(h_text)
            except Exception:
                pass

        if not question_headings:
            # Fallback scan over extracted headings
            for h in h1_list + h2_list + h3_list:
                is_q, _ = is_question_text(h)
                if is_q or h.endswith("?"):
                    question_headings.append(h)

        recs = []
        if h1_count == 0:
            recs.append("Add a single, definitive <h1> heading stating the primary topic.")
        elif h1_count > 1:
            recs.append(f"Consolidate {h1_count} <h1> headings into a single primary document title.")
        if skipped_issues:
            recs.append("Correct heading hierarchy so subheadings descend consecutively without skipping levels.")
        if empty_headings:
            recs.append("Remove empty heading tags from templates.")
        if not recs:
            recs.append("Heading hierarchy is logically structured with a single H1.")

        audits.append(
            HeadingAudit(
                url=url,
                h1_count=h1_count,
                h1_texts=h1_list,
                h2_count=len(h2_list),
                h3_count=len(h3_list),
                has_skipped_levels=len(skipped_issues) > 0,
                skipped_hierarchy_issues=skipped_issues,
                question_headings=question_headings,
                empty_headings=empty_headings,
                recommendation=" ".join(recs),
            )
        )

    return audits


def detect_direct_answer_opportunities(
    pages: List[Dict[str, Any]],
    html_by_url: Dict[str, str],
) -> List[DirectAnswerOpportunity]:
    """
    Detects direct answer and definition opportunities (40-60 word answer boxes, list/table targets).
    """
    opportunities: List[DirectAnswerOpportunity] = []
    seen: Set[str] = set()

    for page in pages:
        url = page.get("url", "")
        d, _ = selected_data(page)
        html = html_by_url.get(url, "")
        if not html:
            continue

        try:
            soup = BeautifulSoup(html, "html.parser")
            for h_tag in soup.find_all(["h2", "h3"]):
                h_text = h_tag.get_text(" ", strip=True)
                is_q, itype = is_question_text(h_text)
                if not (is_q or h_text.endswith("?") or "what is" in h_text.lower() or "how to" in h_text.lower()):
                    continue

                key = f"{url}:{h_text.lower()}"
                if key in seen:
                    continue
                seen.add(key)

                # Inspect immediate following sibling
                is_answered = False
                snippet = None
                curr = h_tag.next_sibling
                hops = 0
                while curr and hops < 4:
                    if getattr(curr, "name", None) in ["h1", "h2", "h3"]:
                        break
                    if getattr(curr, "name", None) == "p":
                        p_text = curr.get_text(" ", strip=True)
                        p_words = p_text.split()
                        if 10 <= len(p_words) <= 75:
                            is_answered = True
                            snippet = p_text[:250]
                            break
                        elif len(p_words) > 75:
                            # Too long for concise answer box
                            snippet = p_text[:200]
                            break
                    elif getattr(curr, "name", None) in ["ul", "ol"]:
                        is_answered = True
                        items = [li.get_text(" ", strip=True) for li in curr.find_all("li")[:3]]
                        snippet = "; ".join(items)
                        break
                    curr = curr.next_sibling
                    hops += 1

                opp_type = "definition" if "what" in h_text.lower() or "is" in h_text.lower() else "procedural_list"
                target_format = "40-60 word answer box" if opp_type == "definition" else "ordered list"
                blueprint = (
                    f"Place a 40-60 word definitive answer paragraph immediately under '<{h_tag.name}> {h_text}' "
                    f"beginning with direct subject-definition syntax for search snippets and AI citation."
                )

                opportunities.append(
                    DirectAnswerOpportunity(
                        url=url,
                        question_or_topic=h_text,
                        opportunity_type=opp_type,
                        target_format=target_format,
                        current_answer_snippet=snippet,
                        is_answered=is_answered,
                        draft_answer_blueprint=blueprint,
                        confidence=0.88 if is_answered else 0.72,
                    )
                )
        except Exception:
            pass

    return opportunities


def detect_faq_and_objection_opportunities(
    pages: List[Dict[str, Any]],
    page_intents: List[Any],
) -> List[FAQOpportunity]:
    """
    Identifies buyer objection gaps (pricing, guarantee, implementation, support) across commercial pages.
    """
    opportunities: List[FAQOpportunity] = []
    intent_map = {p.url: p.primary_intent for p in page_intents}

    for page in pages:
        url = page.get("url", "")
        intent = intent_map.get(url, "informational")
        if intent not in ("transactional", "commercial_investigation"):
            continue

        d, _ = selected_data(page)
        body = d.get("main_text", "").lower()
        title = d.get("title", "")
        slug = urlsplit(url).path.strip("/").split("/")[-1] or "service"

        # Check for pricing objection handling
        if not any(k in body for k in ("pricing", "cost", "rates", "fee", "investment", "quote")):
            opportunities.append(
                FAQOpportunity(
                    url=url,
                    topic=f"{slug.replace('-', ' ').title()} Pricing & Costs",
                    friction_type="pricing",
                    suggested_question=f"How much does {slug.replace('-', ' ')} cost?",
                    suggested_answer_points=[
                        "Transparent baseline cost or engagement pricing model.",
                        "Key variables that determine total investment.",
                        "How clients request a tailored quote or estimate.",
                    ],
                    schema_eligible=True,
                )
            )

        # Check for guarantee or refund handling
        if not any(k in body for k in ("guarantee", "warranty", "satisfaction", "refund", "sla")):
            opportunities.append(
                FAQOpportunity(
                    url=url,
                    topic=f"{slug.replace('-', ' ').title()} Guarantee & Terms",
                    friction_type="guarantee",
                    suggested_question=f"What guarantees or service level agreements are provided?",
                    suggested_answer_points=[
                        "Clear commitment to quality, uptime, or outcome criteria.",
                        "Revisions or remediation process if deliverables need adjustment.",
                        "Customer support and escalation pathways.",
                    ],
                    schema_eligible=True,
                )
            )

    return opportunities


def audit_internal_links_and_orphans(
    pages: List[Dict[str, Any]],
    target_url: str,
) -> Tuple[List[InternalLinkRecommendation], List[str]]:
    """
    Builds site-wide link graph, detects orphan pages, and generates internal link recommendations.
    """
    recs: List[InternalLinkRecommendation] = []
    parsed_target = urlsplit(target_url if "://" in target_url else f"https://{target_url}")
    target_netloc = parsed_target.netloc.lower()

    in_degree: Dict[str, int] = {p.get("url", ""): 0 for p in pages}
    out_degree: Dict[str, int] = {p.get("url", ""): 0 for p in pages}
    link_map: Dict[str, List[Dict[str, Any]]] = {}

    for page in pages:
        src_url = page.get("url", "")
        d, _ = selected_data(page)
        links = d.get("links", [])
        link_map[src_url] = links
        out_degree[src_url] = len(links)

        for l in links:
            dest = l.get("url", "")
            if dest in in_degree:
                in_degree[dest] += 1

            # Check for generic anchor text
            anchor = l.get("anchor", "").strip().lower()
            if anchor in GENERIC_ANCHORS:
                recs.append(
                    InternalLinkRecommendation(
                        source_url=src_url,
                        target_url=dest,
                        recommended_anchor=f"Descriptive phrase matching destination topic instead of '{anchor}'",
                        rationale="Replace generic non-descriptive anchor text with topic-specific keyword phrase.",
                        link_type="generic_anchor_fix",
                    )
                )

    # Detect orphan pages: internal pages with in_degree == 0 (excluding the homepage/root)
    orphan_pages: List[str] = []
    root_paths = {"", "/", "/index.html", "/index.php"}

    for url, count in in_degree.items():
        path = urlsplit(url).path
        if count == 0 and path not in root_paths:
            orphan_pages.append(url)
            # Recommend linking from homepage or relevant hub
            recs.append(
                InternalLinkRecommendation(
                    source_url=pages[0].get("url", target_url) if pages else target_url,
                    target_url=url,
                    recommended_anchor=f"Anchor for {urlsplit(url).path.strip('/').replace('-', ' ').title()}",
                    rationale=f"Orphan page detected with 0 incoming internal links. Connect from authoritative parent.",
                    link_type="orphan_recovery",
                )
            )

    return recs, orphan_pages


def analyze_topic_clusters(
    pages: List[Dict[str, Any]],
    page_intents: List[Any],
) -> List[TopicCluster]:
    """
    Identifies pillar content hubs and maps supporting spoke pages.
    """
    clusters: List[TopicCluster] = []
    intent_map = {p.url: p for p in page_intents}

    # Group pages by first URL directory path or primary query category
    groups: Dict[str, List[str]] = {}
    for page in pages:
        url = page.get("url", "")
        parts = [p for p in urlsplit(url).path.strip("/").split("/") if p]
        if not parts:
            continue
        cluster_key = parts[0].replace("-", " ").title()
        groups.setdefault(cluster_key, []).append(url)

    for cluster_name, urls in groups.items():
        if len(urls) < 2:
            continue

        # Find pillar: highest word count and broadest intent
        best_pillar = None
        max_words = -1
        for u in urls:
            matching_page = next((p for p in pages if p.get("url") == u), None)
            if not matching_page:
                continue
            d, _ = selected_data(matching_page)
            wc = d.get("word_count", 0)
            if wc > max_words:
                max_words = wc
                best_pillar = u

        spokes = [u for u in urls if u != best_pillar]
        health = min(100.0, round((len(spokes) / max(1, len(urls))) * 90.0 + (10.0 if best_pillar else 0.0), 1))

        clusters.append(
            TopicCluster(
                cluster_id=f"cluster_{re.sub(r'[^a-zA-Z0-9]', '_', cluster_name.lower())}",
                topic_name=cluster_name,
                pillar_url=best_pillar,
                spoke_urls=spokes,
                cluster_health_score=health,
                internal_link_coverage=round(health / 100.0, 2),
            )
        )

    return clusters


def recommend_schemas(
    pages: List[Dict[str, Any]],
    page_intents: List[Any],
) -> List[SchemaRecommendation]:
    """
    Determines intent-matched recommended schemas and detects missing structured data.
    """
    recommendations: List[SchemaRecommendation] = []
    intent_map = {p.url: p for p in page_intents}

    for page in pages:
        url = page.get("url", "")
        d, _ = selected_data(page)
        current_schemas = d.get("schema_types", [])
        current_set = {s.lower() for s in current_schemas}
        p_intent = intent_map.get(url)
        intent = p_intent.primary_intent if p_intent else "informational"

        recommended: List[str] = ["WebPage", "BreadcrumbList"]
        missing: List[str] = []

        if intent == "informational":
            recommended.append("Article")
            if "article" not in current_set and "blogposting" not in current_set:
                missing.append("Article")
        elif intent == "transactional":
            recommended.extend(["Service", "Offer"])
            if "service" not in current_set and "product" not in current_set:
                missing.append("Service")
        elif intent == "local":
            recommended.append("LocalBusiness")
            if "localbusiness" not in current_set:
                missing.append("LocalBusiness")

        # If page has FAQs or questions
        headings = d.get("headings", {})
        has_questions = any(
            is_question_text(h)[0] or h.endswith("?")
            for lvl in ("h1", "h2", "h3")
            for h in headings.get(lvl, [])
        )
        if has_questions:
            recommended.append("FAQPage")
            if "faqpage" not in current_set:
                missing.append("FAQPage")

        guide = (
            f"Add {', '.join(missing)} JSON-LD structured data to improve search rich results and entity disambiguation."
            if missing
            else "Current structured data properly reflects page intent."
        )

        recommendations.append(
            SchemaRecommendation(
                url=url,
                page_intent=intent,
                current_schemas=current_schemas,
                recommended_schemas=recommended,
                missing_schemas=missing,
                implementation_guide=guide,
            )
        )

    return recommendations


def detect_content_gaps_and_refresh(
    pages: List[Dict[str, Any]],
    page_intents: List[Any],
    heading_audits: List[HeadingAudit],
) -> Tuple[List[ContentGap], List[ContentRefreshCandidate]]:
    """
    Identifies thin content, outdated year mentions, low heading depth, and strategic gaps.
    """
    gaps: List[ContentGap] = []
    refresh: List[ContentRefreshCandidate] = []
    heading_map = {h.url: h for h in heading_audits}
    intent_map = {p.url: p for p in page_intents}

    for page in pages:
        url = page.get("url", "")
        d, _ = selected_data(page)
        title = d.get("title", "")
        wc = d.get("word_count", 0)
        h_audit = heading_map.get(url)
        p_intent = intent_map.get(url)
        intent = p_intent.primary_intent if p_intent else "informational"

        reasons = []
        actions = []

        # Check thin content
        if wc < 250:
            reasons.append(f"Extremely thin content ({wc} words).")
            actions.append("Expand body text with detailed service/topic explanations and practical steps.")
        elif wc < 500 and intent in ("informational", "commercial_investigation"):
            reasons.append(f"Suboptimal depth for {intent} intent ({wc} words).")
            actions.append("Add definition boxes, comparative tables, and comprehensive FAQ sections.")

        # Check outdated dates in title or main text
        dated_in_title = DATED_YEAR_REGEX.findall(title)
        dated_in_text = DATED_YEAR_REGEX.findall(d.get("main_text", "")[:500])
        if dated_in_title or dated_in_text:
            years = sorted(set(dated_in_title + dated_in_text))
            reasons.append(f"Contains dated historical year references: {', '.join(years)}.")
            actions.append(f"Update statistics, case references, and title date to the current operating year.")

        # Check low heading depth
        if h_audit and (h_audit.h2_count == 0):
            reasons.append("Page lacks subheadings (zero <h2> tags).")
            actions.append("Break content into structured sections using topic-focused <h2> subheadings.")

        if reasons:
            priority = "HIGH" if wc < 250 or dated_in_title else "MEDIUM"
            refresh.append(
                ContentRefreshCandidate(
                    url=url,
                    title=title,
                    current_word_count=wc,
                    refresh_priority=priority,
                    reasons=reasons,
                    recommended_actions=actions,
                )
            )

    # Site-level gaps
    has_comparison = any("vs" in p.get("url", "").lower() or "compare" in p.get("url", "").lower() for p in pages)
    if not has_comparison and len(pages) >= 3:
        gaps.append(
            ContentGap(
                gap_id="gap_comparison_pages",
                gap_type="missing_comparison",
                topic="Head-to-Head Comparison & Alternative Evaluation",
                intent="commercial_investigation",
                evidence="No comparison ('vs' or 'alternatives') pages detected in crawl snapshot.",
                action_plan="Publish dedicated comparison guides pitting your primary solution against standard market alternatives.",
            )
        )

    has_faq_page = any("faq" in p.get("url", "").lower() for p in pages)
    if not has_faq_page and len(pages) >= 3:
        gaps.append(
            ContentGap(
                gap_id="gap_central_faq",
                gap_type="missing_faq",
                topic="Centralized Knowledge & FAQ Hub",
                intent="informational",
                evidence="No centralized FAQ or Help section found in crawl inventory.",
                action_plan="Create a dedicated FAQ resource hub with JSON-LD FAQPage schema resolving buyer questions.",
            )
        )

    return gaps, refresh


def analyze_target_optimization(
    target: str,
    out_dir: Optional[Path] = None,
    brand: str = "",
) -> OptimizationResult:
    """
    Top-level orchestrator for AevoraSEO Content & Optimization Intelligence.
    Accepts a crawl snapshot directory or website URL.
    """
    target_path = Path(target)
    pages: List[Dict[str, Any]] = []
    html_by_url: Dict[str, str] = {}
    target_url = target

    if target_path.exists() and target_path.is_dir():
        # Load from crawl snapshot directory
        for p_file in sorted(target_path.glob("page_*.json")):
            try:
                p_data = json.loads(p_file.read_text(encoding="utf-8"))
                pages.append(p_data)
                url = p_data.get("url", "")
                if not target_url or target_url == target:
                    target_url = url

                # Check for corresponding HTML file
                html_file = p_file.with_suffix(".html")
                if html_file.exists():
                    html_by_url[url] = html_file.read_text(encoding="utf-8", errors="ignore")
                elif "html" in p_data:
                    html_by_url[url] = p_data["html"]
            except Exception:
                continue

    if not pages:
        # Construct single page structure from target URL
        from aevoraseo.extract import extract
        from aevoraseo.network import fetch

        target_url = target if "://" in target else f"https://{target}"
        resp = fetch(target_url)
        extracted = extract(resp.get("body", b""), target_url, headers=resp.get("headers", {}))
        page_entry = {
            "url": target_url,
            "status": resp.get("status", 200),
            "data": extracted,
            "html": resp.get("body", b"").decode("utf-8", errors="ignore"),
        }
        pages.append(page_entry)
        html_by_url[target_url] = page_entry["html"]

    # Deduce brand name if not provided
    if not brand and pages:
        first_title = selected_data(pages[0])[0].get("title", "")
        if "|" in first_title:
            brand = first_title.split("|")[-1].strip()
        elif "-" in first_title:
            brand = first_title.split("-")[-1].strip()
        else:
            brand = urlsplit(target_url).hostname or "Brand"
            brand = brand.removeprefix("www.").split(".")[0].capitalize()

    # Step 1: Run Search Intent Discovery on pages
    page_intents = []
    for p in pages:
        d, _ = selected_data(p)
        pi = classify_search_intent(
            url=p.get("url", ""),
            title=d.get("title", ""),
            h1=(d.get("headings", {}).get("h1") or [""])[0],
            body_text=d.get("main_text", ""),
            schema_types=d.get("schema_types", []),
            cta_texts=[l.get("anchor", "") for l in d.get("links", [])],
            meta_description=d.get("meta_description", ""),
        )
        page_intents.append(pi)

    # Step 2: Audit Titles, Meta Descriptions, Headings
    title_audits = audit_titles(pages, brand=brand)
    meta_audits = audit_meta_descriptions(pages, brand=brand)
    heading_audits = audit_headings(pages, html_by_url)

    # Step 3: Direct Answers, FAQ Objections
    answer_opportunities = detect_direct_answer_opportunities(pages, html_by_url)
    faq_opportunities = detect_faq_and_objection_opportunities(pages, page_intents)

    # Step 4: Internal Links, Orphans, Clusters
    link_recs, orphan_pages = audit_internal_links_and_orphans(pages, target_url)
    topic_clusters = analyze_topic_clusters(pages, page_intents)

    # Step 5: Schema Recommendations
    schema_recs = recommend_schemas(pages, page_intents)

    # Step 6: Content Gaps & Refresh Priorities
    content_gaps, refresh_candidates = detect_content_gaps_and_refresh(pages, page_intents, heading_audits)

    # Step 7: Content Briefs & Outlines for top pages
    content_briefs: List[ContentBrief] = []
    editorial_outlines: List[EditorialOutline] = []
    for idx, page in enumerate(pages[:3]):
        url = page.get("url", "")
        d, _ = selected_data(page)
        pi = page_intents[idx] if idx < len(page_intents) else None
        intent = pi.primary_intent if pi else "informational"
        target_q = pi.primary_target_query if pi else "topic"
        sec_q = pi.secondary_queries if pi else []

        matching_schema = next((s.recommended_schemas[0] for s in schema_recs if s.url == url and s.recommended_schemas), "Article")

        brief = generate_content_brief(
            url=url,
            title=d.get("title", ""),
            h1=(d.get("headings", {}).get("h1") or [""])[0],
            primary_query=target_q,
            secondary_queries=sec_q,
            intent=intent,
            current_word_count=d.get("word_count", 0),
            recommended_schema=matching_schema,
        )
        content_briefs.append(brief)
        editorial_outlines.append(generate_editorial_outline(brief))

    # Step 8: Calculate Deterministic Score
    score = calculate_optimization_score(
        title_audits=[t.to_dict() for t in title_audits],
        meta_audits=[m.to_dict() for m in meta_audits],
        heading_audits=[h.to_dict() for h in heading_audits],
        answer_opportunities=[a.to_dict() for a in answer_opportunities],
        faq_opportunities=[f.to_dict() for f in faq_opportunities],
        internal_links=[l.to_dict() for l in link_recs],
        orphan_pages=orphan_pages,
        schema_recommendations=[s.to_dict() for s in schema_recs],
        page_count=len(pages),
    )

    # Step 9: Synthesize Prioritized Roadmap
    roadmap = generate_optimization_roadmap(
        title_audits=[t.to_dict() for t in title_audits],
        heading_audits=[h.to_dict() for h in heading_audits],
        answer_opportunities=[a.to_dict() for a in answer_opportunities],
        faq_opportunities=[f.to_dict() for f in faq_opportunities],
        orphan_pages=orphan_pages,
        schema_recommendations=[s.to_dict() for s in schema_recs],
        refresh_candidates=[r.to_dict() for r in refresh_candidates],
    )

    # Synthesize Top Strategic Recommendations
    strategic_recs: List[Dict[str, Any]] = []
    for r_item in roadmap:
        strategic_recs.append({
            "timeframe": r_item.timeframe,
            "action": r_item.action,
            "impact": r_item.expected_impact,
            "target_urls": r_item.target_urls,
        })

    created_at = datetime.now(timezone.utc).isoformat()
    result = OptimizationResult(
        target_url=target_url,
        brand_name=brand,
        created_at=created_at,
        pages_analyzed=len(pages),
        score=score.to_dict(),
        title_audits=[t.to_dict() for t in title_audits],
        meta_audits=[m.to_dict() for m in meta_audits],
        heading_audits=[h.to_dict() for h in heading_audits],
        direct_answer_opportunities=[a.to_dict() for a in answer_opportunities],
        faq_opportunities=[f.to_dict() for f in faq_opportunities],
        internal_link_recommendations=[l.to_dict() for l in link_recs],
        orphan_pages=orphan_pages,
        topic_clusters=[c.to_dict() for c in topic_clusters],
        schema_recommendations=[s.to_dict() for s in schema_recs],
        content_briefs=[b.to_dict() for b in content_briefs],
        editorial_outlines=[o.to_dict() for o in editorial_outlines],
        content_gaps=[g.to_dict() for g in content_gaps],
        refresh_candidates=[r.to_dict() for r in refresh_candidates],
        roadmap_items=[item.to_dict() for item in roadmap],
        recommendations=strategic_recs,
    )

    # Persist and write outputs if out_dir supplied
    if out_dir:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        db_path = out_dir / "content_optimization.sqlite3"
        snapshot_id = f"opt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        save_optimization_snapshot(db_path, result, snapshot_id)

        # Write reports
        (out_dir / "content-optimization.json").write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / "content-optimization.md").write_text(
            generate_markdown_report(result), encoding="utf-8"
        )
        generate_csv_reports(result, out_dir)

    return result
