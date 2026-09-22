# Content & Optimization Intelligence Reference

Comprehensive technical reference for AevoraSEO Content & Optimization Intelligence subsystem.

---

## 1. Subsystem Architecture

The Content & Optimization Intelligence engine provides deterministic, evidence-grounded audits of website content quality, metadata, heading structures, answer box readiness, topic clusters, schema recommendations, and internal linking equity.

```
                  +-----------------------------------+
                  |   Crawl Snapshot / Target URL     |
                  +-----------------+-----------------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
  +------------------+    +-------------------+   +--------------------+
  | Metadata Audits  |    | Heading Hierarchy |   | Direct Answer Box  |
  | (Title/Meta/CTA) |    | (H1/H2/H3 Skips)  |   | (40-60w Defs/FAQs) |
  +--------+---------+    +---------+---------+   +----------+---------+
           |                        |                        |
           +------------------------+------------------------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
  +------------------+    +-------------------+   +--------------------+
  | Internal Links   |    | Topic Clusters    |   | Schema Recommender |
  | (Graph & Orphans)|    | (Pillars & Spokes)|   | (Article/Service)  |
  +--------+---------+    +---------+---------+   +----------+---------+
                                    |
                                    v
                     +-----------------------------+
                     |  Deterministic 0-100 Score  |
                     +--------------+--------------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
  +------------------+    +-------------------+   +--------------------+
  |  Content Briefs  |    | Editorial Outlines|   | 30/60/90d Roadmap  |
  +------------------+    +-------------------+   +--------------------+
                                    |
                                    v
                     +-----------------------------+
                     | SQLite (content_opt.sqlite3)|
                     | Multi-Format Reports & CSV  |
                     +-----------------------------+
```

---

## 2. Title Optimization Rules

Title tags are evaluated deterministically:
1. **Length Guidelines**:
   - Optimal: 45–65 characters.
   - `< 30 characters`: Flagged as `too_short`.
   - `> 70 characters`: Flagged as `too_long` (high SERP truncation probability).
2. **Brand Placement**:
   - Detects whether brand name appears with separator (`... | Brand`, `... - Brand`, `... — Brand`, `... • Brand`).
   - If missing, recommends trailing brand placement.
3. **Primary Query Alignment**:
   - Tokenizes primary query extracted from H1 and slug.
   - Evaluates token overlap with title tag.
4. **Keyword Stuffing Detection**:
   - Detects repeated token sequences or individual tokens appearing $\ge 3$ times.

---

## 3. Meta Description Optimization Rules

1. **Length Guidelines**:
   - Optimal: 120–160 characters.
   - `< 70 characters`: Flagged as `too_short`.
   - `> 165 characters`: Flagged as `too_long`.
2. **Action-Oriented Call to Action (CTA)**:
   - Scans for active CTA verbs: `get`, `learn`, `discover`, `explore`, `read`, `find`, `shop`, `book`, `call`, `start`, `contact`, `see`, `try`, `schedule`, `register`, `join`.
   - Flags descriptions lacking an active user instruction.

---

## 4. Heading Hierarchy & Structure Rules

1. **Single Primary H1**:
   - Exactly one `<h1>` per document.
   - 0 `<h1>`: Missing primary heading.
   - `> 1 <h1>`: Multiple competing document headings.
2. **Sequential Nesting Without Skips**:
   - Headings must descend sequentially (`h1 -> h2 -> h3`).
   - Flagged as `has_skipped_levels` if an `<h1>` is followed immediately by an `<h3>`, or `<h2>` followed directly by `<h4>`.
3. **Question Headings**:
   - Identifies question headings starting with interrogatives (`what`, `why`, `how`, `when`, `where`, `who`, `which`, `can`, `does`, `is`) or ending with `?`.
4. **Empty Headings**:
   - Flags empty heading markup (`<h2></h2>`) or whitespace-only headings.

---

## 5. Direct Answer & Definition Box Engineering

