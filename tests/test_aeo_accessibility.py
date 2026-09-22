"""Tests for AevoraSEO AI bot accessibility evaluation."""

import unittest

from aevoraseo.aeo.accessibility import evaluate_bot_accessibility


class TestAEOAccessibility(unittest.TestCase):
    def test_robots_txt_bot_restrictions(self):
        robots_txt = """
        User-agent: *
        Allow: /

        User-agent: GPTBot
        Disallow: /private/
        Disallow: /data/

        User-agent: ClaudeBot
        Disallow: /
        """
        # Test public page
        public_signals = evaluate_bot_accessibility("https://example.com/blog/post-1", robots_text=robots_txt)
        statuses = {s.bot_name: s.status for s in public_signals}
        self.assertEqual(statuses.get("GPTBot"), "crawl_allowed")
        self.assertEqual(statuses.get("ClaudeBot"), "crawl_restricted")
        self.assertEqual(statuses.get("PerplexityBot"), "crawl_allowed")

        # Test restricted page for GPTBot
        private_signals = evaluate_bot_accessibility("https://example.com/private/doc", robots_text=robots_txt)
        priv_statuses = {s.bot_name: s.status for s in private_signals}
        self.assertEqual(priv_statuses.get("GPTBot"), "crawl_restricted")
        self.assertEqual(priv_statuses.get("ClaudeBot"), "crawl_restricted")
        self.assertEqual(priv_statuses.get("PerplexityBot"), "crawl_allowed")

    def test_meta_robots_noai_directive(self):
        meta_directives = {"robots": ["noai", "noindex"]}
        signals = evaluate_bot_accessibility(
            "https://example.com/page",
            robots_text="User-agent: *\nAllow: /",
            meta_directives=meta_directives,
        )
        for s in signals:
            self.assertEqual(s.status, "crawl_restricted")
            self.assertEqual(s.policy_source, "meta:robots")

    def test_x_robots_tag_header(self):
        headers = {"x-robots-tag": "noindex, nofollow"}
        signals = evaluate_bot_accessibility(
            "https://example.com/page",
            robots_text="User-agent: *\nAllow: /",
            headers=headers,
        )
        for s in signals:
            self.assertEqual(s.status, "crawl_restricted")
            self.assertEqual(s.policy_source, "x-robots-tag")


if __name__ == "__main__":
    unittest.main()
