STALE: docs/research/competitors/petsforlove.json (fetched_on NOT FETCHED — homepage gated, the site gave no response; the keyword-gap header lists it as its only stale report)
fresh: docs/research/gap-matrix-2026-09-25.md, docs/research/keyword-gap-2026-09-25.md, docs/research/llm-intel/blue-staffy-puppies-london-2026-09-30.json (fetched_on 2026-09-25, stale list empty), data/queries/blue-staffy-puppies-london.json (fetched 2026-09-30), docs/research/london-page-run/serp-findings.md (2026-09-30), data/queries/raw/blue-staffy-puppies-london/backlinks.response.json (2026-09-30), data/competitors.json, docs/research/competitors/staffie-owners.md, pets4homes.md, freeads.md, staffordshirebullterrierkennel.json and bsuk.json (pages fetched_on 2026-09-25), data/page-map.json, data/locations.json — carrying on with what exists

# London page strategy directions — 2026-09-30

Scope: one page, `/uk-locations/blue-staffy-puppies-london/`. It is a project 5 rebuild of the existing stub, never a new URL. The BSUK profile (`docs/research/competitors/bsuk.json`) lists no London page, and `data/page-map.json` holds a stub there: 4 words and an empty H1, with `noindex, follow` in `data/locations.json`. This is London plan Task 15, step 2 (`docs/superpowers/plans/2026-09-30-london-page-run.md`).

## How to read this file

- **S1** is the cluster strategy's London row, quoted verbatim from `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md` line 107, with one note under it. It is not rewritten here.
- **S2 and S3** are the two strategies this file writes. Each is a different bet on what the London page is for, not a reordering of the same sections.
- Exactly one of S1–S3 is marked **(Recommended)**, with its why and its downside (working rule 4).
- **Where the check reads.** The cite check (`scripts/strategy_cite_check.py`) reads figures only under headings that begin "Strategy A", "Strategy B" or "Recommendation". So S1 sits under Strategy A, and each alternative sits under its own Strategy B heading (S2, then S3). All three are checked.
- **Scales.** The gap matrix's high / medium / low is a share of competitors. The keyword-gap's high / medium is a points score. The llm-intel bands are a third measure, per entity. Each use below names its scale, and none is merged with another.
- **LLM intel.** `blue-staffy-puppies-london-2026-09-30.json` is the `question-file` kind and is provisional. The stub is noindex, so the engine's answer was checked against the question file's picks, not a built page. S1 rested on the 2026-09-25 file, which is the `page-map` kind. The two kinds were checked against different page text, so their bands are never compared here. `bsuk_cited` is false: the answer cites the Kennel Club and UKStaffyPups (tier 1), not BSUK.
- **Tier 5.** The tier-5 entry (staffordshirebullterrierkennel) holds a London map-pack slot (`data/competitors.json` notes). It appears below only as a risk, never as a link or a model. The matrix's Person 5/20 includes its report.
- **No traffic figures.** GSC and GA4 are not fetched until project 6. No traffic, ranking or search-volume figure appears here, and the keyword-volume response bought on 2026-09-30 is not used.
- **Business facts** (prices, the deposit amount, the delivery band, the guarantee) are read from data by the page and are not typed here. The deposit and content rulings are cited by number from the London plan:
  - Ruling 1: what the deposit does, and the video call offered before it;
  - Ruling 2: no refund wording until the `deposit-wording` branch lands;
  - Ruling 4: name the tests, never a result;
  - Ruling 5: nothing about a licence.
- **The reader.** The user's answer to Q8 in `docs/superpowers/sessions/2026-09-30-session-brief.md` is that the London buyer's main worry, and main reason to leave, is "having to pay the deposit before seeing the puppy".

## Evidence the cite check cannot read

The cite check does not accept these files as sources. So their figures are quoted here only, exactly as each file writes them, and the checked sections below describe them in words.

