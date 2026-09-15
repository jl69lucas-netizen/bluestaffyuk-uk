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
        assert (ROOT / "assets" / "brand" / p["slug"] / p["card_photo"]).exists()
        for g in p["gallery"]:
            assert (ROOT / "assets" / "brand" / p["slug"] / g).exists()
        assert p["card_photo"] in p["gallery"]
    assert {p["slug"] for p in pups} == {"roman","byrd","ince","vennie","christa","cheryl"}
