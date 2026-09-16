# tests/py/test_final_page_audit.py
#
# Ported from CAG tests/test_final_page_audit.py (Task 6). The fixtures are rewritten
# as BSUK puppy pages: GBP delivery band, BSUK nouns, no US credential tokens.
#
# Tests dropped in the port, each with its reason:
#   - test_bird_pbfd_claim_fails       — the no_pbfd_claim check is deleted (plan step 6);
#                                        the disease it named has no BSUK analogue.
#   - test_pbfd_denial_does_not_falsely_fail — same, the check it guards is gone.
#   - test_house_method_named_passes   — the house_method check is deleted (plan step 8,
#                                        spec §7 drops CAG's rule 12, brand-owned method
#                                        labels).
#   - test_airport_codes_warn_on_interior — the airport_codes check is deleted (plan
#                                        step 9); BSUK delivers by road.
# Tests added by the port: the exit code (plan step 2.13), repo-rooted DIST, the
# argparse profile choices, the JSON report shape, and the migration-baseline count.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import final_page_audit as A


def test_nested_slug_resolves_to_available_puppies_path():
    # available-puppies/roman must map to dist/available-puppies/roman/index.html
    p = A.dist_path("available-puppies/roman")
    assert str(p).endswith("dist/available-puppies/roman/index.html"), p


def test_flat_slug_resolves_unchanged():
    p = A.dist_path("buy-blue-staffy-puppies-uk")
    assert str(p).endswith("dist/buy-blue-staffy-puppies-uk/index.html"), p


# Canonical clean-puppy fixture: passes ALL puppy hard gates (no_aggregateoffer,
# shipping_line, sold_not_instock). Tests that depend on a passing puppy page use this
# fixture. Do NOT modify it without checking all tests that reference it.
MINIMAL_PUPPY = """
<html><head><title>Roman — Blue Staffy Puppy for Sale | BlueStaffyUK</title>
<link rel="canonical" href="https://SITE_URL_PLACEHOLDER/available-puppies/roman/">
<meta name="description" content="Roman, our home-raised blue Staffy puppy, £1,500.">
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Product","name":"Roman","offers":{"@type":"Offer","availability":"https://schema.org/InStock"}},{"@type":"Organization","name":"BlueStaffyUK"},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://SITE_URL_PLACEHOLDER/"},{"@type":"ListItem","position":2,"name":"Available Puppies","item":"https://SITE_URL_PLACEHOLDER/available-puppies/"},{"@type":"ListItem","position":3,"name":"Roman"}]}]}</script>
</head><body><main><h1>Roman</h1><h2>About Roman</h2><h3>Health</h3><h4>Delivery</h4>
<h5>Collection in Glasgow</h5><h6>What to Bring</h6>
<h5>Home Delivery</h5><h6>Door-to-Door Timing</h6>
<h5>Deposit</h5><h6>What the Deposit Holds</h6>
<h5>Weaning Status</h5><h6>Feeding Schedule</h6>
<h5>Documentation Folder</h5><h6>Microchip Numbers</h6>
<p>UK delivery &middot; £200 to £350 by distance. KC registered, DEFRA-approved transport, microchipped and vet checked. Lifespan 12-14 years.</p>
</main><footer>0141 496 0000</footer></body></html>
"""


def test_profile_marks_newsletter_na_for_puppy():
    r = A.audit_html("available-puppies/roman", MINIMAL_PUPPY, "puppy")
    assert r["_severity"]["newsletter_present"] == "NA", r["_severity"]


def test_profile_marks_newsletter_fail_for_interior():
    r = A.audit_html("uk-blue-staffy-puppy-buying-guide", MINIMAL_PUPPY, "interior")
    assert r["_severity"]["newsletter_present"] in ("FAIL", "WARN"), r["_severity"]


BAD_PUPPY = """
<html><head><title>Bad — BlueStaffyUK</title></head><body><main><h1>X</h1>
<script type="application/ld+json">{"@type":"AggregateOffer"}</script>
<p>This puppy has no delivery band on the page.</p>
</main></body></html>
"""


