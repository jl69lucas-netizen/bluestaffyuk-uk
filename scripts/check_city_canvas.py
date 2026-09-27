#!/usr/bin/env python3
"""Gate: a city component canvas is well-formed before it is built into a page.

A city canvas is `design/city-canvas/<city>/<component>/{a,b,c}.html` plus one `meta.json`
per component (spec docs/superpowers/specs/2026-09-27-london-component-design-pass-design.md
§1–§2). Each `.html` is a FRAGMENT: zero or more `<style>` blocks, then exactly one
`<section data-component="<component>" data-variant="<a|b|c>">`. The canvas builder
(scripts/build_component_canvas.py) wraps it in a frame with the design tokens.

What is refused, per fragment:
  structure  — one root section naming its own component and variant; no <script>, <link>,
               <iframe>, <object>, <embed>, <video>, <audio> (CSS-first, nothing heavy)
  colour     — no hex, no rgb()/hsl()/…, no black/white/grey/silver in CSS or an SVG paint
               attribute: every colour is a var(--…) token (rules/design.md rule 1), so a bleed
               can never be grey or black
  headings   — every h1–h6 ends in "?" (a buyer question) and the next start tag after it,
               skipping <div> wrappers and an image (<figure>/<picture>/<img>, which rule 17
               puts first under an H3), is a <p> of at least 12 words (the conversational
               opening). A puppy card's name may carry data-heading-exempt="puppy-name"
  tables     — every <td> carries a non-empty data-label (working rule 13)
  hero       — the first <img>/<picture> comes before the first <h1>/<h2> in source
  assets     — every src/srcset/poster/url() is /images/<file> (public/images) or
               /puppies/<file> (src/assets/puppies) and exists; <a href> is "#…" or "/…";
               every <img> has a non-empty alt (or alt="" marked aria-hidden="true" /
               role="presentation" when it is decorative) and numeric width and height (no
               layout shift);
               a served /images/ file keeps an alt it was served with, word for word
               (working rule 11; served_alts())
  copy       — the word "London" appears; every £ amount is a price, the deposit or a
               delivery bound from data/; a parent is named only as data/faq.json names them;
               no unconfirmed audience or promise claim (UNCONFIRMED_CLAIMS); no phone
               number (PHONE_PLACEHOLDER only); no
               source-project marker (scripts/marker_check.py MARKERS) and no reference-site
               host name (docs/research/2026-09-27-location-component-design-sources.md)
  reviews    — in `reviews`, every <blockquote> is either data-placeholder="review" or
               data-review="<n>" quoting data/reviews.json[n] word for word: a mockup never
               presents an invented review as a real one (CLAUDE.md working rule 9)
  hooks      — the data hooks HOOKS names for the component (six puppy cards, three FAQ
               blocks of 15–20 questions, …); every form field has a <label for> or
               aria-label; a <form action> is absent or "#…"
and per component meta.json: name, one-line description, idea_sources cited in the ideas
index under that component, the four canonical axes (scripts/city_components.py AXES/VOCAB),
a differs_from note; siblings differ on >= 2 axes; each variant differs on >= 2 axes from
every row of data/design/city-must-differ.json for its component.

    python3 scripts/check_city_canvas.py [--city london] [--only hero,counter-strip]

Without --only, all fifteen components must be present with exactly three variants each.
Exit 1 on any problem, 2 on a usage error. Prints its examined counts.
"""
import argparse
import dataclasses
import html
import html.parser
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import marker_check  # noqa: E402
from city_components import (AXES, CANVAS_ROOT, COMPONENT_IDS, ROOT, VARIANT_IDS,  # noqa: E402
                             VOCAB, axis_distance)

SOURCES_DOC = ROOT / "docs" / "research" / "2026-09-27-location-component-design-sources.md"
IDEAS_INDEX = ROOT / "docs" / "research" / "london-components" / "ideas-index.md"
MUST_DIFFER = ROOT / "data" / "design" / "city-must-differ.json"
IMAGE_ROOTS = {"/images/": ROOT / "public" / "images", "/puppies/": ROOT / "src" / "assets" / "puppies"}

