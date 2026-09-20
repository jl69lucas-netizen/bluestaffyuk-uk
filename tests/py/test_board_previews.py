"""scripts/build_board_previews.py — the cutter that turns the built preview route into
the board's per-style blocks, and the style-option rule the record has to satisfy first."""
import json
import re
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_board_previews as P   # noqa: E402
import build_board_previews as BBP  # noqa: E402  (the per-page id triples, read by name)
import pageboard as PB             # noqa: E402


@pytest.fixture(autouse=True)
def _fixture_link_library(monkeypatch):
    """Validate this module's board fixtures against the FIXTURE link library, for the same
    reason test_page_board.py does: `validate_board()` refuses an external href the real
    `docs/reference/external-link-library.md` does not record, and a fixture URL has no
    business in a content document."""
    monkeypatch.setattr(PB, "EXTERNAL_LIBRARY",
                        ROOT / "tests" / "py" / "fixtures" / "external-link-library.md")


def test_style_blocks_are_cut_per_section_and_style():
    html = ('<section data-section="hero" data-style="S1">A</section>'
            '<section data-section="hero" data-style="S2">B</section>'
            '<section data-section="faq" data-style="S1">C</section>')
    blocks = P.cut(html)
    assert set(blocks) == {("hero", "S1"), ("hero", "S2"), ("faq", "S1")}
    assert blocks[("hero", "S2")] == "B"


def test_record_without_three_styles_is_refused():
    rec = {"sections": [{"id": "hero", "styles": ["S1", "S2"]}]}
    with pytest.raises(P.StyleError) as e:
        P.validate_styles(rec)
    assert "hero" in str(e.value)


def test_a_record_with_no_styles_and_one_with_all_three_are_both_accepted():
    assert P.validate_styles({"sections": [{"id": "a", "styles": []},
                                           {"id": "b", "styles": ["S1", "S2", "S3"]}]})


def test_a_fourth_style_is_refused_as_loudly_as_a_missing_one():
    with pytest.raises(P.StyleError):
        P.validate_styles({"sections": [{"id": "a", "styles": ["S1", "S2", "S3", "S4"]}]})


def test_the_cutter_keeps_a_nested_kit_section_inside_its_block():
    """The kit's Hero, TrustStrip, CounterStrip and Testimonial each render a <section>, so
    a non-greedy regex would end the block at the CHILD's closing tag and drop the rest."""
    html = ('<section data-section="hero" data-style="S1">'
            '<section class="kit-hero">inner</section>tail</section>'
            '<section data-section="hero" data-style="S2">B</section>')
    blocks = P.cut(html)
    assert blocks[("hero", "S1")] == '<section class="kit-hero">inner</section>tail'
    assert blocks[("hero", "S2")] == "B"


def test_a_section_without_both_attributes_is_not_a_block():
    blocks = P.cut('<section class="bp-page"><section data-section="a" data-style="S1">X</section></section>')
    assert set(blocks) == {("a", "S1")}


def test_the_demo_record_loads_and_offers_three_styles_on_every_styled_section():
    """`_demo` is the fixture the route, the cutter and the board builder all render. It is
    never a page: the leading underscore is what keeps it out of every page consumer."""
    rec = PB.load_board("_demo")
    assert rec["meta"]["preview"] is True and rec["meta"]["status"] == "draft"
    assert P.validate_styles(rec)
    # Working rule 16: the fixture's hero and counter carry the interior-guide sets so that
    # the per-page path is BUILT and measured, not only unit-tested. Every other section keeps
    # the shape-wide trio, which is what the four pages built before that rule still name.
    assert rec["meta"]["layout_type"] == "interior-guide"
    offered = {s["id"]: s["styles"] for s in rec["sections"]}
    assert offered["opening"] == ["H-GD1", "H-GD2", "H-GD3"]
    assert offered["at-a-glance"] == ["C-GD1", "C-GD2", "C-GD3"]
    assert all(v == ["S1", "S2", "S3"] for k, v in offered.items()
               if k not in {"opening", "at-a-glance"})


