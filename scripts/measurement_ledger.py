#!/usr/bin/env python3
"""measurement_ledger.py <project> [--slugs S ...] [--md PATH] — the numbers a close reports.

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
  M12  LLM visibility cells fetched / total                  docs/research/llm-intel/<slug>-*.json
  M13  slugs whose rendered output changed                   docs/reports/rendered-changes.json
  M18  untested rules in the rule index                      data/quality/rule-index.json

The pages are --slugs, else every page in data/facts/rebuilt.json that is not one of the twelve
built before the project 5 rules (scripts/family_rules.py BUILT_BEFORE_SYSTEM_GAPS).

Writes docs/reports/<project>-ledger.json and prints the markdown table; --md PATH also writes
the table to PATH for the gate report. A number that cannot be read is written
`NOT FETCHED — <barrier>`, never guessed.

Exit 1 when M1, M2, M6, M8 or M10 is FAIL; 0 otherwise.
"""
import argparse
import datetime
import glob
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import family_rules as FR  # noqa: E402
import render_baseline as RB  # noqa: E402
from _slugs import resolve_page  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
FAILING = ("M1", "M2", "M6", "M8", "M10")
MIN_FONT = "layout-min-font-size"


def _json(path, default=None):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def default_slugs(root):
    rows = _json(root / "data/facts/rebuilt.json", []) or []
    return [s for s in rows if isinstance(s, str) and s not in FR.BUILT_BEFORE_SYSTEM_GAPS]


def latest_cards(root):
    """(run label, [card]): the newest card of each slug, or (None, []).

    Per slug, as tests/render/lib/examined.ts latestCards reads them: a one-page re-run writes
    today's card for that page only, and judging today's date alone would drop every other
    page. The label is the one date, or "runs <oldest> to <newest>" when the cards span dates."""
    cards_dir = root / "data/quality/scorecards"
    if not cards_dir.is_dir():
        return None, []
    best = {}
    for p in sorted(cards_dir.glob("*.json")):
        date = p.stem[-10:]
        if date.count("-") != 2:
            continue
        card = _json(p)
        if not isinstance(card, dict):
            continue
        slug = card.get("slug", p.stem[:-11])
        if slug not in best or date > best[slug][0]:
            best[slug] = (date, card)
    if not best:
        return None, []
    dates = sorted({d for d, _ in best.values()})
    label = "run " + dates[0] if len(dates) == 1 else "runs %s to %s" % (dates[0], dates[-1])
    return label, [best[s][1] for s in sorted(best)]


def row(mid, measurement, value, status, detail=""):
    return {"id": mid, "measurement": measurement, "value": value, "status": status,
            "detail": detail}


def m1(root, date, cards):
    name = "Nodes examined per check, on real pages"
    if not cards:
        return row("M1", name, "NOT FETCHED — no scorecards under data/quality/scorecards "
                   "(run npm run test:render:pages)", "FAIL")
    deferred = (_json(root / "tests/render/targets.json", {}) or {}).get("deferred_checks", {})
    examined = {}
    for c in cards:
        for check, n in c.get("examined_by_check", {}).items():
            examined[check] = examined.get(check, 0) + n
    zero = sorted(k for k, n in examined.items() if n == 0 and k not in deferred)
    # tests/render/lib/examined.ts notYetMeasured: a registered, non-deferred check with no key
    # in any card was registered since the last page run — named, not failed.
    unmeasured = sorted(k for k in RB.load_checks(root / "tests/render/checks")
                        if k not in examined and k not in deferred)
    value = "%d checks, %d at zero%s (%s, %d pages)" % (
        len(examined), len(zero),
        ", %d not yet measured" % len(unmeasured) if unmeasured else "", date, len(cards))
    detail = "; ".join(x for x in (", ".join(zero), "not yet measured: " + ", ".join(unmeasured)
                                   if unmeasured else "") if x)
    return row("M1", name, value, "FAIL" if zero else "PASS", detail)


