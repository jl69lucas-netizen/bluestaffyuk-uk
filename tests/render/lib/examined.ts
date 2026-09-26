import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

/**
 * The slice of a scorecard (scripts/build_scorecard.mjs) the zero-examined guard reads.
 * Cards live at data/quality/scorecards/<slug with / as __>-<YYYY-MM-DD>.json, one per page
 * per run date, and carry `examined_by_check`: units judged per check, summed across that
 * page's viewports.
 */
export interface Scorecard {
  slug: string;
  date: string;
  examined_by_check?: Record<string, number>;
}

/**
 * Every card on disk; an absent directory is an empty list, never an error. A card that does
 * not parse is an error that names the file — a bare JSON SyntaxError points at nothing.
 */
export function readScorecards(dir: string): Scorecard[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .map((f) => {
      const path = join(dir, f);
      try {
        return JSON.parse(readFileSync(path, 'utf8')) as Scorecard;
      } catch (e) {
        throw new Error(`unreadable scorecard ${path}: ${(e as Error).message}`);
      }
    });
}

/**
 * The newest card of each slug, restricted to `slugs` when given. Per slug rather than
 * "the newest date": a one-page re-run writes today's card for that page only, and judging
 * today's date alone would read every other page as absent.
 */
export function latestCards(cards: Scorecard[], slugs?: string[]): Scorecard[] {
  const want = slugs ? new Set(slugs) : null;
  const best = new Map<string, Scorecard>();
  for (const c of cards) {
    if (want && !want.has(c.slug)) continue;
    const prev = best.get(c.slug);
    if (!prev || c.date > prev.date) best.set(c.slug, c);
  }
  return [...best.values()];
}

/** Per registered, non-deferred id: summed examined count, or null when no card has its key. */
function examinedTotals(
  checkIds: string[],
  deferred: Record<string, string>,
  cards: Scorecard[],
): Map<string, number | null> {
  const total = new Map<string, number | null>(
    checkIds.filter((id) => !(id in deferred)).map((id) => [id, null]),
  );
  for (const c of cards) {
    for (const [id, n] of Object.entries(c.examined_by_check ?? {})) {
      if (total.has(id)) total.set(id, (total.get(id) ?? 0) + n);
    }
  }
  return total;
}

/**
 * Registered, non-deferred check ids the cards DID measure and whose examined count sums to
 * zero across them: a check that ran and judged nothing. This fails the meta gate.
 */
export function zeroExamined(
  checkIds: string[],
  deferred: Record<string, string>,
  cards: Scorecard[],
): string[] {
  return [...examinedTotals(checkIds, deferred, cards).entries()]
    .filter(([, n]) => n === 0)
    .map(([id]) => id)
    .sort();
}

/**
 * Registered, non-deferred check ids with no key in ANY card. The cards are the last
 * successful page run, so this is usually a check registered since then; reported by name,
 * not failed — the runner's live Guard 2 (seeded from the manifest, not the cards) judges it
 * on the next full run.
 */
export function notYetMeasured(
  checkIds: string[],
  deferred: Record<string, string>,
  cards: Scorecard[],
): string[] {
  return [...examinedTotals(checkIds, deferred, cards).entries()]
    .filter(([, n]) => n === null)
    .map(([id]) => id)
    .sort();
}
