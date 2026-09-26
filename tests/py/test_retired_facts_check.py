"""`scripts/retired_facts_check.py` — the retired-facts sweep over dist/, data/ and src/.

Audit D5 / Known Issue 65: the fact lint reads the instruction tree only, so eleven indexable
city pages printing retired figures and wording were found by hand. These tests hold the
sweep's predicate on a scratch tree, and hold the allowlist of today's offenders to the one
direction it may move: down.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import retired_facts_check as R  # noqa: E402

# The offenders live on 2026-09-26 (Known Issue 65). Project 5 burns this down; raising it
# is a new retired fact, and that is what the gate exists to refuse.
ALLOWLIST_CEILING = 48

LOCKED = ({0, 500, 1500, 1700, 1000, 1200, 200, 350}, {(200, 350), (1500, 1700)})


def _tree(tmp_path, pages=None, rows=None, src=None):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/settings.json").write_text(json.dumps(
        {"deposit_gbp": 500, "delivery_min_gbp": 200, "delivery_max_gbp": 350}), encoding="utf-8")
    (tmp_path / "data/price-matrix.json").write_text(json.dumps(
        {"male_gbp": 1500, "female_gbp": 1700, "deposit_gbp": 500}), encoding="utf-8")
    (tmp_path / "data/locations.json").write_text(json.dumps(rows or []), encoding="utf-8")
    for key, markup in (pages or {"index": "<p>Hello</p>"}).items():
        d = tmp_path / "dist" if key == "index" else tmp_path / "dist" / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(markup, encoding="utf-8")
    (tmp_path / "src").mkdir()
    for rel, code in (src or {"pages/a.astro": "<p>ok</p>"}).items():
        (tmp_path / "src" / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "src" / rel).write_text(code, encoding="utf-8")
    return tmp_path


def test_the_locked_set_is_read_from_the_data_files():
    singles, ranges = R.locked_amounts(ROOT)
    s = json.loads((ROOT / "data/settings.json").read_text())
    p = json.loads((ROOT / "data/price-matrix.json").read_text())
    assert {p["male_gbp"], p["female_gbp"], p["deposit_gbp"], s["delivery_min_gbp"],
            s["delivery_max_gbp"], 0} <= singles
    assert p["male_gbp"] - p["deposit_gbp"] in singles        # the balance is arithmetic, not new
    assert (s["delivery_min_gbp"], s["delivery_max_gbp"]) in ranges
    assert (p["male_gbp"], p["female_gbp"]) in ranges


@pytest.mark.parametrize("text", ["£1,500", "£1500 - £1700", "£200–£350", "£0 to collect",
                                  "a £500 deposit, refundable", "£1,500–£1,700."])
def test_locked_amounts_pass(text):
    assert R.amount_findings(text, LOCKED) == []


@pytest.mark.parametrize("text,found", [("Ground Transport — £100", ["£100"]),
                                        ("from £850 - £1,200", ["£850–£1,200"]),
                                        ("£1,000–£1,100 each", ["£1,000–£1,100"]),
                                        ("£200 to £300", ["£300"])])
def test_retired_amounts_fail(text, found):
    assert R.amount_findings(text, LOCKED) == found


def test_retired_wording_fails_in_any_case():
    found = R.html_findings("<p>A Non-Refundable deposit from a council licensed breeder.</p>", LOCKED)
    assert found == [("term", "non-refundable"), ("term", "council-licensed")]


def test_the_former_city_fails_in_prose_but_not_as_a_link_to_its_own_page():
    link = '<li><a href="/uk-locations/staffy-puppies-for-sale-glasgow/">Glasgow</a></li>'
    assert R.html_findings(link, LOCKED) == []
    assert R.html_findings("<p>collect from our Glasgow home</p>" + link, LOCKED) == [("city", "Glasgow")]
    # The city's own page may name the city it is about.
    assert R.html_findings("<p>puppies in Glasgow</p>", LOCKED, city_page=True) == []


def test_json_ld_is_read_and_other_scripts_are_not():
    ld = '<script type="application/ld+json">{"priceRange":"£850 - £1,200"}</script>'
    js = '<script>const retired = "£850";</script>'
    assert R.html_findings(ld, LOCKED) == [("amount", "£850–£1,200")]
    assert R.html_findings(js + "<style>.a{content:'£9'}</style>", LOCKED) == []


def test_src_comments_are_history_and_code_is_copy(tmp_path):
    root = _tree(tmp_path, src={
        "pages/a.astro": "---\n// the old £850 band is dropped\nconst url = 'https://x.test/£5';\n---\n"
                         "{/* non-refundable */}<!-- council-licensed --><p>ok</p>",
        "lib/faq.ts": "const t = settings.deposit_refundable ? 'refundable' : 'non-refundable';\n",
        "pages/b.astro": "<p>A £300 deposit</p>"})
    found, n = R.scan_src(root, LOCKED)
    assert n == 3
    assert sorted(found) == ["src:src/pages/a.astro:amount:£5", "src:src/pages/b.astro:amount:£300"]


def test_run_reports_new_allowed_and_stale(tmp_path):
    root = _tree(tmp_path, pages={
        "index": "<p>£1,500</p>",
        "uk-locations/blue-staffy-puppies-hull": "<p>Ground Transport — £100</p>",
        "uk-locations/blue-staffy-puppies-york": "<p>a non-refundable deposit</p>",
        "kit-preview": "<p>£999 specimen</p>"},
        rows=[{"slug": "blue-staffy-puppies-hull", "title": "Hull", "h1": "Hull",
               "description": "Glasgow breeders", "body_html": "<p>£100</p>"}])
    allow = tmp_path / "allow.json"
    allow.write_text(json.dumps({"entries": {
        "dist:uk-locations/blue-staffy-puppies-hull:amount:£100": "KI 65",
        "dist:uk-locations/blue-staffy-puppies-leeds:amount:£100": "KI 65"}}), encoding="utf-8")
    r = R.run(root=root, allowlist=allow)
    assert r["examined"] == {"dist": 3, "data": 6, "src": 1}      # kit-preview is a specimen
    assert r["allowed"] == ["dist:uk-locations/blue-staffy-puppies-hull:amount:£100"]
    assert r["new"] == ["data:locations.json/blue-staffy-puppies-hull/body_html:amount:£100",
                        "data:locations.json/blue-staffy-puppies-hull/description:city:Glasgow",
                        "dist:uk-locations/blue-staffy-puppies-york:term:non-refundable"]
    assert r["stale"] == ["dist:uk-locations/blue-staffy-puppies-leeds:amount:£100"]


def test_no_dist_is_not_a_pass(tmp_path):
    root = _tree(tmp_path)
    import shutil
    shutil.rmtree(root / "dist")
    with pytest.raises(FileNotFoundError):
        R.run(root=root, allowlist=tmp_path / "none.json")


# ── the real allowlist ────────────────────────────────────────────────────────────────────
def _allow():
    return json.loads(R.ALLOWLIST.read_text(encoding="utf-8"))


def test_the_allowlist_only_shrinks():
    entries = _allow()["entries"]
    assert len(entries) <= ALLOWLIST_CEILING, (
        f"{len(entries)} allowlisted retired facts, ceiling {ALLOWLIST_CEILING}: a new retired "
        "fact is fixed on the page, never added to the allowlist")


def test_every_entry_is_known_issue_65_and_dated():
    doc = _allow()
    assert doc["known_issue"] == 65 and doc["since"] == "2026-09-26"
    for key, reason in doc["entries"].items():
        assert key.split(":", 1)[0] in ("dist", "data", "src"), key
        assert "Known Issue 65" in reason, key


def test_no_rebuilt_page_is_ever_allowlisted():
    rebuilt = set(json.loads((ROOT / "data/facts/rebuilt.json").read_text()))
    for key in _allow()["entries"]:
        where = key.split(":")[1]
        page = where.split("/")[-1] if key.startswith("dist:") else where.split("/")[1] \
            if where.startswith("locations.json/") else where
        assert page not in rebuilt, f"{key}: a rebuilt page fixes its retired facts, it is never excused"


@pytest.mark.skipif(not (ROOT / "dist").exists(), reason="needs a build (npm run build)")
def test_the_repo_sweep_is_green_and_the_allowlist_is_exact():
    r = R.run()
    assert r["new"] == [], r["new"]
    assert r["stale"] == [], r["stale"]
    assert len(r["allowed"]) == len(_allow()["entries"])
