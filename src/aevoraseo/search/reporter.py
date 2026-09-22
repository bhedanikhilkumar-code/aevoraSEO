"""
Multi-format reporting for AevoraSEO Search, Local & Commercial Intelligence.
Formats: Terminal, Markdown, JSON, and CSV with formula injection defense.
"""

import json
from pathlib import Path
from typing import Any, List

from .comparison import sanitize_csv_cell
from .models import SearchCommercialAnalysisResult
from .persistence import save_search_snapshot


def generate_terminal_report(result: SearchCommercialAnalysisResult, use_color: bool = True) -> str:
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
    score_color = c_green if headline >= 75 else (c_yellow if headline >= 50 else c_red)

    lines: List[str] = [
        f"{c_bold}{c_cyan}═══════════════════════════════════════════════════════════════════════{c_reset}",
        f"{c_bold}{c_cyan}  AevoraSEO Search, Local & Commercial Intelligence Engine{c_reset}",
        f"{c_bold}{c_cyan}═══════════════════════════════════════════════════════════════════════{c_reset}",
        f"  Target URL:        {result.target_url}",
        f"  Brand Name:        {result.brand_name}",
        f"  Pages Analyzed:    {result.pages_analyzed}",
        f"  Created At:        {result.created_at}",
        "",
        f"  {c_bold}Search & Commercial Visibility Score:{c_reset} {score_color}{c_bold}{headline:.1f} / 100{c_reset} {c_dim}(Confidence: {score.get('confidence', 'low')}){c_reset}",
        "",
        f"  {c_bold}Dimensional Breakdown (0 - 25 points each):{c_reset}",
        f"    • Intent & Query Targeting:         {score.get('intent_query_targeting', 0.0):.1f} / 25",
        f"    • Commercial Journey & CTAs:        {score.get('commercial_journey_cta', 0.0):.1f} / 25",
        f"    • Local Visibility & Service Areas: {score.get('local_visibility_signals', 0.0):.1f} / 25",
        f"    • Comparison & Buyer Decisions:     {score.get('comparison_buyer_support', 0.0):.1f} / 25",
        "",
        f"  {c_bold}Search Intent Distribution:{c_reset}",
    ]

    for intent, count in sorted(result.intent_distribution.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"    • {intent:<25} {count} pages")

    # Cannibalization warnings
    if result.cannibalization_issues:
        lines.extend([
            "",
            f"  {c_bold}{c_yellow}Keyword Cannibalization Alerts ({len(result.cannibalization_issues)}):{c_reset}",
        ])
        for c in result.cannibalization_issues[:5]:
            badge = f"{c_red}[HIGH]{c_reset}" if c.get("risk_level") == "HIGH" else f"{c_yellow}[MED]{c_reset}"
            lines.append(f"    {badge} Query: '{c.get('query')}' (Similarity: {c.get('similarity_score', 0.0):.0%})")
            for u in c.get("competing_urls", []):
                lines.append(f"       ↳ {u}")
            lines.append(f"       {c_dim}Action: {c.get('recommendation')}{c_reset}")
    else:
        lines.extend([
            "",
            f"  {c_green}✓ No critical keyword cannibalization detected among crawled pages.{c_reset}",
        ])

    # Commercial Friction highlights
    friction_count = sum(len(c.get("friction_issues", [])) for c in result.commercial_journeys)
    if friction_count > 0:
        lines.extend([
            "",
            f"  {c_bold}{c_yellow}Commercial Journey & Friction Issues ({friction_count}):{c_reset}",
        ])
        for c in result.commercial_journeys:
            for issue in c.get("friction_issues", []):
                lines.append(f"    [!] {c.get('url')}")
                lines.append(f"        ↳ {issue}")
    else:
        lines.extend([
            "",
            f"  {c_green}✓ No high-friction conversion blockers detected.{c_reset}",
        ])

    # Local Signals Summary
    local_schemas = sum(1 for l in result.local_signals if l.get("has_local_business_schema"))
    naps = sum(1 for l in result.local_signals if l.get("nap_present"))
    click_tels = sum(1 for l in result.local_signals if l.get("has_clickable_tel"))
    lines.extend([
        "",
        f"  {c_bold}Local Visibility Signals:{c_reset}",
        f"    • LocalBusiness Schema:     {local_schemas} pages",
        f"    • Uniform NAP Detected:     {naps} pages",
        f"    • Clickable Phone (tel:):   {click_tels} pages",
    ])

    if result.recommendations:
        lines.extend([
            "",
            f"  {c_bold}Strategic Recommendations:{c_reset}",
        ])
        for rec in result.recommendations[:5]:
            lines.append(f"    {c_cyan}➔{c_reset} {rec}")

    lines.extend([
        "",
        f"{c_bold}{c_cyan}═══════════════════════════════════════════════════════════════════════{c_reset}",
    ])
    return "\n".join(lines)


