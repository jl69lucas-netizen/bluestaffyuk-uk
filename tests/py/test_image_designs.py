"""IMAGE-DESIGNS.md is the art-direction source every image agent and skill reads.

It pins: the twelve sections in order, the brand facts against `data/settings.json` and
`src/styles/tokens.css`, breed accuracy for a blue Staffordshire Bull Terrier, the dog-
specific negative list, unique style ids, the slot fields and picks the build gate reads,
the two-pass approval, the board's label map, no source-repo residue, and that every image
consumer cites the file.
"""
import json
import pathlib
import re

import pytest

import image_designs
from image_designs import REQUIRED_SECTIONS, labels, load, render_labels
from marker_check import hits_in
from test_agent_facts import violations

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "IMAGE-DESIGNS.md"


def text():
    return DOC.read_text(encoding="utf-8")


# ── structure ────────────────────────────────────────────────────────────────

def test_every_required_section_is_present_in_order():
    t = text()
    positions = [t.find("\n" + h + "\n") for h in REQUIRED_SECTIONS]
    missing = [h for h, p in zip(REQUIRED_SECTIONS, positions) if p < 0]
    assert missing == [], "IMAGE-DESIGNS.md lost sections: %s" % missing
    assert positions == sorted(positions), "sections are out of order"


def test_og_style_ids_are_exactly_the_named_six_and_unique():
    ids = load()["og_styles"]
    assert ids == ["A", "B", "C", "D", "E", "H"], ids
    assert len(set(ids)) == len(ids)


def test_infographic_style_ids_are_unique_contiguous_and_three_to_five():
    ids = load()["infographic_styles"]
    assert 3 <= len(ids) <= 5, ids
    assert len(set(ids)) == len(ids), "duplicate infographic style id: %s" % ids
    assert ids == ["IG-%d" % n for n in range(1, len(ids) + 1)], ids


def test_style_names_are_unique_and_no_id_is_shared_between_the_two_tables():
    spec = load()
    names = list(spec["og_names"].values()) + list(spec["infographic_names"].values())
    assert len(set(names)) == len(names), names
    assert not set(spec["og_styles"]) & set(spec["infographic_styles"])


def test_slot_fields_carry_the_values_the_board_uses():
    spec = load()
    f = spec["fields"]
    assert f["source"] == ["existing", "assets-folder", "generate", "infographic"]
    assert f["og_style"] == spec["og_styles"]
    assert f["infographic_style"] == spec["infographic_styles"]
    assert {"file", "source_file", "prompt"} <= set(f)
    assert "status" not in f, "approval is the img: pick, not a slot field (§9)"


PICKS = ("`file:/images/<path>`", "`assets:<filename>`", "`og:<style>`", "`og:<style>:<sha12>`",
         "`ig:IG-<n>`", "`ig:IG-<n>:<sha12>`")


@pytest.mark.parametrize("pick", PICKS)
def test_every_pick_form_is_documented(pick):
    assert pick in "\n".join(image_designs._section_lines(text(), 10)), pick


def test_the_label_map_is_written_from_the_document():
    path = ROOT / "data/design/image-styles.json"
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert path.read_text(encoding="utf-8") == render_labels(), (
        "data/design/image-styles.json is stale — run python3 scripts/image_designs.py --write")
    spec = load()
    assert list(on_disk["og"]) == spec["og_styles"]
    assert list(on_disk["infographic"]) == spec["infographic_styles"]
    for group in on_disk.values():
        for i, row in group.items():
            assert row["name"].strip() and row["use"].strip(), i


def test_the_build_gate_uses_the_same_ids():
    """scripts/image_rules.py (the build gate) spells the ids as constants; they must be
    exactly the ids this document names. Skips until that module exists."""
    rules = pytest.importorskip("image_rules")
    spec = load()
    assert list(rules.OG_STYLES) == spec["og_styles"]
    assert list(rules.IG_STYLES) == spec["infographic_styles"]
    assert list(rules.SOURCES) == spec["fields"]["source"]


# ── brand facts and breed accuracy ───────────────────────────────────────────

def test_brand_facts_match_settings_and_tokens():
    s = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
    tokens = (ROOT / "src/styles/tokens.css").read_text(encoding="utf-8")
    t = text()
    for fact in (s["breeder_name"], s["address"]["city"], s["address"]["region"]):
        assert fact in t, fact
    for hexcode in ("#1F3A52", "#5B7C99", "#C9A227", "#F4F1EA"):
        assert hexcode in t, hexcode
        assert hexcode in tokens, "%s is not a locked token" % hexcode


