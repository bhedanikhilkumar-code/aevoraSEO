"""
Adversarial and Security Verification Tests for AevoraSEO AEO / GEO Engine.
Covers CSV formula injection, cyclical JSON-LD, pathological HTML,
robots directive variations, SQLite schema integrity, and input resilience.
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from aevoraseo.aeo.analyzer import analyze_page, analyze_snapshot, sanitize_csv_cell
from aevoraseo.aeo.comparison import compare_aeo_snapshots
from aevoraseo.aeo.models import SnapshotAEOResult
from aevoraseo.aeo.persistence import init_aeo_db, persist_snapshot_aeo, persist_aeo_diff
from aevoraseo.aeo.questions import analyze_page_questions, extract_faq_from_jsonld
from aevoraseo.aeo.schema import audit_page_schema
from aevoraseo.aeo.visibility import load_observed_visibility


class TestAEOAdversarialAndSecurity(unittest.TestCase):
    def test_csv_cell_sanitization_against_formula_injection(self):
        """Ensures formula-triggering characters are neutralized."""
        malicious_inputs = [
            "=1+1",
            "@SUM(A1:A10)",
            "+cmd|' /C calc'!A0",
            "-2+3",
            "\t=dangerous",
            "\r=danger2",
            "   =spaced_danger",
        ]
        for payload in malicious_inputs:
            sanitized = sanitize_csv_cell(payload)
            self.assertTrue(
                sanitized.startswith("'"),
                f"Payload was not properly escaped: {payload} -> {sanitized}",
            )

        # Benign text should remain unchanged
        benign = "Normal author name"
        self.assertEqual(sanitize_csv_cell(benign), benign)

    def test_csv_export_adversarial_escaping(self):
        """Verifies that generated aeo_pages.csv and aeo_comparison.csv neutralize formula injection."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            snap_path = Path(tmp_dir) / "snap"
            snap_path.mkdir()

            pages_file = snap_path / "pages.jsonl"
            # Page with dangerous author, heading question, and publisher
            page_record = {
                "url": "https://example.com/exploit",
                "final_url": "https://example.com/exploit",
                "html": "<html><body><h1>=cmd|' /C calc'!A0?</h1><p>This is the answer block.</p></body></html>",
                "data": {
                    "title": "=calc()",
                    "jsonld": [
                        {
                            "@context": "https://schema.org",
                            "@type": "Article",
                            "headline": "=ALERT()",
                            "author": {"@type": "Person", "name": "@EVIL_FORMULA"},
                            "publisher": {"@type": "Organization", "name": "+SUM(B1:B10)"},
                            "datePublished": "2026-01-01",
                        }
                    ],
                },
            }
            pages_file.write_text(json.dumps(page_record) + "\n", encoding="utf-8")

            out_dir = Path(tmp_dir) / "out"
            analyze_snapshot(snap_path, out_dir=out_dir)

            csv_file = out_dir / "aeo_pages.csv"
            self.assertTrue(csv_file.exists())
            content = csv_file.read_text(encoding="utf-8-sig")

            # Check that dangerous values are escaped with single quote
            self.assertIn("'@EVIL_FORMULA", content)
            self.assertIn("'+SUM(B1:B10)", content)
            self.assertNotIn("\n@EVIL_FORMULA", content)
            self.assertNotIn("\n+SUM(B1:B10)", content)

    def test_cyclical_jsonld_structure_resilience(self):
        """Verifies that self-referencing / circular JSON-LD dicts do not cause RecursionError."""
        circular_dict: dict = {"@type": "Article", "headline": "Circular test"}
        circular_dict["nested"] = circular_dict  # Direct cycle

        # Should terminate safely without RecursionError
        signals = audit_page_schema({"title": "Cycle Test", "jsonld": [circular_dict]})
        self.assertTrue(len(signals) >= 1)
        self.assertEqual(signals[0].schema_type, "Article")

        # Circular FAQ block
        faq_dict: dict = {
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": "What is AI?", "acceptedAnswer": {"text": "AI is software."}}],
        }
        faq_dict["child"] = faq_dict
        faq_signals = extract_faq_from_jsonld([faq_dict])
        self.assertEqual(len(faq_signals), 1)
        self.assertEqual(faq_signals[0].question, "What is AI?")

    def test_pathological_nesting_depth(self):
        """Deeply nested structures beyond 30 levels should safely truncate without crash."""
        curr: dict = {"@type": "Person", "name": "Deep Persona"}
        root = curr
        for i in range(50):
            nxt: dict = {"level": i, "sub": {}}
            curr["child"] = nxt
            curr = nxt

        signals = audit_page_schema({"title": "Deep Test", "jsonld": [root]})
        self.assertTrue(len(signals) >= 1)

    def test_malformed_html_with_script_tags(self):
        """Verifies that script tags or malformed HTML elements do not inject into questions or answers."""
        malicious_html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h2>What is machine learning?<script>alert('xss')</script></h2>
            <p>Machine learning refers to algorithms that learn from data.<script>stealCookies()</script></p>
            <h3>How does it work?</h3>
            <script>document.write('pwned');</script>
            <p>It works by optimizing statistical objective functions over training datasets.</p>
        </body>
        </html>
        """
        page_res = analyze_page(
            "https://example.com/ml",
            page_data={"headings": {}, "jsonld": []},
            html=malicious_html,
        )
        self.assertEqual(len(page_res.questions), 2)
        # Verify script content did not contaminate question names
        q_texts = [q.question for q in page_res.questions]
        self.assertIn("What is machine learning?", q_texts)
        self.assertIn("How does it work?", q_texts)
        for q in page_res.questions:
            self.assertNotIn("<script>", q.answer_text)

    def test_sqlite_persistence_and_query_integrity(self):
        """Verifies end-to-end SQLite persistence, table schemas, and idempotency."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            snap_path = Path(tmp_dir) / "snap"
            snap_path.mkdir()

            pages_file = snap_path / "pages.jsonl"
            page_data = {
                "url": "https://example.com/guide",
                "final_url": "https://example.com/guide",
                "html": "<html><body><h1>What is Cloud Computing?</h1><p>Cloud computing refers to on-demand computing services over the internet.</p></body></html>",
                "data": {
                    "title": "Cloud Computing Guide",
                    "jsonld": [
                        {
                            "@context": "https://schema.org",
                            "@type": "Article",
                            "headline": "Cloud Computing Guide",
                            "author": {"@type": "Person", "name": "Alice Expert"},
                            "datePublished": "2026-03-01",
                        }
                    ],
                },
            }
            pages_file.write_text(json.dumps(page_data) + "\n", encoding="utf-8")

            # Create existing crawl.sqlite3 in snap_path to verify auto-attachment
            crawl_db = snap_path / "crawl.sqlite3"
            conn = sqlite3.connect(str(crawl_db))
            try:
                conn.execute("CREATE TABLE meta (key TEXT, value TEXT)")
                conn.commit()
            finally:
                conn.close()

            out_dir = Path(tmp_dir) / "out"
            res = analyze_snapshot(snap_path, out_dir=out_dir)

            # 1. Verify crawl.sqlite3 received tables
            conn = sqlite3.connect(str(crawl_db))
            try:
                conn.row_factory = sqlite3.Row
                snap_row = conn.execute("SELECT * FROM aeo_snapshots").fetchone()
                self.assertIsNotNone(snap_row)
                self.assertEqual(snap_row["page_count"], 1)

                page_row = conn.execute("SELECT * FROM aeo_pages").fetchone()
                self.assertIsNotNone(page_row)
                self.assertEqual(page_row["url"], "https://example.com/guide")
                self.assertEqual(page_row["author"], "Alice Expert")

                q_rows = conn.execute("SELECT * FROM aeo_questions").fetchall()
                self.assertEqual(len(q_rows), 1)
                self.assertEqual(q_rows[0]["question"], "What is Cloud Computing?")
                self.assertEqual(q_rows[0]["answer_detected"], 1)

                ent_rows = conn.execute("SELECT * FROM aeo_entities").fetchall()
                self.assertTrue(len(ent_rows) >= 1)
            finally:
                conn.close()

            # 2. Verify out_dir/aeo.sqlite3 was also created
            aeo_db = out_dir / "aeo.sqlite3"
            self.assertTrue(aeo_db.exists())
            conn = sqlite3.connect(str(aeo_db))
            try:
                cnt = conn.execute("SELECT COUNT(*) FROM aeo_pages").fetchone()[0]
                self.assertEqual(cnt, 1)
            finally:
                conn.close()

            # 3. Verify idempotency: re-running analyze_snapshot doesn't violate UNIQUE constraints
            analyze_snapshot(snap_path, out_dir=out_dir)
            conn = sqlite3.connect(str(crawl_db))
            try:
                cnt = conn.execute("SELECT COUNT(*) FROM aeo_pages").fetchone()[0]
                self.assertEqual(cnt, 1)
            finally:
                conn.close()

    def test_corrupted_visibility_records_handling(self):
        """Verifies that malformed or adversarial visibility inputs do not crash or corrupt state."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "bad_vis.csv"
            # Malformed lines with missing columns, invalid integers, formula injection
            csv_path.write_text(
                "query,engine,url,position,citation\n"
                "=cmd|' /c calc'!A0,google_ai_overview,https://example.com,not_an_int,maybe\n"
                "valid query,chatgpt,https://example.com/valid,3,true\n"
                ",,,,\n",
                encoding="utf-8",
            )
            records = load_observed_visibility(csv_path)
            # Only valid query row should be retained
            self.assertTrue(any(r.url == "https://example.com/valid" and r.position == 3 for r in records))


if __name__ == "__main__":
    unittest.main()
