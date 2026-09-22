"""
AevoraSEO Cross-Page Entity Consistency & Conflict Auditor
Detects contradictory organization names, NAP mismatches, broken sameAs, and missing entity pages.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from .models import EntityConflict, EntityNode, SameAsLink


RECOMMENDED_ENTITY_PATHS = {
    "about": ["/about", "/about-us", "/company", "/our-story"],
    "contact": ["/contact", "/contact-us", "/get-in-touch"],
    "team": ["/team", "/leadership", "/our-team", "/founder", "/people"],
    "services_or_products": ["/services", "/products", "/solutions", "/courses"],
    "reviews_or_proof": ["/reviews", "/testimonials", "/case-studies", "/trust", "/clients"],
    "faq": ["/faq", "/frequently-asked-questions", "/help"],
}


def audit_entity_conflicts(
    nodes: List[EntityNode],
    same_as_links: List[SameAsLink],
    crawled_urls: List[str]
) -> Tuple[List[EntityConflict], List[str]]:
    """
    Performs comprehensive cross-page consistency check.
    Returns: (list_of_conflicts, list_of_missing_entity_pages)
    """
    conflicts: List[EntityConflict] = []

    # 1. Organization Name Inconsistency
    org_nodes = [n for n in nodes if n.entity_type in ("Organization", "Corporation", "LocalBusiness")]
    if len(org_nodes) > 1:
        # Check if they are distinct entities or conflicting claims
        names_to_nodes: Dict[str, EntityNode] = {n.canonical_name.lower(): n for n in org_nodes}
        if len(names_to_nodes) > 1:
            # Check if any is declared as legalName or alternateName of another
            primary_name = org_nodes[0].canonical_name
            other_names = [n.canonical_name for n in org_nodes[1:]]
            
            # Filter out names already recorded in alternate_names
            conflicting_names = []
            for n in org_nodes[1:]:
                if n.canonical_name.lower() not in [a.lower() for a in org_nodes[0].alternate_names]:
                    if org_nodes[0].attributes.get("legalName", "").lower() != n.canonical_name.lower():
                        conflicting_names.append(n.canonical_name)

            if conflicting_names:
                conflicts.append(
                    EntityConflict(
                        conflict_id="conflict:org_name_mismatch",
                        conflict_type="NAME_INCONSISTENCY",
                        severity="HIGH",
                        entity_id=org_nodes[0].entity_id,
                        entity_name=primary_name,
                        description=f"Multiple conflicting Organization names detected across pages: {conflicting_names}",
                        conflicting_evidence={
                            primary_name: org_nodes[0].source_pages[:5],
                            **{n.canonical_name: n.source_pages[:5] for n in org_nodes[1:]}
                        }
                    )
                )

    # 2. NAP (Name, Address, Phone) Inconsistencies across organization entities
    phone_numbers: Dict[str, List[str]] = {}
    addresses: Dict[str, List[str]] = {}
    for org in org_nodes:
        tel = org.attributes.get("telephone")
        if tel:
            phone_numbers.setdefault(tel, []).extend(org.source_pages)
        addr = org.attributes.get("address")
        if isinstance(addr, dict):
            addr_str = f"{addr.get('streetAddress', '')} {addr.get('addressLocality', '')} {addr.get('postalCode', '')}".strip()
            if addr_str:
                addresses.setdefault(addr_str, []).extend(org.source_pages)

    if len(phone_numbers) > 1:
        conflicts.append(
            EntityConflict(
                conflict_id="conflict:phone_mismatch",
                conflict_type="NAP_MISMATCH",
                severity="MEDIUM",
                entity_id=org_nodes[0].entity_id if org_nodes else "org:unknown",
                entity_name=org_nodes[0].canonical_name if org_nodes else "Organization",
                description=f"Multiple disparate phone numbers declared in schema: {list(phone_numbers.keys())}",
                conflicting_evidence={p: urls[:3] for p, urls in phone_numbers.items()}
            )
        )

    if len(addresses) > 1:
        conflicts.append(
            EntityConflict(
                conflict_id="conflict:address_mismatch",
                conflict_type="NAP_MISMATCH",
                severity="MEDIUM",
                entity_id=org_nodes[0].entity_id if org_nodes else "org:unknown",
                entity_name=org_nodes[0].canonical_name if org_nodes else "Organization",
                description=f"Multiple disparate physical addresses declared in schema: {list(addresses.keys())}",
                conflicting_evidence={a: urls[:3] for a, urls in addresses.items()}
            )
        )

    # 3. Broken or Invalid SameAs Links
    for sa in same_as_links:
        if not sa.is_valid_url:
            conflicts.append(
                EntityConflict(
                    conflict_id=f"conflict:broken_sameas_{hash(sa.url) % 100000}",
                    conflict_type="BROKEN_SAMEAS",
                    severity="LOW",
                    entity_id=f"sa:{sa.entity_name}",
                    entity_name=sa.entity_name,
                    description=f"Malformed or invalid sameAs URL '{sa.url}' on {sa.found_on_url}",
                    conflicting_evidence={sa.url: [sa.found_on_url]}
                )
            )

    # 4. Missing Recommended Core Entity Pages
    normalized_paths = set()
    for u in crawled_urls:
        try:
            parsed = urlparse(u)
            path = parsed.path.rstrip("/").lower()
            normalized_paths.add(path)
        except Exception:
            continue

    missing_pages: List[str] = []
    for page_group, candidate_paths in RECOMMENDED_ENTITY_PATHS.items():
        found = any(cand in normalized_paths for cand in candidate_paths)
        if not found:
            missing_pages.append(candidate_paths[0])
            conflicts.append(
                EntityConflict(
                    conflict_id=f"conflict:missing_page_{page_group}",
                    conflict_type="MISSING_REQUIRED_PAGE",
                    severity="LOW",
                    entity_id="site:pages",
                    entity_name="Website Entity Architecture",
                    description=f"Missing recommended {page_group.replace('_', ' ')} page ({candidate_paths[0]}) for establishing entity authority.",
                    conflicting_evidence={"candidate_paths": candidate_paths}
                )
            )

    return conflicts, missing_pages
