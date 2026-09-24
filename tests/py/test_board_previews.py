"""scripts/build_board_previews.py — the cutter that turns the built preview route into
the board's per-style blocks, and the style-option rule the record has to satisfy first."""
import html as html_mod
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
    # The fixture carries the INTERIOR-UTILITY sets. It is the only record that can: the
    # three utility pages (privacy, thank-you, contact) were built before working rule 16 and
    # still name S1/S2/S3, so without the fixture those six arrangements would be six styles
    # nothing ever builds, renders or measures.
    assert rec["meta"]["layout_type"] == "interior-utility"
    offered = {s["id"]: s["styles"] for s in rec["sections"]}
    assert offered["opening"] == ["H-UT1", "H-UT2", "H-UT3"]
    assert offered["at-a-glance"] == ["C-UT1", "C-UT2", "C-UT3"]
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
    # THREE, not the shape-wide trio by name. The homepage came under working rule 16 with the
    # rest of the four pre-rule-16 pages, so its hero and its counter offer the HOME family's
    # own arrangements (`H-HM1..3`, `C-HM1..3`, spec §9 amendment 10.2) and everything else
    # still offers `S1`/`S2`/`S3`. What `build_board_previews.py` refuses is a `styles` that is
    # neither empty nor exactly three, which is the property this line was always standing in
    # for; naming the trio made the assertion fail the day the rule it predates arrived.
    PER_PAGE = {"hero": ["H-HM1", "H-HM2", "H-HM3"], "stats": ["C-HM1", "C-HM2", "C-HM3"]}
    for s in rec["sections"]:
        assert s.get("styles") == PER_PAGE.get(s["shape"], ["S1", "S2", "S3"]), s["id"]
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


# The axes a distinctness claim is made on, read out of src/lib/boardStyles.ts rather than
# retyped: a second copy of the list is a copy that drifts, and the whole point of naming them
# in one place is that the rule and the styles cannot disagree about what "different" means.
def _structural_axes():
    src = TS.read_text(encoding="utf-8").split("export const STRUCTURAL_AXES", 1)[1]
    src = src.split("};", 1)[0]
    return {m.group(1): re.findall(r"'(\w+)'", m.group(2))
            for m in re.finditer(r"^\s*([a-z]+):\s*\[(.*?)\],\s*$", src, re.M)}


STRUCTURAL = _structural_axes()


def test_the_structural_axes_are_read_from_the_source_and_are_what_we_think():
    """`stack` is `media === 'top'`, not an axis of Layout: left-against-right is a mirror of
    one arrangement, top-against-side is two. `heading` is absent on purpose — it moves a
    label, not a layout."""
    assert STRUCTURAL == {"hero": ["hero", "ledge", "stack", "frame"],
                          "stats": ["tiles", "label", "frame", "columns"]}, STRUCTURAL
    for which, axes in STRUCTURAL.items():
        assert "media" not in axes and "heading" not in axes and "align" not in axes, (which, axes)
        # every structural axis except the derived `stack` must be one the renderer reads
        assert set(axes) - {"stack"} <= set(AXES[which]), (which, axes)


def _structural_key(which, layout):
    return tuple(
        ("top" if layout.get("media") == "top" else "side") if axis == "stack"
        else layout.get(axis)
        for axis in STRUCTURAL[which])


@pytest.mark.parametrize("sets,which", [(HERO_SETS, "hero"), (COUNTER_SETS, "stats")])
def test_every_pair_of_the_eighteen_differs_on_two_structural_axes(sets, which):
    """WITHIN a family and ACROSS families, and two axes rather than one.

    One axis apart is not an arrangement apart: `H-GD1` and `H-AB1` were a guide hero and an
    about hero that differed by which side the photo sat on, and `C-FS1` and `C-BL1` were the
    same counter with a different column count. A board offering either pair is offering one
    arrangement twice, and working rule 16's promise — no two pages share a hero or a counter —
    is kept by the id, not by the layout. So: two."""
    keys = {}
    for fam, rows in sets.items():
        for sid, _name, layout in rows:
            keys[f"{sid} ({fam})"] = _structural_key(which, layout)
    assert len(keys) == 18, sorted(keys)
    names = sorted(keys)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = sum(1 for x, y in zip(keys[a], keys[b]) if x != y)
            assert d >= 2, (
                f"{which}: {a} and {b} are {d} structural axis apart — "
                f"{keys[a]} against {keys[b]} on {STRUCTURAL[which]}")


@pytest.mark.parametrize("sets,which,axis", [(HERO_SETS, "hero", "hero"),
                                             (COUNTER_SETS, "stats", "tiles")])
def test_each_family_offers_three_different_layouts_not_three_variations(sets, which, axis):
    """A menu whose three options share a layout is two options and a variation of one."""
    for fam, rows in sets.items():
        got = [l.get(axis) for _s, _n, l in rows]
        assert len(set(got)) == 3, (which, fam, got)


