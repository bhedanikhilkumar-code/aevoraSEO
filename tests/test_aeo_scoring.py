"""Tests for AevoraSEO transparent scoring calculations."""

import unittest

from aevoraseo.aeo.models import (
    CitationSignal,
    ContentStructureSignal,
    CrawlerAccessSignal,
    EntitySignal,
    QuestionAnswerSignal,
    SchemaQualitySignal,
)
from aevoraseo.aeo.scoring import calculate_aeo_readiness, calculate_geo_signals


class TestAEOScoring(unittest.TestCase):
    def test_aeo_readiness_scoring(self):
        questions = [
            QuestionAnswerSignal(
                question="What is Answer Engine Optimization?",
                detected=True,
                answer_detected=True,
                answer_text="AEO is the practice of optimizing content for direct answering.",
                answer_location="heading:h2 + p",
                interrogative_type="what",
                confidence=0.92,
            ),
            QuestionAnswerSignal(
                question="How do generative engines select sources?",
                detected=True,
                answer_detected=True,
                answer_text="Generative engines evaluate authority, entity clarity, and citation signals.",
                answer_location="heading:h3 + p",
                interrogative_type="how",
                confidence=0.88,
            ),
        ]
        structure = ContentStructureSignal(
            has_h1=True,
            h1_count=1,
            heading_hierarchy_valid=True,
            structural_weaknesses=[],
            paragraph_count=8,
            unbroken_text_blocks=0,
            list_count=2,
            table_count=1,
            word_count=750,
        )
        schemas = [
            SchemaQualitySignal(
                schema_type="Article",
                detected=True,
                valid=True,
                complete=True,
                consistent=True,
                present_properties=["headline", "author", "datePublished"],
                missing_required=[],
                errors=[],
            )
        ]
        crawler_access = [
            CrawlerAccessSignal(
                bot_name="GPTBot",
                user_agent="GPTBot",
                observed_rule="allow",
                policy_source="robots.txt",
                status="crawl_allowed",
            )
        ]

        score, dimensions = calculate_aeo_readiness(questions, structure, schemas, crawler_access)
        self.assertGreaterEqual(score, 70.0)
        self.assertIn("answer_readiness", dimensions)
        self.assertIn("question_coverage", dimensions)
        self.assertIn("content_structure", dimensions)
        self.assertIn("schema_quality", dimensions)
        self.assertIn("crawler_accessibility", dimensions)

        # Check signal contributions
        self.assertTrue(len(dimensions["answer_readiness"].signals) > 0)
        self.assertEqual(len(dimensions["answer_readiness"].deductions), 0)

    def test_geo_signal_scoring(self):
        entities = [
            EntitySignal(
                entity_type="Organization",
                name="Aevora Research",
                source="jsonld",
                same_as=["https://wikidata.org/wiki/Q999"],
                relationships={"founder": "Alice"},
                is_consistent=True,
            )
        ]
        citations = CitationSignal(
            author="Alice Stone",
            publisher="Aevora Research",
            date_published="2026-01-01",
            date_modified="2026-02-01",
            outbound_references_count=4,
            outbound_citation_domains=["nature.com", "arxiv.org"],
            factual_density_score=0.65,
            has_canonical=True,
            canonical_matches_url=True,
        )
        schemas = [
            SchemaQualitySignal(
                schema_type="Organization",
                detected=True,
                valid=True,
                complete=True,
                consistent=True,
                present_properties=["name", "url"],
            ),
            SchemaQualitySignal(
                schema_type="Article",
                detected=True,
                valid=True,
                complete=True,
                consistent=True,
                present_properties=["headline", "author"],
            ),
        ]

        score, dimensions = calculate_geo_signals(
            entities=entities,
            citations=citations,
            schemas=schemas,
            word_count=1300,
            has_tables_or_lists=True,
        )
        self.assertGreaterEqual(score, 75.0)
        self.assertIn("entity_clarity", dimensions)
        self.assertIn("source_readiness", dimensions)
        self.assertIn("factual_specificity", dimensions)
        self.assertIn("topical_completeness", dimensions)
        self.assertIn("structured_data_richness", dimensions)


if __name__ == "__main__":
    unittest.main()
