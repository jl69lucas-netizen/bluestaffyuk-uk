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
    # `text` joins them (project 4, 2026-09-20): the fixture's two sentences are both claim
    # sentences — one carries prices, one carries a health test and two names — and the new
    # body restates neither closely enough to clear the six-word overlap. That is the point of
    # the kind: a sentence can leave a page without a single TOKEN going missing with it.
    assert missing == {
        "tests": ["DNA"],
        "embeds": ["g9iV9RVr_Sk"],
        "text": ["Puppies from £1,500 and £1,700.",
                 "Roman and Byrd are DNA tested for L-2-HGA."],
    }


def test_a_claim_is_carried_when_its_triggers_and_six_words_survive():
    """The other half of the `text` kind: a rebuild that REWRITES a claim keeps it."""
    facts = {"text": ["Our dedicated team aims to personally review and respond to all "
                      "inquiries within 24-48 business hours."]}
    reworded = ("<main><p>Every inquiry is read and answered personally by our team, within "
                "24-48 business hours.</p></main>")
    assert F.missing(facts, reworded) == {}
    # Drop the number and the claim is gone, however much of the wording survives.
    gutted = ("<main><p>Every inquiry is read and answered personally by our team, quickly."
              "</p></main>")
    assert F.missing(facts, gutted) == facts


def test_a_dropped_text_line_may_quote_the_phrase_rather_than_the_sentence():
    facts = {"text": ["This includes secure servers and regular staff training."]}
    dropped = {"text": ["regular staff training — no file on disk records a programme"]}
    assert F.missing(facts, "<main><p>Nothing here.</p></main>", dropped) == {}


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


KINDS = ["prices", "names", "tests", "creds", "images", "embeds", "text"]

# The blog post is the one page with almost nothing to preserve, and that is a measured fact
# about it rather than an extraction that failed: its body is a 1,150-character introduction
# with no price, no image, no embed and no health test in it. Named here so an empty fact set
# anywhere ELSE stays a failure.
FACTLESS = {"blue-staffy-blog-guides"}


def test_every_fact_set_has_the_seven_kinds_and_nothing_else():
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


