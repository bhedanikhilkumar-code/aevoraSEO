# Complete website SEO plan

## Business goal and scope

Website, audience/market, important products/services, conversion goal, timeframe, capacity, evidence dates and crawl/sample limits.

## Executive priorities

The main opportunities, evidenced blockers and the first actions. Explain the business reason for their order.

## Coverage across the SEO house

| Area | Assessment status | Evidence/findings | Action or next evidence needed |
|---|---|---|---|
| Technical SEO | | | |
| On-page SEO | | | |
| Architecture/internal links | | | |
| Keywords and intent | | | |
| Content/E-E-A-T | | | |
| Structured data | | | |
| AEO | | | |
| GEO | | | |
| Entity SEO | | | |
| Authority / authority for answers | | | |
| REO / reputation | | | |
| Local SEO | | | |
| Backlinks / digital PR | | | |
| Competitors | | | |
| Conversion | | | |
| Measurement | | | |

## Page, content and answer plan

| Current/proposed URL | Intent and query/question cluster | Recommended change | Proof/content brief | Internal links | Schema/CTA | Acceptance check |
|---|---|---|---|---|---|---|

## Entity, authority and reputation

| Entity/claim/asset | Current evidence | Gap | Recommended page/profile/proof action | Owner | Verification |
|---|---|---|---|---|---|

## Backlink and prospect plan

### Current evidence

Include this section in every general website audit. State capture date, model version, conservative headline/status, sensitivity range, confidence, checked sources, conclusive checks and actual discovery coverage. Low-confidence headlines remain below 50. Withhold unsupported scores; do not substitute a higher diagnostic sample midpoint.

| Source URL | Target URL or observed mention | Evidence/date | Link attributes | Source relationship | Verification limits | Next action |
|---|---|---|---|---|---|---|

Separate verified backlinks, mentions without observed links, owned/affiliated sources and unverified candidates. Assess independent proof and profile consistency. These are observed sample counts, not a whole-web total.

### Relevant prospects

Review the posting catalog and follow [the posting standard](../backlink-system/free-paid-backlink-source-library.md). Deliver 15 relevant sources, or 20 when requested and qualified, with specific writing briefs and steps; research or explain a shortfall. Keep existing verified backlinks separate. Identify exclusions with reasons and original DR claims as unverified, not measured DA.

| Website and posting route | Evidence date / authority limits | Fit / format | Target page / link rules | Title and outline | How to post / eligibility | Free terms / effort | Week / owner | Follow-up check |
|---|---|---|---|---|---|---|---|---|

## Competitor websites and responses

Name the relevant companies and exact comparison pages. Explain selection, capture date, service/market comparability and evidence limits. If their reputation evidence is incomplete or differently sampled, mark numerical comparisons inconclusive. Do not claim observed ranking or traffic without that evidence.

| Competitor and page URL | Why comparable | Observed strength/proof | Client strength or gap | Recommended response | Priority | Evidence/date |
|---|---|---|---|---|---|---|

## 30/60/90-day execution

| Phase/week | URL or asset | Action and reason | Owner | Dependency | Effort/capacity | Acceptance check | KPI |
|---|---|---|---|---|---|---|---|

## Measurement and review

| KPI | Definition | Baseline/date/source | Target or hypothesis | Review date | Interpretation limits |
|---|---|---|---|---|---|

## Missing evidence and next checks

Identify remaining data needs, which conclusions they limit, and the smallest next step to resolve each. Do not turn unknowns into zero scores or fabricate ranking/traffic/link metrics.

---

## Supporting Export Template Schemas

### Backlink Prospect Header (`backlink-prospect-template.csv`)
```csv
Website,Posting URL,Format,Why It Fits,Topic or Title,Outline,Target Page,Target Page Status,Permitted Link Location,Anchor Guidance,How To Post,Cost Status,Eligibility,Editorial or Owned Role,Current DA,Current DR,Metric Provider,Metric Date,Sheet DR Unverified,Guidance Checked On,Guidance Sources,Priority,Planned Week,Owner,Status,Live Post URL,Observed Rel,Post Check Date,Result Notes
```

### Competitor Matrix Header (`competitor-matrix-template.csv`)
```csv
Competitor,Domain,Comparable Service,Target Market,Observed Strength,Observed Weakness,Identified Gap,Recommended Response,Priority
```

### Content Calendar Header (`content-calendar-template.csv`)
```csv
Publish Date,Target Keyword,Search Intent,Topic,Title,Target URL,Content Type,Author,Status,Review Date
```

### Issue Log Header (`issue-log-template.csv`)
```csv
Issue ID,Affected URL,Category,Severity,Impact,Effort,Priority Score,Status,Owner,Resolution Date
```

### Keyword Map Header (`keyword-map-template.csv`)
```csv
Keyword,Search Intent,Monthly Volume,Current Rank,Target Page URL,Competitor URL,Business Value,Action Plan
```

### Custom Selectors Spec (`selectors-example.json`)
```json
{
  "page_heading": {"selector": "h1", "all": false},
  "prices": ".price_color, .price",
  "product_links": {"selector": "article h3 a", "attribute": "href", "all": true}
}
```
