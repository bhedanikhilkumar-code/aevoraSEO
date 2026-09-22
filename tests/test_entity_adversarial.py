"""
Adversarial and Security tests for AevoraSEO Entity & Authority subsystem.
"""

from pathlib import Path

from aevoraseo.entity.extractor import EntityExtractor
from aevoraseo.entity.models import EntityAnalysisResult, EntityNode
from aevoraseo.entity.persistence import init_entity_db, save_entity_snapshot
from aevoraseo.entity.reporter import export_conflicts_csv, export_entities_csv, sanitize_csv_cell


def test_sanitize_csv_cell_formula_injection():
    # Direct formula injection payloads
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_cell("-2+3") == "'-2+3"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_csv_cell("\t=HYPERLINK()") == "'\t=HYPERLINK()"
    assert sanitize_csv_cell("\r+DANGER") == "'\r+DANGER"

    # Safe strings must not be prepended with quote
    assert sanitize_csv_cell("Normal Entity Name") == "Normal Entity Name"
    assert sanitize_csv_cell("https://example.com") == "https://example.com"
    assert sanitize_csv_cell(12345) == "12345"
    assert sanitize_csv_cell(None) == ""


def test_csv_export_neutralizes_injection():
    nodes = [
        {
            "entity_id": "=cmd|' /C calc'!A0",
            "entity_type": "@SUM(1,2)",
            "canonical_name": "+Malicious Entity",
            "alternate_names": ["-Evil Alias"],
            "is_first_party": True,
            "source_pages": ["https://evil.example.com"],
        }
    ]
    csv_str = export_entities_csv(nodes)
    assert "'=cmd|" in csv_str
    assert "'@SUM(" in csv_str
    assert "'+Malicious" in csv_str
    assert "'-Evil" in csv_str


def test_cyclical_jsonld_does_not_infinite_loop():
    extractor = EntityExtractor(max_depth=10)

    # Construct circular JSON-LD structure
    node_a = {"@type": "Organization", "name": "Cycle Org A"}
    node_b = {"@type": "Person", "name": "Cycle Person B"}
    node_a["founder"] = node_b
    node_b["worksFor"] = node_a

    page_data = {"jsonld": [node_a]}

    # Traversal must terminate safely without RecursionError
    extractor.extract_from_page("https://example.com", page_data)
    assert "org:cycle_org_a" in extractor.nodes
    assert "person:cycle_person_b" in extractor.nodes


def test_deep_jsonld_boundary():
    extractor = EntityExtractor(max_depth=5)

    # Build 10-level nested structure
    curr = {"@type": "Organization", "name": "Deep Leaf"}
    for i in range(10):
        curr = {"@type": "Thing", "sub": curr}

    page_data = {"jsonld": [curr]}
    # Must not crash
    extractor.extract_from_page("https://example.com", page_data)


def test_sqlite_handle_closed_properly(tmp_path: Path):
    db_file = tmp_path / "test_entities.sqlite3"
    init_entity_db(db_file)

    result = EntityAnalysisResult(
        target_url="https://example.com",
        brand_name="Example",
        created_at="2026-09-22T00:00:00Z",
        primary_organization={"canonical_name": "Example Corp"},
        nodes=[
            {
                "entity_id": "org:example",
                "entity_type": "Organization",
                "canonical_name": "Example Corp",
                "alternate_names": [],
                "attributes": {},
                "is_first_party": True,
                "source_pages": [],
                "confidence_score": 1.0,
            }
        ],
        edges=[],
        same_as_links=[],
        conflicts=[],
        missing_entity_pages=[],
        score={"headline": 50.0, "confidence": "medium"},
    )

    save_entity_snapshot(db_file, result, snapshot_id="snap_test")

    # Verify database file can be unlinked immediately on Windows without handle locking
    db_file.unlink()
    assert not db_file.exists()
