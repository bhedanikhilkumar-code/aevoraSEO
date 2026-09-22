# AevoraSEO AEO & GEO Intelligence Methodology

This document specifies the technical methodology, mathematical scoring formulas, signal evidence models, SQLite persistence schemas, and strict boundary rules governing Answer Engine Optimization (AEO) and Generative Engine Optimization (GEO) in AevoraSEO.

---

## 1. Executive Mission & Foundational Boundary

AevoraSEO is an evidence-first SEO intelligence platform. Its AEO and GEO intelligence engines operate under a non-negotiable architectural boundary:

```
Observed Page & Crawl Evidence
             ↓
Deterministic Analytical Signals
             ↓
Predicted Answer & Generative Readiness

[STRICT BOUNDARY: NEVER CROSS WITHOUT SEPARATE EXTERNAL OBSERVATIONS]
             ↓
Empirical Observed AI Visibility
```

> [!IMPORTANT]
> **Measurement Boundary Rule**:
> - An AevoraSEO AEO Readiness Score or GEO Signal Score measures **internal content readiness, structural clarity, and machine extractability**.
> - It is **not** an external ranking measurement.
> - AevoraSEO **never** claims guaranteed rankings, AI citations, chat answers, or brand inclusion in ChatGPT, Google AI Overviews, Gemini, Perplexity, Claude, or any other engine unless authenticated, dated external measurement records are provided.

---

## 2. AevoraSEO AEO Readiness Score (0–100)

The **AevoraSEO AEO Readiness Score** evaluates whether content is shaped, formatted, and exposed in a way that allows automated answer engines to extract direct, high-confidence answers.

The score is computed deterministically across 5 dimensions:

| Dimension | Max Points | Core Focus |
| :--- | :--- | :--- |
| **Answer Readiness** | 30 | Presence, proximity, and conciseness of direct answers to detected questions |
| **Question Coverage** | 25 | Interrogative question headings (`what`, `how`, `why`, etc.) and structured FAQ schemas |
| **Content Structure** | 20 | Single H1 heading, strict hierarchy sequence, structured lists, and tables |
| **Schema Quality** | 15 | Valid, complete, and title-consistent Schema.org structured data |
| **AI Crawler Accessibility** | 10 | Unrestricted crawler access across standard AI crawler user agents |
| **Total** | **100** | **Normalized AEO Readiness** |

### 2.1 Dimension Breakdown & Formula Rules

#### 1. Answer Readiness (30 pts max)
- **Direct Answer Proximity (+5 pts per answer, max +15 pts)**: Detected paragraph, list, or definition block immediately following a question heading.
- **High-Confidence Definition Bonus (+10 pts)**: Answer contains definition phrasing (e.g. `refers to`, `is defined as`, `means`) and concise length (10–60 words).
- **Structured FAQ Block Bonus (+5 pts)**: Direct answer located inside Schema.org `FAQPage` or HTML `<details><summary>`.
- **Unanswered Question Penalty (-3 pts per unanswered, max -10 pts)**: Question headings followed by another heading without any intervening answer text.

#### 2. Question Coverage (25 pts max)
- **Detected Interrogatives (+4 pts per question, max +16 pts)**: Headings beginning with interrogative words (`what`, `why`, `how`, `when`, `where`, `who`, `which`, `can`, `does`, `is`, `are`, `should`, `will`, `could`, `would`).
- **Diverse Intent Distribution (+5 pts)**: Presence of at least two distinct question starter types (e.g. both informational `what` and procedural `how`).
- **Structured FAQ Markup (+4 pts)**: Questions backed by Schema.org `FAQPage` or `QAPage`.

#### 3. Content Structure (20 pts max)
- **Primary H1 Presence (+6 pts)**: Exactly one `<h1>` tag present on the page.
- **Multiple H1 Penalty (-4 pts)**: More than one `<h1>` tag detected.
- **Valid Heading Sequence (+6 pts)**: Strict hierarchy without skipped levels (e.g. `h2` followed by `h3`, not jumping directly from `h2` to `h4`).
- **Rich Extractable Formats (+4 pts for lists, +4 pts for tables, max +8 pts)**: Unordered/ordered lists and structured data tables.
- **Unbroken Text Penalty (-2 pts per unbroken block >250 words, max -6 pts)**: Walls of text lacking paragraph breaks or subheadings.