def test_main_refuses_a_slug_with_no_built_preview(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    assert P.main(["_demo"]) == 2
    assert "no built preview" in capsys.readouterr().out


def test_main_writes_css_and_blocks_from_the_built_page(tmp_path, monkeypatch):
    rec = PB.load_board("_demo")
    wanted = [(s["id"], sid) for s in rec["sections"] for sid in s["styles"]]
    ids = [s["id"] for s in rec["sections"]]
    body = "".join(f'<section data-section="{i}" data-style="{s}">x{i}{s}</section>'
                   for i, s in wanted)
    page = tmp_path / "dist" / "board-preview" / "_demo" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text(f"<html><style>.a{{color:red}}</style>{body}</html>", encoding="utf-8")
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(P, "OUT", tmp_path / "previews")
    assert P.main(["_demo"]) == 0
    out = json.loads((tmp_path / "previews" / "_demo.json").read_text())
    assert out["css"] == ".a{color:red}"
    second = wanted[1]
    assert out["blocks"][f"{second[0]}|{second[1]}"] == f"x{second[0]}{second[1]}"
    assert len(out["blocks"]) == 3 * len(ids)


def test_main_reports_a_styled_section_the_built_page_did_not_render(tmp_path, monkeypatch, capsys):
    """A gate that examined nothing is not a pass: a block the record asked for and the
    page did not produce is named, not silently written out as an empty iframe."""
    rec = PB.load_board("_demo")
    first = rec["sections"][0]
    one, missing = first["styles"][0], first["styles"][1]
    page = tmp_path / "dist" / "board-preview" / "_demo" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text(f'<section data-section="{first["id"]}" data-style="{one}">x</section>',
                    encoding="utf-8")
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(P, "OUT", tmp_path / "previews")
    assert P.main(["_demo"]) == 1
    assert f"{first['id']}|{missing}" in capsys.readouterr().out


# --- the gate rule and the board's style fieldset ----------------------------------------

def _styled():
    """MIN_BOARD with its one section offering the three styles, approved with no pick."""
    import json as _json
    from test_page_board import MIN_BOARD, _approved
    b = _json.loads(_json.dumps(MIN_BOARD))
    b["sections"][0]["styles"] = ["S1", "S2", "S3"]
    return _approved(b)


def test_gate_fails_style_unpicked_on_an_approved_record_and_skips_a_draft():
    from test_page_board import ONT_OK, LEDGER_EMPTY
    b = _styled()
    b["approval"]["picks"] = {}
    b["approval"]["record_hash"] = PB.record_hash(b)
    live = {"/other/": ["Where Do We Deliver Each Week?"],
            "/uk-locations/staffy-puppies-for-sale-glasgow/": []}
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
    assert [x for x in f if x["check"] == "style-unpicked"], f

    # A draft has not been answered yet, so it is not yet in default on the answer.
    b["meta"]["status"] = "draft"
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
    assert [x for x in f if x["check"] == "style-unpicked"] == []


def test_gate_passes_once_the_approval_names_a_style():
    from test_page_board import ONT_OK, LEDGER_EMPTY
    b = _styled()
    b["approval"]["picks"] = {b["sections"][0]["id"]: "S2"}
    b["approval"]["record_hash"] = PB.record_hash(b)
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY,
                         live={"/other/": ["Where Do We Deliver Each Week?"],
                               "/uk-locations/staffy-puppies-for-sale-glasgow/": []},
                         stage="build")
    assert [x for x in f if x["check"] == "style-unpicked"] == []


