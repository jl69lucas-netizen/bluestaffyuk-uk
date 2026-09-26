"""An approved board's `global_cta` decides whether the footer's CTA band renders
(CAG parity audit D3; answer-board batch 2026-09-26-brief-parity-two-decisions-before-project-5, ruling (a)).

Every board records `brief.cta.global_cta`, and the board Artifact tells the breeder "the
site-wide CTA band is hidden on this page" when it says `hidden`. Eleven of the twelve
approved boards chose `hidden` — and src/components/kit/SiteFooterKit.astro rendered its
`.cta-band` on every page regardless, so eleven approved boards disagreed with their built pages.
PageShell now reads the page's approved record and passes `cta={false}` to the footer when
the record says `hidden`. A page with no approved board keeps the band.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
BAND = re.compile(r'class="[^"]*\bcta-band\b')


def approved_boards():
    out = []
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        if f.stem.startswith("_"):
            continue
        b = json.loads(f.read_text(encoding="utf-8"))
        if b.get("approval"):
            out.append((b["meta"]["slug"], b["brief"]["cta"]["global_cta"]))
    return out


def built(slug):
    return DIST / ("index.html" if slug == "index" else f"{slug}/index.html")


def test_there_are_approved_boards_of_both_kinds():
    kinds = {g for _, g in approved_boards()}
    assert kinds == {"hidden", "shown"}, kinds


@pytest.mark.parametrize("slug,global_cta", approved_boards())
def test_the_built_page_honours_its_boards_global_cta(slug, global_cta):
    page = built(slug)
    if not page.exists():
        pytest.skip("run npm run build first")
    has_band = bool(BAND.search(page.read_text(encoding="utf-8")))
    assert has_band == (global_cta == "shown"), (slug, global_cta, has_band)


def test_a_page_with_no_board_keeps_the_band():
    page = DIST / "available-puppies/index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    assert BAND.search(page.read_text(encoding="utf-8"))


def test_the_footer_takes_the_flag_as_a_prop():
    src = (ROOT / "src/components/kit/SiteFooterKit.astro").read_text(encoding="utf-8")
    assert re.search(r"cta\s*=\s*true", src), "SiteFooterKit needs a `cta` prop defaulting to true"
    assert re.search(r"\{cta\s*&&", src), "the band must render only when `cta` is true"
    shell = (ROOT / "src/layouts/PageShell.astro").read_text(encoding="utf-8")
    assert "globalCtaShown" in shell and "<SiteFooterKit slot=\"footer\" cta={" in shell
