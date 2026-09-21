import pathlib, xml.etree.ElementTree as ET
import generate_sitemaps as gs
from generate_sitemaps import shard_for, build_shards

SM = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
VID = "{http://www.google.com/schemas/sitemap-video/1.1}"


def _dist(tmp_path, pages):
    """pages: {url_path: html}. Returns the dist root."""
    d = tmp_path / "dist"
    d.mkdir(parents=True, exist_ok=True)
    for url, body in pages.items():
        target = d if url == "/" else d / url.strip("/")
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(body, encoding="utf-8")
    return d


def _page(title="T", desc="D", body="", robots=None):
    r = '<meta name="robots" content="%s">' % robots if robots else ""
    return ('<html><head><title>%s</title><meta name="description" content="%s">%s</head>'
            '<body>%s</body></html>' % (title, desc, r, body))


def _embed(vid):
    return '<iframe src="https://www.youtube.com/embed/%s"></iframe>' % vid


def test_shard_routing():
    assert shard_for("/", set()) == "page"
    assert shard_for("/uk-locations/", set()) == "page"
    assert shard_for("/uk-locations/blue-staffy-puppies-york/", set()) == "location"
    assert shard_for("/available-puppies/roman/", set()) == "puppy"
    assert shard_for("/available-puppies/", set()) == "page"
    assert shard_for("/blue-staffy-blog-guides/", {"blue-staffy-blog-guides"}) == "post"
    assert shard_for("/blog/", set()) == "page"
    assert shard_for("/thank-you-blue-staffy-puppies-journey/", set()) is None


def test_video_shard_from_embeds(tmp_path):
    d = tmp_path / "dist"; (d / "x").mkdir(parents=True)
    (d / "x/index.html").write_text('<html><head><title>T</title><meta name="description" content="D"></head><body><iframe src="https://www.youtube.com/embed/g9iV9RVr_Sk"></iframe></body></html>', encoding="utf-8")
    (d / "index.html").write_text("<html><head><title>H</title></head><body></body></html>", encoding="utf-8")
    shards = build_shards(d, "https://example.test", blog_slugs={"x"})
    assert [u for u, _ in shards["video"]] == ["https://example.test/x/"]
    assert shards["video"][0][1][0]["id"] == "g9iV9RVr_Sk"


def test_a_nocookie_player_is_the_same_video_as_a_youtube_com_one(tmp_path):
    """`VideoEmbed` (component 18) requests `youtube-nocookie.com`, deliberately, and the
    shard builder matched `youtube.com/embed/` alone — so every page rebuilt with the kit's
    video component left the video sitemap without one gate reporting it. Working rule 14
    keeps an already-ranking id; losing its sitemap row loses the same thing by another
    route. Both hosts are one video, and `player_loc` stays canonical either way."""
    d = _dist(tmp_path, {
        "/": _page(),
        "/nocookie/": _page(title="N", desc="D", body=(
            '<iframe src="https://www.youtube-nocookie.com/embed/g9iV9RVr_Sk"></iframe>')),
        "/plain/": _page(title="P", desc="D", body=_embed("WuA0yo6HZKE")),
    })
    shards = build_shards(d, "https://example.test", set())
    got = {u: [v["id"] for v in vids] for u, vids in shards["video"]}
    assert got == {"https://example.test/nocookie/": ["g9iV9RVr_Sk"],
                   "https://example.test/plain/": ["WuA0yo6HZKE"]}, got
    gs.write(shards, dist=d, base="https://example.test")
    raw = (d / "video-sitemap.xml").read_text(encoding="utf-8")
    # The PLAYER url is the canonical watch host on both, which is what Google expects there
    # and is not the host the page itself asked the browser for.
    assert raw.count("<video:player_loc>https://www.youtube.com/embed/") == 2, raw
    assert "youtube-nocookie" not in raw, raw


