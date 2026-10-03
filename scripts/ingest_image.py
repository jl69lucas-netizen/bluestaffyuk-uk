#!/usr/bin/env python3
"""Bring a new image onto BlueStaffyUK: IMAGE-DESIGNS.md §6 and §9, as five commands.

  folder   a photo from the breeder's folder -> public/images/<stem>.webp (+ -760 sibling)
  draft    a generated master -> data/boards/generated/<slug file>/<slot>.webp, the exact
           bytes the board shows for approval; prints their sha12 and the pick that approves
           (--sibling: an infographic's 760-wide phone layout, stored beside it as
           <slot>-760.webp)
  phone    an infographic's phone layout (drawn at the width it paints at on a phone, at 2x:
           infographic_plan.bake_infographic) -> data/boards/generated/<slug file>/<slot>-phone.webp,
           a draft of its own beside the slot's box draft, which it never touches; prints its
           sha12 and the pick that approves it, `img:<slot>-phone` = `ig:IG-<n>:<sha12>`
  publish  after the board approved THOSE bytes (pick `og:<style>:<sha12>` or
           `ig:IG-<n>:<sha12>`), copies them UNCHANGED into public/images/<stem>.webp, and the
           draft's own sibling, when it has one, unchanged as the -760 file
  publish-phone  after the board approved an infographic's phone layout (pick
           `img:<slot>-phone` = `ig:IG-<n>:<sha12>`, IG-<n> the box pick's own style), copies
           THOSE bytes unchanged to public/images/<box stem>-phone.webp: a NEW file beside the
           box and its -760 sibling, never in their place. The box is published first. It is
           folded into the box's own rows, as the -760 sibling is: `phone` on its
           data/image-ingest.json row, `phone_w`/`phone_h` on its manifest row (a stem of its own
           would put an infographic in the served-photo pools). The board is not touched: a
           phone layout has no assets[] row.

Every command that writes to public/images/ also bakes the `-760` sibling, adds the measured
row to data/image-manifest.json, records the image in data/image-ingest.json (the ledger this
script owns, which `npm run bake` carries over through ingested_manifest_rows()), and, when
given a board and slot, sets that slot's EXISTING `assets[]` row `file` and `status: "baked"`
(both outside the record hash, so the approval stands). It never adds an `assets[]` row:
that would change the hash and un-approve the page.

CLAUDE.md rule 11: an image already served is never renamed, moved, re-encoded or deleted.
A stem already in public/images/ (a file or a symlink, dangling included) or in the manifest
is REFUSED (exit 2); the master is only ever read.

Size budget (rules/images.md): the full image must fit 95 KB and the -760 sibling 55 KB at
the q60 floor, or the request is REFUSED and nothing is written. A native-ratio image is
at most 1408 wide and 1760 tall.

Every write is staged: images are encoded to temp files beside their targets and the JSON
(ledger, manifest, board) to temp files too; only when every encode succeeded are they moved
into place with os.replace, images first, then ledger, manifest, board. On any failure the
temp files are removed and nothing on the site has changed.

Framing (IMAGE-DESIGNS.md §7): --og-style A|B|E is baked into the 1408x768 box by
scripts/reframe_og.py (A contain, B blurfill with --mobcrop, E topcover); C|D|H are CSS
components, baked at native ratio up to 1408 wide; --infographic IG-n is framed with A.

Style B is retired for in-body images on new pages (user ruling 2026-09-26: "No grey or
black bleed on phones"): it is REFUSED for any page not in family_rules
BUILT_BEFORE_SYSTEM_GAPS, and for `folder` without --board, which cannot know the page.
The twelve built pages keep B, so their existing images can be re-ingested.

Usage:
  python3 scripts/ingest_image.py folder <master> [--stem <seo-stem>] --og-style A
        [--board <slug> --slot <slot>] [--dry-run]
  python3 scripts/ingest_image.py draft <master> --board <slug> --slot <slot> --og-style A
  python3 scripts/ingest_image.py draft <master> --board <slug> --slot <slot> --infographic IG-2
        [--sibling <760-wide phone bake>]
  python3 scripts/ingest_image.py phone <phone master> --board <slug> --slot <slot> --infographic IG-2
  python3 scripts/ingest_image.py publish --board <slug> --slot <slot> --stem <seo-stem>
  python3 scripts/ingest_image.py publish-phone --board <slug> --slot <infographic slot>
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile

from PIL import Image

import family_rules
import image_candidates
import image_designs
import image_rules
import reframe_og

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = "data/image-ingest.json"
MANIFEST = "data/image-manifest.json"
IMAGES = "public/images"
DRAFTS = "data/boards/generated"
MASTER_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")
DRAFT_EXTS = (".webp", ".png", ".jpg")
NATIVE_MAX_H = 1760
FILL_MIN = 0.85
# A phone layout is drawn at the CSS width it paints at on a phone (about 300-380px) at
# 1.5-2x: 440-800 pixels wide. Its text is gated where it is drawn (infographic_plan.bake_infographic
# measures it at the size it reaches the screen); this only refuses a file of the wrong kind.
PHONE_W = (440, 800)

# 3 to 10 lowercase words joined by single hyphens: what the pipeline's SEO filename
# convention produces, and nothing a camera or a download names a file by default.
SEO_STEM = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){2,9}$")
GENERIC = {"img", "image", "photo", "pic", "dsc", "screenshot", "untitled", "copy",
           "final", "file", "name", "new", "edit"}
SLOT_ID = image_rules.SLOT_ID                 # the gate's rule, matched whole
SLUG = re.compile(r"^[a-z0-9-]+(/[a-z0-9-]+)*$")
BAKED = {"A": "contain", "B": "blurfill", "E": "topcover"}
NATIVE = {"C", "D", "H"}
RETIRED_B = ("style B (blurfill) is retired for in-body images — user ruling 2026-09-26: "
             "no grey or black bleed on phones; use A (contain, bone gradient) or E (topcover)")
# The approval pick: the build gate's own grammar (scripts/image_rules.py), matched whole
# with fullmatch, so ingest and the gate cannot drift apart. image_rules never imports this.
PICK = image_rules.PICK


class Refused(Exception):
    """The request would break a rule; nothing was written."""


# ── names ────────────────────────────────────────────────────────────────────────────────
def slug_file(slug):
    """`uk-locations/x` -> `uk-locations--x`, the spelling every per-slug file uses."""
    return slug.replace("/", "--")


def default_stem(filename):
    """The stem a folder file lands under when nothing records another name:
    `File name- x .jpg .jpg` -> `x`. It IS image_candidates.asset_stem, so the name ingest
    writes and the name the candidates script and build gate look for cannot drift apart.
    An empty result is refused by stem_problems()."""
    return image_candidates.asset_stem(filename)


def stem_problems(stem):
    out = []
    if not SEO_STEM.match(stem or ""):
        out.append("stem %r is not 3-10 lowercase words joined by hyphens" % stem)
    words = set((stem or "").split("-"))
    if words & GENERIC:
        out.append("stem %r carries a generic word: %s" % (stem, ", ".join(sorted(words & GENERIC))))
    if len(stem or "") > 80:
        out.append("stem %r is longer than 80 characters" % stem)
    return out


def file_sha(path):
    """First 12 hex digits of the sha256 of a file's bytes: what an approval pick names."""
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()[:12]


