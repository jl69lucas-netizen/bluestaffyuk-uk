"""data/breed-standards.json: every figure is sourced, dated and quoted (CLAUDE.md rule 9).

The file feeds the London breed-split infographic (IG-3, breeder q07, 2026-10-02). A field is
either a sourced fact — value, an exact quote of at most 25 words, a source URL and a fetched
date — or `NOT FETCHED — <barrier>` with nothing else claimed."""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "data/breed-standards.json").read_text())
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NUM = re.compile(r"\d+(?:\.\d+)?")
BREEDS = ("staffordshire-bull-terrier", "american-staffordshire-terrier",
          "american-pit-bull-terrier")
REQUIRED = ("height", "weight", "colours", "temperament_line", "uk_legal_status")
GOV = "https://www.gov.uk/"


def _fields():
    for breed, rec in DATA["breeds"].items():
        for name, field in rec.items():
            if isinstance(field, dict):
                yield f"{breed}.{name}", field
    yield "uk_banned_types", DATA["uk_banned_types"]


FIELDS = dict(_fields())


def test_shape():
    assert DATE.match(DATA["fetched"])
    assert set(BREEDS) <= set(DATA["breeds"])
    for b in BREEDS:
        for f in REQUIRED:
            assert f in DATA["breeds"][b], (b, f)


@pytest.mark.parametrize("key", sorted(FIELDS))
def test_every_field_is_sourced_or_names_its_barrier(key):
    field = FIELDS[key]
    v = field.get("value")
    assert isinstance(v, str) and v, key
    if v.startswith("NOT FETCHED"):
        assert re.match(r"^NOT FETCHED — \S+(?: \S+)+", v), f"{key}: name the barrier"
        assert not {"quote", "source"} & set(field), f"{key}: a NOT FETCHED claims no source"
        return
    assert field.get("source", "").startswith("https://"), key
    assert DATE.match(field.get("fetched", "")), key
    quote = field.get("quote", "")
    assert quote and len(quote.split()) <= 25, f"{key}: quote missing or over 25 words"
    value_nums = set(NUM.findall(v))
    for n in NUM.findall(quote):
        assert n in value_nums, f"{key}: quoted number {n} is not in the value {v!r}"


@pytest.mark.parametrize("breed", BREEDS)
def test_uk_legal_status_comes_from_gov_uk_only(breed):
    st = DATA["breeds"][breed]["uk_legal_status"]
    if not st["value"].startswith("NOT FETCHED"):
        assert st["source"].startswith(GOV), breed


def test_every_verdict_clause_cites_a_source_the_file_uses():
    v = DATA["comparison_verdict"]
    used = {f["source"] for f in FIELDS.values() if "source" in f}
    assert v["clauses"] and DATE.match(v["fetched"])
    for c in v["clauses"]:
        assert c["text"] and c["source"] in used, c
        if "banned" in c["text"]:
            assert c["source"].startswith(GOV), c
    # The verdict says nothing numeric the clauses or fields do not.
    assert not NUM.findall(v["value"])


def test_kc_staffy_figures_as_the_standard_states_them():
    sbt = DATA["breeds"]["staffordshire-bull-terrier"]
    assert "36-41 cms" in sbt["height"]["quote"]
    assert "13-17 kgs" in sbt["weight"]["quote"] and "11-15.4 kgs" in sbt["weight"]["quote"]
    assert "blue" in sbt["colours"]["quote"]
