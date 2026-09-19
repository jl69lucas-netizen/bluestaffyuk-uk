#!/usr/bin/env python3
"""facts_preserved_check.py — a rebuilt page must keep every fact its migrated body carried.

WHY THIS EXISTS. scripts/migration_parity.py measures SIZE — words, headings, images, embeds
against what the extractor promised — and that is the right question for a page migrated
verbatim and the wrong one for a page written fresh, whose heading list is SUPPOSED to change.
Dropping parity for a rebuilt page without putting anything in its place would mean the one
run that rewrites eleven pages is the one run with no content gate at all.

Facts = prices (£ amounts), puppy names (from data/puppies.json), health-test names,
credential phrases, image paths, YouTube embed ids. Extracted from the migrated page
(`--extract <slug>` BEFORE the rewrite, into data/facts/<slug>.json) and checked against
dist/<slug>/index.html after it. The extraction cannot be repeated once the page is rebuilt:
the body it reads no longer exists then, which is why the JSON is committed the moment it is
taken and why every change to the rules below has to be made while the migrated build is
still the build — after that, a re-extraction reads the rebuilt page and the gate becomes a
tautology.

HOW A FACT IS MATCHED, since none of this is plain substring search:
  prices  — compared as INTEGER PENCE, so £1200, £1,200 and £1,200.00 are one fact. The
            regex refuses a longer number it is only the head of (`£1,50` out of `£1,500`).
  names   — whole word: `\bRoman\b`, so Roman is not found inside Romance.
  tests   — stem at a word boundary: `\bvaccinat` matches vaccinated and vaccination. Bare
            `HC` and `KC` were in this list and are not: two capital letters match inside
            half the alphabet soup on a page (HC in `L-2-HGA/HC-HSF4`, KC in `KC-registered`)
            and made the gate report facts the page never claimed.
  creds   — the same stem rule, case-insensitively. `KC-registered` is a CREDENTIAL, not a
            test, and is matched here only.
  images  — the src, in the markup.
  embeds  — the YouTube id, in the markup.

A fact may be dropped only DELIBERATELY: the board record (data/boards/<slug>.json) lists it
under `dropped` with the reason the user accepted. Slugs in data/facts/rebuilt.json are exempt
from migration_parity.py and subject to this instead — the two gates never judge one page.

Usage:
  python3 scripts/facts_preserved_check.py --extract <slug>   # once, before the rewrite
  python3 scripts/facts_preserved_check.py --check            # every slug in rebuilt.json

Exit: 0 clean, 1 a fact went missing with no `dropped` entry behind it.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# `(?!\d)` is what stops the pattern settling for the head of a longer number: without it
# the homepage's `£1200` yielded the fact `£120`, which the page does not carry and which
# would therefore have failed forever. The leading run is `\d+` and not `\d{1,3}` for the
# other half of the same defect: the old site writes both £1200 and £1,200, and with a
# three-digit cap the lookahead does not truncate the unformatted one, it rejects it
# OUTRIGHT — a price silently absent from the fact set is worse than a wrong one, because
# nothing ever reports it. `pence()` below is what makes the two spellings one fact.
PRICE = re.compile(r"£\s?\d+(?:,\d{3})*(?:\.\d\d)?(?!\d)")
TESTS = ["L-2-HGA", "HC-HSF4", "DNA", "microchip", "vaccinat"]
CREDS = ["KC-registered", "Kennel Club", "DEFRA", "licence", "Lucy"]
SCRIPTY = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)
# Either quote style: the build emits double quotes, but a fact set is also read against
# hand-written HTML in the tests, and an extractor that silently finds no images in half the
# HTML it is given is a gate that passes by finding nothing.
IMG = re.compile(r"""<img[^>]+src=["']([^"']+)["']""")
EMBED = re.compile(r"youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{6,})")
TAG = re.compile(r"<[^>]+>")


def pence(price):
    """`£1,200.50` -> 120050. One integer per amount, so the two spellings of one price are
    one fact and a rebuild is free to write it the other way round."""
    digits = re.sub(r"[^\d.]", "", price)
    whole, _, frac = digits.partition(".")
    return int(whole or 0) * 100 + int((frac + "00")[:2])


def visible(html):
    """The readable text of a fragment. Script and style bodies go FIRST: stripping tags
    alone leaves the contents of a <script> behind as words, and one inlined JSON blob then
    supplies every price on the page."""
    return TAG.sub(" ", SCRIPTY.sub(" ", html))


def _stem(term, text):
    """A stem at a word boundary: `\\bvaccinat` finds vaccinated and vaccination, and `\\bHC`
    would have found HC inside nothing, which is why bare HC is no longer asked for."""
    return re.search(rf"\b{re.escape(term)}", text, re.I) is not None


def _word(term, text):
    return re.search(rf"\b{re.escape(term)}\b", text) is not None


def _prices(text):
    """Every distinct AMOUNT in the text, in value order, each keeping the first spelling it
    was written with. Two spellings of one amount are one fact, not two."""
    found = {}
    for p in PRICE.findall(text):
        found.setdefault(pence(p), p.strip())
    return [found[k] for k in sorted(found)]


def extract(html, names):
    """The fact set of one page body. Prices are sorted by VALUE, not as strings, so
    £1,500 precedes £1,700 and both precede nothing that reads larger than it is."""
    text = visible(html)
    return {
        "prices": _prices(text),
        "names": [n for n in names if _word(n, text)],
        "tests": [t for t in TESTS if _stem(t, text)],
        "creds": [c for c in CREDS if _stem(c, text)],
        "images": sorted(set(IMG.findall(html))),
        "embeds": sorted(set(EMBED.findall(html))),
    }


def page_body(html):
    """The rebuilt page's own content: `<main>`, or the whole document when there is none.

    The scope matters as much here as it does on the extraction side. Measured against the
    whole document, a price in the footer, a name in the nav and an image in the header all
    count as "still there", and a page could lose its entire body and pass."""
    found = MAIN.search(html)
    return found.group(1) if found else html


def missing(facts, new_html, dropped=None):
    """{kind: [facts the new page neither carries nor declares dropped]}.

    Images and embeds are looked for in the MARKUP (an image is a src, not a word); prices,
    names, tests and credentials in the visible text, so a price surviving only inside a
    JSON-LD blob or an alt attribute does not count as the reader still being told it.
    """
    dropped = dropped or {}
    body = page_body(new_html)
    text = visible(body)
    here = {pence(p) for p in PRICE.findall(text)}
    out = {}
    for k, vals in facts.items():
        drop = set(dropped.get(k, []))
        dropped_pence = {pence(p) for p in drop} if k == "prices" else set()
        miss = []
        for v in vals:
            if v in drop or (k == "prices" and pence(v) in dropped_pence):
                continue
            if k in ("images", "embeds"):
                present = v in body
            elif k == "prices":
                present = pence(v) in here
            elif k == "names":
                present = _word(v, text)
            else:
                present = _stem(v, text)
            if not present:
                miss.append(v)
        if miss:
            out[k] = miss
    return out


def dist_html(slug):
    """dist/<slug>/index.html, with `index` meaning the site root."""
    return ROOT / "dist" / ("" if slug == "index" else slug) / "index.html"


ARTICLE = re.compile(r"<article[^>]*>(.*?)</article>", re.S)
PROSE = re.compile(r"<article[^>]*prose-migrated[^>]*>(.*?)</article>", re.S)


def migrated_body(html):
    """The body the fact set is a fact about — the SAME two scopes migration_parity.py
    measures: `article.prose-migrated` for a migrated page, and a bare `<article>` for the
    blog post, whose body is rendered markdown and never carried that class. Falling straight
    to the whole document instead would fold the header, the footer and every nav link into
    the fact set, and the rebuild would then be required to keep chrome it never had."""
    return next((m.group(1) for m in (PROSE.search(html), ARTICLE.search(html)) if m), html)


def rebuilt_slugs():
    path = ROOT / "data/facts/rebuilt.json"
    return json.loads(path.read_text()) if path.exists() else []


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--extract", metavar="SLUG",
                    help="extract facts from dist/<slug>/ into data/facts/<slug>.json")
    ap.add_argument("--check", action="store_true",
                    help="check every slug in data/facts/rebuilt.json")
    a = ap.parse_args(argv)
    names = [p["name"] for p in json.loads((ROOT / "data/puppies.json").read_text())]

    if a.extract:
        slug = a.extract
        facts = extract(migrated_body(dist_html(slug).read_text(encoding="utf-8")), names)
        (ROOT / "data/facts").mkdir(parents=True, exist_ok=True)
        (ROOT / f"data/facts/{slug}.json").write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n",
                                                      encoding="utf-8")
        print(f"extracted facts for {slug}: "
              + ", ".join(f"{len(v)} {k}" for k, v in facts.items()))
        return 0

    rebuilt = rebuilt_slugs()
    problems = 0
    for slug in rebuilt:
        facts = json.loads((ROOT / f"data/facts/{slug}.json").read_text(encoding="utf-8"))
        record = ROOT / f"data/boards/{slug}.json"
        dropped = json.loads(record.read_text(encoding="utf-8")).get("dropped", {}) if record.exists() else {}
        html = dist_html(slug).read_text(encoding="utf-8")
        for kind, vals in missing(facts, html, dropped).items():
            for v in vals:
                print(f"{slug}: missing {kind} {v!r}")
                problems += 1
    print(f"examined {len(rebuilt)} rebuilt pages; {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
