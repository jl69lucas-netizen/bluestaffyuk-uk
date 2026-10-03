#!/usr/bin/env python3
"""infographic_plan.py — board block 7c, "Infographics": which sections need one, which IG
type, and three rendered styles of each for the breeder to pick from.

    python3 scripts/infographic_plan.py <slug>            # print the plan table
    python3 scripts/infographic_plan.py <slug> --write    # ...write the previews and measure
                                                          #    their heights (heights.json)
    python3 scripts/infographic_plan.py <slug> --heights  # re-measure heights only

The IG types are the bsuk-infographic skill's (IMAGE-DESIGNS.md §8). A section gets an
infographic when its H2 heading or one of its H3 headings matches TRIGGERS; the IG types are
tried in TRIGGERS order and the first that matches any heading wins, so a delivery heading
that also says "cost" is a route (IG-5), not a price panel. Frame sections (hero, counter,
trust, contents, takeaways, reviews, FAQ blocks, newsletter, form) never get one. An
infographic slot already on the board (an `images` entry of kind "infographic" on the section
or a tree node, or an asset naming its `section`) keeps its slot id and IG type.

Every figure comes from data/settings.json, data/price-matrix.json, data/puppies.json,
data/locations.json or data/breed-standards.json (the IG-3 breed split: sourced, quoted
breed-standard fields, breeder q07, 2026-10-02), or is the section's own outline text
(heading, H3s, the slot prompt).
A fact the data does not hold is written `NOT FETCHED — <file> <key> missing` and rendered
visibly (class "nf"), never guessed (CLAUDE.md rule 9). The deposit is only ever qualified by
settings `deposit_refund_clause`, never called plainly refundable.

Three styles per slot, the same content on the same tokens (src/styles/tokens.css). The
breeder's ruling q08 (2026-10-02): infographics are "nice, playful, cartoonish", so all three
are cartoon treatments, on the site palette only (steel, bone, brass), and every figure stays
exact text — nothing is drawn by AI:
  sticker  die-cut white stickers, thick ink outlines, hard offset shadows, brass number
           badges and the doodle-dog mascot (DOG: a friendly Staffy, rose ears, no collar)
  chalk    a sketchbook on bone graph paper: wobbly hand-drawn outlines (an SVG turbulence
           filter on the lines only, never on text), wavy brass underlines, highlighter
           swipes behind the figures, doodled arrows
  comic    heavy-bordered panels, the dog saying the title in a speech bubble, brass caption
           boxes, speech-bubble labels and halftone dots
No preview carries a script or fetches anything but the two web fonts.

Frame heights: measure_heights() renders every preview at the board's three widths in
Playwright (scripts/ig_shots.mjs, fonts served) and writes HEIGHTS_FILE; the board sizes each
frame from it, so no frame is shorter than its document (the v2 "Card" clipping fix).
Baking: bake_infographic() screenshots ONE picked style per slot into public/images/
infographics/ — only after the breeder picks (Task 9 / STOP 4), never all three styles.

Fonts: previews load Fraunces and Source Sans 3 from the repo's public/fonts by a relative
`font_base` (FONT_BASE), so they render true when opened from the repo. Task 7 publishes
public/fonts once as Artifact files and passes that published `font_base` to render_preview;
until then a published preview falls back to the token stacks (Georgia, system-ui).

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
STYLES = [{"id": "sticker", "label": "Sticker"}, {"id": "chalk", "label": "Chalk"},
          {"id": "comic", "label": "Comic"}]
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


def _is_ig_node(n: dict) -> bool:
    """True for a tree node that exists to carry an infographic (breeder q08, 2026-10-02:
    each infographic gets its own heading, and that heading's only image is the graphic)."""
    return any(img.get("kind") == "infographic" for img in n.get("images") or [])


def _h2_h3(sec: dict) -> list[str]:
    """The H2 heading, then every H3 (top-level tree node) heading. An infographic's own H3
    is left out: it names the graphic, so it is never one of the graphic's subjects or
    steps, and never the trigger that plans it."""
    out = [sec.get("heading", "")]
    for n in sec.get("tree") or []:
        if n.get("level", 3) == 3 and not _is_ig_node(n):
            out.append(n.get("heading") or n.get("text") or "")
    return out


def _all_headings(sec: dict) -> list[str]:
    """Every tree heading, depth first, without the infographic's own H3 and its subtree —
    an IG-4 checklist must not list its own title as a tick."""
    out, stack = [], [n for n in sec.get("tree") or [] if not _is_ig_node(n)]
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
    """The section's infographic slot already on the board, with the heading it sits on
    (`_node`), that heading's level (`_level`) and its path in the section (`_path`: "h2" for
    the section itself, else "tree[i].children[j]…" as the board's
    outline_changes_since_stop2 rows name it)."""
    for img in sec.get("images") or []:
        if img.get("kind") == "infographic":
            return {**img, "_node": sec.get("heading", ""), "_level": "H2", "_path": "h2"}
    stack = [(n, f"tree[{i}]") for i, n in enumerate(sec.get("tree") or [])]
    while stack:
        n, path = stack.pop(0)
        for img in n.get("images") or []:
            if img.get("kind") == "infographic":
                return {**img, "_node": n.get("heading") or n.get("text") or "",
                        "_level": f"H{n.get('level', 3)}", "_path": path}
        stack[:0] = [(c, f"{path}.children[{j}]") for j, c in enumerate(n.get("children") or [])]
    for a in board.get("assets") or []:
        if a.get("kind") == "infographic" and a.get("section") == sec.get("id"):
            return {**a, "_node": sec.get("heading", ""), "_level": "H2", "_path": "h2"}
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
            own = ex["_path"] != "h2"
            p = {"section": sec["id"], "slot": ex["slot"],
                 "ig": ex.get("infographic_style") or asset.get("infographic_style"),
                 "node": ex["_node"], "node_level": ex["_level"], "node_path": ex["_path"],
                 "why": (f"its own {ex['_level']} on the board (breeder q08, 2026-10-02)" if own
                         else "infographic slot already on the board"),
                 "prompt": ex.get("prompt") or asset.get("prompt") or "",
                 "alt": asset.get("alt") or ex.get("alt") or ""}
            if p["ig"] not in IG_NAMES:
                hit = match(_h2_h3(sec))
                if not hit:
                    raise ValueError(
                        f"slot {ex['slot']!r}: infographic_style {p['ig']!r} is missing or "
                        "unknown and no heading matches an IG trigger")
                p["ig"] = hit[0]
                p["why"] = (f"infographic slot already on the board; style {ex.get('infographic_style')!r} "
                            f're-matched by "{hit[1]}" in "{hit[2]}"')
        else:
            hit = match(_h2_h3(sec))
            if not hit:
                continue
            ig, word, text = hit
            level = "H2" if text == sec.get("heading", "") else "H3"
            slot = f"{sec['id']}-{SLOT_SUFFIX[ig]}"
            while slot in taken:
                slot += "-ig"
            # A proposal only: the slot sits on the heading that triggered it until the board
            # gives it a heading of its own (outline_changes_since_stop2).
            p = {"section": sec["id"], "slot": slot, "ig": ig, "node": text,
                 "node_level": level, "node_path": "h2" if level == "H2" else None,
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


#: IG-3 rows, in order: (data/breed-standards.json field, row label). A row is shown only when
#: BOTH subjects' standards state it, so the split compares like with like.
SPLIT_FIELDS = (("standard", "Breed standard"), ("height", "Height"), ("weight", "Weight"),
                ("colours", "Coat colours"), ("uk_legal_status", "UK law"))
#: Source caption: a host in a used source URL -> the name the caption gives it.
CREDITS = (("royalkennelclub.com", "Royal Kennel Club"), ("akc.org", "AKC"),
           ("ukcdogs.com", "UKC"), ("gov.uk", "GOV.UK"))


def _breed_key(subject: str):
    """The data/breed-standards.json breed an outline subject names, or None when it names
    none of the three (its column then renders NOT FETCHED, never another breed's figures)."""
    low = subject.lower()
    if low.startswith(NF):
        return None
    if re.search(r"\bpit ?bulls?\b", low):
        return "american-pit-bull-terrier"
    if re.search(r"\bamerican staff|\bamstaff", low):
        return "american-staffordshire-terrier"
    if re.search(r"\b(english )?staff(y|ies|ordshire bull terriers?)\b", low):
        return "staffordshire-bull-terrier"
    return None


def _fact_value(field):
    """A sourced field's value, or None when it is missing, unsourced or NOT FETCHED."""
    if not isinstance(field, dict):
        return None
    v = field.get("value")
    if not isinstance(v, str) or not v or v.startswith(NF):
        return None
    if "clauses" not in field and not (field.get("source") and field.get("quote")):
        return None
    return v


def facts_for(slot_plan: dict, root) -> dict:
    """The slot's facts, read only from data/ under `root` and the section's outline text."""
    root = Path(root)
    st = _load(root, "settings.json") or {}
    pm = _load(root, "price-matrix.json") or {}
    pups = _load(root, "puppies.json")
    locs = _load(root, "locations.json") or []
    sec = _section(slot_plan, root)
    ig = slot_plan.get("ig")
    city = str(_get(st, "settings.json", "address", "city"))
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
            m = re.search(r"tell (?:an? )?(.+?) from (?:an? )?(.+?)( one)?\?", t, re.I)
            one = bool(m and m.group(3))
            m = m or re.search(r"(\w+ \w+) (?:vs\.?|versus|or) (\w+ \w+)", t, re.I)
            if m:
                a, b = m.group(1).strip(), m.group(2).strip()
                # "an American one" / a bare adjective: borrow the head noun from subject A.
                if (one or len(b.split()) == 1) and len(a.split()) > 1:
                    b = f"{b} {a.split()[-1]}"
                break
        subjects = [a or _nf("*", "comparison subject"), b or _nf("*", "comparison subject")]
        bs = _load(root, "breed-standards.json")
        if not isinstance(bs, dict) or not isinstance(bs.get("breeds"), dict):
            missing = _nf("breed-standards.json", "breeds")
            return {"title": title, "subjects": subjects,
                    "rows": [{"attr": "Breed-standard figures", "a": missing, "b": missing}],
                    "verdict": _nf("breed-standards.json", "comparison_verdict"),
                    "sources": {"subjects": "outline H3 heading",
                                "rows": "none — data/breed-standards.json is missing"}}
        keys = [_breed_key(x) for x in subjects]
        if None in keys:
            row = {"attr": "Breed-standard figures"}
            for side, k, x in zip("ab", keys, subjects):
                row[side] = (_nf("breed-standards.json", f"breed for '{x}'") if k is None
                             else _nf("breed-standards.json", "a comparable second breed"))
            return {"title": title, "subjects": subjects, "rows": [row],
                    "verdict": _nf("breed-standards.json", "comparison_verdict for these subjects"),
                    "sources": {"subjects": "outline H3 heading",
                                "rows": "none — a subject names no breed in data/breed-standards.json"}}
        breeds = [bs["breeds"].get(k) or {} for k in keys]
        rows, used = [], set()
        for field, attr in SPLIT_FIELDS:
            va, vb = (_fact_value(br.get(field)) for br in breeds)
            if va is None or vb is None:          # both breeds must state it: comparable only
                continue
            rows.append({"attr": attr, "a": va, "b": vb})
            used |= {br[field]["source"] for br in breeds}
            if len(rows) == 5:
                break
        if not rows:
            rows = [{"attr": "Breed-standard figures",
                     "a": _nf("breed-standards.json", f"breeds.{keys[0]}"),
                     "b": _nf("breed-standards.json", f"breeds.{keys[1]}")}]
        verdict = _fact_value(bs.get("comparison_verdict")) or _nf(
            "breed-standards.json", "comparison_verdict")
        for c in (bs.get("comparison_verdict") or {}).get("clauses") or []:
            used.add(c.get("source", ""))
        credit = [n for host, n in CREDITS if any(host in u for u in used)]
        return {"title": title, "subjects": subjects, "rows": rows, "verdict": verdict,
                "credit": ("Source: " + " / ".join(credit) + " — figures as each standard states them")
                          if credit else "",
                "sources": {"subjects": "outline H3 heading",
                            "rows": "data/breed-standards.json breeds."
                                    + ", ".join(keys) + " (" + ", ".join(
                                        f for f, _ in SPLIT_FIELDS) + ")",
                            "verdict": "data/breed-standards.json comparison_verdict"}}
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
        texts = [c["text"].rstrip("?") for c in f["checks"]]
        shown = []
        for x in texts[:6]:
            if shown and len("; ".join(shown + [x])) > 250:
                break
            shown.append(x)
        rest = len(texts) - len(shown)
        return "Checklist: " + "; ".join(shown) + (f"; and {rest} more" if rest else "")
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
            f'<li class="it it-{esc(it.get("icon", "check"))}">'
            f'<span class="k">{i:02d}</span>'
            f'<span class="ic">{icon(it.get("icon", "check"))}</span>'
            + (f'<span class="v fig">{t(it["value"])}</span>' if it.get("value") else "")
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
                f'</div><p class="verdict">{t(f.get("verdict", ""))}</p>'
                + (f'<p class="src">{esc(f["credit"])}</p>' if f.get("credit") else ""))
    if ig == "IG-5":
        return ('<div class="route">'
                f'<div class="stop stop-a"><span class="dot"></span>'
                f'<span class="ic">{icon("pin")}</span>'
                f'<span class="city fig">{t(f.get("origin", ""))}</span>'
                f'<span class="n">{t(f.get("alternative", ""))}</span></div>'
                '<div class="leg"><span class="line" aria-hidden="true"></span>'
                f'<span class="ic">{icon("truck")}</span>'
                f'<span class="v fig">{t(f.get("band", ""))}</span>'
                f'<span class="n">{t(f.get("band_note", ""))}</span></div>'
                f'<div class="stop stop-b"><span class="dot"></span>'
                f'<span class="ic">{icon("pin")}</span>'
                f'<span class="city fig">{t(f.get("destination", ""))}</span>'
                '<span class="n">Home delivery</span></div>'
                '</div>')
    return ""


#: The doodle dog (breeder q08, 2026-10-02: "nice, playful, cartoonish"). A head-and-shoulders
#: line drawing of a Staffy: broad cheeks, short muzzle, rose ears folded back, a wide grin,
#: no collar, no spikes. Fills are classes so every style colours it from the tokens.
DOG = (
    '<svg class="dog" viewBox="0 0 120 112" aria-hidden="true" focusable="false">'
    # thick neck and shoulders, with the white chest blaze
    '<path class="dg-fur" d="M27 78C17 88 13 102 13 112H107C107 102 103 88 93 78Z"/>'
    '<path class="dg-pale" d="M50 90Q60 111 70 90Z"/>'
    # rose ears: small, set high, folded back so the inner fold shows
    '<path class="dg-ear" d="M40 27C31 18 19 18 12 27C17 31 19 37 20 42C25 35 30 33 35 36Z"/>'
    '<path class="dg-ear" d="M80 27C89 18 101 18 108 27C103 31 101 37 100 42C95 35 90 33 85 36Z"/>'
    '<path class="dg-ln" d="M13 27C21 27 27 29 33 33M107 27C99 27 93 29 87 33"/>'
    # the broad Staffy head: skull, then cheeks wider than the skull
    '<path class="dg-fur" d="M60 20C43 20 33 25 31 36C22 44 19 57 23 68C27 81 41 89 60 89'
    'C79 89 93 81 97 68C101 57 98 44 89 36C87 25 77 20 60 20Z"/>'
    # cheek muscle, forehead crease, brows, wide-set eyes with a highlight
    '<path class="dg-ln" d="M27 55Q31 64 38 68M93 55Q89 64 82 68M56 24Q60 29 64 24'
    'M40 37Q45 33 51 36M69 36Q75 33 80 37"/>'
    '<circle class="dg-ink" cx="46" cy="44" r="4.3"/><circle class="dg-ink" cx="74" cy="44" r="4.3"/>'
    '<circle class="dg-hi" cx="47.5" cy="42.5" r="1.4"/><circle class="dg-hi" cx="75.5" cy="42.5" r="1.4"/>'
    # short, broad muzzle; a big nose pad with a shine; a closed, curved smile, and a small
    # rounded tongue hanging below the lower lip, off to one side (never two front "teeth")
    '<path class="dg-pale" d="M39 66C39 56 48 51 60 51C72 51 81 56 81 66C81 78 72 84 60 84'
    'C48 84 39 78 39 66Z"/>'
    '<path class="dg-tongue" d="M62 75C61 83 64 88 68 88C72 88 74 83 73 73Q68 76 62 75Z"/>'
    '<path class="dg-ln" d="M67.5 78V84"/>'
    '<path class="dg-ink" d="M48 55Q60 47 72 55Q70 64 60 65Q50 64 48 55Z"/>'
    '<ellipse class="dg-hi" cx="55.5" cy="54.5" rx="3.6" ry="1.8"/>'
    '<path class="dg-ln" d="M60 65V69M43 68Q51 77 60 76Q69 76 77 66"/>'
    '</svg>')

#: The chalk style's wobble: a turbulence displacement applied to the DRAWN lines only (box
#: outlines, dividers, the dog), never to text, so every figure stays crisp exact type.
WOBBLE = ('<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false">'
          '<filter id="wob" x="-5%" y="-5%" width="110%" height="110%">'
          '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="7"/>'
          '<feDisplacementMap in="SourceGraphic" scale="3.5" xChannelSelector="R" yChannelSelector="G"/>'
          '</filter></svg>')


def _svg_uri(svg: str) -> str:
    """An inline SVG as a CSS url(): a decoration drawn in the document, never fetched."""
    return 'url("data:image/svg+xml,' + svg.replace('"', "'").replace("#", "%23").replace(
        "<", "%3C").replace(">", "%3E") + '")'


BASE_CSS = """
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0}
body{background:var(--color-surface);color:var(--color-text);font-family:var(--font-body);
 font-size:var(--text-base);line-height:1.5;padding:var(--space-5) var(--space-5)}
.ig{max-width:1100px;margin:0 auto;display:flex;flex-direction:column;position:relative}
.cap{font-family:var(--font-display);font-weight:600;margin:0;display:flex;align-items:center;
 gap:var(--space-4);line-height:1.2}
.cap-t{text-wrap:balance;min-width:0}
.dog{display:block;width:100%;height:100%;overflow:visible}
.dg-fur{fill:var(--color-brand-tint)}.dg-ear{fill:var(--color-brand-mid)}
.dg-pale{fill:var(--color-bone-50)}.dg-tongue{fill:color-mix(in srgb,var(--color-warn) 42%,var(--color-bone-50))}
.dg-ink{fill:var(--color-ink)}.dg-hi{fill:var(--color-white)}
.dog path,.dog circle{stroke:var(--color-ink);stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round}
.dog .dg-ln{fill:none}.dog .dg-hi{stroke:none}
.dog ellipse{stroke:none}
.defs{position:absolute;width:0;height:0;overflow:hidden}
.items{list-style:none;margin:0;padding:0}
.it,.stop,.leg{display:flex;flex-direction:column;min-width:0;position:relative}
.v{font-family:var(--font-display);font-weight:700;font-variant-numeric:lining-nums tabular-nums;
 overflow-wrap:anywhere;line-height:1.05}
.l{font-weight:700}
.n{font-size:var(--text-sm);overflow-wrap:anywhere}
.nf{display:inline-block;font-size:14px;font-weight:700;letter-spacing:.02em;
 color:var(--color-warn);background:var(--color-white);border:1px dashed var(--color-warn);
 border-radius:var(--radius-sm);padding:2px 6px;line-height:1.35}
.ico{display:block;width:100%;height:100%}
.ic{flex:0 0 auto}
.route{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr) minmax(0,1fr);
 align-items:stretch;gap:var(--space-6);position:relative}
.stop{align-items:center;text-align:center;gap:var(--space-2);justify-content:center}
.leg{align-items:center;text-align:center;gap:var(--space-2);justify-content:center}
.leg .line{display:none}
.dot{display:none}
.city{font-family:var(--font-display);font-weight:700;font-size:var(--text-3xl);line-height:1.1}
.split{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-5)}
.split ul{list-style:none;margin:0;padding:0}
.split li{display:flex;flex-direction:column;gap:2px;padding:var(--space-2) 0}
.split li .l{font-size:var(--text-sm);letter-spacing:.04em;text-transform:uppercase}
.col{min-width:0;position:relative}
.col-h{font-family:var(--font-display);font-weight:700;font-size:var(--text-xl);margin:0 0 var(--space-2)}
.verdict{margin:0}
.src{margin:0;font-size:var(--text-sm);color:var(--color-text-muted)}
@media (max-width:767px){
 body{padding:var(--space-4) var(--space-4)}
 .route{grid-template-columns:1fr;gap:var(--space-5)}
 .split{grid-template-columns:1fr}
 .city{font-size:var(--text-2xl)}
}
"""

_CHALK_ARROW_R = _svg_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 24" fill="none" stroke="STEELHEX" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 15C12 5 24 5 35 12"/>'
    '<path d="M27 6l8 6-9 4"/></svg>')
