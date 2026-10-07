"""Manchester's page-board record (the Manchester page run, Phase F Task 35; page-run row 10).

`data/boards/blue-staffy-puppies-manchester-uk.json` is written from the outline approved at STOP 2
(`data/outlines/blue-staffy-puppies-manchester-uk.json`, hash 593992436b4531ab), which is never
edited. What must hold before the breeder sees it at STOP 3:

  * it validates, as a city board of a location page that draws on the whole density pool;
  * its 22 sections are the outline's, in order, with the outline's headings, keywords, words,
    `why` and `why_source`;
  * every section names one of MANCHESTER's own kit components (city_components.KIT_OF_VARIANT,
    the `manchester/*` rows), never one of London's, and carries a refresh delta whose note is
    its own among the sections that share a component;
  * its tuple is the one the frozen picks imply (board_approve.city_tuple);
  * every link of `docs/research/manchester-page-run/links-plan.md` is on it, typed and
    Link-First, and links 8 and 9 are HELD while the deposit-order correction has not landed;
  * the nine thin FAQ wordings (docs/research/manchester-components/faq-rewordings.md §§1-9) carry
    their Recommended rewording, each with an `outline_changes_since_stop2` row naming the old
    wording, its source and the check date, and no FAQ question is a near-copy of a live one;
  * every image slot is filled from the page's own, the served or the breeder's images, never
    another city's, and keeps a served alt on first use (working rules 11 and 17);
  * the rendered board carries the blocks the plan names, Greater Manchester's boroughs in 3d and
    no London borough, and no other city's photo in block 7.
"""
import json
import pathlib
import re
import sys
from collections import defaultdict

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import board_approve as BA  # noqa: E402
import check_city_canvas as C  # noqa: E402
import image_candidates as IC  # noqa: E402
import keyword_metrics as KM  # noqa: E402
import neighbourhoods as NB  # noqa: E402
import original_slots as OS  # noqa: E402
import pageboard as PB  # noqa: E402
from city_components import KIT_OF_VARIANT  # noqa: E402

SLUG = "blue-staffy-puppies-manchester-uk"
OUTLINE = json.loads((ROOT / f"data/outlines/{SLUG}.json").read_text(encoding="utf-8"))
LINKS_PLAN = (ROOT / "docs/research/manchester-page-run/links-plan.md").read_text(encoding="utf-8")
BOARD_HTML = ROOT / f"docs/artifacts/boards/{SLUG}.html"
MANCHESTER_KITS = {v for k, v in KIT_OF_VARIANT.items() if k.startswith("manchester/")}
LONDON_KITS = {v for k, v in KIT_OF_VARIANT.items() if k.startswith("london/")}
CHECK_DATE = "2026-10-07"

#: The nine thin outline wordings and their Recommended rewordings (faq-rewordings.md §§1-9).
REWORDED = {
    "How Much Is Your Deposit?": ("How Much Deposit Reserves One of Your Puppies?", 1),
    "Do You Deliver Puppies Across the UK?": ("Which Parts of the UK Do You Deliver Puppies To?", 2),
    "Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?":
        ("Was Each Parent DNA Tested for L-2-HGA as Well as HC-HSF4?", 3),
    "How Much Does Each Blue Staffy Puppy Cost?": ("How Much Will the Blue Staffy Puppy I Choose Cost?", 4),
    "Can My Blue Staffy Puppy Be Delivered to My Home?": ("Is Home Delivery an Option for My Blue Staffy Puppy?", 5),
    "Should I See the Mother With Her Puppy Before Money Changes Hands?":
        ("Is It Wise to See the Mother and Puppy Together Before Money Changes Hands?", 6),
    "Is Blue Staffy Aggressive?": ("Is a Blue Staffy an Aggressive Dog by Nature?", 7),
    "Are Blue Staffies Good Pets?": ("Are Blue Staffies Good Pets for an Ordinary Household?", 8),
    "Is a Staffordshire Bull Terrier Able to Live in a Flat?":
        ("Will a Staffordshire Bull Terrier Be Happy Living in a Flat?", 9),
}


@pytest.fixture(scope="module")
def board():
    return PB.load_board(SLUG)       # validates against schemas/board.schema.json


def _h2(row):
    return next((h for h in row["headings"] if h["level"] == 2), None)


def _flat(nodes, key):
    out = []
    for n in nodes:
        out.append((n["level"], n[key]))
        out += _flat(n.get("children") or [], key)
    return out


