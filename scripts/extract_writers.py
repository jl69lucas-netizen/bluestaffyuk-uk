#!/usr/bin/env python3
"""Writers for the extracted WordPress pages: rich .astro pages, locations.json, page-map.json."""
import json, pathlib, re
from bs4 import BeautifulSoup
from extract_wp import inventory, parse_page, classify, OLD_PUPS, OLD_PUP_IMAGES

NOT_FETCHED = "NOT FETCHED — GSC property unverified (domain expired); no exports on disk"
NOISE = ("blue", "staffy", "staffies", "staffordshire", "bull", "terrier", "puppies", "puppy",
         "for", "sale", "in", "buy", "area", "breeding", "dogs", "breeder")
KEEP_LOWER = {"under", "upon", "on", "de"}

# The 28 known location slugs, mapped by hand: the heuristic below cannot know that
# "cardiff-wales" is Cardiff or that the Glasgow breeding-dogs page is a second Glasgow page.
SLUG_CITY = {
    "blue-staffies-newcastle-under-lyme": "Newcastle-under-Lyme",
    "blue-staffy-puppies-aberdeen": "Aberdeen",
    "blue-staffy-puppies-birmingham": "Birmingham",
    "blue-staffy-puppies-bristol-uk": "Bristol",
    "blue-staffy-puppies-dundee": "Dundee",
    "blue-staffy-puppies-edinburgh": "Edinburgh",
    "blue-staffy-puppies-for-sale-in-leicester": "Leicester",
    "blue-staffy-puppies-for-sale-leeds": "Leeds",
    "blue-staffy-puppies-hull": "Hull",
    "blue-staffy-puppies-inverness": "Inverness",
    "blue-staffy-puppies-london": "London",
    "blue-staffy-puppies-manchester-uk": "Manchester",
    "blue-staffy-puppies-middlesbrough": "Middlesbrough",
    "blue-staffy-puppies-oxford": "Oxford",
    "blue-staffy-puppies-south-yorkshire": "South Yorkshire",
    "blue-staffy-puppies-sunderland": "Sunderland",
    "blue-staffy-puppies-uk": "UK",
    "blue-staffy-puppies-york": "York",
    "buy-blue-staffy-puppy-coventry-area": "Coventry",
    "staffy-breeding-dogs-glasgow": "Glasgow (breeding dogs)",
    "staffy-puppies-cardiff-wales": "Cardiff",
    "staffy-puppies-for-sale-cornwall": "Cornwall",
    "staffy-puppies-for-sale-essex": "Essex",
    "staffy-puppies-for-sale-glasgow": "Glasgow",
    "staffy-puppies-for-sale-liverpool": "Liverpool",
    "staffy-puppies-for-sale-nottingham": "Nottingham",
    "staffy-puppies-wolverhampton": "Wolverhampton",
    "uk-staffordshire-bull-terrier-breeder": "UK",
}

OLD_PUP_RE = re.compile(
    "|".join(r"\bmeet %s\b|\b%s['’]s overview\b|\b%s is\b" % (n, n, n) for n in OLD_PUPS))
OLD_PUP_NAME_RE = re.compile(r"\b(%s)\b" % "|".join(OLD_PUPS))
# Blocks that may wrap a whole pup card. `.wp-block-group` is only trusted on the
# image-filename path (see _names_in_labels) because its prose can be ordinary copy.
# `.bsuk-puppy-card` is the hand-written theme card used on nine location pages.
CARD_SELECTORS = (".wp-block-uagb-info-box, .wp-block-uagb-image, .wp-block-uagb-container, "
                  ".wp-block-uagb-column, .wp-block-group, .bsuk-puppy-card")
PROSE_PATH_EXCLUDED = ("wp-block-group",)
# Wrappers that exist only to lay out pup cards: drop them once they are empty.
CARD_GRID_SELECTORS = ".bsuk-puppies-grid"


def city_from_slug(slug):
    if slug in SLUG_CITY:
        return SLUG_CITY[slug]
    words = [w for w in slug.split("-") if w not in NOISE]
    if words and words[-1] == "uk" and len(words) > 1:
        words = words[:-1]
    if words and words[0] == "uk" and len(words) > 1:
        words = words[1:]
    if not words or words == ["uk"]:
        return "UK"
    return " ".join(w if w in KEEP_LOWER else w.capitalize() for w in words)


def meta_dict(page):
    """Shared meta shape for the .astro frontmatter and the locations rows."""
    return {"title": page.title, "description": page.description, "canonical": page.canonical,
            "robots": page.robots or "index, follow", "ogType": page.og_type or "article",
            "schema": page.schema}


def astro_frontmatter(page, layout_rel):
    return ("---\n"
            "import BaseLayout from '%s';\n"
            "const meta = %s;\n"
            "const body = %s;\n"
            "---\n"
            % (layout_rel, json.dumps(meta_dict(page), ensure_ascii=False),
               json.dumps(page.body_html, ensure_ascii=False)))