def test_the_board_renders_one_radio_group_of_three_styles_and_no_component_cards():
    """The style fieldset REPLACES the ledger option cards: both wrote `pick-<id>`, and two
    controls on one radio name is a board that can save a pick nobody made."""
    import build_page_board as BPB
    from test_page_board import ONT_OK, LEDGER_EMPTY
    b = _styled()
    sid = b["sections"][0]["id"]
    previews = {"css": ".x{color:red}", "images": {},
                "blocks": {f"{sid}|S1": "<p>one</p>", f"{sid}|S2": "<p>two</p>", f"{sid}|S3": "<p>three</p>"},
                "names": {f"{sid}|S1": "First", f"{sid}|S2": "Second", f"{sid}|S3": "Third"}}
    html = BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x", previews=previews)
    assert html.count(f'name="pick-{sid}"') == 3
    assert 'value="S1"' in html and 'value="S3"' in html and "Second" in html
    assert "nothumb" not in html.split("6. Component options")[1].split("</script>")[0]
    # three widths per style, nine frames for the one section
    assert html.count(f'data-block="{sid}|') == 9
    for w in BPB.PREVIEW_W:
        assert f'width="{w}"' in html


def test_the_board_says_so_when_a_style_has_not_been_rendered_yet():
    import build_page_board as BPB
    from test_page_board import ONT_OK, LEDGER_EMPTY
    b = _styled()
    html = BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "build_board_previews.py" in html and "data-block=" not in html


def test_picked_sections_covers_a_styled_standard_section():
    import build_page_board as BPB
    b = _styled()
    b["sections"][0]["shape"] = "standard"
    assert BPB.picked_sections(b) == [b["sections"][0]["id"]]


def test_board_preview_slugs_nest_and_stay_out_of_the_field_contract():
    import form_contract_audit as F
    assert "board-preview" in F.NON_CONTENT_ROUTES
    assert F.contract_keys("board-preview/_demo") == []
    assert F.contract_keys("board-preview") == []
    # Not a loosening: a sibling slug that merely starts with the same letters is content.
    assert [k[0] for k in F.contract_keys("board-preview-notes")] == [k[0] for k in F.KEYS]


# --- the style map itself: no inert axes, and three that really differ -------------------

TS = ROOT / "src/lib/boardStyles.ts"


def _parse_style_map():
    """{shape: [(id, name, layout dict), ×3]} read out of src/lib/boardStyles.ts.

    Parsed rather than imported because the map is TypeScript and these are Python tests.
    The parse is deliberately brittle — it expects the `def('S1', 'name', { … })` form the
    file is written in — and every assertion below first checks it found ten shapes with
    three styles each, so a reformat fails loudly here instead of quietly testing nothing."""
    import ast
    src = TS.read_text(encoding="utf-8")
    body = src.split("export const STYLES", 1)[1]
    out, shape = {}, None
    for line in body.splitlines():
        s = line.strip()
        m = re.match(r"^([a-z]+):\s*\[$", s)
        if m:
            shape = m.group(1)
            out[shape] = []
            continue
        m = re.match(r"^def\('(S[123])', '(.*?)', (\{.*\})\),$", s)
        if m and shape:
            # The object literal is JS: bare keys and single quotes. `{ a: 'b', c: 2 }` ->
            # a Python dict via a quote swap and literal_eval, which refuses anything that
            # is not a literal.
            obj = re.sub(r"(\w+):", r"'\1':", m.group(3)).replace("{ ", "{").replace(" }", "}")
            out[shape].append((m.group(1), m.group(2), ast.literal_eval(obj)))
    return out


def _rendered_axes():
    """{shape: [axis, …]} out of the same file's RENDERED_AXES table."""
    src = TS.read_text(encoding="utf-8").split("export const RENDERED_AXES", 1)[1]
    src = src.split("};", 1)[0]
    return {m.group(1): re.findall(r"'(\w+)'", m.group(2))
            for m in re.finditer(r"^\s*([a-z]+):\s*\[(.*?)\],\s*$", src, re.M)}


STYLE_MAP = _parse_style_map()
AXES = _rendered_axes()


