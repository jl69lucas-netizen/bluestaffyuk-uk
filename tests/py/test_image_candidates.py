"""image_candidates.py — every image slot is offered the site's own images first
(system-gaps build, Task 9). All tests run on a tmp tree: a repo with public/images, the
manifest, a verbatim file and two built pages, and a breeder folder outside it."""
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import image_candidates as IC  # noqa: E402

SLUG = "uk-locations/blue-staffy-puppies-leeds"


def _page(imgs, main=True):
    tags = "".join(f'<img src="{s}" alt="{a}">' for s, a in imgs)
    body = f"<main>{tags}</main>" if main else tags
    return f'<!doctype html><header><img src="/images/blue-staffy-uk-official-logo0.png" alt="logo"></header>{body}'


def _tree(tmp_path):
    root = tmp_path / "repo"
    imgs = root / "public" / "images"
    imgs.mkdir(parents=True)
    for name in ("leeds-delivery-van.webp", "leeds-delivery-van-760.webp", "puppy-vaccinations-uk.webp",
                 "kc-registered-staffy-puppies.webp", "family-garden-play.webp",
                 "blue-staffy-uk-official-logo0.png"):
        (imgs / name).write_bytes(b"x")
    (imgs / "puppies").mkdir()
    (imgs / "puppies" / "byrd-byrd1.webp").write_bytes(b"x")
    (root / "data" / "verbatim").mkdir(parents=True)
    (root / "data" / "image-manifest.json").write_text(json.dumps({
        "leeds-delivery-van": {"w": 1, "h": 1, "sib_w": 760},
        "puppy-vaccinations-uk": {"w": 1, "h": 1, "sib_w": None},
        "kc-registered-staffy-puppies": {"w": 1, "h": 1, "sib_w": None},
        "family-garden-play": {"w": 1, "h": 1, "sib_w": None},
        "blue-staffy-uk-official-logo0": {"w": 1, "h": 1, "sib_w": None}}))
    (root / "data" / "verbatim" / "blue-staffy-health-uk.json").write_text(json.dumps({
        "alts": [{"src": "/images/puppy-vaccinations-uk.webp",
                  "alt": "A puppy at the vet after its vaccinations"}]}))
    dist = root / "dist"
    (dist / "uk-locations" / "blue-staffy-puppies-leeds").mkdir(parents=True)
    (dist / "uk-locations" / "blue-staffy-puppies-leeds" / "index.html").write_text(
        _page([("/images/leeds-delivery-van-760.webp", "Our van delivering a puppy to Leeds")]))
    (dist / "blue-staffy-health-uk").mkdir()
    (dist / "blue-staffy-health-uk" / "index.html").write_text(
        _page([("/images/puppy-vaccinations-uk.webp", "Vaccinations"),
               ("/images/kc-registered-staffy-puppies.webp", "Kennel Club papers")]))
    (dist / "board-preview" / "x").mkdir(parents=True)
    (dist / "board-preview" / "x" / "index.html").write_text(
        _page([("/images/family-garden-play.webp", "specimen")]))
    assets = tmp_path / "Assets" / "Images"
    assets.mkdir(parents=True)
    for name in ("Leeds-Kennel-Club-Show.jpg", "Byrd1.jpg", "family-garden-play.png", ".DS_Store",
                 "archive.zip", "File name- vaccination-card-close-up .jpg .jpg"):
        (assets / name).write_bytes(b"x")
    return root, assets


def _board(images_by_section=None, node_images=None):
    sec = {"id": "delivery", "heading": "Delivering Your Puppy To Leeds",
           "keywords": {"primary": ["blue staffy puppies leeds"], "lsi": ["puppy delivery"]},
           "tree": [{"level": 3, "heading": "Vaccinations Before The Journey", "intent": "",
                     "children": [], "images": node_images if node_images is not None else [
                         {"slot": "delivery-vacc", "kind": "photo", "required": True,
                          "prompt": "a puppy being vaccinated"}]}],
           "images": images_by_section if images_by_section is not None else [
               {"slot": "delivery-photo", "kind": "photo", "required": True,
                "prompt": "our van on a delivery run"}]}
    return {"meta": {"slug": SLUG, "page_type": "location"}, "sections": [sec],
            "assets": []}


def test_tokens_fold_plurals_and_drop_the_words_every_image_shares():
    assert IC.tokens("Blue Staffy Puppies: Vaccinations & Deliveries 2026") == {"vaccination", "delivery"}
    assert IC.tokens("kennel-club-assured") == {"kennel", "club", "assured"}


