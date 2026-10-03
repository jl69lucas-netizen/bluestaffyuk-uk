"""scripts/city_must_differ.py — the must-differ inventory (Plan 1, Task 2)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import city_must_differ as M  # noqa: E402
import pageboard as PB  # noqa: E402
from city_components import COMPONENT_IDS  # noqa: E402


def test_the_parse_finds_every_shape_and_every_per_page_style():
    defs = M.style_defs()
    assert len(defs) == 15, sorted(defs)
    assert len(defs["hero"]) == 21 and len(defs["stats"]) == 21  # S1–S3 + 6 families × 3
    assert all(len(v) == 3 for k, v in defs.items() if k not in ("hero", "stats"))
    ids = [sid for sid, _n, _l in defs["hero"]]
    assert ids[:3] == ["S1", "S2", "S3"] and "H-GD3" in ids and "H-BL3" in ids


def test_canonical_axes_read_the_structure_not_the_paint():
    defs = {sid: (shape, l) for shape, rows in M.style_defs().items() for sid, _n, l in rows
            if sid.startswith(("H-", "C-"))}
    assert M.canonical_axes(*defs["H-GD3"]) == {"layout": "panel", "media": "left",
                                                "density": None, "framing": "card"}
    assert M.canonical_axes(*defs["C-FS2"]) == {"layout": "ring", "media": "none",
                                                "density": None, "framing": "card"}
    assert M.canonical_axes("standard", {"frame": "band", "columns": 2, "aside": "infocard"})["layout"] \
        == "cols-2+infocard"
    assert M.canonical_axes("dial", {"ring": "hidden", "marks": "number", "list": "rail"})["layout"] \
        == "ring-hidden+number+rail"


def test_worn_by_uses_the_pick_in_force():
    boards = {"a": {"sections": [{"id": "top", "shape": "hero", "options": {"pick": "H-GD2"}}],
                    "approval": {"picks": {"top": "H-GD1"}}},
              "b": {"sections": [{"id": "top", "shape": "hero", "options": {"pick": "H-GD2"}}]}}
    assert M.worn_by(boards, {"a", "b"}) == {("hero", "H-GD1"): ["a"], ("hero", "H-GD2"): ["b"]}
    assert M.worn_by(boards, {"b"}) == {("hero", "H-GD2"): ["b"]}  # only built pages count


def test_the_inventory_covers_the_fifteen_in_order():
    inv = M.inventory()
    assert list(inv) == list(COMPONENT_IDS)
    counts = {k: len(v) for k, v in inv.items()}
    assert counts["hero"] == 21 and counts["counter-strip"] == 21
    assert counts["jump-links"] == 6 and counts["contents-list"] == 1 and counts["newsletter"] == 0
    assert inv["contents-list"][0]["id"] == "PageNav"


def test_every_built_pages_hero_and_counter_are_listed_as_worn():
    inv = M.inventory()
    boards = PB.load_all_boards()
    for slug in sorted(PB.rebuilt_slugs()):
        b = boards[slug]
        for sec in b["sections"]:
            comp = {"hero": "hero", "stats": "counter-strip"}.get(sec["shape"])
            if not comp:
                continue
            pick = PB.pick_in_force(b, sec["id"])
            if pick is None and sec.get("component"):
                # A project 5 page wears a city-kit component from its own canvas (London,
                # 075355ba), not a boardStyles style, so it has no inventory row; check:canvas
                # holds that variant to differ from every row. The kit file must exist.
                kit = [c for c in (sec.get("options") or {}).get("candidates") or []]
                assert kit and (ROOT / "src/components/kit" / f"{kit[0]}.astro").is_file(), \
                    (slug, comp, sec["component"])
                continue
            rows = [r for r in inv[comp] if r["id"] == pick]
            assert rows and slug in rows[0]["used_by"], (slug, comp, pick)


def test_the_committed_files_are_current(capsys):
    assert M.main(["--check"]) == 0, capsys.readouterr().out
    assert "15 components" in capsys.readouterr().out
