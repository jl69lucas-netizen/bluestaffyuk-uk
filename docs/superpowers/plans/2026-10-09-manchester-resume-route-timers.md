# Manchester Resume, Route Timers and the Faster Lane: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the cloud session's work (PR #2) locally, give the Route Map a start/finish timer for every page-run row and every agent, apply the breeder's eight open answers, and take Manchester from row 14 (Harden: impeccable) to row 21 (close) through one harden round instead of London's five or six.

**Architecture:** The timers follow the Route Map's own rule: nothing is guessed, everything is proved from disk. A row's start and finish come from the commit subjects the page run already writes (`(row N)`, `(rows A-B)`, `STOP k posted|approved`), scoped to commits since the page's session-open commit. `scripts/pipeline_status.py` adds them to its JSON; the `bsuk-route` mod only draws them. Agent timers reuse the `startedAt`/`endedAt` fields the `bsuk-agents` mod already keeps.

**Tech Stack:** Python 3 (scripts, pytest), TypeScript/TSX (Claude Code mods), Astro (the page), the answer board (ArtifactData).

**Branch:** `manchester-page` (working rule 2). Commit after every task, with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (working rule 3). Pushing, and merging PR #2 on GitHub, wait for the breeder's yes in chat.

---

## Where things stand (verified 2026-10-09, 22:00 BST)

| Item | State | Proof |
|---|---|---|
| Rows 1–13 (research → render gates) | done | `python3 scripts/pipeline_status.py blue-staffy-puppies-manchester-uk` |
| STOPs 1–4 | all approved | same, `stops_done: 4` |
| Row 14, Harden: impeccable | **now** | no `impeccable` key in `data/page-runs/blue-staffy-puppies-manchester-uk.json` |
| PR #2 (`manchester-page-gfr12s` → `manchester-page`) | open, 14 commits, fast-forward | `git merge-base --is-ancestor` |
| PR #2 on this Mac | `npm run -s build` exit 0; `npm run check:all` exit 0, `check:parity` included (the cloud could not run it) | `scratchpad/pr2-summary.log` |
| Answer board | watched, auto-replies armed; 2 batches open, 8 questions, 0 answered | ArtifactData `batches` query |
| Agents registry | 47 agents, 0 problems | `python3 scripts/build_agent_registry.py --check` |

## Why it took two weeks, and what to change (the speed decision)

Measured from git, not guessed:

- **London** ran from 2026-09-27 to 2026-10-06: ten calendar days and 221 London commits. The harden-to-close stretch (rows 13–21) alone ran four days (10-03 → 10-06, about 160 commits), through six proposal rounds (Harden Decisions, Harden Proposals, Close Proposals, Final Fixes, Certificates and Tweaks, Map Preview). The same ten days also built the system itself: board v2 and v3, the answer board, the mods, the FAQ fact fixes. 522 commits in all.
- **Manchester** ran rows 1–13 in about **25 hours** (10-07 00:07 → 10-08 01:00). The four STOPs held the breeder for about **4 h 15 m** in all (STOP 1 78 m, STOP 2 17 m, STOP 3 36 m, STOP 4 1 h 44 m with its redo). So the STOPs are not the slow part.
- Of Manchester's 118 commits, **39 (one in three) were system work**, not page work: route mod, board readability, FAQ near-copy check, two `test:py` fixes, the outline data-value fix, image sizes, and 14 CTA-system commits.

The slow parts are therefore **(1) system work done in the middle of a page run** and **(2) a harden/close stage that loops through many proposal rounds**.

**Option A — Two lanes and one harden round (Recommended).** Keep all 21 rows, all four STOPs and every gate. Change three things:
1. *Page lane / system lane.* During a page run, an improvement to a gate, skill, rule or tool goes on the system-lane list (a `spawn_task` chip or a Known Issue). It is done between pages, unless it blocks a gate on the page in hand.
2. *One harden round.* The impeccable, frontend-design and static-scan findings (rows 14–16) land in one preview Artifact and one answer-board batch, not one round each.
3. *Timers on the Route Map* (Phase B), so every row's time is measured and the next decision rests on numbers. Target: one city in two working days.

Why: it attacks the two measured causes without removing a gate or a STOP. Trade-off: a harness fix found mid-page waits for the next gap between pages, so a known non-blocking defect can ship on one page and be swept up afterwards.

