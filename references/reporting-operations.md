# Reporting, Operations & Professional Workflow Reference

Technical methodology and operational standards for unified client audits, multi-format delivery, acceptance verification, and progress tracking in AevoraSEO.

---

## 1. Unified Client Reporting Architecture

AevoraSEO combines individual subsystem intelligence into a cohesive, evidence-backed client audit. Rather than presenting fragmented, disconnected reports, the unified reporting engine synthesizes:

```text
┌───────────────────────────────────────────────────────────┐
│              AEVORASEO UNIFIED CLIENT AUDIT               │
├─────────────────────────────┬─────────────────────────────┤
│ 1. Technical SEO & Crawl    │ Status codes, indexability   │
│ 2. AEO & GEO Intelligence   │ Answer boxes, AI citations  │
│ 3. Entity & Knowledge Graph │ NAP, sameAs, authority     │
│ 4. Search & Commercial      │ Intent, cannibalization     │
│ 5. Content & Optimization   │ Headings, clusters, orphans │
│ 6. Brand Reputation         │ Backlinks, citations        │
└─────────────────────────────┴─────────────────────────────┘
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
       Executive Summary              Prioritized Matrix
       & Unified Scorecard            (P0 / P1 / P2)
               │                             │
               └──────────────┬──────────────┘
                              ▼
                30 / 60 / 90-Day Roadmap
                & Acceptance Criteria
```

---

## 2. Issue Priority Classification

Every recommendation is classified by strict impact and severity:

| Priority | Category | Definition & Criteria | Action Window |
|---|---|---|---|
| **P0** | Critical Blocker | Severe crawl/index blockages (5xx errors, accidental homepage `noindex`, robots disallows), cross-page entity identity conflicts, or catastrophic query collisions. | Days 1–30 |
| **P1** | High Impact | Issues directly damaging search visibility, AI citation, or user conversion: missing direct answer boxes, dead internal links (404), keyword cannibalization, multiple H1s, or orphan landing pages. | Days 31–60 |
| **P2** | Growth Opportunity | Ongoing compounding optimizations: topic cluster spoke expansion, Schema.org type enrichment, thin content refreshes, comparison table buildouts, and external backlink outreach. | Days 61–90 |

---

## 3. Multi-Format Delivery Standards

Audit outputs can be rendered into 5 standard delivery formats without external API dependencies:

1. **Terminal (`--format terminal`)**: Human-readable ASCII scorecard, executive summary, and prioritized action lists.
2. **Markdown (`--format markdown`)**: GitHub Flavored Markdown with structured tables and blockquotes, ready for developer PRs or repository wikis.
3. **HTML (`--format html`)**: Self-contained, responsive offline HTML document with embedded brand assets and professional CSS typography.
4. **JSON (`--format json`)**: Programmatically parseable structured data suitable for automated CI/CD pipelines and dashboards.
5. **CSV (`--format csv`)**: Structured evidence tables (`audit-issues.csv`, `audit-scorecard.csv`) with automatic sanitization against CSV spreadsheet formula injection (`=, +, -, @`).

---

## 4. Operational Acceptance Verification (`audit-verify`)

Recommendations are not closed upon publication; they require empirical verification:

```bash
aevoraseo audit-verify --audit ./audit-report.json --crawl ./crawl_after/
```

The verification engine inspects the subsequent crawl snapshot against the exact acceptance criteria recorded in the prior audit:
- **`RESOLVED`**: The specific technical error, orphan status, or missing answer condition is no longer detected.
- **`UNRESOLVED`**: The issue condition persists in the new crawl.
- **`REGRESSED`**: The metric or score degraded further.

---

## 5. Historical Progress Tracking (`progress`)

Tracks multidimensional score trajectories across chronological crawl series:

```bash
aevoraseo progress --crawls ./crawl1 ./crawl2 ./crawl3
```

Reports:
- Trajectory direction: `IMPROVING`, `STABLE`, or `DECLINING`.
- Score delta ($\Delta$) across crawls.
- Longitudinal issue counts and resolved rate.

---

## 6. Safe Content Publishing Workflow

Operational website updates follow a strict staging, review, cryptographic verification, and rollback lifecycle:

```bash
# 1. Stage recommended modification
aevoraseo edit plan --site ./my-site --file pages/service.html --replacement ./new-service.html --out ./staged_plan

# 2. Review unified diff and inspect SHA-256 plan receipt
cat staged_plan/plan.json

# 3. Apply reviewed changes safely
aevoraseo edit apply --site ./my-site --plan ./staged_plan/plan.json --expect-plan <SHA256>

# 4. Immediate rollback if regressions observed
aevoraseo edit rollback --site ./my-site --plan ./staged_plan/plan.json --expect-plan <SHA256>
```

---

## 7. Security & Non-Destructive Invariants

- **Formula Injection Defense**: All exported CSV cells are sanitized against spreadsheet formula execution.
- **Database Concurrency**: Safe connection handling (`try/finally conn.close()`) prevents database locking on Windows.
- **Boundary Isolation**: Publishing and staging operations restrict edits exclusively to standard content files (`.html`, `.md`, `.php`, etc.) and reject access to credentials (`wp-config.php`, `.env`) or traversal paths.
