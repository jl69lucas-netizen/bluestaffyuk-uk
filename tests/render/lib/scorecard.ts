import { mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';
import type { Defect } from './registry.js';

/** Named PagePartial, not Partial — `Partial<T>` is a TypeScript built-in. */
export interface PagePartial {
  slug: string;
  page_type: string;
  viewport: number;
  examined: Record<string, number>;
  defects: Defect[];
  overrides: { checkId: string; reason: string }[];
}

const RAW_DIR = resolve(process.cwd(), 'data/quality/raw');

/**
 * Slug → a filename component that cannot contain a path separator.
 *
 * Two corpus pages are nested — `blog/african-grey-parrot-cage-setup` and
 * `available/roys`. Interpolated raw, those produce `data/quality/raw/blog/<...>.json`,
 * a directory that does not exist, so the write throws, the page test fails AFTER its
 * checks have already run, and the page contributes no partial. A page with no partial
 * scores ABSENT rather than failed — the failure mode this harness treats as its worst.
 * Guard 1 in build_scorecard.mjs would catch the count mismatch, but it would report it
 * as a crashed page and send someone hunting a defect that is really a filename.
 *
 * The `slug` FIELD inside the JSON keeps the real slug; only the filename is flattened.
 */
export function flattenSlug(slug: string): string {
  return slug.replace(/\//g, '__');
}

export function writePartial(p: PagePartial): void {
  mkdirSync(RAW_DIR, { recursive: true });
  writeFileSync(
    resolve(RAW_DIR, `${flattenSlug(p.slug)}-vp${p.viewport}.json`),
    JSON.stringify(p, null, 2),
  );
}

/**
 * The list of every registered check id, written once per run.
 * The merge script needs this to detect a check that ran NOWHERE — such a check
 * contributes no key to any partial's `examined` map, so it is invisible to a
 * guard that only reads the partials.
 */
export function writeManifest(checkIds: string[], expectedPartials: number): void {
  mkdirSync(RAW_DIR, { recursive: true });
  writeFileSync(
    resolve(RAW_DIR, '_manifest.json'),
    JSON.stringify({ checkIds, expectedPartials }, null, 2),
  );
}

/**
 * A run's results must come from that run. Without this, a refused or crashed run
 * leaves the PREVIOUS run's partials sitting in RAW_DIR; writeManifest still writes
 * expectedPartials for the CURRENT target list (which is usually unchanged), so
 * build_scorecard.mjs Guard 1 compares old-file-count against new-expected-count,
 * finds them equal, and merges yesterday's numbers into a scorecard dated today —
 * a run that never executed, reported as if it had. Reproduced 2026-08-01: the
 * dist/-freshness beforeAll threw, zero new partials were written, and the 27
 * stale partials from the prior run still satisfied Guard 1's count check.
 * Call this immediately before writeManifest, so a refusal leaves RAW_DIR empty
 * rather than stale.
 */
export function resetRaw(dir: string = RAW_DIR): void {
  rmSync(dir, { recursive: true, force: true });
}
