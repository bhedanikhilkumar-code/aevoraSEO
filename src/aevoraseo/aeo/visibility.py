"""
AevoraSEO Observed Visibility Engine
Handles empirical external visibility records (e.g. SERP imports, manual citation logs, API feeds).
Enforces a strict architectural separation between observed visibility and analytical readiness scores.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from aevoraseo.aeo.models import ObservedVisibilityRecord


def load_observed_visibility_from_json(path: Path) -> List[ObservedVisibilityRecord]:
    """Loads empirical observation records from a JSON file."""
    records: List[ObservedVisibilityRecord] = []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    items = data if isinstance(data, list) else data.get("records", [])
    for item in items:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url", "")).strip()
        query = str(item.get("query", "")).strip()
        if not url:
            continue
        records.append(
            ObservedVisibilityRecord(
                query=query,
                engine=str(item.get("engine", "user_supplied")),
                observed=bool(item.get("observed", True)),
                url=url,
                position=int(item["position"]) if item.get("position") is not None else None,
                citation=bool(item.get("citation", False)),
                source=str(item.get("source", "imported")),
                observed_at=str(item.get("observed_at", "")),
                evidence_snippet=str(item["evidence_snippet"]) if item.get("evidence_snippet") else None,
            )
        )
    return records


def load_observed_visibility_from_csv(path: Path) -> List[ObservedVisibilityRecord]:
    """Loads empirical observation records from a CSV file."""
    records: List[ObservedVisibilityRecord] = []
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = str(row.get("url", "")).strip()
            if not url:
                continue
            pos_raw = row.get("position", "")
            pos = int(pos_raw) if pos_raw.isdigit() else None
            obs_raw = str(row.get("observed", "true")).lower()
            observed = obs_raw in ("true", "1", "yes")
            cit_raw = str(row.get("citation", "false")).lower()
            citation = cit_raw in ("true", "1", "yes")

            records.append(
                ObservedVisibilityRecord(
                    query=str(row.get("query", "")),
                    engine=str(row.get("engine", "user_supplied")),
                    observed=observed,
                    url=url,
                    position=pos,
                    citation=citation,
                    source=str(row.get("source", "imported")),
                    observed_at=str(row.get("observed_at", "")),
                    evidence_snippet=row.get("evidence_snippet"),
                )
            )
    return records


def load_observed_visibility(file_path: Path) -> List[ObservedVisibilityRecord]:
    """
    Dispatcher to load external observational records from JSON or CSV.
    Raises ValueError on unsupported format.
    """
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        return load_observed_visibility_from_json(file_path)
    elif suffix == ".csv":
        return load_observed_visibility_from_csv(file_path)
    else:
        raise ValueError(f"Unsupported visibility file format '{suffix}'. Supported: .json, .csv")
