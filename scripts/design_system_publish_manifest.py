#!/usr/bin/env python3
"""Prints the JSON `files` map the controller passes to the Artifact tool for the Design System.

Every file under docs/artifacts/design-system/project/ is published at its own path, so the
map is identity — the type reads `project/tokens.json`, `project/components/<Comp>/preview.html`
and the rest by those exact names. The type caps a version at 1,024 files; this prints the
count and refuses over 256 paths, which is the Artifact tool's own `files` limit.
"""
import json
import pathlib
import sys

OUT = pathlib.Path(__file__).resolve().parent.parent / "docs/artifacts/design-system/project"
LIMIT = 256

if __name__ == "__main__":
    if not OUT.is_dir():
        sys.exit("run npm run ds:build first")
    rel = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    if len(rel) > LIMIT:
        sys.exit(f"{len(rel)} files exceeds the Artifact tool's {LIMIT}-path `files` limit")
    print(json.dumps({f"project/{r}": f"project/{r}" for r in rel}, indent=1))
    print(f"\n{len(rel)} paths", file=sys.stderr)
