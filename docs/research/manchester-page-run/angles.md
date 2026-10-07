# Manchester angles (page-run row 8)

Date: 2026-10-07 · Page: `/uk-locations/blue-staffy-puppies-manchester-uk/` (slug `blue-staffy-puppies-manchester-uk`) · Agent: `bsuk-angle-agent` · Plan: `docs/superpowers/plans/2026-10-07-manchester-page-run.md`, Task 10 step 1.

**Mode:** the page's angle, set by the brief passed in (no interview).

**Keyword:** blue staffy puppies manchester (the question file's primary). The Strategy A row's target is the breed phrase "staffordshire bull terrier puppies for sale in manchester greater manchester" (session brief, SESSION CONTEXT).

**Reader:** a Greater Manchester buyer afraid of a deposit scam and a farmed or sick puppy (session brief, Today's Target). For this task the fears are ranked scam/deposit · farmed puppy · sick puppy · support · cost.

**H1 register:** every header is an FAQ-style buyer question (the user's ruling, 2026-09-27, project 5 decisions q05), so every H1 hook below is a question. The page is a stub with no verbatim set (`intake.txt`: Rule 15 applies — no), so the H1 is open.

Manchester's angles are its own. London's three were read only for shape and to check overlap, never as copy: `docs/research/london-page-run/angles.md` and the `angles` field of `data/research-boards/blue-staffy-puppies-london.json`. The overlap check is the last table in this file.

## Grounding, cited by short name

- **SERP** = `docs/research/manchester-page-run/serp-findings.md` (the eight saved page-one pages; section named).
- **FAN** = `docs/research/manchester-page-run/fanout.md` (People Also Ask, related searches, threads, intent).
- **AIO** = `docs/research/manchester-page-run/ai-overview.md`. The live Google read of 2026-10-07 showed no AI Overview in that session, so none is used as grounding. Its GEO notes are cited where they apply.
- **KWS** = `docs/research/manchester-page-run/free-keyword-signals.md` (§1 autocomplete, §2 Trends, §3 Keyword Planner ranges).
- **KU** = `docs/research/manchester-page-run/keyword-universe.json`.
- **ENT** = `docs/research/manchester-page-run/entities.md`.
- **LLM** = `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json`. ChatGPT was asked "Where can I buy a blue Staffy puppy near Manchester, and what should I ask the breeder?" and did not cite BlueStaffyUK. The answer text is in `data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.response.json`.
- **QF** = `data/queries/blue-staffy-puppies-manchester-uk.json` (question id and score given).
- **RKC** = the Kennel Club's Staffordshire Bull Terrier page, https://www.royalkennelclub.com/search/breeds-a-to-z/breeds/terrier/staffordshire-bull-terrier/ (the link library's row, `docs/reference/external-link-library.md` line 40).
  - Read 2026-10-07 for this file: curl with a desktop user agent, HTTP 200, 256,611 bytes. The capture is not banked in the repository.
  - In its colour section the page says "health and temperament should always be a priority over colour".
  - It lists Blue, Blue & White and White among the breed-standard colours. The colour list is also `data/breed-standards.json` `colours` (fetched 2026-10-03).

Three limits on the evidence:

- Demand is read only as the planner's bucketed ranges (KWS §3). A range is never narrowed to a number or turned into a ratio.
- Search Console: NOT FETCHED — the GSC property is unverified (domain expired) and no exports are on disk.
- Owner language from opened threads: NOT FETCHED — Reddit's network-security block stopped every rung on 2026-10-07 (FAN §2). The excerpts cited below are search-result excerpts: they show language only, never a fact.

## The facts every angle may use

| Fact | Source |
|---|---|
| £500 books your viewing and reserves your puppy, and it comes off the price | `data/settings.json` `deposit_gbp`; `src/lib/cityKit.ts` `depositLine` (the user's rulings, 2026-09-27) |
| the deposit's refund term, added only where a deposit sentence already carries it | `data/settings.json` `deposit_refund_clause`, written `{deposit_refund_clause}` in the hooks: read from data, never typed, never a plain "refundable" |
| a live video call with the puppy and its mother, on request, before any deposit; the deposit is paid by bank transfer | answer board 2026-09-29 q03 and q04 (`docs/reference/answer-board/answers/2026-09-29-lisa-bright-five-facts-before-the-london-page-2026-09-29.md`) |
| boys £1,500 each: Roman (blue and white), Byrd (white), Ince (blue). Girls £1,700 each: Vennie (blue and white), Christa (blue), Cheryl (blue with white blaze). The price matrix has a key per sex and none per colour | `data/puppies.json` `colour`, `price_gbp`; `data/price-matrix.json` `male_gbp`, `female_gbp` |
| UK home delivery £200–£350 by DEFRA-approved transport, priced by distance, or collection in Carlisle | `data/settings.json` `delivery_min_gbp`, `delivery_max_gbp`, `delivery_note`, `address.city` |
| Maggie (dam) and Jones (sire). DNA tests for L-2-HGA and HC-HSF4, and eye and elbow screening: named, never with a result. Their certificates reach a buyer after first contact | follow-up answers 2026-09-27; `data/faq.json` `about-health-tests`, `whyus-evidence`; ledger `certificates-on-request`. Ledger `parents-dna-clear` stays NOT FETCHED — the certificates are held by the breeder, not on file in the repository |
| vet-signed health card, first vaccinations, microchip, worming and flea treatment | ledger `puppy-vet-signed-health-card`; `data/faq.json` `health-vaccinations` |
| raised in our home, never in kennels; Puppy Culture and ENS | ledger `litters-home-raised-never-kennels`; follow-up Q16 |
| the take-back promise is in the written contract: if the fault is ours, or if you can no longer care for the puppy | answer board 2026-09-29 q05; follow-up 2026-09-27 Q6 |
| questions after collection are answered by us, not an agency | ledger `breeder-support-after-collection`; `data/faq.json` `home-after-support` |
| the guarantee and what it covers | `data/settings.json` `guarantee_label`, `guarantee_cover`, written `{guarantee_label}` and `{guarantee_cover}` in the hooks |

The figures in the hooks are what those keys hold on 2026-10-07. The page prints them from data (`cityKit.ts` `BOY_PRICE`, `GIRL_PRICE`, `DEPOSIT`, `DELIVERY_BAND`), never typed.

What every angle leaves out:

- **No licence, registration or statute claim** (working rule 9). The brief's "licensing" fear is met only by what goes home: the paperwork as `data/faq.json` `whyus-paperwork` names it, and the KC registration application form (ledger `parents-kc-registered-application-form`).
- **No health result.** Tests are named only. No "health certificates", "vet checked" or "KC registered" in our own sentence (the ledger vocabulary).
- **No mileage or drive time** (Known Issue 16; ENT, Place). The brief's "120 miles" stays out of every hook; the hooks name Carlisle and Manchester instead.
- **No plain "refundable"**, and no "pay before you see" framing: the deposit books the viewing.
- **Blue is named plainly, never "rare"** (LLM; ENT `ont:blue-coat`).
- **No competitor is named or counted on the page.** Page-one figures are evidence for an angle, not copy.
- **No bargain, giveaway or rescue wording.** `scripts/keyword_variants.py` `BRAND_CLASH` lists these as terms "a BlueStaffyUK page never writes".
- **"Ince" is only ever our puppy, never the place** (ENT flag 3).

## Scoring

Each candidate is scored 1–5 on differentiation (D), credibility (C) and reader resonance (R). The score is D × C × R.

- **D** asks what page one, the answer engine and our own London page do not already say. The London page counts because this brief asks for Manchester's own angles.
- **C** asks whether every fact is a data key, a breeder answer on file or a fetched source.
- **R** is measured against the ranked fears and the question file's scores.

| Angle type | Working hook | D | C | R | Score | Result |
|---|---|---|---|---|---|---|
| Counter-intuitive | Colour comes last, and it doesn't move our price | 5 | 5 | 4 | 100 | **M1 (Recommended)** |
| Fear-validation | Seen before it travels: the delivery warning, answered | 4 | 5 | 5 | 100 | M2 |
| Authority-contrast | After the advert ends: who answers once the puppy is home | 4 | 5 | 3 | 60 | M3 |
| Counter-intuitive (2) | Rescue or breeder? | 5 | 4 | 3 | 60 | cut: brand clash |
| Data-driven | "Manchester" on page one is a filter: count the cards | 4 | 3 | 3 | 36 | kept as evidence inside M2 |
| Before-after-bridge | From a 99-mile feed to one named home | 3 | 4 | 3 | 36 | cut: London A2's ground |
| Insider revelation | The AI answer's ten questions, answered before you ask | 4 | 2 | 4 | 32 | cut; its answerable half is in every section order |
| Specificity | Every Greater Manchester borough, one named home | 3 | 3 | 3 | 27 | becomes the G3 delivery section in every order |
| Authority-contrast (2) | The under-£500 search against a named breeder | 2 | 3 | 3 | 18 | cut: brand clash |
| Story-first | One Manchester family's route from call to collection | 4 | 1 | 4 | 16 | cut |

Why each cut candidate went:

- **Rescue or breeder?** This is the most Manchester-specific strand on page one:
  - Dogs Trust's Manchester rehoming page is #9 on the live read, and "rescue" and "for adoption" are added to "People also search for" (AIO; FAN §1 and §4).
  - The planner puts "staffy rescue manchester" at 10–100 (KWS §3).

  It still cannot be an H1: `scripts/keyword_variants.py` `BRAND_CLASH` lists rescue wording among the terms "a BlueStaffyUK page never writes". See flag 1.
- **"Manchester" is a filter.** The measured in-area counts come from SERP, Universal gaps, "No honest location". For example, Staffie Owners' blue facet promises 7 Manchester blues and none of them is in Greater Manchester. But the counts are a 2026-09-23 snapshot of competitors' pages: on our page they would name rivals and go stale. They stay as M2's evidence.
- **Before-after-bridge.** The contrast between a feed of adverts and one named home is the opening London's A2 used (London `angles.md`, folded into A2).
- **Insider revelation.** The ChatGPT answer asks ten questions (LLM). We can answer six from data. We cannot answer four:
  - the parents' results and the inbreeding coefficient (ENT, Excluded);
  - the dam's litter count and age, and why these two dogs were bred (no data file holds either).

  A numbered list would put those four gaps on show. The answerable half (video call, paperwork, vet-signed health card, socialisation, take-back) sits in the section orders.
- **Specificity (boroughs).** Buyers do think in boroughs: page one has Salford and Bolton facets, autocomplete offers Swinton and Wythenshawe, and a related search is "near Salford" (FAN §4; KWS §1). It still fails as an angle:
  - The demand is small. "staffy puppies for sale" + Bolton, Stockport, Oldham, Rochdale or Wigan is 10–100; every "staffy puppies <borough>" is 0–10 (KWS §3).
  - No borough fact exists. Delivery is one band priced by distance.
  - Only Greater Manchester and Salford are proposed entities. Bolton, Stockport, Wigan and Rochdale wait for the `bsuk-city-places` pass (ENT, Place).

  The boroughs become the place names in the G3 section.
- **Under £500.** Autocomplete's first suggestion for "staffy puppies for sale manchester" is "… under 500 near me" (KWS §1). But "cheap" and "under £N" are on the same brand-clash list, our prices cannot meet the search, and price-led is London A3's ground.
- **Story-first.** No Manchester buyer's story is on record, so writing one would be invention (working rule 9).

## M1: Colour comes last **(Recommended)**

- **Type:** Counter-intuitive, proved by the price matrix.
- **Thesis:** We breed blue Staffies and still tell Manchester to choose the colour last, because the Kennel Club puts health and temperament first and colour doesn't move our prices.
- **H1 hook:** Should Colour Decide Which Blue Staffy Puppy Comes Home to Manchester?
  - **Intro:** Not on its own, and we breed blue Staffies. The Kennel Club says health and temperament should always be a priority over colour, and colour doesn't move our prices: Byrd, our white boy, is £1,500, the same as blue Ince, and each of our three girls is £1,700. So we start you with Maggie and Jones's health screening and how the litter was raised, and leave the coat to last.
- **Meta hook (159 characters):** Our blue Staffy puppies cost one price per boy and one per girl whatever the coat, and reach Manchester from a Carlisle home that puts health first: meet them.
- **Fear it answers:**
  - Farmed puppy first: "rare blue" marketing and colour premiums are the warning signs the answer engine names.
  - Sick puppy second: health comes before colour, with the screening named.
  - Cost third: this litter has no colour premium.
  - It does not answer the first-ranked fear in its opening. The deposit comes in section 2.
- **Section order:**
  1. Hero: does colour decide? The six puppies, one price per sex.
  2. G1 deposit and viewing: the video call on request before any deposit; what £500 books, with `{deposit_refund_clause}`; bank transfer.
  3. G4 health and raising: the four screenings named, certificates after first contact, the vet-signed health card, home-raised, Puppy Culture and ENS.
  4. G2 litter and prices: each puppy, boy or girl.
  5. G3 delivery to Greater Manchester.
  6. G5 life in Manchester: good pets, aggression, being left alone, from Dogs Trust and the PDSA.
  7. G6 FAQ: top, middle and bottom.
- **Rests on:**
  - SERP, "Structural read" and "What shape wins": none of Google's banked top five says "blue" in its title or H1, and the colour ranks only on Bing. London's Google top four were all Staffie Owners blue facets (SERP, head-term table, London rows 1–4). The difference is in the data, not in taste.
  - KWS §3: "staffy puppies for sale manchester", "staffies for sale manchester" and "staffordshire bull terrier for sale manchester" are 100–1K. "blue staffy puppies manchester" and every other blue phrase are 10–100.
  - SERP, competitor 6 (Staffie Owners' blue Manchester facet, Bing #1): page one's only blue-specific claim is a premium. It says blue variants are "trending approximately 61% higher than the market average", by its own "internal marketplace analysis".
  - SERP, Universal gaps, "No answer on colour".
  - LLM: the answer's "Be particularly careful about 'blue'" section warns against "rare blue", "exclusive blue" and unusually high prices, and cites the Kennel Club. Its entities "temperament", "breed standard", "rare blue", "exclusive blue" and "high prices" are all `on_page: false`.
  - RKC: "health and temperament should always be a priority over colour". Blue, blue and white, and white are all breed-standard colours.
  - FAN §1, People Also Ask:
    - "How much does a blue Staffy puppy cost?" (QF `q-how-much-does-a-blue-staffy-cost-uk-4051c2`, score 5, top block, must-answer)
    - "Is it better to get a male or female Staffy?" (4)
    - "Are blue staffies good pets?" (4)
    - "Is blue Staffy aggressive?" (4)
  - FAN §2, threads:
    - "A question for owners of blues" (r/StaffordBullTerriers, 44 replies) asks "Colour or health and temperament first?" and how to tell a responsible blue breeder from a backyard breeder.
    - "To blue or not to blue?" (50 replies; title only).
  - QF's top-scored question: "Are the parents of your blue Staffy puppies health-tested?" (`q-are-the-parents-of-your-blue-staffy-puppy-523777`, score 6, must-answer).
  - `data/price-matrix.json` has `male_gbp` and `female_gbp` and no colour key. `data/puppies.json` prices Byrd (white) at £1,500, the same as Ince (blue).
- **Score:** D5 · C5 · R4 = 100.
  - D: no page-one page says anything about colour in its own voice, and no London angle made this point.
  - C: the prices are data keys, and the Kennel Club line was read at source on 2026-10-07.
  - R: it meets fears two, three and five and the top-scored question, but not the first-ranked fear.
- **Why (Recommended):** see "The pick" below.
- **Trade-off:**
  - The H1 carries neither the first-ranked fear (a deposit scam) nor the answer engine's delivery warning. Section 2 has to carry both, or a cautious buyer leaves first.
  - It asks a breeder named for the colour to say colour is not the first choice.
  - "Colour doesn't move our price" describes this litter's prices. It is not a stated policy, and a line promising it for every litter needs the breeder's yes (flag 2).
  - It cannot explain what makes a Staffy blue: no data file holds the genetics, and QF blocks the inheritance question (ENT, Excluded). "Colour last" must not drift into colour science.
  - The planner's ranges are buckets, so 100–1K against 10–100 shows direction, not a multiple.

## M2: Seen before it travels

- **Type:** Fear-validation of the delivery warning in Manchester's ChatGPT answer.
- **Thesis:** The answer engine's warning against a delivered puppy is right about sellers you cannot see, so we answer it with the order of events: you see the puppy with its mother live from our home, then the deposit books your viewing, and transport comes last.
- **H1 hook:** Is It Safe to Have a Blue Staffy Puppy Delivered to Manchester?
  - **Intro:** Not from a seller you have never seen, and the advice never to take a delivered puppy is right about them. From us, the puppy travels last. Ask, and before any deposit you watch yours with Maggie, its mother, on a live video call from our home in Carlisle. Then £500 books your viewing and reserves your puppy, and comes off the price ({deposit_refund_clause}). Only then does DEFRA-approved transport bring it to your door, priced by distance, unless you collect it here.
- **Meta hook (159 characters):** Blue Staffy puppies delivered to Manchester by DEFRA-approved transport, £200–£350 by distance, from our Carlisle home; ask to see yours with its mother first.
- **Fear it answers:**
  - Scam/deposit first: nothing is paid before you have had the chance to see the puppy with its mother.
  - Farmed puppy second: the car-park meeting and the unseen delivered puppy are the answer engine's own puppy-farm signals, and `data/faq.json` `buying-puppy-farm` names the same ones.
- **Section order:**
  1. Hero: is a delivered puppy safe? The order of events.
  2. G1 deposit and viewing: the video call with Maggie; what £500 books, with `{deposit_refund_clause}`; bank transfer.
  3. G3 delivery to Greater Manchester: DEFRA-approved transport and the band by distance, or collection in Carlisle. Boroughs are named once the city-places pass grounds them.
  4. G2 litter and prices.
  5. G4 health and raising.
  6. G5 life in Manchester.
  7. G6 FAQ: top, middle and bottom.
- **Rests on:**
  - LLM, the answer's first question: "Can I see the puppy with its mother, at the place where it was raised? Don't agree to meet in a car park or have the puppy delivered to you." The entity "car park" is `on_page: false`. London's ChatGPT answer contains neither "deliver" nor "car park" (`data/queries/raw/blue-staffy-puppies-london/ai_engines.response.json`, searched 2026-10-07), so this trigger is Manchester's own.
  - ENT, flag 4: the delivery section has to carry the pre-deposit video call, or the page contradicts the answer engines it wants to be cited by.
  - SERP, Universal gaps: "No delivery answer", "No remote viewing in the page's own voice", and "No honest location" (every Manchester listing pads with puppies from elsewhere).
  - FAN §4, Emotional:
    - "Should I see the puppy with its mother before any money changes hands?" (QF `q-how-can-i-avoid-buying-from-a-puppy-5e9d7e`, score 5, must-answer; from r/UK_Pets, 96 replies).
    - "Is it safe to pay a deposit to a seller I found through an online advert?" and "Should I pay a deposit before I have seen the puppy?" (score 4 each, blocked: unverified fact).
    - The search-result excerpts "Avoid the puppy farmers on Gumtree." and "take your payment online and you never hear from them again." (FAN §3) carry the same fear. They are language only.
  - FAN §4, Local; QF:
    - "Where can I buy a blue Staffy puppy near Manchester?" (score 5, must-answer)
    - "Can I get a blue Staffy puppy delivered to my home?" (4, must-answer). It has no planner range: NOT FETCHED — a thread question longer than the 10 words the planner accepts, so it was not entered (KU).
    - "Do you deliver across the UK?" (4, must-answer)
    - "Can you deliver a Blue Staffy puppy to my location in the UK?" (4)
    - "Can I see the puppy with its mother where the litter was raised?" (4; from the ChatGPT answer; blocked: unverified fact). The video call answers it.
  - AIO, GEO implication "Viewing".
- **Score:** D4 · C5 · R5 = 100.
  - D: page one and the answer engine leave this open, but its proof (the pre-deposit video call) is what London's H1 already leads with.
  - C: every step is a breeder answer or a data key.
  - R: it fronts the first two fears and four must-answer questions.
- **Trade-off:**
  - Its proof is the move London's H1 already makes ("Can I See a Blue Staffy Puppy on Video From London Before Any Deposit?"), so two city pages would answer their opening question the same way. The prose has to be written fresh around the delivery question (`rules/copy.md`, Write-From-Outline), and the headers audit (`dup_content_audit.py --headers`, lessons 18) will be watching.
  - It opens by arguing with an answer engine's advice.
  - The video call is on request, and the visit to Carlisle comes after the deposit. "Seen before it travels" means seen on video before any deposit. The first lines must say so, or the H1 promises a visit.
  - Manchester's own delivery price is not in data, only the band priced by distance.

## M3: After the advert ends

- **Type:** Authority-contrast. Page one's job ends at the advert; ours carries on once the puppy is home.
- **Thesis:** Page one's adverts stop at the sale, while our written take-back promise, our guarantee and our own answers after collection carry on once the puppy is settled in Manchester.
- **H1 hook:** Who Will You Call Once Your Blue Staffy Puppy Is Settled in Manchester?
  - **Intro:** Us, and it's in writing. Our written contract takes your puppy back if the fault is ours or if you can no longer care for it. Our {guarantee_label} {guarantee_cover}. And every question you ask after collection is answered by us, not by an agency.
- **Meta hook (155 characters):** When your blue Staffy puppy is settled in Manchester, our written take-back promise and our own support after collection still stand: ask Lisa about yours.
- **Fear it answers:**
  - Support first: who answers once the seller has been paid.
  - Sick puppy second: the guarantee and what it covers.
- **Section order:**
  1. Hero: who answers after collection. The take-back, the guarantee, our support.
  2. G1 deposit and viewing: the video call on request before any deposit; what £500 books, with `{deposit_refund_clause}`.
  3. G4 health and raising: what the guarantee rests on. The screening named, the vet-signed health card, home-raised.
  4. G2 litter and prices.
  5. G3 delivery to Greater Manchester.
  6. G5 life in Manchester.
  7. G6 FAQ: top, middle and bottom.
- **Rests on:**
  - SERP, Universal gaps:
    - "No support after the sale": "aftercare", "support after" and "ongoing support" are on none of the eight pages, and every page ends its job at the advert.
    - "No single accountable breeder with prices".
  - LLM: "Will you take the dog back or help rehome it if I can't keep it later?" (entity "rehome", `on_page: false`).
  - QF:
    - "Can I contact you for advice for the dog's whole life?" (`q-do-you-offer-support-after-i-take-my-d4ebe8`, score 4, must-answer)
    - "How do I spot a bad Staffy breeder?" (`q-how-do-i-tell-an-ethical-breeder-from-414f97`, 4, must-answer)
  - FAN §3, excerpt 5: "take your payment online and you never hear from them again." It is language only, with no UK signal.
  - The facts behind it:
    - answer board 2026-09-29 q05: the take-back promise is in the written contract;
    - follow-up Q6: the take-back terms;
    - ledger `breeder-support-after-collection`;
    - `data/settings.json` `guarantee_label` and `guarantee_cover`.
- **Score:** D4 · C5 · R3 = 60.
  - D: no page-one page offers anything after the sale.
  - C: every promise is a breeder answer on file.
  - R: support is the fourth fear, and no search on page one asks for it by name.
- **Trade-off:**
  - It answers a question the searcher has not asked yet. A buyer weighs aftercare when deciding, not while searching, so the deposit and delivery questions wait for sections 2 and 3.
  - The take-back is conditional: the fault is ours, or you can no longer care for the puppy. No hook may say "we take any dog back".
  - The "never hear from them again" line it answers is a search-result excerpt with no UK signal, not a quote from an opened thread.

## The pick

**Recommended: M1.** M1 and M2 tie at 100 on D × C × R. On the research, M1 wins four of the five tie-break tests and M2 wins the fifth:

1. **Demand and SERP shape.** Google reads this query as a Staffy query, not a colour query.
   - None of its banked top five says "blue" in a title or H1 (SERP, Structural read).
   - The planner puts the breed phrases at 100–1K, against 10–100 for every blue phrase (KWS §3).
   - M1's frame (breed first, colour second) is the only one that serves both the Strategy A row's breed target and the question file's blue primary.
2. **The answer engine.** M1 agrees with Manchester's ChatGPT answer.
   - The Kennel Club line that answer leans on is verified at source (RKC).
   - The colour-and-temperament points M1 puts on the page ("temperament", "breed standard", the warning about colour premiums) are `on_page: false` today (LLM).
   - M2 has to argue against the same answer's "don't … have the puppy delivered to you".
3. **The questions.** M1 leads with the question file's top-scored question (the parents' health testing, score 6) and with PAA's first question (price, score 5).
4. **Manchester's own.** Page one says nothing about colour in its own voice, and its one blue claim is a premium (SERP, competitor 6). Our price matrix answers that with data. M2's proof is London's opening move.
5. **Fear rank, for M2.** M2 fronts the brief's first-ranked fear, the deposit scam. M1 answers it in section 2.

M1's trade-off is in its block above.

**Alternative, if the deposit fear must be in the H1: M2.** Every section order above answers the deposit and the video call by section 2. Whichever angle is picked, ENT flag 4 holds for G3: the delivery passage carries the video call on request before any deposit.

## Manchester's own: the check against London

| London angle | Its ground | Where it sits in Manchester's three |
|---|---|---|
| A1 (Recommended): See it live first, then the deposit books the visit | the deposit fear, answered by the pre-deposit video call | M2 uses the same proof for a different question: the delivery warning, which only Manchester's answer engine carries. M1 and M3 keep the video call as section 2. |
| A2: We're in Carlisle, and we lead with it | distance and logistics first | No Manchester angle leads with Carlisle or distance. Page one's padding of "Manchester" is evidence inside M2, and the feed-to-named-home contrast is cut. |
| A3: Every figure printed | the whole bill in one place | M1 prints prices only to prove colour doesn't move them. The price-floor candidate is cut. |

Each H1 hook:

- passes the site's Title Case rule, checked both ways against `scripts/page_hardening_scan.py` `MINOR_WORDS`;
- carries "Blue Staffy" and "Manchester";
- is a question;
- matches no heading in `src/`, `data/faq.json` or `data/locations.json` (checked 2026-10-07).

Each meta hook is one sentence in the 140–160 character band (`scripts/pageboard.py` `meta-length`). None rewords London's built description.

## Flags for the controller

1. **Rescue placement.** KU places "staffy rescue manchester" in G5, for a rescue-or-breeder passage, and AIO's GEO notes propose the same passage. But `scripts/keyword_variants.py` `BRAND_CLASH` lists rescue wording among the terms "a BlueStaffyUK page never writes", and KU itself parks "free staffy puppies to good homes manchester" and the first-time-owner rescue question for that reason. No angle here builds on rescue. One of the two has to give before STOP 2.
2. **If M1 is picked, one question goes in the STOP 1 batch:** "Does colour never change your price, for every litter?" Without a yes, the page states only this litter's prices by sex.
3. **The RKC capture is not banked.** It was read for this file only. The writer re-reads the page at the outline; the link library's row (line 40) has the URL.
4. **The delivery warning stands whichever angle is picked** (ENT flag 4).