def generate_markdown_report(result: SearchCommercialAnalysisResult) -> str:
    """Generate clean Markdown documentation report."""
    score = result.score
    headline = score.get("headline", 0.0)

    md: List[str] = [
        f"# Search, Local & Commercial Intelligence Report — {result.target_url}",
        "",
        f"- **Target URL:** {result.target_url}",
        f"- **Brand Name:** {result.brand_name}",
        f"- **Pages Analyzed:** {result.pages_analyzed}",
        f"- **Generated At:** {result.created_at}",
        f"- **AevoraSEO Search & Commercial Score:** **{headline:.1f} / 100** ({score.get('confidence', 'low')} confidence)",
        "",
        "## 1. Dimensional Score Breakdown",
        "",
        "| Dimension | Score | Max Points | Weight |",
        "|---|---|---|---|",
        f"| Intent & Query Targeting | {score.get('intent_query_targeting', 0.0):.1f} | 25.0 | 25% |",
        f"| Commercial Journey & CTA Readiness | {score.get('commercial_journey_cta', 0.0):.1f} | 25.0 | 25% |",
        f"| Local Visibility & Service-Area Signals | {score.get('local_visibility_signals', 0.0):.1f} | 25.0 | 25% |",
        f"| Comparison & Buyer Decision Support | {score.get('comparison_buyer_support', 0.0):.1f} | 25.0 | 25% |",
        "",
        "## 2. Search Intent Taxonomy",
        "",
        "| Intent Category | Page Count | Ratio |",
        "|---|---|---|",
    ]

    total_pages = max(1, result.pages_analyzed)
    for intent, count in sorted(result.intent_distribution.items(), key=lambda x: x[1], reverse=True):
        md.append(f"| {intent} | {count} | {count / total_pages:.1%} |")

    if result.cannibalization_issues:
        md.extend([
            "",
            "## 3. Keyword Cannibalization Audits",
            "",
            "| Primary Query | Intent | Risk Level | Similarity | Competing URLs | Action |",
            "|---|---|---|---|---|---|",
        ])
        for c in result.cannibalization_issues:
            urls = "<br>".join(c.get("competing_urls", []))
            md.append(f"| {c.get('query')} | {c.get('intent')} | {c.get('risk_level')} | {c.get('similarity_score', 0.0):.0%} | {urls} | {c.get('recommendation')} |")

    md.extend([
        "",
        "## 4. Commercial Conversion Journey & CTA Friction",
        "",
        "| Page URL | Type | CTAs | High-Intent CTAs | Trust Proofs | Friction Blockers |",
        "|---|---|---|---|---|---|",
    ])
    for comm in result.commercial_journeys:
        high_cta_str = ", ".join([c.get("text", "") for c in comm.get("high_intent_ctas", [])[:2]]) or "None"
        trust_str = ", ".join(comm.get("trust_signals", [])[:2]) or "None"
        friction_str = "<br>".join(comm.get("friction_issues", [])) or "Clean"
        md.append(f"| {comm.get('url')} | {comm.get('page_type')} | {comm.get('cta_count')} | {high_cta_str} | {trust_str} | {friction_str} |")

    md.extend([
        "",
        "## 5. Local Search Visibility Signals",
        "",
        "| Page URL | LocalBusiness Schema | NAP Present | Clickable Phone | Map Integration | Declared Service Areas |",
        "|---|---|---|---|---|---|",
    ])
    for loc in result.local_signals:
        schema_badge = "Yes" if loc.get("has_local_business_schema") else "No"
        nap_badge = "Yes" if loc.get("nap_present") else "No"
        tel_badge = "Yes" if loc.get("has_clickable_tel") else "No"
        map_badge = "Yes" if loc.get("has_map_embed_or_link") else "No"
        areas = ", ".join(loc.get("service_areas_declared", [])[:3]) or "None"
        md.append(f"| {loc.get('url')} | {schema_badge} | {nap_badge} | {tel_badge} | {map_badge} | {areas} |")

    if result.recommendations:
        md.extend([
            "",
            "## 6. Strategic Recommendations",
            "",
        ])
        for rec in result.recommendations:
            md.append(f"- {rec}")

    return "\n".join(md) + "\n"


