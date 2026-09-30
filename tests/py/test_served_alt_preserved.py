"""Working rule 11: a served image keeps its served alt text word for word, wherever it is reused;
on a page that shows it twice, its first use keeps the served alt and each repeat carries a new
alt, never a copy (the user's ruling, answer board q02, 2026-09-29).

Learning loop 2026-09-27 (docs/reports/learning-loop-2026-09-27.md, L2 / shortlist #1). Tasks 5–8
of the London component pass rewrote the alts of four served files; a reviewer caught it twice and
no check could, because `scripts/check_city_canvas.py` asked only that an alt be non-empty and
`scripts/verbatim_set_check.py` covers a migrated page's own alts, never a served file reused
elsewhere.

The served alts are read from the record of what the old site served (`data/verbatim/*.json` alts
and `data/locations.json` body images), by `check_city_canvas.served_alts()`. A rebuilt page may
also carry the `new` alt of an `alt` row in its board record's `verbatim.changed` (working rule 15
lets a wrong fact be corrected, and records it). An empty alt is a decorative repeat, not a
rewrite. `/puppies/` photos are exempt: they already carry per-page alts (plan2-notes, Task 8).
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_city_canvas as C  # noqa: E402
import verbatim_set_check as V  # noqa: E402
from _slugs import built_page  # noqa: E402

CANVAS = ROOT / "design" / "city-canvas"

#: Second instances on a rebuilt page that re-describe a served file, found when this test was
#: written (2026-09-27) and reported to the user rather than edited: each is a hero-mosaic tile
#: whose file is also shown in the body WITH its served alt. They are real under the rule's
#: letter, so they are listed, counted and exact: a new hit fails, and fixing one fails until
#: its row is removed here. (page, file, alt on the page)
# The four hero-mosaic tiles below keep their live alts by the user's ruling of 2026-09-28
# (Known Issue 93): a served alt on the tile would duplicate the body copy's alt, which Rule 50b
# (board_gate asset-alt-duplicate) blocks. This is a permanent, counted exception.
KNOWN = {
    ("buy-blue-staffy-puppies-uk", "blue-staffy-pups-near-you.webp",
     "Blue Staffy puppies available near you in the UK"),
    ("buy-blue-staffy-puppies-uk", "blue-staffy-puppy-delivery-uk.webp",
     "A blue Staffy puppy ready for UK home delivery"),
    ("blue-staffy-uk-breeders", "breeder-sitting-blue-staffy-puppy-home.webp",
     "Lisa Bright sitting with a blue Staffy puppy at home in Carlisle"),
    ("blue-staffy-uk-breeders", "playful-blue-staffy-lawn-uk.webp",
     "A playful blue Staffy on the lawn at our home in Cumbria"),
}

IMG = re.compile(r"<img\b[^>]*>", re.I)


def judge_page(html_text, served, changed):
    """(served images examined, [(file, alt on the page)] that break the rule). The FIRST use of
    a served file on the page keeps its served alt (or its recorded `verbatim.changed` alt);
    each later use is a repeat and carries a NEW alt, never a copy of one already used for that
    file on the page (the user's ruling, answer board q02, 2026-09-29). An empty alt is a
    decorative repeat and passes; a MISSING alt attribute (None) is a rewrite, never decorative."""
    examined, hits = 0, []
    used = {}  # file -> the alts already used for it on this page
    for tag in IMG.findall(html_text):
        src, alt = C._tag_attr(tag, "src"), C._tag_attr(tag, "alt")
        if not src or not src.startswith("/images/"):
            continue
        name = C.served_name(src[len("/images/"):], served)
        if name not in served:
            continue
        examined += 1
        if alt is None:
            hits.append((name, alt))
            continue
        alt = " ".join(alt.split())
        if alt == "":
            continue
        # Only a NON-EMPTY alt claims the first-use slot: a decorative alt="" before it must not
        # let the served alt be dropped altogether.
        first = name not in used
        seen = used.setdefault(name, set())
        if first:
            ok = alt in served[name] or alt in changed.get(name, ())
        else:
            ok = alt not in seen
        seen.add(alt)
        if not ok:
            hits.append((name, alt))
    return examined, hits


def test_the_served_alts_are_read_and_not_empty():
    served = C.served_alts()
    assert len(served) >= 50, f"only {len(served)} served files read — the source moved?"
    assert "Mark with their healthy blue Staffy puppy from BlueStaffyUK.uk in London." in \
        served["mark-blue-staffy-london.webp"]


def test_every_canvas_fragment_keeps_every_served_alt():
    c = C.default_context()
    frags = sorted(CANVAS.glob("*/*/[abc].html"))
    assert frags, "no canvas fragments — examined 0, not a pass"
    hits = []
    for f in frags:
        hits += [f"{f.relative_to(ROOT)}: {x}" for x in
                 C.validate_fragment(f.parent.name, f.stem, f.read_text(encoding="utf-8"), c)
                 if "served alt" in x]
    assert hits == [], "\n".join(hits)


def _changed_alts(slug):
    """{file: {new alt}} from the page's `verbatim.changed` alt rows."""
    served = C.served_alts()
    out = {}
    for r in (V.load_record(slug).get("verbatim") or {}).get("changed", []):
        if not isinstance(r, dict) or r.get("kind") != "alt" or not r.get("new"):
            continue
        files = [r["src"].rsplit("/", 1)[-1]] if r.get("src") else \
            [f for f, alts in served.items() if r.get("old") in alts]
        for f in files:
            out.setdefault(f, set()).add(r["new"])
    return out


def test_every_rebuilt_page_keeps_every_served_alt():
    rebuilt = json.loads((ROOT / "data" / "facts" / "rebuilt.json").read_text(encoding="utf-8"))
    pages = [(s, built_page(s, ROOT)) for s in rebuilt]
    pages = [(s, p) for s, p in pages if p.is_file()]
    if not pages:
        pytest.skip("dist/ is not built — run npm run -s build")
    served = C.served_alts()
    examined, hits = 0, set()
    for slug, path in pages:
        n, found = judge_page(path.read_text(encoding="utf-8"), served, _changed_alts(slug))
        examined += n
        hits |= {(slug, name, alt) for name, alt in found}
    assert examined >= 30, f"examined {examined} served images on {len(pages)} pages — not a pass"
    assert hits - KNOWN == set(), f"a served alt was rewritten: {sorted(hits - KNOWN)}"
    assert KNOWN - hits == set(), f"fixed — remove from KNOWN: {sorted(KNOWN - hits)}"


def test_every_width_variant_maps_to_its_served_file():
    """Review 2026-09-28: the -440 variants (index's manchester family photo) were not mapped
    back to their served file, so their alts went unchecked. Any 3–4 digit width suffix is."""
    served = {"victoria-family-blue-staffy-manchester.webp": frozenset({"x"}),
              "healthy-staffy-breed-guide-1.webp": frozenset({"y"})}
    for w in (240, 400, 440, 760, 1080):
        assert C.served_name(f"victoria-family-blue-staffy-manchester-{w}.webp", served) == \
            "victoria-family-blue-staffy-manchester.webp"
    assert C.served_name("healthy-staffy-breed-guide-1.webp", served) == "healthy-staffy-breed-guide-1.webp"
    assert C.served_name("unknown-760.webp", served) == "unknown-760.webp"



def test_a_missing_alt_is_a_rewrite_not_a_decorative_image():
    """Review 2026-09-28: an <img> with NO alt attribute was read as alt="" and exempted."""
    served = {"maggie-blue-staffy-dam-with-pups.webp": frozenset({"Maggie"})}
    html = ('<img src="/images/maggie-blue-staffy-dam-with-pups.webp">'
            '<img src="/images/maggie-blue-staffy-dam-with-pups.webp" alt="">'
            "<img src='/images/maggie-blue-staffy-dam-with-pups.webp' alt='Maggie'>"
            "<img src='/images/maggie-blue-staffy-dam-with-pups.webp' alt='Someone else'>")
    examined, hits = judge_page(html, served, {})
    assert examined == 4
    # The first use has no alt (a rewrite); the empty alt is decorative; the two later uses are
    # repeats, each with an alt not yet used for the file on the page (the user's ruling,
    # 2026-09-29: a repeat carries a new alt, never a copy).
    assert hits == [("maggie-blue-staffy-dam-with-pups.webp", None)]


def test_a_repeated_photo_keeps_its_served_alt_first_and_a_new_alt_after():
    """The user's ruling (answer board q02, 2026-09-29): "No repeated alt, same photo use new
    alt". A photo shown twice on one page keeps its served alt on its FIRST use (working rule 11)
    and each repeat carries a new alt, never a copy of one already used for it on the page."""
    served = {"maggie-blue-staffy-dam-with-pups.webp": frozenset({"Maggie"})}
    img = '<img src="/images/maggie-blue-staffy-dam-with-pups.webp" alt="%s">'
    ok = img % "Maggie" + img % "Maggie with her litter in the garden" + img % "The dam, resting"
    assert judge_page(ok, served, {}) == (3, [])
    copy = img % "Maggie" + img % "Maggie"
    assert judge_page(copy, served, {})[1] == [("maggie-blue-staffy-dam-with-pups.webp", "Maggie")]
    first_new = img % "A new alt" + img % "Maggie"
    assert judge_page(first_new, served, {})[1] == [("maggie-blue-staffy-dam-with-pups.webp", "A new alt")]
    # A decorative first use (alt="") does not claim the first-use slot: the first NON-EMPTY
    # alt still has to be the served one (review of Task 10b, item 1).
    decorative_first = img % "" + img % "Brand new"
    assert judge_page(decorative_first, served, {})[1] == [("maggie-blue-staffy-dam-with-pups.webp", "Brand new")]
    assert judge_page(img % "" + img % "Maggie", served, {})[1] == []
    # A width variant is the same photo: its repeat is judged as a repeat.
    variant = img % "Maggie" + '<img src="/images/maggie-blue-staffy-dam-with-pups-760.webp" alt="Maggie">'
    assert judge_page(variant, served, {})[1] == [("maggie-blue-staffy-dam-with-pups.webp", "Maggie")]


def test_the_attribute_reader_takes_both_quotes():
    assert C._tag_attr("<img src='/images/a.webp' alt='It&#39;s Maggie'>", "alt") == "It's Maggie"
    assert C._tag_attr('<img src="/images/a.webp" alt="Maggie">', "alt") == "Maggie"
    assert C._tag_attr('<img src="/images/a.webp">', "alt") is None
