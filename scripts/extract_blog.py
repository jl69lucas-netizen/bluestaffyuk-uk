#!/usr/bin/env python3
"""Writer for the migrated blog post: one markdown file per blog page.

The single migrated post is /blue-staffy-blog-guides/. On the old export that URL is a
WordPress *archive* page: its `.entry-content` is an empty wrapper and the two post cards
sit outside it, so parse_page reports word_count 0. Rather than emit an empty post we fall
back to the archive's visible content (see archive_body_html) and flag it "archive-page".
"""
import json, pathlib, re
from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as md

# Site chrome to drop from an archive fallback body. Deliberately narrow: the per-card
# <header class="entry-header"> holds visible meta and must survive.
CHROME_SELECTORS = ("script", "style", "noscript", "link", "header.site-header",
                    "footer.site-footer", "footer#colophon", "nav", "#ast-mobile-header",
                    ".ast-breadcrumbs-wrapper", ".ast-pagination", ".screen-reader-text")


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
    """Inner HTML of the archive's <main>/#primary, minus site chrome.

    `raw_soup` is a BeautifulSoup over the *unmodified* source file; it is mutated.
    Returns "" when no main region is present.
    """
    node = raw_soup.select_one("main#main") or raw_soup.select_one("main") \
        or raw_soup.select_one("#primary")
    if node is None:
        return ""
    for sel in CHROME_SELECTORS:
        for t in node.select(sel):
            t.decompose()
    for c in node.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in node.find_all(True):
        for attr in list(t.attrs):
            if attr.startswith(("data-", "item")) or attr == "style" \
                    or (attr == "id" and t.get("id", "").startswith(("uagb", "post-"))):
                del t[attr]
    return node.decode_contents()


def _date_from_schema(schema):
    for block in schema:
        nodes = block.get("@graph", [block]) if isinstance(block, dict) else []
        for node in nodes:
            for k in ("datePublished", "dateModified"):
                if isinstance(node, dict) and node.get(k):
                    return node[k][:10]
    return "2025-01-01"


def _yaml_scalar(v):
    # A JSON string / array / object is valid YAML flow style.
    return json.dumps(v, ensure_ascii=False)


def _bare(v):
    """Plain YAML scalar for values known to be safe (slug, fixed author)."""
    return str(v)


def write_blog_post(page, out):
    out = pathlib.Path(out)
    slug = page.url_path.strip("/")
    body_html, flags = page.body_html, list(page.refresh_flags)
    if page.word_count == 0 and page.source_path:
        raw = pathlib.Path(page.source_path).read_text(encoding="utf-8", errors="ignore")
        fallback = archive_body_html(BeautifulSoup(raw, "lxml"))
        if fallback.strip():
            body_html = fallback
            if "archive-page" not in flags:
                flags.append("archive-page")
    soup = BeautifulSoup(body_html, "lxml")
    img = soup.find("img")
    for f in soup.select(".wp-block-uagb-faq"):
        f.decompose()
    body_md = md(str(soup), heading_style="ATX", strip=["span"])
    body_md = re.sub(r"\n{3,}", "\n\n", body_md)
    fm = [("title", _yaml_scalar(page.title)),
          ("slug", _bare(slug)),
          ("date", _bare(_date_from_schema(page.schema))),
          ("author", _bare("Blue Staffy UK Team")),
          ("description", _yaml_scalar(page.description)),
          ("canonical", _yaml_scalar(page.canonical)),
          ("featured_image", _yaml_scalar(img.get("src", "") if img else "")),
          ("featured_image_alt", _yaml_scalar(img.get("alt", "") if img else "")),
          ("schema_type", _bare("BlogPosting")),
          ("faqs", _yaml_scalar(faqs_from_body(page.body_html))),
          ("refresh_flags", _yaml_scalar(flags))]
    lines = ["---"] + ["%s: %s" % (k, v) for k, v in fm] + ["---", "", body_md.strip(), ""]
    f = out / "src/content/blog" / ("%s.md" % slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("\n".join(lines), encoding="utf-8")
    return f
