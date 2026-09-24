# tests/py/test_strategy_example.py — pins bsuk-strategy-synthesizer's output format and rules.
#
# tests/py/fixtures/competitors/strategy-example.md is the agent's GREEN run (Task 9 quality
# round) on tests/py/fixtures/competitors/gap-matrix-fixture.md. That matrix was built by
# scripts/gap_matrix.py from fixture reports a, b, c and a BSUK profile that covers York only —
# fixture research, not real. The example's ## Sources were trimmed to the files its checked
# figures come from, and one note about a fixture-only profile mismatch was removed. The test
# lays those files out at their research paths in a scratch root and runs
# scripts/strategy_cite_check.py on the example, so a checker change that would reject the
# agent's format fails here, in CI. It also pins the key rule phrases of the agent text.
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


def test_the_agent_carries_its_key_rules():
    agent = " ".join(AGENT.read_text(encoding="utf-8").split())
    for phrase in (
        "Exactly TWO strategies",                       # two strategies, never one or three
        "names the pick's own downside",                # the downside
        "never cite traffic",                           # GSC/GA4 not fetched until project 6
        "is a rebuild of that URL (project 5), never a new page",  # stub rows
        "A quantity from 1900 to 2099 takes a comma",   # the comma rule
        "say it **without a number**",                  # self-made counts: words, not numbers
        'never spelled out ("seventeen"',
        "WHY below three sourced figures",              # thin research
        "the profile wins",
        "Tier 5 is never a link",
        "compared within one `page_source.kind` only",
        "the file's own date (older than 30 days → STALE)",  # keyword-gap freshness
        "No row-number column",                          # row numbers ≥10 are checked figures
        "never from old page copy in `data/locations.json` or `data/page-map.json`",  # business facts
    ):
        assert phrase in agent, phrase


def test_the_agent_says_strategy_a_and_b_are_checked():
    # Known Issue 49: the check now reads Strategy A and B, so the agent must not say it doesn't.
    agent = " ".join(AGENT.read_text(encoding="utf-8").split())
    assert "where the check does not look" not in agent
    assert "the check reads them as well" in agent
    assert ("checks every figure under `## Strategy A`, `## Strategy B`, `## Recommendation` "
            "and `## Concrete Artifact`") in agent
    assert "a figure in Strategy A or B, the Recommendation or the Concrete Artifact" in agent


def test_the_agent_keeps_locked_facts_out_of_a_b_and_the_pick():
    # Known Issue 49: Strategy A and B are checked, so a business fact no source prints fails there too.
    agent = " ".join(AGENT.read_text(encoding="utf-8").split())
    assert ("keep them out of Strategy A, Strategy B and the pick unless a listed source prints "
            "them too") in agent
    assert "keep them out of the pick unless" not in agent
