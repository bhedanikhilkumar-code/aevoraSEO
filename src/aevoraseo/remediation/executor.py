"""Safe staging, execution, and rollback engine for AevoraSEO remediation patches.

Enforces strict path traversal checks, pre/post SHA-256 byte checksums,
atomic file backups, and deterministic rollback guarantees.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from .patcher import (
    PatchResult,
    PatchType,
    patch_canonical,
    patch_direct_answer,
    patch_headings,
    patch_internal_link,
    patch_meta_description,
    patch_schema,
    patch_title,
)
from .planner import RemediationPatch, RemediationPlan


@dataclass
class FileChangeRecord:
    relative_path: str
    patch_id: str
    patch_type: str
    before_sha256: str
    after_sha256: str
    backup_path: str
    status: str
    diff: str = ""
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FileChangeRecord:
        return cls(**data)


@dataclass
class RemediationReceipt:
    receipt_id: str
    plan_id: str
    site_root: str
    created_at: str
    dry_run: bool
    changes: list[FileChangeRecord] = field(default_factory=list)
    total_applied: int = 0
    total_failed: int = 0
    backup_dir: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "plan_id": self.plan_id,
            "site_root": self.site_root,
            "created_at": self.created_at,
            "dry_run": self.dry_run,
            "total_applied": self.total_applied,
            "total_failed": self.total_failed,
            "backup_dir": self.backup_dir,
            "changes": [c.to_dict() for c in self.changes],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RemediationReceipt:
        changes = [FileChangeRecord.from_dict(c) for c in data.get("changes", [])]
        return cls(
            receipt_id=data.get("receipt_id", ""),
            plan_id=data.get("plan_id", ""),
            site_root=data.get("site_root", ""),
            created_at=data.get("created_at", ""),
            dry_run=data.get("dry_run", False),
            changes=changes,
            total_applied=data.get("total_applied", 0),
            total_failed=data.get("total_failed", 0),
            backup_dir=data.get("backup_dir", ""),
        )


@dataclass
class RollbackReceipt:
    rollback_id: str
    original_receipt_id: str
    site_root: str
    rolled_back_at: str
    restored_files: list[str] = field(default_factory=list)
    failed_files: list[str] = field(default_factory=list)
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_relative_path(rel_path: str) -> PurePosixPath:
    """Validate relative path to prevent directory traversal and system file attacks."""
    p = PurePosixPath(rel_path)
    if (
        not rel_path
        or p.is_absolute()
        or "\\" in rel_path
        or ".." in p.parts
        or any(ord(c) < 32 for c in rel_path)
    ):
        raise ValueError(f"Invalid or unsafe relative path: {rel_path}")
    if p.suffix.lower() not in (".html", ".htm", ".md", ".php"):
        raise ValueError(f"Refusing to patch non-content file: {rel_path}")
    return p


def execute_single_patch(
    html: str,
    patch: RemediationPatch,
    filename: str = "content.html",
) -> PatchResult:
    """Execute a single patch against HTML string based on its patch_type."""
    ptype = patch.patch_type
    params = patch.patch_params

    if ptype == PatchType.TITLE.value:
        return patch_title(html, params.get("new_title", ""), filename=filename)
    elif ptype == PatchType.META_DESCRIPTION.value:
        return patch_meta_description(html, params.get("new_description", ""), filename=filename)
    elif ptype == PatchType.HEADING_HIERARCHY.value:
        return patch_headings(
            html,
            h1_text=params.get("h1_text"),
            demote_extra_h1=params.get("demote_extra_h1", True),
            level_repairs=params.get("level_repairs"),
            filename=filename,
        )
    elif ptype == PatchType.DIRECT_ANSWER.value:
        return patch_direct_answer(
            html,
            heading_pattern=params.get("heading_pattern", ""),
            answer_text=params.get("answer_text", ""),
            list_items=params.get("list_items"),
            filename=filename,
        )
    elif ptype == PatchType.SCHEMA_JSONLD.value:
        return patch_schema(html, params.get("schema_data", {}), filename=filename)
    elif ptype == PatchType.CANONICAL.value:
        return patch_canonical(html, params.get("canonical_url", ""), filename=filename)
    elif ptype == PatchType.INTERNAL_LINK.value:
        return patch_internal_link(
            html,
            target_url=params.get("target_url", ""),
            anchor_text=params.get("anchor_text", ""),
            context_keyword=params.get("context_keyword"),
            filename=filename,
        )
    else:
        raise ValueError(f"Unknown patch type: {ptype}")


def preview_plan(plan: RemediationPlan) -> list[dict[str, Any]]:
    """Preview all patches in a plan without modifying disk files."""
    site_root = Path(plan.site_root).resolve()
    previews: list[dict[str, Any]] = []

    # Group patches by file so multi-patch files can be chained in preview
    by_file: dict[str, list[RemediationPatch]] = {}
    for p in plan.patches:
        by_file.setdefault(p.relative_path, []).append(p)

    for rel_path, patch_list in by_file.items():
        _validate_relative_path(rel_path)
        target_file = site_root / rel_path
        if not target_file.is_file():
            for p in patch_list:
                previews.append({
                    "patch_id": p.id,
                    "relative_path": rel_path,
                    "patch_type": p.patch_type,
                    "success": False,
                    "diff": "",
                    "details": f"Target file does not exist: {target_file}",
                })
            continue

        original_content = target_file.read_text(encoding="utf-8", errors="replace")
        current_html = original_content

        for p in patch_list:
            res = execute_single_patch(current_html, p, filename=rel_path)
            previews.append({
                "patch_id": p.id,
                "relative_path": rel_path,
                "patch_type": p.patch_type,
                "success": res.success,
                "original_snippet": res.original_snippet,
                "replacement_snippet": res.replacement_snippet,
                "diff": res.diff,
                "details": res.details,
            })
            if res.success:
                current_html = res.full_html

    return previews


def apply_remediation_plan(
    plan: RemediationPlan,
    dry_run: bool = False,
    backup_dir: Path | str | None = None,
) -> RemediationReceipt:
    """Apply all patches in a plan atomically with backup preservation."""
    from ..network import utcnow

    site_root = Path(plan.site_root).resolve()
    if not site_root.is_dir():
        raise ValueError(f"Site root directory does not exist: {site_root}")

    receipt_id = f"receipt_{uuid.uuid4().hex[:8]}"
    created_at = utcnow()
    if backup_dir:
        b_dir = Path(backup_dir).resolve()
    else:
        b_dir = site_root / ".aevora_backups" / plan.plan_id
    if not dry_run:
        b_dir.mkdir(parents=True, exist_ok=True)

    records: list[FileChangeRecord] = []
    total_applied = 0
    total_failed = 0

    # Group patches by file to apply cumulative changes sequentially
    by_file: dict[str, list[RemediationPatch]] = {}
    for p in plan.patches:
        by_file.setdefault(p.relative_path, []).append(p)

    for rel_path, patch_list in by_file.items():
        _validate_relative_path(rel_path)
        target_file = site_root / rel_path

        if not target_file.is_file():
            for p in patch_list:
                records.append(
                    FileChangeRecord(
                        relative_path=rel_path,
                        patch_id=p.id,
                        patch_type=p.patch_type,
                        before_sha256="",
                        after_sha256="",
                        backup_path="",
                        status="FAILED",
                        details=f"File not found: {target_file}",
                    )
                )
                total_failed += 1
            continue

        orig_bytes = target_file.read_bytes()
        before_digest = _compute_sha256(orig_bytes)
        orig_text = orig_bytes.decode("utf-8", errors="replace")

        # Save backup copy before applying any patches to this file
        backup_file = b_dir / rel_path
        if not dry_run:
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            backup_file.write_bytes(orig_bytes)

        current_text = orig_text
        file_cumulative_diff = ""

        for p in patch_list:
            res = execute_single_patch(current_text, p, filename=rel_path)
            if res.success:
                current_text = res.full_html
                file_cumulative_diff += f"\n{res.diff}"
                records.append(
                    FileChangeRecord(
                        relative_path=rel_path,
                        patch_id=p.id,
                        patch_type=p.patch_type,
                        before_sha256=before_digest,
                        after_sha256="",  # filled after final write
                        backup_path=str(backup_file) if not dry_run else "",
                        status="APPLIED" if not dry_run else "SIMULATED",
                        diff=res.diff,
                        details=res.details,
                    )
                )
                total_applied += 1
            else:
                records.append(
                    FileChangeRecord(
                        relative_path=rel_path,
                        patch_id=p.id,
                        patch_type=p.patch_type,
                        before_sha256=before_digest,
                        after_sha256=before_digest,
                        backup_path=str(backup_file) if not dry_run else "",
                        status="FAILED",
                        details=res.details,
                    )
                )
                total_failed += 1

        # Atomically write final modified text to disk if changes were made and not dry_run
        if not dry_run and current_text != orig_text:
            mod_bytes = current_text.encode("utf-8")
            after_digest = _compute_sha256(mod_bytes)

            # Atomic replace via tempfile
            temp_fd, temp_name = tempfile.mkstemp(
                dir=str(target_file.parent),
                prefix=".aevora_tmp_",
            )
            try:
                with os.fdopen(temp_fd, "wb") as f:
                    f.write(mod_bytes)
                os.replace(temp_name, str(target_file))
            finally:
                if os.path.exists(temp_name):
                    try:
                        os.unlink(temp_name)
                    except OSError:
                        pass

            # Update after_sha256 on applied records
            for r in records:
                if r.relative_path == rel_path and r.status in ("APPLIED", "SIMULATED"):
                    r.after_sha256 = after_digest

    receipt = RemediationReceipt(
        receipt_id=receipt_id,
        plan_id=plan.plan_id,
        site_root=str(site_root),
        created_at=created_at,
        dry_run=dry_run,
        changes=records,
        total_applied=total_applied,
        total_failed=total_failed,
        backup_dir=str(b_dir) if not dry_run else "",
    )

    if not dry_run:
        receipt_file = b_dir / "receipt.json"
        receipt_file.write_text(
            json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return receipt


def rollback_remediation_plan(
    receipt_data: Path | str | dict[str, Any],
    site_root: Path | str | None = None,
) -> RollbackReceipt:
    """Roll back applied changes using the recorded backup bytes in receipt."""
    from ..network import utcnow

    if isinstance(receipt_data, (str, Path)):
        p = Path(receipt_data)
        if not p.is_file():
            raise ValueError(f"Receipt file does not exist: {p}")
        data = json.loads(p.read_text(encoding="utf-8"))
    else:
        data = receipt_data

    receipt = RemediationReceipt.from_dict(data)
    root = Path(site_root).resolve() if site_root else Path(receipt.site_root).resolve()
    backup_base = Path(receipt.backup_dir).resolve() if receipt.backup_dir else root / ".aevora_backups" / receipt.plan_id

    rollback_id = f"rollback_{uuid.uuid4().hex[:8]}"
    rolled_back_at = utcnow()
    restored: list[str] = []
    failed: list[str] = []

    # Get distinct files to restore
    distinct_files = {c.relative_path: c for c in receipt.changes if c.status == "APPLIED"}

    for rel_path, change in distinct_files.items():
        _validate_relative_path(rel_path)
        target_file = root / rel_path
        backup_file = backup_base / rel_path

        if not backup_file.is_file():
            failed.append(f"{rel_path}: backup not found at {backup_file}")
            continue

        backup_bytes = backup_file.read_bytes()
        digest = _compute_sha256(backup_bytes)
        if change.before_sha256 and digest != change.before_sha256:
            failed.append(f"{rel_path}: backup checksum mismatch (expected {change.before_sha256}, got {digest})")
            continue

        # Restore atomically
        temp_fd, temp_name = tempfile.mkstemp(
            dir=str(target_file.parent),
            prefix=".aevora_rb_",
        )
        try:
            with os.fdopen(temp_fd, "wb") as f:
                f.write(backup_bytes)
            os.replace(temp_name, str(target_file))
            restored.append(rel_path)
        except Exception as e:
            failed.append(f"{rel_path}: failed to restore ({e})")
        finally:
            if os.path.exists(temp_name):
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass

    return RollbackReceipt(
        rollback_id=rollback_id,
        original_receipt_id=receipt.receipt_id,
        site_root=str(root),
        rolled_back_at=rolled_back_at,
        restored_files=restored,
        failed_files=failed,
        details=f"Successfully restored {len(restored)} files; {len(failed)} failures.",
    )
