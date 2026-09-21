import csv
import http.server
import json
import shutil
import socketserver
import tempfile
import threading
import unittest
from pathlib import Path

from aevoraseo.engine import Crawler
from aevoraseo.network import Config
from aevoraseo.review import compare


class FixtureHandler(http.server.BaseHTTPRequestHandler):
    pages = {}
    etags = {}

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        path = self.path
        if path not in self.pages:
            self.send_response(404)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>404 Not Found</h1></body></html>")
            return

        status, body_str = self.pages[path]
        body_bytes = body_str.encode("utf-8")
        etag = self.etags.get(path, f'"{hash(body_bytes)}"')

        if self.headers.get("If-None-Match") == etag:
            self.send_response(304)
            self.send_header("etag", etag)
            self.end_headers()
            return

        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("etag", etag)
        self.send_header("content-length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)


class TestE2EFixtureDiff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FixtureHandler.pages = {
            "/": (
                200,
                "<html><head><title>Home Page</title></head><body><h1>Home</h1>"
                "<a href='/about'>About</a> <a href='/products'>Products</a> <a href='/old-page'>Old</a>"
                "</body></html>",
            ),
            "/about": (
                200,
                "<html><head><title>About Us</title></head><body><h1>About Us</h1>"
                "<p>Original company background.</p></body></html>",
            ),
            "/products": (
                200,
                "<html><head><title>Products</title></head><body><h1>Products</h1>"
                "<p>Original product catalog.</p></body></html>",
            ),
            "/old-page": (
                200,
                "<html><head><title>Old Page</title></head><body><h1>Legacy</h1>"
                "<p>This page will be removed in snapshot B.</p></body></html>",
            ),
        }
        FixtureHandler.etags = {
            "/": '"home-v1"',
            "/about": '"about-v1"',
            "/products": '"products-v1"',
            "/old-page": '"old-v1"',
        }
        cls.server = socketserver.TCPServer(("127.0.0.1", 0), FixtureHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_e2e_snapshot_diff_workflow(self):
        base_url = f"http://127.0.0.1:{self.port}"

        # === Phase 1: Snapshot A Crawl ===
        snap_a_dir = self.tmp / "snapshot_a"
        cfg_a = Config.from_profile(
            "quick",
            url=f"{base_url}/",
            allow_private=True,
            sitemaps=False,
            max_pages=20,
        )
        crawler_a = Crawler(cfg_a, snap_a_dir)
        summary_a = crawler_a.run()
        crawler_a.close()

        pages_a = {
            json.loads(line)["url"]
            for line in (snap_a_dir / "pages.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        self.assertIn(f"{base_url}/", pages_a)
        self.assertIn(f"{base_url}/about", pages_a)
        self.assertIn(f"{base_url}/products", pages_a)
        self.assertIn(f"{base_url}/old-page", pages_a)

        # === Phase 2: Modify Fixture Website ===
        # - Home links to /new-page instead of /old-page (same home content otherwise)
        # - /about: title changed
        # - /products: content changed
        # - /old-page: removed (404)
        # - /new-page: added
        FixtureHandler.pages = {
            "/": (
                200,
                "<html><head><title>Home Page</title></head><body><h1>Home</h1>"
                "<a href='/about'>About</a> <a href='/products'>Products</a> <a href='/new-page'>New</a>"
                "</body></html>",
            ),
            "/about": (
                200,
                "<html><head><title>About Us - Revised &amp; Updated</title></head><body><h1>About Us</h1>"
                "<p>Original company background.</p></body></html>",
            ),
            "/products": (
                200,
                "<html><head><title>Products</title></head><body><h1>Products</h1>"
                "<p>Completely redesigned product catalog featuring New Products 2026.</p></body></html>",
            ),
            "/new-page": (
                200,
                "<html><head><title>Brand New Page</title></head><body><h1>New</h1>"
                "<p>Brand new page content.</p></body></html>",
            ),
        }
        FixtureHandler.etags = {
            "/": '"home-v2"',
            "/about": '"about-v2"',
            "/products": '"products-v2"',
            "/new-page": '"new-v1"',
        }

        # === Phase 3: Snapshot B Incremental Crawl ===
        snap_b_dir = self.tmp / "snapshot_b"
        cfg_b = Config.from_profile(
            "quick",
            url=f"{base_url}/",
            allow_private=True,
            sitemaps=False,
            max_pages=20,
        )
        crawler_b = Crawler(cfg_b, snap_b_dir, incremental_from=snap_a_dir)
        summary_b = crawler_b.run()
        crawler_b.close()

        self.assertGreaterEqual(summary_b["html_documents"], 4)

        # === Phase 4: Snapshot Diff Comparison ===
        diff_out = self.tmp / "diff_results"
        diff = compare(snap_a_dir, snap_b_dir, diff_out)

        # Verify Added, Removed, Changed, Unchanged
        self.assertIn(f"{base_url}/new-page", diff["added_urls"])
        self.assertIn(f"{base_url}/old-page", diff["removed_urls"])
        changed_urls = {row["url"] for row in diff["changed_pages"]}
        self.assertIn(f"{base_url}/about", changed_urls)
        self.assertIn(f"{base_url}/products", changed_urls)

        # Verify summary counts
        self.assertGreaterEqual(diff["summary"]["added"], 1)
        self.assertGreaterEqual(diff["summary"]["removed"], 1)
        self.assertGreaterEqual(diff["summary"]["changed"], 2)

        # Verify comparison.csv
        csv_file = diff_out / "comparison.csv"
        self.assertTrue(csv_file.exists())
        with csv_file.open(encoding="utf-8-sig") as f:
            reader = list(csv.DictReader(f))
            states = {r["url"]: r["state"] for r in reader}
            self.assertEqual(states.get(f"{base_url}/new-page"), "ADDED")
            self.assertEqual(states.get(f"{base_url}/old-page"), "REMOVED")
            self.assertEqual(states.get(f"{base_url}/about"), "CHANGED")
            self.assertEqual(states.get(f"{base_url}/products"), "CHANGED")

        # Verify comparison.md
        md_file = diff_out / "comparison.md"
        self.assertTrue(md_file.exists())
        md_text = md_file.read_text(encoding="utf-8")
        self.assertIn("Added:", md_text)
        self.assertIn("Removed:", md_text)
        self.assertIn("Changed:", md_text)

        # Verify determinism: repeating comparison yields identical results
        diff_repeat = compare(snap_a_dir, snap_b_dir, diff_out)
        self.assertEqual(diff["summary"], diff_repeat["summary"])
        self.assertEqual(diff["added_urls"], diff_repeat["added_urls"])
        self.assertEqual(diff["removed_urls"], diff_repeat["removed_urls"])


if __name__ == "__main__":
    unittest.main()
