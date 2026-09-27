"""The canvas smoke paints every variant at 375, 768, 1024 and 1280 — and nothing can drop one.

Learning loop 2026-09-27 (docs/reports/learning-loop-2026-09-27.md, L5 / shortlist #8a). The
hero probe in tests/render/canvas.spec.ts tests rules/design.md rule 10's 390–450px band from
1024px and the dial and jump links switch at 1024, but until fc23018 the config painted only
375/768/1280, so hero b's 464px band at 1024 passed. The project was added then; this pins it.
"""
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tests" / "render" / "canvas.config.ts"
REQUIRED = {375, 768, 1024, 1280}


def widths(config_text):
    """Every project viewport width the config declares."""
    return {int(w) for w in re.findall(r"viewport:\s*\{\s*width:\s*(\d+)", config_text)}


def test_the_canvas_paints_every_boundary_width():
    got = widths(CONFIG.read_text(encoding="utf-8"))
    assert REQUIRED <= got, f"canvas.config.ts paints {sorted(got)}; it must include {sorted(REQUIRED)}"


def test_the_config_before_fc23018_fails_this_test():
    """The escape, replayed: the config as it stood when hero b's 1024px band shipped."""
    try:
        old = subprocess.run(["git", "-C", str(ROOT), "show", "fc23018^:tests/render/canvas.config.ts"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("fc23018 is not in this checkout's history")
    assert widths(old) == {375, 768, 1280}
    assert not REQUIRED <= widths(old)
