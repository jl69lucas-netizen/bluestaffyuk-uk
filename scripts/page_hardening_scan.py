#!/usr/bin/env python3
"""
BSUK Page-Hardening Scanner — finds the UI/UX/perf/a11y defect classes that have
actually bitten this site, automatically, instead of waiting for the breeder to
spot them on a phone.

Every check below was banked from a real, confirmed defect (source noted inline).
Owned by .claude/skills/bsuk-page-hardening/SKILL.md.

Usage:
  python3 scripts/page_hardening_scan.py                 # whole site
  python3 scripts/page_hardening_scan.py <slug> [<slug>] # specific pages
  python3 scripts/page_hardening_scan.py --fail-on-error # non-zero exit on ERROR
  python3 scripts/page_hardening_scan.py --json          # also write the JSON report

Exit code: 0 unless --fail-on-error is passed AND at least one ERROR was found.
Without that flag this is a report, not a gate — findings are advisory here because
the migrated pages have not been hardened yet.

Severity:
  ERROR  = shipped-broken; fix before deploy
  WARN   = very likely wrong; eyeball it

Scoped-run source selection (2026-09-10): a scoped run (one or more slugs)
examines the page's own file plus the components it actually imports, plus
BaseLayout.astro/global.css — see src_files()/imports_of(). Before this date
a scoped run examined only the page file itself and could miss a defect
shipped in an imported component.

2026-09-26: a page rendered by a DYNAMIC route (a city at uk-locations/<city>, a
puppy, a blog post) resolves to its template — `src/pages/uk-locations/[slug].astro`
— and that template's imports, data/locations.json among them (page_source()).
The site sweep recurses into src/components/, so the kit is read too.
"""
import re, sys, glob, os, json, pathlib, argparse
from _slugs import select_pages, resolve_page

# `src/components/**` recurses: the kit (`src/components/kit/`) is where every rebuilt and
# project 5 page's sections live, and a non-recursive glob never read one of its files.
SRC_GLOBS = ["src/pages/**/*.astro", "src/components/**/*.astro",
             "src/layouts/*.astro", "src/styles/*.css"]
DIST = "dist"

# The global MobileTabBar is `fixed bottom-0 ... z-50` (src/components/MobileTabBar.astro).
# Anything else pinned to the bottom must clear it or it renders invisible.
TABBAR_Z = 50
TABBAR_H = 56

findings = []
def add(sev, check, f, line, msg, fix):
    findings.append({"sev": sev, "check": check, "file": f, "line": line,
                     "msg": msg, "fix": fix})

def lines_of(path):
    try:
        return open(path, encoding="utf-8").read().split("\n")
    except Exception:
        return []

# Matches single-line `import ... from '...'` only — a multi-line destructured
# import (`import {\n  Foo,\n} from '../x'`) is not followed. None exist in the
# repo as of 2026-09-10.
IMPORT_RE = re.compile(
    r"""^\s*import\b[^'"]*?['"](\.\.?/[^'"]+)['"]""", re.M)

_RESOLVE_EXTS = ("", ".astro", ".ts", ".js", ".json", ".mjs")


def _resolve_import(base_dir, rel_path):
    """Resolve a relative import path to a real file on disk, trying the
    common Astro/TS extensions. Returns None if nothing exists (bare
    package imports never reach here since IMPORT_RE only matches './' and
    '../' specifiers)."""
    candidate = os.path.normpath(os.path.join(base_dir, rel_path))
    for ext in _RESOLVE_EXTS:
        p = candidate + ext
        if os.path.isfile(p):
            return p.replace(os.sep, "/")
    return None


def imports_of(astro_path, root="."):
    """Pure helper: parse `import X from '<relative path>'` lines out of an
    Astro/JS file's frontmatter and return the set of relative-imported
    files that actually exist on disk, resolved relative to astro_path's own
    directory. Bare package imports (no leading './' or '../') and imports
    that don't resolve to a real file are silently dropped.

    `astro_path` is given relative to `root` (default "." — the real repo
    root when run as a script from there); the returned paths are also
    relative to `root`, so tests can point `root` at a fixture tree and get
    back the same style of path (e.g. "src/components/FormA.astro") the
    real scan produces. See tests/test_audit_slug_resolution.py.
    """
    text = "\n".join(lines_of(os.path.join(root, astro_path)))
    base_dir = os.path.join(root, os.path.dirname(astro_path))
    found = set()
    for m in IMPORT_RE.finditer(text):
        resolved = _resolve_import(base_dir, m.group(1))
        if resolved:
            found.add(os.path.relpath(resolved, root).replace(os.sep, "/"))
    return found


def page_source(slug, root="."):
    """The source file a built page is rendered from, or None.

    A static page is `src/pages/<route>/index.astro` (`src/pages/index.astro` for the root).
    Every other page is a DYNAMIC route: a city is `uk-locations/<city>` rendered by
    `src/pages/uk-locations/[slug].astro`, a puppy by `available-puppies/[slug].astro`, a
    blog post by `src/pages/[...post].astro`. Before 2026-09-26 only the static form was
    tried, so a city page's scoped run read BaseLayout and global.css and nothing of the page.
    A bare city key is resolved to its route first (scripts/_slugs.py, Known Issue 39); the
    dynamic file is looked up in the route's parent directory with os.listdir, because glob
    reads the `[` in `[slug].astro` as a character class."""
    try:
        route = resolve_page(slug, root)[1]
    except ValueError:
        return None
    if not route:
        return "src/pages/index.astro"
    static = f"src/pages/{route}/index.astro"
    if os.path.isfile(os.path.join(root, static)):
        return static
    parent = os.path.dirname(route)
    folder = os.path.join(root, "src", "pages", parent)
    if not os.path.isdir(folder):
        return None
    dynamic = sorted(f for f in os.listdir(folder) if f.startswith("[") and f.endswith("].astro"))
    if not dynamic:
        return None
    return "/".join(p for p in ("src/pages", parent, dynamic[0]) if p)


def src_files(slugs, root="."):
    """A scoped run examines the page's OWN source file plus the components
    it actually imports (one level, plus one more level for
    src/components/*.astro components — they commonly import a
    sibling), plus src/layouts/BaseLayout.astro and src/styles/global.css
    (every page is wrapped in BaseLayout). Earlier versions either
    substring-matched "index" against every page (pre-2026-09-10) or, after
    that fix, unconditionally globbed in EVERY component/layout/style file
    for a scoped run — which changed a normal slug's verdict and attributed
    a shared component's findings to pages that never import it (e.g.
    ContactForm.astro's defect blamed on `/`, which does not import it).
    With no slugs (site sweep) this keeps
    the old full-glob behaviour, since every source file is in scope anyway.

    `root` (default "." — the real repo root) lets tests point this at a
    fixture tree; returned paths stay relative to `root`.
    See tests/test_audit_slug_resolution.py.
    """
    always = {"src/layouts/BaseLayout.astro", "src/styles/global.css"}
    if not slugs:
        page_files = sorted(set(
            os.path.relpath(p, root).replace(os.sep, "/")
            for p in glob.glob(os.path.join(root, "src/pages/**/*.astro"), recursive=True)
        ))
        shared_files = []
        for g in ("src/components/**/*.astro", "src/layouts/*.astro", "src/styles/*.css"):
            shared_files += [
                os.path.relpath(p, root).replace(os.sep, "/")
                for p in glob.glob(os.path.join(root, g), recursive=True)
            ]
        return sorted(set(page_files) | set(shared_files) | always)

    result = set(always)
    for s in slugs:
        page_file = page_source(s, root)
        if page_file is None:
            continue
        result.add(page_file)
        first_level = imports_of(page_file, root=root)
        result |= first_level
        for imp in first_level:
            if imp.startswith("src/components/") and imp.endswith(".astro"):
                result |= imports_of(imp, root=root)
    return sorted(result)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Malformed clamp()/calc() — CSS math needs whitespace around + and -.
