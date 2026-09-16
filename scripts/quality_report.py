#!/usr/bin/env python3
"""One screen: is the quality loop closing, and what should be fixed next?

    python3 scripts/quality_report.py

Sections:
  1. Rework rate, current window and delta          (the lagging indicator)
  2. First-run defects per page, by family          (the leading indicator)
  3. Worst family                                   (the next-action list)
  4. Open overrides                                 (suppressed defects, counted)
  5. Rules with no backing test                     (the deletion-candidate list)

Section 5 is the one that makes "no test, no rule" real. Everything else is
reporting; that section is enforcement.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "quality" / "rework-ledger.json"
SCORECARDS = ROOT / "data" / "quality" / "scorecards"
RULE_INDEX = ROOT / "data" / "quality" / "rule-index.json"
CHECKS_DIR = ROOT / "tests" / "render" / "checks"

CHECK_ID_RE = re.compile(r"""\bid:\s*['"]([a-z0-9-]+)['"]""")


def check_ids_from_source(text: str) -> set:
    """Every check id declared in a checks/*.ts source.

    Read from source rather than by running the harness so the report works when
    the harness is red — which is exactly when you most want to know which rules
    have lost their backing test.
    """
    return set(CHECK_ID_RE.findall(text))


PY_AUDIT_ID_RE = re.compile(r"""\{\s*"id":\s*"([a-z0-9-]+)"\s*\}""")


def registry_check_ids(checks_dir: pathlib.Path = CHECKS_DIR) -> set:
    ids = set()
    for p in sorted(checks_dir.glob("*.ts")):
        ids |= check_ids_from_source(p.read_text())
    # Python audits declare their ids as CHECK_IDS = [{"id": "..."}, ...]; they back
    # `enforced: test` rows the same way a checks/*.ts id does.
    for p in sorted((ROOT / "scripts").glob("*_audit.py")):
        ids |= set(PY_AUDIT_ID_RE.findall(p.read_text()))
    return ids


def broken_test_links(index: dict, check_ids: set) -> list:
    """Rules claiming `enforced: test` whose named check does not exist.

    This is the failure mode that would quietly hollow the whole scheme out: a rule
    keeps its exemption from the deletion list by pointing at a test that was
    renamed or deleted months ago.
    """
    out = []
    for r in index.get("rules", []):
        if r.get("enforced") != "test":
            continue
        ref = (r.get("test") or "").strip()
        ids = re.findall(r"::([\w-]+)", ref)
        if ids:
            # A `file::check` reference is a claim about a CHECK, and the check id is the
            # whole claim — file existence proves nothing, because the file can outlive
            # the check that was renamed out of it. Every named id must be registered:
            # a rule enforced by two checks (heading-hierarchy-outline-gate) must not pass
            # on the strength of the second one alone.
            if all(i in check_ids for i in ids):
                continue
            out.append(r["id"])
            continue
        # No `::` — the reference names a TEST FILE. `no-test-no-rule` is held up by
        # tests/test_quality_report.py, this module's own suite, and before this branch
        # existed any such rule was unrepresentable: the validator knew only render-check
        # ids, so a real, passing pytest file read as a broken link. Verified on disk so
        # the branch can still fail.
        if ref and (ROOT / ref).exists():
            continue
        out.append(r["id"])
    return out


def deletion_candidates(index: dict) -> list:
    """Rules with neither a test nor a justified judgment class.

    A judgment rule with no `why` counts as a candidate: the `why` IS the cap. A
    class you can join without stating why a test cannot exist is an exemption
    anyone can grant themselves.
    """
    out = []
    for r in index.get("rules", []):
        enforced = r.get("enforced")
        if enforced == "test":
            continue
        if enforced == "judgment" and (r.get("why") or "").strip():
            continue
        out.append(r["id"])
    return out


def judgment_overflow(index: dict):
    """(count, cap) when the judgment class is over its cap, else None."""
    cap = index.get("judgment_cap", 12)
    n = sum(1 for r in index.get("rules", []) if r.get("enforced") == "judgment")
    return (n, cap) if n > cap else None


def load_scorecards(d: pathlib.Path = SCORECARDS) -> list:
    """Most recent card per slug, newest first."""
    latest = {}
    for p in sorted(d.glob("*.json")):
        c = json.loads(p.read_text())
        prev = latest.get(c["slug"])
        if prev is None or c.get("date", "") >= prev.get("date", ""):
            latest[c["slug"]] = c
    return sorted(latest.values(), key=lambda c: (c.get("date", ""), c["slug"]), reverse=True)


def worst_family(cards: list):
    """(family, rows) with the most defect ROWS.

    Rows, never instances. Ranking by instances would permanently elect whichever
    check enumerates the most nodes, which is a fact about the check, not the site.
    """
    tally = {}
    for c in cards:
        for fam, n in (c.get("defects") or {}).items():
            tally[fam] = tally.get(fam, 0) + n
    if not tally:
        return (None, 0)
    return max(tally.items(), key=lambda kv: kv[1])


def open_overrides(cards: list) -> list:
    out = []
    for c in cards:
        for o in c.get("overrides") or []:
            out.append((c["slug"], o["checkId"], o["reason"]))
    return out


