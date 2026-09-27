"""Every puppy card carries its delivery line (CAG parity audit D4; rules/puppies.md
`delivery-band-on-every-card`).

rules/puppies.md has said since the port that a puppy card MUST show the delivery cost, in
one canonical line — "UK home delivery £200–£350 by distance · or collect in Carlisle" — and
that no card ships without it. Nothing enforced it, and src/components/kit/PuppyCard.astro
showed sex, colour, price and status and nothing about getting the puppy home. Project 5's
city pages mount that card. The line reads the band and the town from data/settings.json,
so it can never disagree with the price table or the FAQ.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import dup_content_audit as dup  # noqa: E402
import evidence_audit as ea  # noqa: E402

CARD = ROOT / "src/components/kit/PuppyCard.astro"
SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
DIST = ROOT / "dist"
ARTICLE = re.compile(r'<article\b[^>]*class="[^"]*\bkit-pup\b[^"]*"[^>]*>(.*?)</article>', re.S)
DELIV = re.compile(r'<p\b[^>]*class="[^"]*\bdeliv\b[^"]*"[^>]*>(.*?)</p>', re.S)
RULES = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))["rules"]


def expected_line():
    lo, hi = SETTINGS["delivery_min_gbp"], SETTINGS["delivery_max_gbp"]
    return f"UK home delivery £{lo:,}–£{hi:,} by distance · or collect in {SETTINGS['address']['city']}"


def test_the_card_reads_the_band_from_settings_and_types_no_amount():
    src = CARD.read_text(encoding="utf-8")
    for key in ("SITE.delivery_min_gbp", "SITE.delivery_max_gbp", "SITE.address.city"):
        assert key in src, key
    markup = src.split("---", 2)[2]
    assert not re.search(r"£\s*\d", markup), "the card template spells a delivery amount by hand"


def test_the_rule_is_enforced_by_this_file():
    row = next(r for r in RULES if r["id"] == "delivery-band-on-every-card")
    assert row["enforced"] == "test" and row["test"] == "tests/py/test_puppy_card_delivery.py", row
    pack = (ROOT / "rules/puppies.md").read_text(encoding="utf-8")
    assert re.search(r"id: delivery-band-on-every-card\nenforced: test\n", pack)


def test_the_line_is_whitelisted_as_the_canonical_card_line():
    stem = " ".join(re.findall(r"[a-z0-9$']+", expected_line().lower()))
    assert stem in dup.WHITELIST_SNIPPETS


def built_pages_with_cards():
    return [p for p in sorted(DIST.glob("**/index.html")) if "kit-pup" in p.read_text(encoding="utf-8")]


def test_every_built_card_carries_the_delivery_line():
    if not DIST.exists():
        pytest.skip("run npm run build first")
    pages = built_pages_with_cards()
    assert len(pages) >= 5, "fewer built pages carry a puppy card than the kit mounts on"
    bad, examined = [], 0
    for page in pages:
        for card in ARTICLE.findall(page.read_text(encoding="utf-8")):
            examined += 1
            got = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m)).strip() for m in DELIV.findall(card)]
            if got != [expected_line()]:
                bad.append((page.relative_to(DIST).as_posix(), got))
    assert examined > 0, "no puppy card was examined — that is not a pass"
    assert bad == [], bad


REBUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("slug", REBUILT)
def test_the_card_line_keeps_every_built_page_inside_its_term_budgets(slug):
    built = DIST / ("index.html" if slug == "index" else f"{slug}/index.html")
    if not built.exists():
        pytest.skip("run npm run build first")
    budgets = json.loads((ROOT / "data/quality/evidence-budgets.json").read_text(encoding="utf-8"))
    over = ea.term_budget(built.read_text(encoding="utf-8"), ea.page_type_for(slug), budgets, slug)
    assert over == [], (slug, over)