def test_a_slug_in_rebuilt_json_leaves_the_parity_report_and_is_counted_as_skipped(tmp_path):
    """The handover, measured rather than restated.

    A rebuilt page's heading list is SUPPOSED to change, so parity has to stop judging it on
    exactly the run the facts gate starts. The second page below would fail parity outright —
    its built body is one sentence where the export had a hundred and twenty words — so if
    listing it in rebuilt.json did not remove it from the run, this test would see the failure
    instead of the skip.
    """
    import migration_parity as P

    prose = " ".join(["alpha"] * 120)
    body = f"<h2>Head</h2><p>{prose}</p>"
    source = f'<html><body><div class="entry-content">{body}</div></body></html>'
    root, src, dist = tmp_path / "root", tmp_path / "src", tmp_path / "dist"
    for path, text in (
        (root / "data/page-map.json", json.dumps(
            {"generated_from": str(src), "pages": [
                {"url": "/kept/", "kind": "rich", "defects": []},
                {"url": "/redone/", "kind": "rich", "defects": []}]})),
        (root / "data/facts/rebuilt.json", json.dumps(["redone"])),
        (src / "kept/index.html", source),
        (src / "redone/index.html", source),
        (dist / "kept/index.html", f'<html><body><article class="prose-migrated">{body}</article></body></html>'),
        (dist / "redone/index.html", "<html><body><main><p>Written fresh.</p></main></body></html>"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    assert P.rebuilt_slugs(root) == {"redone"}
    P.main(root=root, src=src, dist=dist)          # no SystemExit: the failing page is skipped
    report = (root / "docs/reports/parity.md").read_text(encoding="utf-8")
    assert "examined 1 pages, 0 failing, skipped 1 rebuilt" in report
    assert "| /redone/ |" not in report, "a skipped page must leave the table, not sit in it as a pass"
    assert "| /kept/ |" in report


def test_the_checker_runs_clean_over_the_committed_state():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/facts_preserved_check.py"), "--check"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "examined" in proc.stdout


def test_a_dropped_entry_carries_its_reason_and_is_still_matched():
    """`dropped` is "<the fact> — <why it is not carried>", and the reason is the point of
    the field: a bare list of paths records that something went, not that anyone agreed it
    should. The fact is read off the front of the line, so the two forms are equivalent to
    the gate and a record is never pushed into dropping the explanation to pass."""
    facts = {"images": ["/images/a.webp", "/images/b.webp"]}
    html = "<article><p>No images at all.</p></article>"
    reasoned = {"images": [
        "/images/a.webp — the rebuilt page is text-led legal prose and carries one image only.",
        "/images/b.webp — illustrates no clause on this page.",
    ]}
    assert F.missing(facts, html, reasoned) == {}
    # the bare form the older records wrote still works
    assert F.missing(facts, html, {"images": ["/images/a.webp", "/images/b.webp"]}) == {}
    # and a fact nobody dropped is still reported
    assert F.missing(facts, html, {"images": ["/images/a.webp — reason"]}) == {"images": ["/images/b.webp"]}


def test_drop_facts_reads_the_fact_off_the_front_of_the_line():
    assert F.drop_facts(["/images/x.webp — because"]) >= {"/images/x.webp"}
    assert F.drop_facts(["£1,200 – the old band, superseded"]) >= {"£1,200"}
    assert F.drop_facts(["Kane"]) == {"Kane"}
    assert F.drop_facts(None) == set()


def test_a_dropped_claim_matches_through_the_extractors_space_before_a_comma():
    """The WordPress body wrapped emphasised runs in their own tags, so `extract()` reads a
    claim sentence back with a stray space in front of its punctuation — "…(BVA) ,
    Staffordshire Bull Terriers …". A `dropped.text` line quotes the claim the way a person
    reads it, and before `_claim_key` the gate demanded that the record transcribe the
    artifact: two claims the why-us record strikes BY NAME, with reasons, reported as
    unaccounted for (2026-09-21). The match is still exact about every word.
    """
    facts = {"text": [
        "According to the British Veterinary Association (BVA) , Staffordshire Bull Terriers "
        "can be prone to hip and elbow dysplasia , and responsible breeders take measures."
    ]}
    html = "<article><p>Nothing of the sort is claimed here.</p></article>"
    clean = {"text": [
        "'According to the British Veterinary Association (BVA), Staffordshire Bull Terriers "
        "can be prone to hip and elbow dysplasia, and responsible breeders take measures.' — "
        "the health page owns the breed's wider screening and this page links it."
    ]}
    assert F.missing(facts, html, clean) == {}
    # And a claim the record does NOT account for is still reported: the forgiveness is about
    # a typographic accident, never about which words are there.
    other = {"text": ["'Some entirely different sentence.' — a reason"]}
    assert F.missing(facts, html, other)["text"] == facts["text"]


def test_a_dropped_text_line_too_short_to_name_a_claim_cannot_excuse_one():
    """The `text` match runs in BOTH directions so a record may quote the phrase that carries
    a claim rather than transcribe a forty-word sentence. Below a floor that stops naming one
    claim: "kc" would excuse most of a breeder page, and the why-us record's own community
    line all but reached for a two-word quote. `MIN_DROP_PHRASE` is the floor for the
    CONTAINMENT path only — an exact line still matches at any length, so nothing that passed
    on an exact quotation stops passing.
    """
    facts = {"text": ["We are KC registered and the parents are DNA tested clear of L-2-HGA."]}
    html = "<article><p>Nothing at all.</p></article>"
    assert len(F._claim_key("KC")) < F.MIN_DROP_PHRASE
    assert F.missing(facts, html, {"text": ["KC — too short to name anything"]}) == facts
    # A phrase long enough to identify the claim still excuses it.
    long_enough = "DNA tested clear of L-2-HGA"
    assert len(F._claim_key(long_enough)) >= F.MIN_DROP_PHRASE
    assert F.missing(facts, html, {"text": [f"{long_enough} — the health page owns it"]}) == {}
    # And an EXACT line is matched whatever its length, by the plain `v in drop` path.
    short_fact = {"text": ["KC"]}
    assert F.missing(short_fact, html, {"text": ["KC"]}) == {}
