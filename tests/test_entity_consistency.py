"""
Unit tests for AevoraSEO Entity Consistency & Conflict Auditor.
"""

from aevoraseo.entity.consistency import audit_entity_conflicts
from aevoraseo.entity.models import EntityNode, SameAsLink


def test_detect_conflicting_org_names():
    nodes = [
        EntityNode(
            entity_id="org:alpha_enterprises",
            entity_type="Organization",
            canonical_name="Alpha Enterprises",
            source_pages=["https://example.com/page1"],
        ),
        EntityNode(
            entity_id="org:beta_enterprises",
            entity_type="Organization",
            canonical_name="Beta Enterprises Global",
            source_pages=["https://example.com/page2"],
        ),
    ]
    same_as = []
    crawled_urls = ["https://example.com/about", "https://example.com/contact"]

    conflicts, _ = audit_entity_conflicts(nodes, same_as, crawled_urls)
    assert any(c.conflict_type == "NAME_INCONSISTENCY" and c.severity == "HIGH" for c in conflicts)


def test_detect_nap_mismatches():
    nodes = [
        EntityNode(
            entity_id="org:acme",
            entity_type="Organization",
            canonical_name="Acme Inc",
            attributes={
                "telephone": "+1-555-1111",
                "address": {"streetAddress": "100 Main St", "addressLocality": "Austin"},
            },
            source_pages=["https://example.com/home"],
        ),
        EntityNode(
            entity_id="org:acme_branch",
            entity_type="Organization",
            canonical_name="Acme Inc",
            attributes={
                "telephone": "+1-555-2222",
                "address": {"streetAddress": "200 Oak Ave", "addressLocality": "Dallas"},
            },
            source_pages=["https://example.com/contact"],
        ),
    ]
    same_as = []
    crawled_urls = ["https://example.com/home", "https://example.com/contact"]

    conflicts, _ = audit_entity_conflicts(nodes, same_as, crawled_urls)
    assert any(c.conflict_type == "NAP_MISMATCH" and "phone" in c.description.lower() for c in conflicts)
    assert any(c.conflict_type == "NAP_MISMATCH" and "address" in c.description.lower() for c in conflicts)


def test_detect_broken_same_as():
    nodes = [
        EntityNode(
            entity_id="org:acme",
            entity_type="Organization",
            canonical_name="Acme",
        )
    ]
    same_as = [
        SameAsLink(
            url="not-a-valid-url",
            platform="Other",
            entity_name="Acme",
            is_valid_url=False,
            is_high_authority=False,
            found_on_url="https://example.com",
        )
    ]
    crawled_urls = ["https://example.com"]

    conflicts, _ = audit_entity_conflicts(nodes, same_as, crawled_urls)
    assert any(c.conflict_type == "BROKEN_SAMEAS" for c in conflicts)


def test_detect_missing_core_entity_pages():
    nodes = [
        EntityNode(
            entity_id="org:acme",
            entity_type="Organization",
            canonical_name="Acme",
        )
    ]
    same_as = []
    # Only home and pricing crawled; missing about, contact, team, reviews
    crawled_urls = ["https://example.com/", "https://example.com/pricing"]

    conflicts, missing_pages = audit_entity_conflicts(nodes, same_as, crawled_urls)
    assert "/about" in missing_pages
    assert "/contact" in missing_pages
    assert "/team" in missing_pages
    assert any(c.conflict_type == "MISSING_REQUIRED_PAGE" for c in conflicts)