def test_the_parse_found_fifteen_shapes_with_three_styles_each():
    """Ten section shapes, plus the three CHROME shapes the contact board adds — `dial`,
    `sheet` and `strip`, whose three styles are variants of PageDial, SectionSheet and
    SectionStrip themselves rather than of the bed a section sits on — plus `table`,
    component 17's shape, whose three styles are the `chrome` axis (spec §9 amendment 5), plus
    `video`, component 18's shape, whose three styles are the `frame` and `play` axes (spec
    §9 amendment 7)."""
    assert len(STYLE_MAP) == 15, sorted(STYLE_MAP)
    assert {"dial", "sheet", "strip", "table", "video"} <= set(STYLE_MAP), sorted(STYLE_MAP)
    assert all(len(v) == 3 for v in STYLE_MAP.values()), {k: len(v) for k, v in STYLE_MAP.items()}
    assert set(AXES) == set(STYLE_MAP), (sorted(AXES), sorted(STYLE_MAP))


def test_no_style_sets_an_axis_its_renderer_ignores():
    """An axis outside RENDERED_AXES describes a difference nobody can see. Setting one is
    how three styles come to look identical while the record insists they are three."""
    for shape, styles in STYLE_MAP.items():
        allowed = set(AXES[shape])
        for sid, _name, layout in styles:
            assert set(layout) <= allowed, (shape, sid, sorted(set(layout) - allowed))


def test_each_shapes_three_styles_differ_on_an_axis_the_renderer_reads():
    for shape, styles in STYLE_MAP.items():
        axes = AXES[shape]
        for i in range(3):
            for j in range(i + 1, 3):
                a, b = styles[i][2], styles[j][2]
                differ = [x for x in axes if a.get(x) != b.get(x)]
                assert differ, (shape, styles[i][0], styles[j][0], a, b)


def test_every_style_name_is_distinct_within_its_shape():
    for shape, styles in STYLE_MAP.items():
        names = [n for _i, n, _l in styles]
        assert len(set(names)) == 3, (shape, names)


# --- and the BUILT blocks, which is where an inert axis would actually show ---------------

DIST_DEMO = ROOT / "dist/board-preview/_demo/index.html"
_CID = re.compile(r'\s+data-astro-cid-[a-z0-9]+(="[^"]*")?')
_STYLE_ATTRS = re.compile(r'\s+data-style(-name)?="[^"]*"')
_BL = re.compile(r"\bbl-(?:frame|cols|media|list|aside|head|chrome)-[a-z0-9-]+\s*")


def _normalised(inner):
    """A block with everything the STYLE writes into it taken out: the Astro scope hashes,
    the style id and name, the `bl-*` layout classes, and the eyebrow caption (which prints
    the style's own name). What is left is the MARKUP the renderer produced."""
    out = _CID.sub("", inner)
    out = _STYLE_ATTRS.sub("", out)
    out = _BL.sub("", out)
    out = re.sub(r'<p class="bl-eyebrow[^"]*">.*?</p>', "", out, flags=re.S)
    return " ".join(out.split())


def _demo_blocks():
    if not DIST_DEMO.exists():
        pytest.skip("run npm run build first")
    html = DIST_DEMO.read_text(encoding="utf-8")
    blocks, by_section = P.cut(html), {}
    for (sec, sid), inner in blocks.items():
        by_section.setdefault(sec, {})[sid] = inner
    assert by_section, "the built preview carries no [data-section][data-style] blocks"
    return by_section


def _box_classes(inner):
    m = re.search(r'class="(bl-box[^"]*)"', inner)
    assert m, inner[:200]
    return " ".join(sorted(c for c in m.group(1).split() if c.startswith("bl-")))


def _demo_section(sec_id):
    return next(s for s in PB.load_board("_demo")["sections"] if s["id"] == sec_id)


