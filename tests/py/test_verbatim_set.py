"""verbatim_set_check.py — working rule 15's gate: a rebuilt page keeps the old page's words.

`facts_preserved_check.py` asks whether a rebuilt page still carries the migrated page's
FACTS. This asks whether it still carries its WORDING — the H1, the keyword headings, the
first paragraph under each of them, the FAQ questions and the image alts. A page can keep
every fact and lose every phrase it ranked for, which is the hole rule 15 closes.

The unit tests below run on a fixture body, so they say what the rule IS. The last group
runs against the real data files and the real excluded list, so a set that was never taken
or an exclusion that quietly grew cannot pass unnoticed.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import verbatim_set_check as V  # noqa: E402

KEYWORDS = ["staffy", "puppies", "breeder", "carlisle"]

MIGRATED = """
<h1>Our Blue Staffy Promise</h1>
<h2>Blue Staffy Puppies in Carlisle</h2>
<p>Every litter is raised in the kitchen, not a kennel.</p>
<p>A second paragraph nobody has to carry.</p>
<h3>Boosters</h3>
<p>Not a keyword heading, so neither this nor its heading is in the set.</p>
<h2>Why our breeder standards matter</h2>
<h3>A sub-heading with no prose above it</h3>
<p>The first paragraph under the sub-heading.</p>
<div class="uagb-faq">
  <p class="uagb-question"><strong>Are the parents health tested?</strong></p>
  <p>Yes.</p>
</div>
<p class="quiz-question">How much time can you dedicate to a dog?</p>
<img src="/images/pup.webp" alt="A blue Staffy puppy on a lawn">
<img src="/images/spacer.gif" alt="">
"""


def vset():
    return V.extract(MIGRATED, KEYWORDS)


# ── extraction ────────────────────────────────────────────────────────────────────────────

def test_the_h1_is_the_first_h1():
    assert vset()["h1"] == "Our Blue Staffy Promise"


def test_only_headings_carrying_a_target_keyword_are_in_the_set():
    texts = [h["text"] for h in vset()["headings"]]
    assert texts == ["Blue Staffy Puppies in Carlisle", "Why our breeder standards matter"]
    assert "Boosters" not in texts


def test_a_headings_opening_is_the_first_paragraph_under_it_and_not_the_second():
    openings = {o["heading"]: o["text"] for o in vset()["openings"]}
    assert openings["Blue Staffy Puppies in Carlisle"] == \
        "Every litter is raised in the kitchen, not a kennel."


def test_an_opening_is_not_borrowed_from_across_the_next_heading():
    """"Why our breeder standards matter" has a sub-heading and no prose of its own, so it
    reports no opening rather than claiming the sub-heading's paragraph."""
    assert [o["heading"] for o in vset()["openings"]] == ["Blue Staffy Puppies in Carlisle"]


def test_faq_questions_come_from_the_question_elements_and_a_quiz_is_not_one():
    qs = vset()["faq_questions"]
    assert qs == ["Are the parents health tested?"]


def test_every_image_alt_is_carried_including_a_deliberately_empty_one():
    assert vset()["alts"] == [
        {"src": "/images/pup.webp", "alt": "A blue Staffy puppy on a lawn"},
        {"src": "/images/spacer.gif", "alt": ""},
    ]


def test_target_keywords_are_the_title_words_the_site_terms_and_the_city():
    kws = V.target_keywords("index")
    assert "staffordshire bull terrier" in kws and "puppies" in kws
    assert "carlisle" in kws
    assert "the" not in kws and "and" not in kws


# ── the check ─────────────────────────────────────────────────────────────────────────────

def built(main):
    return f"<html><body><header><h2>Blue Staffy Puppies in Carlisle</h2></header>" \
           f"<main>{main}</main></body></html>"


FAITHFUL = built("""
<h1>Our Blue Staffy Promise</h1>
<h2>Blue Staffy Puppies in Carlisle</h2>
<p>Every litter is raised in the kitchen, not a kennel. And here is fresh prose after it.</p>
<h2>Why Our Breeder Standards Matter</h2>
<p>Fresh prose.</p>
<details><summary><h3>Are the parents health tested?</h3></summary><p>Yes.</p></details>
<img src="/images/pup.webp" alt="A blue Staffy puppy on a lawn">
<img src="/images/spacer.gif" alt="">
""")


def test_a_faithful_page_passes_with_nothing_changed():
    examined, changed, misses = V.judge(vset(), FAITHFUL, {})
    assert misses == []
    assert (examined, changed) == (7, 0)


def test_heading_case_is_the_pages_own_because_rules_headings_md_fixes_it():
    """"Why our breeder standards matter" reaches the page title-cased. The WORDING is what
    rule 15 asks for; the casing belongs to rules/headings.md and is applied at render."""
    _, _, misses = V.judge(vset(), FAITHFUL, {})
    assert not any("Breeder Standards" in m for m in misses)


def test_a_reworded_heading_with_no_record_row_is_reported_missing():
    page = FAITHFUL.replace("<h2>Blue Staffy Puppies in Carlisle</h2>",
                            "<h2>Puppies Near You</h2>")
    _, changed, misses = V.judge(vset(), page, {})
    assert changed == 0
    assert any("missing heading" in m and "Carlisle" in m for m in misses)


