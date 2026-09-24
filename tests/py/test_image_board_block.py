"""Board block 7, "Images & styles" (system-gaps build, Task 10b): per slot, candidate
thumbnails and style radios named `pick-img:<slot>`, which the approve script already
writes to `approval.picks["img:<slot>"]`."""
import hashlib
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests" / "py"))

import build_page_board as BPB   # noqa: E402
import image_rules as IR         # noqa: E402
import pageboard as PB           # noqa: E402
from test_image_rules import _full   # noqa: E402

ONT = {"entities": []}
LEDGER = {"pools": {}, "pages": {}}


def _png(path, colour=(40, 80, 120)):
    from PIL import Image
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 40), colour).save(path)


@pytest.fixture
def repo(tmp_path):
    """A tmp repo whose served files are real images (thumbnails are cut from them) and a
    breeder folder with one new photo."""
    root = tmp_path / "repo"
    b = _full()
    stems = {}
    for a in b["assets"]:
        f = a["file"].replace("-760", "")
        _png(root / "public" / f.lstrip("/"))
        stems[pathlib.PurePosixPath(f).stem] = {"w": 64, "h": 40, "sib_w": None}
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "data" / "image-manifest.json").write_text(json.dumps(stems))
    folder = tmp_path / "Assets"
    _png(folder / "Litter-At-Four-Weeks.jpg", (200, 180, 90))
    return root, folder


def _html(board, images):
    return BPB.render(board, ONT, LEDGER, live={}, thumbs={}, slug=board["meta"]["slug"], images=images)


def _block(html):
    return html.split('data-title="7. Images &amp; styles">', 1)[1].split("</script>", 1)[0]


def test_every_slot_gets_a_radio_group_with_thumbnails_and_styles(repo):
    root, folder = repo
    b = _full()
    images = IR.board_images(b, root, folder)
    block = _block(_html(b, images))
    for slot in ("opening-photo", "opening-tile-2", "opening-tile-3", "raise-photo", "weeks-photo", "checks-graphic"):
        assert f'id="img-{slot}"' in block and f'name="pick-img:{slot}"' in block
    # The folder photo is offered to the four-week H3, flagged for ingest, with a thumbnail.
    assert 'value="assets:Litter-At-Four-Weeks.jpg"' in block
    assert "needs ingest → /images/litter-at-four-weeks.webp" in block
    assert block.count('src="data:image/webp;base64,') >= 2
    # OG styles on a photo slot, IG styles on the infographic slot; the record's own style starred.
    weeks = block.split('id="img-weeks-photo"', 1)[1].split("</fieldset>", 1)[0]
    assert [v for v in ("og:A", "og:B", "og:C", "og:D", "og:E", "og:H") if f'value="{v}"' in weeks] == \
        ["og:A", "og:B", "og:C", "og:D", "og:E", "og:H"]
    assert "⭐ C</label>" in weeks and 'value="ig:' not in weeks
    graphic = block.split('id="img-checks-graphic"', 1)[1].split("</fieldset>", 1)[0]
    assert 'value="ig:IG-5"' in graphic and "⭐ IG-2</label>" in graphic and 'value="og:' not in graphic
    # Nothing is pre-checked on a record with no image picks yet.
    assert " checked>" not in block


def test_a_generated_draft_is_previewed_with_its_approval_radio(repo):
    root, folder = repo
    b = _full()
    draft = root / "data" / "boards" / "generated" / "uk-locations--blue-staffy-puppies-leeds" / "weeks-photo.png"
    _png(draft, (10, 10, 10))
    sha = hashlib.sha256(draft.read_bytes()).hexdigest()[:12]
    b["approval"] = {"picks": {"img:weeks-photo": "og:E"}}
    block = _block(_html(b, IR.board_images(b, root, folder)))
    weeks = block.split('id="img-weeks-photo"', 1)[1].split("</fieldset>", 1)[0]
    # The current pick is shown answered, and the preview approves THIS file in that style.
    assert 'value="og:E" checked>' in weeks
    assert f'value="og:E:{sha}">' in weeks and "Approve this generated image" in weeks
    assert "data/boards/generated/uk-locations--blue-staffy-puppies-leeds/weeks-photo.png" in weeks


def test_the_approve_button_refuses_while_a_generated_slot_is_unanswered(repo):
    root, folder = repo
    b = _full()
    html = _html(b, IR.board_images(b, root, folder))
    sig = html.split("var SIGNATURE_SECTIONS=", 1)[1].split(";", 1)[0]
    assert '"img:weeks-photo"' in sig and '"img:checks-graphic"' in sig
    # The approve contract is unchanged: every pick-* radio lands in picks under its name.
    assert "picks[i.name.slice(5)]=i.value" in html


def test_a_page_built_before_this_build_keeps_block_7_as_it_was():
    b = json.loads((ROOT / "data" / "boards" / "blue-staffy-health-uk.json").read_text())
    html = BPB.render(b, PB.load_ontology(), PB.load_ledger(), live={}, thumbs={}, slug=b["meta"]["slug"])
    block = _block(html)
    assert 'class="imgpick"' not in block and 'name="pick-img:' not in html
    assert '<div class="slot"><b>health-litter</b>' in block
    sig = html.split("var SIGNATURE_SECTIONS=", 1)[1].split(";", 1)[0]
    assert "img:" not in sig


def test_board_block_is_empty_without_images_and_says_so_when_nothing_matches(repo):
    root, folder = repo
    b = _full()
    assert IR.board_block(b, None) == ""
    raise_ = next(s for s in b["sections"] if s["id"] == "how-we-raise")
    raise_["tree"][1]["images"][0]["prompt"] = "zzz"
    raise_["tree"][1]["heading"] = "Qqq"
    raise_["heading"] = "Xxx"
    raise_["keywords"] = {}
    block = IR.board_block(b, IR.board_images(b, root, folder))
    graphic = block.split('id="img-checks-graphic"', 1)[1].split("</fieldset>", 1)[0]
    assert "No existing image shares a word with this slot" in graphic


def test_thumb_uri_is_none_for_a_file_that_is_not_an_image(tmp_path):
    bad = tmp_path / "x.webp"
    bad.write_bytes(b"not an image")
    assert IR.thumb_uri(bad) is None
    assert IR.thumb_uri(tmp_path / "missing.webp") is None


def test_a_candidate_whose_path_public_path_refuses_renders_a_card_without_a_thumbnail(repo, monkeypatch):
    """public_path() returns None for a file outside public/images (a `..` segment here). The
    candidate still shows, as a labelled box, and nothing reads the refused path."""
    root, folder = repo
    _png(root / "public" / "outside.png")
    b = _full()
    real = IR.IC.candidates

    def with_refused(board, *a, **k):
        report = real(board, *a, **k)
        row = next(r for r in report["slots"] if r["slot"] == "weeks-photo")
        row["candidates"].insert(0, {"pool": "own", "file": "/images/../outside.png", "asset": None,
                                     "ingest_as": None, "alt": "", "score": 9, "matched": ["weeks"],
                                     "used_on": [], "pick": "file:/images/../outside.png"})
        return report

    monkeypatch.setattr(IR.IC, "candidates", with_refused)
    images = IR.board_images(b, root, folder)
    assert IR.public_path("/images/../outside.png", root) is None
    assert images["thumbs"]["file:/images/../outside.png"] is None
    weeks = IR.board_block(b, images).split('id="img-weeks-photo"', 1)[1].split("</fieldset>", 1)[0]
    assert '<span class="nothumb">/images/../outside.png</span>' in weeks
    assert 'value="file:/images/../outside.png"' in weeks