# ── files ────────────────────────────────────────────────────────────────────────────────
def _read_json(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def _write_json(path, data, sort_keys=True):
    pathlib.Path(path).write_text(
        json.dumps(data, indent=2, sort_keys=sort_keys, ensure_ascii=False) + "\n",
        encoding="utf-8")


def board_path(slug, root=ROOT):
    return pathlib.Path(root) / "data" / "boards" / (slug_file(slug) + ".json")


def draft_path(slug, slot, root=ROOT):
    return pathlib.Path(root) / DRAFTS / slug_file(slug) / (slot + ".webp")


def served(stem, root=ROOT):
    """True when the stem is already on the site (a file or a manifest row)."""
    images = pathlib.Path(root) / IMAGES
    for name in ("%s.webp" % stem, "%s-760.webp" % stem):
        p = images / name
        if p.exists() or p.is_symlink():           # a dangling symlink still takes the name
            return True
    return stem in _read_json(pathlib.Path(root) / MANIFEST, {})


def manifest_row(row):
    """A ledger row's manifest row: {"w", "h", "sib_w"}, plus "phone_w"/"phone_h" once its
    phone layout is published (publish-phone)."""
    out = {"w": row["w"], "h": row["h"], "sib_w": row["sib_w"]}
    if row.get("phone"):
        out.update(phone_w=row["phone"]["w"], phone_h=row["phone"]["h"])
    return out


def ingested_manifest_rows(root=ROOT):
    """{stem: manifest_row()} for every image this script has ingested."""
    ledger = _read_json(pathlib.Path(root) / LEDGER, {})
    return {s: manifest_row(r) for s, r in ledger.items()}


# ── baking ───────────────────────────────────────────────────────────────────────────────
def _style_problems(og_style, infographic, mobcrop=""):
    problem = reframe_og.mobcrop_problem(mobcrop)
    if problem:
        return [problem]
    if bool(og_style) == bool(infographic):
        return ["give exactly one of --og-style or --infographic"]
    if mobcrop and og_style != "B":
        print("warning: --mobcrop only applies to --og-style B; ignored for %s"
              % (og_style or infographic), file=sys.stderr)
    if og_style and og_style not in image_designs.load()["og_styles"]:
        return ["OG style %r is not named in IMAGE-DESIGNS.md §7" % og_style]
    if infographic and infographic not in image_designs.load()["infographic_styles"]:
        return ["infographic style %r is not named in IMAGE-DESIGNS.md §8" % infographic]
    return []


def _retired_problems(og_style, slug):
    """Style B on a new page (or on a page this call cannot name) is refused; the twelve
    pages built before project 5 keep it."""
    if og_style == "B" and (not slug or family_rules.is_new_page(slug)):
        return [RETIRED_B + ("" if slug else " (no --board given, so the page is unknown)")]
    return []


def bake(master, og_style=None, infographic=None, mobcrop=""):
    """The framed full-size image for the requested style."""
    if infographic:
        # A baked infographic master has a transparent background (scripts/ig_shots.mjs
        # crop): it is laid on the frame's own bone through its alpha, so no band forms.
        with Image.open(master) as raw:
            rgba = raw.convert("RGBA")
        return reframe_og.contain_alpha(rgba)
    im = reframe_og.load(master)
    if og_style in BAKED:
        return reframe_og.render(im, BAKED[og_style], mobcrop=mobcrop if og_style == "B" else "")
    scale = min(1.0, reframe_og.W / im.width, NATIVE_MAX_H / im.height)
    if scale < 1.0:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                       Image.LANCZOS)
    return im


