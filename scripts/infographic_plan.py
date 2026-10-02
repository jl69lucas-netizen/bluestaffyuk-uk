#!/usr/bin/env python3
"""infographic_plan.py — board block 7c, "Infographics": which sections need one, which IG
type, and three rendered styles of each for the breeder to pick from.

    python3 scripts/infographic_plan.py <slug>            # print the plan table
    python3 scripts/infographic_plan.py <slug> --write    # ...and write the previews

The IG types are the bsuk-infographic skill's (IMAGE-DESIGNS.md §8). A section gets an
infographic when its H2 heading or one of its H3 headings matches TRIGGERS; the IG types are
tried in TRIGGERS order and the first that matches any heading wins, so a delivery heading
that also says "cost" is a route (IG-5), not a price panel. Frame sections (hero, counter,
trust, contents, takeaways, reviews, FAQ blocks, newsletter, form) never get one. An
infographic slot already on the board (an `images` entry of kind "infographic" on the section
or a tree node, or an asset naming its `section`) keeps its slot id and IG type.

Every figure comes from data/settings.json, data/price-matrix.json, data/puppies.json or
data/locations.json, or is the section's own outline text (heading, H3s, the slot prompt).
A fact the data does not hold is written `NOT FETCHED — <file> <key> missing` and rendered
visibly (class "nf"), never guessed (CLAUDE.md rule 9). The deposit is only ever qualified by
settings `deposit_refund_clause`, never called plainly refundable.

Three styles per slot, the same content on the same tokens (src/styles/tokens.css):
  plate  steel band, large Fraunces figures, bone text           (pairs with city-price-scale)
  ruled  hairline rules on bone, ledger rhythm, tabular figures  (pairs with city-faq-ledger)
  card   white cards, steel accent rail, a line icon per item    (pairs with city-chapters)

Previews are standalone HTML at docs/artifacts/boards/ig/<slug>/<slot>-<style>.html. Board
Task 7 embeds them as iframes with one radio group per slot named `pick-ig:<slot>` (the pick
signature is `ig:<slot>`), so approval waits until every slot's style is chosen.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TRIGGERS = [
    ("IG-5", r"\bdeliver|\bcollect|\bfrom carlisle\b|\btravel"),
    ("IG-1", r"\bcost|\bprice|\bhow much\b|£"),
    ("IG-3", r"\bvs\b|\bversus\b|\bdifference\b|\bor (american|pit)"),
    ("IG-2", r"\bdeposit\b|\bsteps?\b|\bhow to\b|\bprocess\b|\btimeline\b"),
    ("IG-4", r"\bchecklist\b|\bwhat to check\b|\bpaperwork\b|\bhealth test"),
]
IG_NAMES = {"IG-1": "Stat Panel", "IG-2": "Process Steps", "IG-3": "Comparison Split",
            "IG-4": "Checklist Grid", "IG-5": "Route Map"}
SLOT_SUFFIX = {"IG-1": "figures", "IG-2": "steps", "IG-3": "split", "IG-4": "checklist",
               "IG-5": "route"}
STYLES = [{"id": "plate", "label": "Plate"}, {"id": "ruled", "label": "Ruled"},
          {"id": "card", "label": "Card"}]
FRAME_SHAPES = {"hero", "stats", "trust", "dial", "takeaways", "reviews", "faq", "form"}
FRAME_IDS = {"top", "hero", "counter", "trust", "contents", "key-takeaways", "takeaways",
             "newsletter", "enquiry", "form"}
NF = "NOT FETCHED"
OUT_DIR = "docs/artifacts/boards/ig"


def esc(s) -> str:
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- plan

def _is_frame(sec: dict) -> bool:
    sid = sec.get("id", "")
    return (sid.startswith(("faq-", "review-")) or sid in FRAME_IDS
            or sec.get("shape") in FRAME_SHAPES
            or "newsletter" in (sec.get("component") or ""))


def _h2_h3(sec: dict) -> list[str]:
    """The H2 heading, then every H3 (top-level tree node) heading."""
    out = [sec.get("heading", "")]
    for n in sec.get("tree") or []:
        if n.get("level", 3) == 3:
            out.append(n.get("heading") or n.get("text") or "")
    return out


def _all_headings(sec: dict) -> list[str]:
    out, stack = [], list(sec.get("tree") or [])
    while stack:
        n = stack.pop(0)
        out.append(n.get("heading") or n.get("text") or "")
        stack[:0] = n.get("children") or []
    return out


def match(texts: list[str]):
    """(ig, pattern-hit, text) for the first IG in TRIGGERS order any text matches."""
    for ig, pat in TRIGGERS:
        for t in texts:
            m = re.search(pat, t.lower())
            if m:
                return ig, m.group(0), t
    return None


def _existing(sec: dict, board: dict) -> dict | None:
    for img in sec.get("images") or []:
        if img.get("kind") == "infographic":
            return {**img, "_node": sec.get("heading", "")}
    stack = list(sec.get("tree") or [])
    while stack:
        n = stack.pop(0)
        for img in n.get("images") or []:
            if img.get("kind") == "infographic":
                return {**img, "_node": n.get("heading") or n.get("text") or ""}
        stack[:0] = n.get("children") or []
    for a in board.get("assets") or []:
        if a.get("kind") == "infographic" and a.get("section") == sec.get("id"):
            return {**a, "_node": sec.get("heading", "")}
    return None


def _slug(board: dict) -> str:
    return (board.get("meta") or {}).get("slug") or board.get("slug") or "page"


def plan(board: dict, root: Path | None = ROOT) -> list[dict]:
    """[{section, slot, ig, heading, node, why, styles, facts, alt, prompt, page}].

    `root` is where data/ is read from; root=None plans without facts."""
    out = []
    assets = {a.get("slot"): a for a in board.get("assets") or []}
    taken = set(assets)
    for sec in board.get("sections") or []:
        if _is_frame(sec):
            continue
        ex = _existing(sec, board)
        if ex:
            asset = assets.get(ex.get("slot"), {})
            p = {"section": sec["id"], "slot": ex["slot"],
                 "ig": ex.get("infographic_style") or asset.get("infographic_style"),
                 "node": ex["_node"], "why": "infographic slot already on the board",
                 "prompt": ex.get("prompt") or asset.get("prompt") or "",
                 "alt": asset.get("alt") or ex.get("alt") or ""}
        else:
            hit = match(_h2_h3(sec))
            if not hit:
                continue
            ig, word, text = hit
            level = "H2" if text == sec.get("heading", "") else "H3"
            slot = f"{sec['id']}-{SLOT_SUFFIX[ig]}"
            while slot in taken:
                slot += "-ig"
            p = {"section": sec["id"], "slot": slot, "ig": ig, "node": text,
                 "why": f'"{word}" in the {level} "{text}"', "prompt": "", "alt": ""}
        taken.add(p["slot"])
        p.update(heading=sec.get("heading", ""), page=_slug(board),
                 styles=[dict(s) for s in STYLES], _sec=sec)
        p["facts"] = facts_for(p, root) if root is not None else {}
        if not p["alt"]:
            p["alt"] = _alt(p)
        p.pop("_sec")
        out.append(p)
    return out


# ---------------------------------------------------------------- facts

def _load(root: Path, name: str):
    f = Path(root) / "data" / name
    try:
        return json.loads(f.read_text())
    except (OSError, ValueError):
        return None


def _nf(file: str, key: str) -> str:
    return f"{NF} — data/{file} {key} missing"


def _get(d, file: str, *keys):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or cur.get(k) in (None, ""):
            return _nf(file, ".".join(keys))
        cur = cur[k]
    return cur


def _gbp(v) -> str:
    return f"£{v:,}" if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v)


def _band(lo, hi) -> str:
    if isinstance(lo, str):
        return lo
    if isinstance(hi, str):
        return hi
    return f"{_gbp(lo)}–{_gbp(hi)}"


def _section(slot_plan: dict, root) -> dict:
    sec = slot_plan.get("_sec")
    if sec is None and root is not None:
        board = _load(root, f"boards/{slot_plan.get('page')}.json") or {}
        sec = next((s for s in board.get("sections") or []
                    if s.get("id") == slot_plan.get("section")), {})
    return sec or {"heading": slot_plan.get("heading", ""), "tree": []}


def _steps_from_prompt(prompt: str) -> list[str]:
    if "→" not in prompt:
        return []
    parts = [p.strip() for p in prompt.split("→")]
    parts[0] = re.split(r"[—:]", parts[0])[-1].strip()
    parts[-1] = re.split(r"[(.]", parts[-1])[0].strip()
    return [p for p in parts if p]


def facts_for(slot_plan: dict, root) -> dict:
    """The slot's facts, read only from data/ under `root` and the section's outline text."""
    root = Path(root)
    st = _load(root, "settings.json") or {}
    pm = _load(root, "price-matrix.json") or {}
    pups = _load(root, "puppies.json")
    locs = _load(root, "locations.json") or []
    sec = _section(slot_plan, root)
    ig = slot_plan.get("ig")
    city = _get(st, "settings.json", "address", "city")
    deposit = _gbp(_get(st, "settings.json", "deposit_gbp"))
    clause = _get(st, "settings.json", "deposit_refund_clause")
    band = _band(_get(st, "settings.json", "delivery_min_gbp"),
                 _get(st, "settings.json", "delivery_max_gbp"))
    dnote = _get(st, "settings.json", "delivery_note")
    title = slot_plan.get("node") or sec.get("heading", "")
    src = {"settings": "data/settings.json", "matrix": "data/price-matrix.json",
           "puppies": "data/puppies.json", "outline": "the section's outline headings"}

    if ig == "IG-5":
        dest = next((l.get("city") for l in locs if l.get("slug") == slot_plan.get("page")),
                    None) or _nf("locations.json", f"{slot_plan.get('page')}.city")
        return {"title": title, "origin": city, "destination": dest, "band": band,
                "band_note": dnote,
                "alternative": city if city.startswith(NF) else f"Collection in {city}",
                "sources": {"origin": "data/settings.json address.city",
                            "destination": "data/locations.json city",
                            "band": "data/settings.json delivery_min_gbp, delivery_max_gbp",
                            "band_note": "data/settings.json delivery_note",
                            "alternative": "outline H3 (collect in Carlisle) + address.city"}}

    if ig == "IG-1":
        items = []
        if pups is None:
            avail = None
        else:
            avail = [p for p in pups if str(p.get("status", "")).lower() == "available"]
        for sex, key in (("male", "male_gbp"), ("female", "female_gbp")):
            price = _get(pm, "price-matrix.json", key)
            names = (", ".join(p.get("name", "") for p in avail if p.get("sex") == sex)
                     if avail is not None else _nf("puppies.json", "name"))
            items.append({"value": _gbp(price), "label": f"{sex.title()}s",
                          "note": names or _nf("puppies.json", f"{sex} available"),
                          "icon": "tag"})
        items.append({"value": deposit, "label": "Deposit", "note": clause, "icon": "lock"})
        items.append({"value": str(len(avail)) if avail is not None
                      else _nf("puppies.json", "status"),
                      "label": "Available now", "note": "", "icon": "heart"})
        return {"title": title, "items": items,
                "sources": {"prices": "data/price-matrix.json male_gbp, female_gbp",
                            "names, count": "data/puppies.json name, sex, status",
                            "deposit": "data/settings.json deposit_gbp, deposit_refund_clause"}}

    if ig == "IG-2":
        names = _steps_from_prompt(slot_plan.get("prompt", "")) or [
            h.rstrip("?") for h in _h2_h3(sec)[1:]][:5]
        heads = _all_headings(sec)
        steps = []
        for i, n in enumerate(names, 1):
            low = n.lower()
            value, note, icon = "", "", "check"
            if "deposit" in low:
                value, note, icon = deposit, clause, "lock"
            elif "deliver" in low or "collect" in low:
                value, note, icon = band, (dnote if city.startswith(NF)
                                           else f"{dnote}; or collection in {city}"), "truck"
            elif "view" in low or "visit" in low:
                value, icon = "", "eye"
                note = city if city.startswith(NF) else f"In {city}"
            else:
                word = low.split()[-1] if low.split() else ""
                note = next((h for h in heads if word and word in h.lower()), "")
                icon = "video" if "video" in low else "check"
            steps.append({"n": f"{i:02d}", "title": n[:1].upper() + n[1:], "value": value,
                          "note": note, "icon": icon})
        return {"title": title, "steps": steps,
                "sources": {"steps": "the board slot's own prompt (outline text)",
                            "deposit": "data/settings.json deposit_gbp, deposit_refund_clause",
                            "delivery": "data/settings.json delivery_min_gbp, "
                                        "delivery_max_gbp, delivery_note",
                            "viewing": "data/settings.json address.city",
                            "video call": "outline H3 heading"}}

    if ig == "IG-4":
        checks = [{"text": h, "icon": "check"} for h in _all_headings(sec)][:10]
        if re.search(r"paperwork|contract|guarantee", " ".join(_all_headings(sec) + [
                sec.get("heading", "")]).lower()):
            checks.append({"text": _get(st, "settings.json", "guarantee_label"),
                           "icon": "shield"})
        return {"title": title, "checks": checks,
                "sources": {"checks": "the section's outline headings (H3–H6)",
                            "guarantee": "data/settings.json guarantee_label"}}

    if ig == "IG-3":
        texts = _h2_h3(sec)
        a = b = None
        for t in texts[1:] + texts[:1]:
            m = (re.search(r"tell (?:an? )?(.+?) from (?:an? )?(.+?)(?: one)?\?", t, re.I)
                 or re.search(r"(\w+ \w+) (?:vs\.?|versus|or) (\w+ \w+)", t, re.I))
            if m:
                a, b = m.group(1).strip(), m.group(2).strip()
                break
        missing = _nf("*", "breed-comparison file (height, weight, registry)")
        return {"title": title,
                "subjects": [a or _nf("*", "comparison subject"),
                             b or _nf("*", "comparison subject")],
                "rows": [{"attr": "Breed-standard figures", "a": missing, "b": missing}],
                "verdict": _nf("*", "comparison verdict"),
                "sources": {"subjects": "outline H3 heading",
                            "rows": "none — no data file holds breed-standard figures"}}
    return {"title": title, "sources": {}}


def _alt(p: dict) -> str:
    f, ig = p.get("facts") or {}, p.get("ig")
    if not f:
        return f'{IG_NAMES.get(ig, "Infographic")}: {p.get("node") or p.get("heading")}'
    if ig == "IG-5":
        return (f"Route from {f['origin']} to {f['destination']}: {f['band']}, "
                f"{f['band_note']}; or {f['alternative'][:1].lower()}{f['alternative'][1:]}")
    if ig == "IG-1":
        return "Litter figures: " + "; ".join(
            f"{i['label']} {i['value']}" for i in f["items"])
    if ig == "IG-2":
        return f"{len(f['steps'])} steps: " + ", then ".join(
            s["title"].lower() for s in f["steps"])
    if ig == "IG-4":
        return "Checklist: " + "; ".join(c["text"].rstrip("?") for c in f["checks"])
    if ig == "IG-3":
        return f"{f['subjects'][0]} compared with {f['subjects'][1]}"
    return p.get("heading", "")


# ---------------------------------------------------------------- render

ICONS = {  # Feather-style line icons (design rule 7): stroke only, currentColor.
    "check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/>',
    "tag": '<path d="M20.59 13.41 13.42 20.58a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><path d="M7 7h.01"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "heart": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78z"/>',
    "truck": '<path d="M1 3h15v13H1z"/><path d="M16 8h4l3 3v5h-7z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
    "eye": '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "video": '<path d="m23 7-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
}


def icon(name: str) -> str:
    return ('<svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" fill="none" '
            'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICONS.get(name, ICONS["check"])}</svg>')


def t(v) -> str:
    """Escape a fact; a NOT FETCHED value is marked so it renders visibly."""
    s = str(v)
    return f'<span class="nf">{esc(s)}</span>' if s.startswith(NF) else esc(s)


def load_tokens(root: Path = ROOT) -> dict:
    src = (Path(root) / "src/styles/tokens.css").read_text()
    body = src[src.index("{") + 1: src.rindex("}")]
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    return {m.group(1): m.group(2).strip()
            for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", body)}


FONT_BASE = "../../../../../public/fonts/"  # docs/artifacts/boards/ig/<slug>/ -> repo root


def _fonts(base: str) -> str:
    faces = [("Fraunces", "fraunces-latin-standard-normal.woff2"),
             ("Source Sans 3", "source-sans-3-latin-wght-normal.woff2")]
    return "".join(
        f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:100 900;'
        f'font-display:swap;src:url("{base}{f}") format("woff2-variations")}}'
        for fam, f in faces)


def _items_html(items: list[dict]) -> str:
    out = []
    for i, it in enumerate(items, 1):
        out.append(
            '<li class="it">'
            f'<span class="k">{i:02d}</span>'
            f'<span class="ic">{icon(it.get("icon", "check"))}</span>'
            + (f'<span class="v">{t(it["value"])}</span>' if it.get("value") else "")
            + f'<span class="l">{t(it["label"])}</span>'
            + (f'<span class="n">{t(it["note"])}</span>' if it.get("note") else "")
            + "</li>")
    return f'<ol class="items">{"".join(out)}</ol>'


def _body(ig: str, f: dict) -> str:
    if ig == "IG-1":
        return _items_html(f.get("items", []))
    if ig == "IG-2":
        return _items_html([{"value": s["value"], "label": s["title"], "note": s["note"],
                             "icon": s["icon"]} for s in f.get("steps", [])])
    if ig == "IG-4":
        return _items_html([{"label": c["text"], "icon": c["icon"]}
                            for c in f.get("checks", [])])
    if ig == "IG-3":
        a, b = f.get("subjects", ["", ""])
        rows_a = "".join(f'<li><span class="l">{t(r["attr"])}</span>'
                         f'<span class="n">{t(r["a"])}</span></li>' for r in f.get("rows", []))
        rows_b = "".join(f'<li><span class="l">{t(r["attr"])}</span>'
                         f'<span class="n">{t(r["b"])}</span></li>' for r in f.get("rows", []))
        return ('<div class="split">'
                f'<div class="col col-a"><p class="col-h">{t(a)}</p><ul>{rows_a}</ul></div>'
                f'<div class="col col-b"><p class="col-h">{t(b)}</p><ul>{rows_b}</ul></div>'
                f'</div><p class="verdict">{t(f.get("verdict", ""))}</p>')
    if ig == "IG-5":
        return ('<div class="route">'
                f'<div class="stop stop-a"><span class="dot"></span>'
                f'<span class="ic">{icon("pin")}</span>'
                f'<span class="city">{t(f.get("origin", ""))}</span>'
                f'<span class="n">{t(f.get("alternative", ""))}</span></div>'
                '<div class="leg"><span class="line" aria-hidden="true"></span>'
                f'<span class="ic">{icon("truck")}</span>'
                f'<span class="v">{t(f.get("band", ""))}</span>'
                f'<span class="n">{t(f.get("band_note", ""))}</span></div>'
                f'<div class="stop stop-b"><span class="dot"></span>'
                f'<span class="ic">{icon("pin")}</span>'
                f'<span class="city">{t(f.get("destination", ""))}</span>'
                '<span class="n">Home delivery</span></div>'
                '</div>')
    return ""


BASE_CSS = """
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0}
body{background:var(--color-surface);color:var(--color-text);font-family:var(--font-body);
 font-size:var(--text-base);line-height:1.5;padding:var(--space-5) var(--space-4)}
