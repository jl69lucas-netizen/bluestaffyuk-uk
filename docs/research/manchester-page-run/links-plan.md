# Manchester links plan (page-run row 9, steps 4–5)

Date: 2026-10-07 · Page: `blue-staffy-puppies-manchester-uk` (`/uk-locations/blue-staffy-puppies-manchester-uk/`) · Plan: `docs/superpowers/plans/2026-10-07-manchester-page-run.md`, Task 15 (part 1), as London's Task 19 Step 1.
Agent: `bsuk-entity-incorporation-agent`, Moves 1, 2 and 4. The per-section `entities`, each with its why, are in `data/outlines/blue-staffy-puppies-manchester-uk.json`. Nothing else in the outline was changed. The external links are written by `bsuk-external-link-agent` (draft: `docs/research/manchester-page-run/external-links.md`). They go under the last heading of this file.

**Rules applied.** Every anchor opens its sentence (Link-First, `rules/links.md`). Every link has a typed anchor (`anchor-type-variation`). No anchor repeats on the page. No internal anchor is reused for the same route anywhere else: I checked all 14 records in `data/boards/` (the `_demo` fixture included), both outlines in `data/outlines/`, London's `links-plan.md` and the 201 in-copy anchors on the built pages in `dist/` (2026-10-07), folding case and punctuation the way `link_diversity.anchor_key` does. Internal links open in the same tab. Outside citations open in a new tab with `rel="noopener noreferrer"`. FAQ answers carry no `<a>`, because they feed `FAQPage` JSON-LD. The two FAQ pointers (links 11 and 23) are separate paragraphs outside the answer array.

**Rulings respected.**

- No live video call anywhere (STOP 1 q08), so `ont:video-call-before-deposit` is used in no section.
- No rescue or rehoming wording (q10). No council page and no licence (q07, `LICENCE_CLAIM_PLACEHOLDER`).
- Health tests are named, never given a result (ledger `parents-dna-clear`: no proof on file).
- The guarantee is worded only from `guarantee_label` / `guarantee_cover`. The deposit is never called plainly "refundable": the clause comes only from `deposit_refund_clause`.
- Colour and price are stated for this litter only (q09). No anchor adds "Manchester" (term ceilings, q12).
- No mileage, journey time or delivery date appears on the page. The distances below rank the nearby cities only.

## Move 1 — structural critique, section by section

- **§1 Hero (EEBP).** The H1 is a colour question (M1). On its own it has no breed, breeder or place, so the opener must name Lisa Bright, Carlisle, Cumbria and the Staffordshire Bull Terrier in full, or the for-sale family (q04) has nothing to stand on. "Manchester" alone would suggest the puppies are there, which is the pool's own failure (`universal_gaps[4]`). Greater Manchester is named as the area we deliver to, and Carlisle as where the puppies are. Delivery and the deposit stay generic until they are read from data: DEFRA-approved transport inside the band, and `deposit_gbp`.
- **§2–§5 Counter, trust strip, contents, takeaways.** All four are figures and labels read from data. The entity value is in what no pool page has: the delivery band, the guarantee and the trust signs. The risk is drift into ledger vocabulary ("vet checked", "KC registered", "health tested"). The trust items are read verbatim from `puppy_trust_signs`. Takeaway 4 names L-2-HGA and HC-HSF4 with the certificates on request, instead of "health tested".
- **§6, §11, §20 Reviews.** Only the review's own words appear. Each review's entity is the one its quote names: Manchester and home-raising (Victoria Family), the records (Mark J), and the home-raised environment (Rachel L.).
- **§7 FAQ top.** Each answer comes from its bank row only. The score-5 where-to-buy answer has to name Carlisle (bank `home-find-breeders`), and delivery answers three of the six picks.
- **§8 G1 Deposit and viewing (PDB).**
  - The fear, paying a stranger found online, was named, but the section had no outside authority and no named people. The RSPCA's buying advice (the external set's §8 link) and Maggie, Jones and Lisa Bright make the visit concrete.
  - "Deposit" is generic until its terms come from data: `deposit_gbp`, `deposit_refund_clause` for the H5 and H6, payment by bank transfer, and the deposit coming off the price.
  - With no video call (q08), the only "see the mother" moment is the visit in Carlisle, which the deposit books. The copy never takes the RSPCA's or the AI answer's "see before you pay" line as ours (lessons 9; breeder FU Q3/Q5, "viewing stays deposit-first").
  - H6 asks about our vet. The RCVS register is where a buyer checks that a vet is registered. We name no practice.
- **§9 G4 Health and raising (EEBP).**
  - "Health tested" is the generic term. The section names L-2-HGA, HC-HSF4, eye screening and elbow screening as tests and screening, never as results.
  - The H4 carries the BVA eye-scheme link and the H6 the Kennel Club breed page (external set). Neither may imply that our parents were examined under the scheme, or that their results can be looked up.
  - The raising H3 needs its method entities (Puppy Culture, ENS) and the ledgered home-raising, or it reads as a promise.
