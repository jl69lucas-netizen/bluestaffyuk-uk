import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import family_rules as FR  # noqa: E402
import pageboard as PB     # noqa: E402


def _board(slug="uk-locations/blue-staffy-puppies-manchester", page_type="location"):
    b = json.loads((ROOT / "data" / "boards" / "_demo.json").read_text())
    b = copy.deepcopy(b)
    b["meta"]["slug"] = slug
    b["meta"]["page_type"] = page_type
    return b


def test_new_family_pages_are_in_scope_and_built_pages_are_not():
    assert FR.applies(_board())
    assert FR.applies(_board("best-blue-staffy-breeder-vs-backyard", "comparison"))
    assert FR.applies(_board("blue-staffy-first-week-at-home", "blog"))
    # The blog hub is page_type "blog" and was built before this build.
    assert not FR.applies(_board("blue-staffy-blog-guides", "blog"))
    assert not FR.applies(_board("blue-staffy-health-uk", "interior"))
    assert not FR.applies(_board("_demo", "location"))


def test_the_frozen_list_is_exactly_the_pages_built_before_this_build():
    # rebuilt.json only grows, so every frozen slug must still be in it; the new pages
    # project 5 adds to it are never added to the frozen list.
    rebuilt = set(json.loads((ROOT / "data" / "facts" / "rebuilt.json").read_text()))
    assert FR.BUILT_BEFORE_SYSTEM_GAPS <= rebuilt
    assert len(FR.BUILT_BEFORE_SYSTEM_GAPS) == 12


def test_gate_findings_carries_every_registered_check(monkeypatch):
    from test_page_board import ONT_OK, LEDGER_EMPTY
    monkeypatch.setattr(FR, "CHECKS", [])
    FR.register(lambda board, ont: [("family-probe", "FAIL", "probe")])
    f = PB.gate_findings(_board(), ONT_OK, LEDGER_EMPTY, live={}, stage="build")
    assert [x for x in f if x["check"] == "family-probe"] == [
        {"check": "family-probe", "sev": "FAIL", "msg": "probe"}]
    f = PB.gate_findings(_board("blue-staffy-blog-guides", "blog"), ONT_OK, LEDGER_EMPTY, live={}, stage="build")
    assert [x for x in f if x["check"] == "family-probe"] == []
