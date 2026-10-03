"""scripts/board_extras.py — board blocks 2b, 8a, 8b and 8c (breeder q12, 2026-10-02).

2b  the Google result preview: pixel widths from a pinned Arial table, never characters
8a  the structured-data preview: built from data files only, no AggregateRating, no review
    markup that data/reviews.json does not hold, placeholders printed as placeholders
8b  internal links in and out: out from the record, in from dist/ read with an HTML parser
8c  page weight and LCP budget: bytes from public/, the budget cited from the repo or none
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import board_extras as BX  # noqa: E402

LONDON = "blue-staffy-puppies-london"


@pytest.fixture(scope="module")
def london():
    return json.loads((ROOT / "data/boards" / f"{LONDON}.json").read_text(encoding="utf-8"))


def _mini(**over):
    b = {"meta": {"slug": "mini-page", "page_type": "location"},
         "brief": {"schema": {"types": ["LocalBusiness", "BreadcrumbList", "FAQPage"]}},
         "meta_set": {"titles": ["Short Title"], "descriptions": ["A short description."],
                      "recommended": {"title": 0, "description": 0},
                      "pick": {"title": None, "description": None}},
         "assets": [], "sections": []}
    b.update(over)
    return b


# ── 2b: pixel widths ────────────────────────────────────────────────────────────────────
def test_the_width_table_is_pinned_for_every_character_class():
    for ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,:;!?'\"-()–£|&/":
        assert ch in BX.ARIAL, ch
    # Arial's own metrics, per 1000 em: the narrow and the wide ends and the digits.
    assert BX.ARIAL["i"] == 222 and BX.ARIAL["W"] == 944 and BX.ARIAL["0"] == 556
    assert BX.ARIAL[" "] == 278 and BX.ARIAL["–"] == 556 and BX.ARIAL["£"] == 556


def test_pixel_width_is_by_glyph_not_by_character_count():
    assert BX.text_px("iiii", 20) < BX.text_px("WWWW", 20)
    assert BX.text_px("W", 20) == pytest.approx(944 * 20 / 1000)
    assert BX.text_px("", 20) == 0


def test_truncation_cuts_on_a_word_and_shows_an_ellipsis():
    long = "Blue Staffy Puppies London " * 6
    shown, cut = BX.truncate(long.strip(), 20, BX.TITLE_PX)
    assert cut and shown.endswith("…")
    assert BX.text_px(shown, 20) <= BX.TITLE_PX
    assert not shown[:-1].rstrip().endswith("Puppi")      # whole words only
    short, cut2 = BX.truncate("Short", 20, BX.TITLE_PX)
    assert short == "Short" and not cut2


def test_the_breadcrumb_separator_is_333():
    assert BX.ARIAL["›"] == 333


def test_description_has_three_verdicts():
    assert BX.desc_verdict(BX.DESC_PX) == "fits"
    assert BX.desc_verdict(BX.DESC_PX + 1).startswith("may be cut")
    assert BX.desc_verdict(BX.DESC_MAX_PX) .startswith("may be cut")
    assert BX.desc_verdict(BX.DESC_MAX_PX + 1) == "cut"
    assert (BX.DESC_PX, BX.DESC_MAX_PX) == (920, 990)


def test_mobile_title_wraps_to_two_lines_at_most():
    lines, cut = BX.wrap("Blue Staffy Puppies London " * 6, 16, BX.MOBILE_LINE_PX, 2)
    assert len(lines) == 2 and cut and lines[-1].endswith("…")
    for ln in lines:
        assert BX.text_px(ln, 16) <= BX.MOBILE_LINE_PX


def test_serp_block_shows_the_picked_pair_the_placeholder_url_and_the_label(london):
    import pageboard as PB
    out = BX.serp_block(london, ROOT)
    t, d = PB.meta_pick(london)
    assert BX.esc(t.split()[0]) in out
    assert "SITE_URL_PLACEHOLDER" in out and "uk-locations" in out
    assert BX.APPROX_LABEL in out
    assert "600px" in out and "360px" in out
    assert "920px" in out and "990px" in out                     # both description limits
    assert BX.MOBILE_DESC_RULE in out
    assert "padding:12px 0" not in out                            # one padding per mock
    # every option of block 2 carries its own pixel width
    for v in london["meta_set"]["titles"] + london["meta_set"]["descriptions"]:
        assert BX.md_cell(v) in out


def test_serp_block_follows_the_breeders_pick():
    b = _mini(meta_set={"titles": ["First Title", "Second Title"],
                        "descriptions": ["First description.", "Second description."],
                        "recommended": {"title": 0, "description": 0},
                        "pick": {"title": 1, "description": 1}})
    mock = BX.serp_mock(b, ROOT)
    assert "Second Title" in mock and "First Title" not in mock


# ── 8a: structured data ─────────────────────────────────────────────────────────────────
def _types(graph):
    return [n.get("@type") for n in graph]


def test_jsonld_carries_every_type_the_brief_plans(london):
    graph = BX.jsonld_graph(london, ROOT)
    types = set(_types(graph))
    for t in ("LocalBusiness", "Person", "FAQPage", "BreadcrumbList", "Product"):
        assert t in types, t
    products = [n for n in graph if n["@type"] == "Product"]
    assert products and all(p["offers"]["@type"] == "Offer" for p in products)
    assert all(isinstance(p["offers"]["price"], int) for p in products)   # a number, as [slug].astro


def test_parity_with_schema_astro(london):
    graph = BX.jsonld_graph(london, ROOT)
    site = next(n for n in graph if n["@type"] == "WebSite")
    assert site["@id"] == "https://SITE_URL_PLACEHOLDER/#website"
    biz = next(n for n in graph if n["@type"] == "LocalBusiness")
    assert biz["image"] == "https://SITE_URL_PLACEHOLDER/icon-512.png"   # abs(LOGO_RASTER)


def test_person_is_labelled_planned_not_emitted(london):
    out = BX.schema_block(london, ROOT)
    assert "planned for this page (board schema plan), not yet emitted by the site build" in out


def test_prices_come_from_the_data_files(london):
    puppies = json.loads((ROOT / "data/puppies.json").read_text(encoding="utf-8"))
    avail = {p["name"]: p["price_gbp"] for p in puppies if p["status"] == "Available"}
    graph = BX.jsonld_graph(london, ROOT)
    for p in (n for n in graph if n["@type"] == "Product"):
        name = p["name"].split(" – ")[0]
        assert p["offers"]["price"] == avail[name]
        assert p["offers"]["priceCurrency"] == "GBP"


def test_no_aggregate_rating_and_no_review_markup_anywhere(london):
    text = json.dumps(BX.jsonld_graph(london, ROOT))
    assert "AggregateRating" not in text and "aggregateRating" not in text
    assert '"Review"' not in text and '"review"' not in text
    block = BX.schema_block(london, ROOT)
    assert "AggregateRating" not in block.split("```")[1]


def test_review_types_in_a_brief_are_refused_not_built():
    b = _mini(brief={"schema": {"types": ["LocalBusiness", "AggregateRating", "Review"]}})
    graph = BX.jsonld_graph(b, ROOT)
    assert "AggregateRating" not in json.dumps(graph) and '"Review"' not in json.dumps(graph)
    out = BX.schema_block(b, ROOT)
    assert "Rule 33" in out


def test_keys_without_data_are_omitted_as_the_build_omits_them(london):
    biz = next(n for n in BX.jsonld_graph(london, ROOT) if n["@type"] == "LocalBusiness")
    assert "telephone" not in biz and "geo" not in biz
    assert "streetAddress" not in biz["address"] and "postalCode" not in biz["address"]
    assert biz["url"].startswith("https://SITE_URL_PLACEHOLDER")
    out = BX.schema_block(london, ROOT)
    tail = out.split("```")[-1]
    assert "omitted: telephone (PHONE_PLACEHOLDER until project 6), " \
           "streetAddress/postalCode (Known Issue 16)" in tail


def test_faq_rows_not_yet_in_data_print_not_fetched(london):
    faq = next(n for n in BX.jsonld_graph(london, ROOT) if n["@type"] == "FAQPage")
    assert faq["mainEntity"]
    for q in faq["mainEntity"]:
        assert q["name"] and not q["name"].startswith("london-")     # the question, not the id
        a = q["acceptedAnswer"]["text"]
        assert a.startswith("NOT FETCHED") or "{" not in a


def test_an_faq_row_in_data_is_read_and_its_tokens_filled():
    b = _mini(sections=[{"id": "f", "n": 1, "heading": "FAQ", "shape": "faq",
                         "tree": [{"level": 3, "heading": "deposit", "intent": "", "children": []}],
                         "links": {"internal": [], "external": []}}])
    faq = next(n for n in BX.jsonld_graph(b, ROOT) if n["@type"] == "FAQPage")
    settings = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
    a = faq["mainEntity"][0]["acceptedAnswer"]["text"]
    assert f"£{settings['deposit_gbp']}" in a and "{" not in a


def test_breadcrumb_follows_the_route(london):
    bc = next(n for n in BX.jsonld_graph(london, ROOT) if n["@type"] == "BreadcrumbList")
    items = bc["itemListElement"]
    assert [i["name"] for i in items] == ["Home", "UK Locations", "London"]
    assert items[-1]["item"] == "https://SITE_URL_PLACEHOLDER/uk-locations/blue-staffy-puppies-london/"


def test_schema_block_says_it_is_a_preview(london):
    out = BX.schema_block(london, ROOT)
    assert BX.SCHEMA_NOTE in out and "npm run check:schema" in out
    assert "```json" in out


# ── 8b: internal links ──────────────────────────────────────────────────────────────────
def test_links_out_are_the_records_internal_links(london):
    out = BX.links_out(london)
    n = sum(len(s["links"]["internal"]) for s in london["sections"])
    assert len(out) == n and n > 0
    assert all({"href", "anchor", "section"} <= set(r) for r in out)


def _page(tmp, route, body, chrome=""):
    p = tmp / route / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"<html><body><header>{chrome}</header><main>{body}</main></body></html>")


def test_links_in_reads_main_with_a_parser(tmp_path):
    target = "uk-locations/x"
    _page(tmp_path, "a", '<p><a href="/uk-locations/x/">Puppies in <b>X</b></a></p>')
    _page(tmp_path, "b", "<p><a class='k' href='https://SITE_URL_PLACEHOLDER/uk-locations/x/#faq'>x faq</a></p>")
    _page(tmp_path, "c", "<p>nothing</p>", chrome='<a href="/uk-locations/x/">X</a>')
    _page(tmp_path, "d", '<a href="/uk-locations/x"><img src="/i.webp" alt="A puppy in X"></a>')
    _page(tmp_path, "e", '<a aria-label="X" href="/uk-locations/x/"> </a>')
    _page(tmp_path, "uk-locations/x", '<a href="/uk-locations/x/">self</a>')
    _page(tmp_path, "kit-preview/y", '<a href="/uk-locations/x/">specimen</a>')
    rows, chrome = BX.links_in(target, tmp_path)
    assert sorted((r["source"], r["anchor"]) for r in rows) == [
        ("/a/", "Puppies in X"), ("/b/", "x faq"), ("/d/", "[image: A puppy in X]"),
        ("/e/", "[aria-label: X]")]
    assert chrome == 1


def test_relative_hrefs_resolve_against_the_source_page(tmp_path):
    _page(tmp_path, "uk-locations/a", '<a href="../x/">sibling</a><a href="x/">wrong</a>')
    _page(tmp_path, "uk-locations", '<a href="x/">from the hub</a>')
    rows, _ = BX.links_in("uk-locations/x", tmp_path)
    assert sorted((r["source"], r["anchor"]) for r in rows) == [
        ("/uk-locations/", "from the hub"), ("/uk-locations/a/", "sibling")]


def test_another_domain_with_the_same_path_is_not_counted(tmp_path):
    _page(tmp_path, "a", '<a href="https://example.com/uk-locations/x/">elsewhere</a>'
                         '<a href="//example.com/uk-locations/x/">proto</a>'
                         '<a href="mailto:x@y.z">mail</a>')
    _page(tmp_path, "b", '<a href="https://SITE_URL_PLACEHOLDER/uk-locations/x/">ours</a>')
    rows, _ = BX.links_in("uk-locations/x", tmp_path)
    assert [(r["source"], r["anchor"]) for r in rows] == [("/b/", "ours")]


def test_index_html_is_the_directory_route(tmp_path):
    _page(tmp_path, "a", '<a href="/uk-locations/x/index.html">full path</a>')
    rows, _ = BX.links_in("uk-locations/x", tmp_path)
    assert [(r["source"], r["anchor"]) for r in rows] == [("/a/", "full path")]
    assert BX.norm_route("index.html", "/uk-locations/x/") == "/uk-locations/x/"


def test_links_block_says_not_fetched_without_dist(london, tmp_path):
    out = BX.links_block(london, ROOT, dist=tmp_path / "missing")
    assert "NOT FETCHED — dist/ not built (npm run build)" in out


def test_links_block_flags_orphan_risk_under_three(london, tmp_path):
    _page(tmp_path, "a", '<a href="/uk-locations/blue-staffy-puppies-london/">London</a>')
    out = BX.links_block(london, ROOT, dist=tmp_path)
    assert "orphan risk" in out.lower()
    for i in range(3):
        _page(tmp_path, f"p{i}", '<a href="/uk-locations/blue-staffy-puppies-london/">London</a>')
    assert "orphan risk" not in BX.links_block(london, ROOT, dist=tmp_path).lower()


# ── 8c: page weight ─────────────────────────────────────────────────────────────────────
def test_weight_rows_read_real_bytes_and_the_760_sibling(london):
    rows = BX.weight_rows(london, ROOT)
    hero = next(r for r in rows if r["slot"] == "london-hero")
    f = ROOT / "public/images/maggie-blue-staffy-dam-with-pups.webp"
    s = ROOT / "public/images/maggie-blue-staffy-dam-with-pups-760.webp"
    assert hero["bytes"] == f.stat().st_size
    assert hero["sib_bytes"] == s.stat().st_size


def test_unbaked_infographics_say_so(london):
    """An infographic slot with no file says it is not baked, never a size.
    London's six infographics were baked and published (2026-10-03), so the unbaked case is
    now built from a copy of its board with every infographic file removed, and the real
    board is held to the opposite: each baked infographic reports its file's real bytes."""
    import copy
    rows = BX.weight_rows(london, ROOT)
    ig = [r for r in rows if r["kind"] == "infographic"]
    assert ig and all(r["bytes"] == (ROOT / "public" / r["file"].lstrip("/")).stat().st_size
                      and r["note"] != BX.NOT_BAKED for r in ig)
    unbaked = copy.deepcopy(london)
    for _sec, _node, img in BX.IC.iter_slots(unbaked):
        if img.get("kind") == "infographic":
            img.pop("file", None)
    unbaked["assets"] = [a for a in unbaked.get("assets", []) if a.get("kind") != "infographic"]
    rows = BX.weight_rows(unbaked, ROOT)
    ig = [r for r in rows if r["kind"] == "infographic"]
    assert ig and all(r["bytes"] is None and r["note"] == BX.NOT_BAKED for r in ig)
    out = BX.weight_block(unbaked, ROOT)
    assert "not baked — size after STOP 4" in out


def test_weight_block_names_the_lcp_candidate_and_a_page_total(london):
    out = BX.weight_block(london, ROOT)
    assert "LCP candidate" in out and "maggie-blue-staffy-dam-with-pups.webp" in out
    assert "Page total" in out


def test_budget_is_cited_from_the_repo_or_none_is_claimed():
    import bake_images
    src = BX.budget_source(ROOT)
    assert src["max_kb"] == bake_images.MAX_KB
    assert src["per_image_bytes"] == bake_images.MAX_KB * 1024
    for cite in src["cites"]:
        path, line = cite["path"], cite["line"]
        text = (ROOT / path).read_text(encoding="utf-8").splitlines()[line - 1]
        assert cite["needle"] in text
    assert src["page_budget_bytes"] is None          # the repo states no page-weight number
    assert src["lcp_budget_ms"] is None              # nor an LCP time
