"""Data models for AevoraSEO multi-agent platform compatibility."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class PlatformId(enum.Enum):
    """Identifiers for all supported agent/CLI platforms."""

    AGENT = "agent"
    CLAUDE_CODE = "claude-code"
    CODEX = "codex"
    HERMES = "hermes"
    OPENCLAW = "openclaw"
    AIDER = "aider"
    COPILOT = "copilot"
    GEMINI_CLI = "gemini-cli"
    DROID = "droid"
    KILOCODE = "kilocode"
    OPENCODE = "opencode"
    QWEN = "qwen"
    JCODE = "jcode"
    JCODE_CLI = "jcode-cli"
    JUNI = "juni"
    KIRO = "kiro"
    PRIME_AGENT = "prime-agent"
    CAI = "cai"


class PlatformTier(enum.Enum):
    """Integration depth classification."""

    FIRST_PARTY_SKILL = "first-party-skill"
    PROJECT_INSTRUCTION = "project-instruction"
    CLI_INTEGRATION = "cli-integration"
    GENERIC_ADAPTER = "generic-adapter"


class VerificationStatus(enum.Enum):
    """Evidence-based compatibility status."""

    VERIFIED = "VERIFIED"
    PARTIAL = "PARTIAL"
    DOCUMENTED = "DOCUMENTED"
    NOT_VERIFIED = "NOT VERIFIED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass
class RuntimeRequirements:
    """Runtime prerequisites for the AevoraSEO engine."""

    python_minimum: str = "3.10"
    browser_needed: bool = False
    execution_permission: bool = True
    network_access: bool = True


@dataclass
class WorkspaceBehavior:
    """Config discovery paths and markers for a platform."""

    global_config_paths: List[str] = field(default_factory=list)
    workspace_config_paths: List[str] = field(default_factory=list)
    env_vars: List[str] = field(default_factory=list)
    marker_files: List[str] = field(default_factory=list)
    discovery_notes: str = ""


@dataclass
class PlatformSpec:
    """Complete specification for an agent/CLI platform."""

    id: PlatformId
    name: str
    tier: PlatformTier
    install_command: str
    skill_file_location: str
    invocation: str
    workspace: WorkspaceBehavior
    runtime: RuntimeRequirements
    smoke_test: str
    known_limitations: str
    status: VerificationStatus
    verification_evidence: str = ""


@dataclass
class EnvironmentInspection:
    """Result of inspecting the current execution environment."""

    detected_platform: Optional[str] = None
    workspace_root: str = ""
    config_files_found: List[str] = field(default_factory=list)
    python_version: str = ""
    python_path: str = ""
    aevoraseo_installed: bool = False
    install_receipt_path: str = ""
    isolation_status: str = "unknown"


@dataclass
class AdapterResult:
    """Result of generating platform adapter/config files."""

    platform: PlatformId
    files_written: List[str] = field(default_factory=list)
    instructions: str = ""
    dry_run: bool = False


@dataclass
class VerificationResult:
    """Result of fixture-based platform verification."""

    platform: PlatformId
    status: VerificationStatus
    steps: List[Dict[str, str]] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    evidence: str = ""
