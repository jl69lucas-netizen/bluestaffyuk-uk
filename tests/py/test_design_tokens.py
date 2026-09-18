"""tokens.css is the only place a colour is spelled. Three layers; every semantic token
resolves to a primitive; every fg/bg pair in contrast.json clears WCAG AA."""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
TOKENS = ROOT / "src/styles/tokens.css"
GLOBAL = ROOT / "src/styles/global.css"
CONTRAST = ROOT / "data/design/contrast.json"
KIT = ROOT / "src/components/kit"
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
DECL = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")


def layers():
    text = TOKENS.read_text()
    parts = re.split(r"/\*\s*@layer-(primitive|semantic|component)\s*\*/", text)
    out = {}
    for i in range(1, len(parts), 2):
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
        r = ratio(resolve(p["fg"], L), resolve(p["bg"], L))
        need = 4.5 if p["size"] == "normal" else 3.0
        if r < need:
            failures.append((p["fg"], p["bg"], round(r, 2), need))
    assert not failures, failures


def test_kit_has_no_hex_literals():
    if not KIT.exists():
        return
    bad = [str(f.relative_to(ROOT)) for f in KIT.glob("*.astro") if HEX.search(f.read_text())]
    assert not bad, bad
