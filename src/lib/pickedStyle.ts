// src/lib/pickedStyle.ts — the style a board record's section was APPROVED with.
//
// A rebuilt page must mount the arrangement the breeder actually picked on the board, and
// it must mount the same one the preview showed them. Both sides therefore resolve through
// `STYLES` in src/lib/boardStyles.ts: the preview route renders every style a section
// offers, and a page renders the single one `approval.picks` names. A page that hard-coded
// its own `boxClass({...})` would be free to drift from the board the breeder signed off.
import {
  STYLES, STYLE_IDS, STYLES_BY_ID, layoutTypeFor, stylesFor,
  type Shape, type StyleDef,
} from './boardStyles';

/** The shape of a board record this helper needs. Structural, so the imported JSON fits.
 *
 *  `meta` is optional because the four pages built before working rule 16 pick `S1`/`S2`/`S3`
 *  on every shape and never need the layout family. A rule-16 record names its own
 *  `layout_type`, and its hero and counter picks are per-page ids (`H-FS3`, `C-FS1`) that
 *  resolve against that family's trio rather than against the shape-wide one. */
export interface PickedStyleSource {
  meta?: { page_type?: string; layout_type?: string | null } | null;
  sections: { id: string; shape: string; styles?: string[] | null; options?: { pick?: string | null } }[];
  approval?: { picks?: Record<string, string> } | null;
}

/**
 * The `StyleDef` section `id` was approved with.
 *
 * The pick is read from `approval.picks` first and from `options.pick` second. They are
 * written by the same step of `board_approve.py` and agree in practice, but the approval
 * block is the record OF the decision while `options.pick` is a convenience copy — so the
 * approval wins where they ever disagree.
 *
 * Throws rather than falling back to S1. A page whose section silently rendered an
 * arrangement nobody chose is the exact failure the board exists to prevent, and it would
 * ship looking perfectly fine.
 */
export function pickedStyle(record: PickedStyleSource, id: string): StyleDef {
  const section = record.sections.find((s) => s.id === id);
  if (!section) throw new Error(`pickedStyle: the record has no section ${id}`);
  const pick = record.approval?.picks?.[id] ?? section.options?.pick ?? null;
  if (!pick) throw new Error(`pickedStyle: section ${id} carries no approved style pick`);
  // ORDER MATTERS, and it is `styleById()`'s order for `styleById()`'s reason: a per-page id
  // (`H-FS3`, `C-FS1`) names ONE arrangement across the whole repo and is looked up by id,
  // while `S1` on a hero means the shape-wide trio the pre-rule-16 pages approved. The
  // family's own trio is the last resort, for a record that names a family and an id the
  // global map has not learned. Unlike `styleById()` this throws rather than falling back to
  // the first style: a page silently rendering an arrangement nobody chose is the exact
  // failure the board exists to prevent, and it would ship looking perfectly fine.
  const shapeStyles = STYLES[section.shape as Shape];
  if (!shapeStyles) throw new Error(`pickedStyle: section ${id} has shape ${section.shape}, which offers no styles`);
  const family = layoutTypeFor(record.meta?.page_type ?? '', record.meta?.layout_type ?? null);
  const found = STYLES_BY_ID[pick]
    ?? shapeStyles.find((s) => s.id === pick)
    ?? stylesFor(section.shape, family).find((s) => s.id === pick);
  if (!found) {
    throw new Error(`pickedStyle: section ${id} was picked ${pick}, which is neither `
      + `${STYLE_IDS.join('/')} nor a per-page style id`);
  }
  return found;
}
