"""No blurfill bleed on a new page's in-body image (user ruling 2026-09-26, answer-board batch
2026-09-26-brief-parity-two-decisions-before-project-5, q01 note: "No grey or black bleed on
phones; bleeds should be based on site system design colours").

Style B (Blur-Fill, `reframe_og.py --style blurfill`) fills the box around the dog with a
blurred copy of the photo, which can read grey or black on a phone. So, for every page not in
scripts/family_rules.py BUILT_BEFORE_SYSTEM_GAPS:

  * scripts/ingest_image.py refuses `--og-style B` (and refuses it outright when it cannot
    know the page: `folder` without `--board`); A (contain, bone gradient) and E (topcover)
    still work, and the twelve built pages keep B for re-ingest;
  * scripts/reframe_og.py defaults to `--style contain` (blurfill stays selectable for
    social OG images, which are not in-body);
  * board block 7 does not offer `og:B` for a new page's slot (the style ids stay stable);
  * IMAGE-DESIGNS.md and the image skills no longer offer B for a new page.
"""
import json
import pathlib
import re
import sys

import pytest
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import family_rules              # noqa: E402
import image_rules as IR         # noqa: E402
import ingest_image              # noqa: E402
import reframe_og                # noqa: E402
from ingest_image import Refused, draft, folder, slug_file   # noqa: E402

NEW = "uk-locations/blue-staffy-leeds"
FROZEN = "blue-staffy-health-uk"
STEM = "blue-staffy-puppy-garden-carlisle"
RULING = "user ruling 2026-09-26"


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "public/images").mkdir(parents=True)
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "data/image-manifest.json").write_text("{}", encoding="utf-8")
    for slug in (NEW, FROZEN):
        board = {"meta": {"slug": slug, "status": "approved"},
                 "assets": [{"slot": "garden-photo", "kind": "photo", "w": 1408, "h": 768,
                             "required": True, "status": "missing", "file": None,
                             "alt": "A blue Staffy puppy in a garden"}],
                 "approval": {"approved_at": "2026-09-24", "picks": {}}}
        (tmp_path / "data/boards" / (slug_file(slug) + ".json")).write_text(
            json.dumps(board, indent=2), encoding="utf-8")
    return tmp_path


@pytest.fixture
def master(tmp_path):
    p = tmp_path / "Assets" / "Roman1.jpg"
    p.parent.mkdir()
    Image.new("RGB", (900, 1200), (91, 124, 153)).save(p)
    return p


def test_the_fixture_slugs_are_one_new_and_one_frozen():
    assert NEW not in family_rules.BUILT_BEFORE_SYSTEM_GAPS
    assert FROZEN in family_rules.BUILT_BEFORE_SYSTEM_GAPS


# ── ingest ───────────────────────────────────────────────────────────────────────────────

def test_draft_refuses_style_b_on_a_new_page_citing_the_ruling(repo, master):
    with pytest.raises(Refused) as e:
        draft(master, NEW, "garden-photo", og_style="B", mobcrop="4:5", root=repo)
    msg = str(e.value)
    assert "style B (blurfill) is retired for in-body images" in msg and RULING in msg
    assert "no grey or black bleed on phones" in msg and "A (contain" in msg and "E (topcover)" in msg
    assert not (repo / "data/boards/generated").exists()


def test_folder_refuses_style_b_on_a_new_page(repo, master):
    with pytest.raises(Refused, match="retired for in-body images"):
        folder(master, STEM, og_style="B", slug=NEW, slot="garden-photo", root=repo)
    assert not (repo / "data/image-ingest.json").exists()


def test_folder_refuses_style_b_when_it_cannot_know_the_page(repo, tmp_path):
    good = tmp_path / "Assets" / "blue-staffy-puppy-garden-carlisle.jpg"
    good.parent.mkdir(exist_ok=True)
    Image.new("RGB", (900, 1200), (91, 124, 153)).save(good)
    with pytest.raises(Refused, match="retired for in-body images"):
        folder(good, og_style="B", root=repo)


@pytest.mark.parametrize("style", ["A", "E"])
def test_a_and_e_still_work_on_a_new_page(repo, master, style):
    r = draft(master, NEW, "garden-photo", og_style=style, root=repo)
    assert r["pick"].startswith("og:%s:" % style)
    folder(master, STEM + "-" + style.lower(), og_style=style, slug=NEW, slot="garden-photo",
           root=repo, dry_run=True)


def test_a_frozen_page_keeps_style_b(repo, master):
    r = draft(master, FROZEN, "garden-photo", og_style="B", mobcrop="4:5", root=repo)
    assert r["pick"].startswith("og:B:")
    folder(master, STEM, og_style="B", mobcrop="4:5", slug=FROZEN, slot="garden-photo",
           root=repo)
    ledger = json.loads((repo / "data/image-ingest.json").read_text())
    assert ledger[STEM]["og_style"] == "B"


