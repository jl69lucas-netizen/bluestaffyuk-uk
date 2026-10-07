# Manchester frameworks per section group (page-run row 8)

Date: 2026-10-07 · Page: `blue-staffy-puppies-manchester-uk` (`/uk-locations/blue-staffy-puppies-manchester-uk/`) · Agent: `bsuk-content-architect` (tier_high: a framework pick per section group for one page; no agent dispatched) · Plan: `docs/superpowers/plans/2026-10-07-manchester-page-run.md`, Task 10 step 3.

These are options for STOP 1. The user picks one framework per group on the research board, and nothing here is decided until those picks are recorded. Every choice below is argued from Manchester's own research. London's approved table was read for its shape only. Where a pick matches the framework London took, the reason given is Manchester's evidence. Where Manchester's evidence points somewhere else, the pick differs.

## Sources

Cited below by the short name on the left.

- **SERP**: `docs/research/manchester-page-run/serp-findings.md`. The eight pool pages: Google banked and Bing read on 2026-09-23, with the Freeads page captured on 2026-10-07.
- **FAN**: `docs/research/manchester-page-run/fanout.md`. PAA, related searches, threads, the search-result excerpts and the intent split.
- **ENT**: `docs/research/manchester-page-run/entities.md`. Move 2 per section group.
- **KU**: `docs/research/manchester-page-run/keyword-universe.json`. 200 rows, placements proposed.
- **AIO**: `docs/research/manchester-page-run/ai-overview.md`. The live Google read of 2026-10-07, which showed no AI Overview in that session.
- **KWS**: `docs/research/manchester-page-run/free-keyword-signals.md`. Autocomplete, Trends, Keyword Planner ranges and authority, read 2026-10-07.
- **QF**: `data/queries/blue-staffy-puppies-manchester-uk.json`, the question file (106 entries). Every count from it below was made by script.
- **LLM**: `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-10-07.json`. The answer text is in `data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.response.json`. ChatGPT was asked "Where can I buy a blue Staffy puppy near Manchester, and what should I ask the breeder?", and BSUK is not cited.
- **LEDGER**: `data/quality/evidence-ledger.json`.
- **LIB**: `docs/reference/external-link-library.md`, with the row's line number given.
- **STRAT**: `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md`. The Manchester build note is line 108 and the Manchester row is line 118.
- **PLAN**: the Manchester plan's "Rulings that bind every task". These carry over London's rulings 1 and 3–11 (`docs/superpowers/plans/2026-09-30-london-page-run.md`).
- **Breeder answers**: q03 (live video call on request before paying) and q04 (bank transfer) are in `docs/reference/answer-board/answers/2026-09-29-lisa-bright-five-facts-before-the-london-page-2026-09-29.md`. The certificates ruling is `docs/reference/answer-board/answers/chat-2026-10-05-certificates-on-request.md`.
- **Data**: `data/settings.json`, `data/puppies.json`, `data/price-matrix.json`, `data/faq.json`, `data/reviews.json` and `src/lib/cityKit.ts` (`depositLine`).
- **Gate code**: `scripts/outline_matrix.py`, `schemas/board.schema.json`, `scripts/family_rules.py`, `scripts/keyword_variants.py` and `scripts/evidence_audit.py`.
- **Builder**: `.claude/skills/bsuk-location-page-builder/SKILL.md`.

London's outline (`data/outlines/blue-staffy-puppies-london.json`) is cited in the header-style section, as evidence of what our own gates asked of the last city page's headings. It is not used as a template.

## Reader profile

- **Intent:** transactional. That is the primary keyword's intent in KU, and FAN §4 finds the live top eight organic results are all marketplace or classifieds pages.
- **Stage:** decision, with a consideration strand: price first, then suitability (the PAA), and for some buyers rescue or breeder (FAN §4).
- **Fear #1:** sending a deposit to a seller found online and never hearing back, or buying a farmed puppy.
  - QF scores "Should I see the puppy with its mother before any money changes hands?" 5.
  - The r/manchester search-result excerpts say "Avoid the puppy farmers on Gumtree." The scam-alert excerpt says "take your payment online and you never hear from them again" (FAN §3; these are language only).
- **Fear #2:** the parents' health. "Are the parents of your blue Staffy puppies health-tested?" scores 6, the top score in the file (QF).
- **Fear #3:** the puppy is not in Manchester, so the buyer asks how it gets there and whether a delivered puppy is safe.
  - The ChatGPT answer says "Don't agree to meet in a car park or have the puppy delivered to you" (LLM).
  - Three delivery questions score 4 (QF).
  - The breed's reputation sits underneath this fear: PAA asks "Is blue Staffy aggressive?", and an r/manchester thread title reads "So many XL bullies have made me scared of running in MCR" (FAN excerpt 7).
- **Desire:** a blue Staffy puppy from one named breeder, priced on the page, brought to their part of Greater Manchester or collected.
- **Objection:** sending £500 (`data/settings.json` `deposit_gbp`) to a breeder in Carlisle they have not met. The puppy is priced well above page-one listing ranges that start at £50–£75 (AIO).
- **Convert when** they know four things:
  - they have seen the puppy and Maggie on a live video call before any deposit (q03);
  - what the deposit does and when part of it comes back (`depositLine`; `data/settings.json` `deposit_refund_clause`);
  - how the puppy reaches Greater Manchester and for how much, or that they can collect in Carlisle (`data/settings.json`);
  - which papers and certificates they will see before committing (`data/faq.json` `whyus-paperwork`; LEDGER `certificates-on-request`).
- **Cluster role** (STRAT line 118): a city spoke under `/uk-locations/`, linking to the listing and the buying guide. The links themselves are the page board's (working rule 12).

## The names on offer

A group's pick is checked twice later on.

