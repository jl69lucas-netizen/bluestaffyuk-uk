"""scripts/ingest_image.py: folder photos in, generated drafts approved by their exact bytes,
and never a served image replaced (IMAGE-DESIGNS.md §6 and §9, CLAUDE.md rule 11)."""
import datetime
import json
import random
import pathlib
import subprocess
import sys

import pytest
from PIL import Image

import ingest_image
import reframe_og

from ingest_image import (PICK, Refused, default_stem, draft, file_sha, folder,
                          ingested_manifest_rows, publish, slug_file, stem_problems)

ROOT = pathlib.Path(__file__).resolve().parents[2]
DAY = datetime.date(2026, 9, 24)
# A page built before project 5: style B (blurfill) is retired for new pages (user ruling
# 2026-09-26, tests/py/test_no_blurfill_bleed.py) and kept only for these, so the B cases
# below exercise the frozen-page path.
SLUG = "blue-staffy-health-uk"
STEM = "blue-staffy-puppy-garden-carlisle"


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "public/images").mkdir(parents=True)
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "data/image-manifest.json").write_text(
        json.dumps({"blue-staffy-family-dog-uk": {"w": 1408, "h": 768, "sib_w": 760}}),
        encoding="utf-8")
    (tmp_path / "public/images/blue-staffy-family-dog-uk.webp").write_bytes(b"served")
    board = {"meta": {"slug": SLUG, "status": "approved"},
             "assets": [{"slot": "garden-photo", "kind": "photo", "w": 1408, "h": 768,
                         "required": True, "status": "missing", "file": None,
                         "alt": "A blue Staffy puppy in a Carlisle garden"}],
             "approval": {"approved_at": "2026-09-24", "picks": {}}}
    (tmp_path / "data/boards" / (slug_file(SLUG) + ".json")).write_text(
        json.dumps(board, indent=2), encoding="utf-8")
    return tmp_path


def board(repo):
    return json.loads((repo / "data/boards" / (slug_file(SLUG) + ".json")).read_text())


def approve(repo, pick):
    p = repo / "data/boards" / (slug_file(SLUG) + ".json")
    b = json.loads(p.read_text())
    b["approval"]["picks"]["img:garden-photo"] = pick
    p.write_text(json.dumps(b, indent=2))


@pytest.fixture
def master(tmp_path):
    p = tmp_path / "Assets" / "Roman1.jpg"
    p.parent.mkdir()
    Image.new("RGB", (900, 1200), (91, 124, 153)).save(p)
    return p


# ── folder ───────────────────────────────────────────────────────────────────────────────

def test_folder_bakes_records_names_it_on_the_board_and_leaves_the_master(repo, master):
    before = master.read_bytes()
    folder(master, STEM, og_style="B", mobcrop="4:5", slug=SLUG, slot="garden-photo",
           root=repo, today=DAY)
    assert master.read_bytes() == before, "the master is read, never moved or edited"
    full = repo / "public/images" / (STEM + ".webp")
    sib = repo / "public/images" / (STEM + "-760.webp")
    assert Image.open(full).size == (1408, 768) and full.stat().st_size < 95 * 1024
    assert Image.open(sib).size == (760, 415) and sib.stat().st_size < 55 * 1024
    manifest = json.loads((repo / "data/image-manifest.json").read_text())
    assert manifest[STEM] == {"w": 1408, "h": 768, "sib_w": 760}
    assert "blue-staffy-family-dog-uk" in manifest, "existing rows are kept"
    ledger = json.loads((repo / "data/image-ingest.json").read_text())
    assert ledger[STEM]["og_style"] == "B" and ledger[STEM]["source"] == "assets-folder"
    row = board(repo)["assets"][0]
    assert (row["file"], row["status"]) == ("/images/%s.webp" % STEM, "baked")


def test_a_renamed_folder_file_must_be_named_on_the_board(repo, master):
    with pytest.raises(Refused, match="pass --board and --slot"):
        folder(master, STEM, og_style="B", root=repo)


