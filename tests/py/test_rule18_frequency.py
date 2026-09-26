"""Rule 18 says one thing everywhere: a ceiling of 105 keyword mentions, and no floor.

docs/reference/seo-rules.md called its ≈85–105 total a "Hard target per page" while
.claude/agents/bsuk-keyword-verifier.md — the agent that actually judges the count — says
≤105 with no minimum (the floor was retired on 2026-09-09 because it manufactured the very
repetition the evidence pass fails). Five more instruction files told a writer the total
"must hit 85–105×". A writer given both reads a floor and pads. The verifier is the authority;
this test holds every other instruction file to it (CAG parity audit, Wave 1 item 4).
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEO_RULES = ROOT / "docs/reference/seo-rules.md"
VERIFIER = ROOT / ".claude/agents/bsuk-keyword-verifier.md"
TOTAL_ROW = re.compile(r"^\|\s*\*\*TOTAL\*\*\s*\|\s*(.+?)\s*\|", re.M)
# a count band presented as something to reach: "must hit 85–105×", "vs 85–105× target",
# "~85–105 total mentions", "≈85–105×"
FLOOR = re.compile(r"(?i)(?:must hit|hits|≈|~|vs)\s*85\s*[–-]\s*105|85\s*[–-]\s*105[×x]?\s*(?:total\s*)?(?:target|mentions)|hard target")


def rule18(text):
    m = re.search(r"\*\*Rule 18\b.*?(?=\n\*\*Rule 19\b)", text, re.S)
    assert m, "seo-rules.md lost its Rule 18 block"
    return m.group(0)


def instruction_files():
    return (sorted((ROOT / ".claude/agents").glob("*.md"))
            + sorted((ROOT / ".claude/skills").glob("*/SKILL.md"))
            + sorted((ROOT / "docs/reference").glob("*.md"))
            + sorted((ROOT / "rules").glob("*.md")))


def test_seo_rules_total_row_is_the_verifiers():
    ours = TOTAL_ROW.findall(rule18(SEO_RULES.read_text(encoding="utf-8")))
    theirs = TOTAL_ROW.findall(VERIFIER.read_text(encoding="utf-8"))
    assert theirs == ["**≤105 (no minimum)**"], theirs
    assert ours == theirs, (ours, theirs)


def test_seo_rules_rule_18_states_no_floor_and_the_over_stuffed_flag():
    block = rule18(SEO_RULES.read_text(encoding="utf-8"))
    assert "no floor" in block
    assert "OVER-STUFFED" in block and ">110" in block


@pytest.mark.parametrize("path", instruction_files(), ids=lambda p: p.parent.name + "/" + p.name)
def test_no_instruction_file_presents_the_band_as_a_floor(path):
    bad = ["%s:%d  %s" % (path.name, n, l.strip()[:110])
           for n, l in enumerate(path.read_text(encoding="utf-8").splitlines(), 1) if FLOOR.search(l)]
    assert bad == [], ("Rule 18 has no floor (bsuk-keyword-verifier.md): the total is a ceiling "
                       "of 105, never a target to hit:\n  " + "\n  ".join(bad))


def test_the_floor_lint_fires_and_spares_the_ceiling(tmp_path):
    for line in ("total row at bottom must hit 85–105× per Rule 18",
                 "rolling total vs 85–105× target.",
                 "### 2a. Keyword distribution per page (~85–105 total mentions)",
                 "| **TOTAL** | **≈85–105×** | Hard target per page |"):
        assert FLOOR.search(line), line
    for line in ("| **TOTAL** | **≤105 (no minimum)** | |",
                 "the total row stays at or under 105 (Rule 18 — a ceiling, no floor)"):
        assert not FLOOR.search(line), line
