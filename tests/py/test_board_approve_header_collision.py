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


# --- Task 13 review follow-ups -------------------------------------------------------------

CITY_A = "uk-locations/blue-staffy-puppies-leeds"
SHARED_H2 = "Where Do We Deliver Each Week?"


def _approved_board(slug, heading):
    b = _board(slug=slug)
    b["sections"][0]["heading"] = heading
    b["approval"] = _inbox(b)
    b["meta"]["status"] = "approved"
    return b


def test_an_approved_but_unbuilt_board_counts_as_a_sibling():
    """Batch safety: city A is approved but not built yet, so dist/ does not carry its H2.
    Approving city B with the same H2 is refused, naming A — otherwise both pass approval
    and only the build gate finds the pair."""
    a = _approved_board(CITY_A, SHARED_H2)
    b = _board()
    b["sections"][0]["heading"] = SHARED_H2
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, _inbox(b), ONT, LEDGER, live={"/other/": ["Something Else Entirely"]},
                          boards={CITY_A: a, NEW: copy.deepcopy(b)})
    assert "header-collision: exact: 'Where Do We Deliver Each Week?'" in str(e.value)
    assert CITY_A in str(e.value)


def test_a_previously_approved_board_counts_too():
    a = _approved_board(CITY_A, SHARED_H2)
    a["approval_previous"], a["approval"] = a.pop("approval"), None
    b = _board()
    b["sections"][0]["heading"] = SHARED_H2
    with pytest.raises(PB.BoardError, match="blue-staffy-puppies-leeds"):
        BA.apply_approval(b, _inbox(b), ONT, LEDGER, live={"/other/": ["Something Else Entirely"]},
                          boards={CITY_A: a})


def test_a_draft_board_and_the_page_itself_are_not_siblings():
    draft = _board(slug=CITY_A)
    draft["sections"][0]["heading"] = SHARED_H2          # never approved: not a claim yet
    b = _board()
    b["sections"][0]["heading"] = SHARED_H2
    itself = _approved_board(NEW, SHARED_H2)             # its own earlier approval
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER, live={"/other/": ["Something Else Entirely"]},
                            boards={CITY_A: draft, NEW: itself})
    assert out["board"]["meta"]["status"] == "approved"


def test_a_built_board_is_judged_by_its_live_headings_not_twice():
    a = _approved_board(CITY_A, SHARED_H2)
    b = _board()
    b["sections"][0]["heading"] = SHARED_H2
    live = {"/other/": ["Something Else Entirely"], PB.own_live_key(a): ["A Reworded Heading"]}
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=live, boards={CITY_A: a})
    assert out["board"]["meta"]["status"] == "approved"


def test_the_collision_message_says_to_rebuild_if_a_listed_page_changed():
    b = _board()
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=LIVE_COLLIDING)
    assert "(if a listed page changed since the last build, run npm run build and retry)" in str(e.value)


def test_only_the_sentinel_skips_the_check():
    b = _board()
    with pytest.raises(PB.BoardError, match="examined 0 live pages"):
        BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=None)
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=BA.SKIP_LIVE)
    assert out["board"]["meta"]["status"] == "approved"
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER)                   # the default is the sentinel
    assert out["board"]["meta"]["status"] == "approved"


def _cli_tmp(tmp_path, monkeypatch, make_dist=True):
    (tmp_path / "data" / "boards" / "inbox").mkdir(parents=True)
    if make_dist:
        (tmp_path / "dist").mkdir()
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(PB, "LEDGER", tmp_path / "data" / "component-ledger.json")
    monkeypatch.setattr(PB, "ONTOLOGY", tmp_path / "data" / "bsuk-ontology.json")
    monkeypatch.setattr(PB, "load_ontology", lambda: ONT)
    monkeypatch.setattr(PB, "load_ledger", lambda: LEDGER)


def test_main_with_no_dist_refuses_examined_zero(tmp_path, monkeypatch, capsys):
    b = _board()
    _cli_tmp(tmp_path, monkeypatch, make_dist=False)
    stem = PB.slug_file(NEW)
    (tmp_path / "data" / "boards" / "inbox" / (stem + ".json")).write_text(json.dumps(_inbox(b)))
    monkeypatch.setattr(PB, "load_board", lambda slug: copy.deepcopy(b))
    monkeypatch.setattr(sys, "argv", ["board_approve.py", NEW])
    with pytest.raises(SystemExit) as e:
        BA.main()
    assert e.value.code == 2
    assert "examined 0 live pages" in capsys.readouterr().out
    assert not (tmp_path / "data" / "boards" / (stem + ".json")).exists()


def test_the_reapprove_cli_reads_the_live_pages_and_refuses(tmp_path, monkeypatch, capsys):
    import test_board_reapprove as TR
    old = TR.approved()
    old["meta"]["slug"], old["meta"]["page_type"] = NEW, "location"
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["heading"] = "The First Eight Weeks"             # collides with LIVE_COLLIDING
    _cli_tmp(tmp_path, monkeypatch)
    monkeypatch.setattr(PB, "load_board", lambda slug: copy.deepcopy(new))
    monkeypatch.setattr(BA, "baseline_board", lambda slug, ref="HEAD": copy.deepcopy(old))
    monkeypatch.setattr(PB, "live_headings", lambda dist=None: LIVE_COLLIDING)
    monkeypatch.setattr(sys, "argv", ["board_approve.py", NEW, "--reapprove", "--reason", "wording fix"])
    with pytest.raises(SystemExit) as e:
        BA.main()
    assert e.value.code == 2
    assert "header-collision: exact" in capsys.readouterr().out
    assert not (tmp_path / "data" / "boards" / (PB.slug_file(NEW) + ".json")).exists()


def test_live_headings_reads_dist_at_call_time(tmp_path, monkeypatch):
    page = tmp_path / "dist" / "somewhere" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text("<html><body><h2>Hello There</h2></body></html>")
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    assert "/somewhere/" in PB.live_headings()
