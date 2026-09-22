"""
AevoraSEO Multi-Source Entity Extractor
Extracts typed Schema.org, Microdata, meta tags, and content entity signals with cycle guards.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from .models import EntityEdge, EntityNode, EntityType, SameAsLink
from .same_as import build_same_as_link


def _slugify(text: str) -> str:
    """Generates a clean deterministic identifier slug from text."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return slug or "unnamed"


def _normalize_name(name_raw: Any) -> str:
    """Extracts a clean string name from string or schema dictionary."""
    if isinstance(name_raw, dict):
        return str(name_raw.get("name") or name_raw.get("headline") or "").strip()
    if isinstance(name_raw, list) and name_raw:
        return _normalize_name(name_raw[0])
    return str(name_raw or "").strip()


def _normalize_list(val: Any) -> List[str]:
    """Converts a string or list of values into a list of cleaned non-empty strings."""
    if isinstance(val, str):
        s = val.strip()
        return [s] if s else []
    elif isinstance(val, list):
        res = []
        for x in val:
            if isinstance(x, str) and x.strip():
                res.append(x.strip())
            elif isinstance(x, dict):
                n = _normalize_name(x)
                if n:
                    res.append(n)
        return res
    return []


TYPE_PREFIXES = {
    "Organization": "org",
    "Corporation": "org",
    "LocalBusiness": "org",
    "Person": "person",
    "Product": "product",
    "Service": "service",
    "Place": "place",
    "Article": "article",
    "NewsArticle": "article",
    "BlogPosting": "article",
    "WebSite": "site",
    "WebPage": "page",
}


