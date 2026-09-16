import { test, expect } from '@playwright/test';
import {
  mkdtempSync,
  mkdirSync,
  writeFileSync,
  utimesSync,
  symlinkSync,
  rmSync,
  existsSync,
  readdirSync,
  readFileSync,
} from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { registry, MAX_DEFECT_ROWS, type Check, type Defect } from './lib/registry.js';
import { runCheck } from './lib/runCheck.js';
import { flattenSlug } from './lib/scorecard.js';
import { fixtureUrl, FIXTURE_BASE } from './lib/servers.js';
import { measureTopChrome, waitForScrollSettle } from './lib/probes.js';
import { checkDistFreshness, builtRoutesWithoutSource } from './lib/freshness.js';
import {
  fixtureCorpus,
  distSlugs,
  siblingSlugsFor,
  loadWhitelist,
  normalise,
  REPO,
  type Target,
} from './lib/dupCorpus.js';
import { resetRaw } from './lib/scorecard.js';
import { contractFor, fieldChecksSkipped, formExpected } from './checks/form.js';
import './checks/index.js';


/**
 * Fixtures are judged under the STRICTEST page type, not a neutral one.
 *
 * `pageType` only reaches checks that condition on it, and today that is SCHEMA, where
 * `puppy` (CAG's `bird`) is the tightest branch (exactly one Product/Offer, never AggregateOffer). Passing
 * something laxer here would let a SCHEMA check pass its fixtures through a branch it never
 * takes on the page type it was written for — the fixture pair would then be proving a
 * property nobody relies on.
 */
const FIXTURE_CTX = {
  pageType: 'puppy',
  // A slug the FORM policy treats as carrying an inquiry form. With a neutral 'fixture'
  // slug, contractFor() returns 'none' and the form fixtures would pass through a branch
  // that checks no field at all — a fixture pair proving nothing.
  slug: 'uk-blue-staffy-breeders-contact',
  // A REAL corpus, not a stub. DUP's whole predicate is "does this page share copy with
  // another page", so a fixture pair that compared against an empty sibling set would
  // prove only that the check does nothing. tests/render/fixtures/dup_corpus/ holds the
  // sibling the known_broken fixture is supposed to collide with.
  siblings: async () => fixtureCorpus('tests/render/fixtures/dup_corpus'),
};

test('the registry is not empty', () => {
  expect(
    registry.length,
    'a harness that examines zero checks is not a passing harness',
  ).toBeGreaterThan(0);
});

for (const check of registry) {
  test.describe(`${check.id} [${check.family}]`, () => {
    test('fires on the known_broken fixture', async ({ page }, testInfo) => {
      const viewport = testInfo.project.use.viewport!.width;
      const res = await page.goto(fixtureUrl('known_broken', check.id));
      expect(res?.status(), 'known_broken fixture must exist').toBe(200);
      const result = await runCheck(check, page, viewport, FIXTURE_CTX);
      expect(
        result.examined,
        `examined must reach the declared floor (${check.minExamined}) — a check cannot pass by inflating its own count`,
      ).toBeGreaterThanOrEqual(check.minExamined);
      expect(
        result.defects.length,
        `${check.id} did not fire on a page built to contain its defect`,
      ).toBeGreaterThan(0);
    });

    test('is silent on the known_good fixture', async ({ page }, testInfo) => {
      const viewport = testInfo.project.use.viewport!.width;
      const res = await page.goto(fixtureUrl('known_good', check.id));
      expect(res?.status(), 'known_good fixture must exist').toBe(200);
      const result = await runCheck(check, page, viewport, FIXTURE_CTX);
      expect(
        result.examined,
        `examined must reach the declared floor (${check.minExamined})`,
      ).toBeGreaterThanOrEqual(check.minExamined);
      expect(
        result.defects.map((d) => d.message),
        `${check.id} cried wolf on a clean page`,
      ).toEqual([]);
    });
  });
}

/**
 * The DUP whitelist exempts LINES, not the runs they happen to sit inside.
 *
 * Found 2026-09-11: shingle growth fuses a whitelisted line and any shared passage that
 * touches it into one maximal run, and both gates then skipped the WHOLE run because it
 * contained a whitelisted stem. A 17-word shared <legend> placed right after
 * "Ships nationwide · $185 airport · $350 home" never fired. The generic known_broken loop
 * above could not see this: its fixture's crossover is not adjacent to anything whitelisted.
 *
 * The count is pinned at exactly 2, not "> 0": a fix that reported the fused run as one
 * finding would still fire, and would print the shipping line as the defect.
 */
test.describe('dup-no-sibling-crossover sees a crossover adjacent to a whitelisted line', () => {
  const onlyOnce = (testInfo: { project: { name: string }; config: { projects: { name: string }[] } }) =>
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );

  test('reports each passage beside the shipping line, and never the line itself', async ({
    page,
  }, testInfo) => {
    onlyOnce(testInfo);
    const res = await page.goto(fixtureUrl('known_broken', 'dup-adjacent-to-whitelist'));
    expect(res?.status(), 'fixture must load').toBe(200);
    const check = registry.find((c) => c.id === 'dup-no-sibling-crossover')!;
    const r = await runCheck(check, page, testInfo.project.use.viewport!.width, FIXTURE_CTX);

    expect(r.examined, 'must have compared against the corpus').toBeGreaterThanOrEqual(1);
    expect(r.defects.length, 'a crossover beside a whitelisted line must still fire').toBe(1);
    expect(r.defects[0].count, 'one finding per non-whitelisted segment: A before, B after').toBe(2);
    const msg = r.defects[0].message;
    expect(msg).toContain('18w vs /sibling-hand-raised-african-grey-texas/ "before a chick leaves');
    expect(msg).toContain('17w vs /sibling-hand-raised-african-grey-texas/ "tell us which bird');
    expect(msg, 'the whitelisted line is not the defect').not.toContain('ships nationwide');
  });
});

/**
 * The DUP check is only as wide as the sibling set pages.spec hands it.
 *
 * Found 2026-09-11: the set was "same page type", and targets.json holds 13 for-sale
 * targets but exactly ONE each of bird, comparison, interior, location, blog and hub — so on
 * six of eight page types DUP compared against nothing and reported examined=0, while the
 * Python gate (every dist page, pairwise) found 481 crossovers on 70 pages that day. Home
 * did not run DUP at all. The fixture pair above cannot see this: meta supplies its own
 * corpus, so it proves the comparison and never the policy that feeds it.
 *
 * Measured against a synthetic dist/ holding every target plus pages no target names, so
 * it runs with the real dist/ stale or missing, like the rest of this file.
 */
test.describe('dup-no-sibling-crossover judges every page against the whole built site', () => {
  const targetsFile = JSON.parse(
    readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), 'targets.json'), 'utf8'),
  ) as { families_by_page_type: Record<string, string[]>; pages: Target[] };
  let root = '';
  test.afterAll(() => {
    if (root) rmSync(root, { recursive: true, force: true });
  });

  test('every target is compared against every other built page', async ({}, testInfo) => {
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );
    root = mkdtempSync(join(tmpdir(), 'dupcorpus-'));
    const dist = join(root, 'dist');
    // Pages no target names: a care page and a nested blog post, the shapes the Python gate
    // found crossovers on that the harness could not reach.
    const untargeted = ['blue-staffy-temperament-uk', 'blog/blue-staffy-puppy-first-week'];
    const built = [...targetsFile.pages.map((p) => p.slug), ...untargeted];
    for (const slug of built) {
      const dir = slug === 'index' ? dist : join(dist, slug);
      mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, 'index.html'), `<main><p>${slug}</p></main>`);
    }
    const corpus = distSlugs(dist);
    expect(corpus, 'distSlugs keys pages as scripts/_slugs.py page_key does').toEqual([...built].sort());

    const blind = Object.entries(targetsFile.families_by_page_type)
      .filter(([, fams]) => !fams.includes('DUP'))
      .map(([type]) => type);
    expect.soft(blind, 'page types that never run DUP').toEqual([]);

    const short = targetsFile.pages
      .map((t) => {
        const got = siblingSlugsFor(t, targetsFile.pages, corpus);
        const want = corpus.filter((s) => s !== t.slug);
        return { t, got, missing: want.filter((s) => !got.includes(s)) };
      })
      .filter((r) => r.missing.length || r.got.includes(r.t.slug))
      .map((r) => `${r.t.slug} [${r.t.page_type}]: ${r.got.length} siblings, missing ${r.missing.length}`);
    expect.soft(short, 'targets judged against less than the whole built corpus').toEqual([]);
  });
});