.ig{max-width:1100px;margin:0 auto;min-height:380px;display:flex;flex-direction:column}
.cap{font-family:var(--font-display);font-weight:600;margin:0;text-wrap:balance}
.items{list-style:none;margin:0;padding:0}
.it,.stop,.leg{display:flex;flex-direction:column;min-width:0}
.v{font-family:var(--font-display);font-weight:600;font-variant-numeric:lining-nums tabular-nums;
 overflow-wrap:anywhere}
.l{font-weight:600}
.n{font-size:var(--text-sm);overflow-wrap:anywhere}
.nf{display:inline-block;font-size:var(--text-xs);font-weight:700;letter-spacing:.02em;
 color:var(--color-warn);background:var(--color-white);border:1px dashed var(--color-warn);
 border-radius:var(--radius-sm);padding:2px 6px;line-height:1.35}
.ico{display:block;width:100%;height:100%}
.route{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr) minmax(0,1fr);
 align-items:center;gap:var(--space-4);flex:1}
.stop{align-items:center;text-align:center;gap:var(--space-1)}
.leg{position:relative;align-items:center;text-align:center;gap:var(--space-2)}
.city{font-family:var(--font-display);font-weight:600;font-size:var(--text-3xl);line-height:1.1}
.split{display:grid;grid-template-columns:1fr 1fr;flex:1}
.split ul{list-style:none;margin:0;padding:0}
.col-h{font-family:var(--font-display);font-weight:600;font-size:var(--text-xl);margin:0 0 var(--space-3)}
.verdict{margin:0}
@media (max-width:767px){
 .ig{min-height:0}
 .route{grid-template-columns:1fr;gap:var(--space-3)}
 .split{grid-template-columns:1fr}
}
"""

STYLE_CSS = {
    # PLATE — a steel band: the figures are the picture, set big in brass Fraunces.
    "plate": """
