# Plan 2 Notes (London Components)

A running list of what Plan 2 must honour when it builds the picked variants into the kit.
Added to by each Plan 1 task review; read before writing Plan 2.

## Navigation (Task 6: contents list, desktop dial, jump links)

- **The picked sheet is built on the kit's `SectionSheet.astro` pattern**, not on the canvas's
  `:target` mechanism: a `<dialog>` opened with `showModal()`, so it gets Escape to close, a
  focus trap, an inert background, `aria-expanded` on the opener, and no history entry per open
  and close. The canvas fragment is the visual spec only.
- **Current-section marking uses the kit's scroll-spy scripts** (the IntersectionObserver in
  `PageDial.astro` and `SectionStrip.astro`, with `aria-current="location"`), not `:target` and
  not scroll-driven animations. The canvas uses CSS only because a mockup frame carries no script.
- **Dial A (page map) block heights come from the real section lengths** measured on the built
  page (or from the section word counts at build time), never from the stand-in weights.
- **Fragments are the visual spec.** Build each picked component from a `sections` array (id,
  short label, long label, icon), never by pasting the fragment's repeated markup; move every
  inline `style=` value (stub heights, the dial's `--i` stop angles, nowrap spans) into classes
  or computed props.
- **Anything marked `data-canvas-only` is never ported**: the stand-in sections (`.stub`,
  `.stubs`), the "which one navigates at this width" notes, and the fixed zero-size close anchor.

## From the Task 6 re-review

- The `!important` animation longhands in the nav fragments exist only to defeat the canvas frame's
  reduced-motion reset (`scripts/build_component_canvas.py`). Never port them: the kit marks the
  current section with its scroll-spy script.
- Contents a and c duplicate rows 6–10 (a desktop copy and a phone `<details>` copy). Build one
  list and hide rows 6–10 on phones behind the disclosure instead.
