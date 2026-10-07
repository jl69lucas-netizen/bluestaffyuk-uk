"""Gap G17 (Manchester page run, 2026-10-07): an infographic slot can be skipped.

Block 7c proposed an infographic for every heading that matched a trigger word, and approval
then demanded a style (sticker, chalk or comic) for each, with no way to say "no infographic
here". The breeder's ruling (q06, 2026-10-02) puts the site's original photos first: an
infographic goes only where no truthful photo fits. So each proposed slot now offers a fourth
answer, `skip`:

  - a skipped slot builds nothing (no bake, no image the build waits for);
  - a skipped slot never fails approval;
  - a skip is recorded in `approval.picks` like any other pick (`ig:<slot>: "skip"`).

A record may also PROPOSE the answer in its own data, `recommended_picks`, keyed like the
approval's picks: `{"ig:<slot>": {"pick": "skip", "why": "..."}}`. The board shows that value
as the Recommended option and pre-checks it, like the H1 and the meta pair; the breeder can
override it at STOP 3.
"""
import copy
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import board_approve as BA  # noqa: E402
import build_page_board as BPB  # noqa: E402
import image_rules as IR  # noqa: E402
import infographic_plan as IP  # noqa: E402
import pageboard as PB  # noqa: E402

LONDON = "blue-staffy-puppies-london"


@pytest.fixture(scope="module")
def london():
    return PB.load_board(LONDON)


def _inbox(board, ig=None):
    """An inbox that answers every required pick, with `ig` overriding block 7c's answers."""
    picks = {**{"img:" + i["slot"]: "ig:" + i["infographic_style"]
                for _, _, i in IR.IC.iter_slots(board) if i.get("source") == "infographic"},
             **{sid: "sticker" for sid in PB.ig_slots_required(board)}}
    picks.update(ig or {})
    return {"record_hash": PB.record_hash(board), "approved_at": "2026-10-07T00:00:00Z",
            "h1": 0, "meta": {"title": 0, "description": 0}, "notes": {},
            "canvas_version": None, "picks": picks}


def _approve(board, inbox):
    return BA.apply_approval(board, inbox, PB.load_ontology(), PB.load_ledger())


# ── the value ─────────────────────────────────────────────────────────────────────────────
def test_skip_is_offered_beside_the_three_styles_which_stay_the_styles():
    assert IP.SKIP == PB.IG_SKIP == "skip"
    assert PB.V2_PICKS["ig:"] == tuple(s["id"] for s in IP.STYLES) == ("sticker", "chalk", "comic")
    assert PB.V2_VALUES["ig:"] == ("sticker", "chalk", "comic", "skip")
    assert IP.PICK_VALUES == PB.V2_VALUES["ig:"]
    assert PB.V2_VALUES["og:"] == PB.V2_PICKS["og:"]          # block 7d already had its skip


def test_declined_reads_only_ig_skips():
    picks = {"ig:a": "skip", "ig:b": "chalk", "og:c": "skip", "img:d": "skip", "e": "skip"}
    assert IP.declined(picks) == {"a"}
    assert IP.declined({}) == set() and IP.declined(None) == set()


# ── approval ──────────────────────────────────────────────────────────────────────────────
def test_a_skip_answers_its_slot_and_is_recorded_in_the_approval(london):
    first = PB.ig_slots_required(london)[0]
    out = _approve(london, _inbox(london, {first: "skip"}))
    assert out["board"]["approval"]["picks"][first] == "skip"


def test_every_slot_skipped_still_approves(london):
    req = PB.ig_slots_required(london)
    assert req, "London plans infographic slots: the check examined nothing"
    out = _approve(london, _inbox(london, {sid: "skip" for sid in req}))
    assert all(out["board"]["approval"]["picks"][sid] == "skip" for sid in req)


