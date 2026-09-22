"""
SQLite Persistence Engine for AevoraSEO Entity, Authority & Knowledge Intelligence Subsystem.
Guarantees clean connection teardown and robust schema initialization.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import EntityAnalysisResult, EntityDiffResult


ENTITY_SCHEMA = """
CREATE TABLE IF NOT EXISTS entity_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    target_url TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    total_nodes INTEGER NOT NULL,
    total_edges INTEGER NOT NULL,
    authority_score REAL NOT NULL,
    confidence TEXT NOT NULL,
    completeness_score REAL NOT NULL,
    consistency_score REAL NOT NULL,
    footprint_score REAL NOT NULL,
    expert_score REAL NOT NULL,
    raw_json TEXT
);

CREATE TABLE IF NOT EXISTS entity_nodes (
    entity_id TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    alternate_names TEXT,
    attributes_json TEXT,
    is_first_party INTEGER NOT NULL,
    source_pages_json TEXT,
    confidence_score REAL NOT NULL,
    PRIMARY KEY (entity_id, snapshot_id),
    FOREIGN KEY (snapshot_id) REFERENCES entity_snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS entity_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    evidence_url TEXT,
    is_inferred INTEGER NOT NULL,
    confidence REAL NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES entity_snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS entity_same_as (
    same_as_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    url TEXT NOT NULL,
    platform TEXT NOT NULL,
    is_valid_url INTEGER NOT NULL,
    is_high_authority INTEGER NOT NULL,
    found_on_url TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES entity_snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS entity_conflicts (
    conflict_id TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    conflict_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    entity_id TEXT,
    entity_name TEXT,
    description TEXT NOT NULL,
    details_json TEXT,
    PRIMARY KEY (conflict_id, snapshot_id),
    FOREIGN KEY (snapshot_id) REFERENCES entity_snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS entity_diffs (
    diff_id TEXT PRIMARY KEY,
    target_url TEXT NOT NULL,
    before_snapshot_id TEXT NOT NULL,
    after_snapshot_id TEXT NOT NULL,
    score_delta REAL NOT NULL,
    created_at TEXT NOT NULL,
    changes_json TEXT NOT NULL
);
"""


def init_entity_db(db_path: Path) -> None:
    """Initializes tables in entities.sqlite3 database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(ENTITY_SCHEMA)
        conn.commit()
    finally:
        conn.close()


def save_entity_snapshot(db_path: Path, result: EntityAnalysisResult, snapshot_id: str) -> None:
    """Persists complete EntityAnalysisResult to SQLite."""
    init_entity_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        # Snapshot metadata
        score = result.score
        conn.execute(
            """
            INSERT OR REPLACE INTO entity_snapshots (
                snapshot_id, target_url, brand_name, created_at,
                total_nodes, total_edges, authority_score, confidence,
                completeness_score, consistency_score, footprint_score, expert_score,
                raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                result.target_url,
                result.brand_name,
                result.created_at,
                len(result.nodes),
                len(result.edges),
                score.get("headline", 0.0),
                score.get("confidence", "low"),
                score.get("identity_completeness", 0.0),
                score.get("entity_consistency", 0.0),
                score.get("authority_footprint", 0.0),
                score.get("topical_expert_depth", 0.0),
                json.dumps(result.to_dict(), ensure_ascii=False),
            ),
        )

        # Clear existing child records for this snapshot if replacing
        conn.execute("DELETE FROM entity_nodes WHERE snapshot_id = ?", (snapshot_id,))
        conn.execute("DELETE FROM entity_edges WHERE snapshot_id = ?", (snapshot_id,))
        conn.execute("DELETE FROM entity_same_as WHERE snapshot_id = ?", (snapshot_id,))
        conn.execute("DELETE FROM entity_conflicts WHERE snapshot_id = ?", (snapshot_id,))

        # Nodes
        for n in result.nodes:
            conn.execute(
                """
                INSERT INTO entity_nodes (
                    entity_id, snapshot_id, entity_type, canonical_name,
                    alternate_names, attributes_json, is_first_party,
                    source_pages_json, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    n["entity_id"],
                    snapshot_id,
                    n["entity_type"],
                    n["canonical_name"],
                    json.dumps(n.get("alternate_names", []), ensure_ascii=False),
                    json.dumps(n.get("attributes", {}), ensure_ascii=False),
                    1 if n.get("is_first_party", True) else 0,
                    json.dumps(n.get("source_pages", []), ensure_ascii=False),
                    n.get("confidence_score", 1.0),
                ),
            )

        # Edges
        for e in result.edges:
            conn.execute(
                """
                INSERT INTO entity_edges (
                    snapshot_id, source_id, target_id, relationship_type,
                    evidence_url, is_inferred, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    e["source_id"],
                    e["target_id"],
                    e["relationship_type"],
                    e.get("evidence_url", ""),
                    1 if e.get("is_inferred") else 0,
                    e.get("confidence", 1.0),
                ),
            )

        # SameAs links
        for sa in result.same_as_links:
            conn.execute(
                """
                INSERT INTO entity_same_as (
                    snapshot_id, entity_name, url, platform,
                    is_valid_url, is_high_authority, found_on_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    sa["entity_name"],
                    sa["url"],
                    sa["platform"],
                    1 if sa.get("is_valid_url") else 0,
                    1 if sa.get("is_high_authority") else 0,
                    sa.get("found_on_url", ""),
                ),
            )

        # Conflicts
        for c in result.conflicts:
            conn.execute(
                """
                INSERT INTO entity_conflicts (
                    conflict_id, snapshot_id, conflict_type, severity,
                    entity_id, entity_name, description, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    c["conflict_id"],
                    snapshot_id,
                    c["conflict_type"],
                    c["severity"],
                    c.get("entity_id", ""),
                    c.get("entity_name", ""),
                    c["description"],
                    json.dumps(c.get("conflicting_evidence", {}), ensure_ascii=False),
                ),
            )

        conn.commit()
    finally:
        conn.close()


def save_entity_diff(db_path: Path, diff: EntityDiffResult) -> None:
    """Persists temporal entity comparison record to SQLite."""
    init_entity_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        diff_id = f"diff_{diff.before_snapshot_id}_{diff.after_snapshot_id}"
        conn.execute(
            """
            INSERT OR REPLACE INTO entity_diffs (
                diff_id, target_url, before_snapshot_id, after_snapshot_id,
                score_delta, created_at, changes_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                diff_id,
                diff.target_url,
                diff.before_snapshot_id,
                diff.after_snapshot_id,
                diff.score_delta,
                diff.created_at,
                json.dumps(diff.to_dict(), ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()
