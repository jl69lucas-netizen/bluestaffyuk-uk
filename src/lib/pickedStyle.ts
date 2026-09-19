// src/lib/pickedStyle.ts — the style a board record's section was APPROVED with.
//
// A rebuilt page must mount the arrangement the breeder actually picked on the board, and
// it must mount the same one the preview showed them. Both sides therefore resolve through
// `STYLES` in src/lib/boardStyles.ts: the preview route renders every style a section
// offers, and a page renders the single one `approval.picks` names. A page that hard-coded
// its own `boxClass({...})` would be free to drift from the board the breeder signed off.
import { STYLES, STYLE_IDS, type Shape, type StyleDef } from './boardStyles';

/** The shape of a board record this helper needs. Structural, so the imported JSON fits. */
export interface PickedStyleSource {
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
  const styles = STYLES[section.shape as Shape];
  if (!styles) throw new Error(`pickedStyle: section ${id} has shape ${section.shape}, which offers no styles`);
  const found = styles.find((s) => s.id === pick);
  if (!found) throw new Error(`pickedStyle: section ${id} was picked ${pick}, which is not one of ${STYLE_IDS.join('/')}`);
  return found;
}