def _other_cities():
    """Every city of data/locations.json but Manchester, as the image tools read them
    (original_slots.cities: the national 'UK' row is not a city)."""
    return [c for c in OS.cities(ROOT) if c != "Manchester"]


def _is_faq(row):
    return bool(row.get("faq"))


# ── schema and family ───────────────────────────────────────────────────────────────────────
def test_the_record_validates_as_a_city_location_board(board):
    assert board["meta"]["slug"] == SLUG
    assert board["meta"]["layout_type"] == "city"
    assert board["meta"]["page_type"] == "location"
    assert board["density_pool"] == "all"
    # STOP 3 (2026-10-07): the breeder approved on the board; the approval must still match
    # the record, so an edit after it shows here as a stale approval.
    assert board["approval"] is not None, "approved at STOP 3, 2026-10-07"
    assert PB.approval_matches(board), "the record changed after its STOP 3 approval"


def test_the_outline_it_stands_on_is_approved_and_unedited(board):
    import outline_matrix as OM
    assert OM.approval_refusal(SLUG) is None
    assert OUTLINE["approval"]["record_hash"] == "593992436b4531ab"
    paths = {s["path"]: s["fetched"] for s in board["meta"]["sources"]}
    assert "593992436b4531ab" in paths[f"data/outlines/{SLUG}.json"]
    assert "3583bdc08a7bd609" in paths[f"data/research-boards/{SLUG}.json"]
    for need in ("docs/research/manchester-page-run/links-plan.md",
                 "docs/research/manchester-page-run/keyword-variants.json",
                 "docs/research/manchester-page-run/free-keyword-signals.json",
                 f"data/design/city-picks/{SLUG}.json", "data/settings.json", "data/puppies.json",
                 "data/price-matrix.json"):
        assert need in paths, need
    assert any(p.endswith("Assets/Images") for p in paths)


# ── copied from the outline ─────────────────────────────────────────────────────────────────
def test_the_sections_are_the_outlines_22_in_order(board):
    rows = OUTLINE["sections"]
    assert [s["n"] for s in board["sections"]] == [int(r["n"]) for r in rows] == list(range(1, 23))


def test_every_heading_is_the_outlines_word_for_word(board):
    assert board["sections"][0]["heading"] == OUTLINE["h1"]
    assert board["h1"]["variants"][board["h1"]["recommended"]] == OUTLINE["h1"]
    for sec, row in zip(board["sections"], OUTLINE["sections"]):
        h2 = _h2(row)
        if h2 is None:
            continue
        assert sec["heading"] == h2["text"], row["n"]
        if _is_faq(row):
            continue
        want = _flat(h2.get("children") or [], "text")
        assert _flat(sec["tree"], "heading") == want, row["n"]


def test_keywords_words_why_and_why_source_are_unchanged(board):
    for sec, row in zip(board["sections"], OUTLINE["sections"]):
        kw = row["keywords"]
        assert sec["keywords"]["primary"] == kw.get("primary", []), row["n"]
        placed = {k for v in sec["keywords"].values() for k in v}
        assert placed == set(kw.get("primary", [])) | set(kw.get("secondary", [])), row["n"]
        w = sec["words"]
        assert w["min"] <= row["words"] <= w["max"] and abs((w["min"] + w["max"]) / 2 - row["words"]) <= 1, row["n"]
        if row["why"] != "—":
            assert sec["why_source"] == row["why_source"], row["n"]
            assert row["why"].startswith(sec["why"].rstrip("…")), row["n"]
            assert row["why"] in sec["intent"], row["n"]


def test_the_four_extra_keyword_types_are_placed_somewhere(board):
    for t in ("variation", "related", "cooccurring", "similar"):
        assert any(s["keywords"].get(t) for s in board["sections"]), t


# ── components and refresh ──────────────────────────────────────────────────────────────────
def test_every_section_mounts_a_manchester_component_and_none_of_londons(board):
    for sec in board["sections"]:
        assert sec.get("component") in MANCHESTER_KITS, (sec["id"], sec.get("component"))
        assert sec["component"] not in LONDON_KITS
        assert not sec.get("styles"), "a city section names its component and offers no style trio"


def test_video_and_puppy_cards_are_not_mounted(board):
    picks = PB.load_city_picks()[SLUG]
    assert picks["picks"]["video"] == picks["picks"]["puppy-cards"] == "none"
    assert PB.city_unused_mounted(board, picks) == []
    assert not [s for s in board["sections"] if s["shape"] in ("video", "puppies")]


