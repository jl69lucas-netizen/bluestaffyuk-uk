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
import os
import pathlib
import sys

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
        "done-page": page('<h1>Done, rebuilt</h1>'
                          '<p>See <a href="/uk-locations/oldtown/">Oldtown</a>.</p>'),
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
    assert it["h1"] == "EMPTY" and it["h1_source"] == "migrated row"
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
    assert it["baseline"] == "NOT FETCHED — test barrier (data/page-map.json)"


def test_inbound_links_count_other_pages_main_not_the_site_chrome(tmp_path):
    root = repo(tmp_path)
    # done-page links oldtown from its <main>; every page's header links stubtown.
    assert PI.intake("oldtown", root)["inbound_links"] == 1
    assert PI.intake("stubtown", root)["inbound_links"] == 0


def test_inbound_links_skip_the_kit_specimen_routes(tmp_path):
    """A specimen route (board-preview/, kit-preview/) is not a page a reader reaches; a
    real page whose first segment merely starts with the same letters still counts."""
    root = repo(tmp_path)
    link = page('<p><a href="/uk-locations/oldtown/">Oldtown</a></p>')
    for route in ("board-preview/demo", "kit-preview", "board-previews-guide"):
        (root / "dist" / route).mkdir(parents=True)
        (root / "dist" / route / "index.html").write_text(link, encoding="utf-8")
    assert PI.intake("oldtown", root)["inbound_links"] == 2, "done-page + board-previews-guide"


def test_the_root_is_listed_only_by_its_own_loc_and_its_inbound_links_are_not_counted(tmp_path):
    root = repo(tmp_path)
    pm = json.loads((root / "data/page-map.json").read_text(encoding="utf-8"))
    pm["pages"].append({"url": "/", "h1": "Home", "baseline_gsc": "NOT FETCHED — test barrier"})
    (root / "data/page-map.json").write_text(json.dumps(pm), encoding="utf-8")
    (root / "dist/index.html").write_text(page("<h1>Home</h1>"), encoding="utf-8")
    it = PI.intake("index", root)
    assert it["sitemap"] is False, "…/oldtown/</loc> is not the root's entry"
    assert it["inbound_links"] is None
    assert dict(PI.rows(it))["Inbound links (other pages' main)"] == "not counted for the root"
    (root / "dist/page-sitemap.xml").write_text(
        "<urlset><url><loc>https://x/</loc></url></urlset>", encoding="utf-8")
    assert PI.intake("index", root)["sitemap"] is True


def test_a_rebuilt_page_reads_as_rebuilt_with_its_verbatim_count(tmp_path):
    it = PI.intake("done-page", repo(tmp_path))
    assert it["mode"] == "rebuilt"
    assert it["verbatim"] == 4 and it["verbatim_applies"] is True
    assert it["built"]["path"] == "dist/done-page/index.html"


def test_a_rebuilt_page_reports_its_built_h1_not_the_migrated_row(tmp_path):
    it = PI.intake("done-page", repo(tmp_path))
    assert (it["h1"], it["h1_source"]) == ("Done, rebuilt", "built")
    assert ("H1 (built)", "Done, rebuilt") in PI.rows(it)


def test_a_city_scaffolds_placeholder_h1_is_not_read_as_the_pages_h1(tmp_path):
    """A city's component scaffold (the London component design pass, Plan 2) ships an H1 of
    PLACEHOLDER copy, marked `data-city-scaffold`. The page run's intake must not take that as the
    page's starting H1: it falls back as if nothing were built, to the board or the data row."""
    root = repo(tmp_path)
    (root / "dist/uk-locations/stubtown/index.html").write_text(page(
        '<section class="kit-hero" data-city-scaffold="stubtown"><h1>Placeholder Question?</h1></section>',
        robots="noindex, follow"), encoding="utf-8")
    it = PI.intake("stubtown", root)
    assert (it["h1"], it["h1_source"]) == ("EMPTY", "migrated row")


def test_the_h1_falls_back_to_the_board_pick_then_the_migrated_row(tmp_path):
    root = repo(tmp_path)
    (root / "dist/done-page/index.html").write_text(page("<p>no heading</p>"), encoding="utf-8")
    assert (PI.intake("done-page", root)["h1"], PI.intake("done-page", root)["h1_source"]) == (
        "Done", "migrated row")
    (root / "data/boards/done-page.json").write_text(json.dumps(
        {"meta": {"slug": "done-page", "page_type": "guide", "status": "approved"},
         "h1": {"variants": ["Picked", "Other"], "recommended": 1, "pick": 0}}), encoding="utf-8")
    it = PI.intake("done-page", root)
    assert (it["h1"], it["h1_source"]) == ("Picked", "board pick")


def test_an_excluded_page_says_so_and_why(tmp_path):
    root = repo(tmp_path)
    (root / "data/verbatim/applies.json").write_text(json.dumps(
        {"slugs": [], "excluded": {"comment": "x", "done-page": "rebuilt before rule 15"}}),
        encoding="utf-8")
    (root / "data/verbatim/done-page.json").unlink()
    it = PI.intake("done-page", root)
    assert it["verbatim"] == "excluded from rule 15 — rebuilt before rule 15"
    assert it["verbatim_applies"] is False
    assert dict(PI.rows(it))["Rule 15 applies"] == "no"


