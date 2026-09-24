"""System-gaps Task 2: the ontology grows two classes (Organization, Regulation) and is
seeded from the repo's own sourced data only — locations, the external link library, the
evidence ledger and settings. Every health test stays PROPOSED until the ledger proves it."""
import copy
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import ontology_seed as OS  # noqa: E402
import pageboard as PB      # noqa: E402

EXISTING = {"entities": [
    {"id": "ont:lisa-bright", "name": "Lisa Bright", "aliases": ["the breeder"], "class": "People",
     "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "blue-staffy-uk-breeders"},
    {"id": "ont:glasgow", "name": "Glasgow", "aliases": [], "class": "Place",
     "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "custom-owner"},
]}
LOCATIONS = [{"slug": "blue-staffy-puppies-leeds", "city": "Leeds"},
             {"slug": "staffy-breeding-dogs-glasgow", "city": "Glasgow (breeding dogs)"},
             {"slug": "blue-staffy-puppies-uk", "city": "UK"},
             {"slug": "blue-staffy-puppies-for-sale-leeds", "city": "Leeds"}]
SETTINGS = {"breeder_name": "Lisa Bright", "address": {"city": "Carlisle", "region": "Cumbria", "country": "GB"}}
ROWS = [("https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy", "rspca.org.uk", "RSPCA advice", "blue-staffy-uk-breeders"),
        ("https://www.gov.uk/control-dog-public/banned-dogs", "gov.uk", "banned dogs", "uk-staffordshire-bull-terrier-guide"),
        ("https://www.gov.uk/get-your-dog-cat-microchipped", "gov.uk", "microchipping", "blue-staffy-health-uk"),
        ("https://www.gov.uk/data-protection", "gov.uk", "data protection", "privacy-policy-uk"),
        ("https://www.gov.uk/bring-pet-to-great-britain", "gov.uk", "pet travel", "thank-you-blue-staffy-puppies-journey"),
        ("https://assets.publishing.service.gov.uk/media/5a819d3bed915d74e623335d/pb10308-dogs-cats-welfare-060215.pdf",
         "assets.publishing.service.gov.uk", "PB10308", "buy-blue-staffy-puppies-uk"),
        ("https://crufts.org.uk/", "crufts.org.uk", "Crufts", "blue-staffy-uk-breeders")]
EMPTY_LEDGER = {"_comment": "…", "claims": []}


def _seed(existing=EXISTING, ledger=EMPTY_LEDGER, rows=ROWS):
    return OS.seeded(copy.deepcopy(existing), LOCATIONS, SETTINGS, ledger, rows)


def _by_id(ont):
    return {e["id"]: e for e in ont["entities"]}


def test_the_schema_knows_the_two_new_classes():
    schema = json.loads((PB.SCHEMAS / "ontology.schema.json").read_text(encoding="utf-8"))
    classes = schema["properties"]["entities"]["items"]["properties"]["class"]["enum"]
    assert {"Organization", "Regulation"} <= set(classes)
    assert set(OS.CLASS_ORDER) == set(classes)


def test_existing_entities_are_kept_byte_for_byte_and_first():
    ont = _seed()
    assert ont["entities"][:2] == EXISTING["entities"]
    assert _by_id(ont)["ont:glasgow"]["owner_page"] == "custom-owner"


def test_places_come_from_locations_and_settings():
    by = _by_id(_seed())
    assert by["ont:leeds"]["owner_page"] == "uk-locations/blue-staffy-puppies-leeds"   # first row wins
    assert by["ont:leeds"]["source"] == "data/locations.json"
    assert "ont:uk" not in by                                                         # the country rows
    assert by["ont:carlisle"]["source"] == "data/settings.json"
    assert by["ont:cumbria"]["class"] == "Place"


def test_organisations_and_regulations_come_from_library_rows():
    by = _by_id(_seed())
    assert by["ont:rspca"]["class"] == "Organization"
    assert by["ont:uk-government"]["class"] == "Organization"         # gov.uk and its asset host: one
    assert by["ont:dangerous-dogs-act-1991"]["class"] == "Regulation"
    assert by["ont:welfare-in-transport-pb10308"]["class"] == "Regulation"
    assert "ont:crufts" not in by                                     # an event, skipped on purpose
    for e in by.values():
        if e["class"] in ("Organization", "Regulation"):
            assert e["source"] == "docs/reference/external-link-library.md" and e["owner_page"] is None


def test_an_unmapped_library_host_stops_the_seed():
    with pytest.raises(PB.BoardError, match="HOST_ORG"):
        _seed(rows=ROWS + [("https://example.org/x", "example.org", "?", "index")])


def test_health_tests_stay_proposed_with_no_source_while_the_ledger_is_empty():
    by = _by_id(_seed())
    tests = [e for e in by.values() if e["class"] == "Health"]
    assert len(tests) == len(OS.HEALTH_TESTS)
    for e in tests:
        assert e["authorization"] == "PROPOSED" and e["source"] is None, e["id"]


def test_a_not_fetched_ledger_row_does_not_assert_a_test():
    ledger = {"claims": [{"id": "l2hga", "pattern": r"L-?2-?HGA", "proof": "NOT FETCHED",
                          "anchor": "dna-tests", "confirmed": "2026-09-24"}]}
    assert _by_id(_seed(ledger=ledger))["ont:l-2-hga-dna-test"]["authorization"] == "PROPOSED"
    ledger["claims"][0].update({"proof": "/docs/l2hga-cert.pdf", "confirmed": None})
    assert _by_id(_seed(ledger=ledger))["ont:l-2-hga-dna-test"]["authorization"] == "PROPOSED"


def test_a_proved_and_confirmed_ledger_row_asserts_that_test_only():
    ledger = {"claims": [{"id": "l2hga", "pattern": r"L-?2-?HGA", "proof": "/docs/l2hga-cert.pdf",
                          "anchor": "dna-tests", "confirmed": "2026-09-24"}]}
    by = _by_id(_seed(ledger=ledger))
    assert by["ont:l-2-hga-dna-test"]["authorization"] == "ASSERTED"
    assert by["ont:l-2-hga-dna-test"]["source"] == "data/quality/evidence-ledger.json"
    assert by["ont:hc-hsf4-dna-test"]["authorization"] == "PROPOSED"


def test_seeding_is_idempotent():
    once = _seed()
    assert _seed(existing=once) == once


def test_every_health_test_is_named_by_the_ledger_or_the_library():
    """No test is invented: each one's wording is in the ledger's own comment or a library row."""
    text = (json.dumps(PB._read_json(OS.LEDGER)) + PB.EXTERNAL_LIBRARY.read_text(encoding="utf-8")).lower()
    named_by = {"ont:l-2-hga-dna-test": "l-2-hga", "ont:hc-hsf4-dna-test": "hc-hsf4", "ont:phpv-test": "phpv",
                "ont:bva-kc-eye-scheme": "eye scheme", "ont:bva-hip-elbow-scores": "bva hip/elbow"}
    assert set(named_by) == {t[0] for t in OS.HEALTH_TESTS}
    for eid, words in named_by.items():
        assert words in text, (eid, words)


def test_every_organisation_name_or_alias_is_in_the_library_text():
    text = PB.EXTERNAL_LIBRARY.read_text(encoding="utf-8").lower()
    for _host, (_eid, name, aliases) in OS.HOST_ORG.items():
        assert any(f.lower() in text for f in [name] + aliases), name


# --- the real file ----------------------------------------------------------------------

def test_the_committed_ontology_is_exactly_what_a_seed_run_writes():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "ontology_seed.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_the_committed_ontology_counts_by_class():
    ont = PB.load_ontology()
    counts = {c: sum(e["class"] == c for e in ont["entities"]) for c in OS.CLASS_ORDER}
    assert counts["People"] >= 1 and counts["Place"] >= 25
    assert counts["Organization"] >= 9 and counts["Regulation"] >= 5 and counts["Health"] >= 6
    assert not [e["id"] for e in ont["entities"]
                if e["class"] == "Health" and e["authorization"] == "ASSERTED"
                and not PB._read_json(OS.LEDGER)["claims"]]


# --- no street address, and every source names what it sources (system-gaps, Glasgow fix) ---

# A UK postcode (full, or the outward half on its own) or a street-type word. Known Issue 55:
# the former business street address must not survive anywhere as data a page can reach.
_POSTCODE = r"^[A-Z]{1,2}\d[A-Z\d]?(\s*\d[A-Z]{2})?$"
_STREET = r"\b(street|st|road|rd|lane|ln|avenue|ave|drive|dr|close|crescent|terrace|way|place|court)\b\.?$"


def test_no_ontology_entity_carries_a_street_or_postcode_alias():
    import re
    bad = [(e["id"], a) for e in PB.load_ontology()["entities"] for a in [e["name"], *e["aliases"]]
           if re.match(_POSTCODE, a.strip(), re.I) or re.search(_STREET, a.strip(), re.I)]
    assert bad == []


def test_every_sourced_entity_is_named_by_its_source_file():
    """A `source` is the file that says the entity exists: its name or one of its aliases
    appears in that file's text (JSON is read decoded, so an escaped character still matches)."""
    texts, missing = {}, []
    for e in PB.load_ontology()["entities"]:
        src = e["source"]
        if not src or not (ROOT / src).is_file():
            continue
        if src not in texts:
            raw = (ROOT / src).read_text(encoding="utf-8")
            texts[src] = (json.dumps(json.loads(raw), ensure_ascii=False) if src.endswith(".json") else raw).lower()
        if not any(f.lower() in texts[src] for f in [e["name"], *e["aliases"]]):
            missing.append((e["id"], src))
    assert missing == []


def test_glasgow_is_sourced_to_its_location_row_and_owned_by_a_real_route():
    g = {e["id"]: e for e in PB.load_ontology()["entities"]}["ont:glasgow"]
    rows = PB._read_json(OS.LOCATIONS)
    assert g["source"] == "data/locations.json" and any(r["city"] == "Glasgow" for r in rows)
    assert g["aliases"] == []
    assert any(r["canonical"] == f"/{g['owner_page']}/" for r in rows)