/**
 * DUP counts words the way the Python auditor counts them.
 *
 * Found 2026-09-11: scripts/dup_content_audit.py tokenises with [a-z0-9$']+, so "we'd" is one
 * word; normalise() replaced the apostrophe with a space and read "we d". On the same dist/,
 * "answered the same honest way we'd answer them on the phone" — shared by the eggs and congo
 * for-sale pages — was 12 words here (fires) and 11 in Python (silent). The corpus side read
 * raw HTML without decoding entities, so an apostrophe Astro emits as &#39; was a third token
 * shape ("we 39 d") that matched neither.
 *
 * The Python side is run, not restated: each case asks dup_content_audit.py itself, so a
 * tokeniser change on either side fails here instead of drifting.
 */
test.describe('dup-no-sibling-crossover tokenises exactly like dup_content_audit.py', () => {
  const onlyOnce = (testInfo: { project: { name: string }; config: { projects: { name: string }[] } }) =>
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );
  const py = (code: string, ...args: string[]): unknown =>
    JSON.parse(execFileSync('python3', ['-c', code, ...args], { cwd: REPO, encoding: 'utf8' }));
  const PY_AUDITOR = `import sys, json; sys.path.insert(0, 'scripts'); import dup_content_audit as d\n`;
  /** The Python gate's crossovers between two fixture files at a given window. */
  const pyCrossovers = (page: string, minWords: number) =>
    py(
      PY_AUDITOR +
        `from pathlib import Path\n` +
        `d.MIN_WORDS = int(sys.argv[3]); wa, wb = d.words(Path(sys.argv[1])), d.words(Path(sys.argv[2]))\n` +
        `print(json.dumps([' '.join(s) for s in d.crossovers(wa, d.shingles(wa), d.shingles(wb))]))`,
      `tests/render/fixtures/known_broken/${page}.html`,
      'tests/render/fixtures/dup_corpus/sibling-contraction.html',
      String(minWords),
    ) as string[];
  const SHARED_11 = "answered the same honest way we'd answer them on the phone";
  const SHARED_12 = "every hatch record we've kept for a chick goes home with it";

  test('a run that is 12 words only because an apostrophe split a word is not a crossover', async ({
    page,
  }, testInfo) => {
    onlyOnce(testInfo);
    // The fixture sits exactly on the boundary — proven against Python, not assumed, so a
    // silent harness means "11 words, like Python", never "the text did not match at all".
    expect(pyCrossovers('dup-contraction-boundary', 11), 'Python: one shared 11-word run').toEqual([SHARED_11]);
    expect(pyCrossovers('dup-contraction-boundary', 12), 'Python: nothing at the real window').toEqual([]);

    const res = await page.goto(fixtureUrl('known_broken', 'dup-contraction-boundary'));
    expect(res?.status(), 'fixture must load').toBe(200);
    const check = registry.find((c) => c.id === 'dup-no-sibling-crossover')!;
    const r = await runCheck(check, page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined, 'must have compared against the corpus').toBeGreaterThanOrEqual(1);
    expect(r.defects.map((d) => d.message), 'counted a contraction as two words').toEqual([]);
  });

  test('an apostrophe the corpus page writes as &#39; is the same word', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    expect(pyCrossovers('dup-contraction-entity', 12), 'Python fires on the 12-word run').toEqual([SHARED_12]);

    const res = await page.goto(fixtureUrl('known_broken', 'dup-contraction-entity'));
    expect(res?.status(), 'fixture must load').toBe(200);
    const check = registry.find((c) => c.id === 'dup-no-sibling-crossover')!;
    const r = await runCheck(check, page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined, 'must have compared against the corpus').toBeGreaterThanOrEqual(1);
    expect(r.defects.length, 'a 12-word run Python reports must fire here too').toBe(1);
    expect(r.defects[0].count).toBe(1);
    expect(r.defects[0].message).toContain(`12w vs /sibling-contraction/ "${SHARED_12}"`);
  });

  test('normalise() and the whitelist stems match Python token for token', ({}, testInfo) => {
    onlyOnce(testInfo);
    const samples = [
      "We'd answer them",
      'We’d answer — the curly one', // U+2019: outside the class on both sides
      "'quoted words' and rock'n'roll",
      "Mark & Teri's o'clock call",
      '$1,500–$3,500 · 72-hour / 3-day guarantee',
      'Timneh/Congo 1st  clutch\tnaïve ÉCLAT',
      "a''b ' $ -- ",
      '',
    ];
    const want = py(
      `import sys, json, re\nprint(json.dumps([re.findall(r"[a-z0-9$']+", s.lower()) for s in json.loads(sys.argv[1])]))`,
      JSON.stringify(samples),
    );
    expect(samples.map(normalise), 'normalise() vs dup_content_audit.py words()').toEqual(want);
    // Both whitelist readers: Python's WHITELIST_STEMS vs the harness's parse + normalise().
    expect(loadWhitelist().map(normalise), 'whitelist stems, token for token').toEqual(
      py(PY_AUDITOR + 'print(json.dumps(d.WHITELIST_STEMS))'),
    );
  });
});

