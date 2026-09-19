// src/lib/boardStyles.ts — the three arrangements a board offers per section shape.
//
// ONE map, read twice: `src/pages/board-preview/[slug].astro` renders S1/S2/S3 from it so
// the breeder can see the three side by side, and the rebuilt page (P5) reads the SAME
// entry for whichever id the approval picked. That is what makes a pick reproducible —
// "S2" means a layout this file defines, not a screenshot somebody remembers.
//
// The three differ STRUCTURALLY, never by token (the project 3 distinctness rule): a
// different column count, a different media position, a band instead of a card, a grid
// instead of a stack. Two styles that differ only in colour are one style shown twice.
//
// The layout descriptor is deliberately small and CLOSED: every field is an enum the
// preview route switches on, so a style cannot smuggle in markup of its own and the page
// build can rely on the same seven axes being the whole of a style's meaning.

/** The section shapes a board may render. `standard` is the prose default and is kept
 *  under its old name because `schemas/board.schema.json` has always allowed it; the other
 *  nine are the kit-backed shapes project 4 added to that enum. */
export type Shape =
  | 'hero' | 'takeaways' | 'standard' | 'puppies' | 'reviews'
  | 'faq' | 'form' | 'stats' | 'trust' | 'divider';

export interface Layout {
  /** The bed the section sits on. `band` is full-bleed and inverse; `card` is the kit card
   *  shell; `plain` is the page surface. */
  frame: 'plain' | 'band' | 'card';
  /** Body column count at desktop. 1 is a single measure; 2 is a split. */
  columns: 1 | 2;
  /** Where the section's image goes, when it has one. */
  media: 'none' | 'left' | 'right' | 'top';
  /** How the section's repeated parts (tree stubs, cards, reviews, questions) are laid out. */
  list: 'stack' | 'grid-2' | 'grid-3' | 'rail';
  /** A secondary block beside the body. */
  aside: 'none' | 'infocard' | 'jump';
  /** Where the H2 sits relative to the body. */
  heading: 'above' | 'inline' | 'eyebrow';
  /** Mode passed to a kit component that takes one (Testimonial today). */
  mode?: 'single' | 'grid';
}

export interface StyleDef {
  id: 'S1' | 'S2' | 'S3';
  /** The one-line label the board prints over the preview. */
  name: string;
  layout: Layout;
}

/** The three ids every styled section offers, in order. `build_board_previews.validate_styles`
 *  refuses a record whose `styles` is anything else. */
export const STYLE_IDS: ReadonlyArray<StyleDef['id']> = ['S1', 'S2', 'S3'];

const def = (id: StyleDef['id'], name: string, layout: Layout): StyleDef => ({ id, name, layout });

