#!/usr/bin/env node
// npm run test:render:pages [-- <playwright args>]
//
// The page run, then the zero-examined guard — ALWAYS both. build_scorecard.mjs holds Guard 1
// (a page that wrote no partial) and Guard 2 (a check that examined zero nodes across every
// page), and for most of this harness's life it ran only when somebody remembered to type it.
// An npm `post` hook is not enough: npm skips it whenever the page run fails, and a page run
// with one blocking defect is exactly the run whose examined counts need reading.
//
// Exit code: the page run's if it failed, else the scorecard's. A FILTERED run (--grep,
// --project, --shard, --last-failed, --only-changed) writes partials for some pages only, so
// the scorecard is skipped and says why — Guard 1 would otherwise report the pages it was told
// not to run as crashed.
//
// RENDER_PAGES_RUNNER / RENDER_SCORECARD replace the two commands (tests only).
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const args = process.argv.slice(2);
const runner = process.env.RENDER_PAGES_RUNNER
  ? [process.env.RENDER_PAGES_RUNNER]
  : [resolve('node_modules/.bin/playwright'), 'test', '-c', 'tests/render/playwright.config.ts', 'pages.spec.ts'];
const scorecard = process.env.RENDER_SCORECARD ?? 'scripts/build_scorecard.mjs';
const FILTERS = ['--grep', '-g', '--grep-invert', '--project', '--shard', '--last-failed', '--only-changed'];

const pages = spawnSync(runner[0], [...runner.slice(1), ...args], { stdio: 'inherit' });
const pagesStatus = pages.status ?? 1;
if (args.some((a) => FILTERS.some((f) => a === f || a.startsWith(`${f}=`)))) {
  console.log('scorecard: skipped — a filtered run measures some pages only; run the whole suite for the zero-examined guard');
  process.exit(pagesStatus);
}
const card = spawnSync(process.execPath, [scorecard], { stdio: 'inherit' });
process.exit(pagesStatus || (card.status ?? 1));
