#!/usr/bin/env python3
"""gap_matrix.py — the competitive gap matrix, built from the intel reports, never typed.

  python3 scripts/gap_matrix.py --write [--date YYYY-MM-DD] [--root DIR]
      writes docs/research/gap-matrix-<date>.md (date: today, UTC) · exit 0
  python3 scripts/gap_matrix.py --check [--root DIR]
      rebuilds the newest gap-matrix-<date>.md and compares · exit 0 same, or nothing written
      and no reports · 1 differs, or reports exist with no matrix
  Every mode: 2 bad usage · 6 a report is unreadable or breaks schemas/competitor-report.schema.json,
      or data/competitors.json is unreadable or not {"competitors": [{"id": "<string>"}, ...]}

Reads docs/research/competitors/*.json (bsuk.json is BSUK's own profile) and, when present,
data/competitors.json to name registry entries with no report. A row's N/M counts only the
competitors whose field was fetched; the ones that were not are their own column.

Spec: docs/superpowers/specs/2026-09-23-competitor-intel-design.md §6.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys
from collections import Counter
from dataclasses import dataclass

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas/competitor-report.schema.json"
REPORTS = "docs/research/competitors"
OUT_DIR = "docs/research"
DIMENSIONS = (("keywords", "Keyword gaps"), ("page_types", "Page-type gaps"),
              ("cities", "City gaps"), ("schema_types", "Schema gaps"))
QUEUE_LEN = 10
EXIT_OK, EXIT_FAIL, EXIT_USAGE, EXIT_BAD_INPUT = 0, 1, 2, 6


class BadReport(Exception):
    pass


@dataclass(frozen=True)
class Row:
    dimension: str
    value: str
    n: int
    m: int
    not_fetched: int
    bsuk_has: str      # "yes" · "no" · "not fetched"
    band: str          # "high" · "medium" · "low" · "—" (BSUK has it)


def _norm(v):
    return re.sub(r"\s+", " ", v.strip().lower())


def values(report, dim):
    """The set a report holds for one dimension, or None when that field was not fetched."""
    field = report[dim]
    if field["status"] != "ok":
        return None
    if dim == "page_types":
        return {k for k, count in field["values"].items() if count > 0}
    if dim == "cities":
        return set(field["values"])
    return {_norm(v) for v in field["values"]}


def load_reports(root=ROOT):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    bsuk, comps = None, {}
    for path in sorted((pathlib.Path(root) / REPORTS).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            raise BadReport(f"{path.name}: not valid JSON: {exc}")
        errors = list(validator.iter_errors(data))
        if errors:
            raise BadReport(f"{path.name}: {errors[0].message}")
        if data["id"] != path.stem:
            raise BadReport(f"{path.name}: id {data['id']!r} does not match the file name")
        if data["id"] == "bsuk":
            bsuk = data
        else:
            comps[data["id"]] = data
    return bsuk, comps


def priority(n, m):
    share = n / m
    return "high" if share >= 0.4 else "medium" if share >= 0.2 else "low"


def rows(bsuk, comps, dim):
    fetched = [values(c, dim) for c in comps.values()]
    held = [v for v in fetched if v is not None]
    m, not_fetched = len(held), len(fetched) - len(held)
    counts = Counter(v for vs in held for v in vs)
    ours = values(bsuk, dim) if bsuk else None
    out = []
    for value, n in counts.items():
        has = "not fetched" if ours is None else ("yes" if value in ours else "no")
        out.append(Row(dim, value, n, m, not_fetched, has,
                       "—" if has == "yes" else priority(n, m)))
    return sorted(out, key=lambda r: (-r.n, r.value))


def queue(bsuk, comps):
    order = {d: i for i, (d, _) in enumerate(DIMENSIONS)}
    gaps = [r for d, _ in DIMENSIONS for r in rows(bsuk, comps, d) if r.bsuk_has != "yes"]
    return sorted(gaps, key=lambda r: (-r.n / r.m, -r.n, order[r.dimension], r.value))[:QUEUE_LEN]


def _registry_ids(root):
    path = pathlib.Path(root) / "data/competitors.json"
    if not path.is_file():
        return None
    try:
        reg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise BadReport(f"data/competitors.json: not valid JSON: {exc}")
    comps = reg.get("competitors") if isinstance(reg, dict) else None
    if not isinstance(comps, list) or not all(
            isinstance(c, dict) and isinstance(c.get("id"), str) for c in comps):
        raise BadReport("data/competitors.json: competitors must be a list of objects with a "
                        "string id (competitor_registry_check.py names the problem)")
    return [c["id"] for c in comps]


def _read_summary(bsuk, comps):
    n = len(comps) + (1 if bsuk else 0)
    return (f"{n} report{'' if n == 1 else 's'} ({len(comps)} competitor"
            f"{'' if len(comps) == 1 else 's'}, BSUK profile {'present' if bsuk else 'missing'})")


def render(root, date):
    bsuk, comps = load_reports(root)
    lines = [f"# Competitive gap matrix — {date}", "",
             "Built by `scripts/gap_matrix.py` from `docs/research/competitors/*.json`. Do not edit "
             "by hand: `npm run check:gaps` rebuilds it and fails on any difference.", "",
             f"Competitor reports: {len(comps)} · BSUK profile: "
             f"{'present' if bsuk else 'missing — every BSUK column reads not fetched'}"]
    ids = _registry_ids(root)
    if ids is not None:
        missing = [i for i in ids if i not in comps]
        extra = sorted(i for i in comps if i not in ids)
        lines.append(f"Registry entries: {len(ids)}")
        if missing:
            lines.append(f"No report yet: {', '.join(missing)}")
        if extra:
            lines.append(f"Report with no registry entry: {', '.join(extra)}")
    for dim, title in DIMENSIONS:
        lines += ["", f"## {title}", ""]
        found = rows(bsuk, comps, dim)
        if not found:
            lines.append("_No rows._")
            continue
        lines += ["| Value | Competitors | Not fetched | BSUK has it | Priority |",
                  "|---|---|---|---|---|"]
        lines += [f"| {r.value} | {r.n}/{r.m} | {r.not_fetched} | {r.bsuk_has} | {r.band} |"
                  for r in found]
    lines += ["", "## Priority queue", ""]
    q = queue(bsuk, comps)
    lines += [f"{i}. {r.dimension} `{r.value}` — {r.n}/{r.m} competitors; BSUK: {r.bsuk_has}"
              for i, r in enumerate(q, 1)] or ["_No gaps._"]
    return "\n".join(lines) + "\n"


def _latest(root):
    found = sorted((pathlib.Path(root) / OUT_DIR).glob("gap-matrix-*.md"))
    return found[-1] if found else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return EXIT_USAGE
    root = a.root
    try:
        if a.write:
            date = a.date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                print(f"gaps: --date must be YYYY-MM-DD, got {date!r}")
                return EXIT_USAGE
            out = root / OUT_DIR / f"gap-matrix-{date}.md"
            text = render(root, date)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            print(f"gaps: wrote {out.relative_to(root).as_posix()} from "
                  f"{_read_summary(*load_reports(root))}")
            return EXIT_OK
        latest = _latest(root)
        has_reports = any((root / REPORTS).glob("*.json"))
        if latest is None:
            if has_reports:
                print("gaps: intel reports exist but no gap matrix — run gap_matrix.py --write")
                return EXIT_FAIL
            print("gaps: no reports and no gap matrix yet — nothing to check")
            return EXIT_OK
        date = latest.stem.removeprefix("gap-matrix-")
        if latest.read_text(encoding="utf-8") != render(root, date):
            print(f"gaps: {latest.name} differs from the reports — rerun gap_matrix.py --write "
                  f"--date {date}, never edit it by hand")
            return EXIT_FAIL
        print(f"gaps: {latest.name} matches {_read_summary(*load_reports(root))}")
        return EXIT_OK
    except BadReport as exc:
        print(f"gaps: bad input: {exc}")
        return EXIT_BAD_INPUT


if __name__ == "__main__":
    sys.exit(main())
