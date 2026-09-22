"""
AevoraSEO AEO / GEO Data Models
Defines structured evidence models, signal representations, transparent score breakdowns,
and strict separation between observed visibility and analytical readiness.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class QuestionAnswerSignal:
    question: str
    detected: bool
    answer_detected: bool
    answer_text: str
    answer_location: str
    interrogative_type: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EntitySignal:
    entity_type: str
    name: str
    source: str
    same_as: List[str] = field(default_factory=list)
    relationships: Dict[str, Any] = field(default_factory=dict)
    is_consistent: bool = True
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SchemaQualitySignal:
    schema_type: str
    detected: bool
    valid: bool
    complete: bool
    consistent: bool
    present_properties: List[str] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CitationSignal:
    author: Optional[str] = None
    publisher: Optional[str] = None
    date_published: Optional[str] = None
    date_modified: Optional[str] = None
    outbound_references_count: int = 0
    outbound_citation_domains: List[str] = field(default_factory=list)
    factual_density_score: float = 0.0
    has_canonical: bool = False
    canonical_matches_url: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrawlerAccessSignal:
    bot_name: str
    user_agent: str
    observed_rule: str
    policy_source: str
    status: str  # "crawl_allowed", "crawl_restricted", "crawl_unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentStructureSignal:
    has_h1: bool
    h1_count: int
    heading_hierarchy_valid: bool
    structural_weaknesses: List[str] = field(default_factory=list)
    paragraph_count: int = 0
    unbroken_text_blocks: int = 0
    list_count: int = 0
    table_count: int = 0
    word_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScoreSignalContribution:
    name: str
    value: Any
    impact: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScoreDeduction:
    name: str
    penalty: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScoreDimension:
    metric: str
    score: float
    max_score: float
    signals: List[ScoreSignalContribution] = field(default_factory=list)
    deductions: List[ScoreDeduction] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageAEOResult:
    url: str
    aeo_readiness_score: float
    geo_signal_score: float
    aeo_dimensions: Dict[str, ScoreDimension] = field(default_factory=dict)
    geo_dimensions: Dict[str, ScoreDimension] = field(default_factory=dict)
    questions: List[QuestionAnswerSignal] = field(default_factory=list)
    entities: List[EntitySignal] = field(default_factory=list)
    schemas: List[SchemaQualitySignal] = field(default_factory=list)
    citations: CitationSignal = field(default_factory=CitationSignal)
    crawler_accessibility: List[CrawlerAccessSignal] = field(default_factory=list)
    content_structure: ContentStructureSignal = field(default_factory=lambda: ContentStructureSignal(
        has_h1=False, h1_count=0, heading_hierarchy_valid=True
    ))
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "url": self.url,
            "aeo_readiness_score": self.aeo_readiness_score,
            "geo_signal_score": self.geo_signal_score,
            "aeo_dimensions": {k: v.to_dict() for k, v in self.aeo_dimensions.items()},
            "geo_dimensions": {k: v.to_dict() for k, v in self.geo_dimensions.items()},
            "questions": [q.to_dict() for q in self.questions],
            "entities": [e.to_dict() for e in self.entities],
            "schemas": [s.to_dict() for s in self.schemas],
            "citations": self.citations.to_dict(),
            "crawler_accessibility": [c.to_dict() for c in self.crawler_accessibility],
            "content_structure": self.content_structure.to_dict(),
            "recommendations": self.recommendations,
        }
        return d


@dataclass
class ObservedVisibilityRecord:
    """
    Empirical external observation record.
    Strictly isolated from analytical readiness scores.
    """
    query: str
    engine: str  # "google_ai_overview", "perplexity", "chatgpt", "gemini", "claude", "user_supplied"
    observed: bool
    url: str
    position: Optional[int] = None
    citation: bool = False
    source: str = "manual"  # "manual", "imported", "api", "fixture"
    observed_at: str = ""
    evidence_snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SnapshotAEOResult:
    snapshot_id: str
    snapshot_dir: str
    timestamp: str
    seed_url: str
    page_count: int
    average_aeo_readiness_score: float
    average_geo_signal_score: float
    bot_accessibility_matrix: Dict[str, Dict[str, int]]
    top_questions: List[Dict[str, Any]]
    detected_entities: List[Dict[str, Any]]
    content_conflicts: List[Dict[str, Any]]
    pages: List[PageAEOResult]
    observed_visibility: List[ObservedVisibilityRecord]
    summary_markdown: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "snapshot_dir": self.snapshot_dir,
            "timestamp": self.timestamp,
            "seed_url": self.seed_url,
            "page_count": self.page_count,
            "average_aeo_readiness_score": self.average_aeo_readiness_score,
            "average_geo_signal_score": self.average_geo_signal_score,
            "bot_accessibility_matrix": self.bot_accessibility_matrix,
            "top_questions": self.top_questions,
            "detected_entities": self.detected_entities,
            "content_conflicts": self.content_conflicts,
            "pages": [p.to_dict() for p in self.pages],
            "observed_visibility": [v.to_dict() for v in self.observed_visibility],
            "summary_markdown": self.summary_markdown,
        }


@dataclass
class AEODiffItem:
    url: str
    metric: str
    before: float
    after: float
    delta: float
    state: str  # "ADDED", "REMOVED", "IMPROVED", "REGRESSED", "UNCHANGED"
    evidence: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AEODiffResult:
    before_snapshot_id: str
    after_snapshot_id: str
    before_avg_aeo: float
    after_avg_aeo: float
    aeo_delta: float
    before_avg_geo: float
    after_avg_geo: float
    geo_delta: float
    page_transitions: Dict[str, str]
    items: List[AEODiffItem]
    summary: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "before_snapshot_id": self.before_snapshot_id,
            "after_snapshot_id": self.after_snapshot_id,
            "before_avg_aeo": self.before_avg_aeo,
            "after_avg_aeo": self.after_avg_aeo,
            "aeo_delta": self.aeo_delta,
            "before_avg_geo": self.before_avg_geo,
            "after_avg_geo": self.after_avg_geo,
            "geo_delta": self.geo_delta,
            "page_transitions": self.page_transitions,
            "items": [item.to_dict() for item in self.items],
            "summary": self.summary,
        }