**Option B — Waves of three cities.** Subagents run rows 1–11 for three cities in parallel worktrees. Each STOP becomes one combined board sitting covering all three. The three builds are merged one after another.

Why not now: the harness still changes on every page (39 system commits on Manchester), so a defect would land on three pages at once. Three branches would also conflict on the shared generated files (`data/facts/rebuilt.json`, page dates, `data/image-manifest.json`, `public/_redirects`). Working rule 16 (no shared hero or counter) would have to be checked across three unbuilt pages at once. Trade-off of waiting: the first few cities go at single-city speed.

**Verdict:** keep the current system and refine it with Option A now. Move to Option B once two cities in a row close with zero system-lane commits during their runs. The Phase B timeline counts those commits for us.

---

## File structure

| File | Change | Responsibility |
|---|---|---|
| `scripts/pipeline_status.py` | modify | add `timeline()` (pure), `_page_log()`, row `start`/`finish`/`inferred`, `clock`, `--timeline` |
| `tests/py/test_pipeline_status.py` | modify | timeline tests |
| `tools/claude-mods/bsuk-route/types/index.d.ts` | modify | `Row.start/finish/inferred`, `Route.clock` |
| `tools/claude-mods/bsuk-route/hooks/register.tsx` | modify | draw start → finish and a live timer on the row in progress; page clock in the header card |
| `tools/claude-mods/bsuk-agents/hooks/register.tsx` | modify | each agent card shows its start → finish clock time |
| `tools/claude-mods/README.md` | modify | one line on the timers |
| `docs/artifacts/claude-mods-preview.html` | modify | the timer drawn in the pane mock (working rule 10) |
| `docs/reference/WORKFLOW.md`, `docs/reference/page-run.md` | modify (Phase F, if Option A is picked) | page lane / system lane; one harden round |
| `src/lib/manchesterFaq.ts`, `src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro` | modify (Phase C) | the breeder's answers |

---

## Phase A — Land the cloud work

### Task 1: Record the local verification of PR #2

**Files:** Modify `docs/superpowers/sessions/2026-10-07-session-brief.md` (append a dated section).

- [ ] **Step 1: Read the four exit codes**

Run: `cat /private/tmp/claude-501/-Users-apple-Downloads-BSUK/fd81dd2f-f98e-434b-ad20-649a73a1b506/scratchpad/pr2-summary.log`
Expected: `build exit 0`, `check:all exit 0`, then `test:py exit N` and `meta exit N`.

- [ ] **Step 2: Classify any failure before touching code** (`rules/gates.md`, `bsuk-gate-integrity`)

For each failing test in `pr2-testpy.log` / `pr2-meta.log`, reproduce it once on its own in the worktree:
`cd .claude/worktrees/pr2-verify && python3 -m pytest <nodeid> -x -q`.
The PR names `test_page_board::test_refusal_list_renders_in_a_browser…` as a known timing flake, so re-run it three times before calling it a defect. A failure that reproduces and comes from the PR is fixed on `manchester-page` after Task 2 (TDD: the failing test already exists). A failure that also fails on `manchester-page` without the PR is recorded as pre-existing.

- [ ] **Step 3: Append the result to the brief**

```markdown
## 2026-10-09 — resumed locally from the cloud
- PR #2 (manchester-page-gfr12s, 14 commits) verified on the Mac: build 0, check:all 0 (parity included), test:py <N>, meta <N>.
- Open on the answer board: Manchester open items (6), served alts (2). None answered yet.
- Route: rows 1–13 done, row 14 (impeccable) now.
```

### Task 2: Fast-forward `manchester-page` to the PR head

- [ ] **Step 1: Put the PR's 14 commits under this session's commits**

This session's plan commit (`ac6d0de8`) already sits on `manchester-page`, so a plain fast-forward is no longer possible. Replay it on top of the PR head instead (it touches only new files, so there is nothing to conflict):

```bash
git -C /Users/apple/Downloads/BSUK rebase origin/manchester-page-gfr12s
```
Expected: `Successfully rebased`, `git log --oneline -3` shows this session's commits above `a0448ea4`.

- [ ] **Step 2: Remove the verification worktree**

