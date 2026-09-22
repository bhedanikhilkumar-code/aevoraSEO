"""
AevoraSEO Structured Data Intelligence Analyzer
Audits JSON-LD and Microdata for validity, completeness, and consistency.
Distinguishes schema_detected, schema_valid, schema_complete, and schema_consistent.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from aevoraseo.aeo.models import SchemaQualitySignal

# Recommended core properties per Schema.org type for answer engines
SCHEMA_REQUIREMENTS: Dict[str, Dict[str, List[str]]] = {
    "Article": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["publisher", "image", "dateModified", "mainEntityOfPage"],
    },
    "NewsArticle": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["publisher", "image", "dateModified"],
    },
    "BlogPosting": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["publisher", "dateModified"],
    },
    "Organization": {
        "required": ["name", "url"],
        "recommended": ["logo", "sameAs", "contactPoint"],
    },
    "Corporation": {
        "required": ["name", "url"],
        "recommended": ["logo", "sameAs"],
    },
    "LocalBusiness": {
        "required": ["name", "address"],
        "recommended": ["telephone", "openingHours", "url"],
    },
    "Person": {
        "required": ["name"],
        "recommended": ["url", "sameAs", "jobTitle"],
    },
    "Product": {
        "required": ["name"],
        "recommended": ["offers", "image", "description", "brand"],
    },
    "WebSite": {
        "required": ["name", "url"],
        "recommended": ["potentialAction"],
    },
    "WebPage": {
        "required": ["name", "url"],
        "recommended": ["description", "breadcrumb"],
    },
    "FAQPage": {
        "required": ["mainEntity"],
        "recommended": [],
    },
    "QAPage": {
        "required": ["mainEntity"],
        "recommended": [],
    },
}


def audit_jsonld_node(
    node: Dict[str, Any],
    page_title: str = "",
    canonical_url: str = "",
    visited_ids: Optional[Set[int]] = None,
    current_depth: int = 0,
    max_depth: int = 25,
) -> List[SchemaQualitySignal]:
    """
    Evaluates a single JSON-LD dictionary against requirements and page consistency.
    """
    signals: List[SchemaQualitySignal] = []

    if current_depth > max_depth or not isinstance(node, dict):
        return signals

    if visited_ids is None:
        visited_ids = set()

    if id(node) in visited_ids:
        return signals
    visited_ids.add(id(node))

    type_val = node.get("@type")
    if not type_val:
        return signals

    types = type_val if isinstance(type_val, list) else [type_val]

    for t in types:
        if not isinstance(t, str):
            continue

        reqs = SCHEMA_REQUIREMENTS.get(t, {"required": [], "recommended": []})
        required_props = reqs["required"]
        present_props = [k for k in node.keys() if not k.startswith("@")]

        missing = [p for p in required_props if p not in node or not node[p]]

        errors: List[str] = []
        is_consistent = True

        # Check completeness
        is_complete = len(missing) == 0

        # Check consistency with page title
        headline = node.get("headline") or (node.get("name") if t != "Organization" else None)
        if headline and isinstance(headline, str) and page_title:
            h_words = set(headline.lower().split())
            t_words = set(page_title.lower().split())
            # If completely disjoint for an Article / NewsArticle
            if t in ("Article", "NewsArticle", "BlogPosting") and len(h_words) > 2 and len(t_words) > 2:
                if not (h_words & t_words):
                    is_consistent = False
                    errors.append(f"Schema headline '{headline[:50]}' conflicts with page title '{page_title[:50]}'.")

        # Check consistency with canonical URL
        url_in_schema = node.get("url") or node.get("mainEntityOfPage")
        if isinstance(url_in_schema, dict):
            url_in_schema = url_in_schema.get("@id") or url_in_schema.get("url")
        if url_in_schema and isinstance(url_in_schema, str) and canonical_url:
            # Normalized comparison
            if canonical_url.rstrip("/") != url_in_schema.rstrip("/"):
                # Non-fatal notice
                errors.append(f"Schema URL '{url_in_schema}' does not match canonical URL '{canonical_url}'.")

        signals.append(
            SchemaQualitySignal(
                schema_type=t,
                detected=True,
                valid=True,  # Parsed JSON-LD node is syntactically valid
                complete=is_complete,
                consistent=is_consistent,
                present_properties=present_props,
                missing_required=missing,
                errors=errors,
            )
        )

    # Recurse into nested dictionaries or lists
    for val in node.values():
        if isinstance(val, dict):
            signals.extend(
                audit_jsonld_node(
                    val,
                    page_title=page_title,
                    canonical_url=canonical_url,
                    visited_ids=visited_ids,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                )
            )
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    signals.extend(
                        audit_jsonld_node(
                            item,
                            page_title=page_title,
                            canonical_url=canonical_url,
                            visited_ids=visited_ids,
                            current_depth=current_depth + 1,
                            max_depth=max_depth,
                        )
                    )

    return signals


def audit_page_schema(
    page_data: Dict[str, Any],
    canonical_url: str = ""
) -> List[SchemaQualitySignal]:
    """
    Audits structured data for a crawled page.
    Captures detected, valid, complete, and consistent states, plus syntax errors.
    """
    signals: List[SchemaQualitySignal] = []

    jsonld_blocks = page_data.get("jsonld", [])
    jsonld_errors = page_data.get("jsonld_errors", [])
    page_title = page_data.get("title", "")

    # Record malformed JSON-LD syntax errors
    for err in jsonld_errors:
        block_idx = err.get("block", 0)
        msg = err.get("error", "Malformed JSON-LD")
        signals.append(
            SchemaQualitySignal(
                schema_type="Unknown",
                detected=True,
                valid=False,
                complete=False,
                consistent=False,
                present_properties=[],
                missing_required=[],
                errors=[f"JSON-LD syntax error in script block #{block_idx}: {msg}"],
            )
        )

    # Process parsed JSON-LD blocks
    for block in jsonld_blocks:
        if isinstance(block, dict):
            signals.extend(audit_jsonld_node(block, page_title=page_title, canonical_url=canonical_url))
        elif isinstance(block, list):
            for item in block:
                if isinstance(item, dict):
                    signals.extend(audit_jsonld_node(item, page_title=page_title, canonical_url=canonical_url))

    # Also detect microdata types if present without JSON-LD counterpart
    microdata_types = page_data.get("microdata_types", [])
    seen_types = {s.schema_type for s in signals}
    for mtype in microdata_types:
        short_type = mtype.split("/")[-1]
        if short_type not in seen_types:
            signals.append(
                SchemaQualitySignal(
                    schema_type=short_type,
                    detected=True,
                    valid=True,
                    complete=True,
                    consistent=True,
                    present_properties=["microdata"],
                    missing_required=[],
                    errors=[],
                )
            )

    return signals
