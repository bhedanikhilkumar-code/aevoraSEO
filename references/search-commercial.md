# Search, Local & Commercial Intelligence Subsystem

> **Status:** Production / Implemented in Phase F  
> **Subsystem:** `aevoraseo.search`  
> **Primary Commands:** `aevoraseo search`, `aevoraseo search-compare`  
> **Documentation:** User documentation in `docs/README.md`; operating plan in `AGENT.md`.

---

## 1. Executive Overview

AevoraSEO evaluates whether crawled web content is structurally and semantically positioned for search discovery, local relevance, and commercial conversion.

Traditional SEO audits frequently isolate technical crawl errors from commercial reality. A site may achieve 100% clean crawlability while suffering from severe keyword cannibalization, generic call-to-action buttons ("Click Here"), missing local business schemas, high form friction, or absent buyer decision support.

The Search, Local & Commercial Intelligence subsystem unites these dimensions into an evidence-driven analysis loop:

```
Crawl Snapshot
     ↓
Search Intent Taxonomy (Informational, Commercial Investigation, Transactional, Navigational, Local)
     ↓
Target Query Extraction & Keyword Cannibalization Detection
     ↓
Local Search Visibility Signals (LocalBusiness Schema, NAP, Click-to-Call, Maps, Service Areas)
     ↓
Commercial Conversion Journeys & Call-to-Action (CTA) Friction Audit
     ↓
Comparison & Buyer Decision Support (Feature Matrices, Alternatives, Buyer FAQs)
     ↓
AevoraSEO Search & Commercial Visibility Score (0–100)
     ↓
SQLite Persistence (`search_commercial.sqlite3`) & Temporal Snapshot Evolution (`search-compare`)
```

---

## 2. Evidence Contract & Measurement Boundaries

In strict compliance with `references/measurement-boundaries.md` and `AGENT.md`:

1. **No Fabricated Search Rankings:**
   - Search engine rankings, SERP positions, click-through rates, and monthly search query volumes are external measurements.
   - The subsystem **never** fabricates keyword search volume, manufactured impressions, or estimated rank positions without verified, dated first-party Google Search Console exports or explicit SERP observations.
2. **On-Site Readiness vs External Outcome:**
   - The AevoraSEO Search & Commercial Visibility Score evaluates *internal on-site search targeting, local readiness, and conversion friction*.
   - A score of 95/100 proves excellent structural readiness, NOT guaranteed rankings or revenue.
3. **Traceable Observations:**
   - Every cannibalization alert, friction blocker, or local gap is tied to specific page URLs, extracted text, and HTML elements.

---

## 3. Search Intent Taxonomy & Query Extraction

### 3.1 Taxonomy Classes

Pages are classified into primary and secondary search intents:

| Intent Class | Definition | Key Signals |
|---|---|---|
| **Transactional** | User intends to complete an immediate commercial action, booking, or purchase. | `/cart`, `/checkout`, `/book`, `/pricing`, "buy now", "schedule appointment", `Product`/`Offer` schema. |
| **Commercial Investigation** | User evaluates solutions, compares alternatives, or reads reviews prior to buying. | `/vs/`, `/reviews`, `/best-`, "compare", "alternatives", "pros and cons", `AggregateRating`. |
| **Informational** | User seeks education, answers, or instructional guidance. | `/blog/`, `/guide/`, `/how-to-`, "what is", "tips", "tutorial", `Article`/`BlogPosting`/`FAQPage`. |
| **Local** | User searches for a service or business within a geographic area. | `/locations/`, "near me", address, `LocalBusiness` schema, phone number, opening hours. |
| **Navigational** | User seeks a specific branded portal, page, or account destination. | `/`, `/about-us`, `/contact`, `/login`, `/portal`, `/careers`, brand name alone. |

### 3.2 Target Query Extraction

Target queries are extracted deterministically:
1. Normalizes H1 heading, Title tag, meta description, and URL slug.
2. Eliminates standard linguistic stop words ("a", "the", "in", "for", "to", "and", "our", "your", etc.).
3. Computes token overlap between H1, Title, and slug to identify the 2-to-5 word primary target query.
4. Derives secondary queries from meta descriptions and remaining heading keywords.

### 3.3 Keyword Cannibalization Detection

