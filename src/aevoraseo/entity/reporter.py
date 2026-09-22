"""
AevoraSEO Multi-Format Entity & Authority Reporter
Generates terminal, Markdown, JSON, and formula-injection-safe CSV reports.
"""

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import EntityAnalysisResult


def sanitize_csv_cell(value: Any) -> str:
    """Escapes leading spreadsheet formula command characters (=, +, -, @, \\t, \\r) with single quote."""
    if value is None:
        return ""
    val_str = str(value)
    stripped = val_str.lstrip()
    if stripped and stripped[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val_str}"
    return val_str


def generate_terminal_report(result: EntityAnalysisResult, use_color: bool = True) -> str:
    """Renders formatted terminal output."""
    score = result.score
    headline = score.get("headline", 0.0)
    conf = score.get("confidence", "low").upper()
    primary = result.primary_organization or {}
    primary_name = primary.get("canonical_name", "None identified")

    lines = [
        "=" * 70,
        f"AevoraSEO Entity & Authority Intelligence — {result.target_url}",
        "=" * 70,
        f"Primary Organization : {primary_name}",
        f"Authority Headline   : {headline}/100 [{conf} CONFIDENCE]",
        "-" * 70,
        "Score Breakdown (0–25 points each):",
        f"  - Identity Completeness : {score.get('identity_completeness', 0.0):.1f} / 25.0",
        f"  - Entity Consistency    : {score.get('entity_consistency', 0.0):.1f} / 25.0",
        f"  - Authority Footprint   : {score.get('authority_footprint', 0.0):.1f} / 25.0",
        f"  - Topical/Expert Depth  : {score.get('topical_expert_depth', 0.0):.1f} / 25.0",
        "-" * 70,
        f"Entities Discovered    : {len(result.nodes)}",
        f"Relationships Mapped   : {len(result.edges)}",
        f"SameAs Authority Links : {len(result.same_as_links)}",
        f"Consistency Conflicts  : {len(result.conflicts)}",
    ]

    if result.missing_entity_pages:
        lines.append(f"Missing Entity Pages   : {', '.join(result.missing_entity_pages)}")

    if result.conflicts:
        lines.append("\nDetected Entity Conflicts:")
        for c in result.conflicts[:5]:
            lines.append(f"  [!] {c.get('severity')}: {c.get('description')}")

    if result.same_as_links:
        lines.append("\nAuthority & SameAs Footprint:")
        for sa in result.same_as_links[:6]:
            status = "HIGH AUTH" if sa.get("is_high_authority") else "VALID"
            lines.append(f"  [*] {sa.get('platform')}: {sa.get('url')} ({status})")

    lines.append("=" * 70)
    return "\n".join(lines)


