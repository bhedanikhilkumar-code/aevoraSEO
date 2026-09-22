"""
Snapshot-aware Before / After Comparison Engine for Reputation and Backlinks.
Evaluates score deltas, added/lost backlinks, mention changes, and opportunity conversion.
"""

from __future__ import annotations

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

from .backlink_persistence import persist_reputation_diff
from .engine import csv_value
from .network import utcnow


def sanitize_csv_cell(value: Any) -> Any:
    """Neutralize formula injection by prepending single quote if cell starts with risky char."""
    if value is None:
        return ""
    val_str = str(value)
    stripped = val_str.lstrip()
    if stripped and stripped[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val_str}"
    return val_str


def _load_reputation_data(source: Path | str | dict) -> Dict[str, Any]:
    """Resolve reputation dictionary from Path, file, or direct dictionary."""
    if isinstance(source, dict):
        return source
    p = Path(source)
    if p.is_dir():
        rep_file = p / "reputation.json"
        if rep_file.exists():
            return json.loads(rep_file.read_text(encoding="utf-8"))
        # Check subfolder verification
        v_file = p / "verification" / "backlinks.json"
        if v_file.exists():
            return json.loads(v_file.read_text(encoding="utf-8"))
        raise ValueError(f"No reputation.json found in directory: {p}")
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    raise ValueError(f"Invalid reputation source: {source}")


