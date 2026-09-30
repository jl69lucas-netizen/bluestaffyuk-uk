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
  /** Hero only (working rule 16): the ARRANGEMENT of copy against media. A PROP, for the
   *  `play` axis's reason — a mosaic of four tiles and a single portrait are different
   *  markup, and a panel with no photo column is a different grid, none of which a
   *  stylesheet can turn into another. `split` is the shipped two-column hero. */
  hero?: 'split' | 'stacked' | 'mosaic' | 'panel' | 'bleed';
  /** Hero only: the block under the lede. A PROP. `chips` is the credential pill row,
   *  `stats` the figure tiles, `aside` the key-facts / quote card beside the copy, `ticks`
   *  the inline checked list. Each renders ONLY if the page handed the hero the data for it:
   *  an empty ledge is a hero with nothing under its lede, never an invented claim. */
  ledge?: 'none' | 'chips' | 'stats' | 'aside' | 'ticks';
  /** Hero only: where the copy column's text sits. A PROP. */
  align?: 'left' | 'center';
  /** CounterStrip only (working rule 16): how one figure tile is drawn. A PROP, for the
   *  `play` axis's reason — a ring is an SVG, a card is a bordered box and the inline line is
   *  a flex row of pairs; the three are different markup, not three paint jobs. */
  tiles?: 'inline' | 'ruled' | 'card' | 'ring' | 'seam';
  /** CounterStrip only: where one figure's LABEL sits against the figure. A PROP and a
   *  structural axis: `beside` is a row, `under` and `above` are a column read in opposite
   *  directions, and the three are different DOM order, not three paddings. It exists because
   *  the counter needed a fourth structural axis to be able to offer eighteen arrangements no
   *  two of which are one axis apart — with three, the arithmetic caps the set at six. */
  label?: 'under' | 'beside' | 'above';
}

/** THE AXES A DISTINCTNESS CLAIM IS MADE ON, per shape, and the one place they are named.
 *
 *  Working rule 16's promise is that no two pages share a hero or a counter. A pair of styles
 *  one axis apart does not keep it: `media: 'left'` against `media: 'right'` is the same hero
 *  with the photo on the other side, and a board offering both is offering one arrangement
 *  twice. So the rule the tests enforce is TWO: every pair of the eighteen, within a family
 *  and across families, differs on at least two of these.
 *
 *  What is deliberately NOT here: the photo's SIDE (left against right is a mirror, not an
 *  arrangement) and the heading's position (`heading`, which moves a label, not a layout).
 *  `stack` is not an axis of `Layout` at all — it is `media === 'top'`, the one part of the
 *  media axis that IS structural, and `structuralKey()` below is what derives it. */
export const STRUCTURAL_AXES: Record<'hero' | 'stats', readonly string[]> = {
  hero: ['hero', 'ledge', 'stack', 'frame'],
  stats: ['tiles', 'label', 'frame', 'columns'],
};

/** The structural fingerprint of a layout, for the shape whose distinctness is being judged.
 *  Two styles are DIFFERENT ENOUGH when these differ in at least two places. */
export function structuralKey(shape: 'hero' | 'stats', l: Layout): (string | number | undefined)[] {
  return STRUCTURAL_AXES[shape].map((axis) =>
    axis === 'stack' ? (l.media === 'top' ? 'top' : 'side')
      : (l as Record<string, unknown>)[axis] as string | number | undefined);
}

export type Axis = keyof Layout;

