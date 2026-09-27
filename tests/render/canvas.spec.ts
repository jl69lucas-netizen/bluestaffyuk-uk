import { test, expect, type Page } from '@playwright/test';
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { registry } from './lib/registry.js';
import { runCheck } from './lib/runCheck.js';
import './checks/layout.js';
import './checks/a11y.js';
import './checks/img.js';

/**
 * The London component canvas smoke (docs/superpowers/plans/2026-09-27-london-component-design-pass.md).
 * Every variant frame scripts/build_component_canvas.py --emit-frames wrote is painted at 375,
 * 768 and 1280 and held to:
 *   - the registered checks in REUSED, run as they are (no second copy of their logic);
 *   - the component's own probe in PROBES (the hero's photo-first rule, the jump links'
 *     sticky strip, the dial's desktop-only display, the six puppy cards, …), keyed on the
 *     data hooks scripts/check_city_canvas.py HOOKS requires.
 * A variant that fails here is fixed in its fragment, never excused here.
 */
const here = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(here, '../..');
const INDEX = resolve(REPO, 'docs/artifacts/canvas/london-frames/index.json');
const REUSED = [
  'layout-no-horizontal-overflow',
  'layout-min-font-size',
  'layout-tap-target-size',
  'layout-table-stacks-on-mobile',
  'a11y-text-contrast-aa',
  'a11y-no-duplicate-ids',
  'img-alt-present-and-unique',
];
const CTX = { pageType: 'location', slug: 'canvas', siblings: async () => [] };
const PUPPY_NAMES: string[] = JSON.parse(readFileSync(resolve(REPO, 'data/puppies.json'), 'utf8'))
  .map((p: { name: string }) => p.name);

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

/** Every in-frame jump link inside `scope` lands on an element that exists. */
async function anchorsResolve(page: Page, scope: string): Promise<string[]> {
  const dead = await page.evaluate((s) => Array.from(document.querySelectorAll(`${s} a[href^="#"]`))
    .map((a) => a.getAttribute('href')!.slice(1))
    .filter((id) => id && !document.getElementById(id)), scope);
  return dead.length ? [`jump links to missing ids: ${dead.join(', ')}`] : [];
}

/** Painted, or not, as a whole: display none on the element or an ancestor reads as hidden. */
async function isShown(page: Page, sel: string): Promise<boolean> {
  return page.evaluate((s) => {
    const el = document.querySelector(s);
    if (!el) return false;
    const b = el.getBoundingClientRect();
    return b.width > 0 && b.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  }, sel);
}

/** Images that finished loading with no pixels: a poster or photo path that is wrong. */
async function brokenImages(page: Page): Promise<string[]> {
  const n = await page.evaluate(() =>
    Array.from(document.images).filter((i) => i.complete && i.naturalWidth === 0).length);
  return n ? [`${n} image(s) failed to load`] : [];
}

/** Every field and button a person presses inside `scope` is at least 44px tall. */
async function fieldsTall(page: Page, scope: string): Promise<string[]> {
  const short = await page.evaluate((s) => Array.from(document.querySelectorAll(
    `${s} input:not([type="hidden"]), ${s} select, ${s} textarea, ${s} button`))
    .filter((el) => el.getBoundingClientRect().height < 44)
    .map((el) => el.getAttribute('name') || el.tagName.toLowerCase()), scope);
  return short.length ? [`under 44px tall: ${short.join(', ')}`] : [];
}

