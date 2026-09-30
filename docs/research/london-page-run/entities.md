# London entities (page-run row 7)

Date: 2026-09-30 · Page: `blue-staffy-puppies-london` (`/uk-locations/blue-staffy-puppies-london/`) · Agent: `bsuk-entity-incorporation-agent`, Move 2 only (the recommended entities, each with its why). Plan: London page run, Task 13.

Grounding sources, cited by short name below:

- **LLM** = `docs/research/llm-intel/blue-staffy-puppies-london-2026-09-30.json` (`entities[]`, `citations[]`; BSUK is not cited, `bsuk_cited: false`). The answer text is in `data/queries/raw/blue-staffy-puppies-london/ai_engines.response.json`.
- **PAA** = `data/queries/raw/blue-staffy-puppies-london/serp_google.json` `questions[]` (Google PAA and related searches, 2026-09-30).
- **THR** = `data/queries/raw/blue-staffy-puppies-london/threads.json` `questions[]`.
- **QF** = `data/queries/blue-staffy-puppies-london.json` `questions[]` (the page's question file, question id given).
- **GAP** = `docs/research/gap-matrix-2026-09-25.md`.
- **LIB** = `docs/reference/external-link-library.md` Rows table (row line number given).
- **FU** = `docs/reference/answer-board/answers/2026-09-24-questions-for-lisa-bright-followup-2026-09-27.md` (breeder rulings of 2026-09-27).

Section groups: **G1** deposit, viewing and video call · **G2** the litter, prices and parents Maggie and Jones · **G3** delivery to London and collection in Carlisle · **G4** health tests · **G5** raising (Puppy Culture, ENS, home-raised) · **G6** life with a Staffy in London (flats, exercise, children, time alone) · **G7** buyer safety.

**(Recommended)** `ont:refundable-deposit` is the one entity to build the page around. Why: the page's primary reader fear is paying the deposit before seeing the puppy (plan ruling 1, session brief Q8). The engine's answer names "deposit" and BSUK's page does not (LLM, `on_page: false`). THR asks "Is it safe to pay a deposit to a seller I found through an online advert?". QF has `q-how-much-is-the-deposit-2cce23` in the top block. **Trade-off:** the entity's ontology name is "£500 refundable deposit", and plan ruling 2 bars the page from calling the deposit plainly "refundable" until the `deposit-wording` branch lands. So the page names it "£500 deposit" through `cityKit.ts` `depositLine`, never through the entity's name. Renaming the existing row is out of scope for this task. It is flagged for the controller below.

## People

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:lisa-bright` | People | G1, G2, G5, G7 | GAP schema gaps: `Person` is on 5/20 competitors and missing from BSUK (priority queue #1). LLM: BSUK is not cited, and `citation_gap` lists `trojanstaffuk` and `ukstaffypups`, so the page needs a named breeder behind the video call, the viewing and the raising. QF `q-can-i-visit-you-before-i-decide-4fc075`. | existing (ASSERTED) |

## Place

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:london` | Place | all | The primary keyword is `blue staffy puppies london`. GAP city gaps: London is on 12/20 competitors, the highest count of any city. PAA related searches: "Blue staffy puppies london price" and "Blue staffy puppies london kennel club". | existing (ASSERTED) |
| `ont:carlisle` | Place | G1, G3 | Collection is in Carlisle and viewings happen there (`data/settings.json` `address.city`). QF `q-can-i-visit-you-before-i-decide-4fc075`. The page's distance story, London to Carlisle, needs both ends named. | existing (ASSERTED) |
| `ont:cumbria` | Place | G3 | The breeder's region (`data/settings.json` `address.region`). Town and region only, with no street and no postcode (Known Issue 16). | existing (ASSERTED) |

## Organism

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:staffordshire-bull-terrier` | Organism | all | The Knowledge Graph parent term for the breed. LLM lists "staffordshire bull terrier" as a page entity. PAA: "Is a Staffy a good house dog?" and "What are common Staffie behavioral issues?". | existing (ASSERTED) |
| `ont:blue-coat` | Organism | G2 | PAA: "How much is a blue Staffordshire puppy?" and "How rare are blue Staffies?". LLM says blue is a recognised colour and warns against "rare blue" marketing. Name the colour and never call it rare: QF `q-how-rare-are-blue-staffy-c63acb` is `blocked: unverified fact`. | existing (ASSERTED) |
| `ont:maggie` | Organism | G2, G4 | The dam. LLM "meet the mother" (medium) and "pedigree" (medium, not on the page). THR/QF `q-are-the-parents-of-your-blue-staffy-puppy-523777` "Are the puppy's parents health tested?". FU "Which parents": every page names Maggie (dam) and Jones (sire). | **PROPOSED** (added 2026-09-30, source FU) |
| `ont:jones` | Organism | G2, G4 | The sire. Same grounding as `ont:maggie`. LLM: "Why did you choose these two dogs to breed together?" is on its list of questions to ask. | **PROPOSED** (added 2026-09-30, source FU) |

## Commerce

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:refundable-deposit` **(Recommended)** | Commerce | G1, G2, G7 | See the recommendation above. LLM "deposit" (not on the page). THR "Is it safe to pay a deposit to a seller I found through an online advert?". QF `q-how-much-is-the-deposit-2cce23` and `q-how-do-i-reserve-one-of-your-blue-309feb`. Wording: "£500 deposit" from `depositLine`. The deposit books the viewing, reserves the puppy and comes off the price. It is never called plainly "refundable" (plan ruling 2). | existing (ASSERTED) |

## Logistics

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:defra-approved-transport` | Logistics | G3 | QF top-block delivery questions: `q-can-i-get-a-blue-staffy-puppy-delivered-ad16e3` (score 4), `q-can-you-deliver-a-blue-staffy-puppy-to-74fa14` (score 4) and `q-do-you-deliver-across-the-uk-fb0c4a` (score 4). The delivery band comes from `data/settings.json` `delivery_min_gbp` / `delivery_max_gbp` and is never typed. | existing (ASSERTED) |

## Health

The tests are named only. The page states no result, and never "clear", "certified", "tested clear" or "will not be affected" (`data/quality/evidence-ledger.json` row `parents-dna-clear` is `NOT FETCHED — none held: the breeder holds no DNA certificates, answer board q01, 2026-09-29`). `/blue-staffy-health-uk/` is the internal source for health claims (FU Q9).

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:l-2-hga-dna-test` | Health | G4 | LLM "l-2-hga" (medium). The engine's answer tells a London buyer to ask for it by name and cites the Kennel Club health standard. QF `q-what-does-l-2-hga-testing-mean-for-27d9f9`. LIB line 43 (the registry's L-2-HGA page). FU Q9 names it. | existing (PROPOSED) |
| `ont:hc-hsf4-dna-test` | Health | G4 | LLM "hc-hsf4" (**high** band, not on the page). LIB line 44. FU Q9 names it. | existing (PROPOSED) |
| `ont:bva-kc-eye-scheme` | Health | G4 | LLM "eye testing" (not on the page). LIB line 45. FU Q9: "eye screening for hereditary cataracts and other inherited eye diseases". Use the alias **eye screening**: the breeder did not name the BVA/KC scheme, so the page must not say the screening was done under it. | existing (PROPOSED) |
| `ont:elbow-screening` | Health | G4 | LLM "elbow testing" (not on the page), and the engine's answer lists eye and elbow testing beside the DNA tests. FU Q9: "mention elbows as well". Added as a new row because the only existing elbow entity, `ont:bva-hip-elbow-scores`, is a *score*, and a score needs a ledger proof the site does not hold. | **PROPOSED** (added 2026-09-30; source `null`, see note 2) |
| `ont:health-guarantee` | Health | G2, G7 | QF `q-do-you-offer-health-guarantees-for-your-b-04ef4b`. `data/settings.json` now carries `guarantee_label` "Two-year health guarantee" and `guarantee_cover` (q07/q02, 2026-09-29). Read through `guaranteeRow()`, never typed. | existing (PROPOSED, source `data/settings.json`) |

