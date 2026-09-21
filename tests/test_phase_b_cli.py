import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from aevoraseo.cli import main, parser
from aevoraseo.network import Config


class TestPhaseBCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_parser_profile_and_incremental_flags(self):
        p = parser()

        # Check default profile is standard
        args = p.parse_args(["crawl", "https://example.com", "--out", str(self.tmp)])
        self.assertEqual(args.profile, "standard")
        self.assertIsNone(args.incremental)

        # Check quick profile
        args = p.parse_args(["crawl", "https://example.com", "--out", str(self.tmp), "--profile", "quick"])
        self.assertEqual(args.profile, "quick")

        # Check incremental flag
        inc_path = self.tmp / "prev"
        args = p.parse_args(["crawl", "https://example.com", "--out", str(self.tmp), "--incremental", str(inc_path)])
        self.assertEqual(args.incremental, inc_path)

    def test_parser_compare_flags(self):
        p = parser()

        # Check compare options
        args = p.parse_args([
            "compare",
            "--before", str(self.tmp / "a"),
            "--after", str(self.tmp / "b"),
            "--out", str(self.tmp / "diff"),
            "--format", "json",
            "--status", "changed",
            "--filter", r"/products",
        ])
        self.assertEqual(args.format, "json")
        self.assertEqual(args.status, "changed")
        self.assertEqual(args.filter, r"/products")

    def test_cli_compare_terminal_and_json_output(self):
        # Create two minimal snapshots with matching seed
        snap_a = self.tmp / "a"
        snap_b = self.tmp / "b"
        diff_out = self.tmp / "diff"
        snap_a.mkdir()
        snap_b.mkdir()

        summary_a = {"seed": "https://example.com", "snapshot_id": "snap_1", "exported_at": "2026-09-22T01:00:00Z"}
        summary_b = {"seed": "https://example.com", "snapshot_id": "snap_2", "exported_at": "2026-09-22T02:00:00Z"}
        (snap_a / "summary.json").write_text(json.dumps(summary_a), encoding="utf-8")
        (snap_b / "summary.json").write_text(json.dumps(summary_b), encoding="utf-8")
        (snap_a / "issues.json").write_text("[]", encoding="utf-8")
        (snap_b / "issues.json").write_text("[]", encoding="utf-8")

        p1 = {"url": "https://example.com", "status": 200, "data": {"title": "Title A"}}
        p2 = {"url": "https://example.com", "status": 200, "data": {"title": "Title B"}}
        with (snap_a / "pages.jsonl").open("w", encoding="utf-8") as f:
            f.write(json.dumps(p1) + "\n")
        with (snap_b / "pages.jsonl").open("w", encoding="utf-8") as f:
            f.write(json.dumps(p2) + "\n")

        # Test terminal output format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main([
                "compare",
                "--before", str(snap_a),
                "--after", str(snap_b),
                "--out", str(diff_out),
                "--format", "terminal",
            ])
        self.assertEqual(ret, 0)
        output = buf.getvalue()
        self.assertIn("Snapshot comparison", output)
        self.assertIn("Changed:   1", output)

        # Test JSON output format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main([
                "compare",
                "--before", str(snap_a),
                "--after", str(snap_b),
                "--out", str(diff_out),
                "--format", "json",
            ])
        self.assertEqual(ret, 0)
        parsed = json.loads(buf.getvalue())
        self.assertEqual(parsed["summary"]["changed"], 1)

        # Test CSV output format
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main([
                "compare",
                "--before", str(snap_a),
                "--after", str(snap_b),
                "--out", str(diff_out),
                "--format", "csv",
            ])
        self.assertEqual(ret, 0)
        csv_out = buf.getvalue()
        self.assertIn("url,state,field,before,after", csv_out)
        self.assertIn("CHANGED", csv_out)


if __name__ == "__main__":
    unittest.main()