```bash
git -C /Users/apple/Downloads/BSUK worktree remove --force .claude/worktrees/pr2-verify
```

- [ ] **Step 3: Confirm the route now sees the open batch**

Run: `python3 scripts/pipeline_status.py blue-staffy-puppies-manchester-uk | grep -A2 needs_you`
Expected: `"answer board: 2026-10-08-manchester-page-five-open-items-before-the-final-polish"`.

- [ ] **Step 4: Commit Task 1's brief update and this plan**

```bash
git add docs/superpowers/sessions/2026-10-07-session-brief.md docs/superpowers/plans/2026-10-09-manchester-resume-route-timers.md
git commit -m "docs(manchester): resumed locally — PR #2 verified on the Mac, plan for timers and rows 14–21"
```

- [ ] **Step 5: Ask before anything leaves the Mac.** Merging PR #2 on GitHub and pushing `manchester-page` are outward-facing: ask in chat and wait for the breeder's yes.

---

## Phase B — Route Map timers

### Task 3: `timeline()`, the pure function

**Files:** Modify `scripts/pipeline_status.py`; Test `tests/py/test_pipeline_status.py`.

- [ ] **Step 1: Write the failing tests** (append to `tests/py/test_pipeline_status.py`)

```python
def _rows(states):
    return [{"row": n, "stop": PS.STOPS.get(n), "state": s} for n, s in states]


def test_timeline_reads_row_tags_and_ranges():
    log = [(100, "chore(x): session open recorded (row 1)"),
           (200, "docs(x): intake, URL kept, research inventory (rows 2-4)"),
           (260, "fix(x): something else (row 3)")]
    t = PS.timeline(log, _rows([(1, "done"), (2, "done"), (3, "done"), (4, "now")]), now=900)
    assert (t[1]["start"], t[1]["finish"]) == (100, 100)
    assert (t[3]["start"], t[3]["finish"]) == (200, 260)
    assert t[4]["start"] == 200 and t[4]["finish"] is None


def test_a_stop_runs_from_posted_to_approved_and_counts_as_breeder_time():
    log = [(100, "research(x): the research board (row 8, STOP 1 pending)"),
           (180, "research(x): STOP 1 approved — picks saved"),
           (400, "docs(x): Task 41 — no board_revisions row for STOP 1 q12")]
    rows = _rows([(8, "done"), (9, "now")])
    t = PS.timeline(log, rows, now=900)
    assert (t[8]["start"], t[8]["finish"]) == (100, 180)   # a later mention never moves an approval
    assert PS.breeder_wait(t, rows) == 80


def test_a_revert_commit_is_ignored():
    log = [(100, "x(y): STOP 4 posted"), (150, "x(y): STOP 4 approved"),
           (160, 'Revert "x(y): STOP 4 approved"'), (300, "x(y): STOP 4 approved on the board")]
    t = PS.timeline(log, _rows([(11, "done")]), now=900)
    assert t[11]["finish"] == 300


def test_an_untagged_done_row_borrows_its_neighbours_and_says_so():
    log = [(100, "a (row 5)"), (300, "b (row 7)")]
    t = PS.timeline(log, _rows([(5, "done"), (6, "done"), (7, "done")]), now=900)
    assert t[6] == {"start": 100, "finish": 300, "inferred": True}
    assert t[5]["inferred"] is False


def test_todo_rows_have_no_clock():
    t = PS.timeline([(100, "a (row 12)")], _rows([(12, "now"), (13, "todo")]), now=900)
    assert t[13] == {"start": None, "finish": None, "inferred": False}
```

- [ ] **Step 2: Run them and watch them fail**

Run: `python3 -m pytest tests/py/test_pipeline_status.py -k "timeline or breeder or revert or untagged or todo_rows" -q`
Expected: FAIL with `AttributeError: module 'pipeline_status' has no attribute 'timeline'`.

- [ ] **Step 3: Implement** (in `scripts/pipeline_status.py`, after `STOPS`/`BOARDS`)

