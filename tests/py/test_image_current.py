"""Task 10c (system-gaps build): a slot's CURRENT file is always offered first, and the style
radios on board block 7 carry their names from IMAGE-DESIGNS.md's label map.

Two defects seen on the rendered demo board: `opening-tile-2` records
`source: existing, file: /images/blue-staffy-puppies-uk-litter1.webp` yet its candidate list
offered two unrelated score-1 images and never that file; and the style radios read `A … H`,
`IG-1 … IG-5` with no names."""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests" / "py"))

import image_candidates as IC   # noqa: E402
import image_rules as IR        # noqa: E402
from test_image_candidates import _board, _tree          # noqa: E402
from test_image_board_block import _block, _html, repo   # noqa: E402,F401  (fixture)
from test_image_rules import _full                       # noqa: E402


def _photo(r):
    return next(s for s in r["slots"] if s["slot"] == "delivery-photo")


def _picks(slot):
    return [(c["pool"], c["pick"]) for c in slot["candidates"]]


# ── image_candidates: the current file leads, once ──────────────────────────────────────
def test_a_slot_file_is_the_first_candidate_labelled_current_and_suggested(tmp_path):
    root, assets = _tree(tmp_path)
    b = _board(images_by_section=[{"slot": "delivery-photo", "kind": "photo", "required": True,
                                   "prompt": "our van on a delivery run", "source": "existing",
                                   "file": "/images/family-garden-play.webp"}])
    photo = _photo(IC.candidates(b, root, assets, per_pool=2))
    # The record's own file leads even though it shares no word with the slot …
    assert photo["candidates"][0]["pool"] == "current" and photo["candidates"][0]["current"] is True
    assert photo["candidates"][0]["pick"] == "file:/images/family-garden-play.webp"
    # … the ranked pools follow unchanged, and no other candidate is marked current …
    assert _picks(photo)[1:] == [("own", "file:/images/leeds-delivery-van.webp"),
                                 ("assets", "assets:Leeds-Kennel-Club-Show.jpg")]
    assert [c["current"] for c in photo["candidates"]] == [True, False, False]
    # … and it is the suggestion.
    assert photo["suggested"]["pick"] == "file:/images/family-garden-play.webp"


def test_the_current_file_is_never_listed_twice_even_as_a_size_sibling(tmp_path):
    root, assets = _tree(tmp_path)
    b = _board(images_by_section=[{"slot": "delivery-photo", "kind": "photo", "required": True,
                                   "prompt": "our van on a delivery run", "source": "existing",
                                   "file": "/images/leeds-delivery-van-760.webp"}])
    photo = _photo(IC.candidates(b, root, assets, per_pool=2))
    assert _picks(photo) == [("current", "file:/images/leeds-delivery-van.webp"),
                             ("assets", "assets:Leeds-Kennel-Club-Show.jpg")]
    assert photo["candidates"][0]["matched"] == ["delivering", "delivery", "leed", "van"]


def test_an_assets_row_file_is_current_and_the_slot_file_wins_over_it(tmp_path):
    root, assets = _tree(tmp_path)
    b = _board()
    b["assets"] = [{"slot": "delivery-photo", "kind": "photo", "w": 1408, "h": 768, "required": True,
                    "status": "baked", "file": "/images/kc-registered-staffy-puppies.webp", "alt": "Papers"}]
    photo = _photo(IC.candidates(b, root, assets, per_pool=2))
    assert _picks(photo)[0] == ("current", "file:/images/kc-registered-staffy-puppies.webp")
    assert [p for p in _picks(photo) if p[1] == "file:/images/kc-registered-staffy-puppies.webp"] == \
        [("current", "file:/images/kc-registered-staffy-puppies.webp")]
    assert IC.current_file(b, b["sections"][0]["images"][0]) == "/images/kc-registered-staffy-puppies.webp"
    b["sections"][0]["images"][0]["file"] = "/images/family-garden-play.webp"
    assert IC.current_file(b, b["sections"][0]["images"][0]) == "/images/family-garden-play.webp"
    assert IC.current_file(b, {"slot": "other", "kind": "photo"}) is None


def test_a_current_file_is_suggested_even_when_an_earlier_slot_was_suggested_it(tmp_path):
    root, assets = _tree(tmp_path)
    b = _board(node_images=[{"slot": "delivery-vacc", "kind": "photo", "required": True,
                             "prompt": "a puppy being vaccinated", "source": "existing",
                             "file": "/images/leeds-delivery-van.webp"}])
    r = IC.candidates(b, root, assets, per_pool=2)
    photo, vacc = r["slots"]
    assert photo["suggested"]["pick"] == "file:/images/leeds-delivery-van.webp"
    assert vacc["suggested"]["pick"] == "file:/images/leeds-delivery-van.webp"
    assert vacc["candidates"][0]["current"] is True


def test_a_slot_with_no_file_has_no_current_candidate(tmp_path):
    root, assets = _tree(tmp_path)
    r = IC.candidates(_board(), root, assets, per_pool=2)
    assert not any(c["current"] for s in r["slots"] for c in s["candidates"])


