"""
Search intent discovery, query extraction, and keyword cannibalization detection.
"""

import re
from typing import Any, Dict, List, Set, Tuple
from urllib.parse import urlsplit

from .models import CannibalizationCandidate, PageIntentAnalysis, SearchIntent

STOP_WORDS: Set[str] = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is", "are",
    "with", "by", "from", "our", "your", "we", "you", "it", "its", "this", "that",
    "these", "those", "as", "be", "was", "were", "been", "have", "has", "had", "do",
    "does", "did", "but", "if", "not", "so", "than", "too", "very", "can", "will",
    "just", "about", "all", "also", "into", "more", "other", "some", "such", "no",
}

TRANSACTIONAL_KEYWORDS: Set[str] = {
    "buy", "purchase", "order", "book", "booking", "schedule", "reserve", "hire",
    "pricing", "price", "prices", "cost", "plans", "quote", "consultation", "signup",
    "register", "enroll", "enrollment", "demo", "free trial", "get started", "checkout",
    "cart", "package", "service", "appointment",
}

COMMERCIAL_INVESTIGATION_KEYWORDS: Set[str] = {
    "vs", "versus", "alternative", "alternatives", "compare", "comparison", "review",
    "reviews", "best", "top", "rating", "rated", "features", "pros and cons", "competitor",
    "difference between", "better than", "worth it", "which is better",
}

INFORMATIONAL_KEYWORDS: Set[str] = {
    "how to", "what is", "why", "when", "where", "who", "guide", "tutorial", "tips",
    "overview", "explained", "definition", "learn", "examples", "step by step", "benefits",
    "causes", "symptoms", "history", "methods", "strategies", "checklist",
}

LOCAL_INDICATORS: Set[str] = {
    "near me", "in", "city", "county", "district", "local", "area", "neighborhood",
    "downtown", "clinic", "office", "store", "center", "centre", "directions",
    "opening hours", "visit us", "located in", "serving",
}

NAVIGATIONAL_SLUGS: Set[str] = {
    "", "home", "about", "about-us", "team", "our-team", "company", "contact",
    "contact-us", "get-in-touch", "login", "signin", "portal", "careers", "jobs",
    "privacy", "privacy-policy", "terms", "terms-of-service", "terms-and-conditions",
    "press", "newsroom", "faq", "faqs", "help", "support", "sitemap",
}


