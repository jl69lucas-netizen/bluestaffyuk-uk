# Session handoff — BlueStaffyUK

Continue this project in a new chat. Everything below was read from the repo by `python3 scripts/session_handoff.py`; nothing is from memory.

## Where

- Worktree: `/Users/apple/Downloads/BSUK/BSUK-london`
- Branch: `london-components`
- HEAD: `c9a8b0b0`
- git status: dirty (1 changed paths)

## Last 10 commits

- c9a8b0b0 docs(session): mark the London brief's open flags as history and the board-v3 plan as complete, for the handoff
- c32968a3 docs(session): fill What's Next in the London run brief at the close (session-closer)
- 88a80f39 fix(route): a gate run stays current across docs-only commits; the gate report page regenerated at the final close
- dbf23db6 docs(close): London gate report and ledger table, gated at 5b20b9cc after the breeder's approval
- 5b20b9cc docs(page-run): record London's verification before completion (build, check:all, gate:page --skip-record, all exit 0; check:all examined 27)
- dbc05a46 docs(page-run): record London's frontend-design Harden pass, fourth run (0 findings; 375/768/1280)
- 069ed826 docs(harden): London's frontend-design pass, fourth run (0 findings; 375/768/1280)
- ad2c9c40 docs(page-run): record London's impeccable Harden pass, fourth run (1 finding, 1 fixed; 375/768/1280)
- f0d155b1 fix(dial): the dial scrolls its own box to show the row it marks (impeccable Harden pass 2026-10-06b, F1)
- fab1d951 docs(known-issues): 100 London's puppy cards without photos (deferred to project 6); 101 PageDial's batch-only scroll spy

## Newest session brief

`docs/superpowers/sessions/2026-09-30-session-brief.md`

### Open Flags

