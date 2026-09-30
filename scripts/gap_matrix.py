#!/usr/bin/env python3
"""gap_matrix.py — the competitive gap matrix, built from the intel reports, never typed.

  python3 scripts/gap_matrix.py --write [--date YYYY-MM-DD] [--root DIR]
      writes docs/research/gap-matrix-<date>.md (date: today, UTC) · exit 0 · 1 the file
      cannot be written (its path is a directory, or no permission)
  python3 scripts/gap_matrix.py --check [--root DIR]
      validates every report, then rebuilds the newest gap-matrix-YYYY-MM-DD.md and compares
      (older matrices and any other gap-matrix-* name are ignored) · exit 0 same · 1 differs,
      reports exist with no matrix, or no report at all (examined 0 reports, not a pass)
  Every mode: 2 bad usage or an impossible --date · 6 bad input: a report is unreadable,
      breaks schemas/competitor-report.schema.json, or names a city that is not a `city` in
      data/locations.json; data/competitors.json is unreadable or not
      {"competitors": [{"id": "<string>"}, ...]}; the newest matrix cannot be read

Reads docs/research/competitors/*.json (bsuk.json is BSUK's own profile) and, when present,
data/competitors.json to name registry entries with no report. A row's N/M counts only the
competitors whose field was fetched; the ones that were not are their own column. Keywords
are compared case- and space-blind; cities and schema types are compared as written. A
schema type written in two cases (`localbusiness`, `LocalBusiness`) stays two rows, and the
matrix header and the run's output carry a "did you mean" note naming the likely spelling.

Spec: docs/superpowers/specs/2026-09-23-competitor-intel-design.md §6.
"""
import argparse
import datetime
import difflib
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
LOCATIONS = "data/locations.json"
OUT_DIR = "docs/research"
MATRIX_NAME = re.compile(r"gap-matrix-(\d{4}-\d{2}-\d{2})\.md")
DIMENSIONS = (("keywords", "Keyword gaps"), ("page_types", "Page-type gaps"),
              ("cities", "City gaps"), ("schema_types", "Schema gaps"))
QUEUE_LEN = 10
DIFF_LINES = 5
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


def _oneline(v):
    return re.sub(r"\s+", " ", v).strip()


def _cell(v):
    """A value as one markdown table cell: one line, pipes escaped. Backslashes directly
    before a pipe are doubled first, so a value's own `\\|` cannot turn the escape into an
    escaped backslash followed by a real pipe, which would end the cell early."""
    return re.sub(r"(\\*)\|", lambda m: m.group(1) * 2 + "\\|", _oneline(v))


def _code(v):
    """A value as one inline code span that survives backticks inside it."""
    v = _oneline(v)
    run = max((len(m) for m in re.findall(r"`+", v)), default=0)
    fence, pad = "`" * (run + 1), " " if run else ""
    return f"{fence}{pad}{v}{pad}{fence}"


def _is_date(s):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return False
    try:
        datetime.date.fromisoformat(s)
    except ValueError:
        return False
    return True


def values(report, dim):
    """The set a report holds for one dimension, or None when that field was not fetched."""
    field = report[dim]
    if field["status"] != "ok":
        return None
    if dim == "page_types":
        return {k for k, count in field["values"].items() if count > 0}
    if dim == "keywords":
        return {_norm(v) for v in field["values"]}
    if dim == "schema_types":
        return {v.strip() for v in field["values"]}
    return set(field["values"])


def _known_cities(root):
    path = pathlib.Path(root) / LOCATIONS
    try:
        rows_ = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows_, list):
            raise ValueError("expected a list of rows")
        return {row["city"] for row in rows_}
    except (OSError, ValueError, UnicodeDecodeError, KeyError, TypeError) as exc:
        raise BadReport(f"{LOCATIONS} unreadable ({type(exc).__name__}: {exc}); it is needed "
                        "to check the reports' cities")


def _check_cities(root, reports):
    named = {p: r["cities"]["values"] for p, r in reports if r["cities"]["status"] == "ok"
             and r["cities"]["values"]}
    if not named:
        return
    known = _known_cities(root)
    folded = {c.lower(): c for c in known}
    for path, cities in named.items():
        for city in cities:
            if city in known:
                continue
            hint = folded.get(city.lower())
            raise BadReport(f"{path.name}: city {city!r} is not a city in {LOCATIONS}"
                            + (f" — did you mean {hint!r}?" if hint else ""))


def load_reports(root=ROOT):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    loaded = []
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
        loaded.append((path, data))
    _check_cities(root, loaded)
    bsuk = next((d for _, d in loaded if d["id"] == "bsuk"), None)
    comps = {d["id"]: d for _, d in loaded if d["id"] != "bsuk"}
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


