# Changelog

## 1.0.0 — Production Release (2026-09-22)

AevoraSEO 1.0.0 represents the complete, production-ready release of the evidence-first SEO, AEO, GEO, Entity, Authority, Reputation, Search/Commercial, and Content Optimization intelligence engine.

### Complete 10-Phase Capabilities
- **Phase A — Core Engine Reconciliation**: Native Python 3.12+ engine restored, hybrid Node runner, standardized 1.0.0 package metadata, automated release hygiene, and cross-platform CLI parity.
- **Phase B — Crawler Hardening & Incremental Intelligence**: Quick/standard/deep crawl profiles, persistent SQLite snapshots, conditional ETag/304 extraction reuse, snapshot diff engine, SSRF defenses, and cache isolation.
- **Phase C — AEO/GEO Intelligence Engine**: Direct answer proximity detection (10–60w definitions, structured lists), question/intent coverage, Schema.org audits, AI crawler access matrix (10 bots), transparent scoring (0–100), and `aeo-compare` temporal diffing.
- **Phase D — Backlink & Reputation Intelligence**: Conclusive target link matching, anchor text extraction, sentence context excerpts, source classification (`editorial`, `directory`, `profile`, `community`, `owned`), strict ownership boundary, Model 1.1 reputation scoring, 206-site opportunity catalog, and `reputation-compare`.
- **Phase E — Entity, Authority & Knowledge Intelligence**: Multi-source entity extraction (JSON-LD, Microdata, OpenGraph), typed models (`Organization`, `Person`, etc.), `sameAs` authority footprint across 10+ registries, cross-page entity consistency auditing, directed knowledge graph builder with graph metrics, Entity & Authority Score (0–100), and `entity-compare`.
- **Phase F — Search, Local & Commercial Intelligence**: Search intent taxonomy (Informational, Commercial, Transactional, Navigational, Local), deterministic query extraction, cannibalization detection, local search visibility (NAP, maps, click-to-call), commercial CTA and conversion friction, buyer decision support matrices, Search & Commercial Visibility Score (0–100), and `search-compare`.
- **Phase G — Content & Optimization Intelligence**: Title and meta description optimization, heading hierarchy and single H1 audits, direct answer and definition opportunity detection (40–60 words), FAQ objection handling, topic cluster pillar-spoke mapping, internal link graph auditing, intent-matched schema recommendations, grounded content briefs and editorial outlines, content gap/refresh prioritization, 30/60/90-day roadmaps, Content Optimization Score (0–100), and `optimize-compare`.
- **Phase H — Multi-Agent & Platform Compatibility**: Empirical platform registry cataloging 18 target environments (Agent, Claude Code, Codex, Hermes, OpenClaw, aider, Copilot CLI, Gemini CLI, Factory Droid, Kilocode CLI, OpenCode CLI, Qwen, JCODE, jcode CLI, juni CLI, Kiro, prime-agent, cai), runtime environment detection, profile validation, platform adapter generation, fixture verification, and `aevoraseo agent` CLI.
- **Phase I — Reporting, Operations & Professional Workflow**: Unified cross-subsystem report generator synthesizing all intelligence dimensions into executive HTML, terminal, markdown, JSON, and CSV reports, calibrated overall scorecard (0–100), P0/P1/P2 issue prioritization with acceptance criteria, audit verification (`audit-verify`), multi-snapshot progress tracking (`progress`), and SQLite database integrity diagnostics.
- **Phase J — Production Hardening & Security**: Dual-check formula injection defense across all CSV exports, XML sitemap null-byte sanitization, deterministic SQLite connection lifecycle (`try/finally conn.close()`) for Windows lock safety, multi-snapshot scaling, zero stub policy compliance, and strictly validated hosted skill package ceiling ($\le 200$ archive files).

## Phase J — Production Hardening & Release

