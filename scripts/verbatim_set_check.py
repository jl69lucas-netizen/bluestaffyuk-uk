#!/usr/bin/env python3
"""verbatim_set_check.py — a faithfully rewritten page carries its migrated page's VERBATIM
SET, and this proves it (working rule 15).

WHY THIS EXISTS, NEXT TO THE TWO GATES THAT ALREADY GUARD A REBUILD.
scripts/migration_parity.py measures SIZE and is switched off for a rebuilt page, whose
heading list is supposed to change. scripts/facts_preserved_check.py measures FACTS — a
price, a puppy name, a health test, a claim sentence — and a page can keep every one of
them while losing every word the old page ranked for: rewrite "L-2-HGA and HC-HSF4 Tested
Staffy Breeders" as "How We Screen The Parents" and no fact moved, but the heading a search
engine matched is gone. Rule 15 says that heading is not the writer's to reword, and this
file is what makes the rule checkable.

THE SET, and why it is these five kinds and not the whole page:
  h1             — the page's one top heading.
  headings       — every H2/H3 CONTAINING A TARGET KEYWORD. Not every heading: a rebuild is
                   supposed to restructure, and freezing "Boosters" or "Hydration" would
                   freeze the outline. A heading carrying the page's keywords is the part of
                   the structure that is doing the ranking, so it is the part that is carried.
  openings       — the first paragraph under each of those headings. The heading is the
                   promise and the first paragraph is the answer; carrying one without the
                   other keeps the label and throws away what it labelled.
  faq_questions  — the questions of the old FAQ blocks, as the reader asked them.
  alts           — every image alt, against its own src.
Everything else on the page is the outline's, written fresh.

TARGET KEYWORDS are derived, not hand-written, so no page can quietly narrow its own set:
the page-map row's TITLE words minus stopwords, plus the site-wide terms every page of this
site competes on (staffy, staffordshire bull terrier, blue staffy, puppies, breeder(s), uk)
and the breeder's city. The list actually used is recorded in the extracted JSON, so a set
can be read back years later without re-deriving anything.

THE EXTRACTION READS THE MIGRATED SOURCE, NOT dist/.
facts_preserved_check.py extracts from the built page and says, correctly, that the
extraction cannot be repeated once the page is rebuilt. This file has no such window: it
reads `src/pages/<slug>/index.astro` AT THE MIGRATION COMMIT (MIGRATED below) and decodes
the `const body` string the WordPress extractor wrote there. That commit is frozen history,
so `--extract` is re-runnable forever and a set can be re-taken if the rules here change —
which is the whole reason it reads git and not the working tree.

CASE. An opening paragraph and an image alt are compared CASE-SENSITIVELY: they are prose,
and their wording is their text. An H1, a keyword heading and an FAQ question are compared
case-INSENSITIVELY, because their case is not the writer's either: rules/headings.md fixes
AP-style Title Case for every H1-H6 on the site and src/lib/headings.ts applies it AT RENDER,
so "Some Common Health Concerns in Blue Staffies include:" reaches the page as
"... Include:". Demanding the old casing back would be demanding a heading the title-case
gate rejects. Rule 15 asks for the WORDING; the casing belongs to rules/headings.md.

A CHANGED ELEMENT is not a missing one. Where the old wording states a wrong fact (the
former city, an old price, the byline) or collides with another page's heading, the record
says so in `verbatim.changed`:
    {"kind": "heading", "old": "...", "new": "...", "reason": "..."}
and the gate then requires the NEW text on the page instead. Two row kinds name a deviation
rather than an element and are folded back to the element they excuse (ROW_KIND_ELEMENT):
`heading-dropped` is a heading the outline removed outright and `faq-merged` is a question the
old page asked twice, answered by the row that carries the other wording. A row whose `new` is
the EMPTY STRING excuses its element and requires nothing on the page — that is what a drop
is — and every other row requires its `new` text there. `verbatim` sits outside the
record hash for the reason `dropped` does (scripts/pageboard.py::record_hash): it is the
accounting of what the rebuild did, and the rebuild happens after approval.

Usage:
  python3 scripts/verbatim_set_check.py --extract <slug>   # -> data/verbatim/<slug>.json
  python3 scripts/verbatim_set_check.py --check            # every applicable rebuilt slug

`--check` judges every slug that is in BOTH data/facts/rebuilt.json (the page has actually
been rebuilt) and data/verbatim/applies.json (rule 15 covers it — the three pages built
before the rule was written do not appear there, and that file says why).

Exit: 0 clean, 1 an element of some set is neither on the page nor declared changed.
"""
import argparse
import html as _html
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _html import text_of, unescape  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: The commit whose tree still holds the migrated pages. Frozen history on purpose: the
#: working tree's copy of a rebuilt page is the REBUILD, and extracting a verbatim set from
#: it would compare a page with itself.
MIGRATED = "63a7b12"

