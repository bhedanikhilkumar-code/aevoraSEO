"""
AevoraSEO Entity Knowledge Graph Builder
Builds, links, and evaluates directed entity graph topology and connectivity.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from .models import EntityEdge, EntityNode, SameAsLink


class EntityKnowledgeGraph:
    """
    Constructs a connected directed knowledge graph from extracted entity nodes, edges, and sameAs links.
    """

    def __init__(
        self,
        nodes: List[EntityNode],
        edges: List[EntityEdge],
        same_as_links: List[SameAsLink]
    ):
        self.nodes = {n.entity_id: n for n in nodes}
        self.edges = list(edges)
        self.same_as_links = list(same_as_links)

        # Wire sameAs links as external authority nodes and edges in graph
        for sa in self.same_as_links:
            if sa.is_valid_url:
                sa_node_id = f"ext:{sa.platform.lower()}_{hash(sa.url) % 100000}"
                if sa_node_id not in self.nodes:
                    self.nodes[sa_node_id] = EntityNode(
                        entity_id=sa_node_id,
                        entity_type="ExternalAuthorityProfile",
                        canonical_name=f"{sa.platform} ({sa.url})",
                        attributes={"url": sa.url, "platform": sa.platform, "is_high_authority": sa.is_high_authority},
                        is_first_party=False,
                        source_pages=[sa.found_on_url] if sa.found_on_url else [],
                        confidence_score=1.0,
                    )
                
                # Match to source entity if possible
                source_id = None
                for n in nodes:
                    if n.canonical_name.lower() == sa.entity_name.lower():
                        source_id = n.entity_id
                        break
                if not source_id and nodes:
                    source_id = nodes[0].entity_id

                if source_id:
                    self.edges.append(
                        EntityEdge(
                            source_id=source_id,
                            target_id=sa_node_id,
                            relationship_type="SAME_AS",
                            evidence_url=sa.found_on_url,
                            is_inferred=False,
                        )
                    )

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculates graph topology metrics: total nodes, edges, degree centrality, density.
        """
        n_count = len(self.nodes)
        e_count = len(self.edges)
        
        # Degree centrality calculation
        degrees: Dict[str, int] = {node_id: 0 for node_id in self.nodes}
        for e in self.edges:
            if e.source_id in degrees:
                degrees[e.source_id] += 1
            if e.target_id in degrees:
                degrees[e.target_id] += 1

        central_entity_id = max(degrees, key=degrees.get) if degrees else ""
        central_entity_name = self.nodes[central_entity_id].canonical_name if central_entity_id in self.nodes else ""

        isolated_nodes = [node_id for node_id, deg in degrees.items() if deg == 0]
        density = round(e_count / (n_count * (n_count - 1)), 4) if n_count > 1 else 0.0

        return {
            "node_count": n_count,
            "edge_count": e_count,
            "density": density,
            "central_entity_id": central_entity_id,
            "central_entity_name": central_entity_name,
            "isolated_node_count": len(isolated_nodes),
            "isolated_nodes": isolated_nodes[:10],
        }

    def to_graph_json(self) -> Dict[str, Any]:
        """
        Exports graph representation compatible with Cytoscape.js and D3.js.
        """
        nodes_data = [
            {
                "data": {
                    "id": n.entity_id,
                    "label": n.canonical_name,
                    "type": n.entity_type,
                    "is_first_party": n.is_first_party,
                    "confidence": n.confidence_score,
                }
            }
            for n in self.nodes.values()
        ]

        edges_data = [
            {
                "data": {
                    "id": f"edge_{i}",
                    "source": e.source_id,
                    "target": e.target_id,
                    "label": e.relationship_type,
                    "evidence": e.evidence_url,
                }
            }
            for i, e in enumerate(self.edges)
        ]

        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "metrics": self.calculate_metrics(),
        }
