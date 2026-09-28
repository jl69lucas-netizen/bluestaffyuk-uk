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
import { latestCards, notYetMeasured, readScorecards, zeroExamined } from './lib/examined.js';
import { severityFor, isNewPage, approvedBoards, type Promotion, type NewPageRule } from './lib/promotions.js';
import { fixtureUrl, FIXTURE_BASE } from './lib/servers.js';
import { measureTopChrome, waitForScrollSettle } from './lib/probes.js';
import { checkDistFreshness, builtRoutesWithoutSource } from './lib/freshness.js';
import {
  fixtureCorpus,
  distSlugs,
  siblingSlugsFor,
  isSpecimen,
  loadWhitelist,
  normalise,
  REPO,
  type Target,
} from './lib/dupCorpus.js';
import { resetRaw } from './lib/scorecard.js';
import { contractFor, fieldChecksSkipped, formExpected, FORM_ID_FROM_ENV } from './checks/form.js';
import './checks/index.js';


/**
 * Fixtures are judged under the STRICTEST page type, not a neutral one.
 *
 * `pageType` only reaches checks that condition on it, and today that is SCHEMA, where
 * `puppy` is the tightest branch (exactly one Product/Offer, never AggregateOffer). Passing
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

/**
 * The committed form fixtures cannot carry the real Formspree id — it lives in .env and no
 * credential-adjacent value may sit in a committed file. They carry the literal
 * `FORM_ID_FROM_ENV` (exported from checks/form.ts, so the two sides cannot drift) in their
 * form `action`s instead, and this substitutes the live id into the loaded DOM before the
 * check runs, so the FORM family judges known_good against the very endpoint it will judge
 * dist/ against. It THROWS rather than no-ops when the id is unset: with the check now
 * refusing lazily, a silent no-op here would leave the fixture action unsubstituted and the
 * failure would read as a fixture defect instead of a missing environment.
 */
async function substituteFormEndpoint(page: import('@playwright/test').Page): Promise<void> {
  const id = process.env.PUBLIC_FORMSPREE_ID;
  if (!id) {
    throw new Error(
      `PUBLIC_FORMSPREE_ID is unset — the form fixtures' ${FORM_ID_FROM_ENV} placeholder ` +
        'cannot be substituted. Set it in .env (see .env.example) and re-run.',
    );
  }
  await page.evaluate(
    ({ formId, token }) => {
      document.querySelectorAll(`form[action*="${token}"]`).forEach((f) => {
        f.setAttribute('action', (f.getAttribute('action') || '').replace(token, formId));
      });
    },
    { formId: id, token: FORM_ID_FROM_ENV },
  );
}

