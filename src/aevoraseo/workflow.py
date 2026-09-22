"""Operational acceptance verification, progress tracking, and diagnostics for AevoraSEO."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .unified_report import generate_unified_report


def verify_audit_acceptance(audit_report: Dict[str, Any], current_crawl_dir: Path) -> Dict[str, Any]:
    """Verify whether prior audit recommendations have been satisfied in the current crawl."""
    current_path = Path(current_crawl_dir).resolve()
    if not current_path.is_dir():
        raise ValueError(f"Current crawl directory does not exist: {current_path}")

    # Generate current unified report to compare against
    current_report = generate_unified_report(current_path)

    # Extract prior items
    prior_items = audit_report.get("acceptance_checklist") or []
    if not prior_items and "prioritized_issues" in audit_report:
        prior_items = [
            {
                "issue_id": i.get("id", f"ISSUE-{idx:03d}"),
                "title": i.get("title", "Issue"),
                "priority": i.get("priority", "P1"),
                "acceptance_criteria": i.get("acceptance_check", ""),
            }
            for idx, i in enumerate(audit_report["prioritized_issues"], 1)
        ]
    elif not prior_items and "findings" in audit_report:
        prior_items = [
            {
                "issue_id": f"FINDING-{idx:03d}",
                "title": f.get("title") or f.get("code", "Finding"),
                "priority": f.get("priority", "P1"),
                "acceptance_criteria": f.get("acceptance_check", "Check resolved"),
            }
            for idx, f in enumerate(audit_report["findings"], 1)
        ]

    # Map current active issue titles
    current_issue_titles = {i.title.lower() for i in current_report.prioritized_issues}

    verification_items: List[Dict[str, Any]] = []
    resolved = 0
    unresolved = 0

    for item in prior_items:
        title = item.get("title", "")
        # Check if identical issue exists in current report
        matching_current = any(
            title.lower() in ct or ct in title.lower() for ct in current_issue_titles
        )

        if not matching_current:
            status = "RESOLVED"
            detail = "Issue is no longer detected in the current crawl snapshot."
            resolved += 1
        else:
            status = "UNRESOLVED"
            detail = "Issue condition persists in current crawl."
            unresolved += 1

        verification_items.append(
            {
                "id": item.get("issue_id", ""),
                "title": title,
                "priority": item.get("priority", "P1"),
                "acceptance_criteria": item.get("acceptance_criteria", ""),
                "status": status,
                "detail": detail,
            }
        )

    total = len(verification_items)
    if total == 0:
        overall_status = "NO_PRIOR_ITEMS"
    elif unresolved == 0:
        overall_status = "ALL_RESOLVED"
    elif resolved > 0:
        overall_status = "PARTIAL_PROGRESS"
    else:
        overall_status = "NO_PROGRESS"

    return {
        "target": audit_report.get("target") or current_report.target,
        "audit_created_at": audit_report.get("created_at", "Not recorded"),
        "verification_date": datetime.now(timezone.utc).isoformat(),
        "total_items": total,
        "resolved_count": resolved,
        "unresolved_count": unresolved,
        "overall_status": overall_status,
        "current_health_score": current_report.overall_score,
        "items": verification_items,
    }


def track_progress(historical_crawl_dirs: List[Path]) -> Dict[str, Any]:
    """Calculate multi-snapshot score trajectory across chronological crawl snapshots."""
    valid_dirs = [Path(d).resolve() for d in historical_crawl_dirs if Path(d).is_dir()]
    if not valid_dirs:
        raise ValueError("At least one valid crawl directory is required for progress tracking.")

    # Sort directories by creation time or folder name
    timeline = []
    for d in valid_dirs:
        try:
            report = generate_unified_report(d)
            timeline.append(
                {
                    "directory": str(d),
                    "created_at": report.created_at,
                    "target": report.target,
                    "overall_score": report.overall_score,
                    "subsystem_scores": {
                        k: v.score for k, v in report.subsystem_scores.items() if v.score is not None
                    },
                    "issues_count": len(report.prioritized_issues),
                }
            )
        except Exception as err:
            timeline.append(
                {
                    "directory": str(d),
                    "error": str(err),
                }
            )

    # Calculate overall delta if >= 2 snapshots
    score_delta = None
    successful_snapshots = [t for t in timeline if "overall_score" in t and t["overall_score"] is not None]
    if len(successful_snapshots) >= 2:
        first = successful_snapshots[0]["overall_score"]
        last = successful_snapshots[-1]["overall_score"]
        score_delta = round(last - first, 1)

    return {
        "snapshots_evaluated": len(timeline),
        "score_delta": score_delta,
        "trajectory": "IMPROVING" if score_delta and score_delta > 0 else "DECLINING" if score_delta and score_delta < 0 else "STABLE",
        "timeline": timeline,
    }


def run_operational_diagnostics(workspace: Optional[Path] = None) -> Dict[str, Any]:
    """Run comprehensive operational and SQLite database integrity diagnostics."""
    ws = Path(workspace).resolve() if workspace else Path.cwd().resolve()
    db_checks: List[Dict[str, str]] = []

    # Find and check SQLite databases in workspace
    for db_path in ws.rglob("*.sqlite3"):
        try:
            conn = sqlite3.connect(str(db_path))
            try:
                cur = conn.cursor()
                res = cur.execute("PRAGMA integrity_check").fetchone()
                status = "PASS" if res and res[0] == "ok" else f"FAIL: {res}"
            finally:
                conn.close()
            db_checks.append({"path": str(db_path.relative_to(ws)), "integrity": status})
        except Exception as err:
            db_checks.append({"path": str(db_path.relative_to(ws)), "integrity": f"ERROR: {err}"})

    # Disk space check
    try:
        total, used, free = shutil.disk_usage(ws)
        free_gb = round(free / (1024**3), 2)
    except Exception:
        free_gb = -1.0

    return {
        "workspace": str(ws),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_executable": sys.executable,
        "free_disk_space_gb": free_gb,
        "databases_inspected": len(db_checks),
        "database_integrity": db_checks,
        "status": "HEALTHY" if all("PASS" in c["integrity"] for c in db_checks) else "DEGRADED",
    }
