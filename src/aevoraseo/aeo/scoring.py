"""
AevoraSEO AEO / GEO Transparent Scoring Engine
Calculates reproducible, evidence-backed scores with full signal attribution and deduction tracking.
Explicitly separated into:
- AevoraSEO AEO Readiness Score (0-100)
- AevoraSEO GEO Signal Score (0-100)
"""

from typing import Any, Dict, List, Optional, Tuple

from aevoraseo.aeo.models import (
    CitationSignal,
    ContentStructureSignal,
    CrawlerAccessSignal,
    EntitySignal,
    QuestionAnswerSignal,
    SchemaQualitySignal,
    ScoreDeduction,
    ScoreDimension,
    ScoreSignalContribution,
)


def calculate_aeo_readiness(
    questions: List[QuestionAnswerSignal],
    content_structure: ContentStructureSignal,
    schemas: List[SchemaQualitySignal],
    crawler_access: List[CrawlerAccessSignal],
) -> Tuple[float, Dict[str, ScoreDimension]]:
    """
    Computes the AevoraSEO AEO Readiness Score (0-100) across 5 deterministic dimensions.
    """
    dimensions: Dict[str, ScoreDimension] = {}

    # 1. Answer Readiness (30 pts max)
    ar_signals: List[ScoreSignalContribution] = []
    ar_deductions: List[ScoreDeduction] = []
    ar_score = 0.0

    answered_questions = [q for q in questions if q.answer_detected]
    if answered_questions:
        count = len(answered_questions)
        pts = min(15.0, count * 5.0)
        ar_score += pts
        ar_signals.append(
            ScoreSignalContribution(
                name="direct_answers_detected",
                value=count,
                impact=pts,
                description=f"Detected {count} direct answers located adjacent to questions.",
            )
        )

        high_conf = [q for q in answered_questions if q.confidence >= 0.85]
        if high_conf:
            ar_score += 10.0
            ar_signals.append(
                ScoreSignalContribution(
                    name="high_confidence_definitions",
                    value=len(high_conf),
                    impact=10.0,
                    description=f"{len(high_conf)} questions have concise, high-confidence definition answers.",
                )
            )

        faq_answers = [q for q in answered_questions if "faq" in q.answer_location.lower()]
        if faq_answers:
            ar_score += 5.0
            ar_signals.append(
                ScoreSignalContribution(
                    name="faq_structured_answers",
                    value=len(faq_answers),
                    impact=5.0,
                    description=f"{len(faq_answers)} structured FAQ answers identified.",
                )
            )

    unanswered = [q for q in questions if not q.answer_detected]
    if unanswered:
        pen = min(10.0, len(unanswered) * 3.0)
        ar_score = max(0.0, ar_score - pen)
        ar_deductions.append(
            ScoreDeduction(
                name="unanswered_questions",
                penalty=pen,
                reason=f"{len(unanswered)} question headings lack an immediate following answer block.",
            )
        )

    ar_score = min(30.0, max(0.0, round(ar_score, 1)))
    dimensions["answer_readiness"] = ScoreDimension(
        metric="answer_readiness",
        score=ar_score,
        max_score=30.0,
        signals=ar_signals,
        deductions=ar_deductions,
        explanation="Measures presence, proximity, and conciseness of direct answers to detected questions.",
    )

    # 2. Question Coverage (25 pts max)
    qc_signals: List[ScoreSignalContribution] = []
    qc_deductions: List[ScoreDeduction] = []
    qc_score = 0.0

    if questions:
        q_count = len(questions)
        q_pts = min(15.0, q_count * 3.0)
        qc_score += q_pts
        qc_signals.append(
            ScoreSignalContribution(
                name="question_count",
                value=q_count,
                impact=q_pts,
                description=f"Identified {q_count} question-phrased headings or FAQ entries.",
            )
        )

        types_found = {q.interrogative_type for q in questions if q.interrogative_type}
        if len(types_found) >= 2:
            qc_score += 10.0
            qc_signals.append(
                ScoreSignalContribution(
                    name="interrogative_diversity",
                    value=list(types_found),
                    impact=10.0,
                    description=f"Diverse interrogative coverage: {', '.join(sorted(types_found))}.",
                )
            )
    else:
        qc_deductions.append(
            ScoreDeduction(
                name="no_questions_detected",
                penalty=15.0,
                reason="Page contains no detectable question headings or FAQ structures.",
            )
        )

    qc_score = min(25.0, max(0.0, round(qc_score, 1)))
    dimensions["question_coverage"] = ScoreDimension(
        metric="question_coverage",
        score=qc_score,
        max_score=25.0,
        signals=qc_signals,
        deductions=qc_deductions,
        explanation="Measures breadth and variety of user intent and question patterns covered.",
    )

    # 3. Content Structure (20 pts max)
    cs_signals: List[ScoreSignalContribution] = []
    cs_deductions: List[ScoreDeduction] = []
    cs_score = 20.0

    if content_structure.h1_count == 1:
        cs_signals.append(
            ScoreSignalContribution(
                name="valid_single_h1",
                value=1,
                impact=5.0,
                description="Clear primary <h1> heading established.",
            )
        )
    elif content_structure.h1_count == 0:
        cs_score -= 7.0
        cs_deductions.append(
            ScoreDeduction(
                name="missing_h1",
                penalty=7.0,
                reason="Missing primary <h1> heading.",
            )
        )
    else:
        cs_score -= 3.0
        cs_deductions.append(
            ScoreDeduction(
                name="multiple_h1",
                penalty=3.0,
                reason=f"Found {content_structure.h1_count} <h1> headings.",
            )
        )

    if not content_structure.heading_hierarchy_valid:
        cs_score -= 4.0
        cs_deductions.append(
            ScoreDeduction(
                name="skipped_heading_level",
                penalty=4.0,
                reason="Heading hierarchy contains skipped levels.",
            )
        )

    if content_structure.unbroken_text_blocks > 0:
        pen = min(6.0, content_structure.unbroken_text_blocks * 3.0)
        cs_score -= pen
        cs_deductions.append(
            ScoreDeduction(
                name="unbroken_text_blocks",
                penalty=pen,
                reason=f"{content_structure.unbroken_text_blocks} long text blocks exceed 300 words without breaks.",
            )
        )

    if content_structure.list_count > 0 or content_structure.table_count > 0:
        cs_signals.append(
            ScoreSignalContribution(
                name="structured_lists_and_tables",
                value=f"{content_structure.list_count} lists, {content_structure.table_count} tables",
                impact=5.0,
                description="Structured lists or data tables support machine parsing.",
            )
        )

    cs_score = min(20.0, max(0.0, round(cs_score, 1)))
    dimensions["content_structure"] = ScoreDimension(
        metric="content_structure",
        score=cs_score,
        max_score=20.0,
        signals=cs_signals,
        deductions=cs_deductions,
        explanation="Evaluates semantic heading hierarchy, readability, and scannability.",
    )

    # 4. Schema Quality (15 pts max)
    sq_signals: List[ScoreSignalContribution] = []
    sq_deductions: List[ScoreDeduction] = []
    sq_score = 0.0

    valid_schemas = [s for s in schemas if s.valid]
    if valid_schemas:
        sq_score += 6.0
        sq_signals.append(
            ScoreSignalContribution(
                name="schema_valid",
                value=len(valid_schemas),
                impact=6.0,
                description=f"Syntactically valid Schema.org entities detected ({len(valid_schemas)}).",
            )
        )

        complete_schemas = [s for s in valid_schemas if s.complete]
        if complete_schemas:
            sq_score += 5.0
            sq_signals.append(
                ScoreSignalContribution(
                    name="schema_complete",
                    value=len(complete_schemas),
                    impact=5.0,
                    description=f"{len(complete_schemas)} schema entities contain all required properties.",
                )
            )

        consistent_schemas = [s for s in valid_schemas if s.consistent]
        if consistent_schemas:
            sq_score += 4.0
            sq_signals.append(
                ScoreSignalContribution(
                    name="schema_consistent",
                    value=len(consistent_schemas),
                    impact=4.0,
                    description="Schema entities match page title and canonical identity.",
                )
            )

    syntax_errors = [s for s in schemas if not s.valid]
    if syntax_errors:
        pen = min(8.0, len(syntax_errors) * 4.0)
        sq_score = max(0.0, sq_score - pen)
        sq_deductions.append(
            ScoreDeduction(
                name="malformed_schema_blocks",
                penalty=pen,
                reason=f"{len(syntax_errors)} schema script blocks contain JSON syntax errors.",
            )
        )

    sq_score = min(15.0, max(0.0, round(sq_score, 1)))
    dimensions["schema_quality"] = ScoreDimension(
        metric="schema_quality",
        score=sq_score,
        max_score=15.0,
        signals=sq_signals,
        deductions=sq_deductions,
        explanation="Audits structured data validity, completeness of required properties, and consistency.",
    )

    # 5. Crawler Accessibility (10 pts max)
    ca_signals: List[ScoreSignalContribution] = []
    ca_deductions: List[ScoreDeduction] = []
    ca_score = 10.0

    blocked_bots = [b for b in crawler_access if b.status == "crawl_restricted"]
    if blocked_bots:
        pen = min(10.0, len(blocked_bots) * 2.5)
        ca_score -= pen
        ca_deductions.append(
            ScoreDeduction(
                name="ai_bots_restricted",
                penalty=pen,
                reason=f"{len(blocked_bots)} AI bot(s) restricted: {', '.join(b.bot_name for b in blocked_bots)}.",
            )
        )
    else:
        ca_signals.append(
            ScoreSignalContribution(
                name="all_registered_bots_allowed",
                value=len(crawler_access),
                impact=10.0,
                description="No crawl or indexing restrictions observed for registered AI crawlers.",
            )
        )

    ca_score = min(10.0, max(0.0, round(ca_score, 1)))
    dimensions["crawler_accessibility"] = ScoreDimension(
        metric="crawler_accessibility",
        score=ca_score,
        max_score=10.0,
        signals=ca_signals,
        deductions=ca_deductions,
        explanation="Assesses accessibility permissions for major AI crawlers and answer engines.",
    )

    total_aeo = round(sum(d.score for d in dimensions.values()), 1)
    return total_aeo, dimensions


