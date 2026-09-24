"""image_rules — an image under every body heading of a project 5 page (system-gaps build,
Task 10). The checks are registered in scripts/family_rules.py, so they bind location,
comparison and blog pages only and never the twelve pages built before this build.

THE RULE (user ruling G1, 2026-09-24). Every BODY H2 section and every BODY H3 carries at
least one image slot, an OG photo or an infographic, and the hero carries a photo. A slot
names where its image comes from (`source`):

  existing       a file the site already serves            needs `file` (/images/...)
  assets-folder  a file in the breeder's Assets/Images      needs `source_file`
  generate       a new OG photo per IMAGE-DESIGNS.md        needs `prompt` and `og_style`
  infographic    a new infographic per IMAGE-DESIGNS.md     needs `infographic_style`, kind infographic

WHAT IS NOT BODY. scripts/page_sections.py defines it once for every board script: the frame
shapes (the hero is checked on its own), the frame ids, and FAQ blocks (shape `faq`, or any
section carrying `questions`), whose H3s are questions and never asked for an image. This
rule also exempts page_sections.OWN_MEDIA_SHAPES, `video` and `puppies`: their media is the
video or the puppy cards. Body H3s are the level-3 nodes of a body section's tree, at any
depth.

THE PICK. The board writes one radio group per slot, `pick-img:<slot>`, and the approve
button stores the answer as `approval.picks["img:<slot>"]` — outside `record_hash`, like
every pick, so choosing an image never un-approves the outline. The value is one of:

  file:/images/<path>        use a served file
  assets:<filename>          use a folder file (ingest it first)
  og:<A|B|C|D|E|H>           generate an OG photo in this style (not yet approved)
  og:<style>:<sha12>         THIS generated photo is approved: sha256 of its bytes, 12 hex
  ig:IG-<1-5>[:<sha12>]      the same two for an infographic

THE ROW. Every slot, hero, H2 and H3, has its `assets[]` row (slot, kind, w, h, required)
from `boarded` on (`image-asset-row-missing`): ingest and publish only fill its `file` and
`status`, which sit outside the hash, and adding the row later would un-approve the page.

A generated image is approved only by the `:<sha12>` form, which names the exact bytes the
breeder saw: regenerate the file and the pick no longer matches, and the build gate fails.

WHERE A GENERATED FILE IS. A draft is written to
`data/boards/generated/<slug file>/<slot>.<webp|png|jpg>` (not public/, which ships whole),
and the approved file is copied into public/images and named in the slot's `assets[]` row
`file` (lifecycle, outside the hash). The build gate reads the served copy.
"""
import hashlib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import image_candidates as IC  # noqa: E402
import page_sections as PS  # noqa: E402  (one definition of frame, FAQ block and body)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ("existing", "assets-folder", "generate", "infographic")
OG_STYLES = ("A", "B", "C", "D", "E", "H")
IG_STYLES = ("IG-1", "IG-2", "IG-3", "IG-4", "IG-5")
PICK_PREFIX = "img:"
OWN_MEDIA_SHAPES = PS.OWN_MEDIA_SHAPES
SCOPE_STATUSES = ("boarded", "approved", "built", "released")
APPROVED_STATUSES = ("approved", "built", "released")
SLOT_ID = re.compile(r"^[a-z][a-z0-9-]*$")
# One path segment of a served file: a safe charset, and never `.` or `..` (no path escapes).
_SEGMENT = r"(?!\.\.?(?:/|$))[A-Za-z0-9._-]+"
FILE_PATH = rf"/images/{_SEGMENT}(?:/{_SEGMENT})*"
PICK = re.compile(rf"(?:file:(?P<file>{FILE_PATH})"
                  r"|assets:(?P<asset>(?!\.\.?$)[^/\\\x00-\x1f]+)"
                  rf"|og:(?P<og>{'|'.join(map(re.escape, OG_STYLES))})(?::(?P<ogsha>[0-9a-f]{{12}}))?"
                  rf"|ig:(?P<ig>{'|'.join(map(re.escape, IG_STYLES))})(?::(?P<igsha>[0-9a-f]{{12}}))?)")
