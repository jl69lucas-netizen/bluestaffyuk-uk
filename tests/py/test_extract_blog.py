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
