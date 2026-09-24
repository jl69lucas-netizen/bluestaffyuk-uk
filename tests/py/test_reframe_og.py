"""scripts/reframe_og.py keeps the whole dog in the 1408x768 box (IMAGE-DESIGNS.md §7).

Every test runs on a synthetic master: a slate body with a brass band across its top
standing in for the dog's head, so "was the head kept?" is one pixel read.
"""
import pathlib
import subprocess
import sys

import pytest
from PIL import Image, ImageOps

import reframe_og
from reframe_og import BONE_50, blurfill, contain, render, save_webp, subject_box, topcover

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/reframe_og.py"
SLATE = (91, 124, 153)
BRASS = (201, 162, 39)


def near(px, rgb, tol=40):
    return all(abs(a - b) <= tol for a, b in zip(px, rgb))


def portrait(w=400, h=800, head=40):
    im = Image.new("RGB", (w, h), SLATE)
    im.paste(BRASS, (0, 0, w, head))
    return im


def test_a_centre_cover_crop_loses_the_head_which_is_why_the_styles_exist():
    naive = ImageOps.fit(portrait(), (1408, 768), Image.LANCZOS, centering=(0.5, 0.5))
    assert not near(naive.getpixel((704, 5)), BRASS)


def test_style_a_contain_keeps_the_whole_dog_on_a_bone_bed():
    out = contain(portrait())
    assert out.size == (1408, 768)
    assert near(out.getpixel((10, 5)), BONE_50, tol=4), "the bed is the bone gradient"
    top = (768 - int(768 * 0.90)) // 2
    assert near(out.getpixel((704, top + 5)), BRASS), "the head is in frame"
    assert near(out.getpixel((704, 700)), SLATE), "and so is the body"


def test_style_b_blurfill_keeps_the_whole_dog_full_height():
    out = blurfill(portrait())
    assert out.size == (1408, 768)
    assert near(out.getpixel((704, 5)), BRASS), "head at the top of the frame"
    assert near(out.getpixel((704, 760)), SLATE), "body to the bottom of the frame"


def test_style_e_topcover_fills_the_box_and_never_cuts_the_head():
    out = topcover(portrait())
    assert out.size == (1408, 768)
    assert near(out.getpixel((704, 10)), BRASS)
    assert near(out.getpixel((0, 400)), SLATE) and near(out.getpixel((1407, 400)), SLATE)


def test_mobcrop_4_5_keeps_the_sharp_dog_inside_the_central_mobile_strip():
    assert subject_box(1408, 768, "4:5") == (614, 768)
    wide = Image.new("RGB", (1600, 800), SLATE)
    wide.paste(BRASS, (0, 0, 20, 800))                # a marker on the master's left edge
    out = render(wide, "blurfill", mobcrop="4:5")
    left = (1408 - 614) // 2
    assert near(out.getpixel((left + 3, 384)), BRASS), "sharp left edge starts the 4:5 strip"
    assert not near(out.getpixel((left - 10, 384)), BRASS), "nothing sharp outside it"
    full = render(wide, "blurfill")
    assert near(full.getpixel((3, 384)), BRASS), "without --mobcrop it spans the box"