- Conducted adversarial penetration audit across all subsystems, reinforcing SSRF defenses, scheme blocking, private IP detection, and XXE XML injection safeguards.
- Hardened CSV export routines across all subsystems (`engine`, `unified_report`, `review`, `aeo`, `entity`, `search`, `optimization`, `reputation`, `backlinks`) with dual-check formula injection defenses (`=`, `+`, `-`, `@`, `\t`, `\r`, and leading whitespace formula traps).
- Fixed XML sitemap parsing in `engine.parse_sitemap` to ensure sanitized null-byte stripped buffers are passed to XML element trees.
- Audited SQLite connection lifecycle across all operational and persistence modules, guaranteeing immediate file unlock on Windows with `try/finally conn.close()`.
- Verified multi-snapshot progress calculation scalability across multi-snapshot histories without unbounded memory growth.
- Conducted zero stub policy audit across `src/` and `scripts/`, confirming 0 instances of `TODO`, `FIXME`, or `NotImplementedError`.
- Validated hosted skill upload package ceiling compliance: 197 files, 198 archive files strictly within the $\le 200$ ceiling (`validate_skill.py`).
- Release hygiene verified with 0 findings across 268 files (`check_release.py`).
- Implemented comprehensive production hardening test suite in `tests/test_production_hardening.py` (34 new tests, 526 tests passing across the suite).

## Phase I — Reporting, Operations & Professional Workflow

- Implemented unified cross-subsystem report generator (`aevoraseo.unified_report`) synthesizing Technical, Content, AEO, GEO, Entity, Authority, Reputation, and Search/Commercial intelligence.
- Added deterministic health scorecard aggregating subsystem metrics and calculating calibrated overall score (0–100).
- Implemented multi-format client report exports (`terminal`, `html`, `markdown`, `json`, `csv`) with styled responsive executive HTML presentation.
- Added strict P0 (Critical Blocker), P1 (High Impact Opportunity), and P2 (Optimization Routine) issue prioritization with actionable impact, remediation steps, and verification criteria.
- Implemented formula injection protection across all exported CSV files (`audit-issues.csv`, `audit-scorecard.csv`) with `sanitize_csv_cell`.
- Built operational acceptance verification engine (`aevoraseo.workflow.verify_audit_acceptance`) verifying whether prior audit issues are resolved or persist in subsequent crawl snapshots.
- Added chronological progress tracking (`aevoraseo.workflow.track_progress`) analyzing score deltas and trajectory (`IMPROVING`, `DECLINING`, `STABLE`) across multi-snapshot crawl histories.
- Implemented operational database diagnostics (`aevoraseo.workflow.run_operational_diagnostics`) executing `PRAGMA integrity_check` on all workspace SQLite databases and reporting runtime health.
- Added CLI parity for `aevoraseo report`, `aevoraseo audit-verify`, and `aevoraseo progress` across terminal, JSON, Markdown, and CSV formats.
- Maintained Node launcher parity in `bin/aevoraseo.js` with synchronized command routing and help text.
- Authored technical methodology reference in `references/reporting-operations.md`.
- Added comprehensive unit and CLI integration test suites in `tests/test_unified_report.py` and `tests/test_operational_workflow.py` (15 new tests, 492 tests passing across the suite).

## Phase H — Multi-Agent & Platform Compatibility Engine