def export_reports(
    result: SearchCommercialAnalysisResult,
    out_dir: Path,
    snapshot_id: str,
) -> None:
    """Save all report files and persist to SQLite."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. JSON
    (out_dir / "search-commercial.json").write_text(
        json.dumps(result.to_dict(), indent=2), encoding="utf-8"
    )

    # 2. Markdown
    (out_dir / "search-commercial.md").write_text(
        generate_markdown_report(result), encoding="utf-8"
    )

    # 3. Page Intents CSV (sanitized)
    intent_lines = ["url,primary_intent,target_query,secondary_queries,confidence"]
    for p in result.page_intents:
        sec = ";".join(p.get("secondary_queries", []))
        intent_lines.append(
            f"{sanitize_csv_cell(p.get('url'))},{sanitize_csv_cell(p.get('primary_intent'))},"
            f"{sanitize_csv_cell(p.get('primary_target_query'))},{sanitize_csv_cell(sec)},"
            f"{p.get('confidence', 1.0)}"
        )
    (out_dir / "page-intents.csv").write_text("\n".join(intent_lines) + "\n", encoding="utf-8-sig")

    # 4. Cannibalization CSV (sanitized)
    cannibal_lines = ["query,intent,risk_level,similarity_score,competing_urls,recommendation"]
    for c in result.cannibalization_issues:
        urls = ";".join(c.get("competing_urls", []))
        cannibal_lines.append(
            f"{sanitize_csv_cell(c.get('query'))},{sanitize_csv_cell(c.get('intent'))},"
            f"{sanitize_csv_cell(c.get('risk_level'))},{c.get('similarity_score', 0.0)},"
            f"{sanitize_csv_cell(urls)},{sanitize_csv_cell(c.get('recommendation'))}"
        )
    (out_dir / "cannibalization.csv").write_text("\n".join(cannibal_lines) + "\n", encoding="utf-8-sig")

    # 5. Commercial Friction CSV (sanitized)
    comm_lines = ["url,page_type,cta_count,has_phone,has_whatsapp,friction_issues"]
    for comm in result.commercial_journeys:
        issues = ";".join(comm.get("friction_issues", []))
        comm_lines.append(
            f"{sanitize_csv_cell(comm.get('url'))},{sanitize_csv_cell(comm.get('page_type'))},"
            f"{comm.get('cta_count')},{1 if comm.get('has_phone_call_action') else 0},"
            f"{1 if comm.get('has_messaging_action') else 0},{sanitize_csv_cell(issues)}"
        )
    (out_dir / "commercial-friction.csv").write_text("\n".join(comm_lines) + "\n", encoding="utf-8-sig")

    # 6. SQLite Persistence
    db_path = out_dir / "search_commercial.sqlite3"
    save_search_snapshot(db_path, result, snapshot_id)
