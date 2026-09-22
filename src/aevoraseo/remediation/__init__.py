"""AevoraSEO Automated Remediation & Code Patch Subsystem (Phase K).

Provides deterministic AST/HTML patching, prioritized plan generation,
atomic staging/execution with SHA-256 pre/post checks, and verified rollbacks.
"""

from __future__ import annotations

from .executor import (
    FileChangeRecord,
    RemediationReceipt,
    RollbackReceipt,
    apply_remediation_plan,
    preview_plan,
    rollback_remediation_plan,
)
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
from .persistence import (
    get_db_path,
    init_db,
    list_plans,
    load_plan,
    save_plan,
    save_receipt,
)
from .planner import (
    RemediationPatch,
    RemediationPlan,
    generate_remediation_plan,
)
from .reporter import (
    export_patches_csv,
    render_diff_previews,
    render_markdown_plan,
    render_receipt_terminal,
    render_rollback_terminal,
    render_terminal_plan,
)

__all__ = [
    "PatchResult",
    "PatchType",
    "patch_title",
    "patch_meta_description",
    "patch_headings",
    "patch_direct_answer",
    "patch_schema",
    "patch_canonical",
    "patch_internal_link",
    "RemediationPatch",
    "RemediationPlan",
    "generate_remediation_plan",
    "FileChangeRecord",
    "RemediationReceipt",
    "RollbackReceipt",
    "preview_plan",
    "apply_remediation_plan",
    "rollback_remediation_plan",
    "init_db",
    "save_plan",
    "load_plan",
    "list_plans",
    "save_receipt",
    "get_db_path",
    "render_terminal_plan",
    "render_markdown_plan",
    "render_diff_previews",
    "export_patches_csv",
    "render_receipt_terminal",
    "render_rollback_terminal",
]
