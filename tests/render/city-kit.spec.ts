import { test, expect, type Page } from '@playwright/test';
import { registry } from './lib/registry.js';
import { runCheck } from './lib/runCheck.js';
import './checks/layout.js';
import './checks/a11y.js';
import './checks/img.js';
import './checks/nav.js';
import { readFileSync } from 'node:fs';
import { cityTypeFit } from './lib/cityTypeFit.js';
import { cityLayoutFollowsBox } from './lib/cityLayoutFollowsBox.js';
import { TIER } from './lib/cityTiers.js';

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
        // Two animation frames: the sticky band's position is laid out on the frame after the
        // scroll, and that is the condition, not a clock.
        await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(null)))));
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
  // The Task 7b review, item 1 (I3 in the quality review): tests/render/lib/cityLayoutFollowsBox.ts.
  'city-layout-follows-box': {
    present: '.city-kit',
    run: async (page, viewport) => {
      const r = await page.evaluate(cityLayoutFollowsBox, { viewport, tier: TIER });
      console.log(`city-layout-follows-box @ ${viewport}px: examined ${r.examined}`);
      return r.defects;
    },
  },
  // Task 7b item 10 (the user's type-fit ruling): heading caps and lines, paragraph measure
  // and length, section height, per tier (tests/render/lib/cityTypeFit.ts).
  'city-type-fit': {
    present: '.city-kit',
    run: async (page, viewport) => {
      const fullWidthSpecimen = new URL(page.url()).pathname === '/kit-preview/city/';
      const r = await page.evaluate(cityTypeFit, { viewport, tier: TIER, fullWidthSpecimen });
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
        // Wait on the SPY, not on a clock: an IntersectionObserver reports on a rendering
        // opportunity after the scroll, and with four workers painting at once that took up to
        // ~230ms here (measured: the dial still named the previous section 0–2 frames after
        // the scroll, then settled), so a fixed 300ms read raced it about one run in three.
        // The component is right when the named section becomes current; if it never does
        // within 3s the read below reports what it shows instead.
        await page.waitForFunction(({ s, w }) => {
          const cur = Array.from(document.querySelectorAll(`${s} [aria-current="location"]`));
          return cur.length === 1 && (cur[0] as HTMLAnchorElement).dataset.spy === w;
        }, { s: scope, w: want }, { timeout: 3000, polling: 'raf' }).catch(() => {});
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
    const r = await page.evaluate(cityTypeFit, { viewport, tier: TIER });
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

// The type check reads the tier from the section's own box at cityKit's edges (I4, M9): a 27px H2
// in a 650px and in a 790px box is over the TABLET cap, at every viewport.
test('city-type-fit reads the tier from the section box, at the TIER edges', async ({ page }, testInfo) => {
  const viewport = testInfo.project.use.viewport!.width;
  await page.setContent(readFileSync(new URL('./fixtures/city/type-fit-tier-broken.html', import.meta.url), 'utf8'));
  const r = await page.evaluate(cityTypeFit, { viewport, tier: TIER });
  for (const box of ['city-narrow', 'city-edge']) {
    expect(r.defects.some((d) => d.startsWith(box) && /over the tablet cap of 25px/.test(d)),
      `${box}: a 27px H2 was not judged against the tablet cap: ${r.defects.join(' | ')}`).toBe(true);
  }
});

// city-layout-follows-box cannot pass having examined nothing (I3).
test('city-layout-follows-box fails a page it cannot examine', async ({ page }, testInfo) => {
  const viewport = testInfo.project.use.viewport!.width;
  await page.setContent('<main><p>No city section here.</p></main>');
  const r = await page.evaluate(cityLayoutFollowsBox, { viewport, tier: TIER });
  expect(r.defects.some((d) => /matches no section on the page/.test(d)), 'a SPEC key with no root must be reported').toBe(true);
  if (viewport >= 768) expect(r.defects.some((d) => /examined no layout fact/.test(d)), 'zero facts at 768+ must fail').toBe(true);
  // A desktop sheet whose print has no photo: the square fact reports the missing node, never throws.
  await page.setContent('<section class="city-sheet" style="width:900px"><div class="city-pup">a</div><div class="city-pup">b</div><div class="city-pup">c</div></section>');
  const r2 = await page.evaluate(cityLayoutFollowsBox, { viewport, tier: TIER });
  expect(r2.defects.some((d) => /\.city-sheet .*\.city-pup img missing/.test(d)), r2.defects.join(' | ')).toBe(true);
});

// The type and layout checks at the widths between the four (I4): 660 (just past the phone/tablet
// edge; the 656px column at 1024 sits just past it too) and 1160 (the column just under the desktop
// edge, a full-width box well past it). Run once, in the 1280 project, on both routes.
for (const route of ROUTES) {
  test(`city type and layout at the tier edges on ${route}`, async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'vp1280', 'run once, at the edge widths it sets itself');
    for (const width of [660, 1160]) {
      await page.setViewportSize({ width, height: 900 });
      const res = await page.goto(route);
      expect(res?.status()).toBe(200);
      await page.evaluate(() => document.fonts.ready);
      const fullWidthSpecimen = route === '/kit-preview/city/';
      const t = await page.evaluate(cityTypeFit, { viewport: width, tier: TIER, fullWidthSpecimen });
      const l = await page.evaluate(cityLayoutFollowsBox, { viewport: width, tier: TIER });
      console.log(`${route} @ ${width}px: city-type-fit examined ${t.examined}, city-layout-follows-box examined ${l.examined}`);
      expect(t.examined).toBeGreaterThan(0);
      expect([...t.defects, ...l.defects], `${route} at ${width}px`).toEqual([]);
    }
  });
}
