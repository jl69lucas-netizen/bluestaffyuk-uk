#!/usr/bin/env python3
"""Query coverage gate over dist/ (spec 2026-09-23 §10).

For every data/queries/<slug>.json whose route is built in dist/, the page must carry:
  1. FAQ blocks (div.kit-faq), where a question is a <details> that is a direct child of a
     block and each one's question is an H3. On location pages there are exactly three, named
     by position in the document — the 1st is top, the 2nd middle, the 3rd bottom — holding
     5–7, 5–7 and 7–10 questions, 15–20 in total. Comparison, blog and puppy pages may put
     their questions in one block or several, and their FAQ total is not range-checked;
  2. every must-answer question at its covered_by text, with an answer under it. A question
     covered in the FAQ ("where": "faq") is looked up among FAQ H3s only (on a location
     page it must sit in the block its "faq" field names), and its answer is the text inside its own <details> after
     the summary — nothing past that </details> counts. A question covered by a heading is
     looked up among headings inside <main>; its answer runs to the next heading;
  3. FAQPage schema naming exactly the visible FAQ questions, compared as multisets, so a
     duplicated question is reported;
  4. every extra section's recorded heading as an H2 inside <main>;
  5. on location pages, at least section_target.total body sections with an H2 (the
     competitors' count + 3, never below the floor of 9). A body
     section is a <section data-section-label> inside <main>, not nested in another labelled
     section, that holds an H2, is not #top, #key-takeaways or #newsletter and holds no frame
     part: no kit hero, counter, trust strip, page nav, review, FAQ block and no form
     (docs/reference/location-page-template.md, "The fixed frame" — frame is never counted).
     Competitors' sections are counted by H2, so ours are too.

Text inside <script>, <style> and <template> is never page text. A question file is checked
only when its page is built AND the page is listed in data/facts/rebuilt.json (the list
facts_preserved_check.py and final_page_audit.py read). The convention there is the bare slug,
the route's last segment ("/uk-locations/<slug>/" -> "<slug>", "/" -> "index"), which is how
migration_parity.py and facts_preserved_check.py key a page; the full route key
("uk-locations/<slug>"), resolved with scripts/_slugs.py's dist_path/page_key, is accepted
too. A file
whose route is not built is skipped and counted as not built (an unbuilt page ships nothing)
— unless the page is listed in data/facts/rebuilt.json, which is a problem: a rebuilt page
the gate cannot find would otherwise pass unseen. One whose page is built but not yet
rebuilt — the old site's page is still in dist/ — is skipped, counted and named on an
"awaiting rebuild:" line. A question file that is not valid JSON, or not valid against
schemas/queries.schema.json, is a problem, and so is a data/facts/rebuilt.json that is not a
JSON list of slugs. Exit 1 on any problem, 0 otherwise — and exit 1 with "not a pass" when it
examines no page while an approved new-family board (family_rules.applies) exists.

  python3 scripts/query_coverage_check.py
"""
import argparse
import json
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _slugs import dist_path, page_key  # noqa: E402  (one slug convention, shared)
from query_augment import BLOCKS, FAQ_MAX, FAQ_MIN, FAQ_TOTAL_MAX, normalise  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FAQ_TOTAL_MIN = 15
FRAME_IDS = {"top", "key-takeaways", "newsletter"}
# The kit components that make up the fixed frame. A section holding one is frame, not body.
FRAME_CLASSES = {"kit-hero", "kit-counter", "kit-trust", "kit-nav", "kit-quote", "kit-faq"}
HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
RAW = {"script", "style", "template"}   # their text is never page text
# The spend guard's two ledgers (scripts/query_augment.py) and the shared thread ledger
# (scripts/thread_ledger.py) share data/queries/ with the question files; none is one.
LEDGERS = {"spend.json", "dashboard.json", "thread-ledger.json"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # {"tag", "sec", "faq", "classes"}
        self.sections = []       # {"id", "frame", "nested", "main", "h2"}
        self.faq_blocks = []     # {"h3": [text], "details": n}
        self.headings = []       # {"level", "text", "answer", "faq", "main"}
        self.ld = []
        self._heading = None     # [level, [text], faq_index, main]
        self._answer = None      # the heading whose answer text is being collected
        self._answer_end = None  # the stack entry (a <details>) that ends an FAQ answer
        self._ld = None

    def _open(self, key):
        return [e[key] for e in self.stack if e[key] is not None]

    def _in(self, tags):
        return any(e["tag"] in tags for e in self.stack)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in VOID:
            return
        classes = set((a.get("class") or "").split())
        entry = {"tag": tag, "sec": None, "faq": None}
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = []
        if not self._in(RAW) and tag not in RAW:
            in_main = self._in({"main"})
            if tag == "section" and "data-section-label" in a:
                self.sections.append({"id": a.get("id") or "", "frame": False,
                                      "nested": bool(self._open("sec")), "main": in_main,
                                      "h2": False})
                entry["sec"] = len(self.sections) - 1
            if tag == "form" or classes & FRAME_CLASSES:
                for i in self._open("sec") + ([entry["sec"]] if entry["sec"] is not None else []):
                    self.sections[i]["frame"] = True
            if tag == "details" and self.stack and self.stack[-1]["faq"] is not None \
                    and self.stack[-1]["tag"] == "div":
                self.faq_blocks[self.stack[-1]["faq"]]["details"] += 1
            if tag == "div" and "kit-faq" in classes:
                self.faq_blocks.append({"h3": [], "details": 0})
                entry["faq"] = len(self.faq_blocks) - 1
            if tag in HEADINGS:
                inside = self._open("faq")
                faq = inside[-1] if inside and tag == "h3" else None
                self._heading = [int(tag[1]), [], faq, in_main]
                if tag == "h2":
                    for i in self._open("sec"):
                        self.sections[i]["h2"] = True
        self.stack.append(entry)

    def handle_endtag(self, tag):
        if tag in HEADINGS and self._heading:
            level, parts, faq, in_main = self._heading
            text = " ".join("".join(parts).split())
            h = {"level": level, "text": text, "answer": "", "faq": faq, "main": in_main}
            self.headings.append(h)
            self._answer, self._answer_end = h, None
            if faq is not None:
                self.faq_blocks[faq]["h3"].append(text)
                details = [e for e in self.stack if e["tag"] == "details"]
                self._answer_end = details[-1] if details else None
            self._heading = None
        if tag == "script" and self._ld is not None:
            self.ld.append("".join(self._ld))
            self._ld = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                if self._answer_end is not None and any(e is self._answer_end for e in self.stack[i:]):
                    self._answer = self._answer_end = None
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._ld is not None:
            self._ld.append(data)
        elif self._in(RAW):
            return
        elif self._heading is not None:
            self._heading[1].append(data)
        elif self._answer is not None and not self._in({"summary"}):
            self._answer["answer"] += data


def faq_schema_names(blobs):
    names = []

    def walk(node):
        if isinstance(node, list):
            for x in node:
                walk(x)
        elif isinstance(node, dict):
            t = node.get("@type")
            if t == "FAQPage" or (isinstance(t, list) and "FAQPage" in t):
                entities = node.get("mainEntity", [])
                for q in entities if isinstance(entities, list) else [entities]:
                    if isinstance(q, dict) and q.get("name"):
                        names.append(q["name"])
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)

    for b in blobs:
        try:
            walk(json.loads(b))
        except ValueError:
            continue
    return names