- Implemented native Multi-Agent & Platform Compatibility subsystem (`aevoraseo.compatibility`).
- Built platform registry cataloging 18 target AI agent and CLI coding environments: Agent (ChatGPT Work), Claude Code, Codex, Hermes Agent, OpenClaw, aider, Copilot CLI, Gemini CLI, Factory Droid, Kilocode CLI, OpenCode CLI, Qwen, JCODE, jcode CLI, juni CLI, Kiro, prime-agent, and cai.
- Defined empirical platform integration tiers: First-party skill, Project instruction, CLI integration, and Generic adapter.
- Implemented environment detector (`detect_environment`) discovering active platforms and workspaces via environment variables, workspace marker files, and global user config directories.
- Built profile and workspace validator (`validate_installation`, `validate_workspace_isolation`, `check_python_compatibility`) verifying receipt integrity, SHA-256 checksums, and strict boundary isolation.
- Created platform adapter generator (`generate_adapter`) emitting deterministic configuration files (`.aider.conf.yml`, `.github/copilot-instructions.md`, `GEMINI.md`) with safe `--dry-run` and collision guards.
- Implemented fixture-based compatibility verifier (`verify_platform`, `verify_all_platforms`) executing simulated workspace tests without mutating real host configurations.
- Added CLI parity via `aevoraseo agent` (with actions: `detect`, `list`, `inspect`, `adapt`, `verify`) across `terminal`, `json`, and `markdown` output formats.
- Synchronized Node launcher (`bin/aevoraseo.js`) with `agent` command routing and help text.
- Expanded `scripts/install_skill.py` to support all 18 platform destinations under `--host`.
- Authored comprehensive technical reference in `references/multi-agent-compatibility.md` with evidence-based status definitions (`VERIFIED`, `PARTIAL`, `DOCUMENTED`, `NOT VERIFIED`, `UNSUPPORTED`).
- Consolidated 8 unreferenced core and competitor playbooks, maintaining hosted skill bundle strictly below upload ceiling (198 bundle files, 199 archive files $\le 200$ limit).
- Built comprehensive unit, detector, validator, adapter, verifier, and CLI test suites (23 new tests, 477 tests passing across the suite).

## Phase G — Content & Optimization Intelligence Engine

- Implemented native Content & Optimization Intelligence subsystem (`aevoraseo.optimization`).
- Built title tag optimization analyzing character lengths (45–65 chars optimal), trailing/leading brand placement, primary query alignment, and repetitive keyword stuffing.
- Added meta description optimization auditing character limits (120–160 chars optimal), actionable CTA verb detection (`discover`, `explore`, `book`, `call`, `learn`), and query relevance.
- Implemented heading structure audits verifying single H1 presence, logical consecutive nesting, skipped-level detection (e.g. H1 -> H3, H2 -> H4), question headings, and empty heading cleanup.
- Built direct-answer and definition opportunity engine detecting definition phrases (`is a`, `refers to`, `is defined as`) and prescribing 40–60 word answer boxes, procedural lists, and comparison tables.
- Added FAQ and buyer objection opportunity engine discovering pricing transparency, guarantee/SLA, and customer support friction gaps on transactional pages.
- Built site-wide internal link graph auditing in-degree and out-degree, detecting orphan pages (0 incoming internal links), crawl depth, and generic anchor warnings (`click here`, `read more`).
- Implemented topic cluster and pillar-spoke analysis grouping pages by path and topic, mapping pillar hubs to supporting spokes, and calculating cluster health scores (0–100).
- Built intent-matched schema recommendation engine mapping pages to `Article`, `Service`, `Product`, `LocalBusiness`, `FAQPage`, `Course`, and `HowTo` schemas.
- Added grounded content brief generator synthesizing target queries, intent-scaled target word counts, required sections, direct answer targets, internal links, and editorial guidance.
- Implemented editorial outline generator producing structured heading blueprints with 40–60 word answer box targets, bullet points, FAQ blueprints, and CTA placement.
- Built content gap and refresh candidate prioritization detecting thin content (< 250w, < 500w), aging year references ($\le 2023$), and missing comparison/FAQ pages.
- Synthesized prioritized 30/60/90-day optimization roadmaps across Foundation (Days 1–30), Answer Depth & Schema (Days 31–60), and Cluster Compounding (Days 61–90).
- Added deterministic **AevoraSEO Content Optimization Score (0–100)** across four 25-point dimensions: Metadata & Heading Architecture, Content Quality & Answer Depth, Topic Cluster & Internal Link Health, and Structured Data & Schema Coverage.
- Implemented SQLite persistence in `content_optimization.sqlite3` (`optimization_snapshots`, `optimization_page_audits`, `optimization_answer_opportunities`, `optimization_topic_clusters`, `optimization_content_briefs`, `optimization_diffs`) with Windows-safe connection cleanup (`try/finally conn.close()`).
- Built temporal snapshot comparison engine (`compare_optimization_snapshots`, `aevoraseo optimize-compare`) calculating score deltas, resolved deficiencies, new regressions, and cluster evolution.
- Added CLI parity: `aevoraseo optimize <target>` (alias `aevoraseo content`) and `aevoraseo optimize-compare` across terminal, markdown, JSON, and CSV formats.
- Maintained Node launcher parity in `bin/aevoraseo.js`.
- Security hardening: sanitized all exported CSV files (`content-recommendations.csv`, `content-briefs.csv`, `direct-answers.csv`, `internal-links.csv`) against spreadsheet formula injection attacks.
- Consolidated unreferenced single-topic playbooks (`growth-plans.md`, `growth-models.md`, `competitor-research-workflow.md`, `site-audit-workflow.md`, `backlink-evaluation.md`), maintaining hosted skill bundle file count strictly below ceiling (197 bundle files, 198 archive files $\le 200$ limit).
- Added comprehensive unit, metadata, answer, cluster, brief, persistence, comparison, and CLI test suites (20 new tests, 454 tests passing across the suite).

