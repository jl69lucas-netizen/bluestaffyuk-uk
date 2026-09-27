---
name: bsuk-page-hardening
description: "Use when a BSUK page is built but feels rushed, or before any deploy/final pass, or when the breeder reports a page looks wrong on mobile/desktop — zoomed images, broken or overlapping hero art, a jump-rail that does nothing, buttons that wrap or stretch, text cut off at the screen edge, headings that ignore their CSS, or Lighthouse contrast / link-distinguishability / image-delivery flags. Runs an automatic scan for every UI/UX/perf/a11y defect class that has actually shipped on this site, then applies the banked fix for each. Triggers: \"harden this page\", \"polish the UI\", \"fix the mobile view\", \"why is this cut off\", \"sweep the contrast fix\", \"make it modern/clean\", final-pass QA."
---

# SKILL: BSUK Page Hardening (v2.0 — 2026-07-29)

**v2.0 adds the 2026-07-28 adoption-cost lessons.** v1.0 assumed the enemy was a
defect the scanner could not see. v2.0 assumes the harder case: **a clean scan on a
broken page.** `scripts/page_hardening_scan.py` returned `0 ERROR · 0 WARN` on a page whose
FAQ answers were invisible (1.00:1) and whose five mandated components had no markup
behind them. Both halves — static scan AND runtime probes — are mandatory, always.

**Before you fix anything a gate reports, read `.claude/skills/bsuk-gate-integrity/SKILL.md`.**
Nine checkers have cried wolf on this cluster, and building v2.0 added three more
false-positive classes that were fixed in the checks rather than the pages — the
`§1l` check reported **586 WARN** on its first pass and **2** once nesting was
resolved from the DOM instead of from name co-occurrence.

**Why this exists.** The same UI defects keep reaching production because they are
invisible in source review — the CSS *looks* right. Each one below was found the
expensive way: the breeder spotted it on a phone after deploy. This skill turns
every one of them into a check that runs automatically.

**Run this BEFORE `bsuk-final-page-pass`.** That skill audits structure, schema and
SEO; this one audits whether the page actually *renders* correctly.

---

## 0. The static half

```bash
npm run -s build                                   # nothing below works on a stale dist/
python3 scripts/page_hardening_scan.py <slug>      # 21 checks
```

