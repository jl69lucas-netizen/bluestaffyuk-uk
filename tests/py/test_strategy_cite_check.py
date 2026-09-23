# tests/py/test_strategy_cite_check.py — scripts/strategy_cite_check.py (spec §9).
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import strategy_cite_check as S  # noqa: E402

SCRIPT = REPO / "scripts" / "strategy_cite_check.py"
SOURCE = "docs/research/gap-matrix-2026-09-24.md"


def make(tmp_path, recommendation, source_text="| city | 7/12 | 0 | no | high |\n1,200 words\n",
         sources=(SOURCE,), artifact=""):
    (tmp_path / "docs/research").mkdir(parents=True, exist_ok=True)
    (tmp_path / SOURCE).write_text(source_text)
    src = "\n".join(f"- `{s}`" for s in sources)
    doc = (f"# Strategy\n\n## Strategy A — Cities\n\nAbout 99 pages.\n\n"
           f"## Recommendation\n\n{recommendation}\n\n{artifact}"
           f"## Sources\n\n{src}\n")
    p = tmp_path / "strategy.md"
    p.write_text(doc)
    return p


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_figures_found_in_a_source_pass(tmp_path):
    p = make(tmp_path, "Pick A: 7/12 competitors have city pages; theirs run 1,200 words.")
    assert S.check(p, tmp_path) == []


def test_a_figure_in_no_source_fails_with_its_line(tmp_path):
    p = make(tmp_path, "Pick A: 9/12 competitors have city pages.")
    out = S.check(p, tmp_path)
    assert len(out) == 1 and "9/12" in out[0] and "line" in out[0]


def test_percentages_and_decimals_are_checked(tmp_path):
    out = S.check(make(tmp_path, "58% of them, a 0.75 share."), tmp_path)
    assert any("58%" in o for o in out) and any("0.75" in o for o in out)


def test_figures_outside_the_checked_sections_are_not_checked(tmp_path):
    # "99" sits under "## Strategy A" — the options may speculate; the pick may not.
    assert S.check(make(tmp_path, "Pick A: 7/12."), tmp_path) == []


def test_dates_code_single_digits_and_the_city_count_are_not_figures(tmp_path):
    p = make(tmp_path, "Pick A (`gap-matrix-2026-09-24.md`, 2026-09-24): 3 steps, all 28 cities.")
    assert S.check(p, tmp_path) == []


def test_the_artefact_table_is_checked_too(tmp_path):
    art = "## Concrete Artifact\n\n| topic | score |\n|---|---|\n| cities | 11 |\n\n"
    out = S.check(make(tmp_path, "Pick A: 7/12.", artifact=art), tmp_path)
    assert any("11" in o and "Concrete Artifact" in o for o in out)