- **§10 G2 Litter and prices (FAB).**
  - A bare price is the pool's own failure. The section names what the price carries (the application form, and the guarantee by its label) and the parents behind the litter.
  - "Kennel Club" is a keyword placed here. It attaches to the parents' registration (the one ledgered sentence) and to the puppy's application form, never to a registered puppy.
  - Each coat is named from data and never ranked or called rare. The H5 example (Byrd, White, at the boys' price) shows that the price follows the sex.
- **§12 FAQ middle.** Two picks are about tests (named, never a result). The answer to "see the mother before money changes hands" explains our deposit-first order and never repeats the bank row's "before any money moves" (the outline's open flag).
- **§13 G3 Delivery (FAB).**
  - "We deliver nationwide" is generic. DEFRA-approved transport, the band from data and the welfare-in-transport guidance make it specific. The guidance is named with no compliance claim.
  - The boroughs are named once, in the H3 (S2). Salford is the borough with a sourced entity. Stockport, Bolton and Wigan stay plain words (held for a city-places pass, entities.md).
  - The AI answer warns against delivery. With no video call, the answer is collection in Carlisle after the viewing, or delivery after it.
  - The nearby cities are the four nearest location pages plus the nearest indexed one (`bsuk-entity-agent` rule 5).
- **§14 Paperwork (FAB).**
  - The bank row's "Kennel Club registration paperwork" overstates. The section's entity is the application form (ledger), and the Kennel Club is the register the owner joins with it.
  - The vet-signed health card is the research's central entity and needs its own sentence here, with its own ledger pattern at build.
  - The contract is named, with no deposit timing attached to it (lessons 9).
- **§15 Health (EEBP).** "What are Staffies prone to" invites a list of diseases. The skin predispositions are the study's findings (external §15). The two inherited conditions jump to §9 and are not repeated. The guarantee is the only entity of ours in this section.
- **§16 Newsletter.** The breeder's sign-off only.
- **§17 G5 Life in Manchester (QAB).**
  - The banned-breed line is the riskiest sentence on the page. It names the Dangerous Dogs Act 1991 and the government's list, and says only "not on the list", never "legal".
  - Life answers are breed facts in a neutral register, with no named park, vet, business or city statistic. Manchester has no city-places file yet.
  - Dogs Trust is not used, because the library describes it as a rehoming charity (q10).
- **§18 Temperament (QAB).** The exercise figure is the PDSA's breed figure (external §18). Breed facts stay neutral, with no first-hand claim about our dogs as adults (lessons 10).
- **§19 Colour last (QAB).** The coat answer needs:
  - the registry: the standard lists blue and gives no rarity figure;
  - the AmStaff and pit-bull distinction, through the government's list;
  - the pedigree papers, meaning the parents' papers, not a registered puppy.

  There is no colour genetics, because the inheritance question is blocked.
- **§21 FAQ bottom.** Six breed-life answers. Their bank rows point to the breed guide, so the guide link sits in a pointer paragraph outside the array.
- **§22 Enquiry (AIDA, Action).** The breeder, the two routes (collection in Carlisle or delivery) and the Greater Manchester home. There is no phone while `PHONE_PLACEHOLDER` stands.

## Move 2 — entities per section (summary; the whys are in the outline rows)

The outline carries 117 entity references across 22 rows, using 41 distinct ontology ids. Each row marks exactly one entity (Recommended), first, with its trade-off.

| § | Section | Count | (Recommended) | Trade-off, short |
|---|---|---|---|---|
| 1 | Hero and opening | 9 | `ont:manchester` | Named as where the buyer is, never where the puppies are |
| 2 | Counter strip | 2 | `ont:defra-approved-transport` | A band priced by distance; no per-borough price |
| 3 | Trust strip | 6 | `ont:vet-signed-health-card` | Paperwork entity, no local pull; never "health certificate" |
| 4 | Contents | 2 | `ont:manchester` | Labels add no density and must respect the term ceiling |
| 5 | Key takeaways | 6 | `ont:refundable-deposit` | The refund clause in full or not at all |
| 6 | Review — top | 2 | `ont:manchester` | The review's own text only |
| 7 | FAQ top | 5 | `ont:defra-approved-transport` | No journey time, date or per-borough price |
| 8 | G1 Deposit and viewing | 9 | `ont:refundable-deposit` | The clause only; no video call stands in for the visit |
| 9 | G4 Health and raising | 11 | `ont:l-2-hga-dna-test` | Named as a test with certificates on request, never a result |
| 10 | G2 Litter and prices | 8 | `ont:blue-coat` | This litter only; never "rare" |
| 11 | Review — middle | 2 | `ont:vaccination-record` | London reviewer; his "health testing" stays his word |
| 12 | FAQ middle | 8 | `ont:l-2-hga-dna-test` | "Tested Clear" stays inside the question |
| 13 | G3 Delivery | 13 | `ont:defra-approved-transport` | No mileage, journey time, date or per-borough price |
| 14 | Paperwork | 7 | `ont:vet-signed-health-card` | Needs its own ledger pattern at build |
| 15 | Health | 4 | `ont:health-guarantee` | No length typed, no cover paraphrased |
| 16 | Newsletter | 1 | `ont:lisa-bright` | No density gain |
| 17 | G5 Life in Manchester | 5 | `ont:dangerous-dogs-act-1991` | "Not on the list", never "legal" |
| 18 | Temperament | 2 | `ont:staffordshire-bull-terrier` | Breed facts, no first-hand adult claims |
| 19 | Colour last | 6 | `ont:blue-coat` | No colour genetics; never "rare" or a premium |
| 20 | Review — bottom | 1 | `ont:home-raised-litter` | London reviewer; her "health checks" stays hers |
| 21 | FAQ bottom | 4 | `ont:staffordshire-bull-terrier` | Bank answers only; the guide link sits outside the array |
| 22 | Enquiry form | 4 | `ont:lisa-bright` | No phone, so the form is the only route |