#: Terms this whole site competes on, added to every page's keyword list. Without them a
#: page whose title happens not to repeat "puppies" would not treat its own puppy headings
#: as keyword headings.
SITE_KEYWORDS = ["staffy", "staffordshire bull terrier", "blue staffy", "puppies",
                 "breeder", "breeders", "uk"]

#: Title words that carry no targeting. Kept short: this list only has to stop "the", "and"
#: and their kind from making every heading on the page a keyword heading.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "best", "but", "by", "can", "do", "for",
    "from", "has", "have", "how", "in", "is", "it", "its", "of", "on", "or", "our", "the",
    "their", "this", "to", "what", "when", "where", "which", "who", "why", "will", "with",
    "you", "your",
}

MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)
HEADING = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.S | re.I)
PARA = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S | re.I)
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
ATTR = re.compile(r"""\b(src|alt)\s*=\s*["']([^"']*)["']""", re.I)
SUMMARY = re.compile(r"<summary\b[^>]*>(.*?)</summary>", re.S | re.I)
#: An old-site FAQ question is a `uagb-question` element; a hand-written one may be a
#: <summary> or a "Q:" line. `quiz` is excluded by name: the buying guide's `quiz-question`
#: elements are a self-assessment the reader answers about themselves ("How much time can you
#: realistically dedicate…"), not a question the page answers, and carrying seven of them
#: into data/faq.json would put the reader's homework in the FAQPage schema.
QUESTION_EL = re.compile(
    r"""<(\w+)\b[^>]*\bclass=["'](?![^"']*\bquiz)[^"']*\bquestion\b[^"']*["'][^>]*>(.*?)</\1>""",
    re.S | re.I)
Q_PREFIX = re.compile(r"^Q\s*[:.]\s*(.+)$", re.S)


def norm(s):
    """One spelling of a piece of page text: entities decoded, non-breaking spaces and every
    other run of whitespace collapsed to one space, trimmed.

    `_html.unescape` runs after the shared table so the numeric entities the WordPress export
    is full of (`&#8220;`, `&hellip;`) decode too; the shared table runs first so both gates
    that read a built page agree on the common ones."""
    return re.sub(r"\s+", " ", _html.unescape(unescape(s)).replace("\xa0", " ")).strip()


def text(fragment):
    """The readable text of an HTML fragment, normalised as above."""
    return norm(text_of(fragment))


# ── the migrated body ─────────────────────────────────────────────────────────────────────

BODY_CONST = re.compile(r'^const body = (".*?");?$', re.M | re.S)


def _show(path):
    r = subprocess.run(["git", "show", f"{MIGRATED}:{path}"],
                       cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _md_to_html(md):
    """The blog archive's markdown as the fragment the extractor reads.

    Only the three constructs that page has: an ATX heading, a markdown link (kept as its
    anchor text, which is what a reader sees as the heading) and a paragraph. A real markdown
    renderer here would be a dependency taken on for one stub page."""
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    out = []
    for block in re.split(r"\n\s*\n", md):
        b = block.strip()
        if not b:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", b, re.S)
        if m:
            n = len(m.group(1))
            out.append(f"<h{n}>{m.group(2).strip()}</h{n}>")
        else:
            out.append(f"<p>{b}</p>")
    return "\n".join(out)


def migrated_body(slug):
    """The migrated page's body HTML, from the frozen migration commit.

    Two shapes, because the old site had two. A WordPress page is an .astro file whose
    `const body` holds the exported markup as a JSON string. The blog archive
    (blue-staffy-blog-guides) was never a page: it is a markdown entry in the content
    collection, rendered by the post route, so its body is built from the markdown."""
    page = "src/pages/index.astro" if slug == "index" else f"src/pages/{slug}/index.astro"
    src = _show(page)
    if src is not None:
        m = BODY_CONST.search(src)
        if not m:
            raise SystemExit(f"{slug}: no `const body` in {page} at {MIGRATED}")
        return json.loads(m.group(1).rstrip(";"))
    md = _show(f"src/content/blog/{slug}.md")
    if md is not None:
        return _md_to_html(md)
    raise SystemExit(f"{slug}: no migrated source at {MIGRATED} (tried {page} and the blog)")


# ── target keywords ───────────────────────────────────────────────────────────────────────

def page_title(slug):
    """The page-map row's title for this slug, or "" when the map has no row."""
    url = "/" if slug == "index" else f"/{slug}/"
    pages = json.loads((ROOT / "data/page-map.json").read_text(encoding="utf-8"))["pages"]
    for p in pages:
        if p.get("url") == url:
            return p.get("title", "")
    return ""


def target_keywords(slug, city=None):
    """This page's keyword list: its title's content words, the site-wide terms, the city.

    Returned sorted and de-duplicated so the list recorded in the JSON is stable — a set that
    re-extracts to a different key order is a set nobody can diff."""
    if city is None:
        city = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8")
                          )["address"]["city"]
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]+", norm(page_title(slug)).lower())
             if w not in STOPWORDS and len(w) > 2]
    return sorted(set(words) | {k.lower() for k in SITE_KEYWORDS} | {city.lower()})


