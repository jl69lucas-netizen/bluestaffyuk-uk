# Session handoff — BlueStaffyUK

Continue this project in a new chat. Everything below was read from the repo by `python3 scripts/session_handoff.py`; nothing is from memory.

## Where

- Worktree: `/Users/apple/Downloads/BSUK/BSUK-london`
- Branch: `london-components`
- HEAD: `d8d5db81`
- git status: dirty (4 changed paths)

## Last 10 commits

- d8d5db81 skill: bsuk-competitor-parity — match type by type, close 2+-domain gaps, beat on evidence
- 32013e33 fix(board): infographic plan faults as BoardError, per-page pending slots, one plan per render, js() escapes <!--
- 43034c96 fix(board): server-side ig/og pick checks, slot picks carried on re-board, 7d wording
- 1905d46d log: two Gemini smoke attempts with the third key (402, credits depleted; one client-closed script error)
- 15a3f093 feat(board): v2 blocks 1b, 4c, 4d, 5c, 7c, 7d on project 5 boards
- 0406fc25 fix(board): review fixes — whole-phrase names, case-insensitive unnaming, bounded intent cues; Gemini log counts malformed lines
- 561b0b8c fix(board): OG slot subjects and briefs never name a real dog, person or litter (rule 9)
- b6496bf3 feat: Gemini usage log (no key ever written) and the delete-the-key reminder
- 32002e75 feat(board): 4–5 OG slot proposals, share card first (block 7d)
- 1e68ed36 plan(board v2): Task 6b Gemini usage log and delete-the-key reminder; review carry-overs into Tasks 7 and 10

## Newest session brief

`docs/superpowers/sessions/2026-09-30-session-brief.md`

### Open Flags

- **Research on hand:** a gap matrix exists (2026-09-23 and 2026-09-25), and so does the LLM-intel file for London (2026-09-25). `data/queries/` has no London query file, so competitor research and fan-out (page-run rows 4–7) are still to run.
- **Board:** London has no approved page board. That is expected; it comes at STOP 3.
- **Audit:** London has not been through `@bsuk-content-audit-agent`. It is a stub with 4 words, so an audit adds little; the research board covers the intent and gaps.
- **Hub:** `/uk-locations/` is built. Known Issue 86: the UK hub's body does not link the indexable city pages.
- **Deposit refund clause (Ruling 2 of the London plan):** the user's condition is "if you change your mind up to 1 day before collection or delivery" (deposit-wording batch Q3 (b), 2026-09-27), which supersedes this brief's "if a visitor fails to show up". It lives on the unmerged `deposit-wording` branch; `data/settings.json` has no refund-wording key. London prints `depositLine` with no refund wording until that branch is merged (the user's call).
  - **Superseded 2026-09-30 (user, in chat):** "ignore that or just write when build the page, go to the next task". The `deposit-wording` branch is no longer awaited. At the build (Task 23 onward), the refund clause — the deposit is up to 70% refundable if you change your mind up to 1 day before collection or delivery — is added as a data key in `data/settings.json` and the London page reads it from there, never typed. The STOP 1 answer to q07 ((a), wait for the push) is replaced by this ruling. The outline carries the clause in the deposit section.
  - **Landed 2026-09-30 (Task 21 review):** the clause is now `data/settings.json` `deposit_refund_clause` (with `deposit_refund_clause_source`); the London board's rows 8 and 14 point at that key. The approved research board's S2 trade-off ("its lead answer waits on the refund wording … can say what the deposit does" but not when the money comes back) is superseded by this key; the research-board record is left as approved, not edited.
- **Served alt with an unproven result (Task 21 review, 2026-09-30):** `/images/breeder-sitting-blue-staffy-puppy-home.webp` is served on `/blue-staffy-uk-breeders/` with the alt "… Responsible breeders of blue Staffies L-2-HGA clear." That states a DNA result no file backs (working rule 9; plan Ruling 4; evidence ledger `parents-dna-clear` NOT FETCHED — none held). The London board drops the clause in `verbatim.changed`; the breeders page still serves the alt, and correcting it there is a separate decision for the user.
- **External link live checks (Task 19, 2026-09-30):** `curl -sIL` to all six external hosts returned `000`: the session egress proxy refuses CONNECT with 403 (policy). Each is recorded `NOT FETCHED — egress proxy CONNECT 403` in `docs/research/london-page-run/links-plan.md`, with a Firecrawl `maxAge: 0` scrape returning 200 recorded beside it as a second source. This departs from the plan's "keep only 200s" (Task 19 Step 2). Re-run the curl checks from an unrestricted network before launch (project 6).

### What's Next

(empty — run the session-closer skill to fill it)

## Plan

- Newest plan: `docs/superpowers/plans/2026-10-02-london-board-v2.md`
- First task with an unchecked step: ### Task 1: Per-term density against each competitor (`term_density.py`)
- The plan's checkboxes are ticked by hand and can lag the commits: compare this task with the commit log above before starting it.

## Boards and Artifacts

- https://claude.ai/artifact/H4cJdmjeYt28NANi4Ao3S4
- https://claude.ai/artifact/5aMizcnA5f4TJ3RSRhw1fx
- https://claude.ai/artifact/CbemmwUeW5qGEmEFog7ezz
- https://claude.ai/artifact/UCZrjbPCMzksbhoTNT97yJ
- https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf

## Standing instructions

- Read CLAUDE.md, docs/reference/page-run.md, the newest brief and MEMORY.md first
- Watch the answer board and any open page board with ArtifactComments at session start
- Commit after every task; do not push unless the user says so

## Gemini

- GEMINI_API_KEY is set in .env — delete it when image work is done (breeder's instruction, 2026-10-02)
- Gemini usage (UTC): today 5, total 5; by status — 402: 3, 404: 1, RuntimeError: 1
