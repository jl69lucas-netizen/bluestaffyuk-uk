# Foundation migration report

| | |
| --- | --- |
| Source clone | `/Users/apple/bluestaffyuk-site` @ `aa3f139` |
| Generated | 2026-09-16 |
| Generator | `scripts/build_migration_report.py` |

Every number below is read from `data/page-map.json`, `data/*.json` and `dist/` at
generation time. Nothing here is typed by hand.

## Counts

| What | Count |
| --- | ---: |
| Rich pages migrated | 11 |
| Location pages | 28 |
| — of which are indexed (migrated body) | 11 |
| — of which are noindexed stubs awaiting project 5 | 17 |
| Blog posts | 1 |
| Individual puppy pages | 6 |
| New index pages (no WordPress original) | 3 — `/uk-locations/`, `/blog/`, `/available-puppies/` |
| Old URLs read by the extractor | 40 |
| **Total pages built** | **49** |

## Phone numbers removed

The old body text published a phone number the new site does not have yet. The
extractor strips every occurrence and records the count per page; `PHONE_PLACEHOLDER`
stands in until project 6 provisions a number, and `scripts/placeholder_check.py`
refuses to let that placeholder reach a release build.

**39 occurrence(s) removed across 39 page(s).**

| Page kind | Occurrences removed |
| --- | ---: |
| blog | 1 |
| location | 27 |
| rich | 11 |

## Parity

Embedded verbatim from `docs/reports/parity.md`, the gate that produced it.

### Migration parity

Built pages measured against what the extractor promised. `raw` is the old
`.entry-content` before the extractor's deliberate removals (dead WordPress forms,
the four sold pups' cards); `expected` is the same page after them; `built` is what
`article.prose-migrated` renders. Note that `raw` is itself measured after site
chrome and dead forms are stripped, so it slightly understates the WordPress body.
The gate compares expected → built with a 2% whitespace band; headings must match
exactly, embeds must never decrease, a built page missing its article scope fails,
and expected must keep at least 60% of raw's words.

| URL | words raw→expected→built | headings exp→built | images exp→built | embeds exp→built | cards removed | result |
| --- | --- | --- | --- | --- | --- | --- |
| /blue-staffy-blog-guides/ | 0→0→142 | 0→3 | 0→0 | 0→0 | 0 | PASS (archive) |
| /blue-staffy-health-uk/ | 3510→3165→3165 | 62→62 | 8→8 | 0→0 | 4 | PASS |
| /blue-staffy-pup-sale-uk/ | 1133→788→788 | 18→18 | 5→5 | 0→0 | 4 | PASS |
| /blue-staffy-uk-breeders/ | 2316→1780→1780 | 27→27 | 7→7 | 1→1 | 4 | PASS |
| /buy-blue-staffy-puppies-uk/ | 2488→2254→2254 | 27→27 | 7→7 | 1→1 | 5 | PASS |
| /buy-staffy-puppies-for-sale-uk/ | 4706→4706→4706 | 50→50 | 13→13 | 1→1 | 0 | PASS |
| / | 3369→3112→3112 | 59→59 | 14→14 | 2→2 | 4 | PASS |
| /privacy-policy-uk/ | 1015→1015→1015 | 23→23 | 3→3 | 0→0 | 0 | PASS |
| /thank-you-blue-staffy-puppies-journey/ | 422→422→422 | 5→5 | 1→1 | 0→0 | 0 | PASS |
| /uk-blue-staffy-breeders-contact/ | 397→397→397 | 6→6 | 1→1 | 0→0 | 0 | PASS |
| /uk-blue-staffy-puppy-buying-guide/ | 6117→6117→6117 | 68→68 | 17→17 | 1→1 | 0 | PASS |
| /uk-locations/blue-staffies-newcastle-under-lyme/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-aberdeen/ | 476→443→443 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-birmingham/ | 4→4→4 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-bristol-uk/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-dundee/ | 463→430→430 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-edinburgh/ | 485→452→452 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-for-sale-in-leicester/ | 7→7→7 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-for-sale-leeds/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-hull/ | 470→437→437 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-inverness/ | 469→436→436 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-london/ | 4→4→4 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-manchester-uk/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-middlesbrough/ | 449→416→416 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-oxford/ | 473→440→440 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-south-yorkshire/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-sunderland/ | 464→431→431 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-uk/ | 2112→1767→1767 | 29→29 | 11→11 | 0→0 | 4 | PASS |
| /uk-locations/blue-staffy-puppies-york/ | 474→441→441 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/buy-blue-staffy-puppy-coventry-area/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-breeding-dogs-glasgow/ | 1853→1508→1508 | 19→19 | 4→4 | 1→1 | 4 | PASS |
| /uk-locations/staffy-puppies-cardiff-wales/ | 4→4→4 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-cornwall/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-essex/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-glasgow/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-liverpool/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-nottingham/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-wolverhampton/ | 3→3→3 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/uk-staffordshire-bull-terrier-breeder/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-staffordshire-bull-terrier-guide/ | 4975→4630→4630 | 72→72 | 10→10 | 1→1 | 4 | PASS |

