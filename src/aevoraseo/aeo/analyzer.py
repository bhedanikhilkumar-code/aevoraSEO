"""
AevoraSEO AEO / GEO Coordinator & Snapshot Analyzer
Coordinates page-level and snapshot-level analysis, produces transparent scoring audits,
generates Markdown summaries, exports JSON reports and granular CSV data.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from aevoraseo.evidence import selected_data
from aevoraseo.aeo.models import (
    ObservedVisibilityRecord,
    PageAEOResult,
    SnapshotAEOResult,
)
from aevoraseo.aeo.questions import analyze_page_questions
from aevoraseo.aeo.entities import analyze_page_entities, detect_cross_page_conflicts
from aevoraseo.aeo.schema import audit_page_schema
from aevoraseo.aeo.citations import analyze_page_citations
from aevoraseo.aeo.accessibility import evaluate_bot_accessibility
from aevoraseo.aeo.content_structure import audit_page_content_structure, audit_snapshot_content_conflicts
from aevoraseo.aeo.scoring import calculate_aeo_readiness, calculate_geo_signals
from aevoraseo.aeo.visibility import load_observed_visibility


def analyze_page(
    page_url: str,
    page_data: Dict[str, Any],
    html: str = "",
    robots_text: Optional[str] = None,
    headers: Optional[Dict[str, Any]] = None,
) -> PageAEOResult:
    """
    Executes comprehensive AEO and GEO evaluation for a single page.
    """
    # 1. Questions and direct answers
    questions = analyze_page_questions(page_data, html=html)

    # 2. Schema entities and relationships
    entities = analyze_page_entities(page_data, canonical_url=page_url)

    # 3. Structured data audit
    schemas = audit_page_schema(page_data, canonical_url=page_url)

    # 4. Source & citation readiness
    citations = analyze_page_citations(page_url, page_data, html=html)

    # 5. AI bot accessibility
    crawler_access = evaluate_bot_accessibility(
        page_url,
        robots_text=robots_text,
        meta_directives=page_data.get("meta"),
        headers=headers,
    )

    # 6. Content structure & hierarchy
    content_structure = audit_page_content_structure(page_data, html=html)

    # 7. Calculate scores
    aeo_score, aeo_dims = calculate_aeo_readiness(
        questions=questions,
        content_structure=content_structure,
        schemas=schemas,
        crawler_access=crawler_access,
    )

    has_rich_formats = (content_structure.list_count > 0 or content_structure.table_count > 0)
    geo_score, geo_dims = calculate_geo_signals(
        entities=entities,
        citations=citations,
        schemas=schemas,
        word_count=page_data.get("word_count", 0),
        has_tables_or_lists=has_rich_formats,
    )

    # 8. Actionable recommendations
    recommendations: List[str] = []
    unanswered = [q for q in questions if not q.answer_detected]
    if unanswered:
        recommendations.append(
            f"Add concise direct answers (15-50 words) immediately following {len(unanswered)} question heading(s)."
        )

    if not content_structure.has_h1:
        recommendations.append("Add a single descriptive <h1> heading to establish topic clarity.")
    elif content_structure.h1_count > 1:
        recommendations.append(f"Consolidate {content_structure.h1_count} <h1> headings into a single primary <h1>.")

    if not content_structure.heading_hierarchy_valid:
        recommendations.append("Fix heading hierarchy sequence to avoid skipped levels.")

    if not citations.author:
        recommendations.append("Include an explicit author byline and schema Person attribution.")

    if not citations.date_published and not citations.date_modified:
        recommendations.append("Provide publication and modification date timestamps for freshness.")

    if not any(s.valid for s in schemas):
        recommendations.append("Implement valid Schema.org JSON-LD (e.g. Article, FAQPage, or Organization).")

    blocked_bots = [b for b in crawler_access if b.status == "crawl_restricted"]
    if blocked_bots:
        bot_names = ", ".join(b.bot_name for b in blocked_bots[:3])
        recommendations.append(f"Review crawl restrictions blocking AI crawlers: {bot_names}.")

    return PageAEOResult(
        url=page_url,
        aeo_readiness_score=aeo_score,
        geo_signal_score=geo_score,
        aeo_dimensions=aeo_dims,
        geo_dimensions=geo_dims,
        questions=questions,
        entities=entities,
        schemas=schemas,
        citations=citations,
        crawler_accessibility=crawler_access,
        content_structure=content_structure,
        recommendations=recommendations,
    )


def generate_aeo_summary_markdown(result: SnapshotAEOResult) -> str:
    """
    Renders an engineering-grade markdown audit report from a SnapshotAEOResult.
    """
    lines = [
        f"# AevoraSEO AEO / GEO Intelligence Report",
        f"",
        f"**Snapshot**: `{result.snapshot_id}`  ",
        f"**Seed URL**: `{result.seed_url}`  ",
        f"**Pages Analyzed**: {result.page_count}  ",
        f"**Analyzed At**: {result.timestamp}  ",
        f"",
        f"---",
        f"",
        f"## Executive Scores",
        f"",
        f"| Metric | Score | Analytical Benchmark |",
        f"| :--- | :--- | :--- |",
        f"| **AevoraSEO AEO Readiness Score** | **{result.average_aeo_readiness_score:.1f} / 100** | Answer Engine Optimization Readiness |",
        f"| **AevoraSEO GEO Signal Score** | **{result.average_geo_signal_score:.1f} / 100** | Generative Engine Optimization Signal Strength |",
        f"",
        f"> **Notice**: These scores represent internal heuristic models of content readiness and machine accessibility. They do NOT guarantee external search engine ranking or generative AI citation.",
        f"",
        f"---",
        f"",
        f"## AI Crawler Accessibility Matrix",
        f"",
        f"| Crawler | Operator | Allowed Pages | Restricted Pages | Unknown |",
        f"| :--- | :--- | :--- | :--- | :--- |",
    ]

    for bot_name, counts in sorted(result.bot_accessibility_matrix.items()):
        allowed = counts.get("crawl_allowed", 0)
        restricted = counts.get("crawl_restricted", 0)
        unknown = counts.get("crawl_unknown", 0)
        lines.append(f"| `{bot_name}` | AI / Search | {allowed} | {restricted} | {unknown} |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## Detected Entities & Identity Graph",
        f"",
    ])

    if result.detected_entities:
        lines.append(f"| Entity Type | Entity Name | Frequency | Sources |")
        lines.append(f"| :--- | :--- | :--- | :--- |")
        for ent in result.detected_entities[:15]:
            lines.append(
                f"| `{ent.get('type')}` | {ent.get('name')} | {ent.get('count')} | {', '.join(ent.get('sources', []))} |"
            )
    else:
        lines.append(f"*No structured Schema.org entities detected across crawled pages.*")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## Top Question Opportunities & Answer Presence",
        f"",
    ])

    if result.top_questions:
        lines.append(f"| Question | Detected Answer | Location | Confidence |")
        lines.append(f"| :--- | :--- | :--- | :--- |")
        for q in result.top_questions[:15]:
            ans_mark = "✅ Yes" if q.get("answer_detected") else "❌ Missing"
            loc = q.get("answer_location", "N/A")
            conf = f"{q.get('confidence', 0.0):.2f}"
            lines.append(f"| {q.get('question')} | {ans_mark} | `{loc}` | {conf} |")
    else:
        lines.append(f"*No interrogative headings or FAQ questions detected.*")

    if result.content_conflicts:
        lines.extend([
            f"",
            f"---",
            f"",
            f"## Content Conflicts & Contradictions",
            f"",
        ])
        for c in result.content_conflicts:
            lines.append(f"- **{c.get('type')}**: {c.get('message')}")

    if result.observed_visibility:
        lines.extend([
            f"",
            f"---",
            f"",
            f"## Empirical Observed Visibility (External Data)",
            f"",
            f"> **Strict Separation**: These records originate from external datasets, not inferred readiness.",
            f"",
            f"| Query | Engine | URL | Position | Citation Observed | Source |",
            f"| :--- | :--- | :--- | :--- | :--- | :--- |",
        ])
        for obs in result.observed_visibility:
            pos_str = str(obs.position) if obs.position is not None else "N/A"
            cit_str = "Yes" if obs.citation else "No"
            lines.append(f"| {obs.query} | `{obs.engine}` | `{obs.url}` | {pos_str} | {cit_str} | {obs.source} |")

    return "\n".join(lines)


def analyze_snapshot(
    snapshot_dir: Path | str,
    visibility_file: Optional[Path | str] = None,
    out_dir: Optional[Path | str] = None,
) -> SnapshotAEOResult:
    """
    Loads crawled page snapshot, executes complete AEO/GEO analysis,
    and writes out aeo_report.json, aeo_summary.md, and aeo_pages.csv.
    """
    snap_path = Path(snapshot_dir)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot directory does not exist: {snap_path}")

    pages_file = snap_path / "pages.jsonl"
    if not pages_file.exists():
        raise FileNotFoundError(f"Snapshot missing pages.jsonl: {pages_file}")

    # Read summary and robots if present
    summary = {}
    summary_path = snap_path / "summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    robots_text: Optional[str] = None
    robots_path = snap_path / "robots.json"
    if robots_path.exists():
        try:
            robots_data = json.loads(robots_path.read_text(encoding="utf-8"))
            robots_text = robots_data.get("text")
        except Exception:
            pass

    # Read pages
    pages_raw: List[Dict[str, Any]] = []
    with pages_file.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                pages_raw.append(json.loads(line))

    # Evaluate each page
    page_results: List[PageAEOResult] = []
    for page in pages_raw:
        data, _ = selected_data(page)
        url = page.get("final_url") or page.get("url", "")
        html = page.get("html") or ""
        headers = page.get("headers", {})

        p_res = analyze_page(
            page_url=url,
            page_data=data,
            html=html,
            robots_text=robots_text,
            headers=headers,
        )
        page_results.append(p_res)

    # Site-wide calculations
    page_count = len(page_results)
    avg_aeo = round(sum(p.aeo_readiness_score for p in page_results) / page_count, 1) if page_count else 0.0
    avg_geo = round(sum(p.geo_signal_score for p in page_results) / page_count, 1) if page_count else 0.0

    # Bot accessibility matrix aggregation
    matrix: Dict[str, Dict[str, int]] = {}
    for p in page_results:
        for bot_sig in p.crawler_accessibility:
            bot_entry = matrix.setdefault(bot_sig.bot_name, {"crawl_allowed": 0, "crawl_restricted": 0, "crawl_unknown": 0})
            bot_entry[bot_sig.status] = bot_entry.get(bot_sig.status, 0) + 1

    # Detected entities aggregation
    entity_counts: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for p in page_results:
        for ent in p.entities:
            if ent.name:
                key = (ent.entity_type, ent.name)
                if key not in entity_counts:
                    entity_counts[key] = {
                        "type": ent.entity_type,
                        "name": ent.name,
                        "count": 0,
                        "sources": set(),
                    }
                entity_counts[key]["count"] += 1
                entity_counts[key]["sources"].add(ent.source)

    aggregated_entities = [
        {"type": v["type"], "name": v["name"], "count": v["count"], "sources": sorted(v["sources"])}
        for v in entity_counts.values()
    ]
    aggregated_entities.sort(key=lambda x: x["count"], reverse=True)

    # Question opportunities aggregation
    aggregated_questions: List[Dict[str, Any]] = []
    seen_q = set()
    for p in page_results:
        for q in p.questions:
            if q.question.lower() not in seen_q:
                seen_q.add(q.question.lower())
                aggregated_questions.append(q.to_dict())

    # Cross-page conflicts
    entity_pairs = [(p.url, p.entities) for p in page_results]
    ent_conflicts = detect_cross_page_conflicts(entity_pairs)
    content_conflicts = audit_snapshot_content_conflicts(pages_raw)
    all_conflicts = ent_conflicts + content_conflicts

    # Optional observed visibility records
    observed_records: List[ObservedVisibilityRecord] = []
    if visibility_file:
        vis_path = Path(visibility_file)
        if vis_path.exists():
            observed_records = load_observed_visibility(vis_path)

    snap_id = summary.get("snapshot_id") or summary.get("run_id") or snap_path.name
    seed_url = summary.get("url") or (page_results[0].url if page_results else "")
    timestamp = summary.get("created_at") or summary.get("timestamp") or ""

    result = SnapshotAEOResult(
        snapshot_id=snap_id,
        snapshot_dir=str(snap_path.resolve()),
        timestamp=timestamp,
        seed_url=seed_url,
        page_count=page_count,
        average_aeo_readiness_score=avg_aeo,
        average_geo_signal_score=avg_geo,
        bot_accessibility_matrix=matrix,
        top_questions=aggregated_questions,
        detected_entities=aggregated_entities,
        content_conflicts=all_conflicts,
        pages=page_results,
        observed_visibility=observed_records,
        summary_markdown="",
    )

    result.summary_markdown = generate_aeo_summary_markdown(result)

    # Export outputs if out_dir is specified
    if out_dir is not None:
        target_dir = Path(out_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # 1. aeo_report.json
        (target_dir / "aeo_report.json").write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        # 2. aeo_summary.md
        (target_dir / "aeo_summary.md").write_text(
            result.summary_markdown + "\n",
            encoding="utf-8",
        )

        # 3. aeo_pages.csv
        csv_rows = []
        for p in page_results:
            csv_rows.append({
                "url": p.url,
                "aeo_readiness_score": p.aeo_readiness_score,
                "geo_signal_score": p.geo_signal_score,
                "answer_readiness": p.aeo_dimensions.get("answer_readiness", {}).score if hasattr(p.aeo_dimensions.get("answer_readiness"), "score") else "",
                "question_coverage": p.aeo_dimensions.get("question_coverage", {}).score if hasattr(p.aeo_dimensions.get("question_coverage"), "score") else "",
                "content_structure": p.aeo_dimensions.get("content_structure", {}).score if hasattr(p.aeo_dimensions.get("content_structure"), "score") else "",
                "schema_quality": p.aeo_dimensions.get("schema_quality", {}).score if hasattr(p.aeo_dimensions.get("schema_quality"), "score") else "",
                "crawler_accessibility": p.aeo_dimensions.get("crawler_accessibility", {}).score if hasattr(p.aeo_dimensions.get("crawler_accessibility"), "score") else "",
                "entity_clarity": p.geo_dimensions.get("entity_clarity", {}).score if hasattr(p.geo_dimensions.get("entity_clarity"), "score") else "",
                "source_readiness": p.geo_dimensions.get("source_readiness", {}).score if hasattr(p.geo_dimensions.get("source_readiness"), "score") else "",
                "factual_specificity": p.geo_dimensions.get("factual_specificity", {}).score if hasattr(p.geo_dimensions.get("factual_specificity"), "score") else "",
                "questions_count": len(p.questions),
                "direct_answers_count": sum(1 for q in p.questions if q.answer_detected),
                "author": p.citations.author or "",
                "publisher": p.citations.publisher or "",
            })

        fieldnames = [
            "url",
            "aeo_readiness_score",
            "geo_signal_score",
            "answer_readiness",
            "question_coverage",
            "content_structure",
            "schema_quality",
            "crawler_accessibility",
            "entity_clarity",
            "source_readiness",
            "factual_specificity",
            "questions_count",
            "direct_answers_count",
            "author",
            "publisher",
        ]
        with (target_dir / "aeo_pages.csv").open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

    return result