def test_canonical_drops_the_size_sibling_suffix():
    assert IC.canonical("/images/leeds-delivery-van-760.webp?v=1") == "/images/leeds-delivery-van.webp"
    assert IC.canonical("https://example.org/x.webp") is None


def test_iter_slots_reads_section_and_node_slots_in_outline_order():
    got = [(s["id"], n and n["heading"], i["slot"]) for s, n, i in IC.iter_slots(_board())]
    assert got == [("delivery", None, "delivery-photo"),
                   ("delivery", "Vaccinations Before The Journey", "delivery-vacc")]


def test_own_images_come_from_the_migrated_page_in_dist(tmp_path):
    root, _ = _tree(tmp_path)
    own = IC.own_images(_board(), root)
    # The size sibling on the page collapses to its stem file; the header logo is not <main>.
    assert own == [{"file": "/images/leeds-delivery-van.webp", "alt": "Our van delivering a puppy to Leeds"}]


def test_own_images_also_read_the_verbatim_file_and_the_record_assets(tmp_path):
    root, _ = _tree(tmp_path)
    b = _board()
    b["meta"]["slug"] = "blue-staffy-health-uk"
    b["assets"] = [{"slot": "x", "file": "/images/family-garden-play.webp", "alt": "Garden"}]
    files = [o["file"] for o in IC.own_images(b, root)]
    assert files == ["/images/puppy-vaccinations-uk.webp", "/images/kc-registered-staffy-puppies.webp",
                     "/images/family-garden-play.webp"]


def test_served_pool_is_the_manifest_without_the_logo(tmp_path):
    root, _ = _tree(tmp_path)
    assert [s["file"] for s in IC.served_images(root)] == [
        "/images/family-garden-play.webp", "/images/kc-registered-staffy-puppies.webp",
        "/images/leeds-delivery-van.webp", "/images/puppy-vaccinations-uk.webp"]


def test_assets_pool_skips_non_images_and_files_already_served(tmp_path):
    root, assets = _tree(tmp_path)
    fresh, already = IC.asset_images(assets, root)
    assert [f["asset"] for f in fresh] == ["File name- vaccination-card-close-up .jpg .jpg",
                                           "Leeds-Kennel-Club-Show.jpg"]
    assert fresh[0]["ingest_as"] == "/images/vaccination-card-close-up.webp"
    # Byrd1.jpg was ingested as puppies/byrd-byrd1.webp; family-garden-play.png is served as .webp.
    assert sorted(already) == ["Byrd1.jpg", "family-garden-play.png"]
    assert IC.asset_images(tmp_path / "nowhere", root) == ([], [])


def test_usage_index_ignores_previews_and_reads_every_page(tmp_path):
    root, _ = _tree(tmp_path)
    used, alts = IC.usage_and_alts(root)
    assert used["/images/puppy-vaccinations-uk.webp"] == ["/blue-staffy-health-uk/"]
    assert "/images/family-garden-play.webp" not in used          # only on a board preview
    assert alts["/images/puppy-vaccinations-uk.webp"] == ["Vaccinations", "A puppy at the vet after its vaccinations"]


def test_candidates_rank_own_then_served_then_assets_and_flag_reuse(tmp_path):
    root, assets = _tree(tmp_path)
    r = IC.candidates(_board(), root, assets, per_pool=2)
    assert r["pools"] == {"own": 1, "served": 3, "assets": 2, "assets_already_served": 2}
    photo, vacc = r["slots"]
    # The page's own van photo leads; the folder's Leeds show photo follows on one word.
    assert [(c["pool"], c["pick"]) for c in photo["candidates"]] == [
        ("own", "file:/images/leeds-delivery-van.webp"), ("assets", "assets:Leeds-Kennel-Club-Show.jpg")]
    assert photo["candidates"][0]["matched"] == ["delivering", "delivery", "leed", "van"]
    assert photo["candidates"][1]["score"] == 1
    # An H3 slot is scored on its section's heading too, so the page's own photo still leads;
    # the served vaccination photo and the folder's vaccination card follow in pool order.
    assert [(c["pool"], c["pick"]) for c in vacc["candidates"]] == [
        ("own", "file:/images/leeds-delivery-van.webp"),
        ("served", "file:/images/puppy-vaccinations-uk.webp"),
        ("assets", "assets:File name- vaccination-card-close-up .jpg .jpg"),
        ("assets", "assets:Leeds-Kennel-Club-Show.jpg")]
    # Reuse is visible: the served vaccination photo is already on the health page.
    assert vacc["candidates"][1]["used_on"] == ["/blue-staffy-health-uk/"]
    assert vacc["candidates"][2]["ingest_as"] == "/images/vaccination-card-close-up.webp"
    # The van is suggested once; the H3 slot is offered the next image instead.
    assert photo["suggested"]["pick"] == "file:/images/leeds-delivery-van.webp"
    assert vacc["suggested"]["pick"] == "file:/images/puppy-vaccinations-uk.webp"


