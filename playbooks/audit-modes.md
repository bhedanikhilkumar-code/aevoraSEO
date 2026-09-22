# Audit Modes and Capability Onboarding

## Audit Modes

1. **Local crawl:** default for a website URL; raw HTML, sitemaps, robots, links, metadata and content evidence.
2. **Local rendered comparison:** optional local Chromium produces a second representation for JavaScript-heavy pages. Preserve raw observations.
3. **Local crawl plus files:** add supplied GSC, analytics, review, search-observation or backlink exports. Attribute metrics to their actual source/date.
4. **Files only:** analyze supplied artifacts when live access is unavailable. Do not label historical data as a current crawl.
5. **Advisory:** outline checks when there is no executable runtime and no usable data. Do not claim a completed audit.

No mode implies complete information. Report coverage and unverified measurements with each result.

## Capability Detection

Run `python3 scripts/check_environment.py` from the skill folder, then inspect the task's supplied URL, goal and files. The core engine needs Python and BeautifulSoup; Colorama only affects terminal styling. Local Playwright plus installed Chromium enables the optional renderer.

Check output-directory write access and use a bounded crawl to establish network reachability. Do not turn a missing dependency or blocked response into an SEO finding. Follow `docs/setup.md` for dependencies.

The executable capability contract and limitations are in `references/crawler.md` and `references/measurement-boundaries.md`. Never infer availability of rankings, analytics, Maps, backlink databases or AI-answer visibility merely because the crawler runs.

## Onboarding

Use the website URL and main goal already provided. Ask for a missing URL; ask about location only when it materially changes local intent. Start a bounded local crawl and assess coverage before expanding. No key, plugin or remote scraping account is part of onboarding.

Use `scripts/check_environment.py` to identify Python/library availability without inspecting secrets. Follow `docs/setup.md` for local dependencies. Collect only the supplied exports needed for a performance or backlink question. A website crawl can proceed without those exports.

## Executable Code and Reference Depth

`scripts/crawl.py` and `src/aevoraseo/` implement website crawling, extraction, analysis and exports. `tests/` checks their observable behavior. `references/crawler.md` defines the interface and its limits.

The retained audit, strategy, keyword, competitor, local, backlink and AI-search modules are agent playbooks. Some are deliberately concise prompts for expert review. Their presence does not mean every described check has executable automation. The crawler's output schema and measurement boundaries determine which observations are actually available.
