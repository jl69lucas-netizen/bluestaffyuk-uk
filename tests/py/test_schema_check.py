"""Gate tests for scripts/schema_check.py."""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

from schema_check import audit_html, main  # noqa: E402

GOOD = ('<script type="application/ld+json">{"@type":"LocalBusiness","name":"x"}</script>'
        '<script type="application/ld+json">{"@type":"Product","offers":'
        '{"@type":"Offer","availability":"https://schema.org/InStock"}}</script>')


def test_audit_ok():
    r = audit_html(GOOD, available_slugs={"roman"}, slug="available-puppies/roman")
    assert r["parsed"] == 2 and r["blocking"] == [] and r["advisory"] == []


def test_audit_flags_bad_json_phone_and_false_instock():
    bad = ('<script type="application/ld+json">{oops}</script>'
           '<script type="application/ld+json">{"@type":"LocalBusiness",'
           '"telephone":"PHONE_PLACEHOLDER"}</script>'
           '<script type="application/ld+json">{"@type":"Offer",'
           '"availability":"https://schema.org/InStock"}</script>')
    r = audit_html(bad, available_slugs=set(), slug="x")
    b = " ".join(r["blocking"])
    assert "parse" in b and "telephone" in b and "InStock" in b
    # Exactly three: the unparseable block, the placeholder phone, the false InStock.
    assert len(r["blocking"]) == 3


def test_duplicate_sitewide_types_are_advisory():
    dup = ('<script type="application/ld+json">{"@type":"WebSite"}</script>'
           '<script type="application/ld+json">{"@graph":[{"@type":"WebSite"}]}</script>')
    r = audit_html(dup, available_slugs=set(), slug="x")
    assert r["blocking"] == [] and any("WebSite" in a for a in r["advisory"])


def test_dangling_ids_are_blocking():
    d = ('<script type="application/ld+json">{"@graph":[{"@type":"WebPage",'
         '"@id":"/#webpage","isPartOf":{"@id":"/#website"}}]}</script>')
    r = audit_html(d, available_slugs=set(), slug="x")
    assert any("dangling" in b for b in r["blocking"])


def test_resolved_reference_is_not_dangling():
    ok = ('<script type="application/ld+json">{"@graph":[{"@type":"WebPage",'
          '"@id":"/#webpage","name":"Home","isPartOf":{"@id":"/#website"}},'
          '{"@type":"WebSite","@id":"/#website","name":"s"}]}</script>')
    r = audit_html(ok, available_slugs=set(), slug="x")
    assert r["blocking"] == []


def test_product_without_offers_and_half_priced_offer_are_blocking():
    t = ('<script type="application/ld+json">{"@type":"Product","name":"p"}</script>'
         '<script type="application/ld+json">{"@type":"Offer","price":1500}</script>')
    r = audit_html(t, available_slugs=set(), slug="x")
    b = " ".join(r["blocking"])
    assert "offers" in b and "priceCurrency" in b
    assert len(r["blocking"]) == 2


@pytest.mark.parametrize("pup", ["byrd", "ince"])
def test_pup_page_absent_from_available_slugs_may_not_claim_instock(pup):
    # A pup whose data/puppies.json status is not Available is simply missing from
    # available_slugs, so the page set is what encodes availability.
    sold = ('<script type="application/ld+json">{"@type":"Product","offers":'
            '{"@type":"Offer","availability":"https://schema.org/InStock",'
            '"price":1500,"priceCurrency":"GBP"}}</script>')
    r = audit_html(sold, available_slugs={"roman"}, slug="available-puppies/%s" % pup)
    assert len(r["blocking"]) == 1 and "InStock" in r["blocking"][0]


def test_advisory_empty_url_and_nameless_webpage():
    a = ('<script type="application/ld+json">{"@type":"WebPage","@id":"/#w",'
         '"url":""}</script>')
    r = audit_html(a, available_slugs=set(), slug="x")
    joined = " ".join(r["advisory"])
    assert "url" in joined and "name" in joined