def test_the_quality_walk_stops_at_the_first_quality_under_budget(tmp_path):
    kb, q, ok = save_webp(portrait(), tmp_path / "flat.webp", 95)
    assert q == 82 and kb < 95 and ok
    noise = Image.frombytes("RGB", (1408, 768), bytes(range(256)) * (1408 * 768 * 3 // 256))
    kb, q, ok = save_webp(noise, tmp_path / "busy.webp", 1)
    assert q == 60, "the walk has a floor and still writes the file"
    assert not ok, "and says the budget was missed"
    assert (tmp_path / "busy.webp").exists()


def test_cli_writes_1408x768_and_a_760_sibling_under_55_kb(tmp_path):
    src = tmp_path / "master.png"
    portrait(591, 640, 60).save(src)
    out, sib = tmp_path / "puppy.webp", tmp_path / "puppy-760.webp"
    proc = subprocess.run([sys.executable, str(SCRIPT), str(src), str(out), "--style",
                           "blurfill", "--mobcrop", "4:5", "--sib", str(sib)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert Image.open(out).size == (1408, 768)
    assert out.stat().st_size < 95 * 1024
    assert Image.open(sib).size == (760, 415)
    assert sib.stat().st_size < 55 * 1024


def test_cli_refuses_an_unknown_style(tmp_path):
    src = tmp_path / "m.png"
    portrait().save(src)
    proc = subprocess.run([sys.executable, str(SCRIPT), str(src), str(tmp_path / "o.webp"),
                           "--style", "framed"], capture_output=True, text=True)
    assert proc.returncode == 2 and "invalid choice" in proc.stderr


def test_the_engine_names_exactly_the_baked_styles_of_image_designs():
    from image_designs import load
    doc = (ROOT / "IMAGE-DESIGNS.md").read_text(encoding="utf-8")
    for style in reframe_og.STYLES:
        assert "`--style %s`" % style in doc, style
    assert set(load()["og_styles"]) >= {"A", "B", "E"}


# ── review fixes: budget, alpha, mobcrop, odd inputs ─────────────────────────────────────
def noisy(w=1600, h=900, seed=0):
    import random
    return Image.frombytes("RGB", (w, h), random.Random(seed).randbytes(w * h * 3))


def test_cli_refuses_a_master_that_cannot_meet_the_budget(tmp_path):
    src, out = tmp_path / "noise.png", tmp_path / "noise.webp"
    noisy().save(src)
    proc = subprocess.run([sys.executable, str(SCRIPT), str(src), str(out), "--style", "contain"],
                          capture_output=True, text=True)
    assert proc.returncode == 2, proc.stderr
    assert "KB" in proc.stderr and "95" in proc.stderr
    assert not out.exists(), "an over-budget file is not left behind"


def test_a_transparent_corner_comes_out_bone_not_black(tmp_path):
    im = Image.new("RGBA", (400, 800), SLATE + (255,))
    im.paste((0, 0, 0, 0), (0, 0, 60, 60))
    p = tmp_path / "alpha.png"
    im.save(p)
    loaded = reframe_og.load(p)
    assert loaded.mode == "RGB"
    assert near(loaded.getpixel((5, 5)), BONE_50, tol=2)
    assert near(loaded.getpixel((200, 400)), SLATE, tol=2)


def test_a_palette_image_with_transparency_is_flattened_on_bone(tmp_path):
    im = Image.new("P", (40, 40), 1)
    im.putpalette([0, 0, 0] + list(SLATE) + [0] * (254 * 3))
    im.paste(0, (0, 0, 10, 10))
    im.info["transparency"] = 0
    p = tmp_path / "pal.png"
    im.save(p, transparency=0)
    assert near(reframe_og.load(p).getpixel((2, 2)), BONE_50, tol=2)


def test_an_animated_master_is_refused(tmp_path):
    p = tmp_path / "anim.png"
    a, b = Image.new("RGB", (40, 40), SLATE), Image.new("RGB", (40, 40), BRASS)
    a.save(p, save_all=True, append_images=[b])
    with pytest.raises(ValueError, match="animated"):
        reframe_og.load(p)


@pytest.mark.parametrize("bad", ["4:0", "0:5", "4x5", "4:5:1", "-4:5", "a:b"])
def test_a_malformed_mobcrop_is_refused(tmp_path, bad):
    with pytest.raises(ValueError, match="mobcrop"):
        subject_box(1408, 768, bad)
    src = tmp_path / "m.png"
    portrait().save(src)
    proc = subprocess.run([sys.executable, str(SCRIPT), str(src), str(tmp_path / "o.webp"),
                           "--mobcrop", bad], capture_output=True, text=True)
    assert proc.returncode == 2 and "mobcrop" in proc.stderr


def test_mobcrop_with_another_style_warns(tmp_path):
    src = tmp_path / "m.png"
    portrait().save(src)
    proc = subprocess.run([sys.executable, str(SCRIPT), str(src), str(tmp_path / "o.webp"),
                           "--style", "topcover", "--mobcrop", "4:5"], capture_output=True, text=True)
    assert proc.returncode == 0 and "warning" in proc.stderr.lower()