**Ontology change.** I added two `Place` rows to `data/bsuk-ontology.json`. Both are **PROPOSED**, never ASSERTED, and both have a source, so an approved board promotes them through `board_approve.py`. `python3 scripts/ontology_seed.py --check` passes with 81 entities.

- `ont:greater-manchester`, source `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md`. Line 118 is the Manchester row, whose keyword ends "…manchester greater manchester". It is used in §1, §4, §13 and §22.
- `ont:salford`, source `data/queries/raw/blue-staffy-puppies-manchester-uk/serp_google.json`, which has the related search "Staffy puppies for sale near Salford". It is used in §13.

Neither row appears on London's board blocks (term-gap block checked), and `tests/py/test_ontology_seed.py`, `test_term_gap.py`, `test_term_density.py`, `test_nlp_keywords.py` and `test_board_entities.py` pass (127 tests).

**Excluded, with reason.**

| Entity | Reason |
|---|---|
| `ont:video-call-before-deposit` | STOP 1 q08 drops the video call. The research's video-call lines stay research. |
| `ont:paag` | The external agent found its homepage carries no substantive claim, so naming it would be a name-drop with nothing behind it. |
| `ont:dogs-trust` | The library row describes it as "a rehoming charity's own account of the breed" (q10). |
| `ont:blue-cross` | Its socialisation row fails plain curl (403), per the external agent, and §9 is already dense. |
| `ont:animal-licensing-regulations-2018`, `ont:cumberland-council` | No licence and no council (q07, `LICENCE_CLAIM_PLACEHOLDER`). |
| `ont:bva-hip-elbow-scores` | A score needs a ledger proof. |
| `ont:phpv-test` | Not in the breeder's Q9 list. |
| `ont:pet-travel-rules-gb` | Those rules cover bringing a pet into Great Britain. Carlisle to Manchester is domestic. |
| `ont:american-kennel-club` | No answer source on this page names it. |
| Stockport, Bolton, Wigan, Rochdale | Named as words in the §13 H3. Held for a `bsuk-city-places` pass (entities.md); no ontology row was invented from listing text. |

## Move 4 — schema notes

On this route, the shell already emits `LocalBusiness` (`@id` `…/#business`, with `PostalAddress`), `WebSite`, `BreadcrumbList` (Home › UK Locations › Manchester) and `WebPage`. I read this from `dist/uk-locations/blue-staffy-puppies-manchester-uk/index.html` on 2026-10-07. The page extends these and never duplicates a `@type`:

- **`areaServed`** goes on a node that reuses `@id` `…/#business`, as London's built page does, and names Greater Manchester (the outline's `areaServed`). It has no `telephone` key while `PHONE_PLACEHOLDER` stands.
- **`FAQPage`** is one node carrying exactly the 20 visible questions (6 + 7 + 7) in their page wording (`faq_rewordings`). Each answer comes from its bank row or data key. No answer string carries an `<a>`; the pointers (links 11 and 23) are separate paragraphs.
- **`Person`** is Lisa Bright, the byline (`how_we_win[5]`). The route has no Person node today. `WebPage.author` may reference it only if the node is defined on the page.
- **`Product`** appears only where STOP 3 places a puppy card, with one offer each and `InStock` only for a puppy whose status is Available. The §10 table on its own is not a card.
- **No `VideoObject`.** No `youtube_embeds` id is placed, and q08 drops the video call.
- **Verification:** run `npm run check:schema` on the built page at row 12, not on the source.

## Internal links

"Resolves today" means the built file exists in `dist/` (built 2026-10-07) and is listed in `data/page-map.json`. `/available-puppies/`, its puppy pages and the `/uk-locations/` hub are built from data and are not page-map rows. Robots values are as served today.

