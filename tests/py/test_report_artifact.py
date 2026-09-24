"""build_report_artifact.py builds the report it is TOLD to build.

Until the project 5 readiness pass the script took no arguments: it always rebuilt the
Foundation gate report, and three later plans called it with a source, an output and seven
labels that it silently ignored (the later gate reports were in fact built with
build_spec_artifact.py). It now takes the same nine positional arguments as
build_spec_artifact.py and build_plan_artifact.py, and with none it still builds the
Foundation report exactly as it always has.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_report_artifact as R  # noqa: E402

SCRIPT = ROOT / "scripts" / "build_report_artifact.py"
FOUNDATION = ROOT / "docs" / "artifacts" / "bsuk-foundation-gate-report.html"
MD = """# A sheet for someone

Why this exists, in one paragraph.

## First questions

- Is it one?

## Second questions

A body that says </script> in the middle.
"""
ARGS = ["Sheet Title", "Eyebrow line", "The heading", "Copy head — sheet",
        "status: ready to send", "2026-09-24", "docs/reference/sheet.md"]


def test_no_arguments_still_builds_the_foundation_report_byte_for_byte():
    assert R.foundation_page() == FOUNDATION.read_text(encoding="utf-8")


def test_arguments_build_the_named_markdown_into_the_named_file(tmp_path):
    src, out = tmp_path / "sheet.md", tmp_path / "out" / "sheet.html"
    src.write_text(MD, encoding="utf-8")
    before = FOUNDATION.read_bytes()
    r = subprocess.run([sys.executable, str(SCRIPT), str(src), str(out), *ARGS],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    page = out.read_text(encoding="utf-8")
    assert page.startswith("<title>Sheet Title</title>")
    for s in ('data-title="Summary"', 'data-title="First questions"',
              'data-title="Second questions"', "Why this exists, in one paragraph.",
              "Eyebrow line", "The heading", "status: ready to send", "2026-09-24",
              "docs/reference/sheet.md", "Copy the whole document as Markdown"):
        assert s in page, s
    assert "says <\\/script> in the middle" in page
    assert '"# Copy head \\u2014 sheet\\n\\n"' in page
    assert "Foundation" not in page
    assert "3 sections" in r.stdout
    assert FOUNDATION.read_bytes() == before, "an argument run must not touch the Foundation report"


def test_a_partial_argument_list_is_refused():
    r = subprocess.run([sys.executable, str(SCRIPT), "only.md", "two.html"],
                       capture_output=True, text=True)
    assert r.returncode == 2
    assert "usage: build_report_artifact.py" in r.stderr
