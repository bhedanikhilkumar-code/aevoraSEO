"""
AevoraSEO Temporal Entity Snapshot Diff Engine
Compares baseline and subsequent entity snapshots for score changes, entity evolution, and conflict resolution.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import EntityDiffResult
from .persistence import save_entity_diff


def _load_snapshot_data(source: Path) -> Dict[str, Any]:
    """Loads entity analysis dictionary from a JSON file or directory containing entity-report.json."""
    if source.is_dir():
        cand = source / "entity-report.json"
        if cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
        # Fallback to reading sqlite or checking for entity files
        db = source / "entities.sqlite3"
        if db.exists():
            import sqlite3
            conn = sqlite3.connect(str(db))
            try:
                row = conn.execute("SELECT raw_json FROM entity_snapshots ORDER BY created_at DESC LIMIT 1").fetchone()
                if row and row[0]:
                    return json.loads(row[0])
            finally:
                conn.close()
        raise FileNotFoundError(f"No entity-report.json or entities.sqlite3 found in {source}")
    elif source.is_file():
        return json.loads(source.read_text(encoding="utf-8"))
    else:
        raise FileNotFoundError(f"Entity snapshot source not found: {source}")


def compare_entity_snapshots(
    before_path: Path,
    after_path: Path,
    out_dir: Optional[Path] = None
) -> EntityDiffResult:
    """
    Performs deterministic snapshot comparison between before and after entity analysis results.
    """
    before_data = _load_snapshot_data(before_path)
    after_data = _load_snapshot_data(after_path)

    before_score = before_data.get("score", {}).get("headline", 0.0)
    after_score = after_data.get("score", {}).get("headline", 0.0)
    score_delta = round(after_score - before_score, 1)

    before_conf = before_data.get("score", {}).get("confidence", "low")
    after_conf = after_data.get("score", {}).get("confidence", "low")

    # Map nodes by entity_id
    before_nodes = {n["entity_id"]: n for n in before_data.get("nodes", [])}
    after_nodes = {n["entity_id"]: n for n in after_data.get("nodes", [])}

    added_entities: List[Dict[str, Any]] = []
    removed_entities: List[Dict[str, Any]] = []
    modified_entities: List[Dict[str, Any]] = []

    for eid, node in after_nodes.items():
        if eid not in before_nodes:
            added_entities.append(node)
        else:
            b_node = before_nodes[eid]
            # Check for changes in canonical_name or attributes
            if b_node.get("canonical_name") != node.get("canonical_name") or b_node.get("attributes") != node.get("attributes"):
                modified_entities.append({
                    "entity_id": eid,
                    "canonical_name": node.get("canonical_name"),
                    "before_attributes": b_node.get("attributes"),
                    "after_attributes": node.get("attributes"),
                })

    for eid, node in before_nodes.items():
        if eid not in after_nodes:
            removed_entities.append(node)

    # Conflicts diff
    before_conflicts = {c["conflict_id"]: c for c in before_data.get("conflicts", [])}
    after_conflicts = {c["conflict_id"]: c for c in after_data.get("conflicts", [])}

    resolved_conflicts = [c for cid, c in before_conflicts.items() if cid not in after_conflicts]
    new_conflicts = [c for cid, c in after_conflicts.items() if cid not in before_conflicts]

    # SameAs diff
    before_sa = {sa["url"]: sa for sa in before_data.get("same_as_links", [])}
    after_sa = {sa["url"]: sa for sa in after_data.get("same_as_links", [])}

    added_same_as = [sa for url, sa in after_sa.items() if url not in before_sa]
    lost_same_as = [sa for url, sa in before_sa.items() if url not in after_sa]

    target_url = after_data.get("target_url") or before_data.get("target_url") or ""
    created_at = datetime.now(timezone.utc).isoformat()
    b_id = before_path.name
    a_id = after_path.name

    transition_summary = {
        "score_delta": score_delta,
        "added_entities_count": len(added_entities),
        "removed_entities_count": len(removed_entities),
        "modified_entities_count": len(modified_entities),
        "resolved_conflicts_count": len(resolved_conflicts),
        "new_conflicts_count": len(new_conflicts),
        "added_same_as_count": len(added_same_as),
        "lost_same_as_count": len(lost_same_as),
    }

    diff_result = EntityDiffResult(
        before_snapshot_id=b_id,
        after_snapshot_id=a_id,
        target_url=target_url,
        created_at=created_at,
        score_before=before_score,
        score_after=after_score,
        score_delta=score_delta,
        confidence_before=before_conf,
        confidence_after=after_conf,
        added_entities=added_entities,
        removed_entities=removed_entities,
        modified_entities=modified_entities,
        resolved_conflicts=resolved_conflicts,
        new_conflicts=new_conflicts,
        added_same_as=added_same_as,
        lost_same_as=lost_same_as,
        transition_summary=transition_summary,
    )

    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        # JSON output
        (out_dir / "entity-diff.json").write_text(
            json.dumps(diff_result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        # Markdown summary
        md_lines = [
            f"# AevoraSEO Entity Evolution Diff",
            f"",
            f"- **Target URL:** {target_url}",
            f"- **Before Snapshot:** `{b_id}` ({before_score}/100, {before_conf})",
            f"- **After Snapshot:** `{a_id}` ({after_score}/100, {after_conf})",
            f"- **Score Delta:** {score_delta:+.1f} points",
            f"",
            f"## Transition Summary",
            f"",
            f"| Metric | Count |",
            f"|---|---|",
            f"| Added Entities | {len(added_entities)} |",
            f"| Removed Entities | {len(removed_entities)} |",
            f"| Modified Entities | {len(modified_entities)} |",
            f"| Resolved Conflicts | {len(resolved_conflicts)} |",
            f"| New Conflicts | {len(new_conflicts)} |",
            f"| Added SameAs Profiles | {len(added_same_as)} |",
            f"| Lost SameAs Profiles | {len(lost_same_as)} |",
            f"",
        ]
        if resolved_conflicts:
            md_lines.append("## Resolved Conflicts\n")
            for c in resolved_conflicts:
                md_lines.append(f"- **{c.get('conflict_type')}**: {c.get('description')}")
            md_lines.append("")
        if new_conflicts:
            md_lines.append("## New Conflicts\n")
            for c in new_conflicts:
                md_lines.append(f"- **{c.get('conflict_type')}** ({c.get('severity')}): {c.get('description')}")
            md_lines.append("")

        (out_dir / "entity-diff.md").write_text("\n".join(md_lines), encoding="utf-8")

        # SQLite diff persistence
        db_path = out_dir / "entities.sqlite3"
        save_entity_diff(db_path, diff_result)

    return diff_result
