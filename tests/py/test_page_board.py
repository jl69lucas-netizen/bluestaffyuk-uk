"""The Page Board library's tests, ported from CAG's tests/test_page_board.py (183 tests).

Forty-one tests were dropped rather than re-based, because their subject was CAG's own
data or a module this port leaves behind. Each group, and why:

  * the four `..._real_ledger_...` tests, `test_ledger_file_validates_and_knows_pages_a_and_b`
    and `test_ledger_facts_are_present_and_asserted` — they assert against CAG's twelve-page
    component ledger and its ontology. BSUK's ledger is empty until project 3.
  * `test_gate_against_the_real_dist_whitelists_faq_but_flags_current_pricing`,
    `test_near_me_retrofit_board_renders_candidates_and_passes_the_gate`,
    `test_board_html_shows_standard_sections_with_their_default_and_no_radio` and
    `test_gate_links_external_missing_warns_at_build_and_fails_at_release_on_the_hub` —
    they load a real CAG board record out of CAG's 104-page dist/. Task 5 writes the first
    BSUK board; these come back with real records to assert against.
  * the whole canvas group (`test_canvas_*`, `test_board_maps_a_thumb_*`,
    `test_board_keys_a_thumb_*`, the canvas index/manifest tests, the refresh-badge test and
    `test_kit_strip_takes_the_desktop_thumb_...`) — `board_canvas.py` and `board_thumbs.mjs`
    are not ported (spec §2). `file_token`/`unfile_token` moved into pageboard.py and are
    still covered by `test_file_token_round_trips_through_unfile_token`.
  * the nine `test_perf_*` tests and their helpers — `perf_audit.py` arrives in Task 8, and
    its records do not exist until a page is measured. Re-add them there.
  * the three `seed_ontology` tests (re-seed, catalog floor, carried decision) —
    `seed_ontology.py` is not in the port manifest.
  * `test_ontology_file_validates_and_has_the_blocked_family` and
    `test_every_asserted_source_resolves_to_a_real_heading_or_data_key` — they assert CAG's
    ontology contents. Replaced below with the BSUK equivalents.

Two tests were re-based rather than dropped where the plan's text said "drop": the head-term
tests now read `PB.HEAD_TERMS` instead of spelling a head term out (dup_content_audit.py is
re-based in its own task), and `test_validate_ledger_rejects_the_unnamed_refresh_placeholder`
builds a synthetic ledger instead of mutating the repo's empty one.
"""
import json, pathlib, sys
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pageboard as PB


from build_page_board import esc as BPB_esc      # the one None-safe escaper

FIXTURE_LIBRARY = ROOT / "tests" / "py" / "fixtures" / "external-link-library.md"


@pytest.fixture(autouse=True)
def _fixture_link_library(monkeypatch):
    """Every board fixture in this module is validated against a FIXTURE link library.

    `validate_board()` refuses an external href that `docs/reference/external-link-library.md`
    does not record. Pointing the unit tests at the real document would either couple them to
    a content file that changes whenever a page cites something new, or push fixture URLs like
    `https://example.com/foo_bar` into it. A test that needs an UNKNOWN url repoints the path
    itself; this only sets the default."""
    monkeypatch.setattr(PB, "EXTERNAL_LIBRARY", FIXTURE_LIBRARY)


MIN_BOARD = {
    "meta": {"slug": "x", "page_type": "hub", "status": "draft", "research_as_of": "2026-09-12", "sources": []},
    "brief": {"goal": "g", "scope": "s", "gates": ["hardening"], "done": "d", "out_of_scope": [],
              "primary_keyword": "blue staffy puppies for sale uk",
              "angles": [{"name": "n", "hook": "the puppies first, the pitch second", "why_not": ""},
                         {"name": "price-led", "hook": "open on the £1,500 floor",
                          "why_not": "the price bucket is the adoption-cost page's, and it outranks us on it"}],
              "strategy": {"name": "n", "why": "w", "trade_off": "t"},
              "cta": {"cadence": {"min": 500, "max": 700}, "destination": "#reserve",
                      "anchors": ["Reserve This Puppy"], "global_cta": "hidden"},
              "tool": {"pick": "none",
                       "evidence": "No top-10 result for the head term ships a calculator or quiz, and the fan-out has no 'calculate' query.",
                       "trade_off": ""},
              "schema": {"types": ["AggregateOffer", "FAQPage"], "offer_model": "aggregate-offer"},
              },
    "h1": {"variants": ["a", "b", "c", "d", "e"], "recommended": 0, "pick": None},
    "meta_set": {
        "titles": ["Blue Staffy Puppies for Sale UK | Glasgow Breeder | BlueStaffyUK",
                   "Blue Staffy Puppies for Sale — Named and Priced | BlueStaffyUK",
                   "Buy a Blue Staffy Puppy From the Kennel That Raised It"],
        "descriptions": ["d" * 150, "e" * 140, "f" * 160],
        "recommended": {"title": 0, "description": 0},
        "pick": {"title": None, "description": None},
    },
    "sections": [{
        "id": "puppies", "n": 1, "heading": "Our Blue Staffy Puppies", "intent": "inventory first",
        "category": "A", "framework": "EEBP",
        "group": "MANDATORY",
        "why": "A for-sale hub that shows no puppies above the fold reads as a directory, not a breeder.",
        "why_source": "docs/research/for-sale-keywords-2026-07.md",
        "words": {"min": 400, "max": 600}, "shape": "inventory",
        "cta": 1,
        "keywords": {"primary": ["blue staffy puppies for sale uk"], "lsi": [], "longtail": [], "brand": [], "geo": [],
                     "conversational": [], "comparison": [], "solution": [], "transactional": []},
        "entities": ["ont:staffordshire-bull-terrier"],
        "tree": [{"level": 3, "heading": "Our Kennel Today", "intent": "", "children": [
                 {"level": 4, "heading": "What Does Each Cost?", "intent": "", "children": [
                 {"level": 5, "heading": "Every Price Includes the Folder", "intent": "", "children": [
                 {"level": 6, "heading": "Kennel Note: Read the Card", "intent": "", "children": []}]}]}]}],
        "images": [{"slot": "puppies-opener", "kind": "infographic", "required": False, "prompt": "six puppy cards"}],
        "links": {"internal": [{"href": "/uk-locations/staffy-puppies-for-sale-glasgow/", "anchor": "Our Glasgow listings",
                                "sentence_start": True}],
                  "external": [{"href": "https://www.gov.uk/guidance/dog-breeding-licence-england",
                                "anchor": "GOV.UK dog breeding licence guidance",
                                "library_row": "Authority — Government / Legal"}]},
        "options": {"candidates": ["avail-b"], "excluded": [], "pick": None, "note": ""}}],
    "tuple": {"hero": "hero-a", "dial": "dial-1", "rail": "rail-a", "toc": "t1", "takeaway": ["k1"],
              "table": "table-a", "faq": "faq-a", "stepper": "", "newsletter": {"after": "", "variant": ""},
              "h6_prefixes": ["Kennel Note:", "From the Book:", "Ask Us:"]},
    "assets": [{"slot": "hero", "kind": "photo", "w": 1280, "h": 960, "required": True, "status": "missing", "file": None, "alt": ""}],
    "approval": None,
}


@pytest.fixture(scope="session")
def live_dist():
    """Reading dist/ once per session rather than once per test is the difference between
    a gate you run and one you skip."""
    if not PB.DIST.exists():
        pytest.skip("dist/ is not built — run npm run build")
    return PB.live_headings()

def test_minimal_board_validates():
    PB.validate_board(MIN_BOARD)          # raises on failure


def test_board_missing_sections_fails():
    bad = json.loads(json.dumps(MIN_BOARD)); del bad["sections"]
    with pytest.raises(PB.BoardError):
        PB.validate_board(bad)


def test_unknown_shape_fails():
    bad = json.loads(json.dumps(MIN_BOARD)); bad["sections"][0]["shape"] = "banner"
    with pytest.raises(PB.BoardError):
        PB.validate_board(bad)


def test_ontology_and_ledger_schemas_accept_minimal_docs():
    PB.validate_ontology({"entities": [{"id": "ont:x", "name": "X", "aliases": [], "class": "Health",
                                        "authorization": "PROPOSED", "source": None, "owner_page": None}]})
    PB.validate_ledger({"pools": {"inventory": ["avail-a", "avail-b"]}, "pages": {}})


def test_extra_key_inside_words_fails():
    bad = json.loads(json.dumps(MIN_BOARD)); bad["sections"][0]["words"]["target"] = 500
    with pytest.raises(PB.BoardError):
        PB.validate_board(bad)


def test_bad_approval_pick_key_fails():
    bad = json.loads(json.dumps(MIN_BOARD))
    bad["approval"] = {"approved_at": "2026-09-12T00:00:00Z", "h1": 0, "picks": {"Bad Id!": "avail-b"},
                       "notes": {}, "canvas_version": None, "record_hash": "0" * 64}
    with pytest.raises(PB.BoardError):
        PB.validate_board(bad)


def test_save_board_rejects_slug_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    board = json.loads(json.dumps(MIN_BOARD))          # meta.slug is "x"
    with pytest.raises(PB.BoardError):
        PB.save_board("y", board)
    assert not PB.board_path("y").exists()
    PB.save_board("x", board)                          # the matching slug still writes
    assert PB.board_path("x").exists()


def test_record_hash_ignores_approval_and_is_stable():
    a = json.loads(json.dumps(MIN_BOARD))
    b = json.loads(json.dumps(MIN_BOARD))
    b["approval"] = {"approved_at": "2026-09-12T10:00:00Z", "h1": 0, "picks": {}, "notes": {},
                     "canvas_version": None, "record_hash": "0" * 64}
    assert PB.record_hash(a) == PB.record_hash(b)
    assert len(PB.record_hash(a)) == 64


def test_record_hash_changes_when_a_heading_changes():
    a = json.loads(json.dumps(MIN_BOARD))
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["heading"] = "Something Else"
    assert PB.record_hash(a) != PB.record_hash(b)


def test_approval_matches_only_when_hash_matches():
    a = json.loads(json.dumps(MIN_BOARD))
    a["approval"] = {"approved_at": "2026-09-12T10:00:00Z", "h1": 0, "picks": {"puppies": "avail-b"}, "notes": {},
                     "canvas_version": None, "record_hash": PB.record_hash(a)}
    assert PB.approval_matches(a) is True
    a["sections"][0]["intent"] = "edited after approval"
    assert PB.approval_matches(a) is False
    a["approval"] = None
    assert PB.approval_matches(a) is False


def test_record_hash_ignores_lifecycle_fields():
    a = json.loads(json.dumps(MIN_BOARD))
    b = json.loads(json.dumps(MIN_BOARD))
    b["meta"]["status"] = "approved"                   # board_approve.py flips this when it stamps
    b["assets"][0]["status"] = "baked"                 # and baking a photo fills these in
    b["assets"][0]["file"] = "/img/hero.webp"
    assert PB.record_hash(a) == PB.record_hash(b)
    b["assets"][0]["alt"] = "a real alt line"          # alt IS content, so it must move the hash
    assert PB.record_hash(a) != PB.record_hash(b)


def test_approval_survives_the_approve_then_bake_lifecycle():
    board = json.loads(json.dumps(MIN_BOARD))
    board["approval"] = {"approved_at": "2026-09-12T10:00:00Z", "h1": 0, "picks": {}, "notes": {},
                         "canvas_version": None, "record_hash": PB.record_hash(board)}
    board["meta"]["status"] = "approved"
    assert PB.approval_matches(board) is True
    board["assets"][0]["status"] = "baked"
    board["assets"][0]["file"] = "/img/hero.webp"
    assert PB.approval_matches(board) is True


def test_record_hash_survives_a_json_round_trip():
    a = json.loads(json.dumps(MIN_BOARD))
    b = json.loads(json.dumps(a, indent=2, ensure_ascii=False))
    assert PB.record_hash(a) == PB.record_hash(b)


def test_approval_matches_false_when_only_the_stored_hash_is_tampered_with():
    a = json.loads(json.dumps(MIN_BOARD))
    a["approval"] = {"approved_at": "2026-09-12T10:00:00Z", "h1": 0, "picks": {}, "notes": {},
                     "canvas_version": None, "record_hash": PB.record_hash(a)}
    assert PB.approval_matches(a) is True
    a["approval"]["record_hash"] = "0" * 64
    assert PB.approval_matches(a) is False


def test_approval_matches_returns_false_for_a_non_dict_approval():
    for junk in ("approved", ["approved"], 1, True):
        a = json.loads(json.dumps(MIN_BOARD))
        a["approval"] = junk
        assert PB.approval_matches(a) is False


def test_every_asserted_entity_has_a_source():
    ont = PB.load_ontology()
    for e in ont["entities"]:
        if e["authorization"] == "ASSERTED":
            assert e["source"], f"{e['id']} is ASSERTED with no source"


def test_the_ontology_carries_no_page_type_or_price_range_rows():
    ids = {e["id"] for e in PB.load_ontology()["entities"]}
    assert ids.isdisjoint({"ont:page-type", "ont:homepage", "ont:comparison-page", "ont:location-page",
                           "ont:price-page", "ont:variant-guide", "ont:1-500-3-500"})


def test_load_ledger_raises_board_error_when_the_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(PB, "LEDGER", tmp_path / "component-ledger.json")
    with pytest.raises(PB.BoardError) as e:
        PB.load_ledger()
    assert "does not exist" in str(e.value) and "component-ledger.json" in str(e.value)


def test_ledger_twins_are_not_duplicated_as_proposed_catalog_rows():
    ids = {e["id"] for e in PB.load_ontology()["entities"]}
    assert ids.isdisjoint({"ont:kc-registration", "ont:breeding-licence", "ont:microchipping",
                           "ont:defra-transport", "ont:lifetime-advisory"})


def test_candidates_of_a_shared_pool_are_all_free():
    """`inventory` is not a refresh pool: a sibling using avail-b costs nobody anything,
    because the ledger's discipline is that the combo differs, not the component."""
    ledger = {"pools": {"inventory": ["avail-a", "avail-b", "puppy-cards"]},
              "pages": {"kc-registered-blue-staffy-for-sale": {"hero": "hero-c", "dial": "dial-1", "rail": "rail-a", "toc": "avail-b",
                        "takeaway": [], "table": "", "faq": "", "h6_prefixes": []}}}
    cands, excluded = PB.candidates_for("inventory", ledger, slug="blue-staffy-puppies-for-sale")
    assert cands == ["avail-a", "avail-b", "puppy-cards"] and excluded == []


def test_a_nav_shaped_section_draws_from_the_toc_pool():
    ledger = {"pools": {"nav": ["dial-1", "rail-a"], "toc": ["toc-t1", "toc-t2"]}, "pages": {}}
    cands, excluded = PB.candidates_for("nav", ledger, slug="x")
    assert cands == ["toc-t1", "toc-t2"] and excluded == []


def test_candidates_never_exclude_the_page_itself():
    ledger = {"refresh_pools": ["hero"], "pools": {"hero": ["hero-a", "hero-c"]},
              "pages": {"x": {"hero": "hero-a", "dial": "", "rail": "", "toc": "", "takeaway": [], "table": "", "faq": "", "h6_prefixes": []}}}
    cands, excluded = PB.candidates_for("hero", ledger, slug="x")
    assert cands == ["hero-a", "hero-c"] and excluded == []


def test_standard_shape_has_no_options():
    cands, excluded = PB.candidates_for("standard", {"pools": {}, "pages": {}}, slug="x")
    assert cands == [] and excluded == []


def test_exhausted_pool_yields_refresh_candidates():
    ledger = {"refresh_pools": ["hero"], "pools": {"hero": ["hero-a", "hero-c"]},
              "pages": {"p1": {"hero": "hero-a", "dial": "", "rail": "", "toc": "", "takeaway": [], "table": "", "faq": "", "h6_prefixes": []},
                        "p2": {"hero": "hero-c", "dial": "", "rail": "", "toc": "", "takeaway": [], "table": "", "faq": "", "h6_prefixes": []}}}
    cands, excluded = PB.candidates_for("hero", ledger, slug="new-page")
    assert cands == ["hero-a#refresh", "hero-c#refresh"]
    assert excluded == [{"component": "hero-a", "owner": "p1", "owners": ["p1"]},
                        {"component": "hero-c", "owner": "p2", "owners": ["p2"]}]


