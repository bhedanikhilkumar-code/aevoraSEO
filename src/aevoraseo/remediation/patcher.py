"""Deterministic HTML & content patch generators for SEO/AEO/GEO remediation.

Generates precise, syntax-safe AST patches for titles, meta descriptions,
heading hierarchy, direct-answer definitions, schema JSON-LD, canonical tags,
and internal links.
"""

from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from bs4 import BeautifulSoup, Tag


class PatchType(str, Enum):
    TITLE = "title"
    META_DESCRIPTION = "meta_description"
    HEADING_HIERARCHY = "heading_hierarchy"
    DIRECT_ANSWER = "direct_answer"
    SCHEMA_JSONLD = "schema_jsonld"
    CANONICAL = "canonical"
    INTERNAL_LINK = "internal_link"


@dataclass
class PatchResult:
    success: bool
    patch_type: PatchType
    original_snippet: str
    replacement_snippet: str
    full_html: str
    diff: str
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "patch_type": self.patch_type.value,
            "original_snippet": self.original_snippet,
            "replacement_snippet": self.replacement_snippet,
            "diff": self.diff,
            "details": self.details,
        }


def _make_diff(original: str, modified: str, filename: str = "content.html") -> str:
    """Generate a clean unified diff string between original and modified text."""
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=3,
    )
    return "".join(diff)


def patch_title(html: str, new_title: str, filename: str = "content.html") -> PatchResult:
    """Insert or replace the <title> tag with new_title."""
    clean_title = new_title.strip()
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")

    if title_tag:
        orig_snippet = str(title_tag)
        title_tag.string = clean_title
        mod_snippet = str(title_tag)
        details = f"Replaced existing title tag with '{clean_title}'"
    else:
        orig_snippet = ""
        head = soup.find("head")
        new_tag = soup.new_tag("title")
        new_tag.string = clean_title
        if head:
            head.insert(0, new_tag)
            details = f"Inserted title tag into <head>: '{clean_title}'"
        else:
            soup.insert(0, new_tag)
            details = f"Inserted title tag at root: '{clean_title}'"
        mod_snippet = str(new_tag)

    modified_html = str(soup)
    diff = _make_diff(html, modified_html, filename)
    return PatchResult(
        success=True,
        patch_type=PatchType.TITLE,
        original_snippet=orig_snippet,
        replacement_snippet=mod_snippet,
        full_html=modified_html,
        diff=diff,
        details=details,
    )


def patch_meta_description(html: str, new_description: str, filename: str = "content.html") -> PatchResult:
    """Insert or update <meta name="description" content="...">."""
    clean_desc = new_description.strip()
    soup = BeautifulSoup(html, "html.parser")

    # Case-insensitive search for meta description
    meta_tag = None
    for m in soup.find_all("meta"):
        if m.get("name", "").lower() == "description":
            meta_tag = m
            break

    if meta_tag:
        orig_snippet = str(meta_tag)
        meta_tag["content"] = clean_desc
        mod_snippet = str(meta_tag)
        details = f"Updated existing meta description ({len(clean_desc)} chars)"
    else:
        orig_snippet = ""
        new_meta = soup.new_tag("meta", attrs={"name": "description", "content": clean_desc})
        head = soup.find("head")
        if head:
            # Place after title if possible, else append
            title_tag = head.find("title")
            if title_tag:
                title_tag.insert_after(new_meta)
            else:
                head.append(new_meta)
            details = f"Inserted meta description into <head> ({len(clean_desc)} chars)"
        else:
            soup.insert(0, new_meta)
            details = f"Inserted meta description at root ({len(clean_desc)} chars)"
        mod_snippet = str(new_meta)

    modified_html = str(soup)
    diff = _make_diff(html, modified_html, filename)
    return PatchResult(
        success=True,
        patch_type=PatchType.META_DESCRIPTION,
        original_snippet=orig_snippet,
        replacement_snippet=mod_snippet,
        full_html=modified_html,
        diff=diff,
        details=details,
    )


