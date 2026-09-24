"""scripts/link_diversity.py, Task 5 — anchor-type variation on a new page's links.

Every link on a location, comparison or blog page carries `anchor_type`; the page's in-copy
internal anchors use at least three types with at most two exact-match; its external anchors
use at least three types; and no internal anchor another board already uses for the same
target is reused. The page-level "no anchor twice" rule is pageboard's existing
`links-anchor-duplicate`, and the last test here proves it already holds on these pages.
"""
import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import family_rules as FR      # noqa: E402
import link_diversity as LD    # noqa: E402
import pageboard as PB         # noqa: E402

SLUG = "uk-locations/blue-staffy-puppies-manchester"


def _board(status="boarded", slug=SLUG, page_type="location"):
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text(encoding="utf-8")))
    b["meta"].update(slug=slug, page_type=page_type, status=status)
    return b


def _links(board, internal=(), external=()):
    """internal/external: (href, anchor, anchor_type or None). All go on the first section."""
    def row(h, a, t, **extra):
        d = {"href": h, "anchor": a, **extra}
        if t:
            d["anchor_type"] = t
        return d
    board["sections"][0]["links"] = {
        "internal": [row(h, a, t, sentence_start=True) for h, a, t in internal],
        "external": [row(h, a, t, library_row=h) for h, a, t in external],
    }
    return board


GOOD_INTERNAL = [("/blue-staffy-health-uk/", "Blue Staffy health", "exact"),
                 ("/uk-staffordshire-bull-terrier-guide/", "our Staffordshire Bull Terrier guide", "partial"),
                 ("/buy-blue-staffy-puppies-uk/", "home-raised blue pups", "lsi"),
                 ("/uk-blue-staffy-breeders-contact/", "ask Lisa a question", "natural")]
GOOD_EXTERNAL = [("https://www.gov.uk/a", "the government's licence guidance", "natural"),
                 ("https://www.royalkennelclub.com/d", "The Royal Kennel Club", "branded"),
                 ("https://www.pdsa.org.uk/e", "https://www.pdsa.org.uk/e", "naked-url")]


def _anchor_findings(board):
    ids = {LD.ANCHOR_CHECK, LD.SITEWIDE_CHECK}
    return [f for f in FR.findings(board, None) if f[0] in ids]


@pytest.fixture(autouse=True)
def no_other_boards(tmp_path, monkeypatch):
    """The site-wide check reads data/boards/; point it at an empty directory unless a test
    writes a board there itself."""
    d = tmp_path / "boards"
    d.mkdir()
    monkeypatch.setattr(LD, "BOARDS_DIR", d)
    return d


def test_the_schema_accepts_anchor_type_and_keeps_it_optional():
    schema = json.loads((ROOT / "schemas" / "board.schema.json").read_text(encoding="utf-8"))
    links = schema["properties"]["sections"]["items"]["properties"]["links"]["properties"]
    for kind in ("internal", "external"):
        item = links[kind]["items"]
        assert item["properties"]["anchor_type"]["enum"] == list(LD.ANCHOR_TYPES)
        assert "anchor_type" not in item["required"]


def test_the_built_records_still_validate_and_keep_their_hashes():
    """Optional means the twelve approved records neither fail the schema nor change hash."""
    for p in sorted((ROOT / "data" / "boards").glob("*.json")):
        b = json.loads(p.read_text(encoding="utf-8"))
        PB._validate(b, "board.schema.json")
        appr = b.get("approval") or {}
        if appr.get("record_hash"):
            assert PB.approval_matches(b), p.name


def test_a_varied_page_passes():
    b = _links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL)
    assert _anchor_findings(b) == []


def test_a_link_without_anchor_type_fails():
    b = _links(_board(), GOOD_INTERNAL[:3] + [("/x/", "an untyped anchor", None)], GOOD_EXTERNAL)
    f = _anchor_findings(b)
    assert any(c == LD.ANCHOR_CHECK and s == "FAIL" and "an untyped anchor" in m for c, s, m in f), f


