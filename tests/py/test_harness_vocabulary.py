"""Rot guard: the render harness may not drift back into the source project's vocabulary.

`scripts/marker_check.py` owns twelve parrot markers with no allowlist, and spec 4 fixes that
list — so words that are not markers but ARE the source project's animal vocabulary (`bird`,
and the bird name `roys`) slip past it. They did: after Task 15's first pass the harness still
carried `.bird-card`, "Reserve this bird" and `available/roys` in fixtures, check comments and
meta assertions.

The fact lint (tests/py/test_agent_facts.py) is the wrong home for this. Its roots are prose —
`.claude/agents`, `.claude/skills`, `docs/reference` — and its MONEY/YEARS rules would report
every fixture that legitimately prints £1,500 or "12 weeks". So the guard lives here, scoped to
`tests/render/`, where the drift actually happened.

Adding a word here is cheap and removing one should be argued for: this list is the record of
which source-project nouns were re-based by hand.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tests/render"

SUFFIXES = {".ts", ".tsx", ".js", ".mjs", ".html", ".json", ".css", ".md"}

# Whole-word, case-insensitive. `bird` also catches `bird-card` / `bird_selection` because the
# hyphen and underscore are word boundaries; `birmingham` is not a match, which is why this is
# a boundary match and not a substring one.
# `weaned` is deliberately absent: puppies are weaned too, so it is BSUK vocabulary now.
BANNED = ("bird", "birds", "roys", "aviary", "chick", "chicks", "fledge", "clutchmate")
PATTERNS = {w: re.compile(rf"(?<![a-z0-9]){w}(?![a-z0-9])", re.I) for w in BANNED}


def _files():
    return sorted(p for p in HARNESS.rglob("*") if p.is_file() and p.suffix in SUFFIXES)


def test_the_harness_is_scoped_at_all():
    assert HARNESS.is_dir(), "tests/render/ is the scope of this guard"
    assert len(_files()) > 50, "the walk found suspiciously few harness files"


@pytest.mark.parametrize("word", BANNED)
def test_no_source_project_animal_vocabulary_survives(word):
    rx = PATTERNS[word]
    hits = []
    for p in _files():
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if rx.search(line):
                hits.append(f"{p.relative_to(ROOT)}:{i}: {line.strip()[:110]}")
    assert not hits, f"source-project word {word!r} still in the harness:\n" + "\n".join(hits)
