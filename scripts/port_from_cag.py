#!/usr/bin/env python3
"""Apply data/port-manifest.json: copy files from ~/Downloads/CAG into this repo.

The manifest is the record of the port, not a convenience. Four modes:

  copy      byte-identical, same relative path. Rewritten on every run.
  rename    byte-identical, new path (cag-x.md -> bsuk-x.md). Rewritten on every run.
  rebase    copied ONCE, then hand-edited. NEVER overwritten. The hand edits are the
            deliverable; a second run that re-copied the parrot source would undo the
            entire re-base silently, and scripts/marker_check.py would only find
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

Exits non-zero when any non-deferred row's src is missing or its row is blocked (a dst
that already exists as a directory, or a src resolving outside CAG), so a manifest that
drifts from CAG fails loudly instead of half-applying. `--only` matching no row is also
an error, because it means the caller's prefix is wrong and nothing was ported.
"""
import argparse
import json
import os
import pathlib
import shutil
import sys

import jsonschema

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
        if r["mode"] == "rename" and r["src"] == r["dst"]:
            raise ValueError("row %d rename row must change the path: %r" % (i, r["dst"]))

    schema = json.loads(pathlib.Path(schema_path).read_text(encoding="utf-8"))
    try:
        jsonschema.validate(rows, schema)
    except jsonschema.ValidationError as e:
        field = "/".join(str(p) for p in e.absolute_path) or "(root)"
        raise ValueError("manifest invalid at %s: %s" % (field, e.message))
    return rows


def _escapes_root(cag, src):
    """True when src resolves outside the CAG root (a symlink pointing off the source tree).

    Such a row reads as innocent in the manifest but would copy an arbitrary file from the
    machine into the repo, so it is refused rather than applied.
    """
    try:
        cag_real = str(cag.resolve())
        return os.path.commonpath([cag_real, str(src.resolve())]) != cag_real
    except ValueError:
        return True


def apply_manifest(rows, cag=CAG, root=ROOT, dry_run=False):
    cag, root = pathlib.Path(cag), pathlib.Path(root)
    stats = {"applied": 0, "skipped_existing": 0, "deferred": 0, "missing": 0, "blocked": 0}
    missing, blocked = [], []

    def block(row, why):
        stats["blocked"] += 1
        blocked.append(row["dst"])
        blocked_reasons.append((row["dst"], why))

    blocked_reasons = []
    for r in rows:
        if r["mode"] == "deferred":
            stats["deferred"] += 1
            continue
        src, dst = cag / r["src"], root / r["dst"]
        if not src.is_file():
            stats["missing"] += 1
            missing.append(r["src"])
            continue
        if _escapes_root(cag, src):
            block(r, "src %s resolves outside %s" % (r["src"], cag))
            continue
        if dst.is_dir():
            # shutil.copyfile onto a directory raises IsADirectoryError mid-run and leaves
            # the port half-applied; refuse the row and let the summary report it instead.
            block(r, "dst exists as a directory")
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
    stats["blocked_paths"] = blocked
    stats["blocked_reasons"] = blocked_reasons
    return stats


def select_rows(rows, only):
    """Rows whose dst is `only` itself or lies beneath it.

    Matching stops at a path boundary: `--only rules` takes `rules/x.md` and leaves
    `rules-old/x.md` alone, which a bare startswith() would quietly have swept in.
    """
    prefix = only.rstrip("/")
    return [r for r in rows if r["dst"] == prefix or r["dst"].startswith(prefix + "/")]


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
        rows = select_rows(rows, a.only)
        if not rows:
            print("--only %r matched no rows in %s" % (a.only, a.manifest))
            return 1
    stats = apply_manifest(rows, cag=a.cag, root=a.dest, dry_run=a.dry_run)
    for p in stats["missing_paths"]:
        print("MISSING SOURCE: %s" % p)
    for dst, why in stats["blocked_reasons"]:
        print("BLOCKED: %s (%s)" % (dst, why))
    print("examined %d rows; applied %d, skipped-existing %d, deferred %d, missing %d, blocked %d"
          % (len(rows), stats["applied"], stats["skipped_existing"], stats["deferred"],
             stats["missing"], stats["blocked"]))
    return 1 if (stats["missing"] or stats["blocked"]) else 0


if __name__ == "__main__":
    sys.exit(main())