def clean_tokens(text: str) -> List[str]:
    """Tokenize text, remove non-alphanumeric characters, and filter common stop words."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", " ", text.lower())
    tokens = [t.strip("-") for t in cleaned.split() if t.strip("-")]
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def extract_target_queries(
    title: str,
    h1: str,
    slug: str,
    description: str = "",
) -> Tuple[str, List[str]]:
    """
    Extract the primary target query and secondary candidate queries for a page.
    Prioritizes strong token overlap between H1, Title, and URL slug.
    """
    h1_tokens = clean_tokens(h1)
    title_tokens = clean_tokens(title)
    slug_tokens = clean_tokens(slug.replace("-", " ").replace("_", " "))

    # Primary query candidate: tokens present in both H1 and Title or H1/slug
    overlap = [t for t in h1_tokens if t in title_tokens]
    if not overlap and h1_tokens:
        overlap = h1_tokens[:4]
    elif not overlap and title_tokens:
        overlap = title_tokens[:4]
    elif not overlap and slug_tokens:
        overlap = slug_tokens[:4]

    if overlap:
        primary_query = " ".join(overlap[:4])
    else:
        primary_query = " ".join(title_tokens[:3]) if title_tokens else "general"

    # Secondary queries from title, description, and slug
    secondaries: List[str] = []
    if slug_tokens and " ".join(slug_tokens[:3]) != primary_query:
        secondaries.append(" ".join(slug_tokens[:3]))
    if title_tokens and " ".join(title_tokens[:3]) != primary_query:
        secondaries.append(" ".join(title_tokens[:3]))
    if description:
        desc_tokens = clean_tokens(description)
        if desc_tokens:
            phrase = " ".join(desc_tokens[:3])
            if phrase != primary_query and phrase not in secondaries:
                secondaries.append(phrase)

    return primary_query, secondaries[:3]


def classify_search_intent(
    url: str,
    title: str,
    h1: str,
    body_text: str,
    schema_types: List[str],
    cta_texts: List[str],
    meta_description: str = "",
) -> PageIntentAnalysis:
    """
    Classifies search intent using deterministic multi-signal scoring.
    Evaluates: Informational, Commercial Investigation, Transactional, Navigational, Local.
    """
    parsed = urlsplit(url)
    path = parsed.path.lower().strip("/")
    slug_parts = path.split("/")
    slug_last = slug_parts[-1] if slug_parts else ""

    combined_text = f"{title} {h1} {meta_description} {body_text[:1500]}".lower()
    cta_blob = " ".join(cta_texts).lower()
    schema_set = {s.lower() for s in schema_types}

    scores: Dict[str, float] = {
        SearchIntent.NAVIGATIONAL.value: 0.0,
        SearchIntent.TRANSACTIONAL.value: 0.0,
        SearchIntent.COMMERCIAL_INVESTIGATION.value: 0.0,
        SearchIntent.INFORMATIONAL.value: 0.0,
        SearchIntent.LOCAL.value: 0.0,
    }
    signals: Dict[str, List[str]] = {
        "navigational": [],
        "transactional": [],
        "commercial_investigation": [],
        "informational": [],
        "local": [],
    }

    # 1. Navigational signals
    if not path or slug_last in NAVIGATIONAL_SLUGS:
        scores[SearchIntent.NAVIGATIONAL.value] += 40.0
        signals["navigational"].append(f"Standard navigational slug: /{slug_last}")

    for nav_kw in ["about us", "contact us", "privacy policy", "terms of service", "client login", "our team"]:
        if nav_kw in title.lower() or nav_kw in h1.lower():
            scores[SearchIntent.NAVIGATIONAL.value] += 30.0
            signals["navigational"].append(f"Navigational title/h1 phrase: '{nav_kw}'")
            break

    # 2. Transactional signals
    for kw in TRANSACTIONAL_KEYWORDS:
        if kw in path:
            scores[SearchIntent.TRANSACTIONAL.value] += 25.0
            signals["transactional"].append(f"Transactional URL token: '{kw}'")
            break
        if re.search(rf"\b{re.escape(kw)}\b", title.lower()) or re.search(rf"\b{re.escape(kw)}\b", h1.lower()):
            scores[SearchIntent.TRANSACTIONAL.value] += 20.0
            signals["transactional"].append(f"Transactional keyword in title/h1: '{kw}'")

    for cta_kw in ["book", "order", "buy", "schedule", "reserve", "get quote", "start free trial", "sign up"]:
        if cta_kw in cta_blob:
            scores[SearchIntent.TRANSACTIONAL.value] += 15.0
            signals["transactional"].append(f"Transactional CTA button: '{cta_kw}'")
            break

    if "product" in schema_set or "offer" in schema_set:
        scores[SearchIntent.TRANSACTIONAL.value] += 25.0
        signals["transactional"].append("Product or Offer structured data")
    elif "service" in schema_set:
        scores[SearchIntent.TRANSACTIONAL.value] += 15.0
        signals["transactional"].append("Service structured data")

    # 3. Commercial Investigation signals
    for kw in COMMERCIAL_INVESTIGATION_KEYWORDS:
        if kw in path:
            scores[SearchIntent.COMMERCIAL_INVESTIGATION.value] += 25.0
            signals["commercial_investigation"].append(f"Commercial investigation URL token: '{kw}'")
            break
        if re.search(rf"\b{re.escape(kw)}\b", title.lower()) or re.search(rf"\b{re.escape(kw)}\b", h1.lower()):
            scores[SearchIntent.COMMERCIAL_INVESTIGATION.value] += 20.0
            signals["commercial_investigation"].append(f"Comparison phrase in title/h1: '{kw}'")

    if "vs" in slug_last or "-vs-" in slug_last:
        scores[SearchIntent.COMMERCIAL_INVESTIGATION.value] += 30.0
        signals["commercial_investigation"].append("Head-to-head comparison slug format")

    if "aggregaterating" in schema_set or "review" in schema_set:
        scores[SearchIntent.COMMERCIAL_INVESTIGATION.value] += 20.0
        signals["commercial_investigation"].append("Review or AggregateRating schema")

    # 4. Informational signals
    for kw in INFORMATIONAL_KEYWORDS:
        if kw in path:
            scores[SearchIntent.INFORMATIONAL.value] += 25.0
            signals["informational"].append(f"Informational URL token: '{kw}'")
            break
        if re.search(rf"\b{re.escape(kw)}\b", title.lower()) or re.search(rf"\b{re.escape(kw)}\b", h1.lower()):
            scores[SearchIntent.INFORMATIONAL.value] += 20.0
            signals["informational"].append(f"Informational query in title/h1: '{kw}'")

    if "article" in schema_set or "blogposting" in schema_set or "techarticle" in schema_set:
        scores[SearchIntent.INFORMATIONAL.value] += 25.0
        signals["informational"].append("Article or BlogPosting structured data")
    if "faqpage" in schema_set:
        scores[SearchIntent.INFORMATIONAL.value] += 15.0
        signals["informational"].append("FAQPage structured data")

    if "blog" in slug_parts or "articles" in slug_parts or "guides" in slug_parts:
        scores[SearchIntent.INFORMATIONAL.value] += 20.0
        signals["informational"].append("Blog or Guide directory in URL path")

    # 5. Local signals
    local_schema = any(
        s in schema_set
        for s in [
            "localbusiness", "dentist", "medicalbusiness", "legalservice",
            "store", "restaurant", "financialservice", "automotivebusiness"
        ]
    )
    if local_schema:
        scores[SearchIntent.LOCAL.value] += 35.0
        signals["local"].append("LocalBusiness or subtype schema present")

    for kw in ["near me", "directions", "opening hours", "visit our clinic", "visit our office"]:
        if kw in combined_text:
            scores[SearchIntent.LOCAL.value] += 20.0
            signals["local"].append(f"Local physical marker: '{kw}'")
            break

    # Extract target queries
    primary_query, secondary_queries = extract_target_queries(title, h1, slug_last, meta_description)

    # Resolve primary and secondary intents
    sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_intent, best_score = sorted_intents[0]

    if best_score < 15.0:
        primary_intent = SearchIntent.INFORMATIONAL.value
        confidence = 0.5
    else:
        primary_intent = best_intent
        second_score = sorted_intents[1][1] if len(sorted_intents) > 1 else 0.0
        confidence = min(1.0, max(0.6, (best_score - second_score + 10.0) / 40.0))

    secondaries: List[str] = []
    for intent_name, score in sorted_intents[1:]:
        if score >= 20.0 and intent_name != primary_intent:
            secondaries.append(intent_name)

    return PageIntentAnalysis(
        url=url,
        title=title,
        primary_intent=primary_intent,
        secondary_intents=secondaries[:2],
        primary_target_query=primary_query,
        secondary_queries=secondary_queries,
        intent_signals=signals,
        confidence=round(confidence, 2),
    )


def calculate_token_similarity(tokens1: List[str], tokens2: List[str]) -> float:
    """Calculate Jaccard token similarity between two token sets."""
    s1, s2 = set(tokens1), set(tokens2)
    if not s1 or not s2:
        return 0.0
    intersection = s1.intersection(s2)
    union = s1.union(s2)
    return len(intersection) / len(union)


def detect_cannibalization(page_intents: List[PageIntentAnalysis]) -> List[CannibalizationCandidate]:
    """
    Identifies internal pages competing for the same primary query and intent.
    Calculates token similarity and assigns severity risk levels.
    """
    candidates: List[CannibalizationCandidate] = []
    seen_pairs: Set[Tuple[str, str]] = set()

    for i in range(len(page_intents)):
        p1 = page_intents[i]
        tokens1 = clean_tokens(p1.primary_target_query)
        if not tokens1 or p1.primary_target_query == "general":
            continue

        for j in range(i + 1, len(page_intents)):
            p2 = page_intents[j]
            tokens2 = clean_tokens(p2.primary_target_query)
            if not tokens2 or p2.primary_target_query == "general":
                continue

            pair_key = (min(p1.url, p2.url), max(p1.url, p2.url))
            if pair_key in seen_pairs:
                continue

            similarity = calculate_token_similarity(tokens1, tokens2)
            is_exact = p1.primary_target_query == p2.primary_target_query
            same_intent = p1.primary_intent == p2.primary_intent

            if is_exact or (similarity >= 0.70 and same_intent):
                seen_pairs.add(pair_key)
                if is_exact and same_intent:
                    risk = "HIGH"
                    rec = (
                        f"Pages '{p1.url}' and '{p2.url}' target identical search query '{p1.primary_target_query}' "
                        f"with {p1.primary_intent} intent. Consolidate into single authoritative URL or differentiate topics."
                    )
                elif similarity >= 0.80 and same_intent:
                    risk = "HIGH"
                    rec = (
                        f"High query collision between '{p1.primary_target_query}' and '{p2.primary_target_query}'. "
                        "Canonicalize or differentiate target keywords and headings."
                    )
                elif same_intent:
                    risk = "MEDIUM"
                    rec = (
                        f"Moderate keyword overlap ({similarity:.0%}) for {p1.primary_intent} intent. "
                        "Strengthen unique topical modifiers or interlink hierarchically."
                    )
                else:
                    risk = "LOW"
                    rec = "Topical overlap with differing intent. Ensure distinct user journeys and clear internal linking."

                candidates.append(
                    CannibalizationCandidate(
                        query=p1.primary_target_query,
                        intent=p1.primary_intent,
                        competing_urls=[p1.url, p2.url],
                        similarity_score=round(similarity if not is_exact else 1.0, 2),
                        risk_level=risk,
                        recommendation=rec,
                    )
                )

    # Sort candidates by risk level: HIGH first, then MEDIUM, then LOW
    risk_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    candidates.sort(key=lambda c: risk_weights.get(c.risk_level, 0), reverse=True)
    return candidates