`ERROR` = shipped-broken, fix before deploy. `WARN` = very likely wrong, eyeball it.
Omit the slug to sweep the whole site. Add `--fail-on-error` for CI. Seam parity has no
script here (the source repo's was not ported — source repo only); count seams against
sections by hand, or let the render harness do it.

**Pass slugs literally.** zsh does not word-split an unquoted `$VAR`, so
`python3 … $SLUGS` arrives as one argument, matches no page, and the gate reports
PASS having examined nothing. **Read the examined count in the gate's own output
before you believe a pass** — see `.claude/skills/bsuk-gate-integrity/SKILL.md`.

The scan is slow and always has been: roughly 19 s of fixed cost plus ~6 s per page,
so a sweep of the whole site runs to several minutes. Treat the sitewide run as a batch job
and scope interactive runs to the cluster you are working on.

**Both halves are required.** The static scan alone would have missed the two worst
bugs of 2026-07-23 *and* every defect of 2026-07-28 — that page scanned
`0 ERROR · 0 WARN` while its FAQ answers were invisible. Run §2 Runtime as well.

---

## 1. Static defect catalogue (what the scanner knows)

### 1a. `css-math-spacing` — ERROR — *the silent heading-size killer*
`clamp(1.7rem,1.2rem+2.2vw,2.6rem)` is **invalid CSS**. Math functions require
whitespace around `+` and `-`. Without it the entire declaration is dropped and
the element falls back to the global rule — so `h1` renders at 48px while the
source says 2.26rem, and nothing in the file looks wrong.

> **Real cost:** the home-raised hero was 524px instead of ~400px for its whole
> first week live. Two rounds of "make the hero shorter" edits did nothing
> because the rule was never applied. Same bug found on the source repo's `/available/`.

**Fix:** `clamp(1.5rem, 1.02rem + 1.55vw, 1.98rem)`.
**Verify:** `getComputedStyle(h1).fontSize` matches the clamp, not the global token.

### 1b. `bottom-bar-under-tabbar` — ERROR — *"the jump-rail is broken"*
The global `MobileTabBar` is `fixed bottom-0 … z-50`. Any other bottom-pinned UI
at `bottom:0` with a lower z-index renders **underneath it** and looks like dead
code. It isn't broken; it's buried.

**Fix — do NOT pin it to the bottom at all.** The breeder rejected bottom
placement outright (2026-07-23): even correctly stacked above the tab bar it
"interferes with the page's bottom view". **Mobile jump-rails go at the TOP**,
sticky under the header, matching every sibling for-sale page
(`.chero-rail`, `.egg-rail`):

```css
.railB{position:sticky; top:var(--hdr); z-index:40;
  background:rgba(244,241,234,.985);      /* bone — a steel bar merges into the header */
  border-bottom:1px solid var(--bd);
  box-shadow:0 6px 14px rgba(60,30,10,.07);}
```

Differentiate per page with the **chip** treatment, not the bar position
(siblings use single-line pills; home-raised uses stacked two-line chips).
Scroll the active chip into view on scroll-spy so the rail tracks the reader.

**`--hdr` must equal the REAL header height (96px).** It was defaulting to 72px,
which parked the sticky desktop dial 8px *behind* the header. Anchors then need
`scroll-margin-top: calc(var(--hdr) + 16px)` on desktop and
`calc(var(--hdr) + 74px)` on mobile (header + rail + gap) — verify by clicking a
rail chip and confirming the H2 lands below the rail, not under it.

### 1c. `infographic-cropped-mobile` — ERROR — *unreadable infographics*
Infographics carry **baked-in text**. Forcing a 16:9 infographic into a 5:4 or 4:5
mobile box with `object-fit:cover` shaves ~30% off **each side** and cuts the words.

**Fix — split the two image classes; they are not the same thing:**
```css
/* infographics: native ratio, never cover-cropped */
.sec-img.inf-img{width:100vw;margin-left:calc(50% - 50vw);
  aspect-ratio:1408/768;object-fit:contain;background:#fff;}
/* real OG photos: the taller mobile frame (IMAGE-DESIGNS §7) */
.sec-img.og-photo{aspect-ratio:5/4;object-fit:cover;}
```

### 1d. `absolute-hero-not-unwound` — WARN — *overlapping / collapsing hero art*
Absolutely-positioned hero art with `%` widths overlaps on desktop (covering the
puppies' faces) and collapses to slivers on mobile.

**Fix — do not tune the offsets; remove the mechanism.** Lay hero art out as a
grid and get the "scatter" from rotation, so overlap is structurally impossible:
```css
.hero-scatter{display:grid;grid-template-columns:1fr 1fr;gap:9px 8px;place-items:center;}
.pofig{position:relative;width:100%;max-width:148px;}
.pofig.p1{transform:rotate(-4deg) translateY(-5px);}   /* alternate per card */
```
Captions/badges pinned *inside* a card stay absolute — that's correct, and the
scanner ignores them.

### 1e. `cta-small-text-contrast` / `opacity-dims-text-contrast` — WARN
`--color-cta` (brass) is a **fill, not a text colour on a light surface**: it measures
**2.1:1** on `--color-surface` and **2.4:1** on `--color-surface-raised`, so it fails at
every size there — there is no darker small-text variant to fall back to. Small readable
text on light is `--color-text` (13.9:1) or `--color-brand` (10.4:1). Brass is correct as
a **fill labelled `--color-cta-ink`** (6.8:1), and as an accent on the dark bands
(4.9:1 on `--color-surface-inverse`, 6.8:1 on `--color-surface-deep`). Separately, any
`opacity` on a text rule silently drags contrast down — re-measure the pair after adding
one, against the 4.5 floor. Ratios computed from `data/design/contrast.json` by
`tests/py/test_design_tokens.py`.

### 1e-bis. Desktop dial TOC — the CANONICAL row metrics (cluster-wide, LOCKED)
The breeder rejected a "density pass" that shrank rows to `.7rem` / `3.5px 6px`
with the tag hidden: *"I can hardly read the text or click."* **Readability beats
compactness** — the card scrolls internally if it ever runs long.

**Every for-sale / comparison desktop dial matches `/buy-staffy-puppies-for-sale-uk/`
(`.tdial`) exactly.** Copy these numbers verbatim; only the palette changes per
page tuple (light card vs dark-kennel card):

```css
/* sidebar column */   grid-template-columns:196px minmax(0,1fr); gap:28px;
/* card  */ display:flex;flex-direction:column;gap:10px;align-items:stretch;
            border-radius:16px;padding:12px 10px;
            position:sticky;top:calc(var(--hdr) + 16px);
            max-height:calc(100vh - var(--hdr) - 32px);overflow-y:auto;
/* ring  */ 64px outer · 50px inner · number 15px serif · "of N" 7px · margin:2px auto 0;flex:none
/* list  */ display:grid;grid-template-columns:1fr;gap:1px;
            border-top:1px dashed;padding-top:8px;
/* row   */ display:flex;gap:7px;align-items:baseline;
            font-size:.74rem;line-height:1.25;padding:5px 7px;border-radius:8px;
/* num   */ font-size:.7rem;width:16px;flex:none;font-weight:700;font-variant-numeric:tabular-nums;
/* tag   */ margin-left:auto;font-size:.56rem;font-weight:600;
            color:#fff;background:var(--color-cta-ink);border-radius:50px;padding:1px 6px;white-space:nowrap;
```

**The tag pill is always visible** — hiding it on inactive rows was part of the
rejected density pass. Verify: 18 rows ⇒ card ≈ **705–725px**, every row ≥ 24px
tall (WCAG 2.5.8), label ≥ 4.5:1.

**Dial/rail contrast — two variants, do NOT mix them up:**

| Dial variant | Background | Numerals | Ratio |
|---|---|---|---|
| **Light card** (blue, blue and white) | white `#fff` | `#6b625a` | 5.9:1 ✓ |
| **Dark kennel** (home-raised) | `#234f3b` | `#9fc7b0` | 5.0:1 ✓ |
| Mobile rail `.p` | `#234f3b` | `#c9f2db`, **no opacity** | 5.4:1 ✓ |

Applying the light-card `#6b625a` to a dark dial makes it unreadable. Always
check which variant the page ships before "sweeping the contrast fix".

### 1e-ter. `header-not-title-case` — ERROR — *site-wide heading standard*
**Every H1–H6 on every page uses AP-style Title Case.**

**The rule lives in the pack, not here.** `rules/headings.md` `title-case-headings` is the
single statement of what Title Case means on this site — which words are capitalised, which
≤3-letter articles drop mid-title, how an em dash and a hyphenated compound behave, and
which acronyms and brand tokens are never touched. Restating it in a skill is how the two
drift apart, and the pack is the copy a checker can be pointed at. Read it there; the
companion rules are `rules/headings.md` `header-style-declared` (a page declares its heading
style once) and `heading-hierarchy-outline-gate` (the outline is approved before any code).

**What this scanner adds** is only the detection: it flags a heading on a built page whose
casing disagrees with the pack. A sentence-case heading is a defect (one source page shipped
62 of them, 2026-07-23).

**Scope — headings only.** FAQ accordion questions live in `<summary>`, not in a heading
tag, and stay **conversational sentence case** ("How much does a Blue Staffy puppy cost?").
Do NOT title-case them. A page that renders its FAQ questions *as H3* will be flagged by the
scanner; that is a pre-existing inconsistency in the page, not a licence to change the FAQ
voice.

### 1f. `links-colour-only` — WARN — WCAG 1.4.1
In-body links distinguished by colour alone fail Lighthouse.
```css
.content p a,.content li a{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:2px;}
.content p a.btn,.content a.geo-card,.content a.read-card{text-decoration:none;}
```

### 1g. `img-no-srcset` — WARN — image-delivery savings
Any image whose intrinsic width is far above its rendered width. Ship siblings and
a real `sizes`:

| Slot | Rendered | Ship | `sizes` |
|---|---|---|---|
| Hero polaroid | ~150px | `-320` | `(max-width:980px) 42vw, 158px` |
| Puppy card | ~226px | `-440` | `(max-width:640px) 46vw, 226px` |
| Read-card thumb | 120px | `-240` | `120px` |
| In-body infographic | 760px | `-760` | `(max-width:900px) 92vw, 760px` |

> Real cost: 163 KiB flagged on hero polaroids (620×720 shown at ~200px) plus
> 760px thumbnails rendered into a 120px slot.

### 1h. Known render traps (already banked in MEMORY, re-checked here)
`svg-in-css-content` · `escaped-svg` (missing `set:html`) · `user-select-none`
(banned site-wide) · `smooth-scroll-breaks-anchors`.

---

### 1i. The 2026-07-26 gate gaps — *the six the breeder had to find by hand*

Banked after the for-sale cluster PageSpeed/UX review. Every one of these shipped to
production on pages that had already passed `bsuk-final-page-pass`. The scan across all
6 built for-sale pages found each defect is **cluster-wide**, not confined to the page
it was reported on — the breeder saw a sample, not the extent.

| Check | Sev | Catches | Found on |
|---|---|---|---|
| `hero-preload-srcset-drift` | ERROR | `heroPreload` set and the LCP `<img>` uses `srcset`, but `heroPreloadSrcset` is missing — the preload scanner resolves a *different* candidate than the renderer, so the hero downloads twice | dna-tested |
| `tap-target-spacing` | ERROR | Nav/rail/dial pills with `gap` < 10px — adjacent targets fall inside each other's 24px axe exclusion zone. **Checks the desktop dial too**, which is why Lighthouse flagged tap targets on desktop where the mobile rail is `display:none` | **all 6**, 13 instances |
| `form-control-ios-zoom` | ERROR | Form controls under 16px, **including via `font:inherit`** resolving to a smaller ancestor label. Under 16px iOS SThe Kennel Clubri auto-zooms on focus and the form's right edge leaves the viewport — this reads to users as "the form is broken / cut off" | **all 6** |
| `form-control-overflow` | ERROR | A form grid whose children never set `min-width:0`. Grid children default to `min-width:auto` and refuse to shrink below their content | — |
| `font-family-loaded-unused` | ERROR | A family requested in `BaseLayout` that no CSS rule ever resolves to | Lora + Sora, **site-wide** |
| `analytics-double-load` | ERROR | The same GA4 container loading twice — direct `googletagmanager.com` **and** first-party via the edge host (chosen in project 6)'s Google Tag Gateway | see caveat below |
| `deflist-label-not-differentiated` | WARN | `<dt>` and `<dd>` sharing colour+weight, **or** a `--muted` label sitting quieter than its own `--ink` value, so the block reads as one staffy slab | a what's-included receipt |
| `icon-text-baseline-drift` | WARN | An icon+label flex/grid row with no `align-items` — when the label wraps, the glyph drifts off its text and the column reads as scattered | 4 of 6 |

**`analytics-double-load` caveat — this one cannot fire on `dist/`.** The first-party
`/70de/` script is injected by **the edge host (chosen in project 6) at the edge**, not by our build, so it is
absent from local output. Run this check against the **live URL**, not `dist/`:

```bash
curl -s https://SITE_URL_PLACEHOLDER/<slug>/ | grep -cE 'googletagmanager\.com|src="/[0-9a-f]{4,}/"'
```
Two hits = double-load. `/70de/` is **GA4, not Rocket Loader** — confirmed 2026-07-26 by
fetching it (`// Copyright 2012 Google Inc.` + the `G-MEWJ9GVC4T` container). Turning
Rocket Loader off never could have fixed it.

### 1j. `smooth-scroll-breaks-anchors` — REFINED 2026-07-26

The original trap warned on **any** `scroll-behavior:smooth`. That was right when the
pages had no `scroll-margin-top`. They do now (header 96px + sticky rail ~54px), so the
rule is narrowed:

- **Allowed:** `html{scroll-behavior:smooth}` inside `@media (prefers-reduced-motion: no-preference)`.
- **Still warns:** smooth on a jump rail / dial's own scroller — it fights the instant
  active-pill snap.

Anything relying on the old blanket ban must be re-verified per page before delivery
smooth scroll: click every jump link at 390px and 1280px and confirm the target heading
lands *below* the sticky chrome.

### 1k. `markup-css-drift` / `markup-css-orphan` — ERROR / WARN — *the clean-scan trap*

Added 2026-07-29. The page was assembled by porting the CSS kit and hand-writing
markup that drifted from it. On `/blue-staffy-pup-sale-uk/`: **101 classes
defined and never rendered** — five of them components the for-sale spec mandates —
and the two that *were* rendered pointed at **the wrong class names**, so FAQ question
text sat in `.faqC-x`, a 16×16 icon box, and every question crushed to 16px.

**Triage is mandatory and the scanner cannot do it for you:**

| Styled, never rendered | When | Action |
|---|---|---|
| **Missing component** | it is in `SPEC_MANDATED` (`scripts/page_hardening_scan.py`): kit classes whose own file must keep rendering them — `.counter-wrap`, `.stack-table`, `.kit-hero`, `.kit-dial`, `.kit-nav`, `.kit-sheet`, `.kit-faq`, `.stmt-label`. Not a presence check: no page is required to use them, and a page that imports the kit component may restyle its class | **Render it.** Deleting the CSS hides a spec violation. Raised as ERROR. |
| **Dead code** | it belongs to a variant this page does not ship (`.k1` when the page ships K2) | Delete it. Raised as WARN. |

On one source page that split was **7 missing components vs 30 genuinely dead classes**.
**Never bulk-delete a WARN list.**

What the first real run found on pages the previous scanner called clean — one page
had **20** unrendered classes (5–6 whole components, including the `.faq-d` class
behind the white-on-white FAQ bug), another **14** (a care-cards grid, a `chkT`
checklist, a `priceband` scale). The census itself was not ported — source repo only.

**Two false positives to expect, both already handled:** a *comparison value* is not a
class (`class={`bbadge${b.badge === "top" ? …}`}` reported a class `top`), so the
orphan half reads literal `class="…"` tokens only; and Tailwind utilities like
`sr-only` are generated, with no authored rule in `src/`.

### 1l. `component-color-loses-to-descendant` — WARN — *"the component looks wrong"*

Added 2026-07-29. Every such complaint on adoption-cost traced to a generic descendant
selector out-ranking a component selector:

| Component rule | Beaten by | Result |
|---|---|---|
| `.ship-tier{color:#fff}` (0,1,0) | `.ship-c p{color:#5b524a}` (0,1,1) | dark staffy on the steel band, **1.19:1** |
| answer in `.faq-d` (`background:#fff`) inside the dark accordion | `.faqC-item p{color:rgba(255,255,255,.82)}` | **white on white, 1.00:1 — invisible** |

**Rule: when a component's inner element is a bare tag (`p`, `span`, `li`, `dt`, `dd`,
`a`), qualify the component rule** — `.ship-c p.ship-tier{…}` — or the kit's generic
descendant rules silently win. The `:not()` form works too:
`.xsell p:not(.xsell-k){…}`.

Scope: **colour vs colour only.** The second row above is a *background* set by a
wrongly-applied class — that belongs to §1k plus the runtime contrast sweep §2b.
Widening §1l to backgrounds floods it.

**WARN, never ERROR** — nesting is inferred from markup, so this is a "go and measure
it" signal, not a verdict. Confirm with `getComputedStyle` in Playwright first.

> **What building this check taught, which generalises to every check you write.**
> First pass: **586 WARN** on 8 pages. Three separate bugs, all mine:
> 1. **Nesting was a cartesian product** — "ancestor somewhere in the file" ×
>    "component somewhere in the file" paired `.dial-ring span` with every component
>    on the page. CSS descendant selectors are about **DOM containment**; resolve the
>    subtree, don't co-occur names.
> 2. **An existing rescue rule already fixed it** — adoption-cost ships both
>    `.btn-cta{color:#fff}` and `.adopt-main a.btn-cta{color:#fff}`, the prescribed
>    fix. 5 of 8 findings were already correct code.
> 3. **Selectors quoted inside `/* … */` were analysed** — a comment documenting a
>    past fix contains the literal text `.ship-c p{color:#5b524a}`, so the same defect
>    reported twice. **This is the identical trap that produced 6 false icon-baseline
>    WARNs on 2026-07-26.** Strip comments before parsing CSS. Always.

### 1m. `theme-lead-color-outranks-component` — WARN — *the invisible hero lead*

Added 2026-09-12. A theme stylesheet (a theme stylesheet the port did not carry — source repo only) painted the first
paragraph after an `h1`/`h2` in the body ink with a `body.<theme-class> h1 + p:not(…)×3`
rule at **(0,4,3)**. A page's own `.pg .hero .lead{color:…}` is (0,3,0) and loses
silently: on a dark hero the lead rendered body ink on the steel band, invisible. §1l never saw it
(page CSS only, `.ancestor tag` shape only) and a gradient-skipping runtime sweep
skipped the hero too; a fold screenshot caught it.

**Fix — use the rule's own escape whelp, not a specificity war:** give the paragraph
a class containing `text-surface` (or `text-white`), or an inline colour. The check
reads the `hN → p` pairing from source markup, so it is a "go and measure it"
signal. Verify with `getComputedStyle(lead).color`.

## 2. Runtime probes (§Runtime — the static scan CANNOT catch these)

> **Use Playwright, not the Browser pane.** The Browser pane reports `vw: 0` and every
> `getBoundingClientRect()` comes back zero — elements are in the DOM but nothing
> paints, so every probe below reads as a false pass. Sequence: `browser_resize` →
> `browser_navigate` → `browser_evaluate`. Banked as
> `reference_intersectionobserver_needs_painting_page`; it applies to **all**
> measurement, not just scroll-spy.
>
> **Breakpoints: 375 / 768 / 1280 — and 768 is the one that fails.** On the
> adoption-cost pass, 375 and 1280 were clean and *every* line-length defect was at
> tablet.
>
> **Capture components with element screenshots** (`browser_take_screenshot` with
> `target`). A viewport screenshot resets scroll, and a prior `scrollIntoView` does
> not survive it.
>
> **Your own probes are gates too, and they lie.** Two of mine were wrong on
> 2026-07-28: the contrast sweep tested `display:none` on the element but not on its
> ancestors (8 of 13 "failures" evaporated — skip when `!el.offsetParent` or the rect
> is zero-sized), and a hero measured 432px only because I included its `16px 0 20px`
> padding instead of measuring `.hero-grid`, the element the spec actually names.

### 2z. `srcset-sizes-mismatch` — *the oversized-hero root cause*

Added 2026-07-26. Both oversized heroes PageSpeed flagged shared one root cause that is
**not statically knowable**: the `sizes` attribute under-declares the real rendered box,
so the browser resolves a far larger candidate than the layout needs.

| Page | `sizes` declares | Actually renders at | Served |
|---|---|---|---|
| home-raised | `(max-width:980px) 42vw, 158px` | 299 × 348 | 620 × 622 (17.8 KiB wasted) |
| dna-tested | `(max-width:980px) 92vw, 420px` | 665 × 499 | 880 × 660 (17.1 KiB wasted) |

A static scan cannot know the rendered box — that is exactly the information `sizes` is
lying about. **Do not attempt a static version of this check**; it will either miss the
defect or fire on correct pages. Probe it in a real viewport:

```js
// per <img> with srcset, at 390 / 768 / 1280
const r = img.getBoundingClientRect();
({ declared: img.sizes, renderedCss: Math.round(r.width),
   chosen: img.currentSrc, intrinsic: img.naturalWidth,
   wasteRatio: +(img.naturalWidth / (r.width * devicePixelRatio)).toFixed(2) })
```
Flag `wasteRatio > 1.5`. Fix by correcting `sizes` to the true box **first**, then adding
candidates to match — correcting the ladder alone leaves `sizes` still lying.

### 2y. `line-length-out-of-band` — *does the text actually fit*

Added 2026-07-26 for the breeder's "text height/width on mobile, desktop and tablet" ask,
which had **never been measured at any breakpoint**. Body measure must land in 45–75ch.

> **Do not approximate `ch` as `0.5em`.** The first cut of this probe did, and it
> over-reported by ~20% for Source Sans 3, whose "0" advance is nearer `0.6em`. On
> 2026-07-26 that produced a false alarm: it reported the body copy at 84ch and had
> a fix underway to "cap the measure across the cluster" — when `.hgar p{max-width:70ch}`
> was already there and correct, and the only genuinely over-wide text on the whole
> cluster was the FAQ answers. **Measure a real `ch` by rendering "0" in the element's
> own computed font**, as below.

```js
(() => {
  const cache = new Map();
  const realCh = (el) => {                       // width of "0" in THIS element's font
    const cs = getComputedStyle(el);
    const key = cs.fontSize+'|'+cs.fontFamily+'|'+cs.fontWeight;
    if (cache.has(key)) return cache.get(key);
    const s = document.createElement('span');
    s.textContent = '0'.repeat(100);             // x100 so rounding cannot skew it
    s.style.cssText = `position:absolute;visibility:hidden;white-space:pre;font:${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize}/${cs.lineHeight} ${cs.fontFamily};letter-spacing:${cs.letterSpacing};`;
    document.body.appendChild(s);
    const w = s.getBoundingClientRect().width / 100; s.remove();
    cache.set(key, w); return w;
  };
  document.querySelectorAll('details').forEach(d => d.open = true);  // FAQ answers have 0 width while closed
  return [...document.querySelectorAll('main p')]
    .filter(p => p.textContent.trim().length > 60 && p.getBoundingClientRect().width > 0)
    .map(p => ({ ch: Math.round(p.getBoundingClientRect().width / realCh(p)),
                 cls: (p.className || p.parentElement.className || '').toString().split(' ')[0],
                 text: p.textContent.trim().slice(0, 40) }))
    .filter(x => x.ch > 75);                     // see the 45ch note below
})()
```
Run at **360 / 768 / 1280**. Tablet is the breakpoint most likely to fail — these pages
were built mobile-first then verified on desktop, so 768 was never the design target.

**The 45ch floor does not apply at 360px.** A 360px viewport minus padding leaves ~328px;
at 16px body text that is ~41ch, so *every* paragraph reads as "too narrow" and the
result is noise. Filter on `> 75` at mobile and use the full band at 768 and up. Narrow
measures inside cards (blurbs, form asides) are also fine — a 26ch card blurb is not a
defect. **Over-wide is the failure mode worth chasing; under-wide usually is not.**

The real defect this catches looks like `max-width:none` on a paragraph inside a
full-width container. Uncapping inside an *already narrow* box (`.ship-c p`, `.quote-c p`)
is correct and measures in band — verify before "fixing" it.

Build, open the page in the preview browser, then run each probe. These are the
checks that caught the two worst bugs of 2026-07-23.

### 2a. Horizontal overflow at 375px — *text cut off at the screen edge*
A `width:100vw` full-bleed child inflates the `1fr` grid track that **contains**
it (a `1fr` track sizes to min-content = the viewport), so the text column grows
past the container padding and body copy runs off-screen. Which grid is at fault
is a runtime property — no static rule can find it without drowning in false
positives.

```js
(()=>{const bad=[...document.querySelectorAll('main *')]
  .filter(e=>e.getBoundingClientRect().right>innerWidth+1)
  .slice(0,8).map(e=>e.tagName+'.'+(e.className||'').toString().slice(0,34));
 return JSON.stringify({scrollW:document.documentElement.scrollWidth,vw:innerWidth,offenders:bad})})()
```
`scrollW` must equal `vw` and `offenders` must be empty (full-bleed images
legitimately reach exactly `vw`).

**Fix:** `grid-template-columns:minmax(0,1fr)` + `min-width:0` on the content column.

> Note: `overflow-x:clip` on the page root **hides** this — `scrollWidth` still
> reads 375 while text is being clipped. Always check element right-edges too.

### 2b. Full-page contrast sweep
```js
(()=>{const lum=c=>{const[r,g,b]=c.map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return 0.2126*r+0.7152*g+0.0722*b};
const parse=s=>s.match(/[\d.]+/g).map(Number).slice(0,3);
const bgOf=e=>{let n=e;while(n){const b=getComputedStyle(n).backgroundColor;if(b&&!/rgba\(0, 0, 0, 0\)|transparent/.test(b))return parse(b);n=n.parentElement}return[255,255,255]};
const ratio=(a,b)=>{const l1=lum(a),l2=lum(b);return +(((Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05)).toFixed(2))};
const fails=[];document.querySelectorAll('main *').forEach(e=>{
 if(e.closest('video'))return;                      // <video> fallback never renders
 if(![...e.childNodes].some(c=>c.nodeType===3&&c.textContent.trim().length>1))return;
 const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0)return;
 const size=parseFloat(cs.fontSize),bold=parseInt(cs.fontWeight)>=700;
 const need=(size>=24||(size>=18.66&&bold))?3:4.5;
 const r=ratio(parse(cs.color),bgOf(e));
 if(r<need)fails.push({el:e.tagName+'.'+(e.className||'').toString().slice(0,30),txt:e.textContent.trim().slice(0,30),ratio:r,need})});
 return JSON.stringify({failures:fails.length,fails:fails.slice(0,10)},null,1)})()
```
Target **0 failures**. Skip `<video>` fallback text — it is never rendered.

### 2c. Component sizing sanity
```js
(()=>{const r=e=>Math.round(e.getBoundingClientRect().height),w=e=>Math.round(e.getBoundingClientRect().width);
 const dial=document.querySelector('.dial-card');
 return JSON.stringify({vw:innerWidth,
  hero:r(document.querySelector('header.hero, .hero')),      // target 350-400 desktop
  h1:getComputedStyle(document.querySelector('h1')).fontSize, // must match the clamp
  dialH:dial&&r(dial), dialScrolls:dial&&dial.scrollHeight>dial.clientHeight,
  cardH:[...document.querySelectorAll('.bcard')].map(r),      // must be uniform
  btnW:[...document.querySelectorAll('.bfull')].map(w),       // must hug, not stretch
  btnLines:[...document.querySelectorAll('.bfull')].map(b=>Math.round(r(b)/20))})})() // 1 line each
```

**Targets:** hero 350–400px desktop · `h1` honours its clamp · dial fits without
inner scroll at 900px height · card heights uniform (±2px) · card CTAs hug their
label and never wrap.

---

## 3. Fix order (dependencies matter)

1. **`css-math-spacing` first.** Until the clamps are valid, every sizing
   measurement you take is measuring the fallback, and every "make it smaller"
   edit is a no-op. This wasted a full round-trip on 2026-07-23.
2. Layout mechanism next (absolute → grid), then sizing.
3. Overflow (§2a) before any visual judgement — a clipped page misleads every
   other check.
4. Contrast and link affordances.
5. Image delivery last (it does not affect layout).

---

## 4. Standing component rules confirmed by the breeder

- **Puppy card CTA:** `Reserve <name> →`, `white-space:nowrap`, `align-self:start`
  on desktop (hug) / `stretch` on mobile, `margin-top:auto` so every card's button
  shares a baseline. Never a stretched 200px pill with empty space.
- **Card badge:** bottom-left over a `linear-gradient` scrim — pinned top-left it
  lands on the puppy's head.
- **Name/price row:** `grid-template-columns:minmax(0,1fr) auto` with
  `white-space:nowrap` on the price, so a wrapping name never shoves the price.
- **Seam divider:** framed, not floating — two brass rules flanking a ~34px
  wordmark, plus a `--color-cta` `h2::before` tick so sections visibly separate.
- **Hero trust chips:** 2×2 grid on desktop, **1 column** on mobile. `nowrap`
  chips in 2 mobile columns overflow a 343px content box and drag the whole hero
  column wide.

---

## 5. Small defects that reached production anyway

Each of these shipped live and was reported by the breeder, not by a gate.

- **`caption` must join the mobile `display:block` list.** Left as
  `display:table-caption` under a `display:block` table, the browser wraps it in an
  anonymous table box that shrink-wraps to ~70px and stacks the title one word per
  line. This — not font-size — was the true cause of "the ledger title is too thick."
- **`max-width:none` is conditional, not wrong.** Correct while a card is a narrow
  2-up column; a bug the moment that grid collapses to `1fr`. `.ship-c p` and
  `.quote-c p` measured 90ch at 768. **Check every uncapped paragraph at the
  breakpoint where its container goes full width.**
- **A long card label breaks the button baseline.** A two-name card label
  wrapped to two lines while five siblings stayed on one. Shorten the label; never
  add `nowrap` to a label that cannot fit.
- **Every printed figure reads from the data files.** A plan that hand-drafts a price
  will disagree with `data/price-matrix.json` and `data/settings.json` sooner or later.
  Render through a helper, never a typed literal — a literal is a future contradiction.
- **Orphaned assets are a real category.** Six OG photos were committed and never
  referenced by any markup, and `heroPreload` pointed at one of them — 94 KB
  preloaded for an image the page never rendered, which was also not the LCP element.
  Diff `public/` against the page before assuming images are missing.
- **Seam parity** (the source repo's seam script was not ported — source repo only;
  the render harness owns this here). Never
  `grep -c '<section class="sec"'` — only 2 of the 8 source pages used that class,
  so the previously published command compared seams against **zero sections**. And
  never a `\bseam\b` regex: `-` is a word boundary, so `class="seam-wrap"` makes
  every seam count twice (read 34 for 17 real). Fixed 2026-07-29.
- **Sitemap regeneration on a no-URL-change edit is churn** — the generator stamps
  today's date on every URL. Run it for the phantom-URL check, then revert if the
  URL set is unchanged.

## 6. Handoff

Clean scan + clean runtime probes → `.claude/skills/bsuk-final-page-pass/SKILL.md` → deploy.
Anything this skill could not fix in code (e.g. an edge-injected `/70de/` bundle with unused JS and a missing source map — a
dashboard toggle at whichever host is chosen; hosting is NOT FETCHED until project 6) is reported to the breeder and recorded in
`data/quality/rework-ledger.json`, never silently dropped.
