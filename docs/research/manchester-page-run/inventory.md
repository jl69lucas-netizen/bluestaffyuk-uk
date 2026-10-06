# Manchester research inventory (page-run row 4)

Taken on 2026-10-07, before any fetch, from what is on disk for `blue-staffy-puppies-manchester-uk`. The intake (row 2) is in `intake.txt` beside this file: mode stub, robots `noindex, follow`, board none, built page fresh. The paid-call question (plan Task 5) has not been asked yet, so every unbought row names that call and waits on the user's approval.

Spend-guard preflights, run 2026-10-07 (`python3 scripts/query_augment.py --preflight blue-staffy-puppies-manchester-uk --source <s>`):

| Source | Guard says | Exit |
|---|---|---|
| serp_google | cached — make no call | 3 |
| ai_engines | cached — make no call | 3 |
| keyword_volume | proceed | 0 |
| backlinks | proceed | 0 |

| Item | On disk | Status | What fetches it if missing |
|---|---|---|---|
| ChatGPT answer (1 engine) | data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.response.json; ai_engines.json (16 questions) | banked (response 2026-09-25, questions 2026-09-23); preflight exit 3 | — |
| LLM-intel file | docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json (and the earlier -2026-09-23.json) | banked; page_source question-file, provisional; bsuk_cited false | bsuk-llm-keyword-intel (Task 7), no new call |
| Google SERP + PAA, "blue staffy puppies manchester" | data/queries/raw/blue-staffy-puppies-manchester-uk/serp_google.response.json (12 items, one people_also_ask block); serp_google.json (12 questions) | banked 2026-09-23 (14 days old); preflight exit 3 | optional `--refresh` in Task 5 (paid, $0.01), only on the user's approval |
| Google SERP, "staffy puppies for sale manchester" (registry) | data/queries/raw/registry-staffy-puppies-for-sale-manchester/serp_google.response.json | banked 2026-09-23; a different keyword | gap scan only; never the section count |
| Bing top 10 | data/queries/raw/blue-staffy-puppies-manchester-uk/serp_bing.json (10 results, no PAA box); serp_bing.response.json | banked 2026-09-23, read free in the built-in browser (cc=GB) after the paid DataForSEO Bing call returned off-topic results | — |
| Competitor pages | data/queries/cache/blue-staffy-puppies-manchester-uk/1.html … 8.html (8 pages, saved 2026-09-23); data/queries/raw/blue-staffy-puppies-manchester-uk/competitors.json (8 pages with metrics, written 2026-09-27) | banked, except Freeads (3.html, 5,899 bytes): the saved page is a "Just a moment..." bot challenge, `blocked: true`, no headings or prose | Task 4: a free Playwright capture of the Freeads page, Firecrawl last |
| Competitor `words` and `word_target` in the question file | data/queries/blue-staffy-puppies-manchester-uk.json carries `section_target` and `extra_sections`, but no `word_target` and no per-competitor `words` | missing; the question file predates the London-format metrics (fetched 2026-09-23) | Task 4: `python3 scripts/query_augment.py --competitor-metrics blue-staffy-puppies-manchester-uk` (free) |
| Reddit threads | data/queries/raw/blue-staffy-puppies-manchester-uk/threads.json (8 threads, 21 questions, none stale) | banked 2026-09-23 | — |
| Competitor reports (registry) | docs/research/competitors/*.md; 15 name Manchester (champdogs, dogstrust, foreverpuppy, freeads, gumtree, pdsa, petify, pets4homes, preloved, puppies, royalkennelclub, staffie-owners, trojanstaffuk, ukpets, ukstaffypups) | banked 2026-09-23/25 | bsuk-competitor-intel only for a registry competitor with no report |
| Gap matrix / keyword gap | docs/research/gap-matrix-2026-09-25.md (Manchester city 11/20, line 170; "staffies in manchester" 1/19 low, line 109); docs/research/keyword-gap-2026-09-25.md (line 27, "staffordshire bull terrier puppies for salein manchester greater manchester", 10 (3+2+3+2) high, the row's own spelling) | banked | — |
| Cluster strategy row | docs/superpowers/sessions/2026-09-25-location-pages-strategy.md (Manchester, line 118: transactional, local; city spoke → UK hub, listing, buying guide; rebuild (stub, project 5)) | banked | — |
| URL decision | docs/research/2026-09-26-url-family-decision.md (line 39: keep the slug; rebuild the stub); no data/redirects.json row; `npm run check:redirects` exit 0 | decided | — |
| Migrated facts | data/facts/blue-staffy-puppies-manchester-uk.json (0 prices, 0 names, 0 tests, 0 creds, 0 images, 0 embeds, 0 text) | extracted 2026-10-07; the stub body carries no facts | — |
| Keyword volumes (keyword universe, Google Ads, UK, en) | none | NOT FETCHED — not bought yet — awaiting the user's approval of the paid calls (plan Task 5); the keyword_volume preflight ran 2026-10-07 and returned proceed (exit 0), and no call was made | Task 5: DataForSEO search volume through the `keyword_volume` spend-guard source ($0.10 typical) |
| Neighbourhood terms (Greater Manchester, as London's block 3d) | none | NOT FETCHED — not bought yet — awaiting the user's approval of the paid calls (plan Task 5); the keyword_volume preflight ran 2026-10-07 and returned proceed (exit 0), and no call was made | Task 5: DataForSEO search volume through the `keyword_volume` spend-guard source ($0.10) |
| Authority / referring domains (top-5 competitor domains) | none | NOT FETCHED — not bought yet — awaiting the user's approval of the paid calls (plan Task 5); the backlinks preflight ran 2026-10-07 and returned proceed (exit 0), and no call was made | Task 5: DataForSEO backlinks through the `backlinks` spend-guard source ($0.05) |
| Search Console baseline | none | NOT FETCHED — GSC property unverified (domain expired); no exports on disk | project 6 |
| LLM mentions | none | NOT FETCHED — llm_mentions only once BSUK's domain is live (project 6) | project 6 |

Note for the controller: the plan's Task 3 brief counts 5 banked threads; `threads.json` on disk holds 8 threads (21 questions, none stale), and this table records what is on disk.
