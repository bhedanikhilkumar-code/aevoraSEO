"""Unit tests for compatibility verifier and CLI commands."""

import json
from aevoraseo.compatibility import (
    PlatformId,
    VerificationStatus,
    verify_platform,
    verify_all_platforms,
)
from aevoraseo.cli import main as cli_main


def test_verify_platform_claude_code():
    res = verify_platform(PlatformId.CLAUDE_CODE)
    assert res.platform == PlatformId.CLAUDE_CODE
    assert res.status == VerificationStatus.VERIFIED
    assert res.passed >= 3
    assert res.failed == 0


def test_verify_all_platforms():
    results = verify_all_platforms()
    assert len(results) == 18
    for r in results:
        assert r.passed > 0
        assert r.failed == 0
        assert r.status == VerificationStatus.VERIFIED


def test_cli_agent_list(capsys):
    ret = cli_main(["agent", "list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Claude Code" in captured.out
    assert "first-party-skill" in captured.out


def test_cli_agent_list_json(capsys):
    ret = cli_main(["agent", "list", "--format", "json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert len(data) == 18


def test_cli_agent_inspect(capsys):
    ret = cli_main(["agent", "inspect", "aider"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "aider" in captured.out
    assert "project-instruction" in captured.out


def test_cli_agent_detect(capsys):
    ret = cli_main(["agent", "detect"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Python:" in captured.out
    assert "Workspace root:" in captured.out


def test_cli_agent_verify_single(capsys):
    ret = cli_main(["agent", "verify", "--host", "openclaw"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "openclaw" in captured.out
    assert "VERIFIED" in captured.out