- `docs/research/london-page-run/serp-findings.md` (2026-09-30, the nine saved pool pages):
  - "Every ranking page is a feed of other people's adverts or a template; none is a breeder answering a London buyer in its own voice."
  - "No ranking page has a question H2 or a topical body section (question H2s: 0 of 9, by script)".
  - "No table: 0 `<table>` elements on all nine pages".
  - Its universal gaps include "No deposit terms in the page's own voice", "No delivery answer", "No honest location", "No remote viewing in the page's own voice" and "No byline".
  - "Authority does not decide Google: the domain that owns it has the weakest link profile in the pool (rank 14, 51 referring domains, against Pets4Homes' 17,047 and Freeads' 3,517 referring domains)".
  - "The shape to beat keeps the breed-colour-London phrase in the title and H1 and takes the unclaimed ground: question H2s that answer the London buyer, over a real FAQ block."
- `data/queries/raw/blue-staffy-puppies-london/backlinks.response.json` (2026-09-30, `rank_scale` one_hundred):
  - staffie-owners.co.uk: rank 14, 51 referring domains;
  - pets4homes.co.uk: rank 59, 17047;
  - freeads.co.uk: rank 51, 3517;
  - englishbluestaffypuppies.com: no rank field, 149;
  - ukpets.com: rank 44, 2638.
- `docs/research/london-page-run/aio-google-2026-09-30.md` (Google AI Overview, captured 2026-09-30) tells buyers: "Always visit the puppy in person and see them interact with their mother in the home environment." It also records: "BlueStaffyUK is not cited."

## Strategy A — S1: the cluster strategy's London row, verbatim

Source: `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md:107`, the cluster strategy's "First three build steps", step 1. Quoted unchanged:

> 1. Rebuild the London stub (`/uk-locations/blue-staffy-puppies-london/`) on "staffordshire bull terrier puppies and dogs for sale in london". Answer the page-map high-band checks (provisional): health tests, L-2-HGA, HC-HSF4, meet the mother, microchip, vaccinations, KC registration, licence and contract. The licence answer stays a placeholder. Carry breeder proof against the tier-5 map-pack listing, never naming or linking it. Build through `grill-me`.

**Note.** The user's later ruling (2026-09-27) keeps every licence claim off the site: no number, no council, no claim and no licensing link. So S1's "licence" item is dropped, not answered with a placeholder. Its other checks stand as quoted.

### What S1 rests on

- **Keyword.** Its keyword is the keyword-gap file's London row, "staffordshire bull terrier puppies and dogs for sale in london". That row scores 10 (3+2+3+2), high on the points scale, from a Petify London listing (suggested page type: listing).
- **City.** London is the matrix's most contested city, at 12/20 on the city scale. The /20 includes the tier-5 report, which lists no city.
- **Checks.** Its checks are the high band of the 2026-09-25 llm-intel file, which is the `page-map` kind (provisional).
- **Other parts.** Its link plan, schema plan and risks are the cluster strategy's Strategy A, in the same file:
  - links up to the UK hub and the index, down to the listing, and across to the buying guide, the health page and the price page;
  - the location markup BSUK already emits;
  - the tier-5 risk.

## Strategy B — S2: deposit first, the breeder's answers to the London buyer

**Rests on:**
- `docs/research/london-page-run/serp-findings.md`;
- `data/queries/blue-staffy-puppies-london.json`;
- `docs/research/llm-intel/blue-staffy-puppies-london-2026-09-30.json`;
- `docs/research/gap-matrix-2026-09-25.md` and `docs/research/keyword-gap-2026-09-25.md`;
- `data/queries/raw/blue-staffy-puppies-london/backlinks.response.json`, for competitor authority;
- the Staffie Owners, Pets4Homes and Freeads reports;
- the session brief's Q8.