for (const check of registry) {
  test.describe(`${check.id} [${check.family}]`, () => {
    test('fires on the known_broken fixture', async ({ page }, testInfo) => {
      const viewport = testInfo.project.use.viewport!.width;
      const res = await page.goto(fixtureUrl('known_broken', check.id));
      expect(res?.status(), 'known_broken fixture must exist').toBe(200);
      if (check.family === 'FORM') await substituteFormEndpoint(page);
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
      if (check.family === 'FORM') await substituteFormEndpoint(page);
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
    expect(msg).toContain('18w vs /sibling-staffy-puppies-glasgow/ "before a puppy leaves');
    // PASSAGE B IS 19 WORDS, NOT 17, AND THE TWO EXTRA ARE THE POINT. The delivery stem was
    // re-measured on 2026-09-21 and shortened by one word: `…priced by distance 200 to 350 or
    // collect` was carried by 8 built pages and the same run without the trailing `or collect`
    // by 9, so the longer stem exempted nothing on the ninth (/blue-staffy-pup-sale-uk/, which
    // states the band and stops) — the "whitelist the CORE, never the longest run on one page"
    // rule in scripts/dup_content_audit.py's own header. `or collect` is therefore no longer
    // chrome, it is page wording, and this fixture's passage B legitimately starts with it.
    // The assertion moves to the measured value rather than the fixture losing the words:
    // what this test pins is that the two passages fire SEPARATELY and that the exempt line
    // itself is never the defect, and both still hold.
    expect(msg).toContain('19w vs /sibling-staffy-puppies-glasgow/ "or collect tell us which puppy');
    expect(msg, 'the whitelisted line is not the defect').not.toContain('defra approved transport');
  });
});

/**
 * The DUP check is only as wide as the sibling set pages.spec hands it.
 *
 * Found 2026-09-11: the set was "same page type", and targets.json holds 13 for-sale
 * targets but exactly ONE each of puppy, comparison, interior, location, blog and hub — so on
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
    // And two specimen routes (noindex scaffolding): built, keyed, never a sibling.
    const specimens = ['kit-preview/city-page', 'board-preview/index'];
    const built = [...targetsFile.pages.map((p) => p.slug), ...untargeted, ...specimens];
    for (const slug of built) {
      const dir = slug === 'index' ? dist : join(dist, slug);
      mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, 'index.html'), `<main><p>${slug}</p></main>`);
    }
    const corpus = distSlugs(dist);
    expect(specimens.every(isSpecimen), 'the specimen list names kit-preview/ and board-preview/').toBe(true);
    expect(corpus, 'distSlugs keys pages as scripts/_slugs.py page_key does').toEqual([...built].sort());

    const blind = Object.entries(targetsFile.families_by_page_type)
      .filter(([, fams]) => !fams.includes('DUP'))
      .map(([type]) => type);
    expect.soft(blind, 'page types that never run DUP').toEqual([]);

    const short = targetsFile.pages
      .map((t) => {
        const got = siblingSlugsFor(t, targetsFile.pages, corpus);
        // Every other built page EXCEPT a specimen route (data/specimen-routes.json; the /kit-preview/
        // target itself is one), which dup_content_audit.py never counts either.
        const want = corpus.filter((s) => s !== t.slug && !isSpecimen(s));
        return { t, got, missing: want.filter((s) => !got.includes(s)), specimen: got.filter((s) => isSpecimen(s)) };
      })
      .filter((r) => r.missing.length || r.specimen.length || r.got.includes(r.t.slug))
      .map((r) => `${r.t.slug} [${r.t.page_type}]: ${r.got.length} siblings, missing ${r.missing.length}, specimen routes counted ${r.specimen.length}`);
    expect.soft(short, 'targets judged against less than the whole built corpus').toEqual([]);
  });
});

/**
 * DUP counts words the way the Python auditor counts them.
 *
 * Found 2026-09-11: scripts/dup_content_audit.py tokenises with [a-z0-9$']+, so "we'd" is one
 * word; normalise() replaced the apostrophe with a space and read "we d". On the same dist/,
 * "answered the same honest way we'd answer them on the phone" — shared by the source
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
  const SHARED_12 = "every vet record we've kept for a puppy goes home with it";

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
      'Blue/Brindle 1st  litter\tnaïve ÉCLAT',
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
 * Measured 2026-09-13 on the source project's widest for-sale page @1280: it failed once with
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
      unwiredFamilies(['IMG', 'A11Y'], { 'for-sale': ['IMG'], puppy: ['IMG'] }),
    ).toEqual(['A11Y']);
  });

  test('a family wired into even one page type is not reported', () => {
    // Deliberately asymmetric: A11Y runs on for-sale only. That is a scoping decision,
    // not a defect, and this invariant must not force every family onto every page type.
    expect(unwiredFamilies(['IMG', 'A11Y'], { 'for-sale': ['IMG', 'A11Y'], puppy: ['IMG'] })).toEqual(
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
 * the source project's paired-listing page at **vp375 only**, on a 6,294-byte WebP that
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
 * the source project's indexing skill still pointed at the MFS project. None of those three artefacts
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
  // Routed by data/page-map.json `kind`, exactly as scripts/form_contract_audit.py routes
  // it: rich → full, blog → short, location → none, and the hubs (absent from the map)
  // → none by the slug fallback. "Exempt" therefore means "this page's inquiry forms, if
  // it ever grows one, carry no field contract" — NOT "this page has no form today".
  test('in scope: every rich and blog page, contact page included', () => {
    for (const s of [
      'uk-blue-staffy-breeders-contact',
      'index',
      'buy-blue-staffy-puppies-uk',
      'privacy-policy-uk',
      'blue-staffy-blog-guides',
    ]) {
      expect(fieldChecksSkipped(s), s).toBe(false);
    }
  });

  test('exempt: the uk-locations cluster and the hubs', () => {
    for (const s of [
      'uk-locations',
      'uk-locations/blue-staffy-puppies-birmingham',
      'uk-locations/staffy-puppies-for-sale-glasgow',
      'available-puppies',
      'blog',
    ]) {
      expect(fieldChecksSkipped(s), s).toBe(true);
    }
  });
});

/** `contractFor` picks which field list a page's inquiry forms must carry, from
 *  data/page-map.json `kind`. It must agree with scripts/form_contract_audit.py on every
 *  slug or the two gates give different verdicts on the same form. */
test.describe('contractFor pins the per-slug field contract', () => {
  test('full: rich pages', () => {
    expect(contractFor('uk-blue-staffy-breeders-contact')).toBe('full');
    expect(contractFor('index')).toBe('full');
    expect(contractFor('buy-blue-staffy-puppies-uk')).toBe('full');
  });
  test('short: blog-kind pages, and blog/* posts absent from the map', () => {
    expect(contractFor('blue-staffy-blog-guides')).toBe('short');
    expect(contractFor('blog/a-post-built-after-the-map')).toBe('short');
  });
  test('none: the locations cluster and the hubs', () => {
    expect(contractFor('uk-locations/blue-staffy-puppies-birmingham')).toBe('none');
    expect(contractFor('uk-locations')).toBe('none');
    expect(contractFor('available-puppies')).toBe('none');
  });
});

/**
 * `formExpected` decides when the zero-examined defect fires. It is the slug allow-list,
 * not the contract and not `pageType`: on BSUK the one page with a form is `interior`-typed
 * and five other `interior` pages have none, so a pageType rule would emit five false rows,
 * and a contract rule would emit one for every rich page.
 */
test.describe('formExpected pins the zero-examined exemption list', () => {
  test('expected: the contact page only', () => {
    expect(formExpected('uk-blue-staffy-breeders-contact')).toBe(true);
  });

  test('not expected: other interior pages, home, puppy, hub, location and blog', () => {
    for (const s of [
      'blue-staffy-health-uk',
      'index',
      'available-puppies/roman',
      'available-puppies',
      'uk-locations/blue-staffy-puppies-birmingham',
      'blue-staffy-blog-guides',
    ]) {
      expect(formExpected(s), s).toBe(false);
    }
  });
});

/**
 * The 'short' contract has no page carrying a form today, so the generic fixture loop —
 * pinned to the contact slug — never takes that branch. Without this, `SHORT` could be
 * emptied or mis-spelled and every meta test would still pass.
 */
test.describe('form-inquiry-contract: the short (blog) contract is exercised', () => {
  const URL = `${FIXTURE_BASE}/tests/render/fixtures/known_good/form-inquiry-contract-blog-short.html`;
  const check = () => registry.find((x) => x.id === 'form-inquiry-contract')!;

  test('a blog-kind page with name/email/message only is clean', async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto(URL);
    expect(res?.status(), 'fixture must load').toBe(200);
    await substituteFormEndpoint(page);
    expect(contractFor('blue-staffy-blog-guides'), 'fixture must take the short branch').toBe('short');
    const result = await runCheck(check(), page, viewport, {
      ...FIXTURE_CTX,
      slug: 'blue-staffy-blog-guides',
      pageType: 'blog',
    });
    expect(result.examined, 'the blog inquiry form must be examined').toBe(1);
    expect(result.defects.map((d) => d.message), 'short contract cried wolf').toEqual([]);
  });

  test('the same form missing `message` fires', async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    await page.goto(URL);
    await substituteFormEndpoint(page);
    await page.evaluate(() => document.querySelector('textarea[name="message"]')!.remove());
    const result = await runCheck(check(), page, viewport, {
      ...FIXTURE_CTX,
      slug: 'blue-staffy-blog-guides',
      pageType: 'blog',
    });
    expect(result.defects.length, 'a short contract that cannot fail is not a contract').toBeGreaterThan(0);
  });
});

