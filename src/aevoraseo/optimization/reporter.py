"""
Multi-format reporting for AevoraSEO Content & Optimization Intelligence.
Formats: Terminal, Markdown, JSON, and CSV with formula injection defense.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List

from .models import (
    OptimizationDiff,
    OptimizationResult,
)


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


def generate_terminal_report(result: OptimizationResult, use_color: bool = True) -> str:
    """Generate professional terminal presentation with optional ANSI styling."""
    c_bold = "\033[1m" if use_color else ""
    c_green = "\033[32m" if use_color else ""
    c_cyan = "\033[36m" if use_color else ""
    c_yellow = "\033[33m" if use_color else ""
    c_red = "\033[31m" if use_color else ""
    c_dim = "\033[2m" if use_color else ""
    c_reset = "\033[0m" if use_color else ""

    score = result.score
    headline = score.get("headline", 0.0)

    score_color = c_green if headline >= 75.0 else (c_yellow if headline >= 50.0 else c_red)

    lines = [
        f"\n{c_bold}{c_cyan}======================================================================{c_reset}",
        f"{c_bold}  AEVORASEO CONTENT & OPTIMIZATION INTELLIGENCE REPORT{c_reset}",
        f"{c_cyan}======================================================================{c_reset}",
        f"  {c_bold}Target URL:{c_reset}      {result.target_url}",
        f"  {c_bold}Brand Name:{c_reset}      {result.brand_name}",
        f"  {c_bold}Pages Audited:{c_reset}   {result.pages_analyzed}",
        f"  {c_bold}Created At:{c_reset}      {result.created_at}",
        f"  {c_bold}Confidence:{c_reset}      {score.get('confidence', 'low').upper()}",
        "",
        f"  {c_bold}HEADLINE CONTENT SCORE:{c_reset} {score_color}{c_bold}{headline:.1f} / 100{c_reset}",
        f"  {c_dim}------------------------------------------------------------------{c_reset}",
        f"  * Metadata & Heading Architecture:  {score.get('metadata_heading_score', 0.0):.1f} / 25.0",
        f"  * Content Quality & Answer Depth:   {score.get('content_quality_depth_score', 0.0):.1f} / 25.0",
        f"  * Topic Cluster & Link Health:      {score.get('internal_link_cluster_score', 0.0):.1f} / 25.0",
        f"  * Structured Data & Schema Coverage:{score.get('schema_structured_score', 0.0):.1f} / 25.0",
        "",
    ]

    # Deductions
    deductions = score.get("deductions", [])
    if deductions:
        lines.append(f"  {c_bold}Priority Deductions:{c_reset}")
        for d in deductions[:5]:
            lines.append(f"    {c_red}-{d.get('points', 0.0):.1f} pts{c_reset} — {d.get('reason')}")
        lines.append("")

    # Direct answer opportunities
    answers = result.direct_answer_opportunities
    if answers:
        lines.append(f"  {c_bold}Direct Answer & Definition Opportunities ({len(answers)}):{c_reset}")
        for a in answers[:3]:
            mark = f"{c_green}[FOUND]{c_reset}" if a.get("is_answered") else f"{c_yellow}[TARGET]{c_reset}"
            lines.append(f"    {mark} {a.get('question_or_topic')} ({a.get('target_format')})")
            if not a.get("is_answered"):
                lines.append(f"      {c_dim}Action: {a.get('draft_answer_blueprint')[:90]}...{c_reset}")
        lines.append("")

    # Topic clusters
    clusters = result.topic_clusters
    if clusters:
        lines.append(f"  {c_bold}Topic Clusters & Pillar Mapping ({len(clusters)}):{c_reset}")
        for c in clusters[:3]:
            lines.append(f"    * {c_bold}{c.get('topic_name')}{c_reset} (Health: {c.get('cluster_health_score', 0):.0f}%)")
            lines.append(f"      Pillar: {c.get('pillar_url') or 'None'}")
            lines.append(f"      Spokes: {len(c.get('spoke_urls', []))} pages linked")
        lines.append("")

    # Orphan pages
    if result.orphan_pages:
        lines.append(f"  {c_bold}{c_red}Orphan Pages Detected ({len(result.orphan_pages)}):{c_reset}")
        for o in result.orphan_pages[:3]:
            lines.append(f"    ! {o}")
        lines.append("")

    # Strategic Roadmap
    if result.recommendations:
        lines.append(f"  {c_bold}Phased Optimization Roadmap:{c_reset}")
        for r in result.recommendations[:4]:
            lines.append(f"    [{r.get('timeframe')}] {c_bold}{r.get('action')}{c_reset} ({r.get('impact')} impact)")
        lines.append("")

    lines.append(f"{c_cyan}======================================================================{c_reset}\n")
    return "\n".join(lines)


def generate_markdown_report(result: OptimizationResult) -> str:
    """Generate comprehensive GitHub-flavored Markdown report."""
    score = result.score
    headline = score.get("headline", 0.0)

    lines = [
        f"# AevoraSEO Content & Optimization Intelligence Report",
        "",
        f"- **Target URL:** `{result.target_url}`",
        f"- **Brand Name:** {result.brand_name}",
        f"- **Pages Analyzed:** {result.pages_analyzed}",
        f"- **Generated At:** {result.created_at}",
        f"- **Confidence:** {score.get('confidence', 'low').upper()}",
        "",
        f"## Optimization Score: {headline:.1f} / 100",
        "",
        f"| Dimension | Score | Max Points |",
        f"|---|---|---|",
        f"| Metadata & Heading Architecture | {score.get('metadata_heading_score', 0.0):.1f} | 25.0 |",
        f"| Content Quality & Answer Depth | {score.get('content_quality_depth_score', 0.0):.1f} | 25.0 |",
        f"| Topic Cluster & Internal Link Health | {score.get('internal_link_cluster_score', 0.0):.1f} | 25.0 |",
        f"| Structured Data & Schema Coverage | {score.get('schema_structured_score', 0.0):.1f} | 25.0 |",
        "",
    ]

    deductions = score.get("deductions", [])
    if deductions:
        lines.extend([
            "### Identified Penalties & Deficiencies",
            "",
            "| Dimension | Deduction | Reason |",
            "|---|---|---|",
        ])
        for d in deductions:
            lines.append(f"| {d.get('dimension')} | -{d.get('points', 0.0):.1f} pts | {d.get('reason')} |")
        lines.append("")

    # Direct answer opportunities
    if result.direct_answer_opportunities:
        lines.extend([
            "## Direct Answer & Definition Opportunities",
            "",
            "| URL | Question / Topic | Format | Status | Blueprint Guidance |",
            "|---|---|---|---|---|",
        ])
        for a in result.direct_answer_opportunities[:10]:
            status = "Answered" if a.get("is_answered") else "**Unanswered Target**"
            lines.append(
                f"| `{a.get('url')}` | {a.get('question_or_topic')} | {a.get('target_format')} | {status} | {a.get('draft_answer_blueprint')} |"
            )
        lines.append("")

    # Topic clusters
    if result.topic_clusters:
        lines.extend([
            "## Topic Clusters & Pillar Architecture",
            "",
            "| Cluster Name | Health Score | Pillar URL | Supporting Spokes |",
            "|---|---|---|---|",
        ])
        for c in result.topic_clusters:
            spokes_preview = f"{len(c.get('spoke_urls', []))} spokes"
            lines.append(
                f"| **{c.get('topic_name')}** | {c.get('cluster_health_score', 0):.0f}% | `{c.get('pillar_url') or 'None'}` | {spokes_preview} |"
            )
        lines.append("")

    # Content Briefs
    if result.content_briefs:
        lines.extend([
            "## Content Briefs & Outlines",
            "",
        ])
        for b in result.content_briefs:
            lines.extend([
                f"### Brief: `{b.get('url')}`",
                f"- **Primary Query:** `{b.get('primary_query')}` ({b.get('search_intent')} intent)",
                f"- **Target Word Count:** {b.get('target_word_count')} words",
                f"- **Recommended Schema:** `{b.get('recommended_schema')}`",
                f"- **Required Sections:** {', '.join(b.get('required_sections', []))}",
                f"- **Editorial Guidance:** {b.get('editorial_guidance')}",
                "",
            ])

    # 30/60/90-Day Roadmap
    if result.roadmap_items:
        lines.extend([
            "## Phased 30 / 60 / 90-Day Optimization Roadmap",
            "",
            "| Timeframe | Phase | Action | Impact | Dependencies |",
            "|---|---|---|---|---|",
        ])
        for r in result.roadmap_items:
            deps = ", ".join(r.get("dependencies", [])) or "None"
            lines.append(f"| {r.get('timeframe')} | {r.get('phase_name')} | {r.get('action')} | **{r.get('expected_impact')}** | {deps} |")
        lines.append("")

    return "\n".join(lines)


def generate_csv_reports(result: OptimizationResult, out_dir: Path) -> None:
    """Generate all CSV exports with mandatory formula-injection protection."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. content-recommendations.csv
    recs_path = out_dir / "content-recommendations.csv"
    with open(recs_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "title_status", "title_rec", "meta_status", "meta_rec", "h1_count", "heading_rec"])
        meta_map = {m.get("url"): m for m in result.meta_audits}
        heading_map = {h.get("url"): h for h in result.heading_audits}
        for t in result.title_audits:
            u = t.get("url", "")
            m = meta_map.get(u, {})
            h = heading_map.get(u, {})
            writer.writerow([
                sanitize_csv_cell(u),
                sanitize_csv_cell(t.get("status")),
                sanitize_csv_cell(t.get("recommendation")),
                sanitize_csv_cell(m.get("status")),
                sanitize_csv_cell(m.get("recommendation")),
                sanitize_csv_cell(h.get("h1_count")),
                sanitize_csv_cell(h.get("recommendation")),
            ])

    # 2. content-briefs.csv
    briefs_path = out_dir / "content-briefs.csv"
    with open(briefs_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["brief_id", "url", "primary_query", "search_intent", "target_word_count", "recommended_schema"])
        for b in result.content_briefs:
            writer.writerow([
                sanitize_csv_cell(b.get("brief_id")),
                sanitize_csv_cell(b.get("url")),
                sanitize_csv_cell(b.get("primary_query")),
                sanitize_csv_cell(b.get("search_intent")),
                sanitize_csv_cell(b.get("target_word_count")),
                sanitize_csv_cell(b.get("recommended_schema")),
            ])

    # 3. direct-answers.csv
    answers_path = out_dir / "direct-answers.csv"
    with open(answers_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "question_or_topic", "opportunity_type", "target_format", "is_answered", "draft_answer_blueprint"])
        for a in result.direct_answer_opportunities:
            writer.writerow([
                sanitize_csv_cell(a.get("url")),
                sanitize_csv_cell(a.get("question_or_topic")),
                sanitize_csv_cell(a.get("opportunity_type")),
                sanitize_csv_cell(a.get("target_format")),
                sanitize_csv_cell(a.get("is_answered")),
                sanitize_csv_cell(a.get("draft_answer_blueprint")),
            ])

    # 4. internal-links.csv
    links_path = out_dir / "internal-links.csv"
    with open(links_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["source_url", "target_url", "recommended_anchor", "rationale", "link_type"])
        for l in result.internal_link_recommendations:
            writer.writerow([
                sanitize_csv_cell(l.get("source_url")),
                sanitize_csv_cell(l.get("target_url")),
                sanitize_csv_cell(l.get("recommended_anchor")),
                sanitize_csv_cell(l.get("rationale")),
                sanitize_csv_cell(l.get("link_type")),
            ])