def test_every_section_carries_its_own_refresh_delta(board):
    notes = defaultdict(list)
    for sec in board["sections"]:
        assert sec.get("refresh"), sec["id"]
        notes[sec["component"]].append(sec["refresh"]["note"])
    for comp, ns in notes.items():
        assert len(ns) == len(set(ns)), f"{comp}: two sections share a refresh note"


# ── tuple ───────────────────────────────────────────────────────────────────────────────────
def test_the_tuple_is_the_one_the_frozen_picks_imply(board):
    t = board["tuple"]
    assert t == BA.city_tuple(board, t)
    assert t["newsletter"] == {"after": "guarantee", "variant": "B"}
    guarantee = next(s for s in board["sections"] if s["id"] == "guarantee")
    assert guarantee["n"] == 15 and next(s for s in board["sections"] if s["n"] == 16)["id"] == "newsletter"


# ── links ───────────────────────────────────────────────────────────────────────────────────
def _plan_internal():
    """[(row, href, anchor, anchor_type)] for the 23 rows of links-plan.md's internal table."""
    out = []
    for line in LINKS_PLAN.splitlines():
        m = re.match(r"^\| (\d+) \| [^|]+ \| `([^`]+)`[^|]* \| ([^|]+) \| (\w[\w-]*)", line)
        if m:
            out.append((int(m.group(1)), m.group(2), m.group(3).strip(), m.group(4)))
    return out


def _plan_external():
    out = []
    for line in LINKS_PLAN.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) > 6 and cells[1].startswith("https://"):
            out.append((cells[1], cells[4], cells[5]))
    return out


def _board_links(board, kind):
    return [(s["id"], l) for s in board["sections"] for l in s["links"][kind]]


def test_every_internal_link_of_the_links_plan_is_on_the_board(board):
    plan = _plan_internal()
    assert len(plan) == 23
    links = _board_links(board, "internal")
    for row, href, anchor, typ in plan:
        hit = [l for _, l in links if l["href"] == href and l["anchor"] == anchor]
        assert len(hit) == 1, (row, href, anchor)
        l = hit[0]
        assert l["anchor_type"] == typ and l.get("sentence_start") is True and not l.get("nav"), row
        assert f"links-plan.md: Row {row} " in l["why"], row


def test_every_external_link_of_the_links_plan_is_on_the_board(board):
    plan = _plan_external()
    assert len(plan) == 7 and len({h for h, _, _ in plan}) == 6
    links = _board_links(board, "external")
    for href, anchor, typ in plan:
        hit = [l for _, l in links if l["href"] == href and l["anchor"] == anchor]
        assert len(hit) == 1, (href, anchor)
        assert hit[0]["anchor_type"] == typ and hit[0]["library_row"]


def test_every_link_is_typed_and_every_fragment_names_a_section(board):
    ids = {s["id"] for s in board["sections"]}
    for kind in ("internal", "external"):
        for sid, l in _board_links(board, kind):
            assert l.get("anchor_type"), (sid, l["href"])
            if l["href"].startswith("#"):
                assert l["href"][1:] in ids, l["href"]


def test_links_8_and_9_are_held_while_the_deposit_order_fix_has_not_landed(board):
    pages = ["src/pages/buy-blue-staffy-puppies-uk/index.astro", "src/pages/blue-staffy-pup-sale-uk/index.astro"]
    pat = re.compile(r"deposit comes after you have met|video call before the deposit|"
                     r"on a video call we offer before the deposit")
    landed = not any(pat.search((ROOT / p).read_text(encoding="utf-8")) for p in pages)
    links = {l["href"]: l for _, l in _board_links(board, "internal")}
    for href in ("/blue-staffy-pup-sale-uk/", "/buy-blue-staffy-puppies-uk/"):
        held = "HELD: built only once the deposit-order correction (STOP 2 q05 a) has landed on both pages" in links[href]["why"]
        assert held != landed, href


# ── FAQ wordings ────────────────────────────────────────────────────────────────────────────
def test_the_nine_faq_nodes_carry_the_recommended_wordings(board):
    qs = PB.faq_block_questions(board)
    assert len(qs) == 20 == len(set(qs))
    outline_qs = [n["text"] for r in OUTLINE["sections"] if _is_faq(r) for n in _h2(r)["children"]]
    assert qs == [REWORDED.get(q, (q,))[0] for q in outline_qs]
    assert not set(REWORDED) & set(qs)


