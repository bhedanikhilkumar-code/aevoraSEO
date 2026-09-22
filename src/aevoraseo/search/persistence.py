"""
SQLite persistence for AevoraSEO Search, Local & Commercial Intelligence.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    SearchCommercialAnalysisResult,
    SearchCommercialDiffResult,
)


def init_search_db(db_path: Path) -> None:
    """Initialize database tables with indexes."""
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS search_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                target_url TEXT NOT NULL,
                brand_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                pages_analyzed INTEGER NOT NULL,
                headline_score REAL NOT NULL,
                intent_score REAL NOT NULL,
                commercial_score REAL NOT NULL,
                local_score REAL NOT NULL,
                comparison_score REAL NOT NULL,
                confidence TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS search_page_intents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                primary_intent TEXT NOT NULL,
                secondary_intents_json TEXT NOT NULL,
                primary_target_query TEXT NOT NULL,
                secondary_queries_json TEXT NOT NULL,
                intent_signals_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES search_snapshots(snapshot_id)
            );

            CREATE TABLE IF NOT EXISTS search_cannibalization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                query TEXT NOT NULL,
                intent TEXT NOT NULL,
                competing_urls_json TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES search_snapshots(snapshot_id)
            );

            CREATE TABLE IF NOT EXISTS search_local_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                url TEXT NOT NULL,
                has_local_business_schema INTEGER NOT NULL,
                schema_types_json TEXT NOT NULL,
                nap_present INTEGER NOT NULL,
                name TEXT,
                address TEXT,
                phone TEXT,
                has_clickable_tel INTEGER NOT NULL,
                has_map_embed_or_link INTEGER NOT NULL,
                service_areas_json TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES search_snapshots(snapshot_id)
            );

            CREATE TABLE IF NOT EXISTS search_commercial_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                url TEXT NOT NULL,
                page_type TEXT NOT NULL,
                cta_count INTEGER NOT NULL,
                high_intent_ctas_json TEXT NOT NULL,
                generic_ctas_json TEXT NOT NULL,
                friction_issues_json TEXT NOT NULL,
                trust_signals_json TEXT NOT NULL,
                has_phone_call_action INTEGER NOT NULL,
                has_messaging_action INTEGER NOT NULL,
                has_booking_action INTEGER NOT NULL,
                pricing_transparency TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES search_snapshots(snapshot_id)
            );

            CREATE TABLE IF NOT EXISTS search_diffs (
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

            CREATE INDEX IF NOT EXISTS idx_intents_snapshot ON search_page_intents(snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_cannibal_snapshot ON search_cannibalization(snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_local_snapshot ON search_local_signals(snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_comm_snapshot ON search_commercial_audits(snapshot_id);
        """)
        conn.commit()
    finally:
        conn.close()


