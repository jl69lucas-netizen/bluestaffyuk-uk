# Design System and Component Variations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the BlueStaffyUK design tokens, the Staffy-head logo in four lockups, thirteen kit components in five variants each on a published design canvas, the user's picks as data with the losers pruned, and a Design System artifact for projects 4–6.

**Architecture:** Tokens live in one Tailwind 4 `@theme` file and are the only place a colour is spelled. Kit components in `src/components/kit/` take a `variant` prop during the project and render on one hidden route; a Python builder turns that route's built HTML into `.dc.html` artboards for the Design-type canvas, a companion picks board records the user's choices in its shared database, and a pull script writes them to `data/design/picks.json`, after which the variants are pruned and the logo lockups, favicons and Design System artifact are generated from the picked head and tokens.

**Tech Stack:** Astro 6.3.8, Tailwind 4.3 (`@theme`), `astro:assets`, Python 3 + pytest + Playwright (existing harness), Pillow + cairosvg (favicons), Artifact tool (Design type, Design System type, plain Artifact with `db`).

**Spec:** `docs/superpowers/specs/2026-09-18-design-system-design.md` (Artifact https://claude.ai/artifact/T9UYfQtidvt6iN6NzrqWy9). **Canvas:** https://claude.ai/artifact/TAc7sSMqtcANRq9ujEQ5uR (empty; filled in Task 17).

**Working rules for every task.** Branch `design-system`, cut from `foundation`. Run from `/Users/apple/Downloads/BSUK`. Never push, there is no remote. Every commit ends with the trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` — write that model name exactly, not your own. Do not spell any colour hex outside `src/styles/tokens.css` and the spec. Do not write `Glasgow` into anything new (Known Issue 16); the kit shows `Carlisle · Cumbria` via `settings.location_label`. Never name a hosting provider. Never put the words `parrot`, `bird`, `CAG` or `cag-` into a file; `python3 scripts/marker_check.py` must print `0 problems` before every commit. Before every commit also run `python3 -m pytest tests/py -q -x` (fast, ~80 s) and check it is green.

**Kit conventions (added 2026-09-18 after the Task 5 quality review — binding for Tasks 6–15).**
The full list is the comment block at the top of `src/components/kit/_registry.ts`; in short:
(1) never open a second `<main>`, BaseLayout owns it; (2) focus rings use `outline: 3px solid var(--kit-ring)` — `--kit-ring` is set in `global.css` and switched by `.on-inverse` / `[data-surface="inverse"]`; a component with its own dark fill sets `--kit-ring: var(--color-focus-on-inverse)` on itself; (3) components that sit on both bone and steel surfaces take colour from `currentColor` or a context variable, never a fixed `var(--color-brand)`; (4) `interface Props extends HTMLAttributes<'…'>` from `astro/types`, destructure the named props (including `class` and any attribute you also set literally, e.g. `type`), spread `...rest` on the root, apply `class:list`; (5) content via slots for multi-region components, props for variant/size/data; (6) scoped `<style>` rules go inside `@layer components { … }`; (7) register the component in `REGISTRY` in `_registry.ts` with its demo fixtures (the route renders `entry.demo ?? [{}]` per variant and has NO per-component branches — the `byId` object and the `c.id === 'buttons'` ternary in the Task 5 text are superseded; `wrap: 'sticky'` replaces the Task 6 instruction to wrap the header on the route); (8) `tests/py/test_design_components.py::test_built_sections_render_five_distinct_variants` already asserts five distinct renderings per component in dist — add any component-specific dist assertion next to it; (9) the first time a second component needs a shared primitive (card shell, medal, rule, chip), move it to `src/styles/kit.css` (import from `global.css`) instead of copying.

---

## File structure

| Path | Responsibility |
|---|---|
| `src/styles/tokens.css` | the `@theme` block: primitive → semantic → component tokens; the only file with hex colours |
| `src/styles/global.css` | imports `tokens.css`; layout variables and base layer only |
| `data/design/contrast.json` | every fg/bg token pair the kit uses, with `size` |
| `data/design/components.json` | the thirteen component ids, titles, board widths, in canvas order |
| `data/design/picks.json` | written by the pull script; the thirteen picks |
| `data/design/canvas-assets.json` | source image path → canvas `/_blob/` url |
| `data/design/artifacts.json` | URLs of canvas, picks board, Design System |
| `src/components/kit/*.astro` | the thirteen components (with `variant` until Task 19) |
| `src/components/kit/Mark.astro` | the Staffy-head SVG, five variants until Task 19 |
| `src/pages/design-canvas/index.astro` | hidden noindex route mounting every variant; deleted in Task 19 |
| `src/assets/puppies/`, `src/assets/hero/` | images moved from `public/images/` for `astro:assets` |
| `public/brand/logo-{horizontal,stacked,icon,mono}.svg` | the four lockups |
| `public/favicon.svg`, `favicon-32.png`, `apple-touch-icon.png`, `icon-512.png` | rendered from `logo-icon.svg` |
| `scripts/build_design_canvas.py` | dist section → `.dc.html` artboards + `canvas.json` |
| `scripts/build_picks_board.py` | the picks board HTML (db capability) |
| `scripts/pull_design_picks.py` | inbox JSON → `picks.json` |
| `scripts/prune_variants.py` | removes non-picked branches and the `variant` prop |
| `scripts/build_favicons.py` | `logo-icon.svg` → PNG/SVG favicons |
| `scripts/build_design_system.py` | tokens + picks + brand → Design System artifact files |
| `tests/py/test_design_tokens.py` | token layering, contrast, no stray hex |
| `tests/py/test_design_components.py` | components.json ↔ kit files ↔ route |
| `tests/py/test_design_canvas_build.py` | artboard builder on a fixture section |
| `tests/py/test_design_picks.py` | picks.json shape; post-prune invariants |
| `tests/py/test_brand_assets.py` | lockups and favicons |
| `tests/render/fixtures/known_good/kit-*.html`, `known_broken/kit-*.html` | fixture pairs for the promoted checks |
| `rules/design.md` | rules 1, 2, 5 rewritten |
| `docs/reports/design-system-gate-report.md`, `render-baseline-project3.md` | close-out |

---

### Task 1: Branch, spec artifact, `components.json`

**Files:**
- Create: `data/design/components.json`
- Test: `tests/py/test_design_components.py`

- [ ] **Step 1: Confirm the branch and clean tree**

Run: `git branch --show-current && git status --short | wc -l`
Expected: `design-system` and `0`.

- [ ] **Step 2: Write the failing test**

```python
# tests/py/test_design_components.py
"""data/design/components.json is the one list of kit components; everything else
(the kit folder, the canvas route, the picks board, picks.json) is checked against it."""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "data/design/components.json"
KIT = ROOT / "src/components/kit"
IDS = ["site-header", "hero", "buttons", "puppy-card", "trust-strip", "counter-strip",
       "info-card", "testimonial", "faq", "contact-form", "page-nav", "footer", "section-divider"]


def load():
    return json.loads(COMPONENTS.read_text())


def test_thirteen_components_in_spec_order():
    rows = load()
    assert [r["id"] for r in rows] == IDS


def test_each_row_has_file_title_width():
    for r in load():
        assert re.fullmatch(r"[A-Z][A-Za-z]+Kit?\.astro|[A-Z][A-Za-z]+\.astro", r["file"]), r
        assert r["title"] and isinstance(r["title"], str)
        assert r["board_width"] in (640, 1280), r


def test_kit_file_exists_for_each_row():
    missing = [r["file"] for r in load() if not (KIT / r["file"]).exists()]
    assert not missing, missing
```

- [ ] **Step 3: Run it to see it fail**

Run: `python3 -m pytest tests/py/test_design_components.py -q`
Expected: 3 failed (`FileNotFoundError` on `components.json`).

- [ ] **Step 4: Write `components.json`**

```json
[
  {"id": "site-header",     "file": "SiteHeaderKit.astro",  "title": "1 · Site header + nav",     "board_width": 1280},
  {"id": "hero",            "file": "Hero.astro",            "title": "2 · Hero",                  "board_width": 1280},
  {"id": "buttons",         "file": "Button.astro",          "title": "3 · Buttons",               "board_width": 640},
  {"id": "puppy-card",      "file": "PuppyCard.astro",       "title": "4 · Puppy card",            "board_width": 640},
  {"id": "trust-strip",     "file": "TrustStrip.astro",      "title": "5 · Trust strip",           "board_width": 1280},
  {"id": "counter-strip",   "file": "CounterStrip.astro",    "title": "6 · Stat / counter strip",  "board_width": 1280},
  {"id": "info-card",       "file": "InfoCard.astro",        "title": "7 · Content / info card",   "board_width": 640},
  {"id": "testimonial",     "file": "Testimonial.astro",     "title": "8 · Testimonial",           "board_width": 1280},
  {"id": "faq",             "file": "Faq.astro",             "title": "9 · FAQ accordion",         "board_width": 640},
  {"id": "contact-form",    "file": "ContactFormKit.astro",  "title": "10 · Contact form",         "board_width": 640},
  {"id": "page-nav",        "file": "PageNav.astro",         "title": "11 · Breadcrumb + in-page nav", "board_width": 640},
  {"id": "footer",          "file": "SiteFooterKit.astro",   "title": "12 · Footer",               "board_width": 1280},
  {"id": "section-divider", "file": "SectionDivider.astro",  "title": "13 · Section divider",      "board_width": 1280}
]
```

- [ ] **Step 5: Run the tests**

Run: `python3 -m pytest tests/py/test_design_components.py -q`
Expected: 2 passed, 1 failed (`test_kit_file_exists_for_each_row` — the kit does not exist yet; Tasks 4–16 make it pass one file at a time). Mark that test `@pytest.mark.xfail(strict=True, reason="kit lands in Tasks 4-16")` for now; Task 16 removes the marker.

- [ ] **Step 6: Commit**

```bash
git add data/design/components.json tests/py/test_design_components.py
git commit -m "design: components.json — the thirteen kit components in canvas order

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Tokens and the contrast test

**Files:**
- Create: `src/styles/tokens.css`, `data/design/contrast.json`
- Modify: `src/styles/global.css:1-8`
- Test: `tests/py/test_design_tokens.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/py/test_design_tokens.py
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
            return resolve(m.group(1), L, depth + 1) if m else v
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
```

- [ ] **Step 2: Run it to see it fail**

Run: `python3 -m pytest tests/py/test_design_tokens.py -q`
Expected: 5 failed, 1 passed (`test_kit_has_no_hex_literals` passes vacuously).

- [ ] **Step 3: Write `tokens.css`**

```css
/* src/styles/tokens.css — BlueStaffyUK design tokens (project 3, spec §3).
   The ONLY file in src/ that spells a colour. Layer markers are read by
   tests/py/test_design_tokens.py; keep them and keep the order. */
@theme {
  /* @layer-primitive */
  --color-steel-900: #14202B;
  --color-steel-700: #1F3A52;
  --color-steel-500: #5B7C99;
  --color-steel-300: #8FA3B8;
  --color-steel-100: #E4EAF1;
  --color-brass-600: #A8861C;
  --color-brass-500: #C9A227;
  --color-brass-200: #EFE3B4;
  --color-bone-100: #F4F1EA;
  --color-bone-50: #FAF8F3;
  --color-white: #FFFFFF;
  --color-ink: #1B2430;
  --color-ink-2: #46566B;
  --color-ink-3: #5E6B7A;
  --color-rule: #DAD6CC;
  --color-ok: #2F6B4F;
  --color-warn: #9A4A2A;

  --font-display: "Fraunces", Georgia, "Times New Roman", serif;
  --font-body: "Source Sans 3", system-ui, -apple-system, "Segoe UI", sans-serif;

  --text-xs: 13px;   --text-xs--line-height: 1.4;
  --text-sm: 15px;   --text-sm--line-height: 1.5;
  --text-base: 17px; --text-base--line-height: 1.65;
  --text-lg: 20px;   --text-lg--line-height: 1.5;
  --text-xl: 24px;   --text-xl--line-height: 1.3;
  --text-2xl: 30px;  --text-2xl--line-height: 1.2;
  --text-3xl: 36px;  --text-3xl--line-height: 1.12;
  --text-4xl: 44px;  --text-4xl--line-height: 1.08;

  --space-1: 4px;  --space-2: 8px;   --space-3: 12px; --space-4: 16px;
  --space-5: 24px; --space-6: 32px;  --space-7: 40px; --space-8: 48px;
  --space-9: 56px; --space-10: 64px; --space-11: 80px; --space-12: 96px;

  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --radius-pill: 50px;

  --shadow-card: 0 2px 8px rgba(20, 32, 43, 0.08), 0 8px 24px rgba(20, 32, 43, 0.06);
  --shadow-lift: 0 6px 16px rgba(20, 32, 43, 0.12), 0 16px 40px rgba(20, 32, 43, 0.10);

  --dur-fast: 120ms;
  --dur-base: 200ms;
  --ease-out: cubic-bezier(0.2, 0.7, 0.2, 1);

  /* @layer-semantic */
  --color-surface: var(--color-bone-100);
  --color-surface-raised: var(--color-white);
  --color-surface-inverse: var(--color-steel-700);
  --color-surface-deep: var(--color-steel-900);
  --color-text: var(--color-ink);
  --color-text-muted: var(--color-ink-3);
  --color-text-on-inverse: var(--color-bone-100);
  --color-brand: var(--color-steel-700);
  --color-brand-soft: var(--color-steel-100);
  --color-brand-mid: var(--color-steel-500);
  --color-cta: var(--color-brass-500);
  --color-cta-ink: var(--color-steel-900);
  --color-cta-hover: var(--color-brass-600);
  --color-cta-soft: var(--color-brass-200);
  --color-link: var(--color-steel-700);
  --color-link-on-inverse: var(--color-brass-200);
  --color-border: var(--color-rule);
  --color-focus: var(--color-brass-500);

  /* @layer-component */
  --btn-radius: var(--radius-pill);
  --btn-form-radius: var(--radius-md);
  --card-radius: var(--radius-lg);
  --card-border: 1px solid var(--color-border);
  --hdr-bg: var(--color-surface-raised);
  --counter-bed: var(--color-bone-50);
  --seam-gradient: linear-gradient(90deg, var(--color-steel-700), var(--color-brass-500));
}
```

- [ ] **Step 4: Write `contrast.json`**

```json
[
  {"fg": "--color-text",            "bg": "--color-surface",         "size": "normal"},
  {"fg": "--color-text",            "bg": "--color-surface-raised",  "size": "normal"},
  {"fg": "--color-text-muted",      "bg": "--color-surface",         "size": "normal"},
  {"fg": "--color-text-muted",      "bg": "--color-surface-raised",  "size": "normal"},
  {"fg": "--color-text-on-inverse", "bg": "--color-surface-inverse", "size": "normal"},
  {"fg": "--color-text-on-inverse", "bg": "--color-surface-deep",    "size": "normal"},
  {"fg": "--color-cta-ink",         "bg": "--color-cta",             "size": "normal"},
  {"fg": "--color-cta-ink",         "bg": "--color-cta-hover",       "size": "normal"},
  {"fg": "--color-link",            "bg": "--color-surface",         "size": "normal"},
  {"fg": "--color-link",            "bg": "--color-surface-raised",  "size": "normal"},
  {"fg": "--color-link-on-inverse", "bg": "--color-surface-inverse", "size": "normal"},
  {"fg": "--color-brand",           "bg": "--color-brand-soft",      "size": "normal"},
  {"fg": "--color-brand",           "bg": "--color-cta-soft",        "size": "normal"},
  {"fg": "--color-cta",             "bg": "--color-surface-inverse", "size": "large"},
  {"fg": "--color-cta",             "bg": "--color-surface-deep",    "size": "large"},
  {"fg": "--color-brand-mid",       "bg": "--color-surface",         "size": "large"}
]
```

- [ ] **Step 5: Move the two existing tokens out of `global.css`**

Replace lines 1–8 of `src/styles/global.css` (the `@import`, `@source` and the `@theme { --color-ink; --color-rule }` block) with:

```css
@import "./tokens.css";
@import "tailwindcss" source(none);
@source "../../src/**/*.{astro,mdx,md,ts,tsx,js,jsx}";
```

Also change `body { … font: 17px/1.65 system-ui, … }` in `@layer base` to `font: var(--text-base)/var(--text-base--line-height) var(--font-body);` and add `h1,h2,h3,h4,h5,h6 { font-family: var(--font-display); }` after it. Keep every other line.

- [ ] **Step 6: Run the tests, the build, and the harness meta**

Run: `python3 -m pytest tests/py/test_design_tokens.py -q && npm run build 2>&1 | tail -3`
Expected: `6 passed`; build ends `49 page(s) built`. If `test_contrast_pairs_clear_aa` names `--color-brand-mid` on `--color-surface`, darken `--color-steel-500` to `#4F6E8B` and re-run; do not delete the pair.

- [ ] **Step 7: Commit**

```bash
git add src/styles/tokens.css src/styles/global.css data/design/contrast.json tests/py/test_design_tokens.py
git commit -m "tokens: three-layer @theme, contrast proven by test

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Rewrite design rules 1, 2, 5; fact-lint bans; placeholder token; `location_label`

**Files:**
- Modify: `rules/design.md` (rule 1, 2, 5 text), `data/quality/rule-index.json` (row `design-system-nine`), `tests/py/test_agent_facts.py:56` (`BANNED`), `scripts/placeholder_check.py:35`, `data/settings.json`, `tests/py/test_data_files.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/py/test_design_tokens.py`:

```python
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
```

- [ ] **Step 2: Run to see them fail**

Run: `python3 -m pytest tests/py/test_design_tokens.py -q`
Expected: 3 failed, 6 passed. (Check `rule-index.json`'s top-level shape first with `python3 -c "import json;d=json.load(open('data/quality/rule-index.json'));print(type(d), list(d)[:3] if isinstance(d,dict) else d[0])"`; if it is a bare list, change `rows["rules"]` to `rows` in the test.)

- [ ] **Step 3: Rewrite rule 1, 2 and 5 in `rules/design.md`**

Replace the body of rule 1 with:

```
1. **Colors:** Every colour is a token in `src/styles/tokens.css`; no hex anywhere else in `src/`. Roles: `--color-brand` (header, headings, bands), `--color-cta` with `--color-cta-ink` (all CTAs/buttons), `--color-surface` (page surface), `--color-surface-inverse` (dark bands), `--color-link`. AA contrast for every text/background pair is asserted by `tests/py/test_design_tokens.py` from `data/design/contrast.json`; add the pair before you use it.
```

Replace the body of rule 2 with:

```
2. **Type:** `--font-display` (**Fraunces**) for ALL headlines H1–H6, `--font-body` (**Source Sans 3**) for ALL body, labels and buttons, applied globally in `src/styles/global.css`. Never hard-code `font-family` on an element; use the tokens.
```

Replace rule 5 with: `5. **Shadows:** Always \`--shadow-card\` / \`--shadow-lift\` (steel-tinted \`rgba(20,32,43,…)\`). Never neutral grey, never a hand-written shadow.`

Keep rules 3, 4, 6, 7, 8, 9 verbatim except: in rule 3 replace `clay pill` with `\`--color-cta\` pill (\`--btn-radius\`)`; in rule 4 replace `green header band` with `\`--color-brand\` header band`; in rule 7 replace `green \`#2D6A4F\` check-circle` with `\`--color-ok\` check-circle`. Change the front-matter of the `design-system-nine` block from `enforced: untested` to `enforced: test`.

- [ ] **Step 4: Update the rule ledger, fact lint, placeholder gate, settings**

In `data/quality/rule-index.json` set the `design-system-nine` row to `"enforced": "test", "test": "tests/py/test_design_tokens.py"` (keep every other key). Run `python3 -m pytest tests/py/test_rules_index.py -q`; if it asserts on the count of `untested` rows, lower that expected number by one in the test with a comment naming this task.

In `tests/py/test_agent_facts.py` add to `BANNED`: `"#2D6A4F", "#e8604c", "#faf7f4", "Newsreader", "IBM Plex"`.

In `scripts/placeholder_check.py` line 35 add `"REVIEW_PLACEHOLDER"` to `PLACEHOLDERS`, and add a sentence to the module docstring: `REVIEW_PLACEHOLDER stands in a testimonial slot for which no real review exists in the repo (project 3 kit).`

In `data/settings.json` add `"location_label": "Carlisle · Cumbria",` after `"breeder_name"`. Leave `address` untouched (Known Issue 16 owns it).

- [ ] **Step 5: Run the affected suites**

Run: `python3 -m pytest tests/py/test_design_tokens.py tests/py/test_rules_index.py tests/py/test_agent_facts.py tests/py/test_placeholder_check.py tests/py/test_data_files.py -q && python3 scripts/marker_check.py | tail -1`
Expected: all passed; `0 problems`. If `test_agent_facts.py` now fails on a skill or agent that quotes the old hexes, edit that file to the token names (that is the point of the ban) and list the file in the commit message.

- [ ] **Step 6: Commit**

```bash
git add rules/design.md data/quality/rule-index.json tests/py scripts/placeholder_check.py data/settings.json .claude
git commit -m "rules: design rules 1/2/5 on tokens; old palette banned; REVIEW_PLACEHOLDER; location_label

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: The mark (`Mark.astro`) and the kit conventions

**Files:**
- Create: `src/components/kit/Mark.astro`, `src/components/kit/_variant.ts`
- Test: `tests/py/test_design_components.py` (add)

- [ ] **Step 1: Write the failing test**

Append to `tests/py/test_design_components.py`:

```python
VARIANT_TS = KIT / "_variant.ts"
MARK = KIT / "Mark.astro"


def test_variant_helper_exports_the_five_letters():
    t = VARIANT_TS.read_text()
    assert "export type Variant = 'a' | 'b' | 'c' | 'd' | 'e'" in t
    assert "export const VARIANTS" in t


def test_mark_has_five_variants_stroke_currentcolor_and_title():
    t = MARK.read_text()
    for v in "abcde":
        assert f"variant === '{v}'" in t, v
    assert 'stroke="currentColor"' in t
    assert "<title>" in t
    assert "fill=\"#" not in t and "stroke=\"#" not in t
```

- [ ] **Step 2: Run to see it fail**

Run: `python3 -m pytest tests/py/test_design_components.py -q -k "variant or mark"`
Expected: 2 failed.

- [ ] **Step 3: Write `_variant.ts`**

```ts
// src/components/kit/_variant.ts — shared by every kit component during project 3.
// Task 19 (prune) deletes this file together with the `variant` prop.
export type Variant = 'a' | 'b' | 'c' | 'd' | 'e';
export const VARIANTS: readonly Variant[] = ['a', 'b', 'c', 'd', 'e'] as const;
export const isVariant = (v: unknown): v is Variant => typeof v === 'string' && (VARIANTS as readonly string[]).includes(v);
```

- [ ] **Step 4: Write `Mark.astro`**

```astro
---
// src/components/kit/Mark.astro — the BlueStaffyUK mark: a front-facing Staffordshire Bull
// Terrier head, stroke paths on a 64-unit grid, `currentColor` so it takes any token.
// Five variants until the pick (spec §4); Task 19 keeps one.
import type { Variant } from './_variant';
interface Props { variant?: Variant; size?: number; title?: string; class?: string }
const { variant = 'a', size = 48, title = 'BlueStaffyUK mark', class: cls = '' } = Astro.props;
const sw = variant === 'd' ? 4 : 3;
---
<svg class={cls} width={size} height={size} viewBox="0 0 64 64" fill="none" stroke="currentColor"
  stroke-width={sw} stroke-linejoin="round" stroke-linecap="round" role="img" aria-labelledby={`mark-${variant}-t`}>
  <title id={`mark-${variant}-t`}>{title}</title>
  {variant === 'c' && <circle cx="32" cy="32" r="30" stroke-width="2" />}
  {/* skull: broad, wide cheeks, short muzzle */}
  <path d="M15 31c0-11 8-19 17-19s17 8 17 19v6c0 9-8 16-17 16S15 46 15 37v-6z" />
  {/* rose ears folded back */}
  <path d="M15 31l-5-13 11 5" />
  <path d="M49 31l5-13-11 5" />
  {/* eyes */}
  <path d="M25 33h2.5M36.5 33h2.5" stroke-width={sw + 1} />
  {/* nose and muzzle */}
  <path d="M29 41h6l-3 3z" fill="currentColor" stroke="none" />
  {variant === 'e'
    ? <path d="M26 46c2 4 10 4 12 0M30 47v3M34 47v3" />
    : <path d="M27 46c2 3 8 3 10 0" />}
  {variant === 'b' && <path d="M17 50c4 3 26 3 30 0" stroke-width="2.5" />}
  {variant === 'b' && <circle cx="32" cy="53" r="2.5" fill="currentColor" stroke="none" />}
</svg>
```

- [ ] **Step 5: Run the tests**

Run: `python3 -m pytest tests/py/test_design_components.py -q -k "variant or mark"`
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add src/components/kit/_variant.ts src/components/kit/Mark.astro tests/py/test_design_components.py
git commit -m "kit: Mark.astro — the Staffy-head mark in five variants; variant helper

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: The canvas route and the first two components (Button, SectionDivider)

**Files:**
- Create: `src/pages/design-canvas/index.astro`, `src/components/kit/Button.astro`, `src/components/kit/SectionDivider.astro`
- Modify: `scripts/sitemap_check.py` (confirm noindex rule), `tests/py/test_design_components.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/py/test_design_components.py`:

```python
ROUTE = ROOT / "src/pages/design-canvas/index.astro"
DIST_ROUTE = ROOT / "dist/design-canvas/index.html"


def test_route_is_noindex_and_mounts_every_component_variant():
    t = ROUTE.read_text()
    assert 'noindex' in t
    for r in load():
        stem = r["file"].removesuffix(".astro")
        assert f"import {stem} from" in t, stem


def test_built_route_has_sixty_five_sections():
    if not DIST_ROUTE.exists():
        import pytest; pytest.skip("run npm run build first")
    html = DIST_ROUTE.read_text()
    secs = re.findall(r'<section[^>]*data-component="([a-z-]+)"[^>]*data-variant="([a-e])"', html)
    assert len(secs) == 65, len(secs)
    assert {c for c, _ in secs} == set(IDS)
    assert 'name="robots" content="noindex' in html
```

- [ ] **Step 2: Run to see it fail**

Run: `python3 -m pytest tests/py/test_design_components.py -q -k route`
Expected: 1 failed, 1 skipped.

- [ ] **Step 3: Write `Button.astro`**

```astro
---
// src/components/kit/Button.astro — the five button treatments (spec §5 #3).
// a pill/cta · b pill/outline · c pill/inverse · d form submit (md radius) · e text link with arrow
import type { Variant } from './_variant';
interface Props { variant?: Variant; href?: string; type?: 'button' | 'submit'; label: string; class?: string }
const { variant = 'a', href, type = 'button', label, class: cls = '' } = Astro.props;
const base = 'kit-btn inline-flex items-center justify-center gap-2 font-semibold no-underline transition-colors';
const byVariant: Record<Variant, string> = {
  a: 'rounded-[var(--btn-radius)] bg-cta text-cta-ink px-6 py-3 text-base hover:bg-cta-hover',
  b: 'rounded-[var(--btn-radius)] border-2 border-brand text-brand px-6 py-[10px] text-base hover:bg-brand-soft',
  c: 'rounded-[var(--btn-radius)] bg-surface-inverse text-text-on-inverse px-6 py-3 text-base hover:bg-surface-deep',
  d: 'rounded-[var(--btn-form-radius)] bg-cta text-cta-ink px-5 py-3 text-base w-full hover:bg-cta-hover',
  e: 'text-link underline-offset-4 hover:underline px-0 py-2 text-base',
};
const classes = `${base} ${byVariant[variant]} ${cls}`;
---
{href
  ? <a href={href} class={classes} data-variant={variant}>{label}{variant === 'e' && <svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>}</a>
  : <button type={type} class={classes} data-variant={variant}>{label}</button>}
<style>
  .kit-btn { transition-duration: var(--dur-base); transition-timing-function: var(--ease-out); min-height: 44px; }
  .kit-btn:focus-visible { outline: 3px solid var(--color-focus); outline-offset: 2px; }
</style>
```

- [ ] **Step 4: Write `SectionDivider.astro`**

```astro
---
// src/components/kit/SectionDivider.astro — section dividers built around the mark (spec §5 #13).
// a mark centred on a rule · b two brass rules with the stacked lockup between · c mark with a fading rule
// d seam gradient bar with the mark in a bone medallion · e slim rule, mark at the left margin
import type { Variant } from './_variant';
import Mark from './Mark.astro';
interface Props { variant?: Variant; markVariant?: Variant; class?: string }
const { variant = 'a', markVariant = 'a', class: cls = '' } = Astro.props;
---
<div class={`kit-divider kit-divider-${variant} ${cls}`} role="separator" aria-hidden="true" data-variant={variant}>
  {variant === 'a' && <><span class="rule" /><span class="medal"><Mark variant={markVariant} size={40} title="" /></span><span class="rule" /></>}
  {variant === 'b' && <><span class="rule brass" /><span class="stack"><Mark variant={markVariant} size={44} title="" /><span class="word">BlueStaffyUK</span></span><span class="rule brass" /></>}
  {variant === 'c' && <><span class="rule fade-l" /><Mark variant={markVariant} size={36} title="" /><span class="rule fade-r" /></>}
  {variant === 'd' && <><span class="seam" /><span class="medal bone"><Mark variant={markVariant} size={40} title="" /></span></>}
  {variant === 'e' && <><Mark variant={markVariant} size={28} title="" /><span class="rule thin" /></>}
</div>
<style>
  .kit-divider { display: flex; align-items: center; gap: var(--space-4); width: 100%; max-width: var(--container); margin: var(--space-8) auto; padding-inline: var(--space-5); color: var(--color-brand); }
  .rule { flex: 1; height: 2px; background: var(--color-brand-mid); opacity: .6; }
  .rule.brass { background: var(--color-cta); opacity: 1; }
  .rule.thin { height: 1px; background: var(--color-border); opacity: 1; }
  .rule.fade-l { background: linear-gradient(90deg, transparent, var(--color-brand-mid)); }
  .rule.fade-r { background: linear-gradient(90deg, var(--color-brand-mid), transparent); }
  .medal { display: inline-flex; padding: var(--space-2); border-radius: 50%; border: 1px solid var(--color-border); background: var(--color-surface-raised); }
  .medal.bone { background: var(--color-surface); position: relative; z-index: 1; }
  .stack { display: inline-flex; flex-direction: column; align-items: center; gap: 2px; }
  .word { font-family: var(--font-display); font-weight: 700; font-size: var(--text-sm); letter-spacing: .02em; }
  .kit-divider-d { position: relative; justify-content: center; }
  .kit-divider-d .seam { position: absolute; left: var(--space-5); right: var(--space-5); top: 50%; height: 3px; transform: translateY(-50%); background: var(--seam-gradient); }
  .kit-divider-e { justify-content: flex-start; }
</style>
```

- [ ] **Step 5: Write the canvas route**

```astro
---
// src/pages/design-canvas/index.astro — mounts every kit component in every variant for
// scripts/build_design_canvas.py. noindex; excluded from sitemaps by the noindex rule.
// Deleted in Task 19 after the picks are pulled.
import BaseLayout from '../../layouts/BaseLayout.astro';
import components from '../../../data/design/components.json';
import { VARIANTS } from '../../components/kit/_variant';
import Mark from '../../components/kit/Mark.astro';
import Button from '../../components/kit/Button.astro';
import SectionDivider from '../../components/kit/SectionDivider.astro';
// Tasks 6-16 add one import per component here, in components.json order:
// SiteHeaderKit, Hero, PuppyCard, TrustStrip, CounterStrip, InfoCard, Testimonial, Faq,
// ContactFormKit, PageNav, SiteFooterKit.
const byId: Record<string, any> = { buttons: Button, 'section-divider': SectionDivider };
const title = 'Design canvas — BlueStaffyUK kit (project 3)';
---
<BaseLayout title={title} description="Internal design canvas; not indexed." noindex={true}>
  <main class="container" style="padding-block: var(--space-8);">
    <h1 style="font-family: var(--font-display);">Design canvas</h1>
    <section data-component="mark" data-variant="a" class="kit-section">
      <h2>0 · The mark</h2>
      <div style="display:flex;gap:var(--space-6);color:var(--color-brand)">
        {VARIANTS.map((v) => <figure style="margin:0;text-align:center"><Mark variant={v} size={96} /><figcaption>{v}</figcaption></figure>)}
      </div>
    </section>
    {components.map((c) => byId[c.id] && (
      <section data-component={c.id} data-variant="all" class="kit-section"><h2>{c.title}</h2></section>
    ))}
    {components.map((c) => { const C = byId[c.id]; return C && VARIANTS.map((v) => (
      <section data-component={c.id} data-variant={v} data-width={c.board_width} class="kit-section">
        <h3 style="font-size:var(--text-sm);color:var(--color-text-muted)">{c.title} — variant {v}</h3>
        {c.id === 'buttons'
          ? <div style="display:flex;flex-wrap:wrap;gap:var(--space-4);align-items:center"><C variant={v} label="Meet the puppies" href="/available-puppies/" /><C variant={v} label="Ask about Roman" type="submit" /></div>
          : <C variant={v} />}
      </section>
    )); })}
  </main>
</BaseLayout>
```

Check `BaseLayout.astro` accepts a `noindex` prop (`grep -n noindex src/layouts/BaseLayout.astro`). If it does not, add `noindex?: boolean` to its `Props` and render `{noindex && <meta name="robots" content="noindex, nofollow" />}` in `<head>`. Then run `python3 scripts/sitemap_check.py` after a build to confirm the route is absent from every shard; if it is listed, add `design-canvas` to the noindex slug rule in `scripts/generate_sitemaps.py` the same way the thank-you page is excluded.

- [ ] **Step 6: Build and test**

Run: `npm run build 2>&1 | tail -2 && python3 scripts/sitemap_check.py | tail -1 && python3 -m pytest tests/py/test_design_components.py -q`
Expected: `50 page(s) built`; `0 problems`; `test_built_route_has_sixty_five_sections` FAILS with `len == 10` (only two components exist). That is the expected state until Task 16; mark it `xfail(strict=True, reason="kit lands in Tasks 5-16")` now, remove in Task 16.

- [ ] **Step 7: Commit**

```bash
git add src/pages/design-canvas src/components/kit src/layouts tests/py/test_design_components.py scripts
git commit -m "kit: Button and SectionDivider in five variants; noindex design-canvas route

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: `SiteHeaderKit.astro`

**Files:**
- Create: `src/components/kit/SiteHeaderKit.astro`
- Modify: `src/pages/design-canvas/index.astro` (import + `byId`)

- [ ] **Step 1: Write the component**

```astro
---
// src/components/kit/SiteHeaderKit.astro — spec §5 #1. Replaces SiteHeader.astro in project 4.
// a bone bar, left logo, right nav + CTA · b inverse bar, centred nav · c bone bar, centred logo, nav below
// d inverse bar, logo left, CTA only (nav in drawer) · e slim bone bar, nav left of CTA, strapline visible
import type { Variant } from './_variant';
import { SITE, NAV } from '../../lib/site';
import Mark from './Mark.astro';
import Button from './Button.astro';
interface Props { variant?: Variant; markVariant?: Variant }
const { variant = 'a', markVariant = 'a' } = Astro.props;
const inverse = variant === 'b' || variant === 'd';
const here = Astro.url.pathname;
const id = `kit-nav-${variant}`;
---
<header class={`kit-hdr kit-hdr-${variant} ${inverse ? 'inverse' : ''}`} data-variant={variant}>
  <div class="container bar">
    <a href="/" class="brand" aria-label={`${SITE.site_name} home`}>
      <Mark variant={markVariant} size={40} title={`${SITE.site_name} mark`} />
      <span class="word">BlueStaffyUK{variant === 'e' && <small>{SITE.location_label}</small>}</span>
    </a>
    {variant !== 'd' && (
      <nav aria-label="Main" class="nav"><ul>
        {NAV.map((n) => <li><a href={n.href} aria-current={n.href === here ? 'page' : undefined}>{n.label}</a></li>)}
      </ul></nav>
    )}
    {variant !== 'c' && <Button variant={inverse ? 'a' : 'a'} href="/available-puppies/" label="Available puppies" class="cta" />}
    {variant === 'd' && (
      <details class="drawer"><summary aria-label="Open menu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>
        <nav aria-label="Main" id={id}><ul>{NAV.map((n) => <li><a href={n.href}>{n.label}</a></li>)}</ul></nav></details>
    )}
  </div>
</header>
<style>
  .kit-hdr { position: sticky; top: 0; z-index: 50; background: var(--hdr-bg); border-bottom: 1px solid var(--color-border); min-height: var(--hdr); color: var(--color-text); }
  .kit-hdr.inverse { background: var(--color-surface-inverse); color: var(--color-text-on-inverse); border-bottom-color: transparent; }
  .bar { display: flex; align-items: center; justify-content: space-between; gap: var(--space-4); min-height: var(--hdr); flex-wrap: wrap; }
  .brand { display: inline-flex; align-items: center; gap: var(--space-3); text-decoration: none; color: inherit; }
  .word { font-family: var(--font-display); font-weight: 700; font-size: var(--text-xl); line-height: 1; display: flex; flex-direction: column; }
  .word small { font-family: var(--font-body); font-weight: 600; font-size: var(--text-xs); letter-spacing: .12em; text-transform: uppercase; color: var(--color-brand-mid); margin-top: 4px; }
  .inverse .word small { color: var(--color-link-on-inverse); }
  .nav ul { display: flex; gap: var(--space-5); list-style: none; margin: 0; padding: 0; flex-wrap: wrap; }
  .nav a { color: inherit; text-decoration: none; font-weight: 600; font-size: var(--text-sm); padding: var(--space-3) 0; display: inline-block; min-height: 44px; line-height: 20px; }
  .nav a[aria-current="page"] { box-shadow: inset 0 -2px 0 var(--color-cta); }
  .kit-hdr-b .bar { justify-content: center; } .kit-hdr-b .brand { margin-right: auto; } .kit-hdr-b .cta { margin-left: auto; }
  .kit-hdr-c .bar { flex-direction: column; gap: var(--space-2); padding-block: var(--space-3); } .kit-hdr-c .brand { flex-direction: column; text-align: center; }
  .kit-hdr-e { min-height: 56px; } .kit-hdr-e .bar { min-height: 56px; }
  .drawer summary { list-style: none; cursor: pointer; display: inline-flex; padding: 10px; min-width: 44px; min-height: 44px; align-items: center; justify-content: center; }
  .drawer[open] nav { position: absolute; left: 0; right: 0; top: 100%; background: var(--color-surface-inverse); padding: var(--space-5); }
  .drawer nav ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--space-3); }
  .drawer nav a { color: inherit; text-decoration: none; font-weight: 600; display: block; padding: var(--space-2) 0; min-height: 44px; }
  @media (max-width: 640px) { .nav ul { gap: var(--space-3); } }
</style>
```

- [ ] **Step 2: Register on the route**

In `src/pages/design-canvas/index.astro` add `import SiteHeaderKit from '../../components/kit/SiteHeaderKit.astro';` and `'site-header': SiteHeaderKit` to `byId`. Because the header is `position: sticky`, wrap it on the route: change the generic `<C variant={v} />` branch to `c.id === 'site-header' ? <div style="position:relative;min-height:140px"><C variant={v} /></div> : <C variant={v} />`.

- [ ] **Step 3: Build, run the fast suite, marker gate**

Run: `npm run build 2>&1 | tail -1 && python3 -m pytest tests/py/test_design_components.py tests/py/test_design_tokens.py -q && python3 scripts/marker_check.py | tail -1`
Expected: build clean; tests green except the two strict xfails; `0 problems`.

- [ ] **Step 4: Commit**

```bash
git add src/components/kit/SiteHeaderKit.astro src/pages/design-canvas/index.astro
git commit -m "kit: SiteHeaderKit in five variants

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Images to `src/assets` and `PuppyCard.astro` (closes Known Issue 4)

**Files:**
- Move: `public/images/<six puppy photos>` → `src/assets/puppies/`; the three hero images named in `src/pages/index.astro`'s hero → `src/assets/hero/`
- Create: `src/components/kit/PuppyCard.astro`, `src/lib/puppyImages.ts`
- Modify: `src/components/PuppyList.astro`, `src/pages/available-puppies/[slug].astro` (image src), `data/image-manifest.json`, `tests/py/test_images.py`

- [ ] **Step 1: Find the current puppy image references**

Run: `grep -rn "card_photo\|Roman2\|Byrd1" src/ | head -20 && ls public/images | grep -iE "roman|byrd|ince|vennie|christa|cheryl"`
Note every file that renders a puppy photo; each must switch to the `astro:assets` import below.

- [ ] **Step 2: Write the failing test**

Append to `tests/py/test_images.py`:

```python
def test_puppy_photos_live_in_src_assets_and_render_with_srcset():
    import json, pathlib, re
    root = pathlib.Path(__file__).resolve().parents[2]
    pups = json.loads((root / "data/puppies.json").read_text())
    for p in pups:
        assert (root / "src/assets/puppies" / p["card_photo"]).exists(), p["card_photo"]
        assert not (root / "public/images" / p["card_photo"]).exists(), p["card_photo"]
    built = root / "dist/available-puppies/roman/index.html"
    if built.exists():
        html = built.read_text()
        m = re.search(r'<img[^>]+srcset="([^"]+)"[^>]*alt="Roman', html) or re.search(r'<img[^>]+alt="Roman[^"]*"[^>]+srcset="([^"]+)"', html)
        assert m, "Roman's image has no srcset"
        widths = sorted(int(w) for w in re.findall(r"\s(\d+)w", m.group(1)))
        assert widths[-1] / widths[0] <= 3.0 and len(widths) >= 3, widths
```

- [ ] **Step 3: Run to see it fail**

Run: `python3 -m pytest tests/py/test_images.py -q -k srcset`
Expected: 1 failed (`src/assets/puppies/Roman2.jpg` missing).

- [ ] **Step 4: Move the files and write the image map**

```bash
mkdir -p src/assets/puppies src/assets/hero
python3 - <<'EOF'
import json, shutil, pathlib
root = pathlib.Path('.')
for p in json.loads((root/'data/puppies.json').read_text()):
    for f in {p['card_photo'], *p['gallery']}:
        src = root/'public/images'/f
        if src.exists(): shutil.move(str(src), str(root/'src/assets/puppies'/f))
EOF
git status --short | head
```

```ts
// src/lib/puppyImages.ts — every puppy photo as an astro:assets import, keyed by filename.
// Task 7: photos moved from public/images so <Image> can emit a bounded srcset (Known Issue 4).
import type { ImageMetadata } from 'astro';
const files = import.meta.glob<{ default: ImageMetadata }>('../assets/puppies/*.{jpg,jpeg,png,webp}', { eager: true });
export const PUPPY_IMAGES: Record<string, ImageMetadata> = Object.fromEntries(
  Object.entries(files).map(([path, mod]) => [path.split('/').pop()!, mod.default]),
);
export const puppyImage = (file: string): ImageMetadata => {
  const img = PUPPY_IMAGES[file];
  if (!img) throw new Error(`puppy image not in src/assets/puppies: ${file}`);
  return img;
};
```

- [ ] **Step 5: Write `PuppyCard.astro`**

```astro
---
// src/components/kit/PuppyCard.astro — spec §5 #4. Photo, name, sex, colour, price, status.
// a 4:5 photo, price badge top-right · b 1:1 photo, status ribbon · c 4:5 photo, price under name, chips
// d 1:1 photo, brand header band with name · e horizontal card (photo left) for lists
import type { Variant } from './_variant';
import { Image } from 'astro:assets';
import { puppyImage } from '../../lib/puppyImages';
import Button from './Button.astro';
import pups from '../../../data/puppies.json';
interface Props { variant?: Variant; slug?: string }
const { variant = 'a', slug = 'roman' } = Astro.props;
const p = pups.find((x) => x.slug === slug) ?? pups[0];
const img = puppyImage(p.card_photo);
const price = `£${p.price_gbp.toLocaleString('en-GB')}`;
const square = variant === 'b' || variant === 'd';
const avail = p.status === 'Available';
---
<article class={`kit-pup kit-pup-${variant}`} data-variant={variant}>
  <a href={`/available-puppies/${p.slug}/`} class="photo" aria-label={`${p.name}, ${p.sex} blue Staffy puppy`}>
    <Image src={img} alt={`${p.name} the ${p.colour.toLowerCase()} Staffordshire Bull Terrier puppy`} widths={[400, 800, 1200]} sizes="(max-width: 640px) 100vw, 400px" width={square ? 800 : 800} height={square ? 800 : 1000} loading="lazy" decoding="async" />
    {variant === 'a' && <span class="badge price">{price}</span>}
    {variant === 'b' && <span class={`ribbon ${avail ? 'ok' : ''}`}>{p.status}</span>}
  </a>
  <div class="body">
    {variant === 'd' ? <h3 class="band">{p.name}</h3> : <h3>{p.name}</h3>}
    <p class="meta">
      <span class="chip">{p.sex === 'male' ? 'Male' : 'Female'}</span>
      <span class="chip">{p.colour}</span>
      {variant !== 'a' && <span class="chip strong">{price}</span>}
      {variant !== 'b' && <span class={`chip ${avail ? 'ok' : ''}`}>{p.status}</span>}
    </p>
    <Button variant={variant === 'e' ? 'e' : 'a'} href={`/available-puppies/${p.slug}/`} label={`Ask about ${p.name}`} />
  </div>
</article>
<style>
  .kit-pup { background: var(--color-surface-raised); border: var(--card-border); border-radius: var(--card-radius); box-shadow: var(--shadow-card); overflow: hidden; max-width: 400px; transition: transform var(--dur-base) var(--ease-out), box-shadow var(--dur-base) var(--ease-out); }
  .kit-pup:hover { transform: translateY(-2px); box-shadow: var(--shadow-lift); }
  .photo { display: block; position: relative; } .photo img { display: block; width: 100%; height: auto; }
  .body { padding: var(--space-5); display: grid; gap: var(--space-3); }
  h3 { margin: 0; font-family: var(--font-display); font-size: var(--text-xl); color: var(--color-brand); }
  h3.band { background: var(--color-brand); color: var(--color-text-on-inverse); margin: calc(-1 * var(--space-5)) calc(-1 * var(--space-5)) 0; padding: var(--space-3) var(--space-5); }
  .meta { margin: 0; display: flex; flex-wrap: wrap; gap: var(--space-2); }
  .chip { font-size: var(--text-xs); font-weight: 600; padding: 4px 10px; border-radius: var(--radius-pill); background: var(--color-brand-soft); color: var(--color-brand); }
  .chip.strong { background: var(--color-cta-soft); } .chip.ok { background: var(--color-brand-soft); color: var(--color-ok); }
  .badge.price { position: absolute; top: var(--space-3); right: var(--space-3); background: var(--color-cta); color: var(--color-cta-ink); font-weight: 700; padding: 6px 12px; border-radius: var(--radius-pill); }
  .ribbon { position: absolute; left: 0; top: var(--space-4); background: var(--color-surface-inverse); color: var(--color-text-on-inverse); font-size: var(--text-xs); font-weight: 600; padding: 4px 12px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; }
  .kit-pup-e { display: grid; grid-template-columns: 160px 1fr; max-width: 560px; } .kit-pup-e .photo img { height: 100%; object-fit: cover; }
  @media (max-width: 640px) { .kit-pup-e { grid-template-columns: 1fr; } }
</style>
```

- [ ] **Step 6: Switch the existing renderers**

In `src/components/PuppyList.astro` and `src/pages/available-puppies/[slug].astro` replace the `<img src={`/images/${…card_photo}`}>` (and gallery) elements with `<Image src={puppyImage(file)} widths={[400, 800, 1200]} sizes="(max-width: 640px) 100vw, 400px" alt={…} />` importing `Image` from `astro:assets` and `puppyImage` from `../lib/puppyImages` (adjust the relative path). Keep alt text and surrounding markup identical: project 3 must not change content. Remove the moved files' rows from `data/image-manifest.json` (or update their `path` to `src/assets/puppies/<file>` if the manifest is read by `scripts/extract_images.py`; check with `grep -n image-manifest scripts/*.py`).

Register `PuppyCard` on the route (`'puppy-card': PuppyCard`).

- [ ] **Step 7: Build, parity, tests**

Run: `npm run build 2>&1 | tail -1 && python3 scripts/migration_parity.py | tail -1 && python3 -m pytest tests/py/test_images.py tests/py/test_parity.py -q`
Expected: build clean; `examined 40 pages, 0 failing` (image counts unchanged); tests green.

- [ ] **Step 8: Commit**

```bash
git add -A src/assets src/components src/pages src/lib data/image-manifest.json tests/py/test_images.py public/images
git commit -m "kit: PuppyCard in five variants; puppy photos to astro:assets with bounded srcset (Known Issue 4)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: `Hero.astro`

**Files:**
- Create: `src/components/kit/Hero.astro`
- Modify: route import

- [ ] **Step 1: Pick the hero image**

Run: `grep -n "<img" src/pages/index.astro | head -5`. Move the homepage hero image (the first `<img>` inside the hero block) to `src/assets/hero/home.webp` and update `index.astro` to `<Image>` as in Task 7 step 6, same alt. If the homepage has no distinct hero image, use `src/assets/puppies/Roman2.jpg` and say so in the commit.

- [ ] **Step 2: Write the component**

```astro
---
// src/components/kit/Hero.astro — spec §5 #2.
// a photo right, copy left, bone · b full-bleed photo, inverse overlay · c split with trust chips
// d text-only on inverse (guide pages) · e short location hero (eyebrow + H1 + one line)
import type { Variant } from './_variant';
import { Image } from 'astro:assets';
import hero from '../../assets/hero/home.webp';
import { SITE } from '../../lib/site';
import Button from './Button.astro';
interface Props { variant?: Variant; eyebrow?: string; title?: string; lede?: string }
const { variant = 'a',
  eyebrow = `KC-registered · ${SITE.location_label}`,
  title = 'Blue Staffy puppies raised in a family home',
  lede = 'Health-tested parents, five-generation pedigree, and UK delivery from £200.' } = Astro.props;
const inverse = variant === 'b' || variant === 'd';
const chips = ['KC registered', 'DNA tested parents', 'Home raised'];
---
<section class={`kit-hero kit-hero-${variant} ${inverse ? 'inverse' : ''}`} data-variant={variant}>
  {variant === 'b' && <Image src={hero} alt="" widths={[800, 1280, 1920]} sizes="100vw" class="bg" loading="eager" />}
  <div class="container inner">
    <div class="copy">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      {variant !== 'e' && <p class="lede">{lede}</p>}
      {variant === 'e' && <p class="lede">{lede}</p>}
      {variant === 'c' && <ul class="chips">{chips.map((c) => <li>{c}</li>)}</ul>}
      {variant !== 'e' && <div class="ctas"><Button variant="a" href="/available-puppies/" label="Meet the puppies" /><Button variant={inverse ? 'c' : 'b'} href="/uk-blue-staffy-breeders-contact/" label="Ask a question" /></div>}
    </div>
    {(variant === 'a' || variant === 'c') && <Image src={hero} alt="A blue Staffordshire Bull Terrier puppy" widths={[480, 800, 1200]} sizes="(max-width: 900px) 100vw, 560px" class="pic" loading="eager" />}
  </div>
</section>
<style>
  .kit-hero { background: var(--color-surface); color: var(--color-text); position: relative; overflow: hidden; }
  .kit-hero.inverse { background: var(--color-surface-inverse); color: var(--color-text-on-inverse); }
  .inner { display: grid; grid-template-columns: 1fr; gap: var(--space-8); align-items: center; padding-block: var(--space-10); position: relative; }
  .kit-hero-a .inner, .kit-hero-c .inner { grid-template-columns: 1.1fr 1fr; }
  .eyebrow { margin: 0 0 var(--space-3); font-size: var(--text-xs); font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--color-cta-hover); }
  .inverse .eyebrow { color: var(--color-cta); }
  h1 { margin: 0 0 var(--space-4); font-family: var(--font-display); font-weight: 700; font-size: var(--text-4xl); line-height: var(--text-4xl--line-height); text-wrap: balance; color: var(--color-brand); }
  .inverse h1 { color: inherit; }
  .lede { margin: 0 0 var(--space-5); font-size: var(--text-lg); max-width: 52ch; }
  .ctas { display: flex; gap: var(--space-3); flex-wrap: wrap; }
  .chips { list-style: none; margin: 0 0 var(--space-5); padding: 0; display: flex; gap: var(--space-2); flex-wrap: wrap; }
  .chips li { font-size: var(--text-xs); font-weight: 600; padding: 6px 12px; border-radius: var(--radius-pill); background: var(--color-surface-raised); border: var(--card-border); }
  .pic { width: 100%; height: auto; border-radius: var(--card-radius); box-shadow: var(--shadow-lift); }
  .kit-hero-b .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: .28; }
  .kit-hero-b .inner { min-height: 520px; }
  .kit-hero-d .inner { padding-block: var(--space-8); } .kit-hero-d h1 { font-size: var(--text-3xl); }
  .kit-hero-e .inner { padding-block: var(--space-7); } .kit-hero-e h1 { font-size: var(--text-3xl); margin-bottom: var(--space-2); }
  @media (max-width: 900px) { .kit-hero-a .inner, .kit-hero-c .inner { grid-template-columns: 1fr; } h1 { font-size: var(--text-3xl); } }
</style>
```

- [ ] **Step 3: Register, build, test, commit**

Add `import Hero …` and `hero: Hero` on the route. Run `npm run build 2>&1 | tail -1 && python3 -m pytest tests/py/test_design_tokens.py -q && python3 scripts/marker_check.py | tail -1`. Then:

```bash
git add -A src
git commit -m "kit: Hero in five variants

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: `TrustStrip.astro` and `CounterStrip.astro` (with the hero-separation fixture pair)

**Files:**
- Create: `src/components/kit/TrustStrip.astro`, `src/components/kit/CounterStrip.astro`, `tests/render/fixtures/known_good/kit-counter-separated.html`, `tests/render/fixtures/known_broken/kit-counter-flush.html`
- Modify: route

- [ ] **Step 1: Write `TrustStrip.astro`**

```astro
---
// src/components/kit/TrustStrip.astro — spec §5 #5. Line icons, never emoji (rule 7).
// a icon row · b three tiles · c single line with dividers · d inverse band · e stacked list
import type { Variant } from './_variant';
interface Props { variant?: Variant }
const { variant = 'a' } = Astro.props;
const items = [
  { t: 'KC registered', d: 'Every litter registered with The Kennel Club.', i: 'M12 2l3 6 6 1-4.5 4.5L18 20l-6-3-6 3 1.5-6.5L3 9l6-1z' },
  { t: 'DNA-tested parents', d: 'L-2-HGA and HC clear, results on request.', i: 'M6 3v6a6 6 0 0 0 12 0V3M6 21v-6a6 6 0 0 1 12 0v6' },
  { t: 'Raised in the home', d: 'Socialised with children and other dogs.', i: 'M3 11l9-8 9 8v10H3z M9 21v-6h6v6' },
];
const inverse = variant === 'd';
---
<section class={`kit-trust kit-trust-${variant} ${inverse ? 'inverse' : ''}`} data-variant={variant} aria-label="Why buy from BlueStaffyUK">
  <ul class="container list">
    {items.map((x) => (
      <li>
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d={x.i} /></svg>
        <div><strong>{x.t}</strong>{variant !== 'c' && <p>{x.d}</p>}</div>
      </li>
    ))}
  </ul>
</section>
<style>
  .kit-trust { background: var(--color-surface-raised); color: var(--color-text); padding-block: var(--space-6); border-block: 1px solid var(--color-border); }
  .kit-trust.inverse { background: var(--color-surface-inverse); color: var(--color-text-on-inverse); border: 0; }
  .list { list-style: none; margin: 0; padding-block: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-6); }
  li { display: flex; gap: var(--space-3); align-items: flex-start; color: var(--color-brand); }
  .inverse li { color: inherit; } .inverse svg { color: var(--color-cta); }
  strong { display: block; font-family: var(--font-display); font-size: var(--text-lg); color: inherit; }
  p { margin: 4px 0 0; font-size: var(--text-sm); color: var(--color-text-muted); } .inverse p { color: inherit; opacity: .85; }
  .kit-trust-b li { flex-direction: column; padding: var(--space-5); border: var(--card-border); border-radius: var(--card-radius); box-shadow: var(--shadow-card); }
  .kit-trust-c .list { display: flex; justify-content: center; gap: 0; } .kit-trust-c li { padding-inline: var(--space-6); border-left: 1px solid var(--color-border); align-items: center; } .kit-trust-c li:first-child { border-left: 0; }
  .kit-trust-e .list { grid-template-columns: 1fr; max-width: 560px; }
  @media (max-width: 720px) { .list { grid-template-columns: 1fr; } .kit-trust-c .list { flex-direction: column; } .kit-trust-c li { border-left: 0; padding-inline: 0; } }
</style>
```

- [ ] **Step 2: Write `CounterStrip.astro`**

```astro
---
// src/components/kit/CounterStrip.astro — spec §5 #6. Every variant satisfies
// rules/design.md `layout-hero-counter-separation`: tone shift AND a rule/seam.
// Figures come from data, never typed here (rule 9). `.counter-wrap` is the harness hook.
// a tone shift + top rule · b seam gradient bar · c boxed tiles on bone · d hero-edge with brand rule · e minimal, brass rule
import type { Variant } from './_variant';
import pups from '../../../data/puppies.json';
import { SITE } from '../../lib/site';
interface Props { variant?: Variant }
const { variant = 'a' } = Astro.props;
const available = pups.filter((p) => p.status === 'Available').length;
const stats = [
  { n: String(available), l: 'puppies available now' },
  { n: `£${SITE.deposit_gbp}`, l: SITE.deposit_refundable ? 'refundable deposit' : 'deposit' },
  { n: `£${SITE.delivery_min_gbp}–£${SITE.delivery_max_gbp}`, l: 'UK delivery by distance' },
];
---
<section class={`counter-wrap kit-counter kit-counter-${variant}`} data-counters data-variant={variant} aria-label="At a glance">
  <ul class="container list">
    {stats.map((s) => <li><strong>{s.n}</strong><span>{s.l}</span></li>)}
  </ul>
</section>
<style>
  .kit-counter { position: relative; background: var(--counter-bed); color: var(--color-brand); padding-block: var(--space-6); border-top: 1px solid var(--color-border); }
  .list { list-style: none; margin: 0; padding-block: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-5); text-align: center; }
  strong { display: block; font-family: var(--font-display); font-size: var(--text-3xl); line-height: 1.1; }
  span { font-size: var(--text-sm); color: var(--color-text-muted); }
  .kit-counter-b { border-top: 0; } .kit-counter-b::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 3px; background: var(--seam-gradient); }
  .kit-counter-c li { background: var(--color-surface-raised); border: var(--card-border); border-radius: var(--radius-md); padding: var(--space-4); }
  .kit-counter-d { background: var(--color-brand-soft); border-top: 2px solid var(--color-brand); }
  .kit-counter-e { background: var(--color-surface-raised); border-top: 2px solid var(--color-cta); padding-block: var(--space-4); } .kit-counter-e strong { font-size: var(--text-2xl); }
  @media (max-width: 720px) { .list { grid-template-columns: 1fr; } }
</style>
```

- [ ] **Step 3: Write the fixture pair**

Look at an existing pair first: `ls tests/render/fixtures/known_good | head -3` and open one to copy its document shell (each fixture is a complete HTML page; the meta spec loads it and expects the named check to be silent on `known_good` and to fire on `known_broken`). Then:

`tests/render/fixtures/known_good/kit-counter-separated.html` — a page with a `<section class="hero" style="background:#1F3A52;color:#fff;padding:80px 24px">…</section>` followed by `<section class="counter-wrap" style="background:#FAF8F3;border-top:1px solid #DAD6CC;padding:40px 24px"><ul>…three li…</ul></section>`.

`tests/render/fixtures/known_broken/kit-counter-flush.html` — identical but the counter has `style="background:#1F3A52;color:#fff;padding:40px 24px"` and no border (same tone, no rule).

Fixtures are test data; hex in them is allowed (the no-hex test scans `src/components/kit/` only).

- [ ] **Step 4: Register, build, run meta on the fixture pair**

Add both components to the route. Run: `npm run build 2>&1 | tail -1 && npm run test:render:meta -- -g "layout-hero-counter-separation" 2>&1 | tail -5`
Expected: the check passes both fixture halves (the meta spec's per-check fixture tests). If the runner flag differs, use `npx playwright test tests/render/meta.spec.ts -g counter`.

- [ ] **Step 5: Commit**

```bash
git add -A src tests/render/fixtures
git commit -m "kit: TrustStrip and CounterStrip in five variants; counter-separation fixture pair

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: `InfoCard.astro` (with the H3-image-first and statement-label conventions)

**Files:**
- Create: `src/components/kit/InfoCard.astro`, fixtures `known_good/kit-h3-image-first.html`, `known_broken/kit-h3-image-last.html`, `known_good/kit-stmt-label.html`, `known_broken/kit-stmt-label-hidden.html`

- [ ] **Step 1: Read what the two deferred checks measure**

Run: `grep -n "h3-image-first" -A25 tests/render/checks/layout.ts | head -50 && grep -n "statement-label-visible" -A25 tests/render/checks/sem.ts | head -50`
Note the selectors (`.sec-img` owned by an H3; `.stmt-label` visible). The component below uses both; adjust class names to match exactly what the checks query.

- [ ] **Step 2: Write the component**

```astro
---
// src/components/kit/InfoCard.astro — spec §5 #7. Variant d is the H3-owned `.sec-img`
// convention (layout-h3-image-first); every variant carries a visible `.stmt-label`
// (sem-statement-label-visible), so both deferred checks examine nodes once the kit ships.
// a brand header band · b brass eyebrow · c icon-led · d image-top, H3 owns .sec-img · e plain, bordered
import type { Variant } from './_variant';
import { Image } from 'astro:assets';
import hero from '../../assets/hero/home.webp';
interface Props { variant?: Variant; label?: string; title?: string; body?: string }
const { variant = 'a', label = 'Health', title = 'What a health-tested litter means',
  body = 'Both parents are DNA-tested for L-2-HGA and HC. Every puppy leaves with a vet check, first vaccination and microchip.' } = Astro.props;
---
<article class={`kit-info kit-info-${variant}`} data-variant={variant}>
  {variant === 'a' && <div class="band"><span class="stmt-label">{label}</span></div>}
  {variant === 'd' && <h3 class="sec-h3"><span class="stmt-label">{label}</span>{title}</h3>}
  {variant === 'd' && <Image src={hero} alt="" widths={[400, 800]} sizes="(max-width: 640px) 100vw, 400px" class="sec-img" loading="lazy" />}
  <div class="body">
    {variant === 'b' && <p class="eyebrow stmt-label">{label}</p>}
    {variant === 'c' && <p class="icon-row"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg><span class="stmt-label">{label}</span></p>}
    {variant === 'e' && <p class="eyebrow stmt-label">{label}</p>}
    {variant !== 'd' && <h3>{title}</h3>}
    <p>{body}</p>
  </div>
</article>
<style>
  .kit-info { background: var(--color-surface-raised); border: var(--card-border); border-radius: var(--card-radius); box-shadow: var(--shadow-card); overflow: hidden; max-width: 420px; color: var(--color-text); }
  .band { background: var(--color-brand); color: var(--color-text-on-inverse); padding: var(--space-2) var(--space-5); }
  .stmt-label { font-size: var(--text-xs); font-weight: 600; letter-spacing: .12em; text-transform: uppercase; }
  .eyebrow { margin: 0 0 var(--space-2); color: var(--color-cta-hover); }
  .icon-row { margin: 0 0 var(--space-3); display: flex; align-items: center; gap: var(--space-2); color: var(--color-brand); }
  .body { padding: var(--space-5); } .body p:last-child { margin: 0; font-size: var(--text-sm); }
  h3 { margin: 0 0 var(--space-2); font-family: var(--font-display); font-size: var(--text-xl); color: var(--color-brand); }
  .sec-h3 { padding: var(--space-5) var(--space-5) 0; display: flex; flex-direction: column; gap: 4px; } .sec-h3 .stmt-label { color: var(--color-cta-hover); }
  .sec-img { display: block; width: 100%; height: auto; margin-top: var(--space-3); }
  .kit-info-e { box-shadow: none; }
</style>
```

- [ ] **Step 3: Write the two fixture pairs** using the same shell as Task 9's, each a page containing one card: `known_good/kit-h3-image-first.html` has `<h3>…</h3><img class="sec-img" …>` in that order; `known_broken/kit-h3-image-last.html` has the `<img class="sec-img">` before the `<h3>`. `known_good/kit-stmt-label.html` has `<span class="stmt-label">Health</span>` visible; `known_broken/kit-stmt-label-hidden.html` has it with `style="display:none"`. Match the exact selectors from Step 1.

- [ ] **Step 4: Register, build, meta on the two checks, commit**

Run: `npm run build 2>&1 | tail -1 && npx playwright test tests/render/meta.spec.ts -g "h3-image-first|statement-label" 2>&1 | tail -5`
Expected: both pass on both halves.

```bash
git add -A src tests/render/fixtures
git commit -m "kit: InfoCard in five variants; h3-image-first and stmt-label fixture pairs

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 11: `Testimonial.astro`

**Files:**
- Create: `src/components/kit/Testimonial.astro`, `data/reviews.json`

- [ ] **Step 1: Find real reviews in the repo**

Run: `grep -rn -i "testimonial\|review\|\"“\|said" src/pages/index.astro src/pages/buy-blue-staffy-puppies-uk/index.astro | head -20`
Copy up to three verbatim quotes with the attribution exactly as the migrated page prints it into `data/reviews.json` as `[{"quote": "...", "name": "...", "place": "...", "source": "src/pages/index.astro"}]`. If fewer than three exist, fill the remainder with `{"quote": "REVIEW_PLACEHOLDER", "name": "REVIEW_PLACEHOLDER", "place": "", "source": ""}`. Never invent a review (rule 9).

- [ ] **Step 2: Write the component**

```astro
---
// src/components/kit/Testimonial.astro — spec §5 #8. Quotes come from data/reviews.json
// (verbatim from migrated pages, or REVIEW_PLACEHOLDER — never invented).
// a quote card · b inverse band with initials avatar · c three-up grid · d single large pull-quote · e stacked list
import type { Variant } from './_variant';
import reviews from '../../../data/reviews.json';
interface Props { variant?: Variant }
const { variant = 'a' } = Astro.props;
const list = variant === 'c' || variant === 'e' ? reviews.slice(0, 3) : reviews.slice(0, 1);
const initials = (n: string) => n.split(/\s+/).map((w) => w[0]).join('').slice(0, 2).toUpperCase();
const inverse = variant === 'b';
---
<section class={`kit-quote kit-quote-${variant} ${inverse ? 'inverse' : ''}`} data-variant={variant} aria-label="What families say">
  <div class={`container ${variant === 'c' ? 'grid' : 'stack'}`}>
    {list.map((r) => (
      <figure>
        {variant === 'b' && <span class="avatar" aria-hidden="true">{initials(r.name)}</span>}
        <blockquote><p>{r.quote}</p></blockquote>
        <figcaption>{r.name}{r.place && <span> · {r.place}</span>}</figcaption>
      </figure>
    ))}
  </div>
</section>
<style>
  .kit-quote { padding-block: var(--space-8); color: var(--color-text); }
  .kit-quote.inverse { background: var(--color-surface-inverse); color: var(--color-text-on-inverse); }
  .stack { display: grid; gap: var(--space-5); } .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-5); }
  figure { margin: 0; padding: var(--space-6); background: var(--color-surface-raised); border: var(--card-border); border-radius: var(--card-radius); box-shadow: var(--shadow-card); }
  .inverse figure { background: transparent; border: 0; box-shadow: none; text-align: center; max-width: 720px; margin-inline: auto; }
  blockquote { margin: 0 0 var(--space-3); } blockquote p { margin: 0; font-family: var(--font-display); font-size: var(--text-lg); line-height: 1.5; }
  .kit-quote-d blockquote p { font-size: var(--text-2xl); } .kit-quote-d figure { border: 0; box-shadow: none; background: transparent; border-left: 4px solid var(--color-cta); border-radius: 0; }
  figcaption { font-size: var(--text-sm); font-weight: 600; color: var(--color-text-muted); } .inverse figcaption { color: inherit; opacity: .85; }
  .avatar { display: inline-grid; place-items: center; width: 56px; height: 56px; border-radius: 50%; background: var(--color-cta); color: var(--color-cta-ink); font-weight: 700; margin-bottom: var(--space-3); }
  .kit-quote-e figure { padding: var(--space-4) 0; border: 0; border-bottom: 1px solid var(--color-border); border-radius: 0; box-shadow: none; background: transparent; }
  @media (max-width: 720px) { .grid { grid-template-columns: 1fr; } }
</style>
```

- [ ] **Step 3: Register, build, placeholder count, commit**

Run: `npm run build 2>&1 | tail -1 && python3 scripts/placeholder_check.py | tail -2 && python3 -m pytest tests/py/test_data_files.py tests/py/test_placeholder_check.py -q`
Expected: build clean; if `REVIEW_PLACEHOLDER` appears, its count is printed and the gate stays advisory.

```bash
git add -A src data/reviews.json
git commit -m "kit: Testimonial in five variants from data/reviews.json (verbatim or REVIEW_PLACEHOLDER)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 12: `Faq.astro`

**Files:**
- Create: `src/components/kit/Faq.astro`

- [ ] **Step 1: Write the component**

```astro
---
// src/components/kit/Faq.astro — spec §5 #9. Native <details>, five treatments.
// a plus icon · b chevron · c numbered · d bordered cards · e divided list
import type { Variant } from './_variant';
import { SITE } from '../../lib/site';
interface Props { variant?: Variant; items?: { q: string; a: string }[] }
const defaults = [
  { q: 'How much is the deposit?', a: `£${SITE.deposit_gbp}, ${SITE.deposit_refundable ? 'refundable' : 'non-refundable'}, secures your chosen puppy.` },
  { q: 'Do you deliver across the UK?', a: `Yes. ${SITE.delivery_note}, from £${SITE.delivery_min_gbp} to £${SITE.delivery_max_gbp}.` },
  { q: 'Can we visit and meet the mother?', a: 'Yes. Every family meets the mother and sees where the litter is raised before they commit.' },
];
const { variant = 'a', items = defaults } = Astro.props;
---
<div class={`kit-faq kit-faq-${variant}`} data-variant={variant}>
  {items.map((it, i) => (
    <details>
      <summary>
        {variant === 'c' && <span class="num">{String(i + 1).padStart(2, '0')}</span>}
        <span class="q">{it.q}</span>
        {variant === 'a' && <svg class="ico" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>}
        {variant === 'b' && <svg class="ico" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>}
      </summary>
      <p>{it.a}</p>
    </details>
  ))}
</div>
<style>
  .kit-faq { max-width: 640px; display: grid; gap: var(--space-2); color: var(--color-text); }
  details { background: var(--color-surface-raised); border-radius: var(--radius-md); }
  summary { display: flex; align-items: center; gap: var(--space-3); cursor: pointer; list-style: none; padding: var(--space-4); min-height: 44px; font-weight: 600; font-family: var(--font-display); font-size: var(--text-lg); color: var(--color-brand); }
  summary::-webkit-details-marker { display: none; }
  .q { flex: 1; } .ico { transition: transform var(--dur-base) var(--ease-out); }
  details[open] .ico { transform: rotate(45deg); } .kit-faq-b details[open] .ico { transform: rotate(180deg); }
  p { margin: 0; padding: 0 var(--space-4) var(--space-4); font-size: var(--text-base); }
  .num { font-family: var(--font-body); font-size: var(--text-sm); color: var(--color-cta-hover); font-variant-numeric: tabular-nums; }
  .kit-faq-d details { border: var(--card-border); box-shadow: var(--shadow-card); }
  .kit-faq-e { gap: 0; } .kit-faq-e details { border-radius: 0; border-bottom: 1px solid var(--color-border); background: transparent; } .kit-faq-e summary { padding-inline: 0; } .kit-faq-e p { padding-inline: 0; }
  summary:focus-visible { outline: 3px solid var(--color-focus); outline-offset: 2px; border-radius: var(--radius-sm); }
</style>
```

- [ ] **Step 2: Register, build, commit**

```bash
npm run build 2>&1 | tail -1 && python3 scripts/marker_check.py | tail -1
git add -A src
git commit -m "kit: Faq in five variants (native details)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 13: `ContactFormKit.astro` (keeps the form contract)

**Files:**
- Create: `src/components/kit/ContactFormKit.astro`
- Read first: `src/components/ContactForm.astro`, `scripts/form_contract_audit.py` (the required field names)

- [ ] **Step 1: Extract the contract**

Run: `grep -n "name=\"" src/components/ContactForm.astro && grep -n "REQUIRED\|FIELDS\|required_fields" scripts/form_contract_audit.py | head`
Write down every field `name`, the honeypot name, the `action` expression and the `method`. The kit form must use those exactly; only layout changes.

- [ ] **Step 2: Write the component**

```astro
---
// src/components/kit/ContactFormKit.astro — spec §5 #10. Same fields, action and honeypot as
// ContactForm.astro (the FORM_ENDPOINT contract); five layouts.
// a single column · b two column · c stepped labels (fieldsets) · d inverse card · e inline sidebar form
import type { Variant } from './_variant';
import Button from './Button.astro';
interface Props { variant?: Variant }
const { variant = 'a' } = Astro.props;
const id = import.meta.env.PUBLIC_FORMSPREE_ID;
const action = id ? `https://formspree.io/f/${id}` : '#contact-stub';
const inverse = variant === 'd';
const fid = `kit-form-${variant}`;
---
<form class={`kit-form kit-form-${variant} ${inverse ? 'inverse' : ''}`} data-variant={variant} action={action} method="POST" aria-labelledby={`${fid}-h`}>
  <h2 id={`${fid}-h`}>{variant === 'e' ? 'Ask about a puppy' : 'Get in touch about a puppy'}</h2>
  {variant === 'c' ? (
    <>
      <fieldset><legend>1 · About you</legend>
        <label for={`${fid}-name`}>Your name</label><input id={`${fid}-name`} name="name" type="text" autocomplete="name" required />
        <label for={`${fid}-email`}>Email</label><input id={`${fid}-email`} name="email" type="email" autocomplete="email" required />
        <label for={`${fid}-phone`}>Phone (optional)</label><input id={`${fid}-phone`} name="phone" type="tel" autocomplete="tel" />
      </fieldset>
      <fieldset><legend>2 · Your message</legend>
        <label for={`${fid}-msg`}>Message</label><textarea id={`${fid}-msg`} name="message" rows="5" required></textarea>
      </fieldset>
    </>
  ) : (
    <div class="fields">
      <div><label for={`${fid}-name`}>Your name</label><input id={`${fid}-name`} name="name" type="text" autocomplete="name" required /></div>
      <div><label for={`${fid}-email`}>Email</label><input id={`${fid}-email`} name="email" type="email" autocomplete="email" required /></div>
      {variant !== 'e' && <div><label for={`${fid}-phone`}>Phone (optional)</label><input id={`${fid}-phone`} name="phone" type="tel" autocomplete="tel" /></div>}
      <div class="wide"><label for={`${fid}-msg`}>Message</label><textarea id={`${fid}-msg`} name="message" rows={variant === 'e' ? 3 : 5} required></textarea></div>
    </div>
  )}
  <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp" />
  <Button variant="d" type="submit" label="Send message" />
  <p class="note">We reply within one working day. No newsletter, no sharing.</p>
</form>
<style>
  .kit-form { max-width: 560px; padding: var(--space-6); background: var(--color-surface-raised); border: var(--card-border); border-radius: var(--card-radius); box-shadow: var(--shadow-card); color: var(--color-text); display: grid; gap: var(--space-4); }
  .kit-form.inverse { background: var(--color-surface-inverse); color: var(--color-text-on-inverse); border: 0; }
  h2 { margin: 0; font-family: var(--font-display); font-size: var(--text-2xl); color: var(--color-brand); } .inverse h2 { color: inherit; }
  .fields { display: grid; gap: var(--space-4); } .kit-form-b .fields { grid-template-columns: 1fr 1fr; } .kit-form-b .wide { grid-column: 1 / -1; }
  label { display: block; font-weight: 600; font-size: var(--text-sm); margin-bottom: 6px; }
  input, textarea { width: 100%; box-sizing: border-box; font: inherit; padding: 12px 14px; min-height: 44px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-surface-raised); color: var(--color-text); }
  input:focus-visible, textarea:focus-visible { outline: 3px solid var(--color-focus); outline-offset: 1px; }
  fieldset { border: var(--card-border); border-radius: var(--radius-md); padding: var(--space-4); display: grid; gap: var(--space-3); margin: 0; }
  legend { font-family: var(--font-display); font-weight: 600; color: var(--color-brand); padding-inline: var(--space-2); }
  .hp { position: absolute; left: -9999px; width: 1px; height: 1px; }
  .note { margin: 0; font-size: var(--text-xs); color: var(--color-text-muted); } .inverse .note { color: inherit; opacity: .8; }
  .kit-form-e { max-width: 360px; padding: var(--space-5); }
  @media (max-width: 640px) { .kit-form-b .fields { grid-template-columns: 1fr; } }
</style>
```

Replace `name="name"`, `"email"`, `"phone"`, `"message"`, `"_gotcha"` with the exact names from Step 1 if they differ.

- [ ] **Step 3: Register, build with `.env`, run the form audit, commit**

Run: `set -a; source .env; set +a; npm run build 2>&1 | tail -1 && python3 scripts/form_contract_audit.py | tail -1`
Expected: `examined 6 forms; 0 problems` (the contact page plus the five kit forms on the canvas route) — if the audit scopes by `page-map.json` kind and ignores the canvas route, `examined 1 forms; 0 problems` is also correct; either way `0 problems`.

```bash
git add -A src
git commit -m "kit: ContactFormKit in five layouts, same field contract

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 14: `PageNav.astro`

**Files:**
- Create: `src/components/kit/PageNav.astro`

- [ ] **Step 1: Write the component**

```astro
---
// src/components/kit/PageNav.astro — spec §5 #11. Breadcrumb (from lib/site crumbs) plus
// in-page navigation. Jump links carry scroll-margin via global [id] rule (nav-jump-target-lands).
// a breadcrumb only · b breadcrumb + sticky ToC · c chip row · d sidebar ToC · e jump-bar
import type { Variant } from './_variant';
import { crumbs } from '../../lib/site';
interface Props { variant?: Variant; path?: string; title?: string; sections?: { id: string; label: string }[] }
const { variant = 'a', path = '/uk-staffordshire-bull-terrier-guide/', title = 'Staffordshire Bull Terrier guide',
  sections = [{ id: 'temperament', label: 'Temperament' }, { id: 'health', label: 'Health' }, { id: 'exercise', label: 'Exercise' }, { id: 'cost', label: 'Cost' }] } = Astro.props;
const trail = crumbs(path, title);
---
<div class={`kit-nav kit-nav-${variant}`} data-variant={variant}>
  <nav aria-label="Breadcrumb" class="crumbs"><ol>
    {trail.map((c, i) => <li>{i < trail.length - 1 ? <a href={c.href}>{c.label}</a> : <span aria-current="page">{c.label}</span>}</li>)}
  </ol></nav>
  {variant !== 'a' && (
    <nav aria-label="On this page" class="toc"><ul>
      {sections.map((s) => <li><a href={`#${s.id}`}>{s.label}</a></li>)}
    </ul></nav>
  )}
</div>
<style>
  .kit-nav { color: var(--color-text); display: grid; gap: var(--space-3); max-width: 640px; }
  .crumbs ol { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: var(--space-2); font-size: var(--text-sm); }
  .crumbs li + li::before { content: "/"; color: var(--color-text-muted); margin-right: var(--space-2); }
  .crumbs a { color: var(--color-link); } .crumbs [aria-current] { color: var(--color-text-muted); }
  .toc ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: var(--space-2); }
  .toc a { display: inline-block; padding: 8px 14px; min-height: 44px; line-height: 28px; border-radius: var(--radius-pill); background: var(--color-brand-soft); color: var(--color-brand); font-weight: 600; font-size: var(--text-sm); text-decoration: none; }
  .kit-nav-b .toc { position: sticky; top: calc(var(--hdr) + var(--space-2)); background: var(--color-surface); padding-block: var(--space-2); }
  .kit-nav-d { grid-template-columns: 200px 1fr; } .kit-nav-d .crumbs { grid-column: 1 / -1; } .kit-nav-d .toc ul { flex-direction: column; border-left: 2px solid var(--color-border); }
  .kit-nav-d .toc a { background: transparent; border-radius: 0; padding: 6px 12px; }
  .kit-nav-e .toc ul { gap: 0; border: var(--card-border); border-radius: var(--radius-md); overflow: hidden; } .kit-nav-e .toc li { flex: 1; text-align: center; } .kit-nav-e .toc a { display: block; border-radius: 0; background: var(--color-surface-raised); border-left: 1px solid var(--color-border); }
  .kit-nav-e .toc li:first-child a { border-left: 0; }
</style>
```

- [ ] **Step 2: Register, build, commit**

```bash
npm run build 2>&1 | tail -1 && python3 scripts/marker_check.py | tail -1
git add -A src
git commit -m "kit: PageNav in five variants

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 15: `SiteFooterKit.astro`

**Files:**
- Create: `src/components/kit/SiteFooterKit.astro`

- [ ] **Step 1: Write the component**

```astro
---
// src/components/kit/SiteFooterKit.astro — spec §5 #12. Replaces SiteFooter.astro in project 4.
// a four-column · b three-column with stacked lockup · c slim single row · d inverse with CTA band · e sitemap-style
import type { Variant } from './_variant';
import { SITE, NAV } from '../../lib/site';
import Mark from './Mark.astro';
import Button from './Button.astro';
interface Props { variant?: Variant; markVariant?: Variant }
const { variant = 'a', markVariant = 'a' } = Astro.props;
const year = new Date().getFullYear();
const socials = Object.entries(SITE.socials) as [string, string][];
const legal = [{ href: '/privacy-policy-uk/', label: 'Privacy policy' }];
---
<footer class={`kit-ftr kit-ftr-${variant}`} data-variant={variant}>
  {variant === 'd' && <div class="cta-band"><div class="container row"><p>Ready to meet the litter?</p><Button variant="a" href="/available-puppies/" label="See available puppies" /></div></div>}
  <div class="container grid">
    <div class="brand">
      <Mark variant={markVariant} size={variant === 'b' ? 56 : 40} title={`${SITE.site_name} mark`} />
      <p class="word">BlueStaffyUK<small>{SITE.location_label}</small></p>
      {variant !== 'c' && <p class="tag">{SITE.tagline}</p>}
    </div>
    {variant !== 'c' && <nav aria-label="Footer"><h2>Explore</h2><ul>{NAV.map((n) => <li><a href={n.href}>{n.label}</a></li>)}</ul></nav>}
    {(variant === 'a' || variant === 'e') && <div><h2>Contact</h2><ul><li><a href={`mailto:${SITE.email}`}>{SITE.email}</a></li><li>{SITE.hours}</li></ul></div>}
    {variant !== 'c' && <div><h2>Follow</h2><ul>{socials.map(([k, v]) => <li><a href={v} rel="noopener">{k === 'x' ? 'X' : k[0].toUpperCase() + k.slice(1)}</a></li>)}</ul></div>}
    {variant === 'c' && <ul class="inline">{NAV.slice(0, 4).map((n) => <li><a href={n.href}>{n.label}</a></li>)}</ul>}
  </div>
  <div class="container legal"><span>© {year} {SITE.site_name}</span>{legal.map((l) => <a href={l.href}>{l.label}</a>)}</div>
</footer>
<style>
  .kit-ftr { background: var(--color-surface-inverse); color: var(--color-text-on-inverse); padding-block: var(--space-8) var(--space-5); }
  .grid { display: grid; grid-template-columns: 1.4fr repeat(3, 1fr); gap: var(--space-6); }
  .kit-ftr-b .grid { grid-template-columns: 1fr 1fr 1fr; } .kit-ftr-b .brand { align-items: center; text-align: center; }
  .kit-ftr-c { padding-block: var(--space-5); } .kit-ftr-c .grid { grid-template-columns: auto 1fr; align-items: center; }
  .kit-ftr-e .grid { grid-template-columns: repeat(4, 1fr); } .kit-ftr-e .brand { grid-column: 1 / -1; }
  .brand { display: flex; flex-direction: column; gap: var(--space-2); }
  .word { margin: 0; font-family: var(--font-display); font-weight: 700; font-size: var(--text-xl); display: flex; flex-direction: column; }
  .word small { font-family: var(--font-body); font-weight: 600; font-size: var(--text-xs); letter-spacing: .12em; text-transform: uppercase; color: var(--color-link-on-inverse); }
  .tag { margin: 0; font-size: var(--text-sm); opacity: .85; max-width: 32ch; }
  h2 { margin: 0 0 var(--space-3); font-family: var(--font-body); font-size: var(--text-xs); letter-spacing: .12em; text-transform: uppercase; color: var(--color-cta); }
  ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--space-2); } .inline { display: flex; gap: var(--space-5); justify-content: flex-end; }
  a { color: inherit; text-decoration: none; display: inline-block; padding-block: 6px; min-height: 32px; } a:hover { color: var(--color-link-on-inverse); text-decoration: underline; }
  .legal { display: flex; gap: var(--space-5); justify-content: space-between; margin-top: var(--space-6); padding-top: var(--space-4); border-top: 1px solid rgba(255, 255, 255, .15); font-size: var(--text-xs); opacity: .85; }
  .cta-band { background: var(--color-surface-deep); margin: calc(-1 * var(--space-8)) 0 var(--space-8); padding-block: var(--space-6); }
  .cta-band .row { display: flex; align-items: center; justify-content: space-between; gap: var(--space-4); flex-wrap: wrap; } .cta-band p { margin: 0; font-family: var(--font-display); font-size: var(--text-xl); }
  @media (max-width: 800px) { .grid, .kit-ftr-b .grid, .kit-ftr-e .grid { grid-template-columns: 1fr 1fr; } .kit-ftr-c .grid { grid-template-columns: 1fr; } .inline { justify-content: flex-start; } }
  @media (max-width: 480px) { .grid, .kit-ftr-b .grid, .kit-ftr-e .grid { grid-template-columns: 1fr; } }
</style>
```

- [ ] **Step 2: Register, build, commit**

```bash
npm run build 2>&1 | tail -1 && python3 scripts/marker_check.py | tail -1
git add -A src
git commit -m "kit: SiteFooterKit in five variants

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 16: Kit complete — drop the xfails, full suite, render baseline

**Files:**
- Modify: `tests/py/test_design_components.py` (remove both `xfail` markers)

- [ ] **Step 1: Remove the markers and run**

Run: `npm run build 2>&1 | tail -1 && python3 -m pytest tests/py/test_design_components.py -q`
Expected: all passed, including `test_built_route_has_sixty_five_sections` and `test_kit_file_exists_for_each_row`.

- [ ] **Step 2: Full gates**

Run: `npm run check:all 2>&1 | tail -15 && npm run test:py 2>&1 | tail -2`
Expected: every gate at its recorded state or better; marker `0 problems`; placeholders may show `REVIEW_PLACEHOLDER` rows; pytest all green (count ≥ 1240 + the new tests).

- [ ] **Step 3: Render harness — pages**

Run: `npm run test:render:pages 2>&1 | tail -5 && node scripts/build_scorecard.mjs --run first 2>&1 | tail -6`
Expected: the `IMG` family's `img-srcset-within-2x` rows on the puppy pages are **0** (Task 7); no new blocking row in any other family versus `docs/reports/render-baseline-project2.md`. If a new blocking row appears, it is a kit defect: fix the component, do not add an override.

- [ ] **Step 4: Commit**

```bash
git add tests/py/test_design_components.py
git commit -m "kit: all thirteen components on the canvas route; 65 sections built

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 17: Canvas builder — artboards from `dist/`, publish the canvas

**Files:**
- Create: `scripts/build_design_canvas.py`, `tests/py/test_design_canvas_build.py`, `tests/py/fixtures/canvas-section.html`, `data/design/canvas-assets.json` (empty `{}`), `data/design/artifacts.json`
- Output: `docs/artifacts/canvas/project/*.dc.html`, `docs/artifacts/canvas/project/canvas.json` (gitignored: add `docs/artifacts/canvas/` to `.gitignore`; the canvas lives in the Artifact, the builder is the record)

- [ ] **Step 1: Write the failing test**

```python
# tests/py/test_design_canvas_build.py
"""build_design_canvas.py turns one built section into one Design-type artboard."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_design_canvas as B

FIX = ROOT / "tests/py/fixtures/canvas-section.html"


def test_sections_are_found_by_component_and_variant():
    secs = B.find_sections(FIX.read_text())
    assert [(s.component, s.variant) for s in secs] == [("buttons", "a"), ("buttons", "b")]
    assert secs[0].width == 640


def test_artboard_has_required_skeleton():
    secs = B.find_sections(FIX.read_text())
    html = B.artboard(secs[0], css=".kit-btn{min-height:44px}", fonts_link=B.FONTS_LINK, height=120, assets={})
    assert html.startswith("<!doctype html>")
    assert '<script src="./support.js"></script>' in html
    assert "<x-dc>" in html and "</x-dc>" in html
    assert 'data-dc-script' in html and '"$preview":{"width":640,"height":120}' in html
    assert "class Component extends DCLogic" in html
    assert "<iframe" not in html and "<script src=\"/" not in html


def test_assets_are_rewritten_to_blob_urls():
    secs = B.find_sections(FIX.read_text())
    html = B.artboard(secs[1], css="", fonts_link="", height=100, assets={"/_astro/roman.abc.jpg": "/_blob/deadbeef"})
    assert "/_blob/deadbeef" in html and "/_astro/roman.abc.jpg" not in html


def test_canvas_index_lays_out_rows():
    rows = [{"id": "buttons", "title": "3 · Buttons", "board_width": 640}]
    boards = [("buttons", v, 120) for v in "abcde"]
    idx = B.canvas_index("BlueStaffyUK Design Canvas", rows, boards, existing=None)
    assert idx["v"] == 3 and "createdOnFiles" in idx
    assert len(idx["boards"]) == 5 and len(idx["order"]) == 5
    xs = [idx["boards"][f"buttons-{v}.dc.html"]["x"] for v in "abcde"]
    assert xs == [0, 720, 1440, 2160, 2880]           # 640 wide + 80 gap
    assert list(idx["notes"].values())[0]["kind"] == "title1"
```

Fixture `tests/py/fixtures/canvas-section.html`:

```html
<html><body><main>
<section data-component="buttons" data-variant="a" data-width="640" class="kit-section"><h3>3 · Buttons — variant a</h3><a class="kit-btn" href="/x/">Meet</a></section>
<section data-component="buttons" data-variant="b" data-width="640" class="kit-section"><h3>3 · Buttons — variant b</h3><img src="/_astro/roman.abc.jpg" alt="Roman"></section>
</main></body></html>
```

- [ ] **Step 2: Run to see it fail**

Run: `python3 -m pytest tests/py/test_design_canvas_build.py -q`
Expected: `ModuleNotFoundError: build_design_canvas`.

- [ ] **Step 3: Write the builder**

```python
#!/usr/bin/env python3
"""build_design_canvas.py — dist/design-canvas/index.html → Design-type artboards.

Reads the built canvas route, writes one `.dc.html` per [data-component][data-variant]
section plus `canvas.json`, into docs/artifacts/canvas/project/. The controller then
publishes with the Artifact tool (url = the canvas, root = docs/artifacts/canvas,
file_path = project/canvas.json, files = every artboard). Images are uploaded once by the
controller; their /_blob/ urls are kept in data/design/canvas-assets.json and reused.

Usage: python3 scripts/build_design_canvas.py [--dist dist] [--out docs/artifacts/canvas]
       [--heights data/design/canvas-heights.json]
Heights come from scripts/measure_canvas_heights.mjs (Playwright) — run it first.
"""
import argparse, dataclasses, html as H, json, pathlib, re, sys, datetime as dt
ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
              'family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600&display=swap">')
SEC = re.compile(r'<section([^>]*)data-component="([a-z-]+)"([^>]*)data-variant="([a-e])"([^>]*)>(.*?)</section>', re.S)
WIDTH = re.compile(r'data-width="(\d+)"')
IMG_SRC = re.compile(r'(src|srcset)="([^"]+)"')


@dataclasses.dataclass
class Section:
    component: str
    variant: str
    width: int
    inner: str


def find_sections(html):
    out = []
    for m in SEC.finditer(html):
        attrs = m.group(1) + m.group(3) + m.group(5)
        w = WIDTH.search(attrs)
        out.append(Section(m.group(2), m.group(4), int(w.group(1)) if w else 1280, m.group(6).strip()))
    return out


def rewrite_assets(inner, assets):
    def sub(m):
        attr, val = m.group(1), m.group(2)
        if attr == "srcset":
            parts = []
            for cand in val.split(","):
                url, _, desc = cand.strip().partition(" ")
                parts.append((assets.get(url, url) + (" " + desc if desc else "")))
            return f'srcset="{", ".join(parts)}"'
        return f'{attr}="{assets.get(val, val)}"'
    return IMG_SRC.sub(sub, inner)


def artboard(sec, css, fonts_link, height, assets):
    inner = rewrite_assets(sec.inner, assets)
    inner = re.sub(r"<h3[^>]*>.*?</h3>\s*", "", inner, count=1, flags=re.S)   # the route's caption
    title = f"{sec.component} — variant {sec.variant}"
    props = json.dumps({"$preview": {"width": sec.width, "height": height}}, separators=(",", ":"))
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{H.escape(title)}</title>\n<script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n"
        f"{fonts_link}\n<style>\nbody{{margin:0;font-family:'Source Sans 3',system-ui,sans-serif;background:#F4F1EA}}\n"
        f"a{{color:#1F3A52}}a:hover{{color:#14202B}}\n{css}\n</style>\n</helmet>\n"
        f"<div style=\"width: {sec.width}px; height: {height}px; box-sizing: border-box; overflow: hidden; display: flex; flex-direction: column;\">\n"
        f"{inner}\n</div>\n</x-dc>\n"
        f"<script type=\"text/x-dc\" data-dc-script data-props='{props}'>\n"
        "class Component extends DCLogic {\n  renderVals() { return {}; }\n}\n</script>\n</body>\n</html>\n"
    )


def canvas_index(title, rows, boards, existing):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    idx = existing or {"v": 3, "createdOnFiles": {"v": 1, "at": now}, "title": title, "launch": {"view": "canvas"},
                       "pages": [], "boards": {}, "order": [], "notes": {}, "designSystems": []}
    idx["title"] = title
    idx["boards"], idx["order"] = {}, []
    idx["notes"] = {k: v for k, v in idx.get("notes", {}).items() if v.get("kind") != "title1"}
    y = 0
    heights = {(c, v): h for c, v, h in boards}
    for row in rows:
        w = row["board_width"]
        row_h = max(heights.get((row["id"], v), 200) for v in "abcde")
        idx["notes"][f"row-{row['id']}"] = {"x": 0, "y": y - 240, "text": row["title"], "kind": "title1", "maxW": 5 * w + 4 * 80}
        for i, v in enumerate("abcde"):
            f = f"{row['id']}-{v}.dc.html"
            idx["boards"][f] = {"x": i * (w + 80), "y": y, "w": w, "h": heights.get((row["id"], v), 200), "title": f"{row['title']} · {v}"}
            if row["id"] == "faq":
                idx["boards"][f]["is_interactive"] = True
            idx["order"].append(f)
        y += row_h + 120 + 240
    return idx


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=str(ROOT / "dist/design-canvas/index.html"))
    ap.add_argument("--out", default=str(ROOT / "docs/artifacts/canvas"))
    ap.add_argument("--heights", default=str(ROOT / "data/design/canvas-heights.json"))
    a = ap.parse_args(argv)
    html = pathlib.Path(a.dist).read_text()
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    assets = json.loads((ROOT / "data/design/canvas-assets.json").read_text())
    heights = json.loads(pathlib.Path(a.heights).read_text()) if pathlib.Path(a.heights).exists() else {}
    css_files = sorted((ROOT / "dist/_astro").glob("*.css"))
    css = "\n".join(f.read_text() for f in css_files)
    out = pathlib.Path(a.out) / "project"
    out.mkdir(parents=True, exist_ok=True)
    boards = []
    missing = set()
    for sec in find_sections(html):
        if sec.variant not in "abcde" or sec.component == "mark":
            continue
        for m in IMG_SRC.finditer(sec.inner):
            for cand in m.group(2).split(","):
                url = cand.strip().split(" ")[0]
                if url.startswith("/_astro/") and url not in assets:
                    missing.add(url)
        h = heights.get(f"{sec.component}-{sec.variant}", 200)
        (out / f"{sec.component}-{sec.variant}.dc.html").write_text(artboard(sec, css, FONTS_LINK, h, assets))
        boards.append((sec.component, sec.variant, h))
    idx_path = out / "canvas.json"
    existing = json.loads(idx_path.read_text()) if idx_path.exists() else None
    idx_path.write_text(json.dumps(canvas_index("BlueStaffyUK Design Canvas", rows, boards, existing), indent=1))
    print(f"wrote {len(boards)} artboards + canvas.json to {out}")
    if missing:
        print("UPLOAD FIRST (then add to data/design/canvas-assets.json):")
        for u in sorted(missing):
            print("  ", u)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

The Section dataclass reads the `data-width` attribute the route sets, so keep `data-width={c.board_width}` on the route (Task 5 already does).

- [ ] **Step 4: Heights measurer**

`scripts/measure_canvas_heights.mjs`:

```js
// Measures each [data-component][data-variant] section's rendered height at its board
// width, so canvas.json frames fit. Run after `npm run build`; writes data/design/canvas-heights.json.
import { chromium } from '@playwright/test';
import { readFileSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { join, extname } from 'node:path';
const dist = new URL('../dist/', import.meta.url).pathname;
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml' };
const srv = createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  try { const b = readFileSync(join(dist, p)); res.writeHead(200, { 'content-type': types[extname(p)] ?? 'application/octet-stream' }); res.end(b); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = srv.address().port;
const browser = await chromium.launch();
const out = {};
for (const width of [640, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(`http://127.0.0.1:${port}/design-canvas/`, { waitUntil: 'networkidle' });
  const rows = await page.$$eval(`section[data-width="${width}"]`, (els) => els.map((e) => {
    const h3 = e.querySelector('h3'); const cap = h3 ? h3.getBoundingClientRect().height : 0;
    return [e.dataset.component + '-' + e.dataset.variant, Math.ceil((e.getBoundingClientRect().height - cap) / 8) * 8 + 16];
  }));
  for (const [k, h] of rows) out[k] = Math.max(h, 80);
  await page.close();
}
await browser.close(); srv.close();
writeFileSync(new URL('../data/design/canvas-heights.json', import.meta.url), JSON.stringify(out, null, 1));
console.log(`measured ${Object.keys(out).length} sections`);
```

Add to `package.json` scripts: `"canvas:heights": "node scripts/measure_canvas_heights.mjs"`, `"canvas:build": "python3 scripts/build_design_canvas.py"`. Run `python3 -m pytest tests/py/test_package_scripts.py -q` and register the two names wherever that test lists the script surface.

- [ ] **Step 5: Run the unit tests, then the real build**

Run: `python3 -m pytest tests/py/test_design_canvas_build.py -q && npm run build 2>&1 | tail -1 && npm run canvas:heights && npm run canvas:build`
Expected: 4 passed; `measured 65 sections`; the builder exits 2 listing the `/_astro/…` image URLs to upload (puppy photos, hero).

- [ ] **Step 6: Upload assets (controller step, Artifact tool)**

For each listed URL, the file is `dist<url>`. The controller runs, per file: `Artifact publish {url: "https://claude.ai/artifact/TAc7sSMqtcANRq9ujEQ5uR", file_path: "<abs path to dist/_astro/…>", asset: true}` and records `"<url>": "<returned /_blob/ url>"` in `data/design/canvas-assets.json`. Then re-run `npm run canvas:build`; expected exit 0, `wrote 65 artboards + canvas.json`.

- [ ] **Step 7: Publish the canvas (controller step)**

One Artifact call: `{url: "https://claude.ai/artifact/TAc7sSMqtcANRq9ujEQ5uR", root: "/Users/apple/Downloads/BSUK/docs/artifacts/canvas", file_path: "/Users/apple/Downloads/BSUK/docs/artifacts/canvas/project/canvas.json", files: {"project/<name>.dc.html": "project/<name>.dc.html", … all 65 …}}`. Write `data/design/artifacts.json`:

```json
{"canvas": "https://claude.ai/artifact/TAc7sSMqtcANRq9ujEQ5uR", "picks_board": null, "design_system": null}
```

- [ ] **Step 8: Commit**

```bash
echo "docs/artifacts/canvas/" >> .gitignore
git add scripts/build_design_canvas.py scripts/measure_canvas_heights.mjs tests/py/test_design_canvas_build.py tests/py/fixtures/canvas-section.html data/design package.json .gitignore
git commit -m "canvas: builder from dist sections to Design-type artboards; heights measurer; 65 boards published

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 18: Picks board (db) and the pull script

**Files:**
- Create: `scripts/build_picks_board.py`, `docs/artifacts/design-picks.html` (generated, committed), `scripts/pull_design_picks.py`, `tests/py/test_design_picks.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/py/test_design_picks.py
"""picks.json is the record of the user's thirteen picks. Skipped until it exists
(spec §6); after Task 19 the prune invariants must hold too."""
import json, pathlib, re, subprocess, sys
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[2]
PICKS = ROOT / "data/design/picks.json"
KIT = ROOT / "src/components/kit"
IDS = [r["id"] for r in json.loads((ROOT / "data/design/components.json").read_text())]


def test_pull_script_converts_inbox_rows(tmp_path):
    inbox = tmp_path / "inbox.json"
    rows = {f"picks/{i}": {"component": i, "variant": "c", "note": "", "at": "2026-09-19T10:00:00Z", "by": "u"} for i in IDS}
    inbox.write_text(json.dumps(rows))
    out = tmp_path / "picks.json"
    r = subprocess.run([sys.executable, str(ROOT / "scripts/pull_design_picks.py"), "--inbox", str(inbox), "--out", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    d = json.loads(out.read_text())
    assert set(d["picks"]) == set(IDS) and all(v["variant"] == "c" for v in d["picks"].values())


def test_pull_script_refuses_an_incomplete_set(tmp_path):
    inbox = tmp_path / "inbox.json"
    inbox.write_text(json.dumps({"picks/hero": {"component": "hero", "variant": "a"}}))
    r = subprocess.run([sys.executable, str(ROOT / "scripts/pull_design_picks.py"), "--inbox", str(inbox), "--out", str(tmp_path / "p.json")], capture_output=True, text=True)
    assert r.returncode == 2 and "missing" in r.stdout


@pytest.mark.skipif(not PICKS.exists(), reason="picks.json arrives after the user picks (spec §6)")
def test_picks_json_is_complete_and_valid():
    d = json.loads(PICKS.read_text())
    assert set(d["picks"]) == set(IDS)
    assert all(v["variant"] in "abcde" for v in d["picks"].values())
    assert "mark" in d and d["mark"] in "abcde"


@pytest.mark.skipif(not PICKS.exists() or (KIT / "_variant.ts").exists(), reason="prune (Task 19) not run yet")
def test_after_prune_no_variant_prop_remains():
    for f in KIT.glob("*.astro"):
        assert "variant" not in f.read_text(), f.name
    assert not (ROOT / "src/pages/design-canvas").exists()
```

- [ ] **Step 2: Run to see it fail**

Run: `python3 -m pytest tests/py/test_design_picks.py -q`
Expected: 2 failed (no pull script), 2 skipped.

- [ ] **Step 3: Write the pull script**

```python
#!/usr/bin/env python3
"""pull_design_picks.py — picks-board database rows → data/design/picks.json.

Operator step first (a Python script cannot call the Artifact tool): read every
`picks/<component>` doc and the `picks/mark` doc from the picks board's database with the
ArtifactData tool into data/design/inbox/picks.json as {"picks/<id>": {...}, ...}.
Then: python3 scripts/pull_design_picks.py
Refuses (exit 2) unless all thirteen components and the mark are present.
"""
import argparse, datetime as dt, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default=str(ROOT / "data/design/inbox/picks.json"))
    ap.add_argument("--out", default=str(ROOT / "data/design/picks.json"))
    a = ap.parse_args(argv)
    ids = [r["id"] for r in json.loads((ROOT / "data/design/components.json").read_text())]
    rows = json.loads(pathlib.Path(a.inbox).read_text())
    picks, bad = {}, []
    for i in ids:
        r = rows.get(f"picks/{i}")
        if not r or r.get("variant") not in list("abcde"):
            bad.append(i); continue
        picks[i] = {"variant": r["variant"], "note": (r.get("note") or "").strip(), "at": r.get("at"), "by": r.get("by")}
    mark = (rows.get("picks/mark") or {}).get("variant")
    if mark not in list("abcde"):
        bad.append("mark")
    if bad:
        print(f"missing or invalid picks: {', '.join(bad)}")
        return 2
    out = {"pulled_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "mark": mark, "picks": picks}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {len(picks)} picks + mark {mark} to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write the picks board builder**

```python
#!/usr/bin/env python3
"""build_picks_board.py — the picks board: one row per component (+ the mark), five pick
buttons, a note, Save writes {component, variant, note, at, by} to db doc picks/<id>.
Same db mechanism as docs/artifacts/boards/index.html (window.claude.use("db")).
Output: docs/artifacts/design-picks.html — published by the controller with the db capability
{"rules":[{"path":"","write":"admin"}]} and the canvas URL for the row links.
"""
import html as H, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = json.loads((ROOT / "data/design/components.json").read_text())
arts = json.loads((ROOT / "data/design/artifacts.json").read_text())
rows = [{"id": "mark", "title": "0 · The mark"}] + rows
CANVAS = arts["canvas"]

def row_html(r):
    btns = "".join(f'<label><input type="radio" name="pick-{r["id"]}" value="{v}"><span>{v.upper()}</span></label>' for v in "abcde")
    return (f'<section class="row" data-id="{r["id"]}"><h2>{H.escape(r["title"])} <a href="{CANVAS}" target="_blank" rel="noopener">canvas ↗</a></h2>'
            f'<div class="picks">{btns}</div><textarea name="note-{r["id"]}" placeholder="What you would change (optional)"></textarea>'
            f'<div class="bar"><button class="btn" data-save="{r["id"]}">Save pick</button><span class="st" id="st-{r["id"]}"></span></div></section>')

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BSUK Design Picks</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Source+Sans+3:wght@400;600&display=swap">
<style>
:root{{--ground:#F4F1EA;--paper:#fff;--ink:#1B2430;--line:#DAD6CC;--brand:#1F3A52;--cta:#C9A227;--ok:#2F6B4F}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--line:#2C3743;--brand:#8FB3D9}}}}
:root[data-theme="dark"]{{--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--line:#2C3743;--brand:#8FB3D9}}
body{{margin:0;background:var(--ground);color:var(--ink);font:16px/1.5 "Source Sans 3",system-ui,sans-serif}}
.wrap{{max-width:880px;margin:0 auto;padding:32px 16px 96px}} h1{{font-family:Fraunces,serif;color:var(--brand);margin:0 0 8px}}
.row{{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}}
.row h2{{font-family:Fraunces,serif;font-size:20px;margin:0 0 10px;display:flex;justify-content:space-between;align-items:baseline}} .row h2 a{{font:600 13px "Source Sans 3",sans-serif;color:var(--brand)}}
.picks{{display:flex;gap:8px;flex-wrap:wrap}} .picks label{{cursor:pointer}} .picks input{{position:absolute;opacity:0}}
.picks span{{display:inline-grid;place-items:center;min-width:48px;min-height:44px;border:2px solid var(--line);border-radius:50px;font-weight:600}}
.picks input:checked+span{{background:var(--cta);border-color:var(--cta);color:#14202B}} .picks input:focus-visible+span{{outline:3px solid var(--brand);outline-offset:2px}}
textarea{{width:100%;box-sizing:border-box;margin:12px 0;padding:10px;border:1px solid var(--line);border-radius:6px;font:inherit;min-height:60px;background:var(--paper);color:var(--ink)}}
.bar{{display:flex;gap:12px;align-items:center}} .btn{{font:600 14px "Source Sans 3",sans-serif;padding:10px 18px;border-radius:50px;border:0;background:var(--brand);color:#fff;cursor:pointer;min-height:44px}}
.st{{font-size:13px;color:var(--ok)}}
</style></head><body><div class="wrap">
<h1>BlueStaffyUK design picks</h1><p>Open the canvas, look at a row, pick the variant here, save. Each row saves on its own; you can come back later.</p>
{''.join(row_html(r) for r in rows)}
</div>
<script>
(function(){{
  var stAll=function(id,t){{document.getElementById('st-'+id).textContent=t;}};
  if(!window.claude||!window.claude.use){{document.querySelectorAll('.st').forEach(function(s){{s.textContent='Open inside claude.ai to save picks.';}});return;}}
  window.claude.use("db").then(function(db){{
    if(!db){{return;}}
    document.querySelectorAll('.row').forEach(function(row){{
      var id=row.dataset.id, ref=db.doc('picks/'+id);
      ref.get().then(function(snap){{
        if(!snap||!snap.exists)return; var d=snap.data()||{{}};
        var r=row.querySelector('input[value="'+d.variant+'"]'); if(r)r.checked=true;
        row.querySelector('textarea').value=d.note||''; stAll(id,'Saved '+(d.at||'').slice(0,16).replace('T',' '));
      }}).catch(function(){{}});
      row.querySelector('[data-save]').addEventListener('click',function(){{
        var p=row.querySelector('input:checked'); if(!p){{stAll(id,'Pick a variant first.');return;}}
        var rec={{component:id,variant:p.value,note:row.querySelector('textarea').value.trim(),at:new Date().toISOString(),by:'owner'}};
        ref.set(rec).then(function(){{stAll(id,'Saved '+rec.at.slice(0,16).replace('T',' '));}}).catch(function(e){{stAll(id,'Could not save: '+(e&&e.code?e.code:'error'));}});
      }});
    }});
  }});
}})();
</script></body></html>"""
out = ROOT / "docs/artifacts/design-picks.html"
out.write_text(page)
print(f"{out.relative_to(ROOT)} {len(page)} bytes, {len(rows)} rows")
```

Compare with `docs/artifacts/boards/index.html` lines 310–340 for the exact `db.doc(...).get()/.set()` shapes and match them if they differ (e.g. `snap.exists` vs `snap.exists()`).

- [ ] **Step 5: Build, publish (controller), record the URL, test, commit**

Run: `python3 scripts/build_picks_board.py && python3 -m pytest tests/py/test_design_picks.py -q`
Expected: file written; 2 passed, 2 skipped.

Controller publishes `docs/artifacts/design-picks.html` as a new Artifact (favicon `🐾`), loading `artifact-capabilities` first and passing `capabilities: {"db": {"rules": [{"path": "", "write": "admin"}]}}` exactly as the project 2 board did. Set `picks_board` in `data/design/artifacts.json` to the returned URL.

```bash
git add scripts/build_picks_board.py scripts/pull_design_picks.py docs/artifacts/design-picks.html tests/py/test_design_picks.py data/design/artifacts.json
git commit -m "picks: board with shared db, pull script to picks.json

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [ ] **Step 6: PAUSE — the user picks**

Session-closer for this pause: tell the user the canvas URL, the picks board URL, and that thirteen picks plus the mark are needed. Execution resumes at Task 19 when `data/design/inbox/picks.json` has been read from the board with ArtifactData and `python3 scripts/pull_design_picks.py` exits 0.

---

### Task 19: Prune to the picked variants

**Files:**
- Create: `scripts/prune_variants.py`
- Modify: every `src/components/kit/*.astro`; delete `src/components/kit/_variant.ts`, `src/pages/design-canvas/`

- [ ] **Step 1: Pull the picks**

Run: `python3 scripts/pull_design_picks.py && python3 -m pytest tests/py/test_design_picks.py -q`
Expected: `wrote 13 picks + mark <v>`; 3 passed, 1 skipped (the post-prune test).

- [ ] **Step 2: Write the prune script**

```python
#!/usr/bin/env python3
"""prune_variants.py — keep only the picked variant in each kit component.

Mechanical part: rewrites `const { variant = 'a', ...` to `const variant = '<pick>' as const;`
(so every `variant === 'x'` branch becomes statically true/false), deletes the `_variant.ts`
import and the `variant?: Variant;` prop line, removes the canvas route, and prints a checklist
of files. The HUMAN part — deleting the now-dead branches and the dead CSS — is done by the
implementer, file by file, and reviewed; tests/py/test_design_picks.py refuses any file that
still contains the word `variant`.
"""
import json, pathlib, re, shutil, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
picks = json.loads((ROOT / "data/design/picks.json").read_text())
rows = json.loads((ROOT / "data/design/components.json").read_text())
KIT = ROOT / "src/components/kit"
mark = picks["mark"]
for r in rows + [{"id": "mark", "file": "Mark.astro"}]:
    f = KIT / r["file"]
    t = f.read_text()
    v = mark if r["id"] == "mark" else picks["picks"][r["id"]]["variant"]
    t = re.sub(r"import type \{ Variant \} from './_variant';\n", "", t)
    t = re.sub(r"\s*variant\?: Variant;?", "", t)
    t = re.sub(r"\s*markVariant\?: Variant;?", "", t)
    t = re.sub(r"const \{ variant = '[a-e]',?\s*", f"const variant = '{v}' as const;\nconst {{ ", t, count=1)
    t = t.replace("markVariant = 'a', ", "").replace("markVariant = 'a' ", "")
    t = t.replace("markVariant={markVariant}", "").replace(" variant={markVariant}", "")
    t = t.replace("const { } = Astro.props;", "").replace("const {  } = Astro.props;", "")
    f.write_text(t)
    print(f"{r['file']}: pinned to '{v}' — now delete dead branches and CSS by hand")
(KIT / "_variant.ts").unlink(missing_ok=True)
shutil.rmtree(ROOT / "src/pages/design-canvas", ignore_errors=True)
print("removed _variant.ts and src/pages/design-canvas/")
```

- [ ] **Step 3: Run it, then finish each file by hand**

Run: `python3 scripts/prune_variants.py`. Then for each of the fourteen files: delete every `{variant === 'x' && …}` / ternary branch that is not the pick (keep the picked branch's markup inline, unwrapped), delete the `data-variant` attributes, delete the `.kit-*-x` CSS rules for the other letters, delete the `const variant = …` line once nothing reads it, and delete the variant comment block at the top, replacing it with one line naming the pick and the date. `Button.astro` keeps a `kind` prop instead (`'primary' | 'outline' | 'inverse' | 'submit' | 'text'`) because pages need more than one button treatment: rename `byVariant` to `byKind` with those keys, default `'primary'`. `SectionDivider.astro`, `Hero.astro` and `InfoCard.astro` likewise keep only the picked layout.

- [ ] **Step 4: Verify**

Run: `npm run build 2>&1 | tail -1 && python3 -m pytest tests/py/test_design_picks.py tests/py/test_design_components.py tests/py/test_design_tokens.py -q && grep -rl "variant" src/components/kit/ | wc -l`
Expected: `49 page(s) built`; all passed (the post-prune test now runs and passes); `0`. The `test_route_is_noindex…` and `test_built_route…` tests in `test_design_components.py` must be deleted in this task (the route is gone); replace them with `test_no_canvas_route_after_prune` asserting `not (ROOT / "src/pages/design-canvas").exists()`.

- [ ] **Step 5: Commit**

```bash
git add -A src scripts/prune_variants.py tests/py data/design/picks.json data/design/inbox
git commit -m "kit: pruned to the picked variants; canvas route removed

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

**Task 19 prune notes (from the Task 15 quality review).**

Measured on the finished kit at Task 15: `grep -ro "variant ===" src/components/kit/ src/pages/design-canvas/ | wc -l` = **68 sites across 14 files**. The prune is therefore NOT a scripted rewrite. `scripts/prune_variants.py` FINDS THE CANDIDATES with a regex and each file is then collapsed BY HAND, because every one of the shapes below breaks a naive `variant === 'x'` substitution:

- **Multi-line destructures.** `Hero.astro`, `InfoCard.astro` and `PageNav.astro` destructure their props over several lines, so the `variant = 'a'` default is not on the same line as `const {`. A line-oriented edit removes the default and leaves a dangling comma.
- **`Button.astro` destructures twice.** `Astro.props` is cast (`as Props & { class?: string }`) and `type` is pulled out of `rest` in a second statement, so there are two places a prop list changes shape.
- **`markVariant` is a SECOND variant prop.** `SiteHeaderKit.astro`, `SiteFooterKit.astro` and `SectionDivider.astro` each take `markVariant` and pass it to `Mark.astro`. It is coupled to the MARK's pick, not to their own, so the three must be collapsed against `picks['mark']` and not against their own row — and `Mark.astro` must be pruned before or with them.
- **`Faq.astro` defaults a prop to a function call.** `items = loadFaq()` is evaluated in the destructure; the variant collapse must not disturb it.
- **`ContactFormKit.astro` nests ternaries in the template.** `variant === 'c' ? … : (variant === 'b' ? … : …)` spans a large JSX block, and the `rows={variant === 'e' ? 3 : 5}` attribute sits inside it. Collapsing the outer branch without the inner one leaves unreachable markup that still compiles.
- **`SiteFooterKit.astro` computes a value in the frontmatter.** `const explore = variant === 'c' ? NAV.slice(0, 4) : NAV;` is a variant branch OUTSIDE the template, which a template-only pass will miss entirely.
- **`ContactFormKit.astro` carries a canvas-only prop.** Its `action` override exists so the canvas specimens post nowhere; when the route goes, so do the override, its comment and the registry fixture that passes it.
- **`scripts/form_contract_audit.py` names the route.** `NON_CONTENT_ROUTES = ("design-canvas",)` must lose that name in this same commit — `tests/py/test_form_contract_audit.py::test_every_excluded_route_still_exists_as_a_page` fails until it does, which is the point of that test. `LOCAL_STUB_ACTION` and the stub allowance go with it.
- **`PageNav.astro` variant b leaves a note behind.** b's `<nav data-pinned-chrome>` marks pinned chrome the global `[id] { scroll-margin-top }` does not clear. If b is the pick, project 4 has to extend that offset; if it is not, the attribute and its header paragraph go.

Verification is per FILE, not in aggregate: `for f in src/components/kit/*.astro; do echo "$f $(grep -c variant "$f")"; done` must print `0` for every file (`grep -c` counts the bare word, so a surviving comment about variants fails it too), and the Step 4 run above re-checks the built site.


---

### Task 20: Logo lockups, favicons, header and footer

**Files:**
- Create: `public/brand/logo-horizontal.svg`, `logo-stacked.svg`, `logo-icon.svg`, `logo-mono.svg`, `scripts/build_favicons.py`, `tests/py/test_brand_assets.py`
- Modify: `src/components/SiteHeader.astro`, `src/components/SiteFooter.astro`, `src/layouts/BaseLayout.astro` (favicon links), `data/settings.json` (`logo`, `logo_header`), `data/image-manifest.json`; delete `public/images/blue-staffy-uk-official-logo0.png`, `public/images/blue-staffy-uk-header-logo-88.webp`

- [ ] **Step 1: Write the failing test**

```python
# tests/py/test_brand_assets.py
"""Four SVG lockups, four favicon renders, header/footer on the SVG logo, no raster logo left."""
import json, pathlib, re
import xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parents[2]
BRAND = ROOT / "public/brand"
LOCKUPS = ["logo-horizontal.svg", "logo-stacked.svg", "logo-icon.svg", "logo-mono.svg"]
FAVS = ["favicon.svg", "favicon-32.png", "apple-touch-icon.png", "icon-512.png"]


def test_lockups_exist_parse_and_carry_a_title():
    for f in LOCKUPS:
        p = BRAND / f
        assert p.exists(), f
        root = ET.fromstring(p.read_bytes())
        assert root.tag.endswith("svg")
        assert any(el.tag.endswith("title") for el in root.iter()), f
        assert not any(el.tag.endswith("text") for el in root.iter()), f"{f} must outline its text"
        assert not any(el.tag.endswith("image") for el in root.iter()), f


def test_mono_uses_currentcolor_only():
    t = (BRAND / "logo-mono.svg").read_text()
    assert "currentColor" in t and not re.search(r"#[0-9a-fA-F]{3,6}", t)


def test_favicons_exist():
    for f in FAVS:
        assert (ROOT / "public" / f).exists(), f


def test_settings_and_shell_use_the_svg_logo():
    s = json.loads((ROOT / "data/settings.json").read_text())
    assert s["logo"] == "/brand/logo-stacked.svg" and s["logo_header"] == "/brand/logo-horizontal.svg"
    for f in ("SiteHeader.astro", "SiteFooter.astro"):
        assert "logo" in (ROOT / "src/components" / f).read_text().lower()
    src = "\n".join(p.read_text() for p in (ROOT / "src").rglob("*.astro"))
    assert "blue-staffy-uk-official-logo0.png" not in src and "header-logo-88.webp" not in src
    assert not (ROOT / "public/images/blue-staffy-uk-official-logo0.png").exists()
```

- [ ] **Step 2: Run to see it fail**

Run: `python3 -m pytest tests/py/test_brand_assets.py -q`
Expected: 4 failed.

- [ ] **Step 3: Draw the lockups**

Take the picked head's paths from `src/components/kit/Mark.astro` verbatim. For the wordmark, set `BlueStaffyUK` in Fraunces 700 and `CARLISLE · CUMBRIA` in Source Sans 3 600 and convert to outlines with fontTools:

```bash
pip3 install fonttools >/dev/null 2>&1
python3 - <<'EOF'
# Outlines the wordmark/strapline glyphs into SVG <path> data. Fonts: download Fraunces and
# Source Sans 3 TTFs from Google Fonts (github.com/google/fonts, OFL) into /tmp/fonts first.
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
def outline(font_path, text, size, x=0, y=0):
    f = TTFont(font_path); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
    s = size / upm; out = []; cx = x
    for ch in text:
        g = cmap.get(ord(ch)); 
        if g is None: cx += size*0.28; continue
        pen = SVGPathPen(gs); gs[g].draw(pen); d = pen.getCommands()
        if d: out.append(f'<path transform="translate({cx:.1f},{y:.1f}) scale({s:.4f},{-s:.4f})" d="{d}"/>')
        cx += gs[g].width * s
    return "\n".join(out), cx
word, w1 = outline('/tmp/fonts/Fraunces[SOFT,WONK,opsz,wght].ttf', 'BlueStaffyUK', 34, 0, 30)
strap, w2 = outline('/tmp/fonts/SourceSans3-SemiBold.ttf', 'CARLISLE · CUMBRIA', 11, 0, 46)
open('/tmp/word.svg','w').write(word); open('/tmp/strap.svg','w').write(strap); print(w1, w2)
EOF
```

If the variable font has no `wght=700` instance by default, instantiate it first with `fontTools.varLib.instancer` (`instantiateVariableFont(font, {"wght": 700, "opsz": 72})`).

Compose `public/brand/logo-horizontal.svg` (`viewBox="0 0 320 64"`): a `<title>BlueStaffyUK — Carlisle, Cumbria</title>`, a `<g fill="none" stroke="#1F3A52" …>` holding the mark paths at `translate(0,0)`, then `<g fill="#1F3A52" transform="translate(76,0)">` with the wordmark paths and `<g fill="#5B7C99" transform="translate(76,0)">` with the strapline paths. `logo-stacked.svg` (`viewBox="0 0 220 140"`): mark centred at top (`translate(78,0)`), wordmark centred below, strapline under it. `logo-icon.svg` (`viewBox="0 0 64 64"`): `<rect width="64" height="64" rx="14" fill="#1F3A52"/>` then the mark in `stroke="#C9A227"` at `transform="translate(6,6) scale(0.8125)"`. `logo-mono.svg`: the horizontal composition with every `fill`/`stroke` set to `currentColor`. These four files are the only places outside `tokens.css` that may spell a brand hex; `test_kit_has_no_hex_literals` scans `src/` only.

- [ ] **Step 4: Favicon script**

```python
#!/usr/bin/env python3
"""build_favicons.py — public/brand/logo-icon.svg → favicon.svg, favicon-32.png,
apple-touch-icon.png (180), icon-512.png. Idempotent; needs cairosvg + Pillow."""
import pathlib, shutil, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "public/brand/logo-icon.svg"
try:
    import cairosvg
except ImportError:
    print("pip3 install cairosvg pillow"); sys.exit(2)
shutil.copyfile(SRC, ROOT / "public/favicon.svg")
for name, px in (("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)):
    cairosvg.svg2png(url=str(SRC), write_to=str(ROOT / "public" / name), output_width=px, output_height=px)
    print("wrote", name)
```

Run `pip3 install cairosvg pillow` if needed, then `python3 scripts/build_favicons.py`. Add `"brand:favicons": "python3 scripts/build_favicons.py"` to `package.json`.

- [ ] **Step 5: Wire the shell**

In `src/components/SiteHeader.astro` replace the `<img src={SITE.logo_header} …>` + `<span>` with the inline SVG: read `public/brand/logo-horizontal.svg` at build time (`import { readFileSync } from 'node:fs'; const logo = readFileSync(new URL('../../public/brand/logo-horizontal.svg', import.meta.url), 'utf8');`) and render `<Fragment set:html={logo} />` inside the `<a href="/">`, with `aria-label={`${SITE.site_name} home`}` on the `<a>` and `height="44"` enforced by CSS (`.site-header svg { height: 44px; width: auto; }`). Do the same in `SiteFooter.astro` with `logo-stacked.svg` at 96px. In `BaseLayout.astro` `<head>` replace any existing favicon link with:

```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

Set `settings.json` `logo` / `logo_header` to the two SVG paths; check `grep -rn "SITE.logo" src/` for JSON-LD and OG uses — JSON-LD `logo` and `og:image` need a raster: point those at `/icon-512.png`. Delete the two raster logos and their `image-manifest.json` rows.

- [ ] **Step 6: Build, gates, tests, commit**

Run: `npm run build 2>&1 | tail -1 && python3 scripts/schema_check.py | tail -1 && python3 scripts/redirect_check.py | tail -1 && python3 -m pytest tests/py/test_brand_assets.py tests/py/test_images.py tests/py/test_data_files.py -q && grep -rl "&lt;svg" dist/ | wc -l`
Expected: build clean; `0 blocking, 0 advisory`; `0 problems`; tests green; `0` (rule 7's `set:html` check).

```bash
git add -A public src data scripts/build_favicons.py tests/py/test_brand_assets.py package.json
git commit -m "brand: four SVG lockups from the picked mark, favicons, header/footer on the SVG logo

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 21: Promote the three deferred checks

**Files:**
- Modify: `tests/render/targets.json` (`deferred_checks`), `src/pages/index.astro` (mount `CounterStrip` and `SectionDivider` below the migrated hero — the only shell change to a page in project 3), `docs/reports/render-baseline-project3.md`

- [ ] **Step 1: Give the checks nodes to examine**

The three checks need a built page that carries the convention. In `src/pages/index.astro`, immediately after the existing hero block, insert `<CounterStrip />` and after the first migrated `<section>` insert `<SectionDivider />` (imports from `../components/kit/`). Also add one `<InfoCard label="Health" title="What a health-tested litter means" body="…" />` (with `.stmt-label` and, if the picked InfoCard variant is `d`, the `.sec-img`) at the end of the homepage main. If the picked InfoCard is not `d`, add a `sec-img`-carrying `<figure>` under the first migrated H3 on `src/pages/blue-staffy-health-uk/index.astro` instead, using an existing image from that page. This adds components, not copy: parity must still pass (words unchanged; `migration_parity.py` scopes to `article.prose-migrated`).

- [ ] **Step 2: Remove the three `deferred_checks` entries** from `tests/render/targets.json`, leaving the `_deferred_comment` and an empty object `"deferred_checks": {}`.

- [ ] **Step 3: Build, run parity, the harness twice, the baseline**

Run: `npm run build 2>&1 | tail -1 && python3 scripts/migration_parity.py | tail -1 && npm run test:render:meta 2>&1 | tail -3 && npm run test:render:pages 2>&1 | tail -3 && node scripts/build_scorecard.mjs --run first 2>&1 | tail -8`
Expected: parity `0 failing`; meta green with no `DEFERRED` line; Guard 2 passes because each promoted check now examines ≥1 node; pages run shows no new blocking row (`layout-hero-counter-separation` is advisory).

Then: `python3 scripts/render_baseline.py --write --out docs/reports/render-baseline-project3.md && python3 scripts/render_baseline.py --check --out docs/reports/render-baseline-project3.md | tail -1` (check the script's real flag names with `--help` first; if it hard-codes `project2`, add an `--out` argument in this task and keep the project 2 file untouched). Expected: `0 problems`.

- [ ] **Step 4: Commit**

```bash
git add -A src tests/render/targets.json docs/reports/render-baseline-project3.md scripts/render_baseline.py data/quality/scorecards
git commit -m "harness: promote the three deferred checks; project 3 render baseline

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 22: Design System artifact

**Files:**
- Create: `scripts/build_design_system.py`, output folder `docs/artifacts/design-system/project/` (gitignored like the canvas), `tests/py/test_design_system_build.py`

- [ ] **Step 1: Create the artifact and read its instructions (controller step)**

`Artifact publish {type_url: "https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd", title: "BlueStaffyUK Design System", auto_open: "after_first_write"}`. Read the returned instructions: they define the exact `project/tokens.json` shape and what else the type serves (README, `tokens.css`, components). Record the URL in `data/design/artifacts.json` as `design_system`. **Amend spec §7 and this task's Step 3 to the type's real shape before writing code** (spec §11 amendment 2).

- [ ] **Step 2: Write the failing test**

```python
# tests/py/test_design_system_build.py
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_design_system as D


def test_tokens_json_carries_primitive_and_semantic_layers():
    t = D.tokens_json()
    names = {x["name"] for x in t["tokens"]}
    assert "color-steel-700" in names and "color-cta" in names and "font-display" in names
    cta = next(x for x in t["tokens"] if x["name"] == "color-cta")
    assert cta["value"].startswith("#") and cta["alias"] == "color-brass-500"


def test_readme_names_the_locked_facts_and_no_glasgow():
    r = D.readme()
    for s in ("Fraunces", "Source Sans 3", "#1F3A52", "#C9A227", "Carlisle", "£1,500", "£1,700", "namespace `bsuk`", "PLACEHOLDER"):
        assert s in r, s
    assert "Glasgow" not in r
```

- [ ] **Step 3: Write the builder** (adjust `tokens_json()` to the type's shape from Step 1)

```python
#!/usr/bin/env python3
"""build_design_system.py — tokens.css + picks.json + public/brand → the Design System
artifact's files under docs/artifacts/design-system/project/: tokens.json, tokens.css,
README.md, and one reference artboard per picked component copied from the canvas build.
The controller publishes them with the Artifact tool (url = design_system in artifacts.json).
"""
import json, pathlib, re, shutil, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
TOK = ROOT / "src/styles/tokens.css"
DECL = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")
OUT = ROOT / "docs/artifacts/design-system/project"


def layers():
    text = TOK.read_text()
    parts = re.split(r"/\*\s*@layer-(primitive|semantic|component)\s*\*/", text)
    return {parts[i]: dict(DECL.findall(parts[i + 1])) for i in range(1, len(parts), 2)}


def resolve(v, L):
    m = re.fullmatch(r"var\((--[a-z0-9-]+)\)", v.strip())
    if not m: return v.strip()
    for layer in ("component", "semantic", "primitive"):
        if m.group(1) in L[layer]: return resolve(L[layer][m.group(1)], L)
    return v


def tokens_json():
    L = layers(); toks = []
    for layer in ("primitive", "semantic", "component"):
        for k, v in L[layer].items():
            alias = re.fullmatch(r"var\((--[a-z0-9-]+)\)", v.strip())
            toks.append({"name": k.lstrip("-"), "layer": layer, "value": resolve(v, L), "alias": alias.group(1).lstrip("-") if alias else None,
                         "type": "color" if k.startswith("--color") else "font" if k.startswith("--font") else "dimension" if k.startswith(("--space", "--radius", "--text")) else "other"})
    return {"name": "BlueStaffyUK", "namespace": "bsuk", "tokens": toks}


def readme():
    picks = json.loads((ROOT / "data/design/picks.json").read_text())
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    s = json.loads((ROOT / "data/settings.json").read_text())
    rules = (ROOT / "rules/design.md").read_text()
    nine = rules[rules.index("**Non-Negotiable Design Rules"):].split("\n---")[0]
    comp = "\n".join(f"- **{r['title'].split('· ',1)[1]}** — `src/components/kit/{r['file']}`, variant {picks['picks'][r['id']]['variant']}" for r in rows)
    return f"""# BlueStaffyUK Design System

Generated by `scripts/build_design_system.py` from `src/styles/tokens.css`, `data/design/picks.json`
and `public/brand/`. Do not edit by hand; change the source and rebuild.

## Palette
Steel `#1F3A52` (brand), slate `#5B7C99`, brass `#C9A227` (CTA, ink `#14202B`), bone `#F4F1EA` (surface), ink `#1B2430`.

## Type
Display **Fraunces** 600/700 for H1–H6; body **Source Sans 3** 400/600 for everything else.

## Logo
Mark: line-drawn Staffordshire Bull Terrier head (variant {picks['mark']}). Lockups: `logo-horizontal`, `logo-stacked`, `logo-icon`, `logo-mono` (assets on this artifact). Strapline: {s['location_label']}.

## Components (picked {picks['pulled_at'][:10]})
{comp}

## The nine design rules
{nine}

## Locked facts
Breeder {s['breeder_name']}, {s['location_label']} (Carlisle, Cumbria, England). Puppies £1,500 (males) / £1,700 (females); deposit £{s['deposit_gbp']} refundable; UK delivery £{s['delivery_min_gbp']}–£{s['delivery_max_gbp']} by distance. Phone, site URL, licence and legal claims are `*_PLACEHOLDER` until confirmed — a design must never invent them.

## Consuming this system
namespace `bsuk`. Files: `tokens.json`, `tokens.css`. No component bundle: components are Astro in the site repo; their reference artboards are on this artifact.
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tokens.json").write_text(json.dumps(tokens_json(), indent=1))
    (OUT / "tokens.css").write_text(TOK.read_text())
    (OUT / "README.md").write_text(readme())
    picks = json.loads((ROOT / "data/design/picks.json").read_text())
    canvas = ROOT / "docs/artifacts/canvas/project"
    n = 0
    for cid, p in picks["picks"].items():
        src = canvas / f"{cid}-{p['variant']}.dc.html"
        if src.exists():
            shutil.copyfile(src, OUT / f"{cid}.dc.html"); n += 1
    print(f"wrote tokens.json, tokens.css, README.md, {n} reference artboards to {OUT}")


if __name__ == "__main__":
    main()
```

Run `python3 -m pytest tests/py/test_design_system_build.py -q && python3 scripts/build_design_system.py`.

- [ ] **Step 4: Publish (controller)** with `url` = the design-system URL, `root` = `docs/artifacts/design-system`, `file_path` = `project/README.md`, `files` = `tokens.json`, `tokens.css`, the thirteen artboards; upload the four lockups as assets. Follow the type's instructions from Step 1 for anything it requires beyond these.

- [ ] **Step 5: Commit**

```bash
echo "docs/artifacts/design-system/" >> .gitignore
git add scripts/build_design_system.py tests/py/test_design_system_build.py data/design/artifacts.json .gitignore docs/superpowers/specs/2026-09-18-design-system-design.md
git commit -m "design-system: artifact files generated from tokens, picks and brand

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 23: Close-out — two full runs, Lighthouse, gate report, Artifacts, session-closer

**Files:**
- Create: `docs/reports/design-system-gate-report.md`, `docs/reports/design-system-run.log`, `docs/artifacts/bsuk-design-system-gate-report.html`, `docs/artifacts/bsuk-design-system-plan.html`
- Modify: `docs/reference/session-log.md`, `docs/reference/system-registry.md` (via `build_system_registry.py`), memory

- [ ] **Step 1: Two full runs into the log**

```bash
set -a; source .env; set +a
for run in 1 2; do echo "=== RUN $run ==="; npm run build && npm run check:all && npm run test:py && npm run test:render:meta; npm run test:render:pages; node scripts/build_scorecard.mjs --run first; npm run baseline; done 2>&1 | tee docs/reports/design-system-run.log | tail -30
```

Expected: both halves identical after normalising times; every zero-tolerance gate at 0; pytest green; meta green with no `DEFERRED`; pages at the project 3 baseline; `python3 scripts/render_baseline.py --check` `0 problems`. Grep the log for token shapes: `python3 -m pytest tests/py/test_secret_shapes.py tests/py/test_no_env_value_committed.py -q` must be green with the log present.

- [ ] **Step 2: Lighthouse**

Run: `ls scripts/lighthouse && cat scripts/lighthouse/README* 2>/dev/null | head -20` to find the Foundation sweep command; run it for the same five page types (warm median of 3). Expected: no category score below the Foundation baseline table in the spec §9.7. Record the table.

- [ ] **Step 3: Write the gate report** — same structure as `docs/reports/system-transfer-gate-report.md`: Context; Build; Tokens (test counts, contrast pairs); Logo; Kit (thirteen components, picks table with the note column); Canvas and picks (URLs, artboard count); Harness (meta, pages table vs project 2, the three promotions, `img-srcset-within-2x` 0); Ported gates table (every script, summary line, exit, baseline/regression tag); Lighthouse; Placeholders (with `REVIEW_PLACEHOLDER` count); Second-run confirmation; Open items for later projects (carry Known Issues 3, 5–16 with status; add any new ones); Definition of done §9 line by line with PASS / PASS-WITH-DEVIATION / FAIL. Numbers come from the log, never typed from memory.

- [ ] **Step 4: Session log, registry, Artifacts**

Add a `## Project 3 — Design system (2026-09-18/…) — COMPLETE` section to `docs/reference/session-log.md` in the style of project 2's; update Known Issue 4 to CLOSED and any others the report changed; append new flags. Run `python3 scripts/build_system_registry.py` (no `--check`) so the new scripts and tests are registered, then `--check`. Build the Artifacts:

```bash
python3 scripts/build_report_artifact.py docs/reports/design-system-gate-report.md docs/artifacts/bsuk-design-system-gate-report.html "BSUK Design System Gate Report" "BlueStaffyUK rebuild · Project 3 of 6" "Design system gate report" "BlueStaffyUK Rebuild — Project 3 of 6: Design system gate report" "status: complete" "$(date +%F)" docs/reports/design-system-gate-report.md
python3 scripts/build_plan_artifact.py docs/superpowers/plans/2026-09-18-design-system.md docs/artifacts/bsuk-design-system-plan.html "BSUK Design System Plan" "BlueStaffyUK rebuild · Project 3 of 6" "Design system implementation plan" "BlueStaffyUK Rebuild — Project 3 of 6: plan" "status: executed" 2026-09-18 docs/superpowers/plans/2026-09-18-design-system.md
```

(Check each builder's argument order with `head -20` first; they mirror `build_spec_artifact.py`.) The controller publishes both and the re-built spec.

- [ ] **Step 5: Commit, merge, memory**

```bash
python3 scripts/marker_check.py | tail -1 && python3 -m pytest tests/py -q | tail -1
git add -A docs data/quality
git commit -m "close-out: design system gate report, session log, artifacts

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git log --oneline e049f55..HEAD | wc -l
git log e049f55..HEAD --format=%B | grep -c "Co-Authored-By: Claude Fable 5.1"
```

Expected: the two counts are equal (trailer on every commit). Then, with the user's approval, `git checkout foundation && git merge --ff-only design-system && git branch -d design-system`. Update the memory file `bsuk-rebuild-project.md` (project 3 done, date, artifact URLs) and write the session-closer: what shipped, the numbers, the open flags list, and **next build: project 4, page rebuilds**.

---

## Self-review

**Spec coverage.** §1 scope → Tasks 1–23; §2 picks → Tasks 2, 4, 20; §3 tokens, contrast, rule rewrite, fact-lint bans → Tasks 2–3; §4 mark variants, four lockups, favicons, header/footer, test → Tasks 4, 20; §5 thirteen components, no-hex test, images/srcset (Known Issue 4), route, `location_label`, `REVIEW_PLACEHOLDER` → Tasks 3, 5–16; §6 canvas builder, assets map, picks board, pull, `picks.json` test, prune → Tasks 17–19; §7 Design System artifact, spec amendment on its real shape → Task 22; §8 order → task order; §9 done → Task 23; §10 risks: CSS fallback is noted in Task 17 step 3 (if the type refuses `<helmet><style>` selectors, switch the builder to computed styles per element — implement as `--inline-computed` in the measurer, capturing `getComputedStyle` for each element into `style=""` attributes); asset de-dup → `canvas-assets.json`; picks over sessions → skip-until-present; form contract → Task 13.

**Placeholder scan.** No "TBD"/"TODO". Step 1 of Task 22 deliberately defers the `tokens.json` shape to the type's own instructions and requires a spec amendment before code — that is a decision, not a gap. Task 20 step 3 depends on font files being downloaded; the command names the source.

**Consistency.** Component ids and file names are identical in `components.json` (Task 1), the route `byId` (Tasks 5–15), the builder (Task 17, `<id>-<v>.dc.html`), the picks board and pull (`picks/<id>`, Task 18), the prune (Task 19) and the design-system builder (Task 22). `Variant` type and `VARIANTS` from `_variant.ts` are used by every component and deleted in Task 19 together with every `variant` prop, which `test_after_prune_no_variant_prop_remains` enforces. The harness hook classes are `.counter-wrap` + `[data-counters]` (Task 9), `.sec-img` owned by an H3 and `.stmt-label` (Task 10), matching the selectors in `tests/render/checks/`; Task 10 step 1 verifies them against the real check code before writing fixtures.
