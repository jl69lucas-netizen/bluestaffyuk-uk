# Session Brief — 2026-10-07

> **Status:** READY — interview complete (grill-me `--brief`: the user's chat message of 2026-10-07 is the brief; the repo answered the rest, so no question was left to ask).
> **Last updated:** 2026-10-07

## Q&A Log (Verbatim)

**Brief (user, chat, 2026-10-07):** "We work on the Next page, invoke all the skills and agents needed for these job, i want to see them and add them visually to the BSUK route mod, and will all the BSUK mods from the other sessions work here. START WITH SPRINT 0 RESEARCH PRIMARY, secondary KEYWORDS, all categories, Fan-out-, INTENT SLIT, strategies, give SAME DELIVERABLEs on the boards. Check the workflow, boards, gates/stop, skills/agents and make sure all of them are fine for the next page, etc"

**Q1 — Outcome (from the brief):** Sprint 0 research for the next city, with the same deliverables London's research board carried, ending at STOP 1 (the research board).
**Q2/Q3 — Traffic / worst performer:** NOT FETCHED — GSC property unverified (domain expired); no exports on disk (Known Issue 14, `data/page-map.json`). The page comes from the approved build order instead.
**Q5 — Constraints:** the standing rules only (CLAUDE.md working rules 1–17; never push; locked facts from `data/settings.json`, `data/puppies.json`, `data/price-matrix.json`).
**Q6 — Target (from the repo):** `/uk-locations/blue-staffy-puppies-manchester-uk/` — row 2 of Strategy A's build order (`docs/superpowers/sessions/2026-09-25-location-pages-strategy.md`, Concrete Artifact), after London. Keyword-gap 10 (3+2+3+2) high; matrix city 11/20.
**Q7 — Done (this session):** the Manchester research board published as an Artifact with copy buttons and `.md`, its picks posted as one answer-board batch (STOP 1). The run stops there until the user picks.
**Q8 — Reader:** the ranked buyer fears (scam / deposit, licensing, puppy farm, sick puppy, support, cost), for a Greater Manchester buyer 120 miles from Carlisle.
**Q9 — Benchmark:** London, our own closed page (`/uk-locations/blue-staffy-puppies-london/`, gate PASS 88a80f39) — its research board is the deliverable to match.
**Q10–Q12 — Framework, AIO, visuals:** not asked here — they are research-board picks (row 8) and outline rows (row 9), chosen by the user at STOP 1 and STOP 2.
**Q13 — Repeat / avoid (from the 2026-09-30 brief's What's Next and `docs/reference/lessons.md`):** run Known Issue 99 (calibrate `budgets.location`) before Manchester's STOP 3, from Manchester's and London's top-5 competitor pages; run `python3 scripts/dup_content_audit.py --headers` straight after the first build (lessons 18); read every image with words as copy (lessons 7); check every alt against its image at the Asset Gate (lessons 8); check buyer advice against our own facts before the outline (lessons 9); own components per page (London's fifteen are London's).
**Q14 — Urgency:** none stated.

## Decisions Log

- **STOP 1 approved (user, answer board, 2026-10-07T01:38):** M1 colour comes last; S2 blue H1 / for-sale title; every recommended framework and header Style 2; blue stays primary for the H1; keyword universe as shown; 2,000–3,000 words; no council link; colour/price said of this litter only; no rescue wording; keep the DNA FAQ pick, answered with the tests and certificates on request; KI 99 option (a), density ceilings on block 4c's counter. **q08 note: drop the live video call on Manchester's page** (London leads with it; Manchester takes a different angle) — no settings key is added.
- **Board layout: Option A, field cards (user, 2026-10-07, in chat: "A everything look nice", then "i choose A").** Preview https://claude.ai/artifact/VtcsZjjprL3yzWTbMHN4V5 (`docs/artifacts/research/previews/manchester-option-a.html`). Colours by role: Recommended gold, why blue, weakness/wedge green, trade-off rust, NOT FETCHED violet dashed. Applied to the board generators after the `.md`-download task lands (it edits the same renderer). Long paragraphs: **Option 2, plain summary first** (user, 2026-10-07, "Go forr Option 2"; preview https://claude.ai/artifact/X78w7EuhsqYWEoV6TpvPi3): 4–6 plain bullets, a 'What it cost' box and a 'Read with care' box lead each long section or card, with the exact original folded underneath and still what the copy button copies. Applies to every board.
- Next page is Manchester (Strategy A row 2). Branch `manchester-page`, cut from `foundation` at 15236191, in the main checkout.
- grill-me run in `--brief` mode from the chat message; framework, AIO and visual choices go to the research board and outline as picks.
- Manchester's question file (`data/queries/blue-staffy-puppies-manchester-uk.json`) is from 2026-09-23, before London's format: it has no `word_target`, no keyword volumes, no neighbourhood terms and no backlinks. Row 5 refreshes it through the spend guard (counted $0.51 of the $1.00 total cap; London's refresh cost $0.22).
- The route mod (`tools/claude-mods/bsuk-route`) now shows each row's skills and agents from page-run.md, ticked as they run (5e99d0ea); the three mods were copied into this session's dev-mods folder.

## Open Flags

- **STOP 1 posted (2026-10-07):** research board https://claude.ai/artifact/WydQDtbxSc4WdJ5mfFEhkN; batch `2026-10-07-research-board-blue-staffy-puppies-manchester-uk` (12 questions) on the answer board. Nothing from row 9 on starts until the picks are saved and stamped with `python3 scripts/research_board.py blue-staffy-puppies-manchester-uk --approve --answers <file>`.
- **Board template — the `.md` download link does nothing in the Artifact viewer** (publish warning, 2026-10-07): the viewer never grants pages download permission. London's board shares the template. Fix in the renderer (declare the `downloads` capability and save through it), separately from this page.
- **[Closed by STOP 1 q08: the video call is dropped from Manchester's page]** Video call before deposit is not a data key (Task 10, strategies): the offer lives only in London's plan ruling 1 and `ont:video-call-before-deposit`; `data/settings.json` has no key. Pages state facts from data only, so the key is asked for in the STOP 1 batch and added before STOP 2.
- **Owner language — parked (user, 2026-10-07):** Reddit is refused by every fetcher this session can use (Firecrawl, WebFetch, headless Playwright 403, Claude in Chrome and the app browser by safety policy). The research-recency ladder's last rung, `/last30days`, is a third-party plugin (github.com/mvanhorn/last30days-skill) the user could not install from the terminal; "we can come back to it later". The research board carries owner language as NOT FETCHED with that barrier, plus the 21 banked thread questions.
- **LLM intel date (Task 7):** `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-10-07.json` records `fetched_on: 2026-09-23`, but the banked ChatGPT answer was bought 2026-09-25 (its `_saved_note`). On an unpaid run the intel script takes the date from `data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.json` (an older condensed save, still 09-23). The research board states 2026-09-25 from the saved note; fixing the condensed file belongs to bsuk-query-augmentation.
- **Question file — a health-result FAQ pick got through (Task 4, 2026-10-07):** the rebuilt `data/queries/blue-staffy-puppies-manchester-uk.json` picks "Are both parents DNA tested clear for L-2-HGA and HC-HSF4?" (middle block, `bank:health-dna-tests`) in place of "Can I see the genetic test results…". Its wording assumes a result we never state (working rule 9; lessons 9; Known Issue 98). The builder skill says `scripts/query_augment.py` blocks a question only a `parents-dna-clear` row could answer, and it did not block this one — charge it to the harness (a known-broken fixture, then the fix), decided before STOP 2.
- **Live SERP drift (Task 4):** the live Google read of 2026-10-07 has Staffie Owners' Bolton blue facet at #3 (#6 in the banked 2026-09-23 SERP). The pool stays the banked SERP; adding Bolton is a free curl and a rebuild if the user wants it.
- **Word target:** `NOT FETCHED — fewer than two prose competitor pages (1 used)`, as London — the word band is the user's pick on the research board.
- **Workflow check — grill-me's description says "Run AFTER Sprint 0 intelligence is complete"**, while page-run row 1 runs it first at session open. The run follows page-run.md; the skill's description should say so.
- **Workflow check — row 11 (Asset Gate) names no image skill** (`bsuk-image-generation`, `bsuk-photo-ingest`, `image-metadata`), so the route map shows none there.
- **Known Issue 99** blocks Manchester's gate:page; it is calibrated after row 5 fetches Manchester's competitor pages, before STOP 3.
- **Audit:** the page is a 5-word noindex stub, so `@bsuk-content-audit-agent` adds little (as London); the research board covers intent and gaps.
- **LLM visibility:** not cited — chatgpt, 2026-09-25 (`docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json`, provisional: question-file source). Refreshed at row 5.
- **Hub:** `/uk-locations/` is built (Known Issue 86: its body does not link the indexable city pages).

---
<!-- Synthesized fields below are filled in at finalization, from the Q&A Log above. -->

## Business Focus
Turn the second most contested city stub into a real one-breeder Manchester page, beating the marketplace town pages (Pets4Homes, Staffie Owners, Gumtree, Freeads, Puppies.co.uk) that hold the SERP today.

## SESSION CONTEXT
- Page Type: location
- Target Keyword: blue staffy puppies manchester (the question file's primary; the strategy row's target is "staffordshire bull terrier puppies for sale in manchester greater manchester")
- Framework: research-board pick (STOP 1)
- Framework Reason: research-board pick (STOP 1)
- AIO / GEO Approach: research-board pick (STOP 1)
- AIO Notes: not cited by chatgpt (2026-09-25); refreshed at row 5
- Component Style: own components per page (`rules/design.md` `own-components-per-page`), chosen after STOP 2
- Visual Plan: outline rows (STOP 2), then the Asset Gate (STOP 4)
- Audit Status: not needed — stub (see Open Flags)
- LLM Visibility: not cited — chatgpt, 2026-09-25
- Structure.json Entry: city spoke → `/uk-locations/`, listing, buying guide (strategy row)
- Hub Page: /uk-locations/
- Internal Links Needed: TBD at the outline (row 9) and the board (rule 12)

## Today's Target
- Page: /uk-locations/blue-staffy-puppies-manchester-uk/
- Goal: Sprint 0 research and the research board (STOP 1)
- Reader: a Greater Manchester buyer afraid of a deposit scam and a farmed or sick puppy
- Benchmark: London's research board

## Constraints
- **CONSTRAINT:** never push (working rule 3); commit after every task.
- **CONSTRAINT:** no fabricated figures — anything not fetched is `NOT FETCHED — <barrier>` (working rule 9).
- **CONSTRAINT:** paid fetches only through the spend guard (`scripts/query_augment.py`).

## Repeat / Avoid
- Repeat: London's research-board deliverable, section for section; every visual choice previewed.
- Avoid: London's escapes in `docs/reference/lessons.md` (entries 7, 8, 9, 18, 19 above all).

## Urgency
None stated.

## Recommended Next Steps
`superpowers:writing-plans` (Manchester's plan) → `bsuk-location-page-builder` → `python3 scripts/page_run_record.py blue-staffy-puppies-manchester-uk session-open --builder bsuk-location-page-builder` → page-run rows 2–8.

## What's Next
