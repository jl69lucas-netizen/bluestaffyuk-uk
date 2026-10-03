#!/usr/bin/env python3
"""original_slots.py — board block 7d, "Original photos": 4–5 of the site's REAL photos placed
on the body H2s and H3s they suit best, before any infographic or generated image is planned.

    python3 scripts/original_slots.py <slug>        # print the block 7d markdown for the board

THE RULING (answer board q06, 2026-10-02). "OG means ORIGINAL image, not AI-generated or
infographics." Scan the site for its real original images, use 4–5 of them per page, and
choose the sections that best suit an original image BEFORE deciding which sections need an
infographic or a generated image — H2 and H3 headers. The image order on a page is therefore
original photos → infographics → generated images (only for what is left). This module
replaces og_slots.py, which proposed GENERATED photos under the same block number; the rule 9
name guards it carried live on in scripts/generated_briefs.py.

INVENTORY. `inventory(root, board=None)` lists the real photos the site serves: one per stem
of data/image-manifest.json that exists under public/images (size siblings such as `-760` are
already folded there). The manifest records only measured sizes — no kind and no source — so a
graphic is recognised by its filename (FILENAME_MARKERS, regexes on the basename: `^og-` is
anchored so "dog-" never hits, an icon is a whole hyphen token) or by any alt the site shows it
with (ALT_MARKERS; "map", "icon", "graphic" as whole words with an optional plural). Puppy CARD crops (`-card-800`) and 4:5
PORTRAIT crops (`-portrait-4x5`) are real photos, but they are crops of a photo the inventory
already holds at full frame (`puppies/<name>-<name>1.webp`), so they are left out: offering a
crop beside its original would put the same photo up twice. Each item records its `path`, its
served `alt` (the alt this page's record already gives the file, else the first alt the built
site or data/verbatim shows it with, else ""), its pixel size read from the file header (PIL
when installed, else a stdlib WebP/PNG/JPEG header parser) and `used_on_page`: every image
slot of `board` that already shows it.

FIT. `fit(target, photo, board, taken=())` scores a (heading, photo) pair 0–100:

    overlap   WEIGHTS["per_term"] per distinct key word shared by the heading side and the
              photo side, capped at WEIGHTS["overlap_max"]. Heading side: the H2 heading, its
              entity ids and keyword lists (an H3: its own heading). Photo side: the served
              alt and the filename stem. Words are keyword_metrics.key_words, plural-folded,
              with the words every image on the site shares (image_candidates.GENERIC) and
              the question words (QUESTION_WORDS) dropped.
    intent    WEIGHTS["intent"] when the photo's subject matches the heading's intent
              (SUBJECTS: parents and dam for the litter, a van for delivery, a vet for health,
              a family at home for life, Kennel Club papers for paperwork, the breeder for
              the deposit and viewing). Given once, however many classes match.
    city      WEIGHTS["city"] when the photo names the board's own city (see CITIES).
    hero      WEIGHTS["hero"] when the photo is this page's hero image.
    taken     WEIGHTS["taken"] when the photo is already in another selected slot: one this
              proposal picked (`taken`), or an image slot this page's record already places
              under another heading (a repeat would need a new alt). Not added to `hero`.
    portrait  WEIGHTS["portrait"] when the photo is taller than it is wide.
    small     WEIGHTS["small"] when the photo is narrower than MIN_WIDTH px.

PICKER. `propose(board, n=5, root=None)` scores every eligible heading against every photo
and takes pairs greedily, best first: at most one per section, never a photo twice, never a
pair under FLOOR. Page uses and hero files are read once per call. Eligible headings are the body H2s (image_rules.body_sections: no hero,
counter, trust, contents, takeaways, review, FAQ, newsletter or form section) and the level-3
nodes under them. n is clamped to 4..5; a page with too few eligible sections or fitting
photos gets fewer, and the block says so. One slot is also the SHARE CARD at 1200×630
(IMAGE-DESIGNS.md §1, one per page): the best slot whose photo is at least 1200px wide, with
framing style A (Contain on Bone); when no proposed photo is that wide, the best slot with
style C (Editorial Split — a half-width photo panel, never upscaled past the photo's own
width), and the block says so (NO_WIDE). Each slot carries `slot`
(`orig-<section>` for an H2, `orig-<section>-<three key words of the H3>` for an H3),
`section`, `level`, `heading`, `photo`, `alt`, `fit` and `why` (the shared terms and the
matched subject).

CITIES. A photo whose filename or any served alt names a city other than the board's own is
never offered (excluded, not penalised: a Glasgow family is not a London family). The cities
are data/locations.json's, "UK" rows dropped and parentheticals stripped, matched as whole
words ("York" never matches "Yorkshire"). The board's own city is the row whose slug is the
board's; a board with no row has no own city, so every city-naming photo is left out.

ALT (working rule 11). The first use of a photo on a page keeps its served alt; every repeat
carries a NEW alt, never a copy. A photo the page already shows under another heading is a
repeat, so its alt reads NEW_ALT; a photo already at this same heading is that same use.

HAND-OFF. `claimed_sections(board, root)` is the list of section ids these photos claim;
infographic_plan.plan() reads it (plan Task 5) and skips those sections unless the breeder
adds an infographic there.

The board (build_page_board.og_block) renders one radio group per slot, `pick-og:<slot>`,
values use / swap / skip — "swap" asks for a different original photo, described in the
note `note-og:<slot>`. None of them is required for approval.
"""
from __future__ import annotations

