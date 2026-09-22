"""AevoraSEO — website crawling, readable content and SEO evidence."""

__version__ = "1.0.0"
__all__ = [
    "Config",
    "Crawler",
    "analyze_search_snapshot",
    "analyze_target_search",
    "compare_search_snapshots",
    "__version__",
]


def __getattr__(name):
    if name == "Config":
        from .network import Config

        return Config
    if name == "Crawler":
        from .engine import Crawler

        return Crawler
    if name in ("analyze_search_snapshot", "analyze_target_search", "compare_search_snapshots"):
        from .search import analyze_search_snapshot, analyze_target_search, compare_search_snapshots

        mapping = {
            "analyze_search_snapshot": analyze_search_snapshot,
            "analyze_target_search": analyze_target_search,
            "compare_search_snapshots": compare_search_snapshots,
        }
        return mapping[name]
    raise AttributeError(name)