```python
#: A row tag in a commit subject: "(row 12)", "(rows 2-4)", "row 13". A range covers every row in it.
ROW_TAG = re.compile(r"\brows?\s+(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?\b", re.I)
#: "STOP 3 approved" finishes the stop's row; any other "STOP 3" (posted, pending, a batch) starts it.
STOP_TAG = re.compile(r"\bSTOP\s+([1-4])\b", re.I)
STOP_ROW = {k: r for r, k in STOPS.items()}


def timeline(log, rows, now):
    """{row: {start, finish, inferred}} in epoch seconds, from (ts, subject) commits, oldest first.

    A row starts at its first tagged commit and finishes at its last; a STOP row finishes at its
    approval, never later. A done row with no tag borrows the previous row's finish as its start
    and the next clocked row's start as its finish, marked inferred. A todo row has no clock.
    `now` is unused today and kept so a caller can pass the clock it drew with."""
    first, last, approved = {}, {}, {}
    for ts, subj in log:
        if subj.startswith("Revert "):
            continue
        hit = set()
        for a, b in ROW_TAG.findall(subj):
            lo, hi = int(a), int(b or a)
            if 1 <= lo <= hi <= len(ROWS):
                hit.update(range(lo, hi + 1))
        for k in STOP_TAG.findall(subj):
            r = STOP_ROW[int(k)]
            hit.add(r)
            if re.search(rf"\bSTOP\s+{k}\s+approved\b", subj, re.I):
                approved[r] = ts
        for r in hit:
            first[r] = min(first.get(r, ts), ts)
            last[r] = max(last.get(r, ts), ts)
    out, prev_finish = {}, None
    order = [r["row"] for r in rows]
    for i, r in enumerate(rows):
        n = r["row"]
        if r["state"] == "todo":
            out[n] = {"start": None, "finish": None, "inferred": False}
            continue
        start = first.get(n)
        finish = approved.get(n, last.get(n)) if r["state"] == "done" else None
        inferred = False
        if start is None:
            start, inferred = prev_finish, True
        if r["state"] == "done" and n not in first:
            nxt = next((first[m] for m in order[i + 1:] if m in first), None)
            finish, inferred = nxt if nxt is not None else start, True
        out[n] = {"start": start, "finish": finish, "inferred": inferred}
        prev_finish = finish if finish is not None else prev_finish
    return out


def breeder_wait(times, rows):
    """Seconds the four STOPs spent with the breeder: posted → approved, summed."""
    return sum((times[r["row"]]["finish"] or 0) - (times[r["row"]]["start"] or 0)
               for r in rows if r.get("stop") and r["state"] == "done"
               and times.get(r["row"], {}).get("finish") and times[r["row"]].get("start"))
```

- [ ] **Step 4: Run the tests and watch them pass**

Run: `python3 -m pytest tests/py/test_pipeline_status.py -q`
Expected: every test PASS (the 13 existing tests and the 5 new ones).

- [ ] **Step 5: Commit**

```bash
git add scripts/pipeline_status.py tests/py/test_pipeline_status.py
git commit -m "feat(route): each page-run row's start and finish, read from the row tags in its commits"
```

### Task 4: Wire the timeline into `status()` and add `--timeline`

**Files:** Modify `scripts/pipeline_status.py` (`status`, `main`, new `_page_log`); Test `tests/py/test_pipeline_status.py`.

- [ ] **Step 1: Write the failing tests**

```python
def test_status_carries_each_rows_clock_from_the_page_log(tmp_path, monkeypatch):
    _tree(tmp_path, 1)
    monkeypatch.setattr(PS, "_page_log", lambda slug, root: [(10, "x (row 1)"), (50, "x (row 8, STOP 1 pending)"),
                                                            (90, "x: STOP 1 approved")])
    s = PS.status(SLUG, tmp_path)
    assert s["rows"][7]["start"] == 50 and s["rows"][7]["finish"] == 90
    assert s["clock"] == {"opened": 10, "breeder_wait": 40}


def test_a_page_with_no_log_still_draws(tmp_path, monkeypatch):
    _tree(tmp_path, 0)
    monkeypatch.setattr(PS, "_page_log", lambda slug, root: [])
    s = PS.status(SLUG, tmp_path)
    assert s["clock"] == {"opened": None, "breeder_wait": 0}
    assert all("start" in r for r in s["rows"])
```

- [ ] **Step 2: Run them and watch them fail**

Run: `python3 -m pytest tests/py/test_pipeline_status.py -k "clock or no_log" -q`
Expected: FAIL with `AttributeError: ... '_page_log'`.

- [ ] **Step 3: Implement**

