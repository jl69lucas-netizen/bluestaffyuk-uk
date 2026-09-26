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
    assert len(sheet["sections"]) == 7


import answer_board_batch  # noqa: E402

BATCH_KEYS = {"id", "title", "project", "askedAt", "intro", "status", "receivedAt",
              "receivedCommit", "sections", "questions"}
Q_KEYS = {"n", "key", "section", "question", "context", "where", "kind", "options"}


def test_slug_is_lowercase_hyphenated_and_capped():
    assert answer_board_batch.slug("Questions for Lisa Bright") == "questions-for-lisa-bright"
    assert answer_board_batch.slug("Project 5 · London board picks!") == "project-5-london-board-picks"
    assert len(answer_board_batch.slug("x" * 200)) == 60


def test_make_batch_has_the_spec_shape():
    batch = answer_board_batch.make_batch(parse("mini.md"), "2026-09-26-mini", "tools", "2026-09-26T12:00:00Z")
    assert set(batch) == BATCH_KEYS
    assert batch["status"] == "open" and batch["receivedAt"] == "" and batch["receivedCommit"] == ""
    assert [s["title"] for s in batch["sections"]] == ["First part", "Second part", "What happens next"]
    for q in batch["questions"]:
        assert set(q) == Q_KEYS
    assert [q["section"] for q in batch["questions"]] == [0, 0, 1]
    assert batch["questions"][1]["kind"] == "choice"
    assert batch["questions"][1]["options"] == [{"id": "a", "label": "Workspace rail"},
                                                {"id": "b", "label": "Side by side"}]
    assert batch["intro"].startswith("Answer briefly.")
    assert batch["sections"][2]["lead"] == "We read the answers and save them."


def test_the_cli_writes_the_lisa_batch_deterministically(tmp_path):
    cmd = [sys.executable, str(ROOT / "scripts/answer_board_batch.py"), str(LISA),
           "--project", "site-content", "--date", "2026-09-24", "--out-dir", str(tmp_path)]
    first = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert first.returncode == 0, first.stderr
    out = tmp_path / "2026-09-24-questions-for-lisa-bright.json"
    body = out.read_bytes()
    assert subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT).returncode == 0
    assert out.read_bytes() == body
    batch = json.loads(body)
    assert batch["id"] == "2026-09-24-questions-for-lisa-bright"
    assert batch["askedAt"] == "2026-09-24T12:00:00Z" and len(batch["questions"]) == 21
    assert len(body) < 256 * 1024
    assert "21 questions" in first.stdout


def test_the_committed_lisa_batch_matches_the_sheet():
    committed = ROOT / "docs/reference/answer-board/batches/2026-09-24-questions-for-lisa-bright.json"
    sheet = answer_sheet.parse_sheet(LISA.read_text(encoding="utf-8"))
    expected = answer_board_batch.make_batch(sheet, "2026-09-24-questions-for-lisa-bright",
                                             "site-content", "2026-09-24T12:00:00Z")
    assert json.loads(committed.read_text(encoding="utf-8")) == expected


def test_the_cli_exits_non_zero_on_a_bad_sheet(tmp_path):
    run = subprocess.run([sys.executable, str(ROOT / "scripts/answer_board_batch.py"),
                          str(FIX / "gap.md"), "--project", "x", "--out-dir", str(tmp_path)],
                         capture_output=True, text=True, cwd=ROOT)
    assert run.returncode == 1 and "expected question 2, found 3" in run.stderr


def _one(text):
    return all_questions(answer_sheet.parse_sheet(text))[0]


def test_option_ids_are_normalised_to_lowercase():
    q = _one("# T\n\n## S\n\n1. **Q?** x\n   - (A) One\n   - (B) Two\n")
    assert q["kind"] == "choice" and [o["id"] for o in q["options"]] == ["a", "b"]


def test_option_ids_may_be_up_to_three_characters():
    q = _one("# T\n\n## S\n\n1. **Q?** x\n   - (10) Ten\n")
    assert q["options"] == [{"id": "10", "label": "Ten"}]


