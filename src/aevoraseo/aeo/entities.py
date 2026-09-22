"""
AevoraSEO AEO / GEO Entity Clarity & Relationship Analyzer
Extracts, validates, and cross-references core Schema.org entities, author/publisher transparency,
sameAs authority linkages, and detects identity inconsistencies.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from aevoraseo.aeo.models import EntitySignal

RECOGNIZED_ENTITY_TYPES = (
    "Organization",
    "Corporation",
    "LocalBusiness",
    "Person",
    "Product",
    "Article",
    "NewsArticle",
    "BlogPosting",
    "WebSite",
    "WebPage",
    "Service",
    "SoftwareApplication",
    "FAQPage",
)


def _extract_name_and_sameas(node: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Extracts name string and list of sameAs URLs from a schema dictionary."""
    raw_name = node.get("name") or node.get("headline") or ""
    if isinstance(raw_name, dict):
        raw_name = raw_name.get("name", "")
    name = str(raw_name).strip()

    same_as_raw = node.get("sameAs", [])
    if isinstance(same_as_raw, str):
        same_as = [same_as_raw.strip()]
    elif isinstance(same_as_raw, list):
        same_as = [str(x).strip() for x in same_as_raw if isinstance(x, str) and x.strip()]
    else:
        same_as = []

    return name, same_as


def extract_entities_from_jsonld(
    jsonld_blocks: List[Any],
    page_title: str = "",
    canonical_url: str = ""
) -> List[EntitySignal]:
    """
    Traverses JSON-LD blocks to detect known entity types and their relationships.
    """
    signals: List[EntitySignal] = []

    def _inspect_node(node: Any):
        if not isinstance(node, dict):
            return

        type_val = node.get("@type")
        if not type_val:
            return

        types = type_val if isinstance(type_val, list) else [type_val]
        for t in types:
            if t in RECOGNIZED_ENTITY_TYPES:
                name, same_as = _extract_name_and_sameas(node)
                relationships: Dict[str, Any] = {}
                issues: List[str] = []

                # Extract standard relational fields
                for rel in ["author", "publisher", "brand", "provider", "creator", "about", "mentions"]:
                    if rel in node:
                        rel_val = node[rel]
                        if isinstance(rel_val, dict):
                            rel_name = rel_val.get("name") or rel_val.get("@id") or ""
                            relationships[rel] = str(rel_name)
                        elif isinstance(rel_val, list):
                            relationships[rel] = [
                                (x.get("name") or x.get("@id")) if isinstance(x, dict) else str(x)
                                for x in rel_val
                            ]
                        elif isinstance(rel_val, str):
                            relationships[rel] = rel_val

                # Validation checks
                if not name:
                    issues.append(f"Entity of type {t} lacks a descriptive 'name' or 'headline'.")

                # Validate sameAs URLs format if present
                for sa in same_as:
                    parsed = urlparse(sa)
                    if not (parsed.scheme in ("http", "https") and parsed.netloc):
                        issues.append(f"Invalid sameAs URL '{sa}'.")

                # Title alignment check for Articles / Products
                if t in ("Article", "NewsArticle", "BlogPosting", "Product") and name and page_title:
                    # Check if entity name shares keywords with page title
                    title_words = set(page_title.lower().split())
                    name_words = set(name.lower().split())
                    if not (title_words & name_words):
                        issues.append(f"Entity name '{name}' does not align with page title '{page_title}'.")

                signals.append(
                    EntitySignal(
                        entity_type=t,
                        name=name,
                        source="jsonld",
                        same_as=same_as,
                        relationships=relationships,
                        is_consistent=len(issues) == 0,
                        issues=issues,
                    )
                )

        for val in node.values():
            if isinstance(val, dict):
                _inspect_node(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        _inspect_node(item)

    for block in jsonld_blocks:
        _inspect_node(block)

    return signals


def analyze_page_entities(
    page_data: Dict[str, Any],
    canonical_url: str = ""
) -> List[EntitySignal]:
    """
    Extracts all detectable entities for a single page.
    """
    title = page_data.get("title", "")
    jsonld_blocks = page_data.get("jsonld", [])
    signals = extract_entities_from_jsonld(jsonld_blocks, page_title=title, canonical_url=canonical_url)

    # If no Organization found in JSON-LD but OpenGraph / meta provides publisher / site_name
    meta = page_data.get("meta", {})
    site_name_list = meta.get("og:site_name") or []
    if site_name_list and not any(s.entity_type == "Organization" for s in signals):
        site_name = str(site_name_list[0]).strip()
        if site_name:
            signals.append(
                EntitySignal(
                    entity_type="Organization",
                    name=site_name,
                    source="meta:og:site_name",
                    same_as=[],
                    relationships={},
                    is_consistent=True,
                    issues=[],
                )
            )

    # Check author meta if no Person/author found
    author_list = meta.get("author") or []
    if author_list and not any(s.entity_type == "Person" for s in signals):
        author_name = str(author_list[0]).strip()
        if author_name:
            signals.append(
                EntitySignal(
                    entity_type="Person",
                    name=author_name,
                    source="meta:author",
                    same_as=[],
                    relationships={},
                    is_consistent=True,
                    issues=[],
                )
            )

    return signals


def detect_cross_page_conflicts(
    page_results: List[Tuple[str, List[EntitySignal]]]
) -> List[Dict[str, Any]]:
    """
    Audits entity consistency across the entire snapshot.
    Detects contradictory organization names, conflicting author signatures, etc.
    """
    conflicts: List[Dict[str, Any]] = []

    # Map organization names by URL
    org_names: Dict[str, Set[str]] = {}
    for url, entities in page_results:
        for ent in entities:
            if ent.entity_type in ("Organization", "Corporation", "LocalBusiness"):
                if ent.name:
                    org_names.setdefault(ent.name.strip().lower(), set()).add(url)

    # If there are multiple distinct primary organization names across pages of the same site
    if len(org_names) > 1:
        # Check if they look like conflicting brand names
        names = list(org_names.keys())
        conflicts.append({
            "type": "conflicting_organization_names",
            "message": f"Multiple inconsistent Organization names detected across site: {names}",
            "details": {k: list(v)[:5] for k, v in org_names.items()},
        })

    return conflicts