DRAFT_EXTS = (".webp", ".png", ".jpg")

# Not a build-gate id: approval and board block 7b show it and refuse it (Task 12a).
ASSET_ROW_MISSING = "image-asset-row-missing"

# The ids build_findings() can emit, and nothing else (a test drives every branch).
PICK_INVALID = "image-pick-invalid"
EXISTING_MISSING = "image-existing-missing"
ASSET_NOT_INGESTED = "image-asset-not-ingested"
GENERATED_UNAPPROVED = "image-generated-unapproved"
GENERATED_NOT_INGESTED = "image-generated-not-ingested"
BUILD_CHECK_IDS = frozenset({PICK_INVALID, EXISTING_MISSING, ASSET_NOT_INGESTED,
                             GENERATED_UNAPPROVED, GENERATED_NOT_INGESTED})


# ── which headings are body ───────────────────────────────────────────────────────────
is_faq_block = PS.is_faq_block


def body_sections(board):
    """The shared body (page_sections), less the sections whose media is their own."""
    return [s for s in PS.body_sections(board) if s["shape"] not in OWN_MEDIA_SHAPES]


def body_h3s(section):
    """Every level-3 node of a body section's tree, at any depth, in outline order."""
    out = []

    def walk(nodes):
        for n in nodes:
            if n["level"] == 3:
                out.append(n)
            walk(n.get("children") or [])
    walk(section.get("tree") or [])
    return out


# ── a slot's own fields ───────────────────────────────────────────────────────────────
def slot_problems(image):
    """Why this slot's fields do not say where its image comes from. Empty means they do."""
    p = []
    if not SLOT_ID.fullmatch(image["slot"]):
        p.append("slot id is not lowercase letters, digits and hyphens")
    src = image.get("source")
    if src is None:
        p.append("names no source (existing, assets-folder, generate or infographic)")
    elif src == "existing" and not image.get("file"):
        p.append("source existing names no file")
    elif src == "assets-folder" and not image.get("source_file"):
        p.append("source assets-folder names no source_file")
    elif src == "generate":
        if not (image.get("prompt") or "").strip():
            p.append("source generate has no prompt")
        if not image.get("og_style"):
            p.append("source generate names no og_style")
        if image["kind"] != "photo":
            p.append("source generate on a slot whose kind is not photo")
    elif src == "infographic":
        if not image.get("infographic_style"):
            p.append("source infographic names no infographic_style")
        if image["kind"] != "infographic":
            p.append("source infographic on a slot whose kind is not infographic")
    return p


def picks(board):
    return (board.get("approval") or {}).get("picks") or {}


def slot_findings(board):
    """Part (a): the slots a boarded record owes, and what an approved one owes on top."""
    status = board["meta"]["status"]
    if status not in SCOPE_STATUSES:
        return []
    out = []
    heroes = [s for s in board["sections"] if s["shape"] == "hero"]
    if not heroes:
        out.append(("image-hero-photo", "FAIL", "the record has no hero section, and the hero carries a photo"))
    for h in heroes:
        if not any(i["kind"] == "photo" for i in h.get("images") or []):
            out.append(("image-hero-photo", "FAIL", f"hero {h['id']} plans no photo slot"))
    for s in body_sections(board):
        if not s.get("images"):
            out.append(("image-slot-missing", "FAIL",
                        f"section {s['id']} ({s['heading']!r}) is a body H2 and plans no image slot"))
        for n in body_h3s(s):
            if not n.get("images"):
                out.append(("image-slot-missing", "FAIL",
                            f"section {s['id']}: H3 {n['heading']!r} is a body H3 and plans no image slot"))
    seen = {}
    for s, n, img in IC.iter_slots(board):
        seen[img["slot"]] = seen.get(img["slot"], 0) + 1
        where = f"section {s['id']}" + (f", H3 {n['heading']!r}" if n is not None else "")
        for why in slot_problems(img):
            out.append(("image-slot-fields", "FAIL", f"slot {img['slot']} ({where}): {why}"))
    # Task 12a: the row ingest and publish fill. Either adding it later would change the
    # record hash and un-approve the page, so it is planned now, with the slot.
    for s, n, img in IC.iter_slots(board):
        if asset_row(board, img["slot"]) is None:
            where = f"section {s['id']}" + (f", H3 {n['heading']!r}" if n is not None else "")
            out.append((ASSET_ROW_MISSING, "FAIL",
                        f"slot {img['slot']} ({where}): no assets[] row plans it — add "
                        "{slot, kind, w, h, required} at boarding; ingest and publish only fill "
                        "its file and status"))
    for slot, count in sorted(seen.items()):
        if count > 1:
            out.append(("image-slot-duplicate", "FAIL",
                        f"slot {slot} is planned {count} times — a pick is keyed by slot, so each is unique"))
    if status in APPROVED_STATUSES:
        chosen = picks(board)
        for s, n, img in IC.iter_slots(board):
            if img.get("source") in ("generate", "infographic") and PICK_PREFIX + img["slot"] not in chosen:
                out.append(("image-pick-missing", "FAIL",
                            f"slot {img['slot']} (source {img['source']}): the approval names no "
                            f"image or style for it (picks[\"{PICK_PREFIX}{img['slot']}\"])"))
    return out


