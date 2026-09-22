"""
AevoraSEO SameAs & Authority Discovery Module
Classifies, validates, and audits external identity profiles and semantic links.
"""

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from .models import AuthorityPlatform, SameAsLink


PLATFORM_DOMAINS: Dict[str, AuthorityPlatform] = {
    "wikipedia.org": AuthorityPlatform.WIKIPEDIA,
    "wikidata.org": AuthorityPlatform.WIKIDATA,
    "linkedin.com": AuthorityPlatform.LINKEDIN,
    "github.com": AuthorityPlatform.GITHUB,
    "twitter.com": AuthorityPlatform.TWITTER,
    "x.com": AuthorityPlatform.TWITTER,
    "crunchbase.com": AuthorityPlatform.CRUNCHBASE,
    "youtube.com": AuthorityPlatform.YOUTUBE,
    "facebook.com": AuthorityPlatform.FACEBOOK,
    "instagram.com": AuthorityPlatform.INSTAGRAM,
    "trustpilot.com": AuthorityPlatform.TRUSTPILOT,
    "google.com": AuthorityPlatform.GOOGLE_BUSINESS,
    "orcid.org": AuthorityPlatform.ORCID,
    "medium.com": AuthorityPlatform.MEDIUM,
    "substack.com": AuthorityPlatform.SUBSTACK,
    "clutch.co": AuthorityPlatform.CLUTCH,
    "g2.com": AuthorityPlatform.G2,
    "producthunt.com": AuthorityPlatform.PRODUCTHUNT,
}

HIGH_AUTHORITY_PLATFORMS = {
    AuthorityPlatform.WIKIPEDIA,
    AuthorityPlatform.WIKIDATA,
    AuthorityPlatform.LINKEDIN,
    AuthorityPlatform.CRUNCHBASE,
    AuthorityPlatform.GITHUB,
    AuthorityPlatform.ORCID,
    AuthorityPlatform.TRUSTPILOT,
    AuthorityPlatform.GOOGLE_BUSINESS,
}

STANDARD_CORP_PROFILES = [
    AuthorityPlatform.LINKEDIN,
    AuthorityPlatform.TWITTER,
    AuthorityPlatform.CRUNCHBASE,
    AuthorityPlatform.GITHUB,
    AuthorityPlatform.YOUTUBE,
]


def classify_authority_platform(url: str) -> Tuple[AuthorityPlatform, bool]:
    """
    Identifies the authority platform and whether it represents a high-authority semantic signal.
    """
    try:
        parsed = urlparse(url.strip())
        host = (parsed.netloc or "").lower().removeprefix("www.")
        if not host:
            return AuthorityPlatform.OTHER, False

        for domain, platform in PLATFORM_DOMAINS.items():
            if host == domain or host.endswith("." + domain):
                is_high = platform in HIGH_AUTHORITY_PLATFORMS
                return platform, is_high

        return AuthorityPlatform.OTHER, False
    except Exception:
        return AuthorityPlatform.OTHER, False


def validate_same_as_url(url: str) -> bool:
    """
    Validates whether a sameAs target is a structurally valid HTTP/HTTPS URL with host and path.
    """
    if not isinstance(url, str):
        return False
    clean_url = url.strip()
    if not clean_url:
        return False
    try:
        parsed = urlparse(clean_url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc) and "." in parsed.netloc
    except Exception:
        return False


def build_same_as_link(url: str, entity_name: str, found_on_url: str = "") -> SameAsLink:
    """
    Builds and validates a SameAsLink object.
    """
    is_valid = validate_same_as_url(url)
    platform, is_high = classify_authority_platform(url) if is_valid else (AuthorityPlatform.OTHER, False)
    return SameAsLink(
        url=url.strip(),
        platform=platform.value,
        entity_name=entity_name,
        is_valid_url=is_valid,
        is_high_authority=is_high,
        found_on_url=found_on_url,
    )


def audit_missing_profiles(
    existing_links: List[SameAsLink],
    is_tech_or_startup: bool = True
) -> List[str]:
    """
    Identifies standard expected corporate/entity profiles that have not been declared in sameAs.
    """
    declared_platforms = {l.platform for l in existing_links if l.is_valid_url}
    missing: List[str] = []

    for expected in STANDARD_CORP_PROFILES:
        if expected.value not in declared_platforms:
            missing.append(expected.value)

    return missing
