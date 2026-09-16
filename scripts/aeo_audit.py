#!/usr/bin/env python3
"""
AEO audit — the measurable half of .claude/skills/bsuk-aeo-pass/SKILL.md.

Answer Engine Optimization: does this page give an AI engine something it can lift?
Runs over dist/ (the rendered page, never the source).

WHAT THIS CAN AND CANNOT MEASURE — read before trusting a pass.
Measurable, and measured here:
  * BLUF        — is the first sentence under each H2 short and declarative?  (PROXY)
  * Entities    — binomial, breeder name, place, credentials, pronoun density
  * Freshness   — dateModified in JSON-LD, and NO visible date anywhere
  * Formatting  — tables, lists, stat-bearing headers
NOT measurable here, and left to the skill's human checklist:
  * whether a section is genuinely self-contained when chunked (principle 2)
  * whether a declarative sentence is TRUE (that is the Verified-Claim Ledger's job)

Per .claude/skills/bsuk-gate-integrity/SKILL.md: the BLUF check is a PROXY on sentence
length and opening words. Confirm a flagged section by reading it before rewriting
anything.

Usage:
  python3 scripts/aeo_audit.py <slug> [<slug> ...]      # `index` = the homepage
  python3 scripts/aeo_audit.py --all
  python3 scripts/aeo_audit.py --all --json             # also write the JSON report

Exit code: 1 when any page has an ERROR-level finding, when the slug filter matched
nothing (0 pages matched is never a pass), or when --fail-on-error is passed and any
WARN was found; 0 otherwise.
"""
import re, sys, glob, json, argparse, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _slugs import dist_path as _dist_path, page_key  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DEFAULT_JSON = ROOT / "docs/reports/aeo_audit.json"

# Spec §7 drops CAG's rule 12: BSUK owns no branded method label, so the list is empty
# and every check that reads it is inert by design (guarded, not deleted, so that the day
# the breeder names a method there is one place to add it).
LABELED_METHODS = []

BINOMIAL = re.compile(r"Canis\s+(?:lupus\s+)?familiaris", re.I)
BREEDER = re.compile(r"Lisa\s+Bright|Bright['’]s", re.I)
PLACE = re.compile(r"Glasgow|Scotland", re.I)
# Claims about registration or health screening are the breeder's to make; this regex only
# measures whether such an entity is NAMED on the page, never that it is true.
CREDENTIAL = re.compile(r"KC[- ]registered|DEFRA|microchipp?ed|vet[- ]checked|BVA|Kennel Club", re.I)
PRONOUNS = re.compile(r"\b(we|our|us)\b", re.I)

# A visible date is BANNED (CLAUDE.md). Bare years in prose are fine — it is the
# "Updated <month> <year>" / "Last updated" stamp that is the defect.
VISIBLE_DATE = re.compile(
    r"(?:last\s+)?updated\s*:?\s*(?:on\s+)?(?:January|February|March|April|May|June|July|"
    r"August|September|October|November|December)\s+\d{4}"
    r"|(?:last\s+)?updated\s*:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
    r"|posted\s+on\s+\w+\s+\d", re.I)

STAT_HEADER = re.compile(r"\b\d[\d,\.]*\s*\+?\s*(?:%|years?|yrs?|word|puppies?|pups?|"
                         r"regions?|cities?|hours?|days?|weeks?|months?|\$)|^\$?\d", re.I)

HEDGE_OPENERS = ("before we", "in this", "there are many", "it is worth", "when it comes",
                 "as you may", "one of the", "over the years", "let us", "let's",
                 "first, ", "to begin", "many people", "if you have ever")


def strip_tags(html):
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", html)


def unescape(t):
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("&middot;", "·"), ("&ndash;", "–"),
                 ("&mdash;", "—"), ("&rsquo;", "’"), ("&#8217;", "’"), ("&quot;", '"')):
        t = t.replace(a, b)
    return t


def text_of(html):
    return re.sub(r"\s+", " ", unescape(strip_tags(html))).strip()


# ── principle 1: BLUF ────────────────────────────────────────────────────────
def bluf_violations(html, max_words=32):
    """H2/H3s whose first following sentence buries the answer. PROXY — verify by reading.

    Flags a wind-up opener (a hedge phrase) or a first sentence over max_words.
    """
    out = []
    parts = re.split(r"<h([23])\b[^>]*>(.*?)</h\1>", html, flags=re.S | re.I)
    # parts = [pre, level, heading, body, level, heading, body, ...]
    for i in range(1, len(parts) - 1, 3):
        heading = text_of(parts[i + 1])
        body = text_of(parts[i + 2]) if i + 2 < len(parts) else ""
        if not body:
            continue
        first = re.split(r"(?<=[.!?])\s", body)[0]
        low = first.lower()
        if len(first.split()) > max_words or low.startswith(HEDGE_OPENERS):
            out.append(heading)
    return out


# ── principle 3: entity-rich ─────────────────────────────────────────────────
def entity_report(html):
    t = text_of(html)
    return {
        "binomial": len(BINOMIAL.findall(t)),
        "breeder": len(BREEDER.findall(t)),
        "place": len(PLACE.findall(t)),
        "credential": len(CREDENTIAL.findall(t)),
    }


def pronoun_heavy(html, ratio=0.02):
    """True when we/our/us outnumber named entities enough to read as anonymous."""
    t = text_of(html)
    words = max(len(t.split()), 1)
    pro = len(PRONOUNS.findall(t))
    named = sum(entity_report(html).values())
    return (pro / words) > ratio and pro > named


