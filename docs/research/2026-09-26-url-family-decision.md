# URL-Family Decision — the City Cluster and the Comparison Slugs

**Date:** 2026-09-26 · **Question:** before the first project 5 city board, which URL does each
page in the location family keep, which redirects exist or are needed, and what slug do the
comparison pages take? One table, one recommendation (the page-build brief, §4).

**Read from:** `data/locations.json` (28 rows), `data/redirects.json` and the `public/_redirects`
it generates, `data/page-map.json` (the old site's URLs and their Search Console baselines),
`dist/` as built on 2026-09-26 (sitemaps and in-body links), the approved strategy
`docs/superpowers/sessions/2026-09-25-location-pages-strategy.md` (build order and intent), and
Known Issues 16, 59 and 62 in `docs/reference/session-log.md`.

**Not measured:** clicks, impressions, CTR and position per URL, on Google and on Bing, and the
query rows for the family stem — `NOT FETCHED — GSC property unverified (domain expired); no
exports on disk` (the barrier every `data/page-map.json` row records). Backlinks per URL —
`NOT FETCHED — no backlink export; a paid backlinks call was never approved`. This decision is
therefore made on intent, on-disk state and internal links, and is re-checked when project 6
reads Search Console.

## The recommendation

| Option | What changes | Why | Trade-off |
|---|---|---|---|
| **(a) Keep all 28 slugs; no rename, no new redirect; both intent pairs stay two pages (Recommended)** | nothing in `data/redirects.json`; each board keeps its row's slug and canonical | 11 URLs are indexable and in the sitemap, and they are the only ones that can hold search equity; with Search Console unread, no data shows a renamed slug would earn more. The builder takes the 28 slugs from `data/locations.json` and nowhere else (`.claude/skills/bsuk-location-page-builder/SKILL.md`), the per-page run never rewrites a row's slug (`docs/reference/page-run.md`), and the one redirect the family has exists because 32 old pages linked a mistyped slug — old links keep arriving at whatever URL was published. The strategy already gives each pair two distinct intents. | The slugs stay in 11 patterns, and some do not carry the page's target keyword (`buy-blue-staffy-puppy-coventry-area`, `blue-staffy-puppies-south-yorkshire`); the H1, title and meta carry the keyword instead. |
| (b) Rename the 17 noindex stubs to one pattern, `blue-staffy-puppies-<city>`, with a 301 from each old slug | 17 redirects, 17 canonicals, 17 board keys, the footer and hub links | one consistent pattern across the cluster | 17 new redirects to keep one hop for good; the gain cannot be measured until project 6; every internal link and every old-site link to a stub moves to a redirect |
| (c) Merge each intent pair: 301 `uk-staffordshire-bull-terrier-breeder` into `blue-staffy-puppies-uk`, and `staffy-puppies-for-sale-glasgow` into `staffy-breeding-dogs-glasgow` | 2 redirects, 2 fewer pages | two fewer pages competing for "Staffy breeder UK" and "Staffy Glasgow" searches (Known Issue 59) | contradicts the approved strategy, which gives the breeder page a trust role and the breeding-dogs page the parent-dog topic; the city page would lose its own transactional URL |

## The family, per slug

Row order is the strategy's build order. **Links in** counts other built pages linking to the
URL from inside their `<main>` (the header and footer city list link every city from every
page and are not counted), measured on the 2026-09-26 build with
`python3 scripts/page_intake.py <slug>`.

| Order | Slug | City | Pattern | Robots | Mode | H1 | In sitemap | Redirects in | Links in | Intent (strategy) | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `blue-staffy-puppies-london` | London | blue-staffy-puppies-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 2 | `blue-staffy-puppies-manchester-uk` | Manchester | blue-staffy-puppies-<city>-uk | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 3 | `staffy-puppies-for-sale-liverpool` | Liverpool | staffy-puppies-for-sale-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 4 | `staffy-puppies-for-sale-essex` | Essex | staffy-puppies-for-sale-<city> | noindex | stub | EMPTY | no | `/uk-locations/staffordshire-bull-terrier-puppies-for-sale-essex/` | 2 | transactional, local | keep the slug; rebuild the stub |
| 5 | `blue-staffy-puppies-dundee` | Dundee | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 6 | `blue-staffy-puppies-birmingham` | Birmingham | blue-staffy-puppies-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 7 | `blue-staffy-puppies-bristol-uk` | Bristol | blue-staffy-puppies-<city>-uk | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 8 | `staffy-puppies-cardiff-wales` | Cardiff | staffy-puppies-<city> | noindex | stub | set | no | — | 3 | transactional, local | keep the slug; rebuild the stub |
| 9 | `buy-blue-staffy-puppy-coventry-area` | Coventry | buy-blue-staffy-puppy-<city>-area | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 10 | `staffy-puppies-for-sale-glasgow` | Glasgow | staffy-puppies-for-sale-<city> | noindex | stub | set | no | — | 3 | transactional, local | keep the slug; rebuild the stub |
| 11 | `blue-staffy-puppies-for-sale-leeds` | Leeds | blue-staffy-puppies-for-sale-<city> | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 12 | `staffy-puppies-wolverhampton` | Wolverhampton | staffy-puppies-<city> | noindex | stub | EMPTY | no | — | 3 | transactional, local | keep the slug; rebuild the stub |
| 13 | `staffy-puppies-for-sale-nottingham` | Nottingham | staffy-puppies-for-sale-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 14 | `blue-staffy-puppies-oxford` | Oxford | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 15 | `blue-staffy-puppies-sunderland` | Sunderland | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 16 | `blue-staffy-puppies-for-sale-in-leicester` | Leicester | blue-staffy-puppies-for-sale-in-<city> | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 17 | `blue-staffy-puppies-edinburgh` | Edinburgh | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 18 | `blue-staffy-puppies-hull` | Hull | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 19 | `blue-staffy-puppies-york` | York | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 20 | `blue-staffy-puppies-south-yorkshire` | South Yorkshire | blue-staffy-puppies-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 21 | `blue-staffy-puppies-aberdeen` | Aberdeen | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 22 | `staffy-puppies-for-sale-cornwall` | Cornwall | staffy-puppies-for-sale-<city> | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 23 | `blue-staffy-puppies-middlesbrough` | Middlesbrough | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 24 | `blue-staffy-puppies-inverness` | Inverness | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 25 | `blue-staffies-newcastle-under-lyme` | Newcastle-under-Lyme | blue-staffies-<city> | noindex | stub | set | no | — | 3 | transactional, local | keep the slug; rebuild the stub |
| 26 | `uk-staffordshire-bull-terrier-breeder` | UK | uk-staffordshire-bull-terrier-breeder (national) | noindex | stub | EMPTY | no | — | 3 | commercial, trust page | keep the slug; rebuild the stub |
| 27 | `blue-staffy-puppies-uk` | UK | blue-staffy-puppies-uk (national) | index | migrated | set | yes | — | 3 | transactional, national hub | keep the slug; refresh (indexable; keeps its verbatim set) |
| 28 | `staffy-breeding-dogs-glasgow` | Glasgow (breeding dogs) | staffy-breeding-dogs-<city> | index | migrated | set | yes | — | 3 | informational, trust (parent dogs) | keep the slug; refresh (indexable; keeps its verbatim set) |

Eleven slug patterns: `blue-staffy-puppies-<city>` (12), `staffy-puppies-for-sale-<city>` (5),
`blue-staffy-puppies-<city>-uk` (2), `staffy-puppies-<city>` (2), and one each of
`blue-staffy-puppies-for-sale-<city>`, `blue-staffy-puppies-for-sale-in-<city>`,
`blue-staffies-<city>`, `buy-blue-staffy-puppy-<city>-area`, `staffy-breeding-dogs-<city>` and
the two national rows. Nine rows have an empty H1 (Known Issue 59): each board picks its H1 from
the page's own primary keyword, and the empty field is never copied.

## The two intent pairs (Known Issue 59)

- **National:** `blue-staffy-puppies-uk` is the indexable UK hub (in the sitemap; its body links 18
  of the other 27 location pages). `uk-staffordshire-bull-terrier-breeder` is a noindex stub with an empty H1 that the
  strategy rebuilds as the trust page ("uk staffordshire bull terrier breeder", Person schema,
  the licence claim kept as a placeholder). Keep both. The trust page's board takes its own
  primary keyword; the question tool currently gives both rows one location question
  (`scripts/query_augment.py` `location_question()`), so the trust page's question file is
  written for its own keyword, not the hub's.
- **Glasgow:** `staffy-breeding-dogs-glasgow` is indexable and carries the parent-dog topic
  (Known Issue 16 made it the outreach page); `staffy-puppies-for-sale-glasgow` is the noindex
  city stub the strategy rebuilds as the Glasgow city page. Keep both; the city page links to
  the breeding-dogs page (the strategy's link role for the pair).

## Redirects in the family

One redirect touches the cluster: `/uk-locations/staffordshire-bull-terrier-puppies-for-sale-essex/`
→ `/uk-locations/staffy-puppies-for-sale-essex/` (301, one hop, target built). No chain, no
redirect out of any of the 28 URLs; `npm run check:redirects` holds this. Option (a) adds none.

## Comparison slugs (Known Issue 62)

No comparison page, hub or page-map row exists. The strategy's first comparison page targets
"blue and black staffy" (secondary: "blue or black staffordshire bull terrier").

| Option | Slug for the first page | Why | Trade-off |
|---|---|---|---|
| **(a) Top level, the target keyword plus `-uk`: `/blue-and-black-staffy-uk/` (Recommended)** | `blue-and-black-staffy-uk` | Every page rebuilt so far has a top-level slug, most with `uk` in it (`blue-staffy-health-uk`, `uk-staffordshire-bull-terrier-guide`); a top-level route is the page's own key, so it needs no `data/page-map.json` row before the build (the builder skills' project 5 rule 7) and no hub first. The slug carries the strategy's target keyword. | If a comparison hub is built later, this page is not under it in the URL; the hub links to it, and the slug is never changed after it ships. |
| (b) Under a new hub: `/staffy-comparisons/blue-and-black-staffy/` | `staffy-comparisons/blue-and-black-staffy` | groups later comparison pages under one folder | the hub has to be built first, and the page needs a page-map row before its build |
| (c) Under the guides hub: `/blue-staffy-blog-guides/blue-and-black-staffy/` | `blue-staffy-blog-guides/blue-and-black-staffy` | reuses an existing hub | mixes the comparison profile into the blog cluster, and the page needs a page-map row |

Later comparison pages follow the same pattern: top level, the page's target keyword, `-uk`.

## What happens next

The two recommendations go to the answer board as one batch before the first city board. The
chosen option is recorded on each page's board in `meta.slug`, and
`docs/reference/page-run.md` row 3 reads this file.
