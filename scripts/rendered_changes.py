#!/usr/bin/env python3
"""rendered_changes.py — which built pages' RENDERED output changed (a dist-hash diff).

  python3 scripts/rendered_changes.py --base <dir-or-ref> [--json]

IndexNow must be told about every page whose rendered HTML changed, and a source diff cannot
say which those are: a city page renders from `src/pages/uk-locations/[slug].astro` plus a row
of data/locations.json, and a shared component edit changes every page that mounts it (audit
D6 / M13). So this hashes every dist/**/index.html (the specimen routes excepted) and compares
the hashes with an earlier build:

  <dir>  a directory holding the earlier build — a copy of dist/ taken before the work
  <ref>  a git ref; the earlier build is the data/quality/dist-hashes.json that ref committed

Prints the changed slugs (modified or added) and the removed ones. `--json` writes
docs/reports/rendered-changes.json = {"base": <dir-or-ref>, "head": <sha>, "changed": [slugs]}
(read by `indexnow_submit.py --changed` and scripts/measurement_ledger.py) and refreshes
data/quality/dist-hashes.json, the manifest the NEXT close diffs against — commit it with the
close. A slug is the page's dist route (`uk-locations/<city>`), `index` for the root.

Exit 0 on a completed diff, 2 when it cannot run (no dist/, an unreadable base).
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

ROOT = pathlib.Path(os.environ.get("RENDERED_CHANGES_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
MANIFEST = pathlib.Path("data") / "quality" / "dist-hashes.json"
REPORT = pathlib.Path("docs") / "reports" / "rendered-changes.json"
SPECIMEN_PREFIXES = ("board-preview/", "kit-preview/")


class BaseError(Exception):
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
    return json.loads(r.stdout)["pages"]


def head_sha():
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "unknown"


def main(argv=None):
    ap = argparse.ArgumentParser(description="slugs whose rendered dist/ output changed")
    ap.add_argument("--base", required=True, help="a directory holding the earlier build, or a git ref")
    ap.add_argument("--json", action="store_true",
                    help=f"write {REPORT.as_posix()} and refresh {MANIFEST.as_posix()}")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    dist = ROOT / "dist"
    if not dist.is_dir():
        print("rendered-changes ERROR dist/ does not exist — run npm run build first")
        return 2
    try:
        base = base_hashes(a.base)
    except (BaseError, OSError, ValueError, KeyError) as e:
        print(f"rendered-changes ERROR {e}")
        return 2
    head = page_hashes(dist)
    d = diff(base, head)
    sha = head_sha()
    print(f"rendered-changes: base {a.base}, head {sha[:12]} — {len(d['changed'])} changed, "
          f"{len(d['removed'])} removed, of {len(head)} built pages ({len(base)} in the base)")
    for s in d["changed"]:
        print(f"  changed {s}")
    for s in d["removed"]:
        print(f"  removed {s}")
    if a.json:
        rep, man = ROOT / REPORT, ROOT / MANIFEST
        rep.parent.mkdir(parents=True, exist_ok=True)
        man.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text(json.dumps({"base": a.base, "head": sha, "changed": d["changed"]}, indent=2) + "\n",
                       encoding="utf-8")
        man.write_text(json.dumps({"head": sha, "pages": head}, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
        print(f"wrote {REPORT.as_posix()} and {MANIFEST.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