/**
 * A deferral must never be able to hide a dead check.
 *
 * `targets.json > deferred_checks` exempts an id from build_scorecard.mjs Guard 2 — the
 * guard whose entire job is to catch a check that examined ZERO nodes everywhere while
 * looking shipped (reference: a11y-text-contrast-aa, 2026-08-07). Exempting an id is
 * therefore switching off the one alarm that would notice the check had rotted, so the
 * exemption has to buy back the proof by other means: the id must still name a REGISTERED
 * check, and that check must still fire on its known_broken fixture and stay silent on its
 * known_good one. A deferred check is one whose convention the pages do not use yet — not
 * one nobody is testing.
 */
test.describe('every deferred check is registered and still passes both fixtures', () => {
  const deferredIds = Object.keys(
    (
      JSON.parse(
        readFileSync(
          resolve(dirname(fileURLToPath(import.meta.url)), 'targets.json'),
          'utf8',
        ),
      ) as { deferred_checks?: Record<string, string> }
    ).deferred_checks ?? {},
  );

  test('every deferred id names a check the registry actually holds', () => {
    const registered = new Set(registry.map((c) => c.id));
    const phantom = deferredIds.filter((id) => !registered.has(id)).sort();
    expect(
      phantom,
      `deferred in targets.json but no check registers it: ${phantom.join(', ')} — ` +
        `a deferral for a nonexistent id silences nothing and hides the typo`,
    ).toEqual([]);
  });

  const deferredReasons = () =>
    (
      JSON.parse(
        readFileSync(
          resolve(dirname(fileURLToPath(import.meta.url)), 'targets.json'),
          'utf8',
        ),
      ) as { deferred_checks?: Record<string, string> }
    ).deferred_checks ?? {};

  test('every deferred id carries a reason that states its promotion condition', () => {
    // A reason that only says WHY is a reason to never look again. Requiring the sentence
    // that says when the entry comes out turns each deferral into something with an end
    // date somebody can check, rather than a permanent exemption worded as a temporary one.
    for (const [id, reason] of Object.entries(deferredReasons())) {
      expect(reason.trim().length, `${id} is deferred with no stated reason`).toBeGreaterThan(10);
      expect(
        reason.toLowerCase(),
        `${id}'s reason does not say when the deferral ends — every entry must state ` +
          `'remove this entry when …' so the exemption cannot outlive its cause`,
      ).toContain('remove this entry when');
    }
  });

  /**
   * A deferral is only honest while the check really is examining nothing.
   *
   * The moment a page starts carrying the convention — project 3 adds the counter strip,
   * say — the check has real nodes to judge and its findings would be silently exempt from
   * Guard 2. This reads the latest raw run and requires every deferred id to have examined
   * ZERO. It is deliberately a skip, not a pass, when no run exists: "no data" must not
   * read as "verified".
   */
  test('no deferred check is actually examining nodes in the latest run', () => {
    // SCORECARDS, not raw partials. `global-setup.ts` calls resetRaw(), so by the time this
    // spec executes data/quality/raw is empty by design — reading it here would skip on
    // every single run and the assertion would be decoration. The scorecards are the
    // durable record of the last pages run and carry `examined_by_check` per page.
    const root = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
    const dir = join(root, 'data', 'quality', 'scorecards');
    const cards = existsSync(dir) ? readdirSync(dir).filter((f) => f.endsWith('.json')) : [];
    if (cards.length === 0) {
      // Skip, never pass: "no run on disk" must not be able to read as "verified".
      test.skip(
        true,
        'no scorecards on disk — run `npm run test:render:pages` then ' +
          '`node scripts/build_scorecard.mjs` before a deferral can be trusted',
      );
      return;
    }
    const examined = new Map<string, number>();
    for (const file of cards) {
      const card = JSON.parse(readFileSync(join(dir, file), 'utf8')) as {
        examined_by_check?: Record<string, number>;
      };
      for (const [id, n] of Object.entries(card.examined_by_check ?? {})) {
        examined.set(id, (examined.get(id) ?? 0) + n);
      }
    }
    const live = Object.keys(deferredReasons())
      .filter((id) => (examined.get(id) ?? 0) > 0)
      .map((id) => `${id} (${examined.get(id)} nodes)`)
      .sort();
    expect(
      live,
      `deferred but examining real nodes: ${live.join(', ')} — these checks are live again ` +
        `and their defects are being exempted from Guard 2. Remove them from deferred_checks.`,
    ).toEqual([]);
  });

  for (const id of deferredIds) {
    test(`${id} still fires on known_broken and is silent on known_good`, async ({
      page,
    }, testInfo) => {
      const check = registry.find((c) => c.id === id);
      expect(check, `${id} is deferred but not registered`).toBeTruthy();
      const viewport = testInfo.project.use.viewport!.width;

      const broken = await page.goto(fixtureUrl('known_broken', id));
      expect(broken?.status(), 'known_broken fixture must exist').toBe(200);
      const bad = await runCheck(check!, page, viewport, FIXTURE_CTX);
      expect(
        bad.defects.length,
        `${id} is deferred from Guard 2 and no longer fires on its own broken fixture — ` +
          `the deferral is now hiding a dead check`,
      ).toBeGreaterThan(0);

      const good = await page.goto(fixtureUrl('known_good', id));
      expect(good?.status(), 'known_good fixture must exist').toBe(200);
      const clean = await runCheck(check!, page, viewport, FIXTURE_CTX);
      expect(
        clean.defects.map((d) => d.message),
        `${id} cried wolf on a clean page`,
      ).toEqual([]);
    });
  }
});