## Phase F — Search, Local & Commercial Intelligence Engine

- Implemented native Search, Local & Commercial Intelligence subsystem (`aevoraseo.search`).
- Built search intent taxonomy classifying pages into Informational, Commercial Investigation, Transactional, Navigational, and Local intents.
- Added deterministic target query extraction identifying 2-to-5 word primary queries and secondary candidate phrases from H1, Title, meta description, and URL slugs.
- Implemented keyword cannibalization detector using Jaccard token similarity to identify internal page competition, assigning High/Medium/Low risk levels and actionable remediation.
- Built local search visibility auditor validating Schema.org `LocalBusiness` and specialized sub-types (`Dentist`, `Store`, etc.), verifying uniform NAP consistency, clickable telephone links (`<a href="tel:...">`), Google Maps embeds, and service-area declarations.
- Implemented commercial conversion journey and CTA friction engine classifying high-intent action buttons vs generic links, checking trust proof proximity (reviews, doctor/expert credentials, guarantees), and auditing form field friction.
- Added comparison and buyer decision support auditing head-to-head comparison pages, structured feature matrices (`<table>`), evaluated alternatives, and objection-handling buyer FAQs.
- Added deterministic **AevoraSEO Search & Commercial Visibility Score (0–100)** across four 25-point dimensions: Intent & Query Targeting, Commercial Journey & CTAs, Local Visibility Signals, and Comparison & Buyer Decisions.
- Implemented SQLite persistence across `search_commercial.sqlite3` (`search_snapshots`, `search_page_intents`, `search_cannibalization`, `search_local_signals`, `search_commercial_audits`, `search_diffs`) with Windows-safe connection cleanup (`try/finally conn.close()`).
- Built temporal snapshot diff engine (`compare_search_snapshots`, `aevoraseo search-compare`) calculating score deltas, intent shifts, resolved/new cannibalizations, and commercial improvements.
- Added CLI commands: `aevoraseo search <target>`, `aevoraseo commercial <target>`, and `aevoraseo search-compare` with multi-format presentation (`terminal`, `json`, `csv`, `markdown`).
- Security hardening: sanitized all exported CSV files (`page-intents.csv`, `cannibalization.csv`, `commercial-friction.csv`, `search_comparison.csv`) against spreadsheet formula injection attacks.
- Consolidated unreferenced templates and keyword research playbooks into indexed README files, maintaining hosted skill bundle file count strictly below the ceiling (194 files, 195 archive files <= 200 limit).
- Added comprehensive unit, intent, cannibalization, local, commercial, comparison, adversarial, and CLI test suites (22 new tests, 434 tests passing across the suite).

