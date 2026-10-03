"""scripts/answer_board_save.py: the receive step's marker pass (Task 7.5, 2026-10-03).

Saving the breeder's answers verbatim once committed sibling-site URLs and broke
check:markers. The helper replaces each marker-bearing token whole, keeps JSON valid and
byte-identical elsewhere, notes the change in a .md, and re-scans with marker_check itself.
Marker strings are built from marker_check.MARKERS, never typed here.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import answer_board_save as ABS  # noqa: E402
import marker_check as MC  # noqa: E402

BRAND = next(m for m in MC.MARKERS if m.isalpha() and len(m) > 10)   # the long brand marker
WORD = next(m for m in MC.MARKERS if m.isalpha() and len(m) < 8)      # a short plain marker
URL = f"https://{BRAND}.com/some-page/"


def test_the_markers_are_marker_checks_own():
    assert ABS.MC is MC and BRAND in MC.MARKERS and WORD in MC.MARKERS


def test_a_url_is_replaced_whole_and_a_word_by_the_term_label():
    text, n = ABS.neutralise_text(f"see {URL}, and the {WORD.title()} page.")
    assert n == 2
    assert text == f"see {ABS.PAGE_LABEL}, and the {ABS.TERM_LABEL} page."
    assert not ABS._has_marker(text)


def test_a_two_word_marker_is_one_replacement():
    two = next(m for m in MC.MARKERS if " " in m)
    text, n = ABS.neutralise_text(f"a {two.title()} bird")
    assert n == 1 and text == f"a {ABS.TERM_LABEL} bird"


def test_clean_text_is_untouched():
    t = "Not beside: each infographic gets its own H3. See WCAG-AA."
    assert ABS.neutralise_text(t) == (t, 0)


def test_a_json_file_stays_valid_and_keeps_its_layout(tmp_path):
    d = {"answers": [{"key": "q08", "text": f"see this page, {URL}\nthen {WORD}s"}], "n": 1}
    p = tmp_path / "a.json"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    assert ABS.neutralise_file(p) == 2
    out = p.read_text(encoding="utf-8")
    got = json.loads(out)
    assert got["answers"][0]["text"] == f"see this page, {ABS.PAGE_LABEL}\nthen {ABS.TERM_LABEL}"
    assert got["n"] == 1 and out.startswith('{"answers": [{"key": "q08"')
    assert MC.hits_in(p) == []


def test_a_md_file_gets_the_note(tmp_path):
    p = tmp_path / "a.md"
    p.write_text(f"1. Text: {URL}\n", encoding="utf-8")
    assert ABS.neutralise_file(p) == 1
    out = p.read_text(encoding="utf-8")
    assert ABS.PAGE_LABEL in out and "the original text stays in the answer-board db" in out
    assert MC.hits_in(p) == []


def test_a_clean_file_is_not_rewritten(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("clean\n", encoding="utf-8")
    assert ABS.neutralise_file(p) == 0 and p.read_text() == "clean\n"


def test_cli_check_reports_and_changes_nothing(tmp_path, capsys):
    p = tmp_path / "a.md"
    p.write_text(f"{URL}\n", encoding="utf-8")
    assert ABS.main(["--check", str(p)]) == 1
    assert p.read_text() == f"{URL}\n"
    assert ABS.main(["--neutralise", str(p)]) == 0
    assert ABS.main(["--check", str(p)]) == 0
    assert "examined 1 file(s); clean" in capsys.readouterr().out


def test_cli_usage_and_missing_file(tmp_path):
    assert ABS.main([]) == 2
    assert ABS.main(["--neutralise", str(tmp_path / "nope.md")]) == 2


def test_the_saved_answers_on_disk_are_clean():
    files = sorted((ROOT / "docs/reference/answer-board/answers").glob("*.*"))
    assert files
    assert ABS.main(["--check", *map(str, files)]) == 0


def test_the_readme_names_the_step_without_copying_the_markers():
    readme = (ROOT / "docs/reference/answer-board/README.md").read_text(encoding="utf-8")
    assert "scripts/answer_board_save.py --neutralise" in readme
    assert "scripts/marker_check.py" in readme
    assert MC.hits_in(ROOT / "docs/reference/answer-board/README.md") == []


# The reviewer's case: a URL whose path carries a spelled two-word marker. Built from
# marker_check's own markers (the hyphenated spelled one, plus a plain one), never typed.
SPELLED_HYPHEN = next(m for m in MC.SPELLED if "-" in m)
PATH_URL = f"https://example.com/{SPELLED_HYPHEN}-{WORD}s/"


def test_a_url_with_a_spelled_marker_in_its_path_is_one_whole_label():
    text, n = ABS.neutralise_text(f"see {PATH_URL} please")
    assert (text, n) == (f"see {ABS.PAGE_LABEL} please", 1)
    assert text.count(ABS.PAGE_LABEL) == 1 and ABS.TERM_LABEL not in text
    assert "example" not in text and "/" not in text


def test_escaped_slashes_in_a_json_file_are_one_whole_label(tmp_path):
    escaped = PATH_URL.replace("/", "\\/")
    p = tmp_path / "a.json"
    p.write_text('{"text": "see ' + escaped + ' please", "n": 1}', encoding="utf-8")
    assert ABS.neutralise_file(p) == 1
    out = p.read_text(encoding="utf-8")
    assert out == '{"text": "see ' + ABS.PAGE_LABEL + ' please", "n": 1}'
    assert json.loads(out)["text"] == f"see {ABS.PAGE_LABEL} please"
    assert MC.hits_in(p) == []


def test_a_clean_url_is_left_alone_even_beside_a_marker_word():
    text, n = ABS.neutralise_text(f"https://example.com/staffy-guide/ and a {WORD}")
    assert (text, n) == (f"https://example.com/staffy-guide/ and a {ABS.TERM_LABEL}", 1)


def test_marker_check_has_a_public_helper():
    assert MC.has_marker(PATH_URL) and not MC.has_marker("WCAG-AA staffy")
