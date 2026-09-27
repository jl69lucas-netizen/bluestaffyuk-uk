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
 *   - the registered checks in REUSED, run as they are (no second copy of their logic); an
 *     advisory one (img-not-upscaled) prints its hits as `[advisory]` lines and never fails;
 *   - the component's own probe in PROBES (the hero's photo-first rule, the jump links'
 *     sticky strip, the dial's desktop-only display, the six puppy cards, …), keyed on the
 *     data hooks scripts/check_city_canvas.py HOOKS requires.
 * A variant that fails here is fixed in its fragment, never excused here.
 */
const here = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(here, '../..');
// CANVAS_FRAMES_INDEX replays another emit (a past revision's fragments, emitted with
// build_component_canvas.py --root <dir> --emit-frames docs/artifacts/canvas/<name>).
const INDEX = resolve(REPO, process.env.CANVAS_FRAMES_INDEX ?? 'docs/artifacts/canvas/london-frames/index.json');
const REUSED = [
  'layout-no-horizontal-overflow',
  'layout-min-font-size',
  'layout-tap-target-size',
  'layout-table-stacks-on-mobile',
  'a11y-text-contrast-aa',
  'a11y-no-duplicate-ids',
  'img-alt-present-and-unique',
  'img-not-upscaled',
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
  'key-takeaways': (page) => allVisible(page, 'data-takeaway'),
  'puppy-cards': async (page) => {
    const out = await allVisible(page, 'data-puppy');
    const texts = await page.evaluate(() =>
      Array.from(document.querySelectorAll('[data-puppy]')).map((c) => c.textContent || ''));
    const missing = PUPPY_NAMES.filter((n) => !texts.some((t) => t.includes(n)));
    if (missing.length) out.push(`no card for ${missing.join(', ')} (data/puppies.json)`);
    return out;
  },
  tables: async (page) => {
    const n = await page.evaluate(() => document.querySelectorAll('main table').length);
    return n ? [] : ['no <table> in main, so layout-table-stacks-on-mobile examined nothing'];
  },
  video: async (page) => {
    const out = await brokenImages(page);
    const box = await page.locator('[data-play]').boundingBox();
    if (!box || box.width < 44 || box.height < 44) out.push('the play control is under 44×44px');
    return out;
  },
  'image-text': async (page) => [...(await allVisible(page, 'data-media')), ...(await brokenImages(page))],
  reviews: (page) => allVisible(page, 'data-review-slot'),
  'faq-blocks': async (page) => {
    const out = await allVisible(page, 'data-faq-block');
    const before = await page.evaluate(() => {
      const d = document.querySelector('[data-faq-q]')?.closest('details');
      return d ? d.open : null;
    });
    if (before !== null) {
      await page.locator('[data-faq-q]').first().click();
      const after = await page.evaluate(() => document.querySelector('[data-faq-q]')!.closest('details')!.open);
      if (after === before) out.push('pressing the first question does not toggle its answer');
    }
    return out;
  },
  newsletter: (page) => fieldsTall(page, '[data-newsletter]'),
  'contact-form': (page) => fieldsTall(page, '[data-contact-form]'),
};


/**
 * Declared axes vs the paint (learning loop 2026-09-27, shortlist #3). check_city_canvas.py
 * enforces "≥ 2 axes from every must-differ row" on the axes a variant DECLARES in meta.json;
 * six variants passed it while painting something else (a declared `inset` drawn as a raised
 * card, a "contact sheet" whose only photos sat inside the cards). This probe measures the two
 * axes that are readable from paint, at the desktop width the axes describe, and fails on a
 * contradiction. It reads media at SECTION level (the hardening-log's Task 7 convention): an
 * image inside a repeated item (two or more of one data hook — puppy cards, figures, review
 * slots, …) is that item's, not the section's; anything under [data-canvas-only] is ignored.
 *   framing — a section-level container (≥ 40% of the section wide, ≥ 30% of it tall) with an
 *             outer box-shadow paints as a card, so it must be declared `card`.
 *   media   — `none` means no section-level image is painted; any other value means one is;
 *             `left`/`right` mean one sits left/right of the section's centre, `top`/`bottom`
 *             one centred above/below its middle, `background` one covering ≥ 60% of it.
 * layout and density stay the reviewer's. jump-links is measured for framing only: its media
 * lives in the phone strip and sheet, which are not painted at a desktop width.
 */
