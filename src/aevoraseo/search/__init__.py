"""
AevoraSEO Search, Local & Commercial Intelligence Subsystem.
"""

from .analyzer import analyze_search_snapshot, analyze_target_search
from .comparison import compare_search_snapshots
from .models import (
    CannibalizationCandidate,
    CommercialJourneyAnalysis,
    ComparisonSupportAnalysis,
    LocalSignalAnalysis,
    PageIntentAnalysis,
    SearchCommercialAnalysisResult,
    SearchCommercialDiffResult,
    SearchCommercialScore,
    SearchIntent,
)
from .reporter import export_reports, generate_markdown_report, generate_terminal_report

__all__ = [
    "SearchIntent",
    "PageIntentAnalysis",
    "CannibalizationCandidate",
    "LocalSignalAnalysis",
    "CommercialJourneyAnalysis",
    "ComparisonSupportAnalysis",
    "SearchCommercialScore",
    "SearchCommercialAnalysisResult",
    "SearchCommercialDiffResult",
    "analyze_search_snapshot",
    "analyze_target_search",
    "compare_search_snapshots",
    "generate_terminal_report",
    "generate_markdown_report",
    "export_reports",
]