Evaluates eligibility for Google featured snippets, answer boxes, and AI search citation:
1. **40–60 Word Definition Boxes**:
   - Definition phrases (`is a`, `refers to`, `is defined as`, `consists of`) positioned immediately below an `<h2>` or `<h3>`.
   - Paragraphs exceeding 75 words are flagged for refinement into a concise 40–60 word answer box.
2. **Procedural Lists**:
   - Step-by-step ordered lists (`<ol>`) under "how to" or process headings.
3. **Comparison Tables**:
   - Multi-column tables (`<table>`) under comparison headings (`vs`, `alternatives`).

---

## 6. FAQ & Buyer Objection Handling

Evaluates commercial landing pages for critical friction handling:
- **Pricing & Rates**: Baseline pricing transparency or engagement tiers.
- **Guarantees & SLAs**: Risk-reversal terms, satisfaction policies, or support commitments.
- **Implementation Timeline**: Delivery schedules or booking turnaround.
- **Schema Compatibility**: Verification for `FAQPage` JSON-LD eligibility.

---

## 7. Topic Clusters & Internal Link Graph

1. **Pillar / Hub Pages**: Broad, high-word-count (> 800 words) guides with multiple outbound links to subtopics.
2. **Supporting Spoke Pages**: Detailed subtopic articles linking back to the parent pillar.
3. **Orphan Page Recovery**: Identifies pages within the target domain having 0 incoming internal links (excluding the homepage).
4. **Anchor Text Diversity**: Flags generic anchors (`click here`, `read more`, `learn more`, `here`, `link`) and recommends descriptive topic anchors.

---

## 8. Intent-Matched Schema Recommendation Catalog

| Page Intent | Core Schema | Secondary Schema | Purpose |
|---|---|---|---|
| **Informational** | `Article` / `BlogPosting` | `BreadcrumbList`, `FAQPage` | Article attribution, rich snippets |
| **Transactional** | `Service` | `Product`, `Offer`, `AggregateRating` | Commercial clarity, pricing |
| **Local** | `LocalBusiness` | `PostalAddress`, `GeoCoordinates` | Map pack citations, NAP parity |
| **Procedural** | `HowTo` | `Step`, `ImageObject` | Step-by-step search carousels |
| **Q&A Content** | `FAQPage` | `Question`, `Answer` | SERP FAQ drop-downs |

---

## 9. Content Brief & Editorial Outline Specifications

Content briefs and outlines are deterministically generated from crawled evidence:
- **Target Queries**: Primary target query and up to 3 secondary modifiers.
- **Target Word Count**: Calibrated by intent (Informational: 1,200w+; Commercial: 1,400w+; Transactional: 800w+; Local: 650w+).
- **Required Sections**: Structured H2/H3 blueprint.
- **Direct Answer Targets**: 40–60 word definitions and procedural list targets.
- **Recommended Internal Links**: Pillar and spoke cross-linking.

---

## 10. Formula Injection Defense in CSV Exports

All tabular CSV exports (`content-recommendations.csv`, `content-briefs.csv`, `direct-answers.csv`, `internal-links.csv`) sanitize values starting with `=`, `+`, `-`, `@`, `\t`, or `\r` by prefixing a single quotation mark (`'`), neutralizing spreadsheet formula execution.

---

## 11. CLI Commands & Options

```powershell
# Run optimization audit on crawl snapshot
aevoraseo optimize ./crawl_snapshot --format terminal
aevoraseo optimize ./crawl_snapshot --out ./opt_results --format markdown
aevoraseo optimize ./crawl_snapshot --out ./opt_results --format json
aevoraseo optimize ./crawl_snapshot --out ./opt_results --format csv

# Compare optimization snapshots across crawl runs
aevoraseo optimize-compare --before ./crawl_baseline --after ./crawl_retest --out ./opt_diff --format terminal
aevoraseo optimize-compare --before ./crawl_baseline --after ./crawl_retest --out ./opt_diff --format markdown
```
