"""data/design/components.json is the one list of kit components; everything else
(the kit folder, the canvas route, the picks board, picks.json) is checked against it."""
import json, pathlib, re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "data/design/components.json"
KIT = ROOT / "src/components/kit"
IDS = ["site-header", "hero", "buttons", "puppy-card", "trust-strip", "counter-strip",
       "info-card", "testimonial", "faq", "contact-form", "page-nav", "footer", "section-divider"]


def load():
    return json.loads(COMPONENTS.read_text())


def test_thirteen_components_in_spec_order():
    rows = load()
    assert [r["id"] for r in rows] == IDS


def test_each_row_has_file_title_width():
    for r in load():
        assert re.fullmatch(r"[A-Z][A-Za-z]+Kit?\.astro|[A-Z][A-Za-z]+\.astro", r["file"]), r
        assert r["title"] and isinstance(r["title"], str)
        assert r["board_width"] in (640, 1280), r


@pytest.mark.xfail(strict=True, reason="kit lands in Tasks 4-16")
def test_kit_file_exists_for_each_row():
    missing = [r["file"] for r in load() if not (KIT / r["file"]).exists()]
    assert not missing, missing