#### 4. Schema Quality (15 pts max)
- **Valid Core Schema (+8 pts)**: Valid JSON-LD or Microdata matching recognized types (`Article`, `Organization`, `LocalBusiness`, `Product`, `FAQPage`, etc.).
- **Property Completeness (+4 pts)**: All required Schema.org properties populated.
- **Title & URL Consistency (+3 pts)**: Schema headline matches page title and canonical URL.
- **Syntax Error Penalty (-5 pts per error, max -10 pts)**: Malformed JSON-LD script blocks.

#### 5. AI Crawler Accessibility (10 pts max)
- Points allocated proportionately based on the ratio of allowed AI crawler bots:
  $$\text{Score} = \text{round}\left(10 \times \frac{\text{Allowed Bots}}{\text{Total Tracked Bots}}, 1\right)$$

---

## 3. AevoraSEO GEO Signal Score (0–100)

The **AevoraSEO GEO Signal Score** evaluates whether content provides the source authority, entity consistency, factual density, and extractable proof required for generative search models to cite it as a reference source.

| Dimension | Max Points | Core Focus |
| :--- | :--- | :--- |
| **Entity Clarity** | 30 | Identity declaration, disambiguation, `sameAs` authority links, cross-page consistency |
| **Source Readiness** | 25 | Author byline, publisher attribution, date timestamps, canonical validation |
| **Factual Specificity & Density** | 25 | Numerical claims, statistics, percentages, dates, outbound source citations |
| **Content Depth & Extractability** | 20 | Substantial word count, data tables, structured comparative formatting |
| **Total** | **100** | **Normalized GEO Signal Strength** |

### 3.1 Dimension Breakdown & Formula Rules

#### 1. Entity Clarity (30 pts max)
- **Core Entity Declaration (+10 pts)**: Explicit `Organization`, `Person`, or `Product` entity in Schema.org markup.
- **Entity Disambiguation (+10 pts)**: Presence of verified external authority references in `sameAs` (e.g. Wikidata, Wikipedia, official social profiles).
- **Entity Consistency (+10 pts)**: Zero naming or type contradictions detected across pages.
- **Contradiction Penalty (-8 pts per cross-page conflict, max -16 pts)**: Mismatched entity names across canonical URLs.

#### 2. Source Readiness (25 pts max)
- **Author Attribution (+8 pts)**: Explicit author name in byline and Schema markup.
- **Publisher Attribution (+5 pts)**: Verified publishing organization.
- **Freshness Timestamps (+6 pts)**: Both `datePublished` and `dateModified` timestamps present.
- **Canonical Match (+6 pts)**: Self-referential or valid canonical URL matching final request URL.
- **Missing Attribution Deduction (-5 pts)**: Complete absence of author and publisher metadata.

#### 3. Factual Specificity & Density (25 pts max)
- **Statistical Density (+10 pts)**: Frequent presence of quantitative metrics, percentages, dollar amounts, and specific years/dates in text.
- **Outbound Citation Domains (+10 pts max)**: References linking to external reputable or academic sources.
- **Factual Ratio (+5 pts)**: Measured factual density index $\ge 0.40$.

#### 4. Content Depth & Extractability (20 pts max)
- **Substantive Word Count (+10 pts)**:
  - $\ge 1200\text{ words}$: 10 pts
  - $600–1199\text{ words}$: 7 pts
  - $300–599\text{ words}$: 4 pts
  - $< 300\text{ words}$: 1 pt
- **Structured Comparative Tables (+10 pts)**: Presence of data tables and comparison matrices facilitating machine information extraction.

---

## 4. Tracked AI Bot Registry

AevoraSEO tracks and audits 10 major AI training, search, and retrieval bots:

| Crawler Name | User-Agent Identifier | Primary Operator | Purpose / Engine |
| :--- | :--- | :--- | :--- |
| **GPTBot** | `GPTBot` | OpenAI | Model training & answer compilation |
| **ChatGPT-User** | `ChatGPT-User` | OpenAI | Real-time ChatGPT browsing actions |
| **ClaudeBot** | `ClaudeBot` | Anthropic | Claude training & real-time search |
| **PerplexityBot** | `PerplexityBot` | Perplexity AI | Conversational search indexing |
| **Google-Extended** | `Google-Extended` | Google | Gemini & Vertex AI model training |
| **Bytespider** | `Bytespider` | ByteDance | Search indexing & model training |
| **CCBot** | `CCBot` | Common Crawl | Open web dataset ingestion |
| **Applebot-Extended** | `Applebot-Extended` | Apple | Apple Intelligence generative AI |
| **Cohere-AI** | `cohere-ai` | Cohere | Enterprise LLM & RAG retrieval |
| **Meta-ExternalAgent**| `Meta-ExternalAgent` | Meta | Meta AI training & search assistance |

