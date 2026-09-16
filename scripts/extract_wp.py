#!/usr/bin/env python3
"""Extract the old WordPress static export into Astro sources. Verbatim: no rewriting.

Usage: python3 scripts/extract_wp.py [--src /Users/apple/bluestaffyuk-site] [--out .]
"""
import argparse, dataclasses, json, pathlib, re
from bs4 import BeautifulSoup, Comment, Tag

SRC_DEFAULT = pathlib.Path("/Users/apple/bluestaffyuk-site")
ROOT = pathlib.Path(__file__).resolve().parent.parent

RICH_SLUGS = {
    "/", "/buy-blue-staffy-puppies-uk/", "/blue-staffy-pup-sale-uk/",
    "/buy-staffy-puppies-for-sale-uk/", "/uk-blue-staffy-puppy-buying-guide/",
    "/uk-staffordshire-bull-terrier-guide/", "/blue-staffy-health-uk/",
    "/blue-staffy-uk-breeders/", "/uk-blue-staffy-breeders-contact/",
    "/privacy-policy-uk/", "/thank-you-blue-staffy-puppies-journey/",
}
BLOG_SLUGS = {"/blue-staffy-blog-guides/"}
SKIP_PREFIXES = ("/category/", "/form/", "/bluestaffyuk-uk/", "/blog/",
                 "/buy-blue-staffy-puppies-for-sale-uk/", "/healthy-habits-exercises-for-your-pets/")
OLD_PUPS = ("kane", "kobe", "beth", "alis")
OLD_PUP_IMAGES = {
    "blue-staffy-pup-near-me-available.jpg", "blue-staffy-pup-near-me-available-1.jpg",
    "blue-staffy-puppy-uk-sale.jpg", "tan-white-staffy-puppy-uk.jpg", "white-grey-staffy-puppy-uk.jpg",
}
PHONE_RE = re.compile(r"(\+?44\s?7490\s?571\s?679|07490\s?571\s?679|\+447490571679)")
OLD_PRICE_RE = re.compile(r"£\s?(850|1,?000|1,?100|1,?200|300)\b")
DEAD_HREF_RE = re.compile(r"(/wp-json/|/feed/?$|/comments/feed|xmlrpc\.php|/wp-admin/|/wp-login)")
# Two legacy in-body links survive the migration verbatim and would only work through a
# 301. A redirect costs a hop and leaks link equity on every internal click, so the body
# is rewritten at extraction — the one place the change is durable.
LINK_REWRITES = {
    "/buy-blue-staffy-puppies-for-sale-uk/": "/buy-blue-staffy-puppies-uk/",
    "/category/puppy-buying-guide-uk/": "/blog/",
}
OLD_HOST_RE = re.compile(r"^https?://(?:www\.)?bluestaffyuk\.com")


@dataclasses.dataclass
class Page:
    url_path: str
    kind: str
    title: str
    description: str
    canonical: str
    robots: str
    og_type: str
    h1: str
    body_html: str
    schema: list
    word_count: int
    images: list
    embeds: list
    headings: list
    defects: list
    phone_hits: int
    refresh_flags: list
    source_path: str = ""


def classify(url_path: str) -> str:
    if url_path in RICH_SLUGS: return "rich"
    if url_path in BLOG_SLUGS: return "blog"
    if url_path.startswith("/uk-locations/") and url_path != "/uk-locations/": return "location"
    if url_path.startswith(SKIP_PREFIXES): return "skip"
    return "skip"


def _meta(soup, name=None, prop=None):
    tag = soup.find("meta", attrs={"name": name}) if name else soup.find("meta", attrs={"property": prop})
    return tag["content"].strip() if tag and tag.has_attr("content") else ""


# Site chrome dropped before any content extraction. Shared with extract_blog's
# archive fallback, which adds its own archive-only selectors.
CHROME_SELECTORS = ("script", "style", "noscript", "header.site-header", "footer.site-footer",
                    "#ast-mobile-header", ".ast-breadcrumbs-wrapper", "link",
                    "svg.ast-mobile-svg-icon")