def test_refreshed_id_owns_its_base():
    ledger = {"refresh_pools": ["hero"], "pools": {"hero": ["hero-c"]},
              "pages": {"near-me": {"hero": "hero-c#geo-tile-field", "dial": "", "rail": "", "toc": "",
                                    "takeaway": [], "table": "", "faq": "", "h6_prefixes": []}}}
    owned = PB.owned_components(ledger)
    assert owned["hero-c"] == ["near-me"] and owned["hero-c#geo-tile-field"] == ["near-me"]
    cands, excluded = PB.candidates_for("hero", ledger, slug="other")
    assert cands == ["hero-c#refresh"]
    assert excluded == [{"component": "hero-c", "owner": "near-me", "owners": ["near-me"]}]


def test_base_of():
    assert PB.base_of("hero-c-mosaic-metrics") == "hero-c-mosaic-metrics"
    assert PB.base_of("hero-c-mosaic-metrics#geo-tile-field") == "hero-c-mosaic-metrics"
    assert PB.base_of("faq-b#map-pin") == "faq-b"


def test_every_tuple_component_appears_in_some_pool():
    """A tuple may draw from any pool — the litter page's TOC is the nav pool's dial-1-clay — but a
    component no pool carries can never be offered to a sibling page again."""
    ledger = PB.load_ledger()
    pooled = {PB.base_of(c) for pool in ledger["pools"].values() for c in pool}
    orphans = {PB.base_of(cid): slug for slug, t in ledger["pages"].items()
               for cid in PB.tuple_component_ids(t) if PB.base_of(cid) not in pooled}
    assert orphans == {}


def test_validate_ledger_rejects_the_unnamed_refresh_placeholder():
    # A synthetic ledger, not the repo's: BSUK's component ledger is empty until project 3
    # and the rule under test is the validator's, not any particular page's.
    ledger = {"refresh_pools": ["hero"], "pools": {"hero": ["hero-c"]},
              "pages": {"near-me": {"hero": "hero-c", "dial": "", "rail": "", "toc": "",
                                    "takeaway": [], "table": "", "faq": "", "h6_prefixes": []}}}
    ledger["pages"]["near-me"]["hero"] = "x#refresh"
    with pytest.raises(PB.BoardError) as e:
        PB.validate_ledger(ledger)
    assert "x#refresh" in str(e.value)


def test_ledger_tuple_slot_may_be_empty():
    """An empty scalar slot means "this page has no such component", not a bad id."""
    PB.validate_ledger({"pools": {"hero": ["hero-a"]},
                        "pages": {"p1": {"hero": "hero-a", "dial": "", "rail": "", "toc": "",
                                         "takeaway": [], "table": "", "faq": "", "h6_prefixes": []}}})


def test_all_headings_walks_the_tree_in_order():
    hs = PB.all_headings(MIN_BOARD)
    assert hs[0] == (1, "a")                      # h1.pick is None, so the recommendation
    assert hs[1] == (2, "Our Blue Staffy Puppies")
    assert hs[-1] == (6, "Kennel Note: Read the Card")
    assert [lvl for lvl, _ in hs] == [1, 2, 3, 4, 5, 6]


def test_all_headings_opens_on_the_breeder_pick_when_there_is_one():
    b = json.loads(json.dumps(MIN_BOARD)); b["h1"]["pick"] = 3
    assert PB.all_headings(b)[0] == (1, "d")


def test_header_precheck_finds_exact_and_shingle_matches():
    live = {"/blue-vs-brindle/": ["Blue or Brindle — Which Suits Your Household?", "What Every Puppy Card Tells You Before You Ask"]}
    hits = PB.header_precheck(["Blue or Brindle — Which Suits Your Household?",
                               "What Every Puppy Card Tells You Before You Buy",
                               "A Heading Nobody Has Used"], live)
    kinds = {h["heading"]: h["kind"] for h in hits}
    assert kinds["Blue or Brindle — Which Suits Your Household?"] == "exact"
    assert kinds["What Every Puppy Card Tells You Before You Buy"] == "shingle"
    assert "A Heading Nobody Has Used" not in kinds


def test_header_precheck_template_collision_across_species():
    live = {"/blue-vs-brindle/": ["Is a Blue Right for You?"]}
    hits = PB.header_precheck(["Is a Brindle Right for You?"], live)
    assert hits and hits[0]["kind"] == "template"


def test_authorization_check_reports_blocked_and_proposed():
    ont = {"entities": [
        {"id": "ont:ok", "name": "ok", "aliases": [], "class": "Health", "authorization": "ASSERTED", "source": "x", "owner_page": None},
        {"id": "ont:maybe", "name": "maybe", "aliases": [], "class": "Health", "authorization": "PROPOSED", "source": None, "owner_page": None},
        {"id": "ont:wild-caught", "name": "wild-caught", "aliases": [], "class": "Commerce", "authorization": "BLOCKED", "source": "rule 2", "owner_page": None}]}
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["entities"] = ["ont:ok", "ont:maybe", "ont:wild-caught", "ont:unknown"]
    r = PB.authorization_check(b, ont)
    assert r["blocked"] == ["ont:wild-caught"]
    assert r["proposed"] == ["ont:maybe"]
    assert r["unknown"] == ["ont:unknown"]


def test_distribution_sums_keywords_and_words():
    d = PB.distribution(MIN_BOARD)
    assert d["rows"][0]["section"] == "puppies" and d["rows"][0]["primary"] == 1
    assert d["totals"]["words_min"] == 400 and d["totals"]["words_max"] == 600
    assert d["h_counts"] == {"h1": 1, "h2": 1, "h3": 1, "h4": 1, "h5": 1, "h6": 1}


def test_distribution_totals_add_across_two_sections():
    b = json.loads(json.dumps(MIN_BOARD))
    second = json.loads(json.dumps(b["sections"][0]))
    second.update({"id": "shipping", "n": 2, "heading": "How Do We Ship?",
                   "words": {"min": 250, "max": 300}, "tree": []})
    second["keywords"] = {"primary": ["blue staffy delivery"], "lsi": ["defra"],
                          "longtail": [], "brand": ["bluestaffyuk"], "geo": ["glasgow", "scotland"],
                          "conversational": [], "comparison": [], "solution": [], "transactional": []}
    b["sections"].append(second)
    PB.validate_board(b)                                   # still a buildable record
    d = PB.distribution(b)
    assert [r["section"] for r in d["rows"]] == ["puppies", "shipping"]
    assert d["totals"] == {"primary": 2, "lsi": 1, "longtail": 0, "brand": 1, "geo": 2,
                           "conversational": 0, "comparison": 0, "solution": 0, "transactional": 0,
                           "words_min": 650, "words_max": 900}
    assert d["h_counts"] == {"h1": 1, "h2": 2, "h3": 1, "h4": 1, "h5": 1, "h6": 1}


def _tmp_dist(tmp_path):
    """A miniature dist/: the homepage, a one-level page, a two-level page."""
    pages = {
        "index.html": "<html><body><h1>Home</h1></body></html>",
        "foo/index.html": "<html><body><h2>Foo <em>Heading</em></h2></body></html>",
        "a/b/index.html": "<html><body><h3>Cards &amp; Folders</h3>\n"
                          "<h2 class='x'>Every Puppy Card\n  Tells You Something</h2></body></html>",
    }
    for rel, html in pages.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html, encoding="utf-8")
    return tmp_path


def test_live_headings_slugs_the_homepage_as_root(tmp_path):
    live = PB.live_headings(_tmp_dist(tmp_path))
    assert set(live) == {"/", "/foo/", "/a/b/"}
    assert live["/"] == ["Home"]
    assert live["/foo/"] == ["Foo Heading"]                      # nested tags stripped
    assert live["/a/b/"] == ["Cards & Folders", "Every Puppy Card Tells You Something"]


def test_header_precheck_shingle_needs_five_tokens_of_live_heading(tmp_path):
    live = PB.live_headings(_tmp_dist(tmp_path))
    # "Foo Heading" is two tokens long — it can never seed a 5-token shingle.
    assert PB.header_precheck(["Foo Heading With More Words Here"], live) == []
    hits = PB.header_precheck(["Every Puppy Card Tells You Today"], live)
    assert [(h["kind"], h["page"], h["with"]) for h in hits] == [
        ("shingle", "/a/b/", "Every Puppy Card Tells You Something")]


def test_live_headings_skips_site_chrome_like_the_dup_gate():
    """Only body headings enter the corpus. A nav link, a read-card title and a footer
    heading are chrome the dup gate already ignores, and counting them would make the
    pre-check collide every new page with the template every page shares."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        dist = pathlib.Path(d)
        (dist / "p").mkdir()
        (dist / "p" / "index.html").write_text(
            "<html><body>"
            "<nav><h2>By Location</h2></nav>"
            "<div class='read-cards'><h3>Blue vs Brindle</h3></div>"
            "<h2>What Does a Blue Staffy Cost?</h2>"
            "<footer><h2>Contact</h2></footer>"
            "</body></html>", encoding="utf-8")
        assert PB.live_headings(dist) == {"/p/": ["What Does a Blue Staffy Cost?"]}


def test_live_headings_skips_the_specimen_routes():
    """`/board-preview/<slug>/` and `/kit-preview/` render the SAME headings the board
    proposes, three styles over. Counting them collides every board with its own preview
    and reports a copied heading where there is one heading rendered three ways."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        dist = pathlib.Path(d)
        for rel in ("board-preview/privacy-policy-uk", "board-preview/a/b", "kit-preview", "real"):
            (dist / rel).mkdir(parents=True)
            (dist / rel / "index.html").write_text(
                "<html><body><h2>What information we collect</h2></body></html>", encoding="utf-8")
        assert PB.live_headings(dist) == {"/real/": ["What information we collect"]}


def test_header_precheck_excludes_the_page_being_rebuilt():
    live = {"/buy/": ["What Does a Blue Staffy Cost?"], "/other/": ["Where Do We Ship?"]}
    assert PB.header_precheck(["What Does a Blue Staffy Cost?"], live)[0]["kind"] == "exact"
    assert PB.header_precheck(["What Does a Blue Staffy Cost?"], live, exclude_page="/buy/") == []


def test_header_precheck_matches_curly_apostrophes_and_plural_species():
    live = {"/a/": ["What Do Blue Staffies Eat Each Day?"]}          # the coat colour token
    hits = PB.header_precheck(["What Do Brindle Staffies Eat Each Day?"], live)
    assert hits and hits[0]["kind"] == "template"
    assert PB.header_precheck(["A Staffy’s First Week Home"],
                              {"/b/": ["A Staffy's First Week Home"]})[0]["kind"] == "exact"


def _approved(board):
    b = json.loads(json.dumps(board))
    for s in b["sections"]:
        if s["shape"] != "standard":
            s["options"]["pick"] = s["options"]["pick"] or (
                s["options"]["candidates"][0] if s["options"]["candidates"] else "default")
    b["approval"] = {"approved_at": "2026-09-12T10:00:00Z", "h1": 0, "picks": {s["id"]: s["options"]["pick"] for s in b["sections"]},
                     "notes": {}, "canvas_version": None, "record_hash": PB.record_hash(b)}
    b["meta"]["status"] = "approved"
    return b


ONT_OK = {"entities": [{"id": "ont:staffordshire-bull-terrier", "name": "Staffordshire Bull Terrier", "aliases": [], "class": "Organism",
                        "authorization": "ASSERTED", "source": "x", "owner_page": None}]}
LEDGER_EMPTY = {"pools": {"inventory": ["avail-b"]}, "pages": {}}


def test_gate_passes_an_approved_minimal_board():
    b = _approved(MIN_BOARD)
    # A live corpus of one unrelated sibling: live={} is itself a FAIL (a gate that
    # examined nothing is not a pass), which is asserted in its own test below.
    # The corpus carries the one page MIN_BOARD's links plan points at, so links-internal-dead
    # has something to examine: a live map missing it would report a dead link that is only
    # a short fixture.
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY,
                         live={"/other/": ["Where Do We Deliver Each Week?"],
                               "/uk-locations/staffy-puppies-for-sale-glasgow/": []},
                         stage="build")
    # MIN_BOARD carries exactly one H5 and one H6 by design (test_distribution_counts_headings),
    # so the volume floor is the one FAIL a minimal board is meant to raise. Its severity is
    # asserted on its own in test_gate_h5_h6_minimums_are_warn_on_home_and_location.
    assert [x for x in f if x["sev"] == "FAIL" and x["check"] != "min-h5-h6"] == [], f


def test_gate_fails_without_matching_approval():
    b = _approved(MIN_BOARD)
    b["sections"][0]["intent"] = "edited after approval"
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
    assert any(x["check"] == "approval-hash" and x["sev"] == "FAIL" for x in f)


def test_gate_fails_on_blocked_entity_and_owned_shell_and_spent_prefix():
    b = _approved(MIN_BOARD)
    b["sections"][0]["entities"].append("ont:wild-caught")
    ont = {"entities": ONT_OK["entities"] + [{"id": "ont:wild-caught", "name": "w", "aliases": [], "class": "Commerce",
                                              "authorization": "BLOCKED", "source": "r2", "owner_page": None}]}
    ledger = {"refresh_pools": ["hero", "toc", "faq"], "pools": {"inventory": ["avail-b"]},
              "pages": {"sibling": {"hero": "hero-a", "dial": "", "rail": "", "toc": "", "takeaway": [], "table": "", "faq": "",
                                    "h6_prefixes": ["Kennel Note:"]}}}
    b["approval"]["record_hash"] = PB.record_hash(b)
    f = {x["check"] for x in PB.gate_findings(b, ont, ledger, live={}, stage="build") if x["sev"] == "FAIL"}
    assert {"entity-blocked", "ledger-shell-owned", "ledger-spent-prefix"} <= f


def _ledger_with(**tuple_fields):
    t = {"hero": "", "dial": "", "rail": "", "toc": "", "takeaway": [], "table": "", "faq": "", "h6_prefixes": []}
    t.update(tuple_fields)
    return {"refresh_pools": ["hero", "toc", "faq"], "pools": {"inventory": ["avail-b"]}, "pages": {"sibling": t}}


def _checks(board, ledger):
    return {x["check"] for x in PB.gate_findings(board, ONT_OK, ledger, live={}, stage="build") if x["sev"] == "FAIL"}


def _h_page(dist, slug, h5, h6):
    p = dist / slug / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("<html><body><h1>T</h1><h2>S</h2>"
                 + "".join(f"<h5>Point {i}</h5>" for i in range(h5))
                 + "".join(f"<h6>Privacy Note: {i}</h6>" for i in range(h6))
                 + "</body></html>", encoding="utf-8")


def test_min_h5_h6_reads_the_record_tree_for_a_record_not_yet_rebuilt(tmp_path, monkeypatch):
    """The floor stays a planning constraint while the page is still an outline."""
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(PB, "REBUILT", tmp_path / "rebuilt.json")      # absent → no slug rebuilt
    b = _approved(MIN_BOARD)
    hit = [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
           if x["check"] == "min-h5-h6"]
    assert hit and "record tree" in hit[0]["msg"], hit


def test_min_h5_h6_reads_the_built_page_for_a_rebuilt_slug(tmp_path, monkeypatch):
    """A rebuilt page earns the floor the way the migrated pages did: H5 sub-points and
    "<prefix>:" H6 lines written INSIDE the sections at build time. The approved outline
    stops at the H3 the breeder saw, and must not be padded to satisfy arithmetic."""
    dist, rebuilt = tmp_path / "dist", tmp_path / "rebuilt.json"
    monkeypatch.setattr(PB, "DIST", dist)
    monkeypatch.setattr(PB, "REBUILT", rebuilt)
    rebuilt.write_text(json.dumps([MIN_BOARD["meta"]["slug"]]), encoding="utf-8")
    b = _approved(MIN_BOARD)

    _h_page(dist, MIN_BOARD["meta"]["slug"], h5=5, h6=5)
    assert not [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
                if x["check"] == "min-h5-h6"]

    _h_page(dist, MIN_BOARD["meta"]["slug"], h5=5, h6=4)               # one H6 short
    hit = [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
           if x["check"] == "min-h5-h6"]
    assert hit and "built page" in hit[0]["msg"] and "H6 4" in hit[0]["msg"], hit


def test_min_h5_h6_falls_back_to_the_tree_when_a_rebuilt_slug_has_no_built_page(tmp_path, monkeypatch):
    """A missing build is not a pass. `dist/` is absent before the first `npm run build`,
    and reading zero headings out of nothing would clear the floor for free."""
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(PB, "REBUILT", tmp_path / "rebuilt.json")
    (tmp_path / "rebuilt.json").write_text(json.dumps([MIN_BOARD["meta"]["slug"]]), encoding="utf-8")
    hit = [x for x in PB.gate_findings(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, stage="build")
           if x["check"] == "min-h5-h6"]
    assert hit and "record tree" in hit[0]["msg"], hit


