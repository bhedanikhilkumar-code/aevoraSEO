"""Profile and workspace validation for AevoraSEO multi-agent compatibility."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import List, Tuple


def validate_installation(install_path: Path) -> Tuple[bool, List[str]]:
    """Validate that an existing AevoraSEO skill directory matches its install receipt."""
    issues: List[str] = []
    install_dir = Path(install_path).expanduser().resolve()

    if not install_dir.is_dir():
        return False, [f"Install path is not a directory: {install_dir}"]

    receipt_file = install_dir / "aevoraseo-install.json"
    if not receipt_file.is_file():
        return False, ["Missing installation receipt: aevoraseo-install.json"]

    try:
        data = json.loads(receipt_file.read_text(encoding="utf-8"))
    except Exception as err:
        return False, [f"Failed to parse receipt JSON: {err}"]

    if not isinstance(data, dict):
        return False, ["Receipt JSON must be an object"]

    files_sha256 = data.get("files_sha256")
    if not isinstance(files_sha256, dict):
        return False, ["Receipt missing valid 'files_sha256' manifest"]

    for rel_name, expected_hash in files_sha256.items():
        if not isinstance(rel_name, str) or not isinstance(expected_hash, str):
            issues.append(f"Invalid manifest entry: {rel_name}")
            continue

        target = install_dir / rel_name
        if not target.is_file():
            issues.append(f"Missing installed file: {rel_name}")
            continue

        try:
            actual_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                issues.append(f"Hash mismatch for {rel_name}: expected {expected_hash[:8]}, got {actual_hash[:8]}")
        except Exception as err:
            issues.append(f"Error reading {rel_name}: {err}")

    return len(issues) == 0, issues


def validate_workspace_isolation(workspace: Path) -> Tuple[bool, List[str]]:
    """Verify that a workspace maintains proper isolation boundaries."""
    issues: List[str] = []
    ws_dir = Path(workspace).expanduser().resolve()

    if not ws_dir.is_dir():
        return False, [f"Workspace is not a valid directory: {ws_dir}"]

    # Check for symlinks pointing outside workspace
    try:
        for p in ws_dir.rglob("*"):
            if p.is_symlink():
                try:
                    resolved = p.resolve()
                    if not resolved.is_relative_to(ws_dir):
                        issues.append(f"Unsafe symlink pointing outside workspace: {p.name} -> {resolved}")
                except (ValueError, RuntimeError):
                    issues.append(f"Broken or cyclic symlink: {p.name}")
    except Exception as err:
        issues.append(f"Error scanning workspace symlinks: {err}")

    return len(issues) == 0, issues


def check_python_compatibility() -> Tuple[bool, str]:
    """Verify that current Python runtime satisfies the engine requirement (>= 3.10)."""
    version_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    compatible = sys.version_info >= (3, 10)
    return compatible, version_str
