"""End-to-end workflow tests for AevoraSEO remediation plans, execution, and rollback."""

from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from aevoraseo.remediation.executor import (
    apply_remediation_plan,
    preview_plan,
    rollback_remediation_plan,
)
from aevoraseo.remediation.persistence import (
    get_db_path,
    init_db,
    list_plans,
    load_plan,
    save_plan,
    save_receipt,
)
from aevoraseo.remediation.planner import generate_remediation_plan
from aevoraseo.remediation.reporter import (
    export_patches_csv,
    render_diff_previews,
    render_markdown_plan,
    render_receipt_terminal,
    render_rollback_terminal,
    render_terminal_plan,
)


class RemediationWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.site_dir = self.root / "site"
        self.site_dir.mkdir(parents=True)

        # Create sample HTML files with deliberate SEO/AEO deficiencies
        (self.site_dir / "index.html").write_text(
            "<!DOCTYPE html><html><head><meta charset='utf-8'></head>"
            "<body><p>Welcome to our dental clinic.</p></body></html>",
            encoding="utf-8",
        )
        (self.site_dir / "services.html").write_text(
            "<!DOCTYPE html><html><head><title>Svc</title></head>"
            "<body><h1>Services</h1><h1>More Services</h1>"
            "<h2>What is dental implant?</h2>"
            "<p>We offer quality care.</p></body></html>",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_plan_generation_from_site_inspection(self):
        plan = generate_remediation_plan(site_root=self.site_dir, target="dentalclinic.example")
        self.assertEqual(plan.target_host, "dentalclinic.example")
        self.assertGreaterEqual(len(plan.patches), 4)

        types = [p.patch_type for p in plan.patches]
        self.assertIn("title", types)
        self.assertIn("meta_description", types)
        self.assertIn("heading_hierarchy", types)
        self.assertIn("schema_jsonld", types)
        self.assertGreater(plan.estimated_total_score_impact, 0.0)

    def test_preview_plan_without_disk_modifications(self):
        plan = generate_remediation_plan(site_root=self.site_dir, target="dentalclinic.example")
        before_index_bytes = (self.site_dir / "index.html").read_bytes()
        before_services_bytes = (self.site_dir / "services.html").read_bytes()

        previews = preview_plan(plan)
        self.assertEqual(len(previews), len(plan.patches))
        for p in previews:
            self.assertTrue(p["success"])
            self.assertIn(p["relative_path"], ("index.html", "services.html"))

        # Verify disk files remained 100% untouched
        self.assertEqual((self.site_dir / "index.html").read_bytes(), before_index_bytes)
        self.assertEqual((self.site_dir / "services.html").read_bytes(), before_services_bytes)

    def test_dry_run_simulation(self):
        plan = generate_remediation_plan(site_root=self.site_dir, target="dentalclinic.example")
        before_bytes = (self.site_dir / "index.html").read_bytes()

        receipt = apply_remediation_plan(plan, dry_run=True)
        self.assertTrue(receipt.dry_run)
        self.assertEqual(receipt.total_applied, len(plan.patches))
        self.assertEqual(receipt.total_failed, 0)
        self.assertFalse(receipt.backup_dir)

        # Still unchanged on disk
        self.assertEqual((self.site_dir / "index.html").read_bytes(), before_bytes)

    def test_apply_and_rollback_full_cycle(self):
        plan = generate_remediation_plan(site_root=self.site_dir, target="dentalclinic.example")
        orig_index_bytes = (self.site_dir / "index.html").read_bytes()
        orig_services_bytes = (self.site_dir / "services.html").read_bytes()

        # Apply
        backup_dir = self.root / "backups"
        receipt = apply_remediation_plan(plan, dry_run=False, backup_dir=backup_dir)
        self.assertFalse(receipt.dry_run)
        self.assertGreater(receipt.total_applied, 0)
        self.assertEqual(receipt.total_failed, 0)

        # Verify disk files changed
        mod_index_text = (self.site_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn("<title>", mod_index_text)
        self.assertIn('<meta content="', mod_index_text)

        mod_services_text = (self.site_dir / "services.html").read_text(encoding="utf-8")
        self.assertIn("class=\"aevora-direct-answer\"", mod_services_text)
        self.assertEqual(mod_services_text.count("<h1>"), 1)

        # Rollback using receipt
        rollback = rollback_remediation_plan(receipt.to_dict(), site_root=self.site_dir)
        self.assertEqual(len(rollback.failed_files), 0)
        self.assertIn("index.html", rollback.restored_files)
        self.assertIn("services.html", rollback.restored_files)

        # Verify restored bytes exactly match original bytes
        self.assertEqual((self.site_dir / "index.html").read_bytes(), orig_index_bytes)
        self.assertEqual((self.site_dir / "services.html").read_bytes(), orig_services_bytes)

    def test_sqlite_persistence_plans_and_receipts(self):
        db_path = self.root / "remediations.sqlite3"
        init_db(db_path)

        plan = generate_remediation_plan(site_root=self.site_dir, target="persist.example")
        save_plan(plan, db_path)

        loaded = load_plan(plan.plan_id, db_path)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.plan_id, plan.plan_id)
        self.assertEqual(loaded.target_host, "persist.example")
        self.assertEqual(len(loaded.patches), len(plan.patches))

        plans_list = list_plans(db_path)
        self.assertEqual(len(plans_list), 1)
        self.assertEqual(plans_list[0]["plan_id"], plan.plan_id)

    def test_reporter_formatting(self):
        plan = generate_remediation_plan(site_root=self.site_dir, target="report.example")
        term_out = render_terminal_plan(plan)
        self.assertIn("AevoraSEO Remediation Plan", term_out)
        self.assertIn("PATCH-001", term_out)

        md_out = render_markdown_plan(plan)
        self.assertIn("# AevoraSEO Remediation Plan: report.example", md_out)
        self.assertIn("| ID | Priority | Type |", md_out)

        previews = preview_plan(plan)
        diff_out = render_diff_previews(previews)
        self.assertIn("AevoraSEO Remediation Patch Diffs Preview", diff_out)

        csv_file = self.root / "patches.csv"
        export_patches_csv(plan, csv_file)
        self.assertTrue(csv_file.is_file())
        csv_text = csv_file.read_text(encoding="utf-8-sig")
        self.assertIn("patch_id,priority,patch_type", csv_text)


if __name__ == "__main__":
    unittest.main()
