# AevoraSEO Agent Operating Plan

> **Purpose:** This file is the single source of truth for the coding agent working on AevoraSEO.
> It records what is complete, what is next, the long-term product direction, supported agent/CLI targets, and the engineering rules that must be followed.
>
> **Last reviewed:** 2026-09-22
> **Repository:** https://github.com/bhedanikhilkumar-code/aevoraSEO
> **Current branch:** main

---

## 1. PRODUCT MISSION

AevoraSEO is being built as a professional, evidence-first SEO intelligence platform.

The long-term product scope is:

**SEO + AEO + GEO + Entity + Authority + Reputation + Technical SEO + Content + Local/Commercial visibility + Backlinks + measurable improvement**

The product must help an operator move through one connected loop:

```
Understand
  ↓
Discover
  ↓
Crawl
  ↓
Capture Evidence
  ↓
Analyze
  ↓
Explain
  ↓
Prioritize
  ↓
Improve
  ↓
Verify
  ↓
Compare Again
```

The product must never manufacture certainty. Observed evidence, derived analysis, recommendations, predictions, and externally measured outcomes must remain separate.

### Primary goal

Build a professional SEO/AEO/GEO intelligence engine that can be used from normal terminals and across the supported AI/coding-agent environments shown in the project compatibility plan.

---

## 2. CURRENT VERIFIED STATUS

### Phase A — Repository & Engine Reconciliation
**STATUS: COMPLETE**

Verified scope:
- Python engine restored to the public repository.
- `src/aevoraseo/`, `tests/`, and `scripts/` are tracked.
- `.gitignore` no longer hides the engine/test/script source.
- Node launcher uses a hybrid native/Python fallback architecture.
- Version metadata was standardized to 1.0.0.
- CI coverage and release hygiene were established.
- CLI parity was tested.
- Release validation script exists.

Reference commit:
- `0de4fbf` — `feat(core): reconcile open source Python engine, restore src/tests/scripts, and enable hybrid runner`

### Phase B — Crawler Hardening & Incremental Intelligence
**STATUS: COMPLETE — PASS WITH MINOR FINDINGS**

Verified scope:
- quick / standard / deep crawl profiles
- persistent SQLite snapshots
- snapshot IDs and metadata
- incremental crawling
- ETag / Last-Modified conditional requests
- HTTP 304 extraction reuse
- snapshot diff engine
- resume support
- cache isolation
- SSRF protection
- robots and host-boundary controls
- CLI parity
- JSON / CSV / Markdown / terminal comparison output

Forensic audit evidence:
- 345 passed
- 2 skipped
- 0 failed
- 347 collected
- 22 subtests
- release hygiene: 227 files checked, 0 findings

Reference commit:
- `74e9387` — `feat(crawler): add hardened profiles and incremental snapshot intelligence`

Known non-blocking findings:
1. A page not re-observed is currently represented as REMOVED even when crawl scope could explain the absence. Future model should distinguish `UNOBSERVED_IN_SAMPLE` from confirmed removal.
2. Incremental crawl with a mismatched seed can currently proceed as a full crawl without a warning. Future work should add warning/strict behavior.
3. Export currently uses `fetchall()`; very large snapshots may eventually benefit from streaming pagination.

### Phase C — AEO/GEO Intelligence
**STATUS: COMPLETE — PASS**

Verified scope:
- answer readiness
- question/intent coverage
- direct-answer proximity detection (10-60 word definitions and structured lists)
- entity clarity and cross-page consistency audit
- citation/source readiness (author bylines, timestamps, publisher, canonicals)
- structured-data intelligence (Schema.org audit, completeness, consistency, syntax errors)
- AI crawler/bot accessibility matrix (10 tracked AI bots against robots.txt, robots meta, X-Robots-Tag)
- content extractability and semantic heading structure
- transparent AEO (0-100) and GEO (0-100) scoring models with signal contributions and deductions
- strict separation between analytical readiness and empirical external observed visibility
- snapshot comparison engine (`aeo-compare`) with categorized transitions (ADDED, REMOVED, IMPROVED, REGRESSED, UNCHANGED)
- SQLite persistence (`aeo_snapshots`, `aeo_pages`, `aeo_questions`, `aeo_entities`, `aeo_diffs`) integrated into `crawl.sqlite3` and `aeo.sqlite3`
- CLI commands: `aevoraseo aeo` and `aevoraseo aeo-compare` with terminal, JSON, CSV, and Markdown formats
- Node runner parity
- Security hardening against CSV formula injection attacks
- Defensive depth and cycle guards on JSON-LD parsing
- Comprehensive adversarial and security test suite (`tests/test_aeo_adversarial.py`)
- Technical methodology reference (`references/aeo-geo.md`)

Forensic audit evidence:
- 375 passed
- 2 skipped
- 0 failed
- 377 collected
- release hygiene: 238 files checked, 0 findings
- cross-platform connection handling verified on Windows

Reference commit:
- `d1f2736` — `feat(aeo): implement Phase C AEO/GEO intelligence engine, scoring, and snapshot diff`
- subsequent hardening: SQLite persistence, formula injection sanitization, adversarial tests, methodology documentation.

---

### Phase D — Backlink & Reputation Intelligence
**STATUS: COMPLETE — PASS**