def generate_markdown_report(result: EntityAnalysisResult) -> str:
    """Renders comprehensive Markdown report."""
    score = result.score
    primary = result.primary_organization or {}
    primary_name = primary.get("canonical_name", "None identified")

    lines = [
        f"# AevoraSEO Entity, Authority & Knowledge Intelligence Report",
        f"",
        f"- **Target URL:** {result.target_url}",
        f"- **Brand Name:** {result.brand_name}",
        f"- **Primary Organization:** {primary_name}",
        f"- **Authority Headline Score:** **{score.get('headline', 0.0)}/100** ({score.get('confidence', 'low').upper()} CONFIDENCE)",
        f"- **Audit Date:** `{result.created_at}`",
        f"",
        f"## 1. Score Dimensions",
        f"",
        f"| Dimension | Points | Max | Status |",
        f"|---|---|---|---|",
        f"| Identity Completeness | {score.get('identity_completeness', 0.0):.1f} | 25.0 | Complete profile signals |",
        f"| Entity Consistency | {score.get('entity_consistency', 0.0):.1f} | 25.0 | Cross-page integrity |",
        f"| SameAs & Authority Footprint | {score.get('authority_footprint', 0.0):.1f} | 25.0 | High-authority semantic profiles |",
        f"| Topical & Expert Depth | {score.get('topical_expert_depth', 0.0):.1f} | 25.0 | Authorship and entity offerings |",
        f"",
        f"## 2. Knowledge Graph Topology",
        f"",
        f"- **Total Nodes:** {len(result.nodes)}",
        f"- **Total Edges:** {len(result.edges)}",
        f"- **Central Entity:** `{result.graph_metrics.get('central_entity_name', 'None')}`",
        f"- **Graph Density:** {result.graph_metrics.get('density', 0.0)}",
        f"",
        f"## 3. Discovered Entities",
        f"",
        f"| Type | Canonical Name | Source Pages | First Party |",
        f"|---|---|---|---|",
    ]

    for n in result.nodes[:20]:
        first_party = "Yes" if n.get("is_first_party") else "External"
        pages_count = len(n.get("source_pages", []))
        lines.append(f"| {n.get('entity_type')} | {n.get('canonical_name')} | {pages_count} pages | {first_party} |")

    lines.extend([
        f"",
        f"## 4. SameAs Authority Profiles",
        f"",
        f"| Platform | Target Profile URL | Authority Tier | Found On |",
        f"|---|---|---|---|",
    ])

    for sa in result.same_as_links:
        tier = "High Authority" if sa.get("is_high_authority") else "Standard"
        lines.append(f"| {sa.get('platform')} | {sa.get('url')} | {tier} | {sa.get('found_on_url')} |")

    if result.conflicts:
        lines.extend([
            f"",
            f"## 5. Entity Conflicts & Consistency Findings",
            f"",
            f"| Severity | Conflict Type | Entity | Description |",
            f"|---|---|---|---|",
        ])
        for c in result.conflicts:
            lines.append(f"| {c.get('severity')} | {c.get('conflict_type')} | {c.get('entity_name')} | {c.get('description')} |")

    if result.missing_entity_pages:
        lines.extend([
            f"",
            f"## 6. Missing Core Entity Pages",
            f"",
            f"The following recommended entity pages from the AevoraSEO knowledge-graph standard were missing from the crawl sample:",
            f"",
        ])
        for p in result.missing_entity_pages:
            lines.append(f"- `{p}`")

    lines.append("")
    return "\n".join(lines)


def export_entities_csv(nodes: List[Dict[str, Any]]) -> str:
    """Exports formula-injection-safe entities CSV string."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["entity_id", "entity_type", "canonical_name", "alternate_names", "is_first_party", "source_pages_count"])
    for n in nodes:
        alts = "; ".join(n.get("alternate_names", []))
        pages_cnt = len(n.get("source_pages", []))
        writer.writerow([
            sanitize_csv_cell(n.get("entity_id")),
            sanitize_csv_cell(n.get("entity_type")),
            sanitize_csv_cell(n.get("canonical_name")),
            sanitize_csv_cell(alts),
            sanitize_csv_cell("1" if n.get("is_first_party") else "0"),
            sanitize_csv_cell(pages_cnt),
        ])
    return output.getvalue()


def export_conflicts_csv(conflicts: List[Dict[str, Any]]) -> str:
    """Exports formula-injection-safe conflicts CSV string."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["conflict_id", "severity", "conflict_type", "entity_name", "description"])
    for c in conflicts:
        writer.writerow([
            sanitize_csv_cell(c.get("conflict_id")),
            sanitize_csv_cell(c.get("severity")),
            sanitize_csv_cell(c.get("conflict_type")),
            sanitize_csv_cell(c.get("entity_name")),
            sanitize_csv_cell(c.get("description")),
        ])
    return output.getvalue()


def save_entity_reports(result: EntityAnalysisResult, out_dir: Path) -> None:
    """Saves all structured reports and data files to the output directory."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. JSON report
    (out_dir / "entity-report.json").write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # 2. Markdown report
    (out_dir / "entity-report.md").write_text(
        generate_markdown_report(result),
        encoding="utf-8"
    )

    # 3. Graph JSON
    (out_dir / "entity-graph.json").write_text(
        json.dumps(result.graph_metrics.get("graph_json", {}), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # 4. Entities CSV
    (out_dir / "entities.csv").write_text(
        export_entities_csv(result.nodes),
        encoding="utf-8"
    )

    # 5. Conflicts CSV
    if result.conflicts:
        (out_dir / "entity-conflicts.csv").write_text(
            export_conflicts_csv(result.conflicts),
            encoding="utf-8"
        )