#    `clamp(1.7rem,1.2rem+2.2vw,2.6rem)` is INVALID: the whole declaration is
#    dropped and the element silently falls back to the global heading size.
#    This is why a for-sale page shipped a 48px h1 and a 524px hero while the
#    source said 2.26rem / ~400px (found 2026-07-23). Utterly invisible in review.
# ─────────────────────────────────────────────────────────────────────────────
def check_css_math(files):
    pat = re.compile(r"(?:clamp|calc|min|max)\([^)]*\)")
    bad = re.compile(r"[0-9a-z%)]\s*[+\-]\s*(?=[.\d])(?<![ ])|(?<=[0-9a-z%)])[+\-][.\d]")
    for f in files:
        for i, ln in enumerate(lines_of(f), 1):
            for m in pat.finditer(ln):
                expr = m.group(0)
                # A custom property's NAME is not arithmetic: `var(--space-4)` read as
                # `e-4` failed every kit component on 2026-09-26, the day the scan first
                # read src/components/kit/. Names are blanked before the test.
                bare = re.sub(r"--[\w-]+", "--v", expr)
                # a +/- with a non-space on either side, ignoring signs after ( or ,
                if re.search(r"(?<=[0-9a-z%\)])\+(?=[^\s])|(?<=[0-9a-z%\)])\s\-(?=[^\s])|(?<=[0-9a-z%\)])\-(?=[.\d])", bare):
                    add("ERROR", "css-math-spacing", f, i,
                        f"invalid CSS math (needs spaces around +/-): {expr}",
                        "rewrite as clamp(1.5rem, 1.02rem + 1.55vw, 1.98rem) — "
                        "without the spaces the declaration is dropped entirely")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Bottom-pinned UI buried under the global MobileTabBar (z-50, 56px tall).
#    The hand-raised mobile jump-rail was `sticky; bottom:0; z-index:40` and
#    rendered *underneath* the tab bar — the breeder reported it as "broken".
# ─────────────────────────────────────────────────────────────────────────────
def check_bottom_bar_z(files):
    for f in files:
        ls = lines_of(f)
        for i, ln in enumerate(ls, 1):
            if not re.search(r"position:\s*(sticky|fixed)", ln):
                continue
            if not re.search(r"bottom:\s*0", ln):
                continue
            zm = re.search(r"z-index:\s*(\d+)", ln)
            z = int(zm.group(1)) if zm else 0
            if z <= TABBAR_Z:
                add("ERROR", "bottom-bar-under-tabbar", f, i,
                    f"bottom-pinned element at z-index:{z} sits under the global "
                    f"MobileTabBar (fixed bottom-0, z-{TABBAR_Z})",
                    f"bottom:calc({TABBAR_H}px + env(safe-area-inset-bottom)); "
                    f"z-index:{TABBAR_Z-5}; and pad the page bottom so content isn't covered")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Infographics cover-cropped on mobile.
#    Forcing a 16:9 infographic into aspect-ratio:5/4 (or 4/5) with
#    object-fit:cover shaves ~30% off EACH side and cuts the baked-in text.
#    Only real OG photos get the taller mobile frame (IMAGE-DESIGNS §7).
# ─────────────────────────────────────────────────────────────────────────────
def check_infographic_crop(files):
    for f in files:
        for i, ln in enumerate(lines_of(f), 1):
            if ".inf-img" not in ln:
                continue
            has_tall = re.search(r"aspect-ratio:\s*(5\s*/\s*4|4\s*/\s*5)", ln)
            covers = "object-fit:contain" not in ln
            if has_tall and covers:
                add("ERROR", "infographic-cropped-mobile", f, i,
                    "infographic forced to a 5:4/4:5 box without object-fit:contain "
                    "— baked-in text will be cut off at both edges on mobile",
                    "keep infographics at their native aspect-ratio with "
                    "object-fit:contain; reserve the 5:4 mobile frame for .og-photo")


# ─────────────────────────────────────────────────────────────────────────────
# 4. 100vw full-bleed children inflating a grid track.
#    A `1fr` track sizes to its min-content, and a width:100vw child makes that
#    the viewport width — so the text column grew past the container padding and
#    body copy ran off-screen. Needs minmax(0,1fr) + min-width:0.
# ─────────────────────────────────────────────────────────────────────────────
def check_fullbleed_grid(files):
    """A width:100vw child inflates the `1fr` grid track that CONTAINS it — but
    which grid that is cannot be known statically (every attempt produced ~28
    false positives on one page). This defect is detected at RUNTIME instead:
    see the horizontal-overflow probe in .claude/skills/bsuk-page-hardening/SKILL.md §Runtime.
    Kept as a no-op so the check list stays documented in one place."""
    return


# ─────────────────────────────────────────────────────────────────────────────
# 5. Absolutely-positioned hero art never unwound for mobile.
#    The hand-raised Hero-A polaroids were position:absolute with % widths; on
#    desktop they covered each other's heads, on mobile they collapsed to slivers.
# ─────────────────────────────────────────────────────────────────────────────
def check_absolute_hero(files):
    for f in files:
        txt = "\n".join(lines_of(f))
        for i, ln in enumerate(lines_of(f), 1):
            if not re.search(r"position:\s*absolute", ln):
                continue
            if not re.search(r"hero|polaroid|pofig|scatter|collage", ln, re.I):
                continue
            sel = ln.split("{")[0].strip()
            # captions/badges/chips/tags pinned inside a card are correct by design —
            # only the CARD ITSELF being absolute is the overlap/collapse bug.
            # NOTE single-colon `:before` too — `.chero-ribbon li:before{content:"✓"}`
            # is a bullet glyph, not hero art (it was firing before this).
            if re.search(r"figcaption|caption|badge|chip|label|tag|:{1,2}(before|after)",
                         sel, re.I):
                continue
            # A lone element pinned to `inset:0` (or all four offsets at 0) fills its
            # positioned parent — a cover-fill, not a scatter stack. It cannot overlap
            # a sibling at any width, so the overlap/collapse bug does not apply.
            # This is the comparison-cluster `.cvt-hero .hero-single img` pattern.
            decl = ln.split("{", 1)[1] if "{" in ln else ""
            fills = re.search(r"inset:\s*0", decl) or all(
                re.search(rf"{side}:\s*0", decl) for side in ("top", "right", "bottom", "left"))
            if fills:
                continue
            base = sel.split()[-1].lstrip(".")
            # §1d says the bug is "the CARD ITSELF being absolute" — hero ART that
            # overlaps its siblings on desktop and collapses to slivers on mobile.
            # A text element pinned to a corner of its own card is correct by design.
            # The name-based allowlist above misses any badge not literally called
            # badge/chip/tag (e.g. `.hero-tile-p`, a price pill), so test STRUCTURE:
            #   (a) the rule styles type and sets no box  -> it is text, not art, and
            #   (b) a shorter class it extends declares position:relative -> that
            #       ancestor is the positioning context, so it cannot escape the card.
            styles_type = re.search(r"font-(size|family|weight)|letter-spacing", decl)
            sets_box = re.search(r"(?<!min-)(?<!max-)\b(width|height)\s*:", decl)
            parent_relative = any(
                re.search(r"\.%s\s*(,[^{]*)?\{[^{}]*position:\s*relative" % re.escape(base[:n]),
                          txt)
                for n in range(4, len(base))          # any shorter prefix class
                if base[:n].rstrip("-")
            )
            if styles_type and not sets_box and parent_relative:
                continue
            # is it reset inside any max-width media query?
            reset = re.search(
                r"@media[^{]*max-width[^{]*\{(?:[^{}]|\{[^{}]*\})*?"
                + re.escape(base) + r"[^{}]*\{[^{}]*position:\s*(static|relative)",
                txt, re.S)
            if not reset:
                add("WARN", "absolute-hero-not-unwound", f, i,
                    f"absolutely-positioned hero art ({sel}) is never reset to "
                    "static/relative in a mobile media query",
                    "lay hero art out with a grid (rotations for the scatter look) "
                    "so overlap is structurally impossible at every width")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Small clay text below AA.  Brand --clay #e8604c is AA only as LARGE text.
#    Small text on light must be #b04228; solid clay fills use #c8472f.
# ─────────────────────────────────────────────────────────────────────────────
def check_clay_small_text(files):
    for f in files:
        for i, ln in enumerate(lines_of(f), 1):
            if not re.search(r"color:\s*(var\(--clay\)|#e8604c)", ln, re.I):
                continue
            fs = re.search(r"font-size:\s*([\d.]+)rem", ln)
            if fs and float(fs.group(1)) < 1.4:
                add("WARN", "clay-small-text-contrast", f, i,
                    f"--clay #e8604c as {fs.group(1)}rem text is 3.38:1 — below AA (4.5)",
                    "use --clay-ink #c8472f (4.78:1) or #b04228 for small clay text on light")