# ── what the build will use ───────────────────────────────────────────────────────────
def parse_pick(value):
    """{kind: file|assets|og|ig, value, style, sha} for a pick string, or None. The whole
    string must match: a trailing newline is not a pick."""
    m = PICK.fullmatch(value) if isinstance(value, str) else None
    if not m:
        return None
    if m["file"]:
        return {"kind": "file", "value": m["file"], "style": None, "sha": None}
    if m["asset"]:
        return {"kind": "assets", "value": m["asset"], "style": None, "sha": None}
    if m["og"]:
        return {"kind": "og", "value": None, "style": m["og"], "sha": m["ogsha"]}
    return {"kind": "ig", "value": None, "style": m["ig"], "sha": m["igsha"]}


def choice(image, pick):
    """What the build uses for this slot: the breeder's pick, else the record's own source."""
    if pick is not None:
        return parse_pick(pick)
    src = image.get("source")
    if src == "existing" and image.get("file"):
        return {"kind": "file", "value": image["file"], "style": None, "sha": None}
    if src == "assets-folder" and image.get("source_file"):
        return {"kind": "assets", "value": image["source_file"], "style": None, "sha": None}
    if src == "generate":
        return {"kind": "og", "value": None, "style": image.get("og_style"), "sha": None}
    if src == "infographic":
        return {"kind": "ig", "value": None, "style": image.get("infographic_style"), "sha": None}
    return None


def kind_problem(image, parsed):
    """Why a parsed pick's style cannot go on this slot's kind, or None. Shared by the
    approval (validate_image_picks) and the build gate (build_findings)."""
    if parsed["kind"] == "og" and image["kind"] != "photo":
        return f"an OG style is a photo style and this slot is an {image['kind']}"
    if parsed["kind"] == "ig" and image["kind"] != "infographic":
        return f"an infographic style on a {image['kind']} slot"
    return None


def file_sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()[:12]


def _inside(path, base):
    """True when `path`, symlinks followed, resolves strictly inside `base`."""
    try:
        real, top = path.resolve(), base.resolve()
    except (OSError, RuntimeError):
        return False
    return top in real.parents


def public_path(file, root=None):
    """The path under <root>/public/images a served `/images/...` URL names, or None when it
    names anything else: not an /images/ path, a `.`/`..` segment, or a symlink that
    resolves out of public/images. Callers still check is_file()."""
    root = pathlib.Path(root or ROOT)
    if not isinstance(file, str) or not re.fullmatch(FILE_PATH, file):
        return None
    p = root / "public" / file.lstrip("/")
    return p if _inside(p, root / "public" / "images") else None


def public_file(file, root=None):
    """public_path(), only when it is a regular file."""
    p = public_path(file, root)
    return p if p is not None and p.is_file() else None


def asset_row(board, slot):
    return next((a for a in board.get("assets", []) if a.get("slot") == slot), None)


