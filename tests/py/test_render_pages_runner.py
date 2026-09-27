"""`scripts/render_pages.mjs` — `npm run test:render:pages` always ends in the zero-examined guard.

Parity plan Task 11 (CAG §19c, audit M1). The scorecard builder is Guards 1 and 2; it has to
run after EVERY full page run, including a failing one, and must not run after a filtered or
stopped-early run (Guard 1 would report the skipped pages as crashed), nor after a run that
never started (it would merge the previous run's partials into a card dated today). The two
commands and the raw directory are replaced through RENDER_PAGES_RUNNER / RENDER_SCORECARD /
RENDER_RAW_DIR so these tests start no browser."""
import os
import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "render_pages.mjs"
FILTERED = "scorecard: skipped — a filtered run"
STOPPED = "scorecard: skipped — stopped early — not a full run"


def _run(tmp_path, pages_exit, card_exit, *args, manifest=True, runner=None, pages_body=""):
    """Run the runner with a fake page command that logs its argv and, like globalSetup,
    writes a fresh `_manifest.json` (unless `manifest=False`), and a fake scorecard that logs
    its argv. Returns (CompletedProcess, [log lines in call order])."""
    log = tmp_path / "log.txt"
    raw = tmp_path / "raw"
    raw.mkdir(exist_ok=True)
    pages = tmp_path / "pages.sh"
    write = f'echo "{{}}" > {raw}/_manifest.json\n' if manifest else ""
    pages.write_text(f'#!/bin/sh\necho "pages $*" >> {log}\n{write}{pages_body}exit {pages_exit}\n')
    pages.chmod(0o755)
    card = tmp_path / "card.mjs"
    card.write_text("import { appendFileSync } from 'node:fs';\n"
                    f"appendFileSync({str(log)!r}, ['scorecard', ...process.argv.slice(2)].join(' ') + '\\n');\n"
                    f"process.exit({card_exit});\n")
    env = dict(os.environ, RENDER_PAGES_RUNNER=str(runner or pages), RENDER_SCORECARD=str(card),
               RENDER_RAW_DIR=str(raw))
    r = subprocess.run(["node", str(RUNNER), *args], capture_output=True, text=True, env=env, cwd=ROOT)
    lines = log.read_text().splitlines() if log.exists() else []
    if log.exists():
        log.unlink()
    return r, lines


def test_a_clean_run_builds_the_scorecard(tmp_path):
    r, log = _run(tmp_path, 0, 0, "--reporter=dot")
    assert r.returncode == 0
    assert log == ["pages --reporter=dot", "scorecard --run first"]


def test_args_reach_the_page_command_and_flag_values_are_not_filters(tmp_path):
    r, log = _run(tmp_path, 0, 0, "--reporter", "dot", "--workers", "2", "-j", "3", "--retries=1")
    assert r.returncode == 0
    assert log == ["pages --reporter dot --workers 2 -j 3 --retries=1", "scorecard --run first"]


def test_the_run_label_is_stripped_from_playwright_and_given_to_the_scorecard(tmp_path):
    r, log = _run(tmp_path, 0, 0, "--scorecard-run=recheck", "--reporter=dot")
    assert r.returncode == 0
    assert log == ["pages --reporter=dot", "scorecard --run recheck"]


def test_a_failing_page_run_still_builds_the_scorecard_and_still_fails(tmp_path):
    r, log = _run(tmp_path, 1, 0)
    assert log == ["pages ", "scorecard --run first"]
    assert r.returncode == 1


def test_a_zero_examined_scorecard_fails_a_green_page_run(tmp_path):
    r, log = _run(tmp_path, 0, 1)
    assert log == ["pages ", "scorecard --run first"]
    assert r.returncode == 1


@pytest.mark.parametrize("flag", [
    ["--grep", "kit-preview"], ["--grep=kit-preview"], ["-g", "kit"], ["-gkit"], ["-g=kit"],
    ["--grep-invert", "kit"], ["--project=vp375"], ["--project", "vp375"], ["--shard=1/2"],
    ["--shard", "1/2"], ["--last-failed"], ["--only-changed"], ["tests/render/pages.spec.ts"],
    ["--reporter=dot", "kit-preview"],
])
def test_a_filtered_run_skips_the_scorecard_and_says_why(tmp_path, flag):
    r, log = _run(tmp_path, 0, 0, *flag)
    assert log == [f"pages {' '.join(flag)}"], flag
    assert FILTERED in r.stdout, flag
    assert r.returncode == 0


