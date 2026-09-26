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

# The offenders live on 2026-09-26 (Known Issue 65; the former-home and former-city ones
# also Known Issue 16). The ratchet is by IDENTITY, not just by count: every entry must be
# one of FROZEN, and the list must be exactly ALLOWLIST_CEILING long.
# TO LOWER IT (each project 5 city rebuild): delete the page's entries from
# data/quality/retired-facts-allowlist.json and lower ALLOWLIST_CEILING by the number
# deleted, in the same commit. Leave FROZEN alone (a key that is gone can never return,
# because the count would no longer match). Never add to FROZEN or raise the ceiling: a new
# retired fact is fixed on the page.
ALLOWLIST_CEILING = 57
FROZEN = frozenset({
    "data:locations.json/blue-staffy-puppies-aberdeen/body_html:amount:£1,100",
    "data:locations.json/blue-staffy-puppies-aberdeen/body_html:amount:£100",
    "data:locations.json/blue-staffy-puppies-aberdeen/body_html:amount:£850",
    "data:locations.json/blue-staffy-puppies-aberdeen/body_html:amount:£850–£1,200",
    "data:locations.json/blue-staffy-puppies-dundee/body_html:amount:£100",
    "data:locations.json/blue-staffy-puppies-edinburgh/body_html:amount:£1,100",
    "data:locations.json/blue-staffy-puppies-edinburgh/body_html:amount:£100",
    "data:locations.json/blue-staffy-puppies-edinburgh/body_html:amount:£850",
    "data:locations.json/blue-staffy-puppies-edinburgh/body_html:amount:£850–£1,200",
    "data:locations.json/blue-staffy-puppies-hull/body_html:amount:£100",
    "data:locations.json/blue-staffy-puppies-hull/body_html:term:non-refundable",
    "data:locations.json/blue-staffy-puppies-inverness/body_html:amount:£100",
    "data:locations.json/blue-staffy-puppies-middlesbrough/body_html:amount:£100",
    "data:locations.json/blue-staffy-puppies-oxford/body_html:amount:£100",
    "data:locations.json/blue-staffy-puppies-sunderland/body_html:amount:£1,000–£1,100",
    "data:locations.json/blue-staffy-puppies-sunderland/body_html:amount:£100",
    "data:locations.json/blue-staffy-puppies-uk/body_html:amount:£300",
    "data:locations.json/blue-staffy-puppies-uk/body_html:amount:£850–£1,200",
    "data:locations.json/blue-staffy-puppies-uk/body_html:city:Glasgow",
    "data:locations.json/blue-staffy-puppies-uk/body_html:home:from our glasgow home",
    "data:locations.json/blue-staffy-puppies-uk/body_html:home:our glasgow",
    "data:locations.json/blue-staffy-puppies-uk/body_html:term:council-licensed",
    "data:locations.json/blue-staffy-puppies-york/body_html:amount:£100",
    "data:locations.json/staffy-breeding-dogs-glasgow/body_html:amount:£850–£1,200",
    "data:locations.json/staffy-breeding-dogs-glasgow/body_html:city:Glasgow",
    "data:locations.json/staffy-breeding-dogs-glasgow/body_html:home:our glasgow home",
    "data:locations.json/staffy-breeding-dogs-glasgow/description:city:Glasgow",
    "data:locations.json/staffy-breeding-dogs-glasgow/description:home:based in glasgow",
    "data:locations.json/staffy-breeding-dogs-glasgow/h1:city:Glasgow",
    "data:locations.json/staffy-breeding-dogs-glasgow/title:city:Glasgow",
    "dist:uk-locations/blue-staffy-puppies-aberdeen:amount:£1,100",
    "dist:uk-locations/blue-staffy-puppies-aberdeen:amount:£100",
    "dist:uk-locations/blue-staffy-puppies-aberdeen:amount:£850",
    "dist:uk-locations/blue-staffy-puppies-aberdeen:amount:£850–£1,200",
    "dist:uk-locations/blue-staffy-puppies-dundee:amount:£100",
    "dist:uk-locations/blue-staffy-puppies-edinburgh:amount:£1,100",
    "dist:uk-locations/blue-staffy-puppies-edinburgh:amount:£100",
    "dist:uk-locations/blue-staffy-puppies-edinburgh:amount:£850",
    "dist:uk-locations/blue-staffy-puppies-edinburgh:amount:£850–£1,200",
    "dist:uk-locations/blue-staffy-puppies-hull:amount:£100",
    "dist:uk-locations/blue-staffy-puppies-hull:term:non-refundable",
    "dist:uk-locations/blue-staffy-puppies-inverness:amount:£100",
    "dist:uk-locations/blue-staffy-puppies-middlesbrough:amount:£100",
    "dist:uk-locations/blue-staffy-puppies-oxford:amount:£100",
    "dist:uk-locations/blue-staffy-puppies-sunderland:amount:£1,000–£1,100",
    "dist:uk-locations/blue-staffy-puppies-sunderland:amount:£100",
    "dist:uk-locations/blue-staffy-puppies-uk:amount:£300",
    "dist:uk-locations/blue-staffy-puppies-uk:amount:£850–£1,200",
    "dist:uk-locations/blue-staffy-puppies-uk:city:Glasgow",
    "dist:uk-locations/blue-staffy-puppies-uk:home:from our glasgow home",
    "dist:uk-locations/blue-staffy-puppies-uk:home:our glasgow",
    "dist:uk-locations/blue-staffy-puppies-uk:term:council-licensed",
    "dist:uk-locations/blue-staffy-puppies-york:amount:£100",
    "dist:uk-locations/staffy-breeding-dogs-glasgow:amount:£850–£1,200",
    "dist:uk-locations/staffy-breeding-dogs-glasgow:city:Glasgow",
    "dist:uk-locations/staffy-breeding-dogs-glasgow:home:based in glasgow",
    "dist:uk-locations/staffy-breeding-dogs-glasgow:home:our glasgow home",
})

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
                                  "a £500 deposit, refundable", "£1,500–£1,700.",
                                  "£200 to £350", "£1,500 to £1,700", "£ 1,500", "£200-350",
                                  "£1,500–1,700", "£1,700 - £1,500", "£350 to £200"])
