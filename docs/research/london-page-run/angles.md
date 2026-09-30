# London angles (page-run row 8)

Date: 2026-09-30 · Page: `/uk-locations/blue-staffy-puppies-london/` (slug `blue-staffy-puppies-london`) · Agent: `bsuk-angle-agent` · Plan: London page run, Task 15 step 1.

**Mode:** the page's angle, set by the brief passed in (no interview). **Keyword:** blue staffy puppies london. **Reader:** a London buyer whose main fear, and main reason to leave, is paying the deposit before seeing the puppy (session brief Q8).

Grounding, cited by short name below:

- **SERP** = `docs/research/london-page-run/serp-findings.md` (the nine saved page-one pages, 2026-09-30).
- **QF** = `data/queries/blue-staffy-puppies-london.json` (the question file; question id and score given).
- **THR** = `data/queries/raw/blue-staffy-puppies-london/threads.json`.
- **PAA** = `data/queries/raw/blue-staffy-puppies-london/serp_google.json` `questions[]`.
- **LLM** = `docs/research/llm-intel/blue-staffy-puppies-london-2026-09-30.json` (the ChatGPT answer; BlueStaffyUK is not cited).
- **ENT** = `docs/research/london-page-run/entities.md`.
- **KW** = `docs/research/london-page-run/keyword-universe.json`.
- **INV** = `docs/research/london-page-run/inventory.md`.

