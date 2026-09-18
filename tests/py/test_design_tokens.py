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


def test_kit_has_no_hex_literals():
    # The strict-xfail this carried until Task 4 is gone: the kit folder now exists, so the
    # check has something real to say and must stay green for every component added after.
    assert KIT.exists(), "src/components/kit does not exist yet"
    bad = [str(f.relative_to(ROOT)) for f in KIT.rglob("*.astro") if HEX.search(f.read_text())]
    assert not bad, bad


LEGACY_HEX_FILES = (
    "src/components/SiteHeader.astro",
    "src/components/SiteFooter.astro",
    "src/components/ContactForm.astro",
    "src/pages/available-puppies/[slug].astro",
    "src/pages/buy-staffy-puppies-for-sale-uk/index.astro",
    "src/pages/uk-blue-staffy-puppy-buying-guide/index.astro",
)


@pytest.mark.xfail(strict=True, reason=(
    "legacy shell hexes removed in Tasks 6-20; still spelled in "
    + ", ".join(LEGACY_HEX_FILES)))
def test_no_hex_anywhere_in_src_except_tokens():
    """Rule 1: tokens.css is the only file in src/ that spells a colour.

    Strict-xfail because projects 1-2 left hexes in the six files above. The moment
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