.ig{background:var(--color-surface-inverse);color:var(--color-text-on-inverse);
 border-radius:var(--radius-md);box-shadow:var(--shadow-card);overflow:clip;position:relative;
 padding:var(--space-7) var(--space-7) var(--space-6)}
.ig::before{content:"";position:absolute;inset:0 0 auto 0;height:4px;background:var(--seam-gradient)}
.cap{font-size:var(--text-xl);max-width:40ch;margin-bottom:var(--space-6)}
.items{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));flex:1;align-content:center}
.it{padding:var(--space-2) var(--space-5);gap:var(--space-1);
 border-left:1px solid color-mix(in srgb,var(--color-text-on-inverse) 22%,transparent)}
.it:first-child{border-left:0;padding-left:0}
.k{font-size:var(--text-xs);letter-spacing:.14em;opacity:.75}
.ic{display:none}
.v{font-size:var(--text-4xl);line-height:1.05;color:var(--color-cta);margin:var(--space-2) 0 var(--space-1)}
.l{font-size:var(--text-lg)}
.n{color:color-mix(in srgb,var(--color-text-on-inverse) 85%,transparent)}
.ig-2 .items{counter-reset:s}
.ig-2 .it{border-left:0;border-top:2px solid color-mix(in srgb,var(--color-text-on-inverse) 30%,transparent);
 padding:var(--space-4) var(--space-4) 0 0;margin-top:var(--space-4);position:relative}
