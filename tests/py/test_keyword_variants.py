"""System-gaps Task 1: four optional keyword types (variation, related, co-occurring,
similar), the new-family check that fills them, and the cached-data helper that proposes
them. Nothing here calls a paid service: every fixture is written under tmp_path."""
import copy
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import family_rules as FR      # noqa: E402
import pageboard as PB         # noqa: E402
import keyword_variants as KV  # noqa: E402

SCRIPT = ROOT / "scripts" / "keyword_variants.py"
OPTIONAL = ("variation", "related", "cooccurring", "similar")


def _demo(slug="uk-locations/blue-staffy-puppies-manchester-uk", page_type="location", status="boarded"):
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text(encoding="utf-8")))
    b["meta"].update({"slug": slug, "page_type": page_type, "status": status})
    return b


# --- the four types are optional, labelled, and leave every built record alone --------------

def test_the_four_types_are_optional_properties_of_the_schema():
    schema = json.loads((PB.SCHEMAS / "board.schema.json").read_text(encoding="utf-8"))
    kw = schema["properties"]["sections"]["items"]["properties"]["keywords"]
    assert PB.OPTIONAL_KEYWORD_TYPES == OPTIONAL
    assert PB.ALL_KEYWORD_TYPES == PB.KEYWORD_TYPES + OPTIONAL
    assert kw["additionalProperties"] is False
    assert kw["required"] == list(PB.KEYWORD_TYPES)             # none of the four is required
    assert set(kw["properties"]) == set(PB.ALL_KEYWORD_TYPES)
    assert {PB.KEYWORD_LABELS[k] for k in OPTIONAL} == {"Variations", "Related", "Co-occurring", "Similar"}


def test_every_built_record_still_validates_and_keeps_its_approval():
    """Adding optional properties to the schema must not move one byte of any record, so every
    approved record's stamped hash still matches."""
    seen = 0
    for p in sorted((ROOT / "data" / "boards").glob("*.json")):
        board = json.loads(p.read_text(encoding="utf-8"))
        PB.validate_board(board)
        # The boards built before the optional types existed never carry them; a new-family
        # page (working rule 17) must, so the check is scoped to the older records.
        if not FR.is_new_page(board):
            for s in board["sections"]:
                assert not set(s["keywords"]) & set(OPTIONAL), (p.name, s["id"])
        if board["meta"]["status"] == "approved":
            assert PB.approval_matches(board), p.name
            seen += 1
    assert seen >= 12


def test_distribution_reads_a_missing_optional_type_as_empty_and_counts_a_present_one():
    b = _demo()
    d = PB.distribution(b)
    assert all(d["totals"][k] == 0 for k in OPTIONAL)
    b["sections"][0]["keywords"]["related"] = ["blue staffy puppies manchester cheap", "staffy puppies near salford"]
    PB.validate_board(b)
    assert PB.distribution(b)["totals"]["related"] == 2


def test_an_unknown_keyword_type_is_still_refused():
    b = _demo()
    b["sections"][0]["keywords"]["synonyms"] = ["x"]
    with pytest.raises(PB.BoardError):
        PB.validate_board(b)


# --- family rule: a new-family page fills all four page-wide ---------------------------------

def _kv(board):
    return [f for f in FR.findings(board, {"entities": []}) if f[0] == "keyword-variants-missing"]


def test_family_rule_types_match_the_library():
    assert FR.KEYWORD_VARIANT_TYPES == PB.OPTIONAL_KEYWORD_TYPES


def test_a_boarded_new_family_page_with_no_variant_terms_fails():
    f = _kv(_demo(status="boarded"))
    assert len(f) == 1 and f[0][1] == "FAIL"
    for k in OPTIONAL:
        assert k in f[0][2]
    assert "scripts/keyword_variants.py" in f[0][2]


def test_a_draft_only_warns():
    f = _kv(_demo(status="draft"))
    assert len(f) == 1 and f[0][1] == "WARN"


