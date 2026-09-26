"""The answer board (spec docs/superpowers/specs/2026-09-26-answer-board-design.md).

One standing board holds every batch of questions Claude has for the user. A batch is made
from a question sheet; answers are keyed by question number, so the parser is strict about
numbering — a renumbered sheet would attach saved answers to the wrong question.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import answer_sheet  # noqa: E402

FIX = ROOT / "tests" / "py" / "fixtures" / "answer_board"
LISA = ROOT / "docs" / "reference" / "questions-for-lisa.md"


def parse(name):
    return answer_sheet.parse_sheet((FIX / name).read_text(encoding="utf-8"))


def all_questions(sheet):
    return [q for s in sheet["sections"] for q in s["questions"]]


def test_mini_sheet_parses_title_sections_and_questions():
    sheet = parse("mini.md")
    assert sheet["title"] == "Mini sheet"
    assert "Answer briefly." in sheet["preamble"]
    assert [s["title"] for s in sheet["sections"]] == ["First part", "Second part", "What happens next"]
    assert [(q["n"], q["key"], q["question"], q["kind"]) for q in all_questions(sheet)] == [
        (1, "q01", "Is the sky blue?", "text"),
        (2, "q02", "Which layout?", "choice"),
        (3, "q03", "Any other thoughts?", "text")]


def test_choice_options_are_kept_in_order_and_context_is_joined():
    q2 = all_questions(parse("mini.md"))[1]
    assert q2["options"] == [{"id": "a", "label": "Workspace rail"}, {"id": "b", "label": "Side by side"}]
    assert q2["context"] == "Pick one, then add a note if you like."
    assert q2["where"] == ""


def test_where_it_goes_is_split_from_the_context():
    q1 = all_questions(parse("mini.md"))[0]
    assert q1["context"] == "On most days." and q1["where"] == "`data/settings.json`."
    assert q1["options"] == []


def test_a_section_without_questions_keeps_its_prose():
    last = parse("mini.md")["sections"][-1]
    assert last["questions"] == [] and last["lead"] == "We read the answers and save them."


@pytest.mark.parametrize("name, message", [
    ("gap.md", "line 6: expected question 2, found 3"),
    ("dup.md", "line 6: question 1 is numbered twice (first on line 5)"),
    ("nobold.md", "line 5: question 1 has no **bold question**"),
    ("stray.md", "line 5: an option must sit under a question"),
])
def test_malformed_sheets_are_refused_with_the_line(name, message):
    with pytest.raises(answer_sheet.SheetError) as err:
        parse(name)
    assert str(err.value) == message


def test_a_sheet_must_start_with_a_title():
    with pytest.raises(answer_sheet.SheetError, match="line 1"):
        answer_sheet.parse_sheet("## No title\n\n1. **Q?** x\n")


def test_a_repeated_option_id_is_refused():
    # Lines: 1 "# T", 2 "", 3 "## S", 4 "", 5 the question, 6 "(a) One", 7 "(a) Two".
    with pytest.raises(answer_sheet.SheetError, match="line 7: option a is listed twice"):
        answer_sheet.parse_sheet("# T\n\n## S\n\n1. **Q?** x\n   - (a) One\n   - (a) Two\n")


def test_the_lisa_sheet_parses_to_21_text_questions():
    sheet = answer_sheet.parse_sheet(LISA.read_text(encoding="utf-8"))
    qs = all_questions(sheet)
    assert [q["key"] for q in qs] == [f"q{n:02d}" for n in range(1, 22)]
    assert {q["kind"] for q in qs} == {"text"}
    assert sheet["sections"][-1]["title"] == "What happens next"