def case_hints(bsuk, comps):
    """A note per schema type spelt in another case than a spelling some report uses.
    Schema types stay case-exact (spec §16.6), so the two are counted apart; the note names
    the likely spelling: BSUK's, else the one most reports use, else the first in sort order."""
    users = {}  # spelling -> the report ids that use it, BSUK first
    for rid, report in ([("bsuk", bsuk)] if bsuk else []) + sorted(comps.items()):
        for v in sorted(values(report, "schema_types") or ()):
            users.setdefault(v, []).append(rid)
    groups = {}
    for v in users:
        groups.setdefault(v.lower(), []).append(v)
    out = []
    for spellings in groups.values():
        if len(spellings) < 2:
            continue
        best = min(spellings, key=lambda v: ("bsuk" not in users[v], -len(users[v]), v))
        for v in sorted(spellings):
            if v != best:
                out.append(f"schema type {_oneline(v)!r} ({', '.join(users[v])}) differs only in "
                           f"case from {_oneline(best)!r} ({', '.join(users[best])}) — did you "
                           f"mean {_oneline(best)!r}? Schema types are compared as written, so "
                           "the two are counted apart.")
    return sorted(out)


def _registry_ids(root):
    """Registry ids in order, deduped, without bsuk; None when there is no registry."""
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
    return [i for i in dict.fromkeys(c["id"] for c in comps) if i != "bsuk"]


def summary(bsuk, comps):
    n = len(comps) + (1 if bsuk else 0)
    return (f"{n} report{'' if n == 1 else 's'} ({len(comps)} competitor"
            f"{'' if len(comps) == 1 else 's'}, BSUK profile {'present' if bsuk else 'missing'})")


def render(root, date, reports=None):
    """The matrix text. `reports` is load_reports(root)'s result, loaded here when omitted."""
    bsuk, comps = reports if reports is not None else load_reports(root)
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
    lines += [f"Note: {h}" for h in case_hints(bsuk, comps)]
    for dim, title in DIMENSIONS:
        lines += ["", f"## {title}", ""]
        found = rows(bsuk, comps, dim)
        if not found:
            lines.append("_No rows._")
            continue
        lines += ["| Value | Competitors | Not fetched | BSUK has it | Priority |",
                  "|---|---|---|---|---|"]
        lines += [f"| {_cell(r.value)} | {r.n}/{r.m} | {r.not_fetched} | {r.bsuk_has} | {r.band} |"
                  for r in found]
    lines += ["", "## Priority queue", ""]
    q = queue(bsuk, comps)
    lines += [f"{i}. {r.dimension} {_code(r.value)} — {r.n}/{r.m} competitors; BSUK: {r.bsuk_has}"
              for i, r in enumerate(q, 1)] or ["_No gaps._"]
    return "\n".join(lines) + "\n"


def _latest(root):
    found = sorted(p for p in (pathlib.Path(root) / OUT_DIR).glob("gap-matrix-*.md")
                   if (m := MATRIX_NAME.fullmatch(p.name)) and _is_date(m.group(1)))
    return found[-1] if found else None


def _first_difference(expected, found):
    diff = difflib.unified_diff(expected.splitlines(), found.splitlines(),
                                "expected", "found", n=0, lineterm="")
    body = [ln for ln in diff if not ln.startswith(("---", "+++"))]
    return body[:DIFF_LINES]


def _print_hints(reports):
    for h in case_hints(*reports):
        print(f"gaps: note: {h}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    try:
        a = ap.parse_args(argv)
    except SystemExit as exc:
        return EXIT_OK if exc.code == 0 else EXIT_USAGE
    root = a.root
    try:
        if a.write:
            date = a.date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
            if not _is_date(date):
                print(f"gaps: --date must be a real YYYY-MM-DD date, got {date!r}")
                return EXIT_USAGE
            reports = load_reports(root)
            text = render(root, date, reports)
            out = root / OUT_DIR / f"gap-matrix-{date}.md"
            rel = out.relative_to(root).as_posix()
            try:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text, encoding="utf-8")
            except OSError as exc:
                print(f"gaps: cannot write {rel}: {exc.strerror or exc}")
                return EXIT_FAIL
            _print_hints(reports)
            print(f"gaps: wrote {rel} from {summary(*reports)}")
            return EXIT_OK
        reports = load_reports(root)
        _print_hints(reports)
        if not (reports[0] or reports[1]):
            # tests/py/test_gates_refuse_nothing.py: the intel reports exist since the competitor
            # bridge build, so none at all is a lost input, whatever matrix sits beside it.
            print(f"gaps: examined 0 reports in {REPORTS} — not a pass")
            return EXIT_FAIL
        latest = _latest(root)
        if latest is None:
            print("gaps: intel reports exist but no gap matrix — run gap_matrix.py --write")
            return EXIT_FAIL
        date = MATRIX_NAME.fullmatch(latest.name).group(1)
        try:
            found = latest.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"gaps: bad input: {latest.name} cannot be read: {exc}")
            return EXIT_BAD_INPUT
        expected = render(root, date, reports)
        if found != expected:
            print(f"gaps: {latest.name} differs from the reports — rerun gap_matrix.py --write "
                  f"--date {date}, never edit it by hand. First difference:")
            for ln in _first_difference(expected, found):
                print(f"gaps:   {ln}")
            return EXIT_FAIL
        print(f"gaps: {latest.name} matches {summary(*reports)}")
        return EXIT_OK
    except BadReport as exc:
        print(f"gaps: bad input: {exc}")
        return EXIT_BAD_INPUT


if __name__ == "__main__":
    sys.exit(main())
