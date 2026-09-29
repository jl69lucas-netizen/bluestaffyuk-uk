"""STOP 2: the outline is approved on its own, before the page board (the user's ruling, 2026-09-29).

"yes, separate approval, i must see all angles, framework, keywords, why each competitors rank,
full distribution section by section". The approval lives in the outline record,
`data/outlines/<slug>.json` (`approval`, stamped by `scripts/outline_matrix.py --approve` with
the record's hash), mirroring the research board's `data/research-boards/<slug>.json`. For every
new page (scripts/family_rules.py `is_new_page`) the page board is refused without it:
`scripts/build_page_board.py` exits 2 before it reads the board, and `scripts/board_gate.py`
FAILs `outline-unapproved`. The twelve pages built before project 5 are untouched.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

sys.path.insert(0, str(ROOT / "tests/py"))
import _stop_kit as K  # noqa: E402
import board_gate as BG  # noqa: E402
import build_page_board as BPB  # noqa: E402
import outline_matrix as OM  # noqa: E402
import pageboard as PB  # noqa: E402

NEW = "blue-staffy-puppies-for-sale-leeds"       # a project 5 city: is_new_page is True
BUILT = "blue-staffy-health-uk"                  # one of the twelve built before project 5
RULE_ID = "outline-approved-before-page-board"
THIS_TEST = "tests/py/test_outline_approval.py"
GOOD = ROOT / "tests/py/fixtures/outline_matrix/good.json"


def _outline(tmp_path, slug, approved=True, edit_after=False):
    """The page's STOP 1 and STOP 2 records under tmp_path (tests/py/_stop_kit.py), the outline
    approved or not, and optionally edited after its approval."""
    paths = K.lay_out(tmp_path, slug, outline_approved=approved)
    if edit_after:
        rec = json.loads(paths["outline"].read_text())
        rec["sections"][2]["words"] += 10
        paths["outline"].write_text(json.dumps(rec))
    return paths


def test_the_slugs_are_what_the_test_says():
    assert PB.FR.is_new_page(NEW) and not PB.FR.is_new_page(BUILT)


@pytest.mark.parametrize("state, want", [
    ("missing", "no outline record"),
    ("unapproved", "is not approved"),
    ("stale", "changed after its approval"),
])
def test_approval_refusal_names_why(tmp_path, state, want):
    if state != "missing":
        _outline(tmp_path, NEW, approved=(state != "unapproved"), edit_after=(state == "stale"))
    assert want in (OM.approval_refusal(NEW, tmp_path) or "")


def test_an_approved_outline_clears_the_gate(tmp_path):
    _outline(tmp_path, NEW)
    assert OM.approval_refusal(NEW, tmp_path) is None


def _run_builder(monkeypatch, tmp_path, slug):
    monkeypatch.setattr(OM, "ROOT", tmp_path)
    monkeypatch.setattr(BPB, "OUT", tmp_path / "out")
    monkeypatch.setattr(sys, "argv", ["build_page_board.py", slug])

    def no_board(s):
        raise SystemExit("reached load_board")
    monkeypatch.setattr(PB, "load_board", no_board)
    with pytest.raises(SystemExit) as e:
        BPB.main()
    return e.value.code


def test_build_page_board_refuses_a_new_page_without_an_approved_outline(tmp_path, monkeypatch, capsys):
    code = _run_builder(monkeypatch, tmp_path, NEW)
    assert code == 2
    out = capsys.readouterr().out
    assert "outline-unapproved" in out and "STOP 2" in out
    assert not (tmp_path / "out").exists()


def test_build_page_board_goes_on_once_the_outline_is_approved(tmp_path, monkeypatch):
    _outline(tmp_path, NEW)
    assert _run_builder(monkeypatch, tmp_path, NEW) == "reached load_board"


def test_build_page_board_leaves_the_twelve_built_pages_alone(tmp_path, monkeypatch):
    assert _run_builder(monkeypatch, tmp_path, BUILT) == "reached load_board"


def _judge(monkeypatch, tmp_path, slug):
    monkeypatch.setattr(OM, "ROOT", tmp_path)
    board = {"meta": {"slug": slug}, "sections": [], "assets": []}
    monkeypatch.setattr(PB, "load_board", lambda s: board)
    monkeypatch.setattr(PB, "gate_findings", lambda *a, **k: [])
    monkeypatch.setattr(PB, "rule16_findings", lambda *a, **k: [])
    monkeypatch.setattr(PB, "rule16_judged", lambda *a, **k: ["x"])
    monkeypatch.setattr(PB, "all_headings", lambda b: [])
    return BG.judge(slug, "build", {}, {"pages": {}}, {}, {})


def test_board_gate_fails_a_new_page_whose_outline_is_not_approved(tmp_path, monkeypatch):
    n, lines = _judge(monkeypatch, tmp_path, NEW)
    assert n == 1 and any("outline-unapproved" in l for l in lines), lines
    _outline(tmp_path, NEW)
    n, lines = _judge(monkeypatch, tmp_path, NEW)
    assert n == 0, lines
    n, lines = _judge(monkeypatch, tmp_path, BUILT)
    assert n == 0, lines


def _norm(text):
    return " ".join(text.split())


def test_the_rule_is_written_in_the_gates_pack():
    text = (ROOT / "rules/gates.md").read_text(encoding="utf-8")
    m = re.search(rf"---\nid: {RULE_ID}\n(.*?)---\n\n(.*?)(?=\n---\n|\Z)", text, re.S)
    assert m, f"rules/gates.md has no {RULE_ID} block"
    head, body = m.group(1), _norm(m.group(2))
    assert "enforced: test" in head and f"test: {THIS_TEST}" in head, head
    for tok in ("2026-09-29", "yes, separate approval", "STOP 2", "data/outlines/<slug>.json",
                "outline-unapproved", "scripts/build_page_board.py"):
        assert tok in body, tok


def test_the_rule_is_indexed_as_tested_by_this_file():
    index = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))
    rows = [r for r in index["rules"] if r["id"] == RULE_ID]
    assert len(rows) == 1, rows
    assert rows[0]["enforced"] == "test" and rows[0]["test"] == THIS_TEST, rows[0]
    assert rows[0]["pack"] == "rules/gates.md", rows[0]
