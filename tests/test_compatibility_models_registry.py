"""Unit tests for compatibility models and registry."""

from aevoraseo.compatibility import (
    PlatformId,
    PlatformTier,
    VerificationStatus,
    PlatformSpec,
    get_platform_registry,
    get_all_platforms,
    get_platform,
    platform_from_string,
)


def test_platform_id_enum():
    assert len(PlatformId) == 18
    assert PlatformId.CLAUDE_CODE.value == "claude-code"
    assert PlatformId.CODEX.value == "codex"
    assert PlatformId.HERMES.value == "hermes"
    assert PlatformId.OPENCLAW.value == "openclaw"
    assert PlatformId.AIDER.value == "aider"
    assert PlatformId.COPILOT.value == "copilot"
    assert PlatformId.GEMINI_CLI.value == "gemini-cli"


def test_registry_contains_all_18_platforms():
    reg = get_platform_registry()
    assert len(reg) == 18
    for pid in PlatformId:
        assert pid in reg
        spec = reg[pid]
        assert isinstance(spec, PlatformSpec)
        assert spec.id == pid
        assert spec.name
        assert spec.install_command
        assert spec.skill_file_location
        assert spec.invocation
        assert spec.smoke_test
        assert spec.runtime.python_minimum == "3.10"


def test_get_all_platforms():
    all_specs = get_all_platforms()
    assert len(all_specs) == 18
    names = {s.name for s in all_specs}
    assert "Claude Code" in names
    assert "aider" in names
    assert "Copilot CLI" in names
    assert "Gemini CLI" in names


def test_get_platform_by_id():
    spec = get_platform(PlatformId.CLAUDE_CODE)
    assert spec.name == "Claude Code"
    assert spec.tier == PlatformTier.FIRST_PARTY_SKILL
    assert spec.status == VerificationStatus.VERIFIED


def test_platform_from_string():
    assert platform_from_string("claude-code") == PlatformId.CLAUDE_CODE
    assert platform_from_string("claude") == PlatformId.CLAUDE_CODE
    assert platform_from_string("aider") == PlatformId.AIDER
    assert platform_from_string("copilot") == PlatformId.COPILOT
    assert platform_from_string("gemini") == PlatformId.GEMINI_CLI
    assert platform_from_string("gemini-cli") == PlatformId.GEMINI_CLI
    assert platform_from_string("nonexistent") is None
