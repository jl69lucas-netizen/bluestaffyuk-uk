"""tokens.css is the only place a colour is spelled. Three layers; every semantic token
resolves to a primitive; every fg/bg pair in contrast.json clears WCAG AA."""
import json, pathlib, re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
TOKENS = ROOT / "src/styles/tokens.css"
GLOBAL = ROOT / "src/styles/global.css"
CONTRAST = ROOT / "data/design/contrast.json"
KIT = ROOT / "src/components/kit"
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
DECL = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")


def layers():
    text = TOKENS.read_text()
    parts = re.split(r"/\*\s*@layer-(primitive|semantic|component)\s*\*/", text)
    # One preamble + three (marker, body) pairs. A fourth marker, or a repeated one,
    # would silently merge two layers and make the layering assertions vacuous.
    assert len(parts) == 7, f"expected exactly 3 layer markers, split gave {len(parts)} parts"
    out = {}
    for i in range(1, len(parts), 2):
        assert parts[i] not in out, f"@layer-{parts[i]} appears more than once"
        out[parts[i]] = dict(DECL.findall(parts[i + 1]))
    assert set(out) == {"primitive", "semantic", "component"}, set(out)
    return out


def resolve(name, L, depth=0):
    assert depth < 6, name
    for layer in ("component", "semantic", "primitive"):
        if name in L[layer]:
            v = L[layer][name].strip()
            m = re.fullmatch(r"var\((--[a-z0-9-]+)\)", v)
            if m:
                return resolve(m.group(1), L, depth + 1)
            # Composite values (--card-border, --seam-gradient) embed one or more
            # var() references; every one of them must resolve too.
            return re.sub(r"var\((--[a-z0-9-]+)\)",
                          lambda mm: resolve(mm.group(1), L, depth + 1), v)
    raise AssertionError(f"{name} is not defined in tokens.css")


