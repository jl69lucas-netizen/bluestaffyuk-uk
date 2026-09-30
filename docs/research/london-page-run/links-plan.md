# London links plan (page-run row 9, steps 4–5)

Date: 2026-09-30 · Page: `blue-staffy-puppies-london` (`/uk-locations/blue-staffy-puppies-london/`) · Plan: London page run, Task 19.
Agents run: `bsuk-entity-incorporation-agent` Moves 1, 2 and 4 (the per-section `entities`, each with its why, are in `data/outlines/blue-staffy-puppies-london.json`), and `bsuk-external-link-agent` Protocol A.

Rules applied: Link-First (`rules/links.md` `link-first-anchors`, every anchor opens its sentence); a typed anchor on every link (`anchor-type-variation`); no anchor repeats on the page; no internal anchor another board in `data/boards/` uses for the same route (checked against all 13 boards on 2026-09-30); internal links open in the same tab, outside citations in a new tab with `rel="noopener noreferrer"` and no `nofollow`. FAQ answers carry no `<a>` (they feed `FAQPage` JSON-LD); a pointer to a section sits in its own paragraph outside the answer string.

Rulings respected: no licence claim, no licensing page and no council link (STOP 1 q06); health tests are named, never a result (ledger `parents-dna-clear` is `NOT FETCHED — none held`); the guarantee is worded only from `guarantee_label` / `guarantee_cover`; the deposit is never called plainly "refundable" (row 8's refund clause only).

## Move 1 — structural critique (per section group)

- **Hero, counter, trust, takeaways (rows 1–5):** figures are data-read, but the opener names no breeder and no place pair until the entities go in; `ont:lisa-bright`, `ont:london` and `ont:carlisle` fix that.
- **Deposit and viewing (row 8):** the buyer fear is named but the section had no outside authority behind "see the puppy with its mother first"; the RSPCA's puppy-sales page is that authority.
- **Delivery (row 9):** generic "we deliver" copy is the risk; `ont:defra-approved-transport` and the band from data make it specific, and the nearby-city links give the reader in the home counties the page written for them.
- **Litter and health (rows 10, 13, 14):** "health tested" is the generic term; the section names L-2-HGA, HC-HSF4, eye screening and elbow screening as tests to ask about, with `/blue-staffy-health-uk/` as the internal source.
- **London life and the extra sections (rows 15, 17–19):** breed facts need neutral-register citations; PDSA, the registry's breed standard, the government's banned-dogs list and the VetCompass study stand behind them.

## Move 4 — schema notes

`LocalBusiness` (areaServed London; no telephone while `PHONE_PLACEHOLDER`) · `FAQPage` carrying exactly the visible questions of rows 7, 12 and 21 · `BreadcrumbList` (Home › UK locations › London) · `VideoObject` only if the video section is kept · `Product` only where a puppy card shows (one offer each). Extend, never duplicate a `@type`; verify in `dist/` with `npm run check:schema`.

## Internal links

"Resolves today": the route has a source under `src/pages/` (and, for a city, a row in `data/locations.json` built by `src/pages/uk-locations/[slug].astro`). `dist/` is not built in this worktree, so no built file was read.

| Section | Target | Anchor text | anchor_type | Purpose | Resolves today |
|---|---|---|---|---|---|
| 1 Hero | `/` | BlueStaffyUK | branded | Opens the signed first paragraph ("BlueStaffyUK is Lisa Bright's Carlisle kennel…"); names the brand entity behind the video-call promise | yes — `src/pages/index.astro` |
| 1 Hero | `/available-puppies/` | Blue Staffy puppies available now | partial | Supports "the puppies on this page are real and listed"; the transactional next step | yes — `src/pages/available-puppies/index.astro` |
| 8 Deposit · H3 video call | `/uk-blue-staffy-breeders-contact/` | Booking a video call with us | natural | Supports "the video call comes before any deposit" — the route to ask for one | yes — `src/pages/uk-blue-staffy-breeders-contact/` |
| 8 Deposit · H3 what it does | `/uk-blue-staffy-puppy-buying-guide/` | The questions to ask any breeder before you pay | lsi | Supports "ask before you pay"; the long checklist lives on the guide | yes — `src/pages/uk-blue-staffy-puppy-buying-guide/` |
| 9 Delivery · H3 cost | `/blue-staffy-pup-sale-uk/` | How our delivery price is set by distance | partial | Supports the band sentence (band read from `delivery_min_gbp` / `delivery_max_gbp`) | yes — `src/pages/blue-staffy-pup-sale-uk/` |
| 9 Delivery · nearby line | `/uk-locations/staffy-puppies-for-sale-essex/` | Buyers in Essex | natural | Nearest location page; Essex is a county (≈30 mi from central London to its county town, Chelmsford) — same delivery run east of London | route exists (`data/locations.json`); noindex stub with an empty H1 — **live once the stub is rebuilt** |
| 9 Delivery · nearby line | `/uk-locations/blue-staffy-puppies-oxford/` | Our page for Oxford families | natural | ≈51 mi — same delivery run west of London | yes — `data/locations.json`; the only indexed location page near London |
| 9 Delivery · nearby line | `/uk-locations/buy-blue-staffy-puppy-coventry-area/` | Coventry and the surrounding area | natural | ≈86 mi — the Midlands on the M1/M6 side | route exists (`data/locations.json`); noindex stub with an empty H1 — **live once the stub is rebuilt** |
| 9 Delivery · nearby line | `/uk-locations/blue-staffy-puppies-for-sale-in-leicester/` | Leicester readers | natural | ≈89 mi — the next city up the M1 | route exists (`data/locations.json`); noindex stub — **live once the stub is rebuilt** |
| 9 Delivery · nearby line | `/uk-locations/` | The other UK cities we have written about | natural | Hub link for any reader outside London | yes — `src/pages/uk-locations/index.astro` |
| 10 Litter · H3 prices | `/buy-blue-staffy-puppies-uk/` | Buy Blue Staffy puppies in the UK | exact (1 of 2) | Supports "each puppy's price is on its card"; the full listing | yes — `src/pages/buy-blue-staffy-puppies-uk/` |
| 10 Litter · H3 parents | `/blue-staffy-uk-breeders/` | Maggie, Jones and the home they share with us | natural | Supports the parents paragraph (names only; no result) | yes — `src/pages/blue-staffy-uk-breeders/` |
| 13 Health · H3 tests | `/blue-staffy-health-uk/` | Blue Staffy health in the UK | exact (2 of 2) | The internal source for every health sentence (FU Q9); tests named, never a result | yes — `src/pages/blue-staffy-health-uk/` |
| 14 Paperwork | `/buy-staffy-puppies-for-sale-uk/` | Staffy puppies for sale with their paperwork in order | partial | Supports "what comes home" = exactly `whyus-paperwork` | yes — `src/pages/buy-staffy-puppies-for-sale-uk/` |
| 15 London life · H3 alone | `/blue-staffy-blog-guides/` | Settling a new puppy into a flat or a busy home | lsi | Supports the flat and time-alone advice; the longer how-to lives in the guides | yes — `src/pages/blue-staffy-blog-guides/` |
| 18 Breed · H3 English vs American | `/uk-staffordshire-bull-terrier-guide/` | What sets the English Staffy apart | lsi | Supports the English-vs-American paragraph; full breed history on the guide | yes — `src/pages/uk-staffordshire-bull-terrier-guide/` |
| 19 Everyday health | `#health-tests` (row 13, in-page) | The two inherited conditions we name for the parents | natural | Jump link: inherited conditions are answered in row 13, not repeated | in-page target: row 13 carries `"anchor": "health-tests"` in the outline; the build sets it as the `id` of row 13's section component in `src/pages/uk-locations/blue-staffy-puppies-london.astro` |

Mix: 17 links · exact 2 · partial 4 · lsi 4 · natural 8 (incl. the jump link) · branded 1 → 5 types, at most two exact. No anchor repeats; none matches an anchor any other board uses for the same route. Nearby cities are the four nearest by straight-line distance from central London among the 28 in `data/locations.json` (Essex, a county, 30 mi to its county town Chelmsford; the cities Oxford 51, Coventry 86, Leicester 89; the next, Birmingham, is 101). Only Oxford is indexed today; the other three go live once their stubs are rebuilt.

## External links (Protocol A)

Six links, six domains, five source types (gov, registry, vet-charity ×2, welfare, research). All six are existing library rows; no row was added. One outside link per section, so the density cap (one per paragraph, two per 300 words) holds.

| Section | URL (library row) | Anchor text | anchor_type | Type | Claim it stands behind | Live check 2026-09-30 |
|---|---|---|---|---|---|---|
| 8 Deposit · H2 (advert red-flags point) | https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy/sales | The RSPCA's advice on puppy adverts | branded | welfare | The RSPCA advises a buyer to see the puppy with its mother, in person. The next sentence is our own, not the RSPCA's: our video call comes before the deposit, and the deposit books that in-person viewing. The copy never implies the RSPCA endorses a video call as a viewing | curl: NOT FETCHED — egress proxy answers 403 to CONNECT for the host (policy denial); Firecrawl scrape: 200 |
| 13 Health · H3 tests | https://www.bva.co.uk/canine-health-schemes/eye-scheme/ | A clinical eye examination by a veterinary specialist | lsi | vet-charity | Eye screening looks for inherited eye disease a DNA test does not cover — a general statement about eye screening. **Copy note:** the copy must not say or imply the parents were examined under the BVA/KC scheme (the breeder named eye screening, not the scheme); never place "BVA" near hip/elbow/score | curl: NOT FETCHED — proxy CONNECT 403; Firecrawl: 200 |
| 15 London life | https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/puppies-dogs/how-much-exercise-does-your-dog-need | How much exercise a Staffy-sized dog needs | partial | vet-charity | The daily exercise a London owner has to plan around parks and a commute | curl: NOT FETCHED — proxy CONNECT 403; Firecrawl: 200 |
| 17 Temperament | https://www.royalkennelclub.com/breed-standards/terrier/staffordshire-bull-terrier/ | The Staffordshire Bull Terrier breed standard | exact | registry | The standard's temperament line, "Bold, fearless and totally reliable" (read 2026-09-30) | curl: NOT FETCHED — proxy CONNECT 403; Firecrawl: 200 |
| 18 Breed | https://www.gov.uk/control-dog-public/banned-dogs | The government's list of banned dog types | natural | gov | The Staffordshire Bull Terrier is not one of the types banned under the Dangerous Dogs Act 1991 | curl: NOT FETCHED — proxy CONNECT 403; Firecrawl: 200 |
| 19 Everyday health | https://pmc.ncbi.nlm.nih.gov/articles/PMC7510130/ | A 2020 study of UK veterinary records | natural | research | Skin problems (atopic dermatitis, skin masses, skin disorder) are among the breed's recorded predispositions — the study's findings, never our dogs' results | curl: NOT FETCHED — proxy CONNECT 403; Firecrawl: 200 |

External anchor types: branded, lsi, partial, exact, natural → 5 (≥3 required). Not used, by ruling: any licensing page, `gov.uk/find-local-council` and the Cumberland Council rows (STOP 1 q06), competitors and marketplaces. `ont:paag` and `ont:dogs-trust` are named in copy but not linked (the six-link set is complete without them).

## Judgment calls

1. **Live check.** `curl -sIL` from this container returns `000`: the session's egress proxy refuses CONNECT to all six hosts (`/__agentproxy/status` records `connect_rejected … 403`). The curl status is recorded as `NOT FETCHED — egress proxy CONNECT 403`, and the Firecrawl scrape (`statusCode` 200, `maxAge: 0`) is recorded beside it as a second source, not as the curl result.
2. **Stub location pages.** Essex (a county), Coventry and Leicester are `noindex` stubs today (Essex and Coventry with an empty H1). They were kept because the brief picks by proximity; each row is marked "live once the stub is rebuilt", and the board should carry that mark. Oxford is the only indexed one nearby.
4. **RSPCA placement.** The citation sits on the advert red-flags point of row 8's H2, not the video-call H3, so the RSPCA stands behind "see the puppy with its mother in person" only; the video call is stated as ours, before the deposit and the in-person viewing it books.
3. **BVA link wording.** The breeder named eye screening, not the BVA/KC scheme, so the anchor describes the examination in general and the sentence never says ours was done under the scheme.
