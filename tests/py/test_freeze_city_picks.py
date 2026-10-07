"""Freezing a city's canvas picks (the London component design pass, Plan 2 Task 1; spec §2
"Freeze" and §3.4).

`scripts/freeze_city_picks.py` turns the canvas Send snapshot the user made into
data/design/city-picks/<slug>.json and moves every unpicked variant of that canvas into
data/design/city-pool.json, so the rule-16 city gate (scripts/pageboard.py
city_rule16_findings) judges the real files, not an empty folder.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import freeze_city_picks as F  # noqa: E402
import pageboard as PB  # noqa: E402
from city_components import COMPONENT_IDS  # noqa: E402

CANVAS_URL = "https://claude.ai/artifact/EHMKbn9kV3qcfJfPrJhhXN"


def snapshot(**over):
    picks = {c: {"pick": "a", "note": ""} for c in COMPONENT_IDS}
    picks["hero"] = {"pick": "b", "note": ""}
    doc = {"canvas": CANVAS_URL, "submission": "s-2026-09-27T20-49-24-674Z",
           "at": "2026-09-27T20:49:24.675Z", "notes": "", "picks": picks}
    doc.update(over)
    return doc


def empty_pool():
    return {"_comment": "x", "available": {c: [] for c in COMPONENT_IDS}}


def test_the_picks_record_names_one_variant_per_component():
    rec = F.picks_record(snapshot(), slug="blue-staffy-puppies-london", canvas="london")
    assert rec["slug"] == "blue-staffy-puppies-london"
    assert rec["canvas"] == "london"
    assert rec["canvas_url"] == CANVAS_URL
    # The schema's pattern has no fraction of a second: the Send stamp is cut to the second.
    assert rec["approved_at"] == "2026-09-27T20:49:24Z"
    assert rec["picks"]["hero"] == "london/hero/b"
    assert rec["picks"]["tables"] == "london/tables/a"
    assert list(rec["picks"]) == list(COMPONENT_IDS)
    PB._validate(rec, "city-picks.schema.json")


def test_a_redesign_or_missing_pick_refuses_to_freeze():
    snap = snapshot()
    snap["picks"]["video"] = {"pick": "redesign", "note": "try again"}
    with pytest.raises(F.FreezeError, match="video"):
        F.picks_record(snap, slug="blue-staffy-puppies-london", canvas="london")
    snap = snapshot()
    del snap["picks"]["newsletter"]
    with pytest.raises(F.FreezeError, match="newsletter"):
        F.picks_record(snap, slug="blue-staffy-puppies-london", canvas="london")


def test_the_pool_gains_the_thirty_unpicked_variants_and_loses_nothing_else():
    rec = F.picks_record(snapshot(), slug="blue-staffy-puppies-london", canvas="london")
    pool = F.pooled(empty_pool(), rec, canvas="london")
    assert sum(len(v) for v in pool["available"].values()) == 30
    assert pool["available"]["hero"] == ["london/hero/a", "london/hero/c"]
    assert pool["available"]["tables"] == ["london/tables/b", "london/tables/c"]
    PB._validate(pool, "city-pool.schema.json")


def test_a_later_citys_freeze_removes_its_picks_from_the_pool():
    """A pool entry a later city picks leaves the pool: city_pool_findings refuses a picked
    entry, so a freeze that left it there would turn the gate red on its own output."""
    pool = empty_pool()
    pool["available"]["hero"] = ["london/hero/a", "london/hero/c"]
    snap = snapshot()
    rec = F.picks_record(snap, slug="blue-staffy-puppies-leeds", canvas="leeds")
    rec["picks"]["hero"] = "london/hero/a"
    out = F.pooled(pool, rec, canvas="leeds")
    assert "london/hero/a" not in out["available"]["hero"]
    assert "london/hero/c" in out["available"]["hero"]


def test_freezing_twice_is_the_same_files(tmp_path):
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(snapshot()))
    pool_path = tmp_path / "pool.json"
    pool_path.write_text(json.dumps(empty_pool()))
    out_dir = tmp_path / "city-picks"
    args = ["--snapshot", str(snap_path), "--slug", "blue-staffy-puppies-london", "--canvas", "london",
            "--pool", str(pool_path), "--out-dir", str(out_dir)]
    assert F.main(args) == 0
    first = (out_dir / "blue-staffy-puppies-london.json").read_text(), pool_path.read_text()
    assert F.main(args) == 0
    assert ((out_dir / "blue-staffy-puppies-london.json").read_text(), pool_path.read_text()) == first


def test_the_real_london_freeze_is_on_disk_and_passes_the_city_gate():
    """The real files: London's picks match the user's Send snapshot, the pool holds the
    thirty variants London did not pick, and the rule-16 city gate is green on both."""
    snap = json.loads((ROOT / "docs/research/london-components/picks-2026-09-27.json").read_text())
    rec = json.loads((ROOT / "data/design/city-picks/blue-staffy-puppies-london.json").read_text())
    assert rec == F.picks_record(snap, slug="blue-staffy-puppies-london", canvas="london")
    picks = PB.load_city_picks()
    pool = PB.load_city_pool()
    assert sum(len(v) for v in pool["available"].values()) == 30
    assert PB.city_pool_findings(pool, picks, PB.canvas_axes) == []
    md = json.loads(PB.CITY_MUST_DIFFER.read_text(encoding="utf-8"))["components"]
    assert PB.city_pick_findings("blue-staffy-puppies-london", picks, md, PB.canvas_axes) == []


# ── G4 and G5 (the Manchester page run, Phase F Task 19) ───────────────────────────────────
#
# G4: a city whose outline has no section for a component (Manchester: no video, no puppy
# cards) records that component's pick as "none"; the record must be able to hold every answer
# (lessons 12). G5: a pool variant enters a later city's canvas as a refreshed copy whose
# meta.json row records `from_pool: <city>/<component>/<v>`; picking the copy takes its source
# out of the pool, and an unpicked copy never enters the pool (its source is already there).

def snapshot_without(*components):
    snap = snapshot()
    for c in components:
        del snap["picks"][c]
    return snap


def test_a_component_the_page_does_not_use_is_recorded_none():
    rec = F.picks_record(snapshot_without("video", "puppy-cards"), slug="blue-staffy-puppies-leeds",
                         canvas="leeds", not_used=("video", "puppy-cards"))
    assert rec["picks"]["video"] == "none"
    assert rec["picks"]["puppy-cards"] == "none"
    assert rec["picks"]["hero"] == "leeds/hero/b"
    assert list(rec["picks"]) == list(COMPONENT_IDS)
    PB._validate(rec, "city-picks.schema.json")


def test_not_used_still_refuses_a_redesign_or_an_unknown_component():
    snap = snapshot_without("video", "puppy-cards")
    snap["picks"]["tables"] = {"pick": "redesign", "note": "again"}
    with pytest.raises(F.FreezeError, match="tables"):
        F.picks_record(snap, slug="blue-staffy-puppies-leeds", canvas="leeds",
                       not_used=("video", "puppy-cards"))
    with pytest.raises(F.FreezeError, match="carousel"):
        F.picks_record(snapshot(), slug="blue-staffy-puppies-leeds", canvas="leeds",
                       not_used=("carousel",))


def test_the_cli_reads_not_used_as_a_comma_list_and_pools_nothing_for_it(tmp_path):
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(snapshot_without("video", "puppy-cards")))
    pool_path = tmp_path / "pool.json"
    pool_path.write_text(json.dumps(empty_pool()))
    out_dir = tmp_path / "city-picks"
    assert F.main(["--snapshot", str(snap_path), "--slug", "blue-staffy-puppies-leeds",
                   "--canvas", "leeds", "--pool", str(pool_path), "--out-dir", str(out_dir),
                   "--not-used", "video,puppy-cards"]) == 0
    rec = json.loads((out_dir / "blue-staffy-puppies-leeds.json").read_text())
    assert rec["picks"]["video"] == rec["picks"]["puppy-cards"] == "none"
    pool = json.loads(pool_path.read_text())
    # a component the page does not use has no variants on its canvas, so none is pooled
    assert pool["available"]["video"] == [] and pool["available"]["puppy-cards"] == []
    assert sum(len(v) for v in pool["available"].values()) == 26


def _canvas_with_pool_copy(root, canvas="leeds", component="hero", source="london/hero/a"):
    meta = root / canvas / component / "meta.json"
    meta.parent.mkdir(parents=True)
    meta.write_text(json.dumps({"component": component, "variants": {
        "a": {"axes": {}}, "b": {"axes": {}}, "c": {"axes": {}, "from_pool": source}}}))
    return root


def test_picking_a_pool_copy_takes_its_source_out_of_the_pool(tmp_path):
    root = _canvas_with_pool_copy(tmp_path)
    pool = empty_pool()
    pool["available"]["hero"] = ["london/hero/a", "london/hero/c"]
    rec = F.picks_record(snapshot(), slug="blue-staffy-puppies-leeds", canvas="leeds")
    rec["picks"]["hero"] = "leeds/hero/c"
    out = F.pooled(pool, rec, canvas="leeds", canvas_root=root)
    assert out["available"]["hero"] == ["leeds/hero/a", "leeds/hero/b", "london/hero/c"]


def test_an_unpicked_pool_copy_never_enters_the_pool(tmp_path):
    root = _canvas_with_pool_copy(tmp_path)
    pool = empty_pool()
    pool["available"]["hero"] = ["london/hero/a", "london/hero/c"]
    rec = F.picks_record(snapshot(), slug="blue-staffy-puppies-leeds", canvas="leeds")
    assert rec["picks"]["hero"] == "leeds/hero/b"
    out = F.pooled(pool, rec, canvas="leeds", canvas_root=root)
    assert out["available"]["hero"] == ["leeds/hero/a", "london/hero/a", "london/hero/c"]


def test_a_none_pick_is_not_a_pool_key_and_never_leaves_the_pool_by_accident():
    pool = empty_pool()
    pool["available"]["video"] = ["london/video/a", "london/video/b"]
    rec = F.picks_record(snapshot_without("video"), slug="blue-staffy-puppies-leeds",
                         canvas="leeds", not_used=("video",))
    out = F.pooled(pool, rec, canvas="leeds")
    assert out["available"]["video"] == ["london/video/a", "london/video/b"]
