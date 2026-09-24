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
    assert "FAIL" in line or "WARN" in line      # three external links is short of six


def test_an_untyped_record_renders_exactly_as_before():
    """The twelve built boards carry no anchor_type and are not new-family pages; their
    links block must not gain a column or a line (their committed artifacts stay current)."""
    block = _rendered_links(PB.load_board("_demo"))
    assert "Anchor type" not in block
    assert "Link diversity" not in block
