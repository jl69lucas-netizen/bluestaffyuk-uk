#!/usr/bin/env python3
"""measurement_ledger.py <project> [--slugs S ...] [--md PATH] [--require-pages] — the numbers a close reports.

The page-build brief's measurement ledger (§20) is a list of numbers that must appear in the
close-out, not boxes that get ticked. BlueStaffyUK had the data for most of them — the
scorecards, the render checks' own declarations, the rule index, the gate:page reports — and
no step that printed them together. This one reads them and prints the rows it can compute:

  M1   nodes examined per check on real pages, > 0         each page's newest scorecard
  M2   families registered vs families wired, difference ∅  tests/render/checks + targets.json
  M3   advisory vs blocking rows, reported separately       each page's newest scorecard
  M6   minimum rendered text >= 12.5px on the pages          layout-min-font-size, per page
  M8   gate runs per page >= 2, both clean                   docs/reports/gate-page/<slug>.json
  M9   rework: page vs harness, never merged                 data/quality/rework-ledger.json
  M10  dup crossover, body and headers, = 0                  the gate:page reports
  M12  LLM visibility cells fetched / total                  docs/research/llm-intel/<key>-<date>.json
  M13  slugs whose rendered output changed                   docs/reports/rendered-changes.json
  M18  untested rules in the rule index                      data/quality/rule-index.json

The pages are --slugs, else every page in data/facts/rebuilt.json that scripts/family_rules.py
is_new_page counts as a project 5 page (not one of the twelve frozen pages, not a `_` fixture).

Nothing measured is never a pass. A project-scope row with no page in scope reads EMPTY and is
listed under `empty`; --require-pages makes an empty scope, or any EMPTY row, exit 1.

An input that judged another build or another commit is STALE, not evidence. Only four rows
can be STALE:
  M6   a scorecard file older than the built page. File times: the scorecards are written by
       scripts/build_scorecard.mjs and carry no page hash, so a fresh checkout (which resets
       times) reads current until the next render run.
  M8   a gate:page report gated on a dirty tree; or whose `head` is not HEAD or an ancestor of
       it; or whose page's sources (and, for a city, its data/locations.json row) changed
       between that head and HEAD (scripts/page_run_record.py is_ancestor, changed_between);
       or whose `page_hash` is not the rendered_changes.py content_hash of today's built page.
       The page's own gate stays good across commits that do not touch the page.
  M10  the same report, strictly: gated on a dirty tree, `head` not HEAD itself, or the page
       hash differs. Dup crossover is site-wide — any other page's edit can create one — so
       only a gate at the final commit counts, and the close re-gates at that commit.
  M13  a rendered-changes.json written for another commit (reported, not failed).
The close order that keeps every input current, in docs/reference/page-run.md row 21:
build, test:render:pages, gate:page per page, rendered_changes.py --json, this ledger with
--require-pages, then commit — no rebuild after gating.

Scorecards are the newest card of each page tests/render/targets.json still targets (as
tests/render/lib/examined.ts latestCards reads them); a card that does not parse fails M1 by
file name. A number that cannot be read is written `NOT FETCHED — <barrier>`, never guessed;
a malformed input is a named barrier, never a traceback.

Writes docs/reports/<project>-ledger.json and prints the markdown table; --md PATH also writes
the table, under a one-line header (project, date, scope, HEAD, failed, stale, empty), to PATH for the
gate report. <project> is [a-z0-9-]+.

Exit 1 when M1, M2, M6, M8 or M10 is FAIL or STALE (or --require-pages finds nothing in scope);
2 on a bad invocation; 0 otherwise.
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import family_rules as FR  # noqa: E402
import page_run_record as PRR  # noqa: E402
import rendered_changes as RC  # noqa: E402
import render_baseline as RB  # noqa: E402
from _slugs import resolve_page  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
FAILING = ("M1", "M2", "M6", "M8", "M10")
MIN_FONT = "layout-min-font-size"
DUP_STEPS = ("dup-body", "dup-headers")
PROJECT = re.compile(r"[a-z0-9-]+")
DATED = re.compile(r"\d{4}-\d{2}-\d{2}")
SHA = re.compile(r"[0-9a-f]{7,40}")


def _json(path, default=None):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def git_head(root):
    """HEAD's full sha, or None outside a git work tree."""
    try:
        p = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return (p.stdout.strip() or None) if p.returncode == 0 else None