def test_the_default_name_needs_no_board_but_must_still_be_an_seo_name(repo, tmp_path):
    good = tmp_path / "Assets" / "blue-staffy-puppy-garden-carlisle.jpg"
    good.parent.mkdir(exist_ok=True)
    Image.new("RGB", (1600, 900), (91, 124, 153)).save(good)
    r = folder(good, og_style="A", root=repo, today=DAY)
    assert r["stem"] == "blue-staffy-puppy-garden-carlisle"
    bad = tmp_path / "Assets" / "Roman2.jpg"
    Image.new("RGB", (900, 1200), (91, 124, 153)).save(bad)
    with pytest.raises(Refused, match="lowercase words"):
        folder(bad, og_style="B", root=repo)


def test_a_css_component_style_is_baked_at_native_ratio(repo, master):
    folder(master, "blue-staffy-puppy-portrait-frame", og_style="D", slug=SLUG,
           slot="garden-photo", root=repo, today=DAY)
    rows = ingested_manifest_rows(repo)
    assert rows["blue-staffy-puppy-portrait-frame"] == {"w": 900, "h": 1200, "sib_w": 760}


def test_rule_11_a_served_stem_is_refused_and_nothing_is_written(repo, master):
    with pytest.raises(Refused, match="already served"):
        folder(master, "blue-staffy-family-dog-uk", og_style="B", slug=SLUG,
               slot="garden-photo", root=repo)
    assert (repo / "public/images/blue-staffy-family-dog-uk.webp").read_bytes() == b"served"
    assert not (repo / "data/image-ingest.json").exists()


def test_a_slot_without_a_planned_assets_row_is_refused(repo, master):
    with pytest.raises(Refused, match="plans no assets"):
        folder(master, STEM, og_style="B", slug=SLUG, slot="other-photo", root=repo)


def test_dry_run_writes_nothing(repo, master):
    folder(master, STEM, og_style="E", slug=SLUG, slot="garden-photo", root=repo, dry_run=True)
    assert not (repo / "public/images" / (STEM + ".webp")).exists()
    assert board(repo)["assets"][0]["file"] is None


# ── draft → approve → publish ────────────────────────────────────────────────────────────

def test_a_draft_lands_outside_public_and_names_its_approving_pick(repo, master):
    r = draft(master, SLUG, "garden-photo", og_style="B", mobcrop="4:5", root=repo)
    assert r["path"] == repo / "data/boards/generated" / slug_file(SLUG) / "garden-photo.webp"
    assert Image.open(r["path"]).size == (1408, 768)
    assert r["sha12"] == file_sha(r["path"]) and r["pick"] == "og:B:" + r["sha12"]
    assert PICK.match(r["pick"])
    assert not list((repo / "public/images").glob("blue-staffy-puppy*")), "nothing ships yet"


def test_publish_refuses_until_the_board_approves_those_exact_bytes(repo, master):
    r = draft(master, SLUG, "garden-photo", og_style="B", root=repo)
    with pytest.raises(Refused, match="not approved as an image"):
        publish(SLUG, "garden-photo", STEM, root=repo)
    approve(repo, "og:B")                                   # the style, not the image
    with pytest.raises(Refused, match="not approved as an image"):
        publish(SLUG, "garden-photo", STEM, root=repo)
    approve(repo, "og:B:" + "0" * 12)                       # some other bytes
    with pytest.raises(Refused, match="not the image the breeder approved"):
        publish(SLUG, "garden-photo", STEM, root=repo)
    assert not (repo / "public/images" / (STEM + ".webp")).exists()
    approve(repo, r["pick"] + "\n")                        # the gate's grammar: whole string only
    with pytest.raises(Refused, match="not approved as an image"):
        publish(SLUG, "garden-photo", STEM, root=repo)
    approve(repo, r["pick"])
    out = publish(SLUG, "garden-photo", STEM, root=repo, today=DAY)
    served = repo / "public/images" / (STEM + ".webp")
    assert served.read_bytes() == r["path"].read_bytes(), "copied UNCHANGED"
    assert out["sha12"] == r["sha12"] and file_sha(served) == r["sha12"]
    assert Image.open(repo / "public/images" / (STEM + "-760.webp")).size == (760, 415)
    row = board(repo)["assets"][0]
    assert (row["file"], row["status"]) == ("/images/%s.webp" % STEM, "baked")
    ledger = json.loads((repo / "data/image-ingest.json").read_text())
    assert ledger[STEM]["source"] == "generate" and ledger[STEM]["og_style"] == "B"


