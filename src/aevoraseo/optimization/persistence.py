"""
SQLite persistence for AevoraSEO Content & Optimization Intelligence.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    OptimizationDiff,
    OptimizationResult,
)


def init_optimization_db(db_path: Path) -> None:
    """Initialize database tables and indexes."""
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS optimization_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                target_url TEXT NOT NULL,
                brand_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                pages_analyzed INTEGER NOT NULL,
                headline_score REAL NOT NULL,
                metadata_heading_score REAL NOT NULL,
                content_quality_depth_score REAL NOT NULL,
                internal_link_cluster_score REAL NOT NULL,
                schema_structured_score REAL NOT NULL,
                confidence TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS optimization_page_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                url TEXT NOT NULL,
                title_status TEXT NOT NULL,
                title_text TEXT NOT NULL,
                title_rec TEXT NOT NULL,
                meta_status TEXT NOT NULL,
                meta_text TEXT NOT NULL,
                meta_rec TEXT NOT NULL,
                h1_count INTEGER NOT NULL,
                has_skipped_levels INTEGER NOT NULL,
                heading_rec TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES optimization_snapshots(snapshot_id)
            );

            CREATE TABLE IF NOT EXISTS optimization_answer_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                url TEXT NOT NULL,
                question_or_topic TEXT NOT NULL,
                opportunity_type TEXT NOT NULL,
                target_format TEXT NOT NULL,
                is_answered INTEGER NOT NULL,
                draft_answer_blueprint TEXT NOT NULL,
                confidence REAL NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES optimization_snapshots(snapshot_id)
            );

            CREATE TABLE IF NOT EXISTS optimization_topic_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                cluster_id TEXT NOT NULL,
                topic_name TEXT NOT NULL,
                pillar_url TEXT,
                spoke_urls_json TEXT NOT NULL,
                cluster_health_score REAL NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES optimization_snapshots(snapshot_id)
            );

            CREATE TABLE IF NOT EXISTS optimization_content_briefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                brief_id TEXT NOT NULL,
                url TEXT NOT NULL,
                primary_query TEXT NOT NULL,
                search_intent TEXT NOT NULL,
                target_word_count INTEGER NOT NULL,
                required_sections_json TEXT NOT NULL,
                direct_answer_targets_json TEXT NOT NULL,
                recommended_schema TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES optimization_snapshots(snapshot_id)
            );

            CREATE TABLE IF NOT EXISTS optimization_diffs (
                diff_id TEXT PRIMARY KEY,
                before_snapshot_id TEXT NOT NULL,
                after_snapshot_id TEXT NOT NULL,
                target_url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                score_before REAL NOT NULL,
                score_after REAL NOT NULL,
                score_delta REAL NOT NULL,
                transitions_json TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_opt_audits_snapshot ON optimization_page_audits(snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_opt_answers_snapshot ON optimization_answer_opportunities(snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_opt_clusters_snapshot ON optimization_topic_clusters(snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_opt_briefs_snapshot ON optimization_content_briefs(snapshot_id);
        """)
        conn.commit()
    finally:
        conn.close()


