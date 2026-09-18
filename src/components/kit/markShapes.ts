// src/components/kit/markShapes.ts — the mark's geometry, in ONE place.
//
// The BlueStaffyUK mark is drawn twice on a page in two different ways: once as a
// `<symbol>` pair in the document's sprite (MarkSprite.astro, mounted by BaseLayout), which
// every `<Mark />` then references with `<use>`; and once in full when a caller asks for a
// `standalone` copy — the lockup files of Task 20 have to be self-contained SVG documents
// with no sprite to point at. Two copies of a 12-path Staffordshire Bull Terrier head is
// two drawings that drift, so the paths live here and both callers render this string.
//
// COLOUR. Every fill and stroke is a token, never a hex (rule 1). SVG presentation
// attributes accept `var()` because this SVG is inline in the HTML document, so it resolves
// against the page's own custom properties rather than an isolated image document.
//
// The skull is `--color-brand-tint` (steel-300) and the ears `--color-brand-mid`, which is
// exactly the reference lockup's two-tone head. Both are fills and never text, so neither
// carries a pair in data/design/contrast.json.

export const MARK_VIEWBOX = '0 0 100 100';

/** The roundel, the brass ring and the head. `badge` fills the roundel; `outline` is the
 *  stroke that separates the skull from it — swapped for the inverse mark, which is what a
 *  dark band needs (a bone roundel with brand-steel outlines). */
export const markBody = (badge: string, outline: string) => `
  <circle cx="50" cy="50" r="47" fill="${badge}" />
  <circle cx="50" cy="50" r="43" fill="none" stroke="var(--color-cta)" stroke-width="2.5" />
  <g transform="translate(50 54)" stroke-linejoin="round">
    <path d="M-30 -14 C-30 -34 -14 -42 0 -42 C14 -42 30 -34 30 -14 L30 4 C30 22 16 34 0 34 C-16 34 -30 22 -30 4 Z"
      fill="var(--color-brand-tint)" stroke="${outline}" stroke-width="2.5" />
    <path d="M-30 -14 C-40 -20 -44 -30 -38 -36 C-32 -40 -24 -36 -20 -30"
      fill="var(--color-brand-mid)" stroke="${outline}" stroke-width="2.5" />
    <path d="M30 -14 C40 -20 44 -30 38 -36 C32 -40 24 -36 20 -30"
      fill="var(--color-brand-mid)" stroke="${outline}" stroke-width="2.5" />
    <path d="M-16 6 C-16 -2 -8 -6 0 -6 C8 -6 16 -2 16 6 L14 22 C10 30 -10 30 -14 22 Z"
      fill="var(--color-surface)" />
    <ellipse cx="-11" cy="-8" rx="4" ry="4.5" fill="var(--color-surface-deep)" />
    <ellipse cx="11" cy="-8" rx="4" ry="4.5" fill="var(--color-surface-deep)" />
    <ellipse cx="-9.5" cy="-9.5" rx="1.3" ry="1.3" fill="var(--color-surface-raised)" />
    <ellipse cx="12.5" cy="-9.5" rx="1.3" ry="1.3" fill="var(--color-surface-raised)" />
    <path d="M-7 10 C-7 6 7 6 7 10 C7 14 -7 14 -7 10 Z" fill="var(--color-surface-deep)" />
    <path d="M0 14 L0 19 M-9 22 C-4 27 4 27 9 22" fill="none" stroke="var(--color-surface-deep)"
      stroke-width="2.2" stroke-linecap="round" />
    <path d="M-4 24 C-2 30 2 30 4 24 Z" fill="var(--color-cta)" />
  </g>`;

/** The two sprite symbols, by surface. */
export const MARK_SPRITE_ID = 'bsuk-mark';
export const MARK_SPRITE_ID_INVERSE = 'bsuk-mark-inverse';
export const spriteHref = (inverse: boolean) =>
  `#${inverse ? MARK_SPRITE_ID_INVERSE : MARK_SPRITE_ID}`;