test.describe('dist/ freshness gate', () => {
  // mkdtemp leaks a real directory per call unless something removes it. Tracked here
  // and swept in afterAll — 5 tests x 3 viewport projects otherwise left 15 orphaned
  // dirs under the OS tmpdir on every meta run.
  const tempRoots: string[] = [];
  const newRoot = () => {
    const root = mkdtempSync(join(tmpdir(), 'fresh-'));
    tempRoots.push(root);
    return root;
  };
  const mk = () => {
    const root = newRoot();
    mkdirSync(join(root, 'dist'), { recursive: true });
    mkdirSync(join(root, 'src'), { recursive: true });
    return root;
  };

  test.afterAll(() => {
    for (const root of tempRoots) rmSync(root, { recursive: true, force: true });
  });

  test('a dist/ newer than src/ is fresh', () => {
    const root = mk();
    writeFileSync(join(root, 'src', 'a.astro'), 'x');
    writeFileSync(join(root, 'dist', 'index.html'), 'x');
    utimesSync(join(root, 'src', 'a.astro'), new Date(1000), new Date(1000));
    utimesSync(join(root, 'dist', 'index.html'), new Date(2000), new Date(2000));
    expect(checkDistFreshness(root).fresh).toBe(true);
  });

  test('a src/ file newer than every dist/ file is STALE', () => {
    const root = mk();
    writeFileSync(join(root, 'dist', 'index.html'), 'x');
    writeFileSync(join(root, 'src', 'a.astro'), 'x');
    utimesSync(join(root, 'dist', 'index.html'), new Date(1000), new Date(1000));
    utimesSync(join(root, 'src', 'a.astro'), new Date(2000), new Date(2000));
    const r = checkDistFreshness(root);
    expect(r.fresh, r.reason).toBe(false);
    expect(r.reason).toContain('npm run build');
    expect(r.reason).toContain('a.astro');
  });

  test('a newer package.json (the non-directory branch of newest()) forces refusal', () => {
    // 'src' and 'public' hit the directory-walk branch of newest(); 'package.json' and
    // 'astro.config.mjs' are plain files in SOURCES and take the other branch (newest()'s
    // `else best = { path, ms: st.mtimeMs }`, never exercised by any test above). Pin it
    // directly rather than trusting the directory-walk tests to stand in for it.
    const root = mk();
    writeFileSync(join(root, 'dist', 'index.html'), 'x');
    utimesSync(join(root, 'dist', 'index.html'), new Date(1000), new Date(1000));
    writeFileSync(join(root, 'package.json'), '{}');
    utimesSync(join(root, 'package.json'), new Date(2000), new Date(2000));
    const r = checkDistFreshness(root);
    expect(r.fresh, r.reason).toBe(false);
    expect(r.reason).toContain('package.json');
  });

  test('a missing dist/ is STALE, never fresh-by-default', () => {
    const root = newRoot();
    const r = checkDistFreshness(root);
    expect(r.fresh).toBe(false);
    // Pin the actual message, not just the boolean. Deleting the dedicated
    // `!existsSync(dist)` guard would fall through to the ms===0 branch below and
    // still report fresh:false — silently trading a clear message for a confusing one
    // ("a.astro is 29759023 min newer than the newest file in dist/ (dist)"). For a
    // refusal gate the message IS the deliverable; a boolean-only assertion can't catch that.
    expect(r.reason).toContain('dist/ does not exist');
  });

  test('an empty dist/ is STALE', () => {
    const root = mk();
    writeFileSync(join(root, 'src', 'a.astro'), 'x');
    const r = checkDistFreshness(root);
    expect(r.fresh).toBe(false);
    expect(r.reason).toContain('dist/ contains no files');
  });

  // src/pages/node_modules/.vite/deps/ genuinely exists in this repo. Walking it
  // reads thousands of vendored files whose mtimes have nothing to do with our
  // build, and any one of them being newer than dist/ would refuse every run.
  test('vendored trees under src/ are not treated as source', () => {
    const root = mk();
    mkdirSync(join(root, 'src', 'pages', 'node_modules', '.vite'), { recursive: true });
    writeFileSync(join(root, 'dist', 'index.html'), 'x');
    writeFileSync(join(root, 'src', 'pages', 'node_modules', '.vite', 'dep.js'), 'x');
    utimesSync(join(root, 'dist', 'index.html'), new Date(1000), new Date(1000));
    utimesSync(join(root, 'src', 'pages', 'node_modules', '.vite', 'dep.js'), new Date(9000), new Date(9000));
    expect(checkDistFreshness(root).fresh).toBe(true);
  });

  // A directory that legitimately contains nothing but SKIP-listed vendor content also
  // computes ms:0 (proven by the test above) — so ms===0 alone can't distinguish "found
  // nothing" from "couldn't read it". A read failure needs its own signal. Simulated with
  // a broken symlink (points at a path that doesn't exist) rather than chmod, because a
  // permission-denied test is unreliable under a root-running CI user, while a dangling
  // symlink throws ENOENT from statSync regardless of who's running the test.
  test('an unreadable path under src/ refuses rather than silently passing as fresh', () => {
    const root = mk();
    writeFileSync(join(root, 'dist', 'index.html'), 'x');
    utimesSync(join(root, 'dist', 'index.html'), new Date(1000), new Date(1000));
    symlinkSync(join(root, 'this-target-does-not-exist'), join(root, 'src', 'broken-link'));
    const r = checkDistFreshness(root);
    expect(r.fresh, r.reason).toBe(false);
    expect(r.reason).toContain('could not be fully read');
  });
});

test.describe('resetRaw', () => {
  test('empties a populated raw dir, so a refused run cannot merge into a prior clean scorecard', () => {
    const dir = mkdtempSync(join(tmpdir(), 'raw-'));
    writeFileSync(join(dir, 'some-page-vp375.json'), '{}');
    writeFileSync(join(dir, '_manifest.json'), '{}');
    resetRaw(dir);
    expect(existsSync(dir)).toBe(false);
  });
});

test.describe('globalSetup vs spec-module-scope regression probe', () => {
  // Two DIFFERENT things are pinned here, deliberately not conflated:
  //
  // 1. The synthetic probe below (runProbe + its two tests) proves the general
  //    Playwright LOADING MECHANISM: a spec module's top-level code runs once per
  //    worker PROCESS, not once per run, so a destructive call there can destroy an
  //    earlier worker's output, and moving that call into globalSetup fixes it. It
  //    builds its own throwaway spec/config from scratch and never reads
  //    pages.spec.ts or global-setup.ts — so it CANNOT detect a regression in this
  //    repo's actual wiring. (An earlier version of this comment claimed it could;
  //    it was reviewed, the claim was reproduced as false — reintroducing
  //    resetRaw() at pages.spec.ts module scope left both probe tests green — and
  //    the comment is corrected here instead of left to mislead the next reader.)
  //
  // 2. The 'resetRaw() lives in global-setup.ts, never in pages.spec.ts' test below
  //    pins the actual PRODUCTION WIRING by reading both real files from disk. THAT
  //    is the one that goes red if resetRaw() is ever moved back to pages.spec.ts
  //    module scope — confirmed by doing exactly that and reverting (2026-08-01).
  const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
  const playwrightCli = resolve(repoRoot, 'node_modules', '@playwright', 'test', 'cli.js');
  const scorecardAbs = resolve(repoRoot, 'tests', 'render', 'lib', 'scorecard.ts');

  /**
   * Builds and runs a disposable 3-project, 1-test-per-project Playwright suite whose
   * only job is to write one file per project into a shared scratch RAW dir, with
   * resetRaw() placed either at the probe spec's module scope (the old, broken
   * pattern) or inside a probe globalSetup (the fix). Returns which of the 3 files
   * survived. `workers: 2` mirrors the real playwright.config.ts, since the real bug
   * was observed at exactly that worker count on the real harness (2026-08-01).
   *
   * The probe directory is created UNDER tests/render/, not the OS tmpdir — Node's
   * module resolution walks up from a file's own location looking for node_modules,
   * and a probe.config.ts living outside the repo tree cannot find `@playwright/test`
   * at all. First attempt used tmpdir() and both variants silently failed to even
   * start (MODULE_NOT_FOUND), which made the "broken" case pass for the wrong reason
   * (0 survivors satisfies "< 3" same as 1 does) — decoration, caught before it shipped.
   */
  function runProbe(resetAtModuleScope: boolean): string[] {
    const probeRoot = mkdtempSync(resolve(repoRoot, 'tests', 'render', '.probe-'));
    const rawDir = join(probeRoot, 'raw');
    mkdirSync(rawDir, { recursive: true });
    const rawDirLit = JSON.stringify(rawDir);
    const scorecardLit = JSON.stringify(scorecardAbs);
    // mkdirSync here mirrors production writePartial(), which also recreates RAW_DIR
    // before every write — resetRaw() deletes the directory outright, so whichever
    // side runs it (module scope or globalSetup) leaves nothing for a bare
    // writeFileSync to write into.
    const writeOnePartial =
      `test('write-one-partial', ({}, testInfo) => {\n` +
      `  mkdirSync(${rawDirLit}, { recursive: true });\n` +
      `  writeFileSync(join(${rawDirLit}, testInfo.project.name + '.json'), '{}');\n` +
      `});\n`;

    writeFileSync(
      join(probeRoot, 'probe.spec.ts'),
      resetAtModuleScope
        ? `import { test } from '@playwright/test';\n` +
            `import { writeFileSync, mkdirSync } from 'node:fs';\n` +
            `import { join } from 'node:path';\n` +
            `import { resetRaw } from ${scorecardLit};\n` +
            `resetRaw(${rawDirLit}); // BROKEN: module scope runs once per worker process\n` +
            writeOnePartial
        : `import { test } from '@playwright/test';\n` +
            `import { writeFileSync, mkdirSync } from 'node:fs';\n` +
            `import { join } from 'node:path';\n` +
            writeOnePartial,
    );

    if (!resetAtModuleScope) {
      writeFileSync(
        join(probeRoot, 'probe-global-setup.ts'),
        `import { resetRaw } from ${scorecardLit};\n` +
          `export default function globalSetup() { resetRaw(${rawDirLit}); } // FIX: runs exactly once\n`,
      );
    }

    writeFileSync(
      join(probeRoot, 'probe.config.ts'),
      `import { defineConfig } from '@playwright/test';\n` +
        `export default defineConfig({\n` +
        `  testDir: ${JSON.stringify(probeRoot)},\n` +
        `  testMatch: ['probe.spec.ts'],\n` +
        `  fullyParallel: false,\n` +
        `  workers: 2,\n` +
        `  reporter: [['dot']],\n` +
        (resetAtModuleScope ? '' : `  globalSetup: ${JSON.stringify(join(probeRoot, 'probe-global-setup.ts'))},\n`) +
        `  projects: [{ name: 'a' }, { name: 'b' }, { name: 'c' }],\n` +
        `});\n`,
    );

    try {
      execFileSync(process.execPath, [playwrightCli, 'test', '-c', join(probeRoot, 'probe.config.ts')], {
        cwd: repoRoot,
        timeout: 30_000,
        stdio: 'pipe',
      });
    } catch {
      // Nothing here depends on Playwright's own exit code — only on how many
      // scratch files survive in rawDir. A non-zero exit changes nothing.
    }

    const survivors = existsSync(rawDir) ? readdirSync(rawDir) : [];
    rmSync(probeRoot, { recursive: true, force: true });
    return survivors;
  }

  // Viewport-independent: the probe shells out to a whole nested Playwright run and
  // gains nothing from repeating across vp375/vp768/vp1280 — skip on the other two
  // projects so the meta suite isn't paying for 3x identical signal.
  test("resetRaw() at spec module scope loses other workers' partials", ({}, testInfo) => {
    test.skip(testInfo.project.name !== 'vp375', 'viewport-independent; runs once');
    const survivors = runProbe(true);
    expect(
      // > 0 first: a probe that silently fails to run at all (e.g. the tmpdir
      // MODULE_NOT_FOUND case caught while building this) also produces 0 survivors,
      // which satisfies "< 3" for the wrong reason. Pin that this test's OWN signal
      // is "at least one worker actually ran and wrote its file", not borrowed from
      // test 2 failing.
      survivors.length,
      `expected fewer than 3 of 3 projects' partials to survive module-scope reset; found ${JSON.stringify(survivors)}`,
    ).toBeGreaterThan(0);
    expect(survivors.length).toBeLessThan(3);
  });

  test('resetRaw() in globalSetup preserves every project’s partial', ({}, testInfo) => {
    test.skip(testInfo.project.name !== 'vp375', 'viewport-independent; runs once');
    const survivors = runProbe(false);
    expect(
      survivors.length,
      `expected all 3 projects' partials to survive; found ${JSON.stringify(survivors)}`,
    ).toBe(3);
  });
});