def test_a_hero_layout_and_its_media_placement_agree():
    """`stacked` is the arrangement whose photo is ABOVE the copy and `split` is the one whose
    photo is beside it — a def that says otherwise describes a layout the CSS will not build."""
    for fam, rows in HERO_SETS.items():
        for sid, _n, l in rows:
            top = l.get("media") == "top"
            if l.get("hero") == "stacked":
                assert top, (sid, fam, l)
            # `panel` is text-led and takes its photo on either side OR above: a title panel
            # with a slim photo band over it is the same text-led arrangement, and it is the
            # one the utility set's H-UT3 is. Only `split` is side-by-side by definition.
            if l.get("hero") == "split":
                assert not top, (sid, fam, l)


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

@pytest.mark.parametrize("spec,want", [
    ("data/settings.json#deposit_gbp", 500),
    ("data/settings.json#delivery_max_gbp", 350),
    ("data/puppies.json#len", 6),
    ("data/puppies.json#count(status=Available)", 6),
    ("data/puppies.json#count(sex=female)", 3),
    ("src/content/blog#files(*.md)", 1),
    ("data/boards/blue-staffy-health-uk.json#len(sections[dna-tests].table.rows)", 2),
    ("data/boards/uk-blue-staffy-puppy-buying-guide.json#len(sections[breeder-questions].table.rows)", 15),
    ("data/boards/uk-staffordshire-bull-terrier-guide.json"
     "#cell(sections[breed-facts].table.rows, Lifespan)",
     "12 to 14 years with good care and good genetics"),
])
def test_the_source_resolver_reads_every_form(spec, want):
    assert PB.resolve_stat_source(spec) == want


def test_a_section_is_found_by_id_not_by_position():
    """`sections[costs]` has to survive a section being inserted above it. An index that
    silently shifted would resolve to a different fact and still report green, which is the
    one failure a source check cannot afford."""
    record = json.loads((ROOT / "data/boards/uk-blue-staffy-puppy-buying-guide.json")
                        .read_text(encoding="utf-8"))
    positions = [s["id"] for s in record["sections"]]
    assert positions.index("costs") > 0, "the fixture only means something mid-list"
    by_id = PB.resolve_stat_source(
        "data/boards/uk-blue-staffy-puppy-buying-guide.json#len(sections[costs].table.rows)")
    by_index = PB.resolve_stat_source(
        "data/boards/uk-blue-staffy-puppy-buying-guide.json"
        "#len(sections[%d].table.rows)" % positions.index("costs"))
    assert by_id == by_index == 4


@pytest.mark.parametrize("spec", [
    "not-a-source",
    "data/settings.json#no_such_key",
    "data/nope.json#len",
    "data/settings.json#count(status=Available)",
    "data/boards/_demo.json#len(sections[no-such-section].table.rows)",
    "data/boards/uk-staffordshire-bull-terrier-guide.json"
    "#cell(sections[breed-facts].table.rows, No Such Trait)",
    "src/content/nowhere#files(*.md)",
])
def test_the_source_resolver_refuses_what_does_not_resolve(spec):
    """A resolver that silently returned None for a bad path would make the gate report PASS
    over exactly the numbers it exists to catch."""
    with pytest.raises(PB.SourceError):
        PB.resolve_stat_source(spec)


@pytest.mark.parametrize("spec", [
    "data/facts/blue-staffy-uk-breeders.json#tests",      # a three-item array
    "data/facts/buy-staffy-puppies-for-sale-uk.json#tests",  # a five-item array
    "data/settings.json#socials",                         # a whole object
])
def test_a_source_that_lands_on_a_list_or_an_object_is_refused(spec):
    """THE DEFECT THIS RULE WAS WRITTEN FOR. Both `#tests` sources resolved without error and
    proved nothing: one is a five-item array, the other a three-item array, and both stood
    behind a tile printing "2". A value a figure cannot be compared against is not a source."""
    with pytest.raises(PB.SourceError, match="not a single value"):
        PB.resolve_stat_source(spec)


# ── the figure has to be IN what its sources resolved to ──────────────────────────────────

@pytest.mark.parametrize("n,values", [
    ("£500", [500]),
    ("£1,500", [1500]),
    ("6", [6]),
    ("£200–£350", [200, 350]),
    ("11–17 kg", ["11 to 17 kg (24 to 38 lbs), males generally at the higher end"]),
    ("12–14 years", ["12 to 14 years with good care and good genetics"]),
    ("14–16 in", ["14 to 16 inches (35 to 41 cm)"]),
    ("Clear", ["DNA tested clear"]),          # no digits to check
    # `L-2-HGA` and `HC-HSF4` are the NAMES of two DNA tests. A digit rule that read them as
    # quantities would demand a source for a test's name, so only standalone numbers count.
    ("L-2-HGA and HC-HSF4 tested clear", ["DNA tested clear"]),
])
def test_a_figure_whose_numbers_are_in_its_sources_passes(n, values):
    assert PB.figure_matches(n, values)