def _write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_main_fixture_fails_and_names_the_page(tmp_path):
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "puppies.json",
           json.dumps([{"slug": "roman", "status": "Available"}]))
    _write(dist / "index.html",
           '<script type="application/ld+json">{"@type":"LocalBusiness","name":"x"}</script>')
    _write(dist / "blog" / "index.html",
           '<script type="application/ld+json">{"@graph":[{"@type":"WebPage",'
           '"@id":"/blog/#webpage","name":"Blog","isPartOf":{"@id":"/#website"}}]}</script>')
    with pytest.raises(SystemExit) as exc:
        main(root=root, dist=dist)
    assert exc.value.code == 1
    report = (root / "docs" / "reports" / "schema.md").read_text(encoding="utf-8")
    assert "/blog/" in report and "dangling" in report


def test_main_fixture_passes_when_clean(tmp_path):
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "puppies.json",
           json.dumps([{"slug": "roman", "status": "Available"}]))
    _write(dist / "index.html",
           '<script type="application/ld+json">{"@type":"LocalBusiness","name":"x"}</script>')
    main(root=root, dist=dist)   # no SystemExit
    assert (root / "docs" / "reports" / "schema.md").is_file()


def test_nested_product_and_webpage_are_checked():
    # A Product hung off mainEntity reaches Google exactly like a top-level one.
    nested = ('<script type="application/ld+json">{"@type":"CollectionPage",'
              '"name":"Pups","mainEntity":[{"@type":"Product","name":"p"},'
              '{"@type":"WebPage","@id":"/#w","name":"named"},'
              '{"@type":"WebPage","@id":"/#x","url":"/x/"}]}</script>')
    r = audit_html(nested, available_slugs=set(), slug="x")
    assert r["blocking"] == ["Product without offers"]
    assert r["advisory"] == ["WebPage without name"]


def test_prose_mention_of_instock_is_advisory_not_blocking():
    prose = ('<script type="application/ld+json">{"@type":"FAQPage","mainEntity":'
             '[{"@type":"Question","name":"q","acceptedAnswer":{"@type":"Answer",'
             '"text":"We mark pups https://schema.org/InStock when reserved."}}]}</script>')
    r = audit_html(prose, available_slugs=set(), slug="x")
    assert r["blocking"] == []
    assert any("outside any Offer" in a for a in r["advisory"])


def test_typed_stub_reference_to_a_dropped_node_is_blocking():
    # Rank Math writes {"@type": T, "@id": X}; a dedupe that drops X leaves the stub, and
    # the stub must not be mistaken for a definition of X.
    stub = ('<script type="application/ld+json">{"@graph":[{"@type":"WebPage",'
            '"@id":"/#webpage","name":"Home","publisher":{"@id":"/#business"}},'
            '{"@type":"Organization","@id":"/#business"}]}</script>')
    r = audit_html(stub, available_slugs=set(), slug="x")
    assert r["blocking"] == ["dangling @id reference: /#business"]


def test_list_valued_availability_claiming_instock_is_blocking():
    # `"availability": ["https://schema.org/InStock"]` is the shape Rank Math emits for a
    # multi-availability offer. The blocking test used to require a str, and
    # _strip_availability removed the key before the prose scan, so this page claimed
    # InStock on a non-pup URL and the gate reported nothing at all.
    listed = ('<script type="application/ld+json">{"@type":"Product","name":"p",'
              '"offers":{"@type":"Offer","availability":'
              '["https://schema.org/InStock"]}}</script>')
    r = audit_html(listed, available_slugs={"roman"}, slug="uk-locations/birmingham")
    assert len(r["blocking"]) == 1
    assert "InStock claimed on a page that is not an available puppy" in r["blocking"][0]


def test_list_valued_availability_is_allowed_on_an_available_pup():
    listed = ('<script type="application/ld+json">{"@type":"Product","name":"p",'
              '"offers":{"@type":"Offer","availability":'
              '["https://schema.org/InStock"]}}</script>')
    r = audit_html(listed, available_slugs={"roman"}, slug="available-puppies/roman")
    assert r["blocking"] == []