def test_a_failing_filtered_run_keeps_its_exit_code(tmp_path):
    r, log = _run(tmp_path, 1, 0, "--grep", "kit-preview")
    assert log == ["pages --grep kit-preview"]
    assert FILTERED in r.stdout
    assert r.returncode == 1


@pytest.mark.parametrize("flag", [["-x"], ["--max-failures=1"], ["--max-failures", "3"]])
def test_a_stop_early_run_skips_the_scorecard_with_its_own_message(tmp_path, flag):
    r, log = _run(tmp_path, 1, 0, *flag)
    assert log == [f"pages {' '.join(flag)}"]
    assert STOPPED in r.stdout
    assert FILTERED not in r.stdout
    assert r.returncode == 1


@pytest.mark.parametrize("flag", ["--list", "--help", "-h", "--ui"])
def test_a_non_measuring_invocation_skips_the_scorecard(tmp_path, flag):
    r, log = _run(tmp_path, 0, 0, flag)
    assert log == [f"pages {flag}"]
    assert "scorecard: skipped" in r.stdout
    assert r.returncode == 0


def test_a_page_command_that_cannot_start_fails_without_a_scorecard(tmp_path):
    r, log = _run(tmp_path, 0, 0, runner=tmp_path / "no-such-runner")
    assert r.returncode != 0
    assert log == []
    assert "no-such-runner" in r.stderr


def test_no_fresh_manifest_means_no_scorecard(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    stale = raw / "_manifest.json"
    stale.write_text("{}")
    os.utime(stale, (1_000_000_000, 1_000_000_000))
    r, log = _run(tmp_path, 1, 0, manifest=False)
    assert log == ["pages "]
    assert "scorecard: skipped — the page run never started (no fresh manifest)" in r.stdout
    assert r.returncode == 1


def test_a_green_run_without_a_fresh_manifest_does_not_pass(tmp_path):
    r, log = _run(tmp_path, 0, 0, manifest=False)
    assert log == ["pages "]
    assert r.returncode != 0


def test_a_killed_page_run_reports_the_signal_and_builds_no_scorecard(tmp_path):
    r, log = _run(tmp_path, 0, 0, pages_body="kill -TERM $$\n")
    assert log == ["pages "]
    assert r.returncode == 128 + 15
    assert "SIGTERM" in r.stderr


def test_a_rewritten_older_manifest_is_fresh(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    old = raw / "_manifest.json"
    old.write_text("{}")
    os.utime(old, (1_000_000_000, 1_000_000_000))
    r, log = _run(tmp_path, 0, 0)
    assert log == ["pages ", "scorecard --run first"]
    assert r.returncode == 0


def test_an_untouched_manifest_is_not_fresh_even_when_recent(tmp_path):
    """Freshness is before/after, not wall clock: a manifest written a moment before this
    invocation (by another run) and left untouched by this one is not this run's — even
    with its mtime ahead of this machine's clock (skew, a network filesystem)."""
    import time
    raw = tmp_path / "raw"
    raw.mkdir()
    m = raw / "_manifest.json"
    m.write_text("{}")
    ahead = time.time() + 60
    os.utime(m, (ahead, ahead))
    r, log = _run(tmp_path, 0, 0, manifest=False)
    assert log == ["pages "]
    assert "the page run never started (no fresh manifest)" in r.stdout
    assert r.returncode != 0


@pytest.mark.parametrize("flag", [["-u"], ["-u", "all"], ["--update-snapshots"],
                                  ["--update-snapshots", "missing"], ["--update-snapshots=changed"],
                                  ["-u", "none", "--reporter=dot"]])
def test_update_snapshots_with_or_without_a_value_is_a_full_run(tmp_path, flag):
    r, log = _run(tmp_path, 0, 0, *flag)
    assert log == [f"pages {' '.join(flag)}", "scorecard --run first"], flag
    assert r.returncode == 0


@pytest.mark.parametrize("flag", [["-u", "kit-preview"], ["--update-snapshots", "kit-preview"]])
def test_update_snapshots_does_not_swallow_a_positional_filter(tmp_path, flag):
    r, log = _run(tmp_path, 0, 0, *flag)
    assert log == [f"pages {' '.join(flag)}"], flag
    assert FILTERED in r.stdout
