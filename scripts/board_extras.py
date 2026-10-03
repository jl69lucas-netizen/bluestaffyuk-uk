#!/usr/bin/env python3
"""Board blocks 2b, 8a, 8b and 8c — the four the breeder asked for (answer board q12,
2026-10-02, "add all four"):

  2b  How the result could look in Google: the picked title and description at desktop (600px)
      and mobile (360px) result widths, truncated by PIXEL width from a pinned Arial table.
  8a  Structured data the page will emit: a preview JSON-LD graph built from data files only.
  8b  Internal links in and out: out from the record, in from dist/ read with an HTML parser.
  8c  Page weight and LCP budget: the bytes of the images the board places, per section.

Rule 9: nothing here is invented. A value no file holds prints its placeholder or
`NOT FETCHED — <barrier>`. There is no host and no domain until project 6, so every URL is
built on `https://SITE_URL_PLACEHOLDER`, exactly as src/lib/site.ts builds it.

Pure functions returning markdown, like scripts/serp_reading.py and scripts/neighbourhoods.py;
scripts/build_page_board.py appends them on project 5 boards only.

    python3 scripts/board_extras.py <slug>      # prints the four blocks

Python 3.9 stdlib only.
"""
import html as H
import json
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB  # noqa: E402
import image_candidates as IC  # noqa: E402
from _slugs import resolve_page  # noqa: E402

ROOT = PB.ROOT
SITE_URL = "https://SITE_URL_PLACEHOLDER"      # src/lib/site.ts's default, until project 6