def same_commit(recorded, head):
    """True when `recorded` (a full or >= 7-char sha, `-dirty` allowed) names `head`."""
    if not isinstance(recorded, str) or not head:
        return False
    sha = recorded[:-len("-dirty")] if recorded.endswith("-dirty") else recorded
    return len(sha) >= 7 and head.startswith(sha)


def _checks(root):
    """id -> (family, severity), or {} when no check definition can be read."""
    try:
        return RB.load_checks(root / "tests/render/checks")
    except (SystemExit, OSError):
        return {}


def built_file(root, route):
    rel = pathlib.PurePosixPath("dist", route, "index.html") if route else \
        pathlib.PurePosixPath("dist/index.html")
    return root / rel, rel.as_posix()


def default_slugs(root):
    rows = _json(root / "data/facts/rebuilt.json", []) or []
    return [s for s in rows if isinstance(s, str) and FR.is_new_page(s)] if isinstance(rows, list) else []


def latest_cards(root):
    """(run label, [(path, card)], [unreadable file names]).

    The newest card of each slug, as tests/render/lib/examined.ts latestCards reads them: a
    one-page re-run writes today's card for that page only, and judging today's date alone
    would drop every other page. Only slugs tests/render/targets.json still lists count (when
    it lists pages), so a card for a page no longer targeted cannot pass or fail the run. A card
    that does not parse is returned by name, never skipped. The label is `run <date>`, or
    `runs <oldest> to <newest>` when the cards span dates."""
    cards_dir = root / "data/quality/scorecards"
    if not cards_dir.is_dir():
        return None, [], []
    targets = _json(root / "tests/render/targets.json", {}) or {}
    pages = targets.get("pages") if isinstance(targets, dict) else None
    want = {p.get("slug") for p in pages if isinstance(p, dict)} if isinstance(pages, list) else None
    best, broken = {}, []
    for p in sorted(cards_dir.glob("*.json")):
        date = p.stem[-10:]
        if not DATED.fullmatch(date):
            continue
        card = _json(p)
        if not isinstance(card, dict) or not isinstance(card.get("slug", ""), str) or not \
                isinstance(card.get("examined_by_check", {}), dict) or not \
                isinstance(card.get("details", []), list):
            broken.append(p.name)
            continue
        slug = card.get("slug") or p.stem[:-11]
        if want is not None and slug not in want:
            continue
        if slug not in best or date > best[slug][0]:
            best[slug] = (date, p, card)
    if not best:
        return None, [], broken
    dates = sorted({d for d, _, _ in best.values()})
    label = "run " + dates[0] if len(dates) == 1 else "runs %s to %s" % (dates[0], dates[-1])
    return label, [(best[s][1], best[s][2]) for s in sorted(best)], broken


def row(mid, measurement, value, status, detail=""):
    return {"id": mid, "measurement": measurement, "value": value, "status": status,
            "detail": detail}


def _verdict(hard, stale):
    return "FAIL" if hard else "STALE" if stale else "PASS"