def test_puppy_aggregateoffer_fails():
    r = A.audit_html("available-puppies/x", BAD_PUPPY, "puppy")
    assert r["no_aggregateoffer"] is False
    assert r["_severity"]["no_aggregateoffer"] == "FAIL"


def test_good_puppy_passes_hard_gates():
    r = A.audit_html("available-puppies/roman", MINIMAL_PUPPY, "puppy")
    assert r["no_aggregateoffer"] is True
    assert r["shipping_line"] is True


SOLD_PUPPY_STILL_INSTOCK = """
<html><head><title>Old — BlueStaffyUK</title></head><body><main><h1>X</h1>
<script type="application/ld+json">{"@type":"Product","offers":{"@type":"Offer","availability":"https://schema.org/InStock"}}</script>
<p>This puppy is sold. Status: Sold.</p></main></body></html>
"""


def test_sold_but_instock_fails():
    r = A.audit_html("available-puppies/x", SOLD_PUPPY_STILL_INSTOCK, "puppy")
    assert r["sold_not_instock"] is False


def test_sold_together_phrase_does_not_falsely_fail():
    html = MINIMAL_PUPPY.replace("Lifespan 12-14 years.",
                                 "These two are sold together as a bonded pair. Lifespan 12-14 years.")
    r = A.audit_html("available-puppies/vennie", html, "puppy")
    assert r["sold_not_instock"] is True


def test_missing_delivery_line_fails():
    html = MINIMAL_PUPPY.replace("UK delivery &middot; £200 to £350 by distance. ", "")
    r = A.audit_html("available-puppies/x", html, "puppy")
    assert r["shipping_line"] is False


def test_delivery_band_written_as_a_range_passes():
    """£200–£350 is how the band reads in prose; the regex must accept both shapes."""
    html = MINIMAL_PUPPY.replace("£200 to £350 by distance", "£200–£350 by distance")
    r = A.audit_html("available-puppies/x", html, "puppy")
    assert r["shipping_line"] is True


def test_placeholder_hero_warns():
    html = "<html><head><title>x</title></head><body><main><h1>x</h1><img src='/img/placeholder.jpg'></main></body></html>"
    r = A.audit_html("available-puppies/x", html, "puppy")
    assert r["real_hero_image"] is False


def test_verdict_fail_when_hard_gate_breaks():
    r = A.audit_html("available-puppies/x", BAD_PUPPY, "puppy")
    assert r["_verdict"] == "FAIL", r["_verdict"]


def test_verdict_not_fail_for_clean_puppy():
    r = A.audit_html("available-puppies/roman", MINIMAL_PUPPY, "puppy")
    assert r["_verdict"] in ("PASS", "PASS-WITH-WARNINGS"), r["_verdict"]


def test_credentials_and_lifespan_read_uk_tokens():
    r = A.audit_html("available-puppies/roman", MINIMAL_PUPPY, "puppy")
    assert r["cites_credentials_early"] is True
    assert r["lifespan_12_14"] is True


def test_sold_not_instock_explicit_fail_on_puppy():
    # Guards the EXPLICIT declaration, not the DEFAULT_SEVERITY fallback —
    # this fails if someone deletes the puppy-profile entry.
    assert "sold_not_instock" in A.PROFILES.get("puppy", {}), \
        "sold_not_instock must be explicitly declared in the puppy profile"
    assert A.PROFILES["puppy"]["sold_not_instock"] == "FAIL"


def test_home_and_location_profiles_downgrade_h5_h6_minimums_to_warn():
    for pt in ("home", "location"):
        assert A.severity(pt, "min_h5_5") == "WARN", pt
        assert A.severity(pt, "min_h6_5") == "WARN", pt
        assert A.severity(pt, "no_skip") == "FAIL", pt   # skipped levels stay a hard FAIL