def is_keyword_heading(heading_text, keywords):
    return any(k in heading_text.lower() for k in keywords)


# ── extraction ────────────────────────────────────────────────────────────────────────────

def _blocks(body):
    """(kind, text, raw) for every heading and paragraph of the body, in document order.

    One pass over both so "the first paragraph under this heading" is a question about
    position, which is what it is."""
    found = []
    for m in HEADING.finditer(body):
        found.append((m.start(), "h", int(m.group(1)), text(m.group(2))))
    for m in PARA.finditer(body):
        found.append((m.start(), "p", 0, text(m.group(1))))
    found.sort(key=lambda t: t[0])
    return found


def alts(body):
    """[{src, alt}] for every image of the body, first spelling of each src kept.

    An `<img>` with no alt is still recorded, with the empty string: a decorative image's
    empty alt is a decision the rebuild has to carry too, and dropping the row would let a
    page give it a sentence nobody wrote."""
    out, seen = [], set()
    for tag in IMG_TAG.findall(body):
        a = {k.lower(): v for k, v in ATTR.findall(tag)}
        src = a.get("src", "").strip()
        if not src or src in seen:
            continue
        seen.add(src)
        out.append({"src": src, "alt": norm(a.get("alt", ""))})
    return out


def faq_questions(body):
    """The questions of the old FAQ blocks, in document order, de-duplicated.

    Four spellings, because the old site used more than one: a `class="…question…"` element
    (the UAGB FAQ block), a `<summary>`, and a "Q:"-prefixed paragraph. A question that is
    ALSO a heading is left to the heading kinds — carrying it twice would count one element
    as two and report one miss as two."""
    out = []
    for pattern, group in ((QUESTION_EL, 2), (SUMMARY, 1)):
        for m in pattern.finditer(body):
            q = text(m.group(group))
            if q and q not in out:
                out.append(q)
    for m in PARA.finditer(body):
        q = Q_PREFIX.match(text(m.group(1)))
        if q and q.group(1).strip() not in out:
            out.append(q.group(1).strip())
    return out


def extract(body, keywords):
    """The verbatim set of one migrated body."""
    blocks = _blocks(body)
    h1 = next((t for _, kind, lvl, t in blocks if kind == "h" and lvl == 1 and t), "")
    headings, openings = [], []
    for i, (_, kind, lvl, t) in enumerate(blocks):
        if kind != "h" or lvl not in (2, 3) or not t:
            continue
        if not is_keyword_heading(t, keywords):
            continue
        if any(h["text"] == t and h["level"] == lvl for h in headings):
            continue
        headings.append({"level": lvl, "text": t})
        # The walk stops at the NEXT heading rather than taking the next paragraph anywhere
        # below, so a heading with no prose of its own reports no opening instead of
        # borrowing the following section's first paragraph.
        opening = None
        for _, bk, _, bt in blocks[i + 1:]:
            if bk == "h":
                break
            if bt:
                opening = bt
                break
        if opening:
            openings.append({"heading": t, "text": opening})
    qs = [q for q in faq_questions(body)
          if not any(h["text"].lower() == q.lower() for h in headings) and q.lower() != h1.lower()]
    return {
        "keywords": keywords,
        "h1": h1,
        "headings": headings,
        "openings": openings,
        "faq_questions": qs,
        "alts": alts(body),
    }


