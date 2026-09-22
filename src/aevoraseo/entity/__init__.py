"""
AevoraSEO Entity, Authority & Knowledge Intelligence Subsystem
"""

from .models import (
    EntityType,
    AuthorityPlatform,
    SameAsLink,
    EntityNode,
    EntityEdge,
    EntityConflict,
    EntityScore,
    EntityAnalysisResult,
    EntityDiffResult,
)
from .analyzer import analyze_entity_snapshot, analyze_target_entities
from .comparison import compare_entity_snapshots

__all__ = [
    "EntityType",
    "AuthorityPlatform",
    "SameAsLink",
    "EntityNode",
    "EntityEdge",
    "EntityConflict",
    "EntityScore",
    "EntityAnalysisResult",
    "EntityDiffResult",
    "analyze_entity_snapshot",
    "analyze_target_entities",
    "compare_entity_snapshots",
]
