#!/usr/bin/env python3
"""retired_facts_check.py — no retired fact on a built page, in rendered data or in src/.

The fact lint (tests/py/test_agent_facts.py) reads the instruction tree only: agents,
skills and docs/reference. Nothing read what SHIPS, so Known Issue 65 — eleven indexable
city pages printing a retired delivery fee, a retired price band, a "non-refundable"
deposit, collection from the former city and "council-licensed" — was found by hand. This
gate sweeps both tenses of the site (audit D5):

  dist      every built page (dist/**/index.html) minus the specimen routes, visible text
            plus JSON-LD
  data      the data files pages render facts from: data/locations.json (field by field,
            per city row), settings, puppies, price matrix, FAQ and reviews
  src       src/**/*.{astro,ts,tsx,js,mjs,md,mdx} with comments stripped — a comment that
            records a dropped figure is history, not copy

and fails on
  amount    a £ figure whose value is not locked: the deposit, the two prices, the two
            balances (price less deposit), the delivery band ends, the two locked ranges and
            £0 (collection is free); values are read from data/settings.json and
            data/price-matrix.json, never typed here. Trade-off: a retired figure that
            happens to equal a locked one (a balance) passes on its own — the retired band
            it sits in still fails
  term      "non-refundable", "council-licensed" / "council licensed"
  city      the former city (Known Issue 16) anywhere but its own two city pages and the
            anchor text of a link to one of them

WHAT IS NOT SCANNED, and why. data/boards/, data/facts/ and data/verbatim/ record retired
wording ON PURPOSE (`dropped.prices` is the accounting of what a rebuild struck); a figure
there only matters if it renders, and dist/ is where rendering is judged. data/queries/raw/
is competitor SERP text.

THE ALLOWLIST. data/quality/retired-facts-allowlist.json names every offender that was live
on 2026-09-26 (Known Issue 65) — the migrated city bodies project 5 rewrites. It exists so
this gate can enter check:all green today and still fail the first NEW retired fact. It only
shrinks: an entry that no longer fires is a FAIL too (remove it), a rebuilt page can never
carry one, and tests/py/test_retired_facts_check.py pins its ceiling.

Exit 1 on any finding outside the allowlist or any stale entry, 2 when dist/ is missing.
Usage: python3 scripts/retired_facts_check.py [--json]   |   npm run check:retired
"""
import html.parser
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWLIST = ROOT / "data" / "quality" / "retired-facts-allowlist.json"

SPECIMEN_PREFIXES = ("board-preview/", "kit-preview/")
FORMER_CITY = "Glasgow"
FORMER_CITY_SLUGS = ("staffy-breeding-dogs-glasgow", "staffy-puppies-for-sale-glasgow")
TERMS = re.compile(r"(?i)\bnon-refundable\b|\bcouncil[- ]licensed\b")
AMOUNT = r"£\d[\d,]*(?<![,])"
MONEY = re.compile(AMOUNT + r"(?:\s*[–—-]\s*" + AMOUNT + r")?")
RENDERED_DATA = ("settings.json", "puppies.json", "price-matrix.json", "faq.json", "reviews.json")
LOCATION_FIELDS = ("title", "h1", "description", "body_html")
SRC_SUFFIXES = {".astro", ".ts", ".tsx", ".js", ".mjs", ".md", ".mdx"}
# The one sanctioned spelling of the retired word in code: the false branch of a ternary on
# the LOCKED setting (data/settings.json deposit_refundable: true), so it never renders.
REFUNDABLE_TERNARY = re.compile(
    r"deposit_refundable\s*\?\s*(['\"`])refundable\1\s*:\s*(['\"`])non-refundable\2")


def locked_amounts(root=ROOT):
    """({single values}, {(low, high) ranges}) — every £ figure the site may print."""
    s = json.loads((root / "data" / "settings.json").read_text(encoding="utf-8"))
    p = json.loads((root / "data" / "price-matrix.json").read_text(encoding="utf-8"))
    singles = {0, s["deposit_gbp"], p["deposit_gbp"], p["male_gbp"], p["female_gbp"],
               p["male_gbp"] - p["deposit_gbp"], p["female_gbp"] - p["deposit_gbp"],
               s["delivery_min_gbp"], s["delivery_max_gbp"]}
    ranges = {(s["delivery_min_gbp"], s["delivery_max_gbp"]),
              (min(p["male_gbp"], p["female_gbp"]), max(p["male_gbp"], p["female_gbp"]))}
    return singles, ranges


def _value(token):
    return int(token.replace("£", "").replace(",", ""))


def amount_findings(text, locked):
    """Every £ figure (or range) in `text` that is not locked, spelled as found."""
    singles, ranges = locked
    out = []
    for m in MONEY.finditer(text):
        parts = re.findall(AMOUNT, m.group(0))
        vals = tuple(_value(x) for x in parts)
        ok = vals[0] in singles if len(vals) == 1 else vals in ranges
        if not ok:
            out.append(re.sub(r"\s*[–—-]\s*", "–", m.group(0).strip()))
    return out