def _demo_style_ids(sec_id):
    """The ids the RECORD offers for a section. Hardcoding S1/S2/S3 stopped being right when
    working rule 16 gave the hero and the counter strip per-page-type sets of their own: the
    fixture's hero now offers H-GD1..3 and its counter C-GD1..3, and a test that kept asking
    for S1 would raise a KeyError rather than report a layout defect."""
    return list(_demo_section(sec_id).get("styles") or list(P.STYLE_IDS))


def _demo_defs(sec_id):
    """[(id, name, layout), ×3] for a section, from whichever map owns its ids."""
    shape = _demo_section(sec_id)["shape"]
    out = []
    for sid in _demo_style_ids(sec_id):
        if sid.startswith("H-") or sid.startswith("C-"):
            sets = HERO_SETS if sid.startswith("H-") else COUNTER_SETS
            row = next(r for rows in sets.values() for r in rows if r[0] == sid)
        else:
            row = next(r for r in STYLE_MAP[shape] if r[0] == sid)
        out.append(row)
    return out


def test_built_blocks_carry_three_distinct_layouts_per_section():
    """The `bl-*` class list IS the layout: it is what boxClass() emits and what
    board-styles.css keys on, so three identical lists are three identical renderings.

    A CAVEAT working rule 16 introduced: the hero's and the counter's per-page axes are PROPS,
    not classes, so two of their styles can differ genuinely and still emit the same box. Those
    two shapes are held by the markup test below instead, which is the stricter check anyway."""
    prop_only = {"hero", "stats"}
    for sec, styles in _demo_blocks().items():
        if _demo_section(sec)["shape"] in prop_only:
            continue
        lists = [_box_classes(styles[s]) for s in _demo_style_ids(sec)]
        assert len(set(lists)) == 3, (sec, lists)


def test_the_per_page_shapes_render_three_distinct_markups():
    """The other half of the test above. A hero whose three arrangements are props has to
    prove itself in the MARKUP, because its box classes may legitimately agree."""
    checked = 0
    for sec, styles in _demo_blocks().items():
        if _demo_section(sec)["shape"] not in {"hero", "stats"}:
            continue
        bodies = [_normalised(styles[s]) for s in _demo_style_ids(sec)]
        assert len(set(bodies)) == 3, (sec, [b[:120] for b in bodies])
        checked += 1
    assert checked == 2, (
        f"the fixture exercised {checked} per-page shape(s) — it owes a hero and a counter, "
        "or this test is measuring nothing")


def _markup_signature(layout):
    """The parts of a layout that change the MARKUP rather than only the CSS: an aside is a
    whole element, `mode` is a different Testimonial, and `grid-2` is two puppy cards
    instead of three. Everything else — frame, columns, media position, stack vs rail, and
    where the heading sits — the stylesheet does on identical markup. `heading` is not here
    even though `eyebrow` adds a paragraph: that paragraph is the style's own CAPTION, and
    `_normalised()` strips it, because a board that only ever differed by its own label
    would be three identical renderings with three names on them."""
    return (layout.get("aside"), layout.get("mode"), layout.get("list") == "grid-2",
            # Working rule 16's four: a mosaic is four `<img>` where a split is one, a panel
            # drops the photo column, a ledge is a whole block under the lede and a ring tile
            # is a drawn circle. None of the four is a stylesheet doing something to identical
            # markup, which is exactly what puts them on this list.
            layout.get("hero"), layout.get("ledge"), layout.get("tiles"))


