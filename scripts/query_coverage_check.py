#!/usr/bin/env python3
"""Query coverage gate over dist/ (spec 2026-09-23 §10).

For every data/queries/<slug>.json whose route is built in dist/, the page must carry:
  1. three FAQ blocks (kit-faq, in document order top/middle/bottom) of 5–7, 5–7 and 7–10
     questions, 15–20 in total, every question an H3;
  2. every must-answer question at its covered_by text, with an answer under it;
  3. FAQPage schema naming exactly the visible FAQ questions;
  4. every extra section's recorded heading as an H2;
  5. on location pages, at least section_target.total body sections — a body section is a
     <section data-section-label> that is not #top, #key-takeaways or #newsletter and holds no frame part:
     no kit hero, counter, trust strip, page nav, review, FAQ block and no form
     (docs/reference/location-page-template.md, "The fixed frame" — frame is never counted).

A question file whose route is not built is skipped and counted: an unbuilt page ships
nothing. Exit 1 on any problem, 0 otherwise.

  python3 scripts/query_coverage_check.py
"""
import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
from query_augment import BLOCKS, FAQ_MAX, FAQ_MIN, FAQ_TOTAL_MAX, normalise  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FAQ_TOTAL_MIN = 15
FRAME_IDS = {"top", "key-takeaways", "newsletter"}
# The kit components that make up the fixed frame. A section holding one is frame, not body.
FRAME_CLASSES = {"kit-hero", "kit-counter", "kit-trust", "kit-nav", "kit-quote", "kit-faq"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [tag, section_index|None, faq_index|None]
        self.sections = []       # {"id", "frame"}
        self.faq_blocks = []     # {"h3": [text], "details": n}
        self.headings = []       # {"level", "text", "answer", "faq"}
        self.ld = []
        self._heading = None     # [level, [text], faq_index]
        self._ld = None

    def _open(self, kind):
        return [e[kind] for e in self.stack if e[kind] is not None]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in VOID:
            return
        sec = faq = None
        classes = set((a.get("class") or "").split())
        if tag == "section" and "data-section-label" in a:
            self.sections.append({"id": a.get("id") or "", "frame": False})
            sec = len(self.sections) - 1
        if tag == "form" or classes & FRAME_CLASSES:
            for i in self._open(1) + ([sec] if sec is not None else []):
                self.sections[i]["frame"] = True
        if tag == "div" and "kit-faq" in classes:
            self.faq_blocks.append({"h3": [], "details": 0})
            faq = len(self.faq_blocks) - 1
        if tag == "details" and self._open(2):
            self.faq_blocks[self._open(2)[-1]]["details"] += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            inside = self._open(2)
            self._heading = [int(tag[1]), [], inside[-1] if inside and tag == "h3" else None]
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = []
        self.stack.append([tag, sec, faq])

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading:
            level, parts, faq = self._heading
            text = " ".join("".join(parts).split())
            self.headings.append({"level": level, "text": text, "answer": "", "faq": faq})
            if faq is not None:
                self.faq_blocks[faq]["h3"].append(text)
            self._heading = None
        if tag == "script" and self._ld is not None:
            self.ld.append("".join(self._ld))
            self._ld = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._ld is not None:
            self._ld.append(data)
        elif self._heading is not None:
            self._heading[1].append(data)
        elif self.headings and not any(e[0] == "summary" for e in self.stack):
            self.headings[-1]["answer"] += data


def faq_schema_names(blobs):
    names = []

    def walk(node):
        if isinstance(node, list):
            for x in node:
                walk(x)
        elif isinstance(node, dict):
            t = node.get("@type")
            if t == "FAQPage" or (isinstance(t, list) and "FAQPage" in t):
                for q in node.get("mainEntity", []):
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
    if len(blocks) != 3:
        problems.append(f"FAQ blocks: {len(blocks)}, want 3 (top, middle, bottom)")
    else:
        for name, b in zip(BLOCKS, blocks):
            n = len(b["h3"])
            if b["details"] != n:
                problems.append(f"FAQ {name}: {b['details']} questions but {n} H3s — "
                                "every question must be an H3")
            if not FAQ_MIN[name] <= n <= FAQ_MAX[name]:
                problems.append(f"FAQ {name}: {n} questions, want {FAQ_MIN[name]}–{FAQ_MAX[name]}")
    total = sum(len(b["h3"]) for b in blocks)
    if not FAQ_TOTAL_MIN <= total <= FAQ_TOTAL_MAX:
        problems.append(f"FAQ total: {total}, want {FAQ_TOTAL_MIN}–{FAQ_TOTAL_MAX}")
    faq_h3 = {normalise(t) for b in blocks for t in b["h3"]}
    heads = {}
    for h in p.headings:
        heads.setdefault(normalise(h["text"]), h)
    for item in q["questions"]:
        if not item["must_answer"]:
            continue
        cov = item.get("covered_by")
        if not cov:
            problems.append(f"{item['id']}: must-answer question has no covered_by")
            continue
        key = normalise(cov["text"])
        h = heads.get(key) if (cov["where"] == "heading" or key in faq_h3) else None
        if h is None:
            where = "an FAQ H3" if cov["where"] == "faq" else "a heading"
            problems.append(f"{item['id']}: '{cov['text']}' not found as {where}")
        elif not h["answer"].strip():
            problems.append(f"{item['id']}: '{cov['text']}' has no answer under it")
    schema = {normalise(n) for n in faq_schema_names(p.ld)}
    if schema != faq_h3:
        problems.append(f"FAQPage schema: {len(faq_h3 - schema)} visible questions missing, "
                        f"{len(schema - faq_h3)} not visible")
    h2s = {normalise(h["text"]) for h in p.headings if h["level"] == 2}
    for e in q.get("extra_sections", []):
        if not e.get("heading"):
            problems.append(f"extra section '{e['topic']}': no heading recorded")
        elif normalise(e["heading"]) not in h2s:
            problems.append(f"extra section '{e['topic']}': '{e['heading']}' is not an H2 on the page")
    if q["page_type"] == "location":
        body = [s for s in p.sections if s["id"] not in FRAME_IDS and not s["frame"]]
        t = q["section_target"]
        if len(body) < t["total"]:
            problems.append(f"body sections: {len(body)}, want at least {t['total']} "
                            f"(competitors {t['matched']} + {t['extra']})")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    schema = json.loads((ROOT / "schemas/queries.schema.json").read_text(encoding="utf-8"))
    examined = unbuilt = 0
    problems = []
    for f in sorted((root / "data/queries").glob("*.json")):
        if f.name == "spend.json":
            continue
        q = json.loads(f.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(q, schema)
        except jsonschema.ValidationError as e:
            problems.append(f"{f.stem}: invalid question file — {e.message}")
            continue
        page = root / "dist" / q["route"].strip("/") / "index.html"
        if not page.is_file():
            unbuilt += 1
            continue
        examined += 1
        problems += [f"{q['slug']}: {p}" for p in check_page(q, page.read_text(encoding="utf-8"))]
    for p in problems:
        print(p)
    print(f"examined {examined} pages ({unbuilt} not built); {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
