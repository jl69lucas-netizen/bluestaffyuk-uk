"""An image under every body heading of a project 5 page (system-gaps build, Task 10):
the slot rule, the build gate and the approval of `img:<slot>` picks."""
import copy
import hashlib
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import family_rules as FR   # noqa: E402
import image_rules as IR    # noqa: E402
import pageboard as PB      # noqa: E402

SLUG = "uk-locations/blue-staffy-puppies-leeds"


def _demo(status="boarded"):
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text()))
    b["meta"].update({"slug": SLUG, "page_type": "location", "status": status})
    return b


def _full(status="boarded"):
    """The demo record with every slot sourced and both body H3s carrying a slot."""
    b = _demo(status)
    files = {a["slot"]: a["file"] for a in b["assets"]}
    for s in b["sections"]:
        for img in s["images"]:
            img.update({"source": "existing", "file": files[img["slot"]].replace("-760", "")})
    raise_ = next(s for s in b["sections"] if s["id"] == "how-we-raise")
    raise_["tree"][0]["images"] = [{"slot": "weeks-photo", "kind": "photo", "required": True,
                                    "prompt": "a litter at four weeks on a clean vet bed",
                                    "source": "generate", "og_style": "C"}]
    raise_["tree"][1]["images"] = [{"slot": "checks-graphic", "kind": "infographic", "required": True,
                                    "prompt": "the checks every puppy has before it leaves",
                                    "source": "infographic", "infographic_style": "IG-2"}]
    return b


def _ids(found):
    return sorted({c for c, sev, msg in found})


def _sha(data):
    return hashlib.sha256(data).hexdigest()[:12]


# ── which headings are body ───────────────────────────────────────────────────────────
def test_body_sections_leave_out_the_frame_the_faq_and_own_media_sections():
    b = _demo()
    assert [s["id"] for s in IR.body_sections(b)] == ["how-we-raise"]
    extra = copy.deepcopy(next(s for s in b["sections"] if s["id"] == "how-we-raise"))
    for sid, shape, more in (("faq", "standard", {"questions": ["q1"]}), ("newsletter", "standard", {}),
                             ("film", "video", {}), ("litter", "puppies", {}), ("deliveries", "table", {})):
        e = copy.deepcopy(extra)
        e.update({"id": sid, "shape": shape, **more})
        b["sections"].append(e)
    assert [s["id"] for s in IR.body_sections(b)] == ["how-we-raise", "deliveries"]


def test_body_h3s_are_level_three_nodes_at_any_depth():
    s = {"tree": [{"level": 3, "heading": "A", "children": [
        {"level": 4, "heading": "A1", "children": [{"level": 3, "heading": "B", "children": []}]}]}]}
    assert [n["heading"] for n in IR.body_h3s(s)] == ["A", "B"]


# ── part (a): the slot rule ───────────────────────────────────────────────────────────
def test_a_boarded_location_record_owes_a_slot_under_every_body_heading():
    found = FR.findings(_demo(), {})
    msgs = [m for c, sev, m in found if c == "image-slot-missing"]
    assert msgs == ["section how-we-raise: H3 'The first eight weeks' is a body H3 and plans no image slot",
                    "section how-we-raise: H3 'Health checks' is a body H3 and plans no image slot"]
    # The FAQ block's three H3s are questions and owe nothing.
    assert not any("deposit" in m or "puppy-package" in m for c, sev, m in found)
    # Every existing slot names no source yet.
    assert sorted(m for c, sev, m in found if c == "image-slot-fields") == [
        f"slot {s}: names no source (existing, assets-folder, generate or infographic)"
        for s in ("opening-photo", "opening-tile-2", "opening-tile-3", "raise-photo")]
    assert all(sev == "FAIL" for c, sev, m in found)


def test_a_fully_sourced_record_passes_the_slot_rule():
    assert IR.slot_findings(_full()) == []


def test_a_body_section_with_no_slot_fails_and_a_draft_owes_nothing():
    b = _full()
    next(s for s in b["sections"] if s["id"] == "how-we-raise")["images"] = []
    assert [c for c, sev, m in IR.slot_findings(b)] == ["image-slot-missing"]
    b["meta"]["status"] = "draft"
    assert IR.slot_findings(b) == []


def test_the_rule_never_reaches_a_page_built_before_this_build():
    b = _demo()
    b["meta"].update({"slug": "blue-staffy-blog-guides", "page_type": "blog"})
    assert FR.findings(b, {}) == []
    b["meta"].update({"slug": "blue-staffy-health-uk", "page_type": "interior"})
    assert FR.findings(b, {}) == []


def test_the_hero_needs_a_photo_slot():
    b = _full()
    hero = next(s for s in b["sections"] if s["shape"] == "hero")
    for img in hero["images"]:
        img["kind"] = "infographic"
        img.update({"source": "infographic", "infographic_style": "IG-1"})
    assert _ids(IR.slot_findings(b)) == ["image-hero-photo"]
    b["sections"].remove(hero)
    assert "the record has no hero section" in IR.slot_findings(b)[0][2]