## Phase E — Entity, Authority & Knowledge Intelligence Engine

- Implemented native Entity, Authority & Knowledge Intelligence subsystem (`aevoraseo.entity`).
- Added multi-source entity extraction parsing Schema.org JSON-LD, Microdata, OpenGraph, and meta tags with recursive cycle guards (`max_depth=25`).
- Supported rich typed entity models: `Organization`, `Person`, `Product`, `Service`, `Place`, `LocalBusiness`, and `Article` with attribute mapping.
- Built `sameAs` authority discovery classifying external profiles across Wikidata, Wikipedia, LinkedIn, Crunchbase, GitHub, ORCID, Google Business, Trustpilot, etc., and identifying missing standard corporate profiles.
- Implemented cross-page entity consistency auditor detecting organization name contradictions, NAP (Name, Address, Phone) mismatches, broken sameAs URLs, and missing core entity pages (`/about`, `/team`, `/contact`, `/reviews`).
- Built directed knowledge graph builder (`EntityKnowledgeGraph`) computing graph topology metrics (degree centrality, density, central entity) and exporting standard D3/Cytoscape format (`entity-graph.json`).
- Added deterministic **AevoraSEO Entity & Authority Score (0–100)** evaluated across four 25-point dimensions: Identity Completeness, Entity Consistency & Integrity, SameAs & Authority Footprint, and Topical/Expert Depth.
- Implemented SQLite persistence across `entities.sqlite3` (`entity_snapshots`, `entity_nodes`, `entity_edges`, `entity_same_as`, `entity_conflicts`, `entity_diffs`) with Windows-safe connection cleanup (`try/finally conn.close()`).
- Built temporal entity diff engine (`compare_entity_snapshots`, `aevoraseo entity-compare`) tracking added/removed/modified entities, resolved/new conflicts, added/lost sameAs profiles, and score deltas.
- Added CLI commands: `aevoraseo entity <target>` and `aevoraseo entity-compare` with multi-format presentation (`terminal`, `json`, `csv`, `markdown`).
- Security hardening: sanitized all exported CSV files (`entities.csv`, `entity-conflicts.csv`) against spreadsheet formula injection attacks.
- Consolidated unreferenced supporting playbooks into indexed README resources to comply with hosted skill bundle upload boundaries (196 files <= 200 limit).
- Added comprehensive unit, consistency, graph, comparison, adversarial, and CLI test suites (18 new tests, 412 tests passing across the suite).

## Phase D — Backlink & Reputation Intelligence Engine

- Implemented native backlink discovery and verification subsystem (`aevoraseo.backlinks` & `aevoraseo.backlink_persistence`).
- Added granular link attribute extraction: normalized anchor text, tokenized `rel` attributes, conclusive `dofollow` classification, target URL path resolution, and 160-char sentence context excerpts.
- Built automated source page classification (`editorial`, `directory`, `profile`, `community`, `owned`) based on structural URL and domain heuristics.
- Enforced strict ownership boundaries: target domain, subdomains, and `--related-host` flags are classified as owned and excluded from independent proof.
- Implemented SQLite persistence for backlink verification and reputation assessments across `backlinks.sqlite3` (`backlink_snapshots`, `backlink_sources`, `backlink_links`, `backlink_mentions`) and `reputation.sqlite3` (`reputation_assessments`, `reputation_diffs`).
- Integrated backlink opportunity pipeline cross-referencing candidate referring domains and unreached leads against the embedded 206-site catalog (`posting-sites.json`), outputting actionable recommendations (`reputation-opportunities.json`, `reputation-opportunities.csv`).
- Built snapshot-aware temporal diff engine (`aevoraseo.reputation_comparison`, `aevoraseo reputation-compare`) calculating score deltas, added/lost/retained links, added/lost/retained mentions, and converted opportunities.
- Added new CLI commands and arguments: `aevoraseo backlinks <target>`, `aevoraseo reputation <target>`, `aevoraseo reputation-compare --before <file> --after <file>` with format support (`--format {terminal,json,csv,markdown}`).
- Security hardening: sanitized all exported CSV files (`reputation-sources.csv`, `reputation-opportunities.csv`, `backlink-links.csv`) against spreadsheet formula injection attacks.
- Added comprehensive unit, intelligence, adversarial, and CLI test suites (22 new tests, 394 tests passing across the suite).

