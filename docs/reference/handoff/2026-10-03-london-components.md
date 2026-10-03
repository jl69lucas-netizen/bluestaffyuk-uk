# Session handoff — BlueStaffyUK

Continue this project in a new chat. Everything below was read from the repo by `python3 scripts/session_handoff.py`; nothing is from memory.

## Where

- Worktree: `/Users/apple/Downloads/BSUK/BSUK-london`
- Branch: `london-components`
- HEAD: `e8b849d1`
- git status: clean

## Last 10 commits

- e8b849d1 docs: answer-board batch JSON — approve London board v3
- aae48d25 docs: answer-board batch — approve London board v3 (published, version 3); plan follow-ups from Task 9
- 9d628bec fix(task 7 review): sourced-only rarity answer, quote-traced FAQ test, URL-first neutraliser, component share refused at approval
- 9af8c184 docs(skill): bsuk-infographic cites heights.json by its full path only (test_rules_index path guard)
- d2b8c62e answer-board: marker pass in the receive step — scripts/answer_board_save.py --neutralise
- c02a7e15 rules(design): own components per page — no two new-family boards share a section component (breeder q10, 2026-10-02)
- 782a0e3c docs(session-log): close Known Issue 70 — the real smoke image passed the negative list (breeder q09, 2026-10-02)
- 289162d6 rules(copy): FAQ placement method A (intent spread) is the rule for every new page (breeder q05, 2026-10-02)
- 6f23f946 faq(london): answer "How Rare Are Blue Staffies?" in the bottom FAQ block (breeder q04, 2026-10-02)
- b54a80d3 feat(board): Google result preview, structured-data preview, internal-link map, page-weight budget (breeder q12, 2026-10-02)

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

- Newest plan: `docs/superpowers/plans/2026-10-03-london-board-v3.md`
- First task with an unchecked step: ### Task 1: Approve-button refusal names what is missing (small, do first)
- The plan's checkboxes are ticked by hand and can lag the commits: compare this task with the commit log above before starting it.

## Boards and Artifacts

- https://claude.ai/artifact/5aMizcnA5f4TJ3RSRhw1fx
- https://claude.ai/artifact/CbemmwUeW5qGEmEFog7ezz
- https://claude.ai/artifact/UCZrjbPCMzksbhoTNT97yJ
- https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf

## Standing instructions

- Read CLAUDE.md, docs/reference/page-run.md, the newest brief and MEMORY.md first
- Watch the answer board and any open page board with ArtifactComments at session start
- Commit after every task; never push unless the user explicitly says so (CLAUDE.md rule 3).

## Gemini

- GEMINI_API_KEY is set in .env — delete it when image work is done (breeder's instruction, 2026-10-02)
- Gemini usage (UTC): today 0, total 6; by status — 200: 1, 402: 3, 404: 1, RuntimeError: 1
