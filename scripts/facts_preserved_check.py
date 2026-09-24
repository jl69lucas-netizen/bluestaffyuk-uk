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
the built page after it — dist/<slug>/index.html, or for a city page (a bare slug whose
data/page-map.json route is uk-locations/<slug>) dist/uk-locations/<slug>/index.html; the
fact set, the board record and the rebuilt.json entry keep the bare slug (scripts/_slugs.py).
The extraction cannot be repeated once the page is rebuilt:
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
  embeds  — the YouTube id, in the markup, in any of the five spellings EMBED knows:
            `/embed/<id>`, `youtu.be/<id>`, `watch?v=<id>`, a `<lite-youtube videoid>` and
            a `data-video-id` attribute. The CHECK side still looks for the bare id in the
            rebuilt markup, so a page that re-spells one of them still passes.

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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _slugs import built_page, resolve_page  # noqa: E402  (one route convention, shared)

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

# ── CLAIM SENTENCES (the `text` kind, spec §9 amendment 4 / 2026-09-20 review) ────────────
#
# The other six kinds are TOKENS: a price, a name, a test, an image path. A migrated page
# also makes CLAIMS — "we respond to all inquiries within 24-48 business hours", "regular
# staff training" — and a rebuild that simply does not rewrite one drops it with nothing
# reporting the loss, because no token went missing. This kind closes that hole.
#
# A claim sentence is one carrying at least one TRIGGER: a number, a named organisation, or a
# named process. Those three are what makes a sentence checkable — a sentence with none of
# them is voice, and voice is exactly what a rebuild is supposed to replace.
CLAIM_ORGS = ["Kennel Club", "DEFRA", "Google", "ICO", "Information Commissioner",
              "Citizens Advice", "GOV.UK", "Formspree", "BVA", "RSPCA"]
CLAIM_PROCESSES = ["training", "review", "audit", "screening", "vaccinat", "microchip",
                   "health test", "inspection", "assessment", "socialis"]
CLAIM_NUMBER = re.compile(r"\b\d")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
# Words that carry no evidence. A six-word overlap made of "the of and to a is" would match
# any two sentences in English, which is the failure mode this list exists to prevent.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can", "do", "for",
    "from", "has", "have", "how", "i", "if", "in", "is", "it", "its", "me", "my", "no",
    "not", "of", "on", "or", "our", "out", "so", "that", "the", "their", "them", "then",
    "there", "they", "this", "to", "up", "us", "was", "we", "what", "when", "which", "who",
    "will", "with", "you", "your",
}
# Collected at four content words, judged at six. A short sentence can still be a claim
# ("We provide regular staff training."), and refusing to collect it would let the shortest,
# most quotable promises leave a page unreported; but judging a four-word claim on a
# six-word overlap is impossible, so the overlap is capped at the claim's own length.
MIN_CLAIM_WORDS = 4
CLAIM_OVERLAP = 6


def _tokens(s):
    return re.findall(r"[a-z0-9£'-]+", s.lower())


def _content(s):
    """The evidence-bearing words of a sentence, in order, without duplicates."""
    out = []
    for w in _tokens(s):
        if w not in STOPWORDS and len(w) > 1 and w not in out:
            out.append(w)
    return out


def _triggers(sentence):
    """What made this sentence a claim: the numbers, organisations and processes in it."""
    return _hard_triggers(sentence) + [pr for pr in CLAIM_PROCESSES if _stem(pr, sentence)]


def _hard_triggers(sentence):
    """The triggers a rebuild may NOT paraphrase away: every number and every named
    organisation.

    A PROCESS word is deliberately not here. "review and respond within 24-48 business
    hours" is honestly rewritten as "read and answered within 24-48 business hours", and a
    gate that demanded the word `review` would be demanding the old sentence back — which is
    the one thing working rule 8 forbids. A NUMBER or an ORGANISATION is different in kind:
    there is no paraphrase of 24-48, and a page that stopped naming The Kennel Club stopped
    making the claim. So processes qualify a sentence as a claim and then count toward the
    overlap like any other content word, while numbers and names have to be there."""
    found = re.findall(r"\b\d[\d,.:-]*", sentence) if CLAIM_NUMBER.search(sentence) else []
    return found + [o for o in CLAIM_ORGS if _stem(o, sentence)]


def claims(text):
    """Every claim sentence of a page body, collapsed to one line each.

    Deliberately the SENTENCE and not a summary of it: the entry a record writes under
    `dropped.text` has to be findable in the migrated body by somebody reading the record,
    and a paraphrase is not findable."""
    out = []
    for raw in SENTENCE_SPLIT.split(re.sub(r"\s+", " ", text)):
        s = raw.strip()
        if len(_content(s)) < MIN_CLAIM_WORDS or not _triggers(s):
            continue
        if s not in out:
            out.append(s)
    return out


