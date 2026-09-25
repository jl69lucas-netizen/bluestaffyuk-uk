"""Task 12a item 1: every image slot has its `assets[]` row planned at boarding, so the
ingest and publish steps only ever fill a row's `file` and `status` (outside the hash) and
never have to add one (which would un-approve the page)."""
import copy
import json
import pathlib
import shutil
import sys

import pytest
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import family_rules as FR    # noqa: E402
import image_rules as IR     # noqa: E402
import ingest_image as II    # noqa: E402
import pageboard as PB       # noqa: E402

SLUG = "uk-locations/blue-staffy-puppies-leeds"
ROW_MISSING = "image-asset-row-missing"


def _row(slot, kind, alt):
    return {"slot": slot, "kind": kind, "w": 1408, "h": 768, "required": True,
            "status": "missing", "file": None, "alt": alt}


def _record(status="boarded", rows=True):
    """The demo record as a new location page, every slot sourced: the hero and the body H2
    reuse served files, the two body H3s are generated (an OG photo and an infographic)."""
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text()))
    b["meta"].update({"slug": SLUG, "page_type": "location", "status": status})
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
    if rows:
        b["assets"] += [_row("weeks-photo", "photo", "A blue Staffy litter at four weeks"),
                        _row("checks-graphic", "infographic", "The checks every puppy has")]
    return b


def _ids(found):
    return sorted({c for c, sev, m in found})


# ── the rule ─────────────────────────────────────────────────────────────────────────────
def test_a_slot_with_no_assets_row_fails_from_boarded_on():
    b = _record(rows=False)
    found = [f for f in IR.slot_findings(b) if f[0] == ROW_MISSING]
    assert [(sev, m) for c, sev, m in found] == [
        ("FAIL", "slot weeks-photo (section how-we-raise, H3 'The first eight weeks'): no assets[] row "
                 "plans it — add {slot, kind, w, h, required} at boarding; ingest and publish only "
                 "fill its file and status"),
        ("FAIL", "slot checks-graphic (section how-we-raise, H3 'Health checks'): no assets[] row "
                 "plans it — add {slot, kind, w, h, required} at boarding; ingest and publish only "
                 "fill its file and status")]
    b["meta"]["status"] = "draft"
    assert IR.slot_findings(b) == []


def test_the_hero_and_h2_slots_need_a_row_too():
    b = _record()
    b["assets"] = [a for a in b["assets"] if a["slot"] not in ("opening-tile-3", "raise-photo")]
    assert [m.split(" ")[1] for c, sev, m in IR.slot_findings(b) if c == ROW_MISSING] == \
        ["opening-tile-3", "raise-photo"]


def test_a_record_with_every_row_passes_and_the_id_is_not_approval_exempt():
    assert IR.slot_findings(_record()) == []
    assert ROW_MISSING not in FR.APPROVAL_EXEMPT
    assert ROW_MISSING not in IR.BUILD_CHECK_IDS


def test_it_binds_new_family_pages_only():
    b = _record(rows=False)
    assert ROW_MISSING in _ids(FR.findings(b, {}))
    b["meta"].update({"slug": "blue-staffy-blog-guides", "page_type": "blog"})
    assert FR.findings(b, {}) == []


def test_the_board_gate_shows_it():
    b = _record(rows=False)
    found = PB.gate_findings(b, {"entities": []}, {"pages": {}}, live={}, stage="build")
    assert ROW_MISSING in {x["check"] for x in found}


# ── the flow: board → draft → approve the bytes → publish ────────────────────────────────
@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / "public" / "images").mkdir(parents=True)
    (tmp_path / "data" / "boards").mkdir(parents=True)
    (tmp_path / "data" / "image-manifest.json").write_text("{}", encoding="utf-8")
    for a in _record()["assets"]:
        if a["file"]:
            f = a["file"].replace("-760", "")
            shutil.copy(ROOT / "public" / f.lstrip("/"), tmp_path / "public" / f.lstrip("/"))
    monkeypatch.setattr(IR, "ROOT", tmp_path)
    return tmp_path


def _save(repo, b):
    (repo / "data" / "boards" / (II.slug_file(SLUG) + ".json")).write_text(
        json.dumps(b, indent=2), encoding="utf-8")


def _load(repo):
    return json.loads((repo / "data" / "boards" / (II.slug_file(SLUG) + ".json")).read_text())


def _master(tmp_path, name, size, colour):
    p = tmp_path / "masters" / name
    p.parent.mkdir(exist_ok=True)
    Image.new("RGB", size, colour).save(p)
    return p


def _image_findings(b):
    return [f for f in FR.findings(b, {}) if f[0].startswith("image-")]


def test_a_boarded_record_with_its_rows_drafts_approves_and_publishes_clean(repo, tmp_path):
    b = _record()
    _save(repo, b)
    assert _image_findings(b) == []
    weeks = II.draft(_master(tmp_path, "weeks.png", (1600, 900), (91, 124, 153)), SLUG, "weeks-photo",
                     og_style="C", root=repo)
    checks = II.draft(_master(tmp_path, "checks.png", (1600, 900), (201, 162, 39)), SLUG,
                      "checks-graphic", infographic="IG-2", root=repo)
    # The second pass of the board: the breeder approves the exact bytes, by sha12.
    picks = {"img:weeks-photo": weeks["pick"], "img:checks-graphic": checks["pick"]}
    assert IR.validate_image_picks(b, picks, root=repo) == []
    b = _load(repo)
    b["meta"]["status"] = "approved"
    b["approval"] = {"approved_at": "2026-09-24T12:00:00Z", "picks": picks}
    _save(repo, b)
    # Approved, not yet published: only the approval-exempt build ids remain.
    assert {c for c, sev, m in _image_findings(b)} <= FR.APPROVAL_EXEMPT
    hash_before = PB.record_hash(b)
    II.publish(SLUG, "weeks-photo", "blue-staffy-litter-four-weeks-leeds", root=repo)
    II.publish(SLUG, "checks-graphic", "blue-staffy-puppy-health-checks-leeds", root=repo)
    b = _load(repo)
    assert PB.record_hash(b) == hash_before, "publishing fills file and status, outside the hash"
    assert _image_findings(b) == []


def test_without_the_row_publish_is_refused_and_the_board_says_why_first(repo, tmp_path):
    b = _record(rows=False)
    _save(repo, b)
    assert ROW_MISSING in _ids(_image_findings(b))
    weeks = II.draft(_master(tmp_path, "weeks.png", (1600, 900), (91, 124, 153)), SLUG, "weeks-photo",
                     og_style="C", root=repo)
    b["approval"] = {"picks": {"img:weeks-photo": weeks["pick"]}}
    _save(repo, b)
    with pytest.raises(II.Refused, match="plans no assets"):
        II.publish(SLUG, "weeks-photo", "blue-staffy-litter-four-weeks-leeds", root=repo)