def fill_problems(full, infographic):
    """An infographic must fill its box: the content's bounding box covers at least FILL_MIN
    of the box's width or height, whichever binds (the coordinator's review, 2026-10-03: the
    first drafts filled about half the box and left a bone band below)."""
    if not infographic:
        return []
    fw, fh = reframe_og.content_fill(full)
    if max(fw, fh) < FILL_MIN:
        return ["the infographic covers %.0f%% of the box's width and %.0f%% of its height, "
                "under the %.0f%% floor — bake it at a width whose shape fits the box"
                % (fw * 100, fh * 100, FILL_MIN * 100)]
    return []


def load_sibling(path):
    """A supplied -760 sibling (an infographic's reflowed phone bake), flattened onto bone.
    Returns (image, problems)."""
    path = pathlib.Path(path)
    problems = _check_master(path)
    if problems:
        return None, ["sibling: " + p for p in problems]
    with Image.open(path) as raw:
        im = reframe_og.flatten_on_bone(raw.convert("RGBA"))
    if im.width != reframe_og.SIB_W:
        return None, ["sibling %s is %d wide; a -760 sibling is exactly %d wide"
                      % (path.name, im.width, reframe_og.SIB_W)]
    return im, []


def sibling_draft_path(slug, slot, root=ROOT):
    return draft_path(slug, slot, root).with_name(slot + "-760.webp")


def sibling_of(full):
    """The -760 sibling: the box's own 760x415 for a boxed image, proportional otherwise;
    None when the image is already 760 wide or narrower."""
    if full.size == (reframe_og.W, reframe_og.H):
        return reframe_og.sibling(full)
    if full.width <= reframe_og.SIB_W:
        return None
    return full.resize((reframe_og.SIB_W, round(full.height * reframe_og.SIB_W / full.width)),
                       Image.LANCZOS)