- **Closed 2026-10-06 (session-closer):** London is done, approved and merged into `foundation`. Every flag below is London history, kept as the record, and none blocks the next page. The newest plan, `docs/superpowers/plans/2026-10-03-london-board-v3.md`, is complete: STOP 3 was approved at f27ab66, and its unticked boxes are lag, not open work. The next session starts from What's Next below, with a new plan for the next city.
- **Research on hand:** a gap matrix exists (2026-09-23 and 2026-09-25), and so does the LLM-intel file for London (2026-09-25). `data/queries/` has no London query file, so competitor research and fan-out (page-run rows 4–7) are still to run.
- **Board:** London has no approved page board. That is expected; it comes at STOP 3.
- **Audit:** London has not been through `@bsuk-content-audit-agent`. It is a stub with 4 words, so an audit adds little; the research board covers the intent and gaps.
- **Hub:** `/uk-locations/` is built. Known Issue 86: the UK hub's body does not link the indexable city pages.
- **Deposit refund clause (Ruling 2 of the London plan):** the user's condition is "if you change your mind up to 1 day before collection or delivery" (deposit-wording batch Q3 (b), 2026-09-27), which supersedes this brief's "if a visitor fails to show up". It lives on the unmerged `deposit-wording` branch; `data/settings.json` has no refund-wording key. London prints `depositLine` with no refund wording until that branch is merged (the user's call).
  - **Superseded 2026-09-30 (user, in chat):** "ignore that or just write when build the page, go to the next task". The `deposit-wording` branch is no longer awaited. At the build (Task 23 onward), the refund clause — the deposit is up to 70% refundable if you change your mind up to 1 day before collection or delivery — is added as a data key in `data/settings.json` and the London page reads it from there, never typed. The STOP 1 answer to q07 ((a), wait for the push) is replaced by this ruling. The outline carries the clause in the deposit section.
  - **Landed 2026-09-30 (Task 21 review):** the clause is now `data/settings.json` `deposit_refund_clause` (with `deposit_refund_clause_source`); the London board's rows 8 and 14 point at that key. The approved research board's S2 trade-off ("its lead answer waits on the refund wording … can say what the deposit does" but not when the money comes back) is superseded by this key; the research-board record is left as approved, not edited.
- **Served alt with an unproven result (Task 21 review, 2026-09-30):** `/images/breeder-sitting-blue-staffy-puppy-home.webp` is served on `/blue-staffy-uk-breeders/` with the alt "… Responsible breeders of blue Staffies L-2-HGA clear." That states a DNA result no file backs (working rule 9; plan Ruling 4; evidence ledger `parents-dna-clear` NOT FETCHED — none held). The London board drops the clause in `verbatim.changed`; the breeders page still serves the alt, and correcting it there is a separate decision for the user.
- **FAQ total 21 against the 15–20 cap (Task 27, 2026-10-03):** the approved board carries 21 FAQ questions (top 6, middle 7, bottom 8, since the breeder's q04 of 2026-10-02 added "How Rare Are Blue Staffies?"), and the London page renders all 21. `scripts/query_coverage_check.py` caps a location page at `FAQ_TOTAL_MAX` 20 (plan Ruling 9), so once London is in `data/facts/rebuilt.json` (Task 28) `check:queries` reports `FAQ total: 21, want 15–20` and nothing else. One narrow question for the user: drop one of the two promoted top-block questions ("Where Can I Find Blue Staffy Breeders in the UK?" is the weaker), or allow 21 on this page. Not widened, not dropped: the page follows the approved board until the user answers.
- **External link live checks (Task 19, 2026-09-30):** `curl -sIL` to all six external hosts returned `000`: the session egress proxy refuses CONNECT with 403 (policy). Each is recorded `NOT FETCHED — egress proxy CONNECT 403` in `docs/research/london-page-run/links-plan.md`, with a Firecrawl `maxAge: 0` scrape returning 200 recorded beside it as a second source. This departs from the plan's "keep only 200s" (Task 19 Step 2). Re-run the curl checks from an unrestricted network before launch (project 6).

### What's Next

_Filled by session-closer, 2026-10-06. London closed: approved, indexable, gate PASS at 88a80f39; `london-components` fast-forwarded into `foundation` (local only, no push until project 6)._
1. **The next project 5 city page.** Walk `docs/reference/page-run.md` from row 1. Row 1 now reads `docs/reference/lessons.md` first. Before its research board, run Known Issue 99: tune the location word-count ceilings in `data/quality/evidence-budgets.json` against London's real counts. Also run the duplicate-content gate straight after the first build (lessons, entry 18), not first at the close.
2. **Known Issue 101:** port the scroll-spy fix (`src/lib/scrollSpy.ts`, 9010e4f4) to `src/components/kit/PageDial.astro` on the twelve pre-project-5 pages, with its test.
3. **Lessons marked "not gated"** (`docs/reference/lessons.md`): turn the cheapest into tests. Candidates: text inside generated images read as copy before the board (entry 7); alts checked against their image at the Asset Gate (entry 8); a fact-correction sweep (entry 19).

## Plan

- Newest plan: `docs/superpowers/plans/2026-10-03-london-board-v3.md`
- First task with an unchecked step: ### Task 1: Approve-button refusal names what is missing (small, do first)
- The plan's checkboxes are ticked by hand and can lag the commits: compare this task with the commit log above before starting it.

## Boards and Artifacts

- https://claude.ai/artifact/DKEoYmE3AUtyXafHKesx8n
- https://claude.ai/artifact/PJqqDhC5aeCXRcSUr7kTrs
- https://claude.ai/artifact/RJscU1NMGaL4ijCn2sxpvi
- https://claude.ai/artifact/AVKRRvthQ6wqgvwBp8DBDJ
- https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf

## Standing instructions

- Read CLAUDE.md, docs/reference/page-run.md, the newest brief and MEMORY.md first
- Watch the answer board and any open page board with ArtifactComments at session start
- Commit after every task; never push unless the user explicitly says so (CLAUDE.md rule 3).

## Gemini

- GEMINI_API_KEY is set in .env — delete it when image work is done (breeder's instruction, 2026-10-02)
- Gemini usage (UTC): today 0, total 6; by status — 200: 1, 402: 3, 404: 1, RuntimeError: 1