/**
 * The KIT's counter strip, not a generic one.
 *
 * The generic loop above judges `layout-hero-counter-separation` against the fixture named
 * after the check, which proves the check can tell separated from flush. It says nothing
 * about whether the component BSUK actually ships clears the bar. This pair is
 * src/components/kit/CounterStrip.astro's own geometry with its tokens resolved: the
 * known_good half is variant a under the inverse hero band, and the known_broken half is
 * the same markup with the bed and the rule taken away — the one edit that would silently
 * reintroduce the 2026-08-07 defect while every other test stayed green.
 */
test.describe('layout-hero-counter-separation [kit CounterStrip]', () => {
  const check = () => registry.find((c) => c.id === 'layout-hero-counter-separation')!;

  test('is silent on the kit strip with its bed and rule', async ({ page }, testInfo) => {
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_good/kit-counter-separated.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined, 'the check must find the strip at all').toBe(1);
    expect(r.defects.map((d) => d.message)).toEqual([]);
  });

  test('fires when the kit strip keeps the hero band and drops the rule', async ({
    page,
  }, testInfo) => {
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_broken/kit-counter-flush.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined).toBe(1);
    expect(r.defects.length, 'a flush strip must be reported').toBeGreaterThan(0);
    // Matched loosely on purpose: the assertion is that BOTH halves are reported missing,
    // not that the check's prose never gets reworded.
    expect(r.defects[0].message).toMatch(/tone/);
    expect(r.defects[0].message).toMatch(/rule/);
  });
});

/**
 * The KIT's section sheet, not a generic bottom bar.
 *
 * The generic loop judges `nav-bottom-chrome-clear` against the fixture named after the
 * check, which proves the check can tell a reserved bar from an unreserved one. It says
 * nothing about whether src/components/kit/SectionSheet.astro reserves. This pair is that
 * component's own resolved geometry: the 64px `.kit-tabbar` and the `is:global`
 * `body:has(.kit-sheet) { padding-bottom: 64px }` that pays for it. The known_broken half
 * is the same markup with that ONE declaration deleted — the edit that would put the last
 * section of every page back under the bar while every other test stayed green.
 *
 * Convention 10 in kit form: the bar is chrome measured against the scroll, so on the
 * preview page it examines what the preview happens to contain. The fixture pair IS the
 * coverage for the shipped component.
 */
// The bar is `display: none` at >=1024px, where PageDial is the in-page nav. At vp1280 the
// fixture therefore contains no bottom chrome at all and the check examines zero — which is
// the component behaving correctly, not a pair that failed to prove anything. Skipped
// rather than asserted-empty, so that adding a fourth viewport project above 1024 does not
// quietly turn this pair into two vacuous passes.
const DESKTOP = (info: { project: { use: { viewport?: { width: number } | null } } }) =>
  (info.project.use.viewport?.width ?? 0) >= 1024;
const DESKTOP_REASON = 'SectionSheet is hidden at >=1024px; PageDial owns in-page nav there';