| # | Section | Target | Anchor text | anchor_type | Purpose | Resolves today |
|---|---|---|---|---|---|---|
| 1 | §1 Hero, opening sentence | `/` | Here at BlueStaffyUK | branded | Opens the signed EEBP opener (Entity): the kennel behind the litter, Lisa Bright in Carlisle, Cumbria, S2's one named breeder | yes: `dist/index.html`, index, page-map row |
| 2 | §1 Hero, Evidence | `/available-puppies/` | Available Blue Staffy puppies | exact (1 of 2) | The six named puppies of this litter, each with its price. This is the for-sale next step (q04), and the anchor is the target's own H1. | yes: `dist/available-puppies/`, index; built from `data/puppies.json` |
| 3 | §8 G1 · H3 "Which Questions Should a Staffy Breeder Answer Before Any Money Moves?" | `/uk-blue-staffy-puppy-buying-guide/` | The UK Blue Staffy puppy buying guide | exact (2 of 2) | The full question list lives on the guide. This H3 answers only what our own deposit-first order passes before the deposit: the puppy confirmed still free, the certificates on request, the guarantee terms (`guarantee_note`) and our vet (FU Q12). See flag 3. | yes, index, page-map row |
| 4 | §8 G1 · H4 "Can I Read Both Parents' Certificates Before I Reserve?" | `/uk-blue-staffy-breeders-contact/` | Ask us for both parents' certificates | natural | The certificates go to a buyer on request (ledger `certificates-on-request`; the breeder's chat ruling of 2026-10-05). No result is stated, and the sentence needs its own pattern on that ledger row at build. | yes, index, page-map row |
| 5 | §8 G1 · last line | `#enquiry` (§22, in-page) | Tell us which puppy you would like to visit | natural | Enquire call to action: the deposit books the visit, and the form is the next step | in-page: §22's form carries `id="enquiry"` at build |
| 6 | §9 G4 · H3 "Why Does an L-2-HGA Test on Both Parents Matter to My Puppy?" | `/blue-staffy-health-uk/` | How L-2-HGA and HC-HSF4 pass from parent to puppy | lsi | The internal source for health claims (FU Q9). The health page states that both conditions are recessive: "a puppy needs two copies to be affected, one from each parent". This is a breed fact, never a result. | yes, index, page-map row |
| 7 | §9 G4 · H3 "Where Does Each Blue Staffy Puppy Spend Its First Weeks in Our Carlisle Home?" | `/blue-staffy-uk-breeders/` | The home our puppies grow up in | natural | Backs "raised in our home, never in kennels" (ledger `litters-home-raised-never-kennels`) with the target's own sections, "Raised in Our Home, Not in A Kennel" and "Who the Puppies Meet Before They Leave". See flag 2. | yes, index, page-map row |
| 8 | §10 G2 · H3 "Why Do Our Blue Staffy Puppy Prices Follow the Sex, Not the Coat, in This Litter?" | `/blue-staffy-pup-sale-uk/` | Our Blue Staffy pup prices in full | partial | Backs the per-sex price sentence (`data/price-matrix.json`). The price page shows the same figures with the deposit and the band beside them. See flag 1. | yes, index, page-map row |
| 9 | §10 G2 · H4 "Who Are the Three Boys and Three Girls in This Litter?" (under the table) | `/buy-blue-staffy-puppies-uk/` | Our regularly updated listing | natural | Bank `listing-availability`: a puppy still showing on the listing is unreserved, and we confirm before you pay anything | yes, index, page-map row (see flag 1) |
| 10 | §10 G2 · H5 "Does a White or Part-White Coat Change the Figure?" | `/available-puppies/byrd/` | Byrd, our solid white boy | natural | The H5's worked example. Byrd's coat is White (`data/puppies.json`; his personality line opens "Our solid white boy"), and he costs the boys' price (`male_gbp`). Said of this litter only (q09). | yes: `dist/available-puppies/byrd/`, index. Re-pick at STOP 3 if Byrd's status changes. |
| 11 | §12 FAQ middle · pointer paragraph after the block | `/buy-staffy-puppies-for-sale-uk/` | How we compare with a classified puppy advert | lsi | Gives more depth for "How Do I Spot a Bad Staffy Breeder?" (bank `buying-puppy-farm`) through the target's own section, "How Does BlueStaffyUK Compare to Generic Classified Puppy Ads in the UK?". Every pool page is a classifieds feed (`universal_gaps[9]`). The pointer sits outside the FAQ array. | yes, index, page-map row (see flag 2) |
| 12 | §13 G3 · nearby line | `/uk-locations/staffy-puppies-for-sale-liverpool/` | Liverpool buyers | natural | The nearest location page (method below). The same band applies, priced by distance. | route exists (`dist/`, page-map). Noindex stub with an empty H1 and 5 words, **live once the stub is rebuilt** |
| 13 | §13 G3 · nearby line | `/uk-locations/blue-staffy-puppies-south-yorkshire/` | Our South Yorkshire page | natural | The second nearest | route exists. Noindex stub with an empty H1 and 0 words, **live once rebuilt** |
| 14 | §13 G3 · nearby line | `/uk-locations/blue-staffies-newcastle-under-lyme/` | Readers in Newcastle-under-Lyme | natural | The third nearest | route exists. Noindex stub, 5 words, **live once rebuilt** |
| 15 | §13 G3 · nearby line | `/uk-locations/blue-staffy-puppies-for-sale-leeds/` | Families in Leeds | natural | The fourth nearest | route exists. Noindex stub, 0 words, **live once rebuilt** |
| 16 | §13 G3 · nearby line | `/uk-locations/blue-staffy-puppies-york/` | York households | natural | The nearest location page indexed today. Nottingham is a hair nearer but is a 5-word noindex stub. | yes: index, 441 words, H1 "Blue Staffy Puppies For Sale in York, Yorkshire" |
| 17 | §13 G3 · nearby line | `/uk-locations/` | Every other UK city on our list | lsi | The hub, for any reader outside Greater Manchester | yes: `dist/uk-locations/`, index, H1 "Blue Staffy Puppies by UK Location" |
| 18 | §13 G3 · last line | `#enquiry` (§22, in-page) | Tell us whether you will collect or want delivery | natural | Enquire call to action. §22's note asks for collection in Carlisle or delivery. | in-page, as above |
| 19 | §15 Health · H2 answer | `#health-tests` (§9, in-page) | Both inherited conditions in the parents' screening | natural | Jump-link teaser. §15 names the two inherited conditions (bank `whyus-prone-to`), and §9 covers them in depth, so they are not repeated here. | in-page: the build sets `id="health-tests"` on §9's section, matching the ledger's `tests-named-no-result` anchor. The outline row has no `anchor` key, because this task wrote only `entities`. |
| 20 | §15 Health · H4 "Which Page of Ours Covers Staffy Skin in More Depth?" | `/blue-staffy-health-uk/` | Our Blue Staffy health page | partial | The H4's own answer. The health page covers skin and itching ("Itching hard enough to break the skin"; "The Skin Often Answers to the Bowl"), and bank rows `whyus-prone-to` and `listing-scratching` both say "Our health page covers…" | yes, index, page-map row |
| 21 | §17 G5 · H2 answer | `/blue-staffy-blog-guides/` | Choosing the right puppy for your household | lsi | Backs the household-fit answer with the hub's latest guide, "How To Choose The Right Blue Staffy Puppy For Your Family" | yes, index, page-map row |
| 22 | §18 Temperament · H3 "Are Boy Staffy Dogs More Boisterous Than Girls?", last line | `#enquiry` (§22, in-page) | Tell us whether you would like a boy or a girl | natural | Enquire call to action. §22's note asks for which puppy, or boy or girl. | in-page, as above |
| 23 | §21 FAQ bottom · pointer paragraph after the block | `/uk-staffordshire-bull-terrier-guide/` | Our Staffordshire Bull Terrier guide for UK owners | partial | Four bottom bank answers point to the breed guide (`listing-aggressive`, `listing-first-time-owners`, `listing-left-alone`, `listing-family-dog`). The pointer sits outside the FAQ array, so no `<a>` enters `acceptedAnswer.text`. See flag 4. | yes, index, page-map row |

