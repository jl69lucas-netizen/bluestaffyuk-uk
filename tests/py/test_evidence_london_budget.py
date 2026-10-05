"""London's term budget is its count as built, by the breeder's ruling, and it ratchets.

Answer board 2026-10-05 london-gate-findings q03 (a): "Keep London as approved: record its
counts as its own limit, then tune the location limits before the next city". The entry is
`budgets_by_slug["uk-locations/blue-staffy-puppies-london"]` in
data/quality/evidence-budgets.json; the calibration is Known Issue 99.

These tests read the LIVE budgets file on purpose: what they pin is the entry the ruling
wrote, not the override mechanism (tests/py/test_evidence_per_slug_overrides.py pins that
on a fixture).
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
RULINGS = "docs/reference/answer-board/answers/2026-10-05-london-gate-findings-2026-10-05.md"
BOARD = "data/boards/blue-staffy-puppies-london.json"
LIVE = json.loads((ROOT / "data/quality/evidence-budgets.json").read_text(encoding="utf-8"))
ENTRY = LIVE["budgets_by_slug"].get(SLUG, {})
BUILT = ROOT / "dist" / SLUG / "index.html"


def test_london_has_an_entry_citing_the_ruling_and_the_board():
    assert ENTRY, f"budgets_by_slug has no {SLUG!r} entry (q03 (a))"
    why = ENTRY.get("_why", "")
    assert "q03" in why and RULINGS in why, "the _why must cite the rulings file and q03"
    assert BOARD in why, "the _why must name the approved board record"
    assert "Known Issue 99" in why, "the _why must point at the calibration task"
    assert (ROOT / RULINGS).exists() and (ROOT / BOARD).exists()


def test_every_london_budget_names_a_capped_location_term():
    """A key the location map never caps is ignored by term_budget (with a stderr WARN):
    a typo here would silently leave a term on the default."""
    caps = LIVE["budgets"]["location"]
    terms = [t for t in ENTRY if not t.startswith("_")]
    assert terms, "the entry records no counts"
    for t in terms:
        assert t in caps, t
        assert isinstance(ENTRY[t], int) and ENTRY[t] > caps[t], (t, ENTRY[t], caps[t])


def test_known_issue_99_records_the_calibration_task():
    log = (ROOT / "docs/reference/session-log.md").read_text(encoding="utf-8")
    m = re.search(r"^99\. \*\*(.+?)\*\*", log, flags=re.M)
    assert m, "Known Issue 99 is missing from docs/reference/session-log.md"
    assert "calibrat" in m.group(1).lower() and "location" in m.group(1).lower()


def _main(text):
    return f"<html><body><main><p>{text}</p></main></body></html>"


def test_the_entry_is_a_ratchet_one_more_london_fails():
    cap = ENTRY["city"]
    at_cap = _main(" ".join(["London."] * cap))
    over = _main(" ".join(["London."] * (cap + 1)))
    assert ea.term_budget(at_cap, "location", LIVE, slug=SLUG) == []
    assert ea.term_budget(over, "location", LIVE, slug=SLUG) == [("city", cap + 1, cap)]


def test_another_city_keeps_the_location_default():
    """The entry is London's only: Leeds at London's density still fails on the default."""
    leeds = "uk-locations/blue-staffy-puppies-for-sale-leeds"
    if ea.city_for(leeds) is None:
        pytest.skip("no Leeds row in data/locations.json")
    html = _main(" ".join(["Leeds."] * 60))
    assert ea.term_budget(html, "location", LIVE, slug=leeds) == [
        ("city", 60, LIVE["budgets"]["location"]["city"])]


def test_the_built_london_page_is_inside_its_budget():
    if not BUILT.exists():
        pytest.skip("run npm run build first")
    html = BUILT.read_text(encoding="utf-8")
    assert ea.term_budget(html, "location", LIVE, slug=SLUG) == []
