#!/usr/bin/env python3
"""Gate: no launch placeholder survives into a release build.

Foundation deliberately ships stand-ins. `SITE_URL_PLACEHOLDER` stands in for the domain
nobody has bought yet, `PHONE_PLACEHOLDER` for the number project 6 will provision, and
`FORMSPREE_ID_PLACEHOLDER` for the form endpoint, as the build-time sentinel
`src/components/ContactForm.astro` falls back to when `PUBLIC_FORMSPREE_ID` is unset — the
env var is the endpoint's ONE name in `.claude/`; this token exists only so a build that
shipped without it is visible here. Two more
stand in for unverified facts rather than unprovisioned services: `LICENCE_CLAIM_PLACEHOLDER`
and `LEGAL_CLAIM_PLACEHOLDER` hold the breeder-licence and Lucy's-Law claims the skill
re-base would otherwise have asserted, until Lisa Bright confirms them. Every one
of them is correct today and catastrophic on launch day: a canonical pointing at
`https://SITE_URL_PLACEHOLDER/`, or a `tel:` link nobody can ring, is the kind of defect
that is invisible in review and obvious to the first visitor.

So the gate is conditional rather than absolute. It always COUNTS and always PRINTS — a
pre-launch build stays green while showing exactly how much stand-in text is still in
`dist/` — and it only FAILS when `BSUK_RELEASE=1` says this build is meant to go live.
An unconditional failure would have to be commented out for every Foundation build, which
is the same as not having the gate; an unconditional pass could ship a placeholder.

Usage:  python3 scripts/placeholder_check.py          # count and report, always exit 0
        BSUK_RELEASE=1 python3 scripts/placeholder_check.py   # exit 1 if any count > 0
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

PLACEHOLDERS = ("SITE_URL_PLACEHOLDER", "PHONE_PLACEHOLDER", "FORMSPREE_ID_PLACEHOLDER",
                "LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER")

# The claim placeholders live in the instruction tree, not in dist/ — a skill that tells a
# writer to assert an unconfirmed licence is the defect, and it never reaches a built page
# to be caught there. So the scan covers dist/ plus these source roots. `docs/reference`
# joined them in Task 13: seo-rules.md Rule 7 and the credentials table are read the same
# way a skill is, and a stand-in that survives launch there is the same defect one rung up.
SOURCE_ROOTS = (".claude/skills", ".claude/agents", "docs/reference")

# Text formats only. A byte scan of dist/ would also walk every baked WebP, which cannot
# contain a placeholder and would dominate the run time.
TEXT_SUFFIXES = {".html", ".xml", ".txt", ".json", ".js", ".css", ".mjs", ".map",
                 ".webmanifest", ".md"}

# How many files are listed per placeholder before the tail is summarised. The COUNT is
# never capped, and a truncated list says so — a silent cut reads as "that is all of them".
LIST_CAP = 20


def _label(path, root):
    """Repo-root-relative path. `dist/index.html` and `.claude/skills/x/SKILL.md` are both
    `x/SKILL.md` when reported relative to their own scan base, which makes a skill hit
    indistinguishable from a built-page hit."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(pathlib.Path(root).resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def scan(dist, roots=(), root=ROOT):
    """{placeholder: total occurrences} and {placeholder: [files]} across dist/ and roots."""
    counts = {p: 0 for p in PLACEHOLDERS}
    files = {p: set() for p in PLACEHOLDERS}
    bases = [pathlib.Path(dist)] + [pathlib.Path(r) for r in roots]
    for base in bases:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for placeholder in PLACEHOLDERS:
                n = text.count(placeholder)
                if n:
                    counts[placeholder] += n
                    files[placeholder].add(_label(path, root))
    return counts, {p: sorted(f) for p, f in files.items()}


def main(root=ROOT, dist=None, release=None):
    root = pathlib.Path(root)
    dist = pathlib.Path(dist) if dist else root / "dist"
    if release is None:
        release = os.environ.get("BSUK_RELEASE") == "1"

    if not dist.is_dir():
        print("FAIL: no dist/ to scan — a build that does not exist is not placeholder-free.")
        return 1

    counts, files = scan(dist, [root / r for r in SOURCE_ROOTS], root=root)
    total = sum(counts.values())
    mode = "release" if release else "pre-launch"
    print("# Placeholders (%s build)" % mode)
    for placeholder in PLACEHOLDERS:
        print("  %-24s %5d occurrence(s) in %d file(s)"
              % (placeholder, counts[placeholder], len(files[placeholder])))
    print("  %-24s %5d" % ("TOTAL", total))

    if not release:
        print("placeholders: %d (advisory — set BSUK_RELEASE=1 to make this blocking)" % total)
        return 0
    if total:
        for placeholder in PLACEHOLDERS:
            listed = files[placeholder]
            for f in listed[:LIST_CAP]:
                print("  %s — %s" % (placeholder, f))
            if len(listed) > LIST_CAP:
                print("  %s — … and %d more" % (placeholder, len(listed) - LIST_CAP))
        print("FAIL: BSUK_RELEASE=1 and %d placeholder occurrence(s) remain in dist/ "
              "and the instruction tree." % total)
        return 1
    print("placeholders: 0 — release build is clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