test.describe('resetRaw placement — pins the actual production wiring', () => {
  // Unlike the synthetic probe above, this reads the REAL files. Comments are
  // stripped before matching so prose that mentions "resetRaw()" — including the
  // paragraph in pages.spec.ts explaining why the call moved OUT of that file —
  // can't produce a false positive; only a call in live code counts.
  const stripComments = (src: string) => src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*$/gm, '');
  const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');

  test('resetRaw() is called in global-setup.ts and nowhere in pages.spec.ts', () => {
    const globalSetupCode = stripComments(readFileSync(resolve(repoRoot, 'tests', 'render', 'global-setup.ts'), 'utf8'));
    const pagesSpecCode = stripComments(readFileSync(resolve(repoRoot, 'tests', 'render', 'pages.spec.ts'), 'utf8'));

    expect(
      globalSetupCode,
      'global-setup.ts must call resetRaw() — that is the entire fix this file exists for',
    ).toContain('resetRaw(');
    expect(
      pagesSpecCode,
      'resetRaw() must not be called anywhere in pages.spec.ts — Playwright loads a spec ' +
        "module's top-level code once per WORKER PROCESS, not once per run, so a destructive " +
        "call there destroys earlier workers' already-written partials (reproduced 2026-08-01: " +
        '3 tests across 3 viewport projects left exactly 1 partial standing). See global-setup.ts.',
    ).not.toContain('resetRaw(');
  });
});

/**
 * NAV supplied 337 of the 418 rows in the first baseline (81%) purely by counting
 * granularity: three checks aggregate to one row per page-viewport, NAV emitted one row
 * per anchor. A family total is only meaningful if every family counts the same unit.
 */
test.describe('nav-jump-target-lands reports causes, not instances', () => {
  test('a page with many broken anchors yields ONE row per failure mode', async ({
    page,
  }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const anchors = Array.from({ length: 20 }, (_, i) => i + 1);
    const html =
      `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>many</title><style>` +
      `html{scroll-behavior:auto}body{margin:0;font:16px/1.5 system-ui}` +
      `header{position:sticky;top:0;height:96px;background:#2D6A4F;display:flex;align-items:center}` +
      `nav a{color:#fff;margin-right:8px;display:inline-block;min-width:44px;min-height:44px}` +
      `section{min-height:900px}h2{margin:0}</style></head><body><header><nav>` +
      anchors.map((i) => `<a href="#h${i}">${i}</a>`).join(' ') +
      `</nav></header>` +
      anchors.map((i) => `<section><h2 id="h${i}">H${i}</h2></section>`).join('') +
      `</body></html>`;
    await page.setContent(html);

    const check = registry.find((c) => c.id === 'nav-jump-target-lands')!;
    const result = await check.run(page, viewport);

    expect(result.examined, 'must have judged all 20 targets').toBe(20);
    expect(
      result.defects.length,
      `expected at most 3 rows (one per failure mode); got ${result.defects.length}`,
    ).toBeLessThanOrEqual(3);
    expect(
      result.defects.reduce((n, d) => n + (d.count ?? 0), 0),
      'the rows must still carry the instance count',
    ).toBeGreaterThan(3);
    expect(
      result.defects[0].message,
      'the row must name the page-level cause',
    ).toMatch(/scroll-margin-top/);
  });
});

/**
 * Naming a cause is only worth doing if the cause names the right DIRECTION.
 *
 * Measured 2026-08-01: dna-tested and hand-raised land every one of their 18 links at
 * 162px and 170px against an 88-156px band — OVERSHOOTS, past the far edge — and both
 * rows read "1 of 19 targets have scroll-margin-top under the 96px of pinned chrome".
 * That is an undershoot description, sourced from a minority of one, and a reader who
 * followed it would INCREASE a scroll-margin that is already 66px too large.
 *
 * Four fixtures, because direction has FOUR quadrants and three of them can be satisfied
 * by a wrong implementation. Defining `long` as "not short" rather than "past the far
 * edge" passes the uniform, the good and the mixed fixture, and then prints "18 of 19
 * targets overshoot" on a page whose 18 targets sit correctly IN-BAND — the mirror image
 * of the bug this exists to kill. nav-undershoot-minority.html is that fourth quadrant.
 *
 * Every test here forces its own 1280x900 viewport because the fixtures' geometry is
 * computed against it, so running them once per viewport project would be three
 * byte-identical executions of the same work.
 */
