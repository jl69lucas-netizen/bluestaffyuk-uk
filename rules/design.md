# Design system — the ten non-negotiable visual rules

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4). **The rule text is verbatim.**
Rule 10 was added on 2026-09-18 from the user's review of the design canvas (spec §11
amendment 3c) and is the one rule here that was not carried over from `CLAUDE.md`.

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.

---
id: design-system-nine
enforced: test
family: CSS
---

**Non-Negotiable Design Rules — enforced on every page build and rebuild:**
1. **Colors:** Every colour is a token in `src/styles/tokens.css`; no hex anywhere else in `src/`. Roles: `--color-brand` (header, headings, bands), `--color-cta` with `--color-cta-ink` (all CTAs/buttons), `--color-surface` (page surface), `--color-surface-inverse` (dark bands), `--color-link`. AA contrast for every text/background pair is asserted by `tests/py/test_design_tokens.py` from `data/design/contrast.json`; add the pair before you use it.
2. **Type:** `--font-display` (**Fraunces**) for ALL headlines H1–H6, `--font-body` (**Source Sans 3**) for ALL body, labels and buttons, applied globally in `src/styles/global.css`. Never hard-code `font-family` on an element; use the tokens.
3. **Buttons:** Primary CTA = `--color-cta` pill, `border-radius: var(--btn-radius)`. This is the brand signature. Form submit buttons only use `border-radius: var(--btn-form-radius)`.
4. **Cards:** `--card-radius`, `--card-border`, `--shadow-card`, white surface. Info cards use `--color-brand` header band.
5. **Shadows:** Always `--shadow-card` / `--shadow-lift` (steel-tinted `rgba(20,32,43,…)`). Never neutral grey, never a hand-written shadow.
6. **Motion:** Max 0.2s transitions. No bounce, no parallax, no auto-playing video.
7. **Icons = line-icon SVGs, NOT emoji** (site-wide sweep 2026-06-03, commit `9ff570f`; the icon system is specified in project 3's design system). Use inline Feather-style SVGs (`width/height="1em"`, `stroke="currentColor"`) — map + transform in `scripts/emoji_to_icons.py` (not ported — source repo only). The former canonical emoji set (📞 ✉️ 📍 🕐 ✈️ 🚗 ✅) is now line icons (✅ → `--color-ok` check-circle). KEEP only the text glyphs ✔ ✗ ★ (list/rating markers). One per element. Banned: 🎉 🔥 🚀 and any colorful pictograph emoji. **Render rule:** a data-array icon rendered via `{x.icon}` must use `set:html`, then verify `grep -rl "&lt;svg" dist/` is empty. **NEVER put an `<svg>` inside CSS `content:`** — `content` only renders plain text, so `::before{content:'<svg…>'}` dumps the raw markup (or drops it) AND collapses badge spacing when the separator lived in that pseudo-element. Put the inline `<svg>` in the markup instead. Detect: `grep -rn "content: '<svg\|content:\"<svg" src/`. (Fixed on kc-registered / home-raised / dna-tested trust bars, 2026-06-05.)
   - **Dog icon — NEVER use a generic 🐕 / 🐶 emoji** (it is not a Staffordshire Bull Terrier). Use the line-icon SVG set; when a filled mark is wanted, use the brand mark (`src/components/kit/Mark.astro`). There is no custom dog-emoji image set — the source repo's `/emoji/` images were never ported, and `tests/py/test_doc_drift.py` fails a pack that names a public file that is not there.
     - Plain text / email / JS string contexts: use `[BSUK]` as a text marker — HTML img not possible in strings
8. **Anti-copy:** NEVER add `user-select: none` CSS or JS.
9. **Infographic widths:** `760px` wrapper for species guides / blogs / care pages; `1100px` wrapper for homepage / location pages / hero sections. Height always `400px` fixed on desktop, `auto` on mobile. Never use `900px` or `max-w-4xl` — those are legacy values. Widths are set in `src/styles/global.css`; project 3's design system owns the rule.

---
id: layout-hero-counter-separation
enforced: test
family: LAYOUT
---

- **Hero and counter strip must be visually separated (ALWAYS — breeder, 2026-08-07)** — A counter/stat strip placed directly under a hero on one continuous background reads as hero furniture, and the figures stop registering as claims. Every page carrying both MUST put a visible boundary between them: at minimum a **background-tone shift AND a 1px rule**; at most a `.bsuk-seam` divider. Never zero separation, and never whitespace alone. On the puppy cluster the marker is a 3px `--seam-gradient` bar on `.counter-wrap::before` plus a `--counter-bed` bed. Enforced by `tests/render/checks/layout.ts::layout-hero-counter-separation`, with both fixture halves — a page with a tone shift but no rule still fails. Blocking on project 5 pages (targets.json `promotions`, scope `new-pages`).

---
id: layout-h3-image-first
enforced: test
family: LAYOUT
---

- **Under an H3, the image comes before the prose (ALWAYS — breeder, 2026-08-07)** — In the puppy cluster a sectional image sits immediately after its `</h3>` and before that block's first `<p>`, so the reader gets the subject before the argument. **H2 blocks keep lead-paragraph-first** — this rule is H3-scoped, deliberately, and a check that flags H2s is over-broad. Only a sectional image counts — `.sec-img` (the kit specimen) or `.bl-img` (`src/components/BodyImage.astro`, the body photograph every rebuilt page renders); seam emblems and icons are decorative and must never register as "the image". An H3 that owns no image is not a violation and must not be counted as examined. Enforced by `tests/render/checks/layout.ts::layout-h3-image-first` — blocking on project 5 pages (targets.json `promotions`, scope `new-pages`), advisory on the twelve pages built before them.

---
id: layout-hero-height-and-image-first
enforced: test
family: LAYOUT
---

10. **Hero image first in the DOM; hero section height ≤ 450px and ≥ 390px on desktop (≥1024px), auto on mobile.** The image element precedes the copy in source order and CSS `order` puts it back where the layout wants it, so a reader on a narrow screen or with stylesheets off meets the subject before the argument — the same reasoning as `layout-h3-image-first`, applied to the band that sets the page's first impression. The band is clamped, not merely advised — but **the copy must FIT the clamp, and the photo is what the clamp crops.** Nothing on the copy path may hide its overflow: the section carries no `overflow: hidden`, and the heading, lede and CTA row are SIZED to fit instead (heading at `--text-3xl`, tight block margins), so a hero that no longer fits fails loudly rather than quietly losing its call to action. **The lede is the one clamped element, so it is held to two lines AND MEASURED.** A clamp hides its own overflow: a third line is never pushed past the ceiling where the section and `.inner` figures would catch it, it is simply not painted. `lede_overflow` (`scrollHeight - clientHeight` on `.lede`) is therefore recorded beside them and must be zero — copy that needs three lines is shortened, never quietly truncated by the clamp. At ≥1024px the ceiling (`max-height: 450px`) sits on the section and the floor (`min-height: 390px`) on `.inner`; only the photo column takes `overflow: clip`, with `object-fit: cover` and a `max-height` equal to the content box the ceiling leaves, so the picture's own aspect ratio can never set the height. Below 1024px the height is `auto`, because a phone hero that clipped its own call to action would be worse than a tall one. Enforced by `tests/py/test_design_components.py::test_built_hero_puts_the_image_before_the_heading` and `::test_measured_hero_fits_its_clamp_without_clipping_anything`, which reads the overflow, lede-overflow and CTA-edge figures `scripts/measure_canvas_heights.mjs` records at 1024, 1100 and 1280 — a board height alone cannot tell fitting from clipping. **On a phone the photo also PAINTS first** (the user's ruling, 2026-09-27: "ALL HEROES images come first on MOBILE"): below 900px, where every arrangement is one column, `.pic` takes `order: 1` and `.copy` `order: 2`, so the reader sees the subject before the heading. Enforced by `tests/render/checks/layout.ts::layout-hero-image-first-mobile` (blocking on every page).
