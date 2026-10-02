---
name: session-handoff
description: Use when the user wants to continue the BlueStaffyUK project in a new chat — "handoff", "session handoff", "continue in a new chat", "new chat", "start fresh and pick up where we left off" — and needs every file, link and summary the next session must read first. (BlueStaffyUK)
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Overview

A new chat starts with no memory of this one. The handoff is a paste-ready prompt that
carries the repo state, the open flags, the next task and every board link — **all read from
the repo by a script, never written from memory.** `session-closer` ends a session (fills the
brief's What's Next); this skill hands it to the next one.

## Steps

1. **Brief first.** Open the newest `docs/superpowers/sessions/<date>-session-brief.md`. If
   today's brief has an empty `## What's Next` (the script prints "empty — run the
   session-closer skill"), run the `session-closer` skill first, commit, then continue.
2. **Run the script:**
   ```bash
   python3 scripts/session_handoff.py --write
   ```
   It prints the prompt and saves it to `docs/reference/handoff/<YYYY-MM-DD>-<branch>.md`:
   worktree path, branch, short HEAD and clean/dirty; the last ten commits; the newest brief's
   Open Flags and What's Next; the newest plan and its first `### Task` with an unchecked
   step; every `https://claude.ai/artifact/<id>` link in the last five answer-board batches
   and CLAUDE.md; the standing instructions; and the Gemini line.
3. **Publish it** as an Artifact with a copy button per section that downloads as `.md`
   (CLAUDE.md: every deliverable ships as an Artifact with copy buttons, plus `.md`). If a
   handoff Artifact already exists, update it in place by its `url`; keep the HTML source in
   `docs/artifacts/`. Commit the written handoff file.
4. **Paste the prompt in chat** inside one ```` ```text ```` block, so the user can copy it
   straight into the new chat, followed by the Artifact link.

## Never

- **Paste a secret.** The script parses `.env` like a dotenv loader (quotes, multi-line
  values, ` #` comments, `export`) and redacts every value of a secret-looking key at any
  length, every other value of six or more characters, and anything shaped like a key
  (`AQ.…`, `AIza…`, `sk-…`, `ghp_…`, `github_pat_…`, `xox[bpa]-…`, `AKIA…`). Never print `.env`, never add a value by hand, and never edit
  the redaction out. The Gemini line says only whether GEMINI_API_KEY is set.
- **Claim state the script did not read.** If a line says `NOT FETCHED` or "none", the
  handoff says so. Do not add progress, test results or decisions from memory; if something
  is missing, put it in the brief or plan first and re-run the script.
- **Push.** The handoff is committed, never pushed (CLAUDE.md rule 3).

## See also

- `session-closer` — fills What's Next before the handoff
- `grill-me` — the next session's opener (`--resume` continues an unfinished interview)
