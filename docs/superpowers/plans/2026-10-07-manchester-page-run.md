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

## Phases F–J (rows 10–21) — after STOP 2

These follow London's plan Tasks 18–37 command for command, with the slug `blue-staffy-puppies-manchester-uk`, the route `uk-locations/blue-staffy-puppies-manchester-uk`, research folder `docs/research/manchester-page-run/`, and these differences: Manchester's own components are designed at row 10 (ruling 2) on the board's three styles at 1280 / 768 / 375; `python3 scripts/dup_content_audit.py --headers` runs straight after the first `npm run build` at row 12; every image with words is read as copy before STOP 4. Each phase is written out in full in this file once the stop before it is approved, so its commands are checked against the tree as it stands then.

## Self-review

- Spec coverage: rows 1–8 → Tasks 1–12; KI 99 → Task 13; rows 9–21 → Phases E–J. The user's asks — primary and secondary keywords, every keyword category, fan-out, intent split, strategies — map to Tasks 8, 6, 11 (`intent`) and 10.
- No step names a script that `npm run check:workflow` cannot resolve.