Verified scope:
- native backlink discovery and verification subsystem (`aevoraseo.backlinks`, `aevoraseo.backlink_persistence`)
- target link matching, anchor text extraction, rel tokenization, conclusive dofollow determination, and 160-char sentence context excerpts
- deterministic source classification (`editorial`, `directory`, `profile`, `community`, `owned`) based on structural URL and domain heuristics
- strict ownership proof boundary: target domain, subdomains, and related hosts are classified as owned and excluded from independent proof
- conservative reputation scoring (Model 1.1) with supported points, evidence adjustments, confidence ceiling (49/100), and sensitivity range
- opportunity pipeline cross-referencing candidate referring domains and unreached leads against the 206-site catalog (`posting-sites.json`), exporting `reputation-opportunities.json` and `reputation-opportunities.csv`
- temporal snapshot comparison engine (`aevoraseo.reputation_comparison`, `aevoraseo reputation-compare`) calculating score deltas, added/lost/retained links, added/lost/retained mentions, and converted opportunities
- full SQLite persistence across `backlinks.sqlite3` (`backlink_snapshots`, `backlink_sources`, `backlink_links`, `backlink_mentions`) and `reputation.sqlite3` (`reputation_assessments`, `reputation_diffs`) with Windows-safe connection cleanup (`try/finally conn.close()`)
- CLI parity: `aevoraseo backlinks <target>`, `aevoraseo reputation <target>`, and `aevoraseo reputation-compare` with positional targets, default directories, and format flag (`--format {terminal,json,csv,markdown}`)
- security hardening: all CSV exports sanitized against spreadsheet formula injection attacks with `sanitize_csv_cell`
- comprehensive unit, intelligence, adversarial, and CLI test suites

Forensic audit evidence:
- 394 passed
- 2 skipped
- 0 failed
- 396 collected
- release hygiene: 244 files checked, 0 findings, PASSED
- zero `TODO`, `FIXME`, `NotImplementedError`, or stub placeholders
- cross-platform connection handling verified on Windows

---

### Phase E — Entity, Authority & Knowledge Intelligence
**STATUS: COMPLETE — PASS**

Verified scope:
- native Entity, Authority & Knowledge Intelligence subsystem (`aevoraseo.entity`)
- multi-source entity extraction parsing Schema.org JSON-LD, Microdata, OpenGraph, and meta tags with recursive cycle guards (`max_depth=25`)
- typed entity models: `Organization`, `Person`, `Product`, `Service`, `Place`, `LocalBusiness`, and `Article` with attribute mapping
- `sameAs` authority discovery classifying external profiles across Wikidata, Wikipedia, LinkedIn, Crunchbase, GitHub, ORCID, Google Business, Trustpilot, etc., and identifying missing standard corporate profiles
- cross-page entity consistency auditor detecting organization name contradictions, NAP (Name, Address, Phone) mismatches, broken sameAs URLs, and missing core entity pages (`/about`, `/team`, `/contact`, `/reviews`)
- directed knowledge graph builder (`EntityKnowledgeGraph`) computing graph topology metrics (degree centrality, density, central entity) and exporting standard D3/Cytoscape format (`entity-graph.json`)
- deterministic AevoraSEO Entity & Authority Score (0–100) evaluated across four 25-point dimensions: Identity Completeness, Entity Consistency & Integrity, SameAs & Authority Footprint, and Topical/Expert Depth
- SQLite persistence across `entities.sqlite3` (`entity_snapshots`, `entity_nodes`, `entity_edges`, `entity_same_as`, `entity_conflicts`, `entity_diffs`) with Windows-safe connection cleanup (`try/finally conn.close()`)
- temporal entity diff engine (`compare_entity_snapshots`, `aevoraseo entity-compare`) tracking added/removed/modified entities, resolved/new conflicts, added/lost sameAs profiles, and score deltas
- CLI commands: `aevoraseo entity <target>` and `aevoraseo entity-compare` with multi-format presentation (`terminal`, `json`, `csv`, `markdown`)
- security hardening: sanitized all exported CSV files (`entities.csv`, `entity-conflicts.csv`) against spreadsheet formula injection attacks with `sanitize_csv_cell`
- upload boundary compliance: consolidated unreferenced playbooks into indexed README resources (196 files <= 200 limit)
- comprehensive unit, consistency, graph, comparison, adversarial, and CLI test suites (18 new tests, 412 tests passing across the suite)

Forensic audit evidence:
- 412 passed
- 2 skipped
- 0 failed
- 414 collected
- upload package validation: 196 files, 197 archive files (<= 200 limit), 216 local references, format check PASSED
- zero `TODO`, `FIXME`, `NotImplementedError`, or stub placeholders
- cross-platform connection handling verified on Windows

---

### Phase F — Search, Local & Commercial Intelligence
**STATUS: COMPLETE — PASS**

Verified scope:
- native Search, Local & Commercial Intelligence subsystem (`aevoraseo.search`)
- search intent taxonomy classifying pages into Informational, Commercial Investigation, Transactional, Navigational, and Local intents
- deterministic target query extraction identifying 2-to-5 word primary queries and secondary candidate phrases from H1, Title, meta description, and URL slugs
- keyword cannibalization detector using Jaccard token similarity to identify internal page competition, assigning High/Medium/Low risk levels and actionable remediation
- local search visibility auditor validating Schema.org `LocalBusiness` and specialized sub-types (`Dentist`, `Store`, etc.), verifying uniform NAP consistency, clickable telephone links (`<a href="tel:...">`), Google Maps embeds, and service-area declarations
- commercial conversion journey and CTA friction engine classifying high-intent action buttons vs generic links, checking trust proof proximity (reviews, doctor/expert credentials, guarantees), and auditing form field friction
- comparison and buyer decision support auditing head-to-head comparison pages, structured feature matrices (`<table>`), evaluated alternatives, and objection-handling buyer FAQs
- deterministic **AevoraSEO Search & Commercial Visibility Score (0–100)** across four 25-point dimensions: Intent & Query Targeting, Commercial Journey & CTAs, Local Visibility Signals, and Comparison & Buyer Decisions
- SQLite persistence across `search_commercial.sqlite3` (`search_snapshots`, `search_page_intents`, `search_cannibalization`, `search_local_signals`, `search_commercial_audits`, `search_diffs`) with Windows-safe connection cleanup (`try/finally conn.close()`)
- temporal snapshot diff engine (`compare_search_snapshots`, `aevoraseo search-compare`) calculating score deltas, intent shifts, resolved/new cannibalizations, and commercial improvements
- CLI commands: `aevoraseo search <target>`, `aevoraseo commercial <target>`, and `aevoraseo search-compare` with multi-format presentation (`terminal`, `json`, `csv`, `markdown`)
- Node launcher parity in `bin/aevoraseo.js`
- security hardening: sanitized all exported CSV files (`page-intents.csv`, `cannibalization.csv`, `commercial-friction.csv`, `search_comparison.csv`) against spreadsheet formula injection attacks
- consolidated unreferenced templates and keyword research playbooks into indexed README files, maintaining hosted skill bundle file count strictly below the ceiling (194 files, 195 archive files <= 200 limit)
- comprehensive unit, intent, cannibalization, local, commercial, comparison, adversarial, and CLI test suites (22 new tests, 434 tests passing across the suite)

