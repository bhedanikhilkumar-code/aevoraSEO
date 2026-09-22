"""
Temporal comparison engine for AevoraSEO Search, Local & Commercial Intelligence.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .models import SearchCommercialDiffResult
from .persistence import load_search_snapshot, save_search_diff


def sanitize_csv_cell(value: Any) -> str:
    """Sanitize CSV cells to prevent formula injection attacks."""
    if value is None:
        return ""
    s = str(value)
    if s.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{s}"
    stripped = s.lstrip()
    if stripped.startswith(("=", "+", "-", "@")):
        return f"'{s}"
    return s


def load_snapshot_data(target: Path) -> Dict[str, Any]:
    """Load snapshot data from directory JSON or SQLite database."""
    target_path = Path(target)
    if target_path.is_file() and target_path.suffix.lower() == ".json":
        return json.loads(target_path.read_text(encoding="utf-8"))

    if target_path.is_dir():
        json_file = target_path / "search-commercial.json"
        if json_file.exists():
            return json.loads(json_file.read_text(encoding="utf-8"))

        sqlite_file = target_path / "search_commercial.sqlite3"
        if sqlite_file.exists():
            data = load_search_snapshot(sqlite_file, target_path.name)
            if data:
                return data

    raise ValueError(f"Could not load search intelligence snapshot from {target}")


def compare_search_snapshots(
    before_target: Path,
    after_target: Path,
    out_dir: Optional[Path] = None,
) -> SearchCommercialDiffResult:
    """
    Compares two Search & Commercial snapshots to calculate score deltas,
    intent shifts, resolved/new cannibalizations, and commercial improvements.
    """
    before_data = load_snapshot_data(before_target)
    after_data = load_snapshot_data(after_target)

    before_id = before_data.get("snapshot_id") or Path(before_target).name
    after_id = after_data.get("snapshot_id") or Path(after_target).name
    target_url = after_data.get("target_url") or before_data.get("target_url") or ""

    score_before_obj = before_data.get("score", {})
    score_after_obj = after_data.get("score", {})
    score_before = float(score_before_obj.get("headline", 0.0))
    score_after = float(score_after_obj.get("headline", 0.0))
    score_delta = round(score_after - score_before, 1)

    # 1. Compare page intents
    before_intents: Dict[str, Dict[str, Any]] = {p["url"]: p for p in before_data.get("page_intents", [])}
    after_intents: Dict[str, Dict[str, Any]] = {p["url"]: p for p in after_data.get("page_intents", [])}

    intent_transitions: List[Dict[str, Any]] = []
    all_urls = sorted(set(before_intents.keys()).union(set(after_intents.keys())))

    for u in all_urls:
        if u in before_intents and u in after_intents:
            b_int = before_intents[u].get("primary_intent", "")
            a_int = after_intents[u].get("primary_intent", "")
            if b_int != a_int:
                intent_transitions.append({
                    "url": u,
                    "status": "INTENT_CHANGED",
                    "before_intent": b_int,
                    "after_intent": a_int,
                })
        elif u not in before_intents:
            intent_transitions.append({
                "url": u,
                "status": "ADDED",
                "after_intent": after_intents[u].get("primary_intent", ""),
            })
        else:
            intent_transitions.append({
                "url": u,
                "status": "REMOVED",
                "before_intent": before_intents[u].get("primary_intent", ""),
            })

    # 2. Compare cannibalization issues
    before_cannibal: Dict[str, Dict[str, Any]] = {c["query"]: c for c in before_data.get("cannibalization_issues", [])}
    after_cannibal: Dict[str, Dict[str, Any]] = {c["query"]: c for c in after_data.get("cannibalization_issues", [])}

    new_cannibalizations: List[Dict[str, Any]] = []
    resolved_cannibalizations: List[Dict[str, Any]] = []

    for q, item in after_cannibal.items():
        if q not in before_cannibal:
            new_cannibalizations.append(item)

    for q, item in before_cannibal.items():
        if q not in after_cannibal:
            resolved_cannibalizations.append(item)

    # 3. Compare commercial journeys
    before_comm: Dict[str, Dict[str, Any]] = {c["url"]: c for c in before_data.get("commercial_journeys", [])}
    after_comm: Dict[str, Dict[str, Any]] = {c["url"]: c for c in after_data.get("commercial_journeys", [])}

    commercial_improvements: List[Dict[str, Any]] = []
    commercial_regressions: List[Dict[str, Any]] = []

    for u, a_c in after_comm.items():
        if u in before_comm:
            b_c = before_comm[u]
            # Improvements: CTAs increased, trust added, friction resolved
            b_high_ctas = len(b_c.get("high_intent_ctas", []))
            a_high_ctas = len(a_c.get("high_intent_ctas", []))
            b_friction = len(b_c.get("friction_issues", []))
            a_friction = len(a_c.get("friction_issues", []))
            b_trust = len(b_c.get("trust_signals", []))
            a_trust = len(a_c.get("trust_signals", []))

            if a_high_ctas > b_high_ctas or a_trust > b_trust or a_friction < b_friction:
                commercial_improvements.append({
                    "url": u,
                    "high_intent_ctas_delta": a_high_ctas - b_high_ctas,
                    "trust_signals_delta": a_trust - b_trust,
                    "friction_issues_delta": a_friction - b_friction,
                })
            elif a_friction > b_friction or a_high_ctas < b_high_ctas:
                commercial_regressions.append({
                    "url": u,
                    "friction_issues_delta": a_friction - b_friction,
                    "high_intent_ctas_delta": a_high_ctas - b_high_ctas,
                })

    # 4. Compare local signals
    before_local: Dict[str, Dict[str, Any]] = {l["url"]: l for l in before_data.get("local_signals", [])}
    after_local: Dict[str, Dict[str, Any]] = {l["url"]: l for l in after_data.get("local_signals", [])}
    local_changes: List[Dict[str, Any]] = []

    for u, a_l in after_local.items():
        if u in before_local:
            b_l = before_local[u]
            if not b_l.get("has_local_business_schema") and a_l.get("has_local_business_schema"):
                local_changes.append({"url": u, "change": "LocalBusiness schema added"})
            if not b_l.get("has_clickable_tel") and a_l.get("has_clickable_tel"):
                local_changes.append({"url": u, "change": "Clickable telephone link added"})
            if not b_l.get("has_map_embed_or_link") and a_l.get("has_map_embed_or_link"):
                local_changes.append({"url": u, "change": "Google Maps integration added"})

    transition_summary = {
        "score_delta": score_delta,
        "new_pages_count": sum(1 for t in intent_transitions if t.get("status") == "ADDED"),
        "removed_pages_count": sum(1 for t in intent_transitions if t.get("status") == "REMOVED"),
        "intent_shifts_count": sum(1 for t in intent_transitions if t.get("status") == "INTENT_CHANGED"),
        "resolved_cannibalizations_count": len(resolved_cannibalizations),
        "new_cannibalizations_count": len(new_cannibalizations),
        "commercial_improvements_count": len(commercial_improvements),
        "commercial_regressions_count": len(commercial_regressions),
        "local_upgrades_count": len(local_changes),
    }

    diff_result = SearchCommercialDiffResult(
        before_snapshot_id=before_id,
        after_snapshot_id=after_id,
        target_url=target_url,
        created_at=datetime.now(timezone.utc).isoformat(),
        score_before=score_before,
        score_after=score_after,
        score_delta=score_delta,
        confidence_before=score_before_obj.get("confidence", "low"),
        confidence_after=score_after_obj.get("confidence", "low"),
        intent_transitions=intent_transitions,
        new_cannibalizations=new_cannibalizations,
        resolved_cannibalizations=resolved_cannibalizations,
        commercial_improvements=commercial_improvements,
        commercial_regressions=commercial_regressions,
        local_signal_changes=local_changes,
        transition_summary=transition_summary,
    )

    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        # JSON
        (out_dir / "search_comparison.json").write_text(
            json.dumps(diff_result.to_dict(), indent=2), encoding="utf-8"
        )
        # CSV
        csv_lines = ["metric,value"]
        for k, v in transition_summary.items():
            csv_lines.append(f"{sanitize_csv_cell(k)},{sanitize_csv_cell(v)}")
        (out_dir / "search_comparison.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8-sig")

        # Markdown
        md_lines = [
            f"# Search & Commercial Intelligence Diff — {target_url}",
            "",
            f"- **Before Snapshot**: {before_id} ({score_before:.1f}/100)",
            f"- **After Snapshot**:  {after_id} ({score_after:.1f}/100)",
            f"- **Score Delta**:     {score_delta:+.1f} points",
            "",
            "## Transition Summary",
            "",
            "| Metric | Count |",
            "|---|---|",
        ]
        for k, v in transition_summary.items():
            md_lines.append(f"| {k.replace('_', ' ').title()} | {v} |")

        if resolved_cannibalizations:
            md_lines.extend([
                "",
                "## Resolved Keyword Cannibalizations",
                "",
                "| Query | Intent | Recommendation |",
                "|---|---|---|",
            ])
            for rc in resolved_cannibalizations:
                md_lines.append(f"| {rc.get('query')} | {rc.get('intent')} | {rc.get('recommendation')} |")

        if new_cannibalizations:
            md_lines.extend([
                "",
                "## New Keyword Cannibalization Warnings",
                "",
                "| Query | Intent | Risk Level | Competing URLs |",
                "|---|---|---|---|",
            ])
            for nc in new_cannibalizations:
                urls = "<br>".join(nc.get("competing_urls", []))
                md_lines.append(f"| {nc.get('query')} | {nc.get('intent')} | {nc.get('risk_level')} | {urls} |")

        (out_dir / "search_comparison.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

        # Save diff to SQLite if available
        db_path = out_dir / "search_commercial.sqlite3"
        save_search_diff(db_path, diff_result)

    return diff_result