def trend(ledger: dict):
    """(most recent window, delta vs the one before it or None).

    The delta is computed on the SAME number that gets printed. After the 2026-08-03
    split the headline is `page_rate`, so a delta taken from the union `rate` would sit
    next to the page figure and describe something else entirely — the union moved
    +4.0 points in the window where page rework moved -0.8. Both windows must carry the
    key, or there is nothing comparable to subtract.
    """
    w = sorted(ledger.get("windows", []), key=lambda x: x["from"])
    if not w:
        return (None, None)
    if len(w) == 1:
        return (w[-1], None)
    key = "page_rate" if "page_rate" in w[-1] and "page_rate" in w[-2] else "rate"
    return (w[-1], w[-1][key] - w[-2][key])


def _read(path: pathlib.Path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=10, help="how many pages to list")
    args = ap.parse_args(argv)

    ledger = _read(LEDGER, {"windows": []})
    index = _read(RULE_INDEX, {"rules": []})
    cards = load_scorecards()
    ids = registry_check_ids()

    print("=" * 78)
    print("BSUK QUALITY REPORT")
    print("=" * 78)

    cur, delta = trend(ledger)
    print("\n1. REWORK RATE  (lagging — spec target: under 15% at 90 days)")
    if cur is None:
        print("   no windows recorded — run scripts/rework_ledger.py --last-30-days (arrives with project 4)")
    else:
        arrow = "" if delta is None else f"  ({delta:+.1%} vs previous window)"
        # PAGE rework is the headline. Harness self-repair is printed beside it, never
        # folded in: the learning loop REQUIRES escaped defects to be charged to the
        # harness, so counting checker fixes here would make the number worse every time
        # the loop works. Split 2026-08-03; every historical window was recomputed then.
        # `page_rate` is absent from windows recorded before the split — fall back rather
        # than crash, and say which number is being shown.
        if "page_rate" in cur:
            print(f"   {cur['from']} .. {cur['to']}   "
                  f"PAGE {cur['page_rework']}/{cur['total']} = {cur['page_rate']:.1%}{arrow}")
            print(f"   {'':<24}harness self-repair {cur['harness_rework']} = "
                  f"{cur['harness_rate']:.1%}  (checker fixes, no page edited)")
        else:
            print(f"   {cur['from']} .. {cur['to']}   {cur['rework']}/{cur['total']} = "
                  f"{cur['rate']:.1%}{arrow}   [pre-split window: page and harness combined]")

    print(f"\n2. FIRST-RUN DEFECTS  (leading — most recent {args.limit} pages)")
    if not cards:
        print("   no scorecards — run npm run test:render:pages && node scripts/build_scorecard.mjs")
    else:
        print(f"   {'page':<46}{'rows':>6}{'inst':>7}  by family")
        for c in cards[: args.limit]:
            fams = " ".join(f"{k}:{v}" for k, v in sorted((c.get('defects') or {}).items()))
            print(f"   {c['slug'][:45]:<46}{c.get('total', 0):>6}{c.get('total_instances', 0):>7}  {fams}")

    fam, n = worst_family(cards)
    print("\n3. NEXT ACTION")
    print(f"   worst family: {fam or 'n/a'} ({n} rows) — fix the check first if it looks impossible")

    ovr = open_overrides(cards)
    # Grouped by (check, reason), not listed per page. An override is DECLARED once for a
    # run and rides along in every page's scorecard, so printing it per page repeated one
    # 105-character reason nine times and swallowed the screen this report promises to fit
    # on. Its magnitude is the number of pages it silences — that is a count, not nine
    # copies of the same sentence. Same mixed-unit error the harness itself was just fixed
    # for; `open_overrides` still returns per-page tuples, because callers and its test
    # want the pages, and only the DISPLAY groups.
    grouped: dict = {}
    for slug, cid, reason in ovr:
        grouped.setdefault((cid, reason), []).append(slug)
    print(f"\n4. OPEN OVERRIDES  ({len(grouped)} distinct, suppressing on {len(ovr)} page-runs)")
    for (cid, reason), slugs in grouped.items():
        print(f"   {cid} — silencing {len(slugs)} page(s)")
        print(f"      {reason}")
    if not grouped:
        print("   none")

    print("\n5. RULES WITH NO BACKING TEST  (deletion candidates)")
    broken = broken_test_links(index, ids)
    orphans = deletion_candidates(index)
    over = judgment_overflow(index)
    if broken:
        print(f"   BROKEN test link (rule claims a check that does not exist): {', '.join(broken)}")
    if orphans:
        print(f"   no test and no justified judgment class: {', '.join(orphans)}")
    if over:
        print(f"   judgment class is {over[0]}, cap is {over[1]} — it is a cap, not a loophole")
    if not (broken or orphans or over):
        n_j = sum(1 for r in index.get('rules', []) if r.get('enforced') == 'judgment')
        print(f"   none. {len(ids)} checks registered, {n_j} judgment rules within cap.")

    print()
    # Exit non-zero on a broken test link only. An orphan rule is a decision for a
    # human; a rule pointing at a check that no longer exists is a fact, and a fact
    # that silently passes is how the twelve lying gates happened.
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
