# Board Readability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every board reads easily: the user's two picks of 2026-10-07 are built into the board generators. The layout is **Option A, field cards** with a colour per role (preview https://claude.ai/artifact/VtcsZjjprL3yzWTbMHN4V5). The paragraphs follow **Option 2, plain summary first** (preview https://claude.ai/artifact/X78w7EuhsqYWEoV6TpvPi3).

**Architecture:** One shared presentation layer, `scripts/board_style.py`, holds the CSS (role-colour tokens in both themes, card, field, legend and summary styles) and the client-side layout script. Each generator includes it: `scripts/research_board.py` first, then `scripts/outline_matrix.py` and `scripts/build_page_board.py`. The markdown stays the single source, and every copy button still copies the exact markdown. Plain summaries are data: the record's `summaries` key holds `sections` (by section title) and `items` (by record path). They are rendered above the original, which sits folded in a `<details>`.

**Tech Stack:** Python 3 generators, pytest under `tests/py/`, marked + DOMPurify in the page (already loaded), the Artifact tool for republishing.

**Order constraint:** the `.md`-download fix (branch `artifact-downloads`, worktree `.claude/worktrees/eager-wescoff-a1dc05`) edits the same generators. Task 1 waits for it to finish and for the user's word to merge it.

---

### Task 1: Bring in the download fix
- [ ] When the `artifact-downloads` session reports done, ask the user once in chat: merge `artifact-downloads` into `manchester-page`?
- [ ] On yes: `git merge --no-ff artifact-downloads`, then `python3 -m pytest -q tests/py/test_research_board_builder.py tests/py/test_research_board_rule.py` (expect all pass), then commit.

### Task 2: The shared style layer, test first
- [ ] Write `tests/py/test_board_style.py`. It asserts that `board_style.CSS` defines every role token (`--rec-bg --rec-line --why --why-bg --wedge --wedge-bg --trade --trade-bg --nf --nf-bg`) on bare `:root` and again in both dark blocks. It also asserts that `board_style.SCRIPT` contains the legend and the card transform. Run it and see it fail.
- [ ] Create `scripts/board_style.py` from the layers in `docs/artifacts/research/previews/make_previews.py` (A_CSS, A_JS, MARK_JS; the copy is already committed as `docs/artifacts/research/previews/manchester-option-a.html`). Run it to green.

### Task 3: Summaries in the research board, test first
- [ ] Extend `tests/py/test_research_board_builder.py`:
  - a record with `summaries.sections["Status"]` renders the bullets before the original, and the original sits inside `<details class="full">`;
  - a section's copy button still copies the unchanged markdown;
  - the validator refuses a bullet over 25 words, more than 6 bullets, or a bullet with a file path (`/` followed by a word plus an extension) or a backticked field;
  - a missing `summaries` key renders exactly as today.

  Run them and see them fail.
- [ ] Implement it in `scripts/research_board.py`: render `summaries` and validate it. Embed `board_style` in the page. Run the tests to green, then `npm run -s check:workflow`.

### Task 4: The other boards
- [ ] Do the same for `scripts/outline_matrix.py` and `scripts/build_page_board.py`, each with its own test. The answer board (`docs/artifacts/bsuk-answer-board.html`) takes the role colours and the question-card layout. It is republished only on the user's word, because it is the live board they answer on.

### Task 5: Manchester's board, regenerated in place
- [ ] Run `python3 scripts/research_board.py blue-staffy-puppies-manchester-uk`; expect exit 0. Read the whole rendered `.md`, then republish `docs/artifacts/research/blue-staffy-puppies-manchester-uk.html` at its existing URL (https://claude.ai/artifact/WydQDtbxSc4WdJ5mfFEhkN). The record's `approval` is still null, so STOP 1 is unaffected.
- [ ] Commit on `manchester-page`; never push.
