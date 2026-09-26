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
    # B (blurfill) is not offered on a new page (user ruling 2026-09-26; test_no_blurfill_bleed.py).
    assert [v for v in ("og:A", "og:B", "og:C", "og:D", "og:E", "og:H") if f'value="{v}"' in weeks] == \
        ["og:A", "og:C", "og:D", "og:E", "og:H"]
    assert "⭐ C</label>" in weeks and 'value="ig:' not in weeks
    graphic = block.split('id="img-checks-graphic"', 1)[1].split("</fieldset>", 1)[0]
    assert 'value="ig:IG-5"' in graphic and "⭐ IG-2</label>" in graphic and 'value="og:' not in graphic
    # With no image picks yet, only each existing slot's current file is pre-checked (Task 10c).
    import re
    assert re.findall(r'name="pick-img:([a-z0-9-]+)" value="([^"]+)" checked>', block) == [
        (s, "file:" + f) for s, f in (
            ("opening-photo", "/images/blue-staffy-puppy-for-sale-uk.webp"),
            ("opening-tile-2", "/images/blue-staffy-puppies-uk-litter1.webp"),
            ("opening-tile-3", "/images/blue-staffy-family-dog-uk.webp"),
            ("raise-photo", "/images/1blue-staffy-family-breeder.webp"))]


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


# ── Task 10b review fixes ───────────────────────────────────────────────────────────────
def _slot(block, slot):
    return block.split(f'id="img-{slot}"', 1)[1].split("</fieldset>", 1)[0]


def test_record_text_with_blank_lines_cannot_break_a_slot(repo):
    """Block 7 sits in Markdown: a blank line inside the HTML would end the HTML block and
    turn the rest of the fieldset into text. Record text is collapsed to one line."""
    root, folder = repo
    b = _full()
    before = _slot(IR.board_block(b, IR.board_images(b, root, folder)), "weeks-photo")
    node = next(s for s in b["sections"] if s["id"] == "how-we-raise")["tree"][0]
    img = next(i for i in node["images"] if i["slot"] == "weeks-photo")
    img["prompt"] = "a litter at four weeks\n\n    on a clean vet bed"
    block = IR.board_block(b, IR.board_images(b, root, folder))
    weeks = _slot(block, "weeks-photo")
    assert weeks.count('name="pick-img:weeks-photo"') == before.count('name="pick-img:weeks-photo"')
    assert "\n" not in weeks and "<fieldset" not in weeks
    assert "prompt: a litter at four weeks on a clean vet bed</p>" in weeks
    assert block.count('<fieldset class="imgpick"') == block.count("</fieldset>") == 6


def test_record_text_and_filenames_are_escaped(repo):
    root, folder = repo
    _png(folder / 'Litter-Four-Weeks-<b>"&.jpg', (90, 90, 90))
    b = _full()
    node = next(s for s in b["sections"] if s["id"] == "how-we-raise")["tree"][0]
    img = next(i for i in node["images"] if i["slot"] == "weeks-photo")
    img["prompt"] = 'four weeks <script>"x" & y'
    weeks = _slot(IR.board_block(b, IR.board_images(b, root, folder)), "weeks-photo")
    assert "prompt: four weeks &lt;script&gt;&quot;x&quot; &amp; y</p>" in weeks
    assert 'value="assets:Litter-Four-Weeks-&lt;b&gt;&quot;&amp;.jpg"' in weeks
    assert "<script>" not in weeks and '<b>"&' not in weeks


def test_thumbnails_carry_the_candidate_alt_and_the_preview_names_its_slot(repo):
    root, folder = repo
    b = _full()
    _png(root / "data" / "boards" / "generated" / "uk-locations--blue-staffy-puppies-leeds" / "weeks-photo.png")
    images = IR.board_images(b, root, folder)
    block = IR.board_block(b, images)
    alts = {c["pick"]: c["alt"] for r in images["report"]["slots"] for c in r["candidates"]}
    shown = [(p, a) for p, a in alts.items() if a and images["thumbs"].get(p)]
    assert shown
    for pick, alt in shown:
        assert f'<img src="{images["thumbs"][pick]}" alt="{IR._e(alt)}">' in block
    assert 'alt="Generated draft for weeks-photo"' in _slot(block, "weeks-photo")


def test_thumb_uri_shows_the_labelled_box_for_a_decompression_bomb(tmp_path, monkeypatch):
    from PIL import Image
    ok = tmp_path / "ok.png"
    _png(ok)
    assert IR.thumb_uri(ok).startswith("data:image/webp;base64,")

    def bomb(*a, **k):
        raise Image.DecompressionBombError("too many pixels")

    monkeypatch.setattr(Image, "open", bomb)
    assert IR.thumb_uri(ok) is None


def test_thumb_uri_downsizes_before_it_converts(tmp_path):
    """A large JPEG is decoded at a reduced scale (draft) and shrunk before the RGB copy."""
    from PIL import Image
    big = tmp_path / "big.jpg"
    Image.new("RGB", (4000, 3000), (10, 20, 30)).save(big, quality=60)
    uri = IR.thumb_uri(big)
    import base64
    import io
    with Image.open(io.BytesIO(base64.b64decode(uri.split(",", 1)[1]))) as im:
        assert im.size == (240, 180)
    cmyk = tmp_path / "cmyk.jpg"
    Image.new("CMYK", (600, 400)).save(cmyk)
    assert IR.thumb_uri(cmyk).startswith("data:image/webp;base64,")


def test_style_labels_have_room_to_tap():
    # A 44px tap target on a phone: the height is pinned, not left to the line height.
    assert (".imgstyles label{padding:10px 6px;min-height:44px;box-sizing:border-box;"
            "display:inline-flex;align-items:center}") in IR.BLOCK_CSS


def test_the_schema_refuses_a_slot_id_that_is_not_a_slug():
    import jsonschema
    schema = json.loads((ROOT / "schemas" / "board.schema.json").read_text())
    for where in (schema["properties"]["sections"]["items"]["properties"]["images"]["items"],
                  schema["properties"]["assets"]["items"]):
        pat = where["properties"]["slot"]["pattern"]
        v = jsonschema.Draft202012Validator({"type": "string", "pattern": pat})
        assert v.is_valid("weeks-photo") and v.is_valid("tile-2")
        # (Python's `$` also matches before a final newline; image_rules.SLOT_ID.fullmatch
        # refuses "a\n" at the image gate.)
        for bad in ('x"><script>', "Weeks", "-x", "a b", "", "1blue-staffy", "2-tile"):
            assert not v.is_valid(bad), bad
        # One rule in three places: the schema, the image gate and the ingest step agree.
        assert pat == IR.SLOT_ID.pattern
