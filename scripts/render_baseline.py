#!/usr/bin/env python3
"""Derive the render-harness baseline table from the scorecards, so nobody types it.

`data/quality/scorecards/<slug>-<date>.json` records one `details` row per check that
reported on that page, and those rows carry NO severity: the scorecard groups by FAMILY only.
Blocking-vs-advisory is a property of the check, declared as a `severity:` literal beside its
`id:` in `tests/render/checks/*.ts`, so this script resolves it by reading those TypeScript
sources. That is the one coupling worth stating out loud — if a check's severity is flipped in
the .ts file, this table changes without any scorecard changing, which is the intended
behaviour and the reason `--check` belongs in the sweep.

    python3 scripts/render_baseline.py                      # print the table for the latest run
    python3 scripts/render_baseline.py --date 2026-09-17    # ... for one run
    python3 scripts/render_baseline.py --compare 2026-09-16 # per-check deltas, other -> chosen
    python3 scripts/render_baseline.py --write <report.md>  # regenerate the block in the report
    python3 scripts/render_baseline.py --check              # exit 1 if the report is stale

`--write` replaces only the text between `<!-- generated:start -->` and `<!-- generated:end -->`,
so the report's hand-written prose survives regeneration. `--check` implies the default report
and never writes.
"""
import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCORECARDS = ROOT / "data/quality/scorecards"
CHECKS = ROOT / "tests/render/checks"
REPORT = ROOT / "docs/reports/render-baseline-project2.md"
START = "<!-- generated:start -->"
END = "<!-- generated:end -->"

# `id: 'x'` … `family: 'Y'` … `severity: 'z'` in that order inside one check literal. The
# non-greedy body cannot cross the next `id:`, which is what keeps neighbouring checks apart.
CHECK_RX = re.compile(
    r"\bid:\s*'([a-z0-9-]+)'((?:(?!\bid:\s*')[\s\S])*?)"
    r"\bfamily:\s*'([A-Z0-9]+)'((?:(?!\bid:\s*')[\s\S])*?)"
    r"\bseverity:\s*'(blocking|advisory)'"
)


def load_checks(checks_dir):
    """id -> (family, severity), read from the harness's TypeScript check definitions."""
    out = {}
    for path in sorted(checks_dir.glob("*.ts")):
        for m in CHECK_RX.finditer(path.read_text(encoding="utf-8")):
            out.setdefault(m.group(1), (m.group(3), m.group(5)))
    if not out:
        sys.exit(f"no check definitions found in {checks_dir} — severity cannot be resolved")
    return out


def dates_present(cards_dir):
    return sorted({p.stem[-10:] for p in cards_dir.glob("*.json") if p.stem[-10:].count("-") == 2})


def rows_for(cards_dir, date):
    """(rows_by_check, pages_by_check, slugs) for one scorecard run."""
    rows = collections.Counter()
    pages = collections.defaultdict(set)
    slugs = set()
    for card in sorted(cards_dir.glob(f"*-{date}.json")):
        data = json.loads(card.read_text(encoding="utf-8"))
        slug = data.get("slug", card.stem)
        slugs.add(slug)
        for row in data.get("details", []):
            rows[row["checkId"]] += 1
            pages[row["checkId"]].add(slug)
    return rows, pages, slugs


def render(cards_dir, checks_dir, date):
    meta = load_checks(checks_dir)
    rows, pages, slugs = rows_for(cards_dir, date)
    unknown = sorted(c for c in rows if c not in meta)
    if unknown:
        sys.exit(f"checks in the scorecards with no definition in {checks_dir}: {unknown}")

    fam_rows = collections.Counter()
    fam_pages = collections.defaultdict(set)
    for check, count in rows.items():
        family, severity = meta[check]
        fam_rows[(family, severity)] += count
        fam_pages[family] |= pages[check]
    families = sorted({fam for fam, _ in meta.values()} | set(fam_pages))

    out = [
        f"Scorecard run {date} — {len(slugs)} page scorecards, {sum(rows.values())} defect rows.",
        "",
        "| Family | Blocking rows | Advisory rows | Pages affected |",
        "|---|---|---|---|",
    ]
    total_b = total_a = 0
    for family in families:
        blocking = fam_rows[(family, "blocking")]
        advisory = fam_rows[(family, "advisory")]
        total_b += blocking
        total_a += advisory
        out.append(f"| {family} | {blocking} | {advisory} | {len(fam_pages[family])} |")
    out.append(f"| **Total** | **{total_b}** | **{total_a}** | **{len(slugs)}** |")
    out.append("")
    by_check = ", ".join(
        f"`{c}` {n}" for c, n in sorted(rows.items(), key=lambda kv: (-kv[1], kv[0]))
    )
    out.append(f"Rows by check: {by_check}.")
    return "\n".join(out) + "\n"


def compare(cards_dir, date, other):
    now, _, _ = rows_for(cards_dir, date)
    then, _, _ = rows_for(cards_dir, other)
    lines = [f"per-check row deltas, {other} -> {date} (checks whose count did not move are omitted):"]
    moved = False
    for check in sorted(set(now) | set(then)):
        if now[check] != then[check]:
            moved = True
            lines.append(f"  {check} {then[check]} -> {now[check]}")
    if not moved:
        lines.append("  (no check moved)")
    return "\n".join(lines) + "\n"


def splice(report, block):
    text = report.read_text(encoding="utf-8")
    if START not in text or END not in text:
        sys.exit(f"{report} carries no {START} / {END} markers — add them around the table")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{block}{END}{tail}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", help="scorecard date (default: the latest present)")
    ap.add_argument("--compare", metavar="DATE", help="print per-check deltas against DATE")
    ap.add_argument("--write", metavar="REPORT", help="regenerate the block in REPORT")
    ap.add_argument("--check", action="store_true", help="exit 1 if the report is stale")
    ap.add_argument("--scorecards-dir", default=str(SCORECARDS))
    ap.add_argument("--checks-dir", default=str(CHECKS))
    args = ap.parse_args()

    cards_dir = pathlib.Path(args.scorecards_dir)
    checks_dir = pathlib.Path(args.checks_dir)
    available = dates_present(cards_dir)
    if not available:
        sys.exit(f"no scorecards in {cards_dir} — run node scripts/build_scorecard.mjs first")
    date = args.date or available[-1]
    if date not in available:
        sys.exit(f"no scorecards for {date}; present: {', '.join(available)}")

    block = render(cards_dir, checks_dir, date)
    report = pathlib.Path(args.write) if args.write else REPORT

    if args.check:
        want = splice(report, block)
        if report.read_text(encoding="utf-8") != want:
            print(f"{report} is stale — run: python3 scripts/render_baseline.py --write {report}")
            return 1
        print(f"examined {report.name}; 0 problems")
        return 0

    if args.write:
        report.write_text(splice(report, block), encoding="utf-8")
        print(f"wrote the generated block in {report}")
    else:
        print(block, end="")
    if args.compare:
        print(compare(cards_dir, date, args.compare), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
