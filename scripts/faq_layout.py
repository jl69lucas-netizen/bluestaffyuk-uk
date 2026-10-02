#!/usr/bin/env python3
"""Board block 4d: FAQ placement — three FAQ blocks (top, middle, bottom) or one bottom block.

Two methods, shown side by side so the breeder can pick the rule:

  A · intent spread (Recommended): every fact-backed question for the page, picked or not
      (so the three-block pick cannot decide its own layout), is mapped topic -> intent group
      (INTENT_GROUPS: buying, dog, living). Three blocks when every group has at least
      GROUP_MIN questions AND the page's word target (the sum of the sections' "words"
      midpoints) is at least MIN_WORDS; otherwise one bottom block. A question's topic is its
      own "topic" key, else the first query_augment.TOPICS pattern its text matches, else
      "other", which belongs to no group. The "block" field is never the topic.
  B · by page type: THREE_BLOCK_TYPES get three blocks, every other type one bottom block.

A question counts when it is fact-backed: its "fact_source" is truthy, or it has no
"fact_source" key at all (a bare list). The question file is data/queries/<slug>.json; when it
is missing, method A is "NOT FETCHED".

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
GROUP_MIN = 2
MIN_WORDS = 2000
GROUPS = ("buying", "dog", "living")
# Every query_augment.TOPICS name -> the stage of the buyer's read it belongs to.
INTENT_GROUPS = {
    "price": "buying", "reserve": "buying", "delivery": "buying", "visit": "buying",
    "paperwork": "buying", "trust": "buying", "age": "buying",
    "health": "dog", "temperament": "dog", "coat": "dog", "breed": "dog", "lifespan": "dog",
    "home": "living", "family": "living", "training": "living", "care": "living",
}
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


def fact_backed(questions):
    return [q for q in questions if q.get("fact_source", True)]


def group_counts(questions):
    """{group: n} over the fact-backed questions; "other" and unmapped topics count nowhere."""
    counts = {g: 0 for g in GROUPS}
    for q in fact_backed(questions):
        g = INTENT_GROUPS.get(topic_of(q))
        if g:
            counts[g] += 1
    return counts


def word_target(board):
    return sum(_section_words(s) for s in board.get("sections", []))


def decide(questions, words, page_type, method="A"):
    """{"method", "layout", "groups", "topics", "words", "page_type"} for one method."""
    groups = group_counts(questions)
    topics = sorted({topic_of(q) for q in fact_backed(questions)})
    if method == "A":
        spread = all(n >= GROUP_MIN for n in groups.values())
        layout = THREE if spread and words >= MIN_WORDS else ONE
    elif method == "B":
        layout = THREE if page_type in THREE_BLOCK_TYPES else ONE
    else:
        raise ValueError(f"unknown method {method!r}")
    return {"method": method, "layout": layout, "groups": groups, "topics": topics,
            "words": words, "page_type": page_type}


def outline_layout(board):
    """The layout the board's outline has now, from its section ids starting "faq-"."""
    n = sum(1 for s in board.get("sections", []) if str(s.get("id", "")).startswith("faq-"))
    return "none" if n == 0 else ONE if n == 1 else THREE if n == 3 else f"{n} blocks"


def load_questions(slug, root=ROOT):
    path = pathlib.Path(root) / "data/queries" / f"{KM._bare(slug)}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("questions", [])


def _groups_str(r):
    return " · ".join(f"{g} {r['groups'][g]}" for g in GROUPS)


def _why_a(r):
    return (f"{_groups_str(r)}; {r['words']:,} words "
            f"(three blocks need every group at {GROUP_MIN}+ and {MIN_WORDS:,}+ words)")


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
             + (f"{_groups_str(a)}; " if a else "")
             + f"{words:,} words, not used")
    table = _md(["Method", "Result for this page", "Why"],
                [["A · intent spread (Recommended)"] + a_cells, ["B · by page type", b["layout"], b_why]])
    have = outline_layout(board)
    lines = [
        "Top, middle and bottom FAQs answer a buyer early: someone who lands with a question "
        "(price, delivery, health) gets it answered beside the section it belongs to, before "
        "they scroll away. One bottom FAQ is a closing block — it mops up what the body did "
        "not say, and suits a page read top to bottom. Method A counts every fact-backed question "
        "for the page, grouped into buying, the dog, and living with it; a page whose questions "
        "reach all three groups gets an FAQ at each stage of the read.",
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