.ig-2 .k{position:absolute;top:-19px;left:0;width:36px;height:36px;border-radius:50%;
 background:var(--color-surface-inverse);border:2px solid var(--color-cta);display:grid;place-items:center;
 font-size:var(--text-sm);font-weight:700;opacity:1;letter-spacing:0}
.ig-2 .v{font-size:var(--text-3xl)}
.ig-4 .items{grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:var(--space-3) var(--space-6)}
.ig-4 .it{flex-direction:row;align-items:flex-start;gap:var(--space-3);border-left:0;padding:var(--space-2) 0;
 border-bottom:1px solid color-mix(in srgb,var(--color-text-on-inverse) 18%,transparent)}
.ig-4 .k{display:none}
.ig-4 .ic{display:block;flex:0 0 24px;height:24px;color:var(--color-cta)}
.ig-4 .l{font-weight:400;font-size:var(--text-base)}
.route .ic{display:none}
.dot{width:18px;height:18px;border-radius:50%;background:var(--color-cta);margin-bottom:var(--space-2)}
.stop-b .dot{background:var(--color-brand-tint)}
.leg .line{position:absolute;left:-8%;right:-8%;top:50%;border-top:3px dashed color-mix(in srgb,var(--color-text-on-inverse) 55%,transparent);z-index:0}
.leg .v,.leg .n{position:relative;z-index:1;background:var(--color-surface-inverse);padding:0 var(--space-3)}
.leg .v{font-size:var(--text-4xl);color:var(--color-cta);margin:0}
.leg .n{max-width:32ch}
.split{gap:1px;background:color-mix(in srgb,var(--color-text-on-inverse) 22%,transparent);border-radius:var(--radius-sm);overflow:hidden}
.col{background:var(--color-surface-inverse);padding:var(--space-4) var(--space-5)}
.split li{display:flex;flex-direction:column;gap:var(--space-1);padding:var(--space-2) 0}
.verdict{margin-top:var(--space-4);padding-top:var(--space-3);border-top:1px solid color-mix(in srgb,var(--color-text-on-inverse) 22%,transparent)}
@media (max-width:767px){
 .ig{padding:var(--space-6) var(--space-5) var(--space-5)}
 .cap{margin-bottom:var(--space-4)}
 .items{grid-template-columns:1fr 1fr;row-gap:var(--space-4)}
 .it,.it:first-child{border-left:0;padding:0 var(--space-3) 0 0}
 .v{font-size:var(--text-3xl)}
 .ig-2 .items,.ig-4 .items{grid-template-columns:1fr}
 .ig-2 .it{border-top:0;border-left:2px solid color-mix(in srgb,var(--color-text-on-inverse) 30%,transparent);
  margin:0 0 0 17px;padding:0 0 var(--space-5) var(--space-6)}
 .ig-2 .k{top:-2px;left:-19px}
 .leg{padding:var(--space-5) 0}
 .leg .line{left:50%;right:auto;top:0;bottom:0;border-top:0;border-left:3px dashed color-mix(in srgb,var(--color-text-on-inverse) 55%,transparent)}
 .leg .v,.leg .n{padding:var(--space-1) var(--space-2)}
}
@media (max-width:420px){.ig-1 .items{grid-template-columns:1fr}}
""",
    # RULED — a ledger on bone: index, entry, figure; hairlines carry the rhythm.
    "ruled": """
