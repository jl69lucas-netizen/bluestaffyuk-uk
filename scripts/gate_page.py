#!/usr/bin/env python3
"""gate_page.py <slug> — every page gate for one page, run twice, the two runs diffed.

`npm run gate:page -- <slug>`. One command per page instead of seven, and the brief's rule
that one clean run proves nothing (rules/gates.md `run-every-gate-twice`): the same input has
produced different verdicts, so every step runs twice and a step that answers differently the
second time fails the page as surely as a step that fails.

Steps, in order, each with --fail-on-error where the audit takes it (evidence only on a new
page: a migrated or frozen page carries expected WARNs, and an unledgered claim is an ERROR
only on a new page):
  dup-body          scripts/dup_content_audit.py over the whole built site; the page fails on
                    any duplicated passage that names it (a pair of two other pages is theirs)
  dup-headers       the same with --headers: any crossover heading that names the page
  final-audit       scripts/final_page_audit.py <route> --type <profile>
  hardening         scripts/page_hardening_scan.py <route>
  aeo               scripts/aeo_audit.py <route>
  evidence          scripts/evidence_audit.py <route> --type <profile>
  page-run-record   data/page-runs/<slug>.json holds the session open and the impeccable,
                    frontend-design and verification-before-completion passes, current
                    (scripts/page_run_record.py; the twelve frozen pages are exempt)
  check-all         the full gate only: `npm run -s check:all`, run ONCE and judged by its own
                    exit code. The exit codes a verification record holds are informational;
                    the gate re-verifies rather than trusting them.

Before any step, the built page's file must be newer than every one of the page's source
files on disk (data/locations.json included for a city); an older dist/ fails the gate with
"rebuild first" (npm run -s build). File times, not commit times.
An audit that runs past 600 s is a failed step with exit 124; the last 20 lines of a step's
stderr are kept in the report beside its evidence (never inside the diffed evidence).

`<slug>` is the page's key (a city's bare slug); the audits get its route (uk-locations/<slug>).
The profile is --type, else the board's meta.page_type, else `location` for a city.

  python3 scripts/gate_page.py <slug> [--type PROFILE] [--skip-record] [--json PATH]

--skip-record leaves out the page-run-record and check-all steps. It is the form the verification pass runs
and records, because the full gate cannot pass before that record exists.
--json PATH moves the report from docs/reports/gate-page/<slug>.json. The report records
`head`: the commit the gates ran on (`git rev-parse HEAD`, `-dirty` when the tree had
uncommitted changes), and `page_hash`: scripts/rendered_changes.py content_hash of the built
dist/<route>/index.html it judged, so scripts/measurement_ledger.py can refuse a report from
another commit or for another build of the page. Gate a page after committing it.

Exit 0 when every step passes in both runs and the runs agree; 1 on any FAIL or any
difference; 2 on a bad invocation (a slug no data file knows, no built page, no profile).
"""
import argparse
import functools
import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import evidence_audit  # noqa: E402
import family_rules as FR  # noqa: E402
import final_page_audit  # noqa: E402
import page_intake as PI  # noqa: E402
import page_run_record as PRR  # noqa: E402
import rendered_changes as RC  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports" / "gate-page"
RUNS = 2
PROFILES = sorted(set(final_page_audit.PROFILES) & set(evidence_audit.PAGE_TYPES))
AUDIT_STEPS = ("dup-body", "dup-headers", "final-audit", "hardening", "aeo", "evidence")
RECORD_STEP = "page-run-record"
CHECK_ALL_STEP = "check-all"
AUDIT_TIMEOUT = 600      # seconds per audit run; past it the step fails with exit 124
CHECK_ALL_TIMEOUT = 1800
TAIL = 20                # stderr lines kept per step and run


def tail(text, n=TAIL):
    """The last n non-empty lines of a stream."""
    if isinstance(text, bytes):
        text = text.decode("utf-8", "replace")
    return [l for l in (text or "").splitlines() if l.strip()][-n:]


def argv_for(step, route, profile, out, new=True):
    """The command a step runs, writing its JSON to `out`. `new`: the page is a project 5
    page (scripts/family_rules.py is_new_page), so the evidence audit fails on WARN too."""
    s = str(ROOT / "scripts") + "/"
    return {
        "dup-body": [s + "dup_content_audit.py", "--json", out],
        "dup-headers": [s + "dup_content_audit.py", "--headers", "--json", out],
        "final-audit": [s + "final_page_audit.py", route, "--type", profile,
                        "--fail-on-error", "--json", out],
        "hardening": [s + "page_hardening_scan.py", route, "--fail-on-error", "--json", out],
        "aeo": [s + "aeo_audit.py", route, "--fail-on-error", "--json", out],
        "evidence": [s + "evidence_audit.py", route, "--type", profile]
                    + (["--fail-on-error"] if new else []) + ["--json", out],
    }[step]


