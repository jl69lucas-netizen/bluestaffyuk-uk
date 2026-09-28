import { test, expect, type Page } from '@playwright/test';
import { registry } from './lib/registry.js';
import { runCheck } from './lib/runCheck.js';
import './checks/layout.js';
import './checks/a11y.js';
import './checks/img.js';
import './checks/nav.js';
import { readFileSync } from 'node:fs';
import { cityTypeFit } from './lib/cityTypeFit.js';

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
const ROUTES = ['/kit-preview/city/', '/kit-preview/city-page/'];
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
  'img-face-visible',
  'nav-anchors-resolve',
];
// Named, never derived from registry severity (the canvas smoke's lesson, 4214d23).
const CITY_ADVISORY = new Set(['img-not-upscaled', 'img-face-visible']);
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
  'city-hero-filmstrip': {
    present: '.city-hero-filmstrip',
    run: async (page, viewport) => {
      const out: string[] = [];
      const band = await page.evaluate(() =>
        Math.round(document.querySelector('.city-hero-filmstrip')!.getBoundingClientRect().height));
      // rules/design.md rule 10: 390px floor from 1024, 450px ceiling at 1280 and up.
      if (viewport >= 1024 && band < 390) out.push(`hero band is ${band}px at ${viewport}px; the floor is 390`);
      if (viewport >= 1280 && band > 450) out.push(`hero band is ${band}px at ${viewport}px; the ceiling is 450`);
      const thumbs = await page.evaluate(() => document.querySelectorAll('.city-hero-filmstrip .pic img').length);
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
  'city-contents-photo-index': {
    present: '.city-contents-photo-index',
    run: async (page, viewport) => {
      const out = await allVisible(page, 'data-contents');
      const rest = page.locator('.city-contents-photo-index [data-rest]');
      if (!(await rest.count())) return out;
      const shown = async () => rest.first().isVisible();
      if (viewport < 640) {
        if (await shown()) out.push('rows after the phone cut are painted before the disclosure is opened');
        const more = page.locator('.city-contents-photo-index [data-more]');
        await more.click();
        if (!(await shown())) out.push('opening the disclosure does not paint the rest of the rows');
        if ((await more.getAttribute('aria-expanded')) !== 'true') out.push('the disclosure does not report aria-expanded="true"');
        await more.click();
      } else if (!(await shown())) out.push(`rows after the fifth are hidden at ${viewport}px`);
      return out;
    },
  },
  'city-dial-photo-marker': {
    present: '[data-city-dial-photo-marker]',
    run: async (page, viewport) => {
      const out: string[] = [];
      const shown = await page.locator('[data-city-dial-photo-marker]').isVisible();
      if (viewport >= 1024 && !shown) out.push('the dial is not painted at a desktop width');
      if (viewport < 1024 && shown) out.push('the dial is painted below 1024px, where the jump band navigates');
      const current = await page.locator('[data-city-dial-photo-marker] [aria-current="location"]').count();
      if (current !== 1) out.push(`${current} dial rows are marked current; exactly one must be`);
      return out;
    },
  },
  'city-jump-stepper': {
    present: '[data-city-jump-stepper]',
    run: async (page, viewport) => {
      const out: string[] = [];
      const band = page.locator('[data-city-jump-stepper]');
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
      // The dialog's `close` event, which resets the key, is dispatched as a task after Escape:
      // read the key once it has run (up to 1s), not in the same tick — the probe raced it on
      // the chrome band (/kit-preview/city-page/) about one run in three.
      await page.waitForFunction(() => document.querySelector('[data-city-jump-stepper] [data-jump-open]')
        ?.getAttribute('aria-expanded') === 'false', null, { timeout: 1000 }).catch(() => {});
      const closed = await band.locator('[data-jump-sheet]').evaluate((d) => !(d as HTMLDialogElement).open);
      if (!closed) out.push('Escape does not close the sheet');
      if ((await opener.getAttribute('aria-expanded')) !== 'false') out.push('after Escape the key still reports aria-expanded="true"');
      return out;
    },
  },
  'city-takeaways-ledger': {
    present: '.city-takeaways-ledger',
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
  'city-faq-ledger': {
    present: '.city-faq',
    run: async (page) => {
      const out = await allVisible(page, 'data-faq-block');
      const q = page.locator('.city-faq [data-faq-q]').first();
      const before = await q.evaluate((h) => (h.closest('details') as HTMLDetailsElement).open);
      await q.click();
      const after = await q.evaluate((h) => (h.closest('details') as HTMLDetailsElement).open);
      if (after === before) out.push('pressing the first question does not toggle its answer');
      // The numbering runs on across the blocks: 01, 02, … with no gap and no repeat.
      const nums = await page.evaluate(() => Array.from(document.querySelectorAll('.city-faq .n')).map((n) => Number(n.textContent)));
      if (nums.some((n, i) => n !== i + 1)) out.push(`the ledger numbers run ${nums.join(',')}, not 1..${nums.length}`);
      return out;
    },
  },
  'city-newsletter-notice': {
    present: '[data-newsletter]',
    run: async (page) => {
      const out: string[] = [];
      const email = page.locator('[data-newsletter] input[type="email"]');
      const h = (await email.boundingBox())?.height ?? 0;
      if (h < 44) out.push(`the email field is ${h}px tall`);
      await page.locator('[data-newsletter] button[type="submit"]').click();
      if ((await email.getAttribute('aria-invalid')) !== 'true') out.push('an empty submit does not mark the field aria-invalid');
      const desc = await email.getAttribute('aria-describedby');
      if (!desc || !(await page.locator(`#${desc}`).isVisible())) out.push('the invalid field is not described by a painted error line');
      return out;
    },
  },
  'city-contact-lineup': {
    present: '.city-contact',
    run: async (page) => {
      const out: string[] = [];
      const short = await page.evaluate(() => Array.from(document.querySelectorAll(
        '[data-contact-form] input:not([type="hidden"]):not([name="_gotcha"]), [data-contact-form] select, [data-contact-form] textarea, [data-contact-form] button'))
        .filter((el) => el.getBoundingClientRect().height < 44).map((el) => el.getAttribute('name') || el.tagName));
      if (short.length) out.push(`under 44px tall: ${short.join(', ')}`);
      // The line-up is a picture: nothing in it takes a tap.
      const tappable = await page.locator('.city-contact .pups a, .city-contact .pups button').count();
      if (tappable) out.push(`${tappable} control(s) inside the line-up, which selects nothing`);
      await page.locator('[data-contact-form] [type="submit"]').click();
      const name = page.locator('[data-contact-form] [name="name"]');
      if ((await name.getAttribute('aria-invalid')) !== 'true') out.push('an empty submit does not mark the name aria-invalid');
      const desc = await name.getAttribute('aria-describedby');
      if (!desc || !(await page.locator(`#${desc}`).isVisible())) out.push('the invalid name is not described by a painted error line');
      return out;
    },
  },
  // The Task 7b review, item 1: the in-body components are containers, and on a city page the
  // body is the column beside the dial (656px at 1024, 832px at 1280), so a tier set for the
  // canvas's full-width 1024 was never reached there. Each component's tier now follows ITS OWN
  // BOX — phone below 640px, tablet from 640, desktop from 800 — on the full-width preview and in
  // the column alike, and this probe reads the tier from the box and asserts the layout facts of
  // that tier (two parts side by side, prints to a row, the square print). Heading SIZE is
  // city-type-fit's.
  'city-layout-follows-box': {
    present: '.city-kit',
    run: async (page) => page.evaluate(() => {
      type Fact = ['beside', string, string] | ['row', string, number] | ['square', string] | ['fill', string, string];
      const SPEC: Record<string, { tablet: Fact[]; desktop: Fact[] }> = {
        '.city-takeaways-ledger': { tablet: [['beside', '.row dt', '.row dd']], desktop: [['beside', '.pic', 'dl']] },
        '.city-sheet': { tablet: [['row', '.city-pup', 3]], desktop: [['row', '.city-pup', 3], ['square', '.city-pup img']] },
        '.city-roster': { tablet: [], desktop: [] },
        '.city-video': { tablet: [['beside', '.side > img', '.facts']], desktop: [['beside', '.grid > .kit-video', '.side']] },
        '.city-chapters': { tablet: [['beside', '.ch .media', '.ch p']], desktop: [['beside', '.ch h3', '.ch .media'], ['beside', '.ch .media', '.ch p']] },
        '.city-letter': { tablet: [], desktop: [['beside', '.pic', 'blockquote']] },
        '.city-faq.has-rail': { tablet: [], desktop: [['beside', '.rail', '.blk']] },
        '.city-newsletter-notice': { tablet: [['beside', 'figure', '.body']], desktop: [['beside', 'figure', '.body']] },
        '.city-contact': { tablet: [['row', '.pups li', 6], ['row', '.field', 2], ['fill', '.field.wide', 'form']], desktop: [['row', '.pups li', 6], ['row', '.field', 3], ['fill', '.field.wide', 'form']] },
      };
      const out: string[] = [];
      for (const [sel, tiers] of Object.entries(SPEC)) {
        for (const root of Array.from(document.querySelectorAll<HTMLElement>(sel))) {
          const w = root.getBoundingClientRect().width;
          const tier = w >= 800 ? 'desktop' : w >= 640 ? 'tablet' : null;
          if (!tier) continue;
          const at = `${sel} (${Math.round(w)}px box, ${tier})`;
          for (const f of tiers[tier]) {
            if (f[0] === 'beside') {
              const a = root.querySelector(f[1]); const b = root.querySelector(f[2]);
              if (!a || !b) { out.push(`${at}: ${f[1]} or ${f[2]} missing`); continue; }
              const ra = a.getBoundingClientRect(); const rb = b.getBoundingClientRect();
              if (!(ra.right <= rb.left + 1 && ra.top < rb.bottom && rb.top < ra.bottom)) {
                out.push(`${at}: ${f[1]} is not beside ${f[2]}`);
              }
            } else if (f[0] === 'row') {
              const els = Array.from(root.querySelectorAll(f[1])).filter((e) => e.getBoundingClientRect().height > 0);
              const top = els.length ? els[0].getBoundingClientRect().top : 0;
              const n = els.filter((e) => Math.abs(e.getBoundingClientRect().top - top) < 2).length;
              if (n !== f[2]) out.push(`${at}: ${n} ${f[1]} to the first row, not ${f[2]}`);
            } else if (f[0] === 'fill') {
              // A full-width row really runs the width of its box (the 65ch paragraph measure once
              // caught the message field, a <p>, at 549px: the Task 7b design pass).
              const el = root.querySelector(f[1]); const box = root.querySelector(f[2]);
              if (el && box && el.getBoundingClientRect().width < box.clientWidth - 2) {
                out.push(`${at}: ${f[1]} is ${Math.round(el.getBoundingClientRect().width)}px of its ${box.clientWidth}px ${f[2]}`);
              }
            } else {
              const r = root.querySelector(f[1])!.getBoundingClientRect();
              if (Math.abs(r.width - r.height) > 2) out.push(`${at}: ${f[1]} is ${Math.round(r.width)}×${Math.round(r.height)}, not square`);
            }
          }
        }
      }
      return out;
    }),
  },
  // Task 7b item 10 (the user's type-fit ruling): heading caps and lines, paragraph measure
  // and length, section height, per tier (tests/render/lib/cityTypeFit.ts).
  'city-type-fit': {
    present: '.city-kit',
    run: async (page, viewport) => {
      const r = await page.evaluate(cityTypeFit, viewport);
      console.log(`city-type-fit @ ${viewport}px: examined ${r.examined}`);
      return r.examined ? r.defects : ['city-type-fit examined nothing'];
    },
  },
  // Learning loop 2026-09-27, L8: the current-section marker, under BOTH motion preferences.
  // Scroll the fourth section to the reading band and read which row is current, on the dial at
  // a desktop width and on the band's rail below it.
  'city-nav-current-section': {
    present: '[data-city-dial-photo-marker], [data-city-jump-stepper]',
    run: async (page, viewport) => {
      const out: string[] = [];
      const scope = viewport >= 1024 ? '[data-city-dial-photo-marker]' : '[data-city-jump-stepper] .rail';
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

// The type-fit check against its own fixtures (the meta gate's discipline, for a check that lives
// in this suite): it must fire on the page built to break it and stay silent on the clean one.
for (const kind of ['broken', 'good'] as const) {
  test(`city-type-fit on its known_${kind} fixture`, async ({ page }, testInfo) => {
    const viewport = testInfo.project.use.viewport!.width;
    await page.setContent(readFileSync(new URL(`./fixtures/city/type-fit-${kind}.html`, import.meta.url), 'utf8'));
    const r = await page.evaluate(cityTypeFit, viewport);
    expect(r.examined, 'the fixture must be examined').toBeGreaterThan(0);
    if (kind === 'broken') {
      // Each kind of defect fires on its own element, not merely "something fired".
      const kinds: [string, RegExp][] = [
        ['heading cap', /is [\d.]+px, over the \w+ cap/],
        ['heading lines', /wraps to \d+ lines/],
        ['75ch measure', /ch wide \(75 max\)/],
        ['paragraph lines', /runs \d+ lines \(\d max/],
      ];
      // Section height is judged at a phone width and from 1280 only (the ruling's two caps).
      if (viewport < 768 || viewport >= 1280) kinds.push(['section height', /the section is \d+px tall/]);
      for (const [what, re] of kinds) {
        expect(r.defects.some((d) => re.test(d)), `city-type-fit did not report the ${what} defect: ${r.defects.join(' | ')}`).toBe(true);
      }
    }
    else expect(r.defects, 'city-type-fit cried wolf on its known_good fixture').toEqual([]);
  });
}
