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
LOCATIONS = [{"slug": s, "city": c, "canonical": f"/uk-locations/{s}/"} for s, c in (
             ("blue-staffy-puppies-leeds", "Leeds"),
             ("staffy-breeding-dogs-glasgow", "Glasgow (breeding dogs)"),
             ("blue-staffy-puppies-uk", "UK"),
             ("blue-staffy-puppies-for-sale-leeds", "Leeds"))]
SETTINGS = {"breeder_name": "Lisa Bright", "address": {"city": "Carlisle", "region": "Cumbria", "country": "GB"}}
ROWS = [("https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy", "rspca.org.uk", "RSPCA advice", "blue-staffy-uk-breeders"),
        ("https://www.gov.uk/control-dog-public/banned-dogs", "gov.uk", "banned dogs", "uk-staffordshire-bull-terrier-guide"),
        ("https://www.gov.uk/get-your-dog-cat-microchipped", "gov.uk", "microchipping", "blue-staffy-health-uk"),
        ("https://www.gov.uk/data-protection", "gov.uk", "data protection", "privacy-policy-uk"),
        ("https://www.gov.uk/bring-pet-to-great-britain", "gov.uk", "pet travel", "thank-you-blue-staffy-puppies-journey"),
        ("https://assets.publishing.service.gov.uk/media/5a819d3bed915d74e623335d/pb10308-dogs-cats-welfare-060215.pdf",
         "assets.publishing.service.gov.uk", "PB10308", "buy-blue-staffy-puppies-uk"),
        ("https://crufts.org.uk/", "crufts.org.uk", "Crufts", "blue-staffy-uk-breeders"),
        ("https://www.legislation.gov.uk/uksi/2018/486/contents/made", "legislation.gov.uk",
         "The Animal Welfare (Licensing of Activities Involving Animals) (England) Regulations 2018", "index"),
        ("https://www.legislation.gov.uk/uksi/2015/108/contents/made", "legislation.gov.uk",
         "The Microchipping of Dogs (England) Regulations 2015", "index")]
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
    ledger = PB._read_json(OS.LEDGER)
    health = [e for e in ont["entities"] if e["class"] == "Health"]
    if not ledger["claims"]:
        assert all(e["authorization"] != "ASSERTED" for e in health)


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


# --- review fixes: one certificate proves one test, proved tests upgrade, no duplicate ids ---

PROVED = {"proof": "/docs/cert.pdf", "anchor": "dna-tests", "confirmed": "2026-09-24"}


def test_a_claim_whose_pattern_matches_two_tests_stops_the_seed():
    ledger = {"claims": [{"id": "dna", "pattern": "DNA test", **PROVED}]}
    with pytest.raises(PB.BoardError, match=r"'dna'.*L-2-HGA DNA test.*HC-HSF4 DNA test"):
        _seed(ledger=ledger)


def test_a_specific_claim_asserts_its_own_test_and_no_other():
    ledger = {"claims": [{"id": "phpv", "pattern": r"\bPHPV\b", **PROVED}]}
    health = [e for e in _seed(ledger=ledger)["entities"] if e["class"] == "Health"]
    assert [e["id"] for e in health if e["authorization"] == "ASSERTED"] == ["ont:phpv-test"]


def test_a_committed_proposed_health_test_upgrades_once_the_ledger_proves_it():
    committed = _seed()                                        # the test is already in the file, PROPOSED
    ids = [e["id"] for e in committed["entities"]]
    ledger = {"claims": [{"id": "l2hga", "pattern": r"L-?2-?HGA", **PROVED}]}
    after = _seed(existing=committed, ledger=ledger)
    assert [e["id"] for e in after["entities"]] == ids         # upgraded in place, nothing appended
    t = _by_id(after)["ont:l-2-hga-dna-test"]
    assert (t["authorization"], t["source"]) == ("ASSERTED", "data/quality/evidence-ledger.json")
    before = _by_id(committed)
    changed = [e["id"] for e in after["entities"] if e != before[e["id"]]]
    assert changed == ["ont:l-2-hga-dna-test"]