.ig{background:var(--counter-bed);color:var(--color-text);padding:var(--space-6) var(--space-7);
 border-top:3px solid var(--color-brand);border-bottom:1px solid var(--color-border)}
.cap{font-size:var(--text-xl);color:var(--color-brand);padding-bottom:var(--space-3);
 border-bottom:1px solid var(--color-brand);margin-bottom:var(--space-2)}
.items{flex:1;display:flex;flex-direction:column;justify-content:center}
.it{display:grid;grid-template-columns:3.25rem minmax(0,1fr) auto;grid-template-areas:"k l v" "k n v";
 column-gap:var(--space-5);align-items:baseline;padding:var(--space-3) 0;border-bottom:1px solid var(--color-border)}
.it:last-child{border-bottom:0}
.k{grid-area:k;font-family:var(--font-display);font-size:var(--text-lg);color:var(--color-text-muted);
 font-variant-numeric:tabular-nums}
.ic{display:none}
.l{grid-area:l;font-size:var(--text-lg);color:var(--color-text)}
.n{grid-area:n;color:var(--color-text-muted)}
.v{grid-area:v;font-size:var(--text-2xl);color:var(--color-brand);text-align:right;align-self:center}
.ig-4 .items{display:grid;grid-template-columns:1fr 1fr;column-gap:var(--space-7)}
.ig-4 .it{grid-template-columns:2.25rem minmax(0,1fr);grid-template-areas:"k l";border-bottom:1px solid var(--color-border)}
.ig-4 .it:last-child{border-bottom:1px solid var(--color-border)}
.ig-4 .k{font-size:var(--text-base)}
.ig-4 .l{font-weight:400;font-size:var(--text-base)}
.route{grid-template-columns:auto minmax(0,1fr) auto;margin-top:var(--space-5);align-items:start}
.route .ic{display:none}
.stop{align-items:flex-start;text-align:left}
.stop-b{align-items:flex-end;text-align:right}
.dot{width:12px;height:12px;border:2px solid var(--color-brand);border-radius:50%;background:var(--counter-bed)}
.stop-a .dot{background:var(--color-brand)}
.city{color:var(--color-brand);font-size:var(--text-2xl)}
.stop .n{color:var(--color-text-muted)}
.leg{padding-top:5px;align-items:stretch;text-align:center}
.leg .line{display:block;height:0;border-top:1px solid var(--color-brand);
 background:repeating-linear-gradient(90deg,var(--color-brand) 0 1px,transparent 1px 24px);height:9px;
 border-bottom:0;margin-bottom:var(--space-3)}