def test_the_cli_refuses_b_on_a_new_page_with_exit_2(repo, master, capsys, monkeypatch):
    monkeypatch.setattr(ingest_image, "ROOT", repo)
    code = ingest_image.main(["draft", str(master), "--board", NEW, "--slot", "garden-photo",
                              "--og-style", "B"])
    err = capsys.readouterr().err
    assert code == 2 and "retired for in-body images" in err


# ── reframe_og ───────────────────────────────────────────────────────────────────────────

def test_reframe_og_defaults_to_contain(tmp_path, master, monkeypatch):
    seen = {}
    real = reframe_og.render

    def spy(im, style, *a, **k):
        seen["style"] = style
        return real(im, style, *a, **k)
    monkeypatch.setattr(reframe_og, "render", spy)
    assert reframe_og.main([str(master), str(tmp_path / "out.webp")]) == 0
    assert seen["style"] == "contain"
    assert "blurfill" in reframe_og.STYLES, "blurfill stays selectable for social OG images"


def test_reframe_og_usage_names_contain_as_the_default():
    doc = reframe_og.__doc__
    assert "[--style contain]" in doc and "[--style blurfill]" not in doc
    assert "The default for a single-dog portrait." not in doc


# ── the board's style offer ──────────────────────────────────────────────────────────────

def _slot(slug, current=None):
    board = {"meta": {"slug": slug}}
    sec = {"heading": "How we raise"}
    img = {"slot": "weeks-photo", "kind": "photo", "source": "generate", "og_style": "A",
           "prompt": "a litter"}
    images = {"thumbs": {}, "generated": {}, "styles": {}}
    return IR._slot_html(board, sec, None, img, None, images, current)


def test_a_new_page_is_not_offered_style_b():
    html = _slot(NEW)
    assert 'value="og:B"' not in html
    for st in ("A", "C", "D", "E", "H"):
        assert 'value="og:%s"' % st in html
    assert IR.OG_STYLES == ("A", "B", "C", "D", "E", "H"), "the style ids stay stable"


def test_a_frozen_page_is_still_offered_style_b():
    assert 'value="og:B"' in _slot(FROZEN)


def test_a_stored_b_pick_on_a_new_page_is_still_shown():
    assert 'value="og:B" checked>' in _slot(NEW, current="og:B")


# ── the docs and skills ──────────────────────────────────────────────────────────────────

def test_image_designs_retires_b_for_new_pages():
    text = (ROOT / "IMAGE-DESIGNS.md").read_text(encoding="utf-8")
    assert ("Retired for in-body images on new pages (user ruling 2026-09-26: bleeds use "
            "design colours — bone — never a blurred/grey/black bed). Social OG only.") in text
    assert "the default for any single-dog portrait OG photo" not in text


@pytest.mark.parametrize("skill", ["bsuk-image-generation", "bsuk-photo-ingest",
                                   "image-prompt-generator"])
def test_no_image_skill_offers_b_for_a_new_page(skill):
    text = (ROOT / ".claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert "--og-style B" not in text
    assert "Style `B` (Blur-Fill) with" not in text
    assert "when the slot's style is `B`" not in text


@pytest.mark.parametrize("skill", ["bsuk-site-patterns", "bsuk-puppy-page-builder"])
def test_new_puppy_portraits_are_baked_contain_on_bone(skill):
    """The ruling is general: a NEW puppy portrait is baked 4:5 with the bone-gradient contain
    style; the puppy images already baked are unchanged, and the skill says so."""
    text = (ROOT / ".claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert not re.search(r"4:5 blur-fill (?:portrait|master)", text), skill
    assert "--og-style B" not in text and "--style blurfill" not in text
    assert "--style contain" in text and RULING in text
    assert "already baked" in text and "unchanged" in text


# ── the build gate ───────────────────────────────────────────────────────────────────────

def _record(slug):
    sys.path.insert(0, str(ROOT / "tests" / "py"))
    from test_image_rules import _full
    b = _full()
    b["meta"]["slug"] = slug
    weeks = next(s for s in b["sections"] if s["id"] == "how-we-raise")["tree"][0]["images"][0]
    weeks["og_style"] = "B"
    return b


def test_the_gate_fails_a_new_page_whose_record_names_style_b():
    found = [f for f in IR.slot_findings(_record(NEW)) if f[0] == IR.OG_STYLE_RETIRED]
    assert len(found) == 1 and found[0][1] == "FAIL", found
    assert ("style B (blurfill) is retired for in-body images on new pages — "
            "user ruling 2026-09-26") in found[0][2] and "weeks-photo" in found[0][2]
    assert IR.OG_STYLE_RETIRED in {c for c, _, _ in family_rules.findings(_record(NEW), {})}


def test_the_gate_leaves_a_frozen_page_s_style_b_alone():
    assert not [f for f in IR.slot_findings(_record(FROZEN)) if f[0] == IR.OG_STYLE_RETIRED]
