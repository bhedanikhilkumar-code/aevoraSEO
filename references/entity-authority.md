# AevoraSEO Entity, Authority & Knowledge Intelligence

The **AevoraSEO Entity, Authority & Knowledge Intelligence Engine** extracts, models, audits, and tracks entity structures, cross-page brand consistency, semantic relationships, and external authority signals across crawled websites.

It produces a deterministic **AevoraSEO Entity & Authority Score (0–100)**, builds a connected knowledge graph, audits identity conflicts, maps outbound `sameAs` authority footprints, and tracks entity evolution over time.

---

## 1. Core Principles & Measurement Boundaries

1. **Observed Evidence Only**:
   The engine extracts only facts and relationships explicitly observed in Schema.org JSON-LD, Microdata, meta tags, and rendered page content. It never invents unobserved knowledge-graph facts or infers relationships without supporting evidence.
2. **First-Party vs. Independent Proof**:
   Self-declared claims (such as an organization claiming on its own website that it is an industry leader) are marked as `is_first_party = True`. Independent corroboration requires external high-authority semantic profiles (Wikidata, Wikipedia, Crunchbase, verified official registers) linked via validated `sameAs` URLs.
3. **No Ranking Predictions**:
   A high Entity & Authority Score indicates structural clarity, data completeness, and semantic connectedness for search engines and answer engines. It is not an external Google PageRank or a guarantee of search ranking positions.

---

## 2. Supported Entity Types & Extraction

The extractor maps visible content and structured schemas into typed entity nodes:

| Entity Type | Schema.org Type | Extracted Attributes |
|---|---|---|
| **Organization** | `Organization`, `Corporation`, `LocalBusiness` | Legal name, alternate names, brand URL, logo, description, telephone, email, founding date, physical address, geo coordinates |
| **Person** | `Person` | Full name, job title, bio/description, affiliated organization (`worksFor`), alma mater (`alumnusOf`), official profiles (`sameAs`) |
| **Product** | `Product` | Name, brand, SKU, offers (price, currency, availability), aggregate ratings (rating value, review count) |
| **Service** | `Service` | Name, provider, service type, area served, offers |
| **Place** | `Place`, `PostalAddress` | Street address, locality, region, postal code, country, geo latitude/longitude |
| **Article** | `Article`, `NewsArticle`, `BlogPosting` | Headline, author, publisher, date published, date modified, main entity of page |

---

## 3. Authority & SameAs Discovery

The `same_as` subsystem validates and categorizes external semantic links into authority tiers:

| Authority Tier | Platforms | Authority Weight |
|---|---|---|
| **Knowledge & Semantic** | Wikidata, Wikipedia | Tier 1 (10 pts) |
| **Corporate & Professional** | LinkedIn, Crunchbase | Tier 1 (8 pts) |
| **Technical & Reputation** | GitHub, ORCID, Trustpilot, Google Business, Clutch, G2, ProductHunt | Tier 2 (5 pts) |
| **Media & Publishing** | YouTube, Twitter/X, Medium, Substack, Facebook, Instagram | Tier 3 (2 pts) |

### Missing Profile Detection
The engine audits expected corporate profiles against the entity type, flagging gaps where key authority registries (e.g., LinkedIn or Crunchbase for a corporation, or Google Business for a local business) are missing from `sameAs`.

---

## 4. Entity Consistency & Conflict Detection

The consistency auditor scans across all crawled pages of a website to identify contradictions and integrity issues:

1. **Name Inconsistency (`NAME_INCONSISTENCY`) — High Severity**:
   Flags contradictory primary organization names appearing across pages unless formally linked as an `alternateName` or `legalName`.
2. **NAP Mismatch (`NAP_MISMATCH`) — Medium Severity**:
   Detects disparate physical addresses or phone numbers declared across different pages for the same entity.
3. **Broken SameAs (`BROKEN_SAMEAS`) — Low Severity**:
   Flags invalid, malformed, or relative URLs declared in `sameAs` properties.
4. **Missing Recommended Entity Pages (`MISSING_REQUIRED_PAGE`) — Low Severity**:
   Audits crawl paths against the AevoraSEO knowledge-graph standard:
   - `/about` or `/company`
   - `/contact`
   - `/team` or `/founder`
   - `/services` or `/products`
   - `/reviews` or `/case-studies`
   - `/faq`

---

## 5. Knowledge Graph Topology

Extracted entities are assembled into a formal directed graph:

- **Nodes**: Entities (`org:...`, `person:...`, `service:...`, `product:...`) and external authority profiles (`ext:...`).
- **Edges**: Directed semantic relationships:
  - `(Person)-[FOUNDED_BY]->(Organization)`
  - `(Person)-[WORKS_FOR]->(Organization)`
  - `(Person)-[AUTHORED_BY]->(Article)`
  - `(Organization)-[PUBLISHED_BY]->(Article)`
  - `(Organization)-[PROVIDED_BY]->(Service)`
  - `(Organization)-[BRANDED_BY]->(Product)`
  - `(Entity)-[SAME_AS]->(ExternalProfile)`
