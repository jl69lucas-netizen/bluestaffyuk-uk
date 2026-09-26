# Answer board — answer a question sheet on the board, then send it to Claude Code — design

Status: approved in brainstorm 2026-09-26. Branch `answer-board`, cut from `foundation` at
`e9b3c1b` (worktree `/Users/apple/Downloads/BSUK-answers`). A tool build before project 5: the
user answers Lisa Bright's 21 questions (Known Issue 41) on the published board instead of
copying them out, and the answers reach Claude Code without copy and paste.

## 1. Goal and done

Goal: every question on a question sheet has its own answer field on the published board, and
one button after "What happens next" hands the answers to Claude Code.

Done when:

1. Each of the 21 questions has a "Your answer" field and a status: Answered, Not yet, or
   Leave it off the site.
2. Answers save as they are typed; a refresh or a closed tab loses nothing.
3. A progress count ("13 / 21") and a per-question status dot are always visible.
4. After "What happens next" a **Send to Claude Code** button delivers the answers to a
   watching Claude Code session, with a copy and a download fallback when none is watching.
5. The page is full width, uses layout A (sticky progress rail + wide question column), and
   works at phone width (the rail becomes a top bar) with no horizontal scroll.
6. It is reusable: one builder turns any sheet in the same markdown format into the same board.

Applying the answers to `data/settings.json`, `data/faq.json`, `data/puppies.json` and the
evidence ledger is **project 5 work** (it closes KI 41), not this build.

## 2. Decisions

| # | Decision | Why |
|---|---|---|
| D1 | Option A: an answer board inside the Artifact (runtime `db` + `comments`), not a local form served from the Mac (option B) | Works on any device, keeps the existing link, and Claude reads the answers directly; B needs a running local server and only works on the user's Mac |
| D2 | Layout A: sticky progress rail left, wide question column right; the rail collapses to a top bar under 900px | With 21 questions in 7 sections, knowing which are left and jumping to them matters most; side-by-side (layout B) cramps long answers |
| D3 | The user (artifact owner) answers, relaying Lisa | Owner is an editor, so `sendToClaude` is allowed; no invitations needed |
| D4 | Republish to the existing URL `https://claude.ai/artifact/CvLPpj438KFNfJcFd9gFTH` | The user keeps one link; KI 41 already points at it |
| D5 | Answers stored one document per question; Send writes an immutable snapshot | Last-writer-wins per document means two open tabs cannot overwrite each other's other answers; snapshots keep every send |
| D6 | The Send note is a short summary; the full answers are read from `db` | A comment is capped at 4 KiB; 21 answers can exceed it |
| D7 | `db` rules `read: "admin"`, `write: "admin"` at the root | Answers include licence numbers and business facts; only editors (the owner) read or write them |
| D8 | A declaring page is organization-internal, never public | Accepted by the user; the owner is the only answerer |

## 3. Components

- `scripts/build_answer_board.py` — builder. Args: sheet path, output path, title, eyebrow,
  heading, sheet id (a slug, e.g. `questions-for-lisa`), date, repo-relative sheet path.
  Defaults build the Lisa sheet to `docs/artifacts/bsuk-questions-for-lisa.html`.
- `docs/artifacts/bsuk-questions-for-lisa.html` — regenerated output (replaces the copy-only
  board built earlier; the per-section copy buttons and "copy the whole document" stay).
- `tests/py/test_answer_board.py` — builder tests (section 8).
- `docs/reference/answers/` — where received answers are saved (section 6).
- Docs: `docs/reference/quick-start.md` gets an "Answer boards" entry; the session log gets
  the build record; KI 41's line names the board as the way to answer.

## 4. Parsing

The builder reads the sheet format `tests/py/test_questions_for_lisa.py` already enforces:
a preamble, then `## Section` headings, each holding numbered items
`N. **Question.** context… **Where it goes:** …`. Sections without numbered items (the
summary, "What happens next") render as prose. The builder fails loudly (non-zero exit, a
message naming the line) when numbers are not 1..N in order, a question has no bold text, or
two questions share a number. Each question gets a stable key `qNN` (zero-padded) plus the
sheet id, so a rebuilt board keeps its saved answers as long as numbering is unchanged.

The markdown for each question and section is embedded as data (as the current builder does
with `<script type="text/markdown">`) and rendered with `marked` from cdnjs.

## 5. Page and state

