# Manchester Page Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Walk `/uk-locations/blue-staffy-puppies-manchester-uk/` (slug `blue-staffy-puppies-manchester-uk`) through page-run rows 1–21 so the 5-word noindex stub becomes a real city page, written from its own approved outline. This session runs Phases A–D and ends at STOP 1, the research board.

**Architecture:** One page, one run, in `docs/reference/page-run.md` order — that file is the spec, and every command below is its command. Research (rows 4–7) writes under `data/queries/` and `docs/research/manchester-page-run/`; four controller stops each publish an Artifact, post one answer-board batch named for the slug, and record the approval from the saved answers file. London's plan (`docs/superpowers/plans/2026-09-30-london-page-run.md`) is the worked example; this plan states only what differs for Manchester, and gives every command in full.

**Tech Stack:** Astro 4 on `CityShell`; Python 3 scripts under `scripts/` and pytest under `tests/py/`; the Playwright render harness; DataForSEO (paid, only through `scripts/query_augment.py`'s spend guard); Firecrawl (credits, last resort); the claude.ai Artifact / ArtifactData / ArtifactComments tools.

---

## How this plan is executed

- **Subagent-driven**, Opus implementers, one fresh subagent per research task, dispatched in parallel where tasks share no file; the controller reads every agent's diff before accepting it (lessons, entry 3).
- **CONTROLLER-only:** every STOP, every paid-call approval, every ArtifactComments watch, every Artifact publish, every answer-board read or write.
- **Branch `manchester-page`** in the main checkout `/Users/apple/Downloads/BSUK` (so the route mod reads this run). Commit after every task; never push; never merge into `foundation` without the user's word. Trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Rulings that bind every task

London's rulings 1, 3–11 carry over unchanged (`docs/superpowers/plans/2026-09-30-london-page-run.md`, "Rulings that bind every task"), with these Manchester updates:

1. **Deposit refund wording now exists as data:** `data/settings.json` `deposit_refund_clause` (landed 2026-09-30). A page reads it, never types it.
2. **Own components per page** (`rules/design.md` `own-components-per-page`, breeder q10, 2026-10-02): London's fifteen `City*` components are London's. Manchester's components are designed after STOP 2 from Manchester's outline.
3. **Breeder facts of 2026-10-04/05** (memory, London close): parents KC registered; vet-signed health card, first vaccinations, microchip, worming and flea treatment; certificates and DNA results exist and are shared on request, but none is in the repo, so a page names the tests and states no result.
4. **Lessons 7, 8, 9, 18, 19** (`docs/reference/lessons.md`): an image with words is read as copy; every alt is checked against its picture at the Asset Gate; buyer advice is checked against our own facts before STOP 2; `python3 scripts/dup_content_audit.py --headers` runs right after the first build; a corrected fact is searched site-wide.
5. **Known Issue 99** (`docs/reference/session-log.md`): `budgets.location` in `data/quality/evidence-budgets.json` is calibrated from Manchester's and London's top-5 competitor pages before STOP 3 (Task 13). Manchester never inherits London's `budgets_by_slug` entry.

## Stops (controller-owned, hard)

| Stop | Row | Task | Batch id | Recorded by |
|---|---|---|---|---|
| STOP 1: research board | 8 | Task 12 | `2026-10-07-research-board-blue-staffy-puppies-manchester-uk` | `python3 scripts/research_board.py blue-staffy-puppies-manchester-uk --approve --answers <file>` |
| STOP 2: outline | 9 | Phase E | `<date>-outline-blue-staffy-puppies-manchester-uk` | `python3 scripts/outline_matrix.py blue-staffy-puppies-manchester-uk --approve --answers <file>` |
| STOP 3: page board | 10 | Phase F | `<date>-page-board-blue-staffy-puppies-manchester-uk` | the board's db, then `python3 scripts/board_approve.py blue-staffy-puppies-manchester-uk` |
| STOP 4: Asset Gate | 11 | Phase G | `<date>-asset-gate-blue-staffy-puppies-manchester-uk` | the board's db, then `python3 scripts/board_approve.py blue-staffy-puppies-manchester-uk` |

## Paid fetches

Guard read 2026-10-07 (`python3 scripts/query_augment.py --budget <source>`): $0.51215 counted of the $1.00 total cap; page cap $0.50 per slug per day. Preflights for the slug: `serp_google` 3 and `ai_engines` 3 (banked 2026-09-23 / 2026-09-25), `keyword_volume` 0 and `backlinks` 0 (not bought).

| Call | Source | Estimate |
|---|---|---|
| Keyword volumes for the keyword universe (Google Ads, UK, en) | `keyword_volume` | $0.10 (typical call) |
| Neighbourhood terms for Greater Manchester (as London's block 3d) | `keyword_volume` | $0.10 |
| Competitor authority (referring domains of the top-5 domains) | `backlinks` | $0.05 |
| Google SERP + PAA refresh, "blue staffy puppies manchester" (optional; banked copy is 14 days old) | `serp_google` with `--refresh` | $0.01 |

**Worst case $0.26**, inside the page cap and leaving $0.23 of the total cap. Every call runs `--preflight` then `--record` (`.claude/skills/bsuk-query-augmentation/SKILL.md`, Money); the controller asks the user once (Task 5) before any of them.

## File map

**Created:** `data/page-runs/blue-staffy-puppies-manchester-uk.json`; `data/facts/blue-staffy-puppies-manchester-uk.json`; `docs/research/manchester-page-run/{intake.txt,inventory.md,serp-findings.md,keyword-variants.json,keyword-universe.json,entities.md,angles.md,strategies.md,frameworks.md,ai-overview.md}`; `data/queries/raw/blue-staffy-puppies-manchester-uk/{keyword_volume,neighbourhood_keywords,backlinks}.response.json`; `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-10-07.json`; `data/research-boards/blue-staffy-puppies-manchester-uk.json`; `docs/artifacts/research/blue-staffy-puppies-manchester-uk.{html,md}`; `docs/reference/answer-board/batches/2026-10-07-research-board-blue-staffy-puppies-manchester-uk.{md,json}`.
**Modified:** `data/queries/blue-staffy-puppies-manchester-uk.json` (regenerated in London's format: `word_target`, competitor `words`); `data/quality/evidence-budgets.json` (KI 99); `docs/superpowers/sessions/2026-10-07-session-brief.md`.
**Never hand-edited:** `data/locations.json`, `data/page-map.json`, `public/_redirects`, `public/images/**`, `data/queries/spend.json`, `data/queries/dashboard.json` (the guard writes them).

---

## Phase A: Session open (row 1)

### Task 1: Builder skill and session-open record

- [ ] **Step 1 (CONTROLLER):** ArtifactComments `watch` on `https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf`. (Done 2026-10-07.)
- [ ] **Step 2:** `grill-me` ran (`--brief`, `docs/superpowers/sessions/2026-10-07-session-brief.md`); `superpowers:writing-plans` is this plan; invoke the Skill tool with `bsuk-location-page-builder`.
- [ ] **Step 3:** Run `python3 scripts/page_run_record.py blue-staffy-puppies-manchester-uk session-open --builder bsuk-location-page-builder`. Expected: exit 0; `session_open` lists `grill-me`, `superpowers:writing-plans`, `bsuk-location-page-builder` in that order.
- [ ] **Step 4:** Run `python3 scripts/pipeline_status.py | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['slug'],d['now'])"`. Expected: `blue-staffy-puppies-manchester-uk 2` (the route map has moved to Manchester).
- [ ] **Step 5:** Commit `data/page-runs/blue-staffy-puppies-manchester-uk.json`, the brief and this plan: `chore(manchester): session open recorded (row 1); brief and plan`.

## Phase B: Intake, URL and inventory (rows 2–4)

### Task 2: Intake, URL decision, facts extract

- [ ] **Step 1:** `mkdir -p docs/research/manchester-page-run && npm run -s build && python3 scripts/page_intake.py blue-staffy-puppies-manchester-uk | tee docs/research/manchester-page-run/intake.txt`. Expected: `Mode stub`, `Robots noindex, follow`, `Board none`, built page no longer STALE.
- [ ] **Step 2:** `grep -n "manchester" docs/research/2026-09-26-url-family-decision.md` and `npm run -s check:redirects`. Expected: the slug is kept; exit 0; no `data/redirects.json` row.
- [ ] **Step 3:** `python3 scripts/facts_preserved_check.py --extract blue-staffy-puppies-manchester-uk`. Expected: all counts 0 (the body is "Blue Staffy Puppies Manchester UK"). A non-zero count is a harness defect: do not commit; report it.
- [ ] **Step 4:** `python3 -c "import json;print('blue-staffy-puppies-manchester-uk' in json.load(open('data/verbatim/applies.json'))['slugs'])"`. Expected: `False` (stub, Known Issue 79).
- [ ] **Step 5:** Commit `chore(manchester): intake, URL kept, migrated facts extracted (rows 2-3)`.

### Task 3: Research inventory (row 4)

- [ ] **Step 1:** Write `docs/research/manchester-page-run/inventory.md` as London's (one row per item: on disk, status, what fetches it), from the preflights above: SERP + PAA banked 2026-09-23 (exit 3); ChatGPT answer banked 2026-09-25 (exit 3); 8 competitor pages under `data/queries/cache/blue-staffy-puppies-manchester-uk/`; threads banked (`data/queries/raw/blue-staffy-puppies-manchester-uk/threads.json`, 8 threads, 21 questions); keyword volumes, neighbourhood terms and backlinks missing (exit 0, Task 5); Search Console `NOT FETCHED — GSC property unverified (domain expired); no exports on disk`; LLM mentions `NOT FETCHED — llm_mentions only once BSUK's domain is live (project 6)`.
- [ ] **Step 2:** `npm run -s check:barriers`. Expected: exit 0.
- [ ] **Step 3:** Commit `docs(manchester): research inventory before any fetch (row 4)`.

## Phase C: Research and fan-out (rows 5–7)

Tasks 4, 6, 7, 8 and 9 share no file and run as parallel agents. Task 5 runs in the controller while they work.

### Task 4: Competitor pool — H2s, metrics, word target (row 5, steps 2–3) — free

- [ ] **Step 1:** For each `data/queries/cache/blue-staffy-puppies-manchester-uk/<n>.html`: `python3 scripts/query_augment.py --extract-h2 <file>`.
- [ ] **Step 2:** `python3 scripts/query_augment.py --competitor-metrics blue-staffy-puppies-manchester-uk`. Expected: each competitor gains `words`; the file gains `word_target` (median, or `NOT FETCHED — <barrier>` when fewer than two prose pages, as London).
- [ ] **Step 3:** `@bsuk-framework-agent` reads each saved page (no new fetch unless a page is blocked — Freeads was blocked on 2026-09-23; a Playwright capture is free, Firecrawl last) and writes `docs/research/manchester-page-run/serp-findings.md`: per top-5 competitor its type, section count, why it ranks, its weakness (our wedge), and the evidence path.
- [ ] **Step 4:** `npm run -s check:queries && npm run -s check:competitors && npm run -s check:gaps`. Expected: exit 0.
- [ ] **Step 5:** Commit `research(manchester): competitor metrics, word target and SERP findings (row 5)`.

### Task 5 (CONTROLLER): The paid calls

- [ ] **Step 1:** Ask the user once in chat to approve the calls in the Paid fetches table (worst case $0.26), and for today's DataForSEO dashboard balance.
- [ ] **Step 2:** On a yes: `python3 scripts/query_augment.py --reconcile --balance <B> --opening <O> --covers <N>` (the skill's Money procedure); then each call `--preflight` → call → `--record`, saving the responses under `data/queries/raw/blue-staffy-puppies-manchester-uk/`. On a no: each is written `NOT FETCHED — the user declined the paid <source> call on 2026-10-07`.
- [ ] **Step 3:** Commit `research(manchester): keyword volumes, neighbourhood terms and competitor authority (row 5; paid, guarded)`.

### Task 6: Fan-out — PAA, threads, owner language (row 5, step 4)

- [ ] **Step 1:** PAA from the banked SERP response (`people_also_ask` items); `@bsuk-paa-agent` only if the banked set is empty.
- [ ] **Step 2:** `bsuk-reddit-threads`: `python3 scripts/thread_ledger.py --known <url>` before reading any thread; reuse the ledger's Manchester threads; real owner quotes with their URLs, or `NOT FETCHED — <barrier>`.
- [ ] **Step 3:** The Google AI Overview for the primary keyword, read free in the browser into `docs/research/manchester-page-run/ai-overview.md` (cited domains, the answer's claims, the GEO implication); a CAPTCHA is never bypassed — then it is `NOT FETCHED — Google served a challenge page`.
- [ ] **Step 4:** `npm run -s check:threads`. Commit `research(manchester): PAA, threads, owner language and the AI Overview (row 5)`.

### Task 7: LLM intel (row 5, step 5) — no new call

- [ ] **Step 1:** `@bsuk-llm-keyword-intel blue-staffy-puppies-manchester-uk` against the refreshed question file, from the banked `ai_engines.response.json`; writes `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-10-07.json`.
- [ ] **Step 2:** Commit `research(manchester): LLM intel against the question file (row 5)`.

### Task 8: Keyword deliverables (row 6)

- [ ] **Step 1:** `python3 scripts/keyword_variants.py blue-staffy-puppies-manchester-uk` (the four extra types) → `docs/research/manchester-page-run/keyword-variants.json`.
- [ ] **Step 2:** `python3 scripts/nlp_keywords.py blue-staffy-puppies-manchester-uk` (named entities, core concepts, semantic attributes, attested only).
- [ ] **Step 3:** Build `docs/research/manchester-page-run/keyword-universe.json`: every keyword with intent (transactional / commercial / informational / navigational / local), type (primary, secondary, similar, related, variation, question, co-occurring, neighbourhood) and volume from Task 5 or `NOT FETCHED — <barrier>`; and its distribution section by section, every keyword placed or parked with a reason.
- [ ] **Step 4:** Commit `research(manchester): keyword universe, variants and NLP terms (row 6)`.

### Task 9: Entities (row 7)

- [ ] **Step 1:** `python3 scripts/ontology_seed.py --check`; `@bsuk-entity-incorporation-agent` Move 2 for each planned section group → `docs/research/manchester-page-run/entities.md`, grouped by class, each from `data/bsuk-ontology.json` with its source (a new one `PROPOSED`).
- [ ] **Step 2:** Commit `research(manchester): entities and co-occurrence (row 7)`.

## Phase D: The research board (row 8, STOP 1)

### Task 10: The options

- [ ] **Step 1:** `@bsuk-angle-agent` → 3 angles with hooks (`angles.md`).
- [ ] **Step 2:** 2–3 strategy directions (`strategies.md`): Strategy A's Manchester row is one; `@bsuk-strategy-synthesizer` writes the alternatives; `python3 scripts/strategy_cite_check.py docs/research/manchester-page-run/strategies.md`.
- [ ] **Step 3:** Frameworks per section group (`frameworks.md`) from the `framework-*` skills, routed by `@bsuk-content-architect`.
- [ ] **Step 4:** Exactly one option per choice marked (Recommended), with its why from the research and its named trade-off (working rule 4). Commit.

### Task 11: Assemble and validate the record

- [ ] **Step 1:** Write `data/research-boards/blue-staffy-puppies-manchester-uk.json` with every section London's record carries: `serp`, `intent` (dominant, secondary, emotional, local), `reverse_engineering`, `universal_gaps`, `owner_language`, `fanout`, `why_competitors_rank`, `how_we_win`, `content_gap`, `entities`, `angles`, `strategies`, `frameworks`, `header_style`, `keywords`, `ai_overview`, `heading_types`, `serp_schema`, `authority`.
- [ ] **Step 2:** `python3 scripts/research_board.py blue-staffy-puppies-manchester-uk`. Expected: exit 0 and `docs/artifacts/research/blue-staffy-puppies-manchester-uk.{html,md}` written with all 19 sections.
- [ ] **Step 3:** Commit `research(manchester): the research board record and page (row 8)`.

### Task 12 (CONTROLLER): STOP 1

- [ ] **Step 1:** Publish `docs/artifacts/research/blue-staffy-puppies-manchester-uk.html` as an Artifact.
- [ ] **Step 2:** Write `docs/reference/answer-board/batches/2026-10-07-research-board-blue-staffy-puppies-manchester-uk.md` (angle, strategy, frameworks per group, header style, word band if no median, any open question), then `python3 scripts/answer_board_batch.py docs/reference/answer-board/batches/2026-10-07-research-board-blue-staffy-puppies-manchester-uk.md --project project-5 --batch-id 2026-10-07-research-board-blue-staffy-puppies-manchester-uk`.
- [ ] **Step 3:** Chat says only "N new questions on the board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf", and the turn ends.
- [ ] **Step 4:** On the user's Send: save the answers file, `python3 scripts/research_board.py blue-staffy-puppies-manchester-uk --approve --answers <file>`, commit.

### Task 13: Known Issue 99 (before STOP 3)

- [ ] **Step 1:** Measure the head-term counts (blue staffy, staffy puppies, Staffordshire Bull Terrier, city, UK) in `<main>` of Manchester's and London's saved top-5 competitor pages (`data/queries/cache/<slug>/*.html`).
- [ ] **Step 2:** Write a failing test in `tests/py/test_evidence_location_calibrated.py` that `budgets.location` has a `calibrated` date and that each ceiling equals the measured value in the calibration file.
- [ ] **Step 3:** Write the measurements to `docs/reports/ki99-location-calibration-2026-10-07.md`, set `budgets.location` and `calibrated` in `data/quality/evidence-budgets.json`, run the test to green, and revisit London's `budgets_by_slug` entry (delete it if the new ceilings cover London as built; `tests/py/test_evidence_london_budget.py` changes with it).
- [ ] **Step 4:** Commit `fix(evidence): calibrate the location term ceilings from competitor pages (Known Issue 99)`.

## Phase E: The outline (row 9, STOP 2) — written 2026-10-07 after STOP 1 (approval hash 3583bdc08a7bd609)

STOP 1 picks (`docs/reference/answer-board/answers/2026-10-07-research-board-blue-staffy-puppies-manchester-uk-2026-10-07.json`): M1 colour comes last; S2; every recommended framework (EEBP hero, PDB deposit and viewing, FAB litter and prices, FAB delivery, EEBP health and raising, QAB life in Manchester, QAB FAQ, AIDA contact); header Style 2 (Conversational Hybrid, FAQ register); blue stays primary for the H1, the for-sale family leads the title and the first 100 words; the keyword universe as shown; 2,000–3,000 words; no council link; colour and price said of this litter only; no rescue wording; the DNA FAQ pick kept, answered with the tests named and certificates on request (never a result); **no live video call on this page (q08 note)**.

### Task 14: Write the outline record from the picks
London's Task 18 command for command (`docs/superpowers/plans/2026-09-30-london-page-run.md`), slug `blue-staffy-puppies-manchester-uk`, with these values:
- `h1`: M1's question, "Should Colour Decide Which Blue Staffy Puppy Comes Home to Manchester?" (`h1-pick-is-final`).
- `word_target`: `{"min": 2000, "max": 3000, "source": "median NOT FETCHED — fewer than two prose competitor pages (1 used) in data/queries/blue-staffy-puppies-manchester-uk.json; the user's 2,000–3,000 band, STOP 1 q06 (2026-10-07)"}`.
- `header_style`: Style 2, Conversational Hybrid in the FAQ register: every H2 and H3 is a buyer question that also carries a keyword (STOP 1 q03).
- Body rows: exactly `section_target.total` (9), split across the builder's three gaps. M1's section order leads. The deposit and viewing section answers "see the puppy with its mother before any money changes hands" without a video call: the deposit books the viewing in Carlisle, reserves the puppy and comes off the price; the refund wording comes from `deposit_refund_clause`; payment is by bank transfer; the parents, papers and vet records are seen before the buyer commits (`data/faq.json` `whyus-evidence`). It never repeats a "see before you pay" rule we do not follow (lessons 9).
- The census has one H1 and all six levels, with at least 5 H5s and at least 5 H6s (hard FAIL on a project 5 location page, the user's ruling of 2026-09-30).
- FAQ: three blocks of the question file's picks (top, middle, bottom), 15–20 H3s in total, none repeating a body heading. The DNA pick stays (q11 b).
- No rescue wording anywhere (q10). Colour and price are said of this litter only (q09).
- Run `python3 scripts/outline_matrix.py blue-staffy-puppies-manchester-uk --check` until it exits 0, then commit.

### Task 15: Entities, internal links and external links
London's Task 19, with `docs/research/manchester-page-run/links-plan.md`. Internal anchors are never reused from another board for the same route, including London's. External links: six domains from four source types, no council page (STOP 1 q07), each live-checked. Then `python3 -m pytest -q tests/py/test_link_library.py tests/py/test_link_diversity.py` and the outline `--check`; commit.

### Task 16 (CONTROLLER): STOP 2
London's Task 20, with the batch `<date>-outline-blue-staffy-puppies-manchester-uk`. Before posting, read every piece of buyer advice in the outline against `data/settings.json`, the evidence ledger and the answer-board rulings (lessons 9).

## Phase F: Manchester's own components and its page board (row 10, STOP 3)

Row 10 runs after STOP 2 (outline approved 2026-10-07, hash 593992436b4531ab; research hash 3583bdc08a7bd609). It covers:
- Manchester's component design pass: a canvas with picks saved in its own database, like London's.
- The picks built into the kit.
- The page board, ending at STOP 3.

London's component pass (spec `docs/superpowers/specs/2026-09-27-london-component-design-pass-design.md`; plans `2026-09-27-london-component-design-pass.md` and `2026-09-28-london-component-build.md`) is the worked example. Only the differences are written here, with every command in full.

### Phase F rulings (bind every task below)

1. **Own components per page** (`rules/design.md` `own-components-per-page`). No section of Manchester's board names a London component: the twenty `city-*` ids in `data/design/components.json`, London's fifteen picks plus the five pieces inside sections.
   - Every Manchester pick differs from London's pick for the same component on at least two of layout, media, density and framing (`PB.city_pick_findings`, `city-pick-too-close`).
   - It also differs on at least two axes from every row of `data/design/city-must-differ.json` that a built page wears.
   - The board gate must print `own components: 2 new-family records judged` or more. A count of 1 means nothing was compared.
2. **The outline decides which components exist.** Manchester's 22 rows need 13 of the 15 city components:

   | Component | Outline rows |
   |---|---|
   | hero | §1 |
   | counter-strip | §2 |
   | trust-strip | §3 |
   | contents-list, desktop-dial, jump-links | §4 (22 sections, so all three mount) |
   | key-takeaways | §5 |
   | reviews | §6, §11, §20 |
   | faq-blocks | §7, §12, §21 (6 + 7 + 7 = 20 questions) |
   | image-text | the nine body sections |
   | tables | the G2 litter table under the H4 "Who Are the Three Boys and Three Girls in This Litter?" |
   | newsletter | §16 |
   | contact-form | §22 |

   - **`puppy-cards` is not used.** G2's table carries the six puppies, and no section is added to use a component.
   - **`video` is not used (Recommended, asked once in Task 26).**
     - Why: `data/settings.json` `youtube_embeds` holds three ids, and each already sits on its own page: `g9iV9RVr_Sk` on the breed guide, `g88qOo9C94c` on `/buy-staffy-puppies-for-sale-uk/`, `fXhu9jDS6CA` on `/blue-staffy-uk-breeders/`. Working rule 14 keeps a video where a page already had one, and Manchester's 5-word stub had none. The approved outline has no video row, and its schema note says "no VideoObject unless a youtube_embeds id is placed at STOP 3".
     - Trade-off: the page gets no video-search surface.
     - If the user picks (b), `g88qOo9C94c` ("our blue Staffy puppies on film") goes under G2's H2 as a click-to-play facade. That means three `video` variants on the canvas (facade first), a `VideoObject`, and `bsuk-video-seo-agent` at row 12.
3. **Hero and counter: three new designs each, from the breeder's idea sheets** (working rule 16), in `/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Components-Ideas/`.
   - London's heroes used `hero-idea-1.png`, `hero-idea.png` and `hero-idea00.png`. Manchester's three take their ideas from `hero-idea-3.png`, `hero-idea-5.png`, `hero-idea66.png`, `hero-idea77.png` and `comparison-hero-idea1.png`.
   - Each counter variant cites at least one sheet from that folder that shows figures. London's counters cited none of the breeder's sheets.
   - Neither component offers a pool variant.
4. **Pool variants versus new designs** (`data/design/city-pool.json`, 30 London variants).
   - For each of the other 11 components, variant `c` may be a refreshed pool variant. The rest are new.
   - A pool variant is copied into `design/city-canvas/manchester/<component>/c.html`, rewritten with Manchester copy and given one named refresh delta on a non-palette axis.
   - Its `meta.json` row records `"from_pool": "london/<component>/<v>"`.
   - It goes through the same validator, smoke test and both design skills as a new design.
   - Use the pool variant whose axes are furthest from London's pick and whose layout suits Manchester's outline. If neither London pool variant suits the section (for example, a layout built around London's video call), `c` is new and the meta says why.
   - (Recommended.) Why: pool variants have already passed frontend-design, impeccable, the canvas smoke test and the must-differ check, so they cost less than a fresh design. Trade-off: they were drawn for London's content, so the refresh delta has to be real, not a copy change.
5. **Tables** (working rule 13): three variants at 1280/768/375.
   - Every `<td>` carries a `data-label`, and every table stacks into labelled rows below 640px (`.stack-table`).
   - The caption is the outline's "This litter: each puppy, sex, coat and price".
   - At least one variant carries each pup's own photo in its row (Known Issue 100: the breeder missed the pup photos on London's cards).
6. **Type fits every tier.** London ruling 10 holds: no big or chunky headings, no tall sections or paragraphs.
   - Enforced on the canvas by `layout-min-font-size` and `layout-no-horizontal-overflow`.
   - Enforced on the built components by `tests/render/lib/cityTypeFit.ts`, `cityTiers.ts` and `cityLayoutFollowsBox.ts`. Every component root carries `city-kit`.
   - The hero band is 390–450px at 1024px and up, with the photo first on phones (`rules/design.md` rule 10).
7. **Image bleed in design colours.** Every colour is a `var(--…)` token: the canvas validator's colour rule refuses hex, `rgb()` and black/white/grey. Letterbox and contain areas are bone (`--color-surface`, `--counter-bed`). Photos are baked with Style A at the Asset Gate.
8. **A refresh delta on every section.** Each board section carries `refresh: {axis, note}`, with axis one of layout, accent, motif, container or density, never the palette. The note names which sibling or London section it departs from. The three review slots, the three FAQ blocks and the nine body sections each differ from their siblings on this page, for example photo side alternating, accent role or density.
9. **Visual companion, always.** Every visual choice is shown in the browser: the canvas, the side-by-side and the board. Text-only questions go to the answer board.
10. **Facts from data only.** Prices, the deposit and its clause (`deposit_refund_clause`, never plainly "refundable"), the delivery band, the guarantee label and cover, puppy names and statuses. Also: no video call (STOP 1 q08), no rescue wording (q10), no licence claim, colour and price said of this litter only (q09), no "Manchester" added to an anchor or FAQ heading (q12). Placeholder copy on the canvas is about Manchester and states only those facts.
11. **Every image with words is read as copy** before it reaches a board (lessons 7), and every alt is checked against its picture (lessons 8, at STOP 4).

### Tooling gaps found while writing this phase (each fixed test-first in the task named)

| # | Gap (file:line as of f0133373) | Smallest fix | Task |
|---|---|---|---|
| G1 | `scripts/check_city_canvas.py:428` refuses any fragment without the word "London". `IDEAS_INDEX` (line 66) and the must-differ message point at `london-components/`. With no `--city`, `check:canvas` in `check:all` validates London only. | The copy rule reads the canvas key, title-cased ("Manchester"). Add `ideas_index(city)` → `docs/research/<city>-components/ideas-index.md`. With no arguments, validate every city that has a picks record, against its non-`none` picks. Add a new rule: hero and counter variants cite at least one `Components-Ideas` sheet. | 18 |
| G2 | London's 15 picks are not rows in `data/design/city-must-differ.json`. The inventory reads only `boardStyles.ts` style picks, and city sections carry components, not picks. A variant one axis from London's pick passes the canvas and fails at the gate after the user picked it. | `scripts/city_must_differ.py` `inventory()` adds one row per city pick: `shape: "city"`, `id: london/hero/b`, axes from that canvas's meta, `used_by: [slug]`. The validator skips rows whose id starts with its own city. `PB.city_pick_findings` skips `shape == "city"` rows, which `city-pick-too-close` already covers. The `.md` title becomes "the city component design passes". | 18 |
| G3 | `scripts/build_component_canvas.py:37,249-255` (TITLE and header) and `scripts/component_canvas_client.js:181,213` ("London component picks", "London canvas picks") are hard-coded. | `--city` sets the title, eyebrow and lede. The body carries `data-city="<Name>"`, which the client reads. | 18 |
| G4 | `schemas/city-picks.schema.json` requires 15 `<city>/<comp>/<v>` values, and `freeze_city_picks.py` refuses any missing pick. Manchester has no video or puppy-card section (lesson 12: the record must be able to hold every answer). | The value `"none"` is allowed, and `freeze_city_picks.py --not-used video,puppy-cards` writes it. `city_pick_findings` and `board_approve.city_tuple` skip it, and the gate fails a board that mounts a component its picks mark `none`. | 19 |
| G5 | `picks_record()` always names `<canvas>/…`, and `city_pick_findings` (pageboard.py:1843) refuses a pick from another city's canvas. So a pool variant cannot be picked as itself. | Pool variants enter as `from_pool` copies (ruling 4). `pooled()` removes the `from_pool` source when its copy is picked, and never adds an unpicked `from_pool` copy to the pool. | 19 |
| G6 | `scripts/neighbourhoods.py` has a London-only gazetteer (32 boroughs, compass areas, districts) and reads only a DataForSEO `neighbourhood_keywords.response.json`. Manchester has `docs/research/manchester-page-run/free-keyword-signals.json` instead (Planner ranges plus autocomplete). Block 3d would show London boroughs on Manchester's board. | One gazetteer per city, chosen by `original_slots.own_city(board)`. Greater Manchester: the ten boroughs, "City of Manchester" and "manchester city centre" (bare "manchester" is the page's city, not an area), compass areas, a test-pinned district → borough map, and ambiguity rules. A reader for `keyword_planner.runs[].rows[]` shows each `avg_monthly_searches_range` as recorded (never narrowed) and applies the use rule to the range's lower bound. Autocomplete phrases are shown as "attested, no volume". "London" in labels becomes the city. | 20 |
| G7 | `scripts/serp_reading.py:69` `GENERIC` holds "london" but not the board's own city, which inflates heading overlap in block 1b. | Add the lower-cased `own_city(board)` to the generic set per board. | 20 |
| G8 | `scripts/image_candidates.py` still offers photos named for another city on a location board (board v3 follow-up, still open). A Manchester board would be offered London's photos. | `candidates()` drops a served or own photo whose stem or alt names a city other than the board's, through `original_slots.cities_named` (lazy import, because `original_slots` imports `image_candidates`). | 20 |
| G9 | `PB.component_findings` (pageboard.py:1760) compares only `sections[].component`, not the pieces inside sections. | Subcomponent rows get an optional `component` (`schemas/board.schema.json`), included in `shared_section_components`. London's five rows back-fill their kit ids. | 19 |
| G10 | `scripts/city_side_by_side.mjs:37-41` compares all `project: 5` rows (20 today) with the picks (15) and exits 1 already. `ROOT_SELECTOR` lists London's files only. | Each picked row in `components.json` gets `canvas_variant` and `root_selector` (London back-filled). The script selects rows whose `canvas_variant` is one of the city's picks, and reads the selector from the row. | 32 |
| G11 | `/kit-preview/city/` is London's (it imports London's places; the nav set is one per page). `tests/render/city-kit.spec.ts:28` `ROUTES` lists London only. | A new route `src/pages/kit-preview/city-manchester.astro`, plus it and the Manchester route in `ROUTES`/`BOARDS`. | 28 |
| G12 | `cityTypeFit.ts:95` `skipRoot` names London's nav hooks (`data-city-jump-stepper`, `data-city-dial-photo-marker`). | A shared `data-city-nav` attribute on every city's nav furniture, with `skipRoot` matching it. London's two nav components gain the attribute too. | 29 |
| G13 | `npm run test:render:canvas` emits `london-frames` only. | No code change: emit `manchester-frames` and run the smoke test with `CANVAS_FRAMES_INDEX` (already read at `canvas.spec.ts:26`). | 22 |
| G14 | Readability Option 2 summaries stored in the board record are hashed (`PB.record_hash`), so adding them after STOP 3 makes the approval stale. | Summaries for a page board live in a sidecar, `data/boards/summaries/<slug>.json`, outside the hash. (Recommended; trade-off: one more file per board.) | 36 |
| G15 | STOP 2 q03 asks for proper rewording, but the existing collision gate already passes the three thin wordings. There is no near-copy check. | `PB.near_copy_hits(questions, live)` compares content-token sets after `PB.tokens()`, dropping `KM.STOP` and pronouns. A hit when the symmetric difference is 2 or fewer. A WARN on the board, pinned to zero for Manchester by its test. | 34 |
| G16 | `city_components.KIT_OF_VARIANT` maps London's variants only, and `board_approve.city_tuple` raises without it. | Add Manchester's entries at the freeze (Task 27). | 27 |

### Task 17: Pre-flight (the gates are open; the side tasks are known)

**Files:** none (read-only).

- [ ] **Step 1:** Check the outline gate and the branch.

  ```bash
  python3 -c "import sys;sys.path.insert(0,'scripts');import outline_matrix as OM;print(OM.approval_refusal('blue-staffy-puppies-manchester-uk'))"
  ```
  Expected: `None`. Then `git branch --show-current`, expected `manchester-page`.
- [ ] **Step 2:** Check Known Issue 99 option (a).

  ```bash
  git log --oneline -1 -- tests/py/test_evidence_location_density.py scripts/evidence_audit.py data/quality/evidence-budgets.json
  python3 -m pytest -q tests/py/test_evidence_location_density.py
  ```
  Expected: a commit on `manchester-page` and all tests passing. If the files are still uncommitted, another session owns them. Do not stage them. Log "KI 99 uncommitted at Phase F start" under `## Open Flags` in the session brief. STOP 3 does not start until they are committed.
- [ ] **Step 3:** Check the STOP 2 side tasks.

  ```bash
  grep -n "deposit comes after you have met\|video call before the deposit\|on a video call we offer before the deposit" src/pages/buy-blue-staffy-puppies-uk/index.astro src/pages/blue-staffy-pup-sale-uk/index.astro
  ```
  Expected while the deposit-order fix (q05) has not landed: hits. Record the result for Task 35, which marks links 8 and 9 as held. Also record whether the FAQ-bank fix (q06) has landed: `git log --oneline -3 -- data/faq.json`.
- [ ] **Step 4:** `test -f scripts/board_style.py && echo present || echo absent`. Record the result for Task 36.

### Task 18: The canvas tools take any city (gaps G1, G2, G3). Tests first.

**Files:**
- Modify: `scripts/check_city_canvas.py`, `scripts/build_component_canvas.py`, `scripts/component_canvas_client.js`, `scripts/city_must_differ.py`, `scripts/pageboard.py` (`city_pick_findings` only)
- Regenerate: `data/design/city-must-differ.json`, `docs/research/london-components/must-differ.md`
- Test: `tests/py/test_check_city_canvas.py`, `tests/py/test_build_component_canvas.py`, `tests/py/test_city_must_differ.py`

- [ ] **Step 1: Write the failing tests.**
  - `test_check_city_canvas.py`:
    - A fragment for `--city manchester` that says "Manchester" and not "London" passes the copy rule; one that names no city fails with `copy: no mention of Manchester`.
    - `ideas_index("manchester")` is `docs/research/manchester-components/ideas-index.md`.
    - A hero or counter-strip meta row with no `…/Assets/Components-Ideas/…` idea source fails with `meta a: hero/counter cite a breeder idea sheet (working rule 16)`.
    - A Manchester variant within one axis of `london/hero/b`'s axes fails with `within one axis of existing style london/hero/b`.
    - A London variant is never compared with London's own pick rows.
    - With no arguments, `main()` validates every city in `data/design/city-picks/` (today, London: `examined 45 fragments, 15 meta files; 0 problems`).
  - `test_city_must_differ.py`: `inventory()` holds one `shape: "city"` row per London pick, with `used_by == ["blue-staffy-puppies-london"]`; `--check` is fresh after a regenerate.
  - `test_build_component_canvas.py`: `render_page(..., city="manchester")` has `<title>Manchester Component Canvas</title>` and `data-city="Manchester"`, and contains no "London". The client's copy text reads "Manchester component picks".
  - `test_freeze_city_picks.py::test_the_real_london_freeze_is_on_disk_and_passes_the_city_gate` stays green once city rows exist (`city_pick_findings` skips `shape == "city"`).

  Run `python3 -m pytest -q tests/py/test_check_city_canvas.py tests/py/test_build_component_canvas.py tests/py/test_city_must_differ.py tests/py/test_freeze_city_picks.py`. Expected: the new tests FAIL.
- [ ] **Step 2: Implement G1–G3** as described in the gap table.
- [ ] **Step 3:** Run `python3 scripts/city_must_differ.py`, then the Step 1 command (expected: all pass), then `npm run -s check:canvas` (expected: `check-city-canvas london: examined 45 fragments, 15 meta files; 0 problems`), then `python3 scripts/build_system_registry.py`.
- [ ] **Step 4: Commit.** Message: `feat(canvas): the city canvas tools take any city; other cities' picks join the must-differ table (G1–G3)`. Stage `scripts/check_city_canvas.py scripts/build_component_canvas.py scripts/component_canvas_client.js scripts/city_must_differ.py scripts/pageboard.py data/design/city-must-differ.json docs/research/london-components/must-differ.md docs/reference/system-registry.md tests/py/test_check_city_canvas.py tests/py/test_build_component_canvas.py tests/py/test_city_must_differ.py`. Trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

### Task 19: Picks that a page does not use, pool copies, and pieces inside sections (G4, G5, G9). Tests first.

Runs after Task 18 (both touch `scripts/pageboard.py`).

**Files:**
- Modify: `schemas/city-picks.schema.json`, `scripts/freeze_city_picks.py`, `scripts/pageboard.py`, `scripts/board_approve.py`, `schemas/board.schema.json` (subcomponent `component`), `data/boards/blue-staffy-puppies-london.json` (back-fill its five subcomponent `component` ids; the approval stays valid only if `record_hash` is unaffected, otherwise see the note below)
- Test: `tests/py/test_freeze_city_picks.py`, `tests/py/test_city_uniqueness_gate.py`, `tests/py/test_rule16_gate.py`

- [ ] **Step 1: Write the failing tests.**
  - `F.picks_record(snap, slug=…, canvas="leeds", not_used=("video","puppy-cards"))` writes `"video": "none"`, and the schema validates it.
  - A `redesign` value still refuses.
  - `pooled()` with a picked variant whose meta says `from_pool: london/hero/a` removes `london/hero/a`.
  - An unpicked `from_pool` copy never enters the pool.
  - `city_pick_findings` ignores `none`.
  - `board_approve.city_tuple` raises on a board that mounts a component its picks mark `none`.
  - Two new-family boards whose subcomponents carry the same `component` FAIL `component-shared`.
- [ ] **Step 2: Implement.**
  - `--not-used` reads a comma list.
  - The `from_pool` source is read from `design/city-canvas/<canvas>/<comp>/meta.json`.
  - `shared_section_components` adds `subcomponents[].component`.
  - **London's record hash.** London is approved, so back-filling its five subcomponent ids changes its `record_hash`. Smallest safe path: make the subcomponent `component` default to the `KIT_OF_SUBCOMPONENT` map in `city_components.py`, keyed by board slug and subcomponent id, instead of editing London's record. Pin it with a test that London's `approval_matches()` is still True.
- [ ] **Step 3:** `python3 -m pytest -q tests/py/test_freeze_city_picks.py tests/py/test_city_uniqueness_gate.py tests/py/test_rule16_gate.py tests/py/test_city_board.py`. Expected: all pass. Then `npm run -s build && python3 scripts/board_gate.py blue-staffy-puppies-london; echo "exit $?"`. Expected: exit 0, as before.
- [ ] **Step 4: Commit.** Message: `feat(city-gate): a page may leave a component unused; pool copies leave the pool; pieces inside sections are judged (G4, G5, G9)`.

### Task 20: Board blocks for a second city (G6, G7, G8). Tests first. Runs in parallel with Task 18.

**Files:**
- Modify: `scripts/neighbourhoods.py`, `scripts/serp_reading.py`, `scripts/image_candidates.py`
- Test: `tests/py/test_neighbourhoods.py`, `tests/py/test_serp_reading.py`, `tests/py/test_image_candidates.py`

- [ ] **Step 1: Write the failing tests.**
  - **Gazetteer.**
    - Greater Manchester's gazetteer holds Bolton, Bury, Oldham, Rochdale, Salford, Stockport, Tameside, Trafford, Wigan and "City of Manchester".
    - Bare "manchester" is never an area.
    - `lookup("staffy puppies for sale manchester") == []`: "sale" counts as the town of Sale only after a location word (in, near, around, from, to) and never in "for sale".
    - "bury" counts only as a place after a location word or beside "manchester"/"greater manchester".
    - "Leigh-on-Sea" is outside.
    - Districts map to their borough, for example Altrincham → Trafford, Stalybridge → Tameside, Cheadle → Stockport, Eccles → Salford, Wythenshawe → City of Manchester.
  - **Volumes and labels.**
    - On Manchester's board, volumes come from `free-keyword-signals.json` Planner rows, shown exactly as recorded (e.g. `100 – 1K`), and the use rule reads the lower bound.
    - Autocomplete phrases appear as "attested, no volume".
    - The block says "Greater Manchester" and never "London borough".
    - London's block renders byte-for-byte as before (a golden test on London's board).
  - **SERP reading.** `serp_reading` treats "manchester" as generic on Manchester's board.
  - **Image candidates.** `image_candidates.candidates(manchester_board)` offers no file whose stem or alt names London, Glasgow or another city, but keeps `victoria-family-blue-staffy-manchester.webp`.
- [ ] **Step 2: Implement** as in the gap table. Each gazetteer holds names only, never volumes.
- [ ] **Step 3:** `python3 -m pytest -q tests/py/test_neighbourhoods.py tests/py/test_serp_reading.py tests/py/test_image_candidates.py tests/py/test_family_rules_on_board.py`. Expected: all pass.
- [ ] **Step 4: Commit.** Message: `feat(board): block 3d, 1b and the photo picker read a page's own city (G6–G8)`.

### Task 21: Manchester's ideas index and the design brief

**Files:**
- Create: `docs/research/manchester-components/README.md`, `docs/research/manchester-components/ideas-index.md`, `docs/research/manchester-components/hardening-log.md` (header only)
- Modify: `tests/py/test_city_ideas_index.py` (parametrise by city)

- [ ] **Step 1:** Open every sheet in `/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Components-Ideas/` (42 PNGs) with the Read tool, plus London's captures under `/Users/apple/Downloads/BSUK/BSUK-refs/london/`. Write `ideas-index.md` in London's format: 13 sections in city-page order (no `video`, no `puppy-cards`), one line of idea per cited file, and a "Sheets not used" section.
  - Hero cites `hero-idea-3.png`, `hero-idea-5.png`, `hero-idea66.png`, `hero-idea77.png`, `comparison-hero-idea1.png`.
  - Counter-strip cites the breeder sheets that show figures (say which, after opening them).
  - Each other component lists its two pool variants (`london/<comp>/<v>`) with their names and axes from London's meta.
- [ ] **Step 2:** In `README.md`, write:
  - the 13-component scope and the two not used, with the video why from Phase F ruling 2;
  - the pool rule (ruling 4);
  - the variant contract (London Plan 1 "The variant contract", unchanged except the copy names Manchester and states only Phase F ruling 10's facts);
  - the served Manchester photos: `reputable-blue-staffy-breeder-manchester-pup.webp`, `victoria-family-blue-staffy-manchester.webp`, `victoria-family-blue-staffy-manchester-440.webp`, the parent photos and `src/assets/puppies/*`;
  - London's picked axes, which every new variant differs from (from `data/design/city-must-differ.json` `shape: "city"` rows).
- [ ] **Step 3:** `python3 -m pytest -q tests/py/test_city_ideas_index.py`. Expected: pass for London and Manchester. Commit: `docs(manchester): ideas index and component brief (row 10)`.

### Tasks 22–25: Design the variants (39), three or four components per task

One Opus implementer per task, run in order (they share `hardening-log.md`). Every task has the same steps; the batches are:

| Task | Components | Pool slot `c` |
|---|---|---|
| 22 | hero, counter-strip, trust-strip | trust-strip only (hero and counter are three new designs from the breeder's sheets) |
| 23 | contents-list, desktop-dial, jump-links | each |
| 24 | key-takeaways, tables, image-text | each (tables: one of the three carries pup photos, ruling 5) |
| 25 | reviews, faq-blocks, newsletter, contact-form | each |

Steps per task:
- [ ] **Step 1: Read the design context first** (`rules/gates.md` `design-context-read-first`):
  - `rules/design.md`, `src/styles/tokens.css`, `src/styles/global.css`, `src/styles/city.css`, `data/design/contrast.json`, `rules/headings.md`;
  - Phase F rulings and the README of Task 21;
  - the batch's sections of `ideas-index.md` and `docs/research/london-components/must-differ.md`;
  - every cited sheet, opened with the Read tool;
  - the outline rows the components serve, in `data/outlines/blue-staffy-puppies-manchester-uk.json`.
- [ ] **Step 2:** Invoke the Skill tool with skill `frontend-design:frontend-design` and these args (substitute the batch's components):

  > Design three variants each of <components> for BlueStaffyUK's Manchester city page as HTML fragments under design/city-canvas/manchester/<component>/{a,b,c}.html, on the real tokens in src/styles/tokens.css only. Contract: docs/research/manchester-components/README.md and London Plan 1 'The variant contract'. Ideas: docs/research/manchester-components/ideas-index.md. Each variant differs on two or more of layout/media/density/framing from its siblings, from every row of data/design/city-must-differ.json for its component, and from London's pick. Phone first, type fits every tier, tables stack below 640px, bleeds in bone or steel tokens only, headings are buyer questions in Title Case answered by a conversational opening paragraph of 12+ words. Variant c of <pool components> is the pool variant <key>, refreshed on one named non-palette axis with Manchester copy.

  Write the fragments and one `meta.json` per component: `name`, `description`, `idea_sources`, `differs_from`, `axes`, and `from_pool` on a pool copy.
- [ ] **Step 3:** `python3 scripts/check_city_canvas.py --city manchester --only <comma list>`. Expected: `check-city-canvas manchester: examined <3n> fragments, <n> meta files; 0 problems`.
- [ ] **Step 4:** Run the smoke test.

  ```bash
  python3 scripts/build_component_canvas.py --city manchester --emit-frames docs/artifacts/canvas/manchester-frames
  CANVAS_FRAMES_INDEX=docs/artifacts/canvas/manchester-frames/index.json npx playwright test -c tests/render/canvas.config.ts
  ```
  Expected: the frames line, then every test passed at vp375, vp768 and vp1280.
- [ ] **Step 5:** Invoke the Skill tool with skill `impeccable:impeccable` and these args:

  > Critique and harden design/city-canvas/manchester/<components> (frames in docs/artifacts/canvas/manchester-frames/) at 375, 768 and 1280 in a painting browser: hierarchy, type fit per tier, tap targets, focus rings, contrast, image boxes reserved, bleeds in design colours, no invented fact.

  Fix every finding in the fragment, then re-run Steps 3–4.
- [ ] **Step 6:** Append to `docs/research/manchester-components/hardening-log.md` under `## Task <n>`: each skill's findings and what changed.
- [ ] **Step 7: Commit** `design/city-canvas/manchester/<components>/` and the log. Message: `design(manchester): <components> — three variants each, hardened (row 10)`.

### Task 26 (CONTROLLER): Publish the canvas and wait for the picks

**Files:** Create `docs/artifacts/bsuk-manchester-component-canvas.html` and the batch pair `docs/reference/answer-board/batches/${D}-component-canvas-blue-staffy-puppies-manchester-uk.{md,json}`; modify `data/design/artifacts.json` (`manchester_component_canvas`) and `docs/research/manchester-components/README.md` (the URL).

- [ ] **Step 1: Prove the canvas complete.**

  ```bash
  python3 scripts/check_city_canvas.py --city manchester --only hero,counter-strip,trust-strip,contents-list,desktop-dial,jump-links,key-takeaways,tables,image-text,reviews,faq-blocks,newsletter,contact-form
  ```
  Expected: `examined 39 fragments, 13 meta files; 0 problems`. Then re-run the Task 22 Step 4 smoke. Expected: all passed.
- [ ] **Step 2: Build the page.**

  ```bash
  D=$(date +%F)
  python3 scripts/build_component_canvas.py --city manchester --allow-partial --files-map docs/artifacts/canvas/manchester-files.json
  ```
  Expected: `docs/artifacts/bsuk-manchester-component-canvas.html — <bytes> bytes, 39 variants`.
- [ ] **Step 3:** Invoke `artifact-design` and `artifact-capabilities`. Read the page in full. Publish with:
  - icon `layout`;
  - description "Thirteen Manchester page components, three designs each, to pick from.";
  - `capabilities={"db": {"rules": [{"path": "", "read": "admin", "write": "admin"}]}, "comments": {}}`;
  - `files` from `manchester-files.json`.

  Then:
  - Run the database check: ArtifactData `set`/`get`/`delete` of `picks/_controller-check`.
  - Open the canvas at phone and desktop widths. If a frame's image is missing, rebuild with `--inline-images` and republish to the same URL.
  - Confirm the watch with a bare ArtifactComments `watch`.
- [ ] **Step 4: Post the batch.** Two questions, both linking to the canvas:
  1. "Have you picked A, B or C for each of the thirteen components on the Manchester canvas?" (a) Picked and sent · (b) Redesign some (say which in the text box).
  2. "Should Manchester's page carry one of our YouTube videos?"
     - (a) No video (Recommended). Why: the stub had none; each of our three videos already sits on its own page; the approved outline has no video row. Trade-off: no video-search result for this page.
     - (b) Place 'our blue Staffy puppies on film' (`g88qOo9C94c`) as a tap-to-play facade under the litter section.

  Run `python3 scripts/answer_board_batch.py docs/reference/answer-board/batches/${D}-component-canvas-blue-staffy-puppies-manchester-uk.md --project project-5 --batch-id ${D}-component-canvas-blue-staffy-puppies-manchester-uk`, ArtifactData `set`, and commit the canvas page, the batch pair, `artifacts.json` and the README. Chat says only "2 new questions on the board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf". **End the turn.**
- [ ] **Step 5: On the Send.**
  - Save the answers pair.
  - ArtifactData `list` the canvas's `submissions`, newest first, and save the snapshot as `docs/research/manchester-components/picks-${D}.json` with a readable `.md`.
  - For each "redesign", repeat Tasks 22–25's steps for that component only, with the user's note as the frontend-design brief, then rebuild and republish to the same URL.
  - If q2 is (b), design three `video` variants (facade first; `data-play` hook; `scripts/check_city_canvas.py --only video`) and republish the canvas for that one pick.

### Task 27: Freeze the picks (G16)

**Files:** Create `data/design/city-picks/blue-staffy-puppies-manchester-uk.json`; modify `data/design/city-pool.json`, `scripts/city_components.py` (`KIT_OF_VARIANT`), `docs/artifacts/bsuk-manchester-component-canvas.html` (rebuilt `--final`).

- [ ] **Step 1:** Freeze.

  ```bash
  python3 scripts/freeze_city_picks.py --snapshot docs/research/manchester-components/picks-${D}.json --slug blue-staffy-puppies-manchester-uk --canvas manchester --not-used video,puppy-cards
  ```
  Use `--not-used puppy-cards` alone if q2 was (b). Expected: exit 0. The pool now holds `30 − (pool sources picked) + (26 − unpicked pool copies)` entries.
- [ ] **Step 2:** Add the 13 `manchester/<comp>/<v>` → kit id entries to `KIT_OF_VARIANT`. Each kit id is `city-<name of the picked variant, slugified>`, and none may equal an existing `city-*` id. Add a test in `tests/py/test_city_uniqueness_gate.py` that no Manchester kit id is one of London's.
- [ ] **Step 3:** `python3 -m pytest -q tests/py/test_freeze_city_picks.py tests/py/test_city_uniqueness_gate.py`. Expected: all pass. Then:

  ```bash
  python3 -c "import sys;sys.path.insert(0,'scripts');import pageboard as PB,json;p=PB.load_city_picks();md=json.load(open(PB.CITY_MUST_DIFFER))['components'];print(PB.city_pick_findings('blue-staffy-puppies-manchester-uk',p,md,PB.canvas_axes), PB.city_pool_findings(PB.load_city_pool(),p,PB.canvas_axes))"
  ```
  Expected: `[] []`.
- [ ] **Step 4 (CONTROLLER):** `python3 scripts/build_component_canvas.py --city manchester --allow-partial --final`, republish to the same URL, then commit: `design(manchester): picks frozen, pool updated, canvas final`.

### Tasks 28–31: Build the picks into the kit (London Plan 2 Tasks 2–6, Manchester's picks)

| Task | Components | Also |
|---|---|---|
| 28 | hero, counter-strip, trust-strip | `src/pages/kit-preview/city-manchester.astro`; `tests/render/city-kit.spec.ts` `ROUTES` gains it (G11) |
| 29 | contents-list, desktop-dial, jump-links (`CityNavSet` for CityShell) | the `data-city-nav` hook and `cityTypeFit.ts` `skipRoot` (G12), with London's two nav components gaining the attribute |
| 30 | key-takeaways, tables, image-text | the table's `.stack-table` with `data-label`; the table's pup photos from `data/puppies.json` `card_photo` |
| 31 | reviews, faq-blocks, newsletter, contact-form | `form_contract_audit.py` classes the newsletter |

Steps per task:
- [ ] **Step 1: Tests first.** In `tests/py/test_city_kit_manchester.py`, write per component:
  - a `data/design/components.json` row (`project: 5`, `canvas_variant`, `root_selector`);
  - a `_registry.ts` entry;
  - the root carries `city-kit`;
  - every fact comes from `src/lib/cityKit.ts` or a data file, never a typed price;
  - for the hero, the photo comes before the H1 in source;
  - the component is rendered on `dist/kit-preview/city-manchester/index.html`.

  Also add the component's probe to `tests/render/city-kit.spec.ts`. Run them. Expected: FAIL.
- [ ] **Step 2:** Build `src/components/kit/City<Name>.astro` from the picked fragment, under London Plan 2's execution notes 11–13: never port `data-canvas-only`, inline style values or typed figures. The component must not import or copy any London City component file.
- [ ] **Step 3:** `npm run -s build`, then `python3 -m pytest -q tests/py/test_city_kit_manchester.py tests/py/test_city_kit.py tests/py/test_design_components.py`, then `npm run test:render:city`. Expected: exit 0 and all passed, with London's routes unchanged.
- [ ] **Step 4:** Invoke `frontend-design:frontend-design`, then `impeccable:impeccable`, on the built components: `CITY_SHOTS=/Users/apple/Downloads/BSUK/BSUK-refs/manchester/_build-shots npm run test:render:city` writes the four-width shots. Fix each finding, and append to `hardening-log.md` under `## Built — Task <n>`.
- [ ] **Step 5:** `python3 scripts/build_system_registry.py`, then commit the components, rows, registry, preview, tests and log. Message: `feat(manchester-kit): <components> built from the frozen picks`.

### Task 32: Manchester's own route (a noindex scaffold) and the side-by-side (G10)

**Files:**
- Create: `src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro` (CityShell; the 13 picks; headings and sections from the approved outline; figures from data; each body section's prose a marked scaffold line; `noindex, follow`; `data-city-scaffold`)
- Modify: `scripts/city_side_by_side.mjs`, `data/design/components.json` (London's back-fill: `canvas_variant`, `root_selector`)
- Create: `tests/py/test_manchester_scaffold.py`, `docs/artifacts/bsuk-manchester-side-by-side.html`

- [ ] **Step 1: Tests first.**
  - `[slug].astro` no longer builds Manchester; the other 26 cities still build.
  - The scaffold is noindex and in no sitemap shard.
  - Every component on it is one of Manchester's picks, and no London `city-*` root class appears.
  - The FAQPage node equals the visible questions.
- [ ] **Step 2:** Commit the page file first (the prebuild dates routes from history), then `npm run -s build`, then commit `data/page-dates.json` and the `docs/reports/{redirects,schema,sitemaps}.md` the build rewrites.
- [ ] **Step 3:** Fix G10.

  ```bash
  node scripts/city_side_by_side.mjs --city manchester --slug blue-staffy-puppies-manchester-uk
  node scripts/city_side_by_side.mjs --city london --slug blue-staffy-puppies-london
  ```
  Expected: Manchester writes 13 pairs and `docs/artifacts/bsuk-manchester-side-by-side.html`. London exits 0 again (it exits 1 today).
- [ ] **Step 4:** `python3 -m pytest -q tests/py/test_manchester_scaffold.py tests/py/test_city_scaffold.py tests/py/test_page_dates.py`. Expected: pass. Commit: `feat(manchester): own route as a noindex scaffold; side-by-side of canvas against build`.

### Task 33 (CONTROLLER): Publish the side-by-side

- [ ] Read `docs/artifacts/bsuk-manchester-side-by-side.html` in full. Publish it, with `files` from `docs/artifacts/canvas/side-by-side/manchester/files.json`. Add `manchester_side_by_side` to `data/design/artifacts.json` and commit. The user judges it at STOP 3 (Task 38, q3), not as a stop of its own.

### Task 34: The three thin FAQ wordings, reworded properly (STOP 2 q03 (b); G15). Tests first.

**Files:** Modify `scripts/pageboard.py` (`near_copy_hits`; a WARN in block 3); create `tests/py/test_faq_near_copy.py`; create `docs/research/manchester-components/faq-rewordings.md`.

- [ ] **Step 1: Failing test.** `near_copy_hits` returns a hit for each of the outline's three page wordings against the live corpus (`PB.live_headings()` plus every board's `faq_block_questions` plus `data/faq.json` questions):
  - "How Much Is Your Deposit?" against "How Much Is the Deposit?";
  - "Do You Deliver Puppies Across the UK?" against "Do You Deliver Across the UK?";
  - "Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?" against London's and the health page's L-2-HGA/HC-HSF4 headings.

  It returns no hit for "How Much Is the Deposit?" against an unrelated corpus.
- [ ] **Step 2:** Implement. The new wording must keep the pick's search phrase and meaning (the builder rule in `faq_rewordings`). Check each candidate with `PB.header_precheck`, `PB.faq_hits`, `near_copy_hits` and a within-page repeat check, then write `faq-rewordings.md` with three options per question, one marked (Recommended):
  - **Top, `q-how-much-is-the-deposit-2cce23`.**
    - (Recommended) "How Much Deposit Reserves One of Your Puppies?" Keeps "how much … deposit". The answer comes from `deposit_gbp` and `deposit_refund_clause` and never says plainly "refundable".
    - "How Much Do I Pay as a Deposit Up Front?"
    - "What Deposit Holds a Blue Staffy Puppy for Me?"
  - **Top, `q-do-you-deliver-across-the-uk-fb0c4a`.**
    - (Recommended) "Which Parts of the UK Do You Deliver Puppies To?" Asks about reach and so stays apart from the same block's "Can My Blue Staffy Puppy Be Delivered to My Home?".
    - "Is Home Delivery Available Anywhere in the UK?"
    - "Can You Deliver a Puppy to Any UK Address?"
  - **Middle, the DNA pick.**
    - (a) Keeps "clear" and the meaning unchanged: "Is Each Parent DNA Tested Clear of L-2-HGA, Then of HC-HSF4?"
    - (b) (Recommended) "What Did the Parents' DNA Tests Cover: L-2-HGA, HC-HSF4 or Both?" Its answer can be given in full from our facts: the tests are named and the certificates are on request, never a result. It avoids the spent run "L-2-HGA and HC-HSF4". Trade-off: it drops "clear", which changes the pick's wording.
    - (c) "Which Two DNA Tests Did Maggie and Jones Have Before This Litter?"

  A candidate that fails any check is replaced and the replacement recorded. None adds "Manchester", a video call, rescue wording, a licence or a result.
- [ ] **Step 3:** `python3 -m pytest -q tests/py/test_faq_near_copy.py tests/py/test_page_board.py`. Expected: pass. Commit: `feat(board): FAQ near-copy check; Manchester's three thin wordings re-proposed (STOP 2 q03 b)`.

### Task 35: Write the page-board record from the approved outline

**Files:** Create `data/boards/blue-staffy-puppies-manchester-uk.json` and `tests/py/test_manchester_board.py`.

- [ ] **Step 1: Tests first** (`test_manchester_board.py`):
  - **Schema and family.** The record validates (`PB.load_board`), with `meta.layout_type == "city"`, `page_type == "location"` and `density_pool == "all"`.
  - **Copied from the outline.**
    - Its sections are the outline's 22, in order, with unchanged headings, keywords, words, `why` and `why_source`.
    - Every non-standard section names a `component` from Manchester's `KIT_OF_VARIANT` values, and none of London's twenty `city-*` ids.
    - Every section has a `refresh`, and no two sections that share a component have the same `refresh.note`.
  - **Tuple and links.**
    - `tuple == board_approve.city_tuple(board, board["tuple"])`.
    - Every link of `docs/research/manchester-page-run/links-plan.md` (23 internal, plus the external set) is on the board, with `anchor_type` and `sentence_start`.
  - **FAQ wordings.**
    - The three FAQ nodes carry the Recommended wordings.
    - Each has an `outline_changes_since_stop2` row whose `reason` names the old wording, STOP 2 q03 (b) and the check date.
    - `near_copy_hits` over the board's FAQ questions is `[]`.
  - **Rendered board.** The rendered `docs/artifacts/boards/blue-staffy-puppies-manchester-uk.html`:
    - contains these blocks: "1b. How Google reads this page", "3d. Neighbourhoods", "4c. Term density against competitors", "4d. FAQ placement", "5c. What competitors say that we do not", "7b. Rules for new pages", "7c. Infographics", "7d. Original photos", "8a.", "8b." and "8c.";
    - names a Greater Manchester borough in 3d and no London borough;
    - offers no other-city photo in block 7.
- [ ] **Step 2: Write the record.** Shape `schemas/board.schema.json`; London's record is the worked example.
  - **`meta`.**
    - The title is front-loaded with the for-sale family (STOP 1 q04), 70 characters or fewer, under `PB.title_ceiling`. The description is 140–160 characters.
    - `canonical` is `/uk-locations/blue-staffy-puppies-manchester-uk/`.
    - `meta.sources` lists the approved outline (hash 593992436b4531ab), the research board (3583bdc08a7bd609), `links-plan.md`, `keyword-variants.json`, `free-keyword-signals.json`, `data/design/city-picks/blue-staffy-puppies-manchester-uk.json`, the data files and the Assets folder.
  - **`h1`.** Variants with the approved H1 "Should Colour Decide Which Blue Staffy Puppy Comes Home to Manchester?" as `recommended` (`h1-pick-is-final`).
  - **`brief`.** From the STOP 1 picks: M1, S2, the frameworks, header Style 2. `strategy.why` names `docs/reference/answer-board/answers/2026-10-07-research-board-blue-staffy-puppies-manchester-uk-2026-10-07.json`.
  - **`sections`.** As tested. Body sections that answer a competitor are `group: "COMPETITOR-BASED"` with that URL in `why_source`. The four optional keyword types come from `keyword-variants.json`.
  - **`tuple`.**
    - The city tuple.
    - `newsletter: {"after": "<§15 health section id>", "variant": "<the picked newsletter variant, upper-case>"}`.
    - `h6_prefixes` only if the outline's H6s share a prefix that `PB.spent_h6_prefixes` does not hold.
  - **`links`.** Every row of `links-plan.md`, per section.
    - Links 8 and 9 (`/blue-staffy-pup-sale-uk/` and `/buy-blue-staffy-puppies-uk/`) carry `why` "… HELD: built only once the deposit-order correction (STOP 2 q05 a) has landed on both pages; otherwise left unbuilt and recorded in board_revisions", unless Task 17 Step 3 found the fix already landed.
    - Flags 2–4 of `links-plan.md` go into the STOP 3 sheet as notes.
  - **`assets[]`.** `{slot, kind, w, h, required}` for the hero and every body H2 and H3, FAQ blocks excepted.
  - **`entities`.** Per section, from the outline, with the deposit entity labelled "£500 reservation deposit" (q07).
  - **`dropped`.** `{}`: the facts extract was empty.
  - **`verbatim`.** Empty: the stub is not under rule 15 (Known Issue 79).
- [ ] **Step 3:** `python3 scripts/image_candidates.py blue-staffy-puppies-manchester-uk --write`. Expected: exit 0, own photos first, no other-city file.
  - Set each slot's `source` to `existing`, `assets-folder` or `infographic`.
  - The hero alt alone carries the primary keyword.
  - A served image keeps its served alt on first use; a repeat gets a new alt.
  - List `PB.ig_plan(board)`. For any infographic heading it proposes, add an `outline_changes_since_stop2` row only where no original photo fits (breeder q06 order).
  - Read every infographic's words as copy (lessons 7).
- [ ] **Step 4:** Build and run the checks.

  ```bash
  npm run -s build
  python3 scripts/build_board_previews.py blue-staffy-puppies-manchester-uk
  python3 scripts/build_page_board.py blue-staffy-puppies-manchester-uk
  python3 scripts/keyword_metrics.py blue-staffy-puppies-manchester-uk; echo "exit $?"
  python3 -m pytest -q tests/py/test_manchester_board.py tests/py/test_rule16_gate.py tests/py/test_anchor_types.py tests/py/test_link_diversity.py tests/py/test_image_rules.py tests/py/test_outline_approval.py tests/py/test_city_board.py tests/py/test_city_uniqueness_gate.py
  ```
  Expected:
  - previews `wrote data/boards/previews/blue-staffy-puppies-manchester-uk.json — <n> blocks, 0 required by the record`;
  - the board writes `docs/artifacts/boards/blue-staffy-puppies-manchester-uk.html`;
  - keyword metrics exit 0, with no FAIL on title-front-load, first-100-words or the primary keyword;
  - pytest all pass.

  An exit 2 with `outline-unapproved` means the outline was edited: revert the edit.
- [ ] **Step 5: Commit** the record, the board page and the test. Message: `board(manchester): page board from the approved outline — own components, links, images (row 10)`.

### Task 36: The board reads like the other boards (layout A field cards, paragraph Option 2; G14)

- [ ] **Step 1:** If Task 17 Step 4 found `scripts/board_style.py` absent, the CONTROLLER asks once in chat, as a single either/or: "Bring the board-readability layer into manchester-page now, so the Manchester board ships in layout A? (a) Yes, merge `foundation` (it holds artifact-downloads) and run the readability plan's Tasks 2–3 first (Recommended) (b) No, publish the board in the current layout and republish it in place later." On (b), skip to Task 37. A later republish changes rendering only, not the record, so the approval holds.
- [ ] **Step 2: Tests first.** In `tests/py/test_page_board_readability.py` (readability plan Task 4 for `scripts/build_page_board.py`):
  - the board page embeds `board_style.CSS` and `SCRIPT`;
  - a summaries sidecar `data/boards/summaries/<slug>.json` renders 4–6 bullets above the folded original (`<details class="full">`);
  - each section's copy button still copies the unchanged markdown;
  - `PB.record_hash` is identical with or without the sidecar.
- [ ] **Step 3:** Implement, then write `data/boards/summaries/blue-staffy-puppies-manchester-uk.json`: plain summaries for blocks 1b, 3d, 4c, 4d, 5c and 7b, each fact-checked against the block it sums up. Rebuild the board (Task 35 Step 4). Commit: `feat(board): page boards in layout A with plain summaries (sidecar); Manchester's board regenerated`.

### Task 37: Read the board as approval will see it

- [ ] **Step 1:** `python3 scripts/board_gate.py blue-staffy-puppies-manchester-uk; echo "exit $?"`. Expected:
  - The only FAILs are `unapproved` and the image checks that pass only after publish.
  - It prints `rule 16: <n> records judged` and `own components: 2 new-family records judged` (London and Manchester), or more.
  - No `component-shared`, `city-pick-*`, `city-picks-missing` or `entity-blocked` line.
  - Every block-7b rule reads PASS: `external-links-six-diverse`, `anchor-type-variation`, `keyword-variants-missing`, `image-slot-missing`, `image-asset-row-missing`, `entity-blocked`, and the H5/H6 floor.

  Any other FAIL is fixed in the record, then Task 35 Step 4 runs again.
- [ ] **Step 2:** `python3 scripts/dup_content_audit.py --headers` (lessons 18: the duplicate check runs before the close). Expected: no Manchester heading or FAQ question listed. Report the output to the controller.

### Task 38 (CONTROLLER): STOP 3, the page board

**Files:** Create `docs/reference/answer-board/batches/${D}-page-board-blue-staffy-puppies-manchester-uk.{md,json}`, `data/boards/inbox/blue-staffy-puppies-manchester-uk.json` and the answers pair. Modify `data/boards/blue-staffy-puppies-manchester-uk.json` (approval) and `data/component-ledger.json`.

- [ ] **Step 1:** Read `docs/artifacts/boards/blue-staffy-puppies-manchester-uk.html` in full. Publish it with icon `layout` and `capabilities={"db": {}}`.
- [ ] **Step 2: Post the batch.** Every question links to the board.
  1. Have you approved the Manchester page board on the board? (a) Approved · (b) Changes needed. Recommended (a). Why: block 7b passes, and no component is shared with London. Trade-off: slots with no Manchester photo use our puppies' served photos.
  2. "How Much Is Your Deposit?" becomes …: (a) [Recommended wording] · (b) · (c) · (d) keep the outline's wording.
  3. "Do You Deliver Puppies Across the UK?" becomes …: options as in Task 34.
  4. The DNA question becomes …: options as in Task 34, with (b) Recommended and its trade-off stated.
  5. Do the built components match the canvas you picked from? (side-by-side link) (a) They match · (b) Mismatches (name them).
  6. *(Only if links 8 and 9 are held.)* (a) Hold links 8 and 9 until the two pages put the deposit first (Recommended) · (b) Drop both links from this page.

  Run `answer_board_batch.py` with `--batch-id ${D}-page-board-blue-staffy-puppies-manchester-uk`, ArtifactData `set`, and commit. Chat says only "<n> new questions on the board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf". **End the turn.**
- [ ] **Step 3: On the Send.** Save the answers pair. ArtifactData `get` the board's `boards/blue-staffy-puppies-manchester-uk` into `data/boards/inbox/blue-staffy-puppies-manchester-uk.json`. Then:
  - **If q2–q4 picked any non-Recommended wording:** write it into the FAQ node and its change row, run the collision and near-copy checks again, rebuild and republish to the same URL, and post a one-question batch "Approve the board with your FAQ wordings?". The record hash changed, so the first approval is stale. That is a new batch, never a re-`set`.
  - **If q5 is (b):** fix the named components (Tasks 28–31 steps), rerun Task 32 Step 3, then do the same republish and re-ask.
- [ ] **Step 4:** Record the approval.

  ```bash
  npm run -s build
  python3 scripts/board_approve.py blue-staffy-puppies-manchester-uk
  ```
  Expected: exit 0, status `approved`, the city tuple kept, `data/component-ledger.json` appended. A refusal names its cause (stale hash, heading collision, a 7b FAIL, a missing pick): fix the record, rebuild, republish and re-ask.
- [ ] **Step 5:** Commit the board, inbox, ledger and answers. Message: `board(manchester): STOP 3 approved — page board recorded`.

### Order, parallelism and who does what

- **Order:** 17 → (18 ∥ 20) → 19 → 21 → 22 → 23 → 24 → 25 → 26 (user picks) → 27 → 28 → 29 → 30 → 31 → 32 → 33 → 34 → 35 → 36 → 37 → 38 (STOP 3).
- **CONTROLLER:** 26, 27 Step 4, 33, 36 Step 1, 38, every Artifact publish, every ArtifactData read or write, and the comment watch on the canvas and the board.
- **Implementers:** everything else. Each implementer invokes `frontend-design:frontend-design` and then `impeccable:impeccable` by name in Tasks 22–25 and 28–31. The controller reads every agent's diff before accepting it (lessons 3).
- **The user picks twice:**
  - the component canvas, with its picks saved in its own db (Task 26), plus the video question;
  - STOP 3 on the page board (Task 38), with the three FAQ wordings, the side-by-side check and the held links on the same batch.

### Estimate

- **22 tasks (17–38).** Agent time:

  | Work | Tasks | Time |
  |---|---|---|
  | Tooling | 18–20 | 5–7 h |
  | Ideas index | 21 | 1.5 h |
  | 39 variants, 4 batches | 22–25 | 7–9 h |
  | Freeze and canvas | 26–27 | 1 h |
  | 13 components built, 4 batches | 28–31 | 8–11 h |
  | Scaffold and side-by-side | 32–33 | 2–3 h |
  | FAQ rewording | 34 | 1 h |
  | Board record | 35 | 2–3 h |
  | Readability | 36 | 2 h |
  | Gate read | 37 | 0.5 h |
  | STOP 3 controller work | 38 | 0.5 h |

- **Total: about 30–39 agent-hours, roughly four to five working sessions.** On top of that:
  - the user's two waits (canvas picks, STOP 3);
  - one redesign round per "none — redesign" pick (about 1.5 h each);
  - one re-approval round if a non-Recommended FAQ wording or a side-by-side mismatch is picked.
- **Cheaper alternative, not recommended:** build the components after STOP 3, at row 12, which saves about 10 h before the stop. Approval only needs reserved kit ids in `KIT_OF_VARIANT`. Not recommended because the user would then approve a board whose components exist only as canvas mockups, and London's components were built and compared side by side before its board.

## Phase G: Images and the Asset Gate (row 11, STOP 4)

Written out 2026-10-07 after STOP 3 was approved (3a4251a7), from London's Tasks 24–25, checked against the tree as it stands.
The record's approval is re-recorded at STOP 4 by `board_approve.py`, so a record edit made here (an alt, a slot's file) is expected to stale the STOP 3 hash until then.

### Task 39: Ingest the picked images, draft the papers checklist, settle the repeat alts

**Files:** `data/boards/blue-staffy-puppies-manchester-uk.json` (`assets[]`, alts), `public/images/` and `data/image-manifest.json` (through the scripts only), `data/boards/generated/`, `tests/py/test_manchester_board.py`.

- [ ] **Step 1:** List the slots by `source` (`existing`, `assets-folder`, `infographic`). For each `assets-folder` slot: `python3 scripts/ingest_image.py folder "<BSUK_ASSETS_DIR or bluestaffyuk-cms/Assets/Images>/<file>" --board blue-staffy-puppies-manchester-uk --slot <slot> --stem <meaningful-stem> --og-style A` (contain, bone; never blurfill). `existing` slots are reused at their served path, never renamed or re-encoded (rule 11).
- [ ] **Step 2: Repeat alts (rule 11, user 2026-09-29).** Every photo shown twice on the page keeps its served alt on first use, and each repeat gets a new alt, never a copy. The known repeats are the hero puppies (Roman, Cheryl, Ince, Vennie) again in the body as their full-size files, and the middle review's Jones photo. Write each new alt from the picture itself (look at it). Keep the first-person voice. The primary keyword stays on the hero alt only. Test first: a case in `test_manchester_board.py` that no image path appears twice on the board with the same alt.
- [ ] **Step 3: The papers checklist (IG-4, comic, STOP 3 pick).** Render it with the `bsuk-infographic` skill / `bsuk-infographic-builder` agent from the slot's brief. Every line comes from `data/settings.json` `puppy_trust_signs`, with no licence or registration claim beyond the data (`LICENCE_CLAIM_PLACEHOLDER` rules), and no health result. Draft it: `python3 scripts/ingest_image.py draft <master> --board blue-staffy-puppies-manchester-uk --slot papers-checklist --infographic IG-4`. Read every word on it as copy (lessons 7) and list them in the report.
- [ ] **Step 4:** `npm run -s build`, `python3 scripts/build_board_previews.py blue-staffy-puppies-manchester-uk`, `python3 scripts/build_page_board.py blue-staffy-puppies-manchester-uk`; then `python3 -m pytest -q tests/py/test_manchester_board.py tests/py/test_uniform_image_box.py tests/py/test_served_alt_preserved.py tests/py/test_city_board_alts.py tests/py/test_image_truth.py tests/py/test_infographic_skip.py`. Expected: pass. `python3 scripts/board_gate.py blue-staffy-puppies-manchester-uk`: the only FAILs are `approval-hash` (re-recorded at STOP 4) and the papers draft awaiting its pick.
- [ ] **Step 5: Commit.** `images(manchester): repeat alts, folder ingests and the papers-checklist draft for the Asset Gate (row 11)`.

### Task 40 (CONTROLLER): STOP 4, the Asset Gate

- [ ] **Step 1:** Republish the board at https://claude.ai/artifact/4NhTX3rzQXZVXLn4smTop8 (same file path). Block 7 shows the draft with its sha12 and every repeat alt.
- [ ] **Step 2:** Post `docs/reference/answer-board/batches/2026-10-07-asset-gate-blue-staffy-puppies-manchester-uk.md`. It holds one question: "Have you approved every Manchester image slot on the board?" (a) Approved on the board (Recommended) · (b) Changes needed. The question links to the board and names the draft and the new repeat alts. Chat says only "1 new question on the board: <URL>", and the turn ends.
- [ ] **Step 3: On the Send.**
  - Save the answers.
  - Get the board db into `data/boards/inbox/blue-staffy-puppies-manchester-uk.json`.
  - Run `npm run -s build`, then `python3 scripts/board_approve.py blue-staffy-puppies-manchester-uk`. Expected: exit 0, with the `img:` picks recorded.
  - For each approved draft: `python3 scripts/ingest_image.py publish --board blue-staffy-puppies-manchester-uk --slot <slot> --stem <stem>`.
  - Run `python3 scripts/board_gate.py blue-staffy-puppies-manchester-uk`. Expected: 0 FAIL.
  - Rebuild, then `npm run -s check:boards` (approval touches shared data, so every page goes stale until rebuilt).
  - Commit: `images(manchester): STOP 4 approved — Asset Gate picks recorded and published`.
- [ ] **Step 4:** Remind the user to delete `GEMINI_API_KEY` from `.env` once no image work remains (London handoff).

## Phase H: Build from the outline (row 12)

Written out 2026-10-07 after STOP 3 (3a4251a7), from London's Tasks 26–28 (`docs/superpowers/plans/2026-09-30-london-page-run.md`), every command checked against the tree at 6c0ad36d. Phase H starts only once STOP 4 is recorded (Task 40 Step 3).

### Phase H–J rulings (bind every task below)

1. **Write from the board, never from a sibling** (working rule 8). The prose comes from the approved board (`data/boards/blue-staffy-puppies-manchester-uk.json`: each node's `intent`, `why`, `keywords`, `entities`, `links`) and the data files. No one opens London's page, board or built HTML for wording, and no paragraph is copied and reworded.
2. **The nine adopted FAQ wordings** are the STOP 3 picks (`docs/reference/answer-board/answers/2026-10-07-page-board-blue-staffy-puppies-manchester-uk-2026-10-07.md` q2–q10, every one the (a) wording). They are the `REWORDED` map in `tests/py/test_manchester_board.py`, which every test below imports rather than retyping. Each answer text stays as it is. The one exception is the one `docs/research/manchester-components/faq-rewordings.md` §2 (a) names: "Which Parts of the UK Do You Deliver Puppies To?" cannot open on the `delivery` row's "Yes.", so its lead becomes the `about-delivery-home` row's own "wherever you are in the UK".
3. **Section ids are the board's ids.** `scripts/outline_provenance_check.py` (`outline-unknown-section`), `scripts/query_coverage_check.py` and `scripts/dup_content_audit.py` find a section only as `<section id="<board section id>" data-section-label="…">` in `<main>`. Four of the scaffold's anchors are not board ids: `asked-first` becomes `faq-top`, `health-questions` becomes `faq-middle`, `everyday` becomes `faq-bottom` and `enquire` becomes `enquiry`.
4. **Links 8 and 9 stay HELD** (STOP 3 q12 (a)): `/blue-staffy-pup-sale-uk/` ("Our Blue Staffy pup prices in full", litter H3) and `/buy-blue-staffy-puppies-uk/` ("Our regularly updated listing", under the litter table). They are left unbuilt until the Task 17 Step 3 grep finds no hit on both pages.
5. **Images are the board's.** Every `<img>` is its slot's `assets[]` row in the board record (file, alt, size), read from the imported record by slot. The scaffold's hard-coded `BODY`, `FAQ_PHOTO` and `REVIEW_ROW` photo choices go.
6. **Facts from data only** (Phase F ruling 10, unchanged): no video call (STOP 1 q08), no rescue wording (q10), no licence claim, colour and price said of this litter only (q09), the deposit only with `deposit_refund_clause` (never plainly "refundable"), the tests named with the certificates on request and never a result, no phone, no mileage, journey time or date.
7. **noindex until the user approves the page** (Task 54). `robots="noindex, follow"` is written in the page file, never read from data.
8. **`session-open` is never re-recorded** for this slug. Re-recording it stales the Harden passes (page-run row 1), and rows 14–15 would have to run again.

### Task 41: Pre-flight (read-only)

**Files:** none.

- [ ] **Step 1:** Confirm the stops.

  ```bash
  git branch --show-current
  npm run -s build
  python3 scripts/board_gate.py blue-staffy-puppies-manchester-uk; echo "exit $?"
  python3 -c "import json;b=json.load(open('data/boards/blue-staffy-puppies-manchester-uk.json'));print(b['approval']['approved_at'], [a['slot'] for a in b['assets'] if a.get('status')!='baked'])"
  ```
  Expected: `manchester-page`; board gate exit 0 with 0 FAIL; an approval stamped at or after the STOP 4 Send; `[]` (every slot baked, `papers-checklist` included). Anything else means STOP 4 is not recorded: go back to Task 40 Step 3.
- [ ] **Step 2:** Re-run the deposit-order grep (Task 17 Step 3).

  ```bash
  grep -n "deposit comes after you have met\|video call before the deposit\|on a video call we offer before the deposit" src/pages/buy-blue-staffy-puppies-uk/index.astro src/pages/blue-staffy-pup-sale-uk/index.astro
  ```
  Expected while the fix has not landed: hits. Links 8 and 9 stay HELD (ruling 4). If there are no hits, report it to the CONTROLLER and stop this task. Building the links then needs a record change: the two `why` lines drop "HELD", a `board_revisions` row cites STOP 3 q12, and the CONTROLLER re-runs `python3 scripts/board_approve.py blue-staffy-puppies-manchester-uk`. That happens before Task 44.
- [ ] **Step 3:** Confirm that the held links are recorded in `board_revisions`.

  ```bash
  python3 -c "import json;b=json.load(open('data/boards/blue-staffy-puppies-manchester-uk.json'));print([r['source'] for r in b.get('board_revisions') or []])"
  ```
  Expected: a row whose `source` is `answer board 2026-10-07-page-board-blue-staffy-puppies-manchester-uk q12`, whose `record_change` names links 8 and 9 as held, and whose `builder` says "leave both unbuilt". If it is missing, the CONTROLLER adds it. The record is shared with the Asset Gate work, so the CONTROLLER owns that edit. The row moves the record hash, so the CONTROLLER then runs `npm run -s build && python3 scripts/board_approve.py blue-staffy-puppies-manchester-uk` (expected: exit 0). London's board revision was re-approved the same way (f3031626). Commit `board(manchester): links 8 and 9 held, recorded as a board revision (STOP 3 q12)`.
- [ ] **Step 4:** Read `docs/reference/lessons.md` entries 7–9, 15 and 18–21 again. Each one binds a step below.

### Task 42: The rebuilt page's own tests, written first

**Files:**
- Create: `tests/py/test_manchester_page.py`
- Modify: `tests/py/test_manchester_scaffold.py`

- [ ] **Step 1: Write the failing test file.** Write `tests/py/test_manchester_page.py`:

  ```python
  """The Manchester city page, rebuilt from its approved outline and board (page-run row 12).

  What must hold once the scaffold is replaced:
    - no scaffold marker, no scaffold line and no migrated body: Manchester is a rebuilt page;
    - the H1 is the approved outline's H1, and every body H2/H3 is a question (header Style 2);
    - every board section is one labelled <section> in <main>, with the board's id, in order;
    - the three FAQ blocks hold the board's questions (the nine STOP 3 wordings in place), and
      the question file's covered_by records each one;
    - facts come from data: no hand-typed £, parents Maggie and Jones, the tests named and no
      result stated, nothing about a licence, no video call, no rescue wording;
    - the deposit appears only with its refund clause, never plainly "refundable";
    - every board link is on the page except the two HELD ones, and no other external link;
    - the page stays noindex until the user approves it (Task 54).
  """
  import html as H
  import json
  import pathlib
  import re

  import pytest

  from test_manchester_board import REWORDED

  ROOT = pathlib.Path(__file__).resolve().parents[2]
  SLUG = "blue-staffy-puppies-manchester-uk"
  SRC = ROOT / "src/pages/uk-locations" / f"{SLUG}.astro"
  BUILT = ROOT / "dist/uk-locations" / SLUG / "index.html"
  OUTLINE = json.loads((ROOT / "data/outlines" / f"{SLUG}.json").read_text(encoding="utf-8"))
  BOARD = json.loads((ROOT / "data/boards" / f"{SLUG}.json").read_text(encoding="utf-8"))
  QUERIES = json.loads((ROOT / "data/queries" / f"{SLUG}.json").read_text(encoding="utf-8"))
  SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
  FAQ_BAND = {"faq-top": 6, "faq-middle": 7, "faq-bottom": 7}
  NODE_Q = re.compile(r"^Q:\s*(.+?)\s+—")
  HELD = "HELD: built only once the deposit-order correction (STOP 2 q05 a) has landed on both pages"
  ADOPTED = {old: new for old, (new, _) in REWORDED.items()}


  def built():
      if not BUILT.exists():
          pytest.skip("run npm run -s build first")
      return BUILT.read_text(encoding="utf-8")


  def text(fragment):
      """Visible words: an inline <span> breaks no word (src/lib/cityKit.ts `keepRuns` wraps a
      price or a test name in one), every other tag is a space."""
      fragment = re.sub(r"</?span\b[^>]*>", "", fragment)
      return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


  def main_html(html):
      return html.split("<main", 1)[1].split("</main>", 1)[0]


  def main_text(html):
      return text(main_html(html))


  def labelled_sections(html):
      """[(id, html)] for every <section data-section-label> in <main>, each running to the next."""
      main = main_html(html)
      tags = list(re.finditer(r"<section\b[^>]*\bdata-section-label=[^>]*>", main))
      out = []
      for i, m in enumerate(tags):
          sid = re.search(r'\bid="([^"]+)"', m.group(0))
          end = tags[i + 1].start() if i + 1 < len(tags) else len(main)
          out.append((sid.group(1) if sid else f"#{i}", main[m.start():end]))
      return out


  def board_faq_questions(section_id):
      sec = next(s for s in BOARD["sections"] if s["id"] == section_id)
      return [NODE_Q.match(n["intent"]).group(1) for n in sec["tree"]]


  def board_links():
      return [(s["id"], kind, l) for s in BOARD["sections"] for kind in ("internal", "external")
              for l in s.get("links", {}).get(kind, [])]


  def test_manchester_is_no_longer_a_scaffold():
      html = built()
      for mark in ("data-city-scaffold", "data-scaffold-tree", "prose-migrated", "Scaffold line, not copy."):
          assert mark not in html, mark


  def test_the_h1_is_the_approved_outline_h1():
      assert OUTLINE["approval"], "STOP 2 is recorded"
      h1s = [text(h) for h in re.findall(r"<h1[^>]*>(.*?)</h1>", built(), re.S)]
      assert h1s == [OUTLINE["h1"]]


  def test_every_body_h2_and_h3_is_a_question():
      heads = [text(h) for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", main_html(built()), re.S)]
      assert heads
      assert [h for h in heads if not h.endswith("?")] == []


  def test_every_board_section_is_one_labelled_section_with_the_boards_id_in_order():
      ids = [sid for sid, _ in labelled_sections(built())]
      assert ids == [s["id"] for s in BOARD["sections"]], ids


  def test_three_faq_blocks_holding_the_boards_questions_and_covered_by_records_them():
      html = built()
      secs = dict(labelled_sections(html))
      assert html.count('data-faq-block="') == 3
      shown = []
      for sid, n in FAQ_BAND.items():
          want = board_faq_questions(sid)
          got = [text(q) for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", secs[sid], re.S)]
          assert got == want and len(got) == n, (sid, got)
          shown += got
      assert set(ADOPTED.values()) <= set(shown) and not set(ADOPTED) & set(shown)
      covered = {q["covered_by"]["text"] for q in QUERIES["questions"]
                 if q.get("covered_by") and q["covered_by"]["where"] == "faq"}
      assert covered == set(shown)
      assert not [q["id"] for q in QUERIES["questions"] if q["must_answer"] and not q.get("covered_by")]


  def test_no_price_is_typed_in_the_page_source():
      assert "£" not in SRC.read_text(encoding="utf-8")


  def test_the_parents_are_maggie_and_jones():
      body = main_text(built())
      assert "Maggie" in body and "Jones" in body


  def test_the_tests_are_named_and_no_result_is_stated():
      body = main_text(built())
      for name in ("L-2-HGA", "HC-HSF4"):
          assert name in body, name
      for m in re.finditer(r"L-2-HGA|HC-HSF4", body):
          window = body[max(0, m.start() - 80): m.end() + 80].lower()
          assert not re.search(r"\bclear\b|\bcertified\b|will not be affected", window), window


  def test_nothing_about_a_licence_a_video_call_or_a_rescue():
      body = main_text(built()).lower()
      for word in ("licence", "license", "video call", "rescue"):
          assert word not in body, word


  def test_the_deposit_is_never_plainly_refundable():
      body = main_text(built()).lower()
      clause = SETTINGS["deposit_refund_clause"].lower()
      assert body.count("refundable") == body.count(clause) > 0


  def test_no_research_placeholder_ships():
      body = main_text(built())
      for mark in ("NOT FETCHED", "PHONE_PLACEHOLDER", "LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER"):
          assert mark not in body, mark


  def test_every_enquiry_cta_points_at_the_board_id():
      html = built()
      assert 'id="enquiry"' in html and 'href="#enquire"' not in html
      assert main_html(html).count('href="#enquiry"') >= 3


  def test_every_board_link_is_on_the_page_but_the_held_two_and_no_other_external_link():
      main = main_html(built())
      anchors = {(H.unescape(h), text(a)) for h, a in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', main, re.S)}
      rows = board_links()
      held = [l for _, _, l in rows if HELD in l["why"]]
      assert sorted(l["href"] for l in held) == ["/blue-staffy-pup-sale-uk/", "/buy-blue-staffy-puppies-uk/"]
      missing = [(l["href"], l["anchor"]) for _, _, l in rows if HELD not in l["why"]
                 and not any(h == l["href"] and a.startswith(l["anchor"]) for h, a in anchors)]
      assert missing == []
      assert not [l["href"] for l in held if any(h == l["href"] for h, _ in anchors)], "a held link was built"
      external = {h for h, _ in anchors if h.startswith("http")}
      assert external <= {l["href"] for _, kind, l in rows if kind == "external"}, sorted(external)


  def test_the_schema_names_greater_manchester_and_carries_no_telephone():
      html = built()
      nodes = []
      for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
          data = json.loads(block)
          for n in data if isinstance(data, list) else [data]:
              nodes += n.get("@graph", [n])
      local = [n for n in nodes if n.get("@type") == "LocalBusiness"]
      # The layout's site-wide node and the page's own share one @id: one business, described twice.
      assert local and len({n.get("@id") for n in local}) == 1
      assert any("Manchester" in json.dumps(n.get("areaServed")) for n in local)
      assert not [n for n in local if "telephone" in n]
      faq = [n for n in nodes if n.get("@type") == "FAQPage"]
      assert len(faq) == 1 and len(faq[0]["mainEntity"]) == sum(FAQ_BAND.values())


  def test_noindex_until_the_user_approves_the_page():
      assert re.findall(r'<meta name="robots" content="([^"]*)"', built()) == ["noindex, follow"]
      assert 'robots="noindex, follow"' in SRC.read_text(encoding="utf-8")
  ```

- [ ] **Step 2: Retire the scaffold-only assertions** in `tests/py/test_manchester_scaffold.py`. Its other tests hold the components, the nav set, the litter table, the reviews and the alts, and they stay.
  - Add, after the imports: `from test_manchester_board import REWORDED` and `ADOPTED = {old: new for old, (new, _) in REWORDED.items()}`.
  - Rename `test_the_template_no_longer_builds_manchester_and_still_builds_the_other_26` to `test_manchester_has_its_own_rebuilt_page_and_the_template_builds_the_other_26`, and change its first assertion to `assert f'data-city-scaffold="{SLUG}"' not in html`.
  - Delete `test_the_scaffold_keeps_the_migrated_body_for_parity`. Once Manchester is in `data/facts/rebuilt.json` (Task 45), `check:facts` holds it against `data/facts/blue-staffy-puppies-manchester-uk.json`, and `check:parity` no longer measures it.
  - Delete `test_each_body_section_carries_one_marked_scaffold_line`. `test_manchester_page.py::test_manchester_is_no_longer_a_scaffold` holds the reverse.
  - In `test_the_headings_are_the_outlines_in_order_h1_to_h6`, build `want` with each H3 passed through `ADOPTED.get(text, text)`:

    ```python
    want = [(1, OUTLINE["h1"])] + [(l, ADOPTED.get(t, t)) for s in OUTLINE["sections"]
                                    for l, t in flat(s["headings"]) if l > 1]
    ```
  - In `test_the_faq_schema_carries_exactly_the_visible_questions`, build `outline` as `[ADOPTED.get(c["text"], c["text"]) for s in OUTLINE["sections"] if s.get("faq") for h in s["headings"] for c in h["children"]]`.
  - Change the module docstring's first line to "Manchester's own route: the thirteen picks, the nav set and the outline's headings, on the rebuilt page (a scaffold until page-run row 12)."
  - `test_the_scaffold_is_noindex_and_in_no_sitemap` stays until Task 54.

- [ ] **Step 3: Run the tests and see them fail.**

  ```bash
  npm run -s build
  python3 -m pytest tests/py/test_manchester_page.py tests/py/test_manchester_scaffold.py -q
  ```
  Expected: FAIL. On the scaffold at least these fail: `test_manchester_is_no_longer_a_scaffold`, `test_every_board_section_is_one_labelled_section_with_the_boards_id_in_order`, the FAQ-block test (old wordings, `covered_by` null), `test_every_enquiry_cta_points_at_the_board_id`, the board-link test, the schema test (no `areaServed`), `test_the_tests_are_named_and_no_result_is_stated` (the old "Tested Clear for" heading), the renamed template test, and the two `ADOPTED` tests. `test_the_h1_is_the_approved_outline_h1`, `test_no_price_is_typed_in_the_page_source` and the noindex test pass already. Read the failure list: a test that passes on the scaffold for a reason other than these is a weak test and is tightened before the commit.

- [ ] **Step 4: Commit the failing tests.**

  ```bash
  git add tests/py/test_manchester_page.py tests/py/test_manchester_scaffold.py
  git commit -m "test(manchester): the rebuilt page's invariants, failing on the scaffold (row 12)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 43: The nine FAQ wordings reach the build; the DNA xfail goes with them. Tests first.

**Files:**
- Modify: `src/lib/manchesterFaq.ts`, `data/queries/blue-staffy-puppies-manchester-uk.json`, `tests/py/test_city_kit_manchester.py`, `tests/py/test_no_health_result_stated.py`

The approved outline stays frozen (hash 593992436b4531ab). The new wordings live in the board record: each FAQ node's `intent` reads `Q: <question> — …`, which `PB.faq_block_questions` reads too. So the FAQ module reads its questions from the board, as London's page reads its board (`src/pages/uk-locations/blue-staffy-puppies-london.astro` imports `data/boards/blue-staffy-puppies-london.json`). (Recommended.) Why: the board is the approved record that carries the STOP 3 picks. Trade-off: the module now imports the board record, so a later board edit changes the page's questions, and the record hash already guards that edit.

- [ ] **Step 1: Point the kit's FAQ tests at the adopted wordings, and see them fail.** In `tests/py/test_city_kit_manchester.py`:
  - Add `from test_manchester_board import REWORDED` and `ADOPTED = {old: new for old, (new, _) in REWORDED.items()}`.
  - In `test_faq_blocks_are_the_outlines_three_blocks_word_for_word`, compare with `[ADOPTED.get(c["text"], c["text"]) for c in h2["children"]]`.
  - In `test_faq_answers_come_from_the_bank_and_the_data_never_typed`, read every `rows[...]` key through `ADOPTED`:
    - `VERBATIM`'s keys become `ADOPTED.get(k, k)`;
    - `cost`, `deposit`, the mother answer and `across` use the adopted questions;
    - `dna` is `rows[ADOPTED["Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?"]]`.
  - Add `assert across.startswith("Wherever you are in the UK")` (ruling 2's one changed lead).
  - Change the module assertion to `"boards/blue-staffy-puppies-manchester-uk.json" in lib`.

  Run `npm run -s build && python3 -m pytest -q tests/py/test_city_kit_manchester.py -k faq`. Expected: FAIL, because the questions are still the outline's.
- [ ] **Step 2: Read the questions from the board.** In `src/lib/manchesterFaq.ts`, replace the outline import and the `SECTIONS` block with:

  ```ts
  import board from '../../data/boards/blue-staffy-puppies-manchester-uk.json';

  type Node = { intent?: string };
  type Sec = { id: string; heading: string; tree: Node[] };
  /** The board's three FAQ blocks, in page order (STOP 3: the nine wordings the breeder picked are
   *  the nodes' `Q: <question> —` intents; the approved outline stays as STOP 2 approved it). */
  const FAQ_IDS = ['faq-top', 'faq-middle', 'faq-bottom'] as const;
  const NODE_Q = /^Q:\s*(.+?)\s+—/;
  const SECTIONS = FAQ_IDS.map((id) => {
    const s = (board as unknown as { sections: Sec[] }).sections.find((x) => x.id === id);
    if (!s) throw new Error(`manchesterFaq: the board has no section ${id}`);
    return s;
  });
  ```
  The export becomes:

  ```ts
  export const MANCHESTER_FAQ: CityFaqBlock[] = SECTIONS.map((sec, i) => ({
    key: KEYS[i],
    heading: sec.heading,
    items: sec.tree.map((n) => {
      const q = NODE_Q.exec(n.intent ?? '')?.[1];
      if (!q) throw new Error(`manchesterFaq: ${sec.id} has a node with no "Q: <question> —" intent`);
      const hit = ANSWERS[q];
      if (!hit) throw new Error(`manchesterFaq: no answer keyed to the board question "${q}"`);
      return { q, ...hit };
    }),
  }));
  ```
  Keep `KEYS` and the length check. The scaffold page's own check (`block.heading !== h2Of(row(n)).text`) still holds, because the board's FAQ headings are the outline's H2s word for word.
- [ ] **Step 3: Re-key `ANSWERS`.** Rename the nine keys, old → new, as `REWORDED` lists them, and leave every answer text and `source` as it is. There is one exception, the across-the-UK answer (ruling 2):

  ```ts
  'Which Parts of the UK Do You Deliver Puppies To?': {
    // The `delivery` row opens "Yes.", which does not answer a "which" question; the reach is the
    // about-delivery-home row's own words (faq-rewordings.md §2 (a), STOP 3 q3).
    a: `${REACH}: ${edit(bank('delivery'), 'Yes. ', '').replace(/\.$/, '')}, and you can collect your puppy from us in ${TOWN} instead.`,
    source: 'data/faq.json about-delivery-home, delivery, home-safe-delivery; data/settings.json delivery_note, delivery_min_gbp, delivery_max_gbp, address.city',
  },
  ```
  with, above `ANSWERS`:

  ```ts
  const REACH = 'Wherever you are in the UK';
  if (!bank('about-delivery-home').includes(lcFirst(REACH))) throw new Error('manchesterFaq: data/faq.json about-delivery-home no longer says "wherever you are in the UK"');
  ```
  Update the file-top comment: the questions are the board's (the STOP 3 picks), and the answers are the bank and the data.
- [ ] **Step 4: Record each wording in the question file.** In `data/queries/blue-staffy-puppies-manchester-uk.json`, set `covered_by` on every `must_answer` question. `check:queries` holds all 29 once Task 45 registers the page.
  - **The 20 FAQ picks:** `{"where": "faq", "text": <the board question>}`. The nine reworded ones carry the adopted wording: `q-how-much-is-the-deposit-2cce23`, `q-do-you-deliver-across-the-uk-fb0c4a`, `q-which-genetic-tests-have-the-parents-had-19da02`, `q-how-much-does-a-blue-staffy-cost-uk-4051c2`, `q-can-i-get-a-blue-staffy-puppy-delivered-ad16e3`, `q-how-can-i-avoid-buying-from-a-puppy-5e9d7e`, `q-are-blue-staffy-aggressive-55b447`, `q-do-blue-staffy-suit-a-family-home-d39c23`, `q-can-a-staffy-live-in-a-flat-310055`.
  - **The 9 non-FAQ must-answer picks:** `{"where": "heading", "text": <the board heading in <main> that answers it>}`, read from the board node whose `intent` answers that question. Example: `q-do-staffy-get-attached-to-one-person-6d9e29` → the `favourite-person` H2.
  - **The three `extra_sections`:** each takes as its `heading` the board H2 of the section built for it: paperwork → `papers`, health → `guarantee`, temperament → `favourite-person`.

  Then:

  ```bash
  python3 scripts/query_augment.py blue-staffy-puppies-manchester-uk --page-type location --keyword "blue staffy puppies manchester" --route /uk-locations/blue-staffy-puppies-manchester-uk/
  git diff --stat -- data/queries/blue-staffy-puppies-manchester-uk.json
  ```
  Expected: `… kept 29 covered_by and 3 headings, dropped 0`. If the re-run changed anything besides the fills (`fetched`, scores, a regrouped question), `git checkout` the file, re-apply the fills by hand, and keep the hand-written file. The re-run only proves the fills carry.
- [ ] **Step 5: Run it, and watch the strict xfail turn red.**

  ```bash
  npm run -s build
  python3 -m pytest -q tests/py/test_city_kit_manchester.py tests/py/test_no_health_result_stated.py tests/py/test_evidence_certificates_on_request.py tests/py/test_manchester_board.py
  ```
  Expected: the kit tests pass. `test_manchesters_dna_faq_heading_states_no_result` FAILs with `XPASS(strict)` on both Manchester routes, because "Tested Clear for" has left the page.
- [ ] **Step 6: Remove the xfail and its constant, in this same change** (`faq-rewordings.md` §3). In `tests/py/test_no_health_result_stated.py`, delete:
  - the comment block above `PENDING_REWORD`;
  - `PENDING_REWORD = "Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?"`;
  - the two lines `if rel in MANCHESTER_ROUTES:` and `text = text.replace(PENDING_REWORD, " ")   # held by the xfail below, not excused`;
  - the whole `test_manchesters_dna_faq_heading_states_no_result` with its two decorators.

  Re-run the Step 5 command. Expected: all pass, with `test_no_built_page_states_a_dna_or_health_test_result` examining more than 50 files and excusing nothing for the new heading.
- [ ] **Step 7: Commit.**

  ```bash
  git add src/lib/manchesterFaq.ts data/queries/blue-staffy-puppies-manchester-uk.json tests/py/test_city_kit_manchester.py tests/py/test_no_health_result_stated.py
  git commit -m "feat(manchester): the nine STOP 3 FAQ wordings, read from the board; covered_by recorded; the DNA xfail retired with them (row 12)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 44: Write the page from the approved board

**Files:**
- Modify: `src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro`

- [ ] **Step 1: Read the sources, and nothing else.** Invoke the Skill tool with `bsuk-location-page-builder` and read its Step 2 (sections) and Step 5 (FAQ). Then read:
  - the approved board `data/boards/blue-staffy-puppies-manchester-uk.json`, with every section's `tree`, `intent`, `why`, `keywords`, `entities`, `links`, `images` and `refresh`, and its `assets[]`;
  - the outline's `build_notes` and `schema`;
  - `data/settings.json`, `data/puppies.json`, `data/price-matrix.json`, `data/reviews.json`, `data/faq.json`;
  - `src/lib/cityKit.ts`, `src/lib/manchesterFaq.ts`, `src/lib/manchesterNav.ts`.

  Do not open London's page, board or built HTML, or any other city's (ruling 1).
- [ ] **Step 2: Rewire the scaffold's plumbing.**
  - Import the board record: `import board from '../../../data/boards/blue-staffy-puppies-manchester-uk.json';`. Add a `photo(slot)` helper that returns the slot's `assets[]` row and throws on a missing slot.
  - The contents panel (board section `contents`) is mounted by `CityShell` through `nav.contents`, so `id: 'contents'` and `'data-section-label'` go into its props, as London's page passes them.
  - `NAV_ROWS` takes the board ids (ruling 3): `['7', 'faq-top']`, `['12', 'faq-middle']`, `['21', 'faq-bottom']`, `['22', 'enquiry']`. The other nine already match. Every `href: '#enquire'` becomes `'#enquiry'`.
  - Each of the 22 board sections renders as one top-level `<section id="<board id>" data-section-label={<its board heading>}>` in `<main>`, in board order. Where a Manchester component's root is a `<section>` that spreads `...rest` (as `CityOffsetSheet` does), pass `id` and `data-section-label` to it. Otherwise wrap it.
  - Remove the `scaffold()` helper, every scaffold line, the `.scaffold-tree` lists and their `<style>` rules, the `plan()` sheet rows, `data-city-scaffold`, and the `migrated` section with its `<style>` rules.
  - Remove the hard-coded `BODY`, `FAQ_PHOTO`, `REVIEW_ROW` and hero photo choices (ruling 5).
  - Keep `robots="noindex, follow"` (ruling 7) and rewrite the file-top comment: what the page is, its sources (outline STOP 2, board STOP 3, Asset Gate STOP 4), facts from data, and kept out of the index until the user approves it.
- [ ] **Step 3: Write the page top to bottom, in the board's section order.**
  - Each H2 is its section's `heading`, and each H3–H6 is its `tree` node's `heading`, word for word in Title Case. The litter table stays under its H4 with the outline's caption.
  - The frame sections the outline gives no heading carry their board heading only as `data-section-label`, never as a heading element, as the scaffold does. These are `counter`, `trust`, `contents`, `key-takeaways`, the three `review-*` and `newsletter`. The heading census stays the outline's.
  - The opening paragraph under every H2 and H3 answers its question conversationally, in 12 words or more, in Lisa Bright's first-person plural voice (`we`, `our`, `here at BlueStaffyUK`), inside the section's `words` band. The whole page lands in the 2,000–3,000 word target. Draft each section's prose through `@bsuk-seo-content-writer` from the node's `intent` and `entities`, then filter it through the `anti-ai-writing` skill. No em dash in our copy.
  - Every fact is an interpolation from `src/lib/cityKit.ts` or the data, never typed:
    - `BOY_PRICE`, `GIRL_PRICE`, `DEPOSIT`, `DEPOSIT_HOLDS`, `refundClause()`, `depositTerms()`;
    - `DELIVERY_BAND`, `TOWN`, `transportName` and `pricedBy`;
    - `PARENT_DNA_TESTS`, `PUPPY_SIGNS`, `guaranteeFact()` and `guaranteeRow()`, and `guarantee_cover` only where a guarantee sentence already carries it;
    - `settings.breeder_name`;
    - each puppy's name, sex and colour from `availablePuppies()`.
  - **The deposit section** (`deposit`) answers "see the puppy with its mother before any money changes hands" without a video call. The deposit books the viewing in Carlisle, reserves the puppy and comes off the price. The refund wording is `refundClause()`, whole. Payment is by bank transfer. The parents, papers and vet records are seen before the buyer commits (`data/faq.json` `whyus-evidence`). It never states a "see before you pay" rule we do not follow (lessons 9).
  - **Health** (`health-tests`, `guarantee`) names L-2-HGA and HC-HSF4 through `PARENT_DNA_TESTS`, says the certificates are shared on request, and states no result.
  - **Life in Manchester** (`busy-household`) carries only "not a banned breed / not on the government's list", linked to gov.uk as the board lists it. It names no park, vet, business or city statistic.
  - **Colour and price** are said of this litter only (q09). There is no licence claim, no rescue wording and no phone.
  - **Images.** The hero's photos come from slot `manchester-hero`. Each body H2's photo is its `<section>-h2` slot, passed to `CityOffsetSheet` as `photo` (and `photoAlt` only where the record's alt differs from the served one). Each body H3 has its slot as a `BodyImage` (`src/components/BodyImage.astro`) directly after the H3 and before its prose, `box="uniform"` (or `box="tall"` for a portrait). The papers checklist is the published `papers-checklist` asset. Review and FAQ photos are the record's, each repeat with the record's new alt.
  - **Links.** Every link on the board and no other sits Link-First at the start of its sentence, with the board's anchor. The two HELD links (ruling 4) are not built, and their sentences stand without them.
  - **FAQ.** Each FAQ block is `CityRowsBesideAPhoto` with `items` from `MANCHESTER_FAQ` (Task 43), so its questions are the board's and its answers the bank's and the data's.
  - **Schema.** `schema` is `faqPageNode(MANCHESTER_FAQ.flatMap((b) => b.items))`, plus one `LocalBusiness` node with `areaServed` Greater Manchester and no `telephone` key, and the `Person` byline the outline names (Lisa Bright). There is no `VideoObject` and no `Product` (the page shows no puppy card).
  - No section of this board is a scam-and-trust section and none carries a video (Phase F ruling 2; canvas q2 (a)), so neither `bsuk-scam-trust-agent` nor `bsuk-video-seo-agent` runs.
- [ ] **Step 4: Run the tests.**

  ```bash
  git add src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro
  git commit -m "wip(manchester): the page written from its approved board (row 12)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  npm run -s build
  python3 -m pytest -q tests/py/test_manchester_page.py tests/py/test_manchester_scaffold.py tests/py/test_city_kit_manchester.py tests/py/test_no_health_result_stated.py
  ```
  The page is committed first because the prebuild dates a route from its history. Expected: PASS. A failure is confirmed on `dist/uk-locations/blue-staffy-puppies-manchester-uk/index.html` before the page is edited. Commit each fix with the page.
- [ ] **Step 5: The duplicate check, straight after the first build (lessons 18).**

  ```bash
  python3 scripts/dup_content_audit.py --headers; echo "exit $?"
  python3 scripts/dup_content_audit.py; echo "exit $?"
  ```
  Expected: no row names `uk-locations/blue-staffy-puppies-manchester-uk`, whether heading, FAQ question or body passage. A Manchester hit is fixed in the page now: a body sentence is rewritten from the board; a heading or FAQ question goes to the CONTROLLER, because changing it is a board change. It is never left for the close. Report both outputs to the controller.
- [ ] **Step 6: Commit** the page and anything the build rewrote (`data/page-dates.json`, `docs/reports/{redirects,schema,sitemaps}.md`): `feat(manchester): the page written from its approved outline and board (row 12)`, with the trailer.

### Task 45: Provenance, registration and the site gates

**Files:**
- Modify: `data/facts/rebuilt.json`, `tests/render/targets.json`, `scripts/build_llms_txt.py`, `tests/py/test_llms_txt_build.py`

- [ ] **Step 1: Check provenance before registering.**

  ```bash
  npm run -s build
  python3 scripts/outline_provenance_check.py blue-staffy-puppies-manchester-uk; echo "exit $?"
  ```
  Expected: exit 0, with none of these: `outline-unknown-section`, `outline-extra`, `outline-missing`, `outline-order`, `outline-duplicate-heading`, `outline-heading-crossover`, `outline-copy-crossover`, `outline-sentence-crossover`. A crossover is fixed in the copy, never by widening the whitelist.
- [ ] **Step 2: Register the page.** Append `"blue-staffy-puppies-manchester-uk"` to `data/facts/rebuilt.json`. Append to `pages` in `tests/render/targets.json`:

  ```json
  {"slug": "uk-locations/blue-staffy-puppies-manchester-uk", "page_type": "location", "corpus": true}
  ```
- [ ] **Step 3: A rebuilt page that is still noindex stays out of `llms.txt`. Test first.** `scripts/build_llms_txt.py` `rebuilt_stub()` lists a `stub-noindexed` page-map row once its slug is in `data/facts/rebuilt.json`. The rule was written for London, which was indexable when it was added (f3031626). Registration therefore puts the noindex Manchester page into `public/llms.txt`, and `test_listed_page_count_matches_indexable_rows` moves from 23 to 24. In `tests/py/test_llms_txt_build.py`, add:

  ```python
  def test_a_rebuilt_page_still_noindex_stays_out(tmp_path):
      # Manchester is rebuilt (data/facts/rebuilt.json) but its own file still writes
      # robots="noindex, follow" until the user approves it (page-run row 21).
      text = build_llms_txt.main(tmp_path / "llms.txt").read_text(encoding="utf-8")
      assert "/uk-locations/blue-staffy-puppies-manchester-uk/" not in text
  ```
  Run `python3 -m pytest -q tests/py/test_llms_txt_build.py`. Expected: FAIL on the new test and on the count (24). Then, in `scripts/build_llms_txt.py`:

  ```python
  def held_noindex(page):
      """A rebuilt page whose own source still writes robots="noindex is not yet in the index
      (the city pages keep it in the file until the user approves the page)."""
      route = page["url"].strip("/")
      for src in (ROOT / "src/pages" / f"{route}.astro", ROOT / "src/pages" / route / "index.astro"):
          if src.is_file():
              return 'robots="noindex' in src.read_text(encoding="utf-8")
      return False


  def rebuilt_stub(page, rebuilt):
      """A migrated stub (`stub-noindexed`) that a rebuilt page has since replaced AND whose page
      file no longer holds it out of the index. Its row still describes the WordPress stub, so it
      is listed without the stub's word count. London became indexable on the breeder's approval
      (2026-10-06); Manchester is rebuilt and stays out until the user approves it (row 21)."""
      return ("stub-noindexed" in page.get("refresh_flags", []) and _slug(page["url"]) in rebuilt
              and not held_noindex(page))
  ```
  Re-run. Expected: PASS, with the count still 23. Then run `npm run llms` and `git diff --stat public/llms.txt`. Expected: no change.
- [ ] **Step 4: Run the site gates.**

  ```bash
  npm run -s build
  npm run -s check:all; echo "exit $?"
  python3 scripts/board_gate.py blue-staffy-puppies-manchester-uk
  python3 scripts/keyword_metrics.py blue-staffy-puppies-manchester-uk; echo "exit $?"
  npm run -s test:py
  ```
  Expected: exit 0 on each. Read the examined counts:
  - `check:queries` and `check:outline` now examine Manchester;
  - `check:facts` examines it against its empty fact set;
  - `check:parity` no longer measures its migrated body.

  A FAIL is confirmed on the built page before anything is edited (`rules/gates.md`, `bsuk-gate-integrity`).
- [ ] **Step 5: Commit.**

  ```bash
  git add data/facts/rebuilt.json tests/render/targets.json scripts/build_llms_txt.py tests/py/test_llms_txt_build.py
  git commit -m "chore(manchester): registered as rebuilt; a noindex rebuilt page stays out of llms.txt; check:all green (row 12)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase I: Harden (rows 13–16)

### Task 46: Render gates (row 13)

**Files:**
- Create: `data/quality/scorecards/uk-locations__blue-staffy-puppies-manchester-uk-${D}.json` and the other pages' scorecards of the run (written by the run)
- Modify: `docs/reports/render-baseline-project4.md` (regenerated)

- [ ] **Step 1: Check the checkers first.**

  ```bash
  npm run test:render:meta
  ```
  Expected: PASS. A failure here means the harness is broken: stop, report, and trust no page result.
- [ ] **Step 2: Manchester alone, then the full run.**

  ```bash
  npm run test:render:pages -- --grep blue-staffy-puppies-manchester-uk
  npm run test:render:pages
  npm run test:render:city
  ```
  Expected:
  - The filtered run says it skips the scorecard (a filtered run measures some pages only).
  - The full run has no blocking IMG, LAYOUT or NAV row and no check that examined zero nodes.
  - The four promoted checks pass on Manchester: they block a new page from board approval on (`tests/render/targets.json` `new_page_rule`):
    - `hero-counter-separation`;
    - `h3-image-first`;
    - `sem-section-opening-paragraph`;
    - `sem-title-case-headings`.
  - The city suite passes `city-type-fit` on `/uk-locations/blue-staffy-puppies-manchester-uk/` with London's routes unchanged.

  Fix in the page or its data, confirming each defect on the built page first. A flaky probe is reproduced and fixed in the harness or the component, never re-run until it passes (lessons 20).
- [ ] **Step 3: Regenerate the baseline from the new scorecards.**

  ```bash
  python3 scripts/render_baseline.py --write docs/reports/render-baseline-project4.md
  npm run -s baseline
  ```
  Expected: exit 0, then `--check` with 0 problems. Read the command's output before writing the commit message (lessons 15).
- [ ] **Step 4: Commit.**

  ```bash
  git add data/quality/scorecards/ docs/reports/render-baseline-project4.md src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro
  git commit -m "test(manchester): render gates at 375/768/1280, scorecard and baseline (row 13)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 47 (CONTROLLER invokes the skill): Harden, the impeccable pass (row 14)

**Files:**
- Modify: the page and the Manchester `City*` components it mounts, only for fixes that change no content and no palette
- Create: `docs/reports/impeccable-manchester-${D}.md`, `docs/reports/impeccable-manchester/` (screens)
- Modify: `data/page-runs/blue-staffy-puppies-manchester-uk.json`

- [ ] **Step 1: Run the pass.** The main checkout has no `.claude/launch.json` (it is listed in `.git/info/exclude`). Create it with one configuration:

  ```json
  {"version": "0.0.1", "configurations": [{"name": "bsuk-preview", "runtimeExecutable": "npx", "runtimeArgs": ["astro", "preview", "--port", "4321"], "port": 4321}]}
  ```
  Start it with the Browser pane's `preview_start` (name `bsuk-preview`), never as a background shell job.

  The CONTROLLER invokes the Skill tool with `impeccable:impeccable` on `http://localhost:4321/uk-locations/blue-staffy-puppies-manchester-uk/`. The page is judged at 375, 768 and 1280 in a painting browser (the Browser pane or the Playwright MCP), with screenshots taken section by section into `docs/reports/impeccable-manchester/`. The user's type rule applies: every heading, paragraph and label sized per tier, no chunky headings, and no tall sections or uneven paragraphs (Phase F ruling 6). Findings go to `docs/reports/impeccable-manchester-${D}.md`.
- [ ] **Step 2: Fix or defer each finding.**
  - A fix that changes no content and no visual design is committed with the trailer.
  - A proposed visual change is previewed before it is applied (working rule 6). With the user here: show the before/after in the browser, ask once, and apply only on a yes. With the user away: write it as a preview under `docs/reports/impeccable-manchester/preview/`, log it under the session brief's `## Open Flags`, and record it `--deferred "<reason>"`.
  - The palette never changes.
- [ ] **Step 3: Record the pass.**

  ```bash
  python3 scripts/page_run_record.py blue-staffy-puppies-manchester-uk impeccable --findings <n> --fixed <n> [--deferred "<reason>" ...]
  ```
  `<n>` is the count from Step 1's report. Expected: exit 0.
- [ ] **Step 4: Commit.**

  ```bash
  git add data/page-runs/blue-staffy-puppies-manchester-uk.json docs/reports/impeccable-manchester-*.md docs/reports/impeccable-manchester/
  git commit -m "chore(manchester): impeccable pass recorded (row 14)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 48 (CONTROLLER invokes the skill): Harden, the frontend-design pass (row 15)

**Files:** as Task 47, with `docs/reports/frontend-design-manchester-${D}.md` and `docs/reports/frontend-design-manchester/`.

- [ ] **Step 1: Run the pass.** The CONTROLLER invokes the Skill tool with `frontend-design:frontend-design` the same way: the same page, 375, 768 and 1280, a painting browser, and screens section by section. It runs after Task 47's commit, because row 15's key must follow row 14's.
- [ ] **Step 2: Fix or defer each finding**, as Task 47 Step 2. Preview before apply, and the palette never changes.
- [ ] **Step 3: Record the pass.**

  ```bash
  python3 scripts/page_run_record.py blue-staffy-puppies-manchester-uk frontend-design --findings <n> --fixed <n> [--deferred "<reason>" ...]
  ```
  Expected: exit 0.
- [ ] **Step 4: Commit** with `chore(manchester): frontend-design pass recorded (row 15)` and the trailer. From here on, any edit to the page or its sources stales this pass, and Tasks 47–48 run again.

### Task 49: The static scan and visual intelligence (row 16)

**Files:**
- Create: `docs/superpowers/sessions/${D}-visual-intel-blue-staffy-puppies-manchester-uk.md`

- [ ] **Step 1: Run the static scan.**

  ```bash
  python3 scripts/page_hardening_scan.py uk-locations/blue-staffy-puppies-manchester-uk --fail-on-error; echo "exit $?"
  ```
  Expected: exit 0, with 0 ERROR. Read the examined file list and confirm that it names `src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro`, not a shared scaffold (lessons 2). Triage every WARN in the task report as real, dead code or a false positive. A false positive is fixed in the scanner, with a case in its tests.
- [ ] **Step 2: Run the visual-intelligence report.** Invoke the Skill tool with `bsuk-visual-intelligence` on the built page, against every sibling in the location cluster that `tests/render/targets.json` lists:
  - `uk-locations/blue-staffy-puppies-london`;
  - `uk-locations/blue-staffy-puppies-birmingham`;
  - `uk-locations/blue-staffy-puppies-uk`.

  Write the report to `docs/superpowers/sessions/${D}-visual-intel-blue-staffy-puppies-manchester-uk.md`. It holds the verdict, every score's source, every finding's owner, the verbalization table and the predicate inventory (the row 20 input). Every image with words is read as copy again (lessons 7). A proposed visual change is a preview, as in Tasks 47–48.
- [ ] **Step 3: Commit.**

  ```bash
  git add docs/superpowers/sessions/*-visual-intel-blue-staffy-puppies-manchester-uk.md
  git commit -m "docs(manchester): static scan clean; visual-intelligence report (row 16)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase J: Gates, verification and close (rows 17–21)

### Task 50: Every gate twice (row 17)

**Files:** none tracked. `docs/reports/gate-page/blue-staffy-puppies-manchester-uk.json` is git-ignored (`docs/reports/**/*.json`).

- [ ] **Step 1: Confirm the tree is committed.**

  ```bash
  git status --short
  ```
  Expected: no modified tracked file except `public/search-index.json` or a current `data/page-dates.json`. The untracked `.playwright-mcp/`, `BSUK-london-research/` and `BSUK-outline-fix/` are not this run's and stay untouched.
- [ ] **Step 2: Run the gates.**

  ```bash
  npm run -s build
  npm run gate:page -- blue-staffy-puppies-manchester-uk --skip-record; echo "exit $?"
  python3 scripts/quality_report.py
  python3 scripts/perf_audit.py uk-locations/blue-staffy-puppies-manchester-uk
  ```
  Expected:
  - `gate:page` exits 0 with both runs identical. Each of these runs twice: dup (body and `--headers`), `final_page_audit` `--type location`, hardening, AEO, evidence (`--fail-on-error`, so an unledgered health claim is an ERROR) and `board_gate`. The `listed` step passes.
  - `quality_report.py` §5 is read.
  - `perf_audit.py` reports the warm median of runs 2–5 on `dist/`. Never `--live`: it refuses on the placeholder.

  Any FAIL is confirmed on the page, fixed and committed, and then Tasks 47–48 run again, because the page changed after frontend-design.

### Task 51: Verification before completion (row 18)

**Files:**
- Modify: `data/page-runs/blue-staffy-puppies-manchester-uk.json`

- [ ] **Step 1:** Invoke the Skill tool with `superpowers:verification-before-completion`.
- [ ] **Step 2: Record the verification.** With the tree committed, run:

  ```bash
  python3 scripts/page_run_record.py blue-staffy-puppies-manchester-uk verification \
    --run "npm run -s build" --run "npm run -s check:all" \
    --run "npm run gate:page -- blue-staffy-puppies-manchester-uk --skip-record" \
    --claim "Manchester passes every page gate twice, built from its approved outline and board"
  ```
  Expected: exit 0, with each command's exit code 0 and an examined count above 0.
- [ ] **Step 3: Commit, then run the full gate.**

  ```bash
  git add data/page-runs/blue-staffy-puppies-manchester-uk.json
  git commit -m "chore(manchester): verification-before-completion recorded (row 18)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  npm run gate:page -- blue-staffy-puppies-manchester-uk; echo "exit $?"
  ```
  Expected: exit 0. The full gate re-runs `check:all` itself and checks the run record (`page_run_record.py blue-staffy-puppies-manchester-uk --check`: 0 problems).

### Task 52: The measurement ledger and LLM visibility (rows 19–20)

**Files:**
- Create: `docs/reports/manchester-ledger-table.md` (tracked; its table goes into the gate report in Task 53)

- [ ] **Step 1: Run the ledger.**

  ```bash
  python3 scripts/measurement_ledger.py p5 --slugs blue-staffy-puppies-manchester-uk --md docs/reports/manchester-ledger-table.md
  python3 scripts/measurement_ledger.py p5 --require-pages; echo "exit $?"
  ```
  Expected:
  - M1–M3, M6, M8–M10, M12, M13 and M18 are printed as numbers.
  - `--require-pages` exits 0, with no FAIL or STALE on M1, M2, M6, M8 or M10. Its default scope is every project 5 page in `data/facts/rebuilt.json`: London and Manchester.
  - A STALE M6 means the scorecard is older than the page: re-run Task 46.
  - A STALE M8 means re-gate at HEAD (Task 50).
- [ ] **Step 2: Check LLM visibility.**

  ```bash
  python3 scripts/aeo_audit.py uk-locations/blue-staffy-puppies-manchester-uk --fail-on-error; echo "exit $?"
  ```
  Expected: exit 0. Read it with Task 49's report and `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-10-07.json`. The fetched denominator is 1 of 1 (ChatGPT, banked 2026-09-25). `bsuk_cited` is `false`, because the page is not live. List the engine terms the page still lacks for the gate report.

### Task 53: The close (row 21)

**Files:**
- Modify: `docs/reference/lessons.md`, `docs/reference/session-log.md` (Known Issues), the session brief `docs/superpowers/sessions/${D}-session-brief.md` (`## What's Next`; `grill-me` writes it at the session's open, and today's is `2026-10-07-session-brief.md`)
- Create: `docs/reports/manchester-gate-report.md`, `docs/artifacts/manchester-gate-report.html`

- [ ] **Step 1: Run the close in its fixed order, with no rebuild after gating.**

  ```bash
  npm run -s build
  npm run test:render:pages
  python3 -c "import sys,pathlib;sys.path.insert(0,'scripts');import measurement_ledger as M;print('\n'.join(M.default_slugs(pathlib.Path('.').resolve())))" | while read s; do npm run -s gate:page -- "$s" || echo "GATE FAIL $s"; done
  python3 scripts/rendered_changes.py --base $(git merge-base HEAD foundation) --json
  python3 scripts/measurement_ledger.py p5 --require-pages; echo "exit $?"
  ```
  Expected:
  - The slug list prints `blue-staffy-puppies-london` and `blue-staffy-puppies-manchester-uk`, the project 5 pages, so M10 re-gates dup crossover at this commit for both.
  - No `GATE FAIL` line.
  - `docs/reports/rendered-changes.json` lists `blue-staffy-puppies-manchester-uk`.
  - The ledger exits 0.
- [ ] **Step 2: Lessons, through the learning loop.** Invoke the Skill tool with `bsuk-learning-loop`. Add a `## Manchester (blue-staffy-puppies-manchester-uk), 2026-10-07 to <close date>` section to `docs/reference/lessons.md`, numbered on from 21, in the file's form (family, what happened, why, what holds it now, or **not gated**). It must carry at least these:
  - the rebuilt-but-noindex page that `llms.txt` would have listed (Task 45 Step 3, now gated);
  - the nine thin FAQ wordings that `near_copy_hits` found after STOP 2 (G15);
  - the scaffold's anchors that were not board ids (ruling 3);
  - any escape the Harden passes or the gates found.

  An escape an existing invariant should have caught is charged to the harness (a `known_broken` fixture and a fixed check), not to a new rule.
- [ ] **Step 3: Known Issues.** Invoke the Skill tool with `session-closer`. In `docs/reference/session-log.md` `## Known Issues`:
  - add one numbered entry from 102 on for every open item: links 8 and 9 held on the deposit-order fix; each deferred Harden preview; every `NOT FETCHED` the board and the gate report still carry (Search Console and LLM mentions among them), each with its barrier;
  - mark closed what this run closed;
  - extend the section's preamble sentence with "the Manchester page run added 102–<n>".

  Fill the brief's `## What's Next`.
- [ ] **Step 4: Verify again before any PASS claim.** Invoke `superpowers:verification-before-completion` again before the gate report says PASS.
- [ ] **Step 5: The gate report.** Write `docs/reports/manchester-gate-report.md` in `docs/reports/london-gate-report.md`'s form:
  - the double gate run with each step's two counts;
  - the page-run record;
  - the ledger table from `docs/reports/manchester-ledger-table.md`;
  - other checks at the final HEAD;
  - every `NOT FETCHED` with its barrier;
  - the deferred Harden previews;
  - a `## Open items` section (`tests/py/test_doc_drift.py` requires it).

  Then build the page:

  ```bash
  D=$(date +%F)
  python3 scripts/build_report_artifact.py docs/reports/manchester-gate-report.md docs/artifacts/manchester-gate-report.html "Manchester Gate Report" "BlueStaffyUK rebuild · Project 5" "Manchester page gate report" "BlueStaffyUK — Manchester page gate report" "status: PASS" "$D" docs/reports/manchester-gate-report.md
  python3 -m pytest -q tests/py/test_doc_drift.py
  ```
  Expected: the page is written, and the drift test passes.
- [ ] **Step 6 (CONTROLLER):** Read `docs/artifacts/manchester-gate-report.html` in full, then publish it as an Artifact: icon `check`, `capabilities={"downloads": true}` (copy buttons and a `.md` download).
- [ ] **Step 7: Commit, as the close's last step** (lessons 21: the report records HEAD, so it is committed after gating).

  ```bash
  git add docs/reference/lessons.md docs/reference/session-log.md docs/superpowers/sessions/ docs/reports/manchester-gate-report.md docs/reports/manchester-ledger-table.md docs/artifacts/manchester-gate-report.html public/search-index.json data/page-dates.json
  git commit -m "docs(close): Manchester gate report and ledger table, lessons and Known Issues (row 21)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```
  Never push.

### Task 54 (CONTROLLER): The user approves or fails the page; noindex comes off only on approval

**Files:**
- Modify: `src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro` (robots), `tests/py/test_manchester_page.py`, `tests/py/test_manchester_scaffold.py`, `tests/py/test_llms_txt_build.py`, `public/llms.txt` (through `npm run llms`)
- Create: `docs/reference/answer-board/answers/final-approval-blue-staffy-puppies-manchester-uk-${D}.md`

- [ ] **Step 1: Ask one either/or question in chat** (a single blocking pick, so not a board batch):

  > "Manchester is built and passes every gate twice (gate report: <the Artifact URL from Task 53>). Approve it to come out of noindex, or fail it with what to change?"

  End the turn and wait.
- [ ] **Step 2: On a fail.** Log each point under Open Flags. Each fix re-enters at the row it belongs to: copy at Task 44, which then re-runs Tasks 45–53; a visual change goes through a preview first (working rule 6).
- [ ] **Step 3: On approval, save the answer and update the tests first.** Save the user's words, with the date and the gate report URL, as `docs/reference/answer-board/answers/final-approval-blue-staffy-puppies-manchester-uk-${D}.md`.
  - In `tests/py/test_manchester_page.py`, replace `test_noindex_until_the_user_approves_the_page` with:

    ```python
    def test_indexable_and_in_the_sitemap_since_the_user_approved_it():
        html = built()
        assert re.findall(r'<meta name="robots" content="([^"]*)"', html) == ["index, follow"]
        assert 'robots="noindex' not in SRC.read_text(encoding="utf-8")
        shards = [s.read_text(encoding="utf-8") for s in (ROOT / "dist").glob("*sitemap*.xml")]
        assert shards and [s for s in shards if f"/uk-locations/{SLUG}/<" in s], "Manchester is in no sitemap shard"
    ```
  - In `tests/py/test_manchester_scaffold.py`, delete `test_the_scaffold_is_noindex_and_in_no_sitemap`. `tests/py/test_city_scaffold.py::test_every_scaffold_is_noindex_and_in_no_sitemap` still guards any future scaffold.
  - In `tests/py/test_llms_txt_build.py`, replace `test_a_rebuilt_page_still_noindex_stays_out` with:

    ```python
    def test_manchester_is_listed_since_the_user_approved_it(tmp_path):
        text = build_llms_txt.main(tmp_path / "llms.txt").read_text(encoding="utf-8")
        assert "- [Blue Staffy Puppies Manchester UK](/uk-locations/blue-staffy-puppies-manchester-uk/)\n" in text
    ```
    The title is the page-map row's, and a replaced stub is listed with no word count. In `test_listed_page_count_matches_indexable_rows`, change `23` to `24`.

  ```bash
  npm run -s build
  python3 -m pytest -q tests/py/test_manchester_page.py tests/py/test_llms_txt_build.py
  ```
  Expected: FAIL on the new indexable test and on the two `llms` tests.
- [ ] **Step 4: Flip the robots value.** In the page, delete `robots="noindex, follow"` so that the layout default `index, follow` renders, as London did (f3031626). Update the file-top comment's "kept out of the index" paragraph to say the user approved the page on `${D}`, citing the answer file. Then:

  ```bash
  npm run llms
  npm run -s build
  python3 -m pytest -q tests/py/test_manchester_page.py tests/py/test_manchester_scaffold.py tests/py/test_city_scaffold.py tests/py/test_llms_txt_build.py
  npm run -s check:sitemaps; echo "exit $?"
  ```
  Expected: PASS, and `check:sitemaps` exits 0 with Manchester among the indexable URLs.
- [ ] **Step 5: Commit, then re-run the close.**

  ```bash
  git add src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro tests/py/test_manchester_page.py tests/py/test_manchester_scaffold.py tests/py/test_llms_txt_build.py public/llms.txt public/search-index.json docs/reports/sitemaps.md docs/reference/answer-board/answers/final-approval-blue-staffy-puppies-manchester-uk-*.md
  git commit -m "feat(manchester): take noindex off — the user approved the page

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```
  The page changed after frontend-design, so Tasks 47–48 run again (the passes re-record), and then Tasks 50–53 run in order. The gate report is updated in place, and the Artifact is republished to the same URL. Never push, and do not merge into `foundation` until the user says so.
- [ ] **Step 6: The key.** Remind the user to delete `GEMINI_API_KEY` from `.env`: no image work remains for this page (Task 40 Step 4, London handoff).

### Phases H–J: order, parallelism and who does what

- **Order:** 41 → 42 → 43 → 44 → 45 → 46 → 47 → 48 → 49 → 50 → 51 → 52 → 53 → 54 (the user's approval) → 47, 48, 50–53 again.
- **CONTROLLER:**
  - Task 41 Steps 2–3 when a record change is needed;
  - the heading and FAQ hits in Task 44 Step 5;
  - Tasks 47 and 48 (the two Harden skills, invoked by name with the Skill tool);
  - Task 53 Step 6 (the Artifact);
  - Task 54;
  - every preview shown to the user.
- **Implementers:** everything else, one Opus implementer per task. The controller reads every agent's diff before accepting it (lessons 3). No two tasks run in parallel: each one builds on the page the task before it left.
- **The user decides twice:** each visual change a Harden pass proposes (a preview), and the page's approval (Task 54).

## Phases G–J (rows 11–21) — written out

Phases G–J are now written out in full above: Phase G (row 11, STOP 4) as Tasks 39–40, and Phases H–J (rows 12–21) as Tasks 41–54. Both were written on 2026-10-07, after STOP 3 was approved (3a4251a7), and every command in them was checked against the tree at 6c0ad36d. They follow London's Tasks 24–37 command for command, with the slug `blue-staffy-puppies-manchester-uk`, the route `uk-locations/blue-staffy-puppies-manchester-uk` and the research folder `docs/research/manchester-page-run/`. Where London's commands differ from the tree today, the difference is stated in the task:
- the close's gate report is `docs/reports/manchester-gate-report.md` and `docs/artifacts/manchester-gate-report.html`, as London actually shipped (`docs/reports/london-gate-report.md`, `docs/artifacts/london-gate-report.html`), not the plan's `p5-london-*` names;
- the close gates the project 5 pages (`measurement_ledger.default_slugs`), not every page in `data/facts/rebuilt.json`.

Manchester's own differences: its components were designed at row 10 (ruling 2); `python3 scripts/dup_content_audit.py --headers` runs straight after the first build (Task 44 Step 5); every image with words is read as copy before STOP 4 and again at row 16; the nine STOP 3 FAQ wordings and links 8 and 9 held (Phase H–J rulings 2 and 4).

## Self-review

- Spec coverage: rows 1–8 → Tasks 1–12; KI 99 → Task 13; rows 9–21 → Phases E–J. The user's asks — primary and secondary keywords, every keyword category, fan-out, intent split, strategies — map to Tasks 8, 6, 11 (`intent`) and 10.
- No step names a script that `npm run check:workflow` cannot resolve.
