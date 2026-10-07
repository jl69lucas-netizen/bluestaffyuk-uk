"""The page board wears the shared presentation layer (plan 2026-10-07-board-readability.md,
Task 4): scripts/board_style.py's role colours and field cards laid over its own collapsible
block cards, and a plain summary first, read from a SIDECAR, `data/boards/summaries/<slug>.json`
— never from the board record, so the record hash the approval signs is the same with or
without one. Every block has a copy button that copies its markdown exactly.
"""
import copy
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import board_style as BS          # noqa: E402
import build_page_board as BPB    # noqa: E402
import pageboard as PB            # noqa: E402
import _board_harness as BH       # noqa: E402

ONT = {"entities": []}
LEDGER = {"pools": {}, "pages": {}}
BRIEF_BULLETS = ["We rebuild one city page and keep its address.",
                 "The breeder picks an H1 and a title pair.",
                 "Every gate runs twice before the page is called done.",
                 "Nothing ships until this board is approved."]
SIDECAR = {"sections": {"1. Brief": {"bullets": BRIEF_BULLETS,
                                     "care": ["The brief is the plan, not the finished page."]}}}


@pytest.fixture(autouse=True)
def _stop_2_recorded(monkeypatch):
    import outline_matrix as OM
    monkeypatch.setattr(OM, "approval_refusal", lambda slug, root=None: None)


def _board(new=True):
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text()))
    if new:                         # a project 5 board: the three-tab decision queue
        b["meta"]["slug"] = "uk-locations/blue-staffy-puppies-manchester"
        b["meta"]["page_type"] = "location"
    return b


def _render(board, summaries=None):
    return BPB.render(board, ONT, LEDGER, live={}, thumbs={}, slug="x", summaries=summaries)


def _md_blocks(page):
    """(title, markdown) for every block, as the page's copy buttons read them."""
    return [(BPB.H.unescape(t), m.strip("\n").rstrip())
            for t, m in re.findall(r'<script type="text/markdown" data-title="([^"]*)"[^>]*>\n(.*?)\n</script>',
                                   page, re.S)]


@pytest.mark.parametrize("new", [True, False])
def test_the_board_embeds_the_shared_style_layer(new):
    page = _render(_board(new))
    assert BS.CSS in page and BS.SCRIPT in page
    assert page.index(BS.SCRIPT) > page.index("window.claude.use(\"db\")")   # laid over the board
    # the block cards and their one-line summaries are still the board's own
    if new:
        assert 'data-summary="' in page and "card.className='card'" in page


def test_a_sidecar_renders_its_bullets_above_the_folded_original(tmp_path):
    board = _board()
    page = _render(board, SIDECAR)
    data = json.loads(re.search(r'<script type="application/json" id="board-summaries">(.*?)</script>',
                                page, re.S).group(1))
    assert data["sections"]["1. Brief"]["bullets"] == BRIEF_BULLETS
    assert 'id="board-summaries"' not in _render(board)          # no sidecar: as before
    path = tmp_path / "board.html"
    path.write_text(page, encoding="utf-8")
    res = BH.run(path)
    assert res["errors"] == [], res["errors"]
    brief = next(b for b in res["blocks"] if b["title"] == "1. Brief")
    assert brief["plain"] == BRIEF_BULLETS and 4 <= len(brief["plain"]) <= 6
    assert brief["plainFirst"] and brief["fullOpen"] is False, brief
    assert "Goal." in brief["fullText"]
    assert brief["care"] == SIDECAR["sections"]["1. Brief"]["care"]
    assert all(b["plain"] is None for b in res["blocks"] if b["title"] != "1. Brief")


@pytest.mark.parametrize("new", [True, False])
def test_each_blocks_copy_button_copies_its_markdown_unchanged(tmp_path, new):
    board = _board(new)
    plain, summed = _render(board), _render(board, SIDECAR if new else None)
    blocks = _md_blocks(summed)
    assert blocks and blocks == _md_blocks(plain)                 # the sidecar never enters it
    assert not any(b in m for _t, m in blocks for b in BRIEF_BULLETS)
    path = tmp_path / "board.html"
    path.write_text(summed, encoding="utf-8")
    res = BH.run(path)
    assert res["errors"] == [], res["errors"]
    # one copy per block; the queue deals the cards into tabs, so compare without order
    assert sorted(res["copied"]) == sorted(f"## {t}\n\n{m}" for t, m in blocks)


def test_the_record_hash_is_the_same_with_and_without_the_sidecar(tmp_path, monkeypatch):
    board = _board()
    before = PB.record_hash(board)
    snapshot = copy.deepcopy(board)
    page = _render(board, SIDECAR)
    assert board == snapshot and PB.record_hash(board) == before
    assert f"record <code>{before[:12]}</code>" in page
    assert f"var RECORD_HASH={json.dumps(before)};" in page
    assert f"record <code>{before[:12]}</code>" in _render(board)
    # the sidecar lives beside the records, under its own directory, and is read from there
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    assert BPB.load_summaries("blue-staffy-puppies-london") is None
    side = tmp_path / "data" / "boards" / "summaries"
    side.mkdir(parents=True)
    (side / "blue-staffy-puppies-london.json").write_text(json.dumps(SIDECAR), encoding="utf-8")
    assert BPB.load_summaries("blue-staffy-puppies-london") == SIDECAR


def test_a_bad_sidecar_is_refused_not_rendered():
    for bad in ({"sections": {"No Such Block": {"bullets": ["x y"]}}},
                {"sections": {"1. Brief": {"bullets": [" ".join(["word"] * 26)]}}},
                {"sections": {"1. Brief": {"bullets": ["Read data/settings.json first."]}}},
                {"sections": {"1. Brief": {"bullets": ["Short line."] * 7}}}):
        with pytest.raises(PB.BoardError, match="summaries"):
            _render(_board(), bad)
