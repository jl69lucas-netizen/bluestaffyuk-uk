"""`scripts/page_intake.py` — block 0 of the board: a page's starting state, found by looking.

The page-build brief opens every page with a target block whose rule is that the mode is
determined by looking, never assumed. Project 5's 28 city pages start in different states —
stubs with no verbatim set (Known Issue 79), indexable bodies printing retired terms (Known
Issue 65), rows with an empty h1 (Known Issue 59) — and without an intake each builder derives
that again from nothing, 28 times.

The unit tests build a small tree in tmp_path so they pin behaviour, not today's data. The
last tests run the intake on this repo, and one closes Known Issue 63: a city page's built
file now reads as stale when the dynamic route that renders it changes.
"""
import json
import pathlib
import sys
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_page_board as BPB  # noqa: E402
import page_intake as PI  # noqa: E402
import pageboard as PB  # noqa: E402
import retired_facts_check as RFC  # noqa: E402

LOCKED_SETTINGS = {"deposit_gbp": 500, "delivery_min_gbp": 200, "delivery_max_gbp": 350}
PRICE_MATRIX = {"male_gbp": 1500, "female_gbp": 1700, "deposit_gbp": 500}


def page(body, robots="index, follow"):
    return (f'<html><head><meta name="robots" content="{robots}"></head><body>'
            f'<header><a href="/uk-locations/stubtown/">Stubtown</a></header>'
            f"<main>{body}</main></body></html>")


def repo(tmp_path):
    """Two cities (a noindex stub with an empty h1, an indexable migrated page), one rebuilt
    page, the data files the intake reads, and a built dist/ with a sitemap."""
    d = tmp_path / "data"
    for sub in ("facts", "verbatim", "boards", "queries"):
        (d / sub).mkdir(parents=True)
    (d / "locations.json").write_text(json.dumps([
        {"slug": "stubtown", "h1": "", "robots": "noindex, follow", "defects": ["empty-h1", "stub"],
         "body_html": ""},
        {"slug": "oldtown", "h1": "Blue Staffy Puppies Oldtown", "defects": [],
         "robots": "index, follow", "body_html": "<p>Delivery is a flat £100.</p>"},
    ]), encoding="utf-8")
    (d / "page-map.json").write_text(json.dumps({"pages": [
        {"url": "/uk-locations/stubtown/", "h1": "", "baseline_gsc": "NOT FETCHED — test barrier"},
        {"url": "/uk-locations/oldtown/", "h1": "Blue Staffy Puppies Oldtown",
         "baseline_gsc": "NOT FETCHED — test barrier"},
        {"url": "/done-page/", "h1": "Done", "baseline_gsc": "NOT FETCHED — test barrier"},
    ]}), encoding="utf-8")
    (d / "facts/rebuilt.json").write_text(json.dumps(["done-page"]), encoding="utf-8")
    (d / "verbatim/applies.json").write_text(json.dumps({"slugs": ["done-page"]}), encoding="utf-8")
    (d / "verbatim/done-page.json").write_text(json.dumps(
        {"h1": "Done", "headings": [{"text": "A"}, {"text": "B"}], "openings": [],
         "faq_questions": ["Q?"], "alts": []}), encoding="utf-8")
    (d / "settings.json").write_text(json.dumps(LOCKED_SETTINGS), encoding="utf-8")
    (d / "price-matrix.json").write_text(json.dumps(PRICE_MATRIX), encoding="utf-8")
    (d / "queries/oldtown.json").write_text("{}", encoding="utf-8")
    llm = tmp_path / "docs/research/llm-intel"
    llm.mkdir(parents=True)
    (llm / "oldtown-2026-09-25.json").write_text(json.dumps({"fetched": {"status": "ok"}}),
                                                 encoding="utf-8")
    dist = tmp_path / "dist"
    for route, html in {
        "uk-locations/stubtown": page("<p>Coming soon.</p>", robots="noindex, follow"),
        "uk-locations/oldtown": page("<p>Puppies £850 to £1,500. Delivery a flat £100. "
                                     "The deposit is non-refundable. We are council-licensed. "
                                     "Deposit £500.</p>"),
        "done-page": page('<p>See <a href="/uk-locations/oldtown/">Oldtown</a>.</p>'),
    }.items():
        (dist / route).mkdir(parents=True)
        (dist / route / "index.html").write_text(html, encoding="utf-8")
    (dist / "location-sitemap.xml").write_text(
        "<urlset><url><loc>https://x/uk-locations/oldtown/</loc></url></urlset>", encoding="utf-8")
    return tmp_path


