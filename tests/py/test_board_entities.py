"""System-gaps Task 3: the board's keyword and entity views. The grouping is pure and tested
here directly; the rendering is tested through build_page_board.render()."""
import copy
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import board_entities as BE  # noqa: E402
import pageboard as PB       # noqa: E402

ONT = {"entities": [
    {"id": "ont:lisa-bright", "name": "Lisa Bright", "aliases": ["the breeder"], "class": "People",
     "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "blue-staffy-uk-breeders"},
    {"id": "ont:manchester", "name": "Manchester", "aliases": [], "class": "Place",
     "authorization": "ASSERTED", "source": "data/locations.json", "owner_page": "uk-locations/x"},
    {"id": "ont:l-2-hga-dna-test", "name": "L-2-HGA DNA test", "aliases": ["L2-HGA"], "class": "Health",
     "authorization": "PROPOSED", "source": None, "owner_page": "blue-staffy-health-uk"},
    {"id": "ont:rspca", "name": "RSPCA", "aliases": [], "class": "Organization",
     "authorization": "ASSERTED", "source": "docs/reference/external-link-library.md", "owner_page": None},
    {"id": "ont:wild", "name": "wild <b>caught</b>", "aliases": [], "class": "Commerce",
     "authorization": "BLOCKED", "source": "CLAUDE.md", "owner_page": None},
]}


def _board():
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text(encoding="utf-8")))
    for s in b["sections"]:
        s["entities"] = []
    s1, s2, s3 = b["sections"][0], b["sections"][1], b["sections"][2]
    s1["entities"] = ["ont:lisa-bright", "ont:manchester", "ont:mystery"]
    s2["entities"] = ["ont:lisa-bright", "ont:l-2-hga-dna-test", "ont:lisa-bright"]   # a repeat in one section
    s3["entities"] = ["ont:rspca", "ont:wild", "ont:manchester"]
    s1["keywords"]["lsi"] = ["Kennel Club", "health tested"]
    s2["keywords"]["lsi"] = ["kennel  club"]                                        # same term, other spelling
    s2["keywords"]["related"] = ["blue staffy puppies manchester cheap"]
    return b


def test_group_entities_orders_classes_and_carries_sections():
    groups = BE.group_entities(_board(), ONT)
    assert [g["class"] for g in groups] == ["People", "Place", "Health", "Organization", "Commerce", "Unknown"]
    by = {c["id"]: c for g in groups for c in g["entities"]}
    b = _board()
    s1, s2, s3 = (b["sections"][i]["id"] for i in range(3))
    assert [r["id"] for r in by["ont:lisa-bright"]["sections"]] == [s1, s2]          # once per section
    assert [r["id"] for r in by["ont:manchester"]["sections"]] == [s1, s3]
    assert by["ont:mystery"]["class"] == "Unknown" and by["ont:mystery"]["authorization"] == "UNKNOWN"
    assert by["ont:l-2-hga-dna-test"]["aliases"] == ["L2-HGA"]
    place = next(g for g in groups if g["class"] == "Place")
    assert [r["id"] for r in place["columns"]] == [s1, s3]                           # matrix columns


def test_group_entities_puts_a_blocked_card_first_in_its_class():
    ont = copy.deepcopy(ONT)
    ont["entities"].append({"id": "ont:deposit", "name": "Deposit", "aliases": [], "class": "Commerce",
                            "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": None})
    b = _board()
    b["sections"][0]["entities"].append("ont:deposit")
    b["sections"][1]["entities"].append("ont:deposit")
    commerce = next(g for g in BE.group_entities(b, ont) if g["class"] == "Commerce")
    assert [c["id"] for c in commerce["entities"]] == ["ont:wild", "ont:deposit"]


def test_group_entities_on_a_board_with_none_is_empty():
    b = _board()
    for s in b["sections"]:
        s["entities"] = []
    assert BE.group_entities(b, ONT) == []


def test_group_keywords_merges_spellings_and_keeps_every_type():
    groups = BE.group_keywords(_board())
    assert [g["type"] for g in groups] == list(PB.ALL_KEYWORD_TYPES)
    lsi = next(g for g in groups if g["type"] == "lsi")
    kc = next(t for t in lsi["terms"] if t["term"] == "Kennel Club")
    assert len(kc["sections"]) == 2                                                  # "kennel  club" merged
    related = next(g for g in groups if g["type"] == "related")
    assert related["optional"] and related["label"] == "Related"
    assert related["terms"][0]["term"] == "blue staffy puppies manchester cheap"