The AI Overview is not used as grounding for any angle (this task's brief, 2026-09-30).

No angle is ranked by search demand. Keyword volumes are NOT FETCHED — the DataForSEO Google Ads search-volume call of 2026-09-30 returned no search_volume for any of the 30 keywords sent (KW). Search Console is NOT FETCHED — the GSC property is unverified (domain expired) and no exports are on disk (INV). So the scores lean on the question file's scores, the thread questions and the page-one gaps.

## The facts every angle may use

| Fact | Source |
|---|---|
| a £500 deposit | `data/settings.json` `deposit_gbp` |
| it books the viewing, reserves the puppy and comes off the price | `src/lib/cityKit.ts` `depositLine` (the user's rulings, 2026-09-27) |
| a live video call with the puppy and its mother, offered on request before any deposit | answer board q03, 2026-09-29 (`docs/reference/answer-board/answers/2026-09-29-lisa-bright-five-facts-before-the-london-page-2026-09-29.md`) |
| the deposit is paid by bank transfer | the same file, q04 |
| £1,500 for each of the three boys, £1,700 for each of the three girls | `data/puppies.json` `price_gbp` (`data/price-matrix.json` `male_gbp`, `female_gbp`) |
| UK home delivery £200–£350, priced by distance, by DEFRA-approved transport, or collection in Carlisle | `data/settings.json` `delivery_min_gbp`, `delivery_max_gbp`, `delivery_note`, `address.city` |
| Maggie (dam) and Jones (sire) | the user's ruling, 2026-09-27 (`docs/reference/answer-board/answers/2026-09-24-questions-for-lisa-bright-followup-2026-09-27.md`) |

What every angle leaves out:

- No refund wording and no refund percentage. None is in data yet (plan Ruling 2).
- No "pay before you see" framing. The deposit books the viewing (the user, 2026-09-27, follow-up Q3/Q5).
- Health tests are named only, never with a result. No credential the data does not hold is claimed (plan Rulings 4 and 5).
- No mileage. No distance figure is in data, so A2 names Carlisle and prints the delivery band.

## Scoring

Each angle is scored 1–5 on differentiation (D), credibility (C) and reader resonance (R); the score is D × C × R. The basis for each kept angle is in its own block. The basis for each cut angle is below the table.

| Angle type | Working hook | D | C | R | Score | Result |
|---|---|---|---|---|---|---|
| Fear-validation, reframed | See it live first; the deposit books the visit | 5 | 5 | 5 | 125 | **A1 (Recommended)** |
| Counter-intuitive | We're in Carlisle, and we lead with it | 5 | 5 | 4 | 100 | A2 |
| Data-driven | Every figure printed | 4 | 5 | 4 | 80 | A3 |
| Insider revelation | What to ask Lisa on the video call | 4 | 5 | 4 | 80 | folded into A1 |
| Before-after-bridge | From a feed of other people's adverts to one named breeder | 4 | 4 | 3 | 48 | folded into A2 |
| Fear-validation (scam check) | The checks to run on any seller before a deposit | 3 | 2 | 5 | 30 | cut |
| Specificity | A Staffy in a London flat | 2 | 4 | 3 | 24 | a section in every order |
| Story-first | One London family's route from call to collection | 4 | 1 | 4 | 16 | cut |

- **Insider revelation** ties A3 on score. It rests on the same fear and the same facts as A1, though, so offering it gives the user no real choice. It becomes A1's video-call section instead.
- **Before-after-bridge** describes page one more than the buyer's fear: eight of the nine pages are feeds of other people's adverts (SERP, Structural read). It becomes A2's opening contrast.
- **Scam check.** Buyers do ask for it (THR: "How do I tell a genuine online puppy advert from a scam?"). But the checklist in the ChatGPT answer asks for credentials and certificates this page may not show (ENT, Excluded, with reason, which lists the ChatGPT answer's DNA-result and test-certificate entities). Charities already publish the list, too (ENT rows `ont:rspca` and `ont:paag`). Its safe half, the video call and a named breeder, is already in A1.
- **Specificity.** PAA asks "Is a Staffy a good house dog?" (QF score 4), and one thread is about a Staffy puppy in a second-floor flat (THR, r/puppy101). But the question is informational on a transactional page, and Dogs Trust and the PDSA already answer it (ENT, G6). Every section order below keeps it as the London-life section.
- **Story-first.** No buyer story is on record, so writing one would mean inventing it (working rule 9).

## A1: See it live first, then the deposit books the visit **(Recommended)**

- **Type:** Fear-validation, reframed so that the deposit books the viewing.
- **Hook:** Ask for a live video call with your puppy and Maggie, its mother, before any deposit; then £500 books your viewing, reserves your puppy and comes off the price.
- **H1:** Can I See a Blue Staffy Puppy on Video From London Before Any Deposit?
- **Section order:** hero with the answer first (the video call on request, then the deposit) → the video call: the puppy, Maggie and Lisa → what the £500 deposit books, and paying it by bank transfer → the six puppies and their prices → Carlisle to London: collection or delivery → paperwork, named health tests and the guarantee → home-raising (Puppy Culture, ENS) → London life → FAQ top, middle and bottom.
- **Rests on:**
  - SERP, Universal gaps ("No deposit terms in the page's own voice", "No remote viewing in the page's own voice"), plus competitor 1's weakness.
  - THR: r/UK_Pets "Pets4homesuk" (96 replies).
  - QF: `q-how-can-i-avoid-buying-from-a-puppy-5e9d7e` (score 5, must-answer), `q-is-it-safe-to-pay-a-deposit-to-6c495b` (score 4, top block, blocked: unverified fact), `q-how-do-i-reserve-one-of-your-blue-309feb`, `q-how-much-is-the-deposit-2cce23` and `q-can-i-visit-you-before-i-decide-4fc075`.
  - LLM: the entities "deposit" (`on_page: false`) and "meet the mother".
  - ENT: the recommended entity (the deposit, group G1).
  - The session brief, Q8.
- **Score:** D5 · C5 · R5 = 125.
  - D: no page-one page states deposit terms or offers the video call in its own voice.
  - C: every fact is a breeder answer or a data key.
  - R: it is the user's named fear, in the buyer's own words.
- **Why:** It answers the user's named fear (session brief Q8) where page one is silent: none of the nine saved page-one pages states deposit terms in its own voice (deposits appear only inside sellers' advert text), and none offers a live video call with the puppy and its mother before a deposit; the one mention is a single seller's line in a Freeads advert (serp-findings.md, Universal gaps). Buyers ask it in these words: "Should I see the puppy with its mother before any money changes hands?" is the question file's only score-5 thread question and a must-answer (r/UK_Pets, the most-replied thread, 96 replies), and "Is it safe to pay a deposit to a seller I found through an online advert?" scores 4 in the question file's top block. The ChatGPT answer names "deposit", which the page's must-answer set does not carry yet (llm-intel, on_page false). Every fact the angle needs is already a breeder answer or a data key (q03, q04, depositLine).
- **Trade-off:** Leading with the deposit puts the one question the data cannot answer yet in plain sight: until the deposit-wording branch lands (plan Ruling 2), the page can say what the £500 does but not whether any of it comes back, so a cautious buyer's next question waits on that merge. And only the video call comes before the deposit; the visit to Carlisle comes after it, so the opening has to say so in its first lines, or the H1 reads as a promise of a visit before any deposit.

## A2: We're in Carlisle, and we lead with it

- **Type:** Counter-intuitive: a London page from a breeder who says it is not in London.
- **Hook:** We're in Carlisle, not London, and we lead with it: your puppy reaches your door by DEFRA-approved transport for £200–£350, priced by distance, or you collect here.
- **H1:** How Will My Blue Staffy Puppy Get From Carlisle to London?
- **Section order:** hero (Carlisle, not London, and how your puppy reaches you) → collection or UK home delivery (the band and DEFRA-approved transport) → the video call and what the £500 deposit books → the six puppies and their prices → paperwork, named health tests and the guarantee → home-raising → London life → FAQ top, middle and bottom.
- **Rests on:**
  - SERP, Universal gaps ("No delivery answer", "No honest location").
  - SERP competitor 9: its London is a keyword, and its own copy places the kennel in Lincolnshire.
  - SERP competitor 5: 2 of its 7 London matches are in London.
  - SERP, Structural read: "London" is a filter label.
  - QF: `q-can-i-get-a-blue-staffy-puppy-delivered-ad16e3`, `q-can-you-deliver-a-blue-staffy-puppy-to-74fa14` and `q-do-you-deliver-across-the-uk-fb0c4a` (score 4 each, top block).
  - ENT, group G3: `ont:carlisle` and `ont:defra-approved-transport`.
  - KW: the local phrases "staffie puppies in london" and "staffies in london".
- **Score:** D5 · C5 · R4 = 100.
  - D: no page prices the trip to London or says where its puppies are.
  - C: Carlisle, the delivery band and the transport all come from data.
  - R: three top-block delivery questions score 4, but distance is not the fear the user named.
- **Why it is not first:** It raises the distance before the page has shown the video call that settles the user's named fear (Q8). And London's own delivery figure is not in data (only the £200–£350 band, priced by distance), so the hero can print the band but not London's price.

## A3: Every figure printed

- **Type:** Data-driven: one breeder's whole bill in one place.
- **Hook:** Every figure in print before you ask: £1,500 for a boy, £1,700 for a girl, £200–£350 UK home delivery by distance, and a £500 deposit that comes off the price.
- **H1:** How Much Does a Blue Staffy Puppy Cost, Delivered to London?
- **Section order:** hero (every figure printed) → the six puppies and their prices → the deposit: what the £500 books, that it comes off the price, bank transfer, and the video call before it → the delivery band or collection → what the price includes: paperwork, named health tests and the guarantee → home-raising → London life → FAQ top, middle and bottom.
- **Rests on:**
  - PAA: "How much are blue Staffy puppies in the UK?", "How much is a blue Staffordshire puppy?" and the related search "Blue staffy puppies london price".
  - QF: `q-how-much-does-a-blue-staffy-cost-uk-4051c2` (score 5, top block), `q-how-much-is-a-blue-staffordshire-puppy-360d6c` (score 4), and `q-blue-staffy-puppy-london-price-af3e66` (score 4, blocked: unverified fact, so only our own prices answer it).
  - SERP, Universal gaps ("No table", "No single accountable breeder with prices").
  - SERP competitor 6: its FAQ answers 1 of 5 questions, with a UK-wide average.
  - SERP competitor 9: no price on its ranking URL.
  - KW: the price questions.
- **Score:** D4 · C5 · R4 = 80.
  - D: no page prints one breeder's prices, deposit and delivery together. But Google already shows a live price range as the snippet for three of its top four (SERP, competitors 1–3).
  - C: every figure comes from data.
  - R: price is PAA's top question, but it answers "how much" before "is it safe to pay".
- **Why it is not first:** Price is page one's most claimed ground. And `data/faq.json` already answers "How much does a blue Staffy cost UK?", so a price-led H1 sits closest to an answer the site already gives.

## The pick

**Recommended: A1.** It is the only angle whose H1 answers the user's named fear (Q8). It fills the gap no page-one page fills: none states deposit terms or offers a video call in its own voice. The buyer's own score-5 thread question sits behind it, and every fact it needs is already in data. Its trade-off is in its block above.

**Alternative, if the deposit wording should land before the deposit leads the page: A2** (score 100). Every section order above answers the deposit fear by its third section, so either pick keeps the brief's rule that the page answers the fear head-on (Q8).

Each H1:
- passes the site's Title Case rule (`scripts/page_hardening_scan.py` `MINOR_WORDS`, checked both ways);
- carries "Blue Staffy" and "London";
- is a question;
- matches no heading in `src/`, `data/faq.json` or `data/locations.json` (checked 2026-09-30).
