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
    three keys are the ones that would put the old city back on every page. `address` is
    deliberately excluded — Known Issue 16 owns it and project 4 rewrites it."""
    s = load("settings.json")
    for key in ("location_label", "tagline", "site_name"):
        assert "glasgow" not in str(s[key]).lower(), (key, s[key])
    assert s["location_label"] == "Carlisle · Cumbria"
