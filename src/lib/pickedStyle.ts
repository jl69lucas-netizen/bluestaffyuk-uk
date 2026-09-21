// src/lib/pickedStyle.ts — the style a board record's section was APPROVED with.
//
// A rebuilt page must mount the arrangement the breeder actually picked on the board, and
// it must mount the same one the preview showed them. Both sides therefore resolve through
// src/lib/boardStyles.ts: the preview route calls `stylesForSection()` to render every style
// a section offers, and a page calls this to render the single one `approval.picks` names. A
// page that hard-coded its own `boxClass({...})` would be free to drift from the board the
// breeder signed off.
import { stylesForSection, styleById, layoutTypeFor, type StyleDef } from './boardStyles';

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
 * TWO STEPS, and the second is the one that matters. `styleById()` resolves an id against the
 * whole repo — per-page ids first, then the shape's trio, then the family's — and it is reused
 * here rather than copied, so the page and the preview route can never disagree about what an
 * id means. But `styleById()` is deliberately forgiving: an id it cannot place falls back to
 * the first style of the trio, which on a page would be an arrangement nobody chose, rendering
 * perfectly fine. So the def it returns is then checked for MEMBERSHIP of the menu this
 * section actually offered — `stylesForSection()`, the same call the board preview made — and
 * anything else throws. That also catches the subtler failure the global lookup allows: a
 * `stats` section picking `H-FS3`, or a for-sale hero picking `H-GD1`, both of which resolve
 * by id and neither of which was ever on this section's board.
 */
export function pickedStyle(record: PickedStyleSource, id: string): StyleDef {
  const section = record.sections.find((s) => s.id === id);
  if (!section) throw new Error(`pickedStyle: the record has no section ${id}`);
  const pick = record.approval?.picks?.[id] ?? section.options?.pick ?? null;
  if (!pick) throw new Error(`pickedStyle: section ${id} carries no approved style pick`);
  const family = layoutTypeFor(record.meta?.page_type ?? '', record.meta?.layout_type ?? null);
  const offered = stylesForSection(section.shape, section.styles ?? undefined, family);
  const found = styleById(section.shape, pick, family);
  if (!offered.some((s) => s.id === found.id)) {
    throw new Error(`pickedStyle: section ${id} was picked ${pick}, which is not one of the `
      + `styles it offers (${offered.map((s) => s.id).join('/')})`);
  }
  return found;
}
