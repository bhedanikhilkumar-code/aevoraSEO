"""AevoraSEO Multi-Agent & Platform Compatibility subsystem."""

from .models import (
    PlatformId,
    PlatformTier,
    VerificationStatus,
    RuntimeRequirements,
    WorkspaceBehavior,
    PlatformSpec,
    EnvironmentInspection,
    AdapterResult,
    VerificationResult,
)
from .registry import (
    get_platform_registry,
    get_platform,
    get_all_platforms,
    platform_from_string,
)
from .detector import detect_environment
from .validator import (
    validate_installation,
    validate_workspace_isolation,
    check_python_compatibility,
)
from .adapter import generate_adapter
from .verifier import verify_platform, verify_all_platforms

__all__ = [
    "PlatformId",
    "PlatformTier",
    "VerificationStatus",
    "RuntimeRequirements",
    "WorkspaceBehavior",
    "PlatformSpec",
    "EnvironmentInspection",
    "AdapterResult",
    "VerificationResult",
    "get_platform_registry",
    "get_platform",
    "get_all_platforms",
    "platform_from_string",
    "detect_environment",
    "validate_installation",
    "validate_workspace_isolation",
    "check_python_compatibility",
    "generate_adapter",
    "verify_platform",
    "verify_all_platforms",
]
