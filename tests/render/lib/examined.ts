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

/** Every card on disk; an absent directory is an empty list, never an error. */
export function readScorecards(dir: string): Scorecard[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .map((f) => JSON.parse(readFileSync(join(dir, f), 'utf8')) as Scorecard);
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

/**
 * Registered, non-deferred check ids whose examined count sums to zero across `cards`.
 * Seeded from the ids, not from the cards: a check that ran nowhere contributes no key to any
 * card and would be invisible to a sum over the cards alone (build_scorecard.mjs Guard 2's
 * own reasoning).
 */
export function zeroExamined(
  checkIds: string[],
  deferred: Record<string, string>,
  cards: Scorecard[],
): string[] {
  const total = new Map<string, number>(checkIds.map((id) => [id, 0]));
  for (const c of cards) {
    for (const [id, n] of Object.entries(c.examined_by_check ?? {})) {
      if (total.has(id)) total.set(id, (total.get(id) ?? 0) + n);
    }
  }
  return [...total.entries()]
    .filter(([id, n]) => n === 0 && !(id in deferred))
    .map(([id]) => id)
    .sort();
}