# ─────────────────────────────────────────────────────────────────────────────
# 7. opacity dimming text on a coloured fill — silently drops contrast below AA.
#    (`.k2-from{opacity:.9}` white on #c8472f measured 4.10 vs the 4.5 floor.)
# ─────────────────────────────────────────────────────────────────────────────
def check_opacity_text(files):
    for f in files:
        for i, ln in enumerate(lines_of(f), 1):
            m = re.search(r"opacity:\s*(0?\.\d+)", ln)
            if not m:
                continue
            if re.search(r"color:|font-size:|font-weight:", ln):
                add("WARN", "opacity-dims-text-contrast", f, i,
                    f"opacity:{m.group(1)} applied to a text rule — dims the "
                    "foreground and can drop it under AA",
                    "drop the opacity and pick an explicit colour that measures >= 4.5:1")


# ─────────────────────────────────────────────────────────────────────────────
# 8. Oversized image delivery — intrinsic width >> rendered width, no srcset.
#    (Lighthouse flagged 163 KiB on 620x720 hero polaroids shown at ~200px.)
# ─────────────────────────────────────────────────────────────────────────────
def check_img_srcset(pages):
    for p in pages:
        try:
            h = open(p, encoding="utf-8").read()
        except Exception:
            continue
        slug = p.replace(DIST + "/", "").replace("/index.html", "/")
        for m in re.finditer(r"<img\b[^>]*>", h):
            tag = m.group(0)
            if "srcset" in tag:
                continue
            w = re.search(r'width="(\d+)"', tag)
            if w and int(w.group(1)) >= 600:
                src = re.search(r'src="([^"]+)"', tag)
                add("WARN", "img-no-srcset", slug, 0,
                    f"{(src.group(1) if src else '?').split('/')[-1]} is "
                    f"{w.group(1)}px intrinsic with no srcset",
                    "ship a -320/-440/-760 sibling and add srcset+sizes")


# ─────────────────────────────────────────────────────────────────────────────
# 8b. Headings must be AP-style Title Case, matching the homepage and the
#     for-sale pages. A for-sale page shipped 62 sentence-case
#     headings (2026-07-23). See .claude/skills/bsuk-page-hardening/SKILL.md §1e-ter.
# ─────────────────────────────────────────────────────────────────────────────
MINOR_WORDS = {"a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet",
               "at", "by", "in", "of", "on", "to", "as", "vs", "per", "via"}

# Genus names that legitimately precede a lowercase species epithet in a heading.
SPECIES_GENERA = {"Canis"}

def check_title_case(pages):
    import html as _html
    for p in pages:
        try:
            raw = open(p, encoding="utf-8").read()
        except Exception:
            continue
        slug = p.replace(DIST + "/", "").replace("/index.html", "/")
        m = re.search(r"<main[^>]*>(.*)</main>", raw, re.S)
        if not m:
            continue
        seg = m.group(1)
        for lvl in range(1, 7):
            for inner in re.findall(rf"<h{lvl}[^>]*>(.*?)</h{lvl}>", seg, re.S):
                t = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", inner))).strip()
                if not t:
                    continue
                words = t.split(" ")
                force = True
                for i, w in enumerate(words):
                    core = re.sub(r"[^\w'-]", "", w)
                    # Binomial species epithets are correctly lowercase —
                    # "Canis familiaris". Capitalising them would be the
                    # actual defect, so they sit in the same exemption class as acronyms.
                    prev = re.sub(r"[^\w'-]", "", words[i - 1]) if i else ""
                    if prev in SPECIES_GENERA and core.islower():
                        force = bool(re.search(r"[:?!]$", w))
                        continue
                    # skip acronyms, brands, domains, numbers, prices
                    if (not core or core[0].isdigit() or "." in w
                            or core.isupper() or re.search(r"[a-z][A-Z]", core)):
                        force = bool(re.search(r"[:?!]$", w))
                        continue
                    must_cap = (force or i == 0 or i == len(words) - 1
                                or core.lower() not in MINOR_WORDS)
                    if must_cap and core[0].islower():
                        add("ERROR", "header-not-title-case", slug, 0,
                            f'H{lvl} is not Title Case ("{w}" in "{t[:58]}")',
                            "AP-style Title Case: capitalise 4+ letter words and all "
                            "nouns/verbs/adjectives; lowercase only mid-title "
                            "a/an/the/and/or/for/at/by/in/of/on/to/as/vs")
                        break
                    force = bool(re.search(r"[:?!]$", w))


# ─────────────────────────────────────────────────────────────────────────────
# 9. Body links distinguishable by colour alone (WCAG 1.4.1).
# ─────────────────────────────────────────────────────────────────────────────
def check_link_underline(files):
    for f in files:
        txt = "\n".join(lines_of(f))
        if ".content p a" in txt or "content li a" in txt:
            if re.search(r"\.content (?:p|li) a[^{]*\{[^}]*text-decoration:\s*underline", txt):
                continue
        if re.search(r"\.content\b", txt) and "text-decoration:underline" not in txt.replace(" ", ""):
            add("WARN", "links-colour-only", f, 0,
                "no underline rule found for in-body content links",
                "add .content p a{text-decoration:underline;text-underline-offset:2px}")


# ─────────────────────────────────────────────────────────────────────────────
# 10. Known render traps already banked in MEMORY.
# ─────────────────────────────────────────────────────────────────────────────
def check_known_traps(files, pages):
    for f in files:
        for i, ln in enumerate(lines_of(f), 1):
            if re.search(r"content:\s*['\"]\s*<svg", ln):
                add("ERROR", "svg-in-css-content", f, i,
                    "an <svg> inside CSS content: renders as raw text and collapses spacing",
                    "put the inline <svg> in the markup instead")
            if "user-select:none" in ln.replace(" ", "") and ".select-none" not in ln:
                add("ERROR", "user-select-none", f, i,
                    "user-select:none is banned site-wide (anti-copy rule)",
                    "remove it")
            # scroll-behavior is now handled by check_smooth_scroll(), which allows
            # the reduced-motion-guarded global `html` rule and still warns on rails.
    for p in pages:
        try:
            h = open(p, encoding="utf-8").read()
        except Exception:
            continue
        slug = p.replace(DIST + "/", "").replace("/index.html", "/")
        if "&lt;svg" in h:
            add("ERROR", "escaped-svg", slug, 0,
                "an inline SVG rendered escaped (&lt;svg) — a data-array icon is "
                "missing set:html", "add set:html to the {x.icon} render")


# ═════════════════════════════════════════════════════════════════════════════
# The 2026-07-26 gate gaps. Every check below was banked from a defect that
# shipped on the for-sale cluster and was found by the breeder on a phone rather
# than by this scanner. Each takes [(label, text)] so it is unit-testable.
# See tests/test_page_hardening_new_checks.py.
# ═════════════════════════════════════════════════════════════════════════════

# ── hero-preload-srcset-drift ────────────────────────────────────────────────
# BaseLayout.astro:22-23 warns that heroPreloadSrcset/heroPreloadSizes must mirror
# the LCP <img>. When only heroPreloadSizes is passed, the preload scanner resolves
# a different candidate than the renderer, and the hero downloads twice.
def check_hero_preload_drift(sources):
    for label, text in sources:
        if "heroPreload" not in text:
            continue
        img_has_srcset = re.search(r"<img\b[^>]*fetchpriority=\"high\"[^>]*srcset=", text, re.S) \
            or re.search(r"<img\b[^>]*srcset=[^>]*fetchpriority=\"high\"", text, re.S)
        if img_has_srcset and "heroPreloadSrcset" not in text:
            line = text[: text.index("heroPreload")].count("\n") + 1
            add("ERROR", "hero-preload-srcset-drift", label, line,
                "heroPreload is set and the LCP <img> uses srcset, but "
                "heroPreloadSrcset is missing — the preload scanner will fetch a "
                "different candidate than the renderer uses (hero downloads twice)",
                "mirror the img's srcset/sizes into heroPreloadSrcset/heroPreloadSizes")


# ── tap-target-spacing ───────────────────────────────────────────────────────
# A for-sale page shipped 28 failing target pairs on
# BOTH mobile and desktop. The pills are 36px tall so SIZE passed; `gap:7px` put
# each pill inside its neighbour's 24px exclusion zone. axe target-size minimum.
MIN_TARGET_GAP_PX = 10.0

def _px(val):
    """Resolve a CSS length to px. rem = 16px. Returns None if not resolvable."""
    m = re.match(r"^\s*(-?[\d.]+)(px|rem|em)?\s*$", val or "")
    if not m:
        return None
    n = float(m.group(1))
    return n * 16 if m.group(2) in ("rem", "em") else n