def test_a_skipped_record_slot_needs_no_image_pick(london):
    """An infographic slot the record itself plans (an `img:` slot of source infographic): once
    its ig: answer is skip, the approval does not need its img: pick either."""
    plan_slots = {p["slot"] for p in PB.ig_plan(london)}
    rec = [i["slot"] for _, _, i in IR.IC.iter_slots(london)
           if i.get("source") == "infographic" and i["slot"] in plan_slots]
    assert rec, "London has no record infographic slot: the check examined nothing"
    inbox = _inbox(london, {f"ig:{s}": "skip" for s in rec})
    for s in rec:
        inbox["picks"].pop(f"img:{s}", None)
    out = _approve(london, inbox)
    assert all(out["board"]["approval"]["picks"][f"ig:{s}"] == "skip" for s in rec)


def test_a_slot_left_unanswered_is_still_refused(london):
    first = PB.ig_slots_required(london)[0]
    inbox = _inbox(london)
    del inbox["picks"][first]
    with pytest.raises(PB.BoardError, match="no infographic style pick"):
        _approve(london, inbox)


def test_a_value_off_the_menu_is_still_refused(london):
    first = PB.ig_slots_required(london)[0]
    with pytest.raises(PB.BoardError, match="is not one of"):
        _approve(london, _inbox(london, {first: "plate"}))


def test_a_carried_skip_is_kept_on_re_board(london):
    b = copy.deepcopy(london)
    first = PB.ig_slots_required(b)[0]
    b["approval_previous"] = {"picks": {first: "skip"}}
    assert PB.locked_picks(b)[first] == "skip"


# ── a skipped slot builds nothing ───────────────────────────────────────────────────────────
def test_bake_refuses_a_skipped_slot():
    with pytest.raises(ValueError, match="skip"):
        IP.bake_infographic(LONDON, "deposit-steps", IP.SKIP)


def test_image_rules_never_wait_on_a_skipped_slot(london):
    """On an approved record, a skipped infographic slot owes no image pick and no baked
    file: slot_findings and build_findings stay silent about it."""
    b = copy.deepcopy(london)
    plan_slots = {p["slot"] for p in PB.ig_plan(b)}
    rec = [i["slot"] for _, _, i in IR.IC.iter_slots(b)
           if i.get("source") == "infographic" and i["slot"] in plan_slots]
    for s in rec:
        b["approval"]["picks"].pop(f"img:{s}", None)
        b["approval"]["picks"].pop(f"img:{s}-phone", None)
    named = lambda rows: {s for s in rec for r in rows if f"slot {s}" in r[2]}   # noqa: E731
    assert named(IR.slot_findings(b)) == set(rec), "control: an unanswered slot is named"
    for s in rec:
        b["approval"]["picks"][f"ig:{s}"] = IP.SKIP
    assert named(IR.slot_findings(b)) == set()
    assert named(IR.build_findings(b)) == set()


# ── the record's own proposal ───────────────────────────────────────────────────────────────
def _with_rec(board, rec):
    b = copy.deepcopy(board)
    b["recommended_picks"] = rec
    return b


def test_the_plan_carries_the_records_recommendation(london):
    slot = IP.plan(london, root=None)[0]["slot"]
    b = _with_rec(london, {f"ig:{slot}": {"pick": "skip", "why": "a photo already fills it"}})
    PB.validate_board(b)
    rows = {p["slot"]: p for p in IP.plan(b, root=None)}
    assert rows[slot]["recommended"] == "skip"
    assert rows[slot]["recommended_why"] == "a photo already fills it"
    assert all(p["recommended"] is None for s, p in rows.items() if s != slot)


def test_a_recommendation_for_a_slot_the_plan_does_not_offer_is_a_record_fault(london):
    b = _with_rec(london, {"ig:no-such-slot": {"pick": "skip", "why": "x"}})
    with pytest.raises(PB.BoardError, match="no-such-slot"):
        PB.ig_plan(b)