.leg .v{font-size:var(--text-3xl);color:var(--color-brand)}
.leg .n{color:var(--color-text-muted)}
.split{border-top:1px solid var(--color-border);margin-top:var(--space-2)}
.col{padding:var(--space-4) var(--space-5) var(--space-4) 0}
.col-b{border-left:1px solid var(--color-border);padding-left:var(--space-5)}
.col-h{color:var(--color-brand)}
.split li{display:flex;flex-direction:column;gap:var(--space-1);padding:var(--space-2) 0;border-top:1px solid var(--color-border)}
.verdict{border-top:1px solid var(--color-brand);padding-top:var(--space-3)}
@media (max-width:767px){
 .ig{padding:var(--space-5) var(--space-4)}
 .it{grid-template-columns:2.25rem minmax(0,1fr);grid-template-areas:"k l" "k n" "k v"}
 .v{text-align:left;margin-top:var(--space-1);font-size:var(--text-xl)}
 .ig-4 .items{grid-template-columns:1fr}
 .ig-4 .it:not(:last-child){border-bottom:1px solid var(--color-border)}
 .route{grid-template-columns:1.25rem minmax(0,1fr);grid-template-areas:"a a" "leg leg" "b b"}
 .stop-a{grid-area:a}.stop-b{grid-area:b}.leg{grid-area:leg}
 .stop,.stop-b{flex-direction:row;flex-wrap:wrap;align-items:baseline;text-align:left;gap:var(--space-1) var(--space-3)}
 .stop .n{flex-basis:100%;padding-left:calc(12px + var(--space-3))}
 .leg{border-left:1px solid var(--color-brand);margin-left:5px;padding:var(--space-3) 0 var(--space-3) var(--space-5);text-align:left}
 .leg .line{display:none}
 .leg .v,.leg .n{text-align:left;align-self:flex-start}
 .col-b{border-left:0;padding-left:0;border-top:1px solid var(--color-brand)}
}
""",
    # CARD — white cards on the surface; a steel rail and a line icon lead each item.
    "card": """
