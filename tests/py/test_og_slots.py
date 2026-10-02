"""Block 7d: 4–5 generated OG photo slots per page, the share card first."""
import json
import re
import subprocess
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import og_slots as OG

LONDON = ROOT / "data/boards/blue-staffy-puppies-london.json"


def test_four_to_five_slots_share_card_first():
    # The board's own `intent` is a free label ("Delivery and collection"); a label that is a
    # research-board intent word is taken as it stands, so this fixture keeps the plan's words.
    secs = [{"id": f"s{i}", "heading": f"H{i}", "intent": "transactional" if i < 3 else "info"}
            for i in range(8)]
    slots = OG.propose({"sections": secs, "assets": []}, n=5)
    assert slots[0]["slot"] == "og-share" and slots[0]["w"] == 1200 and slots[0]["h"] == 630
    assert 4 <= len(slots) <= 5
    assert all(s["og_style"] in "ACDEH" for s in slots)


def _sec(sid, heading, intent="", shape="standard"):
    return {"id": sid, "heading": heading, "intent": intent, "shape": shape}


FRAMES = [_sec("top", "Hero", "Hero and opening", "hero"), _sec("counter", "Figures", "", "stats"),
          _sec("trust", "Trust", "", "trust"), _sec("contents", "Contents", "", "dial"),
          _sec("key-takeaways", "Takeaways", "", "takeaways"),
          _sec("review-top", "A Letter", "", "reviews"), _sec("faq-top", "FAQ", "", "faq"),
          _sec("newsletter", "Alerts", "Newsletter"), _sec("enquiry", "Send", "", "form")]


def test_frame_sections_are_skipped():
    body = [_sec(f"b{i}", f"Body {i}") for i in range(5)]
    slots = OG.propose({"sections": FRAMES + body, "assets": []})
    secs = {s["section"] for s in slots[1:]}
    assert secs and secs <= {f"b{i}" for i in range(5)}
    assert OG.eligible({"sections": FRAMES}) == []


def test_transactional_first_then_commercial_in_board_order():
    secs = [_sec("life", "Will a Blue Staffy Be Happy in London?"),
            _sec("health", "What Should a Health Tested Staffy Breeder Show You?"),
            _sec("deposit", "Do I Have to Pay a Deposit Before I See My Puppy?"),
            _sec("temper", "Are Blue Staffies Aggressive?"),
            _sec("prices", "Which Puppies Are Available Now, and What Do They Cost?")]
    slots = OG.propose({"sections": secs, "assets": []}, n=5)
    assert [s["section"] for s in slots[1:]] == ["deposit", "prices", "health", "life"]
    assert OG.intent_of(secs[2]) == "transactional"
    assert OG.intent_of(secs[1]) == "commercial"
    assert OG.intent_of(secs[0]) == "informational"


def test_never_b_and_styles_cycle():
    secs = [_sec(f"b{i}", f"Body {i}") for i in range(8)]
    slots = OG.propose({"sections": secs, "assets": []}, n=5)
    assert [s["og_style"] for s in slots] == ["C", "A", "E", "D", "H"]
    assert "B" not in OG.STYLE_CYCLE
    for s in slots:
        assert s["source"] == "generate" and s["status"] == "proposed"
    assert all((s["w"], s["h"]) == (1408, 768) for s in slots[1:])


def test_negative_list_verbatim_in_prompt_brief():
    neg = OG.negative_list()
    assert neg.startswith("no text, no watermarks") and neg.endswith("no cluttered background.")
    assert "\n" not in neg and ">" not in neg
    secs = [_sec(f"b{i}", f"Body heading {i}") for i in range(5)]
    for s in OG.propose({"sections": secs, "assets": []}):
        assert neg in s["prompt_brief"]
    assert "Body heading 0" in OG.propose({"sections": secs, "assets": []})[1]["prompt_brief"]


def test_share_card_subject_is_hero_alt():
    board = {"sections": [{"id": "top", "heading": "H", "shape": "hero",
                           "images": [{"slot": "x-hero"}]}] + [_sec(f"b{i}", "B") for i in range(4)],
             "assets": [{"slot": "x-hero", "alt": "A blue Staffy dam with her pups."}]}
    share = OG.propose(board)[0]
    assert share["subject"] == "a blue Staffordshire Bull Terrier dam with her puppies, at home"
    assert share["og_style"] == "C" and share["subject"] in share["prompt_brief"]
    nohero = OG.propose({"sections": [_sec("b0", "B")], "assets": []})[0]
    assert nohero["subject"].startswith("NOT FETCHED")


def test_n_is_clamped():
    secs = [_sec(f"b{i}", f"Body {i}") for i in range(10)]
    board = {"sections": secs, "assets": []}
    assert len(OG.propose(board, n=9)) == 5
    assert len(OG.propose(board, n=1)) == 4
    assert len(OG.propose(board, n=4)) == 4
    few = OG.propose({"sections": secs[:1], "assets": []}, n=5)
    assert len(few) == 2
    assert "fewer" in OG.block({"sections": secs[:1], "assets": []}).lower()


