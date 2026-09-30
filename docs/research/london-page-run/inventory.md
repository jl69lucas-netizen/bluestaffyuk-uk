# London research inventory (page-run row 4)

Taken on 2026-09-30, before any fetch. Task 4 (the paid-call question) was answered in chat the same day: the user approved SERP + keyword volumes + backlinks, so the two rows the plan had as unbought now name the approved call that fetches them.

| Item | On disk | Status | What fetches it if missing |
|---|---|---|---|
| ChatGPT answer (1 engine) | data/queries/raw/blue-staffy-puppies-london/ai_engines.response.json | banked 2026-09-25; preflight exit 3 | — |
| LLM-intel file | docs/research/llm-intel/blue-staffy-puppies-london-2026-09-25.json | banked; page_source provisional (no question file then) | bsuk-llm-keyword-intel (Task 11), no new call |
| Google SERP + PAA, "blue staffy puppies london" | none | missing; preflight exit 0 | Task 5 (paid, $0.01) |
| Google SERP, "staffy puppies for sale london" (registry) | data/queries/raw/registry-staffy-puppies-for-sale-london/serp_google.response.json | banked 2026-09-23; a different keyword | gap scan only; never the section count |
| Bing top 10 | none | missing | Task 7 (free, browser) |
| Competitor pages | none under data/queries/cache/blue-staffy-puppies-london/ | missing | Task 8 (curl first) |
| Reddit threads | none | missing | Task 9 (bsuk-reddit-threads) |
| Competitor reports (registry) | docs/research/competitors/*.md | banked 2026-09-23/25 | bsuk-competitor-intel only for a registry competitor with no report |
| Gap matrix / keyword gap | docs/research/gap-matrix-2026-09-25.md, keyword-gap-2026-09-25.md | banked; London 12/20 | — |
| Cluster strategy row | docs/superpowers/sessions/2026-09-25-location-pages-strategy.md (London, line 107) | banked | — |
| Keyword volumes | none | missing; no guarded source existed before 2026-09-30 | the user-approved DataForSEO search-volume call (Task 4 answer, 2026-09-30), through a new `keyword_volume` spend-guard source |
| Authority / referring domains | none | missing; no guarded source existed before 2026-09-30 | the user-approved DataForSEO backlinks call for the top-5 competitor domains (Task 4 answer, 2026-09-30), through a new `backlinks` spend-guard source |
| Search Console baseline | none | NOT FETCHED — GSC property unverified (domain expired); no exports on disk | project 6 |
| LLM mentions | none | NOT FETCHED — llm_mentions only once BSUK's domain is live (project 6) | project 6 |