def served_file(board, slot, root=None):
    """The public/images copy the slot's `assets[]` row names, or None when it names no
    regular file there."""
    row = asset_row(board, slot)
    return public_file(row["file"], root) if row and row.get("file") else None


def draft_file(board, slot, root=None):
    """The generated draft of a slot under data/boards/generated, or None. A slot id that is
    not a slot id, or a draft symlinked out of that folder, is no draft."""
    if not SLOT_ID.fullmatch(slot):
        return None
    base = pathlib.Path(root or ROOT) / "data" / "boards" / "generated"
    d = base / IC.slug_file(board["meta"]["slug"])
    return next((d / (slot + e) for e in DRAFT_EXTS
                 if (d / (slot + e)).is_file() and _inside(d / (slot + e), base)), None)


def generated_file(board, slot, root=None):
    """The generated image the board shows for a slot: the draft, else the served copy (the
    order board_images() previews them in), so an approved new draft is checked against
    itself and never against an older served copy."""
    return draft_file(board, slot, root) or served_file(board, slot, root)


def ingested(board, slot, filename, root=None):
    """True when a folder file is in public/images: at the path the slot's `assets[]` row
    names, or at the ingest step's default name for it."""
    return served_file(board, slot, root) is not None or \
        public_file(IC.ingest_target(filename), root) is not None


def build_findings(board, root=None):
    """Part (c): on an approved record, every slot resolves to a file the build may use."""
    if board["meta"]["status"] not in APPROVED_STATUSES:
        return []
    root = pathlib.Path(root or ROOT)
    out = []
    chosen = picks(board)
    for s, n, img in IC.iter_slots(board):
        slot = img["slot"]
        raw = chosen.get(PICK_PREFIX + slot)
        if raw is not None and parse_pick(raw) is None:
            out.append((PICK_INVALID, "FAIL", f"slot {slot}: pick {raw!r} is not a known image pick"))
            continue
        c = choice(img, raw)
        if c is None:
            continue                                   # slot_findings() already names it
        why = kind_problem(img, c)
        if why:
            out.append((PICK_INVALID, "FAIL", f"slot {slot}: {why}"))
        elif c["kind"] == "file" and public_file(c["value"], root) is None:
            out.append((EXISTING_MISSING, "FAIL",
                        f"slot {slot}: {c['value']} is not in public/images — a served file is reused, never invented"))
        elif c["kind"] == "assets" and not ingested(board, slot, c["value"], root):
            out.append((ASSET_NOT_INGESTED, "FAIL",
                        f"slot {slot}: folder file {c['value']!r} was never ingested into public/images "
                        f"(expected {IC.ingest_target(c['value'])} or the slot's assets[].file)"))
        elif c["kind"] in ("og", "ig") and c["style"] is not None:   # no style: slot_findings() names it
            if c["sha"] is None:
                out.append((GENERATED_UNAPPROVED, "FAIL",
                            f"slot {slot}: style {c['style']} is chosen, but no generated image has been "
                            "approved on the board — generate it, re-board, and approve the image"))
                continue
            f = served_file(board, slot, root)
            if f is None:
                out.append((GENERATED_NOT_INGESTED, "FAIL",
                            f"slot {slot}: the approved image is not in public/images and named in "
                            "the slot's assets[].file yet"))
                continue
            sha = file_sha(f)
            if sha != c["sha"]:
                out.append((GENERATED_UNAPPROVED, "FAIL",
                            f"slot {slot}: {f.relative_to(root).as_posix()} is not the image the breeder approved "
                            f"(sha {sha} vs approved {c['sha']})"))
    return out


