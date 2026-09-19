#!/usr/bin/env python3
"""facts_preserved_check.py — a rebuilt page must keep every fact its migrated body carried.

WHY THIS EXISTS. scripts/migration_parity.py measures SIZE — words, headings, images, embeds
against what the extractor promised — and that is the right question for a page migrated
verbatim and the wrong one for a page written fresh, whose heading list is SUPPOSED to change.
Dropping parity for a rebuilt page without putting anything in its place would mean the one
run that rewrites eleven pages is the one run with no content gate at all.

Facts = prices (£ amounts), puppy names (from data/puppies.json), health-test names,
credential phrases, image paths, YouTube embed ids. Extracted ONCE from the migrated page
(`--extract <slug>` BEFORE the rewrite, into data/facts/<slug>.json) and checked against
dist/<slug>/index.html after it. The extraction cannot be repeated later: after the rewrite
the page it reads no longer exists, which is why the JSON is committed.

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
PRICE = re.compile(r"£\s?\d{1,3}(?:,\d{3})*(?:\.\d\d)?")
TESTS = ["L-2-HGA", "HC-HSF4", "HC", "DNA", "KC", "microchip", "vaccinat"]
CREDS = ["KC-registered", "Kennel Club", "DEFRA", "licence", "Lucy"]
# Either quote style: the build emits double quotes, but a fact set is also read against
# hand-written HTML in the tests, and an extractor that silently finds no images in half the
# HTML it is given is a gate that passes by finding nothing.
IMG = re.compile(r"""<img[^>]+src=["']([^"']+)["']""")
EMBED = re.compile(r"youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{6,})")
TAG = re.compile(r"<[^>]+>")


def extract(html, names):
    """The fact set of one page body. Prices are sorted by VALUE, not as strings, so
    £1,500 precedes £1,700 and both precede nothing that reads larger than it is."""
    text = TAG.sub(" ", html)
    return {
        "prices": sorted(set(PRICE.findall(text)), key=lambda p: int(re.sub(r"[^\d]", "", p))),
        "names": [n for n in names if re.search(rf"\b{re.escape(n)}\b", text)],
        "tests": [t for t in TESTS if t in text],
        "creds": [c for c in CREDS if c.lower() in text.lower()],
        "images": sorted(set(IMG.findall(html))),
        "embeds": sorted(set(EMBED.findall(html))),
    }


def missing(facts, new_html, dropped=None):
    """{kind: [facts the new page neither carries nor declares dropped]}.

    Images and embeds are looked for in the MARKUP (an image is a src, not a word); prices,
    names and tests in the visible text, so a price surviving only inside a JSON-LD blob or an
    alt attribute does not count as the reader still being told it.
    """
    dropped = dropped or {}
    text = TAG.sub(" ", new_html)
    out = {}
    for k, vals in facts.items():
        drop = set(dropped.get(k, []))
        miss = []
        for v in vals:
            if v in drop:
                continue
            if k in ("images", "embeds"):
                present = v in new_html
            elif k == "creds":
                present = v.lower() in text.lower()
            else:
                present = v in text
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