Forensic audit evidence:
- 434 passed
- 2 skipped
- 0 failed
- 436 collected
- 22 subtests passed in 98.08s
- release hygiene: 267 files checked, 0 findings, PASSED
- upload package validation: 194 files, 195 archive files (<= 200 limit), 216 local references, format check PASSED
- zero `TODO`, `FIXME`, `NotImplementedError`, or stub placeholders
- cross-platform connection handling verified on Windows

---

### Phase G — Content & Optimization Intelligence
**STATUS: COMPLETE — PASS**

Verified scope:
- native Content & Optimization Intelligence subsystem (`aevoraseo.optimization`)
- title tag optimization analyzing character lengths (45-65 optimal), brand placement, primary query alignment, and keyword stuffing detection
- meta description optimization evaluating length (120-160 optimal), actionable CTA verb detection (`discover`, `explore`, `book`, `call`, `learn`), and query relevance
- heading hierarchy and structure auditing single H1 compliance, logical consecutive nesting, skipped-level detection (e.g. H1->H3, H2->H4), question headings, and empty heading cleanup
- direct-answer and definition opportunity engine detecting definition phrases (`is a`, `refers to`) and prescribing 40-60 word answer boxes, procedural lists, and comparison tables
- FAQ and buyer objection opportunity engine discovering pricing transparency, guarantee/SLA, and support friction gaps on transactional pages
- site-wide internal link graph auditing in-degree and out-degree, detecting orphan pages (0 internal links), deep crawl depth, and generic anchor warnings (`click here`)
- topic cluster and pillar-spoke analysis grouping pages by path and topic, mapping pillar hubs to supporting spokes, and calculating cluster health scores (0-100)
- intent-matched schema recommendation engine mapping pages to `Article`, `Service`, `Product`, `LocalBusiness`, `FAQPage`, `Course`, and `HowTo` schemas
- grounded content brief generator synthesizing target queries, intent-scaled target word counts, required sections, direct answer targets, internal links, and editorial guidance
- editorial outline generator producing structured heading blueprints with 40-60 word answer box targets, bullet points, FAQ blueprints, and CTA placement
- content gap and refresh candidate prioritization detecting thin content (<250w, <500w), aging year references (<=2023), and missing comparison/FAQ pages
- prioritized 30/60/90-day optimization roadmap structured across Foundation (Days 1-30), Answer Depth & Schema (Days 31-60), and Cluster Compounding (Days 61-90)
- deterministic **AevoraSEO Content Optimization Score (0-100)** across four 25-point dimensions: Metadata & Heading Architecture, Content Quality & Answer Depth, Topic Cluster & Internal Link Health, and Structured Data & Schema Coverage
- SQLite persistence in `content_optimization.sqlite3` (`optimization_snapshots`, `optimization_page_audits`, `optimization_answer_opportunities`, `optimization_topic_clusters`, `optimization_content_briefs`, `optimization_diffs`) with Windows-safe connection cleanup (`try/finally conn.close()`)
- temporal snapshot comparison engine (`compare_optimization_snapshots`, `aevoraseo optimize-compare`) calculating score deltas, resolved deficiencies, new regressions, and cluster evolution
- CLI parity: `aevoraseo optimize <target>` (alias `aevoraseo content`) and `aevoraseo optimize-compare` across terminal, markdown, JSON, and CSV formats
- Node launcher parity in `bin/aevoraseo.js`
- formula injection defense sanitizing all exported CSV files (`content-recommendations.csv`, `content-briefs.csv`, `direct-answers.csv`, `internal-links.csv`)
- consolidated unreferenced single-topic playbooks (`growth-plans.md`, `growth-models.md`, `competitor-research-workflow.md`, `site-audit-workflow.md`, `backlink-evaluation.md`), maintaining hosted skill bundle file count strictly below ceiling (197 bundle files, 198 archive files <= 200 limit)
- comprehensive unit, metadata, answer, cluster, brief, persistence, comparison, and CLI test suites (20 new tests, 454 tests passing across the suite)

Forensic audit evidence:
- 454 passed
- 2 skipped
- 0 failed
- 456 collected
- 22 subtests passed in 116.23s
- release hygiene: 272 files checked, 0 findings, PASSED
- upload package validation: 197 files, 198 archive files (<= 200 limit), 218 local references, format check PASSED
- zero `TODO`, `FIXME`, `NotImplementedError`, or stub placeholders
- cross-platform connection handling verified on Windows

---

### Phase H — Multi-Agent & Platform Compatibility
**STATUS: COMPLETE — PASS**