def test_an_infographic_draft_is_approved_with_an_ig_pick(repo, master):
    r = draft(master, SLUG, "garden-photo", infographic="IG-2", root=repo)
    assert r["pick"] == "ig:IG-2:" + r["sha12"]
    approve(repo, r["pick"])
    assert publish(SLUG, "garden-photo", STEM, root=repo)["infographic_style"] == "IG-2"


def test_bad_requests_are_refused(repo, master):
    with pytest.raises(Refused, match="exactly one"):
        draft(master, SLUG, "garden-photo", root=repo)
    with pytest.raises(Refused, match="not named"):
        draft(master, SLUG, "garden-photo", infographic="IG-9", root=repo)
    with pytest.raises(Refused, match="does not exist"):
        draft(master.parent / "gone.jpg", SLUG, "garden-photo", og_style="B", root=repo)
    with pytest.raises(Refused, match="no draft"):
        publish(SLUG, "garden-photo", STEM, root=repo)


# ── names ────────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("stem", ["IMG_4823", "roman1", "blue-staffy-photo-final",
                                  "Blue-Staffy-Garden", "blue--staffy-garden"])
def test_a_non_seo_stem_is_refused(stem):
    assert stem_problems(stem)


def test_a_good_stem_passes():
    assert stem_problems(STEM) == []


NAMES = ["Roman1.jpg", "File name- defra-pet-transport-process.png .png",
         "blue-staffy-for-sale-uk.png", "Christa.jpeg", "sbt-history.v2.jpg", "File name- .jpg"]


def test_default_stem_and_slug_file():
    assert [default_stem(n) for n in NAMES] == ["roman1", "defra-pet-transport-process",
                                                "blue-staffy-for-sale-uk", "christa",
                                                "sbt-history-v2", ""]
    assert slug_file("uk-locations/blue-staffy-leeds") == "uk-locations--blue-staffy-leeds"


def test_the_names_match_the_candidates_script(tmp_path):
    """scripts/image_candidates.py decides where the build gate looks for a folder file.
    Skips until that module exists; from then on the two must agree."""
    ic = pytest.importorskip("image_candidates")
    assert [default_stem(n) for n in NAMES] == [ic.asset_stem(n) for n in NAMES]
    # One rule, not two copies kept in step: default_stem delegates to asset_stem.
    assert ingest_image.default_stem.__code__.co_names.count("asset_stem") == 1
    # An empty stem is the same on both sides: the candidates script skips the file and
    # ingest refuses the name.
    assert default_stem("File name- .jpg") == ic.asset_stem("File name- .jpg") == ""
    (tmp_path / "File name- .jpg").write_bytes(b"x")
    assert ic.asset_images(tmp_path, ROOT) == ([], [])
    assert stem_problems(default_stem("File name- .jpg"))
    assert slug_file(SLUG) == ic.slug_file(SLUG)


def test_the_pick_grammar_matches_the_build_gate():
    rules = pytest.importorskip("image_rules")
    # One grammar, not two copies kept in step: ingest reuses the build gate's PICK, with its
    # containment (no `.`/`..` segments) and its whole-string match.
    assert PICK is rules.PICK
    assert ingest_image.SLOT_ID is rules.SLOT_ID
    for v in ("file:/images/a.webp", "assets:Roman1.jpg", "og:B", "og:B:0123456789ab",
              "ig:IG-3", "ig:IG-3:0123456789ab", "og:F", "ig:IG-9", "og:B:xyz",
              "og:B:0123456789ab\n", "file:/images/../x.webp", "assets:..", "assets:a/b.jpg"):
        assert bool(PICK.fullmatch(v)) == (rules.parse_pick(v) is not None), v


# ── the re-bake and the real ledger ──────────────────────────────────────────────────────

def test_ledger_rows_feed_the_rebake(repo, master):
    folder(master, STEM, og_style="A", slug=SLUG, slot="garden-photo", root=repo, today=DAY)
    assert ingested_manifest_rows(repo) == {STEM: {"w": 1408, "h": 768, "sib_w": 760}}
    assert ingested_manifest_rows(repo / "nowhere") == {}


def test_bake_images_carries_ingested_rows_over():
    """`npm run bake` rewrites the manifest from the migrated pages; without this call an
    ingested image would lose its row on the next bake and render without a srcset."""
    assert "ingested_manifest_rows()" in (ROOT / "scripts/bake_images.py").read_text(encoding="utf-8")