# ── board block 7: current pre-checked, named style radios ──────────────────────────────
def test_the_real_demo_slot_offers_its_own_file_first_and_pre_checks_it(repo):
    root, folder = repo
    b = _full()
    block = _block(_html(b, IR.board_images(b, root, folder)))
    tile = block.split('id="img-opening-tile-2"', 1)[1].split("</fieldset>", 1)[0]
    first = tile.split('<label class="imgopt">', 2)[1]
    assert 'value="file:/images/blue-staffy-puppies-uk-litter1.webp" checked>' in first
    assert "⭐ <b>current</b>" in first
    assert tile.count('value="file:/images/blue-staffy-puppies-uk-litter1.webp"') == 1


def test_an_approval_pick_overrides_the_current_pre_check(repo):
    root, folder = repo
    b = _full()
    b["approval"] = {"picks": {"img:opening-tile-2": "og:B"}}
    block = _block(_html(b, IR.board_images(b, root, folder)))
    tile = block.split('id="img-opening-tile-2"', 1)[1].split("</fieldset>", 1)[0]
    assert 'value="og:B" checked>' in tile
    assert 'value="file:/images/blue-staffy-puppies-uk-litter1.webp">' in tile
    assert tile.count(" checked>") == 1


def test_a_generated_slot_is_never_pre_checked(repo):
    """A generate/infographic slot is answered by the breeder (the approve button refuses
    while it is empty), so even a served copy named in its assets row is offered unchecked."""
    root, folder = repo
    b = _full()
    b["assets"].append({"slot": "weeks-photo", "kind": "photo", "w": 1408, "h": 768, "required": True,
                        "status": "baked", "file": "/images/blue-staffy-family-dog-uk.webp", "alt": "x"})
    block = _block(_html(b, IR.board_images(b, root, folder)))
    weeks = block.split('id="img-weeks-photo"', 1)[1].split("</fieldset>", 1)[0]
    assert "<b>current</b>" in weeks and " checked>" not in weeks


def test_style_radios_carry_the_label_map_names_and_uses(repo):
    root, folder = repo
    (root / "data" / "design").mkdir(parents=True)
    (root / "data" / "design" / "image-styles.json").write_text(
        (ROOT / "data" / "design" / "image-styles.json").read_text(encoding="utf-8"), encoding="utf-8")
    labels = json.loads((ROOT / "data" / "design" / "image-styles.json").read_text(encoding="utf-8"))
    b = _full()
    images = IR.board_images(b, root, folder)
    assert images["styles"] == labels
    block = _block(_html(b, images))
    weeks = block.split('id="img-weeks-photo"', 1)[1].split("</fieldset>", 1)[0]
    b_use = labels["og"]["B"]["use"]
    assert f'title="{b_use}"' in weeks or f'title="{IR._e(b_use)}"' in weeks
    assert "B · %s</label>" % IR._e(labels["og"]["B"]["name"]) in weeks
    assert "⭐ C · %s</label>" % IR._e(labels["og"]["C"]["name"]) in weeks
    graphic = block.split('id="img-checks-graphic"', 1)[1].split("</fieldset>", 1)[0]
    assert "⭐ IG-2 · %s</label>" % IR._e(labels["infographic"]["IG-2"]["name"]) in graphic


def test_style_labels_fall_back_to_the_bare_id(tmp_path, repo):
    root, folder = repo
    assert IR.style_labels(tmp_path / "nowhere") == {}
    bad = tmp_path / "bad"
    (bad / "data" / "design").mkdir(parents=True)
    (bad / "data" / "design" / "image-styles.json").write_text("{not json")
    assert IR.style_labels(bad) == {}
    b = _full()
    images = IR.board_images(b, root, folder)            # the tmp repo has no label map
    assert images["styles"] == {}
    weeks = _block(_html(b, images)).split('id="img-weeks-photo"', 1)[1].split("</fieldset>", 1)[0]
    assert "⭐ C</label>" in weeks
    images.pop("styles")                                   # an images dict built before 10c
    assert "⭐ C</label>" in IR.board_block(b, images)


def test_the_real_label_map_names_every_style_the_rules_know():
    labels = IR.style_labels()
    assert set(labels["og"]) == set(IR.OG_STYLES)
    assert set(labels["infographic"]) == set(IR.IG_STYLES)
    assert all(v["name"] and v["use"] for grp in labels.values() for v in grp.values())


def test_a_real_size_suffixed_name_stays_itself_as_the_current_file(tmp_path):
    """Task 9's review: canonical(src, root) keeps a real -NNN name when no shorter original
    exists. current_file() and candidates() pass root, so the current candidate names the file
    that is really there, not an invented `byrd-card.webp`."""
    root, assets = _tree(tmp_path)
    (root / "public" / "images" / "puppies" / "byrd-card-800.webp").write_bytes(b"x")
    img = {"slot": "delivery-photo", "kind": "photo", "required": True,
           "prompt": "our van on a delivery run", "source": "existing",
           "file": "/images/puppies/byrd-card-800.webp"}
    b = _board(images_by_section=[img])
    assert IC.current_file(b, img, root) == "/images/puppies/byrd-card-800.webp"
    photo = _photo(IC.candidates(b, root, assets, per_pool=2))
    assert _picks(photo)[0] == ("current", "file:/images/puppies/byrd-card-800.webp")
    assert photo["suggested"]["pick"] == "file:/images/puppies/byrd-card-800.webp"
    # A true size sibling still folds to its original when root is given.
    assert IC.current_file(b, dict(img, file="/images/leeds-delivery-van-760.webp"), root) == \
        "/images/leeds-delivery-van.webp"
