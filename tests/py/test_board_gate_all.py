"""`board_gate.py --all` — the Asset Gate over every rebuilt page, chained into check:all.

Audit Wave 2 row 10: `board_gate.py` held the approval hash and the image build-gate checks,
and ran only when somebody typed it. `--all` runs the build stage over every slug in
data/facts/rebuilt.json and is `npm run check:boards`."""
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import board_gate as BG  # noqa: E402
import pageboard as PB   # noqa: E402

GATE = str(ROOT / "scripts" / "board_gate.py")


@pytest.fixture
def quiet_inputs(monkeypatch):
    monkeypatch.setattr(PB, "load_ontology", lambda: {"entities": []})
    monkeypatch.setattr(PB, "load_ledger", lambda: {"pages": {}})
    monkeypatch.setattr(PB, "live_headings", lambda: {"/a/": ["A"]})
    monkeypatch.setattr(PB, "load_all_boards", lambda: [])


def _judge(results):
    def judge(slug, stage, ont, ledger, live, boards):
        assert stage == "build"
        r = results[slug]
        if isinstance(r, Exception):
            raise r
        return r, [f"board-gate {slug} [build] — 1 sections, 1 headings, {len(live)} live pages, "
                   "0 entity refs, 0 ledger siblings, 0 assets examined",
                   f"{r} FAIL · 0 WARN"]
    return judge


def test_all_judges_every_rebuilt_page_and_fails_a_missing_board(monkeypatch, capsys, quiet_inputs):
    monkeypatch.setattr(PB, "rebuilt_slugs", lambda: {"good", "gone", "bad"})
    monkeypatch.setattr(BG, "judge", _judge({"good": 0, "bad": 2,
                                             "gone": PB.BoardError("no board for gone")}))
    assert BG.run_all() == 1
    out = capsys.readouterr().out
    assert "board-gate good [build] — 1 sections" in out and "examined — 0 FAIL" in out
    assert "FAIL board-missing             no board for gone" in out
    assert "2 FAIL · 0 WARN" in out                                   # a failing page prints in full
    assert out.rstrip().endswith("board-gate --all: examined 3 rebuilt pages against 1 live pages; "
                                 "2 failed: bad, gone")


def test_all_passes_when_every_rebuilt_page_passes(monkeypatch, capsys, quiet_inputs):
    monkeypatch.setattr(PB, "rebuilt_slugs", lambda: {"good"})
    monkeypatch.setattr(BG, "judge", _judge({"good": 0}))
    assert BG.run_all() == 0
    assert "examined 1 rebuilt pages against 1 live pages; 0 failed" in capsys.readouterr().out


def test_all_over_no_rebuilt_pages_is_not_a_pass(monkeypatch, capsys, quiet_inputs):
    monkeypatch.setattr(PB, "rebuilt_slugs", lambda: set())
    assert BG.run_all() == 1
    assert "examined 0 rebuilt pages" in capsys.readouterr().out


def test_all_takes_no_slug_and_no_other_flag():
    for argv in (["--all", "index"], ["--all", "--release"]):
        r = subprocess.run([sys.executable, GATE, *argv], capture_output=True, text=True)
        assert r.returncode == 2 and "usage: board_gate.py" in r.stdout, argv


def test_check_boards_is_the_all_run():
    scripts = json.loads((ROOT / "package.json").read_text())["scripts"]
    assert scripts["check:boards"] == "python3 scripts/board_gate.py --all"