def test_a_draft_only_warns():
    b = _links(_board(status="draft"), GOOD_INTERNAL[:3] + [("/x/", "an untyped anchor", None)], GOOD_EXTERNAL)
    f = _anchor_findings(b)
    assert f and {s for _, s, _ in f} == {"WARN"}


def test_two_internal_types_fail():
    internal = [("/a/", "alpha words", "partial"), ("/b/", "beta words", "natural"),
                ("/c/", "gamma words", "natural")]
    f = _anchor_findings(_links(_board(), internal, GOOD_EXTERNAL))
    assert any("internal anchors use 2 type(s)" in m for _, _, m in f), f


def test_three_exact_internal_anchors_fail():
    internal = GOOD_INTERNAL + [("/a/", "Blue Staffy puppies", "exact"), ("/b/", "Staffy breeder UK", "exact")]
    f = _anchor_findings(_links(_board(), internal, GOOD_EXTERNAL))
    assert any("3 exact-match internal anchor(s)" in m for _, _, m in f), f


def test_nav_links_need_a_type_but_do_not_count_toward_the_mix():
    b = _links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL)
    for n in range(3):
        b["sections"][1]["links"]["internal"].append(
            {"href": f"/tile-{n}/", "anchor": f"Blue Staffy tile {n}", "nav": True, "anchor_type": "exact"})
    assert _anchor_findings(b) == []


def test_two_external_types_fail():
    external = [("https://www.gov.uk/a", "the licence guidance", "natural"),
                ("https://www.pdsa.org.uk/e", "the PDSA's breed advice", "natural"),
                ("https://www.royalkennelclub.com/d", "The Royal Kennel Club", "branded")]
    f = _anchor_findings(_links(_board(), GOOD_INTERNAL, external))
    assert any("external anchors use 2 type(s)" in m for _, _, m in f), f


def test_an_anchor_another_board_uses_for_the_same_target_fails(no_other_boards):
    other = _links(_board(slug="uk-locations/blue-staffy-puppies-leeds"),
                   [("/blue-staffy-health-uk", "blue  STAFFY health", "exact")])
    (no_other_boards / "uk-locations--blue-staffy-puppies-leeds.json").write_text(json.dumps(other))
    f = _anchor_findings(_links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL))
    hits = [m for c, s, m in f if c == LD.SITEWIDE_CHECK]
    assert hits and "uk-locations/blue-staffy-puppies-leeds" in hits[0], f


def test_the_same_anchor_to_a_different_target_is_not_a_reuse(no_other_boards):
    other = _links(_board(slug="uk-locations/blue-staffy-puppies-leeds"),
                   [("/some-other-page/", "Blue Staffy health", "exact")])
    (no_other_boards / "uk-locations--blue-staffy-puppies-leeds.json").write_text(json.dumps(other))
    assert _anchor_findings(_links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL)) == []


def _write(d, board):
    p = d / (board["meta"]["slug"].replace("/", "--") + ".json")
    p.write_text(json.dumps(board), encoding="utf-8")
    return p


def _reuse(board):
    return [(s, m) for c, s, m in _anchor_findings(board) if c == LD.SITEWIDE_CHECK]


LEEDS = "uk-locations/blue-staffy-puppies-leeds"


def test_a_lower_status_sibling_never_fails_the_higher_board(no_other_boards):
    """The first owner keeps its anchor: an approved board is not failed by a draft that
    copied it, while the draft is told (WARN) to pick another."""
    approved = _links(_board(status="approved"), GOOD_INTERNAL, GOOD_EXTERNAL)
    draft = _links(_board(status="draft", slug=LEEDS), GOOD_INTERNAL, GOOD_EXTERNAL)
    _write(no_other_boards, approved)
    _write(no_other_boards, draft)
    assert _reuse(approved) == []
    hits = _reuse(draft)
    assert hits and {s for s, _ in hits} == {"WARN"}, hits
    assert all(SLUG in m for _, m in hits), hits