# ── the approval ───────────────────────────────────────────────────────────────────────
def validate_image_picks(board, chosen, root=None, assets_dir=None):
    """Every reason the `img:` picks of an approval cannot be accepted, as printable lines.
    Read by scripts/board_approve.py, which refuses the whole approval on any."""
    root = root or ROOT
    assets_dir = pathlib.Path(assets_dir) if assets_dir else IC.ASSETS_DIR
    slots = {img["slot"]: img for s, n, img in IC.iter_slots(board)}
    errs = []
    for key, value in sorted(chosen.items()):
        if not key.startswith(PICK_PREFIX):
            continue
        slot = key[len(PICK_PREFIX):]
        img = slots.get(slot)
        if img is None:
            errs.append(f"approval picks image slot {slot!r}, which the record does not plan")
            continue
        p = parse_pick(value)
        if p is None:
            errs.append(f"slot {slot}: pick {value!r} is not file:, assets:, og: or ig:")
        elif p["kind"] == "file" and public_file(p["value"], root) is None:
            errs.append(f"slot {slot}: {p['value']} is not in public/")
        elif p["kind"] == "assets" and not ((assets_dir / p["value"]).is_file()
                                            or ingested(board, slot, p["value"], root)):
            errs.append(f"slot {slot}: {p['value']!r} is neither in {assets_dir} nor ingested")
        elif why := kind_problem(img, p):
            errs.append(f"slot {slot}: {why}")
        elif p["kind"] in ("og", "ig") and p["sha"] is not None:
            f = generated_file(board, slot, root)
            if f is None:
                errs.append(f"slot {slot}: approves a generated image, and none exists for this slot")
            elif (sha := file_sha(f)) != p["sha"]:
                msg = (f"slot {slot}: the pick approves sha {p['sha']}, but the board shows "
                       f"{f.relative_to(pathlib.Path(root)).as_posix()} (sha {sha})")
                served = served_file(board, slot, root)
                if served is not None and served != f:
                    msg += ("; a newer draft replaces the served copy; approve the draft, or remove "
                            "it to keep the served image")
                errs.append(msg)
    return errs


def slots_needing_pick(board):
    """The `img:<slot>` radio groups the approve button refuses to leave empty."""
    return [PICK_PREFIX + img["slot"] for s, n, img in IC.iter_slots(board)
            if img.get("source") in ("generate", "infographic")]
# ── Task 10b: the board's "7. Images & styles" block ──────────────────────────────────
# Rendered by scripts/build_page_board.py for location, comparison and blog records only.
# One radio group per slot, `pick-img:<slot>`: the board's approve script already collects
# every `pick-*` radio into `approval.picks`, so the answer lands as picks["img:<slot>"]
# with no change to the approve contract, and board_approve.py validates it.
import base64  # noqa: E402
import html as _html  # noqa: E402
import io  # noqa: E402

THUMB_W = 240
PREVIEW_W = 480
GENERATED = ("generate", "infographic")
BLOCK_CSS = (
    "<style>.imgpick{border:1px solid var(--line);border-radius:8px;padding:10px 12px 12px;margin:10px 0;"
    "background:var(--paper);min-width:0}.imgpick legend{font-size:13px;font-weight:600;color:var(--ink-2);padding:0 6px}"
    ".imgc{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;margin:6px 0}"
    ".imgopt{display:grid;gap:4px;border:1px solid var(--line);border-radius:6px;padding:6px;font-size:12px;cursor:pointer}"
    ".imgopt img,.imgopt .nothumb{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:4px;background:var(--code-bg)}"
    ".imgopt .nothumb{display:grid;place-items:center;color:var(--ink-3)}"
    ".imgopt:has(input:checked){outline:3px solid var(--clay);outline-offset:1px}"
    ".imgstyles{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;font-size:13px;margin:6px 0}"
    ".imgstyles label{padding:10px 6px;min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center}"
    ".imggen img{max-width:min(100%,480px);border-radius:6px;display:block;margin:6px 0}"
    ".imgwhy{font-size:12px;color:var(--ink-3);margin:2px 0 4px}.imgwarn{color:var(--warn);font-weight:600}"
    "@media (max-width:640px){.imgc{grid-template-columns:repeat(2,minmax(0,1fr))}}</style>")


