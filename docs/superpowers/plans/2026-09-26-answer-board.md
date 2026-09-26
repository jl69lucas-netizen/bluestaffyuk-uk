# Answer Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One standing claude.ai board, "Questions for You", where Claude posts batches of questions (text or choice) for the user, the user answers in place with autosave, and each batch's **Send to Claude Code** hands the answers to a watching Claude session.

**Architecture:** The page is a static shell (`scripts/build_answer_board.py` → `docs/artifacts/bsuk-answer-board.html`); questions live in the artifact's `db` as `batches/<id>` documents that Claude writes with the ArtifactData tool from JSON files made by `scripts/answer_board_batch.py`. The inlined client (`scripts/answer_board_client.js`) renders open batches from `db`, saves answers one document per question with a browser draft as backup, and on Send writes a snapshot and calls `comments.sendToClaude` with a short note naming it. Every capability is optional (`claude.use()` → `null` hides only its affordance); `#demo` renders an embedded demo batch for local checks.

**Tech Stack:** Python 3.9 stdlib, plain ES2017 (no libraries), pytest, claude.ai Artifact runtime contract 0.2.59 (`db`, `comments`, `downloads`).

**Spec:** `docs/superpowers/specs/2026-09-26-answer-board-design.md` rev 2 (Artifact https://claude.ai/artifact/53L9VZvUS3Q4UfnqyDAYWV).

**Working directory for every command:** `/Users/apple/Downloads/BSUK-answers` (branch `answer-board`, from `foundation` at `e9b3c1b`). Never push; there is no remote.

**Commit trailer — every commit, exactly this line, whatever model you are:**
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`

**Baseline before Task 1:** `python3 -m pytest tests/py -q` on `foundation` = 5169 passed, 1 skipped, 1 xfailed.

---

## File structure

| File | Responsibility |
|---|---|
| Create `scripts/answer_sheet.py` | `parse_sheet(text)` and `SheetError`: sheet markdown → sections + questions (text or choice) |
| Create `scripts/answer_board_batch.py` | `slug()`, `make_batch()`, CLI: sheet → batch JSON under `docs/reference/answer-board/batches/` |
| Create `scripts/build_answer_board.py` | `render_shell(demo_batch)`, CLI: the static board page |
| Create `scripts/answer_board_client.js` | Browser behaviour (render from `db`, autosave, Send, Copy, Download, Done archive, demo) |
| Create `docs/reference/answer-board/demo.md` | The demo batch's sheet (one text, one choice, one text question) |
| Create `docs/reference/answer-board/README.md` | Posting, receiving, marking received |
| Create `docs/reference/answer-board/batches/2026-09-24-questions-for-lisa-bright.json` | Lisa's batch (generated) |
| Create `docs/reference/answer-board/answers/.gitkeep` | Received answers land here |
| Create `docs/artifacts/bsuk-answer-board.html` | Generated board page |
| Create `tests/py/test_answer_board.py` + `tests/py/fixtures/answer_board/*.md` | Tests |
| Modify `CLAUDE.md` | Section "Questions for the user — the answer board" (bullets, not a numbered list) |
| Modify `docs/reference/quick-start.md` | Entry "Ask the user questions" / "read my answers" |
| Modify `docs/reference/session-log.md` | Build record + KI 41 line |
| Modify `docs/reference/questions-for-lisa.md` + `docs/artifacts/bsuk-questions-for-lisa.html` | Pointer to the board (Task 7, after the board URL exists) |

---

### Task 1: Sheet parser (`scripts/answer_sheet.py`)

**Files:** Create `scripts/answer_sheet.py`, `tests/py/test_answer_board.py`, `tests/py/fixtures/answer_board/{mini,gap,dup,nobold,stray}.md`

- [ ] **Step 1: Write the fixtures**

`tests/py/fixtures/answer_board/mini.md`:
```markdown
# Mini sheet

Answer briefly. **Where it goes** says where each answer is kept.

## First part

1. **Is the sky blue?** On most days. **Where it goes:** `data/settings.json`.
2. **Which layout?** Pick one,
   then add a note if you like.
   - (a) Workspace rail
   - (b) Side by side

## Second part

3. **Any other thoughts?** Anything at all.

## What happens next

We read the answers and save them.
```

`gap.md`:
```markdown
# Gap sheet

## Part

1. **One?** Text.
3. **Three?** Text.
```

`dup.md`:
```markdown
# Dup sheet

## Part

1. **One?** Text.
1. **One again?** Text.
```

`nobold.md`:
```markdown
# No bold sheet

## Part

1. A question with no bold text.
```

`stray.md`:
```markdown
# Stray option sheet

## Part

   - (a) An option with no question
```

- [ ] **Step 2: Write the failing tests** — `tests/py/test_answer_board.py`:

```python
"""The answer board (spec docs/superpowers/specs/2026-09-26-answer-board-design.md).

One standing board holds every batch of questions Claude has for the user. A batch is made
from a question sheet; answers are keyed by question number, so the parser is strict about
numbering — a renumbered sheet would attach saved answers to the wrong question.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import answer_sheet  # noqa: E402

FIX = ROOT / "tests" / "py" / "fixtures" / "answer_board"
LISA = ROOT / "docs" / "reference" / "questions-for-lisa.md"


def parse(name):
    return answer_sheet.parse_sheet((FIX / name).read_text(encoding="utf-8"))


def all_questions(sheet):
    return [q for s in sheet["sections"] for q in s["questions"]]


def test_mini_sheet_parses_title_sections_and_questions():
    sheet = parse("mini.md")
    assert sheet["title"] == "Mini sheet"
    assert "Answer briefly." in sheet["preamble"]
    assert [s["title"] for s in sheet["sections"]] == ["First part", "Second part", "What happens next"]
    assert [(q["n"], q["key"], q["question"], q["kind"]) for q in all_questions(sheet)] == [
        (1, "q01", "Is the sky blue?", "text"),
        (2, "q02", "Which layout?", "choice"),
        (3, "q03", "Any other thoughts?", "text")]


def test_choice_options_are_kept_in_order_and_context_is_joined():
    q2 = all_questions(parse("mini.md"))[1]
    assert q2["options"] == [{"id": "a", "label": "Workspace rail"}, {"id": "b", "label": "Side by side"}]
    assert q2["context"] == "Pick one, then add a note if you like."
    assert q2["where"] == ""


def test_where_it_goes_is_split_from_the_context():
    q1 = all_questions(parse("mini.md"))[0]
    assert q1["context"] == "On most days." and q1["where"] == "`data/settings.json`."
    assert q1["options"] == []


def test_a_section_without_questions_keeps_its_prose():
    last = parse("mini.md")["sections"][-1]
    assert last["questions"] == [] and last["lead"] == "We read the answers and save them."


@pytest.mark.parametrize("name, message", [
    ("gap.md", "line 6: expected question 2, found 3"),
    ("dup.md", "line 6: question 1 is numbered twice (first on line 5)"),
    ("nobold.md", "line 5: question 1 has no **bold question**"),
    ("stray.md", "line 5: an option must sit under a question"),
])
def test_malformed_sheets_are_refused_with_the_line(name, message):
    with pytest.raises(answer_sheet.SheetError) as err:
        parse(name)
    assert str(err.value) == message


def test_a_sheet_must_start_with_a_title():
    with pytest.raises(answer_sheet.SheetError, match="line 1"):
        answer_sheet.parse_sheet("## No title\n\n1. **Q?** x\n")


def test_a_repeated_option_id_is_refused():
    # Lines: 1 "# T", 2 "", 3 "## S", 4 "", 5 the question, 6 "(a) One", 7 "(a) Two".
    with pytest.raises(answer_sheet.SheetError, match="line 7: option a is listed twice"):
        answer_sheet.parse_sheet("# T\n\n## S\n\n1. **Q?** x\n   - (a) One\n   - (a) Two\n")


def test_the_lisa_sheet_parses_to_21_text_questions():
    sheet = answer_sheet.parse_sheet(LISA.read_text(encoding="utf-8"))
    qs = all_questions(sheet)
    assert [q["key"] for q in qs] == [f"q{n:02d}" for n in range(1, 22)]
    assert {q["kind"] for q in qs} == {"text"}
    assert sheet["sections"][-1]["title"] == "What happens next"
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: collection error, `ModuleNotFoundError: No module named 'answer_sheet'`.

- [ ] **Step 4: Write `scripts/answer_sheet.py`**

```python
"""Parse a question sheet for the answer board.

Spec: docs/superpowers/specs/2026-09-26-answer-board-design.md §4. A sheet is markdown: a
'# Title' line, a preamble, then '## Section' headings. A numbered item
'N. **Question** context… **Where it goes:** …' is a question; wrapped lines are indented
under it, and indented '- (x) Label' lines are its options, which make it a choice question.
A section without numbered items is prose. Answers are keyed q01, q02, …, so numbering must
run 1..N with no gaps or repeats.
"""
import re

ITEM = re.compile(r"(\d+)\. (.*)")
OPTION = re.compile(r"\s+- \(([a-z0-9])\) (.+)")
BOLD = re.compile(r"\*\*(.+?)\*\*\s*(.*)", re.S)
GOES = "**Where it goes:**"


class SheetError(ValueError):
    """A sheet the board cannot use; the message names the line."""


def _finish(item):
    joined = " ".join(" ".join(item["lines"]).split())
    m = BOLD.match(joined)
    if not m:
        raise SheetError(f"line {item['line']}: question {item['n']} has no **bold question**")
    context, _, where = m.group(2).partition(GOES)
    return {"n": item["n"], "key": f"q{item['n']:02d}", "question": m.group(1).strip(),
            "context": context.strip(), "where": where.strip(),
            "kind": "choice" if item["options"] else "text", "options": item["options"]}


def parse_sheet(text):
    """Return {"title", "preamble", "sections": [{"title", "lead", "markdown", "questions"}]}.

    Each question: {"n", "key", "question", "context", "where", "kind", "options"}.
    """
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise SheetError("line 1: a sheet starts with '# Title'")
    preamble, sections = [], []
    section = item = None
    expected, seen = 1, {}

    def close_item():
        nonlocal item
        if item is not None:
            section["questions"].append(_finish(item))
            item = None

    for no, line in enumerate(lines[1:], start=2):
        if line.startswith("## "):
            close_item()
            section = {"title": line[3:].strip(), "lead": [], "body": [], "questions": []}
            sections.append(section)
            continue
        if section is None:
            preamble.append(line)
            continue
        section["body"].append(line)
        opt = OPTION.match(line)
        if opt:
            if item is None:
                raise SheetError(f"line {no}: an option must sit under a question")
            if any(o["id"] == opt.group(1) for o in item["options"]):
                raise SheetError(f"line {no}: option {opt.group(1)} is listed twice")
            item["options"].append({"id": opt.group(1), "label": opt.group(2).strip()})
            continue
        m = ITEM.match(line)
        if m:
            close_item()
            n = int(m.group(1))
            if n in seen:
                raise SheetError(f"line {no}: question {n} is numbered twice (first on line {seen[n]})")
            if n != expected:
                raise SheetError(f"line {no}: expected question {expected}, found {n}")
            seen[n] = no
            expected += 1
            item = {"n": n, "line": no, "lines": [m.group(2)], "options": []}
        elif item is not None and (line.startswith(" ") or not line.strip()):
            item["lines"].append(line.strip())
        else:
            close_item()
            section["lead"].append(line)
    close_item()
    for s in sections:
        s["lead"] = "\n".join(s["lead"]).strip()
        s["markdown"] = "\n".join(s.pop("body")).strip()
    return {"title": lines[0][2:].strip(), "preamble": "\n".join(preamble).strip(),
            "sections": sections}
```

- [ ] **Step 5: Run to verify pass**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: `11 passed`.

- [ ] **Step 6: Commit**

```bash
git add scripts/answer_sheet.py tests/py/test_answer_board.py tests/py/fixtures/answer_board
git commit -m "feat: answer sheet parser — text and choice questions

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Batch maker (`scripts/answer_board_batch.py`) and Lisa's batch

**Files:** Create `scripts/answer_board_batch.py`, `docs/reference/answer-board/batches/2026-09-24-questions-for-lisa-bright.json` (generated); append to `tests/py/test_answer_board.py`

- [ ] **Step 1: Append the failing tests**

```python
import answer_board_batch  # noqa: E402

BATCH_KEYS = {"id", "title", "project", "askedAt", "intro", "status", "receivedAt",
              "receivedCommit", "sections", "questions"}
Q_KEYS = {"n", "key", "section", "question", "context", "where", "kind", "options"}


def test_slug_is_lowercase_hyphenated_and_capped():
    assert answer_board_batch.slug("Questions for Lisa Bright") == "questions-for-lisa-bright"
    assert answer_board_batch.slug("Project 5 · London board picks!") == "project-5-london-board-picks"
    assert len(answer_board_batch.slug("x" * 200)) == 60


def test_make_batch_has_the_spec_shape():
    batch = answer_board_batch.make_batch(parse("mini.md"), "2026-09-26-mini", "tools", "2026-09-26T12:00:00Z")
    assert set(batch) == BATCH_KEYS
    assert batch["status"] == "open" and batch["receivedAt"] == "" and batch["receivedCommit"] == ""
    assert [s["title"] for s in batch["sections"]] == ["First part", "Second part", "What happens next"]
    for q in batch["questions"]:
        assert set(q) == Q_KEYS
    assert [q["section"] for q in batch["questions"]] == [0, 0, 1]
    assert batch["questions"][1]["kind"] == "choice"


def test_the_cli_writes_the_lisa_batch_deterministically(tmp_path):
    cmd = [sys.executable, str(ROOT / "scripts/answer_board_batch.py"), str(LISA),
           "--project", "site-content", "--date", "2026-09-24", "--out-dir", str(tmp_path)]
    first = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert first.returncode == 0, first.stderr
    out = tmp_path / "2026-09-24-questions-for-lisa-bright.json"
    body = out.read_bytes()
    assert subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT).returncode == 0
    assert out.read_bytes() == body
    batch = json.loads(body)
    assert batch["id"] == "2026-09-24-questions-for-lisa-bright"
    assert batch["askedAt"] == "2026-09-24T12:00:00Z" and len(batch["questions"]) == 21
    assert len(body) < 256 * 1024
    assert "21 questions" in first.stdout


def test_the_committed_lisa_batch_matches_the_sheet():
    committed = ROOT / "docs/reference/answer-board/batches/2026-09-24-questions-for-lisa-bright.json"
    sheet = answer_sheet.parse_sheet(LISA.read_text(encoding="utf-8"))
    expected = answer_board_batch.make_batch(sheet, "2026-09-24-questions-for-lisa-bright",
                                             "site-content", "2026-09-24T12:00:00Z")
    assert json.loads(committed.read_text(encoding="utf-8")) == expected


def test_the_cli_exits_non_zero_on_a_bad_sheet(tmp_path):
    run = subprocess.run([sys.executable, str(ROOT / "scripts/answer_board_batch.py"),
                          str(FIX / "gap.md"), "--project", "x", "--out-dir", str(tmp_path)],
                         capture_output=True, text=True, cwd=ROOT)
    assert run.returncode == 1 and "expected question 2, found 3" in run.stderr
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: collection error, `No module named 'answer_board_batch'`.

- [ ] **Step 3: Write `scripts/answer_board_batch.py`**

```python
"""Turn a question sheet into an answer-board batch (spec §5 and §7).

The batch JSON is what Claude writes to the board's `db` as `batches/<id>` with the
ArtifactData tool (`set`, `file_path` = the file this writes). The file is kept in the repo
as the record of what was asked.

    python3 scripts/answer_board_batch.py <sheet.md> --project <name> [--date YYYY-MM-DD]
        [--batch-id <id>] [--out-dir <dir>]
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from answer_sheet import SheetError, parse_sheet  # noqa: E402

OUT_DIR = ROOT / "docs" / "reference" / "answer-board" / "batches"
MAX_BYTES = 256 * 1024  # the db's per-document cap


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60].rstrip("-") or "batch"


def make_batch(sheet, batch_id, project, asked_at):
    questions = [
        {"n": q["n"], "key": q["key"], "section": i, "question": q["question"],
         "context": q["context"], "where": q["where"], "kind": q["kind"], "options": q["options"]}
        for i, s in enumerate(sheet["sections"]) for q in s["questions"]]
    return {"id": batch_id, "title": sheet["title"], "project": project, "askedAt": asked_at,
            "intro": sheet["preamble"], "status": "open", "receivedAt": "", "receivedCommit": "",
            "sections": [{"title": s["title"], "lead": s["lead"]} for s in sheet["sections"]],
            "questions": questions}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Make an answer-board batch from a question sheet.")
    ap.add_argument("sheet")
    ap.add_argument("--project", required=True, help="e.g. site-content, project-5, tools")
    ap.add_argument("--date", help="YYYY-MM-DD; default today (UTC)")
    ap.add_argument("--batch-id")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    a = ap.parse_args(argv)
    path = pathlib.Path(a.sheet)
    try:
        sheet = parse_sheet(path.read_text(encoding="utf-8"))
    except SheetError as e:
        print(f"{path}: {e}", file=sys.stderr)
        return 1
    if a.date:
        date, asked_at = a.date, f"{a.date}T12:00:00Z"
    else:
        now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        date, asked_at = now.date().isoformat(), now.strftime("%Y-%m-%dT%H:%M:%SZ")
    batch_id = a.batch_id or f"{date}-{slug(sheet['title'])}"
    batch = make_batch(sheet, batch_id, a.project, asked_at)
    body = json.dumps(batch, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if len(body.encode("utf-8")) >= MAX_BYTES:
        print(f"{path}: the batch is over 256 KiB; split the sheet", file=sys.stderr)
        return 1
    out = pathlib.Path(a.out_dir) / f"{batch_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    choice = sum(q["kind"] == "choice" for q in batch["questions"])
    print(f"{out} — {len(batch['questions'])} questions ({choice} choice), batch {batch_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Generate Lisa's batch**

Run: `python3 scripts/answer_board_batch.py docs/reference/questions-for-lisa.md --project site-content --date 2026-09-24`
Expected: `…/docs/reference/answer-board/batches/2026-09-24-questions-for-lisa-bright.json — 21 questions (0 choice), batch 2026-09-24-questions-for-lisa-bright`

- [ ] **Step 5: Run to verify pass**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: `16 passed`.

- [ ] **Step 6: Commit**

```bash
git add scripts/answer_board_batch.py tests/py/test_answer_board.py docs/reference/answer-board/batches
git commit -m "feat: answer board batch maker; Lisa's 21 questions as the first batch

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Board shell (`scripts/build_answer_board.py`)

**Files:** Create `scripts/build_answer_board.py`, `scripts/answer_board_client.js` (stub), `docs/reference/answer-board/demo.md`; append tests

- [ ] **Step 1: Write the demo sheet** — `docs/reference/answer-board/demo.md`:

```markdown
# Demo batch

This is a demo batch, shown only on the local preview (`#demo`). On claude.ai the board shows
the real batches Claude has posted.

## A text question and a choice

1. **What colour is the front door?** Any answer will do. **Where it goes:** nowhere; this is a demo.
2. **Which layout do you prefer?** Pick one; add a note if you like.
   - (a) Workspace rail
   - (b) Side by side

## One more

3. **Anything else?** Leave it empty, mark it Not yet, or Skip it.
```

- [ ] **Step 2: Create the client stub** — `scripts/answer_board_client.js`:
```js
/* Answer board client: written in Task 4. */
```

- [ ] **Step 3: Append the failing tests**

```python
import build_answer_board  # noqa: E402


def shell():
    return build_answer_board.render_shell(build_answer_board.demo_batch())


def test_the_shell_holds_the_layout_containers_and_no_real_questions():
    page = shell()
    for marker in ('id="rail-batches"', 'id="batches"', 'id="done"', 'id="status-line"',
                   'id="total-done"', 'id="bar"', "<title>Questions for You</title>"):
        assert marker in page, marker
    assert "Are there blue Staffy puppies" not in page  # real questions come from db


def test_the_demo_batch_is_embedded_as_json_without_a_closing_script_tag():
    page = shell()
    blob = page.split('<script type="application/json" id="demo-batch">', 1)[1].split("</script>", 1)[0]
    demo = json.loads(blob)
    assert demo["id"] == "demo" and [q["kind"] for q in demo["questions"]] == ["text", "choice", "text"]
    evil = dict(demo, intro="has </script> inside")
    out = build_answer_board.render_shell(evil)
    blob = out.split('<script type="application/json" id="demo-batch">', 1)[1].split("</script>", 1)[0]
    assert json.loads(blob)["intro"] == "has </script> inside"


def test_only_google_fonts_is_referenced():
    hosts = set(re.findall(r'(?:src|href)="https?://([^/"]+)', shell()))
    assert hosts <= {"fonts.googleapis.com"}, hosts


def test_the_shell_builds_byte_identically(tmp_path):
    cmd = [sys.executable, str(ROOT / "scripts/build_answer_board.py"), "--out", str(tmp_path / "b.html")]
    run = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert run.returncode == 0, run.stderr
    first = (tmp_path / "b.html").read_bytes()
    subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert (tmp_path / "b.html").read_bytes() == first
```

- [ ] **Step 4: Run to verify failure**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: collection error, `No module named 'build_answer_board'`.

- [ ] **Step 5: Write `scripts/build_answer_board.py`**

```python
"""Build the answer board page — a static shell; the questions come from the board's db.

Spec: docs/superpowers/specs/2026-09-26-answer-board-design.md §3, §6, §8. Layout A: a
sticky progress rail and a wide question column (a top bar under 900px). The client
(scripts/answer_board_client.js) is inlined; the demo batch is embedded for `#demo`.

    python3 scripts/build_answer_board.py [--out docs/artifacts/bsuk-answer-board.html]

Publish with capabilities {db: {rules: [{path: "", read: "admin", write: "admin"}]},
comments: {}, downloads: true}.
"""
import argparse
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from answer_board_batch import make_batch  # noqa: E402
from answer_sheet import parse_sheet  # noqa: E402

CLIENT_JS = ROOT / "scripts" / "answer_board_client.js"
DEMO = ROOT / "docs" / "reference" / "answer-board" / "demo.md"
OUT = ROOT / "docs" / "artifacts" / "bsuk-answer-board.html"
TITLE = "Questions for You"

CSS = """
:root{--ground:#F3F1EC;--paper:#FFFFFF;--ink:#1B2430;--ink-2:#46566B;--ink-3:#7A8797;--line:#DAD6CC;--blue:#2C4A6B;--blue-soft:#E4EAF1;--steel:#8FA3B8;--code-bg:#ECE9E1;--ok:#2F6B4F;--warn:#9A4A2A;--brass:#A8851A;--field:#FCFBF8;--on-blue:#FFFFFF}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--ink-2:#B4BFCC;--ink-3:#7F8C9B;--line:#2C3743;--blue:#8FB3D9;--blue-soft:#22303F;--steel:#5C7086;--code-bg:#111820;--ok:#7FC49F;--warn:#E39B7A;--brass:#D9B84A;--field:#161D26;--on-blue:#141A21}}
:root[data-theme="dark"]{--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--ink-2:#B4BFCC;--ink-3:#7F8C9B;--line:#2C3743;--blue:#8FB3D9;--blue-soft:#22303F;--steel:#5C7086;--code-bg:#111820;--ok:#7FC49F;--warn:#E39B7A;--brass:#D9B84A;--field:#161D26;--on-blue:#141A21}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 "Source Sans 3",system-ui,-apple-system,sans-serif}
a{color:var(--blue)}
.app{display:grid;grid-template-columns:300px minmax(0,1fr);min-height:100vh}
.rail{position:sticky;top:0;height:100vh;overflow:auto;background:var(--paper);border-right:1px solid var(--line);padding:24px 18px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--blue);font-weight:600;margin:0 0 6px}
.count{font:700 30px/1.1 Fraunces,Georgia,serif;margin:4px 0 8px}.count span{font-size:15px;color:var(--ink-3);font-weight:600}
.bar{height:6px;background:var(--line);border-radius:6px;overflow:hidden}.bar i{display:block;height:100%;width:0;background:var(--ok);transition:width .2s}
.muted{font-size:12px;color:var(--ink-3);margin:6px 0}
.navbatch{display:flex;justify-content:space-between;gap:8px;margin:16px 0 4px;font-size:13px;font-weight:700;color:var(--ink);text-decoration:none}
.navbatch small{color:var(--ink-3);font-weight:600}
.new{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;background:var(--brass);color:var(--on-blue);border-radius:4px;padding:1px 5px;margin-left:6px}
.navq{display:flex;gap:8px;align-items:center;padding:3px 4px;border-radius:4px;font-size:13px;color:var(--ink-2);text-decoration:none}
.navq:hover{background:var(--blue-soft)}.navq b{min-width:18px;color:var(--blue)}
.dot{width:10px;height:10px;border-radius:50%;border:1.5px solid var(--ink-3);flex:none}
[data-state="answered"] .dot{background:var(--ok);border-color:var(--ok)}
[data-state="skip"] .dot{background:var(--brass);border-color:var(--brass)}
[data-state="not_yet"] .dot{border-style:dashed;border-color:var(--steel);background:var(--blue-soft)}
.main{padding:32px clamp(16px,4vw,56px) 96px;min-width:0}.main>*{max-width:1120px}
header.mast{padding-bottom:16px;border-bottom:3px solid var(--blue);margin-bottom:16px}
h1.title{font-family:Fraunces,Georgia,serif;font-weight:700;font-size:clamp(28px,4vw,42px);line-height:1.08;margin:0}
.note{background:var(--blue-soft);border:1px solid var(--line);border-radius:6px;padding:10px 14px;font-size:15px;margin:0 0 16px}
.btn{font:inherit;font-size:13px;font-weight:600;padding:8px 14px;border-radius:6px;border:1px solid var(--blue);background:var(--blue);color:var(--on-blue);cursor:pointer;text-decoration:none;display:inline-block;text-align:center}
.btn.ghost{background:transparent;color:var(--blue)}.btn:disabled{opacity:.45;cursor:not-allowed}.btn.big{font-size:16px;padding:12px 22px}
button:focus-visible,a:focus-visible,textarea:focus-visible,summary:focus-visible{outline:3px solid var(--steel);outline-offset:2px}
.batch{margin:0 0 34px;scroll-margin-top:16px}
.bhead{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin:0 0 10px}
.bhead h2{font:700 26px/1.2 Fraunces,Georgia,serif;margin:0}
.pill{display:inline-block;border-radius:50px;padding:2px 10px;font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;border:1px solid var(--line);background:var(--paper);color:var(--ink-2)}
section.sec{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:20px 26px 22px;margin:0 0 14px}
section.sec h3.st{font:600 21px/1.25 Fraunces,Georgia,serif;margin:0 0 10px}
.intro p,.lead p,.ctx p{max-width:78ch}
.q{border:1px solid var(--line);border-left:4px solid var(--line);border-radius:8px;padding:16px 18px;margin:0 0 14px;background:var(--paper);scroll-margin-top:16px}
.q[data-state="answered"]{border-left-color:var(--ok)}.q[data-state="skip"]{border-left-color:var(--brass)}.q[data-state="not_yet"]{border-left-color:var(--steel)}
.q h4{font:600 18px/1.3 Fraunces,Georgia,serif;margin:0 0 4px}.qn{color:var(--blue);margin-right:6px}
.ctx{color:var(--ink-2);font-size:15px}.ctx p{margin:4px 0}
.where{font-size:12px;color:var(--ink-3);margin:6px 0}
code{font:13px/1.5 "JetBrains Mono",ui-monospace,Menlo,monospace;background:var(--code-bg);padding:1px 5px;border-radius:4px}
label.lab{display:block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--blue);margin:12px 0 4px}
textarea{width:100%;min-height:72px;resize:vertical;font:15px/1.5 "Source Sans 3",system-ui,sans-serif;color:var(--ink);background:var(--field);border:1.5px solid var(--line);border-radius:6px;padding:10px 12px}
textarea.notefield{min-height:48px}
textarea:focus{border-color:var(--blue);background:var(--paper)}
.opts{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 2px}
.opt{font:inherit;font-size:14px;text-align:left;border:1.5px solid var(--line);border-radius:8px;padding:8px 14px;background:var(--field);color:var(--ink);cursor:pointer}
.opt b{color:var(--blue);margin-right:6px}
.opt[aria-pressed="true"]{border-color:var(--ok);background:var(--blue-soft);font-weight:600}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px;font-size:13px;color:var(--ink-3)}
.chip{font:inherit;font-size:12px;border:1px solid var(--line);border-radius:50px;padding:3px 11px;background:var(--paper);color:var(--ink-2);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--blue-soft);border-color:var(--blue);color:var(--blue);font-weight:600}
.tick{margin-left:auto;color:var(--ok);font-weight:600;font-size:12px}
section.send{border:2px solid var(--blue)}
.sendrow{display:flex;gap:16px;align-items:center;flex-wrap:wrap}.sendrow>div{flex:1;min-width:240px}
.sendstatus{font-size:14px;color:var(--ink-2);margin:10px 0 0}
details#done{margin-top:40px}details#done>summary{cursor:pointer;font:600 20px Fraunces,Georgia,serif}
.donerow{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:10px 0}
.donerow ol{margin:8px 0 0;padding-left:22px;font-size:14px}
@media (max-width:900px){.app{display:block}.rail{position:sticky;top:0;height:auto;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;padding:10px 16px;border-right:0;border-bottom:1px solid var(--line)}
.rail .eyebrow,#rail-batches,#total-detail{display:none}.rail .count{font-size:20px;margin:0}.rail .bar{flex:1;min-width:80px}#saved{flex-basis:100%;margin:0}
.main{padding:20px 16px 72px}section.sec{padding:16px}.q{padding:14px}}
@media (prefers-reduced-motion:reduce){.bar i{transition:none}}
"""


def demo_batch():
    sheet = parse_sheet(DEMO.read_text(encoding="utf-8"))
    return make_batch(sheet, "demo", "tools", "2026-09-26T12:00:00Z")


def render_shell(demo):
    blob = json.dumps(demo, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    client = CLIENT_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap">
<style>{CSS}</style></head><body>
<div class="app">
<aside class="rail" aria-label="Progress">
<p class="eyebrow">BlueStaffyUK · answer board</p>
<p class="count"><b id="total-done">0</b> / <b id="total-all">0</b><span> answered</span></p>
<div class="bar" aria-hidden="true"><i id="bar"></i></div>
<p id="total-detail" class="muted"></p>
<nav id="rail-batches" aria-label="Open batches"></nav>
<p id="saved" class="muted" aria-live="polite"></p>
</aside>
<main class="main">
<header class="mast"><p class="eyebrow">BlueStaffyUK · for you</p><h1 class="title">{html.escape(TITLE)}</h1></header>
<p id="status-line" class="note" role="status">Connecting to the board…</p>
<div id="batches"></div>
<details id="done" hidden><summary>Done</summary><div id="done-list"></div></details>
</main></div>
<script type="application/json" id="demo-batch">{blob}</script>
<script>{client}</script>
</body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the answer board page.")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    page = render_shell(demo_batch())
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"{out} — {len(page.encode('utf-8'))} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run to verify pass**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: `20 passed`.

- [ ] **Step 7: Commit**

```bash
git add scripts/build_answer_board.py scripts/answer_board_client.js docs/reference/answer-board/demo.md tests/py/test_answer_board.py
git commit -m "feat: answer board shell (layout A) with an embedded demo batch

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Client (`scripts/answer_board_client.js`)

**Files:** Replace `scripts/answer_board_client.js`; append tests

- [ ] **Step 1: Append the failing guards**

```python
CLIENT = ROOT / "scripts" / "answer_board_client.js"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_the_client_is_valid_javascript():
    run = subprocess.run(["node", "--check", str(CLIENT)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def test_every_capability_is_optional():
    js = CLIENT.read_text(encoding="utf-8")
    assert "window.claude && window.claude.use" in js
    for name in ("db", "comments", "downloads"):
        assert f'use.call(window.claude, "{name}")' in js
    assert js.count("if (!ns)") >= 3


def test_the_client_uses_the_spec_paths():
    js = CLIENT.read_text(encoding="utf-8")
    assert 'db.collection("batches")' in js
    assert '"batches/" + id + "/answers"' in js and '"batches/" + id + "/submissions"' in js
    for verb in ("canSendToClaude", "sendToClaude", "anchorFor", "onSnapshot", "localStorage"):
        assert verb in js, verb


def test_db_text_is_escaped_before_it_reaches_innerHTML():
    js = CLIENT.read_text(encoding="utf-8")
    assert "function esc(" in js and "function inline(" in js
    assert re.search(r"inline\(s\)\s*\{\s*s = esc\(s\)", js)


def test_the_longest_note_is_well_under_the_comment_limit():
    note = ("Answers submitted — " + "T" * 120 + " (" + "b" * 90 + "). Snapshot s-2026-09-26T10-11-12-000Z: "
            "99 answered, 99 skip, 99 not yet, 99 empty. Read db batches/" + "b" * 90 +
            "/submissions/s-2026-09-26T10-11-12-000Z.")
    assert len(note.encode("utf-8")) < 1024
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: the three content guards fail on the stub.

- [ ] **Step 3: Write the client** — `scripts/answer_board_client.js`:

```js
/* Answer board client (spec docs/superpowers/specs/2026-09-26-answer-board-design.md §5–§6).
   Inlined by scripts/build_answer_board.py. Batches (the questions) come from the board's db;
   answers save one document per question with a browser draft as backup. Every capability is
   optional: claude.use() may resolve null. `#demo` renders the embedded demo batch locally. */
(function () {
  "use strict";
  var DEMO = JSON.parse(document.getElementById("demo-batch").textContent);
  var DRAFT_KEY = "answer-board:v1";
  var CHIPS = ["not_yet", "skip"];
  var STATUSES = ["answered", "not_yet", "skip", "empty"];
  var batches = {};     // id -> batch document
  var answers = {};     // id -> { qNN -> {n, text, choice, status, updatedAt} }
  var subs = {};        // id -> unsubscribe for that batch's answers
  var rendered = {};    // id -> signature of the rendered batch
  var isNew = {};       // id -> true until the batch is scrolled into view
  var written = {}, timers = {}, inflight = {}, again = {};
  var db = null, comments = null, downloads = null, demo = false, firstBatches = true;

  function $(id) { return document.getElementById(id); }
  function setText(el, s) { if (typeof el === "string") el = $(el); if (el) el.textContent = s; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function inline(s) { s = esc(s);
    return s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  }
  function paras(md) {
    return String(md || "").split(/\n\s*\n/).filter(function (b) { return b.trim(); })
      .map(function (b) { return "<p>" + inline(b.split(/\s+/).join(" ").trim()) + "</p>"; }).join("");
  }
  function k(id, key) { return id + "::" + key; }
  function sig(a) { return JSON.stringify([a.text, a.choice, a.status]); }
  function skipLabel(b) { return b.project === "site-content" ? "Leave it off the site" : "Skip"; }
  function questionOf(id, key) {
    var qs = batches[id].questions;
    for (var i = 0; i < qs.length; i++) if (qs[i].key === key) return qs[i];
    return null;
  }
  function derive(q, a, chip) {
    if (chip) return chip;
    if (q.kind === "choice") return a.choice ? "answered" : "empty";
    return a.text.trim() ? "answered" : "empty";
  }
  function blank(q) { return { n: q.n, text: "", choice: "", status: "empty", updatedAt: 0 }; }

  // Browser draft: a per-viewer convenience that can be unavailable.
  function readDraft() {
    try { return JSON.parse(localStorage.getItem(DRAFT_KEY) || "{}") || {}; } catch (e) { return {}; }
  }
  function writeDraft() {
    try { localStorage.setItem(DRAFT_KEY, JSON.stringify(answers)); } catch (e) { /* storage blocked */ }
  }
  var draft = readDraft();
  function adopt(id, key, rec) {
    var a = answers[id][key];
    if (!a || !rec || typeof rec.updatedAt !== "number" || rec.updatedAt <= a.updatedAt) return false;
    a.text = typeof rec.text === "string" ? rec.text : "";
    a.choice = typeof rec.choice === "string" ? rec.choice : "";
    a.status = STATUSES.indexOf(rec.status) >= 0 ? rec.status : derive(questionOf(id, key), a, null);
    a.updatedAt = rec.updatedAt;
    return true;
  }
  function ensureAnswers(id) {
    if (answers[id]) return;
    answers[id] = {};
    batches[id].questions.forEach(function (q) { answers[id][q.key] = blank(q); });
    var d = draft[id] || {};
    Object.keys(d).forEach(function (key) { if (answers[id][key]) adopt(id, key, d[key]); });
  }

  // ---------- rendering ----------
  function cardHtml(b, q) {
    var id = b.id, dom = id + "--" + q.key;
    var h = '<article class="q" id="' + esc(dom) + '" data-batch="' + esc(id) + '" data-key="' + q.key + '" data-state="empty">' +
      '<h4><span class="qn">' + q.n + "</span>" + inline(q.question) + "</h4>" +
      '<div class="ctx">' + paras(q.context) + "</div>" +
      (q.where ? '<p class="where"><strong>Where it goes:</strong> ' + inline(q.where) + "</p>" : "");
    if (q.kind === "choice") {
      h += '<div class="opts" role="group" aria-label="Options">' + q.options.map(function (o) {
        return '<button type="button" class="opt" data-choice="' + esc(o.id) + '" aria-pressed="false"><b>' +
          esc(o.id.toUpperCase()) + "</b>" + inline(o.label) + "</button>";
      }).join("") + "</div>" +
        '<label class="lab" for="a-' + esc(dom) + '">Note (optional)</label>' +
        '<textarea class="notefield" id="a-' + esc(dom) + '" rows="2" autocomplete="off" placeholder="Add a note…"></textarea>';
    } else {
      h += '<label class="lab" for="a-' + esc(dom) + '">Your answer</label>' +
        '<textarea id="a-' + esc(dom) + '" rows="3" autocomplete="off" placeholder="Type your answer…"></textarea>';
    }
    return h + '<div class="row"><button type="button" class="chip" data-status="not_yet" aria-pressed="false">Not yet</button>' +
      '<button type="button" class="chip" data-status="skip" aria-pressed="false">' + esc(skipLabel(b)) + "</button>" +
      '<span class="tick" aria-live="polite"></span></div></article>';
  }
  function batchHtml(b) {
    var h = '<section class="batch" id="b-' + esc(b.id) + '" data-batch="' + esc(b.id) + '">' +
      '<div class="bhead"><h2>' + esc(b.title) + '</h2><span><span class="pill">' + esc(b.project) +
      '</span> <span class="pill">asked ' + esc(String(b.askedAt).slice(0, 10)) + "</span></span></div>" +
      (b.intro ? '<section class="sec intro">' + paras(b.intro) + "</section>" : "");
    b.sections.forEach(function (s, i) {
      var qs = b.questions.filter(function (q) { return q.section === i; });
      h += '<section class="sec"><h3 class="st">' + esc(s.title) + "</h3>" +
        '<div class="lead">' + paras(s.lead) + "</div>" + qs.map(function (q) { return cardHtml(b, q); }).join("") + "</section>";
    });
    return h + '<section class="sec send" data-send-card="' + esc(b.id) + '"><div class="sendrow"><div>' +
      "<h3 class=\"st\">Ready to send?</h3><p class=\"muted\" data-counts></p></div>" +
      '<button type="button" class="btn big" data-send>Send to Claude Code →</button></div>' +
      '<p class="sendstatus" role="status" data-send-status></p>' +
      '<div class="row"><span>No Claude session watching?</span>' +
      '<button type="button" class="chip" data-copy>Copy answers</button>' +
      '<button type="button" class="chip" data-download hidden>Download .md</button>' +
      "<span data-fallback aria-live=\"polite\"></span></div></section></section>";
  }
  function openIds() {
    return Object.keys(batches).filter(function (id) { return batches[id].status !== "received"; })
      .sort(function (x, y) {
        var a = batches[x].askedAt || "", b = batches[y].askedAt || "";
        return a < b ? 1 : a > b ? -1 : (x < y ? -1 : 1);
      });
  }
  function hasFocusIn(el) { return el && document.activeElement && el.contains(document.activeElement); }
  function renderBatches() {
    var host = $("batches"), ids = openIds();
    Object.keys(rendered).forEach(function (id) {
      if (ids.indexOf(id) < 0) { var gone = $("b-" + id); if (gone) gone.remove(); delete rendered[id]; }
    });
    ids.forEach(function (id, i) {
      var b = batches[id], s = JSON.stringify([b.title, b.project, b.askedAt, b.intro, b.sections, b.questions]);
      var el = $("b-" + id);
      if (!el || (rendered[id] !== s && !hasFocusIn(el))) {
        var wrap = document.createElement("div");
        wrap.innerHTML = batchHtml(b);
        var fresh = wrap.firstChild;
        if (el) el.replaceWith(fresh); else host.appendChild(fresh);
        rendered[id] = s;
        wire(fresh, id);
        el = fresh;
      }
      if (host.children[i] !== el) host.insertBefore(el, host.children[i] || null);
      Object.keys(answers[id]).forEach(function (key) { paintCard(id, key); });
    });
    renderRail();
    renderDone();
    paintTotals();
    if (!ids.length) setText("status-line", demo ? "Demo batch" : "No open questions right now. New batches appear here as soon as Claude posts them.");
    else setText("status-line", demo ? "Demo mode: answers are saved in this browser only." : "");
    $("status-line").hidden = !$("status-line").textContent;
  }
  function paintCard(id, key) {
    var a = answers[id][key], card = $(id + "--" + key);
    if (!card) return;
    var ta = card.querySelector("textarea");
    if (ta && document.activeElement !== ta && ta.value !== a.text) { ta.value = a.text; grow(ta); }
    card.querySelectorAll("[data-status]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.getAttribute("data-status") === a.status));
    });
    card.querySelectorAll("[data-choice]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.getAttribute("data-choice") === a.choice));
    });
    card.setAttribute("data-state", a.status);
    var nav = document.querySelector('.navq[href="#' + cssId(id + "--" + key) + '"]');
    if (nav) nav.setAttribute("data-state", a.status);
  }
  function cssId(s) { return window.CSS && CSS.escape ? CSS.escape(s) : s; }
  function counts(id) {
    var c = { answered: 0, skip: 0, not_yet: 0, empty: 0 };
    Object.keys(answers[id] || {}).forEach(function (key) { c[answers[id][key].status] += 1; });
    return c;
  }
  function renderRail() {
    var nav = $("rail-batches");
    nav.innerHTML = openIds().map(function (id) {
      var b = batches[id], c = counts(id), total = b.questions.length;
      return '<a class="navbatch" href="#b-' + esc(id) + '"><span>' + esc(b.title) +
        (isNew[id] ? '<span class="new">New</span>' : "") + "</span><small>" + (total - c.empty) + " / " + total + "</small></a>" +
        b.questions.map(function (q) {
          return '<a class="navq" href="#' + esc(id + "--" + q.key) + '" data-state="' + answers[id][q.key].status +
            '"><span class="dot"></span><b>' + q.n + "</b><span>" + esc(q.question.length > 42 ? q.question.slice(0, 41) + "…" : q.question) + "</span></a>";
        }).join("");
    }).join("");
  }
  function paintTotals() {
    var done = 0, all = 0, open = openIds();
    open.forEach(function (id) {
      var c = counts(id), n = batches[id].questions.length;
      all += n; done += n - c.empty;
      var card = document.querySelector('[data-send-card="' + cssId(id) + '"]');
      if (card) setText(card.querySelector("[data-counts]"), c.answered + " answered · " + c.not_yet + " not yet · " + c.skip + " skipped · " + c.empty + " empty");
    });
    setText("total-done", String(done));
    setText("total-all", String(all));
    $("bar").style.width = (all ? Math.round(done * 100 / all) : 0) + "%";
    setText("total-detail", open.length + (open.length === 1 ? " open batch" : " open batches"));
  }
  function renderDone() {
    var ids = Object.keys(batches).filter(function (id) { return batches[id].status === "received"; })
      .sort(function (x, y) { return (batches[y].receivedAt || "") < (batches[x].receivedAt || "") ? -1 : 1; });
    $("done").hidden = !ids.length;
    $("done-list").innerHTML = ids.map(function (id) {
      var b = batches[id];
      return '<div class="donerow" data-done="' + esc(id) + '"><strong>' + esc(b.title) + "</strong> " +
        '<span class="muted">received ' + esc(String(b.receivedAt).slice(0, 10)) +
        (b.receivedCommit ? " · commit " + esc(b.receivedCommit) : "") + "</span> " +
        '<button type="button" class="chip" data-show>Show answers</button><div data-answers></div></div>';
    }).join("");
    $("done-list").querySelectorAll("[data-show]").forEach(function (btn) {
      btn.addEventListener("click", function () { showDone(btn.closest("[data-done]")); });
    });
  }
  function showDone(row) {
    var id = row.getAttribute("data-done"), out = row.querySelector("[data-answers]");
    if (!db) return;
    db.collection("batches/" + id + "/answers").get().then(function (snap) {
      var got = {};
      snap.docs.forEach(function (d) { got[d.id] = d.data() || {}; });
      out.innerHTML = "<ol>" + batches[id].questions.map(function (q) {
        var a = got[q.key] || {}, opt = (q.options || []).filter(function (o) { return o.id === a.choice; })[0];
        return "<li><strong>" + inline(q.question) + "</strong> — " + esc(a.status || "empty") +
          (opt ? ": " + inline(opt.label) : "") + (a.text ? "<br>" + esc(a.text) : "") + "</li>";
      }).join("") + "</ol>";
    }, function (e) { setText(out, "Could not load (" + ((e && e.code) || "error") + ")"); });
  }
  function grow(ta) { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + 2 + "px"; }

  // ---------- saving ----------
  function touch(id, key) {
    answers[id][key].updatedAt = Date.now();
    writeDraft(); paintCard(id, key); renderRail(); paintTotals();
    var tick = document.getElementById(id + "--" + key).querySelector(".tick");
    if (!db) { setText("saved", "Saved in this browser"); setText(tick, "✓ saved here"); return; }
    setText("saved", "Saving…"); setText(tick, "");
    clearTimeout(timers[k(id, key)]);
    timers[k(id, key)] = setTimeout(function () { flush(id, key); }, 800);
  }
  function flush(id, key) {
    var t = k(id, key);
    clearTimeout(timers[t]); delete timers[t];
    var a = answers[id] && answers[id][key];
    if (!db || !a || a.updatedAt === 0 || written[t] === sig(a)) return inflight[t] || Promise.resolve();
    if (inflight[t]) { again[t] = true; return inflight[t]; }
    var body = { n: a.n, text: a.text, choice: a.choice, status: a.status, updatedAt: a.updatedAt };
    var p = db.collection("batches/" + id + "/answers").doc(key).set(body).then(function () {
      written[t] = sig(body);
      setText("saved", "Saved to the board " + new Date().toLocaleTimeString());
      var card = document.getElementById(id + "--" + key);
      if (card) setText(card.querySelector(".tick"), "✓ saved");
    }, function (e) {
      setText("saved", "Not saved to the board (" + ((e && e.code) || "error") + "). Kept in this browser.");
    }).then(function () {
      delete inflight[t];
      if (again[t]) { delete again[t]; return flush(id, key); }
    });
    inflight[t] = p;
    return p;
  }
  function flushBatch(id) { return Promise.all(Object.keys(answers[id]).map(function (key) { return flush(id, key); })); }

  // ---------- send, copy, download ----------
  function answersMarkdown(id) {
    var b = batches[id], out = ["# " + b.title + ": answers", "", "Batch " + id, ""];
    b.questions.forEach(function (q) {
      var a = answers[id][q.key], opt = (q.options || []).filter(function (o) { return o.id === a.choice; })[0];
      out.push("## " + q.n + ". " + q.question, "", "Status: " + a.status + (opt ? " — picked (" + opt.id + ") " + opt.label : ""), "");
      if (a.text.trim()) out.push(a.text.trim(), "");
    });
    return out.join("\n");
  }
  function flash(el, msg) { setText(el, msg); setTimeout(function () { setText(el, ""); }, 2500); }
  function onSend(id, card) {
    var btn = card.querySelector("[data-send]"), status = card.querySelector("[data-send-status]");
    if (!db) { setText(status, "This view cannot send. Use Copy answers."); return; }
    btn.disabled = true;
    setText(status, "Sending…");
    var sid = "s-" + new Date().toISOString().replace(/[:.]/g, "-"), c = counts(id), b = batches[id];
    var note = "Answers submitted — " + b.title + " (" + id + "). Snapshot " + sid + ": " + c.answered + " answered, " +
      c.skip + " skip, " + c.not_yet + " not yet, " + c.empty + " empty. Read db batches/" + id + "/submissions/" + sid + ".";
    // The send must start inside this click (it needs the viewer's recent gesture), so it runs
    // beside the saves; Claude reads the snapshot seconds later.
    var sending = !comments ? Promise.resolve("off") : comments.canSendToClaude().then(function (v) {
      if (v !== "available") return v;
      return comments.anchorFor(card).then(function (anchor) {
        return comments.sendToClaude({ anchor: anchor, text: note });
      }).then(function () { return "sent"; });
    }).catch(function (e) { return (e && e.code) || "error"; });
    var saving = flushBatch(id).then(function () {
      return db.collection("batches/" + id + "/submissions").doc(sid).set({
        at: new Date().toISOString(), id: sid, batchId: id, counts: c,
        answers: b.questions.map(function (q) {
          var a = answers[id][q.key], opt = (q.options || []).filter(function (o) { return o.id === a.choice; })[0];
          return { n: q.n, key: q.key, question: q.question, kind: q.kind, choice: a.choice,
            choiceLabel: opt ? opt.label : "", status: a.status, text: a.text };
        })
      });
    });
    Promise.all([saving, sending]).then(function (r) {
      var how = r[1];
      if (how === "sent") setText(status, "Sent to Claude Code (copy " + sid + "). Claude's reply will appear in the comment thread.");
      else if (how === "rate_limited") setText(status, "Saved as copy " + sid + ". Sending is limited for a moment; wait, then press Send again.");
      else if (how === "no_session") setText(status, "Saved on the board as copy " + sid + ", but no Claude Code session is watching this board right now. Tell Claude Code \"read my answers\", or use Copy answers.");
      else setText(status, "Saved on the board as copy " + sid + ", but sending to Claude isn't available here. Tell Claude Code \"read my answers\", or use Copy answers.");
    }, function (e) {
      setText(status, "The copy could not be saved (" + ((e && e.code) || "error") + "). Your answers are still here. Press Send again.");
    }).then(function () { btn.disabled = false; });
  }
  function copyText(text, el) {
    if (!navigator.clipboard) { flash(el, "Copy is blocked in this view"); return; }
    navigator.clipboard.writeText(text).then(function () { flash(el, "Copied"); }, function () { flash(el, "Copy is blocked in this view"); });
  }

  // ---------- wiring ----------
  function wire(section, id) {
    section.querySelectorAll("article.q").forEach(function (card) {
      var key = card.getAttribute("data-key"), q = questionOf(id, key), ta = card.querySelector("textarea");
      ta.addEventListener("input", function () {
        var a = answers[id][key];
        a.text = ta.value;
        a.status = derive(q, a, CHIPS.indexOf(a.status) >= 0 ? a.status : null);
        grow(ta); touch(id, key);
      });
      card.querySelectorAll("[data-choice]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var a = answers[id][key], c = btn.getAttribute("data-choice");
          a.choice = a.choice === c ? "" : c;
          a.status = derive(q, a, null);
          touch(id, key);
        });
      });
      card.querySelectorAll("[data-status]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var a = answers[id][key], chip = btn.getAttribute("data-status");
          a.status = a.status === chip ? derive(q, a, null) : chip;
          touch(id, key);
        });
      });
    });
    var card = section.querySelector("[data-send-card]");
    var sendBtn = card.querySelector("[data-send]");
    sendBtn.disabled = !db;
    if (!db) setText(card.querySelector("[data-send-status]"), demo ? "Demo: sending is off. Copy answers works." : "");
    sendBtn.addEventListener("click", function () { onSend(id, card); });
    card.querySelector("[data-copy]").addEventListener("click", function () {
      copyText(answersMarkdown(id), card.querySelector("[data-fallback]"));
    });
    var dl = card.querySelector("[data-download]");
    dl.hidden = !downloads;
    dl.addEventListener("click", function () {
      if (!downloads) return;
      downloads.save({ filename: id + "-answers.md", data: answersMarkdown(id) }).then(function (r) {
        flash(card.querySelector("[data-fallback]"), r && r.status === "saved" ? "Downloaded" : "");
      }, function (e) {
        if (e && e.code === "unavailable") dl.hidden = true;
        flash(card.querySelector("[data-fallback]"), "Download didn't happen (" + ((e && e.code) || "error") + ")");
      });
    });
    if (isNew[id] && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { delete isNew[id]; io.disconnect(); renderRail(); }
      });
      io.observe(section);
    }
  }

  // ---------- db ----------
  function subscribeAnswers(id) {
    if (subs[id]) return;
    subs[id] = db.collection("batches/" + id + "/answers").onSnapshot(function (snap) {
      snap.docs.forEach(function (d) {
        var rec = d.data();
        if (!rec || !answers[id][d.id]) return;
        written[k(id, d.id)] = sig({ text: rec.text || "", choice: rec.choice || "", status: rec.status });
        if (adopt(id, d.id, rec)) paintCard(id, d.id);
      });
      // A browser draft newer than the board is written up.
      Object.keys(answers[id]).forEach(function (key) {
        var a = answers[id][key];
        if (a.updatedAt && written[k(id, key)] !== sig(a)) flush(id, key);
      });
      writeDraft(); renderRail(); paintTotals();
    }, function (e) {
      setText("saved", "Answers for one batch stopped syncing (" + ((e && e.code) || "error") + "). Reload the page.");
    });
  }
  function onBatches(snap) {
    var seen = {};
    snap.docs.forEach(function (d) {
      var b = d.data();
      if (!b || !Array.isArray(b.questions) || !Array.isArray(b.sections)) return;
      b = JSON.parse(JSON.stringify(b));
      b.id = d.id;
      seen[d.id] = true;
      if (!batches[d.id] && !firstBatches) isNew[d.id] = true;
      batches[d.id] = b;
      ensureAnswers(d.id);
      if (b.status === "received") { if (subs[d.id]) { subs[d.id](); delete subs[d.id]; } }
      else subscribeAnswers(d.id);
    });
    Object.keys(batches).forEach(function (id) {
      if (!seen[id]) { if (subs[id]) { subs[id](); delete subs[id]; } delete batches[id]; }
    });
    firstBatches = false;
    renderBatches();
  }
  function noBoard() {
    setText("status-line", "");
    $("status-line").innerHTML = 'Open this board on claude.ai to see your questions. <a href="#demo" id="demo-link">Preview a demo batch</a>';
    $("status-line").hidden = false;
    $("demo-link").addEventListener("click", function () { setTimeout(function () { location.reload(); }, 0); });
  }
  function startDemo() {
    demo = true;
    batches.demo = DEMO;
    ensureAnswers("demo");
    renderBatches();
  }
  function connect() {
    var use = window.claude && window.claude.use;
    if (typeof use !== "function") { noBoard(); return; }
    use.call(window.claude, "comments").then(function (ns) { if (!ns) return; comments = ns; }, function () {});
    use.call(window.claude, "downloads").then(function (ns) {
      if (!ns) return;
      downloads = ns;
      document.querySelectorAll("[data-download]").forEach(function (b) { b.hidden = false; });
    }, function () {});
    use.call(window.claude, "db").then(function (ns) {
      if (!ns) { noBoard(); return; }
      db = ns;
      db.collection("batches").onSnapshot(onBatches, function (e) {
        setText("status-line", "The board's storage stopped (" + ((e && e.code) || "error") + "). Reload the page.");
        $("status-line").hidden = false;
      });
    }, function () { noBoard(); });
  }

  if (location.hash === "#demo") startDemo(); else connect();
})();
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: `25 passed`.

