"""
SQLite persistence for Backlink and Reputation Intelligence observations.
Ensures deterministic storage, clean Windows connection handling, and structured queries.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS backlink_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    target TEXT NOT NULL,
    brand TEXT,
    created_at TEXT NOT NULL,
    sources_supplied INTEGER,
    sources_checked INTEGER,
    sources_remaining INTEGER,
    observed_link_pages INTEGER,
    observed_mention_pages INTEGER,
    unverified_pages INTEGER,
    note TEXT
);

CREATE TABLE IF NOT EXISTS backlink_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    final_url TEXT,
    publisher_group TEXT,
    verification TEXT,
    representation TEXT,
    status_code INTEGER,
    error TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES backlink_snapshots(snapshot_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS backlink_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    target_url TEXT NOT NULL,
    target_path TEXT,
    anchor_text TEXT,
    rel TEXT,
    is_dofollow INTEGER,
    context_text TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES backlink_snapshots(snapshot_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS backlink_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    excerpt TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES backlink_snapshots(snapshot_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reputation_assessments (
    assessment_id TEXT PRIMARY KEY,
    snapshot_id TEXT,
    target TEXT NOT NULL,
    brand TEXT,
    model_version TEXT NOT NULL,
    score REAL,
    score_low REAL,
    score_high REAL,
    score_status TEXT,
    confidence TEXT,
    sample_quality_estimate REAL,
    evidence_factor REAL,
    checked_at TEXT NOT NULL,
    payload TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES backlink_snapshots(snapshot_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS reputation_diffs (
    diff_id TEXT PRIMARY KEY,
    before_assessment_id TEXT,
    after_assessment_id TEXT,
    before_score REAL,
    after_score REAL,
    score_delta REAL,
    new_links_count INTEGER,
    lost_links_count INTEGER,
    new_mentions_count INTEGER,
    lost_mentions_count INTEGER,
    compared_at TEXT NOT NULL,
    payload TEXT
);

CREATE INDEX IF NOT EXISTS idx_backlink_sources_snapshot ON backlink_sources(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_backlink_links_snapshot ON backlink_links(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_backlink_mentions_snapshot ON backlink_mentions(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_reputation_target ON reputation_assessments(target);
"""