def check_page(q, html):
    p = Page()
    p.feed(html)
    p.close()
    problems = []
    blocks = p.faq_blocks
    location = q["page_type"] == "location"
    three = location and len(blocks) == 3
    block_name = {i: BLOCKS[i] if three else f"block {i + 1}" for i in range(len(blocks))}
    for i, b in enumerate(blocks):
        if b["details"] != len(b["h3"]):
            problems.append(f"FAQ {block_name[i]}: {b['details']} questions but {len(b['h3'])} H3s — "
                            "every question must be an H3")
    if location:
        if len(blocks) != 3:
            problems.append(f"FAQ blocks: {len(blocks)}, want 3 (top, middle, bottom)")
        else:
            for name, b in zip(BLOCKS, blocks):
                n = len(b["h3"])
                if not FAQ_MIN[name] <= n <= FAQ_MAX[name]:
                    problems.append(f"FAQ {name}: {n} questions, want {FAQ_MIN[name]}–{FAQ_MAX[name]}")
        total = sum(len(b["h3"]) for b in blocks)
        if not FAQ_TOTAL_MIN <= total <= FAQ_TOTAL_MAX:
            problems.append(f"FAQ total: {total}, want {FAQ_TOTAL_MIN}–{FAQ_TOTAL_MAX}")
    faq_heads, main_heads = {}, {}
    for h in p.headings:
        if h["faq"] is not None:
            faq_heads.setdefault(normalise(h["text"]), h)
        if h["main"]:
            main_heads.setdefault(normalise(h["text"]), h)
    for item in q["questions"]:
        if not item["must_answer"]:
            continue
        cov = item.get("covered_by")
        if not cov:
            problems.append(f"{item['id']}: must-answer question has no covered_by")
            continue
        in_faq = cov["where"] == "faq"
        h = (faq_heads if in_faq else main_heads).get(normalise(cov["text"]))
        if h is None:
            where = "an FAQ H3" if in_faq else "a heading in <main>"
            problems.append(f"{item['id']}: '{cov['text']}' not found as {where}")
            continue
        if three and in_faq and item.get("faq") and block_name[h["faq"]] != item["faq"]:
            problems.append(f"{item['id']}: '{cov['text']}' is in the {block_name[h['faq']]} "
                            f"FAQ block, want {item['faq']}")
        if not h["answer"].strip():
            problems.append(f"{item['id']}: '{cov['text']}' has no answer under it")
    visible = Counter(normalise(t) for b in blocks for t in b["h3"])
    schema = Counter(normalise(n) for n in faq_schema_names(p.ld))
    if schema != visible:
        dupes = sorted(k for k, n in (visible + schema).items() if visible[k] > 1 or schema[k] > 1)
        problems.append(f"FAQPage schema: {sum((visible - schema).values())} visible questions "
                        f"missing, {sum((schema - visible).values())} not visible"
                        + (f"; duplicate: {', '.join(dupes)}" if dupes else ""))
    h2s = {normalise(h["text"]) for h in p.headings if h["level"] == 2 and h["main"]}
    for e in q.get("extra_sections", []):
        if not e.get("heading"):
            problems.append(f"extra section '{e['topic']}': no heading recorded")
        elif normalise(e["heading"]) not in h2s:
            problems.append(f"extra section '{e['topic']}': '{e['heading']}' is not an H2 on the page")
    if location:
        body = [s for s in p.sections if s["main"] and not s["nested"] and s["h2"]
                and s["id"] not in FRAME_IDS and not s["frame"]]
        t = q["section_target"]
        if len(body) < t["total"]:
            problems.append(f"body sections with an H2: {len(body)}, want at least {t['total']} "
                            f"(competitors {t['matched']} + {t['extra']}, floor {t['floor']})")
    return problems