When multiple internal pages target the same or near-identical primary query with identical intent:
- **Jaccard Token Similarity:** Computes token-set overlap between page target queries:
  $$\text{Similarity}(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
- **Risk Classification:**
  - **HIGH (Similarity $\ge 85\%$ or exact match with same intent):** Severe risk of split internal link equity and competing Google ranking signals. Recommendation: Consolidate content into single authoritative page or apply 301 redirect.
  - **MEDIUM (Similarity $70\% - 84\%$ with same intent):** Overlapping commercial topics. Recommendation: Differentiate intent modifiers, headings, and canonical relationships.
  - **LOW:** Minor informational phrase overlap. Recommendation: Establish hierarchical internal linking.

---

## 4. Local Search Visibility Signals

Local visibility requires proof of physical or service-area presence:

1. **LocalBusiness Schema Validation:**
   - Detects `LocalBusiness` and specialized sub-types (`Dentist`, `MedicalBusiness`, `LegalService`, `Store`, `Restaurant`, `AutomotiveBusiness`, etc.).
   - Validates essential properties: `name`, `address` (`PostalAddress`), `telephone`, `geo` (`GeoCoordinates`), `openingHoursSpecification`, `areaServed`.
2. **NAP (Name, Address, Phone) Uniformity:**
   - Detects phone numbers across international and national formats.
   - Extracts postal address strings from schema, `<address>` elements, and page footers.
   - Checks for consistency across site pages.
3. **Click-to-Call Readiness:**
   - Audits whether phone numbers use clickable `<a href="tel:...">` links.
   - Mobile users must be able to tap to call without manual copy-pasting.
4. **Google Maps Integration:**
   - Detects embedded Google Maps iframes (`google.com/maps/embed`) and direction links (`maps.google.com`, `maps.app.goo.gl`).
5. **Service Area Coverage:**
   - Evaluates declared service regions in `areaServed` against dedicated landing pages to prevent thin doorway patterns.

---

## 5. Commercial Journeys & CTA Friction

The conversion journey determines whether visitors can act immediately:

### 5.1 CTA Extraction & Specificity Classification
- **High-Intent Specific CTAs:** Action-oriented phrases with explicit value:
  - *"Book Dental Implant Consultation"*
  - *"Schedule Free Audit"*
  - *"Start 14-Day Free Trial"*
  - *"Order Now"*
- **Generic / Weak CTAs:** Uninformative buttons that increase decision friction:
  - *"Click Here"*, *"Learn More"*, *"Submit"*, *"Read More"*, *"Continue"*.

### 5.2 Friction Audits
- **Excessive Form Fields:** Forms with $> 5$ visible input fields on lead generation pages are flagged for friction.
- **Missing Direct Channels:** Commercial pages without clickable phone (`tel:`) or messaging (WhatsApp `wa.me`) are penalized.
- **Trust Proof Proximity:** Audits whether customer ratings (`AggregateRating`, star badges), doctor/expert credentials, guarantees, or security badges appear near conversion points.
- **Pricing Transparency:** Categorizes pricing availability into `transparent_pricing` (explicit fees or starting rates), `custom_quote` (clear proposal flow), or `no_pricing_info`.

---

## 6. Comparison & Buyer Decision Support

For commercial investigation queries ("X vs Y", "Best X alternatives"):
- **Feature Comparison Matrices:** Checks for structured `<table>` elements comparing features, specs, or pricing tiers.
- **Evaluated Alternatives:** Extracts competitor products and brands analyzed on the page.
- **Buyer Question (FAQ) Coverage:** Audits whether objection-handling questions are answered:
  - *"How much does it cost?"*
  - *"How long does it take?"*
  - *"Is there a warranty or guarantee?"*
  - *"What happens after booking?"*

---

## 7. Scoring Methodology (0–100)

The AevoraSEO Search & Commercial Visibility Score is calculated across four 25-point dimensions:

$$\text{Score} = \text{Intent} + \text{Commercial} + \text{Local} + \text{Comparison}$$

| Dimension | Max Points | Evaluation Factors |
|---|---|---|
| **Intent & Query Targeting** | 25.0 | Average intent classification confidence, non-generic query specificity, and cannibalization deductions (-4.0 for high, -2.0 for medium). |
| **Commercial Journey & CTAs** | 25.0 | Specific high-intent CTAs (+9.0), trust proofs (+6.0), direct channels (+5.0), low form friction (+5.0). |
| **Local Visibility Signals** | 25.0 | Valid LocalBusiness schema (+10.0), uniform NAP (+5.0), clickable tel & map (+5.0), declared service areas (+5.0). Fair baseline (15.0) for purely non-local platforms. |
| **Comparison & Decision Support** | 25.0 | Buyer FAQs addressing purchase objections (+10.0), pricing transparency (+8.0), comparison matrices (+7.0). |

---

## 8. Persistence & Snapshot Evolution

### 8.1 SQLite Persistence (`search_commercial.sqlite3`)
- `search_snapshots`: Snapshot metadata, target, score breakdown, confidence.
- `search_page_intents`: Per-page intent taxonomy, primary target query, secondary queries.
- `search_cannibalization`: Competing queries, URLs, similarity, risk level.
- `search_local_signals`: Local schema, NAP status, clickable phone, service areas.
- `search_commercial_audits`: Page types, CTA counts, trust proofs, friction issues.
- `search_diffs`: Baseline vs subsequent snapshot comparisons.

### 8.2 Security Hardening
All exported CSV files (`page-intents.csv`, `cannibalization.csv`, `commercial-friction.csv`, `search_comparison.csv`) apply `sanitize_csv_cell`:
- Escapes any cell beginning with `=`, `+`, `-`, `@`, `\t`, or `\r` with a leading apostrophe (`'`) to neutralize spreadsheet formula injection attacks.