- [ ] **Step 5: Build the page**

Run: `python3 scripts/build_answer_board.py`
Expected: `…/docs/artifacts/bsuk-answer-board.html — <N> bytes`

- [ ] **Step 6: Commit**

```bash
git add scripts/answer_board_client.js tests/py/test_answer_board.py docs/artifacts/bsuk-answer-board.html
git commit -m "feat: answer board client — batches from db, autosave, Send to Claude Code, Done archive

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Browser check (controller)

The controller runs this in the Browser pane; an implementer reports "not run".

- [ ] Open `file:///Users/apple/Downloads/BSUK-answers/docs/artifacts/bsuk-answer-board.html` — expect "Open this board on claude.ai…" with a demo link, no console errors.
- [ ] Open `…/bsuk-answer-board.html#demo` — the demo batch renders; type in Q1, pick (b) on Q2, press Skip on Q3; the rail reads "3 / 3", dots green/green/brass; "Copy answers" copies markdown; reload — all three kept.
- [ ] Viewport 375×812: the rail is a top bar; `document.documentElement.scrollWidth <= innerWidth`.
- [ ] Dark colour scheme: text and chips readable.
- [ ] Clean up: `localStorage.removeItem("answer-board:v1")`. Fix any fault by returning the task to the implementer with the evidence.

