"""evidence_audit per-slug overrides: the homepage keeps its long Rule-21 title and its
credential entities; every other slug keeps the page-type rules.

Ported from CAG tests/test_evidence_per_slug_overrides.py (Task 7). DEVIATION from the
plan's "only the fixture prose changes": CAG's version read the real
data/quality/evidence-budgets.json, which Task 9 has not written yet — and a gate test
that reads the repo's live budgets would pin whatever is in the file rather than the
behaviour. `_budgets()` therefore returns an inline fixture of the same shape. No test
is dropped; every assertion stands.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as ea


def _budgets():
    """The shape data/quality/evidence-budgets.json carries, as a fixture."""
    return {
        "title_max_chars": 70,
        "title_max_chars_by_slug": {"index": 205},
        "superlatives": [],
        "terms": {"KC": "KC", "microchipped": "microchipped", "DEFRA": "DEFRA",
                  "Glasgow": "Glasgow"},
        "budgets": {"home": {"KC": 6, "microchipped": 6, "DEFRA": 6, "Glasgow": 20}},
        "budgets_by_slug": {"index": {"KC": None, "microchipped": None, "DEFRA": None}},
    }


def test_homepage_title_cap_is_205():
    assert _budgets()["title_max_chars_by_slug"]["index"] == 205


def test_homepage_long_title_passes():
    html = "<title>" + "x" * 200 + "</title>"
    assert ea.title_too_long(html, _budgets(), slug="index") is None


def test_other_slug_keeps_70():
    html = "<title>" + "x" * 90 + "</title>"
    assert ea.title_too_long(html, _budgets(), slug="buy-blue-staffy-puppies-uk") == (90, 70)


def _main(words):
    return "<html><body><main>" + " ".join(words) + "</main></body></html>"


def test_homepage_credential_terms_have_no_ceiling():
    html = _main(["KC"] * 20 + ["microchipped"] * 20 + ["DEFRA"] * 20)
    over = {t for t, n, c in ea.term_budget(html, "home", _budgets(), slug="index")}
    assert not (over & {"KC", "microchipped", "DEFRA"}), over


def test_homepage_other_terms_still_capped():
    html = _main(["Glasgow"] * 30)
    over = {t for t, n, c in ea.term_budget(html, "home", _budgets(), slug="index")}
    assert "Glasgow" in over


def test_other_slug_credential_terms_still_capped():
    html = _main(["KC"] * 20)
    over = {t for t, n, c in ea.term_budget(html, "home", _budgets(), slug="not-the-homepage")}
    assert "KC" in over


def test_unmatched_override_term_is_reported(capsys):
    b = json.loads(json.dumps(_budgets()))  # deep copy
    b["budgets_by_slug"]["index"]["KCpapers"] = None  # typo: no such term in budgets["home"]
    ea.term_budget(_main(["KC"]), "home", b, slug="index")
    err = capsys.readouterr().err
    assert "KCpapers" in err and "index" in err and "home" in err


def test_override_shape_round_trips_through_a_real_budgets_file(tmp_path):
    """The inline fixture above is only trustworthy if the same shape survives
    json.dumps -> file -> json.loads, `null` ceiling removal included."""
    import json as _json
    path = tmp_path / "evidence-budgets.json"
    path.write_text(_json.dumps(_budgets()), encoding="utf-8")
    budgets = _json.loads(path.read_text())
    assert budgets["budgets_by_slug"]["index"]["KC"] is None
    html = _main(["KC"] * 20 + ["Glasgow"] * 30)
    over = {t for t, n, c in ea.term_budget(html, "home", budgets, slug="index")}
    assert "KC" not in over          # null removed the ceiling
    assert "Glasgow" in over         # the untouched ceiling still bites
    over_other = {t for t, n, c in ea.term_budget(html, "home", budgets, slug="other")}
    assert "KC" in over_other        # the override is per-slug, not global
