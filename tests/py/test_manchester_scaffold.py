"""Manchester's own route: the thirteen picks, the nav set and the outline's headings, on the rebuilt page (a scaffold until page-run row 12).

The noindex scaffold came first (the Manchester page run, Phase F Task 32; London's pattern, London
Plan 2 Task 8 and tests/py/test_city_scaffold.py).

src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro mounts Manchester's thirteen picks
(data/design/city-picks/blue-staffy-puppies-manchester-uk.json, frozen 355d5e43) on CityShell, in
the approved outline's order (data/outlines/blue-staffy-puppies-manchester-uk.json, STOP 2), so the
picks can be judged together at every width before the page board (STOP 3). What must hold:
  - one route, one source: [slug].astro no longer builds Manchester, and Manchester's page is
    its own rebuilt page (no `data-city-scaffold`); the other 26 cities still build from the
    template (London and Manchester each have their own file);
  - the page is `noindex, follow` and in no sitemap shard until the user approves it (Task 54);
  - every city component on it is one of Manchester's picks, all thirteen are mounted, and no
    London `city-*` root (nor the kit's own nav set, puppy cards or a video) appears;
  - the headings are the outline's, word for word and in order (H1 to H6), with the nine FAQ
    wordings the breeder adopted at STOP 3 in place (test_manchester_board.REWORDED);
  - the FAQPage node carries exactly the visible questions, the outline's twenty as adopted;
  - the reviews are data/reviews.json's, word for word; the figures are read, never typed;
  - each served photo keeps its served alt on its first use and a new alt on a repeat.
And gap G10: scripts/city_side_by_side.mjs selects a city's rows by `canvas_variant` and reads
each root selector from its row, so London's rows carry both fields too.
"""
import html as H
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests/py"))
from city_components import KIT_OF_VARIANT, NOT_USED  # noqa: E402
from test_manchester_board import REWORDED  # noqa: E402

ADOPTED = {old: new for old, (new, _) in REWORDED.items()}

SLUG = "blue-staffy-puppies-manchester-uk"
LONDON = "blue-staffy-puppies-london"
PAGE = ROOT / "src/pages/uk-locations" / f"{SLUG}.astro"
TEMPLATE = ROOT / "src/pages/uk-locations/[slug].astro"
BUILT = ROOT / "dist/uk-locations" / SLUG / "index.html"
PICKS = json.loads((ROOT / "data/design/city-picks" / f"{SLUG}.json").read_text())["picks"]
OUTLINE = json.loads((ROOT / "data/outlines" / f"{SLUG}.json").read_text())
LOCATIONS = json.loads((ROOT / "data/locations.json").read_text())
COMPONENTS = json.loads((ROOT / "data/design/components.json").read_text())
REVIEWS = json.loads((ROOT / "data/reviews.json").read_text())
SIDE_BY_SIDE = ROOT / "scripts/city_side_by_side.mjs"


def built():
    if not BUILT.exists():
        pytest.fail("run npm run build first")
    return BUILT.read_text(encoding="utf-8")


def main_of(html):
    return html.split("<main", 1)[1].split("</main>", 1)[0]


def text(fragment):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def words(fragment):
    """A heading's words as a reader sees them: inline tags (the kept runs' spans) join, never split."""
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def city_rows(city):
    """The project 5 rows a city's picks were built as (`canvas_variant`, gap G10)."""
    return [r for r in COMPONENTS if r["project"] == 5 and str(r.get("canvas_variant", "")).startswith(f"{city}/")]


def root_class(row):
    sel = row["root_selector"]
    assert sel.startswith("."), sel
    return sel[1:]


def classes(html):
    """Every class token on the page, exactly (so `city-faq` is not found inside `city-faq-x`)."""
    return {c for attr in re.findall(r'class="([^"]*)"', html) for c in attr.split()}


def wears(html, row):
    """True when the page carries the row's root: a class token or a data hook."""
    sel = row["root_selector"]
    if sel.startswith("."):
        return sel[1:] in classes(html)
    return re.search(rf"\s{re.escape(sel[1:-1])}[\s=>]", html) is not None


def flat(headings):
    """The outline's heading tree in document order: (level, text)."""
    out = []
    for h in headings:
        out.append((h["level"], h["text"]))
        out.extend(flat(h.get("children", [])))
    return out


# --------------------------------------------------------------------------- one route, one source

def test_manchester_has_its_own_file():
    assert PAGE.is_file()


def test_manchester_has_its_own_rebuilt_page_and_the_template_builds_the_other_26():
    html = built()
    assert f'data-city-scaffold="{SLUG}"' not in html
    own = {p.stem for p in (ROOT / "src/pages/uk-locations").glob("*.astro") if "[" not in p.name}
    assert {SLUG, LONDON} <= own
    others = [l["slug"] for l in LOCATIONS if l["slug"] not in own]
    assert len(others) == 26, len(others)
    for slug in others:
        page = ROOT / "dist/uk-locations" / slug / "index.html"
        assert page.is_file(), slug
        body = page.read_text(encoding="utf-8")
        assert "prose-migrated" in body and "data-city-scaffold" not in body, slug


