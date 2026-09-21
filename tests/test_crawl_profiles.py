import unittest
from pathlib import Path
from aevoraseo.network import Config, CRAWL_PROFILES
from aevoraseo.cli import parser


class TestCrawlProfiles(unittest.TestCase):
    def test_crawl_profile_definitions(self):
        self.assertIn("quick", CRAWL_PROFILES)
        self.assertIn("standard", CRAWL_PROFILES)
        self.assertIn("deep", CRAWL_PROFILES)

        quick = CRAWL_PROFILES["quick"]
        standard = CRAWL_PROFILES["standard"]
        deep = CRAWL_PROFILES["deep"]

        # Quick must be faster/lighter than standard
        self.assertLess(quick["max_pages"], standard["max_pages"])
        self.assertLess(quick["max_depth"], standard["max_depth"])
        self.assertEqual(quick["render_mode"], "http")

        # Deep must be broader/thorough than standard
        self.assertGreater(deep["max_pages"], standard["max_pages"])
        self.assertGreater(deep["max_depth"], standard["max_depth"])
        self.assertEqual(deep["render_mode"], "auto")

    def test_config_from_profile_factory(self):
        cfg_quick = Config.from_profile("quick", url="https://example.com")
        self.assertEqual(cfg_quick.profile, "quick")
        self.assertEqual(cfg_quick.max_pages, 25)
        self.assertEqual(cfg_quick.max_depth, 3)
        self.assertEqual(cfg_quick.render_mode, "http")

        cfg_deep = Config.from_profile("deep", url="https://example.com")
        self.assertEqual(cfg_deep.profile, "deep")
        self.assertEqual(cfg_deep.max_pages, 500)
        self.assertEqual(cfg_deep.max_depth, 12)
        self.assertEqual(cfg_deep.render_mode, "auto")

        # Custom overrides must be honored
        cfg_custom = Config.from_profile("quick", url="https://example.com", max_pages=15, render_mode="browser")
        self.assertEqual(cfg_custom.profile, "quick")
        self.assertEqual(cfg_custom.max_pages, 15)
        self.assertEqual(cfg_custom.render_mode, "browser")

    def test_invalid_profile_raises(self):
        with self.assertRaises(ValueError):
            Config.from_profile("ultra_turbo", url="https://example.com")

    def test_cli_profile_parsing(self):
        p = parser()
        args = p.parse_args(["crawl", "https://example.com", "--out", "./tmp", "--profile", "quick"])
        self.assertEqual(args.profile, "quick")
        self.assertIsNone(args.max_pages)

        # Explicit CLI overrides
        args_override = p.parse_args(["crawl", "https://example.com", "--out", "./tmp", "--profile", "deep", "--max-pages", "100"])
        self.assertEqual(args_override.profile, "deep")
        self.assertEqual(args_override.max_pages, 100)


if __name__ == "__main__":
    unittest.main()
