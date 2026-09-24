"""Task 12a item 4: one definition of "body". scripts/page_sections.py names the frame shapes,
the frame ids and the FAQ test (shape `faq`, OR a section carrying `questions`), and the
image rule, the outline provenance gate and the board's heading-repeat check all read it."""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests" / "py"))

import family_rules as FR               # noqa: E402
import image_rules as IR                # noqa: E402
import outline_provenance_check as OP   # noqa: E402
import page_sections as PS              # noqa: E402
import query_coverage_check as QCC      # noqa: E402

from test_outline_provenance_check import BOARD, HOMES, SLUG, TRAVEL, page, run, site  # noqa: E402


def _sec(sid, shape, heading, **more):
    return {"id": sid, "shape": shape, "heading": heading,
            "tree": [{"level": 3, "heading": f"{heading} detail", "children": []}], **more}


BOARD_ALL = {"meta": {"slug": "x", "page_type": "location", "status": "boarded"}, "sections": [
    _sec("opening", "hero", "Opening"),
    _sec("top", "standard", "Top"),
    _sec("key-takeaways", "standard", "Key"),
    _sec("newsletter", "standard", "Letters"),
    _sec("glance", "stats", "Glance"),
    _sec("trust", "trust", "Trust"),
    _sec("said", "reviews", "Said"),
    _sec("short", "takeaways", "Short"),
    _sec("questions", "faq", "Questions"),
    _sec("faq", "standard", "Older FAQ", questions=["deposit"]),
    _sec("enquire", "form", "Enquire"),
    _sec("rule", "divider", "Rule"),
    _sec("litter", "puppies", "Litter"),
    _sec("film", "video", "Film"),
    _sec("raise", "standard", "Raise"),
    _sec("deliveries", "table", "Deliveries"),
]}


def _ids(sections):
    return [s["id"] for s in sections]


def test_the_shared_definition():
    assert PS.FRAME_IDS == frozenset(QCC.FRAME_IDS)
    assert PS.is_faq_block({"shape": "faq"}) and PS.is_faq_block({"shape": "standard", "questions": ["q"]})
    assert not PS.is_faq_block({"shape": "standard", "questions": []})
    assert _ids(PS.body_sections(BOARD_ALL)) == ["film", "raise", "deliveries"]


def test_the_image_rule_is_the_shared_body_less_its_own_media_shapes():
    assert PS.OWN_MEDIA_SHAPES == frozenset({"video", "puppies"})
    assert _ids(IR.body_sections(BOARD_ALL)) == [
        s["id"] for s in PS.body_sections(BOARD_ALL) if s["shape"] not in PS.OWN_MEDIA_SHAPES]
    assert _ids(IR.body_sections(BOARD_ALL)) == ["raise", "deliveries"]


def test_the_outline_gate_compares_the_shared_body():
    assert [sid for sid, lvl, key, text in OP.outline(BOARD_ALL) if lvl == 2] == \
        _ids(PS.body_sections(BOARD_ALL))


def test_the_outline_gate_never_compares_a_section_carrying_questions(tmp_path, capsys):
    """A standard section with `questions` is an FAQ block: its question H3s are not outline."""
    board = copy.deepcopy(BOARD)
    board["sections"].append({"id": "faq", "shape": "standard", "heading": "More Questions",
                              "questions": ["deposit"], "tree": []})
    faq = ("<section id='faq' data-section-label='FAQ'><h2>More Questions</h2>"
           "<h3>Can We Visit Before Collection?</h3></section>")
    code, out = run(site(tmp_path, html=page(body=TRAVEL + HOMES + faq), board=board), capsys)
    assert code == 0, out


def test_the_heading_repeat_check_skips_every_faq_blocks_tree():
    board = json.loads((ROOT / "data" / "boards" / "_demo.json").read_text())
    board["meta"].update({"slug": "uk-locations/blue-staffy-puppies-testtown", "page_type": "location"})
    older = {"id": "faq", "shape": "standard", "heading": "More Questions", "questions": ["deposit"],
             "tree": [{"level": 3, "heading": "deposit", "children": []},
                      {"level": 3, "heading": "deposit", "children": []}]}
    board["sections"].append(older)
    assert [f for f in FR.outline_heading_repeat(board, {}) if f[0] == "outline-heading-repeat"] == []
    older.pop("questions")
    assert len(list(FR.outline_heading_repeat(board, {}))) == 1
