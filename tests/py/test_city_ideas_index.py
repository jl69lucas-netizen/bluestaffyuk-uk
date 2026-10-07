"""docs/research/<city>-components/ideas-index.md — each city component pass's ideas index
(London: Plan 1, Task 1; Manchester: docs/superpowers/plans/2026-10-07-manchester-page-run.md
Task 21). The screenshots and the two idea-sheet folders live OUTSIDE the repo; the index is the
repo's only record of them. It must cover the city's components in city-page order, cite only
files that exist (checked only where the folder is present, so CI without the user's Mac skips
cleanly), and index every PNG in the idea folders the pass opened.

Manchester adds three rules from Phase F of its plan: the hero cites the five breeder sheets
ruling 3 names; the counter strip cites breeder sheets only; and every other component names its
two London pool variants (data/design/city-pool.json) with the name and axes London's meta.json
gives them, and cites every idea source those variants carry, so a refreshed pool copy passes
scripts/check_city_canvas.py's idea-source rule."""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from city_components import AXES, CANVAS_ROOT, COMPONENT_IDS  # noqa: E402

REFS = pathlib.Path("/Users/apple/Downloads/BSUK/BSUK-refs/london")
MFS = pathlib.Path("/Users/apple/Downloads/MFS/assets/MFS-Components-IDEAS")
BSUK = pathlib.Path("/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Components-Ideas")
UNUSED = "## Sheets not used by a city component"
ENTRY = re.compile(r"^- (`(/[^`]+)`|<(https?://[^>]+)>) — (.{12,})$", re.M)
#: A pool line: "- Pool `london/<comp>/<v>` — **Name** (layout `slug`, media m, density d,
#: framing f): what the variant is."
POOL = re.compile(r"^- Pool `(london/([a-z-]+)/([abc]))` — \*\*(.+?)\*\* \(layout `([a-z0-9-]+)`, "
                  r"media ([a-z]+), density ([a-z]+), framing ([a-z]+)\): .{12,}$", re.M)
POOL_FILE = ROOT / "data" / "design" / "city-pool.json"

#: Per city: the components its page mounts, the idea folders whose every PNG it indexes, and
#: whether each component must cite a Playwright capture (London captured its own pages).
CITIES = {
    "london": {"components": COMPONENT_IDS, "folders": (MFS, BSUK), "capture_each": True},
    "manchester": {
        # Phase F ruling 2: no video section, and G2's table carries the six puppies.
        "components": tuple(c for c in COMPONENT_IDS if c not in ("video", "puppy-cards")),
        "folders": (BSUK,),
        "capture_each": False,
    },
}
#: Phase F ruling 3: Manchester's three heroes take their ideas from these five sheets.
MANCHESTER_HERO_SHEETS = ("hero-idea-3.png", "hero-idea-5.png", "hero-idea66.png",
                          "hero-idea77.png", "comparison-hero-idea1.png")
#: Phase F ruling 3: neither of these offers a pool variant.
NO_POOL = ("hero", "counter-strip")


def index_path(city):
    return ROOT / "docs" / "research" / f"{city}-components" / "ideas-index.md"


def sections(city):
    """(whole text, {component: body}, component order). A sheet no component uses is still
    indexed, under the closing UNUSED heading, which is not a component section."""
    text = index_path(city).read_text(encoding="utf-8")
    parts = re.split(r"^## ([a-z-]+) — .*$", text.split("\n" + UNUSED, 1)[0], flags=re.M)
    return text, {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}, \
        [parts[i] for i in range(1, len(parts), 2)]


def cited_paths(body):
    return [p for _all, p, _u, _i in ENTRY.findall(body) if p]


@pytest.mark.parametrize("city", sorted(CITIES))
def test_the_index_covers_the_city_components_in_city_page_order(city):
    _t, _s, order = sections(city)
    assert order == list(CITIES[city]["components"])


@pytest.mark.parametrize("city", sorted(CITIES))
def test_every_component_cites_at_least_three_sources(city):
    _t, secs, _o = sections(city)
    for cid, body in secs.items():
        entries = ENTRY.findall(body)
        assert len(entries) >= 3, (cid, len(entries))
        if CITIES[city]["capture_each"]:
            assert any(p.startswith(str(REFS)) for _all, p, _u, _i in entries), \
                f"{cid}: no Playwright capture from {REFS}/"