Each page is evaluated against `robots.txt` rules, `<meta name="robots">` directives, bot-specific meta tags (e.g. `<meta name="google-extended" content="noindex">`), and `X-Robots-Tag` HTTP response headers.

---

## 5. SQLite Persistence Architecture

AEO and GEO evidence is persisted into SQLite tables within the crawl snapshot database (`crawl.sqlite3`) and export database (`aeo.sqlite3`):

### 5.1 Schema Definition

```sql
CREATE TABLE IF NOT EXISTS aeo_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    seed_url TEXT,
    analyzed_at TEXT,
    page_count INTEGER,
    average_aeo_score REAL,
    average_geo_score REAL,
    bot_matrix TEXT,
    summary_markdown TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS aeo_pages (
    snapshot_id TEXT,
    url TEXT,
    aeo_readiness_score REAL,
    geo_signal_score REAL,
    questions_count INTEGER,
    direct_answers_count INTEGER,
    schemas_count INTEGER,
    author TEXT,
    publisher TEXT,
    payload TEXT,
    PRIMARY KEY (snapshot_id, url)
);

CREATE TABLE IF NOT EXISTS aeo_questions (
    snapshot_id TEXT,
    url TEXT,
    question TEXT,
    answer_detected INTEGER,
    confidence REAL,
    answer_location TEXT,
    answer_text TEXT,
    PRIMARY KEY (snapshot_id, url, question)
);

CREATE TABLE IF NOT EXISTS aeo_entities (
    snapshot_id TEXT,
    url TEXT,
    entity_type TEXT,
    name TEXT,
    source TEXT,
    is_consistent INTEGER,
    PRIMARY KEY (snapshot_id, url, entity_type, name, source)
);

CREATE TABLE IF NOT EXISTS aeo_diffs (
    before_snapshot_id TEXT,
    after_snapshot_id TEXT,
    before_avg_aeo REAL,
    after_avg_aeo REAL,
    aeo_delta REAL,
    before_avg_geo REAL,
    after_avg_geo REAL,
    geo_delta REAL,
    compared_at TEXT,
    payload TEXT,
    PRIMARY KEY (before_snapshot_id, after_snapshot_id)
);
```

---

## 6. Snapshot Comparison & Trajectory Engine

The comparison engine (`aevoraseo aeo-compare`) analyzes two snapshots and identifies score evolutions:

### 6.1 Page Transition States
- **`ADDED`**: URL newly observed in subsequent snapshot.
- **`REMOVED`**: URL present in baseline snapshot but not observed in subsequent snapshot.
- **`IMPROVED`**: Page AEO Readiness score improved by $\ge +5.0$ points.
- **`REGRESSED`**: Page AEO Readiness score dropped by $\le -5.0$ points.
- **`UNCHANGED`**: Score delta within $(-5.0, +5.0)$ points.

### 6.2 Contributing Evidence Attribution
Every score shift is traced back to specific structural changes:
- Change in direct answers count (`Direct answers increased from X to Y`).
- Schema types added or removed.
- Primary `<h1>` heading added or omitted.
- Author attribution added or removed.
- AI bots unblocked or newly restricted in `robots.txt`.
- Shift in measured factual density score.

---

## 7. Security Hardening & Safe Export

1. **CSV Formula Injection Mitigation**:
   All string values in `aeo_pages.csv` and `aeo_comparison.csv` (author names, publishers, heading questions, evidence text) are sanitized using single-quote prefixing (`'`) if they start with `=`, `+`, `-`, `@`, `\t`, or `\r`.
2. **Pathological Recursion Protection**:
   JSON-LD tree traversal in schema auditing and FAQ extraction is bounded by depth limits (`max_depth = 25`) and identity cycle checks (`visited_ids`), preventing `RecursionError` on malicious or circular markup.
3. **Safe Content Handling**:
   Untrusted HTML content is parsed strictly for DOM text and semantic hierarchy; scripts and external active elements are discarded without execution.