---

### Task 6: Docs, rule and quick-start

**Files:** Create `docs/reference/answer-board/README.md`, `docs/reference/answer-board/answers/.gitkeep`; modify `CLAUDE.md`, `docs/reference/quick-start.md`, `docs/reference/session-log.md`; append tests

- [ ] **Step 1: Append the failing tests**

```python
def test_claude_md_carries_the_answer_board_rule():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "## Questions for the user — the answer board" in text
    section = text.split("## Questions for the user — the answer board", 1)[1].split("\n## ", 1)[0]
    for needle in ("scripts/answer_board_batch.py", "docs/reference/answer-board/README.md",
                   "ArtifactComments", "either/or"):
        assert needle in section, needle
    assert not re.search(r"^\d+\. \*\*", section, re.M), "use bullets: numbered bold items count as working rules"


def test_the_readme_names_the_board_url_and_the_paths():
    text = (ROOT / "docs/reference/answer-board/README.md").read_text(encoding="utf-8")
    assert "batches/<batchId>/submissions" in text and "docs/reference/answer-board/answers/" in text
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/py/test_answer_board.py -q`
Expected: the two new tests fail (section / file missing).

- [ ] **Step 3: Write `docs/reference/answer-board/README.md`** (the board URL is filled in by the controller in Task 7; until then the line reads as below)

