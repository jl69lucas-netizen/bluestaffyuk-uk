import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]

def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))

def test_settings_has_placeholder_phone_and_facts():
    s = load("settings.json")
    assert s["phone"] == "PHONE_PLACEHOLDER"
    assert s["breeder_name"] == "Lisa Bright"
    assert s["deposit_gbp"] == 500 and s["deposit_refundable"] is True
    assert s["delivery_min_gbp"] == 200 and s["delivery_max_gbp"] == 350
    assert s["socials"]["youtube"].startswith("https://www.youtube.com/@")

def test_price_matrix_matches_puppies():
    pm = load("price-matrix.json"); pups = load("puppies.json"); s = load("settings.json")
    assert pm["male_gbp"] == 1500 and pm["female_gbp"] == 1700
    assert pm["deposit_gbp"] == s["deposit_gbp"] and pm["deposit_refundable"] is s["deposit_refundable"]
    assert s["price_range"] == "£%d - £%d" % (pm["male_gbp"], pm["female_gbp"])
    assert len(pups) == 6
    for p in pups:
        assert p["price_gbp"] == (pm["male_gbp"] if p["sex"] == "male" else pm["female_gbp"])
        assert p["sex"] in {"male", "female"}
        assert p["status"] in {"Available", "Reserved", "Sold"}
        assert p["status"] == "Available"
        # Project 3 Task 7 moved the masters into src/assets/puppies/ (astro:assets).
        assert (ROOT / "src" / "assets" / "puppies" / p["card_photo"]).exists()
        for g in p["gallery"]:
            assert (ROOT / "src" / "assets" / "puppies" / g).exists()
        assert p["card_photo"] in p["gallery"]
    assert {p["slug"] for p in pups} == {"roman","byrd","ince","vennie","christa","cheryl"}


def test_puppy_photo_filenames_are_unique_across_the_litter():
    """src/assets/puppies/ is one flat folder keyed by filename (src/lib/puppyImages.ts),
    so two pups sharing a photo name would silently render the same dog twice."""
    # Per pup the names are de-duplicated first: a card_photo that also appears in that
    # pup's own gallery is one file, not a collision.
    names = [n for p in load("puppies.json") for n in sorted({p["card_photo"], *p["gallery"]})]
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, dupes


def test_site_settings_do_not_say_glasgow():
    """Known Issue 16: the breeder relocated. The kit reads `location_label`, so these
    three keys are the ones that would put the old city back on every page. The `address`
    object is checked by the test below, which project 4 Task 6 rewrote."""
    s = load("settings.json")
    for key in ("location_label", "tagline", "site_name"):
        assert "glasgow" not in str(s[key]).lower(), (key, s[key])
    assert s["location_label"] == "Carlisle · Cumbria"


def test_address_is_town_level_only():
    """Known Issue 16: the address is Carlisle, Cumbria and nothing else.

    The breeder has not supplied a street, a postcode or coordinates for the new place,
    so the only honest address is the town and the region. A stale street or a stale
    lat/lng is worse than no address at all: it publishes a location the business has
    left, in the one field a map consumer trusts absolutely. Any of these keys coming
    back means somebody restored the old record rather than waiting for the new one.
    """
    a = load("settings.json")["address"]
    assert a == {"city": "Carlisle", "region": "Cumbria", "country": "GB"}, a
    for gone in ("street", "postcode", "lat", "lng"):
        assert gone not in a, gone


#: The six personality lines the breeder approved word for word (answer board 2026-10-04 q07 (a),
#: docs/reference/answer-board/answers/2026-10-04-london-asset-gate-and-previews-2026-10-04.md).
#: The puppy cards print them (src/components/kit/CityTicketStrip.astro throws on a missing one).
APPROVED_PERSONALITY = {
    "roman": "Our blue-and-white boy with a white blaze and bright blue eyes, happiest stretched out on the grass watching everything we do.",
    "byrd": "Our solid white boy, sturdy and square-faced, first to trot over and see who's come in, then out for a nap on his blanket.",
    "ince": "A solid blue boy with a white chest flash who goes about with his tail up, checking every corner of the garden fence.",
    "vennie": "A white-faced blue-and-white girl with a blue patch over one eye, curled up soft and calm on the sheepskin rug.",
    "christa": "A solid blue girl with a white star on her chest and a steady, thoughtful look, sitting up straight as if she knows she's being photographed.",
    "cheryl": "A blue girl with a white blaze who lies flat out on the floor beside her toy and looks straight up for attention.",
}


def test_every_puppy_has_a_personality_line():
    pups = load("puppies.json")
    missing = [p["slug"] for p in pups if not (p.get("personality") or "").strip()]
    assert missing == [], f"puppies with no personality line: {missing}"


def test_the_personality_lines_are_the_ones_the_breeder_approved():
    pups = load("puppies.json")
    for p in pups:
        if p["slug"] in APPROVED_PERSONALITY:
            assert p["personality"] == APPROVED_PERSONALITY[p["slug"]], p["slug"]
