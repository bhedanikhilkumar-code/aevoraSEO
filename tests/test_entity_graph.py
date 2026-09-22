"""
Unit tests for AevoraSEO Entity Knowledge Graph and Authority Scoring.
"""

from aevoraseo.entity.authority import calculate_entity_authority_score
from aevoraseo.entity.graph import EntityKnowledgeGraph
from aevoraseo.entity.models import EntityConflict, EntityEdge, EntityNode, SameAsLink


def test_entity_graph_topology_and_export():
    org = EntityNode(
        entity_id="org:nexus",
        entity_type="Organization",
        canonical_name="Nexus Technologies",
    )
    person = EntityNode(
        entity_id="person:sarah_connor",
        entity_type="Person",
        canonical_name="Sarah Connor",
    )
    edge = EntityEdge(
        source_id=person.entity_id,
        target_id=org.entity_id,
        relationship_type="FOUNDED_BY",
        evidence_url="https://nexus.example.com/about",
    )
    same_as = [
        SameAsLink(
            url="https://www.wikidata.org/wiki/Q999999",
            platform="Wikidata",
            entity_name="Nexus Technologies",
            is_valid_url=True,
            is_high_authority=True,
            found_on_url="https://nexus.example.com",
        )
    ]

    graph = EntityKnowledgeGraph([org, person], [edge], same_as)
    metrics = graph.calculate_metrics()

    assert metrics["node_count"] == 3  # org + person + wikidata node
    assert metrics["edge_count"] == 2  # founded_by + same_as
    assert metrics["central_entity_id"] == org.entity_id

    graph_json = graph.to_graph_json()
    assert len(graph_json["nodes"]) == 3
    assert len(graph_json["edges"]) == 2


def test_authority_score_calculation():
    org = EntityNode(
        entity_id="org:apex",
        entity_type="Organization",
        canonical_name="Apex Aerospace",
        attributes={
            "url": "https://apex.example.com",
            "logo": "https://apex.example.com/logo.png",
            "description": "Apex Aerospace develops propulsion mechanisms and deep space systems.",
            "telephone": "+1-800-555-4321",
            "foundingDate": "2018-05-20",
        },
    )
    person = EntityNode(
        entity_id="person:david_clark",
        entity_type="Person",
        canonical_name="David Clark",
        attributes={
            "jobTitle": "Chief Engineer",
            "description": "Aerospace propulsion pioneer with 20 years industry experience.",
        },
    )
    same_as = [
        SameAsLink(
            url="https://www.wikidata.org/wiki/Q111111",
            platform="Wikidata",
            entity_name="Apex Aerospace",
            is_valid_url=True,
            is_high_authority=True,
            found_on_url="https://apex.example.com",
        ),
        SameAsLink(
            url="https://www.linkedin.com/company/apex-aerospace",
            platform="LinkedIn",
            entity_name="Apex Aerospace",
            is_valid_url=True,
            is_high_authority=True,
            found_on_url="https://apex.example.com",
        ),
    ]
    conflicts = []
    missing_pages = []

    score = calculate_entity_authority_score([org, person], conflicts, same_as, missing_pages)

    assert score.identity_completeness == 25.0
    assert score.entity_consistency == 25.0
    assert score.authority_footprint >= 18.0  # Wikidata (10) + LinkedIn (8)
    assert score.topical_expert_depth >= 10.0  # Person with jobTitle & description
    assert score.headline >= 78.0
    assert score.confidence == "high"


def test_low_authority_deductions_and_confidence():
    # Only a simple organization without description, contact, or sameAs
    org = EntityNode(
        entity_id="org:bare",
        entity_type="Organization",
        canonical_name="Bare Bones LLC",
    )
    conflicts = [
        EntityConflict(
            conflict_id="c1",
            conflict_type="NAME_INCONSISTENCY",
            severity="HIGH",
            entity_id="org:bare",
            entity_name="Bare Bones LLC",
            description="Major brand contradiction",
        )
    ]
    same_as = []
    missing_pages = ["/about", "/contact"]

    score = calculate_entity_authority_score([org], conflicts, same_as, missing_pages)

    assert score.identity_completeness == 5.0
    assert score.entity_consistency <= 15.0  # High severity penalty -10
    assert score.authority_footprint == 0.0
    assert score.confidence == "low"