```markdown
# The answer board

One standing claude.ai board, **Questions for You**, holds every batch of questions Claude has
for the user (spec `docs/superpowers/specs/2026-09-26-answer-board-design.md`). Board URL:
recorded here by the Task 7 publish.

## Post a batch

1. Write the questions as a sheet (`# Title`, `## Section`, `N. **Question?** context…`,
   optional `**Where it goes:** …`, optional indented `- (a) Option` lines for a choice) at
   `docs/reference/answer-board/batches/<YYYY-MM-DD>-<slug>.md`.
2. `python3 scripts/answer_board_batch.py <sheet> --project <site-content|project-5|tools|…>`
   writes `<batchId>.json` beside it and prints the batch id.
3. ArtifactData `set`, collection `batches`, doc_id `<batchId>`, `file_path` = that JSON, on the
   board URL. The batch appears on the board at once.
4. Commit the sheet and the JSON. In chat, say only: "N new questions on the board: <URL>".

## Receive answers

A session receives a Send only while it watches the board: at the start of any session that
may post or receive, run ArtifactComments `watch` on the board URL.

On a Send notification (or when the user says "read my answers"):

1. ArtifactData `get` the snapshot the note names: collection
   `batches/<batchId>/submissions`, doc_id `s-…`. With no snapshot, `list`
   `batches/<batchId>/answers`.
