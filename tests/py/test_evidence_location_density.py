"""Location head-term ceilings scale with the page's length, on board block 4c's own counter.

Known Issue 99, option (a), the user's pick on the answer board (2026-10-07, batch
2026-10-07-research-board-blue-staffy-puppies-manchester-uk q12 (a)): "Limits that scale
with the page's length, on the board's own counter (London fits under every one, so its
special entry can go)". The method is docs/reports/ki99-location-calibration-2026-10-07.md
section 4 (a):

- a location page's head terms are counted with `term_density.count_terms`, the counter
  board block 4c uses (its scope, its tokeniser), not the gate's regexes;
- each ceiling is the top of block 4c's leader band: the highest competitor density per
  1,000 words in the pooled competitor bodies (listings counted, breeder ruling q02,
  2026-10-02), times the page's own word count from the same counter, rounded as block 4c
  rounds its bands;
- the densities are numbers in data/quality/evidence-budgets.json (`location_density`),
  measured on the competitor pool, never computed from London's own page.

Every other page type keeps its fixed counts and its regex counter.
"""
import copy
import datetime
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as ea  # noqa: E402
import term_density as td  # noqa: E402

LIVE = json.loads((ROOT / "data/quality/evidence-budgets.json").read_text(encoding="utf-8"))
REPORT = "docs/reports/ki99-location-calibration-2026-10-07.md"
LONDON = "uk-locations/blue-staffy-puppies-london"
MANCHESTER = "uk-locations/blue-staffy-puppies-manchester-uk"
BUILT_LONDON = ROOT / "dist" / LONDON / "index.html"
HEAD_TERMS = ["blue staffy", "staffy puppies", "staffordshire bull terrier",
              "puppies for sale", "city", "uk"]
# The report's section 4 (a) figures, per 1,000 words.
REPORTED = {"blue staffy": 4.38, "staffy puppies": 4.72, "staffordshire bull terrier": 28.49,
            "puppies for sale": 3.31, "city": 17.50, "uk": 7.30}
# The pooled competitor bodies the report measured (section 2): (cache dir, pages, city).
POOL = (("blue-staffy-puppies-manchester-uk", 8, "Manchester"),
        ("blue-staffy-puppies-london", 9, "London"))


def page(body):
    return f"<html><head><title>t</title></head><body><main>{body}</main></body></html>"


def words_page(term, n, total, filler="dog"):
    """A <main> of exactly `total` words (block 4c's word count) carrying `term` n times."""
    used = n * len(term.split())
    assert used <= total
    return page("<p>" + (term + " ") * n + (filler + " ") * (total - used) + "</p>")


def fixture(per_1000, location=None):
    """The live file's shape: one density term, the brand on a fixed count."""
    return {"terms": dict(LIVE["terms"]),
            "budgets": {"location": location or {"bluestaffyuk": 10},
                        "home": {"blue staffy": 20}},
            "location_density": {"calibrated": "2026-10-07", "source": REPORT,
                                 "per_1000_words": per_1000},
            "budgets_by_slug": {}}


# ── the figures live in the budgets file ─────────────────────────────────────
def test_the_densities_live_in_the_budgets_file_with_date_and_source():
    ld = LIVE.get("location_density")
    assert isinstance(ld, dict), "evidence-budgets.json has no location_density block"
    datetime.date.fromisoformat(ld["calibrated"])
    assert REPORT in ld["source"], "the source must name the calibration report"
    assert (ROOT / REPORT).is_file()
    assert ld["per_1000_words"] == REPORTED


def test_every_density_term_has_a_pattern_and_is_not_also_a_fixed_count():
    per = LIVE["location_density"]["per_1000_words"]
    for t in per:
        assert t in LIVE["terms"], t
        assert t not in LIVE["budgets"]["location"], f"{t} is capped twice"


def test_the_densities_are_the_competitor_pool_maxima_never_londons_page():
    """Recounted from the cached competitor bodies with block 4c's counter: each figure is
    the pool's maximum, so none of them can have come from our own built page."""
    pages = []
    for bare, n, city in POOL:
        for i in range(1, n + 1):
            p = ROOT / "data/queries/cache" / bare / f"{i}.html"
            if not p.exists():
                pytest.skip(f"competitor cache not on disk: {p.relative_to(ROOT)}")
            terms = [city if t == "city" else t for t in HEAD_TERMS]
            r = td.count_terms(p.read_text(encoding="utf-8", errors="replace"), terms)
            pages.append({t: r["counts"][city if t == "city" else t] / r["words"] * 1000
                          for t in HEAD_TERMS})
    assert len(pages) == 17
    per = LIVE["location_density"]["per_1000_words"]
    for t in HEAD_TERMS:
        assert per[t] == round(max(p[t] for p in pages), 2), t


