STALE: docs/research/competitors/petsforlove.json (fetched_on NOT FETCHED — homepage gated, the site gave no response; the keyword-gap header lists it as its only stale report)
fresh: docs/research/gap-matrix-2026-09-25.md, docs/research/keyword-gap-2026-09-25.md, docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-10-07.json (fetched_on 2026-09-23 as the file records it, stale list empty) and blue-staffy-puppies-manchester-uk-2026-09-25.json (fetched_on 2026-09-25, stale list empty), data/queries/blue-staffy-puppies-manchester-uk.json (fetched 2026-10-06), docs/research/manchester-page-run/serp-findings.md (SERP banked 2026-09-23, pool re-read 2026-10-07), fanout.md, ai-overview.md, free-keyword-signals.md, keyword-universe.json and entities.md (all 2026-10-07), data/competitors.json, docs/research/competitors/staffie-owners.md, pets4homes.md, freeads.md, gumtree.md, puppies.md, preloved.md, dogstrust.md, trojanstaffuk.md, staffordshirebullterrierkennel.json, bsuk.json and bsuk.md (pages fetched_on 2026-09-25), data/page-map.json, data/locations.json — carrying on with what exists

# Manchester page strategy directions — 2026-10-07

Scope: one page, `/uk-locations/blue-staffy-puppies-manchester-uk/`. It is a project 5 rebuild of the existing stub, never a new URL. The BSUK profile (`docs/research/competitors/bsuk.json`) lists no Manchester page, and `data/page-map.json` holds a stub there: 5 words under the H1 "Blue Staffy Puppies Manchester UK", with `noindex, follow` in `data/locations.json`. This is Manchester plan Task 10, step 2 (`docs/superpowers/plans/2026-10-07-manchester-page-run.md`).

## How to read this file

- **S1** is the cluster strategy's Manchester row, quoted verbatim from `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md` (the Concrete Artifact row, line 118, and its build step, line 108). It is not rewritten. A reading of it in this file's terms follows the quote.
- **S2 and S3** are the two strategies this file writes. Each is a different bet on what the Manchester page is for, not a reordering of the same sections.
- **The keyword decision.** The free planner read of 2026-10-07 (`free-keyword-signals.md` §3) exposed a choice between the query file's primary, "blue staffy puppies manchester", and the generic for-sale family: "staffy puppies for sale manchester", "staffies for sale manchester" and "staffordshire bull terrier for sale manchester".
  - S2 keeps the colour in the H1 and carries the for-sale family in the title and the first 100 words.
  - S3 leads the title and the H1 with the for-sale family.
  - S1 takes a third phrase: the keyword-gap row's full breed name.
  - The planner's ranges are search volume, which this file does not use (see "No traffic or volume figures" below). They sit on the research board's keyword universe, where the user weighs them beside this choice.