def test_two_boards_at_the_same_status_are_both_flagged(no_other_boards):
    a = _links(_board(status="boarded"), GOOD_INTERNAL, GOOD_EXTERNAL)
    b = _links(_board(status="boarded", slug=LEEDS), GOOD_INTERNAL, GOOD_EXTERNAL)
    _write(no_other_boards, a)
    _write(no_other_boards, b)
    assert any(LEEDS in m and s == "FAIL" for s, m in _reuse(a))
    assert any(SLUG in m and s == "FAIL" for s, m in _reuse(b))


def test_a_curly_apostrophe_is_the_same_anchor_as_a_straight_one(no_other_boards):
    _write(no_other_boards, _links(_board(slug=LEEDS), [("/uk-blue-staffy-breeders-contact/", "Lisa’s  contact page", "natural")]))
    internal = GOOD_INTERNAL + [("/uk-blue-staffy-breeders-contact/", "lisa's contact page", "partial")]
    hits = _reuse(_links(_board(), internal, GOOD_EXTERNAL))
    assert any("lisa's contact page" in m and LEEDS in m for _, m in hits), hits


def test_a_query_or_fragment_on_the_siblings_href_is_the_same_target(no_other_boards):
    _write(no_other_boards, _links(_board(slug=LEEDS), [("/blue-staffy-health-uk/?utm=x#faq", "Blue Staffy health", "exact")]))
    hits = _reuse(_links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL))
    assert any("/blue-staffy-health-uk/" in m and LEEDS in m for _, m in hits), hits


def test_nav_tiles_are_left_out_of_the_reuse_check(no_other_boards):
    other = _links(_board(slug=LEEDS), [("/uk-blue-staffy-breeders-contact/", "ask Lisa a question", "natural")])
    other["sections"][1]["links"]["internal"].append(
        {"href": "/blue-staffy-health-uk/", "anchor": "Blue Staffy health", "nav": True, "anchor_type": "exact"})
    other["sections"][0]["links"]["internal"][0]["nav"] = True
    _write(no_other_boards, other)
    me = _links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL)
    assert _reuse(me) == []
    # and this board's own nav tile does not collide with a sibling's in-copy anchor
    _write(no_other_boards, _links(_board(slug=LEEDS), [("/tile-0/", "Blue Staffy tile 0", "exact")]))
    me["sections"][1]["links"]["internal"].append(
        {"href": "/tile-0/", "anchor": "Blue Staffy tile 0", "nav": True, "anchor_type": "exact"})
    assert _reuse(me) == []


def test_the_board_map_is_cached_and_refreshed_when_a_board_changes(no_other_boards):
    import os
    p = _write(no_other_boards, _links(_board(slug=LEEDS), [("/blue-staffy-health-uk/", "Blue Staffy health", "exact")]))
    me = _links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL)
    assert _reuse(me)
    assert LD.sitewide_anchor_uses(SLUG) == LD.sitewide_anchor_uses(SLUG)
    st = p.stat()
    _write(no_other_boards, _links(_board(slug=LEEDS), [("/blue-staffy-health-uk/", "health of blue Staffies", "lsi")]))
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
    assert _reuse(me) == []


