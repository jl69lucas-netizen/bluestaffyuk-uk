#!/usr/bin/env python3
"""data/redirects.json -> public/_redirects (Cloudflare Pages format)."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent


def render(rows):
    lines = ["# Generated from data/redirects.json by scripts/build_redirects.py — do not edit by hand"]
    lines += ["%s %s %d" % (r["from"], r["to"], r["type"]) for r in rows]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    rows = json.loads((ROOT / "data/redirects.json").read_text(encoding="utf-8"))["redirects"]
    (ROOT / "public/_redirects").write_text(render(rows), encoding="utf-8")
    print("wrote %d redirects" % len(rows))
