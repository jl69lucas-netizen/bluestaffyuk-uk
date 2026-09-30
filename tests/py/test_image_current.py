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

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests" / "py"))

import image_candidates as IC   # noqa: E402
import image_rules as IR        # noqa: E402
from test_image_candidates import _board, _tree          # noqa: E402
from test_image_board_block import _block, _html, _png, repo   # noqa: E402,F401  (fixture)
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
    a_use = labels["og"]["A"]["use"]
    assert f'title="{IR._e(a_use)}"' in weeks
    assert "A · %s</label>" % IR._e(labels["og"]["A"]["name"]) in weeks
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


# ── Task 10c review fixes ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("bad", [{"og": ["A"]}, {"og": {"C": "Contain"}}, ["A"], {"og": {"C": {"name": 3}}}])
def test_a_wrong_shape_label_map_falls_back_to_bare_ids(tmp_path, repo, bad):
    root, folder = repo
    where = tmp_path / "shaped"
    (where / "data" / "design").mkdir(parents=True)
    (where / "data" / "design" / "image-styles.json").write_text(json.dumps(bad))
    assert IR.style_labels(where) == {}
    b = _full()
    images = IR.board_images(b, root, folder)
    images["styles"] = bad                            # a map handed in unchecked renders too
    weeks = _block(_html(b, images)).split('id="img-weeks-photo"', 1)[1].split("</fieldset>", 1)[0]
    assert "⭐ C</label>" in weeks and "title=" not in weeks


def test_a_well_shaped_group_survives_beside_a_bad_one(tmp_path):
    (tmp_path / "data" / "design").mkdir(parents=True)
    (tmp_path / "data" / "design" / "image-styles.json").write_text(json.dumps(
        {"og": {"B": {"name": "Blur-Fill", "use": "x"}, "C": "Contain"}, "infographic": ["IG-1"]}))
    assert IR.style_labels(tmp_path) == {"og": {"B": {"name": "Blur-Fill", "use": "x"}}}


def test_a_current_file_that_is_not_on_disk_is_labelled_missing_and_not_ticked(tmp_path):
    root, assets = _tree(tmp_path)
    b = _board(images_by_section=[{"slot": "delivery-photo", "kind": "photo", "required": True,
                                   "prompt": "our van on a delivery run", "source": "existing",
                                   "file": "/images/gone-from-disk.webp"}])
    photo = _photo(IC.candidates(b, root, assets, per_pool=2))
    first = photo["candidates"][0]
    assert (first["pool"], first["current"], first["missing"]) == ("current", True, True)
    assert all(c["missing"] is False for c in photo["candidates"][1:])
    b2 = _board(images_by_section=[{"slot": "delivery-photo", "kind": "photo", "required": True,
                                    "prompt": "x", "source": "existing",
                                    "file": "/images/family-garden-play.webp"}])
    assert _photo(IC.candidates(b2, root, assets, per_pool=2))["candidates"][0]["missing"] is False


def test_the_board_does_not_tick_a_missing_current_file(repo):
    root, folder = repo
    b = _full()
    (root / "public" / "images" / "blue-staffy-puppies-uk-litter1.webp").unlink()
    block = _block(_html(b, IR.board_images(b, root, folder)))
    tile = block.split('id="img-opening-tile-2"', 1)[1].split("</fieldset>", 1)[0]
    first = tile.split('<label class="imgopt">', 2)[1]
    assert 'value="file:/images/blue-staffy-puppies-uk-litter1.webp">' in first
    assert "<b>current · missing</b>" in first and " checked>" not in tile


def test_a_missing_current_file_never_carries_the_suggestion(tmp_path):
    """The ⭐ falls to the best-ranked real candidate not already suggested for another slot."""
    root, assets = _tree(tmp_path)
    b = _board(images_by_section=[{"slot": "delivery-photo", "kind": "photo", "required": True,
                                   "prompt": "our van on a delivery run", "source": "existing",
                                   "file": "/images/gone-from-disk.webp"}])
    photo = _photo(IC.candidates(b, root, assets, per_pool=2))
    assert photo["candidates"][0]["missing"] is True
    assert photo["suggested"]["pick"] == "file:/images/leeds-delivery-van.webp"
    # A later slot whose current file is missing skips what an earlier slot was suggested.
    b = _board(node_images=[{"slot": "delivery-vacc", "kind": "photo", "required": True,
                             "prompt": "our van on a delivery run", "source": "existing",
                             "file": "/images/gone-from-disk.webp"}])
    photo, vacc = IC.candidates(b, root, assets, per_pool=2)["slots"]
    assert photo["suggested"]["pick"] == "file:/images/leeds-delivery-van.webp"
    assert vacc["candidates"][0]["missing"] is True
    ranked = [c["pick"] for c in vacc["candidates"][1:]]
    assert "file:/images/leeds-delivery-van.webp" in ranked
    assert vacc["suggested"]["pick"] == next(p for p in ranked if p != "file:/images/leeds-delivery-van.webp")