@pytest.mark.parametrize("n,values", [
    ("2", [["L-2-HGA", "HC-HSF4", "DNA", "microchip", "vaccinat"]]),  # the original defect
    ("2", [None]),
    ("12–17 kg", ["11 to 17 kg (24 to 38 lbs)"]),                     # first number wrong
    ("17–11 kg", ["11 to 17 kg (24 to 38 lbs)"]),                     # right numbers, wrong ORDER
    ("£200–£350", [200]),                                             # the range half-sourced
    ("£1,700", [1500]),
    ("7", [6]),
])
def test_a_figure_whose_numbers_are_not_in_its_sources_fails(n, values):
    assert not PB.figure_matches(n, values)


def test_a_range_needs_both_of_its_sources():
    """`£200–£350` is two facts. Citing only the minimum leaves the maximum unsourced while
    reading as sourced, which is the state every delivery tile shipped in before this."""
    row_one = {"n": "£200–£350", "source": "data/settings.json#delivery_min_gbp"}
    row_both = {"n": "£200–£350", "source": ["data/settings.json#delivery_min_gbp",
                                             "data/settings.json#delivery_max_gbp"]}
    assert PB.sources_of(row_one) == ["data/settings.json#delivery_min_gbp"]
    assert len(PB.sources_of(row_both)) == 2
    assert not PB.figure_matches(row_one["n"], PB.resolve_stat_sources(row_one))
    assert PB.figure_matches(row_both["n"], PB.resolve_stat_sources(row_both))


def test_a_row_citing_no_source_at_all_is_refused():
    with pytest.raises(PB.SourceError):
        PB.resolve_stat_sources({"n": "6", "label": "puppies"})


def test_every_stats_row_in_every_record_resolves_and_matches():
    """Rule 9 through working rule 16, over the real records: a counter figure carries the
    paths it came from, every one of them resolves to a single value, and the numbers the
    tile prints are in what they resolved to."""
    bad = []
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        record = json.loads(f.read_text(encoding="utf-8"))
        bad += [(f.stem, *row) for row in PB.stat_source_problems(record)]
    assert bad == [], bad


def test_the_record_sweep_is_not_vacuous():
    """The sweep above passes trivially over records with no `stats`. Count the rows."""
    rows = sum(len(s.get("stats") or [])
               for f in (ROOT / "data/boards").glob("*.json")
               for s in json.loads(f.read_text(encoding="utf-8"))["sections"])
    assert rows >= 30, f"only {rows} sourced figure(s) on the boards — the sweep proves little"


# ── the two lists that exist in TypeScript and in Python ──────────────────────────────────

def test_the_page_type_union_matches_the_schema_enum():
    """`LAYOUT_BY_PAGE_TYPE` maps every page type to a layout family. A type added to the
    schema and forgotten there does not raise — it falls through to the guide set, which is a
    page silently offered the wrong three heroes."""
    schema = json.loads((ROOT / "schemas/board.schema.json").read_text(encoding="utf-8"))
    enum = set(schema["properties"]["meta"]["properties"]["page_type"]["enum"])
    src = TS.read_text(encoding="utf-8")
    union = set(re.findall(r"'([a-z-]+)'",
                           src.split("export type PageType =", 1)[1].split(";", 1)[0]))
    table = set(re.findall(r"^\s*'?([a-z-]+)'?:\s*'[a-z-]+',\s*$",
                           src.split("const LAYOUT_BY_PAGE_TYPE", 1)[1].split("};", 1)[0], re.M))
    assert union == enum, sorted(union ^ enum)
    assert table == enum, sorted(table ^ enum)


def test_per_page_shapes_agrees_across_typescript_python_and_this_file():
    """The hero and the counter are what a re-board re-asks. Two copies of that list that
    disagree is a section re-asked on the board and locked in the record, or the reverse."""
    ts = re.findall(r"'(\w+)'",
                    TS.read_text(encoding="utf-8")
                      .split("export const PER_PAGE_SHAPES", 1)[1].split(";", 1)[0])
    assert tuple(ts) == tuple(PB.PER_PAGE_SHAPES) == ("hero", "stats"), (ts, PB.PER_PAGE_SHAPES)


# ── the picks a re-boarded record carries forward ─────────────────────────────────────────

def _carry_board(**over):
    """A two-section record with an approval to carry: one prose section and one hero."""
    prose = {"id": "prose", "shape": "standard", "heading": "Prose",
             "styles": ["S1", "S2", "S3"], "options": {"pick": None}, "n": 2}
    hero = {"id": "top", "shape": "hero", "heading": "Top",
            "styles": ["H-GD1", "H-GD2", "H-GD3"], "options": {"pick": None}, "n": 1}
    board = {"sections": [hero, prose],
             "approval_previous": {"picks": {"prose": "S2", "top": "H-GD1"},
                                   "section_hashes": {}}}
    board["approval_previous"]["section_hashes"] = {
        s["id"]: PB.section_fingerprint(s) for s in board["sections"]}
    for k, v in over.items():
        board[k] = v
    return board


def test_a_carried_pick_is_locked_when_nothing_about_its_section_moved():
    assert PB.locked_picks(_carry_board()) == {"prose": "S2"}


def test_the_per_page_shapes_are_never_carried():
    """They are what the re-board is FOR. Carrying the hero forward would answer the one
    question the breeder was brought back to answer."""
    assert "top" not in PB.locked_picks(_carry_board())


