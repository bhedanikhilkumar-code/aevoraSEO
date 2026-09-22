# Multi-Agent & Platform Compatibility Reference

Technical methodology and compatibility matrix for AevoraSEO across AI/coding agent environments.

---

## Compatibility Architecture

AevoraSEO uses a two-layer compatibility model:

### Layer 1 — Native CLI

The core engine runs through:

```bash
python scripts/run.py <command>     # Direct Python
node bin/aevoraseo.js <command>     # Node wrapper
aevoraseo <command>                 # npx/global install
```

### Layer 2 — Agent/Skill Integration

Agent environments integrate through thin adapters:

1. **First-party skill** — Native skill folder recognized by the host (Claude Code, Codex, Hermes, OpenClaw, Agent/ChatGPT Work).
2. **Project instruction** — Markdown or YAML file read by the host as workspace context (aider, Copilot, Gemini CLI, Kiro).
3. **CLI integration** — Command-line invocation with skill folder conventions (Kilocode, OpenCode, Qwen, JCODE, juni, prime-agent, cai).

All integrations invoke the same Python engine. No engine logic is duplicated.

---

## Compatibility Matrix

| Platform | Tier | Install Route | Skill / Config Location | Invocation | Status |
|---|---|---|---|---|---|
| Agent (ChatGPT Work) | First-party skill | Upload bundle or `install_skill.py --host agent` | Skills list | `@aevoraseo` | DOCUMENTED |
| Claude Code | First-party skill | `install_skill.py --host claude-code` | `~/.claude/skills/aevoraseo/` | `/aevoraseo` | VERIFIED |
| Codex | First-party skill | `install_skill.py --host codex` | `~/.agents/skills/aevoraseo/` | `$aevoraseo` | VERIFIED |
| Hermes Agent | First-party skill | `install_skill.py --host hermes` | `~/.hermes/skills/aevoraseo/` | `/aevoraseo` | VERIFIED |
| OpenClaw | First-party skill | `install_skill.py --host openclaw` | `~/.openclaw/skills/aevoraseo/` | `openclaw skills list` | VERIFIED |
| aider | Project instruction | Copy `.aider.conf.yml` | `.aider.conf.yml` | `aider --read SKILL.md` | DOCUMENTED |
| Copilot CLI | Project instruction | Copy `.github/copilot-instructions.md` | `.github/copilot-instructions.md` | `@workspace` | DOCUMENTED |
| Gemini CLI | Project instruction | Copy `GEMINI.md` or `.gemini/` | `GEMINI.md` | `gemini` | DOCUMENTED |
| droid | Project instruction | Copy `.factory/skills/aevoraseo/` | `.factory/skills/aevoraseo/` | `droid invoke` | NOT VERIFIED |
| Kilocode CLI | CLI integration | Copy `.kilocode/skills/aevoraseo/` | `.kilocode/skills/aevoraseo/` | `kilocode skill` | NOT VERIFIED |
| OpenCode CLI | CLI integration | Copy `.opencode/skills/aevoraseo/` | `.opencode/skills/aevoraseo/` | `opencode skill` | NOT VERIFIED |
| Qwen | CLI integration | Copy `.qwen/skills/aevoraseo/` | `.qwen/skills/aevoraseo/` | `qwen skill` | NOT VERIFIED |
| JCODE | CLI integration | Register in JCODE IDE | `.jcode/skills/aevoraseo/` | IDE skill picker | NOT VERIFIED |
| jcode CLI | CLI integration | Copy `.jcode/skills/` | `.jcode/skills/aevoraseo/` | `jcode skill` | NOT VERIFIED |
| juni CLI | CLI integration | Copy `.juni/skills/aevoraseo/` | `.juni/skills/aevoraseo/` | `juni skill` | NOT VERIFIED |
| Kiro | Project instruction | Copy `.kiro/skills/aevoraseo/` | `.kiro/skills/aevoraseo/` | Workspace instructions | NOT VERIFIED |
| prime-agent | CLI integration | Copy `.prime/skills/aevoraseo/` | `.prime/skills/aevoraseo/` | `prime-agent skill` | NOT VERIFIED |
| cai | CLI integration | Copy `.cai/skills/aevoraseo/` | `.cai/skills/aevoraseo/` | `cai skill` | NOT VERIFIED |

---

## Verification Status Definitions

| Status | Meaning |
|---|---|
| **VERIFIED** | Fixture-based installation, detection, and doctor smoke test confirmed. |
| **PARTIAL** | Some verification steps passed; others require manual confirmation. |
| **DOCUMENTED** | Platform-specific instructions exist; no fixture or live verification performed. |
| **NOT VERIFIED** | Platform is in the target list; no verification evidence exists yet. |
| **UNSUPPORTED** | Platform investigated and determined incompatible. |

A host is only marked VERIFIED after a real installation or fixture-based compatibility test proves the required workflow. Reading documentation alone does not establish verified status.

---

## Environment Detection

The `aevoraseo agent detect` command inspects:

1. **Environment variables** — Platform-specific vars (`HERMES_HOME`, `OPENCLAW_STATE_DIR`, `CLAUDE_HOME`).
2. **Workspace marker files** — Config directories (`.claude/`, `.agents/`, `.hermes/`, `.aider.conf.yml`).
3. **Global config paths** — User-level skill folders (`~/.claude/skills/`, `~/.hermes/skills/`).
4. **Python runtime** — Version check (≥ 3.10) and executable path.
5. **Install receipts** — `aevoraseo-install.json` file integrity verification.

Detection priority: environment variables → workspace markers → global paths.

---

## Non-Destructive Execution Contract

All compatibility operations follow these safety rules:

1. **No host mutation** — Detection and verification never modify host configuration files.
2. **Adapter safety** — Adapter generation refuses to overwrite existing config files without explicit confirmation.
3. **Fixture isolation** — Verification tests use temporary directories, never real developer settings.
4. **Receipt integrity** — Installation validation checks SHA-256 hashes from the install receipt.
5. **Workspace isolation** — Validates that skill installations don't symlink outside the workspace boundary.

---

## CLI Commands

```bash
aevoraseo agent detect [--workspace <path>] [--format {terminal,json,markdown}]
aevoraseo agent list [--format {terminal,json,markdown}]
aevoraseo agent inspect <host> [--format {terminal,json,markdown}]
aevoraseo agent adapt <host> [--workspace <path>] [--dry-run]
aevoraseo agent verify [--host <host>] [--format {terminal,json,markdown}]
```

---

## Evidence Boundaries

- Compatibility claims are limited to what fixture-based tests can prove.
- Live installation verification requires the actual host environment.
- A working Python runtime does not prove browser or network access.
- Skill registration does not prove execution permission.
- Detection identifies likely platforms; it does not guarantee the host is running.
