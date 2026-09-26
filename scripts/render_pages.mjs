#!/usr/bin/env node
// npm run test:render:pages [-- <playwright args>] [--scorecard-run=<first|recheck>]
//
// The page run, then the zero-examined guard — ALWAYS both. build_scorecard.mjs holds Guard 1
// (a page that wrote no partial) and Guard 2 (a check that examined zero nodes across every
// page), and for most of this harness's life it ran only when somebody remembered to type it.
// An npm `post` hook is not enough: npm skips it whenever the page run fails, and a page run
// with one blocking defect is exactly the run whose examined counts need reading.
//
// Exit code: the page run's if it failed (128 + signal number if it was killed), else the
// scorecard's. The scorecard is skipped, saying why, when the run is not a full measurement:
//   - FILTERED (--grep/-g, --grep-invert, --project, --shard, --last-failed, --only-changed, or
//     any positional file/title filter): partials for some pages only, and Guard 1 would report
//     the pages it was told not to run as crashed;
//   - STOPPED EARLY (-x, --max-failures): same, for the pages after the stop;
//   - NOT A PAGE RUN (--list, --help/-h, --ui);
//   - NEVER STARTED: globalSetup rewrites data/quality/raw/_manifest.json at the start of every
//     real run; a manifest this invocation did not rewrite means the raw directory holds the
//     previous run's partials, which the scorecard would merge into a card dated today.
//     "Rewrote" is judged before/after (absent before and present after, or a different
//     mtime), never against the wall clock, which skew or a network filesystem can defeat.
//   - KILLED by a signal, or the page command could not be spawned.
//
// --scorecard-run=<label> is ours, not Playwright's: stripped, and passed on as
// `build_scorecard.mjs --run <label>` (default `first`).
//
// RENDER_PAGES_RUNNER / RENDER_SCORECARD / RENDER_RAW_DIR replace the page command, the
// scorecard script and the raw directory (tests only).
import { spawnSync } from 'node:child_process';
import { statSync } from 'node:fs';
import { constants } from 'node:os';
import { resolve } from 'node:path';

// Playwright options that take a value as the NEXT argument; that argument is not a filter.
const VALUE_FLAGS = new Set([
  '-c', '--config', '--reporter', '-j', '--workers', '--retries', '--repeat-each', '--timeout',
  '--global-timeout', '--output', '--trace', '--tsconfig', '--browser',
  '--grep', '-g', '--grep-invert', '--project', '--shard', '--max-failures',
]);
// -u / --update-snapshots take an OPTIONAL value: the next argument is theirs only if it is
// one of these modes; anything else after them is a filter like any other positional.
const OPTIONAL_VALUE_FLAGS = new Set(['-u', '--update-snapshots']);
const UPDATE_MODES = new Set(['all', 'changed', 'missing', 'none']);
const FILTERS = ['--grep', '-g', '--grep-invert', '--project', '--shard', '--last-failed', '--only-changed'];
const STOPS = ['-x', '--max-failures'];
const NOT_A_RUN = ['--list', '--help', '-h', '--ui'];

/** `--name`, `--name=v`, `-g=v`, and a short flag's attached value `-gfoo`. */
function hasFlag(args, names) {
  return args.some((a) =>
    names.some(
      (f) => a === f || a.startsWith(`${f}=`) || (/^-[a-zA-Z]$/.test(f) && a.startsWith(f) && f !== '-x' && f !== '-h'),
    ),
  );
}

/** A bare argument that is not the value of the flag before it: a file or title filter. */
function hasPositional(args) {
  for (let i = 0; i < args.length; i += 1) {
    const a = args[i];
    if (a.startsWith('-')) {
      if (VALUE_FLAGS.has(a)) i += 1;
      else if (OPTIONAL_VALUE_FLAGS.has(a) && UPDATE_MODES.has(args[i + 1])) i += 1;
      continue;
    }
    return true;
  }
  return false;
}

let label = 'first';
const args = [];
for (let i = 2; i < process.argv.length; i += 1) {
  const a = process.argv[i];
  if (a.startsWith('--scorecard-run=')) label = a.slice('--scorecard-run='.length);
  else if (a === '--scorecard-run') label = process.argv[(i += 1)];
  else args.push(a);
}

const runner = process.env.RENDER_PAGES_RUNNER
  ? [process.env.RENDER_PAGES_RUNNER]
  : [resolve('node_modules/.bin/playwright'), 'test', '-c', 'tests/render/playwright.config.ts', 'pages.spec.ts'];
const scorecard = process.env.RENDER_SCORECARD ?? 'scripts/build_scorecard.mjs';
const manifest = resolve(process.env.RENDER_RAW_DIR ?? 'data/quality/raw', '_manifest.json');

const skip = (why, code) => {
  console.log(`scorecard: skipped — ${why}`);
  process.exit(code);
};

/** The manifest's mtime, or null when it does not exist. */
const manifestMtime = () => {
  try {
    return statSync(manifest).mtimeMs;
  } catch {
    return null;
  }
};

const before = manifestMtime();
const pages = spawnSync(runner[0], [...runner.slice(1), ...args], { stdio: 'inherit' });
if (pages.error) {
  console.error(`render_pages: could not run the page command ${runner[0]}: ${pages.error.message}`);
  skip('the page command did not run', 1);
}
if (pages.signal) {
  console.error(`render_pages: the page run was killed by ${pages.signal}`);
  skip(`the page run was killed by ${pages.signal}`, 128 + (constants.signals[pages.signal] ?? 0));
}
const pagesStatus = pages.status ?? 1;

if (hasFlag(args, NOT_A_RUN)) skip('not a page run (--list/--help/--ui)', pagesStatus);
if (hasFlag(args, STOPS)) skip('stopped early — not a full run (-x/--max-failures)', pagesStatus);
if (hasFlag(args, FILTERS) || hasPositional(args)) {
  skip('a filtered run measures some pages only; run the whole suite for the zero-examined guard', pagesStatus);
}

const after = manifestMtime();
if (after === null || after === before) skip('the page run never started (no fresh manifest)', pagesStatus || 1);

const card = spawnSync(process.execPath, [scorecard, '--run', label], { stdio: 'inherit' });
if (card.error) {
  console.error(`render_pages: could not run ${scorecard}: ${card.error.message}`);
  process.exit(pagesStatus || 1);
}
process.exit(pagesStatus || (card.status ?? 1));
