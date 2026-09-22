# AevoraSEO — functionality and skill map

This describes AevoraSEO’s crawler and the SEO workflows included in the project. The implementation status below distinguishes executable features from agent-guided workflows.

AevoraSEO is a complete SEO house supported by its own website crawler. The main workflow covers the full website strategy across SEO, AEO, GEO, entity, authority, REO/reputation, local visibility, backlinks and conversion, and produces a practical execution plan. The Python program collects observations; the skill applies specialist methods and business context. Start with [the complete SEO workflow](../playbooks/core/seo-house-workflow.md).

The backlink catalog preserves 241 PDF rows and groups them into 206 website/community entries. Complete plans select 15 or 20 relevant destinations when supported, with writing briefs, routes, restrictions and timing. [Browse the catalog](../docs/backlink-source-catalog.md) and [posting guide](../docs/backlink-posting-guide.md).

## Website crawler and scraper: implemented

| Function | What it does |
|---|---|
| Website discovery | Starts from a URL, reads robots/sitemaps, follows in-scope page links, and records discovered URLs |
| Sitemap processing | Handles XML URL sets, sitemap indexes, namespaces and gzip content, retaining URL membership and lastmod |
| Crawl controls | Page/depth/discovery/query limits, host allowlists, exclusion patterns, concurrency and request spacing |
| HTTP handling | Records status codes, redirects, loops, errors, response headers, timestamps, byte counts and hashes |
| Access diagnostics | Separates server denials, rate limits, recognizable challenge responses, robots decisions and local crawl limits |
| Retry evidence | Preserves individual HTTP attempts, including an initial 429 followed by a successful retry |
| Robots handling | Respects directives by default with a recorded explicit override for authorized crawling; treats an unavailable robots file separately from a public resource denial; defers on network/server failure and rate limits |
| HTML extraction | Titles, descriptions, meta/Open Graph fields, H1–H6, language, canonicals, hreflang, links, images, forms and JSON-LD |
| Content extraction | Body/main text, word counts, content hashes and custom CSS-selected fields; supports repeated listing cards |
| Custom scraping | Named fields such as product name, price, article title, author or selected link attributes using a JSON selector file |
| JavaScript comparison | Automatic fallback or explicit browser mode captures a second DOM representation and discovers rendered links |
| Content readiness and scrolling | Waits for a visible CSS element, samples text/link stability and performs bounded viewport scrolling |
| Readable documents | Markdown and plain-text files, plus structured documents with their source representation |
| Screenshots | Optional 1440 × 1000 browser viewport PNGs |
| Website dependencies | Public dependency loading or explicit asset/API host allowlists; supported public GET and CORS OPTIONS requests preserve needed origin-bound headers without logging their values |
| Rendering diagnostics | Records locally blocked resources, request failures, JavaScript errors and empty-content warnings |
| Internal link graph | Observed inbound/outbound links, anchors/rel attributes, checked target status and observed click depth |
| Technical findings | Uses successful rendered content for metadata/duplicate checks; preserves raw noindex; flags missing-content screens behind HTTP 200 and links pointing to them, alongside other technical candidates |
| Resume | SQLite persists processed pages and the pending queue; a resumed run can raise the page budget without refetching completed pages |
| Evidence/reporting | Raw HTML, sitemap XML, JSONL, CSV inventories, issue tables, access diagnostics and Markdown reports |
| Terminal feedback | Colorama styles interactive progress; machine-readable output remains plain |

The command-line interface is documented in `crawler.md`. The crawler does not submit forms or perform publishing actions. Resume continues the same snapshot; a fresh run is needed to refresh completed pages.

## Branded client reports: implemented

`present` exports local PDF and self-contained HTML using the official AevoraSEO logo, black/red palette, editorial cover, linked contents, tables, charts and evidence notes. Normal setup includes the free ReportLab renderer. `--audit` preserves a native audit’s findings; `--input` presents a reviewed strategy report. The renderer does not research, score or verify supplied claims. The assistant prepares the analysis and checks every rendered page before delivery. See [report content and export](../docs/branded-reports.md) for formats, font limits and HTML fallback.

## Review and implementation: implemented