examined 40 pages, 0 failing

## Flags for projects 4 and 5

Pages the extractor flagged. These are properties of the WordPress content,
not defects introduced by the migration: Foundation's job was to carry them
across unchanged, and fixing them is the content work projects 4 and 5 own.
A page with neither a defect nor a refresh flag is omitted.

| URL | Kind | Words | Defects | Refresh flags |
| --- | --- | ---: | --- | --- |
| `/` | rich | 3112 | — | `wp-form-removed`, `legacy-links-rewritten:1`, `count-in-title`, `old-pup-cards-removed:4`, `old-price:£850`, `old-price:£1200`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:2` |
| `/blue-staffy-blog-guides/` | blog | 0 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:3` |
| `/blue-staffy-health-uk/` | rich | 3165 | — | `wp-form-removed`, `old-pup-cards-removed:4`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,200`, `old-pup-schema-images-removed:3`, `legacy-schema-nodes-dropped:3` |
| `/blue-staffy-pup-sale-uk/` | rich | 788 | — | `wp-form-removed`, `old-pup-cards-removed:4`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,200`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:3` |
| `/blue-staffy-uk-breeders/` | rich | 1780 | — | `wp-form-removed`, `old-pup-cards-removed:4`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,200`, `old-pup-schema-images-removed:3`, `legacy-schema-nodes-dropped:3` |
| `/buy-blue-staffy-puppies-uk/` | rich | 2254 | — | `wp-form-removed`, `legacy-links-rewritten:1`, `old-pup-cards-removed:5`, `old-price:£850`, `old-price:£1,200`, `old-price:£300`, `old-price:£850`, `old-price:£1,200`, `old-pup-schema-images-removed:3`, `legacy-schema-nodes-dropped:3` |
| `/buy-staffy-puppies-for-sale-uk/` | rich | 4706 | — | `wp-form-removed`, `legacy-links-rewritten:3`, `old-price:£850`, `old-price:£1,200`, `legacy-schema-nodes-dropped:3` |
| `/privacy-policy-uk/` | rich | 1015 | — | `legacy-schema-nodes-dropped:3` |
| `/thank-you-blue-staffy-puppies-journey/` | rich | 422 | — | `wp-form-removed`, `legacy-schema-nodes-dropped:3` |
| `/uk-blue-staffy-breeders-contact/` | rich | 397 | — | `wp-form-removed`, `legacy-schema-nodes-dropped:3` |
| `/uk-blue-staffy-puppy-buying-guide/` | rich | 6117 | — | `wp-form-removed`, `legacy-links-rewritten:3`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,200`, `old-price:£300`, `old-price:£300`, `old-price:£1,000`, `old-price:£1,100`, `old-price:£1,000`, `old-price:£1,200`, `old-price:£850`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:3` |
| `/uk-locations/blue-staffies-newcastle-under-lyme/` | location | 5 | `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/blue-staffy-puppies-aberdeen/` | location | 443 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,000`, `old-price:£1,100`, `old-price:£1,200`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/blue-staffy-puppies-birmingham/` | location | 4 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/blue-staffy-puppies-bristol-uk/` | location | 0 | `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/blue-staffy-puppies-dundee/` | location | 430 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/blue-staffy-puppies-edinburgh/` | location | 452 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,000`, `old-price:£1,100`, `old-price:£1,200`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/blue-staffy-puppies-for-sale-in-leicester/` | location | 7 | `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/blue-staffy-puppies-for-sale-leeds/` | location | 0 | `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/blue-staffy-puppies-hull/` | location | 437 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/blue-staffy-puppies-inverness/` | location | 436 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/blue-staffy-puppies-london/` | location | 4 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/blue-staffy-puppies-manchester-uk/` | location | 5 | `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/blue-staffy-puppies-middlesbrough/` | location | 416 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/blue-staffy-puppies-oxford/` | location | 440 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/blue-staffy-puppies-south-yorkshire/` | location | 0 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/blue-staffy-puppies-sunderland/` | location | 431 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `old-price:£1,000`, `old-price:£1,100`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/blue-staffy-puppies-uk/` | location | 1767 | — | `wp-form-removed`, `legacy-links-rewritten:1`, `old-pup-cards-removed:4`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,200`, `old-price:£300`, `legacy-schema-nodes-dropped:4` |
| `/uk-locations/blue-staffy-puppies-york/` | location | 441 | — | `old-pup-cards-removed:4`, `puppy-grid-emptied`, `old-pup-names-in-prose:4`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/buy-blue-staffy-puppy-coventry-area/` | location | 0 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/staffy-breeding-dogs-glasgow/` | location | 1508 | — | `wp-form-removed`, `old-pup-cards-removed:4`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,200`, `legacy-schema-nodes-dropped:2` |
| `/uk-locations/staffy-puppies-cardiff-wales/` | location | 4 | `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/staffy-puppies-for-sale-cornwall/` | location | 0 | `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/staffy-puppies-for-sale-essex/` | location | 0 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/staffy-puppies-for-sale-glasgow/` | location | 5 | `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/staffy-puppies-for-sale-liverpool/` | location | 5 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/staffy-puppies-for-sale-nottingham/` | location | 5 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/staffy-puppies-wolverhampton/` | location | 3 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-locations/uk-staffordshire-bull-terrier-breeder/` | location | 0 | `empty-h1`, `stub` | `legacy-schema-nodes-dropped:2`, `stub-noindexed` |
| `/uk-staffordshire-bull-terrier-guide/` | rich | 4630 | — | `wp-form-removed`, `old-pup-cards-removed:4`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£1,200`, `old-price:£850`, `old-price:£850`, `old-pup-schema-images-removed:3`, `legacy-schema-nodes-dropped:3` |

40 of 40 pages flagged.

### Flags by kind

Counted in PAGES carrying the flag, not occurrences.

| Flag | Pages |
| --- | ---: |
| `flag: legacy-schema-nodes-dropped` | 40 |
| `defect: stub` | 18 |
| `flag: old-pup-cards-removed` | 17 |
| `flag: stub-noindexed` | 17 |
| `flag: old-price` | 13 |
| `flag: wp-form-removed` | 12 |
| `defect: empty-h1` | 10 |
| `flag: old-pup-names-in-prose` | 10 |
| `flag: puppy-grid-emptied` | 9 |
| `flag: legacy-links-rewritten` | 5 |
| `flag: old-pup-schema-images-removed` | 4 |
| `flag: count-in-title` | 1 |