def test_one_term_of_each_type_anywhere_on_the_page_passes():
    b = _demo(status="approved")
    for i, k in enumerate(OPTIONAL):                       # spread across sections on purpose
        b["sections"][i % len(b["sections"])]["keywords"][k] = [f"{k} term"]
    assert _kv(b) == []


def test_a_single_missing_type_is_named_alone():
    b = _demo(status="approved")
    for k in ("variation", "related", "cooccurring"):
        b["sections"][0]["keywords"][k] = [f"{k} term"]
    f = _kv(b)
    assert len(f) == 1 and "similar" in f[0][2] and "related" not in f[0][2].split("—")[0]


def test_built_pages_and_other_families_are_never_asked():
    assert _kv(_demo("blue-staffy-health-uk", "interior", "approved")) == []
    assert _kv(_demo("blue-staffy-blog-guides", "blog", "approved")) == []
    assert _kv(_demo("_demo", "location", "approved")) == []


# --- keyword_variants.py: proposes the four buckets from cached query files only -------------

def _root(tmp_path):
    raw = tmp_path / "data" / "queries" / "raw" / "blue-staffy-puppies-testtown"
    raw.mkdir(parents=True)
    (tmp_path / "data" / "locations.json").write_text(json.dumps([{"city": "Testtown"}, {"city": "Otherby"}]))
    (tmp_path / "data" / "queries" / "blue-staffy-puppies-testtown.json").write_text(json.dumps({
        "primary_keyword": "blue staffy puppies testtown",
        "questions": [{"question": "Are the parents health tested for L-2-HGA?"},
                      {"question": "Do blue Staffies need a Kennel Club health test?"}]}))
    (raw / "serp_google.json").write_text(json.dumps({"questions": [
        {"text": "Blue staffy puppies testtown kennel club", "detail": "serp_google_related"},
        {"text": "Staffy puppies for sale near Otherby", "detail": "serp_google_related"},
        {"text": "How much is a blue Staffy?", "detail": "serp_google_paa"}]}))
    (raw / "serp_google.response.json").write_text(json.dumps({"items": [
        {"type": "organic", "url": "https://www.petmarket.example/testtown",
         "title": "Blue Staffie Puppies for sale in Testtown - PetMarket",
         "description": "Blue Staffordshire Bull Terrier puppies, health tested, Kennel Club registered."},
        {"type": "organic", "url": "https://breeder.example/", "title": "12 Staffy Puppies For Sale In Testtown | Breeder",
         "description": "Health tested parents and Kennel Club registered blue Staffy pups in Testtown."},
        {"type": "related_searches", "items": ["Blue staffy puppies testtown kennel club", "Blue staffy testtown cheap"]}]}))
    (raw / "ai_engines.response.json").write_text(json.dumps({"answer_points": [
        "Ask to see health tested parents and the L-2-HGA certificate ([Kennel Club](https://example.org/?utm_source=chatgpt.com))."]}))
    (raw / "competitors.json").write_text(json.dumps({"pages": [
        {"url": "https://breeder.example/", "h2": ["Frequently Asked Questions", "Blue Staffy Puppies Near Testtown"]}]}))
    return tmp_path


