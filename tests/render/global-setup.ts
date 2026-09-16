import type { FullConfig } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { resetRaw, writeManifest } from './lib/scorecard.js';
import { registry } from './lib/registry.js';
import './checks/index.js';

const here = dirname(fileURLToPath(import.meta.url));

/**
 * Playwright loads every spec file's module scope ONCE during collection and AGAIN
 * inside every worker process it spawns. Code that must run exactly once per RUN —
 * not once per PROCESS — cannot live at spec module scope, because "module scope"
 * there means "once per process it happens to load in", not "once, period".
 * globalSetup is the one hook Playwright guarantees runs exactly once, in the main
 * process, before any worker spawns — which is what resetRaw() actually needs.
 *
 * Measured failure (2026-08-01), reproduced on the real harness, not a toy:
 *   rm -rf data/quality/raw && npx playwright test pages.spec.ts \
 *     --grep congo-african-grey-parrot-pair
 * 3 tests ran across 3 viewport projects. Exactly ONE partial survived. resetRaw()
 * at pages.spec.ts module scope ran once per worker process; the last worker to load
 * the module deleted the other workers' already-written output out from under them.
 * Scaled to the full 9-page x 3-viewport suite, that pattern writes 27 partials and
 * leaves some smaller number standing, and build_scorecard.mjs's Guard 1 reports
 * "expected 27, found N" — which the guard's own comment defines as "a page test
 * crashed". A false diagnosis pointing the operator at a crash that never happened,
 * shipped inside the very fix meant to stop this harness issuing false diagnoses.
 *
 * Contrast with writeManifest, which was ALSO always at module scope and was never
 * the problem: two workers each writing the same manifest content is idempotent —
 * the second write just repeats the first. Deleting a directory is not idempotent
 * in that way — the second worker's resetRaw() destroys the first worker's already-
 * written partial. That asymmetry between "rewrite" and "delete" is the entire bug,
 * and it is why both calls now live here instead of at spec module scope, even
 * though only the deletion was ever actually unsafe there.
 *
 * checkDistFreshness()'s refusal deliberately does NOT live here, even though the
 * previous round of review asked for it here. globalSetup is registered once in
 * playwright.config.ts and fires for EVERY invocation of that config — confirmed by
 * a throwaway probe global-setup that logged + threw unconditionally: `npm run
 * test:render:meta`, which passes the CLI filter `meta.spec.ts` and matches zero
 * pages tests, still ran it. meta.spec.ts tests the checkers against static
 * fixtures, has nothing to do with dist/, and is explicitly designed to keep running
 * while a build is broken (see its own file). Putting the freshness throw here would
 * silently reintroduce exactly that regression on every meta-only invocation. The
 * freshness check instead stays in pages.spec.ts's own beforeAll — safe to re-run
 * once per worker, unlike resetRaw, because it only reads; every worker reaches the
 * same true/false answer and nothing is destroyed by asking twice.
 *
 * Accepted trade-off: this still means running the meta gate after a page run clears
 * that page run's partials, and a subsequent build_scorecard.mjs invocation then
 * refuses with "expected N, found 0" instead of reporting the page run's real
 * numbers. Accepted deliberately rather than sniffing process.argv to suppress
 * resetRaw for meta-only invocations: (a) the documented workflow order is
 * meta-first-then-pages, so normal use never hits this; (b) the failure is loud and
 * names its own cause (found 0), never a silently wrong number; and (c) a guard
 * built on inspecting how it was invoked is exactly the kind of quiet, easily-
 * bypassed correctness mechanism this whole task exists to replace.
 */
export default function globalSetup(config: FullConfig): void {
  resetRaw();

  const targets = JSON.parse(readFileSync(resolve(here, 'targets.json'), 'utf8')) as {
    pages: { slug: string; page_type: string; corpus: boolean }[];
  };
  // config.projects.length, not a hardcoded 3 — so adding a fourth viewport project
  // widens the expected count automatically. A hardcoded number would silently
  // under-count forever the day someone adds a project, and Guard 1 would then
  // "pass" while genuinely missing a third of every run's partials.
  writeManifest(
    registry.map((c) => c.id),
    targets.pages.length * config.projects.length,
  );
}