import functools
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import image_candidates as IC  # noqa: E402
import image_designs  # noqa: E402
import image_rules as IR  # noqa: E402
from keyword_metrics import key_words  # noqa: E402
from term_density import md_table  # noqa: E402

#: Regexes searched in the file's BASENAME stem (no folder, no extension): `^og-` is anchored
#: so "dog-" never matches, and an icon is a whole hyphen-delimited token ("iconic" is not).
FILENAME_MARKERS = ("infographic", "comparison", "-vs-", "chart", "diagram", "steps",
                    "process", "logo", r"(?:^|-)icons?(?:-|$)", "generated", "^og-",
                    "-card-", "-portrait-")
ALT_MARKERS = ("infographic", "graphic", "illustrat", "icons", "montage", "map",
               "cover image", "silhouette", "visual comparison", "side-by-side",
               "quote displayed", "thank you message", "webpage")
#: Alt markers matched as whole words, a plural allowed ("map" must not hit "mapping",
#: "graphic" does hit "graphics"); the rest are substrings.
_WHOLE_WORD = frozenset({"map", "icons", "graphic"})

WEIGHTS = {"per_term": 10, "overlap_max": 50, "intent": 30, "city": 10, "hero": -40,
           "taken": -50, "portrait": -10, "small": -10}
MIN_WIDTH = 760
FLOOR = 20
N_MIN, N_MAX, N_DEFAULT = 4, 5, 5
SHARE_W, SHARE_H = 1200, 630
NEW_ALT = "NEW alt needed (repeat use, rule 11)"
NO_WIDE = "No photo is 1200px wide; the share card uses the Editorial Split panel."
NO_ALT = "NOT FETCHED — no served alt; NEW alt needed"
QUESTION_WORDS = frozenset("""
will can could should would does did i my me get which who where much many there here
has have had been being than then also just very own one each before after
""".split())

#: (subject, heading cue, photo cue). A heading that matches a cue and a photo (alt + filename)
#: that matches the same subject earn WEIGHTS["intent"].
SUBJECTS = (
    ("litter", r"\b(litters?|available|prices?|costs?|parents?|dams?|sires?|mother|father)\b",
     r"\b(dams?|sires?|litters?|mother|pups)\b"),
    ("delivery", r"\b(deliver\w*|collect\w*|journey|transport\w*|travel\w*|carlisle)\b",
     r"\b(deliver\w*|vans?|transport\w*|journey)\b"),
    ("health", r"\b(health\w*|vets?|vaccin\w*|tests?|tested)\b",
     r"\b(vets?|veterinar\w*|vaccin\w*|examination|check)\b"),
    ("paperwork", r"\b(paperwork|kennel club|registration|papers|kc)\b",
     r"\b(kennel club|kc|registration|papers)\b"),
    ("life", r"\b(living|life|lives|home|family|happy|temperament|aggressive|attached|flats?)\b",
     r"\b(family|children|child|owners?|home|living room)\b"),
    ("viewing", r"\b(deposit|viewing|see|video|visit\w*)\b",
     r"\b(breeder|enquiry|contact|holding)\b"),
)
USAGE = "usage: python3 scripts/original_slots.py <slug>   (reads data/boards/<slug>.json)"


