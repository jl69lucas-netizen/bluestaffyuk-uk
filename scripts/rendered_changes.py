#!/usr/bin/env python3
"""rendered_changes.py — which built pages' RENDERED output changed (a dist-hash diff).

  python3 scripts/rendered_changes.py --base <dir-or-ref> [--json] [--record-manifest]

IndexNow must be told about every page whose rendered HTML changed, and a source diff cannot
say which those are: a city page renders from `src/pages/uk-locations/[slug].astro` plus a row
of data/locations.json, and a shared component edit changes every page that mounts it (audit
D6 / M13). So this hashes every dist/**/index.html (the specimen routes excepted) and compares
the hashes with an earlier build:

  <dir>  a directory holding the earlier build — a copy of dist/ taken before the work
  <ref>  a git ref; the earlier build is the data/quality/dist-hashes.json that ref committed

Prints the changed slugs (modified or added) and the removed ones. A slug is the page's dist
route (`uk-locations/<city>`), `index` for the root.

  --json             writes docs/reports/rendered-changes.json =
                     {"base": <dir-or-ref>, "head": <sha>, "changed": [slugs]} (git-ignored;
                     read by `indexnow_submit.py --changed` and scripts/measurement_ledger.py).
                     It never touches the manifest.
  --record-manifest  refreshes data/quality/dist-hashes.json = {"head": <sha>, "pages": {...}},
                     the manifest the NEXT diff uses as its base. Record it only after a
                     successful IndexNow submit of the changed list (or at a project close that
                     deliberately rebases), never after a skipped or failed submit: the
                     unsubmitted pages would drop out of the next diff. Commit it.

`head` is the commit the build was made on top of (HEAD when this runs), with `-dirty`
appended when a tracked file has uncommitted changes (scripts/page_run_record.py dirty_tracked,
the manifest aside; the report is under docs/reports/, which that test already sets aside). The manifest belongs to the commit that adds it, one after its `head`.

What the hash counts. Inline <style>, non-JSON-LD <script> and /_astro/ asset links are
stripped, so a shared CSS or bundle edit alone is not a change. Still counted as a change
although no search engine indexes it: inline style="" attributes, class names, a component
rename (it rewrites every data-astro-cid-* attribute the component emits) and an image-transform
change (new hashed /_astro/ image URLs in <img>/srcset). Missed: text a script inserts at
runtime, built files that are not an index.html (404.html) and the sitemaps. Removed pages are
printed, never written to the report, so they are never submitted.

Exit 0 on a completed diff, 2 when it cannot run (no dist/, an unreadable or empty base, a
malformed manifest, no readable git HEAD).
RENDERED_CHANGES_ROOT points it at another tree (tests only).
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import page_run_record as PRR  # noqa: E402

ROOT = pathlib.Path(os.environ.get("RENDERED_CHANGES_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
MANIFEST = pathlib.Path("data") / "quality" / "dist-hashes.json"
REPORT = pathlib.Path("docs") / "reports" / "rendered-changes.json"
SPECIMEN_PREFIXES = tuple(json.loads((pathlib.Path(__file__).resolve().parent.parent / "data" / "specimen-routes.json").read_text(encoding="utf-8"))["prefixes"])


class BaseError(Exception):
    pass


class HeadError(Exception):
    pass


def page_hashes(dist):
    """{slug: content_hash of the built index.html} for every page but the specimen routes."""
    dist = pathlib.Path(dist)
    out = {}
    for page in sorted(dist.glob("**/index.html")):
        rel = page.parent.relative_to(dist).as_posix()
        slug = "index" if rel == "." else rel
        if (slug + "/").startswith(SPECIMEN_PREFIXES):
            continue
        out[slug] = content_hash(page.read_text(encoding="utf-8", errors="replace"))
    return out


# What a search engine indexes is the text, the links and the JSON-LD — not the inline CSS,
# the script bundles or the content-hashed asset names. A shared CSS edit rewrites every
# page's <style> and /_astro/ links; hashing raw bytes would report all 51 pages "changed"
# and send the whole site to IndexNow. JSON-LD scripts are kept: a schema change is indexed.
#
# Assumptions the regexes rely on (true of Astro's output; revisit if a page breaks them):
#   - JSON-LD text never contains a literal `<script` or `<style` (it is JSON.stringify output;
#     a `</script>` inside a string would end the element early in a browser too);
#   - the ld+json `type` attribute comes before any attribute whose value contains `>`,
#     because the lookahead scans the open tag only up to its first `>`.
# Matching is case-insensitive and ignores attribute spacing and quote style.
_STYLE = re.compile(r"<style\b[^>]*>.*?</style>", re.S | re.I)
_SCRIPT = re.compile(r"<script\b(?![^>]*application/ld\+json)[^>]*>.*?</script>", re.S | re.I)
_ASSET_LINK = re.compile(r"<link\b[^>]*\bhref=\"/_astro/[^\"]*\"[^>]*>", re.I)


def content_hash(html):
    """sha256 of the page with inline styles, non-JSON-LD scripts and /_astro/ asset links removed."""
    for rx in (_STYLE, _SCRIPT, _ASSET_LINK):
        html = rx.sub("", html)
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


def diff(base, head):
    """{'changed': modified or added slugs, 'removed': slugs the head no longer builds}."""
    return {"changed": sorted(s for s, h in head.items() if base.get(s) != h),
            "removed": sorted(s for s in base if s not in head)}


def base_hashes(base):
    """The earlier build's hashes: a directory is hashed; anything else is a git ref."""
    path = pathlib.Path(base)
    if not path.is_absolute():
        path = ROOT / path
    if path.is_dir():
        return page_hashes(path)
    r = subprocess.run(["git", "show", f"{base}:{MANIFEST.as_posix()}"], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise BaseError(f"no {MANIFEST.as_posix()} at {base!r} — pass a directory holding the "
                        "earlier build, or a ref whose close committed the manifest")
    try:
        pages = json.loads(r.stdout)["pages"]
    except (ValueError, KeyError, TypeError) as e:
        raise BaseError(f"{MANIFEST.as_posix()} at {base!r} is malformed: {e!r}")
    if not isinstance(pages, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in pages.items()):
        raise BaseError(f"{MANIFEST.as_posix()} at {base!r} is malformed: \"pages\" must map "
                        "slug strings to hash strings")
    return pages


def head_sha():
    """HEAD's sha, plus `-dirty` when a tracked file has uncommitted changes.

    Dirty is scripts/page_run_record.py dirty_tracked, the definition the gate report's `head`
    uses: untracked files, records, reports (this one included), rewritten scorecards and the
    build's own tracked outputs are not uncommitted work. The manifest this script records is
    its own output too, so it is set aside here."""
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    sha = r.stdout.strip()
    if r.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", sha):
        why = (r.stderr or r.stdout).strip() or "no output"
        raise HeadError(f"cannot read git HEAD in {ROOT}: {why}")
    # rev-parse above proved ROOT is a git work tree, so dirty_tracked's own status call runs.
    dirty = [f for f in PRR.dirty_tracked(ROOT) if f != MANIFEST.as_posix()]
    return sha + "-dirty" if dirty else sha


def main(argv=None):
    ap = argparse.ArgumentParser(description="slugs whose rendered dist/ output changed")
    ap.add_argument("--base", required=True, help="a directory holding the earlier build, or a git ref")
    ap.add_argument("--json", action="store_true", help=f"write {REPORT.as_posix()}")
    ap.add_argument("--record-manifest", action="store_true",
                    help=f"refresh {MANIFEST.as_posix()} (only after a successful IndexNow submit)")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    dist = ROOT / "dist"
    if not dist.is_dir():
        print("rendered-changes ERROR dist/ does not exist — run npm run build first")
        return 2
    try:
        base = base_hashes(a.base)
    except (BaseError, OSError) as e:
        print(f"rendered-changes ERROR {e}")
        return 2
    if not base:
        print(f"rendered-changes ERROR base {a.base!r} has no pages — not a build directory or "
              "ref without a manifest")
        return 2
    try:
        sha = head_sha()
    except HeadError as e:
        print(f"rendered-changes ERROR {e}")
        return 2
    head = page_hashes(dist)
    d = diff(base, head)
    short = sha[:12] + ("-dirty" if sha.endswith("-dirty") else "")
    print(f"rendered-changes: base {a.base}, head {short} — {len(d['changed'])} changed, "
          f"{len(d['removed'])} removed, of {len(head)} built pages ({len(base)} in the base)")
    for s in d["changed"]:
        print(f"  changed {s}")
    for s in d["removed"]:
        print(f"  removed {s}")
    if a.json:
        rep = ROOT / REPORT
        rep.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text(json.dumps({"base": a.base, "head": sha, "changed": d["changed"]}, indent=2) + "\n",
                       encoding="utf-8")
        print(f"wrote {REPORT.as_posix()}")
    if a.record_manifest:
        man = ROOT / MANIFEST
        man.parent.mkdir(parents=True, exist_ok=True)
        man.write_text(json.dumps({"head": sha, "pages": head}, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
        print(f"wrote {MANIFEST.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