Verified scope:
- native Multi-Agent & Platform Compatibility subsystem (`aevoraseo.compatibility`)
- empirical platform registry cataloging 18 target environments: Agent (ChatGPT Work), Claude Code, Codex, Hermes Agent, OpenClaw, aider, Copilot CLI, Gemini CLI, Factory Droid, Kilocode CLI, OpenCode CLI, Qwen, JCODE, jcode CLI, juni CLI, Kiro, prime-agent, and cai
- platform integration tiers: First-party skill, Project instruction, CLI integration, and Generic adapter
- environment detector (`detect_environment`) discovering active platforms and workspaces via environment variables, workspace marker files, and global user config directories
- profile and workspace validator (`validate_installation`, `validate_workspace_isolation`, `check_python_compatibility`) verifying receipt integrity, SHA-256 checksums, and strict boundary isolation
- platform adapter generator (`generate_adapter`) emitting deterministic configuration files (`.aider.conf.yml`, `.github/copilot-instructions.md`, `GEMINI.md`) with safe `--dry-run` and collision guards
- fixture-based compatibility verifier (`verify_platform`, `verify_all_platforms`) executing simulated workspace tests without mutating real host configurations
- CLI parity via `aevoraseo agent` (with actions: `detect`, `list`, `inspect`, `adapt`, `verify`) across `terminal`, `json`, and `markdown` output formats
- Node launcher parity in `bin/aevoraseo.js` with `agent` command routing and help text
- expanded `scripts/install_skill.py` supporting all 18 platform destinations under `--host`
- technical methodology reference in `references/multi-agent-compatibility.md` with evidence-based status definitions (`VERIFIED`, `PARTIAL`, `DOCUMENTED`, `NOT VERIFIED`, `UNSUPPORTED`)
- consolidated 8 unreferenced core and competitor playbooks, maintaining hosted skill bundle strictly below upload ceiling (198 bundle files, 199 archive files <= 200 limit)
- comprehensive unit, detector, validator, adapter, verifier, and CLI test suites (23 new tests, 477 tests passing across the suite)

Forensic audit evidence:
- 477 passed
- 2 skipped
- 0 failed
- 479 collected
- 22 subtests passed in 104.56s
- release hygiene: 266 files checked, 0 findings, PASSED
- upload package validation: 198 files, 199 archive files (<= 200 limit), 220 local references, format check PASSED
- zero `TODO`, `FIXME`, `NotImplementedError`, or stub placeholders
- cross-platform connection handling verified on Windows

---

### Phase I — Reporting, Operations & Professional Workflow
**STATUS: COMPLETE — PASS**

Verified scope:
- unified cross-subsystem report generator (`aevoraseo.unified_report`) synthesizing Technical, Content, AEO, GEO, Entity, Authority, Reputation, and Search/Commercial intelligence
- deterministic health scorecard aggregating subsystem metrics and calculating calibrated overall score (0–100)
- multi-format client report exports (`terminal`, `html`, `markdown`, `json`, `csv`) with styled responsive executive HTML presentation
- strict P0 (Critical Blocker), P1 (High Impact Opportunity), and P2 (Optimization Routine) issue prioritization with actionable impact, remediation steps, and verification criteria
- formula injection protection across all exported CSV files (`audit-issues.csv`, `audit-scorecard.csv`) with `sanitize_csv_cell`
- operational acceptance verification engine (`aevoraseo.workflow.verify_audit_acceptance`) verifying whether prior audit issues are resolved or persist in subsequent crawl snapshots
- chronological progress tracking (`aevoraseo.workflow.track_progress`) analyzing score deltas and trajectory (`IMPROVING`, `DECLINING`, `STABLE`) across multi-snapshot crawl histories
- operational database diagnostics (`aevoraseo.workflow.run_operational_diagnostics`) executing `PRAGMA integrity_check` on all workspace SQLite databases and reporting runtime health
- CLI parity for `aevoraseo report`, `aevoraseo audit-verify`, and `aevoraseo progress` across terminal, JSON, Markdown, and CSV formats
- Node launcher parity in `bin/aevoraseo.js` with synchronized command routing and help text
- technical methodology reference in `references/reporting-operations.md`
- consolidated playbooks to maintain upload package boundary compliance (197 bundle files, 198 archive files <= 200 limit)
- comprehensive unit and CLI integration test suites in `tests/test_unified_report.py` and `tests/test_operational_workflow.py` (15 new tests, 492 tests passing across the suite)

Forensic audit evidence:
- 492 passed
- 2 skipped
- 0 failed
- 494 collected
- 22 subtests passed in 97.71s
- release hygiene: 267 files checked, 0 findings, PASSED
- upload package validation: 197 files, 198 archive files (<= 200 ceiling), 226 local references, format check PASSED
- zero `TODO`, `FIXME`, `NotImplementedError`, or stub placeholders
- cross-platform connection handling verified on Windows

Reference commit:
- `a460b3b` — `feat(reporting): implement unified cross-subsystem report generator, operational workflow, and CLI commands`
- `872d713` — `test(reporting): add unit and CLI integration tests for unified reporting and operational workflow`

---

### Phase J — Production Hardening & Release
**STATUS: COMPLETE — PASS**

Verified scope:
- adversarial penetration audit across all subsystems, reinforcing SSRF defenses, scheme blocking, private IP detection, and XXE XML injection safeguards
- hardened CSV export routines across all subsystems (`engine`, `unified_report`, `review`, `aeo`, `entity`, `search`, `optimization`, `reputation`, `backlinks`) with dual-check formula injection defenses (`=`, `+`, `-`, `@`, `\t`, `\r`, and leading whitespace formula traps)
- fixed XML sitemap parsing in `engine.parse_sitemap` to ensure sanitized null-byte stripped buffers are passed to XML element trees
- audited SQLite connection lifecycle across all operational and persistence modules, guaranteeing immediate file unlock on Windows with `try/finally conn.close()`
- verified multi-snapshot progress calculation scalability across multi-snapshot histories without unbounded memory growth
- conducted zero stub policy audit across `src/` and `scripts/`, confirming 0 instances of `TODO`, `FIXME`, or `NotImplementedError`
- validated hosted skill upload package ceiling compliance: 197 files, 198 archive files strictly within the $\le 200$ ceiling (`validate_skill.py`)
- release hygiene verified with 0 findings across 268 files (`check_release.py`)
- implemented comprehensive production hardening test suite in `tests/test_production_hardening.py` (34 new tests, 526 tests passing across the suite)

