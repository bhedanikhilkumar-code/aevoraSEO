"""Command wiring for discovery and evidence-based research."""

from pathlib import Path


def add_commands(sub):
    p = sub.add_parser(
        "research-plan", help="Plan browser-first deep research and equal cohort budgets."
    )
    p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--brand")
    p.add_argument("--selection", type=Path)
    p.add_argument("--source-limit", type=int, default=30)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser(
        "compare-reputation", help="Compare reputation snapshots across time or cohort manifest."
    )
    p.add_argument("--before", type=Path, default=None, help="Initial reputation snapshot folder or JSON.")
    p.add_argument("--after", type=Path, default=None, help="Subsequent reputation snapshot folder or JSON.")
    p.add_argument("--manifest", type=Path, default=None, help="Cohort research manifest for multi-site ranking.")
    p.add_argument("--out", type=Path, default=None, help="Output directory for comparison results.")
    p.add_argument(
        "--format",
        choices=["terminal", "json", "csv", "markdown"],
        default="terminal",
        help="Output presentation format.",
    )
    p = sub.add_parser("discover", help="Collect unverified search leads with bounded fallbacks.")
    p.add_argument("--query", action="append", default=[])
    p.add_argument(
        "--queries", type=Path, help="JSON query specifications from profile or a reviewed plan."
    )
    p.add_argument("--market")
    p.add_argument("--language")
    p.add_argument("--target", default="")
    p.add_argument("--provider", action="append", choices=["duckduckgo-html", "bing-rss"])
    p.add_argument("--host-results", type=Path)
    p.add_argument(
        "--saved-search",
        type=Path,
        help="JSON list of saved HTML path/provider/query/captured_at records.",
    )
    p.add_argument("--candidate", action="append", default=[])
    p.add_argument("--sources-csv", type=Path)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--max-requests", type=int, default=16)
    p.add_argument("--max-queries", type=int, default=8)
    p.add_argument("--max-candidates", type=int, default=100)
    p.add_argument("--timeout", type=float, default=12)
    p.add_argument("--seconds", type=float, default=90)
    p.add_argument("--cache", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("profile", help="Prepare evidence or validate a reviewed business profile.")
    p.add_argument("--crawl", type=Path, required=True)
    p.add_argument("--brief", type=Path)
    p.add_argument("--review", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("competitors", help="Select comparable businesses from verified profiles.")
    p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--candidate-profile", type=Path, action="append", required=True)
    p.add_argument("--discovery", type=Path)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser(
        "audit", help="Create actionable findings from a crawl; search failure is nonfatal."
    )
    p.add_argument("--crawl", type=Path, required=True)
    p.add_argument("--profile", type=Path)
    p.add_argument("--discovery", type=Path)
    p.add_argument("--discover-queries", type=Path)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--reviewed-findings", type=Path)
    p.add_argument("--out", type=Path, required=True)


def execute(args):
    from .backlinks import source_rows
    from .discovery import PROVIDERS, discover, host_attempts
    from .findings import audit_report
    from .research import profile, select_competitors
    from .review import read_json

    if args.command == "research-plan":
        from .deep_research import research_plan

        return research_plan(
            read_json(args.profile),
            args.out,
            args.brand,
            read_json(args.selection) if args.selection else None,
            args.source_limit,
        )
    if args.command == "compare-reputation":
        if args.manifest:
            from .deep_research import comparison_from_manifest

            return comparison_from_manifest(args.manifest, args.out)
        elif args.before and args.after:
            from .reputation_comparison import compare_reputation_snapshots, generate_reputation_diff_markdown

            out_dir = args.out or (args.after if args.after.is_dir() else args.after.parent) / "reputation_compare"
            diff = compare_reputation_snapshots(args.before, args.after, out_dir=out_dir)
            fmt = getattr(args, "format", "terminal")
            if fmt == "terminal":
                s = diff["summary"]
                delta_str = f"{s['score_delta']:+.1f}" if s["score_delta"] is not None else "N/A"
                print("AevoraSEO Reputation Snapshot Comparison")
                print(f"Target: {diff['target']}")
                print(f"Score Delta: {delta_str} (Before: {s['before_score']}, After: {s['after_score']})")
                print(f"Backlinks: +{s['new_backlinks_count']} new, -{s['lost_backlinks_count']} lost, {s['retained_backlinks_count']} retained")
                print(f"Brand Mentions: +{s['new_mentions_count']} new, -{s['lost_mentions_count']} lost, {s['retained_mentions_count']} retained")
                print(f"Converted Opportunities: {s['opportunity_conversions_count']}")
                if diff["opportunity_conversions"]:
                    print("\nConverted Opportunities:")
                    for c in diff["opportunity_conversions"]:
                        print(f"  🎯 {c['source_url']} -> {c['target_url']}")
                print(f"\nDiff saved to: {out_dir}")
                return diff
            elif fmt == "markdown":
                print(generate_reputation_diff_markdown(diff))
                return diff
            elif fmt == "csv":
                csv_file = out_dir / "reputation_comparison.csv"
                if csv_file.exists():
                    print(csv_file.read_text(encoding="utf-8-sig").strip())
                else:
                    print("change_type,source_url,target_url,anchor,rel,note")
                return diff
            elif fmt == "json":
                return diff
        else:
            raise ValueError("Provide either --manifest for cohort comparison, or --before and --after for snapshot comparison.")
    if args.command == "discover":
        queries = read_json(args.queries) if args.queries else []
        queries += [
            {"query": q, "market": args.market, "language": args.language} for q in args.query
        ]
        candidates = args.candidate + (source_rows(args.sources_csv) if args.sources_csv else [])
        return discover(
            queries,
            args.out,
            args.target,
            args.provider or PROVIDERS,
            host_attempts(args.host_results) if args.host_results else [],
            candidates,
            read_json(args.saved_search) if args.saved_search else [],
            args.offline,
            args.max_requests,
            args.max_queries,
            args.max_candidates,
            args.timeout,
            args.seconds,
            args.cache,
        )
    if args.command == "profile":
        return profile(
            args.crawl,
            args.out,
            read_json(args.brief) if args.brief else None,
            read_json(args.review) if args.review else None,
        )
    if args.command == "competitors":
        return select_competitors(
            read_json(args.profile),
            [read_json(p) for p in args.candidate_profile],
            args.out,
            args.limit,
            read_json(args.discovery) if args.discovery else None,
        )
    found = read_json(args.discovery) if args.discovery else None
    if args.discover_queries:
        found = discover(
            read_json(args.discover_queries), args.out / "discovery", offline=args.offline
        )
    return audit_report(
        args.crawl,
        args.out,
        read_json(args.profile) if args.profile else None,
        found,
        read_json(args.reviewed_findings) if args.reviewed_findings else [],
    )
