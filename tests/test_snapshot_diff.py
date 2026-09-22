import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aevoraseo.review import compare, normalize_text_for_diff


def make_snapshot(path: Path, seed: str, snapshot_id: str, pages: list[dict]):
    path.mkdir(parents=True, exist_ok=True)
    summary = {
        "seed": seed,
        "snapshot_id": snapshot_id,
        "exported_at": "2026-09-22T01:00:00Z",
        "html_documents": len(pages),
        "total_requests": len(pages),
        "coverage_limited": False,
        "configuration": {},
    }
    (path / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    with (path / "pages.jsonl").open("w", encoding="utf-8") as f:
        for p in pages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    (path / "issues.json").write_text("[]", encoding="utf-8")


class TestSnapshotDiff(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_normalize_text_for_diff(self):
        self.assertEqual(normalize_text_for_diff("  Hello   \n\t World  "), "Hello World")
        self.assertEqual(normalize_text_for_diff(None), "")
        self.assertEqual(normalize_text_for_diff(""), "")

    def test_identical_snapshots(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff"

        page = {
            "url": "https://example.com/",
            "status": 200,
            "data": {
                "title": "Title",
                "meta_description": "Desc",
                "headings": {"h1": ["Heading"]},
                "main_text": "Text",
                "content_sha256": "abc123",
                "word_count": 1,
            },
        }

        make_snapshot(snap_a, "https://example.com/", "20260922T010000Z_111111", [page])
        make_snapshot(snap_b, "https://example.com/", "20260922T020000Z_111111", [page])

        result = compare(snap_a, snap_b, diff_out)
        self.assertEqual(result["summary"]["added"], 0)
        self.assertEqual(result["summary"]["removed"], 0)
        self.assertEqual(result["summary"]["changed"], 0)
        self.assertEqual(result["summary"]["unchanged"], 1)
        self.assertIn("https://example.com/", result["unchanged_urls"])

        # Check comparison.csv was created
        self.assertTrue((diff_out / "comparison.csv").exists())
        self.assertTrue((diff_out / "comparison.json").exists())
        self.assertTrue((diff_out / "comparison.md").exists())

    def test_added_and_removed_urls(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff"

        p_home = {
            "url": "https://example.com/",
            "status": 200,
            "data": {"title": "Home", "content_sha256": "hash1"},
        }
        p_old = {
            "url": "https://example.com/old",
            "status": 200,
            "data": {"title": "Old", "content_sha256": "hash2"},
        }
        p_new = {
            "url": "https://example.com/new",
            "status": 200,
            "data": {"title": "New", "content_sha256": "hash3"},
        }

        make_snapshot(snap_a, "https://example.com/", "snap1", [p_home, p_old])
        make_snapshot(snap_b, "https://example.com/", "snap2", [p_home, p_new])

        result = compare(snap_a, snap_b, diff_out)
        self.assertEqual(result["summary"]["added"], 1)
        self.assertEqual(result["summary"]["removed"], 1)
        self.assertEqual(result["summary"]["unchanged"], 1)
        self.assertEqual(result["added_urls"], ["https://example.com/new"])
        self.assertEqual(result["removed_urls"], ["https://example.com/old"])
        self.assertEqual(result["unchanged_urls"], ["https://example.com/"])

    def test_changed_url_detection(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff"

        p_a = {
            "url": "https://example.com/page",
            "status": 200,
            "data": {
                "title": "Old Title",
                "meta_description": "Old Desc",
                "headings": {"h1": ["Old H1"]},
                "main_text": "Original text content",
                "canonical": [{"url": "https://example.com/page"}],
            },
        }
        p_b = {
            "url": "https://example.com/page",
            "status": 200,
            "data": {
                "title": "New Title",
                "meta_description": "New Desc",
                "headings": {"h1": ["New H1"]},
                "main_text": "Updated text content here",
                "canonical": [{"url": "https://example.com/canonical-target"}],
            },
        }

        make_snapshot(snap_a, "https://example.com/", "snap1", [p_a])
        make_snapshot(snap_b, "https://example.com/", "snap2", [p_b])

        result = compare(snap_a, snap_b, diff_out)
        self.assertEqual(result["summary"]["changed"], 1)
        self.assertEqual(len(result["changed_pages"]), 1)
        fields = result["changed_pages"][0]["fields"]
        self.assertIn("title", fields)
        self.assertIn("description", fields)
        self.assertIn("h1", fields)
        self.assertIn("content_hash", fields)
        self.assertIn("canonical", fields)

    def test_url_filter(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff"

        p1 = {"url": "https://example.com/blog/1", "status": 200, "data": {"title": "Blog 1"}}
        p2 = {"url": "https://example.com/products/1", "status": 200, "data": {"title": "Prod 1"}}

        make_snapshot(snap_a, "https://example.com/", "snap1", [p1, p2])
        make_snapshot(snap_b, "https://example.com/", "snap2", [p1, p2])

        result = compare(snap_a, snap_b, diff_out, url_filter=r"/products")
        self.assertEqual(result["summary"]["unchanged"], 1)
        self.assertEqual(result["unchanged_urls"], ["https://example.com/products/1"])

    def test_status_filter_csv_and_result(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff_status"

        p_home = {"url": "https://example.com/", "status": 200, "data": {"title": "Home", "content_sha256": "h1"}}
        p_old = {"url": "https://example.com/old", "status": 200, "data": {"title": "Old", "content_sha256": "h2"}}
        p_new = {"url": "https://example.com/new", "status": 200, "data": {"title": "New", "content_sha256": "h3"}}
        make_snapshot(snap_a, "https://example.com/", "snap1", [p_home, p_old])
        make_snapshot(snap_b, "https://example.com/", "snap2", [p_home, p_new])

        # Filter by added
        res_added = compare(snap_a, snap_b, diff_out / "added", status_filter="added")
        self.assertEqual(res_added["filtered_urls"], ["https://example.com/new"])
        with (diff_out / "added" / "comparison.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["state"], "ADDED")
            self.assertEqual(rows[0]["url"], "https://example.com/new")

        # Filter by removed
        res_removed = compare(snap_a, snap_b, diff_out / "removed", status_filter="removed")
        self.assertEqual(res_removed["filtered_urls"], ["https://example.com/old"])
        with (diff_out / "removed" / "comparison.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["state"], "REMOVED")
            self.assertEqual(rows[0]["url"], "https://example.com/old")

    def test_invalid_url_filter_regex_raises_value_error(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff_regex"
        p1 = {"url": "https://example.com/", "status": 200, "data": {"title": "Home"}}
        make_snapshot(snap_a, "https://example.com/", "snap1", [p1])
        make_snapshot(snap_b, "https://example.com/", "snap2", [p1])

        with self.assertRaises(ValueError) as ctx:
            compare(snap_a, snap_b, diff_out, url_filter="[invalid")
        self.assertIn("Invalid URL filter regular expression", str(ctx.exception))

    def test_invalid_status_filter_raises_value_error(self):
        snap_a = self.tmp / "snap_a"
        snap_b = self.tmp / "snap_b"
        diff_out = self.tmp / "diff_sf"
        p1 = {"url": "https://example.com/", "status": 200, "data": {"title": "Home"}}
        make_snapshot(snap_a, "https://example.com/", "snap1", [p1])
        make_snapshot(snap_b, "https://example.com/", "snap2", [p1])

        with self.assertRaises(ValueError) as ctx:
            compare(snap_a, snap_b, diff_out, status_filter="unknown_state")
        self.assertIn("Invalid status filter", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