def test_a_rebuilt_page_with_no_set_on_disk_is_not_called_new(tmp_path):
    root = repo(tmp_path)
    (root / "data/verbatim/done-page.json").unlink()
    it = PI.intake("done-page", root)
    assert it["mode"] == "rebuilt" and not it["verbatim"].startswith("none — a new page")


def test_the_three_pages_rebuilt_before_rule_15_read_as_excluded():
    excluded = json.loads((ROOT / "data/verbatim/applies.json").read_text(encoding="utf-8"))[
        "excluded"]
    slugs = sorted(k for k in excluded if k != "comment")
    assert slugs == ["privacy-policy-uk", "thank-you-blue-staffy-puppies-journey",
                     "uk-blue-staffy-breeders-contact"]
    for slug in slugs:
        it = PI.intake(slug)
        assert it["mode"] == "rebuilt"
        assert it["verbatim"] == f"excluded from rule 15 — {excluded[slug]}", slug
        assert it["verbatim_applies"] is False


def test_robots_falls_back_to_the_page_map_row_before_not_built(tmp_path):
    root = repo(tmp_path)
    pm = json.loads((root / "data/page-map.json").read_text(encoding="utf-8"))
    pm["pages"].append({"url": "/unbuilt/", "h1": "U", "robots": "noindex, nofollow",
                        "baseline_gsc": "NOT FETCHED — test barrier"})
    pm["pages"].append({"url": "/bare/", "h1": "B", "baseline_gsc": "NOT FETCHED — test barrier"})
    (root / "data/page-map.json").write_text(json.dumps(pm), encoding="utf-8")
    assert PI.intake("unbuilt", root)["robots"] == "noindex, nofollow"
    assert PI.intake("bare", root)["robots"] == "NOT FETCHED — not built yet"


def test_a_malformed_data_file_is_a_clear_intake_error(tmp_path):
    root = repo(tmp_path)
    (root / "data/page-map.json").write_text("[]", encoding="utf-8")
    with pytest.raises(PI.IntakeError, match="data/page-map.json"):
        PI.intake("oldtown", root)
    root2 = repo(tmp_path / "b")
    (root2 / "data/boards/oldtown.json").write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(PI.IntakeError, match="data/boards/oldtown.json"):
        PI.intake("oldtown", root2)
    root3 = repo(tmp_path / "c")
    (root3 / "data/locations.json").write_text("not json", encoding="utf-8")
    with pytest.raises(PI.IntakeError, match="data/locations.json is not readable JSON"):
        PI.intake("oldtown", root3)


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
    for field in ("Mode", "Robots", "Built page", "Sitemap entry", "H1 (migrated row)",
                  "Verbatim set", "Rule 15 applies", "Question file", "LLM intel", "Board", "Search Console baseline",
                  "Inbound links (other pages' main)", "Retired-term hits"):
        assert any(l.startswith(f"| {field} |") for l in lines), field


def test_main_exits_2_on_an_unknown_slug_and_0_on_a_known_one(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(PI, "ROOT", repo(tmp_path))
    assert PI.main(["nowhere"]) == 2
    assert "page-intake ERROR" in capsys.readouterr().out
    assert PI.main(["oldtown", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["mode"] == "migrated" and out["route"] == "uk-locations/oldtown"
    (tmp_path / "data/page-map.json").write_text("{\"pages\": 3}", encoding="utf-8")
    assert PI.main(["oldtown"]) == 2
    assert "page-intake ERROR" in capsys.readouterr().out


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


def test_block_0_escapes_every_value_and_keeps_the_rest_of_the_board():
    """Block 0 goes through the board's md(): an H1 carrying markdown, a pipe and a
    `</script>` shows literally and cannot end the text/markdown block early."""
    board = PB.load_board("_demo")
    args = (board, PB.load_ontology(), PB.load_ledger(), {}, {}, "_demo")
    it = dict(PI.intake("index"), h1="A *b* </script> |")
    html = BPB.render(*args, intake=it)
    plain = BPB.render(*args)
    assert html.count("</script>") == plain.count("</script>") + 1, "only block 0's own close"
    assert "A \\*b\\* &lt;/script&gt; \\|" in html
    assert html.index('data-title="0. Intake') < html.index('data-title="1. Brief"')
    assert html.count("data-title=") == plain.count("data-title=") + 1


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
    built.write_text("x", encoding="utf-8")
    for f in (tmp_path / "data/locations.json", template):
        os.utime(f, (1_000_000, 1_000_000))
    os.utime(built, (2_000_000, 2_000_000))
    assert PB.dist_page_is_fresh(built, tmp_path, slug="oldtown")
    os.utime(template, (3_000_000, 3_000_000))
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
    built.write_text("x", encoding="utf-8")
    os.utime(tmp_path / "data/locations.json", (1_000_000, 1_000_000))
    os.utime(built, (2_000_000, 2_000_000))
    os.utime(hub, (3_000_000, 3_000_000))
    assert PB.dist_page_is_fresh(built, tmp_path, slug="oldtown")
