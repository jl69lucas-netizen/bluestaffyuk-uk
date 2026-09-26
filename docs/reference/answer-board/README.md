# The answer board

One standing claude.ai board, **Questions for You**, holds every batch of questions Claude has
for the user (spec `docs/superpowers/specs/2026-09-26-answer-board-design.md`). Board URL:
recorded here by the Task 7 publish.

## Post a batch

1. Write the questions as a sheet (`# Title`, `## Section`, `N. **Question?** context…`,
   optional `**Where it goes:** …`, optional indented `- (a) Option` lines for a choice) at
   `docs/reference/answer-board/batches/<YYYY-MM-DD>-<slug>.md`. The title is capped at 120
   characters (the batch maker refuses a longer one), and option ids are 1–3 letters or digits.
2. `python3 scripts/answer_board_batch.py <sheet> --project <site-content|project-5|tools|…>`
   writes `<batchId>.json` beside it and prints the batch id.
3. ArtifactData `set`, collection `batches`, doc_id `<batchId>`, `file_path` = that JSON, on the
   board URL. The batch appears on the board at once.
4. Commit the sheet and the JSON. In chat, say only: "N new questions on the board: <URL>".

To correct a posted batch, `update` it; never re-`set` a received batch (that resets it to open).

## Receive answers

A session receives a Send only while it watches the board: at the start of any session that
may post or receive, run ArtifactComments `watch` on the board URL. Only a main-loop session
holds a watch; a subagent cannot.

Then confirm it: a bare ArtifactComments `watch` (no URL) lists the watches, and the board's
row must say auto-replies armed. If it does not, ask the user to paste the board link in chat
and run `watch` again: a watch arms auto-replies only for a board this session published or
whose link the user gave in their own message. Without an armed watch, the user's fallback is
to tell Claude Code "read my answers".

On a Send notification (or when the user says "read my answers"):

1. ArtifactData `get` the snapshot the note names: collection
   `batches/<batchId>/submissions`, doc_id `s-…`. With no snapshot, `list`
   `batches/<batchId>/answers`.
2. Save it as `docs/reference/answer-board/answers/<batchId>-<YYYY-MM-DD>.json` (as stored) and
   `.md` (question, status, picked option, text), and commit.
3. ArtifactData `update` `batches/<batchId>`: `status: "received"`, `receivedAt` (ISO time),
   `receivedCommit` (the short hash), passing `if_version` from the last read of that batch so
   a change made since is not overwritten. The board moves the batch to Done.
4. ArtifactComments `reply` in the Send's thread with the counts and the commit, then act on
   the answers.

Answers are records of what the user said. Writing them into the site's data files is the
work that asked the questions (for the questions for Lisa: project 5, Known Issue 41).
