"""SQLite persistence layer for AevoraSEO remediation plans and receipts.

Stores remediation plans, individual patches, execution receipts, and rollback
records in remediations.sqlite3 with deterministic connection lifecycle management.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .executor import FileChangeRecord, RemediationReceipt
from .planner import RemediationPatch, RemediationPlan


def get_db_path(base_dir: Path | str) -> Path:
    p = Path(base_dir).resolve()
    if p.is_file() and p.name.endswith(".sqlite3"):
        return p
    return p / "remediations.sqlite3"


def init_db(db_path: Path | str) -> None:
    """Initialize SQLite tables for remediation subsystem with immediate close."""
    p = Path(db_path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS remediation_plans (
                plan_id TEXT PRIMARY KEY,
                target_host TEXT NOT NULL,
                site_root TEXT NOT NULL,
                crawl_dir TEXT,
                created_at TEXT NOT NULL,
                total_patches INTEGER NOT NULL,
                estimated_score_impact REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS remediation_patches (
                patch_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                patch_type TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                rationale TEXT NOT NULL,
                priority TEXT NOT NULL,
                expected_score_impact REAL NOT NULL,
                patch_params_json TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES remediation_plans (plan_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS remediation_receipts (
                receipt_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                site_root TEXT NOT NULL,
                created_at TEXT NOT NULL,
                dry_run INTEGER NOT NULL,
                total_applied INTEGER NOT NULL,
                total_failed INTEGER NOT NULL,
                backup_dir TEXT NOT NULL,
                changes_json TEXT NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES remediation_plans (plan_id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_plan(plan: RemediationPlan, db_path: Path | str, status: str = "CREATED") -> None:
    """Save or update a RemediationPlan and its constituent patches."""
    init_db(db_path)
    p = Path(db_path).resolve()
    conn = sqlite3.connect(str(p))
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO remediation_plans (
                    plan_id, target_host, site_root, crawl_dir, created_at,
                    total_patches, estimated_score_impact, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(plan_id) DO UPDATE SET
                    status=excluded.status,
                    total_patches=excluded.total_patches,
                    estimated_score_impact=excluded.estimated_score_impact
                """,
                (
                    plan.plan_id,
                    plan.target_host,
                    plan.site_root,
                    plan.crawl_dir,
                    plan.created_at,
                    len(plan.patches),
                    plan.estimated_total_score_impact,
                    status,
                ),
            )
            for patch in plan.patches:
                conn.execute(
                    """
                    INSERT INTO remediation_patches (
                        patch_id, plan_id, patch_type, relative_path, url,
                        title, rationale, priority, expected_score_impact,
                        patch_params_json, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(patch_id) DO UPDATE SET
                        status=excluded.status
                    """,
                    (
                        patch.id,
                        plan.plan_id,
                        patch.patch_type,
                        patch.relative_path,
                        patch.url,
                        patch.title,
                        patch.rationale,
                        patch.priority,
                        patch.expected_score_impact,
                        json.dumps(patch.patch_params, ensure_ascii=False),
                        patch.status,
                    ),
                )
    finally:
        conn.close()


def load_plan(plan_id: str, db_path: Path | str) -> RemediationPlan | None:
    """Load a RemediationPlan and all its patches from SQLite."""
    p = Path(db_path).resolve()
    if not p.is_file():
        return None
    conn = sqlite3.connect(str(p))
    try:
        cur = conn.execute(
            """
            SELECT plan_id, target_host, site_root, crawl_dir, created_at, estimated_score_impact
            FROM remediation_plans WHERE plan_id = ?
            """,
            (plan_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        p_id, host, site_root, crawl_dir, created_at, score_impact = row
        patches_cur = conn.execute(
            """
            SELECT patch_id, patch_type, relative_path, url, title, rationale,
                   priority, expected_score_impact, patch_params_json, status
            FROM remediation_patches WHERE plan_id = ?
            ORDER BY priority ASC, patch_id ASC
            """,
            (plan_id,),
        )
        patches: list[RemediationPatch] = []
        for prow in patches_cur.fetchall():
            (
                patch_id,
                ptype,
                rel_path,
                url,
                title,
                rationale,
                priority,
                impact,
                params_json,
                status,
            ) = prow
            patches.append(
                RemediationPatch(
                    id=patch_id,
                    patch_type=ptype,
                    relative_path=rel_path,
                    url=url,
                    title=title,
                    rationale=rationale,
                    priority=priority,
                    expected_score_impact=impact,
                    patch_params=json.loads(params_json) if params_json else {},
                    status=status,
                )
            )

        return RemediationPlan(
            plan_id=p_id,
            target_host=host,
            site_root=site_root,
            crawl_dir=crawl_dir or "",
            created_at=created_at,
            patches=patches,
            estimated_total_score_impact=score_impact,
        )
    finally:
        conn.close()


def list_plans(db_path: Path | str) -> list[dict[str, Any]]:
    """List all saved remediation plans with summary statistics."""
    p = Path(db_path).resolve()
    if not p.is_file():
        return []
    conn = sqlite3.connect(str(p))
    try:
        cur = conn.execute(
            """
            SELECT plan_id, target_host, site_root, created_at, total_patches,
                   estimated_score_impact, status
            FROM remediation_plans ORDER BY created_at DESC
            """
        )
        results = []
        for row in cur.fetchall():
            results.append({
                "plan_id": row[0],
                "target_host": row[1],
                "site_root": row[2],
                "created_at": row[3],
                "total_patches": row[4],
                "estimated_score_impact": row[5],
                "status": row[6],
            })
        return results
    finally:
        conn.close()


def save_receipt(receipt: RemediationReceipt, db_path: Path | str) -> None:
    """Save execution receipt into SQLite."""
    init_db(db_path)
    p = Path(db_path).resolve()
    conn = sqlite3.connect(str(p))
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO remediation_receipts (
                    receipt_id, plan_id, site_root, created_at, dry_run,
                    total_applied, total_failed, backup_dir, changes_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(receipt_id) DO UPDATE SET
                    total_applied=excluded.total_applied,
                    total_failed=excluded.total_failed,
                    changes_json=excluded.changes_json
                """,
                (
                    receipt.receipt_id,
                    receipt.plan_id,
                    receipt.site_root,
                    receipt.created_at,
                    1 if receipt.dry_run else 0,
                    receipt.total_applied,
                    receipt.total_failed,
                    receipt.backup_dir,
                    json.dumps([c.to_dict() for c in receipt.changes], ensure_ascii=False),
                ),
            )
            # Update plan status if all applied
            if not receipt.dry_run:
                status = "APPLIED" if receipt.total_failed == 0 else "PARTIAL"
                conn.execute(
                    "UPDATE remediation_plans SET status = ? WHERE plan_id = ?",
                    (status, receipt.plan_id),
                )
    finally:
        conn.close()
