import pathlib
import pytest
from PIL import Image
import extract_images
from extract_images import rewrite_image_srcs, rewrite_schema_urls, stem_for, set_manifest
from bake_images import (bake_body_image, bake_puppy_card, referenced_stems, referenced_videos,
                         MAX_KB)

LITTER = "blue-staffy-puppies-uk-litter1"


@pytest.fixture(autouse=True)
def _clean_manifest():
    """Every test states the manifest it wants; none inherit the repo's real one."""
    set_manifest({})
    yield
    extract_images._MANIFEST = None


def _noisy(size, blur=1, seed=7):
    """Blurred noise compresses roughly like a detailed photograph: busts the budget at
    full resolution, fits once stepped down."""
    import random
    from PIL import ImageFilter
    random.seed(seed)
    im = Image.new("RGB", size)
    im.putdata([(random.randrange(256),) * 3 for _ in range(size[0] * size[1])])
    return im.filter(ImageFilter.GaussianBlur(blur))


def test_rewrite_srcs_points_to_images_webp():
    set_manifest({LITTER: {"w": 1408, "h": 768, "sib_w": 760}})
    html = '<img src="/wp-content/uploads/%s.jpg" srcset="/wp-content/uploads/x.jpg 780w" sizes="(max-width:480px) 150px" alt="a" width="576" height="350">' % LITTER
    out = rewrite_image_srcs(html)
    assert 'src="/images/%s.webp"' % LITTER in out
    assert 'srcset="/images/%s-760.webp 760w, /images/%s.webp 1408w"' % (LITTER, LITTER) in out
    assert "wp-content" not in out and 'loading="lazy"' in out and 'alt="a"' in out
    assert 'width="1408"' in out and 'height="768"' in out     # WP's guesses overwritten


def test_rewrite_srcs_uses_measured_widths_not_guesses():
    set_manifest({LITTER: {"w": 1046, "h": 1036, "sib_w": 760}})
    out = rewrite_image_srcs('<img src="/wp-content/uploads/%s.jpg" alt="a">' % LITTER)
    assert 'srcset="/images/%s-760.webp 760w, /images/%s.webp 1046w"' % (LITTER, LITTER) in out
    assert "1408w" not in out
    assert 'width="1046"' in out and 'height="1036"' in out


def test_rewrite_srcs_single_candidate_when_no_sibling_was_baked():
    set_manifest({"small": {"w": 600, "h": 300, "sib_w": None}})
    out = rewrite_image_srcs('<img src="/wp-content/uploads/small.png" alt="a">')
    assert 'srcset="/images/small.webp 600w"' in out
    assert "-760.webp" not in out


def test_rewrite_srcs_never_guesses_without_a_manifest_entry():
    out = rewrite_image_srcs('<img src="/wp-content/uploads/unbaked.jpg" alt="a" width="576" height="350">')
    assert 'src="/images/unbaked.webp"' in out
    assert "srcset" not in out and "sizes" not in out
    assert "width=" not in out and "height=" not in out


def test_rewrite_is_idempotent():
    set_manifest({LITTER: {"w": 1046, "h": 1036, "sib_w": 760}})
    html = '<img src="/wp-content/uploads/%s.jpg" alt="a" width="576">' % LITTER
    once = rewrite_image_srcs(html)
    assert rewrite_image_srcs(once) == once


def test_rewrite_rewrites_lightbox_anchor_href():
    html = '<a href="/wp-content/uploads/foo.jpg"><img src="/wp-content/uploads/foo.jpg" alt="f"></a>'
    out = rewrite_image_srcs(html)
    assert 'href="/images/foo.webp"' in out
    assert "wp-content" not in out


def test_rewrite_rewrites_logo_anchor_to_png():
    html = '<a href="/wp-content/uploads/cropped-blue-staffy-uk-official-logo0.png"><img src="/wp-content/uploads/cropped-blue-staffy-uk-official-logo0.png" alt="logo"></a>'
    out = rewrite_image_srcs(html)
    assert 'href="/images/cropped-blue-staffy-uk-official-logo0.png"' in out
    assert 'src="/images/cropped-blue-staffy-uk-official-logo0.png"' in out
    assert "srcset" not in out