def test_the_facade_is_an_embed_and_a_lookalike_host_is_not(tmp_path):
    """`VideoEmbed`'s DEFAULT arrangement ships no `<iframe>` at all until somebody clicks:
    the player url is a `data-src` on the frame and an `<iframe>` inside `<noscript>`. Both
    carry the id, so both count — a page whose video is the light arrangement is still a page
    with a video. And the pattern is LEFT-BOUND, so `notyoutube.com/embed/<id>` is somebody
    else's lookalike host and is not submitted as ours."""
    facade = ('<div data-video-frame data-src="https://www.youtube-nocookie.com/embed/aaaaaaaaaaa?autoplay=1">'
              '<button data-video-play></button>'
              '<noscript><iframe src="https://www.youtube-nocookie.com/embed/aaaaaaaaaaa"></iframe></noscript>'
              '</div>')
    d = _dist(tmp_path, {
        "/": _page(),
        "/facade/": _page(title="F", desc="D", body=facade),
        "/lookalike/": _page(title="L", desc="D", body=(
            '<iframe src="https://notyoutube.com/embed/bbbbbbbbbbb"></iframe>')),
    })
    shards = build_shards(d, "https://example.test", set())
    got = {u: [v["id"] for v in vids] for u, vids in shards["video"]}
    assert got == {"https://example.test/facade/": ["aaaaaaaaaaa"]}, got