def test_home_profile_marks_breadcrumb_not_applicable():
    # The root page has no trail — a missing BreadcrumbList on "/" is not a defect.
    assert A.severity("home", "has_breadcrumb") != "FAIL", A.severity("home", "has_breadcrumb")


def test_slug_and_puppy_lists_are_read_from_data_not_retyped():
    """A hand-typed list drifts the first time a page is added."""
    assert "buy-blue-staffy-puppies-uk" in A.SLUGS, A.SLUGS
    assert "available-puppies/roman" in A.PUPPIES, A.PUPPIES
    assert A.COMPARISONS == []   # project 5 writes the cluster


def _build_dist(tmp_path, pages):
    """Write {slug: html} into a tmp dist/ and point the script at it."""
    dist = tmp_path / "dist"
    for slug, html in pages.items():
        d = dist if slug == "index" else dist / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")
    return dist


def test_main_exits_one_when_a_page_fails(tmp_path, monkeypatch, capsys):
    """CAG's final_page_audit could not fail. Spec §11: this gate exits 1 on FAIL."""
    dist = _build_dist(tmp_path, {"available-puppies/roman": BAD_PUPPY})
    monkeypatch.setattr(A, "DIST", dist)
    rc = A.main(["available-puppies/roman", "--type", "puppy"])
    assert rc == 1, capsys.readouterr().out


def test_main_exits_zero_when_every_page_passes(tmp_path, monkeypatch, capsys):
    dist = _build_dist(tmp_path, {"available-puppies/roman": MINIMAL_PUPPY})
    monkeypatch.setattr(A, "DIST", dist)
    rc = A.main(["available-puppies/roman", "--type", "puppy"])
    assert rc == 0, capsys.readouterr().out


def test_dist_is_resolved_from_the_repo_root_not_the_cwd(tmp_path, monkeypatch):
    """A gate that only works when you happen to be standing in the repo root is a
    trap; DIST hangs off ROOT."""
    assert A.DIST == A.ROOT / "dist"
    monkeypatch.chdir(tmp_path)
    assert str(A.dist_path("available-puppies/roman")).startswith(str(A.ROOT))


def test_dist_path_uses_the_shared_slug_resolution():
    import _slugs
    assert A.dist_path("index") == _slugs.dist_path("index", A.DIST)
    assert A.dist_path("available-puppies/roman") == _slugs.dist_path(
        "available-puppies/roman", A.DIST)


def test_type_flag_rejects_a_profile_that_does_not_exist(tmp_path, monkeypatch):
    """argparse `choices` — a typo used to be accepted and silently scored against
    DEFAULT_SEVERITY."""
    import pytest
    monkeypatch.setattr(A, "DIST", tmp_path / "dist")
    with pytest.raises(SystemExit):
        A.main(["index", "--type", "parakeet"])


BASELINE_ONLY_PUPPY = MINIMAL_PUPPY.replace(
    "<h5>Documentation Folder</h5><h6>Microchip Numbers</h6>", "")


