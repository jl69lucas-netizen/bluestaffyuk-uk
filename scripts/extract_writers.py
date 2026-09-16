#!/usr/bin/env python3
"""Writers for the extracted WordPress pages: rich .astro pages, locations.json, page-map.json."""
import json, pathlib, re
from bs4 import BeautifulSoup
from extract_wp import (inventory, parse_page, classify, OLD_PUPS, OLD_PUP_IMAGES,
                        OLD_PRICE_RE)
from extract_images import SIZE_SUFFIX

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
# WordPress size suffix on a derived upload ("...-300x200.jpg"); the pups' own filenames
# never look like that, so stripping it is safe and catches resized copies in JSON-LD.
SIZE_SUFFIX_RE = re.compile(r"-\d{2,4}x\d{2,4}$")
OLD_PUP_STEMS = set(pathlib.Path(n).stem for n in OLD_PUP_IMAGES)
# "@id" is included because Yoast's graph names an ImageObject by its own file URL, so the
# bare {"@id": "...jpg"} reference stubs elsewhere in the graph must go with the node itself.
SCHEMA_URL_KEYS = ("url", "contentUrl", "thumbnailUrl", "@id")
SCHEMA_IMAGE_KEYS = ("image", "primaryImageOfPage")


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


# Pages that must never be indexed regardless of what the old Rank Math tags said: the
# thank-you page is a post-submit destination with no standalone search value.
NOINDEX_PATHS = ["/thank-you-blue-staffy-puppies-journey/"]

# Pages whose generated .astro also renders the live puppy list. These files are rewritten
# by every `npm run extract`, so the component has to be emitted by the writer.
PUPPY_LIST_PAGES = {"/", "/buy-blue-staffy-puppies-uk/"}
CONTACT_FORM_PAGES = {"/uk-blue-staffy-breeders-contact/"}

# (pages that get it, component name) — write_rich_page imports and emits each match,
# in this order, just before </BaseLayout>.
PAGE_COMPONENTS = ((PUPPY_LIST_PAGES, "PuppyList"), (CONTACT_FORM_PAGES, "ContactForm"))


