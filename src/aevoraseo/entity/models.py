"""
Data models for AevoraSEO Entity, Authority & Knowledge Intelligence Subsystem.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EntityType(str, Enum):
    ORGANIZATION = "Organization"
    CORPORATION = "Corporation"
    LOCAL_BUSINESS = "LocalBusiness"
    PERSON = "Person"
    PRODUCT = "Product"
    SERVICE = "Service"
    PLACE = "Place"
    ARTICLE = "Article"
    BLOG_POSTING = "BlogPosting"
    NEWS_ARTICLE = "NewsArticle"
    WEBSITE = "WebSite"
    WEBPAGE = "WebPage"
    EVENT = "Event"
    PROFILE_PAGE = "ProfilePage"
    UNKNOWN = "Unknown"


class AuthorityPlatform(str, Enum):
    WIKIPEDIA = "Wikipedia"
    WIKIDATA = "Wikidata"
    LINKEDIN = "LinkedIn"
    GITHUB = "GitHub"
    TWITTER = "Twitter/X"
    CRUNCHBASE = "Crunchbase"
    YOUTUBE = "YouTube"
    FACEBOOK = "Facebook"
    INSTAGRAM = "Instagram"
    TRUSTPILOT = "Trustpilot"
    GOOGLE_BUSINESS = "Google Business"
    ORCID = "ORCID"
    MEDIUM = "Medium"
    SUBSTACK = "Substack"
    CLUTCH = "Clutch"
    G2 = "G2"
    PRODUCTHUNT = "ProductHunt"
    OTHER = "Other"


@dataclass
class SameAsLink:
    url: str
    platform: str
    entity_name: str
    is_valid_url: bool
    is_high_authority: bool
    found_on_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EntityNode:
    entity_id: str
    entity_type: str
    canonical_name: str
    alternate_names: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_first_party: bool = True
    source_pages: List[str] = field(default_factory=list)
    confidence_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EntityEdge:
    source_id: str
    target_id: str
    relationship_type: str
    evidence_url: str
    is_inferred: bool = False
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EntityConflict:
    conflict_id: str
    conflict_type: str
    severity: str  # "HIGH", "MEDIUM", "LOW"
    entity_id: str
    entity_name: str
    description: str
    conflicting_evidence: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EntityScore:
    headline: float
    identity_completeness: float
    entity_consistency: float
    authority_footprint: float
    topical_expert_depth: float
    contributing_factors: Dict[str, float] = field(default_factory=dict)
    deductions: List[str] = field(default_factory=list)
    confidence: str = "low"  # "high", "medium", "low"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EntityAnalysisResult:
    target_url: str
    brand_name: str
    created_at: str
    primary_organization: Optional[Dict[str, Any]]
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    same_as_links: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    missing_entity_pages: List[str] = field(default_factory=list)
    score: Dict[str, Any] = field(default_factory=dict)
    topical_clusters: Dict[str, int] = field(default_factory=dict)
    graph_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EntityDiffResult:
    before_snapshot_id: str
    after_snapshot_id: str
    target_url: str
    created_at: str
    score_before: float
    score_after: float
    score_delta: float
    confidence_before: str
    confidence_after: str
    added_entities: List[Dict[str, Any]] = field(default_factory=list)
    removed_entities: List[Dict[str, Any]] = field(default_factory=list)
    modified_entities: List[Dict[str, Any]] = field(default_factory=list)
    resolved_conflicts: List[Dict[str, Any]] = field(default_factory=list)
    new_conflicts: List[Dict[str, Any]] = field(default_factory=list)
    added_same_as: List[Dict[str, Any]] = field(default_factory=list)
    lost_same_as: List[Dict[str, Any]] = field(default_factory=list)
    transition_summary: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