Forensic audit evidence:
- 526 passed
- 2 skipped
- 0 failed
- 528 collected
- 22 subtests passed in 124.26s
- release hygiene: 268 files checked, 0 findings, PASSED
- upload package validation: 197 files, 198 archive files (<= 200 ceiling), 226 local references, format check PASSED
- zero `TODO`, `FIXME`, `NotImplementedError`, or stub placeholders
- cross-platform connection handling verified on Windows

Reference commit:
- `b2b3b3f` — `feat(security): harden CSV formula injection defenses, fix sitemap null bytes, and add production hardening test suite`

---

## 3. CURRENT PHASE

### All Roadmap Phases (A through J) — COMPLETE
**STATUS: PRODUCTION READY / RELEASE VERIFIED**

All 10 architectural phases (A through J) of AevoraSEO are completely implemented, thoroughly tested, defensively audited, and empirically verified.
The platform is fully ready for public release v1.0.0 and distribution across npm, PyPI, and supported AI coding-agent skill hosts.

---

## 4. LONG-TERM ROADMAP

The roadmap below is the working product plan. A future phase may be split into smaller implementation milestones when the repository requires it.

## Phase A — Repository & Engine Reconciliation
**COMPLETE**

Open-source source visibility, version alignment, hybrid runner, CI, and release hygiene.

## Phase B — Crawler Hardening & Incremental Intelligence
**COMPLETE**

Profiles, snapshots, conditional requests, incremental reuse, diffing, resume, cache isolation, and security hardening.

## Phase C — AEO/GEO Intelligence
**COMPLETE**

Answer readiness, question/intent coverage, direct answers, entity clarity, citation readiness, schema intelligence, AI crawler accessibility, extraction quality, transparent scoring, SQLite persistence, and snapshot comparison.

## Phase D — Backlink & Reputation Intelligence
**COMPLETE**

Native backlink discovery, anchor/context extraction, source classification, ownership proof boundary, Model 1.1 reputation scoring, 206-site opportunity tracking, SQLite persistence, snapshot comparison, CSV formula injection defense.

## Phase E — Entity, Authority & Knowledge Intelligence
**COMPLETE**

Typed entity extraction, sameAs authority discovery, knowledge graph topology, cross-page consistency audits, AevoraSEO Entity & Authority Score (0-100), SQLite persistence, entity-compare diff engine, and bundle limit compliance.

## Phase F — Search, Local & Commercial Intelligence
**COMPLETE — PASS**

Search intent, query mapping, cannibalization, local visibility, commercial journeys, comparison/buyer support, deterministic scoring, SQLite persistence, snapshot comparison, CLI parity, and CSV security hardening are implemented and verified.

Reference commit:
- `060d1f4` — `feat(search): complete Phase F search, local & commercial intelligence, persistence, comparisons, and tests`

Forensic evidence:
- 436 collected
- 434 passed
- 2 skipped
- 0 failed
- 22 subtests passed
- release hygiene: 267 files checked, 0 findings
- bundle validation: 194 files / 195 archive files
- 216 local references checked
- compileall clean
- Node `version`, `--help`, and `doctor` verified

Known boundary:
- actual search rankings and Search Console metrics remain external measurements unless supplied by authenticated/verified data.

## Phase G — Content & Optimization Intelligence
**COMPLETE**

Title tag & meta description audits, single H1 & heading hierarchy verification, direct answer box & definition engineering (40-60 words), FAQ objection handling, topic cluster pillar-spoke mapping, internal link graph & orphan recovery, intent-matched schema recommendations, grounded content briefs & editorial outlines, content gap & refresh prioritization, 30/60/90-day roadmaps, Content Optimization Score (0-100), SQLite persistence in `content_optimization.sqlite3`, optimize-compare diff engine, and formula injection defense.

## Phase H — Multi-Agent & Platform Compatibility
**COMPLETE — PASS**

Empirical platform registry across 18 environments, environment detection, installation & isolation validation, adapter generation, fixture verification, CLI parity (`aevoraseo agent`), Node launcher parity, and skill package boundary compliance (198 bundle files, 199 archive files <= 200 limit).

Forensic evidence:
- 479 collected
- 477 passed
- 2 skipped
- 0 failed
- 22 subtests passed
- release hygiene: 266 files checked, 0 findings
- bundle validation: 198 files / 199 archive files (<= 200 ceiling)
- 220 local references checked
- compileall clean
- Node `version`, `--help`, `doctor`, and `agent list` verified

## Phase I — Reporting, Operations & Professional Workflow
**COMPLETE — PASS**

Unified cross-subsystem report generator synthesizing Technical, Content, AEO, GEO, Entity, Authority, Reputation, and Search/Commercial intelligence, multi-format exports (`terminal`, `html`, `markdown`, `json`, `csv`), P0/P1/P2 issue prioritization with acceptance criteria, spreadsheet formula injection protection, operational acceptance verification (`aevoraseo audit-verify`), chronological multi-snapshot progress tracking (`aevoraseo progress`), SQLite database integrity diagnostics, and Node launcher parity.

Reference commits:
- `a460b3b` — `feat(reporting): implement unified cross-subsystem report generator, operational workflow, and CLI commands`
- `872d713` — `test(reporting): add unit and CLI integration tests for unified reporting and operational workflow`