test.describe('nav-bottom-chrome-clear [kit SectionSheet]', () => {
  const check = () => registry.find((c) => c.id === 'nav-bottom-chrome-clear')!;

  // The bar is `display: none` at >=1024px, where PageDial is the in-page nav. At vp1280
  // the fixture therefore contains no bottom chrome at all and the check examines zero —
  // which is the component behaving correctly, not a pair that failed to prove anything.
  // Skipped rather than asserted-empty, so a viewport project added above 1024 later does
  // not quietly turn this pair into two vacuous passes.

  test('is silent on the kit bar that reserves its own height', async ({ page }, testInfo) => {
    test.skip(DESKTOP(testInfo), DESKTOP_REASON);
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_good/kit-bottom-chrome-clear.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    // Six, not "at least one": a fixture that silently lost five of its sections would
    // otherwise pass while proving a sixth of what it claims.
    expect(r.examined, 'all six section targets must be judged').toBe(6);
    expect(r.defects.map((d) => d.message)).toEqual([]);
  });

  test('fires when the kit bar keeps its height but drops the body reservation', async ({
    page,
  }, testInfo) => {
    test.skip(DESKTOP(testInfo), DESKTOP_REASON);
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_broken/kit-bottom-chrome-covers.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined).toBe(6);
    expect(r.defects.length, 'a covered jump target must be reported').toBeGreaterThan(0);
    // The short final section is the one that lands under the bar; the five tall ones
    // scroll their own tops to the viewport top and cannot.
    expect(r.defects[0].message).toContain('#d-f');
    expect(r.defects[0].count).toBe(1);
  });
});

/**
 * The KIT's info card, not a generic one.
 *
 * The generic loop above resolves a fixture BY CHECK ID, so it judges
 * `layout-h3-image-first` and `sem-statement-label-visible` against
 * known_good/layout-h3-image-first.html and known_good/sem-statement-label-visible.html —
 * pages written to prove those checks can tell the two states apart. Neither says anything
 * about src/components/kit/InfoCard.astro. These kit-named pairs do, and because the loop
 * cannot find them by id they need their own describes, the same way the kit counter strip
 * does.
 *
 * Both checks are convention-10 positional/state checks: on the canvas every demo is the
 * first child of its own artboard and the labels sit outside a page's real flow, so the
 * fixture pair IS the coverage.
 */
test.describe('layout-h3-image-first [kit InfoCard]', () => {
  const check = () => registry.find((c) => c.id === 'layout-h3-image-first')!;

  test('is silent on the kit card with its image above its prose', async ({ page }, testInfo) => {
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_good/kit-h3-image-first.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    // Two blocks, not one: a fixture that silently lost its only unit would otherwise pass
    // as clean while examining nothing.
    expect(r.examined, 'both H3 blocks must own a sectional image').toBe(2);
    expect(r.defects.map((d) => d.message)).toEqual([]);
  });

  test('fires when the kit card drops the image below the prose', async ({ page }, testInfo) => {
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_broken/kit-h3-image-last.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined).toBe(2);
    expect(r.defects.length, 'a prose-first block must be reported').toBeGreaterThan(0);
    expect(r.defects[0].count, 'both blocks are offenders').toBe(2);
  });
});

test.describe('sem-statement-label-visible [kit InfoCard]', () => {
  const check = () => registry.find((c) => c.id === 'sem-statement-label-visible')!;

  test('is silent on the kit card labels in all three places it puts one', async ({
    page,
  }, testInfo) => {
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_good/kit-stmt-label.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined, 'band, eyebrow and H3 labels').toBe(3);
    expect(r.defects.map((d) => d.message)).toEqual([]);
  });

  test('fires on a hidden label and on one with no kind', async ({ page }, testInfo) => {
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_broken/kit-stmt-label-hidden.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined).toBe(3);
    // Matched loosely on purpose: the assertion is that BOTH halves of the predicate are
    // reported, not that the check's prose never gets reworded.
    expect(r.defects[0].count).toBe(2);
    expect(r.defects[0].message).toMatch(/hidden/);
    expect(r.defects[0].message).toMatch(/kind/);
  });
});

test.describe('a11y-text-contrast-aa [kit Hero aside]', () => {
  const check = () => registry.find((c) => c.id === 'a11y-text-contrast-aa')!;

  // THE BUG CLASS THIS PAIR PINS is "component paints a bed, child keeps the inherited ink".
  // `.hero-aside` fills `--color-surface-raised` inside a hero whose box may be
  // `.bl-frame-band`, which sets `--color-text-on-inverse` on everything beneath it — so an
  // aside that does not state its own `color` renders bone text on a near-white card. That
  // is what /blue-staffy-uk-breeders/ shipped at 8472c06: the quote measured 1.05:1 and was
  // invisible. Neither declaration is wrong on its own and every other element in the box
  // names a colour of its own, so only a RENDERED measurement can see it.
  test('is silent on the aside once it states the ink for the bed it paints', async ({
    page,
  }, testInfo) => {
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_good/kit-hero-aside-ink.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined, 'H1, lede, aside title, quote and two items').toBeGreaterThanOrEqual(6);
    expect(r.defects.map((d) => d.message)).toEqual([]);
  });

  test('fires on the aside that inherits the band ink onto its own light bed', async ({
    page,
  }, testInfo) => {
    const res = await page.goto(
      `${FIXTURE_BASE}/tests/render/fixtures/known_broken/kit-hero-aside-ink-inherited.html`,
    );
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined, 'the same six nodes are judged either way').toBeGreaterThanOrEqual(6);
    // Matched loosely: the assertion is that the QUOTE is caught and that the ratio reported
    // is the near-1:1 one, not that the check's prose never gets reworded. The aside's title
    // still passes in both fixtures, which is the point — it names a colour of its own.
    expect(r.defects.length, 'the pair differs by one declaration').toBe(1);
    expect(r.defects[0].message).toMatch(/aside-quote/);
    expect(r.defects[0].message).toMatch(/1\.0\d:1/);
  });
});

