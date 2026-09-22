"""Verify discovered pages, preserving access and rendering limits."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from .backlink_persistence import persist_backlink_verification
from .engine import Crawler
from .evidence import capture_quality, combined_index_signals, missing_content, selected_data
from .network import Config, normalize_url, utcnow
from .review import read_json, read_pages, save_report


def sanitize_csv_cell(value):
    if value is None:
        return ""
    val_str = str(value)
    stripped = val_str.lstrip()
    if stripped and stripped[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val_str}"
    return val_str


def source_rows(path):
    if isinstance(path, list):
        rows = []
        for item in path:
            if isinstance(item, str):
                rows.append({"URL": item})
            elif isinstance(item, dict):
                rows.append(item)
    else:
        try:
            with Path(path).open(encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f, strict=True))
        except csv.Error as error:
            raise ValueError(
                "Malformed source CSV: "
                + str(error)
                + ". Use discovery's sources.csv or CSV doubled quotes, not JSON backslash escaping."
            ) from error
    result = {}
    for row in rows:
        if None in row:
            raise ValueError(
                "Source CSV has extra fields. Quote values containing commas correctly."
            )
        url = normalize_url(row.get("URL") or row.get("url") or "")
        if not url:
            raise ValueError("Source CSV needs a URL column with valid http(s) addresses.")
        provenance = row.get("provenance")
        if isinstance(provenance, str) and provenance:
            provenance = json.loads(provenance)
        provenance = provenance or [
            {k: v for k, v in row.items() if k not in ("URL", "url", "provenance") and v}
        ]
        if not isinstance(provenance, list) or any(
            not isinstance(item, dict) for item in provenance
        ):
            raise ValueError("Source provenance must be a JSON list of observations.")
        existing = result.setdefault(url, {**row, "URL": url, "provenance": []})
        for observation in provenance:
            if observation not in existing["provenance"]:
                existing["provenance"].append(observation)
    if not result:
        raise ValueError("Source CSV has no URLs.")
    return list(result.values())


def target_links(data, target_host):
    text = data.get("text") or data.get("main_text") or ""
    results = []
    target_clean = target_host.lower().removeprefix("www.")
    for link in data.get("links", []):
        link_url = link.get("url", "")
        h = (urlsplit(link_url).hostname or "").lower().removeprefix("www.")
        if h == target_clean:
            anchor = link.get("anchor") or link.get("text") or ""
            raw_rels = link.get("rel", [])
            rels = [str(r).lower() for r in (raw_rels if isinstance(raw_rels, list) else str(raw_rels).split())]
            is_dofollow = not any(r in ("nofollow", "ugc", "sponsored") for r in rels)
            ctx = link.get("context", "")
            if not ctx and anchor and anchor.strip() and text:
                idx = text.find(anchor)
                if idx != -1:
                    start = max(0, idx - 60)
                    end = min(len(text), idx + len(anchor) + 100)
                    ctx = text[start:end].strip()
            item = dict(link)
            item["target_path"] = urlsplit(link_url).path or "/"
            item["anchor"] = anchor
            item["text"] = anchor
            item["rel"] = rels
            item["is_dofollow"] = is_dofollow
            item["context"] = ctx
            results.append(item)
    return results


def mention_evidence(data, names):
    text = data.get("text") or data.get("main_text") or ""
    matches = []
    for name in dict.fromkeys(n.strip() for n in names if n and n.strip()):
        match = re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text, re.I)
        if match:
            matches.append(
                {"name": name, "excerpt": text[max(0, match.start() - 90) : match.end() + 130]}
            )
    return matches


def verify_source(
    source,
    target_host,
    out,
    mode="auto",
    allow_private=False,
    follow_redirects=True,
    brand="",
    aliases=(),
):
    host = urlsplit(source).hostname
    allowed_hosts = {host.removeprefix("www."), "www." + host.removeprefix("www.")}
    mode_now = mode
    attempts = []
    # Bounded redirect-host expansion; no ordinary outgoing links are followed.
    for index in range(7):
        folder = Path(out) / f"attempt-{index + 1:02d}"
        config = Config(
            source,
            max_pages=1,
            workers=1,
            sitemaps=False,
            render_mode=mode_now,
            allow_hosts=sorted(allowed_hosts),
            allow_private=allow_private,
            render_max_requests=100,
        )
        crawler = Crawler(config, folder)
        try:
            crawler.log = lambda _: None
            summary = crawler.run()
        finally:
            crawler.close()
        page = next((p for p in read_pages(folder) if p["url"] == config.url), {})
        data, representation = selected_data(page)
        links = target_links(data, target_host)
        attempts.append(
            {
                "folder": folder.name,
                "error": page.get("error", ""),
                "status": page.get("status", 0),
                "representation": representation,
                "allowed_hosts": sorted(allowed_hosts),
                "mode": mode_now,
            }
        )
        redirects = list(page.get("redirects", []))
        if page.get("error") in ("robots_scope_limited", "robots_disallowed"):
            for policy in read_json(folder / "robots.json").values():
                if policy.get("error") == "redirect_out_of_scope":
                    redirects.extend(policy.get("redirects", []))
        if (
            follow_redirects
            and page.get("error")
            in ("redirect_out_of_scope", "robots_scope_limited", "robots_disallowed")
            and index < 5
        ):
            new_hosts = {
                urlsplit(r["target"]).hostname
                for r in redirects
                if r.get("target") and normalize_url(r["target"])
            } - allowed_hosts
            if new_hosts:
                allowed_hosts.update(new_hosts)
                continue
        # Check late links on scripted pages even when their initial text looks substantial.
        if (
            mode == "auto"
            and mode_now != "browser"
            and not links
            and not page.get("error")
            and data.get("script_count")
            and not page.get("rendered")
            and not missing_content(page)
        ):
            mode_now = "browser"
            continue
        break
    rendered = page.get("rendered") or {}
    missing = missing_content(page)
    usable = (
        bool(data) and not page.get("error") and 200 <= page.get("status", 0) < 300 and not missing
    )
    incomplete_render = bool(
        rendered.get("error")
        or rendered.get("content_warning")
        or rendered.get("javascript_errors")
        or capture_quality(page)["limits"]
    )
    if usable and links:
        verification = "link_observed"
    elif usable and not incomplete_render:
        verification = "no_link_in_captured_content"
    else:
        verification = "unverified_access"
    mentions = mention_evidence(data, [brand, *aliases]) if usable else []
    classification = classify_source_context(source, data.get("title", ""), data.get("main_text", ""))
    return {
        "source_url": source,
        "final_url": page.get("final_url"),
        "status": page.get("status"),
        "checked_at": utcnow(),
        "verification": verification,
        "representation": representation,
        "coverage_limited": summary["coverage_limited"] or incomplete_render,
        "target_links": links if usable else [],
        "brand_mentions": mentions,
        "mention_status": "observed_in_page"
        if mentions
        else "not_observed_in_capture"
        if usable
        else "unverified",
        "suggested_classification": classification,
        "source_index_signals": combined_index_signals(page),
        "error": page.get("error", ""),
        "access": page.get("access"),
        "robots_decision": page.get("robots_decision"),
        "missing_content_candidate": missing,
        "render_error": rendered.get("error", ""),
        "render_warning": rendered.get("content_warning", ""),
        "title": data.get("title", ""),
        "main_excerpt": data.get("main_text", "")[:500],
        "independent_endorsement": "not_assessed",
        "evidence_folder": str(folder),
        "attempt_history": attempts,
    }


def classify_source_context(url: str, title: str = "", text: str = "") -> dict:
    """Classify a source candidate into standard context and relationship categories."""
    h = (urlsplit(url).hostname or "").lower().removeprefix("www.")
    path = (urlsplit(url).path or "").lower()

    if any(k in h for k in ("forum", "community", "reddit.com", "quora.com", "stackexchange.com", "discord.com", "discourse")) or any(k in path for k in ("/forum/", "/threads/", "/comments/", "/discussion/")):
        return {"context": "user_generated", "relationship": "independent", "basis": "community_domain_or_path"}

    if any(k in h for k in ("directory", "catalog", "yellowpages", "yelp.com", "clutch.co")) or any(k in path for k in ("/directory/", "/categories/", "/listing/")):
        return {"context": "directory", "relationship": "third_party_profile", "basis": "directory_domain_or_path"}

    if any(k in path for k in ("/profile/", "/user/", "/users/", "/u/", "/member/", "/author/", "/company/", "/org/")) or any(k in h for k in ("linkedin.com", "github.com", "crunchbase.com")):
        return {"context": "directory", "relationship": "third_party_profile", "basis": "profile_path_or_domain"}

    return {"context": "editorial", "relationship": "independent", "basis": "standard_publisher_content"}


def check_sources(
    sources,
    target,
    out,
    limit=30,
    mode="auto",
    allow_private=False,
    follow_redirects=True,
    brand="",
    aliases=(),
):
    target = normalize_url(target)
    if not target or not 1 <= limit <= 500:
        raise ValueError("Supply a valid target URL and a source limit from 1 to 500.")
    if sources is None:
        cat_file = Path(__file__).resolve().parents[2] / "playbooks/backlink-system/posting-sites.json"
        if cat_file.exists():
            catalog_rows = json.loads(cat_file.read_text(encoding="utf-8"))
            inputs = [{"URL": s["website_url"], "name": s["name"], "kind": s["kind"]} for s in catalog_rows[:limit]]
        else:
            inputs = []
    else:
        inputs = source_rows(sources)
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError("Choose a new backlink-check output folder.")
    out.mkdir(parents=True, exist_ok=True)
    target_host = urlsplit(target).hostname.removeprefix("www.")
    results = []
    for row in inputs[:limit]:
        source = row["URL"]
        folder = out / "sources" / hashlib.sha256(source.encode()).hexdigest()[:20]
        result = verify_source(
            source, target_host, folder, mode, allow_private, follow_redirects, brand, aliases
        )
        try:
            result["evidence_folder"] = Path(result["evidence_folder"]).relative_to(out).as_posix()
        except Exception:
            result["evidence_folder"] = str(result["evidence_folder"])
        result["discovery"] = {k: v for k, v in row.items() if k != "URL" and v}
        results.append(result)

    referring_domains = set()
    total_links = 0
    dofollow_count = 0
    nofollow_count = 0
    for r in results:
        t_links = r.get("target_links", [])
        if t_links:
            referring_domains.add((urlsplit(r.get("final_url") or r["source_url"]).hostname or "").lower().removeprefix("www."))
            total_links += len(t_links)
            for l in t_links:
                if l.get("is_dofollow", True):
                    dofollow_count += 1
                else:
                    nofollow_count += 1

    summary_result = {
        "target": target,
        "brand": brand,
        "checked_at": utcnow(),
        "sources_supplied": len(inputs),
        "sources_checked": len(results),
        "sources_remaining": max(0, len(inputs) - len(results)),
        "observed_link_pages": sum(r["verification"] == "link_observed" for r in results),
        "observed_mention_pages": sum(bool(r["brand_mentions"]) for r in results),
        "unverified_pages": sum(r["verification"] == "unverified_access" for r in results),
        "referring_domains": sorted(referring_domains),
        "referring_domains_count": len(referring_domains),
        "total_links_observed": total_links,
        "dofollow_links_count": dofollow_count,
        "nofollow_links_count": nofollow_count,
        "results": results,
        "note": "A supplied/search-result URL is a candidate. Links and mentions are verified separately in captured content. This is a bounded sample, not a complete backlink count or proof of indexing, endorsement or ranking value.",
    }
    lines = [
        "# Your backlink and mention evidence",
        "",
        f"Checked {len(results)} sources for target {target}.",
        f"- Verified Backlinks Observed: {summary_result['observed_link_pages']} pages ({total_links} total links: {dofollow_count} dofollow, {nofollow_count} nofollow/ugc/sponsored).",
        f"- Unique Referring Domains: {len(referring_domains)} ({', '.join(sorted(referring_domains)) if referring_domains else 'none'}).",
        f"- Brand Mentions Observed: {summary_result['observed_mention_pages']} pages.",
        f"- Unverified / Inaccessible: {summary_result['unverified_pages']} pages.",
        "",
        summary_result["note"],
        "",
        "## Verified Source Pages",
        "",
    ]
    lines += [
        f"- {r['source_url']} — {r['verification']} ({r['representation']}; {r['error'] or 'response captured'})"
        for r in results
    ]

    save_report(out, "backlinks", summary_result, lines)

    # Export backlinks.csv
    csv_rows = []
    for r in results:
        for l in r.get("target_links", []):
            csv_rows.append({
                "source_url": r.get("source_url", ""),
                "final_url": r.get("final_url", ""),
                "verification": r.get("verification", ""),
                "target_url": l.get("url", ""),
                "anchor": l.get("anchor", "") or l.get("text", ""),
                "rel": " ".join(l.get("rel", [])),
                "is_dofollow": "yes" if l.get("is_dofollow", True) else "no",
                "context": l.get("context", ""),
            })
    csv_fields = ["source_url", "final_url", "verification", "target_url", "anchor", "rel", "is_dofollow", "context"]
    csv_path = out / "backlinks.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow({k: sanitize_csv_cell(v) for k, v in row.items()})

    # Persist to SQLite
    try:
        persist_backlink_verification(out / "backlinks.sqlite3", summary_result)
    except Exception:
        pass

    return summary_result