Add above `status()`:

```python
def _page_log(slug, root=ROOT):
    """(ts, subject) for every commit on this branch since the page's session-open commit, oldest first."""
    added = _git(root, "log", "--diff-filter=A", "--format=%ct", "--", f"data/page-runs/{slug}.json").splitlines()
    if not added:
        return []
    since = added[-1]
    out = []
    for line in _git(root, "log", "--reverse", f"--since=@{since}", "--format=%ct%x09%s").splitlines():
        ts, _, subj = line.partition("\t")
        if ts.isdigit():
            out.append((int(ts), subj))
    return out
```

In `status()`, after the `rows` list is built and before `stops_done`:

```python
    log = _page_log(slug, root)
    times = timeline(log, rows, now=None)
    for r in rows:
        r.update(times[r["row"]])
```

and add to the returned dict:

```python
        "clock": {"opened": log[0][0] if log else None, "breeder_wait": breeder_wait(times, rows)},
```

Replace `main()`:

```python
def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    slug = args[0] if args else newest_board()
    if not slug:
        print(json.dumps({"error": "no page board on disk"}))
        return 2
    s = status(slug)
    if "--timeline" in argv:
        import datetime as dt
        fmt = lambda t: dt.datetime.fromtimestamp(t).strftime("%m-%d %H:%M") if t else "     -     "
        for r in s["rows"]:
            took = (r["finish"] - r["start"]) // 60 if r["start"] and r["finish"] else None
            print(f"{r['row']:>2} {r['name'][:26]:<26} {fmt(r['start'])} → {fmt(r['finish'])}"
                  f" {'' if took is None else f'{took // 60}h{took % 60:02d}m'}{' ~' if r['inferred'] else ''}")
        print(f"with the breeder: {s['clock']['breeder_wait'] // 60} min")
        return 0
    print(json.dumps(s, indent=1))
    return 0
```

- [ ] **Step 4: Run the whole file, then the real page**

Run: `python3 -m pytest tests/py/test_pipeline_status.py -q`
Expected: all PASS.
Run: `python3 scripts/pipeline_status.py blue-staffy-puppies-manchester-uk --timeline`
Expected: rows 1–13 carry dates on 10-07/10-08, row 8 runs from about 01:21 to 02:39, row 14 shows a start and no finish, and `with the breeder:` reads about 255 min. Check three rows by hand against `git log --format='%ad %s' --date=format:'%m-%d %H:%M'` before trusting it.

- [ ] **Step 5: Commit**

```bash
git add scripts/pipeline_status.py tests/py/test_pipeline_status.py
git commit -m "feat(route): the route JSON carries every row's clock and the page's breeder time; --timeline prints them"
```

### Task 5: Draw the timers in the Route Map mod

**Files:** Modify `tools/claude-mods/bsuk-route/types/index.d.ts`, `tools/claude-mods/bsuk-route/hooks/register.tsx`.

- [ ] **Step 1: Types**

In `index.d.ts`, replace the `Row` line and add `clock` to `Route`:

```ts
export type Row = { row: number; name: string; phase: string; state: 'done' | 'now' | 'todo'; stop: number | null; evidence: string; tools?: Tools; start?: number | null; finish?: number | null; inferred?: boolean }
```
```ts
  clock?: { opened: number | null; breeder_wait: number }
```

- [ ] **Step 2: Formatters** (in `register.tsx`, under `took`)

```ts
// A commit time (epoch seconds) as the breeder reads it: "22:10" today, "07 Oct 22:10" before.
const at = (ts: number | null | undefined, now: number) => {
  if (!ts) return ''
  const d = new Date(ts * 1000)
  const hm = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
  return d.toDateString() === new Date(now).toDateString()
    ? hm : `${d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })} ${hm}`
}
const span = (r: any, now: number) =>
  r.state === 'done' && r.start && r.finish
    ? `${at(r.start, now)} → ${at(r.finish, now)} · ${took((r.finish - r.start) * 1000)}${r.inferred ? ' ~' : ''}`
    : r.state === 'now' && r.start
      ? `since ${at(r.start, now)} · ${took(now - r.start * 1000)}`
      : ''
```

- [ ] **Step 3: Draw them.** In the row renderer, directly under the row's name/status `<Box>`, add:

