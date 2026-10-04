# tests/py/test_board_subcomponents.py — the two board fields the London board revision
# (answer board 2026-10-03-london-board-revision) added: `subcomponents`, a piece built inside
# a section beside its component, with the style the breeder picked; and `board_revisions`,
# the breeder's decisions after STOP 3, each with its answer-board question. Both are inside
# the record hash, both are validated against the record, and a board without them renders
# exactly as before (blocks 1c and 6b appear only when the field is present).
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests" / "py"))
import pageboard as PB  # noqa: E402
from test_page_board import (FIXTURE_LIBRARY, LEDGER_EMPTY, MIN_BOARD, ONT_OK,  # noqa: E402
                             _approved)

LONDON = "blue-staffy-puppies-london"
SRC = "answer board 2026-10-03-london-board-revision"


@pytest.fixture(autouse=True)
def _fixture_link_library(monkeypatch):
    monkeypatch.setattr(PB, "EXTERNAL_LIBRARY", FIXTURE_LIBRARY)


def _with(piece=None, revision=None):
    b = json.loads(json.dumps(MIN_BOARD))
    p = {"id": "price-note", "section": "puppies", "node": "tree[0].children[0]",
         "heading": "What Does Each Cost?", "name": "Price note", "placement": "under the H4",
         "style": {"pick": "A", "name": "Plain"}, "source": f"{SRC} q01",
         "links": ["/uk-locations/staffy-puppies-for-sale-glasgow/"]}
    r = {"date": "2026-10-03", "source": f"{SRC} q01", "decision": "style A",
         "sections": ["puppies"], "record_change": "subcomponents[price-note]"}
    p.update(piece or {})
    r.update(revision or {})
    b["subcomponents"] = [p]
    b["board_revisions"] = [r]
    return b


def test_a_valid_piece_and_revision_validate_and_move_the_hash():
    b = _with()
    PB.validate_board(b)
    assert PB.record_hash(b) != PB.record_hash(MIN_BOARD)      # approving the board approves them


def test_a_board_without_either_field_keeps_its_hash():
    b = json.loads(json.dumps(MIN_BOARD))
    h = PB.record_hash(b)
    PB.validate_board(b)
    assert "subcomponents" not in b and "board_revisions" not in b and PB.record_hash(b) == h


@pytest.mark.parametrize("piece", [
    {"section": "nope"},                                        # no such section
    {"node": "tree[4]"},                                        # no such node
    {"heading": "Something Else"},                              # node is another heading
    {"links": ["/not-on-the-board/"]},                          # rule 12: link not on the board
    {"links": ["https://www.gov.uk/x"]},                        # in the library, not in the section
])
def test_a_piece_that_does_not_match_the_record_is_refused(piece):
    with pytest.raises(PB.BoardError):
        PB.validate_board(_with(piece=piece))


def test_a_heading_without_a_node_is_refused():
    b = _with()
    del b["subcomponents"][0]["node"]
    with pytest.raises(PB.BoardError):
        PB.validate_board(b)


def test_duplicate_piece_ids_are_refused():
    b = _with()
    b["subcomponents"].append(dict(b["subcomponents"][0]))
    with pytest.raises(PB.BoardError, match="duplicate"):
        PB.validate_board(b)


@pytest.mark.parametrize("over", [{"source": "q01"}, {"source": f"{SRC} 1"}, {"date": "3 Oct"},
                                  {"style": {"pick": "AB", "name": "x"}}, {"extra": 1}])
def test_the_schema_holds_the_source_date_and_style_forms(over):
    b = _with(piece={k: v for k, v in over.items() if k in ("style", "extra")},
              revision={k: v for k, v in over.items() if k in ("source", "date")})
    with pytest.raises(PB.BoardError):
        PB.validate_board(b)


def test_a_revision_naming_an_unknown_section_is_refused():
    with pytest.raises(PB.BoardError, match="board_revisions"):
        PB.validate_board(_with(revision={"sections": ["nope"]}))