See [operations](../docs/operations.md) for readiness reports, source-page backlink checks, snapshot comparisons, bounded repeat audits and reviewed local/SFTP/FTPS content-file changes. Changes retain original bytes, verify reviewed hashes and refuse to overwrite later edits during rollback. Remote adapters need compatible hosting; database/CMS editing and arbitrary third-party account automation remain separate.

## Reputation discovery, backlinks and rating: implemented

The [shared discovery workflow](../docs/discovery-and-competitors.md) collects bounded search leads through native public-search adapters, available host browser/search tools, saved result HTML or supplied URLs/CSVs. The agent chooses from its actual available capabilities; a particular browser or paid search API is not required. Source failures retain evidence and use permitted fallbacks. Search snippets are leads until the native crawler checks the source page.

The [native reputation system](reputation.md) verifies backlinks and page mentions, follows bounded redirect hosts and checks late JavaScript links. It calculates the AevoraSEO Reputation Score with its sensitivity range, confidence and transparent rubric. Own-site sources are excluded; repeated publishers are grouped and related sources cannot supply independent proof. `search-plan` prepares navigation URLs and a requested page budget; it does not execute a search. Native discovery is a bounded sample, never a complete backlink index.

| Function | What it does |
|---|---|
| Direct backlink verification | Inspects external HTML, extracts anchor text, rel tokens, dofollow status, context excerpts, and target paths |
| Brand mention extraction | Discovers target brand and alias occurrences without direct links in readable body text |
| Source classification | Heuristically categorizes sources as editorial, directory, profile, community, or owned |
| Ownership proof boundary | Excludes target domain, subdomains, and explicit related hosts from independent editorial proof |
| Conservative reputation scoring | Implements Model 1.1 with supported points, evidence adjustments, confidence ceiling (49/100), and sensitivity range |
| Opportunity pipeline | Cross-references unreached discovery leads against the 206-site catalog (`posting-sites.json`) |
| SQLite persistence | Persists snapshots, sources, links, mentions, assessments, and diffs to `backlinks.sqlite3` and `reputation.sqlite3` |
| Snapshot diff engine (`reputation-compare`) | Compares temporal snapshots for score deltas, added/lost/retained links/mentions, and converted opportunities |
| Export & security hardening | Emits Terminal, JSON, CSV, and Markdown with mandatory sanitization against CSV formula injection |

## Posting catalog and shortlist helper: implemented

`scripts/backlink_sources.py` filters the local catalog and builds a business-specific shortlist from documented, sufficiently recent routes. It checks topic/market fit, known prerequisites and cost status; emits per-format writing briefs, posting instructions and a capacity-based calendar; and reports shortages instead of filling them with unqualified sites. It does not crawl the supplied business, operate accounts or generate finished articles. Those are separate agent tasks using the actual website and current platform guidance. Sheet DR values do not affect selection.

The optional `scripts/import_backlink_pdf.py` reads visible PDF rows, preserves duplicate records and detects conflicting DR claims. It needs `pypdf` only for importing a new PDF; normal browsing and planning use the standard library.

## AEO and GEO intelligence: implemented

The native AEO/GEO intelligence engine evaluates answer readiness, question coverage, direct-answer proximity, structured-data validity, entity clarity, citation and source readiness, and AI crawler accessibility.

| Function | What it does |
|---|---|
| AevoraSEO AEO Readiness Score | Evaluates 0–100 readiness across Answer Readiness, Question Coverage, Content Structure, Schema Quality, and AI Crawler Accessibility |
| AevoraSEO GEO Signal Score | Evaluates 0–100 signal strength across Entity Clarity, Source Readiness, Factual Specificity, and Content Depth & Extractability |
| Direct answer detection | Identifies adjacent definition/answer paragraphs (10–60 words) or structured lists following interrogative headings |
| AI crawler accessibility matrix | Audits 10 AI bots (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, etc.) against robots.txt, robots meta, and X-Robots-Tag |
| Structured schema audit | Validates required and recommended properties, detects syntax errors, and checks title/canonical URL consistency |
| Cross-page entity conflict audit | Flags naming contradictions across pages for declared Organization and Person entities |
| SQLite persistence | Persists snapshots, pages, questions, entities, and diffs to `crawl.sqlite3` and `aeo.sqlite3` |
| Snapshot diff engine (`aeo-compare`) | Compares two crawl snapshots for AEO/GEO deltas, categorized states (ADDED, REMOVED, IMPROVED, REGRESSED, UNCHANGED), and attributed evidence |