## Phase C — AEO & GEO Intelligence Engine

- Implemented native Answer Engine Optimization (AEO) and Generative Engine Optimization (GEO) analytical engines.
- Added deterministic **AevoraSEO AEO Readiness Score (0–100)** across 5 dimensions: Answer Readiness, Question Coverage, Content Structure, Schema Quality, and AI Crawler Accessibility.
- Added deterministic **AevoraSEO GEO Signal Score (0–100)** across 4 dimensions: Entity Clarity, Source Readiness, Factual Specificity & Density, and Content Depth & Extractability.
- Implemented direct-answer proximity detection, concise definition phrasing analysis, and structured FAQ extraction.
- Built tracked AI bot accessibility matrix auditing 10 major AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, etc.) across robots.txt, robots meta, and X-Robots-Tag.
- Implemented structured Schema.org audit for completeness, syntax validity, and page-title/canonical URL consistency.
- Built cross-page entity conflict detector flagging contradictions in Organization and Person entities.
- Implemented full SQLite persistence across `crawl.sqlite3` and standalone `aeo.sqlite3` (`aeo_snapshots`, `aeo_pages`, `aeo_questions`, `aeo_entities`, and `aeo_diffs`).
- Implemented snapshot comparison CLI command (`aevoraseo aeo-compare`) with categorized state transitions (ADDED, REMOVED, IMPROVED, REGRESSED, UNCHANGED) and attributed contributing evidence.
- Hardened CSV exports against formula injection attacks with single-quote escaping on untrusted strings.
- Added recursion depth and identity cycle guards preventing stack overflow on circular JSON-LD markup.
- Added comprehensive adversarial and security test suite (`tests/test_aeo_adversarial.py`).
- Added technical methodology documentation (`references/aeo-geo.md`).

## 1.0.0 — AevoraSEO launch

- Renamed the project, Python distribution, CLI entry point and import package to `aevoraseo`.
- Replaced legacy project branding in documentation, metadata, examples and tests.
- Replaced the legacy logo/banner assets with the AevoraSEO identity.
- Removed the previous creator's personal details from project metadata and documentation.
- Updated maintainer metadata to Bheda Nikhilkumar.
- Added a deeper README covering architecture, evidence model, capabilities, security boundaries, development and roadmap.
- Set the package version to 1.0.0 for the official initial launch of AevoraSEO.

2.7.1

- Fixed the hosted skill upload exceeding the observed 200-file limit. Consolidated reporting and industry references into indexed resources while preserving their full guidance; native code, catalog, templates and report assets remain bundled.
- Count the installation receipt when validating upload size and reject oversized packages before creating an archive.
- Added a regression for the exact 200/201-file upload boundary and verified that rejected packages leave no incomplete archive behind.
- Updated direct-upload steps for Claude Desktop and ChatGPT Work, plus specific guidance for browser-download and DNS failures. Skill registration and successful live crawling remain separate checks.
- Published a ready-to-upload skill ZIP with a SHA-256 checksum and a dated roundup of the previous 24 hours of improvements.

## 2.7.0

- Added offline branded PDF and HTML reports with the existing AevoraSEO logo, editorial cover, linked contents, evidence tables, source notes and action roadmaps. Normal setup includes the free PDF renderer; HTML stays available when PDF rendering is unavailable.
- Added report integration checks for embedded assets, pagination, navigation, long tables, escaped content, mobile layout and precise partial-output handling.

