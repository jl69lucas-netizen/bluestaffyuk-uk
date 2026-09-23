# tests/py/test_strategy_example.py — pins bsuk-strategy-synthesizer's output format.
#
# tests/py/fixtures/competitors/strategy-example.md is the Task 9 GREEN run of the agent on
# the fixture gap matrix (tests/py/fixtures/competitors/gap-matrix-fixture.md, itself built by
# scripts/gap_matrix.py from fixture reports — fixture research, not real). Its ## Sources were
# trimmed to the files its checked figures come from. The test lays those files out at their
# research paths in a scratch root and runs scripts/strategy_cite_check.py on the example, so a
# change to the checker that would reject the agent's format fails here, in CI.
import pathlib
import re
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
FIX = REPO / "tests/py/fixtures/competitors"
EXAMPLE = FIX / "strategy-example.md"
SCRIPT = REPO / "scripts/strategy_cite_check.py"
AGENT = REPO / ".claude/agents/bsuk-strategy-synthesizer.md"


def _root(tmp_path):
    (tmp_path / "docs/research").mkdir(parents=True)
    (tmp_path / "data").mkdir()
    shutil.copy(FIX / "gap-matrix-fixture.md", tmp_path / "docs/research/gap-matrix-2026-09-24.md")
    for name in ("locations.json", "page-map.json"):
        shutil.copy(REPO / "data" / name, tmp_path / "data" / name)
    return tmp_path


def _check(strategy, root):
    return subprocess.run([sys.executable, str(SCRIPT), str(strategy), "--root", str(root)],
                          capture_output=True, text=True)


def test_the_example_passes_the_cite_check(tmp_path):
    r = _check(EXAMPLE, _root(tmp_path))
    assert r.returncode == 0, r.stdout
    last = r.stdout.strip().splitlines()[-1]
    m = re.search(r"(\d+) sources?, (\d+) figures? checked, 0 problems", last)
    assert m and int(m.group(1)) == 3 and int(m.group(2)) >= 3, last


def test_the_example_has_the_agents_shape():
    text = EXAMPLE.read_text(encoding="utf-8")
    heads = [h for h in re.findall(r"^## (.+)$", text, re.M)]
    assert len([h for h in heads if h.startswith("Strategy ")]) == 2
    assert len([h for h in heads if h.startswith("Recommendation")]) == 1
    assert heads[-1] == "Sources"  # Sources is last
    pick = text.split("## Recommendation", 1)[1].split("## Sources", 1)[0]
    assert "downside" in pick.lower()
    assert text.splitlines()[0].startswith(("STALE:", "MISSING:", "fresh:"))


def test_a_changed_figure_in_the_example_fails(tmp_path):
    root = _root(tmp_path)
    text = EXAMPLE.read_text(encoding="utf-8")
    pick_at = text.index("## Recommendation")
    bad = text[:pick_at] + text[pick_at:].replace("3/3", "4/5", 1)
    assert bad != text
    p = tmp_path / "strategy.md"
    p.write_text(bad, encoding="utf-8")
    r = _check(p, root)
    assert r.returncode == 1 and "figure 4/5 is in no listed source" in r.stdout, r.stdout


def test_the_agent_names_the_check_and_the_output_sections():
    agent = AGENT.read_text(encoding="utf-8")
    for s in ("scripts/strategy_cite_check.py", "## Strategy A", "## Strategy B",
              "## Recommendation", "## Concrete Artifact", "## Sources"):
        assert s in agent, s