def claim_present(claim, page_text):
    """True when the rebuilt page still makes this claim.

    TWO conditions, because either alone is wrong. Every HARD trigger must appear — a page that
    dropped "24-48" has dropped the reply window whatever else it kept. And at least six of
    the claim's content words must appear (or all of them, for a claim shorter than that),
    so a shared "Kennel Club" between two unrelated sentences is not read as the claim
    surviving."""
    for trig in _hard_triggers(claim):
        if not _stem(trig, page_text):
            return False
    words = _content(claim)
    hits = sum(1 for w in words if _stem(w, page_text))
    return hits >= min(CLAIM_OVERLAP, len(words))


MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)
# Either quote style: the build emits double quotes, but a fact set is also read against
# hand-written HTML in the tests, and an extractor that silently finds no images in half the
# HTML it is given is a gate that passes by finding nothing.
IMG = re.compile(r"""<img[^>]+src=["']([^"']+)["']""")
# FIVE SPELLINGS OF ONE FACT. The original pattern read `…/embed/<id>` only, which is the
# form a WordPress oEmbed happens to produce and the form this kit's VideoEmbed emits — so
# it found every video on the pages that were extracted first and would have found none on a
# page whose author had pasted a share link, a watch url or a lite-player element. A video id
# silently absent from a fact set is a video that can leave the site with nothing reporting
# it, which is the one failure this file exists to prevent. Each alternative captures the id
# in its own group; `ids()` below collects whichever one matched.
#
# `youtu.be/<id>` and `watch?v=<id>` are bounded by a lookahead rather than by the end of the
# match, so `youtu.be/abcdefghijk?t=30` is the same fact as `youtu.be/abcdefghijk`.
EMBED = re.compile(
    r"youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{6,})"
    r"|youtu\.be/([A-Za-z0-9_-]{6,})(?![A-Za-z0-9_-])"
    r"|youtube\.com/watch\?(?:[^\s\"'<>]*&(?:amp;)?)?v=([A-Za-z0-9_-]{6,})(?![A-Za-z0-9_-])"
    r"|<lite-youtube[^>]*\bvideoid=[\"']([A-Za-z0-9_-]{6,})"
    r"|\bdata-video-id=[\"']([A-Za-z0-9_-]{6,})"
)


def embed_ids(html):
    """Every distinct YouTube id in the markup, however it is spelled."""
    return sorted({g for match in EMBED.findall(html) for g in match if g})
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
        "embeds": embed_ids(html),
        "text": claims(text),
    }


def page_body(html):
    """The rebuilt page's own content: `<main>`, or the whole document when there is none.

    The scope matters as much here as it does on the extraction side. Measured against the
    whole document, a price in the footer, a name in the nav and an image in the header all
    count as "still there", and a page could lose its entire body and pass."""
    found = MAIN.search(html)
    return found.group(1) if found else html


# A `dropped` entry is "<the fact> — <the reason it is not carried>". The reason is the whole
# point of the field: a bare list of paths records that something went, not that anyone
# agreed it should. So the fact is read off the FRONT of the line, up to the dash, and an
# entry with no dash is taken whole — which is what the older records wrote.
#
# EM AND EN DASH ONLY. A spaced HYPHEN was in this class and should never have been: the
# facts it separates are slugs, paths, prices and health tests, and every one of those can
# contain a hyphen — `L-2-HGA`, `/uk-locations/blue-staffy-puppies-uk/`, `24-48`. A line
# whose fact happened to be followed by " - " split in the wrong place and the gate then
# looked for half a fact. The records all use the em dash, which is also what the schema's
# own description spells (2026-09-20 review).
_DROP_SPLIT = re.compile(r"\s+[—–]\s+")


def _claim_key(s):
    """A claim sentence reduced to what a record can be expected to reproduce.

    THE SPACE BEFORE THE COMMA IS THE WORDPRESS EXTRACTOR'S, NOT THE RECORD'S. The old body
    wrapped emphasised runs in their own tags, so `extract()` reads the sentence back as
    "…(BVA) , Staffordshire Bull Terriers …" and "…£1,200 , covering…" — a stray space in
    front of the punctuation, several times in one sentence. A `dropped.text` line quotes the
    claim the way a person reads it, and demanding that the record transcribe the artifact
    made two claims this record DOES strike, with reasons, report as unaccounted for
    (2026-09-21, the why-us page). Comparing the two with the space removed keeps the match
    exact about every word and forgiving only about a typographic accident nobody typed.
    Casefolded here too, so the caller does not do it twice.
    """
    return re.sub(r"\s+([,.;:!?])", r"\1", re.sub(r"\s+", " ", s)).strip().lower()