def compare_reputation_snapshots(
    before_input: Path | str | dict,
    after_input: Path | str | dict,
    out_dir: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Compare two reputation assessments over time.
    Calculates score changes, backlink evolution, mention progression, and opportunity conversions.
    """
    before = _load_reputation_data(before_input)
    after = _load_reputation_data(after_input)

    target = after.get("target") or before.get("target", "")
    brand = after.get("brand") or before.get("brand", "")
    diff_id = f"diff-{uuid.uuid4().hex[:8]}"
    compared_at = utcnow()

    before_score = before.get("score")
    after_score = after.get("score")
    score_delta = (
        round(after_score - before_score, 1)
        if before_score is not None and after_score is not None
        else None
    )

    before_confidence = before.get("confidence", "unknown")
    after_confidence = after.get("confidence", "unknown")
    before_status = before.get("score_status", "unknown")
    after_status = after.get("score_status", "unknown")

    # Map backlinks: { (source_url, target_url): link_dict }
    before_links_map = {}
    for s in before.get("sources", []):
        for l in s.get("target_links", []):
            key = (s.get("source_url", ""), l.get("url", ""))
            before_links_map[key] = {
                "source_url": s.get("source_url"),
                "target_url": l.get("url"),
                "publisher_group": s.get("publisher_group"),
                "anchor": l.get("anchor") or l.get("text", ""),
                "rel": l.get("rel", []),
                "is_dofollow": l.get("is_dofollow", True),
                "context": l.get("context", ""),
                "quality_estimate": s.get("quality_estimate"),
            }

    after_links_map = {}
    for s in after.get("sources", []):
        for l in s.get("target_links", []):
            key = (s.get("source_url", ""), l.get("url", ""))
            after_links_map[key] = {
                "source_url": s.get("source_url"),
                "target_url": l.get("url"),
                "publisher_group": s.get("publisher_group"),
                "anchor": l.get("anchor") or l.get("text", ""),
                "rel": l.get("rel", []),
                "is_dofollow": l.get("is_dofollow", True),
                "context": l.get("context", ""),
                "quality_estimate": s.get("quality_estimate"),
            }

    new_backlinks = [after_links_map[k] for k in sorted(after_links_map.keys() - before_links_map.keys())]
    lost_backlinks = [before_links_map[k] for k in sorted(before_links_map.keys() - after_links_map.keys())]
    retained_backlinks = [after_links_map[k] for k in sorted(after_links_map.keys() & before_links_map.keys())]

    # Map mentions: { (source_url, brand_name): mention_dict }
    before_mentions_map = {}
    for s in before.get("sources", []):
        for m in s.get("brand_mentions", []):
            m_name = m.get("name") if isinstance(m, dict) else str(m)
            key = (s.get("source_url", ""), m_name)
            before_mentions_map[key] = {
                "source_url": s.get("source_url"),
                "name": m_name,
                "excerpt": m.get("excerpt", "") if isinstance(m, dict) else "",
                "publisher_group": s.get("publisher_group"),
            }

    after_mentions_map = {}
    for s in after.get("sources", []):
        for m in s.get("brand_mentions", []):
            m_name = m.get("name") if isinstance(m, dict) else str(m)
            key = (s.get("source_url", ""), m_name)
            after_mentions_map[key] = {
                "source_url": s.get("source_url"),
                "name": m_name,
                "excerpt": m.get("excerpt", "") if isinstance(m, dict) else "",
                "publisher_group": s.get("publisher_group"),
            }

    new_mentions = [after_mentions_map[k] for k in sorted(after_mentions_map.keys() - before_mentions_map.keys())]
    lost_mentions = [before_mentions_map[k] for k in sorted(before_mentions_map.keys() - after_mentions_map.keys())]
    retained_mentions = [after_mentions_map[k] for k in sorted(after_mentions_map.keys() & before_mentions_map.keys())]

    # Detect Opportunity Conversions:
    # A source that had brand mentions in 'before' but no links, and now has a backlink in 'after'!
    before_unlinked_sources = {
        s.get("source_url")
        for s in before.get("sources", [])
        if s.get("observed_mention") and not s.get("observed_link")
    }
    opportunity_conversions = []
    for l in new_backlinks:
        if l["source_url"] in before_unlinked_sources:
            opportunity_conversions.append(
                {
                    "source_url": l["source_url"],
                    "target_url": l["target_url"],
                    "type": "unlinked_mention_to_backlink",
                    "anchor": l["anchor"],
                    "note": "Mention successfully converted into verified backlink",
                }
            )

    # Publisher group changes
    before_groups = (before.get("coverage") or {}).get("unique_publisher_groups_with_evidence", 0)
    after_groups = (after.get("coverage") or {}).get("unique_publisher_groups_with_evidence", 0)
    group_delta = after_groups - before_groups

    # Build summary
    summary = {
        "score_delta": score_delta,
        "before_score": before_score,
        "after_score": after_score,
        "before_confidence": before_confidence,
        "after_confidence": after_confidence,
        "new_backlinks_count": len(new_backlinks),
        "lost_backlinks_count": len(lost_backlinks),
        "retained_backlinks_count": len(retained_backlinks),
        "new_mentions_count": len(new_mentions),
        "lost_mentions_count": len(lost_mentions),
        "retained_mentions_count": len(retained_mentions),
        "opportunity_conversions_count": len(opportunity_conversions),
        "publisher_group_delta": group_delta,
    }

    result = {
        "diff_id": diff_id,
        "target": target,
        "brand": brand,
        "compared_at": compared_at,
        "before_checked_at": before.get("checked_at"),
        "after_checked_at": after.get("checked_at"),
        "summary": summary,
        "new_backlinks": new_backlinks,
        "lost_backlinks": lost_backlinks,
        "retained_backlinks": retained_backlinks,
        "new_mentions": new_mentions,
        "lost_mentions": lost_mentions,
        "retained_mentions": retained_mentions,
        "opportunity_conversions": opportunity_conversions,
    }

    # Save outputs if out_dir is provided
    if out_dir:
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # JSON
        (out_path / "reputation_comparison.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # Markdown
        md_content = generate_reputation_diff_markdown(result)
        (out_path / "reputation_comparison.md").write_text(md_content, encoding="utf-8")

        # CSV
        csv_rows = []
        for l in new_backlinks:
            csv_rows.append({
                "change_type": "NEW_BACKLINK",
                "source_url": l["source_url"],
                "target_url": l["target_url"],
                "anchor": l["anchor"],
                "rel": " ".join(l["rel"]),
                "note": f"Dofollow: {l['is_dofollow']}",
            })
        for l in lost_backlinks:
            csv_rows.append({
                "change_type": "LOST_BACKLINK",
                "source_url": l["source_url"],
                "target_url": l["target_url"],
                "anchor": l["anchor"],
                "rel": " ".join(l["rel"]),
                "note": "Backlink no longer observed in capture",
            })
        for m in new_mentions:
            csv_rows.append({
                "change_type": "NEW_MENTION",
                "source_url": m["source_url"],
                "target_url": "",
                "anchor": m["name"],
                "rel": "",
                "note": m["excerpt"][:100],
            })
        for m in lost_mentions:
            csv_rows.append({
                "change_type": "LOST_MENTION",
                "source_url": m["source_url"],
                "target_url": "",
                "anchor": m["name"],
                "rel": "",
                "note": "Mention no longer observed in capture",
            })
        for c in opportunity_conversions:
            csv_rows.append({
                "change_type": "CONVERTED_OPPORTUNITY",
                "source_url": c["source_url"],
                "target_url": c["target_url"],
                "anchor": c["anchor"],
                "rel": "",
                "note": c["note"],
            })

        csv_path = out_path / "reputation_comparison.csv"
        fields = ["change_type", "source_url", "target_url", "anchor", "rel", "note"]
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in csv_rows:
                writer.writerow({k: sanitize_csv_cell(v) for k, v in row.items()})

        # Persist to SQLite
        db_path = out_path / "reputation.sqlite3"
        try:
            persist_reputation_diff(db_path, result)
        except Exception:
            pass

    return result


def generate_reputation_diff_markdown(diff: Dict[str, Any]) -> str:
    """Generate professional GitHub-flavored markdown report of reputation comparison."""
    s = diff["summary"]
    score_delta_str = f"{s['score_delta']:+.1f}" if s["score_delta"] is not None else "N/A"
    lines = [
        f"# Reputation & Backlink Snapshot Comparison — {diff['target']}",
        "",
        f"**Compared At:** {diff['compared_at']}  ",
        f"**Baseline Capture:** {diff.get('before_checked_at', 'N/A')}  ",
        f"**Subsequent Capture:** {diff.get('after_checked_at', 'N/A')}  ",
        "",
        "## Executive Summary",
        "",
        "| Metric | Before | After | Delta |",
        "|---|---|---|---|",
        f"| **Reputation Score** | {s['before_score'] if s['before_score'] is not None else 'withheld'} | {s['after_score'] if s['after_score'] is not None else 'withheld'} | **{score_delta_str}** |",
        f"| **Confidence Level** | {s['before_confidence']} | {s['after_confidence']} | - |",
        f"| **Observed Backlinks** | {s['retained_backlinks_count'] + s['lost_backlinks_count']} | {s['retained_backlinks_count'] + s['new_backlinks_count']} | {s['new_backlinks_count'] - s['lost_backlinks_count']:+d} |",
        f"| **Brand Mentions** | {s['retained_mentions_count'] + s['lost_mentions_count']} | {s['retained_mentions_count'] + s['new_mentions_count']} | {s['new_mentions_count'] - s['lost_mentions_count']:+d} |",
        f"| **Converted Opportunities** | - | {s['opportunity_conversions_count']} | +{s['opportunity_conversions_count']} |",
        f"| **Publisher Groups** | - | - | {s['publisher_group_delta']:+d} |",
        "",
    ]

    if diff.get("opportunity_conversions"):
        lines += [
            "## 🎯 Converted Opportunities (Unlinked Mention → Backlink)",
            "",
            "The following sources previously only mentioned your brand and now directly link to your target pages:",
            "",
        ]
        for c in diff["opportunity_conversions"]:
            lines.append(f"- **{c['source_url']}** → [{c['anchor'] or 'link'}]({c['target_url']})")
        lines.append("")

    if diff.get("new_backlinks"):
        lines += [
            "## 🟢 New Observed Backlinks",
            "",
            "| Source URL | Target URL | Anchor Text | Rel Attributes | Dofollow |",
            "|---|---|---|---|---|",
        ]
        for l in diff["new_backlinks"]:
            rel_str = ", ".join(l["rel"]) if l["rel"] else "standard"
            dofollow_mark = "✅ Yes" if l["is_dofollow"] else "⚠️ No"
            lines.append(f"| {l['source_url']} | {l['target_url']} | {l['anchor'] or '(none)'} | {rel_str} | {dofollow_mark} |")
        lines.append("")

    if diff.get("lost_backlinks"):
        lines += [
            "## 🔴 Lost Backlinks",
            "",
            "| Source URL | Target URL | Anchor Text | Rel Attributes |",
            "|---|---|---|---|",
        ]
        for l in diff["lost_backlinks"]:
            rel_str = ", ".join(l["rel"]) if l["rel"] else "standard"
            lines.append(f"| {l['source_url']} | {l['target_url']} | {l['anchor'] or '(none)'} | {rel_str} |")
        lines.append("")

    if diff.get("new_mentions"):
        lines += [
            "## 💬 New Brand Mentions (Without Link)",
            "",
            "| Source URL | Brand Term | Excerpt |",
            "|---|---|---|",
        ]
        for m in diff["new_mentions"]:
            exc = m["excerpt"].replace("\n", " ")[:120] if m.get("excerpt") else ""
            lines.append(f"| {m['source_url']} | {m['name']} | {exc}... |")
        lines.append("")

    lines += [
        "## Strategic Action Items",
        "",
        "1. **Protect New Links**: Monitor new backlink sources to ensure placement longevity.",
        "2. **Investigate Lost Links**: Review lost backlink URLs for page updates, broken redirects, or editorial removals.",
        "3. **Pursue Unlinked Mentions**: Conduct outreach to newly discovered brand mention publishers to request backlink attribution.",
        "",
        "---",
        "*Report generated by AevoraSEO Reputation Comparison Engine.*",
    ]
    return "\n".join(lines)