**Thesis.** Every page in London's research pool is a marketplace feed or a website-builder template, and no page uses a question H2 (serp-findings). None states deposit terms of its own. The registry reports say the same:
- Staffie Owners: "each seller sets their own. The site states none".
- Pets4Homes: "No deposit amount or terms are stated."
- Freeads: "the fetched pages show no platform deposit terms".

Yet the deposit is the London buyer's main worry (Q8). The question file asks it in a buyer's own words: "Should I see the puppy with its mother before any money changes hands?" It comes from a Reddit thread and the site's question bank, and it shares the file's top score (5) with the UK price question. S2 bets that London wins by being the one page that answers that worry first and plainly. It then takes the next things a London buyer asks:
- how the puppy gets to London;
- which puppies are available, and at what price;
- which health tests the parents have had;
- what life with a Staffy in London is like.

Every body heading is a buyer question, as the user ruled.

**Target clusters.** The questions below use the question file's wording; the keywords are picked at STOP 1.
- **Deposit and viewing (the lead).**
  - The questions: "Should I see the puppy with its mother before any money changes hands?" (score 5), "Is it safe to pay a deposit to a seller I found through an online advert?" (score 4), "How much is the deposit?", "How do I reserve one of your Blue Staffy puppies?" and "Can I visit you before I decide?".
  - The engine's answer names "deposit", and the question file's picks do not carry it (llm-intel: `on_page` false, medium band; question-file kind, provisional).
- **Getting the puppy to London.** "Can I get a blue Staffy puppy delivered to my home?" and "Do you deliver across the UK?" (top block, score 4 each).
- **The litter and its price.** "How much are blue Staffy puppies in the UK?" (score 5, from People Also Ask), "How much is a blue Staffordshire puppy?" and the related search "Blue staffy puppies london price".
- **The checks the engine's answer names.** In the llm-intel file, HC-HSF4, microchip, vaccinations, KC registration and contract are high band and not carried (question-file kind, provisional).
  - Microchip, vaccinations, KC registration and contract are answered together, as what comes with the puppy.
  - HC-HSF4 and L-2-HGA are named in the health answer beside eye and elbow testing, with no result.
- **London life.** "Can a Staffordshire Bull Terrier live in a flat?", "Is a Staffy a good house dog?" and "Is it better to get a male or female Staffy?".
- **Title and H1.** The query file's primary keyword, "blue staffy puppies london", leads.
  - The H1 keeps breed, colour and London together and pairs the full breed name with London. That closes the keyword-gap's London row, 10 (3+2+3+2), high on the points scale.
  - The matrix's "staffies in london" and "staffie puppies in london" (1/19 each, low on the matrix scale) ride as secondaries.

**Cluster → page map.** Everything lands on the existing stub URL, rebuilt under project 5. There is no second London URL. The general "questions to ask the breeder" topic, 7 (0+2+3+2), high on the points scale, stays with the buying guide and the planned faq page. London answers only its London slice.

**Internal-link plan.** Every link goes on the page board before it is built.
- **Up:** `/uk-locations/` and the UK page `/uk-locations/blue-staffy-puppies-uk/`.
- **Down:** `/available-puppies/`, and each puppy's own page from the litter answer.
- **Across:**
  - `/blue-staffy-health-uk/` from the health answer (the internal source for health claims, plan Ruling 4);
  - `/uk-blue-staffy-puppy-buying-guide/` from the buyer-checks answer;
  - `/blue-staffy-pup-sale-uk/` from the price answer;
  - `/uk-blue-staffy-breeders-contact/` as the next step after the deposit answer, to ask for the video call.