def test_the_scaffold_is_noindex_and_in_no_sitemap():
    html = built()
    assert re.search(r'<meta name="robots" content="noindex, follow"', html)
    shards = [s.read_text(encoding="utf-8") for s in (ROOT / "dist").glob("*sitemap*.xml")]
    assert shards
    route = f"/uk-locations/{SLUG}/"
    assert not [s for s in shards if f"{route}<" in s or f'{route}"' in s]
    src = PAGE.read_text(encoding="utf-8")
    assert 'robots="noindex, follow"' in src, "written in the file, never read from a data row"


def test_manchester_keeps_the_date_its_url_was_first_published():
    row = json.loads((ROOT / "data/page-dates.json").read_text())["routes"][f"/uk-locations/{SLUG}/"]
    assert row["datePublished"] == "2026-09-16"
    assert row["dateModified"] >= row["datePublished"]


# --------------------------------------------------------------------------- the picks, and only them

def test_every_city_component_is_a_manchester_pick_and_all_thirteen_are_mounted():
    main = main_of(built())
    picked = [v for v in PICKS.values() if v != NOT_USED]
    assert len(picked) == 13
    mine = city_rows("manchester")
    assert sorted(r["canvas_variant"] for r in mine) == sorted(picked)
    mine_roots = {root_class(r) for r in mine}
    html = built()
    for r in mine:
        assert wears(html, r), f"{r['canvas_variant']} ({r['id']}) is not mounted"
    found = set()
    for cls in re.findall(r'class="([^"]*\bcity-kit\b[^"]*)"', html):
        roots = {c for c in cls.split() if c in mine_roots}
        assert roots, f"a city-kit root that is no Manchester pick: {cls}"
        found |= roots
    assert found == mine_roots
    assert main.count('data-faq-block="') == 3, "the three FAQ blocks"
    assert main.count('class="city-kit city-three-plates') == 3, "the three review slots"


def test_no_london_root_no_kit_nav_no_video_and_no_puppy_cards():
    html = built()
    london = city_rows("london")
    assert len(london) == 15, "London's fifteen picks carry canvas_variant (G10 back-fill)"
    for r in london:
        assert not wears(html, r), r["id"]
    for sub in (r for r in COMPONENTS if r["project"] == 5 and r.get("subcomponent")):
        stem = re.sub(r"(?<!^)(?=[A-Z])", "-", sub["file"].replace(".astro", "")).lower()
        assert f'class="city-kit {stem}' not in html, sub["id"]
    for kit in ('class="kit-dial', 'class="kit-strip', 'class="kit-sheet', 'class="puppy-card'):
        assert kit not in html, kit
    main = main_of(html)
    for video in ("youtube", "data-play", "city-video"):
        assert video not in main, video
    assert "VideoObject" not in html


def test_the_city_nav_set_is_manchesters_and_every_link_names_a_section():
    html = built()
    bar = re.search(r"<div[^>]*city-question-bar[^>]*>", html).group(0)
    assert 'data-city-nav="bar"' in bar and "data-strip" in bar, "on a real page the bar is the top chrome"
    assert re.search(r"<aside[^>]*city-numeral-rail[^>]*data-city-nav=\"dial\"", html)
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    spies = re.findall(r'data-spy="([^"]+)"', html)
    order = list(dict.fromkeys(spies))
    assert len(order) == 13, order
    assert not [s for s in spies if s not in ids]
    h2s = [h["text"] for s in OUTLINE["sections"] for h in s["headings"] if h["level"] == 2]
    for sid, question in zip(order, h2s):
        block = re.search(rf'id="{re.escape(sid)}"(.*?)(?=<h2\b)<h2[^>]*>(.*?)</h2>', html, re.S)
        assert block and words(block.group(2)) == question, (sid, question)


# --------------------------------------------------------------------------- the outline, word for word

def test_the_headings_are_the_outlines_in_order_h1_to_h6():
    main = main_of(built())
    found = [(int(l), words(t)) for l, t in re.findall(r"<h([1-6])\b[^>]*>(.*?)</h\1>", main, re.S)]
    want = [(1, OUTLINE["h1"])] + [(l, ADOPTED.get(t, t)) for s in OUTLINE["sections"]
                                    for l, t in flat(s["headings"]) if l > 1]
    assert found == want


