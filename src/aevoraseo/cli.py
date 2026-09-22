#!/usr/bin/env python3
"""AevoraSEO: inspect, improve and review your website's search foundations."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


def parser():
    root = argparse.ArgumentParser(prog="aevoraseo", description=__doc__)
    from . import __version__

    root.add_argument("--version", action="version", version="AevoraSEO " + __version__)
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("crawl", "scrape", "watch"):
        p = sub.add_parser(name)
        p.add_argument("url")
        p.add_argument("--out", required=True, type=Path)
        p.add_argument(
            "--profile",
            choices=["quick", "standard", "deep"],
            default="standard",
            help="Crawl profile preset (quick: rapid diagnostic, standard: balanced default, deep: comprehensive analysis).",
        )
        p.add_argument(
            "--incremental",
            type=Path,
            default=None,
            help="Incremental crawl against a previous snapshot directory, reusing unchanged pages.",
        )
        p.add_argument("--max-pages", type=int, default=None)
        if name == "watch":
            p.add_argument("--cycles", type=int, default=3)
            p.add_argument(
                "--interval",
                type=int,
                default=3600,
                help="Seconds between completed runs; minimum 60.",
            )
        p.add_argument("--max-depth", type=int, default=None)
        p.add_argument("--workers", type=int, default=None)
        p.add_argument("--delay", type=float, default=None)
        p.add_argument("--timeout", type=float, default=None)
        p.add_argument("--retries", type=int, default=None)
        p.add_argument("--max-bytes", type=int, default=5_000_000)
        p.add_argument("--max-discovered", type=int, default=10_000)
        p.add_argument("--max-sitemaps", type=int, default=25)
        p.add_argument("--max-query-variants", type=int, default=20)
        p.add_argument(
            "--allow-host",
            action="append",
            default=[],
            help="Additional exact website host to crawl (e.g. www.example.com).",
        )
        p.add_argument(
            "--include-www",
            action="store_true",
            help="Include the seed host's exact www/non-www counterpart; retain robots and address checks.",
        )
        p.add_argument(
            "--exclude", action="append", default=[], help="Regex against full normalized URL."
        )
        p.add_argument(
            "--allow-private",
            action="store_true",
            help="Permit nonpublic IPs for an explicitly intended local/staging audit.",
        )
        p.add_argument("--no-sitemaps", action="store_true")
        p.add_argument("--keep-tracking", action="store_true")
        p.add_argument("--no-html", action="store_true")
        p.add_argument(
            "--resume",
            action="store_true",
            help="Continue the same snapshot; completed pages are not fetched again.",
        )
        p.add_argument(
            "--render",
            action="store_true",
            help="Also inspect JavaScript using local Playwright Chromium.",
        )
        p.add_argument("--render-wait-ms", type=int, default=1000)
        p.add_argument("--render-max-requests", type=int, default=100)
        p.add_argument(
            "--render-allow-host",
            action="append",
            default=[],
            help="Allow an exact additional host for browser assets/APIs only.",
        )
        p.add_argument(
            "--mode",
            choices=["auto", "http", "browser"],
            default=None,
            help="Auto renders likely JavaScript shells; browser renders every HTML page.",
        )
        p.add_argument(
            "--robots",
            choices=["respect", "ignore"],
            default="respect",
            help="Ignore is an explicit override for authorized crawls; recorded in every run.",
        )
        p.add_argument(
            "--browser-assets",
            choices=["public", "allowlist"],
            default="public",
            help="Load public dependency hosts or restrict to the explicit host list.",
        )
        p.add_argument(
            "--wait-for-selector",
            default="",
            help="Wait for a visible CSS selector before capture.",
        )
        p.add_argument(
            "--render-settle-ms",
            type=int,
            default=1500,
            help="Maximum extra observation window for text/link stability.",
        )
        p.add_argument(
            "--scroll-steps",
            type=int,
            default=None,
            help="Bounded viewport scrolls to expose lazy content; 0 disables.",
        )
        p.add_argument(
            "--screenshot",
            action="store_true",
            help="Capture a viewport PNG; enables browser mode and image/font loading.",
        )
        p.add_argument("--headed", action="store_true", help="Show the local browser window.")
        p.add_argument(
            "--selectors",
            type=Path,
            help="JSON map of names to CSS selectors or selector/attribute/all objects.",
        )
        p.add_argument("--quiet", action="store_true")
        p.add_argument("--no-color", action="store_true")
    p = sub.add_parser("report", help="Regenerate reports from an existing local crawl database.")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser(
        "present", help="Export an offline AevoraSEO-branded HTML/PDF client report."
    )
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Reviewed report-content JSON.")
    source.add_argument(
        "--audit", type=Path, help="Existing audit.json; preserve its findings and limits."
    )
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--format", choices=["both", "html", "pdf"], default="both")
    p.add_argument("--overwrite", action="store_true")
    p = sub.add_parser(
        "doctor", help="Check runtime; optionally probe target and search separately."
    )
    p.add_argument("--target")
    p.add_argument("--query")
    p.add_argument("--out", type=Path)
    from .research_cli import add_commands

    add_commands(sub)
    sub.add_parser(
        "browser-setup", help="Check first; install missing free Chromium support in this runtime."
    )
    p = sub.add_parser("readiness", help="Explain search and answer readiness from saved evidence.")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("compare", help="Compare two snapshots of the same website.")
    p.add_argument("--before", type=Path, required=True, help="Path to initial crawl snapshot.")
    p.add_argument("--after", type=Path, required=True, help="Path to subsequent crawl snapshot.")
    p.add_argument("--out", type=Path, required=True, help="Path to write comparison report.")
    p.add_argument(
        "--format",
        choices=["terminal", "json", "csv", "markdown"],
        default="terminal",
        help="Format for comparison output.",
    )
    p.add_argument(
        "--status",
        choices=["all", "added", "removed", "changed", "unchanged"],
        default="all",
        help="Filter compared pages by state.",
    )
    p.add_argument("--filter", default=None, help="Regex pattern to filter compared URLs.")
    p = sub.add_parser(
        "aeo",
        help="Analyze answer readiness, GEO signals, and AI crawler accessibility.",
    )
    p.add_argument("snapshot", type=Path, help="Path to crawl snapshot folder.")
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Directory to save aeo_report.json, aeo_summary.md, aeo_pages.csv.",
    )
    p.add_argument(
        "--visibility",
        type=Path,
        default=None,
        help="Optional external observed visibility records (.json or .csv).",
    )
    p.add_argument(
        "--format",
        choices=["terminal", "json", "csv", "markdown"],
        default="terminal",
        help="Output presentation format.",
    )
    p = sub.add_parser(
        "aeo-compare",
        help="Compare AEO/GEO scores and signals between two crawl snapshots.",
    )
    p.add_argument(
        "--before",
        type=Path,
        required=True,
        help="Path to baseline crawl snapshot folder.",
    )
    p.add_argument(
        "--after",
        type=Path,
        required=True,
        help="Path to subsequent crawl snapshot folder.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Directory to save comparison outputs.",
    )
    p.add_argument(
        "--format",
        choices=["terminal", "json", "csv", "markdown"],
        default="terminal",
        help="Output presentation format.",
    )
    p = sub.add_parser("backlinks", help="Check supplied source pages for links to a website.")
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-sources", type=int, default=30)
    p.add_argument("--mode", choices=["http", "auto", "browser"], default="auto")
    p.add_argument("--allow-private", action="store_true")
    p.add_argument("--brand", default="", help="Brand name to verify mentions in captured pages.")
    p.add_argument("--alias", action="append", default=[])
    p.add_argument(
        "--no-follow-redirects",
        action="store_true",
        help="Keep redirected source hosts within the initial scope.",
    )
    p = sub.add_parser(
        "search-plan",
        help="Prepare a bounded Google discovery plan; does not claim to run searches.",
    )
    p.add_argument("--target", required=True)
    p.add_argument("--brand", required=True)
    p.add_argument("--pages", type=int, default=5)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser(
        "search-import", help="Extract candidate links from saved public search result HTML."
    )
    p.add_argument("--html", type=Path, nargs="+", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--captured-at", required=True)
    p.add_argument("--engine", default="Google")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser(
        "reputation", help="AevoraSEO's estimated reputation score from verified source evidence."
    )
    inputs = p.add_mutually_exclusive_group(required=True)
    inputs.add_argument(
        "--sources", type=Path, help="Discovered source CSV; pages are fetched and verified."
    )
    inputs.add_argument(
        "--evidence",
        type=Path,
        help="Reuse a prior brand-aware backlinks.json; no new live checks.",
    )
    p.add_argument("--target", required=True)
    p.add_argument("--brand", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-sources", type=int, default=50)
    p.add_argument("--search-pages", type=int, default=5)
    p.add_argument("--mode", choices=["http", "auto", "browser"], default="auto")
    p.add_argument("--alias", action="append", default=[])
    p.add_argument("--related-host", action="append", default=[])
    p.add_argument("--allow-private", action="store_true")
    edit = sub.add_parser("edit", help="Stage, apply or roll back a reviewed content file.")
    actions = edit.add_subparsers(dest="action", required=True)
    for action in ("plan", "apply", "rollback"):
        p = actions.add_parser(action)
        target = p.add_mutually_exclusive_group(required=True)
        target.add_argument("--site", type=Path, help="Existing local site root.")
        target.add_argument(
            "--connection",
            type=Path,
            help="SFTP/FTPS profile with environment-variable references.",
        )
        if action == "plan":
            p.add_argument(
                "--file", required=True, help="Relative path of an existing website content file."
            )
            p.add_argument("--replacement", type=Path, required=True)
            p.add_argument("--out", type=Path, required=True)
        else:
            p.add_argument("--plan", type=Path, required=True)
            p.add_argument(
                "--expect-plan", required=True, help="SHA-256 of the reviewed plan.json."
            )
    return root


class OutputLock:
    def __init__(self, out):
        self.path = out / "crawl.lock"

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise ValueError(
                "crawl.lock exists. Stop the other crawl; remove a stale lock only after checking its recorded PID."
            )
        with os.fdopen(fd, "w") as f:
            json.dump({"pid": os.getpid()}, f)
        return self

    def __exit__(self, *args):
        self.path.unlink(missing_ok=True)


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == "browser-setup":
        from .doctor import prepare_browser

        result = prepare_browser()
        print(json.dumps(result, indent=2))
        return 0 if result["status"] in ("ready", "already_ready") else 1
    if args.command == "doctor":
        from .doctor import check_environment

        return check_environment(args.target, args.query, args.out)
    if args.command == "present":
        from .reports import export_report, from_audit

        try:
            source = args.input or args.audit
            if source.stat().st_size > 5_000_000:
                raise ValueError(
                    "Report input exceeds 5 MB; split the report or keep raw evidence in a separate appendix."
                )
            data = json.loads(source.read_text(encoding="utf-8"))
            if args.audit:
                data = from_audit(data)
            result = export_report(data, args.out, args.format, args.overwrite)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print("Report export failed: " + str(exc), file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "complete" else 1
    if not importlib.util.find_spec("bs4"):
        print(
            "Install local dependencies from the repository: python -m pip install -e .",
            file=sys.stderr,
        )
        return 2
    from aevoraseo.engine import Crawler
    from aevoraseo.network import Config

    crawler = None
    try:
        if args.command in (
            "discover",
            "profile",
            "competitors",
            "audit",
            "research-plan",
            "compare-reputation",
        ):
            from .research_cli import execute

            result = execute(args)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command in (
            "readiness",
            "compare",
            "aeo",
            "aeo-compare",
            "backlinks",
            "edit",
            "reputation",
            "search-plan",
            "search-import",
        ):
            if args.command == "readiness":
                from .review import export_readiness

                result = export_readiness(args.out)
            elif args.command == "compare":
                from .review import compare

                fmt = getattr(args, "format", "terminal")
                result = compare(
                    args.before,
                    args.after,
                    args.out,
                    format=fmt,
                    status_filter=getattr(args, "status", "all"),
                    url_filter=getattr(args, "filter", None),
                )
                if fmt == "terminal":
                    s = result.get("summary", {})
                    out_lines = [
                        "Snapshot comparison",
                        f"Before: {result.get('before_snapshot_id') or result.get('before_at') or 'N/A'}",
                        f"After:  {result.get('after_snapshot_id') or result.get('after_at') or 'N/A'}",
                        "",
                        f"Added:     {s.get('added', 0)}",
                        f"Removed:   {s.get('removed', 0)}",
                        f"Changed:   {s.get('changed', 0)}",
                        f"Unchanged: {s.get('unchanged', 0)}",
                        f"Errors:    {s.get('errors', 0)}",
                    ]
                    if result.get("status_filter") and result["status_filter"] != "all":
                        sf = result["status_filter"]
                        urls = result.get("filtered_urls", [])
                        out_lines.append(f"\nFiltered by status: {sf} ({len(urls)} matching)")
                        for u in urls:
                            out_lines.append(f"  - {u}")
                    print("\n".join(out_lines))
                elif fmt == "markdown":
                    md_path = args.out / "comparison.md"
                    if md_path.exists():
                        print(md_path.read_text(encoding="utf-8").strip())
                    else:
                        print(json.dumps(result, ensure_ascii=False, indent=2))
                elif fmt == "csv":
                    csv_path = args.out / "comparison.csv"
                    if csv_path.exists():
                        print(csv_path.read_text(encoding="utf-8").strip())
                    else:
                        print("url,state,field,before,after")
                else:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0
            elif args.command == "aeo":
                from .aeo import analyze_snapshot

                out_dir = args.out or (args.snapshot / "aeo")
                res = analyze_snapshot(args.snapshot, visibility_file=args.visibility, out_dir=out_dir)

                fmt = getattr(args, "format", "terminal")
                if fmt == "terminal":
                    print(f"AevoraSEO AEO Intelligence Engine — Snapshot: {res.snapshot_id}")
                    print(f"Pages Analyzed: {res.page_count}")
                    print(f"AevoraSEO AEO Readiness Score: {res.average_aeo_readiness_score:.1f} / 100")
                    print(f"AevoraSEO GEO Signal Score:    {res.average_geo_signal_score:.1f} / 100")
                    print("\nAI Crawler Accessibility:")
                    for bot, counts in sorted(res.bot_accessibility_matrix.items()):
                        allowed = counts.get("crawl_allowed", 0)
                        restricted = counts.get("crawl_restricted", 0)
                        print(f"  - {bot:20} Allowed: {allowed} | Restricted: {restricted}")
                    if res.top_questions:
                        print(f"\nTop Detected Questions ({len(res.top_questions)}):")
                        for q in res.top_questions[:5]:
                            ans_mark = "✅" if q.get("answer_detected") else "❌"
                            print(f"  {ans_mark} {q.get('question')} ({q.get('confidence', 0):.2f} conf)")
                    if res.content_conflicts:
                        print(f"\nContent Conflicts ({len(res.content_conflicts)}):")
                        for c in res.content_conflicts:
                            print(f"  - {c.get('type')}: {c.get('message')}")
                    print(f"\nFull reports saved to: {out_dir}")
                elif fmt == "markdown":
                    print(res.summary_markdown)
                elif fmt == "csv":
                    csv_file = out_dir / "aeo_pages.csv"
                    if csv_file.exists():
                        print(csv_file.read_text(encoding="utf-8-sig").strip())
                    else:
                        print("url,aeo_readiness_score,geo_signal_score")
                elif fmt == "json":
                    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))
                return 0
            elif args.command == "aeo-compare":
                from .aeo import compare_aeo_snapshots, generate_aeo_diff_markdown

                out_dir = args.out or (args.after / "aeo_compare")
                diff = compare_aeo_snapshots(args.before, args.after, out_dir=out_dir)

                fmt = getattr(args, "format", "terminal")
                if fmt == "terminal":
                    print("AevoraSEO AEO / GEO Snapshot Comparison")
                    print(
                        f"Before: {diff.before_snapshot_id} (AEO: {diff.before_avg_aeo:.1f}, GEO: {diff.before_avg_geo:.1f})"
                    )
                    print(
                        f"After:  {diff.after_snapshot_id} (AEO: {diff.after_avg_aeo:.1f}, GEO: {diff.after_avg_geo:.1f})"
                    )
                    print(f"Deltas: AEO {diff.aeo_delta:+.1f} | GEO {diff.geo_delta:+.1f}")
                    print(
                        f"Summary: Added {diff.summary.get('added', 0)}, Removed {diff.summary.get('removed', 0)}, "
                        f"Improved {diff.summary.get('improved', 0)}, Regressed {diff.summary.get('regressed', 0)}, "
                        f"Unchanged {diff.summary.get('unchanged', 0)}"
                    )
                    print("\nPage Changes:")
                    for it in diff.items[:10]:
                        ev = "; ".join(it.evidence) if it.evidence else "Stable"
                        print(
                            f"  [{it.state}] {it.url} ({it.metric}: {it.before:.1f} -> {it.after:.1f}, {it.delta:+.1f}) — {ev}"
                        )
                    print(f"\nDiff outputs saved to: {out_dir}")
                elif fmt == "markdown":
                    print(generate_aeo_diff_markdown(diff))
                elif fmt == "csv":
                    csv_file = out_dir / "aeo_comparison.csv"
                    if csv_file.exists():
                        print(csv_file.read_text(encoding="utf-8-sig").strip())
                    else:
                        print("url,metric,before,after,delta,state,evidence")
                elif fmt == "json":
                    print(json.dumps(diff.to_dict(), ensure_ascii=False, indent=2))
                return 0
            elif args.command == "backlinks":
                from .backlinks import check_sources

                result = check_sources(
                    args.sources,
                    args.target,
                    args.out,
                    args.max_sources,
                    args.mode,
                    args.allow_private,
                    not args.no_follow_redirects,
                    args.brand,
                    args.alias,
                )
            elif args.command == "search-plan":
                from .reputation import search_plan

                result = search_plan(args.target, args.brand, args.out, args.pages)
            elif args.command == "search-import":
                from .reputation import import_search_html

                result = import_search_html(
                    args.html, args.target, args.query, args.captured_at, args.out, args.engine
                )
            elif args.command == "reputation":
                from .reputation import reputation

                result = reputation(
                    args.sources,
                    args.target,
                    args.brand,
                    args.out,
                    args.max_sources,
                    args.mode,
                    args.allow_private,
                    args.alias,
                    args.related_host,
                    args.search_pages,
                    args.evidence,
                )
            else:
                from .publishing import apply_change, open_store, stage

                store = open_store(args.site, args.connection)
                try:
                    result = (
                        stage(store, args.file, args.replacement, args.out)
                        if args.action == "plan"
                        else apply_change(
                            store, args.plan, args.expect_plan, args.action == "rollback"
                        )
                    )
                finally:
                    store.close()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "report":
            import sqlite3

            if not (args.out / "crawl.sqlite3").exists():
                raise ValueError("No crawl database in that directory.")
            with sqlite3.connect(str(args.out / "crawl.sqlite3")) as db:
                row = db.execute("SELECT value FROM meta WHERE key='config'").fetchone()
            if not row:
                raise ValueError("Missing crawl configuration")
            saved = json.loads(row[0])
            config = Config(**saved["config"])
            selectors = saved["selectors"]
        else:
            if args.command == "scrape":
                args.max_pages = 1
                args.no_sitemaps = True
            from .network import CRAWL_PROFILES

            profile_name = getattr(args, "profile", "standard")
            preset = CRAWL_PROFILES.get(profile_name, CRAWL_PROFILES["standard"])

            max_pages = (
                args.max_pages
                if args.max_pages is not None
                else (1 if args.command == "scrape" else preset["max_pages"])
            )
            max_depth = args.max_depth if args.max_depth is not None else preset["max_depth"]
            workers = args.workers if args.workers is not None else preset["workers"]
            delay = args.delay if args.delay is not None else preset["delay"]
            timeout = args.timeout if args.timeout is not None else preset["timeout"]
            retries = args.retries if args.retries is not None else preset["retries"]
            render_mode = args.mode if args.mode is not None else preset["render_mode"]
            scroll_steps = (
                args.scroll_steps
                if args.scroll_steps is not None
                else preset.get("scroll_steps", 3)
            )
            render_settle_ms = (
                args.render_settle_ms
                if args.render_settle_ms is not None
                else preset.get("render_settle_ms", 1500)
            )

            config = Config(
                url=args.url,
                profile=profile_name,
                max_pages=max_pages,
                max_depth=max_depth,
                workers=workers,
                delay=delay,
                timeout=timeout,
                retries=retries,
                max_bytes=args.max_bytes,
                max_discovered=args.max_discovered,
                max_sitemaps=args.max_sitemaps,
                max_query_variants=args.max_query_variants,
                allow_hosts=args.allow_host,
                include_www=args.include_www,
                exclude=args.exclude,
                allow_private=args.allow_private,
                sitemaps=not args.no_sitemaps,
                drop_tracking=not args.keep_tracking,
                save_html=not args.no_html,
                render=args.render or args.screenshot,
                render_wait_ms=args.render_wait_ms,
                render_max_requests=args.render_max_requests,
                render_allow_hosts=args.render_allow_host,
                render_mode=render_mode,
                robots_policy=args.robots,
                render_asset_policy=args.browser_assets,
                wait_for_selector=args.wait_for_selector,
                render_settle_ms=render_settle_ms,
                scroll_steps=scroll_steps,
                screenshot=args.screenshot,
                headless=not args.headed,
            )
            selectors = json.loads(args.selectors.read_text()) if args.selectors else {}
            from bs4 import BeautifulSoup

            if not isinstance(selectors, dict):
                raise ValueError("Selectors must be a JSON object.")
            for spec in selectors.values():
                if not isinstance(spec, (str, dict)):
                    raise ValueError("Each selector must be a string or object.")
                try:
                    BeautifulSoup("", "html.parser").select(
                        spec if isinstance(spec, str) else spec["selector"]
                    )
                except Exception as e:
                    raise ValueError("Invalid selector: " + str(e)) from e
            if config.wait_for_selector:
                try:
                    BeautifulSoup("", "html.parser").select(config.wait_for_selector)
                except Exception as e:
                    raise ValueError("Invalid wait selector: " + str(e)) from e
        with OutputLock(args.out):
            if args.command == "watch":
                from .monitor import watch

                if args.resume:
                    raise ValueError(
                        "Watch needs a fresh series; resume an individual crawl with crawl --resume."
                    )
                result = watch(
                    config, args.out, args.cycles, args.interval, args.quiet, selectors=selectors
                )
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0 if result["status"] == "completed" else 1
            crawler = Crawler(
                config,
                args.out,
                resume=args.command == "report" or args.resume,
                selectors=selectors,
                incremental_from=getattr(args, "incremental", None),
            )
            if args.command != "report":
                if args.quiet:
                    crawler.log = lambda _: None
                elif sys.stderr.isatty() and not args.no_color and os.getenv("NO_COLOR") is None:
                    try:
                        from colorama import Fore, Style, just_fix_windows_console

                        just_fix_windows_console()

                        def log(msg):
                            status = int(msg.split("] ", 1)[1].split(" ", 1)[0])
                            color = (
                                Fore.RED
                                if " — " in msg or status >= 400
                                else Fore.YELLOW
                                if status >= 300
                                else Fore.GREEN
                            )
                            print(color + msg + Style.RESET_ALL, file=sys.stderr, flush=True)

                        crawler.log = log
                    except ImportError:
                        pass
                summary = crawler.run()
            else:
                summary = crawler.export()
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            # Distinguish wholly unsuccessful runs from useful partial results.
            return 0 if summary["html_documents"] else 1
    except (ValueError, OSError, KeyError, TypeError) as e:
        print("Error: " + str(e), file=sys.stderr)
        return 2
    finally:
        if crawler:
            crawler.close()


if __name__ == "__main__":
    sys.exit(main())