def check_tap_target_spacing(sources):
    """axe target-size PASSES any target >=24x24 CSS px, whatever its neighbours do.
    Spacing only rescues UNDERSIZED targets. The first cut of this check ignored that
    and flagged every jump rail on all six for-sale pages purely for a 7px gap — but
    those pills measure 202x37 and always passed. Meanwhile the real failures (17px-tall
    index links) went unreported, because their rule sets no gap at all.

    So: flag a link rule that cannot reach 24px tall. Height comes from height or
    min-height, or from font-size x line-height + vertical padding. If none of those
    are declared the rule is not sized here and is skipped — better silent than
    crying wolf.

    2026-07-26: that "better silent" promise was not being kept. This check reported
    7 ERRORs across four for-sale pages and every one was wrong, for two
    reasons now guarded against:

      1. It matched `li`/`pill`/`chip` in a selector, so decorative content lists were
         treated as pointer targets. `.ds-list li::before` is a counter badge and
         `.handraised .hero-chips` is a <ul> of static trust labels — neither contains
         an <a> or a <button>, and WCAG 2.5.8 governs TARGETS, not text. A `::before`
         can never be a target at all. Now: the selector must name a link or button,
         and pseudo-elements are skipped outright.
      2. It read only min-height, so a rule declaring `height:28px` fell through to the
         font-size guess and "measured" 19px. Now: height counts the same as min-height.
    """
    for label, text in sources:
        for m in rule_blocks(text):
            sel, body = m.group(1).strip().split("\n")[-1].strip(), m.group(2)
            if "<" in sel or not re.match(r"^[.#a-z]", sel):
                continue
            # A pseudo-element is decoration, never a pointer target.
            if "::before" in sel or "::after" in sel:
                continue
            # Must actually BE a control. "pill"/"chip"/"li" alone are just names.
            if not re.search(r"\ba\b|\bbutton\b", sel, re.I):
                continue
            flat = body.replace(" ", "")
            if "display:block" not in flat and "display:inline-flex" not in flat \
               and "display:grid" not in flat and "display:flex" not in flat:
                continue
            sized = None
            for prop in ("min-height", "height"):
                hit = re.search(prop + r":\s*([^;]+);", body)
                if hit:
                    val = _px(hit.group(1))
                    if val is not None:
                        sized = val if sized is None else max(sized, val)
            if sized is not None and sized >= 24:
                continue
            fs = re.search(r"font-size:\s*([^;]+);", body)
            lh = re.search(r"line-height:\s*([\d.]+)\s*;", body)
            pad = re.search(r"padding:\s*([^;]+);", body)
            if not fs:
                continue
            size = _px(fs.group(1))
            if size is None:
                continue
            content = size * (float(lh.group(1)) if lh else 1.4)
            padv = 0.0
            if pad:
                first = _px(pad.group(1).split()[0])
                padv = (first or 0) * 2
            total = content + padv
            if total >= 24:
                continue
            line = text[: m.start()].count("\n") + 1
            add("ERROR", "tap-target-spacing", label, line,
                f"`{sel}` renders about {total:.0f}px tall — under the 24px axe "
                f"target-size minimum. Spacing cannot rescue an undersized target.",
                "add vertical padding (or min-height:24px) so the whole row is tappable")


# ── form-control-overflow / form-control-ios-zoom ────────────────────────────
# The health-guarantee contact form was cut off on the right at mobile/tablet.
# A CSS grid child defaults to min-width:auto and refuses to shrink below its
# content — the single most common cause of exactly this symptom. Sub-16px inputs
# additionally trigger iOS Safari auto-zoom, which reads as "too zoomed, cut off".
# ── rule_blocks: the one CSS block scanner ───────────────────────────────────
# A flat `([^{}]*)\{([^}]*)\}` regex cannot see inside an at-rule — `[^}]*` stops at
# the first `}`, so `@media(...){ input{...} }` yielded the @media header as a
# "selector" with a truncated body and the real rule was never scanned as a block.
# It also backtracks catastrophically over the long brace-free regions in .astro
# markup. This tokenizer walks the braces once, linearly, at any nesting depth.
_COMMENT_OR_STRING = re.compile(r"/\*.*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", re.S)
_NESTING_AT_RULE = re.compile(r"@(?:media|supports|layer|container|document|scope)\b", re.I)


def _mask(css):
    """Blank out comments and quoted strings, preserving length and newlines, so a
    `}` inside `/* ... */` or `content:"}"` cannot desynchronise the depth counter.
    Offsets into the mask are offsets into the original text."""
    def blank(m):
        return "".join("\n" if c == "\n" else " " for c in m.group(0))
    return _COMMENT_OR_STRING.sub(blank, css)


class _Block:
    """One declaration block. `group(1)` is its selector, `group(2)` its declarations,
    `start()` the offset of the selector — the re.Match surface the checks already use."""
    __slots__ = ("_sel", "_body", "_start")

    def __init__(self, sel, body, start):
        self._sel, self._body, self._start = sel, body, start

    def group(self, n):
        return self._sel if n == 1 else self._body

    def start(self):
        return self._start


def rule_blocks(css):
    """Yield every declaration block in `css`, at any nesting depth.

    At-rule headers (`@media`, `@font-face`, `@keyframes`, …) are never yielded as
    selectors; the nesting at-rules are descended into so the rules they wrap are
    judged like any other. A selector is trimmed at the last `;` before it, so a
    nested rule's selector does not carry its parent's declarations.
    """
    masked = _mask(css)
    stack = []
    last = 0
    for m in re.finditer(r"[{}]", masked):
        i = m.start()
        if masked[i] == "{":
            sel_masked = masked[last:i]
            is_at = sel_masked.lstrip().startswith("@")
            sel = css[last:i]
            if ";" in sel_masked:                     # drop a parent's declarations
                cut = sel_masked.rfind(";") + 1
                sel, sel_start = sel[cut:], last + cut
            else:
                sel_start = last
            # Comments are not part of a selector: a `/* FAQ tick */` above a rule
            # used to be read as its name (icon-baseline false positives, 2026-07-26).
            sel = re.sub(r"/\*.*?\*/", "", sel, flags=re.S)
            stack.append((sel, sel_start, is_at, i))
            last = i + 1
        else:
            if stack:
                sel, sel_start, is_at, brace = stack.pop()
                if not is_at:
                    body_masked = masked[brace + 1:i]
                    nested = body_masked.find("{")
                    end = brace + 1 + (nested if nested >= 0 else len(body_masked))
                    yield _Block(sel, css[brace + 1:end], sel_start)
            last = i + 1


def write_json_report(path, slugs):
    """Write the machine-readable result: one entry per scanned slug/file, its status
    (ERROR > WARN > OK) and every finding as {check, severity, message}."""
    by = {s: [] for s in slugs}
    for f in findings:
        by.setdefault(f["file"], []).append(
            {"check": f["check"], "severity": f["sev"], "message": f["msg"]})
    pages = []
    for slug in sorted(by):
        checks = by[slug]
        sevs = {c["severity"] for c in checks}
        status = "ERROR" if "ERROR" in sevs else ("WARN" if "WARN" in sevs else "OK")
        pages.append({"slug": slug, "status": status, "checks": checks})
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"pages": pages}, indent=2) + "\n", encoding="utf-8")
    return out