def test_built_blocks_differ_in_markup_wherever_the_styles_promise_they_will():
    """PAIRWISE, and only where the promise is a markup one. Two styles that differ solely
    in where the stylesheet puts the image (standard S1 vs S2, and every hero pair) render
    the SAME markup by design — the class-list test above is what holds those apart. But a
    pair whose markup signatures differ — an aside appears, the Testimonial changes mode, a
    caption is added — must produce different markup, or the renderer is ignoring the axis
    the record is offering a pick on."""
    checked = 0
    for sec, styles in _demo_blocks().items():
        shape = _demo_section(sec)["shape"]
        ids = _demo_style_ids(sec)
        sigs = [_markup_signature(l) for _i, _n, l in _demo_defs(sec)]
        bodies = [_normalised(styles[s]) for s in ids]
        for i in range(3):
            for j in range(i + 1, 3):
                if sigs[i] == sigs[j]:
                    continue
                assert bodies[i] != bodies[j], (sec, shape, ids[i], ids[j])
                checked += 1
    assert checked >= 4, f"only {checked} pair(s) had a markup difference to check"


def test_the_demo_record_exercises_more_than_one_shape():
    """A fixture that only ever rendered prose would let every other branch of the route
    rot unnoticed."""
    shapes = {s["shape"] for s in PB.load_board("_demo")["sections"]}
    assert len(shapes) >= 4, shapes


# --- a kit-shaped section can never reach the approve button without a control ------------

def test_the_schema_refuses_a_kit_shape_with_no_styles():
    """The deadlock this closes: a `faq`-shaped section with no `styles` is offered no
    arrangements (that is a boardStyles decision, not a ledger one) and no ledger card
    either, yet the approve button would still demand a pick for it."""
    import json as _json
    from test_page_board import MIN_BOARD
    b = _json.loads(_json.dumps(MIN_BOARD))
    b["sections"][0]["shape"] = "faq"
    with pytest.raises(PB.BoardError) as e:
        PB.validate_board(b)
    assert "styles" in str(e.value)
    b["sections"][0]["styles"] = ["S1", "S2", "S3"]
    PB.validate_board(b)


def test_standard_keeps_its_exemption_from_the_styles_requirement():
    """`standard` is shared with the ported CAG shapes, so it is the one shape a record may
    use with no `styles` at all — and it must also still ACCEPT the three, because a rebuilt
    page's prose sections are boarded with rendered arrangements like every other section.

    Written against this module's own fixture rather than against `data/boards/index.json`.
    It used to load the homepage record, on the reading that the record was all-`standard`,
    style-less and approved; project 4 Task 18 re-cut that record into fifteen sections of
    ten shapes, each offering S1/S2/S3, so the assertion had stopped describing the
    exemption and started describing one page's outline. It also read the real link library
    through this module's autouse repoint, which the homepage's citations are not in.
    """
    import json as _json
    from test_page_board import MIN_BOARD
    b = _json.loads(_json.dumps(MIN_BOARD))
    b["sections"][0]["shape"] = "standard"
    b["sections"][0].pop("styles", None)
    PB.validate_board(b)                       # no styles: allowed
    b["sections"][0]["styles"] = ["S1", "S2", "S3"]
    PB.validate_board(b)                       # three styles: also allowed


def test_the_homepage_record_is_boarded_with_rendered_styles():
    """Task 18 migrated `data/boards/index.json` from the project-2 placeholder — fourteen
    style-less `standard` sections carrying the migrated headings — into a draft record the
    board-preview route renders. Three properties are load-bearing downstream: the route
    builds only a record whose status is not `approved`, `build_board_previews.py` refuses a
    section whose `styles` is neither empty nor exactly three, and the project-2 approval is
    kept rather than discarded so the picks already made are not retyped.

    The status is `boarded` rather than `draft` since the video sections were added (spec §9
    amendment 7): the record has been through a board and is waiting on the breeder, which is
    what `boarded` means. What the route cares about is only that it is not `approved`."""
    rec = json.loads((ROOT / "data" / "boards" / "index.json").read_text())
    # 2026-09-20: the breeder approved the homepage board, so the status is now `approved`
    # and the route no longer renders it; the two remaining properties still hold.
    assert rec["meta"]["status"] in ("draft", "boarded", "approved"), rec["meta"]["status"]
    assert rec["approval"] is None or rec["approval"]["approved_at"] >= "2026-09-20"  # the 2026-09-20 board approval
    assert rec["approval_previous"], "the project-2 approval is kept, not discarded"
    assert len(rec["sections"]) >= 12
    for s in rec["sections"]:
        assert s.get("styles") == ["S1", "S2", "S3"], s["id"]
    P.validate_styles(rec)


