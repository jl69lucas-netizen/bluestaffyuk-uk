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
      --run "npm run -s check:all" --run "npm run gate:page -- <slug> --skip-record" \\
      --claim "the page passes every gate twice"

`verification` RUNS each `--run` command itself and records its exit code and the first
`examined N` its output prints, so the record is evidence rather than a claim about evidence.

Check a page (what the gate reports):  python3 scripts/page_run_record.py <slug> --check

The gate fails a page when: the record is missing or breaks the schema (a `session_open` whose
skills are out of order breaks it); a pass or the `session_open` key is missing; a Harden pass
lacks one of 375 / 768 / 1280 or leaves a finding neither fixed nor deferred (a visual change
that waits for the breeder is `--deferred "<reason>"`); a verification command exited
non-zero, or `npm run -s check:all` or the page's own `npm run gate:page -- <slug>` run is not
among its commands; the record is stale; or the page's sources have uncommitted changes.

Freshness is the verification pass's: the record is fresh when the
`verification_before_completion` commit is at or after the last commit that changed the
page's own sources (`git merge-base --is-ancestor`). Each Harden pass's commit must be at or
before the verification commit, so a Harden fix committed after the impeccable pass does not
stale it — the verification run that follows covers the fix. The twelve pages built before
these rules (scripts/family_rules.py BUILT_BEFORE_SYSTEM_GAPS) are exempt.

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


class RecordError(Exception):
    pass


def record_path(key, root=ROOT):
    return pathlib.Path(root) / "data" / "page-runs" / (key.replace("/", "--") + ".json")


def page_sources(key, root=ROOT):
    """The files that are this page's own source, relative to root: its board record, its
    src/pages/<route> file or folder, the `[...]` route files of a nested page's parent (a
    city page is rendered by src/pages/uk-locations/[slug].astro — Known Issue 63) and a blog
    post's content file. The shared kit and data/*.json are deliberately not here: an edit
    to them would stale every page's record at once."""
    root = pathlib.Path(root)
    _, route = resolve_page(key, root)
    cands = [root / "data" / "boards" / (key.replace("/", "--") + ".json"),
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


def dirty_sources(key, root=ROOT):
    srcs = page_sources(key, root)
    if not srcs:
        return []
    p = _git(root, "status", "--porcelain", "--", *srcs)
    return [l[3:] for l in p.stdout.splitlines() if l.strip()]


def last_source_commit(key, root=ROOT):
    srcs = page_sources(key, root)
    if not srcs:
        return None
    p = _git(root, "log", "-1", "--format=%H", "--", *srcs)
    return p.stdout.strip() or None


def covers(record_commit, last, root=ROOT):
    """True when `last` (the newest commit touching the page's sources) is `record_commit`
    or one of its ancestors — the pass ran on a tree that already held that change."""
    if last is None:
        return True
    return _git(root, "merge-base", "--is-ancestor", last, record_commit).returncode == 0


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


def findings(key, root=ROOT, schema_path=SCHEMA):
    """[message] — every reason the gate fails this page's record; [] means it passes."""
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
    if SESSION not in record:
        out.append(f"{rel}: the {SESSION} key is missing — record grill-me, "
                   "superpowers:writing-plans and the builder skill (page-run.md row 1)")
    last = last_source_commit(key, root)
    verify = record.get(VERIFY)
    for name in KEYS:
        rec = record.get(name)
        if rec is None:
            out.append(f"{rel}: the {name} pass is missing")
            continue
        if name == VERIFY and not covers(rec["commit"], last, root):
            out.append(f"{rel}: the {name} pass ran at {rec['commit'][:12]}, older than the page's "
                       f"last source change {last[:12]} — run it again")
        if name != VERIFY and verify is not None and not covers(verify["commit"], rec["commit"], root):
            out.append(f"{rel}: the {name} pass ran at {rec['commit'][:12]}, after the verification "
                       f"commit {verify['commit'][:12]} (or on no ancestor of it) — run "
                       "verification-before-completion again")
        if name != VERIFY:
            missing = [w for w in WIDTHS if w not in rec["widths"]]
            if missing:
                out.append(f"{rel}: the {name} pass did not check {missing}")
            if rec["fixed"] + len(rec["deferred"]) != rec["findings"]:
                out.append(f"{rel}: the {name} pass found {rec['findings']} but fixed "
                           f"{rec['fixed']} and deferred {len(rec['deferred'])} — every finding "
                           "is fixed or deferred with its reason")
            continue
        for c in rec["commands"]:
            if c["exit"] != 0:
                out.append(f"{rel}: verification ran `{c['cmd']}` and it exited {c['exit']}")
        cmds = [c["cmd"].strip() for c in rec["commands"]]
        if not any(CHECK_ALL.match(c) for c in cmds):
            out.append(f"{rel}: verification did not run `npm run -s check:all`")
        gate = re.compile(r"^npm run (?:-s |--silent )?gate:page -- " + re.escape(key) + r"(?:\s|$)")
        if not any(gate.match(c) for c in cmds):
            out.append(f"{rel}: verification did not run `npm run gate:page -- {key}`")
    dirty = dirty_sources(key, root)
    if dirty:
        out.append(f"{rel}: the page's sources have uncommitted changes the record cannot "
                   f"cover: {', '.join(dirty)}")
    return out


def run_command(cmd, root=ROOT):
    """{cmd, exit, examined} for one shell command run from the repo root."""
    p = subprocess.run(cmd, shell=True, cwd=str(root), capture_output=True, text=True)
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