class EntityExtractor:
    """
    Extracts, deduplicates, and resolves entity nodes and relationship edges across crawled pages.
    """

    def __init__(self, max_depth: int = 25):
        self.max_depth = max_depth
        self.nodes: Dict[str, EntityNode] = {}
        self.edges: List[EntityEdge] = []
        self.same_as_links: List[SameAsLink] = []
        self.visited_ids: Set[int] = set()

    def extract_from_page(
        self,
        url: str,
        page_data: Dict[str, Any]
    ) -> List[EntityNode]:
        """
        Extracts entities from a single page's JSON-LD, meta tags, and content structure.
        """
        page_nodes: List[EntityNode] = []
        jsonld_blocks = page_data.get("jsonld", [])
        meta = page_data.get("meta", {})
        title = page_data.get("title", "")

        # 1. Parse JSON-LD blocks
        for block in jsonld_blocks:
            self._traverse_jsonld(block, url, depth=0)

        # 2. Extract fallback Organization from OpenGraph / meta if missing
        site_name_list = meta.get("og:site_name") or []
        if site_name_list:
            site_name = str(site_name_list[0]).strip()
            if site_name and not any(n.entity_type in ("Organization", "Corporation", "LocalBusiness") for n in self.nodes.values()):
                org_node = self._get_or_create_node(
                    entity_type=EntityType.ORGANIZATION.value,
                    name=site_name,
                    page_url=url,
                    attributes={"source": "meta:og:site_name"}
                )
                page_nodes.append(org_node)

        # 3. Extract fallback Person / author from meta tags
        author_list = meta.get("author") or meta.get("article:author") or []
        if author_list:
            for auth in author_list:
                auth_name = str(auth).strip()
                if auth_name and not auth_name.startswith("http"):
                    person_node = self._get_or_create_node(
                        entity_type=EntityType.PERSON.value,
                        name=auth_name,
                        page_url=url,
                        attributes={"source": "meta:author"}
                    )
                    page_nodes.append(person_node)

        return list(self.nodes.values())

    def _traverse_jsonld(self, node: Any, page_url: str, depth: int) -> Optional[EntityNode]:
        """
        Recursively extracts entities from a JSON-LD structure with cycle and depth guards.
        """
        if depth > self.max_depth or not isinstance(node, dict):
            return None

        node_id = id(node)
        if node_id in self.visited_ids:
            return None
        self.visited_ids.add(node_id)

        try:
            type_val = node.get("@type")
            if not type_val:
                # Still traverse children
                self._traverse_children(node, page_url, depth)
                return None

            types = type_val if isinstance(type_val, list) else [type_val]
            primary_type = types[0] if types else "Unknown"

            name = _normalize_name(node.get("name") or node.get("headline") or node.get("legalName"))
            if not name:
                self._traverse_children(node, page_url, depth)
                return None

            # Attributes extraction
            attributes: Dict[str, Any] = {}
            if "description" in node:
                attributes["description"] = str(node["description"]).strip()
            if "url" in node:
                attributes["url"] = str(node["url"]).strip()
            if "logo" in node:
                attributes["logo"] = _normalize_name(node["logo"]) or str(node["logo"]).strip()
            if "telephone" in node:
                attributes["telephone"] = str(node["telephone"]).strip()
            if "email" in node:
                attributes["email"] = str(node["email"]).strip()
            if "foundingDate" in node:
                attributes["foundingDate"] = str(node["foundingDate"]).strip()
            if "legalName" in node:
                attributes["legalName"] = str(node["legalName"]).strip()
            if "jobTitle" in node:
                attributes["jobTitle"] = str(node["jobTitle"]).strip()

            # Address parsing
            address = node.get("address")
            if isinstance(address, dict):
                attributes["address"] = {
                    "streetAddress": str(address.get("streetAddress", "")).strip(),
                    "addressLocality": str(address.get("addressLocality", "")).strip(),
                    "addressRegion": str(address.get("addressRegion", "")).strip(),
                    "postalCode": str(address.get("postalCode", "")).strip(),
                    "addressCountry": str(address.get("addressCountry", "")).strip(),
                }
            elif isinstance(address, str):
                attributes["address"] = {"streetAddress": address.strip()}

            # Geo coordinates
            geo = node.get("geo")
            if isinstance(geo, dict):
                attributes["geo"] = {
                    "latitude": geo.get("latitude"),
                    "longitude": geo.get("longitude"),
                }

            # Offers & pricing
            offers = node.get("offers")
            if isinstance(offers, dict):
                attributes["offers"] = {
                    "price": offers.get("price"),
                    "priceCurrency": offers.get("priceCurrency"),
                    "availability": offers.get("availability"),
                }

            # Ratings
            agg_rating = node.get("aggregateRating")
            if isinstance(agg_rating, dict):
                attributes["aggregateRating"] = {
                    "ratingValue": agg_rating.get("ratingValue"),
                    "reviewCount": agg_rating.get("reviewCount"),
                    "bestRating": agg_rating.get("bestRating"),
                }

            # Alternate names
            alternate_names = _normalize_list(node.get("alternateName"))

            # SameAs links
            same_as_raw = node.get("sameAs", [])
            same_as_urls = _normalize_list(same_as_raw)
            for sa_url in same_as_urls:
                sa_link = build_same_as_link(sa_url, entity_name=name, found_on_url=page_url)
                self.same_as_links.append(sa_link)
            attributes["same_as"] = same_as_urls

            # Create or update node
            entity_node = self._get_or_create_node(
                entity_type=primary_type,
                name=name,
                page_url=page_url,
                attributes=attributes,
                alternate_names=alternate_names,
            )

            # Relationship traversal: founder, author, publisher, provider, worksFor, memberOf
            self._extract_relationships(node, entity_node, page_url, depth)

            # Continue traversing child dicts/lists
            self._traverse_children(node, page_url, depth)

            return entity_node
        finally:
            self.visited_ids.remove(node_id)

    def _traverse_children(self, node: Dict[str, Any], page_url: str, depth: int) -> None:
        """Helper to traverse nested objects in values."""
        for k, val in node.items():
            if k in ("author", "founder", "publisher", "provider", "worksFor", "brand", "creator"):
                # Handled specifically in _extract_relationships
                continue
            if isinstance(val, dict):
                self._traverse_jsonld(val, page_url, depth + 1)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        self._traverse_jsonld(item, page_url, depth + 1)

    def _extract_relationships(
        self,
        raw_node: Dict[str, Any],
        parent_entity: EntityNode,
        page_url: str,
        depth: int
    ) -> None:
        """
        Extracts directed relationship edges connecting entities.
        """
        rel_specs = [
            ("founder", EntityType.PERSON.value, "FOUNDED_BY", True),
            ("founders", EntityType.PERSON.value, "FOUNDED_BY", True),
            ("author", EntityType.PERSON.value, "AUTHORED_BY", True),
            ("creator", EntityType.PERSON.value, "CREATED_BY", True),
            ("publisher", EntityType.ORGANIZATION.value, "PUBLISHED_BY", True),
            ("provider", EntityType.ORGANIZATION.value, "PROVIDED_BY", True),
            ("worksFor", EntityType.ORGANIZATION.value, "WORKS_FOR", False),
            ("alumnusOf", EntityType.ORGANIZATION.value, "ALUMNUS_OF", False),
            ("brand", EntityType.ORGANIZATION.value, "BRANDED_BY", True),
        ]

        for field_name, default_type, edge_label, is_reverse in rel_specs:
            if field_name not in raw_node:
                continue

            targets = raw_node[field_name]
            target_list = targets if isinstance(targets, list) else [targets]

            for t in target_list:
                if isinstance(t, dict):
                    t_type = t.get("@type") or default_type
                    t_name = _normalize_name(t.get("name") or t.get("headline"))
                    if t_name:
                        t_node = self._traverse_jsonld(t, page_url, depth + 1)
                        if not t_node:
                            t_node = self._get_or_create_node(t_type, t_name, page_url)
                        
                        src_id = t_node.entity_id if is_reverse else parent_entity.entity_id
                        tgt_id = parent_entity.entity_id if is_reverse else t_node.entity_id
                        
                        self.edges.append(
                            EntityEdge(
                                source_id=src_id,
                                target_id=tgt_id,
                                relationship_type=edge_label,
                                evidence_url=page_url,
                                is_inferred=False,
                            )
                        )
                elif isinstance(t, str) and t.strip():
                    t_name = t.strip()
                    t_node = self._get_or_create_node(default_type, t_name, page_url)
                    src_id = t_node.entity_id if is_reverse else parent_entity.entity_id
                    tgt_id = parent_entity.entity_id if is_reverse else t_node.entity_id
                    self.edges.append(
                        EntityEdge(
                            source_id=src_id,
                            target_id=tgt_id,
                            relationship_type=edge_label,
                            evidence_url=page_url,
                            is_inferred=False,
                        )
                    )

    def _get_or_create_node(
        self,
        entity_type: str,
        name: str,
        page_url: str,
        attributes: Optional[Dict[str, Any]] = None,
        alternate_names: Optional[List[str]] = None
    ) -> EntityNode:
        """
        Retrieves existing entity node or instantiates a new one, merging observations.
        """
        canonical_type = entity_type or EntityType.UNKNOWN.value
        clean_name = name.strip()
        slug = _slugify(clean_name)
        type_prefix = TYPE_PREFIXES.get(canonical_type, canonical_type.lower()[:4])
        entity_id = f"{type_prefix}:{slug}"

        if entity_id in self.nodes:
            existing = self.nodes[entity_id]
            if page_url and page_url not in existing.source_pages:
                existing.source_pages.append(page_url)
            if alternate_names:
                for alt in alternate_names:
                    if alt not in existing.alternate_names and alt.lower() != existing.canonical_name.lower():
                        existing.alternate_names.append(alt)
            if attributes:
                for k, v in attributes.items():
                    if k not in existing.attributes or not existing.attributes[k]:
                        existing.attributes[k] = v
            return existing

        node = EntityNode(
            entity_id=entity_id,
            entity_type=canonical_type,
            canonical_name=clean_name,
            alternate_names=alternate_names or [],
            attributes=attributes or {},
            is_first_party=True,
            source_pages=[page_url] if page_url else [],
            confidence_score=1.0,
        )
        self.nodes[entity_id] = node
        return node