@pytest.mark.parametrize("text", [
    "# T\n\n## S\n\n1. **Q?** x\n- (a) Unindented\n",
    "# T\n\n## S\n\n1. **Q?** x\n   - (a)\n",
])
def test_a_malformed_option_is_refused_with_the_line(text):
    with pytest.raises(answer_sheet.SheetError) as err:
        answer_sheet.parse_sheet(text)
    assert str(err.value) == "line 6: malformed option; write it indented as '   - (a) Label'"


def test_a_question_before_any_section_is_refused():
    with pytest.raises(answer_sheet.SheetError) as err:
        answer_sheet.parse_sheet("# T\n\n1. **Q?** x\n\n## S\n")
    assert str(err.value) == "line 3: a question must sit under a '## Section'"


def test_a_sheet_with_no_questions_is_refused():
    with pytest.raises(answer_sheet.SheetError) as err:
        answer_sheet.parse_sheet("# T\n\n## S\n\nJust prose.\n")
    assert str(err.value) == "the sheet has no questions"


def test_an_empty_section_title_is_refused():
    with pytest.raises(answer_sheet.SheetError, match="line 3"):
        answer_sheet.parse_sheet("# T\n\n## \n\n1. **Q?** x\n")


def test_an_empty_bold_question_is_refused():
    with pytest.raises(answer_sheet.SheetError, match="line 5"):
        answer_sheet.parse_sheet("# T\n\n## S\n\n1. ** ** x\n")


def test_a_tab_indented_continuation_joins_the_question():
    q = _one("# T\n\n## S\n\n1. **Q?** first\n\tsecond\n")
    assert q["context"] == "first second"


def test_a_leading_bom_is_ignored():
    sheet = answer_sheet.parse_sheet("\ufeff# T\n\n## S\n\n1. **Q?** x\n")
    assert sheet["title"] == "T" and len(all_questions(sheet)) == 1


def test_sections_carry_no_markdown_key():
    assert all(set(s) == {"title", "lead", "questions"} for s in parse("mini.md")["sections"])


def _cli(*args, cwd=ROOT):
    return subprocess.run([sys.executable, str(ROOT / "scripts/answer_board_batch.py"), *args],
                          capture_output=True, text=True, cwd=cwd)


def test_the_cli_refuses_a_bad_date(tmp_path):
    run = _cli(str(FIX / "mini.md"), "--project", "x", "--date", "2026-13-40", "--out-dir", str(tmp_path))
    assert run.returncode == 2 and list(tmp_path.iterdir()) == []


def test_the_cli_refuses_a_batch_id_that_is_not_a_slug(tmp_path):
    out = tmp_path / "out"
    run = _cli(str(FIX / "mini.md"), "--project", "x", "--batch-id", "../x", "--out-dir", str(out))
    assert run.returncode == 2 and "batch id must be a lowercase slug" in run.stderr
    assert list(tmp_path.rglob("*.json")) == []


def test_the_cli_reports_a_missing_sheet_without_a_traceback(tmp_path):
    run = _cli(str(tmp_path / "nope.md"), "--project", "x", "--out-dir", str(tmp_path))
    assert run.returncode == 1 and "Traceback" not in run.stderr and "nope.md" in run.stderr


def test_a_batch_over_the_size_cap_is_refused(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(answer_board_batch, "MAX_BYTES", 10)
    rc = answer_board_batch.main([str(FIX / "mini.md"), "--project", "x", "--out-dir", str(tmp_path)])
    assert rc == 1 and list(tmp_path.iterdir()) == []
    assert "over 256 KiB" in capsys.readouterr().err


def test_an_option_without_a_label_is_refused():
    with pytest.raises(answer_sheet.SheetError) as err:
        answer_sheet.parse_sheet("# T\n\n## S\n\n1. **Q?** x\n   - (a)  \n")
    assert str(err.value) == "line 6: option a has no label"
