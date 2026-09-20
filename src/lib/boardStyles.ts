// src/lib/boardStyles.ts — the three arrangements a board offers per section shape, and
// the ONE function that turns one of them into class names.
//
// READ TWICE, BY DESIGN. `src/pages/board-preview/[slug].astro` renders S1/S2/S3 so the
// breeder can see the three side by side; a page rebuilt from an approved record (the page
// procedure's P5) calls the same `boxClass()` for whichever id the approval picked. The CSS
// those classes resolve to lives in `src/styles/board-styles.css`, which `global.css`
// imports, so it is on every page — the preview and the real page are the same layout, not
// two implementations of one description.
//
// The three differ STRUCTURALLY, never by token (the project 3 distinctness rule): a
// different column count, a different media position, a band instead of a card, a grid
// instead of a stack.
//
// AXES A RENDERER IGNORES ARE NOT SET. A `list: 'rail'` on a shape whose renderer is the
// kit's Hero would describe a difference nobody can see, and three styles that all render
// the same are a pick with no question in it. `RENDERED_AXES` names, per shape, the axes
// that shape's renderer actually reads; `tests/py/test_board_previews.py` holds the three
// defs of every shape to differing on at least one of them, and holds the BUILT blocks of
// `/board-preview/_demo/` to differing too.

/** The section shapes a board may render. `standard` is the prose default and keeps its
 *  old name because `schemas/board.schema.json` has always allowed it; the other nine are
 *  the kit-backed shapes project 4 added to that enum. */
export type Shape =
  | 'hero' | 'takeaways' | 'standard' | 'puppies' | 'reviews'
  | 'faq' | 'form' | 'stats' | 'trust' | 'divider'
  | 'dial' | 'sheet' | 'strip' | 'table' | 'video';

export const SHAPES: readonly Shape[] = [
  'hero', 'takeaways', 'standard', 'puppies', 'reviews', 'faq', 'form', 'stats', 'trust', 'divider',
  'dial', 'sheet', 'strip', 'table', 'video',
];

/** Every axis a layout can state. All optional: a def sets only what its renderer reads,
 *  and `boxClass()` fills the rest with the neutral value. */
export interface Layout {
  /** The bed the section sits on: the page surface, the kit card shell, or a steel band. */
  frame?: 'plain' | 'band' | 'card';
  /** Body column count at desktop. */
  columns?: 1 | 2;
  /** Where the section's image sits. For `hero` this moves the kit Hero's own photo. */
  media?: 'none' | 'left' | 'right' | 'top';
  /** How the section's repeated parts (tree stubs, cards) are laid out. */
  list?: 'stack' | 'grid-2' | 'grid-3' | 'rail';
  /** A secondary block beside the body. */
  aside?: 'none' | 'infocard' | 'jump';
  /** Where the H2 sits relative to the body. */
  heading?: 'above' | 'inline' | 'eyebrow';
  /** Passed straight to a kit component that takes a mode (Testimonial). */
  mode?: 'single' | 'grid';
  /** PageDial only: whether the progress ring is drawn at all. */
  ring?: 'shown' | 'hidden';
  /** PageDial only: what each row of the section list carries beside its label. */
  marks?: 'number' | 'label';
  /** SectionSheet only: the control that opens the sections sheet. */
  launcher?: 'tab' | 'pill' | 'fab';
  /** SectionStrip only: how a chip on the sticky mobile rail is drawn. */
  chip?: 'outline' | 'filled' | 'text';
  /** DataTable only: how the table's rows and header are drawn. A CLASS axis, not a prop —
   *  `boxClass()` emits `bl-chrome-*` and board-styles.css paints it, so the arrangement the
   *  breeder approves on the board is the same rule the rebuilt page resolves. Stacking
   *  below 640px is NOT on this axis: all three stack, always (working rule 13). */
  chrome?: 'ruled' | 'zebra' | 'brass';
  /** VideoEmbed only: whether the player is in the document from the start, or injected on
   *  the first click. A PROP, not a class — the two arrangements are different MARKUP (a
   *  button and a thumbnail, or an iframe), which no stylesheet can turn into the other. */
  play?: 'facade' | 'iframe';
}

export type Axis = keyof Layout;

export interface StyleDef {
  id: 'S1' | 'S2' | 'S3';
  /** The one-line label the board prints over the preview. It says what the style
   *  RENDERS — an axis outside `RENDERED_AXES` may not be named in it. */
  name: string;
  layout: Layout;
}

/** The three ids every styled section offers, in order. `build_board_previews.validate_styles`
 *  refuses a record whose `styles` is anything else. */
export const STYLE_IDS: ReadonlyArray<StyleDef['id']> = ['S1', 'S2', 'S3'];