def test_nothing_but_a_proposed_sourceless_seeded_health_test_is_ever_rewritten():
    committed = _seed()
    by = _by_id(committed)
    by["ont:l-2-hga-dna-test"]["source"] = "data/some-other.json"      # has a source: left alone
    by["ont:hc-hsf4-dna-test"]["authorization"] = "BLOCKED"            # not PROPOSED: left alone
    committed["entities"].append({"id": "ont:health-guarantee", "name": "Health guarantee", "aliases": [],
                                  "class": "Health", "authorization": "PROPOSED", "source": None,
                                  "owner_page": None})                 # not a HEALTH_TESTS id
    ledger = {"claims": [{"id": "l2hga", "pattern": r"L-?2-?HGA", **PROVED},
                         {"id": "hc", "pattern": r"HC-HSF4", **PROVED},
                         {"id": "hg", "pattern": r"^Health guarantee$", **PROVED}]}
    assert _seed(existing=committed, ledger=ledger) == committed


def test_a_generated_id_in_two_classes_stops_the_seed():
    settings = dict(SETTINGS, breeder_name="Leeds")          # a People and a Place both ont:leeds
    with pytest.raises(PB.BoardError, match=r"ont:leeds.*(People.*Place|Place.*People)"):
        OS.seeded(copy.deepcopy(EXISTING), LOCATIONS, settings, EMPTY_LEDGER, ROWS)


def test_a_new_id_already_in_the_file_under_another_class_stops_the_seed():
    existing = copy.deepcopy(EXISTING)
    existing["entities"].append({"id": "ont:leeds", "name": "Leeds", "aliases": [], "class": "Organism",
                                 "authorization": "ASSERTED", "source": None, "owner_page": None})
    with pytest.raises(PB.BoardError, match=r"ont:leeds.*(Organism.*Place|Place.*Organism)"):
        _seed(existing=existing)


def test_a_fresh_seed_owns_glasgow_where_the_committed_file_does():
    locations = PB._read_json(OS.LOCATIONS)
    fresh = _by_id(OS.seeded({"entities": []}, locations, SETTINGS, EMPTY_LEDGER, ROWS))
    committed = {e["id"]: e for e in PB.load_ontology()["entities"]}
    assert fresh["ont:glasgow"]["owner_page"] == committed["ont:glasgow"]["owner_page"]
    for e in fresh.values():                                  # every place owner is its row's canonical
        if e["source"] == "data/locations.json":
            assert any(r["canonical"].strip("/") == e["owner_page"] for r in locations), e["id"]


def test_a_parenthetical_row_yields_to_a_plain_one_for_the_owner():
    rows = [{"slug": "a", "city": "Glasgow (breeding dogs)", "canonical": "/uk-locations/a/"},
            {"slug": "b", "city": "Glasgow", "canonical": "/uk-locations/b/"}]
    fresh = _by_id(OS.seeded({"entities": []}, rows, SETTINGS, EMPTY_LEDGER, ROWS))
    assert fresh["ont:glasgow"]["owner_page"] == "uk-locations/b"


@pytest.mark.parametrize("missing", ["slug", "canonical", "city"])
def test_a_location_row_missing_a_field_stops_the_seed(missing):
    row = {"slug": "blue-staffy-puppies-hull", "city": "Hull", "canonical": "/uk-locations/blue-staffy-puppies-hull/"}
    del row[missing]
    with pytest.raises(PB.BoardError, match=missing):
        OS.seeded({"entities": []}, [row], SETTINGS, EMPTY_LEDGER, ROWS)


def test_slug_id_folds_accents_and_refuses_an_empty_slug():
    assert OS.slug_id("Bôrth-y-Gêst") == "ont:borth-y-gest"
    with pytest.raises(PB.BoardError, match="cannot slug"):
        OS.slug_id("——")


@pytest.mark.parametrize("name", ["LOCATIONS", "SETTINGS", "LEDGER"])
def test_a_missing_input_file_is_a_board_error(monkeypatch, tmp_path, name):
    monkeypatch.setattr(OS, name, tmp_path / "absent.json")
    with pytest.raises(PB.BoardError, match="absent.json"):
        OS.main(["--check"])


# --- Task 4's starter rows: the two legislation.gov.uk laws are Regulation entities ---------

LICENSING_2018 = "The Animal Welfare (Licensing of Activities Involving Animals) (England) Regulations 2018"
MICROCHIP_2015 = "Microchipping of Dogs (England) Regulations 2015"


