// src/lib/recordText.ts — the wording and the figures a rebuilt page reads OFF ITS RECORD.
//
// WHY A MODULE AND NOT FOUR COPIES. Working rule 15 says a rebuilt page carries its migrated
// page's verbatim set word for word, and the safest way to do that is not to type the words
// into the page at all: the board record already holds the approved heading, the approved
// opening paragraph and the approved alt, and the page renders what the record says. Three
// pages had each written the same four closures to do it (`sec`, `heading`, `opening`, and
// the tree-node pair), plus the same `LedgeEntry` unwrap and, on two of them, the same
// build-time figure check. A lookup copied three times is a lookup that can be fixed twice,
// which is the reason `src/lib/assets.ts` was hoisted out of the same three pages at the
// review of 0128e21. This is the rest of that move.
//
// EVERYTHING HERE THROWS RATHER THAN RETURNING A BLANK. A `find` that misses returns
// `undefined`, and a heading built from it renders as an empty `<h2>` — a page that passes
// the build, says nothing where the breeder approved a sentence, and is invisible to every
// gate that reads headings by text. A named build-time error says which record and which
// section, while the person who renamed it is still looking at the build.

/** A hero ledge entry is a bare string when it states no figure and `{text, source}` when it
 *  does (spec §9 amendment 10.6) — a chip, a tick, an aside row. */
export type LedgeEntry = string | { text: string };

/** One unwrap, used by the chips and the ticks on every page that mounts a ledge: two copies
 *  of it is two places for the two shapes to drift apart. */
export const ledgeText = (e: LedgeEntry) => (typeof e === 'string' ? e : e.text);

/** An H3 the migrated body put under an H2, with the paragraph that opened it. */
export interface TreeNode { heading: string; verbatim_opening?: string }

/** The part of a board record this module reads. Structural, so an imported record's JSON
 *  fits without either side importing the other's type. */
export interface TextSection {
  id: string;
  heading: string;
  verbatim_opening?: string;
  tree?: readonly TreeNode[];
}
export interface TextRecord {
  meta?: { slug?: string } | null;
  sections: readonly TextSection[];
}

/** The five readers a rebuilt page uses to render its approved wording. */
export interface RecordText {
  /** The section row itself, for the fields with no reader of their own (`stats`, `hero`). */
  sec: (id: string) => TextSection;
  /** The approved H2 — already the repaired one where `verbatim.changed` says so. */
  heading: (id: string) => string;
  /** The first paragraph the section carries word for word. */
  opening: (id: string) => string;
  /** A tree node by position, for a keyword H3. */
  node: (id: string, i: number) => TreeNode;
  /** That node's own carried opening paragraph. */
  nodeOpening: (id: string, i: number) => string;
}

/**
 * `recordText(record)` for one board record: the readers above, each naming the record's own
 * slug in anything it throws, so a page that mounts more than one record still says which.
 */
export function recordText(record: TextRecord, label?: string): RecordText {
  const who = label ?? record.meta?.slug ?? 'board record';
  const sec = (id: string) => {
    const s = record.sections.find((x) => x.id === id);
    if (!s) throw new Error(`${who}: the record has no section ${id}`);
    return s;
  };
  const node = (id: string, i: number) => {
    const n = (sec(id).tree ?? [])[i];
    if (!n) throw new Error(`${who}: section ${id} has no tree node ${i}`);
    return n;
  };
  return {
    sec,
    heading: (id) => sec(id).heading,
    opening: (id) => {
      const o = sec(id).verbatim_opening;
      if (!o) throw new Error(`${who}: section ${id} carries no verbatim opening`);
      return o;
    },
    node,
    nodeOpening: (id, i) => {
      const n = node(id, i);
      if (!n.verbatim_opening) {
        throw new Error(`${who}: ${id} tree node ${i} carries no verbatim opening`);
      }
      return n.verbatim_opening;
    },
  };
}

/** A counter tile or a hero ledge figure, as the record writes it. `source` is a path into a
 *  data file, or a LIST of them when the figure is made of more than one fact — `£200–£350`
 *  is two, and citing only the minimum leaves the maximum unsourced while reading as
 *  sourced (spec §9 amendment 10.5). */
export interface StatRow { n: string; label: string; source?: string | string[] }

/** The key a `source` resolves to in a page's own count table. A LIST is joined, so a figure
 *  standing on two facts cannot be satisfied by a table that knows only one of them. */
export const sourceKey = (source?: string | string[]) =>
  (Array.isArray(source) ? source.join('|') : (source ?? ''));

/**
 * `counted(row)` for one page's table of build-time counts.
 *
 * THE RECORD'S `n` IS THE EXPECTATION, NOT THE FIGURE — the lesson da9c34e wrote down. A
 * record's `n` is a hand-written number: true on the day it was boarded, and the first thing
 * to go stale when a puppy is reserved or a screen is added to the health board. So the
 * figure a page prints is derived from the file its `source` names, and a derived figure that
 * no longer equals what the breeder approved throws at build with BOTH numbers in the message
 * rather than printing one nobody has checked. Keeping both is the point: the data decides
 * what prints, and the record decides when a human has to look.
 *
 * A row whose `source` the table does not know also throws, which is what stops a page
 * quietly falling back to copying the record.
 */
export function countedFigures(
  table: Readonly<Record<string, string | number>>, label: string,
): (row: StatRow) => { n: string; label: string } {
  return (row: StatRow) => {
    const key = sourceKey(row.source);
    const found = table[key];
    if (found === undefined) {
      throw new Error(`${label}: no build-time count for ${key || '(no source)'} `
        + '— a figure this page prints must be derived from data, not copied from the record');
    }
    const n = String(found);
    if (n !== row.n) {
      throw new Error(`${label}: ${key} reads ${n} today and the approved record expects `
        + `${row.n} — the fact moved, so the board's figure needs a look`);
    }
    return { n, label: row.label };
  };
}