@pytest.mark.parametrize("city", sorted(CITIES))
def test_the_four_reference_pages_are_named(city):
    text, _s, _o = sections(city)
    src = (ROOT / "docs/research/2026-09-27-location-component-design-sources.md").read_text(encoding="utf-8")
    for url in set(re.findall(r"https?://[^\s)>`]+", src)):
        assert url in text, url


@pytest.mark.parametrize("city,root", [(c, r) for c in sorted(CITIES) for r in (REFS, MFS, BSUK)],
                         ids=lambda v: v if isinstance(v, str) else v.name)
def test_every_cited_path_under_a_present_folder_exists(city, root):
    if not root.is_dir():
        pytest.skip(f"{root} is not on this machine")
    text, _s, _o = sections(city)
    cited = [p for p in re.findall(r"`(/[^`]+)`", text) if p.startswith(str(root))]
    assert cited, f"nothing cited under {root}"
    missing = [p for p in cited if not pathlib.Path(p).is_file()]
    assert missing == [], missing


@pytest.mark.parametrize("city,folder", [(c, f) for c in sorted(CITIES) for f in CITIES[c]["folders"]],
                         ids=lambda v: v if isinstance(v, str) else v.name)
def test_every_idea_sheet_is_indexed(city, folder):
    if not folder.is_dir():
        pytest.skip(f"{folder} is not on this machine")
    text, _s, _o = sections(city)
    pngs = sorted(p for p in folder.glob("*.png"))
    assert pngs
    unindexed = [p.name for p in pngs if f"`{p}`" not in text]
    assert unindexed == [], unindexed


@pytest.mark.parametrize("city", sorted(CITIES))
def test_a_sheet_listed_as_unused_is_cited_by_no_component(city):
    text, secs, _o = sections(city)
    unused = cited_paths(text.split("\n" + UNUSED, 1)[1]) if UNUSED in text else []
    used = {p for body in secs.values() for p in cited_paths(body)}
    assert sorted(set(unused) & used) == []


@pytest.mark.parametrize("city", sorted(CITIES))
def test_nothing_was_copied_into_the_repo(city):
    here = sorted(index_path(city).parent.glob("*"))
    assert all(p.suffix in (".md", ".json") for p in here), here


# ---- Manchester only (Phase F rulings 3 and 4) ----

def test_manchester_hero_cites_exactly_the_five_named_breeder_sheets():
    _t, secs, _o = sections("manchester")
    cited = cited_paths(secs["hero"])
    assert sorted(cited) == sorted(str(BSUK / n) for n in MANCHESTER_HERO_SHEETS)


def test_manchester_counter_cites_breeder_sheets_only():
    _t, secs, _o = sections("manchester")
    cited = cited_paths(secs["counter-strip"])
    assert cited and all(p.startswith(str(BSUK) + "/") for p in cited), cited


def test_manchester_hero_and_counter_offer_no_pool_variant():
    _t, secs, _o = sections("manchester")
    for cid in NO_POOL:
        assert POOL.findall(secs[cid]) == [], cid


def test_manchester_pool_lines_match_the_pool_and_london_meta():
    _t, secs, _o = sections("manchester")
    pool = json.loads(POOL_FILE.read_text(encoding="utf-8"))["available"]
    for cid, body in secs.items():
        if cid in NO_POOL:
            continue
        rows = POOL.findall(body)
        # The index lists London's pool as it stood when Manchester was designed: the London
        # entries still pooled, plus any London source a frozen Manchester pick copied (a picked
        # from_pool copy takes its source out of the pool, Phase F gap G5).
        at_design = [k for k in pool[cid] if k.startswith("london/")]
        meta_m = json.loads((CANVAS_ROOT / "manchester" / cid / "meta.json").read_text(encoding="utf-8"))
        at_design += [r["from_pool"] for r in meta_m["variants"].values()
                      if r.get("from_pool") and r["from_pool"] not in at_design]
        assert sorted(r[0] for r in rows) == sorted(at_design), cid
        meta = json.loads((CANVAS_ROOT / "london" / cid / "meta.json").read_text(encoding="utf-8"))
        for key, comp, v, name, layout, media, density, framing in rows:
            assert comp == cid, key
            row = meta["variants"][v]
            assert name == row["name"], key
            assert dict(zip(AXES, (layout, media, density, framing))) == row["axes"], key
            missing = [s for s in row["idea_sources"] if f"`{s}`" not in body]
            assert missing == [], (key, missing)
