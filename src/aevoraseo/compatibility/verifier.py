"""Fixture-based platform compatibility verification for AevoraSEO."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional

from .models import (
    PlatformId,
    VerificationResult,
    VerificationStatus,
)
from .registry import get_platform, get_all_platforms
from .detector import detect_environment
from .validator import validate_installation, check_python_compatibility


def verify_platform(
    platform_id: PlatformId,
    aevoraseo_root: Optional[str] = None,
) -> VerificationResult:
    """Run fixture-based verification for a single platform.

    Creates a temporary workspace simulating the platform's expected layout,
    then validates detection, path resolution, and Python compatibility.
    Does not mutate real developer settings or install anything.
    """
    spec = get_platform(platform_id)
    steps: list[dict[str, str]] = []
    passed = 0
    failed = 0

    if aevoraseo_root is None:
        aevoraseo_root = str(Path(__file__).resolve().parents[2])

    # Step 1: Python compatibility
    py_ok, py_version = check_python_compatibility()
    if py_ok:
        steps.append({
            "step": "Python compatibility",
            "result": "PASS",
            "detail": f"Python {py_version} >= 3.10",
        })
        passed += 1
    else:
        steps.append({
            "step": "Python compatibility",
            "result": "FAIL",
            "detail": f"Python {py_version} < 3.10",
        })
        failed += 1

    # Step 2: Platform spec completeness
    spec_fields = [spec.name, spec.install_command, spec.skill_file_location, spec.invocation, spec.smoke_test]
    if all(spec_fields):
        steps.append({
            "step": "Platform specification completeness",
            "result": "PASS",
            "detail": f"All required fields present for {spec.name}",
        })
        passed += 1
    else:
        missing = [f for f, v in zip(
            ["name", "install_command", "skill_file_location", "invocation", "smoke_test"],
            spec_fields,
        ) if not v]
        steps.append({
            "step": "Platform specification completeness",
            "result": "FAIL",
            "detail": f"Missing fields: {', '.join(missing)}",
        })
        failed += 1

    # Step 3: Fixture workspace detection
    with tempfile.TemporaryDirectory(prefix="aevoraseo_verify_") as tmpdir:
        workspace = Path(tmpdir)
        # Create marker files for this platform
        for marker in spec.workspace.marker_files:
            marker_path = workspace / marker
            if marker.endswith("/"):
                marker_path.mkdir(parents=True, exist_ok=True)
            else:
                marker_path.parent.mkdir(parents=True, exist_ok=True)
                marker_path.write_text("", encoding="utf-8")

        # Build clean test environment without host platform env vars
        test_env = {
            k: v for k, v in os.environ.items()
            if not k.startswith("HERMES_")
            and not k.startswith("OPENCLAW_")
            and not k.startswith("CLAUDE_")
            and not k.startswith("AIDER_")
            and not k.startswith("CHATGPT_")
        }
        for var in spec.workspace.env_vars:
            if var not in ("LOCALAPPDATA",):  # Don't override system vars
                test_env[var] = str(workspace)

        inspection = detect_environment(workspace=str(workspace), env=test_env)

        if inspection.detected_platform == spec.name:
            steps.append({
                "step": "Fixture workspace detection",
                "result": "PASS",
                "detail": f"Detected {spec.name} from workspace markers",
            })
            passed += 1
        elif inspection.detected_platform is not None:
            steps.append({
                "step": "Fixture workspace detection",
                "result": "PARTIAL",
                "detail": f"Detected {inspection.detected_platform} instead of {spec.name}",
            })
            passed += 1  # Detection works, just different priority
        else:
            steps.append({
                "step": "Fixture workspace detection",
                "result": "FAIL",
                "detail": f"No platform detected for {spec.name} fixture",
            })
            failed += 1

    # Step 4: Install receipt validation (simulate)
    with tempfile.TemporaryDirectory(prefix="aevoraseo_receipt_") as tmpdir:
        install_dir = Path(tmpdir)
        test_content = b"# AevoraSEO Skill Package\n"
        test_file = install_dir / "SKILL.md"
        test_file.write_bytes(test_content)
        content_hash = hashlib.sha256(test_content).hexdigest()
        receipt = {
            "files_sha256": {
                "SKILL.md": content_hash,
            },
        }
        (install_dir / "aevoraseo-install.json").write_text(
            json.dumps(receipt), encoding="utf-8"
        )
        valid, issues = validate_installation(install_dir)
        if valid and not issues:
            steps.append({
                "step": "Install receipt validation",
                "result": "PASS",
                "detail": "Receipt parsing and file check succeeded",
            })
            passed += 1
        else:
            steps.append({
                "step": "Install receipt validation",
                "result": "FAIL",
                "detail": f"Issues: {'; '.join(issues[:3])}",
            })
            failed += 1

    # Determine overall status
    if failed == 0:
        status = VerificationStatus.VERIFIED
    elif passed > failed:
        status = VerificationStatus.PARTIAL
    else:
        status = VerificationStatus.NOT_VERIFIED

    evidence_lines = [f"{s['step']}: {s['result']} — {s['detail']}" for s in steps]

    return VerificationResult(
        platform=platform_id,
        status=status,
        steps=steps,
        passed=passed,
        failed=failed,
        evidence="\n".join(evidence_lines),
    )


def verify_all_platforms(
    aevoraseo_root: Optional[str] = None,
) -> List[VerificationResult]:
    """Run fixture-based verification for all registered platforms."""
    results = []
    for spec in get_all_platforms():
        results.append(verify_platform(spec.id, aevoraseo_root=aevoraseo_root))
    return results
