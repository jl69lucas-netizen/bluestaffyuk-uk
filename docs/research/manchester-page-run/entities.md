# Manchester entities (page-run row 7)

Date: 2026-10-07 · Page: `blue-staffy-puppies-manchester-uk` (`/uk-locations/blue-staffy-puppies-manchester-uk/`) · Skill: `bsuk-entity-agent` (vocabulary), Move 2 only of the `bsuk-entity-incorporation-agent` loop (the recommended entities, each with its why). Plan: `docs/superpowers/plans/2026-10-07-manchester-page-run.md`, Task 9.

`python3 scripts/ontology_seed.py --check` → `examined 79 entities; ontology is seeded`, exit 0. Every id below is a row of `data/bsuk-ontology.json` unless it is marked **PROPOSED (new)**. Nothing was added to the ontology file: a new row is proposed here with its source, for the controller to add.

Grounding sources, cited by short name:

- **LLM** = `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json` (`entities[]` with band, `citations[]`: royalkennelclub.com, pdsa.org.uk, bonosue.co.uk; `bsuk_cited: false`). The answer text is in `data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.response.json` (query "Where can I buy a blue Staffy puppy near Manchester, and what should I ask the breeder?", 2026-09-25). Its `on_page` flags were read against the question file, so they are provisional (strategy file line 13).
- **PAA** = `data/queries/raw/blue-staffy-puppies-manchester-uk/serp_google.json` (Google PAA and related searches, 2026-09-23). **REG** = `data/queries/raw/registry-staffy-puppies-for-sale-manchester/serp_google.response.json` (the registry SERP for "staffy puppies for sale manchester", 2026-09-23).
- **THR** = `data/queries/raw/blue-staffy-puppies-manchester-uk/threads.json` `questions[]`.
- **QF** = `data/queries/blue-staffy-puppies-manchester-uk.json` `questions[]` (question id given).
- **COMP** = the cached competitor pages `data/queries/cache/blue-staffy-puppies-manchester-uk/1.html`–`8.html`, read as five domains: pets4homes.co.uk, staffie-owners.co.uk, gumtree.com, puppies.co.uk and freeads.co.uk. Pages 1–2 and 4–8 were saved on 2026-09-23; page 3 (freeads) was saved on 2026-10-07 and its `blocked` flag cleared, per the `note` in `data/queries/raw/blue-staffy-puppies-manchester-uk/competitors.json` (that update landed while this file was being written, and the counts below include it). "COMP 3/5" means the term is written, on word boundaries, case-folded, on three of the five domains. These are marketplace listing pages, so a hit is a seller's advert wording, not an editorial claim.
- **STRAT** = `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md` (Strategy A, Manchester row line 118; the Manchester build note line 108: "Answer the question-file high-band checks (provisional): microchip and vaccinations. Link out to the Royal Kennel Club and the PDSA").
- **GAP** = `docs/research/gap-matrix-2026-09-25.md`. **LIB** = `docs/reference/external-link-library.md` (row line number given).
- **FU** = `docs/reference/answer-board/answers/2026-09-24-questions-for-lisa-bright-followup-2026-09-27.md`. **LEDGER** = `data/quality/evidence-ledger.json` (row id given). **CERT** = `docs/reference/answer-board/answers/chat-2026-10-05-certificates-on-request.md`.