def test_baseline_only_failures_are_counted_and_tagged(tmp_path, monkeypatch, capsys):
    """The three heading-outline checks fail on every migrated page. A page failing
    ONLY those is the migration baseline, not a regression, and must be countable."""
    dist = _build_dist(tmp_path, {"available-puppies/roman": BASELINE_ONLY_PUPPY})
    monkeypatch.setattr(A, "DIST", dist)
    rc = A.main(["available-puppies/roman", "--type", "puppy"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "[migration baseline]" in out, out
    assert "baseline-only FAIL pages: 1" in out, out


def test_a_real_regression_is_not_counted_as_baseline(tmp_path, monkeypatch, capsys):
    dist = _build_dist(tmp_path, {"available-puppies/roman": BAD_PUPPY})
    monkeypatch.setattr(A, "DIST", dist)
    A.main(["available-puppies/roman", "--type", "puppy"])
    out = capsys.readouterr().out
    assert "baseline-only FAIL pages: 0" in out, out


def test_json_report_shape(tmp_path, monkeypatch):
    import json as _j
    dist = _build_dist(tmp_path, {"available-puppies/roman": BAD_PUPPY})
    monkeypatch.setattr(A, "DIST", dist)
    out = tmp_path / "final_page_audit.json"
    A.main(["available-puppies/roman", "--type", "puppy", "--json", str(out)])
    doc = _j.loads(out.read_text())
    page = doc["pages"][0]
    assert page["slug"] == "available-puppies/roman"
    assert page["status"] == "FAIL"
    entry = page["checks"][0]
    assert set(entry) == {"check", "severity", "message"}
    assert entry["severity"] in ("FAIL", "WARN")
    assert all(c["severity"] in ("FAIL", "WARN") for c in page["checks"])


def test_forsale_list_is_the_single_source_of_the_transactional_slugs():
    assert not hasattr(A, "TRANSACTIONAL")
    assert "buy-blue-staffy-puppies-uk" in A.FORSALE
    assert len(A.FORSALE) == 3


# --- no_aggregateoffer: an aggregate a Product owns is not a stray (harness fix 2026-09-12) ---
# A hub listing carries exactly the shape Google wants for a group: one Product whose
# `offers` is an AggregateOffer, plus an ItemList of per-puppy Product+Offer. The checker
# only asked whether the string "AggregateOffer" appeared anywhere in the flattened types.
HUB_GRAPH_AGGREGATE = """
<html><head><title>Blue Staffy Puppies for Sale | BlueStaffyUK</title></head><body><main><h1>Blue Staffies</h1>
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[
{"@type":"Product","name":"Blue Staffy Puppy","offers":{"@type":"AggregateOffer","lowPrice":"1500","highPrice":"1700","offerCount":"6","priceCurrency":"GBP"}},
{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":1,"item":{"@type":"Product","name":"Roman","offers":{"@type":"Offer","price":"1500"}}}]},
{"@type":"Organization","name":"BlueStaffyUK"}]}</script>
<p>UK delivery: £200 to £350 by distance.</p></main></body></html>
"""

STRAY_AGGREGATE = """
<html><head><title>Stray | BlueStaffyUK</title></head><body><main><h1>Stray</h1>
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[
{"@type":"Product","name":"One Puppy","offers":{"@type":"Offer","price":"1500"}},
{"@type":"AggregateOffer","lowPrice":"1500","highPrice":"1700"}]}</script>
<p>UK delivery: £200 to £350 by distance.</p></main></body></html>
"""


def test_for_sale_hub_product_carrying_aggregateoffer_is_not_flagged():
    r = A.audit_html("buy-blue-staffy-puppies-uk", HUB_GRAPH_AGGREGATE, "for-sale")
    assert "AggregateOffer" in r["schema_types"]          # it IS on the page
    assert r["no_aggregateoffer"] is True                  # and it is not a defect there


def test_for_sale_stray_aggregateoffer_is_still_flagged():
    """An aggregate that belongs to no Product is a price claim nothing on the page owns."""
    r = A.audit_html("blue-staffy-pup-sale-uk", STRAY_AGGREGATE, "for-sale")
    assert r["no_aggregateoffer"] is False


def test_puppy_page_product_carrying_aggregateoffer_still_fails():
    """A single-puppy listing never aggregates, however well-formed the shape is: the FAIL
    the puppy profile raises is not weakened by the hub fix."""
    r = A.audit_html("available-puppies/x", HUB_GRAPH_AGGREGATE, "puppy")
    assert r["no_aggregateoffer"] is False
    assert r["_severity"]["no_aggregateoffer"] == "FAIL"


def test_single_product_offer_page_passes_on_both_profiles():
    for pt in ("puppy", "for-sale"):
        assert A.audit_html("available-puppies/roman", MINIMAL_PUPPY, pt)["no_aggregateoffer"] is True, pt
