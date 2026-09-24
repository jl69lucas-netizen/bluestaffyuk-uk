"""The system-gaps rules reach the people who build project 5's pages.

Each builder skill carries the one block that names every script and check this build
added, CLAUDE.md points at the packs and at IMAGE-DESIGNS.md, WORKFLOW names the gate and
the generated ontology, and the image-generation key is documented by name only."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILLS = [ROOT / ".claude/skills" / d / "SKILL.md"
          for d in ("bsuk-location-page-builder", "bsuk-comparison-page-builder", "bsuk-blog-post")]
BLOCK = "## Project 5 page rules (system-gaps)"
MUST_NAME = (
    "scripts/keyword_variants.py", "scripts/ontology_seed.py", "scripts/image_candidates.py",
    "scripts/ingest_image.py", "IMAGE-DESIGNS.md", "docs/reference/external-link-library.md",
    "anchor_type", "check:outline", "keyword-variants-missing", "external-links-six-diverse",
    "anchor-type-variation", "anchor-reuse-sitewide", "image-slot-missing",
    "image-generated-unapproved", "data/page-map.json", "block 7b", "scripts/board_approve.py",
    "BSUK_ASSETS_DIR", "outline-not-found", "`other` does not count toward the four",
    "in-copy internal anchor", "nav tiles excepted",
)


def _block(text):
    assert text.count(BLOCK) == 1, f"expected exactly one {BLOCK!r}"
    return text.split(BLOCK, 1)[1]


def test_every_builder_skill_carries_the_block_and_it_names_everything():
    for p in SKILLS:
        body = _block(p.read_text())
        missing = [m for m in MUST_NAME if m not in body]
        assert not missing, f"{p.relative_to(ROOT)} block does not name {missing}"


def test_the_block_comes_after_the_outline_block():
    for p in SKILLS:
        t = p.read_text()
        assert t.index("## Build from the approved outline (system-gaps)") < t.index(BLOCK), p


def test_claude_md_rule_17_points_at_the_packs_and_the_image_file():
    t = (ROOT / "CLAUDE.md").read_text()
    m = re.search(r"^17\. \*\*Project 5 pages.*?(?=^\S|\Z)", t, re.M | re.S)
    assert m, "CLAUDE.md has no working rule 17"
    for name in ("rules/images.md", "rules/links.md", "rules/copy.md", "IMAGE-DESIGNS.md",
                 "scripts/family_rules.py", "BSUK_ASSETS_DIR", "block 7b"):
        assert name in m.group(0), name


def test_workflow_names_the_gate_and_the_generated_ontology():
    t = (ROOT / "docs/reference/WORKFLOW.md").read_text()
    assert "| `data/bsuk-ontology.json` | `scripts/ontology_seed.py` + manual |" in t
    assert "13. **Project 5 page rules (system-gaps)**" in t
    assert "npm run check:outline" in t
    rule = t.split("13. **Project 5 page rules (system-gaps)**", 1)[1]
    assert "refuses approval, and any re-approval, while one FAILs" in rule
    for check in ("image-generated-unapproved", "image-generated-not-ingested",
                  "image-asset-not-ingested", "image-existing-missing", "image-pick-invalid"):
        assert f"`{check}`" in rule, check


def test_the_image_key_is_documented_by_name_only():
    env = (ROOT / ".env.example").read_text().splitlines()
    assert "GEMINI_API_KEY=" in env
    cred = (ROOT / "docs/reference/credentials.md").read_text()
    assert "| `GEMINI_API_KEY` |" in cred
    assert "(system-gaps plan Task 11b)" in cred
    assert "Twelve keys." in cred and "Eleven keys." not in cred


ASSET_ROW_SENTENCE = ("Every image slot has its `assets[]` row (slot, kind, w, h, required) planned "
                      "at boarding; ingest and publish only fill its `file` and `status`.")


def test_the_assets_row_sentence_is_in_image_designs_and_every_builder_item_5():
    """Task 12a item 1: the row publish fills is planned at boarding, and the docs say so."""
    def flat(t):
        return " ".join(t.split())
    s9 = (ROOT / "IMAGE-DESIGNS.md").read_text().split("## 9. Approval Before the Build", 1)[1]
    assert ASSET_ROW_SENTENCE in flat(s9.split("\n## 10.", 1)[0])
    for p in SKILLS:
        item5 = _block(p.read_text()).split("5. **Images.**", 1)[1].split("\n6. ", 1)[0]
        assert ASSET_ROW_SENTENCE in flat(item5), p
        assert "image-asset-row-missing" in item5, p
