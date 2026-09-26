"""`scripts/render_pages.mjs` — `npm run test:render:pages` always ends in the zero-examined guard.

Parity plan Task 11 (CAG §19c, audit M1). The scorecard builder is Guards 1 and 2; it has to
run after EVERY full page run, including a failing one, and must not run after a filtered run
(Guard 1 would report the skipped pages as crashed). The two commands are replaced through
RENDER_PAGES_RUNNER / RENDER_SCORECARD so these tests start no browser."""
import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "render_pages.mjs"


def _run(tmp_path, pages_exit, card_exit, *args):
    log = tmp_path / "log.txt"
    pages = tmp_path / "pages.sh"
    pages.write_text(f'#!/bin/sh\necho "pages $*" >> {log}\nexit {pages_exit}\n')
    pages.chmod(0o755)
    card = tmp_path / "card.mjs"
    card.write_text("import { appendFileSync } from 'node:fs';\n"
                    f"appendFileSync({str(log)!r}, 'scorecard\\n');\nprocess.exit({card_exit});\n")
    env = dict(os.environ, RENDER_PAGES_RUNNER=str(pages), RENDER_SCORECARD=str(card))
    r = subprocess.run(["node", str(RUNNER), *args], capture_output=True, text=True, env=env, cwd=ROOT)
    return r, (log.read_text().splitlines() if log.exists() else [])


def test_a_clean_run_builds_the_scorecard(tmp_path):
    r, log = _run(tmp_path, 0, 0, "--reporter=dot")
    assert r.returncode == 0
    assert log == ["pages --reporter=dot", "scorecard"]


def test_a_failing_page_run_still_builds_the_scorecard_and_still_fails(tmp_path):
    r, log = _run(tmp_path, 1, 0)
    assert log == ["pages ", "scorecard"]
    assert r.returncode == 1


def test_a_zero_examined_scorecard_fails_a_green_page_run(tmp_path):
    r, log = _run(tmp_path, 0, 1)
    assert log[-1] == "scorecard"
    assert r.returncode == 1


def test_a_filtered_run_skips_the_scorecard_and_says_why(tmp_path):
    for flag in (["--grep", "kit-preview"], ["--project=vp375"], ["--last-failed"]):
        r, log = _run(tmp_path, 0, 0, *flag)
        assert "scorecard" not in log, flag
        assert "scorecard: skipped — a filtered run" in r.stdout, flag
        (tmp_path / "log.txt").unlink()