def test_the_litter_table_sits_under_its_h4_with_the_outlines_caption():
    main = main_of(built())
    table = next(s["table"] for s in OUTLINE["sections"] if s.get("table"))
    level, words = re.match(r"H([2-6]) (.+)", table["under"]).groups()
    shelf = re.search(r'<section[^>]*city-photo-shelf[^>]*>(.*?)</section>', main, re.S).group(1)
    assert re.search(rf"<h{level}\b[^>]*>\s*{re.escape(H.escape(words, quote=False))}\s*</h{level}>", shelf)
    assert table["caption"] in text(shelf)
    cells = re.findall(r"<td\b[^>]*>", shelf)
    assert cells and all("data-label=" in c for c in cells), "every cell labelled (rule 13)"
    assert len(re.findall(r"<tr\b", shelf)) == 1 + len([p for p in json.loads((ROOT / "data/puppies.json").read_text()) if p["status"] == "Available"])


# --------------------------------------------------------------------------- FAQ, reviews, facts

def test_the_faq_schema_carries_exactly_the_visible_questions():
    html = built()
    visible = [words(q) for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", html, re.S)]
    outline = [ADOPTED.get(c["text"], c["text"]) for s in OUTLINE["sections"] if s.get("faq") for h in s["headings"] for c in h["children"]]
    assert len(outline) == 20 and visible == outline
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    nodes = [n for b in blocks for n in (b if isinstance(b, list) else [b]) if n.get("@type") == "FAQPage"]
    assert len(nodes) == 1
    assert [q["name"] for q in nodes[0]["mainEntity"]] == visible


def test_the_three_reviews_are_the_outlines_reviewers_word_for_word():
    main = main_of(built())
    plates = re.findall(r'<section[^>]*city-three-plates[^>]*>(.*?)</section>', main, re.S)
    assert len(plates) == 3
    for plate, name in zip(plates, ["The Victoria Family", "Mark J", "Rachel L."]):
        review = next(r for r in REVIEWS if r["name"] == name)
        quote = re.sub(r"\s+", " ", review["quote"]).strip()
        assert quote.replace(" ", "") in text(plate).replace(" ", ""), name
        assert name in text(plate)


def test_the_page_types_no_figure_and_imports_no_london_component():
    src = PAGE.read_text(encoding="utf-8")
    code = re.sub(r"^\s*//.*$", "", src, flags=re.M)
    assert "£" not in code, "prices, the deposit and the band are read from the data"
    assert not re.search(r"\b(1,?500|1,?700|500|200|350)\b", re.sub(r"\d+px|var\([^)]*\)", "", code))
    for r in city_rows("london") + [r for r in COMPONENTS if r["project"] == 5 and r.get("subcomponent")]:
        assert r["file"] not in src, r["file"]
    assert "_registry" not in src, "the registry imports every kit component (and so their CSS)"


def scaffold_alt_defects(main, served):
    """The first use of a served photo keeps its served alt (working rule 11), or the alt the
    board records in `verbatim.changed` for it (working rule 15: the Asset Gate replaced eight
    served alts that described another picture, STOP 4 q07); each repeat takes a new alt, never a
    copy (answer board q02, 2026-09-29). As tests/py/test_city_scaffold.py's."""
    from test_city_scaffold import scaffold_alt_defects as check
    board = json.loads((ROOT / "data/boards" / f"{SLUG}.json").read_text())
    changed = {}
    for r in board.get("verbatim", {}).get("changed", []):
        if r.get("kind") == "alt" and r.get("src", "").startswith("/images/"):
            changed.setdefault(r["src"][len("/images/"):], set()).add(r["new"])
    return check(main, served, changed)


def test_each_served_photo_keeps_its_served_alt_first_and_a_new_alt_on_a_repeat():
    from check_city_canvas import served_alts
    main = main_of(built())
    assert re.search(r'<img [^>]*src="/images/', main), "the scaffold reuses served photographs"
    assert scaffold_alt_defects(main, served_alts()) == []
    alts = [H.unescape(a) for a in re.findall(r'<img [^>]*alt="([^"]+)"', main)]
    assert len(alts) == len(set(alts)), sorted(a for a in alts if alts.count(a) > 1)


# --------------------------------------------------------------------------- G10: the side-by-side

def test_every_picked_city_row_names_its_variant_and_root_selector():
    picked = {v for p in (ROOT / "data/design/city-picks").glob("*.json")
              for v in json.loads(p.read_text())["picks"].values() if v != NOT_USED}
    rows = {r["id"]: r for r in COMPONENTS if r["project"] == 5 and not r.get("subcomponent")}
    assert len(rows) == len(picked) == 28
    for rid, r in rows.items():
        assert r.get("canvas_variant") in picked, rid
        assert KIT_OF_VARIANT[r["canvas_variant"]] == rid, rid
        assert re.fullmatch(r"(\.[a-z0-9-]+|\[data-[a-z0-9-]+\])", r.get("root_selector", "")), rid


def test_the_side_by_side_selects_rows_by_variant_and_reads_the_selector_from_the_row():
    src = SIDE_BY_SIDE.read_text(encoding="utf-8")
    assert "ROOT_SELECTOR = {" not in src, "no city's file map is typed in the script"
    assert "canvas_variant" in src and "root_selector" in src
    assert "rows.length !== order.length" not in src, "all project 5 rows are never compared with one city's picks"