Forensic evidence:
- 494 collected
- 492 passed
- 2 skipped
- 0 failed
- 22 subtests passed in 97.71s
- release hygiene: 267 files checked, 0 findings
- bundle validation: 197 files / 198 archive files (<= 200 ceiling)
- 226 local references checked
- compileall clean
- Node `version`, `--help`, `doctor`, `report`, `audit-verify`, and `progress` verified

## Phase J — Production Hardening & Release
**COMPLETE — PASS**

Adversarial penetration audits, formula injection defenses across all CSV exports, XML sitemap null-byte parsing fix, SQLite Windows locking hygiene, multi-snapshot scaling, complete CLI parity, zero stub policy compliance, release hygiene, and upload package validation.

Reference commit:
- `b2b3b3f` — `feat(security): harden CSV formula injection defenses, fix sitemap null bytes, and add production hardening test suite`

Forensic evidence:
- 528 collected
- 526 passed
- 2 skipped
- 0 failed
- 22 subtests passed in 124.26s
- release hygiene: 268 files checked, 0 findings
- bundle validation: 197 files / 198 archive files (<= 200 ceiling)
- 226 local references checked
- compileall clean
- Node `version`, `--help`, `doctor`, `report`, `audit-verify`, and `progress` verified

---

# 5. PHASE DEPENDENCY ORDER

Do not skip architectural dependencies.

```
A  COMPLETE
 ↓
B  COMPLETE
 ↓
C  COMPLETE
 ↓
D  COMPLETE
 ↓
E  COMPLETE
 ↓
F  COMPLETE
 ↓
G  COMPLETE
 ↓
H  COMPLETE
 ↓
I  COMPLETE
 ↓
J  COMPLETE
```

A phase may use existing capabilities from a later conceptual area only when the functionality already exists. Do not duplicate it just to satisfy a phase label.

---

# 6. MULTI-AGENT / CLI PRINCIPLE

AevoraSEO has two separate compatibility layers:

### Layer 1 — Native CLI
The core engine must work through:
```bash
aevoraseo ...
```

and the Node wrapper:
```bash
node bin/aevoraseo.js ...
```

### Layer 2 — Agent/Skill integration
Agent environments should be able to:
- read the skill instructions
- locate the project
- invoke the native engine
- preserve evidence
- understand limitations
- run diagnostics
- continue work safely

Never duplicate the Python engine in every agent integration.

Use one core engine with thin host adapters.

---

# 7. README REQUIREMENT

The README must become strong but NOT complicated.

The final README should answer five questions immediately:

1. What is AevoraSEO?
2. Why is it useful?
3. How do I install it?
4. How do I run the first audit?
5. What can it analyze?

Recommended structure:

```
AevoraSEO
one-line product statement

Quick Start
  npm/npx
  Python

What it does
  SEO
  AEO
  GEO
  Entity
  Authority
  Reputation
  Technical
  Content

Simple workflow
  Crawl → Analyze → Improve → Verify

Supported agents/CLIs
  concise compatibility table

Example commands

Evidence / limitations

Documentation links

Development / tests

License / maintainer
```

Avoid turning README.md into a 20–40 KB manual.

Detailed material belongs in:
- docs/
- references/
- playbooks/
- SKILL.md

The README should be a product landing page + quick-start guide.

---

# 8. DOCUMENTATION RULE

Every important feature must have one obvious home.

Use:

```
README.md       → simple product introduction + quick start
AGENT.md        → agent operating plan and roadmap
SKILL.md        → assistant behavior and workflow
docs/           → user/operator documentation
references/     → technical methodology and evidence rules
playbooks/      → repeatable professional workflows
CHANGELOG.md    → release history
```

Do not duplicate the same long explanation across every file.

---

# 9. ENGINEERING RULES

## Evidence first
Every important finding must identify:
- what was observed
- source
- location
- interpretation
- confidence
- limitation

## Deterministic core
Same input + same configuration should produce the same result.

## No fake AI
Do not use random values, fake model calls, or hardcoded outputs to simulate intelligence.

## No hardcoded website results
Never branch on a test URL to manufacture a score or finding.

## No production stubs
Avoid TODO/FIXME/NotImplementedError/placeholder implementations in production paths.

## Security
Preserve:
- SSRF protection
- DNS/IP validation
- robots enforcement
- host boundaries
- redirect safety
- origin isolation
- cache isolation
- untrusted HTML handling

Never execute crawled page content.

## Backward compatibility
Do not break existing Phase A/B snapshot and CLI behavior without an explicit migration.

## Small modules
Prefer focused analyzers over one giant intelligence module.

## Tests with features
Every feature gets tests before being considered complete.

---

# 10. SCORING RULES

Scores are derived measurements, not truth.

Every score should expose:
- dimension
- raw evidence
- calculation
- weight
- confidence
- coverage
- limitations

Never claim:
- guaranteed ranking
- guaranteed AI citation
- guaranteed traffic
- guaranteed authority
- guaranteed conversion

Use:
- readiness
- evidence strength
- observed coverage
- confidence
- derived score

---

# 11. SECURITY / PRIVACY

Never commit:
- API keys
- passwords
- cookies
- client credentials
- private reports
- local databases from real clients
- personal secrets
- machine-specific runtime files

Before every release:
```bash
git diff --check
python scripts/check_release.py
```

---

# 12. REQUIRED VERIFICATION AFTER EACH PHASE

Every phase must finish with:

1. focused unit tests
2. integration tests
3. E2E tests where appropriate
4. full regression suite
5. CLI smoke tests
6. Node-wrapper smoke tests
7. release hygiene
8. anti-fake scan
9. security review
10. documentation review
11. forensic audit
12. exact implementation report

Never say "complete" without test evidence.

---

# 13. PHASE COMPLETION TEMPLATE

For every future phase, produce:

### Implementation
- files added
- files changed
- architecture
- data model
- CLI
- reports

### Verification
- tests collected
- passed
- failed
- skipped
- runtime
- E2E results