See [AEO & GEO methodology](aeo-geo.md) for detailed scoring formulas and boundary definitions.

## Entity, Authority and Knowledge Intelligence: implemented

The native entity intelligence engine extracts, models, and audits entity identities, semantic relationships, cross-page brand consistency, and external authority signals.

| Function | What it does |
|---|---|
| Typed entity extraction | Extracts Organization, Person, Product, Service, Place, and Article entities from Schema.org JSON-LD, Microdata, and meta tags |
| SameAs authority discovery | Classifies external profiles across Wikidata, Wikipedia, LinkedIn, Crunchbase, GitHub, etc., and flags missing standard profiles |
| Knowledge graph construction | Maps directed semantic relationships (`FOUNDED_BY`, `WORKS_FOR`, `AUTHORED_BY`, `PUBLISHED_BY`, `SAME_AS`) and calculates network density and central entities |
| Cross-page consistency audit | Flags contradictory organization names, NAP mismatches, broken sameAs targets, and missing recommended entity pages (`/about`, `/team`, `/contact`, `/reviews`) |
| AevoraSEO Entity & Authority Score | Evaluates 0–100 headline score across Identity Completeness, Entity Consistency, Authority Footprint, and Topical/Expert Depth |
| SQLite persistence | Persists snapshots, nodes, edges, sameAs profiles, conflicts, and diffs to `entities.sqlite3` |
| Snapshot diff engine (`entity-compare`) | Compares temporal entity snapshots for entity evolution, score deltas, added/lost sameAs, and resolved conflicts |
| Export & security hardening | Formats Terminal, JSON, Markdown, and CSV outputs with formula injection neutralization |

See [Entity & Authority methodology](entity-authority.md) for detailed technical specifications.

## Search, Local & Commercial Intelligence: implemented

The native Search, Local & Commercial intelligence engine analyzes search intent taxonomy, target query extraction, keyword cannibalization, local search visibility signals (LocalBusiness schema, uniform NAP, clickable tel, map embeds), commercial conversion journeys, CTA friction, and comparison decision support.

| Function | What it does |
|---|---|
| Search intent taxonomy | Classifies pages deterministically into Informational, Commercial Investigation, Transactional, Navigational, and Local intents |
| Query extraction & mapping | Extracts 2-to-5 word primary target queries and secondary candidate phrases from H1, Title, meta description, and URL slugs |
| Keyword cannibalization detection | Detects internal pages competing for identical queries and intents with Jaccard token similarity and assigns High/Medium/Low risk levels |
| Local visibility audit | Validates Schema.org `LocalBusiness` and specialized sub-types (`Dentist`, `Store`, etc.), audits NAP uniformity, clickable telephone (`tel:`), Google Maps embeds, and service-area declarations |
| Commercial journey & CTA audit | Classifies high-intent specific CTAs vs generic buttons, detects trust proof proximity (reviews, credentials, guarantees), and audits form friction |
| Decision & comparison support | Audits head-to-head comparison pages, structured feature matrices (`<table>`), evaluated alternatives, and buyer question (FAQ) objection coverage |
| AevoraSEO Search & Commercial Score | Evaluates 0–100 headline score across Intent & Query Targeting, Commercial Journey & CTAs, Local Visibility Signals, and Comparison & Buyer Decisions |
| SQLite persistence | Persists snapshots, page intents, cannibalizations, local signals, commercial audits, and diffs to `search_commercial.sqlite3` |
| Snapshot diff engine (`search-compare`) | Compares temporal snapshots for score deltas, intent shifts, resolved/new cannibalizations, and commercial improvements |
| Export & security hardening | Emits Terminal, JSON, Markdown, and CSV outputs with CSV formula injection neutralization |

See [Search & Commercial methodology](search-commercial.md) for detailed technical specifications.

## Content & Optimization Intelligence: implemented