def test_the_two_legislation_rows_seed_regulations():
    by = _by_id(_seed())
    reg = by["ont:animal-licensing-regulations-2018"]
    assert (reg["name"], reg["class"], reg["authorization"], reg["source"], reg["owner_page"]) == (
        LICENSING_2018, "Regulation", "ASSERTED", "docs/reference/external-link-library.md", None)
    assert MICROCHIP_2015 in by["ont:dog-microchipping-law"]["aliases"]   # folded, not a second law
    assert "ont:microchipping-of-dogs-england-regulations-2015" not in by
    assert by["ont:uk-government"]["class"] == "Organization"            # the host stays the government


def test_the_committed_ontology_carries_both_laws():
    by = {e["id"]: e for e in PB.load_ontology()["entities"]}
    assert by["ont:animal-licensing-regulations-2018"]["name"] == LICENSING_2018
    assert by["ont:animal-licensing-regulations-2018"]["source"] == "docs/reference/external-link-library.md"
    assert MICROCHIP_2015 in by["ont:dog-microchipping-law"]["aliases"]
    text = PB.EXTERNAL_LIBRARY.read_text(encoding="utf-8")
    assert LICENSING_2018 in text and MICROCHIP_2015 in text           # both named in the row's own words


# --- library_rows reads the Rows table by its header row; HOST_ORG constants ----------------

LIB_HEADER = ("| URL | Host | What it is | First page using it | Verified | Source type |\n"
              "|---|---|---|---|---|---|\n")


def test_a_mixed_width_library_table_stops_the_seed(tmp_path):
    p = tmp_path / "lib.md"
    p.write_text("# lib\n\n" + LIB_HEADER
                 + "| https://www.rspca.org.uk/a | rspca.org.uk | RSPCA advice | `/` | 2026-09-24 · 200 | welfare |\n"
                 + "| https://www.pdsa.org.uk/b | pdsa.org.uk | PDSA advice | `/` | 2026-09-24 · 200 |\n",
                 encoding="utf-8")
    with pytest.raises(PB.BoardError, match=r"line 6 has 5 cells.*header has 6"):
        OS.library_rows(p)


def test_an_extra_column_is_read_by_its_header_name(tmp_path):
    p = tmp_path / "lib.md"
    p.write_text("| URL | Notes | Host | What it is | First page using it | Verified | Source type |\n"
                 "|---|---|---|---|---|---|---|\n"
                 "| https://www.rspca.org.uk/a | a note | rspca.org.uk | RSPCA advice | `/blue-staffy-health-uk/` "
                 "| 2026-09-24 · 200 | welfare |\n", encoding="utf-8")
    assert OS.library_rows(p) == [
        ("https://www.rspca.org.uk/a", "rspca.org.uk", "RSPCA advice", "blue-staffy-health-uk")]


def test_a_header_without_a_needed_column_stops_the_seed(tmp_path):
    p = tmp_path / "lib.md"
    p.write_text("| URL | What it is | First page using it |\n|---|---|---|\n"
                 "| https://www.rspca.org.uk/a | RSPCA advice | `/` |\n", encoding="utf-8")
    with pytest.raises(PB.BoardError, match="Host"):
        OS.library_rows(p)


def test_a_url_row_outside_a_table_with_a_header_stops_the_seed(tmp_path):
    p = tmp_path / "lib.md"
    p.write_text("| https://www.rspca.org.uk/a | rspca.org.uk | RSPCA advice | `/` | x | welfare |\n",
                 encoding="utf-8")
    with pytest.raises(PB.BoardError, match="no header"):
        OS.library_rows(p)


def test_the_real_library_parses_one_row_per_url_line():
    urls = [l for l in PB.EXTERNAL_LIBRARY.read_text(encoding="utf-8").splitlines() if l.startswith("| http")]
    assert [r[0] for r in OS.library_rows()] == [l.split("|")[1].strip() for l in urls]


def test_shared_publishers_are_one_named_tuple():
    h = OS.HOST_ORG
    assert h["gov.uk"] is h["assets.publishing.service.gov.uk"] is h["legislation.gov.uk"] is OS.UK_GOVERNMENT
    assert h["thekennelclub.org.uk"] is h["royalkennelclub.com"] is OS.KENNEL_CLUB