- **Topology Metrics**:
  - `node_count`: Total distinct entities.
  - `edge_count`: Total validated relationships.
  - `density`: Network connectedness ratio.
  - `central_entity_id`: Node with highest degree centrality.
- **Graph Serialization**: Exported to `entity-graph.json` in Cytoscape.js / D3.js compatible format.

---

## 6. Scoring Model (0–100)

The headline **AevoraSEO Entity & Authority Score** is computed across four 25-point dimensions:

$$\text{Headline Score} = \text{Identity Completeness} + \text{Entity Consistency} + \text{Authority Footprint} + \text{Topical/Expert Depth}$$

### Dimension 1: Identity Completeness (0–25 pts)
- Primary Organization declared: +5 pts
- Brand URL & Logo verified: +5 pts
- Substantive description (>20 chars): +5 pts
- Contact info (phone/email/address): +5 pts
- Founding date or founder provenance: +5 pts

### Dimension 2: Entity Consistency & Integrity (0–25 pts)
Base of 25.0 points with deductions for detected conflicts:
- High-severity conflict (name contradiction): -10.0 pts each
- Medium-severity conflict (NAP mismatch): -5.0 pts each
- Low-severity conflict (broken sameAs, missing pages): -2.0 pts each
- Floor: 0.0 pts

### Dimension 3: SameAs & Authority Footprint (0–25 pts)
- Wikidata / Wikipedia presence: +10.0 pts
- LinkedIn / Crunchbase presence: +8.0 pts
- Technical/Reputation profile (GitHub, ORCID, Trustpilot, Google Business): +5.0 pts
- Additional valid profiles: +2.0 pts each (capped at 25.0 pts total)

### Dimension 4: Topical & Expert Depth (0–25 pts)
- Person/Expert entities with bio or job title: +10.0 pts
- Content authorship attribution across articles: +10.0 pts
- Offerings entity mapping (Services / Products linked to organization): +5.0 pts

### Confidence Rating
- **High**: Headline $\ge 70.0$, primary organization verified, authority footprint $\ge 15.0$, 0 high-severity conflicts.
- **Medium**: Primary organization verified, headline $\ge 40.0$.
- **Low**: Missing primary organization or headline $< 40.0$ or active high-severity conflicts.

---

## 7. SQLite Persistence (`entities.sqlite3`)

Persisted to SQLite with safe connection management:

```sql
CREATE TABLE entity_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    target_url TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    total_nodes INTEGER NOT NULL,
    total_edges INTEGER NOT NULL,
    authority_score REAL NOT NULL,
    confidence TEXT NOT NULL,
    completeness_score REAL NOT NULL,
    consistency_score REAL NOT NULL,
    footprint_score REAL NOT NULL,
    expert_score REAL NOT NULL,
    raw_json TEXT
);

CREATE TABLE entity_nodes (
    entity_id TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    alternate_names TEXT,
    attributes_json TEXT,
    is_first_party INTEGER NOT NULL,
    source_pages_json TEXT,
    confidence_score REAL NOT NULL,
    PRIMARY KEY (entity_id, snapshot_id)
);

CREATE TABLE entity_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    evidence_url TEXT,
    is_inferred INTEGER NOT NULL,
    confidence REAL NOT NULL
);

CREATE TABLE entity_same_as (
    same_as_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    url TEXT NOT NULL,
    platform TEXT NOT NULL,
    is_valid_url INTEGER NOT NULL,
    is_high_authority INTEGER NOT NULL,
    found_on_url TEXT
);

CREATE TABLE entity_conflicts (
    conflict_id TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    conflict_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    entity_id TEXT,
    entity_name TEXT,
    description TEXT NOT NULL,
    details_json TEXT,
    PRIMARY KEY (conflict_id, snapshot_id)
);

CREATE TABLE entity_diffs (
    diff_id TEXT PRIMARY KEY,
    target_url TEXT NOT NULL,
    before_snapshot_id TEXT NOT NULL,
    after_snapshot_id TEXT NOT NULL,
    score_delta REAL NOT NULL,
    created_at TEXT NOT NULL,
    changes_json TEXT NOT NULL
);
```

---

## 8. CLI Usage

### Entity Extraction & Authority Scoring
```bash
# Analyze an existing crawl snapshot directory
aevoraseo entity ./crawl_output --format terminal

# Output Markdown report
aevoraseo entity ./crawl_output --format markdown

# Output JSON data
aevoraseo entity ./crawl_output --format json

# Export formula-sanitized entities CSV
aevoraseo entity ./crawl_output --format csv

# Directly analyze a target website
aevoraseo entity https://example.com --out ./entity_example
```

### Temporal Snapshot Diffing
```bash
# Compare two entity snapshots
aevoraseo entity-compare --before ./crawl1 --after ./crawl2 --out ./entity_diff --format terminal
```
