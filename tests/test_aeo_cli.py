"""Tests for AevoraSEO CLI aeo and aeo-compare subcommands."""

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from aevoraseo.cli import main


def make_cli_test_snapshot(folder: Path, snap_id: str):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "summary.json").write_text(
        json.dumps({
            "snapshot_id": snap_id,
            "url": "https://example.com/",
            "timestamp": "2026-09-22T10:00:00Z",
            "page_count": 1,
        }),
        encoding="utf-8",
    )
    (folder / "robots.json").write_text(
        json.dumps({"text": "User-agent: *\nAllow: /\n"}),
        encoding="utf-8",
    )
    page = {
        "url": "https://example.com/guide",
        "status": 200,
        "data": {
            "title": "AEO Complete Guide",
            "headings": {"h1": ["AEO Complete Guide"], "h2": ["What is Answer Engine Optimization?"]},
            "main_text": "Answer Engine Optimization is the discipline of structuring content for AI engines.",
            "word_count": 400,
            "jsonld": [
                {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": "AEO Complete Guide",
                    "author": {"@type": "Person", "name": "Bheda Nikhilkumar"},
                    "datePublished": "2026-01-01",
                }
            ],
            "meta": {"author": ["Bheda Nikhilkumar"]},
            "canonical": [{"url": "https://example.com/guide"}],
        },
        "html": "<h1>AEO Complete Guide</h1><h2>What is Answer Engine Optimization?</h2><p>Answer Engine Optimization is the discipline of structuring content for AI engines.</p>",
    }
    (folder / "pages.jsonl").write_text(json.dumps(page) + "\n", encoding="utf-8")


class TestAEOCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_aeo_cli_terminal_and_json_and_markdown(self):
        snap = self.tmp / "snap_1"
        out_dir = self.tmp / "aeo_out"
        make_cli_test_snapshot(snap, "snap_1")

        # 1. Terminal format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["aeo", str(snap), "--out", str(out_dir), "--format", "terminal"])
        self.assertEqual(ret, 0)
        out = buf.getvalue()
        self.assertIn("AevoraSEO AEO Intelligence Engine", out)
        self.assertIn("AevoraSEO AEO Readiness Score", out)
        self.assertIn("AI Crawler Accessibility", out)

        # Verify exported files exist
        self.assertTrue((out_dir / "aeo_report.json").exists())
        self.assertTrue((out_dir / "aeo_summary.md").exists())
        self.assertTrue((out_dir / "aeo_pages.csv").exists())

        # 2. JSON format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["aeo", str(snap), "--format", "json"])
        self.assertEqual(ret, 0)
        parsed = json.loads(buf.getvalue())
        self.assertEqual(parsed["snapshot_id"], "snap_1")
        self.assertIn("average_aeo_readiness_score", parsed)

        # 3. Markdown format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["aeo", str(snap), "--format", "markdown"])
        self.assertEqual(ret, 0)
        md_out = buf.getvalue()
        self.assertIn("# AevoraSEO AEO / GEO Intelligence Report", md_out)

        # 4. CSV format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["aeo", str(snap), "--out", str(out_dir), "--format", "csv"])
        self.assertEqual(ret, 0)
        csv_out = buf.getvalue()
        self.assertIn("url,aeo_readiness_score,geo_signal_score", csv_out)

    def test_aeo_compare_cli(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff_out"
        make_cli_test_snapshot(snap_a, "snap_a")
        make_cli_test_snapshot(snap_b, "snap_b")

        # Terminal format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main([
                "aeo-compare",
                "--before", str(snap_a),
                "--after", str(snap_b),
                "--out", str(diff_out),
                "--format", "terminal",
            ])
        self.assertEqual(ret, 0)
        out = buf.getvalue()
        self.assertIn("AevoraSEO AEO / GEO Snapshot Comparison", out)
        self.assertIn("Before: snap_a", out)
        self.assertIn("After:  snap_b", out)

        # JSON format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main([
                "aeo-compare",
                "--before", str(snap_a),
                "--after", str(snap_b),
                "--format", "json",
            ])
        self.assertEqual(ret, 0)
        parsed = json.loads(buf.getvalue())
        self.assertEqual(parsed["before_snapshot_id"], "snap_a")
        self.assertEqual(parsed["after_snapshot_id"], "snap_b")


if __name__ == "__main__":
    unittest.main()