#: The shortest `dropped.text` line that may EXCUSE a claim by containment. The match runs in
#: both directions so a record can quote the PHRASE that carries a claim rather than transcribe
#: a forty-word sentence — but a short enough phrase stops identifying anything. "Community
#: support" is eighteen characters and would excuse every claim sentence with those two words
#: in it; a bare "KC" would excuse most of the page. Twelve characters is the floor: long
#: enough that the phrase names a claim, short enough that no honest quotation is refused (the
#: shortest on any record today is "8-12-week-old", fourteen). A line below it is still matched
#: EXACTLY, by `v in drop`, so nothing that used to pass on an exact line stops passing.
MIN_DROP_PHRASE = 12


def drop_facts(entries):
    """The fact each `dropped` line names, with its reason stripped off."""
    out = set()
    for e in entries or []:
        if not isinstance(e, str):
            continue
        e = e.strip()
        out.add(e)
        out.add(_DROP_SPLIT.split(e, 1)[0].strip())
    return out


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
        drop = drop_facts(dropped.get(k, []))
        # The AMOUNTS inside the dropped lines, not the lines themselves. A `dropped`
        # entry is prose ("the form card's delivery notice — 'Delivery begins 24-48 hours
        # …'"), and the fact it names is not always the bit before the em dash: the contact
        # record's price entry is a whole paragraph, and handing that to `pence()` raised
        # ValueError on the "…" it contains rather than reporting anything (found 2026-09-20,
        # project 4 Task 9). Reading every £ amount out of the line keeps the intent — a
        # price this record says it dropped is not missing — and cannot be fed a non-price.
        dropped_pence = ({pence(m) for line in drop for m in PRICE.findall(line)}
                         if k == "prices" else set())
        miss = []
        for v in vals:
            if v in drop or (k == "prices" and pence(v) in dropped_pence):
                continue
            # A `dropped.text` line quotes the claim, and a record is allowed to quote the
            # PHRASE that carries it ("regular staff training") rather than transcribe a
            # forty-word sentence. Either containment counts, in either direction, so the
            # record stays readable and the match stays exact enough to be wrong loudly.
            # Both sides go through `_claim_key` first — see its docstring — and a line
            # shorter than `MIN_DROP_PHRASE` may not excuse a claim by CONTAINMENT, because a
            # two-word phrase stops naming one claim and starts matching several.
            if k == "text":
                nv = _claim_key(v)
                if any(len(nd := _claim_key(d)) >= MIN_DROP_PHRASE and (nd in nv or nv in nd)
                       for d in drop):
                    continue
            if k in ("images", "embeds"):
                present = v in body
            elif k == "prices":
                present = pence(v) in here
            elif k == "names":
                present = _word(v, text)
            elif k == "text":
                present = claim_present(v, text)
            else:
                present = _stem(v, text)
            if not present:
                miss.append(v)
        if miss:
            out[k] = miss
    return out


def dist_html(slug):
    """The built page: dist/index.html for `index`, else dist/<route>/index.html, where a
    bare slug in data/page-map.json takes its mapped route — a city page's
    `blue-staffy-puppies-for-sale-leeds` is dist/uk-locations/blue-staffy-puppies-for-sale-leeds/."""
    return built_page(slug, ROOT)


def fact_file(slug):
    """data/facts/<key>.json — the bare slug for a page-map row, the slug as given otherwise."""
    return ROOT / "data" / "facts" / f"{resolve_page(slug, ROOT)[0]}.json"


def record_file(slug):
    """data/boards/<key>.json, keyed the same way as fact_file."""
    return ROOT / "data" / "boards" / f"{resolve_page(slug, ROOT)[0]}.json"


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
        out = fact_file(slug)
        out.parent.mkdir(parents=True, exist_ok=True)   # data/facts/, and any nested key's folder
        out.write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"extracted facts for {resolve_page(slug, ROOT)[0]}: "
              + ", ".join(f"{len(v)} {k}" for k, v in facts.items()))
        return 0

    rebuilt = rebuilt_slugs()
    problems = 0
    for slug in rebuilt:
        facts = json.loads(fact_file(slug).read_text(encoding="utf-8"))
        record = record_file(slug)
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