def m1(root, date, cards, broken):
    name = "Nodes examined per check, on real pages"
    unreadable = ["unreadable scorecard " + b for b in broken]
    if not cards:
        return row("M1", name, "NOT FETCHED — no scorecards under data/quality/scorecards "
                   "(run npm run test:render:pages)", "FAIL", "; ".join(unreadable))
    targets = _json(root / "tests/render/targets.json", {}) or {}
    deferred = targets.get("deferred_checks", {}) if isinstance(targets, dict) else {}
    # Registered, non-deferred ids only, as examined.ts examinedTotals counts them.
    registered = sorted(k for k in _checks(root) if k not in deferred)
    examined = {}
    for _, c in cards:
        for check, n in c.get("examined_by_check", {}).items():
            if check in registered and isinstance(n, (int, float)):
                examined[check] = examined.get(check, 0) + n
    zero = sorted(k for k, n in examined.items() if n == 0)
    # examined.ts notYetMeasured: a registered check with no key in any card was registered
    # since the last page run — named, not failed. Measured-zero fails.
    unmeasured = [k for k in registered if k not in examined]
    value = "%d checks, %d at zero%s (%s, %d pages)" % (
        len(registered), len(zero),
        ", %d not yet measured" % len(unmeasured) if unmeasured else "", date, len(cards))
    detail = "; ".join(x for x in (", ".join(zero), "not yet measured: " + ", ".join(unmeasured)
                                   if unmeasured else "", "; ".join(unreadable)) if x)
    return row("M1", name, value, "FAIL" if zero or broken or not registered else "PASS", detail)


def m2(root):
    name = "Families registered vs families wired"
    checks = _checks(root)
    if not checks:
        return row("M2", name, "NOT FETCHED — no check definitions under tests/render/checks",
                   "FAIL")
    registered = {fam for fam, _ in checks.values()}
    targets = _json(root / "tests/render/targets.json", {}) or {}
    by_type = targets.get("families_by_page_type", {}) if isinstance(targets, dict) else {}
    wired = {f for fams in (by_type.values() if isinstance(by_type, dict) else [])
             if isinstance(fams, list) for f in fams}
    diff = sorted(registered ^ wired)
    value = "registered %d · wired %d · difference %s" % (
        len(registered), len(wired), "∅" if not diff else "{" + ", ".join(diff) + "}")
    return row("M2", name, value, "FAIL" if diff else "PASS")


def m3(root, date, cards):
    name = "Advisory findings vs blocking failures"
    if not cards:
        return row("M3", name, "NOT FETCHED — no scorecards under data/quality/scorecards",
                   "REPORTED")
    meta = _checks(root)
    blocking = advisory = 0
    for _, c in cards:
        for d in c.get("details", []):
            sev = meta.get(d.get("checkId") if isinstance(d, dict) else None, ("", "advisory"))[1]
            if sev == "blocking":
                blocking += 1
            else:
                advisory += 1
    return row("M3", name, "blocking %d · advisory %d (%s; never summed)" % (
        blocking, advisory, date), "REPORTED")


def m6(root, routes, date, cards):
    name = "Minimum rendered text >= 12.5px"
    if not routes:
        return row("M6", name, "no project 5 page in scope yet", "EMPTY")
    by = {c.get("slug"): (p, c) for p, c in cards}
    missing = [r for r in routes if r not in by]
    if missing:
        return row("M6", name, "NOT FETCHED — no scorecard for " + ", ".join(missing), "FAIL")
    hard, stale, bad = [], [], []
    for r in routes:
        path, c = by[r]
        if any(isinstance(d, dict) and d.get("checkId") == MIN_FONT for d in c.get("details", [])):
            bad.append(r)
            hard.append(r)
        # A missing key fails here although M1 only names it: M1 judges the harness, and a
        # check registered since the last run is not the harness's fault; M6 judges this page,
        # and a page whose text size was never measured has no M6 number.
        if not c.get("examined_by_check", {}).get(MIN_FONT):
            hard.append("%s examined 0" % r)
        built, rel = built_file(root, r if r != "index" else "")
        if not built.is_file():
            hard.append(f"{r}: not built ({rel})")
        elif path.stat().st_mtime < built.stat().st_mtime:
            stale.append(f"{r}: scorecard older than {rel} — re-run npm run test:render:pages")
    value = "%d of %d pages clean (%s)" % (len(routes) - len(bad), len(routes), date)
    return row("M6", name, value, _verdict(hard, stale), "; ".join(hard + stale))