/** The neutral value of each CLASS axis: what `boxClass()` writes when a def leaves it
 *  unset. `mode`, `ring`, `marks`, `launcher` and `chip` are not here and are not classes:
 *  they are handed straight to a kit component as a prop (Testimonial's mode, PageDial's,
 *  SectionSheet's and SectionStrip's style), so there is no `bl-*` rule for the stylesheet
 *  to key on — `chip` was missing from the omit list until component 17 was added, which
 *  made this type ask for a neutral value no caller could ever have used.
 *  `chrome` IS here: DataTable's three arrangements are pure CSS over identical markup,
 *  which is exactly what a class axis is for. */
const NEUTRAL: Required<Omit<Layout, 'mode' | 'ring' | 'marks' | 'launcher' | 'chip' | 'play'>> = {
  frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above',
  chrome: 'ruled',
};

/** Per shape, the axes that shape's RENDERER reads. Anything else would be decoration. */
export const RENDERED_AXES: Record<Shape, readonly Axis[]> = {
  // The kit Hero owns its own copy, chips and CTA row; what a board can move is the bed it
  // sits on and which side its photo is on (board-styles.css reorders `.kit-hero`).
  hero: ['frame', 'media'],
  takeaways: ['frame', 'list', 'columns', 'aside', 'heading'],
  standard: ['frame', 'media', 'columns', 'aside', 'heading'],
  puppies: ['frame', 'list', 'columns', 'heading'],
  // Testimonial takes `mode`; the rest is the bed and where the heading sits.
  reviews: ['frame', 'mode', 'columns', 'heading'],
  faq: ['frame', 'columns', 'aside', 'heading'],
  form: ['frame', 'columns', 'aside', 'heading'],
  stats: ['frame', 'columns', 'heading'],
  trust: ['frame', 'columns', 'heading'],
  // SectionDivider takes `inverse`, and the band frame is what selects it.
  divider: ['frame', 'columns', 'heading'],
  // PageDial and SectionSheet are the only two shapes whose three styles are STRUCTURAL
  // variants of the component itself rather than of the bed it sits on — the dial's ring and
  // row content, the sheet's launcher. So each reads its own props and nothing about frames
  // or columns: a dial in a card and a dial on a band are the same dial.
  dial: ['ring', 'marks', 'list'],
  sheet: ['launcher'],
  // SectionStrip joins them: its three styles are how one chip is drawn, nothing about the
  // bed the rail sits on — the rail is always full-bleed under the header.
  strip: ['chip'],
  // DataTable (component 17). `chrome` is the question the board asks; `frame` and
  // `heading` are the ordinary bed and heading position every prose section has. `columns`
  // is deliberately absent: a table beside a narrow column is a table with a scrollbar.
  table: ['chrome', 'frame', 'heading'],
  // VideoEmbed (component 18). `frame` is the question the board asks — the bed the 16:9 box
  // sits on — and `play` is the second half of it, because the lightest arrangement is not a
  // bed at all but a thumbnail that fetches the player only when someone presses it.
  // `columns` is absent for the table's reason: a 16:9 box in a narrow column is a stamp.
  video: ['frame', 'play'],
};

const def = (id: StyleDef['id'], name: string, layout: Layout): StyleDef => ({ id, name, layout });