def test_a_stub_city_reads_as_a_stub_with_its_empty_h1_and_no_verbatim_set(tmp_path):
    it = PI.intake("stubtown", repo(tmp_path))
    assert it["mode"] == "stub" and it["route"] == "uk-locations/stubtown"
    assert it["robots"] == "noindex, follow", "robots is read from the built page"
    assert it["h1"] == "EMPTY"
    assert it["verbatim"].startswith("stub — no verbatim set")
    assert it["sitemap"] is False and it["question_file"] is False and it["llm_intel"] is None
    assert it["page_type"] == "location"


def test_a_migrated_city_reports_its_retired_terms_sitemap_and_research(tmp_path):
    it = PI.intake("oldtown", repo(tmp_path))
    assert it["mode"] == "migrated" and it["sitemap"] is True
    # The detection is retired_facts_check's (check:retired), so "£850 to £1,500" is read
    # as the one retired band it is, not as a lone £850.
    assert it["retired"] == {"non-refundable": 1, "council-licensed": 1,
                             "£850–£1,500 (not a locked amount)": 1,
                             "£100 (not a locked amount)": 1}
    assert it["question_file"] is True
    assert it["llm_intel"] == {"file": "docs/research/llm-intel/oldtown-2026-09-25.json",
                               "status": "ok"}
    assert it["verbatim"].startswith("not extracted — run python3 scripts/verbatim_set_check.py")
    assert it["baseline"] == "NOT FETCHED — test barrier"


def test_inbound_links_count_other_pages_main_not_the_site_chrome(tmp_path):
    root = repo(tmp_path)
    # done-page links oldtown from its <main>; every page's header links stubtown.
    assert PI.intake("oldtown", root)["inbound_links"] == 1
    assert PI.intake("stubtown", root)["inbound_links"] == 0


def test_a_rebuilt_page_reads_as_rebuilt_with_its_verbatim_count(tmp_path):
    it = PI.intake("done-page", repo(tmp_path))
    assert it["mode"] == "rebuilt"
    assert it["verbatim"] == 4 and it["verbatim_applies"] is True
    assert it["built"]["path"] == "dist/done-page/index.html"


def test_a_page_known_only_by_its_board_is_new(tmp_path):
    root = repo(tmp_path)
    (root / "data/boards/fresh-compare.json").write_text(json.dumps(
        {"meta": {"slug": "fresh-compare", "page_type": "comparison", "status": "draft"},
         "h1": {"variants": ["Blue or Black"], "recommended": 0, "pick": None}}), encoding="utf-8")
    it = PI.intake("fresh-compare", root)
    assert it["mode"] == "new" and it["board"] == "draft" and it["built"] is None
    assert it["page_type"] == "comparison" and it["h1"] == "Blue or Black"
    assert it["verbatim"] == "none — a new page has no migrated wording"
    assert it["baseline"] == "NOT FETCHED — no Search Console export under data/analytics/"


def test_an_unknown_slug_is_refused(tmp_path):
    root = repo(tmp_path)
    with pytest.raises(PI.UnknownSlug):
        PI.intake("nowhere", root)
    with pytest.raises(PI.UnknownSlug):
        PI.intake("../etc", root)


def test_the_locked_amounts_come_from_the_data_files(tmp_path):
    """The intake judges £ figures with check:retired's locked set, read from the data files:
    the deposit, the two prices and balances, the delivery band ends, £0 and the two ranges."""
    root = repo(tmp_path)
    singles, ranges = PI.locked_amounts(root)
    assert (singles, ranges) == RFC.locked_amounts(root)
    assert singles == {0, 200, 350, 500, 1000, 1200, 1500, 1700}
    assert ranges == {(200, 350), (1500, 1700)}


