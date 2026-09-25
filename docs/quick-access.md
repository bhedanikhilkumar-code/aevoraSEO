# AevoraSEO Quick Access — Agent & CLI Skill Installation

This page is the copy-paste installation hub for AevoraSEO.

## Canonical repository

`bhedanikhilkumar-code/aevoraSEO`

The repository root contains the canonical `SKILL.md` plus the complete supporting resources (`docs/`, `references/`, `playbooks/`, `scripts/`, `src/`, and related skill assets). An installer must preserve the complete skill bundle rather than copying only `SKILL.md`.

## Universal master prompt

```text
Install the AevoraSEO Agent Skill from:
https://github.com/bhedanikhilkumar-code/aevoraSEO

First inspect the repository itself and identify the canonical SKILL.md and every
supporting file/resource required by that skill. Do NOT invent a new skill body,
do NOT copy only SKILL.md, and do NOT omit nested docs, references, playbooks,
scripts, assets, or runtime resources that the skill references.

Use this CLI/agent's official supported skill-installation mechanism. Register the
skill under the name `aevoraseo` (or the host's equivalent), preserving the complete
bundle. If this host supports slash commands, make `/aevoraseo` resolve to the
installed skill. If it uses a different skill invocation syntax, report the exact
native invocation after installation.

After installation:
1. Verify the skill is visible in the host's actual skill list/registry.
2. Verify SKILL.md is readable from the installed location.
3. Verify the referenced docs, references, playbooks, scripts and assets are present.
4. Run the host's skill validation/discovery check if available.
5. Run AevoraSEO's native doctor only if the runtime is available and permitted.
6. Do NOT crawl any website during installation unless I separately request it.
7. If any step fails, inspect the exact error, fix the installation problem, and
   re-run the failed verification. Do not report success from a copied folder alone.

Finally report:
- Skill registered: PASS/FAIL
- Complete bundle present: PASS/FAIL
- `/aevoraseo` or native invocation available: PASS/FAIL/NATIVE-EQUIVALENT
- Runtime/doctor: PASS/FAIL/NOT-RUN
- Exact installed skill path
- Any remaining limitation
```

## GitHub CLI (`gh skill`)

```text
Install the AevoraSEO skill from GitHub using this host's native GitHub skill
installer. Inspect https://github.com/bhedanikhilkumar-code/aevoraSEO first,
install the complete `aevoraseo` skill, and verify the host skill registry.
Use the exact repository and skill path discovered from the repository; do not
copy only SKILL.md. If supported, install at user scope so the skill is available
across projects, then verify the installed source metadata and skill listing.
```

Typical native command:

```bash
gh skill install bhedanikhilkumar-code/aevoraSEO aevoraseo --agent <agent> --scope user
```

## `npx skills` / Skills CLI

```text
Use the Skills CLI to install AevoraSEO from
https://github.com/bhedanikhilkumar-code/aevoraSEO.
First list/discover the repository's skills, then install the `aevoraseo` skill
for this agent using the complete repository bundle. Preserve all referenced
resources. Verify it appears in the agent's installed skill list and report the
native invocation. Do not run a website crawl as part of installation.
```

Typical command:

```bash
npx skills add bhedanikhilkumar-code/aevoraSEO --skill aevoraseo -a <agent> -y
```

## Claude Code

```text
Install AevoraSEO from https://github.com/bhedanikhilkumar-code/aevoraSEO as a
complete Claude Code skill. Inspect the repo, preserve every referenced resource,
register it as `aevoraseo`, verify it appears in Claude Code's skill discovery,
and confirm `/aevoraseo` is available. Then report the exact installed path and
any runtime setup that still needs to be done. Do not crawl a site yet.
```

## Codex

```text
Install AevoraSEO from https://github.com/bhedanikhilkumar-code/aevoraSEO as a
complete Codex Agent Skill. Inspect SKILL.md and all referenced resources first,
then use Codex's supported skill installation/discovery mechanism. Register it as
`aevoraseo`, verify it is discoverable, and report whether `$aevoraseo` is
available. Do not crawl a site yet. If runtime setup is supported, validate it
separately from skill registration.
```

## Cursor

```text
Install the complete AevoraSEO Agent Skill from
https://github.com/bhedanikhilkumar-code/aevoraSEO using Cursor's supported skill
mechanism. Inspect the repository and copy/register all files required by SKILL.md,
not just the root file. Verify the skill is discoverable in this workspace and
report the exact invocation. Do not run a website crawl yet.
```

## Gemini CLI

```text
Install the complete AevoraSEO Agent Skill from
https://github.com/bhedanikhilkumar-code/aevoraSEO using Gemini CLI's supported
skill mechanism. Inspect the repo, preserve every referenced skill resource,
register `aevoraseo`, refresh/reload skill discovery if required, and verify the
skill is available. Report the native invocation and installed path. Do not crawl
a website during installation.
```

## GitHub Copilot / Copilot CLI

```text
Install AevoraSEO from https://github.com/bhedanikhilkumar-code/aevoraSEO as an
Agent Skill using the host's supported GitHub Copilot skill mechanism. Inspect the
repository's SKILL.md and all referenced resources, install the complete bundle,
verify it in the Copilot skill list, and report the native invocation. Do not
crawl a website yet. If the host requires a reload, perform it and verify again.
```

## Antigravity / Antigravity CLI

```text
Install AevoraSEO from https://github.com/bhedanikhilkumar-code/aevoraSEO using
Antigravity's supported Agent Skills mechanism. Inspect the repo first, install
`aevoraseo` with every referenced docs/reference/playbook/script/asset resource,
then refresh skill discovery and verify the skill is active. Report the native
invocation and exact installation path. Do not crawl a website yet.
```

## Cline / OpenCode / Amp / Augment / Continue / CodeBuddy / Command Code / Cortex / Crush

```text
Install AevoraSEO from https://github.com/bhedanikhilkumar-code/aevoraSEO using
this agent's native Agent Skills mechanism. Inspect the repository before writing
anything. Discover the canonical `SKILL.md`, install the complete `aevoraseo` bundle
and every resource referenced by it, refresh skill discovery, and verify the skill
is registered. Use the host's native invocation syntax (slash command, skill
selector, or equivalent) and report it exactly. Do not crawl a website yet.
```

## Important behavior

A skill installation and the crawler runtime are separate checks. A successful file copy is not enough. The installer should verify host registration first, then runtime readiness separately. Website crawling, publishing, account access and external changes require a separate user request/authorization.

AevoraSEO follows the Agent Skills convention: `SKILL.md` provides the skill metadata/instructions, while additional files are loaded as needed. The repository's `SKILL.md` resolves its own skill root and uses the bundled resources.

## Updating later

When a newer repository version is released, use the host's supported skill update command or reinstall from the canonical repository. After updating, re-run the skill-list check and verify that the complete bundle remains present.
