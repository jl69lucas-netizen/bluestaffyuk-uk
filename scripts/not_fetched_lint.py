#!/usr/bin/env python3
"""not_fetched_lint.py — a NOT FETCHED names its barrier (audit rows 1f.2 and 5d).

Parity build, Task 21. A bare `NOT FETCHED` cannot be compared against a later run: nobody
knows what to try next. So in the research a page is built from — data/boards/*.json,
data/queries/**/*.json, data/research-boards/*.json, data/outlines/*.json,
data/city-places/*.json (a city's sourced places, from 2026-10-03) and
docs/research/**/*.{md,json} — every NOT FETCHED is written

  text   NOT FETCHED — <barrier>      (an en dash, a colon or an opening bracket also count;
                                       backticks or bold around the token are fine; in a
                                       markdown table, `| NOT FETCHED | <barrier> |` — the
                                       next cell names it)
  JSON   "NOT FETCHED — <barrier>", or "NOT FETCHED" with a "reason" or "barrier" string
         beside it in the same object. A "reason"/"barrier" value is never linted itself:
         it may quote the token ("left NOT FETCHED by the controller").

A barrier is real: at least two words or eight word characters, and not wholly a
placeholder (todo, tbd, n/a, na, none, unknown, ?, x). "NOT FETCHED — TODO" is still bare.

Quoting the rule in a scoped doc: write it with a real example barrier
(`NOT FETCHED — <what stopped the fetch>`), never the bare token in backticks, or the doc
fails its own check.

Files that already carried a bare one when this check arrived are grandfathered BY CONTENT
HASH in data/quality/not-fetched-baseline.json. Editing such a file ends its exemption:
a changed file is linted like a new one. Never rerun --write-baseline to clear a finding —
name the barrier instead.

Out of scope: gitignored working folders (data/boards/inbox, data/boards/previews,
data/queries/cache) and every other tree.

Stale baseline entries (the file is gone, or it no longer carries a bare token) print a
WARN line and never fail the run; delete them by hand — the baseline only shrinks.

Usage:
  python3 scripts/not_fetched_lint.py [--root DIR]      exit 0 clean · 1 problems · 2 no baseline
  python3 scripts/not_fetched_lint.py --write-baseline  once, when the check is introduced;
                                                        refuses (exit 2) if the file exists
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASELINE = pathlib.Path("data/quality/not-fetched-baseline.json")
SCOPE = (("data/boards", ("*.json",)), ("data/queries", ("**/*.json",)),
         ("data/research-boards", ("*.json",)), ("data/outlines", ("*.json",)),
         ("data/city-places", ("*.json",)),
         ("docs/research", ("**/*.md", "**/*.json")))
IGNORED = ("data/boards/inbox/", "data/boards/previews/", "data/queries/cache/")
TOKEN = re.compile(r"NOT FETCHED")
# After the token: optional closing markup, then a dash, colon or bracket; group 1 = the rest.
NAMED = re.compile(r"[`*_\"']*\s*(?:—|–|:|\()(.*)")
# A markdown table cell holding only the token: the next cell is the barrier.
CELL = re.compile(r"[`*_]*\s*\|([^|]*)")
PLACEHOLDER = re.compile(r"(?:todo|tbd|n/?a|none|unknown|\?|x)", re.I)
REASON_KEYS = ("reason", "barrier")
FIX = ("a bare NOT FETCHED — name the barrier: `NOT FETCHED — <barrier>` (an em dash, "
       "en dash, colon or opening bracket before it; in a table, the next cell; in JSON, "
       'the inline form or a sibling "reason" or "barrier"; at least two words or eight '
       "letters, never a placeholder such as TODO or n/a)")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def real_barrier(s):
    """True when `s` names a barrier someone could act on."""
    if not isinstance(s, str):
        return False
    core = s.strip().strip("`*_\"'()[]{}.,;:—–- ")
    if not core or PLACEHOLDER.fullmatch(core):
        return False
    words = re.findall(r"\w+", core)
    return len(words) >= 2 or sum(map(len, words)) >= 8


def _named(line, start, end):
    m = NAMED.match(line, end)
    if m:
        rest = m.group(1)
        if line[m.start(1) - 1] == "(":
            rest = rest.split(")", 1)[0]
        return real_barrier(rest.split("|", 1)[0].split("NOT FETCHED", 1)[0])
    before = line[:start].rstrip().rstrip("`*_").rstrip()
    c = CELL.match(line, end)
    return bool(c and before.endswith("|") and real_barrier(c.group(1)))


def bare_in_text(text):
    """[line number] of every NOT FETCHED not followed by a named barrier."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in TOKEN.finditer(line):
            if not _named(line, m.start(), m.end()):
                out.append(i)
    return out