- **STOP 2:** `scripts/outline_matrix.py` accepts either a research-board pick (a group's `recommended`) or a `.claude/skills/framework-*` skill name. It refuses "—" on any row whose tree holds an H2.
- **STOP 3:** the page-board schema checks the section `framework` field against its enum: EEBP, FAB, QAB, PAS, BAB, PDB, AIDA, EBD and HSS (`schemas/board.schema.json`).

Every option offered below is one of the seven names that pass both gates whichever option the user picks: **AIDA, BAB, EEBP, FAB, PAS, PDB, QAB**. The other names in the brief are left out as group options, for these reasons:

| Name | STOP 2 (outline) | STOP 3 (page board) | Why it is not a group option |
|---|---|---|---|
| EBP (Evidence → Baseline → Profile) | passes (framework-ebp) | refused | EEBP passes both gates and carries the named-evidence job in the hero and health groups. |
| AIO-GEO | passes (framework-aio-geo) | refused | It is a page-wide layer, not a section shape. Answer-first openers (the header ruling below), FAQPage JSON-LD and tables apply in every group. |
| EEAT | passes (framework-eeat) | refused | It is an audit lens for the whole page, not a section shape. |
| H-S-S (Hook, Story, Solution) | only as a group's recorded pick | passes (HSS) | It is defined only in agent files (`bsuk-about-builder`, `bsuk-seo-content-writer`). Its Story beat needs first-hand material Manchester's research does not hold: a first-hand claim needs a saved answer or a data row (lessons 10), and the one Manchester review may not be quoted inside a body section (builder, Reviews). |
| EBD | only as a group's recorded pick | passes | It has no skill and no written expansion anywhere in the repo. |
| Entity-Tree | only as a group's recorded pick | refused | `.claude/agents/bsuk-content-architect.md` routes location pages to Entity-Tree + QAB, with BAB second (line 67). Entity-Tree cannot be a section's framework on a page board. Its job is done by EEBP's Entity move and by the entity loop every section runs anyway (`rules/copy.md` `entity-4-move-loop`; ENT per group). QAB and BAB are offered below where they fit. |
| Inverse Pyramid | only as a group's recorded pick | refused | It is already in every section. The user's header ruling answers each heading first, and QAB's Answer step is an inverse pyramid by definition. |

## Header style

**The register is already settled.** The user ruled: "All headers must be FAQ STYLE QUESTION AND ANSWER FORMAT and must also have a conversational opening paragraph reinforcing the core message of the header." The source is answer board batch `2026-09-26-project-5-decisions-before-the-first-city-page`, q05, snapshot `s-2026-09-27T14-42-39-101Z`. London's plan Ruling 7, which Manchester's plan carries over, applies it to every H2 and H3.

The open choice is the style inside that register (`.claude/skills/framework-heading-hierarchy/SKILL.md`, Header Style Selection). It is declared here, as `rules/headings.md` `header-style-declared` requires. Title Case applies to every heading whatever the style, FAQ questions included (`title-case-headings`).

**Options.** The heading after each option is an illustration of the style, not an outline heading. The outline writes the real headings and pre-checks them.

- **Style 2 (Conversational Hybrid), FAQ register (Recommended).** Every H2 and H3 is a buyer question built around one keyword from the research board's universe and one Manchester entity or related term. The place goes only on questions whose answer is about Manchester, and by borough name where the planner shows demand. Illustration: *"Can You Bring a Blue Staffy Puppy to Bolton, Stockport or Wigan?"*
- **Style 1 (Pure Conversational), FAQ register.** Natural questions with no keyword placed on purpose. Illustration: *"What Happens to My Deposit If I Change My Mind?"*
  - **Fits:** it is the purest reading of "conversational", and it is the style London declared.
  - **Trade-off:** the page board's `two_keyword_header` check (`scripts/family_rules.py`) warns on any body H2 that names none of its section's keyword terms. London declared Style 1 at STOP 1, and at STOP 2 its approved outline rewrote 8 headings to add a keyword from the universe (London outline, `heading_changes`). Declaring Style 1 here would mean redoing the headings at the outline.
- **Style 3 (Recommended Hybrid), FAQ register.** A question plus a parenthetical that states the answer's scope. Illustration: *"How Much Is a Blue Staffy Puppy From Carlisle? (Price, Deposit and What It Includes)"*
  - **Fits:** it is the snippet shape, and four of Google's six PAA questions are answered by no page of the eight (SERP, PAA against the pool).
  - **Trade-off:** no AI Overview appeared in the Manchester read (AIO), so the shape's main payoff is unproven for this query. A parenthetical cannot carry the price or the delivery band, because `data/price-matrix.json` and `data/settings.json` own those figures. Used on every H2, it reads as repetitive.

**Why Style 2:**

1. **The buyers' questions are questions, but the measured demand is keyword-shaped.**
   - 100 of the question file's 106 entries are questions, and so are 103 of the keyword universe's 200 rows (QF; KU).
   - The Keyword Planner's only 100–1K phrases are "staffy puppies for sale manchester", "staffies for sale manchester" and "staffordshire bull terrier for sale manchester".
   - The primary keyword and its blue variants sit at 10–100. No question phrase returned a figure (KWS §3; KU volume fields).

   A question built around one keyword serves both the ruling and the demand.
2. **The questions themselves are national.** Five of the six PAA questions name no place (FAN §1). The question intents in autocomplete ("how much are blue staffy puppies uk", "where can i buy a blue staffy puppy", "what to look for when buying a staffy puppy") do not name Manchester (KWS §1). So the place goes where the answer is local, not on every heading. The builder also lets a question name the city only when its meaning and its fact are unchanged (builder, Step 5).
3. **The page's own gates ask for this shape.** `two_keyword_header` (`scripts/family_rules.py`) and the SEO master checklist's Two-Keyword Header Method both expect a keyword in each body H2: one keyword plus one related term, never three (`.claude/skills/bsuk-seo-master-checklist/SKILL.md`). Style 2 is that shape, declared up front instead of retrofitted at STOP 2.
4. **Style 2 is already the location default.** framework-heading-hierarchy sets location pages to "Style 2 with the geo modifier". This line departs from that default in two declared ways only: the FAQ register (the user's ruling), and a place modifier used only where the answer is local.
5. **Page one leaves the ground open.** Question H2s are 0 on all eight pool pages, and questions appear only as FAQ H3s (SERP, Universal gaps). Google's top-five H1s are breed-and-place statements (SERP, What shape wins). The H1 here stays the fixed statement from `data/locations.json`, "Blue Staffy Puppies Manchester UK".
6. **Borough names keep the place in the headings without spending the city term.**
   - `budgets.location` counts "Manchester" in `<main>`, so every "Greater Manchester" counts too. "Bolton" and "Stockport" do not (`scripts/evidence_audit.py` `city_pattern`).
   - Plan Task 13 calibrates those ceilings from the pool pages before STOP 3. In scope, Manchester's pool pages carry a median of 20 city mentions and a maximum of 100 (SERP, head-term table).
   - Manchester never inherits London's per-slug override (PLAN ruling 5).

**Trade-off:**

- A question that carries two terms makes a longer heading, which works against the type-fit ruling (London's Ruling 10, carried over). Each heading holds to one keyword and one related term.
- Keyword phrases are exactly what London's two shingle collisions were made of. "does a blue staffy puppy" collided with Edinburgh's migrated heading, and "is a blue staffy a" with the buying guide's H2 (London outline, `heading_changes`).
  - So every Style 2 heading needs its own Manchester entity beside the keyword.
  - The header pre-check runs at STOP 2.
  - `python3 scripts/dup_content_audit.py --headers` runs right after the first build (lessons 18).
- Keywords in headings count toward the page's term ceilings. So the keyword rotates through the universe's variants rather than putting "blue staffy puppy" on every line.
- It departs from London's declared Style 1, though not from the location default.

**How the counts were made.** These shares are supporting evidence for question headings. The register itself is set by the ruling. A question counts as PAA when its `found_in` holds `serp_google_paa`:

```bash
python3 -c "
import json
q = json.load(open('data/queries/blue-staffy-puppies-manchester-uk.json'))['questions']
paa = lambda x: 'serp_google_paa' in x['found_in']
live = lambda x: any(f in ('serp_google_paa', 'serp_google_related') or f.startswith('thread:') for f in x['found_in'])
for name, rows in (('all', q), ('faq picks', [x for x in q if x['faq']]), ('must-answer', [x for x in q if x['must_answer']]), ('live search', [x for x in q if live(x)])):
    print(name, sum(map(paa, rows)), len(rows))
"
```

It prints `all 6 106`, `faq picks 4 20`, `must-answer 5 29` and `live search 6 33`.

| Measure | PAA | Of | Share |
|---|---|---|---|
| Every entry in the question file | 6 | 106 | 5.7% |
| FAQ picks (6 top, 7 middle, 7 bottom) | 4 | 20 | 20.0% |
| Must-answer questions | 5 | 29 | 17.2% |
| Questions found in live search (PAA, related searches, threads) | 6 | 33 | 18.2% |
| Google's banked PAA questions that are in the file | 6 | 6 | 100.0% |

Two of the six PAA questions need care:

- One is blocked as an unverified fact: "Are there blue Staffordshire Bull Terrier puppies available for sale in Manchester?"
- One is a must-answer that no FAQ block picks: "Is it better to get a male or female Staffy?"

**The same line, as one string for the research-board record:**

> Style 2 (Conversational Hybrid), FAQ register. Why: the user ruled on 2026-09-27 that every header is an FAQ-style buyer question with a conversational opening paragraph that answers it (answer board, project 5 decisions q05; London's plan Ruling 7, carried over), so the open choice is the style inside that register. Manchester's questions are questions (100 of the question file's 106 entries; 103 of the keyword universe's 200 rows), but its measured demand is keyword-shaped: the Keyword Planner's only 100–1K phrases are "staffy puppies for sale manchester", "staffies for sale manchester" and "staffordshire bull terrier for sale manchester", and no question phrase returned a figure. A question built around one universe keyword and one Manchester entity serves both, and it is what the board's two_keyword_header check and the SEO master checklist's Two-Keyword Header Method ask for: London declared Style 1, and its approved outline rewrote 8 headings at STOP 2 to add a keyword. Style 2 is the location default. The declared departures are the FAQ register and a place modifier used only where the answer is local, by borough where the planner shows demand (Bolton, Stockport, Oldham, Rochdale and Wigan at 10–100 a month each), since budgets.location counts "Manchester" but not the boroughs. No ranking page uses a question H2 (0 of 8). Trade-off: headings run longer, against the type-fit ruling. Keyword phrases are what London's shingle collisions were made of, so each heading needs its own Manchester entity and the STOP 2 header pre-check. Keywords in headings count toward the term ceilings, so they rotate through the universe's variants. It departs from London's declared Style 1. Title Case on every heading, FAQ questions included.

## Frameworks per section group

| # | Section group | Label in ENT and KU | Options | (Recommended) |
|---|---|---|---|---|
| 1 | Hero and opening | hero, title, H1 and first 100 words | EEBP, AIDA, QAB | **EEBP** |
| 2 | Deposit and viewing | G1 | PDB, QAB, BAB | **PDB** |
| 3 | Litter and prices | G2 | FAB, EEBP, QAB | **FAB** |
| 4 | Delivery to Greater Manchester | G3 | FAB, QAB, EEBP | **FAB** |
| 5 | Health and raising | G4 | EEBP, QAB, BAB | **EEBP** |
| 6 | Life in Manchester, with the rescue-or-breeder strand | G5 | QAB, FAB, PAS | **QAB** |
| 7 | The FAQ blocks | G6 | QAB, EEBP | **QAB** |
| 8 | Contact | none yet | AIDA, QAB, PDB | **AIDA** |

Against London's approved table:

- **Same framework:** groups 1, 2, 4, 6 and 7 land on the framework London took. Each is argued below from Manchester's evidence.
- **Different framework:** groups 3 and 5 differ because Manchester's evidence points elsewhere. Group 3 takes FAB where London took EEBP. Group 5 takes EEBP where London took QAB.
- **New:** group 8 had no group on London.

The research-board record's `why` and `trade_off` for each group are the two paragraphs marked **Why** and **Trade-off**, verbatim.

### 1. Hero and opening

**Options:**

- **EEBP (Recommended).** The opening paragraph under the fixed H1 is one Entity → Evidence → Benefit → Purpose statement:
  - **Entity:** Lisa Bright in Carlisle, Cumbria, with the breed named in full.
  - **Evidence:** six named puppies, five of them blue or blue and white, at £1,500 a boy and £1,700 a girl (`data/price-matrix.json`); the £500 deposit as `depositLine` words it; UK home delivery to Greater Manchester by DEFRA-approved transport at £200–£350, priced by distance, or collection in Carlisle (`data/settings.json`).
  - **Benefit:** what that gives a Manchester buyer.
  - **Purpose:** the next decision, which is to ask about a puppy or book the video call.

  The hero's counter figures are the same facts, read from data (working rule 16).
- **AIDA.**
  - **Fits:** framework-aida names region pages as its own use ("AIDA with geo-specific desire"). A hook could hold a Manchester searcher who reads "Carlisle" and is about to leave.
  - **Trade-off:** its Attention and Interest beats are written for readers who do not yet know what they want (framework-library routes unaware readers to AIDA). This searcher typed the colour, the breed and the city. The facts an engine lifts would arrive a paragraph late.
- **QAB.**
  - **Fits:** this page's ChatGPT query is "Where can I buy a blue Staffy puppy near Manchester…", and the question file scores "Where can I buy a blue Staffy puppy near Manchester?" 5, must-answer (QF; LLM). An opener that answers it in its first sentence is what an answer engine lifts.
  - **Trade-off:** that question is a top-block FAQ pick, so the hero and the top FAQ block would answer it twice. Under a fixed statement H1, the question itself is never shown.

**Why EEBP:** On Manchester's page one, "Manchester" is a search filter, not where the sellers are:
- Staffie Owners' blue Manchester facet (Bing #1) lists 7 Manchester matches, and none is in Greater Manchester.
- puppies.co.uk (Google #5) shows 3 adverts, and none is in Greater Manchester.
- Gumtree (Google #4) has 1 local advert and 13 from outside the area.
- Pets4Homes (Google #1) puts 9 of its 24 cards in the county (SERP, Universal gaps).

A Manchester buyer needs to know who is selling, where the puppies actually are, and how they reach Manchester at what price. That is also the first sentence an engine lifts. EEBP's Entity and Evidence moves put all of it into one sentence: a named breeder in a named town, six named puppies at printed prices, the deposit and the delivery band. The Entity move names the breed in full, which matters for three reasons:
- All five of Google's banked top-five H1s say "Staffordshire Bull Terrier" and Manchester, and none says "blue" (SERP, What shape wins).
- The strategy row targets "staffordshire bull terrier puppies for sale in manchester greater manchester" (KU; STRAT line 118, where the row spells it "salein").
- The fixed H1, "Blue Staffy Puppies Manchester UK", already carries the colour.

The ChatGPT answer opens by steering the buyer away from "a general classified advert" toward a source they can check, and adds that a listing or reviews are not proof a breeder is responsible (LLM). A named breeder with checkable facts is the source that answer describes. Google shows the marketplaces' own opening lines as their snippets: Pets4Homes' live count (SERP #1), and Staffie Owners' count and price range (SERP #2). Our first sentence answers them with exact figures read from data.

**Trade-off:** The opener names Carlisle in its first line, so a buyer who searched "Manchester" learns at once that the puppies are not local. An AIDA hook would hold that reader longer. The sentence has to carry the delivery band beside "Carlisle" so the place reads as an answer. It can go no further than the band: data holds no Greater Manchester figure inside it, and no mileage or journey time may be printed (builder, UK geography), although the session brief puts the buyer about 120 miles away. EEBP also does not work through the deposit fear; that job belongs to group 2.

### 2. Deposit and viewing

**Options:**

- **PDB (Recommended).** The buyer-question heading carries the Pain: the worry about sending money to a seller found online and never hearing back. Depth explains why that worry is rational, from independent guidance and our own reading of the ranking pages. The Brief lists what a buyer needs before paying, each item met by a ruled fact, and then the next step.
- **QAB.**
  - **Fits:** the ruling makes every heading a question answered first, and the deposit questions arrive as questions.
  - **Trade-off:** the strongest of them are taken or blocked. "Should I see the puppy with its mother before any money changes hands?" (5) is a middle-block FAQ pick. Three more are blocked as unverified fact: "Is it safe to pay a deposit to a seller I found through an online advert?" (4), "Should I pay a deposit before I have seen the puppy?" (4) and "Can I see the puppy with its mother where the litter was raised?" (4) (QF). So QAB headings would start from second-rank questions, and the fear behind them would be answered but never acknowledged.
- **BAB.**
  - **Fits:** framework-bab's own scam-prevention row moves the reader from a deposit lost to a vanished seller to a purchase they can check.
  - **Trade-off:** its Before has to be a scene. The only one in Manchester's research is a search-result excerpt from a Staffy scam-alert thread with no UK signal (FAN excerpt 5). Owner language from opened threads is not available. The eight reused threads were recorded as paraphrases, and the thread ledger says not to reopen them. Reddit's network-security block stopped every new fetch (FAN §2 and §3). A Before written as a Manchester buyer's story would be invented (rule 9).

**Why PDB:** The Manchester buyer arrives with the fear already named:
- "Should I see the puppy with its mother before any money changes hands?" is one of the question file's three score-5 questions (QF, from r/UK_Pets), and two more deposit questions score 4 (FAN §4).
- The r/manchester excerpts aim at the platforms that rank #1 and #4 for this query: "Avoid the puppy farmers on Gumtree." and "Pets4Homes also has stolen puppies, and puppy-farmed puppies."
- The scam-alert excerpt names the outcome buyers dread: "take your payment online and you never hear from them again" (FAN §3; language only).

framework-pdb is written for a reader who lands with a named fear, and its page table gives location pages this distance-and-trust pain. Depth has independent material and needs no statistic we have not fetched:
- the RSPCA and PAAG guidance on online adverts that ENT recommends for this group (LIB lines 52 and 66);
- our own reading of page one, where a deposit appears only inside sellers' adverts, once marked "non refundable", and no page offers remote viewing in its own voice (SERP, Universal gaps).

The Brief is then met by facts alone:
- a live video call with the puppy and Maggie, on request, before any deposit (q03);
- a deposit that books the viewing, reserves the puppy and comes off the price (`depositLine`);
- its refund term as `data/settings.json` `deposit_refund_clause` words it, which is now in data (PLAN ruling 1);
- payment by bank transfer (q04);
- the parents, their papers and the vet records seen before the buyer commits (`data/faq.json` `whyus-evidence`).

**Trade-off:**
- **Length.** PDB is the longest of the three shapes, which works against the type-fit ruling and the per-H3 height cap (lessons 17).
- **Advice.** Its Brief must be written from our own process, never from general advice (lessons 9). The Manchester ChatGPT answer tells buyers to see the puppy "at the place where it was raised" and not to have it delivered. Our deposit books the in-person viewing, and we deliver. So the Brief says what the video call and the viewing order give the buyer, and never adopts either line as a rule we would then fail.
- **Excerpts.** The r/manchester excerpts lend tone, never quotes. The platforms they name are never named or linked on the page (BRAND_CLASH in `scripts/keyword_variants.py`; builder, Links).
- **Order.** The heading has to be the buyer's question, answered first, so the Pain lives in the heading and the Depth comes after the answer, not before it.

### 3. Litter and prices

**Options:**

- **FAB (Recommended).** Each thing the price includes is a Feature. The Advantage is what it does that an advert's bare price does not show. The Benefit is what it means for the buyer. The price is explained by the puppy's sex and its inclusions, never by its coat.
- **EEBP.**
  - **Fits:** framework-eebp names puppy cards and price-explainer rows as its uses. An entity-first row per named puppy, with Maggie and Jones, is the form answer engines lift. The ChatGPT answer's only high-band entities, microchip and vaccinations, are puppy-level facts (LLM).
  - **Trade-off:** the rows read as a spec sheet and do not take on the price-floor objection. With group 5 also on EEBP, the page would carry two row sections with the same rhythm.
- **QAB.**
  - **Fits:** PAA #1 is "How much does a blue Staffy puppy cost?" (QF score 5, must-answer).
  - **Trade-off:** that question and "How much is the deposit?" are both top-block FAQ picks. A QAB section here would echo the FAQ and could use neither as a heading.

**Why FAB:** Manchester's commercial searches hunt for a price floor:
- Three of the six related searches Google gave for the primary keyword are "cheap", "under 500" and "free … to good homes" (FAN §1).
- Autocomplete adds "staffy puppies for sale manchester under 500 near me" (KWS §1).
- The page-one snippets quote ranges from £50 or £75 up to £2,800 (AIO).

Our £1,500 a boy and £1,700 a girl (`data/price-matrix.json`) meets that reader beside those numbers. framework-fab exists so that a price never ships as a bare number. Each inclusion becomes a Feature with its Advantage and its Benefit:
- the vet-signed health card recording the first vaccination, microchip, worming and flea treatment (LEDGER `puppy-vet-signed-health-card`, confirmed 2026-10-04);
- the KC registration application form;
- the written contract;
- the Two-year health guarantee;
- support after collection.

The sources for these are `data/settings.json` `puppy_trust_signs` and `guarantee_label`, and `data/faq.json` `whyus-paperwork`. The Advantage has fetched ground: across all eight ranking pages, "guarantee" and "contract" appear nowhere, no page names the paperwork a puppy goes home with, and there are 0 tables (SERP, Universal gaps).

FAB also keeps the price off the colour:
- The Manchester ChatGPT answer warns against "rare blue", "exclusive blue" and "unusually high prices", and says the Royal Kennel Club puts health and temperament before colour (LLM).
- The only blue price claim on page one is a marketplace FAQ's "Blue variants are trending approximately 61% higher than the market average" (SERP #6).
- Our price follows the sex, not the coat (`data/puppies.json`), so the Features are the inclusions and the sex, never the colour.

The question file's uncovered paperwork section is the same documentation stack (QF `extra_sections`).

**Trade-off:**
- **Parked words.** The price-floor words themselves are parked as BRAND_CLASH (`scripts/keyword_variants.py`: cheap, under £N, free to good homes; KU). So the Advantage answers that reader without writing their words, without naming a marketplace, and without using anyone else's prices as a foil, since those ranges are not our data.
- **Fewer entities.** FAB names entities less than EEBP does. The six puppies and the parents are carried by the puppy cards, not by the rows.
- **Ledger limits.** Every Benefit stays inside the ledger:
  - the guarantee only as `guarantee_label` and `guarantee_cover` word it;
  - the Kennel Club only as the application-form wording (LEDGER `parents-kc-registered-application-form`);
  - never "vet checked" in our own sentence (ENT).

### 4. Delivery to Greater Manchester

**Options:**

- **FAB (Recommended).** Two rows, one for UK home delivery and one for collection in Carlisle. The Feature is the route and its price from data. The Advantage is what it does better than the other route. The Benefit is what it means for a home in Greater Manchester.
- **QAB.**
  - **Fits:** three delivery questions score 4 (QF), and the borough phrases show place intent that a direct answer serves.
  - **Trade-off:**
    - Two of the three delivery questions are top-block FAQ picks.
    - PAA #2 ("Are there blue Staffordshire Bull Terrier puppies available for sale in Manchester?") is blocked as unverified fact, so QAB lacks its natural headings.
    - A heading per borough would repeat one answer, because data has no figure per borough.
    - QAB's Benefit does not weigh the two routes.
- **EEBP.**
  - **Fits:** DEFRA-approved transport and the government's welfare-in-transport guidance can be the entity (ENT G3; LIB line 55), with the band and "priced by distance" as the evidence.
  - **Trade-off:** it suits one route, and the Manchester buyer's real decision is between two.

**Why FAB:** This is the only group where an answer engine argues against one of our options. The Manchester ChatGPT answer tells the buyer: "Don't agree to meet in a car park or have the puppy delivered to you" (LLM; ENT flag 4).

The buyer still has two real routes (`data/settings.json` `delivery_min_gbp`, `delivery_max_gbp`, `delivery_note`):
- UK home delivery by DEFRA-approved transport at £200–£350, priced by distance;
- collection in Carlisle.

FAB's Advantage beat is where two routes get weighed, and framework-fab's advantage-comparison says to admit it when the alternative wins a row:
- Collection wins on seeing the puppy where it was raised, which is the engine's own advice.
- Delivery wins on the journey. The live video call with the puppy and its mother before any deposit (q03) answers the engine's worry about a puppy the buyer never sees.

The gap is total: none of the eight pages says how a puppy reaches a Manchester home or what that costs (SERP, Universal gaps). The demand sits in the boroughs:
- "staffy puppies for sale" with Bolton, Stockport, Oldham, Rochdale or Wigan is 10–100 a month each (KWS §3);
- "Staffy puppies for sale near Salford" is a Google related search;
- Google's #2 result is a Salford facet (SERP #2).

One Feature-Advantage-Benefit pair per route can name those boroughs in its Benefit. That keeps the place in the copy, because `budgets.location` counts "Manchester" but not "Bolton" or "Stockport" (`scripts/evidence_audit.py` `city_pattern`).

**Trade-off:**
- **Data limits.** Each Advantage has to come from data. Data holds the band, the method and "priced by distance". It holds no Greater Manchester figure inside the band, and no mileage, journey time, vehicle or delivery date may be stated (builder, UK geography). So the advantages speak to cost, method and what the buyer sees before paying, never to the trip itself.
- **Borough names.** A borough is attested only as search demand and as a listing location, and every borough gets the same band, priced by distance. So a borough is named only as a place we deliver to, never with a price, a time or a local claim.
- **Lost sales.** Weighing collection honestly will send some Manchester buyers on the drive to Carlisle, at the cost of the easier sale.

### 5. Health and raising

**Options:**

- **EEBP (Recommended).** One row per entity:
  - the vet-signed health card, with the first vaccination, microchip, worming and flea treatment recorded on it;
  - the parents' DNA tests (L-2-HGA and HC-HSF4), with eye and elbow screening named and the certificates shared on request;
  - the raising in our home, including Puppy Culture and ENS;
  - support after collection.

  Each row carries its evidence, what it gives the buyer, and the decision it supports.
- **QAB.**
  - **Fits:** the top-scored question in the file is "Are the parents of your blue Staffy puppies health-tested?" (6), and the ChatGPT answer is itself a list of questions to ask a breeder. Two unpicked must-answers have answers on file: "Can I see the genetic test results for both parents before I commit?" and "What paperwork should a puppy advertised as KC registered come with?" (QF).
  - **Trade-off:** the middle FAQ block already asks four health and paperwork questions as questions: health-tested (6), microchipped and vet checked (4), vaccinations, worming and flea (4), and the flagged DNA question (4). A QAB section would ask the same kind of question a second time. Seven of the fifteen blocked thread questions are health or paperwork questions (QF).
- **BAB.**
  - **Fits:** framework-bab's health row runs from sick-puppy fear to a vet health check, first vaccinations and a vet-signed health card. That After is now ledger-backed (2026-10-04).
  - **Trade-off:** the Before, a sick or farmed puppy, has no documented Manchester scene. The one buyer scenario on record, a viewed puppy with mites, is a blocked thread question that KU parks. framework-bab also rules itself out for informational care content.

**Why EEBP:** The two high-band entities in Manchester's ChatGPT answer are microchip and vaccinations. Neither is on the page yet (LLM, `on_page` false), and the strategy row's build note names the same two as the checks this page must answer (STRAT line 108). Both sit on one document that has a proof on file: every puppy leaves with a vet-signed health card recording its first vaccination, microchip, worming and flea treatment (LEDGER `puppy-vet-signed-health-card`, confirmed 2026-10-04; `data/faq.json` `health-vaccinations`). The entity research picked that card as the entity to build around (ENT).

The same answer asks for three more things:
- "the parents' actual results, rather than simply 'health tested'";
- the certificates;
- that the buyer not accept "KC registered" as meaning "health tested".

EEBP's Evidence step can meet these without stating a result. Since 2026-10-05 the ledger has held that the parents' certificates and DNA results are shared with a buyer on request (LEDGER `certificates-on-request`). So the parents' row names L-2-HGA and HC-HSF4, names eye and elbow screening (ENT), and offers the certificates. Each entity keeps its own evidence, so the KC registration application form is never blended with the tests. None of the eight ranking pages names a health test, a guarantee or the paperwork in its own voice (SERP, Universal gaps).

The raising is backed by data too:
- the litters grow up in our home and meet children, cats, older people and household sounds (`data/faq.json` `about-home-raised`; LEDGER `litters-home-raised-never-kennels`);
- Puppy Culture and ENS come from the breeder's answer (ENT).

This is the socialisation the ChatGPT answer asks about (LLM).

**Trade-off:**
- **Spec-sheet feel.** EEBP rows read as a spec sheet, and the raising half is more story than spec, so the rows flatten it.
- **No results.** The parents' row can promise access to the certificates, never a result: no "clear", no grade, no score. The ledger's `parents-dna-clear` row has no proof on file (PLAN ruling 3).
- **Unanswered asks.** Some of the ChatGPT answer's questions have no data behind them, so no row answers them: the inbreeding coefficient (ENT, Excluded), and two socialisation items that `about-home-raised` does not list, other dogs and being left alone.
- **Ledger vocabulary.** EEBP concentrates the ledger's vocabulary: "DNA test", "health certificate", "KC registered" and "vet checked". Every sentence that uses those words must match a ledger row's pattern, and those rows list London's sentences one by one. So each new Manchester evidence sentence needs its row extended before `scripts/evidence_audit.py` passes it. `claim-unledgered` is an ERROR on a new location page.

### 6. Life in Manchester, with the rescue-or-breeder strand

**Options:**

- **QAB (Recommended).** Each life question is answered first with a sourced breed fact, then with what that means in a Manchester home. The questions cover male or female, exercise, a flat, time alone, the reputation worry and the banned-breed line, and buying or rescuing.
- **FAB.**
  - **Fits:** the rescue strand is a choice between two routes, and framework-fab's advantage-comparison is the honest shape for one, because it admits when the alternative wins a row.
  - **Trade-off:** FAB is for spec-bearing content. The rest of this group (a flat, time alone, exercise, temperament) has no specs, so FAB fits one strand and strains on the others.
- **PAS.**
  - **Fits:** the reputation worry has a Manchester voice, the r/manchester thread title "So many XL bullies have made me scared of running in MCR" (FAN excerpt 7), and PAA asks "Is blue Staffy aggressive?".
  - **Trade-off:**
    - PAS agitates, and agitating a reputation fear on a page that sells the breed works against the page.
    - The only legal line the page may state is that the breed is not on the government's banned list (builder, fact table).
    - Every agitation line needs a sourced consequence (framework-pas).
    - The reader here is checking suitability, not in pain; framework-library keeps PAS for problem-aware readers.

**Why QAB:** These questions arrive as questions, and page one leaves them open. Four of Google's six PAA questions are life questions: male or female, good pets, aggressive, and left alone. None of the eight pages answers any of them (SERP, PAA against the pool).

The rescue strand is Manchester's own:
- The live read of 2026-10-07 put Dogs Trust's Manchester rehoming page at #9 and showed "blue staffy puppies manchester rescue" and "… for adoption" among the related searches (AIO).
- The planner puts "staffy rescue manchester" at 10–100 a month. It is the only phrase outside the three 100–1K for-sale phrases that shows a top-of-page bid, £0.99–£1.60 (KWS §3).
- Trends shows Adoption (+40%) and Animal shelter (Breakout) rising beside "blue staffy" (KWS §2).
- The r/manchester excerpts frame the choice as "buying or adopting" and "If you must buy a pedigree, get it from a responsible family breeder" (FAN §3).

The content-architect matrix pairs adoption content with H-S-S and BAB (`.claude/agents/bsuk-content-architect.md` line 70). On a breeder's page, though, BAB would cast rescue as the "Before". QAB answers the choice as a question, honestly, with Dogs Trust as the independent source (ENT G5; LIB line 65). The ai-overview read notes that a short, honest rescue-or-breeder passage is citable, and that no page on page one answers it (AIO, GEO implication).

Each Answer carries a sourced breed fact in the neutral register allowed for breed facts (CLAUDE.md rule 1): the PDSA on exercise, Dogs Trust on the breed, and gov.uk for "not a banned breed". The Benefit then ties that fact to a home in Manchester.

**Trade-off:**
- **Header supply.** The bottom FAQ block already holds seven life questions: aggressive, good pets, family and children, first-time owners, a flat, left alone, and food (QF). No FAQ question may repeat a header (London's plan Ruling 7, carried over). So QAB headings come from the unpicked supply, or the outline moves picks. The unpicked supply is:
  - male or female (a PAA must-answer, unpicked; KU places it with litter and prices);
  - exercise;
  - bonding with one person;
  - the banned-breed question;
  - the rescue question.
- **Repetition.** A run of QAB sections can read like a second FAQ.
- **Brand clash.** "Rescue" is a BRAND_CLASH term in `scripts/keyword_variants.py`, so the strand answers the buyer's question without targeting "rescue" as a keyword. Its answer must never push a buyer away from us or talk down rescue (lessons 9).
- **Link.** The link library's Dogs Trust row is the breed page. A Manchester rehoming page would need its own row and a live check before the board (working rule 12).

### 7. The FAQ blocks

**Options:**

- **QAB (Recommended).** Question, Answer (the fact first), and Benefit (one short line), in three blocks with FAQPage JSON-LD.
- **EEBP.**
  - **Fits:** an answer led by its entity and a named proof is the most citable form.
  - **Trade-off:** the builder draws each answer only from its own bank row or the settings key its `fact_source` names (builder, Step 5). So EEBP's Evidence and Purpose beats cannot add a proof the row does not hold. framework-eebp is also aimed at rows, not answers.

There is no third option. framework-bab, framework-fab and framework-pas each send FAQ answers to framework-qab, and AIDA and PDB shape a page or a section, not a single answer.

**Why QAB:** On Manchester's page one, the FAQ is where the ranking pages are weakest.
- FAQPage markup sits only on the three Staffie Owners pages: Google #2 (the Salford facet), Bing #1 (the blue Manchester facet) and Bing #4 (SERP, SERP schema). That domain is the weakest in the pool on both indexes (Ahrefs DR 0; 51 referring domains on DataForSEO), and it ranks on exact-match facets and markup (SERP; KWS §4).
- Pets4Homes holds Google #1 with an FAQ of five questions, only one of them answered on the saved page, and no FAQPage markup (SERP #1).

A fully answered, marked-up QAB block beats both with the page's own facts. framework-qab sets location pages at six QAB items or more, with FAQPage JSON-LD. The question file holds 20 picks today (6 top, 7 middle, 7 bottom). Four of them are Google PAA questions and seven were asked in the ChatGPT answer (QF), so the blocks carry the answer engines' own questions in buyers' words.

**Trade-off:**
- **Benefit line.** The builder draws each answer only from its own bank row or settings key (builder, Step 5). The Benefit line may say what that one fact means for the buyer and must never add a second fact. Where it would, the Benefit is dropped.
- **Flagged pick.** One middle pick, "Are both parents DNA tested clear for L-2-HGA and HC-HSF4?", assumes a result we never state. It is an open flag on the session brief, to be fixed in the harness before STOP 2. Under any framework, its answer cannot say "clear".
- **Header competition.** QAB draws the page's best questions into the FAQ, and no header may repeat them.

### 8. Contact

**Options:**

- **AIDA (Recommended).** The section runs the Action stage of the page's arc: one form, what happens after you send it, the last doubt answered before the button, and honest urgency only.
- **QAB.**
  - **Fits:** the ruling makes the contact heading a buyer question answered first, which is QAB's native shape. The ChatGPT answer closes by asking the buyer two things, how far they would travel and boy or girl (LLM). A QAB answer can turn those into "tell us which puppy, or boy or girl, and whether you would collect or want delivery".
  - **Trade-off:** QAB stops at a benefit line. It does not call for the friction items a form section depends on (one call to action, the reply time, the last objection), so those would rest on the writer's judgment rather than on the framework.
- **PDB.**
  - **Fits:** the dread in the deposit-scam excerpt ("you never hear from them again") is the last fear before a stranger's form.
  - **Trade-off:** it repeats group 2's Pain at the foot of the page, and it runs long for a form section.

**Why AIDA:** framework-aida names region pages as its own use. Its Action stage is the checklist a form section needs: one call to action, what happens after the buyer submits, the last objection answered before the button, and honest urgency only. Manchester's evidence fills each item from data:
- **The objection** is the one the deposit-scam excerpt names: "take your payment online and you never hear from them again" (FAN §3, excerpt 5). The bank holds the answer:
  - every enquiry is answered by us within 24 to 48 business hours, after the handover as well as before it (`data/faq.json` `enquiry-reply-time`, `home-after-support`; LEDGER `breeder-support-after-collection`);
  - the puppy is confirmed as still free before the buyer pays anything (`data/faq.json` `listing-availability`).
- **What to send** follows the ChatGPT answer's own close, which asks how far the buyer will travel and whether they want a boy or a girl (LLM). Here that means which puppy (or boy or girl, since the price follows the sex), and collection in Carlisle or delivery to their part of Greater Manchester.
- **Urgency** is only what data holds: six puppies available today (`data/puppies.json` `status`).

The group needs a pick in any case. The ruling makes this heading a buyer question, and `scripts/outline_matrix.py` refuses "—" on any row whose tree holds an H2 ("a row with an H2 names its framework").

**Trade-off:**
- **Arc.** With the heading a buyer question answered first, AIDA's Attention and Interest beats have no room here. The section runs only AIDA's Action stage, so the label promises more arc than this section carries; the arc is the page's.
- **Reply time.** It is the bank's "24 to 48 business hours", never a shorter one (framework-aida).
- **Project 6.** Until project 6 the phone is `PHONE_PLACEHOLDER` and `PUBLIC_FORMSPREE_ID` is unset, so the copy cannot offer a call and the form posts nowhere live.
- **Age.** The litter's age ("10 weeks old", `age_weeks`) goes stale. It is confirmed before it is printed and is never used as a deadline.

## For the outline (STOP 2): noted, not decided here

1. **Header and FAQ collisions.** The FAQ picks already hold questions the groups would lead with, and London's plan Ruling 7 (carried over) bars an FAQ question from repeating a header.
   - **Top block:** both delivery must-answers, PAA #1 on price, "How much is the deposit?", "How do I know a puppy is still available?" and "Where can I buy a blue Staffy puppy near Manchester?".
   - **Middle block:** "Should I see the puppy with its mother before any money changes hands?", the health-tested question, "Has the puppy been microchipped and vet checked?", "What vaccinations, worming and flea treatments has the puppy had?" and "How do I spot a bad Staffy breeder?".
   - **Bottom block:** seven life questions.

   For each collision, the outline either moves the question out of the FAQ (taking a replacement from the question file) or asks the section's question in other words. Nine must-answer questions sit in no FAQ block, and they are the natural header supply:
   - **Group 3:** "What is included when I buy a Blue Staffy puppy…", "What paperwork should a puppy advertised as KC registered come with?", "Are your Blue Staffy puppies Kennel Club registered and health-checked?" and "Is it better to get a male or female Staffy?".
   - **Group 5:** "Do you offer health guarantees…", "What are Staffies prone to?" and "Can I see the genetic test results for both parents before I commit?".
   - **Group 6:** "Do Staffies get attached to one person?" and "How much exercise does a Staffordshire Bull Terrier need daily?".
2. **The flagged DNA pick.** The middle-block "Are both parents DNA tested clear…" pick is the session brief's open harness flag. It is fixed before the outline is approved.
3. **The rescue keyword is placed two ways.**
   - KU places "staffy rescue manchester" in G5.
   - KU parks "as a first-time owner, should i get a staffy puppy or an adult rescue" because "rescue" is a BRAND_CLASH term in `scripts/keyword_variants.py`.

   One rule gives two outcomes. Group 6's recommendation answers the rescue question without targeting the phrase. The controller makes the two placements agree before the record is written (plan Task 11).
4. **One primary framework per section** (`.claude/skills/framework-library/SKILL.md`, "Framework stacking"). The header ruling already fixes the top of every section: a buyer question, answered first. The EEBP and FAB rows sit under that opener.
5. **The Manchester review.** `data/reviews.json` has one Manchester row, The Victoria Family ("Manchester, UK"). It is the page's only local proof. The builder keeps every review in its own section, so no framework above quotes it inside a body section. Which slot it takes (top, middle or bottom) is an outline choice.
6. **Frame parts that carry an H2.** If the outline lists an H2 for a frame part (key takeaways, a review, the newsletter), that row needs one of the seven names too (`scripts/outline_matrix.py`).
7. **Ledger coverage.** Groups 3 and 5 put the most ledger vocabulary on the page.
   - A new evidence sentence needs a matching ledger pattern, or `claim-unledgered` fails it.
   - A ledger claim made twice must link a proof object (`claim-bound-to-proof`). The proofs are rulings files that no page can link, so each such claim is made once, or worded outside the vocabulary (for example "vet-signed health card").
8. **Shapes.** The page has two EEBP groups (a single opening statement in group 1, rows in group 5) and two FAB groups (what the price includes in group 3, two routes weighed in group 4). They should look different on the page. Any of them rendered as a table is a `table` shape with three styles at 1280 / 768 / 375 and stacks below 640px (working rule 13).
9. **The engine's delivery advice is answered once.** Groups 2 and 4 both meet the ChatGPT answer's "see it where it was raised" and "don't have it delivered" with the video call before any deposit. The outline decides which section carries the full answer and which points to it.
