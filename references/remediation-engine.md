# Automated Remediation & Code Patch Engine Reference

Technical methodology, patch generation contracts, safety boundaries, and rollback guarantees for the AevoraSEO Remediation Subsystem (`aevoraseo.remediation`).

---

## 1. Architectural Purpose & Remediation Pipeline

AevoraSEO identifies technical defects, content deficiencies, structured data gaps, and optimization opportunities across its intelligence subsystems. The Remediation Engine bridges the gap between diagnostic observation and physical codebase correction:

```text
┌────────────────────────────────────────────────────────┐
│                   AEVORASEO AUDIT                      │
│   (crawl.sqlite3, content_optimization.sqlite3, etc.)   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  REMEDIATION PLANNER                   │
│   Maps P0/P1/P2 findings to deterministic patches      │
│   Emits RemediationPlan (remediation-plan.json)        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  REMEDIATION EXECUTOR                  │
│   1. Pre-flight verification (path boundary, UTF-8)    │
│   2. Unified Diff Preview (preview_plan)               │
│   3. Atomic Backup to .aevora/backups/                 │
│   4. Deterministic AST Patch Application               │
│   5. Verification Receipt (receipt.json + SHA-256)     │
│   6. SQLite Persistence (remediations.sqlite3)         │
└───────────────────────────┬────────────────────────────┘
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
      OPERATIONAL AUDIT           ATOMIC ROLLBACK
      aevoraseo audit-verify      aevoraseo remediate rollback
```

---

## 2. Deterministic Patch Contracts

All patch routines operate via `BeautifulSoup` AST manipulation, guaranteeing valid HTML serialization without regex corruption of markup syntax:

### Title Tag Patching (`patch_title`)
- **Target:** `<head>` element, `<title>` tag.
- **Contract:** Creates `<title>` if absent or replaces existing inner text. Enforces 45–65 character length, trims excessive whitespace, appends brand suffix if provided, and preserves outer document hierarchy.

### Meta Description Patching (`patch_meta_description`)
- **Target:** `<head>` element, `<meta name="description" content="...">`.
- **Contract:** Creates or updates `<meta name="description">` with an actionable summary (120–160 chars) beginning with high-intent verbs (`Discover`, `Explore`, `Book`, `Learn`).

### Heading Structure Repair (`patch_headings`)
- **Target:** `<h1>` through `<h6>` tags across `<body>`.
- **Contract:**
  1. Ensures a single semantic `<h1>` representing the page target query; converts surplus `<h1>` elements to `<h2>`.
  2. Removes empty or whitespace-only heading tags.
  3. Corrects skipped heading levels (e.g. converting orphaned `<h3>` following an `<h1>` to `<h2>`) to maintain strict accessibility and AEO parsing standards.

### Direct Answer Block Injection (`patch_direct_answer`)
- **Target:** Immediate sibling position following the primary target heading (`<h1>` or matching question `<h2>`).
- **Contract:** Injects a semantic `<section class="aevora-direct-answer" data-aevora-patch="direct-answer">` container containing:
  - A concise, 40–60 word definition or factual summary designed for generative search engine extraction.
  - A structured list (`<ol>` or `<ul>`) for procedural or faceted answers.
- Replaces any prior patch container without duplicate nesting.

### Structured Data / Schema.org Injection (`patch_schema`)
- **Target:** `<head>` element.
- **Contract:** Generates compliant Schema.org JSON-LD `<script type="application/ld+json">`. Injects `Article`, `Service`, `Product`, `LocalBusiness`, `FAQPage`, or `HowTo` schema. Detects existing schema types to avoid duplicate root declarations.

### Canonical URL Repair (`patch_canonical`)
- **Target:** `<head>` element, `<link rel="canonical" href="...">`.
- **Contract:** Injects or replaces the canonical link element with the normalized absolute target URL.

### Internal Link Injection (`patch_internal_link`)
- **Target:** First contextually eligible `<p>` in `<body>` containing matching anchor phrases.
- **Contract:** Safely wraps the target keyword in `<a href="..." title="...">` while avoiding existing anchor tags, script tags, and header navigation elements.

---

## 3. Safety Invariants & Non-Destructive Operation

The remediation engine enforces rigorous defensive guarantees before touching any file on disk:

1. **Path Boundary Enforcement:** Target paths must resolve strictly within the designated `--site` root directory. Path traversal sequences (`../`, `..\\`, absolute drive escapes) are rejected with `ValueError`.
2. **UTF-8 Integrity:** Source files must decode cleanly as valid UTF-8. Binary assets, non-HTML files, and unreadable files are skipped with logged warnings.
3. **Pre-Flight Digest Matching:** If a patch specifies a target checksum, file application fails immediately if the on-disk file was modified by an external process.
4. **Dry-Run Simulation:** The `--dry-run` mode runs all AST manipulations in-memory, computing unified diffs and score impact without writing files or creating database records.

---

## 4. Atomic Backup & Rollback Protocol

When applying a remediation plan:

1. **Backup Storage:** Original file bytes are copied to `.aevora/backups/<plan_id>/` before any modification occurs.
2. **Pre/Post Digest Verification:** Pre-application and post-application SHA-256 cryptographic hashes are recorded for every modified file.
3. **Receipt Generation:** A tamper-evident `remediation-receipt.json` is generated containing:
   - `plan_id` and execution timestamp
   - Total files targeted and modified
   - Detailed patch entries with backup paths and SHA-256 digests
4. **Verified Atomic Rollback:** `aevoraseo remediate rollback --receipt <path>` reads the backup file, verifies the backup digest, restores the original file content atomically, and verifies that the restored file matches the pre-patch hash.

---

## 5. Persistence Architecture (`remediations.sqlite3`)

All plans, patches, and receipts are recorded in `remediations.sqlite3`:

```sql
CREATE TABLE IF NOT EXISTS remediation_plans (
    plan_id TEXT PRIMARY KEY,
    crawl_id TEXT,
    site_root TEXT NOT NULL,
    target_host TEXT,
    created_at TEXT NOT NULL,
    total_patches INTEGER NOT NULL,
    expected_score_recovery REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING'
);

CREATE TABLE IF NOT EXISTS remediation_patches (
    patch_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    patch_type TEXT NOT NULL,
    selector TEXT,
    description TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    FOREIGN KEY (plan_id) REFERENCES remediation_plans(plan_id)
);

CREATE TABLE IF NOT EXISTS remediation_receipts (
    receipt_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    files_modified INTEGER NOT NULL,
    backup_dir TEXT NOT NULL,
    receipt_json TEXT NOT NULL,
    rolled_back_at TEXT,
    FOREIGN KEY (plan_id) REFERENCES remediation_plans(plan_id)
);
```

All SQLite operations utilize deterministic `try/finally conn.close()` resource handling to ensure immediate file unlock on Windows file systems.

---

## 6. Security Hardening

- **Spreadsheet Formula Injection Defense:** All exported patch lists (`patches.csv`) pass through `sanitize_csv_cell` to strip or neutralize formula prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`, and leading whitespace).
- **Zero In-Memory Eval:** Patch operations strictly parse HTML through BeautifulSoup's tree model without invoking dynamic script evaluators or template runtime engines.
