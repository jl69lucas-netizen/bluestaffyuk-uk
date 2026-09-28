#!/usr/bin/env python3
"""Freeze one city's component picks: the canvas Send snapshot → the picks record and the pool.

Spec docs/superpowers/specs/2026-09-27-london-component-design-pass-design.md §2 ("Freeze") and
§3.4. When every component on a city's canvas has a pick, the picks are saved in
data/design/city-picks/<slug>.json (schemas/city-picks.schema.json) and every variant of that
canvas the city did NOT pick joins data/design/city-pool.json, open to a later city. A pool
entry this city picked (a variant another city left in the pool) leaves it. The rule-16 city
gate (scripts/pageboard.py city_rule16_findings) then judges both files.

    python3 scripts/freeze_city_picks.py --snapshot docs/research/london-components/picks-2026-09-27.json \\
        --slug blue-staffy-puppies-london --canvas london

Refuses (exit 1, nothing written) while any component's pick is missing or "redesign".
Idempotent: freezing the same snapshot twice writes the same bytes.
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from city_components import COMPONENT_IDS, ROOT, VARIANT_IDS, variant_key  # noqa: E402
import pageboard as PB  # noqa: E402

PICKS_DIR = ROOT / "data" / "design" / "city-picks"
POOL = ROOT / "data" / "design" / "city-pool.json"
#: The schema's `approved_at` has no fraction of a second; the canvas stamps milliseconds.
_STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?Z$")


class FreezeError(ValueError):
    """The snapshot cannot be frozen yet (a component has no final pick)."""


def picks_record(snapshot, slug, canvas):
    """The data/design/city-picks/<slug>.json record for one canvas Send snapshot."""
    got = snapshot.get("picks") or {}
    missing = [c for c in COMPONENT_IDS if (got.get(c) or {}).get("pick") not in VARIANT_IDS]
    if missing:
        raise FreezeError("no final pick (a, b or c) for: " + ", ".join(missing))
    m = _STAMP.match(snapshot.get("at", ""))
    if not m:
        raise FreezeError(f"the snapshot's `at` is not a UTC stamp: {snapshot.get('at')!r}")
    rec = {
        "slug": slug,
        "canvas": canvas,
        "canvas_url": snapshot["canvas"],
        "approved_at": m.group(1) + "Z",
        "picks": {c: variant_key(canvas, c, got[c]["pick"]) for c in COMPONENT_IDS},
    }
    PB._validate(rec, "city-picks.schema.json")
    return rec


def pooled(pool, record, canvas):
    """`pool` with this canvas's unpicked variants added and this city's picks removed."""
    picked = set(record["picks"].values())
    out = {"_comment": pool["_comment"], "available": {}}
    for c in COMPONENT_IDS:
        keep = [k for k in pool["available"].get(c, []) if k not in picked]
        new = [variant_key(canvas, c, v) for v in VARIANT_IDS
               if variant_key(canvas, c, v) not in picked]
        out["available"][c] = sorted(set(keep) | set(new))
    PB._validate(out, "city-pool.schema.json")
    return out


def _dump(doc):
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Freeze one city's component picks.")
    ap.add_argument("--snapshot", required=True, help="the canvas Send snapshot (JSON)")
    ap.add_argument("--slug", required=True, help="the city page's slug, e.g. blue-staffy-puppies-london")
    ap.add_argument("--canvas", required=True, help="the canvas key, e.g. london")
    ap.add_argument("--pool", default=str(POOL))
    ap.add_argument("--out-dir", default=str(PICKS_DIR))
    a = ap.parse_args(argv)
    snap = json.loads(pathlib.Path(a.snapshot).read_text(encoding="utf-8"))
    try:
        rec = picks_record(snap, a.slug, a.canvas)
    except FreezeError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    pool_path = pathlib.Path(a.pool)
    pool = pooled(json.loads(pool_path.read_text(encoding="utf-8")), rec, a.canvas)
    out = pathlib.Path(a.out_dir) / f"{a.slug}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_dump(rec), encoding="utf-8")
    pool_path.write_text(_dump(pool), encoding="utf-8")
    print(f"{out}: 15 picks; {pool_path}: {sum(len(v) for v in pool['available'].values())} pooled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
