"""Parse a question sheet for the answer board.

Spec: docs/superpowers/specs/2026-09-26-answer-board-design.md §4. A sheet is markdown: a
'# Title' line, a preamble, then '## Section' headings. A numbered item
'N. **Question** context… **Where it goes:** …' is a question; wrapped lines are indented
under it, and indented '- (x) Label' lines are its options, which make it a choice question.
A section without numbered items is prose. Answers are keyed q01, q02, …, so numbering must
run 1..N with no gaps or repeats.
"""
import re

ITEM = re.compile(r"(\d+)\. (.*)")
OPTION = re.compile(r"\s+- \(([a-z0-9])\) (.+)")
BOLD = re.compile(r"\*\*(.+?)\*\*\s*(.*)", re.S)
GOES = "**Where it goes:**"


class SheetError(ValueError):
    """A sheet the board cannot use; the message names the line."""


def _finish(item):
    joined = " ".join(" ".join(item["lines"]).split())
    m = BOLD.match(joined)
    if not m:
        raise SheetError(f"line {item['line']}: question {item['n']} has no **bold question**")
    context, _, where = m.group(2).partition(GOES)
    return {"n": item["n"], "key": f"q{item['n']:02d}", "question": m.group(1).strip(),
            "context": context.strip(), "where": where.strip(),
            "kind": "choice" if item["options"] else "text", "options": item["options"]}


def parse_sheet(text):
    """Return {"title", "preamble", "sections": [{"title", "lead", "markdown", "questions"}]}.

    Each question: {"n", "key", "question", "context", "where", "kind", "options"}.
    """
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise SheetError("line 1: a sheet starts with '# Title'")
    preamble, sections = [], []
    section = item = None
    expected, seen = 1, {}

    def close_item():
        nonlocal item
        if item is not None:
            section["questions"].append(_finish(item))
            item = None

    for no, line in enumerate(lines[1:], start=2):
        if line.startswith("## "):
            close_item()
            section = {"title": line[3:].strip(), "lead": [], "body": [], "questions": []}
            sections.append(section)
            continue
        if section is None:
            preamble.append(line)
            continue
        section["body"].append(line)
        opt = OPTION.match(line)
        if opt:
            if item is None:
                raise SheetError(f"line {no}: an option must sit under a question")
            if any(o["id"] == opt.group(1) for o in item["options"]):
                raise SheetError(f"line {no}: option {opt.group(1)} is listed twice")
            item["options"].append({"id": opt.group(1), "label": opt.group(2).strip()})
            continue
        m = ITEM.match(line)
        if m:
            close_item()
            n = int(m.group(1))
            if n in seen:
                raise SheetError(f"line {no}: question {n} is numbered twice (first on line {seen[n]})")
            if n != expected:
                raise SheetError(f"line {no}: expected question {expected}, found {n}")
            seen[n] = no
            expected += 1
            item = {"n": n, "line": no, "lines": [m.group(2)], "options": []}
        elif item is not None and (line.startswith(" ") or not line.strip()):
            item["lines"].append(line.strip())
        else:
            close_item()
            section["lead"].append(line)
    close_item()
    for s in sections:
        s["lead"] = "\n".join(s["lead"]).strip()
        s["markdown"] = "\n".join(s.pop("body")).strip()
    return {"title": lines[0][2:].strip(), "preamble": "\n".join(preamble).strip(),
            "sections": sections}
