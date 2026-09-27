#!/usr/bin/env python3
"""page_run_record.py — the record of a project 5 page's mandatory skill passes.

The user ruled (2026-09-26) that three skills are never skipped on a project 5 page: the
`impeccable:impeccable` and `frontend-design:frontend-design` Harden passes, and
`superpowers:verification-before-completion` before any "page done" claim
(docs/reference/page-run.md rows 14, 15 and 18). A ruling nothing checks is a paragraph, so
each pass leaves a key in `data/page-runs/<slug>.json` (schemas/page-run-record.schema.json)
and `npm run gate:page -- <slug>` fails the page until all three are there and current. A
fourth key, `session_open`, proves row 1 ran: `grill-me`, then `superpowers:writing-plans`,
then the page-type builder skill, in that order.

Record the session open (row 1), once the three skills have run:

  python3 scripts/page_run_record.py <slug> session-open --builder bsuk-location-page-builder

Write a pass (after committing the fixes it produced — the writer refuses while the page's
sources have uncommitted changes, because the record's commit would not contain them):

  python3 scripts/page_run_record.py <slug> impeccable --findings 7 --fixed 6 --deferred "why"
  python3 scripts/page_run_record.py <slug> frontend-design --findings 3 --fixed 3
  python3 scripts/page_run_record.py <slug> verification \\
      --run "npm run -s build" --run "npm run -s check:all" \\
      --run "npm run gate:page -- <slug> --skip-record" --claim "the page passes every gate twice"

`verification` RUNS each `--run` command itself and records its exit code and the first
`examined N` its output prints (a command past 1800 s is exit 124), so the record is evidence
rather than a claim about evidence. It refuses while any tracked file outside data/page-runs/,
docs/reports/, data/quality/scorecards/ and the build's two tracked outputs
(BUILD_OUTPUT_PATHS) has uncommitted changes, because it stamps HEAD. The exit codes it records
are informational: the full `npm run gate:page -- <slug>` re-runs `npm run -s check:all`
itself. A Harden pass is refused for a page with no sources yet.

Check a page (what the gate reports):  python3 scripts/page_run_record.py <slug> --check

The gate fails a page when: the record is missing or breaks the schema (a `session_open` whose
skills are out of order breaks it); a pass or the `session_open` key is missing; a Harden pass
lacks one of 375 / 768 / 1280 or leaves a finding neither fixed nor deferred (a visual change
that waits for the breeder is `--deferred "<reason>"`); the session open is dated after the
impeccable pass; a verification command exited non-zero or examined 0, `npm run -s check:all`
or the page's own `npm run gate:page -- <slug>` run is not among its commands, or
`npm run -s build` did not run before that gate run; the record is stale; the page's sources
have uncommitted changes; or the record itself is not committed.

Freshness. The page's sources are its board, facts and verbatim files, its route file or
folder, its parent's `[...]` route files, a blog post's content file, and a city's own row of
data/locations.json (compared as a row, so another city's edit stales nothing). The record
is fresh when the verification commit is in HEAD's history and
`git diff --quiet <verify> HEAD -- <sources>` is clean (a change a merge brought in counts).
The Harden passes: the impeccable commit is an ancestor of the frontend-design commit, and
the page is unchanged between the frontend-design commit and the verification commit — a fix
committed between the two Harden passes stales nothing; an edit after the frontend-design
pass stales it ("the page changed after the frontend-design pass; re-run it"). The twelve
pages built before these rules (scripts/family_rules.py BUILT_BEFORE_SYSTEM_GAPS) are exempt.

Exit codes: 0 written / clean; 1 --check found problems; 2 bad invocation, dirty sources or
no git history to stamp.
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

import jsonschema

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import family_rules as FR  # noqa: E402
from _slugs import resolve_page  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "page-run-record.schema.json"
WIDTHS = (375, 768, 1280)
HARDEN = {"impeccable": "impeccable", "frontend-design": "frontend_design"}
VERIFY = "verification_before_completion"
SESSION = "session_open"
SESSION_FIRST = ("grill-me", "superpowers:writing-plans")
KEYS = ("impeccable", "frontend_design", VERIFY)
EXAMINED = re.compile(r"\bexamined (\d+)")
CHECK_ALL = re.compile(r"^npm run (?:-s |--silent )?check:all$")
BUILD = re.compile(r"^npm run (?:-s |--silent )?build$")
COMMAND_TIMEOUT = 1800  # seconds; a verification command past it is recorded as exit 124


class RecordError(Exception):
    pass


def record_path(key, root=ROOT):
    return pathlib.Path(root) / "data" / "page-runs" / (key.replace("/", "--") + ".json")


def page_sources(key, root=ROOT):
    """The files that are this page's own source, relative to root: its board record, its
    facts and verbatim files, its src/pages/<route> file or folder, the `[...]` route files of
    a nested page's parent (a city page is rendered by src/pages/uk-locations/[slug].astro —
    Known Issue 63) and a blog post's content file. A city's own row of data/locations.json is
    a source too, compared as a row (city_row), not as the file. The shared kit and the rest of
    data/*.json are deliberately not here: an edit to them would stale every page's record at
    once."""
    root = pathlib.Path(root)
    _, route = resolve_page(key, root)
    stem = key.replace("/", "--") + ".json"
    cands = [root / "data" / "boards" / stem,
             root / "data" / "facts" / stem,
             root / "data" / "verbatim" / stem,
             root / "src" / "pages" / route,
             root / "src" / "pages" / (route + ".astro"),
             root / "src" / "content" / "blog" / (key + ".md"),
             root / "src" / "content" / "blog" / (key + ".mdx")]
    if "/" in route:
        parent = root / "src" / "pages" / route.rsplit("/", 1)[0]
        if parent.is_dir():
            cands += [f for f in sorted(parent.iterdir()) if f.is_file() and f.name.startswith("[")]
    return [c.relative_to(root).as_posix() for c in cands if c.exists()]


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def head_commit(root=ROOT):
    p = _git(root, "rev-parse", "HEAD")
    if p.returncode != 0:
        raise RecordError("no git history to stamp the record with: " + p.stderr.strip())
    return p.stdout.strip()


def city_row(key, root=ROOT, rev=None):
    """This page's own data/locations.json row as canonical JSON — at `rev`, or in the working
    tree when rev is None; None when there is no such row (not a city, or no file)."""
    if rev is None:
        p = pathlib.Path(root) / "data" / "locations.json"
        text = p.read_text(encoding="utf-8") if p.is_file() else None
    else:
        g = _git(root, "show", f"{rev}:data/locations.json")
        text = g.stdout if g.returncode == 0 else None
    try:
        rows = json.loads(text) if text else []
    except json.JSONDecodeError:
        return "unreadable"
    row = next((r for r in rows if isinstance(r, dict) and r.get("slug") == key), None) \
        if isinstance(rows, list) else None
    return json.dumps(row, sort_keys=True) if row is not None else None


def changed_between(key, a, b, root=ROOT):
    """The page's sources that differ between commits a and b (`git diff --quiet a b -- ...`,
    plus its own locations row); [] when the page is the same at both."""
    srcs = page_sources(key, root)
    out = []
    if srcs:
        p = _git(root, "diff", "--name-only", a, b, "--", *srcs)
        if p.returncode != 0:
            return [f"(git diff {a[:12]} {b[:12]} failed: {p.stderr.strip()})"]
        out = [l for l in p.stdout.splitlines() if l.strip()]
    if city_row(key, root, a) != city_row(key, root, b):
        out.append(f"data/locations.json (the {key} row)")
    return out


def is_ancestor(a, b, root=ROOT):
    """True when commit a is b or one of b's ancestors."""
    return _git(root, "merge-base", "--is-ancestor", a, b).returncode == 0


def dirty_sources(key, root=ROOT):
    srcs = page_sources(key, root)
    out = []
    if srcs:
        p = _git(root, "status", "--porcelain", "--", *srcs)
        out = [l[3:] for l in p.stdout.splitlines() if l.strip()]
    if _git(root, "rev-parse", "--verify", "-q", "HEAD").returncode == 0 and \
            city_row(key, root, "HEAD") != city_row(key, root):
        out.append(f"data/locations.json (the {key} row)")
    return out


# Written by the run itself, not page changes. data/quality/scorecards/ is here because
# scripts/build_scorecard.mjs names a card <slug>-<run date>.json: a second render run on the
# day a card was committed rewrites that TRACKED file (a new day adds an untracked one).
MEASUREMENT_PATHS = ("data/page-runs/", "docs/reports/", "data/quality/scorecards/")
#: Tracked files every `npm run build` rewrites (package.json): prebuild's
#: data/page-dates.json is derived from COMMITTED git history of the page files, and postbuild's
#: public/search-index.json from the built dist/. Neither is an input anyone edits, both are
#: reproduced exactly from what is committed, so rewriting them is not a page change. Without
#: this, the close order docs/reference/page-run.md row 21 documents (build, then gate) would
#: stamp every gate report `-dirty` and the ledger would read M8 and M10 as STALE.
BUILD_OUTPUT_PATHS = ("data/page-dates.json", "public/search-index.json")


def dirty_tracked(root=ROOT):
    """Tracked files with uncommitted changes, outside MEASUREMENT_PATHS and
    BUILD_OUTPUT_PATHS. The one definition of a dirty tree: the record writer refuses on it,
    scripts/gate_page.py git_head marks its report `-dirty` on it and
    scripts/rendered_changes.py head_sha stamps its report with it."""
    p = _git(root, "status", "--porcelain", "--untracked-files=no")
    return [l[3:] for l in p.stdout.splitlines() if l.strip()
            and not l[3:].startswith(MEASUREMENT_PATHS + BUILD_OUTPUT_PATHS)]


def load(key, root=ROOT):
    p = record_path(key, root)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def schema_errors(record, schema_path=SCHEMA):
    schema = json.loads(pathlib.Path(schema_path).read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    return sorted("%s: %s" % ("/".join(str(x) for x in e.absolute_path) or "(record)", e.message)
                  for e in v.iter_errors(record))


def _verification_findings(rel, key, rec):
    out = []
    for c in rec["commands"]:
        if c["exit"] != 0:
            out.append(f"{rel}: verification ran `{c['cmd']}` and it exited {c['exit']}")
        if c["examined"] == 0:
            out.append(f"{rel}: verification ran `{c['cmd']}` and it examined 0 — a gate that "
                       "examined nothing proved nothing")
    cmds = [c["cmd"].strip() for c in rec["commands"]]
    if not any(CHECK_ALL.match(c) for c in cmds):
        out.append(f"{rel}: verification did not run `npm run -s check:all`")
    gate = re.compile(r"^npm run (?:-s |--silent )?gate:page -- " + re.escape(key) + r"(?:\s|$)")
    gates = [i for i, c in enumerate(cmds) if gate.match(c)]
    if not gates:
        out.append(f"{rel}: verification did not run `npm run gate:page -- {key}`")
    elif not any(BUILD.match(c) for c in cmds[:gates[0]]):
        out.append(f"{rel}: verification did not run `npm run -s build` before "
                   f"`npm run gate:page -- {key}` — the gate read a stale dist/")
    return out


def findings(key, root=ROOT, schema_path=SCHEMA):
    """[message] — every reason the gate fails this page's record; [] means it passes.

    Freshness: the verification commit is in HEAD's history and the page (its sources and
    its own locations row) is the same at that commit and at HEAD. The Harden passes: the
    impeccable commit is an ancestor of the frontend-design commit, and the page is the same
    at the frontend-design commit and at the verification commit — so a fix committed between
    the two Harden passes stales nothing, and an edit after frontend-design stales that pass."""
    root = pathlib.Path(root)
    if not FR.is_new_page(key):
        return []
    rel = record_path(key, root).relative_to(root).as_posix()
    record = load(key, root)
    if record is None:
        return [f"no {rel} — record the session open, the impeccable and frontend-design passes "
                "and verification-before-completion (docs/reference/page-run.md rows 1, 14, 15, 18)"]
    out = [f"{rel} breaks the schema at {e}" for e in schema_errors(record, schema_path)]
    if out:
        return out
    session = record.get(SESSION)
    if session is None:
        out.append(f"{rel}: the {SESSION} key is missing — record grill-me, "
                   "superpowers:writing-plans and the builder skill (page-run.md row 1)")
    for name in KEYS:
        if name not in record:
            out.append(f"{rel}: the {name} pass is missing")
    imp, fd, ver = (record.get(k) for k in KEYS)
    if session and imp and session["ran_on"] > imp["ran_on"]:
        out.append(f"{rel}: the {SESSION} ran on {session['ran_on']}, after the impeccable pass "
                   f"({imp['ran_on']}) — the session opens before the page is hardened")
    for name, rec in (("impeccable", imp), ("frontend_design", fd)):
        if rec is None:
            continue
        missing = [w for w in WIDTHS if w not in rec["widths"]]
        if missing:
            out.append(f"{rel}: the {name} pass did not check {missing}")
        if rec["fixed"] + len(rec["deferred"]) != rec["findings"]:
            out.append(f"{rel}: the {name} pass found {rec['findings']} but fixed "
                       f"{rec['fixed']} and deferred {len(rec['deferred'])} — every finding "
                       "is fixed or deferred with its reason")
    if imp and fd and not is_ancestor(imp["commit"], fd["commit"], root):
        out.append(f"{rel}: the impeccable pass ran at {imp['commit'][:12]}, after the "
                   f"frontend-design pass {fd['commit'][:12]} (or off its history) — impeccable "
                   "runs first; run frontend-design and verification again")
    if ver is not None:
        head = head_commit(root)
        if not is_ancestor(ver["commit"], head, root):
            out.append(f"{rel}: the {VERIFY} pass ran at {ver['commit'][:12]}, which is not in "
                       "HEAD's history — run it again")
        else:
            changed = changed_between(key, ver["commit"], head, root)
            if changed:
                out.append(f"{rel}: the {VERIFY} pass ran at {ver['commit'][:12]}, older than the "
                           f"page's last source change (changed since: {', '.join(changed)}) — "
                           "run it again")
        if fd is not None:
            changed = changed_between(key, fd["commit"], ver["commit"], root)
            if changed:
                out.append(f"{rel}: the page changed after the frontend-design pass; re-run it "
                           f"(changed: {', '.join(changed)})")
        out += _verification_findings(rel, key, ver)
    dirty = dirty_sources(key, root)
    if dirty:
        out.append(f"{rel}: the page's sources have uncommitted changes the record cannot "
                   f"cover: {', '.join(dirty)}")
    if _git(root, "status", "--porcelain", "--", rel).stdout.strip():
        out.append(f"{rel}: commit {rel} — an uncommitted record is not evidence")
    return out


def run_command(cmd, root=ROOT, timeout=COMMAND_TIMEOUT):
    """{cmd, exit, examined} for one shell command run from the repo root; a command that
    runs past `timeout` seconds is recorded as exit 124."""
    try:
        p = subprocess.run(cmd, shell=True, cwd=str(root), capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "exit": 124, "examined": None}
    m = EXAMINED.search(p.stdout + "\n" + p.stderr)
    return {"cmd": cmd, "exit": p.returncode, "examined": int(m.group(1)) if m else None}


def write_pass(key, which, root=ROOT, today=None, **kw):
    """Add or replace one pass in the page's record and return the record."""
    root = pathlib.Path(root)
    ran_on = (today or datetime.date.today()).isoformat()
    if which == "session-open":
        # Row 1 runs before the page has sources to commit: no commit stamp, no clean check.
        record = load(key, root) or {"slug": key}
        record[SESSION] = {"ran_on": ran_on, "skills": [*SESSION_FIRST, kw.get("builder") or ""]}
        return _save(key, record, root)
    dirty = dirty_sources(key, root)
    if dirty:
        raise RecordError("commit the page's sources first — uncommitted: " + ", ".join(dirty))
    commit = head_commit(root)
    record = load(key, root) or {"slug": key}
    if which in HARDEN and not page_sources(key, root):
        raise RecordError(f"{key} has no sources yet (no board, template or content file) — "
                          "build the page before hardening it")
    if which == "verification":
        dirty = dirty_tracked(root)
        if dirty:
            raise RecordError("commit everything first — verification stamps HEAD, and these "
                              "tracked files differ from it: " + ", ".join(dirty))
    if which in HARDEN:
        record[HARDEN[which]] = {"ran_on": ran_on, "widths": list(kw.get("widths") or WIDTHS),
                                 "findings": kw["findings"], "fixed": kw["fixed"],
                                 "deferred": list(kw.get("deferred") or []), "commit": commit}
    elif which == "verification":
        record[VERIFY] = {"ran_on": ran_on, "commit": commit,
                          "commands": [run_command(c, root) for c in kw["run"]],
                          "claims_verified": list(kw["claims"])}
    else:
        raise RecordError(f"unknown pass {which!r}")
    return _save(key, record, root)


def _save(key, record, root):
    errs = schema_errors(record)
    if errs:
        raise RecordError("the record would break its schema: " + "; ".join(errs))
    p = record_path(key, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(prog="page_run_record.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("which", nargs="?", choices=sorted(HARDEN) + ["session-open", "verification"])
    ap.add_argument("--check", action="store_true", help="print what the gate would report")
    ap.add_argument("--findings", type=int)
    ap.add_argument("--fixed", type=int)
    ap.add_argument("--deferred", action="append", default=[], metavar="REASON")
    ap.add_argument("--widths", type=int, nargs="+", default=list(WIDTHS))
    ap.add_argument("--run", action="append", default=[], metavar="CMD")
    ap.add_argument("--claim", action="append", default=[], metavar="TEXT")
    ap.add_argument("--builder", metavar="SKILL",
                    help="session-open: the page-type builder skill that ran after writing-plans")
    ns = ap.parse_args(argv)
    try:
        key, _ = resolve_page(ns.slug, root)
    except ValueError as e:
        print(f"page-run-record ERROR {e}")
        return 2
    if ns.check:
        probs = findings(key, root)
        for p in probs:
            print(f"  FAIL {p}")
        print(f"page-run-record: {key} — {len(probs)} problem(s)")
        return 1 if probs else 0
    if ns.which is None:
        ap.error("name a pass (session-open, impeccable, frontend-design, verification) or "
                 "pass --check")
    if ns.which == "session-open" and not ns.builder:
        ap.error("session-open needs --builder <the page-type builder skill>")
    if ns.which in HARDEN and (ns.findings is None or ns.fixed is None):
        ap.error(f"{ns.which} needs --findings and --fixed")
    if ns.which == "verification" and (not ns.run or not ns.claim):
        ap.error("verification needs at least one --run and one --claim")
    try:
        rec = write_pass(key, ns.which, root, findings=ns.findings, fixed=ns.fixed,
                         deferred=ns.deferred, widths=ns.widths, run=ns.run, claims=ns.claim,
                         builder=ns.builder)
    except RecordError as e:
        print(f"page-run-record ERROR {e}")
        return 2
    rel = record_path(key, root).relative_to(root)
    if ns.which == "session-open":
        print(f"wrote {rel} — {SESSION}: {' -> '.join(rec[SESSION]['skills'])}")
        return 0
    name = HARDEN.get(ns.which, VERIFY)
    print(f"wrote {rel} — {name} at {rec[name]['commit'][:12]}")
    if name == VERIFY:
        for c in rec[name]["commands"]:
            print(f"  exit {c['exit']}  examined {c['examined']}  {c['cmd']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