- Use reviewed buyer phrases and customer questions for discovery instead of mechanically stacking service labels; validate their profile/brief basis and distinguish hypotheses from keyword recommendations and measured demand.
- Added browser-first deep-research plans, five reputation query families and shared competitor/source budgets, with evidence-based comparison instead of a backlink-list-only report.
- Added cohort reputation comparison that recalculates source evidence and withholds ordinal positions when methods, dates, sample coverage or confidence differ.
- Preserve actual native result-page and multi-query provenance through reputation assessment; do not invent missing host pagination.
- Order strongest source examples by supported quality points instead of optimistic unknown-dimension midpoints; headline scoring model 1.1 remains unchanged.
- Added release hygiene checks for client captures, private identifiers and machine-specific paths; live research stays outside the repository.

- Recognize an unavailable host search provider without attributing it to Google or a remote denial; retain its unknown underlying cause and use the next permitted source.
- Require final competitor classifications to use reviewed evidence, retain known conflicts and use exact discovered domains; keep briefs for uninspected pages conditional.
- Do not promote broad international/global delivery overlap into a direct geographic competitor match.
- Let an older default Python hand off to an already installed compatible runtime before checking the engine version requirement.
- Corrected older capability descriptions to include the implemented native discovery adapters and explain browser choices across agent hosts.
- Preserve an existing local virtualenv during a backed-up skill update; restore the previous installation if preservation fails.
- Added explicit `--include-www` scope support for ordinary www/non-www redirects while retaining robots, TLS and address checks. Exact-host crawling remains available.
- Reject malformed source CSV quoting instead of silently corrupting search-query provenance; native discovery exports remain the preferred input.
- Clarified model authentication, tool execution and website/search access as separate diagnostic layers, and documented use of packaged commands to avoid unnecessary inline-code approvals.

## 2.6.0

- Added shared, bounded discovery for reputation and competitor work: permitted native DuckDuckGo HTML/Bing RSS, recorded host search/browser results, saved HTML and existing source CSVs. Failures, empty results, parser errors, query context and fallback attempts remain visible; duplicates retain provenance.
- Added reviewed business profiles, profile-derived queries and service/customer-first competitor selection. Offices, markets and languages stay separate; direct competitors, benchmarks, search leads and rejected candidates are labeled.
- Added evidence-based audit reports with exact URLs, dates, observations, business context, actions, priority rationale and acceptance checks. Failed/partial captures cannot establish missing content or markup.
- Fixed SVG accessibility titles being counted as document titles. Missing or denied browser runtime no longer aborts usable HTTP audit work.
- Added separate environment/search diagnostics, installed-browser detection and explicit, idempotent free Chromium setup. Host browser control remains a separately verified capability.
- Added deterministic discovery, relevance, evidence and browser-setup regressions. The reputation scoring model remains 1.1; no paid service or API key was introduced.


## 2.5.2

- Make printed follow-up commands safe to paste into PowerShell when paths contain spaces or special characters.

## 2.5.1

- Add a complete upload bundle with a matching `aevoraseo/` folder, concise metadata and a SHA-256 checksum.
- Add host-specific installation commands, profile/workspace options, repeat-install detection and backed-up updates.
- Support a separate approved runtime directory for hosted or read-only skill mounts.
- Separate skill registration from HTTP/browser readiness, with specific guidance for HTTP 422, permission and scan errors.
- Keep developer fixtures in the repository; distribute the runtime, playbooks, catalog and documentation in the skill bundle.
- Clarify package permissions and use dedicated credential paths in the optional hosting example.

## 2.5.0

- Added a 206-entry publishing library with 241 traceable source rows and documented posting guidance for 22 destinations.
- Added website-specific shortlists of 15 or 20 sources, including topics, writing briefs, posting steps, eligibility, link rules and a calendar.
- Added topic, prerequisite, free-term and freshness filters, with clear research gaps when too few sources qualify.
- Added Markdown, CSV and JSON plan exports and an optional PDF importer that preserves visible rows and conflicting source claims.
- Kept source-sheet DR values separate from current measured authority and from the AevoraSEO Reputation Score.
- Refreshed the README, assistant setup and posting guide with clear examples and a development guide.