def test_page_h_counts_ignores_site_chrome():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "index.html"
        p.write_text("<html><body><nav><h5>Jump</h5></nav><h5>Real</h5>"
                     "<footer><h6>Chrome</h6></footer><h6>Privacy Note: x</h6></body></html>",
                     encoding="utf-8")
        assert PB.page_h_counts(p)["h5"] == 1 and PB.page_h_counts(p)["h6"] == 1


# ---------------------------------------------------------------- words-out-of-band
# Spec §9 amendment 4a: a band counts the section's OWN prose. The H4-H6 ladder the page
# writes to meet `min-h5-h6` and the FAQ accordion's answers are outside it, and so is
# every heading — a band pays for body copy, not for the outline the breeder approved.

_PROSE_PAGE = (
    "<html><body>"
    "<nav><p>one two three four five</p></nav>"          # chrome: never a section's prose
    "<main>"
    "<section id='puppies'>"
    "<h2>Six Word Heading Right Here Now</h2>"           # headings do not count
    "<p>one two three four five six seven eight nine ten</p>"
    "<h3>Another Heading That Is Not Prose</h3>"
    "<p>eleven twelve</p>"
    "<h4>The Ladder Starts Here</h4>"
    "<p>ladder words that must not count at all</p>"
    "<h5>Still The Ladder</h5><p>more ladder words</p>"
    "<details><summary><h3>A Question</h3></summary><p>an answer from data faq json</p></details>"
    "</section>"
    "<section id='afterwards'><p>alpha beta gamma</p></section>"
    "</main></body></html>"
)


def _prose_page(dist, slug, html=_PROSE_PAGE, monkeypatch=None):
    """The built page for `slug`, and — when a monkeypatch is given — the rebuilt list that
    says this page IS the record's page. Before P5 the built page is still the migrated body,
    and `word_band_findings` measures nothing there on purpose."""
    p = pathlib.Path(dist) / slug / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    if monkeypatch is not None:
        rebuilt = pathlib.Path(dist) / "rebuilt.json"
        rebuilt.write_text(json.dumps([slug]), encoding="utf-8")
        monkeypatch.setattr(PB, "REBUILT", rebuilt)
    return p


def test_word_band_findings_measures_nothing_until_the_page_is_rebuilt(tmp_path, monkeypatch):
    """Before P5 the built page is the MIGRATED body: none of the record's section ids, none
    of its prose. Reporting every band as "not on the built page" would say only that the page
    has not been written yet, ten times, on the board the author is still drafting."""
    _prose_page(tmp_path, "x")
    monkeypatch.setattr(PB, "REBUILT", tmp_path / "absent.json")
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["id"] = "puppies"
    b["sections"][0]["words"] = {"min": 400, "max": 600}
    assert PB.word_band_findings(b, dist=tmp_path) == []


def test_page_section_words_counts_prose_and_skips_headings_ladder_details_and_chrome(tmp_path):
    got = PB.page_section_words(_prose_page(tmp_path, "x"))
    assert got == {"puppies": 12, "afterwards": 3}, got


def test_word_band_findings_is_silent_when_every_section_is_in_band(tmp_path, monkeypatch):
    _prose_page(tmp_path, "x", monkeypatch=monkeypatch)
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["id"] = "puppies"
    b["sections"][0]["words"] = {"min": 10, "max": 15}
    assert PB.word_band_findings(b, dist=tmp_path) == []


def test_word_band_findings_warns_per_section_and_never_fails(tmp_path, monkeypatch):
    """WARN, never FAIL: a section twenty words short is not a page that may not ship."""
    _prose_page(tmp_path, "x", monkeypatch=monkeypatch)
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["id"] = "puppies"
    b["sections"][0]["words"] = {"min": 400, "max": 600}
    f = PB.word_band_findings(b, dist=tmp_path)
    assert {x[1] for x in f} == {"WARN"}, f
    assert any("section puppies: 12 prose words against the record's 400-600" in x[2] for x in f), f
    assert any(x[2].startswith("page: 12 prose words against 400-600") for x in f), f


def test_word_band_findings_reports_a_section_the_built_page_does_not_carry(tmp_path, monkeypatch):
    """A band measured against nothing is not a band that passed."""
    _prose_page(tmp_path, "x", monkeypatch=monkeypatch)
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["id"] = "not-on-the-page"
    f = PB.word_band_findings(b, dist=tmp_path)
    assert any("not on the built page" in x[2] and x[1] == "WARN" for x in f), f


def test_word_band_findings_says_nothing_when_the_page_is_not_built(tmp_path, monkeypatch):
    """`min-h5-h6` already fails a rebuilt slug with no build; this one stays quiet rather
    than reporting every section of every unbuilt record as short."""
    (tmp_path / "rebuilt.json").write_text(json.dumps([MIN_BOARD["meta"]["slug"]]), encoding="utf-8")
    monkeypatch.setattr(PB, "REBUILT", tmp_path / "rebuilt.json")
    assert PB.word_band_findings(MIN_BOARD, dist=tmp_path) == []


def test_gate_reports_words_out_of_band_as_a_warning(tmp_path, monkeypatch):
    monkeypatch.setattr(PB, "DIST", tmp_path)
    _prose_page(tmp_path, MIN_BOARD["meta"]["slug"], monkeypatch=monkeypatch)
    b = _approved(MIN_BOARD)
    b["sections"][0]["id"] = "puppies"
    hit = [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
           if x["check"] == "words-out-of-band"]
    assert hit and {x["sev"] for x in hit} == {"WARN"}, hit


def _sig_ledger(**over):
    """A sibling matching MIN_BOARD's hero+faq+takeaway signature, every other axis
    different so `ledger-tuple-identical` does not fire first and swallow the finding."""
    t = {"hero": "hero-a", "faq": "faq-a", "takeaway": ["k1"],
         "dial": "dial-9", "rail": "rail-9", "toc": "t9", "table": "table-z"}
    t.update(over)
    return _ledger_with(**t)


def test_gate_flags_a_copied_hero_faq_takeaway_signature():
    """Components are shared by design; the signature the reader sees first is not.

    The signature is the tuple MINUS `dial` and `rail`. Those two stopped telling pages
    apart in project 4: the breeder picked one dial style and one sheet style for the whole
    site on the contact board and both are baked into the kit, so including them reduced
    the rule to "no two pages may share a hero style"."""
    b = _approved(MIN_BOARD)
    assert "ledger-tuple-owned" in _checks(b, _sig_ledger())
    # A different dial and rail buy a page nothing: they are not the breeder's to vary.
    assert "ledger-tuple-owned" in _checks(b, _sig_ledger(dial="dial-4", rail="rail-4"))
    # A different FAQ shell does separate two pages — which is what separates
    # privacy-policy-uk (faq-s1) from thank-you-…-journey (faq-s3) on a shared hero S3.
    assert "ledger-tuple-owned" not in _checks(b, _sig_ledger(faq="faq-z"))
    # ...and so does a different takeaway set.
    assert "ledger-tuple-owned" not in _checks(b, _sig_ledger(takeaway=["k9"]))


def test_gate_does_not_name_the_hero_twice_when_the_signature_is_owned():
    """The signature finding names the hero already, so the shell rule stays quiet about
    it — the shared FAQ shell is still reported in its own right."""
    found = PB.gate_findings(_approved(MIN_BOARD), ONT_OK, _sig_ledger(), live={}, stage="build")
    shells = [x["msg"] for x in found if x["check"] == "ledger-shell-owned"]
    assert any("faq" in m for m in shells), shells
    assert not any("hero" in m for m in shells), shells


def test_gate_flags_a_takeaway_set_a_sibling_already_uses():
    b = _approved(MIN_BOARD)
    b["tuple"]["takeaway"] = ["k1", "k2"]
    b["approval"]["record_hash"] = PB.record_hash(b)
    same = _checks(b, _ledger_with(takeaway=["k2", "k1"]))          # a set, so order cannot dodge it
    assert "ledger-takeaway-set-owned" in same
    assert "ledger-takeaway-set-owned" not in _checks(b, _ledger_with(takeaway=["k1", "k3"]))
    assert "ledger-takeaway-set-owned" not in _checks(b, _ledger_with(takeaway=["k1"]))


def test_gate_flags_a_tuple_that_is_identical_to_a_siblings():
    b = _approved(MIN_BOARD)
    t = b["tuple"]
    ledger = _ledger_with(hero=t["hero"], dial=t["dial"], rail=t["rail"], toc=t["toc"],
                          takeaway=list(t["takeaway"]), table=t["table"], faq=t["faq"])
    f = _checks(b, ledger)
    assert "ledger-tuple-identical" in f
    # one identical sibling is ONE finding, not four: the narrower rules stay silent
    assert sorted(x for x in f if x.startswith("ledger-")) == ["ledger-tuple-identical"], f


def test_gate_lets_a_refreshed_shell_pass_but_not_a_bare_one():
    b = _approved(MIN_BOARD)
    ledger = _ledger_with(hero="hero-a", dial="dial-9", rail="rail-9")
    assert "ledger-shell-owned" in _checks(b, ledger)               # MIN_BOARD's bare hero-a
    b["tuple"]["hero"] = "hero-a#minimal"
    b["approval"]["record_hash"] = PB.record_hash(b)
    assert "ledger-shell-owned" not in _checks(b, ledger)
    ledger["pages"]["sibling"]["hero"] = "hero-a#minimal"           # the same delta, though, is the same shell
    assert "ledger-shell-owned" in _checks(b, ledger)


def test_gate_does_not_police_shared_pool_components():
    """dial-1-clay is on nine pages by design: a shared dial, rail or table is never a FAIL."""
    b = _approved(MIN_BOARD)
    f = _checks(b, _ledger_with(hero="hero-z", dial="dial-1", rail="rail-a", toc="t9", table="table-a", faq="faq-z"))
    assert not any(c.startswith("ledger-") for c in f), f


def test_gate_fails_on_live_header_collision_and_missing_pick():
    b = _approved(MIN_BOARD)
    b["sections"][0]["options"]["pick"] = None
    b["approval"]["picks"] = {}
    b["approval"]["record_hash"] = PB.record_hash(b)
    live = {"/y/": ["Our Blue Staffy Puppies"]}   # a sibling, not "/x/": the gate excludes the board's own page
    f = {x["check"] for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build") if x["sev"] == "FAIL"}
    assert {"header-collision", "signature-no-pick"} <= f


def test_gate_release_stage_fails_on_missing_required_slot_only_at_release():
    b = _approved(MIN_BOARD)
    build = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
    release = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="release")
    assert not any(x["check"] == "asset-required-missing" for x in build)
    assert any(x["check"] == "asset-required-missing" and x["sev"] == "FAIL" for x in release)


def test_gate_h5_h6_minimums_are_warn_on_home_and_location():
    b = _approved(MIN_BOARD)
    f = {x["check"]: x["sev"] for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")}
    assert f.get("min-h5-h6") == "FAIL"           # hub page type: hard
    b["meta"]["page_type"] = "location"; b["approval"]["record_hash"] = PB.record_hash(b)
    f = {x["check"]: x["sev"] for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")}
    assert f.get("min-h5-h6") == "WARN"


def test_gate_whitelist_matches_whole_tokens_not_substrings():
    """"ince" is a puppy-name whitelist entry and it lives inside "Since". Substring
    matching cleared a real crossover; whole-token matching keeps the FAIL."""
    b = _approved(MIN_BOARD)
    b["sections"][0]["tree"][0]["heading"] = "Since 2014 We Have Raised Every Puppy At Home"
    b["approval"]["record_hash"] = PB.record_hash(b)
    live = {"/sibling/": ["Since 2014 We Have Raised Every Puppy At Home"]}
    msgs = [x["msg"] for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
            if x["check"] == "header-collision"]
    assert any("Since 2014" in m for m in msgs), msgs
    assert PB._whitelisted("Ince") and PB._whitelisted("Frequently Asked Questions")
    assert not PB._whitelisted("Since 2014 We Have Raised Every Puppy At Home")


def test_gate_fails_when_the_header_precheck_examined_zero_live_pages():
    b = _approved(MIN_BOARD)
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
    assert any(x["check"] == "header-precheck-examined-zero" and x["sev"] == "FAIL" for x in f)
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={"/other/": ["Where Do We Deliver Each Week?"]},
                         stage="build")
    assert not any(x["check"] == "header-precheck-examined-zero" for x in f)


def test_gate_rejects_an_unknown_stage():
    with pytest.raises(PB.BoardError):
        PB.gate_findings(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, stage="deploy")


def test_board_gate_cli_exits_2_on_an_unknown_flag_and_on_a_missing_board():
    import subprocess
    gate = str(ROOT / "scripts" / "board_gate.py")
    r = subprocess.run([sys.executable, gate, "x", "--publish"], capture_output=True, text=True)
    assert r.returncode == 2 and "usage: board_gate.py" in r.stdout
    r = subprocess.run([sys.executable, gate, "no-such-page-anywhere"], capture_output=True, text=True)
    assert r.returncode == 2 and "board-gate ERROR no board for" in r.stdout


def test_own_live_key_is_the_root_for_the_homepage():
    b = json.loads(json.dumps(MIN_BOARD))
    assert PB.own_live_key(b) == "/x/"
    b["meta"]["page_type"] = "home"
    assert PB.own_live_key(b) == "/"
    b["meta"]["page_type"] = "hub"; b["meta"]["slug"] = "index"
    assert PB.own_live_key(b) == "/"


def test_shingle_hits_carry_the_window_they_matched():
    hits = PB.header_precheck(["Where Do We Deliver Each Week, Exactly?"],
                              {"/y/": ["Where Do We Deliver Each Week?"]})
    assert hits[0]["kind"] == "shingle" and hits[0]["shingle"] == "where do we deliver each"


def test_head_term_shingle_helper():
    # Read from PB.HEAD_TERMS rather than spelled out: the head terms live in
    # dup_content_audit.py, which is re-based in its own task, and a literal here would
    # pin this test to whichever site's vocabulary was current when it was written.
    pk = PB.HEAD_TERMS[1] + " near me"
    assert PB._head_term_shingle(PB.HEAD_TERMS[0], pk)       # a head term
    assert PB._head_term_shingle(PB.HEAD_TERMS[1], pk)       # and the board's own keyword
    assert not PB._head_term_shingle("every puppy we place", pk)
    assert not PB._head_term_shingle("", pk)


def test_gate_exempts_a_head_term_only_shingle_but_not_a_real_one():
    """The head term is in dozens of live headings by design; a page cannot be asked to
    rank for a phrase it is forbidden to write. Precedent: 2026-08-10 §C2."""
    b = _approved(MIN_BOARD)
    ht = PB.HEAD_TERMS[0].title()
    b["sections"][0]["heading"] = "Is a %s Here Right for You?" % ht
    b["approval"]["record_hash"] = PB.record_hash(b)
    head_only = {"/y/": ["%s Glasgow" % ht]}
    msgs = lambda live: [x["msg"] for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
                         if x["check"] == "header-collision"]
    assert msgs(head_only) == []
    real = {"/y/": ["What Health Guarantees Come With Every Puppy We Place?"]}
    b["sections"][0]["heading"] = "What Arrives With Every Puppy We Place?"
    b["approval"]["record_hash"] = PB.record_hash(b)
    assert len(msgs(real)) == 1, msgs(real)


def test_an_exact_head_term_heading_is_never_exempt():
    """The exemption is for shingles. A heading copied whole is copied whole."""
    b = _approved(MIN_BOARD)
    b["sections"][0]["heading"] = PB.HEAD_TERMS[0].title()
    b["approval"]["record_hash"] = PB.record_hash(b)
    f = [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={"/y/": [PB.HEAD_TERMS[0].upper()]},
                                     stage="build") if x["check"] == "header-collision"]
    assert len(f) == 1 and "exact" in f[0]["msg"], f

def test_shingle_hits_report_every_window_not_just_the_first():
    """A heading may open on the head term it is allowed to rank for and still copy a real
    run further along; breaking at the first window would hide the second."""
    ht = PB.HEAD_TERMS[0].title()
    hits = PB.header_precheck(["%s: What Health Guarantees Come With Every Puppy" % ht],
                              {"/y/": ["%s Glasgow" % ht],
                               "/z/": ["Our Promise: What Health Guarantees Come With Every Puppy We Place"]})
    assert hits[0]["shingles"][0] == PB.HEAD_TERMS[0]
    assert "what health guarantees come with" in hits[0]["shingles"]
    assert hits[0]["shingle"] == hits[0]["shingles"][0]      # the first, kept for compatibility