## Method

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:puppy-culture` | Method | G5 | LLM "socialisation" (medium, not on the page). The engine's answer asks "what socialisation has it received?". QF `q-are-the-puppy-raised-in-a-family-home-c93ef5`. FU Q16: litters follow **both** Puppy Culture and ENS. This is a named third-party programme, not a house method, so the agent rule against a named house method does not apply. | **PROPOSED** (added 2026-09-30, source FU) |
| `ont:early-neurological-stimulation` | Method | G5 | Same grounding as `ont:puppy-culture` (FU Q16, "both"). | **PROPOSED** (added 2026-09-30, source FU) |

"Home-raised" is a claim, not an entity. It is carried by `ont:lisa-bright` plus QF `q-are-the-puppy-raised-in-a-family-home-c93ef5` (fact source `src/pages/blue-staffy-uk-breeders/index.astro`) and the breeder's socialisation answer (cats, people, children, other dogs, household noises, car journeys; `docs/reference/answer-board/answers/2026-09-24-questions-for-lisa-bright-2026-09-27.md` Q15).

## Documentation

The paperwork is exactly `data/faq.json` `whyus-paperwork`: the Kennel Club registration paperwork, the vaccination records, the microchipping details and a written puppy purchase contract.

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:kc-registration-paperwork` | Documentation | G2, G7 | LLM "kc registration" (**high**, not on the page). PAA related search "Blue staffy puppies london kennel club" (QF `q-blue-staffy-puppy-london-kennel-club-865a10`, score 3). THR "How can I be sure a puppy's Kennel Club registration will be issued if the papers are delayed?". GAP priority queue #7: `kc registered staffordshire bull terrier puppies` is on 3/19 competitors and missing from BSUK. **Wording:** "Kennel Club registration paperwork", never "KC registered". That phrase matches the evidence-ledger vocabulary `kc-registered` and is an ERROR on a new location page. | **PROPOSED** (added 2026-09-30, source `data/faq.json`) |
| `ont:vaccination-record` | Documentation | G2, G7 | LLM "vaccinations" (**high**, not on the page). QF `q-do-your-puppy-come-with-vet-records-and-30768c`. The heading or answer must not say "health certificate", which matches the ledger vocabulary `health-tested`. | **PROPOSED** (added 2026-09-30, source `data/faq.json`) |
| `ont:puppy-purchase-contract` | Documentation | G1, G7 | LLM "contract" (**high**, not on the page) and "receipt". The engine's answer asks "Can I have a written contract and a receipt?". Breeder answers Q6/Q7: take-back when the fault is ours or the owner can no longer care for the puppy (FU Q6), and the buyer's own vet check within 7 days. | **PROPOSED** (added 2026-09-30, source `data/faq.json`) |