def save_search_snapshot(db_path: Path, result: SearchCommercialAnalysisResult, snapshot_id: str) -> None:
    """Save complete search & commercial intelligence result to SQLite."""
    init_search_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        score = result.score
        cur.execute(
            """
            INSERT OR REPLACE INTO search_snapshots (
                snapshot_id, target_url, brand_name, created_at, pages_analyzed,
                headline_score, intent_score, commercial_score, local_score,
                comparison_score, confidence, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                result.target_url,
                result.brand_name,
                result.created_at,
                result.pages_analyzed,
                score.get("headline", 0.0),
                score.get("intent_query_targeting", 0.0),
                score.get("commercial_journey_cta", 0.0),
                score.get("local_visibility_signals", 0.0),
                score.get("comparison_buyer_support", 0.0),
                score.get("confidence", "low"),
                json.dumps({
                    "intent_distribution": result.intent_distribution,
                    "recommendations": result.recommendations,
                    "deductions": score.get("deductions", []),
                }),
            ),
        )

        for p in result.page_intents:
            cur.execute(
                """
                INSERT INTO search_page_intents (
                    snapshot_id, url, title, primary_intent, secondary_intents_json,
                    primary_target_query, secondary_queries_json, intent_signals_json, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    p.get("url", ""),
                    p.get("title", ""),
                    p.get("primary_intent", ""),
                    json.dumps(p.get("secondary_intents", [])),
                    p.get("primary_target_query", ""),
                    json.dumps(p.get("secondary_queries", [])),
                    json.dumps(p.get("intent_signals", {})),
                    p.get("confidence", 1.0),
                ),
            )

        for c in result.cannibalization_issues:
            cur.execute(
                """
                INSERT INTO search_cannibalization (
                    snapshot_id, query, intent, competing_urls_json,
                    similarity_score, risk_level, recommendation
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    c.get("query", ""),
                    c.get("intent", ""),
                    json.dumps(c.get("competing_urls", [])),
                    c.get("similarity_score", 0.0),
                    c.get("risk_level", "LOW"),
                    c.get("recommendation", ""),
                ),
            )

        for l in result.local_signals:
            cur.execute(
                """
                INSERT INTO search_local_signals (
                    snapshot_id, url, has_local_business_schema, schema_types_json,
                    nap_present, name, address, phone, has_clickable_tel,
                    has_map_embed_or_link, service_areas_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    l.get("url", ""),
                    1 if l.get("has_local_business_schema") else 0,
                    json.dumps(l.get("schema_types", [])),
                    1 if l.get("nap_present") else 0,
                    l.get("name"),
                    l.get("address"),
                    l.get("phone"),
                    1 if l.get("has_clickable_tel") else 0,
                    1 if l.get("has_map_embed_or_link") else 0,
                    json.dumps(l.get("service_areas_declared", [])),
                ),
            )

        for comm in result.commercial_journeys:
            cur.execute(
                """
                INSERT INTO search_commercial_audits (
                    snapshot_id, url, page_type, cta_count, high_intent_ctas_json,
                    generic_ctas_json, friction_issues_json, trust_signals_json,
                    has_phone_call_action, has_messaging_action, has_booking_action,
                    pricing_transparency
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    comm.get("url", ""),
                    comm.get("page_type", ""),
                    comm.get("cta_count", 0),
                    json.dumps(comm.get("high_intent_ctas", [])),
                    json.dumps(comm.get("generic_ctas", [])),
                    json.dumps(comm.get("friction_issues", [])),
                    json.dumps(comm.get("trust_signals", [])),
                    1 if comm.get("has_phone_call_action") else 0,
                    1 if comm.get("has_messaging_action") else 0,
                    1 if comm.get("has_booking_action") else 0,
                    comm.get("pricing_transparency", "no_pricing_info"),
                ),
            )

        conn.commit()
    finally:
        conn.close()


def load_search_snapshot(db_path: Path, snapshot_id: str) -> Optional[Dict[str, Any]]:
    """Load snapshot data from SQLite."""
    if not db_path.exists():
        return None
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM search_snapshots WHERE snapshot_id = ?", (snapshot_id,))
        row = cur.fetchone()
        if not row:
            return None

        meta = json.loads(row[11])
        score = {
            "headline": row[5],
            "intent_query_targeting": row[6],
            "commercial_journey_cta": row[7],
            "local_visibility_signals": row[8],
            "comparison_buyer_support": row[9],
            "confidence": row[10],
            "deductions": meta.get("deductions", []),
        }

        # Load page intents
        cur.execute("SELECT * FROM search_page_intents WHERE snapshot_id = ?", (snapshot_id,))
        page_intents = []
        for pi in cur.fetchall():
            page_intents.append({
                "url": pi[2],
                "title": pi[3],
                "primary_intent": pi[4],
                "secondary_intents": json.loads(pi[5]),
                "primary_target_query": pi[6],
                "secondary_queries": json.loads(pi[7]),
                "intent_signals": json.loads(pi[8]),
                "confidence": pi[9],
            })

        # Load cannibalization
        cur.execute("SELECT * FROM search_cannibalization WHERE snapshot_id = ?", (snapshot_id,))
        cannibalizations = []
        for cb in cur.fetchall():
            cannibalizations.append({
                "query": cb[2],
                "intent": cb[3],
                "competing_urls": json.loads(cb[4]),
                "similarity_score": cb[5],
                "risk_level": cb[6],
                "recommendation": cb[7],
            })

        # Load local signals
        cur.execute("SELECT * FROM search_local_signals WHERE snapshot_id = ?", (snapshot_id,))
        local_signals = []
        for ls in cur.fetchall():
            local_signals.append({
                "url": ls[2],
                "has_local_business_schema": bool(ls[3]),
                "schema_types": json.loads(ls[4]),
                "nap_present": bool(ls[5]),
                "name": ls[6],
                "address": ls[7],
                "phone": ls[8],
                "has_clickable_tel": bool(ls[9]),
                "has_map_embed_or_link": bool(ls[10]),
                "service_areas_declared": json.loads(ls[11]),
            })

        # Load commercial audits
        cur.execute("SELECT * FROM search_commercial_audits WHERE snapshot_id = ?", (snapshot_id,))
        commercial_journeys = []
        for ca in cur.fetchall():
            commercial_journeys.append({
                "url": ca[2],
                "page_type": ca[3],
                "cta_count": ca[4],
                "high_intent_ctas": json.loads(ca[5]),
                "generic_ctas": json.loads(ca[6]),
                "friction_issues": json.loads(ca[7]),
                "trust_signals": json.loads(ca[8]),
                "has_phone_call_action": bool(ca[9]),
                "has_messaging_action": bool(ca[10]),
                "has_booking_action": bool(ca[11]),
                "pricing_transparency": ca[12],
            })

        return {
            "snapshot_id": row[0],
            "target_url": row[1],
            "brand_name": row[2],
            "created_at": row[3],
            "pages_analyzed": row[4],
            "score": score,
            "page_intents": page_intents,
            "cannibalization_issues": cannibalizations,
            "local_signals": local_signals,
            "commercial_journeys": commercial_journeys,
            "intent_distribution": meta.get("intent_distribution", {}),
            "recommendations": meta.get("recommendations", []),
        }
    finally:
        conn.close()


def save_search_diff(db_path: Path, diff: SearchCommercialDiffResult) -> None:
    """Persist temporal snapshot difference to SQLite."""
    init_search_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        diff_id = f"{diff.before_snapshot_id}_to_{diff.after_snapshot_id}"
        cur.execute(
            """
            INSERT OR REPLACE INTO search_diffs (
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
                    "intent_transitions": diff.intent_transitions,
                    "new_cannibalizations": diff.new_cannibalizations,
                    "resolved_cannibalizations": diff.resolved_cannibalizations,
                    "commercial_improvements": diff.commercial_improvements,
                    "commercial_regressions": diff.commercial_regressions,
                    "local_signal_changes": diff.local_signal_changes,
                }),
            ),
        )
        conn.commit()
    finally:
        conn.close()
