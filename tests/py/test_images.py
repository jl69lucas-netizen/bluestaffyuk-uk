import pathlib
from PIL import Image
from extract_images import rewrite_image_srcs, rewrite_schema_urls, stem_for
from bake_images import bake_body_image, bake_puppy_card, MAX_KB


def test_rewrite_srcs_points_to_images_webp():
    html = '<img src="/wp-content/uploads/blue-staffy-puppies-uk-litter1.jpg" srcset="/wp-content/uploads/x.jpg 780w" sizes="(max-width:480px) 150px" alt="a" width="576" height="350">'
    out = rewrite_image_srcs(html)
    assert 'src="/images/blue-staffy-puppies-uk-litter1.webp"' in out
    assert 'srcset="/images/blue-staffy-puppies-uk-litter1-760.webp 760w, /images/blue-staffy-puppies-uk-litter1.webp 1408w"' in out
    assert "wp-content" not in out and 'loading="lazy"' in out and 'alt="a"' in out


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
    html = ('<video controls="" poster="/wp-content/uploads/blue-staffy-puppies-uk-litter1.jpg" '
            'src="/wp-content/uploads/best-blue-staffy-puppies-uk.mp4"></video>')
    out = rewrite_image_srcs(html)
    assert 'poster="/images/blue-staffy-puppies-uk-litter1.webp"' in out
    assert 'src="/videos/best-blue-staffy-puppies-uk.mp4"' in out
    assert "wp-content" not in out


def test_rewrite_is_noop_without_uploads():
    html = "<p>x</p><img src=\"/images/already.webp\" alt=\"y\">"
    assert rewrite_image_srcs(html) == html


def test_stem_for_strips_wp_size_suffix():
    assert stem_for("/wp-content/uploads/foo-768x776.png") == "foo"
    assert stem_for("/wp-content/uploads/cropped-blue-staffy-uk-official-logo0.png") == "cropped-blue-staffy-uk-official-logo0"
    assert stem_for("/wp-content/uploads/a.jpg?ver=3") == "a"


def test_rewrite_schema_urls_rewrites_nested_image_and_video_urls():
    schema = [{"@type": "ImageObject", "url": "/wp-content/uploads/blue-staffy-health-uk.jpg"},
              {"@type": "Organization",
               "logo": {"url": "https://bluestaffyuk.uk/wp-content/uploads/blue-staffy-uk-official-logo0.png"}},
              {"@type": "VideoObject",
               "contentUrl": "/wp-content/uploads/best-blue-staffy-puppies-uk.mp4",
               "thumbnailUrl": "/wp-content/uploads/blue-staffy-puppies-uk-litter1-768x761.jpg"}]
    out = rewrite_schema_urls(schema)
    assert out[0]["url"] == "/images/blue-staffy-health-uk.webp"
    assert out[1]["logo"]["url"] == "/images/blue-staffy-uk-official-logo0.png"  # logo stays PNG
    assert out[2]["contentUrl"] == "/videos/best-blue-staffy-puppies-uk.mp4"
    assert out[2]["thumbnailUrl"] == "/images/blue-staffy-puppies-uk-litter1.webp"


def test_rewrite_schema_urls_leaves_clean_schema_alone():
    schema = [{"@type": "WebPage", "url": "/blue-staffy-health-uk/", "name": "x", "n": 3}]
    assert rewrite_schema_urls(schema) == schema


def test_bake_body_image_under_budget(tmp_path):
    src = tmp_path / "big.jpg"; Image.new("RGB", (3000, 2000), (40, 80, 120)).save(src, quality=95)
    full, sib = bake_body_image(src, tmp_path / "out", "big")
    assert Image.open(full).size == (1408, 768) and Image.open(sib).size == (760, 415)
    assert full.stat().st_size <= MAX_KB * 1024


def test_bake_small_image_not_upscaled(tmp_path):
    src = tmp_path / "small.png"; Image.new("RGB", (600, 300), (10, 10, 10)).save(src)
    full, sib = bake_body_image(src, tmp_path / "out", "small")
    assert Image.open(full).size == (600, 300) and Image.open(sib).size == (600, 300)


def test_bake_steps_resolution_down_when_quality_walk_cannot_hit_budget(tmp_path):
    import random
    from PIL import ImageFilter
    random.seed(7)
    src = tmp_path / "noise.png"
    noisy = Image.new("RGB", (1080, 1080))
    noisy.putdata([(random.randrange(256),) * 3 for _ in range(1080 * 1080)])
    # Lightly blurred noise compresses roughly like a detailed photograph: it busts the
    # budget at full resolution but fits once stepped down.
    noisy.filter(ImageFilter.GaussianBlur(1)).save(src)
    full, sib = bake_body_image(src, tmp_path / "out", "noise")
    assert full.stat().st_size <= MAX_KB * 1024
    assert sib.stat().st_size <= MAX_KB * 1024
    assert Image.open(full).width < 1080          # could not fit at full resolution


def test_bake_puppy_card_square_and_portrait(tmp_path):
    src = tmp_path / "pup.jpg"; Image.new("RGB", (1080, 1350), (90, 90, 90)).save(src)
    card, tall = bake_puppy_card(src, tmp_path / "out", "christa")
    assert Image.open(card).size == (800, 800) and Image.open(tall).size == (800, 1000)
