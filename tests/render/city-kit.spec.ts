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
  },  'city-contents': {
    present: '.city-contents',
    run: async (page, viewport) => {
      const out = await allVisible(page, 'data-contents');
      const rest = page.locator('.city-contents [data-rest]');
      if (!(await rest.count())) return out;
      const shown = async () => rest.first().isVisible();
      if (viewport < 640) {
        if (await shown()) out.push('rows after the phone cut are painted before the disclosure is opened');
        const more = page.locator('.city-contents [data-more]');
        await more.click();
        if (!(await shown())) out.push('opening the disclosure does not paint the rest of the rows');
        if ((await more.getAttribute('aria-expanded')) !== 'true') out.push('the disclosure does not report aria-expanded="true"');
        await more.click();
      } else if (!(await shown())) out.push(`rows after the fifth are hidden at ${viewport}px`);
      return out;
    },
  },
  'city-dial': {
    present: '[data-city-dial]',
    run: async (page, viewport) => {
      const out: string[] = [];
      const shown = await page.locator('[data-city-dial]').isVisible();
      if (viewport >= 1024 && !shown) out.push('the dial is not painted at a desktop width');
      if (viewport < 1024 && shown) out.push('the dial is painted below 1024px, where the jump band navigates');
      const current = await page.locator('[data-city-dial] [aria-current="location"]').count();
      if (current !== 1) out.push(`${current} dial rows are marked current; exactly one must be`);
      return out;
    },
  },
  'city-jump-band': {
    present: '[data-city-jump]',
    run: async (page, viewport) => {
      const out: string[] = [];
      const band = page.locator('[data-city-jump]');
      const shown = await band.isVisible();
      if (viewport >= 1024) {
        if (shown) out.push('the jump band is painted at a desktop width, where the dial navigates');
        return out;
      }
      if (!shown) return ['the jump band is not painted below 1024px'];
      if (await band.getAttribute('data-strip') !== null) {
        await page.evaluate(() => window.scrollTo(0, 900));
        await page.waitForTimeout(150);
        const top = await band.evaluate((el) => el.getBoundingClientRect().top);
        if (top < -1 || top > 160) out.push(`after a 900px scroll the band sits at ${Math.round(top)}px, not under the header`);
        await page.evaluate(() => window.scrollTo(0, 0));
      }
      const opener = band.locator('[data-jump-open]');
      const box = await opener.boundingBox();
      if (!box || box.height < 44) out.push('the sheet key is under 44px tall');
      await opener.click();
      const open = await band.locator('[data-jump-sheet]').evaluate((d) => (d as HTMLDialogElement).open);
      if (!open) out.push('pressing the key does not open the sheet');
      if ((await opener.getAttribute('aria-expanded')) !== 'true') out.push('the key does not report aria-expanded="true"');
      await page.keyboard.press('Escape');
      const closed = await band.locator('[data-jump-sheet]').evaluate((d) => !(d as HTMLDialogElement).open);
      if (!closed) out.push('Escape does not close the sheet');
      if ((await opener.getAttribute('aria-expanded')) !== 'false') out.push('after Escape the key still reports aria-expanded="true"');
      return out;
    },
  },
  'city-takeaways': {
    present: '.city-takeaways',
    run: (page) => allVisible(page, 'data-takeaway'),
  },
  'city-puppy-sheet': {
    present: '.city-sheet',
    run: async (page) => {
      const out = await allVisible(page, 'data-puppy');
      // One tap target per print: the Ask link's box is the whole print.
      // Each print is scrolled to the middle of the viewport first, clear of the sticky chrome,
      // and the point tested is on its photograph.
      const small = await page.evaluate(() => Array.from(document.querySelectorAll('.city-pup')).filter((card) => {
        card.scrollIntoView({ block: 'center' });
        const a = card.querySelector('.ask')!;
        const img = card.querySelector('img')!.getBoundingClientRect();
        const hit = document.elementFromPoint(img.left + img.width / 2, img.top + img.height / 2);
        return !(hit === a || a.contains(hit!));
      }).length);
      if (small) out.push(`${small} print(s) whose photo does not hand the tap to its Ask link`);
      return out;
    },
  },
  'city-roster': {
    present: '.city-roster',
    run: async (page, viewport) => {
      const out: string[] = [];
      if (viewport <= 640) {
        const overlap = await page.evaluate(() => Array.from(document.querySelectorAll('.city-roster tbody tr')).filter((tr) => {
          const price = tr.querySelector('td.num')!.getBoundingClientRect();
          // The name's TEXT, not its block box (which runs the row's width by design).
          const range = document.createRange();
          range.selectNodeContents(tr.querySelector('.nm')!);
          const name = range.getBoundingClientRect();
          return price.left < name.right - 1 && price.top < name.bottom - 1 && price.bottom > name.top + 1;
        }).length);
        if (overlap) out.push(`${overlap} stacked row(s) paint the price over the name`);
      }
      return out;
    },
  },
  'city-video-panel': {
    present: '.city-video',
    run: async (page) => {
      const out: string[] = [];
      const play = page.locator('.city-video [data-video-play]');
      const box = await play.boundingBox();
      if (!box || box.width < 44 || box.height < 44) out.push('the play control is under 44×44px');
      const name = (await play.getAttribute('aria-label')) ?? '';
      const label = ((await play.locator('.badge-label').textContent()) ?? '').trim();
      if (!name.startsWith(label)) out.push(`the play button's name "${name}" does not contain its visible label "${label}" (WCAG 2.5.3)`);
      await play.click();
      const src = await page.locator('.city-video iframe').first().getAttribute('src');
      if (!src || !/youtube-nocookie\.com\/embed\//.test(src)) out.push('pressing play does not load the youtube-nocookie player');
      return out;
    },
  },
  'city-chapters': {
    present: '.city-chapters',
    run: async (page) => {
      const out: string[] = [];
      const bad = await page.evaluate(() => Array.from(document.querySelectorAll('.city-chapters h3')).filter((h) => {
        const next = h.nextElementSibling;
        return !next || !next.matches('img.bl-img');
      }).length);
      if (bad) out.push(`${bad} chapter heading(s) not followed straight by their .bl-img photo (layout-h3-image-first)`);
      return out;
    },
  },
  'city-letter': {
    present: '.city-letter',
    run: (page) => allVisible(page, 'data-review-slot'),
  },
  // Learning loop 2026-09-27, L8: the current-section marker, under BOTH motion preferences.
  // Scroll the fourth section to the reading band and read which row is current, on the dial at
  // a desktop width and on the band's rail below it.
  'city-nav-current-section': {
    present: '[data-city-dial], [data-city-jump]',
    run: async (page, viewport) => {
      const out: string[] = [];
      const scope = viewport >= 1024 ? '[data-city-dial]' : '[data-city-jump] .rail';
      if (!(await page.locator(scope).isVisible())) return out;
      for (const motion of ['reduce', 'no-preference'] as const) {
        await page.emulateMedia({ reducedMotion: motion });
        const want = await page.evaluate((s) => {
          const links = Array.from(document.querySelectorAll<HTMLAnchorElement>(`${s} [data-spy]`));
          const link = links[Math.min(3, links.length - 1)];
          const target = document.getElementById(link.dataset.spy!)!;
          // The target's top at 30% of the viewport: above the reading band (40–45%), so the
          // section before it has left the band and this one fills it.
          window.scrollTo(0, target.getBoundingClientRect().top + window.scrollY - window.innerHeight * 0.3);
          return link.dataset.spy!;
        }, scope);
        await page.waitForTimeout(300);
        const got = await page.evaluate((s) => Array.from(document.querySelectorAll(`${s} [aria-current="location"]`))
          .map((a) => (a as HTMLAnchorElement).dataset.spy), scope);
        if (got.length !== 1 || got[0] !== want) {
          out.push(`reducedMotion=${motion}: section ${want} in the reading band, current is [${got.join(', ')}]`);
        }
      }
      await page.emulateMedia({ reducedMotion: null });
      return out;
    },
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
