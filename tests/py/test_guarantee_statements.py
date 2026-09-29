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
    "buy-staffy-puppies-for-sale-uk": ["No Term Is Stated, Because None Is Held"],
    "buy-blue-staffy-puppies-uk": ["No term is stated for a guarantee"],
}
NOW = {
    "index": [f"Every puppy leaves with our written {LOWER}", f"Our {TITLED}", f"Ours is a {LOWER}"],
    "blue-staffy-health-uk": [f"Ours is a {LOWER}, a promise we make", f"Ask Us About Our {TITLED}"],
    "blue-staffy-pup-sale-uk": [f"A {TITLED} With Every Puppy", f"Our {LOWER} is set out below them"],
    "buy-staffy-puppies-for-sale-uk": [f"Our {TITLED}, in Writing", f"Ours is a {LOWER}."],
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


@pytest.mark.parametrize("slug", ["index", "blue-staffy-health-uk", "blue-staffy-pup-sale-uk", "buy-blue-staffy-puppies-uk",
                                  "buy-staffy-puppies-for-sale-uk"])
def test_each_page_reads_the_label_rather_than_typing_it(slug):
    src = (ROOT / "src/pages" / ("index.astro" if slug == "index" else f"{slug}/index.astro")).read_text(encoding="utf-8")
    assert "guaranteeLabel(" in src
    assert "Two-Year Health Guarantee" not in src and "two-year health guarantee" not in src.lower().replace("`", "")


# The ruling covers EVERY line that contradicts the guarantee (coordinator, 2026-09-29): no built
# page anywhere in dist/ may say the guarantee's length is unstated, unconfirmed or absent. The
# board previews (/board-preview/) render the approved board records, which stay as history.
UNSTATED = [
    r"no (?:health )?guarantee length",
    r"state no (?:health )?guarantee",
    r"no guarantee is (?:stated|offered|claimed)",
    r"not (?:yet )?confirmed (?:a|one|any) (?:term|length)",
    r"confirmed no guarantee",
    r"no term is stated",
    r"records a length for one",
    r"guarantee[^.]{0,80}deliberately absent|deliberately absent[^.]{0,80}guarantee",
    r"guarantee length[^.]{0,40}(?:not established|prints nothing)",
    r"not established[^.]{0,20}a guarantee length",
    r"length of the cover is not published",
    r"guarantee_days: null",
]
UNSTATED_RE = re.compile("(?i)" + "|".join(UNSTATED))


def unstated_lines(text):
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text)))
    return [text[max(0, m.start() - 60):m.end() + 40] for m in UNSTATED_RE.finditer(text)]


def test_no_built_page_says_the_guarantee_length_is_unstated():
    dist = ROOT / "dist"
    if not dist.exists():
        pytest.skip("run npm run -s build first")
    pages = [p for p in dist.rglob("*") if p.suffix in (".html", ".txt", ".xml", ".json")
             and "board-preview" not in p.parts]
    assert len(pages) > 50, "examined too few built files to be a pass"
    bad = [f"{p.relative_to(dist)}: {l}" for p in pages for l in unstated_lines(p.read_text(errors="ignore"))]
    assert bad == [], "\n".join(bad)


def test_the_unstated_patterns_fire_on_the_old_lines():
    for old in ["We state no guarantee, because we have not confirmed a term for one.",
                "no guarantee length, no laboratory named, no percentage anywhere",
                "and no file we keep records a length for one",
                "No Term Is Stated, Because None Is Held",
                "We have confirmed no guarantee length and no support period",
                "Where a fact is not established — a guarantee length, a licence number",
                "The length of the cover is not published on this site"]:
        assert unstated_lines(old), old
    assert not unstated_lines("Ours is a two-year health guarantee; no laboratory named, no percentage anywhere.")
