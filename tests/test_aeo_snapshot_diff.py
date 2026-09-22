"""Tests for AevoraSEO AEO snapshot comparison and diff intelligence."""

import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aevoraseo.aeo.comparison import compare_aeo_snapshots


def make_test_snapshot(folder: Path, snap_id: str, pages: list, robots_text: str = "User-agent: *\nAllow: /"):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "summary.json").write_text(
        json.dumps({
            "snapshot_id": snap_id,
            "url": "https://example.com/",
            "timestamp": "2026-09-22T10:00:00Z",
            "page_count": len(pages),
        }),
        encoding="utf-8",
    )
    (folder / "robots.json").write_text(
        json.dumps({"text": robots_text}),
        encoding="utf-8",
    )
    lines = [json.dumps(p) for p in pages]
    (folder / "pages.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


class TestAEOSnapshotDiff(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_snapshot_comparison_improved_and_added(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff_out"

        # Baseline: Page with question heading but no answer, no schema, no author
        p1_before = {
            "url": "https://example.com/guide",
            "status": 200,
            "data": {
                "title": "AEO Guide",
                "headings": {"h1": ["AEO Guide"], "h2": ["What is Answer Engine Optimization?"]},
                "main_text": "Random background information without definition.",
                "word_count": 100,
                "jsonld": [],
                "canonical": [{"url": "https://example.com/guide"}],
            },
            "html": "<h1>AEO Guide</h1><h2>What is Answer Engine Optimization?</h2><p>Random background info.</p>",
        }

        # Subsequent: Added direct definition answer, FAQPage schema, author byline
        p1_after = {
            "url": "https://example.com/guide",
            "status": 200,
            "data": {
                "title": "AEO Guide",
                "headings": {"h1": ["AEO Guide"], "h2": ["What is Answer Engine Optimization?"]},
                "main_text": "Answer Engine Optimization is a methodology that structures content for generative answer engines.",
                "word_count": 350,
                "jsonld": [
                    {
                        "@context": "https://schema.org",
                        "@type": "FAQPage",
                        "mainEntity": [
                            {
                                "@type": "Question",
                                "name": "What is Answer Engine Optimization?",
                                "acceptedAnswer": {
                                    "@type": "Answer",
                                    "text": "AEO is a methodology for generative answer engines.",
                                },
                            }
                        ],
                    }
                ],
                "meta": {"author": ["Dr. Jane Smith"]},
                "canonical": [{"url": "https://example.com/guide"}],
            },
            "html": (
                "<h1>AEO Guide</h1>"
                "<h2>What is Answer Engine Optimization?</h2>"
                "<p>Answer Engine Optimization is a methodology that structures content for generative answer engines.</p>"
            ),
        }

        # Page 2: Newly added in snap_b
        p2_new = {
            "url": "https://example.com/faq",
            "status": 200,
            "data": {
                "title": "FAQ Page",
                "headings": {"h1": ["Frequently Asked Questions"]},
                "main_text": "Here are our questions.",
                "word_count": 200,
                "jsonld": [],
            },
            "html": "<h1>Frequently Asked Questions</h1>",
        }

        make_test_snapshot(snap_a, "snap_1", [p1_before])
        make_test_snapshot(snap_b, "snap_2", [p1_after, p2_new])

        diff = compare_aeo_snapshots(snap_a, snap_b, out_dir=diff_out)

        self.assertEqual(diff.summary["improved"], 1)
        self.assertEqual(diff.summary["added"], 1)
        self.assertEqual(diff.page_transitions["https://example.com/guide"], "IMPROVED")
        self.assertEqual(diff.page_transitions["https://example.com/faq"], "ADDED")

        # Verify exported files
        self.assertTrue((diff_out / "aeo_comparison.json").exists())
        self.assertTrue((diff_out / "aeo_comparison.md").exists())
        self.assertTrue((diff_out / "aeo_comparison.csv").exists())

        # Inspect CSV content
        with (diff_out / "aeo_comparison.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
            self.assertGreaterEqual(len(rows), 2)
            states = {r["url"]: r["state"] for r in rows}
            self.assertEqual(states.get("https://example.com/guide"), "IMPROVED")
            self.assertEqual(states.get("https://example.com/faq"), "ADDED")


if __name__ == "__main__":
    unittest.main()
