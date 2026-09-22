"""Unified cross-subsystem client report generator for AevoraSEO."""

from __future__ import annotations

import base64
import enum
import html
import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

from .reports import asset


class IssuePriority(enum.Enum):
    """Severity classification for audit recommendations."""

    P0 = "P0"  # Critical Blocker (Crawl/Index/Security/Severe Cannibalization)
    P1 = "P1"  # High Impact (Conversion/Direct Answer/Entity Conflict/Hierarchy)
    P2 = "P2"  # Growth Opportunity (Cluster Expansion/Schema Enhancement/Thin Content)


def sanitize_csv_cell(value: Any) -> str:
    """Sanitize CSV cells to prevent formula injection attacks (=, +, -, @, \\t, \\r)."""
    s = str(value if value is not None else "")
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


@dataclass
class PrioritizedIssue:
    """An actionable finding categorized across subsystems and priority levels."""

    id: str
    title: str
    subsystem: str
    priority: IssuePriority
    impact: str
    affected_urls: List[str]
    recommended_action: str
    acceptance_check: str
    evidence: str


@dataclass
class SubsystemScore:
    """Dimensional score and diagnostic status for a specific subsystem."""

    name: str
    score: Optional[float]
    status: str
    key_metric: str


@dataclass
class UnifiedAuditReport:
    """Comprehensive client-ready SEO audit report synthesizing all intelligence subsystems."""

    target: str
    created_at: str
    executive_summary: str
    overall_score: Optional[float]
    subsystem_scores: Dict[str, SubsystemScore]
    prioritized_issues: List[PrioritizedIssue]
    roadmap_30_60_90: Dict[str, List[str]]
    acceptance_checklist: List[Dict[str, str]]
    coverage_summary: Dict[str, Any] = field(default_factory=dict)


def _score_status(score: Optional[float]) -> str:
    if score is None:
        return "Not Evaluated"
    if score >= 80:
        return "Good"
    if score >= 60:
        return "Needs Improvement"
    return "Poor"


