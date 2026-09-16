#!/usr/bin/env node
// Merges data/quality/raw/*.json (one per page+viewport) into one scorecard per page.
// Usage: node scripts/build_scorecard.mjs [--run first|recheck]
import { readdirSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

const RAW = resolve('data/quality/raw');
const OUT = resolve('data/quality/scorecards');
const runLabel = process.argv.includes('--run')
  ? process.argv[process.argv.indexOf('--run') + 1]
  : 'first';
const date = new Date().toISOString().slice(0, 10);

mkdirSync(OUT, { recursive: true });

const files = readdirSync(RAW).filter((f) => f.endsWith('.json') && f !== '_manifest.json');
let manifest = { checkIds: [], expectedPartials: 0 };
try {
  manifest = JSON.parse(readFileSync(resolve(RAW, '_manifest.json'), 'utf8'));
} catch {
  console.error('FAIL: no _manifest.json — cannot tell which checks were supposed to run.');
  process.exit(1);
}

const bySlug = new Map();
const examinedAnywhere = new Map(manifest.checkIds.map((id) => [id, 0]));
for (const file of files) {
  const p = JSON.parse(readFileSync(resolve(RAW, file), 'utf8'));
  if (!bySlug.has(p.slug)) bySlug.set(p.slug, []);
  bySlug.get(p.slug).push(p);
  for (const [checkId, n] of Object.entries(p.examined)) {
    examinedAnywhere.set(checkId, (examinedAnywhere.get(checkId) ?? 0) + n);
  }
}

// Guard 1: a page that crashed the harness writes no partial and would otherwise
// score as absent rather than as failed. "PASS in 0 pages" wearing a new costume.
if (files.length !== manifest.expectedPartials) {
  console.error(
    `FAIL: expected ${manifest.expectedPartials} partials, found ${files.length}. ` +
      `Missing results are not passes.`,
  );
  process.exit(1);
}

// Guard 2: seeded from the MANIFEST, not from the partials — a check that ran
// nowhere contributes no key to any partial and would be invisible otherwise.
const dead = [...examinedAnywhere.entries()].filter(([, n]) => n === 0).map(([id]) => id);
if (dead.length) {
  console.error(`FAIL: check(s) examined zero nodes across every page: ${dead.join(', ')}`);
  process.exit(1);
}

if (bySlug.size === 0) {
  console.error('FAIL: zero pages examined. A run over no pages is never a pass.');
  process.exit(1);
}

/** One entry per distinct checkId+reason. See the call site for why this matters. */
function dedupeOverrides(list) {
  const seen = new Map();
  for (const o of list) seen.set(`${o.checkId}\u0000${o.reason}`, o);
  return [...seen.values()];
}

let grandTotal = 0;
for (const [slug, parts] of bySlug) {
  // Two numbers, deliberately. `defects` counts ROWS — one failure mode of one check at
  // one viewport — and is the only number comparable across families. `instances` sums
  // `count` and is the magnitude. The first baseline had only the first, computed from
  // checks that disagreed about what a row was.
  const defectsByFamily = {};
  const instancesByFamily = {};
  const examined = { pages: 1, checks: 0 };
  // Per-check examined counts, summed across this page's viewports.
  //
  // Guard 2 above only proves a check examined something SOMEWHERE across the whole
  // corpus, so a check examining 500 units on one page and 0 on the other 14 passes it.
  // That is not enough to promote a check to `blocking` on the strength of "it reported
  // zero rows": zero rows from a check that examined nothing is the exact failure this
  // harness was built after (`rule.cssRules` truthy on every rule skipped every rule in
  // the document, and two CSS checks reported a clean pass having examined ZERO). Keeping
  // the per-check number in the card makes that judgement auditable after the run, instead
  // of requiring a 13-minute re-run to ask the question.
  const examinedByCheck = {};
  const details = [];
  for (const part of parts) {
    examined.checks = Math.max(examined.checks, Object.keys(part.examined).length);
    for (const [checkId, n] of Object.entries(part.examined)) {
      examinedByCheck[checkId] = (examinedByCheck[checkId] ?? 0) + n;
    }
    for (const d of part.defects) {
      defectsByFamily[d.family] = (defectsByFamily[d.family] || 0) + 1;
      instancesByFamily[d.family] = (instancesByFamily[d.family] || 0) + (d.count ?? 1);
      details.push({
        viewport: part.viewport,
        checkId: d.checkId,
        count: d.count ?? 1,
        message: d.message,
      });
    }
  }
  const total = Object.values(defectsByFamily).reduce((a, b) => a + b, 0);
  const totalInstances = Object.values(instancesByFamily).reduce((a, b) => a + b, 0);
  grandTotal += total;
  const card = {
    slug,
    date,
    page_type: parts[0].page_type,
    run: runLabel,
    harness_version: '2.0.0',
    viewports: parts.map((p) => p.viewport).sort((a, b) => a - b),
    examined,
    examined_by_check: examinedByCheck,
    defects: defectsByFamily,
    instances: instancesByFamily,
    total,
    total_instances: totalInstances,
    // Deduped. One override is DECLARED once for the run, but it rides along in every
    // partial, so flattening gave the same suppression 3x per page and 27x overall —
    // the same mixed-unit error this harness version exists to remove, reappearing in
    // the report about it. An override's magnitude is the pages it silences, not the
    // partials it was copied into.
    overrides: dedupeOverrides(parts.flatMap((p) => p.overrides ?? [])),
    details,
  };
  // Same flattening as lib/scorecard.ts: a nested slug (blog/..., available/...) would
  // otherwise name a directory that does not exist. The `slug` field inside the card
  // keeps the real slug — only the filename is flattened.
  writeFileSync(
    resolve(OUT, `${slug.replace(/\//g, '__')}-${date}.json`),
    JSON.stringify(card, null, 2),
  );
  console.log(`${String(total).padStart(3)} rows ${String(totalInstances).padStart(4)} inst  ${slug}`);
}

const allOverrides = dedupeOverrides([...bySlug.values()].flat().flatMap((p) => p.overrides ?? []));
console.log(
  `---\n${grandTotal} defect ROWS across ${bySlug.size} pages (run=${runLabel}, harness 2.0.0). ` +
    `Rows are comparable across families; instances are not.`,
);
if (allOverrides.length) {
  console.log(
    `${allOverrides.length} DISTINCT OVERRIDE(S) IN EFFECT across ${bySlug.size} pages — suppressed defects:`,
  );
  for (const o of allOverrides) console.log(`  ${o.checkId}: ${o.reason}`);
}
