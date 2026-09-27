"""Tests for universal skill installer, git pull engine, and CLI agent commands."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from aevoraseo.compatibility import (
    PlatformId,
    bundle_files,
    generate_adapter,
    host_destination,
    install_skill,
    validate_installation,
)


def test_host_destination_resolutions():
    home = Path.home()
    # Global destinations
    assert host_destination("claude-code") == home / ".claude/skills/aevoraseo"
    assert host_destination("claude") == home / ".claude/skills/aevoraseo"
    assert host_destination("gemini") == home / ".gemini/skills/aevoraseo"
    assert host_destination("antigravity") == home / ".gemini/skills/aevoraseo"
    assert host_destination("cursor") == home / ".agents/skills/aevoraseo"
    assert host_destination("codex") == home / ".agents/skills/aevoraseo"

    # Workspace destinations
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)
        assert host_destination("claude-code", workspace=ws) == ws / ".claude/skills/aevoraseo"
        assert host_destination("gemini", workspace=ws) == ws / ".gemini/skills/aevoraseo"
        assert host_destination("cursor", workspace=ws) == ws / ".agents/skills/aevoraseo"
        assert host_destination("codex", workspace=ws) == ws / ".agents/skills/aevoraseo"


def test_install_skill_lifecycle():
    with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as ws_dir:
        src = Path(src_dir)
        ws = Path(ws_dir)

        # Create minimal valid bundle source
        for name in ("SKILL.md", "pyproject.toml", "LICENSE"):
            (src / name).write_text("dummy", encoding="utf-8")
        (src / "src").mkdir()
        (src / "src" / "test.py").write_text("# code", encoding="utf-8")

        # 1. Dry run
        dry_res = install_skill(
            source=src,
            host="cursor",
            workspace=ws,
            dry_run=True,
        )
        assert dry_res["status"] == "dry_run"
        dest_path = Path(dry_res["destination"])
        assert not dest_path.exists()

        # 2. Real install
        real_res = install_skill(
            source=src,
            host="cursor",
            workspace=ws,
            dry_run=False,
        )
        assert real_res["status"] == "installed"
        assert dest_path.is_dir()
        assert (dest_path / "SKILL.md").is_file()
        assert (dest_path / "aevoraseo-install.json").is_file()
        assert (ws / ".cursorrules").is_file()

        # Validate with existing validator
        valid, issues = validate_installation(dest_path)
        assert valid is True
        assert len(issues) == 0


def test_cli_agent_install_dry_run():
    repo_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as ws_dir:
        cmd = [
            sys.executable,
            "-m",
            "aevoraseo.cli",
            "agent",
            "install",
            "gemini",
            "--workspace",
            ws_dir,
            "--dry-run",
            "--format",
            "json",
        ]
        proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        data = json.loads(proc.stdout)
        assert data["status"] == "dry_run"
        assert "aevoraseo" in data["destination"]


def test_cli_skill_install_dry_run():
    repo_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as ws_dir:
        cmd = [
            sys.executable,
            "-m",
            "aevoraseo.cli",
            "skill",
            "install",
            "claude-code",
            "--workspace",
            ws_dir,
            "--dry-run",
            "--format",
            "json",
        ]
        proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        data = json.loads(proc.stdout)
        assert data["status"] == "dry_run"
        assert ".claude" in data["destination"]


def test_cli_agent_adapt_cursor():
    with tempfile.TemporaryDirectory() as ws_dir:
        ws = Path(ws_dir)
        res = generate_adapter(PlatformId.CODEX, workspace=str(ws))
        assert res.platform == PlatformId.CODEX
        assert ".cursorrules" in res.files_written
        assert (ws / ".cursorrules").is_file()
