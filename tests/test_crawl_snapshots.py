import json
import re
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from aevoraseo.engine import Crawler, generate_snapshot_id
from aevoraseo.network import Config


class TestCrawlSnapshots(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_generate_snapshot_id_format(self):
        sid1 = generate_snapshot_id("https://example.com/blog")
        sid2 = generate_snapshot_id("https://example.com/blog")
        sid3 = generate_snapshot_id("https://different.org")

        pattern = r"^\d{8}T\d{6}Z_[a-f0-9]{6}$"
        self.assertRegex(sid1, pattern)
        self.assertRegex(sid3, pattern)

        # Same seed produces same trailing 6-char seed hash
        self.assertEqual(sid1.split("_")[1], sid2.split("_")[1])
        # Different seed produces different seed hash
        self.assertNotEqual(sid1.split("_")[1], sid3.split("_")[1])

    def test_snapshot_persistence_in_sqlite(self):
        out = self.tmp / "crawl_snap"
        config = Config.from_profile("quick", url="https://example.com", allow_private=True)
        crawler = Crawler(config, out)

        # Check snapshots table exists in crawl.sqlite3
        with sqlite3.connect(str(out / "crawl.sqlite3")) as db:
            tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            self.assertIn("snapshots", tables)

        from aevoraseo.extract import extract

        sample_page = {
            "url": "https://example.com",
            "final_url": "https://example.com",
            "status": 200,
            "headers": {"content-type": "text/html"},
            "data": extract(
                "<html><head><title>Home</title></head><body><h1>Hello</h1><p>Welcome</p></body></html>",
                "https://example.com",
            ),
            "error": "",
            "rendered": None,
            "body_sha256": "abc",
            "elapsed_ms": 10,
            "depth": 0,
            "http_events": [],
            "attempts": 1,
            "incremental_state": "added",
        }
        crawler.db.execute(
            "INSERT OR REPLACE INTO pages (url, payload) VALUES (?, ?)",
            ("https://example.com", json.dumps(sample_page)),
        )
        crawler.db.commit()

        summary = crawler.export()
        self.assertIn("snapshot_id", summary)
        self.assertEqual(summary["profile"], "quick")

        # Verify snapshots table row was written
        with sqlite3.connect(str(out / "crawl.sqlite3")) as db:
            row = db.execute("SELECT snapshot_id, profile, page_count FROM snapshots WHERE snapshot_id=?", (summary["snapshot_id"],)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], summary["snapshot_id"])
            self.assertEqual(row[1], "quick")
            self.assertEqual(row[2], 1)

        crawler.close()


if __name__ == "__main__":
    unittest.main()