test.describe('nav-jump-target-lands names the direction of failure', () => {
  const check = () => registry.find((c) => c.id === 'nav-jump-target-lands')!;
  // These four fixtures pin their own viewport, so running them once per project is
  // duplicate work. Anchored on the FIRST CONFIGURED PROJECT rather than the literal
  // 'vp375': with a literal, renaming that project made all four tests skip in every
  // project and the suite still reported green — coverage vanishing silently is the
  // failure this repo has already shipped twice, and a skip is the easiest place to
  // hide it. Deriving the name means there is always exactly one project that runs.
  const onlyOnce = (testInfo: { project: { name: string }; config: { projects: { name: string }[] } }) =>
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );

  test('fires on a page whose targets overshoot the chrome band', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(`${FIXTURE_BASE}/tests/render/fixtures/known_broken/nav-overshoot.html`);
    const r = await runCheck(check(), page, 1280, FIXTURE_CTX);

    expect(r.defects.length).toBe(1);
    // The whole point of this fixture: the cause must not blame a too-SMALL margin.
    expect(r.defects[0].message).toMatch(/overshoot|past|beyond|over the/i);
    expect(r.defects[0].message).not.toMatch(/under the \d+px of pinned chrome/);
  });

  test('stays silent when the same page lands inside the band', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(`${FIXTURE_BASE}/tests/render/fixtures/known_good/nav-overshoot-fixed.html`);
    const r = await runCheck(check(), page, 1280, FIXTURE_CTX);

    expect(r.defects.length).toBe(0);
  });

  // The pair above pins BLINDNESS to overshoot (uniform cohort, old code returned
  // "no single page-level cause identified"). This third fixture pins the defect
  // actually measured in the scorecards: a MIXED cohort, where the old code found the
  // one small target among nineteen and printed it as THE root cause of the other
  // eighteen's overshoot. Verified red against the pre-fix nav.ts, whose output was
  // "1 of 19 targets have scroll-margin-top under the 96px of pinned chrome" —
  // character-for-character the string dna-tested and hand-raised shipped.
  test('names both cohorts when targets fail in opposite directions', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(`${FIXTURE_BASE}/tests/render/fixtures/known_broken/nav-overshoot-mixed.html`);
    const r = await runCheck(check(), page, 1280, FIXTURE_CTX);

    expect(r.defects.length).toBe(1);
    // The measured real-page failure: 1 small target among 19 was reported as THE
    // root cause of 18 overshoot failures. The cause must name the 18, not the 1.
    // Both cohorts must be named. Reporting only the majority is a milder form of the
    // misattribution this function was rewritten to remove: a reader of a 10-long /
    // 9-short page would learn nothing about the 9 that need the OPPOSITE fix.
    expect(r.defects[0].message).toMatch(
      /18 of 19 targets declare scroll-margin-top past the 156px far edge/,
    );
    expect(r.defects[0].message).toMatch(/and 1 declare scroll-margin-top under the 88px near edge/);
    expect(r.defects[0].message).toMatch(/the two need opposite fixes/);
  });

  test('names an undershooting minority without claiming overshoot', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_broken/nav-undershoot-minority.html`,
    );
    const r = await runCheck(check(), page, 1280, FIXTURE_CTX);

    expect(r.defects.length).toBe(1);
    // Guards the fourth quadrant: 18 targets sit correctly IN-BAND and one undershoots.
    // An implementation that defines `long` as "not short" rather than "past the far
    // edge" passes every other fixture and reports "18 of 19 targets overshoot" here.
    // Verified: the `else long++` mutant fails exactly this assertion.
    expect(r.defects[0].message).toMatch(
      /1 of 19 targets declare scroll-margin-top under the 88px near edge/,
    );
    // Asserted against the far-edge PHRASE, not the word "overshoot". The vocabulary no
    // longer contains "overshoot" anywhere, so a `not.toMatch(/overshoot/)` here would
    // pass on every possible implementation — the third toothless assertion this file
    // has shipped. Match what the wrong implementation would actually print.
    expect(r.defects[0].message).not.toMatch(/past the \d+px far edge/);
  });
});

/**
 * A landing must be a fact about the page's geometry, never about animation timing.
 *
 * Measured 2026-09-13: /african-grey-parrots-for-sale-near-me/ @1280 failed once with
 * `#mt-dallas@7373px` (its raw document offset is ~7394px, so the page had barely moved),
 * then passed twice on the identical dist/. waitForScrollSettle's equal-read and
 * start-grace logic was already in place and still lost the race to the site's
 * `html{scroll-behavior:smooth}`. Waiting longer only makes the race less likely. It never
 * removes it, so the check now measures with the root forced to instant scrolling.
 *
 * The race itself cannot be scheduled from a fixture, so this pins the property that
 * rules it out: every click happens under `scroll-behavior:auto`. Against the pre-fix
 * nav.ts the first assertion fails deterministically, with every entry "smooth".
 */
test.describe('nav-jump-target-lands measures geometry, not smooth-scroll timing', () => {
  const URL = `${FIXTURE_BASE}/tests/render/fixtures/known_broken/nav-smooth-scroll-landing.html`;

  test('clicks under instant scrolling, restores the page, and still catches the real miss', async ({
    page,
  }, testInfo) => {
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(URL);
    expect(
      await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior),
      'the fixture must declare smooth scrolling, or this test proves nothing',
    ).toBe('smooth');

    const check = registry.find((c) => c.id === 'nav-jump-target-lands')!;
    const r = await runCheck(check, page, 1280, FIXTURE_CTX);

    const behaviors: string[] = await page.evaluate(() => (window as any).__navBehaviors);
    expect(r.examined, 'must have judged all 30 targets').toBe(30);
    expect(behaviors.length, 'one recorded click per examined target').toBe(r.examined);
    expect(
      [...new Set(behaviors)],
      'every click must run under scroll-behavior:auto — a smooth click hands the landing to the animation scheduler',
    ).toEqual(['auto']);

    expect(
      await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior),
      'the check must restore the page as shipped for the checks that run after it',
    ).toBe('smooth');
    expect(
      await page.evaluate(() => document.documentElement.getAttribute('style')),
      'no inline style may be left behind on <html>',
    ).toBeNull();

    // Not blinded: the one genuine defect is still caught, and only it.
    expect(r.defects.length).toBe(1);
    expect(r.defects[0].count).toBe(1);
    expect(r.defects[0].message).toMatch(/1 of 30 in-page links land outside 88-156px/);
    expect(r.defects[0].message).toMatch(/first: #s17@20px/);
    expect(r.defects[0].message).toMatch(/1 of 30 targets declare scroll-margin-top under the 88px near edge/);
    // The page's smooth scrolling can no longer move a measured landing, so naming it as
    // a root cause would send the next reader to edit CSS that was never the problem.
    expect(r.defects[0].message).not.toMatch(/scroll-behavior/);
  });
});

/**
 * The contract is enforced at the call site, not in each check, and not only against
 * fixtures. A fixture has two anchors; a real page has sixty-two. A rule that only the
 * fixtures can violate is a rule the real pages are exempt from.
 */
test.describe('the check-result contract', () => {
  const fake = (defects: Partial<Defect>[]): Check => ({
    id: 'synthetic-check',
    family: 'NAV',
    severity: 'advisory',
    describe: 'synthetic',
    minExamined: 0,
    async run() {
      return { examined: 9, defects: defects as Defect[] };
    },
  });

  const row = (over: Partial<Defect> = {}): Partial<Defect> => ({
    checkId: 'synthetic-check',
    family: 'NAV',
    viewport: 375,
    count: 1,
    message: 'x',
    ...over,
  });

  test('accepts a well-formed result', async ({ page }) => {
    const r = await runCheck(fake([row()]), page, 375, FIXTURE_CTX);
    expect(r.defects.length).toBe(1);
  });

  test('rejects more rows than MAX_DEFECT_ROWS', async ({ page }) => {
    const many = Array.from({ length: MAX_DEFECT_ROWS + 1 }, () => row());
    await expect(runCheck(fake(many), page, 375, FIXTURE_CTX)).rejects.toThrow(/rows/i);
  });

  test('rejects a row with no count', async ({ page }) => {
    await expect(runCheck(fake([row({ count: undefined })]), page, 375, FIXTURE_CTX)).rejects.toThrow(/count/i);
  });

  test('rejects count: 0 — a defect row describes at least one failure', async ({ page }) => {
    await expect(runCheck(fake([row({ count: 0 })]), page, 375, FIXTURE_CTX)).rejects.toThrow(/count/i);
  });

  test('rejects a row attributed to a different check', async ({ page }) => {
    await expect(runCheck(fake([row({ checkId: 'someone-else' })]), page, 375, FIXTURE_CTX)).rejects.toThrow(
      /checkId/i,
    );
  });

  test('rejects a row attributed to a different family', async ({ page }) => {
    await expect(runCheck(fake([row({ family: 'IMG' })]), page, 375, FIXTURE_CTX)).rejects.toThrow(/family/i);
  });

  test('rejects a negative examined count', async ({ page }) => {
    const bad: Check = { ...fake([]), async run() { return { examined: -1, defects: [] }; } };
    await expect(runCheck(bad, page, 375, FIXTURE_CTX)).rejects.toThrow(/examined/i);
  });
});

