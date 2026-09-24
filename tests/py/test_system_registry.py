"""`scripts/build_system_registry.py` — the registry is derived, not typed.

The failure this prevents is the one the source repo shipped: a registry hand-maintained
until it claimed 68 agents over 67 files, with no gate that noticed. The tests below run
the generator against a temporary tree rather than this repo, so they assert the
generator's BEHAVIOUR — what it renders, what it preserves, when `--check` fails — instead
of pinning today's counts, which every new agent would come here to bump.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_system_registry as bsr  # noqa: E402

PROSE = "Hand-written prose that must survive every regeneration.\n"


def tree(tmp_path, agents=("bsuk-alpha", "bsuk-beta"), skills=("zeta",), deferred=True):
    """A minimal repo: one agent per tier name, one skill, the gate scripts, a manifest."""
    (tmp_path / ".claude/agents").mkdir(parents=True)
    tiers = ["tier_max", "tier_medium"]
    for i, name in enumerate(agents):
        (tmp_path / ".claude/agents" / (name + ".md")).write_text(
            "---\nname: %s\ndescription: Does the %s thing.\n---\nbody\n" % (name, name),
            encoding="utf-8")
    for s in skills:
        d = tmp_path / ".claude/skills" / s
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: %s\n---\n" % s, encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    for path, _ in bsr.GATES:
        f = tmp_path / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("# stub\n", encoding="utf-8")
    (tmp_path / "scripts/aeo_audit.py").write_text("# stub\n", encoding="utf-8")
    (tmp_path / "scripts/notes.txt").write_text("not a script\n", encoding="utf-8")
    (tmp_path / "data").mkdir(exist_ok=True)
    (tmp_path / "data/boards").mkdir()
    (tmp_path / "data/agent-registry.json").write_text(json.dumps(
        {"_meta": {}, "agents": {n: {"tier": tiers[i % len(tiers)]}
                                 for i, n in enumerate(agents)}}), encoding="utf-8")
    rows = [{"src": "a.md", "dst": "a.md", "mode": "rebase", "notes": ""}]
    if deferred:
        rows += [{"src": "b.md", "dst": "b.md", "mode": "deferred", "notes": "project 6 owns it"},
                 {"src": "c.md", "dst": "c.md", "mode": "deferred", "notes": "spec §10 out of scope"}]
    (tmp_path / "data/port-manifest.json").write_text(json.dumps(rows), encoding="utf-8")
    doc = tmp_path / "docs/reference/system-registry.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# Title\n\n" + PROSE + "\n" + bsr.START + "\n\n" + bsr.END + "\n",
                   encoding="utf-8")
    return tmp_path


def written(tmp_path):
    doc = tmp_path / "docs/reference/system-registry.md"
    doc.write_text(bsr.compose(tmp_path), encoding="utf-8")
    return doc.read_text(encoding="utf-8")


def test_it_renders_every_agent_under_its_own_tier(tmp_path):
    out = written(tree(tmp_path))
    assert "## Agents — 2" in out
    assert "`.claude/agents/bsuk-alpha.md`" in out
    assert "`.claude/agents/bsuk-beta.md`" in out
    assert "### `tier_max` — 1" in out and "### `tier_medium` — 1" in out


def test_it_renders_skills_scripts_and_data_from_the_filesystem(tmp_path):
    out = written(tree(tmp_path))
    assert "`.claude/skills/zeta/SKILL.md`" in out
    assert "`scripts/aeo_audit.py`" in out
    assert "notes.txt" not in out, "only .py/.sh/.mjs are scripts"
    assert "`data/boards/`" in out, "a directory keeps its trailing slash"
    assert "`data/agent-registry.json`" in out


def test_it_groups_deferred_rows_by_project_without_naming_paths(tmp_path):
    out = written(tree(tmp_path))
    assert "**project 6** — 1 rows" in out
    assert "**no project** — 1 rows" in out
    assert "b.md" not in out, "a deferred path named here is a path the guard would flag"


def test_hand_written_prose_outside_the_markers_survives(tmp_path):
    root = tree(tmp_path)
    first = written(root)
    assert PROSE in first
    again = bsr.compose(root)
    assert PROSE in again
    assert again == first, "regeneration must be idempotent"


def test_check_fails_when_the_doc_is_stale_and_passes_when_it_is_not(tmp_path):
    root = tree(tmp_path)
    doc = root / "docs/reference/system-registry.md"
    assert doc.read_text(encoding="utf-8") != bsr.compose(root), "starts stale"
    doc.write_text(bsr.compose(root), encoding="utf-8")
    assert doc.read_text(encoding="utf-8") == bsr.compose(root), "now in sync"

    # Adding an agent makes it stale again — the whole point of the gate.
    (root / ".claude/agents/bsuk-gamma.md").write_text(
        "---\nname: bsuk-gamma\ndescription: New.\n---\n", encoding="utf-8")
    reg = json.loads((root / "data/agent-registry.json").read_text(encoding="utf-8"))
    reg["agents"]["bsuk-gamma"] = {"tier": "tier_max"}
    (root / "data/agent-registry.json").write_text(json.dumps(reg), encoding="utf-8")
    assert doc.read_text(encoding="utf-8") != bsr.compose(root)


def test_a_missing_marker_is_an_error_not_a_silent_rewrite(tmp_path):
    root = tree(tmp_path)
    (root / "docs/reference/system-registry.md").write_text("no markers here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="markers"):
        bsr.compose(root)


def test_a_gate_table_row_naming_a_missing_script_is_an_error(tmp_path):
    root = tree(tmp_path)
    (root / bsr.GATES[0][0]).unlink()
    with pytest.raises(ValueError, match="does not exist"):
        bsr.render(root)


def test_the_real_doc_is_in_sync():
    # The gate itself, run against this repo — `--check` exits 0.
    assert bsr.main(["--check"]) == 0


def test_it_lists_every_schema(tmp_path):
    # Known Issue 53: the registry listed agents, skills, scripts and data files but not
    # `schemas/`, so a reader looking for the contract a report must pass found nothing.
    root = tree(tmp_path)
    (root / "schemas").mkdir()
    for name in ("board.schema.json", "queries.schema.json"):
        (root / "schemas" / name).write_text("{}\n", encoding="utf-8")
    (root / "schemas/README.txt").write_text("not a schema\n", encoding="utf-8")
    out = written(root)
    assert "## Schemas — 2" in out
    assert "- `schemas/board.schema.json`" in out and "- `schemas/queries.schema.json`" in out
    assert "README.txt" not in out, "only *.json files are schemas"


def test_every_check_all_gate_is_in_the_gate_table():
    # The gate table is hand-maintained; `check:all` is the list that actually gates. A gate
    # added to the chain without a row here is a gate the registry says does not exist.
    import re
    scripts = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
    chained = re.findall(r"npm run ([\w:-]+)", scripts["check:all"])
    run = {p for name in chained
           for p in re.findall(r"python3 (scripts/[\w./-]+\.py)", scripts[name])}
    missing = sorted(run - {path for path, _ in bsr.GATES})
    assert missing == [], f"check:all runs these, but GATES does not list them: {missing}"