def test_picked_sections_skips_a_section_the_board_offers_nothing_for():
    import build_page_board as BPB
    import json as _json
    from test_page_board import MIN_BOARD
    b = _json.loads(_json.dumps(MIN_BOARD))
    sid = b["sections"][0]["id"]
    empty = {"pools": {}, "pages": {}}
    stocked = {"pools": {"inventory": ["avail-b"]}, "pages": {}}
    # Nothing in the pool and nothing already picked: no control, so no answer is owed.
    assert BPB.picked_sections(b, empty, "x") == []
    # A stocked pool is a real question and is still asked.
    assert BPB.picked_sections(b, stocked, "x") == [sid]
    # And with no ledger passed, the old rule stands.
    assert BPB.picked_sections(b) == [sid]


# --- working rule 16: the per-page hero and counter sets ----------------------------------
#
# "No two pages share the same hero layout or the same counter strip." The construction that
# delivers it is six sets of three, one per LAYOUT FAMILY, and the guarantee is only as good
# as the distinctness of the eighteen: two families sharing an arrangement would let two pages
# of different types ship the same hero while every within-set check stayed green. So the
# tuples are checked across all eighteen, not within each three.

PER_PAGE_RX = re.compile(
    r"def\('([HC]-[A-Z]{2}[123])',\s*'(.*?)',\s*(\{.*?\})\),", re.S)
FAMILY_RX = re.compile(r"^  '?([a-z-]+)'?:\s*\[\s*$", re.M)


def _parse_per_page(const_name):
    """{family: [(id, name, layout dict), ×3]} out of one of the two per-page maps.

    Brittle in the same deliberate way as `_parse_style_map`: it expects the `def(…)` form
    the file is written in, and the count assertions below fail loudly on a reformat rather
    than quietly testing nothing."""
    import ast
    src = TS.read_text(encoding="utf-8").split("export const " + const_name, 1)[1]
    src = src.split("\n};", 1)[0]
    out, order = {}, [m.group(1) for m in FAMILY_RX.finditer(src)]
    chunks = re.split(FAMILY_RX, src)[1:]
    for i in range(0, len(chunks), 2):
        fam, body = chunks[i], chunks[i + 1]
        rows = []
        for m in PER_PAGE_RX.finditer(body):
            obj = re.sub(r"(\w+):", r"'\1':", " ".join(m.group(3).split()))
            rows.append((m.group(1), m.group(2), ast.literal_eval(obj)))
        out[fam] = rows
    assert list(out) == order, (list(out), order)
    return out


HERO_SETS = _parse_per_page("HERO_STYLES_BY_PAGE_TYPE")
COUNTER_SETS = _parse_per_page("COUNTER_STYLES_BY_PAGE_TYPE")
FAMILIES = ["home", "for-sale", "interior-guide", "interior-about", "interior-utility", "blog"]


@pytest.mark.parametrize("sets,which", [(HERO_SETS, "hero"), (COUNTER_SETS, "stats")])
def test_every_layout_family_offers_exactly_three(sets, which):
    assert list(sets) == FAMILIES, sorted(sets)
    assert all(len(v) == 3 for v in sets.values()), {k: len(v) for k, v in sets.items()}


@pytest.mark.parametrize("sets,which", [(HERO_SETS, "hero"), (COUNTER_SETS, "stats")])
def test_no_per_page_style_sets_an_axis_its_renderer_ignores(sets, which):
    allowed = set(AXES[which])
    for fam, rows in sets.items():
        for sid, _name, layout in rows:
            assert set(layout) <= allowed, (fam, sid, sorted(set(layout) - allowed))