# ── image header size ───────────────────────────────────────────────────────────────────
def _header_size(path):
    """(w, h) from a WebP, PNG or JPEG header with the stdlib, or None when unreadable."""
    try:
        with open(path, "rb") as f:
            head = f.read(64)
            if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
                return struct.unpack(">II", head[16:24])
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                kind = head[12:16]
                if len(head) < 30:
                    return None
                if kind == b"VP8X":
                    w = int.from_bytes(head[24:27], "little") + 1
                    h = int.from_bytes(head[27:30], "little") + 1
                    return w, h
                if kind == b"VP8 ":
                    w, h = struct.unpack("<HH", head[26:30])
                    return w & 0x3FFF, h & 0x3FFF
                if kind == b"VP8L":
                    b = int.from_bytes(head[21:25], "little")
                    return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
                return None
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        return None
                    if marker[1] in (0xD8, 0x01) or 0xD0 <= marker[1] <= 0xD7:
                        continue
                    (length,) = struct.unpack(">H", f.read(2))
                    if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                        _prec, h, w = struct.unpack(">BHH", f.read(5))
                        return w, h
                    f.seek(length - 2, 1)
    except (OSError, struct.error):
        return None
    return None


def image_size(path):
    """(w, h) of an image file: PIL when it is installed, else the stdlib header parser."""
    try:
        from PIL import Image
    except ImportError:
        return _header_size(path)
    try:
        with Image.open(path) as im:
            return im.size
    except Image.DecompressionBombError:
        return None                        # a bomb is unreadable, never parsed further
    except OSError:
        return _header_size(path)


# ── inventory ───────────────────────────────────────────────────────────────────────────
def _alt_hit(alt, marker):
    low = (alt or "").lower()
    if marker in _WHOLE_WORD:
        stem = marker[:-1] if marker.endswith("s") else marker
        return re.search(r"\b%ss?\b" % re.escape(stem), low) is not None
    return marker in low


def _name_hit(path, marker):
    return re.search(marker, Path(path).stem.lower()) is not None


def _is_graphic(path, alts):
    return (any(_name_hit(path, m) for m in FILENAME_MARKERS)
            or any(_alt_hit(a, m) for a in alts for m in ALT_MARKERS))


# ── cities ──────────────────────────────────────────────────────────────────────────────
def _words(text):
    return " ".join(re.findall(r"[a-z0-9]+", (text or "").lower()))


@functools.lru_cache(maxsize=4)
def _city_rows(root_s):
    """((slug, city), ...) from data/locations.json: the "UK" rows dropped, parentheticals
    stripped ("Glasgow (breeding dogs)" is Glasgow)."""
    f = Path(root_s) / "data" / "locations.json"
    rows = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    out = []
    for r in rows:
        city = re.sub(r"\s*\([^)]*\)", "", r.get("city") or "").strip()
        if city and city.upper() != "UK":
            out.append((r.get("slug", ""), city))
    return tuple(out)


def cities(root=None):
    """Every city the location pages name, once each."""
    return sorted({c for _s, c in _city_rows(str(Path(root or ROOT).resolve()))})


def own_city(board, root=None):
    """The board's own city: the data/locations.json row whose slug is the board's, else None."""
    slug = ((board or {}).get("meta") or {}).get("slug", "")
    slug = slug.rsplit("/", 1)[-1]
    for s, c in _city_rows(str(Path(root or ROOT).resolve())):
        if s == slug:
            return c
    return None


def cities_named(text, names):
    """The cities in `names` that `text` names as whole words ("York" is not "Yorkshire")."""
    w = " %s " % _words(text)
    return [c for c in names if " %s " % _words(c) in w]