export const STYLES: Record<Shape, [StyleDef, StyleDef, StyleDef]> = {
  // The page opener. Three genuinely different openers: text beside the photo, text over a
  // full-bleed band with the photo above it, and a compact card-framed opener.
  hero: [
    def('S1', 'Split — copy left, photo right', { frame: 'plain', columns: 2, media: 'right', list: 'stack', aside: 'none', heading: 'above' }),
    def('S2', 'Photo above, copy on a steel band', { frame: 'band', columns: 1, media: 'top', list: 'rail', aside: 'none', heading: 'eyebrow' }),
    def('S3', 'Card opener with a jump list', { frame: 'card', columns: 2, media: 'left', list: 'stack', aside: 'jump', heading: 'above' }),
  ],
  // Key takeaways. A stacked list of statements, a three-up grid, or one lead statement
  // with the rest as a rail beside it.
  takeaways: [
    def('S1', 'Stacked statement cards', { frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above' }),
    def('S2', 'Three-up grid on a band', { frame: 'band', columns: 1, media: 'none', list: 'grid-3', aside: 'none', heading: 'eyebrow' }),
    def('S3', 'Lead card with a rail of the rest', { frame: 'plain', columns: 2, media: 'none', list: 'rail', aside: 'infocard', heading: 'inline' }),
  ],
  // The prose workhorse (spec's three worked examples).
  standard: [
    def('S1', 'Prose with the image right', { frame: 'plain', columns: 1, media: 'right', list: 'stack', aside: 'none', heading: 'above' }),
    def('S2', 'Image full width above two-column prose', { frame: 'plain', columns: 2, media: 'top', list: 'stack', aside: 'none', heading: 'above' }),
    def('S3', 'Band with an InfoCard aside', { frame: 'band', columns: 2, media: 'none', list: 'stack', aside: 'infocard', heading: 'eyebrow' }),
  ],
  puppies: [
    def('S1', 'Three-up card grid', { frame: 'plain', columns: 1, media: 'none', list: 'grid-3', aside: 'none', heading: 'above' }),
    def('S2', 'Two-up grid with an intro column', { frame: 'plain', columns: 2, media: 'none', list: 'grid-2', aside: 'none', heading: 'inline' }),
    def('S3', 'Scrolling rail on a band', { frame: 'band', columns: 1, media: 'none', list: 'rail', aside: 'none', heading: 'eyebrow' }),
  ],
  reviews: [
    def('S1', 'One review given room', { frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above', mode: 'single' }),
    def('S2', 'Review grid on a band', { frame: 'band', columns: 1, media: 'none', list: 'grid-3', aside: 'none', heading: 'eyebrow', mode: 'grid' }),
    def('S3', 'Heading beside the review grid', { frame: 'plain', columns: 2, media: 'none', list: 'grid-2', aside: 'none', heading: 'inline', mode: 'grid' }),
  ],
  faq: [
    def('S1', 'Full-width accordion', { frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above' }),
    def('S2', 'Heading and intro beside the accordion', { frame: 'plain', columns: 2, media: 'none', list: 'stack', aside: 'none', heading: 'inline' }),
    def('S3', 'Accordion in a card with a jump list', { frame: 'card', columns: 2, media: 'none', list: 'stack', aside: 'jump', heading: 'above' }),
  ],
  form: [
    def('S1', 'Form under the heading', { frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above' }),
    def('S2', 'Form beside the reasons to write', { frame: 'plain', columns: 2, media: 'none', list: 'stack', aside: 'infocard', heading: 'above' }),
    def('S3', 'Form in a card on a band', { frame: 'band', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'eyebrow' }),
  ],
  stats: [
    def('S1', 'Counter strip full width', { frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above' }),
    def('S2', 'Counter strip on a band, heading above', { frame: 'band', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'eyebrow' }),
    def('S3', 'Heading beside the counters', { frame: 'plain', columns: 2, media: 'none', list: 'stack', aside: 'none', heading: 'inline' }),
  ],
  trust: [
    def('S1', 'Trust strip alone', { frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above' }),
    def('S2', 'Trust strip in a card', { frame: 'card', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'eyebrow' }),
    def('S3', 'Trust strip beside the heading', { frame: 'plain', columns: 2, media: 'none', list: 'stack', aside: 'none', heading: 'inline' }),
  ],
  divider: [
    def('S1', 'Light seam', { frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above' }),
    def('S2', 'Inverse seam on a band', { frame: 'band', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'eyebrow' }),
    def('S3', 'Seam with the section label beside it', { frame: 'plain', columns: 2, media: 'none', list: 'stack', aside: 'none', heading: 'inline' }),
  ],
};

/** The three styles a shape offers, or the `standard` trio for a shape this map has not
 *  learned yet — a board is never rendered with an empty option set. */
export function stylesFor(shape: string): [StyleDef, StyleDef, StyleDef] {
  return STYLES[shape as Shape] ?? STYLES.standard;
}

/** The one style a pick names. Unknown id → S1, so a stale pick renders rather than throws. */
export function styleById(shape: string, id: string): StyleDef {
  return stylesFor(shape).find((s) => s.id === id) ?? stylesFor(shape)[0];
}