```tsx
                  {span(r, now) ? <Text color={now ? BRASS : INK_3}>     ⏱ {span(r, now)}</Text> : null}
```

The `now` boolean already in scope there shadows the clock. Rename that boolean to `isNow` in that block first (three uses: `backgroundColor`, `bold`, the evidence line), then pass the clock `now` to `span`.

In the header card, under the progress bar, add:

```tsx
          {rt.clock?.opened ? (
            <Text color={INK_2}>
              ⏱ page clock {took(now - rt.clock.opened * 1000)}  ·  with you {took(rt.clock.breeder_wait * 1000)}
            </Text>
          ) : null}
```

In the LIVE card, give each working agent its start time: change `{took(now - c.startedAt)}` to `{at(c.startedAt / 1000, now)} · {took(now - c.startedAt)}`.

- [ ] **Step 4: Validate and look at it**

Run: `claude plugin validate tools/claude-mods/bsuk-route`
Expected: valid.
Then start a session with `claude --plugin-dir tools/claude-mods/bsuk-route --plugin-dir tools/claude-mods/bsuk-agents --plugin-dir tools/claude-mods/bsuk-gauges`, run `/bsuk-route`, and check: done rows read `07 Oct 01:21 → 07 Oct 02:39 · 1h 18m`, row 14 reads `since … · Nm` and ticks every 15 s, and the header shows the page clock.

- [ ] **Step 5: Commit**

```bash
git add tools/claude-mods/bsuk-route
git commit -m "tools(route): every row shows when it started and finished; the row in progress runs a live timer; page clock and breeder time in the header"
```

### Task 6: Start → finish on every agent card

**Files:** Modify `tools/claude-mods/bsuk-agents/hooks/register.tsx`.

- [ ] **Step 1: Add the clock formatter** under the existing `since` helper:

```ts
const hm = (ms: number) => new Date(ms).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
```

- [ ] **Step 2: Show it.** In `card()`, replace the line under the title row:

```tsx
          <Text color={INK_3}>
            {[c.type, c.model].filter(Boolean).join(' · ')}{c.type || c.model ? ' · ' : ''}{c.calls} tool calls
          </Text>
```
with
```tsx
          <Text color={INK_3}>
            {[c.type, c.model].filter(Boolean).join(' · ')}{c.type || c.model ? ' · ' : ''}{c.calls} tool calls
            {'  ·  '}⏱ {hm(c.startedAt)} → {c.endedAt ? hm(c.endedAt) : 'running'}
          </Text>
```

- [ ] **Step 3: Validate**

Run: `claude plugin validate tools/claude-mods/bsuk-agents`
Expected: valid. Launch one background agent and check that its card reads `⏱ 22:14 → running`, then `⏱ 22:14 → 22:19` once it finishes.

- [ ] **Step 4: Commit**

```bash
git add tools/claude-mods/bsuk-agents
git commit -m "tools(agents): each agent card shows its start and finish clock time"
```

### Task 7: README and the visual companion

**Files:** Modify `tools/claude-mods/README.md`, `docs/artifacts/claude-mods-preview.html`.

