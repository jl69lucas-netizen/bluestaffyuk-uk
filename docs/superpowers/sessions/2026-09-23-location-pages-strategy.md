MISSING: docs/research/competitors/bullscaff.json
MISSING: docs/research/competitors/ukstaffypups.json
MISSING: docs/research/competitors/vaderblustaf.json
MISSING: docs/research/competitors/exodusbulls.json
MISSING: docs/research/competitors/staffie-owners.json
MISSING: docs/research/competitors/puppies.json
MISSING: docs/research/competitors/gumtree.json
MISSING: docs/research/competitors/champdogs.json
MISSING: docs/research/competitors/freeads.json
MISSING: docs/research/competitors/preloved.json
MISSING: docs/research/competitors/royalkennelclub.json
MISSING: docs/research/competitors/foreverpuppy.json
MISSING: docs/research/competitors/petsforlove.json
MISSING: docs/research/competitors/petify.json
MISSING: docs/research/competitors/ukpets.json
MISSING: docs/research/competitors/pdsa.json
MISSING: docs/research/competitors/dogstrust.json
MISSING: docs/research/llm-intel/blue-staffies-newcastle-under-lyme-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-aberdeen-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-birmingham-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-bristol-uk-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-dundee-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-edinburgh-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-for-sale-in-leicester-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-hull-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-inverness-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-london-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-middlesbrough-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-oxford-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-south-yorkshire-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-sunderland-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-uk-<date>.json
MISSING: docs/research/llm-intel/blue-staffy-puppies-york-<date>.json
MISSING: docs/research/llm-intel/buy-blue-staffy-puppy-coventry-area-<date>.json
MISSING: docs/research/llm-intel/staffy-breeding-dogs-glasgow-<date>.json
MISSING: docs/research/llm-intel/staffy-puppies-cardiff-wales-<date>.json
MISSING: docs/research/llm-intel/staffy-puppies-for-sale-cornwall-<date>.json
MISSING: docs/research/llm-intel/staffy-puppies-for-sale-essex-<date>.json
MISSING: docs/research/llm-intel/staffy-puppies-for-sale-glasgow-<date>.json
MISSING: docs/research/llm-intel/staffy-puppies-for-sale-liverpool-<date>.json
MISSING: docs/research/llm-intel/staffy-puppies-for-sale-nottingham-<date>.json
MISSING: docs/research/llm-intel/staffy-puppies-wolverhampton-<date>.json
MISSING: docs/research/llm-intel/uk-staffordshire-bull-terrier-breeder-<date>.json
fresh: docs/research/gap-matrix-2026-09-23.md, docs/research/keyword-gap-2026-09-23.md, docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-23.json, docs/research/llm-intel/blue-staffy-puppies-for-sale-leeds-2026-09-23.json, data/competitors.json, docs/research/competitors/trojanstaffuk.json|md, docs/research/competitors/pets4homes.json|md, docs/research/competitors/rspca.json|md, docs/research/competitors/bsuk.json|md, data/page-map.json, data/locations.json — carrying on with what exists

# Location pages strategy — 2026-09-23

Scope: the 28 pages in `data/locations.json` (project 5), plus the comparison and guide pages the research supports as their link targets.

How the research was read:

- Every input is dated 2026-09-23; nothing is stale. What is missing is breadth: the matrix has competitor reports for Trojanstaff, Pets4Homes and the RSPCA only, and llm-intel exists for the Manchester and Leeds pages only. The classifieds that the registry shows with a page per town (staffie-owners, puppies, champdogs, freeads, preloved, gumtree, petify, ukpets) have no report yet, so every city signal below rests on Pets4Homes (tier 2) and, for Birmingham, Trojanstaff (tier 1). No N/M count here includes a tier-5 report; the one tier-5 entry (staffordshirebullterrierkennel) has no report and appears below only as a risk.
- The keyword-gap file's BSUK source is the BSUK profile (`docs/research/competitors/bsuk.json`), not the page-map fallback, so its scores are not provisional on that ground.
- The BSUK profile lists the indexable pages only. Its indexable location pages are Aberdeen, Dundee, Edinburgh, Hull, Inverness, Middlesbrough, Oxford, Sunderland, York, the UK page and the Glasgow breeding-dogs page. Every other page in `data/locations.json` is a noindex stub (`defects: stub`); the profile does not list those URLs, so each is a **project 5 rebuild of its existing URL**, never a new page. The matrix's city rows mark every competitor city "BSUK has it: yes" because the profile's city list counts a city that is only *named* (for example in the "Cities We Serve" block); those rows are quoted as the matrix prints them and not re-marked. For the stub cities the practical gap is the page, not the name.
- Both llm-intel results are `page_source.kind` `question-file` and `provisional: true` (the pages are stubs, so the engine's answer was checked against each page's question file). They are compared with each other only, and every use below says provisional. Manchester's `answer_text` is `summary`: its entities and citations count, its format does not. Neither page is cited (`bsuk_cited: false`).
- GSC and GA4 are not fetched until project 6: no traffic, ranking or volume figure appears anywhere here.
- Scales: the matrix's "high" is a share of competitors; the keyword-gap's "high" is a points score. They are named each time and never merged.

