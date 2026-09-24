"""The project-5 builder skills say what the code does (Known Issue 40).

A builder skill is the instruction a page is built from, and four of Known Issue 40's items
were places where the location builder said something the repo contradicts: its precedence
table stopped at rule 10 while rule 15 governs every city page with a body; it said "no
variant prop" while `Hero` takes four arrangement props; its worked example handed variant
letters to components and gave every city the same counter; and it told the builder to
hand-record a competitor table in a board block the schema does not have. Each test below
reads the skill for the sentence that was wrong and for the one that replaced it, so the fix
cannot quietly revert. The comparison builder gets the same treatment for its section count.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pageboard  # noqa: E402
LOCATION = (ROOT / ".claude/skills/bsuk-location-page-builder/SKILL.md").read_text(encoding="utf-8")
COMPARISON = (ROOT / ".claude/skills/bsuk-comparison-page-builder/SKILL.md").read_text(encoding="utf-8")
BLOG = (ROOT / ".claude/skills/bsuk-blog-post/SKILL.md").read_text(encoding="utf-8")
CHECKLIST = (ROOT / ".claude/skills/bsuk-seo-master-checklist/SKILL.md").read_text(encoding="utf-8")
MD_LINK = re.compile(r"\]\((https?://[^)\s]+)\)")


def norm(text):
    """Whitespace-collapsed, so a phrase a line wrap splits still matches."""
    return " ".join(text.split())


def section(text, heading):
    """The body of the `## heading` section, up to the next `## `."""
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    return text[start:nxt if nxt != -1 else len(text)]


def test_the_precedence_table_cites_rules_15_and_16():
    table = section(LOCATION, "## What wins when this file and something else disagree")
    assert "judgment rules 1–10" not in table
    assert re.search(r"faithful rewrite \(15\)", table), table
    assert re.search(r"per-page hero and counter \(16\)", table), table


def test_the_hero_wording_matches_hero_astro():
    hero = (ROOT / "src/components/kit/Hero.astro").read_text(encoding="utf-8")
    for prop in ("layout", "align", "media", "ledge"):
        assert re.search(r"\b%s\?:" % prop, hero), "Hero.astro no longer declares %s" % prop
        assert "`%s`" % prop in LOCATION, "the builder does not name Hero's `%s` prop" % prop
    assert "pickedStyle" in LOCATION, "the arrangement props come from the board pick"


def test_the_worked_example_hands_no_letter_to_a_component():
    example = section(LOCATION, "## Worked example")
    letter = re.compile(r"`(?:Hero|CounterStrip|TrustStrip|PageNav|InfoCard|Faq|PuppyCard|"
                        r"ContactFormKit|Testimonial)`\s+[a-d]\b")
    assert not letter.findall(example), letter.findall(example)
    assert "pups available · £500 refundable · £200–£350 delivery" not in example, (
        "a counter set written into the example is a counter every city page would share")


def test_every_review_slot_is_a_single_block():
    assert 'Testimonial mode="grid"' not in LOCATION
    assert "never uses one" in norm(section(LOCATION, "## Step 2")), "the grid ruling must be stated"


def test_the_competitor_record_is_the_question_file_not_a_board_block():
    step1 = section(LOCATION, "## Step 1")
    assert "competitor block" not in norm(LOCATION).replace("no competitor block", "")
    assert "| sections | its H2 list, verbatim |" not in step1
    assert "`competitors`" in step1 and "`why_source`" in step1


def test_body_sections_are_labelled_sections():
    assert "data-section-label" in section(LOCATION, "## Step 2")


def test_a_health_test_result_is_not_a_city_page_fact():
    facts = section(LOCATION, "## The facts a city page may state")
    assert "parents-dna-clear" in facts and "NOT FETCHED" in facts