- [ ] **Step 1:** In the README's `bsuk-route` row, append: `Each row shows when it started and finished (read from the row tags in the page's commits; ~ marks a row with no tag of its own), the row in progress runs a live timer, and the header shows the page clock and the time the four STOPs spent with the breeder.` In the `bsuk-agents` row, append: `Each card shows its start → finish clock time.`
- [ ] **Step 2:** In the "Already built" section of `claude-mods-preview.html`, add a pane-mock card with three rows (`● 08 Research board 07 Oct 01:21 → 02:39 · 1h 18m`, `◉ 14 Harden: impeccable since 22:10 · 47m`, `○ 15 Harden: frontend-design`) in the existing dark card styles. Republish it to its existing URL (https://claude.ai/artifact/QANFSikGiqZDcWffmE1kzR; read it first) and open it for the breeder (working rule 10).
- [ ] **Step 3: Commit**

```bash
git add tools/claude-mods/README.md docs/artifacts/claude-mods-preview.html
git commit -m "docs(mods): the route and agent timers in the README and the pane mock"
```

---

## Phase C — The breeder's eight answers

### Task 8: Receive and save

- [ ] **Step 1:** On a Send (or "read my answers"), follow `docs/reference/answer-board/README.md` *Receive answers* steps 1–5 for each batch: `get` the submission, save it as `docs/reference/answer-board/answers/<batchId>-2026-10-09.json` and `.md`, run `python3 scripts/answer_board_save.py --neutralise <json> <md>`, commit, `update` the batch to `received` with `if_version`, then reply in the Send's thread.

### Task 9: Apply the Manchester picks

**Files:** `src/lib/manchesterFaq.ts`, `src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro`, and the files named under each answer.

- [ ] **q01 (health-testing FAQ).** On (a), in `src/lib/manchesterFaq.ts:101` replace
  `are both Kennel Club registered and fully vaccinated, and both have had DNA tests for ${TEST_A} and ${TEST_B} and eye and elbow screening.`
  with
  `are both fully vaccinated, and both have had DNA tests for ${TEST_A} and ${TEST_B} and eye and elbow screening, with the certificates shared on request.`
  On (c), use the breeder's own words, keeping `${TEST_A}`/`${TEST_B}`. On (b), change nothing.
- [ ] **q02 (doubled "change your mind").** Run `grep -n "change your mind" dist/uk-locations/blue-staffy-puppies-manchester-uk/index.html` to find the two occurrences. On (a), make the sentence at `src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro:209` render the board's wording through `refundClause()` (from `src/lib/cityKit.ts`), never typed. Keep the figures read from `data/settings.json`. Rebuild and grep again: exactly one "change your mind".
- [ ] **q03 (seam bar).** (a): no change. (b): remove the bar and, in the same commit, give the hero/counter separation another visible line. That rule is gated (`rules/design.md` hero/counter separation), so show the replacement in a browser preview first (working rule 6).
- [ ] **q04 (phone headings).** (a): no change. (b) or (c): find the commit that set it with `git log -S "clamp(" --oneline -- src/styles | head`, revert that value (for (c), scope it back to the Manchester page's own class). For (b), also shorten Manchester's longest H2, keeping its target keyword (working rule 15).
- [ ] **q05 (middle FAQ photo).** (a): no change. (b): set the middle FAQ slot to Maggie's served file and caption from the approved board record. Then run `python3 -m pytest tests/py/test_served_alt_preserved.py -q`: a repeated photo needs a new alt (working rule 11).
- [ ] **q06 (AI preparation photo).** (a): no change. (b): swap in the named photo (or pick from `public/images/`, then the breeder's `Assets/Images/`), keeping its served alt.
- [ ] **Then:** `npm run -s build && npm run check:all && python3 -m pytest tests/py -q -k manchester`, then commit: `fix(manchester): the breeder's answers to the five open items (q01–q06)`.

### Task 10: Served alts

- [ ] Check out `served-alt-corrections` (10aa9cb6) and apply the q01/q02 picks with the proposal script already on that branch. Re-approve the touched boards with `python3 scripts/board_approve.py <slug>` (the board's own save is the approval, never the answer board's), run `npm run check:all`, commit, and leave the branch unmerged until the breeder says merge.

---

## Phase D — CTAs on the Manchester board (only if the breeder says yes)

PR #2 exempts London and Manchester, because their boards were approved before the CTA rule. The cloud's own eval found Manchester's three gold pills nearly identical (`cta-style-distinct`, advisory today).

### Task 11: Add block 7e to Manchester's board