Layout A (approved mockup): masthead; rail with the section list, a status dot per question
(answered = green, leave off = brass, not yet = hollow outline, empty = hollow), the count, a
progress bar, "Saved Ns ago", and a Send button; main column with one card per question:
number, question, context, the "Where it goes" line in small mono, a **Your answer** textarea
(auto-growing), chips *Not yet* and *Leave it off the site*, and a saved tick. Typing text sets
status Answered unless a chip is on; a chip with empty text is a complete answer.

State, per question: `{n, text, status: "answered"|"not_yet"|"leave_off"|"empty", updatedAt}`.

- `db` present: document `sheets/<sheetId>/answers/qNN`; writes debounced 800 ms per question,
  only on change, one write in flight per document. Load reads all answers once, then
  `onSnapshot` on the collection (subscribed once) so a second tab stays current; a field
  that has focus is not overwritten by a snapshot.
- Always: a per-viewer browser draft (`localStorage`, wrapped in try/catch) of the same shape,
  so the page works with `db` null (preview, private window) and a reload without `db` keeps
  typing. When `db` loads and a draft is newer than the stored document, the draft wins and is
  written.
- `db` null: a quiet banner "Saving in this browser only"; Send falls back (section 6).

## 6. Send to Claude Code

The Send card sits after "What happens next": the counts (answered / left off / not yet /
empty), the Send button, and the fallback row.

On click:

1. Flush pending writes.
2. Write the snapshot `sheets/<sheetId>/submissions/s-<ISO time>`:
   `{at, sheetId, counts, answers: [{n, key, question, status, text}]}`.
3. `canSendToClaude()`; if `"available"`, `sendToClaude({anchor: anchorFor(sendCard), text})`
   with text under 1 KiB:
   `Answers submitted — <title> (<sheetId>). Snapshot s-<time>: A answered, L leave off,
   N not yet, E empty. Read db sheets/<sheetId>/submissions/s-<time> and save to
   docs/reference/answers/.`
4. Show "Sent to Claude Code — a reply will appear in the comment thread."

Any other `canSendToClaude` value or a rejection shows the reason in plain words
(`no_session`: "No Claude Code session is watching this board right now"; `writers_only`,
`off`, `claude_unavailable`, `capability_removed`: "Sending to Claude isn't available here")
and leaves the fallbacks: **Copy all answers** (markdown: `## N. Question` + status + text,
via the clipboard) and **Download .md** (`downloads` capability; hidden when `null`). The
snapshot is still written, so Claude can read it later. `rate_limited`: "Wait a moment and try
again." Nothing retries on its own.

Claude's side, on the notification (or when the user says "read my answers"): read the named
snapshot with ArtifactData, write `docs/reference/answers/<sheetId>-<date>.md` (human) and
`.json` (the snapshot as stored), commit on the current branch, reply in the thread with the
counts saved and the commit hash. Each send is its own snapshot; re-sending after edits is how
answers are changed.

Receiving needs a session watching the artifact: the publishing session watches automatically;
a later session starts watching with the ArtifactComments tool. `quick-start.md` says so.

## 7. Declaration

`capabilities: {db: {rules: [{path: "", read: "admin", write: "admin"}]}, comments: {},
downloads: true}`. Every capability is optional at runtime: `claude.use()` returning `null`
hides only its affordance. No capability is used on load except `db` reads.

## 8. Testing

Pytest (`tests/py/test_answer_board.py`), on the built HTML and on fixtures:

- the Lisa sheet builds; the output has 21 answer fields keyed `q01`..`q21` in order, each
  inside its question card;
- the Send card comes after the "What happens next" section in document order;
- section titles and every question's bold text appear in the output;
- a fixture with a gap in numbering, a duplicate number, or no bold text exits non-zero;
- a second fixture sheet (3 questions, 2 sections) builds, proving reuse;
- the page references only allowed script hosts (cdnjs) and Google Fonts;
- `use("db")`, `use("comments")` and `use("downloads")` results are each null-checked;
- the output is deterministic (building twice gives identical bytes).

The existing `test_questions_for_lisa.py` is unchanged and must still pass, and the full
suite plus `check:all` stays green.

Browser checks (Browser pane, local file, capabilities absent): type in three answers, set a
chip, reload — all kept; the count and dots match; phone width (375px) shows the top bar and no
horizontal scroll; dark mode readable. After publishing: one ArtifactData `list` of
`sheets/questions-for-lisa/answers`, and a test snapshot + send round trip reported to the
user (the user presses Send; Claude confirms receipt).

## 9. Out of scope

Emailing Lisa; multi-person answering; editing a sent snapshot (send again instead); writing
answers into the site's data files (project 5, KI 41); a generic form builder beyond this
sheet format.
