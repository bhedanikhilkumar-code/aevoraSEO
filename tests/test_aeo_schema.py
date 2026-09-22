"""Tests for AevoraSEO structured data schema auditing."""

import unittest

from aevoraseo.aeo.schema import audit_page_schema


class TestAEOSchema(unittest.TestCase):
    def test_complete_and_consistent_schema(self):
        page_data = {
            "title": "Machine Learning Fundamentals",
            "jsonld": [
                {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": "Machine Learning Fundamentals",
                    "author": {"@type": "Person", "name": "Elena Rostova"},
                    "datePublished": "2026-01-15T08:00:00Z",
                    "publisher": {"@type": "Organization", "name": "AI Institute"},
                    "url": "https://example.com/ml-fundamentals",
                }
            ],
            "jsonld_errors": [],
            "microdata_types": [],
        }
        signals = audit_page_schema(page_data, canonical_url="https://example.com/ml-fundamentals")
        article_sig = next(s for s in signals if s.schema_type == "Article")

        self.assertTrue(article_sig.detected)
        self.assertTrue(article_sig.valid)
        self.assertTrue(article_sig.complete)
        self.assertTrue(article_sig.consistent)
        self.assertEqual(article_sig.missing_required, [])

    def test_incomplete_schema(self):
        page_data = {
            "title": "Incomplete Article",
            "jsonld": [
                {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    # Missing author and datePublished
                    "headline": "Incomplete Article",
                }
            ],
            "jsonld_errors": [],
            "microdata_types": [],
        }
        signals = audit_page_schema(page_data)
        article_sig = next(s for s in signals if s.schema_type == "Article")

        self.assertTrue(article_sig.valid)
        self.assertFalse(article_sig.complete)
        self.assertIn("author", article_sig.missing_required)
        self.assertIn("datePublished", article_sig.missing_required)

    def test_malformed_jsonld_syntax_error(self):
        page_data = {
            "title": "Malformed Page",
            "jsonld": [],
            "jsonld_errors": [{"block": 0, "error": "Expecting property name enclosed in double quotes"}],
            "microdata_types": [],
        }
        signals = audit_page_schema(page_data)
        self.assertEqual(len(signals), 1)
        err_sig = signals[0]
        self.assertTrue(err_sig.detected)
        self.assertFalse(err_sig.valid)
        self.assertIn("syntax error", err_sig.errors[0])


if __name__ == "__main__":
    unittest.main()