@pytest.mark.parametrize("fields, why", [
    ({"source": "existing"}, "source existing names no file"),
    ({"source": "assets-folder"}, "source assets-folder names no source_file"),
    ({"source": "generate", "og_style": "A", "prompt": " "}, "source generate has no prompt"),
    ({"source": "generate"}, "source generate names no og_style"),
    ({"source": "infographic"}, "source infographic names no infographic_style"),
    ({"source": "infographic", "infographic_style": "IG-3"}, "source infographic on a slot whose kind is not infographic"),
    ({"slot": "Bad_Slot", "source": "existing", "file": "/images/x.webp"}, "slot id is not lowercase letters, digits and hyphens"),
])
def test_each_source_names_what_it_needs(fields, why):
    img = {"slot": "s", "kind": "photo", "required": True, "prompt": "p", **fields}
    assert why in IR.slot_problems(img)


def test_a_slot_id_is_planned_once():
    b = _full()
    raise_ = next(s for s in b["sections"] if s["id"] == "how-we-raise")
    raise_["tree"][1]["images"][0]["slot"] = "weeks-photo"
    assert "image-slot-duplicate" in _ids(IR.slot_findings(b))


def test_an_approved_record_owes_a_pick_for_every_generated_slot():
    b = _full("approved")
    b["approval"] = {"picks": {"img:weeks-photo": "og:C"}}
    assert [m for c, sev, m in IR.slot_findings(b) if c == "image-pick-missing"] == [
        'slot checks-graphic (source infographic): the approval names no image or style for it '
        '(picks["img:checks-graphic"])']


def test_the_schema_takes_the_new_fields_and_the_img_pick_key():
    b = _full()
    b["approval"] = None
    PB.validate_board(b)
    b["sections"][2]["tree"][0]["images"][0]["og_style"] = "F"
    with pytest.raises(PB.BoardError):
        PB.validate_board(b)
    b = _full()
    b["approval"] = {"approved_at": "t", "h1": 0, "picks": {"img:weeks-photo": "og:C", "opening": "H-UT1"},
                     "notes": {}, "canvas_version": None, "record_hash": "0" * 64}
    PB.validate_board(b)
    b["approval"]["picks"] = {"img:Weeks": "og:C"}
    with pytest.raises(PB.BoardError):
        PB.validate_board(b)


def test_every_record_built_before_this_build_keeps_its_approval():
    for p in sorted((ROOT / "data" / "boards").glob("*.json")):
        b = json.loads(p.read_text(encoding="utf-8"))
        PB.validate_board(b)
        if b.get("approval"):
            assert PB.approval_matches(b), p.name


# ── part (c): the build gate ──────────────────────────────────────────────────────────
@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A tmp repo holding the demo's served files, so the build gate reads disk it owns."""
    (tmp_path / "public" / "images").mkdir(parents=True)
    for a in _full()["assets"]:
        (tmp_path / "public" / a["file"].replace("-760", "").lstrip("/")).write_bytes(b"x")
    monkeypatch.setattr(IR, "ROOT", tmp_path)
    return tmp_path


def _approved(picks):
    b = _full("approved")
    b["approval"] = {"picks": picks}
    return b


def test_a_style_with_no_approved_image_fails_the_build(repo):
    b = _approved({"img:weeks-photo": "og:C", "img:checks-graphic": "ig:IG-2"})
    found = IR.build_findings(b)
    assert [(c, m.split(":")[0]) for c, sev, m in found] == [
        ("image-generated-unapproved", "slot weeks-photo"), ("image-generated-unapproved", "slot checks-graphic")]


def test_an_approved_generated_image_passes_only_as_the_bytes_approved(repo):
    draft = repo / "data" / "boards" / "generated" / "uk-locations--blue-staffy-puppies-leeds"
    draft.mkdir(parents=True)
    (draft / "weeks-photo.webp").write_bytes(b"generated-v1")
    b = _approved({"img:weeks-photo": "og:C:" + _sha(b"generated-v1"),
                   "img:checks-graphic": "file:/images/1blue-staffy-family-breeder.webp"})
    # Approved, but only the draft exists: not yet ingested and named in assets[].file.
    assert _ids(IR.build_findings(b)) == ["image-generated-not-ingested"]
    (repo / "public" / "images" / "four-week-litter.webp").write_bytes(b"generated-v1")
    b["assets"].append({"slot": "weeks-photo", "kind": "photo", "w": 1408, "h": 768, "required": True,
                        "status": "baked", "file": "/images/four-week-litter.webp", "alt": "A litter at four weeks"})
    assert IR.build_findings(b) == []
    (repo / "public" / "images" / "four-week-litter.webp").write_bytes(b"generated-v2")
    assert _ids(IR.build_findings(b)) == ["image-generated-unapproved"]


