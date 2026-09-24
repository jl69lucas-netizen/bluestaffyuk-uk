"""The rules for new pages are answered on the board and before approval (system-gaps Task 10d).

Every `family_rules` check used to run only in `pageboard.gate_findings`, i.e. at the build gate,
after approval. A board could be approved that the build then refused, and fixing it changed the
record hash and forced a second approval. Now block 7b of the board lists the findings, and
`board_approve.apply_approval` refuses while any FAIL stands that is not a build-gate check."""
import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import board_approve as BA        # noqa: E402
import build_page_board as BPB    # noqa: E402
import family_rules as FR         # noqa: E402
import image_rules as IR          # noqa: E402
import pageboard as PB            # noqa: E402

ONT = {"entities": []}
LEDGER = {"pools": {}, "pages": {}}
REFUSAL = "Approval will be refused until the FAIL rows in 7b are fixed."


def _board(slug="uk-locations/blue-staffy-puppies-manchester", page_type="location"):
    """The `_demo` record re-slugged as a new-family page (the test_family_rules.py pattern)."""
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text()))
    b["meta"]["slug"] = slug
    b["meta"]["page_type"] = page_type
    return b


def _inbox(b):
    picks = {s["id"]: (s.get("styles") or s["options"]["candidates"])[0]
             for s in b["sections"] if s["shape"] != "standard"}
    return {"approved_at": "2026-09-24T12:00:00Z", "h1": 0, "picks": picks, "notes": {},
            "canvas_version": None, "record_hash": PB.record_hash(b)}


def _probe(*finding):
    def probe(board, ont):
        yield finding
    return probe


def _real_records():
    return [json.loads(p.read_text()) for p in sorted((ROOT / "data" / "boards").glob("*.json"))]


# ── approval ──────────────────────────────────────────────────────────────────────────────
def test_approval_is_refused_while_a_new_page_rule_fails(monkeypatch):
    b = _board()
    before = json.dumps(b, sort_keys=True)
    monkeypatch.setattr(FR, "CHECKS", [_probe("probe-rule", "FAIL", "probe")])
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, _inbox(b), ONT, LEDGER)
    msg = str(e.value)
    assert msg.startswith("this record breaks the rules for new pages — fix the record and board it again:")
    assert "\n  - probe-rule: probe" in msg
    assert json.dumps(b, sort_keys=True) == before          # still pure


def test_the_probe_sees_the_post_approval_status(monkeypatch):
    seen = []

    def probe(board, ont):
        seen.append(board["meta"]["status"])
        return []
    monkeypatch.setattr(FR, "CHECKS", [probe])
    b = _board()
    BA.apply_approval(b, _inbox(b), ONT, LEDGER)
    assert seen == ["approved"]


def test_a_warn_never_blocks_approval(monkeypatch):
    b = _board()
    monkeypatch.setattr(FR, "CHECKS", [_probe("probe-rule", "WARN", "probe")])
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER)
    assert out["board"]["meta"]["status"] == "approved"


def test_build_gate_checks_do_not_block_approval(monkeypatch):
    b = _board()
    monkeypatch.setattr(FR, "CHECKS", [_probe("image-generated-unapproved", "FAIL", "x")])
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER)
    assert out["board"]["meta"]["status"] == "approved"


def test_every_build_gate_id_is_exempt(tmp_path):
    assert set(IR.BUILD_CHECK_IDS) <= BA.APPROVAL_EXEMPT
    # The outline and approval facts are never exempt.
    for cid in ("image-slot-missing", "image-slot-fields", "image-hero-photo", "image-pick-missing"):
        assert cid not in BA.APPROVAL_EXEMPT
    # On the Task 10 fixture (an approved record whose generated slots have no approved
    # image), every id build_findings yields is a build-gate id.
    b = _board()
    b["meta"]["status"] = "approved"
    raise_ = next(s for s in b["sections"] if s["id"] == "how-we-raise")
    raise_["tree"][0]["images"] = [{"slot": "weeks-photo", "kind": "photo", "required": True,
                                    "prompt": "a litter at four weeks", "source": "generate", "og_style": "C"}]
    b["approval"] = {"picks": {"img:weeks-photo": "og:C"}}
    found = IR.build_findings(b, root=tmp_path)
    assert found
    assert {c for c, sev, m in found} <= IR.BUILD_CHECK_IDS


def test_built_pages_approve_exactly_as_before(monkeypatch):
    calls = []
    monkeypatch.setattr(FR, "CHECKS", [lambda board, ont: calls.append(1) or [("probe-rule", "FAIL", "p")]])
    records = _real_records()
    assert len(records) == 13          # the 12 built pages and _demo
    for r in records:
        assert not FR.applies(r), r["meta"]["slug"]
        assert FR.findings(r, ONT) == []
    assert calls == []


# ── the board ─────────────────────────────────────────────────────────────────────────────
def test_the_board_lists_the_rules_for_a_new_page(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [_probe("probe-rule", "FAIL", "probe"),
                                       _probe("probe-warn", "WARN", "<img src=x onerror=1>"),
                                       _probe("image-generated-unapproved", "FAIL", "later")])
    html = BPB.render(_board(), ONT, LEDGER, live={}, thumbs={}, slug="x")
    assert "7b. Rules for new pages" in html
    assert html.index("7b. Rules for new pages") < html.index('data-title="8. Approve"')
    assert "probe-rule" in html and "probe-warn" in html
    assert '<span class="pill fail">FAIL</span>' in html
    assert '<span class="pill warn">WARN</span>' in html
    assert "checked at build, after the image is approved" in html
    assert REFUSAL in html
    assert "<img src=x onerror=1>" not in html
    assert "&lt;img src=x onerror=1&gt;" in html


def test_an_exempt_fail_alone_does_not_announce_a_refusal(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [_probe("image-generated-unapproved", "FAIL", "later")])
    html = BPB.render(_board(), ONT, LEDGER, live={}, thumbs={}, slug="x")
    assert "checked at build, after the image is approved" in html
    assert REFUSAL not in html


def test_a_clean_new_page_says_every_rule_passes(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [])
    html = BPB.render(_board(), ONT, LEDGER, live={}, thumbs={}, slug="x")
    assert "7b. Rules for new pages" in html
    assert "All new-page rules pass." in html
    assert REFUSAL not in html


def test_built_boards_render_unchanged(monkeypatch):
    ont, ledger = PB.load_ontology(), PB.load_ledger()
    routes = BPB.load_routes()
    for r in _real_records():
        slug = r["meta"]["slug"]
        monkeypatch.setattr(FR, "CHECKS", [])
        plain = BPB.render(r, ont, ledger, live={}, thumbs={}, slug=slug, routes=routes)
        monkeypatch.setattr(FR, "CHECKS", [_probe("probe-rule", "FAIL", "probe")])
        probed = BPB.render(r, ont, ledger, live={}, thumbs={}, slug=slug, routes=routes)
        assert plain == probed, slug
        assert "7b. Rules for new pages" not in probed
