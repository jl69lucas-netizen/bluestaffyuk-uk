"""London has no term-budget entry of its own: it fits the location density ceilings.

Answer board 2026-10-05 london-gate-findings q03 (a) held London at its counts as built
(`budgets_by_slug["uk-locations/blue-staffy-puppies-london"]`) until Known Issue 99
calibrated the location ceilings. The user's pick on 2026-10-07 (batch
2026-10-07-research-board-blue-staffy-puppies-manchester-uk q12 (a)) made those ceilings
densities on board block 4c's counter (`location_density` in
data/quality/evidence-budgets.json, pinned by tests/py/test_evidence_location_density.py),
and London as built fits under every one, so its entry was deleted. What stays pinned here:
London carries no entry, no other city has one to inherit, and London as built passes the
live budgets.

These tests read the LIVE budgets file on purpose (tests/py/test_evidence_per_slug_overrides.py
pins the override mechanism on a fixture).
"""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as ea  # noqa: E402

SLUG = "uk-locations/blue-staffy-puppies-london"
LIVE = json.loads((ROOT / "data/quality/evidence-budgets.json").read_text(encoding="utf-8"))
BUILT = ROOT / "dist" / SLUG / "index.html"


def test_london_carries_no_entry_of_its_own():
    assert SLUG not in LIVE["budgets_by_slug"], (
        "London fits the density ceilings (Known Issue 99 option (a)); its entry was deleted")


def test_no_city_inherits_a_per_slug_entry():
    """Every city is judged on the location density ceilings, never on a per-slug entry."""
    cities = [s for s in LIVE["budgets_by_slug"] if s.startswith("uk-locations/")]
    assert cities == [], cities


def test_known_issue_99_records_the_calibration_task_closed():
    log = (ROOT / "docs/reference/session-log.md").read_text(encoding="utf-8")
    m = re.search(r"^99\. \*\*(.+?)\*\*", log, flags=re.M)
    assert m, "Known Issue 99 is missing from docs/reference/session-log.md"
    assert "calibrat" in m.group(1).lower() and "location" in m.group(1).lower()
    assert "CLOSED" in m.group(1)


def _main(text):
    return f"<html><body><main><p>{text}</p></main></body></html>"


def test_another_city_is_judged_on_the_density_ceiling():
    """A page that is nothing but its city's name is far over the city density: 60 words
    at 17.5 per 1,000 is a ceiling of 1."""
    leeds = "uk-locations/blue-staffy-puppies-for-sale-leeds"
    if ea.city_for(leeds) is None:
        pytest.skip("no Leeds row in data/locations.json")
    html = _main(" ".join(["Leeds."] * 60))
    cap = int(round(LIVE["location_density"]["per_1000_words"]["city"] * 60 / 1000))
    assert ea.term_budget(html, "location", LIVE, slug=leeds) == [("city", 60, cap)]


def test_the_built_london_page_is_inside_its_budget():
    if not BUILT.exists():
        pytest.skip("run npm run build first")
    html = BUILT.read_text(encoding="utf-8")
    assert ea.term_budget(html, "location", LIVE, slug=SLUG) == []