@pytest.mark.parametrize("bad", [
    {"ig:deposit-steps": {"pick": "plate", "why": "x"}},          # off the menu
    {"ig:deposit-steps": {"pick": "skip"}},                        # no reason
    {"ig:deposit-steps": {"pick": "skip", "why": ""}},             # empty reason
    {"deposit-steps": {"pick": "skip", "why": "x"}},               # not keyed like a pick
])
def test_the_schema_holds_the_recommendation_to_its_shape(london, bad):
    with pytest.raises(PB.BoardError):
        PB.validate_board(_with_rec(london, bad))


def test_a_recommendation_is_inside_the_record_hash(london):
    slot = IP.plan(london, root=None)[0]["slot"]
    b = _with_rec(london, {f"ig:{slot}": {"pick": "skip", "why": "x"}})
    assert PB.record_hash(b) != PB.record_hash(london)


def test_a_record_without_recommendations_keeps_its_hash(london):
    assert "recommended_picks" not in london
    assert PB.approval_matches(london), "London's approval must still verify"


# ── the board ───────────────────────────────────────────────────────────────────────────────
def test_block_7c_offers_skip_on_every_slot(london):
    plan = PB.ig_plan(london)
    out = BPB.infographic_block(london, {}, plan)
    for p in plan:
        assert f'name="pick-ig:{p["slot"]}" value="skip">' in out, p["slot"]


def test_block_7c_pre_checks_and_labels_the_recommended_skip(london):
    plan0 = IP.plan(london, root=None)
    slot, other = plan0[0]["slot"], plan0[1]["slot"]
    b = _with_rec(london, {f"ig:{slot}": {"pick": "skip", "why": "a photo fills it"}})
    plan = PB.ig_plan(b)
    out = BPB.infographic_block(b, {}, plan)
    assert f'name="pick-ig:{slot}" value="skip" checked>' in out
    fs = out[out.index(f'id="ig-{slot}"'):]
    fs = fs[:fs.index("</fieldset>")]
    assert "(Recommended)" in fs
    assert "a photo fills it" in out
    assert f'name="pick-ig:{other}" value="skip">' in out          # not pre-checked elsewhere
    # A pick carried from an earlier approval wins over the record's proposal.
    out = BPB.infographic_block(b, {f"ig:{slot}": "chalk"}, plan)
    assert f'name="pick-ig:{slot}" value="chalk" checked>' in out
    assert f'name="pick-ig:{slot}" value="skip" checked>' not in out


def test_the_approve_script_drops_a_skipped_slots_image_pick(london):
    """The approve button waits for `img:<slot>` on a record infographic slot. Once the
    breeder picks skip for `ig:<slot>`, that image pick (and its phone layout) is no longer
    open. Project 5 boards only: a pre-rule board's script stays byte for byte."""
    js = BPB.SKIP_JS
    assert "pick-ig:" in js and "'skip'" in js and "'img:'" in js and "-phone" in js
    html = BPB.render(london, PB.load_ontology(), {"pools": {"inventory": ["avail-b"]}, "pages": {}}, live={}, thumbs={}, slug=LONDON,
                      images=IR.board_images(london))
    assert js in html
    m = re.search(r"function missingPicks\(\)\{.*?\n  \}", html, re.S)
    assert m and "!skippedImg(id)&&" in m.group(0)
    home = PB.load_board("index")
    html = BPB.render(home, PB.load_ontology(), {"pools": {"inventory": ["avail-b"]}, "pages": {}}, live={}, thumbs={}, slug="index")
    assert "skippedImg" not in html


def test_the_schema_menu_is_the_approval_menu():
    schema = json.loads((ROOT / "schemas/board.schema.json").read_text(encoding="utf-8"))
    enum = schema["properties"]["recommended_picks"]["additionalProperties"]["properties"]["pick"]["enum"]
    assert tuple(enum) == PB.V2_VALUES["ig:"]