# ── principle 6a: labeled concepts ───────────────────────────────────────────
def labeled_methods(html):
    t = text_of(html)
    return [m for m in LABELED_METHODS if m.lower() in t.lower()]


# ── principle 6b: freshness, schema-only ─────────────────────────────────────
def has_freshness(html):
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                        html, re.S):
        if "dateModified" in b:
            return True
    return False


def visible_dates(html):
    return VISIBLE_DATE.findall(text_of(html))


# ── principle 5: strategic formatting ────────────────────────────────────────
def formatting_report(html):
    return {"tables": len(re.findall(r"<table\b", html, re.I)),
            "lists": len(re.findall(r"<(?:ul|ol)\b", html, re.I))}


def stat_headers(html):
    out = []
    for m in re.finditer(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", html, re.S | re.I):
        h = text_of(m.group(1))
        if h and STAT_HEADER.search(h):
            out.append(h)
    return out


# ── principle 4: declarative sentences ───────────────────────────────────────
def sentence_report(html):
    t = text_of(html)
    sents = [s for s in re.split(r"(?<=[.!?])\s", t) if len(s.split()) > 3]
    if not sents:
        return {"count": 0, "avg_words": 0, "over_30": 0}
    lens = [len(s.split()) for s in sents]
    return {"count": len(sents), "avg_words": round(sum(lens) / len(lens), 1),
            "over_30": sum(1 for n in lens if n > 30)}


def audit(slug, html):
    ent = entity_report(html)
    f = []
    if not has_freshness(html):
        f.append(("ERROR", "no dateModified in JSON-LD — page emits no freshness signal"))
    for d in visible_dates(html):
        f.append(("ERROR", f"VISIBLE date on the page (banned): '{d.strip()}'"))
    if ent["binomial"] == 0:
        f.append(("WARN", "no binomial (Canis familiaris) anywhere"))
    if ent["breeder"] == 0:
        f.append(("WARN", "breeder-name entity absent — 'we' instead of 'Lisa Bright'"))
    if LABELED_METHODS and not labeled_methods(html):
        f.append(("WARN", "no brand-owned method name — expertise reads as generic"))
    if pronoun_heavy(html):
        f.append(("WARN", "pronoun-heavy: we/our/us outnumber named entities"))
    bl = bluf_violations(html)
    if bl:
        f.append(("WARN", f"{len(bl)} section(s) bury the answer (PROXY — read them): "
                          + "; ".join(bl[:3]) + ("…" if len(bl) > 3 else "")))
    if not stat_headers(html):
        f.append(("WARN", "no stat-bearing header — nothing for an AI to cite as a figure"))
    return f, ent


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1])
    ap.add_argument("slugs", nargs="*", help="audit these slugs (`index` = the homepage)")
    ap.add_argument("--all", action="store_true", help="audit every built page")
    ap.add_argument("--fail-on-error", action="store_true",
                    help="also exit non-zero when only WARN-level findings were made")
    ap.add_argument("--json", nargs="?", const=str(DEFAULT_JSON), default=None,
                    metavar="PATH",
                    help=f"write the machine-readable result (default {DEFAULT_JSON})")
    ns = ap.parse_args(sys.argv[1:] if argv is None else argv)

    if not ns.slugs and not ns.all:
        ap.error("give one or more slugs, or --all")
    pages = sorted(glob.glob(str(DIST / "**" / "index.html"), recursive=True))
    if ns.slugs:
        # one slug-resolution convention, shared: scripts/_slugs.py
        wanted = {str(_dist_path(s, DIST)) for s in ns.slugs}
        pages = [p for p in pages if p in wanted]
    if not pages:
        print("aeo-audit: 0 pages matched — CHECK YOUR SLUGS, this is not a pass.")
        print("  (zsh does not word-split an unquoted $VAR: pass slugs literally "
              "or use ${=VAR})")
        return 1

    errs = warns = 0
    report = []
    print(f"AEO audit — {len(pages)} pages examined\n")
    for p in pages:
        html = pathlib.Path(p).read_text(encoding="utf-8")
        f, ent = audit(p, html)
        slug = page_key(pathlib.Path(p), DIST)
        e = sum(1 for s, _ in f if s == "ERROR")
        errs += e
        warns += len(f) - e
        fm = formatting_report(html)
        sr = sentence_report(html)
        print(f"── {slug}")
        print(f"   entities: binomial={ent['binomial']} breeder={ent['breeder']} "
              f"place={ent['place']} credential={ent['credential']} · "
              f"tables={fm['tables']} lists={fm['lists']} · "
              f"avg sentence {sr['avg_words']}w, {sr['over_30']} over 30w")
        for sev, msg in f:
            print(f"   [{sev}] {msg}")
        if not f:
            print("   ✅ clean")
        report.append({"slug": slug, "entities": ent, "formatting": fm,
                       "sentences": sr,
                       "findings": [{"severity": s, "message": m} for s, m in f]})

    print(f"\nexamined {len(pages)} pages; {errs} problems ({warns} WARN)")
    if ns.json:
        out = pathlib.Path(ns.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"pages": report, "errors": errs, "warns": warns},
                                  indent=2) + "\n", encoding="utf-8")
        print(f"JSON report → {out}")
    return 1 if errs or (ns.fail_on_error and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