def test_former_home_and_former_city_claims_are_hits(tmp_path):
    """The same four kinds check:retired fails on: amount, term, former city, former home."""
    root = repo(tmp_path)
    (root / "dist/uk-locations/oldtown/index.html").write_text(
        page("<p>Raised in our Glasgow home in Coltmuir.</p>"), encoding="utf-8")
    assert PI.intake("oldtown", root)["retired"] == {
        "Glasgow (former city)": 1, "our glasgow home (former home)": 1,
        "coltmuir (former home)": 1}


def test_render_md_is_a_two_column_table_with_every_field(tmp_path):
    md = PI.render_md(PI.intake("oldtown", repo(tmp_path)))
    lines = md.splitlines()
    assert lines[:2] == ["| Field | Value |", "|---|---|"]
    for field in ("Mode", "Robots", "Built page", "Sitemap entry", "H1", "Verbatim set",
                  "Question file", "LLM intel", "Board", "Search Console baseline",
                  "Inbound links (other pages' main)", "Retired-term hits"):
        assert any(l.startswith(f"| {field} |") for l in lines), field


def test_main_exits_2_on_an_unknown_slug_and_0_on_a_known_one(capsys):
    assert PI.main(["no-such-page-anywhere"]) == 2
    assert "page-intake ERROR" in capsys.readouterr().out
    assert PI.main(["blue-staffy-puppies-manchester-uk", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["mode"] in PI.MODES and out["route"] == "uk-locations/blue-staffy-puppies-manchester-uk"


# ── block 0 on the board ──────────────────────────────────────────────────────────────────

def test_the_board_renders_block_0_when_given_an_intake():
    board = PB.load_board("_demo")
    it = PI.intake("index")
    html = BPB.render(board, PB.load_ontology(), PB.load_ledger(), live={}, thumbs={},
                      slug="_demo", intake=it)
    assert 'data-title="0. Intake — found by looking"' in html
    assert "| Mode | rebuilt |" in html
    first = html.index('data-title="0. Intake')
    assert first < html.index('data-title="1. Brief"'), "block 0 comes before the brief"


def test_the_board_has_no_block_0_without_an_intake():
    html = BPB.render(PB.load_board("_demo"), PB.load_ontology(), PB.load_ledger(), live={},
                      thumbs={}, slug="_demo")
    assert "0. Intake" not in html


# ── this repo ─────────────────────────────────────────────────────────────────────────────

def test_every_city_row_has_an_intake_and_the_empty_h1s_are_counted():
    rows = json.loads((ROOT / "data/locations.json").read_text(encoding="utf-8"))
    intakes = [PI.intake(r["slug"]) for r in rows]
    assert {i["mode"] for i in intakes} <= set(PI.MODES)
    assert sum(i["h1"] == "EMPTY" for i in intakes) == sum(not r["h1"] for r in rows)


# ── Known Issue 63: a city page's freshness sees the template that renders it ──────────────

def test_a_city_page_is_stale_after_its_dynamic_route_changes(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "oldtown"}]),
                                                  encoding="utf-8")
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    template = tmp_path / "src/pages/uk-locations/[slug].astro"
    template.write_text("template", encoding="utf-8")
    built = tmp_path / "dist/uk-locations/oldtown/index.html"
    built.parent.mkdir(parents=True)
    time.sleep(0.01)
    built.write_text("x", encoding="utf-8")
    assert PB.dist_page_is_fresh(built, tmp_path, slug="oldtown")
    time.sleep(0.01)
    template.write_text("edited", encoding="utf-8")
    assert not PB.dist_page_is_fresh(built, tmp_path, slug="oldtown"), (
        "Known Issue 63: an edit to the dynamic route must make the city page stale")


def test_the_city_hub_page_is_not_one_of_its_sources(tmp_path):
    """Only the `[...]` route files render a city; the hub's own index.astro does not."""
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "oldtown"}]),
                                                  encoding="utf-8")
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    hub = tmp_path / "src/pages/uk-locations/index.astro"
    hub.write_text("hub", encoding="utf-8")
    built = tmp_path / "dist/uk-locations/oldtown/index.html"
    built.parent.mkdir(parents=True)
    time.sleep(0.01)
    built.write_text("x", encoding="utf-8")
    time.sleep(0.01)
    hub.write_text("edited", encoding="utf-8")
    assert PB.dist_page_is_fresh(built, tmp_path, slug="oldtown")