def bare_in_json(node, path="$", parent=None):
    """[JSON path] of every string value carrying a bare NOT FETCHED. A "reason" or
    "barrier" value is the barrier itself and is never linted."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k in REASON_KEYS:
                continue
            out += bare_in_json(v, f"{path}.{k}", node)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += bare_in_json(v, f"{path}[{i}]", None)
    elif isinstance(node, str) and TOKEN.search(node):
        if bare_in_text(node):
            sibling = parent is not None and node.strip() == "NOT FETCHED" and any(
                real_barrier(parent.get(k)) for k in REASON_KEYS)
            if not sibling:
                out.append(path)
    return out


def scoped_files(root):
    root = pathlib.Path(root)
    seen = set()
    for base, patterns in SCOPE:
        for pat in patterns:
            for p in sorted((root / base).glob(pat)):
                rel = p.relative_to(root).as_posix()
                if p.is_file() and not rel.startswith(IGNORED) and rel not in seen:
                    seen.add(rel)
                    yield rel, p


def problems_in(rel, path):
    """[problem line] for one file, empty when every NOT FETCHED names its barrier."""
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    if "NOT FETCHED" not in text:
        return []
    if rel.endswith(".json"):
        try:
            where = bare_in_json(json.loads(text))
        except ValueError:
            return [f"{rel}  not valid JSON — cannot tell which NOT FETCHED names a barrier"]
        return [f"{rel}:{w}  {FIX}" for w in where]
    return [f"{rel}:{n}  {FIX}" for n in bare_in_text(text)]


def load_baseline(root):
    p = pathlib.Path(root) / BASELINE
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8")).get("files", {})


def lint(root=ROOT):
    """(problems, files examined, files grandfathered). Raises FileNotFoundError without a
    baseline: a check with nothing to compare against has not passed."""
    base = load_baseline(root)
    if base is None:
        raise FileNotFoundError(str(BASELINE))
    probs, examined, kept = [], 0, 0
    for rel, path in scoped_files(root):
        examined += 1
        found = problems_in(rel, path)
        if found and base.get(rel) == sha(path.read_bytes()):
            kept += 1
            continue
        probs += found
    return probs, examined, kept


def stale_entries(root=ROOT):
    """Baseline entries whose file is gone or no longer carries a bare token."""
    base = load_baseline(root) or {}
    out = []
    for rel in sorted(base):
        path = pathlib.Path(root) / rel
        if not path.is_file() or not problems_in(rel, path):
            out.append(rel)
    return out


def write_baseline(root):
    files = {}
    for rel, path in scoped_files(root):
        if problems_in(rel, path):
            files[rel] = sha(path.read_bytes())
    out = pathlib.Path(root) / BASELINE
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "_comment": "Files that carried a bare NOT FETCHED when scripts/not_fetched_lint.py "
                    "arrived (parity build Task 21), by sha256 of their content. An entry "
                    "exempts that exact content only: edit the file and it is linted like a "
                    "new one. Never regenerate this file to clear a finding.",
        "files": files}, indent=2) + "\n", encoding="utf-8")
    return len(files)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--write-baseline", action="store_true")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root)
    if a.write_baseline:
        if (root / BASELINE).exists():
            print(f"not-fetched-lint: {BASELINE} exists — it is written once, never regenerated",
                  file=sys.stderr)
            return 2
        n = write_baseline(root)
        print(f"not-fetched-lint: wrote {BASELINE} — {n} files grandfathered")
        return 0
    try:
        probs, examined, kept = lint(root)
    except FileNotFoundError:
        print(f"not-fetched-lint: no {BASELINE} — examined nothing, not a pass")
        return 2
    for p in probs:
        print(f"  {p}")
    stale = stale_entries(root)
    if stale:
        print(f"not-fetched-lint: WARN: {len(stale)} stale baseline entries (file gone or now "
              f"clean) — delete them from {BASELINE}: {', '.join(stale)}")
    print(f"not-fetched-lint: examined {examined} files ({kept} grandfathered); "
          f"{len(probs)} problems")
    if not examined:
        # tests/py/test_gates_refuse_nothing.py: no board, query or research file was read.
        print("not-fetched-lint: examined 0 files — not a pass")
        return 1
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
