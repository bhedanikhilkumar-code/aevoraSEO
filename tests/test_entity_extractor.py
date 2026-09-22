"""
Unit tests for AevoraSEO Multi-Source Entity Extractor.
"""

from aevoraseo.entity.extractor import EntityExtractor
from aevoraseo.entity.models import EntityType


def test_extract_organization_and_person():
    extractor = EntityExtractor()
    page_data = {
        "jsonld": [
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Acme Global Corporation",
                "legalName": "Acme Global Corp LLC",
                "url": "https://acmeglobal.example.com",
                "logo": "https://acmeglobal.example.com/logo.png",
                "description": "Leading provider of autonomous robotic widgets and planetary solutions.",
                "telephone": "+1-800-555-0199",
                "email": "contact@acmeglobal.example.com",
                "foundingDate": "2020-01-15",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "123 Innovation Drive",
                    "addressLocality": "San Francisco",
                    "addressRegion": "CA",
                    "postalCode": "94105",
                    "addressCountry": "US",
                },
                "sameAs": [
                    "https://www.wikidata.org/wiki/Q123456",
                    "https://en.wikipedia.org/wiki/Acme_Global",
                    "https://www.linkedin.com/company/acme-global",
                    "https://github.com/acme-global",
                ],
                "founder": {
                    "@type": "Person",
                    "name": "Jane Doe",
                    "jobTitle": "Chief Executive Officer & Founder",
                    "sameAs": "https://www.linkedin.com/in/janedoe",
                },
            }
        ]
    }

    nodes = extractor.extract_from_page("https://acmeglobal.example.com", page_data)
    
    org_nodes = [n for n in nodes if n.entity_type == "Organization"]
    assert len(org_nodes) == 1
    org = org_nodes[0]
    assert org.canonical_name == "Acme Global Corporation"
    assert org.attributes["legalName"] == "Acme Global Corp LLC"
    assert org.attributes["telephone"] == "+1-800-555-0199"
    assert len(org.attributes["same_as"]) == 4

    person_nodes = [n for n in nodes if n.entity_type == "Person"]
    assert len(person_nodes) == 1
    person = person_nodes[0]
    assert person.canonical_name == "Jane Doe"
    assert person.attributes["jobTitle"] == "Chief Executive Officer & Founder"

    # Check relationship edges
    assert len(extractor.edges) >= 1
    edge = extractor.edges[0]
    assert edge.relationship_type == "FOUNDED_BY"
    assert edge.source_id == person.entity_id
    assert edge.target_id == org.entity_id


def test_extract_product_and_service():
    extractor = EntityExtractor()
    page_data = {
        "jsonld": [
            {
                "@context": "https://schema.org",
                "@type": "Service",
                "name": "Autonomous SEO Optimization",
                "serviceType": "Search Engine Intelligence",
                "provider": {
                    "@type": "Organization",
                    "name": "AevoraSEO",
                },
                "offers": {
                    "@type": "Offer",
                    "price": "499.00",
                    "priceCurrency": "USD",
                },
            },
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Aevora Engine Pro",
                "sku": "AEV-PRO-01",
                "brand": {
                    "@type": "Organization",
                    "name": "AevoraSEO",
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.9",
                    "reviewCount": "120",
                },
            },
        ]
    }

    extractor.extract_from_page("https://example.com/services", page_data)
    nodes = extractor.nodes

    assert any(n.entity_type == "Service" and n.canonical_name == "Autonomous SEO Optimization" for n in nodes.values())
    assert any(n.entity_type == "Product" and n.canonical_name == "Aevora Engine Pro" for n in nodes.values())
    assert any(n.entity_type == "Organization" and n.canonical_name == "AevoraSEO" for n in nodes.values())


def test_extract_fallback_from_meta():
    extractor = EntityExtractor()
    page_data = {
        "jsonld": [],
        "meta": {
            "og:site_name": ["Nexus Intelligence"],
            "author": ["Alex River"],
        },
    }

    extractor.extract_from_page("https://nexus.example.com/article", page_data)
    nodes = extractor.nodes

    assert any(n.entity_type == "Organization" and n.canonical_name == "Nexus Intelligence" for n in nodes.values())
    assert any(n.entity_type == "Person" and n.canonical_name == "Alex River" for n in nodes.values())