def test_block_markdown():
    secs = [_sec(f"b{i}", f"Body {i}") for i in range(6)]
    md = OG.block({"sections": secs, "assets": []})
    assert "| Slot | Where | Size | Framing style | Subject |" in md
    assert "1200×630" in md and "1408×768" in md
    assert "pick-og:" in md and "use" in md and "skip" in md
    assert "402" in md and "rule 11" in md and "STOP 4" in md
    assert "proposal" in md.lower()
    assert "Editorial Split" in md and "Blur-Fill" not in md


def test_cli_bad_input_exits_2():
    r = subprocess.run([sys.executable, str(ROOT / "scripts/og_slots.py")],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "usage" in r.stderr.lower() and r.stdout == ""
    r = subprocess.run([sys.executable, str(ROOT / "scripts/og_slots.py"), "no-such-page"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and r.stdout == ""


def test_london_yields_five_slots():
    board = json.loads(LONDON.read_text())
    slots = OG.propose(board)
    for s in slots:  # printed by eye with -s
        print(s["slot"], s["section"], s["w"], s["h"], s["og_style"], s["subject"][:60])
    assert len(slots) == 5
    assert slots[0]["slot"] == "og-share" and slots[0]["section"] == "top"
    assert slots[0]["subject"] == "a blue Staffordshire Bull Terrier dam with her puppies, at home"
    assert [s["section"] for s in slots[1:]] == ["deposit-viewing", "delivery",
                                                 "litter-prices", "health-tests"]
    r = subprocess.run([sys.executable, str(ROOT / "scripts/og_slots.py"),
                        "blue-staffy-puppies-london"], capture_output=True, text=True)
    assert r.returncode == 0 and "og-share" in r.stdout


def test_no_real_name_in_any_generated_brief():
    """Rule 9: a generated image never names a real dog, person or litter."""
    board = json.loads(LONDON.read_text())
    pups = json.loads((ROOT / "data/puppies.json").read_text())
    forbidden = {p["name"] for p in pups} | {"Maggie", "Jones", "Lisa Bright"}
    assert forbidden <= OG.real_names()
    slots = OG.propose(board)
    for s in slots:
        for field in ("subject", "prompt_brief", "where"):
            for name in forbidden:
                assert not re.search(r"\b%s\b" % name, s[field], re.I), (s["slot"], field, name)
    assert slots[0]["subject"] == "a blue Staffordshire Bull Terrier dam with her puppies, at home"


def test_unnamed_strips_names_from_headings():
    assert OG.unnamed("Meet Roman and Maggie's Litter", {"Roman", "Maggie"}) == "Meet and Litter"
    secs = [_sec("b0", "Is Roman the Right Puppy for You?")] + [_sec(f"b{i}", "B") for i in range(1, 4)]
    s = OG.propose({"sections": secs, "assets": []})[1]
    assert "Roman" not in s["subject"] and "Roman" not in s["prompt_brief"]


def test_person_names_are_whole_phrases_only():
    names = OG.real_names()
    assert "Lisa Bright" in names
    assert not {"Bright", "Victoria", "Mark", "Lisa", "Rachel"} & names
    assert OG.unnamed("A Bright Future in London", names) == "A Bright Future in London"
    assert OG.unnamed("Victoria Station", names) == "Victoria Station"
    assert OG.unnamed("Lisa Bright's litter", names) == "litter"


def test_unnamed_case_possessive_and_joins():
    n = {"Roman", "Byrd", "Maggie"}
    assert OG.unnamed("Meet ROMAN Today", n) == "Meet Today"
    assert OG.unnamed("maggie’s pups at home", n) == "pups at home"
    assert OG.unnamed("Roman-Byrd Litter", n) == "Litter"
    assert OG.unnamed("Carlisle — London", n) == "Carlisle — London"


def test_intent_cues_need_word_boundaries():
    assert OG.intent_of(_sec("a", "A Priceless Companion")) == "informational"
    assert OG.intent_of(_sec("b", "Costume Ideas for Staffies")) == "informational"
    assert OG.intent_of(_sec("c", "What Do Puppies Cost?")) == "transactional"
    assert OG.intent_of(_sec("d", "Prices This Year")) == "transactional"


def test_brief_has_no_question_full_stop_and_sections_need_an_id():
    secs = [_sec(f"b{i}", f"Is This Body {i}?") for i in range(4)] + [{"heading": "No id"}]
    slots = OG.propose({"sections": secs, "assets": []})
    assert all("?." not in s["prompt_brief"] for s in slots)
    assert "Is This Body 0? Negative:" in slots[1]["prompt_brief"]
    assert all(s["section"] for s in slots) and "og-None" not in {s["slot"] for s in slots}


def test_fewer_wording_is_singular_or_plural():
    one = OG.block({"sections": [_sec("b0", "B")], "assets": []})
    assert "Only 1 eligible body section on this board, so 2 slots are proposed" in one
    two = OG.block({"sections": [_sec("b0", "B"), _sec("b1", "C")], "assets": []})
    assert "Only 2 eligible body sections on this board, so 3 slots are proposed" in two