def test_gate_does_not_exempt_a_heading_that_copies_a_run_beyond_the_head_term():
    b = _approved(MIN_BOARD)
    ht = PB.HEAD_TERMS[0].title()
    b["sections"][0]["heading"] = "%s: What Health Guarantees Come With Every Puppy" % ht
    b["approval"]["record_hash"] = PB.record_hash(b)
    live = {"/y/": ["%s Glasgow" % ht],
            "/z/": ["Our Promise: What Health Guarantees Come With Every Puppy We Place"]}
    f = [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
         if x["check"] == "header-collision"]
    assert len(f) == 1, f


def test_pick_tuple_mismatch_is_a_warn_on_a_nav_section():
    b = _approved(MIN_BOARD)
    b["sections"][0]["shape"] = "nav"
    b["sections"][0]["options"]["pick"] = "toc-t2-chip-cloud#state-chips"
    b["tuple"]["toc"] = "toc-t2-chip-cloud"                  # the stale bare id
    b["approval"]["record_hash"] = PB.record_hash(b)
    f = [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={"/y/": ["Something Else Entirely Here Now"]},
                                     stage="build") if x["check"] == "pick-tuple-mismatch"]
    assert len(f) == 1 and f[0]["sev"] == "WARN", f
    b["tuple"]["toc"] = "toc-t2-chip-cloud#state-chips"      # the ids agree
    b["approval"]["record_hash"] = PB.record_hash(b)
    assert [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={"/y/": ["Something Else Entirely Here Now"]},
                                        stage="build") if x["check"] == "pick-tuple-mismatch"] == []

def test_board_html_carries_every_block_and_the_theme_rules(tmp_path):
    import build_page_board as BPB
    b = _approved(MIN_BOARD)
    ont, ledger = ONT_OK, LEDGER_EMPTY
    html = BPB.render(b, ont, ledger, live={}, thumbs={}, slug="x")
    for marker in ["data-title=\"1. Brief\"", "data-title=\"2. H1 and meta\"", "data-title=\"3. Outline\"", "data-title=\"4. Distribution\"",
                   "id=\"entity-graph\"", "data-title=\"6. Component options\"", "data-title=\"7. Asset slots\"", "id=\"approve\""]:
        assert marker in html, marker
    assert ":root{" in html and "prefers-color-scheme: dark" in html and ':root[data-theme="dark"]' in html
    assert "body{margin:0;background:var(--ground)" in html
    assert "claude.use(\"db\")" in html and "boards/x" in html
    assert "<title>Page Board: x</title>" in html


def test_board_html_flags_header_collisions_inline():
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={"/y/": ["Our Blue Staffy Puppies"]}, thumbs={}, slug="x")
    assert "exact match with /y/" in html


def test_board_html_escapes_record_text_in_every_context():
    """Record text is breeder- and agent-written, and the board renders it into three
    contexts that each read different characters: HTML, markdown, and the graph's JSON
    inside a <script>. A `</script>` in any of them would end the block and drop the rest
    of the page, so none may survive raw."""
    import re
    import build_page_board as BPB
    b = json.loads(json.dumps(MIN_BOARD))
    b["brief"]["goal"] = "</script><b>x</b>"
    b["sections"][0]["heading"] = "# a | b *c* _d_ </script>"
    html = BPB.render(_approved(b), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")

    assert "&lt;/script&gt;&lt;b&gt;x&lt;/b&gt;" in html          # the goal, escaped
    assert "<b>x</b>" not in html
    assert "\\# a \\| b \\*c\\* \\_d\\_" in html                  # the heading, markdown-neutral
    assert "<\\/script>" in html                                  # the graph label, JSON-escaped
    blocks = re.findall(r'<script type="text/markdown"[^>]*>(.*?)\n</script>', html, re.S)
    assert len(blocks) == 10    # eight numbered blocks plus 3b (image plan) and 5b (the kit strip)
    for i, blk in enumerate(blocks):
        assert "</script" not in blk, i


# ---------------------------------------------------------------- canvas artboards

# --- Task 10: approval read-back, promotions, ledger append, text write-back -------------

def _hub_board(slug="hub-test"):
    b = json.loads(json.dumps(MIN_BOARD))
    b["meta"]["slug"] = slug
    b["meta"]["status"] = "boarded"
    b["sections"][0]["entities"] = ["ont:staffordshire-bull-terrier", "ont:new-thing"]
    return b


ONT_PROMOTE = {"entities": [
    {"id": "ont:staffordshire-bull-terrier", "name": "Staffordshire Bull Terrier", "aliases": [], "class": "Organism",
     "authorization": "ASSERTED", "source": "x", "owner_page": None},
    {"id": "ont:new-thing", "name": "New", "aliases": [], "class": "Health",
     "authorization": "PROPOSED", "source": "ledger#y", "owner_page": None},
    {"id": "ont:no-source", "name": "NS", "aliases": [], "class": "Health",
     "authorization": "PROPOSED", "source": None, "owner_page": None},
    {"id": "ont:unused-thing", "name": "Unused", "aliases": [], "class": "Health",
     "authorization": "PROPOSED", "source": "ledger#z", "owner_page": None}]}


def test_approve_writes_approval_ledger_and_promotions():
    import board_approve as BA
    b = _hub_board()
    ont = json.loads(json.dumps(ONT_PROMOTE))
    ledger = {"pools": {"inventory": ["avail-b"]}, "pages": {}}
    inbox = {"approved_at": "2026-09-12T12:00:00Z", "h1": 2, "picks": {"puppies": "avail-b"},
             "notes": {"puppies": "shorter eyebrow"}, "canvas_version": "v7", "record_hash": PB.record_hash(b)}
    out = BA.apply_approval(b, inbox, ont, ledger)
    # Picks and notes ARE hashed content, so the stamped hash is the record the breeder
    # saw WITH their choices in it — every field but record_hash is the inbox verbatim.
    assert {k: v for k, v in out["board"]["approval"].items()
            if k not in ("record_hash", "tuple_before")} == \
           {k: v for k, v in inbox.items() if k != "record_hash"}
    # The authored tuple is stamped beside the hash so a re-run can undo the derivation.
    assert out["board"]["approval"]["tuple_before"] == MIN_BOARD["tuple"]
    assert PB.approval_matches(out["board"]) is True
    assert out["board"]["meta"]["status"] == "approved"
    assert out["board"]["h1"]["pick"] == 2
    assert out["board"]["sections"][0]["options"]["pick"] == "avail-b"
    assert out["board"]["sections"][0]["options"]["note"] == "shorter eyebrow"
    # The tuple is DERIVED from the picks now, not copied from the authored record: this
    # board's one section is `puppies`, which is section content and not a tuple axis, so
    # the authored `hero-a` is not carried and the hero axis records nothing.
    assert out["ledger"]["pages"]["hub-test"]["hero"] == ""
    assert out["ledger"]["pages"]["hub-test"]["toc"] == BA.FIXED_TOC
    auth = {e["id"]: e["authorization"] for e in out["ontology"]["entities"]}
    assert auth["ont:new-thing"] == "ASSERTED"          # referenced + sourced
    assert auth["ont:no-source"] == "PROPOSED"          # no source, never promoted
    assert auth["ont:unused-thing"] == "PROPOSED"       # sourced but this page never names it
    assert b["meta"]["status"] == "boarded"             # the caller's record is not mutated


def test_approve_refuses_a_stale_hash():
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    inbox = {"approved_at": "t", "h1": 0, "picks": {}, "notes": {}, "canvas_version": None,
             "record_hash": "f" * 64}
    with pytest.raises(PB.BoardError):
        BA.apply_approval(b, inbox, ONT_OK, LEDGER_EMPTY)


def test_approve_clears_a_note_with_an_empty_string():
    import board_approve as BA
    b = _hub_board()
    b["sections"][0]["options"]["note"] = "an older note"
    inbox = {"approved_at": "t", "h1": 0, "picks": {"puppies": "avail-b"}, "notes": {"puppies": ""},
             "canvas_version": None, "record_hash": PB.record_hash(b)}
    out = BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)),
                            {"pools": {"inventory": ["avail-b"]}, "pages": {}})
    assert out["board"]["sections"][0]["options"]["note"] == ""


def test_ledger_refuses_an_unrenamed_refresh_placeholder_in_a_recorded_tuple():
    """The guard lives on validate_ledger, which is what board_approve.py calls before it
    writes. It is asserted here rather than through an approval because a DERIVED tuple can
    no longer carry a `#refresh`: the id is built from a shape and a style pick, neither of
    which can contain a `#`. An authored one is simply not carried any more."""
    led = {"pools": {"hero": ["hero-a"]},
           "pages": {"p": {"hero": "hero-a#refresh", "dial": "", "rail": "", "toc": "",
                           "table": "", "faq": "", "takeaway": [], "h6_prefixes": []}}}
    with pytest.raises(PB.BoardError) as e:
        PB.validate_ledger(led)
    assert "refresh" in str(e.value)


def test_approve_drops_an_authored_refresh_placeholder_instead_of_recording_it():
    import board_approve as BA
    b = _hub_board()
    b["tuple"]["hero"] = "hero-a#refresh"
    inbox = {"approved_at": "t", "h1": 0, "picks": {"puppies": "avail-b"}, "notes": {},
             "canvas_version": None, "record_hash": PB.record_hash(b)}
    out = BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)),
                            {"pools": {"inventory": ["avail-b"]}, "pages": {}})
    assert out["board"]["tuple"]["hero"] == ""
    assert out["ledger"]["pages"]["hub-test"]["hero"] == ""
    # ...but the authored value is still recoverable, so the derivation can be undone.
    assert out["board"]["approval"]["tuple_before"]["hero"] == "hero-a#refresh"


def test_approve_refuses_a_board_whose_signature_section_has_no_pick():
    import board_approve as BA
    b = _hub_board()
    inbox = {"approved_at": "t", "h1": 0, "picks": {}, "notes": {}, "canvas_version": None,
             "record_hash": PB.record_hash(b)}
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)),
                          {"pools": {"inventory": ["avail-b"]}, "pages": {}})
    assert "puppies" in str(e.value)


def test_approve_refuses_a_pick_for_a_section_that_does_not_exist():
    import board_approve as BA
    b = _hub_board()
    inbox = {"approved_at": "t", "h1": 0, "picks": {"puppies": "avail-b", "ghost": "avail-b"},
             "notes": {}, "canvas_version": None, "record_hash": PB.record_hash(b)}
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)),
                          {"pools": {"inventory": ["avail-b"]}, "pages": {}})
    assert "ghost" in str(e.value)


def test_approve_records_the_ledger_entry_in_the_shape_the_twelve_pages_use():
    """Same eight keys as every existing ledger page, and the H6 prefixes come from the
    record's own H6 nodes — a prefix the page declared but never spent stays free."""
    import board_approve as BA
    b = _hub_board()
    inbox = {"approved_at": "t", "h1": 0, "picks": {"puppies": "avail-b"}, "notes": {},
             "canvas_version": None, "record_hash": PB.record_hash(b)}
    out = BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)),
                            {"pools": {"inventory": ["avail-b"]}, "pages": {}})
    entry = out["ledger"]["pages"]["hub-test"]
    assert sorted(entry) == ["dial", "faq", "h6_prefixes", "hero", "rail", "table", "takeaway", "toc"]
    assert entry["h6_prefixes"] == ["Kennel Note:"]        # declared three, spent one
    assert PB.spent_h6_prefixes(out["ledger"]) == {"Kennel Note:": ["hub-test"]}


def test_text_writeback_updates_the_record_from_the_saved_artboard(tmp_path):
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["options"]["pick"] = "avail-b"
    art = tmp_path / "puppies--avail-b--Desktop.dc.html"
    art.write_text('<div id="root"><h2 style="x">What Do We Have for Sale Today?</h2>'
                   '<p>Our puppies, today.</p></div>', encoding="utf-8")
    changed = BA.writeback_text(b, tmp_path)
    assert b["sections"][0]["heading"] == "What Do We Have for Sale Today?"
    assert changed == [("puppies", "heading", "Our Blue Staffy Puppies",
                        "What Do We Have for Sale Today?")]


def test_text_writeback_maps_a_hash_in_the_pick_to_an_underscore_in_the_filename(tmp_path):
    """board_canvas.py writes `#` as `_`; a write-back that looked for the `#` spelling
    would silently find no artboard and report no change."""
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["id"] = "grid"
    b["sections"][0]["options"]["pick"] = "toc-t1-numbered-ledger#state-chips"
    (tmp_path / "grid--toc-t1-numbered-ledger_state-chips--Desktop.dc.html").write_text(
        "<h2>Where Do We Ship Each Week?</h2>", encoding="utf-8")
    changed = BA.writeback_text(b, tmp_path)
    assert changed == [("grid", "heading", "Our Blue Staffy Puppies",
                        "Where Do We Ship Each Week?")]
    assert b["sections"][0]["heading"] == "Where Do We Ship Each Week?"


def test_approve_main_reads_a_wrapped_inbox_and_writes_all_three_files(tmp_path, monkeypatch):
    """read_db may hand the document back wrapped in {"data": ...}; main() unwraps it and
    writes the board, the ledger and the ontology."""
    import board_approve as BA
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    monkeypatch.setattr(PB, "ONTOLOGY", tmp_path / "data" / "bsuk-ontology.json")
    monkeypatch.setattr(PB, "LEDGER", tmp_path / "data" / "component-ledger.json")
    b = _hub_board()
    PB.save_board("hub-test", b)
    PB.ONTOLOGY.parent.mkdir(parents=True, exist_ok=True)
    PB.ONTOLOGY.write_text(json.dumps(ONT_PROMOTE), encoding="utf-8")
    PB.LEDGER.write_text(json.dumps({"pools": {"inventory": ["avail-b"]}, "pages": {}}), encoding="utf-8")
    inbox_dir = tmp_path / "data" / "boards" / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    (inbox_dir / "hub-test.json").write_text(json.dumps({"data": {
        "approved_at": "2026-09-12T12:00:00Z", "h1": 1, "picks": {"puppies": "avail-b"},
        "notes": {}, "canvas_version": None, "record_hash": PB.record_hash(b)}}), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test"])
    BA.main()
    saved = PB.load_board("hub-test")
    assert saved["meta"]["status"] == "approved" and PB.approval_matches(saved) is True
    assert PB.load_ledger()["pages"]["hub-test"]["toc"] == BA.FIXED_TOC   # the derived tuple landed
    assert {e["id"]: e["authorization"] for e in PB.load_ontology()["entities"]}["ont:new-thing"] == "ASSERTED"


def _approve_main_fixture(tmp_path, monkeypatch, record_hash=None, with_canvas=None):
    """Plant a hub-test board, ledger, ontology and an inbox under a tmp ROOT for main() tests.
    `with_canvas` = (directory, h2 text) writes a Desktop artboard for the puppies/avail-b pick."""
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    monkeypatch.setattr(PB, "ONTOLOGY", tmp_path / "data" / "bsuk-ontology.json")
    monkeypatch.setattr(PB, "LEDGER", tmp_path / "data" / "component-ledger.json")
    b = _hub_board()
    PB.save_board("hub-test", b)
    PB.ONTOLOGY.parent.mkdir(parents=True, exist_ok=True)
    PB.ONTOLOGY.write_text(json.dumps(ONT_PROMOTE), encoding="utf-8")
    PB.LEDGER.write_text(json.dumps({"pools": {"inventory": ["avail-b"]}, "pages": {}}), encoding="utf-8")
    inbox_dir = tmp_path / "data" / "boards" / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    (inbox_dir / "hub-test.json").write_text(json.dumps({
        "approved_at": "2026-09-12T12:00:00Z", "h1": 1, "picks": {"puppies": "avail-b"},
        "notes": {}, "canvas_version": None,
        "record_hash": record_hash or PB.record_hash(b)}), encoding="utf-8")
    if with_canvas:
        d, h2 = with_canvas
        d.mkdir(parents=True, exist_ok=True)
        (d / "puppies--avail-b--Desktop.dc.html").write_text(
            f'<div id="root"><h2 style="x">{h2}</h2></div>', encoding="utf-8")
    return b


def test_approve_main_exits_2_on_a_stale_hash_and_writes_nothing(tmp_path, monkeypatch):
    import board_approve as BA
    _approve_main_fixture(tmp_path, monkeypatch, record_hash="f" * 64)
    before = {p: p.read_text(encoding="utf-8") for p in
              (PB.board_path("hub-test"), PB.LEDGER, PB.ONTOLOGY)}
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test"])
    with pytest.raises(SystemExit) as ex:
        BA.main()
    assert ex.value.code == 2
    for p, text in before.items():
        assert p.read_text(encoding="utf-8") == text, f"{p.name} was written on a refused approval"
    assert PB.load_board("hub-test")["meta"]["status"] != "approved"


def test_approve_main_exits_2_when_the_inbox_is_missing(tmp_path, monkeypatch, capsys):
    import board_approve as BA
    _approve_main_fixture(tmp_path, monkeypatch)
    inbox = tmp_path / "data" / "boards" / "inbox" / "hub-test.json"
    inbox.unlink()
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test"])
    with pytest.raises(SystemExit) as ex:
        BA.main()
    assert ex.value.code == 2
    assert str(inbox) in capsys.readouterr().out


def test_approve_main_defaults_the_canvas_dir_to_docs_design_board_slug(tmp_path, monkeypatch):
    import board_approve as BA
    default = tmp_path / "docs" / "design" / "board-hub-test"
    _approve_main_fixture(tmp_path, monkeypatch, with_canvas=(default, "Puppies Heading From the Default Canvas"))
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test"])
    BA.main()
    saved = PB.load_board("hub-test")
    assert saved["sections"][0]["heading"] == "Puppies Heading From the Default Canvas"
    assert PB.approval_matches(saved) is True


def test_approve_main_prefers_an_explicit_canvas_dir_over_the_default(tmp_path, monkeypatch):
    import board_approve as BA
    default = tmp_path / "docs" / "design" / "board-hub-test"
    _approve_main_fixture(tmp_path, monkeypatch, with_canvas=(default, "Heading From the Default"))
    other = tmp_path / "elsewhere"
    other.mkdir()
    (other / "puppies--avail-b--Desktop.dc.html").write_text(
        '<div id="root"><h2>Heading From the Explicit Dir</h2></div>', encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test", "--canvas-dir", str(other)])
    BA.main()
    assert PB.load_board("hub-test")["sections"][0]["heading"] == "Heading From the Explicit Dir"


# --- Task 10 quality pass: atomic writes, candidate-checked picks, strict write-back -----

def test_approve_refuses_a_pick_that_is_not_on_the_offered_menu():
    import board_approve as BA
    b = _hub_board()
    inbox = {"approved_at": "t", "h1": 0, "picks": {"puppies": "avail-z"}, "notes": {},
             "canvas_version": None, "record_hash": PB.record_hash(b)}
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)),
                          {"pools": {"inventory": ["avail-b"]}, "pages": {}})
    assert "puppies" in str(e.value) and "avail-z" in str(e.value)


