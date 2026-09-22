"""Tests for AevoraSEO source and citation readiness signals."""

import unittest

from aevoraseo.aeo.citations import (
    analyze_page_citations,
    calculate_factual_density,
    extract_outbound_citations,
)


class TestAEOCitations(unittest.TestCase):
    def test_factual_density_calculation(self):
        # Text rich with numbers, percentages, and currencies
        rich_text = (
            "In 2025, cloud infrastructure expenditures surged by 34.5% reaching $120.4 billion. "
            "Average latency dropped to 42 ms across 15 global clusters handling 5,000,000 queries per second."
        )
        density = calculate_factual_density(rich_text)
        self.assertGreater(density, 0.4)

        # Fluffy text with zero factual figures
        fluffy_text = (
            "We believe in providing the absolute best experience for our cherished clients. "
            "Our dedication to excellence and wonderful customer satisfaction has always been paramount."
        )
        low_density = calculate_factual_density(fluffy_text)
        self.assertEqual(low_density, 0.0)

    def test_outbound_citations_extraction(self):
        page_url = "https://example.com/research-paper"
        links = [
            {"href": "https://example.com/about", "text": "About us"},
            {"href": "https://arxiv.org/abs/2301.00001", "text": "Primary Research"},
            {"href": "https://doi.org/10.1000/182", "text": "DOI reference"},
            {"href": "/local-link", "text": "Local"},
        ]
        count, domains = extract_outbound_citations(page_url, links)
        self.assertEqual(count, 2)
        self.assertIn("arxiv.org", domains)
        self.assertIn("doi.org", domains)

    def test_full_citation_signal_analysis(self):
        page_data = {
            "title": "Comprehensive SEO Study",
            "meta": {
                "author": ["Sarah Connor"],
                "article:published_time": ["2026-02-01T10:00:00Z"],
                "article:modified_time": ["2026-02-15T14:30:00Z"],
            },
            "jsonld": [],
            "main_text": "In 2026, 45% of organic traffic converted at $35 per order.",
            "links": [{"href": "https://reuters.com/news/123", "text": "Reuters"}],
            "canonical": [{"url": "https://example.com/study"}],
        }
        sig = analyze_page_citations("https://example.com/study", page_data)
        self.assertEqual(sig.author, "Sarah Connor")
        self.assertEqual(sig.date_published, "2026-02-01T10:00:00Z")
        self.assertEqual(sig.date_modified, "2026-02-15T14:30:00Z")
        self.assertEqual(sig.outbound_references_count, 1)
        self.assertTrue(sig.has_canonical)
        self.assertTrue(sig.canonical_matches_url)


if __name__ == "__main__":
    unittest.main()
