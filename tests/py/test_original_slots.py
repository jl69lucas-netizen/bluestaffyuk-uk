"""Block 7d, "Original photos": 4–5 of the site's real photos on the best-suited H2/H3s.

The breeder's ruling (answer board q06, 2026-10-02): OG means ORIGINAL image — not generated,
not an infographic. Original photos go on first; infographics and generated images only fill
what is left.
"""
import json
import re
import struct
import subprocess
import sys
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import original_slots as OS  # noqa: E402
import generated_briefs as GB  # noqa: E402

LONDON = ROOT / "data/boards/blue-staffy-puppies-london.json"


@pytest.fixture(scope="module")
def london():
    return json.loads(LONDON.read_text())


@pytest.fixture(scope="module")
def inv():
    return OS.inventory(ROOT)


# ── inventory ───────────────────────────────────────────────────────────────────────────
def test_exclusion_markers_are_pinned():
    assert OS.FILENAME_MARKERS == ("infographic", "comparison", "-vs-", "chart", "diagram",
                                   "steps", "process", "logo", "icon", "generated", "og-",
                                   "-card-", "-portrait-")
    assert OS.ALT_MARKERS == ("infographic", "graphic", "illustrat", "icons", "montage",
                              "map", "cover image", "silhouette", "visual comparison",
                              "side-by-side", "quote displayed", "thank you message",
                              "webpage")


def test_inventory_is_real_photos_only(inv):
    paths = {p["path"] for p in inv}
    assert len(inv) >= 40
    for p in paths:
        low = p.lower()
        assert not any(m in low for m in OS.FILENAME_MARKERS), p
        assert not re.search(r"-\d{2,4}\.webp$", p), p          # size siblings fold away
    for p in inv:
        assert not any(OS._alt_hit(p["alt"], m) for m in OS.ALT_MARKERS), p
    # real photos are in
    for keep in ("/images/maggie-blue-staffy-dam-with-pups.webp",
                 "/images/bluestaffyuk-nationwide-delivery.webp",
                 "/images/blue-staffy-vet-check.webp",
                 "/images/puppies/roman-roman1.webp"):
        assert keep in paths, keep
    # graphics are out — by filename and by alt
    for drop in ("/images/defra-pet-transport-process.webp",               # "process"
                 "/images/blue-staffy-adoption-vs-buying-infographic.webp",
                 "/images/what-health-tests-blue-staffies-need.webp",       # alt "graphic"
                 "/images/1blue-staffy-socialisation-checklist.webp",       # alt "infographic"
                 "/images/sbt-history-heritage-from-pit-to-pet.webp",       # alt "montage"
                 "/images/puppies/ince-card-800.webp",                      # card crop
                 "/images/puppies/ince-portrait-4x5.webp",                  # portrait crop
                 "/images/blue-staffy-uk-official-logo0.png"):
        assert drop not in paths, drop


def test_inventory_items_carry_path_alt_size_and_page_use(inv, london):
    by = {p["path"]: p for p in OS.inventory(ROOT, london)}
    m = by["/images/maggie-blue-staffy-dam-with-pups.webp"]
    assert set(m) >= {"path", "alt", "w", "h", "used_on_page"}
    assert m["w"] > 0 and m["h"] > 0
    assert m["alt"].startswith("A heartwarming photo of Maggie")
    assert {u["slot"] for u in m["used_on_page"]} == {"london-hero", "litter-parents-dam"}
    assert all(p["used_on_page"] == [] for p in inv)              # no board: no page use


def test_stdlib_header_parser_matches_pil(tmp_path):
    for rel in ("images/maggie-blue-staffy-dam-with-pups.webp",
                "images/blue-staffy-uk-official-logo0.png",
                "images/puppies/roman-roman1.webp"):
        f = ROOT / "public" / rel
        assert OS._header_size(f) == OS.image_size(f), rel
    # a minimal PNG and JPEG header, built by hand
    png = tmp_path / "x.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR"
                    + struct.pack(">II", 321, 123) + b"\x08\x02\x00\x00\x00")
    assert OS._header_size(png) == (321, 123)
    jpg = tmp_path / "x.jpg"
    jpg.write_bytes(b"\xff\xd8" + b"\xff\xe0" + struct.pack(">H", 4) + b"\x00\x00"
                    + b"\xff\xc0" + struct.pack(">HBHH", 11, 8, 77, 99) + b"\x03")
    assert OS._header_size(jpg) == (99, 77)
    junk = tmp_path / "x.webp"
    junk.write_bytes(b"not an image")
    assert OS._header_size(junk) is None


# ── fit ─────────────────────────────────────────────────────────────────────────────────
def test_weights_are_pinned():
    assert OS.WEIGHTS == {"per_term": 10, "overlap_max": 50, "intent": 30, "hero": -40,
                          "taken": -50, "portrait": -10, "small": -10}
    assert OS.MIN_WIDTH == 760 and OS.FLOOR == 20