def test_entity_html_is_one_line_escaped_and_links_every_section():
    html = BE.entities_html(BE.group_entities(_board(), ONT))
    assert "\n\n" not in html                                   # marked would end the HTML block
    assert "<b>caught</b>" not in html and "wild &lt;b&gt;caught&lt;/b&gt;" in html
    for badge in ("b-asserted", "b-proposed", "b-blocked", "b-unknown"):
        assert badge in html
    assert html.count('class="ent kv-item') == 6
    b = _board()
    assert f'href="#outline-{b["sections"][1]["id"]}"' in html
    assert 'class="kv-bar"' in html and 'type="search"' in html
    assert re.search(r'data-f="People" aria-pressed="false"><i class="dot c-people"[^>]*></i>People <b>1</b>', html)
    assert html.count('<table class="mx">') == 6                # one matrix per class


def test_keyword_html_lists_missing_optional_types_only_when_asked():
    groups = BE.group_keywords(_board())
    quiet = BE.keywords_html(groups)
    assert "No term yet" not in quiet and "\n\n" not in quiet
    loud = BE.keywords_html(groups, show_empty=PB.OPTIONAL_KEYWORD_TYPES)
    assert "No term yet: Variations, Co-occurring, Similar." in loud


def test_the_board_renders_cards_matrix_and_outline_anchors_and_no_graph():
    import build_page_board as BPB
    from test_page_board import LEDGER_EMPTY
    b = _board()
    html = BPB.render(b, ONT, LEDGER_EMPTY, live={}, thumbs={}, slug="_demo")
    assert "cytoscape" not in html and "entity-graph" not in html
    for s in b["sections"]:
        assert f'id="outline-{s["id"]}"' in html                   # every chip has a target
    assert 'data-kv="entities"' in html and 'data-kv="keywords"' in html
    assert "html{scroll-behavior:smooth}" in html
    assert ':root[data-theme="dark"]{--c-people' in html           # class colours in both themes
    assert "section.sec:has(.kv){overflow:clip}" in html          # the sticky bar can stick


def test_a_new_family_board_shows_the_four_optional_columns_and_names_the_empty_ones():
    import build_page_board as BPB
    from test_page_board import LEDGER_EMPTY
    b = _board()
    b["meta"].update({"slug": "uk-locations/blue-staffy-puppies-manchester-uk", "page_type": "location"})
    html = BPB.render(b, ONT, LEDGER_EMPTY, live={}, thumbs={}, slug=b["meta"]["slug"])
    assert "| Transact | Variations | Related | Co-occurring | Similar | Words |" in html
    assert "No term yet: Variations, Co-occurring, Similar." in html
    built = _board()                                                # _demo is not a new-family page
    html = BPB.render(built, ONT, LEDGER_EMPTY, live={}, thumbs={}, slug="_demo")
    assert "| Transact | Related | Words |" in html                  # only the optional type it uses


# ── review fixes ─────────────────────────────────────────────────────────────────────────

def _one(ent):
    """A board naming one entity, rendered as block 5's HTML."""
    b = _board()
    for s in b["sections"]:
        s["entities"] = []
    b["sections"][0]["entities"] = [ent["id"]]
    return BE.entities_html(BE.group_entities(b, {"entities": [ent]}))


def test_a_hostile_authorization_renders_inert_and_a_none_renders():
    evil = '" onmouseover="alert(1)'
    html = _one({"id": "ont:x", "name": "X", "aliases": [], "class": "People", "authorization": evil,
                 "source": None, "owner_page": None})
    assert "onmouseover=" not in html.replace("onmouseover=&quot;", "")      # never an attribute
    assert 'class="kv-badge b-unknown"' in html and "&quot; onmouseover=&quot;alert(1)" in html
    html = _one({"id": "ont:y", "name": None, "aliases": None, "class": "People", "authorization": None,
                 "source": None, "owner_page": None})
    assert 'class="kv-badge b-unknown">UNKNOWN<' in html and '<b class="ent-name">ont:y</b>' in html


def test_aliases_sources_owner_pages_and_keyword_terms_are_escaped():
    html = _one({"id": "ont:z", "name": "Z", "aliases": ["<i>al</i>"], "class": "People",
                 "authorization": "ASSERTED", "source": "<s>src</s>", "owner_page": "<o>page"})
    for raw in ("<i>al</i>", "<s>src</s>", "<o>page"):
        assert raw not in html
    for safe in ("&lt;i&gt;al&lt;/i&gt;", "&lt;s&gt;src&lt;/s&gt;", "/&lt;o&gt;page/"):
        assert safe in html
    b = _board()
    b["sections"][0]["keywords"]["lsi"] = ['<img src=x onerror="y">']
    kh = BE.keywords_html(BE.group_keywords(b))
    assert "<img" not in kh and "&lt;img src=x onerror=&quot;y&quot;&gt;" in kh