/**
 * Every check a page run registers must have examined something on a real page.
 *
 * build_scorecard.mjs Guard 2 is the corpus-level alarm for a check that ran and judged
 * nothing, but it only fires when somebody runs it — and for most of this harness's life
 * nobody did, because `test:render:pages` stopped at Playwright. It is now chained after the
 * page run (package.json), and this is the other half: the scorecards on disk are the
 * durable record of the last page run, so the meta gate reads them and refuses a registered,
 * non-deferred check whose examined count is zero across the newest card of every target.
 * A skip, never a pass, when no target has a card: no data must not read as verified.
 *
 * This reads the last successful scorecard run; the runner's exit code (Guard 2) is the live
 * guard. So a check registered SINCE that run has no key in any card: it is reported by name
 * as "not yet measured" (annotation + console), never failed — the next full page run's Guard 2
 * judges it. Only a check the cards DID measure, at zero everywhere, fails here.
 */
test.describe('zero-examined guard: every non-deferred check examined > 0 in the latest scorecards', () => {
  const here = dirname(fileURLToPath(import.meta.url));
  const root = resolve(here, '..', '..');
  const targetsFile = JSON.parse(readFileSync(resolve(here, 'targets.json'), 'utf8')) as {
    deferred_checks?: Record<string, string>;
    pages: { slug: string }[];
  };

  test('latestCards keeps the newest card per slug and only the slugs asked for', () => {
    const cards = [
      { slug: 'a', date: '2026-09-16', examined_by_check: { x: 5 } },
      { slug: 'a', date: '2026-09-22', examined_by_check: { x: 0 } },
      { slug: 'b', date: '2026-09-19', examined_by_check: { x: 1 } },
      { slug: 'gone', date: '2026-09-22', examined_by_check: { x: 9 } },
    ];
    const got = latestCards(cards, ['a', 'b']).map((c) => `${c.slug}@${c.date}`).sort();
    expect(got).toEqual(['a@2026-09-22', 'b@2026-09-19']);
  });

  const synthetic = [
    { slug: 'a', date: '2026-09-22', examined_by_check: { live: 3, dead: 0, parked: 0 } },
    { slug: 'b', date: '2026-09-22', examined_by_check: { live: 1, dead: 0 } },
  ];

  test('zeroExamined names a measured check that judged nothing, and never a deferred or unmeasured one', () => {
    expect(zeroExamined(['live', 'dead', 'parked', 'unwired'], { parked: 'reason' }, synthetic)).toEqual([
      'dead',
    ]);
  });

  test('notYetMeasured names a registered check absent from every card, and never a deferred one', () => {
    expect(
      notYetMeasured(['live', 'dead', 'parked', 'unwired', 'shelved'], { shelved: 'reason' }, synthetic),
    ).toEqual(['unwired']);
  });

  test('readScorecards names the file it could not parse', () => {
    const dir = mkdtempSync(join(tmpdir(), 'cards-'));
    try {
      writeFileSync(join(dir, 'good-2026-09-22.json'), JSON.stringify({ slug: 'good', date: '2026-09-22' }));
      writeFileSync(join(dir, 'broken-2026-09-22.json'), '{ not json');
      expect(() => readScorecards(dir)).toThrow(/broken-2026-09-22\.json/);
      expect(readScorecards(join(dir, 'absent'))).toEqual([]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('the REAL latest scorecards examined every registered, non-deferred check', () => {
    const cards = latestCards(
      readScorecards(join(root, 'data', 'quality', 'scorecards')),
      targetsFile.pages.map((p) => p.slug),
    );
    if (cards.length === 0) {
      test.skip(true, 'no scorecard for any target — run `npm run test:render:pages` (it builds them)');
      return;
    }
    const ids = registry.map((c) => c.id);
    const deferred = targetsFile.deferred_checks ?? {};
    const unmeasured = notYetMeasured(ids, deferred, cards);
    if (unmeasured.length > 0) {
      const note =
        `not yet measured (no key in the newest scorecard of any target; the next full ` +
        `\`npm run test:render:pages\` judges them): ${unmeasured.join(', ')}`;
      test.info().annotations.push({ type: 'not yet measured', description: note });
      console.warn(note);
    }
    const dead = zeroExamined(ids, deferred, cards);
    expect(
      dead,
      `examined zero nodes across the newest scorecard of ${cards.length} target page(s): ` +
        `${dead.join(', ')} — a check that judged nothing is not a pass. Point it at markup the ` +
        `pages really carry, or defer it in targets.json with a promotion condition.`,
    ).toEqual([]);
  });
});

/**
 * The image class a rebuilt page really renders.
 *
 * `layout-h3-image-first` counted only `img.sec-img`, which ships on /kit-preview/ alone:
 * every rebuilt page renders its body photographs through src/components/BodyImage.astro as
 * `img.bl-img`, so on the pages rule 17 puts an image under every H3 the check examined zero
 * blocks. This pair is BodyImage's own markup.
 */
test.describe('layout-h3-image-first [BodyImage .bl-img]', () => {
  const check = () => registry.find((c) => c.id === 'layout-h3-image-first')!;

  test('is silent when each H3 opens on its body photograph', async ({ page }, testInfo) => {
    const res = await page.goto(`${FIXTURE_BASE}/tests/render/fixtures/known_good/h3-image-first-bl-img.html`);
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined, 'both H3 blocks own a .bl-img').toBe(2);
    expect(r.defects.map((d) => d.message)).toEqual([]);
  });

  test('fires when the body photograph follows the prose', async ({ page }, testInfo) => {
    const res = await page.goto(`${FIXTURE_BASE}/tests/render/fixtures/known_broken/h3-image-first-bl-img.html`);
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined).toBe(2);
    expect(r.defects[0]?.count, 'both blocks are offenders').toBe(2);
  });
});

/**
 * Promotion is a record, not a flag flip.
 *
 * targets.json's `_comment` says a check enters advisory and is promoted after it has
 * passed its fixtures and made zero false reports across one full cluster — and until the
 * parity plan's Task 14 nothing recorded when that had happened, so `blocking` checks carried
 * no evidence of an advisory period at all. `promotions` is that record: every blocking check
 * has an entry, and a `new-pages` entry makes an advisory check blocking on the project 5
 * pages only (new-family page type, rebuilt from its board, not one of the twelve frozen
 * pages — `new_page_rule`, pinned to scripts/family_rules.py by tests/py/test_targets_coverage.py).
 */
test.describe('promotions: every blocking check is on record, and new-page promotions bind new pages only', () => {
  const here = dirname(fileURLToPath(import.meta.url));
  const t = JSON.parse(readFileSync(resolve(here, 'targets.json'), 'utf8')) as {
    promotions: Record<string, Promotion>;
    new_page_rule: NewPageRule;
  };
  const rule: NewPageRule = {
    page_types: ['location', 'comparison', 'blog'],
    built_before: ['blue-staffy-blog-guides'],
    excluded_prefix: '_',
    or_board_approved: true,
  };
  const rebuilt = new Set(['blue-staffy-puppies-hull', 'blue-staffy-blog-guides', 'index']);
  const promo: Record<string, Promotion> = {
    promoted: { scope: 'new-pages', since: '2026-09-26', cluster_cleared: 'x', false_reports: 0 },
  };

  test('isNewPage is a new-family, rebuilt, unfrozen page — by route or by bare key', () => {
    expect(isNewPage({ slug: 'uk-locations/blue-staffy-puppies-hull', page_type: 'location' }, rule, rebuilt)).toBe(true);
    expect(isNewPage({ slug: 'uk-locations/blue-staffy-puppies-leeds', page_type: 'location' }, rule, rebuilt)).toBe(false); // migrated, not rebuilt
    expect(isNewPage({ slug: 'blue-staffy-blog-guides', page_type: 'blog' }, rule, rebuilt)).toBe(false); // frozen
    expect(isNewPage({ slug: 'index', page_type: 'home' }, rule, rebuilt)).toBe(false); // not a new family
  });

  test('severityFor blocks a promoted check on a new page and nowhere else', () => {
    const hull = { slug: 'uk-locations/blue-staffy-puppies-hull', page_type: 'location' };
    const leeds = { slug: 'uk-locations/blue-staffy-puppies-leeds', page_type: 'location' };
    expect(severityFor({ id: 'promoted', severity: 'advisory' }, hull, promo, rule, rebuilt)).toBe('blocking');
    expect(severityFor({ id: 'promoted', severity: 'advisory' }, leeds, promo, rule, rebuilt)).toBe('advisory');
    expect(severityFor({ id: 'other', severity: 'advisory' }, hull, promo, rule, rebuilt)).toBe('advisory');
    expect(severityFor({ id: 'other', severity: 'blocking' }, leeds, promo, rule, rebuilt)).toBe('blocking');
  });

  test('every blocking check has a promotions entry with scope all', () => {
    const missing = registry
      .filter((c) => c.severity === 'blocking' && t.promotions[c.id]?.scope !== 'all')
      .map((c) => c.id)
      .sort();
    expect(missing, `blocking with no promotion on record: ${missing.join(', ')}`).toEqual([]);
  });

  test('every promotion names a registered check, fits its severity and records zero false reports', () => {
    const bad: string[] = [];
    for (const [id, p] of Object.entries(t.promotions)) {
      const c = registry.find((x) => x.id === id);
      if (!c) bad.push(`${id}: not a registered check`);
      else if (p.scope === 'all' && c.severity !== 'blocking') bad.push(`${id}: scope all but registered ${c.severity}`);
      else if (p.scope === 'new-pages' && c.severity !== 'advisory') bad.push(`${id}: new-pages scope on a ${c.severity} check`);
      if (!['all', 'new-pages'].includes(p.scope)) bad.push(`${id}: unknown scope ${p.scope}`);
      if (!/^\d{4}-\d{2}-\d{2}$/.test(p.since)) bad.push(`${id}: since ${p.since} is not a date`);
      if (p.false_reports !== 0) bad.push(`${id}: ${p.false_reports} false reports — not promotable`);
      if (!(p.cluster_cleared ?? '').trim()) bad.push(`${id}: no cluster_cleared evidence`);
    }
    expect(bad).toEqual([]);
  });

  test('a new page is new from board approval on, before it is in rebuilt.json', () => {
    const york = { slug: 'uk-locations/blue-staffy-puppies-york', page_type: 'location' };
    const leeds = { slug: 'uk-locations/blue-staffy-puppies-leeds', page_type: 'location' };
    const boards = new Set(['uk-locations--blue-staffy-puppies-york', '_demo', 'blue-staffy-blog-guides']);
    // Approved board, not yet rebuilt: the four checks already block its first build.
    expect(isNewPage(york, rule, rebuilt, boards)).toBe(true);
    expect(severityFor({ id: 'promoted', severity: 'advisory' }, york, promo, rule, rebuilt, boards)).toBe('blocking');
    // Bare-key board spelling is found too.
    expect(isNewPage(york, rule, rebuilt, new Set(['blue-staffy-puppies-york']))).toBe(true);
    // A legacy city page has no board and is not rebuilt: advisory.
    expect(isNewPage(leeds, rule, rebuilt, boards)).toBe(false);
    expect(severityFor({ id: 'promoted', severity: 'advisory' }, leeds, promo, rule, rebuilt, boards)).toBe('advisory');
    // A frozen page and a `_` fixture stay out whatever their board says.
    expect(isNewPage({ slug: 'blue-staffy-blog-guides', page_type: 'blog' }, rule, rebuilt, boards)).toBe(false);
    expect(isNewPage({ slug: '_demo', page_type: 'blog' }, rule, rebuilt, boards)).toBe(false);
    // With or_board_approved off, the board alone is not enough.
    expect(isNewPage(york, { ...rule, or_board_approved: false }, rebuilt, boards)).toBe(false);
  });

  test('approvedBoards reads approval or approval_previous and nothing else', () => {
    const dir = mkdtempSync(join(tmpdir(), 'boards-'));
    try {
      writeFileSync(join(dir, 'uk-locations--a.json'), JSON.stringify({ approval: { approved_at: 'x' } }));
      writeFileSync(join(dir, 'b.json'), JSON.stringify({ approval: null, approval_previous: { approved_at: 'x' } }));
      writeFileSync(join(dir, 'c.json'), JSON.stringify({ approval: null }));
      writeFileSync(join(dir, 'notes.txt'), 'not a board');
      expect([...approvedBoards(dir)].sort()).toEqual(['b', 'uk-locations--a']);
      expect([...approvedBoards(join(dir, 'missing'))]).toEqual([]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('targets.json records the board-approval condition and the fixture prefix', () => {
    expect(t.new_page_rule.or_board_approved).toBe(true);
    expect(t.new_page_rule.excluded_prefix).toBe('_');
  });

  test('the four project 5 promotions are on record', () => {
    for (const id of [
      'layout-hero-counter-separation',
      'layout-h3-image-first',
      'sem-section-opening-paragraph',
      'sem-title-case-headings',
    ]) {
      expect(t.promotions[id]?.scope, id).toBe('new-pages');
    }
  });
});

/**
 * layout-hero-image-first-mobile has two halves (source order, paint order), and the generic
 * fixture pair fires on the SOURCE half at every width — so on its own it could not tell a
 * working paint half from a dead one. This fixture has the source order right and the paint
 * order wrong below 900px, which is exactly what Hero.astro shipped before 2026-09-27.
 */
test.describe('layout-hero-image-first-mobile sees a paint-order defect on its own', () => {
  test('fires on one-column widths and is silent at 1280', async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto(fixtureUrl('known_broken', 'hero-image-first-order-only'));
    expect(res?.status(), 'fixture must load').toBe(200);
    const check = registry.find((c) => c.id === 'layout-hero-image-first-mobile')!;
    const r = await runCheck(check, page, viewport, FIXTURE_CTX);
    expect(r.examined, 'one hero with a photo and a heading').toBe(1);
    if (viewport <= 900) {
      expect(r.defects.length, 'the paint half must fire without the source half').toBe(1);
      expect(r.defects[0].message).toContain('paints');
    } else {
      expect(r.defects.map((d) => d.message), 'two columns: nothing to paint in order').toEqual([]);
    }
  });
});

/**
 * img-face-visible has two halves (the crop, the overlay), and the generic fixture pair fires on
 * the OVERLAY half (the Vennie plate). This fixture has nothing painted over the photograph and
 * a crop that shows only the top of Roman's head, so it proves the crop half works on its own.
 */
test.describe('img-face-visible sees a cropped face on its own', () => {
  test('fires at every width with a crop message', async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto(fixtureUrl('known_broken', 'img-face-visible-crop'));
    expect(res?.status(), 'fixture must load').toBe(200);
    const check = registry.find((c) => c.id === 'img-face-visible')!;
    const r = await runCheck(check, page, viewport, FIXTURE_CTX);
    expect(r.examined, 'one recorded photograph').toBe(1);
    expect(r.defects.length, 'the crop half must fire without an overlay').toBe(1);
    expect(r.defects[0].message).toContain('% painted');
  });
});

/**
 * The crop half must read the RESOLVED object-position. Neither fixture above can tell: the
 * Vennie pair is a square photo in a square tile (position moves nothing) and the Roman letterbox
 * cuts his head wherever it is pinned. Here a centred crop would cut Vennie's muzzle, and the
 * page's own position keeps her whole face — a check that assumed 50% 50% cries wolf.
 */
test.describe('img-face-visible reads object-position', () => {
  test('is silent on a letterbox pinned to a low face', async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto(fixtureUrl('known_good', 'img-face-visible-position'));
    expect(res?.status(), 'fixture must load').toBe(200);
    const check = registry.find((c) => c.id === 'img-face-visible')!;
    const r = await runCheck(check, page, viewport, FIXTURE_CTX);
    expect(r.examined, 'one recorded photograph').toBe(1);
    expect(r.defects.map((d) => d.message), 'a positioned crop that shows the face').toEqual([]);
  });
});
