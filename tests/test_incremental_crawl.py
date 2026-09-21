import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aevoraseo.engine import Crawler
from aevoraseo.network import Config, Response


class TestIncrementalCrawl(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_incremental_cache(self):
        prev_dir = self.tmp / "prev_crawl"
        prev_dir.mkdir()
        pages = [
            {
                "url": "https://example.com/",
                "status": 200,
                "headers": {"etag": '"v1"', "last-modified": "Wed, 21 Oct 2025 07:28:00 GMT"},
                "content_type": "text/html",
                "html": "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>",
                "data": {"title": "Test", "content_sha256": "abc"},
                "body_sha256": "abc",
            }
        ]
        with (prev_dir / "pages.jsonl").open("w", encoding="utf-8") as f:
            for p in pages:
                f.write(json.dumps(p) + "\n")

        config = Config.from_profile("quick", url="https://example.com", allow_private=True)
        crawler = Crawler(config, self.tmp / "new_crawl", incremental_from=prev_dir)

        self.assertIn("https://example.com/", crawler.previous_cache)
        cached = crawler.previous_cache["https://example.com/"]
        self.assertEqual(cached["etag"], '"v1"')
        self.assertEqual(cached["last_modified"], "Wed, 21 Oct 2025 07:28:00 GMT")
        crawler.close()

    def test_fetch_page_304_reuses_previous_payload(self):
        prev_dir = self.tmp / "prev_crawl"
        prev_dir.mkdir()
        prev_page = {
            "url": "https://example.com/item",
            "status": 200,
            "headers": {"etag": '"etag-123"', "content-type": "text/html"},
            "content_type": "text/html",
            "data": {"title": "Old Item", "content_sha256": "hash_old"},
            "body_sha256": "hash_old",
        }
        with (prev_dir / "pages.jsonl").open("w", encoding="utf-8") as f:
            f.write(json.dumps(prev_page) + "\n")

        config = Config.from_profile("quick", url="https://example.com", allow_private=True)
        crawler = Crawler(config, self.tmp / "new_crawl", incremental_from=prev_dir)

        # Mock transport.fetch to return 304 when conditional headers are sent
        mock_resp = Response(
            url="https://example.com/item",
            final_url="https://example.com/item",
            status=304,
            headers={"etag": '"etag-123"'},
            redirects=[],
            error="",
            attempts=1,
            elapsed_ms=5,
            fetched_at="2026-09-22T01:00:00Z",
            body=b"",
            http_events=[],
            withheld_url=None,
        )

        with patch.object(crawler.transport, "fetch", return_value=mock_resp) as mock_fetch:
            result = crawler.fetch_page("https://example.com/item", depth=0)

            # Verify conditional header If-None-Match was passed
            call_kwargs = mock_fetch.call_args[1]
            self.assertEqual(call_kwargs["request_headers"].get("if-none-match"), '"etag-123"')

            # Result must reuse previous data and state is unchanged
            self.assertEqual(result["status"], 200)
            self.assertEqual(result["data"], prev_page["data"])
            self.assertEqual(result["incremental_state"], "unchanged")
            self.assertEqual(result["conditional_status"], 304)

        crawler.close()

    def test_fetch_page_200_tags_changed_or_added(self):
        prev_dir = self.tmp / "prev_crawl"
        prev_dir.mkdir()
        prev_page = {
            "url": "https://example.com/item",
            "status": 200,
            "headers": {"etag": '"etag-1"'},
            "content_type": "text/html",
            "data": {"title": "Old Content", "content_sha256": "hash_old"},
            "body_sha256": "hash_old",
        }
        with (prev_dir / "pages.jsonl").open("w", encoding="utf-8") as f:
            f.write(json.dumps(prev_page) + "\n")

        config = Config.from_profile("quick", url="https://example.com", allow_private=True)
        crawler = Crawler(config, self.tmp / "new_crawl", incremental_from=prev_dir)

        # Modified page returns 200 with new content
        new_resp = Response(
            url="https://example.com/item",
            final_url="https://example.com/item",
            status=200,
            headers={"etag": '"etag-2"', "content-type": "text/html"},
            redirects=[],
            error="",
            attempts=1,
            elapsed_ms=10,
            fetched_at="2026-09-22T01:00:00Z",
            body=b"<html><body>Updated Content</body></html>",
            http_events=[],
            withheld_url=None,
        )

        with patch.object(crawler.transport, "fetch", return_value=new_resp):
            result = crawler.fetch_page("https://example.com/item", depth=0)
            self.assertEqual(result["incremental_state"], "changed")

        # Brand new URL returns 200
        brand_new_resp = Response(
            url="https://example.com/brand-new",
            final_url="https://example.com/brand-new",
            status=200,
            headers={"content-type": "text/html"},
            redirects=[],
            error="",
            attempts=1,
            elapsed_ms=10,
            fetched_at="2026-09-22T01:00:00Z",
            body=b"<html><body>Brand new page</body></html>",
            http_events=[],
            withheld_url=None,
        )

        with patch.object(crawler.transport, "fetch", return_value=brand_new_resp):
            result_new = crawler.fetch_page("https://example.com/brand-new", depth=0)
            self.assertEqual(result_new["incremental_state"], "added")

        crawler.close()


if __name__ == "__main__":
    unittest.main()