@functools.lru_cache(maxsize=4)
def _site_photos(root_s):
    """The board-independent half of the inventory, read once per root."""
    root = Path(root_s)
    _used, alts = IC.usage_and_alts(root)
    mf = root / "data" / "image-manifest.json"
    manifest = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    out = []
    for stem in sorted(manifest):
        for ext in (".webp", ".png", ".jpg", ".jpeg"):
            f = root / "public" / "images" / (stem + ext)
            if f.is_file():
                break
        else:
            continue
        path = f"/images/{stem}{ext}"
        site_alts = alts.get(path, [])
        if _is_graphic(path, site_alts):
            continue
        size = image_size(f) or (0, 0)
        out.append({"path": path, "alt": site_alts[0] if site_alts else "",
                    "alts": site_alts, "w": size[0], "h": size[1]})
    return tuple(json.dumps(o) for o in out)


def _file_of(board, img):
    """The file an image slot shows: its own `file`, else its assets[] row's."""
    if img.get("file"):
        return IC.canonical(img["file"])
    row = IR.asset_row(board, img.get("slot")) or {}
    return IC.canonical(row.get("file")) if row.get("file") else None


def page_uses(board):
    """{file: [{slot, section, heading}]} for every image slot of `board` that shows a file."""
    out = {}
    for sec, node, img in IC.iter_slots(board or {}):
        f = _file_of(board, img)
        if f:
            out.setdefault(f, []).append({"slot": img.get("slot"), "section": sec.get("id"),
                                          "heading": (node or sec).get("heading", "")})
    return out


def _board_alts(board):
    """{file: alt} — the FIRST alt this page's record gives each file (its first use)."""
    out = {}
    for a in (board or {}).get("assets", []):
        if a.get("file") and a.get("alt"):
            out.setdefault(IC.canonical(a["file"]), a["alt"])
    return out


def inventory(root=None, board=None):
    """[{path, alt, w, h, used_on_page, own_city}] — the site's real photos (module doc).
    With a board, a photo whose filename or any served alt names a city OTHER than the
    board's own (data/locations.json) is left out — a Glasgow family never stands in for
    London; `own_city` is True when it names the board's own city."""
    root = Path(root or ROOT)
    uses = page_uses(board) if board else {}
    balts = _board_alts(board)
    names = cities(root) if board else []
    home = own_city(board, root) if board else None
    out = []
    for raw in _site_photos(str(root.resolve())):
        p = json.loads(raw)
        if p["path"] in balts and not _is_graphic(p["path"], [balts[p["path"]]]):
            p["alt"] = balts[p["path"]]
        elif p["path"] in balts:
            continue                       # this page's own alt names it a graphic
        named = set(cities_named(" ".join([Path(p["path"]).stem.replace("-", " ")]
                                          + p.get("alts", [p["alt"]]) + [p["alt"]]), names))
        if named - {home}:
            continue
        p.pop("alts", None)
        p["own_city"] = bool(home) and home in named
        p["used_on_page"] = uses.get(p["path"], [])
        out.append(p)
    return out


# ── fit ─────────────────────────────────────────────────────────────────────────────────
def _terms(text):
    out = set()
    for w in key_words(text):
        for raw in re.findall(r"[a-z0-9]+", w):
            if raw.isdigit():
                continue
            t = IC._fold(raw)
            if (len(t) > 1 and raw not in IC.GENERIC and t not in IC.GENERIC
                    and t not in QUESTION_WORDS and raw not in QUESTION_WORDS):
                out.add(t)
    return out


def _heading_side(target):
    parts = [target.get("heading", "")]
    if target.get("level") != 3:
        parts += [e.split(":", 1)[-1].replace("-", " ") for e in target.get("entities") or []]
        for words in (target.get("keywords") or {}).values():
            parts += list(words)
    out = set()
    for p in parts:
        out |= _terms(p)
    return out


def _photo_text(photo):
    stem = re.sub(r"[-_\d]+", " ", Path(photo["path"]).stem)
    return "%s %s" % (photo.get("alt", ""), stem)


def _photo_side(photo):
    return _terms(_photo_text(photo))


def subject_of(target, photo):
    """The first SUBJECTS class the heading and the photo both match, or None."""
    heading = (target.get("heading") or "").lower()
    text = _photo_text(photo).lower()
    for name, hcue, pcue in SUBJECTS:
        if re.search(hcue, heading) and re.search(pcue, text):
            return name
    return None


