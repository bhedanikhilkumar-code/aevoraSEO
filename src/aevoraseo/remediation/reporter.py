"""Multi-format reporting for AevoraSEO remediation plans, diff previews, and receipts.

Generates terminal ANSI scorecards, unified diff blocks, Markdown documentation,
JSON models, and formula-injection-sanitized CSV exports.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

def sanitize_csv_cell(value: Any) -> str:
    """Neutralize spreadsheet formula injection traps (=, +, -, @, \\t, \\r, leading space)."""
    s = str(value) if value is not None else ""
    if s.startswith(("=", "+", "-", "@", "\t", "\r")) or s.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + s
    return s
from .executor import RemediationReceipt, RollbackReceipt
from .planner import RemediationPlan


def render_terminal_plan(plan: RemediationPlan) -> str:
    """Render a human-readable terminal summary of a RemediationPlan."""
    lines = [
        "==================================================================",
        f" AevoraSEO Remediation Plan — Target: {plan.target_host}",
        "==================================================================",
        f"Plan ID:                 {plan.plan_id}",
        f"Site Root:               {plan.site_root}",
        f"Crawl Directory:         {plan.crawl_dir or 'Local Scan'}",
        f"Created At:              {plan.created_at}",
        f"Total Patches:           {len(plan.patches)}",
        f"Est. Health Score Delta: +{plan.estimated_total_score_impact:.1f} pts",
        "------------------------------------------------------------------",
        f"{'ID':<11} {'PRI':<5} {'TYPE':<18} {'FILE':<22} {'IMPACT':<7}",
        "------------------------------------------------------------------",
    ]

    for p in plan.patches:
        fname = Path(p.relative_path).name
        if len(fname) > 20:
            fname = fname[:17] + "..."
        lines.append(
            f"{p.id:<11} {p.priority:<5} {p.patch_type:<18} {fname:<22} +{p.expected_score_impact:<6.1f}"
        )
        lines.append(f"  └─ {p.title}")
        lines.append(f"     Why: {p.rationale}")

    lines.append("==================================================================")
    lines.append("Next Steps:")
    lines.append(f"  Preview diffs:  aevoraseo remediate preview --plan {plan.plan_id}")
    lines.append(f"  Dry-run check:  aevoraseo remediate apply --plan {plan.plan_id} --dry-run")
    lines.append(f"  Apply patches:  aevoraseo remediate apply --plan {plan.plan_id}")
    lines.append("==================================================================")
    return "\n".join(lines)


def render_markdown_plan(plan: RemediationPlan) -> str:
    """Render a Markdown executive report of the plan."""
    lines = [
        f"# AevoraSEO Remediation Plan: {plan.target_host}\n",
        f"- **Plan ID:** `{plan.plan_id}`",
        f"- **Site Root:** `{plan.site_root}`",
        f"- **Crawl Directory:** `{plan.crawl_dir or 'Direct Inspection'}`",
        f"- **Created At:** `{plan.created_at}`",
        f"- **Total Planned Patches:** `{len(plan.patches)}`",
        f"- **Projected Score Delta:** `+{plan.estimated_total_score_impact:.1f} pts`\n",
        "## Prioritized Patches\n",
        "| ID | Priority | Type | Target File | Impact | Description |",
        "|---|---|---|---|---|---|",
    ]

    for p in plan.patches:
        lines.append(
            f"| `{p.id}` | **{p.priority}** | `{p.patch_type}` | `{p.relative_path}` | `+{p.expected_score_impact:.1f}` | {p.title} |"
        )

    lines.append("\n## Patch Rationales\n")
    for p in plan.patches:
        lines.append(f"### {p.id}: {p.title}")
        lines.append(f"- **File:** `{p.relative_path}` (`{p.url}`)")
        lines.append(f"- **Priority:** `{p.priority}` | **Expected Impact:** `+{p.expected_score_impact:.1f}`")
        lines.append(f"- **Rationale:** {p.rationale}")
        lines.append(f"- **Parameters:**\n```json\n{json.dumps(p.patch_params, indent=2)}\n```\n")

    return "\n".join(lines)


def render_diff_previews(previews: list[dict[str, Any]]) -> str:
    """Render unified diff previews for all patches."""
    lines = [
        "==================================================================",
        " AevoraSEO Remediation Patch Diffs Preview",
        "==================================================================",
    ]

    for prev in previews:
        lines.append(f"\n--- Patch {prev['patch_id']} [{prev['patch_type']}] on {prev['relative_path']} ---")
        if not prev["success"]:
            lines.append(f"  [ERROR] {prev['details']}")
        elif prev["diff"]:
            lines.append(prev["diff"].strip())
        else:
            lines.append("  (No byte changes required; target state already satisfied)")

    lines.append("\n==================================================================")
    return "\n".join(lines)


def export_patches_csv(plan: RemediationPlan, out_path: Path | str) -> Path:
    """Export patches to CSV with spreadsheet formula injection protection."""
    dest = Path(out_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "patch_id",
            "priority",
            "patch_type",
            "relative_path",
            "url",
            "title",
            "rationale",
            "expected_score_impact",
            "status",
        ])
        for p in plan.patches:
            writer.writerow([
                sanitize_csv_cell(p.id),
                sanitize_csv_cell(p.priority),
                sanitize_csv_cell(p.patch_type),
                sanitize_csv_cell(p.relative_path),
                sanitize_csv_cell(p.url),
                sanitize_csv_cell(p.title),
                sanitize_csv_cell(p.rationale),
                sanitize_csv_cell(f"+{p.expected_score_impact:.1f}"),
                sanitize_csv_cell(p.status),
            ])
    return dest


def render_receipt_terminal(receipt: RemediationReceipt) -> str:
    """Render execution receipt in human-readable terminal format."""
    lines = [
        "==================================================================",
        f" AevoraSEO Remediation Execution Receipt {'(DRY RUN)' if receipt.dry_run else ''}",
        "==================================================================",
        f"Receipt ID:     {receipt.receipt_id}",
        f"Plan ID:        {receipt.plan_id}",
        f"Site Root:      {receipt.site_root}",
        f"Timestamp:      {receipt.created_at}",
        f"Total Applied:  {receipt.total_applied}",
        f"Total Failed:   {receipt.total_failed}",
        f"Backup Store:   {receipt.backup_dir or 'None (Dry Run)'}",
        "------------------------------------------------------------------",
        f"{'FILE':<28} {'TYPE':<16} {'STATUS':<10} {'DETAILS':<20}",
        "------------------------------------------------------------------",
    ]

    for c in receipt.changes:
        fname = Path(c.relative_path).name
        if len(fname) > 26:
            fname = fname[:23] + "..."
        lines.append(f"{fname:<28} {c.patch_type:<16} {c.status:<10} {c.details[:25]}")

    lines.append("==================================================================")
    if not receipt.dry_run and receipt.total_applied > 0:
        lines.append("To rollback changes:")
        lines.append(f"  aevoraseo remediate rollback --receipt {receipt.backup_dir}/receipt.json")
        lines.append("==================================================================")
    return "\n".join(lines)


def render_rollback_terminal(rollback: RollbackReceipt) -> str:
    """Render rollback summary in human-readable terminal format."""
    lines = [
        "==================================================================",
        " AevoraSEO Remediation Rollback Summary",
        "==================================================================",
        f"Rollback ID:      {rollback.rollback_id}",
        f"Target Root:      {rollback.site_root}",
        f"Timestamp:        {rollback.rolled_back_at}",
        f"Restored Files:   {len(rollback.restored_files)}",
        f"Failed Files:     {len(rollback.failed_files)}",
        f"Status:           {rollback.details}",
        "------------------------------------------------------------------",
    ]
    for r in rollback.restored_files:
        lines.append(f"  [RESTORED] {r}")
    for f in rollback.failed_files:
        lines.append(f"  [FAILED]   {f}")
    lines.append("==================================================================")
    return "\n".join(lines)