def check_form_overflow(sources):
    for label, text in sources:
        flat = text.replace(" ", "")
        # Scan rule blocks once and test the captured selector, rather than asking the
        # engine for `[^{}]*form[^{}]*` — two unbounded stars around a literal backtrack
        # catastrophically over a long brace-free region, and BSUK's .astro files are
        # mostly markup. Same matches, linear time. (Re-base fix, Task 6.)
        form_grid = next(
            (m for m in rule_blocks(text)
             if re.search(r"form", m.group(1), re.I)
             and re.search(r"display:\s*grid", m.group(2), re.I)),
            None)
        if form_grid and "min-width:0" not in flat:
            line = text[: form_grid.start()].count("\n") + 1
            add("ERROR", "form-control-overflow", label, line,
                f"`{form_grid.group(1).strip()}` is a grid but no child sets "
                "min-width:0 — grid children default to min-width:auto and will "
                "not shrink below their content, overflowing the viewport",
                "add `.row>*{min-width:0}` and max-width:100%;box-sizing:border-box "
                "on every input/select")
        for m in (m for m in rule_blocks(text)
                  if re.search(r"input|select|textarea", m.group(1), re.I)):
            sel, body = m.group(1).strip(), m.group(2)
            line = text[: m.start()].count("\n") + 1
            fs = re.search(r"font-size:\s*([^;]+);", body)
            if fs:
                size = _px(fs.group(1))
                if size is not None and size < 16:
                    add("ERROR", "form-control-ios-zoom", label, line,
                        f"`{sel}` sets font-size {size:g}px — anything under 16px "
                        "makes iOS Safari auto-zoom the page on focus, which reads "
                        "to users as the form being cut off",
                        "set font-size:16px on every input/select/textarea")
                continue
            # `font:inherit` is the sneaky case — the size is real but declared on an
            # ancestor. Resolve it against the nearest label/form rule in the same file.
            if not re.search(r"font:\s*inherit", body):
                continue
            scope = sel.split(",")[0].rsplit(" ", 1)[0].strip()
            inherited = None
            for anc in rule_blocks(text):
                anc_sel = anc.group(1).strip()
                if scope and scope not in anc_sel:
                    continue
                if not re.search(r"\b(label|form|fieldset)\b", anc_sel, re.I):
                    continue
                afs = re.search(r"font-size:\s*([^;]+);", anc.group(2))
                if afs:
                    inherited = _px(afs.group(1))
            if inherited is not None and inherited < 16:
                add("ERROR", "form-control-ios-zoom", label, line,
                    f"`{sel}` uses font:inherit, which resolves to {inherited:g}px "
                    f"from its ancestor label — under 16px iOS Safari auto-zooms on "
                    "focus and the form's right edge leaves the viewport",
                    "set an explicit font-size:16px on every input/select/textarea "
                    "(the label can stay smaller)")


# ── font-family-loaded-unused ────────────────────────────────────────────────
# Lora and Sora were requested in BaseLayout on EVERY page of the site but never
# rendered: direction-d.css overrides .font-lora/.font-sora with !important. Two of
# the five woff2 files in every "Network dependency tree" PageSpeed finding.
def check_font_families(head_html, theme_css):
    requested = set()
    for m in re.finditer(r"family=([A-Za-z0-9+]+)[:&]", head_html):
        requested.add(m.group(1).replace("+", " "))
    for m in re.finditer(r"@font-face\s*\{[^}]*font-family:\s*['\"]([^'\"]+)", head_html):
        requested.add(m.group(1))
    # A family can reach the page through a CUSTOM PROPERTY as easily as through a
    # font-family declaration: `--font-lora:'Lora',Georgia,serif` consumed by
    # `font-family:var(--font-lora)` in page CSS. The first cut of this check only
    # looked at `font-family:` in two stylesheets and wrongly declared Lora and Sora
    # dead — a runtime probe found them rendering on 51 elements. Err toward a false
    # NEGATIVE here: wrongly deleting a font is a visible sitewide regression, while
    # wrongly keeping one costs a few KB.
    rendered = set()
    for m in re.finditer(r"(?:font-family|--font[\w-]*|font)\s*:\s*([^;}]+)", theme_css):
        rendered.update(re.findall(r"['\"]([^'\"]+)['\"]", m.group(1)))
    for fam in sorted(requested):
        if any(fam.lower() == r.lower() or fam.lower() in r.lower() for r in rendered):
            continue
        add("ERROR", "font-family-loaded-unused", "src/layouts/BaseLayout.astro", 0,
            f"'{fam}' is downloaded on every page but nothing references it — not a "
            f"font-family rule and not a --font-* custom property. Confirm with a "
            f"runtime probe before deleting.",
            f"remove {fam} from the font request, or repoint the token that should "
            f"have used it")


# ── analytics-double-load ────────────────────────────────────────────────────
# A GA4 container served first-party via Cloudflare's Google Tag Gateway while the
# direct googletagmanager.com tag ALSO fires loads the same container twice — a
# second copy of the analytics payload on every page. NOT Rocket Loader.
# BSUK ships no analytics until project 6; the check stays wired so the day a tag
# lands it is already judged.
GA4_MEASUREMENT_ID = os.environ.get("GA4_MEASUREMENT_ID", "")
GTAG_GATEWAY = re.compile(r"""<script[^>]*\bsrc=["']/[0-9a-f]{4,}/["']""", re.I)
GTAG_DIRECT = re.compile(r"googletagmanager\.com/(?:gtag/js|gtm\.js)", re.I)

def check_analytics_double_load(pages):
    if not GA4_MEASUREMENT_ID:
        return
    for label, html in pages:
        direct = GTAG_DIRECT.search(html)
        gateway = GTAG_GATEWAY.search(html)
        if direct and gateway:
            line = html[: direct.start()].count("\n") + 1
            add("ERROR", "analytics-double-load", label, line,
                "the GA4 container loads twice — once directly from "
                "googletagmanager.com and once first-party via Cloudflare's Google "
                "Tag Gateway (a second copy of the analytics payload here)",
                "keep ONE. Prefer the first-party gateway, loaded on the window "
                "load event so it never competes with LCP")


# ── deflist-label-not-differentiated ─────────────────────────────────────────
# The health-guarantee "guarantee on one receipt" component: Window / Covered /
# Remedy / Voided by / Confirmed by / From rendered in the same colour AND weight
# as their values, so the block read as one grey slab.
# `.dt` is a real class on this site (the dial-list tag chip), so the element must be
# matched without a leading . or - or word char, or the wrong rule gets paired.
# Matched via RULE_BLOCK (one scan of the file) rather than a per-element regex with
# two unbounded `[^{}]*` stars around the element name — that shape backtracks
# catastrophically over a long brace-free region. (Re-base fix, Task 6.)
def EL(n):
    """Rule blocks whose selector names element `n` (not as part of a longer word
    and not as a class/id fragment)."""
    sel_re = re.compile(rf"(?<![.\w-]){n}(?![\w-])")
    class _ELRe:
        @staticmethod
        def finditer(text):
            return (m for m in rule_blocks(text) if sel_re.search(m.group(1)))
    return _ELRe

def check_deflist_labels(sources):
    for label, text in sources:
        dts = list(EL("dt").finditer(text))
        dds = list(EL("dd").finditer(text))
        if not (dts and dds):
            continue
        # Pair each dt rule with the dd rule sharing its scope (same ancestor chain).
        def scope_of(sel):
            # `[^{}]*` greedily swallows preceding comments/newlines, so keep only
            # the final selector line before the brace.
            last = sel.strip().split("\n")[-1].strip()
            last = re.sub(r"^.*\*/", "", last).strip()
            return last.rsplit(" ", 1)[0].strip()
        def is_css(sel):
            # These files are .astro — the same regex happily matches markup like
            # `<span class="dt">`. Only keep things that look like a CSS selector.
            return "<" not in sel and ">" not in sel and bool(re.match(r"^[.#a-z]", sel))

        def prop(body, name):
            m = re.search(rf"{name}:\s*([^;]+);", body)
            return m.group(1).strip() if m else None

        pairs = []
        for d in dts:
            sel = scope_of(d.group(1))
            full = d.group(1).strip().split("\n")[-1].strip()
            if not is_css(full):
                continue
            match = next((x for x in dds
                          if scope_of(x.group(1)) == sel
                          and is_css(x.group(1).strip().split("\n")[-1].strip())), None)
            if match:
                pairs.append((d, match))
        if not pairs:
            continue
        # Report the first pair that actually declares colours.
        dt, dd = next(((a, b) for a, b in pairs if prop(a.group(2), "color")), pairs[0])
        dt_colour, dd_colour = prop(dt.group(2), "color"), prop(dd.group(2), "color")
        same_colour = dt_colour == dd_colour
        same_weight = prop(dt.group(2), "font-weight") == prop(dd.group(2), "font-weight")
        line = text[: dt.start()].count("\n") + 1
        if same_colour and same_weight and dt_colour:
            add("WARN", "deflist-label-not-differentiated", label, line,
                "<dt> labels and their <dd> values share the same colour AND weight "
                "— the list reads as one undifferentiated block",
                "give the <dt> a distinct colour (var(--green-d)) and heavier weight, "
                "and lighten the <dd>")
        elif dt_colour and "muted" in dt_colour and dd_colour and "muted" not in dd_colour:
            # Different, but backwards: a muted label RECEDES behind its own value.
            # A label should lead the eye into the row, not sit quieter than it.
            add("WARN", "deflist-label-not-differentiated", label, line,
                f"<dt> labels use {dt_colour} while their values use {dd_colour} — the "
                "label is quieter than the thing it labels, so the block reads as one "
                "grey slab and the reader cannot scan the rows",
                "give the <dt> a distinct hue that leads (var(--green-d)), not a "
                "lower-contrast grey")


