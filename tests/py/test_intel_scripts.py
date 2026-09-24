# tests/py/test_intel_scripts.py — runs the code embedded in .claude/agents/bsuk-competitor-intel.md.
#
# The intel reports are only as good as the snippets that count them: the page-type table (shared
# line for line with bsuk-competitive-keyword-gap-agent, see test_agent_snippets.py), the map
# classifier and the homepage measures. Each is extracted from the agent file exactly as a reader
# would run it, and run here on small inputs (Known Issue 51).
import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
AGENT = REPO / ".claude/agents/bsuk-competitor-intel.md"
BLOCK = re.compile(r'^rows = json\.load\(open\("data/locations\.json"\)\)\n.*?^kind = lambda path: [^\n]*\n',
                   re.M | re.S)


@pytest.fixture
def kind(monkeypatch):
    """intel's `kind(path)`: the shared page-type table, run against the real data/locations.json."""
    monkeypatch.chdir(REPO)
    ns = {"json": json, "re": re}
    exec(BLOCK.findall(AGENT.read_text(encoding="utf-8"))[0], ns)
    return ns["kind"]


@pytest.mark.parametrize("path,want", [
    ("/careers/", None),                                   # not care-guide: whole words only
    ("/about-us/careers/", "about"),
    ("/preview/", None),                                   # not reviews
    ("/reviews/", "reviews"),
    ("/customer-testimonials/", "reviews"),
    ("/adviceandwelfare/costofliving/petcalculator", None),  # not price
    ("/puppy-prices/", "price"),
    ("/pricing/", "price"),
    ("/healthy-treats/", None),                            # not health
    ("/health-testing/", "health"),
    ("/pet-advice/staffy-care.html", "care-guide"),        # a dot ends a word
    ("/staffy_grooming/", "care-guide"),                   # so does an underscore
    ("/contact-us/", "contact"),
    ("/contactus/", "contact"),
    ("/enquiry-form/", "contact"),
    ("/faqs/", "faq"),
    ("/breeders/", None),                                  # breed is a whole word, never breeders
    ("/breed-guide/", "breed-guide"),
    ("/litters/", "listing"),
    ("/pups/", "listing"),
    ("/2025/09/our-news/", "blog"),
    ("/uk-locations/blue-staffy-puppies-leeds/", "city"),
    ("/uk-locations/blue-staffies-newcastle-under-lyme/", "city"),
])
def test_page_types_match_whole_words(kind, path, want):
    assert kind(path) == want


@pytest.mark.parametrize("path", ["/blog/staffy-vs-pitbull/", "/staffy-versus-pitbull/",
                                  "/blue-staffy-vs-pitbull-london/", "/news/2025/staffy-vs-bully/"])
def test_a_comparison_path_is_a_comparison_before_any_other_row(kind, path):
    # one rule for both agents: the keyword-gap agent no longer puts comparison first on its own
    assert kind(path) == "comparison"


def test_the_keyword_gap_agent_has_no_comparison_override_of_its_own():
    gap = (REPO / ".claude/agents/bsuk-competitive-keyword-gap-agent.md").read_text(encoding="utf-8")
    assert 're.search(r"-vs-|versus", path)' not in gap