2. Save it as `docs/reference/answer-board/answers/<batchId>-<YYYY-MM-DD>.json` (as stored) and
   `.md` (question, status, picked option, text), and commit.
3. ArtifactData `update` `batches/<batchId>`: `status: "received"`, `receivedAt` (ISO time),
   `receivedCommit` (the short hash). The board moves the batch to Done.
4. ArtifactComments `reply` in the Send's thread with the counts and the commit, then act on
   the answers.

Answers are records of what the user said. Writing them into the site's data files is the
work that asked the questions (for the questions for Lisa: project 5, Known Issue 41).
```

And `docs/reference/answer-board/answers/.gitkeep` (empty).

- [ ] **Step 4: Add the CLAUDE.md section** — insert immediately before the line `## Gates — run these, do not re-derive them`:

```markdown
## Questions for the user — the answer board

- Two or more questions for the user, or any question that needs a written answer, go to the
  answer board as a batch (`python3 scripts/answer_board_batch.py`), never as a list in chat.
  Chat then says only "N new questions on the board: <link>".
- A single blocking either/or pick may still be asked in chat. Visual picks keep their browser
  mockups, and the board question links to the mockup.
- Watch the board with the ArtifactComments tool at the start of any session that may post or
  receive, so the user's **Send to Claude Code** reaches the session.
- Posting, receiving and marking a batch received: `docs/reference/answer-board/README.md`.

```

