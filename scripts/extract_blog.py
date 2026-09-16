#!/usr/bin/env python3
"""Writer for the migrated blog post: one markdown file per blog page.

The single migrated post is /blue-staffy-blog-guides/. On the old export that URL is a
WordPress *archive* page: its `.entry-content` is an empty wrapper and the two post cards
sit outside it, so parse_page reports word_count 0. Rather than emit an empty post we fall
back to the archive's visible content (see archive_body_html), mark the page
schema_type CollectionPage and flag it "archive-page" / "needs-real-post-body".

Nothing here invents data. The post date comes from JSON-LD, else from the old export's
sitemap <lastmod>, else the `date` key is omitted and "date-not-fetched" recorded.
"""
import json, pathlib, re
from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as md
from extract_wp import CHROME_SELECTORS, clean_content_node, scrub_phone

# Chrome plus the archive-only furniture. The per-card <header class="entry-header">
# is deliberately NOT listed: it holds visible meta that must survive.
ARCHIVE_CHROME = CHROME_SELECTORS + ("footer#colophon", "nav", ".ast-pagination",
                                    ".screen-reader-text")
# Archive furniture pointing at dead WordPress routes.
ARCHIVE_FURNITURE = (".comments-link", ".ast-read-more-container", ".posted-by")
# Author archive and category archive both 301 to /blog/ later, so rewrite them now.
BLOG_HREF_RE = re.compile(r"^(?:https?://[^/]+)?/(?:category|bluestaffyuk-uk)/")
RESPOND_HREF_RE = re.compile(r"#respond$")
SITEMAPS = ("post-sitemap.xml", "page-sitemap.xml")


def faqs_from_body(body_html):
    soup = BeautifulSoup(body_html, "lxml")
    out = []
    for item in soup.select(".uagb-faq-item"):
        q = item.select_one(".uagb-question, .uagb-faq-questions")
        a = item.select_one(".uagb-faq-content")
        if q and a:
            out.append({"question": q.get_text(" ", strip=True),
                        "answer": a.get_text(" ", strip=True)})
    return out


def archive_body_html(raw_soup):
    """Inner HTML of the archive's <main>/#primary, cleaned. Returns (html, links_rewritten).

    `raw_soup` is a BeautifulSoup over the *unmodified* source file; it is mutated.
    Returns ("", 0) when no main region is present.
    """
    node = raw_soup.select_one("main#main") or raw_soup.select_one("main") \
        or raw_soup.select_one("#primary")
    if node is None:
        return "", 0
    for sel in ARCHIVE_CHROME + ARCHIVE_FURNITURE:
        for t in node.select(sel):
            t.decompose()
    for c in node.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    rewritten = 0
    for a in node.find_all("a", href=True):
        if RESPOND_HREF_RE.search(a["href"]):
            a.insert_before(" "); a.insert_after(" ")
            a.unwrap()
            continue
        if BLOG_HREF_RE.match(a["href"]):
            a["href"] = "/blog/"
            rewritten += 1
    for t in node.find_all(True):
        for attr in list(t.attrs):
            if attr.startswith("item") or (attr == "id" and t.get("id", "").startswith("post-")):
                del t[attr]
    clean_content_node(node)
    return node.decode_contents(), rewritten


def _date_from_schema(schema):
    """First datePublished/dateModified in the JSON-LD, or None. Blocks may be lists."""
    for block in schema:
        blocks = block if isinstance(block, list) else [block]
        for b in blocks:
            if not isinstance(b, dict):
                continue
            nodes = b.get("@graph", [b])
            if not isinstance(nodes, list):
                nodes = [nodes]
            for node in nodes:
                if isinstance(node, dict):
                    for k in ("datePublished", "dateModified"):
                        if isinstance(node.get(k), str) and node[k]:
                            return node[k][:10]
    return None