def patch_headings(
    html: str,
    h1_text: str | None = None,
    demote_extra_h1: bool = True,
    level_repairs: dict[str, str] | None = None,
    filename: str = "content.html",
) -> PatchResult:
    """Ensure a single primary <h1> tag and repair skipped heading levels (e.g. h3->h2)."""
    soup = BeautifulSoup(html, "html.parser")
    h1_tags = soup.find_all("h1")
    changes: list[str] = []
    orig_snippets: list[str] = []
    mod_snippets: list[str] = []

    if not h1_tags and h1_text:
        new_h1 = soup.new_tag("h1")
        new_h1.string = h1_text.strip()
        body = soup.find("body") or soup.find("main") or soup.find("article")
        if body:
            body.insert(0, new_h1)
        else:
            soup.insert(0, new_h1)
        changes.append(f"Inserted primary <h1>: '{h1_text.strip()}'")
        orig_snippets.append("")
        mod_snippets.append(str(new_h1))
    elif h1_tags:
        if h1_text:
            orig_snippets.append(str(h1_tags[0]))
            h1_tags[0].string = h1_text.strip()
            mod_snippets.append(str(h1_tags[0]))
            changes.append(f"Updated primary <h1> to: '{h1_text.strip()}'")

        if demote_extra_h1 and len(h1_tags) > 1:
            for extra in h1_tags[1:]:
                orig_snippets.append(str(extra))
                extra.name = "h2"
                mod_snippets.append(str(extra))
                changes.append(f"Demoted secondary <h1> '{extra.get_text()[:30]}' to <h2>")

    if level_repairs:
        for from_tag, to_tag in level_repairs.items():
            for t in soup.find_all(from_tag):
                orig_snippets.append(str(t))
                t.name = to_tag
                mod_snippets.append(str(t))
                changes.append(f"Repaired skipped level: {from_tag} -> {to_tag}")

    modified_html = str(soup)
    diff = _make_diff(html, modified_html, filename)
    return PatchResult(
        success=bool(changes),
        patch_type=PatchType.HEADING_HIERARCHY,
        original_snippet="\n".join(orig_snippets),
        replacement_snippet="\n".join(mod_snippets),
        full_html=modified_html,
        diff=diff,
        details="; ".join(changes) if changes else "No heading changes required",
    )


def patch_direct_answer(
    html: str,
    heading_pattern: str,
    answer_text: str,
    list_items: list[str] | None = None,
    filename: str = "content.html",
) -> PatchResult:
    """Inject a semantic direct-answer box immediately below a matching question heading."""
    soup = BeautifulSoup(html, "html.parser")
    clean_answer = answer_text.strip()
    target_heading = None

    # Search headings (h2, h3, h4) for pattern
    for h in soup.find_all(["h1", "h2", "h3", "h4", "h5"]):
        text = h.get_text().strip().lower()
        if heading_pattern.lower() in text or re.search(re.escape(heading_pattern.lower()), text):
            target_heading = h
            break

    if not target_heading:
        return PatchResult(
            success=False,
            patch_type=PatchType.DIRECT_ANSWER,
            original_snippet="",
            replacement_snippet="",
            full_html=html,
            diff="",
            details=f"Target heading matching '{heading_pattern}' not found",
        )

    # Check if a direct answer block is already present
    next_sibling = target_heading.find_next_sibling()
    if next_sibling and isinstance(next_sibling, Tag) and "aevora-direct-answer" in next_sibling.get("class", []):
        orig_snippet = str(next_sibling)
        p = next_sibling.find("p")
        if p:
            p.string = clean_answer
        else:
            new_p = soup.new_tag("p", attrs={"class": "aevora-definition"})
            new_p.string = clean_answer
            next_sibling.insert(0, new_p)
        mod_snippet = str(next_sibling)
        details = f"Updated existing direct-answer block below <{target_heading.name}>"
    else:
        orig_snippet = ""
        container = soup.new_tag("div", attrs={"class": "aevora-direct-answer", "data-aevora-type": "direct-answer"})
        p = soup.new_tag("p", attrs={"class": "aevora-definition"})
        p.string = clean_answer
        container.append(p)

        if list_items:
            ul = soup.new_tag("ul", attrs={"class": "aevora-answer-list"})
            for item in list_items:
                li = soup.new_tag("li")
                li.string = item.strip()
                ul.append(li)
            container.append(ul)

        target_heading.insert_after(container)
        mod_snippet = str(container)
        details = f"Injected semantic direct-answer block below <{target_heading.name}> '{target_heading.get_text()[:40]}'"

    modified_html = str(soup)
    diff = _make_diff(html, modified_html, filename)
    return PatchResult(
        success=True,
        patch_type=PatchType.DIRECT_ANSWER,
        original_snippet=orig_snippet,
        replacement_snippet=mod_snippet,
        full_html=modified_html,
        diff=diff,
        details=details,
    )


