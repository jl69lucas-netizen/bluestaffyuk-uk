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


import build_answer_board  # noqa: E402


def shell():
    return build_answer_board.render_shell(build_answer_board.demo_batch())


def test_the_shell_holds_the_layout_containers_and_no_real_questions():
    page = shell()
    for marker in ('id="rail-batches"', 'id="batches"', 'id="done"', 'id="status-line"',
                   'id="total-done"', 'id="bar"', "<title>Questions for You</title>"):
        assert marker in page, marker
    assert "Are there blue Staffy puppies" not in page  # real questions come from db


def test_the_demo_batch_is_embedded_as_json_without_a_closing_script_tag():
    page = shell()
    blob = page.split('<script type="application/json" id="demo-batch">', 1)[1].split("</script>", 1)[0]
    demo = json.loads(blob)
    assert demo["id"] == "demo" and [q["kind"] for q in demo["questions"]] == ["text", "choice", "text"]
    evil = dict(demo, intro="has </script> inside")
    out = build_answer_board.render_shell(evil)
    blob = out.split('<script type="application/json" id="demo-batch">', 1)[1].split("</script>", 1)[0]
    assert json.loads(blob)["intro"] == "has </script> inside"


def test_only_google_fonts_is_referenced():
    hosts = set(re.findall(r'(?:src|href)="https?://([^/"]+)', shell()))
    assert hosts <= {"fonts.googleapis.com"}, hosts


def test_the_shell_builds_byte_identically(tmp_path):
    cmd = [sys.executable, str(ROOT / "scripts/build_answer_board.py"), "--out", str(tmp_path / "b.html")]
    run = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert run.returncode == 0, run.stderr
    first = (tmp_path / "b.html").read_bytes()
    subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert (tmp_path / "b.html").read_bytes() == first