def test_each_rewording_has_a_change_row_naming_old_wording_source_and_date(board):
    rows = board["outline_changes_since_stop2"]
    assert len(rows) == len(REWORDED)
    by_old = {}
    for c in rows:
        node = PB.outline_change_node(board, c)
        assert node is not None and node["heading"] == c["heading"]
        q = PB._FAQ_NODE_Q.match(node["intent"]).group(1)
        old = next(o for o, (new, _) in REWORDED.items() if new == q)
        by_old[old] = c
        sec = REWORDED[old][1]
        assert f'"{old}"' in c["reason"], old
        assert CHECK_DATE in c["reason"]
        assert ("STOP 2 q03 (b)" if sec <= 3 else "Task 34 near-copy check, 2026-10-07") in c["reason"], old
        assert "not yet picked" in c["reason"]
    assert set(by_old) == set(REWORDED)


def test_no_faq_question_is_a_near_copy_or_a_collision(board):
    if not (ROOT / "dist" / "index.html").is_file():
        pytest.skip("run npm run -s build first")
    live = PB.live_headings()
    assert PB.board_near_copy_hits(board, live) == []
    assert PB.faq_hits(board, live) == []


# ── images ──────────────────────────────────────────────────────────────────────────────────
def test_the_hero_and_every_body_h2_and_h3_have_a_filled_slot_and_an_asset_row(board):
    rows = {a["slot"]: a for a in board["assets"]}
    slots = list(IC.iter_slots(board))
    assert len(slots) == len(rows) == 27
    for sec, node, img in slots:
        a = rows[img["slot"]]
        assert img["source"] in ("existing", "assets-folder", "infographic"), img["slot"]
        if img["source"] == "existing":
            assert img["file"] == a["file"] and a["status"] == "baked", img["slot"]
            assert (ROOT / "public" / img["file"].lstrip("/")).is_file(), img["file"]
        assert a["alt"], img["slot"]
    assert not PB.duplicate_alts(board)


def test_no_image_names_another_city(board):
    others = _other_cities()
    for a in board["assets"]:
        if a["file"]:
            assert not OS.cities_named(a["file"].replace("-", " "), others), a["file"]
        assert not OS.cities_named(a["alt"], others), a["slot"]


def test_only_the_hero_alt_carries_the_primary_keyword(board):
    primary = board["brief"]["primary_keyword"]
    carry = [a["slot"] for a in board["assets"] if KM.phrase_count(primary, a["alt"])]
    assert carry == ["manchester-hero"]


def test_a_served_photo_keeps_its_served_alt_on_first_use_and_a_repeat_gets_a_new_one(board):
    served = C.served_alts()
    seen = {}
    for sec, node, img in IC.iter_slots(board):
        if img.get("source") != "existing":
            continue
        a = next(x for x in board["assets"] if x["slot"] == img["slot"])
        name = img["file"][len("/images/"):]
        if name.startswith("puppies/"):
            continue
        if name not in seen:
            seen[name] = {a["alt"]}
            if name in served:
                assert a["alt"] in served[name], img["slot"]
        else:
            assert a["alt"] not in seen[name], img["slot"]
            seen[name].add(a["alt"])


# ── the rendered board ──────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def html():
    if not BOARD_HTML.is_file():
        pytest.skip("run python3 scripts/build_page_board.py blue-staffy-puppies-manchester-uk first")
    return BOARD_HTML.read_text(encoding="utf-8")


def _block(html, bid):
    """The rendered block `bid`: from its data-id to the next block's."""
    i = html.index(f'data-id="{bid}"')
    j = html.find(' data-id="', i + 10)
    return html[i:j if j > 0 else len(html)]


def test_the_board_carries_the_blocks_the_plan_names(html):
    for title in ("1b. How Google reads this page", "3d. Neighbourhoods", "4c. Term density against competitors",
                  "4d. FAQ placement", "5c. What competitors say that we do not", "7b. Rules for new pages",
                  "7c. Infographics", "7d. Original photos", "8a.", "8b.", "8c."):
        assert title in html, title


def test_block_3d_names_greater_manchester_boroughs_and_no_london_borough(html):
    text = re.sub(r"<[^>]+>", " ", _block(html, "3d"))
    assert OS.cities_named(text, list(NB.GM_BOROUGHS)), "no Greater Manchester borough in 3d"
    assert not OS.cities_named(text, list(NB.BOROUGHS) + [NB.CITY]), "a London borough in 3d"


