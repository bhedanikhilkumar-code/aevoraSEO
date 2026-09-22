"""
AevoraSEO AEO / GEO SQLite Persistence Layer
Manages structured SQLite tables for snapshots, pages, questions, entities, and diffs.
Integrates with crawl.sqlite3 or standalone aeo.sqlite3 databases.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from aevoraseo.aeo.models import (
    AEODiffItem,
    AEODiffResult,
    PageAEOResult,
    SnapshotAEOResult,
)


AEO_SCHEMA = """
CREATE TABLE IF NOT EXISTS aeo_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    seed_url TEXT,
    analyzed_at TEXT,
    page_count INTEGER,
    average_aeo_score REAL,
    average_geo_score REAL,
    bot_matrix TEXT,
    summary_markdown TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS aeo_pages (
    snapshot_id TEXT,
    url TEXT,
    aeo_readiness_score REAL,
    geo_signal_score REAL,
    questions_count INTEGER,
    direct_answers_count INTEGER,
    schemas_count INTEGER,
    author TEXT,
    publisher TEXT,
    payload TEXT,
    PRIMARY KEY (snapshot_id, url)
);

CREATE TABLE IF NOT EXISTS aeo_questions (
    snapshot_id TEXT,
    url TEXT,
    question TEXT,
    answer_detected INTEGER,
    confidence REAL,
    answer_location TEXT,
    answer_text TEXT,
    PRIMARY KEY (snapshot_id, url, question)
);

CREATE TABLE IF NOT EXISTS aeo_entities (
    snapshot_id TEXT,
    url TEXT,
    entity_type TEXT,
    name TEXT,
    source TEXT,
    is_consistent INTEGER,
    PRIMARY KEY (snapshot_id, url, entity_type, name, source)
);

CREATE TABLE IF NOT EXISTS aeo_diffs (
    before_snapshot_id TEXT,
    after_snapshot_id TEXT,
    before_avg_aeo REAL,
    after_avg_aeo REAL,
    aeo_delta REAL,
    before_avg_geo REAL,
    after_avg_geo REAL,
    geo_delta REAL,
    compared_at TEXT,
    payload TEXT,
    PRIMARY KEY (before_snapshot_id, after_snapshot_id)
);

CREATE INDEX IF NOT EXISTS idx_aeo_pages_score ON aeo_pages(snapshot_id, aeo_readiness_score);
CREATE INDEX IF NOT EXISTS idx_aeo_questions_conf ON aeo_questions(snapshot_id, confidence);
CREATE INDEX IF NOT EXISTS idx_aeo_entities_type ON aeo_entities(snapshot_id, entity_type);
"""


def init_aeo_db(conn: sqlite3.Connection) -> None:
    """Initializes AEO schema tables and indexes."""
    conn.executescript(AEO_SCHEMA)
    conn.commit()


def persist_snapshot_aeo(result: SnapshotAEOResult, db_path: Path | str) -> None:
    """
    Persists a SnapshotAEOResult into SQLite.
    Creates or updates tables in an atomic transaction.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    try:
        init_aeo_db(conn)

        # 1. Insert or replace snapshot record
        conn.execute(
            """
            INSERT OR REPLACE INTO aeo_snapshots (
                snapshot_id, seed_url, analyzed_at, page_count,
                average_aeo_score, average_geo_score, bot_matrix,
                summary_markdown, payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.snapshot_id,
                result.seed_url,
                result.timestamp,
                result.page_count,
                result.average_aeo_readiness_score,
                result.average_geo_signal_score,
                json.dumps(result.bot_accessibility_matrix, ensure_ascii=False),
                result.summary_markdown,
                json.dumps(result.to_dict(), ensure_ascii=False),
            ),
        )

        # 2. Insert or replace pages
        for page in result.pages:
            author = page.citations.author or ""
            publisher = page.citations.publisher or ""
            conn.execute(
                """
                INSERT OR REPLACE INTO aeo_pages (
                    snapshot_id, url, aeo_readiness_score, geo_signal_score,
                    questions_count, direct_answers_count, schemas_count,
                    author, publisher, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.snapshot_id,
                    page.url,
                    page.aeo_readiness_score,
                    page.geo_signal_score,
                    len(page.questions),
                    sum(1 for q in page.questions if q.answer_detected),
                    len(page.schemas),
                    author,
                    publisher,
                    json.dumps(page.to_dict(), ensure_ascii=False),
                ),
            )

            # 3. Insert or replace questions
            for q in page.questions:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO aeo_questions (
                        snapshot_id, url, question, answer_detected,
                        confidence, answer_location, answer_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result.snapshot_id,
                        page.url,
                        q.question,
                        1 if q.answer_detected else 0,
                        q.confidence,
                        q.answer_location,
                        q.answer_text,
                    ),
                )

            # 4. Insert or replace entities
            for ent in page.entities:
                if ent.name:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO aeo_entities (
                            snapshot_id, url, entity_type, name, source, is_consistent
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            result.snapshot_id,
                            page.url,
                            ent.entity_type,
                            ent.name,
                            ent.source,
                            1 if ent.is_consistent else 0,
                        ),
                    )

        conn.commit()
    finally:
        conn.close()


def persist_aeo_diff(diff: AEODiffResult, db_path: Path | str) -> None:
    """
    Persists an AEODiffResult into SQLite.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    try:
        init_aeo_db(conn)

        from aevoraseo.network import utcnow

        conn.execute(
            """
            INSERT OR REPLACE INTO aeo_diffs (
                before_snapshot_id, after_snapshot_id,
                before_avg_aeo, after_avg_aeo, aeo_delta,
                before_avg_geo, after_avg_geo, geo_delta,
                compared_at, payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                diff.before_snapshot_id,
                diff.after_snapshot_id,
                diff.before_avg_aeo,
                diff.after_avg_aeo,
                diff.aeo_delta,
                diff.before_avg_geo,
                diff.after_avg_geo,
                diff.geo_delta,
                utcnow(),
                json.dumps(diff.to_dict(), ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def query_snapshot_aeo_summary(db_path: Path | str, snapshot_id: str) -> Optional[Dict[str, Any]]:
    """
    Queries SQLite for summary statistics of a snapshot's AEO results.
    """
    path = Path(db_path)
    if not path.exists():
        return None

    conn = sqlite3.connect(str(path))
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM aeo_snapshots WHERE snapshot_id = ?", (snapshot_id,)
        ).fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()
