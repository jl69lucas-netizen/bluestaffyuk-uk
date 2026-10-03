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


@pytest.fixture(autouse=True)
def _stop_2_recorded(monkeypatch):
    """These tests are about other approval rules; STOP 2 (the outline approval, which
    refuse_on_new_page_rules also checks) is taken as recorded. tests/py/test_outline_stop_review.py
    pins that refusal."""
    import outline_matrix as OM
    monkeypatch.setattr(OM, "approval_refusal", lambda slug, root=None: None)


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
    """The boards built before the new-page rules (working rule 17): the pages these tests
    prove unchanged. A project 5 board (London onward) is a new page and is left out."""
    records = [json.loads(p.read_text()) for p in sorted((ROOT / "data" / "boards").glob("*.json"))]
    return [r for r in records if not FR.is_new_page(r)]


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
    # One constant: the board's 7b and the approval read the same set.
    assert BA.APPROVAL_EXEMPT is FR.APPROVAL_EXEMPT
    # image-pick-invalid is exempt: validate_image_picks refuses a bad img: pick first.
    assert "image-pick-invalid" in BA.APPROVAL_EXEMPT
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


# ── review fixes: 7b says what approval will say; re-approval runs the rules too ─────────
def test_a_draft_board_shows_what_approval_will_refuse():
    b = _board()
    assert b["meta"]["status"] == "draft"
    for sec in b["sections"]:
        for k in FR.KEYWORD_VARIANT_TYPES:
            sec["keywords"][k] = []
    html = BPB.render(b, ONT, LEDGER, live={}, thumbs={}, slug="x")
    # On a draft the rule itself only WARNs; approval runs it as approved, so 7b does too.
    assert '<span class="pill fail">FAIL</span><code>keyword-variants-missing</code>' in html
    assert REFUSAL in html


def test_a_missing_image_pick_is_left_to_the_button(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [_probe("image-pick-missing", "FAIL", "pick one")])
    html = BPB.render(_board(), ONT, LEDGER, live={}, thumbs={}, slug="x")
    assert "image-pick-missing" not in html.split('data-title="7b. Rules for new pages"')[1].split("</script>")[0]
    assert "All new-page rules pass." in html
    assert REFUSAL not in html


def test_backticks_in_a_message_render_as_code_after_escaping(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [_probe("probe-rule", "WARN", "run `python3 x.py <slug>` now")])
    html = BPB.render(_board(), ONT, LEDGER, live={}, thumbs={}, slug="x")
    assert "run <code>python3 x.py &lt;slug&gt;</code> now" in html


def test_7b_wraps_on_a_phone():
    css = BPB.RULES_CSS
    assert ".rules{display:grid;grid-template-columns:minmax(0,1fr)" in css
    assert "overflow-wrap:anywhere" in css


def _reapproval_pair(slug, page_type):
    import test_board_reapprove as TR
    old = TR.approved()
    old["meta"]["slug"], old["meta"]["page_type"] = slug, page_type
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["heading"] = "A Heading The Review Moved"
    return old, new


def test_re_approval_is_refused_while_a_new_page_rule_fails(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [_probe("probe-rule", "FAIL", "probe")])
    old, new = _reapproval_pair("uk-locations/blue-staffy-puppies-manchester", "location")
    with pytest.raises(PB.BoardError, match="probe-rule: probe"):
        BA.apply_reapproval(new, "wording fix", old, "2026-09-24T12:00:00Z", ONT)


def test_a_built_pages_re_approval_is_unchanged(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [_probe("probe-rule", "FAIL", "probe")])
    old, new = _reapproval_pair("x", "hub")
    out = BA.apply_reapproval(new, "wording fix", old, "2026-09-24T12:00:00Z", ONT)
    assert PB.approval_matches(out["board"])


def test_a_sibling_board_without_meta_is_named(tmp_path, monkeypatch):
    import link_diversity as LD
    (tmp_path / "broken.json").write_text('{"sections": []}')
    monkeypatch.setattr(LD, "BOARDS_DIR", tmp_path)
    with pytest.raises(PB.BoardError, match="broken.json"):
        LD._site_map()


# ── follow-up: an H1 variant that would repeat a heading if picked ────────────────────────
def test_an_h1_variant_that_repeats_a_heading_is_warned_about(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [FR.outline_heading_repeat])
    b = _board()
    assert b["h1"]["recommended"] == 0 and b["h1"]["pick"] is None
    b["h1"]["variants"][2] = "How our puppies are raised"          # = section how-we-raise's H2
    html = BPB.render(b, ONT, LEDGER, live={}, thumbs={}, slug="x")
    block = html.split('data-title="7b. Rules for new pages"')[1].split("</script>")[0]
    assert '<span class="pill warn">WARN</span><code>outline-heading-repeat</code>' in block
    assert "H1 variant 3 &#x27;How our puppies are raised&#x27;, if picked" in block
    # Not picked, not recommended: approval as it stands would not refuse.
    assert REFUSAL not in html
    assert block.count("outline-heading-repeat") == 1