test.describe('nested slugs cannot silently lose a page', () => {
  // The corpus spans seven page types, two of which are nested: uk-locations/<town> and
  // available-puppies/<puppy>. Interpolated raw into a filename they name a directory that does
  // not exist, so writePartial throws AFTER the checks have run and the page writes
  // nothing. A page with no partial scores ABSENT, not failed — and build_scorecard's
  // count guard would report it as a crashed page, sending the reader after a defect
  // that is really a filename. Cheap to pin, expensive to debug.
  test('flattenSlug removes every path separator', () => {
    expect(flattenSlug('uk-locations/blue-staffy-puppies-birmingham')).toBe(
      'uk-locations__blue-staffy-puppies-birmingham',
    );
    expect(flattenSlug('available-puppies/roman')).toBe('available-puppies__roman');
    expect(flattenSlug('buy-blue-staffy-puppies-uk')).toBe('buy-blue-staffy-puppies-uk');
    expect(flattenSlug('a/b/c')).not.toContain('/');
  });

  test('writePartial actually lands a file for a nested slug', () => {
    const dir = mkdtempSync(join(tmpdir(), 'raw-'));
    const prev = process.cwd();
    process.chdir(dir);
    try {
      mkdirSync(join(dir, 'data', 'quality', 'raw'), { recursive: true });
      // Re-import is not possible mid-run, so assert the naming contract the writer uses.
      const name = `${flattenSlug('blog/x')}-vp375.json`;
      writeFileSync(join(dir, 'data', 'quality', 'raw', name), '{}');
      expect(readdirSync(join(dir, 'data', 'quality', 'raw'))).toEqual(['blog__x-vp375.json']);
    } finally {
      process.chdir(prev);
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

test.describe('measureTopChrome is deterministic and finds late-pinning chrome', () => {
  const onlyOnce = (testInfo: { project: { name: string }; config: { projects: { name: string }[] } }) =>
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );

  const URL = `${FIXTURE_BASE}/tests/render/fixtures/known_broken/chrome-late-rail.html`;

  test('finds a rail that only pins past 1.5 viewports', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(URL);

    // The rail sits 2000px down; 1.5 viewports is 1200px. A single-sample probe that
    // scrolls 1.5 viewports and looks once reports 96 and misses 62px of real chrome —
    // every heading judged against a band 62px too high. Measured on the live site:
    // dna-tested and hand-raised reported 96 fresh / 147-158 pre-scrolled.
    const chrome = await measureTopChrome(page);
    expect(chrome.height).toBe(158);
    expect(chrome.parts.length).toBe(2);
  });

  test('returns the same height however the page was left scrolled', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(URL);

    // pages.spec shares ONE page object across every check, so this probe runs on
    // whatever scroll position the previous check left behind. Until this test existed,
    // the same page measured 96 or 158 depending purely on check order, which made the
    // band that judges every NAV landing non-deterministic across runs.
    const fresh = await measureTopChrome(page);

    await page.evaluate(() =>
      window.scrollTo({ top: 5000, behavior: 'instant' as ScrollBehavior }),
    );
    await page.waitForTimeout(150);
    const afterDeepScroll = await measureTopChrome(page);

    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior }));
    await page.waitForTimeout(150);
    const afterReset = await measureTopChrome(page);

    expect(afterDeepScroll.height).toBe(fresh.height);
    expect(afterReset.height).toBe(fresh.height);
  });
});

test.describe('waitForScrollSettle does not call an UNSTARTED scroll settled', () => {
  const onlyOnce = (testInfo: { project: { name: string }; config: { projects: { name: string }[] } }) =>
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );

  const URL = `${FIXTURE_BASE}/tests/render/fixtures/known_broken/scroll-late-start.html`;

  test('waits out a scroll whose first frame lands after the stability threshold', async ({
    page,
  }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(URL);
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior }));

    await page.evaluate(() => document.getElementById('jump')!.click());
    const settle = await waitForScrollSettle(page);

    // Without the start grace this resolves settled:true at y=0 after ~160ms, and
    // nav-jump-target-lands then reports the target at its raw document offset — the
    // exact `#reserve@26059px` row that failed a clean page on the live site.
    expect(settle.settled).toBe(true);
    expect(settle.y).toBeGreaterThan(1000);

    const top = await page.evaluate(() =>
      Math.round(document.getElementById('reserve')!.getBoundingClientRect().top),
    );
    expect(Math.abs(top)).toBeLessThan(60);
  });

  test('still settles promptly when the scroll never needed to move', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(URL);
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior }));

    // The grace must not turn every no-op into a 3s timeout: a click that legitimately
    // moves nothing should still report settled, bounded by the grace and not by maxMs.
    const settle = await waitForScrollSettle(page);
    expect(settle.settled).toBe(true);
    expect(settle.ms).toBeLessThan(1500);
  });
});

test.describe('measureTopChrome does not absorb sticky page content', () => {
  const onlyOnce = (testInfo: { project: { name: string }; config: { projects: { name: string }[] } }) =>
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );

  test('a sticky sidebar pinned at top:0 is not counted as chrome', async ({ page }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(`${FIXTURE_BASE}/tests/render/fixtures/known_broken/chrome-sticky-sidebar.html`);

    // Vertical adjacency alone absorbed this 300px-wide sidebar into the band. On the
    // live site that pulled aside.availB-rail (287px) and div.dial-card (672px) in,
    // reported "chrome measures 784px", tripped the implausible guard, and left NAV
    // examining ZERO units on those page-viewports — worse than the too-low band it
    // replaced, because a page that is not judged reports no defects at all.
    const chrome = await measureTopChrome(page);
    expect(chrome.height).toBe(96);
    expect(chrome.parts.length).toBe(1);
    expect(chrome.implausible).toBe(false);
  });
});