- [ ] **Step 1:** `python3 scripts/cta_rules.py --propose blue-staffy-puppies-manchester-uk` (prints the proposed slots, three options each). Then `--write` to put them on the record.
- [ ] **Step 2:** `python3 scripts/build_page_board.py blue-staffy-puppies-manchester-uk` and republish the board to its existing URL (https://claude.ai/artifact/4NhTX3rzQXZVXLn4smTop8). Post a one-question batch ("Pick a button for each slot on block 7e").
- [ ] **Step 3:** After the breeder's picks are saved on the board, run `python3 scripts/board_approve.py blue-staffy-puppies-manchester-uk`. It refuses an unpicked slot, twin texts or a repeated style. Then replace each `.mx-cta` link in the page with `CtaButton` fed by `src/lib/ctas.ts`, rebuild, and run `npm run test:render:pages -- --grep manchester`. Expected: `cta-style-distinct` silent.
- [ ] **Step 4:** Commit: `feat(manchester): the CTAs the breeder picked on board block 7e`.

---

## Phase E — Manchester rows 14–21 in one harden round

### Task 12: Rows 14–16 together

- [ ] **Step 1:** The controller (main loop, not a subagent) invokes the Skill tool `impeccable:impeccable` on the built page at 375 / 768 / 1280 in the browser pane (`npm run preview`, then open `/uk-locations/blue-staffy-puppies-manchester-uk/`). Write each finding down; edit nothing yet.
- [ ] **Step 2:** Same for `frontend-design:frontend-design`.
- [ ] **Step 3:** Run `python3 scripts/page_hardening_scan.py --json` and the `bsuk-visual-intelligence` skill (page-run row 16).
- [ ] **Step 4:** Put all three lists in ONE preview Artifact `docs/artifacts/bsuk-manchester-harden.html`. Each finding gets a before/after screenshot, one **(Recommended)** fix with its why and trade-off, and copy buttons. Post ONE batch. This is the Option A change; on London these were five or six rounds.
- [ ] **Step 5:** Apply the approved fixes (visual layer only, working rule 6), rebuild, and record `impeccable` and `frontend_design` in `data/page-runs/blue-staffy-puppies-manchester-uk.json` in the shape London's record uses (`ran_on`, `widths`, `findings`, `fixed`, `deferred`, `commit`). Commit per fix group.

### Task 13: Rows 17–18

- [ ] `npm run gate:page -- blue-staffy-puppies-manchester-uk`. Expected: every step twice, runs identical, verdict PASS. Read each gate's examined count before believing it.
- [ ] Invoke `superpowers:verification-before-completion`, then write the `verification_before_completion` key in the page-run record (shape: London's). Commit.

### Task 14: Rows 19–21

- [ ] Row 19: write the measurement-ledger row in `docs/reports/p5-ledger.json`. Row 20: `python3 scripts/aeo_audit.py --all --json` clean for the page, using the `bsuk-aeo-pass` skill.
- [ ] Row 21: run the `bsuk-learning-loop` skill and add a lessons entry to `docs/reference/lessons.md`. Then publish the gate report Artifact and ask the breeder for final approval. Only after their yes: save `final-approval-blue-staffy-puppies-manchester-uk-<date>.md`, turn noindex off, run `npm run sitemaps`, run `check:all`, commit.
- [ ] Check `python3 scripts/pipeline_status.py blue-staffy-puppies-manchester-uk --timeline`: every row has a finish. Copy the table into the lessons entry. That table is the first measured city.

---

## Phase F — Make Option A standing (only if the breeder picks it)

### Task 15: Write the two-lane rule where the run reads it

**Files:** Modify `docs/reference/WORKFLOW.md`, `docs/reference/page-run.md`.

- [ ] In `WORKFLOW.md`, add a section `## Page lane and system lane` with three rules. (1) During a page run, a change to a gate, skill, rule, mod or script that does not block a gate on the page in hand goes on the system-lane list (`mcp__ccd_session__spawn_task` chip, or a Known Issue in `docs/reference/session-log.md`). (2) The system lane is worked between pages. (3) A blocking defect is fixed in the page lane, with a failing test first (`rules/gates.md`).
- [ ] In `page-run.md` rows 14–16, add: "One harden round: the findings of rows 14, 15 and 16 go to the breeder in one preview Artifact and one batch."
- [ ] Run `npm run check:workflow` and `python3 -m pytest tests/py/test_doc_drift.py -q`, then commit: `docs(workflow): page lane and system lane; one harden round (breeder's pick, Option A)`.

## Phase G — System check: workflow, boards, skills, agents

### Task 16: One health pass, reported as a table

- [ ] `python3 scripts/build_agent_registry.py --check` (47 agents, 0 problems on 2026-10-09).
- [ ] Dispatch `@bsuk-agent-system-qa` once over `.claude/agents` and `.claude/skills` (now with `bsuk-cta` and `bsuk-cta-agent`).
- [ ] `python3 scripts/quality_report.py` §5 (`untested` rules = deletion candidates); `npm run check:workflow`; `npm run check:boards`.
- [ ] Report: one row per check with its examined count and result, in the session brief. Fixes go to the system lane unless one blocks Manchester.