def test_approve_accepts_a_delta_rename_of_an_offered_candidate():
    """The board offers `base` (or `base#refresh`) and the author renames it to the axis
    the option actually varies — `toc-t2-chip-cloud#state-chips` is the shipped hub's own
    pick. A strict membership test would refuse the documented workflow, so the menu is
    matched on the BASE."""
    import board_approve as BA
    b = _hub_board()
    inbox = {"approved_at": "t", "h1": 0, "picks": {"puppies": "avail-b#state-chips"}, "notes": {},
             "canvas_version": None, "record_hash": PB.record_hash(b)}
    out = BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)),
                            {"pools": {"inventory": ["avail-b"]}, "pages": {}})
    assert out["board"]["sections"][0]["options"]["pick"] == "avail-b#state-chips"


def test_writeback_raises_when_the_canvas_dir_does_not_exist(tmp_path):
    """A canvas directory the caller named and that is not there is a typo, not an absence
    of tweaks — returning [] would silently approve the un-tweaked record."""
    import board_approve as BA
    with pytest.raises(PB.BoardError) as e:
        BA.writeback_text(json.loads(json.dumps(MIN_BOARD)), tmp_path / "nope")
    assert "nope" in str(e.value)


def test_writeback_raises_when_an_artboard_carries_two_h2s(tmp_path):
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["options"]["pick"] = "avail-b"
    (tmp_path / "puppies--avail-b--Desktop.dc.html").write_text(
        "<h2>First Heading Here</h2><div><h2>Second Heading Here</h2></div>", encoding="utf-8")
    with pytest.raises(PB.BoardError) as e:
        BA.writeback_text(b, tmp_path)
    assert "puppies" in str(e.value)
    assert b["sections"][0]["heading"] == "Our Blue Staffy Puppies"


def test_writeback_warns_on_a_missing_artboard_and_on_one_without_an_h2(tmp_path, capsys):
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["options"]["pick"] = "avail-b"
    assert BA.writeback_text(b, tmp_path) == []                      # nothing on disk at all
    assert "puppies" in capsys.readouterr().err
    (tmp_path / "puppies--avail-b--Desktop.dc.html").write_text("<p>no heading</p>", encoding="utf-8")
    assert BA.writeback_text(b, tmp_path) == []
    assert "no <h2>" in capsys.readouterr().err


def test_approve_main_exits_2_and_leaves_the_board_unapproved_when_the_ledger_write_fails(
        tmp_path, monkeypatch):
    """Three documents, one approval: a board stamped approved with no ledger row would
    leave every component it just claimed unowned, and the next page would claim them."""
    import board_approve as BA
    _approve_main_fixture(tmp_path, monkeypatch)
    real_replace = BA.os.replace

    def flaky(src, dst):
        if str(dst).endswith("component-ledger.json"):
            raise OSError("disk full")
        return real_replace(src, dst)

    monkeypatch.setattr(BA.os, "replace", flaky)
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test"])
    with pytest.raises(SystemExit) as ex:
        BA.main()
    assert ex.value.code == 2
    assert PB.load_board("hub-test")["meta"]["status"] != "approved"
    assert PB.load_ledger()["pages"] == {}


def test_approve_main_exits_2_on_a_slug_the_record_disagrees_with(tmp_path, monkeypatch, capsys):
    import board_approve as BA
    b = _approve_main_fixture(tmp_path, monkeypatch)
    b["meta"]["slug"] = "hub-other"
    PB.board_path("hub-test").write_text(json.dumps(b), encoding="utf-8")
    # the hash the inbox carries has to be the hash of the record as it now stands
    inbox = tmp_path / "data" / "boards" / "inbox" / "hub-test.json"
    doc = json.loads(inbox.read_text(encoding="utf-8"))
    doc["record_hash"] = PB.record_hash(b)
    inbox.write_text(json.dumps(doc), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test"])
    with pytest.raises(SystemExit) as ex:
        BA.main()
    assert ex.value.code == 2
    assert "slug" in capsys.readouterr().out


def test_approve_main_exits_2_when_canvas_dir_has_no_value(tmp_path, monkeypatch):
    import board_approve as BA
    _approve_main_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test", "--canvas-dir"])
    with pytest.raises(SystemExit) as ex:
        BA.main()
    assert ex.value.code == 2


def test_approve_main_takes_the_last_canvas_dir_and_accepts_the_equals_form(tmp_path, monkeypatch):
    import board_approve as BA
    default = tmp_path / "docs" / "design" / "board-hub-test"
    _approve_main_fixture(tmp_path, monkeypatch, with_canvas=(default, "Heading From the Default"))
    first, last = tmp_path / "first", tmp_path / "last"
    for d, h2 in ((first, "Heading From the First Dir"), (last, "Heading From the Last Dir")):
        d.mkdir()
        (d / "puppies--avail-b--Desktop.dc.html").write_text(f"<h2>{h2}</h2>", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test",
                                      "--canvas-dir", str(first), f"--canvas-dir={last}"])
    BA.main()
    assert PB.load_board("hub-test")["sections"][0]["heading"] == "Heading From the Last Dir"


def test_approve_main_reports_only_the_promotions_this_run_made(tmp_path, monkeypatch, capsys):
    """ONT_PROMOTE already holds one ASSERTED entity; counting every ASSERTED row would
    report two promotions for a run that made one."""
    import board_approve as BA
    _approve_main_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "argv", ["board_approve.py", "hub-test"])
    BA.main()
    assert "1 PROPOSED→ASSERTED" in capsys.readouterr().out


# --- Task 11 close-out: idempotent re-approval, `_` fallback, gate counts, rsplit ids ----

def test_record_hash_bare_ignores_picks_notes_and_h1_pick():
    """The hash of the record as it stood BEFORE an approval wrote the choices in."""
    bare = json.loads(json.dumps(MIN_BOARD))
    filled = json.loads(json.dumps(MIN_BOARD))
    filled["sections"][0]["options"]["pick"] = "avail-b"
    filled["sections"][0]["options"]["note"] = "shorter eyebrow"
    filled["h1"]["pick"] = 2
    assert PB.record_hash_bare(filled) == PB.record_hash(bare)
    assert PB.record_hash_bare(filled) != PB.record_hash(filled)
    filled["sections"][0]["heading"] = "Something Else"      # a real edit still moves it
    assert PB.record_hash_bare(filled) != PB.record_hash(bare)


def _idempotent_inbox(board):
    return {"approved_at": "2026-09-12T12:00:00Z", "h1": 2, "picks": {"puppies": "avail-b"},
            "notes": {"puppies": "shorter eyebrow"}, "canvas_version": "v7",
            "record_hash": PB.record_hash(board)}


def test_approve_twice_with_the_same_inbox_is_idempotent():
    """Re-running the approval step is a normal operator move (a rerun, a retry after a
    failed write). The first run writes the picks INTO the record, which moves its hash —
    so the second run has to recognise the record it itself produced."""
    import board_approve as BA
    b = _hub_board()
    ledger = {"pools": {"inventory": ["avail-b"]}, "pages": {}}
    inbox = _idempotent_inbox(b)
    first = BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)), ledger)
    second = BA.apply_approval(first["board"], inbox, json.loads(json.dumps(ONT_PROMOTE)), ledger)
    assert PB.record_hash(second["board"]) == PB.record_hash(first["board"])
    assert second["board"]["sections"][0]["options"]["pick"] == "avail-b"
    assert second["board"]["sections"][0]["options"]["note"] == "shorter eyebrow"
    assert second["board"]["h1"]["pick"] == 2
    assert PB.approval_matches(second["board"]) is True


def _styled(shape, sid, pick):
    s = json.loads(json.dumps(MIN_BOARD["sections"][0]))
    s.update({"id": sid, "shape": shape, "styles": ["S1", "S2", "S3"]})
    s["options"]["pick"] = pick
    return s


def test_derive_tuple_reads_each_axis_off_the_shape_that_feeds_it():
    """One styled section per axis. `sheet` lands on `rail` (the ledger has no eighth
    axis for the mobile sheet) and `toc` is the fixed kit page nav, picked by nobody."""
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"] = [_styled("hero", "top", "S3"), _styled("faq", "questions", "S1"),
                     _styled("takeaways", "keys", "S2"), _styled("dial", "desktop-dial", "S2"),
                     _styled("sheet", "mobile-sections", "S3")]
    t = BA.derive_tuple(b, MIN_BOARD["tuple"])
    assert (t["hero"], t["faq"], t["dial"], t["rail"], t["toc"], t["table"]) == \
           ("hero-s3", "faq-s1", "dial-s2", "rail-s3", "pagenav-c", "")
    assert t["takeaway"] == ["takeaways-s2"]
    # Authored, not derived: carried through untouched.
    assert t["h6_prefixes"] == MIN_BOARD["tuple"]["h6_prefixes"]
    assert t["newsletter"] == MIN_BOARD["tuple"]["newsletter"]


def test_derive_tuple_ignores_the_shapes_that_are_section_content():
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"] = [_styled(sh, sh, "S2") for sh in
                     ("reviews", "puppies", "form", "trust", "stats", "divider")]
    t = BA.derive_tuple(b, MIN_BOARD["tuple"])
    assert [t[k] for k in BA.DERIVED_ID_AXES] == ["", "", "", "", ""]
    assert t["takeaway"] == []


def test_derive_tuple_gives_two_boards_that_picked_differently_different_tuples():
    """The point of the change: `ledger-tuple-identical` fired between the first three
    approved records because every one of them wore the authored "kit" sentinel."""
    import board_approve as BA
    a = json.loads(json.dumps(MIN_BOARD)); a["sections"] = [_styled("faq", "questions", "S1")]
    c = json.loads(json.dumps(MIN_BOARD)); c["sections"] = [_styled("faq", "questions", "S3")]
    assert BA.derive_tuple(a, MIN_BOARD["tuple"]) != BA.derive_tuple(c, MIN_BOARD["tuple"])


def test_approve_twice_is_idempotent_when_the_outline_shipped_with_notes():
    """The thank-you and contact records ship notes written by the OUTLINE author, which
    the breeder's approval carried back unchanged. record_hash_bare() cleared them, so it
    described a record that never existed and re-approving either was refused as a
    post-approval edit — with the derived tuple in play, that refusal is permanent."""
    import board_approve as BA
    b = _hub_board()
    b["sections"][0]["options"]["note"] = "written by the outline author"
    ledger = {"pools": {"inventory": ["avail-b"]}, "pages": {}}
    inbox = {"approved_at": "t", "h1": 2, "picks": {"puppies": "avail-b"},
             "notes": {"puppies": "written by the outline author"}, "canvas_version": None,
             "record_hash": PB.record_hash(b)}
    first = BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)), ledger)
    second = BA.apply_approval(first["board"], inbox, json.loads(json.dumps(ONT_PROMOTE)), ledger)
    assert PB.record_hash(second["board"]) == PB.record_hash(first["board"])
    assert second["board"]["tuple"] == first["board"]["tuple"]
    assert PB.approval_matches(second["board"]) is True


def test_approve_still_refuses_a_record_edited_after_approval():
    import board_approve as BA
    b = _hub_board()
    ledger = {"pools": {"inventory": ["avail-b"]}, "pages": {}}
    inbox = _idempotent_inbox(b)
    first = BA.apply_approval(b, inbox, json.loads(json.dumps(ONT_PROMOTE)), ledger)
    edited = first["board"]
    edited["sections"][0]["heading"] = "A Heading Nobody Approved"
    with pytest.raises(PB.BoardError):
        BA.apply_approval(edited, inbox, json.loads(json.dumps(ONT_PROMOTE)), ledger)


def test_writeback_reads_the_underscore_spelling(tmp_path):
    """`_` is the one spelling on disk (2026-09-12): the canvas writer emits it and the
    published design canvas — whose helper refuses `+` — extracts it unchanged."""
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["id"] = "grid"
    b["sections"][0]["options"]["pick"] = "toc-t1-numbered-ledger#refresh"
    (tmp_path / "grid--toc-t1-numbered-ledger_refresh--Desktop.dc.html").write_text(
        "<h2>Where Do We Ship Each Week?</h2>", encoding="utf-8")
    assert BA.writeback_text(b, tmp_path) == [
        ("grid", "heading", "Our Blue Staffy Puppies", "Where Do We Ship Each Week?")]


def test_artboard_names_offers_only_the_underscore_spelling():
    """The `+` fallback is gone: one spelling on disk means one name to try, and a second
    name that can never exist only hides a real miss behind a longer WARN line."""
    import board_approve as BA
    assert BA.artboard_names("grid", "toc-a#refresh") == ["grid--toc-a_refresh--Desktop.dc.html"]
    assert BA.artboard_names("grid", "toc-a") == ["grid--toc-a--Desktop.dc.html"]


def test_writeback_ignores_the_retired_plus_spelling(tmp_path, capsys):
    """A stale `+`-named artboard left over from the old spelling is not a match — it warns
    rather than writing back a heading from a file the current canvas never emits."""
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["id"] = "grid"
    b["sections"][0]["options"]["pick"] = "toc-t1-numbered-ledger#refresh"
    (tmp_path / "grid--toc-t1-numbered-ledger+refresh--Desktop.dc.html").write_text(
        "<h2>Where Do We Ship Each Week?</h2>", encoding="utf-8")
    assert BA.writeback_text(b, tmp_path) == []
    assert "no artboard for grid" in capsys.readouterr().err


def test_writeback_warns_when_an_artboard_h2_strips_to_empty(tmp_path, capsys):
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["options"]["pick"] = "avail-b"
    (tmp_path / "puppies--avail-b--Desktop.dc.html").write_text(
        "<h2><span> </span></h2>", encoding="utf-8")
    assert BA.writeback_text(b, tmp_path) == []
    assert "empty" in capsys.readouterr().err