def run_audit(step, route, profile, new=True):
    """(exit code, JSON payload or None, stderr tail) for one audit step, run from the repo
    root. A run past AUDIT_TIMEOUT is exit 124 with no payload."""
    with tempfile.TemporaryDirectory() as tmp:
        out = str(pathlib.Path(tmp) / "out.json")
        try:
            p = subprocess.run([sys.executable] + argv_for(step, route, profile, out, new),
                               cwd=str(ROOT), capture_output=True, text=True,
                               timeout=AUDIT_TIMEOUT)
        except subprocess.TimeoutExpired as e:
            return 124, None, tail(e.stderr, TAIL - 1) + [f"timed out after {AUDIT_TIMEOUT} s"]
        try:
            payload = json.loads(pathlib.Path(out).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = None
    return p.returncode, payload, tail(p.stderr)


def run_check_all(root=ROOT):
    """(exit code, stderr+stdout tail) of `npm run -s check:all`, run once."""
    try:
        p = subprocess.run(["npm", "run", "-s", "check:all"], cwd=str(root), capture_output=True,
                           text=True, timeout=CHECK_ALL_TIMEOUT)
    except subprocess.TimeoutExpired as e:
        return 124, tail(e.stderr, TAIL - 1) + [f"timed out after {CHECK_ALL_TIMEOUT} s"]
    return p.returncode, tail(p.stderr + "\n" + p.stdout)


def git_head(root=ROOT):
    """HEAD's sha, plus `-dirty` when the work tree has uncommitted changes; None outside a
    git work tree. Stamped on the report so a reader can tell which commit it judged."""
    try:
        p = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                           text=True, timeout=60)
        sha = p.stdout.strip()
        if p.returncode != 0 or not sha:
            return None
        s = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return sha + "-dirty" if s.returncode != 0 or s.stdout.strip() else sha


def page_hash(route, root=ROOT):
    """rendered_changes.content_hash of the built page, or None when it is not built."""
    root = pathlib.Path(root)
    built = root / "dist" / route / "index.html" if route else root / "dist" / "index.html"
    if not built.is_file():
        return None
    return RC.content_hash(built.read_text(encoding="utf-8", errors="replace"))


def stale_build(key, route, root=ROOT):
    """A message when the built page is older than any of the page's sources on disk — its
    board, facts and verbatim files, route files (a folder counts by its files) and, for a
    city, data/locations.json; None when the build is current. File times, not commit times:
    edit, build, then commit is current; an edit after the build is not."""
    root = pathlib.Path(root)
    built = root / "dist" / route / "index.html" if route else root / "dist" / "index.html"
    if not built.is_file():
        return None
    files = []
    for rel in PRR.page_sources(key, root):
        path = root / rel
        files += [f for f in path.rglob("*") if f.is_file()] if path.is_dir() else [path]
    if PRR.city_row(key, root) is not None:
        files.append(root / "data" / "locations.json")
    newer = sorted(f.relative_to(root).as_posix() for f in files
                   if f.stat().st_mtime > built.stat().st_mtime)
    if newer:
        return (f"{built.relative_to(root)} is older than {', '.join(newer)} — rebuild first "
                "(npm run -s build)")
    return None


def judge(step, code, payload, page):
    """(ok, problems, evidence) — `evidence` is what the two runs are diffed on."""
    if payload is None:
        return False, 1, {"error": f"exit {code} and no JSON report"}
    if step == "dup-body":
        mine = sorted((f for f in payload.get("findings", []) if page in (f.get("a"), f.get("b"))),
                      key=lambda f: (f.get("a"), f.get("b"), f.get("run")))
        return not mine, len(mine), {"pages": payload.get("pages"), "findings": mine}
    if step == "dup-headers":
        mine = sorted((f for f in payload.get("findings", []) if page in f.get("pages", [])),
                      key=lambda f: (f.get("kind"), f.get("text")))
        return not mine, len(mine), {"pages": payload.get("pages"), "findings": mine}
    rows = [r for pg in payload.get("pages", []) for r in (pg.get("checks") or pg.get("findings") or [])]
    problems = sum(1 for r in rows if str(r.get("severity", "")).upper() in ("FAIL", "ERROR", "WARN"))
    return code == 0, problems, {"exit": code, "payload": payload}