@pytest.mark.parametrize("sets,which", [(HERO_SETS, "hero"), (COUNTER_SETS, "stats")])
def test_all_eighteen_per_page_styles_have_distinct_axis_tuples(sets, which):
    """Within a set AND across the six sets. A tuple shared by two families is how two pages
    of different types come to ship the same arrangement with rule 16 still reporting green."""
    axes = AXES[which]
    seen = {}
    for fam, rows in sets.items():
        for sid, _name, layout in rows:
            key = tuple(layout.get(a) for a in axes)
            assert key not in seen, (
                f"{which}: {sid} ({fam}) renders exactly what {seen[key]} does — {key}")
            seen[key] = f"{sid} ({fam})"
    assert len(seen) == 18, len(seen)


@pytest.mark.parametrize("sets", [HERO_SETS, COUNTER_SETS])
def test_per_page_ids_and_names_are_unique(sets):
    ids = [sid for rows in sets.values() for sid, _n, _l in rows]
    names = [n for rows in sets.values() for _s, n, _l in rows]
    assert len(set(ids)) == 18, sorted(ids)
    assert len(set(names)) == 18, sorted(names)


def test_the_python_side_knows_the_same_eighteen_ids():
    """`scripts/build_board_previews.py` carries the id TRIPLES so it can refuse a record
    that mixes two families' styles. A second copy of a list is a copy that drifts, so the
    two are read here and compared."""
    ts_ids = {sid for sets in (HERO_SETS, COUNTER_SETS)
              for rows in sets.values() for sid, _n, _l in rows}
    py_ids = {sid for triple in BBP.PER_PAGE_TRIPLES for sid in triple}
    assert ts_ids == py_ids, sorted(ts_ids ^ py_ids)
    assert all(len(t) == 3 for t in BBP.PER_PAGE_TRIPLES)


def test_a_record_mixing_two_families_styles_is_refused():
    """Three ids that each exist, from three different sets. Every one of them resolves, and
    the combination is still a pick no page type offers."""
    with pytest.raises(BBP.StyleError, match="per-page"):
        BBP.validate_styles({"sections": [
            {"id": "top", "styles": ["H-FS1", "H-GD2", "H-UT3"]}]})


def test_a_per_page_triple_is_accepted_and_so_is_the_legacy_one():
    assert BBP.validate_styles({"sections": [
        {"id": "top", "styles": ["H-FS1", "H-FS2", "H-FS3"]},
        {"id": "glance", "styles": ["C-FS1", "C-FS2", "C-FS3"]},
        {"id": "old", "styles": ["S1", "S2", "S3"]},
    ]})


# --- and the figures those counters print -------------------------------------------------

def test_every_stats_row_in_every_record_resolves_to_a_file_on_disk():
    """Rule 9 through working rule 16: a counter figure carries the path it came from, and a
    path nobody resolves is a citation format rather than a citation."""
    bad = []
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        record = json.loads(f.read_text(encoding="utf-8"))
        bad += [(f.stem, *row) for row in PB.stat_source_problems(record)]
    assert bad == [], bad


@pytest.mark.parametrize("spec,want", [
    ("data/settings.json#deposit_gbp", 500),
    ("data/puppies.json#len", 6),
    ("data/puppies.json#count(status=Available)", 6),
])
def test_the_source_resolver_reads_the_three_forms(spec, want):
    assert PB.resolve_stat_source(spec) == want


@pytest.mark.parametrize("spec", [
    "not-a-source",
    "data/settings.json#no_such_key",
    "data/nope.json#len",
    "data/settings.json#count(status=Available)",
])
def test_the_source_resolver_refuses_what_does_not_resolve(spec):
    """A resolver that silently returned None for a bad path would make the gate above
    report PASS over exactly the numbers it exists to catch."""
    with pytest.raises(PB.SourceError):
        PB.resolve_stat_source(spec)
