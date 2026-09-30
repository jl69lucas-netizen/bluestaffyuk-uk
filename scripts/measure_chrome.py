#!/usr/bin/env python3
"""Measure the site's real chrome from dist/ — the input to WHITELIST_SNIPPETS.

The DUP whitelist exempts the lines that LEGITIMATELY repeat. Guessing that list is how a
whitelist stops being evidence, so it is measured, and this script is the measurement, kept
runnable so the next person can reproduce and re-measure it after a redesign.

Method (the one used for the 2026-09-17 re-base in scripts/dup_content_audit.py):

  1. Tokenise every built page with the auditor's own tokeniser (so the counts mean the same
     thing in both places).
  2. Count, for each MIN_WORDS shingle, how many PAGES carry it (document frequency, not pair
     count — 45 pairs is 10 pages, and pair counts make thin chrome look enormous).
  3. Keep shingles at or above --min-pages, merge adjacent kept shingles back into maximal
     runs, and report each run with the set of pages carrying it.
  4. Reduce each run to its INVARIANT CORE: the sub-run carried by the MOST pages (longest
     wins a tie). A merged run is the longest run on the pages that share it in full;
     whitelisting that leaves the shorter variant other pages carry unexempted, which is
     exactly how the first draft of this whitelist reported the same CTA fragment nine
     times and the delivery line eight. The core is what goes in WHITELIST_SNIPPETS.

Reading the output: a run carried by a large share of the pages, across different page
TYPES, is chrome and belongs in WHITELIST_SNIPPETS (use the CORE line, not the RUN line).
A run carried by one templated cluster is page prose — the migrated-content baseline — and
must stay OUT of the whitelist so the gate keeps reporting it.

Usage:
  python3 scripts/measure_chrome.py                    # every page in dist/
  python3 scripts/measure_chrome.py --min-pages 6      # stricter chrome threshold
  python3 scripts/measure_chrome.py --top 40           # print only the widest runs
"""
import argparse
import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _slugs import page_key
from dup_content_audit import MIN_WORDS, norm, words


def measure(dist: pathlib.Path, min_pages: int):
    """[(core_words, run_words, {slug, ...}), ...], widest group first."""
    pages = {page_key(p, dist): words(p) for p in dist.rglob("index.html")}
    docfreq = collections.Counter()
    for ws in pages.values():
        for s in {norm(ws[i:i + MIN_WORDS]) for i in range(len(ws) - MIN_WORDS + 1)}:
            docfreq[s] += 1

    runs = collections.defaultdict(set)
    for slug, ws in pages.items():
        keep = [docfreq[norm(ws[j:j + MIN_WORDS])] >= min_pages
                for j in range(len(ws) - MIN_WORDS + 1)]
        j = 0
        while j < len(keep):
            if not keep[j]:
                j += 1
                continue
            start = j
            while j < len(keep) and keep[j]:
                j += 1
            runs[tuple(ws[start:j - 1 + MIN_WORDS])].add(slug)

    out = []
    for run, slugs in runs.items():
        core, core_pages = _core(run, pages)
        out.append((core, core_pages, run, slugs))
    out.sort(key=lambda r: (-len(r[3]), -len(r[0])))
    return pages, out


def _core(run, pages):
    """(sub-run carried by the most pages, that page count) — longest wins a tie.

    The whitelist stem must be the part that is invariant across every page carrying the
    chrome; anything longer is one page's local phrasing and exempts nothing elsewhere.
    """
    best, best_n = run, -1
    for n in range(len(run), MIN_WORDS - 1, -1):
        for k in range(0, len(run) - n + 1):
            cand = run[k:k + n]
            hits = sum(1 for ws in pages.values() if _contains(ws, cand))
            if hits > best_n:
                best, best_n = cand, hits
    return best, best_n


def _contains(haystack, needle):
    n = len(needle)
    return any(tuple(haystack[i:i + n]) == tuple(needle) for i in range(len(haystack) - n + 1))


def main():
    ap = argparse.ArgumentParser(
        prog="measure_chrome.py",
        description="Measure repeated runs in dist/ so WHITELIST_SNIPPETS can be derived "
                    "rather than guessed.",
        epilog="Whitelist the CORE line of a run carried across page TYPES; leave a run "
               "carried by one templated cluster out — that is the content baseline.")
    ap.add_argument("--dist", default="dist", help="built site directory (default dist)")
    ap.add_argument("--min-pages", type=int, default=3,
                    help="a shingle counts as repeated at this many pages (default 3)")
    ap.add_argument("--top", type=int, default=0, help="print only the N widest runs")
    ap.add_argument("--slugs", action="store_true", help="list every carrying page, not just a sample")
    ns = ap.parse_args()

    dist = pathlib.Path(ns.dist)
    if not dist.is_dir():
        sys.exit(f"no built site at {dist}/ — run the build first")
    pages, groups = measure(dist, ns.min_pages)
    if ns.top:
        groups = groups[:ns.top]
    for core, core_pages, run, slugs in groups:
        sample = sorted(slugs) if ns.slugs else sorted(slugs)[:4]
        more = "" if ns.slugs or len(slugs) <= 4 else f" (+{len(slugs) - 4} more)"
        print(f"=== {len(slugs)}/{len(pages)} pages")
        print(f"  RUN  [{len(run):3d}w] {norm(run)}")
        print(f"  CORE [{len(core):3d}w on {core_pages} pages] {norm(core)}")
        print(f"  ON   {', '.join(sample)}{more}\n")
    print(f"examined {len(pages)} pages; {len(groups)} repeated run(s) at >={ns.min_pages} pages")


if __name__ == "__main__":
    main()