def test_the_real_ledger_is_valid_and_every_row_is_in_the_manifest():
    ledger = json.loads((ROOT / "data/image-ingest.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "data/image-manifest.json").read_text(encoding="utf-8"))
    for stem, row in ledger.items():
        assert manifest.get(stem) == {"w": row["w"], "h": row["h"], "sib_w": row["sib_w"]}
        assert (ROOT / "public/images" / (stem + ".webp")).exists(), stem


def test_cli_exit_codes(master):
    script = ROOT / "scripts/ingest_image.py"
    proc = subprocess.run([sys.executable, str(script), "folder", str(master), "--stem", STEM,
                           "--og-style", "B", "--dry-run"], capture_output=True, text=True)
    assert proc.returncode == 2 and proc.stderr.startswith("REFUSED:"), proc.stderr
    assert proc.stdout == ""
    proc = subprocess.run([sys.executable, str(script), "publish", "--board", "no-such-page",
                           "--slot", "x", "--stem", STEM], capture_output=True, text=True)
    assert proc.returncode == 2 and "no board" in proc.stderr, proc.stderr


# ── review fixes ─────────────────────────────────────────────────────────────────────────
def noisy_master(tmp_path, name="noise.png", w=1600, h=900):
    p = tmp_path / "Assets" / name
    p.parent.mkdir(exist_ok=True)
    Image.frombytes("RGB", (w, h), random.Random(0).randbytes(w * h * 3)).save(p)
    return p


def snapshot(repo):
    """Every file under the tmp repo with its bytes, to prove a refusal wrote nothing."""
    return {q.relative_to(repo).as_posix(): q.read_bytes()
            for q in sorted(repo.rglob("*")) if q.is_file() and "Assets" not in q.parts}


def test_folder_refuses_an_image_that_misses_the_size_budget(repo, tmp_path):
    before = snapshot(repo)
    with pytest.raises(Refused, match=r"KB.*95 KB"):
        folder(noisy_master(tmp_path), STEM, og_style="A", slug=SLUG, slot="garden-photo",
               root=repo, today=DAY)
    assert snapshot(repo) == before, "nothing written, not even a temp file"


def test_folder_refuses_when_only_the_sibling_misses_its_budget(repo, master, monkeypatch):
    monkeypatch.setattr(reframe_og, "SIB_MAX_KB", 0.1)
    before = snapshot(repo)
    with pytest.raises(Refused, match=r"-760.*KB"):
        folder(master, STEM, og_style="B", slug=SLUG, slot="garden-photo", root=repo)
    assert snapshot(repo) == before


def test_draft_refuses_an_image_that_misses_the_size_budget(repo, tmp_path):
    with pytest.raises(Refused, match="KB"):
        draft(noisy_master(tmp_path), SLUG, "garden-photo", og_style="A", root=repo)
    assert not (repo / "data/boards/generated").exists() or not list(
        (repo / "data/boards/generated").rglob("*.*"))


def test_publish_refuses_an_approved_draft_over_the_budget(repo, tmp_path):
    big = ingest_image.draft_path(SLUG, "garden-photo", repo)
    big.parent.mkdir(parents=True)
    Image.frombytes("RGB", (1408, 768), random.Random(1).randbytes(1408 * 768 * 3)).save(
        big, "WEBP", quality=95)
    approve(repo, "og:B:" + file_sha(big))
    before = snapshot(repo)
    with pytest.raises(Refused, match="KB"):
        publish(SLUG, "garden-photo", STEM, root=repo)
    assert snapshot(repo) == before


def test_native_ratio_styles_are_capped_at_1760_tall(repo, tmp_path):
    tall = tmp_path / "Assets" / "tall.png"
    tall.parent.mkdir(exist_ok=True)
    Image.new("RGB", (1000, 4000), (91, 124, 153)).save(tall)
    folder(tall, "blue-staffy-puppy-tall-portrait", og_style="D", slug=SLUG,
           slot="garden-photo", root=repo, today=DAY)
    row = ingested_manifest_rows(repo)["blue-staffy-puppy-tall-portrait"]
    assert row["h"] == 1760 and row["w"] == 440


def fail_the_sibling(monkeypatch):
    real = reframe_og.save_webp

    def boom(img, path, maxkb):
        if "-760" in str(path):
            raise OSError("disk full")
        return real(img, path, maxkb)
    monkeypatch.setattr(reframe_og, "save_webp", boom)


def test_a_failed_publish_leaves_nothing_and_a_retry_succeeds(repo, master, monkeypatch):
    r = draft(master, SLUG, "garden-photo", og_style="B", root=repo)
    approve(repo, r["pick"])
    before = snapshot(repo)
    fail_the_sibling(monkeypatch)
    with pytest.raises(OSError, match="disk full"):
        publish(SLUG, "garden-photo", STEM, root=repo, today=DAY)
    assert sorted(q.name for q in (repo / "public/images").iterdir()) == [
        "blue-staffy-family-dog-uk.webp"], "no image and no temp file in public/images"
    assert snapshot(repo) == before, "ledger, manifest and board untouched"
    monkeypatch.undo()
    publish(SLUG, "garden-photo", STEM, root=repo, today=DAY)
    assert (repo / "public/images" / (STEM + "-760.webp")).exists()
    assert board(repo)["assets"][0]["status"] == "baked"


def test_a_failed_folder_ingest_leaves_nothing(repo, master, monkeypatch):
    before = snapshot(repo)
    fail_the_sibling(monkeypatch)
    with pytest.raises(OSError):
        folder(master, STEM, og_style="B", slug=SLUG, slot="garden-photo", root=repo)
    assert snapshot(repo) == before


def test_a_transparent_master_is_baked_on_bone(repo, tmp_path):
    p = tmp_path / "Assets" / "cutout.png"
    p.parent.mkdir(exist_ok=True)
    im = Image.new("RGBA", (1408, 768), (91, 124, 153, 255))
    im.paste((0, 0, 0, 0), (0, 0, 100, 100))
    im.save(p)
    r = draft(p, SLUG, "garden-photo", og_style="E", root=repo)
    with Image.open(r["path"]) as out:
        px = out.convert("RGB").getpixel((10, 10))
    assert all(abs(a - b) <= 6 for a, b in zip(px, reframe_og.BONE_50)), px


@pytest.mark.parametrize("kw", [{"slug": SLUG}, {"slot": "garden-photo"}])
def test_board_and_slot_come_together(repo, master, kw):
    with pytest.raises(Refused, match="together"):
        folder(master, og_style="B", root=repo, **kw)


def test_cli_board_without_slot_exits_2(master):
    script = ROOT / "scripts/ingest_image.py"
    proc = subprocess.run([sys.executable, str(script), "folder", str(master), "--og-style", "B",
                           "--board", SLUG, "--dry-run"], capture_output=True, text=True)
    assert proc.returncode == 2 and proc.stderr.startswith("REFUSED:") and "together" in proc.stderr


@pytest.mark.parametrize("bad", ["4:0", "4x5", "0:5", "4:5:1"])
def test_a_malformed_mobcrop_is_refused(repo, master, bad):
    with pytest.raises(Refused, match="mobcrop"):
        folder(master, STEM, og_style="B", mobcrop=bad, slug=SLUG, slot="garden-photo", root=repo)
    with pytest.raises(Refused, match="mobcrop"):
        draft(master, SLUG, "garden-photo", og_style="B", mobcrop=bad, root=repo)


def test_mobcrop_with_a_non_b_style_warns(repo, master, capsys):
    folder(master, STEM, og_style="A", mobcrop="4:5", slug=SLUG, slot="garden-photo", root=repo,
           dry_run=True)
    assert "warning" in capsys.readouterr().err.lower()


def test_a_corrupt_master_is_refused(repo, tmp_path):
    p = tmp_path / "Assets" / "broken.jpg"
    p.parent.mkdir(exist_ok=True)
    p.write_bytes(b"\xff\xd8\xff not really a jpeg")
    with pytest.raises(Refused, match="cannot be read"):
        draft(p, SLUG, "garden-photo", og_style="B", root=repo)


def test_a_decompression_bomb_is_refused(repo, master, monkeypatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1000)
    with pytest.raises(Refused, match="cannot be read"):
        draft(master, SLUG, "garden-photo", og_style="B", root=repo)


def test_a_bomb_warning_is_refused_too(repo, master, monkeypatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 900 * 1200 - 1)   # warns, does not raise
    with pytest.raises(Refused, match="cannot be read"):
        draft(master, SLUG, "garden-photo", og_style="B", root=repo)


def test_an_animated_master_is_refused(repo, tmp_path):
    p = tmp_path / "Assets" / "anim.png"
    p.parent.mkdir(exist_ok=True)
    a, b = Image.new("RGB", (40, 40), (91, 124, 153)), Image.new("RGB", (40, 40), (0, 0, 0))
    a.save(p, save_all=True, append_images=[b])
    with pytest.raises(Refused, match="animated"):
        draft(p, SLUG, "garden-photo", og_style="B", root=repo)


@pytest.mark.parametrize("bad", ["../etc", "UK-Locations/x", "a//b", "/abs", "a/b/", "a b"])
def test_a_malformed_slug_is_refused(repo, master, bad):
    with pytest.raises(Refused, match="slug"):
        draft(master, bad, "garden-photo", og_style="B", root=repo)
    with pytest.raises(Refused, match="slug"):
        publish(bad, "garden-photo", STEM, root=repo)


@pytest.mark.parametrize("dangling", [True, False])
def test_a_symlinked_stem_is_already_taken(repo, master, tmp_path, dangling):
    target = tmp_path / ("gone.webp" if dangling else "real.webp")
    if not dangling:
        target.write_bytes(b"x")
    (repo / "public/images" / (STEM + ".webp")).symlink_to(target)
    assert ingest_image.served(STEM, repo)
    with pytest.raises(Refused, match="already served"):
        folder(master, STEM, og_style="B", slug=SLUG, slot="garden-photo", root=repo)


def test_publish_has_no_bare_assert_and_no_assets_constant():
    src = (ROOT / "scripts/ingest_image.py").read_text(encoding="utf-8")
    assert "\n    assert " not in src
    assert "ASSETS =" not in src


# ── follow-up: dry run checks the budget; a part-way commit names the stem ───────────────
def test_folder_dry_run_refuses_over_budget_exactly_as_a_real_run(repo, tmp_path):
    before = snapshot(repo)
    with pytest.raises(Refused, match=r"KB.*95 KB"):
        folder(noisy_master(tmp_path), STEM, og_style="A", slug=SLUG, slot="garden-photo",
               root=repo, dry_run=True)
    assert snapshot(repo) == before


def test_folder_dry_run_checks_the_sibling_budget_too(repo, master, monkeypatch):
    monkeypatch.setattr(reframe_og, "SIB_MAX_KB", 0.1)
    before = snapshot(repo)
    with pytest.raises(Refused, match="-760"):
        folder(master, STEM, og_style="B", slug=SLUG, slot="garden-photo", root=repo,
               dry_run=True)
    assert snapshot(repo) == before


def test_a_commit_that_stops_part_way_names_the_stem(repo, master, monkeypatch):
    real, calls = ingest_image.os.replace, []

    def flaky(src, dst):
        calls.append(dst)
        if len(calls) == 2:
            raise OSError("device went away")
        return real(src, dst)
    monkeypatch.setattr(ingest_image.os, "replace", flaky)
    with pytest.raises(OSError, match=STEM) as e:
        folder(master, STEM, og_style="B", slug=SLUG, slot="garden-photo", root=repo)
    assert "%s.webp" % STEM in str(e.value) and "device went away" in str(e.value)
    monkeypatch.undo()
    assert not [q for q in repo.rglob(".*.tmp-*")], "the temps that were not moved are removed"


def test_a_slot_id_must_match_whole(repo, master):
    """ingest uses the gate's SLOT_ID with fullmatch: a trailing newline or a leading digit
    is not a slot id."""
    for bad in ("garden-photo\n", "1garden"):
        with pytest.raises(Refused, match="is not a slot id"):
            draft(master, SLUG, bad, og_style="B", root=repo)
        with pytest.raises(Refused, match="is not a slot id"):
            publish(SLUG, bad, STEM, root=repo)


# ── --sibling: an infographic's own phone layout served as -760 ────────────────────────

def _phone_sibling(tmp_path, h=900, noisy=False):
    p = tmp_path / "phone-760.png"
    if noisy:
        rnd = random.Random(7)
        im = Image.new("RGB", (760, h))
        im.putdata([tuple(rnd.randrange(256) for _ in range(3)) for _ in range(760 * h)])
    else:
        im = Image.new("RGBA", (760, h), (0, 0, 0, 0))
        im.paste((40, 60, 80, 255), (40, 40, 720, h - 40))
    im.save(p)
    return p


def test_publish_serves_the_drafts_own_sibling_unchanged(repo, master, tmp_path):
    sib = _phone_sibling(tmp_path)
    r = draft(master, SLUG, "garden-photo", infographic="IG-2", root=repo, sibling=sib)
    stored = repo / "data/boards/generated" / slug_file(SLUG) / "garden-photo-760.webp"
    assert r["sibling"] == stored and Image.open(stored).size == (760, 900)
    assert stored.stat().st_size <= reframe_og.SIB_MAX_KB * 1024
    assert Image.open(stored).convert("RGB").getpixel((5, 5)) != (0, 0, 0), \
        "the transparent margin is laid on bone, never dropped to black"
    approve(repo, r["pick"])
    publish(SLUG, "garden-photo", STEM, root=repo, today=DAY)
    served = repo / "public/images" / (STEM + "-760.webp")
    assert served.read_bytes() == stored.read_bytes(), "the phone layout, not a shrunk box"
    assert Image.open(served).size == (760, 900)
    manifest = json.loads((repo / "data/image-manifest.json").read_text())
    assert manifest[STEM] == {"w": 1408, "h": 768, "sib_w": 760}


def test_a_sibling_over_its_budget_is_refused_and_nothing_written(repo, master, tmp_path):
    with pytest.raises(Refused, match=r"sibling.*KB"):
        draft(master, SLUG, "garden-photo", infographic="IG-2", root=repo,
              sibling=_phone_sibling(tmp_path, h=1600, noisy=True))
    assert not (repo / "data/boards/generated" / slug_file(SLUG)).exists() or not list(
        (repo / "data/boards/generated" / slug_file(SLUG)).glob("garden-photo*.webp"))


def test_a_sibling_must_be_exactly_760_wide(repo, master, tmp_path):
    p = tmp_path / "wide.png"
    Image.new("RGB", (800, 600), (40, 60, 80)).save(p)
    with pytest.raises(Refused, match="760 wide"):
        draft(master, SLUG, "garden-photo", infographic="IG-2", root=repo, sibling=p)


def test_without_a_sibling_publish_shrinks_the_box_and_a_stale_sibling_is_removed(
        repo, master, tmp_path):
    draft(master, SLUG, "garden-photo", infographic="IG-2", root=repo,
          sibling=_phone_sibling(tmp_path))
    r = draft(master, SLUG, "garden-photo", infographic="IG-2", root=repo)
    assert "sibling" not in r
    assert not (repo / "data/boards/generated" / slug_file(SLUG) / "garden-photo-760.webp").exists()
    approve(repo, r["pick"])
    publish(SLUG, "garden-photo", STEM, root=repo, today=DAY)
    assert Image.open(repo / "public/images" / (STEM + "-760.webp")).size == (760, 415)


def test_an_infographic_that_leaves_its_box_mostly_empty_is_refused(repo, tmp_path):
    """The coordinator's review (2026-10-03): the first drafts filled about half the box."""
    p = tmp_path / "small.png"
    Image.new("RGB", (500, 200), (40, 60, 80)).save(p)     # never enlarged: ~35% of the box
    with pytest.raises(Refused, match="floor"):
        draft(p, SLUG, "garden-photo", infographic="IG-2", root=repo)


def test_a_transparent_infographic_master_has_no_band_against_the_frame(repo, tmp_path):
    p = tmp_path / "ig.png"
    im = Image.new("RGBA", (2000, 1090), (0, 0, 0, 0))
    im.paste((40, 60, 80, 255), (40, 40, 1960, 1050))
    im.save(p)
    r = draft(p, SLUG, "garden-photo", infographic="IG-2", root=repo)
    out = Image.open(r["path"]).convert("RGB")
    bed = reframe_og.gradient()
    for xy in ((50, 30), (1360, 30), (50, 740), (1360, 740), (30, 384)):
        assert max(abs(a - b) for a, b in zip(out.getpixel(xy), bed.getpixel(xy))) <= 3, xy
