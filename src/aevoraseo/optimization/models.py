"""
Data models for AevoraSEO Content & Optimization Intelligence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TitleAudit:
    url: str
    title: str
    length: int
    status: str  # "optimal", "too_short", "too_long", "missing"
    brand_detected: bool
    brand_position: str  # "end", "start", "none"
    keyword_stuffed: bool
    primary_query: str
    query_overlap: bool
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetaDescriptionAudit:
    url: str
    description: str
    length: int
    status: str  # "optimal", "too_short", "too_long", "missing"
    has_cta: bool
    cta_phrases: List[str]
    primary_query: str
    query_overlap: bool
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HeadingAudit:
    url: str
    h1_count: int
    h1_texts: List[str]
    h2_count: int
    h3_count: int
    has_skipped_levels: bool
    skipped_hierarchy_issues: List[str]
    question_headings: List[str]
    empty_headings: List[str]
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DirectAnswerOpportunity:
    url: str
    question_or_topic: str
    opportunity_type: str  # "definition", "procedural_list", "comparison_table", "faq"
    target_format: str  # "40-60 word answer box", "ordered list", "table", "summary box"
    current_answer_snippet: Optional[str]
    is_answered: bool
    draft_answer_blueprint: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FAQOpportunity:
    url: str
    topic: str
    friction_type: str  # "pricing", "guarantee", "implementation", "support", "cancellation", "technical"
    suggested_question: str
    suggested_answer_points: List[str]
    schema_eligible: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InternalLinkRecommendation:
    source_url: str
    target_url: str
    recommended_anchor: str
    rationale: str
    link_type: str  # "hub_to_spoke", "spoke_to_hub", "cross_spoke", "orphan_recovery"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TopicCluster:
    cluster_id: str
    topic_name: str
    pillar_url: Optional[str]
    spoke_urls: List[str] = field(default_factory=list)
    cluster_health_score: float = 0.0
    missing_spokes: List[str] = field(default_factory=list)
    internal_link_coverage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SchemaRecommendation:
    url: str
    page_intent: str
    current_schemas: List[str]
    recommended_schemas: List[str]
    missing_schemas: List[str]
    implementation_guide: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentBrief:
    brief_id: str
    url: str
    primary_query: str
    secondary_queries: List[str]
    search_intent: str
    target_word_count: int
    required_sections: List[str]
    direct_answer_targets: List[str]
    recommended_internal_links: List[Dict[str, str]]
    recommended_schema: str
    editorial_guidance: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EditorialOutline:
    outline_id: str
    url: str
    h1_title: str
    sections: List[Dict[str, Any]]
    faq_items: List[Dict[str, str]]
    cta_placement: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentGap:
    gap_id: str
    gap_type: str  # "missing_faq", "missing_comparison", "missing_guide", "thin_service_page", "uncovered_query"
    topic: str
    intent: str
    evidence: str
    action_plan: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentRefreshCandidate:
    url: str
    title: str
    current_word_count: int
    refresh_priority: str  # "HIGH", "MEDIUM", "LOW"
    reasons: List[str]
    recommended_actions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationRoadmapItem:
    timeframe: str  # "30-day", "60-day", "90-day"
    phase_name: str
    action: str
    target_urls: List[str]
    expected_impact: str  # "HIGH", "MEDIUM", "LOW"
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationScore:
    headline: float  # 0.0 - 100.0
    metadata_heading_score: float  # 0.0 - 25.0
    content_quality_depth_score: float  # 0.0 - 25.0
    internal_link_cluster_score: float  # 0.0 - 25.0
    schema_structured_score: float  # 0.0 - 25.0
    confidence: str  # "high", "medium", "low"
    deductions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationResult:
    target_url: str
    brand_name: str
    created_at: str
    pages_analyzed: int
    score: Dict[str, Any]
    title_audits: List[Dict[str, Any]] = field(default_factory=list)
    meta_audits: List[Dict[str, Any]] = field(default_factory=list)
    heading_audits: List[Dict[str, Any]] = field(default_factory=list)
    direct_answer_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    faq_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    internal_link_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    orphan_pages: List[str] = field(default_factory=list)
    topic_clusters: List[Dict[str, Any]] = field(default_factory=list)
    schema_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    content_briefs: List[Dict[str, Any]] = field(default_factory=list)
    editorial_outlines: List[Dict[str, Any]] = field(default_factory=list)
    content_gaps: List[Dict[str, Any]] = field(default_factory=list)
    refresh_candidates: List[Dict[str, Any]] = field(default_factory=list)
    roadmap_items: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationDiff:
    before_snapshot_id: str
    after_snapshot_id: str
    target_url: str
    created_at: str
    score_before: float
    score_after: float
    score_delta: float
    confidence_before: str
    confidence_after: str
    transition_summary: Dict[str, int]
    dimension_deltas: Dict[str, float]
    resolved_issues: List[Dict[str, Any]] = field(default_factory=list)
    new_issues: List[Dict[str, Any]] = field(default_factory=list)
    new_answer_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    cluster_evolution: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
