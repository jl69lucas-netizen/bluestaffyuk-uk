#!/usr/bin/env python3
"""Board block 4d: FAQ placement — three FAQ blocks (top, middle, bottom) or one bottom block.

Two methods, shown side by side so the breeder can pick the rule:

  A · intent spread (Recommended): three blocks when the page's picked FAQ questions span at
      least SPREAD distinct topics AND the page's word target (the sum of the sections'
      "words" midpoints) is at least MIN_WORDS; otherwise one bottom block. A question's topic
      is its own "topic" key, else the first query_augment.TOPICS pattern its text matches,
      else "other". The "block" field is never the topic: it has only three values.
  B · by page type: THREE_BLOCK_TYPES get three blocks, every other type one bottom block.

A question counts when it is picked: its "faq" is truthy (query_augment.pick_faq writes the
block name there), or it has no "faq" key at all (a bare list). The question file is
data/queries/<slug>.json; when it is missing, method A is "NOT FETCHED".

    python3 scripts/faq_layout.py <slug>
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
import query_augment as QA  # noqa: E402
from term_density import _md, _section_words  # noqa: E402

ROOT = QA.ROOT
SPREAD = 3
MIN_WORDS = 2000
# "for-sale" is the page_type the buy pages' boards carry; "buy" is kept as the plan named it.
THREE_BLOCK_TYPES = frozenset({"location", "buy", "for-sale"})
THREE, ONE = "top-middle-bottom", "bottom"


def _text(q):
    return q.get("question") or q.get("text") or ""


def topic_of(q):
    """The question's own topic, else the first TOPICS match on its text, else "other"."""
    if q.get("topic"):
        return q["topic"]
    topic, _ = QA.topic_of(_text(q))
    return topic or "other"


def picked(questions):
    return [q for q in questions if q.get("faq", True)]


def word_target(board):
    return sum(_section_words(s) for s in board.get("sections", []))


def decide(questions, words, page_type, method="A"):
    """{"method", "layout", "topics", "words", "page_type"} for one method."""
    topics = sorted({topic_of(q) for q in picked(questions)})
    if method == "A":
        layout = THREE if len(topics) >= SPREAD and words >= MIN_WORDS else ONE
    elif method == "B":
        layout = THREE if page_type in THREE_BLOCK_TYPES else ONE
    else:
        raise ValueError(f"unknown method {method!r}")
    return {"method": method, "layout": layout, "topics": topics, "words": words,
            "page_type": page_type}


def outline_layout(board):
    """The layout the board's outline has now, from its section ids starting "faq-"."""
    n = sum(1 for s in board.get("sections", []) if str(s.get("id", "")).startswith("faq-"))
    return "none" if n == 0 else ONE if n == 1 else THREE if n == 3 else f"{n} blocks"


def load_questions(slug, root=ROOT):
    path = pathlib.Path(root) / "data/queries" / f"{KM._bare(slug)}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("questions", [])


def _why_a(r):
    names = ", ".join(r["topics"]) or "none"
    n = len(r["topics"])
    return (f"{n} topic{'s' if n != 1 else ''} ({names}) against a spread of {SPREAD}; "
            f"word target {r['words']:,} words against {MIN_WORDS:,}")


def block(board, root=ROOT):
    slug = board["meta"]["slug"]
    page_type = board["meta"].get("page_type", "")
    words = word_target(board)
    qs = load_questions(slug, root)
    b = decide(qs or [], words, page_type, "B")
    if qs is None:
        a = None
        a_cells = [f"NOT FETCHED — no data/queries/{KM._bare(slug)}.json", "no question file to count"]
    else:
        a = decide(qs, words, page_type, "A")
        a_cells = [a["layout"], _why_a(a)]
    b_why = (f"page type `{page_type or 'unknown'}` "
             f"{'is' if page_type in THREE_BLOCK_TYPES else 'is not'} one of "
             f"{', '.join(sorted(THREE_BLOCK_TYPES))}; "
             + (f"{len(a['topics'])} topics ({', '.join(a['topics']) or 'none'}), " if a else "")
             + f"word target {words:,} words, not used")
    table = _md(["Method", "Result for this page", "Why"],
                [["A · intent spread (Recommended)"] + a_cells, ["B · by page type", b["layout"], b_why]])
    have = outline_layout(board)
    lines = [
        "Top, middle and bottom FAQs answer a buyer early: someone who lands with a question "
        "(price, delivery, health) gets it answered beside the section it belongs to, before "
        "they scroll away. One bottom FAQ is a closing block — it mops up what the body did "
        "not say, and suits a page read top to bottom.",
        "",
        table,
        "",
        f"The outline currently has **{have}** ({sum(1 for s in board.get('sections', []) if str(s.get('id', '')).startswith('faq-'))} "
        f"section{'s' if have != ONE else ''} whose id starts `faq-`).",
    ]
    if a is None:
        lines.append("The recommended method cannot decide until the question file exists.")
    elif a["layout"] != have:
        lines.append(f"**Mismatch:** method A (Recommended) says **{a['layout']}**, the outline has **{have}**.")
    else:
        lines.append(f"Method A (Recommended) agrees with the outline: **{have}**.")
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    usage = "usage: python3 scripts/faq_layout.py <slug>"
    if len(argv) != 1:
        print(usage, file=sys.stderr)
        return 2
    path = ROOT / "data/boards" / f"{KM._bare(argv[0])}.json"
    if not path.is_file():
        print(f"{usage} — no board at {path.relative_to(ROOT)}", file=sys.stderr)
        return 2
    print(block(json.loads(path.read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