def _img_names(box):
    """Every image filename referenced by a box: src, data-src and the first srcset candidate."""
    names = set()
    for img in box.find_all("img"):
        raw = [img.get("src", ""), img.get("data-src", "")]
        srcset = img.get("srcset", "")
        if srcset:
            raw.append(srcset.split(",")[0].strip().split(" ")[0])
        for u in raw:
            u = re.split(r"[?#]", u)[0]
            if u:
                names.add(pathlib.Path(u).name)
    return names


def _names_in_labels(box):
    """True if a heading or <strong> inside the box names one of the sold pups."""
    for t in box.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"]):
        if OLD_PUP_NAME_RE.search(t.get_text(" ", strip=True).lower()):
            return True
    return False


def strip_old_pups(body_html):
    """Remove the four sold pups' cards (Spectra info-box / image / column / container blocks that
    name them or use their images). Returns (inner_html, removed_count); the original html is
    returned unchanged when nothing matched."""
    soup = BeautifulSoup(body_html, "lxml")
    removed = 0
    for box in soup.select(CARD_SELECTORS):
        if box.parent is None:          # already removed as part of an outer card
            continue
        txt = box.get_text(" ", strip=True).lower()
        if len(txt) >= 900:
            continue
        classes = box.get("class") or []
        by_image = bool(_img_names(box) & OLD_PUP_IMAGES)
        by_prose = (bool(OLD_PUP_RE.search(txt))
                    and not any(c in classes for c in PROSE_PATH_EXCLUDED)
                    and (box.find("img") is not None or _names_in_labels(box)))
        if by_image or by_prose:
            box.decompose()
            removed += 1
    if not removed:
        return body_html, 0
    for grid in soup.select(CARD_GRID_SELECTORS):
        if grid.parent is not None and not grid.find(True):
            grid.decompose()
    inner = soup.body.decode_contents() if soup.body else str(soup)
    return inner, removed


def old_pup_mentions(body_html):
    """How many times the sold pups are still named in the body text (prose, alts aside)."""
    text = BeautifulSoup(body_html, "lxml").get_text(" ", strip=True)
    return len(OLD_PUP_NAME_RE.findall(text.lower()))


def recount(page, body_html):
    """Refresh the derived counts/lists on `page` from a (stripped) body, one parse."""
    b = BeautifulSoup(body_html, "lxml")
    text = b.get_text(" ", strip=True)
    page.word_count = len(text.split())
    page.images = [{"src": i.get("src", ""), "alt": i.get("alt", "")} for i in b.find_all("img")]
    page.embeds = [f.get("src", "") for f in b.find_all("iframe")]
    page.headings = [(t.name, t.get_text(" ", strip=True)) for t in b.find_all(re.compile("^h[1-6]$"))]
    if page.word_count < 50:
        if "stub" not in page.defects:
            page.defects.append("stub")
    elif "stub" in page.defects:
        page.defects.remove("stub")
    return page


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
        meta = meta_dict(p)
        rows.append({"slug": slug, "city": city_from_slug(slug), "title": meta["title"],
                     "h1": p.h1, "description": meta["description"],
                     "canonical": meta["canonical"], "robots": meta["robots"],
                     "og_type": meta["ogType"], "body_html": p.body_html,
                     "word_count": p.word_count, "schema": meta["schema"], "defects": p.defects})
    f = out / "data/locations.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return f


def write_page_map(pages, out, src):
    rows = [{"url": p.url_path, "kind": p.kind, "title": p.title, "h1": p.h1,
             "word_count": p.word_count, "images": len(p.images), "embeds": len(p.embeds),
             "headings": p.headings, "defects": p.defects, "phone_hits": p.phone_hits,
             "refresh_flags": p.refresh_flags,
             "baseline_gsc": NOT_FETCHED, "baseline_bing": NOT_FETCHED} for p in pages]
    f = out / "data/page-map.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"generated_from": str(src), "pages": rows},
                            ensure_ascii=False, indent=2), encoding="utf-8")
    return f


def run(src, out):
    from extract_blog import write_blog_post       # Task 6
    from extract_images import rewrite_image_srcs  # Task 7
    src, out = pathlib.Path(src), pathlib.Path(out)
    pages, locs = [], []
    for url_path, f in inventory(src):
        kind = classify(url_path)
        if kind == "skip":
            continue
        page = parse_page(f, url_path)
        page.body_html, removed = strip_old_pups(page.body_html)
        if removed:
            page.refresh_flags.append("old-pup-cards-removed:%d" % removed)
            recount(page, page.body_html)
        mentions = old_pup_mentions(page.body_html)
        if mentions:
            page.refresh_flags.append("old-pup-names-in-prose:%d" % mentions)
        page.body_html = rewrite_image_srcs(page.body_html)
        if kind == "rich":
            write_rich_page(page, out)
        elif kind == "location":
            locs.append(page)
        elif kind == "blog":
            write_blog_post(page, out)
        pages.append(page)
    write_locations(locs, out)
    write_page_map(pages, out, src)
    print("extracted %d pages (%d locations)" % (len(pages), len(locs)))