export interface StyleDef {
  /** `S1`/`S2`/`S3` for a shape whose three options are the same on every page. The hero and
   *  the counter strip are NOT: working rule 16 gives each page type its own three, and those
   *  carry their own ids (`H-FS1`, `C-GD2`, …) so that one id names one arrangement across
   *  the whole repo and a record's pick can never be read against the wrong set. */
  id: string;
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
const NEUTRAL: Required<Omit<Layout, 'mode' | 'ring' | 'marks' | 'launcher' | 'chip' | 'play'
  | 'hero' | 'ledge' | 'align' | 'tiles' | 'label'>> = {
  frame: 'plain', columns: 1, media: 'none', list: 'stack', aside: 'none', heading: 'above',
  chrome: 'ruled',
};

/** Per shape, the axes that shape's RENDERER reads. Anything else would be decoration. */
export const RENDERED_AXES: Record<Shape, readonly Axis[]> = {
  // The kit Hero owns its own copy, chips and CTA row; what a board can move is the bed it
  // sits on and which side its photo is on (board-styles.css reorders `.kit-hero`).
  // Working rule 16: the hero is per PAGE TYPE, so the axes are the ones Hero.astro reads as
  // props (`hero`, `ledge`, `align`) as well as the bed and the photo side the box writes.
  hero: ['frame', 'media', 'hero', 'ledge', 'align'],
  takeaways: ['frame', 'list', 'columns', 'aside', 'heading'],
  standard: ['frame', 'media', 'columns', 'aside', 'heading'],
  puppies: ['frame', 'list', 'columns', 'heading'],
  // Testimonial takes `mode`; the rest is the bed and where the heading sits.
  reviews: ['frame', 'mode', 'columns', 'heading'],
  faq: ['frame', 'columns', 'aside', 'heading'],
  form: ['frame', 'columns', 'aside', 'heading'],
  // Working rule 16 again: `tiles` is how ONE figure is drawn, and CounterStrip reads it as
  // a prop. The bed, the column count and the heading position are the ordinary three.
  stats: ['frame', 'columns', 'heading', 'tiles', 'label'],
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

// ── working rule 16: the hero and the counter strip are PER PAGE TYPE ──────────────────────
//
// "No two pages share the same hero layout or the same counter strip." Two shapes therefore
// have no single trio: each PAGE TYPE gets three, and the three differ structurally from each
// other AND from every other page type's three, so a set of three pages of one type can take
// one arrangement each and still share nothing. `tests/py/test_board_previews.py` holds all
// eighteen hero defs (and all eighteen counter defs) to unique axis tuples.
//
// THE LAYOUTS COME FROM THE BREEDER'S IDEA SHEETS. The commit that added them names the sheet
// each one was drawn from, so a layout is traceable to a reference rather than to taste.
//
// A page type is NOT the same thing as `meta.page_type`: eight of the thirteen records are
// `interior`, and a privacy policy, a breed guide and an about page do not want one hero
// between them. `layoutTypeFor()` below is the mapping, and a record may state its own
// `meta.layout_type` when the mapping would guess wrong.

/** The layout families. The first six are the ones the hero and the counter strip are cut
 *  for in this file. `city` is the seventh (Known Issue 60, closed by the London component
 *  design pass): a city page takes all fifteen of its components from its OWN component pass
 *  (`data/design/city-picks/<slug>.json`, gated by `scripts/pageboard.py`
 *  `city_rule16_findings`), so this file cuts no trio for it. */
export type LayoutType =
  | 'home' | 'for-sale' | 'interior-guide' | 'interior-about' | 'interior-utility' | 'blog'
  | 'city';

export const LAYOUT_TYPES: readonly LayoutType[] = [
  'home', 'for-sale', 'interior-guide', 'interior-about', 'interior-utility', 'blog', 'city',
];

/** The families whose hero and counter trios live in this file: every family but `city`. */
export type PerPageFamily = Exclude<LayoutType, 'city'>;

/** `meta.page_type` -> the layout family, when the record does not state one itself. The
 *  `interior` fallback is the GUIDE set, because that is what most interior pages are; the
 *  three utility pages (privacy, thank-you, contact) say so in their own records. */
/** Every value `meta.page_type` may take, as `schemas/board.schema.json` enumerates them.
 *  `tests/py/test_board_previews.py` reads the schema and this union and holds them equal, so
 *  a page type added to the schema and forgotten here is a failing test rather than a page
 *  that silently falls back to the guide set. */
export type PageType =
  | 'home' | 'hub' | 'location' | 'puppy' | 'blog'
  | 'about' | 'contact' | 'comparison' | 'interior' | 'for-sale';

const LAYOUT_BY_PAGE_TYPE: Record<PageType, LayoutType> = {
  home: 'home',
  'for-sale': 'for-sale',
  puppy: 'for-sale',
  hub: 'for-sale',
  blog: 'blog',
  about: 'interior-about',
  contact: 'interior-utility',
  interior: 'interior-guide',
  comparison: 'interior-guide',
  location: 'city',
};

/** The layout family a record belongs to. An explicit `meta.layout_type` wins; anything
 *  unrecognised falls to the guide set rather than throwing, so a new page type renders. */
export function layoutTypeFor(pageType: string, explicit?: string | null): LayoutType {
  if (explicit && (LAYOUT_TYPES as readonly string[]).includes(explicit)) {
    return explicit as LayoutType;
  }
  return LAYOUT_BY_PAGE_TYPE[pageType as PageType] ?? 'interior-guide';
}

/** Three heroes per layout family. Every one of the eighteen has its own axis tuple.
 *
 *  Rule 10 binds all of them: the photo precedes the copy in source order and the band is
 *  held between 390px and 450px at 1024px and up with nothing clipped. `stacked`, `mosaic`
 *  and `bleed` release the ceiling where the arrangement is no longer a split hero (a 450px
 *  cap over a stacked hero is a guillotine, not a clamp) — board-styles.css does that, and
 *  scripts/measure_canvas_heights.mjs measures what actually happens. */
export const HERO_STYLES_BY_PAGE_TYPE: Record<PerPageFamily, [StyleDef, StyleDef, StyleDef]> = {
  // hero-idea00 (copy left on a band, photo card right, a credentials card beneath it),
  // hero-idea (a photo mosaic with figure tiles under it), hero-idea-1 (a full-bleed photo
  // filling one half, one CTA, quiet copy beside it).
  home: [
    def('H-HM1', 'Copy left on a steel band, photo right, credential chips under the lede',
        { hero: 'split', ledge: 'chips', media: 'right', frame: 'band', align: 'left' }),
    def('H-HM2', 'Four-photo mosaic above the copy, figure tiles beneath it',
        { hero: 'mosaic', ledge: 'stats', media: 'top', align: 'center' }),
    def('H-HM3', 'Full-bleed photo on the right half, quiet copy left',
        { hero: 'bleed', ledge: 'none', media: 'right', align: 'left' }),
  ],
  // hero-idea66 (a staggered portrait mosaic with a tick list under the CTAs), hero-idea-3
  // (a full-bleed band over the copy with a chip row), hero-idea77 (a figure row and one
  // large photo, stacked).
  'for-sale': [
    def('H-FS1', 'Puppy grid peek right of the copy, tick list under the lede',
        { hero: 'mosaic', ledge: 'ticks', media: 'right', align: 'left' }),
    def('H-FS2', 'Full-bleed photo above the copy, price chips under the lede',
        { hero: 'bleed', ledge: 'chips', media: 'top', align: 'left' }),
    def('H-FS3', 'Stacked on a steel band, figures under the CTA row',
        { hero: 'stacked', ledge: 'stats', media: 'top', frame: 'band', align: 'center' }),
  ],
  // component-idea-faq1 (an editorial two-column: prose left, one image right),
  // component-idea5 (an image and a specification column), component-idea33 (wide rows in a
  // card, title left and summary right).
  'interior-guide': [
    def('H-GD1', 'Editorial two-column: copy left, key-facts aside, photo right',
        { hero: 'split', ledge: 'aside', media: 'right', align: 'left' }),
    def('H-GD2', 'Magazine: image above the copy in a card, chips under the lede',
        { hero: 'stacked', ledge: 'chips', media: 'top', frame: 'card', align: 'left' }),
    def('H-GD3', 'Text-led card with a contents aside, photo left',
        { hero: 'panel', ledge: 'aside', media: 'left', frame: 'card', align: 'left' }),
  ],
  // hero-idea-5 (a portrait with a caption chip and a credential line), hero-idea66 (named
  // portraits), hero-idea00 (the band treatment).
  'interior-about': [
    def('H-AB1', 'Photo mosaic left of the copy on a steel band, quote in the aside',
        { hero: 'mosaic', ledge: 'aside', media: 'left', frame: 'band', align: 'left' }),
    def('H-AB2', 'Portrait right of the copy in a card, tick list under the lede',
        { hero: 'split', ledge: 'ticks', media: 'right', frame: 'card', align: 'left' }),
    def('H-AB3', 'Photo above centred copy, tick list beneath it',
        { hero: 'stacked', ledge: 'ticks', media: 'top', align: 'center' }),
  ],
  // The quiet set. A privacy policy, a thank-you page and a contact page are not selling
  // anything, so none of the three carries a claim under its lede — `ledge: 'none'` on all
  // three, which is why their distinctness has to come from the layout and the bed.
  'interior-utility': [
    def('H-UT1', 'Small photo mosaic right of the copy, in a card',
        { hero: 'mosaic', ledge: 'none', media: 'right', frame: 'card', align: 'left' }),
    def('H-UT2', 'Full-bleed photo above the copy, in a card',
        { hero: 'bleed', ledge: 'none', media: 'top', frame: 'card', align: 'left' }),
    def('H-UT3', 'Title panel on a steel band with a slim photo above it',
        { hero: 'panel', ledge: 'none', media: 'top', frame: 'band', align: 'center' }),
  ],
  // component-idea55 (release cards with a ruled meta block at the foot), component-idea3
  // (numbered columns divided by vertical rules), component-idea-modern (a tab row over one
  // wide panel).
  blog: [
    def('H-BL1', 'Full-bleed photo one side on a steel band, post counts beneath',
        { hero: 'bleed', ledge: 'stats', media: 'right', frame: 'band', align: 'left' }),
    def('H-BL2', 'Contents panel with the cover image above it',
        { hero: 'panel', ledge: 'aside', media: 'top', align: 'left' }),
    def('H-BL3', 'Photo mosaic above the copy on a steel band, topic chips',
        { hero: 'mosaic', ledge: 'chips', media: 'top', frame: 'band', align: 'center' }),
  ],
};

/** Three counter strips per layout family, on the same construction and the same rule.
 *
 *  The FIGURES never come from here — they come from the record's `sections[].stats`, each row
 *  sourced to a path in `data/*.json` (working rules 9 and 16). A style decides how a figure is
 *  drawn, never what it says.
 *
 *  `label` is the fourth structural axis, and it is here because of arithmetic rather than
 *  taste: with three axes of five, three and two values, no more than six arrangements can be
 *  pairwise two axes apart, and eighteen are needed. With `label` the set exists — and it
 *  exists exactly, so every one of the eighteen `frame`/`columns`/`label` combinations is used
 *  once. That is a tight fit, and it is recorded here so the next person does not try to add a
 *  nineteenth. */
export const COUNTER_STYLES_BY_PAGE_TYPE: Record<PerPageFamily, [StyleDef, StyleDef, StyleDef]> = {
  // hero-idea (the figure tiles under the mosaic), component-idea3 (columns with vertical
  // rules), component-idea55 (the ruled meta block at the foot of a card).
  home: [
    def('C-HM1', 'One flush line of figure-and-label pairs',
        { tiles: 'inline', label: 'under' }),
    def('C-HM2', 'Ruled columns, the label beside each figure',
        { tiles: 'ruled', label: 'beside' }),
    def('C-HM3', 'Seam bar inside a card, labels above the figures',
        { tiles: 'seam', frame: 'card', label: 'above' }),
  ],
  // hero-idea77 (a ruled figure row), component-idea1 (three cards in a row), and the seam
  // the kit already owns (--seam-gradient).
  'for-sale': [
    def('C-FS1', 'Figure cards, labels above the figures',
        { tiles: 'card', label: 'above' }),
    def('C-FS2', 'Ring tiles in a card, beside the heading',
        { tiles: 'ring', frame: 'card', columns: 2, label: 'under' }),
    def('C-FS3', 'Seam bar in a card, beside the heading, labels beside the figures',
        { tiles: 'seam', frame: 'card', columns: 2, label: 'beside' }),
  ],
  // component-idea2 (an icon-led ruled list), component-idea444 (ruled columns), and the ring
  // the kit's PageDial already draws, reused at figure size.
  'interior-guide': [
    def('C-GD1', 'Ruled columns beside the heading',
        { tiles: 'ruled', columns: 2, label: 'under' }),
    def('C-GD2', 'Ring tiles beside the heading, labels above',
        { tiles: 'ring', columns: 2, label: 'above' }),
    def('C-GD3', 'Figure cards inside a card',
        { tiles: 'card', frame: 'card', label: 'under' }),
  ],
  // The about page's set is the one that takes the steel band on all three: a page about who
  // we are is the page that can afford the loudest bed.
  'interior-about': [
    def('C-AB1', 'Figure cards on a steel band, beside the heading',
        { tiles: 'card', frame: 'band', columns: 2, label: 'under' }),
    def('C-AB2', 'Ring tiles on a steel band, labels above',
        { tiles: 'ring', frame: 'band', label: 'above' }),
    def('C-AB3', 'Seam bar on a steel band, beside the heading, labels above',
        { tiles: 'seam', frame: 'band', columns: 2, label: 'above' }),
  ],
  'interior-utility': [
    def('C-UT1', 'One flush line in a card, beside the heading, labels above',
        { tiles: 'inline', frame: 'card', columns: 2, label: 'above' }),
    def('C-UT2', 'Ring tiles in a card, labels beside the figures',
        { tiles: 'ring', frame: 'card', label: 'beside' }),
    def('C-UT3', 'Figure cards on a steel band, labels beside the figures',
        { tiles: 'card', frame: 'band', label: 'beside' }),
  ],
  blog: [
    def('C-BL1', 'Figure cards beside the heading, labels beside the figures',
        { tiles: 'card', columns: 2, label: 'beside' }),
    def('C-BL2', 'Ruled columns on a steel band',
        { tiles: 'ruled', frame: 'band', label: 'under' }),
    def('C-BL3', 'Ring tiles on a steel band, beside the heading, labels beside',
        { tiles: 'ring', frame: 'band', columns: 2, label: 'beside' }),
  ],
};

/** The shapes whose three styles depend on the page's layout family — working rule 16's two.
 *  `scripts/pageboard.py` carries the same tuple (it is what `locked_picks` re-asks), and
 *  `tests/py/test_board_previews.py` reads both and holds them equal: two copies of a list
 *  that disagree is a section re-asked on the board and locked in the record, or the reverse. */
export const PER_PAGE_SHAPES: readonly Shape[] = ['hero', 'stats'];

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

/** Every per-page def, by its own id. One id names one arrangement across the whole repo, so
 *  a pick can be resolved without knowing which page it was made on — which is what lets the
 *  preview route render a record's own `styles` list rather than a shape's default trio. */
export const STYLES_BY_ID: Record<string, StyleDef> = Object.fromEntries(
  [...Object.values(HERO_STYLES_BY_PAGE_TYPE), ...Object.values(COUNTER_STYLES_BY_PAGE_TYPE)]
    .flat().map((s) => [s.id, s]),
);

/** The three styles a shape offers on a page of this layout family.
 *
 *  `hero` and `stats` are per page type (working rule 16); every other shape has one trio.
 *  A shape this map has not learned yet falls to the `standard` trio — a board is never
 *  rendered with an empty option set. Omitting `layout` keeps the LEGACY S1/S2/S3 trio for
 *  the hero and the counter, which is what the four pages built before this rule still name. */
export function stylesFor(shape: string, layout?: LayoutType | null): [StyleDef, StyleDef, StyleDef] {
  // A `city` page has no trio here: its hero and counter come from its component pass, so a
  // board asking for one gets the shape-wide trio rather than another family's three.
  if (layout && layout !== 'city') {
    if (shape === 'hero') return HERO_STYLES_BY_PAGE_TYPE[layout] ?? STYLES.hero;
    if (shape === 'stats') return COUNTER_STYLES_BY_PAGE_TYPE[layout] ?? STYLES.stats;
  }
  return STYLES[shape as Shape] ?? STYLES.standard;
}

/** The three styles a RECORD's section offers: the ids it names, resolved one by one, or the
 *  shape's trio for the layout family when it names none. A record is the authority on which
 *  three it is offering — reading the map instead would render one set and approve another. */
export function stylesForSection(
  shape: string, ids: readonly string[] | undefined, layout?: LayoutType | null,
): StyleDef[] {
  if (ids && ids.length) return ids.map((id) => styleById(shape, id, layout));
  return [...stylesFor(shape, layout)];
}

/** The one style a pick names. The per-page ids are looked up by id alone; an S1/S2/S3 pick
 *  is read against the shape's own trio. An unknown id falls back to the first style of the
 *  trio, so a stale pick renders rather than throws. */
export function styleById(shape: string, id: string, layout?: LayoutType | null): StyleDef {
  // ORDER MATTERS. `S1` on a hero means the SHAPE-WIDE trio — the arrangement the four pages
  // built before working rule 16 approved — and must not be resolved against this page's
  // per-page set, where no `S1` exists and a `find` would miss and hand back H-…1 for all
  // three. So: the per-page ids by id, then the shape's own trio, then the family's.
  return STYLES_BY_ID[id]
    ?? (STYLES[shape as Shape] ?? STYLES.standard).find((s) => s.id === id)
    ?? stylesFor(shape, layout).find((s) => s.id === id)
    ?? stylesFor(shape, layout)[0];
}