def test_a_pick_for_a_section_that_is_gone_is_not_carried():
    b = _carry_board()
    b["sections"] = [s for s in b["sections"] if s["id"] != "prose"]
    assert PB.locked_picks(b) == {}


def test_a_pick_that_is_no_longer_on_the_menu_is_not_carried():
    """Pre-filling an id `board_approve.py` would then refuse is worse than asking again."""
    b = _carry_board()
    prose = next(s for s in b["sections"] if s["id"] == "prose")
    prose["styles"] = ["C-GD1", "C-GD2", "C-GD3"]
    b["approval_previous"]["section_hashes"]["prose"] = PB.section_fingerprint(prose)
    assert PB.locked_picks(b) == {}


def test_a_pick_whose_section_changed_under_it_is_not_carried():
    """The breeder answered a question about THIS section. Change the question and the answer
    is not theirs any more, whatever the record says."""
    b = _carry_board()
    prose = next(s for s in b["sections"] if s["id"] == "prose")
    prose["heading"] = "Prose, rewritten"
    assert PB.locked_picks(b) == {}


def test_a_refresh_delta_does_not_unlock_a_carried_pick():
    """A delta is a NOTE about which sibling the section departs from; the arrangement it
    departs INTO is the pick, unchanged. Counting it would have unlocked every carried pick
    on the day working rule 16 gave every section a delta."""
    b = _carry_board()
    prose = next(s for s in b["sections"] if s["id"] == "prose")
    prose["refresh"] = {"axis": "accent", "note": "brass as a hairline, not a fill, against the buy pages"}
    assert PB.locked_picks(b) == {"prose": "S2"}


def test_an_approval_with_no_recorded_hashes_locks_nothing():
    """An approval that kept no record of what it approved cannot prove anything stayed still,
    and a lock that cannot prove it is a lock on the breeder's behalf."""
    b = _carry_board()
    b["approval_previous"]["section_hashes"] = {}
    assert PB.locked_picks(b) == {}


def test_a_moved_section_position_does_not_unlock():
    """`n` is where a section sits, not what it says."""
    b = _carry_board()
    next(s for s in b["sections"] if s["id"] == "prose")["n"] = 9
    assert PB.locked_picks(b) == {"prose": "S2"}


def test_the_real_reboarded_records_carry_what_they_should():
    """Four records went back to the board for two questions each. Every other answer they
    already had is still theirs."""
    expected = {"blue-staffy-pup-sale-uk": {"at-a-glance", "top"},
                "buy-blue-staffy-puppies-uk": {"at-a-glance", "top"},
                "buy-staffy-puppies-for-sale-uk": {"top"},
                "blue-staffy-uk-breeders": {"top"}}
    for slug, reasked in expected.items():
        record = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text(encoding="utf-8"))
        prev = set(record["approval_previous"]["picks"])
        locked = set(PB.locked_picks(record))
        assert locked, f"{slug} carried nothing forward"
        assert prev - locked == reasked, (slug, sorted(prev - locked))


def test_a_locked_radio_is_checked_and_disabled_and_still_submits():
    """The board's approve button reads `input[name^="pick-"]:checked`. A disabled radio still
    matches that selector, which is what lets a carried answer be submitted and not changed."""
    import build_page_board as BPB
    record = json.loads((ROOT / "data/boards/blue-staffy-pup-sale-uk.json")
                        .read_text(encoding="utf-8"))
    locked = PB.locked_picks(record)
    assert locked, "the fixture record carries nothing — this test would prove nothing"
    sid, pick = sorted(locked.items())[0]
    section = next(s for s in record["sections"] if s["id"] == sid)
    html = BPB.style_fieldset(section, {"names": {}, "blocks": {}}, locked)
    assert 'class="styles locked"' in html
    assert f'value="{pick}" checked disabled' in html, html[:400]
    assert html.count(" disabled") == 3, "all three radios are disabled, one of them checked"
    # and an UNLOCKED section is left alone
    plain = BPB.style_fieldset(section, {"names": {}, "blocks": {}}, {})
    assert " disabled" not in plain


def test_a_record_pick_that_disagrees_with_the_carried_one_stops_the_build():
    """Two answers to one question. Quietly preferring either is the board telling the breeder
    they decided something they did not."""
    import build_page_board as BPB
    section = {"id": "prose", "shape": "standard", "heading": "Prose",
               "styles": ["S1", "S2", "S3"], "options": {"pick": "S3", "note": ""}}
    with pytest.raises(PB.BoardError, match="two answers to one question"):
        BPB.style_fieldset(section, {"names": {}, "blocks": {}}, {"prose": "S1"})
    # agreeing is fine
    section["options"]["pick"] = "S1"
    assert BPB.style_fieldset(section, {"names": {}, "blocks": {}}, {"prose": "S1"})


# ── every section carries a refresh delta ─────────────────────────────────────────────────

BOARDED = ("boarded", "approved", "built", "released")


