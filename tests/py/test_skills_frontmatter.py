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