def test_propose_fills_all_four_buckets_from_the_cache(tmp_path):
    out = KV.propose("blue-staffy-puppies-testtown", root=_root(tmp_path))
    terms = {k: [t["term"] for t in out["buckets"][k]] for k in OPTIONAL}
    assert out["primary"] == "blue staffy puppies testtown"
    # related: the engine's own related box, merged across the two files, deduplicated
    # ("blue staffy testtown cheap" is in the box too, and dropped: a brand clash, Task 12a)
    assert terms["related"] == ["blue staffy puppies testtown kennel club",
                                "staffy puppies for sale near otherby"]
    # variation: attested surface forms of the head term, never the primary itself
    assert "blue staffie puppies" in terms["variation"]
    assert "blue staffordshire bull terrier puppies" in terms["variation"]
    assert "blue staffy puppies testtown" not in terms["variation"]
    # similar: how the ranking pages word the same query; the FAQ heading is not one
    assert "blue staffie puppies for sale in testtown" in terms["similar"]
    assert "staffy puppies for sale in testtown" in terms["similar"]          # leading count stripped
    assert "frequently asked questions" not in terms["similar"]
    # co-occurring: phrases in two or more cached documents, marketplace names and URLs out
    assert "health tested" in terms["cooccurring"] and "kennel club" in terms["cooccurring"]
    assert not any("petmarket" in t or "utm" in t or "chatgpt" in t for t in terms["cooccurring"])
    for k in OPTIONAL:
        for t in out["buckets"][k]:
            assert t["sources"], (k, t)


