"""build_design_system.py — the repo's tokens, rules, brand and built kit → the artifact.

The Design System type reads a file table, and every shape in it is a shape the page silently
cannot read when it is wrong: a name-to-value token map shows an empty family, a colour value
that is not a hex or an alias of an existing token drops, a preview with no `@dsCard` line on
line 1 loses its group and its height. None of that fails loudly on publish, which is why it
is asserted here instead.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_design_system as D  # noqa: E402

OUT = ROOT / "docs/artifacts/design-system/project"
LIST_FAMILIES = ("color", "spacing", "radius", "shadow")
HEX = re.compile(r"^#(?:[0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})$")
ALIAS = re.compile(r"^\{([A-Za-z0-9][A-Za-z0-9_.-]{0,63})\}$")
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


@pytest.fixture(scope="module")
def tokens():
    return D.tokens_json()


@pytest.fixture(scope="module")
def settings():
    return json.loads((ROOT / "data/settings.json").read_text())


# --------------------------------------------------------------------------- tokens.json

def test_every_family_is_list_shaped(tokens):
    """A map is valid JSON the page cannot read: the family shows empty and its entries leave
    the file at the first token edit. So every family but `type` is `{"tokens": [...]}`."""
    for fam in LIST_FAMILIES:
        assert isinstance(tokens[fam], dict), fam
        assert isinstance(tokens[fam]["tokens"], list) and tokens[fam]["tokens"], fam
        for t in tokens[fam]["tokens"]:
            assert set(t) >= {"name", "value", "usage"}, (fam, t)
    assert tokens["color"]["themes"] == [{"id": "light", "name": "Light"}]
    # `type` is the one family that is not a token list.
    assert set(tokens["type"]) == {"fonts", "families", "groups"}
    assert isinstance(tokens["type"]["groups"], list) and tokens["type"]["groups"]


def test_every_colour_is_a_hex_or_an_alias_of_a_token_that_exists(tokens):
    names = {t["name"] for t in tokens["color"]["tokens"]}
    for t in tokens["color"]["tokens"]:
        v = t["value"]
        if HEX.match(v):
            continue
        m = ALIAS.match(v)
        assert m, f"{t['name']} = {v!r} is neither a hex nor an alias"
        assert m.group(1) in names, f"{t['name']} aliases {m.group(1)}, which is not a token"
        assert m.group(1) != t["name"], f"{t['name']} aliases itself"


def test_the_semantic_layer_really_is_expressed_as_aliases(tokens):
    """Writing the hex twice would let the primitive and the semantic name drift apart."""
    by_name = {t["name"]: t["value"] for t in tokens["color"]["tokens"]}
    assert by_name["color-brand"] == "{color-steel-700}"
    assert by_name["color-cta"] == "{color-brass-500}"
    assert by_name["color-steel-700"] == "#1f3a52"
    assert by_name["color-brass-500"] == "#c9a227"


def test_names_are_unique_across_families_and_legal(tokens):
    names = [t["name"] for fam in LIST_FAMILIES for t in tokens[fam]["tokens"]]
    assert len(names) == len(set(names)), "the families share one --name namespace"
    for n in names:
        assert NAME.match(n), n
    styles = [s["name"] for g in tokens["type"]["groups"] for s in g["styles"]]
    assert len(styles) == len(set(styles)) and all(NAME.match(s) for s in styles)


def test_every_token_has_a_usage_sentence(tokens):
    for fam in LIST_FAMILIES:
        for t in tokens[fam]["tokens"]:
            assert t["usage"].strip() and t["usage"].strip().endswith("."), (fam, t["name"])
    for g in tokens["type"]["groups"]:
        for s in g["styles"]:
            assert s["usage"].strip(), s["name"]


def test_lengths_and_shadows_carry_literals_not_var_references(tokens):
    """Only colours may alias. A component radius therefore carries what its `var()` resolves
    to — `btn-radius` is 50px, not a pointer at `radius-pill`."""
    for fam in ("spacing", "radius", "shadow"):
        for t in tokens[fam]["tokens"]:
            assert "var(" not in t["value"] and not ALIAS.match(t["value"]), (fam, t)
    by_name = {t["name"]: t["value"] for t in tokens["radius"]["tokens"]}
    assert by_name["btn-radius"] == "50px" and by_name["btn-form-radius"] == "12px"
    assert by_name["card-radius"] == "20px"


def test_fonts_are_google_hosted_so_nothing_is_embedded(tokens):
    assert tokens["type"]["fonts"] == []
    fams = tokens["type"]["families"]
    assert "Fraunces" in fams["display"] and "Source Sans 3" in fams["body"]
    for v in fams.values():
        assert len(v) <= 200 and not re.search(r"[;{}<>\\()]", v), v


def test_text_styles_come_from_the_text_scale(tokens):
    """A retyped size is a size that drifts; every style reads `--text-*` and its line height."""
    css = (ROOT / "src/styles/tokens.css").read_text()
    scale = dict(re.findall(r"(--text-[a-z0-9-]+):\s*([^;]+);", css))
    for g in tokens["type"]["groups"]:
        for s in g["styles"]:
            step = next(k for k, v in scale.items()
                        if not k.endswith("--line-height") and v.strip() == s["fontSize"])
            assert float(scale[f"{step}--line-height"]) == s["lineHeight"], s["name"]
            assert s["fontWeight"] in (400, 600, 700), s


def test_composites_and_motion_are_left_out_of_the_grammar(tokens):
    """`card-border`, `seam-gradient` and the motion values have no family the type can read;
    they are documented in README.md instead, and the README section is asserted below."""
    names = {t["name"] for fam in LIST_FAMILIES for t in tokens[fam]["tokens"]}
    assert not names & {"card-border", "seam-gradient", "dur-fast", "dur-base", "ease-out"}
    assert "motion" not in tokens


# --------------------------------------------------------------------------- README.md

def test_readme_names_the_locked_facts_and_the_system(settings):
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    D.FILE_BY_ID.update({r["id"]: r["file"] for r in rows})
    r = D.readme(D.tokens_json(), settings, (ROOT / "rules/design.md").read_text(),
                 [x["id"] for x in rows])
    for s in ("Lisa Bright", "Carlisle · Cumbria", "£1,500", "£1,700", "£500", "refundable",
              "£200", "£350", "Fraunces", "Source Sans 3", "#1f3a52", "#c9a227",
              "PHONE_PLACEHOLDER", "REVIEW_PLACEHOLDER", "FORMSPREE_ID_PLACEHOLDER",
              "SITE_URL_PLACEHOLDER", "LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER",
              "namespace `bsuk`", "no bundle", "src/components/kit/", "dist/kit-preview/",
              "32px", "Clear space", "24 grid"):
        assert s in r, s


def test_readme_names_no_place_the_repo_has_not_locked(settings):
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    D.FILE_BY_ID.update({r["id"]: r["file"] for r in rows})
    r = D.readme(D.tokens_json(), settings, (ROOT / "rules/design.md").read_text(),
                 [x["id"] for x in rows])
    assert "Glasgow" not in r, "the locked location is Carlisle · Cumbria"


def test_readme_carries_the_ten_rules_in_their_current_wording():
    text = (ROOT / "rules/design.md").read_text()
    nine, ten = D.design_rules(text)
    assert nine in text and ten in text, "the rules must be lifted verbatim, never paraphrased"
    assert nine.startswith("**Non-Negotiable Design Rules")
    for n in range(1, 10):
        assert f"{n}. **" in nine, n
    assert ten.startswith("10. **Hero image first in the DOM")


# --------------------------------------------------------------------------- the built tree

def built():
    if not (OUT / "design-system.json").exists():
        pytest.skip("run npm run ds:build first")
    return OUT


def test_every_component_folder_plus_the_cover_each_carries_a_ds_card_line():
    out = built()
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    expected = {D.COMPONENTS[r["id"]]["comp"] for r in rows} | {"Cover"}
    assert {p.name for p in (out / "components").iterdir()} == expected
    # Sixteen components and the cover. Unlike the canvas and the picks board, this
    # artifact documents the CURRENT kit, so it carries project 4's three rows too
    # (spec §3, and §9 amendment 3b for SectionStrip).
    assert len(expected) == 17
    heights = json.loads((ROOT / "data/design/canvas-heights.json").read_text())
    for r in rows:
        spec = D.COMPONENTS[r["id"]]
        d = out / "components" / spec["comp"]
        line = (d / "preview.html").read_text().splitlines()[0]
        assert line.startswith("<!-- @dsCard "), line
        assert f'group="{spec["group"]}"' in line, line
        assert f"height={heights[r['id']]}" in line, line
        assert spec["group"] in D.GROUP_ORDER
        assert (d / "README.md").is_file()


def test_the_cover_folder_stays_bare():
    """A README.md or a .d.ts beside it makes Cover an ordinary component and the system has
    no cover at all."""
    out = built()
    cover = out / "components" / "Cover"
    assert {p.name for p in cover.iterdir()} == {"preview.html"}
    head = (cover / "preview.html").read_text().splitlines()[0]
    assert head == f"<!-- @dsCard height={D.COVER_HEIGHT} -->"
    assert 240 <= D.COVER_HEIGHT <= 360


def test_previews_are_static_self_contained_documents():
    out = built()
    for p in (out / "components").rglob("preview.html"):
        t = p.read_text()
        assert "<script" not in t and "<iframe" not in t, p.name
        assert "<!doctype html>" in t and "fonts.googleapis.com" in t, p.name
        assert len(t.encode()) <= 256 * 1024, (p.name, len(t))


def test_a_preview_that_references_the_sprite_carries_it():
    """`Mark.astro` is a `<use>` at a sprite the layout emits OUTSIDE every section — a
    preview with the `<use>` and no `<symbol>` renders an empty box where the mark should be."""
    out = built()
    for p in (out / "components").rglob("preview.html"):
        t = p.read_text()
        if "<use " in t:
            assert "<symbol " in t, p.name


def test_component_readme_leads_with_the_summary_and_names_its_checks():
    out = built()
    for cid, spec in D.COMPONENTS.items():
        t = (out / "components" / spec["comp"] / "README.md").read_text()
        assert t.startswith(f"# {spec['comp']}\n\n{spec['summary']}"), spec["comp"]
        for head in ("## Props", "## Slots", "## States", "## What holds it up", "## Don'ts"):
            assert head in t, (spec["comp"], head)
        for check in spec["checks"]:
            assert check in t, (spec["comp"], check)


def test_every_component_readme_names_the_file_it_maps_to():
    """Four of the fifteen artifact names are not their filenames — SiteHeader is
    SiteHeaderKit.astro, Buttons is Button.astro, Footer is SiteFooterKit.astro and
    ContactForm is ContactFormKit.astro — so a reader who guesses the file from the heading is
    wrong four times in fifteen. Every README prints its source path, and the four that
    differ say so in words as well."""
    out = built()
    # Read the mapping from its source of truth rather than D.FILE_BY_ID, which the builder
    # populates inside main() and is empty in a test process that only imported the module.
    files = {c["id"]: c["file"] for c in json.loads(
        (pathlib.Path(__file__).resolve().parents[2] / "data/design/components.json").read_text())}
    differing = set()
    for cid, spec in D.COMPONENTS.items():
        file = files[cid]
        t = (out / "components" / spec["comp"] / "README.md").read_text()
        assert f"`src/components/kit/{file}`" in t, (spec["comp"], file)
        if file != f"{spec['comp']}.astro":
            differing.add(spec["comp"])
            assert "The two names differ" in t and f"`{file[:-6]}`" in t, spec["comp"]
    assert differing == {"SiteHeader", "Buttons", "Footer", "ContactForm"}, differing


def test_the_index_has_the_marker_the_namespace_and_the_logo_group():
    out = built()
    idx = json.loads((out / "design-system.json").read_text())
    assert idx["v"] == 3 and idx["layout"] == "files"
    assert idx["createdOnFiles"]["v"] == 1 and idx["createdOnFiles"]["at"]
    assert idx["title"] == "BlueStaffyUK" and idx["namespace"] == "bsuk"
    assert idx["libraries"] == [], "there is no bundle: the kit is Astro, rendered on the server"
    assert idx["groups"] == ["Logos"]
    assert idx["docs"] == {"readme": "project/README.md", "sections": []}
    assert idx["lastChange"]["via"] == "Claude Code (scripts/build_design_system.py)"
    assert idx["lastChange"]["by"] and idx["lastChange"]["at"]


def test_the_index_refuses_to_invent_a_blob_id():
    """An index naming a blob the store does not hold renders a broken tile and says nothing
    about why. Every `files` entry must carry a real id, and the upload list is printed instead."""
    out = built()
    idx = json.loads((out / "design-system.json").read_text())
    group = idx["assetGroups"]["Logos"]
    assert group["name"] == "Logos" and group["tile"] == "l"
    assert set(group["order"]) == set(group["files"])
    for name, rec in group["files"].items():
        assert rec["blob"] and rec["name"] == name and rec["size"] > 0
        assert rec["type"] == "image/svg+xml"
    uploaded = json.loads((ROOT / "data/design/design-system-assets.json").read_text())
    assert set(group["files"]) == {n for n, r in uploaded.get("assets", {}).items() if r.get("blob")}


def test_the_five_lockups_are_copied_with_a_group_readme_that_names_the_mono_ink():
    out = built()
    logos = out / "assets" / "Logos"
    for name in D.LOGO_FILES:
        assert (logos / name).is_file(), name
        src = ROOT / ("public/favicon.svg" if name == "favicon.svg" else f"public/brand/{name}")
        assert (logos / name).read_bytes() == src.read_bytes(), name
    readme = (logos / "README.md").read_text()
    # An SVG served as an upload gets no `currentColor` context, so the group README is the
    # only place the mono lockup's ink can be named.
    assert "currentColor" in readme and "logo-mono.svg" in readme
    assert "32px" in readme


def test_the_publish_manifest_lists_every_file_within_the_tool_limit():
    out = built()
    import design_system_publish_manifest as M
    rel = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    assert len(rel) <= M.LIMIT
    assert "design-system.json" in rel and "tokens.json" in rel and "README.md" in rel