def _date_from_sitemap(url_path, src_root):
    """<lastmod> for url_path in the old export's post/page sitemaps, or None."""
    if not src_root:
        return None
    for name in SITEMAPS:
        f = pathlib.Path(src_root) / name
        if not f.is_file():
            continue
        soup = BeautifulSoup(f.read_text(encoding="utf-8", errors="ignore"), "xml")
        for url in soup.find_all("url"):
            loc, mod = url.find("loc"), url.find("lastmod")
            if loc is None or mod is None:
                continue
            path = re.sub(r"^https?://[^/]+", "", loc.get_text(strip=True))
            if path == url_path and mod.get_text(strip=True):
                return mod.get_text(strip=True)[:10]
    return None


def _src_root(source_path):
    """The export root holding the sitemaps: parent of the page's own directory."""
    if not source_path:
        return None
    return pathlib.Path(source_path).resolve().parent.parent


def _yaml_scalar(v):
    # A JSON string / array / object is valid YAML flow style.
    return json.dumps(v, ensure_ascii=False)


def _bare(v):
    """Plain YAML scalar for values known to be safe (slug, date, fixed author)."""
    return str(v)


def write_blog_post(page, out):
    out = pathlib.Path(out)
    slug = page.url_path.strip("/")
    body_html, flags = page.body_html, list(page.refresh_flags)
    archive = False
    if page.word_count == 0 and page.source_path:
        raw = pathlib.Path(page.source_path).read_text(encoding="utf-8", errors="ignore")
        fallback, rewritten = archive_body_html(BeautifulSoup(raw, "lxml"))
        fallback, _ = scrub_phone(fallback)
        if fallback.strip():
            body_html, archive = fallback, True
            for flag in ("archive-page", "needs-real-post-body"):
                if flag not in flags:
                    flags.append(flag)
            if rewritten and "archive-links-rewritten" not in flags:
                flags.append("archive-links-rewritten")

    soup = BeautifulSoup(body_html, "lxml")
    for faq in soup.select(".wp-block-uagb-faq"):
        faq.decompose()
    img = soup.find("img")          # after the FAQ blocks are gone: never a FAQ icon
    body_md = md(str(soup), heading_style="ATX", strip=["span"])
    # Lines left holding only the WP meta separators once their spans are gone.
    body_md = re.sub(r"(?m)^[ \t]*/[ \t/]*$\n?", "", body_md)
    body_md = re.sub(r"(?m)[ \t]+$", "", body_md)          # trailing space -> empty lines
    body_md = re.sub(r"\n{3,}", "\n\n", body_md)
    # markdownify escapes the underscore; keep the sentinel greppable.
    body_md = body_md.replace("PHONE\\_PLACEHOLDER", "PHONE_PLACEHOLDER")

    fm = [("title", _yaml_scalar(page.title)), ("slug", _bare(slug))]
    date = (_date_from_schema(page.schema)
            or _date_from_sitemap(page.url_path, _src_root(page.source_path)))
    if date:
        fm.append(("date", _bare(date)))
    elif "date-not-fetched" not in flags:
        flags.append("date-not-fetched")
    fm.append(("author", _bare("Blue Staffy UK Team")))
    fm.append(("description", _yaml_scalar(page.description)))
    fm.append(("canonical", _yaml_scalar(page.canonical)))
    if img is not None and img.get("src"):
        fm.append(("featured_image", _yaml_scalar(img["src"])))
        fm.append(("featured_image_alt", _yaml_scalar(img.get("alt", ""))))
    elif "no-featured-image" not in flags:
        flags.append("no-featured-image")
    fm.append(("schema_type", _bare("CollectionPage" if archive else "BlogPosting")))
    fm.append(("faqs", _yaml_scalar(faqs_from_body(body_html))))
    fm.append(("refresh_flags", _yaml_scalar(flags)))

    lines = ["---"] + ["%s: %s" % (k, v) for k, v in fm] + ["---", "", body_md.strip(), ""]
    path = out / "src/content/blog" / ("%s.md" % slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