def test_rewrite_video_poster_and_src():
    html = ('<video controls="" poster="/wp-content/uploads/%s.jpg" '
            'src="/wp-content/uploads/best-blue-staffy-puppies-uk.mp4"></video>' % LITTER)
    out = rewrite_image_srcs(html)
    assert 'poster="/images/%s.webp"' % LITTER in out
    assert 'src="/videos/best-blue-staffy-puppies-uk.mp4"' in out
    assert "wp-content" not in out


def test_rewrite_is_noop_without_uploads():
    html = "<p>x</p><img src=\"/images/already.webp\" alt=\"y\">"
    assert rewrite_image_srcs(html) == html


def test_stem_for_strips_wp_size_suffix():
    assert stem_for("/wp-content/uploads/foo-768x776.png") == "foo"
    assert stem_for("/wp-content/uploads/cropped-blue-staffy-uk-official-logo0.png") == "cropped-blue-staffy-uk-official-logo0"
    assert stem_for("/wp-content/uploads/a.jpg?ver=3") == "a"


def test_referenced_stems_matches_uppercase_and_sibling_forms(tmp_path):
    f = tmp_path / "page.astro"
    f.write_text('"/images/Roman2.webp" "/images/blue-staffy-UK.webp" '
                 '"/images/litter1-760.webp" "/images/logo0.png"', encoding="utf-8")
    assert referenced_stems([f]) == ["Roman2", "blue-staffy-UK", "litter1", "logo0"]


def test_referenced_videos_finds_mp4s(tmp_path):
    f = tmp_path / "page.astro"
    f.write_text('"/videos/Best-Blue-Staffy.mp4" "/videos/a.webm"', encoding="utf-8")
    assert referenced_videos([f]) == ["Best-Blue-Staffy.mp4", "a.webm"]


def test_rewrite_schema_urls_rewrites_nested_image_and_video_urls():
    schema = [{"@type": "ImageObject", "url": "/wp-content/uploads/blue-staffy-health-uk.jpg"},
              {"@type": "Organization",
               "logo": {"url": "https://bluestaffyuk.uk/wp-content/uploads/blue-staffy-uk-official-logo0.png"}},
              {"@type": "VideoObject",
               "contentUrl": "/wp-content/uploads/best-blue-staffy-puppies-uk.mp4",
               "thumbnailUrl": "/wp-content/uploads/%s-768x761.jpg" % LITTER}]
    out = rewrite_schema_urls(schema)
    assert out[0]["url"] == "/images/blue-staffy-health-uk.webp"
    assert out[1]["logo"]["url"] == "/images/blue-staffy-uk-official-logo0.png"  # logo stays PNG
    assert out[2]["contentUrl"] == "/videos/best-blue-staffy-puppies-uk.mp4"
    assert out[2]["thumbnailUrl"] == "/images/%s.webp" % LITTER


def test_rewrite_schema_urls_leaves_clean_schema_alone():
    schema = [{"@type": "WebPage", "url": "/blue-staffy-health-uk/", "name": "x", "n": 3}]
    assert rewrite_schema_urls(schema) == schema


def test_bake_body_image_under_budget(tmp_path):
    src = tmp_path / "big.jpg"; Image.new("RGB", (3000, 2000), (40, 80, 120)).save(src, quality=95)
    full, sib, dims = bake_body_image(src, tmp_path / "out", "big")
    assert Image.open(full).size == (1408, 768) and Image.open(sib).size == (760, 415)
    assert full.stat().st_size <= MAX_KB * 1024
    assert dims == {"w": 1408, "h": 768, "sib_w": 760}


def test_bake_small_image_not_upscaled_and_writes_no_sibling(tmp_path):
    src = tmp_path / "small.png"; Image.new("RGB", (600, 300), (10, 10, 10)).save(src)
    full, sib, dims = bake_body_image(src, tmp_path / "out", "small")
    assert Image.open(full).size == (600, 300)
    assert sib is None and dims == {"w": 600, "h": 300, "sib_w": None}
    # A 760 sibling of a 600px image would be a byte-identical duplicate.
    assert not (tmp_path / "out" / "small-760.webp").exists()