def test_locked_amounts_pass(text):
    assert R.amount_findings(text, LOCKED) == []


@pytest.mark.parametrize("text,found", [("Ground Transport — £100", ["£100"]),
                                        ("from £850 - £1,200", ["£850–£1,200"]),
                                        ("£1,000–£1,100 each", ["£1,000–£1,100"]),
                                        # "to" joins a range like a dash does, so "£200 to
                                        # £300" is ONE claim — a delivery band whose top end
                                        # is retired — and is reported as the band, the same
                                        # spelling a dashed band gets.
                                        ("£200 to £300", ["£200–£300"]),
                                        ("£1,000 to £1,200", ["£1,000–£1,200"]),
                                        ("from £850 to £1,200", ["£850–£1,200"]),
                                        ("£850-1,200", ["£850–£1,200"]),
                                        ("£ 100 delivery", ["£100"])])
def test_retired_amounts_fail(text, found):
    assert R.amount_findings(text, LOCKED) == found


def test_retired_wording_fails_in_any_case():
    found = R.html_findings("<p>A Non-Refundable deposit from a council licensed breeder.</p>", LOCKED)
    assert found == [("term", "non-refundable"), ("term", "council-licensed")]


def test_the_former_city_fails_in_prose_but_not_as_a_link_to_its_own_page():
    link = '<li><a href="/uk-locations/staffy-puppies-for-sale-glasgow/">Glasgow</a></li>'
    assert R.html_findings(link, LOCKED) == []
    # "from our Glasgow home" is also a former-HOME claim, which no page may make.
    assert R.html_findings("<p>collect from our Glasgow home</p>" + link, LOCKED) == [
        ("city", "Glasgow"), ("home", "from our glasgow home")]
    # The city's own page may name the city it is about.
    assert R.html_findings("<p>puppies in Glasgow</p>", LOCKED, city_page=True) == []