class _Text(html.parser.HTMLParser):
    """Visible text plus JSON-LD. Text inside <a> whose href names one of the former city's
    own pages is collected apart, because naming the city a page is ABOUT is not a claim."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip, self.city_link = [], 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "style" or (tag == "script" and a.get("type") != "application/ld+json"):
            self.skip += 1
        if tag == "a" and any(s in (a.get("href") or "") for s in FORMER_CITY_SLUGS):
            self.city_link += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self.skip:
            self.skip -= 1
        if tag == "a" and self.city_link:
            self.city_link -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(("link" if self.city_link else "text", data))


def html_findings(markup, locked, city_page=False):
    p = _Text()
    p.feed(markup)
    text = " ".join(d for _, d in p.parts)
    plain = " ".join(d for kind, d in p.parts if kind == "text")
    return text_findings(text, locked, city=not city_page, city_text=plain)


def text_findings(text, locked, city=True, city_text=None):
    """[(kind, value)] for one blob. `city=False` switches the former-city rule off (the
    city's own page); `city_text` is what that rule reads when it is not `text` itself."""
    found = [("amount", a) for a in amount_findings(text, locked)]
    found += [("term", m.group(0).lower().replace(" ", "-")) for m in TERMS.finditer(text)]
    if city and FORMER_CITY in (text if city_text is None else city_text):
        found.append(("city", FORMER_CITY))
    return found


def strip_comments(src, suffix):
    """Code minus its comments: // and /* */ in script, {/* */} and <!-- --> in markup.
    A `//` inside a string or URL (`'https://…'`) is kept: it must follow a line start or
    whitespace and not a quote or a colon."""
    if suffix in (".md", ".mdx"):
        return re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    src = re.sub(r"\{/\*.*?\*/\}", " ", src, flags=re.S)
    src = re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"(?m)(^|\s)//.*$", r"\1", src)


def scan_dist(dist, locked):
    out, n = {}, 0
    for page in sorted(pathlib.Path(dist).glob("**/index.html")):
        rel = page.parent.relative_to(dist).as_posix()
        key = "index" if rel == "." else rel
        if (key + "/").startswith(SPECIMEN_PREFIXES):
            continue
        n += 1
        city_page = key.split("/")[-1] in FORMER_CITY_SLUGS
        for kind, value in html_findings(page.read_text(encoding="utf-8"), locked, city_page):
            out.setdefault(f"dist:{key}:{kind}:{value}", 0)
            out[f"dist:{key}:{kind}:{value}"] += 1
    return out, n


def scan_data(root, locked):
    out, n = {}, 0
    rows = json.loads((root / "data" / "locations.json").read_text(encoding="utf-8"))
    for row in rows:
        city_page = row["slug"] in FORMER_CITY_SLUGS
        for field in LOCATION_FIELDS:
            n += 1
            value = row.get(field) or ""
            found = (html_findings(value, locked, city_page) if field == "body_html"
                     else text_findings(value, locked, city=not city_page))
            for kind, v in found:
                k = f"data:locations.json/{row['slug']}/{field}:{kind}:{v}"
                out[k] = out.get(k, 0) + 1
    for name in RENDERED_DATA:
        path = root / "data" / name
        if not path.exists():
            continue
        n += 1
        for kind, v in text_findings(path.read_text(encoding="utf-8"), locked):
            k = f"data:{name}:{kind}:{v}"
            out[k] = out.get(k, 0) + 1
    return out, n


def scan_src(root, locked):
    out, n = {}, 0
    for path in sorted((root / "src").rglob("*")):
        if not path.is_file() or path.suffix not in SRC_SUFFIXES:
            continue
        n += 1
        code = REFUNDABLE_TERNARY.sub(" ", strip_comments(path.read_text(encoding="utf-8"), path.suffix))
        for kind, v in text_findings(code, locked):
            k = f"src:{path.relative_to(root).as_posix()}:{kind}:{v}"
            out[k] = out.get(k, 0) + 1
    return out, n


def load_allowlist(path=ALLOWLIST):
    if not pathlib.Path(path).exists():
        return {}
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8")).get("entries", {})


def run(root=ROOT, dist=None, allowlist=None):
    """{'examined': {...}, 'new': [...], 'allowed': [...], 'stale': [...]}; raises
    FileNotFoundError when dist/ is missing — a sweep of no pages is not a pass."""
    root = pathlib.Path(root)
    dist = root / "dist" if dist is None else pathlib.Path(dist)
    if not dist.exists():
        raise FileNotFoundError(f"{dist} does not exist — build first (npm run build)")
    locked = locked_amounts(root)
    found, examined = {}, {}
    for scope, fn in (("dist", lambda: scan_dist(dist, locked)),
                      ("data", lambda: scan_data(root, locked)),
                      ("src", lambda: scan_src(root, locked))):
        f, n = fn()
        found.update(f)
        examined[scope] = n
    allowed = load_allowlist(ALLOWLIST if allowlist is None else allowlist)
    return {"examined": examined,
            "new": sorted(k for k in found if k not in allowed),
            "allowed": sorted(k for k in found if k in allowed),
            "stale": sorted(k for k in allowed if k not in found)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        r = run()
    except FileNotFoundError as e:
        print(f"retired-facts ERROR {e}")
        return 2
    ex = r["examined"]
    print(f"retired-facts: examined {ex['dist']} built pages, {ex['data']} data fields/files, "
          f"{ex['src']} src files; {len(r['allowed'])} allowlisted (Known Issue 65), "
          f"{len(r['new'])} new, {len(r['stale'])} stale")
    if 0 in ex.values():
        print("  FAIL examined-zero: a scope examined nothing, which is not a pass")
    for k in r["new"]:
        print(f"  FAIL retired-fact {k}")
    for k in r["stale"]:
        print(f"  FAIL allowlist-stale {k} no longer fires — remove it from "
              f"{ALLOWLIST.relative_to(ROOT)} (the list only shrinks)")
    if "--json" in argv:
        out = ROOT / "docs" / "reports" / "retired-facts.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    return 1 if (r["new"] or r["stale"] or 0 in ex.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
