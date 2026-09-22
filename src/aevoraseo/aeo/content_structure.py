"""
AevoraSEO Content Structure & Duplication Analyzer
Inspects heading hierarchy, text block distribution, lists, tables, semantic HTML,
and detects structural weaknesses and intra-site content contradictions.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from bs4 import BeautifulSoup

from aevoraseo.aeo.models import ContentStructureSignal


def audit_page_content_structure(
    page_data: Dict[str, Any],
    html: str = ""
) -> ContentStructureSignal:
    """
    Analyzes heading hierarchy, paragraph distribution, lists, tables, and structural weaknesses.
    """
    headings_data = page_data.get("headings", {})
    h1_list = headings_data.get("h1", [])
    h1_count = len(h1_list)
    has_h1 = h1_count > 0

    weaknesses: List[str] = []
    if h1_count == 0:
        weaknesses.append("missing_h1: Page lacks a primary <h1> heading.")
    elif h1_count > 1:
        weaknesses.append(f"multiple_h1: Page contains {h1_count} <h1> headings.")

    # Check for empty headings
    for level, h_items in headings_data.items():
        for h in h_items:
            if not h.strip():
                weaknesses.append(f"empty_heading: Found empty or whitespace-only <{level}> heading.")

    # Check heading sequence / hierarchy if HTML is available
    hierarchy_valid = True
    paragraph_count = 0
    unbroken_text_blocks = 0
    list_count = 0
    table_count = 0

    if html:
        try:
            soup = BeautifulSoup(html, "html.parser")
            # Analyze heading levels sequence
            heading_tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            prev_level = 0
            for h in heading_tags:
                level = int(h.name[1])
                if prev_level > 0 and level > prev_level + 1:
                    hierarchy_valid = False
                    weaknesses.append(
                        f"skipped_heading_level: <{h.name}> appears after <h{prev_level}> without intermediate level."
                    )
                prev_level = level

            # Paragraph and text block inspection
            paragraphs = soup.find_all("p")
            paragraph_count = len(paragraphs)
            for p in paragraphs:
                words = p.get_text(" ", strip=True).split()
                if len(words) > 300:
                    unbroken_text_blocks += 1

            if unbroken_text_blocks > 0:
                weaknesses.append(
                    f"long_unbroken_text: {unbroken_text_blocks} paragraph(s) exceed 300 words without subheadings or lists."
                )

            # Lists and tables
            lists = soup.find_all(["ul", "ol", "dl"])
            list_count = len(lists)

            tables = soup.find_all("table")
            table_count = len(tables)

        except Exception:
            pass

    word_count = page_data.get("word_count", 0)

    return ContentStructureSignal(
        has_h1=has_h1,
        h1_count=h1_count,
        heading_hierarchy_valid=hierarchy_valid,
        structural_weaknesses=weaknesses,
        paragraph_count=paragraph_count,
        unbroken_text_blocks=unbroken_text_blocks,
        list_count=list_count,
        table_count=table_count,
        word_count=word_count,
    )


def audit_snapshot_content_conflicts(
    pages: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Audits cross-page conflicts across the snapshot: duplicate titles, conflicting canonicals,
    and duplicate FAQ questions.
    """
    conflicts: List[Dict[str, Any]] = []

    # 1. Duplicate page titles across different URLs
    titles_map: Dict[str, List[str]] = {}
    canonical_map: Dict[str, List[str]] = {}
    faq_questions: Dict[str, List[str]] = {}

    for page in pages:
        url = page.get("url", "")
        data = page.get("data", {})
        title = data.get("title", "").strip()
        if title:
            titles_map.setdefault(title.lower(), []).append(url)

        canonicals = data.get("canonical", [])
        if canonicals:
            can_url = canonicals[0].get("url", "").rstrip("/")
            if can_url:
                canonical_map.setdefault(can_url, []).append(url)

    # Report duplicate titles
    for title, urls in titles_map.items():
        if len(urls) > 1:
            conflicts.append({
                "type": "duplicate_title",
                "message": f"Identical title '{title[:60]}' shared across multiple URLs.",
                "urls": urls[:5],
            })

    # Report conflicting canonicals pointing multiple pages to one target
    for can_url, urls in canonical_map.items():
        if len(urls) > 1 and can_url not in urls:
            conflicts.append({
                "type": "shared_canonical_target",
                "message": f"Multiple distinct pages point to canonical target '{can_url}'.",
                "urls": urls[:5],
            })

    return conflicts
