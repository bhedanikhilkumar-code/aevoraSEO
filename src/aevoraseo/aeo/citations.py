"""
AevoraSEO Source & Citation Readiness Analyzer
Analyzes deterministic source attribution signals: author bylines, publication/modification timestamps,
outbound reference links, factual specificity, and canonical identity integrity.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from aevoraseo.aeo.models import CitationSignal

FACTUAL_REGEX = re.compile(
    r"\b(?:"
    r"\d+(?:\.\d+)?%|"  # Percentages
    r"[$€£¥]\s*\d+(?:,\d{3})*(?:\.\d+)?|"  # Currencies
    r"\d+(?:,\d{3})*(?:\.\d+)?\s*(?:kg|g|km|m|cm|mm|ms|s|hours|days|GB|TB|MB|users|customers|queries|tokens|requests)|"  # Quantities
    r"\b(?:19\d\d|20[0-3]\d)\b"  # Historical or current years
    r")\b",
    re.IGNORECASE,
)


def calculate_factual_density(text: str) -> float:
    """
    Calculates the density of factual and statistical figures within text.
    Returns a score between 0.0 and 1.0.
    """
    if not text or not text.strip():
        return 0.0

    words = text.split()
    if len(words) < 20:
        return 0.0

    matches = FACTUAL_REGEX.findall(text)
    match_count = len(matches)

    # 1 factual reference per 40 words is considered high density (1.0)
    density_ratio = match_count / (len(words) / 40.0)
    return round(min(1.0, max(0.0, density_ratio)), 2)


def extract_dates(
    meta: Dict[str, List[str]],
    jsonld_blocks: List[Any],
    html: str = ""
) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts publication date and modification date from meta, schema, and HTML.
    """
    pub_date: Optional[str] = None
    mod_date: Optional[str] = None

    # 1. Check meta tags
    article_pub = meta.get("article:published_time") or meta.get("pubdate") or meta.get("date")
    if article_pub:
        pub_date = article_pub[0]
    article_mod = meta.get("article:modified_time") or meta.get("last-modified")
    if article_mod:
        mod_date = article_mod[0]

    # 2. Check JSON-LD
    def _search_jsonld(node: Any):
        nonlocal pub_date, mod_date
        if isinstance(node, dict):
            if not pub_date and "datePublished" in node and isinstance(node["datePublished"], str):
                pub_date = node["datePublished"]
            if not mod_date and "dateModified" in node and isinstance(node["dateModified"], str):
                mod_date = node["dateModified"]
            for v in node.values():
                _search_jsonld(v)
        elif isinstance(node, list):
            for item in node:
                _search_jsonld(item)

    for b in jsonld_blocks:
        _search_jsonld(b)

    # 3. Check HTML <time> tags if still missing
    if (not pub_date or not mod_date) and html:
        try:
            soup = BeautifulSoup(html, "html.parser")
            times = soup.find_all("time")
            for t in times:
                dt = t.get("datetime") or t.get_text(" ", strip=True)
                if dt:
                    if not pub_date:
                        pub_date = dt
                    elif not mod_date:
                        mod_date = dt
        except Exception:
            pass

    return pub_date, mod_date


def extract_author_and_publisher(
    meta: Dict[str, List[str]],
    jsonld_blocks: List[Any],
    html: str = ""
) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts author name and publisher/organization name.
    """
    author: Optional[str] = None
    publisher: Optional[str] = None

    # Meta
    meta_author = meta.get("author")
    if meta_author:
        author = str(meta_author[0]).strip()

    meta_pub = meta.get("og:site_name") or meta.get("publisher")
    if meta_pub:
        publisher = str(meta_pub[0]).strip()

    # JSON-LD
    def _search_jsonld(node: Any):
        nonlocal author, publisher
        if isinstance(node, dict):
            if not author and "author" in node:
                a_val = node["author"]
                if isinstance(a_val, dict):
                    author = str(a_val.get("name") or a_val.get("@id") or "")
                elif isinstance(a_val, list) and a_val:
                    first = a_val[0]
                    author = str(first.get("name") if isinstance(first, dict) else first)
                elif isinstance(a_val, str):
                    author = a_val

            if not publisher and "publisher" in node:
                p_val = node["publisher"]
                if isinstance(p_val, dict):
                    publisher = str(p_val.get("name") or p_val.get("@id") or "")
                elif isinstance(p_val, str):
                    publisher = p_val

            for v in node.values():
                _search_jsonld(v)
        elif isinstance(node, list):
            for item in node:
                _search_jsonld(item)

    for b in jsonld_blocks:
        _search_jsonld(b)

    # HTML byline fallback
    if not author and html:
        try:
            soup = BeautifulSoup(html, "html.parser")
            byline_node = (
                soup.find(attrs={"rel": "author"})
                or soup.find(class_=re.compile(r"\b(author|byline)\b", re.I))
            )
            if byline_node:
                t = byline_node.get_text(" ", strip=True)
                if 2 <= len(t.split()) <= 6:
                    author = t
        except Exception:
            pass

    return author, publisher


def extract_outbound_citations(
    page_url: str,
    links: List[Dict[str, Any]]
) -> Tuple[int, List[str]]:
    """
    Extracts external outbound reference links and distinct cited domains.
    """
    current_domain = urlparse(page_url).netloc.lower()
    citation_domains: Set[str] = set()
    citation_count = 0

    for link in links:
        href = link.get("href") or link.get("url") or ""
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        parsed = urlparse(href)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            ext_domain = parsed.netloc.lower()
            if ext_domain != current_domain:
                citation_count += 1
                citation_domains.add(ext_domain)

    return citation_count, sorted(citation_domains)[:10]


def analyze_page_citations(
    page_url: str,
    page_data: Dict[str, Any],
    html: str = ""
) -> CitationSignal:
    """
    Extracts all citation readiness signals for a crawled page.
    """
    meta = page_data.get("meta", {})
    jsonld_blocks = page_data.get("jsonld", [])
    text = page_data.get("main_text") or page_data.get("text") or ""
    links = page_data.get("links", [])
    canonicals = page_data.get("canonical", [])

    author, publisher = extract_author_and_publisher(meta, jsonld_blocks, html=html)
    date_pub, date_mod = extract_dates(meta, jsonld_blocks, html=html)
    ref_count, ref_domains = extract_outbound_citations(page_url, links)
    factual_density = calculate_factual_density(text)

    # Canonical evaluation
    has_canonical = len(canonicals) > 0
    canonical_matches = False
    if has_canonical:
        canonical_target = canonicals[0].get("url", "").rstrip("/")
        normalized_url = page_url.rstrip("/")
        canonical_matches = (canonical_target == normalized_url)

    return CitationSignal(
        author=author,
        publisher=publisher,
        date_published=date_pub,
        date_modified=date_mod,
        outbound_references_count=ref_count,
        outbound_citation_domains=ref_domains,
        factual_density_score=factual_density,
        has_canonical=has_canonical,
        canonical_matches_url=canonical_matches,
    )
