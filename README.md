<p align="center">
  <img src="assets/aevoraseo-banner.png" alt="AevoraSEO — evidence-first SEO, AEO, GEO and technical intelligence" width="960">
</p>

<h1 align="center">AevoraSEO</h1>

<p align="center">
  <strong>Autonomous SEO, AEO & GEO intelligence platform for modern search, answer engines, and generative discovery.</strong><br>
  Crawl the real site. Verify the evidence. Diagnose search foundations. Remediate with deterministic code patches.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111827?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.npmjs.com/package/aevoraseo"><img src="https://img.shields.io/badge/npm-aevoraseo-CB3837?style=for-the-badge&logo=npm&logoColor=white" alt="NPM Package"></a>
  <a href="https://github.com/bhedanikhilkumar-code/aevoraSEO/releases/tag/v1.1.0"><img src="https://img.shields.io/badge/release-1.1.0-2563EB?style=for-the-badge" alt="Release 1.1.0"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="package.json"><img src="https://img.shields.io/badge/node-%3E%3D16.0.0-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js 16+"></a>
  <a href="#development--testing"><img src="https://img.shields.io/badge/tests-554%20passed-16A34A?style=for-the-badge&logo=pytest&logoColor=white" alt="Test Suite: 554 passed"></a>
</p>

<p align="center">
  <a href="#quick-access">Quick Access</a> ·
  <a href="#demo-video">Demo Video</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#cli-command-reference">CLI Reference</a> ·
  <a href="#automated-remediation">Automated Remediation</a> ·
  <a href="#architecture--how-it-works">Architecture</a> ·
  <a href="#documentation">Documentation</a>
</p>

---

## ⚡ Quick Access

**Install AevoraSEO into the CLI/agent you are using.** Choose your environment below and open the master prompt. The prompt tells the agent to inspect this repository, discover the canonical `SKILL.md`, preserve **all referenced skill files/resources**, register the skill with the host's native mechanism, and verify the final installation.

> **Canonical skill repository:** `bhedanikhilkumar-code/aevoraSEO`  
> **Skill name:** `aevoraseo`  
> **Expected user invocation:** `/aevoraseo` where the host supports slash commands; otherwise use the host's native skill selector/invocation.