# ── icon-text-baseline-drift ─────────────────────────────────────────────────
# The health-guarantee trust ticks looked "scattered" on mobile: the flex row never
# set align-items, so each tick floated against a differently-wrapped label.
def check_icon_baseline(sources):
    """2026-07-26: the keyword used to be matched against everything between the
    previous } and the next {, which includes comments. A "/* FAQ-A GREEN TICK */"
    or "/* trust chips */" comment therefore flagged the rule beneath it whatever
    its selector said — that is how a vertical accordion stack (.faqA) and a plain
    grid container (.hero-chips, whose child li sets align-items itself) came to be
    reported as drifting icon rows. The keyword is now tested against the SELECTOR
    ONLY, with comments stripped first."""
    for label, text in sources:
        for m in rule_blocks(text):
            sel = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
            sel = sel.strip().split("\n")[-1].strip()
            if not re.search(r"tick|badge|check|trust|feat", sel, re.I):
                continue
            body = m.group(2).replace(" ", "")
            if "display:flex" not in body and "display:grid" not in body:
                continue
            # place-items / place-content are the shorthands that set align-items.
            if "align-items:" in body or "place-items:" in body or "place-content:" in body:
                continue
            line = text[: m.start()].count("\n") + 1
            add("WARN", "icon-text-baseline-drift", label, line,
                f"`{sel}` lays out an icon+label row but never sets "
                "align-items — when the label wraps, the glyph drifts off its text "
                "and the column reads as scattered",
                "use grid-template-columns:1rem 1fr with align-items:start so wrapped "
                "labels stay hanging-indented under themselves")


# ── smooth-scroll-breaks-anchors (refined 2026-07-26) ────────────────────────
# The original trap warned on ANY scroll-behavior:smooth. The pages now set
# scroll-margin-top to clear the header + sticky rail, so a reduced-motion-guarded
# GLOBAL rule on html is correct. A jump rail's own horizontal scroller must still
# warn — smooth there fights the active-pill auto-scroll.
def check_smooth_scroll(sources):
    for label, text in sources:
        # Strip /* ... */ first. Without this the check reads its own documentation:
        # a for-sale page carries a comment explaining WHY it sets
        # scroll-behavior:auto, and the phrase `scroll-behavior:smooth` inside that
        # prose was reported as a defect (2026-07-31). Third recurrence of this trap
        # after icon-baseline (2026-07-26) and the §1l selector check (2026-07-29).
        text = _strip_css_comments(text)
        for m in re.finditer(r"scroll-behavior:\s*smooth", text):
            before = text[: m.start()]
            line = before.count("\n") + 1
            block_start = max(before.rfind("{"), 0)
            selector = before[max(before.rfind("}", 0, block_start), 0):block_start]
            guarded = "prefers-reduced-motion" in before[-400:]
            global_rule = re.search(r"\bhtml\b\s*$", selector.strip()) is not None
            if guarded and global_rule:
                continue
            add("WARN", "smooth-scroll-breaks-anchors", label, line,
                "scroll-behavior:smooth here fights in-page navigation — on a jump "
                "rail it cancels the instant active-pill snap",
                "keep scroll-behavior:auto on rails/dials; the only allowed smooth "
                "rule is `html` inside @media (prefers-reduced-motion: no-preference)")


# ─────────────────────────────────────────────────────────────────────────────
# 1k. markup↔CSS drift — the 2026-07-28 adoption-cost failure mode.
#     A page assembled by porting the CSS kit and hand-writing markup drifts:
#     classes get styled and never rendered, and rendered components point at the
#     wrong class name. This scanner returned 0 ERROR / 0 WARN on a page whose FAQ
#     answers were white-on-white (1.00:1) and whose five mandated components had
#     no markup behind them at all — 101 classes styled, never rendered.
#
#     TRIAGE IS REQUIRED, and the check cannot do it for you:
#       styled + never rendered + spec-mandated   -> MISSING COMPONENT. Render it.
#       styled + never rendered + variant-not-used -> DEAD CODE. Delete it.
#     Deleting the CSS of a mandated component hides a spec violation.
#     On adoption-cost the split was 7 missing components vs 30 dead classes.
# ─────────────────────────────────────────────────────────────────────────────

# Components the for-sale spec mandates. Sourced from
# sessions/2026-07-19-for-sale-component-map.md + the 2026-07-28 harden pass,
# where all of these shipped as CSS with no markup behind them.
#
# Re-based 2026-09-26. The set above was the source repo's for-sale components, none of which
# any BSUK file renders, so the ERROR half of this check could never fire here. These are the
# kit components the working rules require on a rebuilt page, each styled and rendered in its
# own kit file: the counter strip (rule 16; layout-hero-counter-separation hooks on
# .counter-wrap), the stacking table (rule 13), the hero (rule 16), the page dial, the page
# nav, the section sheet, the FAQ block and the statement label.
# tests/py/test_page_hardening_scope.py holds every member to a class a kit file renders.
SPEC_MANDATED = {
    "counter-wrap", "stack-table", "kit-hero", "kit-dial", "kit-nav", "kit-sheet",
    "kit-faq", "stmt-label",
}

_QUOTED = re.compile(r'"([^"]*)"|\'([^\']*)\'')

# Tailwind is in this project's toolchain (package.json), so its utilities have no
# authored rule anywhere in src/ — they are generated. `sr-only` was reported as a
# missing class on adoption-cost for exactly this reason (2026-07-29). Tailwind
# variant syntax (`md:flex`, `w-1/2`) is filtered structurally below.
TAILWIND_UTILS = {"sr-only", "not-sr-only", "container", "group", "peer",
                  "antialiased", "truncate", "sticky", "fixed", "absolute",
                  "relative", "hidden", "block", "flex", "grid", "inline",
                  # Theme SENTINELS, not utilities: direction-d.css reads them with
                  # `[class*="text-cream"]` / `[class*="text-white"]` to exempt a lead
                  # paragraph from its var(--ink) rule (§1m). They never have a rule of
                  # their own; case-studies was reported for carrying one (2026-09-12).
                  "text-cream", "text-white"}


def _rendered_classes(markup):
    """(harvested, literal) class-token sets.

    `harvested` is every token the markup could possibly emit — including values
    scraped out of dynamic expressions. Dynamic attributes must be read from EVERY
    quoted branch, not just the first: `class={`tile ${x ? "on" : "off"}`}` renders
    `off` as readily as `on`, and taking only the first branch misreports `off` as
    dead code. Over-collecting is the SAFE direction for the never-rendered half.

    `literal` is only the tokens from a plain `class="..."` attribute. The orphan
    half must use this narrower set, because harvesting quoted strings out of
    expressions also picks up comparison VALUES: `class={`bbadge${b.badge === "top"
        ? " badge-top" : ""}`}` made the scanner report a non-existent class `top`
    on the baby page (2026-07-29).
    """
    harvested, literal = set(), set()
    for m in re.finditer(r'class(?:Name)?="([^"{}]+)"', markup):
        literal.update(m.group(1).split())
    harvested |= literal
    # Template-literal form: class={`a b ${cond ? "c" : "d"}`}
    for m in re.finditer(r"class(?:Name)?=\{`([^`]*)`\}", markup):
        raw = m.group(1)
        for q in _QUOTED.findall(raw):
            harvested.update((q[0] or q[1]).split())
        harvested.update(re.findall(r"[A-Za-z][\w-]*", re.sub(r"\$\{[^}]*\}", " ", raw)))
    # Expression form: class={cond ? "a" : "b"} / class={map[k]}
    for m in re.finditer(r"class(?:Name)?=\{([^}]*)\}", markup):
        for q in _QUOTED.findall(m.group(1)):
            harvested.update((q[0] or q[1]).split())
    # Astro's class:list={['kit-dial', cls]} — how every kit component renders its root. Not
    # read before 2026-09-26, so each kit root would have read as styled-but-never-rendered.
    for m in re.finditer(r"class:list=\{(\[.*?\])\}", markup, re.S):
        for q in _QUOTED.findall(m.group(1)):
            harvested.update((q[0] or q[1]).split())
    return harvested, literal


def _global_css():
    """The project-wide sheets, cached. A class styled here is not an orphan."""
    if not hasattr(_global_css, "_cache"):
        text = ""
        for g in ("src/styles/*.css", "src/layouts/*.astro", "src/components/**/*.astro"):
            for p in glob.glob(g, recursive=True):
                text += "\n".join(lines_of(p))
        _global_css._cache = text
    return _global_css._cache


