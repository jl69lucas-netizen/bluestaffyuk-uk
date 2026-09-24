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

WHAT IS NOT BODY. The fixed frame of docs/reference/location-page-template.md, spelled as
the record spells it: the hero (checked on its own), and every section whose shape is a
frame part — stats (counter), trust, nav/dial/sheet/strip (contents), takeaways, reviews,
faq, form, divider — or whose id is one scripts/query_coverage_check.py treats as frame
(`top`, `key-takeaways`, `newsletter`). An FAQ BLOCK is a section of shape `faq`, or any
section carrying `questions` (the older spelling: a standard section with id `faq`), and
every H3 inside one is a question, so FAQ-block H3s are never asked for an image. `video`
and `puppies` sections are exempt too: their media is the video or the puppy cards.
Body H3s are the level-3 nodes of a body section's tree, at any depth.

THE PICK. The board writes one radio group per slot, `pick-img:<slot>`, and the approve
button stores the answer as `approval.picks["img:<slot>"]` — outside `record_hash`, like
every pick, so choosing an image never un-approves the outline. The value is one of:

  file:/images/<path>        use a served file
  assets:<filename>          use a folder file (ingest it first)
  og:<A|B|C|D|E|H>           generate an OG photo in this style (not yet approved)
  og:<style>:<sha12>         THIS generated photo is approved: sha256 of its bytes, 12 hex
  ig:IG-<1-5>[:<sha12>]      the same two for an infographic

A generated image is approved only by the `:<sha12>` form, which names the exact bytes the
breeder saw: regenerate the file and the pick no longer matches, and the build gate fails.

WHERE A GENERATED FILE IS. A draft is written to
`data/boards/generated/<slug file>/<slot>.<webp|png|jpg>` (not public/, which ships whole),
and the approved file is copied into public/images and named in the slot's `assets[]` row
`file` (lifecycle, outside the hash). The build gate reads the served copy.
"""
import hashlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import image_candidates as IC  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ("existing", "assets-folder", "generate", "infographic")
OG_STYLES = ("A", "B", "C", "D", "E", "H")
IG_STYLES = ("IG-1", "IG-2", "IG-3", "IG-4", "IG-5")
PICK_PREFIX = "img:"
FRAME_SHAPES = frozenset({"stats", "trust", "nav", "dial", "sheet", "strip", "takeaways",
                          "reviews", "faq", "form", "divider"})
OWN_MEDIA_SHAPES = frozenset({"video", "puppies"})
FRAME_IDS = frozenset({"top", "key-takeaways", "newsletter"})
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

# The ids build_findings() can emit, and nothing else (a test drives every branch).
PICK_INVALID = "image-pick-invalid"
EXISTING_MISSING = "image-existing-missing"
ASSET_NOT_INGESTED = "image-asset-not-ingested"
GENERATED_UNAPPROVED = "image-generated-unapproved"
GENERATED_NOT_INGESTED = "image-generated-not-ingested"
BUILD_CHECK_IDS = frozenset({PICK_INVALID, EXISTING_MISSING, ASSET_NOT_INGESTED,
                             GENERATED_UNAPPROVED, GENERATED_NOT_INGESTED})


# ── which headings are body ───────────────────────────────────────────────────────────
def is_faq_block(section):
    return section["shape"] == "faq" or bool(section.get("questions"))


def body_sections(board):
    return [s for s in board["sections"]
            if s["shape"] != "hero" and s["shape"] not in FRAME_SHAPES
            and s["shape"] not in OWN_MEDIA_SHAPES and s["id"] not in FRAME_IDS
            and not is_faq_block(s)]


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
    """The generated image the board shows for a slot: the served copy, else the draft."""
    return served_file(board, slot, root) or draft_file(board, slot, root)


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
            elif file_sha(f) != p["sha"]:
                errs.append(f"slot {slot}: the generated image changed since the board showed it")
    return errs


def slots_needing_pick(board):
    """The `img:<slot>` radio groups the approve button refuses to leave empty."""
    return [PICK_PREFIX + img["slot"] for s, n, img in IC.iter_slots(board)
            if img.get("source") in ("generate", "infographic")]