def test_noindex_pages_excluded(tmp_path):
    d = tmp_path / "dist"; (d / "n").mkdir(parents=True)
    (d / "n/index.html").write_text('<html><head><meta name="robots" content="noindex, follow"></head><body></body></html>', encoding="utf-8")
    (d / "index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
    shards = build_shards(d, "https://example.test", blog_slugs=set())
    assert all(not u.endswith("/n/") for u, _ in shards["page"])


def test_meta_tolerates_quote_style_and_attribute_order():
    assert "noindex" in gs._meta("<meta name='robots' content='noindex, follow'>", "robots")
    assert "noindex" in gs._meta('<meta content="noindex" name="robots">', "robots")
    assert gs._meta("<meta name='description' content='D'>", "description") == "D"
    assert gs._meta("<html><head></head>", "robots") == ""


def test_blog_slugs_only_read_from_frontmatter(tmp_path, monkeypatch):
    blog = tmp_path / "src/content/blog"; blog.mkdir(parents=True)
    (blog / "a.md").write_text('---\ntitle: A\nslug: real-slug\n---\n\nslug: body-slug\n', encoding="utf-8")
    (blog / "b.md").write_text("no frontmatter here\nslug: nope\n", encoding="utf-8")
    monkeypatch.setattr(gs, "ROOT", tmp_path)
    assert gs.blog_slugs_from_content() == {"real-slug"}


def test_clip_cuts_at_word_boundary_with_ellipsis():
    assert gs._clip("short title", 100) == "short title"
    long = "word " * 40
    out = gs._clip(long, 100)
    assert len(out) <= 100 and out.endswith("…") and not out.endswith(" …")
    assert gs._clip("a  b\nc", 100) == "a b c", "whitespace collapsed"


def test_video_title_and_description_are_capped(tmp_path):
    title = "Blue Staffy " * 30
    desc = "d" * 3000
    d = _dist(tmp_path, {"/": _page(), "/v/": _page(title=title, desc=desc, body=_embed("abcdef1234"))})
    v = build_shards(d, "https://example.test", set())["video"][0][1][0]
    assert len(v["title"]) <= gs.VIDEO_TITLE_MAX and v["title"].endswith("…")
    assert len(v["description"]) == gs.VIDEO_DESC_MAX


def test_write_emits_well_formed_xml_for_every_shard(tmp_path):
    d = _dist(tmp_path, {
        "/": _page(),
        "/uk-locations/york/": _page(),
        "/available-puppies/roman/": _page(),
        "/a-post/": _page(body=_embed("abcdef1234")),
    })
    shards = build_shards(d, "https://example.test", {"a-post"})
    written = gs.write(shards, dist=d, base="https://example.test")
    assert written == ["page-sitemap.xml", "post-sitemap.xml", "location-sitemap.xml",
                       "puppy-sitemap.xml", "video-sitemap.xml"]
    for fn in written + ["sitemap_index.xml"]:
        ET.parse(d / fn)
    locs = [e.text for e in ET.parse(d / "sitemap_index.xml").getroot().iter(SM + "loc")]
    assert locs == ["https://example.test/%s" % fn for fn in written]


def test_video_sitemap_namespace_and_required_children(tmp_path):
    d = _dist(tmp_path, {"/": _page(), "/v/": _page(title="Watch", desc="Desc", body=_embed("g9iV9RVr_Sk"))})
    shards = build_shards(d, "https://example.test", set())
    gs.write(shards, dist=d, base="https://example.test")
    raw = (d / "video-sitemap.xml").read_text(encoding="utf-8")
    assert 'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1"' in raw
    video = ET.parse(d / "video-sitemap.xml").getroot().find(SM + "url").find(VID + "video")
    assert video is not None
    assert video.findtext(VID + "thumbnail_loc") == "https://i.ytimg.com/vi/g9iV9RVr_Sk/hqdefault.jpg"
    assert video.findtext(VID + "title") == "Watch"
    assert video.findtext(VID + "description") == "Desc"
    assert video.findtext(VID + "player_loc") == "https://www.youtube.com/embed/g9iV9RVr_Sk"


def test_empty_shards_are_skipped_and_absent_from_index(tmp_path):
    d = _dist(tmp_path, {"/": _page()})
    written = gs.write(build_shards(d, "https://example.test", set()), dist=d, base="https://example.test")
    assert written == ["page-sitemap.xml"]
    for fn in ("post-sitemap.xml", "location-sitemap.xml", "puppy-sitemap.xml", "video-sitemap.xml"):
        assert not (d / fn).exists()
    assert fn not in (d / "sitemap_index.xml").read_text(encoding="utf-8")


def test_special_characters_are_escaped(tmp_path):
    d = _dist(tmp_path, {"/": _page(), "/v/": _page(title="Tom &amp; Jerry&#39;s", body=_embed("abcdef1234"))})
    gs.write(build_shards(d, "https://example.test", set()), dist=d, base="https://example.test")
    raw = (d / "video-sitemap.xml").read_text(encoding="utf-8")
    assert "&amp;" in raw and "Tom & Jerry" not in raw
    video = ET.parse(d / "video-sitemap.xml").getroot().find(SM + "url").find(VID + "video")
    assert video.findtext(VID + "title") == "Tom & Jerry's"


def test_robots_rewrite_is_idempotent_and_collapses_duplicates(tmp_path):
    d = _dist(tmp_path, {"/": _page()})
    (d / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://old.test/sitemap_index.xml\n"
        "Sitemap: https://older.test/sitemap.xml\n", encoding="utf-8")
    shards = build_shards(d, "https://example.test", set())
    gs.write(shards, dist=d, base="https://example.test")
    first = (d / "robots.txt").read_text(encoding="utf-8")
    gs.write(shards, dist=d, base="https://example.test")
    assert (d / "robots.txt").read_text(encoding="utf-8") == first
    assert first.count("Sitemap:") == 1
    assert "Sitemap: https://example.test/sitemap_index.xml" in first
    assert "Allow: /" in first


def test_write_does_not_touch_tracked_public_robots(tmp_path):
    public = pathlib.Path(gs.__file__).resolve().parents[1] / "public/robots.txt"
    before = public.read_text(encoding="utf-8")
    d = _dist(tmp_path, {"/": _page()})
    gs.write(build_shards(d, "https://example.test", set()), dist=d, base="https://example.test")
    assert public.read_text(encoding="utf-8") == before