# ── the ceiling is density x the page's own words ────────────────────────────
def test_a_page_over_the_density_fails():
    b = fixture({"blue staffy": 10.0})
    html = words_page("blue staffy", 11, 1000)
    assert ea.term_budget(html, "location", b, slug=MANCHESTER) == [("blue staffy", 11, 10)]


def test_a_page_at_or_under_the_density_passes():
    b = fixture({"blue staffy": 10.0})
    assert ea.term_budget(words_page("blue staffy", 10, 1000), "location", b, slug=MANCHESTER) == []


def test_the_ceiling_scales_with_the_pages_own_length():
    b = fixture({"blue staffy": 10.0})
    assert ea.term_budget(words_page("blue staffy", 11, 2000), "location", b, slug=MANCHESTER) == []
    assert ea.term_budget(words_page("blue staffy", 21, 2000), "location", b,
                          slug=MANCHESTER) == [("blue staffy", 21, 20)]


def test_the_ceiling_rounds_as_block_4c_rounds_its_leader_band():
    b = fixture({"blue staffy": 4.38})
    # 4.38 x 1,370 / 1,000 = 6.0006 -> 6; seven fails, six passes
    assert ea.term_budget(words_page("blue staffy", 7, 1370), "location", b,
                          slug=MANCHESTER) == [("blue staffy", 7, 6)]
    assert ea.term_budget(words_page("blue staffy", 6, 1370), "location", b, slug=MANCHESTER) == []


# ── counted with block 4c's counter ──────────────────────────────────────────
def test_the_count_is_block_4cs_count():
    b = fixture({"blue staffy": 1.0})
    html = words_page("Blue Staffy", 30, 1000)
    want = td.count_terms(html, ["blue staffy"])
    assert want["words"] == 1000
    assert ea.term_budget(html, "location", b, slug=MANCHESTER) == [
        ("blue staffy", want["counts"]["blue staffy"], 1)]


def test_block_4cs_tokeniser_not_the_gate_regex():
    """block 4c matches exact tokens: "blue staffies" is not "blue staffy" there."""
    b = fixture({"blue staffy": 1.0})
    assert ea.term_budget(words_page("blue staffies", 50, 1000), "location", b,
                          slug=MANCHESTER) == []


def test_block_4cs_scope_skips_navigation_inside_main():
    b = fixture({"blue staffy": 1.0})
    html = page("<nav>" + "blue staffy " * 40 + "</nav><p>" + "dog " * 1000 + "</p>")
    assert ea.term_budget(html, "location", b, slug=MANCHESTER) == []


def test_the_city_term_is_the_pages_own_city():
    b = fixture({"city": 10.0})
    over = ea.term_budget(words_page("Manchester", 11, 1000), "location", b, slug=MANCHESTER)
    assert over == [("city", 11, 10)]
    assert ea.term_budget(words_page("Leeds", 11, 1000), "location", b, slug=MANCHESTER) == []


def test_a_national_row_has_no_city_density():
    b = fixture({"city": 1.0})
    assert ea.term_budget(words_page("UK", 50, 1000), "location", b,
                          slug="uk-locations/blue-staffy-puppies-uk") == []


def test_a_per_slug_override_still_replaces_a_density_ceiling():
    b = fixture({"blue staffy": 1.0})
    b["budgets_by_slug"][MANCHESTER] = {"_why": "fixture", "blue staffy": 40}
    assert ea.term_budget(words_page("blue staffy", 30, 1000), "location", b, slug=MANCHESTER) == []


def test_the_brand_stays_a_fixed_count_on_location_pages():
    """No competitor writes our brand, so the pool has no density for it."""
    assert "bluestaffyuk" not in LIVE["location_density"]["per_1000_words"]
    b = fixture({"blue staffy": 10.0})
    html = words_page("BlueStaffyUK", 11, 1000)
    assert ea.term_budget(html, "location", b, slug=MANCHESTER) == [("bluestaffyuk", 11, 10)]


# ── other page types are untouched ───────────────────────────────────────────
def test_other_page_types_keep_their_fixed_count_and_regex():
    """`blue staffies` counts for the regex (block 4c would not count it), and the ceiling
    is the fixed 20 whatever the page's length."""
    b = fixture({"blue staffy": 100.0})
    assert ea.term_budget(words_page("blue staffies", 21, 5000), "home", b,
                          slug="index-like") == [("blue staffy", 21, 20)]


def test_the_live_non_location_budgets_are_fixed_counts():
    for page_type, caps in LIVE["budgets"].items():
        for t, c in caps.items():
            assert isinstance(c, int), (page_type, t, c)


# ── London as built ──────────────────────────────────────────────────────────
def test_london_as_built_fits_under_every_density_ceiling_without_an_entry():
    if not BUILT_LONDON.exists():
        pytest.skip("run npm run build first")
    b = copy.deepcopy(LIVE)
    b["budgets_by_slug"].pop(LONDON, None)
    html = BUILT_LONDON.read_text(encoding="utf-8")
    assert ea.term_budget(html, "location", b, slug=LONDON) == []
