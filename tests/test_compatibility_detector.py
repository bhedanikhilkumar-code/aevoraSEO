"""Unit tests for compatibility environment detection."""

import tempfile
from pathlib import Path
from aevoraseo.compatibility import (
    detect_environment,
    EnvironmentInspection,
)


def test_detect_environment_with_clean_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        clean_env = {"PATH": "/bin"}
        inspection = detect_environment(workspace=tmpdir, env=clean_env)
        assert isinstance(inspection, EnvironmentInspection)
        assert inspection.workspace_root == str(Path(tmpdir).resolve())
        assert inspection.python_version
        assert inspection.python_path
        assert inspection.aevoraseo_installed is False


def test_detect_environment_via_env_var():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_env = {"HERMES_HOME": str(tmpdir)}
        inspection = detect_environment(workspace=tmpdir, env=test_env)
        assert inspection.detected_platform == "Hermes Agent"
        assert inspection.isolation_status == "environment"


def test_detect_environment_via_workspace_marker():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)
        (ws / ".aider.conf.yml").write_text("read: []", encoding="utf-8")
        clean_env = {"PATH": "/bin"}
        inspection = detect_environment(workspace=tmpdir, env=clean_env)
        assert inspection.detected_platform == "aider"
        assert inspection.isolation_status == "workspace"
        assert ".aider.conf.yml" in inspection.config_files_found


def test_detect_environment_receipt_discovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)
        receipt = ws / "aevoraseo-install.json"
        receipt.write_text("{}", encoding="utf-8")
        clean_env = {"PATH": "/bin"}
        inspection = detect_environment(workspace=tmpdir, env=clean_env)
        assert inspection.aevoraseo_installed is True
        assert inspection.install_receipt_path == str(receipt.resolve())