- [ ] **Step 5: Add the quick-start entry** — insert into `docs/reference/quick-start.md` immediately before the line `### "A puppy was reserved or sold"`:

```markdown
### "Ask the user questions" / "read my answers"
→ the answer board: `docs/reference/answer-board/README.md`. A batch is made with
`python3 scripts/answer_board_batch.py <sheet> --project <name>` and written to the board with
the ArtifactData tool; answers come back through the board's **Send to Claude Code** and are
saved under `docs/reference/answer-board/answers/`. The board page is built with
`python3 scripts/build_answer_board.py`.

```

- [ ] **Step 6: Add the session-log build record** — insert into `docs/reference/session-log.md` immediately before `## Known Issues`:

```markdown
## Answer board tool build (2026-09-26) — COMPLETE

Branch `answer-board` (worktree `/Users/apple/Downloads/BSUK-answers`), cut from `foundation` at `e9b3c1b`. Spec: `docs/superpowers/specs/2026-09-26-answer-board-design.md` (Artifact https://claude.ai/artifact/53L9VZvUS3Q4UfnqyDAYWV). Plan: `docs/superpowers/plans/2026-09-26-answer-board.md`.

What it added:
- **One standing board, "Questions for You"** (`scripts/build_answer_board.py` → `docs/artifacts/bsuk-answer-board.html`). Every batch of questions for the user is posted there; the user answers in place (text, or a choice plus a note; Not yet / Skip on every question) and presses **Send to Claude Code** per batch. Layout A: sticky progress rail, wide question column, a top bar on phones.
- **Batches live in the board's `db`**, written by Claude with the ArtifactData tool from `scripts/answer_board_batch.py`'s JSON (sheet parser `scripts/answer_sheet.py`), so posting never republishes the page. Answers save one document per question with a browser draft as backup; Send writes a snapshot and sends a short note (a comment is capped at 4 KiB) naming it.
- **The rule:** CLAUDE.md "Questions for the user — the answer board"; the procedure is `docs/reference/answer-board/README.md`. Lisa's 21 questions are the first batch (`docs/reference/answer-board/batches/2026-09-24-questions-for-lisa-bright.json`).

```

