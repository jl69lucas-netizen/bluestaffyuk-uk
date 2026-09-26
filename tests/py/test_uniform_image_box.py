"""The uniform in-body image box (rules/images.md `uniform-inbody-image-sizing`; CAG §15a;
answer-board batch 2026-09-26-brief-parity-two-decisions-before-project-5, ruling (a)).

rules/images.md has described one box for every in-body image — 760px wide, 1408:768 (16:9),
`object-fit: cover`, the same at every width — since the port, marked `untested`, and no CSS
in src/ defined it: every rebuilt page paints `.bl-img` at its natural ratio, capped at 420px
beside the prose. Rule 17 puts an image under every heading of 30+ project 5 pages, so the
box is built now, once, in src/components/BodyImage.astro:

  box="natural" (default)  .bl-img                 the twelve built pages, frozen until touched
  box="uniform"            .bl-img.sec-img         760px, 1408:768, cover, focal point by prop
  box="tall"               .bl-img.sec-img.og-tall the same box, 4:5 portrait at 900px and below

Every body image keeps `.bl-img`, so a check that looks for in-body images reads one class.

The user's ruling came with a note: "No grey or black bleed on phones; bleeds should be based
on site system design colours". So the box's background is a design-system token (bone,
`--color-surface`), no `.sec-img`/`.og-tall` rule paints a grey, black or transparent
background, and rules/images.md bakes in-body portraits with `--style contain`, never
`--style blurfill`.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
CSS = (ROOT / "src/styles/board-styles.css").read_text(encoding="utf-8")
BODY = (ROOT / "src/components/BodyImage.astro").read_text(encoding="utf-8")
ASSETS = (ROOT / "src/lib/assets.ts").read_text(encoding="utf-8")
BUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))
RULES = (ROOT / "rules/images.md").read_text(encoding="utf-8")


def block(selector_rx, text=CSS):
    """The declarations of the first rule whose selector list matches `selector_rx`."""
    m = re.search(selector_rx + r"[^{]*\{([^}]*)\}", text)
    assert m, f"no CSS rule for {selector_rx}"
    return {k.strip(): v.strip() for k, v in
            (d.split(":", 1) for d in m.group(1).split(";") if ":" in d)}


def media(query):
    """Every `@media (<query>)` block of the stylesheet, joined."""
    found = re.findall(r"@media \(" + re.escape(query) + r"\) \{(.*?)\n  \}", CSS, re.S)
    assert found, f"no @media ({query}) block"
    return "\n".join(found)


def test_the_uniform_box_is_760_wide_16_by_9_and_cropped_not_squashed():
    d = block(r"\n  \.bl-img\.sec-img ")
    assert d["max-width"] == "760px"
    assert d["aspect-ratio"] == "1408 / 768"
    assert d["object-fit"] == "cover"
    assert d["height"] == "auto" and d["width"] == "100%"


def test_the_box_never_takes_the_side_media_cap():
    wide = media("min-width: 900px")
    assert re.search(r"\.bl-media-left \.bl-prose > \.bl-img\.sec-img", wide)
    d = block(r"\.bl-media-right \.bl-prose > \.bl-img\.sec-img", wide)
    assert d["max-width"] == "760px" and d["grid-column"] == "1 / -1"


def test_a_portrait_goes_4_by_5_at_900px_and_below():
    d = block(r"\.bl-img\.sec-img\.og-tall", media("max-width: 900px"))
    assert d["aspect-ratio"] == "4 / 5"


def test_body_image_offers_the_three_boxes():
    assert re.search(r"box\?:\s*'natural'\s*\|\s*'uniform'\s*\|\s*'tall'", BODY)
    assert "box = 'natural'" in BODY
    assert "'sec-img'" in BODY and "'og-tall'" in BODY and "'bl-img'" in BODY
    assert "UNIFORM_SIZES" in BODY and "focal" in BODY


def test_uniform_sizes_matches_the_box():
    m = re.search(r"export const UNIFORM_SIZES = '([^']+)';", ASSETS)
    assert m and m.group(1) == "(max-width: 800px) 100vw, 760px"


def test_the_twelve_built_pages_keep_the_natural_box():
    for slug in BUILT:
        page = ROOT / "src/pages" / slug / "index.astro"
        if slug == "index":
            page = ROOT / "src/pages/index.astro"
        assert not re.search(r'box="(?:uniform|tall)"', page.read_text(encoding="utf-8")), slug


def test_the_rule_is_enforced_by_this_file():
    assert re.search(r"id: uniform-inbody-image-sizing\nenforced: test\n", RULES)
    rows = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))["rules"]
    row = next(r for r in rows if r["id"] == "uniform-inbody-image-sizing")
    assert row["enforced"] == "test" and row["test"] == "tests/py/test_uniform_image_box.py", row


# --- the bleed colour (user ruling 2026-09-26: "No grey or black bleed on phones") ---------

def test_the_box_bleeds_a_design_system_colour():
    d = block(r"\n  \.bl-img\.sec-img ")
    assert re.fullmatch(r"var\(--color-[a-z0-9-]+\)", d.get("background-color", "")), d
    assert d["background-color"] == "var(--color-surface)"


def _bad_background(value):
    v = value.lower()
    if re.search(r"\b(black|grey|gray|transparent)\b", v):
        return True
    if re.search(r"rgba?\(\s*0\s*,\s*0\s*,\s*0\b", v):
        return True
    for h in re.findall(r"#([0-9a-f]{6}|[0-9a-f]{3})\b", v):
        ch = [h[i] * 2 for i in range(3)] if len(h) == 3 else [h[i:i + 2] for i in (0, 2, 4)]
        if ch[0] == ch[1] == ch[2] and int(ch[0], 16) <= 0x99:
            return True  # black (#000) or a neutral grey #111-#999
    return False


def test_no_box_rule_paints_a_grey_black_or_transparent_bleed():
    rules = re.findall(r"([^{}]*)\{([^{}]*)\}", CSS)
    seen = 0
    for selector, body in rules:
        if not re.search(r"\.sec-img|\.og-tall", selector):
            continue
        seen += 1
        for decl in body.split(";"):
            if ":" not in decl:
                continue
            prop, value = (s.strip() for s in decl.split(":", 1))
            if prop in ("background", "background-color"):
                assert not _bad_background(value), (selector.strip(), prop, value)
    assert seen >= 3, "expected the .sec-img / .og-tall rules in board-styles.css"


def test_the_rule_bakes_portraits_with_contain_never_blurfill():
    assert "never `--style blurfill`" in RULES
    assert "--style contain" in RULES
