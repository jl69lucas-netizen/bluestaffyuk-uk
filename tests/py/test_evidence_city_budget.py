"""The city term is the page's own city, and the brand has a ceiling (CAG parity audit D2).

data/quality/evidence-budgets.json hard-coded its city term to `glasgow` — the city the
breeder has LEFT (Known Issue 16) — so 27 of the 28 city pages in data/locations.json had no
ceiling on their own city, and `bluestaffyuk` had no ceiling anywhere. CAG §8 counts the
city 5–8 times on a location page and the brand 5–10 times on any page. The fix is one
`{city}` term that scripts/evidence_audit.py resolves per slug from data/locations.json,
and a `bluestaffyuk` term budgeted on every page type.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as ea  # noqa: E402

LIVE = json.loads((ROOT / "data/quality/evidence-budgets.json").read_text(encoding="utf-8"))
LOCATIONS = json.loads((ROOT / "data/locations.json").read_text(encoding="utf-8"))


def page(body):
    return f"<html><head><title>t</title></head><body><main>{body}</main></body></html>"


def budgets():
    """The live file's shape, cut down to the two terms under test."""
    return {"terms": {"city": LIVE["terms"]["city"], "bluestaffyuk": LIVE["terms"]["bluestaffyuk"]},
            "budgets": {"location": {"city": 8, "bluestaffyuk": 10},
                        "interior": {"bluestaffyuk": 10}},
            "budgets_by_slug": {}}


def test_the_live_budgets_name_no_former_city():
    assert "glasgow" not in LIVE["terms"]
    for page_type, caps in LIVE["budgets"].items():
        assert "glasgow" not in caps, page_type


def test_the_city_term_is_resolved_per_slug_and_capped_on_location_pages():
    assert LIVE["terms"]["city"] == "{city}"
    # Since Known Issue 99 option (a) (user, 2026-10-07) the live city ceiling is a density
    # (tests/py/test_evidence_location_density.py); the fixed-count path is pinned below on
    # the budgets() fixture.
    assert LIVE["location_density"]["per_1000_words"]["city"] > 0


def test_every_page_type_budgets_the_brand():
    assert re.fullmatch(LIVE["terms"]["bluestaffyuk"], "BlueStaffyUK", re.I)
    missing = [t for t, caps in LIVE["budgets"].items() if "bluestaffyuk" not in caps]
    assert missing == [], f"page types with no brand ceiling: {missing}"


def test_a_city_page_over_its_own_city_budget_fails():
    html = page("<p>" + "Aberdeen families. " * 9 + "</p>")
    over = ea.term_budget(html, "location", budgets(), slug="uk-locations/blue-staffy-puppies-aberdeen")
    assert over == [("city", 9, 8)]


def test_another_citys_name_is_not_this_pages_city():
    html = page("<p>" + "Aberdeen families. " * 9 + "</p>")
    assert ea.term_budget(html, "location", budgets(), slug="uk-locations/blue-staffy-puppies-dundee") == []


def test_a_hyphenated_city_matches_its_spaced_spelling():
    html = page("<p>" + "Newcastle under Lyme buyers. " * 9 + "</p>")
    over = ea.term_budget(html, "location", budgets(), slug="uk-locations/blue-staffies-newcastle-under-lyme")
    assert over == [("city", 9, 8)]


def test_a_bracketed_note_is_not_part_of_the_city():
    assert ea.city_for("uk-locations/staffy-breeding-dogs-glasgow") == "Glasgow"


def test_a_national_row_has_no_city_term():
    # `city: "UK"` rows are the country; the `uk` head term already budgets that word
    assert ea.city_for("uk-locations/blue-staffy-puppies-uk") is None
    html = page("<p>" + "UK buyers. " * 20 + "</p>")
    assert ea.term_budget(html, "location", budgets(), slug="uk-locations/blue-staffy-puppies-uk") == []


def test_a_page_outside_the_city_cluster_has_no_city_term():
    assert ea.city_for("index") is None
    assert ea.city_for("uk-locations") is None


def test_every_location_row_resolves_to_a_city_or_is_national():
    for row in LOCATIONS:
        city = ea.city_for("uk-locations/" + row["slug"])
        assert city is None or city in row["city"], row["slug"]
        if row["city"] != "UK":
            assert city, row["slug"]


def test_the_brand_is_capped():
    html = page("<p>" + "BlueStaffyUK raises them. " * 11 + "</p>")
    assert ea.term_budget(html, "interior", budgets(), slug="some-new-page") == [("bluestaffyuk", 11, 10)]


BUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("slug", BUILT)
def test_the_twelve_built_pages_pass_their_brand_budget_as_built(slug):
    """The brand term is new, so each built page is held at its count AS BUILT through a
    budgets_by_slug override (the Known Issue 34 ratchet), never failed retroactively."""
    built = ROOT / "dist" / ("index.html" if slug == "index" else f"{slug}/index.html")
    if not built.exists():
        pytest.skip("run npm run build first")
    html = built.read_text(encoding="utf-8")
    over = [t for t, n, c in ea.term_budget(html, ea.page_type_for(slug), LIVE, slug) if t == "bluestaffyuk"]
    assert over == [], slug


def test_city_pattern_keeps_word_boundaries():
    # `York` must not match inside `Yorkshire`, but a hyphen is a word boundary (`York-based`)
    assert re.findall(ea.city_pattern("York"), "North Yorkshire, York-based, York", re.I) == ["York", "York"]
    # a name with no words would give r"\b\b", which matches everywhere: refuse it
    with pytest.raises(ValueError):
        ea.city_pattern("-")