_CHALK_ARROW_D = _svg_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 40" fill="none" stroke="STEELHEX" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3C19 12 19 24 12 35"/>'
    '<path d="M18 27l-6 8-4-9"/></svg>')
_CHALK_PATH_H = _svg_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 40" preserveAspectRatio="none" fill="none" '
    'stroke="STEELHEX" stroke-width="3" stroke-dasharray="9 8" stroke-linecap="round">'
    '<path d="M4 26C40 6 70 36 100 20S160 8 194 22"/><path stroke-dasharray="none" d="M184 12l11 10-13 5"/></svg>')
_CHALK_PATH_V = _svg_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 200" preserveAspectRatio="none" fill="none" '
    'stroke="STEELHEX" stroke-width="3" stroke-dasharray="9 8" stroke-linecap="round">'
    '<path d="M20 2C4 40 34 70 18 100S6 160 21 194"/><path stroke-dasharray="none" d="M10 186l11 10 6-13"/></svg>')

STYLE_CSS = {
    # STICKER — die-cut stickers on bone: white cards with a thick ink outline, a hard
    # offset shadow, a slight tilt each, brass number badges and the doodle-dog mascot.
    "sticker": """
body{background:var(--color-bone-100)}
.ig{gap:var(--space-6);padding:var(--space-2) var(--space-3) var(--space-3)}
.cap{font-size:var(--text-2xl);color:var(--color-steel-900);font-weight:700}
.cap .dog{flex:0 0 88px;width:88px;height:88px;background:var(--color-white);border:3px solid var(--color-ink);
 border-radius:50%;padding:8px 6px 0;box-shadow:4px 4px 0 var(--color-ink);transform:rotate(-7deg);overflow:hidden}
.items{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:var(--space-6) var(--space-5);
 align-content:start;padding:var(--space-3) var(--space-2) 0}
.it,.stop,.leg,.col,.verdict{background:var(--color-white);border:3px solid var(--color-ink);border-radius:var(--radius-lg);
 box-shadow:5px 5px 0 var(--color-ink)}
.it{padding:78px var(--space-5) var(--space-5);gap:var(--space-2)}
.it:nth-child(odd){transform:rotate(-1.2deg)}.it:nth-child(even){transform:rotate(1deg)}
.k{position:absolute;top:-18px;left:-10px;width:42px;height:42px;border-radius:50%;background:var(--color-cta);
 border:3px solid var(--color-ink);display:grid;place-items:center;font-weight:800;font-size:var(--text-sm);
 color:var(--color-ink);transform:rotate(-8deg)}
.ic{width:50px;height:50px;padding:11px;border-radius:16px;background:var(--color-brand-soft);
 border:2.5px solid var(--color-ink);color:var(--color-steel-700);transform:rotate(-5deg)}
.it .ic{position:absolute;top:14px;right:14px}
.v{font-size:var(--text-3xl);color:var(--color-steel-700)}
.ig-2 .v{font-size:var(--text-2xl);white-space:nowrap}
.l{font-size:var(--text-lg);color:var(--color-ink)}
.n{color:var(--color-ink-2)}
.ig-4 .items{grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:var(--space-5)}
.ig-4 .it{flex-direction:row;align-items:center;gap:var(--space-4);padding:var(--space-4) var(--space-5)}
.ig-4 .k{display:none}
.ig-4 .it .ic{position:static;flex:0 0 46px;height:46px;padding:10px;border-radius:50%;background:var(--color-cta);color:var(--color-ink)}
.ig-4 .it .l{font-size:var(--text-base);font-weight:600}
.ig-4 .it-shield{background:var(--color-brand-soft)}
.route{padding:var(--space-3) var(--space-2) var(--space-2)}
.route::before{content:"";position:absolute;left:12%;right:12%;top:50%;border-top:4px dashed var(--color-ink);z-index:0}
.stop,.leg{z-index:1;padding:var(--space-5)}
.stop-a{transform:rotate(-2deg)}.stop-b{transform:rotate(2deg)}
.leg{background:var(--color-cta-soft);transform:rotate(-1deg)}
.leg .v{font-size:var(--text-4xl)}
.leg .n{color:var(--color-ink)}
.stop .ic,.leg .ic{width:56px;height:56px}
.leg .ic{background:var(--color-white)}
.city{color:var(--color-steel-700)}
.split{padding:var(--space-2)}
.col{padding:var(--space-5)}
.col-b{background:var(--color-brand-soft)}
.col-a{transform:rotate(-.6deg)}.col-b{transform:rotate(.6deg)}
.col-h{display:inline-block;background:var(--color-cta);color:var(--color-ink);border:3px solid var(--color-ink);
 border-radius:var(--radius-pill);padding:2px 16px;font-size:var(--text-lg);transform:rotate(-2deg);margin-bottom:var(--space-3)}
.split li{border-top:2px dashed var(--color-rule)}
.split li .l{color:var(--color-ink-2)}
.split li .n{font-size:var(--text-base);color:var(--color-ink)}
.verdict{background:var(--color-surface-inverse);color:var(--color-text-on-inverse);padding:var(--space-4) var(--space-5);
 margin-top:var(--space-3)}
.src{padding:0 var(--space-2)}
@media (max-width:767px){
 .cap{font-size:var(--text-xl)}
 .cap .dog{flex-basis:68px;width:68px;height:68px}
 .items,.ig-4 .items{grid-template-columns:1fr;gap:var(--space-6)}
 .ig-4 .items{gap:var(--space-4)}
 .v{font-size:var(--text-2xl)}
 .route::before{left:50%;right:auto;top:6%;bottom:6%;border-top:0;border-left:4px dashed var(--color-ink)}
 .leg .v{font-size:var(--text-3xl)}
}
""",
    # CHALK — a sketchbook on bone graph paper: hand-drawn wobbly outlines, circled numbers,
    # wavy brass underlines, highlighter swipes behind the figures and doodled arrows.
    "chalk": """
body{background:var(--color-bone-100)}
.ig{gap:var(--space-6);padding:var(--space-6) var(--space-6) var(--space-5);background-color:var(--color-bone-50);
 background-image:linear-gradient(var(--color-steel-100) 1px,transparent 1px),linear-gradient(90deg,var(--color-steel-100) 1px,transparent 1px);
 background-size:28px 28px;background-position:-1px -1px}
.ig::before{content:"";position:absolute;inset:6px;border:2.5px solid var(--color-steel-700);
 border-radius:14px 4px 18px 6px / 6px 16px 4px 14px;filter:url(#wob);pointer-events:none}
.cap{font-size:var(--text-2xl);color:var(--color-steel-700);font-weight:700}
.cap-t{text-decoration:underline wavy var(--color-cta);text-decoration-thickness:2.5px;text-underline-offset:9px;
 text-decoration-skip-ink:none}
.cap .dog{flex:0 0 84px;width:84px;height:84px;filter:url(#wob)}
.cap .dog .dg-fur,.cap .dog .dg-ear{fill:var(--color-steel-100)}
.cap .dog .dg-pale{fill:var(--color-bone-50)}
.items{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:var(--space-7);align-content:start}
.it{padding:var(--space-5) var(--space-4) var(--space-4);gap:var(--space-2)}
.it::before,.stop::before,.leg::before,.col::before{content:"";position:absolute;inset:0;border:2.5px solid var(--color-steel-700);
 border-radius:18px 6px 22px 8px / 8px 20px 6px 18px;filter:url(#wob);pointer-events:none}
.it:nth-child(even)::before{border-radius:6px 20px 8px 18px / 18px 6px 20px 8px}
.k{width:44px;height:44px;display:grid;place-items:center;font-family:var(--font-display);font-weight:700;
 font-size:var(--text-lg);color:var(--color-steel-700);border:2.5px solid var(--color-steel-700);
 border-radius:52% 46% 55% 44% / 48% 55% 45% 52%;filter:url(#wob);margin-bottom:var(--space-1)}
.ic{position:absolute;top:var(--space-5);right:var(--space-4);width:34px;height:34px;color:var(--color-steel-700)}
.v{align-self:flex-start;font-size:var(--text-3xl);color:var(--color-steel-900);padding:0 6px;margin-left:-6px;
 background:linear-gradient(176deg,transparent 30%,var(--color-cta-soft) 31%,var(--color-cta-soft) 88%,transparent 89%)}
.ig-2 .v{font-size:var(--text-2xl);white-space:nowrap}
.l{font-size:var(--text-lg);color:var(--color-steel-700)}
.n{color:var(--color-ink-2)}
.ig-2 .it:not(:last-child)::after{content:"";position:absolute;top:30px;right:-40px;width:38px;height:24px;
 background:ARROW_R center/contain no-repeat}
.ig-4 .items{grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:var(--space-3) var(--space-7)}
.ig-4 .it{flex-direction:row;align-items:flex-start;gap:var(--space-3);padding:var(--space-2) 0 var(--space-3)}
.ig-4 .it::before{inset:auto 0 0 0;height:0;border-width:0 0 2px;border-radius:0}
.ig-4 .k{display:none}
.ig-4 .it .ic{position:static;flex:0 0 30px;height:30px;color:var(--color-steel-700)}
.ig-4 .l{font-size:var(--text-base);font-weight:600;color:var(--color-ink)}
.ig-4 .it-shield .l{background:linear-gradient(176deg,transparent 30%,var(--color-cta-soft) 31%,var(--color-cta-soft) 88%,transparent 89%)}
.route{gap:var(--space-5);align-items:center}
.stop{padding:var(--space-5) var(--space-3)}
.stop::before{border-radius:50% 46% 52% 44% / 46% 54% 44% 52%}
.stop .ic,.leg .ic{position:static;width:40px;height:40px}
.city{color:var(--color-steel-900)}
.stop .n{color:var(--color-ink-2)}
.leg{padding:var(--space-8) var(--space-3) var(--space-3)}
.leg::before{border:0;inset:6px -34px auto -34px;height:40px;border-radius:0;filter:none;background:PATH_H center/100% 100% no-repeat}
.leg .v{align-self:center;font-size:var(--text-4xl);margin:0}
.split{gap:var(--space-7)}
.col{padding:var(--space-5)}
.col-h{color:var(--color-steel-700);text-decoration:underline wavy var(--color-cta);text-decoration-thickness:2px;
 text-underline-offset:7px;margin-bottom:var(--space-3)}
.split li{border-top:2px dotted var(--color-steel-300)}
.split li:first-child{border-top:0}
.split li .l{color:var(--color-ink-3)}
.split li .n{font-size:var(--text-base);color:var(--color-ink)}
.verdict{position:relative;padding:var(--space-3) var(--space-5);color:var(--color-ink);font-size:var(--text-base);
 background:linear-gradient(178deg,transparent 4%,var(--color-cta-soft) 5%,var(--color-cta-soft) 95%,transparent 96%)}
@media (max-width:767px){
 .ig{padding:var(--space-5) var(--space-4) var(--space-4)}
 .cap{font-size:var(--text-xl);line-height:1.5}
 .cap-t{text-underline-offset:6px;text-decoration-thickness:2px}
 .cap .dog{flex-basis:56px;width:56px;height:56px}
 .items{grid-template-columns:1fr;gap:var(--space-8)}
 .ig-1 .items{gap:var(--space-5)}
 .ig-2 .it:not(:last-child)::after{top:auto;right:auto;left:50%;bottom:-42px;width:24px;height:38px;
  margin-left:-12px;background-image:ARROW_D}
 .ig-4 .items{grid-template-columns:1fr;gap:var(--space-2)}
 .v{font-size:var(--text-2xl)}
 .leg{padding:var(--space-4) var(--space-3) var(--space-4) 64px;align-items:flex-start;text-align:left;min-height:120px}
 .leg::before{inset:-20px auto -20px 6px;width:44px;height:auto;background-image:PATH_V}
 .leg .v{align-self:flex-start;font-size:var(--text-3xl)}
 .split{gap:var(--space-5)}
}
""".replace("ARROW_R", _CHALK_ARROW_R).replace("ARROW_D", _CHALK_ARROW_D)
   .replace("PATH_H", _CHALK_PATH_H).replace("PATH_V", _CHALK_PATH_V),
    # COMIC — a comic strip: heavy-bordered panels on a white page, the dog saying the title
    # in a speech bubble, brass caption boxes, speech-bubble labels and halftone dots.
    "comic": """
body{background:var(--color-bone-100)}
.ig{background:var(--color-white);border:4px solid var(--color-steel-900);box-shadow:7px 7px 0 var(--color-steel-900);
 padding:var(--space-5);gap:var(--space-5)}
.cap{font-size:var(--text-xl);color:var(--color-steel-900);font-weight:700;align-items:flex-end}
.cap .dog{flex:0 0 92px;width:92px;height:92px;border:3px solid var(--color-steel-900);border-radius:50%;
 padding:8px 6px 0;overflow:hidden;background-color:var(--color-cta-soft);
 background-image:radial-gradient(var(--color-cta) 22%,transparent 26%);background-size:9px 9px}
.cap-t{position:relative;background:var(--color-white);border:3px solid var(--color-steel-900);border-radius:26px;
 padding:var(--space-3) var(--space-5);margin-bottom:var(--space-5);flex:1 1 auto}
.cap-t::before{content:"";position:absolute;left:-17px;bottom:8px;width:24px;height:22px;background:var(--color-steel-900);
 clip-path:polygon(100% 0,0 100%,100% 70%)}
.cap-t::after{content:"";position:absolute;left:-10px;bottom:12px;width:16px;height:13px;background:var(--color-white);
 clip-path:polygon(100% 0,0 100%,100% 70%)}
.items{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:var(--space-3);align-content:start}
.it,.stop,.leg,.col{border:3px solid var(--color-steel-900);background:var(--color-white)}
.it::before,.stop::before,.leg::before,.col::before{content:"";position:absolute;top:0;right:0;width:min(60%,190px);height:120px;
 background-image:radial-gradient(var(--color-steel-300) 26%,transparent 30%);background-size:10px 10px;
 -webkit-mask-image:radial-gradient(circle at 100% 0,black 0,transparent 72%);mask-image:radial-gradient(circle at 100% 0,black 0,transparent 72%);
 pointer-events:none}
.it:nth-child(3n+2)::before{background-image:radial-gradient(var(--color-cta) 26%,transparent 30%)}
.it{padding:68px var(--space-4) var(--space-4);gap:var(--space-2)}
.k{position:absolute;top:0;left:0;background:var(--color-cta);color:var(--color-steel-900);font-weight:800;
 font-size:var(--text-sm);letter-spacing:.08em;padding:3px 12px;border-right:3px solid var(--color-steel-900);
 border-bottom:3px solid var(--color-steel-900)}
.ic{position:absolute;top:6px;right:8px;width:52px;height:52px;padding:13px;color:var(--color-steel-900);background:var(--color-cta);
 clip-path:polygon(50% 0,61% 18%,82% 9%,79% 31%,100% 38%,84% 54%,96% 74%,73% 75%,68% 98%,50% 84%,32% 98%,27% 75%,4% 74%,16% 54%,0 38%,21% 31%,18% 9%,39% 18%)}
.it .l{align-self:flex-start;position:relative;background:var(--color-white);border:2.5px solid var(--color-steel-900);
 border-radius:18px;padding:3px 14px;font-size:var(--text-lg);color:var(--color-steel-900);margin-bottom:8px;order:-1}
.it .l::after{content:"";position:absolute;left:18px;bottom:-11px;width:14px;height:11px;background:var(--color-steel-900);
 clip-path:polygon(0 0,100% 0,10% 100%)}
.v{font-size:var(--text-3xl);color:var(--color-steel-700);font-weight:800;text-shadow:3px 3px 0 var(--color-brass-200)}
.n{color:var(--color-ink)}
.it>.v,.it>.n,.stop>*,.leg>.v,.leg>.n,.col>ul,.leg>.ic,.stop>.ic{position:relative}
.ig-4 .items{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.ig-4 .it{flex-direction:row;align-items:center;gap:var(--space-4);padding:var(--space-4)}
.ig-4 .k{display:none}
.ig-4 .it .ic{position:static;flex:0 0 46px;height:46px;padding:12px}
.ig-4 .it .l{order:0;align-self:center;font-size:var(--text-base);font-weight:600;margin:0;border-radius:14px}
.ig-4 .it .l::after{left:-11px;top:50%;bottom:auto;margin-top:-6px;width:11px;height:12px;clip-path:polygon(100% 0,0 50%,100% 100%)}
.route{gap:var(--space-3)}
.stop,.leg{padding:var(--space-5) var(--space-4)}
.stop .ic,.leg .ic{position:static;width:56px;height:56px}
.city{color:var(--color-steel-900);font-weight:800;text-shadow:3px 3px 0 var(--color-brass-200)}
.leg{background:var(--color-steel-700);color:var(--color-bone-100)}
.leg::before{background-image:radial-gradient(var(--color-steel-500) 26%,transparent 30%)}
.leg .v{color:var(--color-cta);text-shadow:3px 3px 0 var(--color-steel-900);font-size:var(--text-4xl)}
.leg .n{color:var(--color-bone-100)}
.split{gap:var(--space-3)}
.col{padding:var(--space-8) var(--space-4) var(--space-4)}
.col-h{position:absolute;top:0;left:0;margin:0;background:var(--color-cta);color:var(--color-steel-900);
 font-size:var(--text-base);text-transform:uppercase;letter-spacing:.06em;padding:3px 14px;
 border-right:3px solid var(--color-steel-900);border-bottom:3px solid var(--color-steel-900)}
.split li .l{color:var(--color-steel-700)}
.split li .n{font-size:var(--text-base)}
.verdict{border:3px solid var(--color-steel-900);background:var(--color-steel-700);color:var(--color-bone-100);
 padding:var(--space-4) var(--space-5)}
@media (max-width:767px){
 .ig{padding:var(--space-4);box-shadow:5px 5px 0 var(--color-steel-900)}
 .cap{font-size:var(--text-lg)}
 .cap .dog{flex-basis:56px;width:56px;height:56px}
 .cap{gap:var(--space-3)}
 .cap-t{padding:var(--space-3) var(--space-4);margin-bottom:var(--space-4)}
 .items,.ig-4 .items{grid-template-columns:1fr}
 .v{font-size:var(--text-2xl)}
 .leg .v{font-size:var(--text-3xl)}
}
""",
}


