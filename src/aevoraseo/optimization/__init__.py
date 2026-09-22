"""
AevoraSEO Content & Optimization Intelligence package.
"""

from .analyzer import analyze_target_optimization
from .comparison import compare_optimization_snapshots
from .models import (
    ContentBrief,
    EditorialOutline,
    OptimizationDiff,
    OptimizationResult,
    OptimizationScore,
)
from .persistence import (
    load_optimization_snapshot,
    save_optimization_snapshot,
)

__all__ = [
    "analyze_target_optimization",
    "compare_optimization_snapshots",
    "OptimizationResult",
    "OptimizationDiff",
    "ContentBrief",
    "EditorialOutline",
    "OptimizationScore",
    "save_optimization_snapshot",
    "load_optimization_snapshot",
]