def test_atomic_write_uses_a_unique_tmp_name(tmp_path, monkeypatch):
    import board_approve as BA
    seen, real = [], BA.os.replace

    def spy(src, dst):
        seen.append(str(src))
        return real(src, dst)

    monkeypatch.setattr(BA.os, "replace", spy)
    BA._atomic_write(tmp_path / "a.json", "1\n")
    BA._atomic_write(tmp_path / "a.json", "2\n")
    assert (tmp_path / "a.json").read_text(encoding="utf-8") == "2\n"
    assert len(set(seen)) == 2                       # two runs never race on one .tmp name
    assert list(tmp_path.glob("*.tmp")) == []        # and nothing is left behind


LEDGER_ONE_SIBLING = {"pools": {"inventory": ["avail-b"]}, "refresh_pools": [],
                      "pages": {"sib": {"hero": "hero-z", "dial": "dial-9", "rail": "rail-z", "toc": "t9",
                                        "table": "table-z", "faq": "faq-z", "takeaway": ["k9"],
                                        "h6_prefixes": ["Field Note:"]}}}


def test_gate_warns_when_the_component_ledger_has_no_pages():
    """An empty ledger makes the five ledger-* checks examine nothing, and a PASS that
    examined nothing is not a pass (.claude/skills/bsuk-gate-integrity/SKILL.md)."""
    live = {"/other/": ["Where Do We Deliver Each Week?"]}
    empty = [x for x in PB.gate_findings(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live, stage="build")
             if x["check"] == "ledger-examined-zero"]
    assert len(empty) == 1 and empty[0]["sev"] == "WARN"
    assert [x for x in PB.gate_findings(_approved(MIN_BOARD), ONT_OK, LEDGER_ONE_SIBLING, live, stage="build")
            if x["check"] == "ledger-examined-zero"] == []


def test_board_gate_banner_counts_ledger_siblings_assets_and_the_pages_own_live_page(tmp_path, monkeypatch, capsys):
    """The banner has to show what every family examined — and the own page is no longer
    popped out of the live corpus, because header_hits() excludes it internally."""
    import board_gate as BG
    monkeypatch.setattr(PB, "load_board", lambda slug: _approved(MIN_BOARD))
    monkeypatch.setattr(PB, "load_ontology", lambda: ONT_OK)
    monkeypatch.setattr(PB, "load_ledger", lambda: LEDGER_ONE_SIBLING)
    (tmp_path / "dist").mkdir()
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(PB, "live_headings", lambda: {
        "/x/": ["Our Blue Staffy Puppies"],          # the board's own live page
        "/other/": ["Where Do We Deliver Each Week?"]})
    monkeypatch.setattr(sys, "argv", ["board_gate.py", "x"])
    with pytest.raises(SystemExit):
        BG.main()
    out = capsys.readouterr().out
    banner = out.splitlines()[0]
    assert "2 live pages" in banner, banner
    assert "1 ledger siblings" in banner and "1 assets" in banner, banner
    assert "header-collision" not in out                          # its own headings are its own


def test_header_hits_excludes_the_homepage_without_a_pop():
    """The homepage's slug is "", so a caller-side `live.pop("/"+slug+"/")` would pop "//"
    and leave the homepage colliding with itself. header_hits() keys it on own_live_key()."""
    b = json.loads(json.dumps(MIN_BOARD))
    b["meta"]["slug"] = ""
    b["meta"]["page_type"] = "home"
    live = {"/": [t for _, t in PB.all_headings(b)],
            "/other/": ["Something Else Entirely Different Here"]}
    assert PB.header_hits(b, live) == []


def test_file_token_round_trips_through_unfile_token():
    """One spelling on every surface outside the record: `#` travels as `_`. A section id
    may carry `--` and a delta may carry `-`, but `_` appears in no id the schema allows
    (^[a-z0-9-]+(#[a-z0-9-]+)?$), so the mapping cannot be ambiguous."""
    assert PB.file_token("toc-a#refresh") == "toc-a_refresh"
    assert PB.unfile_token("toc-a_refresh") == "toc-a#refresh"
    assert PB.file_token("toc-t1-numbered-ledger#state-chips") == "toc-t1-numbered-ledger_state-chips"
    assert PB.unfile_token(PB.file_token("toc-t1-numbered-ledger#state-chips")) == "toc-t1-numbered-ledger#state-chips"
    assert PB.file_token("toc-t1-numbered-ledger") == "toc-t1-numbered-ledger"
    assert PB.unfile_token(PB.file_token("toc-a")) == "toc-a"


def test_board_renders_an_excluded_shell_owner_when_only_owner_is_set(monkeypatch):
    """The board schema requires `owner` and only allows `owners`, so a record written by
    hand may carry the singular alone — and an excluded card with no owner reads as a bug."""
    import build_page_board as BPB
    monkeypatch.setattr(PB, "candidates_for", lambda shape, ledger, slug: (
        ["avail-b"], [{"component": "avail-a", "owner": "sibling-page"}]))
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "owned by sibling-page" in html


# --- Task 12: the canvas writer owns Main.dc.html and canvas.json ------------------------

def test_meta_set_rejects_a_long_title_a_description_off_band_and_a_fourth_variant():
    for field, i, value in (("titles", 1, "A" * 71), ("descriptions", 0, "d" * 139),
                            ("descriptions", 0, "d" * 161), ("titles", 3, "A fourth title")):
        bad = json.loads(json.dumps(MIN_BOARD))
        bad["meta_set"][field][i:i + 1] = [value]
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)


def test_meta_pick_falls_back_to_the_recommendation_and_hash_bare_resets_it():
    b = json.loads(json.dumps(MIN_BOARD))
    before = PB.record_hash_bare(b)
    assert PB.meta_pick(b) == (b["meta_set"]["titles"][0], b["meta_set"]["descriptions"][0])
    b["meta_set"]["pick"] = {"title": 2, "description": 1}
    assert PB.meta_pick(b) == (b["meta_set"]["titles"][2], b["meta_set"]["descriptions"][1])
    assert PB.record_hash(b) != before and PB.record_hash_bare(b) == before


def test_gate_meta_no_pick_warns_at_build_and_fails_at_release():
    b = _approved(MIN_BOARD)
    found = lambda stage: [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage=stage)
                           if x["check"] == "meta-no-pick"]
    assert [x["sev"] for x in found("build")] == ["WARN", "WARN"]
    assert [x["sev"] for x in found("release")] == ["FAIL", "FAIL"]
    b["meta_set"]["pick"] = {"title": 0, "description": 0}
    b["approval"]["record_hash"] = PB.record_hash(b)
    assert found("release") == []


def test_gate_meta_length_reads_the_per_slug_ceiling(monkeypatch, tmp_path):
    budgets = tmp_path / "evidence-budgets.json"
    budgets.write_text(json.dumps({"title_max_chars": 40, "title_max_chars_by_slug": {"x": 70}}))
    monkeypatch.setattr(PB, "BUDGETS", budgets)
    assert PB.title_ceiling("x") == 70 and PB.title_ceiling("other") == 40
    b = _approved(MIN_BOARD)
    checks = lambda: {x["check"] for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")}
    assert "meta-length" not in checks()                 # ceiling 70 for slug "x"
    b["meta"]["slug"] = "other"; b["approval"]["record_hash"] = PB.record_hash(b)
    assert "meta-length" in checks()


def test_board_renders_the_meta_radio_groups_beside_the_h1():
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert 'data-title="2. H1 and meta"' in html
    assert 'name="meta-title"' in html and 'name="meta-description"' in html
    assert "meta-title" in html.split("Approve this board")[0]
    assert "meta:{title:" in html                        # Approve sends the pair


def test_approve_applies_the_meta_picks_and_refuses_an_index_off_the_menu():
    import board_approve as BA
    b = json.loads(json.dumps(MIN_BOARD))
    inbox = {"approved_at": "t", "h1": 0, "picks": {"puppies": "avail-b"}, "notes": {},
             "meta": {"title": 2, "description": 1}, "canvas_version": None, "record_hash": PB.record_hash(b)}
    out = BA.apply_approval(b, inbox, ONT_OK, LEDGER_EMPTY)
    assert out["board"]["meta_set"]["pick"] == {"title": 2, "description": 1}
    with pytest.raises(PB.BoardError):
        BA.apply_approval(json.loads(json.dumps(MIN_BOARD)), dict(inbox, meta={"title": 9, "description": 0}),
                          ONT_OK, LEDGER_EMPTY)


def test_meta_pick_index_below_zero_is_rejected():
    for field in ("title", "description"):
        bad = json.loads(json.dumps(MIN_BOARD))
        bad["meta_set"]["pick"][field] = -1
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)


def test_approve_js_refuses_an_unanswered_h1_or_meta_group():
    """The Approve handler's own guards, read out of the rendered page: a board where the
    breeder skipped the H1 or either meta group must refuse the write rather than send a
    record with a missing index in it."""
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    script = html.split("btn.addEventListener('click'", 1)[1]
    assert "input[name=\"h1\"]:checked" in script
    assert "if(!h1){st.textContent='Pick an H1 before approving.'" in script
    assert "input[name=\"meta-title\"]:checked" in script
    assert "input[name=\"meta-description\"]:checked" in script
    # Either group unanswered refuses — an OR, not an AND, so one skipped group is enough.
    assert "if(!mt||!mdsc){st.textContent='Pick a title and a description before approving.'" in script
    assert "btn.disabled=false;return;" in script



def test_angles_reject_one_entry_four_entries_a_duplicate_name_and_a_long_field():
    one = json.loads(json.dumps(MIN_BOARD)); one["brief"]["angles"] = one["brief"]["angles"][:1]
    four = json.loads(json.dumps(MIN_BOARD)); four["brief"]["angles"] += [
        {"name": "a", "hook": "h", "why_not": "w"}, {"name": "b", "hook": "h", "why_not": "w"}]
    dupe = json.loads(json.dumps(MIN_BOARD)); dupe["brief"]["angles"][1]["name"] = "n"
    long = json.loads(json.dumps(MIN_BOARD)); long["brief"]["angles"][1]["hook"] = "x" * 241
    for bad in (one, four, dupe, long):
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)


def test_angles_tie_to_the_strategy_and_a_rejected_one_must_say_why_not():
    off = json.loads(json.dumps(MIN_BOARD)); off["brief"]["strategy"]["name"] = "an angle nobody listed"
    with pytest.raises(PB.BoardError, match="not one of the angles"):
        PB.validate_board(off)
    silent = json.loads(json.dumps(MIN_BOARD)); silent["brief"]["angles"][1]["why_not"] = "   "
    with pytest.raises(PB.BoardError, match="records no why_not"):
        PB.validate_board(silent)
    PB.validate_board(MIN_BOARD)                  # the chosen angle's empty why_not is fine


def test_board_renders_the_angles_table_with_the_chosen_one_starred():
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "Angles considered" in html and "⭐ n" in html and "price-led" in html
    assert "trade-off: t" in html                 # the chosen row carries the strategy's trade-off
    assert "adoption-cost page" in html           # the rejected row carries its why_not


def _with_faq(questions):
    b = json.loads(json.dumps(MIN_BOARD))
    faq = json.loads(json.dumps(b["sections"][0]))
    faq.update({"id": "faq", "n": 2, "heading": "Questions Buyers Ask Us Before They Reserve",
                "shape": "standard", "tree": [], "images": [], "questions": questions,
                "options": {"candidates": [], "excluded": [], "pick": None, "note": ""}})
    b["sections"].append(faq)
    return b


EIGHT = [f"Question number {n} about buying a Blue Staffy?" for n in range(1, 9)]

# EIGHT's eight questions differ by one token in a position every 5-token window covers, so
# a live copy of the first collides with all eight. Fine for the schema tests; useless for
# counting collisions, which is what this second set is for.
DISTINCT = ["Where do our Blue Staffy puppies come from?",
            "When may a weaned chick travel home?",
            "Which airport handles the flight?",
            "Does the price include the folder?",
            "How long until a puppy settles in?",
            "Can we visit before we reserve?",
            "What happens if plans change?",
            "Is a deposit refundable?"]


def test_faq_questions_reject_seven_fifteen_a_duplicate_a_flat_line_and_an_absent_list():
    fifteen = [f"Question number {n} about buying a Blue Staffy?" for n in range(1, 16)]
    for bad in (EIGHT[:7], fifteen, EIGHT[:7] + [EIGHT[0]], EIGHT[:7] + ["A statement, not a question."]):
        with pytest.raises(PB.BoardError):
            PB.validate_board(_with_faq(bad))
    PB.validate_board(_with_faq(EIGHT))
    PB.validate_board(MIN_BOARD)                      # no faq section, nothing to enumerate
    bare = _with_faq(EIGHT); del bare["sections"][1]["questions"]
    with pytest.raises(PB.BoardError):
        PB.validate_board(bare)


def test_faq_questions_are_not_headings_but_are_listed_in_the_outline():
    import build_page_board as BPB
    b = _with_faq(EIGHT)
    assert EIGHT[0] not in [t for _, t in PB.all_headings(b)]
    assert PB.faq_questions(b) == EIGHT
    html = BPB.render(_approved(b), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "Q01 " + BPB.esc(EIGHT[0]) in html and "Q08 " in html


def test_gate_calls_a_colliding_faq_question_a_warn_not_a_fail():
    b = _approved(_with_faq(DISTINCT))
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY,
                         live={"/uk-locations/staffy-puppies-for-sale-glasgow/": [DISTINCT[0]]}, stage="build")
    hits = [x for x in f if x["check"] == "faq-collision"]
    assert len(hits) == 1 and hits[0]["sev"] == "WARN"
    assert not [x for x in f if x["check"] == "header-collision"]


def test_approve_leaves_the_faq_questions_alone():
    import board_approve as BA
    b = _with_faq(EIGHT)
    inbox = {"approved_at": "t", "h1": 0, "picks": {"puppies": "avail-b"}, "notes": {},
             "meta": {"title": 0, "description": 0}, "canvas_version": None, "record_hash": PB.record_hash(b)}
    out = BA.apply_approval(b, inbox, ONT_OK, LEDGER_EMPTY)
    assert out["board"]["sections"][1]["questions"] == EIGHT


def test_links_reject_a_relative_href_an_empty_anchor_and_a_url_outside_the_library(monkeypatch):
    # BSUK has no docs/reference/external-link-library.md yet (it arrives with the rules
    # port), and an absent library switches the membership rule off, so the test supplies
    # one holding exactly the fixture's own external href.
    monkeypatch.setattr(PB, "library_urls",
                        lambda *a, **k: frozenset({PB.normalise_url("https://www.gov.uk/guidance/dog-breeding-licence-england")}))
    rel = json.loads(json.dumps(MIN_BOARD))
    rel["sections"][0]["links"]["internal"][0]["href"] = "uk-locations/staffy-puppies-for-sale-glasgow/"
    blank = json.loads(json.dumps(MIN_BOARD))
    blank["sections"][0]["links"]["external"][0]["anchor"] = ""
    for bad in (rel, blank):
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)
    off = json.loads(json.dumps(MIN_BOARD))
    off["sections"][0]["links"]["external"][0]["href"] = "https://example.com/elsewhere"
    with pytest.raises(PB.BoardError, match="external-link-library"):
        PB.validate_board(off)


def test_gate_fails_on_a_duplicate_anchor_and_on_an_internal_href_with_no_built_page():
    b = _approved(MIN_BOARD)
    live = {"/x/": [], "/uk-locations/staffy-puppies-for-sale-glasgow/": []}
    hits = lambda check: [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
                          if x["check"] == check]
    assert hits("links-internal-dead") == [] and hits("links-anchor-duplicate") == []
    b["sections"][0]["links"]["internal"].append(
        {"href": "/a-page-that-was-never-built/#papers", "anchor": "our glasgow listings", "sentence_start": True})
    b["approval"]["record_hash"] = PB.record_hash(b)
    for check in ("links-anchor-duplicate", "links-internal-dead"):
        assert len(hits(check)) == 1 and hits(check)[0]["sev"] == "FAIL"


def _nav(board, section_links):
    b = json.loads(json.dumps(board))
    b["sections"][0]["links"]["internal"] = section_links
    return b


NAV_TILE = {"href": "/uk-locations/staffy-puppies-for-sale-leeds/", "anchor": "Leeds · Yorkshire", "nav": True}


def test_a_nav_anchor_needs_no_sentence_start_but_a_prose_anchor_still_does():
    PB.validate_board(_nav(MIN_BOARD, [NAV_TILE]))                      # no sentence_start, and none needed
    PB.validate_board(_nav(MIN_BOARD, [dict(NAV_TILE, nav=False, sentence_start=True)]))
    for bad in ([dict(NAV_TILE, nav=False)],                            # nav:false is prose: Link-First applies
                [{"href": "/uk-locations/staffy-puppies-for-sale-glasgow/", "anchor": "Our Glasgow listings"}],
                [dict(NAV_TILE, sentence_start=False)]):                # sentence_start is const true
        with pytest.raises(PB.BoardError):
            PB.validate_board(_nav(MIN_BOARD, bad))


