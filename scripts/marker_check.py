#!/usr/bin/env python3
"""Gate: no C.A.Gs parrot vocabulary survives anywhere the port touched.

The port copies a parrot breeder's operating system into a dog breeder's repo. Every ported
file is either rewritten by hand or judged not to need it, and the only honest proof that
the judgement was right is a scan that cannot be argued with.

So: twelve markers, case-insensitive, NO ALLOWLIST. A legitimate-looking hit is a design
error to fix, not an exception to record — the moment this gate grows an allowlist it stops
being evidence and becomes a list of the places nobody re-based.

Scanned: every `dst` the manifest names that was actually written (deferred rows write
nothing), plus CLAUDE.md, rules/, docs/reference/, package.json, tests/render/ and
scripts/dup_content_audit.py — the last because its whitelist is re-measured in Task 15 and
nothing else would catch a parrot stem left in it.

ONE path is excluded, and the exclusion is structural rather than an allowlist:
`data/port-manifest.json` itself. Every `src` in it is a CAG path, most beginning `cag-`;
a manifest that could pass this gate would be a manifest that failed to record the port.

Output shape matches the Foundation gates: `examined N files; 0 problems`.

Usage:  python3 scripts/marker_check.py   |   npm run check:markers
"""
import pathlib
import sys

from port_from_cag import load_manifest, validate

ROOT = pathlib.Path(__file__).resolve().parent.parent

MARKERS = (
    "parrot", "african grey", "african-grey", "timneh", "congo", "clutch",
    "c.a.gs", "cags", "congoafricangreys", "agcare", "xrejpnvn", "cag-",
)

FIXED_ROOTS = (
    "CLAUDE.md", "rules", "docs/reference", "package.json", "tests/render",
    "scripts/dup_content_audit.py",
)

# The record of the port cannot describe the port without naming CAG. Structural, not an
# allowlist: exactly one path, and it is the only file in the repo whose CONTENT IS the list
# of parrot-named sources.
EXCLUDED = ("data/port-manifest.json",)

# How many hits are printed before the tail is summarised. The COUNT is never capped.
PRINT_CAP = 60

TEXT_SUFFIXES = {
    ".md", ".json", ".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".html", ".css",
    ".sh", ".txt", ".yml", ".yaml", ".xml", ".astro",
}


def hits_in(path):
    """[(line_number, marker, line_text)] for every marker occurrence in a text file.

    Markers overlap: `congoafricangreys` contains `congo`. Reporting both would double-count
    one defect and name it less precisely than the repo does, so when one matched marker is
    a substring of another matched marker on the same line only the longer one is reported.
    The only overlapping pair in MARKERS today is `congo` / `congoafricangreys`; re-check this
    rule when a marker is added.
    """
    # errors="replace", like placeholder_check.py: a stray non-UTF-8 byte must not buy a
    # file a silent pass, and an OSError is a real fault that belongs in the traceback.
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        matched = [m for m in MARKERS if m in low]
        for m in matched:
            # Line-scoped: a standalone `congo` sharing a line with `congoafricangreys` is
            # absorbed. Acceptable for a zero-tolerance gate — the line is reported either way.
            if any(other != m and m in other for other in matched):
                continue
            out.append((n, m, line.strip()))
    return out


def _walk(p):
    if p.is_file():
        return [p] if p.suffix.lower() in TEXT_SUFFIXES else []
    return sorted(f for f in p.rglob("*")
                  if f.is_file() and f.suffix.lower() in TEXT_SUFFIXES
                  and "__pycache__" not in f.parts and "node_modules" not in f.parts)


def scan_roots(root=ROOT):
    """Every file this gate judges: written manifest dsts + the fixed roots, deduped."""
    root = pathlib.Path(root)
    excluded = {(root / e).resolve() for e in EXCLUDED}
    files = []
    manifest = root / "data/port-manifest.json"
    if manifest.is_file():
        rows = load_manifest(manifest)
        # Task 1's validator owns the readable messages for a drifted manifest. An empty
        # list is left alone: it is a repo with nothing ported yet, not a malformed record.
        if rows:
            validate(rows)
        for r in rows:
            if r["mode"] == "deferred":
                continue
            files += _walk(root / r["dst"])
    for rel in FIXED_ROOTS:
        p = root / rel
        if p.exists():
            files += _walk(p)
    seen, out = set(), []
    for f in files:
        rp = f.resolve()
        if rp in excluded or rp in seen:
            continue
        seen.add(rp)
        out.append(f)
    return out


def main(root=ROOT):
    root = pathlib.Path(root)
    files = scan_roots(root)
    problems = 0
    for f in files:
        for n, marker, line in hits_in(f):
            problems += 1
            if problems <= PRINT_CAP:
                print("  %s:%d  [%s]  %s" % (f.relative_to(root), n, marker, line[:140]))
    if problems > PRINT_CAP:
        print("  … and %d more" % (problems - PRINT_CAP))
    print("examined %d files; %d problems" % (len(files), problems))
    if problems:
        print("FAIL — a parrot marker is a re-base that did not happen. There is no allowlist.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