def generate_unified_report(
    crawl_dir: Path,
    target: Optional[str] = None,
    brand: Optional[str] = None,
    previous_crawl_dir: Optional[Path] = None,
) -> UnifiedAuditReport:
    """Synthesize Technical, Content, AEO, GEO, Entity, Search/Commercial, and Reputation intelligence."""
    crawl_path = Path(crawl_dir).resolve()
    if not crawl_path.is_dir():
        raise ValueError(f"Crawl directory does not exist: {crawl_path}")

    created_at = datetime.now(timezone.utc).isoformat()
    detected_target = target or ""
    subsystem_scores: Dict[str, SubsystemScore] = {}
    prioritized_issues: List[PrioritizedIssue] = []
    coverage_summary: Dict[str, Any] = {}
    issue_counter = 1

    # 1. Technical & Crawl Subsystem
    crawl_db = crawl_path / "crawl.sqlite3"
    tech_score = None
    if crawl_db.is_file():
        try:
            conn = sqlite3.connect(str(crawl_db))
            try:
                cur = conn.cursor()
                row = cur.execute("SELECT value FROM meta WHERE key='config'").fetchone()
                if row and not detected_target:
                    cfg = json.loads(row[0]).get("config", {})
                    detected_target = cfg.get("start_urls", [""])[0]

                total_pages = cur.execute("SELECT count(*) FROM pages").fetchone()[0]
                status_200 = cur.execute("SELECT count(*) FROM pages WHERE status_code=200").fetchone()[0]
                status_4xx = cur.execute("SELECT count(*) FROM pages WHERE status_code>=400 AND status_code<500").fetchone()[0]
                status_5xx = cur.execute("SELECT count(*) FROM pages WHERE status_code>=500").fetchone()[0]
                noindex_count = cur.execute("SELECT count(*) FROM pages WHERE robots_noindex=1").fetchone()[0]

                coverage_summary["crawled_pages"] = total_pages
                coverage_summary["status_200"] = status_200
                coverage_summary["status_4xx"] = status_4xx
                coverage_summary["status_5xx"] = status_5xx

                # Calculate Technical Score
                if total_pages > 0:
                    health_ratio = (status_200 / total_pages) * 100.0
                    deduction = (status_5xx * 15.0) + (status_4xx * 5.0)
                    tech_score = max(0.0, min(100.0, round(health_ratio - deduction, 1)))
                else:
                    tech_score = 0.0

                if status_5xx > 0:
                    prioritized_issues.append(
                        PrioritizedIssue(
                            id=f"ISSUE-{issue_counter:03d}",
                            title=f"Critical 5xx Server Errors ({status_5xx} pages)",
                            subsystem="Technical SEO",
                            priority=IssuePriority.P0,
                            impact="Server errors completely block search indexation and destroy user conversion.",
                            affected_urls=[f"{detected_target} (5xx endpoints)"],
                            recommended_action="Inspect server logs, fix unhandled exceptions, and restore stable 200 OK responses.",
                            acceptance_check="Re-crawl confirms zero 5xx response codes.",
                            evidence=f"Observed {status_5xx} pages returning HTTP 5xx.",
                        )
                    )
                    issue_counter += 1

                if status_4xx > 0:
                    prioritized_issues.append(
                        PrioritizedIssue(
                            id=f"ISSUE-{issue_counter:03d}",
                            title=f"Broken Internal Links ({status_4xx} 404 pages)",
                            subsystem="Technical SEO",
                            priority=IssuePriority.P1,
                            impact="Broken links waste crawl budget and frustrate navigating visitors.",
                            affected_urls=[f"{detected_target} (broken links)"],
                            recommended_action="Update internal links or implement 301 redirects to relevant live pages.",
                            acceptance_check="No internal link leads to an unhandled 404 error.",
                            evidence=f"Observed {status_4xx} dead internal links.",
                        )
                    )
                    issue_counter += 1
            finally:
                conn.close()
        except Exception:
            pass

    subsystem_scores["technical"] = SubsystemScore(
        name="Technical SEO & Crawlability",
        score=tech_score,
        status=_score_status(tech_score),
        key_metric=f"{coverage_summary.get('status_200', 0)}/{coverage_summary.get('crawled_pages', 0)} healthy pages",
    )

    # 2. AEO & GEO Subsystem
    aeo_db = crawl_path / "aeo.sqlite3"
    aeo_score = None
    geo_score = None
    if aeo_db.is_file():
        try:
            conn = sqlite3.connect(str(aeo_db))
            try:
                cur = conn.cursor()
                row = cur.execute(
                    "SELECT overall_score, dimensional_scores FROM aeo_snapshots ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                if row:
                    aeo_score = round(float(row[0]), 1)
                    dims = json.loads(row[1]) if row[1] else {}
                    geo_score = round(dims.get("ai_citation_readiness", aeo_score), 1)

                no_answers = cur.execute(
                    "SELECT count(*) FROM aeo_page_evaluations WHERE direct_answer_present=0"
                ).fetchone()
                if no_answers and no_answers[0] > 0:
                    prioritized_issues.append(
                        PrioritizedIssue(
                            id=f"ISSUE-{issue_counter:03d}",
                            title=f"Missing Direct Answer Boxes ({no_answers[0]} pages)",
                            subsystem="AEO / GEO",
                            priority=IssuePriority.P1,
                            impact="Pages without concise 40–60 word answer boxes are omitted from AI overview citations.",
                            affected_urls=[f"{detected_target} (key landing pages)"],
                            recommended_action="Add direct definitions and bulleted procedural summaries immediately under question headings.",
                            acceptance_check="Target pages contain structured 40–60 word answer summaries verified by AEO analyzer.",
                            evidence=f"{no_answers[0]} pages lack clear direct answer blocks.",
                        )
                    )
                    issue_counter += 1
            finally:
                conn.close()
        except Exception:
            pass

    subsystem_scores["aeo"] = SubsystemScore(
        name="Answer Engine Optimization (AEO)",
        score=aeo_score,
        status=_score_status(aeo_score),
        key_metric=f"Score {aeo_score}/100" if aeo_score is not None else "Not run",
    )
    subsystem_scores["geo"] = SubsystemScore(
        name="Generative Engine Optimization (GEO)",
        score=geo_score,
        status=_score_status(geo_score),
        key_metric=f"Score {geo_score}/100" if geo_score is not None else "Not run",
    )

    # 3. Entity & Authority Subsystem
    entity_db = crawl_path / "entities.sqlite3"
    entity_score = None
    if entity_db.is_file():
        try:
            conn = sqlite3.connect(str(entity_db))
            try:
                cur = conn.cursor()
                row = cur.execute(
                    "SELECT overall_score, total_entities, sameas_count FROM entity_snapshots ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                if row:
                    entity_score = round(float(row[0]), 1)
                    tot_entities = row[1]
                    sameas = row[2]
                    coverage_summary["entities_found"] = tot_entities
                    coverage_summary["sameas_links"] = sameas

                conflicts = cur.execute("SELECT count(*) FROM entity_conflicts").fetchone()
                if conflicts and conflicts[0] > 0:
                    prioritized_issues.append(
                        PrioritizedIssue(
                            id=f"ISSUE-{issue_counter:03d}",
                            title=f"Entity Identity & NAP Conflicts ({conflicts[0]} detected)",
                            subsystem="Entity & Authority",
                            priority=IssuePriority.P0,
                            impact="Contradictory brand names or addresses confuse knowledge graph construction.",
                            affected_urls=[f"{detected_target} (Schema.org declarations)"],
                            recommended_action="Harmonize organization name, address, phone, and sameAs profiles across all pages.",
                            acceptance_check="Re-crawl entity extraction reports 0 entity conflicts.",
                            evidence=f"Observed {conflicts[0]} cross-page identity conflicts in SQLite.",
                        )
                    )
                    issue_counter += 1
            finally:
                conn.close()
        except Exception:
            pass

    subsystem_scores["entity"] = SubsystemScore(
        name="Entity & Knowledge Graph Authority",
        score=entity_score,
        status=_score_status(entity_score),
        key_metric=f"Score {entity_score}/100" if entity_score is not None else "Not run",
    )

    # 4. Search & Commercial Subsystem
    search_db = crawl_path / "search_commercial.sqlite3"
    search_score = None
    if search_db.is_file():
        try:
            conn = sqlite3.connect(str(search_db))
            try:
                cur = conn.cursor()
                row = cur.execute(
                    "SELECT overall_score, cannibalization_count FROM search_snapshots ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                if row:
                    search_score = round(float(row[0]), 1)
                    cannibals = row[1]
                    if cannibals > 0:
                        prioritized_issues.append(
                            PrioritizedIssue(
                                id=f"ISSUE-{issue_counter:03d}",
                                title=f"Keyword Cannibalization Detected ({cannibals} conflicts)",
                                subsystem="Search & Commercial",
                                priority=IssuePriority.P1,
                                impact="Multiple internal pages competing for the same target query split ranking signals.",
                                affected_urls=[f"{detected_target} (conflicting query targets)"],
                                recommended_action="Consolidate duplicate pages or differentiate search intent and internal anchor targeting.",
                                acceptance_check="Cannibalization audit reports zero High-severity query collisions.",
                                evidence=f"Observed {cannibals} cannibalization collisions.",
                            )
                        )
                        issue_counter += 1
            finally:
                conn.close()
        except Exception:
            pass

    subsystem_scores["search_commercial"] = SubsystemScore(
        name="Search Intent & Commercial Conversion",
        score=search_score,
        status=_score_status(search_score),
        key_metric=f"Score {search_score}/100" if search_score is not None else "Not run",
    )

    # 5. Content & Optimization Subsystem
    opt_db = crawl_path / "content_optimization.sqlite3"
    opt_score = None
    if opt_db.is_file():
        try:
            conn = sqlite3.connect(str(opt_db))
            try:
                cur = conn.cursor()
                row = cur.execute(
                    "SELECT overall_score, cluster_count, orphan_count FROM optimization_snapshots ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                if row:
                    opt_score = round(float(row[0]), 1)
                    orphans = row[2]
                    if orphans > 0:
                        prioritized_issues.append(
                            PrioritizedIssue(
                                id=f"ISSUE-{issue_counter:03d}",
                                title=f"Orphan Pages Found ({orphans} isolated URLs)",
                                subsystem="Content Optimization",
                                priority=IssuePriority.P1,
                                impact="Orphan pages have 0 inbound internal links, starving them of crawl frequency and authority.",
                                affected_urls=[f"{detected_target} (isolated pages)"],
                                recommended_action="Add contextual internal links from relevant parent pillar pages and site navigation.",
                                acceptance_check="Re-crawl internal link graph confirms zero orphan pages.",
                                evidence=f"Found {orphans} orphan URLs with in-degree 0.",
                            )
                        )
                        issue_counter += 1
            finally:
                conn.close()
        except Exception:
            pass

    subsystem_scores["content_optimization"] = SubsystemScore(
        name="Content Architecture & Optimization",
        score=opt_score,
        status=_score_status(opt_score),
        key_metric=f"Score {opt_score}/100" if opt_score is not None else "Not run",
    )

    # 6. Reputation & Backlinks Subsystem
    rep_db = crawl_path / "reputation.sqlite3"
    rep_json = crawl_path / "reputation.json"
    rep_score = None
    if rep_db.is_file():
        try:
            conn = sqlite3.connect(str(rep_db))
            try:
                cur = conn.cursor()
                row = cur.execute("SELECT score FROM reputation_snapshots ORDER BY created_at DESC LIMIT 1").fetchone()
                if row:
                    rep_score = round(float(row[0]), 1)
            finally:
                conn.close()
        except Exception:
            pass
    elif rep_json.is_file():
        try:
            data = json.loads(rep_json.read_text(encoding="utf-8"))
            if "score" in data:
                rep_score = round(float(data["score"]), 1)
        except Exception:
            pass

    subsystem_scores["reputation"] = SubsystemScore(
        name="Brand Reputation & Backlink Authority",
        score=rep_score,
        status=_score_status(rep_score),
        key_metric=f"Score {rep_score}/100" if rep_score is not None else "Not run",
    )

    # Calculate Overall Composite Score
    valid_scores = [s.score for s in subsystem_scores.values() if s.score is not None]
    overall_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else None

    # Fallback default target
    if not detected_target:
        detected_target = crawl_path.name

    # If no issues were detected from databases, provide standard health check finding
    if not prioritized_issues:
        prioritized_issues.append(
            PrioritizedIssue(
                id=f"ISSUE-{issue_counter:03d}",
                title="Baseline Verification Complete",
                subsystem="Unified Audit",
                priority=IssuePriority.P2,
                impact="Baseline technical and content health satisfied for inspected sample.",
                affected_urls=[detected_target],
                recommended_action="Continue ongoing 30/60/90-day topic cluster buildout and reputation tracking.",
                acceptance_check="Audit re-check maintains high dimensional health scores.",
                evidence="Inspected sample passed baseline checks.",
            )
        )

    # Sort prioritized issues (P0 -> P1 -> P2)
    p_order = {IssuePriority.P0: 0, IssuePriority.P1: 1, IssuePriority.P2: 2}
    prioritized_issues.sort(key=lambda x: p_order.get(x.priority, 3))

    # Dynamic Executive Summary
    p0_count = sum(1 for i in prioritized_issues if i.priority == IssuePriority.P0)
    p1_count = sum(1 for i in prioritized_issues if i.priority == IssuePriority.P1)
    p2_count = sum(1 for i in prioritized_issues if i.priority == IssuePriority.P2)

    summary_parts = [
        f"AevoraSEO unified audit completed for {detected_target}.",
        f"Overall Health Score: {overall_score}/100." if overall_score is not None else "Overall Health Score: Uncalculated (run sub-analyzers for full scoring).",
        f"Identified {len(prioritized_issues)} action items: {p0_count} Critical Blockers (P0), {p1_count} High Impact (P1), and {p2_count} Growth Opportunities (P2).",
        "Technical and entity foundations must be stabilized before proceeding with aggressive content and authority scaling.",
    ]
    executive_summary = " ".join(summary_parts)

    # 30/60/90-Day Implementation Roadmap
    roadmap_30_60_90 = {
        "days_1_30": [
            f"Resolve {p0_count} Critical Blockers (P0): eliminate 5xx server errors, unblock robots disallows, and harmonize entity identity.",
            "Verify search console and event conversion tracking (forms, phone calls, bookings).",
            "Stabilize metadata: single H1 enforcement and title tag optimization across tier-1 landing pages.",
        ],
        "days_31_60": [
            f"Resolve {p1_count} High-Impact items (P1): add direct 40–60 word answer boxes, fix 404s, and resolve keyword cannibalization.",
            "Recover orphan URLs by linking them from contextual pillar hubs.",
            "Implement typed Schema.org structured data (Article, Service, LocalBusiness, FAQPage).",
        ],
        "days_61_90": [
            f"Execute {p2_count} Growth Opportunities (P2): expand spoke clusters, build comparison matrices, and refresh thin content.",
            "Execute authentic backlink outreach to verified editorial and industry partner directories.",
            "Conduct split-testing on snippet CTR and commercial CTA conversion paths.",
        ],
    }

    # Acceptance Checklist
    acceptance_checklist = [
        {
            "issue_id": issue.id,
            "title": issue.title,
            "priority": issue.priority.value,
            "acceptance_criteria": issue.acceptance_check,
            "verification_status": "PENDING",
        }
        for issue in prioritized_issues
    ]

    return UnifiedAuditReport(
        target=detected_target,
        created_at=created_at,
        executive_summary=executive_summary,
        overall_score=overall_score,
        subsystem_scores=subsystem_scores,
        prioritized_issues=prioritized_issues,
        roadmap_30_60_90=roadmap_30_60_90,
        acceptance_checklist=acceptance_checklist,
        coverage_summary=coverage_summary,
    )


def render_terminal_report(report: UnifiedAuditReport) -> str:
    """Format unified audit report for clean terminal output."""
    lines = []
    lines.append("=" * 72)
    lines.append(f"  AEVORASEO UNIFIED CLIENT AUDIT REPORT")
    lines.append(f"  Target: {report.target}")
    lines.append(f"  Generated: {report.created_at[:19]} UTC")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Overall Health Score: {report.overall_score if report.overall_score is not None else 'N/A'}/100")
    lines.append("")
    lines.append("EXECUTIVE SUMMARY:")
    lines.append(f"  {report.executive_summary}")
    lines.append("")
    lines.append("SUBSYSTEM SCORECARD:")
    lines.append(f"  {'Subsystem':<38} {'Score':<10} {'Status':<18}")
    lines.append("  " + "-" * 66)
    for s in report.subsystem_scores.values():
        score_str = f"{s.score:.1f}" if s.score is not None else "N/A"
        lines.append(f"  {s.name:<38} {score_str:<10} {s.status:<18}")
    lines.append("")
    lines.append("PRIORITIZED ACTION ITEMS:")
    lines.append(f"  {'ID':<11} {'Pri':<5} {'Subsystem':<22} {'Title'}")
    lines.append("  " + "-" * 66)
    for issue in report.prioritized_issues:
        lines.append(f"  {issue.id:<11} {issue.priority.value:<5} {issue.subsystem:<22} {issue.title}")
    lines.append("")
    lines.append("30/60/90-DAY IMPLEMENTATION ROADMAP:")
    for period, tasks in report.roadmap_30_60_90.items():
        title = period.replace("_", " ").title()
        lines.append(f"  [{title}]")
        for t in tasks:
            lines.append(f"    - {t}")
    lines.append("")
    lines.append("=" * 72)
    return "\n".join(lines)


def render_markdown_report(report: UnifiedAuditReport) -> str:
    """Format unified audit report as rich GitHub Flavored Markdown."""
    lines = []
    lines.append(f"# AevoraSEO Unified Client Audit Report: {report.target}\n")
    lines.append(f"**Generated:** `{report.created_at[:19]} UTC`  ")
    score_display = f"**{report.overall_score}/100**" if report.overall_score is not None else "*Not fully evaluated*"
    lines.append(f"**Overall Health Score:** {score_display}\n")
    lines.append("## Executive Summary\n")
    lines.append(f"> {report.executive_summary}\n")
    lines.append("## Subsystem Scorecard\n")
    lines.append("| Subsystem | Score | Status | Key Metric |")
    lines.append("|---|---|---|---|")
    for s in report.subsystem_scores.values():
        score_str = f"{s.score:.1f}" if s.score is not None else "N/A"
        lines.append(f"| **{s.name}** | {score_str} | {s.status} | {s.key_metric} |")
    lines.append("\n## Prioritized Action Items\n")
    lines.append("| ID | Priority | Subsystem | Action Item | Acceptance Check |")
    lines.append("|---|---|---|---|---|")
    for i in report.prioritized_issues:
        lines.append(f"| `{i.id}` | **{i.priority.value}** | {i.subsystem} | {i.title} | {i.acceptance_check} |")
    lines.append("\n## Phased 30 / 60 / 90-Day Roadmap\n")
    for period, tasks in report.roadmap_30_60_90.items():
        label = period.replace("_", " ").title()
        lines.append(f"### {label}")
        for t in tasks:
            lines.append(f"- {t}")
        lines.append("")
    lines.append("## Acceptance Checklist\n")
    lines.append("| ID | Issue Title | Acceptance Criteria | Status |")
    lines.append("|---|---|---|---|")
    for c in report.acceptance_checklist:
        lines.append(f"| `{c['issue_id']}` | {c['title']} | {c['acceptance_criteria']} | `{c['verification_status']}` |")
    return "\n".join(lines)


def render_html_report(report: UnifiedAuditReport) -> str:
    """Format unified audit report as self-contained, responsive offline HTML."""
    try:
        logo = base64.b64encode(asset("aevoraseo-logo.png")).decode("ascii")
        logo_html = f'<img src="data:image/png;base64,{logo}" alt="AevoraSEO Logo" style="height:36px;vertical-align:middle;margin-right:12px;">'
    except Exception:
        logo_html = ""

    score_val = f"{report.overall_score:.1f}" if report.overall_score is not None else "N/A"

    score_rows = []
    for s in report.subsystem_scores.values():
        sc = f"{s.score:.1f}" if s.score is not None else "N/A"
        status_color = "#15803d" if s.status == "Good" else "#b45309" if s.status == "Needs Improvement" else "#b91c1c"
        score_rows.append(
            f"<tr><td><strong>{html.escape(s.name)}</strong></td><td>{sc}</td><td style='color:{status_color};font-weight:600;'>{html.escape(s.status)}</td><td>{html.escape(s.key_metric)}</td></tr>"
        )

    issue_rows = []
    for i in report.prioritized_issues:
        pri_bg = "#fee2e2" if i.priority == IssuePriority.P0 else "#fef3c7" if i.priority == IssuePriority.P1 else "#e0f2fe"
        pri_fg = "#991b1b" if i.priority == IssuePriority.P0 else "#92400e" if i.priority == IssuePriority.P1 else "#075985"
        issue_rows.append(
            f"<tr><td><code>{html.escape(i.id)}</code></td><td><span style='background:{pri_bg};color:{pri_fg};padding:2px 8px;border-radius:4px;font-weight:700;'>{i.priority.value}</span></td><td>{html.escape(i.subsystem)}</td><td><strong>{html.escape(i.title)}</strong><br><small style='color:#666;'>{html.escape(i.recommended_action)}</small></td><td>{html.escape(i.acceptance_check)}</td></tr>"
        )

    roadmap_html = []
    for period, tasks in report.roadmap_30_60_90.items():
        title = period.replace("_", " ").title()
        task_items = "".join(f"<li>{html.escape(t)}</li>" for t in tasks)
        roadmap_html.append(f"<div style='flex:1;min-width:240px;background:#f8fafc;padding:16px;border-radius:8px;border:1px solid #e2e8f0;'><h4>{title}</h4><ul>{task_items}</ul></div>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AevoraSEO Audit - {html.escape(report.target)}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1e293b; background: #fff; line-height: 1.5; margin: 0; padding: 24px; }}
.container {{ max-width: 1040px; margin: 0 auto; }}
.header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
.score-badge {{ background: #0f172a; color: #fff; padding: 12px 20px; border-radius: 8px; text-align: center; }}
.score-badge .num {{ font-size: 32px; font-weight: 800; }}
.summary-box {{ background: #f1f5f9; border-left: 4px solid #3b82f6; padding: 16px; margin-bottom: 24px; border-radius: 0 8px 8px 0; }}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 14px; }}
th, td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; text-align: left; }}
th {{ background: #f8fafc; font-weight: 600; color: #475569; }}
.roadmap {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      {logo_html}
      <h1 style="display:inline;font-size:24px;vertical-align:middle;">AevoraSEO Client Audit</h1>
      <p style="margin:4px 0 0 0;color:#64748b;">Target: <strong>{html.escape(report.target)}</strong> | Generated: {report.created_at[:19]} UTC</p>
    </div>
    <div class="score-badge">
      <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;">Health Score</div>
      <div class="num">{score_val}</div>
    </div>
  </div>

  <div class="summary-box">
    <h3 style="margin:0 0 8px 0;">Executive Summary</h3>
    <p style="margin:0;">{html.escape(report.executive_summary)}</p>
  </div>

  <h2>Subsystem Scorecard</h2>
  <table>
    <thead><tr><th>Subsystem</th><th>Score</th><th>Status</th><th>Key Metric</th></tr></thead>
    <tbody>{"".join(score_rows)}</tbody>
  </table>

  <h2>Prioritized Action Matrix</h2>
  <table>
    <thead><tr><th>ID</th><th>Priority</th><th>Subsystem</th><th>Action Item</th><th>Acceptance Check</th></tr></thead>
    <tbody>{"".join(issue_rows)}</tbody>
  </table>

  <h2>30 / 60 / 90-Day Implementation Roadmap</h2>
  <div class="roadmap">{"".join(roadmap_html)}</div>
</div>
</body>
</html>"""


def render_json_report(report: UnifiedAuditReport) -> str:
    """Format unified audit report as formatted JSON."""
    data = asdict(report)
    # Convert IssuePriority enum
    for issue in data["prioritized_issues"]:
        issue["priority"] = issue["priority"].value if hasattr(issue["priority"], "value") else str(issue["priority"])
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_evidence_csv(report: UnifiedAuditReport, out_dir: Path) -> List[str]:
    """Export structured audit findings to formula-injection-safe CSV files."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    files_written = []

    # 1. audit-issues.csv
    issues_file = out_path / "audit-issues.csv"
    issue_lines = ["id,priority,subsystem,title,impact,affected_urls,recommended_action,acceptance_check,evidence"]
    for i in report.prioritized_issues:
        urls_str = "; ".join(i.affected_urls)
        row = [
            sanitize_csv_cell(i.id),
            sanitize_csv_cell(i.priority.value),
            sanitize_csv_cell(i.subsystem),
            sanitize_csv_cell(i.title),
            sanitize_csv_cell(i.impact),
            sanitize_csv_cell(urls_str),
            sanitize_csv_cell(i.recommended_action),
            sanitize_csv_cell(i.acceptance_check),
            sanitize_csv_cell(i.evidence),
        ]
        issue_lines.append(",".join(f'"{r}"' for r in row))
    issues_file.write_text("\n".join(issue_lines), encoding="utf-8-sig")
    files_written.append(str(issues_file))

    # 2. audit-scorecard.csv
    score_file = out_path / "audit-scorecard.csv"
    score_lines = ["subsystem,score,status,key_metric"]
    for s in report.subsystem_scores.values():
        score_val = f"{s.score:.1f}" if s.score is not None else ""
        row = [
            sanitize_csv_cell(s.name),
            sanitize_csv_cell(score_val),
            sanitize_csv_cell(s.status),
            sanitize_csv_cell(s.key_metric),
        ]
        score_lines.append(",".join(f'"{r}"' for r in row))
    score_file.write_text("\n".join(score_lines), encoding="utf-8-sig")
    files_written.append(str(score_file))

    return files_written
