"""The homepage's H-HM2 hero is the arrangement the breeder picked: four photographs and figure
tiles (Known Issue 33, first half; user ruling R11, 2026-09-24).

H-HM2 is "four-photo mosaic above the copy, figure tiles beneath it", but the record named one
photograph and no figures, so `Hero` rendered its fallback — a single photo, no ledge — on the
board and on the page. The record now names four existing photographs (working rule 11: the
first is the migrated page's primary image with its alt, the other three are photographs the
page already shows, repeated with an empty alt) and figures of the page's own.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pageboard as PB  # noqa: E402

RECORD = json.loads((ROOT / "data/boards/index.json").read_text(encoding="utf-8"))
SECTIONS = {s["id"]: s for s in RECORD["sections"]}
ASSETS = {a["slot"]: a for a in RECORD["assets"]}


def test_the_hero_names_four_existing_photographs_the_migrated_hero_first():
    slots = [i["slot"] for i in SECTIONS["top"]["images"]]
    assert len(slots) == 4 and len(set(slots)) == 4, slots
    assert slots[0] == "home-hero", slots
    for s in slots:
        a = ASSETS[s]
        assert a["file"].startswith("/images/") and (ROOT / "public" / a["file"][1:]).is_file(), s


def test_the_hero_figures_are_sourced_and_not_the_counters():
    hero = SECTIONS["top"].get("stats") or []
    assert len(hero) >= 2, hero
    for row in hero:
        values = PB.resolve_stat_sources(row)
        assert PB.figure_matches(row["n"], values), (row, values)
    counter = {r["n"] for r in SECTIONS["at-a-glance"]["stats"]}
    assert not counter & {r["n"] for r in hero}, "a figure printed twice, in the hero and the counter"


def test_the_built_hero_shows_four_tiles_and_the_figures():
    page = ROOT / "dist" / "index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    html = page.read_text(encoding="utf-8")
    hero = re.search(r'<section[^>]*class="kit-hero[^"]*"[^>]*>(.*?)</section>', html, re.S)
    assert hero, "no kit hero on the built homepage"
    tiles = re.findall(r"<img\b[^>]*>", re.search(r'<ul class="mosaic pic[^"]*"[^>]*>(.*?)</ul>',
                                                   hero.group(1), re.S).group(1))
    assert len(tiles) == 4, len(tiles)
    # An empty alt is serialised as the bare attribute `alt`, which a browser reads as "".
    alts = [re.search(r'\balt(?:="([^"]*)")?[\s>]', t).group(1) or "" for t in tiles]
    assert alts[0] == ASSETS["home-hero"]["alt"] and alts[1:] == ["", "", ""], alts
    figures = re.findall(r"<strong[^>]*>([^<]+)</strong>", hero.group(1))
    assert figures == [r["n"] for r in SECTIONS["top"]["stats"]], figures