def patch_schema(
    html: str,
    schema_data: dict[str, Any],
    filename: str = "content.html",
) -> PatchResult:
    """Inject a formatted Schema.org JSON-LD script block into <head>."""
    soup = BeautifulSoup(html, "html.parser")
    schema_type = schema_data.get("@type", "Thing")

    # Format JSON-LD
    json_ld_str = json.dumps(schema_data, ensure_ascii=False, indent=2)

    # Check for existing identical schema type to avoid redundant duplication
    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            parsed = json.loads(s.string or "{}")
            if parsed.get("@type") == schema_type and parsed.get("name") == schema_data.get("name"):
                return PatchResult(
                    success=False,
                    patch_type=PatchType.SCHEMA_JSONLD,
                    original_snippet=str(s),
                    replacement_snippet="",
                    full_html=html,
                    diff="",
                    details=f"Schema @type '{schema_type}' already exists in document",
                )
        except Exception:
            continue

    script_tag = soup.new_tag("script", attrs={"type": "application/ld+json"})
    script_tag.string = f"\n{json_ld_str}\n"

    head = soup.find("head")
    if head:
        head.append(script_tag)
        details = f"Appended Schema.org JSON-LD (@type: '{schema_type}') to <head>"
    else:
        soup.insert(0, script_tag)
        details = f"Inserted Schema.org JSON-LD (@type: '{schema_type}') at document root"

    modified_html = str(soup)
    diff = _make_diff(html, modified_html, filename)
    return PatchResult(
        success=True,
        patch_type=PatchType.SCHEMA_JSONLD,
        original_snippet="",
        replacement_snippet=str(script_tag),
        full_html=modified_html,
        diff=diff,
        details=details,
    )


def patch_canonical(
    html: str,
    canonical_url: str,
    filename: str = "content.html",
) -> PatchResult:
    """Insert or update <link rel="canonical" href="...">."""
    clean_url = canonical_url.strip()
    soup = BeautifulSoup(html, "html.parser")
    canonical_tag = soup.find("link", attrs={"rel": lambda r: r and "canonical" in r})

    if canonical_tag:
        orig_snippet = str(canonical_tag)
        canonical_tag["href"] = clean_url
        mod_snippet = str(canonical_tag)
        details = f"Updated canonical link href to '{clean_url}'"
    else:
        orig_snippet = ""
        new_tag = soup.new_tag("link", attrs={"rel": "canonical", "href": clean_url})
        head = soup.find("head")
        if head:
            head.append(new_tag)
            details = f"Appended canonical link to <head>: '{clean_url}'"
        else:
            soup.insert(0, new_tag)
            details = f"Inserted canonical link at root: '{clean_url}'"
        mod_snippet = str(new_tag)

    modified_html = str(soup)
    diff = _make_diff(html, modified_html, filename)
    return PatchResult(
        success=True,
        patch_type=PatchType.CANONICAL,
        original_snippet=orig_snippet,
        replacement_snippet=mod_snippet,
        full_html=modified_html,
        diff=diff,
        details=details,
    )


def patch_internal_link(
    html: str,
    target_url: str,
    anchor_text: str,
    context_keyword: str | None = None,
    filename: str = "content.html",
) -> PatchResult:
    """Inject an internal link into a matching body paragraph or as a contextual related link."""
    clean_url = target_url.strip()
    clean_anchor = anchor_text.strip()
    soup = BeautifulSoup(html, "html.parser")
    linked = False
    orig_snippet = ""
    mod_snippet = ""

    # Check paragraphs for clean_anchor occurrence as plain text
    paragraphs = soup.find_all("p")
    for p in paragraphs:
        text = p.get_text()
        # Look for exact anchor text inside paragraph that isn't already inside an <a> tag
        if clean_anchor.lower() in text.lower():
            # If paragraph doesn't already link to target_url
            if not p.find("a", href=clean_url):
                orig_snippet = str(p)
                # Regex replace first case-insensitive plain occurrence
                pattern = re.compile(re.escape(clean_anchor), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    exact_text = match.group(0)
                    new_p_html = str(p).replace(exact_text, f'<a href="{clean_url}">{exact_text}</a>', 1)
                    new_p_soup = BeautifulSoup(new_p_html, "html.parser")
                    p.replace_with(new_p_soup)
                    mod_snippet = new_p_html
                    linked = True
                    details = f"Converted in-paragraph anchor text '{exact_text}' into link to '{clean_url}'"
                    break

    # If anchor text wasn't found in paragraphs, append a contextual related link
    if not linked:
        container = soup.find("main") or soup.find("article") or soup.find("body") or soup
        rel_p = soup.new_tag("p", attrs={"class": "aevora-related-link"})
        rel_p.string = "Explore further: "
        a_tag = soup.new_tag("a", href=clean_url)
        a_tag.string = clean_anchor
        rel_p.append(a_tag)
        container.append(rel_p)
        orig_snippet = ""
        mod_snippet = str(rel_p)
        details = f"Appended contextual related link block to '{clean_url}' with anchor '{clean_anchor}'"

    modified_html = str(soup)
    diff = _make_diff(html, modified_html, filename)
    return PatchResult(
        success=True,
        patch_type=PatchType.INTERNAL_LINK,
        original_snippet=orig_snippet,
        replacement_snippet=mod_snippet,
        full_html=modified_html,
        diff=diff,
        details=details,
    )