BREED = ("blue Staffordshire Bull Terrier", "muscular, stocky, medium-sized", "broad head",
         "cheek muscles", "short, smooth coat", "Rose or half-pricked ears", "never cropped")


@pytest.mark.parametrize("phrase", BREED)
def test_breed_accuracy_is_stated(phrase):
    assert phrase in text(), phrase


def test_breed_accuracy_is_sourced_to_the_breed_standard_row():
    lib = (ROOT / "docs/reference/external-link-library.md").read_text(encoding="utf-8")
    assert "royalkennelclub.com/breed-standards/terrier/staffordshire-bull-terrier/" in lib
    assert "docs/reference/external-link-library.md" in text()


NEGATIVES = ("no text", "no watermarks", "no cropped ears", "no fighting or aggression imagery",
             "no spiked collar", "no chain collar", "no XL Bully build",
             "no pit-bull-type build", "nothing that could imply a banned type",
             "no clinical or studio lighting")


@pytest.mark.parametrize("ban", NEGATIVES)
def test_negative_list_carries_the_dog_specific_bans(ban):
    # The list is one wrapped blockquote: rejoin it so a ban split across lines still counts.
    neg = " ".join(l.lstrip("> ").strip() for l in image_designs._section_lines(text(), 3))
    assert ban in neg, ban


def test_uniform_sizing_defers_to_the_rule_pack_and_does_not_restate_it_differently():
    rules = (ROOT / "rules/images.md").read_text(encoding="utf-8")
    assert "id: uniform-inbody-image-sizing" in rules
    sec = "\n".join(image_designs._section_lines(text(), 1))
    assert "uniform-inbody-image-sizing" in sec and "rules/images.md" in sec
    for value in ("max-width:760px", "aspect-ratio:1408/768", "95 KB", "-760.webp"):
        assert value in sec and value.replace(" KB", "") in rules.replace(" KB", ""), value


APPROVAL = ("approval.picks[\"img:<slot>\"]", "data/boards/generated/<slug file>/<slot>.webp",
            "sha12", "UNCHANGED", "The build refuses an unapproved generated image",
            "scripts/image_candidates.py", "scripts/image_rules.py", "image-generated-unapproved",
            "image_candidates.ingest_target", "`assets[]`")


@pytest.mark.parametrize("phrase", APPROVAL)
def test_approval_section_describes_the_two_pass_flow(phrase):
    assert phrase in "\n".join(image_designs._section_lines(text(), 9)), phrase


# ── residue ──────────────────────────────────────────────────────────────────
RESIDUE = re.compile(r"(?i)\b(parrots?|midland|benjamin|cites|forest[- ]green|clay|"
                     r"aviary|timneh|congo)\b|#2D6A4F|#e8604c|#faf7f4")


def residue(path):
    return [(n, l.strip()) for n, l in
            enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), 1)
            if RESIDUE.search(l)]


def test_no_source_repo_residue():
    assert residue(DOC) == []
    assert hits_in(DOC) == []
    assert violations(DOC) == []


def test_the_residue_detector_fires(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("fine line\nTeri's Midland aviary, forest green and clay\n", encoding="utf-8")
    assert [n for n, _ in residue(p)] == [2]


# ── consumers ────────────────────────────────────────────────────────────────
CONSUMER_LINE = (
    "> **Image designs:** `IMAGE-DESIGNS.md` (repo root) names the OG framing styles "
    "(§7: A, B, C, D, E, H), the infographic styles (§8: IG-1 to IG-5), the approval rule "
    "(§9: nothing generated is built until the board approves its exact bytes) and the "
    "image-slot fields and picks (§10: `source`, `file`, `source_file`, `og_style`, "
    "`infographic_style`, `prompt`, `img:<slot>`). Read it before choosing, generating, "
    "framing or placing an image; on conflict it wins.")

CONSUMERS = (
    ".claude/agents/bsuk-image-pipeline.md",
    ".claude/agents/bsuk-infographic-builder.md",
    ".claude/skills/image-prompt-generator/SKILL.md",
    ".claude/skills/image-metadata/SKILL.md",
)


@pytest.mark.parametrize("consumer", CONSUMERS)
def test_every_image_consumer_cites_image_designs(consumer):
    lines = (ROOT / consumer).read_text(encoding="utf-8").splitlines()
    assert CONSUMER_LINE in lines, (
        "%s does not carry the IMAGE-DESIGNS.md citation line — append it verbatim" % consumer)


def test_the_consumer_line_names_every_style_id():
    spec = load()
    for i in spec["og_styles"]:
        assert i in CONSUMER_LINE
    assert "IG-1 to IG-%d" % len(spec["infographic_styles"]) in CONSUMER_LINE