.ig{background:transparent;padding:0;gap:var(--space-5)}
.cap{font-size:var(--text-2xl);color:var(--color-brand);max-width:36ch}
.items{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:var(--space-4);flex:1;align-content:start}
.it,.stop,.leg,.col{background:var(--color-surface-raised);border:var(--card-border);border-radius:var(--card-radius);
 box-shadow:var(--shadow-card);padding:var(--space-5) var(--space-5) var(--space-5) calc(var(--space-5) + 4px);
 position:relative;overflow:hidden;gap:var(--space-2)}
.it::before,.stop::before,.leg::before,.col::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:var(--color-brand-mid)}
.k{display:none}
.ic{width:40px;height:40px;padding:9px;border-radius:50%;background:var(--color-brand-soft);color:var(--color-brand);flex:0 0 auto}
.v{font-size:var(--text-2xl);color:var(--color-brand);line-height:1.1}
.l{color:var(--color-text);font-size:var(--text-lg)}
.n{color:var(--color-text-muted)}
.ig-2 .items{counter-reset:s}
.ig-2 .it::after{counter-increment:s;content:"Step " counter(s);position:absolute;top:var(--space-5);right:var(--space-5);
 font-size:var(--text-xs);letter-spacing:.08em;text-transform:uppercase;color:var(--color-text-muted)}