def generate_diff_terminal_report(diff: OptimizationDiff) -> str:
    """Generate terminal presentation for snapshot comparison."""
    lines = [
        f"\n======================================================================",
        f"  AEVORASEO CONTENT OPTIMIZATION SNAPSHOT COMPARISON",
        f"======================================================================",
        f"  Target:        {diff.target_url}",
        f"  Before:        {diff.before_snapshot_id} (Score: {diff.score_before:.1f}/100, {diff.confidence_before})",
        f"  After:         {diff.after_snapshot_id} (Score: {diff.score_after:.1f}/100, {diff.confidence_after})",
        f"  Score Delta:   {diff.score_delta:+.1f} points",
        "",
        f"  Dimension Deltas:",
        f"    * Metadata & Heading:     {diff.dimension_deltas.get('metadata_heading_delta', 0.0):+.1f}",
        f"    * Content Quality Depth:  {diff.dimension_deltas.get('content_quality_depth_delta', 0.0):+.1f}",
        f"    * Topic Clusters & Links: {diff.dimension_deltas.get('internal_link_cluster_delta', 0.0):+.1f}",
        f"    * Schema & Structured:    {diff.dimension_deltas.get('schema_structured_delta', 0.0):+.1f}",
        "",
        f"  Transition Summary:",
    ]
    for k, v in diff.transition_summary.items():
        lines.append(f"    - {k.replace('_', ' ').title()}: {v}")

    if diff.resolved_issues:
        lines.append(f"\n  Resolved Issues ({len(diff.resolved_issues)}):")
        for r in diff.resolved_issues[:5]:
            lines.append(f"    [OK] {r.get('url')} - {r.get('issue')}")

    if diff.new_issues:
        lines.append(f"\n  New Issues / Regressions ({len(diff.new_issues)}):")
        for i in diff.new_issues[:5]:
            lines.append(f"    [!]  {i.get('url')} - {i.get('issue')}")

    lines.append("======================================================================\n")
    return "\n".join(lines)


