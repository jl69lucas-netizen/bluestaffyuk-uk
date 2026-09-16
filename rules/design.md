# Design system — the nine non-negotiable visual rules

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4). **The rule text is verbatim.**

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.

---
id: design-system-nine
enforced: untested
family: CSS
---

**Non-Negotiable Design Rules — enforced on every page build and rebuild:**
1. **Colors:** Three anchors only — Forest Green `#2D6A4F` (nav/headers), Clay `#e8604c` (all CTAs/buttons), Cream `#faf7f4` (page surface). `--gold` MUST always equal `--clay`. (Direction D does NOT change the palette.)
   - **WCAG AA contrast variants (2026-06-03 — do NOT revert):** `#e8604c` only clears AA as *large* text/fill (3.38:1 white). For accessibility, solid clay **button fills** render `--color-clay-ink #c8472f` (white text 4.78:1, via a global `.bg-clay` rule in `src/styles/global.css`), and **clay as small readable text** (inline links, eyebrows, form prices) renders `#b04228` (4.5:1+ on light). Brand identity token `--clay #e8604c` is unchanged; it still applies to tints, large display, and clay text **on dark/green** (hero "Trust" accent, dark testimonial chips — kept bright via `.home-d` exceptions). The palette and its AA variants are locked in `src/styles/global.css`; the full design system arrives in project 3.
2. **Type:** The **Direction D** theme — **Newsreader** serif for ALL headlines (H1–H6), **IBM Plex Sans** for ALL body/labels/buttons, applied globally via `body.theme-d` — **arrives in project 3**; Foundation ships the token-level fallback in `src/styles/global.css`. Keep using the `font-lora`/`font-sora` utility classes in markup: the project-3 theme restyles them, and until it lands the fallback stack is what renders. Do not hard-code `font-family` on elements to fight the theme.
3. **Buttons:** Primary CTA = clay pill, `border-radius: 50px`. This is the brand signature. Form submit buttons only use `border-radius: 12px`.
4. **Cards:** 20px radius, 1px `--border`, warm shadow, white surface. Info cards use green header band.
5. **Shadows:** Always warm-tinted `rgba(60,30,10,…)`. Never neutral grey.
6. **Motion:** Max 0.2s transitions. No bounce, no parallax, no auto-playing video.
7. **Icons = line-icon SVGs, NOT emoji** (site-wide sweep 2026-06-03, commit `9ff570f`; the icon system is specified in project 3's design system). Use inline Feather-style SVGs (`width/height="1em"`, `stroke="currentColor"`) — map + transform in `scripts/emoji_to_icons.py` (not ported — source repo only). The former canonical emoji set (📞 ✉️ 📍 🕐 ✈️ 🚗 ✅) is now line icons (✅ → green `#2D6A4F` check-circle). KEEP only the text glyphs ✔ ✗ ★ (list/rating markers). One per element. Banned: 🎉 🔥 🚀 and any colorful pictograph emoji. **Render rule:** a data-array icon rendered via `{x.icon}` must use `set:html`, then verify `grep -rl "&lt;svg" dist/` is empty. **NEVER put an `<svg>` inside CSS `content:`** — `content` only renders plain text, so `::before{content:'<svg…>'}` dumps the raw markup (or drops it) AND collapses badge spacing when the separator lived in that pseudo-element. Put the inline `<svg>` in the markup instead. Detect: `grep -rn "content: '<svg\|content:\"<svg" src/`. (Fixed on kc-registered / home-raised / dna-tested trust bars, 2026-06-05.)
   - **Dog icon — NEVER use a generic 🐕 / 🐶 emoji** (it is not a Staffordshire Bull Terrier). Use the custom line-icon SVG set, or the custom images when a filled mark is wanted:
     - Blue Staffy: `<img src="/emoji/bsuk-blue.png" alt="Blue Staffy" class="bsuk-emoji" loading="lazy">`
     - Brindle Staffy: `<img src="/emoji/bsuk-brindle.png" alt="Brindle Staffy" class="bsuk-emoji" loading="lazy">`
     - Large decorative (100px+): `<img src="/emoji/bsuk-blue.png" style="width:Xpx;height:Xpx;object-fit:contain;" alt="" loading="lazy">` — match original font-size value
     - Plain text / email / JS string contexts: use `[BSUK]` as a text marker — HTML img not possible in strings
8. **Anti-copy:** NEVER add `user-select: none` CSS or JS.
9. **Infographic widths:** `760px` wrapper for species guides / blogs / care pages; `1100px` wrapper for homepage / location pages / hero sections. Height always `400px` fixed on desktop, `auto` on mobile. Never use `900px` or `max-w-4xl` — those are legacy values. Widths are set in `src/styles/global.css`; project 3's design system owns the rule.

---
id: layout-hero-counter-separation
enforced: test
family: LAYOUT
---

- **Hero and counter strip must be visually separated (ALWAYS — breeder, 2026-08-07)** — A counter/stat strip placed directly under a hero on one continuous background reads as hero furniture, and the figures stop registering as claims. Every page carrying both MUST put a visible boundary between them: at minimum a **background-tone shift AND a 1px rule**; at most a `.bsuk-seam` divider. Never zero separation, and never whitespace alone. On the puppy cluster the marker is a 3px `--bp-green → --bp-clay` gradient bar on `.counter-wrap::before` plus a `#f6efe8` bed. Enforced by `tests/render/checks/layout.ts::layout-hero-counter-separation`, with both fixture halves — a page with a tone shift but no rule still fails.

---
id: layout-h3-image-first
enforced: test
family: LAYOUT
---

- **Under an H3, the image comes before the prose (ALWAYS — breeder, 2026-08-07)** — In the puppy cluster a sectional image sits immediately after its `</h3>` and before that block's first `<p>`, so the reader gets the subject before the argument. **H2 blocks keep lead-paragraph-first** — this rule is H3-scoped, deliberately, and a check that flags H2s is over-broad. Only `.sec-img` counts; seam emblems and icons are decorative and must never register as "the image". An H3 that owns no image is not a violation and must not be counted as examined. Enforced by `tests/render/checks/layout.ts::layout-h3-image-first`.
