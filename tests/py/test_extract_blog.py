import pathlib

from extract_wp import parse_page
from extract_blog import write_blog_post, faqs_from_body

FIX = pathlib.Path(__file__).parent / "fixtures"


def test_blog_post_markdown(tmp_path):
    page = parse_page(FIX / "blog-guides.html", "/blue-staffy-blog-guides/")
    f = write_blog_post(page, tmp_path)
    assert f == tmp_path / "src/content/blog/blue-staffy-blog-guides.md"
    md = f.read_text(encoding="utf-8")
    assert md.startswith("---\n") and "slug: blue-staffy-blog-guides" in md
    assert 'title: "How To Choose The Right Blue Staffy Puppy' in md
    assert "author: Blue Staffy UK Team" in md
    assert "<script" not in md


def test_archive_fallback_keeps_visible_cards(tmp_path):
    """The old blog index is a WP archive: .entry-content is empty, the two post
    cards sit outside it. The fallback must keep what was visible."""
    page = parse_page(FIX / "blog-guides.html", "/blue-staffy-blog-guides/")
    assert page.word_count == 0            # documents why the fallback exists
    f = write_blog_post(page, tmp_path)
    md = f.read_text(encoding="utf-8")
    body = md.split("---", 2)[2]
    assert "Buy Staffy Puppies for Sale UK" in body
    assert "UK Blue Staffy Puppy Buying Guide" in body
    assert len(body.split()) > 100
    assert "archive-page" in md


def test_faqs_extracted():
    page = parse_page(FIX / "home.html", "/")
    faqs = faqs_from_body(page.body_html)
    assert len(faqs) >= 5 and all(q["question"] and q["answer"] for q in faqs)


ARCHIVE_HTML = """<!doctype html><html><head><title>Synthetic Archive</title>
<meta name="description" content="synthetic"/></head><body>
<header class="site-header">chrome</header>
<div id="primary"><main id="main" class="site-main"><div class="ast-row">
<article id="post-1"><div class="post-content">
<h2 class="entry-title"><a href="/first-post/" rel="bookmark">First Synthetic Post</a></h2>
<header class="entry-header"><div class="entry-meta">
<span class="comments-link"><a href="/first-post/#respond">Leave a Comment</a></span>
/ <span class="ast-taxonomy-container cat-links"><a href="/category/guides/">Guides</a></span>
/ <span class="posted-by"><a href="/bluestaffyuk-uk/iiashymongmail-com/">Blue Staffy UK</a></span>
</div></header>
<div class="ast-excerpt-container"><p>Ring us on +447490571679 about this pup.</p></div>
<p class="ast-read-more-container read-more"><a href="/first-post/">Read More &raquo;</a></p>
<div class="entry-content clear"></div>
</div></article></div></main></div>
<footer class="site-footer">chrome</footer></body></html>
"""


def _synthetic_archive(tmp_path, slug="synthetic-archive", sitemap=None):
    """Write a hermetic WP-archive export under tmp_path and parse it."""
    d = tmp_path / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(ARCHIVE_HTML, encoding="utf-8")
    if sitemap is not None:
        (tmp_path / "post-sitemap.xml").write_text(sitemap, encoding="utf-8")
    return parse_page(d / "index.html", "/%s/" % slug)


SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://bluestaffyuk.uk/synthetic-archive/</loc>
<lastmod>2025-06-11T14:14:05+00:00</lastmod></url>
</urlset>
"""


def test_date_from_sitemap_lastmod(tmp_path):
    page = _synthetic_archive(tmp_path, sitemap=SITEMAP)
    assert not page.schema                      # no JSON-LD: the sitemap is the only source
    md = write_blog_post(page, tmp_path / "out").read_text(encoding="utf-8")
    assert "date: 2025-06-11" in md
    assert "date-not-fetched" not in md


def test_date_omitted_and_flagged_when_unknown(tmp_path):
    page = _synthetic_archive(tmp_path)          # no sitemap written
    md = write_blog_post(page, tmp_path / "out").read_text(encoding="utf-8")
    assert "\ndate:" not in md
    assert "date-not-fetched" in md


def test_archive_schema_type_and_flags(tmp_path):
    page = _synthetic_archive(tmp_path)
    md = write_blog_post(page, tmp_path / "out").read_text(encoding="utf-8")
    assert "schema_type: CollectionPage" in md
    assert "needs-real-post-body" in md and "archive-page" in md
    assert "no-featured-image" in md and "featured_image" not in md


def test_archive_fallback_is_scrubbed_and_relinked(tmp_path):
    page = _synthetic_archive(tmp_path)
    md = write_blog_post(page, tmp_path / "out").read_text(encoding="utf-8")
    assert "PHONE_PLACEHOLDER" in md
    assert "447490" not in md and "7490" not in md
    assert "/category/" not in md and "/bluestaffyuk-uk/" not in md
    assert "#respond" not in md and "Read More" not in md
    assert "archive-links-rewritten" in md
    assert "First Synthetic Post" in md


def test_real_blog_page_schema_type_is_collection(tmp_path):
    page = parse_page(FIX / "blog-guides.html", "/blue-staffy-blog-guides/")
    md = write_blog_post(page, tmp_path).read_text(encoding="utf-8")
    assert "schema_type: CollectionPage" in md