- **Borough coverage** is the other dimension the research opens. S3 gives the Greater Manchester boroughs their own section group, S2 names them inside its delivery answer, and S1 does not name them.
- Exactly one of S1–S3 is marked **(Recommended)**, with its why and its downside (working rule 4).
- **Where the check reads.** The cite check (`scripts/strategy_cite_check.py`) reads figures only under headings that begin "Strategy A", "Strategy B" or "Recommendation". So S1 sits under Strategy A, and each alternative sits under its own Strategy B heading (S2, then S3). All three are checked.
- **Scales.** The gap matrix's high / medium / low is a share of competitors. The keyword-gap's high / medium is a points score. The llm-intel bands are a third measure, per entity. Each use below names its scale, and none is merged with another.
- **LLM intel.** Both Manchester files are the `question-file` kind and provisional: the stub is noindex, so the engine's answer was checked against the question file's picks, not a built page. The 2026-10-07 file re-reads the same banked ChatGPT answer against the refreshed question file (no new call). Its bands match those of the 2026-09-25 file that S1 rested on; both are the same kind, so they may be compared, and they agree. `bsuk_cited` is false: the answer cites the Royal Kennel Club (tier 2), the PDSA (tier 3) and an unregistered breeder domain, not BSUK.
- **Tier 5.** The tier-5 entry (staffordshirebullterrierkennel) holds no place in Manchester's pool. It enters only through the matrix: its report lists Person in its schema and no city, so it is one of the matrix's Person 5/20, and it sits in the /20 of Manchester's 11/20 without adding to the 11. It is never a link or a model.
- **Tier 1.** The engine's answer lists two tier-1 breeders among its local businesses (Trojanstaff and UKStaffyPups), and Trojanstaff's stud page "talks of a new Manchester branch" (`trojanstaffuk.md`). The cluster strategy links no tier-1 breeder, and no direction here does.
- **No traffic or volume figures.** GSC and GA4 are not fetched until project 6. No traffic, ranking or search-volume figure is used here as a WHY or an outcome, and no planner range or Trends index is quoted. Competitor SERP positions describe the pool's shape only.
- **Business facts** (the breeder's name, prices, the deposit and its refund clause, the delivery band, the guarantee, the puppy trust signs) are read from data by the page and are not typed here. In the checked sections below, a business fact appears only where a listed source prints it too (the BSUK profile prints the base town, Carlisle, and the deposit, collection and delivery terms); otherwise the text names the data key or the ruling it comes from. The pre-deposit video call is set by the plan's first ruling and the ontology entity `ont:video-call-before-deposit`; it is not a key in `data/settings.json`. The Manchester plan's rulings bind every direction:
  - London's rulings 1 and 3–11 carry over (`docs/superpowers/plans/2026-09-30-london-page-run.md`): the deposit-before-viewing fear answered head-on, in the ruling's own words with "a live video call with the puppy and its mother ... offered on request before any deposit" (1); Maggie and Jones (3); name the tests, never a result (4); nothing about a licence (5); facts from data only (6); every H2 and H3 a buyer question (7); the word band when the pool gives no median (8); three FAQ blocks (9); type fits every tier (10); write from the outline only, with the external-link rule (11).
  - Manchester's own: the refund wording now exists as data (`data/settings.json` `deposit_refund_clause`), so the deposit answer no longer waits on a branch; own components per page; the breeder facts of 2026-10-04/05 (parents KC registered; vet-signed health card, first vaccinations, microchip, worming and flea treatment; certificates and DNA results shared on request, none in the repo).
- **The reader.** The session brief (`docs/superpowers/sessions/2026-10-07-session-brief.md`, Q8) names "the ranked buyer fears (scam / deposit, licensing, puppy farm, sick puppy, support, cost), for a Greater Manchester buyer 120 miles from Carlisle". The page itself states no mileage or drive time (`entities.md`, Place and geography).
- **An open flag every direction inherits.** The rebuilt question file picks "Are both parents DNA tested clear for L-2-HGA and HC-HSF4?", whose wording assumes a result we never state (session brief, Open Flags). No direction uses that wording; every health answer names the tests only.

## The directions at a glance

| | Bet | H1 | Title and opening | Leads with | Boroughs |
|---|---|---|---|---|---|
| S1 | The cluster row: rebuild on the keyword-gap's full-breed for-sale row and answer the engine's high-band checks | the row's phrase | the row's phrase | microchip and vaccinations; the Royal Kennel Club and PDSA links | not named |
| S2 **(Recommended)** | One accountable breeder answers the Greater Manchester buyer; the colour stays in the H1 | "blue Staffy puppies" + Manchester | the for-sale family with the full breed name and the colour | where to buy near Manchester, answered honestly: Carlisle, seeing the puppy before any deposit (plan ruling 1), delivery or collection | named inside the delivery answer |
| S3 | Page one's own shape on one breeder's litter: the for-sale family leads, the litter first, borough by borough | "Staffy puppies for sale" + (Greater) Manchester | the for-sale family with the full breed name; the colour in the opening | the litter at data prices in a stacked table, and where it is | their own section group |

## Evidence the cite check cannot read

The cite check does not accept these files as sources. So their figures are quoted here only, exactly as each file writes them, and the checked sections below describe them in words.

- `docs/research/manchester-page-run/serp-findings.md` (the banked SERP of 2026-09-23; the eight pool pages re-read 2026-10-07):
  - "Every ranking page is a feed of other people's adverts; none is a breeder answering a Manchester buyer in its own voice."
  - "On Google a breed-and-place statement wins, not the colour and not a question: all five banked Google top-five H1s name "Staffordshire Bull Terrier" and Manchester (or "Salford, Manchester"), all five say "for sale" (puppies.co.uk "for Sale near me"), and none says "blue"."
  - "The colour wins only on Bing, where #1 is the exact-match statement "Blue Staffordshire Bull Terrier Puppies For Sale In Manchester" and #5 pastes the raw query ("Blue staf …")."
  - "The shape to beat keeps "blue Staffy puppies" and "Manchester" in the title and H1 — the one term Google's banked top five leave out — and takes the unclaimed ground: question H2s that answer the Manchester buyer, over a real FAQ block."
  - Staffie Owners' Salford facet holds Google #2 in the banked read "with a neighbouring-town facet whose name carries the keyword's place", and the template "links to 58 distinct Greater Manchester Staffie hubs (paths ending `-manchester`, plus the Manchester hub) among 137 place hubs". Its Bolton blue facet (banked #6; #3 on the live read of 2026-10-07) "is outside the pool and was not read".
  - "On every page "Manchester" is a search filter, not where the sellers are: the cards actually in Greater Manchester run from none (the blue facet's 7 matches; puppies.co.uk's 3 adverts) to 9 of 24 (Pets4Homes)."
  - Its universal gaps include "No table", "No deposit terms in the page's own voice", "No delivery answer", "No honest location", "No remote viewing in the page's own voice", "No health tests, guarantee or paperwork in the page's own voice", "No single accountable breeder with prices" and "No question-led body headings: question H2s are 0 on all eight pages (by script)".
  - "Google's People Also Ask asks six buyer questions, four of which no pool page answers."
- `docs/research/manchester-page-run/fanout.md` (2026-10-07):
  - "**Dominant: transactional.**" The secondary layer is "commercial investigation, price first, then suitability", and "A third strand is new on the live page: **rescue or adoption** … Some Manchester searchers are weighing a breeder against a rescue."
  - "Page one splits the city into Salford, Bolton and Greater Manchester facets, and one related search is "near Salford". The buyer thinks in boroughs, not just "Manchester"."
  - "We have no Manchester address. The local answer is UK home delivery by DEFRA-approved transport, priced by distance …, or collection in Carlisle."
  - Owner language: "NOT FETCHED — no thread could be read for owners' own words". One search-result excerpt, language only and not a verified reading: "Avoid the puppy farmers on Gumtree."
- `docs/research/manchester-page-run/ai-overview.md` (2026-10-07; headless, signed out, placed by Google in Birmingham): "AI Overview shown: no"; "BlueStaffyUK does not appear on page one"; and "a short, honest "rescue or breeder" passage is citable. Today no listing page on page one answers that question."
- `docs/research/manchester-page-run/free-keyword-signals.md` (2026-10-07):
  - §1, autocomplete ("Google suggests the phrase, so people search it. It says nothing about how many."): the first suggestion for `blue staffy puppies manchester` is "blue staffy puppies for sale manchester". "Neighbourhood seeds with a for-sale suggestion of their own: Salford, Bolton, Stockport, Oldham, Rochdale, Wigan, Bury. Trafford and Altrincham return only Manchester or Wythenshawe suggestions; Tameside returns nothing."
  - §3, the planner's ranges: search volume, not quoted here.
- `docs/research/manchester-page-run/keyword-universe.json` (DRAFT, 2026-10-07):
  - Its groups are "hero, title, H1 and first 100 words", "G1 deposit and viewing", "G2 litter and prices", "G3 delivery to Greater Manchester", "G4 health and raising", "G5 life in Manchester" and "G6 FAQ".
  - It places the primary and the generic for-sale phrases in the hero zone together.
  - It places Salford, Stockport, Bolton, Wigan and Rochdale, and the for-sale forms for Bolton, Stockport, Oldham, Rochdale and Wigan, in G3.
  - It parks the cheap, under-£N, free-to-good-homes and marketplace-named phrases as BRAND_CLASH.
- `docs/research/manchester-page-run/entities.md` (2026-10-07):
  - The engine's answer, as quoted there: "Can I see the puppy with its mother, at the place where it was raised? Don't agree to meet in a car park or have the puppy delivered to you". Its flag 4: "The AI answer argues against delivery."
  - Places: Greater Manchester and Salford are PROPOSED; "Stockport (COMP 4/5), Wigan (COMP 4/5), Rochdale (COMP 2/5), Bolton" are held for the `bsuk-city-places` pass, because "Manchester has no city-places file yet". "Bolton also appears in the AI answer only as the town of a competitor business (Bonosue), which is not a reason to name it."

## Strategy A — S1: the cluster strategy's Manchester row, verbatim

Source: `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md:118` (the Concrete Artifact row) and `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md:108` (the "First three build steps", step 2). Quoted unchanged:

> | topic or page | target keyword | gap score | intent | link role | new or rebuild |
> |---|---|---|---|---|---|
> | Manchester — `/uk-locations/blue-staffy-puppies-manchester-uk/` (question-file, provisional) | staffordshire bull terrier puppies for salein manchester greater manchester (the row's own spelling) | 10 (3+2+3+2) high (keyword-gap); matrix city 11/20; matrix keyword "staffies in manchester" 1/19 low | transactional, local | city spoke → UK hub, listing, buying guide | rebuild (stub, project 5) |

> 2. Rebuild the Manchester stub (`/uk-locations/blue-staffy-puppies-manchester-uk/`) on the Manchester high row. Answer the question-file high-band checks (provisional): microchip and vaccinations. Link out to the Royal Kennel Club and the PDSA, both cited in its answer.

**Note.** Nothing in the row is dropped. Its keyword is printed in the row's own spelling: the source heading runs "sale" and "in" together, so a page can only carry it as "for sale in" (keyword-gap, note on city rows). Its two checks still stand: the 2026-10-07 llm-intel file keeps microchip and vaccinations as the only high-band entities in the engine's answer (question-file kind, provisional).

### S1 in this file's terms (a reading, not a rewrite)

- **Thesis.** Manchester is the matrix's second most contested city, at 11/20 on the city scale (the /20 includes the tier-5 report, which lists no city), and its keyword-gap row scores 10 (3+2+3+2), high on the points scale. The cluster strategy builds the contested stubs first, each deep from its own outline, each answering the checks its own AI answer names.
- **Leads with.** The row's full-breed for-sale phrase and the engine's checklist: microchip and vaccinations (high band), then the medium-band checks.
- **Primary keyword and title shape.** "staffordshire bull terrier puppies for salein manchester greater manchester", read as "for sale in": the full breed name, "for sale", Manchester and Greater Manchester in the title and H1. The phrase comes from the Pets4Homes Manchester listing (keyword-gap; suggested page type listing). The colour is not in it.
- **Section emphasis.** The buyer checks, beside outbound links to the Royal Kennel Club (tier 2, `link_allowed` true) and the PDSA (tier 3, `link_allowed` true), both cited in the engine's answer.
- **Other parts.** Its link plan, schema plan and risks are the cluster strategy's Strategy A, in the same file:
  - links up to the UK hub and the index, down to the listing, and across to the buying guide, the health page and the price page;
  - the location markup BSUK already emits, with Person on the licensed-breeder page rather than here;
  - its named risks: city priority measures how many competitors publish a town page, not local demand; building pages one after another invites templated prose.
- **Evidence.** The cluster strategy (Strategy A and its Concrete Artifact); `docs/research/keyword-gap-2026-09-25.md` (the Manchester row); `docs/research/gap-matrix-2026-09-25.md` (city and keyword gaps); `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json`.
- **Why it could win.** It is already set for the whole city cluster, and it puts the high row's words in the title and H1 on the second most contested city.
- **Expected outcome (no traffic figure).** In the cluster strategy's own words: "The contested cities stop being noindex placeholders in the order competitors contest them. Each city page carries the local detail and the buyer checks that the marketplace town pages lack. Each also answers the checks its own AI answer names, which makes it a candidate citation where today no answer cites BSUK."
- **Trade-off.** It predates Manchester's own research and drops the colour:
  - the SERP read, the refreshed question file, the free keyword signals and the AI Overview read are all of 2026-10-07;
  - it names no answer to the deposit-before-viewing fear the plan carries over as its first ruling, and none to the pool's missing delivery and location answers;
  - the query file's primary, the stub's H1 and the URL all say blue, and its phrase does not;
  - its two checks rest on the question-file llm-intel kind (provisional), and its two outbound links fall short of the project 5 external-link rule, which the page board must fill whichever direction runs.

## Strategy B — S2: blue in the H1, for sale in the title — one accountable breeder answers the Greater Manchester buyer

**Rests on:**
- `docs/research/manchester-page-run/serp-findings.md` ("Why they rank", "What shape wins", "Universal gaps", "People Also Ask against the pool");
- `data/queries/blue-staffy-puppies-manchester-uk.json` (the questions, their scores and the word target);
- `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-10-07.json`;
- `docs/research/manchester-page-run/fanout.md` (the intent layers), `ai-overview.md` (the GEO implication) and `entities.md` (groups G1–G6 and flag 4);
- `docs/research/keyword-gap-2026-09-25.md` and `docs/research/gap-matrix-2026-09-25.md`;
- the Staffie Owners, Pets4Homes, Freeads, Gumtree and Preloved reports, for the deposit and location gaps;
- `docs/research/competitors/bsuk.json`, for the buy page's Manchester delivery heading.

**Thesis.** Every page in Manchester's pool is a feed of other people's adverts, and on each one "Manchester" is a search filter, not where the sellers are (serp-findings). None states deposit terms of its own:
- Staffie Owners: "each seller sets their own. The site states none".
- Pets4Homes: "No deposit amount or terms are stated."
- Freeads: "the fetched pages show no platform deposit terms".
- Gumtree: "No deposit is mentioned on any fetched page."

None says how a puppy reaches a Manchester home, and Preloved's Manchester Staffy page shows the same UK-wide adverts as its national search, none of them in or near Manchester. Yet those are the buyer's top questions. "Where can I buy a blue Staffy puppy near Manchester?" and "Should I see the puppy with its mother before any money changes hands?" share the question file's second-highest score (5) with the price question, behind only "Are the parents of your blue Staffy puppies health-tested?" (6). S2 bets that Manchester wins by being the one page that answers those questions in the breeder's own voice, in that order. It also bets that the colour can stay in the H1 at no cost, because the title carries the for-sale family.

**Why it could win.** The answer lane is empty: no pool page uses a question H2 or states its own deposit, delivery or location answer, and the engine's high-band checks are not yet carried by the question file's picks (llm-intel, provisional).

**Leads with.** "Where can I buy a blue Staffy puppy near Manchester?" (score 5; found in the engine's answer and the site's question bank), answered honestly:
- the puppies are with us in Carlisle (the BSUK profile's base town), not in Manchester;
- how the buyer sees the puppy and its mother before any money changes hands, answered as the plan's first ruling sets it;
- what the deposit does: it holds the puppy and comes off the price (the BSUK profile's terms), with the refund clause read from data;
- how the puppy comes home: delivery priced by distance, or collection (the BSUK profile's terms);
- the Greater Manchester boroughs are named here, as places we deliver to.

That meets the engine's warning against meeting in a car park or having the puppy delivered (entities, flag 4) in the same answer as the delivery.

**Primary keyword and title shape.**
- **H1:** the primary's words together, "blue Staffy puppies" and Manchester. That is the stub's own H1, "Blue Staffy Puppies Manchester UK", or the picked angle's question if it carries the same words (London's H1 became its angle's question).
- **Title:** the for-sale family stacked with the colour and the full breed name, in the shape of Bing's first result for the primary, "Blue Staffordshire Bull Terrier Puppies For Sale In Manchester". That puts the keyword-gap row's words (the full breed name, "for sale", Manchester), 10 (3+2+3+2), high on the points scale, in the title.
- **Opening lines:** the short for-sale family ("Staffy puppies for sale in Manchester", "Staffies for sale") and Greater Manchester, where the keyword universe's hero zone already places them beside the primary.
- The matrix's "staffies in manchester" (1/19, low on the matrix scale) rides as a secondary.

**Section emphasis.** The keyword universe's groups, in this order; every H2 and H3 is a buyer question.
1. Where to buy near Manchester, seeing the puppy before any deposit, and how the puppy gets there (G1 with G3; the boroughs named).
2. The deposit and the viewing: "Should I see the puppy with its mother before any money changes hands?" (score 5), answered from the deposit terms in data (G1).
3. The litter and its price: "How much does a blue Staffy puppy cost?" (score 5, from People Also Ask) (G2).
4. What comes with the puppy (G2, G4). Microchip and vaccinations lead it: they are the only high-band entities in the engine's answer, and the question file's picks do not carry them (llm-intel, question-file kind, provisional). The rest of the list is read from `data/settings.json` `puppy_trust_signs`, and the puppy purchase contract follows.
5. The parents' tests, named with no result: "Are the parents of your blue Staffy puppies health-tested?" (score 6) (G4).
6. Life in Manchester, and rescue or breeder (G5). These are People Also Ask's suitability questions (aggressive, left alone, good pets, male or female), which no pool page answers in its own voice, plus the rescue strand page one now shows.
7. The FAQ blocks, from the question file's picks (G6).

**Cluster → page map.** Everything lands on the existing stub URL, rebuilt under project 5. There is no second Manchester URL and no borough URL. The general "questions to ask the breeder" topic, 7 (0+2+3+2), high on the points scale, stays with the buying guide and the planned faq page; Manchester answers only its Manchester slice.

**Internal-link plan.** Every link goes on the page board before it is built.
- **Up:** `/uk-locations/` and the UK page `/uk-locations/blue-staffy-puppies-uk/`.
- **Down:** `/available-puppies/`, and each puppy's own page from the litter answer.
- **Across:**
  - `/blue-staffy-health-uk/` from the tests answer;
  - `/uk-blue-staffy-puppy-buying-guide/` from the buyer-checks answer;
  - `/blue-staffy-pup-sale-uk/` from the price answer;
  - `/uk-blue-staffy-breeders-contact/` as the next step after the deposit answer, to ask to see the puppy.
- **Watch:** the BSUK profile shows that `/buy-blue-staffy-puppies-uk/` already carries the H2 "Need Staffy Puppy Delivery to London, Manchester, or Beyond? We Can Help!". Manchester's delivery answer goes deeper and links to that page rather than repeating it.
- **Outbound,** each beside the answer it supports:
  - the Royal Kennel Club (tier 2) and the PDSA (tier 3), both `link_allowed` true and both cited in the engine's answer;
  - Dogs Trust (tier 4, `link_allowed` true) for the rescue-or-breeder answer: its report finds a Manchester rehoming-centre page in its site map.

  Never a classifieds competitor, a tier-1 breeder, the tier-5 entry or a licensing page.

**Schema plan.**
- Keep FAQPage, BreadcrumbList and the location markup BSUK's location pages already emit.
- Add Person for the breeder as the signed byline, the name read from `data/settings.json` `breeder_name`. Person is 5/20 on the matrix schema scale, medium, and BSUK has none (the 5/20 includes the tier-5 report).
- No licence property. No Review or AggregateRating markup: the matrix marks BSUK "no" on both, and none is invented.

**Build order and effort.** One page, in page-run order. The outline (STOP 2) opens on where to buy near Manchester and seeing the puppy before any deposit. Then come the deposit and viewing, the litter and its price, what comes with the puppy, the named tests, life in Manchester, and the FAQ blocks. The effort is prose: every answer is written fresh from the outline, and every fact comes from data or the rulings. It is the most writing of S1–S3.

**Expected outcome (no traffic figure).** Manchester becomes the only page in its pool that, in the seller's own voice:
- says where the puppies are and how one reaches Greater Manchester;
- states its deposit terms and answers how the buyer sees the puppy before paying;
- names what comes with the puppy and the tests the parents have had, with no result.

It is also the only one signed by a named breeder, and its H1 keeps the colour that the pool's Google results leave out of theirs. It carries the engine answer's high-band checks, which makes it a candidate citation where today no answer cites BSUK.

**Trade-off.** It gives up Google's for-sale H1 for the colour, and gives the boroughs a line each rather than a section.

**Risks.**
- **It skips Google's winning H1.** Every Google result in the pool says "for sale" with the breed and Manchester in its H1, and none says blue (serp-findings). S2 keeps blue there and carries the for-sale family in the title and opening lines only. If Google keeps rewarding the statement, better answers alone may not move the page.
- **The boroughs get a line each,** not a section (S3 gives them one).
- **The lead answer argues with the engine.** It must carry the first ruling's answer on seeing the puppy before any deposit in the same answer as delivery, or the page contradicts the answers it wants to be cited in.
- **Health.** The tests are named, never a result, and the question file's "DNA tested clear" pick is not used as worded.
- **The buy page's Manchester delivery heading** could compete with the delivery answer (see the link plan).
- **Templated prose.** A long question-led page invites it, so the outline-only rule applies.

## Strategy B — S3: Staffy puppies for sale across Greater Manchester — the for-sale family leads, borough by borough

**Rests on:**
- `docs/research/manchester-page-run/serp-findings.md` ("What shape wins", the Staffie Owners facets, "Structural read", "SERP schema");
- `docs/research/manchester-page-run/free-keyword-signals.md` §1 (autocomplete) and `keyword-universe.json` (the G3 placements);
- `docs/research/manchester-page-run/fanout.md` (the local layer) and `entities.md` (Place and geography);
- `docs/research/competitors/staffie-owners.md` and `docs/research/competitors/puppies.md`, for the town-hub model;
- the Pets4Homes and Freeads reports, for inventory;
- `docs/research/keyword-gap-2026-09-25.md` and `docs/research/gap-matrix-2026-09-25.md`;
- `data/queries/blue-staffy-puppies-manchester-uk.json`.

**Thesis.** Google answers this query with breed-and-place "for sale" statements, and it splits Greater Manchester into towns. Staffie Owners' Salford facet is among the pool's Google results, its Bolton blue facet comes next in the banked read and higher in the live one, and puppies.co.uk lists the nearest towns (serp-findings). The registry reports show the model behind it:
- Staffie Owners' first map returned 46 URLs against a limit of 500, "and every one is a Staffie for-sale town hub in Lancashire or Greater Manchester";
- Puppies.co.uk "wins Staffy-plus-town searches with a hub for every town".

Autocomplete attests a for-sale suggestion of its own for Salford, Bolton, Stockport, Oldham, Rochdale, Wigan and Bury (free-keyword-signals; attested, not counted). So S3 bets that page one's own shape wins, and that one breeder's page can take it honestly:
- the for-sale family leads the title and the H1;
- the litter comes first, at its data prices, in a table that stacks on phones (no pool page has a table), and says up front that the puppies are in Carlisle;
- one section group answers the Greater Manchester buyer borough by borough: delivery, collection and seeing the puppy before any deposit, for the towns autocomplete attests;
- then the deposit and viewing, the named tests and the FAQ blocks.

**Why it could win.** It copies the shape the pool's Google results share, on the page type every competitor whose page types were read holds (matrix page type listing 19/19), and it names the boroughs page one splits the city into.

**Leads with.** The answer to "Are there Staffy puppies for sale in Greater Manchester?" from data: the named puppies and their prices, where they are, and how they reach each borough. The question file blocks its blue twin, "Are there blue Staffordshire Bull Terrier puppies available for sale in Manchester?", as an unverified fact, so S3 answers it only from the puppy data.

**Primary keyword and title shape.**
- **Title and H1:** the for-sale family first, "Staffy puppies for sale" with Manchester and Greater Manchester (the H1 a buyer question if the picked angle makes it one). The title's tail carries the full breed name, so the keyword-gap row's words, 10 (3+2+3+2), high on the points scale, are in the title.
- **The colour** moves to the opening and the litter table.
- **Borough phrases** go in the borough group's H3s: the for-sale forms the keyword universe places in G3 (Bolton, Stockport, Oldham, Rochdale, Wigan), and Salford from the question file's related search "Staffy puppies for sale near Salford".
- The matrix keyword "staffie puppies for sale" (2/19, low on the matrix scale; BSUK "no") rides as a variant.

**Section emphasis.** The litter and prices (G2) first and the borough group (G3, enlarged) second. Deposit and viewing (G1), health (G4) and the FAQ blocks (G6) follow. Life in Manchester (G5) shrinks into the FAQ.

**Cluster → page map.** The same stub URL, rebuilt under project 5. The boroughs are sections on this page, never URLs of their own: the cluster strategy allows no second URL for a city. Each puppy keeps its own page under `/available-puppies/`, and the table links each row to it.

**Internal-link plan.**
- **Down, as the page's main job:** each table row to its puppy's page, and `/available-puppies/`.
- **Up:** `/uk-locations/` and the UK page.
- **Across:** the price page and the health page, and the buy page's delivery section from the borough group.
- **Outbound:** as in S2. Never a classifieds competitor, a tier-1 breeder, the tier-5 entry or a licensing page.

**Schema plan.**
- An ItemList of Product and Offer, built from `data/puppies.json` and never typed. The matrix shows BSUK already emits Product and ItemList (1/20 each, BSUK "yes"), so S3 reuses markup the site has.
- FAQPage and BreadcrumbList, with the location markup kept. Person is optional here.

**Build order and effort.**
1. The `bsuk-city-places` pass first: Greater Manchester and Salford are proposed places, and Stockport, Wigan, Rochdale and Bolton wait on that pass (entities).
2. Data wiring: the table and its markup, read from data.
3. The borough group, then the deposit, health and FAQ answers.

It needs less prose per section than S2 but more sections that carry the same facts, more data and schema work, and a refresh every time a litter changes.

**Expected outcome (no traffic figure).** Manchester matches the shape the pool's Google results share: a for-sale breed-and-place statement, inventory and prices up front, and ItemList, Product and Offer markup, all on one breeder's real litter. It names the towns page one splits the city into. It is the only page in its pool that lists puppies a Manchester buyer can actually have, at printed prices, and says where they are.

**Trade-off.** It takes Google's for-sale shape and the borough split at the cost of the colour in the H1 and of borough sections that share one answer.

**Risks.**
- **The boroughs share one answer.** Our base is Carlisle (the BSUK profile), the delivery terms in data are priced by distance with no price per town, and the page states no mileage or drive time. So each borough section would carry the same delivery, collection and viewing facts under a new town name. That is the weakness the Puppies.co.uk report names ("The hubs are templated"), and the near-duplicate text the duplicate-content audit and the outline-only rule exist to catch.
- **It drops the colour from the H1:** the term the pool's Google results leave out, the query file's primary, the stub's H1 and the word the kept URL carries.
- **One litter against far bigger feeds.** The Pets4Homes report counts adverts "137 across the UK and 28 for Manchester", and the Freeads report counts "about 250 adverts across the UK" on its Staffy hub. The shape rewards live inventory, which one litter cannot match.
- **The same puppies are listed twice.** Manchester and `/available-puppies/` (and each puppy's page) compete for the listing intent, and their Product markup repeats. The keyword-gap file already lists "staffy puppies for sale" as covered by `/available-puppies/`.
- **The table empties** as puppies go home.
- **The for-sale family pulls price-floor searches.** The question file's related searches include "Staffy puppies for sale Manchester under 500" and "Staffy puppies for sale Manchester gumtree" (both blocked as unverified facts), and the keyword universe parks them as brand clashes.
- **The places are not ready.** Stockport, Wigan, Rochdale and Bolton wait on a `bsuk-city-places` pass, and the Bolton facet Google shows is outside the pool and unread (session brief, live SERP drift).
- **The worry sits low.** The deposit-before-viewing fear, which the plan's first ruling puts first, sits below the inventory and the boroughs.

## Recommendation — S2 (Recommended)

**Pick: S2, blue in the H1, for sale in the title — one accountable breeder answers the Greater Manchester buyer.** It is not provisional. Its WHY rests on:
- the question file;
- the gap matrix and the keyword-gap file;
- the Staffie Owners and Puppies.co.uk reports.

The llm-intel files are the `question-file` kind and provisional. They are used as support only, and are marked so wherever they are used.

### WHY

- **The answer lane is empty; the listing lane is full.**
  - The question file sets no word target from the pool. It excludes every pool page but one as a listing, because the card grid holds 100% of the prose on the Pets4Homes Manchester listing and 82% on Staffie Owners' blue and Manchester facets.
  - The one page it can use, Freeads, is a feed as well: 3,922 words under one clean content H2.
  - Staffie Owners' facets print an `h2_raw` of 22 against an `h2_clean` of 0: their body headings are advert titles.
  - S3's table and borough sections would add one more listing to a pool of listings. S2's page of answers has no rival in it.
- **Borough coverage is the marketplaces' game, played at scale.**
  - Staffie Owners' first map returned 46 URLs against a limit of 500, every one a for-sale town hub in Lancashire or Greater Manchester, and its homepage links to 100 town hubs. Puppies.co.uk has "a hub for every town".
  - Nothing we can state changes from one borough to the next: our base is Carlisle, delivery is priced by distance with no price per town in data, and the page states no mileage or drive time. A borough group would repeat one answer under each town name. S2 names the boroughs once, inside the delivery answer, where the facts are true.
- **The colour costs nothing on the high row.**
  - S2's title pairs the full breed name with Manchester and "for sale". So the keyword-gap row's words, 10 (3+2+3+2), high on the points scale, are carried as they are under S1 and S3.
  - That row sits on the matrix's second most contested city (Manchester 11/20; the /20 includes the tier-5 report, which lists no city).
  - The H1 keeps the colour that the query file's primary, the stub's H1 and the URL carry, and that the pool's Google results leave out.
- **A named breeder closes a matrix gap on this page.**
  - Person is 5/20 on the matrix schema scale, medium (the 5/20 includes the tier-5 report).
  - S2 signs the page with the breeder's name, read from data, and marks it up as Person. S1's cluster plan put Person on the licensed-breeder page, whose central claim the 2026-09-27 ruling keeps off the site.
- **Support (provisional).** The engine's answer names microchip and vaccinations in the high band, and the question file's picks do not carry them (llm-intel, question-file kind, provisional). S2 answers both in its what-comes-with-the-puppy answer, as S1 would.

### The pick's downside

- **It gives up Google's for-sale H1.** Every Google result in the pool names the breed and Manchester and says "for sale" in its H1, and none says blue (the live read of 2026-10-07 adds Staffie Owners' Bolton blue facet among them, outside the pool and unread). S3 would copy that statement into its H1. S2 keeps the colour there and carries the for-sale family in the title and opening lines only. If Google keeps rewarding the statement, S2 waits on answers and citations while the marketplaces hold page one.
- **The boroughs get a line, not a section.** The borough for-sale phrases autocomplete attests are named once each inside the delivery answer. S3 would give them a section group of their own.
- **It is the most writing.** Every section is a prose answer in the breeder's voice, written fresh from the outline. S3's table and markup carry more of its page from data.
- **Its lead answer argues with the engine.** The engine's answer warns against having the puppy delivered, and S2 leads with delivery. So the first ruling's answer on seeing the puppy before any deposit must sit in that same answer. S3 meets the warning lower down, in its borough group, and S1 does not lead with delivery at all.

### Tie-break

Not needed: S2 wins on the WHY above. Had one been needed, neither rule would separate S1, S2 and S3:
- **Rule one** (the highest keyword-gap band first): each carries the high row's words, the full breed name with "for sale" and Manchester, in its title or H1.
- **Rule two** (the highest matrix share first): each rebuilds the same stub, on Manchester's 11/20.

### First three build steps

1. **STOP 1, the research board.** Offer S2 first, marked (Recommended), with this why and downside, and show S1 and S3 as the alternatives. Show the keyword decision beside the board's keyword universe, where the planner's ranges sit. Nothing is outlined until the user picks.
2. **STOP 2, the outline (if S2 is picked).**
   - The H1 keeps "blue Staffy puppies" and Manchester. The title stacks the colour, the full breed name, "for sale" and Manchester. The opening lines carry the short for-sale family and Greater Manchester.
   - Open on the question file's own words, "Where can I buy a blue Staffy puppy near Manchester?", answered honestly: the puppies are in Carlisle; seeing the puppy and its mother before any deposit, as the plan's first ruling sets it; the deposit terms, read from data; delivery priced by distance, or collection; the boroughs named here.
   - Then the deposit and viewing, the litter and its price, what comes with the puppy, the named tests (no result), life in Manchester with rescue or breeder, and the FAQ blocks from the question file's picks. Every H2 and H3 is a buyer question.
3. **STOP 3, the page board.**
   - Markup: Person for the breeder (`breeder_name`), FAQPage, BreadcrumbList and the location markup.
   - Links: every link above goes on the board, with the buy page's Manchester delivery section linked, not repeated.
   - Limits: no licence, no health result, and no mileage or drive time.

## Sources

- `docs/research/gap-matrix-2026-09-25.md`
- `docs/research/keyword-gap-2026-09-25.md`
- `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-10-07.json`
- `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json`
- `data/queries/blue-staffy-puppies-manchester-uk.json`
- `data/competitors.json`
- `docs/research/competitors/staffie-owners.md`
- `docs/research/competitors/pets4homes.md`
- `docs/research/competitors/freeads.md`
- `docs/research/competitors/gumtree.md`
- `docs/research/competitors/puppies.md`
- `docs/research/competitors/preloved.md`
- `docs/research/competitors/dogstrust.md`
- `docs/research/competitors/trojanstaffuk.md`
- `docs/research/competitors/staffordshirebullterrierkennel.json`
- `docs/research/competitors/bsuk.json`
- `docs/research/competitors/bsuk.md`
- `data/page-map.json`
- `data/locations.json`
