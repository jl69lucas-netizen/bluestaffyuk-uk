#!/usr/bin/env python3
"""Bring a new image onto BlueStaffyUK: IMAGE-DESIGNS.md §6 and §9, as three commands.

  folder   a photo from the breeder's folder -> public/images/<stem>.webp (+ -760 sibling)
  draft    a generated master -> data/boards/generated/<slug file>/<slot>.webp, the exact
           bytes the board shows for approval; prints their sha12 and the pick that approves
  publish  after the board approved THOSE bytes (pick `og:<style>:<sha12>` or
           `ig:IG-<n>:<sha12>`), copies them UNCHANGED into public/images/<stem>.webp

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

Usage:
  python3 scripts/ingest_image.py folder <master> [--stem <seo-stem>] --og-style B [--mobcrop 4:5]
        [--board <slug> --slot <slot>] [--dry-run]
  python3 scripts/ingest_image.py draft <master> --board <slug> --slot <slot> --og-style B [--mobcrop 4:5]
  python3 scripts/ingest_image.py draft <master> --board <slug> --slot <slot> --infographic IG-2
  python3 scripts/ingest_image.py publish --board <slug> --slot <slot> --stem <seo-stem>
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

# 3 to 10 lowercase words joined by single hyphens: what the pipeline's SEO filename
# convention produces, and nothing a camera or a download names a file by default.
SEO_STEM = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){2,9}$")
GENERIC = {"img", "image", "photo", "pic", "dsc", "screenshot", "untitled", "copy",
           "final", "file", "name", "new", "edit"}
SLOT_ID = re.compile(r"^[a-z][a-z0-9-]*$")
SLUG = re.compile(r"^[a-z0-9-]+(/[a-z0-9-]+)*$")
BAKED = {"A": "contain", "B": "blurfill", "E": "topcover"}
NATIVE = {"C", "D", "H"}
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


def ingested_manifest_rows(root=ROOT):
    """{stem: {"w", "h", "sib_w"}} for every image this script has ingested."""
    ledger = _read_json(pathlib.Path(root) / LEDGER, {})
    return {s: {"w": r["w"], "h": r["h"], "sib_w": r["sib_w"]} for s, r in ledger.items()}


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


def bake(master, og_style=None, infographic=None, mobcrop=""):
    """The framed full-size image for the requested style."""
    im = reframe_og.load(master)
    if infographic:
        return reframe_og.render(im, "contain")
    if og_style in BAKED:
        return reframe_og.render(im, BAKED[og_style], mobcrop=mobcrop if og_style == "B" else "")
    scale = min(1.0, reframe_og.W / im.width, NATIVE_MAX_H / im.height)
    if scale < 1.0:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                       Image.LANCZOS)
    return im


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
    if not SLOT_ID.match(slot or ""):
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
                   expect_sha=None):
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
        sib = sibling_of(full_img)
        if sib is not None:
            _encode_staged(stage, sib, images / ("%s-760.webp" % stem), reframe_og.SIB_MAX_KB,
                           "/images/%s-760.webp" % stem, over)
        if over:
            raise Refused("; ".join(over) + " — nothing written")
        row.update({"w": full_img.width, "h": full_img.height,
                    "sib_w": sib.width if sib is not None else None})
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
                + _style_problems(og_style, infographic, mobcrop))
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


def draft(master, slug, slot, og_style=None, infographic=None, mobcrop="", root=ROOT):
    """A generated master baked into the board's draft folder. Returns the path, the sha12
    of the bytes written, and the pick that approves exactly those bytes."""
    master, root = pathlib.Path(master), pathlib.Path(root)
    problems = (_check_master(master) + _style_problems(og_style, infographic, mobcrop)
                + _slug_problems(slug))
    if not SLOT_ID.match(slot or ""):
        problems.append("slot %r is not a slot id" % slot)
    if not _slug_problems(slug) and not board_path(slug, root).exists():
        problems.append("no board for %s" % slug)
    _refuse(problems)
    full = bake(master, og_style, infographic, mobcrop)
    out = draft_path(slug, slot, root)
    out.parent.mkdir(parents=True, exist_ok=True)
    stage, over = _Stage("draft %s" % out), []
    try:
        _encode_staged(stage, full, out, reframe_og.MAX_KB, "the draft", over)
        sib = sibling_of(full)
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
        stage.commit()
    finally:
        stage.close()
    sha = file_sha(out)
    pick = ("og:%s:%s" % (og_style, sha)) if og_style else ("ig:%s:%s" % (infographic, sha))
    return {"path": out, "sha12": sha, "pick": pick}


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
    _publish_files(src, full, stem, row, root, slug, slot, expect_sha=sha)
    return dict(row, stem=stem, sha12=sha)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("folder")
    d = sub.add_parser("draft")
    p = sub.add_parser("publish")
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
    p.add_argument("--stem", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "folder":
            r = folder(a.master, a.stem, a.og_style, a.infographic, a.mobcrop, a.board, a.slot,
                       dry_run=a.dry_run)
            print("%s /images/%s.webp  [%s]" % ("would ingest" if a.dry_run else "ingested",
                                                r["stem"], a.og_style or a.infographic))
        elif a.cmd == "draft":
            r = draft(a.master, a.board, a.slot, a.og_style, a.infographic, a.mobcrop)
            print("draft %s  sha12 %s\napprove on the board with pick: %s"
                  % (r["path"].relative_to(ROOT), r["sha12"], r["pick"]))
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
