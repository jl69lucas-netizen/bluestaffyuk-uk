# Answer board — one standing board for every question Claude has for the user — design

Status: approved in brainstorm 2026-09-26 (revision 2: the user widened the scope from Lisa's
21 questions to every question, now and in future sessions). Branch `answer-board`, cut from
`foundation` at `e9b3c1b` (worktree `/Users/apple/Downloads/BSUK-answers`). A tool build before
project 5.

## 1. Goal and done

Goal: every question Claude has for the user, in any project or session, is posted to one
standing board where the user answers in place and presses **Send to Claude Code**; the
answers reach Claude without copy and paste.

Done when:

1. One published board, **Questions for You**, at a URL that never changes.
2. Claude posts a **batch** of questions (a titled group, e.g. "Project 5 · London board
   picks") without republishing the page; it appears at once, even in an open tab.
3. Each question is either **text** ("Your answer" field) or **choice** (one of A/B/C… chips
   plus an optional note). Every question also has *Not yet* and *Leave it off the site* /
   *Skip* chips.
4. Answers save as they are typed; a refresh or a closed tab loses nothing.
5. Layout A: a sticky rail lists the open batches with progress and each question's status dot;
   the main column shows open batches, newest first; received batches fold into a **Done**
   archive at the bottom. The rail becomes a top bar under 900px; no horizontal scroll.
6. Each batch ends with **Send to Claude Code**: it saves a snapshot of that batch and notifies
   the watching Claude session; with none watching, **Copy answers** and **Download .md** remain.
7. Lisa's 21 questions are the first batch; the old Lisa link points to the board.
8. A written rule makes it the default: questions for the user go to the board.

Writing Lisa's answers into the site's data files is project 5 work (KI 41), not this build.

## 2. Decisions

| # | Decision | Why |
|---|---|---|
| D1 | Option A: a board inside a claude.ai Artifact (runtime `db` + `comments` + `downloads`), not a local form on the Mac | Any device, one link, Claude reads answers directly; a local form needs a running server |
| D2 | Layout A (sticky progress rail + wide question column) | Approved on the mockup; with many questions, seeing what is left matters most |
| D3 | The user (the artifact's owner) answers everything, relaying Lisa where needed | Owner is an editor, so `sendToClaude` works; no invitations |
| D4 | Questions live in the board's `db`, not in the page HTML | Claude posts new batches with ArtifactData writes, no republish; the page renders from `db` |
| D5 | A new Artifact "Questions for You"; the Lisa link (CvLPpj438KFNfJcFd9gFTH) keeps its sheet and gains a line pointing to the board | A general board must not carry Lisa's title; the old link stays valid |
| D6 | Answers are one document per question; Send writes an immutable snapshot | Two tabs cannot overwrite each other's other answers; every send is kept |
| D7 | The Send note is a short summary; the full answers are read from `db` | A comment is capped at 4 KiB |
| D8 | `db` rules: `read: "admin"`, `write: "admin"` at the root | Answers include licence numbers and business facts; only the owner reads or writes |
| D9 | Rule scope (user ruling): two or more questions, or any that needs a written answer, go to the board; a single blocking either/or pick may still be asked in chat | Batches get the board; work does not stall on one quick pick |
| D10 | The rule is an unnumbered CLAUDE.md section, not working rule 18 | Rules 10–17 are page-building rules with ledger rows and 41 agent banners; this rule governs the conversation, not the pages |

## 3. Components

| File | Responsibility |
|---|---|
| `scripts/answer_sheet.py` | `parse_sheet(text)`: the sheet markdown → sections and questions (text or choice). Shared by the two scripts below |
| `scripts/answer_board_batch.py` | CLI: a sheet → a batch JSON file (the payload Claude writes to `db`), kept in `docs/reference/answer-board/batches/` |
| `scripts/build_answer_board.py` | CLI: builds the static board shell `docs/artifacts/bsuk-answer-board.html` (styles, layout, client) |
| `scripts/answer_board_client.js` | Inlined client: reads batches and answers from `db`, renders, autosaves, sends |
| `docs/reference/answer-board/README.md` | How to post a batch, receive answers, mark received |
| `docs/reference/answer-board/batches/`, `…/answers/` | Posted batch files; received answers (`.md` + `.json`) |
| `CLAUDE.md` | New section "Questions for the user — the answer board" |
| `docs/reference/quick-start.md` | "Ask the user questions" / "read my answers" entry |
| `docs/reference/questions-for-lisa.md` + its HTML | One preamble line linking the board; rebuilt with `build_report_artifact.py` as before |
| `docs/reference/session-log.md` | Build record; KI 41 line |

## 4. Sheet format

The format `tests/py/test_questions_for_lisa.py` already enforces, plus choice options:

```
# Batch title

Optional intro paragraphs.

## Section

1. **Question?** Context… **Where it goes:** … (optional)
   - (a) First option
   - (b) Second option
2. **Next question?** Context…
```

A numbered item is a question; wrapped lines are indented under it; indented `- (x) Label`
lines are its options (then it is a choice question, keys are the letters/digits in the
parentheses). A section with no numbered items is prose. Numbers run 1..N across the sheet
with no gaps or repeats; the parser exits non-zero naming the line otherwise. Keys are `qNN`.

## 5. Data model (`db`)

| Path | Written by | Body |
|---|---|---|
| `batches/<batchId>` | Claude (ArtifactData) | `{id, title, project, askedAt, intro, status: "open"\|"received", receivedAt, receivedCommit, sections: [{title, lead}], questions: [{n, key, section, question, context, where, kind: "text"\|"choice", options: [{id, label}]}]}` |
| `batches/<batchId>/answers/<qNN>` | the page | `{n, text, choice, status: "answered"\|"not_yet"\|"skip"\|"empty", updatedAt}` |
| `batches/<batchId>/submissions/<s-time>` | the page, on Send | `{at, id, batchId, counts, answers: [{n, key, question, kind, choice, choiceLabel, status, text}]}` |
| `drafts/additional` | the page | `{text, updatedAt}` — the "Any additional questions" text as typed; `text: ""` after a Send |
| `additional/<s-time>` | the page, on the additional Send | `{at, id, text}` — the text as sent |

`batchId` is a slug with the date, e.g. `2026-09-24-questions-for-lisa-bright`. A choice question is
Answered once an option is picked; the note is optional. A text question is Answered when it
has text. *Not yet* and *Skip* (labelled "Leave it off the site" when the batch's `project` is
`site-content`, else "Skip") are complete answers on their own.

## 6. Page behaviour

- On load the page shows its shell and "Connecting to the board…". `claude.use("db")`:
  - null → "Open this board on claude.ai to see your questions." (plus a `#demo` mode that
    renders an embedded demo batch with browser-only storage, for local checks);
  - present → one `onSnapshot` on `batches`, and one on `batches/<id>/answers` per **open**
    batch (subscribed once per batch, unsubscribed when it is received; well under the 64
    limit). Received batches render read-only from a one-off `get()` of their answers when
    their Done row is opened.
- Answer writes: debounced 800 ms per question, only on change, one write in flight per
  document; a per-browser draft (`localStorage`, try/catch) keeps typing through reloads and
  is written up when it is newer than the stored answer; a focused field is never overwritten
  by a snapshot.
- Rail: open batches (title, "7 / 12"), then each open batch's questions with status dots
  (answered green, skip brass, not yet dashed, empty hollow), a total progress bar, "Saved Ns
  ago", and "N open batches". A new batch arriving while the page is open shows a "New"
  badge until scrolled into view.
- Send (per batch): flush that batch's writes, write the snapshot, and — started inside the
  click, because it needs the viewer's gesture — `canSendToClaude()`; if `"available"`,
  `sendToClaude({anchor: anchorFor(batchSendCard), text})` with a note under 1 KiB:
  `Answers submitted — <title> (<batchId>). Snapshot <s-time>: A answered, K skip, N not yet,
  E empty. Read db batches/<batchId>/submissions/<s-time>.` Other outcomes show plain reasons
  (`no_session`: "No Claude Code session is watching this board right now. Tell Claude Code
  'read my answers', or copy them below."; `rate_limited`: wait and press again) and keep Copy
  and Download (`downloads` capability; hidden when null). Nothing retries by itself.
- Received batches (status `received`, set by Claude) move to Done, showing the commit.
- **Any additional questions** (revision 3, 2026-09-26: the user asked for one free-text field
  for extra questions or sub-tasks). A static section between the open batches and Done — not
  from `db`, no rail entry — shown once the board connects and in `#demo`, hidden in the
  "open this on claude.ai" state. One auto-growing textarea autosaves like an answer (browser
  draft under the reserved key `_additional`, `drafts/additional` with the same 800 ms / only
  on change / one in flight rules; the newer of draft and board wins; a focused field is never
  overwritten). Its own Send (disabled until the trimmed text is non-empty: "Type something
  first") writes `additional/<s-time>` and, inside the click, sends the note `Additional
  questions submitted. Snapshot <s-time> (N characters). Read db additional/<s-time>.`; once
  the snapshot is saved the field, the draft and `drafts/additional` are cleared (a failed save
  clears nothing). Outcome messages match the batch Send; Copy text is the fallback. In
  `#demo` Send is off and Copy works.

## 7. Claude's side (the rule)

CLAUDE.md section "Questions for the user — the answer board":

1. Two or more questions, or any question that needs a written answer, are posted to the
   board as a batch; chat says only "N new questions on the board: <link>". A single blocking
   either/or pick may still be asked in chat. Visual picks keep their browser mockups; the
   batch question links to the mockup.
2. Posting: write the sheet to `docs/reference/answer-board/batches/<batchId>.md`, run
   `python3 scripts/answer_board_batch.py <sheet> --project <p>`, which writes
   `<batchId>.json`; set `batches/<batchId>` from that file with ArtifactData; commit both.
3. At the start of any session that may post or receive, watch the board with the
   ArtifactComments tool so a Send reaches it.
4. Receiving (a Send notification, or the user says "read my answers"): read the named
   snapshot (or, with none, the batch's `answers` collection), write
   `docs/reference/answer-board/answers/<batchId>-<YYYY-MM-DD>.md` and `.json`, commit, update
   `batches/<batchId>` to `status: "received"` with the commit, and reply in the thread with
   the counts and the commit. Then act on the answers.

## 8. Declaration

`capabilities: {db: {rules: [{path: "", read: "admin", write: "admin"}]}, comments: {},
downloads: true}`. Every capability is optional at runtime: `null` hides only its affordance.
No capability call happens on load except `db` reads.

## 9. Testing

Pytest:
- `answer_sheet.parse_sheet`: the Lisa sheet → 21 text questions, 7 sections; a fixture with
  choice options → `kind: "choice"` and the options in order; gap / duplicate / no-bold /
  option-outside-a-question fixtures exit with the line named.
- `answer_board_batch.py`: builds the Lisa batch; the JSON matches §5's batch shape (every
  question has `key`, `kind`, `options` list); output is deterministic; the batch id is
  `<date>-<slug>`; the payload is under 256 KiB.
- `build_answer_board.py`: the shell holds no question text (questions come from `db`), holds
  the Send/Done/rail containers, references only Google Fonts, embeds the demo batch as JSON
  without a closing script tag, and builds byte-identically twice.
- Client guards: `node --check` passes; `use("db")`, `use("comments")`, `use("downloads")` each
  null-checked; the spec's paths appear; the longest note is under 1 KiB.
- `test_questions_for_lisa.py` still passes after the preamble line is added.
- CLAUDE.md contains the section and names `scripts/answer_board_batch.py`; the full suite and
  `check:all` stay green (including `test_rules_index.py`'s reference-doc path guard).

Browser (Browser pane, local file `#demo`): answer a text question, pick a choice option,
mark one Skip, reload — all kept; dots and counts right; 375px top bar, no horizontal scroll;
dark mode readable; no console errors. After publishing: post the Lisa batch with
ArtifactData, `list` `batches` to confirm it, and one real Send round trip with the user.

## 10. Out of scope

Emailing Lisa; answerers other than the owner; editing a sent snapshot (send again instead);
applying answers to the site's data (project 5, KI 41); asking questions in any channel other
than this board and chat.
