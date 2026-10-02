#!/usr/bin/env python3
"""session_handoff.py — a paste-ready prompt that lets a new chat pick up where this one stopped.

    python3 scripts/session_handoff.py           # print the prompt
    python3 scripts/session_handoff.py --write   # print it and save it to
                                                 # docs/reference/handoff/<YYYY-MM-DD>-<branch>.md

Every line is read from the repo, never remembered: the worktree path, the branch, the short
HEAD sha and whether `git status` is clean; the last ten commits; the newest session brief
(docs/superpowers/sessions/*-session-brief.md) with its `## Open Flags` bullet lines and its
`## What's Next` lines; the newest plan in docs/superpowers/plans/ (by filename date) and the
heading of its first `### Task` that still has an unchecked `- [ ]` step; every
https://claude.ai/artifact/<id> link in the last five answer-board batch files plus CLAUDE.md;
the standing instructions; and the Gemini line.

Secrets: `.env` is read only to learn whether GEMINI_API_KEY has a non-empty value and to
learn every value it must never print. The finished prompt has every `.env` value of six or
more characters, and anything shaped like a key (`AQ.…`, `AIza…`, `sk-…`), replaced with
`[redacted]` before it is returned.

`build(root, branch=None)` is the pure entry point the tests call. Python 3.9 stdlib only.
"""
import argparse
import datetime
import importlib.util
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SESSIONS = "docs/superpowers/sessions"
PLANS = "docs/superpowers/plans"
BATCHES = "docs/reference/answer-board/batches"
HANDOFF = "docs/reference/handoff"
GEMINI_LOG = "docs/reports/gemini-usage.jsonl"

ARTIFACT = re.compile(r"https://claude\.ai/artifact/[A-Za-z0-9_-]+")
ENV_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
GEMINI_SET = re.compile(r"^\s*(?:export\s+)?GEMINI_API_KEY\s*=\s*['\"]?\s*[^\s'\"#]")
KEY_SHAPE = re.compile(r"AQ\.\S+|AIza\S+|(?<![A-Za-z0-9])sk-\S+")
TASK = re.compile(r"^###\s+Task\b")
OPEN_STEP = re.compile(r"^\s*- \[ \]")
REDACTED = "[redacted]"
MIN_SECRET = 6

STANDING = [
    "Read CLAUDE.md, docs/reference/page-run.md, the newest brief and MEMORY.md first",
    "Watch the answer board and any open page board with ArtifactComments at session start",
    "Commit after every task; do not push unless the user says so",
]
GEMINI_LINE = ("GEMINI_API_KEY is set in .env — delete it when image work is done "
               "(breeder's instruction, 2026-10-02)")


