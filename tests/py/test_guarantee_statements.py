"""The user's ruling (2026-09-29, "Correct them now"): the six statements on four built pages
that said no guarantee length is stated now state the two-year health guarantee, read from
data/settings.json `guarantee_label` (answer board q07). The pages are hand-written rebuilt
pages (data/facts/rebuilt.json; README "Generated vs hand-authored"), so each page file reads the
label through src/lib/site.ts `guaranteeLabel()`; the FAQ answer is static JSON, pinned here to
the label.
"""
import html
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
LABEL = SETTINGS["guarantee_label"]            # "Two-year health guarantee"
LOWER = LABEL[0].lower() + LABEL[1:]           # "two-year health guarantee"
TITLED = "Two-Year Health Guarantee"           # the label as T() titles it in a heading

GONE = {
    "index": ["The length of the cover is not published on this site until the figure is confirmed",
              "No Guarantee Length Is Printed Here"],
    "blue-staffy-health-uk": ["There is no guarantee length anywhere on this site",
                              "The Guarantee Row Is Absent, Not Overlooked"],
    "blue-staffy-pup-sale-uk": ["No Health Guarantee Is Stated"],
    "buy-blue-staffy-puppies-uk": ["No term is stated for a guarantee"],
}
NOW = {
    "index": [f"Every puppy leaves with our written {LOWER}", f"Our {TITLED}", f"Ours is a {LOWER}"],
    "blue-staffy-health-uk": [f"Ours is a {LOWER}, a promise we make", f"Ask Us About Our {TITLED}"],
    "blue-staffy-pup-sale-uk": [f"And Our {TITLED}"],
    "buy-blue-staffy-puppies-uk": [f"What we do promise is our {LOWER}"],
}


def page(slug):
    f = ROOT / "dist" / ("index.html" if slug == "index" else f"{slug}/index.html")
    if not f.exists():
        pytest.skip("run npm run -s build first")
    return re.sub(r"\s+", " ", html.unescape(f.read_text(encoding="utf-8")))


def test_the_label_is_the_one_the_pages_title():
    assert LABEL == "Two-year health guarantee"
    assert TITLED.lower() == LABEL.lower()


@pytest.mark.parametrize("slug", sorted(GONE))
def test_the_absence_statements_are_gone_and_the_guarantee_is_stated(slug):
    text = page(slug)
    for old in GONE[slug]:
        assert old not in text, f"{slug} still says: {old}"
    for new in NOW[slug]:
        assert new in text, f"{slug} does not say: {new}"


def test_the_faq_answer_names_the_guarantee_from_the_label():
    rows = {r["id"]: r for r in json.loads((ROOT / "data/faq.json").read_text(encoding="utf-8"))}
    a = rows["home-health-guarantee"]["a"]
    assert "{guarantee_label_lc}" in a and "not published" not in a
    assert rows["home-health-guarantee"]["source"] == "data/settings.json"


@pytest.mark.parametrize("slug", ["index", "blue-staffy-health-uk", "blue-staffy-pup-sale-uk", "buy-blue-staffy-puppies-uk"])
def test_each_page_reads_the_label_rather_than_typing_it(slug):
    src = (ROOT / "src/pages" / ("index.astro" if slug == "index" else f"{slug}/index.astro")).read_text(encoding="utf-8")
    assert "guaranteeLabel(" in src
    assert "Two-Year Health Guarantee" not in src and "two-year health guarantee" not in src.lower().replace("`", "")