**Mix.**

- **Totals:** 23 in-copy internal links: 19 to 18 distinct routes (the health page twice, links 6 and 20) and 4 in-page links (3 `#enquiry`, 1 `#health-tests`).
- **Types:** exact 2, partial 3, lsi 4, natural 13, branded 1. That is 5 types, at most two exact. There are no nav tiles in the table.
- **Repeats:** no anchor repeats on the page. I compared all 23 with the external agent's seven anchors in `external-links.md`, and none matches.
- **Reuse:** no anchor is reused for the same route on any board, any outline, London's plan or a built page. `scripts/link_diversity.py`'s vocabulary and folding were used for the check.
- **Wording:** no anchor matches a ledger vocabulary pattern or carries "Manchester", "video", "rescue" or "licence".
- **Build test:** at least 3 `href="#enquiry"` in the built body, as London's Task 26.
- **Nav furniture, not counted here:** the contents jump links (§4), the breadcrumb (`/` and `/uk-locations/`) and the form's privacy link (`/privacy-policy-uk/`, a form-component link) go on the board as nav tiles at STOP 3 (working rule 12).

**Nearby cities, by real proximity.** `data/locations.json` and the competitor cache hold no coordinates or distances for these cities. I computed great-circle distances from standard WGS84 city-centre coordinates (general reference, not a repo file). For a county row I used both of its main towns. The ranking only picks the links: no mileage goes on the page (`bsuk-location-page-builder`, UK geography).

| Rank | Location row | Distance used |
|---|---|---|
| 1 | Liverpool | 50.1 km |
| 2 | South Yorkshire | 51.3 km (Barnsley) / 52.5 km (Sheffield) |
| 3 | Newcastle-under-Lyme | 52.1 km |
| 4 | Leeds | 58.2 km |
| 5 | Nottingham | 93.0 km |
| 6 | York | 93.3 km |
| 7 | Wolverhampton | 99.6 km |
| 8 | Birmingham | 113.0 km |

The first four form a tight cluster, and then the distance jumps. York, sixth, is the fifth link because it is the nearest page indexed today. Nottingham, fifth, is a 5-word noindex stub, 0.3 km nearer. Wolverhampton, the brief's example, ranks seventh by distance and is a 3-word noindex stub, so it is not picked.

**Link-First openings (draft, for the writer; `{…}` is read from data at build).**