def test_blocks_1c_and_6b_show_only_when_the_fields_are_recorded():
    import build_page_board as BPB
    old = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "1c. Decisions since STOP 3" not in old and "6b. Pieces inside sections" not in old
    new = BPB.render(_approved(_with()), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert 'data-title="1c. Decisions since STOP 3"' in new
    assert 'data-title="6b. Pieces inside sections"' in new
    assert "Price note" in new and "A · Plain" in new and f"{SRC} q01" in new
    assert new.index('data-title="6. Component options"') < new.index('data-title="6b. Pieces inside sections"')


def test_1c_and_6b_are_decisions_in_the_queue():
    import build_page_board as BPB
    assert {"1c", "6b"} <= set(BPB.DECIDE_ALWAYS)
    assert BPB.BLOCK_GROUP["1c"] == "Start" and BPB.BLOCK_GROUP["6b"] == "Components"


# ── the London record (answer board 2026-10-03-london-board-revision) ─────────────────────
@pytest.fixture
def london(monkeypatch):
    monkeypatch.setattr(PB, "EXTERNAL_LIBRARY", PB.ROOT / "docs/reference/external-link-library.md")
    return json.loads((ROOT / "data/boards" / f"{LONDON}.json").read_text(encoding="utf-8"))


def test_london_records_the_four_pieces_in_their_picked_styles(london):
    PB.validate_board(london)
    got = {p["id"]: (p["section"], p["style"]["pick"], p["style"]["name"], p["source"])
           for p in london["subcomponents"]}
    assert got == {
        "byline": ("top", "A", "Signed rule", f"{SRC} q01"),
        # restyled as CARD-3, the steel pass (answer board 2026-10-04 q08 (c)); first picked q02
        "puppy-strip": ("key-takeaways", "C", "The steel pass", f"{SRC} q02"),
        "video-call-checklist": ("deposit-viewing", "B", "Look and listen", f"{SRC} q03"),
        "london-places": ("london-life", "C", "Grouped by who sets the rules", f"{SRC} q04"),
    }
    checklist = next(p for p in london["subcomponents"] if p["id"] == "video-call-checklist")
    assert len(checklist["items"]) == 8
    assert checklist["heading"] == "What Should I Ask to See While We Are on the Call?"
    # the tests are named only, never "the parents had them" (q01, 2026-10-02 preview fix)
    assert not any("parents had" in (i["detail"] + i["label"]).lower() for i in checklist["items"])


def test_london_puppy_strip_links_every_listed_puppy(london):
    puppies = json.loads((ROOT / "data/puppies.json").read_text(encoding="utf-8"))
    rows = puppies if isinstance(puppies, list) else puppies.get("puppies", [])
    want = {f"/available-puppies/{p['slug']}/" for p in rows}
    strip = next(p for p in london["subcomponents"] if p["id"] == "puppy-strip")
    assert set(strip["links"]) == want and len(want) == 6


def test_london_carries_every_new_link_and_the_faq_drop(london):
    by_id = {s["id"]: s for s in london["sections"]}
    hrefs = lambda sid, kind: {l["href"] for l in by_id[sid]["links"][kind]}  # noqa: E731
    assert "/blue-staffy-uk-breeders/" in hrefs("top", "internal")
    assert "/privacy-policy-uk/" in hrefs("enquiry", "internal")
    assert len(hrefs("key-takeaways", "internal")) == 6
    assert len(hrefs("london-life", "external")) == 1 + 8      # the PDSA row, plus the eight new
    faq_top = [n["intent"] for n in by_id["faq-top"]["tree"]]
    assert len(faq_top) == 5 and not any("Find Blue Staffy Breeders" in i for i in faq_top)
    assert sum(len(by_id[s]["tree"]) for s in ("faq-top", "faq-middle", "faq-bottom")) == 20
    srcs = {r["source"] for r in london["board_revisions"]}
    assert {f"{SRC} q{n:02d}" for n in range(1, 12)} <= srcs
