"""
AevoraSEO AI Crawler Accessibility Analyzer
Maintains an extensible bot-policy registry and inspects robots.txt, robots meta,
and X-Robots-Tag directives to determine accessibility status per AI crawler.
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

from aevoraseo.network import RobotsRules
from aevoraseo.aeo.models import CrawlerAccessSignal

# Extensible registry of AI and Generative search crawlers
AI_BOT_REGISTRY: List[Dict[str, str]] = [
    {
        "name": "GPTBot",
        "user_agent": "GPTBot",
        "operator": "OpenAI",
        "purpose": "AI model training and answer synthesis",
    },
    {
        "name": "ChatGPT-User",
        "user_agent": "ChatGPT-User",
        "operator": "OpenAI",
        "purpose": "Real-time user search browsing actions",
    },
    {
        "name": "ClaudeBot",
        "user_agent": "ClaudeBot",
        "operator": "Anthropic",
        "purpose": "Claude AI model training and retrieval",
    },
    {
        "name": "PerplexityBot",
        "user_agent": "PerplexityBot",
        "operator": "Perplexity AI",
        "purpose": "Real-time conversational search indexer",
    },
    {
        "name": "Google-Extended",
        "user_agent": "Google-Extended",
        "operator": "Google",
        "purpose": "Gemini & Vertex AI model training",
    },
    {
        "name": "Bytespider",
        "user_agent": "Bytespider",
        "operator": "ByteDance",
        "purpose": "ByteDance AI training and search crawler",
    },
    {
        "name": "CCBot",
        "user_agent": "CCBot",
        "operator": "Common Crawl",
        "purpose": "Open web crawl dataset for AI research",
    },
    {
        "name": "Applebot-Extended",
        "user_agent": "Applebot-Extended",
        "operator": "Apple",
        "purpose": "Apple Intelligence generative AI data ingestion",
    },
    {
        "name": "Cohere-AI",
        "user_agent": "cohere-ai",
        "operator": "Cohere",
        "purpose": "Enterprise LLM training and RAG data",
    },
    {
        "name": "Meta-ExternalAgent",
        "user_agent": "Meta-ExternalAgent",
        "operator": "Meta",
        "purpose": "Meta AI search and training crawler",
    },
]


def evaluate_bot_accessibility(
    page_url: str,
    robots_text: Optional[str] = None,
    meta_directives: Optional[Dict[str, List[str]]] = None,
    headers: Optional[Dict[str, Any]] = None,
    robots_blocked: bool = False,
) -> List[CrawlerAccessSignal]:
    """
    Evaluates accessibility status for all registered AI bots against robots.txt,
    HTML meta robots directives, and HTTP X-Robots-Tag headers.
    """
    signals: List[CrawlerAccessSignal] = []
    meta = meta_directives or {}
    hdrs = headers or {}

    # Extract page-level meta directives
    robots_meta = [str(x).lower() for x in meta.get("robots", [])]
    x_robots_tag = str(hdrs.get("x-robots-tag") or hdrs.get("X-Robots-Tag") or "").lower()

    # Pre-parse robots rules per bot
    rules_cache: Dict[str, RobotsRules] = {}
    if robots_text is not None:
        for bot in AI_BOT_REGISTRY:
            ua = bot["user_agent"]
            rules_cache[ua] = RobotsRules(text=robots_text, blocked=robots_blocked, agent=ua)

    for bot in AI_BOT_REGISTRY:
        bot_name = bot["name"]
        ua = bot["user_agent"]

        # 1. Check robots.txt
        if robots_text is not None:
            rules = rules_cache.get(ua)
            if rules and not rules.allowed(page_url):
                signals.append(
                    CrawlerAccessSignal(
                        bot_name=bot_name,
                        user_agent=ua,
                        observed_rule="disallow",
                        policy_source="robots.txt",
                        status="crawl_restricted",
                    )
                )
                continue

        # 2. Check bot-specific meta (e.g. meta name="google-extended" or meta name="gptbot")
        bot_meta = [str(x).lower() for x in meta.get(ua.lower(), [])]
        if any("noindex" in d or "none" in d for d in bot_meta):
            signals.append(
                CrawlerAccessSignal(
                    bot_name=bot_name,
                    user_agent=ua,
                    observed_rule="noindex",
                    policy_source=f"meta:{ua}",
                    status="crawl_restricted",
                )
            )
            continue

        # 3. Check general meta robots (noindex, nofollow, noai, noimageai)
        if any("noindex" in d or "none" in d or "noai" in d for d in robots_meta):
            signals.append(
                CrawlerAccessSignal(
                    bot_name=bot_name,
                    user_agent=ua,
                    observed_rule="noindex/noai",
                    policy_source="meta:robots",
                    status="crawl_restricted",
                )
            )
            continue

        # 4. Check X-Robots-Tag
        if "noindex" in x_robots_tag or "noai" in x_robots_tag or "none" in x_robots_tag:
            signals.append(
                CrawlerAccessSignal(
                    bot_name=bot_name,
                    user_agent=ua,
                    observed_rule="noindex/noai",
                    policy_source="x-robots-tag",
                    status="crawl_restricted",
                )
            )
            continue

        # 5. Default allowed if robots.txt is present and no restrictions found
        if robots_text is not None:
            signals.append(
                CrawlerAccessSignal(
                    bot_name=bot_name,
                    user_agent=ua,
                    observed_rule="allow",
                    policy_source="robots.txt:implicit_or_explicit",
                    status="crawl_allowed",
                )
            )
        else:
            signals.append(
                CrawlerAccessSignal(
                    bot_name=bot_name,
                    user_agent=ua,
                    observed_rule="none_observed",
                    policy_source="unspecified",
                    status="crawl_unknown",
                )
            )

    return signals