export const STYLES: Record<Shape, [StyleDef, StyleDef, StyleDef]> = {
  hero: [
    def('S1', 'Photo right of the copy', { media: 'right' }),
    def('S2', 'Photo above the copy, on a steel band', { frame: 'band', media: 'top' }),
    def('S3', 'Photo left of the copy, in a card', { frame: 'card', media: 'left' }),
  ],
  takeaways: [
    def('S1', 'Stacked statement cards', { list: 'stack' }),
    def('S2', 'Three-up grid on a band', { frame: 'band', list: 'grid-3', heading: 'eyebrow' }),
    def('S3', 'Rail of cards beside the heading', { list: 'rail', columns: 2, heading: 'inline' }),
  ],
  standard: [
    def('S1', 'Prose with the image right', { media: 'right' }),
    def('S2', 'Image full width above two-column prose', { media: 'top', columns: 2 }),
    def('S3', 'Band with an InfoCard aside', { frame: 'band', columns: 2, aside: 'infocard', heading: 'eyebrow' }),
  ],
  puppies: [
    def('S1', 'Three-up card grid', { list: 'grid-3' }),
    def('S2', 'Two-up grid beside the heading', { list: 'grid-2', columns: 2, heading: 'inline' }),
    def('S3', 'Scrolling rail on a band', { frame: 'band', list: 'rail', heading: 'eyebrow' }),
  ],
  reviews: [
    def('S1', 'One review given room', { mode: 'single' }),
    def('S2', 'Review grid on a band', { frame: 'band', mode: 'grid', heading: 'eyebrow' }),
    def('S3', 'Review grid beside the heading', { mode: 'grid', columns: 2, heading: 'inline' }),
  ],
  faq: [
    def('S1', 'Full-width accordion', {}),
    def('S2', 'Heading and intro beside the accordion', { columns: 2, heading: 'inline' }),
    def('S3', 'Accordion in a card with a jump list', { frame: 'card', columns: 2, aside: 'jump' }),
  ],
  form: [
    def('S1', 'Form under the heading', {}),
    def('S2', 'Form beside the reasons to write', { columns: 2, aside: 'infocard' }),
    def('S3', 'Form in a card, heading beside it', { frame: 'card', columns: 2, heading: 'inline' }),
  ],
  stats: [
    def('S1', 'Counter strip full width', {}),
    def('S2', 'Counter strip on a band', { frame: 'band', heading: 'eyebrow' }),
    def('S3', 'Counters beside the heading', { columns: 2, heading: 'inline' }),
  ],
  trust: [
    def('S1', 'Trust strip full width', {}),
    def('S2', 'Trust strip in a card', { frame: 'card', heading: 'eyebrow' }),
    def('S3', 'Trust strip beside the heading', { columns: 2, heading: 'inline' }),
  ],
  divider: [
    def('S1', 'Light seam', {}),
    def('S2', 'Inverse seam on a band', { frame: 'band', heading: 'eyebrow' }),
    def('S3', 'Seam beside the section label', { columns: 2, heading: 'inline' }),
  ],
  // THE THREE CHROME SHAPES ARE DECIDED. The breeder picked dial S2, sheet S2 and strip S2
  // on the contact board (2026-09-19), and PageDial, SectionSheet and SectionStrip have been
  // pruned to those arrangements — the losing markup and CSS are gone, and so are the
  // components' `style` props. These entries STAY because the approved records name
  // `styles: ["S1","S2","S3"]` on their chrome sections and `board_approve.py` matches a
  // pick against that list: deleting them would make three approved records refuse to
  // re-approve. They are a record of a decision taken, not a menu still open, and the
  // preview route now renders the one shipped arrangement whichever id it is asked for.
  dial: [
    def('S1', 'Progress ring above a numbered list', { ring: 'shown', marks: 'number', list: 'stack' }),
    def('S2', 'Compact numbered strip, no ring', { ring: 'hidden', marks: 'number', list: 'rail' }),
    def('S3', 'Progress ring above labels only', { ring: 'shown', marks: 'label', list: 'stack' }),
  ],
  sheet: [
    def('S1', 'Sections as the fourth tab in the bar', { launcher: 'tab' }),
    def('S2', 'Full-width Sections pill above the bar', { launcher: 'pill' }),
    def('S3', 'Floating round Sections button, bottom right', { launcher: 'fab' }),
  ],
  strip: [
    def('S1', 'Outlined pills, number in the brand colour', { chip: 'outline' }),
    def('S2', 'Filled tab chips, active chip on brand', { chip: 'filled' }),
    def('S3', 'Flat text links, underline on the active one', { chip: 'text' }),
  ],
  // All three stack into labelled rows below 640px — that is working rule 13 and is not
  // one of the options. What differs is the chrome above that breakpoint.
  table: [
    def('S1', 'Ruled rows under a brand header band', { chrome: 'ruled' }),
    def('S2', 'Zebra rows inside a card', { frame: 'card', chrome: 'zebra' }),
    def('S3', 'Borderless rows with brass column rules', { chrome: 'brass' }),
  ],
  // Component 18, the video (spec §9 amendment 7; working rule 14). S3 is the one a rebuilt
  // page takes unless the board says otherwise: it is the only arrangement that does not
  // load a player before anybody asks for one.
  video: [
    def('S1', 'Player in a card, caption beneath it', { frame: 'card', play: 'iframe' }),
    def('S2', 'Player full width on a steel band', { frame: 'band', play: 'iframe' }),
    def('S3', 'Thumbnail with a play button, player loaded on click', { play: 'facade' }),
  ],
};

/** The class list a layout resolves to — the ONE place a style becomes markup. Both the
 *  preview route and a rebuilt page call this; the rules are in board-styles.css. */
export function boxClass(style: StyleDef | Layout): string {
  const l: Layout = 'layout' in style ? (style as StyleDef).layout : (style as Layout);
  return [
    'bl-box',
    `bl-frame-${l.frame ?? NEUTRAL.frame}`,
    `bl-cols-${l.columns ?? NEUTRAL.columns}`,
    `bl-media-${l.media ?? NEUTRAL.media}`,
    `bl-list-${l.list ?? NEUTRAL.list}`,
    `bl-aside-${l.aside ?? NEUTRAL.aside}`,
    `bl-head-${l.heading ?? NEUTRAL.heading}`,
    `bl-chrome-${l.chrome ?? NEUTRAL.chrome}`,
  ].join(' ');
}

/** The three styles a shape offers, or the `standard` trio for a shape this map has not
 *  learned yet — a board is never rendered with an empty option set. */
export function stylesFor(shape: string): [StyleDef, StyleDef, StyleDef] {
  return STYLES[shape as Shape] ?? STYLES.standard;
}

/** The one style a pick names. Unknown id → S1, so a stale pick renders rather than throws. */
export function styleById(shape: string, id: string): StyleDef {
  return stylesFor(shape).find((s) => s.id === id) ?? stylesFor(shape)[0];
}
