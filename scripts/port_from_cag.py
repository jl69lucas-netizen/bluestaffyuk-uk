#!/usr/bin/env python3
"""Apply data/port-manifest.json: copy files from ~/Downloads/CAG into this repo.

The manifest is the record of the port, not a convenience. Four modes:

  copy      byte-identical, same relative path. Rewritten on every run.
  rename    byte-identical, new path (cag-x.md -> bsuk-x.md). Rewritten on every run.
  rebase    copied ONCE, then hand-edited. NEVER overwritten. The hand edits are the
            deliverable; a second run that re-copied the parrot source would undo the
            entire re-base silently, and scripts/parrot_marker_check.py would only find
            out afterwards. `skipped-existing` on a second run is the expected result.
  deferred  recorded, not written. The file exists in CAG and belongs to a later project;
            listing it keeps the manifest a complete account of the source tree. Its src
            is not required to exist, because the manifest must be able to record a
            decision about a file CAG later deletes.

Usage:
  python3 scripts/port_from_cag.py                 # apply every row
  python3 scripts/port_from_cag.py --dry-run       # report, write nothing
  python3 scripts/port_from_cag.py --only rules/   # rows whose dst starts with this prefix
  python3 scripts/port_from_cag.py --cag /path     # override the source root
  python3 scripts/port_from_cag.py --manifest P --dest D   # override manifest / destination

Exits non-zero when any non-deferred row's src is missing, so a manifest that drifts
from CAG fails loudly instead of half-applying.
"""
import argparse
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAG = pathlib.Path("/Users/apple/Downloads/CAG")
MANIFEST = ROOT / "data/port-manifest.json"
SCHEMA = ROOT / "schemas/port-manifest.schema.json"
MODES = ("copy", "rename", "rebase", "deferred")


def load_manifest(path=MANIFEST):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def validate(rows, schema_path=SCHEMA):
    """The two rules a JSON Schema cannot express on its own, then the schema itself.

    The row-level checks run first so their messages ("relative", "duplicate dst",
    "unknown mode") name the actual defect rather than a regex the reader has to decode.
    """
    import jsonschema

    if not isinstance(rows, list):
        raise ValueError("manifest invalid at (root): expected a list of rows, got %s"
                         % type(rows).__name__)
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            raise ValueError("manifest invalid at %d: expected an object, got %s"
                             % (i, type(r).__name__))
        for key in ("src", "dst", "mode"):
            if key not in r:
                raise ValueError("manifest invalid at %d: missing required key %r" % (i, key))
            if not isinstance(r[key], str):
                raise ValueError("manifest invalid at %d: %s must be a string, got %s"
                                 % (i, key, type(r[key]).__name__))

    seen = {}
    for i, r in enumerate(rows):
        for key in ("src", "dst"):
            p = r[key]
            if p.startswith("/") or ".." in pathlib.PurePosixPath(p).parts:
                raise ValueError("row %d %s must be relative and inside the repo: %r" % (i, key, p))
        if r["dst"] in seen:
            raise ValueError("duplicate dst %r (rows %d and %d)" % (r["dst"], seen[r["dst"]], i))
        seen[r["dst"]] = i
        if r["mode"] not in MODES:
            raise ValueError("row %d unknown mode %r" % (i, r["mode"]))

    schema = json.loads(pathlib.Path(schema_path).read_text(encoding="utf-8"))
    try:
        jsonschema.validate(rows, schema)
    except jsonschema.ValidationError as e:
        field = "/".join(str(p) for p in e.absolute_path) or "(root)"
        raise ValueError("manifest invalid at %s: %s" % (field, e.message))
    return rows


def apply_manifest(rows, cag=CAG, root=ROOT, dry_run=False):
    cag, root = pathlib.Path(cag), pathlib.Path(root)
    stats = {"applied": 0, "skipped_existing": 0, "deferred": 0, "missing": 0}
    missing = []
    for r in rows:
        if r["mode"] == "deferred":
            stats["deferred"] += 1
            continue
        src, dst = cag / r["src"], root / r["dst"]
        if not src.is_file():
            stats["missing"] += 1
            missing.append(r["src"])
            continue
        if r["mode"] == "rebase" and dst.exists():
            stats["skipped_existing"] += 1
            continue
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            if src.suffix == ".sh" or src.stat().st_mode & 0o111:
                dst.chmod(dst.stat().st_mode | 0o111)
        stats["applied"] += 1
    stats["missing_paths"] = missing
    return stats


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="report, write nothing")
    ap.add_argument("--only", default="", help="apply only rows whose dst starts with this prefix")
    ap.add_argument("--cag", default=str(CAG), help="source repo root (default %s)" % CAG)
    ap.add_argument("--manifest", default=str(MANIFEST),
                    help="manifest to apply (default %s)" % MANIFEST)
    ap.add_argument("--dest", default=str(ROOT),
                    help="destination repo root (default %s)" % ROOT)
    a = ap.parse_args(argv)
    rows = validate(load_manifest(a.manifest))
    if a.only:
        rows = [r for r in rows if r["dst"].startswith(a.only)]
    stats = apply_manifest(rows, cag=a.cag, root=a.dest, dry_run=a.dry_run)
    for p in stats["missing_paths"]:
        print("MISSING SOURCE: %s" % p)
    print("examined %d rows; applied %d, skipped-existing %d, deferred %d, missing %d"
          % (len(rows), stats["applied"], stats["skipped_existing"], stats["deferred"], stats["missing"]))
    return 1 if stats["missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
