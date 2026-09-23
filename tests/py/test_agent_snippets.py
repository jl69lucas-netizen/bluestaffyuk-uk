# tests/py/test_agent_snippets.py — code copied between agents must not drift.
#
# bsuk-competitive-keyword-gap-agent types competitor pages with bsuk-competitor-intel's
# page-type table. The two agents carry that table as code in their fenced python snippets;
# if one is edited and the other is not, the gap list and the intel reports type the same URL
# two ways and nobody notices. The block runs from the locations read to the `kind` helper.
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".claude/agents"
BLOCK = re.compile(r'^rows = json\.load\(open\("data/locations\.json"\)\)\n.*?^kind = lambda path: [^\n]*\n',
                   re.M | re.S)


def page_type_block(name):
    found = BLOCK.findall((AGENTS / name).read_text(encoding="utf-8"))
    assert len(found) == 1, f"{name}: expected one page-type block, found {len(found)}"
    return found[0]


def test_the_keyword_gap_agent_carries_intels_page_type_table_line_for_line():
    intel = page_type_block("bsuk-competitor-intel.md")
    gap = page_type_block("bsuk-competitive-keyword-gap-agent.md")
    assert "TABLE = [" in intel and 'city"].lower().replace(" ", "-")' in intel
    assert gap == intel, "the page-type table differs: change it in intel, then copy it"


def test_the_block_extractor_rejects_a_drifted_copy(tmp_path):
    text = (AGENTS / "bsuk-competitor-intel.md").read_text(encoding="utf-8")
    drifted = text.replace('("faq", [r"faq", r"questions"])', '("faq", [r"faq"])')
    assert drifted != text
    assert BLOCK.findall(drifted)[0] != page_type_block("bsuk-competitor-intel.md")


@pytest.mark.parametrize("name", ["bsuk-competitor-intel.md", "bsuk-competitive-keyword-gap-agent.md"])
def test_each_agent_has_exactly_one_block(name):
    page_type_block(name)
