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
    # Only the §10 field table; the pick-grammar table below it is not a field.
    assert list(f) == ["source", "og_style", "infographic_style", "file", "source_file",
                       "prompt"], list(f)
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


# ── a broken document is an error, not a quiet empty list ───────────────────

def broken(tmp_path, old, new):
    """A copy of IMAGE-DESIGNS.md with one exact edit, as a path."""
    t = text()
    assert t.count(old) == 1, old
    p = tmp_path / "IMAGE-DESIGNS.md"
    p.write_text(t.replace(old, new), encoding="utf-8")
    return p


def test_a_missing_required_section_is_an_error(tmp_path):
    p = broken(tmp_path, "\n## 4. Lighting & Focal Length (per scene)\n", "\n## 4. Lighting\n")
    with pytest.raises(ValueError, match=r"IMAGE-DESIGNS\.md.*## 4\. Lighting & Focal Length"):
        load(p)


def test_a_duplicate_og_style_id_is_an_error(tmp_path):
    p = broken(tmp_path, "| `E` | Top-Anchored Cover |", "| `A` | Top-Anchored Cover |")
    with pytest.raises(ValueError, match=r"IMAGE-DESIGNS\.md.*duplicate.*`A`"):
        load(p)


def test_a_duplicate_infographic_style_id_is_an_error(tmp_path):
    p = broken(tmp_path, "| `IG-5` | Route Map |", "| `IG-4` | Route Map |")
    with pytest.raises(ValueError, match=r"IMAGE-DESIGNS\.md.*duplicate.*`IG-4`"):
        load(p)


def test_a_short_og_row_is_an_error(tmp_path):
    p = broken(tmp_path, "| two puppies or a pair, two portraits side by side | yes |",
               "| two puppies or a pair, two portraits side by side |")
    with pytest.raises(ValueError, match=r"IMAGE-DESIGNS\.md.*§7.*`H`.*5 cells"):
        load(p)


def test_a_short_infographic_row_is_an_error(tmp_path):
    p = broken(tmp_path, "| delivery, collection, travel, where | location |",
               "| delivery, collection, travel, where |")
    with pytest.raises(ValueError, match=r"IMAGE-DESIGNS\.md.*§8.*`IG-5`.*6 cells"):
        load(p)


def test_an_empty_style_table_is_an_error(tmp_path):
    t = text()
    rows = [l for l in image_designs._section_lines(t, 8) if l.startswith("| `IG-")]
    p = tmp_path / "IMAGE-DESIGNS.md"
    p.write_text("\n".join(l for l in t.splitlines() if l not in rows) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"IMAGE-DESIGNS\.md.*§8.*no style rows"):
        load(p)


def test_section_lines_stop_after_the_first_matching_section():
    doc = "## 7. Styles\none\n## 8. Next\ntwo\n## 7. Appendix\nthree\n"
    assert image_designs._section_lines(doc, 7) == ["one"]


# ── CLI ──────────────────────────────────────────────────────────────────────

def test_check_reports_in_sync(capsys):
    assert image_designs.main(["--check"]) == 0
    assert "in sync" in capsys.readouterr().out


def test_an_unknown_flag_exits_2():
    with pytest.raises(SystemExit) as e:
        image_designs.main(["--wirte"])
    assert e.value.code == 2


def test_write_and_check_are_mutually_exclusive():
    with pytest.raises(SystemExit) as e:
        image_designs.main(["--write", "--check"])
    assert e.value.code == 2


def test_a_broken_doc_exits_2_with_a_message(tmp_path, monkeypatch, capsys):
    p = broken(tmp_path, "| `E` | Top-Anchored Cover |", "| `A` | Top-Anchored Cover |")
    monkeypatch.setattr(image_designs, "DOC", p)
    assert image_designs.main([]) == 2
    err = capsys.readouterr().err
    assert "duplicate" in err and "IMAGE-DESIGNS.md" in err


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


BREED_FACTS = ROOT / "data/facts/uk-staffordshire-bull-terrier-guide.json"

# Every breed description is the repo's own sourced wording (BREED_FACTS), nothing invented.
BREED = ("muscular", "Medium-sized", "Broad and deep", "pronounced cheek muscles",
         "Short, smooth, and close-lying", "grey/blue", "Rose or half-pricked")

# Instructions, not breed claims: the breed we draw, and a ban on cropped ears.
BREED_INSTRUCTIONS = ("blue Staffordshire Bull Terrier", "never cropped")

UNSOURCED = ("stocky", "compact and balanced", "leggy or bulky", "foreface", "blue-grey")


@pytest.mark.parametrize("phrase", BREED + BREED_INSTRUCTIONS)
def test_breed_accuracy_is_stated(phrase):
    assert phrase in text(), phrase


@pytest.mark.parametrize("phrase", BREED)
def test_every_breed_phrase_is_backed_by_the_breed_facts_file(phrase):
    facts = BREED_FACTS.read_text(encoding="utf-8").lower()
    assert phrase.lower() in facts, "%s is not in %s" % (phrase, BREED_FACTS.name)


@pytest.mark.parametrize("phrase", UNSOURCED)
def test_no_unsourced_breed_wording(phrase):
    assert phrase not in text(), phrase


def test_breed_accuracy_is_sourced_to_the_breed_standard_row():
    lib = (ROOT / "docs/reference/external-link-library.md").read_text(encoding="utf-8")
    assert "royalkennelclub.com/breed-standards/terrier/staffordshire-bull-terrier/" in lib
    assert "docs/reference/external-link-library.md" in text()
    assert "data/facts/uk-staffordshire-bull-terrier-guide.json" in text()


# ── scope ────────────────────────────────────────────────────────────────────
SCOPE = ("This file governs the images on location, comparison and blog-post pages built "
         "from 2026-09-24 on.")


def test_the_scope_binds_the_new_pages_only():
    flat = " ".join(l.lstrip("> ").strip() for l in text().splitlines())
    assert SCOPE in flat
    assert "scripts/family_rules.py" in flat
    assert "keep their images and boards unchanged" in flat


@pytest.mark.parametrize("row", ("| Hub |", "| Puppy card |"))
def test_no_row_for_a_page_type_built_before(row):
    assert row not in text(), row


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