def test_cli_prints_json_and_exits_6_with_no_cache(tmp_path):
    root = _root(tmp_path)
    r = subprocess.run([sys.executable, str(SCRIPT), "blue-staffy-puppies-testtown", "--root", str(root)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert set(json.loads(r.stdout)["buckets"]) == set(OPTIONAL)
    r = subprocess.run([sys.executable, str(SCRIPT), "blue-staffy-puppies-nowhere", "--root", str(root)],
                       capture_output=True, text=True)
    assert r.returncode == 6 and "bsuk-query-augmentation" in r.stderr
    r = subprocess.run([sys.executable, str(SCRIPT), "../etc"], capture_output=True, text=True)
    assert r.returncode == 2


@pytest.mark.parametrize("slug", ["blue-staffy-puppies-manchester-uk", "blue-staffy-puppies-for-sale-leeds"])
def test_the_real_cached_cities_fill_every_bucket(slug):
    if not (ROOT / "data" / "queries" / "raw" / slug).is_dir():
        pytest.skip(f"no cached query data for {slug}")
    out = KV.propose(slug)
    for k in OPTIONAL:
        assert out["buckets"][k], (slug, k)


def test_also_folds_in_a_neighbouring_folder_and_refuses_a_missing_one(tmp_path):
    root = _root(tmp_path)
    near = root / "data" / "queries" / "raw" / "registry-staffy-puppies-testtown"
    near.mkdir()
    (near / "serp_google.response.json").write_text(json.dumps({"items": [
        {"type": "organic", "url": "https://other.example/", "title": "Blue Staffy Puppies and Dogs in Testtown - Other"},
        {"type": "people_also_ask", "items": ["How much is a blue Staffy puppy?"]},     # bare strings
        {"type": "related_searches", "items": ["Staffy puppies testtown kennel club"]}]}))
    base = KV.propose("blue-staffy-puppies-testtown", root=root)
    out = KV.propose("blue-staffy-puppies-testtown", root=root, also=["registry-staffy-puppies-testtown"])
    assert out["primary"] == base["primary"]                           # the primary stays the slug's
    assert "blue staffy puppies and dogs in testtown" in [t["term"] for t in out["buckets"]["similar"]]
    assert "staffy puppies testtown kennel club" in [t["term"] for t in out["buckets"]["related"]]
    assert KV.propose("blue-staffy-puppies-testtown", root=root, also=["registry-nowhere"]) is None
    r = subprocess.run([sys.executable, str(SCRIPT), "blue-staffy-puppies-testtown", "--also", "../x",
                        "--root", str(root)], capture_output=True, text=True)
    assert r.returncode == 2


# --- review fixes: whole-label domain ban, any cache shape, blank terms, empty cache ---------

def test_a_hyphenated_host_bans_its_whole_label_not_every_word_in_it(tmp_path):
    """The label is banned in both forms — hyphenated (`staffy-owners`, after the shared
    spelling merge) and joined (`staffieowners`, which the merge leaves alone) — and only
    because of the host: with no such host the same two phrases survive."""
    root = _root(tmp_path)
    raw = root / "data" / "queries" / "raw" / "blue-staffy-puppies-testtown"
    (raw / "threads.json").write_text(json.dumps({"threads": [
        {"title": "Responsible owners on the staffie-owners forum"},
        {"title": "What responsible owners ask on the staffieowners forum"},
        {"title": "Staffie-owners forum rules for responsible owners"},
        {"title": "The staffieowners forum answers responsible owners"}]}))

    def cooccurring():
        return [t["term"] for t in KV.propose("blue-staffy-puppies-testtown", root=root)["buckets"]["cooccurring"]]

    control = cooccurring()                                   # no staffie-owners host yet
    assert "staffy-owners forum" in control and "staffieowners forum" in control, control
    (raw / "competitors.json").write_text(json.dumps({"pages": [
        {"url": "https://staffie-owners.example/", "h2": ["Advice for responsible owners"]}]}))
    terms = cooccurring()
    assert "responsible owners" in terms
    assert not any("staffy-owners" in t or "staffieowners" in t for t in terms), terms


def test_a_host_named_after_a_place_bans_nothing(tmp_path):
    """A council host (manchester.gov.uk) has a place name for a label; banning it would drop
    every phrase that names the city."""
    root = _root(tmp_path)
    (root / "data" / "locations.json").write_text(json.dumps([{"city": "Testtown"}, {"city": "Manchester"}]))
    raw = root / "data" / "queries" / "raw" / "blue-staffy-puppies-testtown"
    (raw / "competitors.json").write_text(json.dumps({"pages": [
        {"url": "https://www.manchester.gov.uk/dogs", "h2": ["Rehoming at Manchester Dogs Home"]}]}))
    (raw / "threads.json").write_text(json.dumps({"threads": [{"title": "Adopting from Manchester Dogs Home"}]}))
    terms = [t["term"] for t in KV.propose("blue-staffy-puppies-testtown", root=root)["buckets"]["cooccurring"]]
    assert "manchester dogs home" in terms, terms


def test_a_list_shaped_file_and_string_items_do_not_crash(tmp_path):
    root = _root(tmp_path)
    raw = root / "data" / "queries" / "raw" / "blue-staffy-puppies-testtown"
    (raw / "serp_bing.json").write_text(json.dumps(["not", "an", "object"]))
    (raw / "ai_engines.json").write_text(json.dumps({"questions": ["Is a blue staffy kennel club registered?", 7]}))
    (raw / "threads.json").write_text(json.dumps({"threads": ["Blue staffy kennel club advice", {"title": None}],
                                                  "questions": "not a list"}))
    (raw / "competitors.json").write_text(json.dumps({"pages": ["https://x.example/", {"url": 3, "h2": [None, "Health tested parents"]}]}))
    resp = json.loads((raw / "serp_google.response.json").read_text())
    resp["items"] += ["organic", {"type": "people_also_ask", "items": [{"title": "Do they shed?"}, None]}]
    (raw / "serp_google.response.json").write_text(json.dumps(resp))
    out = KV.propose("blue-staffy-puppies-testtown", root=root)
    assert set(out["buckets"]) == set(OPTIONAL)
    assert KV._read(raw / "serp_bing.json") is None


def test_blank_terms_do_not_fill_a_type():
    b = _demo(status="approved")
    for k in OPTIONAL:
        b["sections"][0]["keywords"][k] = ["term"]
    b["sections"][0]["keywords"]["similar"] = ["", "   "]
    f = _kv(b)
    assert len(f) == 1 and f[0][1] == "FAIL" and "similar" in f[0][2]


def test_the_hint_takes_the_board_slug_or_the_cache_folder():
    msg = _kv(_demo(status="boarded"))[0][2]
    assert "`python3 scripts/keyword_variants.py <board slug or query-cache folder>`" in msg
    assert "uk-locations/blue-staffy-puppies-manchester-uk" in msg


# --- Task 12a item 2: the board slug resolves to its query-cache folder ---------------------

def _cli(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), *args, "--root", str(root)],
                          capture_output=True, text=True)


