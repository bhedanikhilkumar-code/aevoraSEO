"""
Data models for AevoraSEO Search, Local & Commercial Intelligence Subsystem.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SearchIntent(str, Enum):
    INFORMATIONAL = "Informational"
    COMMERCIAL_INVESTIGATION = "Commercial Investigation"
    TRANSACTIONAL = "Transactional"
    NAVIGATIONAL = "Navigational"
    LOCAL = "Local"
    UNKNOWN = "Unknown"


@dataclass
class PageIntentAnalysis:
    url: str
    title: str
    primary_intent: str
    secondary_intents: List[str] = field(default_factory=list)
    primary_target_query: str = ""
    secondary_queries: List[str] = field(default_factory=list)
    intent_signals: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CannibalizationCandidate:
    query: str
    intent: str
    competing_urls: List[str]
    similarity_score: float
    risk_level: str  # "HIGH", "MEDIUM", "LOW"
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LocalSignalAnalysis:
    url: str
    has_local_business_schema: bool = False
    schema_types: List[str] = field(default_factory=list)
    nap_present: bool = False
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    has_clickable_tel: bool = False
    has_map_embed_or_link: bool = False
    service_areas_declared: List[str] = field(default_factory=list)
    opening_hours_present: bool = False
    geo_coordinates_present: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CommercialJourneyAnalysis:
    url: str
    page_type: str  # "service_page", "product_page", "comparison_page", "lead_gen_page", "pricing_page", "content_page"
    cta_count: int = 0
    high_intent_ctas: List[Dict[str, str]] = field(default_factory=list)
    generic_ctas: List[Dict[str, str]] = field(default_factory=list)
    friction_issues: List[str] = field(default_factory=list)
    trust_signals: List[str] = field(default_factory=list)
    has_phone_call_action: bool = False
    has_messaging_action: bool = False
    has_booking_action: bool = False
    pricing_transparency: str = "no_pricing_info"  # "transparent_pricing", "custom_quote", "no_pricing_info"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ComparisonSupportAnalysis:
    url: str
    is_comparison_page: bool = False
    has_comparison_table: bool = False
    alternatives_evaluated: List[str] = field(default_factory=list)
    buyer_questions_answered: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SearchCommercialScore:
    headline: float
    intent_query_targeting: float
    commercial_journey_cta: float
    local_visibility_signals: float
    comparison_buyer_support: float
    contributing_factors: Dict[str, float] = field(default_factory=dict)
    deductions: List[str] = field(default_factory=list)
    confidence: str = "low"  # "high", "medium", "low"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SearchCommercialAnalysisResult:
    target_url: str
    brand_name: str
    created_at: str
    pages_analyzed: int
    page_intents: List[Dict[str, Any]] = field(default_factory=list)
    cannibalization_issues: List[Dict[str, Any]] = field(default_factory=list)
    local_signals: List[Dict[str, Any]] = field(default_factory=list)
    commercial_journeys: List[Dict[str, Any]] = field(default_factory=list)
    comparison_pages: List[Dict[str, Any]] = field(default_factory=list)
    score: Dict[str, Any] = field(default_factory=dict)
    intent_distribution: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SearchCommercialDiffResult:
    before_snapshot_id: str
    after_snapshot_id: str
    target_url: str
    created_at: str
    score_before: float
    score_after: float
    score_delta: float
    confidence_before: str
    confidence_after: str
    intent_transitions: List[Dict[str, Any]] = field(default_factory=list)
    new_cannibalizations: List[Dict[str, Any]] = field(default_factory=list)
    resolved_cannibalizations: List[Dict[str, Any]] = field(default_factory=list)
    commercial_improvements: List[Dict[str, Any]] = field(default_factory=list)
    commercial_regressions: List[Dict[str, Any]] = field(default_factory=list)
    local_signal_changes: List[Dict[str, Any]] = field(default_factory=list)
    transition_summary: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