def one_run(key, route, profile, runner, record, root):
    page = route or "index"
    steps = []
    for step in AUDIT_STEPS:
        code, payload, *rest = runner(step, route, profile)
        ok, problems, evidence = judge(step, code, payload, page)
        steps.append({"step": step, "ok": ok, "problems": problems, "evidence": evidence,
                      "stderr": rest[0] if rest else []})
    if record:
        # The record step reads git and one file; its second run cannot flake the way an audit
        # can, but it runs in both so every step has the same two-run shape — and a record
        # rewritten between the runs (a concurrent writer) shows up as a difference.
        try:
            found = PRR.findings(key, root)
        except PRR.RecordError as e:  # no git history, say: a failed step, not a traceback
            found = [f"page-run record could not be checked: {e}"]
        steps.append({"step": RECORD_STEP, "ok": not found, "problems": len(found),
                      "evidence": {"findings": found}, "stderr": []})
    return steps


def gate(key, route, profile, runs=RUNS, runner=None, record=True, root=ROOT, check_all=None,
         head=None):
    """The report: both runs, per-step agreement, and the verdict. `runner(step, route,
    profile)` -> (exit, payload[, stderr tail]) defaults to the real audits; `check_all(root)`
    -> (exit, tail) to the real `npm run -s check:all`, which only the full gate (record=True)
    runs, once. `head` defaults to git_head(root) and `page_hash` is the built page's, both
    read before the first run."""
    head = git_head(root) if head is None else head
    built_hash = page_hash(route, root)
    if runner is None:
        runner = functools.partial(run_audit, new=FR.is_new_page(key))
    all_runs = [one_run(key, route, profile, runner, record, root) for _ in range(runs)]
    steps = []
    for i, first in enumerate(all_runs[0]):
        mine = [r[i] for r in all_runs]
        same = all(json.dumps(m["evidence"], sort_keys=True) == json.dumps(first["evidence"], sort_keys=True)
                   and m["ok"] == first["ok"] for m in mine)
        steps.append({"step": first["step"], "ok": [m["ok"] for m in mine],
                      "problems": [m["problems"] for m in mine], "identical": same,
                      "stderr": [m["stderr"] for m in mine]})
    if record:
        code, ca_tail = (check_all or run_check_all)(root)
        steps.append({"step": CHECK_ALL_STEP, "ok": [code == 0], "problems": [int(code != 0)],
                      "identical": True, "exit": code, "stderr": [ca_tail]})
    verdict = "PASS" if all(all(s["ok"]) and s["identical"] for s in steps) else "FAIL"
    return {"slug": key, "route": route, "page_type": profile, "head": head,
            "page_hash": built_hash, "runs": runs,
            "record_checked": record, "steps": steps,
            "identical": all(s["identical"] for s in steps), "verdict": verdict,
            "evidence": [[{"step": s["step"], "evidence": s["evidence"]} for s in r] for r in all_runs]}


def resolve(slug, page_type=None, root=ROOT):
    """(key, route, profile) or raise PI.UnknownSlug / ValueError."""
    it = PI.intake(slug, root)
    profile = page_type or it["page_type"]
    if profile not in PROFILES:
        raise ValueError(f"no audit profile for {slug!r} (got {profile!r}); pass --type, one of "
                         + ", ".join(PROFILES))
    if it["built"] is None:
        raise ValueError(f"/{it['route']}/ is not built — run npm run build first")
    return it["slug"], it["route"], profile


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gate_page.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--type", dest="page_type", choices=PROFILES)
    ap.add_argument("--skip-record", action="store_true",
                    help="leave out the page-run-record step (the form verification records)")
    ap.add_argument("--json", metavar="PATH", help="where to write the report")
    ns = ap.parse_args(argv)
    try:
        key, route, profile = resolve(ns.slug, ns.page_type)
    except (PI.UnknownSlug, ValueError) as e:
        print(f"gate-page ERROR {e}")
        return 2
    stale = stale_build(key, route)
    if stale:
        print(f"gate-page FAIL {stale}")
        return 1
    report = gate(key, route, profile, record=not ns.skip_record)
    out = pathlib.Path(ns.json) if ns.json else REPORTS / (key.replace("/", "--") + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gate:page /{route}/ — profile {profile}, {report['runs']} runs")
    for s in report["steps"]:
        state = "PASS" if all(s["ok"]) and s["identical"] else (
            "UNSTABLE" if not s["identical"] else "FAIL")
        print(f"  {state:<8} {s['step']:<16} problems per run {s['problems']}")
    twice = [x for x in report["steps"] if x["step"] != CHECK_ALL_STEP]
    once = " + check-all once" if len(twice) < len(report["steps"]) else ""
    print(f"{report['verdict']} — {len(twice)} steps x {report['runs']} runs{once}; runs identical: "
          f"{report['identical']}; report {out}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