# ── the built page ────────────────────────────────────────────────────────────────────────

def page_main(html):
    """`<main>`, or the whole document when a page has none. The scope matters for the same
    reason it does in facts_preserved_check.py: measured against the document, a heading in
    the footer and an alt in the header both count as carried."""
    m = MAIN.search(html)
    return m.group(1) if m else html


class Page:
    """The one parse of a built page every element of a set is judged against."""

    def __init__(self, html):
        body = page_main(html)
        self.headings = [text(m.group(2)) for m in HEADING.finditer(body)]
        self.h1s = [text(m.group(2)) for m in HEADING.finditer(body) if m.group(1) == "1"]
        self.paras = [text(m.group(1)) for m in PARA.finditer(body)]
        # EVERY alt a src is rendered with, not the first one. A page may legitimately render
        # one file twice — the listing page's hero mosaic reuses two of its own section
        # photographs as tiles — and `img-alt-present-and-unique` (tests/render/checks/img.ts)
        # then REQUIRES the two renderings to carry DIFFERENT wording, so the pair is a rule
        # rather than a defect. With `setdefault` the first rendering won and rule 15 read the
        # other one as missing: the page carried the migrated alt on the migrated src and the
        # gate said it did not. Rule 15 asks for the old wording to be on the page against its
        # own src (spec §9 amendment 8), which is a membership question, not an ordering one.
        self.alts = {}
        for tag in IMG_TAG.findall(body):
            a = {k.lower(): v for k, v in ATTR.findall(tag)}
            if a.get("src"):
                self.alts.setdefault(a["src"].strip(), set()).add(norm(a.get("alt", "")))
        self.questions = self.headings + [text(m.group(1)) for m in SUMMARY.finditer(body)] \
            + [text(m.group(2)) for m in QUESTION_EL.finditer(body)]

    def has_heading(self, t):
        return any(h.lower() == t.lower() for h in self.headings)

    def has_h1(self, t):
        return any(h.lower() == t.lower() for h in self.h1s)

    def has_paragraph(self, t):
        """Case-SENSITIVE, and containment rather than equality: a rebuilt section may open
        with the old paragraph and carry on in the writer's own words, which is exactly what
        rule 15 asks for — the old wording present, fresh prose after it."""
        return any(t in p for p in self.paras)

    def has_question(self, t):
        return any(q.lower() == t.lower() for q in self.questions)

    def has_alt(self, src, alt):
        """True when SOME rendering of `src` carries this alt. See `__init__`: one file may be
        rendered twice and the two alts must differ, so "the page's alt for this src" is a set
        and not a single value."""
        return alt in self.alts.get(src, ())


# ── the check ─────────────────────────────────────────────────────────────────────────────

#: kind -> (how the element's OLD text is read, how a text is looked for on the page).
#: One table, so the `changed` path and the carried path cannot drift: an element's `new`
#: text is proved present by the same predicate that failed on its `old` text.
def _present(page, kind, elem):
    if kind == "h1":
        return page.has_h1(elem)
    if kind == "heading":
        return page.has_heading(elem)
    if kind == "opening":
        return page.has_paragraph(elem)
    if kind == "faq":
        return page.has_question(elem)
    raise ValueError(kind)


def elements(vset):
    """(kind, old_text, extra) for every element of a set, in a fixed order.

    `extra` is the image src for an alt and None otherwise — an alt is the one element whose
    identity is not its own text (two images may share the empty alt)."""
    out = []
    if vset.get("h1"):
        out.append(("h1", vset["h1"], None))
    out += [("heading", h["text"], None) for h in vset.get("headings", [])]
    out += [("opening", o["text"], None) for o in vset.get("openings", [])]
    out += [("faq", q, None) for q in vset.get("faq_questions", [])]
    out += [("alt", a["alt"], a["src"]) for a in vset.get("alts", [])]
    return out


#: A row's `kind` says what KIND OF DEVIATION it is; the element it excuses is one of the five
#: kinds elements() yields. Two row kinds are not element kinds and have to be folded back, or
#: the row would key on a pair no element produces and the gate would quietly go on demanding
#: the old wording it was written to excuse — the loudest possible way for an accounting file
#: to do nothing. `heading-dropped` is a heading; `faq-merged` is an FAQ question.
ROW_KIND_ELEMENT = {"heading-dropped": "heading", "faq-merged": "faq"}