def page_key_for(route, dist=Path("dist")):
    """The data/facts/rebuilt.json key for a route, via the shared _slugs convention."""
    return page_key(dist_path(route.strip("/") or "index", dist), dist)


def route_slug(route):
    """A route's last segment — the bare slug the other gates key a page by."""
    return route.strip("/").rsplit("/", 1)[-1] or "index"


def approved_new_family(root):
    """Slugs of the approved project 5 boards in data/boards/ (family_rules.applies, status
    approved or later). While there are none, examining 0 pages is the expected result."""
    import family_rules as FR      # imported here: only the zero-examined branch needs it
    import page_sections as PS
    ok = PS.statuses_from("approved")
    out = []
    for f in sorted((Path(root) / "data" / "boards").glob("*.json")):
        if f.name.startswith("_"):
            continue
        try:
            b = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        m = b.get("meta") or {}
        if m.get("page_type") and m.get("slug") and FR.applies(b) and m.get("status") in ok:
            out.append(m["slug"])
    return out


def rebuilt_keys(root):
    """(keys, problem). A missing file is no keys. A file that is not a JSON list of strings
    is a problem line, not a crash — and no keys, so nothing is judged against a list the gate
    cannot read (the problem alone fails the run)."""
    f = root / "data/facts/rebuilt.json"
    if not f.is_file():
        return set(), None
    try:
        keys = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        return set(), f"data/facts/rebuilt.json: unreadable — not JSON ({e})"
    if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
        return set(), "data/facts/rebuilt.json: unreadable — must be a JSON list of slugs"
    return set(keys), None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    schema = json.loads((ROOT / "schemas/queries.schema.json").read_text(encoding="utf-8"))
    rebuilt, bad = rebuilt_keys(root)
    examined = unbuilt = 0
    problems = [bad] if bad else []
    awaiting = []
    for f in sorted((root / "data/queries").glob("*.json")):
        if f.name in LEDGERS:
            continue
        try:
            q = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            problems.append(f"{f.stem}: invalid question file — not JSON ({e})")
            continue
        try:
            jsonschema.validate(q, schema)
        except jsonschema.ValidationError as e:
            problems.append(f"{f.stem}: invalid question file — {e.message}")
            continue
        if q["slug"] != f.stem:
            problems.append(f"{f.stem}: invalid question file — slug '{q['slug']}' does not "
                            f"match the file name '{f.stem}'")
            continue
        if route_slug(q["route"]) != q["slug"]:
            problems.append(f"{f.stem}: invalid question file — route '{q['route']}' does not "
                            f"end in /{q['slug']}/")
            continue
        page = dist_path(q["route"].strip("/") or "index", root / "dist")
        listed = bool({page_key_for(q["route"]), route_slug(q["route"])} & rebuilt)
        if not page.is_file():
            if listed:   # rebuilt.json owes this gate a page; skipping it would pass it
                problems.append(f"{q['slug']}: listed in data/facts/rebuilt.json but not built — "
                                f"no {page.relative_to(root).as_posix()}; run the build")
            else:
                unbuilt += 1
            continue
        if not listed:
            awaiting.append(q["slug"])
            continue
        examined += 1
        problems += [f"{q['slug']}: {p}" for p in check_page(q, page.read_text(encoding="utf-8"))]
    for p in problems:
        print(p)
    if awaiting:
        print(f"awaiting rebuild: {', '.join(awaiting)}")
    print(f"examined {examined} pages ({unbuilt} not built, {len(awaiting)} awaiting rebuild); "
          f"{len(problems)} problems")
    # Zero input is not a pass once an approved project 5 board exists: the gate owes that
    # page a judgment and judged nothing (tests/py/test_gates_refuse_nothing.py).
    waiting = approved_new_family(root)
    if not examined and waiting:
        print(f"examined 0 pages while {len(waiting)} approved new-family board"
              f"{'s' if len(waiting) != 1 else ''} exist ({', '.join(waiting)}) — not a pass")
        return 1
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
