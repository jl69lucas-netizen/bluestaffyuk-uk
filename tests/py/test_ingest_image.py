"""scripts/ingest_image.py: folder photos in, generated drafts approved by their exact bytes,
and never a served image replaced (IMAGE-DESIGNS.md §6 and §9, CLAUDE.md rule 11)."""
import datetime
import json
import pathlib
import subprocess
import sys

import pytest
from PIL import Image

from ingest_image import (PICK, Refused, default_stem, draft, file_sha, folder,
                          ingested_manifest_rows, publish, slug_file, stem_problems)

ROOT = pathlib.Path(__file__).resolve().parents[2]
DAY = datetime.date(2026, 9, 24)
SLUG = "uk-locations/blue-staffy-leeds"
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
         "blue-staffy-for-sale-uk.png", "Christa.jpeg"]


def test_default_stem_and_slug_file():
    assert [default_stem(n) for n in NAMES] == ["roman1", "defra-pet-transport-process",
                                                "blue-staffy-for-sale-uk", "christa"]
    assert slug_file(SLUG) == "uk-locations--blue-staffy-leeds"


def test_the_names_match_the_candidates_script():
    """scripts/image_candidates.py decides where the build gate looks for a folder file.
    Skips until that module exists; from then on the two must agree."""
    ic = pytest.importorskip("image_candidates")
    assert [default_stem(n) for n in NAMES] == [ic.asset_stem(n) for n in NAMES]
    assert slug_file(SLUG) == ic.slug_file(SLUG)


def test_the_pick_grammar_matches_the_build_gate():
    rules = pytest.importorskip("image_rules")
    for v in ("file:/images/a.webp", "assets:Roman1.jpg", "og:B", "og:B:0123456789ab",
              "ig:IG-3", "ig:IG-3:0123456789ab", "og:F", "ig:IG-9", "og:B:xyz"):
        assert bool(PICK.match(v)) == (rules.parse_pick(v) is not None), v


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
    assert proc.returncode == 2 and proc.stdout.startswith("REFUSED:"), proc.stdout
    proc = subprocess.run([sys.executable, str(script), "publish", "--board", "no-such-page",
                           "--slot", "x", "--stem", STEM], capture_output=True, text=True)
    assert proc.returncode == 2 and "no board" in proc.stdout, proc.stdout