- [ ] **Step 7: KI 41** — in `docs/reference/session-log.md`, replace the sentence `Open until she answers.` in KI 41 with:

```markdown
Open until she answers. Since 2026-09-26 they are the first batch on the answer board (`docs/reference/answer-board/README.md`): the user types each answer there and presses Send to Claude Code.
```

- [ ] **Step 8: Run the doc guards**

Run: `python3 -m pytest tests/py/test_answer_board.py tests/py/test_claude_md.py tests/py/test_rules_index.py tests/py/test_questions_for_lisa.py -q`
Expected: all pass.

- [ ] **Step 9: Commit**

```bash
git add CLAUDE.md docs/reference tests/py/test_answer_board.py
git commit -m "docs: the answer board rule, procedure, quick-start entry and build record

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Verify, merge, publish, post Lisa's batch (controller)

- [ ] **Step 1: Branch checks** (worktree; if `node_modules` is missing, `ln -s /Users/apple/Downloads/BSUK/node_modules node_modules` and remove the link before merging): `npm run -s build` (exit 0), `python3 -m pytest tests/py -q` (5169 + this build's tests passed, 1 skipped, 1 xfailed), `npm run -s check:all` (exit 0).
- [ ] **Step 2: Whole-branch review** of `git diff foundation...answer-board` by a fresh reviewer; fix Critical/Important; re-review.
- [ ] **Step 3: Publish the board** — Artifact publish `docs/artifacts/bsuk-answer-board.html` (new artifact, icon `question`) with `capabilities: {db: {rules: [{path: "", read: "admin", write: "admin"}]}, comments: {}, downloads: true}`. Record the URL in `docs/reference/answer-board/README.md` (replace "recorded here by the Task 7 publish." with the URL), `docs/reference/session-log.md` (build record) and CLAUDE.md's first bullet ("…go to the answer board (<URL>)…").
- [ ] **Step 4: Post Lisa's batch** — ArtifactData `set`, collection `batches`, doc_id `2026-09-24-questions-for-lisa-bright`, `file_path` = the committed JSON; then `list` `batches` (1 document) and `list` with `as_level: "interact"` (must return nothing: the rules hide the batch from non-editors).
- [ ] **Step 5: Lisa's old link** — add to `docs/reference/questions-for-lisa.md` a final preamble paragraph: `**Answer these on the answer board:** <board URL> (the questions are the batch "Questions for Lisa Bright").`, rebuild with Task R6's command (`python3 scripts/build_report_artifact.py docs/reference/questions-for-lisa.md docs/artifacts/bsuk-questions-for-lisa.html "Questions for Lisa" "BlueStaffyUK · for Lisa Bright" "Questions only you can answer" "BlueStaffyUK — questions for Lisa Bright" "for Lisa: please answer" "2026-09-24" docs/reference/questions-for-lisa.md`), run `python3 -m pytest tests/py/test_questions_for_lisa.py -q`, republish to https://claude.ai/artifact/CvLPpj438KFNfJcFd9gFTH.
- [ ] **Step 6: Commit** the URL records; merge `--no-ff` into `foundation` (`merge: answer board tool build` + trailer); on `foundation` run build, pytest, check:all, `npm run -s ds:build`; record counts.
- [ ] **Step 7: Round trip with the user** — watch the board (ArtifactComments `watch`), ask the user to answer one question and press Send on the Lisa batch; on the notification follow README "Receive answers" (save, commit, reply) but leave the batch **open** (status stays `open`) since the other questions are unanswered.
- [ ] **Step 8: Close-out** — execution record appended to this plan; plan Artifact published; worktree removed; memory updated.