def hero_files(board):
    out = set()
    for sec in (board or {}).get("sections", []):
        if sec.get("shape") == "hero" or sec.get("id") in ("top", "hero"):
            for img in sec.get("images") or []:
                f = _file_of(board, img)
                if f:
                    out.add(f)
    return out


def _context(board):
    """(page_uses, hero_files) — read once per propose(), not once per pair."""
    return page_uses(board), hero_files(board)


def _elsewhere(uses, target, photo):
    """True when the page already shows `photo` in an image slot under another heading."""
    heading = target.get("heading", "")
    return any(u["heading"] != heading for u in uses.get(photo["path"], []))


def _parts(target, photo, board, taken=(), ctx=None):
    uses, heroes = ctx if ctx is not None else _context(board)
    raw = {IC._fold(w): w for w in re.findall(r"[a-z0-9]+", _photo_text(photo).lower())}
    shared = sorted(raw.get(t, t) for t in _heading_side(target) & _photo_side(photo))
    subject = subject_of(target, photo)
    score = min(WEIGHTS["overlap_max"], WEIGHTS["per_term"] * len(shared))
    score += WEIGHTS["intent"] if subject else 0
    notes = []
    if photo.get("own_city"):
        score += WEIGHTS["city"]
        shared = shared + ["(this city)"]
    if photo["path"] in heroes:
        score += WEIGHTS["hero"]
        notes.append("hero photo")
    elif photo["path"] in set(taken) or _elsewhere(uses, target, photo):
        score += WEIGHTS["taken"]
        notes.append("already in another slot")
    if photo.get("h", 0) > photo.get("w", 0):
        score += WEIGHTS["portrait"]
        notes.append("portrait")
    if photo.get("w", 0) < MIN_WIDTH:
        score += WEIGHTS["small"]
        notes.append("%dpx wide" % photo.get("w", 0))
    return max(0, min(100, score)), shared, subject, notes


def fit(target, photo, board, taken=()):
    """0–100: how well `photo` suits the heading `target` (a section, or a level-3 node)."""
    return _parts(target, photo, board, taken)[0]


# ── picker ──────────────────────────────────────────────────────────────────────────────
def eligible_sections(board):
    return [s for s in IR.body_sections(board) if s.get("id")]


def slot_id(section, node):
    if node is None:
        return "orig-%s" % section["id"]
    words = [w for w in key_words(node.get("heading", ""))
             if w not in IC.GENERIC and w not in QUESTION_WORDS]
    tail = "-".join(re.sub(r"[^a-z0-9]+", "", w) for w in words[:3]).strip("-")
    return "orig-%s-%s" % (section["id"], tail or "h3")


def alt_for(board, section, node, photo):
    """The served alt on a first use; NEW_ALT when the page already shows the photo under
    another heading (working rule 11)."""
    heading = (node or section).get("heading", "")
    uses = page_uses(board).get(photo["path"], [])
    elsewhere = [u for u in uses
                 if not (u["section"] == section.get("id") and u["heading"] == heading)]
    if elsewhere:
        return NEW_ALT
    return photo.get("alt") or NO_ALT


def _why(shared, subject, notes):
    bits = []
    if shared:
        bits.append("terms: " + ", ".join(shared[:4]))
    if subject:
        bits.append("subject: " + subject)
    if notes:
        bits.append("minus: " + ", ".join(notes))
    return "; ".join(bits) or "—"