- **Watch:** the BSUK profile shows that `/buy-blue-staffy-puppies-uk/` already carries the H2 "Need Staffy Puppy Delivery to London, Manchester, or Beyond? We Can Help!". London's delivery answer goes deeper and links to that page rather than repeating it.
- **Outbound,** each beside the check it supports:
  - the Royal Kennel Club (tier 2, `link_allowed` true; the engine's answer cites the Kennel Club);
  - the RSPCA or the PDSA (tier 3).

  Never a classifieds competitor, a tier-1 breeder, the tier-5 entry or a licensing page.

**Schema plan.**
- Keep FAQPage for the FAQ blocks, BreadcrumbList and the location markup BSUK's location pages already emit.
- Add Person for Lisa Bright as the signed byline. Person is 5/20 on the matrix schema scale, medium, and BSUK has none (the 5/20 includes the tier-5 report).
- No licence property.
- No Review or AggregateRating markup: the matrix marks BSUK "no" on both, and none is invented.

**Build order and effort.** One page, in page-run order. The outline (STOP 2) opens on the deposit question, answered from plan Ruling 1:
- the deposit books the viewing and reserves the puppy;
- it comes off the price;
- it is paid by bank transfer;
- a live video call with the puppy and its mother is offered on request before any deposit.

Next come viewing and collection in Carlisle and delivery to London. Then the litter and its parents (Maggie and Jones), then the named tests, then London life, then the FAQ blocks from the question file's picks. The effort is prose: every answer is written fresh from the outline, and every fact comes from data or the rulings. It is the most writing of S1–S3.

**Expected outcome (no traffic figure).** London becomes the only page in its research pool that states, in the seller's own voice:
- the deposit terms;
- the viewing path;
- the way a puppy reaches London.

It is also the only one signed by a named breeder. It carries the engine answer's deposit and see-the-mother checks, and most of its high-band checks. That makes it a candidate citation, where today no answer cites BSUK.

**Risks.**
- **It skips the winning shape.** It does not copy the listing shape that holds Google's page one for this query: facet templates with live counts and ItemList, Product, Offer and FAQPage markup (serp-findings). If Google keeps rewarding that shape, better answers alone may not move the page.
- **The refund wording is pending (plan Ruling 2).** Until the `deposit-wording` branch lands, the lead answer can say what the deposit does and offer the video call first. It cannot yet say when the money comes back.
- **Buyers hear the opposite advice.** The engine's answer lists meeting the mother as a check, and Google's AI Overview tells buyers: "Always visit the puppy in person". The page must be plain that the deposit books the in-person viewing, and that the video call comes before any money.
- **Health.** The tests are named, never a result. The engine's answer also names "dna clear" and "test certificates" (medium band). Those stay unanswered, because the breeder holds no DNA certificates (plan Ruling 4).
- **Licence.** It is high band in the engine's answer and stays unanswered, under the 2026-09-27 ruling.
- **Tier 5.** The tier-5 entry holds a London map-pack slot (registry notes). The page answers it with breeder proof and never names or links it.
- **The buy page.** The buy page's London-delivery H2 could compete with the delivery answer (see the link plan).
- **Templated prose.** A long question-led page invites it, so the outline-only rule applies.

## Strategy B — S3: the honest listing, Google's page-one shape with one breeder's litter

**Rests on:**
- `docs/research/london-page-run/serp-findings.md`, for the page-one shape and the SERP schema;
- `data/queries/raw/blue-staffy-puppies-london/backlinks.response.json`, for competitor authority;
- `docs/research/keyword-gap-2026-09-25.md` and `docs/research/gap-matrix-2026-09-25.md`;
- `data/queries/blue-staffy-puppies-london.json`;
- `docs/research/llm-intel/blue-staffy-puppies-london-2026-09-30.json`;
- the Freeads and Pets4Homes reports.

**Thesis.** On Google, London's page one is one template, not one page. Its facet listings:
- put breed, colour and place in the title and H1;
- open with a live count and a price range;
- mark every advert up as ItemList, Product and Offer;
- close on an FAQPage block (serp-findings).

Links do not decide it: the site that owns it has the weakest link profile in the pool (serp-findings and the backlinks file). So S3 bets that the shape wins, and that BSUK can take it honestly with a litter-led London page:
- first, BSUK's own named puppies at their data prices, in a table that stacks on phones, marked up from data as an ItemList of Product and Offer;
- in the opening lines, where the puppies are (Carlisle) and the priced trip to London;
- then the question H2s and the FAQ blocks.

It aims at the listing intent that the keyword-gap's London row names: suggested page type listing, 10 (3+2+3+2), high on the points scale. It also aims at the page type every competitor whose page types were read holds (matrix page type listing 19/19).

**Target clusters.**
- **Listing phrases.**
  - "blue staffy puppies london", the query file's primary keyword;
  - the keyword-gap's "staffordshire bull terrier puppies and dogs for sale in london";
  - the matrix's "staffies in london" and "staffie puppies in london" (1/19 each, low on the matrix scale).

  The H1 pairs the full breed name with London, as the facet template does.
- **Price and availability, first.** "How much are blue Staffy puppies in the UK?" (score 5, from People Also Ask), "How much is a blue Staffordshire puppy?", the related search "Blue staffy puppies london price", and "How do I know a puppy is still available?" (top block).
- **Then, in the FAQ blocks:** the deposit and viewing questions, delivery to London, the paperwork and the named tests.

**Cluster → page map.** The same stub URL, rebuilt under project 5, with no second London URL. Each puppy keeps its own page under `/available-puppies/`, and the London table links each row to it.

**Internal-link plan.**
- **Down, as the page's main job:** each table row to its puppy's page, and `/available-puppies/`.
- **Up:** `/uk-locations/` and the UK page.
- **Across:** the price page and the health page.
- **Outbound:** as in S2, the Royal Kennel Club and the RSPCA or the PDSA. Never a competitor, the tier-5 entry or a licensing page.

**Schema plan.**
- An ItemList of Product and Offer, built from `data/puppies.json` and never typed.
- FAQPage and BreadcrumbList, with the location markup kept.
- The matrix shows BSUK already emits Product and ItemList (1/20 each, BSUK "yes"), so S3 reuses markup the site has.
- Person is optional here.

**Build order and effort.**
1. Data wiring first: the table and its markup, read from data.
2. Then the opening lines: where the puppies are, the price range from data, and how the puppies reach London.
3. Then the question H2s and the FAQ blocks.

It needs less prose than S2 and more data and schema work, and it needs a refresh every time a litter changes.

**Expected outcome (no traffic figure).** London matches the shape that holds Google's page one. It is the only page in its pool that lists one breeder's puppies with printed prices and says where they are. A buyer who wants a listing sees puppies and prices first.

**Risks.**
- **The same puppies are listed twice.** London and `/available-puppies/` (and each puppy's page) compete for the same listing intent, and their Product markup repeats.
- **One litter against far bigger feeds.** The Freeads report counts "about 250 adverts across the UK" on its Staffy hub. The shape rewards live inventory, and BSUK cannot win that count.
- **The table empties.** As puppies go home, the page's core depends on the current litter.
- **"London" as a label.** A listing headed London for puppies in Carlisle repeats the pool's weakness, unless its first lines say where the puppies are.
- **The worry sits low.** The deposit worry and the top-scored see-the-mother question sit below the inventory, in the FAQ.
- **The same limits as S2.** The tier-5 map-pack risk, the licence ruling and the pending refund wording apply here too.

## Recommendation — S2 (Recommended)

**Pick: S2, deposit first, the breeder's answers to the London buyer.** It is not provisional. Its WHY rests on:
- the question file;
- the gap matrix;
- the keyword-gap file;
- the Staffie Owners, Pets4Homes and Freeads reports.

The llm-intel file is the `question-file` kind and provisional. It is used as support only, and is marked so wherever it is used.

### WHY

- **The lane S2 takes is empty; the lane S3 takes is full.**
  - The question file sets no word target from the pool. It excludes every listing page because the card grid holds between 80% and 100% of its prose. The one page it can use, the breeder site, has 51 words. So the word target is NOT FETCHED — fewer than two prose competitor pages (1 used).
  - Staffie Owners' London facets print an `h2_raw` of 22 against an `h2_clean` of 1 or 0: their body headings are advert titles.
  - S3 would add one more card grid to a pool of card grids. S2's page of answers has no rival in it.
- **The worry is the gap every rival leaves.**
  - The Staffie Owners, Pets4Homes and Freeads reports each find no deposit terms of the site's own.
  - "Should I see the puppy with its mother before any money changes hands?" shares the question file's top score (5).
  - The engine's answer names "deposit", and the question file's picks do not carry it (llm-intel, question-file kind, provisional).
  - S2 answers the worry first, S3 answers it under the inventory, and S1's checklist does not name it.
- **A named breeder closes a matrix gap on this page.**
  - Person is 5/20 on the matrix schema scale, medium (the 5/20 includes the tier-5 report).
  - S2 signs the page and marks Lisa Bright up as Person.
  - S1's cluster plan put Person on the licensed-breeder page. The 2026-09-27 ruling now keeps that page's central claim off the site.
- **It gives up nothing on the London high row.**
  - S2's H1 pairs the full breed name with London. So the keyword-gap's London row, 10 (3+2+3+2), high on the points scale, closes as it would under S1.
  - That row sits on the matrix's most contested city (London 12/20).

### The pick's downside

- **It gives up the page-one shape.** S3 would copy the listing template Google rewards here: a live count, ItemList, Product and Offer, and FAQPage. S2 does not. It sends listing-minded buyers down to `/available-puppies/`, and waits on trust and citations while the template holds Google.
- **Its lead answer is not finished.** Until the `deposit-wording` branch merges (plan Ruling 2), the lead section can say what the deposit does and offer the video call before it. It cannot yet say when the money comes back. S1 and S3 do not lead with the deposit, so they wait on nothing.
- **It is the most writing.** Every section is a prose answer in the breeder's voice, written fresh from the outline. S3's table and markup carry more of its page from data.
- **The checklist gets less room than in S1.** Microchip, vaccinations, KC registration and contract share one paperwork answer instead of leading the page.

### Tie-break

Not needed: S2 wins on the WHY above. Had one been needed, neither rule would separate S1, S2 and S3:
- **Rule one** (the highest keyword-gap band first): each rebuilds the same stub and pairs the full breed name with London in its title or H1, so each closes the same high row.
- **Rule two** (the highest matrix share first): each sits on London's 12/20.

### First three build steps

1. **STOP 1, the research board.** Offer S2 first, marked (Recommended), with this why and downside. Show S1 and S3 as the alternatives. Nothing is outlined until the user picks.
2. **STOP 2, the outline (if S2 is picked).**
   - Open on the question file's own words, "Should I see the puppy with its mother before any money changes hands?", answered from plan Ruling 1.
   - Then delivery to London and collection in Carlisle, the litter and its parents, the named tests (no result) and London life.
   - Close with the FAQ blocks from the question file's picks.
   - The H1 keeps breed, colour and London, and every H2 and H3 is a buyer question.
3. **STOP 3, the page board.**
   - Markup: Person for Lisa Bright, FAQPage, BreadcrumbList and the location markup.
   - Links: every link above goes on the board.
   - Limits: no licence, no refund wording until Ruling 2 lands, and no health result.

## Sources

- `docs/research/gap-matrix-2026-09-25.md`
- `docs/research/keyword-gap-2026-09-25.md`
- `docs/research/llm-intel/blue-staffy-puppies-london-2026-09-30.json`
- `data/queries/blue-staffy-puppies-london.json`
- `data/competitors.json`
- `docs/research/competitors/staffie-owners.md`
- `docs/research/competitors/pets4homes.md`
- `docs/research/competitors/freeads.md`
- `docs/research/competitors/staffordshirebullterrierkennel.json`
- `docs/research/competitors/bsuk.json`
- `data/page-map.json`
- `data/locations.json`