def test_an_unknown_ontology_class_falls_back_to_unknown():
    b = _board()
    for s in b["sections"]:
        s["entities"] = []
    b["sections"][0]["entities"] = ["ont:odd"]
    groups = BE.group_entities(b, {"entities": [{"id": "ont:odd", "name": "Odd", "aliases": [], "class": "Wizardry",
                                                 "authorization": "ASSERTED", "source": None, "owner_page": None}]})
    assert [g["class"] for g in groups] == ["Unknown"]
    html = BE.entities_html(groups)
    assert "Wizardry" not in html and "c-unknown" in html


def test_the_view_css_is_scoped_and_the_bar_is_a_group():
    html = BE.entities_html(BE.group_entities(_board(), ONT))
    assert 'role="group" aria-label="Filter entities by class"' in html and "toolbar" not in html
    css = BE.CSS
    for bare in ("\n.dot{", "\n.badge{", "\n.c-people{", "\n.b-blocked{", "\n.none{", "\n.ent .none{"):
        assert bare not in css, bare
    assert "\n.kv .dot{" in css and "\n.kv .kv-badge{" in css and "\n.kv .c-people{" in css
    assert "\nhtml{scroll-behavior:smooth}" in css and "\n.oanchor{" in css
    assert "table.mx caption{display:flex;align-items:center;gap:6px}" in css
    assert css.count("--kv-blocked:") == 3                            # light, dark (media), dark (attribute)
    assert "--kv-blocked:#FF9B8A" in css and ".b-blocked{border-color:var(--kv-blocked);color:var(--kv-blocked)}" in css


def test_search_text_collapses_whitespace_and_matrix_rows_carry_their_entity():
    html = BE.entities_html(BE.group_entities(_board(), ONT))
    assert 'data-q="lisa bright the breeder people' in html
    assert re.search(r'<tr data-id="ont:lisa-bright"><th scope="row">Lisa Bright</th>', html)
    assert "replace(/\\s+/g,' ')" in BE.JS
    b = _board()
    b["sections"][0]["keywords"]["lsi"] = ["kennel   club  uk"]
    assert 'data-q="kennel club uk"' in BE.keywords_html(BE.group_keywords(b))


_SHOT = r"""
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2]);
let chromium;
try { ({ chromium } = require('@playwright/test')); } catch (e) { console.log('SKIP no playwright'); process.exit(0); }
let browser;
try { browser = await chromium.launch(); } catch (e) { console.log('SKIP no browser'); process.exit(0); }
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.goto('file://' + process.argv[3]);
try { await page.waitForSelector('[data-kv="entities"]', { timeout: 15000 }); }
catch (e) { console.log('SKIP board did not mount (marked unavailable)'); await browser.close(); process.exit(0); }
const ents = page.locator('[data-kv="entities"]');
const count = () => ents.evaluate(r => ({
  cards: r.querySelectorAll('.ent[hidden]').length,
  rows: [...r.querySelectorAll('table.mx tbody tr')].filter(t => t.hidden || t.closest('.mx-wrap').hidden).length,
  rowsHidden: r.querySelectorAll('table.mx tbody tr[hidden]').length,
  tables: r.querySelectorAll('.mx-wrap[hidden]').length }));
const out = { start: await count() };
await ents.locator('.kv-chip[data-f="People"]').click();
out.people = await count();
await ents.locator('.kv-chip[data-f="*"]').click();
await ents.locator('.kv-q').fill('  MANCHESTER ');
out.search = await count();
await ents.locator('.kv-q').fill('lisa    bright');
out.spaces = await count();
console.log('RESULT ' + JSON.stringify(out));
await browser.close();
"""


def test_the_filter_and_search_hide_cards_and_matrix_rows_in_a_browser(tmp_path):
    import shutil
    import subprocess
    import pytest
    import build_page_board as BPB
    from test_page_board import LEDGER_EMPTY
    if shutil.which("node") is None:
        pytest.skip("node not installed")
    page = tmp_path / "board.html"
    page.write_text(BPB.render(_board(), ONT, LEDGER_EMPTY, live={}, thumbs={}, slug="_demo"), encoding="utf-8")
    script = tmp_path / "shot.mjs"
    script.write_text(_SHOT, encoding="utf-8")
    r = subprocess.run(["node", str(script), str(ROOT / "package.json"), str(page)],
                       capture_output=True, text=True, timeout=120)
    if r.stdout.startswith("SKIP"):
        pytest.skip(r.stdout.strip())
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout.split("RESULT ", 1)[1])
    # six cards in six classes: Lisa, Manchester, L-2-HGA, RSPCA, wild, mystery
    assert res["start"] == {"cards": 0, "rows": 0, "rowsHidden": 0, "tables": 0}
    assert res["people"]["cards"] == 5 and res["people"]["tables"] == 5 and res["people"]["rows"] == 5
    # the search follows into the matrix: only Manchester's row and the Place table stay
    assert res["search"] == {"cards": 5, "rows": 5, "rowsHidden": 5, "tables": 5}
    assert res["spaces"]["cards"] == 5 and res["spaces"]["rowsHidden"] == 5