def test_bake_removes_a_stale_sibling(tmp_path):
    out = tmp_path / "out"; out.mkdir()
    stale = out / "small-760.webp"; stale.write_bytes(b"stale")
    src = tmp_path / "small.png"; Image.new("RGB", (600, 300), (10, 10, 10)).save(src)
    bake_body_image(src, out, "small")
    assert not stale.exists()


def test_bake_steps_resolution_down_when_quality_walk_cannot_hit_budget(tmp_path):
    src = tmp_path / "noise.png"; _noisy((1080, 1080)).save(src)
    full, sib, dims = bake_body_image(src, tmp_path / "out", "noise")
    assert full.stat().st_size <= MAX_KB * 1024
    assert sib is not None and sib.stat().st_size <= MAX_KB * 1024
    assert dims["w"] < 1080                       # could not fit at full resolution


def test_bake_sibling_is_never_wider_than_the_full_image(tmp_path):
    src = tmp_path / "noise.png"; _noisy((1080, 1080)).save(src)
    full, sib, dims = bake_body_image(src, tmp_path / "out", "noise")
    assert sib is not None
    assert Image.open(sib).width <= Image.open(full).width
    assert dims["sib_w"] <= dims["w"]


def test_bake_puppy_card_square_and_portrait(tmp_path):
    src = tmp_path / "pup.jpg"; Image.new("RGB", (1080, 1350), (90, 90, 90)).save(src)
    card, tall = bake_puppy_card(src, tmp_path / "out", "christa")
    assert Image.open(card).size == (800, 800) and Image.open(tall).size == (800, 1000)
    assert card.stat().st_size <= MAX_KB * 1024 and tall.stat().st_size <= MAX_KB * 1024


def test_bake_puppy_card_keeps_geometry_even_when_over_budget(tmp_path, capsys):
    """Pup geometry is a layout contract: warn rather than shrink."""
    src = tmp_path / "pup.png"; _noisy((1200, 1500), blur=0).save(src)
    card, tall = bake_puppy_card(src, tmp_path / "out", "noisy")
    assert Image.open(card).size == (800, 800) and Image.open(tall).size == (800, 1000)
    assert "WARNING over budget" in capsys.readouterr().out


def test_puppy_photos_live_in_src_assets_and_render_with_srcset():
    """Known Issue 4: the puppy photos were only ever available as one baked 800px webp,
    so every card painted at ~240px decoded a 3.3x image. The masters now live in
    src/assets/puppies/ where astro:assets can emit a bounded srcset.

    Deviation from the Task 7 text: the masters were in assets/brand/<slug>/, not in
    public/images/ — public/images only ever held bake_images.py's webp derivatives, which
    stay where they are because the og:image and the Product schema still point at them.
    """
    import json, pathlib, re
    root = pathlib.Path(__file__).resolve().parents[2]
    pups = json.loads((root / "data/puppies.json").read_text())
    for p in pups:
        for f in {p["card_photo"], *p["gallery"]}:
            assert (root / "src/assets/puppies" / f).exists(), f
            assert not (root / "public/images" / f).exists(), f
            assert not (root / "assets/brand" / p["slug"] / f).exists(), f
    built = root / "dist/available-puppies/roman/index.html"
    if not built.exists():
        pytest.skip("run npm run build first")
    html = built.read_text()
    m = (re.search(r'<img[^>]+srcset="([^"]+)"[^>]*alt="Roman', html)
         or re.search(r'<img[^>]+alt="Roman[^"]*"[^>]+srcset="([^"]+)"', html))
    assert m, "Roman's image has no srcset"
    widths = sorted(int(w) for w in re.findall(r"\s(\d+)w", m.group(1)))
    assert widths[-1] / widths[0] <= 3.0 and len(widths) >= 3, widths
