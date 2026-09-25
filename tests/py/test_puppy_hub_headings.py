"""Known Issue 31, first half: `/available-puppies/` opened each puppy card at H3 directly
under the page's H1, with no H2 between them — `sem-heading-order` failed it at all three
viewports, three of the six blocking rows in the project 4 render baseline.

The hub mounts `PuppyList` with `heading="none"` (the page's own H1 already says "Available
Blue Staffy Puppies"), so in that mode the cards themselves are the page's second level.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HUB = ROOT / "dist/available-puppies/index.html"
MAIN = re.compile(r"<main\b.*?</main>", re.S | re.I)
HEADING = re.compile(r"<h([1-6])\b", re.I)


def skips(html):
    """Every place a heading level is skipped going DOWN inside <main> (H1 -> H3 is one)."""
    main = MAIN.search(html)
    levels = [int(m.group(1)) for m in HEADING.finditer(main.group(0) if main else html)]
    return [(a, b) for a, b in zip(levels, levels[1:]) if b > a + 1]


def test_the_skip_finder_sees_h1_to_h3():
    assert skips("<main><h1>x</h1><h3>y</h3></main>") == [(1, 3)]
    assert skips("<main><h1>x</h1><h2>y</h2><h3>z</h3><h2>w</h2></main>") == []


def test_the_puppy_hub_skips_no_heading_level():
    if not HUB.exists():
        pytest.skip("run npm run build first")
    assert skips(HUB.read_text(encoding="utf-8")) == []
