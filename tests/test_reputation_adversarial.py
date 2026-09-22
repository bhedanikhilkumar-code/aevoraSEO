"""
Adversarial and Security Verification Tests for Backlink & Reputation Engine.
Covers CSV formula injection, pathological HTML, extreme anchor sizes,
Unicode handling, Windows SQLite file locking, and zero-evidence boundaries.
"""

import csv
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aevoraseo.backlink_persistence import (
    init_backlink_db,
    persist_backlink_verification,
    persist_reputation_assessment,
    persist_reputation_diff,
)
from aevoraseo.backlinks import (
    check_sources,
    sanitize_csv_cell,
    target_links,
)
from aevoraseo.reputation import (
    assess,
    export_assessment,
    reputation,
    source_score,
)
from aevoraseo.reputation_comparison import compare_reputation_snapshots

TARGET = "https://example.com"


class ReputationAdversarialTests(unittest.TestCase):
    def test_csv_formula_sanitization_unit(self):
        """Verify that all dangerous leading characters are prefixed with single quote."""
        risky = [
            "=1+1",
            "@SUM(A1:B10)",
            "+cmd|' /C calc'!A0",
            "-2+3",
            "\t=tab_formula",
            "\r=cr_formula",
            "   =spaced_formula",
        ]
        for val in risky:
            sanitized = sanitize_csv_cell(val)
            self.assertTrue(
                sanitized.startswith("'"),
                f"Failed to neutralize formula: {val} -> {sanitized}",
            )

        # Benign text is unaffected
        self.assertEqual(sanitize_csv_cell("Normal Anchor"), "Normal Anchor")
        self.assertEqual(sanitize_csv_cell(123), "123")
        self.assertEqual(sanitize_csv_cell(None), "")

    def test_backlinks_csv_export_neutralizes_formula_injection(self):
        """Check that backlinks.csv safely neutralizes formulas injected via anchor, context, or url."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir) / "out_backlinks"
            verified = {
                "source_url": "https://attacker.test/exploit",
                "final_url": "https://attacker.test/exploit",
                "verification": "link_observed",
                "representation": "http",
                "status": 200,
                "error": "",
                "target_links": [
                    {
                        "url": f"{TARGET}/",
                        "anchor": "=cmd|' /C calc'!A0",
                        "rel": ["@DANGEROUS"],
                        "is_dofollow": True,
                        "context": "+SUM(1,2)",
                    }
                ],
                "brand_mentions": [{"name": "-MALICIOUS", "excerpt": "=ALERT()"}],
                "evidence_folder": "sources/dummy",
                "attempt_history": [],
            }
            with patch("aevoraseo.backlinks.verify_source", return_value=verified):
                check_sources(
                    [{"URL": "https://attacker.test/exploit"}],
                    TARGET,
                    out,
                    brand="Example",
                )

            csv_file = out / "backlinks.csv"
            self.assertTrue(csv_file.exists())
            content = csv_file.read_text(encoding="utf-8-sig")

            # Must contain escaped formula
            self.assertIn("'=cmd|' /C calc'!A0", content)
            self.assertIn("'+SUM(1,2)", content)

    def test_reputation_opportunities_csv_neutralizes_injection(self):
        """Check that reputation-opportunities.csv and reputation-sources.csv neutralize formula injection."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir) / "out_rep"
            assessment_data = {
                "name": "AevoraSEO Reputation Score",
                "model_version": "1.1",
                "target": TARGET,
                "brand": "=CALC()",
                "checked_at": "2026-09-22T00:00:00Z",
                "score": 50.0,
                "score_range": [40.0, 60.0],
                "score_status": "assessed_within_sample",
                "confidence": "moderate within this sample",
                "range_meaning": "Test range",
                "observed_link_pages": 1,
                "observed_mention_pages": 1,
                "total_backlinks_note": "Test note",
                "formula": "Test formula",
                "evidence_adjustment": {
                    "factor": 1.0,
                    "confidence_ceiling": 100.0,
                    "limiting_factors": [],
                },
                "sample_quality_estimate": 50.0,
                "sample_quality_range": [40.0, 60.0],
                "top_backlinks": [],
                "top_mentions_without_links": [],
                "coverage": {
                    "sources_checked": 1,
                    "conclusive_link_checks": 1,
                    "partial_or_unverified_link_checks": 0,
                    "sources_with_positive_evidence": 1,
                    "known_source_candidates": 1,
                    "sources_unchecked": 0,
                    "requested_search_pages": 1,
                    "recorded_search_pages": [],
                },
                "sources": [
                    {
                        "source_url": "https://evil.test/@SUM",
                        "final_url": "https://evil.test/@SUM",
                        "publisher_group": "evil.test",
                        "verification": "link_observed",
                        "observed_link": False,
                        "observed_mention": True,
                        "quality_estimate": 25.0,
                        "supported_quality_points": 25.0,
                        "quality_range": [25.0, 50.0],
                        "assessed_weight_percent": 25.0,
                        "relationship": "@FORMULA",
                        "context": "+DANGER",
                        "relevance": "-LOW",
                        "representation": "http",
                        "access_error": "=ERROR()",
                        "target_links": [],
                        "brand_mentions": [{"name": "=CALC()", "excerpt": "@EVIL"}],
                    }
                ],
                "limitations": [],
            }

            export_assessment(assessment_data, out)

            # Check reputation-sources.csv
            sources_csv = out / "reputation-sources.csv"
            self.assertTrue(sources_csv.exists())
            sources_content = sources_csv.read_text(encoding="utf-8-sig")
            self.assertIn("'@FORMULA", sources_content)
            self.assertIn("'+DANGER", sources_content)
            self.assertIn("'-LOW", sources_content)
            self.assertIn("'=ERROR()", sources_content)

            # Check reputation-opportunities.csv
            opps_csv = out / "reputation-opportunities.csv"
            self.assertTrue(opps_csv.exists())
            opps_content = opps_csv.read_text(encoding="utf-8-sig")
            self.assertFalse("=CALC()" in opps_content and not "'=CALC()" in opps_content)

    def test_reputation_comparison_csv_neutralizes_injection(self):
        """Check that reputation_comparison.csv neutralizes formula injection in diffs."""
        before = {
            "target": TARGET,
            "brand": "Example",
            "score": 30.0,
            "sources": [],
        }
        after = {
            "target": TARGET,
            "brand": "Example",
            "score": 40.0,
            "sources": [
                {
                    "source_url": "https://pub.test/",
                    "target_links": [
                        {
                            "url": f"{TARGET}/",
                            "anchor": "=1+2",
                            "rel": ["+danger"],
                            "is_dofollow": True,
                        }
                    ],
                    "brand_mentions": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            compare_reputation_snapshots(before, after, out_dir=tmp_dir)
            csv_file = Path(tmp_dir) / "reputation_comparison.csv"
            self.assertTrue(csv_file.exists())
            content = csv_file.read_text(encoding="utf-8-sig")
            self.assertIn("'=1+2", content)

    def test_windows_sqlite_no_file_lock(self):
        """Verify that SQLite connection cleanup on Windows allows immediate directory removal."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "lock_test.sqlite3"
            init_backlink_db(db_path)
            persist_backlink_verification(db_path, {"target": TARGET, "results": []})
            persist_reputation_assessment(db_path, {"target": TARGET, "score": 50})
            persist_reputation_diff(db_path, {"diff_id": "test", "before_score": 10, "after_score": 20})
        # If any connection was leaked on Windows, TemporaryDirectory cleanup raises PermissionError (WinError 32).
        # Reaching here means clean exit!
        self.assertTrue(True)

    def test_pathological_anchor_text_and_unicode(self):
        """Verify handling of 50,000-char anchor text and mixed Unicode/emojis."""
        huge_anchor = "🚀" * 1000 + "A" * 50000
        data = {
            "text": "Link " + huge_anchor + " end",
            "links": [
                {
                    "url": f"{TARGET}/unicode",
                    "anchor": huge_anchor,
                    "rel": ["nofollow"],
                }
            ],
        }
        links = target_links(data, "example.com")
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["url"], f"{TARGET}/unicode")
        self.assertTrue(links[0]["anchor"].startswith("🚀"))

    def test_empty_or_zero_evidence_bounds(self):
        """Verify that zero-evidence inputs cleanly withhold scores without crashing."""
        result = assess({"target": TARGET, "brand": "Example", "results": []})
        self.assertIsNone(result["score"])
        self.assertEqual(result["score_status"], "withheld")
        self.assertEqual(result["confidence"], "insufficient conclusive evidence")


if __name__ == "__main__":
    unittest.main()