def test_a_folder_file_must_be_ingested_before_the_build(repo):
    b = _approved({"img:weeks-photo": "assets:Leeds Show 2.JPG", "img:checks-graphic": "ig:IG-2:" + "a" * 12})
    b["assets"].append({"slot": "checks-graphic", "kind": "infographic", "w": 1408, "h": 768, "required": True,
                        "status": "baked", "file": "/images/checks.webp", "alt": "Checks"})
    (repo / "public" / "images" / "checks.webp").write_bytes(b"ig")
    b["approval"]["picks"]["img:checks-graphic"] = "ig:IG-2:" + _sha(b"ig")
    assert _ids(IR.build_findings(b)) == ["image-asset-not-ingested"]
    (repo / "public" / "images" / "leeds-show-2.webp").write_bytes(b"x")
    assert IR.build_findings(b) == []


def test_a_missing_existing_file_and_a_malformed_pick_fail(repo):
    b = _approved({"img:weeks-photo": "file:/images/nowhere.webp", "img:checks-graphic": "ig:IG-9"})
    assert _ids(IR.build_findings(b)) == ["image-existing-missing", "image-pick-invalid"]
    b["meta"]["status"] = "boarded"
    assert IR.build_findings(b) == []


def test_the_build_gate_rides_in_gate_findings(repo):
    b = _approved({"img:weeks-photo": "og:C", "img:checks-graphic": "ig:IG-2"})
    checks = [x["check"] for x in PB.gate_findings(b, {"entities": []}, {"pages": {}}, live={}, stage="build")]
    assert "image-generated-unapproved" in checks


# ── the approval of img: picks ────────────────────────────────────────────────────────
def test_validate_image_picks_names_every_bad_pick(repo, tmp_path):
    folder = tmp_path / "Assets"
    folder.mkdir()
    (folder / "Byrd1.jpg").write_bytes(b"x")
    b = _full()
    ok = {"img:weeks-photo": "assets:Byrd1.jpg", "img:checks-graphic": "ig:IG-2",
          "img:raise-photo": "file:/images/1blue-staffy-family-breeder.webp", "opening": "H-UT1"}
    assert IR.validate_image_picks(b, ok, assets_dir=folder) == []
    assert IR.validate_image_picks(b, {"img:weeks-photo": "og:C:" + "0" * 12}) == [
        "slot weeks-photo: approves a generated image, and none exists for this slot"]
    bad = {"img:ghost": "og:A", "img:weeks-photo": "ig:IG-1", "img:checks-graphic": "og:B",
           "img:raise-photo": "file:/images/nowhere.webp", "img:opening-photo": "og:C:" + "0" * 12,
           "img:opening-tile-2": "assets:Missing.jpg", "img:opening-tile-3": "http://x"}
    errs = IR.validate_image_picks(b, bad, assets_dir=folder)
    assert errs == [
        "slot checks-graphic: an OG style is a photo style and this slot is an infographic",
        "approval picks image slot 'ghost', which the record does not plan",
        # opening-photo's assets[] row names a served file, and those bytes are not the approved ones.
        "slot opening-photo: the generated image changed since the board showed it",
        "slot opening-tile-2: 'Missing.jpg' is neither in %s nor ingested" % folder,
        "slot opening-tile-3: pick 'http://x' is not file:, assets:, og: or ig:",
        "slot raise-photo: /images/nowhere.webp is not in public/",
        "slot weeks-photo: an infographic style on a photo slot"]


def test_board_approve_stores_img_picks_and_refuses_a_bad_one(repo):
    import board_approve as BA
    b = _full()
    picks = {"opening": "H-UT1", "at-a-glance": "C-UT1", "how-we-raise": "S1", "owners": "S1",
             "questions": "S1", "img:weeks-photo": "og:C", "img:checks-graphic": "ig:IG-2"}
    inbox = {"approved_at": "2026-09-24T12:00:00Z", "h1": 0, "picks": picks, "notes": {},
             "canvas_version": None, "record_hash": PB.record_hash(b)}
    out = BA.apply_approval(b, inbox, {"entities": []}, {"pools": {}, "pages": {}})
    assert out["board"]["approval"]["picks"]["img:weeks-photo"] == "og:C"
    assert PB.approval_matches(out["board"])
    inbox["picks"] = dict(picks, **{"img:weeks-photo": "og:Z"})
    with pytest.raises(PB.BoardError, match="image picks refused"):
        BA.apply_approval(b, inbox, {"entities": []}, {"pools": {}, "pages": {}})


def test_slots_needing_pick_are_the_generated_ones():
    assert IR.slots_needing_pick(_full()) == ["img:weeks-photo", "img:checks-graphic"]
    assert IR.slots_needing_pick(_demo()) == []
