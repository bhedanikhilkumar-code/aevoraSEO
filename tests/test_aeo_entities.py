"""Tests for AevoraSEO AEO entity extraction, validation, and conflict auditing."""

import unittest

from aevoraseo.aeo.entities import (
    analyze_page_entities,
    detect_cross_page_conflicts,
    extract_entities_from_jsonld,
)


class TestAEOEntities(unittest.TestCase):
    def test_jsonld_entity_extraction(self):
        jsonld = [
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Aevora Technologies",
                "url": "https://aevora.example.com",
                "sameAs": [
                    "https://www.wikidata.org/wiki/Q12345",
                    "https://github.com/aevora",
                ],
            },
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Understanding Generative Search Engines",
                "author": {
                    "@type": "Person",
                    "name": "Dr. Alex Vance",
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "Aevora Technologies",
                },
            },
        ]
        entities = extract_entities_from_jsonld(jsonld, page_title="Understanding Generative Search Engines")
        self.assertGreaterEqual(len(entities), 2)

        # Organization check
        org = next(e for e in entities if e.entity_type == "Organization")
        self.assertEqual(org.name, "Aevora Technologies")
        self.assertEqual(len(org.same_as), 2)
        self.assertTrue(org.is_consistent)

        # Article check
        art = next(e for e in entities if e.entity_type == "Article")
        self.assertEqual(art.name, "Understanding Generative Search Engines")
        self.assertEqual(art.relationships.get("author"), "Dr. Alex Vance")
        self.assertEqual(art.relationships.get("publisher"), "Aevora Technologies")

    def test_meta_fallback_entities(self):
        page_data = {
            "title": "Welcome to Acme",
            "jsonld": [],
            "meta": {
                "og:site_name": ["Acme Corp"],
                "author": ["Jane Doe"],
            },
        }
        entities = analyze_page_entities(page_data)
        types = {e.entity_type: e.name for e in entities}
        self.assertEqual(types.get("Organization"), "Acme Corp")
        self.assertEqual(types.get("Person"), "Jane Doe")

    def test_cross_page_entity_conflicts(self):
        page_results = [
            (
                "https://example.com/page1",
                analyze_page_entities({
                    "jsonld": [{"@type": "Organization", "name": "Acme Global Solutions"}],
                    "title": "Home",
                }),
            ),
            (
                "https://example.com/page2",
                analyze_page_entities({
                    "jsonld": [{"@type": "Organization", "name": "Beta Industries Inc"}],
                    "title": "About",
                }),
            ),
        ]
        conflicts = detect_cross_page_conflicts(page_results)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["type"], "conflicting_organization_names")


if __name__ == "__main__":
    unittest.main()
