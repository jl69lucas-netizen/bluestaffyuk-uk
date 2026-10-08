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
import math
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
    found = re.findall(r"@media \(" + re.escape(query) + r"\)\s*\{(.*?)\n\s*\}", CSS, re.S)
    assert found, f"no @media ({query}) block"
    return "\n".join(found)


UNIFORM_RULE = r"\n\s*\.bl-img\.sec-img\s*(?=\{)"
TALL_QUERY = "max-width: 899.98px) and (orientation: portrait"


def test_the_uniform_box_is_760_wide_16_by_9_and_cropped_not_squashed():
    d = block(UNIFORM_RULE)
    assert d["max-width"] == "760px"
    assert d["aspect-ratio"] == "1408 / 768"
    assert d["object-fit"] == "cover"
    assert d["height"] == "auto" and d["width"] == "100%"


def test_the_box_never_takes_the_side_media_cap():
    wide = media("min-width: 900px")
    assert re.search(r"\.bl-media-left \.bl-prose > \.bl-img\.sec-img", wide)
    d = block(r"\.bl-media-right \.bl-prose > \.bl-img\.sec-img", wide)
    assert d["max-width"] == "760px" and d["grid-column"] == "1 / -1"
    # Full width, so it sits directly under its heading (rule 17, image-first), never after
    # the prose as the natural right-hand image does (`order: 99`).
    assert d["order"] == "-1"


def test_a_portrait_goes_4_by_5_below_900px_in_portrait_orientation_only():
    d = block(r"\.bl-img\.sec-img\.og-tall", media(TALL_QUERY))
    assert d["aspect-ratio"] == "4 / 5"
    # 899.98px pairs with the min-width: 900px rules without a 1px overlap; a landscape phone
    # keeps the 16:9 box.
    assert "(max-width: 900px)" not in CSS
    assert not re.search(r"\.og-tall[^{]*\{[^}]*(?:100vw|calc\(50% - 50vw\))", CSS)


def test_body_image_offers_the_three_boxes():
    assert re.search(r"box\?:\s*'natural'\s*\|\s*'uniform'\s*\|\s*'tall'", BODY)
    assert "box = 'natural'" in BODY
    assert "'sec-img'" in BODY and "'og-tall'" in BODY and "'bl-img'" in BODY
    assert "UNIFORM_SIZES" in BODY and "focal" in BODY


def test_uniform_sizes_matches_the_box():
    m = re.search(r"export const UNIFORM_SIZES = '([^']+)';", ASSETS)
    assert m and m.group(1) == "(max-width: 800px) 100vw, 760px"


def test_tall_sizes_fetches_the_whole_file_for_the_4_by_5_strip():
    """A 4:5 box W wide is 1.25W tall; a 1408x768 file covering it is scaled to 1.25W/768, so
    it is 1408 * 1.25 / 768 = 2.29W wide. The phone must fetch ~230vw, not 100vw."""
    m = re.search(r"export const TALL_SIZES = '([^']+)';", ASSETS)
    assert m and m.group(1) == "(max-width: 899.98px) and (orientation: portrait) 230vw, 760px"
    assert round(1408 * 1.25 / 768, 2) == 2.29


def _tall_vw(w, h):
    """The tall box's phone `sizes` in vw for a w x h file: a 4:5 box W wide is 1.25W tall, and
    the file covering it paints max(W, 1.25W * w / h) wide."""
    return math.ceil(100 * max(1.0, 1.25 * w / h))


def test_tall_sizes_follow_the_files_own_ratio():
    """TALL_SIZES is the 16:9 master's case only. A PORTRAIT file in the same 4:5 box paints
    about the box's own width, so 230vw sent the phone the full file for a 295px box
    (Manchester row 13: img-srcset-within-2x, blue-staffy-pups-near-you 870x1080 at 2.92x,
    cheryl-cheryl1 918x1148). BodyImage reads the factor from the asset's own width and height
    through tallSizes(), and the 1408x768 case still spells TALL_SIZES (assets.ts throws if not)."""
    assert _tall_vw(1408, 768) == 230
    assert _tall_vw(870, 1080) == 101 and _tall_vw(918, 1148) == 100
    assert re.search(r"export function tallSizes\(w: number, h: number\): string", ASSETS)
    assert "Math.ceil(100 * Math.max(1, (1.25 * w) / h))" in ASSETS
    assert re.search(r"tallSizes\(1408, 768\) !== TALL_SIZES", ASSETS), "the 16:9 case must spell TALL_SIZES"
    assert "import { BODY_SIZES, UNIFORM_SIZES, tallSizes } from '../lib/assets';" in BODY
    assert re.search(r"box === 'tall'\s*\?\s*tallSizes\(asset\.w, asset\.h\)", BODY)


def test_an_explicit_sizes_prop_overrides_the_default():
    assert re.search(r"const sizes = Astro\.props\.sizes \?\?", BODY)


def test_focal_is_validated_and_dropped_for_the_natural_box():
    assert "/^\\d{1,3}% \\d{1,3}%$/" in BODY
    m = re.search(r"const style = ([^;]+);", BODY)
    assert m and "box !== 'natural'" in m.group(1) and "FOCAL.test(focal)" in m.group(1), m
    assert "undefined" in m.group(1)


def test_the_twelve_built_pages_keep_the_natural_box():
    """London joined data/facts/rebuilt.json (075355ba) and is a project 5 page, which paints
    the uniform box by design (rules/images.md), and is built at src/pages/uk-locations/. "The
    twelve" are the rebuilt pages family_rules does not count as project 5 pages."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import family_rules as FR
    twelve = [s for s in BUILT if not FR.is_new_page(s)]
    assert len(twelve) == len(FR.BUILT_BEFORE_SYSTEM_GAPS), twelve
    for slug in twelve:
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
    d = block(UNIFORM_RULE)
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


def test_the_docs_name_og_tall_as_the_one_exception_and_no_full_bleed_recipe():
    assert re.search(r"`\.og-tall`[^\n]*one sanctioned exception", RULES)
    pup = (ROOT / ".claude/skills/bsuk-puppy-page-builder/SKILL.md").read_text(encoding="utf-8")
    assert "margin-left:calc(50% - 50vw)" not in pup and 'box="tall"' in pup
    assert "never 100vw full-bleed (scrollbar overflow)" in pup
    designs = (ROOT / "IMAGE-DESIGNS.md").read_text(encoding="utf-8")
    assert "**mC** 4:5 blur-fill (matches B) · " not in designs
    assert re.search(r"\*\*mC\*\*[^·]*retired for new pages", designs)


def test_body_sizes_comment_is_current():
    head = ASSETS.split("export const BODY_SIZES", 1)[0].rsplit("/**", 1)[1]
    assert "measures the promise\n * against the box on every one of them" not in head
    assert ".kit-hero .pic" in head


def test_the_rule_bakes_portraits_with_contain_never_blurfill():
    assert "never `--style blurfill`" in RULES
    assert "--style contain" in RULES