def thumb_uri(path, width=THUMB_W):
    """A small WebP data URI of an image file, or None when the file cannot be read. The
    board is a standalone Artifact, so /images/ paths resolve to nothing inside it."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            im.draft("RGB", (width, width * 2))        # a JPEG decodes at a reduced scale
            im.thumbnail((width, width * 2))          # shrink first, then the RGB copy
            im = im.convert("RGB")
            buf = io.BytesIO()
            im.save(buf, "WEBP", quality=70)
    except (OSError, ValueError, Image.DecompressionBombError):
        return None                                   # shown as a labelled box instead
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def style_labels(root=None):
    """IMAGE-DESIGNS.md's label map (data/design/image-styles.json, written by
    scripts/image_designs.py): {"og": {id: {"name", "use"}}, "infographic": {…}}, or {} when the
    file is missing or unreadable, and the board falls back to the bare ids."""
    p = pathlib.Path(root or ROOT) / "data" / "design" / "image-styles.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return _label_map(data)


def _label_map(data):
    """Only the well-shaped part of a label map: {group: {id: {"name": str, "use": str}}}.
    Anything else (a list, a bare string, a non-string name) is dropped, so a wrong-shape
    file falls back to the bare ids instead of breaking the board."""
    out = {}
    for grp, entries in (data.items() if isinstance(data, dict) else ()):
        if not isinstance(entries, dict):
            continue
        good = {k: v for k, v in entries.items()
                if isinstance(v, dict) and isinstance(v.get("name"), str) and isinstance(v.get("use"), str)}
        if good:
            out[grp] = good
    return out


def board_images(board, root=None, assets_dir=None, per_pool=3):
    """Everything block 7 shows for one record: the candidate report, a thumbnail per
    candidate, and a preview of each generated image that exists."""
    root = root or ROOT
    assets_dir = pathlib.Path(assets_dir) if assets_dir else IC.ASSETS_DIR
    report = IC.candidates(board, root, assets_dir, per_pool)
    thumbs = {}
    for s in report["slots"]:
        for c in s["candidates"]:
            src = public_path(c["file"], root) if c["file"] else assets_dir / c["asset"]
            if c["pick"] not in thumbs:
                # public_path() is None for a path outside public/images: no thumbnail, no read.
                thumbs[c["pick"]] = src and thumb_uri(src)
    generated = {}
    for s, n, img in IC.iter_slots(board):
        f = draft_file(board, img["slot"], root) or \
            (served_file(board, img["slot"], root) if img.get("source") in GENERATED else None)
        if f is not None:
            generated[img["slot"]] = {"sha": file_sha(f), "uri": thumb_uri(f, PREVIEW_W),
                                      "path": f.relative_to(root).as_posix()}
    return {"report": report, "thumbs": thumbs, "generated": generated, "styles": style_labels(root)}


def _e(v):
    """Record text for the board, escaped and on one line: block 7 sits in Markdown, where a
    blank line inside the HTML ends the HTML block and breaks the slot's fieldset."""
    return _html.escape(" ".join(("" if v is None else str(v)).split()), quote=True)


def _radio(name, value, checked):
    # The value is escaped but NOT collapsed: it is the exact pick the approval stores.
    v = _html.escape(value, quote=True)
    return f'<input type="radio" name="{_e(name)}" value="{v}"{" checked" if checked else ""}>'


