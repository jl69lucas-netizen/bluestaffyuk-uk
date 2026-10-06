# London page · gate report · 2026-10-06

Page `/uk-locations/blue-staffy-puppies-london/` · branch `london-components` · gated at HEAD `5b20b9cc` · verdict **PASS**. The breeder approved the page on 2026-10-06 (`docs/reference/answer-board/answers/final-approval-blue-staffy-puppies-london-2026-10-06.md`), so `noindex, follow` is off: the built page prints one robots meta, `index, follow`, and `location-sitemap.xml` lists it. This short close re-gated the indexable page. The earlier close was gated at `f7d88055`.

## The double gate run (row 17), with the page-run record

Two runs, identical, at `5b20b9cc`, with the record checked (`npm run gate:page -- blue-staffy-puppies-london`, exit 0).

| Step | Problems per run | Result |
|---|---|---|
| Duplicate body text (51 pages) | 0 · 0 | PASS |
| Duplicate headers (51 pages) | 0 · 0 | PASS |
| Final page audit (location) | 0 · 0 | PASS |
| Static scan (71 source files, 1 built page) | 1 · 1 (a WARN: icon baseline in the puppy cards) | PASS |
| AEO audit | 0 · 0 | PASS |
| Evidence audit | 0 · 0 | PASS |
| Board gate (22 sections, 92 headings, 35 assets) | 0 · 0 | PASS |
| Listed (rebuilt and render targets) | 0 · 0 | PASS |
| Page-run record | 0 · 0 | PASS |
| check:all (run once) | 0 | PASS |

## The page-run record (rows 1, 14, 15, 18)

Session open; impeccable, fourth run (2026-10-06b: 1 finding, 1 fixed, `docs/reports/impeccable-london-2026-10-06b.md`: the dial now scrolls its own box to show the row it marks, `f0d155b1`); frontend-design, fourth run (2026-10-06b: 0 findings, `docs/reports/frontend-design-london-2026-10-06b.md`); and verification before completion at `dbc05a46` (build, check:all with 27 examined, and the gate, all exit 0). `page_run_record.py --check`: 0 problems.

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
| M13 | Slugs whose rendered output changed | 38 (base foundation → head 5b20b9ccc887376f3ba6d9db28002d4f0e838dd1) · IndexNow submitted: NOT FETCHED — project 6 | REPORTED | available-puppies, available-puppies/byrd, available-puppies/cheryl, available-puppies/christa, available-puppies/ince, available-puppies/roman, available-puppies/vennie, blog, blue-staffy-blog-guides, blue-staffy-health-uk, blue-staffy-pup-sale-uk, blue-staffy-uk-breeders, buy-blue-staffy-puppies-uk, buy-staffy-puppies-for-sale-uk, how-to-choose-the-right-blue-staffy-puppy-for-your-family, index, privacy-policy-uk, thank-you-blue-staffy-puppies-journey, uk-blue-staffy-breeders-contact, uk-blue-staffy-puppy-buying-guide, uk-locations, uk-locations/blue-staffies-newcastle-under-lyme, uk-locations/blue-staffy-puppies-aberdeen, uk-locations/blue-staffy-puppies-dundee, uk-locations/blue-staffy-puppies-edinburgh, uk-locations/blue-staffy-puppies-for-sale-in-leicester, uk-locations/blue-staffy-puppies-for-sale-leeds, uk-locations/blue-staffy-puppies-hull, uk-locations/blue-staffy-puppies-inverness, uk-locations/blue-staffy-puppies-london, uk-locations/blue-staffy-puppies-middlesbrough, uk-locations/blue-staffy-puppies-oxford, uk-locations/blue-staffy-puppies-sunderland, uk-locations/blue-staffy-puppies-uk, uk-locations/blue-staffy-puppies-york, uk-locations/staffy-breeding-dogs-glasgow, uk-locations/staffy-puppies-cardiff-wales, uk-staffordshire-bull-terrier-guide |
| M18 | Untested rules in the rule index | 14 of 87 rules | REPORTED | design-context-read-first, entity-4-move-loop, header-style-declared, image-keyword-distribution, link-first-anchors, meaningful-words-no-stop-words, no-credential-in-a-committed-file, read-card-thumb-is-target-hero, release-guarded-publication, same-content-on-redesign, src-pages-is-deployed, verify-the-gate-first, visual-companion-always, visual-first-workflow |

## Other checks at the final HEAD

- `npm run test:render:pages` on the close build: 63 passed; 0 blocking, 209 advisory rows (the scorecards rewrote identical).
- `python3 -m pytest tests/py -q`: 7,696 passed, 18 skipped, 1 xfailed.
- `npm run test:render:city`: 52 passed, 52 skipped, 0 failed, 0 flaky, including the new "the dial keeps its current row in view" (20 rows examined on London) and the touching-pairs scroll-spy test.
- `npm run check:sitemaps`: 63 built pages, 5 shards, 37 sitemap urls, 0 problems; London in `location-sitemap.xml`.
- `python3 scripts/measurement_ledger.py p5 --require-pages`: failed none, stale none, empty none.
- `python3 scripts/rendered_changes.py --base foundation --json`: 38 slugs changed (the M13 row).

## Open items

- The delivery section's board WARN (210 prose words against its 171–209 band) is gone: the map's note lost two words and delivery measures 208 (board revision 43, `fbf80a9c`).
- The city render suite's flakes are fixed in the harness and the scroll spy, not re-run away (lessons entry 20; `d64ed4c7`, `9010e4f4`).
- `noindex` is off: the page is indexable and in the sitemap (`f3031626`; board revision 44 records the approval).
- Known Issue 100 (new): the puppy cards carry no photo of each pup, deferred by the breeder to the post-launch refinement (project 6).
- Known Issue 101 (new): `PageDial.astro` on the twelve pre-project-5 pages has the batch-only scroll spy `9010e4f4` fixed for the city pages. Not gated.
- Known Issue 99: tune the location word-count ceilings before the next city.
- Lessons: `docs/reference/lessons.md` (21 entries; 8 marked "not gated").
- No push and no IndexNow until project 6.
