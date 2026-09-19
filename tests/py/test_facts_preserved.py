"""facts_preserved_check.py — the gate that replaces migration parity for a rebuilt page.

Parity measures SIZE: words, headings, images, embeds against what the extractor promised.
That is the right question for a page migrated verbatim and the wrong one for a page written
fresh, where the heading list is supposed to change. What must not change is the FACTS —
a price, a puppy's name, a health test, a credential, an image, a video — and a fact may
only leave a page deliberately, which means listed under `dropped` in the board record with
a reason beside it.

The fixture below is a miniature migrated body: two prices, two of the three names offered,
a health test, an image and a YouTube embed.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import facts_preserved_check as F

OLD = (
    "<article class='prose-migrated'><p>Puppies from £1,500 and £1,700. Roman and Byrd are "
    "DNA tested for L-2-HGA.</p>"
    "<img src='/images/blue-staffy-puppy-for-sale-uk.webp' alt='x'>"
    "<iframe src='https://www.youtube.com/embed/g9iV9RVr_Sk'></iframe></article>"
)


def test_extract_finds_prices_names_tests_images_embeds():
    f = F.extract(OLD, names=["Roman", "Byrd", "Ince"])
    assert f["prices"] == ["£1,500", "£1,700"]
    assert f["names"] == ["Roman", "Byrd"]
    assert "L-2-HGA" in f["tests"]
    assert f["images"] == ["/images/blue-staffy-puppy-for-sale-uk.webp"]
    assert f["embeds"] == ["g9iV9RVr_Sk"]


def test_check_reports_missing_unless_dropped():
    facts = F.extract(OLD, names=["Roman", "Byrd"])
    new = ("<main><p>Roman is £1,500. L-2-HGA clear.</p>"
           "<img src='/images/blue-staffy-puppy-for-sale-uk.webp'></main>")
    missing = F.missing(facts, new, dropped={"names": ["Byrd"], "prices": ["£1,700"]})
    # `DNA` is reported alongside the embed: the old body says the pups are "DNA tested" and
    # the new one does not say it at all. The plan's draft of this test expected only the
    # embed, which would require the checker to treat the specific test name (L-2-HGA) as
    # covering the general claim (DNA tested) — two different facts, and letting one stand in
    # for the other is exactly the quiet loss this gate exists to catch.
    assert missing == {"tests": ["DNA"], "embeds": ["g9iV9RVr_Sk"]}


# --- The committed fact sets and the wiring -----------------------------------------------

TWELVE = [
    "index", "blue-staffy-uk-breeders", "buy-blue-staffy-puppies-uk", "blue-staffy-pup-sale-uk",
    "buy-staffy-puppies-for-sale-uk", "blue-staffy-health-uk",
    "uk-staffordshire-bull-terrier-guide", "uk-blue-staffy-puppy-buying-guide",
    "uk-blue-staffy-breeders-contact", "privacy-policy-uk",
    "thank-you-blue-staffy-puppies-journey", "blue-staffy-blog-guides",
]


def test_every_page_this_project_rebuilds_has_a_committed_fact_set():
    """Extracted ONCE, from the migrated build, before the rewrite. After the rewrite the
    page it was taken from no longer exists, so a fact set that was never committed can
    never be recovered."""
    missing = [s for s in TWELVE if not (ROOT / f"data/facts/{s}.json").is_file()]
    assert not missing, "no fact set for: " + ", ".join(missing)


KINDS = ["prices", "names", "tests", "creds", "images", "embeds"]

# The blog post is the one page with nothing to preserve, and that is a measured fact about
# it rather than an extraction that failed: its body is a 1,150-character introduction with
# no price, no image, no embed and no health test in it. Named here so an empty fact set
# anywhere ELSE stays a failure.
FACTLESS = {"blue-staffy-blog-guides"}


def test_every_fact_set_has_the_six_kinds_and_nothing_else():
    for slug in TWELVE:
        facts = json.loads((ROOT / f"data/facts/{slug}.json").read_text())
        assert sorted(facts) == sorted(KINDS), slug
        assert all(isinstance(v, list) and all(isinstance(x, str) for x in v)
                   for v in facts.values()), slug


def test_the_fact_sets_are_not_empty_shells():
    """A file of empty lists is the failure mode this gate is most likely to have: it passes
    every check forever and proves nothing."""
    thin = [s for s in TWELVE if s not in FACTLESS
            and not any(json.loads((ROOT / f"data/facts/{s}.json").read_text()).values())]
    assert not thin, "fact sets with nothing in them: " + ", ".join(thin)


def test_rebuilt_json_lists_only_slugs_that_have_a_fact_set():
    rebuilt = json.loads((ROOT / "data/facts/rebuilt.json").read_text())
    assert isinstance(rebuilt, list)
    assert not [s for s in rebuilt if not (ROOT / f"data/facts/{s}.json").is_file()]


def test_parity_and_the_facts_gate_never_judge_the_same_page():
    """The two gates are exclusive by construction: a rebuilt page's heading list is supposed
    to change, so parity must stop looking at it on exactly the run the facts gate starts."""
    import migration_parity as P
    rebuilt = set(json.loads((ROOT / "data/facts/rebuilt.json").read_text()))
    page_map = json.loads((ROOT / "data/page-map.json").read_text())
    judged = {P.slug_of(row) for row in page_map["pages"]} - rebuilt
    assert not (judged & rebuilt)
    assert P.rebuilt_slugs(ROOT) == rebuilt


def test_the_checker_runs_clean_over_the_committed_state():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/facts_preserved_check.py"), "--check"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "examined" in proc.stdout