Section groups (the controller's plan): **G1** deposit and viewing · **G2** litter and prices · **G3** delivery to Greater Manchester · **G4** health and raising · **G5** life in Manchester · **G6** FAQ.

## The one to build around

**(Recommended)** `ont:vet-signed-health-card`. Why: the only two **high**-band entities in Manchester's AI answer are "microchip" and "vaccinations" (LLM, both `on_page: false`), and STRAT line 108 names exactly those two as the checks this page must answer. The answer asks "Has the puppy had a veterinary examination, vaccinations, microchip and worming?". The health card is the one entity that carries all four with a ledger proof: LEDGER `puppy-vet-signed-health-card` (confirmed 2026-10-04) covers a vet-signed health card plus first vaccinations, a microchip, worming and flea treatment, and `data/faq.json` `health-vaccinations` words it. COMP backs the buyer's expectation: microchip and vaccination are on 4/5 domains, worming on 3/5. **Trade-off:** it is a paperwork entity, not a local one, so it does nothing for the page's Manchester relevance on its own; and the AI answer's strongest instruction is a viewing one ("Can I see the puppy with its mother, at the place where it was raised? Don't agree to meet in a car park or have the puppy delivered to you"), which pulls against G3. That tension is carried by `ont:video-call-before-deposit` and `ont:maggie` in G1, not by this entity.

## Breed

| Entity | Ontology class | Groups | Why (grounding) | Attested by | Status |
|---|---|---|---|---|---|
| `ont:staffordshire-bull-terrier` | Organism | all | The breed's Knowledge Graph term and the full-breed-name buying phrase of the strategy row ("staffordshire bull terrier puppies for sale in manchester greater manchester", STRAT line 118). PAA "Is it better to get a male or female Staffy?", "Can a Staffy be left alone for hours?". | COMP 5/5; LLM "staffordshire bull terrier"; `data/settings.json` | existing (ASSERTED) |
| `ont:maggie` | Organism | G1, G2, G4 | The dam. LLM: "Can I see the puppy with its mother, at the place where it was raised?" (the answer's first question). THR/QF `q-how-can-i-avoid-buying-from-a-puppy-5e9d7e` "Should I see the puppy with its mother before any money changes hands?" (score 5). FU "Which parents": every page names Maggie and Jones. | COMP mum/mother 3/5; FU | existing (ASSERTED) |
| `ont:jones` | Organism | G2, G4 | The sire. QF `q-are-the-parents-of-your-blue-staffy-puppy-523777` (score 6, the top-scored question) and `q-who-are-the-bluestaffyuk-stud-dogs-and-ho-54449c`. LLM asks for "the mother's and father's" results. | COMP dad/sire 3/5; FU | existing (ASSERTED) |
| `ont:american-staffordshire-terrier` | Organism | G6 | QF `q-how-can-i-tell-if-my-puppy-is-c8ea81` "American or an English Staffy?" and `q-what-is-the-difference-between-an-amstaff-0fd204`. COMP: an advert listed in Wigan on pets4homes offers "Blue American staffies", so a Manchester buyer meets the confusion in the listings. | COMP 2/5 (pets4homes, freeads); `data/breed-standards.json` | existing (ASSERTED) |

## Coat and genetics

| Entity | Ontology class | Groups | Why (grounding) | Attested by | Status |
|---|---|---|---|---|---|
| `ont:blue-coat` | Organism | G2, G6 | PAA "How much does a blue Staffy puppy cost?", "Are blue staffies good pets?", "Is blue Staffy aggressive?". Each puppy's colour (blue, blue and white, white) is `data/puppies.json` `colour`, an attribute of this entity, not a separate one. LLM: the Royal Kennel Club "explicitly says health and temperament should take priority over colour", and the answer warns against "rare blue" and "exclusive blue". Name the colour plainly and never as rare. | COMP 5/5; `data/puppies.json` | existing (ASSERTED) |

No genetics entity is recommended. THR asks "Can a blue Staffy puppy come from parents that are not both blue?" and "Does it matter for a puppy's health if both parents are blue?", but QF marks `q-can-a-blue-staffy-puppy-come-from-parents-4e444c` `blocked: unverified fact`, no competitor domain writes "dilute", and no data file explains the colour's inheritance. A dilute-gene entity would be inferred (working rule 9). See "Excluded".

## Health

The tests are named; no result is stated. The breeder holds the parents' certificates and DNA results and shares them with a buyer on request, kept off the website (CERT, 2026-10-05, correcting answer board q01 of 2026-09-29). They are not on file in the repository, so LEDGER `parents-dna-clear` stays `NOT FETCHED — held by the breeder but not on file in the repository` and no page says "clear", a grade, a score or a pass. A health RESULT is never an entity here.

| Entity | Ontology class | Groups | Why (grounding) | Attested by | Status |
|---|---|---|---|---|---|
| `ont:l-2-hga-dna-test` | Health | G4 | LLM "l-2-hga" (medium): the Royal Kennel Club "recommends testing for HC-HSF4 hereditary cataracts and L-2-HGA". QF `q-what-does-l-2-hga-testing-mean-for-27d9f9`. keyword-variants co-occurring "l-2-hga" (df 6). LIB line 43. FU Q9. | COMP 1/5 (pets4homes); LLM; LIB | existing (PROPOSED) |
| `ont:hc-hsf4-dna-test` | Health | G4 | Same answer sentence as above. QF `q-which-genetic-tests-are-the-parents-clear-c94eed` (score 4) asks for a result: answer it by naming the test and the on-request certificates (LEDGER `certificates-on-request`). LIB line 44. FU Q9. | COMP 2/5 (pets4homes, freeads); LLM; LIB | existing (PROPOSED) |
| `ont:bva-kc-eye-scheme` | Health | G4 | LLM "eye testing", "litter eye screening" (both not on the page). QF `q-have-the-parents-had-eye-examinations-and-6c1484` (blocked: unverified fact). FU Q9: "eye screening for hereditary cataracts and other inherited eye diseases". Use the alias **eye screening**; the breeder did not name the BVA/KC scheme. | COMP eye 3/5; LLM; FU | existing (PROPOSED) |
| `ont:elbow-screening` | Health | G4 | LLM "elbow testing" (not on the page). FU Q9 "mention elbows as well". Screening only: LEDGER vocabulary `hip-elbow-score` forbids a score. | COMP 1/5 (staffie-owners); LLM; FU | existing (PROPOSED, `source: null`) |
| `ont:health-guarantee` | Health | G2, G4 | QF `q-do-you-offer-health-guarantees-for-your-b-04ef4b` (one of the three uncovered `extra_sections` health questions). Wording only from `data/settings.json` `guarantee_label` and `guarantee_cover`. | COMP 1/5 (puppies.co.uk, as a marketplace banner "Health guarantee"); `data/settings.json` | existing (ASSERTED) |

## Paperwork, registry and regulation

The paperwork is exactly `data/faq.json` `whyus-paperwork`: the Kennel Club registration paperwork, the vaccination records, the microchipping details and a written puppy purchase contract.

| Entity | Ontology class | Groups | Why (grounding) | Attested by | Status |
|---|---|---|---|---|---|
| `ont:vet-signed-health-card` **(Recommended)** | Documentation | G2, G4 | See "The one to build around". QF `q-what-comes-with-a-puppy-ccf7f1` "Has the puppy been microchipped and vet checked?" (score 4), `q-what-has-a-puppy-had-before-it-comes-46de43` (score 4), `q-do-your-puppy-come-with-vet-records-and-30768c`. Never "health certificate" or "vet checked" in our own sentence (LEDGER vocabulary `health-tested`, `vet-checked`); the ledger row's own wording clears it. | COMP microchip 4/5, vaccination 4/5, worming 3/5; LLM high; LEDGER `puppy-vet-signed-health-card` | existing (ASSERTED) |
| `ont:vaccination-record` | Documentation | G2, G4 | LLM "vaccinations" (**high**). QF `q-what-vaccinations-do-your-puppy-have-befo-cfc6a9`, THR `q-should-a-staffy-puppy-have-had-its-first-f0d071` (blocked). LIB line 47 (PDSA dog vaccines: the second dose and booster are the owner's own vet's). | COMP 4/5; `data/faq.json` | existing (ASSERTED) |
| `ont:dog-microchipping-law` | Regulation | G4 | LLM "microchip" (**high**). The microchipping details go home (`whyus-paperwork`). LIB lines 46 and 59. Named, with no compliance claim. | COMP microchip 4/5; LIB | existing (ASSERTED) |
| `ont:kc-registration-paperwork` | Documentation | G2 | LLM "kc registration" (medium), "kc records". PAA related "Blue staffy puppies manchester kennel club" and REG "Staffy puppies for sale manchester kennel club". keyword-variants co-occurring "kennel club" (df 5). | COMP KC reg 4/5; `data/faq.json` | existing (ASSERTED) |
| `ont:kc-registration-application-form` | Documentation | G2 | What actually goes home: LEDGER `parents-kc-registered-application-form` (the parents are registered; every puppy comes with its KC registration application form, answer board 2026-10-04 q06). This is the only wording in which "Kennel Club registered" may appear. QF `q-what-paperwork-comes-with-a-puppy-7f78f0` (score 4). | LEDGER | existing (ASSERTED) |
| `ont:puppy-purchase-contract` | Documentation | G1, G2 | LLM "Will you take the dog back or help rehome it if I can't keep it later?". QF `q-do-you-give-a-written-contract-and-a-f01711` and `q-should-the-purchase-contract-give-me-time-3991cc` (both blocked in QF; the take-back terms are FU Q6, and the own-vet-check window, "within 7 days", is breeder answer 7 in `docs/reference/answer-board/answers/2026-09-24-questions-for-lisa-bright-2026-09-27.md`). | `data/faq.json`; FU Q6 | existing (ASSERTED) |
| `ont:welfare-in-transport-pb10308` | Regulation | G3 | The rules DEFRA-approved transport works to. QF delivery questions `q-can-i-get-a-blue-staffy-puppy-delivered-ad16e3`, `q-can-you-deliver-a-blue-staffy-puppy-to-74fa14`, `q-do-you-deliver-across-the-uk-fb0c4a` (score 4 each). LIB line 55. | LIB | existing (ASSERTED) |
| `ont:dangerous-dogs-act-1991` | Regulation | G5, G6 | QF `q-is-the-staffy-a-banned-breed-in-the-954365`, `q-why-werent-staffy-banned-in-the-uk-9c6951`, `q-is-a-staffy-a-pitbull-e881f1`. LIB line 50: the breed is not on the banned list. | LIB | existing (ASSERTED) |

## Place and geography

The page's own geography is Manchester (where the buyer is) and Carlisle, Cumbria (where we are). Town and region only (Known Issue 16). Never a mileage or a drive time (`bsuk-entity-agent` rule 5).

| Entity | Ontology class | Groups | Why (grounding) | Attested by | Status |
|---|---|---|---|---|---|
| `ont:manchester` | Place | all | The primary keyword "blue staffy puppies manchester". GAP: Manchester is on 11/20 competitors (line 170), the second-highest city. The ontology row's `owner_page` is this page. | COMP 5/5; `data/locations.json` | existing (ASSERTED) |
| `ont:carlisle` | Place | G1, G3 | Viewing and collection happen in Carlisle (`data/settings.json` `address.city`). QF `q-can-i-visit-you-before-i-decide-4fc075`. The Manchester-to-Carlisle story needs both ends named. | `data/settings.json` | existing (ASSERTED) |
| `ont:cumbria` | Place | G3 | The breeder's region (`address.region`). | `data/settings.json` | existing (ASSERTED) |
| `ont:greater-manchester` | Place | G3, hero | The strategy row's keyword ends "…manchester greater manchester" (STRAT line 118). The county name is how the ranking listings place every Manchester advert ("Rochdale, Greater Manchester", "Stockport, Greater Manchester"). Bing ranks freeads and pets4homes URLs under `/greater-manchester/` (`serp_bing.json`). Not a city of `data/locations.json`. | COMP 2/5 (pets4homes, puppies.co.uk); STRAT; `serp_bing.json` | **PROPOSED (new)** — source `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md` line 118 |
| `ont:salford` | Place | G3 | PAA related search "Staffy puppies for sale near Salford" (also keyword-variants `related`). The rank-2 Google result is staffie-owners' Salford page ("…For Sale In Salford, Manchester"). | COMP 3/5 (staffie-owners, puppies.co.uk, freeads — "7 Beautiful Blue Staffies … Salford"); PAA; REG | **PROPOSED (new)** — source `data/queries/raw/blue-staffy-puppies-manchester-uk/serp_google.json` |

Held for the `bsuk-city-places` pass, not recommended yet: **Stockport** (COMP 4/5), **Wigan** (COMP 4/5), **Rochdale** (COMP 2/5), **Bolton** (the rank-7 organic title "Blue Staffordshire Bull Terrier Puppies For Sale In Bolton", COMP 1/5). The London page's places (Croydon, Edmonton, Ilford) entered the ontology through `data/city-places/blue-staffy-puppies-london.json`; Manchester has no city-places file yet, so these four wait for it rather than being proposed from listing text. Bolton also appears in the AI answer only as the town of a competitor business (Bonosue), which is not a reason to name it.

## Process

| Entity | Ontology class | Groups | Why (grounding) | Attested by | Status |
|---|---|---|---|---|---|
| `ont:video-call-before-deposit` | Commerce | G1, G3 | The answer to the AI answer's "Don't agree to meet in a car park or have the puppy delivered to you": a Manchester buyer who takes delivery still sees the puppy with its mother on a live video call before any deposit (answer board 2026-09-29). THR "Is it safe to pay a deposit to a seller I found through an online advert?" (QF `q-is-it-safe-to-pay-a-deposit-to-6c495b`, blocked) and QF `q-should-i-pay-a-deposit-before-i-have-c724f9` (blocked). | ontology source file; COMP video 2/5 (gumtree, freeads) | existing (ASSERTED) |
| `ont:refundable-deposit` | Commerce | G1, G2 | QF `q-how-much-is-the-deposit-2cce23`, `q-how-do-i-reserve-one-of-your-blue-309feb`. LLM "Can I see the puppy's paperwork before paying a deposit?". Wording only through `depositLine` and `data/settings.json` `deposit_refund_clause` ("up to 70% refundable if you change your mind up to 1 day before collection or delivery"); never a plain "refundable" (see flag 1). | COMP 3/5 (puppies.co.uk, staffie-owners, freeads); `data/settings.json` | existing (ASSERTED) |
| `ont:defra-approved-transport` | Logistics | G3 | The three score-4 delivery questions (above). Band from `delivery_min_gbp` / `delivery_max_gbp`, never typed. | COMP deliver 2/5; `data/settings.json` | existing (ASSERTED) |
| `ont:home-raised-litter` | Method | G4 | QF `q-are-the-puppy-raised-in-a-family-home-c93ef5`. LLM "How have the puppies been socialised? … children, household noises, handling, other dogs and being left alone". LEDGER `litters-home-raised-never-kennels`. | COMP 2/5 (staffie-owners, freeads); LEDGER | existing (ASSERTED) |
| `ont:puppy-culture` | Method | G4 | LLM "socialisation" (medium, not on the page); PDSA "recommends asking breeders about early socialisation" in the answer. QF `q-what-socialisation-has-the-puppy-had-06a259` (blocked). FU Q16 "both". | COMP socialis 3/5; FU | existing (ASSERTED) |
| `ont:early-neurological-stimulation` | Method | G4 | Same grounding (FU Q16, "both"). | FU | existing (ASSERTED) |
| `ont:after-collection-support` | Commerce | G4, G6 | QF `q-do-you-offer-support-after-i-take-my-d4ebe8` (score 4, found in the AI answer and the bank). LEDGER `breeder-support-after-collection`. | LEDGER | existing (ASSERTED) |

## Organisation (and the breeder)

| Entity | Ontology class | Groups | Why (grounding) | Attested by | Status |
|---|---|---|---|---|---|
| `ont:lisa-bright` | People | G1, G4 | GAP schema gaps: `Person` is on 5/20 competitors and missing from BSUK (line 202). LLM: BSUK is not cited and `citation_gap` lists `trojanstaffuk` and `ukstaffypups`; the page needs a named breeder behind the viewing, the video call and the raising. | `data/settings.json` | existing (ASSERTED) |
| `ont:the-kennel-club` | Organization | G2, G4 | LLM `citations[]`: royalkennelclub.com is the first cited domain, and the answer cites it for the puppy-finder, the health tests and colour against health. STRAT line 108: link out to the Royal Kennel Club. Alias "Royal Kennel Club" is already on the row. LIB lines 40, 43, 44, 51. Name the organisation only; no Assured Breeder claim. | COMP "kennel club" 4/5; LLM | existing (ASSERTED) |
| `ont:pdsa` | Organization | G4, G5 | LLM `citations[]`: pdsa.org.uk (early socialisation). STRAT line 108: link out to the PDSA. LIB lines 47 (vaccines), 49 (breed page), 56 (exercise). QF exercise questions `q-how-much-exercise-does-a-staffy-need-dail-0d2427` / `…-each-bd9421`. | LLM; LIB | existing (ASSERTED) |
| `ont:rspca` | Organization | G1 | THR "How can I tell whether a puppy advert on a UK classifieds site is genuine?" (QF `q-how-can-i-tell-whether-a-puppy-advert-20b0e5`, blocked). QF `q-how-do-i-tell-an-ethical-breeder-from-414f97` "How do I spot a bad Staffy breeder?" (score 4). LIB line 52. Every page in `data/queries/raw/blue-staffy-puppies-manchester-uk/competitors.json` is a classifieds or listing page. | LIB | existing (ASSERTED) |
| `ont:paag` | Organization | G1 | The same two online-advert questions; LIB line 66. | LIB | existing (ASSERTED) |
| `ont:dogs-trust` | Organization | G5 | QF `q-can-staffy-be-left-alone-for-8-hours-858e97` (score 4, PAA), `q-can-a-staffy-live-in-a-flat-310055`, `q-do-staffy-get-along-with-children-and-oth-e9aa5f`. LIB line 65. | LIB | existing (ASSERTED) |
| `ont:blue-cross` | Organization | G4 | LLM "socialisation" (not on the page). LIB line 53. | LIB | existing (ASSERTED) |
| `ont:bva` | Organization | G4 | LIB line 45 (the eye scheme). Never within 20 characters of "hip", "elbow" or "score" (LEDGER vocabulary `hip-elbow-score`). Optional; the eye entity can stand without it. | LIB | existing (ASSERTED) |
| `ont:rcvs` | Organization | G4, G6 | Thread question QF `q-how-can-i-confirm-that-a-puppy-has-661d01` "How can I confirm that a puppy has been examined by a vet?" (blocked) and the contract's own-vet check. LIB line 75 (Find a Vet: a Manchester buyer finds a registered vet near them). Optional. | LIB | existing (ASSERTED) |
| `ont:uk-government` | Organization | G4, G5 | The publisher behind `ont:dog-microchipping-law` (LIB line 46) and `ont:dangerous-dogs-act-1991` (LIB line 50). | LIB | existing (ASSERTED) |

## Per section group (Move 2)

| Group | Recommended entities | Why, in one line |
|---|---|---|
| G1 deposit and viewing | `ont:video-call-before-deposit`, `ont:maggie`, `ont:refundable-deposit`, `ont:carlisle`, `ont:lisa-bright`, `ont:rspca`, `ont:paag` | The AI answer's first instruction is "see the puppy with its mother where it was raised", and the fear questions ask about money before seeing (QF `q-how-can-i-avoid-buying-from-a-puppy-5e9d7e`, score 5; `q-should-i-pay-a-deposit-before-i-have-c724f9`, score 4); the video call and a Carlisle viewing answer both, from a named breeder. |
| G2 litter and prices | `ont:blue-coat`, `ont:maggie`, `ont:jones`, `ont:kc-registration-application-form`, `ont:kc-registration-paperwork`, `ont:puppy-purchase-contract`, `ont:health-guarantee`, `ont:the-kennel-club` | PAA's first question is the blue puppy's price, and the "kennel club" related searches on both SERPs ask what registration a Manchester buyer gets; prices come from `data/price-matrix.json`. |
| G3 delivery to Greater Manchester | `ont:manchester`, `ont:greater-manchester` (PROPOSED), `ont:salford` (PROPOSED), `ont:carlisle`, `ont:cumbria`, `ont:defra-approved-transport`, `ont:welfare-in-transport-pb10308`, `ont:video-call-before-deposit` | Three score-4 delivery questions and the Salford related search; the AI answer's "don't have the puppy delivered" is answered by pairing delivery with the pre-deposit video call. |
| G4 health and raising | `ont:vet-signed-health-card` (Recommended), `ont:vaccination-record`, `ont:dog-microchipping-law`, `ont:l-2-hga-dna-test`, `ont:hc-hsf4-dna-test`, `ont:bva-kc-eye-scheme` (as eye screening), `ont:elbow-screening`, `ont:home-raised-litter`, `ont:puppy-culture`, `ont:early-neurological-stimulation`, `ont:after-collection-support`, `ont:the-kennel-club`, `ont:pdsa`, `ont:blue-cross` | Microchip and vaccinations are the AI answer's only high-band gaps and STRAT's named checks; the tests are named with the on-request certificates and no result; the raising answers the answer's socialisation question. |
| G5 life in Manchester | `ont:staffordshire-bull-terrier`, `ont:manchester`, `ont:pdsa`, `ont:dogs-trust`, `ont:dangerous-dogs-act-1991`, `ont:uk-government` | The PAA life questions (left alone for hours, good pets, aggressive) and the banned-breed questions, answered from independent sources rather than from us. |
| G6 FAQ | `ont:staffordshire-bull-terrier`, `ont:american-staffordshire-terrier`, `ont:blue-coat`, `ont:dangerous-dogs-act-1991`, `ont:after-collection-support`, `ont:rcvs` | The breed-identity questions (AmStaff, pit bull, lifespan) and the leftover must-answer questions the body groups do not carry. |

## Excluded, with reason

| Candidate | Why it is not recommended |
|---|---|
| LLM "licence" (the AI answer lists a "licenced breeder" business) · `ont:animal-licensing-regulations-2018` · `ont:cumberland-council` | The user's ruling of 2026-09-27 (FU Q19–21): no licence number, no council, no licence claim and no licensing link on the site. COMP "licen" is on 3/5 domains as sellers' wording; the page still carries none (`LICENCE_CLAIM_PLACEHOLDER` only). |
| LLM "certificates", "dna clear", "health tested" as our claim | No result is stated (LEDGER `parents-dna-clear`: NOT FETCHED — certificates held by the breeder, not on file in the repository; CERT). "Health tested" is LEDGER vocabulary `health-tested`; COMP has it on 4/5 domains as advert wording, and our page uses it only inside a buyer's question. |
| LLM "inbreeding coefficient" · QF `q-what-is-the-parents-coefficient-of-inbree-131772` | No coefficient is held in any data file; stating one would be invented. |
| `ont:bva-hip-elbow-scores` | A score needs a ledger proof; FU Q9 allows elbow screening only. |
| `ont:phpv-test` | Not in the breeder's Q9 list. |
| A dilute-gene / colour-genetics entity | Not attested: no competitor domain writes "dilute", QF blocks the colour-inheritance question, and no data file explains it. |
| LLM "rare blue", "exclusive blue", "high prices"; COMP "rare" (2/5), "merle" (4/5), "bully" (4/5) | Marketing terms the AI answer warns against, or colours and types we do not breed (`data/puppies.json` holds blue, blue and white, and white). |
| LLM "idcbullz manchester", "bonosue", "smethwick", "puppy finder" | Competitor businesses, a competitor litter's town and the registry's search tool. Naming them sends a Manchester buyer to someone else; `ont:the-kennel-club` covers the registry. |
| COMP "insurance" (3/5) | A marketplace's buyer perk ("Free Insurance To Buyers"), not something we offer; no data file mentions insurance. |
| `ont:pet-travel-rules-gb` | Those rules cover bringing a pet into Great Britain; Carlisle to Manchester is domestic. |
| Didsbury, and the 18 towns in the staffie-owners / puppies.co.uk town indexes | Didsbury is on one listing on one domain (gumtree). The index towns (Middleton, Stretford, Eccles, Sale, …) are attested only as entries in marketplace town lists; they are parked in `keyword-universe.json` as neighbourhood keywords and are not entities. |

## Flags for the controller

1. **Deposit entity name.** `ont:refundable-deposit` is still named "£500 refundable deposit". `data/settings.json` now carries `deposit_refund_clause` ("up to 70% refundable if you change your mind up to 1 day before collection or delivery") and its source says a page never renders `deposit_refundable` as a plain "refundable". The page wording comes from `depositLine`; renaming the row was not done here (out of scope for this task).
2. **Two new Place rows proposed:** `ont:greater-manchester` (source: the strategy file line 118) and `ont:salford` (source: `data/queries/raw/blue-staffy-puppies-manchester-uk/serp_google.json`). Neither was written to `data/bsuk-ontology.json`. Each carries a source, so an approved board would promote it to ASSERTED. If the controller prefers the London route, `bsuk-city-places` writes `data/city-places/blue-staffy-puppies-manchester-uk.json` first and the rows take it as their source; Stockport, Wigan, Rochdale and Bolton wait for that pass.
3. **"Ince" is a place name and a puppy.** The staffie-owners town index lists Ince-in-Makerfield ("Ince in Makerfield, Manchester"), and Ince is one of our puppies (`data/puppies.json`, male, £1,500 from `data/price-matrix.json`). The page never uses "Ince" as a place, so the puppy's name is never read as a town in G2 or G3.
4. **The AI answer argues against delivery.** It tells a Manchester buyer not to have the puppy delivered. G3 cannot ignore that: the delivery section has to carry the pre-deposit video call with the mother (and the option of viewing in Carlisle) in the same breath, or the page contradicts the answer engines it is trying to be cited by.
5. **`nlp_keywords.py` did not run.** It needs `data/boards/blue-staffy-puppies-manchester-uk.json`, which is built after STOP 2 (`docs/research/manchester-page-run/nlp-keywords.json` records the barrier and what the script reads). The COMP domain counts in this file are a word-boundary reading of the same cache, for this row only; re-run the script once the board exists.