def check_class_drift(src_pairs):
    for f, text in src_pairs:
        i = text.find("<style>")
        if i == -1:
            continue
        markup, css = text[:i], text[i:]
        css = css[:css.find("<script")] if "<script" in css else css
        css = _strip_css_comments(css)
        used, literal = _rendered_classes(markup)
        defined = set(re.findall(r"^\s*\.([A-Za-z][\w-]*)", css, re.M))

        unrendered = sorted(defined - used)
        mandated = [c for c in unrendered if c in SPEC_MANDATED]
        dead = [c for c in unrendered if c not in SPEC_MANDATED]
        if mandated:
            add("ERROR", "markup-css-drift", f, None,
                f"{len(mandated)} SPEC-MANDATED component(s) styled but never rendered: "
                + ", ".join(mandated),
                "Render them. Do NOT delete the CSS — that hides a spec violation. "
                "See .claude/skills/bsuk-page-hardening/SKILL.md §1k.")
        if dead:
            add("WARN", "markup-css-drift", f, None,
                f"{len(dead)} class(es) styled but never rendered: " + ", ".join(dead),
                "Triage each: a variant this page does not ship -> delete; a component "
                "the spec mandates -> render it. Never bulk-delete this list.")

        # Classes rendered with no rule at all — the 'wrong class name' half.
        # Literal tokens only, and a rule anywhere (page, global sheet, layout,
        # component, or a Tailwind utility) clears it.
        gcss = _global_css()
        orphans = sorted(c for c in literal - defined
                         if not re.search(rf"[.\[]{re.escape(c)}\b", css)
                         and not re.search(rf"[.\[]{re.escape(c)}\b", gcss)
                         and c not in TAILWIND_UTILS)
        if orphans:
            add("WARN", "markup-css-orphan", f, None,
                f"{len(orphans)} class(es) in markup with no CSS rule: " + ", ".join(orphans),
                "Either the component name is misspelled (adoption-cost put FAQ text in "
                "`.faqC-x`, a 16x16 icon box) or the rule lives in a global sheet — "
                "confirm which before editing.")


# ─────────────────────────────────────────────────────────────────────────────
# 1l. component-color-loses-to-descendant — the concrete mechanism behind
#     "this component looks wrong" (three instances on one page, 2026-07-28).
#     `.ship-tier{color:#fff}` is (0,1,0); `.ship-c p{color:#5b524a}` is (0,1,1)
#     and wins -> dark grey on forest green, 1.19:1, shipped live.
#     Fix: qualify the component rule — `.ship-c p.ship-tier{...}`.
#
#     COLOUR-vs-COLOUR ONLY. The background half (the white-on-white FAQ, where a
#     `.faq-d` wrapper set background:#fff inside a dark accordion) belongs to §1k
#     plus the runtime contrast sweep §2b. Widening this check to backgrounds
#     floods it. WARN, never ERROR: nesting is inferred from the markup, so this
#     is a "go and measure it" signal, not a verdict.
# ─────────────────────────────────────────────────────────────────────────────
BARE_TAGS = ("p", "li", "span", "dt", "dd", "a", "small", "strong", "em")
_HAS_COLOR = re.compile(r"(?<![-\w])color\s*:")


_CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def _strip_css_comments(css):
    """Blank out /* ... */ so selectors QUOTED IN PROSE are never analysed.

    This is how the icon-baseline checker produced 6 false WARNs on 2026-07-26, and
    adoption-cost repeats the trap: a comment documenting a past fix contains the
    literal text `.ship-c p{color:#5b524a}`, which made the same defect report twice
    (2026-07-29). Replace with spaces, not "", to keep byte offsets stable.
    """
    return _CSS_COMMENT.sub(lambda m: " " * len(m.group(0)), css)


def _subtrees_with_class(markup, cls):
    """Every element subtree (as raw markup) whose opening tag carries `cls`.

    Needed because CSS descendant selectors are about DOM containment. Matching on
    "both names appear in the file" instead pairs every kit rule with every
    component and floods the gate.
    """
    out = []
    for m in re.finditer(r"<([a-zA-Z][\w-]*)\b[^>]*class=\"([^\"]*)\"[^>]*>", markup):
        if cls not in m.group(2).split():
            continue
        tag, gt = m.group(1), m.end()
        if markup[gt - 2] == "/":                      # self-closing: empty subtree
            out.append("")
            continue
        depth, pos = 1, gt
        step = re.compile(rf"<(/?){re.escape(tag)}\b", re.I)
        while depth and pos < len(markup):
            n = step.search(markup, pos)
            if not n:
                break
            depth += -1 if n.group(1) else 1
            pos = n.end()
        out.append(markup[gt:pos])
    return out


def check_component_color_specificity(src_pairs):
    for f, text in src_pairs:
        i = text.find("<style>")
        if i == -1:
            continue
        markup, css = text[:i], text[i:]
        css = css[:css.find("<script")] if "<script" in css else css
        css = _strip_css_comments(css)

        # Kit rules `.ancestor tag{...color...}` — specificity (0,1,1).
        descendants = []
        for m in re.finditer(r"\.([A-Za-z][\w-]*)\s+([a-z]+)\s*\{([^}]*)\}", css):
            anc, tag, body = m.group(1), m.group(2), m.group(3)
            if tag in BARE_TAGS and _HAS_COLOR.search(body):
                descendants.append((anc, tag))

        # Component rules `.component{...color...}` — specificity (0,1,0).
        # Anchor on line start: a `(?<![\w.\s>+~])` lookbehind looks right but also
        # rejects a rule at the start of a line, because the preceding newline IS
        # whitespace — it silently collected nothing (caught by the RED test,
        # 2026-07-29). Line-anchoring keeps this to genuine single-class rules, so
        # the prescribed fix `.ship-c p.ship-tier{...}` is correctly NOT collected,
        # and neither is a descendant selector like `.a .b{...}` at (0,2,0).
        singles = {m.group(1) for m in
                   re.finditer(r"^[ \t]*\.([A-Za-z][\w-]*)\s*\{([^}]*)\}", css, re.M)
                   if _HAS_COLOR.search(m.group(2))}

        for anc, tag in descendants:
            # Nesting must be established in the DOM, not by co-occurrence in the
            # file. Pairing "ancestor appears somewhere" with "component appears
            # somewhere" is a cartesian product and produced 586 WARNs across 8
            # pages (2026-07-29) — e.g. `.dial-ring span` paired with every
            # component on the page, none of which live inside a .dial-ring.
            subtrees = _subtrees_with_class(markup, anc)
            if not subtrees:
                continue
            for comp in sorted(singles):
                if comp == anc:
                    continue
                pat = re.compile(rf'<{tag}\b[^>]*class="[^"]*\b{re.escape(comp)}\b')
                if not any(pat.search(s) for s in subtrees):
                    continue
                # Already fixed? A selector that qualifies the component — the very
                # fix this check prescribes — clears it. adoption-cost ships both
                # `.btn-clay{color:#fff}` and `.adopt-main a.btn-clay{color:#fff}`;
                # without this, .btn-clay accounted for 5 of 8 findings and every
                # one of them was already correct (2026-07-29).
                c = re.escape(comp)
                if re.search(rf"\.{re.escape(anc)}\b[^{{}}]*\.{c}\b", css) or \
                   re.search(rf"\b{tag}\.{c}\b", css):
                    continue
                add("WARN", "component-color-loses-to-descendant", f, None,
                    f".{comp} (0,1,0) sets color but `.{anc} {tag}` (0,1,1) outranks it "
                    "— the component colour is silently discarded",
                    f"Qualify the component rule: `.{anc} {tag}.{comp}{{...}}`. Confirm "
                    "with getComputedStyle in Playwright before editing "
                    "(.claude/skills/bsuk-gate-integrity/SKILL.md).")


