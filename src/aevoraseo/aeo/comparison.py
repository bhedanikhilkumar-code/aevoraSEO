"""
AevoraSEO AEO / GEO Snapshot Comparison Engine
Compares AEO/GEO scores across snapshots, computes deltas, categorizes state transitions
(ADDED, REMOVED, IMPROVED, REGRESSED, UNCHANGED), and attributes contributing evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from aevoraseo.aeo.models import AEODiffItem, AEODiffResult
from aevoraseo.aeo.analyzer import analyze_snapshot


def _derive_contributing_evidence(
    before_p: Optional[Dict[str, Any]],
    after_p: Optional[Dict[str, Any]],
) -> List[str]:
    """
    Computes human-readable evidence strings describing why scores changed between snapshots.
    """
    evidence: List[str] = []
    if before_p is None and after_p is not None:
        evidence.append("Page newly discovered in snapshot.")
        return evidence
    if before_p is not None and after_p is None:
        evidence.append("Page removed or not re-observed in snapshot.")
        return evidence

    if not before_p or not after_p:
        return evidence

    # 1. Direct answers delta
    b_ans = sum(1 for q in before_p.questions if q.answer_detected)
    a_ans = sum(1 for q in after_p.questions if q.answer_detected)
    if a_ans > b_ans:
        evidence.append(f"Direct answers increased from {b_ans} to {a_ans}.")
    elif a_ans < b_ans:
        evidence.append(f"Direct answers decreased from {b_ans} to {a_ans}.")

    # 2. Schema delta
    b_schemas = {s.schema_type for s in before_p.schemas if s.valid}
    a_schemas = {s.schema_type for s in after_p.schemas if s.valid}
    added_s = a_schemas - b_schemas
    removed_s = b_schemas - a_schemas
    if added_s:
        evidence.append(f"Schema type(s) added: {', '.join(sorted(added_s))}.")
    if removed_s:
        evidence.append(f"Schema type(s) removed: {', '.join(sorted(removed_s))}.")

    # 3. Heading structure delta
    if not before_p.content_structure.has_h1 and after_p.content_structure.has_h1:
        evidence.append("Primary <h1> heading added.")
    elif before_p.content_structure.has_h1 and not after_p.content_structure.has_h1:
        evidence.append("Primary <h1> heading removed.")

    # 4. Author & timestamp delta
    if not before_p.citations.author and after_p.citations.author:
        evidence.append(f"Author attribution added: {after_p.citations.author}.")
    elif before_p.citations.author and not after_p.citations.author:
        evidence.append("Author attribution removed.")

    # 5. Crawler accessibility delta
    b_blocked = {c.bot_name for c in before_p.crawler_accessibility if c.status == "crawl_restricted"}
    a_blocked = {c.bot_name for c in after_p.crawler_accessibility if c.status == "crawl_restricted"}
    newly_blocked = a_blocked - b_blocked
    unblocked = b_blocked - a_blocked
    if newly_blocked:
        evidence.append(f"AI bot(s) newly restricted: {', '.join(sorted(newly_blocked))}.")
    if unblocked:
        evidence.append(f"AI bot(s) unblocked: {', '.join(sorted(unblocked))}.")

    # 6. Factual density delta
    diff_fd = after_p.citations.factual_density_score - before_p.citations.factual_density_score
    if abs(diff_fd) >= 0.15:
        dir_str = "increased" if diff_fd > 0 else "decreased"
        evidence.append(f"Factual density {dir_str} from {before_p.citations.factual_density_score:.2f} to {after_p.citations.factual_density_score:.2f}.")

    return evidence


def generate_aeo_diff_markdown(diff: AEODiffResult) -> str:
    """
    Renders an engineering-grade markdown comparison report.
    """
    lines = [
        f"# AevoraSEO AEO / GEO Snapshot Comparison",
        f"",
        f"**Before Snapshot**: `{diff.before_snapshot_id}`  ",
        f"**After Snapshot**: `{diff.after_snapshot_id}`  ",
        f"",
        f"---",
        f"",
        f"## Overall Score Trajectory",
        f"",
        f"| Metric | Before | After | Delta | Direction |",
        f"| :--- | :--- | :--- | :--- | :--- |",
        f"| **Average AEO Readiness** | {diff.before_avg_aeo:.1f} | {diff.after_avg_aeo:.1f} | {diff.aeo_delta:+.1f} | {'🟢 Improved' if diff.aeo_delta >= 5 else '🔴 Regressed' if diff.aeo_delta <= -5 else '⚪ Stable'} |",
        f"| **Average GEO Signal** | {diff.before_avg_geo:.1f} | {diff.after_avg_geo:.1f} | {diff.geo_delta:+.1f} | {'🟢 Improved' if diff.geo_delta >= 5 else '🔴 Regressed' if diff.geo_delta <= -5 else '⚪ Stable'} |",
        f"",
        f"---",
        f"",
        f"## Summary of Transitions",
        f"",
        f"- **Added Pages**: {diff.summary.get('added', 0)}",
        f"- **Removed Pages**: {diff.summary.get('removed', 0)}",
        f"- **Improved Pages**: {diff.summary.get('improved', 0)}",
        f"- **Regressed Pages**: {diff.summary.get('regressed', 0)}",
        f"- **Unchanged Pages**: {diff.summary.get('unchanged', 0)}",
        f"",
        f"---",
        f"",
        f"## Page-Level Score Changes",
        f"",
        f"| URL | Metric | Before | After | Delta | State | Contributing Evidence |",
        f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for item in diff.items[:30]:
        ev_str = "; ".join(item.evidence) if item.evidence else "No specific structural shifts"
        lines.append(
            f"| `{item.url}` | {item.metric} | {item.before:.1f} | {item.after:.1f} | {item.delta:+.1f} | **{item.state}** | {ev_str} |"
        )

    return "\n".join(lines)


def compare_aeo_snapshots(
    before_dir: Path | str,
    after_dir: Path | str,
    out_dir: Optional[Path | str] = None,
) -> AEODiffResult:
    """
    Compares two crawl snapshots, analyzes AEO/GEO score evolutions, and exports diff reports.
    """
    res_before = analyze_snapshot(before_dir)
    res_after = analyze_snapshot(after_dir)

    pages_b = {p.url: p for p in res_before.pages}
    pages_a = {p.url: p for p in res_after.pages}

    all_urls = sorted(set(pages_b.keys()) | set(pages_a.keys()))

    diff_items: List[AEODiffItem] = []
    page_transitions: Dict[str, str] = {}
    summary_counts = {"added": 0, "removed": 0, "improved": 0, "regressed": 0, "unchanged": 0}

    for url in all_urls:
        p_b = pages_b.get(url)
        p_a = pages_a.get(url)

        evidence = _derive_contributing_evidence(p_b, p_a)

        if p_b is None and p_a is not None:
            state = "ADDED"
            summary_counts["added"] += 1
            diff_items.append(
                AEODiffItem(
                    url=url,
                    metric="aeo_readiness_score",
                    before=0.0,
                    after=p_a.aeo_readiness_score,
                    delta=p_a.aeo_readiness_score,
                    state=state,
                    evidence=evidence,
                )
            )
            diff_items.append(
                AEODiffItem(
                    url=url,
                    metric="geo_signal_score",
                    before=0.0,
                    after=p_a.geo_signal_score,
                    delta=p_a.geo_signal_score,
                    state=state,
                    evidence=evidence,
                )
            )
            page_transitions[url] = state

        elif p_b is not None and p_a is None:
            state = "REMOVED"
            summary_counts["removed"] += 1
            diff_items.append(
                AEODiffItem(
                    url=url,
                    metric="aeo_readiness_score",
                    before=p_b.aeo_readiness_score,
                    after=0.0,
                    delta=-p_b.aeo_readiness_score,
                    state=state,
                    evidence=evidence,
                )
            )
            diff_items.append(
                AEODiffItem(
                    url=url,
                    metric="geo_signal_score",
                    before=p_b.geo_signal_score,
                    after=0.0,
                    delta=-p_b.geo_signal_score,
                    state=state,
                    evidence=evidence,
                )
            )
            page_transitions[url] = state

        else:
            # Both present
            aeo_delta = round(p_a.aeo_readiness_score - p_b.aeo_readiness_score, 1)
            geo_delta = round(p_a.geo_signal_score - p_b.geo_signal_score, 1)
            primary_delta = aeo_delta

            if primary_delta >= 5.0:
                state = "IMPROVED"
                summary_counts["improved"] += 1
            elif primary_delta <= -5.0:
                state = "REGRESSED"
                summary_counts["regressed"] += 1
            else:
                state = "UNCHANGED"
                summary_counts["unchanged"] += 1

            page_transitions[url] = state

            diff_items.append(
                AEODiffItem(
                    url=url,
                    metric="aeo_readiness_score",
                    before=p_b.aeo_readiness_score,
                    after=p_a.aeo_readiness_score,
                    delta=aeo_delta,
                    state=state,
                    evidence=evidence,
                )
            )
            diff_items.append(
                AEODiffItem(
                    url=url,
                    metric="geo_signal_score",
                    before=p_b.geo_signal_score,
                    after=p_a.geo_signal_score,
                    delta=geo_delta,
                    state=state,
                    evidence=evidence,
                )
            )

    aeo_delta_total = round(res_after.average_aeo_readiness_score - res_before.average_aeo_readiness_score, 1)
    geo_delta_total = round(res_after.average_geo_signal_score - res_before.average_geo_signal_score, 1)

    diff_result = AEODiffResult(
        before_snapshot_id=res_before.snapshot_id,
        after_snapshot_id=res_after.snapshot_id,
        before_avg_aeo=res_before.average_aeo_readiness_score,
        after_avg_aeo=res_after.average_aeo_readiness_score,
        aeo_delta=aeo_delta_total,
        before_avg_geo=res_before.average_geo_signal_score,
        after_avg_geo=res_after.average_geo_signal_score,
        geo_delta=geo_delta_total,
        page_transitions=page_transitions,
        items=diff_items,
        summary=summary_counts,
    )

    if out_dir is not None:
        target_dir = Path(out_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # 1. aeo_comparison.json
        (target_dir / "aeo_comparison.json").write_text(
            json.dumps(diff_result.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        # 2. aeo_comparison.md
        md_content = generate_aeo_diff_markdown(diff_result)
        (target_dir / "aeo_comparison.md").write_text(md_content + "\n", encoding="utf-8")

        # 3. aeo_comparison.csv
        csv_rows = []
        for item in diff_items:
            csv_rows.append({
                "url": item.url,
                "metric": item.metric,
                "before": item.before,
                "after": item.after,
                "delta": item.delta,
                "state": item.state,
                "evidence": "; ".join(item.evidence),
            })
        with (target_dir / "aeo_comparison.csv").open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["url", "metric", "before", "after", "delta", "state", "evidence"])
            writer.writeheader()
            writer.writerows(csv_rows)

    return diff_result