- §1: "<a>Here at BlueStaffyUK</a> we raise Staffordshire Bull Terrier puppies in our own home in Carlisle, Cumbria…"
- §1: "<a>Available Blue Staffy puppies</a> from this litter are listed one by one, each with its own price."
- §8 H3: "<a>The UK Blue Staffy puppy buying guide</a> sets out the questions in full; here are the answers you can have from us before you pay the deposit."
- §8 H4: "<a>Ask us for both parents' certificates</a> and we send them once you have written to us."
- §8 end: "<a>Tell us which puppy you would like to visit</a>, and we confirm it is still free before anything is paid."
- §9 H3: "<a>How L-2-HGA and HC-HSF4 pass from parent to puppy</a> is set out on our health page: both are recessive, so a puppy is affected only if it inherits the gene from each parent."
- §9 H3: "<a>The home our puppies grow up in</a> is our own, never a kennel, and our breeders page shows a day in the house."
- §10 H3: "<a>Our Blue Staffy pup prices in full</a> sit on one page, with the deposit and the delivery band beside them."
- §10 H4: "<a>Our regularly updated listing</a> shows every puppy nobody has reserved yet, and we confirm yours before you pay anything."
- §10 H5: "<a>Byrd, our solid white boy</a>, costs what his blue and blue-and-white brothers cost: in this litter the price follows the sex, never the coat."
- §12 pointer: "<a>How we compare with a classified puppy advert</a> is set out point by point on our why-choose-us page."
- §13 nearby: "<a>Liverpool buyers</a> have a page of their own, and the same delivery band applies." · "<a>Our South Yorkshire page</a> answers the same questions for that county." · "<a>Readers in Newcastle-under-Lyme</a> have their own page too." · "<a>Families in Leeds</a> have a page written for them." · "<a>York households</a> have one as well." · "<a>Every other UK city on our list</a> is on our locations page."
- §13 end: "<a>Tell us whether you will collect or want delivery</a> when you write, and we price the journey by distance."
- §15 H2: "<a>Both inherited conditions in the parents' screening</a> are covered above, test by test, with the certificates on request."
- §15 H4: "<a>Our Blue Staffy health page</a> covers Staffy skin in more depth, from itching to what the diet has to do with it."
- §17 H2: "<a>Choosing the right puppy for your household</a> is the subject of the latest guide on our blog."
- §18 end: "<a>Tell us whether you would like a boy or a girl</a>, and we will say which of this litter are still free."
- §21 pointer: "<a>Our Staffordshire Bull Terrier guide for UK owners</a> goes further on each of these: the law, time alone and the breed's family reputation."

## Open flags (for the controller; lessons 9 and 19)

1. **Viewing order on two sibling pages.** Links 8 and 9 land on pages that put meeting the puppy before the deposit:
   - `/buy-blue-staffy-puppies-uk/`: "Step Two: Meet Them First — A video call before the deposit, or a visit here by appointment to see the puppy with their mother", and "the deposit comes after you have met the puppy".
   - `/blue-staffy-pup-sale-uk/`: "You meet the litter first, here or on a video call we offer before the deposit".

   The breeder's FU Q3/Q5 (2026-09-27) says "viewing stays deposit-first", and Manchester's §8 is written that way. **One narrow question:** should the two siblings' viewing lines be corrected to deposit-first before Manchester's board (STOP 3), or should links 8 and 9 be held? Recommended: correct the siblings. The breeder's ruling is the fact, and a buyer who follows either link today reads a different order. Trade-off: two built pages are edited outside this run.
2. **"KC registered" puppies on two sibling pages.** These sit behind links 11 and 7:
   - `/buy-staffy-puppies-for-sale-uk/`: its H1 "…Trusted KC Registered Pedigree Dogs" and the H3 "The Paperwork That Travels With A KC-Registered Puppy";
   - `/blue-staffy-uk-breeders/`: the H2 "KC‑registered, Health‑checked Staffy Puppies Raised for Loving Family Homes".

   The ledger (`parents-kc-registered-application-form`) says a puppy goes home with its application form and is never called registered, which is what Manchester's §14 says.
3. **The buying guide's "Get the terms in writing before any money moves".** This sits behind link 3. Is the written contract given before the deposit? If it is not, the guide states a rule our own order does not follow. The guide also calls the deposit plainly "refundable".
4. **The breed guide's H3 "Legal to Own, Breed and Import in the UK".** This sits behind link 23. It goes further than the fact table's banned-breed line ("not on the government's list"). The outline already flags the bank rows (`guide-banned-breed`, `whyus-not-banned`), and the built page carries the same wording.
5. **§13 H6 "Where Does the Government Set Out Rules for Moving Animals?"** The external set does not link the PB10308 guidance, because it adds no domain (external-links.md, judgment 4). When the two files are merged, decide whether the H6 names the guidance in words or links its library row (`assets.publishing.service.gov.uk`, the same gov.uk domain).
6. **Ledger patterns at build.** `certificates-on-request` and `puppy-vet-signed-health-card` match London's exact sentences only. The Manchester sentences behind link 4 and §14's health card need their own patterns before `evidence_audit` passes.

## External links

Date: 2026-10-07 · Page: `blue-staffy-puppies-manchester-uk` · Plan: `docs/superpowers/plans/2026-10-07-manchester-page-run.md`, Task 15 (part 2), as London's Task 19 Step 2 · Agent: `bsuk-external-link-agent`, Protocol A.