const PROBES: Record<string, Probe> = {
  hero: async (page, viewport) => {
    const out: string[] = [];
    if (viewport >= 1024) {
      // rules/design.md rule 10: the band is 390–450px tall on desktop, auto on a phone.
      const band = await page.evaluate(() =>
        Math.round(document.querySelector('[data-component="hero"]')!.getBoundingClientRect().height));
      if (band < 390 || band > 450) out.push(`hero band is ${band}px tall at ${viewport}px; rule 10 wants 390–450`);
    }
    const h = await page.evaluate(() => {
      const pic = document.querySelector('main img, main picture');
      const head = document.querySelector('main h1, main h2');
      if (!pic || !head) return 'a hero frame needs a photo and a heading';
      if (!(head.compareDocumentPosition(pic) & Node.DOCUMENT_POSITION_PRECEDING)) {
        return 'the heading precedes the photo in source';
      }
      const oneCol = document.documentElement.clientWidth <= 900;
      if (oneCol && pic.getBoundingClientRect().top >= head.getBoundingClientRect().top) {
        return 'the photo paints below the heading on a one-column width';
      }
      return '';
    });
    if (h) out.push(`hero-image-first: ${h}`);
    return out;
  },
  'counter-strip': (page) => allVisible(page, 'data-figure'),
  'trust-strip': (page) => allVisible(page, 'data-trust-item'),
  'contents-list': async (page) => [
    ...(await allVisible(page, 'data-contents')),
    ...(await anchorsResolve(page, '[data-contents]')),
  ],
  'desktop-dial': async (page, viewport) => {
    const out = await anchorsResolve(page, '[data-dial]');
    const shown = await isShown(page, '[data-dial]');
    if (viewport >= 1024 && !shown) out.push('the dial is not painted at a desktop width');
    if (viewport < 1024 && shown) out.push('the dial is painted below 1024px, where the jump links navigate');
    return out;
  },
  'jump-links': async (page, viewport) => {
    const out = await anchorsResolve(page, '[data-jump-strip]');
    const strip = await isShown(page, '[data-jump-strip]');
    if (viewport >= 1024) {
      if (strip) out.push('the jump strip is painted at a desktop width, where the dial navigates');
      return out;
    }
    if (!strip) return [...out, 'the jump strip is not painted below 1024px'];
    const room = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight);
    if (room < 600) {
      out.push(`the frame scrolls only ${room}px; give it stub sections so the strip can be seen sticking`);
    } else {
      await page.evaluate(() => window.scrollTo(0, 600));
      const top = await page.evaluate(() => document.querySelector('[data-jump-strip]')!.getBoundingClientRect().top);
      if (top < -1 || top > 80) out.push(`after a 600px scroll the strip sits at ${Math.round(top)}px, not stuck to the top`);
      await page.evaluate(() => window.scrollTo(0, 0));
    }
    const opener = page.locator('[data-jump-open]');
    const box = await opener.boundingBox();
    if (!box || box.height < 44) out.push('the sheet opener is under 44px tall');
    await opener.click();
    await page.waitForTimeout(250);
    if (!(await isShown(page, '[data-jump-sheet]'))) out.push('pressing the opener does not show the sheet');
    return out;
  },
};

type Frame = { component: string; variant: string; path: string };
const frames: Frame[] = existsSync(INDEX) ? JSON.parse(readFileSync(INDEX, 'utf8')) : [];

test('the frames were emitted', () => {
  expect(frames.length,
    'run: python3 scripts/build_component_canvas.py --emit-frames docs/artifacts/canvas/london-frames')
    .toBeGreaterThan(0);
});

for (const f of frames) {
  test(`${f.component}/${f.variant}`, async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    const res = await page.goto('/' + f.path);
    expect(res?.status()).toBe(200);
    await page.evaluate(() => document.fonts.ready);
    // CANVAS_SHOTS=<dir> keeps a full-frame PNG of every variant at every width, for the
    // impeccable and frontend-design passes to read. Outside the repo, never committed.
    if (process.env.CANVAS_SHOTS) {
      await page.screenshot({ fullPage: true,
        path: resolve(process.env.CANVAS_SHOTS, `${f.component}-${f.variant}-${viewport}.png`) });
    }
    const failures: string[] = [];
    for (const id of REUSED) {
      const check = registry.find((c) => c.id === id);
      expect(check, `${id} is registered`).toBeTruthy();
      const r = await runCheck(check!, page, viewport, CTX);
      for (const d of r.defects) failures.push(`${id}: ${d.message}`);
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    const probe = PROBES[f.component];
    if (probe) failures.push(...(await probe(page, viewport)));
    expect(failures, `${f.component}/${f.variant} at ${viewport}px`).toEqual([]);
  });
}
