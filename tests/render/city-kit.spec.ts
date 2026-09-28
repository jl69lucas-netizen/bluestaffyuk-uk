import { test, expect, type Page } from '@playwright/test';
import { registry } from './lib/registry.js';
import { runCheck } from './lib/runCheck.js';
import './checks/layout.js';
import './checks/a11y.js';
import './checks/img.js';
import './checks/nav.js';

/**
 * The city-kit render spec (the London component design pass, Plan 2). Every built page that
 * carries city components — the specimen page /kit-preview/city/ and, from Plan 2 Task 8, the
 * London scaffold — is painted at 375, 768, 1024 and 1280 (tests/render/city-kit.config.ts) and
 * held to:
 *   - the registered checks in REUSED, run as they are; those in CITY_ADVISORY print their hits
 *     as `[advisory]` lines and never fail (a new check earns blocking after a clean cluster);
 *   - each city component's probe in PROBES, keyed on the data hooks the component renders (the
 *     same hooks scripts/check_city_canvas.py HOOKS required of the canvas variants), run only
 *     where that component is on the page.
 * The kit's page harness (pages.spec.ts) paints 375/768/1280 only; this spec is where 1024 — the
 * dial's and rule 10's boundary — is measured for the city set. A component that fails here is
 * fixed in the component, never excused here.
 */
const ROUTES = ['/kit-preview/city/'];
const REUSED = [
  'layout-no-horizontal-overflow',
  'layout-min-font-size',
  'layout-tap-target-size',
  'layout-table-stacks-on-mobile',
  'layout-image-box-reserved',
  'layout-hero-image-first-mobile',
  'layout-h3-image-first',
  'a11y-text-contrast-aa',
  'a11y-no-duplicate-ids',
  'img-alt-present-and-unique',
  'img-srcset-within-2x',
  'img-sizes-matches-box',
  'img-not-upscaled',
  'nav-anchors-resolve',
];
// Named, never derived from registry severity (the canvas smoke's lesson, 4214d23).
const CITY_ADVISORY = new Set(['img-not-upscaled']);
const CTX = { pageType: 'location', slug: 'city-kit', siblings: async () => [] };

type Probe = (page: Page, viewport: number) => Promise<string[]>;

/** Every element carrying `attr` is painted (a box of at least 1×1 and not visibility:hidden). */
async function allVisible(page: Page, attr: string): Promise<string[]> {
  const hidden = await page.evaluate((a) => Array.from(document.querySelectorAll(`[${a}]`))
    .filter((el) => {
      const b = el.getBoundingClientRect();
      return b.width < 1 || b.height < 1 || getComputedStyle(el).visibility === 'hidden';
    }).length, attr);
  return hidden ? [`${hidden} [${attr}] element(s) are not painted`] : [];
}

/** Each probe: the selector that says its component is on the page, and what it measures. */
const PROBES: Record<string, { present: string; run: Probe }> = {
  'city-hero': {
    present: '.city-hero',
    run: async (page, viewport) => {
      const out: string[] = [];
      const band = await page.evaluate(() =>
        Math.round(document.querySelector('.city-hero')!.getBoundingClientRect().height));
      // rules/design.md rule 10: 390px floor from 1024, 450px ceiling at 1280 and up.
      if (viewport >= 1024 && band < 390) out.push(`hero band is ${band}px at ${viewport}px; the floor is 390`);
      if (viewport >= 1280 && band > 450) out.push(`hero band is ${band}px at ${viewport}px; the ceiling is 450`);
      const thumbs = await page.evaluate(() => document.querySelectorAll('.city-hero .pic img').length);
      if (thumbs < 1) out.push('the filmstrip paints no puppy');
      return out;
    },
  },
  'city-price-scale': {
    present: '.city-scale',
    run: async (page) => {
      const out = await allVisible(page, 'data-figure');
      // The stops are laid on one line: every figure's box stays inside the panel.
      const spill = await page.evaluate(() => {
        const panel = document.querySelector('.city-scale .panel')!.getBoundingClientRect();
        return Array.from(document.querySelectorAll('.city-scale [data-figure]'))
          .filter((f) => { const b = f.getBoundingClientRect(); return b.left < panel.left - 1 || b.right > panel.right + 1; }).length;
      });
      if (spill) out.push(`${spill} figure(s) run outside the panel`);
      return out;
    },
  },
  'city-trust-ledger': {
    present: '.city-trust',
    run: (page) => allVisible(page, 'data-trust-item'),
  },
};

for (const route of ROUTES) {
  test(`city components on ${route}`, async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto(route);
    expect(res?.status(), `${route} must be built`).toBe(200);
    await page.evaluate(() => document.fonts.ready);
    // CITY_SHOTS=<dir> keeps a full-page PNG per width for the impeccable and frontend-design
    // passes to read. Outside the repo, never committed.
    if (process.env.CITY_SHOTS) {
      await page.screenshot({ fullPage: true,
        path: `${process.env.CITY_SHOTS}/${route.replace(/\//g, '_')}-${viewport}.png` });
    }
    const failures: string[] = [];
    for (const id of REUSED) {
      const check = registry.find((c) => c.id === id);
      expect(check, `${id} is registered`).toBeTruthy();
      const r = await runCheck(check!, page, viewport, CTX);
      console.log(`${route} @ ${viewport}px ${id}: examined ${r.examined}`);
      for (const d of r.defects) {
        if (CITY_ADVISORY.has(id)) {
          console.log(`[advisory] ${route} @ ${viewport}px ${id}: ${d.message}`);
          testInfo.annotations.push({ type: 'advisory', description: `${id}: ${d.message}` });
        } else failures.push(`${id}: ${d.message}`);
      }
    }
    let probed = 0;
    for (const [id, probe] of Object.entries(PROBES)) {
      await page.evaluate(() => window.scrollTo(0, 0));
      if (!(await page.locator(probe.present).count())) continue;
      probed++;
      failures.push(...(await probe.run(page, viewport)).map((m) => `${id}: ${m}`));
    }
    expect(probed, `${route} carries no city component a probe knows`).toBeGreaterThan(0);
    expect(failures, `${route} at ${viewport}px`).toEqual([]);
  });
}