def _photo(path="/images/x.webp", alt="", w=1200, h=800):
    return {"path": path, "alt": alt, "w": w, "h": h, "used_on_page": []}


def test_fit_overlap_and_intent_bonus():
    sec = {"id": "delivery", "heading": "How Will My Puppy Get From Carlisle to London?",
           "entities": [], "keywords": {}}
    van = _photo("/images/nationwide-delivery-van.webp", "A van delivering puppies")
    sofa = _photo("/images/sofa.webp", "A dog asleep on a sofa")
    assert OS.fit(sec, van, {}) == OS.WEIGHTS["per_term"] * 0 + OS.WEIGHTS["intent"]
    assert OS.fit(sec, sofa, {}) == 0
    sec2 = dict(sec, heading="Delivery of Your Puppy by Van")
    assert OS.fit(sec2, van, {}) == 2 * OS.WEIGHTS["per_term"] + OS.WEIGHTS["intent"]
    many = dict(sec, heading="Delivery van nationwide delivering puppies, alpha beta gamma delta")
    big = _photo("/images/a.webp", "delivery van nationwide delivering alpha beta gamma delta")
    assert OS.fit(many, big, {}) == OS.WEIGHTS["overlap_max"] + OS.WEIGHTS["intent"]


def test_fit_subject_matches_section_intent():
    cases = [("Which Puppies Are Available, and Who Are the Parents?", "the dam with her pups"),
             ("What Should a Health Tested Breeder Show You?", "a vet examination"),
             ("Will a Staffy Be Happy Living in London?", "a family with two children"),
             ("What Kennel Club Paperwork Comes Home?", "puppy next to Kennel Club papers")]
    for heading, alt in cases:
        sec = {"heading": heading}
        assert OS.fit(sec, _photo(alt=alt), {}) >= OS.WEIGHTS["intent"], heading


def test_fit_penalties_and_clamp():
    sec = {"heading": "Delivery by van"}
    van = _photo("/images/van.webp", "delivery van")
    base = OS.fit(sec, van, {})
    hero_board = {"sections": [{"id": "top", "shape": "hero",
                                "images": [{"slot": "h", "file": "/images/van.webp"}]}]}
    assert OS.fit(sec, van, hero_board) == max(0, base + OS.WEIGHTS["hero"])
    assert OS.fit(sec, van, {}, taken={"/images/van.webp"}) == max(0, base + OS.WEIGHTS["taken"])
    placed = {"sections": [{"id": "s", "heading": "Elsewhere", "shape": "standard",
                            "images": [{"slot": "e", "file": "/images/van.webp"}]}]}
    assert OS.fit(sec, van, placed) == max(0, base + OS.WEIGHTS["taken"])   # repeat use
    assert OS.fit({"heading": "Elsewhere"}, van, placed) == OS.fit({"heading": "Elsewhere"}, van, {})
    tall = dict(van, w=900, h=1200)
    assert OS.fit(sec, tall, {}) == base + OS.WEIGHTS["portrait"]
    small = dict(van, w=500, h=400)
    assert OS.fit(sec, small, {}) == base + OS.WEIGHTS["small"]
    assert OS.fit({"heading": "x"}, dict(van, w=10, h=40), hero_board, taken={van["path"]}) == 0
    assert all(0 <= OS.fit(sec, p, {}) <= 100 for p in (van, tall, small))


# ── picker ──────────────────────────────────────────────────────────────────────────────
def test_london_proposal(london):
    slots = OS.propose(london, root=ROOT)
    for s in slots:  # read by eye with -s
        print(s["slot"], s["fit"], s["photo"], "|", s["alt"][:50], "|", s["why"])
    assert 4 <= len(slots) <= 5
    secs = [s["section"] for s in slots]
    assert len(secs) == len(set(secs))                               # one per section
    body = {s["id"] for s in OS.eligible_sections(london)}
    assert set(secs) <= body
    assert not body & {"top", "counter", "trust", "contents", "key-takeaways", "newsletter",
                       "enquiry"}
    assert not any(x.startswith(("faq-", "review-")) for x in body)
    photos = [s["photo"] for s in slots]
    assert len(photos) == len(set(photos))                           # no photo twice
    fits = [s["fit"] for s in slots]
    assert fits == sorted(fits, reverse=True) and fits[-1] >= OS.FLOOR
    share = slots[0]
    assert share["share"] == {"w": 1200, "h": 630, "og_style": share["share"]["og_style"]}
    assert share["share"]["og_style"] in ("A", "C")
    assert not any(s.get("share") for s in slots[1:])
    for s in slots:
        assert re.fullmatch(r"orig-[a-z0-9-]+", s["slot"])
        assert s["slot"].startswith("orig-" + s["section"])
        assert s["level"] in ("H2", "H3")
        assert s["why"]
        assert (ROOT / "public" / s["photo"].lstrip("/")).is_file()