| CLI / Agent | Master Prompt |
|---|---|
| 🌐 **Any CLI / Agent** | [Universal Master Prompt →](docs/quick-access.md#universal-master-prompt) |
| 🧰 **GitHub CLI (`gh skill`)** | [GitHub CLI Prompt →](docs/quick-access.md#github-cli-gh-skill) |
| 📦 **`npx skills` / Skills CLI** | [`npx skills` Prompt →](docs/quick-access.md#npx-skills--skills-cli) |
| 🤖 **Claude Code** | [Claude Code Prompt →](docs/quick-access.md#claude-code) |
| 🧠 **Codex** | [Codex Prompt →](docs/quick-access.md#codex) |
| 🎨 **Cursor** | [Cursor Prompt →](docs/quick-access.md#cursor) |
| ✨ **Gemini CLI** | [Gemini CLI Prompt →](docs/quick-access.md#gemini-cli) |
| 🐙 **GitHub Copilot / Copilot CLI** | [Copilot Prompt →](docs/quick-access.md#github-copilot--copilot-cli) |
| 🚀 **Antigravity / Antigravity CLI** | [Antigravity Prompt →](docs/quick-access.md#antigravity--antigravity-cli) |
| 🔧 **Cline / OpenCode / Amp / Augment / Continue / CodeBuddy / Command Code / Cortex / Crush** | [Compatible Agents Prompt →](docs/quick-access.md#cline--opencode--amp--augment--continue--codebuddy--command-code--cortex--crush) |

### What the installation prompt guarantees

The prompt is designed around the repository itself rather than a hand-written list of files. The agent is instructed to:

1. Inspect the GitHub repository first.
2. Locate the canonical `SKILL.md` and resolve its referenced resources.
3. Install the **complete skill bundle**, not only `SKILL.md`.
4. Register the skill using the CLI/agent's supported mechanism.
5. Refresh/reload skill discovery when required.
6. Verify the skill appears in the host's real skill registry.
7. Verify the bundled docs, references, playbooks, scripts and assets are present.
8. Report the native invocation (`/aevoraseo`, `$aevoraseo`, selector, or equivalent).
9. Keep skill registration separate from crawler/runtime readiness.
10. Avoid crawling or changing a website during installation unless separately requested.

**Full copy-paste prompts:** [Open AevoraSEO Quick Access →](docs/quick-access.md)

---

## 🎥 Demo Video

> **Demo video placeholder:** the repository is ready for the final AevoraSEO demo recording. Add the finished MP4 as `assets/aevoraseo-demo.mp4` and this section can be converted into the native GitHub video player/embed.
>
> The video should demonstrate: **install skill → invoke AevoraSEO → audit a site → inspect evidence → generate report → remediation workflow → final verification**.

---

## What AevoraSEO Is

**AevoraSEO** is a professional, local-first search intelligence engine and autonomous audit toolkit. It combines an inspectable Python crawler, deterministic structured analyzers, and an automated HTML/metadata remediation engine to diagnose and improve website visibility across traditional search engines, answer engines (AEO), and generative AI discovery engines (GEO).

```text
Discover ──► Crawl ──► Capture Evidence ──► Analyze ──► Prioritize ──► Remediate ──► Verify ──► Track Progress
```

### Core Principle: Evidence First

AevoraSEO keeps observed facts separate from derived findings, recommendations, unknowns, and external outcomes. If a metric was not directly observed, it is recorded as unobserved rather than guessed.

---

## Core Capabilities

| Capability | Subsystem | Description |
|---|---|---|
| **Technical Crawling** | `crawl`, `scrape` | Multi-profile crawler with caching, ETag/304 reuse, and optional Chromium rendering |
| **Unified Audit** | `report` | Technical, content, AEO, GEO, entity, and search health reporting |
| **AEO & GEO** | `aeo`, `aeo-compare` | Answer readiness, question coverage, direct-answer proximity, AI bot accessibility |
| **Entity & Authority** | `entity`, `entity-compare` | Schema.org knowledge graph, `sameAs` footprint, consistency audits |
| **Search & Commercial** | `search`, `commercial` | Intent taxonomy, cannibalization, local NAP, and CTA audits |
| **Content Optimization** | `optimize`, `content` | Title/meta, heading hierarchy, answer boxes, topic clusters, roadmaps |
| **Backlink Verification** | `backlinks` | Source-page verification, anchor text, `rel` attributes, and context |
| **Reputation** | `reputation` | Evidence-based reputation analysis and verified-source opportunities |
| **Automated Remediation** | `remediate` | Deterministic HTML/metadata patches, diff preview, backup, rollback |
| **Progress Tracking** | `progress` | Multi-snapshot score and issue-resolution tracking |
| **Audit Verification** | `audit-verify` | Verifies whether previous recommendations persist or were resolved |
| **Branded Presentations** | `present` | Standalone HTML/PDF client deliverables |
| **Multi-Agent Runtime** | `agent` | Platform detection, adapters, and compatibility verification |
| **Runtime Diagnostics** | `doctor` | Local environment, browser dependency, and network diagnostics |

---

## Quick Start

### Prerequisites

- **Python:** `3.10+`
- **Node.js:** `>=16.0.0` (only for NPX / Node CLI usage)
- **Git:** standard installation
- **Optional:** Chromium via Playwright for JavaScript rendering

> **Repository setup:** Open the AevoraSEO repository directory in your development environment. The README intentionally does not include repository-cloning commands.

### Windows

Open **PowerShell** in the repository directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
aevoraseo --help
aevoraseo doctor
```

If PowerShell restricts script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Linux & macOS

Open a terminal in the repository directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -e .
aevoraseo --help
aevoraseo doctor
```

### NPX

```bash
npx aevoraseo doctor
npx aevoraseo crawl https://example.com --profile quick --out ./runs/quick-check
npx aevoraseo report ./runs/quick-check --format terminal
```

---

## First Audit

```bash
# Crawl evidence
aevoraseo crawl https://example.com --profile quick --out ./runs/example-baseline

# Generate unified report
aevoraseo report ./runs/example-baseline --format terminal

# Check answer and search readiness
aevoraseo aeo ./runs/example-baseline --format terminal
```

---

## CLI Command Reference

The CLI provides commands across crawling, reporting, AEO/GEO, entity intelligence, search, content, reputation, remediation, research, agents, and diagnostics.

| Command | Purpose |
|---|---|
| `crawl` | Crawl website structure and capture evidence |
| `scrape` | Inspect a single page |
| `watch` | Bounded change observation and re-crawling |
| `report` | Generate unified audit reports |
| `audit-verify` | Verify prior audit recommendations |
| `progress` | Track multi-snapshot progress |
| `present` | Generate branded HTML/PDF deliverables |
| `doctor` | Verify local runtime and dependencies |
| `browser-setup` | Manage Playwright Chromium setup |
| `readiness` | Explain search/answer readiness |
| `compare` | Compare crawl snapshots |
| `aeo` / `aeo-compare` | Analyze and compare AEO/GEO readiness |
| `entity` / `entity-compare` | Analyze and compare entities and schema |
| `search` / `search-compare` | Search intent and cannibalization analysis |
| `optimize` / `optimize-compare` | Content optimization analysis |
| `backlinks` | Verify backlink evidence |
| `reputation` / `reputation-compare` | Reputation analysis and comparison |
| `discover` | Collect bounded search leads |
| `profile` | Prepare/validate business profiles |
| `competitors` | Evaluate comparable businesses |
| `audit` | Generate actionable findings |
| `search-plan` / `search-import` | Prepare/import bounded search research |
| `edit` | Stage and apply content changes |
| `agent` | Multi-agent compatibility tooling |
| `remediate` | Generate, preview, apply, and rollback code patches |

---

## Automated Remediation

Phase K translates audit findings into deterministic, syntax-safe HTML and metadata patches:

```text
Crawl Audit ──► Generate Plan ──► Preview Diff ──► Apply ──► Verify Fix
                                                │
                                                └──► Rollback
```

Safety features include deterministic transformations, pre-flight checks, atomic backups, SHA-256 receipts, dry-run previews, and verified rollback.

```bash
aevoraseo remediate generate --crawl ./runs/snap1 --site ./my-website --out ./remediation
aevoraseo remediate preview --plan ./remediation/plan_*.json
aevoraseo remediate apply --plan ./remediation/plan_*.json --dry-run
aevoraseo remediate apply --plan ./remediation/plan_*.json
aevoraseo remediate rollback --receipt ./remediation/receipt_*.json
```

See [Remediation User Guide](docs/remediation.md) and [Methodology Reference](references/remediation-engine.md).

---

## Output Formats

AevoraSEO supports native **Terminal**, **HTML**, **Markdown**, **JSON**, and **CSV** output formats across major commands.

---

## Architecture & How It Works

```text
┌──────────────────────────────────────────────────────────────┐
│                    AevoraSEO Skill Layer                    │
│       Research • Playbooks • Strategy • Agents              │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    Native Python Engine                      │
│    CLI • Crawler • Extractor • Analyzers • Patcher           │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                      Target Website                          │
│     HTTP • DOM • Robots.txt • Sitemaps • Schema.org          │
└──────────────────────────────────────────────────────────────┘
```

---

## Safety & Boundaries

- Respects `robots.txt` by default.
- Protects against SSRF and private-network targets unless explicitly permitted.
- Enforces host boundaries and resource ceilings.
- Defends exported CSV files against formula injection.
- Keeps evidence and derived findings clearly separated.

See [Permissions Model](docs/permissions.md) and [Crawler Reference](references/crawler.md).

---

## Project Status

- **Current Version:** `v1.1.0`
- **Implementation:** Phases A through K complete and verified locally.
- **Local Test Suite:** **554 passed, 2 skipped, 22 subtests passed**.

---

## Documentation

- `README.md` — User-facing overview and CLI reference.
- `AGENT.md` — Agent operating plan and verified phase history.
- `SKILL.md` — Portable agent instructions and playbooks.
- `docs/` and `references/` — Detailed architecture, methodology, and scoring documentation.
- `docs/quick-access.md` — Copy-paste master prompts for CLI/agent skill installation.

| Area | Guide |
|---|---|
| Getting Started | [Setup Guide](docs/setup.md) |
| Agent Installation | [Quick Access & Master Prompts](docs/quick-access.md) |
| Architecture | [Architecture Reference](docs/architecture.md) |
| AEO & GEO | [AEO & GEO Methodology](references/aeo-geo.md) |
| Entity & Authority | [Entity Methodology](references/entity-authority.md) |
| Search & Commercial | [Search Intelligence](references/search-commercial.md) |
| Remediation | [Remediation User Guide](docs/remediation.md) |
| Reputation | [Reputation Methodology](references/reputation.md) |
| Multi-Agent | [Multi-Agent Guide](references/multi-agent-compatibility.md) |
| Branded Reports | [Branded Reports Guide](docs/branded-reports.md) |
| Documentation Index | [docs/README.md](docs/README.md) |

---

## Development & Testing

```bash
python -m pip install -e ".[dev,reports]"
python -m pytest tests/ -q
python scripts/check_release.py
python scripts/validate_skill.py
node bin/aevoraseo.js --help
node bin/aevoraseo.js version
```

---

## Contributing, Security & Privacy

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

Engineering rules:

- **Evidence First** — Findings cite observable evidence.
- **Deterministic Core** — Identical inputs produce reproducible results.
- **Zero Stub Policy** — No production placeholder stubs.
- **Privacy by Default** — Never commit API keys, credentials, cookies, or client datasets.

For security disclosures, see [SECURITY.md](SECURITY.md).

---

## License

AevoraSEO is open-source software licensed under the **MIT License**.

See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

## Maintainer & Connect

**Bheda Nikhilkumar**  
Engineering Student · Software Development