def _git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _read(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _section(text, heading):
    """Lines under `## <heading>` up to the next `## ` heading (an `###` stays inside)."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower() == heading.lower()
            continue
        if inside:
            out.append(line.rstrip())
    return out


def newest_brief(root):
    briefs = sorted((root / SESSIONS).glob("*-session-brief.md"))
    return briefs[-1] if briefs else None


def newest_plan(root):
    plans = sorted(p for p in (root / PLANS).glob("*.md")
                   if re.match(r"\d{4}-\d{2}-\d{2}-", p.name))
    return plans[-1] if plans else None


def first_open_task(text):
    """The heading of the first `### Task` with an unchecked `- [ ]` step, or None."""
    current = None
    for line in text.splitlines():
        if TASK.match(line):
            current = line.strip()
        elif current and OPEN_STEP.match(line):
            return current
    return None


def artifact_urls(root):
    files = sorted((root / BATCHES).glob("*.md"))[-5:] + [root / "CLAUDE.md"]
    seen = []
    for f in files:
        for url in ARTIFACT.findall(_read(f)):
            if url not in seen:
                seen.append(url)
    return seen


def _env_lines(root):
    return _read(root / ".env").splitlines()


def gemini_key_set(root):
    return any(GEMINI_SET.match(line) for line in _env_lines(root))


def _env_values(root):
    values = []
    for line in _env_lines(root):
        if line.lstrip().startswith("#"):
            continue
        m = ENV_LINE.match(line)
        if not m:
            continue
        v = m.group(2).strip().strip("'\"").strip()
        if len(v) >= MIN_SECRET:
            values.append(v)
    return sorted(set(values), key=len, reverse=True)


def gemini_summary(root):
    """`scripts/gemini_log.py summary`, imported as a module, or None when it is absent."""
    mod_path = root / "scripts/gemini_log.py"
    if not mod_path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("_handoff_gemini_log", mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.render(mod.summary(root / GEMINI_LOG))
    except Exception as exc:  # report, never guess
        return "Gemini usage: NOT FETCHED — gemini_log.py failed (%s)" % type(exc).__name__


def scrub(text, root):
    for v in _env_values(root):
        text = text.replace(v, REDACTED)
    return KEY_SHAPE.sub(REDACTED, text)


def current_branch(root):
    return _git(root, "rev-parse", "--abbrev-ref", "HEAD") or "NOT FETCHED — not a git repo"


def build(root=ROOT, branch=None):
    root = pathlib.Path(root).resolve()
    branch = branch or current_branch(root)
    sha = _git(root, "rev-parse", "--short", "HEAD") or "NOT FETCHED — no commit"
    status = _git(root, "status", "--porcelain")
    state = "clean" if not status else "dirty (%d changed paths)" % len(status.splitlines())
    log = _git(root, "log", "--oneline", "-10").splitlines()

    L = ["# Session handoff — BlueStaffyUK", "",
         "Continue this project in a new chat. Everything below was read from the repo by "
         "`python3 scripts/session_handoff.py`; nothing is from memory.", "",
         "## Where", "",
         "- Worktree: `%s`" % root,
         "- Branch: `%s`" % branch,
         "- HEAD: `%s`" % sha,
         "- git status: %s" % state, "",
         "## Last 10 commits", ""]
    L += ["- %s" % c for c in log] or ["- NOT FETCHED — no commits"]

    L += ["", "## Newest session brief", ""]
    brief = newest_brief(root)
    if brief is None:
        L.append("NOT FETCHED — no `*-session-brief.md` in `%s`" % SESSIONS)
    else:
        text = _read(brief)
        L.append("`%s`" % brief.relative_to(root).as_posix())
        flags = [l for l in _section(text, "Open Flags") if l.lstrip().startswith("- ")]
        L += ["", "### Open Flags", ""] + (flags or ["(none)"])
        nxt = [l for l in _section(text, "What's Next") if l.strip()]
        L += ["", "### What's Next", ""]
        L += nxt or ["(empty — run the session-closer skill to fill it)"]

    L += ["", "## Plan", ""]
    plan = newest_plan(root)
    if plan is None:
        L.append("NOT FETCHED — no dated plan in `%s`" % PLANS)
    else:
        L.append("- Newest plan: `%s`" % plan.relative_to(root).as_posix())
        task = first_open_task(_read(plan))
        L.append("- First task with an unchecked step: %s"
                 % (task if task else "none — every step is checked"))
        L.append("- The plan's checkboxes are ticked by hand and can lag the commits: "
                 "compare this task with the commit log above before starting it.")

    L += ["", "## Boards and Artifacts", ""]
    urls = artifact_urls(root)
    L += ["- %s" % u for u in urls] or ["- none found"]

    L += ["", "## Standing instructions", ""] + ["- %s" % s for s in STANDING]

    L += ["", "## Gemini", ""]
    L.append("- " + (GEMINI_LINE if gemini_key_set(root) else "GEMINI_API_KEY is not set in .env"))
    g = gemini_summary(root)
    if g:
        L.append("- " + g)

    return scrub("\n".join(L) + "\n", root)


def main(argv=None, root=ROOT, today=None):
    ap = argparse.ArgumentParser(description="Print a paste-ready new-chat handoff prompt.")
    ap.add_argument("--write", action="store_true",
                    help="also save it to %s/<YYYY-MM-DD>-<branch>.md" % HANDOFF)
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)
    root = pathlib.Path(root).resolve()
    branch = current_branch(root)
    out = build(root, branch)
    print(out, end="")
    if args.write:
        today = today or datetime.date.today().isoformat()
        safe = re.sub(r"[^A-Za-z0-9._-]+", "-", branch)
        dest = root / HANDOFF / ("%s-%s.md" % (today, safe))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
        print("\nwrote %s" % dest.relative_to(root).as_posix(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