def test_a_nested_board_slug_resolves_to_its_cache_folder(tmp_path):
    root = _root(tmp_path)
    assert KV.resolve_cache("uk-locations/blue-staffy-puppies-testtown", root) == "blue-staffy-puppies-testtown"
    r = _cli(root, "uk-locations/blue-staffy-puppies-testtown")
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["slug"] == "blue-staffy-puppies-testtown"


def test_a_bare_board_slug_maps_to_its_uk_folder(tmp_path):
    root = _root(tmp_path)
    (root / "data" / "queries" / "raw" / "blue-staffy-puppies-testtown").rename(
        root / "data" / "queries" / "raw" / "blue-staffy-puppies-testtown-uk")
    (root / "data" / "queries" / "blue-staffy-puppies-testtown.json").unlink()
    assert KV.resolve_cache("blue-staffy-puppies-testtown", root) == "blue-staffy-puppies-testtown-uk"
    assert KV.resolve_cache("uk-locations/blue-staffy-puppies-testtown", root) == "blue-staffy-puppies-testtown-uk"
    r = _cli(root, "uk-locations/blue-staffy-puppies-testtown")
    assert r.returncode == 0, r.stderr


def test_a_unique_prefix_resolves_and_an_existing_folder_is_taken_as_it_is(tmp_path):
    root = _root(tmp_path)
    assert KV.resolve_cache("blue-staffy-puppies-test", root) == "blue-staffy-puppies-testtown"
    assert KV.resolve_cache("blue-staffy-puppies-testtown", root) == "blue-staffy-puppies-testtown"


def test_an_ambiguous_or_unknown_slug_exits_6_naming_close_folders(tmp_path):
    root = _root(tmp_path)
    raw = root / "data" / "queries" / "raw"
    for name in ("blue-staffy-puppies-testtown-north", "registry-staffy-puppies-testtown"):
        (raw / name).mkdir()
    with pytest.raises(KV.CacheNotFound) as e:
        KV.resolve_cache("uk-locations/blue-staffy-puppies-test", root)
    assert e.value.candidates == ["blue-staffy-puppies-testtown", "blue-staffy-puppies-testtown-north"]
    r = _cli(root, "uk-locations/blue-staffy-puppies-test")
    assert r.returncode == 6
    assert "blue-staffy-puppies-testtown, blue-staffy-puppies-testtown-north" in r.stderr
    r = _cli(root, "uk-locations/staffy-puppies-testtwn")
    assert r.returncode == 6 and "registry-staffy-puppies-testtown" in r.stderr
    assert len(KV.close_folders("x", [f"f{i}" for i in range(20)] + ["x1", "x2"])) <= 5


def test_an_empty_or_unreadable_cache_folder_exits_6(tmp_path):
    root = tmp_path
    raw = root / "data" / "queries" / "raw"
    (raw / "blue-staffy-puppies-emptyville").mkdir(parents=True)
    (raw / "blue-staffy-puppies-brokenville").mkdir()
    (raw / "blue-staffy-puppies-brokenville" / "serp_google.json").write_text("{not json")
    for slug in ("blue-staffy-puppies-emptyville", "blue-staffy-puppies-brokenville"):
        r = subprocess.run([sys.executable, str(SCRIPT), slug, "--root", str(root)], capture_output=True, text=True)
        assert r.returncode == 6, (slug, r.stdout)
        assert "nothing readable" in r.stderr and "bsuk-query-augmentation" in r.stderr