def test_the_board_stars_a_real_candidate_when_the_current_file_is_missing(repo):
    root, folder = repo
    b = _full()
    (root / "public" / "images" / "blue-staffy-puppies-uk-litter1.webp").unlink()
    tile = _block(_html(b, IR.board_images(b, root, folder))).split(
        'id="img-opening-tile-2"', 1)[1].split("</fieldset>", 1)[0]
    assert "<b>current · missing</b>" in tile and "⭐" not in tile     # nothing real to suggest
    _png(folder / "Indoors-With-Us-Day-One.jpg", (90, 120, 150))     # a real candidate arrives
    tile = _block(_html(b, IR.board_images(b, root, folder))).split(
        'id="img-opening-tile-2"', 1)[1].split("</fieldset>", 1)[0]
    first, rest = tile.split('<label class="imgopt">', 2)[1:]
    assert "⭐" not in first and "<b>current · missing</b>" in first
    assert "⭐ <b>assets</b>" in rest and "Indoors-With-Us-Day-One.jpg" in rest


# ── Task 12a item 6: an assets-folder slot is offered its own source_file ────────────────
def _folder_slot(source_file):
    return _board(images_by_section=[{"slot": "delivery-photo", "kind": "photo", "required": True,
                                      "prompt": "our van on a delivery run", "source": "assets-folder",
                                      "source_file": source_file}])


def test_an_assets_folder_slot_offers_its_own_source_file_first_as_current(tmp_path):
    root, assets = _tree(tmp_path)
    # Byrd1.jpg is left out of the folder pool (its stem is served), and scores nothing here.
    photo = _photo(IC.candidates(_folder_slot("Byrd1.jpg"), root, assets, per_pool=2))
    first = photo["candidates"][0]
    assert (first["pool"], first["pick"], first["current"], first["missing"]) == \
        ("current", "assets:Byrd1.jpg", True, False)
    assert first["asset"] == "Byrd1.jpg" and first["ingest_as"] == "/images/byrd1.webp"
    assert photo["suggested"]["pick"] == "assets:Byrd1.jpg"
    assert [c["pick"] for c in photo["candidates"]].count("assets:Byrd1.jpg") == 1


def test_a_source_file_already_in_the_pool_is_listed_once(tmp_path):
    root, assets = _tree(tmp_path)
    photo = _photo(IC.candidates(_folder_slot("Leeds-Kennel-Club-Show.jpg"), root, assets, per_pool=2))
    picks = [c["pick"] for c in photo["candidates"]]
    assert picks[0] == "assets:Leeds-Kennel-Club-Show.jpg" and picks.count(picks[0]) == 1


def test_a_source_file_not_in_the_folder_is_offered_missing_and_not_suggested(tmp_path):
    root, assets = _tree(tmp_path)
    photo = _photo(IC.candidates(_folder_slot("Gone.jpg"), root, assets, per_pool=2))
    assert (photo["candidates"][0]["pick"], photo["candidates"][0]["missing"]) == ("assets:Gone.jpg", True)
    assert photo["suggested"]["pick"] != "assets:Gone.jpg"


def test_an_ingested_folder_slot_keeps_its_served_copy_current_and_offers_the_folder_file(tmp_path):
    root, assets = _tree(tmp_path)
    b = _folder_slot("Byrd1.jpg")
    b["assets"] = [{"slot": "delivery-photo", "kind": "photo", "w": 1408, "h": 768, "required": True,
                    "status": "baked", "file": "/images/family-garden-play.webp", "alt": "x"}]
    photo = _photo(IC.candidates(b, root, assets, per_pool=2))
    assert [(c["pick"], c["current"]) for c in photo["candidates"][:2]] == [
        ("file:/images/family-garden-play.webp", True), ("assets:Byrd1.jpg", False)]


def test_block_7_ticks_the_folder_file_labelled_current_with_its_ingest_note(repo):
    root, folder = repo
    b = _full()
    img = next(s for s in b["sections"] if s["id"] == "how-we-raise")["tree"][0]["images"][0]
    img.update({"source": "assets-folder", "source_file": "Litter-At-Four-Weeks.jpg"})
    img.pop("og_style")
    block = _block(_html(b, IR.board_images(b, root, folder)))
    weeks = block.split('id="img-weeks-photo"', 1)[1].split("</fieldset>", 1)[0]
    first = weeks.split('<label class="imgopt">', 2)[1]
    assert 'value="assets:Litter-At-Four-Weeks.jpg" checked>' in first
    assert "<b>current</b> · the file this slot names now" in first
    assert "needs ingest → /images/litter-at-four-weeks.webp" in first
    assert weeks.count('value="assets:Litter-At-Four-Weeks.jpg"') == 1