.ig-4 .items{grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:var(--space-3)}
.ig-4 .it{flex-direction:row;align-items:center;gap:var(--space-3);padding-block:var(--space-3)}
.ig-4 .ic{width:34px;height:34px;padding:7px}
.ig-4 .l{font-size:var(--text-base);font-weight:400}
.ig-4 .it:last-child .ic{background:var(--color-cta-soft)}
.route{gap:var(--space-4);align-items:stretch}
.stop{align-items:flex-start;text-align:left}
.dot{display:none}
.city{color:var(--color-brand);font-size:var(--text-2xl)}
.leg{align-items:flex-start;text-align:left;background:var(--color-brand-soft)}
.leg .line{display:none}
.leg .v{font-size:var(--text-3xl)}
.leg .n{color:var(--color-text)}
.leg .ic{background:var(--color-surface-raised)}
.split{gap:var(--space-4)}
.split li{display:flex;flex-direction:column;gap:var(--space-1);padding:var(--space-2) 0}
.verdict{background:var(--color-surface-inverse);color:var(--color-text-on-inverse);border-radius:var(--radius-md);padding:var(--space-3) var(--space-5)}
@media (max-width:767px){
 .cap{font-size:var(--text-xl)}
 .items{grid-template-columns:1fr}
 .it{flex-direction:row;flex-wrap:wrap;align-items:center;column-gap:var(--space-3)}
 .it .v,.it .l{flex:1 1 auto}
 .it .n{flex-basis:100%}
 .ig-2 .it::after{top:var(--space-3);right:var(--space-4)}
}
""",
}


def render_preview(slot_plan: dict, style_id: str, facts: dict, tokens: dict,
                   font_base: str = FONT_BASE) -> str:
    """A standalone HTML document: tokens inlined as :root, no external requests."""
    ig = slot_plan.get("ig") or "IG-1"
    alt = slot_plan.get("alt") or _alt({**slot_plan, "facts": facts})
    root_css = ":root{" + ";".join(f"{k}:{v}" for k, v in tokens.items()) + "}"
    title = facts.get("title") or slot_plan.get("node") or slot_plan.get("heading", "")
    label = f'{slot_plan.get("slot")} · {ig} {IG_NAMES.get(ig, "")} · {style_id}'
    return (
        "<!doctype html>\n<html lang=\"en-GB\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(label)}</title>"
        f"<style>{_fonts(font_base)}{root_css}{BASE_CSS}{STYLE_CSS[style_id]}</style>"
        "</head><body>"
        f'<!-- BSUK Infographic: {esc(ig)} {esc(IG_NAMES.get(ig, ""))} | '
        f'{esc(slot_plan.get("page", ""))} | slot {esc(slot_plan.get("slot", ""))} | '
        f'style {esc(style_id)} -->'
        f'<figure class="ig {ig.lower()} st-{style_id}" role="img" aria-label="{esc(alt)}">'
        f'<figcaption class="cap">{t(title)}</figcaption>'
        f"{_body(ig, facts)}</figure></body></html>\n")


# ---------------------------------------------------------------- outputs

def preview_path(slug: str, slot: str, style: str) -> str:
    return f"{OUT_DIR}/{slug}/{slot}-{style}.html"


def write_previews(board: dict, root: Path = ROOT) -> list[str]:
    tokens = load_tokens(root)
    written = []
    for p in plan(board, root):
        for s in p["styles"]:
            rel = preview_path(p["page"], p["slot"], s["id"])
            out = Path(root) / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render_preview(p, s["id"], p["facts"], tokens))
            written.append(rel)
    return written


def block(board: dict, root: Path | None = ROOT) -> str:
    """Board block 7c as markdown: the plan table, then per slot its three preview paths."""
    rows = plan(board, root)
    if not rows:
        return "No section needs an infographic: no heading matched an IG trigger.\n"
    lines = ["| Section | Heading | IG type | Why it triggered |", "|---|---|---|---|"]
    for p in rows:
        lines.append(f"| {p['section']} | {p['node']} | {p['ig']} "
                     f"{IG_NAMES.get(p['ig'], '')} | {p['why']} |")
    for p in rows:
        lines += ["", f"**{p['slot']}** ({p['ig']} {IG_NAMES.get(p['ig'], '')}) — pick one: "
                  f"radio `pick-ig:{p['slot']}`"]
        for s in p["styles"]:
            lines.append(f"- {s['label']}: `{preview_path(p['page'], p['slot'], s['id'])}`")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print("usage: infographic_plan.py <slug> [--write]", file=sys.stderr)
        return 2
    f = ROOT / "data/boards" / f"{args[0]}.json"
    if not f.exists():
        print(f"no board: {f.relative_to(ROOT)}", file=sys.stderr)
        return 2
    board = json.loads(f.read_text())
    rows = plan(board)
    print(f"{'section':<18} {'slot':<26} {'IG':<5} why")
    for p in rows:
        print(f"{p['section']:<18} {p['slot']:<26} {p['ig']:<5} {p['why']}")
    if "--write" in argv:
        for rel in write_previews(board):
            print("wrote", rel)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