def test_slot_ids_name_the_h3():
    sec = {"id": "delivery", "heading": "Getting Home", "shape": "standard",
           "tree": [{"level": 3, "heading": "Can I Collect My Puppy in Carlisle Instead?",
                     "children": []}]}
    assert OS.slot_id(sec, None) == "orig-delivery"
    assert OS.slot_id(sec, sec["tree"][0]) == "orig-delivery-collect-carlisle-instead"


def test_first_use_keeps_served_alt_and_a_repeat_needs_a_new_one(london):
    inv = {p["path"]: p for p in OS.inventory(ROOT, london)}
    maggie = inv["/images/maggie-blue-staffy-dam-with-pups.webp"]
    litter = next(s for s in london["sections"] if s["id"] == "litter-prices")
    other = next(s for s in london["sections"] if s["id"] == "london-life")
    # maggie is the hero and litter-parents-dam already: a third heading is a repeat use
    assert OS.alt_for(london, other, None, maggie).startswith(OS.NEW_ALT)
    # a photo this page never shows keeps its served alt on first use
    van = inv["/images/bluestaffyuk-nationwide-delivery.webp"]
    assert OS.alt_for(london, other, None, van) == van["alt"]
    # a photo already at THIS heading is that same use, not a repeat
    litter_photo = inv["/images/blue-staffy-puppies-uk-litter1.webp"]
    assert OS.alt_for(london, litter, None, litter_photo) == litter_photo["alt"]


def test_n_is_clamped_and_few_sections_give_fewer(london):
    assert 4 <= len(OS.propose(london, n=9, root=ROOT)) <= 5
    assert len(OS.propose(london, n=1, root=ROOT)) == 4
    one = {"meta": london["meta"], "assets": [],
           "sections": [s for s in london["sections"] if s["id"] == "delivery"]}
    assert len(OS.propose(one, root=ROOT)) == 1
    assert "fewer" in OS.block(one, ROOT).lower()


def test_claimed_sections(london):
    slots = OS.propose(london, root=ROOT)
    assert OS.claimed_sections(london, ROOT) == [s["section"] for s in slots]


# ── block ───────────────────────────────────────────────────────────────────────────────
def test_block_markdown(london):
    md = OS.block(london, ROOT)
    assert md.startswith("### Original photos (block 7d)")
    assert "q06" in md and "ORIGINAL" in md
    assert "| Slot | Heading | Photo | Alt | Fit | Why |" in md
    assert "1200×630" in md
    claimed = OS.claimed_sections(london, ROOT)
    line = next(ln for ln in md.splitlines() if ln.startswith("**Sections these photos claim"))
    for sid in claimed:
        assert f"`{sid}`" in line
    assert "infographic plan" in line.lower()


def test_cli(london):
    r = subprocess.run([sys.executable, str(ROOT / "scripts/original_slots.py")],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "usage" in r.stderr.lower() and r.stdout == ""
    r = subprocess.run([sys.executable, str(ROOT / "scripts/original_slots.py"), "no-such-page"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and r.stdout == ""
    r = subprocess.run([sys.executable, str(ROOT / "scripts/original_slots.py"),
                        "blue-staffy-puppies-london"], capture_output=True, text=True)
    assert r.returncode == 0 and "Original photos" in r.stdout


def test_the_generated_slot_module_is_gone():
    assert not (ROOT / "scripts/og_slots.py").exists()


# ── the rule 9 guards generated briefs still need (scripts/generated_briefs.py) ──────────
def test_real_names_cover_dogs_and_whole_person_names():
    pups = json.loads((ROOT / "data/puppies.json").read_text())
    names = GB.real_names()
    assert {p["name"] for p in pups} | {"Maggie", "Jones", "Lisa Bright"} <= names
    assert not {"Bright", "Victoria", "Mark", "Lisa", "Rachel"} & names


def test_unnamed_strips_names_cases_possessives_and_joins():
    n = {"Roman", "Byrd", "Maggie"}
    assert GB.unnamed("Meet Roman and Maggie's Litter", n) == "Meet and Litter"
    assert GB.unnamed("Meet ROMAN Today", n) == "Meet Today"
    assert GB.unnamed("maggie’s pups at home", n) == "pups at home"
    assert GB.unnamed("Roman-Byrd Litter", n) == "Litter"
    assert GB.unnamed("Carlisle — London", n) == "Carlisle — London"
    names = GB.real_names()
    assert GB.unnamed("A Bright Future in London", names) == "A Bright Future in London"
    assert GB.unnamed("Lisa Bright's litter", names) == "litter"


def test_negative_list_is_verbatim_one_line():
    neg = GB.negative_list()
    assert neg.startswith("no text, no watermarks") and neg.endswith("no cluttered background.")
    assert "\n" not in neg and ">" not in neg
