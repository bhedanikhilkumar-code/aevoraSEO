"""
Unit and integration tests for Backlink Intelligence:
Anchor context extraction, rel parsing, dofollow categorization,
source classification, referring domain metrics, catalog opportunities,
and SQLite persistence round-trips.
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aevoraseo.backlink_persistence import (
    init_backlink_db,
    load_backlink_snapshot,
    load_reputation_assessment,
    persist_backlink_verification,
    persist_reputation_assessment,
)
from aevoraseo.backlinks import (
    check_sources,
    classify_source_context,
    source_rows,
    target_links,
    verify_source,
)
from aevoraseo.reputation import (
    assess,
    extract_backlink_opportunities,
    reputation,
    source_score,
)

TARGET = "https://example.com/"


class BacklinkIntelligenceTests(unittest.TestCase):
    def test_target_links_extracts_anchor_rel_dofollow_and_context(self):
        page_data = {
            "text": "Check out our trusted partner Example Company for modern solutions.",
            "main_text": "Check out our trusted partner Example Company for modern solutions.",
            "links": [
                {
                    "url": "https://example.com/product",
                    "anchor": "Example Company",
                    "rel": ["noopener", "noreferrer"],
                },
                {
                    "url": "https://example.com/pricing",
                    "anchor": "pricing",
                    "rel": ["nofollow", "sponsored"],
                },
                {
                    "url": "https://unrelated.com/blog",
                    "anchor": "unrelated",
                    "rel": [],
                },
            ],
        }
        links = target_links(page_data, "example.com")
        self.assertEqual(len(links), 2)

        # First link: dofollow with context
        first = links[0]
        self.assertEqual(first["url"], "https://example.com/product")
        self.assertEqual(first["target_path"], "/product")
        self.assertEqual(first["anchor"], "Example Company")
        self.assertTrue(first["is_dofollow"])
        self.assertIn("partner Example Company for modern", first["context"])

        # Second link: nofollow/sponsored
        second = links[1]
        self.assertEqual(second["url"], "https://example.com/pricing")
        self.assertEqual(second["target_path"], "/pricing")
        self.assertFalse(second["is_dofollow"])
        self.assertEqual(set(second["rel"]), {"nofollow", "sponsored"})

    def test_classify_source_context(self):
        # Community
        comm = classify_source_context("https://www.reddit.com/r/seo/comments/123")
        self.assertEqual(comm["context"], "user_generated")
        self.assertEqual(comm["relationship"], "independent")

        # Directory / Profile
        dir_res = classify_source_context("https://clutch.co/profile/example")
        self.assertEqual(dir_res["context"], "directory")
        self.assertEqual(dir_res["relationship"], "third_party_profile")

        prof = classify_source_context("https://github.com/example")
        self.assertEqual(prof["context"], "directory")
        self.assertEqual(prof["relationship"], "third_party_profile")

        # Editorial
        edit = classify_source_context("https://techcrunch.com/2026/01/01/ai-news")
        self.assertEqual(edit["context"], "editorial")
        self.assertEqual(edit["relationship"], "independent")

    def test_referring_domain_aggregation_and_dofollow_metrics(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir) / "backlinks_out"
            verified_sample = {
                "source_url": "https://publisher1.com/article",
                "final_url": "https://publisher1.com/article",
                "verification": "link_observed",
                "representation": "http",
                "status": 200,
                "error": "",
                "target_links": [
                    {
                        "url": "https://example.com/",
                        "target_path": "/",
                        "anchor": "Example",
                        "rel": [],
                        "is_dofollow": True,
                        "context": "Visit Example.",
                    },
                    {
                        "url": "https://example.com/docs",
                        "target_path": "/docs",
                        "anchor": "Docs",
                        "rel": ["nofollow"],
                        "is_dofollow": False,
                        "context": "Read Docs.",
                    },
                ],
                "brand_mentions": [{"name": "Example", "excerpt": "Example is great."}],
                "evidence_folder": "sources/dummy",
                "attempt_history": [],
            }
            with patch("aevoraseo.backlinks.verify_source", return_value=verified_sample):
                res = check_sources(
                    [{"URL": "https://publisher1.com/article"}],
                    "https://example.com",
                    out,
                    brand="Example",
                )

            self.assertEqual(res["observed_link_pages"], 1)
            self.assertEqual(res["total_links_observed"], 2)
            self.assertEqual(res["dofollow_links_count"], 1)
            self.assertEqual(res["nofollow_links_count"], 1)
            self.assertEqual(res["referring_domains"], ["publisher1.com"])
            self.assertEqual(res["referring_domains_count"], 1)

            # Check exported backlinks.csv
            csv_path = out / "backlinks.csv"
            self.assertTrue(csv_path.exists())
            content = csv_path.read_text(encoding="utf-8-sig")
            self.assertIn("publisher1.com", content)
            self.assertIn("https://example.com/docs", content)
            self.assertIn("nofollow", content)

    def test_sqlite_persistence_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test_backlinks.sqlite3"
            init_backlink_db(db_path)

            verification_data = {
                "target": TARGET,
                "brand": "Example",
                "checked_at": "2026-09-22T10:00:00Z",
                "sources_supplied": 3,
                "sources_checked": 3,
                "sources_remaining": 0,
                "observed_link_pages": 1,
                "observed_mention_pages": 2,
                "unverified_pages": 0,
                "note": "Test note",
                "results": [
                    {
                        "source_url": "https://editorial.com/post",
                        "final_url": "https://editorial.com/post",
                        "publisher_group": "editorial.com",
                        "verification": "link_observed",
                        "representation": "http",
                        "status": 200,
                        "error": "",
                        "target_links": [
                            {
                                "url": "https://example.com/",
                                "target_path": "/",
                                "anchor": "Example Homepage",
                                "rel": ["noopener"],
                                "is_dofollow": True,
                                "context": "Visit Example Homepage here.",
                            }
                        ],
                        "brand_mentions": [{"name": "Example", "excerpt": "Example is leading the way."}],
                    }
                ],
            }

            sid = persist_backlink_verification(db_path, verification_data)
            self.assertTrue(sid)

            # Load back from SQLite
            loaded = load_backlink_snapshot(db_path, sid)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["target"], TARGET)
            self.assertEqual(loaded["observed_link_pages"], 1)
            self.assertEqual(len(loaded["results"]), 1)
            self.assertEqual(loaded["results"][0]["source_url"], "https://editorial.com/post")
            self.assertEqual(len(loaded["results"][0]["target_links"]), 1)
            self.assertEqual(loaded["results"][0]["target_links"][0]["text"], "Example Homepage")

    def test_extract_backlink_opportunities_with_catalog(self):
        scored = [
            {
                "source_url": "https://dev.to/example-user/my-post",
                "final_url": "https://dev.to/example-user/my-post",
                "publisher_group": "dev.to",
                "observed_link": True,
                "observed_mention": True,
                "supported_quality_points": 70,
                "brand_mentions": [{"name": "Example", "excerpt": "Example post"}],
            },
            {
                "source_url": "https://news.ycombinator.com/item?id=123",
                "final_url": "https://news.ycombinator.com/item?id=123",
                "publisher_group": "ycombinator.com",
                "observed_link": False,
                "observed_mention": True,
                "supported_quality_points": 25,
                "brand_mentions": [{"name": "Example", "excerpt": "Heard about Example recently."}],
            },
        ]

        opps = extract_backlink_opportunities("https://example.com", "Example", scored)
        self.assertEqual(opps["acquired_count"], 1)
        self.assertEqual(opps["unlinked_mention_count"], 1)
        self.assertGreater(opps["catalog_prospects_count"], 0)

        # dev.to is already acquired, so it should not appear in catalog_shortlist
        shortlist_domains = {p["domain"] for p in opps["catalog_shortlist"]}
        self.assertNotIn("dev.to", shortlist_domains)

        # Unlinked mention from ycombinator
        mention = opps["unlinked_mentions"][0]
        self.assertEqual(mention["domain"], "news.ycombinator.com")
        self.assertEqual(mention["priority"], "HIGH")

    def test_reputation_sqlite_persistence(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "rep_test.sqlite3"
            assessment = {
                "name": "AevoraSEO Reputation Score",
                "model_version": "1.1",
                "target": TARGET,
                "brand": "Example",
                "score": 42.5,
                "score_range": [35.0, 50.0],
                "score_status": "provisional",
                "confidence": "low",
                "sample_quality_estimate": 60.0,
                "checked_at": "2026-09-22T10:00:00Z",
                "evidence_adjustment": {"factor": 0.5},
            }
            aid = persist_reputation_assessment(db_path, assessment)
            self.assertTrue(aid)

            loaded = load_reputation_assessment(db_path, aid)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["score"], 42.5)
            self.assertEqual(loaded["confidence"], "low")


if __name__ == "__main__":
    unittest.main()
