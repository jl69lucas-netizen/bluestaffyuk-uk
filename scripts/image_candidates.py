#!/usr/bin/env python3
"""image_candidates.py <slug> [--assets-dir DIR] [--per-pool N] [--write]

Ranks candidate images for every image slot a board record plans, so a slot is filled from
images the site already has before anything is generated (system-gaps build, 2026-09-24;
working rule 11: reuse every existing image first).

THREE POOLS, in this order of preference:

  own     the images the migrated page itself served: its `data/verbatim/<slug>.json` alts,
          the <img> tags inside <main> of its page in dist/ (the migrated page until it is
          rebuilt), and any file its own record's `assets[]` already names
  served  every other image the site serves, one per stem of `data/image-manifest.json`
          (the manifest carries only measured sizes, no description, so an image's words are
          its filename plus every alt it is shown with anywhere in dist/ or data/verbatim/)
  assets  files in the breeder's folder (`ASSETS_DIR`, the Assets/Images folder of the
          bluestaffyuk-cms directory, or `--assets-dir`). These
          are NOT in the repo: picking one means ingesting it into public/images first. A
          folder file whose stem is already served (the same stem, or a served stem ending
          in `-<stem>`) is left out and counted as already served.

SCORING is plain token overlap, deliberately: the slot's words (its section heading, the
section's keyword lists, the H3's heading for an H3 slot, and the slot's prompt) against
the image's words (filename stem and alts), lowercased, split on non-alphanumerics, a
trailing plural folded, and the words every image on this site shares (blue, staffy, uk,
puppy …) dropped, since they would match everything and rank nothing. The score is the
number of distinct shared words. Each pool keeps its best `--per-pool` (score >= 1), and
the pools are listed own → served → assets, so a weaker match from the page's own images
is still offered ahead of a stronger one from elsewhere — reuse is the preference, and the
score orders within a pool. `suggested` is the first candidate not already suggested for
an earlier slot, so one photo is not proposed twice on one page (Rule 50b: no shared alt).

Every served candidate carries `used_on`: the other built pages that already show it, so
reuse across pages is visible on the board rather than discovered after the build.

Pure functions take `root` (the repo) and `assets_dir`, so the tests run on a tmp tree.
Prints the JSON; `--write` also writes data/boards/candidates/<slug file>.json.
"""
import argparse
import json
import os
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
#: The breeder's image folder. It sits outside the repo, so it is named absolutely, the way
#: scripts/bake_images.py names its source tree; BSUK_ASSETS_DIR overrides it.
ASSETS_DIR = pathlib.Path(os.environ.get("BSUK_ASSETS_DIR",
                                         "/Users/apple/Downloads/bluestaffyuk-cms/Assets/Images"))
POOLS = ("own", "served", "assets")
IMAGE_EXTS = (".webp", ".png", ".jpg", ".jpeg")
SIZE_SUFFIX = re.compile(r"-(\d{2,4})$")
#: Routes that are not pages: the board previews, the kit specimen, the 404 and search.
NOT_PAGES = ("board-preview", "kit-preview", "search")
#: Words every image on this site shares. They match everything, so they rank nothing.
GENERIC = frozenset("""
blue staffy staffie staffordshire bull terrier sbt uk bluestaffyuk puppy pup dog webp png
jpg jpeg image photo picture file name our we us the a an and or of to in for on with at by
is are be your you from it this that as how what why when do doe its their them into
alt text migrated reused original path working rule page
""".split())
METHOD = ("token overlap: slot words (section heading, section keywords, H3 heading, prompt) "
          "against image words (filename stem, alts); shared site-wide words dropped; score = "
          "distinct shared words; pools own > served > assets, score orders within a pool")


def slug_file(slug):
    """`uk-locations/x` -> `uk-locations--x`, the spelling every per-slug file uses."""
    return slug.replace("/", "--")


def route_of(slug):
    return "/" if slug == "index" else "/" + slug.strip("/") + "/"


def _fold(tok):
    if len(tok) > 4 and tok.endswith("ies"):
        return tok[:-3] + "y"
    if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss"):
        return tok[:-1]
    return tok


def tokens(text):
    """The scoring words of a string: lowercased, folded, generic and numeric words dropped."""
    out = set()
    for raw in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if raw.isdigit():
            continue
        t = _fold(raw)
        if t not in GENERIC and len(t) > 1:
            out.add(t)
    return out


def canonical(src):
    """An /images/ URL with its size sibling suffix dropped: `/images/x-760.webp` -> `/images/x.webp`."""
    src = (src or "").split("?")[0].split("#")[0]
    if not src.startswith("/images/"):
        return None
    p = pathlib.PurePosixPath(src)
    stem = SIZE_SUFFIX.sub("", p.stem)
    return str(p.with_name(stem + p.suffix))