Outline read: `data/outlines/blue-staffy-puppies-manchester-uk.json` (sections 8, 9, 15, 17, 18, 19). Every URL is an existing row in `docs/reference/external-link-library.md`, and **no library row was added**.

Rulings respected: no licensing page, no council page (STOP 1 q07, "(a) Yes, no local council link"), and no rescue-centre page (q10, "(a) Keep rescue wording off the page"). Dogs Trust's breed page was left out because Dogs Trust is a rehoming charity. There are no competitors and no marketplaces. Health tests are named and no result is ever stated (ledger `parents-dna-clear`). The licence stays `LICENCE_CLAIM_PLACEHOLDER` whatever the page linked beside it says.

## The set

**Result: 6 links (six distinct URLs, one of them cited in two sections), 6 domains, 5 source types.** The domains are rspca.org.uk, bva.co.uk, royalkennelclub.com, nih.gov, gov.uk and pdsa.org.uk. The source types are welfare, vet-charity ×2, registry, research and gov. I checked these counts on 2026-10-07 by running `link_diversity.external_summary()` on a mock board of these hrefs. It returned `links: 6`, six domains and five types.

| Section | URL | Domain | Source type | Anchor text | anchor_type | Claim it supports | Live check (date · code) |
|---|---|---|---|---|---|---|---|
| 8 G1 Deposit and viewing · H3 "What Will I See When I Visit a Staffy Breeder's Home in Carlisle?" | https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy | rspca.org.uk | welfare | Advice on buying a puppy from a breeder | natural | The RSPCA's own line under "Buying a puppy from a breeder": "Always make sure you see mum and her pups together, and never buy a puppy if you have doubts about the breeder or situation." The next sentence is ours, not the RSPCA's: at the visit you meet Maggie with the litter before you commit (H4). The copy never says the RSPCA endorses our deposit-before-visit order. | 2026-10-07 · 200 (`curl -sIL`, and GET 200) |
| 9 G4 Health and raising · H4 "Which Eye and Elbow Screening Sits Beside the DNA Tests?" | https://www.bva.co.uk/canine-health-schemes/eye-scheme/ | bva.co.uk | vet-charity | Hereditary eye disease screening by veterinary ophthalmologists | lsi | General statement about eye screening only: the scheme's panel of expert veterinary ophthalmologists carries out clinical eye examinations to find inherited and non-inherited eye conditions, which a DNA test does not cover. **Copy note:** the copy never says or implies that Maggie or Jones were examined under this scheme or hold a CHS certificate. The breeder named eye screening, not the scheme. | 2026-10-07 · **HEAD 404, GET 200**: `curl -sIL` returns 404 because the server answers HEAD requests with 404. `curl -sL` (GET, with or without a browser user agent) returns 200 at the same URL with the title "BVA - Hereditary Eye Disease Scheme for dogs" |
| 9 G4 Health and raising · H6 "Where Does the Kennel Club Explain These Health Schemes?" | https://www.royalkennelclub.com/search/breeds-a-to-z/breeds/terrier/staffordshire-bull-terrier/ | royalkennelclub.com | registry | The breed's pre-breeding health screening list | lsi | The Kennel Club's breed page, under "Pre-breeding Health Screening", lists the DNA test for hereditary cataracts (HC-HSF4), the DNA test for L-2-HGA, elbow testing under the BVA/KC Elbow Dysplasia Scheme and eye testing under the BVA/KC/ISDS Eye Scheme. These are the schemes this section names. **Copy note:** the page also points to the Health Test Results Finder, and the copy must not imply our parents' results can be looked up there. Certificates are shared on request, and no result is stated. | 2026-10-07 · 200 (`curl -sIL`, and GET 200) |
| 15 Health (extra) · H3 "Why Do Staffy Dogs Itch, and When Is It Time for the Vet?" | https://pmc.ncbi.nlm.nih.gov/articles/PMC7510130/ | nih.gov (pmc.ncbi.nlm.nih.gov) | research | Veterinary research on what Staffies are prone to | partial | Pegram et al. 2020 (VetCompass records): compared with other breeds, Staffordshire Bull Terriers had higher odds of atopic dermatitis (OR 1.88) and skin mass (OR 1.80), and of skin disorder at the grouped level. The study also says it found "no evidence that Staffordshire Bull Terriers have higher overall health problems". These are the study's findings, never our dogs' results. | 2026-10-07 · 200 (`curl -sIL`, and GET 200) |
| 17 G5 Life in Manchester · H3 "What Does the Banned-Breed Line Mean for Staffy Dogs in a Rented Manchester Home?" | https://www.gov.uk/control-dog-public/banned-dogs | gov.uk | gov | The dog types it is against the law to own in the UK | natural | The government lists the banned types as Pit Bull Terrier, Japanese Tosa, Dogo Argentino, Fila Brasileiro and XL Bully. The Staffordshire Bull Terrier is not on the list. **Copy note:** the page also says a banned type is judged by what a dog looks like, not its breed or name. So the copy never says "legal" or "cannot be seized" (outline row 17). | 2026-10-07 · 200 (`curl -sIL`, and GET 200) |
| 18 Temperament (extra) · H4 "How Long Should a Grown Staffy's Daily Walks and Play Last?" | https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/puppies-dogs/medium-dogs/staffordshire-bull-terrier | pdsa.org.uk | vet-charity | Staffordshire Bull Terrier exercise and care advice | partial | The PDSA's breed key facts give a minimum of 1 hour of exercise a day. The page also says Staffies are "very people-orientated", "love the company of their owners and prefer to have someone around all day", and can be "boisterous well into their adult years". This is a breed figure, never a first-hand claim (lessons 10). | 2026-10-07 · 200 (`curl -sIL`, and GET 200) |
| 19 Colour last · H2 "Are Blue Staffies Rare, and Why Should the Coat Be the Last Thing You Choose?" | https://www.royalkennelclub.com/search/breeds-a-to-z/breeds/terrier/staffordshire-bull-terrier/ | royalkennelclub.com (same URL as row 9 H6; counts once) | registry | The Kennel Club's Staffordshire Bull Terrier page | branded | The M1 angle's line, read at source on 2026-10-07: "Colour is only one consideration when picking a breed or individual dog, health and temperament should always be a priority over colour." Blue and Blue & White are among the breed-standard colours listed. The page gives no rarity figure, so the copy gives none. | 2026-10-07 · 200 (same check as row 9 H6) |