def changed_rows(record):
    """The record's `verbatim.changed` rows, keyed (kind, old) — the pair that identifies the
    element the row excuses. A row naming a `src` keys on that instead of the old alt, since
    an alt row is about an image."""
    rows = {}
    for r in (record.get("verbatim") or {}).get("changed", []):
        if not isinstance(r, dict):
            continue
        kind = ROW_KIND_ELEMENT.get(r.get("kind"), r.get("kind"))
        key = (kind, r.get("src") or r.get("old"))
        rows[key] = r
    return rows


def judge(vset, html, record):
    """(examined, changed, [misses]) for one page. A miss is a printable line."""
    page = Page(html)
    rows = changed_rows(record or {})
    examined = changed = 0
    misses = []
    for kind, old, src in elements(vset):
        examined += 1
        row = rows.get((kind, src if kind == "alt" else old))
        if row is not None:
            changed += 1
            new = row.get("new", "")
            if not new:
                # An EMPTY `new` is the record saying the element is gone and nothing stands in
                # for it: a keyword heading the outline removed outright (`heading-dropped`) and
                # the opening paragraph that went with it. Demanding the empty string on the page
                # would pass for any page at all, so the row is counted and nothing is looked up.
                continue
            ok = page.has_alt(src, new) if kind == "alt" else _present(page, kind, new)
            if not ok:
                misses.append(f"changed {kind} not on the page: {new!r} "
                              f"(replacing {old!r})")
            continue
        ok = page.has_alt(src, old) if kind == "alt" else _present(page, kind, old)
        if not ok:
            where = f" on {src}" if kind == "alt" else ""
            misses.append(f"missing {kind}{where}: {old!r}")
    return examined, changed, misses


# ── plumbing ──────────────────────────────────────────────────────────────────────────────

def applicable_slugs():
    """The slugs `--check` judges: rebuilt AND covered by rule 15.

    The intersection and not either list alone. data/facts/rebuilt.json answers "has this
    page been rewritten yet"; data/verbatim/applies.json answers "does rule 15 reach it" —
    the three pages built before the rule was written are not in it. Reading only the first
    would demand a verbatim set from privacy-policy-uk that was never taken; reading only the
    second would demand one from a page that is still the migrated page."""
    rebuilt = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))
    path = ROOT / "data/verbatim/applies.json"
    applies = json.loads(path.read_text(encoding="utf-8"))["slugs"] if path.exists() else []
    return [s for s in rebuilt if s in applies]


def dist_html(slug):
    return ROOT / "dist" / ("" if slug == "index" else slug) / "index.html"


def load_record(slug):
    p = ROOT / f"data/boards/{slug}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def do_extract(slug):
    vset = extract(migrated_body(slug), target_keywords(slug))
    out = ROOT / "data/verbatim"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{slug}.json").write_text(
        json.dumps(vset, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"extracted verbatim set for {slug}: "
          f"h1 {'1' if vset['h1'] else '0'}, {len(vset['headings'])} headings, "
          f"{len(vset['openings'])} openings, {len(vset['faq_questions'])} faq questions, "
          f"{len(vset['alts'])} alts")
    return 0


def do_check():
    slugs = applicable_slugs()
    problems = 0
    for slug in slugs:
        vset = json.loads((ROOT / f"data/verbatim/{slug}.json").read_text(encoding="utf-8"))
        html = dist_html(slug).read_text(encoding="utf-8")
        examined, changed, misses = judge(vset, html, load_record(slug))
        for m in misses:
            print(f"{slug}: {m}")
        print(f"{slug}: examined {examined} elements; {changed} changed; {len(misses)} missing")
        problems += len(misses)
    if not slugs:
        print("examined 0 elements; 0 changed; 0 missing (no rebuilt page is under rule 15 yet)")
    print(f"examined {len(slugs)} applicable pages; {problems} problems")
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--extract", metavar="SLUG",
                    help="extract the verbatim set from the migrated page into "
                         "data/verbatim/<slug>.json")
    ap.add_argument("--check", action="store_true",
                    help="check every slug in both rebuilt.json and verbatim/applies.json")
    a = ap.parse_args(argv)
    if a.extract:
        return do_extract(a.extract)
    return do_check()


if __name__ == "__main__":
    sys.exit(main())
