"""The user's ruling (2026-09-29, "Correct them now"): every line on the built pages that said
no guarantee length is stated now states the two-year health guarantee, read from
data/settings.json `guarantee_label` (answer board q07): fourteen lines on six pages (six on
four pages in de8853f, eight more on five in e8dde15), with copy fixes in 9830276. The pages are hand-written rebuilt
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
              "No Guarantee Length Is Printed Here", f"Ours is a {LOWER}, and it is written down like the rest"],
    "blue-staffy-health-uk": ["There is no guarantee length anywhere on this site",
                              "The Guarantee Row Is Absent, Not Overlooked",
                              "answered just below the list", "This is where you would have looked for it"],
    "blue-staffy-pup-sale-uk": ["No Health Guarantee Is Stated", f"A {TITLED} With Every Puppy"],
    "buy-staffy-puppies-for-sale-uk": ["No Term Is Stated, Because None Is Held"],
    "buy-blue-staffy-puppies-uk": ["No term is stated for a guarantee"],
}
NOW = {
    # The FAQ answer now says the length once, inside the cover clause (review M1, 2026-09-29):
    # "our written health guarantee, which covers … for two years …".
    "index": ["Every puppy leaves with our written health guarantee, which covers", f"Our {TITLED}",
              "Every puppy goes home with it on paper"],
    "blue-staffy-health-uk": [f"Ours is a {LOWER}, a promise we make", f"Ask Us About Our {TITLED}",
                              f"asked how long the health guarantee lasts: ours is a {LOWER}.",
                              "The old tenth row would have sat here. It covers health issues and birth defects from the day your puppy comes home. Ask us for the full wording before you pay a deposit."],
    "blue-staffy-pup-sale-uk": [f"Not an Item, a Promise: Our {TITLED}", f"Our {LOWER} is set out below them",
                                "it is a promise we make with every puppy"],
    "buy-staffy-puppies-for-sale-uk": [f"Our {TITLED}, in Writing",
                                       f"Ours is a {LOWER}, and it is written down. It covers health issues and birth defects from the day your puppy comes home. Ask us for the full wording before you pay a deposit."],
    "buy-blue-staffy-puppies-uk": [f"What we do promise is our {LOWER}; ask us for its full wording before you pay a deposit."],
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
    assert "{guarantee_phrase}" in a and "not published" not in a
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
    r"no health guarantee is",
    # "we / this site state(s) no guarantee" — but not "we state no guarantee about temperament"
    r"\b(?:we|this (?:site|page))\s+states? no (?:health )?guarantee(?!\s+(?:about|on|that|for)\b)",
    # "no guarantee is offered" only when it is ours ("A classified ad: no guarantee is offered" is not)
    r"\b(?:we|our|us|this (?:site|page))\b[^.]{0,40}\bno guarantee is (?:stated|offered|claimed)",
    r"not (?:yet )?confirmed (?:a|one|any) (?:term|length)",
    r"confirmed no guarantee",
    r"no term is stated",
    r"records a length for one",
    r"guarantee (?:row|length|term)[^.]{0,20}(?:absent|not fetched|unconfirmed)",
    r"guarantee[^.]{0,60}\bnot fetched|\bnot fetched[^.]{0,60}guarantee",
    r"guarantee[^.]{0,60}\bnot (?:yet )?(?:confirmed|established)|\bnot (?:yet )?(?:confirmed|established)[^.]{0,60}guarantee",
    r"guarantee[^.]{0,60}\bunconfirmed|\bunconfirmed[^.]{0,60}guarantee",
    r"guarantee[^.]{0,80}deliberately absent|deliberately absent[^.]{0,80}guarantee",
    r"guarantee length[^.]{0,40}(?:not established|prints nothing)",
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
    assert unstated_lines("We state no guarantee, because we have not confirmed a term for one.")


def test_no_page_promises_to_send_the_wording():
    """Re-review, item 3 (rule 9): data/settings.json `guarantee_note` says "Ask us for the full
    terms before you pay a deposit." A page may not promise more (that we SEND the wording)."""
    dist = ROOT / "dist"
    if not dist.exists():
        pytest.skip("run npm run -s build first")
    send = re.compile(r"(?i)\bwe (?:will )?send (?:you )?(?:its|the) full wording")
    bad = [str(p.relative_to(dist)) for p in dist.rglob("*.html") if send.search(p.read_text(errors="ignore"))]
    assert bad == [], bad


STALE_SOURCE = re.compile(r"(?i)guarantee_days`?:?\s*null|guarantee_days`? is null|holds guarantee_days|"
                          r"no (?:health )?guarantee (?:of any length|length)|guarantee[^.]{0,40}\bNOT (?:claimed|restated)|"
                          r"no guarantee (?:is )?(?:offered|stated)|no length may be written|guarantee length[^.]{0,30}NOT FETCHED")


def test_no_page_source_comment_says_the_guarantee_is_unset():
    """Re-review, item 4: a page file's comments that still say the guarantee is not stated sit
    on top of corrected copy and send the next editor the wrong way."""
    bad = []
    for f in sorted((ROOT / "src/pages").rglob("*.astro")):
        text = f.read_text(encoding="utf-8")
        # Join a comment's wrapped lines so a clause split across two lines is still read whole.
        flat = re.sub(r"\n\s*(?://|\*)?\s*", " ", text)
        bad += [f"{f.relative_to(ROOT)}: …{flat[max(0, m.start() - 50):m.end() + 30]}…" for m in STALE_SOURCE.finditer(flat)]
    assert bad == [], "\n".join(bad)


def test_the_unstated_patterns_cover_both_directions():
    """Re-review, item 6. Two old headings injected into a page that never carried them (the
    breed guide) must fail; sentences that only resemble the claim must pass."""
    f = ROOT / "dist/uk-staffordshire-bull-terrier-guide/index.html"
    if not f.exists():
        pytest.skip("run npm run -s build first")
    clean = f.read_text(encoding="utf-8")
    assert unstated_lines(clean) == []
    for heading in ["No Health Guarantee Is Stated", "The Guarantee Row Is Absent, Not Overlooked"]:
        assert unstated_lines(clean.replace("</main>", f"<h5>{heading}</h5></main>", 1)), heading
    for fires in ["Our guarantee length is NOT FETCHED.", "The guarantee term is unconfirmed.",
                  "The health guarantee is not yet confirmed.", "We have not established a guarantee length.",
                  "This site offers no guarantee: no guarantee is offered by us."]:
        assert unstated_lines(fires), fires
    for legit in ["We state no guarantee about temperament, because every dog is its own.",
                  "A classified ad: no guarantee is offered, and no paperwork either.",
                  "Ours is a two-year health guarantee; no laboratory named, no percentage anywhere."]:
        assert unstated_lines(legit) == [], legit
