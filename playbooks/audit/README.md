# Website Audit Playbooks & Checklists

This directory contains operational playbooks and checklists for conducting comprehensive website SEO, AEO, and technical audits.

---

## 1. Technical SEO & Architecture

### Crawlability and Indexing Audit
Checks whether search engines can discover, crawl, render, and index important pages.
- **Checks**: Sitemap, robots.txt, noindex, canonical, status codes, internal links, JS rendering, blocked resources, orphan pages.
- **Critical Issues**: Money pages blocked, noindexed, canonicalized away, broken, or missing from crawl path.
- **Output**: URL, issue, evidence, impact, fix, priority.

### Page Speed and Core Web Vitals Audit
Audits performance issues that affect UX, conversion, and search ranking signals.
- **Metrics**: LCP (Largest Contentful Paint), INP (Interaction to Next Paint), CLS (Cumulative Layout Shift), TTFB (Time to First Byte), image weight, JS bundle size, render-blocking resources, web fonts, mobile layout responsiveness.
- **Priority**: Fix money pages and conversion landing pages first.
- **Output**: Metric, affected template/page, cause, fix, priority.

### Internal Linking & Hierarchy Audit
Audits how authority and relevance flow across the website.
- **Checks**: Homepage to money pages, hubs to subpages, support articles to money pages, breadcrumbs, contextual anchors, orphan pages.
- **Rules**: Use natural, descriptive anchors. Avoid repetitive exact-match anchor stuffing.
- **Output**: From page, to page, anchor text, reason, priority.

---

## 2. Content & Trust Signals

### E-E-A-T and YMYL Audit
Audits experience, expertise, authoritativeness, trustworthiness, and high-stakes content requirements.
- **YMYL Areas**: Medical, dental, legal, financial, safety, government, health, and high-stakes career/education claims.
- **Required Signals**: Expert credentials, author/reviewer bylines, last updated dates, disclaimers, risk/limitations, evidence citations, customer reviews, verified sources, and clear contact information.
- **Output**: Page, missing trust signal, risk assessment, fix, priority.

---

## 3. Specialized Audit Playbooks
- [On-Page SEO Audit](on-page-seo-audit.md)
- [Technical SEO Audit](technical-seo-audit.md)
- [Content Quality Audit](content-quality-audit.md)
- [Schema.org Structured Data Audit](schema-audit.md)
- [Conversion & Commercial SEO Audit](conversion-seo-audit.md)
- [Site Audit Workflow](site-audit-workflow.md)