def meta_dict(page):
    """Shared meta shape for the .astro frontmatter and the locations rows."""
    robots = page.robots or "index, follow"
    if page.canonical in NOINDEX_PATHS:
        robots = "noindex, follow"
    if "stub" in page.defects:
        # Interim call from Task 9: the thin (4-word) location pages stay out of the index
        # until project 5 rebuilds them, so a crawl never sees the placeholder prose.
        robots = "noindex, follow"
        if "stub-noindexed" not in page.refresh_flags:
            page.refresh_flags.append("stub-noindexed")
    return {"title": page.title, "description": page.description, "canonical": page.canonical,
            "robots": robots, "ogType": page.og_type or "article", "h1": page.h1,
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
    """Every image filename a box references, with the WP size suffix normalised away.

    src, data-src and *every* srcset candidate are considered: WordPress resizes mean the
    same photo appears as pup.jpg, pup-300x200.jpg, pup-768x512.jpg, and a card may carry
    only the resized variants. Names are returned both verbatim and suffix-stripped so a
    comparison against OLD_PUP_IMAGES (which lists full-size names) matches either way.
    """
    names = set()
    for img in box.find_all("img"):
        raw = [img.get("src", ""), img.get("data-src", "")]
        for attr in ("srcset", "data-srcset"):
            for cand in img.get(attr, "").split(","):
                cand = cand.strip().split(" ")[0]
                if cand:
                    raw.append(cand)
        for u in raw:
            u = re.split(r"[?#]", u)[0]
            if not u:
                continue
            name = pathlib.Path(u).name
            names.add(name)
            stem, suffix = pathlib.Path(name).stem, pathlib.Path(name).suffix
            names.add(SIZE_SUFFIX.sub("", stem) + suffix)
    return names


def _names_in_labels(box):
    """True if a heading or <strong> inside the box names one of the sold pups."""
    for t in box.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"]):
        if OLD_PUP_NAME_RE.search(t.get_text(" ", strip=True).lower()):
            return True
    return False


def strip_old_pups(body_html):
    """Remove the four sold pups' cards (Spectra info-box / image / column / container blocks that
    name them or use their images). Returns (inner_html, removed_count, notes); the original
    html is returned unchanged when nothing matched."""
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
        return body_html, 0, []
    notes = []
    for grid in soup.select(CARD_GRID_SELECTORS):
        if grid.parent is not None and not grid.find(True) and not grid.get_text(strip=True):
            grid.decompose()
            notes.append("puppy-grid-emptied")
    inner = soup.body.decode_contents() if soup.body else str(soup)
    return inner, removed, notes


def old_pup_mentions(body_html):
    """How many times the sold pups are still named in the body text (prose, alts aside)."""
    text = BeautifulSoup(body_html, "lxml").get_text(" ", strip=True)
    return len(OLD_PUP_NAME_RE.findall(text.lower()))


def _is_old_pup_url(value):
    if not isinstance(value, str) or not value:
        return False
    stem = pathlib.Path(re.split(r"[?#]", value)[0]).stem
    return SIZE_SUFFIX_RE.sub("", stem) in OLD_PUP_STEMS


def _node_is_old_pup(node):
    return isinstance(node, dict) and any(_is_old_pup_url(node.get(k)) for k in SCHEMA_URL_KEYS)


def scrub_schema_old_pups(schema):
    """Drop JSON-LD nodes whose image URL is one of the sold pups' photos.

    Returns (schema, removed). A deleted node that was the whole value of an "image" /
    "primaryImageOfPage" key takes the key with it.
    """
    count = [0]

    def walk(node):
        if isinstance(node, list):
            out = []
            for v in node:
                if _node_is_old_pup(v):
                    count[0] += 1
                    continue
                out.append(walk(v))
            return out
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                if k in SCHEMA_IMAGE_KEYS and _node_is_old_pup(v):
                    count[0] += 1
                    continue                      # drop the key with its only value
                if k in SCHEMA_IMAGE_KEYS and isinstance(v, str) and _is_old_pup_url(v):
                    count[0] += 1
                    continue
                if _node_is_old_pup(v):
                    count[0] += 1
                    continue
                out[k] = walk(v)
            return out
        return node

    return walk(schema), count[0]


def recount(page, body_html):
    """Refresh the derived counts/lists and price flags on `page` from a (stripped) body.

    Mutates `page` in place and returns None: one BeautifulSoup parse, same field shapes
    as extract_wp.parse_page.
    """
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
    page.refresh_flags[:] = [f for f in page.refresh_flags if not f.startswith("old-price:")]
    for m in OLD_PRICE_RE.finditer(text):
        page.refresh_flags.append("old-price:%s" % m.group(0))


LEGACY_SITEWIDE_TYPES = {"WebSite", "BreadcrumbList", "Organization", "PetStore",
                         "LocalBusiness"}


def _types_of(node):
    t = node.get("@type") if isinstance(node, dict) else None
    if isinstance(t, str):
        return {t}
    if isinstance(t, list):
        return set(x for x in t if isinstance(x, str))
    return set()


DANGLING_REF_KEYS = ("isPartOf", "breadcrumb", "publisher", "about", "mainEntity")


def _note_id(node, ids):
    if isinstance(node, dict) and isinstance(node.get("@id"), str):
        ids.add(node["@id"])


def _prune_refs(node, dropped_ids):
    """Delete refs on a kept node that point at a node dedupe just dropped."""
    if not isinstance(node, dict):
        return node
    out = dict(node)
    for key in DANGLING_REF_KEYS:
        v = out.get(key)
        target = (v.get("@id") if isinstance(v, dict) and set(v) == {"@id"}
                  else v if isinstance(v, str) else None)
        if isinstance(target, str) and target in dropped_ids:
            del out[key]
    return out


def _prune_block_refs(block, dropped_ids):
    if isinstance(block, dict) and isinstance(block.get("@graph"), list):
        return dict(block, **{"@graph": [_prune_refs(n, dropped_ids) for n in block["@graph"]]})
    return _prune_refs(block, dropped_ids)


def dedupe_legacy_schema(schema):
    """Drop the sitewide entities the old Rank Math graph repeated on every page.

    Schema.astro now emits LocalBusiness, WebSite and BreadcrumbList itself from
    data/settings.json, so carrying the legacy copies through would ship two of each with
    conflicting @ids. Page-specific nodes (WebPage, Article, FAQPage, VideoObject,
    ImageObject, Person, Place, ...) are kept verbatim. References from kept
    nodes to a dropped node's @id are deleted too, so no dangling refs survive.
    Returns (schema, dropped).
    """
    dropped = 0
    dropped_ids = set()
    out_blocks = []
    for block in schema:
        if isinstance(block, dict) and isinstance(block.get("@graph"), list):
            kept = []
            for node in block["@graph"]:
                if _types_of(node) & LEGACY_SITEWIDE_TYPES:
                    dropped += 1
                    _note_id(node, dropped_ids)
                    continue
                kept.append(node)
            block = dict(block, **{"@graph": kept})
            if not kept:
                continue
        elif _types_of(block) & LEGACY_SITEWIDE_TYPES:
            # A top-level block that is solely one of the sitewide entities.
            dropped += 1
            _note_id(block, dropped_ids)
            continue
        out_blocks.append(block)
    if dropped_ids:
        out_blocks = [_prune_block_refs(b, dropped_ids) for b in out_blocks]
    return out_blocks, dropped


def write_rich_page(page, out):
    rel = page.url_path.strip("/")
    d = out / "src/pages" / rel if rel else out / "src/pages"
    d.mkdir(parents=True, exist_ok=True)
    f = d / "index.astro"
    depth = len([p for p in rel.split("/") if p]) + 1
    layout_rel = "../" * depth + "layouts/BaseLayout.astro"
    components = [name for pages, name in PAGE_COMPONENTS if page.url_path in pages]
    frontmatter = astro_frontmatter(page, layout_rel)
    if components:
        imports = "".join("import %s from '%scomponents/%s.astro';\n" % (name, "../" * depth, name)
                          for name in components)
        frontmatter = frontmatter.replace(
            "import BaseLayout from '%s';\n" % layout_rel,
            "import BaseLayout from '%s';\n%s" % (layout_rel, imports))
    f.write_text(frontmatter +
                 "<BaseLayout title={meta.title} description={meta.description} canonical={meta.canonical} "
                 "robots={meta.robots} ogType={meta.ogType} schema={meta.schema} "
                 "crumbTitle={meta.h1 || meta.title}>\n"
                 "  <article class=\"container container-text prose-migrated\">\n"
                 "    <Fragment set:html={body} />\n  </article>\n" +
                 "".join("  <%s />\n" % name for name in components) +
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
    from extract_images import rewrite_image_srcs, rewrite_schema_urls  # Task 7
    src, out = pathlib.Path(src), pathlib.Path(out)
    pages, locs = [], []
    for url_path, f in inventory(src):
        kind = classify(url_path)
        if kind == "skip":
            continue
        page = parse_page(f, url_path)
        page.body_html, removed, notes = strip_old_pups(page.body_html)
        if removed:
            page.refresh_flags.append("old-pup-cards-removed:%d" % removed)
            page.refresh_flags.extend(notes)
            recount(page, page.body_html)
        page.schema, schema_removed = scrub_schema_old_pups(page.schema)
        if schema_removed:
            page.refresh_flags.append("old-pup-schema-images-removed:%d" % schema_removed)
        mentions = old_pup_mentions(page.body_html)
        if mentions:
            page.refresh_flags.append("old-pup-names-in-prose:%d" % mentions)
        page.schema, legacy_dropped = dedupe_legacy_schema(page.schema)
        if legacy_dropped:
            page.refresh_flags.append("legacy-schema-nodes-dropped:%d" % legacy_dropped)
        page.body_html = rewrite_image_srcs(page.body_html)
        page.schema = rewrite_schema_urls(page.schema)
        if kind == "rich":
            write_rich_page(page, out)
        elif kind == "location":
            locs.append(page)
        elif kind == "blog":
            write_blog_post(page, out)
        pages.append(page)
    write_locations(locs, out)
    write_page_map(pages, out, src)
    seen = set(p.canonical for p in pages)
    for path in NOINDEX_PATHS:
        if path not in seen:
            print("WARNING: NOINDEX_PATHS entry %s matched no page — the rule is dead" % path)
    stubs = len([p for p in pages if "stub-noindexed" in p.refresh_flags])
    print("extracted %d pages (%d locations); %d stub page(s) noindexed"
          % (len(pages), len(locs), stubs))
