// src/components/kit/_registry.ts — the one place the canvas route learns what a kit
// component is and how to demo it. The route renders `REGISTRY` generically; it has no
// per-component branches, so Tasks 6-16 add a component by adding an entry here.
// Task 19 (prune) deletes this file with the rest of the variant machinery.
//
// KIT CONVENTIONS — every component in this folder follows all nine.
//  1. No second `<main>`: BaseLayout already renders one, so a kit component and the canvas
//     route use `<div>`/`<section>`, never `<main>`.
//  2. Focus rings read `var(--kit-ring)`, never a fixed focus token: --color-focus is
//     steel-700, the same colour as the inverse surface, so a fixed ring vanishes on dark bands.
//  3. Colour comes from `currentColor` or a context variable with a default. A component that
//     can sit on both the bone surface and a dark band never hard-codes `--color-brand`.
//  4. `Props` extends `HTMLAttributes<'tag'>`, spreads `...rest` onto the root element, and
//     applies `class` with `class:list` — so no bare `class=""` or trailing space is emitted.
//  5. Multi-region components take content through named slots; `variant`, `size` and data
//     come through props.
//  6. Scoped `<style>` rules that a caller should be able to override live in
//     `@layer components { … }`, so a passed Tailwind utility wins over them.
//  7. Register the component here with demo fixtures; the canvas renders one copy per fixture.
//  8. Add a dist assertion for it in tests/py/test_design_components.py.
//  9. A primitive needed by a SECOND component (card shell, medal, rule) moves to
//     src/styles/kit.css rather than being copied into another scoped style block.
//
// Brass (--color-cta) is a FILL with --color-cta-ink text or an accent on a dark band. It is
// never the colour of small text on a light surface: it is 2.1:1 there.
import type { AstroComponentFactory } from 'astro/runtime/server/index.js';
import Button from './Button.astro';
import SectionDivider from './SectionDivider.astro';

export type ComponentId =
  | 'site-header' | 'hero' | 'buttons' | 'puppy-card' | 'trust-strip' | 'counter-strip'
  | 'info-card' | 'testimonial' | 'faq' | 'contact-form' | 'page-nav' | 'footer'
  | 'section-divider';

export interface KitEntry {
  C: AstroComponentFactory;
  /** One rendering per fixture, inside one variant section. Omitted means a single bare copy. */
  demo?: Record<string, unknown>[];
  /** Extra chrome the canvas wraps the demo in, for components that need a context to be judged. */
  wrap?: 'sticky' | 'inverse';
}

/** The row in data/design/components.json, typed so a typo in an id fails the build. */
export interface ComponentRow {
  id: ComponentId;
  file: string;
  title: string;
  board_width: 640 | 1280;
}

export const REGISTRY: Partial<Record<ComponentId, KitEntry>> = {
  buttons: {
    C: Button,
    demo: [
      { label: 'Meet the puppies', href: '/available-puppies/' },
      { label: 'Ask about Roman', type: 'submit' },
    ],
  },
  'section-divider': { C: SectionDivider },
};