CLIENT = ROOT / "scripts" / "answer_board_client.js"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_the_client_is_valid_javascript():
    run = subprocess.run(["node", "--check", str(CLIENT)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def test_every_capability_is_optional():
    js = CLIENT.read_text(encoding="utf-8")
    assert "window.claude && window.claude.use" in js
    for name in ("db", "comments", "downloads"):
        assert f'use.call(window.claude, "{name}")' in js
    assert js.count("if (!ns)") >= 3


def test_the_client_uses_the_spec_paths():
    js = CLIENT.read_text(encoding="utf-8")
    assert 'db.collection("batches")' in js
    assert '"batches/" + id + "/answers"' in js and '"batches/" + id + "/submissions"' in js
    for verb in ("canSendToClaude", "sendToClaude", "anchorFor", "onSnapshot", "localStorage"):
        assert verb in js, verb


def test_db_text_is_escaped_before_it_reaches_innerHTML():
    js = CLIENT.read_text(encoding="utf-8")
    assert "function esc(" in js and "function inline(" in js
    assert re.search(r"inline\(s\)\s*\{\s*s = esc\(s\)", js)


def test_the_longest_note_is_well_under_the_comment_limit():
    note = ("Answers submitted — " + "T" * 120 + " (" + "b" * 90 + "). Snapshot s-2026-09-26T10-11-12-000Z: "
            "99 answered, 99 skip, 99 not yet, 99 empty. Read db batches/" + "b" * 90 +
            "/submissions/s-2026-09-26T10-11-12-000Z.")
    assert len(note.encode("utf-8")) < 1024


def test_the_cli_refuses_a_sheet_title_over_120_characters(tmp_path):
    sheet = tmp_path / "long.md"
    sheet.write_text("# " + "T" * 121 + "\n\n## S\n\n1. **Q?** x\n", encoding="utf-8")
    run = _cli(str(sheet), "--project", "x", "--out-dir", str(tmp_path / "out"))
    assert run.returncode == 1 and "title is over 120 characters" in run.stderr
    assert not (tmp_path / "out").exists()
    sheet.write_text("# " + "T" * 120 + "\n\n## S\n\n1. **Q?** x\n", encoding="utf-8")
    assert _cli(str(sheet), "--project", "x", "--out-dir", str(tmp_path / "out")).returncode == 0


def test_the_demo_json_cannot_open_an_html_comment():
    demo = dict(build_answer_board.demo_batch(), intro="a <!-- b")
    out = build_answer_board.render_shell(demo)
    blob = out.split('<script type="application/json" id="demo-batch">', 1)[1].split("</script>", 1)[0]
    assert "<!--" not in blob and json.loads(blob)["intro"] == "a <!-- b"


HTML_BUILDERS = ("cardHtml", "batchHtml", "renderRail", "renderDone", "showDone")


def _strip_escapes(src):
    """Drop every esc(…), inline(…) and paras(…) call, parentheses balanced."""
    out, i = [], 0
    for m in re.finditer(r"\b(?:esc|inline|paras)\(", src):
        if m.start() < i:
            continue
        out.append(src[i:m.start()])
        depth, j = 1, m.end()
        while depth:
            depth += {"(": 1, ")": -1}.get(src[j], 0)
            j += 1
        i = j
    return "".join(out) + src[i:]


def test_every_db_field_in_the_html_builders_is_escaped():
    js = CLIENT.read_text(encoding="utf-8")
    for name in HTML_BUILDERS:
        body = re.search(r"\n  function " + name + r"\(.*?\n  }\n", js, re.S)
        assert body, name
        # On a line that builds HTML, a field of a question, batch, option, section or answer
        # may only be concatenated through esc(), inline() or paras(); a nested .map() that
        # builds more HTML is allowed.
        raw = [f for line in _strip_escapes(body.group(0)).splitlines() if "<" in line
               for f in re.findall(r"\+\s*(?:q|b|o|s|a)\.(?!\w+\.map\()[\w.]+", line)]
        assert raw == [], (name, raw)


HARNESS = FIX / "harness"


def _node_path():
    """node_modules of this checkout, then of the main checkout when this is a worktree."""
    paths = [ROOT / "node_modules"]
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    if common:
        paths.append((ROOT / common).resolve().parent / "node_modules")
    return ":".join(str(p) for p in paths if p.is_dir())


def test_the_client_in_a_browser_against_a_fake_db(tmp_path):
    import os
    if shutil.which("node") is None:
        pytest.skip("node not installed")
    env = dict(os.environ, NODE_PATH=_node_path())
    probe = subprocess.run(["node", "-e", "require('playwright')"], cwd=ROOT, env=env,
                           capture_output=True, text=True)
    if probe.returncode != 0:
        pytest.skip("playwright is not installed (node_modules here or in the main checkout)")
    page = tmp_path / "board.html"
    page.write_text(build_answer_board.render_shell(build_answer_board.demo_batch()), encoding="utf-8")
    run = subprocess.run(["node", str(HARNESS / "run.cjs"), str(page), str(HARNESS / "fake.js")],
                         cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
    if run.stdout.startswith("SKIP"):
        pytest.skip(run.stdout.strip())
    assert run.returncode == 0, run.stderr
    res = json.loads(run.stdout.split("RESULT ", 1)[1])
    assert 1 <= res["burstWrites"] <= 2, res                       # the debounce holds
    assert res["draft"] == {"writes": 1, "texts": ["from draft"], "shown": "from draft"}, res
    assert res["idleWrites"] == 0, res                             # nothing new, nothing written
    assert res["focus"]["submitted"] == res["focus"]["shown"], res  # Send submits what is shown
    assert res["focus"]["typedStill"] == "mine", res
    assert res["malformed"]["good"] == 1 and res["malformed"]["bad"] == 0, res
    assert res["malformed"]["errors"] == [], res
    assert res["demoDraft"] == {"ids": ["b9", "demo"], "real": "real"}, res  # demo keeps real drafts
    assert res["held"] == {"texts": [], "shown": "theirs"}, res               # a held newer record wins
    assert res["staleCache"]["sent"] == 1, res                  # a stale cache never blocks a send
    assert res["staleCache"]["status"].startswith("Sent to Claude Code"), res
    assert res["unavailable"]["snapshots"] == 1, res
    assert "Claude Code couldn't receive it right now" in res["unavailable"]["status"], res


def test_claude_md_carries_the_answer_board_rule():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "## Questions for the user — the answer board" in text
    section = text.split("## Questions for the user — the answer board", 1)[1].split("\n## ", 1)[0]
    for needle in ("scripts/answer_board_batch.py", "docs/reference/answer-board/README.md",
                   "ArtifactComments", "either/or"):
        assert needle in section, needle
    assert not re.search(r"^\d+\. \*\*", section, re.M), "use bullets: numbered bold items count as working rules"


def test_the_readme_names_the_board_url_and_the_paths():
    text = (ROOT / "docs/reference/answer-board/README.md").read_text(encoding="utf-8")
    assert "batches/<batchId>/submissions" in text and "docs/reference/answer-board/answers/" in text


def test_a_busy_send_button_looks_busy():
    assert '.btn[aria-disabled="true"]{opacity:.45;cursor:progress}' in build_answer_board.CSS


def test_claude_unavailable_has_its_own_message():
    js = CLIENT.read_text(encoding="utf-8")
    assert 'how === "claude_unavailable"' in js and "Claude Code couldn't receive it right now" in js
