"""
AevoraSEO Entity & Authority Scoring Engine
Calculates the 0–100 Entity & Authority Headline Score across four conservative, evidence-based dimensions.
"""

from typing import Any, Dict, List, Optional, Tuple

from .models import AuthorityPlatform, EntityConflict, EntityNode, EntityScore, SameAsLink


def calculate_entity_authority_score(
    nodes: List[EntityNode],
    conflicts: List[EntityConflict],
    same_as_links: List[SameAsLink],
    missing_pages: List[str]
) -> EntityScore:
    """
    Computes the 0–100 AevoraSEO Entity & Authority Score based strictly on observed evidence.
    """
    contributing: Dict[str, float] = {}
    deductions: List[str] = []

    # 1. Identity Completeness (0–25)
    org_nodes = [n for n in nodes if n.entity_type in ("Organization", "Corporation", "LocalBusiness")]
    primary_org: Optional[EntityNode] = org_nodes[0] if org_nodes else None

    id_pts = 0.0
    if primary_org:
        id_pts += 5.0
        contributing["org_declared"] = 5.0

        attrs = primary_org.attributes
        if attrs.get("url") or attrs.get("logo"):
            id_pts += 5.0
            contributing["brand_assets"] = 5.0

        if attrs.get("description") and len(attrs["description"]) > 20:
            id_pts += 5.0
            contributing["description_depth"] = 5.0

        if attrs.get("telephone") or attrs.get("email") or attrs.get("address"):
            id_pts += 5.0
            contributing["contact_or_location"] = 5.0

        if attrs.get("foundingDate") or any(n.entity_type == "Person" and "founder" in n.entity_id for n in nodes):
            id_pts += 5.0
            contributing["founding_provenance"] = 5.0
    else:
        deductions.append("No primary Organization or LocalBusiness entity declared on website.")

    id_score = min(25.0, id_pts)

    # 2. Entity Consistency & Integrity (0–25)
    consistency_pts = 25.0
    for c in conflicts:
        if c.severity == "HIGH":
            deduction = 10.0
            consistency_pts -= deduction
            deductions.append(f"[-10 pts] High-severity conflict: {c.description}")
        elif c.severity == "MEDIUM":
            deduction = 5.0
            consistency_pts -= deduction
            deductions.append(f"[-5 pts] Medium-severity conflict: {c.description}")
        elif c.severity == "LOW":
            deduction = 2.0
            consistency_pts -= deduction
            deductions.append(f"[-2 pts] Low-severity finding: {c.description}")

    consistency_score = max(0.0, round(consistency_pts, 2))

    # 3. SameAs & Authority Footprint (0–25)
    valid_same_as = [sa for sa in same_as_links if sa.is_valid_url]
    platforms = {sa.platform for sa in valid_same_as}

    footprint_pts = 0.0
    if AuthorityPlatform.WIKIPEDIA.value in platforms or AuthorityPlatform.WIKIDATA.value in platforms:
        footprint_pts += 10.0
        contributing["semantic_wiki_authority"] = 10.0

    if AuthorityPlatform.LINKEDIN.value in platforms or AuthorityPlatform.CRUNCHBASE.value in platforms:
        footprint_pts += 8.0
        contributing["corporate_registry_authority"] = 8.0

    if any(p in platforms for p in (AuthorityPlatform.GITHUB.value, AuthorityPlatform.ORCID.value, AuthorityPlatform.TRUSTPILOT.value, AuthorityPlatform.GOOGLE_BUSINESS.value)):
        footprint_pts += 5.0
        contributing["industry_reputation_profiles"] = 5.0

    # Remaining profiles earn +2 pts each
    other_platforms = platforms - {
        AuthorityPlatform.WIKIPEDIA.value,
        AuthorityPlatform.WIKIDATA.value,
        AuthorityPlatform.LINKEDIN.value,
        AuthorityPlatform.CRUNCHBASE.value,
        AuthorityPlatform.GITHUB.value,
        AuthorityPlatform.ORCID.value,
        AuthorityPlatform.TRUSTPILOT.value,
        AuthorityPlatform.GOOGLE_BUSINESS.value,
    }
    footprint_pts += min(5.0, len(other_platforms) * 2.0)
    footprint_score = min(25.0, round(footprint_pts, 2))

    # 4. Topical & Expert Depth (0–25)
    expert_pts = 0.0
    person_nodes = [n for n in nodes if n.entity_type == "Person"]
    if person_nodes:
        # Check bio/jobTitle/alumnusOf depth
        has_bio = any(n.attributes.get("jobTitle") or n.attributes.get("description") for n in person_nodes)
        expert_pts += 10.0 if has_bio else 5.0
        contributing["person_expert_entities"] = 10.0 if has_bio else 5.0

    article_nodes = [n for n in nodes if n.entity_type in ("Article", "NewsArticle", "BlogPosting")]
    if article_nodes:
        expert_pts += 10.0
        contributing["content_authorship_attribution"] = 10.0

    service_prod_nodes = [n for n in nodes if n.entity_type in ("Service", "Product")]
    if service_prod_nodes:
        expert_pts += 5.0
        contributing["offerings_entity_mapping"] = 5.0

    expert_score = min(25.0, round(expert_pts, 2))

    # Total headline
    headline = round(id_score + consistency_score + footprint_score + expert_score, 1)

    # Confidence calculation
    has_high_conflict = any(c.severity == "HIGH" for c in conflicts)
    if primary_org and headline >= 70.0 and (footprint_score >= 15.0) and not has_high_conflict:
        confidence = "high"
    elif primary_org and headline >= 40.0:
        confidence = "medium"
    else:
        confidence = "low"

    return EntityScore(
        headline=headline,
        identity_completeness=id_score,
        entity_consistency=consistency_score,
        authority_footprint=footprint_score,
        topical_expert_depth=expert_score,
        contributing_factors=contributing,
        deductions=deductions,
        confidence=confidence,
    )