The native Content & Optimization intelligence engine audits content quality, title tags, meta descriptions, single H1 and heading hierarchies, direct answer definitions, FAQ objection opportunities, topic clusters, intent-matched schema recommendations, content briefs, and 30/60/90-day roadmaps.

| Function | What it does |
|---|---|
| Title tag optimization | Audits length (45–65 chars optimal), brand placement, primary query alignment, and repetitive keyword stuffing |
| Meta description optimization | Audits length (120–160 chars optimal), action-oriented CTA verb detection, and query relevance |
| Heading hierarchy audit | Enforces single H1, validates sequential nesting without skipped levels (e.g. H1 -> H3), detects question headings and empty headings |
| Direct answer & definition engineering | Identifies definition phrases (`is a`, `refers to`) and prescribes 40–60 word answer boxes, procedural lists, and comparison tables |
| FAQ & buyer objection handling | Discovers missing pricing transparency, guarantee/SLA terms, and support details on transactional pages |
| Internal link & orphan optimization | Maps global internal link graph, detects orphan pages (0 inbound links), crawl depth, and flags generic anchors (`click here`) |
| Topic cluster analysis | Groups pages by path and topic, maps pillar hubs to supporting spokes, and computes cluster health scores (0–100) |
| Intent-matched schema recommender | Suggests `Article`, `Service`, `Product`, `LocalBusiness`, `FAQPage`, `Course`, and `HowTo` structured data |
| Content briefs & editorial outlines | Generates grounded briefs and heading-by-heading outlines with 40–60 word answer box targets, bullet points, and CTA placement |
| Content gap & refresh prioritization | Identifies thin content (< 250w, < 500w), aging year references ($\le 2023$), and missing comparison/FAQ sections |
| AevoraSEO Content Optimization Score | Evaluates 0–100 headline score across Metadata & Headings, Content Depth & Answers, Link & Cluster Health, and Schema Coverage |
| SQLite persistence | Persists snapshots, page audits, answer opportunities, clusters, briefs, and diffs to `content_optimization.sqlite3` |
| Snapshot diff engine (`optimize-compare`) | Compares temporal snapshots for score deltas, resolved deficiencies, new regressions, and cluster evolution |
| Export & security hardening | Emits Terminal, JSON, Markdown, and CSV outputs with CSV formula injection neutralization |

See [Content & Optimization methodology](content-optimization.md) for detailed technical specifications.

## SEO workflows included

These are agent workflows supported by the reference library. They are available for analysis and planning; their presence does not mean the standalone Python script automatically completes every task.