# ── the record's slots ──────────────────────────────────────────────────────────────────
def iter_slots(board):
    """(section, node or None, image) for every image slot the record plans: a section's
    `images[]`, then every node's `images[]` (H3–H6), in outline order."""
    def walk(section, nodes):
        for n in nodes:
            for img in n.get("images") or []:
                yield section, n, img
            yield from walk(section, n.get("children") or [])
    for s in board.get("sections", []):
        for img in s.get("images") or []:
            yield s, None, img
        yield from walk(s, s.get("tree") or [])


def slot_words(section, node, image):
    """The words a slot is scored on."""
    parts = [section.get("heading", ""), image.get("prompt", "")]
    if node is not None:
        parts.append(node.get("heading", ""))
    else:
        for words in (section.get("keywords") or {}).values():
            parts.extend(words)
    out = set()
    for p in parts:
        out |= tokens(p)
    return out


# ── the pools ───────────────────────────────────────────────────────────────────────────
class _Imgs(HTMLParser):
    """Every <img src alt> on a page, and which of them sit inside <main>."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.all, self.main = [], []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.depth += 1
        elif tag == "img":
            a = dict(attrs)
            row = (a.get("src") or "", a.get("alt") or "")
            self.all.append(row)
            if self.depth:
                self.main.append(row)

    def handle_endtag(self, tag):
        if tag == "main" and self.depth:
            self.depth -= 1


def _page_imgs(path):
    p = _Imgs()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    return p


def dist_pages(root):
    """{route: dist file} for every built page, previews and specimens left out."""
    dist = root / "dist"
    out = {}
    if not dist.is_dir():
        return out
    for f in sorted(dist.rglob("index.html")):
        rel = f.relative_to(dist).as_posix()
        if rel.split("/")[0] in NOT_PAGES:
            continue
        out["/" if rel == "index.html" else "/" + rel[: -len("index.html")]] = f
    return out


def _verbatim_files(root):
    d = root / "data" / "verbatim"
    return sorted(p for p in d.glob("*.json") if p.name != "applies.json") if d.is_dir() else []


def usage_and_alts(root):
    """({canonical file: sorted routes that show it}, {canonical file: [alts]}) from dist/
    and data/verbatim/."""
    used, alts = {}, {}

    def note_alt(src, alt):
        if alt and alt not in alts.setdefault(src, []):
            alts[src].append(alt)

    for route, f in dist_pages(root).items():
        for src, alt in _page_imgs(f).all:
            c = canonical(src)
            if c:
                used.setdefault(c, set()).add(route)
                note_alt(c, alt)
    for vf in _verbatim_files(root):
        for row in json.loads(vf.read_text(encoding="utf-8")).get("alts", []):
            c = canonical(row.get("src"))
            if c:
                note_alt(c, row.get("alt", ""))
    return {k: sorted(v) for k, v in used.items()}, alts


def own_images(board, root):
    """[{file, alt}] the migrated page itself served, plus the files its record names."""
    slug = board["meta"]["slug"]
    seen, out = set(), []

    def add(src, alt):
        c = canonical(src)
        if c and c not in seen and (root / "public" / c.lstrip("/")).exists():
            seen.add(c)
            out.append({"file": c, "alt": alt or ""})

    for name in (slug, slug_file(slug)):
        vf = root / "data" / "verbatim" / f"{name}.json"
        if vf.exists():
            for row in json.loads(vf.read_text(encoding="utf-8")).get("alts", []):
                add(row.get("src"), row.get("alt"))
            break
    page = dist_pages(root).get(route_of(slug))
    if page is not None:
        for src, alt in _page_imgs(page).main:
            add(src, alt)
    for a in board.get("assets", []):
        if a.get("file"):
            add(a["file"], a.get("alt"))
    return out


def served_images(root):
    """[{file}] one per stem of data/image-manifest.json that exists under public/images."""
    mf = root / "data" / "image-manifest.json"
    manifest = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    out = []
    for stem in sorted(manifest):
        if "logo" in stem:
            continue
        for ext in (".webp", ".png"):
            if (root / "public" / "images" / (stem + ext)).exists():
                out.append({"file": f"/images/{stem}{ext}"})
                break
    return out


def asset_stem(filename):
    """A folder filename -> the stem it would be ingested under: `File name- x .jpg` -> `x`."""
    stem = pathlib.Path(filename.strip()).stem.strip()
    stem = re.sub(r"^file name-\s*", "", stem, flags=re.I)
    stem = pathlib.Path(stem.strip()).stem          # `x .jpg .jpg` carries a second extension
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")


def ingest_target(filename):
    """Where the ingest step puts a folder file unless it records another path."""
    return f"/images/{asset_stem(filename)}.webp"


def served_stems(root):
    d = root / "public" / "images"
    if not d.is_dir():
        return set()
    return {SIZE_SUFFIX.sub("", p.stem) for p in d.rglob("*") if p.suffix.lower() in IMAGE_EXTS}


def already_served(filename, stems):
    s = asset_stem(filename)
    return s in stems or any(x.endswith("-" + s) for x in stems)


def asset_images(assets_dir, root):
    """([{asset, ingest_as}], [already-served filenames]) from the breeder's folder."""
    d = pathlib.Path(assets_dir) if assets_dir else None
    if d is None or not d.is_dir():
        return [], []
    stems = served_stems(root)
    fresh, served = [], []
    for p in sorted(d.iterdir()):
        if p.name.startswith(".") or not p.is_file():
            continue
        if not p.name.strip().lower().endswith(IMAGE_EXTS):
            continue
        if already_served(p.name, stems):
            served.append(p.name)
        else:
            fresh.append({"asset": p.name, "ingest_as": ingest_target(p.name)})
    return fresh, served


