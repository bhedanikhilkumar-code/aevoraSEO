# Automated Remediation & Code Patches

AevoraSEO includes an automated remediation and code patch subsystem (`aevoraseo remediate`). It converts crawl audits, content optimization findings, and unified report recommendations into concrete, verifiable, syntax-safe HTML and metadata code patches.

---

## 1. Remediation Workflow Overview

The remediation workflow follows a strict review, preview, apply, and verify lifecycle:

```text
1. Crawl & Audit Site
   aevoraseo crawl https://example.com --out runs/audit-01
   aevoraseo optimize runs/audit-01 --out runs/optimization

2. Generate Remediation Plan
   aevoraseo remediate generate --crawl runs/audit-01 --site /path/to/local/html/site --out runs/remediation

3. Preview Changes (Dry-Run / Unified Diff)
   aevoraseo remediate preview --plan runs/remediation/remediation-plan.json

4. Apply Remediation Patches (Atomic with Backup)
   aevoraseo remediate apply --plan runs/remediation/remediation-plan.json

5. Re-Crawl & Verify Resolution
   aevoraseo crawl https://example.com --out runs/audit-02
   aevoraseo audit-verify --audit runs/remediation/remediation-plan.json --crawl runs/audit-02

6. Optional Rollback (If needed)
   aevoraseo remediate rollback --receipt runs/remediation/remediation-receipt.json
```

---

## 2. Command Reference

### Generate a Remediation Plan

Synthesizes findings from a crawl snapshot or local HTML files and builds patch blueprints:

```bash
# Generate remediation plan from crawl results targeting local site directory
aevoraseo remediate generate --crawl runs/audit-01 --site ./site --out runs/remediation

# Generate directly from local site inspection without previous crawl
aevoraseo remediate generate --site ./site --out runs/remediation

# Output format options: terminal (default), json, markdown
aevoraseo remediate generate --crawl runs/audit-01 --site ./site --format markdown
```

**Artifacts Generated:**
- `remediation-plan.json`: Machine-readable plan with patch specifications, target files, and estimated score recovery.
- `remediation-plan.md`: Human-readable summary of proposed changes grouped by priority (P0, P1, P2).
- `patches.csv`: Sanitized CSV list of all planned patches.
- Persistence record in `remediations.sqlite3`.

---

### Preview a Remediation Plan

Inspect unified colorized diffs without writing any changes to disk:

```bash
# Terminal unified diff preview
aevoraseo remediate preview --plan runs/remediation/remediation-plan.json

# Markdown formatted diff preview (ideal for PR descriptions)
aevoraseo remediate preview --plan runs/remediation/remediation-plan.json --format markdown

# JSON diff inspection
aevoraseo remediate preview --plan runs/remediation/remediation-plan.json --format json
```

---

### Apply Remediation Patches

Applies deterministic AST patches to local HTML files with automatic atomic backup:

```bash
# Dry-run test (verifies path resolution, UTF-8 compliance, and AST validity without disk writes)
aevoraseo remediate apply --plan runs/remediation/remediation-plan.json --dry-run

# Live patch application (creates backup and writes changes)
aevoraseo remediate apply --plan runs/remediation/remediation-plan.json

# Markdown receipt output
aevoraseo remediate apply --plan runs/remediation/remediation-plan.json --format markdown
```

**Safety Guarantees during Application:**
- **Atomic Backup:** Exact pre-patch copies stored in `.aevora/backups/<plan_id>/`.
- **Pre/Post Digest Verification:** SHA-256 hashes calculated before and after modification.
- **Tamper-Evident Receipt:** `remediation-receipt.json` records execution timestamp, backup paths, and checksums.

---

### Rollback an Applied Remediation

Restores original files with verified SHA-256 hash matching:

```bash
# Rollback using execution receipt
aevoraseo remediate rollback --receipt runs/remediation/remediation-receipt.json

# Output rollback status as JSON or Markdown
aevoraseo remediate rollback --receipt runs/remediation/remediation-receipt.json --format json
```

---

### List Stored Remediation Plans

Inspect past plans and execution statuses recorded in `remediations.sqlite3`:

```bash
# List all remediation plans
aevoraseo remediate list

# Filter plans for a specific workspace directory
aevoraseo remediate list --crawl runs/audit-01
```

---

## 3. Supported Patch Types

| Patch Type | Target | Description |
|---|---|---|
| `TITLE_OPTIMIZATION` | `<title>` | Injects or repairs title tag to 45–65 characters with primary query and brand suffix. |
| `META_DESCRIPTION` | `<meta name="description">` | Injects or updates description with actionable verb prompts within 120–160 characters. |
| `HEADING_HIERARCHY` | `<h1>`–`<h6>` | Enforces single H1, corrects skipped heading levels (e.g. H1->H3), and removes empty headings. |
| `DIRECT_ANSWER` | `<section class="aevora-direct-answer">` | Injects structured 40–60 word answer boxes and procedural lists under question headings for AEO/GEO discovery. |
| `SCHEMA_JSONLD` | `<script type="application/ld+json">` | Injects valid Schema.org JSON-LD structured data matching detected page intent. |
| `CANONICAL_URL` | `<link rel="canonical">` | Injects or updates canonical URL reference. |
| `INTERNAL_LINK` | `<a href="https://example.com/target-page">` | Injects contextual in-body links to eliminate orphan pages and reinforce topic clusters. |

---

## 4. Node Runner Parity

All remediation commands run identically via the Node launcher:

```bash
node bin/aevoraseo.js remediate --help
node bin/aevoraseo.js remediate generate --crawl runs/audit-01 --site ./site
node bin/aevoraseo.js remediate preview --plan runs/remediation/remediation-plan.json
node bin/aevoraseo.js remediate apply --plan runs/remediation/remediation-plan.json
node bin/aevoraseo.js remediate rollback --receipt runs/remediation/remediation-receipt.json
```