def test_a_host_named_after_a_primary_keyword_word_bans_nothing(tmp_path):
    """puppies.co.uk ranks for Manchester: its label normalises to `puppy`, a word of the
    primary, and banning it would drop every phrase that says puppy."""
    root = _root(tmp_path)
    raw = root / "data" / "queries" / "raw" / "blue-staffy-puppies-testtown"
    (raw / "competitors.json").write_text(json.dumps({"pages": [
        {"url": "https://www.puppies.example/sale", "h2": ["Ask for the puppy contract"]}]}))
    (raw / "threads.json").write_text(json.dumps({"threads": [{"title": "Is a puppy contract worth it?"}]}))
    terms = [t["term"] for t in KV.propose("blue-staffy-puppies-testtown", root=root)["buckets"]["cooccurring"]]
    assert "puppy contract" in terms, terms


# --- Task 12a item 8: proposals that clash with the brand are dropped -----------------------

@pytest.mark.parametrize("term", [
    "blue staffy testtown cheap", "cheapest staffy puppies", "staffy puppies under £500",
    "blue staffy under 300", "staffy puppies under £ 400", "free staffy puppy to good home",
    "free blue staffies to good homes", "staffy rescue testtown", "blue staffy rescues"])
def test_a_brand_clash_is_denied(term):
    assert KV.brand_clash(term)


@pytest.mark.parametrize("term", [
    "blue staffy puppies testtown kennel club", "health tested", "free puppy pack",
    "a good home for a blue staffy", "under the table", "staffy puppy price"])
def test_an_ordinary_term_is_not(term):
    assert not KV.brand_clash(term)


def test_no_bucket_proposes_a_brand_clash(tmp_path):
    root = _root(tmp_path)
    raw = root / "data" / "queries" / "raw" / "blue-staffy-puppies-testtown"
    (raw / "threads.json").write_text(json.dumps({"threads": [
        {"title": "Cheap blue staffy puppies testtown under £300"},
        {"title": "Cheap blue staffy puppies testtown, free to a good home"},
        {"title": "Staffy rescue centre Testtown"}, {"title": "Staffy rescue centre Otherby"}]}))
    (raw / "serp_google.json").write_text(json.dumps({"questions": [
        {"text": "Blue staffy puppies testtown kennel club", "detail": "serp_google_related"},
        {"text": "Staffy rescue Testtown", "detail": "serp_google_related"},
        {"text": "Blue staffy puppies testtown under 500", "detail": "serp_google_related"}]}))
    out = KV.propose("blue-staffy-puppies-testtown", root=root)
    terms = [t["term"] for k in OPTIONAL for t in out["buckets"][k]]
    assert terms and not [t for t in terms if KV.brand_clash(t)], terms
    assert not any("rescue" in t or "cheap" in t or "under" in t for t in terms), terms


# --- a marketplace or directory name is never proposed ------------------------------------

@pytest.mark.parametrize("term", [
    "staffy puppies for sale manchester gumtree", "pets4homes blue staffy", "pets 4 homes staffy",
    "preloved staffy puppies", "freeads staffy", "free ads staffy puppies", "champdogs staffordshire",
    "puppies co uk staffy", "puppies.co.uk blue staffy", "petsforlove staffy", "petify staffy",
    "ukpets blue staffy"])
def test_a_marketplace_term_is_denied(term):
    assert KV.brand_clash(term)


@pytest.mark.parametrize("term", ["blue staffy puppies uk", "puppies for sale uk", "free puppy pack",
                                  "health tested pets"])
def test_ordinary_puppy_words_are_not_a_marketplace(term):
    assert not KV.brand_clash(term)


def test_the_marketplaces_in_the_competitor_registry_are_all_denied():
    reg = json.loads((ROOT / "data" / "competitors.json").read_text(encoding="utf-8"))
    ids = {c["id"] for c in reg["competitors"]}
    for mid in ("gumtree", "pets4homes", "preloved", "freeads", "champdogs", "puppies"):
        assert mid in ids, mid
    for c in reg["competitors"]:
        if c["id"] in KV.MARKETPLACE_IDS:
            assert KV.brand_clash(c["root_domain"]), c["root_domain"]
