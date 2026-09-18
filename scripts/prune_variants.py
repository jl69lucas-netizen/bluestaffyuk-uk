#!/usr/bin/env python3
"""prune_variants.py — find every variant site in the kit, then get out of the way.

SPENT, AND KEPT FOR THE RECORD. This was a ONE-SHOT for Task 19. No kit file contains the
word `variant` any more — `tests/py/test_design_picks.py::test_after_prune_no_variant_prop_remains`
refuses one — so a run today finds no candidates and has nothing left to delete, and
`--check` is green by construction. It survives because it is the written-down account of
WHY the collapse was done by hand: the seven shapes listed below are the argument against
scripting a prop out of fourteen components, and that argument outlives the run it was
written for.

THIS SCRIPT DOES NOT REWRITE THE COMPONENTS, and the plan's Task 19 sketch that had it
substituting `const { variant = 'a', …` for a pinned constant is superseded by the Task 15
prune notes. Measured on the finished kit there were 68 `variant ===` sites across 14 files,
and every one of the shapes below defeats a line-oriented or regex substitution:

  · Hero, InfoCard and PageNav destructure their props over SEVERAL LINES, so the
    `variant = 'a'` default is not on the line that opens the destructure.
  · Button destructures TWICE — `Astro.props` is cast, and `type` is pulled out of `rest`
    in a second statement — so two prop lists change shape.
  · `markVariant` is a SECOND variant prop on SiteHeaderKit, SiteFooterKit and
    SectionDivider, coupled to the MARK's pick and not to their own row.
  · Faq defaults a prop to a FUNCTION CALL (`items = loadFaq()`), which must survive intact.
  · ContactFormKit NESTS its ternaries and hides `rows={variant === 'e' ? 3 : 5}` inside the
    block one of them owns; collapsing the outer branch alone leaves markup that still
    compiles and is unreachable.
  · SiteFooterKit branches in the FRONTMATTER (`const explore = variant === 'c' ? …`), which
    a template-only pass never sees.

So this prints the candidates — every file, its pick, and every line that mentions a variant
— and performs only the two deletions that cannot be got wrong: `_variant.ts` and the canvas
route directory. The collapse itself is done by hand, file by file, and the result is
verified by `tests/py/test_design_picks.py::test_after_prune_no_variant_prop_remains`, which
refuses any kit file that still contains the word `variant` at all.

    python3 scripts/prune_variants.py          # report + the two deletions
    python3 scripts/prune_variants.py --check  # report only; exit 1 while work remains
"""
import argparse
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = ROOT / "src/components/kit"
VARIANT_TS = KIT / "_variant.ts"
CANVAS_ROUTE = ROOT / "src/pages/design-canvas"


def rows():
    picks = json.loads((ROOT / "data/design/picks.json").read_text())
    comps = json.loads((ROOT / "data/design/components.json").read_text())
    out = [(r["file"], picks["picks"][r["id"]]["variant"]) for r in comps]
    # The mark is not a components.json row: its pick is the top-level `mark` key, and the
    # three components that pass `markVariant` collapse against THAT, not against their own.
    out.append(("Mark.astro", picks["mark"]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report only; do not delete _variant.ts or the canvas route")
    a = ap.parse_args(argv)

    total = 0
    for name, pick in rows():
        f = KIT / name
        if not f.exists():
            print(f"{name}: MISSING")
            continue
        hits = [(i, line.rstrip()) for i, line in enumerate(f.read_text().splitlines(), 1)
                if "variant" in line.lower()]
        total += len(hits)
        print(f"\n{name} — keep variant '{pick}'  ({len(hits)} line(s) to collapse)")
        for i, line in hits:
            print(f"  {i:>4}: {line.strip()[:120]}")

    print(f"\n{total} line(s) mention a variant across {len(rows())} kit files.")
    if a.check:
        print("--check: nothing deleted.")
        return 1 if total else 0

    if VARIANT_TS.exists():
        VARIANT_TS.unlink()
        print(f"deleted {VARIANT_TS.relative_to(ROOT)}")
    if CANVAS_ROUTE.exists():
        shutil.rmtree(CANVAS_ROUTE)
        print(f"deleted {CANVAS_ROUTE.relative_to(ROOT)}/")
    print("now collapse each file by hand: delete the branches that are not the pick, their "
          "CSS, the data-variant attributes and the variant comment block.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