## Strategy A — Contested stubs first

**Thesis.** The stubs are noindex, so today they earn nothing; the competitor research points at specific stub cities. Rebuild the stubs in the order the research ranks them — the keyword-gap high rows first, then the cities the matrix names in a breed-plus-town keyword row, then the other competitor cities, then the stubs no competitor in this research touches — and only then refresh the pages that are already indexable. Each city page competes with the Pets4Homes town template on depth rather than volume, which is the Pets4Homes report's own reading of how to beat it.

**Target clusters.**
- Breed-plus-city buying phrases: "staffordshire bull terrier puppies for sale in manchester greater manchester" (keyword-gap, high band) and the matrix keyword rows "staffordshire bull terrier in leeds / bristol / coventry / nottingham / glasgow / essex" (medium priority).
- Licensed-breeder trust: "uk staffordshire bull terrier licenced breeders" (keyword-gap, high band) — its natural home is the existing stub `/uk-locations/uk-staffordshire-bull-terrier-breeder/`.
- Buyer-safety questions each city page must answer, from the two llm-intel files (provisional): health tests, L-2-HGA and HC-HSF4, meeting the mother, microchip, vaccinations, the puppy contract, worming, socialisation, a return-to-breeder policy.

**Cluster → page map.** Each stub city → its own existing stub URL (never a second URL for the city). Licensed-breeder cluster → the `uk-staffordshire-bull-terrier-breeder` stub. The Glasgow puppies-for-sale stub takes "staffordshire bull terrier in glasgow"; the indexable Glasgow breeding-dogs page keeps its stud-dog topic, so the two do not compete. The national phrase "staffordshire bull terrier puppies for sale" (keyword-gap, high band) belongs to the listing page, not a location page — it is noted for the architect, not placed on a city page.

**Internal-link plan.** Every city page links up to the UK page and the `/uk-locations/` index, across to the licensed-breeder page, and down to the available-puppies listing. Nearby cities link to each other (the Yorkshire group; the Scottish group; the West Midlands group). Once built, the care, price and colour guides (below) receive a link from every city page. Outbound authority links, where a page cites a buying check: the RSPCA (tier 3) and the Royal Kennel Club (tier 2), both `link_allowed: true` and both cited in the Leeds engine answer (provisional). No link to any tier-1 breeder or classifieds competitor, and never to the tier-5 entry.

**Schema plan.** Keep what BSUK already emits (LocalBusiness, FAQPage, BreadcrumbList, Product/Offer per the profile). Add Person on the licensed-breeder page — the one competitor type BSUK lacks (Trojanstaff has it). No schema claim for a licence number: CLAUDE.md gates an unconfirmed licence claim behind `LICENCE_CLAIM_PLACEHOLDER`.

**Build order and effort.** Stub rebuilds first, in the Concrete Artifact order, each a full page from its own outline through `grill-me`; then refreshes of the indexable pages (lighter: FAQ blocks for the llm-intel questions, links to the licensed-breeder page and the guides); then the care, price and colour guides. Most of the effort is the stubs — each is written from nothing.

**Expected outcome (no traffic figure).** The competitor cities stop being noindex placeholders; each rebuilt city page answers the buyer-safety questions the engine answers list, so it becomes a candidate citation where today BSUK is not cited for Manchester or Leeds (provisional).