def m2(root):
    name = "Families registered vs families wired"
    registered = {fam for fam, _ in RB.load_checks(root / "tests/render/checks").values()}
    targets = _json(root / "tests/render/targets.json", {}) or {}
    wired = {f for fams in targets.get("families_by_page_type", {}).values() for f in fams}
    diff = sorted(registered ^ wired)
    value = "registered %d · wired %d · difference %s" % (
        len(registered), len(wired), "∅" if not diff else "{" + ", ".join(diff) + "}")
    return row("M2", name, value, "FAIL" if diff else "PASS")


def m3(root, date, cards):
    name = "Advisory findings vs blocking failures"
    if not cards:
        return row("M3", name, "NOT FETCHED — no scorecards under data/quality/scorecards",
                   "REPORTED")
    meta = RB.load_checks(root / "tests/render/checks")
    blocking = advisory = 0
    for c in cards:
        for d in c.get("details", []):
            sev = meta.get(d["checkId"], ("", "advisory"))[1]
            if sev == "blocking":
                blocking += 1
            else:
                advisory += 1
    return row("M3", name, "blocking %d · advisory %d (%s; never summed)" % (
        blocking, advisory, date), "REPORTED")


def m6(routes, date, cards):
    name = "Minimum rendered text >= 12.5px"
    if not routes:
        return row("M6", name, "no project 5 page in scope yet", "EMPTY")
    by = {c.get("slug"): c for c in cards}
    missing = [r for r in routes if r not in by]
    if missing:
        return row("M6", name, "NOT FETCHED — no scorecard for " + ", ".join(missing), "FAIL")
    bad = [r for r in routes if any(d["checkId"] == MIN_FONT for d in by[r].get("details", []))]
    unexamined = [r for r in routes if not by[r].get("examined_by_check", {}).get(MIN_FONT)]
    value = "%d of %d pages clean (%s)" % (len(routes) - len(bad), len(routes), date)
    return row("M6", name, value, "FAIL" if bad or unexamined else "PASS",
               ", ".join(bad + ["%s examined 0" % r for r in unexamined]))


def _gate_report(root, key):
    return _json(root / "docs/reports/gate-page" / (key.replace("/", "--") + ".json"))


def m8(root, keys):
    name = "Gate runs per page, both clean"
    if not keys:
        return row("M8", name, "no project 5 page in scope yet", "EMPTY")
    bad = []
    for k in keys:
        r = _gate_report(root, k)
        if r is None:
            bad.append(f"{k}: no gate:page report")
        elif r.get("runs", 0) < 2 or r.get("verdict") != "PASS" or not r.get("identical"):
            bad.append(f"{k}: {r.get('runs', 0)} runs, {r.get('verdict')}, "
                       f"identical {r.get('identical')}")
    value = "%d of %d pages: >= 2 runs, both clean" % (len(keys) - len(bad), len(keys))
    return row("M8", name, value, "FAIL" if bad else "PASS", "; ".join(bad))


def m9(root):
    name = "Rework rate: page vs harness, never merged"
    windows = (_json(root / "data/quality/rework-ledger.json", {}) or {}).get("windows") or []
    if not windows:
        return row("M9", name, "NOT FETCHED — data/quality/rework-ledger.json holds no window yet",
                   "REPORTED")
    w = windows[-1]
    return row("M9", name, "page %s · harness %s (window %s)" % (
        w.get("page_rate"), w.get("harness_rate"), w.get("window") or w.get("end") or "latest"),
        "REPORTED")


def m10(root, keys):
    name = "Dup crossover, body and headers"
    if not keys:
        return row("M10", name, "no project 5 page in scope yet", "EMPTY")
    body = heads = 0
    missing = []
    for k in keys:
        r = _gate_report(root, k)
        if r is None:
            missing.append(k)
            continue
        steps = {s["step"]: s for s in r.get("steps", [])}
        body += max(steps.get("dup-body", {}).get("problems", [0]) or [0])
        heads += max(steps.get("dup-headers", {}).get("problems", [0]) or [0])
    value = "body %d · headers %d across %d pages" % (body, heads, len(keys) - len(missing))
    detail = ("no gate:page report for " + ", ".join(missing)) if missing else ""
    return row("M10", name, value, "FAIL" if body or heads or missing else "PASS", detail)