def _under_rule_16(record):
    """A record is under working rule 16 once it names its LAYOUT FAMILY.

    Not an allowlist and not a date: the four pages built before the rule still name S1/S2/S3
    on their hero and carry no `meta.layout_type`, and the later task that refreshes them adds
    one — at which point the two checks below start asking them for what they ask everybody
    else. A slug list here would have to be edited by hand on that day, and would not be."""
    return bool(record["meta"].get("layout_type"))


def test_every_section_of_every_boarded_record_carries_a_refresh_delta():
    """Working rule 16 asks EVERY section for one, not the three to five a page felt like
    writing. The hero and the counter are exempt: they are per-page by construction, and their
    delta is the style set itself."""
    bad = []
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        record = json.loads(f.read_text(encoding="utf-8"))
        if record["meta"]["status"] not in BOARDED or not _under_rule_16(record):
            continue
        bad += [(f.stem, s["id"]) for s in record["sections"]
                if s["shape"] not in PB.PER_PAGE_SHAPES and not s.get("refresh")]
    assert bad == [], bad


def test_the_refresh_sweep_covers_the_eight_records():
    boarded = [f.stem for f in sorted((ROOT / "data/boards").glob("*.json"))
               if json.loads(f.read_text(encoding="utf-8"))["meta"]["status"] in BOARDED
               and _under_rule_16(json.loads(f.read_text(encoding="utf-8")))]
    assert len(boarded) >= 8, boarded


#: A delta is a DEPARTURE, so its note has to name something to have departed from. The list
#: is the ways the notes actually say it — a plain "against the …", a comparative ("roomier
#: than", "the only … on the site"), or a correction ("reversing", "instead of"). It is
#: deliberately generous and still rejects a bare description of the section, which is what
#: four of them were before this test existed.
COMPARATIVE = ("against", "rather than", "instead", "not the", "not a", "where", "unlike",
               "than", "no other", "the only", "matching", "reversing", "any guide")


def test_a_refresh_note_says_what_it_is_a_delta_from():
    """A delta with no sibling named is a description of a section, not a departure from one.
    The skill's wording: what the delta is, and which page it is a delta FROM."""
    thin = []
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        for s in json.loads(f.read_text(encoding="utf-8"))["sections"]:
            r = s.get("refresh")
            if r and not any(w in r["note"].lower() for w in COMPARATIVE):
                thin.append((f.stem, s["id"], r["note"]))
    assert thin == [], thin


# ── the counter strip's deprecated fallback ───────────────────────────────────────────────

def test_no_board_record_relies_on_the_counter_strips_fallback_figures():
    """CounterStrip used to print three site-wide figures when a page passed none; it now stops
    the build instead. A stats section with no rows of its own is therefore a board whose
    counter cannot render at all."""
    bad = []
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        record = json.loads(f.read_text(encoding="utf-8"))
        if not _under_rule_16(record):
            continue          # the four built before the rule; their counters are a later task
        for s in record["sections"]:
            if s["shape"] == "stats" and not (s.get("stats") or []):
                bad.append((f.stem, s["id"]))
    assert bad == [], bad
    assert any(_under_rule_16(json.loads(f.read_text(encoding="utf-8")))
               for f in (ROOT / "data/boards").glob("*.json")), "the sweep examined nothing"


def test_the_counter_strip_has_no_figures_of_its_own():
    """The fallback was kept on sufferance for the four pages built before working rule 16 and
    went with the last of their rebuilds. The component reads no data file and refuses an
    empty `stats`, so no page can reach site-wide figures by omission."""
    src = (ROOT / "src/components/kit/CounterStrip.astro").read_text(encoding="utf-8")
    front = src.split("---")[1]
    imports = [l for l in front.splitlines() if l.startswith("import ")]
    assert not [l for l in imports if "data/" in l or "lib/site" in l], (
        "the strip reads a data file again", imports)
    assert "fallback" not in front.split("const {")[1], "a fallback figure set is back"
    assert "throw new Error" in front, "an empty strip must stop the build"


def test_the_hero_has_no_default_photograph():
    """Amendment 10.7 kept `image` defaulting to a kit master while the four early pages relied
    on it. They pass their own now, so a hero with no photo says media="none" or stops."""
    src = (ROOT / "src/components/kit/Hero.astro").read_text(encoding="utf-8")
    front = src.split("---")[1]
    imports = [l for l in front.splitlines() if l.startswith("import ")]
    assert not [l for l in imports if "assets/" in l], ("Hero imports a photo again", imports)
    assert re.search(r"^\s*image,\s*$", front, re.M), "`image` has a default again"


# ── the gate does not read a build in progress ────────────────────────────────────────────

def test_a_built_page_older_than_its_sources_is_not_fresh(tmp_path):
    """`min-h5-h6` read `dist/` mid-build and flipped on the same record. A file existing is
    not a build having finished."""
    import time
    (tmp_path / "src").mkdir()
    (tmp_path / "dist").mkdir()
    built = tmp_path / "dist/index.html"
    built.write_text("<h5>x</h5>", encoding="utf-8")
    assert PB.dist_page_is_fresh(built, tmp_path)
    time.sleep(0.01)
    (tmp_path / "src/page.astro").write_text("edited\n", encoding="utf-8")
    assert not PB.dist_page_is_fresh(built, tmp_path)