**Risks.** City priority rests on one classifieds report; the unreported classifieds may cover different towns. The London search also shows the tier-5 map-pack listing (registry notes) — a buyer-trust risk to answer on the London page with breeder proof, never by naming or linking it. The licensed-breeder page's central claim stays a placeholder until the breeder confirms the licence. Templated city prose risks the sibling-copy rule; each page is written from its own outline.

## Strategy B — Proof and answer pages first, cities after

**Thesis.** A city page is only as strong as the proof it links to, and BSUK's supporting content is thin (one blog post, no care-guide, price, faq or reviews page type per the profile). Build the depth pages first — the licensed-breeder page, a care guide, a Staffy price guide and a questions-to-ask-a-breeder guide built from the llm-intel entities — then rebuild all the stubs in one pass on a single outline pattern, each linking into those pages from day one.

**Target clusters.**
- Care guide: the matrix page-type row care-guide (the matrix's only high-share page-type gap).
- Price: the matrix page-type row price and the keyword-gap row "how much will a pet cost" (medium band), plus the matrix keyword rows "price of a staffy" / "price of a staffy puppy".
- Licensed breeder: "uk staffordshire bull terrier licenced breeders" (keyword-gap, high band) on its existing stub.
- Buyer questions: the llm-intel entities (provisional) and the keyword-gap row "advice for buying and advertising pets" (low band).
- Then the city stubs, in no research-ranked order (one batch).

**Cluster → page map.** Care guide → new page under the guides hub. Price guide → new page. Buyer-questions guide → new page. Licensed breeder → the existing stub rebuild. Each city → its existing stub URL.

**Internal-link plan.** Guides form a hub (the blog guides index) and each links to the licensed-breeder page and the listing; city pages, when built, link to all guides. Outbound: RSPCA and Royal Kennel Club as in A.

**Schema plan.** Article/BlogPosting and FAQPage on the guides; Person on the licensed-breeder page; city pages as in A.

**Build order and effort.** Guides and the licensed-breeder page first (fewer pages, heavier research per page); then every stub in one batch; then refreshes.

**Expected outcome (no traffic figure).** When city pages ship, each links to real depth, and the care-guide gap closes first.

**Risks.** Every stub stays noindex for the whole guide phase, including the Manchester stub that carries the keyword-gap's highest score. The guides compete with RSPCA's authority pages on general welfare topics, where the RSPCA report says its pull is domain authority. A single-batch city pass invites the templated prose the sibling rule forbids.

## Recommendation

**Pick: Strategy A — Contested stubs first.** Not provisional: the WHY below rests on keyword-gap and matrix rows scored from the BSUK profile, not the page-map fallback; the llm-intel figures are supporting only and marked provisional. No tie-break was needed: the topic is the location pages, and B leaves every stub noindex until its guides are done, including the highest-scoring gap in the research.

**WHY.**
- The keyword-gap file's joint-highest score, 10 (3+2+3+2) (high band, points scale), is the Manchester breed-plus-city row, and its natural home is the Manchester stub's project 5 rebuild — A builds it first; B leaves it noindex through the guide phase.
- The licensed-breeder row scores 8 (3+0+3+2) (high band) and maps onto an existing stub in `data/locations.json`, so A closes both high-band location rows with its first two rebuilds.
- The matrix names stub cities in its own keyword rows — "staffordshire bull terrier in leeds / bristol / coventry / nottingham / glasgow / essex" at 1/3 each (medium priority) — and Birmingham is the only city at 2/3 in the city gaps; all of these are noindex stubs today.
- Neither page with llm-intel is cited (`bsuk_cited: false`, provisional, question-file), and the Leeds answer cites the Royal Kennel Club and the RSPCA while the Manchester answer lists Trojanstaff and UKStaffyPups as local businesses — the city page is where BSUK must answer those buyer checks.

**The pick's downside.** It delays the care guide — care-guide is 2/3 in the matrix page types, the only "high" in the matrix's share scale — until every city is done, and until then the city pages link into a blog whose one post runs 162 words. B would close that gap first. It also orders cities on thin breadth: the matrix has 3 competitor reports against 21 registry entries, so the city ranking below the high rows is Pets4Homes' town list, and may change once the classifieds are analysed.

**First three build steps.**
1. Rebuild the Manchester stub (`/uk-locations/blue-staffy-puppies-manchester-uk/`) on the Manchester breed-plus-city phrase, with FAQ answers for the llm-intel high-band entities (microchip, vaccinations, contract — provisional), through `grill-me`.
2. Rebuild the licensed-breeder stub (`/uk-locations/uk-staffordshire-bull-terrier-breeder/`) with Person schema; the licence claim stays `LICENCE_CLAIM_PLACEHOLDER` until the breeder confirms it.
3. Rebuild the Leeds stub (`/uk-locations/blue-staffy-puppies-for-sale-leeds/`) on "staffordshire bull terrier in leeds", answering the Leeds high-band entities (L-2-HGA, HC-HSF4, meet the mother — provisional).

## Concrete Artifact

Build order for the 28 location pages, then the guides they link to. Row order is the build order. Gap score: keyword-gap score with its parts where a keyword-gap row exists; otherwise the matrix N/M, naming which matrix table.

| topic or page | target keyword | gap score | intent | link role | new or rebuild |
|---|---|---|---|---|---|
| Manchester — `/uk-locations/blue-staffy-puppies-manchester-uk/` | staffordshire bull terrier puppies for sale in manchester greater manchester | 10 (3+2+3+2) high (keyword-gap); matrix city 1/3 | transactional, local | city spoke → UK page, licensed-breeder page, listing | rebuild (stub, project 5) |
| Licensed breeder — `/uk-locations/uk-staffordshire-bull-terrier-breeder/` | uk staffordshire bull terrier licenced breeders | 8 (3+0+3+2) high (keyword-gap) | commercial, trust | trust page linked from every city page | rebuild (stub, project 5) |
| Leeds — `/uk-locations/blue-staffy-puppies-for-sale-leeds/` | staffordshire bull terrier in leeds | matrix keyword 1/3 medium; matrix city 1/3 | transactional, local | city spoke; Yorkshire group | rebuild (stub, project 5) |
| Birmingham — `/uk-locations/blue-staffy-puppies-birmingham/` | blue staffy puppies birmingham | matrix city 2/3 | transactional, local | city spoke; West Midlands group | rebuild (stub, project 5) |
| Bristol — `/uk-locations/blue-staffy-puppies-bristol-uk/` | staffordshire bull terrier in bristol | matrix keyword 1/3 medium; matrix city 1/3 | transactional, local | city spoke | rebuild (stub, project 5) |
| Coventry — `/uk-locations/buy-blue-staffy-puppy-coventry-area/` | staffordshire bull terrier in coventry | matrix keyword 1/3 medium; matrix city 1/3 | transactional, local | city spoke; West Midlands group | rebuild (stub, project 5) |
| Nottingham — `/uk-locations/staffy-puppies-for-sale-nottingham/` | staffordshire bull terrier in nottingham | matrix keyword 1/3 medium; matrix city 1/3 | transactional, local | city spoke | rebuild (stub, project 5) |
| Glasgow — `/uk-locations/staffy-puppies-for-sale-glasgow/` | staffordshire bull terrier in glasgow | matrix keyword 1/3 medium; matrix city 1/3 | transactional, local | city spoke; Scottish group; links to the breeding-dogs page | rebuild (stub, project 5) |
| Essex — `/uk-locations/staffy-puppies-for-sale-essex/` | staffordshire bull terrier in essex | matrix keyword 1/3 medium; matrix city 1/3 | transactional, local | city spoke | rebuild (stub, project 5) |
| London — `/uk-locations/blue-staffy-puppies-london/` | blue staffy puppies london | matrix city 1/3 | transactional, local | city spoke (tier-5 map-pack listing is a risk, never a link) | rebuild (stub, project 5) |
| Liverpool — `/uk-locations/staffy-puppies-for-sale-liverpool/` | staffy puppies for sale liverpool | matrix city 1/3 | transactional, local | city spoke | rebuild (stub, project 5) |
| Cardiff — `/uk-locations/staffy-puppies-cardiff-wales/` | staffy puppies cardiff | matrix city 1/3 | transactional, local | city spoke | rebuild (stub, project 5) |
| Leicester — `/uk-locations/blue-staffy-puppies-for-sale-in-leicester/` | blue staffy puppies for sale in leicester | matrix city 1/3 | transactional, local | city spoke | rebuild (stub, project 5) |
| Wolverhampton — `/uk-locations/staffy-puppies-wolverhampton/` | staffy puppies wolverhampton | no row in this research | transactional, local | city spoke; West Midlands group | rebuild (stub, project 5) |
| South Yorkshire — `/uk-locations/blue-staffy-puppies-south-yorkshire/` | blue staffy puppies south yorkshire | no row in this research | transactional, local | city spoke; Yorkshire group | rebuild (stub, project 5) |
| Newcastle-under-Lyme — `/uk-locations/blue-staffies-newcastle-under-lyme/` | blue staffies newcastle under lyme | no row in this research | transactional, local | city spoke; West Midlands group | rebuild (stub, project 5) |
| Cornwall — `/uk-locations/staffy-puppies-for-sale-cornwall/` | staffy puppies for sale cornwall | no row in this research | transactional, local | city spoke | rebuild (stub, project 5) |
| UK — `/uk-locations/blue-staffy-puppies-uk/` | blue staffy puppies uk | no location row (the national listing phrase belongs to the listing page) | transactional, national | hub: links to every city page | refresh (indexable) |
| York — `/uk-locations/blue-staffy-puppies-york/` | blue staffy puppies york | matrix city 1/3 (BSUK yes) | transactional, local | city spoke; Yorkshire group | refresh (indexable) |
| Hull — `/uk-locations/blue-staffy-puppies-hull/` | blue staffy puppies hull | matrix city 1/3 (BSUK yes) | transactional, local | city spoke; Yorkshire group | refresh (indexable) |
| Sunderland — `/uk-locations/blue-staffy-puppies-sunderland/` | blue staffy puppies sunderland | matrix city 1/3 (BSUK yes) | transactional, local | city spoke | refresh (indexable) |
| Oxford — `/uk-locations/blue-staffy-puppies-oxford/` | blue staffy puppies oxford | matrix city 1/3 (BSUK yes) | transactional, local | city spoke | refresh (indexable) |
| Edinburgh — `/uk-locations/blue-staffy-puppies-edinburgh/` | blue staffy puppies edinburgh | matrix city 1/3 (BSUK yes) | transactional, local | city spoke; Scottish group | refresh (indexable) |
| Aberdeen — `/uk-locations/blue-staffy-puppies-aberdeen/` | blue staffy puppies aberdeen | matrix city 1/3 (BSUK yes) | transactional, local | city spoke; Scottish group | refresh (indexable) |
| Dundee — `/uk-locations/blue-staffy-puppies-dundee/` | blue staffy puppies dundee | matrix city 1/3 (BSUK yes) | transactional, local | city spoke; Scottish group | refresh (indexable) |
| Middlesbrough — `/uk-locations/blue-staffy-puppies-middlesbrough/` | blue staffy puppies middlesbrough | no row in this research | transactional, local | city spoke | refresh (indexable) |
| Inverness — `/uk-locations/blue-staffy-puppies-inverness/` | blue staffy puppies inverness | no row in this research | transactional, local | city spoke; Scottish group | refresh (indexable) |
| Glasgow breeding dogs — `/uk-locations/staffy-breeding-dogs-glasgow/` | staffy breeding dogs glasgow | no row in this research | informational, trust | parent-dog proof page linked from the Glasgow city page | refresh (indexable; keeps its stud-dog topic) |
| Staffy care guide | no keyword row (page type care-guide) | matrix page type care-guide 2/3 high (matrix share) | informational | guide linked from every city page | new |
| Staffy price guide | price of a staffy puppy | how much will a pet cost 5 (0+2+3+0) medium (keyword-gap); matrix keyword 1/3 medium; matrix page type price 1/3 | informational, commercial | guide linked from every city page | new |
| Blue or black Staffy comparison | blue or black staffordshire bull terrier | matrix keyword 1/3 medium | comparison | guide linked from every city page and the listing | new |

## Sources

- `docs/research/gap-matrix-2026-09-23.md`
- `docs/research/keyword-gap-2026-09-23.md`
- `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-23.json`
- `docs/research/llm-intel/blue-staffy-puppies-for-sale-leeds-2026-09-23.json`
- `data/competitors.json`
- `docs/research/competitors/bsuk.json`
- `docs/research/competitors/bsuk.md`
- `docs/research/competitors/pets4homes.md`
- `docs/research/competitors/trojanstaffuk.md`
- `docs/research/competitors/rspca.md`
- `data/locations.json`
- `data/page-map.json`