def test_a_changed_row_excuses_the_old_wording_and_demands_the_new():
    page = FAITHFUL.replace("<h2>Blue Staffy Puppies in Carlisle</h2>",
                            "<h2>Blue Staffy Puppies in Cumbria</h2>")
    record = {"verbatim": {"changed": [{
        "kind": "heading",
        "old": "Blue Staffy Puppies in Carlisle",
        "new": "Blue Staffy Puppies in Cumbria",
        "reason": "the heading collides with the Carlisle location page (header-collision)",
    }]}}
    examined, changed, misses = V.judge(vset(), page, record)
    assert misses == []
    assert (examined, changed) == (7, 1)


def test_a_changed_row_whose_new_text_is_absent_is_still_a_miss():
    record = {"verbatim": {"changed": [{
        "kind": "heading", "old": "Blue Staffy Puppies in Carlisle",
        "new": "A Heading Nobody Wrote", "reason": "a reason long enough to be a reason",
    }]}}
    _, changed, misses = V.judge(vset(), FAITHFUL, record)
    assert changed == 1
    assert any("changed heading not on the page" in m for m in misses)


def test_a_heading_dropped_row_excuses_the_heading_and_demands_nothing():
    """`heading-dropped` is a deviation kind, not an element kind. If it were keyed as it is
    written the row would match no element, the gate would go on demanding the old heading, and
    an accounting file would silently excuse nothing at all."""
    page = FAITHFUL.replace("<h2>Blue Staffy Puppies in Carlisle</h2>", "")
    record = {"verbatim": {"changed": [{
        "kind": "heading-dropped", "old": "Blue Staffy Puppies in Carlisle", "new": "",
        "reason": "the outline removed the section outright and nothing stands in for it",
    }]}}
    _, changed, misses = V.judge(vset(), page, record)
    assert changed == 1
    assert not any("Blue Staffy Puppies in Carlisle" in m for m in misses)


def test_a_faq_merged_row_is_judged_as_the_question_it_merges_into():
    page = FAITHFUL.replace("Are the parents health tested?",
                            "Are the parents of your puppies health tested?")
    record = {"verbatim": {"changed": [{
        "kind": "faq-merged", "old": "Are the parents health tested?",
        "new": "Are the parents of your puppies health tested?",
        "reason": "the old page asked the same question twice and one row answers both",
    }]}}
    _, changed, misses = V.judge(vset(), page, record)
    assert changed == 1
    assert misses == []


def test_an_opening_may_be_followed_by_fresh_prose_but_not_reworded():
    page = FAITHFUL.replace("Every litter is raised in the kitchen, not a kennel.",
                            "Every litter is raised at home.")
    _, _, misses = V.judge(vset(), page, {})
    assert any("missing opening" in m for m in misses)


def test_an_alt_is_judged_against_its_own_src():
    page = FAITHFUL.replace('alt="A blue Staffy puppy on a lawn"', 'alt="A puppy"')
    _, _, misses = V.judge(vset(), page, {})
    assert any("missing alt on /images/pup.webp" in m for m in misses)


def test_an_alt_row_keys_on_the_src_so_two_empty_alts_do_not_collide():
    page = FAITHFUL.replace('src="/images/spacer.gif" alt=""',
                            'src="/images/spacer.gif" alt="A brand divider"')
    record = {"verbatim": {"changed": [{
        "kind": "alt", "src": "/images/spacer.gif", "old": "", "new": "A brand divider",
        "reason": "the empty alt hid a mark that now carries meaning",
    }]}}
    _, changed, misses = V.judge(vset(), page, record)
    assert (changed, misses) == (1, [])


def test_the_scope_is_main_so_a_heading_in_the_header_does_not_count():
    page = built("<h1>Our Blue Staffy Promise</h1>")
    _, _, misses = V.judge(vset(), page, {})
    assert any("missing heading" in m and "Carlisle" in m for m in misses)


# ── the applicable list ───────────────────────────────────────────────────────────────────

EXCLUDED = ["privacy-policy-uk", "thank-you-blue-staffy-puppies-journey",
            "uk-blue-staffy-breeders-contact"]

NINE = ["index", "blue-staffy-uk-breeders", "blue-staffy-health-uk",
        "uk-staffordshire-bull-terrier-guide", "uk-blue-staffy-puppy-buying-guide",
        "blue-staffy-blog-guides", "blue-staffy-pup-sale-uk",
        "buy-staffy-puppies-for-sale-uk", "buy-blue-staffy-puppies-uk"]


def applies():
    return json.loads((ROOT / "data/verbatim/applies.json").read_text(encoding="utf-8"))


def test_the_nine_faithful_rewrite_pages_are_the_applicable_list():
    assert applies()["slugs"] == NINE


def test_the_three_pages_built_before_rule_15_are_excluded_by_name_with_a_reason():
    a = applies()
    for slug in EXCLUDED:
        assert slug not in a["slugs"]
        assert len(a["excluded"][slug]) > 10


def test_every_applicable_slug_has_a_set_on_disk():
    for slug in applies()["slugs"]:
        path = ROOT / f"data/verbatim/{slug}.json"
        assert path.exists(), f"{slug} is under rule 15 with no extracted set"
        vs = json.loads(path.read_text(encoding="utf-8"))
        assert set(vs) == {"keywords", "h1", "headings", "openings", "faq_questions", "alts"}


def test_check_skips_an_excluded_slug_even_once_it_is_rebuilt():
    """The three are in rebuilt.json today. The gate must still not ask them for a set."""
    rebuilt = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))
    assert set(EXCLUDED) <= set(rebuilt)
    assert not set(V.applicable_slugs()) & set(EXCLUDED)