def test_a_missing_built_page_is_never_fresh(tmp_path):
    assert not PB.dist_page_is_fresh(tmp_path / "dist/nope.html", tmp_path)


def test_the_preview_payloads_do_not_make_every_build_stale(tmp_path):
    """`data/boards/previews/` is written BY the build. Counting it would make every build
    instantly stale against its own output."""
    import time
    (tmp_path / "data/boards/previews").mkdir(parents=True)
    (tmp_path / "dist").mkdir()
    built = tmp_path / "dist/index.html"
    built.write_text("x", encoding="utf-8")
    time.sleep(0.01)
    (tmp_path / "data/boards/previews/x.json").write_text("{}", encoding="utf-8")
    assert PB.dist_page_is_fresh(built, tmp_path)


def test_a_siblings_record_does_not_make_this_pages_dist_stale(tmp_path):
    """Two agents in one tree. Agent A writing data/boards/<other>.json made EVERY page read
    as stale, `min-h5-h6` fell back to the record tree, and a page whose built file was
    perfectly current failed the gate. Freshness is a question about one page."""
    import time
    (tmp_path / "src/pages/mine").mkdir(parents=True)
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "dist/mine").mkdir(parents=True)
    (tmp_path / "src/pages/mine/index.astro").write_text("page", encoding="utf-8")
    (tmp_path / "data/boards/mine.json").write_text("{}", encoding="utf-8")
    built = tmp_path / "dist/mine/index.html"
    built.write_text("<h5>x</h5>", encoding="utf-8")
    time.sleep(0.01)
    (tmp_path / "data/boards/other.json").write_text("{}", encoding="utf-8")
    assert PB.dist_page_is_fresh(built, tmp_path, slug="mine")
    # ...and the whole-tree sweep, which a caller that cannot name a page still gets, is the
    # reading that was wrong. Kept in the same test so the contrast cannot drift apart.
    assert not PB.dist_page_is_fresh(built, tmp_path)


def test_the_pages_own_sources_and_the_shared_shell_still_make_it_stale(tmp_path):
    """Narrowing the sweep is only safe if it still catches what a page is actually built
    from: its own file, its own record, and the kit every page renders through."""
    import time

    def tree():
        for d in ("src/pages/mine", "data/boards", "dist/mine", "src/components/kit", "src/lib"):
            (tmp_path / d).mkdir(parents=True, exist_ok=True)
        (tmp_path / "src/pages/mine/index.astro").write_text("page", encoding="utf-8")
        (tmp_path / "data/boards/mine.json").write_text("{}", encoding="utf-8")
        b = tmp_path / "dist/mine/index.html"
        b.write_text("x", encoding="utf-8")
        return b

    for rel in ("src/pages/mine/index.astro", "data/boards/mine.json",
                "src/components/kit/Hero.astro", "src/lib/boardStyles.ts", "data/puppies.json"):
        built = tree()
        assert PB.dist_page_is_fresh(built, tmp_path, slug="mine"), rel
        time.sleep(0.01)
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("edited", encoding="utf-8")
        assert not PB.dist_page_is_fresh(built, tmp_path, slug="mine"), rel


def test_the_root_slugs_page_is_src_pages_index_astro(tmp_path):
    """`index` is the slug this repo gives "/", and `src/pages/index/index.astro` exists on
    no tree — the same spelling amendment 9.3 fixed in four other places."""
    import time
    (tmp_path / "src/pages").mkdir(parents=True)
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "dist").mkdir(parents=True)
    (tmp_path / "src/pages/index.astro").write_text("home", encoding="utf-8")
    built = tmp_path / "dist/index.html"
    built.write_text("x", encoding="utf-8")
    assert PB.dist_page_is_fresh(built, tmp_path, slug="index")
    time.sleep(0.01)
    (tmp_path / "src/pages/index.astro").write_text("edited", encoding="utf-8")
    assert not PB.dist_page_is_fresh(built, tmp_path, slug="index")


# ── the delta is printed where the pick is made ───────────────────────────────────────────

def test_the_refresh_delta_is_printed_under_a_sections_options():
    import build_page_board as BPB
    sec = {"id": "prices", "shape": "table", "heading": "Prices",
           "refresh": {"axis": "accent", "note": "the price table on a brand header band"}}
    html = BPB.refresh_line(sec)
    assert "Refresh" in html and "accent" in html
    assert "the price table on a brand header band" in html
    assert BPB.refresh_line({"id": "x", "shape": "standard"}) == "", "no delta, no empty row"