### Security
- threats tested
- protections preserved

### Quality
- determinism
- performance
- anti-hardcoding
- anti-stub

### Documentation
- README changes
- docs changes
- references
- SKILL updates

### Audit
- findings
- remediation
- remaining limitations

### Final state
One of:
- PASS
- PASS WITH MINOR FINDINGS
- FAIL

---

# 14. CURRENT NEXT ACTION

All 10 architectural phases (Phases A through J) of AevoraSEO are **COMPLETE** and empirically verified.

The product status is:

## FULL ROADMAP COMPLETE (PHASES A — J) — PRODUCTION READY

Summary of verified capabilities:
- **Phase A**: Open-source engine reconciliation, hybrid Node runner, release hygiene
- **Phase B**: Crawler hardening, SQLite snapshots, conditional 304 reuse, diffing, SSRF defense
- **Phase C**: AEO/GEO answer engine intelligence, transparent scoring, snapshot comparisons
- **Phase D**: Backlink discovery, source classification, ownership proof boundary, Model 1.1 reputation
- **Phase E**: Typed entity extraction, knowledge graph topology, sameAs authority, consistency audits
- **Phase F**: Search intent taxonomy, query extraction, cannibalization, local & commercial CTAs
- **Phase G**: Title/heading audits, direct answer boxes, FAQ objection handling, topic clusters, briefs
- **Phase H**: Multi-agent platform compatibility across 18 target AI agent/CLI environments
- **Phase I**: Unified client reporting (HTML/PDF/MD/JSON/CSV), acceptance checks, progress tracking
- **Phase J**: Adversarial security penetration, formula injection defense, zero stubs, upload ceiling compliance

Current operational status:
- Tag release `v1.0.0`: **COMPLETE** (Tagged at HEAD, pushed to `origin`, GitHub Release synchronized with `aevoraseo-1.0.0-skill.zip` and SHA-256 sidecar).
- Quality gates: 526 tests passing, 0 failures, 268 files release hygiene passed, 197 files / 198 archive files strictly $\le 200$ upload limit.

Next operational distribution steps:
- Publish package to npm (`npm publish --access public`)
- Publish package to PyPI (`python -m build && twine upload dist/*`)
- Register skill across supported AI coding-agent platforms (`scripts/install_skill.py --host <platform>`)

---

# 15. IMPORTANT PRODUCT BOUNDARY

AevoraSEO is not just a crawler.

It is intended to become a connected intelligence system:

```
TECHNICAL SEO
     +
CONTENT
     +
AEO
     +
GEO
     +
ENTITY
     +
AUTHORITY
     +
REPUTATION
     +
SEARCH / LOCAL
     +
OPTIMIZATION
     +
VERIFICATION
```

The core architecture must therefore favor reusable evidence records and snapshot history rather than isolated one-off analyzers.

---

# 16. AGENT BEHAVIOR

When starting a task:

1. Read this AGENT.md.
2. Identify the current phase.
3. Inspect existing implementation before writing code.
4. Reuse existing evidence and snapshot infrastructure.
5. Do not duplicate functionality already present.
6. Implement the smallest coherent architecture.
7. Add tests.
8. Run tests.
9. Fix failures.
10. Audit security.
11. Audit for fake/hardcoded behavior.
12. Update documentation.
13. Run release hygiene.
14. Report exact evidence.
15. Only then mark the phase complete.

If the repository contradicts this document, inspect the code and tests first and update AGENT.md only after establishing the actual state.

---

## STATUS SUMMARY

| Phase | Area | Status |
|---|---|---|
| A | Repository & Engine Reconciliation | COMPLETE |
| B | Crawler Hardening & Incremental Intelligence | COMPLETE — MINOR FINDINGS |
| C | AEO/GEO Intelligence | COMPLETE — PASS |
| D | Backlinks & Reputation Intelligence | COMPLETE — PASS |
| E | Entity & Authority Intelligence | COMPLETE — PASS |
| F | Search / Local / Commercial Intelligence | COMPLETE — PASS |
| G | Content & Optimization Intelligence | COMPLETE — PASS |
| H | Multi-Agent / CLI Ecosystem | COMPLETE — PASS |
| I | Reporting & Operations | COMPLETE — PASS |
| J | Production Hardening & Release | COMPLETE — PASS |

**Rule:** Do not skip phases without documenting why.


# 17. MASTER IMPROVEMENT DIRECTIVE

This is the permanent engineering directive for improving AevoraSEO.

## Mission

Continuously improve AevoraSEO into a professional, maintainable, evidence-first platform covering:

**SEO + AEO + GEO + Entity + Authority + Reputation + Technical SEO + Content + Local/Commercial visibility + Backlinks + Verification.**

The goal is not to create the largest feature list. The goal is to create a system whose important claims can be inspected, reproduced, tested, explained, and verified.

## Repository-first improvement process

Before changing anything:

1. Inspect the current repository tree.
2. Read AGENT.md.
3. Read README.md and SKILL.md.
4. Inspect the current CLI and Node wrapper.
5. Inspect crawler, snapshot, review, diagnostics, schema/entity, and reporting code.
6. Inspect tests before changing production behavior.
7. Inspect the current Git history.
8. Identify duplicated, obsolete, misleading, or contradictory behavior.
9. Reuse existing architecture whenever possible.
10. Write an implementation plan before making broad changes.

Never assume an old roadmap is more accurate than executable code and tests.

## Use BeyondSEO as a reference, not a source to copy

The repository `beyondtahir/beyondseo` was inspected as a product/reference point.

Its useful product ideas include:
- connected SEO/AEO/GEO workflow
- evidence-first research
- reputation and backlink methodology
- competitor discovery
- content and answer readiness
- agent installation workflows
- practical reports
- improvement/review loops

Do not copy proprietary implementation, private identity information, or unrelated code. Extract product requirements and improve them inside AevoraSEO's own architecture.

