"""scripts/build_page_board.py — working rule 12: every page board shows every internal and
external link the page will carry, per section and once for the page.

The board is built through the builder's own render(), from the _demo record, so a test that
passes is a statement about the document the breeder is actually sent — not about a helper.
"""
import copy
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_page_board as B   # noqa: E402
import pageboard as PB         # noqa: E402

SLUG = "_demo"

#: dist/ is not consulted; the page map is these two routes and nothing else, so every
#: expectation below is a statement about the record rather than about the last build.
ROUTES = {"built": None, "mapped": {"/uk-blue-staffy-breeders-contact/", "/privacy-policy-uk/"}}


def build(record, routes=ROUTES):
    ont, ledger = PB.load_ontology(), PB.load_ledger()
    previews = B.load_previews(SLUG)
    return B.render(record, ont, ledger, {}, {}, SLUG, previews, routes)


@pytest.fixture()
def record():
    return PB.load_board(SLUG)


def links_block(html):
    """Just the links half of block 3, so an assertion cannot be satisfied by the outline's
    own arrow lines saying something similar above it."""
    m = re.search(r'<script type="text/markdown" data-title="3\. Outline">(.*?)</script>',
                  html, re.S)
    assert m, "the board has no outline block"
    assert "## Links — every link this page will carry" in m.group(1)
    return m.group(1).split("## Links — every link this page will carry", 1)[1]


def linked(section, internal=(), external=()):
    section["links"] = {
        "internal": [{"href": h, "anchor": a, **extra} for h, a, extra in internal],
        "external": [{"href": h, "anchor": a, "library_row": row} for h, a, row in external],
    }
    return section


def test_the_links_block_exists_and_names_every_section(record):
    block = links_block(build(record))
    for s in record["sections"]:
        assert f"{s['n']:02d} · {s['heading']}" in block


def test_a_section_with_no_links_says_so(record):
    # Every _demo section carries an empty links object, so the untouched record is the
    # cleanest statement of the empty case there is.
    assert all(not s["links"]["internal"] and not s["links"]["external"]
               for s in record["sections"])
    block = links_block(build(record))
    assert block.count("No links in this section.") == len(record["sections"])
    assert "Totals: 0 internal · 0 external" in block


def test_a_section_block_carries_target_anchor_purpose_and_resolution(record):
    linked(record["sections"][0],
           internal=[("/privacy-policy-uk/", "our privacy notice", {"sentence_start": True})],
           external=[("https://ico.org.uk/", "the ICO", "ICO — the UK supervisory authority")])
    block = links_block(build(record))
    assert "| Target | Anchor | Purpose | Resolves |" in block
    assert "/privacy-policy-uk/" in block
    assert "our privacy notice" in block
    assert "in copy, sentence start" in block
    assert ">yes<" in block
    assert "ICO — the UK supervisory authority" in block
    assert "external · ico.org.uk" in block


def test_a_nav_link_reads_as_a_nav_link(record):
    linked(record["sections"][0],
           internal=[("/privacy-policy-uk/", "privacy", {"nav": True})])
    assert "nav link" in links_block(build(record))


def test_a_target_the_page_map_does_not_know_resolves_to_no(record):
    linked(record["sections"][0],
           internal=[("/a-page-nobody-planned/", "ghost", {"sentence_start": True})])
    block = links_block(build(record))
    row = next(l for l in block.splitlines() if "/a-page-nobody-planned/" in l)
    assert "no (dead)" in row
    assert ">yes<" not in row


def test_a_planned_but_unbuilt_target_is_distinguished_from_a_dead_one(record):
    routes = {"built": {"/privacy-policy-uk/"},
              "mapped": {"/privacy-policy-uk/", "/uk-blue-staffy-breeders-contact/"}}
    linked(record["sections"][0],
           internal=[("/uk-blue-staffy-breeders-contact/", "contact", {"sentence_start": True}),
                     ("/privacy-policy-uk/", "privacy", {"nav": True}),
                     ("/nowhere/", "nowhere", {"nav": True})])
    block = links_block(build(record, routes))
    lines = {h: next(l for l in block.splitlines() if h in l)
             for h in ("/uk-blue-staffy-breeders-contact/", "/nowhere/")}
    assert "no (not built yet)" in lines["/uk-blue-staffy-breeders-contact/"]
    assert "no (dead)" in lines["/nowhere/"]


def test_a_query_or_fragment_does_not_make_a_known_route_dead(record):
    linked(record["sections"][0],
           internal=[("/privacy-policy-uk/#cookies", "cookies", {"sentence_start": True})])
    row = next(l for l in links_block(build(record)).splitlines() if "#cookies" in l)
    assert "no (" not in row


def test_the_page_table_deduplicates_a_target_and_lists_its_sections(record):
    a, b = record["sections"][0], record["sections"][1]
    linked(a, internal=[("/privacy-policy-uk/", "privacy notice", {"nav": True})])
    linked(b, internal=[("/privacy-policy-uk/", "privacy notice", {"nav": True})])
    block = links_block(build(record))
    page = block.split("### Every link on this page", 1)[1]
    assert page.count("/privacy-policy-uk/") == 1
    row = next(l for l in page.splitlines() if "/privacy-policy-uk/" in l)
    assert f"{a['n']:02d} {a['heading']}" in row
    assert f"{b['n']:02d} {b['heading']}" in row
    assert "1 distinct target(s) across 2 placement(s)" in block


def test_the_totals_count_distinct_targets_by_kind(record):
    a, b = record["sections"][0], record["sections"][1]
    linked(a,
           internal=[("/privacy-policy-uk/", "privacy", {"nav": True}),
                     ("/uk-blue-staffy-breeders-contact/", "contact", {"sentence_start": True})],
           external=[("https://ico.org.uk/", "the ICO", "ICO row")])
    linked(b,
           internal=[("/privacy-policy-uk/", "privacy", {"nav": True})],
           external=[("https://www.gov.uk/x", "GOV.UK", "GOV.UK row")])
    block = links_block(build(record))
    assert "Totals: 2 internal · 2 external" in block
    assert "4 distinct target(s) across 5 placement(s)" in block


def test_the_built_record_still_validates_against_the_schema(record):
    """The block reads the record's own link shape, so a test that invented a field would
    pass while the real boards rendered nothing. Guard the shape the tests above use."""
    linked(record["sections"][0],
           internal=[("/privacy-policy-uk/", "privacy", {"nav": True})],
           external=[("https://ico.org.uk/", "the ICO", "ICO row")])
    schema = json.loads((ROOT / "schemas" / "board.schema.json").read_text(encoding="utf-8"))
    props = schema["properties"]["sections"]["items"]["properties"]["links"]["properties"]
    assert set(props) == {"internal", "external"}
    assert set(props["external"]["items"]["required"]) == {"href", "anchor", "library_row"}
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(copy.deepcopy(record), schema)