def test_every_delta_reaches_the_built_board_including_the_locked_ones():
    """A delta the breeder cannot see is a decision taken on their behalf, and it matters most
    under a LOCKED fieldset: the pick says "you already chose this" and the note says what has
    changed about the section since."""
    from html import escape
    for slug in ("blue-staffy-pup-sale-uk", "uk-blue-staffy-puppy-buying-guide"):
        page = ROOT / "docs/artifacts/boards" / f"{slug}.html"
        if not page.exists():
            pytest.skip("run scripts/build_page_board.py first")
        html = page.read_text(encoding="utf-8")
        record = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text(encoding="utf-8"))
        deltas = [s for s in record["sections"] if s.get("refresh")]
        assert deltas, slug
        missing = [s["id"] for s in deltas if escape(s["refresh"]["note"], quote=False) not in html]
        assert missing == [], (slug, missing)
        assert html.count('class="refresh"') == len(deltas), slug
        # and at least one of them sits under a fieldset the record is carrying a pick across
        locked = PB.locked_picks(record)
        if locked:
            both = [s for s in deltas if s["id"] in locked]
            assert both, f"{slug} locks picks but prints no delta beside any of them"


# ── pickedStyle(): a page may only mount a style its own section offered ───────────────────
#
# The TypeScript has no unit harness in this repo, so the guard is proved from two directions
# rather than one: the source is held to enforcing it, and the invariant it enforces is checked
# against every record on disk. Added in the review of 0128e21, where `pickedStyle()` had been
# widened to resolve working rule 16's per-page ids (`H-FS3`, `C-FS1`) through the global
# `STYLES_BY_ID` map and, in doing so, had stopped asking whether the id it found belonged to
# the section that named it.

PICKED_STYLE_TS = (ROOT / "src/lib/pickedStyle.ts").read_text(encoding="utf-8")


def test_picked_style_reuses_style_by_id_and_refuses_a_style_the_section_never_offered():
    """It resolves through the shared helpers and throws on a def outside the section's menu.

    `styleById()` is deliberately forgiving — an id it cannot place falls back to the first
    style of the trio — which is right for a preview route and wrong for a page: the fallback
    would be an arrangement nobody chose, rendering perfectly fine. So the resolved def is
    checked for membership of `stylesForSection()`, the same menu the board preview rendered,
    and the chain is not re-implemented here where it could drift from the one the preview
    calls."""
    src = PICKED_STYLE_TS
    assert "styleById(" in src, "the id chain is reused, not copied"
    assert "STYLES_BY_ID" not in src, "resolving by id belongs to styleById(), not to a copy here"
    offered = src.split("const offered = ", 1)
    assert len(offered) == 2 and offered[1].startswith("stylesForSection("), \
        "the menu comes from stylesForSection(), the call the preview route makes"
    guard = src.split("const found = styleById(", 1)[1]
    assert "offered.some((s) => s.id === found.id)" in guard, "membership is asserted"
    assert "throw new Error(" in guard, "and a non-member throws rather than rendering"


def test_every_record_pick_is_one_of_that_sections_own_styles():
    """The invariant the guard enforces, against the records as they stand.

    `board_approve.py` refuses a pick outside the section's `styles` at approval time; this is
    the second opinion on what is on disk now, and it is what would have caught a `stats`
    section carrying a hero's id — which resolves by id, renders, and is nobody's decision."""
    bad = []
    for path in sorted((ROOT / "data/boards").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        picks = dict(((record.get("approval") or {}).get("picks") or {}))
        for section in record["sections"]:
            styles = section.get("styles") or []
            pick = picks.get(section["id"]) or (section.get("options") or {}).get("pick")
            if not pick or not styles:
                continue
            if pick not in styles:
                bad.append(f"{record['meta']['slug']}/{section['id']}: {pick} not in {styles}")
    assert bad == [], bad


# ── A RE-BOARD MUST NOT CHANGE THE PAGE UNDER IT ──────────────────────────────────────────
#
# Spec §9 amendment 11, the re-board rule (breeder 2026-09-21). The four pages built before
# working rule 16 were the first records ever re-boarded while their page was LIVE, and the
# first build after it broke every one of them: `record.approval` is null under a re-board,
# and `record.approval!.meta!.title`, `.description`, `.h1` and `pickedStyle()` all read it.
#
# `approvalInForce()` and `pickedStyle()`'s carried-pick fallback are what fixed it, and the
# guarantee they make is exact: THE BUILT PAGE DOES NOT MOVE. That was verified once by
# diffing `dist/` against a build of HEAD, which proves it for one commit and for no other.
# This is the durable form of the same claim — the page still renders precisely what the
# carried approval says, index for index and pick for pick, so a regression in either helper
# shows up as a page that has stopped matching the answers the breeder actually gave.
#
# THE RE-BOARD WAS ANSWERED on 2026-09-22 (`2ce9e93`), and a record can go BACK: the homepage
# was re-boarded a second time for its mosaic and its figure tiles (Known Issue 33, user ruling
# R11). So the two tests below hold either state. A record ON THE BOARD (`approval` null)
# renders the carried approval and carries every answer the board is not asking again; an
# ANSWERED record renders the live approval, and the live one differs from the carried one only
# on the hero and the counter — or on neither, when the question was the hero's content rather
# than its arrangement.
RE_BOARDED = ("index", "privacy-policy-uk", "thank-you-blue-staffy-puppies-journey",
              "uk-blue-staffy-breeders-contact")


def _built(slug):
    # The root slug's built file is dist/index.html (spec §9 amendment 9.3).
    return ROOT / "dist" / ("index.html" if slug == "index" else f"{slug}/index.html")


def _per_page(rec):
    return {s["id"] for s in rec["sections"] if s["shape"] in PB.PER_PAGE_SHAPES}


@pytest.mark.parametrize("slug", RE_BOARDED)
def test_a_re_boarded_record_renders_the_approval_in_force(slug):
    """The page renders the approval IN FORCE — the live one once the re-board is answered, the
    carried one while it is on the board — index for index, and no answer the board did not ask
    again has moved. Before the first re-board was answered this test held the page to
    `approval_previous`; after it, to the live answer; a second re-board puts it back."""
    rec = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text(encoding="utf-8"))
    live, prev = rec["approval"], rec["approval_previous"]
    assert prev and prev.get("picks"), "a re-board keeps the approval it replaced"
    in_force = live or prev
    if live:
        # The three INDICES were not the question, so they are carried unchanged.
        for key in ("title", "description"):
            assert live["meta"][key] == prev["meta"][key], (slug, key, "moved under a re-board")
        assert live["h1"] == prev["h1"], (slug, "the H1 index moved under a re-board")
        for sid, pick in prev["picks"].items():
            if sid in _per_page(rec):
                continue
            assert live["picks"].get(sid) == pick, (
                slug, sid, "a carried answer changed when the re-board was approved")
    else:
        # ON THE BOARD: every answer it is not asking again is locked, exactly as carried.
        locked = PB.locked_picks(rec)
        want = {sid: pick for sid, pick in prev["picks"].items() if sid not in _per_page(rec)}
        assert locked == want, (slug, "the board would re-ask an answered question",
                                sorted(set(want) - set(locked)))

    page = _built(slug)
    if not page.exists():
        pytest.skip("run npm run build first")
    html = page.read_text(encoding="utf-8")
    title = rec["meta_set"]["titles"][in_force["meta"]["title"]]
    description = rec["meta_set"]["descriptions"][in_force["meta"]["description"]]
    h1 = rec["h1"]["variants"][in_force["h1"]]
    # Compared on normalised TEXT: `rules/headings.md` applies Title Case at render and the
    # serializer escapes `&`, so an exact string match would be testing the renderer's
    # spelling rather than which variant the page chose.
    def norm(t):
        return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", t)).split()).casefold()
    got_title = re.search(r"<title>(.*?)</title>", html, re.S)
    assert got_title and norm(got_title.group(1)) == norm(title), (slug, "title index")
    got_desc = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
    assert got_desc and norm(got_desc.group(1)) == norm(description), (slug, "description index")
    got = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    assert got and norm(got.group(1)) == norm(h1), (slug, "H1 index", got and norm(got.group(1)))


