"""Platform registry with empirical specifications for all 18 target environments."""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import (
    PlatformId,
    PlatformSpec,
    PlatformTier,
    RuntimeRequirements,
    VerificationStatus,
    WorkspaceBehavior,
)


def _build_registry() -> Dict[PlatformId, PlatformSpec]:
    rt = RuntimeRequirements()
    return {
        PlatformId.AGENT: PlatformSpec(
            id=PlatformId.AGENT, name="Agent (ChatGPT Work)",
            tier=PlatformTier.FIRST_PARTY_SKILL,
            install_command="python3 scripts/install_skill.py --host agent --setup",
            skill_file_location="Skills list (ChatGPT Work)",
            invocation="@aevoraseo in chat",
            workspace=WorkspaceBehavior(env_vars=["CHATGPT_SKILL_DIR"], marker_files=[]),
            runtime=rt, smoke_test="Ask assistant to run aevoraseo doctor",
            known_limitations="Cloud-hosted; file upload limits; execution sandbox restrictions",
            status=VerificationStatus.DOCUMENTED,
        ),
        PlatformId.CLAUDE_CODE: PlatformSpec(
            id=PlatformId.CLAUDE_CODE, name="Claude Code",
            tier=PlatformTier.FIRST_PARTY_SKILL,
            install_command="python3 scripts/install_skill.py --host claude-code --setup",
            skill_file_location="~/.claude/skills/aevoraseo/",
            invocation="/aevoraseo",
            workspace=WorkspaceBehavior(
                global_config_paths=["~/.claude/skills/"],
                workspace_config_paths=[".claude/skills/"],
                env_vars=["CLAUDE_HOME"], marker_files=[".claude/"],
            ),
            runtime=rt, smoke_test="node bin/aevoraseo.js doctor",
            known_limitations="OAuth token expiry requires claude auth login",
            status=VerificationStatus.VERIFIED,
            verification_evidence="Fixture-based installation and doctor smoke test verified",
        ),
        PlatformId.CODEX: PlatformSpec(
            id=PlatformId.CODEX, name="Codex",
            tier=PlatformTier.FIRST_PARTY_SKILL,
            install_command="python3 scripts/install_skill.py --host codex --setup",
            skill_file_location="~/.agents/skills/aevoraseo/",
            invocation="$aevoraseo",
            workspace=WorkspaceBehavior(
                global_config_paths=["~/.agents/skills/"],
                workspace_config_paths=[".agents/skills/"],
                marker_files=[".agents/"],
            ),
            runtime=rt, smoke_test="node bin/aevoraseo.js doctor",
            known_limitations="Sandbox execution; network access may be restricted",
            status=VerificationStatus.VERIFIED,
            verification_evidence="Fixture-based installation and doctor smoke test verified",
        ),
        PlatformId.HERMES: PlatformSpec(
            id=PlatformId.HERMES, name="Hermes Agent",
            tier=PlatformTier.FIRST_PARTY_SKILL,
            install_command="python3 scripts/install_skill.py --host hermes --setup",
            skill_file_location="~/.hermes/skills/aevoraseo/",
            invocation="/aevoraseo",
            workspace=WorkspaceBehavior(
                global_config_paths=["~/.hermes/skills/"],
                env_vars=["HERMES_HOME"], marker_files=[".hermes/"],
            ),
            runtime=rt, smoke_test="node bin/aevoraseo.js doctor",
            known_limitations="Named profiles need --profile-home; skill scanner may flag files",
            status=VerificationStatus.VERIFIED,
            verification_evidence="Fixture-based installation and doctor smoke test verified",
        ),
        PlatformId.OPENCLAW: PlatformSpec(
            id=PlatformId.OPENCLAW, name="OpenClaw",
            tier=PlatformTier.FIRST_PARTY_SKILL,
            install_command="python3 scripts/install_skill.py --host openclaw --setup",
            skill_file_location="~/.openclaw/skills/aevoraseo/",
            invocation="openclaw skills list",
            workspace=WorkspaceBehavior(
                global_config_paths=["~/.openclaw/skills/"],
                env_vars=["OPENCLAW_STATE_DIR"], marker_files=[".openclaw/"],
            ),
            runtime=rt, smoke_test="node bin/aevoraseo.js doctor",
            known_limitations="Sandboxed agents need Python inside execution environment",
            status=VerificationStatus.VERIFIED,
            verification_evidence="Fixture-based installation and doctor smoke test verified",
        ),
        PlatformId.AIDER: PlatformSpec(
            id=PlatformId.AIDER, name="aider",
            tier=PlatformTier.PROJECT_INSTRUCTION,
            install_command="Copy .aider.conf.yml to project root",
            skill_file_location=".aider.conf.yml + .aider.conventions.md",
            invocation="aider --read SKILL.md",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".aider.conf.yml"],
                marker_files=[".aider.conf.yml"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="No native skill folder; uses --read directive and conventions file",
            status=VerificationStatus.DOCUMENTED,
        ),
        PlatformId.COPILOT: PlatformSpec(
            id=PlatformId.COPILOT, name="Copilot CLI",
            tier=PlatformTier.PROJECT_INSTRUCTION,
            install_command="Copy .github/copilot-instructions.md",
            skill_file_location=".github/copilot-instructions.md",
            invocation="@workspace in Copilot Chat",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".github/copilot-instructions.md"],
                marker_files=[".github/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Reads project instructions; no native skill registration",
            status=VerificationStatus.DOCUMENTED,
        ),
        PlatformId.GEMINI_CLI: PlatformSpec(
            id=PlatformId.GEMINI_CLI, name="Gemini CLI",
            tier=PlatformTier.PROJECT_INSTRUCTION,
            install_command="Copy GEMINI.md or .gemini/ instructions",
            skill_file_location="GEMINI.md or .gemini/settings.json",
            invocation="gemini in terminal",
            workspace=WorkspaceBehavior(
                workspace_config_paths=["GEMINI.md", ".gemini/"],
                marker_files=["GEMINI.md", ".gemini/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Reads project-level markdown; no standalone skill folder",
            status=VerificationStatus.DOCUMENTED,
        ),
        PlatformId.DROID: PlatformSpec(
            id=PlatformId.DROID, name="droid",
            tier=PlatformTier.PROJECT_INSTRUCTION,
            install_command="Copy .factory/skills/aevoraseo/",
            skill_file_location=".factory/skills/aevoraseo/",
            invocation="droid invoke aevoraseo",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".factory/skills/"],
                marker_files=[".factory/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Platform documentation limited; skill format unconfirmed",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.KILOCODE: PlatformSpec(
            id=PlatformId.KILOCODE, name="Kilocode CLI",
            tier=PlatformTier.CLI_INTEGRATION,
            install_command="Copy .kilocode/skills/aevoraseo/",
            skill_file_location=".kilocode/skills/aevoraseo/",
            invocation="kilocode skill run aevoraseo",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".kilocode/skills/"],
                marker_files=[".kilocode/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Platform documentation limited",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.OPENCODE: PlatformSpec(
            id=PlatformId.OPENCODE, name="OpenCode CLI",
            tier=PlatformTier.CLI_INTEGRATION,
            install_command="Copy .opencode/skills/aevoraseo/",
            skill_file_location=".opencode/skills/aevoraseo/",
            invocation="opencode skill aevoraseo",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".opencode/skills/"],
                marker_files=[".opencode/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Platform documentation limited",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.QWEN: PlatformSpec(
            id=PlatformId.QWEN, name="Qwen",
            tier=PlatformTier.CLI_INTEGRATION,
            install_command="Copy .qwen/skills/aevoraseo/",
            skill_file_location=".qwen/skills/aevoraseo/",
            invocation="qwen skill aevoraseo",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".qwen/skills/"],
                marker_files=[".qwen/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Platform documentation limited",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.JCODE: PlatformSpec(
            id=PlatformId.JCODE, name="JCODE",
            tier=PlatformTier.CLI_INTEGRATION,
            install_command="Register in JCODE IDE skills",
            skill_file_location=".jcode/skills/aevoraseo/",
            invocation="JCODE IDE skill picker",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".jcode/skills/"],
                marker_files=[".jcode/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="IDE-based; CLI access may vary",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.JCODE_CLI: PlatformSpec(
            id=PlatformId.JCODE_CLI, name="jcode CLI",
            tier=PlatformTier.CLI_INTEGRATION,
            install_command="Copy to .jcode/skills/",
            skill_file_location=".jcode/skills/aevoraseo/",
            invocation="jcode skill aevoraseo",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".jcode/skills/"],
                marker_files=[".jcode/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Command-line variant of JCODE",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.JUNI: PlatformSpec(
            id=PlatformId.JUNI, name="juni CLI",
            tier=PlatformTier.CLI_INTEGRATION,
            install_command="Copy .juni/skills/aevoraseo/",
            skill_file_location=".juni/skills/aevoraseo/",
            invocation="juni skill aevoraseo",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".juni/skills/"],
                marker_files=[".juni/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Platform documentation limited",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.KIRO: PlatformSpec(
            id=PlatformId.KIRO, name="Kiro",
            tier=PlatformTier.PROJECT_INSTRUCTION,
            install_command="Copy .kiro/skills/aevoraseo/",
            skill_file_location=".kiro/skills/aevoraseo/",
            invocation="Kiro workspace instructions",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".kiro/skills/"],
                marker_files=[".kiro/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Platform documentation limited; workspace instruction format",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.PRIME_AGENT: PlatformSpec(
            id=PlatformId.PRIME_AGENT, name="prime-agent",
            tier=PlatformTier.CLI_INTEGRATION,
            install_command="Copy .prime/skills/aevoraseo/",
            skill_file_location=".prime/skills/aevoraseo/",
            invocation="prime-agent skill aevoraseo",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".prime/skills/"],
                marker_files=[".prime/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Platform documentation limited",
            status=VerificationStatus.NOT_VERIFIED,
        ),
        PlatformId.CAI: PlatformSpec(
            id=PlatformId.CAI, name="cai",
            tier=PlatformTier.CLI_INTEGRATION,
            install_command="Copy .cai/skills/aevoraseo/",
            skill_file_location=".cai/skills/aevoraseo/",
            invocation="cai skill aevoraseo",
            workspace=WorkspaceBehavior(
                workspace_config_paths=[".cai/skills/"],
                marker_files=[".cai/"],
            ),
            runtime=rt, smoke_test="python scripts/run.py doctor",
            known_limitations="Platform documentation limited",
            status=VerificationStatus.NOT_VERIFIED,
        ),
    }


_REGISTRY = _build_registry()

_STRING_MAP = {p.value: p for p in PlatformId}
_STRING_MAP.update({
    "claude": PlatformId.CLAUDE_CODE,
    "chatgpt": PlatformId.AGENT,
    "work": PlatformId.AGENT,
    "gemini": PlatformId.GEMINI_CLI,
    "openclaw": PlatformId.OPENCLAW,
    "prime": PlatformId.PRIME_AGENT,
})


def get_platform_registry() -> Dict[PlatformId, PlatformSpec]:
    """Return the full platform registry."""
    return dict(_REGISTRY)


def get_platform(platform_id: PlatformId) -> PlatformSpec:
    """Return the specification for a single platform."""
    return _REGISTRY[platform_id]


def get_all_platforms() -> List[PlatformSpec]:
    """Return all platform specs in registration order."""
    return list(_REGISTRY.values())


def platform_from_string(name: str) -> Optional[PlatformId]:
    """Map a CLI string to a PlatformId, or None if unrecognized."""
    return _STRING_MAP.get(name.lower().strip())