def save_optimization_snapshot(
    db_path: Path,
    result: OptimizationResult,
    snapshot_id: str,
) -> None:
    """Persist complete optimization result to SQLite."""
    init_optimization_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        score = result.score
        cur.execute(
            """
            INSERT OR REPLACE INTO optimization_snapshots (
                snapshot_id, target_url, brand_name, created_at, pages_analyzed,
                headline_score, metadata_heading_score, content_quality_depth_score,
                internal_link_cluster_score, schema_structured_score, confidence, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                result.target_url,
                result.brand_name,
                result.created_at,
                result.pages_analyzed,
                score.get("headline", 0.0),
                score.get("metadata_heading_score", 0.0),
                score.get("content_quality_depth_score", 0.0),
                score.get("internal_link_cluster_score", 0.0),
                score.get("schema_structured_score", 0.0),
                score.get("confidence", "low"),
                json.dumps({
                    "deductions": score.get("deductions", []),
                    "recommendations": result.recommendations,
                    "content_gaps": result.content_gaps,
                    "refresh_candidates": result.refresh_candidates,
                    "roadmap_items": result.roadmap_items,
                    "orphan_pages": result.orphan_pages,
                }),
            ),
        )

        # Page audits (combine title, meta, heading info by URL)
        meta_by_url = {m.get("url"): m for m in result.meta_audits}
        heading_by_url = {h.get("url"): h for h in result.heading_audits}

        for t in result.title_audits:
            u = t.get("url", "")
            m = meta_by_url.get(u, {})
            h = heading_by_url.get(u, {})
            cur.execute(
                """
                INSERT INTO optimization_page_audits (
                    snapshot_id, url, title_status, title_text, title_rec,
                    meta_status, meta_text, meta_rec, h1_count,
                    has_skipped_levels, heading_rec
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    u,
                    t.get("status", ""),
                    t.get("title", ""),
                    t.get("recommendation", ""),
                    m.get("status", ""),
                    m.get("description", ""),
                    m.get("recommendation", ""),
                    h.get("h1_count", 0),
                    1 if h.get("has_skipped_levels") else 0,
                    h.get("recommendation", ""),
                ),
            )

        # Answer opportunities
        for a in result.direct_answer_opportunities:
            cur.execute(
                """
                INSERT INTO optimization_answer_opportunities (
                    snapshot_id, url, question_or_topic, opportunity_type,
                    target_format, is_answered, draft_answer_blueprint, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    a.get("url", ""),
                    a.get("question_or_topic", ""),
                    a.get("opportunity_type", ""),
                    a.get("target_format", ""),
                    1 if a.get("is_answered") else 0,
                    a.get("draft_answer_blueprint", ""),
                    a.get("confidence", 0.0),
                ),
            )

        # Topic clusters
        for c in result.topic_clusters:
            cur.execute(
                """
                INSERT INTO optimization_topic_clusters (
                    snapshot_id, cluster_id, topic_name, pillar_url,
                    spoke_urls_json, cluster_health_score
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    c.get("cluster_id", ""),
                    c.get("topic_name", ""),
                    c.get("pillar_url"),
                    json.dumps(c.get("spoke_urls", [])),
                    c.get("cluster_health_score", 0.0),
                ),
            )

        # Content briefs
        for b in result.content_briefs:
            cur.execute(
                """
                INSERT INTO optimization_content_briefs (
                    snapshot_id, brief_id, url, primary_query, search_intent,
                    target_word_count, required_sections_json, direct_answer_targets_json,
                    recommended_schema
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    b.get("brief_id", ""),
                    b.get("url", ""),
                    b.get("primary_query", ""),
                    b.get("search_intent", ""),
                    b.get("target_word_count", 0),
                    json.dumps(b.get("required_sections", [])),
                    json.dumps(b.get("direct_answer_targets", [])),
                    b.get("recommended_schema", ""),
                ),
            )

        conn.commit()
    finally:
        conn.close()


def load_optimization_snapshot(db_path: Path, snapshot_id: str) -> Optional[Dict[str, Any]]:
    """Loads snapshot data from SQLite."""
    if not db_path.exists():
        return None
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM optimization_snapshots WHERE snapshot_id = ?", (snapshot_id,))
        row = cur.fetchone()
        if not row:
            return None

        meta = json.loads(row[11])
        score = {
            "headline": row[5],
            "metadata_heading_score": row[6],
            "content_quality_depth_score": row[7],
            "internal_link_cluster_score": row[8],
            "schema_structured_score": row[9],
            "confidence": row[10],
            "deductions": meta.get("deductions", []),
        }

        # Page audits
        cur.execute("SELECT * FROM optimization_page_audits WHERE snapshot_id = ?", (snapshot_id,))
        page_audits = []
        for r in cur.fetchall():
            page_audits.append({
                "url": r[2],
                "title_status": r[3],
                "title_text": r[4],
                "title_rec": r[5],
                "meta_status": r[6],
                "meta_text": r[7],
                "meta_rec": r[8],
                "h1_count": r[9],
                "has_skipped_levels": bool(r[10]),
                "heading_rec": r[11],
            })

        # Answer opportunities
        cur.execute("SELECT * FROM optimization_answer_opportunities WHERE snapshot_id = ?", (snapshot_id,))
        answer_opportunities = []
        for r in cur.fetchall():
            answer_opportunities.append({
                "url": r[2],
                "question_or_topic": r[3],
                "opportunity_type": r[4],
                "target_format": r[5],
                "is_answered": bool(r[6]),
                "draft_answer_blueprint": r[7],
                "confidence": r[8],
            })

        # Topic clusters
        cur.execute("SELECT * FROM optimization_topic_clusters WHERE snapshot_id = ?", (snapshot_id,))
        topic_clusters = []
        for r in cur.fetchall():
            topic_clusters.append({
                "cluster_id": r[2],
                "topic_name": r[3],
                "pillar_url": r[4],
                "spoke_urls": json.loads(r[5]),
                "cluster_health_score": r[6],
            })

        # Content briefs
        cur.execute("SELECT * FROM optimization_content_briefs WHERE snapshot_id = ?", (snapshot_id,))
        content_briefs = []
        for r in cur.fetchall():
            content_briefs.append({
                "brief_id": r[2],
                "url": r[3],
                "primary_query": r[4],
                "search_intent": r[5],
                "target_word_count": r[6],
                "required_sections": json.loads(r[7]),
                "direct_answer_targets": json.loads(r[8]),
                "recommended_schema": r[9],
            })

        return {
            "snapshot_id": row[0],
            "target_url": row[1],
            "brand_name": row[2],
            "created_at": row[3],
            "pages_analyzed": row[4],
            "score": score,
            "page_audits": page_audits,
            "answer_opportunities": answer_opportunities,
            "topic_clusters": topic_clusters,
            "content_briefs": content_briefs,
            "content_gaps": meta.get("content_gaps", []),
            "refresh_candidates": meta.get("refresh_candidates", []),
            "roadmap_items": meta.get("roadmap_items", []),
            "recommendations": meta.get("recommendations", []),
            "orphan_pages": meta.get("orphan_pages", []),
        }
    finally:
        conn.close()


def save_optimization_diff(db_path: Path, diff: OptimizationDiff) -> None:
    """Persists temporal optimization snapshot diff to SQLite."""
    init_optimization_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        diff_id = f"{diff.before_snapshot_id}_to_{diff.after_snapshot_id}"
        cur.execute(
            """
            INSERT OR REPLACE INTO optimization_diffs (
                diff_id, before_snapshot_id, after_snapshot_id, target_url,
                created_at, score_before, score_after, score_delta, transitions_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                diff_id,
                diff.before_snapshot_id,
                diff.after_snapshot_id,
                diff.target_url,
                diff.created_at,
                diff.score_before,
                diff.score_after,
                diff.score_delta,
                json.dumps({
                    "transition_summary": diff.transition_summary,
                    "dimension_deltas": diff.dimension_deltas,
                    "resolved_issues": diff.resolved_issues,
                    "new_issues": diff.new_issues,
                    "new_answer_opportunities": diff.new_answer_opportunities,
                    "cluster_evolution": diff.cluster_evolution,
                }),
            ),
        )
        conn.commit()
    finally:
        conn.close()