def calculate_geo_signals(
    entities: List[EntitySignal],
    citations: CitationSignal,
    schemas: List[SchemaQualitySignal],
    word_count: int,
    has_tables_or_lists: bool = False,
) -> Tuple[float, Dict[str, ScoreDimension]]:
    """
    Computes the AevoraSEO GEO Signal Score (0-100) across 5 deterministic dimensions.
    """
    dimensions: Dict[str, ScoreDimension] = {}

    # 1. Entity Clarity (25 pts max)
    ec_signals: List[ScoreSignalContribution] = []
    ec_deductions: List[ScoreDeduction] = []
    ec_score = 0.0

    named_entities = [e for e in entities if e.name]
    if named_entities:
        ec_score += 10.0
        ec_signals.append(
            ScoreSignalContribution(
                name="named_entities_detected",
                value=len(named_entities),
                impact=10.0,
                description=f"Explicitly declared entity records: {', '.join(e.entity_type for e in named_entities[:4])}.",
            )
        )

        has_org = any(e.entity_type in ("Organization", "Corporation", "LocalBusiness") for e in named_entities)
        if has_org:
            ec_score += 5.0
            ec_signals.append(
                ScoreSignalContribution(
                    name="organization_identity_present",
                    value=True,
                    impact=5.0,
                    description="Clear organizational publisher entity established.",
                )
            )

        with_sameas = [e for e in named_entities if e.same_as]
        if with_sameas:
            ec_score += 5.0
            ec_signals.append(
                ScoreSignalContribution(
                    name="sameas_authority_links",
                    value=len(with_sameas),
                    impact=5.0,
                    description=f"{len(with_sameas)} entity record(s) link to authoritative external sameAs URIs.",
                )
            )

        with_relationships = [e for e in named_entities if e.relationships]
        if with_relationships:
            ec_score += 5.0
            ec_signals.append(
                ScoreSignalContribution(
                    name="entity_graph_relationships",
                    value=len(with_relationships),
                    impact=5.0,
                    description="Established relational connections (author, publisher, brand, etc.).",
                )
            )

    inconsistent_entities = [e for e in entities if not e.is_consistent]
    if inconsistent_entities:
        pen = min(8.0, len(inconsistent_entities) * 4.0)
        ec_score = max(0.0, ec_score - pen)
        ec_deductions.append(
            ScoreDeduction(
                name="entity_inconsistencies",
                penalty=pen,
                reason=f"{len(inconsistent_entities)} entity declaration(s) have naming or identity conflicts.",
            )
        )

    ec_score = min(25.0, max(0.0, round(ec_score, 1)))
    dimensions["entity_clarity"] = ScoreDimension(
        metric="entity_clarity",
        score=ec_score,
        max_score=25.0,
        signals=ec_signals,
        deductions=ec_deductions,
        explanation="Measures clarity, consistency, and disambiguation of primary entities and sameAs linkages.",
    )

    # 2. Source & Citation Readiness (25 pts max)
    sc_signals: List[ScoreSignalContribution] = []
    sc_deductions: List[ScoreDeduction] = []
    sc_score = 0.0

    if citations.author:
        sc_score += 8.0
        sc_signals.append(
            ScoreSignalContribution(
                name="explicit_author_attribution",
                value=citations.author,
                impact=8.0,
                description=f"Author transparency established: {citations.author}.",
            )
        )
    else:
        sc_deductions.append(
            ScoreDeduction(
                name="missing_author",
                penalty=4.0,
                reason="No author byline or schema author entity detected.",
            )
        )

    if citations.date_published or citations.date_modified:
        pts = 8.0 if citations.date_published and citations.date_modified else 5.0
        sc_score += pts
        sc_signals.append(
            ScoreSignalContribution(
                name="content_timestamps",
                value=f"pub: {citations.date_published}, mod: {citations.date_modified}",
                impact=pts,
                description="Publication or modification date markers present for freshness verification.",
            )
        )
    else:
        sc_deductions.append(
            ScoreDeduction(
                name="missing_timestamps",
                penalty=4.0,
                reason="Content lacks publication or last-modified timestamps.",
            )
        )

    if citations.outbound_references_count > 0:
        pts = min(5.0, citations.outbound_references_count * 1.5)
        sc_score += pts
        sc_signals.append(
            ScoreSignalContribution(
                name="outbound_citations",
                value=citations.outbound_references_count,
                impact=pts,
                description=f"{citations.outbound_references_count} outbound citations across {len(citations.outbound_citation_domains)} domains.",
            )
        )

    if citations.has_canonical and citations.canonical_matches_url:
        sc_score += 4.0
        sc_signals.append(
            ScoreSignalContribution(
                name="canonical_alignment",
                value=True,
                impact=4.0,
                description="Self-referencing canonical URL confirms source identity.",
            )
        )

    sc_score = min(25.0, max(0.0, round(sc_score, 1)))
    dimensions["source_readiness"] = ScoreDimension(
        metric="source_readiness",
        score=sc_score,
        max_score=25.0,
        signals=sc_signals,
        deductions=sc_deductions,
        explanation="Audits observable characteristics that establish the content as an authoritative primary source.",
    )

    # 3. Factual Specificity (20 pts max)
    fs_signals: List[ScoreSignalContribution] = []
    fs_score = round(citations.factual_density_score * 20.0, 1)
    fs_signals.append(
        ScoreSignalContribution(
            name="factual_density_score",
            value=citations.factual_density_score,
            impact=fs_score,
            description=f"Factual density score of {citations.factual_density_score:.2f} based on verified quantities, dates, and metrics.",
        )
    )

    dimensions["factual_specificity"] = ScoreDimension(
        metric="factual_specificity",
        score=fs_score,
        max_score=20.0,
        signals=fs_signals,
        deductions=[],
        explanation="Measures density of empirical data points, statistics, metrics, and numerical claims.",
    )

    # 4. Topical Completeness (15 pts max)
    tc_signals: List[ScoreSignalContribution] = []
    tc_score = 0.0

    if word_count >= 1200:
        tc_score += 10.0
        tc_signals.append(
            ScoreSignalContribution(
                name="comprehensive_depth",
                value=word_count,
                impact=10.0,
                description=f"Extensive textual coverage ({word_count} words).",
            )
        )
    elif word_count >= 600:
        tc_score += 7.0
        tc_signals.append(
            ScoreSignalContribution(
                name="moderate_depth",
                value=word_count,
                impact=7.0,
                description=f"Substantive textual depth ({word_count} words).",
            )
        )
    elif word_count >= 250:
        tc_score += 4.0
        tc_signals.append(
            ScoreSignalContribution(
                name="concise_depth",
                value=word_count,
                impact=4.0,
                description=f"Concise topical overview ({word_count} words).",
            )
        )

    if has_tables_or_lists:
        tc_score += 5.0
        tc_signals.append(
            ScoreSignalContribution(
                name="rich_content_formats",
                value=True,
                impact=5.0,
                description="Complementary structured formats (tables, lists) enrich topical depth.",
            )
        )

    tc_score = min(15.0, max(0.0, round(tc_score, 1)))
    dimensions["topical_completeness"] = ScoreDimension(
        metric="topical_completeness",
        score=tc_score,
        max_score=15.0,
        signals=tc_signals,
        deductions=[],
        explanation="Evaluates topical substance, depth of coverage, and multi-format presentation.",
    )

    # 5. Structured Data Richness (15 pts max)
    sdr_signals: List[ScoreSignalContribution] = []
    sdr_score = 0.0

    unique_types = {s.schema_type for s in schemas if s.valid}
    if len(unique_types) >= 3:
        sdr_score += 15.0
        sdr_signals.append(
            ScoreSignalContribution(
                name="rich_schema_graph",
                value=list(unique_types),
                impact=15.0,
                description=f"Rich structured schema graph across {len(unique_types)} distinct types.",
            )
        )
    elif len(unique_types) >= 1:
        sdr_score += 10.0
        sdr_signals.append(
            ScoreSignalContribution(
                name="baseline_schema_graph",
                value=list(unique_types),
                impact=10.0,
                description=f"Found {len(unique_types)} schema entity type(s).",
            )
        )

    sdr_score = min(15.0, max(0.0, round(sdr_score, 1)))
    dimensions["structured_data_richness"] = ScoreDimension(
        metric="structured_data_richness",
        score=sdr_score,
        max_score=15.0,
        signals=sdr_signals,
        deductions=[],
        explanation="Evaluates breadth and relational depth of machine-readable schema types.",
    )

    total_geo = round(sum(d.score for d in dimensions.values()), 1)
    return total_geo, dimensions