def _strip_chrome(soup):
    for sel in CHROME_SELECTORS:
        for t in soup.select(sel): t.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)): c.extract()


def _label_table(tbl):
    """Add stack-table + per-cell data-label, using the first row that has <th>.

    Cells are indexed by position among th/td siblings so row-header tables line up.
    Tables using rowspan/colspan are left unlabelled: the column mapping is unreliable.
    """
    tbl["class"] = (tbl.get("class") or []) + ["stack-table"]
    if tbl.find(lambda x: x.name in ("td", "th") and (x.has_attr("rowspan") or x.has_attr("colspan"))):
        return
    head_row = None
    for tr in tbl.find_all("tr"):
        if tr.find("th"):
            head_row = tr
            break
    if head_row is None:
        return
    if head_row.find("td"):
        # Row-header layout: the header cell lives in each data row, so label from it.
        for tr in tbl.find_all("tr"):
            row_head = tr.find("th")
            if row_head is None:
                continue
            label = row_head.get_text(" ", strip=True)
            for cell in tr.find_all("td"):
                cell["data-label"] = label
        return
    heads = [c.get_text(" ", strip=True) for c in head_row.find_all(["th", "td"])]
    for tr in tbl.find_all("tr"):
        if tr is head_row:
            continue
        for i, cell in enumerate(tr.find_all(["th", "td"])):
            if cell.name == "td" and i < len(heads):
                cell["data-label"] = heads[i]


FORM_WRAPPERS = ".wpforms-container, .wpcf7, .forminator-ui, .wp-block-uagb-forms"


def rewrite_legacy_href(href):
    """The rewritten href for a legacy path, or None. Fragments are preserved.

    The old host is stripped first so an absolute legacy link is matched too; the path
    must match a LINK_REWRITES key exactly, since a prefix match would catch unrelated
    deeper paths.
    """
    path = OLD_HOST_RE.sub("", href.strip())
    path, sep, fragment = path.partition("#")
    dest = LINK_REWRITES.get(path)
    return None if dest is None else dest + sep + fragment


