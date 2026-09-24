"""Every commit example an agent or skill tells a model to run carries the project trailer.

Subagents copy these examples verbatim, so an example without the trailer produces commits
without it (the user's standing rule: `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`).
"""
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TRAILER = "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
SCOPES = [ROOT / ".claude", ROOT / "docs/reference", ROOT / "CLAUDE.md"]
WINDOW = 8  # a multi-line message may put the trailer a few lines below `git commit`


def _files():
    for scope in SCOPES:
        if scope.is_file():
            yield scope
        else:
            yield from sorted(p for p in scope.rglob("*.md") if p.is_file())


def _missing(text):
    lines = text.split("\n")
    out = []
    for i, line in enumerate(lines):
        if "git commit -m" in line and TRAILER not in "\n".join(lines[i:i + WINDOW]):
            out.append((i + 1, line.strip()))
    return out


def test_detector_flags_a_bare_example_and_passes_a_trailed_one():
    assert _missing('git commit -m "fix: x"') == [(1, 'git commit -m "fix: x"')]
    assert _missing(f'git commit -m "fix: x" -m "{TRAILER}"') == []
    assert _missing(f'git commit -m "fix: x\n\n{TRAILER}"') == []


@pytest.mark.parametrize("path", list(_files()), ids=lambda p: str(p.relative_to(ROOT)))
def test_every_commit_example_carries_the_trailer(path):
    bad = _missing(path.read_text(encoding="utf-8"))
    assert not bad, f"{path.relative_to(ROOT)}: commit example(s) without the trailer: {bad}"
