import json, pathlib
from build_redirects import render
ROOT = pathlib.Path(__file__).resolve().parents[2]

def rows():
    return json.loads((ROOT / "data/redirects.json").read_text(encoding="utf-8"))["redirects"]

def test_render_redirects_lines():
    text = render(rows())
    assert "/uk-locations/staffordshire-bull-terrier-puppies-for-sale-essex/ /uk-locations/staffy-puppies-for-sale-essex/ 301" in text
    assert "/form/* /uk-blue-staffy-breeders-contact/ 301" in text
    assert "/wp-json/* / 301" in text
    assert "/admin/* / 301" in text
    assert "/:slug/feed/ / 301" in text
    assert "/:a/:b/feed/ / 301" in text
    assert not any(l.startswith("/sitemap") for l in text.splitlines())

def test_no_chains():
    froms = {r["from"] for r in rows()}
    assert not [r for r in rows() if r["to"] in froms], "a redirect target is itself redirected"

def test_every_target_is_a_known_page():
    pm = json.loads((ROOT / "data/page-map.json").read_text(encoding="utf-8"))["pages"]
    known = {p["url"] for p in pm} | {"/", "/blog/", "/uk-locations/", "/available-puppies/"}
    for r in rows():
        assert r["to"] in known, r

def test_committed_redirects_file_matches_data():
    assert render(rows()) == (ROOT / "public/_redirects").read_text(encoding="utf-8")

def test_no_duplicate_from():
    froms = [r["from"] for r in rows()]
    assert len(froms) == len(set(froms)), [f for f in froms if froms.count(f) > 1]

def test_splats_trailing_and_placeholders_well_formed():
    import re
    for r in rows():
        src = r["from"]
        if "*" in src:
            assert src.count("*") == 1 and src.endswith("*"), src
        for seg in src.split("/"):
            if seg.startswith(":"):
                assert re.fullmatch(r":[a-z]+", seg), src
