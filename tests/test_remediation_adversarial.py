"""Adversarial and security tests for AevoraSEO remediation engine.

Verifies path traversal defenses, dangerous file extension blocking,
CSV formula injection neutralization, corrupted backup detection,
and resilience against malformed HTML inputs.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aevoraseo.remediation.executor import (
    _validate_relative_path,
    apply_remediation_plan,
    rollback_remediation_plan,
)
from aevoraseo.remediation.patcher import (
    patch_canonical,
    patch_direct_answer,
    patch_headings,
    patch_meta_description,
    patch_title,
)
from aevoraseo.remediation.planner import RemediationPatch, RemediationPlan
from aevoraseo.remediation.reporter import export_patches_csv, sanitize_csv_cell


class RemediationAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.site_dir = self.root / "site"
        self.site_dir.mkdir(parents=True)
        (self.site_dir / "index.html").write_text("<html><body>Test</body></html>", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_path_traversal_attempts_blocked(self):
        dangerous_paths = [
            "../../etc/passwd",
            "../secret.txt",
            "/absolute/path/index.html",
            "C:\\Windows\\System32\\calc.exe",
            "sub/../../secret.html",
            "subdir/../../../root.html",
            "test\x00nullbyte.html",
        ]
        for p in dangerous_paths:
            with self.assertRaises(ValueError, msg=f"Should have blocked: {p}"):
                _validate_relative_path(p)

    def test_non_content_extension_blocked(self):
        forbidden_extensions = [
            "config.py",
            "database.sqlite3",
            "server.exe",
            "passwd.sh",
            "id_rsa",
            "secret.env",
            "app.jar",
        ]
        for f in forbidden_extensions:
            with self.assertRaises(ValueError, msg=f"Should have blocked: {f}"):
                _validate_relative_path(f)

    def test_csv_formula_injection_defense(self):
        # Test leading spreadsheet operators and control characters
        traps = [
            "=1+1",
            "+cmd|' /C calc'!A0",
            "-2+3",
            "@SUM(A1:A10)",
            "\t=cmd|' /C calc'!A0",
            "\r=cmd|' /C calc'!A0",
            "   =1+1",
            "   @calc",
        ]
        for trap in traps:
            sanitized = sanitize_csv_cell(trap)
            self.assertTrue(
                sanitized.startswith("'"),
                f"Formula trap '{trap}' was not neutralized; got '{sanitized}'",
            )

        # Test safe values are untouched
        self.assertEqual(sanitize_csv_cell("Normal Title"), "Normal Title")
        self.assertEqual(sanitize_csv_cell("P0"), "P0")

    def test_export_patches_csv_sanitizes_adversarial_plan(self):
        plan = RemediationPlan(
            plan_id="plan_adversarial",
            target_host="test.example",
            site_root=str(self.site_dir),
            crawl_dir="",
            created_at="2026-09-22T00:00:00Z",
            patches=[
                RemediationPatch(
                    id="=cmd|' /C calc'!A0",
                    patch_type="+formula",
                    relative_path="index.html",
                    url="https://test.example/@calc",
                    title="-Malicious Title",
                    rationale="\t=1+1",
                    priority="@P0",
                    expected_score_impact=5.0,
                    patch_params={},
                )
            ],
        )
        csv_file = self.root / "adversarial.csv"
        export_patches_csv(plan, csv_file)

        content = csv_file.read_text(encoding="utf-8-sig")
        lines = content.strip().splitlines()
        self.assertEqual(len(lines), 2)
        row = lines[1].split(",")

        # Verify every adversarial field is escaped with leading quote
        for cell in row:
            if any(cell.startswith(p) for p in ('"=', "'+", "'-", "'@", "'\t")):
                continue
            # If quotes wrap it: e.g. "'=cmd..."
            clean = cell.strip('"')
            if clean and clean[0] in ("=", "+", "-", "@", "\t"):
                self.fail(f"Cell '{cell}' contained unescaped formula operator!")

    def test_malformed_html_does_not_crash_patchers(self):
        malformed = "<html><head><title>Unclosed title</title><body><div><h1>Broken tags<p>Test"
        # Patcher should process without throwing an unhandled exception
        res1 = patch_title(malformed, "New Title")
        self.assertTrue(res1.success)

        res2 = patch_meta_description(malformed, "New Desc")
        self.assertTrue(res2.success)

        res3 = patch_headings(malformed, h1_text="Fixed H1")
        self.assertTrue(res3.success)

        res4 = patch_direct_answer(malformed, "Broken", "Answer text")
        self.assertTrue(res4.success)

        res5 = patch_canonical(malformed, "https://example.com")
        self.assertTrue(res5.success)

    def test_corrupted_backup_detected_on_rollback(self):
        # Create plan, apply, then tamper with the backup file
        plan = RemediationPlan(
            plan_id="plan_corrupt_test",
            target_host="test.example",
            site_root=str(self.site_dir),
            crawl_dir="",
            created_at="2026-09-22T00:00:00Z",
            patches=[
                RemediationPatch(
                    id="PATCH-001",
                    patch_type="title",
                    relative_path="index.html",
                    url="https://test.example/",
                    title="Add Title",
                    rationale="Testing backup integrity",
                    priority="P0",
                    expected_score_impact=5.0,
                    patch_params={"new_title": "Tamper Test"},
                )
            ],
        )
        backup_dir = self.root / "backups_corrupt"
        receipt = apply_remediation_plan(plan, dry_run=False, backup_dir=backup_dir)

        # Deliberately corrupt the backup file
        backup_file = backup_dir / "index.html"
        self.assertTrue(backup_file.is_file())
        backup_file.write_text("CORRUPTED BACKUP CONTENT", encoding="utf-8")

        # Rollback must detect checksum mismatch and refuse to overwrite target with corrupted data
        rollback = rollback_remediation_plan(receipt.to_dict(), site_root=self.site_dir)
        self.assertEqual(len(rollback.restored_files), 0)
        self.assertEqual(len(rollback.failed_files), 1)
        self.assertIn("checksum mismatch", rollback.failed_files[0])


if __name__ == "__main__":
    unittest.main()
