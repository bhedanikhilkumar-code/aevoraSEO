"""Environment detection module for AevoraSEO multi-agent compatibility."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Optional

from .models import EnvironmentInspection
from .registry import get_all_platforms


def detect_environment(
    workspace: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
) -> EnvironmentInspection:
    """Detect active agent environment, workspace root, configs, and Python runtime.

    Priority order:
    1. Active environment variables (e.g. HERMES_HOME, OPENCLAW_STATE_DIR, CLAUDE_HOME)
    2. Workspace marker files (e.g. .claude/, .agents/, .aider.conf.yml, .github/)
    3. Global user configuration paths (e.g. ~/.claude/skills/, ~/.hermes/skills/)
    """
    if env is None:
        env = dict(os.environ)

    ws_path = Path(workspace).expanduser().resolve() if workspace else Path.cwd().resolve()
    ws_str = str(ws_path)

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_path = sys.executable

    receipt_path = ws_path / "aevoraseo-install.json"
    aevoraseo_installed = receipt_path.is_file()
    install_receipt_str = str(receipt_path) if aevoraseo_installed else ""

    config_files_found = []
    detected_platform = None
    isolation_status = "unknown"

    platforms = get_all_platforms()

    # Pass 1: Environment variables
    for spec in platforms:
        for var in spec.workspace.env_vars:
            if var in env and env[var]:
                detected_platform = spec.name
                isolation_status = "environment"
                break
        if detected_platform:
            break

    # Pass 2: Workspace markers (if not detected or to find config files)
    for spec in platforms:
        for marker in spec.workspace.marker_files:
            marker_clean = marker.rstrip("/\\")
            candidate = ws_path / marker_clean
            if candidate.exists():
                rel_str = str(candidate.relative_to(ws_path))
                if rel_str not in config_files_found:
                    config_files_found.append(rel_str)
                if not detected_platform:
                    detected_platform = spec.name
                    isolation_status = "workspace"

    # Pass 3: Global config paths
    home = Path.home()
    if not detected_platform:
        for spec in platforms:
            for gpath in spec.workspace.global_config_paths:
                clean_path = gpath.replace("~/", "").rstrip("/\\")
                full_global = home / clean_path
                if full_global.exists():
                    detected_platform = spec.name
                    isolation_status = "global"
                    break
            if detected_platform:
                break

    return EnvironmentInspection(
        detected_platform=detected_platform,
        workspace_root=ws_str,
        config_files_found=config_files_found,
        python_version=python_version,
        python_path=python_path,
        aevoraseo_installed=aevoraseo_installed,
        install_receipt_path=install_receipt_str,
        isolation_status=isolation_status,
    )