type Axes = { layout: string; media: string; density: string; framing: string };
const AXES_WIDTH = 1280;
const ITEM_HOOKS = ['data-figure', 'data-trust-item', 'data-takeaway', 'data-puppy',
  'data-review-slot', 'data-faq-q', 'data-faq-block'];

async function axesMatchPaint(page: Page, component: string, axes: Axes): Promise<string[]> {
  const got = await page.evaluate((hooks) => {
    const sec = document.querySelector('[data-component]')!;
    const sb = sec.getBoundingClientRect();
    const painted = (el: Element) => {
      const b = el.getBoundingClientRect();
      if (b.width < 2 || b.height < 2) return false;
      for (let e: Element | null = el; e; e = e.parentElement) {
        const cs = getComputedStyle(e);
        if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') return false;
      }
      return true;
    };
    const repeated = hooks.filter((h) => sec.querySelectorAll(`[${h}]`).length >= 2);
    const inItem = (el: Element) => {
      for (let e: Element | null = el; e && e !== sec; e = e.parentElement) {
        if (e.hasAttribute('data-canvas-only') || repeated.some((h) => e!.hasAttribute(h))) return true;
      }
      return false;
    };
    const imgs: { x: number; y: number; w: number; h: number }[] = [];
    let cards = 0;
    for (const el of [sec, ...Array.from(sec.querySelectorAll('*'))]) {
      if (el !== sec && inItem(el)) continue;
      if (!painted(el)) continue;
      const cs = getComputedStyle(el);
      const b = el.getBoundingClientRect();
      if (el.tagName === 'IMG' || /url\(/.test(cs.backgroundImage)) {
        imgs.push({ x: b.left - sb.left, y: b.top - sb.top, w: b.width, h: b.height });
      }
      const outer = cs.boxShadow !== 'none'
        && cs.boxShadow.split(/,(?![^(]*\))/).some((sh) => !sh.includes('inset'));
      if (outer && b.width >= 0.4 * sb.width && b.height >= 0.3 * sb.height) cards += 1;
    }
    return { w: sb.width, h: sb.height, imgs, cards };
  }, ITEM_HOOKS);
  const out: string[] = [];
  const say = (axis: string, why: string) => out.push(`declared ${axis} "${(axes as any)[axis]}" but ${why}`);
  if (got.cards && axes.framing !== 'card') say('framing', 'a section-level container casts an outer shadow (a card)');
  if (component === 'jump-links') return out;
  const { imgs, w, h } = got;
  if (axes.media === 'none') {
    if (imgs.length) say('media', `${imgs.length} section-level image(s) are painted`);
    return out;
  }
  if (!imgs.length) {
    say('media', 'no section-level image is painted (images inside repeated items are the items\')');
    return out;
  }
  const cx = (i: typeof imgs[0]) => i.x + i.w / 2;
  const cy = (i: typeof imgs[0]) => i.y + i.h / 2;
  const side: Record<string, () => boolean> = {
    left: () => imgs.some((i) => cx(i) < w / 2),
    right: () => imgs.some((i) => cx(i) > w / 2),
    top: () => imgs.some((i) => cy(i) < h / 2),
    bottom: () => imgs.some((i) => cy(i) > h / 2),
    background: () => imgs.some((i) => i.w * i.h >= 0.6 * w * h),
  };
  if (side[axes.media] && !side[axes.media]()) say('media', `no section-level image is painted to the ${axes.media}`);
  return out;
}

type Frame = { component: string; variant: string; path: string; axes?: Axes };
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
      for (const d of r.defects) {
        // An advisory check reports and never fails the smoke (bsuk-learning-loop Step 4: a new
        // check earns blocking after a clean cluster). Its hits are printed and annotated.
        if (check!.severity === 'advisory') {
          console.log(`[advisory] ${f.component}/${f.variant} @ ${viewport}px ${id}: ${d.message}`);
          testInfo.annotations.push({ type: 'advisory', description: `${id}: ${d.message}` });
        } else failures.push(`${id}: ${d.message}`);
      }
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    const probe = PROBES[f.component];
    if (probe) failures.push(...(await probe(page, viewport)));
    if (viewport === AXES_WIDTH) {
      if (!f.axes) failures.push('the frame index carries no declared axes (re-emit the frames)');
      else failures.push(...(await axesMatchPaint(page, f.component, f.axes)).map((m) => `axes: ${m}`));
    }
    expect(failures, `${f.component}/${f.variant} at ${viewport}px`).toEqual([]);
  });
}
