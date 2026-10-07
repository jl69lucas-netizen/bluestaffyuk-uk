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
`--not-used video,puppy-cards` records those components as "none": the page's approved outline
has no section for them, so they need no pick and pool nothing (the Manchester page run, Phase F
gap G4). A picked pool copy (meta.json `from_pool`) takes its source out of the pool (gap G5).
Idempotent: freezing the same snapshot twice writes the same bytes.
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from city_components import (CANVAS_ROOT, COMPONENT_IDS, NOT_USED, ROOT, VARIANT_IDS,  # noqa: E402
                             variant_key)
import pageboard as PB  # noqa: E402

PICKS_DIR = ROOT / "data" / "design" / "city-picks"
POOL = ROOT / "data" / "design" / "city-pool.json"
#: The schema's `approved_at` has no fraction of a second; the canvas stamps milliseconds.
_STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?Z$")


class FreezeError(ValueError):
    """The snapshot cannot be frozen yet (a component has no final pick)."""


def picks_record(snapshot, slug, canvas, not_used=()):
    """The data/design/city-picks/<slug>.json record for one canvas Send snapshot.

    `not_used` names the components the page's approved outline has no section for; each is
    recorded as "none" (city_components.NOT_USED) and needs no pick (gap G4)."""
    not_used = tuple(not_used)
    unknown = [c for c in not_used if c not in COMPONENT_IDS]
    if unknown:
        raise FreezeError("--not-used names no city component: " + ", ".join(unknown))
    got = snapshot.get("picks") or {}
    missing = [c for c in COMPONENT_IDS
               if c not in not_used and (got.get(c) or {}).get("pick") not in VARIANT_IDS]
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
        "picks": {c: NOT_USED if c in not_used else variant_key(canvas, c, got[c]["pick"])
                  for c in COMPONENT_IDS},
    }
    PB._validate(rec, "city-picks.schema.json")
    return rec


def pool_source(key, canvas_root=None):
    """The pool variant a canvas variant was copied from (its meta.json row's `from_pool`,
    Phase F ruling 4), or None for a new design or a variant with no meta row."""
    city, component, variant = key.split("/")
    meta = (CANVAS_ROOT if canvas_root is None else pathlib.Path(canvas_root)) / city / component / "meta.json"
    if not meta.is_file():
        return None
    row = (json.loads(meta.read_text(encoding="utf-8")).get("variants") or {}).get(variant) or {}
    return row.get("from_pool")


def pooled(pool, record, canvas, canvas_root=None):
    """`pool` with this canvas's unpicked variants added and this city's picks removed.

    A picked pool copy (a variant whose meta row says `from_pool`) takes its source out of the
    pool too, and an unpicked copy never enters it: its source is already there (gap G5). A
    component the page does not use ("none") adds nothing and removes nothing (gap G4)."""
    picked = {k for k in record["picks"].values() if k != NOT_USED}
    sources = {pool_source(k, canvas_root) for k in picked} - {None}
    out = {"_comment": pool["_comment"], "available": {}}
    for c in COMPONENT_IDS:
        keep = [k for k in pool["available"].get(c, []) if k not in picked and k not in sources]
        new = [] if record["picks"][c] == NOT_USED else [
            k for k in (variant_key(canvas, c, v) for v in VARIANT_IDS)
            if k not in picked and pool_source(k, canvas_root) is None]
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
    ap.add_argument("--not-used", default="",
                    help='comma list of components the outline has no section for, recorded "none" '
                         "(e.g. video,puppy-cards)")
    ap.add_argument("--pool", default=str(POOL))
    ap.add_argument("--out-dir", default=str(PICKS_DIR))
    a = ap.parse_args(argv)
    snap = json.loads(pathlib.Path(a.snapshot).read_text(encoding="utf-8"))
    try:
        rec = picks_record(snap, a.slug, a.canvas,
                           not_used=[c.strip() for c in a.not_used.split(",") if c.strip()])
    except FreezeError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    pool_path = pathlib.Path(a.pool)
    pool = pooled(json.loads(pool_path.read_text(encoding="utf-8")), rec, a.canvas)
    out = pathlib.Path(a.out_dir) / f"{a.slug}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_dump(rec), encoding="utf-8")
    pool_path.write_text(_dump(pool), encoding="utf-8")
    used = sum(1 for k in rec["picks"].values() if k != NOT_USED)
    print(f"{out}: {used} picks, {len(rec['picks']) - used} not used; {pool_path}: {sum(len(v) for v in pool['available'].values())} pooled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