External anchor types: natural ×2, lsi ×2, partial ×2 and branded ×1, so **four types** (at least three are required). No anchor repeats on the page. None matches an anchor on any board in `data/boards/` (grepped 2026-10-07), and none matches London's six. I could not check them against Manchester's internal anchors, because `links-plan.md` is being written in parallel. Check both lists together when they are merged.

## Link-First openings (draft, for the writer)

Every anchor opens its sentence:

- §8: "<a>Advice on buying a puppy from a breeder</a> from the RSPCA is to always see the mother and her puppies together…"
- §9 H4: "<a>Hereditary eye disease screening by veterinary ophthalmologists</a> looks for eye conditions a DNA test cannot…"
- §9 H6: "<a>The breed's pre-breeding health screening list</a>, kept by the Kennel Club, names the two DNA tests, elbow testing and eye testing…"
- §15: "<a>Veterinary research on what Staffies are prone to</a>, drawn from UK vet practice records, found higher odds of atopic dermatitis and skin masses…"
- §17: "<a>The dog types it is against the law to own in the UK</a> are listed by the government, and the Staffordshire Bull Terrier is not one of them…"
- §18: "<a>Staffordshire Bull Terrier exercise and care advice</a> from the PDSA puts the minimum at an hour a day…"
- §19: "<a>The Kennel Club's Staffordshire Bull Terrier page</a> says health and temperament should always come before colour…"

Each link has `target="_blank" rel="noopener noreferrer"` and no `nofollow`. FAQ answers (rows 7, 12, 21) carry no `<a>`.

## Overlap with London

London's six (`docs/research/london-page-run/links-plan.md`) were RSPCA puppy-sales, the BVA eye scheme, PDSA exercise, the RKC breed standard, gov.uk banned-dogs and the VetCompass study. Three of Manchester's six target URLs are different: RSPCA `/dogs/puppy`, the RKC breed page and the PDSA breed page. Three are the same, because the library holds only one row for each of those claims: the BVA eye scheme, gov.uk banned-dogs and the PMC study. All of Manchester's anchors are different from London's.

## Judgment calls

1. **Two links in section 9 (230 words).** The H6 heading asks where the Kennel Club explains the schemes, and the outline marks that H6 as a citation, so the Kennel Club page has to sit there. A sixth domain also has to come from somewhere, and the BVA eye scheme is the only library row that fits a section without a link. The two links are in different paragraphs (H4 and H6), which meets "one per paragraph". Two links in a 230-word section is within "never more than two per 300 words" as I read it. If the cap is read pro rata (about 1.5 links for 230 words), the fallback is to drop BVA and add a sixth domain from a new library row (Protocol D). Moving BVA to another section is not an option either, because no other section makes an eye-screening claim.
2. **BVA HEAD 404.** The site answers HEAD with 404 and GET with 200, so the page is live. The brief's `curl -sIL` command records 404 for it today, and London's board cites the same row. The library row needs no change. Protocol C should use a GET check, or it will report a false dead row.
3. **One URL in two sections.** The RKC breed page stands behind both §9 H6 (the screening list) and §19 (colour). Each use has its own anchor, and the URL counts once toward the six. The more specific L-2-HGA DNA-test row was considered for §9 H6, but it covers only one of the four schemes the H6 refers to.
4. **Rejected rows:** Dogs Trust (rehoming charity, q10). PAAG (its homepage has no substantive claim, only navigation and FAQ titles). Blue Cross socialisation (plain curl 403; it would also have been a second link in §17). The gov.uk licensing, find-local-council and buying-a-cat-or-dog rows, the Cumberland rows and legislation.gov.uk (q07). The transport PDF, because `link_diversity` aliases `service.gov.uk` to gov.uk so it adds no domain.
