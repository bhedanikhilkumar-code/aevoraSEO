# Integration & Tooling Workflows

Read only the section relevant to the current task or requested audit area.

- [AevoraSEO reputation checks](#aevoraseo-reputation-checks)
- [Working with limited access](#fallback-without-apis)
- [Google Analytics Workflow](#google-analytics)
- [Google Search Console Workflow](#google-search-console)
- [Local website collection](#native-agent-scraping)
- [PageSpeed Insights Workflow](#pagespeed-insights)

---

<a id="aevoraseo-reputation-checks"></a>

# AevoraSEO reputation checks

Use native discovery, backlink verification and reputation commands from [our scoring reference](../../references/reputation.md). Retain query, date, actual search-page coverage, source HTML and attributable review judgments.

Compare observed links, mentions, relevance, placement context and independent proof. Use similar scope for competitors and disclose unreadable sources. Position is not authority; a candidate or snippet is not a backlink.

Deliver the conservative headline with its status, range, confidence, coverage, strongest sources and practical actions. Low-confidence headlines stay below 50; unsupported headlines are withheld. Do not use the diagnostic sample midpoint as the overall score. Apply identical rules to every site. Bring separate evidence for traffic, keywords, customer reviews and actual search visibility.

---

<a id="fallback-without-apis"></a>

# Working with limited access

The local crawler needs no remote API. If it cannot run, identify the actual reason: missing local libraries, no network access, robots restrictions, HTTP denial, or a rendering limitation. Keep failures and missing fields separate from site defects.

Use supplied crawl/HTML files where available. For performance questions, use supplied GSC, analytics or GBP exports with dates and definitions. For backlink questions, inspect supplied link evidence; do not treat the site's outbound links as its inbound backlink profile.

When no usable evidence exists, provide a concrete manual plan and label the result advisory. Do not claim an audit, ranking history, traffic estimate, AI citation, or complete site inventory was measured.

---

<a id="google-analytics"></a>

# Google Analytics Workflow

How AevoraSEO should use GA4 data.

---

## Key Data

Organic landing pages, sessions, engagement, conversions, events, source/medium, paths, and revenue where relevant.

## Use Cases

Find pages with traffic but low conversion, conversion tracking gaps, and landing page quality issues.

## Output

Tie SEO traffic to business outcomes, not vanity sessions.

---

<a id="google-search-console"></a>

# Google Search Console Workflow

How AevoraSEO should use GSC exports or access.

---

## Key Data

Queries, pages, clicks, impressions, CTR, average position, countries, devices, and dates.

## Use Cases

Find existing winners, fastest wins, low CTR pages, cannibalization hints, pages with impressions but weak clicks, and pages needing refresh.

## Output

Create GSC opportunity table: query, page, impressions, clicks, CTR, position, issue, action.

---

<a id="native-agent-scraping"></a>

# Local website collection

Use `scripts/crawl.py` as the website collection engine. The complete command contract is in `references/crawler.md` from the skill root. Inspect saved HTML and `pages.jsonl` when a finding is uncertain; compare optional rendered output for JavaScript sites.

Scope each competitor or known proof-page domain separately. For custom fields, supply a CSS-selector JSON file. The crawler follows links; it does not discover every competitor on the internet or automate SERP/Maps/social products. Use supplied dated observations or exports for those questions.

---

<a id="pagespeed-insights"></a>

# PageSpeed Insights Workflow

How AevoraSEO should use PageSpeed and Core Web Vitals data.

---

## Metrics

LCP, INP, CLS, TTFB, mobile/desktop performance, field data, lab data.

## Use Cases

Identify page speed issues that hurt UX, crawl efficiency, and conversion.

## Caution

Do not make speed the whole SEO strategy. Speed is important, but weak content and architecture still need fixing.

---
