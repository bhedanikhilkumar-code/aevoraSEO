"""Readable readiness observations and comparisons, using saved crawl evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from .evidence import capture_quality, missing_content, selected_data
from .extract import index_signals
from .network import RobotsRules, origin, utcnow


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_pages(folder):
    return [
        json.loads(line)
        for line in (Path(folder) / "pages.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def save_report(out, name, result, lines):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / (name + ".json")).write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / (name + ".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def readiness(pages, summary, robots, sitemaps):
    entries = []
    listed = {r["url"] for r in sitemaps.get("urls", [])}
    for page in pages:
        data, representation = selected_data(page)
        quality = capture_quality(page)
        url = page.get("final_url") or page["url"]
        observations = []

        def add(code, observation, why, action):
            if (
                code in {"main_content_empty", "title_missing", "h1_missing", "schema_review"}
                and not quality["absence_supported"]
            ):
                return
            observations.append(
                {
                    "code": code,
                    "observation": observation,
                    "why_it_matters": why,
                    "next_step": action,
                }
            )

        if page.get("error") or not 200 <= page.get("status", 0) < 300 or not data:
            add(
                "access_incomplete",
                "We did not capture usable page content.",
                "We cannot assess an unread page's answers or trust signals.",
                "Check access.json and the response, then repeat this page when access is available.",
            )
        else:
            if quality["limits"]:
                add(
                    "capture_incomplete",
                    "; ".join(quality["limits"]),
                    "A partial capture cannot establish missing answers or markup.",
                    "Resolve the recorded capture limitation and recapture this URL.",
                )
            missing = missing_content(page)
            if missing:
                add(
                    "missing_content_candidate",
                    "HTTP success returned a missing-content screen candidate.",
                    "A successful status alone does not establish that the intended page exists.",
                    "Inspect the saved text, repair referring links and return an appropriate status for missing pages.",
                )
            if not data.get("main_text"):
                add(
                    "main_content_empty",
                    "The captured page has no main text.",
                    "Important answers may be unavailable in this representation.",
                    "Inspect rendered HTML and dependency errors; provide accessible text for essential information.",
                )
            raw = page.get("data") or {}
            if (
                representation == "rendered"
                and data.get("word_count", 0) > raw.get("word_count", 0) + 50
            ):
                add(
                    "javascript_content",
                    "Substantial text arrived after JavaScript ran.",
                    "Different crawlers may see different content.",
                    "Compare the raw response with the full page; consider server-rendering important answers and links.",
                )
            if not data.get("title"):
                add(
                    "title_missing",
                    "The captured page has no title.",
                    "Its topic is harder to identify in search results and browser tabs.",
                    "Write a descriptive title matching this page's purpose.",
                )
            if not data.get("headings", {}).get("h1"):
                add(
                    "h1_missing",
                    "We found no H1 in the captured content.",
                    "A clear page heading can help visitors understand its purpose.",
                    "Review the visible structure and add a useful primary heading where appropriate.",
                )
            if data.get("jsonld_errors"):
                add(
                    "schema_syntax",
                    "At least one JSON-LD block could not be parsed.",
                    "Malformed structured data cannot reliably describe the page.",
                    "Fix the recorded syntax errors, then validate the intended schema against visible facts.",
                )
            if not data.get("schema_types") and not data.get("microdata_types"):
                add(
                    "schema_review",
                    "No JSON-LD or microdata types were observed.",
                    "Structured data may clarify real entities, but its absence does not establish an AI visibility problem.",
                    "Review relevant markup for this page; add only types and facts it actually supports.",
                )
        raw_signals = index_signals(
            page.get("data") or {}, page.get("headers") or {}, page.get("status", 0), url
        )
        selected_signals = index_signals(
            data, page.get("headers") or {}, page.get("status", 0), url
        )
        if (
            raw_signals["googlebot_noindex_observed"]
            or selected_signals["googlebot_noindex_observed"]
        ):
            add(
                "noindex_observed",
                "A noindex instruction was observed in the response or captured DOM.",
                "This can prevent the page from appearing in Google Search, including its AI features.",
                "Confirm whether the page should be public in search before changing this instruction.",
            )
        controls = (
            selected_signals["generic_meta"]
            + selected_signals["googlebot_meta"]
            + [selected_signals["x_robots_tag"]]
        )
        # Preserve exact header text; agent-specific headers need individual interpretation.
        snippet_controls = [
            v for v in controls if re.search(r"nosnippet|max-snippet\s*:\s*0(?:\D|$)", v, re.I)
        ]
        evidence = robots.get(origin(url))
        policies = {}
        for agent in ("Googlebot", "Bingbot"):
            policies[agent] = (
                None
                if not evidence or evidence.get("blocked")
                else RobotsRules(evidence.get("text", ""), agent=agent).allowed(url)
            )
        if any(v is False for v in policies.values()):
            add(
                "robots_restriction",
                "The saved robots file restricts this path for a checked search crawler.",
                "That crawler may be unable to discover current page content.",
                "Review the exact rule and its purpose; changing our crawl override does not change search-engine access.",
            )
        entries.append(
            {
                "url": page["url"],
                "final_url": url,
                "representation": representation,
                "status": page.get("status"),
                "main_words": data.get("word_count", 0),
                "body_words": data.get("body_word_count", 0),
                "in_observed_sitemap": page["url"] in listed or url in listed,
                "schema_types": data.get("schema_types", []),
                "microdata_types": data.get("microdata_types", []),
                "schema_errors": data.get("jsonld_errors", []),
                "robots_path_permissions": policies,
                "snippet_controls_to_review": snippet_controls,
                "index_signals_http": raw_signals,
                "index_signals_selected": selected_signals,
                "observations": observations,
            }
        )
    return {
        "schema_version": 1,
        "checked_at": summary.get("exported_at") or utcnow(),
        "seed": summary.get("seed"),
        "coverage_limited": summary.get("coverage_limited", True),
        "sitemap_urls_observed": len(listed),
        "sitemap_fetch_failures": summary.get("sitemap_fetch_failures", 0),
        "pages": entries,
        "not_measured": [
            "actual indexing",
            "AI answer inclusion",
            "competitor rankings",
            "independent reputation",
            "schema semantic validity",
        ],
        "interpretation": "These are access, text and markup observations. They do not measure an engine's trust, indexing or citations.",
    }


def export_readiness(out, pages=None, summary=None, robots=None, sitemaps=None):
    out = Path(out)
    result = readiness(
        pages if pages is not None else read_pages(out),
        summary if summary is not None else read_json(out / "summary.json"),
        robots if robots is not None else read_json(out / "robots.json"),
        sitemaps if sitemaps is not None else read_json(out / "sitemaps.json"),
    )
    lines = [
        "# Your website's search and answer readiness",
        "",
        "Here is what we could read, what needs attention, and what to do next.",
        "",
        result["interpretation"],
        "",
        f"Sitemap URLs observed: {result['sitemap_urls_observed']}. Coverage limited: {result['coverage_limited']}.",
        "",
        "Start with access problems on important pages, then review the content and proof that answer your customers' questions.",
    ]
    for p in result["pages"]:
        lines += [
            "",
            "## " + p["url"],
            "",
            f"Captured {p['main_words']} main-content words using {p['representation']}. Schema types: {', '.join(p['schema_types']) or 'none observed'}.",
        ]
        for item in p["observations"]:
            lines += [
                "",
                item["observation"]
                + " "
                + item["why_it_matters"]
                + " **Next:** "
                + item["next_step"],
            ]
        if not p["observations"]:
            lines += [
                "",
                "No issue was flagged by these limited checks. Review answer quality, entity facts and independent proof separately.",
            ]
    return save_report(out, "readiness", result, lines)


def normalize_text_for_diff(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def page_snapshot(page):
    data, representation = selected_data(page)
    signals = index_signals(
        data, page.get("headers") or {}, page.get("status", 0), page.get("final_url", page["url"])
    )
    main_text = data.get("main_text", "")
    norm_text = normalize_text_for_diff(main_text)
    norm_text_hash = hashlib.sha256(norm_text.encode("utf-8")).hexdigest() if norm_text else ""
    return {
        "status": page.get("status"),
        "error": page.get("error", ""),
        "final_url": page.get("final_url"),
        "representation": representation,
        "title": data.get("title"),
        "description": data.get("meta_description"),
        "h1": data.get("headings", {}).get("h1", []),
        "content_hash": norm_text_hash or data.get("content_sha256"),
        "word_count": data.get("word_count", 0),
        "canonical": data.get("canonical", []),
        "noindex": signals["googlebot_noindex_observed"],
        "schema_types": data.get("schema_types", []),
        "schema_errors": data.get("jsonld_errors", []),
        "render_error": (page.get("rendered") or {}).get("error", ""),
    }


def compare(before, after, out, format="terminal", status_filter="all", url_filter=None):
    a, b = Path(before), Path(after)
    sa, sb = read_json(a / "summary.json"), read_json(b / "summary.json")
    if sa["seed"] != sb["seed"]:
        raise ValueError(
            "Snapshot comparison needs the same seed URL. Compare competitors in the SEO workflow."
        )
    sf = (status_filter or "all").lower()
    if sf not in ("all", "added", "removed", "changed", "unchanged"):
        raise ValueError(
            f"Invalid status filter '{status_filter}'. Expected all, added, removed, changed, or unchanged."
        )
    left, right = ({p["url"]: page_snapshot(p) for p in read_pages(d)} for d in (a, b))

    if url_filter:
        try:
            pattern = re.compile(url_filter)
        except re.error as e:
            raise ValueError(f"Invalid URL filter regular expression: {e}") from e
        left = {u: p for u, p in left.items() if pattern.search(u)}
        right = {u: p for u, p in right.items() if pattern.search(u)}

    common_urls = sorted(left.keys() & right.keys())
    newly_observed = sorted(right.keys() - left.keys())
    not_reobserved = sorted(left.keys() - right.keys())

    changed = []
    unchanged = []
    errors = []

    for url in common_urls:
        l_page = left[url]
        r_page = right[url]
        if (
            l_page.get("error")
            or r_page.get("error")
            or l_page.get("status", 0) >= 400
            or r_page.get("status", 0) >= 400
        ):
            errors.append(url)
        fields = {
            k: {"before": l_page[k], "after": r_page[k]}
            for k in l_page
            if l_page[k] != r_page[k]
        }
        if fields:
            changed.append({"url": url, "fields": fields})
        else:
            unchanged.append(url)

    old_issues, new_issues = (
        {(r["url"], r["code"]) for r in read_json(d / "issues.json")} for d in (a, b)
    )
    # A disappearing URL or failed observation must never count as a resolved issue.
    comparable = {
        u
        for u in common_urls
        if left[u]["content_hash"]
        and right[u]["content_hash"]
        and not left[u]["error"]
        and not right[u]["error"]
        and left[u]["status"] == right[u]["status"] == 200
        and left[u]["representation"] == right[u]["representation"]
        and not left[u]["render_error"]
        and not right[u]["render_error"]
    }
    resolved = sorted(i for i in old_issues - new_issues if i[0] in comparable)
    result = {
        "checked_at": utcnow(),
        "seed": sa["seed"],
        "before_snapshot_id": sa.get("snapshot_id"),
        "after_snapshot_id": sb.get("snapshot_id"),
        "before_at": sa.get("exported_at"),
        "after_at": sb.get("exported_at"),
        "coverage_limited": bool(sa.get("coverage_limited") or sb.get("coverage_limited")),
        "configuration_changed": sa.get("configuration") != sb.get("configuration"),
        "summary": {
            "added": len(newly_observed),
            "removed": len(not_reobserved),
            "changed": len(changed),
            "unchanged": len(unchanged),
            "errors": len(errors),
            "total_before": len(left),
            "total_after": len(right),
        },
        "changed_pages": changed,
        "newly_observed_urls": newly_observed,
        "not_reobserved_urls": not_reobserved,
        "added_urls": newly_observed,
        "removed_urls": not_reobserved,
        "unchanged_urls": unchanged,
        "status_filter": sf,
        "filtered_urls": (
            newly_observed
            if sf == "added"
            else not_reobserved
            if sf == "removed"
            else [r["url"] for r in changed]
            if sf == "changed"
            else unchanged
            if sf == "unchanged"
            else []
        ),
        "new_findings": [{"url": u, "code": c} for u, c in sorted(new_issues - old_issues)],
        "findings_no_longer_observed_on_comparable_pages": [
            {"url": u, "code": c} for u, c in resolved
        ],
        "note": "Not reobserved does not mean deleted. Findings no longer observed need acceptance checks; crawl scope and rendering can affect comparison.",
    }
    lines = [
        "# What changed since the last review",
        "",
        f"Added: {len(newly_observed)} | Removed: {len(not_reobserved)} | Changed: {len(changed)} | Unchanged: {len(unchanged)} | Errors: {len(errors)}",
        "",
        f"{len(changed)} pages changed; {len(result['new_findings'])} new findings; {len(resolved)} findings no longer observed on comparable pages.",
        "",
        result["note"],
        "",
        f"Coverage limited: {result['coverage_limited']}. Configuration changed: {result['configuration_changed']}.",
    ]
    if sf != "all":
        lines.append(f"\nFiltered by state '{sf}': {len(result['filtered_urls'])} matching URLs.")
    for row in changed:
        lines += ["", "- " + row["url"] + ": " + ", ".join(row["fields"])]

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    # Export comparison.csv
    csv_rows = []
    if sf in ("all", "added"):
        for u in newly_observed:
            csv_rows.append({"url": u, "state": "ADDED", "field": "url", "before": "", "after": u})
    if sf in ("all", "removed"):
        for u in not_reobserved:
            csv_rows.append({"url": u, "state": "REMOVED", "field": "url", "before": u, "after": ""})
    if sf in ("all", "changed"):
        for row in changed:
            for f, diff in row["fields"].items():
                csv_rows.append(
                    {
                        "url": row["url"],
                        "state": "CHANGED",
                        "field": f,
                        "before": json.dumps(diff["before"], ensure_ascii=False)
                        if isinstance(diff["before"], (list, dict))
                        else str(diff["before"]),
                        "after": json.dumps(diff["after"], ensure_ascii=False)
                        if isinstance(diff["after"], (list, dict))
                        else str(diff["after"]),
                    }
                )
    if sf in ("all", "unchanged"):
        for u in unchanged:
            csv_rows.append(
                {"url": u, "state": "UNCHANGED", "field": "all", "before": "matched", "after": "matched"}
            )

    with (out / "comparison.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "state", "field", "before", "after"])
        writer.writeheader()
        if csv_rows:
            writer.writerows(csv_rows)

    return save_report(out, "comparison", result, lines)