def generate_diff_markdown_report(diff: OptimizationDiff) -> str:
    """Generate Markdown presentation for snapshot comparison."""
    lines = [
        f"# Content Optimization Evolution & Comparison Report",
        "",
        f"- **Target URL:** `{diff.target_url}`",
        f"- **Before Snapshot:** `{diff.before_snapshot_id}` (Score: {diff.score_before:.1f})",
        f"- **After Snapshot:** `{diff.after_snapshot_id}` (Score: {diff.score_after:.1f})",
        f"- **Score Delta:** **{diff.score_delta:+.1f} points**",
        "",
        f"## Dimension Deltas",
        f"| Dimension | Delta |",
        f"|---|---|",
        f"| Metadata & Heading Architecture | {diff.dimension_deltas.get('metadata_heading_delta', 0.0):+.1f} |",
        f"| Content Quality & Answer Depth | {diff.dimension_deltas.get('content_quality_depth_delta', 0.0):+.1f} |",
        f"| Topic Cluster & Internal Links | {diff.dimension_deltas.get('internal_link_cluster_delta', 0.0):+.1f} |",
        f"| Structured Data & Schema Coverage | {diff.dimension_deltas.get('schema_structured_delta', 0.0):+.1f} |",
        "",
        f"## Transition Summary",
        f"| Transition Metric | Value |",
        f"|---|---|",
    ]
    for k, v in diff.transition_summary.items():
        lines.append(f"| {k.replace('_', ' ').title()} | {v} |")
    lines.append("")

    if diff.resolved_issues:
        lines.extend([
            f"## Resolved Deficiencies ({len(diff.resolved_issues)})",
            "",
            "| URL | Resolved Issue |",
            "|---|---|",
        ])
        for r in diff.resolved_issues:
            lines.append(f"| `{r.get('url')}` | {r.get('issue')} |")
        lines.append("")

    if diff.new_issues:
        lines.extend([
            f"## Newly Introduced Issues ({len(diff.new_issues)})",
            "",
            "| URL | Issue |",
            "|---|---|",
        ])
        for i in diff.new_issues:
            lines.append(f"| `{i.get('url')}` | {i.get('issue')} |")
        lines.append("")

    return "\n".join(lines)