def init_backlink_db(db_path: Path | str) -> None:
    """Initialize database tables with pragma integrity."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def persist_backlink_verification(
    db_path: Path | str,
    verification: Dict[str, Any],
    snapshot_id: Optional[str] = None,
) -> str:
    """Store verification evidence into SQLite and return the snapshot_id."""
    init_backlink_db(db_path)
    sid = snapshot_id or str(uuid.uuid4())[:12]
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute(
            """
            INSERT OR REPLACE INTO backlink_snapshots (
                snapshot_id, target, brand, created_at,
                sources_supplied, sources_checked, sources_remaining,
                observed_link_pages, observed_mention_pages, unverified_pages, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sid,
                verification.get("target", ""),
                verification.get("brand", ""),
                verification.get("checked_at", ""),
                verification.get("sources_supplied", 0),
                verification.get("sources_checked", 0),
                verification.get("sources_remaining", 0),
                verification.get("observed_link_pages", 0),
                verification.get("observed_mention_pages", 0),
                verification.get("unverified_pages", 0),
                verification.get("note", ""),
            ),
        )

        for row in verification.get("results", []):
            source_url = row.get("source_url", "")
            final_url = row.get("final_url") or source_url
            pub_group = row.get("publisher_group", "")
            if not pub_group:
                host_str = (urlsplit(final_url).hostname or "").lower().removeprefix("www.")
                pub_group = host_str

            conn.execute(
                """
                INSERT INTO backlink_sources (
                    snapshot_id, source_url, final_url, publisher_group,
                    verification, representation, status_code, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sid,
                    source_url,
                    final_url,
                    pub_group,
                    row.get("verification", ""),
                    row.get("representation", ""),
                    row.get("status", 0),
                    row.get("error", ""),
                ),
            )

            for link in row.get("target_links", []):
                t_url = link.get("url", "")
                t_path = urlsplit(t_url).path or "/"
                anchor = link.get("anchor", "") or link.get("text", "") or ""
                rels = link.get("rel", [])
                rel_str = " ".join(sorted(rels)) if isinstance(rels, list) else str(rels)
                rel_set = {r.lower() for r in (rels if isinstance(rels, list) else rel_str.split())}
                is_dofollow = 1 if not any(r in ("nofollow", "ugc", "sponsored") for r in rel_set) else 0
                ctx = link.get("context", "") or link.get("excerpt", "") or ""

                conn.execute(
                    """
                    INSERT INTO backlink_links (
                        snapshot_id, source_url, target_url, target_path,
                        anchor_text, rel, is_dofollow, context_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sid,
                        source_url,
                        t_url,
                        t_path,
                        anchor,
                        rel_str,
                        is_dofollow,
                        ctx,
                    ),
                )

            for mention in row.get("brand_mentions", []):
                b_name = mention.get("name", "") if isinstance(mention, dict) else str(mention)
                exc = mention.get("excerpt", "") if isinstance(mention, dict) else ""
                conn.execute(
                    """
                    INSERT INTO backlink_mentions (
                        snapshot_id, source_url, brand_name, excerpt
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        sid,
                        source_url,
                        b_name,
                        exc,
                    ),
                )

        conn.commit()
    finally:
        conn.close()
    return sid


def load_backlink_snapshot(
    db_path: Path | str,
    snapshot_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Load a backlink snapshot by ID, or the most recent one if ID is omitted."""
    path = Path(db_path)
    if not path.exists():
        return None
    conn = sqlite3.connect(str(path))
    try:
        conn.row_factory = sqlite3.Row
        if snapshot_id:
            cur = conn.execute(
                "SELECT * FROM backlink_snapshots WHERE snapshot_id = ?", (snapshot_id,)
            )
        else:
            cur = conn.execute(
                "SELECT * FROM backlink_snapshots ORDER BY created_at DESC LIMIT 1"
            )
        snap_row = cur.fetchone()
        if not snap_row:
            return None

        sid = snap_row["snapshot_id"]
        result = dict(snap_row)

        sources_rows = conn.execute(
            "SELECT * FROM backlink_sources WHERE snapshot_id = ?", (sid,)
        ).fetchall()

        results_list = []
        for s in sources_rows:
            s_dict = dict(s)
            s_url = s_dict["source_url"]

            links = conn.execute(
                "SELECT target_url AS url, target_path, anchor_text AS text, rel, is_dofollow, context_text AS context "
                "FROM backlink_links WHERE snapshot_id = ? AND source_url = ?",
                (sid, s_url),
            ).fetchall()
            link_list = []
            for l in links:
                l_dict = dict(l)
                l_dict["rel"] = l_dict["rel"].split() if l_dict["rel"] else []
                link_list.append(l_dict)

            mentions = conn.execute(
                "SELECT brand_name AS name, excerpt FROM backlink_mentions WHERE snapshot_id = ? AND source_url = ?",
                (sid, s_url),
            ).fetchall()

            s_dict["target_links"] = link_list
            s_dict["brand_mentions"] = [dict(m) for m in mentions]
            results_list.append(s_dict)

        result["results"] = results_list
        return result
    finally:
        conn.close()


def persist_reputation_assessment(
    db_path: Path | str,
    assessment: Dict[str, Any],
    snapshot_id: Optional[str] = None,
    assessment_id: Optional[str] = None,
) -> str:
    """Persist reputation assessment output into SQLite."""
    init_backlink_db(db_path)
    aid = assessment_id or str(uuid.uuid4())[:12]
    score_range = assessment.get("score_range") or [None, None]
    score_low = score_range[0] if len(score_range) > 0 else None
    score_high = score_range[1] if len(score_range) > 1 else None

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute(
            """
            INSERT OR REPLACE INTO reputation_assessments (
                assessment_id, snapshot_id, target, brand, model_version,
                score, score_low, score_high, score_status, confidence,
                sample_quality_estimate, evidence_factor, checked_at, payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                aid,
                snapshot_id,
                assessment.get("target", ""),
                assessment.get("brand", ""),
                assessment.get("model_version", "1.1"),
                assessment.get("score"),
                score_low,
                score_high,
                assessment.get("score_status", ""),
                assessment.get("confidence", ""),
                assessment.get("sample_quality_estimate"),
                (assessment.get("evidence_adjustment") or {}).get("factor"),
                assessment.get("checked_at", ""),
                json.dumps(assessment, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return aid


def load_reputation_assessment(
    db_path: Path | str,
    assessment_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve full reputation assessment payload from SQLite."""
    path = Path(db_path)
    if not path.exists():
        return None
    conn = sqlite3.connect(str(path))
    try:
        conn.row_factory = sqlite3.Row
        if assessment_id:
            cur = conn.execute(
                "SELECT payload FROM reputation_assessments WHERE assessment_id = ?",
                (assessment_id,),
            )
        else:
            cur = conn.execute(
                "SELECT payload FROM reputation_assessments ORDER BY checked_at DESC LIMIT 1"
            )
        row = cur.fetchone()
        if not row or not row["payload"]:
            return None
        return json.loads(row["payload"])
    finally:
        conn.close()


def persist_reputation_diff(
    db_path: Path | str,
    diff: Dict[str, Any],
) -> str:
    """Store reputation before/after diff into SQLite."""
    init_backlink_db(db_path)
    did = diff.get("diff_id") or str(uuid.uuid4())[:12]
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO reputation_diffs (
                diff_id, before_assessment_id, after_assessment_id,
                before_score, after_score, score_delta,
                new_links_count, lost_links_count,
                new_mentions_count, lost_mentions_count,
                compared_at, payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                did,
                diff.get("before_id", ""),
                diff.get("after_id", ""),
                diff.get("before_score"),
                diff.get("after_score"),
                diff.get("score_delta"),
                len(diff.get("new_backlinks", [])),
                len(diff.get("lost_backlinks", [])),
                len(diff.get("new_mentions", [])),
                len(diff.get("lost_mentions", [])),
                diff.get("compared_at", ""),
                json.dumps(diff, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return did


def load_reputation_diff(
    db_path: Path | str,
    diff_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve full reputation diff payload from SQLite."""
    path = Path(db_path)
    if not path.exists():
        return None
    conn = sqlite3.connect(str(path))
    try:
        conn.row_factory = sqlite3.Row
        if diff_id:
            cur = conn.execute(
                "SELECT payload FROM reputation_diffs WHERE diff_id = ?",
                (diff_id,),
            )
        else:
            cur = conn.execute(
                "SELECT payload FROM reputation_diffs ORDER BY compared_at DESC LIMIT 1"
            )
        row = cur.fetchone()
        if not row or not row["payload"]:
            return None
        return json.loads(row["payload"])
    finally:
        conn.close()