def clean_content_node(node):
    """Clean one content node in place; returns (node, forms_removed, links_rewritten).

    Shared by extract_body and extract_blog.archive_body_html so both paths get the
    same treatment: dead forms dropped, dead hrefs unwrapped with spacing preserved,
    inline styles and WP data-*/uagb ids stripped, tables labelled and wrapped.

    Every <form> is a dead WordPress endpoint on this export (the enquiry form still
    lists the sold pups), so forms and their plugin wrappers are dropped outright.
    """
    forms_removed = 0
    for t in node.select(FORM_WRAPPERS):
        if t.parent is None:
            continue
        forms_removed += len(t.find_all("form")) or 1
        t.decompose()
    for form in node.find_all("form"):
        if form.parent is None:
            continue
        forms_removed += 1
        form.decompose()
    links_rewritten = 0
    for a in node.find_all("a", href=True):
        if DEAD_HREF_RE.search(a["href"]):
            a.insert_before(" "); a.insert_after(" ")
            a.unwrap()
            continue
        dest = rewrite_legacy_href(a["href"])
        if dest is not None:
            a["href"] = dest
            links_rewritten += 1
    for t in node.select("[style]"):
        if t.name in ("p", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6"): del t["style"]
    for t in node.find_all(True):
        for attr in list(t.attrs):
            if attr.startswith("data-") or (attr == "id" and t.get("id", "").startswith("uagb")):
                del t[attr]
    for tbl in node.find_all("table"):
        _label_table(tbl)
        tbl.wrap(Tag(name="div", attrs={"class": "table-wrap"}))
    return node, forms_removed, links_rewritten


def extract_body(soup):
    """Return (node mutated in place, forms_removed, links_rewritten)."""
    node = soup.select_one(".entry-content") or soup.select_one("#primary") or soup.body
    return clean_content_node(node)


def scrub_phone(text: str):
    n = len(PHONE_RE.findall(text))
    return PHONE_RE.sub("PHONE_PLACEHOLDER", text), n


def drop_placeholder_telephones(node):
    """Strip telephone keys whose value is (or contains) the phone placeholder.

    The migrated Rank Math @graph is carried through verbatim, so the scrubbed
    "telephone": "PHONE_PLACEHOLDER" would otherwise ship in public JSON-LD. The real
    number was already counted by scrub_phone before json.loads, so removing the dead
    key here leaves phone_hits unchanged. Returns (cleaned node, keys removed).
    """
    removed = 0
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k == "telephone" and isinstance(v, str) and "PHONE_PLACEHOLDER" in v:
                removed += 1
                continue
            out[k], n = drop_placeholder_telephones(v)
            removed += n
        return out, removed
    if isinstance(node, list):
        out = []
        for v in node:
            cleaned, n = drop_placeholder_telephones(v)
            out.append(cleaned)
            removed += n
        return out, removed
    return node, 0


def parse_page(path: pathlib.Path, url_path: str) -> Page:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "lxml")
    defects, flags = [], []
    schema, schema_phone_hits = [], 0
    for s in soup.find_all("script", type="application/ld+json"):
        raw_json, n = scrub_phone(s.get_text() or "{}")
        schema_phone_hits += n
        try:
            block, _ = drop_placeholder_telephones(json.loads(raw_json))
            schema.append(block)
        except json.JSONDecodeError:
            defects.append("bad-ld-json")
    title = (soup.title.string or "").strip() if soup.title else ""
    description = _meta(soup, name="description")
    canon = soup.find("link", rel="canonical")
    canonical = re.sub(r"^https?://[^/]+", "", canon["href"]) if canon else url_path
    canonical = canonical or "/"
    robots = _meta(soup, name="robots")
    og_type = _meta(soup, prop="og:type")
    _strip_chrome(soup)
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(" ", strip=True) if h1_tag else ""
    node, forms_removed, links_rewritten = extract_body(soup)
    if forms_removed:
        flags.append("wp-form-removed")
    if links_rewritten:
        flags.append("legacy-links-rewritten:%d" % links_rewritten)
    body_html, phone_hits = scrub_phone(node.decode_contents())
    title, n1 = scrub_phone(title); description, n2 = scrub_phone(description)
    phone_hits += n1 + n2 + schema_phone_hits
    b = BeautifulSoup(body_html, "lxml")
    text = b.get_text(" ", strip=True)
    word_count = len(text.split())
    images = [{"src": i.get("src", ""), "alt": i.get("alt", "")} for i in b.find_all("img")]
    embeds = [f.get("src", "") for f in b.find_all("iframe")]
    headings = [(t.name, t.get_text(" ", strip=True)) for t in b.find_all(re.compile("^h[1-6]$"))]
    if not h1: defects.append("empty-h1")
    if word_count < 50: defects.append("stub")
    if re.search(r"\b\d+ (Sweet )?Blue Staffy Pupp", title): flags.append("count-in-title")
    for m in OLD_PRICE_RE.finditer(text): flags.append("old-price:%s" % m.group(0))
    return Page(url_path, classify(url_path), title, description, canonical, robots, og_type, h1,
                body_html, schema, word_count, images, embeds, headings, defects, phone_hits, flags,
                str(path))


def inventory(src: pathlib.Path):
    for f in sorted(src.rglob("index.html")):
        rel = f.parent.relative_to(src).as_posix()
        url_path = "/" if rel == "." else "/%s/" % rel
        if rel.startswith(("wp-content", "wp-includes", "admin", ".git")): continue
        yield url_path, f


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--src", default=str(SRC_DEFAULT)); ap.add_argument("--out", default=str(ROOT))
    args = ap.parse_args()
    from extract_writers import run  # Task 4
    run(pathlib.Path(args.src), pathlib.Path(args.out))
