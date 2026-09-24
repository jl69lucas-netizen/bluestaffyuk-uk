"""The three guides no longer share a hero (Known Issues 30 and 35, user ruling R13, 2026-09-24).

All three picked H-GD3, the interior-guide family's text-led panel, which broke working rule
16 between them. All three went back to the board. Measured at 1280 with the self-hosted faces,
H-GD1 (the editorial split, never rendered on a page before) fits only the health guide, H-GD2
fits the breed guide and the buying guide, and H-GD3 fits all three — so the three can end on
three different heroes, and the recommended answer is health H-GD1, breed guide H-GD3, buying
guide H-GD2.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
GUIDES = ("blue-staffy-health-uk", "uk-staffordshire-bull-terrier-guide",
          "uk-blue-staffy-puppy-buying-guide")


def hero_in_force(slug):
    """`pickedStyle()`'s order: the live approval, the section's own pick, the carried one."""
    rec = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text(encoding="utf-8"))
    top = next(s for s in rec["sections"] if s["shape"] == "hero")
    for source in ((rec.get("approval") or {}).get("picks") or {},
                   {top["id"]: top["options"].get("pick")},
                   (rec.get("approval_previous") or {}).get("picks") or {}):
        if source.get(top["id"]):
            return source[top["id"]]
    return None


def test_the_three_guides_take_three_different_heroes():
    picks = {slug: hero_in_force(slug) for slug in GUIDES}
    assert sorted(picks.values()) == ["H-GD1", "H-GD2", "H-GD3"], picks


def test_each_guides_hero_is_on_its_own_menu():
    for slug in GUIDES:
        rec = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text(encoding="utf-8"))
        top = next(s for s in rec["sections"] if s["shape"] == "hero")
        assert top["styles"] == ["H-GD1", "H-GD2", "H-GD3"], (slug, top["styles"])
        assert hero_in_force(slug) in top["styles"], slug
