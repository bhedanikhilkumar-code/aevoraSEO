"""
Tests for Reputation Snapshot Comparison Engine:
Before/after score deltas, added/lost/retained backlinks and mentions,
opportunity conversions, multi-format exports, and SQLite persistence.
"""

import json
import tempfile
import unittest
from pathlib import Path

from aevoraseo.backlink_persistence import load_reputation_diff, persist_reputation_diff
from aevoraseo.reputation_comparison import (
    compare_reputation_snapshots,
    generate_reputation_diff_markdown,
)

TARGET = "https://example.com"
BRAND = "Example"


class ReputationComparisonTests(unittest.TestCase):
    def setUp(self):
        self.before_snapshot = {
            "name": "AevoraSEO Reputation Score",
            "model_version": "1.1",
            "target": TARGET,
            "brand": BRAND,
            "checked_at": "2026-09-01T00:00:00Z",
            "score": 35.0,
            "score_range": [30.0, 45.0],
            "score_status": "provisional",
            "confidence": "low",
            "coverage": {
                "unique_publisher_groups_with_evidence": 2,
            },
            "sources": [
                {
                    "source_url": "https://pub1.test/article",
                    "publisher_group": "pub1.test",
                    "observed_link": True,
                    "observed_mention": True,
                    "target_links": [
                        {
                            "url": f"{TARGET}/",
                            "anchor": "Example",
                            "rel": ["noopener"],
                            "is_dofollow": True,
                        }
                    ],
                    "brand_mentions": [{"name": "Example", "excerpt": "Example is great"}],
                    "quality_estimate": 60.0,
                },
                {
                    "source_url": "https://pub2.test/review",
                    "publisher_group": "pub2.test",
                    "observed_link": False,
                    "observed_mention": True,
                    "target_links": [],
                    "brand_mentions": [{"name": "Example", "excerpt": "We reviewed Example"}],
                    "quality_estimate": 25.0,
                },
            ],
        }

        self.after_snapshot = {
            "name": "AevoraSEO Reputation Score",
            "model_version": "1.1",
            "target": TARGET,
            "brand": BRAND,
            "checked_at": "2026-09-22T00:00:00Z",
            "score": 65.0,
            "score_range": [60.0, 75.0],
            "score_status": "assessed_within_sample",
            "confidence": "moderate within this sample",
            "coverage": {
                "unique_publisher_groups_with_evidence": 3,
            },
            "sources": [
                # pub1.test retained
                {
                    "source_url": "https://pub1.test/article",
                    "publisher_group": "pub1.test",
                    "observed_link": True,
                    "observed_mention": True,
                    "target_links": [
                        {
                            "url": f"{TARGET}/",
                            "anchor": "Example",
                            "rel": ["noopener"],
                            "is_dofollow": True,
                        }
                    ],
                    "brand_mentions": [{"name": "Example", "excerpt": "Example is great"}],
                    "quality_estimate": 60.0,
                },
                # pub2.test gained a backlink! (Opportunity conversion)
                {
                    "source_url": "https://pub2.test/review",
                    "publisher_group": "pub2.test",
                    "observed_link": True,
                    "observed_mention": True,
                    "target_links": [
                        {
                            "url": f"{TARGET}/features",
                            "anchor": "Example Features",
                            "rel": [],
                            "is_dofollow": True,
                        }
                    ],
                    "brand_mentions": [{"name": "Example", "excerpt": "We reviewed Example features"}],
                    "quality_estimate": 70.0,
                },
                # pub3.test is completely new
                {
                    "source_url": "https://pub3.test/news",
                    "publisher_group": "pub3.test",
                    "observed_link": True,
                    "observed_mention": True,
                    "target_links": [
                        {
                            "url": f"{TARGET}/press",
                            "anchor": "Press Release",
                            "rel": ["nofollow"],
                            "is_dofollow": False,
                        }
                    ],
                    "brand_mentions": [{"name": "Example", "excerpt": "News on Example"}],
                    "quality_estimate": 50.0,
                },
            ],
        }

    def test_compare_reputation_score_delta_and_conversions(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            diff = compare_reputation_snapshots(
                self.before_snapshot, self.after_snapshot, out_dir=tmp_dir
            )

            s = diff["summary"]
            self.assertEqual(s["score_delta"], 30.0)
            self.assertEqual(s["before_score"], 35.0)
            self.assertEqual(s["after_score"], 65.0)
            self.assertEqual(s["before_confidence"], "low")
            self.assertEqual(s["after_confidence"], "moderate within this sample")

            # Backlinks
            self.assertEqual(s["retained_backlinks_count"], 1)  # pub1
            self.assertEqual(s["new_backlinks_count"], 2)  # pub2 and pub3
            self.assertEqual(s["lost_backlinks_count"], 0)

            # Opportunity conversion: pub2 was unlinked mention, now has a link
            self.assertEqual(s["opportunity_conversions_count"], 1)
            conv = diff["opportunity_conversions"][0]
            self.assertEqual(conv["source_url"], "https://pub2.test/review")
            self.assertEqual(conv["target_url"], f"{TARGET}/features")

            # Check generated files
            out = Path(tmp_dir)
            self.assertTrue((out / "reputation_comparison.json").exists())
            self.assertTrue((out / "reputation_comparison.md").exists())
            self.assertTrue((out / "reputation_comparison.csv").exists())
            self.assertTrue((out / "reputation.sqlite3").exists())

            # Verify SQLite persistence
            db_path = out / "reputation.sqlite3"
            loaded_diff = load_reputation_diff(db_path, diff["diff_id"])
            self.assertIsNotNone(loaded_diff)
            self.assertEqual(loaded_diff["summary"]["score_delta"], 30.0)

    def test_lost_backlinks_and_mentions_detection(self):
        # Inverted comparison: after -> before
        diff = compare_reputation_snapshots(self.after_snapshot, self.before_snapshot)
        s = diff["summary"]
        self.assertEqual(s["score_delta"], -30.0)
        self.assertEqual(s["lost_backlinks_count"], 2)
        self.assertEqual(s["new_backlinks_count"], 0)
        self.assertEqual(s["retained_backlinks_count"], 1)

    def test_generate_reputation_diff_markdown_content(self):
        diff = compare_reputation_snapshots(self.before_snapshot, self.after_snapshot)
        md = generate_reputation_diff_markdown(diff)
        self.assertIn("# Reputation & Backlink Snapshot Comparison", md)
        self.assertIn("+30.0", md)
        self.assertIn("Converted Opportunities", md)
        self.assertIn("New Observed Backlinks", md)
        self.assertIn("pub2.test/review", md)


if __name__ == "__main__":
    unittest.main()
