"""`scripts/workflow_ref_check.py` — the workflow docs may only name what exists.

`docs/reference/WORKFLOW.md` and `docs/reference/quick-start.md` are the two documents a
session reads to decide which agent to call next. Known Issue 56 found WORKFLOW naming
monitoring agents that were never ported, with nothing on the line to say so: a reader
calls the agent and the first symptom is a failed run. The gate resolves every `bsuk-*`
agent or skill name, every `scripts/...` path and every `npm run ...` name against the
repo, and a line may name a missing one only when it carries a parenthesised
"not ported" marker.

The tests run the checker against a temporary tree, so they pin its BEHAVIOUR rather than
today's agent list; the last test runs it against this repo.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import workflow_ref_check as wrc  # noqa: E402


def tree(tmp_path, workflow, quick_start="# Quick start\n", page_run="# Page run\n"):
    """A minimal repo: one agent, one skill, one script, two npm scripts, the three docs."""
    (tmp_path / ".claude/agents").mkdir(parents=True)
    (tmp_path / ".claude/agents/bsuk-real-agent.md").write_text("---\n---\n", encoding="utf-8")
    (tmp_path / ".claude/skills/bsuk-real-skill").mkdir(parents=True)
    (tmp_path / ".claude/skills/bsuk-real-skill/SKILL.md").write_text("---\n---\n",
                                                                      encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/real.py").write_text("# stub\n", encoding="utf-8")
    (tmp_path / "package.json").write_text(json.dumps(
        {"scripts": {"check:real": "python3 scripts/real.py", "build": "astro build"}}),
        encoding="utf-8")
    ref = tmp_path / "docs/reference"
    ref.mkdir(parents=True)
    (ref / "WORKFLOW.md").write_text(workflow, encoding="utf-8")
    (ref / "quick-start.md").write_text(quick_start, encoding="utf-8")
    (ref / "page-run.md").write_text(page_run, encoding="utf-8")
    return tmp_path


def refs(problems):
    return [p.split("  ", 1)[1] for p in problems]


def test_names_that_exist_pass(tmp_path):
    root = tree(tmp_path, "Call `@bsuk-real-agent`, then bsuk-real-skill.\n"
                          "Run `python3 scripts/real.py` and `npm run check:real`.\n")
    problems, examined = wrc.check(root)
    assert problems == []
    assert examined == 4, "every reference counted — a gate that examines 0 is not a pass"


def test_a_missing_agent_is_flagged_backticked_or_not(tmp_path):
    root = tree(tmp_path, "| `@bsuk-ghost-agent` | weekly |\n"
                          "bsuk-litter-manager [when a puppy is available]\n")
    problems, _ = wrc.check(root)
    assert refs(problems) == ["bsuk-ghost-agent", "bsuk-litter-manager"]
    assert problems[0].startswith("WORKFLOW.md:1  "), problems


def test_a_missing_script_and_an_undefined_npm_script_are_flagged(tmp_path):
    root = tree(tmp_path, "SUPERSEDES scripts/gone_audit.py.\n"
                          "then `npm run -s check:ghost`\n")
    problems, _ = wrc.check(root)
    assert refs(problems) == ["scripts/gone_audit.py", "npm run check:ghost"]


def test_the_parenthesised_marker_excuses_the_line(tmp_path):
    root = tree(tmp_path,
                "| `@bsuk-ghost-agent` (not ported — deferred to project 6) | weekly |\n"
                "the source repo's scripts/seam_parity.py (not ported — source repo only)\n")
    problems, examined = wrc.check(root)
    assert problems == [] and examined == 2


def test_prose_saying_not_ported_is_not_a_marker(tmp_path):
    # Without the parentheses the phrase is a sentence about something else on the line,
    # and letting it excuse a name would disarm the gate for every name on that line.
    root = tree(tmp_path, "bsuk-ghost-agent — its data file was not ported\n")
    problems, _ = wrc.check(root)
    assert refs(problems) == ["bsuk-ghost-agent"]


def test_a_name_inside_a_path_is_not_an_agent_name(tmp_path):
    # `.claude/skills/bsuk-x/SKILL.md` and `data/bsuk-ontology.json` are paths; the path
    # guard in tests/py/test_rules_index.py owns them. Reading them as agent names would
    # flag every skill path in the doc.
    root = tree(tmp_path, "Read `.claude/skills/bsuk-ghost/SKILL.md` and `data/bsuk-ontology.json`.\n")
    problems, examined = wrc.check(root)
    assert problems == [] and examined == 0


def test_quick_start_is_checked_too(tmp_path):
    root = tree(tmp_path, "# Workflow\n", quick_start="→ `@bsuk-angle-ghost`\n")
    problems, _ = wrc.check(root)
    assert problems == ["quick-start.md:1  bsuk-angle-ghost"]


def test_the_page_run_is_checked_too(tmp_path):
    # docs/reference/page-run.md is the ordered per-page run: every row names a command, and
    # a row naming a command that does not exist is the row that gets skipped on page 14.
    root = tree(tmp_path, "# Workflow\n", page_run="| 1 | `npm run gate:ghost -- <slug>` |\n")
    problems, _ = wrc.check(root)
    assert problems == ["page-run.md:1  npm run gate:ghost"]


def test_the_arrives_in_task_marker_excuses_the_line(tmp_path):
    # The page run is written before two of the scripts it names (plan Tasks 25 and 26), and
    # tests/py/test_claude_md.py already expires the same marker the moment its path exists.
    root = tree(tmp_path, "# Workflow\n",
                page_run="`python3 scripts/ghost.py` then `npm run gate:ghost` (arrives in Task 25)\n")
    problems, examined = wrc.check(root)
    assert problems == [] and examined == 2


def test_a_missing_doc_is_an_error_not_a_silent_pass(tmp_path):
    root = tree(tmp_path, "# Workflow\n")
    (root / "docs/reference/page-run.md").unlink()
    with pytest.raises(FileNotFoundError):
        wrc.check(root)


def test_main_exits_1_on_a_problem_and_0_when_clean(tmp_path, capsys):
    bad = tree(tmp_path / "bad", "bsuk-ghost-agent\n")
    assert wrc.main(bad) == 1
    out = capsys.readouterr().out
    assert "bsuk-ghost-agent" in out and "1 problems" in out

    good = tree(tmp_path / "good", "bsuk-real-agent\n")
    assert wrc.main(good) == 0
    assert "examined 1 references in 3 files; 0 problems" in capsys.readouterr().out


def test_a_name_with_an_underscore_is_read_whole(tmp_path):
    # `bsuk-x_y` is a misspelt name, not `bsuk-x` followed by prose: the gate must see it.
    root = tree(tmp_path, "Call `@bsuk-real_agent` next.\n")
    problems, _ = wrc.check(root)
    assert refs(problems) == ["bsuk-real_agent"]


def test_npm_run_with_the_long_silent_flag_is_read(tmp_path):
    root = tree(tmp_path, "then `npm run --silent check:ghost` and `npm run -s check:real`\n")
    problems, examined = wrc.check(root)
    assert refs(problems) == ["npm run check:ghost"] and examined == 2


def test_a_skill_counts_only_when_its_skill_md_exists(tmp_path):
    root = tree(tmp_path, "bsuk-empty-skill\n")
    (root / ".claude/skills/bsuk-empty-skill").mkdir()
    problems, _ = wrc.check(root)
    assert refs(problems) == ["bsuk-empty-skill"]


def test_the_real_workflow_docs_name_only_what_exists():
    # The gate itself, run against this repo — `npm run check:workflow` exits 0.
    problems, examined = wrc.check(ROOT)
    assert examined > 50, f"examined only {examined} references — the parser stopped matching"
    assert problems == [], (
        "WORKFLOW.md / quick-start.md name an agent, skill, script or npm script that does "
        "not exist. Fix the name, or add a parenthesised '(not ported — …)' marker to the "
        "line:\n  " + "\n  ".join(problems))