def test_cli_prints_json_and_writes_only_when_asked(tmp_path, monkeypatch, capsys):
    root, assets = _tree(tmp_path)
    (root / "data" / "boards").mkdir(parents=True)
    (root / "data" / "boards" / (IC.slug_file(SLUG) + ".json")).write_text(json.dumps(_board()))
    monkeypatch.setattr(IC, "ROOT", root)
    assert IC.main([SLUG, "--assets-dir", str(assets)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["slug"] == SLUG and len(out["slots"]) == 2
    assert not (root / "data" / "boards" / "candidates").exists()
    assert IC.main([SLUG, "--assets-dir", str(assets), "--write"]) == 0
    written = root / "data" / "boards" / "candidates" / "uk-locations--blue-staffy-puppies-leeds.json"
    assert json.loads(written.read_text())["slots"][0]["slot"] == "delivery-photo"
    assert json.loads(written.read_text())["assets_dir"] == "../Assets/Images"
    assert IC.main(["uk-locations/nowhere", "--assets-dir", str(assets)]) == 2


# ── review follow-ups (Task 9 review) ───────────────────────────────────────────────────
def test_canonical_keeps_a_real_size_named_file_unless_its_original_exists(tmp_path):
    root, _ = _tree(tmp_path)
    (root / "public" / "images" / "puppies" / "byrd-card-800.webp").write_bytes(b"x")
    assert IC.canonical("/images/puppies/byrd-card-800.webp", root) == "/images/puppies/byrd-card-800.webp"
    assert IC.already_served("Byrd-Card-800.jpg", IC.served_stems(root))
    assert IC.canonical("/images/leeds-delivery-van-760.webp", root) == "/images/leeds-delivery-van.webp"
    # A page that shows the card keeps the card's real name in the own pool.
    page = root / "dist" / "uk-locations" / "blue-staffy-puppies-leeds" / "index.html"
    page.write_text(_page([("/images/puppies/byrd-card-800.webp", "Byrd, our blue boy")]))
    assert [o["file"] for o in IC.own_images(_board(), root)] == ["/images/puppies/byrd-card-800.webp"]
    assert IC.usage_and_alts(root)[0]["/images/puppies/byrd-card-800.webp"] == [
        "/uk-locations/blue-staffy-puppies-leeds/"]


def test_generic_sales_words_do_not_rank():
    assert IC.tokens("Blue staffy puppies for sale near me: buy from a breeder now, new home available") == set()
    assert IC.tokens("Breeders") == set()
    words = IC.tokens("Puppies For Sale With Their Mother")
    assert words == {"mother"}
    pools = {"own": [], "assets": [],
             "served": [{"file": "/images/puppies-for-sale-uk.webp"}, {"file": "/images/dam-resting.webp"}]}
    alts = {"/images/dam-resting.webp": ["The litter's mother resting"]}
    got = IC.rank(words, pools, alts, {}, "/x/", per_pool=3)
    assert [c["file"] for c in got] == ["/images/dam-resting.webp"]


def test_a_word_is_dropped_when_its_raw_or_folded_form_is_generic():
    assert IC.tokens("this thus plus always") == set()
    assert IC.tokens("status analysis kennels") == {"status", "analysis", "kennel"}


def test_asset_stem_strips_only_an_image_second_extension_and_empty_stems_are_skipped(tmp_path):
    assert IC.asset_stem("sbt-history.v2.jpg") == "sbt-history-v2"
    assert IC.asset_stem("File name- vaccination-card-close-up .jpg .jpg") == "vaccination-card-close-up"
    assert IC.asset_stem("File name- .jpg") == ""
    root, assets = _tree(tmp_path)
    (assets / "File name- .jpg").write_bytes(b"x")
    fresh, already = IC.asset_images(assets, root)
    assert "File name- .jpg" not in [f["asset"] for f in fresh] + already


def test_an_upper_case_extension_is_an_image(tmp_path):
    root, assets = _tree(tmp_path)
    (assets / "Kennel-Visit.JPG").write_bytes(b"x")
    fresh, _ = IC.asset_images(assets, root)
    assert {"asset": "Kennel-Visit.JPG", "ingest_as": "/images/kennel-visit.webp"} in fresh


def test_a_malformed_verbatim_file_is_skipped_with_a_warning(tmp_path, capsys):
    root, _ = _tree(tmp_path)
    (root / "data" / "verbatim" / "broken.json").write_text("{not json")
    (root / "data" / "verbatim" / "listy.json").write_text("[1, 2]")
    used, alts = IC.usage_and_alts(root)
    assert alts["/images/puppy-vaccinations-uk.webp"] == ["Vaccinations", "A puppy at the vet after its vaccinations"]
    b = _board()
    b["meta"]["slug"] = "broken"
    assert IC.own_images(b, root) == []
    err = capsys.readouterr().err
    assert "broken.json" in err and "listy.json" in err


def test_the_report_names_the_folder_only_when_it_is_not_the_default(tmp_path, monkeypatch):
    root, assets = _tree(tmp_path)
    assert IC.candidates(_board(), root, assets)["assets_dir"] == "../Assets/Images"
    monkeypatch.setattr(IC, "ASSETS_DIR", assets)
    assert IC.candidates(_board(), root, assets)["assets_dir"] is None
    assert IC.candidates(_board(), root, None)["assets_dir"] is None


def test_without_dist_the_pools_still_work(tmp_path):
    root, assets = _tree(tmp_path)
    shutil.rmtree(root / "dist")
    assert IC.dist_pages(root) == {}
    assert IC.usage_and_alts(root)[0] == {}
    r = IC.candidates(_board(), root, assets, per_pool=2)
    assert r["pools"]["own"] == 0 and r["pools"]["served"] == 4
    assert all(c["used_on"] == [] for s in r["slots"] for c in s["candidates"])


def test_ties_within_a_pool_order_by_pick():
    pools = {"own": [], "served": [{"file": "/images/van-b.webp"}, {"file": "/images/van-a.webp"}],
             "assets": [{"asset": "van-c.jpg", "ingest_as": "/images/van-c.webp"}]}
    got = IC.rank({"van"}, pools, {}, {}, "/x/", per_pool=3)
    assert [c["pick"] for c in got] == ["file:/images/van-a.webp", "file:/images/van-b.webp", "assets:van-c.jpg"]


# ── Task 12a item 3: a location board's bare slug finds its built route ─────────────────
def _glasgow(tmp_path):
    root, _ = _tree(tmp_path)
    (root / "data" / "page-map.json").write_text(json.dumps({"pages": [
        {"url": "/uk-locations/staffy-breeding-dogs-glasgow/"}, {"url": "/blue-staffy-health-uk/"}]}))
    page = root / "dist" / "uk-locations" / "staffy-breeding-dogs-glasgow"
    page.mkdir(parents=True)
    (page / "index.html").write_text(_page([("/images/family-garden-play.webp", "A Glasgow garden")]))
    return root


def test_a_bare_location_slug_finds_the_same_own_images_as_its_nested_route(tmp_path):
    root = _glasgow(tmp_path)
    bare, nested = _board(), _board()
    bare["meta"]["slug"] = "staffy-breeding-dogs-glasgow"
    nested["meta"]["slug"] = "uk-locations/staffy-breeding-dogs-glasgow"
    want = [{"file": "/images/family-garden-play.webp", "alt": "A Glasgow garden"}]
    assert IC.own_images(nested, root) == want
    assert IC.own_images(bare, root) == want
    assert IC.page_route("staffy-breeding-dogs-glasgow", root) == "/uk-locations/staffy-breeding-dogs-glasgow/"
    assert IC.page_route("index", root) == "/"


def test_the_bare_slug_is_its_own_page_when_counting_reuse(tmp_path):
    """`used_on` leaves out the page itself, found by its route, not by the bare slug."""
    root = _glasgow(tmp_path)
    b = _board(images_by_section=[{"slot": "garden-photo", "kind": "photo", "required": True,
                                   "prompt": "a garden in glasgow"}], node_images=[])
    b["meta"]["slug"] = "staffy-breeding-dogs-glasgow"
    row = IC.candidates(b, root, tmp_path / "Assets" / "Images", per_pool=3)["slots"][0]
    own = [c for c in row["candidates"] if c["pool"] == "own"]
    assert own and own[0]["file"] == "/images/family-garden-play.webp"
    assert "/uk-locations/staffy-breeding-dogs-glasgow/" not in own[0]["used_on"]


def test_the_real_glasgow_board_slug_resolves_like_its_route():
    if not (ROOT / "dist" / "uk-locations" / "staffy-breeding-dogs-glasgow" / "index.html").is_file():
        import pytest
        pytest.skip("dist/ not built")
    b = _board()
    b["meta"]["slug"] = "staffy-breeding-dogs-glasgow"
    bare = IC.own_images(b, ROOT)
    b["meta"]["slug"] = "uk-locations/staffy-breeding-dogs-glasgow"
    assert bare and bare == IC.own_images(b, ROOT)


# ── Task 20 (G8): a location board is never offered another city's photo ───────────────────
MAN_SLUG = "blue-staffy-puppies-manchester-uk"


def _cities_tree(tmp_path):
    root, assets = _tree(tmp_path)
    (root / "data" / "locations.json").write_text(json.dumps([
        {"slug": MAN_SLUG, "city": "Manchester"}, {"slug": "blue-staffy-puppies-london", "city": "London"},
        {"slug": "staffy-breeding-dogs-glasgow", "city": "Glasgow (breeding dogs)"},
        {"slug": "blue-staffy-puppies-for-sale-leeds", "city": "Leeds"},
        {"slug": "blue-staffy-puppies-uk", "city": "UK"}]))
    imgs = root / "public" / "images"
    manifest = json.loads((root / "data" / "image-manifest.json").read_text())
    for stem in ("victoria-family-blue-staffy-manchester", "mark-family-blue-staffy-london",
                 "family-friendly-blue-staffy-glasgow", "family-sofa-cuddle"):
        (imgs / f"{stem}.webp").write_bytes(b"x")
        manifest[stem] = {"w": 1, "h": 1, "sib_w": None}
    (root / "data" / "image-manifest.json").write_text(json.dumps(manifest))
    # family-sofa-cuddle names no city in its stem, but the site shows it with a London alt.
    (root / "dist" / "blue-staffy-health-uk" / "index.html").write_text(_page([
        ("/images/puppy-vaccinations-uk.webp", "Vaccinations"),
        ("/images/family-sofa-cuddle.webp", "A family in London cuddling their puppy")]))
    page = root / "dist" / "uk-locations" / MAN_SLUG
    page.mkdir(parents=True)
    # The migrated Manchester page itself served a Glasgow photo: an own photo is dropped too.
    (page / "index.html").write_text(_page([
        ("/images/family-friendly-blue-staffy-glasgow.webp", "A family with their blue staffy")]))
    return root, assets


def _family_board(slug=MAN_SLUG, page_type="location"):
    b = _board(images_by_section=[{"slot": "family-photo", "kind": "photo", "required": True,
                                   "prompt": "a family with their puppy at home"}], node_images=[])
    b["meta"] = {"slug": slug, "page_type": page_type}
    return b


def _offered(report):
    return {c["file"] for s in report["slots"] for c in s["candidates"] if c["file"]}


def test_a_location_board_is_offered_no_other_citys_photo(tmp_path):
    root, assets = _cities_tree(tmp_path)
    got = _offered(IC.candidates(_family_board(), root, assets, per_pool=10))
    assert "/images/victoria-family-blue-staffy-manchester.webp" in got
    for f in ("/images/mark-family-blue-staffy-london.webp",
              "/images/family-friendly-blue-staffy-glasgow.webp",   # own photo, Glasgow stem
              "/images/family-sofa-cuddle.webp",                    # London named in its alt
              "/images/leeds-delivery-van.webp"):                   # Leeds stem
        assert f not in got, f


def test_a_non_location_board_keeps_city_named_photos(tmp_path):
    root, assets = _cities_tree(tmp_path)
    got = _offered(IC.candidates(_family_board("blue-staffy-blog-guides", "hub"), root, assets,
                                 per_pool=10))
    assert "/images/mark-family-blue-staffy-london.webp" in got
    assert "/images/family-sofa-cuddle.webp" in got


def test_the_real_manchester_board_is_offered_no_other_citys_photo():
    import original_slots as OS
    board = _family_board()
    report = IC.candidates(board, ROOT, ROOT / "no-assets-folder", per_pool=50)
    _used, alts = IC.usage_and_alts(ROOT)
    names = OS.cities(ROOT)
    files = _offered(report)
    assert "/images/victoria-family-blue-staffy-manchester.webp" in files
    for f in files:
        text = " ".join([pathlib.PurePosixPath(f).stem.replace("-", " ")] + alts.get(f, []))
        assert set(OS.cities_named(text, names)) <= {"Manchester"}, (f, OS.cities_named(text, names))
