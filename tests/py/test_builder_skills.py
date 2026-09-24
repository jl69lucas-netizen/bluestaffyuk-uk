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
import copy
import json
import pathlib
import re
import sys

import pytest

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
    assert re.search(r"per-page hero and counter, and a refresh delta on every section \(16\)",
                     norm(table)), table


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


def arrangement_paragraph():
    """The paragraph that says which props come from the board pick."""
    start = LOCATION.index("**No `variant` prop and no letter")
    return norm(LOCATION[start:LOCATION.index("\n\n", start)])


def test_the_board_pick_arranges_hero_and_counter_but_never_a_city_review():
    para = arrangement_paragraph()
    assert "Testimonial" not in para.replace('Testimonial mode="single"', ""), (
        "a board-picked review style can be a grid; a city review is always single")
    assert 'Testimonial mode="single"' in para and "`S1`" in para and "styles: []" not in para
    assert "layout={pick.layout.hero}" in para, "the hero's layout is the style's `hero` axis"
    for axis in ("align", "media", "ledge", "tiles", "label"):
        assert "%s={pick.layout.%s}" % (axis, axis) in para, axis


def test_a_review_section_cannot_offer_no_styles():
    """Why the skill says S1 and not `styles: []`: the board schema makes every kit shape,
    reviews included, offer three styles, so an empty list is not a way out of the grid."""
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "schemas/board.schema.json").read_text(encoding="utf-8"))
    board = json.loads((ROOT / "data/boards/blue-staffy-health-uk.json").read_text(encoding="utf-8"))
    jsonschema.validate(copy.deepcopy(board), schema)
    review = next(s for s in board["sections"] if s["shape"] == "reviews")
    review["styles"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(board, schema)


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


def test_the_comparison_builder_derives_its_section_count():
    assert not re.search(r"22[–-]25|\b22[- ]section", COMPARISON)
    assert "section_target" in COMPARISON


def test_the_comparison_builder_has_no_source_site_polish_leftovers():
    for leftover in ("cvt-", "CvT", "CvM", "CvC", "MvF", "blue-brindle", "Blue-Brindle",
                     "vs-french", "map-pin"):
        assert leftover not in COMPARISON, leftover
    polish = section(COMPARISON, "## 12.") + section(COMPARISON, "## 13.")
    for route in ("/blue-staffy-uk-breeders/", "/buy-blue-staffy-puppies-uk/"):
        assert route not in polish, route


def test_the_comparison_layout_rules_name_no_fixed_header_or_toc_size():
    layout = section(COMPARISON, "## 11.")
    for fixed in ("96px", "200px"):
        assert fixed not in layout, fixed


def test_the_blog_builder_uses_the_link_library_and_the_registry():
    assert "docs/reference/external-link-library.md" in BLOG
    assert "data/competitors.json" in BLOG
    assert "This file governs in any conflict" not in BLOG


def test_the_blog_builder_has_no_source_site_leftovers():
    for leftover in ("best-place", "crate-setup", "Batch-2", "assets/BSUK-BLOG-POSTS",
                     "quality=82", "1408×768", "media=print", "interaction-deferred",
                     "/blog/uk-staffordshire", "FAQ / 3 zones", "all 9 posts",
                     "the other 8 posts"):
        assert leftover not in BLOG, leftover
    assert "`/<slug>/`" in BLOG
    assert "sources.serp_google" not in BLOG
    assert "data/queries/raw/<slug>/serp_google.json" in BLOG
    for fact in ("src/content.config.ts", "SiteFooterKit", "POST_EXEMPT_CHECKS"):
        assert fact in BLOG, fact
    assert "confirm ≥5 H5 / ≥5 H6 still hold" not in BLOG
    delivery = ("UK home delivery by DEFRA-approved transport, priced by distance, "
                "£200–£350 · or collect in Carlisle")
    assert BLOG.count(delivery) >= 2


def test_the_checklist_external_links_are_library_rows():
    """Known Issue 40: the checklist's external-link list was the source site's US set (AVMA,
    AAHA, ASPCA, the FTC, Chewy). Every URL it lists now must be a row of
    docs/reference/external-link-library.md, the list scripts/pageboard.py enforces on boards."""
    start = CHECKLIST.index("#### B. External Links")
    block = CHECKLIST[start:CHECKLIST.index("#### C.", start)]
    urls = MD_LINK.findall(block)
    assert len(urls) >= 10, urls
    library = pageboard.library_urls()
    assert library, "docs/reference/external-link-library.md is missing"
    missing = [u for u in urls if pageboard.normalise_url(u) not in library]
    assert missing == [], "not rows of the external-link library: %s" % missing