def m12(root, keys):
    name = "LLM visibility cells fetched / total"
    if not keys:
        return row("M12", name, "no project 5 page in scope yet", "EMPTY")
    fetched = 0
    gaps = []
    for k in keys:
        files = sorted(glob.glob(str(root / "docs/research/llm-intel" / f"{k}-*.json")))
        status = ((_json(files[-1], {}) or {}).get("fetched") or {}).get("status") if files else None
        if status == "ok":
            fetched += 1
        else:
            gaps.append(f"{k}: {status or 'no llm-intel file'}")
    return row("M12", name, "%d / %d (one engine, one query per page)" % (fetched, len(keys)),
               "REPORTED", "; ".join(gaps))


def m13(root):
    name = "Slugs whose rendered output changed"
    data = _json(root / "docs/reports/rendered-changes.json")
    if not data:
        return row("M13", name, "NOT FETCHED — no docs/reports/rendered-changes.json (run "
                   "python3 scripts/rendered_changes.py --base <ref> --json)", "REPORTED")
    changed = data.get("changed", [])
    # `head` as rendered_changes.py wrote it: a 12-char sha, `-dirty` when the tree was
    # modified — never cut, or a dirty build would read as the clean commit.
    return row("M13", name, "%d (base %s → head %s)" % (
        len(changed), data.get("base"), data.get("head")), "REPORTED",
        ", ".join(changed))


def m18(root):
    name = "Untested rules in the rule index"
    rules = (_json(root / "data/quality/rule-index.json", {}) or {}).get("rules", [])
    untested = sorted(r["id"] for r in rules if r.get("enforced") == "untested")
    return row("M18", name, "%d of %d rules" % (len(untested), len(rules)), "REPORTED",
               ", ".join(untested))


def ledger(project, slugs=None, root=ROOT, today=None):
    root = pathlib.Path(root)
    slugs = default_slugs(root) if slugs is None else list(slugs)
    pages = [resolve_page(s, root) for s in slugs]
    keys = [k for k, _ in pages]
    routes = [r or "index" for _, r in pages]
    date, cards = latest_cards(root)
    rows = [m1(root, date, cards), m2(root), m3(root, date, cards), m6(routes, date, cards),
            m8(root, keys), m9(root), m10(root, keys), m12(root, keys), m13(root), m18(root)]
    return {"project": project, "date": (today or datetime.date.today()).isoformat(),
            "scope": keys, "rows": rows,
            "failed": [r["id"] for r in rows if r["id"] in FAILING and r["status"] == "FAIL"]}


def markdown(led):
    esc = lambda v: str(v).replace("|", "\\|")
    out = ["| # | Measurement | Value | Status | Detail |", "|---|---|---|---|---|"]
    out += ["| %s | %s | %s | %s | %s |" % (r["id"], esc(r["measurement"]), esc(r["value"]),
                                            r["status"], esc(r["detail"]) or "—")
            for r in led["rows"]]
    return "\n".join(out) + "\n"


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(prog="measurement_ledger.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("project", help="the project's name, e.g. p5 — names the JSON file")
    ap.add_argument("--slugs", nargs="+", help="the pages (default: project 5 pages in rebuilt.json)")
    ap.add_argument("--md", metavar="PATH", help="also write the markdown table to PATH")
    ns = ap.parse_args(argv)
    try:
        led = ledger(ns.project, ns.slugs, root)
    except ValueError as e:
        print(f"measurement-ledger ERROR {e}")
        return 2
    out = pathlib.Path(root) / "docs/reports" / f"{ns.project}-ledger.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    table = markdown(led)
    if ns.md:
        pathlib.Path(ns.md).write_text(table, encoding="utf-8")
    print(table, end="")
    print("measurement-ledger: %d rows, %d page(s) in scope; failed: %s; JSON %s" % (
        len(led["rows"]), len(led["scope"]), ", ".join(led["failed"]) or "none",
        out.relative_to(root) if pathlib.Path(root) in out.parents else out))
    return 1 if led["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