def _slot_html(board, sec, node, img, row, images, current):
    slot = img["slot"]
    name = "pick-" + PICK_PREFIX + slot
    where = _e(sec["heading"]) + (" › " + _e(node["heading"]) if node else "")
    rec = [f"source {img.get('source') or 'not named'}"]
    for k in ("file", "source_file", "og_style", "infographic_style"):
        if img.get(k):
            rec.append(f"{k} {img[k]}")
    parts = [f'<fieldset class="imgpick" id="img-{_e(slot)}"><legend>{_e(slot)} · {_e(img["kind"])} · {where}</legend>',
             f'<p class="imgwhy">record: {_e(", ".join(rec))} · prompt: {_e(img.get("prompt"))}</p>']
    cands = row["candidates"] if row else []
    suggested = (row or {}).get("suggested") or {}
    # Task 10c: the file the record already names is pre-checked until a pick says otherwise,
    # except on a generated slot, whose answer is always the breeder's.
    precheck = current is None and img.get("source") not in GENERATED
    if cands:
        cells = []
        for c in cands:
            # A current file that is not on disk is offered, labelled, and never ticked.
            checked = current == c["pick"] or (precheck and c.get("current", False) and not c.get("missing"))
            uri = images["thumbs"].get(c["pick"])
            pic = f'<img src="{uri}" alt="{_e(c["alt"])}">' if uri else f'<span class="nothumb">{_e(c["file"] or c["asset"])}</span>'
            star = "⭐ " if c["pick"] == suggested.get("pick") else ""
            note = (f'<span class="imgwarn">needs ingest → {_e(c["ingest_as"])}</span>' if c["pool"] == "assets"
                    else f'<span class="why">{_e(c["file"])}'
                         + (f' · also on {_e(", ".join(c["used_on"]))}' if c["used_on"] else "") + "</span>")
            what = ("the file this slot names now" if c.get("current")
                    else f'score {c["score"]} · {_e(", ".join(c["matched"]))}')
            cells.append(f'<label class="imgopt">{pic}<span>{_radio(name, c["pick"], checked)} '
                         f'{star}<b>{_e(c["pool"])}{" · missing" if c.get("missing") else ""}</b> · {what}</span>{note}</label>')
        parts.append(f'<div class="imgc">{"".join(cells)}</div>')
    else:
        parts.append('<p class="imgwhy">No existing image shares a word with this slot — pick a style to generate one.</p>')
    if img["kind"] == "infographic":
        label, styles, prefix, want = "Or make an infographic, style", IG_STYLES, "ig:", img.get("infographic_style")
    else:
        label, styles, prefix, want = "Or generate an OG photo, style", OG_STYLES, "og:", img.get("og_style")
    named = _label_map(images.get("styles")).get("infographic" if prefix == "ig:" else "og", {})

    def _style(st):
        lab = named.get(st) or {}
        title = f' title="{_e(lab["use"])}"' if lab.get("use") else ""
        text = _e(st) + (f' · {_e(lab["name"])}' if lab.get("name") else "")
        return (f'<label{title}>{_radio(name, prefix + st, current == prefix + st)} '
                f'{"⭐ " if st == want else ""}{text}</label>')
    opts = " ".join(_style(st) for st in styles)
    parts.append(f'<div class="imgstyles"><span>{label} (IMAGE-DESIGNS.md):</span> {opts}</div>')
    gen = images["generated"].get(slot)
    if gen:
        cur = parse_pick(current) if current else None
        style = (cur["style"] if cur and cur["kind"] in ("og", "ig") else None) or want or styles[0]
        value = f"{prefix}{style}:{gen['sha']}"
        pic = f'<img src="{gen["uri"]}" alt="Generated draft for {_e(slot)}">' if gen["uri"] else ""
        parts.append(f'<div class="imggen"><label>{_radio(name, value, current == value)} '
                     f'<b>Approve this generated image</b> (style {_e(style)}, {_e(gen["path"])}, sha {gen["sha"]})</label>{pic}</div>')
    parts.append("</fieldset>")
    return "".join(parts)


def board_block(board, images):
    """Block 7's image pickers, or "" for a record the rule does not bind (images is None)."""
    if images is None:
        return ""
    rows = {r["slot"]: r for r in images["report"]["slots"]}
    chosen = picks(board)
    pools = images["report"]["pools"]
    head = (f"{BLOCK_CSS}\n\n**Pick one image for every slot.** The page's own images come first "
            f"({pools['own']}), then the site's other served images ({pools['served']}), then your Assets "
            f"folder ({pools['assets']} not yet on the site; those are copied in before the build). ⭐ marks the "
            "suggestion; **current** is the file the slot names now, offered first and ticked until you "
            "pick another. Hover a style for when it is used (IMAGE-DESIGNS.md). Or pick a style and a new image is generated for the slot; it is used only after "
            "you approve the generated image itself here, on a later pass of this board.")
    body = [_slot_html(board, s, n, img, rows.get(img["slot"]), images, chosen.get(PICK_PREFIX + img["slot"]))
            for s, n, img in IC.iter_slots(board)]
    return head + "\n\n" + "\n\n".join(body)