| Skill area | What the workflow covers | Evidence it needs |
|---|---|---|
| Full-site SEO audit | Combine technical, on-page, content, keyword, competitor, local, authority and conversion findings into priorities | Crawl plus whatever performance/market evidence the requested sections require |
| Technical SEO | Crawlability, indexing signals, status codes, redirects, canonicals, robots, sitemaps, internal links and JavaScript checks | Raw/rendered crawl; actual indexing needs separate evidence |
| On-page SEO | Review titles, descriptions, heading hierarchy, intent alignment, content structure and relevant internal links | Page content and the intended audience/query; observed SERPs when making SERP claims |
| Content quality and E-E-A-T | Review experience/expertise evidence, authorship, review dates, originality, completeness, proof and useful answer coverage | Extracted content and verifiable business/expert evidence |
| Schema planning | Inspect current structured data, find syntax problems and propose markup suited to visible page content | JSON-LD/HTML; semantic validation remains a separate check |
| Keyword research | Discover candidate topics, classify intent, cluster keywords, defend existing winners and select business-relevant opportunities | Content can suggest topics; demand/ranking claims need dated query/keyword evidence |
| Keyword-to-page mapping | Assign a target to an existing page, new service/product page, support article, local page or other appropriate action | Page inventory, business priorities and available query evidence |
| Competitor analysis | Compare service pages, content clusters, FAQs, proof, metadata, internal links and conversion paths; identify gaps | Separate scoped crawls of named competitors; ranking/authority comparisons need separate data |
| Local SEO | Review website NAP, service areas, local pages, citations, review strategy and Google Business Profile improvement plans | Website observations and supplied local/profile/review evidence |
| Backlink audit and prospect review | Assess supplied backlinks, relevance, anchors, placements, risk, referring-domain gaps and potential prospects | Supplied backlink/prospect lists and accessible source pages; not inferred from outbound links |
| Authority and digital PR | Plan relevant associations, partnerships, editorial coverage, resource pages, founder interviews and useful third-party articles | Real business proof and identifiable relevant opportunities |
| AEO — answer engine optimization | Design clear definitions, direct answers, FAQs, process/cost/risk explanations and comparison sections | Actual page content and audience questions |
| GEO — generative engine optimization | Review source-worthiness, citation-ready material, proof, clarity and potential content improvements | Page evidence; actual AI mentions/citations require observed answers |
| Entity SEO | Clarify organization/person identity, profiles, service relationships, structured data and consistent descriptions | Website declarations and verified profiles/proof |
| Reputation SEO | Discover and verify a bounded sample of mentions, reviews, media references and third-party articles; compare brand claims | Dated discovery records and directly inspected source pages; no complete mention index |
| Conversation SEO | Map full customer questions and decision paths, objections, follow-up questions and comparisons | Customer/sales questions, supplied reviews and content evidence |
| Conversion SEO | Review calls to action, service-specific journeys, trust placement, forms and potential friction | Rendered pages; conversion performance needs analytics or business records |
| Growth planning | Build 30/60/90-day priorities, content hubs, service-page plans and traffic-to-inquiry scenarios | Baselines, resources and explicitly stated assumptions |
| Reporting and proposals | Create client reports, proposals, developer briefs, content briefs, keyword maps, content calendars, issue logs and roadmaps | Verified findings, task scope and appropriate business context |

The 500-query growth model uses “queries” to mean business inquiries/leads. That is different from search queries in Google Search Console. Future reports should use the clearer term for each measurement.

## Industry playbooks retained

Eight brief industry playbooks cover:

1. Agencies.
2. AI and SaaS companies.
3. Dental practices.
4. Ecommerce.
5. Education and courses.
6. Local businesses.
7. Medical practices.
8. Real estate.

They adapt page strategy, proof, local relevance and conversion focus. They are concise guidance, not separate trained models or completed industry automation systems. Report templates, example report structures and the backlink source library were also retained.

## Functions needing separate evidence or further engineering

| Capability | Current position |
|---|---|
| Search volume and rankings | No search/rank database is implemented; use supplied dated evidence |
| Complete inbound backlink graph | No web-wide backlink index is implemented |
| Traffic, conversions and GBP performance | The website crawler cannot observe private account measurements; supplied exports can support analysis |
| Search-engine/Maps/social product scraping | Bounded native search-result adapters and host browser/search imports are implemented; dedicated Maps/social collectors are not |
| AI-answer visibility/history | Readiness review is available; actual visibility needs captured answer evidence |
| Core Web Vitals and performance audits | HTTP elapsed time is recorded; Lighthouse/field measurement is not implemented |
| Complete schema validation | JSON parsing is implemented; semantic and rich-result validation is separate |
| Authenticated workflows | No account login, session import, consent-click or form-submission automation |
| Interaction-heavy harvesting | Bounded scrolling is available; no general click recipes or unlimited infinite-scroll engine |
| PDF/media analysis | No downloaded PDF/image/video extraction pipeline |
| Refresh and monitoring | Fresh snapshot comparisons and bounded foreground watch loops are implemented; installing a scheduler or sending notifications is separate |
| Large distributed service | The current engine runs locally with bounded queues and in-memory reporting |

No hosted scraping provider, plugin or external skill is needed to run the native crawler. BeautifulSoup and Colorama are ordinary local Python libraries; Playwright and Chromium are optional local rendering components. A website's own externally hosted scripts or public content API are website dependencies, not outsourced scraping services.

Deep reputation research now has two native helpers: `research-plan` generates matching query families and bounded cohort budgets after profile review; `compare-reputation` recalculates verified evidence and checks method/date/coverage comparability before assigning a within-sample position. Browser actions and semantic source review remain the host assistant's work. See [deep research](../docs/deep-research.md).