#: Appended after every style: a figure drops a type step when its card is narrow, so it
#: keeps its own line and never runs under the card's icon or out of the card (the check in
#: scripts/ig_shots.mjs fails the measurement if one does).
FIT_CSS = """
.it{container-type:inline-size}
@container (max-width:250px){.it .fig{font-size:var(--text-2xl)}}
@container (max-width:205px){.it .fig{font-size:var(--text-xl)}}
"""


def _style_css(style_id: str, tokens: dict) -> str:
    """The style's CSS, with the drawn SVG decorations stroked in the token steel, then
    FIT_CSS."""
    ink = tokens.get("--color-steel-700", "currentColor").replace("#", "%23")
    return STYLE_CSS[style_id].replace("STEELHEX", ink) + FIT_CSS


def render_preview(slot_plan: dict, style_id: str, facts: dict, tokens: dict,
                   font_base: str = FONT_BASE) -> str:
    """A standalone HTML document: tokens inlined as :root, no script, no external requests.
    Every decoration (the doodle dog, the chalk wobble, arrows, halftone) is inline SVG or CSS;
    every figure is exact text from `facts`, never drawn."""
    ig = slot_plan.get("ig") or "IG-1"
    alt = slot_plan.get("alt") or _alt({**slot_plan, "facts": facts})
    root_css = ":root{" + ";".join(f"{k}:{v}" for k, v in tokens.items()) + "}"
    title = facts.get("title") or slot_plan.get("node") or slot_plan.get("heading", "")
    label = f'{slot_plan.get("slot")} · {ig} {IG_NAMES.get(ig, "")} · {style_id}'
    return (
        "<!doctype html>\n<html lang=\"en-GB\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(label)}</title>"
        f"<style>{_fonts(font_base)}{root_css}{BASE_CSS}{_style_css(style_id, tokens)}</style>"
        "</head><body>"
        f'<!-- BSUK Infographic: {esc(ig)} {esc(IG_NAMES.get(ig, ""))} | '
        f'{esc(slot_plan.get("page", ""))} | slot {esc(slot_plan.get("slot", ""))} | '
        f'style {esc(style_id)} -->'
        f'<figure class="ig {esc(ig.lower())} st-{esc(style_id)}" role="img" aria-label="{esc(alt)}">'
        f'<figcaption class="cap">{DOG}<span class="cap-t">{t(title)}</span></figcaption>'
        f"{_body(ig, facts)}</figure>"
        + (WOBBLE if style_id == "chalk" else "")
        + "</body></html>\n")


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


