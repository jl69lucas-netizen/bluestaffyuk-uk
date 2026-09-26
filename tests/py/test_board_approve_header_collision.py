"""`board_approve.py` refuses a header collision on a new page (audit Wave 2 row 11, CAG §12.9).

`header-collision` used to FAIL only at `board_gate.py`, after approval: a new city H2 that
collided with a live sibling was approved, then refused at the build gate, and fixing the
wording moved the record hash and forced a second approval. Across 28 city pages that is 28
chances of a wasted round trip. Approval (and re-approval) of a page `family_rules.applies()`
names now runs the same `pageboard.header_hits()` the gate runs; the twelve built pages
approve exactly as before."""
import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import board_approve as BA   # noqa: E402
import family_rules as FR    # noqa: E402
import pageboard as PB       # noqa: E402

ONT = {"entities": []}
LEDGER = {"pools": {}, "pages": {}}
NEW = "uk-locations/blue-staffy-puppies-manchester"
LIVE_CLEAN = {"/other/": ["Where Do We Deliver Each Week?"]}
LIVE_COLLIDING = {"/other/": ["The First Eight Weeks"]}      # _demo carries "The first eight weeks"


def _board(slug=NEW, page_type="location"):
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text()))
    b["meta"]["slug"] = slug
    b["meta"]["page_type"] = page_type
    return b


def _inbox(b):
    picks = {s["id"]: (s.get("styles") or s["options"]["candidates"])[0]
             for s in b["sections"] if s["shape"] != "standard"}
    return {"approved_at": "2026-09-26T12:00:00Z", "h1": 0, "picks": picks, "notes": {},
            "canvas_version": None, "record_hash": PB.record_hash(b)}


@pytest.fixture(autouse=True)
def no_other_new_page_rules(monkeypatch):
    """Only the collision refusal is under test; the other family rules have their own file."""
    monkeypatch.setattr(FR, "CHECKS", [])


def test_a_new_page_whose_heading_collides_is_refused_at_approval():
    b = _board()
    before = json.dumps(b, sort_keys=True)
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=LIVE_COLLIDING)
    msg = str(e.value)
    assert msg.startswith("this record's headings collide with live pages — reword them and board it again:")
    assert "header-collision: exact: 'The first eight weeks' vs /other/" in msg
    assert json.dumps(b, sort_keys=True) == before                 # still pure


def test_a_new_page_with_no_collision_approves():
    b = _board()
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=LIVE_CLEAN)
    assert out["board"]["meta"]["status"] == "approved"


def test_a_new_page_is_not_approved_against_no_live_pages():
    b = _board()
    with pytest.raises(PB.BoardError, match="examined 0 live pages"):
        BA.apply_approval(b, _inbox(b), ONT, LEDGER, live={})


def test_a_built_page_still_approves_over_a_collision():
    """Frozen: the twelve pages built before the system-gaps build keep the old contract,
    where a collision is the build gate's to report."""
    b = _board(slug="x", page_type="hub")
    assert not FR.applies(b)
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=LIVE_COLLIDING)
    assert out["board"]["meta"]["status"] == "approved"


def test_re_approval_of_a_new_page_is_refused_while_a_heading_collides():
    import test_board_reapprove as TR
    old = TR.approved()
    old["meta"]["slug"], old["meta"]["page_type"] = NEW, "location"
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["heading"] = "Where Do We Deliver Each Week?"
    with pytest.raises(PB.BoardError, match="header-collision: exact"):
        BA.apply_reapproval(new, "wording fix", old, "2026-09-26T12:00:00Z", ONT, live=LIVE_CLEAN)


def test_the_cli_reads_the_live_pages_and_refuses(tmp_path, monkeypatch, capsys):
    """main() is what the operator runs: it must hand apply_approval the real live headings,
    not leave the check to a caller who might not pass them."""
    b = _board()
    stem = PB.slug_file(NEW)
    (tmp_path / "data" / "boards" / "inbox").mkdir(parents=True)
    (tmp_path / "data" / "boards" / "inbox" / (stem + ".json")).write_text(json.dumps(_inbox(b)))
    (tmp_path / "dist").mkdir()
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    # LEDGER and ONTOLOGY are bound at import to the real files: repoint them, so that a
    # main() which (wrongly) approved would write into tmp_path and never into data/.
    monkeypatch.setattr(PB, "LEDGER", tmp_path / "data" / "component-ledger.json")
    monkeypatch.setattr(PB, "ONTOLOGY", tmp_path / "data" / "bsuk-ontology.json")
    monkeypatch.setattr(PB, "load_board", lambda slug: copy.deepcopy(b))
    monkeypatch.setattr(PB, "load_ontology", lambda: ONT)
    monkeypatch.setattr(PB, "load_ledger", lambda: LEDGER)
    monkeypatch.setattr(PB, "live_headings", lambda: LIVE_COLLIDING)
    monkeypatch.setattr(sys, "argv", ["board_approve.py", NEW])
    with pytest.raises(SystemExit) as e:
        BA.main()
    assert e.value.code == 2
    out = capsys.readouterr().out
    assert "board-approve ERROR this record's headings collide with live pages" in out
    for written in ("boards/" + stem + ".json", "component-ledger.json", "bsuk-ontology.json"):
        assert not (tmp_path / "data" / written).exists(), written          # nothing written
