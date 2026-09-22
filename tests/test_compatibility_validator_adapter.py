"""Unit tests for compatibility validator and adapter generator."""

import hashlib
import json
import tempfile
from pathlib import Path
from aevoraseo.compatibility import (
    PlatformId,
    validate_installation,
    validate_workspace_isolation,
    check_python_compatibility,
    generate_adapter,
)


def test_python_compatibility():
    compatible, ver = check_python_compatibility()
    assert compatible is True
    assert ver.startswith("3.")


def test_validate_installation_valid():
    with tempfile.TemporaryDirectory() as tmpdir:
        install_dir = Path(tmpdir)
        content = b"# Skill\n"
        (install_dir / "SKILL.md").write_bytes(content)
        receipt = {
            "files_sha256": {
                "SKILL.md": hashlib.sha256(content).hexdigest(),
            }
        }
        (install_dir / "aevoraseo-install.json").write_text(json.dumps(receipt), encoding="utf-8")
        valid, issues = validate_installation(install_dir)
        assert valid is True
        assert len(issues) == 0


def test_validate_installation_tampered():
    with tempfile.TemporaryDirectory() as tmpdir:
        install_dir = Path(tmpdir)
        (install_dir / "SKILL.md").write_bytes(b"tampered content")
        receipt = {
            "files_sha256": {
                "SKILL.md": "0000000000000000000000000000000000000000000000000000000000000000",
            }
        }
        (install_dir / "aevoraseo-install.json").write_text(json.dumps(receipt), encoding="utf-8")
        valid, issues = validate_installation(install_dir)
        assert valid is False
        assert any("Hash mismatch" in i for i in issues)


def test_validate_workspace_isolation_clean():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)
        valid, issues = validate_workspace_isolation(ws)
        assert valid is True
        assert len(issues) == 0


def test_generate_adapter_aider():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)
        result = generate_adapter(PlatformId.AIDER, workspace=str(ws))
        assert result.platform == PlatformId.AIDER
        assert ".aider.conf.yml" in result.files_written
        assert (ws / ".aider.conf.yml").is_file()
        assert (ws / ".aider.conventions.md").is_file()


def test_generate_adapter_copilot():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)
        result = generate_adapter(PlatformId.COPILOT, workspace=str(ws))
        assert result.platform == PlatformId.COPILOT
        assert (ws / ".github" / "copilot-instructions.md").is_file()


def test_generate_adapter_dry_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)
        result = generate_adapter(PlatformId.GEMINI_CLI, workspace=str(ws), dry_run=True)
        assert result.dry_run is True
        assert "GEMINI.md" in result.files_written
        assert not (ws / "GEMINI.md").exists()
