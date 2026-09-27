<div align="center">

```text
   █████╗ ███████╗██╗   ██╗ ██████╗ ██████╗  █████╗ ███████╗███████╗ ██████╗ 
  ██╔══██╗██╔════╝██║   ██║██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗
  ███████║█████╗  ██║   ██║██║   ██║██████╔╝███████║███████╗█████╗  ██║   ██║
  ██╔══██║██╔══╝  ╚██╗ ██╔╝██║   ██║██╔══██╗██╔══██║╚════██║██╔══╝  ██║   ██║
  ██║  ██║███████╗ ╚████╔╝ ╚██████╔╝██║  ██║██║  ██║███████║███████╗╚██████╔╝
  ╚═╝  ╚═╝╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ 
```

### **Autonomous SEO, AEO & GEO Intelligence Platform**
*The professional evidence-first search intelligence engine, local web crawler, and automated code remediation toolkit.*

[![NPM Version](https://img.shields.io/npm/v/aevoraseo?style=for-the-badge&color=CB3837&logo=npm)](https://www.npmjs.com/package/aevoraseo)
[![PyPI Version](https://img.shields.io/pypi/v/aevoraseo?style=for-the-badge&color=3776AB&logo=pypi&logoColor=white)](https://pypi.org/project/aevoraseo/)
[![Release](https://img.shields.io/badge/release-1.1.0-2563EB?style=for-the-badge&logo=github)](https://github.com/bhedanikhilkumar-code/aevoraSEO/releases/tag/v1.1.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-111827?style=for-the-badge)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](pyproject.toml)
[![Node >= 16](https://img.shields.io/badge/node-%3E%3D16.0.0-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](package.json)
[![Tests Passed](https://img.shields.io/badge/tests-554%20passed-16A34A?style=for-the-badge&logo=pytest&logoColor=white)](#tests--quality-assurance)
[![Zero API Keys](https://img.shields.io/badge/API_Keys-Zero_Required-16A34A?style=for-the-badge)](docs/setup.md)

<p align="center">
  <a href="#-quick-start-zero-setup">Quick Start</a> •
  <a href="#-installation-matrix">Installation</a> •
  <a href="#-add-to-ai-agents--clis-skill-setup">AI Agent & CLI Skill</a> •
  <a href="#-core-intelligence-pillars">7 Pillars</a> •
  <a href="#-step-by-step-workflows">Workflows</a> •
  <a href="#-automated-code-remediation-phase-k">Remediation</a> •
  <a href="#-full-cli-command-reference">CLI Reference</a> •
  <a href="#-documentation-hub">Docs</a>
</p>

---

</div>

## 🌐 Overview

**AevoraSEO** is a developer-first, local-first search intelligence engine designed for modern web architects, growth engineers, and AI coding agents. It unifies **traditional technical SEO**, **Answer Engine Optimization (AEO)**, **Generative Engine Optimization (GEO)**, and **deterministic code patching** into a single autonomous workflow.

Unlike cloud-based SEO platforms that hide their calculations behind proprietary black-boxes and charge hundreds of dollars per month, AevoraSEO runs **directly on your machine**:
* **100% Free & Open Source (MIT)** — Zero subscriptions, zero third-party API keys required.
* **Direct Observable Evidence** — Inspects real HTTP response headers, robots directives, HTML AST, Schema.org entities, and backlink source pages.
* **Closed-Loop Execution** — Crawl ➔ Diagnose ➔ Generate Code Patches ➔ Preview Unified Diffs ➔ Apply with Atomic Backup ➔ Verify Resolution.

```text
 ┌──────────┐     ┌───────────┐     ┌─────────────┐     ┌────────────┐     ┌────────────┐
 │  Crawl   │ ──► │  Capture  │ ──► │  Diagnose   │ ──► │ Code Patch │ ──► │   Verify   │
 │ Target   │     │ Evidence  │     │ SEO/AEO/GEO │     │  (Phase K) │     │ Resolution │
 └──────────┘     └───────────┘     └─────────────┘     └────────────┘     └────────────┘
```

---

## ⚡ Quick Start (Zero Setup)

You do **not** need to clone the repository or manually manage dependencies. Run AevoraSEO instantly from your terminal using your preferred package runner:

### 🚀 Instant Run via Node / JavaScript Ecosystem

```bash
# Using NPX (npm runner - built into Node.js)
npx aevoraseo doctor
npx aevoraseo crawl https://example.com --profile quick --out ./runs/audit1
npx aevoraseo report ./runs/audit1 --format terminal

# Using Bun (instant start, ultra fast)
bunx aevoraseo doctor
bunx aevoraseo crawl https://example.com --profile quick --out ./runs/audit1

# Using PNPM
pnpm dlx aevoraseo doctor

# Using Yarn
yarn dlx aevoraseo doctor
```

### 🐍 Instant Run via Python Ecosystem

```bash
# Using uvx (Astral UV runner - blazing fast)
uvx aevoraseo doctor
uvx aevoraseo crawl https://example.com --profile quick --out ./runs/audit1

# Using pipx (isolated application runner)
pipx run aevoraseo doctor
```

---

## 📦 Installation Matrix

Install AevoraSEO globally to use the `aevoraseo` command everywhere in any terminal, script, or CI pipeline:

### Option 1: Global Package Managers (NPM / PNPM / Bun / Yarn)

Choose your tool of choice:

```bash
# NPM
npm install -g aevoraseo

# PNPM
pnpm add -g aevoraseo

# Bun
bun add -g aevoraseo

# Yarn
yarn global add aevoraseo
```

Verify your installation:
```bash
aevoraseo --version
aevoraseo doctor
```

### Option 2: Python Package Managers (pip / pipx / uv)

```bash
# Modern UV tool install (Recommended for Python users)
uv tool install aevoraseo

# Isolated pipx install
pipx install aevoraseo

# Standard pip install
pip install aevoraseo
```

---

## 🤖 Add to AI Agents & CLIs (Skill Setup)

AevoraSEO is built from the ground up to empower **AI Coding Agents**, **terminal assistants**, and **agentic IDEs**. You can register AevoraSEO as a native skill right from your terminal without editing complex JSON files.

For prompt-based installation across all environments, see the [Quick Access Installation Hub](docs/quick-access.md).

### 1. Auto-Detect Your Active Environment

AevoraSEO inspects your active workspace, config directories, and running shells to detect supported platforms:

```bash
npx aevoraseo agent detect
# or
aevoraseo agent detect
```

### 2. List Supported Platforms

AevoraSEO natively supports **18 AI agent & CLI platforms**:

```bash
aevoraseo agent list
```

| Platform | Tier | Invocation | Config Path |
|---|---|---|---|
| **Claude Code** | First-Party Skill | `/aevoraseo` | `~/.claude/skills/aevoraseo/` |
| **Cursor / Windsurf** | Agent Rules & Tools | Terminal / Rules | `.agents/` or workspace rules |
| **Codex** | First-Party Skill | `$aevoraseo` | `~/.agents/skills/aevoraseo/` |
| **Gemini CLI / Antigravity** | Agent Skill | Terminal / Skill | `~/.gemini/skills/aevoraseo/` |
| **OpenClaw** | Workspace Tool | Prompt / Tool | `~/.openclaw/skills/aevoraseo/` |
| **Hermes** | Profile Skill | Profile / Skill | `~/.hermes/skills/aevoraseo/` |
| **Aider** | Command-Line | Terminal / Repo map | `.aider/` |
| **GitHub Copilot CLI** | Agent Integration | `@copilot` | `.github/` |
| **Qwen / KiloCode / Droid** | Native Adapters | CLI / Skill | Custom toolpaths |

### 3. Setup Skill in One Terminal Command

Automatically generate and wire up the skill adapter for your target platform:

```bash
# For Claude Code
aevoraseo agent adapt claude-code

# For Codex / ChatGPT Work
aevoraseo agent adapt codex

# For Gemini / Antigravity IDE
aevoraseo agent adapt gemini

# For OpenClaw
aevoraseo agent adapt openclaw

# For Cursor / VS Code (Current Project Workspace)
aevoraseo agent adapt cursor --workspace .
```

### 4. Verify Platform Compatibility

Run fixture-based verification to ensure the agent environment can execute crawls and read evidence:

```bash
aevoraseo agent verify --host claude-code
```

> [!TIP]
> Once installed as a skill, you can tell your AI assistant:
> *"Audit this website for AEO answer readiness and fix missing meta tags."*
> The agent will leverage AevoraSEO CLI commands, inspect the JSON output, and apply verified code patches autonomously.

---

## 🏛️ Core Intelligence Pillars

AevoraSEO evaluates websites across seven interconnected dimensions:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          AevoraSEO Intelligence Suite                           │
├─────────────────┬─────────────────┬──────────────────┬──────────────────────────┤
│ 1. SEO          │ 2. AEO          │ 3. GEO           │ 4. Entity & Authority    │
│ Technical crawl,│ Direct answers, │ Factual density, │ Schema knowledge graph,  │
│ status codes,   │ question intent,│ citation readiness, sameAs footprint,       │
│ metadata, links │ bot access      │ extractability   │ consistency audits       │
├─────────────────┴─────────────────┼──────────────────┴──────────────────────────┤
│ 5. Reputation & Backlinks         │ 6. Search & Commercial Intelligence         │
│ Verified sources, anchor context, │ Intent taxonomy, keyword cannibalization,   │
│ conservative evidence scoring     │ local NAP visibility, CTA friction audits   │
├───────────────────────────────────┴─────────────────────────────────────────────┤
│ 7. Automated Remediation (Phase K)                                              │
│ Deterministic AST/HTML code patches, unified diffs, atomic backups & rollback   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Traditional Technical SEO
Deep-crawls link topology, HTTP status codes, redirects, canonical tags, `robots.txt`, XML sitemaps, title tags, meta descriptions, image alt attributes, and detects orphan pages.

### 2. AEO (Answer Engine Optimization)
Evaluates whether your content directly answers user questions in conversational search. Audits 40–60 word answer boxes, question headings (`H2`/`H3`), procedural step-lists, and crawler permissions across **10 major AI bots** (GPTBot, ClaudeBot, PerplexityBot, Applebot-Extended, Google-Extended, etc.).

### 3. GEO (Generative Engine Optimization)
Measures factual density, citation extractability, authoritative author bylines, publication timestamps, and structured knowledge representations that AI search models (SearchGPT, Perplexity, Gemini, Google SGE) require to reference your site as a primary source.

### 4. Entity & Knowledge Graph Intelligence
Extracts Schema.org models (`Organization`, `Person`, `Product`, `LocalBusiness`, `Article`), analyzes `sameAs` authority links (Wikidata, Wikipedia, LinkedIn, Crunchbase), and flags cross-page entity conflicts (conflicting telephone numbers, mismatched business names, broken social footprints).

### 5. Reputation & Backlinks
Verifies backlinks through direct source-page inspection. Evaluates anchor text, link rels (`dofollow`, `nofollow`, `ugc`, `sponsored`), and surrounding 160-character sentence context. Separates owned web profiles from genuine third-party editorial citations.

### 6. Search Intent & Commercial Friction
Classifies query intent (Informational, Commercial, Transactional, Navigational, Local), detects internal keyword cannibalization via token similarity algorithms, validates local NAP consistency, and audits conversion CTA visibility.

### 7. Automated Remediation Engine (Phase K)
Translates audit findings into deterministic, syntax-safe HTML and metadata code patches with unified diff previews, pre-flight safety checks, atomic backups, and instant rollback.

---

## 🚀 Step-by-Step Workflows

### Step 1: Run a Technical Crawl

Collect full diagnostic evidence from a target website:

```bash
# Fast crawl (25 pages, standard rate limits)
aevoraseo crawl https://example.com --profile quick --out ./runs/site-baseline

# Full crawl with subdomains & deep link discovery
aevoraseo crawl https://example.com --profile deep --include-www --out ./runs/site-deep
```

*What happens:* AevoraSEO respects `robots.txt`, captures exact HTTP headers, saves full HTML snapshots, builds a link graph, and stores results in `./runs/site-baseline/crawl.sqlite3` and `pages.jsonl`.

---

### Step 2: Generate Unified Client Audit

Synthesize technical, content, entity, AEO, and GEO findings into a scored report:

```bash
# Colorized terminal summary
aevoraseo report ./runs/site-baseline --format terminal

# Export an executive branded HTML report
aevoraseo report ./runs/site-baseline --format html --out ./deliverables

# Export machine-readable JSON for CI/CD
aevoraseo report ./runs/site-baseline --format json --out ./deliverables
```

Inspect `./deliverables/audit-report.html` in your browser for interactive scorecards, issue severity breakdown (P0 / P1 / P2), and prioritized action items.

---

### Step 3: Analyze AEO & AI Bot Readiness

Check how answer engines perceive your content:

```bash
aevoraseo aeo ./runs/site-baseline --format terminal
```

*Outputs:*
* AI Bot Accessibility Matrix (which LLMs are blocked in `robots.txt` vs allowed)
* Answer Box Candidate Coverage (percentage of questions with clear 40–60 word answer paragraphs)
* Heading Question Ratio (`H2`/`H3` query-matching percentage)

---

### Step 4: Extract Schema.org Entity Knowledge Graph

```bash
aevoraseo entity ./runs/site-baseline --brand "My Brand" --format terminal
```

*Outputs:*
* Extracted typed Schema.org entities (`Organization`, `WebSite`, `FAQPage`, etc.)
* Detected cross-page schema discrepancies
* `sameAs` entity footprint verification

---

### Step 5: Detect Keyword Cannibalization

```bash
aevoraseo search ./runs/site-baseline --format terminal
```

*Outputs:*
* Page intent classification table
* Keyword conflict warnings where multiple URLs compete for identical search intents

---

## 🛠️ Automated Code Remediation (Phase K)

AevoraSEO does not just give you a checklist of problems — it can **fix them directly in your codebase** with military-grade safety.

```text
Audit Findings ──► Generate Plan ──► Preview Diff ──► Dry Run ──► Apply (Atomic Backup) ──► Verify
                                                                        │
                                                                        └──► Rollback (1-Click)
```

### Remediation Workflow

```bash
# 1. Generate code patch plan from crawl evidence targeting your local site folder
aevoraseo remediate generate --crawl ./runs/site-baseline --site ./my-website-code --out ./remediation

# 2. Preview colorized unified diffs (inspect exact changes before applying)
aevoraseo remediate preview --plan ./remediation/plan_*.json

# 3. Dry-run test (simulates patch application without touching disk)
aevoraseo remediate apply --plan ./remediation/plan_*.json --dry-run

# 4. Apply patches to disk with automatic atomic backup
aevoraseo remediate apply --plan ./remediation/plan_*.json

# 5. Rollback at any time if needed
aevoraseo remediate rollback --receipt ./remediation/receipt_*.json
```

### Safety Guarantees
* **Deterministic AST HTML Transformations** — Powered by BeautifulSoup parser; never corrupts unclosed tags or attributes.
* **Cryptographic Digests** — SHA-256 hashes recorded for every file pre- and post-patch in `receipt.json`.
* **Atomic Pre-Patch Backups** — Original byte copies saved to `.aevora/backups/` before any write operation.
* **Instant Rollback** — Guaranteed restoration to the exact pre-patch byte state.

---

## 📋 Full CLI Command Reference

AevoraSEO provides 36 public commands and subcommands:

| Command | Category | Description | Example Syntax |
|---|---|---|---|
| `crawl` | Crawler | Crawl website structure and capture raw evidence | `aevoraseo crawl <url> --out <dir> [--profile quick\|deep]` |
| `scrape` | Crawler | Inspect and capture a single web page | `aevoraseo scrape <url> --out <dir> [--mode browser]` |
| `watch` | Monitoring | Bounded change observation and re-crawling | `aevoraseo watch <url> --out <dir> --interval 3600` |
| `compare` | Crawler | Diff two crawl snapshots (added, changed, removed) | `aevoraseo compare --before <dir1> --after <dir2>` |
| `report` | Reporting | Generate unified audit report (Terminal, HTML, JSON, CSV) | `aevoraseo report <crawl-dir> --format html --out <dir>` |
| `aeo` | AEO / GEO | Analyze answer readiness and AI bot access matrix | `aevoraseo aeo <crawl-dir> --format terminal` |
| `aeo-compare` | AEO / GEO | Track AEO score progression between snapshots | `aevoraseo aeo-compare --before <d1> --after <d2>` |
| `entity` | Entity Graph | Extract Schema.org entities and authority graph | `aevoraseo entity <crawl-dir> --format terminal` |
| `entity-compare`| Entity Graph | Compare entity evolution and resolved conflicts | `aevoraseo entity-compare --before <d1> --after <d2>` |
| `search` | Commercial | Analyze query intent, cannibalization & CTA friction | `aevoraseo search <crawl-dir> --format terminal` |
| `commercial` | Commercial | Alias for `search` | `aevoraseo commercial <crawl-dir>` |
| `search-compare`| Commercial | Compare search intent shifts across crawls | `aevoraseo search-compare --before <d1> --after <d2>` |
| `optimize` | Content | Content quality, titles, headings, and answer boxes | `aevoraseo optimize <crawl-dir> --format terminal` |
| `content` | Content | Alias for `optimize` | `aevoraseo content <crawl-dir>` |
| `optimize-compare`| Content | Compare content scores and resolved deficiencies | `aevoraseo optimize-compare --before <d1> --after <d2>` |
| `remediate` | Remediation | Automated code patching: generate, preview, apply, rollback | `aevoraseo remediate generate --crawl <c> --site <s>` |
| `audit-verify` | Verification| Verify if audit recommendations were fixed in new crawl | `aevoraseo audit-verify --audit <a.json> --crawl <dir>` |
| `progress` | Trajectory | Multi-snapshot score tracking over historical crawls | `aevoraseo progress --crawls <s1> <s2> <s3>` |
| `backlinks` | Reputation | Inspect source pages for backlinks and anchor context | `aevoraseo backlinks <domain> --sources <file.csv>` |
| `reputation` | Reputation | Calculate evidence-based reputation score (0–100) | `aevoraseo reputation <domain> --sources <file.csv>` |
| `reputation-compare`| Reputation | Compare reputation snapshots for gained/lost links | `aevoraseo reputation-compare --before <r1> --after <r2>` |
| `present` | Deliverables| Export standalone branded client deliverables | `aevoraseo present --input <report.json> --format html` |
| `agent` | Multi-Agent | Platform integration: `detect`, `list`, `inspect`, `adapt`, `verify` | `aevoraseo agent detect`, `aevoraseo agent adapt <host>` |
| `doctor` | Diagnostics | Validate local runtime, Playwright & network health | `aevoraseo doctor [--target <url>]` |
| `browser-setup`| Diagnostics | Download & configure Playwright Chromium browser | `aevoraseo browser-setup` |
| `version` | Info | Print current CLI version | `aevoraseo version` |

---

## 📊 Output Formats & Deliverables

Every major command supports multiple output formats via `--format <type>`:

* **Terminal (`--format terminal`)** — Interactive, colorized tables with clear status indicators (`PASS`, `WARN`, `FAIL`).
* **HTML (`--format html`)** — Executive-ready, standalone, mobile-responsive client presentation with interactive filtering.
* **JSON (`--format json`)** — Strict schema contracts designed for CI/CD pipelines and automated agent parsing.
* **Markdown (`--format markdown`)** — Formatted markdown summaries ready for GitHub PR descriptions or documentation.
* **CSV (`--format csv`)** — Spreadsheets protected with formula injection defenses against `=`, `+`, `-`, `@`, `\t`, and `\r` vectors.

---

## 🛡️ Security, Privacy & Guardrails

AevoraSEO is built for enterprise safety:

* **SSRF & Private Network Defense** — Rejects loopback (`127.0.0.1`), link-local (`169.254.x.x`), and private RFC 1918 subnets (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`) by default.
* **Strict Host Boundaries** — Crawler never leaves target domain boundaries unless explicitly allowed via `--allow-host`.
* **Robots Directives Respect** — Respects `robots.txt` disallow rules and crawl delays by default.
* **Spreadsheet Formula Sanitization** — All exported CSVs are sanitized against formula execution vulnerabilities.
* **Resource Quotas** — 5 MB response size limits, request timeouts, and maximum page ceilings prevent memory exhaustion.
* **Zero Telemetry / Privacy by Default** — AevoraSEO never transmits your crawled data, audit findings, or codebase back to any remote analytics server.

---

## 🧪 Tests & Quality Assurance

AevoraSEO maintains an uncompromising standard for engineering stability:

* **554 Passed Tests**, 2 skipped, 22 subtests across unit, integration, and adversarial suites.
* **Deterministic Core** — Identical inputs yield identical outputs.
* **Zero Stub Policy** — No placeholder `TODO`, `FIXME`, or `NotImplementedError` stubs in production paths.

To run the local test suite:

```bash
# Run pytest test suite
python -m pytest tests/ -q
```

---

## 📚 Documentation Hub

Explore deep architectural guides and methodology references:

| Guide | Link | Description |
|---|---|---|
| **Quick Access Skill Hub** | [docs/quick-access.md](docs/quick-access.md) | Universal master prompts and copy-paste skill installation |
| **Environment Setup** | [docs/setup.md](docs/setup.md) | Python, Node.js, and optional Chromium setup |
| **Agent Installation** | [docs/agent-installation.md](docs/agent-installation.md) | Wiring AevoraSEO into 18 AI coding agents |
| **AEO & GEO Methodology** | [references/aeo-geo.md](references/aeo-geo.md) | Answer readiness criteria, scoring formulas & bot matrix |
| **Entity & Authority** | [references/entity-authority.md](references/entity-authority.md) | Knowledge graph parsing & conflict resolution |
| **Search Intelligence** | [references/search-commercial.md](references/search-commercial.md) | Intent taxonomy, query extraction & cannibalization |
| **Remediation Guide** | [docs/remediation.md](docs/remediation.md) | Automated code patching, diffs & rollback |
| **Reputation Scoring** | [references/reputation.md](references/reputation.md) | Evidence-based reputation calculation |
| **Permissions Model** | [docs/permissions.md](docs/permissions.md) | Security constraints, SSRF & network boundaries |
| **Branded Reports** | [docs/branded-reports.md](docs/branded-reports.md) | Customizing executive HTML/PDF client deliverables |
| **Documentation Index**| [docs/README.md](docs/README.md) | Complete documentation directory |

---

## 🤝 Contributing

Contributions are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and review [SECURITY.md](SECURITY.md) before submitting a pull request.

---

## 📄 License

AevoraSEO is open-source software licensed under the **MIT License**. See [LICENSE](LICENSE) for full details.

---

## 👤 Maintainer

**Bheda Nikhilkumar**  
*Software Engineer & Creator of AevoraSEO*

* **GitHub:** [@bhedanikhilkumar-code](https://github.com/bhedanikhilkumar-code)
* **LinkedIn:** [Bheda Nikhilkumar](https://www.linkedin.com/in/bhedanikhilkumar)
* **Portfolio:** [bhedanikhilkumar-portfolio](https://github.com/bhedanikhilkumar-code/Bheda-Nikhilkumar-portfolio)
* **Contact:** [bhedanikhilkumarpro@gmail.com](mailto:bhedanikhilkumarpro@gmail.com)

<div align="center">
  <sub>Built with precision for the modern search and answer era. Evidence first. Clear reasoning. Better websites.</sub>
</div>
