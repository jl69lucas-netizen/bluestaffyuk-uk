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
import re
from html import unescape

import pytest

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


# ── A chips ledge renders the record's chips ──────────────────────────────────────────────────
#
# H-GD2's ledge is `chips`, and `Hero` renders the chip row only when the page hands it the
# `chips` prop. The buying guide took H-GD2 on its re-board without passing it, so its built
# hero showed no chip row while the board's H-GD2 frame showed "What to ask · What to check ·
# What it costs" (R13 review). This holds the built hero to the ledge its pick names.

def _style_ledges():
    """Each hero style's ledge, as `src/lib/boardStyles.ts` defines it."""
    src = (ROOT / "src/lib/boardStyles.ts").read_text(encoding="utf-8")
    found = re.findall(r"def\('(H-[A-Z]+\d)',[^{]*\{([^}]*)\}", src)
    return {sid: (re.search(r"ledge:\s*'(\w+)'", body) or [None, None])[1] for sid, body in found}


def _built_hero(slug):
    page = ROOT / "dist" / slug / "index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    html = page.read_text(encoding="utf-8")
    m = re.search(r'<section class="kit-hero"[^>]*>.*?</section>', html, flags=re.S)
    assert m, f"{slug}: no .kit-hero in the built page"
    return m.group(0)


@pytest.mark.parametrize("slug", GUIDES)
def test_a_chips_ledge_hero_renders_the_records_chips_as_its_row(slug):
    ledges = _style_ledges()
    pick = hero_in_force(slug)
    assert pick in ledges, (slug, pick)
    rec = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text(encoding="utf-8"))
    top = next(s for s in rec["sections"] if s["shape"] == "hero")
    chips = [c if isinstance(c, str) else c["text"] for c in (top.get("hero") or {}).get("chips", [])]
    hero = _built_hero(slug)
    assert f'data-hero-ledge="{ledges[pick]}"' in hero, (slug, pick, ledges[pick])
    row = re.search(r'<ul class="chips"[^>]*>(.*?)</ul>', hero, flags=re.S)
    if ledges[pick] == "chips":
        assert chips, f"{slug}: {pick} has a chips ledge but the record gives the hero no chips"
        assert row, f"{slug}: {pick} names a chips ledge and the built hero has no chip row"
        rendered = [unescape(t).strip() for t in re.findall(r"<li[^>]*>(.*?)</li>", row.group(1), flags=re.S)]
        assert rendered == chips, (slug, rendered, chips)
    else:
        assert row is None, f"{slug}: {pick}'s ledge is {ledges[pick]}, yet the hero renders a chip row"
