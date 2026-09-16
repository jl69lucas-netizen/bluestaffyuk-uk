import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_headers_file_has_security_headers():
    text = (ROOT / "public/_headers").read_text(encoding="utf-8")
    for h in ("X-Frame-Options: DENY", "X-Content-Type-Options: nosniff",
              "Referrer-Policy: strict-origin-when-cross-origin",
              "Permissions-Policy: camera=(), microphone=(), geolocation=()"):
        assert h in text, h


def test_robots_allows_all_and_points_at_sitemap_index():
    text = (ROOT / "public/robots.txt").read_text(encoding="utf-8")
    assert "Allow: /" in text
    assert re.search(r"(?m)^Sitemap: \S+/sitemap_index\.xml$", text), text


def test_404_is_noindexed_and_links_home():
    text = (ROOT / "public/404.html").read_text(encoding="utf-8")
    assert "noindex" in text
    for href in ('href="/"', 'href="/buy-blue-staffy-puppies-uk/"', 'href="/uk-locations/"'):
        assert href in text, href
    assert "PHONE_PLACEHOLDER" not in text
    assert not re.search(r"tel:|\b0\d{3}[\s-]?\d{3}[\s-]?\d{4}\b", text)