## Organization

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:the-kennel-club` | Organization | G2, G4, G7 | LLM `citations[]`: `thekennelclub.org.uk` is one of only two domains the engine cites, and it is the source it gives for L-2-HGA, HC-HSF4, eye and elbow testing and the breed standard. LLM "kennel club" (not on the page). LIB lines 43, 44 and 51 (questions to ask a breeder). This is the high-authority parent for G4. Name the organisation only. Kennel Club Assured Breeder membership (breeder answer Q18, "Yes") is a credential with no ledger row, so the page does not claim it. | existing (ASSERTED) |
| `ont:bva` | Organization | G4 | LIB line 45 (the BVA eye scheme page, the examination for the inherited eye disease that HC-HSF4 does not cover). **Wording:** never put "BVA" within 20 characters of "hip", "elbow" or "score". That matches the ledger vocabulary `hip-elbow-score`. | existing (ASSERTED) |
| `ont:rspca` | Organization | G7 | THR "How do I tell a genuine online puppy advert from a scam?". QF `q-how-do-i-tell-an-ethical-breeder-from-414f97`. LIB line 52 (the RSPCA on spotting a puppy dealer's advert). | existing (ASSERTED) |
| `ont:paag` | Organization | G7 | THR "How can I tell whether a puppy advert on a UK classifieds site is genuine?" and "Is it safe to pay a deposit to a seller I found through an online advert?". LIB line 66 (PAAG how-to-buy-a-pet advice for online adverts). LLM "online advert" (not on the page). | existing (ASSERTED) |
| `ont:pdsa` | Organization | G6 | QF `q-how-much-exercise-does-a-staffy-need-dail-0d2427` and `q-how-much-exercise-does-a-staffy-need-each-bd9421`. LIB line 56 (PDSA exercise) and line 49 (PDSA Staffordshire Bull Terrier page). | existing (ASSERTED) |
| `ont:dogs-trust` | Organization | G6 | QF `q-can-blue-staffy-be-left-alone-ef945b`, `q-can-a-staffy-live-in-a-flat-310055` and `q-do-staffy-get-along-with-children-and-oth-e9aa5f`. THR "Should I adopt a rescue dog or buy from a breeder?". LIB line 65 (Dogs Trust breed page, a rehoming charity's own account of the breed). | existing (ASSERTED) |
| `ont:blue-cross` | Organization | G5 | LLM "socialisation" (not on the page). LIB line 53 (Blue Cross on socialising a puppy, the independent version of the home-raising section). | existing (ASSERTED) |
| `ont:uk-government` | Organization | G6, G7 | The publisher behind `ont:dog-microchipping-law` (LIB line 46) and `ont:dangerous-dogs-act-1991` (LIB line 50). | existing (ASSERTED) |

## Regulation

| Entity | Class | Groups | Why (grounding) | Status |
|---|---|---|---|---|
| `ont:dog-microchipping-law` | Regulation | G2, G7 | LLM "microchip" (**high**, not on the page). The engine's answer asks "What vaccinations, microchip and worming has it had?". The microchipping details are in `whyus-paperwork`. LIB line 46. The law is named, and the page makes no compliance claim. | existing (ASSERTED) |
| `ont:welfare-in-transport-pb10308` | Regulation | G3 | QF delivery questions (above). LIB line 55 (the government's welfare-in-transport guidance for dogs and cats, the rules DEFRA-approved transport works to). It pairs with `ont:defra-approved-transport` for the London delivery run. | existing (ASSERTED) |
| `ont:dangerous-dogs-act-1991` | Regulation | G6 | QF `q-is-the-staffy-a-banned-breed-in-the-954365` "Is the Staffordshire Bull Terrier a banned breed in the UK?" and `q-is-a-staffy-a-pitbull-e881f1`. LLM "xl staffy" (the engine warns against it). LIB line 50: the Staffordshire Bull Terrier is not on the banned list. This is a London renter and landlord concern. | existing (ASSERTED) |

## Excluded, with reason

| Candidate | Why it is not recommended |
|---|---|
| LLM "licence" (high band) · `ont:animal-licensing-regulations-2018` · `ont:cumberland-council` | **Excluded by the user's ruling of 2026-09-27** (FU Q19–21; plan ruling 5): no licence number, no council, no licence claim and no licensing link on the site. The engine's answer names a licence, and the page still carries none. |
| LLM "dna clear" · "test certificates" | The page states no result, and the breeder holds no DNA certificates (ledger `parents-dna-clear`, `NOT FETCHED — none held: breeder answer q01, 2026-09-29`). The tests are named through the Health entities above. |
| `ont:bva-hip-elbow-scores` | A hip or elbow score needs a ledger proof. FU Q9 allows elbow *screening* only, so `ont:elbow-screening` is used instead. |
| `ont:phpv-test` | It is not in the breeder's Q9 list of the tests the parents had. |
| LLM "plumstead", "canary wharf", "southeast london" | These are the locations of competitor listings in the engine's answer, not places BSUK serves from. Naming them would point a London buyer at `ukstaffypups` and others. `ont:london` covers the city. |
| LLM "rare blue", "blue & tan", "xl staffy", "crossbreed" | These are marketing terms the engine warns buyers against. The page does not use them as its own entities. `ont:blue-coat` is named plainly, and "rare" is blocked (QF `q-how-rare-are-blue-staffy-c63acb`). |
| Kennel Club Assured Breeder Scheme | Breeder answer Q18 says "Yes", but the claim has no evidence-ledger row or proof, so it is a credential the page may not assert. It goes to the answer board if wanted. |
| `ont:pet-travel-rules-gb` | These rules cover bringing a pet *into* Great Britain. A Carlisle-to-London delivery is domestic. |
| Video call (G1) | This is a claim, not an entity: a live video call with the puppy and its mother is offered on request before any deposit (Lisa, answer board q03, 2026-09-29; plan ruling 1). It is carried by `ont:lisa-bright`, `ont:maggie` and `ont:refundable-deposit`. |

## Flags for the controller

1. **Deposit entity name.** `ont:refundable-deposit` is named "£500 refundable deposit", which conflicts with plan ruling 2. The page wording comes from `depositLine`, not the entity name. Renaming or re-aliasing the row is a separate decision and was not made here.
2. **`ont:elbow-screening` has `source: null`.** This follows the file's own convention for Health rows (`scripts/ontology_seed.py` docstring): `board_approve.py` promotes a PROPOSED entity that has a source to ASSERTED when a board using it is approved, and a health entity must not be promoted that way. The grounding is FU Q9 plus LLM "elbow testing", recorded here. Every other new row carries its source.
3. **The Maggie, Jones, Puppy Culture, ENS and the three Documentation rows carry a source,** so an approved board will promote them to ASSERTED. That is intended: each is a breeder-confirmed fact or the listed paperwork, not a health result.
