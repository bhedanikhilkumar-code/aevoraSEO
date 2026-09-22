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

Do not regress or silently remove these Phase B controls.

---

## 3. CURRENT PHASE

### Phase C — AEO/GEO Intelligence
**STATUS: NEXT / NOT YET VERIFIED COMPLETE**

This is the next implementation phase.

Required areas:
- answer readiness
- question/intent coverage
- direct-answer detection
- entity clarity
- citation/source readiness
- structured-data intelligence
- AI crawler/bot accessibility
- content extractability
- semantic structure
- transparent AEO/GEO scoring
- confidence and evidence models
- snapshot-aware AEO/GEO comparisons
- SQLite persistence
- CLI commands
- terminal/JSON/CSV/Markdown reports
- deterministic tests
- adversarial/security tests

Critical boundary:

```
Observed Evidence
      ↓
Derived Signals
      ↓
Predicted Readiness

DO NOT present predicted readiness as actual AI visibility.
```

Do not claim rankings, citations, recommendations, or visibility in ChatGPT, Google AI, Gemini, Perplexity, or other answer engines unless real external measurements are supplied.

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
**NEXT**

Answer readiness, question/intent coverage, direct answers, entity clarity, citation readiness, schema intelligence, AI crawler accessibility, extraction quality, transparent scoring, and snapshot comparison.

## Phase D — Backlink & Reputation Intelligence
**PLANNED**

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

## PHASE C — AEO/GEO INTELLIGENCE

Start by inspecting:
- current `src/aevoraseo/`
- `engine.py`
- `network.py`
- `review.py`
- `cli.py`
- SQLite snapshot schema
- existing schema/entity extraction
- existing reports
- current tests
- `SKILL.md`
- `references/capabilities.md`
- `docs/agent-installation.md`

Then implement Phase C according to the Phase C Master Prompt.

Do not begin Phase D backlink work until Phase C has passed its full verification and forensic audit.

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
| C | AEO/GEO Intelligence | NEXT |
| D | Backlinks & Reputation Intelligence | PLANNED |
| E | Entity & Authority Intelligence | PLANNED |
| F | Search / Local / Commercial Intelligence | PLANNED |
| G | Content & Optimization Intelligence | PLANNED |
| H | Multi-Agent / CLI Ecosystem | PLANNED |
| I | Reporting & Operations | PLANNED |
| J | Production Hardening & Release | PLANNED |

**Rule:** Do not skip phases without documenting why.