def test_block_7_offers_no_other_city_photo(html):
    others = _other_cities()
    seen = 0
    for bid in ("7", "7b", "7c", "7d"):
        block = _block(html, bid)
        srcs = set(re.findall(r"/images/[A-Za-z0-9_./-]+\.(?:webp|png|jpe?g)", block))
        seen += len(srcs)
        for src in srcs:
            assert not OS.cities_named(src.replace("-", " "), others), (bid, src)
    assert seen, "block 7 shows no image at all: the check examined nothing"


# ── block 7c: photos first, an infographic only where none fits (gap G17) ──────────────────
#: The four proposed infographic slots whose heading an original photo already fills, and the
#: image slot that fills it. papers-checklist stays an infographic: no truthful photo of a
#: puppy's papers exists (kc-registered-staffy-puppies.webp is lessons 7's false image).
SKIP_RECOMMENDED = {"deposit-steps": "deposit-h2", "health-tests-checklist": "health-tests-h2",
                    "litter-figures": "litter-prices", "travel-route": "travel-h2"}


def test_photo_covered_infographic_slots_are_recommended_skip(board):
    plan = {p["slot"]: p for p in PB.ig_plan(board)}
    assert set(plan) == set(SKIP_RECOMMENDED) | {"papers-checklist"}
    photos = {img["slot"]: ((node or sec).get("heading"), img) for sec, node, img in IC.iter_slots(board)}
    for slot, photo_slot in SKIP_RECOMMENDED.items():
        assert plan[slot]["recommended"] == "skip", slot
        heading, img = photos[photo_slot]
        assert heading == plan[slot]["node"], (slot, heading)
        assert img["kind"] == "photo" and img["source"] == "existing", photo_slot
        assert img["file"].rsplit("/", 1)[-1] in plan[slot]["recommended_why"], slot
    assert plan["papers-checklist"]["recommended"] is None
    # A recommendation is a proposal: every slot is still asked at STOP 3.
    assert set(PB.ig_slots_required(board)) == {f"ig:{s}" for s in plan}


def test_block_7c_pre_checks_skip_on_the_four_photo_covered_slots(html):
    block = _block(html, "7c")
    for slot in SKIP_RECOMMENDED:
        assert f'name="pick-ig:{slot}" value="skip" checked>' in block, slot
    assert 'name="pick-ig:papers-checklist" value="skip">' in block
    # The record proposes nothing for papers-checklist; the one style ticked is the breeder's
    # own STOP 3 pick (comic, 2026-10-07), carried from the approval.
    ticked = re.findall(r'name="pick-ig:papers-checklist" value="([a-z]+)" checked>', block)
    assert ticked == [PB.load_board(SLUG)["approval"]["picks"]["ig:papers-checklist"]] == ["comic"]


# ── Task 36 Step 3: the plain summaries, from a sidecar outside the record hash ─────────────
SUMMARY_BLOCKS = ("1b. How Google reads this page", "3d. Neighbourhoods", "3e. Changed since STOP 2",
                  "4c. Term density against competitors", "4d. FAQ placement",
                  "5c. What competitors say that we do not", "7b. Rules for new pages", "7c. Infographics")


def test_the_summaries_sidecar_covers_the_eight_blocks_in_plain_bullets(html):
    import board_style as BS
    import build_page_board as BPB
    side = BPB.load_summaries(SLUG)
    assert side is not None, "no sidecar at data/boards/summaries/<slug>.json"
    titles = re.findall(r'<script type="text/markdown" data-title="([^"]+)"', html)
    titles = [t.replace("&amp;", "&") for t in titles]
    assert BS.validate_summaries(side, titles) == []
    assert set(side["sections"]) == set(SUMMARY_BLOCKS)
    for t, entry in side["sections"].items():
        assert 4 <= len(entry["bullets"]) <= 6, t
    # The rendered board carries it, and the record's hash is untouched by it.
    assert 'id="board-summaries"' in html
    data = json.loads(re.search(r'<script type="application/json" id="board-summaries">(.*?)</script>',
                                html, re.S).group(1))
    assert data == side
    assert f"record <code>{PB.record_hash(PB.load_board(SLUG))[:12]}" in html or \
        PB.record_hash(PB.load_board(SLUG)) in html
