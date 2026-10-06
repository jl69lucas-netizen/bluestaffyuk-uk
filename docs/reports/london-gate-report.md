# London page · gate report · 2026-10-06

Page `/uk-locations/blue-staffy-puppies-london/` · branch `london-components` · gated at HEAD `f7d88055` · verdict **PASS**, waiting on the breeder's final approval. The page is still `noindex, follow`: the flag comes off when she approves, and one short close then re-gates the indexable page.

## The double gate run (row 17), with the page-run record

Two runs, identical, at `f7d88055`, with the record checked.

| Step | Problems per run | Result |
|---|---|---|
| Duplicate body text (51 pages) | 0 · 0 | PASS |
| Duplicate headers (51 pages) | 0 · 0 | PASS |
| Final page audit (location) | 0 · 0 | PASS |
| Static scan | 1 · 1 (a WARN: icon baseline in the puppy cards) | PASS |
| AEO audit | 0 · 0 | PASS |
| Evidence audit | 0 · 0 | PASS |
| Board gate | 0 · 0 | PASS |
| Listed (rebuilt and render targets) | 0 · 0 | PASS |
| Page-run record | 0 · 0 | PASS |
| check:all (run once) | 0 | PASS |

## The page-run record (rows 1, 14, 15, 18)

Session open, impeccable (2026-10-06: 1 finding, 1 fixed), frontend-design (2026-10-06: 1 finding, 1 fixed) and verification before completion (build, check:all and the gate, all exit 0). `page_run_record.py --check`: 0 problems.

## Measurement ledger (row 19)

| # | Measurement | Value | Status | Detail |
|---|---|---|---|---|
| M1 | Nodes examined per check, on real pages | 46 checks, 0 at zero (run 2026-10-06, 21 pages) | PASS | — |
| M2 | Families registered vs families wired | registered 9 · wired 9 · difference ∅ | PASS | — |
| M3 | Advisory findings vs blocking failures | blocking 0 · advisory 209 (run 2026-10-06; never summed) | REPORTED | — |
| M6 | Minimum rendered text >= 12.5px | 1 of 1 pages clean (run 2026-10-06) | PASS | — |
| M8 | Gate runs per page, both clean | 1 of 1 pages: >= 2 runs, both clean | PASS | — |
| M9 | Rework rate: page vs harness, never merged | page 0.032 · harness 0.032 (window london-components) | REPORTED | — |
| M10 | Dup crossover, body and headers | body 0 · headers 0 across 1 pages | PASS | — |
| M12 | LLM visibility cells fetched / total | 1 / 1 (one engine, one query per page) | REPORTED | — |
| M13 | Slugs whose rendered output changed | 38 (base foundation → head f7d8805516cc76f8d416f04ddf338f411a2667f3) · IndexNow submitted: NOT FETCHED — project 6 | REPORTED | available-puppies, available-puppies/byrd, available-puppies/cheryl, available-puppies/christa, available-puppies/ince, available-puppies/roman, available-puppies/vennie, blog, blue-staffy-blog-guides, blue-staffy-health-uk, blue-staffy-pup-sale-uk, blue-staffy-uk-breeders, buy-blue-staffy-puppies-uk, buy-staffy-puppies-for-sale-uk, how-to-choose-the-right-blue-staffy-puppy-for-your-family, index, privacy-policy-uk, thank-you-blue-staffy-puppies-journey, uk-blue-staffy-breeders-contact, uk-blue-staffy-puppy-buying-guide, uk-locations, uk-locations/blue-staffies-newcastle-under-lyme, uk-locations/blue-staffy-puppies-aberdeen, uk-locations/blue-staffy-puppies-dundee, uk-locations/blue-staffy-puppies-edinburgh, uk-locations/blue-staffy-puppies-for-sale-in-leicester, uk-locations/blue-staffy-puppies-for-sale-leeds, uk-locations/blue-staffy-puppies-hull, uk-locations/blue-staffy-puppies-inverness, uk-locations/blue-staffy-puppies-london, uk-locations/blue-staffy-puppies-middlesbrough, uk-locations/blue-staffy-puppies-oxford, uk-locations/blue-staffy-puppies-sunderland, uk-locations/blue-staffy-puppies-uk, uk-locations/blue-staffy-puppies-york, uk-locations/staffy-breeding-dogs-glasgow, uk-locations/staffy-puppies-cardiff-wales, uk-staffordshire-bull-terrier-guide |
| M18 | Untested rules in the rule index | 14 of 87 rules | REPORTED | design-context-read-first, entity-4-move-loop, header-style-declared, image-keyword-distribution, link-first-anchors, meaningful-words-no-stop-words, no-credential-in-a-committed-file, read-card-thumb-is-target-hero, release-guarded-publication, same-content-on-redesign, src-pages-is-deployed, verify-the-gate-first, visual-companion-always, visual-first-workflow |

## Other checks at the final HEAD

- `python3 -m pytest tests/py -q`: 7,692 passed, 18 skipped, 1 xfailed.
- `npm run test:render:pages`: 63 passed; 0 blocking, 209 advisory rows.
- `npm run test:render:city`: London 0 failures in every run. The specimen page `/kit-preview/city-page/` failed one timing probe in 3 of 6 parallel runs and passed when run alone (lessons, entry 20).
- `npm run check:sitemaps`: 63 built pages, 0 problems.

## Open items

- The delivery section is 210 prose words against its 171–209 band (a board WARN), because the map's caption and note added words.
- Known Issue 99: tune the location word-count ceilings before the next city.
- Lessons: `docs/reference/lessons.md` (21 entries; 8 marked "not gated").
- No push and no IndexNow until project 6.
