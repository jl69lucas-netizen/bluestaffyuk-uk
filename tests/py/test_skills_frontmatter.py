"""A skill is addressed by name, and the name is case-sensitive.

Task 12 re-based 25 system skills out of the source repo with a substitution table, and
`CAG` → `BSUK` is an uppercase-to-uppercase rule. It fired inside a frontmatter `name:`
and produced `name: BSUK-comprehensive-page-audit-system` in a directory called
`bsuk-comprehensive-page-audit-system`. Nothing else in the repo noticed: the marker gate
found no parrot stem, the fact lint found no unbacked claim, and the path guard found no
missing file. The only symptom would have been a skill that never loads, at the moment
somebody asked for it by its directory name.

So: for every skill, the frontmatter parses, `name:` equals the directory name **exactly**,
and `description:` is non-empty — a skill with no description is a skill the model cannot
decide to use.

Agents are NOT re-checked for name-vs-filename here. `scripts/build_agent_registry.py`
already derives the registry from the directory and refuses a file whose `name:` disagrees
with its stem (`tests/py/test_agent_registry.py`). What that registry does not assert is a
non-empty `description:`, so that one check is added below rather than duplicated.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".claude/skills"
AGENTS = ROOT / ".claude/agents"

FENCE = re.compile(r"^---\s*$")
# `name: x` / `description: "x"` — deliberately a line scanner rather than a YAML parse, so
# the test has no dependency the repo does not already carry, and so a broken frontmatter
# reports as "no frontmatter" rather than as a library traceback.
FIELD = re.compile(r"^([A-Za-z_-]+):\s*(.*)$")


def frontmatter(path: pathlib.Path) -> dict:
    """The file's YAML frontmatter as a flat dict, or ValueError when there is none."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or not FENCE.match(lines[0]):
        raise ValueError("%s has no YAML frontmatter" % path)
    out = {}
    for line in lines[1:]:
        if FENCE.match(line):
            return out
        m = FIELD.match(line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    raise ValueError("%s frontmatter is never closed" % path)


def skills():
    return sorted(SKILLS.glob("*/SKILL.md"))


@pytest.mark.parametrize("skill", skills(), ids=lambda p: p.parent.name)
def test_skill_name_matches_its_directory_exactly(skill):
    fm = frontmatter(skill)
    assert "name" in fm, "%s frontmatter has no name:" % skill.parent.name
    assert fm["name"] == skill.parent.name, (
        "%s declares name: %s — skill loading is case-sensitive and addresses a skill by "
        "its directory name, so these two must match character for character."
        % (skill.parent.name, fm["name"]))


@pytest.mark.parametrize("skill", skills(), ids=lambda p: p.parent.name)
def test_skill_has_a_non_empty_description(skill):
    fm = frontmatter(skill)
    assert fm.get("description", "").strip(), (
        "%s has no description: — a skill the model cannot decide to use is a skill "
        "nobody runs." % skill.parent.name)


def test_there_are_skills_to_check():
    # A glob that silently stopped matching would make both parametrised tests above
    # vacuous. 53 exist today: 28 generic plus the 25 system skills of Task 12.
    assert len(skills()) >= 25


@pytest.mark.parametrize("agent", sorted(AGENTS.glob("*.md")), ids=lambda p: p.stem)
def test_agent_has_a_non_empty_description(agent):
    # name-vs-filename is enforced by scripts/build_agent_registry.py; this is the one
    # frontmatter field that registry does not require.
    fm = frontmatter(agent)
    assert fm.get("description", "").strip(), (
        "%s has no description: — an agent with no description is never selected."
        % agent.name)


def test_the_frontmatter_reader_actually_fires(tmp_path):
    """Prove the checks can fail, on the exact defect that motivated this file."""
    d = tmp_path / "bsuk-thing"
    d.mkdir()
    p = d / "SKILL.md"
    p.write_text('---\nname: BSUK-thing\ndescription: ""\n---\nbody\n', encoding="utf-8")
    fm = frontmatter(p)
    assert fm["name"] != d.name, "an uppercase name must not compare equal to its directory"
    assert not fm["description"].strip()

    bare = tmp_path / "no-frontmatter.md"
    bare.write_text("body only\n", encoding="utf-8")
    with pytest.raises(ValueError, match="frontmatter"):
        frontmatter(bare)


# ── the frontmatter key set ─────────────────────────────────────────────────
# 25 skills arrived from the source repo in Task 12, each with whatever frontmatter its
# author happened to write. One carried a `context:` key nothing in this repo reads. A
# convention that holds for 24 of 25 files is not a convention, it is a coin flip the next
# author loses: pin it. `allowed-tools` is optional because it is a real, meaningful
# declaration on the skills that shell out, and noise on the ones that do not.
#
# Scoped to `bsuk-*` on purpose. The `openspec-*` skills are vendored upstream and carry
# their author's `license` / `compatibility` / `metadata` keys; rewriting someone else's
# frontmatter to match a house convention would break the next re-sync and buys nothing.
ALLOWED_KEYS = {"name", "description", "allowed-tools"}
REQUIRED_KEYS = {"name", "description"}
OURS = [p for p in skills() if p.parent.name.startswith("bsuk-")]


@pytest.mark.parametrize("skill", OURS, ids=lambda p: p.parent.name)
def test_skill_frontmatter_uses_the_agreed_key_set(skill):
    keys = set(frontmatter(skill))
    assert REQUIRED_KEYS <= keys, (
        "%s frontmatter is missing %s" % (skill.parent.name, sorted(REQUIRED_KEYS - keys)))
    assert keys <= ALLOWED_KEYS, (
        "%s frontmatter carries %s — the agreed key set is name, description and "
        "allowed-tools (the last only where the skill runs Bash). Add the key to every "
        "skill deliberately, or drop it here."
        % (skill.parent.name, sorted(keys - ALLOWED_KEYS)))


# ── the markdown-table lint ─────────────────────────────────────────────────
# A skill is read by a model, and a table whose row has fewer cells than its header does
# not render as a row with a gap — it renders as a row whose columns have all shifted, so
# the WHY column of a gate table lands under "Check ID". Three of these shipped in the
# Task 12 re-base, each made by editing one cell of a row and losing a pipe.
#
# The ONE pipe that is not a column separator is an escaped `\|`. A pipe inside a backtick
# span is NOT exempt: GFM splits a table row into cells before it parses inline code, so
# `badge|chip|tag|caption` really does become four columns on the page, which is the third
# defect this lint was written for. Masking backticks would have hidden it. Measured over
# every table in .claude/: escaping only `\|` reports exactly the three broken rows and
# nothing else, so the stricter rule costs no false positives.
ROW = re.compile(r"^\s*\|.*\|\s*$")
DIVIDER = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def _cells(line: str) -> int:
    return len(line.replace(r"\|", "\x00").strip().strip("|").split("|"))


def bad_table_rows(path: pathlib.Path):
    """[(lineno, got, want, text)] for every row whose cell count differs from its header."""
    out, fenced, header, width = [], False, False, 0
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            header, width = False, 0
            continue
        if fenced:
            continue
        if not ROW.match(line):
            header, width = False, 0
            continue
        if DIVIDER.match(line):
            continue
        if not header:
            header, width = True, _cells(line)
            continue
        got = _cells(line)
        if got != width:
            out.append((lineno, got, width, line.strip()[:110]))
    return out


TABLE_FILES = sorted(SKILLS.glob("*/SKILL.md")) + sorted(AGENTS.glob("*.md"))


@pytest.mark.parametrize("doc", TABLE_FILES,
                         ids=lambda p: (p.parent.name if p.name == "SKILL.md" else p.stem))
def test_every_markdown_table_row_matches_its_header(doc):
    bad = bad_table_rows(doc)
    assert bad == [], (
        "%s has a table row whose cell count disagrees with its header — every cell after "
        "the missing pipe renders under the wrong column:\n  " % doc.name
        + "\n  ".join("line %d: %d cells, header has %d  |  %s" % b for b in bad))


def test_the_table_lint_actually_fires(tmp_path):
    p = tmp_path / "t.md"
    p.write_text(
        "| A | B | C |\n|---|---|---|\n| one | two |\n"          # short row: reported
        "| x | y | z |\n"                                        # good row: silent
        "\n| P | Q |\n|---|---|\n| `a|b` | two |\n"              # pipe in code: REPORTED
        "| a \\| b | two |\n",                                   # escaped pipe: silent
        encoding="utf-8")
    bad = bad_table_rows(p)
    assert [b[0] for b in bad] == [3, 8], bad