def test_a_listed_source_that_does_not_exist_fails(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.", sources=(SOURCE, "docs/research/nope.md"))
    assert any("nope.md" in o and "does not exist" in o for o in S.check(p, tmp_path))


def test_no_sources_section_fails(tmp_path):
    p = tmp_path / "s.md"
    p.write_text("# S\n\n## Recommendation\n\nPick A.\n")
    assert any("## Sources" in o for o in S.check(p, tmp_path))


def test_no_recommendation_fails(tmp_path):
    p = tmp_path / "s.md"
    (tmp_path / "docs/research").mkdir(parents=True)
    (tmp_path / SOURCE).write_text("x")
    p.write_text(f"# S\n\n## Sources\n\n- `{SOURCE}`\n")
    assert any("## Recommendation" in o for o in S.check(p, tmp_path))


def test_cli_exit_codes(tmp_path):
    good = make(tmp_path, "Pick A: 7/12.")
    r = run(str(good), "--root", str(tmp_path))
    assert r.returncode == 0
    bad = make(tmp_path, "Pick A: 8/12.")
    r = run(str(bad), "--root", str(tmp_path))
    assert r.returncode == 1 and "8/12" in r.stdout
    r = run(str(tmp_path / "missing.md"))
    assert r.returncode == 2


# --- review-driven hardening: no tracebacks, a summary, --help, sources stay in root ---

def test_the_summary_says_what_was_examined(tmp_path):
    p = make(tmp_path, "Pick A: 7/12 competitors; theirs run 1,200 words.")
    r = run(str(p), "--root", str(tmp_path))
    assert r.returncode == 0
    assert "cite-check: strategy.md: 1 source, 2 figures checked, 0 problems" in r.stdout


def test_the_summary_counts_problems(tmp_path):
    p = make(tmp_path, "Pick A: 8/12 and 9/12.")
    r = run(str(p), "--root", str(tmp_path))
    assert r.returncode == 1
    assert "cite-check: strategy.md: 1 source, 2 figures checked, 2 problems" in r.stdout


def test_help_exits_0():
    r = run("--help")
    assert r.returncode == 0 and "may quote only" in r.stdout
    assert "Traceback" not in r.stderr


def test_bad_usage_exits_2():
    r = run()
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_a_strategy_that_is_a_directory_exits_2(tmp_path):
    r = run(str(tmp_path), "--root", str(tmp_path))
    assert r.returncode == 2 and "Traceback" not in r.stderr and "cite-check:" in r.stdout


def test_a_strategy_that_is_not_utf8_exits_2(tmp_path):
    p = tmp_path / "s.md"
    p.write_bytes(b"## Recommendation\n\n\xff\xfe 7/12\n")
    r = run(str(p), "--root", str(tmp_path))
    assert r.returncode == 2 and "Traceback" not in r.stderr and "cite-check:" in r.stdout


def test_a_strategy_that_cannot_be_read_exits_2(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.")
    p.chmod(0)
    try:
        if os.access(p, os.R_OK):
            return  # running as root: permissions are not enforced
        r = run(str(p), "--root", str(tmp_path))
        assert r.returncode == 2 and "Traceback" not in r.stderr and "cite-check:" in r.stdout
    finally:
        p.chmod(0o644)


def test_a_source_that_is_a_directory_is_a_problem(tmp_path):
    (tmp_path / "docs/research/adir").mkdir(parents=True)
    p = make(tmp_path, "Pick A: 7/12.", sources=(SOURCE, "docs/research/adir"))
    out = S.check(p, tmp_path)
    assert len(out) == 1 and "docs/research/adir" in out[0] and "not a file" in out[0]


def test_a_source_that_is_not_utf8_is_a_problem(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.", sources=(SOURCE, "docs/research/bin.md"))
    (tmp_path / "docs/research/bin.md").write_bytes(b"\xff\xfe 8/12")
    out = S.check(p, tmp_path)
    assert len(out) == 1 and "bin.md" in out[0] and "UTF-8" in out[0]


def test_a_source_that_cannot_be_read_is_a_problem(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.", sources=(SOURCE, "docs/research/locked.md"))
    locked = tmp_path / "docs/research/locked.md"
    locked.write_text("7/12")
    locked.chmod(0)
    try:
        if os.access(locked, os.R_OK):
            return  # running as root
        out = S.check(p, tmp_path)
        assert len(out) == 1 and "locked.md" in out[0] and "cannot be read" in out[0]
    finally:
        locked.chmod(0o644)


def test_an_absolute_source_path_is_a_problem(tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("8/12")
    root = tmp_path / "root"
    root.mkdir()
    p = make(root, "Pick A: 8/12.", sources=(SOURCE, str(outside)))
    out = S.check(p, root)
    assert any(str(outside) in o and "outside the root" in o for o in out)
    assert any("8/12" in o for o in out)  # its figures do not count


def test_a_source_that_escapes_the_root_is_a_problem(tmp_path):
    (tmp_path / "outside.md").write_text("8/12")
    root = tmp_path / "root"
    root.mkdir()
    p = make(root, "Pick A: 8/12.", sources=(SOURCE, "../outside.md"))
    out = S.check(p, root)
    assert any("../outside.md" in o and "outside the root" in o for o in out)
    assert any("8/12" in o for o in out)


def test_a_dotdot_path_that_stays_inside_the_root_is_fine(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.", sources=("docs/research/../research/gap-matrix-2026-09-24.md",))
    assert S.check(p, tmp_path) == []