def test_duplicate_anchors_skip_nav_lists_and_anchors_that_tokenise_to_nothing():
    live = {"/x/": [], "/uk-locations/staffy-puppies-for-sale-glasgow/": [], "/uk-locations/staffy-puppies-for-sale-leeds/": [],
            "/uk-locations/staffy-puppies-for-sale-hull/": []}
    dupes = lambda b: [x for x in PB.gate_findings(_approved(b), ONT_OK, LEDGER_EMPTY, live=live, stage="build")
                       if x["check"] == "links-anchor-duplicate"]
    # A grid repeats its own tiles by nature — chip row and map tile, one destination twice.
    assert dupes(_nav(MIN_BOARD, [NAV_TILE, dict(NAV_TILE, href="/uk-locations/staffy-puppies-for-sale-hull/"),
                                  dict(NAV_TILE)])) == []
    # And a nav tile is not a second use of the prose anchor that happens to read the same.
    assert dupes(_nav(MIN_BOARD, [{"href": "/uk-locations/staffy-puppies-for-sale-glasgow/", "anchor": "Our Glasgow listings",
                                   "sentence_start": True},
                                  {"href": "/uk-locations/staffy-puppies-for-sale-glasgow/", "anchor": "our glasgow listings",
                                   "nav": True}])) == []
    # Two prose anchors that tokenise to nothing are not "the same anchor twice".
    assert dupes(_nav(MIN_BOARD, [{"href": "/uk-locations/staffy-puppies-for-sale-glasgow/", "anchor": "—", "sentence_start": True},
                                  {"href": "/uk-locations/staffy-puppies-for-sale-leeds/", "anchor": "→",
                                   "sentence_start": True}])) == []
    # The real rule still fires on two prose uses of one anchor.
    assert len(dupes(_nav(MIN_BOARD, [{"href": "/uk-locations/staffy-puppies-for-sale-glasgow/", "anchor": "Our Glasgow listings",
                                       "sentence_start": True},
                                      {"href": "/uk-locations/staffy-puppies-for-sale-leeds/", "anchor": "our glasgow listings,",
                                       "sentence_start": True}]))) == 1


def test_library_urls_is_cached_but_notices_a_changed_library(tmp_path):
    lib = tmp_path / "external-link-library.md"
    lib.write_text("| `https://www.thekennelclub.org.uk/breed-standards/` |\n", encoding="utf-8")
    assert PB.library_urls(lib) == {"https://thekennelclub.org.uk/breed-standards"}
    assert PB.library_urls(lib) is PB.library_urls(lib)          # same object: read once, not per link
    lib.write_text("| `https://www.gov.uk/guidance/dog-breeding-licence-england` |\n", encoding="utf-8")
    import os
    os.utime(lib, (0, 0))                                        # a different mtime is a different library
    assert PB.library_urls(lib) == {"https://gov.uk/guidance/dog-breeding-licence-england"}


# --- Task 16: the kit strip --------------------------------------------------------------

def test_kit_strip_shows_every_axis_the_tuple_names_and_offers_nothing():
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert 'data-title="5b. The kit"' in html
    for shell in ("hero-a", "dial-1", "rail-a", "t1", "faq-a"):
        assert f'<div class="nothumb">{shell}</div>' in html
    assert 'name="pick-hero"' not in html and 'name="kit-' not in html
    b = _approved(MIN_BOARD)
    b["tuple"]["hero"] = "hero-a#inventory-tiles"
    ledger = {"pools": {"inventory": ["avail-b"]}, "refresh_pools": ["hero"],
              "pages": {"sibling": {"hero": "hero-a", "dial": "", "rail": "", "toc": "", "takeaway": [],
                                    "table": "", "faq": "", "h6_prefixes": []}}}
    html = BPB.render(b, ONT_OK, ledger, live={}, thumbs={}, slug="x")
    assert "refresh: inventory-tiles" in html and "also worn by sibling" in html
    assert "new to the cluster" in html            # the dial nobody else records


# --- Task 17: the image plan on the board --------------------------------------------------

def test_image_plan_lists_every_slot_with_its_prompt_and_flags_a_bare_signature_section():
    import build_page_board as BPB
    b = _approved(MIN_BOARD)
    html = BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert 'data-title="3b. Image plan"' in html
    block = html.split('data-title="3b. Image plan">', 1)[1].split("</script>", 1)[0]
    assert "puppies-opener" in html and "six puppy cards" in html and "| optional |" in block
    b["sections"][0]["images"] = []
    html = BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "**⚠ no image slot**" in html

    std = json.loads(json.dumps(b["sections"][0]))
    std.update({"id": "reserve", "n": 2, "shape": "standard", "images": [], "tree": []})
    b["sections"].append(std)
    html = BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    block = html.split('data-title="3b. Image plan">', 1)[1].split("</script>", 1)[0]
    assert "_no image slot_" in block


def test_gate_warns_on_a_signature_section_with_no_image_and_fails_on_a_shared_alt():
    b = _approved(MIN_BOARD)
    checks = lambda: [(x["check"], x["sev"]) for x in
                      PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")]
    assert ("image-coverage", "WARN") not in checks()
    assert ("asset-alt-duplicate", "FAIL") not in checks()
    reserve = json.loads(json.dumps(b["sections"][0]))
    reserve.update({"id": "reserve", "n": 2, "shape": "standard", "images": [], "tree": []})
    b["sections"].append(reserve)
    assert ("image-coverage", "WARN") not in checks()          # a standard section is exempt
    b["sections"][0]["images"] = []
    assert ("image-coverage", "WARN") in checks()
    b["assets"] = [dict(b["assets"][0], alt="A blue Staffy pup on the grass"),
                   dict(b["assets"][0], slot="card-01", alt="a blue staffy pup on the grass.")]
    assert ("asset-alt-duplicate", "FAIL") in checks()

    b["assets"] = [dict(b["assets"][0], slot="hero", alt="A blue Staffy pup on the grass"),
                   dict(b["assets"][0], slot="card-01", alt=""),
                   dict(b["assets"][0], slot="card-02", alt="A brindle Staffy pup on the scale")]
    assert ("asset-alt-duplicate", "FAIL") not in checks()

    a0 = b["assets"][0]
    b["assets"] = [dict(a0, slot="hero", alt="Staffy!"),
                   dict(a0, slot="card-01", alt="staffy"),
                   dict(a0, slot="card-02", alt="STAFFY.")]
    findings = [x for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage="build")
                if x["check"] == "asset-alt-duplicate"]
    assert len(findings) == 1
    assert "hero, card-01, card-02" in findings[0]["msg"]


def test_section_why_is_required_c_is_always_ours_and_competitor_names_a_url():
    for mutate in (lambda s: s.pop("why"), lambda s: s.update(why="too short"),
                   lambda s: s.update(group="OPTIONAL"), lambda s: s.pop("group"),
                   lambda s: s.update(why_source=""), lambda s: s.update(why="w" * 401)):
        bad = json.loads(json.dumps(MIN_BOARD)); mutate(bad["sections"][0])
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)
    bad = json.loads(json.dumps(MIN_BOARD)); bad["sections"][0]["category"] = "C"
    with pytest.raises(PB.BoardError, match="SUGGESTED-RECOMMENDED"):
        PB.validate_board(bad)
    bad = json.loads(json.dumps(MIN_BOARD)); bad["sections"][0]["group"] = "COMPETITOR-BASED"
    with pytest.raises(PB.BoardError, match="URL"):
        PB.validate_board(bad)
    bad = json.loads(json.dumps(MIN_BOARD))
    bad["sections"][0].update(group="COMPETITOR-BASED", why_source="no https:// found")
    with pytest.raises(PB.BoardError, match="URL"):
        PB.validate_board(bad)
    ok = json.loads(json.dumps(MIN_BOARD))
    ok["sections"][0].update(group="COMPETITOR-BASED",
                             why_source="https://www.champdogs.co.uk/breeds/staffordshire-bull-terrier (ranks first with a grid)")
    PB.validate_board(ok)