def propose(board, n=N_DEFAULT, root=None):
    n = max(N_MIN, min(N_MAX, int(n)))
    photos = inventory(root, board)
    ctx = _context(board)
    pairs = []
    for order, sec in enumerate(eligible_sections(board)):
        targets = [(sec, None)] + [(sec, h3) for h3 in IR.body_h3s(sec)]
        for k, (s, node) in enumerate(targets):
            tgt = node if node is not None else s
            for p in photos:
                score, shared, subject, notes = _parts(tgt, p, board, ctx=ctx)
                if score >= FLOOR:
                    pairs.append((-score, order, k, p["path"], s, node, p, shared, subject,
                                  notes))
    pairs.sort(key=lambda t: t[:4])
    slots, used_secs, taken = [], set(), set()
    for neg, _o, _k, path, sec, node, p, shared, subject, notes in pairs:
        if len(slots) >= n:
            break
        if sec["id"] in used_secs or path in taken:
            continue
        used_secs.add(sec["id"])
        taken.add(path)
        slots.append({"slot": slot_id(sec, node), "section": sec["id"],
                      "level": "H3" if node is not None else "H2",
                      "heading": (node or sec).get("heading", ""), "photo": path,
                      "w": p["w"], "h": p["h"], "alt": alt_for(board, sec, node, p),
                      "fit": -neg, "why": _why(shared, subject, notes)})
    if slots:
        wide = [s for s in slots if s["w"] >= SHARE_W]
        card = wide[0] if wide else slots[0]
        card["share"] = {"w": SHARE_W, "h": SHARE_H, "og_style": "A" if wide else "C"}
    return slots


def share_slot(slots):
    """The slot that also makes the share card, or None."""
    return next((s for s in slots if s.get("share")), None)


def claimed_sections(board, root=None):
    """The section ids block 7d's original photos claim. infographic_plan.plan() reads this
    (plan Task 5) and leaves these sections without an infographic unless the breeder adds
    one."""
    return [s["section"] for s in propose(board, root=root)]


# ── block ───────────────────────────────────────────────────────────────────────────────
def block(board, root=None, n=N_DEFAULT):
    want = max(N_MIN, min(N_MAX, int(n)))
    slots = propose(board, n, root)
    names = image_designs.load()["og_names"]
    out = ["### Original photos (block 7d)", "",
           "The breeder's ruling (answer board q06, 2026-10-02): OG means ORIGINAL image — "
           "not AI-generated and not an infographic. These are 4–5 of the site's own real "
           "photos, placed on the H2 and H3 headings they suit best, chosen BEFORE any "
           "section is given an infographic or a generated image. A photo keeps its filename, "
           "path and served alt on its first use on this page; a repeat use needs a NEW alt, "
           "never a copy (working rule 11).", ""]
    if len(slots) < want:
        out += ["Only %d heading%s on this board fit%s an original photo well enough "
                "(fit %d or more), so %d %s proposed — fewer than the %d asked for."
                % (len(slots), "" if len(slots) == 1 else "s", "s" if len(slots) == 1 else "",
                   FLOOR, len(slots), "slot is" if len(slots) == 1 else "slots are", want), ""]
    rows = [[s["slot"], "%s · %s" % (s["level"], s["heading"]), s["photo"], s["alt"],
             str(s["fit"]), s["why"]] for s in slots]          # md_table escapes the pipes
    out += [md_table(["Slot", "Heading", "Photo", "Alt", "Fit", "Why"], rows) if rows
            else "_no heading on this board fits an original photo_", ""]
    card = share_slot(slots)
    if card:
        sh = card["share"]
        out += ["**Share card:** `%s`'s photo, recomposed at %d×%d with framing style %s "
                "(%s) — one per page (IMAGE-DESIGNS.md §1)."
                % (card["slot"], sh["w"], sh["h"], sh["og_style"],
                   names.get(sh["og_style"], "")), ""]
        if sh["og_style"] == "C":
            out += [NO_WIDE, ""]
    claimed = ", ".join("`%s`" % s["section"] for s in slots) or "none"
    out += ["**Sections these photos claim:** %s — the infographic plan skips these unless "
            "the breeder adds one." % claimed, "",
            "Each slot below has a use / swap / skip choice (`pick-og:<slot>`; swap asks for "
            "a different original photo, named in its note). None is required for approval."]
    return "\n".join(out)


def main(argv):
    if len(argv) != 1 or argv[0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 2
    path = ROOT / "data/boards" / ("%s.json" % argv[0])
    if not path.is_file():
        print("no board at %s\n%s" % (path.relative_to(ROOT), USAGE), file=sys.stderr)
        return 2
    try:
        board = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print("%s is not JSON: %s" % (path.relative_to(ROOT), e), file=sys.stderr)
        return 2
    print(block(board, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
