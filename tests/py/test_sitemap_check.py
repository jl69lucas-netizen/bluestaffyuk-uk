import pytest

from sitemap_check import audit, main

BASE = "https://x.test"


def _w(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _urlset(*paths):
    urls = "".join("<url><loc>%s%s</loc></url>" % (BASE, p) for p in paths)
    return "<urlset>%s</urlset>" % urls


def _index(*files):
    body = "".join("<sitemap><loc>%s/%s</loc></sitemap>" % (BASE, f) for f in files)
    return "<sitemapindex>%s</sitemapindex>" % body


def _robots(target="%s/sitemap_index.xml" % BASE):
    return "User-agent: *\nAllow: /\nSitemap: %s\n" % target


def _clean(d, extra_pages=(), shards=None, robots=None):
    """A consistent tmp dist: every built page indexable and in exactly one shard."""
    _w(d / "index.html", "<html></html>")
    for p in extra_pages:
        _w(d / p.strip("/") / "index.html", "<html></html>")
    shards = shards or {"page-sitemap.xml": ["/"] + [p for p in extra_pages]}
    for name, paths in shards.items():
        _w(d / name, _urlset(*paths))
    _w(d / "sitemap_index.xml", _index(*sorted(shards)))
    _w(d / "robots.txt", robots or _robots())


def test_audit(tmp_path):
    d = tmp_path
    (d / "a").mkdir()
    (d / "a/index.html").write_text("<html></html>", encoding="utf-8")
    (d / "index.html").write_text("<html></html>", encoding="utf-8")
    (d / "b").mkdir()
    (d / "b/index.html").write_text(
        '<html><head><meta name="robots" content="noindex, follow"></head></html>',
        encoding="utf-8")
    (d / "page-sitemap.xml").write_text(
        '<urlset><url><loc>https://x.test/</loc></url>'
        '<url><loc>https://x.test/a/</loc></url>'
        '<url><loc>https://x.test/b/</loc></url>'
        '<url><loc>https://x.test/ghost/</loc></url></urlset>', encoding="utf-8")
    (d / "post-sitemap.xml").write_text(
        '<urlset><url><loc>https://x.test/a/</loc></url></urlset>', encoding="utf-8")
    (d / "sitemap_index.xml").write_text(
        '<sitemapindex><sitemap><loc>https://x.test/page-sitemap.xml</loc></sitemap>'
        '<sitemap><loc>https://x.test/post-sitemap.xml</loc></sitemap>'
        '<sitemap><loc>https://x.test/missing-sitemap.xml</loc></sitemap></sitemapindex>',
        encoding="utf-8")
    (d / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://x.test/sitemap_index.xml\n",
        encoding="utf-8")

    probs = audit(d, BASE)
    j = " ".join(probs)
    assert "/a/ in 2 shards" in j
    assert "/b/ is noindex but listed" in j
    assert "/ghost/ not built" in j
    assert "missing-sitemap.xml listed in index but missing" in j


def test_audit_clean(tmp_path):
    _clean(tmp_path, extra_pages=["/a/", "/blog/post-one/"])
    assert audit(tmp_path, BASE) == []


def test_video_shard_is_supplementary(tmp_path):
    _clean(tmp_path, extra_pages=["/v/"], shards={
        "page-sitemap.xml": ["/", "/v/"],
        "video-sitemap.xml": ["/v/"],
    })
    assert audit(tmp_path, BASE) == []


def test_robots_sitemap_line_must_match_index(tmp_path):
    _clean(tmp_path, robots=_robots("https://other.test/sitemap_index.xml"))
    probs = audit(tmp_path, BASE)
    assert len(probs) == 1 and "robots.txt" in probs[0]


def test_missing_page_in_no_shard(tmp_path):
    _clean(tmp_path, extra_pages=["/orphan/"], shards={"page-sitemap.xml": ["/"]})
    assert any("/orphan/" in p and "no shard" in p for p in audit(tmp_path, BASE))


def test_duplicate_within_one_shard(tmp_path):
    _clean(tmp_path, extra_pages=["/a/"], shards={"page-sitemap.xml": ["/", "/a/", "/a/"]})
    assert any("twice" in p for p in audit(tmp_path, BASE))


def test_loc_outside_base(tmp_path):
    _clean(tmp_path)
    (tmp_path / "page-sitemap.xml").write_text(
        "<urlset><url><loc>https://x.test/</loc></url>"
        "<url><loc>https://elsewhere.test/a/</loc></url></urlset>", encoding="utf-8")
    assert any("elsewhere.test" in p for p in audit(tmp_path, BASE))


def test_malformed_shard_xml(tmp_path):
    _clean(tmp_path)
    (tmp_path / "page-sitemap.xml").write_text("<urlset><url>", encoding="utf-8")
    assert any("unparseable" in p for p in audit(tmp_path, BASE))


def test_shard_not_listed_in_index(tmp_path):
    _clean(tmp_path, extra_pages=["/a/"])
    (tmp_path / "post-sitemap.xml").write_text(_urlset("/a/"), encoding="utf-8")
    assert any("not listed in the index" in p for p in audit(tmp_path, BASE))


def test_main_fails_without_dist(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main(root=tmp_path / "root", dist=tmp_path / "nodist")
    assert exc.value.code == 1
    assert "npm run build && npm run sitemaps" in capsys.readouterr().out


def test_main_end_to_end(tmp_path, capsys):
    root, dist = tmp_path / "root", tmp_path / "dist"
    dist.mkdir()
    _clean(dist, extra_pages=["/a/"])
    main(root=root, dist=dist, base=BASE)
    out = capsys.readouterr().out
    assert "examined 2 built pages, 1 shards, 2 sitemap urls; 0 problems" in out
    assert (root / "docs" / "reports" / "sitemaps.md").is_file()