def test_distribution_block_shows_group_and_grounded_why():
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "**Why each section is here**" in html
    assert "reads as a directory, not a breeder." in html and "for-sale-keywords-2026-07.md" in html
    assert "[A · mandatory · inventory" in html                  # the outline line carries the group

    competitor = json.loads(json.dumps(MIN_BOARD))
    competitor["sections"][0].update(group="COMPETITOR-BASED",
                                     why_source="https://example.com/foo_bar (a note)")
    html2 = BPB.render(_approved(competitor), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "· competitor ·" in html2
    assert "<https://example.com/foo_bar>" in html2

    ours = json.loads(json.dumps(MIN_BOARD))
    ours["sections"][0]["category"] = "C"
    ours["sections"][0]["group"] = "SUGGESTED-RECOMMENDED"
    html3 = BPB.render(_approved(ours), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "[C · ours ·" in html3


def test_keywords_carry_the_briefs_eight_types_plus_geo():
    import build_page_board as BPB
    bad = json.loads(json.dumps(MIN_BOARD)); del bad["sections"][0]["keywords"]["transactional"]
    with pytest.raises(PB.BoardError):
        PB.validate_board(bad)
    b = json.loads(json.dumps(MIN_BOARD))
    b["sections"][0]["keywords"]["transactional"] = ["reserve a blue staffy", "blue staffy deposit"]
    PB.validate_board(b)
    assert PB.distribution(b)["totals"]["transactional"] == 2
    html = BPB.render(_approved(b), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "| Section | Primary | LSI | Long-tail | Brand | Geo | Voice | Compare | Solution | Transact | Words |" in html


def test_keyword_types_tuple_labels_and_schema_name_the_same_arrays():
    """The schema keeps its own copy of the names; this pins it to PB.KEYWORD_TYPES, so a type
    added in one place and not the other fails here instead of silently vanishing from the board
    (schema only) or raising KeyError in distribution() (tuple only)."""
    schema = json.loads((PB.SCHEMAS / "board.schema.json").read_text(encoding="utf-8"))
    kw = schema["properties"]["sections"]["items"]["properties"]["keywords"]
    assert kw["required"] == list(PB.KEYWORD_TYPES)
    assert set(kw["properties"]) == set(PB.KEYWORD_TYPES)
    assert set(PB.KEYWORD_LABELS) == set(PB.KEYWORD_TYPES)
    for typ in PB.KEYWORD_TYPES:
        b = json.loads(json.dumps(MIN_BOARD))
        b["sections"][0]["keywords"][typ] = ["one", "two"]
        assert PB.distribution(b)["totals"][typ] == 2
    bad = json.loads(json.dumps(MIN_BOARD)); bad["sections"][0]["keywords"]["voice"] = []
    with pytest.raises(PB.BoardError):
        PB.validate_board(bad)


# --- Task 20: the whole tuple on the kit strip ------------------------------------------

def test_tuple_newsletter_names_a_real_section_and_sets_both_fields_together():
    for nl in ({"after": "puppies", "variant": ""}, {"after": "", "variant": "A"},
               {"after": "shipping", "variant": "A"}, {"after": "puppies", "variant": "D"}):
        bad = json.loads(json.dumps(MIN_BOARD)); bad["tuple"]["newsletter"] = nl
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)
    ok = json.loads(json.dumps(MIN_BOARD)); ok["tuple"]["newsletter"] = {"after": "puppies", "variant": "B"}
    PB.validate_board(ok)

    bad_takeaway = json.loads(json.dumps(MIN_BOARD)); bad_takeaway["tuple"]["takeaway"] = ["k1", ""]
    with pytest.raises(PB.BoardError):
        PB.validate_board(bad_takeaway)


def test_kit_strip_shows_takeaway_table_stepper_and_the_newsletter():
    import build_page_board as BPB
    b = _approved(MIN_BOARD)
    b["tuple"].update(takeaway=["k1", "k2"], newsletter={"after": "puppies", "variant": "B"})
    html = BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    for shell in ("table-a", "k1", "k2"):
        assert f'<div class="nothumb">{shell}</div>' in html
    assert "this page wears no stepper" in html
    assert "after 01 · Our Blue Staffy Puppies" in html and "variant B" in html

    # the newsletter card itself carries both fields, not just the page somewhere
    start = html.index('<span class="pill">newsletter</span>')
    stops = [i for i in (html.find("</div></div>", start), html.find('<div class="opt', start + 1)) if i != -1]
    card = html[start:min(stops)]
    assert "variant B" in card and "after 01 · Our Blue Staffy Puppies" in card

    b["tuple"]["newsletter"] = {"after": "", "variant": ""}
    assert "this page places no newsletter" in BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")

    # a stepper is not a ledger-tracked axis, so ownership is unknowable, not "new"
    b2 = _approved(MIN_BOARD)
    b2["tuple"]["stepper"] = "t5-stepper"
    html2 = BPB.render(b2, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "not tracked by the component ledger yet" in html2
    assert '<div class="nothumb">t5-stepper</div>' in html2

    # a tracked axis (table) still says who else wears it
    b3 = _approved(MIN_BOARD)
    html3 = BPB.render(b3, ONT_OK, _ledger_with(table="table-a"), live={}, thumbs={}, slug="x")
    assert "also worn by sibling" in html3

    # render() is called on unvalidated dicts in tests, so it needs its own guard for a
    # newsletter.after that names no real section
    b4 = _approved(MIN_BOARD)
    b4["tuple"]["newsletter"] = {"after": "shipping", "variant": "A"}
    with pytest.raises(PB.BoardError):
        BPB.render(b4, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")


# --- Task 21: the CTA plan -------------------------------------------------------------------

def test_cta_plan_validates_cadence_destination_and_needs_one_cta():
    for mutate in (lambda b: b["sections"][0].update(cta=0),
                   lambda b: b["brief"]["cta"]["cadence"].update(min=800),
                   lambda b: b["brief"]["cta"].update(destination="reserve"),
                   lambda b: b["brief"]["cta"].update(anchors=[])):
        bad = json.loads(json.dumps(MIN_BOARD)); mutate(bad)
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)


def test_gate_warns_on_thin_cta_cadence_and_a_long_cta_free_run():
    b = json.loads(json.dumps(MIN_BOARD))
    assert PB.cta_findings(b) == []                            # one CTA in ~500 words
    ship = json.loads(json.dumps(b["sections"][0]))
    ship.update({"id": "shipping", "n": 2, "words": {"min": 700, "max": 900}, "cta": 0, "tree": []})
    b["sections"].append(ship)
    found = dict(PB.cta_findings(b))
    assert set(found) == {"cta-cadence", "cta-gap"}            # ~1300 words on one CTA; shipping runs ~800 bare
    assert "shipping" in found["cta-gap"]
    f = [x for x in PB.gate_findings(_approved(b), ONT_OK, LEDGER_EMPTY, live={}, stage="build")
         if x["check"].startswith("cta-")]
    assert sorted((x["check"], x["sev"]) for x in f) == [("cta-cadence", "WARN"), ("cta-gap", "WARN")]


def test_board_renders_the_cta_plan_and_marks_cta_sections():
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "**CTA plan.** One every 500–700 words" in html and "Reserve This Puppy" in html
    assert "hidden on this page" in html and "400–600w · CTA×1]" in html


def test_cta_gap_runs_break_at_each_cta_section_and_counts_move_the_cadence():
    b = json.loads(json.dumps(MIN_BOARD))
    def add(sid, n, lo, hi, cta):
        s = json.loads(json.dumps(b["sections"][0]))
        s.update({"id": sid, "n": n, "words": {"min": lo, "max": hi}, "cta": cta, "tree": []})
        b["sections"].append(s)
    b["sections"][0]["cta"] = 0                      # birds ~500, no CTA
    add("a", 2, 400, 600, 0)                         # run puppies+a = ~1000 -> gap
    add("b", 3, 400, 600, 1)                         # CTA closes it
    add("c", 4, 700, 900, 0)                         # run c = ~800 -> second gap (trailing)
    gaps = [m for c, m in PB.cta_findings(b) if c == "cta-gap"]
    assert len(gaps) == 2
    assert "sections puppies, a run ~1000 words" in gaps[0]
    assert "sections c run ~800 words" in gaps[1]
    assert ("cta-cadence" in dict(PB.cta_findings(b)))                                  # 2300 / 1 CTA
    b["sections"][2]["cta"] = 4                                                        # 2300 / 4 = 575
    assert "cta-cadence" not in dict(PB.cta_findings(b))

    # a long CTA-carrying section reports no gap on its own (it still trips cta-cadence,
    # 2000/1 > 700 — that is not asserted away here)
    single = json.loads(json.dumps(MIN_BOARD))
    single["sections"][0]["words"] = {"min": 1900, "max": 2100}
    single["sections"][0]["cta"] = 1
    assert [c for c, _ in PB.cta_findings(single) if c == "cta-gap"] == []


# --- Task 22: the tool decision ---------------------------------------------------------------

def test_tool_decision_requires_evidence_and_a_trade_off_for_a_real_tool():
    for mutate in (lambda t: t.update(evidence="none seen"),
                   lambda t: t.update(pick="first-year cost calculator", trade_off=""),
                   lambda t: t.pop("pick")):
        bad = json.loads(json.dumps(MIN_BOARD)); mutate(bad["brief"]["tool"])
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)
    ok = json.loads(json.dumps(MIN_BOARD))
    ok["brief"]["tool"].update(pick="first-year cost calculator", trade_off="adds JS to a page that ships none today")
    PB.validate_board(ok)


def test_board_renders_the_tool_decision():
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "**Tool.** none — evidence: No top-10 result for the head term" in html
    assert "Trade-off:" not in html

    picked = json.loads(json.dumps(MIN_BOARD))
    picked["brief"]["tool"].update(pick="first-year cost calculator",
                                   evidence="No top-10 result for the head term ships a calculator or quiz.",
                                   trade_off="adds JS to a page that ships none today")
    html2 = BPB.render(_approved(picked), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "Trade-off: adds JS to a page that ships none today" in html2


def test_schema_plan_ties_offer_model_to_its_types():
    for sch in ({"types": ["AggregateOffer"], "offer_model": "product-offer-per-puppy"},
                {"types": ["Offer", "FAQPage"], "offer_model": "none"},
                {"types": ["FAQPage"], "offer_model": "aggregate-offer"},
                {"types": ["faqpage"], "offer_model": "none"}):
        bad = json.loads(json.dumps(MIN_BOARD)); bad["brief"]["schema"] = sch
        with pytest.raises(PB.BoardError):
            PB.validate_board(bad)
    ok = json.loads(json.dumps(MIN_BOARD))
    ok["brief"]["schema"] = {"types": ["Product", "Offer", "FAQPage"], "offer_model": "product-offer-per-puppy"}
    PB.validate_board(ok)


def test_release_gate_reads_json_ld_from_the_built_page(tmp_path, monkeypatch):
    page = tmp_path / "x" / "index.html"
    page.parent.mkdir()
    page.write_text('<script type="application/ld+json">{"@graph":[{"@type":"Product","offers":{"@type":"AggregateOffer"}}]}</script>'
                    '<script type="application/ld+json">{broken</script>', encoding="utf-8")
    monkeypatch.setattr(PB, "DIST", tmp_path)
    assert PB.dist_schema_types("x") == ({"Product", "AggregateOffer"}, 1)
    b = _approved(MIN_BOARD)
    schema_rows = lambda stage: sorted((x["check"], x["msg"].split(" ")[0]) for x in
                                       PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live={}, stage=stage)
                                       if x["check"].startswith("schema-"))
    assert schema_rows("build") == []
    assert schema_rows("release") == [("schema-planned-missing", "FAQPage"), ("schema-unparsed", "1")]
    monkeypatch.setattr(PB, "DIST", tmp_path / "nowhere")
    assert [c for c, _ in schema_rows("release")] == ["schema-examined-zero"]

    # quote/param variants, schema.org URL and schema: prefixed types, non-string @type ignored
    ypage = tmp_path / "y" / "index.html"
    ypage.parent.mkdir()
    ypage.write_text(
        "<script type='application/ld+json'>{\"@type\": \"https://schema.org/FAQPage\"}</script>"
        '<script type="application/ld+json; charset=utf-8">{"@type": ["schema:Product", 5]}</script>'
        '<script type="application/ld+json">{"@type": 7}</script>',
        encoding="utf-8")
    assert PB.dist_schema_types("y", dist=tmp_path) == ({"FAQPage", "Product"}, 0)

    # the index slug reads <dist>/index.html directly
    (tmp_path / "index.html").write_text(
        '<script type="application/ld+json">{"@type": "WebSite"}</script>', encoding="utf-8")
    assert PB.dist_schema_types("index", dist=tmp_path) == ({"WebSite"}, 0)

    # all planned types present on the built page -> no schema-* release findings
    x2page = tmp_path / "x2" / "index.html"
    x2page.parent.mkdir()
    x2page.write_text(
        '<script type="application/ld+json">'
        '{"@graph": [{"@type": "AggregateOffer"}, {"@type": "FAQPage"}]}</script>',
        encoding="utf-8")
    monkeypatch.setattr(PB, "DIST", tmp_path)
    b2 = json.loads(json.dumps(b)); b2["meta"]["slug"] = "x2"
    findings2 = PB.gate_findings(b2, ONT_OK, LEDGER_EMPTY, live={}, stage="release")
    assert [x for x in findings2 if x["check"].startswith("schema-")] == []


def test_board_renders_the_schema_plan():
    import build_page_board as BPB
    html = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "**Schema plan.** offer model aggregate-offer; types: AggregateOffer, FAQPage." in html


# --- perf records at release (2026-09-13) ------------------------------------------------
# A page is not released on board picks alone: PageSpeed must read 100 in all five
# categories. Local records gate the release; the PSI record (only possible after deploy)
# is pending until measured and FAILS the next release once it reads under 100.


def _perf(tmp_path, name, **kw):
    rec = {"failed": [], "edge_blocking": [], "dist_mtime": 2000.0, "measured_at": "2026-09-13T20:00:00+00:00",
           "median": {c: 1 for c in ("performance", "accessibility", "best-practices", "seo", "agentic-browsing")}}
    rec.update(kw)
    (tmp_path / f"{name}.json").write_text(json.dumps(rec))


def _page(tmp_path, mtime=1000.0):
    import os
    p = tmp_path / "index.html"
    p.write_text("<html></html>")
    os.utime(p, (mtime, mtime))
    return p


def _perf_checks(found):
    return sorted((x["check"], x["sev"]) for x in found)


def test_perf_silent_at_build_stage(tmp_path):
    assert PB.perf_findings("s", "build", perf_dir=tmp_path, dist_page=_page(tmp_path)) == []


def test_perf_missing_local_records_fail_release(tmp_path):
    found = PB.perf_findings("s", "release", perf_dir=tmp_path, dist_page=_page(tmp_path))
    assert ("perf-record-missing", "FAIL") in _perf_checks(found)
    assert sum(1 for x in found if x["check"] == "perf-record-missing") == 2   # mobile and desktop


def test_perf_clean_local_records_leave_only_psi_pending(tmp_path):
    _perf(tmp_path, "s--desktop"); _perf(tmp_path, "s--mobile")
    assert _perf_checks(PB.perf_findings("s", "release", perf_dir=tmp_path, dist_page=_page(tmp_path))) == [
        ("perf-psi-pending", "WARN"), ("perf-psi-pending", "WARN")]


def test_perf_local_record_older_than_the_build_is_stale(tmp_path):
    _perf(tmp_path, "s--desktop", dist_mtime=500.0); _perf(tmp_path, "s--mobile")
    assert ("perf-record-stale", "FAIL") in _perf_checks(PB.perf_findings("s", "release", perf_dir=tmp_path, dist_page=_page(tmp_path)))


def test_perf_local_category_under_100_fails(tmp_path):
    _perf(tmp_path, "s--desktop", failed=["accessibility"]); _perf(tmp_path, "s--mobile")
    msgs = [x["msg"] for x in PB.perf_findings("s", "release", perf_dir=tmp_path, dist_page=_page(tmp_path))
            if x["check"] == "perf-below-100"]
    assert len(msgs) == 1 and "accessibility" in msgs[0]


def test_perf_local_mobile_performance_is_not_judged_hardware_bound(tmp_path):
    # This Mac's CPU cannot stand in for PSI's; mobile Performance is judged by the PSI record.
    _perf(tmp_path, "s--desktop"); _perf(tmp_path, "s--mobile", failed=["performance"])
    assert not [x for x in PB.perf_findings("s", "release", perf_dir=tmp_path, dist_page=_page(tmp_path))
                if x["check"] == "perf-below-100"]


def test_perf_failing_psi_record_fails_release(tmp_path):
    _perf(tmp_path, "s--desktop"); _perf(tmp_path, "s--mobile")
    _perf(tmp_path, "s--mobile--psi", failed=["performance"], median={"performance": 0.77})
    _perf(tmp_path, "s--desktop--psi")
    assert _perf_checks(PB.perf_findings("s", "release", perf_dir=tmp_path, dist_page=_page(tmp_path))) == [
        ("perf-psi-below-100", "FAIL")]


def test_perf_edge_injected_script_fails_release(tmp_path):
    _perf(tmp_path, "s--desktop"); _perf(tmp_path, "s--mobile")
    _perf(tmp_path, "s--mobile--psi", edge_blocking=["https://example-host.test/70de/"])
    _perf(tmp_path, "s--desktop--psi")
    assert ("perf-edge-injected", "FAIL") in _perf_checks(PB.perf_findings("s", "release", perf_dir=tmp_path, dist_page=_page(tmp_path)))


def test_perf_psi_record_older_than_local_record_is_pending_again(tmp_path):
    _perf(tmp_path, "s--desktop", measured_at="2026-09-14T00:00:00+00:00"); _perf(tmp_path, "s--mobile")
    _perf(tmp_path, "s--desktop--psi", measured_at="2026-09-13T00:00:00+00:00")
    _perf(tmp_path, "s--mobile--psi")
    assert _perf_checks(PB.perf_findings("s", "release", perf_dir=tmp_path, dist_page=_page(tmp_path))) == [
        ("perf-psi-pending", "WARN")]



def test_ontology_file_validates_and_marks_the_unconfirmed_guarantee_proposed():
    """data/settings.json has guarantee_days: null (Foundation, unconfirmed). An ontology
    that ASSERTED a guarantee would let a page publish a number nobody has given."""
    ont = PB.load_ontology()
    by_id = {e["id"]: e for e in ont["entities"]}
    assert by_id["ont:health-guarantee"]["authorization"] == "PROPOSED"
    assert by_id["ont:health-guarantee"]["source"] is None


def test_every_asserted_entity_names_a_source_that_exists():
    for e in PB.load_ontology()["entities"]:
        if e["authorization"] == "ASSERTED":
            assert e["source"], e["id"]
            assert (PB.ROOT / e["source"]).exists(), (e["id"], e["source"])


# --- quality pass: nested slugs, slug validation, token round trip, empty-ledger banner ---

def test_a_nested_slug_flattens_to_one_board_file():
    assert PB.slug_file("uk-locations/glasgow") == "uk-locations--glasgow"
    assert PB.board_path("uk-locations/glasgow") == PB.ROOT / "data" / "boards" / "uk-locations--glasgow.json"
    assert PB.board_path("available-puppies/roman").name == "available-puppies--roman.json"
    assert PB.slug_file("index") == "index"


def test_the_schema_accepts_a_nested_slug():
    """BSUK routes nest (`available-puppies/roman`); CAG's did not, and its `^[a-z0-9-]+$`
    made the flattening in board_path unreachable."""
    b = json.loads(json.dumps(MIN_BOARD))
    b["meta"]["slug"] = "available-puppies/roman"
    PB.validate_board(b)


def test_a_slug_segment_may_not_carry_the_flattening_separator():
    """`a--b` and `a/b` would otherwise name the same file, so the flattening would not be
    reversible and two records could silently overwrite each other."""
    with pytest.raises(PB.BoardError, match="--"):
        PB.slug_file("a--b")
    with pytest.raises(PB.BoardError, match="--"):
        PB.board_path("uk-locations--glasgow")
    bad = json.loads(json.dumps(MIN_BOARD))
    bad["meta"]["slug"] = "a--b"
    with pytest.raises(PB.BoardError):
        PB.save_board("a--b", bad)


@pytest.mark.parametrize("slug", ["../x", "/abs", "a//b", "a/", "/", "", "Upper", "..", "a b", "a/../b"])
def test_board_path_refuses_a_slug_that_is_not_a_slug(slug):
    """A path built from an unvalidated slug reads a file the caller never named."""
    with pytest.raises(PB.BoardError, match="slug"):
        PB.board_path(slug)


def test_board_gate_cli_exits_2_on_a_traversal_slug_without_reading_a_file():
    import subprocess
    r = subprocess.run([sys.executable, str(PB.ROOT / "scripts" / "board_gate.py"), "../../etc"],
                       capture_output=True, text=True)
    assert r.returncode == 2
    assert "board-gate ERROR" in r.stdout and "slug" in r.stdout
    assert "does not exist" not in r.stdout          # refused before any file was looked for


def test_unfile_token_round_trips_an_id_without_an_underscore():
    for cid in ("toc-a", "hero-c-mosaic-metrics", "toc-t1-numbered-ledger#state-chips"):
        assert PB.unfile_token(PB.file_token(cid)) == cid
    # Documented one-way limit: an id that already spells `_` cannot come back.
    assert PB.unfile_token(PB.file_token("toc_a")) == "toc#a"


def test_board_gate_says_so_when_the_ledger_is_empty(tmp_path, monkeypatch, capsys):
    """Until project 3 the component ledger has no pages, so the five ledger-* checks
    examine nothing. A gate that examines nothing is not a pass."""
    import board_gate
    b = _approved(MIN_BOARD)
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(PB, "load_board", lambda slug: b)
    monkeypatch.setattr(PB, "load_ontology", lambda: ONT_OK)
    monkeypatch.setattr(PB, "load_ledger", lambda: {"refresh_pools": [], "pools": {}, "pages": {}})
    monkeypatch.setattr(sys, "argv", ["board_gate.py", "x"])
    with pytest.raises(SystemExit):
        board_gate.main()
    assert "ledger: empty — ledger-* families examined 0, not a pass" in capsys.readouterr().out


def test_board_gate_says_nothing_about_an_empty_ledger_when_it_has_pages(tmp_path, monkeypatch, capsys):
    import board_gate
    b = _approved(MIN_BOARD)
    ledger = {"refresh_pools": [], "pools": {"hero": ["hero-a"]},
              "pages": {"sibling": {"hero": "hero-a", "dial": "", "rail": "", "toc": "",
                                    "takeaway": [], "table": "", "faq": "", "h6_prefixes": []}}}
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(PB, "load_board", lambda slug: b)
    monkeypatch.setattr(PB, "load_ontology", lambda: ONT_OK)
    monkeypatch.setattr(PB, "load_ledger", lambda: ledger)
    monkeypatch.setattr(sys, "argv", ["board_gate.py", "x"])
    with pytest.raises(SystemExit):
        board_gate.main()
    assert "ledger: empty" not in capsys.readouterr().out


def test_board_approve_cli_exits_2_on_a_traversal_slug():
    import subprocess
    r = subprocess.run([sys.executable, str(PB.ROOT / "scripts" / "board_approve.py"), "../../etc"],
                       capture_output=True, text=True)
    assert r.returncode == 2
    assert "board-approve ERROR" in r.stdout and "slug" in r.stdout
    assert "no approval at" not in r.stdout


def test_puppy_card_headings_are_matched_exactly_not_as_a_sub_run():
    """The substring trap, one layer down: the CONSUMER of the whitelist.

    `roman` is a puppy-card heading — a card whose H3 is exactly the puppy's name may repeat
    wherever the card renders. Matching it as a contiguous token sub-run exempted every board
    heading that merely contains the word ("Roman Roads of Glasgow"), which is the same
    failure the dup gate's own header whitelist had. Card headings match exactly; only the
    phrase list keeps sub-run behaviour, and it holds no single common words.
    """
    assert PB._whitelisted("Roman")
    assert PB._whitelisted("roman")          # normalised
    assert not PB._whitelisted("Roman Roads of Glasgow")
    assert not PB._whitelisted("Meet Roman, Byrd and Ince")
    # the phrase list is unaffected
    assert PB._whitelisted("Frequently Asked Questions")


def test_gate_still_fails_a_collision_that_merely_contains_a_puppy_name():
    b = _approved(MIN_BOARD)
    b["sections"][0]["tree"][0]["heading"] = "Roman Roads of Glasgow and Our Puppies"
    b["approval"]["record_hash"] = PB.record_hash(b)
    live = {"/sibling/": ["Roman Roads of Glasgow and Our Puppies"]}
    msgs = [x["msg"] for x in PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
            if x["check"] == "header-collision"]
    assert any("Roman Roads" in m for m in msgs), msgs
