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

## 3. CURRENT PHASE

### Phase D — Backlink & Reputation Intelligence
**STATUS: NEXT / READY FOR IMPLEMENTATION**

Phase C has passed all verification gates and forensic audits. Phase D is the next implementation phase.

Required areas:
- native backlink discovery model
- verified backlinks vs. page mentions
- source classification (editorial, directory, profile, community, owned)
- ownership vs. independent proof
- referring-domain evidence and anchor context
- link status, target reachability, and rel attributes (nofollow, ugc, sponsored)
- conservative reputation scoring with confidence intervals
- backlink opportunity tracking and catalog shortlist integration
- snapshot-aware before/after reputation comparisons
- SQLite persistence for backlink and mention observations
- deterministic and adversarial tests

Critical boundary:
- Do not pretend to be a whole-web commercial backlink index.
- Search snippets are leads, not verified backlinks.
- Never extrapolate whole-web totals from a sample.

---

# 4. LONG-TERM ROADMAP

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
**NEXT**

Build a native evidence model for:
- backlink discovery
- verified backlinks
- page mentions
- source classification
- ownership vs independent sources
- referring-domain evidence
- anchor/context evidence
- link status and verification
- reputation evidence
- conservative reputation scoring
- opportunity tracking
- source quality and confidence
- before/after reputation comparisons

Do not pretend to be a commercial whole-web backlink index.

## Phase E — Entity, Authority & Knowledge Intelligence
**PLANNED**

Build:
- organization identity
- brand/entity consistency
- person/product/service/place entities
- sameAs relationships
- organization/publisher/author relationships
- entity conflicts
- authority evidence
- topical authority signals
- first-party vs independent proof
- entity graph stored from observed evidence
- entity changes across snapshots

Do not invent knowledge-graph facts.

## Phase F — Search, Local & Commercial Intelligence
**PLANNED**

Build evidence-driven analysis for:
- search intent
- keyword/query mapping
- local visibility signals
- business/service/location relationships
- commercial investigation pages
- comparison pages
- buyer questions
- conversion journeys
- local business evidence
- sitemap/content coverage

Actual search rankings remain external measurements unless supplied.

## Phase G — Content & Optimization Intelligence
**PLANNED**

Turn findings into actionable, verified work:
- title/meta improvements
- headings
- answer blocks
- FAQ opportunities
- internal-link plans
- schema recommendations
- content briefs
- content gap analysis
- refresh plans
- 30/60/90-day roadmaps
- acceptance checks

Never invent business facts.

## Phase H — Shopper / Multi-Agent Platform Compatibility
**PLANNED**

The product must work consistently across the agent/CLI environments shown in the project compatibility target.

Target environments from the current project setup:

1. Agent
2. aider
3. cai
4. Copilot CLI
5. droid
6. Gemini CLI
7. JCODE
8. jcode CLI
9. juni CLI
10. Kilocode CLI
11. Kiro
12. OpenCode CLI
13. prime-agent
14. Qwen

Compatibility must be evidence-based.

For each target, maintain:
- installation route
- skill/agent file location if applicable
- runtime requirements
- CLI invocation
- workspace behavior
- Python/runtime discovery
- crawler readiness
- browser readiness
- permission requirements
- smoke test
- known limitations

Do not claim a host is supported merely because it can read Markdown.

A host is only marked verified after a real installation or fixture-based compatibility test proves the required workflow.

## Phase I — Reporting, Operations & Professional Workflow
**PLANNED**

Unify:
- client reports
- HTML/PDF/Markdown/JSON/CSV outputs
- evidence tables
- priorities
- acceptance checks
- snapshot history
- change review
- operational diagnostics
- safe approved website changes
- audit/review loops

## Phase J — Production Hardening & Release
**PLANNED**

Finalize:
- security review
- performance benchmarks
- large-site behavior
- migration compatibility
- CLI parity
- cross-platform checks
- package validation
- documentation
- release automation
- reproducibility
- forensic audit
- final public release readiness

---

# 5. PHASE DEPENDENCY ORDER

Do not skip architectural dependencies.

```
A  COMPLETE
 ↓
B  COMPLETE
 ↓
C  AEO/GEO
 ↓
D  Backlinks + Reputation
 ↓
E  Entity + Authority
 ↓
F  Search + Local + Commercial
 ↓
G  Content + Optimization
 ↓
H  Multi-Agent / CLI Ecosystem
 ↓
I  Reporting + Operations
 ↓
J  Production Release
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

The agent must NOT jump randomly between future phases.

The next implementation target is:

## PHASE D — BACKLINK & REPUTATION INTELLIGENCE

Start by inspecting:
- current `src/aevoraseo/`
- `backlinks.py`
- `reputation.py`
- `discovery.py`
- `deep_research.py`
- `review.py`
- `cli.py`
- SQLite snapshot and AEO persistence schemas
- existing backlink catalog `docs/backlink-source-catalog.md` and `scripts/backlink_sources.py`
- current tests (`tests/test_reputation.py`, `tests/test_posting_catalog.py`, `tests/test_deep_research.py`, `tests/test_discovery_research.py`)
- `references/reputation.md`
- `references/measurement-boundaries.md`

Then implement Phase D according to the Phase D specification:
1. Native backlink discovery and verification model.
2. Verified backlinks vs unverified page mentions.
3. Source classification (editorial, directory, profile, community, owned).
4. Ownership vs independent proof.
5. Referring-domain evidence and anchor context.
6. Link status, target reachability, and rel attributes (nofollow, ugc, sponsored).
7. Conservative reputation scoring with confidence intervals.
8. Backlink opportunity tracking and catalog shortlist integration.
9. Snapshot-aware before/after reputation comparisons.
10. SQLite persistence for backlink and mention observations.
11. Deterministic and adversarial tests.

Do not begin Phase E entity graph work until Phase D has passed its full verification and forensic audit.

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
| D | Backlinks & Reputation Intelligence | NEXT |
| E | Entity & Authority Intelligence | PLANNED |
| F | Search / Local / Commercial Intelligence | PLANNED |
| G | Content & Optimization Intelligence | PLANNED |
| H | Multi-Agent / CLI Ecosystem | PLANNED |
| I | Reporting & Operations | PLANNED |
| J | Production Hardening & Release | PLANNED |

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