def gate_report(root, key, route, head, strict):
    """(report or None, hard problems, stale problems) for one page's gate:page report.

    `strict` (M10): the report's head must be HEAD. Otherwise (M8) an ancestor of HEAD will
    do while the page's sources are the same at both. Either way a dirty-tree gate and a page
    hash that is not today's built page are stale."""
    path = root / "docs/reports/gate-page" / (key.replace("/", "--") + ".json")
    if not path.is_file():
        return None, [f"{key}: no gate:page report"], []
    rep = _json(path)
    if not isinstance(rep, dict):
        return None, [f"{key}: malformed gate:page report"], []
    built, rel = built_file(root, route)
    if not built.is_file():
        return rep, [f"{key}: not built ({rel})"], []
    stale = []
    rh = rep.get("head")
    again = f"re-run npm run gate:page -- {key}"
    if isinstance(rh, str) and rh.endswith("-dirty"):
        stale.append(f"{key}: gated on a dirty tree — re-gate after commit")
    elif not head:
        stale.append(f"{key}: HEAD unreadable — the report's commit cannot be checked")
    elif strict:
        if not same_commit(rh, head):
            stale.append(f"{key}: report is for {rh}, HEAD is {head} — dup crossover is "
                         f"site-wide; {again} at the final commit")
    elif not (isinstance(rh, str) and SHA.fullmatch(rh) and PRR.is_ancestor(rh, head, root)):
        stale.append(f"{key}: report is for {rh}, not an ancestor of HEAD {head} — {again}")
    else:
        changed = PRR.changed_between(key, rh, head, root)
        if changed:
            stale.append(f"{key}: sources changed since {rh[:12]}: {', '.join(changed)} — {again}")
    current = RC.content_hash(built.read_text(encoding="utf-8", errors="replace"))
    if rep.get("page_hash") != current:
        stale.append(f"{key}: built page differs from the one gated ({rel}) — {again}")
    return rep, [], stale


def m8(root, pages, head):
    name = "Gate runs per page, both clean"
    if not pages:
        return row("M8", name, "no project 5 page in scope yet", "EMPTY")
    hard, stale, clean = [], [], 0
    for k, route in pages:
        r, h, s = gate_report(root, k, route, head, strict=False)
        if r is not None and not h:
            runs = r.get("runs") if isinstance(r.get("runs"), int) else 0
            if runs < 2 or r.get("verdict") != "PASS" or r.get("identical") is not True:
                h.append(f"{k}: {runs} runs, {r.get('verdict')}, identical {r.get('identical')}")
        hard += h
        stale += s
        clean += not h and not s
    value = "%d of %d pages: >= 2 runs, both clean" % (clean, len(pages))
    return row("M8", name, value, _verdict(hard, stale), "; ".join(hard + stale))


def dup_problems(key, rep):
    """(body, headers, problems) from one report's dup steps and their per-run evidence."""
    steps = rep.get("steps") if isinstance(rep.get("steps"), list) else []
    by = {s.get("step"): s for s in steps if isinstance(s, dict)}
    runs = rep.get("evidence") if isinstance(rep.get("evidence"), list) else []
    counts, problems = [], []
    for name in DUP_STEPS:
        step = by.get(name)
        if step is None:
            problems.append(f"{key}: missing step {name}")
            counts.append(0)
            continue
        per_run = step.get("problems")
        per_run = [n for n in per_run if isinstance(n, int)] if isinstance(per_run, list) else []
        counts.append(max(per_run or [0]))
        evs = [e.get("evidence") for run in runs if isinstance(run, list) for e in run
               if isinstance(e, dict) and e.get("step") == name]
        if any(isinstance(ev, dict) and "error" in ev for ev in evs):
            problems.append(f"{key}: {name} audit error")
        elif not evs or not all(isinstance(ev, dict) and isinstance(ev.get("pages"), int)
                                and ev["pages"] > 0 for ev in evs):
            problems.append(f"{key}: {name} examined nothing")
    return counts[0], counts[1], problems


