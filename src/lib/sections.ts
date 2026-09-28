// src/lib/sections.ts — the section list a page exposes to PageDial and SectionSheet.
//
// A section is a `<section id="…">` in the page body. Both components take the list as a
// PROP rather than reading the DOM at build time, because the page owns the order: it is
// the board record's section order, and a component that re-derived it from rendered HTML
// would be free to disagree with the page it sits in.
//
// The ids here are the same ids the `<section>` elements carry, so `nav-anchors-resolve`
// (blocking) is satisfied by construction as long as the page passes its own list.
export interface SectionRef {
  /** The `<section id>` on the page. Must resolve — a dial link to nothing is a dead anchor. */
  id: string;
  /** The short label shown in the dial and the sheet, not the full heading. */
  label: string;
  /** The section's heading, the buyer question it answers. The city set's sheet lists it
   *  (CityJumpBand); the kit set never reads it. */
  question?: string;
  /** The line icon the city set's stepper shows for the section (src/components/kit/cityIcons.ts). */
  icon?: CityIcon;
  /** The one-word name under the city stepper's stop ("Puppies"); `label` when absent. */
  stop?: string;
}

/** The line icons a city page's jump band draws, by name (src/components/kit/cityIcons.ts). */
export type CityIcon = 'list' | 'puppies' | 'prices' | 'deposit' | 'delivery' | 'health'
  | 'home' | 'play' | 'faq' | 'enquire';

/** A board record's sections, narrowed to what the two nav components need.
 *  Typed structurally so `scripts/build_page_board.py`'s JSON can be handed over as-is. */
export interface SectionSource {
  sections: { id: string; heading: string }[];
}

/**
 * The dial/sheet list for a board record.
 *
 * The label is the heading up to its first colon: page headings on this site are written
 * "Health testing: what we screen for", and a 196px dial column cannot show the tail. The
 * trim is here rather than in either component so the dial and the sheet cannot show two
 * different labels for the same section.
 */
export const sectionsFromRecord = (record: SectionSource): SectionRef[] =>
  record.sections.map((s) => ({ id: s.id, label: s.heading.replace(/:.*$/, '').trim() }));