def test_a_recommended_h1_that_repeats_a_heading_still_refuses(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [FR.outline_heading_repeat])
    b = _board()
    b["h1"]["variants"][0] = "How our puppies are raised"
    html = BPB.render(b, ONT, LEDGER, live={}, thumbs={}, slug="x")
    assert '<span class="pill fail">FAIL</span><code>outline-heading-repeat</code>' in html
    assert REFUSAL in html
    assert "if picked" not in html


def test_clean_h1_variants_add_no_row(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [FR.outline_heading_repeat])
    html = BPB.render(_board(), ONT, LEDGER, live={}, thumbs={}, slug="x")
    assert "All new-page rules pass." in html


def test_re_approval_takes_the_ontology_it_is_given():
    import inspect
    p = inspect.signature(BA.apply_reapproval).parameters["ont"]
    assert p.default is inspect.Parameter.empty


# ── a BLOCKED entity refuses approval on a new page (Task 28a) ──────────────────────────────
def _with_entity(b, authorization):
    eid = "ont:probe-entity"
    b["sections"][0]["entities"] = list(b["sections"][0]["entities"]) + [eid]
    return b, {"entities": [{"id": eid, "name": "Probe", "aliases": [], "class": "Organism",
                             "authorization": authorization, "source": "test",
                             "owner_page": None}]}


def test_a_blocked_entity_refuses_a_new_pages_approval(monkeypatch):
    # docs/reference/page-run.md row 7 and board block 5 ("The board cannot be approved") say
    # so; until Task 28a only the build gate's `entity-blocked` FAIL did.
    monkeypatch.setattr(FR, "CHECKS", [])
    b, ont = _with_entity(_board(), "BLOCKED")
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, _inbox(b), ont, LEDGER)
    assert "entity-blocked: ont:probe-entity is BLOCKED" in str(e.value)


def test_a_proposed_entity_does_not_refuse_approval(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [])
    b, ont = _with_entity(_board(), "PROPOSED")
    assert BA.apply_approval(b, _inbox(b), ont, LEDGER)["board"]["meta"]["status"] == "approved"


def test_a_blocked_entity_leaves_a_frozen_pages_approval_as_before(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [])
    b, ont = _with_entity(_board(slug="blue-staffy-health-uk", page_type="guide"), "BLOCKED")
    BA.refuse_on_new_page_rules(b, ont)          # no raise: FR.applies leaves it out


# ── board v2 (Task 7): the 7c / 7d picks name a slot, not a section ──────────────────────
def _slots(monkeypatch, ig=("delivery-route", "breed-split"), og=("og-share",)):
    """Give the `_demo` record infographic and original-photo slots, through the modules PB
    reads."""
    import infographic_plan as IP
    import original_slots as OS
    monkeypatch.setattr(FR, "CHECKS", [])
    monkeypatch.setattr(IP, "plan", lambda board, root=None: [{"slot": s} for s in ig])
    monkeypatch.setattr(OS, "propose", lambda board, n=5, root=None: [{"slot": s} for s in og])
    # breed-split is pending on THIS record (IG_PENDING is keyed by board slug and slot).
    monkeypatch.setattr(PB, "IG_PENDING", {(_board()["meta"]["slug"], "breed-split"): "pending"})


def test_infographic_and_og_picks_are_accepted(monkeypatch):
    _slots(monkeypatch)
    b = _board()
    inbox = _inbox(b)
    inbox["picks"].update({"ig:delivery-route": "ruled", "og:og-share": "skip"})
    out = BA.apply_approval(b, inbox, ONT, LEDGER)
    assert out["board"]["approval"]["picks"]["ig:delivery-route"] == "ruled"
    assert out["board"]["approval"]["picks"]["og:og-share"] == "skip"


@pytest.mark.parametrize("sid,val", [("ig:delivery-route", "fancy"), ("og:og-share", "maybe")])
def test_an_off_menu_infographic_or_og_pick_is_refused(monkeypatch, sid, val):
    _slots(monkeypatch)
    b = _board()
    inbox = _inbox(b)
    inbox["picks"].update({"ig:delivery-route": "ruled", sid: val})
    with pytest.raises(PB.BoardError, match=sid):
        BA.apply_approval(b, inbox, ONT, LEDGER)


def test_a_missing_required_infographic_pick_is_refused(monkeypatch):
    # breed-split is pending (PB.IG_PENDING), so only delivery-route is required.
    _slots(monkeypatch)
    b = _board()
    with pytest.raises(PB.BoardError, match="no infographic style pick for: ig:delivery-route$"):
        BA.apply_approval(b, _inbox(b), ONT, LEDGER)