def m10(root, pages, head):
    name = "Dup crossover, body and headers"
    if not pages:
        return row("M10", name, "no project 5 page in scope yet", "EMPTY")
    body = heads = read = 0
    hard, stale = [], []
    for k, route in pages:
        r, h, s = gate_report(root, k, route, head, strict=True)
        hard += h
        stale += s
        if r is None:
            continue
        read += 1
        b, hd, problems = dup_problems(k, r)
        body += b
        heads += hd
        hard += problems
    value = "body %d · headers %d across %d pages" % (body, heads, read)
    return row("M10", name, value, _verdict(hard or body or heads, stale), "; ".join(hard + stale))


def m9(root):
    name = "Rework rate: page vs harness, never merged"
    ledger_ = _json(root / "data/quality/rework-ledger.json", {})
    windows = ledger_.get("windows") if isinstance(ledger_, dict) else None
    if not isinstance(windows, list) or not windows or not isinstance(windows[-1], dict):
        return row("M9", name, "NOT FETCHED — data/quality/rework-ledger.json holds no window yet",
                   "REPORTED")
    w = windows[-1]
    return row("M9", name, "page %s · harness %s (window %s)" % (
        w.get("page_rate"), w.get("harness_rate"), w.get("window") or w.get("end") or "latest"),
        "REPORTED")


def m12(root, keys):
    name = "LLM visibility cells fetched / total"
    if not keys:
        return row("M12", name, "no project 5 page in scope yet", "EMPTY")
    intel = root / "docs/research/llm-intel"
    names = sorted(p.name for p in intel.glob("*.json")) if intel.is_dir() else []
    fetched = 0
    gaps = []
    for k in keys:
        rx = re.compile(re.escape(k.replace("/", "--")) + r"-\d{4}-\d{2}-\d{2}\.json")
        files = [n for n in names if rx.fullmatch(n)]
        data = _json(intel / files[-1], {}) if files else None
        got = data.get("fetched") if isinstance(data, dict) else None
        status = got.get("status") if isinstance(got, dict) else (
            "malformed llm-intel file" if files else None)
        if status == "ok":
            fetched += 1
        else:
            gaps.append(f"{k}: {status or 'no llm-intel file'}")
    return row("M12", name, "%d / %d (one engine, one query per page)" % (fetched, len(keys)),
               "REPORTED", "; ".join(gaps))


def m13(root, head):
    name = "Slugs whose rendered output changed"
    data = _json(root / "docs/reports/rendered-changes.json")
    if not isinstance(data, dict) or not isinstance(data.get("changed"), list):
        return row("M13", name, "NOT FETCHED — no docs/reports/rendered-changes.json (run "
                   "python3 scripts/rendered_changes.py --base <ref> --json)", "REPORTED")
    changed = [str(c) for c in data["changed"]]
    written = str(data.get("head"))
    # `head` as rendered_changes.py wrote it: a 12-char sha, `-dirty` when the tree was
    # modified — never cut, and labelled, or a dirty build would read as the clean commit.
    dirty = " (built from a dirty tree)" if written.endswith("-dirty") else ""
    value = "%d (base %s → head %s%s) · IndexNow submitted: NOT FETCHED — project 6" % (
        len(changed), data.get("base"), written, dirty)
    if not same_commit(written, head):
        return row("M13", name, value, "STALE",
                   f"rendered-changes.json is for {written}, HEAD is {head} — re-run "
                   "rendered_changes.py --base <ref> --json")
    return row("M13", name, value, "REPORTED", ", ".join(changed))


def m18(root):
    name = "Untested rules in the rule index"
    index = _json(root / "data/quality/rule-index.json", {})
    rules = index.get("rules") if isinstance(index, dict) else None
    if not isinstance(rules, list) or not all(isinstance(r, dict) for r in rules):
        return row("M18", name, "NOT FETCHED — data/quality/rule-index.json is missing or "
                   "has no rules list", "REPORTED")
    untested = sorted(str(r.get("id")) for r in rules if r.get("enforced") == "untested")
    return row("M18", name, "%d of %d rules" % (len(untested), len(rules)), "REPORTED",
               ", ".join(untested))