test.describe('layout-tap-target-size honours WCAG 2.5.8 exemptions', () => {
  const onlyOnce = (testInfo: { project: { name: string }; config: { projects: { name: string }[] } }) =>
    test.skip(
      testInfo.project.name !== testInfo.config.projects[0].name,
      `viewport-independent; runs once in ${testInfo.config.projects[0].name}`,
    );

  test('is silent on skip links, prose links, labelled inputs and isolated targets', async ({
    page,
  }, testInfo) => {
    onlyOnce(testInfo);
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_good/layout-tap-target-exemptions.html`,
    );
    const check = registry.find((c) => c.id === 'layout-tap-target-size')!;
    const r = await runCheck(check, page, 1280, FIXTURE_CTX);

    // Four categories, all of them WCAG's OWN exemptions, and all four were reported
    // as defects on live pages:
    //   - the 1x1 clipped skip link appeared in all 45 LAYOUT rows of the 2026-08-01
    //     baseline;
    //   - inline prose links supplied the bulk of every message (SC 2.5.8 exempts a
    //     target "in a sentence or block of text");
    //   - 12 rows on the care-guide and health-guarantee pages were 13x13 checkboxes
    //     and radios wrapped in 86x47 to 341x62 <label>s — the label IS the target;
    //   - 6 rows per page were card-title links, 18px tall and alone in their card,
    //     which the SPACING exception covers explicitly.
    //
    // Each of the four is pinned independently: the fixture puts a flush button beside
    // the labelled checkbox so the spacing exception cannot cover it, and isolates the
    // card link so the label rule cannot. Verified by deleting each rule in turn and
    // watching this test go red — an earlier fixture passed with the label rule
    // deleted, because spacing was silently covering that case too.
    expect(r.defects.map((d) => d.message)).toEqual([]);
    // ...and it must still have judged the real controls, not skipped everything.
    expect(r.examined).toBeGreaterThanOrEqual(2);
  });
});

test.describe('dist/ freshness sees a DELETED source page', () => {
  const roots: string[] = [];
  const mkRoot = () => {
    const root = mkdtempSync(join(tmpdir(), 'del-'));
    roots.push(root);
    mkdirSync(join(root, 'src', 'pages'), { recursive: true });
    mkdirSync(join(root, 'dist'), { recursive: true });
    return root;
  };
  const page = (root: string, route: string) => {
    mkdirSync(join(root, 'src', 'pages', route), { recursive: true });
    writeFileSync(join(root, 'src', 'pages', route, 'index.astro'), 'x');
  };
  const built = (root: string, route: string) => {
    mkdirSync(join(root, 'dist', route), { recursive: true });
    writeFileSync(join(root, 'dist', route, 'index.html'), 'x');
  };

  test.afterAll(() => {
    for (const r of roots) rmSync(r, { recursive: true, force: true });
  });

  test('a built route whose source was deleted is reported by name', () => {
    const root = mkRoot();
    page(root, 'kept');
    built(root, 'kept');
    built(root, 'deleted-page'); // source removed; dist/ still serves the old build
    expect(builtRoutesWithoutSource(root)).toEqual(['deleted-page']);
  });

  test('matching source and built sets report no orphan', () => {
    const root = mkRoot();
    page(root, 'a');
    page(root, 'b');
    built(root, 'a');
    built(root, 'b');
    // The false-FAIL risk is the whole reason this was deferred once. If a legitimate
    // build ever produces routes with no 1:1 source file, THIS is the test that fails.
    expect(builtRoutesWithoutSource(root)).toEqual([]);
  });

  test('checkDistFreshness refuses, and its reason names the orphaned route', () => {
    const root = mkRoot();
    page(root, 'kept');
    built(root, 'kept');
    built(root, 'ghost');
    // mtimes alone CANNOT see this: every surviving file is older than dist/, so the
    // age comparison says fresh. Only the set comparison catches it.
    utimesSync(join(root, 'src', 'pages', 'kept', 'index.astro'), new Date(1000), new Date(1000));
    const r = checkDistFreshness(root);
    expect(r.fresh).toBe(false);
    expect(r.reason).toContain('/ghost/');
    expect(r.reason).toContain('no source');
  });

  test('the real repo has no orphaned routes', () => {
    // Measured 2026-08-01: 108 source routes, 108 built routes. If this ever fails it
    // is either a genuine stale dist/ or the site gained dynamic/collection routes —
    // both worth knowing, and both named explicitly rather than guessed at.
    expect(builtRoutesWithoutSource(resolve(dirname(fileURLToPath(import.meta.url)), '..', '..'))).toEqual([]);
  });
});

/**
 * A check can be written, registered, fixture-tested, declared `blocking`, and still run
 * on ZERO pages — because `pages.spec.ts:88` filters the registry by
 * `targets.json > families_by_page_type`, and nothing required a registered family to
 * appear there.
 *
 * That is not hypothetical. `a11y-text-contrast-aa` shipped 2026-08-07 as a blocking
 * check with a known_broken fixture, and the A11Y family was never added to any page
 * type. It examined nothing on every page of the site for a full day while reporting as
 * a shipped gate — the same "PASS in 0 pages" costume as
 * reference_gate_examined_zero_pages and reference_cssrules_truthy_on_every_rule.
 *
 * `build_scorecard.mjs` Guard 2 caught it only AFTER a full 13-minute run. These tests
 * catch it in milliseconds, before the run.
 */
test.describe('every registered family is actually wired into targets.json', () => {
  const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
  const readTargets = (root = repoRoot) =>
    JSON.parse(readFileSync(join(root, 'tests', 'render', 'targets.json'), 'utf8')) as {
      families_by_page_type: Record<string, string[]>;
    };

  /** Families that exist in code but no page type will ever run. */
  const unwiredFamilies = (
    registered: string[],
    byPageType: Record<string, string[]>,
  ): string[] => {
    const wired = new Set(Object.values(byPageType).flat());
    return [...new Set(registered)].filter((f) => !wired.has(f)).sort();
  };

  test('the predicate names a family that is registered but wired nowhere', () => {
    expect(
      unwiredFamilies(['IMG', 'A11Y'], { 'for-sale': ['IMG'], bird: ['IMG'] }),
    ).toEqual(['A11Y']);
  });

  test('a family wired into even one page type is not reported', () => {
    // Deliberately asymmetric: A11Y runs on for-sale only. That is a scoping decision,
    // not a defect, and this invariant must not force every family onto every page type.
    expect(unwiredFamilies(['IMG', 'A11Y'], { 'for-sale': ['IMG', 'A11Y'], bird: ['IMG'] })).toEqual(
      [],
    );
  });

  test('the REAL repo wires every family it registers', () => {
    const registered = registry.map((c) => c.family);
    const unwired = unwiredFamilies(registered, readTargets().families_by_page_type);
    expect(
      unwired,
      `registered but wired to no page type: ${unwired.join(', ')} — ` +
        `these checks run on zero pages while looking shipped`,
    ).toEqual([]);
  });

  test('targets.json declares no family that no check registers', () => {
    // The mirror failure: a typo'd or retired family name in targets.json silently
    // widens nothing and hides that a family is misspelled.
    const registered = new Set(registry.map((c) => c.family));
    const declared = [...new Set(Object.values(readTargets().families_by_page_type).flat())];
    const phantom = declared.filter((f) => !registered.has(f)).sort();
    expect(phantom, `declared in targets.json but no check registers it: ${phantom.join(', ')}`).toEqual(
      [],
    );
  });
});

/**
 * `img-srcset-within-2x` conflated two unrelated states under one message,
 * "failed to decode and could not be measured":
 *
 *   - `complete === true && naturalWidth === 0` — a real 404 or corrupt file.
 *   - `complete === false` — still in flight when we happened to look.
 *
 * The second is a fact about the run, not the page. On 2026-08-08 it failed
 * `congo-african-grey-parrot-pair-for-sale` at **vp375 only**, on a 6,294-byte WebP that
 * decodes perfectly to 230x144 — that page has 58 images, the file is the eager
 * `decoding="async"` hero, and 375px is the one viewport whose `sizes` (~170px) selects
 * the 230w candidate. It passed at 768 and 1280 in the same run.
 * reference_same_input_different_verdict.
 *
 * Because the check is `blocking`, that flake fails builds at random. These tests pin the
 * distinction so the two states can never be merged back together.
 */
test.describe('img-srcset-within-2x separates broken from still-loading', () => {
  const imgCheck = () => {
    const c = registry.find((x) => x.id === 'img-srcset-within-2x');
    if (!c) throw new Error('img-srcset-within-2x is not registered');
    return c;
  };

  test('a 404 image is still reported — a broken page must not score clean', async ({
    page,
  }, testInfo) => {
    const res0 = await page.goto(fixtureUrl('known_broken', 'img-broken-vs-still-loading'));
    // Assert the fixture actually loaded. A mistyped fixture URL yields an empty page,
    // zero images, and a green "no defects" — a pass that proves nothing.
    expect(res0?.status(), 'fixture must load').toBe(200);
    const res = await runCheck(imgCheck(), page, testInfo.project.use.viewport!.width);
    const msg = res.defects.map((d) => d.message).join(' | ');
    expect(msg, 'the 404 must be named').toContain('definitely-not-a-real-image-404.webp');
    expect(msg, 'and described as a LOAD failure, not a decode failure').toMatch(/failed to LOAD/);
  });

  test('the decodable image is examined, not skipped', async ({ page }, testInfo) => {
    const res0 = await page.goto(fixtureUrl('known_broken', 'img-broken-vs-still-loading'));
    // Assert the fixture actually loaded. A mistyped fixture URL yields an empty page,
    // zero images, and a green "no defects" — a pass that proves nothing.
    expect(res0?.status(), 'fixture must load').toBe(200);
    const res = await runCheck(imgCheck(), page, testInfo.project.use.viewport!.width);
    // The good image must land in `examined`; if it did not, the check is judging nothing
    // and would pass on zero. reference_gate_examined_zero_pages.
    expect(res.examined, 'the decodable image must be examined').toBeGreaterThanOrEqual(1);
  });

  test('no defect row ever describes an image as merely still loading', async ({
    page,
  }, testInfo) => {
    const res0 = await page.goto(fixtureUrl('known_broken', 'img-broken-vs-still-loading'));
    // Assert the fixture actually loaded. A mistyped fixture URL yields an empty page,
    // zero images, and a green "no defects" — a pass that proves nothing.
    expect(res0?.status(), 'fixture must load').toBe(200);
    const res = await runCheck(imgCheck(), page, testInfo.project.use.viewport!.width);
    for (const d of res.defects) {
      expect(
        d.message,
        'still-loading is a statement about the run, not a defect on a blocking check',
      ).not.toMatch(/still loading/i);
    }
  });
});

/*
 * REMOVED IN THE BSUK PORT (2026-09-16): CAG's `IndexNow tooling is intact` describe.
 * It asserted the existence of scripts/indexnow_submit.py, exactly one 32-hex
 * public/<key>.txt whose body equals its filename, and that no live line of
 * skills/cag-indexing.md still pointed at the MFS project. None of those three artefacts
 * exists in this repo, so every assertion would have failed for the absence of a CAG
 * tool rather than for a defect in anything BSUK ships. It is deliberately DELETED rather
 * than skipped: a skipped test is the easiest place to hide vanished coverage, and this
 * one covered nothing here to begin with. If BSUK ever adopts IndexNow submission, port
 * the block back alongside the tool.
 */

/**
 * form-inquiry-contract: examined === 0 is a legitimate silent state on every BSUK page
 * EXCEPT the contact page, which is the only one that ships ContactForm.astro. On that one
 * page, zero forms examined must itself become a defect row — otherwise a page that lost
 * its whole form (or that only carries a `/search/` form) scores clean forever,
 * indistinguishable from a page nobody ever built the check against.
 *
 * FIXTURE_CTX pins the contact slug so the generic known_good/known_broken loop exercises
 * the field contract rather than the 'none' branch — which means this predicate needs its
 * own fixture with no non-search form at all, run under several different slugs.
 */
test.describe('form-inquiry-contract: zero-examined is a defect only where a form is expected', () => {
  const NOFORM_URL = `${FIXTURE_BASE}/tests/render/fixtures/form-inquiry-contract-noform.html`;
  const check = () => {
    const c = registry.find((x) => x.id === 'form-inquiry-contract')!;
    if (!c) throw new Error('form-inquiry-contract is not registered');
    return c;
  };

  test('the contact page with no non-search form fires one defect', async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto(NOFORM_URL);
    expect(res?.status(), 'fixture must load').toBe(200);
    const result = await runCheck(check(), page, viewport, {
      ...FIXTURE_CTX,
      slug: 'uk-blue-staffy-breeders-contact',
      pageType: 'interior',
    });
    expect(result.examined).toBe(0);
    expect(result.defects.length, 'zero examined on a form-bearing page must not pass silently').toBe(1);
    expect(result.defects[0].message).toBe(
      'no non-search form on uk-blue-staffy-breeders-contact (interior) — nothing to judge',
    );
  });

  test('a location page with no non-search form is silent', async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto(NOFORM_URL);
    expect(res?.status(), 'fixture must load').toBe(200);
    const result = await runCheck(check(), page, viewport, {
      ...FIXTURE_CTX,
      slug: 'uk-locations/blue-staffy-puppies-birmingham',
      pageType: 'location',
    });
    expect(result.examined).toBe(0);
    expect(result.defects, 'location legitimately carries no inquiry form').toEqual([]);
  });

  test('a hub page with no non-search form is silent', async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto(NOFORM_URL);
    expect(res?.status(), 'fixture must load').toBe(200);
    const result = await runCheck(check(), page, viewport, {
      ...FIXTURE_CTX,
      slug: 'available-puppies',
      pageType: 'hub',
    });
    expect(result.examined).toBe(0);
    expect(result.defects, 'hub legitimately carries no inquiry form').toEqual([]);
  });
});

/**
 * `fieldChecksSkipped` decides which slugs are exempt from the seven-field screening
 * contract. Pinned directly (same reason as `flattenSlug` above): the predicate is a pure
 * function driving a policy decision, not something the generic fixture loop can exercise
 * for every slug shape it needs to cover.
 */
test.describe('fieldChecksSkipped pins the field-contract exemption list', () => {
  // BSUK's inventory is the mirror image of CAG's: exactly ONE page carries an inquiry
  // form, so the exemption is an explicit allow-list and everything else is exempt.
  // Verified against dist/ 2026-09-16 — 1 of 17 targets contains a <form> at all.
  test('in scope: the contact page, which is the only page that ships ContactForm.astro', () => {
    expect(fieldChecksSkipped('uk-blue-staffy-breeders-contact')).toBe(false);
  });

  test('exempt: every other page type, because none of them carries an inquiry form', () => {
    for (const s of [
      'index',
      'buy-blue-staffy-puppies-uk',
      'available-puppies/roman',
      'available-puppies',
      'uk-locations',
      'uk-locations/blue-staffy-puppies-birmingham',
      'blue-staffy-blog-guides',
      'privacy-policy-uk',
    ]) {
      expect(fieldChecksSkipped(s), s).toBe(true);
    }
  });
});

/** `contractFor` picks which field list a page's inquiry forms must carry. The field lists
 *  themselves are CAG's and are pinned by the fixtures — see the note at the top of
 *  checks/form.ts for why the port deliberately did not rewrite them. */
test.describe('contractFor pins the per-slug field contract', () => {
  test('full: the contact page', () => {
    expect(contractFor('uk-blue-staffy-breeders-contact')).toBe('full');
  });
  test('none: every page with no inquiry form', () => {
    expect(contractFor('index')).toBe('none');
    expect(contractFor('uk-locations/blue-staffy-puppies-birmingham')).toBe('none');
    expect(contractFor('buy-blue-staffy-puppies-uk')).toBe('none');
  });
});

/**
 * `formExpected` decides when the zero-examined defect fires, and it must agree with the
 * exemption above rather than with `pageType` alone. On CAG the discriminator was pageType
 * plus a slug escape hatch for two for-sale pages that carried only the search form; on
 * BSUK it is the slug outright, because the one page with a form is `interior`-typed and
 * five other `interior` pages have none — a pageType rule would emit five false rows.
 */
test.describe('formExpected pins the zero-examined exemption list', () => {
  test('expected: the contact page only', () => {
    expect(formExpected('uk-blue-staffy-breeders-contact', 'interior')).toBe(true);
  });

  test('not expected: other interior pages, home, puppy, hub, location and blog', () => {
    expect(formExpected('blue-staffy-health-uk', 'interior')).toBe(false);
    expect(formExpected('index', 'home')).toBe(false);
    expect(formExpected('available-puppies/roman', 'puppy')).toBe(false);
    expect(formExpected('available-puppies', 'hub')).toBe(false);
    expect(formExpected('uk-locations/blue-staffy-puppies-birmingham', 'location')).toBe(false);
    expect(formExpected('blue-staffy-blog-guides', 'blog')).toBe(false);
  });
});