def _check_master(master):
    if not master.is_file():
        return ["master %s does not exist" % master]
    if master.suffix.lower() not in MASTER_SUFFIXES:
        return ["master %s is not one of %s" % (master.name, " ".join(MASTER_SUFFIXES))]
    try:
        reframe_og.load(master)
    except ValueError as e:                       # animated
        return [str(e)]
    except (OSError, SyntaxError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as e:
        return ["master %s cannot be read as an image (%s: %s)"
                % (master.name, type(e).__name__, e)]
    return []


def _refuse(problems):
    if problems:
        raise Refused("; ".join(problems))


# ── the board's assets[] row ─────────────────────────────────────────────────────────────
def _asset_row(board, slot):
    return next((a for a in board.get("assets", []) if a.get("slot") == slot), None)


def _slug_problems(slug):
    if not SLUG.match(slug or ""):
        return ["slug %r is not a page slug (lowercase words and hyphens, parts joined by /)"
                % slug]
    return []


def _board_problems(slug, slot, root):
    if _slug_problems(slug):
        return _slug_problems(slug)
    if not (isinstance(slot, str) and SLOT_ID.fullmatch(slot)):
        return ["slot %r is not a slot id" % slot]
    p = board_path(slug, root)
    if not p.exists():
        return ["no board for %s: %s does not exist" % (slug, p)]
    if _asset_row(_read_json(p, {}), slot) is None:
        return ["the board plans no assets[] row for slot %r — plan it at boarding; adding "
                "one now would change the record hash and un-approve the page" % slot]
    return []


def _named_on_board(slug, slot, stem, root):
    """The board with the slot's existing assets[] row `file` and `status` set (both
    outside the hash). Returned, not written: the caller stages it."""
    board = _read_json(board_path(slug, root), {})
    row = _asset_row(board, slot)
    row["file"] = "/images/%s.webp" % stem
    row["status"] = "baked"
    return board


# ── staged writes ────────────────────────────────────────────────────────────────────────
class _Stage:
    """Temp files beside their targets; commit() moves them into place in the order they
    were staged; close() removes whatever was not committed."""

    def __init__(self, label=""):
        self.label = label                         # named in a part-way commit failure
        self.pending = []                          # [(temp, target)]

    def temp_for(self, target):
        target = pathlib.Path(target)
        tmp = target.with_name(".%s.tmp-%d" % (target.name, os.getpid()))
        self.pending.append((tmp, target))
        return tmp

    def json(self, target, data, sort_keys=True):
        _write_json(self.temp_for(target), data, sort_keys)

    def commit(self):
        moved = []
        while self.pending:
            tmp, target = self.pending[0]
            try:
                os.replace(tmp, target)
            except OSError as e:
                raise OSError("%s: commit stopped part-way (%s) — already moved: %s; not moved: %s"
                              % (self.label, e, ", ".join(moved) or "nothing",
                                 ", ".join(str(t) for _, t in self.pending))) from e
            moved.append(str(target))
            self.pending.pop(0)

    def close(self):
        for tmp, _ in self.pending:
            if tmp.exists() or tmp.is_symlink():
                tmp.unlink()
        self.pending = []


def _over(what, kb, maxkb):
    return "%s is %s KB at the q60 floor, over its %s KB budget" % (what, kb, maxkb)


def _encode_staged(stage, img, target, maxkb, what, over):
    kb, _, ok = reframe_og.save_webp(img, stage.temp_for(target), maxkb)
    if not ok:
        over.append(_over(what, kb, maxkb))


def _budget_problems(full, stem):
    """The budget check a real run makes, encoded into a scratch directory that is removed."""
    over = []
    with tempfile.TemporaryDirectory() as d:
        stage = _Stage("dry run %r" % stem)
        try:
            _encode_staged(stage, full, pathlib.Path(d) / ("%s.webp" % stem), reframe_og.MAX_KB,
                           "/images/%s.webp" % stem, over)
            sib = sibling_of(full)
            if sib is not None:
                _encode_staged(stage, sib, pathlib.Path(d) / ("%s-760.webp" % stem),
                               reframe_og.SIB_MAX_KB, "/images/%s-760.webp" % stem, over)
        finally:
            stage.close()
    return over


def _publish_files(full_bytes_from, full_img, stem, row, root, slug=None, slot=None,
                   expect_sha=None, sib_bytes_from=None):
    """Stage the full image (copied byte for byte when a path is given), its sibling, the
    ledger row, the manifest row and the board, then move them all into place. Refused
    (nothing written) when an image misses its budget or the copy is not the approved bytes."""
    root = pathlib.Path(root)
    images = root / IMAGES
    images.mkdir(parents=True, exist_ok=True)
    full_path = images / ("%s.webp" % stem)
    stage, over = _Stage("stem %r" % stem), []
    try:
        if full_bytes_from is not None:
            tmp = stage.temp_for(full_path)
            shutil.copyfile(full_bytes_from, tmp)
            if expect_sha is not None and file_sha(tmp) != expect_sha:
                raise Refused("the staged copy (sha %s) is not byte-identical to the approved "
                              "draft (sha %s)" % (file_sha(tmp), expect_sha))
            kb = round(tmp.stat().st_size / 1024, 1)
            if kb > reframe_og.MAX_KB:
                over.append("the approved draft is %s KB, over the %s KB budget — re-draft it"
                            % (kb, reframe_og.MAX_KB))
        else:
            _encode_staged(stage, full_img, full_path, reframe_og.MAX_KB,
                           "/images/%s.webp" % stem, over)
        if sib_bytes_from is not None:          # the draft's own sibling, copied unchanged
            tmp = stage.temp_for(images / ("%s-760.webp" % stem))
            shutil.copyfile(sib_bytes_from, tmp)
            kb = round(tmp.stat().st_size / 1024, 1)
            if kb > reframe_og.SIB_MAX_KB:
                over.append("the draft's -760 sibling is %s KB, over the %s KB budget — re-draft it"
                            % (kb, reframe_og.SIB_MAX_KB))
            with Image.open(tmp) as s_im:
                sib_w = s_im.width
        else:
            sib = sibling_of(full_img)
            sib_w = sib.width if sib is not None else None
            if sib is not None:
                _encode_staged(stage, sib, images / ("%s-760.webp" % stem),
                               reframe_og.SIB_MAX_KB, "/images/%s-760.webp" % stem, over)
        if over:
            raise Refused("; ".join(over) + " — nothing written")
        row.update({"w": full_img.width, "h": full_img.height, "sib_w": sib_w})
        ledger = _read_json(root / LEDGER, {})
        ledger[stem] = row
        stage.json(root / LEDGER, ledger)
        manifest = _read_json(root / MANIFEST, {})
        manifest[stem] = {"w": row["w"], "h": row["h"], "sib_w": row["sib_w"]}
        stage.json(root / MANIFEST, manifest)
        if slug:
            stage.json(board_path(slug, root), _named_on_board(slug, slot, stem, root),
                       sort_keys=False)
        stage.commit()
    finally:
        stage.close()
    return full_path


def _today(today):
    return (today or datetime.date.today()).isoformat()


# ── the three commands ───────────────────────────────────────────────────────────────────
def folder(master, stem=None, og_style=None, infographic=None, mobcrop="", slug=None,
           slot=None, root=ROOT, dry_run=False, today=None):
    """A breeder's photo into public/images/. Without --stem it lands at the default name
    (`/images/<default stem>.webp`, where the build gate looks); any other name must be
    written into the slot's assets[] row, so --stem needs --board and --slot."""
    master, root = pathlib.Path(master), pathlib.Path(root)
    stem = stem or default_stem(master.name)
    problems = (_check_master(master) + stem_problems(stem)
                + _style_problems(og_style, infographic, mobcrop)
                + _retired_problems(og_style, slug))
    if bool(slug) != bool(slot):
        problems.append("give --board and --slot together (got %s)"
                        % ("--board only" if slug else "--slot only"))
    elif stem != default_stem(master.name) and not slug:
        problems.append("stem %r is not the default %r, so the build gate cannot find it unless "
                        "the slot's assets[] row names it — pass --board and --slot"
                        % (stem, default_stem(master.name)))
    if slug and slot:
        problems += _board_problems(slug, slot, root)
    if not problems and served(stem, root):
        problems.append("stem %r is already served — rule 11: never replace a served image; "
                        "choose a new stem and add it beside the old one" % stem)
    _refuse(problems)
    full = bake(master, og_style, infographic, mobcrop)
    row = {"master": str(master), "source": "assets-folder", "og_style": og_style,
           "infographic_style": infographic, "ingested": _today(today)}
    if dry_run:
        over = _budget_problems(full, stem)
        if over:
            raise Refused("; ".join(over) + " — a real run would write nothing")
        return dict(row, stem=stem, w=full.width, h=full.height)
    _publish_files(None, full, stem, row, root, slug, slot)
    return dict(row, stem=stem)


def draft(master, slug, slot, og_style=None, infographic=None, mobcrop="", root=ROOT,
          sibling=None):
    """A generated master baked into the board's draft folder. Returns the path, the sha12
    of the bytes written, and the pick that approves exactly those bytes.

    `sibling` (an infographic's reflowed 760-wide phone bake) is stored beside the draft as
    `<slot>-760.webp`, held to the sibling budget, and `publish` serves it as the -760 file
    instead of shrinking the whole box. Without it any stored sibling is removed, and publish
    shrinks the box as before."""
    master, root = pathlib.Path(master), pathlib.Path(root)
    problems = (_check_master(master) + _style_problems(og_style, infographic, mobcrop)
                + _slug_problems(slug) + _retired_problems(og_style, slug))
    if not (isinstance(slot, str) and SLOT_ID.fullmatch(slot)):
        problems.append("slot %r is not a slot id" % slot)
    if not _slug_problems(slug) and not board_path(slug, root).exists():
        problems.append("no board for %s" % slug)
    sib_img = None
    if sibling is not None and not problems:
        sib_img, sib_problems = load_sibling(sibling)
        problems += sib_problems
    _refuse(problems)
    full = bake(master, og_style, infographic, mobcrop)
    _refuse(fill_problems(full, infographic))
    out = draft_path(slug, slot, root)
    sib_out = sibling_draft_path(slug, slot, root)
    out.parent.mkdir(parents=True, exist_ok=True)
    stage, over = _Stage("draft %s" % out), []
    try:
        _encode_staged(stage, full, out, reframe_og.MAX_KB, "the draft", over)
        sib = None if sib_img is not None else sibling_of(full)
        if sib_img is not None:
            _encode_staged(stage, sib_img, sib_out, reframe_og.SIB_MAX_KB,
                           "the supplied -760 sibling", over)
        if sib is not None:                    # checked now so publish cannot fail on it later
            probe = _Stage()
            try:
                _encode_staged(probe, sib, out.with_name(out.stem + "-760.webp"),
                               reframe_og.SIB_MAX_KB, "its -760 sibling", over)
            finally:
                probe.close()
        if over:
            raise Refused("; ".join(over) + " — nothing written")
        for ext in DRAFT_EXTS:                 # one draft per slot: the board shows this one
            stale = out.with_suffix(ext)
            if stale.exists() and stale != out:
                stale.unlink()
        if sib_img is None and (sib_out.exists() or sib_out.is_symlink()):
            sib_out.unlink()                   # a stale sibling never outlives its draft
        stage.commit()
    finally:
        stage.close()
    sha = file_sha(out)
    pick = ("og:%s:%s" % (og_style, sha)) if og_style else ("ig:%s:%s" % (infographic, sha))
    r = {"path": out, "sha12": sha, "pick": pick}
    if sib_img is not None:
        r.update(sibling=sib_out, sibling_sha12=file_sha(sib_out))
    return r


#: A phone layout is flat colour and text: quantised to this many colours (most first, no
#: dither) and stored lossless, its text stays crisper than lossy WebP and the file is smaller.
#: The lossy quality walk is the fallback when no palette fits.
PHONE_PALETTES = (64, 48)


def _encode_phone(im, path, maxkb):
    """Lossless on a PHONE_PALETTES palette first, then the lossy quality walk. Writes the
    smallest tried when none fits. Returns (kb, encoding, ok)."""
    import io
    best = None
    for n in PHONE_PALETTES:
        buf = io.BytesIO()
        im.quantize(n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
            buf, "WEBP", lossless=True, quality=100, method=6)
        size = buf.tell() / 1024                  # compared unrounded: 55.03 is over 55
        if best is None or size < best[0]:
            best = (size, "lossless %d colours" % n, buf.getvalue())
        if size <= maxkb:
            pathlib.Path(path).write_bytes(buf.getvalue())
            return round(size, 1), best[1], True
    kb, q, ok = reframe_og.save_webp(im, path, maxkb)
    if ok or kb <= best[0]:
        return kb, "lossy q%d" % q, ok
    pathlib.Path(path).write_bytes(best[2])
    return round(best[0], 1), best[1], False


def phone_draft_path(slug, slot, root=ROOT):
    return draft_path(slug, slot, root).with_name(slot + "-phone.webp")


def phone_draft(master, slug, slot, infographic, root=ROOT):
    """An infographic's phone layout (impeccable London D4, 2026-10-03) as a draft of its own:
    flattened on bone, held to the sibling budget, written to `<slot>-phone.webp` beside the
    slot's box draft, which is never touched (it may already be approved and published).
    Returns the path, the sha12 of the bytes written, the pick key `img:<slot>-phone` and the
    pick `ig:IG-<n>:<sha12>` that approves exactly those bytes."""
    master, root = pathlib.Path(master), pathlib.Path(root)
    problems = (_check_master(master) + _style_problems(None, infographic)
                + _board_problems(slug, slot, root))
    if not problems:
        with Image.open(master) as raw:
            w = raw.width
        if not PHONE_W[0] <= w <= PHONE_W[1]:
            problems.append("phone layout %s is %d wide; one drawn at a phone's width at 1.5-2x is "
                            "%d-%d wide" % (master.name, w, PHONE_W[0], PHONE_W[1]))
    _refuse(problems)
    with Image.open(master) as raw:
        im = reframe_og.flatten_on_bone(raw.convert("RGBA"))
    out = phone_draft_path(slug, slot, root)
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = _Stage("phone draft %s" % out)
    try:
        kb, how, ok = _encode_phone(im, stage.temp_for(out), reframe_og.SIB_MAX_KB)
        if not ok:
            raise Refused("the phone layout is %s KB at its smallest encoding (%s), over its "
                          "%s KB budget — bake it at a lower phone_scale; nothing written"
                          % (kb, how, reframe_og.SIB_MAX_KB))
        stage.commit()
    finally:
        stage.close()
    sha = file_sha(out)
    return {"path": out, "sha12": sha, "w": im.width, "h": im.height, "encoding": how,
            "kb": round(out.stat().st_size / 1024, 1),
            "pick_key": "img:%s-phone" % slot, "pick": "ig:%s:%s" % (infographic, sha)}


def publish(slug, slot, stem, root=ROOT, today=None):
    """Copy an APPROVED draft's bytes unchanged into public/images/ and name it on the board."""
    root = pathlib.Path(root)
    problems = stem_problems(stem) + _board_problems(slug, slot, root)
    _refuse(problems)
    src = draft_path(slug, slot, root)
    if not src.exists():
        _refuse(["no draft for slot %r at %s — run the draft command first" % (slot, src)])
    board = _read_json(board_path(slug, root), {})
    raw = ((board.get("approval") or {}).get("picks") or {}).get("img:" + slot)
    m = PICK.fullmatch(raw) if isinstance(raw, str) else None
    sha = m and (m.group("ogsha") or m.group("igsha"))
    if not sha:
        _refuse(["slot %r is not approved as an image: its pick is %r — re-board and approve "
                 "the draft (IMAGE-DESIGNS.md §9)" % (slot, raw)])
    if sha != file_sha(src):
        _refuse(["slot %r: the draft on disk (sha %s) is not the image the breeder approved "
                 "(sha %s) — re-board and approve it again" % (slot, file_sha(src), sha)])
    if served(stem, root):
        _refuse(["stem %r is already served — rule 11: never replace a served image" % stem])
    with Image.open(src) as im:
        full = im.convert("RGB")
    row = {"master": src.relative_to(root).as_posix(), "source": "generate",
           "og_style": m.group("og"), "infographic_style": m.group("ig"),
           "ingested": _today(today)}
    sib_src = sibling_draft_path(slug, slot, root)
    _publish_files(src, full, stem, row, root, slug, slot, expect_sha=sha,
                   sib_bytes_from=sib_src if sib_src.exists() else None)
    return dict(row, stem=stem, sha12=sha)


def publish_phone(slug, slot, root=ROOT, today=None):
    """Copy an infographic's APPROVED phone layout (`img:<slot>-phone`) unchanged to
    public/images/<box stem>-phone.webp, beside the published box, and record it on the box's
    ledger and manifest rows. Returns {path, sha12, w, h}."""
    root = pathlib.Path(root)
    _refuse(_board_problems(slug, slot, root))
    board = _read_json(board_path(slug, root), {})
    row = _asset_row(board, slot)
    if row.get("kind") != "infographic":
        _refuse(["slot %r is a %s slot; a phone layout belongs to an infographic slot"
                 % (slot, row.get("kind"))])
    key = "img:%s%s" % (slot, image_rules.PHONE_SUFFIX)
    picks = (board.get("approval") or {}).get("picks") or {}
    if key not in picks:
        _refuse(["%s is not approved: the approval names no pick for it — board the phone "
                 "layout and approve its exact bytes" % key])
    _refuse(image_rules.phone_pick_problems(board, {"slot": slot, "kind": "infographic"},
                                            picks[key], picks, root))
    src = phone_draft_path(slug, slot, root)
    if not src.is_file():
        _refuse(["no phone draft for slot %r at %s — run the phone command first" % (slot, src)])
    sha = PICK.fullmatch(picks[key]).group("igsha")
    f = row.get("file") or ""
    m = re.fullmatch(r"/images/(?P<stem>[a-z0-9-]+)\.webp", f)
    stem = m and m.group("stem")
    ledger = _read_json(root / LEDGER, {})
    manifest = _read_json(root / MANIFEST, {})
    if not stem or not (root / IMAGES / ("%s.webp" % stem)).is_file() or stem not in ledger \
            or stem not in manifest:
        _refuse(["slot %r: publish the box image first (its assets[] row names %r, and the phone "
                 "layout is served beside a published, ingested box)" % (slot, f or None)])
    target = root / IMAGES / ("%s%s.webp" % (stem, image_rules.PHONE_SUFFIX))
    if target.exists() or target.is_symlink() or served(target.stem, root) or ledger[stem].get("phone"):
        _refuse(["%s is already served — rule 11: never replace a served image"
                 % target.relative_to(root).as_posix()])
    stage = _Stage("phone %r" % stem)
    try:
        tmp = stage.temp_for(target)
        shutil.copyfile(src, tmp)
        if file_sha(tmp) != sha:
            raise Refused("the staged copy (sha %s) is not byte-identical to the approved phone "
                          "layout (sha %s)" % (file_sha(tmp), sha))
        kb = tmp.stat().st_size / 1024
        if kb > reframe_og.SIB_MAX_KB:
            raise Refused("the approved phone layout is %.1f KB, over its %s KB budget — re-draft "
                          "it; nothing written" % (kb, reframe_og.SIB_MAX_KB))
        with Image.open(tmp) as im:
            w, h = im.size
        ledger[stem]["phone"] = {"file": "/images/%s" % target.name, "w": w, "h": h,
                                 "sha12": sha, "infographic_style": PICK.fullmatch(picks[key]).group("ig"),
                                 "master": src.relative_to(root).as_posix(),
                                 "ingested": _today(today)}
        stage.json(root / LEDGER, ledger)
        manifest[stem] = manifest_row(ledger[stem])
        stage.json(root / MANIFEST, manifest)
        stage.commit()
    finally:
        stage.close()
    return {"path": target, "sha12": sha, "w": w, "h": h}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("folder")
    d = sub.add_parser("draft")
    p = sub.add_parser("publish")
    ph = sub.add_parser("phone")
    pp = sub.add_parser("publish-phone")
    pp.add_argument("--board", required=True)
    pp.add_argument("--slot", required=True, help="the infographic slot (not <slot>-phone)")
    ph.add_argument("master")
    ph.add_argument("--board", required=True)
    ph.add_argument("--slot", required=True)
    ph.add_argument("--infographic", metavar="IG-n", required=True)
    for s in (f, d):
        s.add_argument("master")
        s.add_argument("--og-style", choices=sorted(set(BAKED) | NATIVE))
        s.add_argument("--infographic", metavar="IG-n")
        s.add_argument("--mobcrop", default="")
    f.add_argument("--stem")
    f.add_argument("--board")
    f.add_argument("--slot")
    f.add_argument("--dry-run", action="store_true")
    for s in (d, p):
        s.add_argument("--board", required=True)
        s.add_argument("--slot", required=True)
    d.add_argument("--sibling", metavar="PATH",
                   help="a 760-wide phone sibling, stored with the draft and served as -760")
    p.add_argument("--stem", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "folder":
            r = folder(a.master, a.stem, a.og_style, a.infographic, a.mobcrop, a.board, a.slot,
                       dry_run=a.dry_run)
            print("%s /images/%s.webp  [%s]" % ("would ingest" if a.dry_run else "ingested",
                                                r["stem"], a.og_style or a.infographic))
        elif a.cmd == "phone":
            r = phone_draft(a.master, a.board, a.slot, a.infographic)
            print("phone draft %s  %dx%d  %s KB (%s)  sha12 %s\napprove on the board with "
                  "pick: %s = %s" % (r["path"].relative_to(ROOT), r["w"], r["h"], r["kb"],
                                     r["encoding"], r["sha12"], r["pick_key"], r["pick"]))
        elif a.cmd == "publish-phone":
            r = publish_phone(a.board, a.slot)
            print("published %s  %dx%d  (sha12 %s, byte-identical to the approved phone layout)"
                  % (r["path"].relative_to(ROOT), r["w"], r["h"], r["sha12"]))
        elif a.cmd == "draft":
            r = draft(a.master, a.board, a.slot, a.og_style, a.infographic, a.mobcrop,
                      sibling=a.sibling)
            print("draft %s  sha12 %s\napprove on the board with pick: %s"
                  % (r["path"].relative_to(ROOT), r["sha12"], r["pick"]))
            if "sibling" in r:
                print("sibling %s  sha12 %s" % (r["sibling"].relative_to(ROOT),
                                                r["sibling_sha12"]))
        else:
            r = publish(a.board, a.slot, a.stem)
            print("published /images/%s.webp (sha12 %s, byte-identical to the approved draft)"
                  % (r["stem"], r["sha12"]))
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