def test_a_malformed_sibling_record_names_its_file(no_other_boards):
    (no_other_boards / "broken-board.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(PB.BoardError, match="broken-board.json"):
        LD.sitewide_anchor_uses(SLUG)


def test_the_exact_match_message_names_the_links_to_retype():
    internal = GOOD_INTERNAL + [("/a/", "Blue Staffy puppies", "exact"), ("/b/", "Staffy breeder UK", "exact")]
    b = _links(_board(), internal, GOOD_EXTERNAL)
    sid = b["sections"][0]["id"]
    msg = next(m for _, _, m in _anchor_findings(b) if "exact-match" in m)
    for anchor in ("Blue Staffy health", "Blue Staffy puppies", "Staffy breeder UK"):
        assert f"{sid}: {anchor!r}" in msg, msg


@pytest.mark.parametrize("href", ["/x", "/x/", "/x?q=1", "/x/?q", "/x#frag", "/x/#faq", "/a//b",
                                  "//", "/a//b//", " /x ", "/x ?q", "\t/x/\n", "x", "", None])
def test_the_route_rule_is_the_board_builders(href):
    import build_page_board as B
    assert LD._route(href) == B.route_of(href)


@pytest.mark.parametrize("href", ["//evil.example/x", " //host/x", "https://example.com/x"])
def test_an_href_with_a_host_is_not_an_internal_route(href):
    """A protocol-relative `//host/x` passes the schema's `^/` pattern; route_of would fold it
    to `/x/` and silently drop the host, so the reuse check treats it as no internal route."""
    assert LD._route(href) is None


def test_a_board_does_not_collide_with_its_own_record(no_other_boards):
    me = _links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL)
    (no_other_boards / "uk-locations--blue-staffy-puppies-manchester.json").write_text(json.dumps(me))
    assert _anchor_findings(me) == []


def test_the_built_pages_are_not_asked():
    b = _links(_board(slug="blue-staffy-blog-guides", page_type="blog"), [("/x/", "untyped", None)])
    assert _anchor_findings(b) == []


def test_a_repeated_anchor_is_already_refused_by_the_page_gate():
    """Page-level 'no anchor twice' (case, whitespace and punctuation folded) is pageboard's
    links-anchor-duplicate, which runs on every page; Task 5 reuses it rather than adding a
    second check that would report the same fault twice."""
    from test_page_board import ONT_OK, LEDGER_EMPTY
    external = GOOD_EXTERNAL + [("https://www.rspca.org.uk/f", "the Government's  licence guidance", "partial")]
    b = _links(_board(), GOOD_INTERNAL, external)
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
    assert any(x["check"] == "links-anchor-duplicate" and x["sev"] == "FAIL" for x in f)


def test_the_anchor_summary_counts_by_type():
    s = LD.anchor_summary(_links(_board(), GOOD_INTERNAL, GOOD_EXTERNAL))
    assert s["internal"] == {"exact": 1, "partial": 1, "lsi": 1, "natural": 1}
    assert s["external"] == {"natural": 1, "branded": 1, "naked-url": 1}
    assert s["untyped"] == []


# ── the board shows it ──────────────────────────────────────────────────────────────────
ROUTES = {"built": None, "mapped": {"/blue-staffy-health-uk/"}}


def _rendered_links(record):
    import re
    import build_page_board as B
    html = B.render(record, PB.load_ontology(), PB.load_ledger(), {}, {}, "_demo",
                    B.load_previews("_demo"), ROUTES)
    m = re.search(r'<script type="text/markdown" data-title="3\. Outline">(.*?)</script>', html, re.S)
    return m.group(1).split("## Links — every link this page will carry", 1)[1]


def test_a_typed_record_gets_an_anchor_type_column_and_a_diversity_line():
    rec = _links(PB.load_board("_demo"), GOOD_INTERNAL, GOOD_EXTERNAL)
    block = _rendered_links(rec)
    assert "| Target | Anchor | Purpose | Resolves | Source | Anchor type |" in block
    row = next(l for l in block.splitlines() if "/buy-blue-staffy-puppies-uk/" in l)
    assert row.rstrip().endswith("| lsi |")
    line = next(l for l in block.splitlines() if "Link diversity" in l)
    assert "internal anchors: exact 1, partial 1, lsi 1, natural 1" in line
    assert "external anchors: natural 1, branded 1, naked-url 1" in line
    assert "3 link(s) on 3 domain(s)" in line
    assert "WARN (" in line      # _demo is a draft; three external links is short of six


def test_an_untyped_record_renders_exactly_as_before():
    """The twelve built boards carry no anchor_type and are not new-family pages; their
    links block must not gain a column or a line (their committed artifacts stay current)."""
    block = _rendered_links(PB.load_board("_demo"))
    assert "Anchor type" not in block
    assert "Link diversity" not in block
