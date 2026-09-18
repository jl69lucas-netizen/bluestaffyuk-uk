#!/usr/bin/env python3
"""Prints the JSON `files` map the controller passes to the Artifact tool for the canvas."""
import json, pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs/artifacts/canvas/project"

if __name__ == "__main__":
    names = sorted(p.name for p in OUT.glob("*.dc.html"))
    print(json.dumps({f"project/{n}": f"project/{n}" for n in names}, indent=1))
