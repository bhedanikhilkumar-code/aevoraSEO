"""
CLI tests for Backlinks, Reputation, and Reputation-Compare commands.
Validates positional arguments, output formats, auto-defaults, and error handling.
"""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from aevoraseo.cli import main

TARGET = "https://example.com/"


class BacklinksCLITests(unittest.TestCase):
    def test_backlinks_cli_positional_and_formats(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "bl_out"
            verified = {
                "source_url": "https://pub.test/",
                "final_url": "https://pub.test/",
                "verification": "link_observed",
                "representation": "http",
                "status": 200,
                "error": "",
                "target_links": [
                    {
                        "url": f"{TARGET}/",
                        "anchor": "Example Link",
                        "rel": [],
                        "is_dofollow": True,
                        "context": "Context for Example Link",
                    }
                ],
                "brand_mentions": [{"name": "Example", "excerpt": "Example mention"}],
                "evidence_folder": "sources/dummy",
                "attempt_history": [],
            }

            with patch("aevoraseo.backlinks.verify_source", return_value=verified):
                # Run terminal format
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["backlinks", TARGET, "--out", str(out_dir), "--format", "terminal"])
                self.assertEqual(code, 0)
                output = stdout.getvalue()
                self.assertIn("AevoraSEO Backlink Verification", output)
                self.assertIn("Verified Backlink Pages", output)

                # Run JSON format
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["backlinks", TARGET, "--out", str(Path(tmp_dir) / "bl_json"), "--format", "json"])
                self.assertEqual(code, 0)
                parsed = json.loads(stdout.getvalue())
                self.assertEqual(parsed["target"], TARGET)

                # Run CSV format
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["backlinks", TARGET, "--out", str(Path(tmp_dir) / "bl_csv"), "--format", "csv"])
                self.assertEqual(code, 0)
                self.assertIn("source_url", stdout.getvalue())

    def test_reputation_cli_positional_and_formats(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "rep_out"
            verified = {
                "target": TARGET,
                "brand": "Example",
                "checked_at": "2026-09-22T00:00:00Z",
                "sources_supplied": 1,
                "sources_checked": 1,
                "sources_remaining": 0,
                "observed_link_pages": 1,
                "observed_mention_pages": 1,
                "unverified_pages": 0,
                "results": [
                    {
                        "source_url": "https://pub.test/",
                        "final_url": "https://pub.test/",
                        "verification": "link_observed",
                        "target_links": [{"url": f"{TARGET}/", "rel": ["nofollow"]}],
                        "brand_mentions": [{"name": "Example", "excerpt": "Example is here"}],
                        "mention_status": "observed_in_page",
                        "representation": "http",
                        "discovery": {},
                    }
                ],
            }
            with patch("aevoraseo.reputation.check_sources", return_value=verified):
                # Terminal format
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["reputation", "example.com", "--out", str(out_dir), "--format", "terminal"])
                self.assertEqual(code, 0)
                output = stdout.getvalue()
                self.assertIn("AevoraSEO Reputation Assessment", output)
                self.assertIn("Evidence-supported Score", output)

                # JSON format
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["reputation", "example.com", "--out", str(Path(tmp_dir) / "rep_json"), "--format", "json"])
                self.assertEqual(code, 0)
                parsed = json.loads(stdout.getvalue())
                self.assertIn("score", parsed)

    def test_compare_reputation_cli(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir)
            before_file = p / "before.json"
            after_file = p / "after.json"

            before_file.write_text(json.dumps({
                "target": TARGET,
                "brand": "Example",
                "score": 30.0,
                "sources": [],
            }))
            after_file.write_text(json.dumps({
                "target": TARGET,
                "brand": "Example",
                "score": 50.0,
                "sources": [
                    {
                        "source_url": "https://newlink.test/",
                        "target_links": [{"url": f"{TARGET}/", "rel": []}],
                        "brand_mentions": [],
                    }
                ],
            }))

            # Test compare-reputation
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main([
                    "compare-reputation",
                    "--before", str(before_file),
                    "--after", str(after_file),
                    "--out", str(p / "diff1"),
                    "--format", "terminal",
                ])
            self.assertEqual(code, 0)
            self.assertIn("AevoraSEO Reputation Snapshot Comparison", stdout.getvalue())
            self.assertIn("+20.0", stdout.getvalue())

            # Test reputation-compare
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main([
                    "reputation-compare",
                    "--before", str(before_file),
                    "--after", str(after_file),
                    "--out", str(p / "diff2"),
                    "--format", "json",
                ])
            self.assertEqual(code, 0)
            parsed = json.loads(stdout.getvalue())
            self.assertEqual(parsed["summary"]["score_delta"], 20.0)


if __name__ == "__main__":
    unittest.main()