@pytest.mark.parametrize("slug", RE_BOARDED)
def test_a_re_boarded_record_asks_or_answered_only_its_hero_and_its_counter(slug):
    """The hero and the counter are `PER_PAGE_SHAPES`, and they are the whole of what a rule-16
    re-board sends a record back for (spec §9 amendment 10.10). On the board, those two are the
    only unlocked styled sections. Answered, every styled section carries a pick, and the only
    picks that differ from the carried approval are on those two shapes — and if none differs,
    the per-page section itself changed, because a re-board that asked nothing is not one."""
    rec = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text(encoding="utf-8"))
    prev = rec["approval_previous"]
    styled = {s["id"] for s in rec["sections"] if s.get("styles")}
    if rec["approval"] is None:
        asked = styled - set(PB.locked_picks(rec))
        assert asked and asked <= _per_page(rec), (slug, sorted(asked))
        return
    unpicked = [s["id"] for s in rec["sections"]
                if s.get("styles") and not (s.get("options") or {}).get("pick")]
    assert unpicked == [], (slug, unpicked)
    moved = [sid for sid, pick in rec["approval"]["picks"].items() if prev["picks"].get(sid) != pick]
    assert all(sid in _per_page(rec) for sid in moved), (slug, moved)
    changed = [s["id"] for s in rec["sections"] if s["id"] in _per_page(rec)
               and (prev.get("section_hashes") or {}).get(s["id"]) != PB.section_fingerprint(s)]
    assert moved or changed, (slug, "a rule-16 re-board answers or changes at least the hero")


def test_the_chrome_preview_grid_cannot_be_widened_by_the_strip():
    """Known Issue 32: at 375 the contact board preview scrolled sideways by 606px. `.bp-chrome`
    was a grid with no column template, so its one implicit track was `auto` and grew to the
    STRIP specimen's min-content — its whole row of links, 933px. The base rule must give the
    track a zero minimum so the strip keeps its own scroller; the 1024px rule adds the dial
    column in front of the same `minmax(0, 1fr)`."""
    src = (ROOT / "src/pages/board-preview/[slug].astro").read_text(encoding="utf-8")
    base = re.search(r"\.bp-chrome\s*\{([^}]*)\}", src)
    assert base, "the preview route no longer styles .bp-chrome"
    assert re.search(r"grid-template-columns:\s*minmax\(0,\s*1fr\)", base.group(1)), (
        "the base .bp-chrome rule needs grid-template-columns: minmax(0, 1fr)")