BANNED_TAGS = {"script", "link", "iframe", "object", "embed", "video", "audio"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
MIN_OPENING_WORDS = 12
HEADING_SKIP = {"div", "figure", "picture", "img", "source", "figcaption"}
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
COLOUR_FN = re.compile(r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(", re.I)
NAMED = re.compile(r"(?<![-\w])(?:black|white|gr[ae]y|silver)(?![-\w])", re.I)
PAINT_ATTRS = {"fill", "stroke", "stop-color", "flood-color", "lighting-color", "color"}
PAINT_OK = re.compile(r"^(?:none|currentcolor|transparent|url\(#[\w-]+\))$", re.I)
CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)")
POUNDS = re.compile(r"£\s?(\d[\d,]*)")
PHONE = re.compile(r"(?:\+44\s?|\b0)\d(?:[\s-]?\d){8,9}\b")
LAYOUT_SLUG = re.compile(r"^[a-z0-9]+(?:[-+][a-z0-9]+)*$")

#: The data hooks each component's fragment must carry, as (attribute, minimum, maximum). They
#: are what tests/render/canvas.spec.ts measures and what the kit build in Plan 2 keys on, so a
#: variant that restyles a component can never quietly drop a part of it: six puppy cards (the
#: litter in data/puppies.json), three FAQ blocks holding 15–20 questions (the city page's FAQ
#: shape), a strip AND a sheet for the phone jump links, a play control for the video facade.
HOOKS = {
    "hero": (),
    "counter-strip": (("data-figure", 3, 6),),
    "trust-strip": (("data-trust-item", 3, 8),),
    "contents-list": (("data-contents", 1, 1),),
    "desktop-dial": (("data-dial", 1, 1),),
    "jump-links": (("data-jump-strip", 1, 1), ("data-jump-sheet", 1, 1), ("data-jump-open", 1, 1)),
    "key-takeaways": (("data-takeaway", 3, 6),),
    "puppy-cards": (("data-puppy", 6, 6),),
    "tables": (("data-table", 1, 3),),
    "video": (("data-play", 1, 1),),
    "image-text": (("data-media", 1, 2),),
    "reviews": (("data-review-slot", 1, 3),),
    "faq-blocks": (("data-faq-block", 3, 3), ("data-faq-q", 15, 20)),
    "newsletter": (("data-newsletter", 1, 1),),
    "contact-form": (("data-contact-form", 1, 1),),
}
FIELDS = {"input", "select", "textarea"}


@dataclasses.dataclass
class Context:
    banned_words: tuple
    allowed_pounds: frozenset
    must_differ: dict
    ideas: dict
    reviews: tuple = ()
    image_roots: dict = dataclasses.field(default_factory=lambda: dict(IMAGE_ROOTS))
    served_alts: dict = dataclasses.field(default_factory=dict)
    parents: frozenset = frozenset()


def banned_words(sources_doc=SOURCES_DOC):
    """Every reference-site host named in the sources doc, and its first label. The
    source-project markers are judged separately, by marker_check's own matcher."""
    words = set()
    text = pathlib.Path(sources_doc).read_text(encoding="utf-8") if pathlib.Path(sources_doc).exists() else ""
    for host in re.findall(r"https?://(?:www\.)?([^/\s)>`]+)", text):
        words.add(host.lower())
        words.add(host.lower().split(".")[0])
    return tuple(sorted(words))


def allowed_pounds(root=ROOT):
    s = json.loads((root / "data" / "settings.json").read_text(encoding="utf-8"))
    p = json.loads((root / "data" / "puppies.json").read_text(encoding="utf-8"))
    vals = {s["deposit_gbp"], s["delivery_min_gbp"], s["delivery_max_gbp"]}
    vals |= {row["price_gbp"] for row in p}
    return frozenset(int(v) for v in vals)


def real_reviews(root=ROOT):
    """The quotes of data/reviews.json, in file order: the only reviews a variant may show."""
    rows = json.loads((root / "data" / "reviews.json").read_text(encoding="utf-8"))
    return tuple(" ".join(r["quote"].split()) for r in rows)


_IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
_SIZED = re.compile(r"^(?P<base>.+)-(?:\d{3,4})(?P<ext>\.\w+)$")


def _tag_attr(tag, name):
    """An attribute's value, double- or single-quoted; "" for a bare attribute (`alt`, as Astro
    renders alt=""); None when the tag does not carry it."""
    m = re.search(r"""\s%s\s*=\s*(?:"([^"]*)"|'([^']*)')""" % name, tag)
    if m:
        return html.unescape(m.group(1) if m.group(1) is not None else m.group(2))
    return "" if re.search(r"\s%s(?=[\s>/])" % name, tag) else None


def served_alts(root=ROOT):
    """{file under public/images/: frozenset(alt)} — every alt the old site served each file
    with: the migrated pages' verbatim sets (data/verbatim/*.json `alts`) and the location pages'
    body images (data/locations.json). Working rule 11 keeps these word for word wherever the
    file is reused (learning loop 2026-09-27, L2)."""
    root = pathlib.Path(root)
    out = {}

    def add(src, alt):
        if src and alt is not None and "/images/" in src:
            name = src.split("/images/", 1)[1].split("?", 1)[0]
            if name and "/" not in name:
                out.setdefault(name, set()).add(" ".join(alt.split()))
    for f in sorted((root / "data" / "verbatim").glob("*.json")):
        for row in json.loads(f.read_text(encoding="utf-8")).get("alts", []):
            add(row.get("src"), row.get("alt"))
    loc = root / "data" / "locations.json"
    if loc.exists():
        for row in json.loads(loc.read_text(encoding="utf-8")):
            for tag in _IMG_TAG.findall(row.get("body_html") or ""):
                add(_tag_attr(tag, "src"), _tag_attr(tag, "alt"))
    return {k: frozenset(v - {""}) for k, v in out.items() if v - {""}}


#: Parent-name phrasings (learning loop 2026-09-27, L3 i): a capitalised name the copy gives the
#: dam, the sire or "the parents". The same patterns read the allowed set out of data/faq.json,
#: so the canvas can only name the parents the facts name (Maggie and Jones, 7ce341a).
_NAME = r"([A-Z][a-z]+)"
_PARENT_WORD = r"(?i:dam|sire|mother|father|mum|dad)"
PARENT_PATTERNS = (
    re.compile(r"\b(?i:parents?)\b[,:]?\s+(?:(?i:are|were)\s+)?" + _NAME + r"\s+(?:and|&)\s+" + _NAME + r"\b"),
    re.compile(_NAME + r"\s+(?:and|&)\s+" + _NAME
               + r",?\s+(?:(?i:both|our|the)\s+)*(?i:parents|dam and sire|sire and dam)\b"),
    re.compile(r"\b" + _NAME + r",?\s+(?i:our|the|a|her|his|their)\s+(?:[\w-]+\s+){0,2}?"
               + _PARENT_WORD + r"\b"),
    re.compile(r"\b" + _PARENT_WORD + r"\b[,:]?\s+(?:(?i:is|was)\s+)?\(?" + _NAME + r"\b"),
)
#: Capitalised words the patterns can catch that are not names (Title Case headings, sentence starts).
NOT_NAMES = frozenset({
    "A", "An", "And", "Are", "Blue", "Both", "Carlisle", "Cumbria", "Dam", "Do", "Does", "Each",
    "Every", "Father", "Has", "Have", "Health", "Her", "His", "In", "Is", "London", "Meet",
    "Mother", "Of", "Our", "Parent", "Parents", "Photo", "See", "Sire", "Staffy", "Tests", "The",
    "Their", "Was", "What", "Which", "Who", "Your"})
#: Claims no file records (learning loop 2026-09-27, L3 ii): an audience majority, a promise in
#: writing, a handling routine, a litter count. Refused until the breeder confirms one.
UNCONFIRMED_CLAIMS = (
    re.compile(r"\b(?:most|many|some|plenty of)\s+(?:\w+\s+)?(?:buyers|families|owners|people)\b", re.I),
    re.compile(r"\bin writing\b", re.I),
    re.compile(r"\bhandled daily\b", re.I),
    re.compile(r"\bone litter\b", re.I),
)


def named_parents(text):
    """Every name the text gives a parent, in order (NOT_NAMES removed)."""
    return [g for rx in PARENT_PATTERNS for m in rx.finditer(text)
            for g in m.groups() if g and g not in NOT_NAMES]


def parent_names(root=ROOT):
    """The parents data/faq.json names (each at least twice, so a stray capital is not one)."""
    rows = json.loads((pathlib.Path(root) / "data" / "faq.json").read_text(encoding="utf-8"))
    found = named_parents(" ".join(f"{r.get('q', '')}. {r.get('a', '')}" for r in rows))
    return frozenset(n for n in found if found.count(n) >= 2)


def served_name(name, served):
    """The served file a srcset width (`x-760.webp`) belongs to; the name itself otherwise."""
    if name in served:
        return name
    m = _SIZED.match(name)
    return m.group("base") + m.group("ext") if m and m.group("base") + m.group("ext") in served else name


def ideas_sections(text):
    """{component id: section text} out of the ideas index (`## <id> — <name>` headings)."""
    out = {}
    parts = re.split(r"^## ([a-z-]+) — .*$", text, flags=re.M)
    for i in range(1, len(parts), 2):
        out[parts[i]] = parts[i + 1]
    return out


def default_context():
    md = json.loads(MUST_DIFFER.read_text(encoding="utf-8"))["components"] if MUST_DIFFER.exists() else {}
    ideas = ideas_sections(IDEAS_INDEX.read_text(encoding="utf-8")) if IDEAS_INDEX.exists() else {}
    return Context(banned_words=banned_words(), allowed_pounds=allowed_pounds(),
                   must_differ=md, ideas=ideas, reviews=real_reviews(), served_alts=served_alts(),
                   parents=parent_names())


class _Walk(html.parser.HTMLParser):
    """One pass over a fragment, collecting what the rules need, in source order."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events = []          # ("start", tag, attrs) / ("end", tag) / ("text", data)
        self.css = []             # every <style> body and style="" value
        self.depth = 0
        self.roots = []           # (tag, attrs) of every element opened at depth 0
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if self.depth == 0:
            self.roots.append((tag, a))
        self.events.append(("start", tag, a))
        if "style" in a:
            self.css.append(a["style"])
        if tag == "style":
            self._in_style = True
        if tag not in {"img", "source", "br", "hr", "input", "meta", "wbr", "col", "area"}:
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in {"img", "source", "br", "hr", "input", "meta", "wbr", "col", "area"}:
            self.depth -= 1
            self.events.append(("end", tag))

    def handle_endtag(self, tag):
        if tag in {"img", "source", "br", "hr", "input", "meta", "wbr", "col", "area"}:
            return
        self.depth -= 1
        self.events.append(("end", tag))
        if tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_style:
            self.css.append(data)
        else:
            self.events.append(("text", data))


def _text(events):
    return " ".join(e[1] for e in events if e[0] == "text")


def _url_ok(url, ctx):
    """None when the URL is an allowed repo image, else the reason it is not."""
    for prefix, folder in ctx.image_roots.items():
        if url.startswith(prefix):
            name = url[len(prefix):]
            if "/" in name or not name:
                return f"{url}: nested or empty image path"
            return None if (pathlib.Path(folder) / name).is_file() else f"{url}: no such file under {folder}"
    return f"{url}: not a repo image (/images/… or /puppies/…)"


def validate_fragment(component, variant, text, ctx):
    """[problem] for one fragment."""
    p = []
    w = _Walk()
    w.feed(text)
    w.close()
    roots = [r for r in w.roots if r[0] != "style"]
    if len(roots) != 1 or roots[0][0] != "section":
        p.append(f"structure: one root <section> expected after the <style> blocks, found "
                 f"{[r[0] for r in roots]}")
    else:
        a = roots[0][1]
        if a.get("data-component") != component or a.get("data-variant") != variant:
            p.append(f"structure: root section must carry data-component=\"{component}\" "
                     f"data-variant=\"{variant}\"")
    starts = [(i, e[1], e[2]) for i, e in enumerate(w.events) if e[0] == "start"]
    for _i, tag, _a in starts:
        if tag in BANNED_TAGS:
            p.append(f"structure: <{tag}> is not allowed in a canvas fragment")
    css = "\n".join(w.css)
    for rx, what in ((HEX, "hex colour"), (COLOUR_FN, "colour function"), (NAMED, "named colour")):
        for m in rx.finditer(css):
            p.append(f"colour: {what} {m.group(0)!r} in CSS — use a var(--…) token")
    for _i, tag, a in starts:
        for attr in PAINT_ATTRS & set(a):
            if tag in {"svg", "path", "circle", "rect", "line", "polyline", "polygon", "g",
                       "ellipse", "stop", "text", "use"} and not PAINT_OK.match(a[attr].strip()):
                p.append(f"colour: <{tag} {attr}=\"{a[attr]}\"> — use currentColor or none")
    # headings
    events = w.events
    for idx, tag, a in starts:
        if tag not in HEADINGS:
            continue
        end = next((j for j in range(idx + 1, len(events))
                    if events[j][0] == "end" and events[j][1] == tag), len(events))
        heading = " ".join(_text(events[idx + 1:end]).split())
        exempt = component == "puppy-cards" and a.get("data-heading-exempt") == "puppy-name"
        if exempt:
            continue
        if not heading.endswith("?"):
            p.append(f"heading: <{tag}> {heading!r} is not a question ending in '?'")
        nxt = next(((j, e[1]) for j, e in enumerate(events[end + 1:], end + 1)
                    if e[0] == "start" and e[1] not in HEADING_SKIP), None)
        if not nxt or nxt[1] != "p":
            p.append(f"heading: <{tag}> {heading!r} is not followed by an opening <p>")
            continue
        pend = next((j for j in range(nxt[0] + 1, len(events))
                     if events[j][0] == "end" and events[j][1] == "p"), len(events))
        words = len(_text(events[nxt[0] + 1:pend]).split())
        if words < MIN_OPENING_WORDS:
            p.append(f"heading: the opening <p> after {heading!r} has {words} words, "
                     f"fewer than {MIN_OPENING_WORDS}")
    # hooks: the parts of the component a variant may restyle but never drop
    for attr, lo, hi in HOOKS.get(component, ()):
        n = sum(1 for _i, _t, a in starts if attr in a)
        if not lo <= n <= hi:
            want = str(lo) if lo == hi else f"{lo}–{hi}"
            p.append(f"hooks: {n} element(s) carry {attr}, {component} needs {want}")
    if component == "tables" and not any(t == "table" for _i, t, _a in starts):
        p.append("hooks: a tables variant renders a real <table>")
    # form fields: a label for every field a person fills in
    labelled = {a.get("for") for _i, t, a in starts if t == "label"}
    for _i, tag, a in starts:
        if tag in FIELDS and a.get("type") not in ("hidden", "submit", "button"):
            if not (a.get("id") in labelled or a.get("aria-label", "").strip()):
                p.append(f"form: <{tag} name=\"{a.get('name', '')}\"> has no <label for> or aria-label")
    # tables
    for _i, tag, a in starts:
        if tag == "td" and not a.get("data-label", "").strip():
            p.append("table: a <td> carries no data-label, so it stacks unlabelled on a phone")
    # hero: the photo precedes the heading in source
    if component == "hero":
        first_img = next((i for i, t, _a in starts if t in ("img", "picture")), None)
        first_h = next((i for i, t, _a in starts if t in ("h1", "h2")), None)
        if first_img is None or first_h is None or first_img > first_h:
            p.append("hero: the <img>/<picture> must come before the <h1>/<h2> in source "
                     "(the photo paints first on phones)")
    # assets and links
    for _i, tag, a in starts:
        urls = []
        if "src" in a:
            urls.append(a["src"])
        for key in ("srcset", "imagesrcset"):
            if key in a:
                urls += [c.strip().split()[0] for c in a[key].split(",") if c.strip()]
        if "poster" in a:
            urls.append(a["poster"])
        for u in urls:
            why = _url_ok(u, ctx)
            if why:
                p.append(f"asset: {why}")
        if tag == "a":
            href = a.get("href", "")
            if not (href.startswith("#") or (href.startswith("/") and not href.startswith("//"))):
                p.append(f"asset: <a href=\"{href}\"> — a mockup links to #… or /… only")
        if tag == "form" and a.get("action", "#")[:1] != "#":
            p.append(f"asset: <form action=\"{a['action']}\"> — a mockup form posts nowhere")
        if tag == "img":
            decorative = a.get("aria-hidden") == "true" or a.get("role") in ("presentation", "none")
            if "alt" in a and not a["alt"].strip() and decorative:
                pass    # alt="" marked decorative is the correct markup (learning loop, L9)
            elif not a.get("alt", "").strip():
                p.append(f"asset: <img src=\"{a.get('src', '')}\"> has no alt text (a decorative "
                         "image carries alt=\"\" with aria-hidden=\"true\" or role=\"presentation\")")
            elif a.get("src", "").startswith("/images/"):
                name = served_name(a["src"][len("/images/"):], ctx.served_alts)
                served = ctx.served_alts.get(name)
                if served and " ".join(a["alt"].split()) not in served:
                    p.append(f"asset: {name} is a served image and keeps its served alt word for "
                             f"word (working rule 11), not {a['alt']!r}")
            if not (a.get("width", "").isdigit() and a.get("height", "").isdigit()):
                p.append(f"asset: <img src=\"{a.get('src', '')}\"> needs numeric width and "
                         "height so its box is reserved")
    for m in CSS_URL.finditer(css):
        why = _url_ok(m.group(1), ctx)
        if why:
            p.append(f"asset: CSS {why}")
    # copy
    body = " ".join(_text(events).split())
    if "london" not in body.lower():
        p.append("copy: no mention of London — the placeholder copy is London-flavoured")
    for m in POUNDS.finditer(body):
        n = int(m.group(1).replace(",", ""))
        if n not in ctx.allowed_pounds:
            p.append(f"copy: £{m.group(1)} is not a price, the deposit or a delivery bound "
                     "from data/ (never invent a figure)")
    for m in PHONE.finditer(body):
        p.append(f"copy: {m.group(0)!r} looks like a phone number — write PHONE_PLACEHOLDER")
    for name in dict.fromkeys(named_parents(body)):
        if name not in ctx.parents:
            p.append(f"copy: {name!r} is named as a parent; data/faq.json names "
                     f"{sorted(ctx.parents)} (never invent a fact)")
    for rx in UNCONFIRMED_CLAIMS:
        for m in rx.finditer(body):
            p.append(f"copy: {m.group(0)!r} is a claim no file records — write only what "
                     "data/ confirms")
    low = text.lower()
    for marker in marker_check.MARKERS:
        if marker_check._present(marker, low):
            p.append(f"copy: {marker!r} is source-project text (scripts/marker_check.py)")
    for word in ctx.banned_words:
        if word in low:
            p.append(f"copy: {word!r} is reference-site text")
    if component == "reviews":
        for idx, tag, a in starts:
            if tag != "blockquote" or a.get("data-placeholder") == "review":
                continue
            n = a.get("data-review", "")
            if not (n.isdigit() and int(n) < len(ctx.reviews)):
                p.append("reviews: a <blockquote> is neither data-placeholder=\"review\" nor "
                         "data-review=\"<n>\" quoting data/reviews.json — never invent a review")
                continue
            end = next((j for j in range(idx + 1, len(events))
                        if events[j][0] == "end" and events[j][1] == "blockquote"), len(events))
            quote = " ".join(_text(events[idx + 1:end]).split())
            if ctx.reviews[int(n)][:60] not in quote:
                p.append(f"reviews: data-review=\"{n}\" does not quote data/reviews.json[{n}] "
                         "word for word")
    return p


def validate_meta(component, meta, ctx):
    """([problem], {variant: axes}) for one component's meta.json."""
    p, axes = [], {}
    if meta.get("component") != component:
        p.append(f"meta: \"component\" must be {component!r}")
    variants = meta.get("variants") or {}
    if sorted(variants) != list(VARIANT_IDS):
        p.append(f"meta: \"variants\" must hold exactly {list(VARIANT_IDS)}")
    cited = ctx.ideas.get(component, "")
    for v in VARIANT_IDS:
        row = variants.get(v) or {}
        name, desc = row.get("name", ""), row.get("description", "")
        if not (isinstance(name, str) and 0 < len(name) <= 60):
            p.append(f"meta {v}: name is 1–60 characters")
        if not (isinstance(desc, str) and 0 < len(desc) <= 160 and "\n" not in desc):
            p.append(f"meta {v}: description is one line of 1–160 characters")
        srcs = row.get("idea_sources")
        if not (isinstance(srcs, list) and srcs):
            p.append(f"meta {v}: idea_sources lists at least one source")
        else:
            for s in srcs:
                if not isinstance(s, str) or s not in cited:
                    p.append(f"meta {v}: idea source {s!r} is not cited under ## {component} "
                             "in the ideas index")
        diff = row.get("differs_from", "")
        if not (isinstance(diff, str) and len(diff.strip()) >= 20):
            p.append(f"meta {v}: differs_from says how it differs (20+ characters)")
        ax = row.get("axes") or {}
        if sorted(ax) != sorted(AXES):
            p.append(f"meta {v}: axes must be exactly {list(AXES)}")
            continue
        if not (isinstance(ax["layout"], str) and LAYOUT_SLUG.match(ax["layout"])):
            p.append(f"meta {v}: axes.layout {ax['layout']!r} is not a short slug")
        for k, allowed in VOCAB.items():
            if ax[k] not in allowed:
                p.append(f"meta {v}: axes.{k} {ax[k]!r} is not one of {list(allowed)}")
        axes[v] = ax
    for i, a in enumerate(VARIANT_IDS):
        for b in VARIANT_IDS[i + 1:]:
            if a in axes and b in axes and axis_distance(axes[a], axes[b]) < 2:
                p.append(f"axes: siblings {a} and {b} differ on fewer than 2 axes")
    for v, ax in axes.items():
        for row in ctx.must_differ.get(component, []):
            if axis_distance(ax, row["axes"]) < 2:
                p.append(f"axes: {v} is within one axis of existing style {row['id']} "
                         f"({row['name']}) — see docs/research/london-components/must-differ.md")
    return p, axes


def validate_canvas(root, ctx, only=None):
    """(problems, fragments examined, metas examined). `only` limits the components judged;
    without it the canvas must hold all fifteen and nothing else."""
    root = pathlib.Path(root)
    problems, n_frag, n_meta = [], 0, 0
    wanted = list(only) if only else list(COMPONENT_IDS)
    if not only:
        present = sorted(d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith(("_", "."))) \
            if root.is_dir() else []
        for extra in sorted(set(present) - set(COMPONENT_IDS)):
            problems.append(f"{extra}: not one of the fifteen city components")
    for cid in wanted:
        d = root / cid
        if not d.is_dir():
            problems.append(f"{cid}: missing — design/city-canvas/<city>/{cid}/ does not exist")
            continue
        files = sorted(f.name for f in d.iterdir() if f.is_file() and not f.name.startswith("."))
        want = sorted([f"{v}.html" for v in VARIANT_IDS] + ["meta.json"])
        if files != want:
            problems.append(f"{cid}: holds {files}, expected exactly {want}")
        for v in VARIANT_IDS:
            f = d / f"{v}.html"
            if f.is_file():
                n_frag += 1
                problems += [f"{cid}/{v}.html: {x}" for x in
                             validate_fragment(cid, v, f.read_text(encoding="utf-8"), ctx)]
        m = d / "meta.json"
        if m.is_file():
            n_meta += 1
            try:
                meta = json.loads(m.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                problems.append(f"{cid}/meta.json: {e}")
                continue
            problems += [f"{cid}/meta.json: {x}" for x in validate_meta(cid, meta, ctx)[0]]
    return problems, n_frag, n_meta


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate a city component canvas.")
    ap.add_argument("--city", default="london")
    ap.add_argument("--only", help="comma-separated component ids")
    a = ap.parse_args(argv)
    only = [c.strip() for c in a.only.split(",")] if a.only else None
    if only and set(only) - set(COMPONENT_IDS):
        ap.error(f"unknown component(s): {sorted(set(only) - set(COMPONENT_IDS))}")
    root = CANVAS_ROOT / a.city
    problems, n_frag, n_meta = validate_canvas(root, default_context(), only)
    for x in problems:
        print(f"  FAIL {x}")
    print(f"check-city-canvas {a.city}: examined {n_frag} fragments, {n_meta} meta files; "
          f"{len(problems)} problems")
    if n_frag == 0:
        print("examined 0 fragments — not a pass")
        return 1
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
