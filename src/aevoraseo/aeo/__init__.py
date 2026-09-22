"""
AevoraSEO AEO / GEO Intelligence Engine
Deterministic, evidence-backed evaluation of answer readiness, entity clarity,
structured data quality, citation characteristics, and AI crawler accessibility.
"""

from aevoraseo.aeo.models import (
    AEODiffItem,
    AEODiffResult,
    CitationSignal,
    ContentStructureSignal,
    CrawlerAccessSignal,
    EntitySignal,
    ObservedVisibilityRecord,
    PageAEOResult,
    QuestionAnswerSignal,
    SchemaQualitySignal,
    ScoreDeduction,
    ScoreDimension,
    ScoreSignalContribution,
    SnapshotAEOResult,
)
from aevoraseo.aeo.analyzer import (
    analyze_page,
    analyze_snapshot,
    generate_aeo_summary_markdown,
)
from aevoraseo.aeo.comparison import (
    compare_aeo_snapshots,
    generate_aeo_diff_markdown,
)
from aevoraseo.aeo.accessibility import AI_BOT_REGISTRY, evaluate_bot_accessibility
from aevoraseo.aeo.visibility import load_observed_visibility
from aevoraseo.aeo.persistence import (
    init_aeo_db,
    persist_snapshot_aeo,
    persist_aeo_diff,
    query_snapshot_aeo_summary,
)

__all__ = [
    "AEODiffItem",
    "AEODiffResult",
    "AI_BOT_REGISTRY",
    "CitationSignal",
    "ContentStructureSignal",
    "CrawlerAccessSignal",
    "EntitySignal",
    "ObservedVisibilityRecord",
    "PageAEOResult",
    "QuestionAnswerSignal",
    "SchemaQualitySignal",
    "ScoreDeduction",
    "ScoreDimension",
    "ScoreSignalContribution",
    "SnapshotAEOResult",
    "analyze_page",
    "analyze_snapshot",
    "compare_aeo_snapshots",
    "evaluate_bot_accessibility",
    "generate_aeo_diff_markdown",
    "generate_aeo_summary_markdown",
    "init_aeo_db",
    "load_observed_visibility",
    "persist_aeo_diff",
    "persist_snapshot_aeo",
    "query_snapshot_aeo_summary",
]