# ─────────────────────────────────────────────────────────────────────────────
# 1m. theme-lead-color-outranks-component — the §1l gap the near-me router
#     shipped through (2026-09-12). src/styles/direction-d.css paints the first
#     paragraph after an h1/h2 `var(--ink)` with
#     `body.theme-d h1 + p:not([style*="color"]):not([class*="text-cream"]):not([class*="text-white"])`
#     — specificity (0,4,3). A page's `.pg .hero .lead{color:#dcebe3}` is (0,3,0)
#     and loses silently: the lead rendered ink on a dark green field, invisible.
#     §1l reads only the page's own CSS and only the `.ancestor tag` shape, and
#     a gradient-skipping runtime sweep skipped the hero. Caught by eye.
#     The rule's own escape hatch is a class containing `text-cream`/`text-white`
#     or an inline color; that is the prescribed fix, not a specificity war.
#     WARN: the pairing h-tag→p is read from source markup, not a painted DOM.
# ─────────────────────────────────────────────────────────────────────────────
_RULE_RE = re.compile(r"([^{}]+)\{([^}]*)\}")
_LEAD_SEL = re.compile(r"^body\.theme-d\s+(h[1-6])\s*\+\s*p\b")


def _specificity(sel):
    """(ids, classes+attrs+pseudo-classes, elements) for one compound/complex selector.
    `:not(X)` counts X's specificity, per CSS Selectors 4. Pseudo-elements ignored."""
    sel = re.sub(r"::[\w-]+", "", sel)
    ids = len(re.findall(r"#[\w-]+", sel))
    attrs = len(re.findall(r"\[[^\]]*\]", sel))
    sel_no_attr = re.sub(r"\[[^\]]*\]", "", sel)
    classes = len(re.findall(r"\.[\w-]+", sel_no_attr))
    pseudo = len(re.findall(r":(?!not\b)[\w-]+", sel_no_attr))
    elements = len(re.findall(r"(?:^|[\s>+~(])([a-zA-Z][\w-]*)", sel_no_attr))
    return (ids, classes + attrs + pseudo, elements)


_LIGHT_TOKENS = ("#fff", "white", "var(--cream)", "var(--warm-white)", "#faf7f4", "#fff9f6")


def _declares_light_color(body):
    """True when a rule body's `color:` resolves to something light (luminance > .5).
    Unresolvable `var()`s other than the known light tokens are treated as NOT light,
    so the check stays quiet rather than guessing."""
    m = re.search(r"(?<![-\w])color\s*:\s*([^;}]+)", body)
    if not m:
        return False
    v = m.group(1).strip().lower()
    if any(v.startswith(t) for t in _LIGHT_TOKENS):
        return True
    hm = re.match(r"#([0-9a-f]{3}|[0-9a-f]{6})\b", v)
    if hm:
        h = hm.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.5
    rm = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", v)
    if rm:
        r, g, b = (int(x) / 255 for x in rm.groups())
        return (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.5
    return False


def check_theme_lead_color(src_pairs, theme_css):
    theme = _strip_css_comments(theme_css)
    lead_rules = []                                   # (h-tag, selector, specificity)
    for m in _RULE_RE.finditer(theme):
        if not _HAS_COLOR.search(m.group(2)):
            continue
        for sel in m.group(1).split(","):
            sel = " ".join(sel.split())
            lm = _LEAD_SEL.match(sel)
            if lm:
                lead_rules.append((lm.group(1), sel, _specificity(sel)))
    if not lead_rules:
        return
    for f, text in src_pairs:
        i = text.find("<style")
        if i == -1:
            continue
        markup, css = text[:i], text[i:]
        css = css[:css.find("<script")] if "<script" in css else css
        css = _strip_css_comments(css)
        page_rules = []                               # (selector, last class, specificity)
        for m in _RULE_RE.finditer(css):
            body = m.group(2)
            if not _HAS_COLOR.search(body) or "!important" in body:
                continue
            # Only a LIGHT declared colour is a defect when the theme's var(--ink)
            # wins: a dark lead losing to ink is invisible in the other sense — nobody
            # can see the difference. First survey (2026-09-12) fired on 18 light-hero
            # pages for exactly that reason; a check that cries wolf once is ignored.
            if not _declares_light_color(body):
                continue
            for sel in m.group(1).split(","):
                sel = " ".join(sel.split())
                if not sel or sel.startswith("@"):
                    continue
                last = re.search(r"\.([\w-]+)$", sel)
                if last:
                    page_rules.append((sel, last.group(1), _specificity(sel)))
        for hm in re.finditer(r"<(h[1-6])\b[^>]*>.*?</\1>\s*<p\b([^>]*)>", markup, re.S):
            htag, attrs = hm.group(1), hm.group(2)
            if re.search(r'style="[^"]*color', attrs):
                continue
            cm = re.search(r'class="([^"]*)"', attrs)
            classes = cm.group(1).split() if cm else []
            if any("text-cream" in c or "text-white" in c for c in classes):
                continue
            for ht, tsel, tspec in lead_rules:
                if ht != htag:
                    continue
                for psel, cls, pspec in page_rules:
                    if cls in classes and pspec < tspec:
                        fmt = lambda t: "(" + ",".join(map(str, t)) + ")"
                        add("WARN", "theme-lead-color-outranks-component", f, None,
                            f"`{psel}` {fmt(pspec)} sets color on the paragraph after an <{htag}>, but the "
                            f"theme's `{tsel[:60]}…` {fmt(tspec)} outranks it — the lead renders var(--ink) "
                            "whatever the page says (invisible on a dark hero)",
                            "Add a class containing `text-cream` (or `text-white`) to that <p> — the theme "
                            "rule's own escape hatch — or set the colour inline. Confirm with "
                            "getComputedStyle in Playwright (.claude/skills/bsuk-gate-integrity/SKILL.md).")


DEFAULT_JSON = "docs/reports/page_hardening.json"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("slugs", nargs="*", help="scope the scan to these built pages")
    ap.add_argument("--fail-on-error", action="store_true",
                    help="exit 1 when any ERROR is found (default: report only)")
    ap.add_argument("--json", nargs="?", const=DEFAULT_JSON, default=None,
                    metavar="PATH",
                    help=f"write the machine-readable result (default {DEFAULT_JSON})")
    ns = ap.parse_args(sys.argv[1:] if argv is None else argv)
    args = ns.slugs
    fail_on_error = ns.fail_on_error
    files = src_files(args)
    pages = sorted(glob.glob(f"{DIST}/**/index.html", recursive=True))
    pages = select_pages(pages, args)

    check_css_math(files)
    check_bottom_bar_z(files)
    check_infographic_crop(files)
    check_fullbleed_grid(files)
    check_absolute_hero(files)
    check_clay_small_text(files)
    check_opacity_text(files)
    check_link_underline(files)
    check_known_traps(files, pages)

    # 2026-07-26 gate gaps — see tests/test_page_hardening_new_checks.py
    src_pairs = [(f, "\n".join(lines_of(f))) for f in files]
    check_hero_preload_drift(src_pairs)
    check_tap_target_spacing(src_pairs)
    check_form_overflow(src_pairs)
    check_deflist_labels(src_pairs)
    check_icon_baseline(src_pairs)
    check_smooth_scroll(src_pairs)

    # 2026-07-29: markup↔CSS drift + component colour specificity
    # (adoption-cost harden lessons §1 and §2)
    check_class_drift(src_pairs)
    check_component_color_specificity(src_pairs)

    base = "src/layouts/BaseLayout.astro"
    theme = "\n".join(lines_of("src/styles/direction-d.css") +
                      lines_of("src/styles/global.css"))
    # 2026-09-12: the theme's h1/h2 + p lead rule vs a page's own lead colour
    check_theme_lead_color(src_pairs, theme)
    if os.path.exists(base):
        check_font_families("\n".join(lines_of(base)), theme)

    if pages:
        check_img_srcset(pages)
        check_title_case(pages)
        check_analytics_double_load(
            [(p.replace(DIST + "/", "").replace("/index.html", "/"),
              open(p, encoding="utf-8").read()) for p in pages])

    errs = [f for f in findings if f["sev"] == "ERROR"]
    warns = [f for f in findings if f["sev"] == "WARN"]
    print(f"BSUK page-hardening scan — {len(files)} source files, {len(pages)} built pages\n")
    for group, title in ((errs, "ERROR"), (warns, "WARN")):
        if not group:
            continue
        print(f"── {title} ({len(group)}) " + "─" * 40)
        for f in group:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"  [{f['check']}] {loc}\n      {f['msg']}\n      fix: {f['fix']}\n")
    if not findings:
        print("✅ clean — no known hardening defects found")
    else:
        print(f"{len(errs)} ERROR · {len(warns)} WARN")
    if ns.json:
        labels = list(files) + [p.replace(DIST + "/", "").replace("/index.html", "/")
                                for p in pages]
        out = write_json_report(ns.json, labels)
        print(f"JSON report → {out}")
    return 1 if (fail_on_error and errs) else 0


if __name__ == "__main__":
    sys.exit(main())
