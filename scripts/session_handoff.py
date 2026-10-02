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
learn every value it must never print. It is parsed like a dotenv loader (quotes, multi-line
quoted values, ` #` comments, `export`). The finished prompt has every value of a secret-looking
key (`*_KEY`, `*_TOKEN`, `*_SECRET`, `*_PASSWORD`, `*_ID`, `*_PAT`) from three characters, every other
value of six or more characters, and anything shaped like a key (`AQ.…`, `AIza…`, `sk-…`,
`ghp_…`, `github_pat_…`, `xox[bpa]-…`, `AKIA…`) replaced with `[redacted]`.

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
ENV_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")
SECRET_KEY = re.compile(r"(?:^|_)(?:KEY|TOKEN|SECRET|PASSWORD|ID|PAT)$")
KEY_SHAPE = re.compile(r"AQ\.\S+|AIza\S+|(?<![A-Za-z0-9])sk-\S+|ghp_\S+|github_pat_\S+"
                       r"|xox[bpa]-\S+|AKIA[0-9A-Z]{16}")
TASK = re.compile(r"^###\s+Task\b")
OPEN_STEP = re.compile(r"^\s*- \[ \]")
REDACTED = "[redacted]"
MIN_SECRET = 6
# A secret-looking key's value is redacted from three characters: a one- or two-character
# value (`H_ID=1`) would blank every count, date and sha digit it happens to match.
SHORT_SECRET = 3

STANDING = [
    "Read CLAUDE.md, docs/reference/page-run.md, the newest brief and MEMORY.md first",
    "Watch the answer board and any open page board with ArtifactComments at session start",
    "Commit after every task; never push unless the user explicitly says so (CLAUDE.md rule 3).",
]
GEMINI_LINE = ("GEMINI_API_KEY is set in .env — delete it when image work is done "
               "(breeder's instruction, 2026-10-02)")


def _git(root, *args):
    """git's stdout, or "" when git is missing, times out or fails (callers say NOT FETCHED)."""
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                           timeout=20)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
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
    """The plan with the newest filename date; a tie on the date goes to the newest mtime."""
    plans = [p for p in (root / PLANS).glob("*.md") if re.match(r"\d{4}-\d{2}-\d{2}-", p.name)]
    if not plans:
        return None
    return max(plans, key=lambda p: (p.name[:10], p.stat().st_mtime, p.name))


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


def _close(s, q):
    """Index of the quote `q` that closes a value in `s`, or -1. Inside double quotes a
    backslash escapes the next character, so `\\"` does not close the value."""
    i = 0
    while i < len(s):
        if q == '"' and s[i] == "\\":
            i += 2
            continue
        if s[i] == q:
            return i
        i += 1
    return -1


def parse_env(text):
    """[(key, value)] from .env text, parsed the way a dotenv loader reads it.

    A quoted value (single or double) ends at its closing quote, across lines if it has to,
    so a trailing `# note` is never part of it; an unquoted value ends before ` #`.
    `export KEY=` is accepted. A comment line is skipped.
    """
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = ENV_LINE.match(line)
        if not m:
            continue
        key, rest = m.group(1), m.group(2).lstrip()
        if rest[:1] in ("'", '"'):
            q, body = rest[0], rest[1:]
            close = _close(body, q)
            if close >= 0:
                value = body[:close]
            else:  # multi-line: run to the line that closes the quote (or end of file)
                parts = [body]
                while i < len(lines):
                    nxt = lines[i]
                    i += 1
                    close = _close(nxt, q)
                    if close >= 0:
                        parts.append(nxt[:close])
                        break
                    parts.append(nxt)
                value = "\n".join(parts)
            if q == '"':
                value = value.replace('\\"', '"')
        else:
            value = re.split(r"\s#", rest, maxsplit=1)[0].strip()
        out.append((key, value))
    return out


def _env(root):
    return parse_env(_read(root / ".env"))


def gemini_key_set(root):
    return any(k == "GEMINI_API_KEY" and v.strip() for k, v in _env(root))


def _env_secrets(root):
    """Every string the prompt must not carry: each value (and each line of a multi-line
    value). A key that looks secret is redacted at any length; any other key from MIN_SECRET."""
    secrets = set()
    for key, value in _env(root):
        floor = SHORT_SECRET if SECRET_KEY.search(key.upper()) else MIN_SECRET
        escaped = value.replace('"', '\\"')
        for piece in [value, escaped] + value.splitlines() + escaped.splitlines():
            piece = piece.strip()
            if len(piece) >= floor:
                secrets.add(piece)
    return sorted(secrets, key=len, reverse=True)


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
    for v in _env_secrets(root):
        if len(v) >= MIN_SECRET:
            text = text.replace(v, REDACTED)
        else:  # a short secret is redacted wherever it stands as its own token
            text = re.sub(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(v), REDACTED, text)
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