# ── 2b: the Google result preview ───────────────────────────────────────────────────────
#: Arial advance widths, units per 1000 em (Arial is metric-compatible with Helvetica, whose
#: AFM these are). Pinned so a board renders the same widths on every machine; a character
#: not listed is measured as DEFAULT_W, the width of a digit.
ARIAL = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667, "'": 191,
    "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278,
    ":": 278, ";": 278, "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015,
    "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556, "`": 333,
    "{": 334, "|": 260, "}": 334, "~": 584,
    "–": 556, "—": 1000, "£": 556, "’": 222, "‘": 222, "“": 333, "”": 333, "…": 1000,
    "·": 278, "×": 584, "›": 584, "€": 556,
    **{d: 556 for d in "0123456789"},
    "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278,
    "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778, "P": 667, "Q": 778, "R": 722,
    "S": 667, "T": 611, "U": 722, "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556, "h": 556, "i": 222,
    "j": 222, "k": 500, "l": 222, "m": 833, "n": 556, "o": 556, "p": 556, "q": 556, "r": 333,
    "s": 500, "t": 278, "u": 556, "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
}
DEFAULT_W = 556
ELLIPSIS = "…"

DESKTOP_W, MOBILE_W = 600, 360           # the result widths the mocks are drawn at
TITLE_PX, TITLE_SIZE = 600, 20           # desktop title: one line, 20px Arial
MOBILE_TITLE_SIZE, MOBILE_LINES = 16, 2  # mobile title: about two lines at 16px
MOBILE_LINE_PX = MOBILE_W - 2 * 16       # 360px result, 16px padding each side
DESC_PX, DESC_SIZE = 920, 14             # description: about 920px in all, two lines at 14px

APPROX_LABEL = ("Approximation. Google may rewrite titles and descriptions and decides "
                "truncation itself.")


def esc(v):
    return H.escape("" if v is None else str(v))


def md_cell(v):
    """A record value for a markdown table cell: HTML-escaped, pipes escaped."""
    return " ".join(esc(v).replace("|", "\\|").split())


def md_table(head, body):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in body]
    return "\n".join(out)


def text_px(text, size):
    """The rendered width of `text` in Arial at `size` px, from the pinned table."""
    return sum(ARIAL.get(ch, DEFAULT_W) for ch in str(text)) * size / 1000


def truncate(text, size, limit):
    """(shown, cut): the text as it fits in `limit` px, cut at a word with "…" when it does
    not fit. A first word wider than the limit is cut mid-word, as Google does."""
    text = " ".join(str(text).split())
    if text_px(text, size) <= limit:
        return text, False
    words, shown = text.split(" "), ""
    for w in words:
        cand = (shown + " " + w).strip()
        if text_px(cand + " " + ELLIPSIS, size) > limit:
            break
        shown = cand
    if not shown:                                       # one very long word
        for ch in text:
            if text_px(shown + ch + ELLIPSIS, size) > limit:
                break
            shown += ch
        return shown + ELLIPSIS, True
    return shown + " " + ELLIPSIS, True


def wrap(text, size, line_px, max_lines):
    """(lines, cut): greedy word wrap into lines of `line_px`; past `max_lines` the last line
    is truncated with "…"."""
    words, lines, cur = " ".join(str(text).split()).split(" "), [], ""
    for i, w in enumerate(words):
        cand = (cur + " " + w).strip()
        if cur and text_px(cand, size) > line_px:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                rest = " ".join([lines.pop()] + words[i:])
                last, _ = truncate(rest, size, line_px)
                return lines + [last], True
        else:
            cur = cand
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:                         # a single word wider than a line
        last, _ = truncate(" ".join(lines[max_lines - 1:]), size, line_px)
        return lines[:max_lines - 1] + [last], True
    return lines, False


def route_of(board, root=ROOT):
    """The page's built route, e.g. `uk-locations/blue-staffy-puppies-london`."""
    _, route = resolve_page(board.get("meta", {}).get("slug", ""), root)
    return route


def page_url(route):
    return SITE_URL + ("/" + route.strip("/") + "/" if route else "/")


def _settings(root):
    return json.loads((pathlib.Path(root) / "data/settings.json").read_text(encoding="utf-8"))


def fit_rows(board):
    """Every title and description option of block 2 with its pixel widths and fit."""
    ms = board["meta_set"]
    rows = []
    for i, t in enumerate(ms["titles"]):
        d = text_px(t, TITLE_SIZE)
        _, mcut = wrap(t, MOBILE_TITLE_SIZE, MOBILE_LINE_PX, MOBILE_LINES)
        rows.append({"kind": "title", "i": i, "text": t, "px": d, "limit": TITLE_PX,
                     "fits": d <= TITLE_PX, "mobile_fits": not mcut})
    for i, t in enumerate(ms["descriptions"]):
        d = text_px(t, DESC_SIZE)
        rows.append({"kind": "description", "i": i, "text": t, "px": d, "limit": DESC_PX,
                     "fits": d <= DESC_PX, "mobile_fits": d <= DESC_PX})
    return rows


def option_px(text, kind):
    """The short label block 2 prints beside an option: its desktop pixel width and fit."""
    if kind == "title":
        px, lim = text_px(text, TITLE_SIZE), TITLE_PX
    else:
        px, lim = text_px(text, DESC_SIZE), DESC_PX
    return f"{px:.0f} of {lim}px, {'fits' if px <= lim else 'cut'}"


def _crumb_line(route, site_name):
    parts = [SITE_URL] + [p for p in route.strip("/").split("/") if p]
    return esc(site_name), " › ".join(esc(p) for p in parts)


def serp_mock(board, root=ROOT):
    """The two result mocks, desktop then mobile, as one line of HTML each (no blank lines,
    so the board's markdown renderer passes them through)."""
    title, desc = PB.meta_pick(board)
    route = route_of(board, root)
    site, crumb = _crumb_line(route, _settings(root).get("site_name", ""))
    t_desk, _ = truncate(title, TITLE_SIZE, TITLE_PX)
    t_mob, _ = wrap(title, MOBILE_TITLE_SIZE, MOBILE_LINE_PX, MOBILE_LINES)
    d_shown, _ = truncate(desc, DESC_SIZE, DESC_PX)
    font = "font-family:Arial,sans-serif;"
    head = (f'<div style="{font}font-size:14px;color:#202124">{site}</div>'
            f'<div style="{font}font-size:12px;color:#4d5156;margin-bottom:4px">{crumb}</div>')
    desk = (f'<div class="serp serp-desktop" style="width:{DESKTOP_W}px;max-width:100%;padding:12px 0;'
            f'background:#fff;border:1px solid #dadce0;border-radius:8px;padding:12px 16px;box-sizing:content-box">'
            f'<div style="{font}font-size:12px;color:#70757a;margin-bottom:6px">Desktop · {DESKTOP_W}px</div>'
            f'{head}<div style="{font}font-size:{TITLE_SIZE}px;line-height:1.3;color:#1a0dab;white-space:nowrap">'
            f'{esc(t_desk)}</div><div style="{font}font-size:{DESC_SIZE}px;line-height:1.58;color:#4d5156">'
            f'{esc(d_shown)}</div></div>')
    mob = (f'<div class="serp serp-mobile" style="width:{MOBILE_LINE_PX}px;max-width:100%;padding:12px 16px;'
           f'background:#fff;border:1px solid #dadce0;border-radius:8px;margin-top:12px;box-sizing:content-box">'
           f'<div style="{font}font-size:12px;color:#70757a;margin-bottom:6px">Mobile · {MOBILE_W}px</div>'
           f'{head}<div style="{font}font-size:{MOBILE_TITLE_SIZE}px;line-height:1.35;color:#1a0dab">'
           f'{"<br>".join(esc(ln) for ln in t_mob)}</div>'
           f'<div style="{font}font-size:{DESC_SIZE}px;line-height:1.58;color:#4d5156">{esc(d_shown)}</div></div>')
    return desk + "\n" + mob


def serp_block(board, root=ROOT):
    title, desc = PB.meta_pick(board)
    ms = board["meta_set"]
    picked = ms["pick"]["title"] is not None or ms["pick"]["description"] is not None
    route = route_of(board, root)
    t_px, d_px = text_px(title, TITLE_SIZE), text_px(desc, DESC_SIZE)
    _, mcut = wrap(title, MOBILE_TITLE_SIZE, MOBILE_LINE_PX, MOBILE_LINES)
    out = [f"**{APPROX_LABEL}**", "",
           ("The breeder's picked title and description from block 2."
            if picked else "Block 2's recommended title and description (option 1 of each); "
                           "the preview follows the pick once one is made."),
           f"URL line: `{esc(page_url(route))}` — the site has no domain until project 6, so "
           "the placeholder is shown as it is.", "",
           serp_mock(board, root), "",
           md_table(["", "Width", "Limit", "Fits"], [
               ["Title, desktop (20px Arial)", f"{t_px:.0f}px", f"{TITLE_PX}px",
                "yes" if t_px <= TITLE_PX else "no — cut with …"],
               [f"Title, mobile (16px, {MOBILE_LINES} lines of {MOBILE_LINE_PX}px)",
                f"{text_px(title, MOBILE_TITLE_SIZE):.0f}px",
                f"{MOBILE_LINES} × {MOBILE_LINE_PX}px",
                "yes" if not mcut else "no — cut with …"],
               ["Description (14px, about two lines)", f"{d_px:.0f}px", f"{DESC_PX}px",
                "yes" if d_px <= DESC_PX else "no — cut with …"]]), "",
           "**Every option in block 2, by pixel width**", "",
           md_table(["Option", "Text", "Desktop width", "Fits desktop", "Fits mobile"], [
               [f"{r['kind']} {r['i'] + 1}", md_cell(r["text"]), f"{r['px']:.0f} of {r['limit']}px",
                "yes" if r["fits"] else "no", "yes" if r["mobile_fits"] else "no"]
               for r in fit_rows(board)]), "",
           f"Widths come from a pinned Arial table (`scripts/board_extras.py` `ARIAL`), "
           f"desktop title {TITLE_PX}px at {TITLE_SIZE}px, mobile title {MOBILE_LINES} lines of "
           f"{MOBILE_LINE_PX}px at {MOBILE_TITLE_SIZE}px, description {DESC_PX}px at {DESC_SIZE}px."]
    return "\n".join(out)


# ── 8a: structured data ─────────────────────────────────────────────────────────────────
SCHEMA_NOTE = ("Preview only — the built page's JSON-LD is produced by the site build and "
               "checked by `npm run check:schema`.")
#: Never emitted: seo-rules Rule 33 forbids AggregateRating, and no review markup is built
#: from anything but data/reviews.json — which this preview does not mark up at all.
REFUSED_TYPES = {"AggregateRating": "seo-rules Rule 33: no AggregateRating markup",
                 "Review": "seo-rules Rule 33: no review markup in the preview; data/reviews.json "
                           "rows are shown as letters, not marked up"}
NAV_RE = re.compile(r"\{\s*href:\s*'([^']+)',\s*label:\s*'([^']+)'\s*\}")
KEEP_LOWER = {"uk", "and", "of", "for", "in", "the"}
FAQ_Q = re.compile(r"^Q:\s*(.+?)\s+—\s")


def _title_case_slug(seg):
    """src/lib/site.ts titleCase, for a path segment."""
    return " ".join("UK" if w.lower() == "uk" else w.lower() if w.lower() in KEEP_LOWER
                    else w[:1].upper() + w[1:] for w in seg.split("-"))


def _nav(root):
    p = pathlib.Path(root) / "src/lib/site.ts"
    return dict(NAV_RE.findall(p.read_text(encoding="utf-8"))) if p.is_file() else {}


def _leaf_name(route, root):
    """The breadcrumb leaf: a city row's `h1 || city` (src/pages/uk-locations/[slug].astro),
    else the page-map title cut at its first ` | `, else the slug title-cased."""
    last = route.strip("/").rsplit("/", 1)[-1]
    locs = json.loads((pathlib.Path(root) / "data/locations.json").read_text(encoding="utf-8"))
    row = next((r for r in locs if isinstance(r, dict) and r.get("slug") == last), None)
    if row:
        return row.get("h1") or row.get("city") or _title_case_slug(last)
    pm = json.loads((pathlib.Path(root) / "data/page-map.json").read_text(encoding="utf-8"))
    prow = next((r for r in pm.get("pages", []) if str(r.get("url", "")).strip("/") == route.strip("/")), None)
    if prow and prow.get("title"):
        return re.split(r"\s+(?:\||—|–)\s+", prow["title"])[0].strip()
    return _title_case_slug(last)


def _crumbs(route, root):
    segs = [s for s in route.strip("/").split("/") if s]
    nav = _nav(root)
    out = [("Home", "/")]
    for i, seg in enumerate(segs):
        href = "/" + "/".join(segs[:i + 1]) + "/"
        out.append((_leaf_name(route, root) if i == len(segs) - 1
                    else nav.get(href, _title_case_slug(seg)), href))
    return out


def _tokens(s):
    """src/lib/faq.ts TOKENS, from data/settings.json."""
    label = s.get("guarantee_label", "")
    lower = label[:1].lower() + label[1:]
    noun = re.sub(r"^\S+-(?:year|day)\s+", "", lower, flags=re.I)
    phrase = f"{noun}, which {s['guarantee_cover']}," if s.get("guarantee_days") and s.get("guarantee_cover") else lower
    return {"deposit_gbp": str(s.get("deposit_gbp")), "delivery_min_gbp": str(s.get("delivery_min_gbp")),
            "delivery_max_gbp": str(s.get("delivery_max_gbp")), "delivery_note": s.get("delivery_note", ""),
            "deposit_terms": "refundable" if s.get("deposit_refundable") else "non-refundable",
            "guarantee_label_lc": lower, "guarantee_phrase": phrase}


def faq_rows(board, root=ROOT):
    """[(question, answer)] for every row the board's FAQ sections list, in order. A row
    data/faq.json holds is read with its tokens filled; one it does not yet hold takes its
    question from the record's intent and its answer is NOT FETCHED."""
    rows = json.loads((pathlib.Path(root) / "data/faq.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in rows}
    toks = _tokens(_settings(root))
    fill = lambda a: re.sub(r"\{([a-z_]+)\}", lambda m: toks.get(m.group(1), m.group(0)), a)
    out = []
    for s in board.get("sections", []):
        if s.get("shape") != "faq" and not s.get("questions"):
            continue
        for n in s.get("tree") or []:
            rid = n.get("heading", "")
            if rid in by_id:
                out.append((by_id[rid]["q"], fill(by_id[rid]["a"])))
                continue
            m = FAQ_Q.match(n.get("intent") or "")
            q = m.group(1) if m else f"NOT FETCHED — no question recorded for {rid}"
            out.append((q, f"NOT FETCHED — data/faq.json has no row `{rid}` yet "
                           "(written at build from the outline)"))
    return out


def schema_types(board):
    sch = (board.get("brief") or {}).get("schema") or {}
    return list(sch.get("types") or []) if isinstance(sch, dict) else []


def jsonld_graph(board, root=ROOT):
    """The preview graph, one node per planned type, from data files only — the field names
    src/components/Schema.astro and src/pages/available-puppies/[slug].astro emit."""
    root = pathlib.Path(root)
    s = _settings(root)
    route = route_of(board, root)
    url = page_url(route)
    types = schema_types(board)
    want = lambda t: t in types
    graph = []
    addr_in = s.get("address") or {}
    ki16 = "NOT FETCHED — the breeder has supplied no {} for the new place (Known Issue 16)"
    if want("LocalBusiness"):
        graph.append({
            "@context": "https://schema.org", "@type": "LocalBusiness", "@id": f"{SITE_URL}/#business",
            "name": s.get("site_name"), "url": SITE_URL, "email": s.get("email"),
            "telephone": s.get("phone"), "priceRange": s.get("price_range"),
            "address": {"@type": "PostalAddress", "addressLocality": addr_in.get("city"),
                        "addressRegion": addr_in.get("region"),
                        "addressCountry": addr_in.get("country"),
                        "streetAddress": addr_in.get("street") or ki16.format("street"),
                        "postalCode": addr_in.get("postcode") or ki16.format("postcode")},
            "openingHours": s.get("hours"),
            "sameAs": list((s.get("socials") or {}).values()) if isinstance(s.get("socials"), dict) else [],
        })
    if want("Person"):
        graph.append({"@context": "https://schema.org", "@type": "Person", "@id": f"{SITE_URL}/#breeder",
                      "name": s.get("breeder_name"), "worksFor": {"@id": f"{SITE_URL}/#business"},
                      "address": {"@type": "PostalAddress", "addressLocality": addr_in.get("city"),
                                  "addressRegion": addr_in.get("region"),
                                  "addressCountry": addr_in.get("country")}})
    if want("BreadcrumbList"):
        graph.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                      "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                                           "item": SITE_URL + h}
                                          for i, (n, h) in enumerate(_crumbs(route, root))]})
    if want("Product") or want("Offer"):
        pups = json.loads((root / "data/puppies.json").read_text(encoding="utf-8"))
        pm = json.loads((root / "data/price-matrix.json").read_text(encoding="utf-8"))
        for p in (p for p in pups if p.get("status") == "Available"):
            price = p.get("price_gbp")
            matrix = pm.get(f"{p.get('sex')}_gbp")
            graph.append({"@context": "https://schema.org", "@type": "Product",
                          "@id": f"{url}#puppy-{p['slug']}", "name": f"{p['name']} – Blue Staffy puppy",
                          "image": f"{SITE_URL}/images/puppies/{p['slug']}-card-800.webp",
                          "brand": {"@type": "Brand", "name": s.get("site_name")},
                          "offers": {"@type": "Offer",
                                     "price": str(price if price is not None else matrix),
                                     "priceCurrency": pm.get("currency", "GBP"),
                                     "availability": "https://schema.org/InStock",
                                     "url": f"{SITE_URL}/available-puppies/{p['slug']}/",
                                     "seller": {"@id": f"{SITE_URL}/#business"}}})
    if want("FAQPage"):
        graph.append({"@context": "https://schema.org", "@type": "FAQPage", "@id": f"{url}#faq",
                      "mainEntity": [{"@type": "Question", "name": q,
                                      "acceptedAnswer": {"@type": "Answer", "text": a}}
                                     for q, a in faq_rows(board, root)]})
    return graph


def schema_block(board, root=ROOT):
    types = schema_types(board)
    graph = jsonld_graph(board, root)
    built = sorted({n["@type"] for n in graph} | ({"Offer"} if any(n["@type"] == "Product" for n in graph) else set()))
    refused = [t for t in types if t in REFUSED_TYPES]
    unknown = [t for t in types if t not in built and t not in REFUSED_TYPES]
    out = [f"**{SCHEMA_NOTE}**", "",
           f"The brief plans: {', '.join('`' + esc(t) + '`' for t in types) or '_no schema plan recorded_'}"
           f" (offer model: `{esc(((board.get('brief') or {}).get('schema') or {}).get('offer_model', 'not recorded'))}`).",
           f"This preview emits: {', '.join('`' + t + '`' for t in built) or 'nothing'}.", ""]
    for t in refused:
        out.append(f"- `{esc(t)}` is not emitted — {REFUSED_TYPES[t]}.")
    for t in unknown:
        out.append(f"- `{esc(t)}` — NOT FETCHED: no data file this preview reads describes it.")
    out += ["- No `AggregateRating` and no review markup (seo-rules Rule 33).",
            "- `telephone` prints `PHONE_PLACEHOLDER` and the street and postcode print NOT FETCHED: "
            "the build leaves those fields out until the breeder supplies them (src/components/Schema.astro).",
            "- Sources: `data/settings.json`, `data/puppies.json`, `data/price-matrix.json`, "
            "`data/faq.json` (the rows the FAQ sections list), the route for the breadcrumb.", "",
            "```json", json.dumps(graph, indent=2, ensure_ascii=False).replace("</", "<\\/"), "```"]
    return "\n".join(out)


# ── 8b: internal links ──────────────────────────────────────────────────────────────────
SPECIMENS = ("board-preview", "kit-preview")
HOST = re.compile(r"^https?://[^/]+")
ORPHAN_FLOOR = 3


def norm_route(href):
    path = urlsplit(HOST.sub("", str(href or "").strip())).path
    if not path.startswith("/"):
        return None
    return "/" + path.strip("/") + "/" if path.strip("/") else "/"


def links_out(board):
    out = []
    for s in board.get("sections", []):
        for l in (s.get("links") or {}).get("internal") or []:
            out.append({"href": l["href"], "anchor": l.get("anchor", ""),
                        "section": f"{s['n']:02d} {s['heading']}"})
    return out


class _Anchors(HTMLParser):
    """Every <a href> with its text, and whether it sits inside <main>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main, self.cur, self.found = 0, None, []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.main += 1
        elif tag == "a":
            a = dict(attrs)
            href = a.get("href")
            self.cur = ({"href": href, "text": [], "label": (a.get("aria-label") or "").strip(),
                         "in_main": self.main > 0} if href else None)
        elif tag == "img" and self.cur is not None:
            # An image link's anchor text is its alt, as a search engine reads it.
            alt = (dict(attrs).get("alt") or "").strip()
            if alt:
                self.cur["text"].append(f" [image: {alt}] ")

    def handle_endtag(self, tag):
        if tag == "main":
            self.main = max(0, self.main - 1)
        elif tag == "a" and self.cur is not None:
            self.cur["text"] = " ".join("".join(self.cur["text"]).split())
            if not self.cur["text"] and self.cur["label"]:
                # An empty link named only by aria-label: the label is all a reader hears.
                self.cur["text"] = f"[aria-label: {self.cur['label']}]"
            self.found.append(self.cur)
            self.cur = None

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self.cur is not None:
            self.cur["text"].append(data)


def links_in(route, dist):
    """([{source, anchor}], chrome_pages): links to /<route>/ from inside other built pages'
    <main>, and how many other pages link it only from the site chrome (header and footer),
    which links every city from every page and is not counted (as scripts/page_intake.py)."""
    dist = pathlib.Path(dist)
    target = "/" + route.strip("/") + "/" if route.strip("/") else "/"
    own = (dist / route / "index.html") if route else dist / "index.html"
    rows, chrome = [], 0
    for page in sorted(dist.rglob("*.html")):
        rel = page.relative_to(dist).as_posix()
        if page == own or rel.split("/", 1)[0] in SPECIMENS:
            continue
        p = _Anchors()
        p.feed(page.read_text(encoding="utf-8", errors="ignore"))
        hits = [a for a in p.found if norm_route(a["href"]) == target]
        src = "/" + rel[:-len("index.html")] if rel.endswith("index.html") else "/" + rel
        main_hits = [a for a in hits if a["in_main"]]
        for a in main_hits:
            rows.append({"source": src, "anchor": a["text"]})
        if hits and not main_hits:
            chrome += 1
    return rows, chrome


def links_block(board, root=ROOT, dist=None):
    dist = pathlib.Path(dist) if dist is not None else pathlib.Path(root) / "dist"
    route = route_of(board, root)
    outs = links_out(board)
    lines = [f"**Out — {len(outs)} internal link{'s' if len(outs) != 1 else ''} this board plans** "
             "(block 3's link tables, from the record)", ""]
    lines.append(md_table(["Target", "Anchor", "Section"],
                          [[f"`{md_cell(o['href'])}`", md_cell(o["anchor"]), md_cell(o["section"])]
                           for o in outs]) if outs else "_No internal links planned._")
    lines += ["", f"**In — built pages that link to `/{esc(route)}/`**", ""]
    if not dist.is_dir():
        lines.append("NOT FETCHED — dist/ not built (npm run build)")
        return "\n".join(lines)
    rows, chrome = links_in(route, dist)
    sources = sorted({r["source"] for r in rows})
    lines.append(md_table(["Source page", "Anchor"],
                          [[f"`{md_cell(r['source'])}`", md_cell(r["anchor"]) or "_no text_"]
                           for r in rows]) if rows else "_No built page links here from its body._")
    lines += ["", f"Counts: **{len(outs)} out** · **{len(rows)} in** from {len(sources)} "
                  f"page{'s' if len(sources) != 1 else ''}' `<main>` (read from `dist/` with an HTML "
                  f"parser) · {chrome} more page{'s' if chrome != 1 else ''} link it only from the "
                  "site header or footer, which is not counted."]
    if len(sources) < ORPHAN_FLOOR:
        lines.append(f"\n**Orphan risk:** {len(sources)} page{'s' if len(sources) != 1 else ''} "
                     f"link here from body copy — under {ORPHAN_FLOOR}. Plan links in from the hub "
                     "and sibling pages.")
    return "\n".join(lines)


# ── 8c: page weight ─────────────────────────────────────────────────────────────────────
NOT_BAKED = "not baked — size after STOP 4"




def budget_source(root=ROOT):
    """What the repo itself states about page weight and LCP, each with its line. Read at run
    time, so a moved line moves the citation. No page-weight or LCP-time number exists today,
    and none is supplied here."""
    root = pathlib.Path(root)
    probes = [("scripts/perf_audit.py", "THRESHOLDS = {c: 0.995",
               "Lighthouse category floors only (every category 0.995) — a score, not bytes or ms"),
              ("scripts/bake_images.py", "MAX_KB = 95",
               "the bake budget per image: 95 KB, where 1 KB is 1,024 bytes"),
              ("rules/images.md", "<100 KB WebP + -760.webp",
               "each in-body image ships as a <100 KB WebP plus its -760 sibling")]
    cites = []
    for path, needle, what in probes:
        p = root / path
        line = None
        if p.is_file():
            for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if needle in ln:
                    line = i
                    break
        if line:
            cites.append({"path": path, "line": line, "needle": needle, "what": what})
    design = root / "rules/design.md"
    design_hit = None
    if design.is_file():
        for i, ln in enumerate(design.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\b\d+\s?KB\b|\bLCP\b|page weight", ln, re.I):
                design_hit = i
                break
    per_image = 95 * 1024 if any(c["path"] == "scripts/bake_images.py" for c in cites) else None
    return {"cites": cites, "design_line": design_hit, "per_image_bytes": per_image,
            "page_budget_bytes": None, "lcp_budget_ms": None}


def _manifest(root):
    p = pathlib.Path(root) / "data/image-manifest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def weight_rows(board, root=ROOT):
    """One row per image slot the board places, with the file's bytes and its -760 sibling's
    when data/image-manifest.json records one (`sib_w`)."""
    root = pathlib.Path(root)
    man = _manifest(root)
    assets = {a["slot"]: a for a in board.get("assets", [])}
    rows = []
    for sec, node, img in IC.iter_slots(board):
        slot = img.get("slot", "")
        kind = img.get("kind", "photo")
        file = img.get("file") or (assets.get(slot) or {}).get("file")
        row = {"section": f"{sec['n']:02d} {sec['heading']}", "n": sec["n"], "slot": slot,
               "kind": kind, "file": file, "bytes": None, "sib": None, "sib_bytes": None,
               "note": ""}
        if not file:
            row["note"] = NOT_BAKED if kind == "infographic" else "NOT FETCHED — no file recorded"
            rows.append(row)
            continue
        path = root / "public" / file.lstrip("/")
        if not path.is_file():
            row["note"] = f"NOT FETCHED — {file} is not under public/"
            rows.append(row)
            continue
        row["bytes"] = path.stat().st_size
        stem = path.stem
        if (man.get(stem) or {}).get("sib_w"):
            sib = path.with_name(f"{stem}-{man[stem]['sib_w']}{path.suffix}")
            if sib.is_file():
                row["sib"] = "/" + sib.relative_to(root / "public").as_posix()
                row["sib_bytes"] = sib.stat().st_size
        rows.append(row)
    return rows


def _kb(n):
    return "—" if n is None else f"{n / 1024:.1f} KB"


def weight_block(board, root=ROOT):
    rows = weight_rows(board, root)
    src = budget_source(root)
    out = []
    # The budget, cited or declared absent.
    out.append("**Budget.** No page-weight or LCP-time budget is stated in `scripts/perf_audit.py` "
               "or `rules/design.md`" + (f" (rules/design.md line {src['design_line']} mentions one — read it)"
                                         if src["design_line"] else "")
               + ", so this block sets no page-total budget and no LCP target; it measures and shows the bytes. What the repo does state:")
    for c in src["cites"]:
        out.append(f"- `{c['path']}:{c['line']}` — {c['what']}.")
    out.append("")
    per = src["per_image_bytes"]
    # The LCP candidate: the hero section's first image.
    hero = next((r for r in rows if r["kind"] == "photo" and r["bytes"] is not None
                 and any(s.get("shape") == "hero" and s["n"] == r["n"] for s in board["sections"])), None)
    if hero:
        out.append(f"**LCP candidate:** the hero image `{esc(hero['file'])}` — {_kb(hero['bytes'])} "
                   f"({hero['bytes']:,} bytes)" + (f"; phones get `{esc(hero['sib'])}` at "
                                                   f"{_kb(hero['sib_bytes'])} ({hero['sib_bytes']:,} bytes)"
                                                   if hero["sib"] else "") + ".")
    else:
        out.append("**LCP candidate:** NOT FETCHED — the board places no hero image with a file.")
    out.append("")
    body = []
    for r in rows:
        size = NOT_BAKED if r["note"] == NOT_BAKED else (r["note"] or f"{_kb(r['bytes'])}")
        over = per is not None and r["bytes"] is not None and r["bytes"] > per
        body.append([md_cell(r["section"]), f"`{md_cell(r['slot'])}`", r["kind"],
                     f"`{md_cell(r['file'])}`" if r["file"] else "—", size + (" ⚠ over 95 KB" if over else ""),
                     _kb(r["sib_bytes"]) if r["sib"] else "no sibling"])
    out.append(md_table(["Section", "Slot", "Kind", "File", "Bytes", "-760 sibling"], body)
               if body else "_No image slots on this board._")
    out.append("")
    # Per section: the distinct files placed there.
    secs, order = {}, []
    for r in rows:
        if r["section"] not in secs:
            secs[r["section"]] = {"full": {}, "phone": {}, "pending": 0}
            order.append(r["section"])
        e = secs[r["section"]]
        if r["bytes"] is None:
            e["pending"] += 1
            continue
        e["full"][r["file"]] = r["bytes"]
        e["phone"][r["file"]] = r["sib_bytes"] if r["sib"] else r["bytes"]
    out.append(md_table(["Section", "Images (largest files)", "Images (phone, -760 where served)", "Not baked"],
                        [[md_cell(k), _kb(sum(secs[k]["full"].values())), _kb(sum(secs[k]["phone"].values())),
                          str(secs[k]["pending"]) if secs[k]["pending"] else "—"] for k in order]))
    full, phone = {}, {}
    for r in rows:
        if r["bytes"] is not None:
            full[r["file"]] = r["bytes"]
            phone[r["file"]] = r["sib_bytes"] if r["sib"] else r["bytes"]
    pending = sum(1 for r in rows if r["note"] == NOT_BAKED)
    out += ["", f"**Page total (images, each file once):** {_kb(sum(full.values()))} "
                f"({sum(full.values()):,} bytes) at full size · {_kb(sum(phone.values()))} "
                f"({sum(phone.values()):,} bytes) where the -760 sibling is served"
                + (f" · plus {pending} infographic{'s' if pending != 1 else ''} {NOT_BAKED}" if pending else "")
                + ". Images only: HTML, CSS, fonts and the video facade are not counted here."]
    return "\n".join(out)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python3 scripts/board_extras.py <slug>", file=sys.stderr)
        return 2
    path = ROOT / "data/boards" / f"{PB.slug_file(argv[0]) if hasattr(PB, 'slug_file') else argv[0]}.json"
    if not path.is_file():
        print(f"no board at {path}", file=sys.stderr)
        return 2
    board = json.loads(path.read_text(encoding="utf-8"))
    for title, fn in (("2b", serp_block), ("8a", schema_block), ("8b", links_block), ("8c", weight_block)):
        print(f"## {title}\n\n{fn(board, ROOT)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