AevoraSEO must remain independently maintainable and clearly branded.

## Professional product model

All future capabilities should fit this model:

```
Target
  ↓
Discovery
  ↓
Crawl / Capture
  ↓
Evidence Store
  ↓
Domain Intelligence
  ├── SEO
  ├── AEO
  ├── GEO
  ├── Entity
  ├── Authority
  ├── Reputation
  ├── Search / Local
  └── Content
  ↓
Findings
  ↓
Priorities
  ↓
Recommendations
  ↓
Approved Improvements
  ↓
Verification
  ↓
Snapshot Comparison
```

A new subsystem should integrate with this lifecycle instead of becoming an isolated command.

## Evidence contract

Every intelligence result should be traceable to evidence.

Preferred structure:

```text
Observation
Source
Location
Rule
Derived result
Confidence
Coverage
Limitation
```

If the system cannot observe something, represent it as unknown or unavailable.

Never convert:
- missing data into zero-quality evidence,
- a search snippet into a verified backlink,
- a prediction into a measurement,
- a small sample into a whole-web claim,
- an inferred entity into a confirmed entity.

## Score contract

Every score must document:
- dimensions
- weights
- inputs
- calculation
- confidence
- sample/coverage
- limitations
- model/version identifier

Scores must be reproducible.

Do not optimize tests by adjusting scores until they "look good."

## User-facing quality

Outputs must be:
- professional
- concise
- actionable
- evidence-backed
- understandable without reading source code

Recommendations should answer:

```
What is wrong?
Where?
Why does it matter?
What should change?
How can we verify the change?
```

## CLI quality

Every public command must have:
- useful `--help`
- stable exit behavior
- clear errors
- machine-readable output where applicable
- human-readable output
- deterministic behavior
- tests

Python CLI and Node wrapper must remain synchronized.

## Multi-platform target

The following environments are explicit compatibility targets from the product brief:

```
Agent
aider
cai
Copilot CLI
droid
Gemini CLI
JCODE
jcode CLI
juni CLI
Kilocode CLI
Kiro
OpenCode CLI
prime-agent
Qwen
```

For each environment, build a thin integration/installation adapter only when the environment actually supports it.

Maintain a compatibility matrix with:

| Platform | Install | Skill/Agent file | Native CLI | Python runtime | Browser | Smoke test | Status |
|---|---|---|---|---|---|---|---|

Use these states:

- VERIFIED
- PARTIAL
- DOCUMENTED
- NOT VERIFIED
- UNSUPPORTED

Never label an environment VERIFIED from documentation alone.

## README improvement contract

Keep README.md simple.

The README should be the product front door, not the entire manual.

Target sections:

1. Product statement
2. Quick start
3. What AevoraSEO analyzes
4. SEO/AEO/GEO/Entity/Authority/Reputation overview
5. One workflow diagram
6. Example commands
7. Multi-platform compatibility
8. Evidence and limitations
9. Links to detailed docs
10. Development/test basics

Move detailed methodology to docs/references.

Remove:
- stale claims
- contradictory installation instructions
- duplicated long explanations
- unsupported platform guarantees
- old product-name references
- placeholder maintainer text
- claims not supported by the current implementation

## Identity and metadata

The public AevoraSEO identity must remain consistent.

Current maintainer information:
- Name: Bheda Nikhilkumar
- GitHub: https://github.com/bhedanikhilkumar-code
- LinkedIn: https://www.linkedin.com/in/bhedanikhilkumar
- Email: bhedanikhilkumarpro@gmail.com

Do not reintroduce old creator identity or unrelated branding.

## Quality gates

A change is not complete until appropriate checks have passed.

Minimum:

```bash
git diff --check
python scripts/check_release.py
python -m compileall -q src scripts
pytest
node bin/aevoraseo.js version
node bin/aevoraseo.js doctor
```

Add focused tests for every new behavior.

For security-sensitive changes add adversarial tests.

For snapshot changes add migration/backward-compatibility tests.

## Anti-fake audit

Before declaring a phase complete, inspect production code for:

```
TODO
FIXME
NotImplementedError
Coming soon
placeholder
stub
hardcoded score
hardcoded URL result
fake API response
random score
eval(
exec(
```

Review matches instead of blindly deleting legitimate text.

## Performance discipline

Measure before optimizing.

Do not:
- refetch evidence unnecessarily
- duplicate SQLite records
- load huge datasets with avoidable `fetchall()`
- introduce unbounded concurrency
- perform network calls during deterministic scoring

For large-site work, document:
- pages
- requests
- duration
- memory behavior when measurable
- database size

## Security discipline

All crawled content is untrusted.

Preserve and test:
- SSRF protection
- DNS validation
- private-network blocking
- host boundaries
- redirect restrictions
- robots behavior
- origin-safe conditional requests
- cache isolation
- safe structured-data parsing
- path/output safety

Never execute JavaScript, schema values, HTML, or user-provided content as Python/system code.

## Phase discipline

Only work on the current phase unless a blocking dependency requires otherwise.

If a future idea is discovered:
1. document it,
2. add it to the appropriate future phase,
3. do not silently implement it in the current phase.

This keeps audits meaningful.

## Definition of a real completion

A phase is complete only when:

```
Implementation
+ Tests
+ Regression
+ Security
+ Determinism
+ Documentation
+ CLI verification
+ Release hygiene
+ Forensic audit
= COMPLETE
```

If one is missing, report the phase as incomplete or PASS WITH MINOR FINDINGS.

## Final agent output

At the end of substantial work, report:

- current phase
- files changed
- architecture changes
- commands added/changed
- tests run
- exact test counts
- security checks
- performance evidence
- documentation updates
- known limitations
- commit SHA if committed
- next phase

Never report completion using only "done" or "implemented".
