"""Tests for AevoraSEO empirical observed visibility ingestion and isolation."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aevoraseo.aeo.visibility import (
    load_observed_visibility,
    load_observed_visibility_from_csv,
    load_observed_visibility_from_json,
)


class TestAEOVisibility(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_visibility_from_json(self):
        json_file = self.tmp / "visibility.json"
        data = [
            {
                "query": "best aeo optimization platform",
                "engine": "google_ai_overview",
                "observed": True,
                "url": "https://example.com/aeo-guide",
                "position": 1,
                "citation": True,
                "source": "manual_audit",
                "observed_at": "2026-09-22T09:00:00Z",
                "evidence_snippet": "AevoraSEO was cited as primary reference.",
            }
        ]
        json_file.write_text(json.dumps(data), encoding="utf-8")

        records = load_observed_visibility(json_file)
        self.assertEqual(len(records), 1)
        rec = records[0]
        self.assertEqual(rec.query, "best aeo optimization platform")
        self.assertEqual(rec.engine, "google_ai_overview")
        self.assertTrue(rec.observed)
        self.assertTrue(rec.citation)
        self.assertEqual(rec.position, 1)

    def test_load_visibility_from_csv(self):
        csv_file = self.tmp / "visibility.csv"
        content = (
            "query,engine,observed,url,position,citation,source,observed_at,evidence_snippet\n"
            "what is generative engine optimization,perplexity,true,https://example.com/geo,2,true,serp_export,2026-09-22,Cited in answer\n"
        )
        csv_file.write_text(content, encoding="utf-8")

        records = load_observed_visibility(csv_file)
        self.assertEqual(len(records), 1)
        rec = records[0]
        self.assertEqual(rec.engine, "perplexity")
        self.assertEqual(rec.position, 2)
        self.assertTrue(rec.citation)


if __name__ == "__main__":
    unittest.main()