@pytest.mark.parametrize("sid,val", [("ig:no-such-slot", "plate"), ("og:og-nowhere", "use")])
def test_a_pick_for_an_unknown_slot_is_refused(monkeypatch, sid, val):
    _slots(monkeypatch)
    b = _board()
    inbox = _inbox(b)
    inbox["picks"].update({"ig:delivery-route": "ruled", sid: val})
    with pytest.raises(PB.BoardError, match=f"approval picks '{sid}', which is not in the record"):
        BA.apply_approval(b, inbox, ONT, LEDGER)


def test_the_approval_and_the_board_require_the_same_infographic_picks(monkeypatch):
    import build_page_board as BPB
    _slots(monkeypatch)
    b = _board()
    assert PB.ig_slots_required(b) == ["ig:delivery-route"]
    # One source: the board keeps no copy of the list or the pending table of its own.
    assert not hasattr(BPB, "ig_slots_required") and not hasattr(BPB, "IG_PENDING")
    assert BPB.signature_sections(b, LEDGER, "x")[-1:] == ["ig:delivery-route"]


def test_a_pending_slot_on_one_page_never_exempts_another_pages_slot(monkeypatch):
    _slots(monkeypatch)
    monkeypatch.setattr(PB, "IG_PENDING", {("blue-staffy-puppies-london", "breed-split"): "p"})
    b = _board()                                   # the Manchester-slugged record
    assert PB.ig_pending(b, "breed-split") is None
    assert PB.ig_slots_required(b) == ["ig:delivery-route", "ig:breed-split"]


def _bad_infographic_board():
    """A record with an infographic slot whose style is unknown and whose section headings
    match no IG trigger — infographic_plan.plan() raises ValueError on it."""
    b = _board()
    sec = next(s for s in b["sections"] if s["shape"] == "standard")
    sec["heading"] = "Our Kennel Days"
    for n in sec.get("tree") or []:
        n["heading"] = "A Quiet Morning"
    sec.setdefault("images", []).append({"slot": "kennel-graphic", "kind": "infographic",
                                         "infographic_style": "IG-9"})
    return b


def test_an_unknown_infographic_style_is_a_board_error_from_approve(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [])
    b = _bad_infographic_board()
    with pytest.raises(PB.BoardError, match="kennel-graphic"):
        BA.apply_approval(b, _inbox(b), ONT, LEDGER)


def test_an_unknown_infographic_style_is_a_board_error_from_render(monkeypatch):
    monkeypatch.setattr(FR, "CHECKS", [])
    with pytest.raises(PB.BoardError, match="infographic plan for .*kennel-graphic"):
        BPB.render(_bad_infographic_board(), ONT, LEDGER, live={}, thumbs={}, slug="x")


def test_a_re_board_carries_slot_picks_whose_slots_still_exist(monkeypatch):
    _slots(monkeypatch)
    b = _board()
    b["approval_previous"] = {"picks": {"ig:delivery-route": "card",      # kept
                                        "ig:gone-slot": "plate",          # slot gone
                                        "ig:breed-split": "fancy",        # off the menu
                                        "og:og-share": "use",             # kept
                                        "og:og-gone": "skip"}}            # slot gone
    assert PB.locked_picks(b) == {"ig:delivery-route": "card", "og:og-share": "use"}


def test_a_carried_slot_pick_is_pre_checked_on_the_board(monkeypatch):
    import build_page_board as BPB
    import infographic_plan as IP
    london = PB.load_board("blue-staffy-puppies-london")
    slot = IP.plan(london, root=None)[0]["slot"]
    out = BPB.infographic_block(london, {f"ig:{slot}": "ruled"})
    assert f'name="pick-ig:{slot}" value="ruled" checked>' in out
    assert f'name="pick-ig:{slot}" value="plate">' in out
    import original_slots as OS
    first = OS.propose(london, root=PB.ROOT)[0]["slot"]
    og = BPB.og_block(london, {f"og:{first}": "swap"})
    assert f'name="pick-og:{first}" value="swap" checked>' in og
    assert f'name="pick-og:{first}" value="use">' in og
    assert f'name="pick-og:{first}" value="skip">' in og
    assert f'name="note-og:{first}"' in og
    assert "Each slot below has a use / swap / skip choice (`pick-og:<slot>`" in og
    assert "None is required for approval." in og


def test_a_swap_note_names_an_offered_slot(monkeypatch):
    _slots(monkeypatch)
    b = _board()
    inbox = _inbox(b)
    inbox["picks"].update({"ig:delivery-route": "ruled", "og:og-share": "swap"})
    inbox["notes"] = {"og:og-share": "the van photo instead"}
    out = BA.apply_approval(b, inbox, ONT, LEDGER)
    assert out["board"]["approval"]["notes"]["og:og-share"] == "the van photo instead"
    assert out["board"]["approval"]["picks"]["og:og-share"] == "swap"
    inbox["notes"] = {"og:og-nowhere": "x"}
    with pytest.raises(PB.BoardError, match="approval notes 'og:og-nowhere', which is not in the record"):
        BA.apply_approval(b, inbox, ONT, LEDGER)
