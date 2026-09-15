#!/usr/bin/env python3
"""Writers for the extracted WordPress pages: rich .astro pages, locations.json, page-map.json."""
import json, pathlib, re
from bs4 import BeautifulSoup
from extract_wp import Page, inventory, parse_page, classify, OLD_PUPS, OLD_PUP_IMAGES

NOT_FETCHED = "NOT FETCHED — GSC property unverified (domain expired); no exports on disk"
NOISE = ("blue", "staffy", "staffies", "staffordshire", "bull", "terrier", "puppies", "puppy",
         "for", "sale", "in", "buy", "area", "breeding", "dogs", "breeder")
KEEP_LOWER = {"under", "upon", "on", "de"}

OLD_PUP_RE = re.compile(
    "|".join(r"\bmeet %s\b|\b%s['’]s overview\b|\b%s is\b" % (n, n, n) for n in OLD_PUPS))
CARD_SELECTORS = (".wp-block-uagb-info-box, .wp-block-uagb-image, .wp-block-uagb-container, "
                  ".wp-block-uagb-column, .wp-block-group")


def city_from_slug(slug):
    words = [w for w in slug.split("-") if w not in NOISE]
    if words and words[-1] == "uk" and len(words) > 1:
        words = words[:-1]
    if words and words[0] == "uk" and len(words) > 1:
        words = words[1:]
    if not words or words == ["uk"]:
        return "UK"
    return " ".join(w if w in KEEP_LOWER else w.capitalize() for w in words)


def astro_frontmatter(page, layout_rel):
    meta = {"title": page.title, "description": page.description, "canonical": page.canonical,
            "robots": page.robots or "index, follow", "ogType": page.og_type or "article",
            "schema": page.schema}
    return ("---\n"
            "import BaseLayout from '%s';\n"
            "const meta = %s;\n"
            "const body = %s;\n"
            "---\n"
            % (layout_rel, json.dumps(meta, ensure_ascii=False),
               json.dumps(page.body_html, ensure_ascii=False)))


def strip_old_pups(body_html):
    """Remove the four sold pups' cards (Spectra info-box / image / column blocks that name them
    or use their images). Returns (inner_html, removed_count)."""
    soup = BeautifulSoup(body_html, "lxml")
    removed = 0
    for box in soup.select(CARD_SELECTORS):
        if box.parent is None:          # already removed as part of an outer card
            continue
        txt = box.get_text(" ", strip=True).lower()
        imgs = {pathlib.Path(i.get("src", "")).name for i in box.find_all("img")}
        if (OLD_PUP_RE.search(txt) or (imgs & OLD_PUP_IMAGES)) and len(txt) < 900:
            box.decompose()
            removed += 1
    inner = soup.body.decode_contents() if soup.body else str(soup)
    return inner, removed


def write_rich_page(page, out):
    rel = page.url_path.strip("/")
    d = out / "src/pages" / rel if rel else out / "src/pages"
    d.mkdir(parents=True, exist_ok=True)
    f = d / "index.astro"
    depth = len([p for p in rel.split("/") if p]) + 1
    layout_rel = "../" * depth + "layouts/BaseLayout.astro"
    f.write_text(astro_frontmatter(page, layout_rel) +
                 "<BaseLayout title={meta.title} description={meta.description} canonical={meta.canonical} "
                 "robots={meta.robots} ogType={meta.ogType} schema={meta.schema}>\n"
                 "  <article class=\"container container-text prose-migrated\">\n"
                 "    <Fragment set:html={body} />\n  </article>\n"
                 "</BaseLayout>\n", encoding="utf-8")
    return f


def write_locations(pages, out):
    rows = []
    for p in pages:
        slug = p.url_path.strip("/").split("/")[-1]
        rows.append({"slug": slug, "city": city_from_slug(slug), "title": p.title, "h1": p.h1,
                     "description": p.description, "canonical": p.canonical, "robots": p.robots,
                     "body_html": p.body_html, "word_count": p.word_count, "schema": p.schema,
                     "defects": p.defects})
    f = out / "data/locations.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return f


def write_page_map(pages, out):
    rows = [{"url": p.url_path, "kind": p.kind, "title": p.title, "h1": p.h1,
             "word_count": p.word_count, "images": len(p.images), "embeds": len(p.embeds),
             "headings": p.headings, "defects": p.defects, "phone_hits": p.phone_hits,
             "refresh_flags": p.refresh_flags,
             "baseline_gsc": NOT_FETCHED, "baseline_bing": NOT_FETCHED} for p in pages]
    f = out / "data/page-map.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"generated_from": "/Users/apple/bluestaffyuk-site", "pages": rows},
                            ensure_ascii=False, indent=2), encoding="utf-8")
    return f


def run(src, out):
    from extract_blog import write_blog_post       # Task 6
    from extract_images import rewrite_image_srcs  # Task 7
    pages, locs = [], []
    for url_path, f in inventory(src):
        kind = classify(url_path)
        if kind == "skip":
            continue
        page = parse_page(f, url_path)
        page.body_html, removed = strip_old_pups(page.body_html)
        if removed:
            page.refresh_flags.append("old-pup-cards-removed:%d" % removed)
        page.body_html = rewrite_image_srcs(page.body_html)
        if kind == "rich":
            write_rich_page(page, out)
        elif kind == "location":
            locs.append(page)
        elif kind == "blog":
            write_blog_post(page, out)
        pages.append(page)
    write_locations(locs, out)
    write_page_map(pages, out)
    print("extracted %d pages (%d locations)" % (len(pages), len(locs)))