# ── ranking ─────────────────────────────────────────────────────────────────────────────
def _candidate(pool, item, words, alts, used, own_route):
    if pool == "assets":
        img_words = tokens(item["asset"].replace("File name-", ""))
        cand = {"pool": pool, "file": None, "asset": item["asset"], "ingest_as": item["ingest_as"],
                "alt": "", "used_on": [], "pick": "assets:" + item["asset"]}
    else:
        f = item["file"]
        known = alts.get(f, [])
        alt = item.get("alt") or (known[0] if known else "")
        img_words = tokens(pathlib.PurePosixPath(f).stem)
        for a in [alt] + known:
            img_words |= tokens(a)
        cand = {"pool": pool, "file": f, "asset": None, "ingest_as": None, "alt": alt,
                "used_on": [r for r in used.get(f, []) if r != own_route], "pick": "file:" + f}
    matched = sorted(words & img_words)
    cand["score"] = len(matched)
    cand["matched"] = matched
    return cand


def rank(words, pools, alts, used, own_route, per_pool=3):
    """The candidates for one slot: each pool's best `per_pool` with score >= 1, pools in
    preference order, score descending then filename within a pool."""
    out, seen = [], set()
    for pool in POOLS:
        scored = [_candidate(pool, it, words, alts, used, own_route) for it in pools[pool]]
        scored = [c for c in scored if c["score"] >= 1 and c["pick"] not in seen]
        scored.sort(key=lambda c: (-c["score"], c["pick"]))
        for c in scored[:per_pool]:
            seen.add(c["pick"])
            out.append(c)
    return out


def candidates(board, root=None, assets_dir=None, per_pool=3):
    """The whole candidate report for one record. Pure: reads files, writes nothing."""
    root = pathlib.Path(root) if root is not None else ROOT
    slug = board["meta"]["slug"]
    own = own_images(board, root)
    own_files = {o["file"] for o in own}
    served = [s for s in served_images(root) if s["file"] not in own_files]
    fresh, already = asset_images(assets_dir, root)
    pools = {"own": own, "served": served, "assets": fresh}
    used, alts = usage_and_alts(root)
    route = route_of(slug)
    slots, taken = [], set()
    for section, node, img in iter_slots(board):
        words = slot_words(section, node, img)
        cands = rank(words, pools, alts, used, route, per_pool)
        suggested = next((c for c in cands if c["pick"] not in taken), None)
        if suggested:
            taken.add(suggested["pick"])
        slots.append({"slot": img["slot"], "section": section["id"],
                      "node": node["heading"] if node else None, "kind": img["kind"],
                      "source": img.get("source"), "context": sorted(words),
                      "candidates": cands, "suggested": suggested})
    return {"slug": slug, "method": METHOD, "assets_dir": str(assets_dir) if assets_dir else None,
            "pools": {"own": len(own), "served": len(served), "assets": len(fresh),
                      "assets_already_served": len(already)},
            "slots": slots}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--assets-dir", default=str(ASSETS_DIR))
    ap.add_argument("--per-pool", type=int, default=3)
    ap.add_argument("--write", action="store_true",
                    help="also write data/boards/candidates/<slug file>.json")
    a = ap.parse_args(argv)
    rec = ROOT / "data" / "boards" / (slug_file(a.slug) + ".json")
    if not rec.exists():
        print(f"image-candidates: no board record at {rec.relative_to(ROOT)}", file=sys.stderr)
        return 2
    board = json.loads(rec.read_text(encoding="utf-8"))
    report = candidates(board, ROOT, pathlib.Path(a.assets_dir), a.per_pool)
    text = json.dumps(report, indent=1, ensure_ascii=False) + "\n"
    print(text, end="")
    if a.write:
        out = ROOT / "data" / "boards" / "candidates" / (slug_file(a.slug) + ".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"image-candidates: wrote {out.relative_to(ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
