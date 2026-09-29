"""A counter strip's lede counts its own tiles (review I5, 2026-09-29).

Two tiles came out of two counter strips for stating a DNA result (answer board q01), and
the ledes above them still said "all three" and "Three figures". A lede that names a count
(a number word) must name the number of tiles the strip renders."""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
PAGES = ["blue-staffy-health-uk", "blue-staffy-uk-breeders", "index", "buy-staffy-puppies-for-sale-uk",
         "blue-staffy-pup-sale-uk", "buy-blue-staffy-puppies-uk"]


def strip(slug):
    f = ROOT / "dist" / ("index.html" if slug == "index" else f"{slug}/index.html")
    if not f.exists():
        pytest.skip("run npm run -s build first")
    html = f.read_text(encoding="utf-8")
    m = re.search(r'<section id="stats".*?</section>\s*</div>\s*</section>', html, re.S)
    if not m:
        pytest.skip(f"{slug} has no stats section")
    sec = m.group(0)
    lede = re.search(r'<p class="bl-lede">(.*?)</p>', sec, re.S)
    tiles = len(re.findall(r"<li\b", sec.split("kit-counter", 1)[1])) if "kit-counter" in sec else 0
    return (lede.group(1) if lede else ""), tiles


@pytest.mark.parametrize("slug", PAGES)
def test_the_lede_counts_the_tiles(slug):
    lede, tiles = strip(slug)
    assert tiles, slug
    named = [WORDS[w.lower()] for w in re.findall(r"(?i)\b(two|three|four|five|six)\b", lede)]
    assert all(n == tiles for n in named), (slug, lede.strip(), tiles)


def test_the_about_page_counts_its_dna_tests_again():
    """Review I6: "2 / DNA tests on both parents" is a true count, restored."""
    f = ROOT / "dist/blue-staffy-uk-breeders/index.html"
    if not f.exists():
        pytest.skip("run npm run -s build first")
    assert re.search(r"<strong[^>]*>2</strong><span[^>]*>DNA tests on both parents</span>", f.read_text(encoding="utf-8"))