def to_rgb(h):
    # A token that resolves to rgb()/oklch()/a gradient has no single colour to measure;
    # say so instead of silently reading the first two characters as a red channel.
    assert re.fullmatch(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", h), (
        f"{h!r} is not a 3- or 6-digit hex colour; contrast.json can only measure those")
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lum(rgb):
    def ch(c): return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(ch, rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(to_rgb(a)), lum(to_rgb(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def test_three_layers_present_and_ordered():
    text = TOKENS.read_text()
    assert text.index("@layer-primitive") < text.index("@layer-semantic") < text.index("@layer-component")


def test_hex_only_in_primitive_layer():
    L = layers()
    for layer in ("semantic", "component"):
        bad = {k: v for k, v in L[layer].items() if HEX.search(v)}
        assert not bad, bad


def test_every_semantic_and_component_token_resolves():
    L = layers()
    for layer in ("semantic", "component"):
        for k in L[layer]:
            v = resolve(k, L)
            assert v and "var(" not in v, (k, v)


def test_global_css_declares_no_colour():
    text = GLOBAL.read_text()
    assert not re.search(r"--color-[a-z0-9-]+\s*:", text)
    assert '@import "./tokens.css"' in text.splitlines()[0] or "@import './tokens.css'" in text.splitlines()[0]


def test_contrast_pairs_clear_aa():
    L = layers()
    pairs = json.loads(CONTRAST.read_text())
    assert len(pairs) >= 10
    failures = []
    for p in pairs:
        # "nontext" is WCAG 1.4.11 (focus rings, UI component boundaries): 3:1, like large text.
        assert p["size"] in ("normal", "large", "nontext"), p
        r = ratio(resolve(p["fg"], L), resolve(p["bg"], L))
        need = 4.5 if p["size"] == "normal" else 3.0
        if r < need:
            failures.append((p["fg"], p["bg"], round(r, 2), need))
    assert not failures, failures


#: Every kit rule that fills a BACKGROUND on an element whose text can be inherited from a
#: dark band, and which must therefore state its own `color`. One entry per rule, because the
#: failure is per-rule: `.hero-aside` shipped a raised fill with no ink of its own and rendered
#: bone text on a near-white card at 1.05:1 inside `.bl-frame-band` (/blue-staffy-uk-breeders/,
#: 8472c06). Neither declaration was wrong alone, which is why a token-pair table could not see
#: it — `--color-text` on `--color-surface-raised` is in CONTRAST and has always passed. What
#: was missing was the component naming the pair at all.
#:
#: The RENDERED proof is the fixture pair tests/render/fixtures/{known_good,known_broken}/
#: kit-hero-aside-ink*.html, measured by `a11y-text-contrast-aa` in the meta gate. This is the
#: cheap source-level guard beside it: a reader deleting the line sees a named test fail
#: without waiting for a browser.
SELF_BEDDED_KIT_RULES = (
    ("src/components/kit/Hero.astro", ".hero-aside"),
)


@pytest.mark.parametrize(("path", "selector"), SELF_BEDDED_KIT_RULES)
def test_a_kit_rule_that_paints_its_own_bed_also_states_its_own_ink(path, selector):
    src = (ROOT / path).read_text(encoding="utf-8")
    start = src.index(selector + " {")
    block = src[start:src.index("}", start)]
    assert "background:" in block, f"{path} {selector} no longer paints a bed — update the list"
    assert "color:" in block, (
        f"{path} {selector} fills a background but states no `color`, so its text takes "
        "whatever the surrounding band set — bone ink on a light card is 1.05:1"
    )


def test_kit_has_no_hex_literals():
    # The strict-xfail this carried until Task 4 is gone: the kit folder now exists, so the
    # check has something real to say and must stay green for every component added after.
    assert KIT.exists(), "src/components/kit does not exist yet"
    bad = [str(f.relative_to(ROOT)) for f in KIT.rglob("*.astro") if HEX.search(f.read_text())]
    assert not bad, bad


LEGACY_HEX_FILES = (
    # SiteHeader.astro and SiteFooter.astro came off this list in Task 20: the shell moved
    # to the SVG lockups, and its inline style attributes became scoped rules over tokens.
    # The why-us page and the buying guide came off it in project 4's sweep: both were
    # rebuilt from an approved board onto the kit and neither spells a colour any more.
    # What is left is the two files project 4 never rebuilt — the shared contact form and
    # the data-driven puppy detail route.
    "src/components/ContactForm.astro",
    "src/pages/available-puppies/[slug].astro",
)


@pytest.mark.xfail(strict=True, reason=(
    "legacy shell hexes removed in Tasks 6-20; still spelled in "
    + ", ".join(LEGACY_HEX_FILES)))
def test_no_hex_anywhere_in_src_except_tokens():
    """Rule 1: tokens.css is the only file in src/ that spells a colour.

    Strict-xfail because projects 1-2 left hexes in the files above. The moment
    Tasks 6-20 finish replacing them this test passes, xfail(strict) turns that pass
    into a failure, and whoever sees it deletes the marker — so the rule starts being
    enforced for real instead of being quietly forgotten.
    """
    bad = sorted(
        str(f.relative_to(ROOT))
        for f in SRC.rglob("*")
        if f.is_file()
        and f.suffix in {".astro", ".css", ".ts", ".tsx", ".js", ".jsx", ".mjs"}
        and f != TOKENS
        and HEX.search(f.read_text())
    )
    assert not bad, bad


RULES = ROOT / "rules/design.md"
INDEX = ROOT / "data/quality/rule-index.json"
SETTINGS = ROOT / "data/settings.json"


def test_design_rules_name_the_new_palette_and_type():
    text = RULES.read_text()
    for old in ("#2D6A4F", "#e8604c", "#faf7f4", "Newsreader", "IBM Plex", "font-lora", "font-sora", "Forest Green", "Clay"):
        assert old not in text, old
    for new in ("--color-brand", "--color-cta", "--color-surface", "Fraunces", "Source Sans 3", "src/styles/tokens.css"):
        assert new in text, new


def test_rule_index_marks_design_system_nine_tested():
    rows = json.loads(INDEX.read_text())
    row = next(r for r in rows["rules"] if r["id"] == "design-system-nine")
    assert row["enforced"] == "test"
    assert row["test"] == "tests/py/test_design_tokens.py"


def test_settings_has_location_label_without_a_city_field_change():
    s = json.loads(SETTINGS.read_text())
    assert s["location_label"] == "Carlisle · Cumbria"


#: Every rule in `CounterStrip` that paints text straight onto the strip's own steel-100 bed.
#: Known Issue 21: the inline arrangement's separator dot was `--color-text-muted` on that bed
#: and measured 4.49:1 (AA wants 4.50) on /kit-preview/, /thank-you-blue-staffy-puppies-journey/
#: and /uk-blue-staffy-breeders-contact/ — and no pair in contrast.json named it, so the token
#: test above could not see it. Each ink named here must be a pair with the bed in
#: contrast.json, which is what makes `test_contrast_pairs_clear_aa` measure it.
COUNTER_BED_INKS = (".kit-counter", ".lbl", ".dot")


def test_counter_inks_are_guarded_pairs_on_the_counter_bed():
    src = (KIT / "CounterStrip.astro").read_text(encoding="utf-8")
    bed = re.search(r"\.kit-counter\s*\{[^}]*?background:\s*var\((--[a-z0-9-]+)\)", src)
    assert bed, "CounterStrip no longer names its bed in `.kit-counter`"
    pairs = {(p["fg"], p["bg"]) for p in json.loads(CONTRAST.read_text())}
    missing = []
    for selector in COUNTER_BED_INKS:
        ink = re.search(re.escape(selector) + r"\s*\{[^}]*?[^-]color:\s*var\((--[a-z0-9-]+)\)", src)
        assert ink, f"{selector} states no ink of its own"
        if (ink.group(1), bed.group(1)) not in pairs:
            missing.append((selector, ink.group(1), bed.group(1)))
    assert not missing, f"add these fg/bg pairs to data/design/contrast.json: {missing}"