#: The widths the board shows every style at (build_page_board.PREVIEW_W pins the same three).
PREVIEW_WIDTHS = (1280, 768, 375)
SHOTS_JS = "scripts/ig_shots.mjs"
#: The asset row size (scripts/bake_images.py BOX) and the guide sibling's width.
BAKE_BOX = (1408, 768)
BAKE_SIB_W = 760
BAKE_DIR = "public/images/infographics"


def heights_path(slug: str) -> str:
    return f"{OUT_DIR}/{slug}/heights.json"


def browser_available(root: Path = ROOT) -> bool:
    """True when node and the repo's Playwright (with its Chromium) can run here."""
    import shutil
    import subprocess
    if not shutil.which("node") or not (Path(root) / "node_modules/@playwright/test").exists():
        return False
    try:
        r = subprocess.run(["node", "-e", "require('@playwright/test').chromium.executablePath()"
                            "&&process.exit(require('fs').existsSync(require('@playwright/test')"
                            ".chromium.executablePath())?0:1)"],
                           cwd=str(root), capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


class FigureDefect(RuntimeError):
    """A `.fig` (an exact figure) overflows its box or card, or touches an icon box."""


def _shots(mode: str, spec: dict, root: Path = ROOT) -> dict:
    import subprocess
    r = subprocess.run(["node", str(ROOT / SHOTS_JS), mode], cwd=str(ROOT),
                       input=json.dumps({"root": str(root), **spec}), capture_output=True,
                       text=True, timeout=600)
    if r.returncode == 3 and mode == "measure":
        bad = [f"{key} @{w}: {msg}" for key, per in json.loads(r.stdout).items()
               for w, m in per.items() for msg in m["problems"]]
        raise FigureDefect("a figure overflows or sits under an icon:\n  " + "\n  ".join(bad))
    if r.returncode:
        raise RuntimeError(f"{SHOTS_JS} {mode} failed: {r.stderr.strip()[-800:]}")
    return json.loads(r.stdout)


def measure_heights(board: dict, root: Path = ROOT) -> dict:
    """Render every written preview at PREVIEW_WIDTHS in Chromium (fonts served) and write
    heights.json: {"widths": [...], "heights": {slot: {style: {"<width>": px}}}}. Prints a
    warning for any preview wider than its viewport (a horizontal overflow).

    Raises FigureDefect, and writes nothing, when any `.fig` text overflows its box or its
    card or touches an icon box, at any width (scripts/ig_shots.mjs checks every preview)."""
    rows = plan(board, root)
    if not rows:
        return {}
    slug = rows[0]["page"]
    jobs = [{"key": f"{p['slot']}|{s['id']}", "path": preview_path(slug, p["slot"], s["id"]),
             "widths": list(PREVIEW_WIDTHS)} for p in rows for s in p["styles"]]
    got = _shots("measure", {"jobs": jobs}, root)
    heights: dict = {}
    for key, per in got.items():
        slot, style = key.split("|", 1)
        for w, m in per.items():
            heights.setdefault(slot, {}).setdefault(style, {})[str(w)] = m["h"]
            if m["sw"] > int(w):
                print(f"WARNING {key} overflows at {w}px: scroll width {m['sw']}", file=sys.stderr)
    out = {"widths": list(PREVIEW_WIDTHS), "heights": heights}
    f = Path(root) / heights_path(slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


def load_heights(slug: str, root: Path = ROOT) -> dict:
    """{slot: {style: {"<width>": px}}} from heights.json, or {} when it was never measured."""
    try:
        return json.loads((Path(root) / heights_path(slug)).read_text()).get("heights") or {}
    except (OSError, ValueError):
        return {}


def bake_infographic(slug: str, slot: str, style: str, out_dir=None, root: Path = ROOT) -> dict:
    """Bake ONE picked style of one slot for the built page: screenshot its preview at the
    asset row size (BAKE_BOX, 1408×768 viewport) and at BAKE_SIB_W (760) wide, in Chromium with
    the fonts served, and write `<slug>-<slot>-<style>.webp` and `…-760.webp` to `out_dir`
    (default public/images/infographics/), held to bake_images.py's size budget.

    WHEN: only after the breeder picks, one style per slot — at Task 9 or the Asset Gate
    (STOP 4). Never bake all three styles: an unpicked style is a board preview, not an asset.
    The screenshot is full page, never clipped; a graphic taller than 768px keeps its height
    (the returned dims say so). Returns {"full": path, "sib": path, "w", "h", "sib_w", "sib_h"}."""
    import tempfile
    sys.path.insert(0, str(ROOT / "scripts"))
    from PIL import Image
    import bake_images as BI
    out_dir = Path(out_dir) if out_dir is not None else Path(root) / BAKE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    src = preview_path(slug, slot, style)
    if not (Path(root) / src).exists():
        raise FileNotFoundError(f"no preview to bake: {src}")
    stem = f"{slug}-{slot}-{style}"
    with tempfile.TemporaryDirectory() as tmp:
        png_full, png_sib = Path(tmp) / "full.png", Path(tmp) / "sib.png"
        _shots("shoot", {"jobs": [
            {"path": src, "width": BAKE_BOX[0], "height": BAKE_BOX[1], "out": str(png_full)},
            {"path": src, "width": BAKE_SIB_W, "height": 400, "out": str(png_sib)}]}, root)
        full = BI._save_within_budget(Image.open(png_full).convert("RGB"),
                                      out_dir / f"{stem}.webp", allow_downscale=False)
        sib = BI._save_within_budget(Image.open(png_sib).convert("RGB"),
                                     out_dir / f"{stem}-760.webp", allow_downscale=False)
    return {"full": str(out_dir / f"{stem}.webp"), "sib": str(out_dir / f"{stem}-760.webp"),
            "w": full.width, "h": full.height, "sib_w": sib.width, "sib_h": sib.height}


def block(board: dict, root: Path | None = ROOT) -> str:
    """Board block 7c as markdown: the plan table, then per slot its three preview paths."""
    rows = plan(board, root)
    if not rows:
        return "No section needs an infographic: no heading matched an IG trigger.\n"
    lines = ["| Section | Heading | IG type | Why it is here |", "|---|---|---|---|"]
    for p in rows:
        cells = [p["section"], f"{p.get('node_level') or ''} {p['node']}".strip(),
                 f"{p['ig']} {IG_NAMES.get(p['ig'], '')}", p["why"]]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |")
    for p in rows:
        lines += ["", f"**{p['slot']}** ({p['ig']} {IG_NAMES.get(p['ig'], '')}) — pick one: "
                  f"radio `pick-ig:{p['slot']}`"]
        for s in p["styles"]:
            lines.append(f"- {s['label']}: `{preview_path(p['page'], p['slot'], s['id'])}`")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print("usage: infographic_plan.py <slug> [--write] [--heights]", file=sys.stderr)
        return 2
    f = ROOT / "data/boards" / f"{args[0]}.json"
    if not f.exists():
        print(f"no board: {f.relative_to(ROOT)}", file=sys.stderr)
        return 2
    board = json.loads(f.read_text())
    rows = plan(board)
    print(f"{'section':<18} {'slot':<26} {'IG':<5} {'node':<12} heading — why")
    for p in rows:
        node = f"{p.get('node_level') or ''} {p.get('node_path') or ''}".strip()
        print(f"{p['section']:<18} {p['slot']:<26} {p['ig']:<5} {node:<12} {p['node']} — {p['why']}")
    if "--write" in argv:
        for rel in write_previews(board):
            print("wrote", rel)
    if "--write" in argv or "--heights" in argv:
        if not browser_available():
            print("heights NOT MEASURED — node or Playwright's Chromium is unavailable; "
                  "the board falls back to a fixed scrolling frame", file=sys.stderr)
            return 1 if "--heights" in argv else 0
        measure_heights(board)
        print("wrote", heights_path(_slug(board)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