def ledger(project, slugs=None, root=ROOT, today=None, head=None):
    root = pathlib.Path(root)
    head = git_head(root) if head is None else head
    slugs = default_slugs(root) if slugs is None else list(slugs)
    pages = [resolve_page(s, root) for s in slugs]
    keys = [k for k, _ in pages]
    routes = [r or "index" for _, r in pages]
    date, cards, broken = latest_cards(root)
    rows = [m1(root, date, cards, broken), m2(root), m3(root, date, cards),
            m6(root, routes, date, cards), m8(root, pages, head), m9(root),
            m10(root, pages, head), m12(root, keys), m13(root, head), m18(root)]
    return {"project": project, "date": (today or datetime.date.today()).isoformat(),
            "head": head, "scope": keys, "rows": rows,
            "failed": [r["id"] for r in rows if r["id"] in FAILING
                       and r["status"] in ("FAIL", "STALE")],
            "stale": [r["id"] for r in rows if r["status"] == "STALE"],
            "empty": [r["id"] for r in rows if r["status"] == "EMPTY"]}


def header(led):
    return ("Measurement ledger — %s · %s · scope %s · HEAD %s · failed: %s · stale: %s · "
            "empty: %s") % (
        led["project"], led["date"], ", ".join(led["scope"]) or "none", led["head"],
        ", ".join(led["failed"]) or "none", ", ".join(led["stale"]) or "none",
        ", ".join(led["empty"]) or "none")


def markdown(led):
    esc = lambda v: str(v).replace("|", "\\|")
    out = ["| # | Measurement | Value | Status | Detail |", "|---|---|---|---|---|"]
    out += ["| %s | %s | %s | %s | %s |" % (r["id"], esc(r["measurement"]), esc(r["value"]),
                                            r["status"], esc(r["detail"]) or "—")
            for r in led["rows"]]
    return "\n".join(out) + "\n"


def main(argv=None, root=ROOT, head=None):
    ap = argparse.ArgumentParser(prog="measurement_ledger.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("project", help="the project's name, [a-z0-9-]+, e.g. p5 — names the JSON file")
    ap.add_argument("--slugs", nargs="+", help="the pages (default: project 5 pages in rebuilt.json)")
    ap.add_argument("--md", metavar="PATH", help="also write the header and table to PATH")
    ap.add_argument("--require-pages", action="store_true",
                    help="exit 1 when no page is in scope or any row is EMPTY")
    ns = ap.parse_args(argv)
    if not PROJECT.fullmatch(ns.project):
        print(f"measurement-ledger ERROR project {ns.project!r} is not [a-z0-9-]+")
        return 2
    try:
        led = ledger(ns.project, ns.slugs, root, head=head)
    except ValueError as e:
        print(f"measurement-ledger ERROR {e}")
        return 2
    out = pathlib.Path(root) / "docs/reports" / f"{ns.project}-ledger.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    table = markdown(led)
    if ns.md:
        pathlib.Path(ns.md).write_text(header(led) + "\n\n" + table, encoding="utf-8")
    print(header(led) + "\n")
    print(table, end="")
    empty = ("empty: " + ", ".join(led["empty"]) + " — nothing measured") if led["empty"] \
        else "empty: none"
    print("measurement-ledger: %d rows, %d page(s) in scope; failed: %s; stale: %s; %s; JSON %s" % (
        len(led["rows"]), len(led["scope"]), ", ".join(led["failed"]) or "none",
        ", ".join(led["stale"]) or "none", empty,
        out.relative_to(root) if pathlib.Path(root) in out.parents else out))
    if ns.require_pages and (not led["scope"] or led["empty"]):
        print("measurement-ledger FAIL --require-pages: %s" % (
            "no page in scope" if not led["scope"] else "EMPTY rows " + ", ".join(led["empty"])))
        return 1
    return 1 if led["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