def test_the_former_home_is_a_claim_even_on_the_citys_own_pages():
    # The business moved to Carlisle (Known Issue 16). The for-sale-glasgow page may name the
    # city it is about; no page may say the kennel is there.
    claim = "<p>Collect from our Glasgow home in Coltmuir, G22.</p>"
    assert R.html_findings(claim, LOCKED, city_page=True) == [
        ("home", "from our glasgow home"), ("home", "coltmuir"), ("home", "g22")]
    assert R.html_findings("<p>Staffy puppies in Glasgow</p>", LOCKED, city_page=True) == []
    assert R.html_findings("<p>We are based in Carlisle, our home.</p>", LOCKED) == []


def test_only_the_for_sale_page_may_name_the_former_city(tmp_path):
    root = _tree(tmp_path, pages={
        "index": "<p>ok</p>",
        "uk-locations/staffy-breeding-dogs-glasgow": "<p>Breeding dogs in Glasgow, based in Glasgow.</p>",
        "uk-locations/staffy-puppies-for-sale-glasgow": "<p>Staffy puppies for sale in Glasgow.</p>"},
        rows=[{"slug": "staffy-puppies-for-sale-glasgow", "title": "Glasgow", "h1": "Glasgow",
               "description": "Puppies near Glasgow", "body_html": "<p>our Glasgow home</p>"}])
    r = R.run(root=root, allowlist=tmp_path / "none.json")
    assert r["new"] == [
        "data:locations.json/staffy-puppies-for-sale-glasgow/body_html:home:our glasgow home",
        "dist:uk-locations/staffy-breeding-dogs-glasgow:city:Glasgow",
        "dist:uk-locations/staffy-breeding-dogs-glasgow:home:based in glasgow"]


def test_head_meta_and_alt_text_are_read_but_urls_are_not():
    head = ('<meta name="description" content="Pups from £850 - £1,200">'
            '<meta property="og:title" content="A non-refundable deposit">'
            '<meta property="og:url" content="https://x.test/£5">'
            '<img src="/£7.jpg" alt="Our council licensed kennel">'
            '<a href="/£9/">ok</a>')
    assert R.html_findings(head, LOCKED) == [
        ("amount", "£850–£1,200"), ("term", "non-refundable"), ("term", "council-licensed")]


def test_entities_in_plain_text_fields_are_decoded(tmp_path):
    root = _tree(tmp_path, rows=[{"slug": "blue-staffy-puppies-hull", "title": "Hull",
                                  "h1": "Hull", "description": "Delivery &pound;100",
                                  "body_html": "<p>ok</p>"}])
    assert R.run(root=root, allowlist=tmp_path / "none.json")["new"] == [
        "data:locations.json/blue-staffy-puppies-hull/description:amount:£100"]


def test_a_missing_data_file_is_not_a_missing_build(tmp_path, capsys, monkeypatch):
    root = _tree(tmp_path)
    (root / "data/locations.json").unlink()
    monkeypatch.setattr(R, "ROOT", root)
    assert R.main([]) == 2
    out = capsys.readouterr().out
    assert "data/locations.json" in out and "build first" not in out
    (root / "data/locations.json").write_text("[]", encoding="utf-8")
    import shutil
    shutil.rmtree(root / "dist")
    (root / "dist").write_text("not a directory", encoding="utf-8")
    assert R.main([]) == 2
    assert "build first" in capsys.readouterr().out


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
    entries = set(_allow()["entries"])
    assert entries <= FROZEN, (
        f"not in the 2026-09-26 set: {sorted(entries - FROZEN)} — a new retired fact is fixed "
        "on the page, never added to the allowlist")
    assert len(entries) == ALLOWLIST_CEILING, (
        f"{len(entries)} allowlisted retired facts, ALLOWLIST_CEILING {ALLOWLIST_CEILING}: after "
        "deleting entries, lower the constant by the same number in the same commit")


def test_every_entry_is_known_issue_65_and_dated():
    doc = _allow()
    assert doc["known_issue"] == 65 and doc["since"] == "2026-09-26"
    assert doc["known_issues"] == [65, 16]
    for key, reason in doc["entries"].items():
        assert key.split(":", 1)[0] in ("dist", "data", "src"), key
        assert "Known Issue 65" in reason, key
        # A former-home or former-city entry is also the relocation (Known Issue 16).
        if key.split(":")[-2] in ("home", "city"):
            assert "Known Issue 16" in reason, key


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
