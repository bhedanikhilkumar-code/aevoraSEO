"""Remediation Plan generator for AevoraSEO.

Synthesizes findings from crawl snapshot databases (content optimization,
search commercial, unified reports) or scans local website HTML trees directly
to generate prioritized, actionable RemediationPlans.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from .patcher import PatchType


@dataclass
class RemediationPatch:
    id: str
    patch_type: str
    relative_path: str
    url: str
    title: str
    rationale: str
    priority: str
    expected_score_impact: float
    patch_params: dict[str, Any]
    status: str = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RemediationPatch:
        return cls(**data)


@dataclass
class RemediationPlan:
    plan_id: str
    target_host: str
    site_root: str
    crawl_dir: str
    created_at: str
    patches: list[RemediationPatch] = field(default_factory=list)
    estimated_total_score_impact: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "target_host": self.target_host,
            "site_root": self.site_root,
            "crawl_dir": self.crawl_dir,
            "created_at": self.created_at,
            "patches": [p.to_dict() for p in self.patches],
            "estimated_total_score_impact": round(self.estimated_total_score_impact, 2),
            "total_patches": len(self.patches),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RemediationPlan:
        patches = [RemediationPatch.from_dict(p) for p in data.get("patches", [])]
        return cls(
            plan_id=data.get("plan_id", str(uuid.uuid4())[:8]),
            target_host=data.get("target_host", ""),
            site_root=data.get("site_root", ""),
            crawl_dir=data.get("crawl_dir", ""),
            created_at=data.get("created_at", ""),
            patches=patches,
            estimated_total_score_impact=data.get("estimated_total_score_impact", 0.0),
        )


def resolve_url_to_file(url: str, site_root: Path) -> str | None:
    """Map a website URL to a relative local file path in site_root."""
    parsed = urlsplit(url)
    path_str = parsed.path.strip("/")
    if not path_str:
        if (site_root / "index.html").exists():
            return "index.html"
        return "index.html"

    # Try exact path
    candidate = site_root / path_str
    if candidate.is_file():
        return path_str
    if (site_root / f"{path_str}.html").is_file():
        return f"{path_str}.html"
    if (site_root / path_str / "index.html").is_file():
        return f"{path_str}/index.html"

    # Default fallback
    if path_str.endswith(".html") or path_str.endswith(".htm"):
        return path_str
    return f"{path_str}.html"


def generate_remediation_plan(
    site_root: str | Path,
    crawl_dir: str | Path | None = None,
    target: str | None = None,
) -> RemediationPlan:
    """Generate a prioritized remediation plan from crawl snapshots or local inspection."""
    from ..network import utcnow

    site_path = Path(site_root).resolve()
    crawl_path = Path(crawl_dir).resolve() if crawl_dir else None
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"
    created_at = utcnow()
    patches: list[RemediationPatch] = []
    patch_idx = 1

    host = target or ""
    if not host and crawl_path and (crawl_path / "crawl.sqlite3").exists():
        try:
            with sqlite3.connect(str(crawl_path / "crawl.sqlite3")) as db:
                row = db.execute("SELECT value FROM meta WHERE key='config'").fetchone()
                if row:
                    saved = json.loads(row[0])
                    host = urlsplit(saved.get("config", {}).get("url", "")).netloc
        except Exception:
            pass

    if not host:
        host = site_path.name

    # Strategy 1: Ingest from SQLite databases in crawl_dir if available
    db_ingested = False
    if crawl_path and (crawl_path / "content_optimization.sqlite3").exists():
        try:
            with sqlite3.connect(str(crawl_path / "content_optimization.sqlite3")) as db:
                # 1. Page audits
                cursor = db.execute(
                    "SELECT url, title_status, title_recommendation, meta_status, meta_recommendation, "
                    "h1_count, primary_query, schema_types, recommended_schema "
                    "FROM optimization_page_audits"
                )
                for row in cursor.fetchall():
                    (
                        url,
                        title_status,
                        title_rec,
                        meta_status,
                        meta_rec,
                        h1_count,
                        query,
                        schema_types,
                        rec_schema,
                    ) = row
                    rel_file = resolve_url_to_file(url, site_path)
                    if not rel_file:
                        continue

                    # Title tag deficiency
                    if title_status in ("SHORT", "LONG", "MISSING") and title_rec:
                        patches.append(
                            RemediationPatch(
                                id=f"PATCH-{patch_idx:03d}",
                                patch_type=PatchType.TITLE.value,
                                relative_path=rel_file,
                                url=url,
                                title=f"Optimize Title Tag on {Path(rel_file).name}",
                                rationale=f"Title status is {title_status}; recommendation aligns query '{query or ''}' with optimal length.",
                                priority="P1" if title_status != "MISSING" else "P0",
                                expected_score_impact=3.5 if title_status != "MISSING" else 6.0,
                                patch_params={"new_title": title_rec},
                            )
                        )
                        patch_idx += 1

                    # Meta description deficiency
                    if meta_status in ("MISSING", "SHORT", "LONG") and meta_rec:
                        patches.append(
                            RemediationPatch(
                                id=f"PATCH-{patch_idx:03d}",
                                patch_type=PatchType.META_DESCRIPTION.value,
                                relative_path=rel_file,
                                url=url,
                                title=f"Inject Meta Description on {Path(rel_file).name}",
                                rationale=f"Meta description is {meta_status}; recommendation provides actionable CTA verb and query relevance.",
                                priority="P1",
                                expected_score_impact=3.0,
                                patch_params={"new_description": meta_rec},
                            )
                        )
                        patch_idx += 1

                    # Heading hierarchy deficiency
                    if h1_count != 1:
                        patches.append(
                            RemediationPatch(
                                id=f"PATCH-{patch_idx:03d}",
                                patch_type=PatchType.HEADING_HIERARCHY.value,
                                relative_path=rel_file,
                                url=url,
                                title=f"Repair Heading Hierarchy on {Path(rel_file).name}",
                                rationale=f"Page has {h1_count} H1 tags; SEO standard requires exactly 1 primary H1 matching target intent.",
                                priority="P0" if h1_count == 0 else "P2",
                                expected_score_impact=4.0 if h1_count == 0 else 2.0,
                                patch_params={
                                    "h1_text": query.title() if query else None,
                                    "demote_extra_h1": True,
                                },
                            )
                        )
                        patch_idx += 1

                    # Schema recommendation
                    if rec_schema and rec_schema not in (schema_types or ""):
                        schema_data = {
                            "@context": "https://schema.org",
                            "@type": rec_schema,
                            "name": query.title() if query else host,
                            "url": url,
                        }
                        patches.append(
                            RemediationPatch(
                                id=f"PATCH-{patch_idx:03d}",
                                patch_type=PatchType.SCHEMA_JSONLD.value,
                                relative_path=rel_file,
                                url=url,
                                title=f"Inject Schema.org {rec_schema} on {Path(rel_file).name}",
                                rationale=f"Page is missing structured data for recognized intent type {rec_schema}.",
                                priority="P1",
                                expected_score_impact=5.0,
                                patch_params={"schema_data": schema_data},
                            )
                        )
                        patch_idx += 1

                # 2. Answer opportunities
                cursor = db.execute(
                    "SELECT url, question_heading, recommended_definition, bullet_points "
                    "FROM optimization_answer_opportunities"
                )
                for row in cursor.fetchall():
                    url, question, definition, bullets_json = row
                    rel_file = resolve_url_to_file(url, site_path)
                    if not rel_file:
                        continue
                    bullets = json.loads(bullets_json) if bullets_json else []
                    patches.append(
                        RemediationPatch(
                            id=f"PATCH-{patch_idx:03d}",
                            patch_type=PatchType.DIRECT_ANSWER.value,
                            relative_path=rel_file,
                            url=url,
                            title=f"Add Direct-Answer Definition Box to {Path(rel_file).name}",
                            rationale=f"High AEO/GEO opportunity: question heading '{question[:40]}' lacks immediate 40-60 word answer definition.",
                            priority="P1",
                            expected_score_impact=4.5,
                            patch_params={
                                "heading_pattern": question,
                                "answer_text": definition,
                                "list_items": bullets,
                            },
                        )
                    )
                    patch_idx += 1

            db_ingested = True
        except Exception:
            db_ingested = False

    # Strategy 2: If no DB ingested or DB was empty, scan site_path HTML files directly
    if not db_ingested or not patches:
        html_files = sorted(
            [p for p in site_path.rglob("*.html") if not p.name.startswith(".")]
        )
        for h_path in html_files:
            rel_file = str(h_path.relative_to(site_path)).replace("\\", "/")
            url = f"https://{host}/{rel_file.removesuffix('.html').removesuffix('/index')}"
            try:
                content = h_path.read_text(encoding="utf-8", errors="replace")
                soup = BeautifulSoup(content, "html.parser")

                # Title
                title_tag = soup.find("title")
                title_text = title_tag.get_text().strip() if title_tag else ""
                if not title_text:
                    patches.append(
                        RemediationPatch(
                            id=f"PATCH-{patch_idx:03d}",
                            patch_type=PatchType.TITLE.value,
                            relative_path=rel_file,
                            url=url,
                            title=f"Add Missing Title Tag to {Path(rel_file).name}",
                            rationale="Page has no <title> tag; essential for search indexing and click-through visibility.",
                            priority="P0",
                            expected_score_impact=6.0,
                            patch_params={"new_title": f"{h_path.stem.capitalize()} | {host}"},
                        )
                    )
                    patch_idx += 1
                elif len(title_text) < 30:
                    patches.append(
                        RemediationPatch(
                            id=f"PATCH-{patch_idx:03d}",
                            patch_type=PatchType.TITLE.value,
                            relative_path=rel_file,
                            url=url,
                            title=f"Expand Short Title Tag on {Path(rel_file).name}",
                            rationale=f"Title tag is too short ({len(title_text)} chars); recommended 45-65 chars for topic clarity.",
                            priority="P1",
                            expected_score_impact=3.0,
                            patch_params={"new_title": f"{title_text} — Professional Guide & Overview | {host}"},
                        )
                    )
                    patch_idx += 1

                # Meta description
                meta_desc = None
                for m in soup.find_all("meta"):
                    if m.get("name", "").lower() == "description":
                        meta_desc = m.get("content", "").strip()
                        break
                if not meta_desc:
                    patches.append(
                        RemediationPatch(
                            id=f"PATCH-{patch_idx:03d}",
                            patch_type=PatchType.META_DESCRIPTION.value,
                            relative_path=rel_file,
                            url=url,
                            title=f"Add Meta Description to {Path(rel_file).name}",
                            rationale="Page lacks meta description; search engines may synthesize arbitrary snippets.",
                            priority="P1",
                            expected_score_impact=3.5,
                            patch_params={
                                "new_description": f"Discover comprehensive insights and practical guidance on {h_path.stem}. Learn best practices, key features, and expert analysis."
                            },
                        )
                    )
                    patch_idx += 1

                # Heading hierarchy
                h1_tags = soup.find_all("h1")
                if len(h1_tags) == 0:
                    patches.append(
                        RemediationPatch(
                            id=f"PATCH-{patch_idx:03d}",
                            patch_type=PatchType.HEADING_HIERARCHY.value,
                            relative_path=rel_file,
                            url=url,
                            title=f"Insert Missing Primary H1 in {Path(rel_file).name}",
                            rationale="No <h1> found; page requires a single primary heading for semantic structure.",
                            priority="P0",
                            expected_score_impact=4.0,
                            patch_params={"h1_text": h_path.stem.replace("-", " ").title()},
                        )
                    )
                    patch_idx += 1
                elif len(h1_tags) > 1:
                    patches.append(
                        RemediationPatch(
                            id=f"PATCH-{patch_idx:03d}",
                            patch_type=PatchType.HEADING_HIERARCHY.value,
                            relative_path=rel_file,
                            url=url,
                            title=f"Demote Duplicate H1 Tags in {Path(rel_file).name}",
                            rationale=f"Multiple ({len(h1_tags)}) <h1> tags found; demote secondary H1s to <h2> for clear document outline.",
                            priority="P2",
                            expected_score_impact=2.0,
                            patch_params={"demote_extra_h1": True},
                        )
                    )
                    patch_idx += 1

                # Canonical
                canonical_tag = soup.find("link", attrs={"rel": lambda r: r and "canonical" in r})
                if not canonical_tag:
                    patches.append(
                        RemediationPatch(
                            id=f"PATCH-{patch_idx:03d}",
                            patch_type=PatchType.CANONICAL.value,
                            relative_path=rel_file,
                            url=url,
                            title=f"Add Canonical Link to {Path(rel_file).name}",
                            rationale="Missing self-referencing canonical URL; helps avoid duplicate content ambiguity.",
                            priority="P2",
                            expected_score_impact=2.0,
                            patch_params={"canonical_url": url},
                        )
                    )
                    patch_idx += 1

                # Direct answer gap on question headings
                for h in soup.find_all(["h2", "h3"]):
                    text = h.get_text().strip()
                    if text.endswith("?") or any(text.lower().startswith(w) for w in ("what is", "how to", "why does", "can you")):
                        next_el = h.find_next_sibling()
                        if not next_el or "aevora-direct-answer" not in next_el.get("class", []):
                            patches.append(
                                RemediationPatch(
                                    id=f"PATCH-{patch_idx:03d}",
                                    patch_type=PatchType.DIRECT_ANSWER.value,
                                    relative_path=rel_file,
                                    url=url,
                                    title=f"Add Direct Answer Box below '{text[:30]}...' in {Path(rel_file).name}",
                                    rationale=f"Question heading '{text}' is prime target for AI search engine answer extraction.",
                                    priority="P1",
                                    expected_score_impact=4.0,
                                    patch_params={
                                        "heading_pattern": text,
                                        "answer_text": f"{text.rstrip('?')} is an essential component designed to deliver reliable performance, compliance, and structured outcomes.",
                                    },
                                )
                            )
                            patch_idx += 1
                            break

                # Schema JSON-LD
                has_schema = False
                for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
                    if s.string and "@type" in s.string:
                        has_schema = True
                        break
                if not has_schema:
                    schema_data = {
                        "@context": "https://schema.org",
                        "@type": "WebPage",
                        "name": title_text or h_path.stem.title(),
                        "url": url,
                        "description": meta_desc or f"Comprehensive guide covering {h_path.stem}.",
                    }
                    patches.append(
                        RemediationPatch(
                            id=f"PATCH-{patch_idx:03d}",
                            patch_type=PatchType.SCHEMA_JSONLD.value,
                            relative_path=rel_file,
                            url=url,
                            title=f"Inject WebPage Schema.org JSON-LD in {Path(rel_file).name}",
                            rationale="No structured data found; adding Schema.org enhances search entity recognition.",
                            priority="P1",
                            expected_score_impact=4.5,
                            patch_params={"schema_data": schema_data},
                        )
                    )
                    patch_idx += 1
            except Exception:
                continue

    # Sort patches: P0 first, then P1, then P2
    p_order = {"P0": 0, "P1": 1, "P2": 2}
    patches.sort(key=lambda p: (p_order.get(p.priority, 3), p.relative_path))

    total_impact = min(35.0, sum(p.expected_score_impact for p in patches))

    return RemediationPlan(
        plan_id=plan_id,
        target_host=host,
        site_root=str(site_path),
        crawl_dir=str(crawl_path) if crawl_path else "",
        created_at=created_at,
        patches=patches,
        estimated_total_score_impact=total_impact,
    )