## 2.4.0

- Launched the branded GitHub project with MIT licensing, a documentation index, verified creator links and issue templates.
- Fixed crawl exports to use the same package version as the CLI.
- Closed the crawl database when initialization rejects an incompatible resume or an existing output directory, preventing Windows file locks.
- Made the FTPS fixture's replacement capability explicit on all operating systems and verified that unsupported replacements preserve the live file and recovery receipt.
- Added a local skill-folder installer with dry runs, checksum receipts and protection for existing destinations.
- Added an activation-free launcher that resolves its own runtime and works from other working directories.
- Documented Claude Code, Codex, ChatGPT Work, Hermes and OpenClaw setup with explicit validation and cloud limits.
- Added a friendly FAQ, example questions, capability overview and precise no-API-key / model-usage explanation.
- Clarified why a small observed sample cannot replicate a proprietary authority model; retained conservative scoring model 1.1.
- Added portability behavior tests for clean copying, path handling, existing files and launcher exit codes.

## 2.3.1

- Changed the reputation headline to supported lower-bound points adjusted for the weakest measured evidence factor; low-confidence results cannot reach 50/100.
- Kept the old sample-quality midpoint as diagnostic context and added explicit provisional/withheld states and adjustment factors.
- Prevented duplicate imported evidence and unrelated target links from inflating observed support.
- Made backlinks, named competitor comparisons and a practical 30/60/90-day plan explicit defaults for general website audits.
- Added a complete audit delivery standard and a worked example.
- Added behavioral coverage for conservative scoring and identical treatment of client/competitor evidence.

## 2.3.0

- Added AevoraSEO Reputation Score, its published rubric, sensitivity ranges, coverage and attributable source reviews.
- Added five-page discovery plans, saved search-result imports and native link/mention verification without a service account.
- Grouped repeated publishers; excluded same-site sources and separated owned/affiliated evidence from independent editorial proof.
- Added bounded cross-host backlink redirect follow-ups and automatic checks for late links on text-rich JavaScript pages.
- Switched SEO metadata, duplicates and page inventories to successful rendered content while preserving raw noindex evidence.
- Added heuristic missing-content detection for HTTP 200 screens and their referring internal links.
- Separated robots disallow, unavailable policy, robots scope limits and redirect loops.
- Removed external SEO metric dependencies and added regression tests for crawler behavior and reputation evidence boundaries.

## 2.2.0

- Added plain-language readiness reports, separate search-crawler robots observations and raw/rendered indexing evidence.
- Added supplied-backlink verification, snapshot comparisons and bounded review loops.
- Added staged single-file text updates with local/SFTP/FTPS transport, reviewed hashes, backups and guarded rollback.
- Compacted the main skill and added friendly reporting, answer writing and reputation workflows.
- Added a source library and seven additional reputation routes.
- Added behavioral coverage for comparisons, monitoring, backlink verification and publishing safeguards.

## 2.1.0

- Added automatic browser fallback and an explicit browser mode.
- Added public dependency loading, visible-element waits, bounded scrolling and viewport screenshots.
- Added Markdown/text documents and improved selection for pages with incomplete main landmarks.
- Added a recorded robots-policy override for authorized crawling.
- Added the installable `aevoraseo` command, environment checks and a cross-platform setup script.
- Organized the SEO playbooks, examples, browser documentation and repository contribution files.
- Expanded regression coverage for browser behavior, content extraction and access diagnostics.

## 2.0.0

- Introduced the local HTTP crawler, BeautifulSoup extraction, SQLite resume and evidence exports.
- Added optional local Chromium observations and practical SEO finding candidates.
- Separated website observations from rankings, private analytics and backlink-index measurements.
