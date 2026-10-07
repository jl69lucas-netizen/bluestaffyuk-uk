import { test, expect, type Page } from '@playwright/test';
import { registry } from './lib/registry.js';
import { runCheck } from './lib/runCheck.js';
import './checks/layout.js';
import './checks/a11y.js';
import './checks/img.js';
import './checks/nav.js';
import { readFileSync } from 'node:fs';
import { cityTypeFit } from './lib/cityTypeFit.js';
import { cityLayoutFollowsBox, absentFromBoard, SPEC_COMPONENT } from './lib/cityLayoutFollowsBox.js';
import { cityChapterImageFirst } from './lib/cityChapterImageFirst.js';
import { TIER, HEADING_CAPS } from './lib/cityTiers.js';

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
// Manchester's own components (the Manchester page run, Phase F Tasks 28-31; gap G11) are
// previewed on their own route, never on London's /kit-preview/city/: the nav set is a page
// singleton, and each city's picks are components of their own (rules/design.md
// own-components-per-page).
const MANCHESTER_KIT = '/kit-preview/city-manchester/';
// Manchester's own route, a noindex scaffold until its page run writes it (Phase F Task 32; gap
// G11's "the Manchester route"): the picks on CityShell in the approved outline's order.
const MANCHESTER_PAGE = '/uk-locations/blue-staffy-puppies-manchester-uk/';
const ROUTES = ['/kit-preview/city/', '/kit-preview/city-page/', '/uk-locations/blue-staffy-puppies-london/', MANCHESTER_KIT, MANCHESTER_PAGE];
// The full-width specimen routes: every component paints the viewport wide, as the canvas frames did.
const FULL_WIDTH_SPECIMENS = new Set(['/kit-preview/city/', MANCHESTER_KIT]);
// city-layout-follows-box judges the IN-BODY city components (its SPEC keys). Each city's are its
// own (rules/design.md own-components-per-page), so a route is judged on its OWN city's keys: the
// other city's are declared absent for that reason, and one that the route does carry is a
// defect (a stale declaration). Manchester's preview carried no in-body component until Task 30
// (the takeaways, the table, the image and text) and was skipped; it is judged like London's now.
const ROUTE_CITY: Record<string, string> = { [MANCHESTER_KIT]: 'manchester', [MANCHESTER_PAGE]: 'manchester' };
const routeCity = (route: string) => ROUTE_CITY[route] ?? 'london';
const COMPONENT_ROWS: { id: string; canvas_variant?: string }[] =
  JSON.parse(readFileSync(new URL('../../data/design/components.json', import.meta.url), 'utf8'));
/** The city a kit component was built for (its row's `canvas_variant`; London's rows predate it). */
const cityOfComponent = (id: string) => COMPONENT_ROWS.find((r) => r.id === id)?.canvas_variant?.split('/')[0] ?? 'london';
const cityKeys = (city: string) => Object.keys(SPEC_COMPONENT).filter((k) => cityOfComponent(SPEC_COMPONENT[k]) === city);
// A real city page's approved board says which city components it mounts; a SPEC key of
// city-layout-follows-box whose component the board does not mount is declared absent, never
// demanded (tests/render/lib/cityLayoutFollowsBox.ts `absent`, 2026-10-04). The specimen routes
// carry every one of their city's components and declare none of them.
const LONDON = '/uk-locations/blue-staffy-puppies-london/';
const BOARDS: Record<string, { meta: { slug: string }; sections: { component?: string }[] }> = {
  [LONDON]: JSON.parse(readFileSync(new URL('../../data/boards/blue-staffy-puppies-london.json', import.meta.url), 'utf8')),
};
const absentFor = (route: string) => absentFromBoard(BOARDS[route] ?? null, cityKeys(routeCity(route)));
/** Everything a route declares absent: the other cities' keys, then its board's own. */
const absentOn = (route: string): Record<string, string> => ({
  ...Object.fromEntries(Object.entries(SPEC_COMPONENT).filter(([, c]) => cityOfComponent(c) !== routeCity(route))
    .map(([k, c]) => [k, `${c} is ${cityOfComponent(c)}'s own component and ${route} is ${routeCity(route)}'s`])),
  ...absentFor(route),
});
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

/** Scroll to `y` and return once the page has painted a frame at it (lessons entry 20,
 *  2026-10-06). A page's scroll handlers read the position once per frame (the jump band's tuck
 *  compares it with the last frame's), so two scrolls that land in the same frame are one scroll
 *  to the page: on four workers the reset to the top before a probe and the jump band probe's
 *  first scroll down (0, then 900) were read as 1200 -> 900, a scroll UP, and the band stayed
 *  on screen. Two animation frames: the first runs after the scroll event and the handler's own
 *  frame callback are queued, the second after they have run. A condition, never a clock. */
const scrollSettled = (page: Page, y: number) => page.evaluate((v) => new Promise((r) => {
  window.scrollTo(0, v);
  requestAnimationFrame(() => requestAnimationFrame(() => r(null)));
}), y);

/** Every element carrying `attr` is painted (a box of at least 1×1 and not visibility:hidden). */
async function allVisible(page: Page, attr: string): Promise<string[]> {
  const hidden = await page.evaluate((a) => Array.from(document.querySelectorAll(`[${a}]`))
    .filter((el) => {
      const b = el.getBoundingClientRect();
      return b.width < 1 || b.height < 1 || getComputedStyle(el).visibility === 'hidden';
    }).length, attr);
  return hidden ? [`${hidden} [${attr}] element(s) are not painted`] : [];
}

/** The email error line says one thing for an empty field and another for a malformed address
 *  (M8, as behaviour): submit empty, then type "a", then clear it, and read which line paints. */
async function emailMessages(page: Page, form: string, email: string): Promise<string[]> {
  const out: string[] = [];
  const shown = async (sel: string) => page.locator(`${form} ${sel}`).first().isVisible();
  const expectLine = async (state: string, want: 'e-empty' | 'e-bad') => {
    const other = want === 'e-empty' ? 'e-bad' : 'e-empty';
    if (!(await shown(`.${want}`)) || (await shown(`.${other}`))) out.push(`${form}: a ${state} email does not paint its own line (.${want})`);
  };
  await page.locator(`${form} [type="submit"]`).click();
  await expectLine('empty', 'e-empty');
  await page.fill(email, 'a');
  await page.locator(`${form} [type="submit"]`).click();
  await expectLine('malformed', 'e-bad');
  await page.fill(email, '');
  await page.locator(`${form} [type="submit"]`).click();
  await expectLine('cleared', 'e-empty');
  return out;
}

/** The price scale's figures stay on the panel and on the number line (the Task 8 quality
 *  review, I1): every figure's PAINTED text (a Range over its glyphs, so a no-wrap figure that
 *  overflows its own box is caught) ends inside the panel's content edge and, where the stops are
 *  laid on a horizontal line (from 640px), inside the line's right end. Returns the defects. */
async function priceScaleSpill(page: Page): Promise<string[]> {
  return page.evaluate(() => {
    const out: string[] = [];
    const root = document.querySelector('.city-scale');
    // Nothing to measure is a defect, never a pass (Task 8b, M-new-2).
    if (!root) return ['the page has no price scale (.city-scale) to measure'];
    const panel = root.querySelector('.panel')!;
    const ps = getComputedStyle(panel);
    const pr = panel.getBoundingClientRect();
    const panelRight = pr.right - parseFloat(ps.paddingRight);
    const panelLeft = pr.left + parseFloat(ps.paddingLeft);
    const ol = root.querySelector('ol')!;
    const horizontal = getComputedStyle(ol).display === 'flex';
    const lineRight = ol.getBoundingClientRect().right;
    const figs = Array.from(root.querySelectorAll('[data-figure]'))
      .flatMap((f) => (f.classList.contains('n') ? [f] : Array.from(f.querySelectorAll('.n'))));
    if (!figs.length) return ['the price scale has no figure to measure'];
    for (const f of figs) {
      const r = document.createRange(); r.selectNodeContents(f);
      const b = r.getBoundingClientRect();
      const name = (f.textContent || '').replace(/\s+/g, ' ').trim();
      if (b.right > panelRight + 1 || b.left < panelLeft - 1) out.push(`"${name}" paints ${Math.round(Math.max(b.right - panelRight, panelLeft - b.left))}px outside the panel`);
      else if (horizontal && b.right > lineRight + 1) out.push(`"${name}" runs ${Math.round(b.right - lineRight)}px past the number line`);
    }
    return out;
  });
}

/** The range sheet's figures stay on the sheet (Manchester's counter, CityRangeSheet): every
 *  figure's PAINTED glyphs (a Range over its text, so a no-wrap figure that overflows its own cell
 *  is caught, as priceScaleSpill reads London's) end inside the sheet's content box, a face paints,
 *  and the delivery band paints its bar. Nothing to measure is a defect, never a pass. */
async function rangeSheetSpill(page: Page): Promise<string[]> {
  return page.evaluate(() => {
    const bad: string[] = [];
    const sheet = document.querySelector('.city-range-sheet .sheet');
    if (!sheet) return ['the page has no range sheet (.city-range-sheet) to measure'];
    const s = getComputedStyle(sheet);
    const b = sheet.getBoundingClientRect();
    const left = b.left + parseFloat(s.paddingLeft); const right = b.right - parseFloat(s.paddingRight);
    const figs = Array.from(sheet.querySelectorAll('.fig'));
    if (!figs.length) return ['the range sheet has no figure to measure'];
    for (const f of figs) {
      const r = document.createRange(); r.selectNodeContents(f);
      const g = r.getBoundingClientRect();
      if (g.left < left - 1 || g.right > right + 1) bad.push(`"${(f.textContent || '').trim()}" paints outside the sheet`);
    }
    const faces = Array.from(sheet.querySelectorAll<HTMLImageElement>('.faces img')).filter((i) => i.getBoundingClientRect().width > 0);
    if (!faces.length) bad.push('the range sheet paints no face');
    const track = sheet.querySelector('.track')?.getBoundingClientRect();
    if (!track || track.width < 40) bad.push('the delivery band paints no range bar');
    return bad;
  });
}

/** The current-section marker follows the reader (learning loop 2026-09-27, L8), under BOTH motion
 *  preferences: scroll the fourth tall-enough section named in `scope` to the reading band and
 *  read which `[data-spy]` row in `scope` is current. Every city's nav set is held to it: London's
 *  dial and band rail, Manchester's numeral rail and question bar. Returns the defects. */
async function navCurrentSection(page: Page, scope: string): Promise<string[]> {
  const out: string[] = [];
  // A sheet an earlier probe left open would make the page inert: this probe judges the
  // spy, not the sheet, so it starts from a shut sheet (Task 8b, M-new-1).
  await page.evaluate(() => document.querySelectorAll<HTMLDialogElement>('dialog[open]').forEach((d) => d.close()));
  if (!(await page.locator(scope).first().isVisible())) return out;
  for (const motion of ['reduce', 'no-preference'] as const) {
    await page.emulateMedia({ reducedMotion: motion });
    const want = await page.evaluate((s) => {
      // Only a section tall enough to fill the reading band can be asked to be current: on the
      // specimen route the contents list's wrapper is a one-line caption from 1024px, where
      // the list itself is hidden (answer board q05), so the band reads the section after it.
      const links = Array.from(document.querySelectorAll<HTMLAnchorElement>(`${s} [data-spy]`))
        .filter((a) => document.getElementById(a.dataset.spy!)!.getBoundingClientRect().height >= window.innerHeight * 0.2);
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
    // within 10s (a ceiling; Task 8b) the read below reports what it shows instead.
    await page.waitForFunction(({ s, w }) => {
      const cur = Array.from(document.querySelectorAll(`${s} [aria-current="location"]`));
      return cur.length === 1 && (cur[0] as HTMLAnchorElement).dataset.spy === w;
    }, { s: scope, w: want }, { timeout: 10_000, polling: 'raf' }).catch(() => {});
    const got = await page.evaluate((s) => Array.from(document.querySelectorAll(`${s} [aria-current="location"]`))
      .map((a) => (a as HTMLAnchorElement).dataset.spy), scope);
    if (got.length !== 1 || got[0] !== want) {
      out.push(`reducedMotion=${motion}: section ${want} in the reading band, current is [${got.join(', ')}]`);
    }
  }
  await page.emulateMedia({ reducedMotion: null });
  return out;
}

/** A jump sheet that is a native `<dialog>` opened by a key (`[data-jump-open]`): the key opens
 *  it and reports aria-expanded, Escape shuts it and the key follows. Every read waits on the
 *  state it judges (Task 8b, M-new-1), and the page is always left with the sheet shut. */
async function jumpSheetOpensAndShuts(page: Page, root: string): Promise<string[]> {
  const out: string[] = [];
  const opener = page.locator(`${root} [data-jump-open]`);
  const box = await opener.boundingBox();
  if (!box || box.height < 44) out.push('the sheet key is under 44px tall');
  const sheetState = (want: { open: boolean; expanded: string }) => page.waitForFunction(({ r, w }) => {
    const d = document.querySelector<HTMLDialogElement>(`${r} [data-jump-sheet]`);
    const k = document.querySelector(`${r} [data-jump-open]`);
    return !!d && !!k && d.open === w.open && k.getAttribute('aria-expanded') === w.expanded;
  }, { r: root, w: want }, { timeout: 10_000, polling: 'raf' }).then(() => true, () => false);
  await opener.click();
  if (!(await sheetState({ open: true, expanded: 'true' }))) out.push('pressing the key does not open the sheet and report aria-expanded="true"');
  await page.keyboard.press('Escape');
  if (!(await sheetState({ open: false, expanded: 'false' }))) out.push('Escape does not shut the sheet and reset the key');
  await page.locator(`${root} [data-jump-sheet]`).evaluate((d) => (d as HTMLDialogElement).close());
  return out;
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
    run: async (page) => [...(await allVisible(page, 'data-figure')), ...(await priceScaleSpill(page))],
  },
  'city-trust-ledger': {
    present: '.city-trust',
    run: (page) => allVisible(page, 'data-trust-item'),
  },
  // ── Manchester's picks (Phase F Task 28): hero C, counter B, trust B ──────────────────────
  'city-feature-and-three': {
    present: '.city-feature-and-three',
    run: async (page, viewport) => {
      const out: string[] = [];
      const r = await page.evaluate(() => {
        const root = document.querySelector('.city-feature-and-three')!;
        const ticks = Array.from(root.querySelectorAll<HTMLElement>('[data-tick]'))
          .filter((t) => t.getBoundingClientRect().height > 0);
        return {
          band: Math.round(root.getBoundingClientRect().height),
          pics: root.querySelectorAll('.pic img').length,
          ticks: ticks.length,
          tops: ticks.map((t) => Math.round(t.getBoundingClientRect().top)),
          lefts: ticks.map((t) => Math.round(t.getBoundingClientRect().left)),
        };
      });
      // rules/design.md rule 10: 390px floor from 1024, 450px ceiling from 1024 (the pick's band).
      if (viewport >= 1024 && (r.band < 390 || r.band > 450)) out.push(`hero band is ${r.band}px at ${viewport}px; it must be 390-450`);
      if (r.pics !== 4) out.push(`the hero paints ${r.pics} puppies, not the feature and three`);
      if (r.ticks !== 4) out.push(`${r.ticks} ticks are painted, not four`);
      // The user's canvas note: one line on desktop; two left and two right below it.
      const rowsOf = (xs: number[]) => new Set(xs.map((x) => Math.round(x / 4))).size;
      if (viewport >= 1024 && rowsOf(r.tops) !== 1) out.push(`the four ticks take ${rowsOf(r.tops)} lines at ${viewport}px, not one`);
      if (viewport < 1024 && (rowsOf(r.tops) !== 2 || rowsOf(r.lefts) !== 2)) out.push(`the ticks are not a 2x2 at ${viewport}px`);
      return out;
    },
  },
  'city-range-sheet': {
    present: '.city-range-sheet',
    run: async (page) => {
      const out = await allVisible(page, 'data-figure');
      out.push(...await rangeSheetSpill(page));
      return out;
    },
  },
  'city-puppy-folder': {
    present: '.city-puppy-folder',
    run: async (page, viewport) => {
      const out = await allVisible(page, 'data-trust-item');
      out.push(...await page.evaluate((vp) => {
        const bad: string[] = [];
        const root = document.querySelector('.city-puppy-folder')!;
        const box = (sel: string) => root.querySelector(sel)!.getBoundingClientRect();
        const intro = box('.intro'); const folder = box('.folder'); const steps = box('.steps'); const tab = box('.tab');
        // The tab sits on the folder's top edge, inside the panel, never clipped by it.
        if (Math.abs(tab.bottom - folder.top) > 1) bad.push('the folder tab does not sit on the folder');
        if (tab.top < box('.panel').top) bad.push('the folder tab runs out of the panel');
        if (vp >= 1024) {
          if (!(intro.right <= folder.left + 1 && folder.right <= steps.left + 1)) bad.push(`the intro, folder and steps are not side by side at ${vp}px`);
        } else if (!(intro.bottom <= tab.top + 1 && folder.bottom <= steps.top + 1)) bad.push(`the intro, folder and steps do not stack at ${vp}px`);
        return bad;
      }, viewport));
      return out;
    },
  },
  // ── Manchester's nav set (Phase F Task 29): contents B, dial A, jump links B ────────────────
  'city-icon-rows': {
    present: '.city-icon-rows',
    run: async (page, viewport) => {
      const root = page.locator('.city-icon-rows');
      const painted = await root.isVisible();
      // From 1024px the dial is the contents (answer board q05, 2026-09-29, "as the other pages do").
      if (viewport >= 1024) return painted ? [`the contents card is painted at ${viewport}px, where the dial navigates`] : [];
      if (!painted) return [`the contents card is not painted at ${viewport}px`];
      const out = await allVisible(page, 'data-contents');
      const photo = await page.evaluate(() => {
        const i = document.querySelector<HTMLImageElement>('.city-icon-rows img')!;
        const b = i.getBoundingClientRect();
        return { w: b.width, h: b.height, list: document.querySelector('.city-icon-rows nav')!.getBoundingClientRect().left - b.left };
      });
      if (photo.w < 100 || photo.h < 80) out.push(`the photo paints at ${Math.round(photo.w)}x${Math.round(photo.h)}`);
      // The pick's media axis: the photo is the card's right column from 640px.
      if (viewport >= 640 && photo.list >= 0) out.push('the photo is not the right-hand column from 640px');
      const rest = page.locator('.city-icon-rows [data-rest]');
      if (!(await rest.count())) return out;
      const shown = async () => rest.first().isVisible();
      if (viewport < 768) {
        if (await shown()) out.push('rows after the phone cut are painted before the disclosure is opened');
        const more = page.locator('.city-icon-rows [data-more]');
        await more.click();
        if (!(await shown())) out.push('opening the disclosure does not paint the rest of the rows');
        if ((await more.getAttribute('aria-expanded')) !== 'true') out.push('the disclosure does not report aria-expanded="true"');
        await more.click();
      } else if (!(await shown())) out.push(`rows after the phone cut are hidden at ${viewport}px`);
      return out;
    },
  },
  'city-numeral-rail': {
    present: '.city-numeral-rail',
    run: async (page, viewport) => {
      const out: string[] = [];
      const shown = await page.locator('.city-numeral-rail').isVisible();
      if (viewport >= 1024 && !shown) out.push('the dial is not painted at a desktop width');
      if (viewport < 1024 && shown) out.push('the dial is painted below 1024px, where the question bar navigates');
      const current = await page.locator('.city-numeral-rail [aria-current="location"]').count();
      if (current !== 1) out.push(`${current} dial rows are marked current; exactly one must be`);
      if (!shown) return out;
      // The current numeral sits in a brass square (the pick, after impeccable's side-stripe ban).
      const sq = await page.evaluate(() => {
        const n = document.querySelector('.city-numeral-rail [aria-current="location"] .n')!;
        const idle = document.querySelector('.city-numeral-rail a:not([aria-current]) .n')!;
        return [getComputedStyle(n).backgroundColor, getComputedStyle(idle).backgroundColor];
      });
      if (sq[0] === sq[1]) out.push('the current numeral is painted like an idle one');
      out.push(...await navCurrentSection(page, '.city-numeral-rail'));
      return out;
    },
  },
  'city-question-bar': {
    present: '.city-question-bar',
    run: async (page, viewport) => {
      const out: string[] = [];
      const bar = page.locator('.city-question-bar');
      const shown = await bar.isVisible();
      if (viewport >= 1024) return shown ? ['the question bar is painted at a desktop width, where the dial navigates'] : [];
      if (!shown) return ['the question bar is not painted below 1024px'];
      // One tick per section, one of them on, and it is the sheet's current row; the readout names it.
      const r = await page.evaluate(() => {
        const root = document.querySelector('.city-question-bar')!;
        const ticks = Array.from(root.querySelectorAll('.ticks i'));
        const rows = Array.from(root.querySelectorAll<HTMLAnchorElement>('[data-jump-sheet] [data-spy]'));
        const tickWidths = ticks.map((t) => t.getBoundingClientRect().width);
        return {
          ticks: ticks.length, rows: rows.length,
          on: ticks.findIndex((t) => t.hasAttribute('data-on')),
          cur: rows.findIndex((a) => a.getAttribute('aria-current') === 'location'),
          now: (root.querySelector('[data-now]')?.textContent ?? '').trim(),
          narrowest: Math.min(...tickWidths),
          bar: Math.round(root.getBoundingClientRect().height),
        };
      });
      if (r.ticks !== r.rows) out.push(`${r.ticks} ticks for ${r.rows} sections`);
      if (r.on < 0 || r.on !== r.cur) out.push(`the lit tick (${r.on}) is not the current section (${r.cur})`);
      if (!r.now.startsWith(`${r.cur + 1} of ${r.rows}:`)) out.push(`the readout "${r.now}" does not name section ${r.cur + 1} of ${r.rows}`);
      if (r.narrowest < 4) out.push(`a tick paints ${r.narrowest}px wide`);
      // Slim: the bar and its ticks under 72px, so the header and the bar cover far less of a
      // phone than London's 27% (answer board q03).
      if (r.bar > 72) out.push(`the bar is ${r.bar}px tall`);
      out.push(...await jumpSheetOpensAndShuts(page, '.city-question-bar'));
      // Harden (Task 29): opening focuses the question being read, and a tap on the sheet's own
      // padding (the dialog is its target, as a backdrop tap's is) leaves it open.
      await page.locator('.city-question-bar [data-jump-open]').click();
      const sheetOpen = () => page.evaluate(() => document.querySelector<HTMLDialogElement>('.city-question-bar [data-jump-sheet]')!.open);
      await page.waitForFunction(() => document.querySelector<HTMLDialogElement>('.city-question-bar [data-jump-sheet]')!.open,
        null, { timeout: 10_000, polling: 'raf' }).catch(() => {});
      const focusOk = await page.evaluate(() => document.activeElement?.getAttribute('aria-current') === 'location'
        && !!document.activeElement.closest('.city-question-bar [data-jump-sheet]'));
      if (!focusOk) out.push('opening the sheet does not focus the current question');
      const sheetBox = await page.locator('.city-question-bar [data-jump-sheet]').boundingBox();
      if (sheetBox) await page.mouse.click(sheetBox.x + 4, sheetBox.y + sheetBox.height - 4);
      if (!(await sheetOpen())) out.push('a tap on the sheet\'s own padding shuts it');
      await page.mouse.click(4, 4);
      if (await page.waitForFunction(() => !document.querySelector<HTMLDialogElement>('.city-question-bar [data-jump-sheet]')!.open,
        null, { timeout: 10_000, polling: 'raf' }).then(() => false, () => true)) out.push('a tap on the backdrop does not shut the sheet');
      await page.locator('.city-question-bar [data-jump-sheet]').evaluate((d) => (d as HTMLDialogElement).close());
      out.push(...await navCurrentSection(page, '.city-question-bar'));
      return out;
    },
  },
  // ── Manchester's in-body picks (Phase F Task 30): takeaways C, tables A, image and text C ────
  'city-tick-card': {
    present: '.city-tick-card',
    run: async (page) => {
      const out = await allVisible(page, 'data-takeaway');
      out.push(...await page.evaluate(() => {
        const bad: string[] = [];
        const root = document.querySelector('.city-tick-card')!;
        const ticks = Array.from(root.querySelectorAll('[data-takeaway]'));
        if (ticks.length !== 5) bad.push(`${ticks.length} ticks, not the outline's five`);
        // Two to a row from a 640px box, and an odd last tick takes the whole row rather than
        // sitting alone beside an empty cell (Task 24: the fifth tick spans both columns).
        const list = root.querySelector('ul')!.getBoundingClientRect();
        const last = ticks[ticks.length - 1].getBoundingClientRect();
        const two = new Set(ticks.slice(0, 2).map((t) => Math.round(t.getBoundingClientRect().top))).size === 1;
        if (two && ticks.length % 2 === 1 && last.width < list.width - 2) bad.push(`the odd last tick is ${Math.round(last.width)}px of a ${Math.round(list.width)}px list`);
        const img = root.querySelector('img')!.getBoundingClientRect();
        const card = root.querySelector('.card')!.getBoundingClientRect();
        if (Math.abs(img.width - card.width) > 2) bad.push('the photo does not run the card wide');
        return bad;
      }));
      return out;
    },
  },
  'city-photo-shelf': {
    present: '.city-photo-shelf',
    run: async (page) => {
      const out = await allVisible(page, 'data-pup');
      out.push(...await page.evaluate(() => {
        const bad: string[] = [];
        const root = document.querySelector<HTMLElement>('.city-photo-shelf')!;
        const s = getComputedStyle(root);
        const box = root.clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
        const rows = Array.from(root.querySelectorAll('tbody tr'));
        if (rows.length < 1) return ['the shelf has no row to measure'];
        for (const tr of rows) {
          const img = tr.querySelector('img');
          const r = img?.getBoundingClientRect();
          if (!img || !r || r.width < 40 || r.height < 40) bad.push(`a row paints no photo of its puppy (${(tr.textContent || '').trim().slice(0, 12)})`);
          // The price's glyphs never run over the name's, stacked or not.
          const price = tr.querySelector('td[data-label="Price"]')!.getBoundingClientRect();
          const range = document.createRange(); range.selectNodeContents(tr.querySelector('.nm')!);
          const name = range.getBoundingClientRect();
          if (price.left < name.right - 1 && price.right > name.left + 1 && price.top < name.bottom - 1 && price.bottom > name.top + 1) bad.push('a price paints over its puppy\'s name');
        }
        const tops = rows.map((tr) => Math.round(tr.getBoundingClientRect().top));
        // Below a 640px box each row is a small portrait card, two to a line; from 640 a table row.
        const perLine = tops.filter((t) => Math.abs(t - tops[0]) < 2).length;
        if (box < 640 && perLine !== 2) bad.push(`${perLine} stacked cards to a line in a ${Math.round(box)}px box, not two`);
        if (box >= 640 && perLine !== 1) bad.push(`${perLine} rows share a line in a ${Math.round(box)}px box`);
        return bad;
      }));
      return out;
    },
  },
  'city-offset-sheet': {
    present: '.city-offset-sheet',
    run: async (page) => {
      const out = await allVisible(page, 'data-cell');
      out.push(...await page.evaluate(() => {
        const bad: string[] = [];
        const root = document.querySelector('.city-offset-sheet')!;
        const img = root.querySelector('.media img')!.getBoundingClientRect();
        const media = root.querySelector('.media')!;
        // The steel bleed is painted behind the photo and runs past it on the page's side.
        const bleed = getComputedStyle(media, '::before');
        if (bleed.content === 'none' || bleed.backgroundColor === 'rgba(0, 0, 0, 0)') bad.push('the photo has no steel bleed');
        if (img.width < 200) bad.push(`the photo paints ${Math.round(img.width)}px wide`);
        if (root.querySelectorAll('[data-cell]').length !== 4) bad.push('the sheet does not hold four cells');
        return bad;
      }));
      return out;
    },
  },
  // Manchester's last four (Phase F Task 31). The reviews: three plates, one review each, the
  // photo changing sides; the plate sits on its photo (overlapping it on a phone and a tablet,
  // beside it from a desktop box) and never covers a face (img-face-visible measures that).
  'city-three-plates': {
    present: '.city-three-plates',
    run: async (page) => {
      const out = await allVisible(page, 'data-review-slot');
      out.push(...await page.evaluate(() => {
        const bad: string[] = [];
        const roots = Array.from(document.querySelectorAll<HTMLElement>('.city-three-plates'));
        if (roots.length !== 3) bad.push(`${roots.length} plates on the page, not the outline's three review slots`);
        const sides: string[] = [];
        for (const root of roots) {
          const s = getComputedStyle(root);
          const box = root.clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
          const ph = root.querySelector('.ph')!.getBoundingClientRect();
          const plate = root.querySelector('.plate')!.getBoundingClientRect();
          if (ph.width < 1 || plate.width < 1) { bad.push('a slot paints no photo or no plate'); continue; }
          if (box >= 800) {
            // Beside: the photo's half and the plate's half on opposite sides, the plate over the photo's edge.
            sides.push(ph.left + ph.width / 2 < plate.left + plate.width / 2 ? 'start' : 'end');
            if (plate.top < ph.top - 1 || plate.bottom > ph.bottom + 1) bad.push('the desktop plate runs outside its photo band');
          } else if (!(plate.top < ph.bottom - 8 && plate.top > ph.top)) bad.push(`the plate does not rise over its photo's foot in a ${Math.round(box)}px box`);
          const cr = root.querySelector('.cr');
          if (cr) {
            const c = cr.getBoundingClientRect();
            if (c.left < ph.left - 1 || c.right > ph.right + 1 || c.top < ph.top - 1 || c.bottom > ph.bottom + 1) bad.push('a photo credit paints outside its photo');
          }
        }
        if (sides.length === 3 && sides.join() !== 'start,end,start') bad.push(`the photos sit ${sides.join(', ')}, not start, end, start`);
        return bad;
      }));
      return out;
    },
  },
  // The FAQ blocks: native details rows beside one photo per block, side swapping block by block.
  'city-rows-beside-a-photo': {
    present: '.city-rows-beside-a-photo',
    run: async (page) => {
      const out = await allVisible(page, 'data-faq-block');
      const q = page.locator('.city-rows-beside-a-photo [data-faq-q]').first();
      const before = await q.evaluate((h) => (h.closest('details') as HTMLDetailsElement).open);
      await q.click();
      const after = await q.evaluate((h) => (h.closest('details') as HTMLDetailsElement).open);
      if (after === before) out.push('pressing the first question does not toggle its answer');
      await q.evaluate((h) => { (h.closest('details') as HTMLDetailsElement).open = false; });
      out.push(...await page.evaluate(() => {
        const bad: string[] = [];
        const roots = Array.from(document.querySelectorAll('.city-rows-beside-a-photo'));
        if (roots.length !== 3) bad.push(`${roots.length} FAQ blocks, not three`);
        const n = roots.reduce((t, r) => t + r.querySelectorAll('[data-faq-q]').length, 0);
        if (n < 15 || n > 20) bad.push(`${n} questions across the blocks (15 to 20)`);
        for (const r of roots) {
          for (const s of Array.from(r.querySelectorAll('summary'))) {
            if (s.getBoundingClientRect().height < 44) bad.push('a question row is under 44px tall');
          }
          const img = r.querySelector('.pic img')!.getBoundingClientRect();
          if (img.width < 100) bad.push(`a block's photo paints ${Math.round(img.width)}px wide`);
        }
        return bad;
      }));
      return out;
    },
  },
  // The newsletter: a signed note with Vennie's round postmark; one email field, its error wired.
  'city-postmarked-note': {
    present: '.city-postmarked-note',
    run: async (page) => {
      const out: string[] = [];
      out.push(...await page.evaluate(() => {
        const bad: string[] = [];
        const root = document.querySelector('.city-postmarked-note')!;
        const pm = root.querySelector('.pm .disc')!.getBoundingClientRect();
        if (pm.width < 60 || Math.abs(pm.width - pm.height) > 2) bad.push(`the postmark paints ${Math.round(pm.width)}×${Math.round(pm.height)}, not a round stamp`);
        const ring = getComputedStyle(root.querySelector('.pm')!);
        if (ring.borderTopStyle !== 'dashed') bad.push('the postmark has no dashed ring');
        if (root.querySelector('h1, h2, h3, h4')) bad.push('the note carries a heading (outline row 16 carries none)');
        return bad;
      }));
      const email = page.locator('.city-postmarked-note input[type="email"]');
      const h = (await email.boundingBox())?.height ?? 0;
      if (h < 44) out.push(`the email field is ${h}px tall`);
      await page.locator('.city-postmarked-note button[type="submit"]').click();
      if ((await email.getAttribute('aria-invalid')) !== 'true') out.push('an empty submit does not mark the field aria-invalid');
      const desc = await email.getAttribute('aria-describedby');
      if (!desc || !(await page.locator(`#${desc}`).isVisible())) out.push('the invalid field is not described by a painted error line');
      out.push(...(await emailMessages(page, '.city-postmarked-note form', '.city-postmarked-note input[type="email"]')));
      return out;
    },
  },
  // The enquiry form: Lisa's photo at the edge, a collect-or-delivery switch, the kit form's contract.
  'city-photo-at-the-edge': {
    present: '.city-photo-at-the-edge',
    run: async (page) => {
      const out: string[] = [];
      const form = '.city-photo-at-the-edge form';
      const short = await page.evaluate((f) => Array.from(document.querySelectorAll(
        `${f} input:not([type="hidden"]):not([name="_gotcha"]):not([type="radio"]), ${f} select, ${f} textarea, ${f} button, ${f} .key`))
        .filter((el) => el.getBoundingClientRect().height < 44).map((el) => el.getAttribute('name') || el.className || el.tagName), form);
      if (short.length) out.push(`under 44px tall: ${short.join(', ')}`);
      // The switch: a tap on a key checks its radio and rings the key.
      await page.locator(`${form} .key`).nth(1).click();
      const picked = await page.evaluate((f) => {
        const k = document.querySelectorAll(`${f} .key`)[1];
        return { checked: (k.querySelector('input') as HTMLInputElement).checked, ring: getComputedStyle(k).boxShadow };
      }, form);
      if (!picked.checked) out.push('a tap on the delivery key does not pick it');
      if (!/3px/.test(picked.ring)) out.push('the picked key has no 3px ring');
      await page.locator(`${form} [type="submit"]`).click();
      const name = page.locator(`${form} [name="name"]`);
      if ((await name.getAttribute('aria-invalid')) !== 'true') out.push('an empty submit does not mark the name aria-invalid');
      const desc = await name.getAttribute('aria-describedby');
      if (!desc || !(await page.locator(`#${desc}`).isVisible())) out.push('the invalid name is not described by a painted error line');
      out.push(...(await emailMessages(page, form, `${form} [name="email"]`)));
      out.push(...await page.evaluate(() => {
        const root = document.querySelector('.city-photo-at-the-edge')!;
        const img = root.querySelector('.ph img')!.getBoundingClientRect();
        return img.width < 200 ? [`the photo paints ${Math.round(img.width)}px wide`] : [];
      }));
      return out;
    },
  },
  'city-contents-photo-index': {
    present: '.city-contents-photo-index',
    run: async (page, viewport) => {
      // The user's ruling (answer board q05, 2026-09-29): the contents list is hidden from 1024px,
      // where the dial takes over, as the other pages' SectionSheet is; shown at 375 and 768.
      const painted = await page.locator('.city-contents-photo-index').isVisible();
      if (viewport >= 1024) {
        return painted ? [`the contents list is painted at ${viewport}px, where the dial navigates`] : [];
      }
      if (!painted) return [`the contents list is not painted at ${viewport}px`];
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
        // THE BAND SLIDES AWAY ON THE WAY DOWN AND COMES BACK ON THE WAY UP (the user's ruling,
        // answer board q03, 2026-09-29), under both motion preferences: with reduced motion it
        // does not slide, but it still hides and shows. Every read waits on the state it judges
        // (the 10s ceiling is only a ceiling), never on a clock.
        const where = (): Promise<{ top: number; bottom: number; hdr: number }> => band.evaluate((el) => {
          const r = el.getBoundingClientRect();
          const hdr = document.querySelector('.kit-hdr')?.getBoundingClientRect().bottom ?? 0;
          return { top: r.top, bottom: r.bottom, hdr };
        });
        // Off screen: nothing of it below the site header's bottom edge (it slides up behind the
        // header, z 50 over its 30, and on out of the viewport).
        const offScreen = () => page.waitForFunction(() => {
          const el = document.querySelector('[data-city-jump-stepper]')!;
          return el.getBoundingClientRect().bottom <= 0.5;
        }, null, { timeout: 10_000, polling: 'raf' }).then(() => true, () => false);
        // Back: its top edge sits on the header's bottom edge, as a sticky band does.
        const back = () => page.waitForFunction(() => {
          const el = document.querySelector('[data-city-jump-stepper]')!;
          const hdr = document.querySelector('.kit-hdr')?.getBoundingClientRect().bottom ?? 0;
          return Math.abs(el.getBoundingClientRect().top - hdr) <= 1.5;
        }, null, { timeout: 10_000, polling: 'raf' }).then(() => true, () => false);
        for (const motion of ['reduce', 'no-preference'] as const) {
          await page.emulateMedia({ reducedMotion: motion });
          const m = `reducedMotion=${motion}:`;
          const dur = await band.evaluate((el) => getComputedStyle(el).transitionDuration);
          if (motion === 'reduce' && dur.split(',').some((d) => parseFloat(d) > 0)) out.push(`${m} the band still animates (${dur})`);
          await scrollSettled(page, 900);
          if (!(await offScreen())) out.push(`${m} after scrolling down 900px the band is still on screen (${JSON.stringify(await where())})`);
          await scrollSettled(page, 600);
          if (!(await back())) out.push(`${m} after scrolling back up the band is not back under the header (${JSON.stringify(await where())})`);
          // Focus inside keeps it shown: hide it, then move a keyboard focus into the rail.
          await scrollSettled(page, 1400);
          if (!(await offScreen())) out.push(`${m} after scrolling down again the band is still on screen`);
          await page.keyboard.press('Shift');
          await band.locator('.rail a').first().focus();
          if (!(await back())) out.push(`${m} a keyboard focus inside the band does not bring it back`);
          await scrollSettled(page, 2200);
          // One frame for the scroll handler, then it must still be where focus holds it.
          await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(null)))));
          if (!(await back())) out.push(`${m} the band hides while focus is inside it`);
          await band.locator('.rail a').first().evaluate((a) => (a as HTMLElement).blur());
          // An open sheet holds it too: open it from the shown band with a tap on its key, as a
          // reader does, and scroll down behind it. (A sheet opened by script has no opener, so
          // its focus would have nowhere to return to when it shuts.)
          await scrollSettled(page, 1000);
          await back();
          await band.locator('[data-jump-open]').click();
          await scrollSettled(page, 2600);
          await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(null)))));
          if (!(await back())) out.push(`${m} the band hides while its sheet is open`);
          await band.locator('[data-jump-close]').click();
          if (!(await page.waitForFunction(() => !document.querySelector<HTMLDialogElement>('[data-city-jump-stepper] [data-jump-sheet]')!.open,
            null, { timeout: 10_000, polling: 'raf' }).then(() => true, () => false))) out.push(`${m} the sheet's Close button does not shut it`);
          // At the top of the page it shows, whatever the last direction was.
          await scrollSettled(page, 3200);
          if (!(await offScreen())) out.push(`${m} after the sheet shuts, scrolling down does not hide the band`);
          await scrollSettled(page, 0);
          if (!(await back())) out.push(`${m} at the top of the page the band is not shown`);
        }
        await page.emulateMedia({ reducedMotion: null });
        await scrollSettled(page, 0);
      }
      const opener = band.locator('[data-jump-open]');
      const box = await opener.boundingBox();
      if (!box || box.height < 44) out.push('the sheet key is under 44px tall');
      // WAIT ON THE CONDITION, NEVER A CLOCK (Task 8b, M-new-1). On four workers on a busy
      // machine the sheet's open and its `close` task (which resets the key) landed after the
      // fixed 1s this probe used to allow, about one full run in three; a sheet left open then
      // made the page inert and failed the next probe too. Each read now waits for the state it
      // judges (the ceiling is only a ceiling), and the probe always leaves the sheet shut.
      const sheetState = (want: { open: boolean; expanded: string }) => page.waitForFunction((w) => {
        const d = document.querySelector<HTMLDialogElement>('[data-city-jump-stepper] [data-jump-sheet]');
        const k = document.querySelector('[data-city-jump-stepper] [data-jump-open]');
        return !!d && !!k && d.open === w.open && k.getAttribute('aria-expanded') === w.expanded;
      }, want, { timeout: 10_000, polling: 'raf' }).then(() => true, () => false);
      await opener.click();
      if (!(await sheetState({ open: true, expanded: 'true' }))) {
        const open = await band.locator('[data-jump-sheet]').evaluate((d) => (d as HTMLDialogElement).open);
        out.push(open ? 'the key does not report aria-expanded="true"' : 'pressing the key does not open the sheet');
      }
      await page.keyboard.press('Escape');
      if (!(await sheetState({ open: false, expanded: 'false' }))) {
        const closed = await band.locator('[data-jump-sheet]').evaluate((d) => !(d as HTMLDialogElement).open);
        out.push(closed ? 'after Escape the key still reports aria-expanded="true"' : 'Escape does not close the sheet');
        // Leave the page usable for the next probe whatever happened here.
        await band.locator('[data-jump-sheet]').evaluate((d) => (d as HTMLDialogElement).close());
      }
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
      // M6: a keyboard focus on an Ask link rings its whole print, through the link's own ::after.
      await scrollSettled(page, 0);
      const ask = page.locator('.city-pup .ask').first();
      await ask.focus();
      await page.keyboard.press('Shift+Tab');
      await page.keyboard.press('Tab');
      const ring = await ask.evaluate((a) => ({ fv: a.matches(':focus-visible'), style: getComputedStyle(a, '::after').outlineStyle,
        width: getComputedStyle(a, '::after').outlineWidth }));
      if (!ring.fv || ring.style !== 'solid' || ring.width !== '3px') out.push(`a keyboard-focused Ask link draws no 3px ring on its print (${JSON.stringify(ring)})`);
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
      // tests/render/lib/cityChapterImageFirst.ts: an `img.bl-img`, or a `<picture>` holding one.
      const r = await page.evaluate(cityChapterImageFirst);
      if (!r.examined) return ['the page has .city-chapters but no chapter H3 to examine'];
      return r.bad.length
        ? [`${r.bad.length} chapter heading(s) not followed straight by their .bl-img photo (layout-h3-image-first): ${r.bad.join(' | ')}`]
        : [];
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
      out.push(...(await emailMessages(page, '[data-newsletter]', '[data-newsletter] input[type="email"]')));
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
      out.push(...(await emailMessages(page, '[data-contact-form]', '[data-contact-form] [name="email"]')));
      // M7: the invalid border reads at 3:1 or more against the band it sits on (WCAG 1.4.11).
      const ratio = await page.evaluate(() => {
        const lum = (rgb: string) => {
          const c = (rgb.match(/[\d.]+/g) ?? []).slice(0, 3).map((v) => Number(v) / 255)
            .map((x) => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
          return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
        };
        const field = document.querySelector('[data-contact-form] [name="name"]')!;
        const band = getComputedStyle(document.querySelector('.city-contact')!).backgroundColor;
        const [a, b] = [lum(getComputedStyle(field).borderTopColor), lum(band)].sort((x, y) => y - x);
        return (a + 0.05) / (b + 0.05);
      });
      if (ratio < 3) out.push(`the invalid border is ${ratio.toFixed(2)}:1 against the band (3:1 needed)`);
      return out;
    },
  },
  // The Task 7b review, item 1 (I3 in the quality review): tests/render/lib/cityLayoutFollowsBox.ts.
  'city-layout-follows-box': {
    present: '.city-kit',
    run: async (page, viewport) => {
      const path = new URL(page.url()).pathname;
      const absent = absentOn(path);
      const r = await page.evaluate(cityLayoutFollowsBox, { viewport, tier: TIER, absent });
      console.log(`city-layout-follows-box @ ${viewport}px: examined ${r.examined}, declared absent ${Object.keys(absent).join(', ') || 'none'}`);
      return r.defects;
    },
  },
  // Task 7b item 10 (the user's type-fit ruling): heading caps and lines, paragraph measure
  // and length, section height, per tier (tests/render/lib/cityTypeFit.ts).
  'city-type-fit': {
    present: '.city-kit',
    run: async (page, viewport) => {
      const fullWidthSpecimen = FULL_WIDTH_SPECIMENS.has(new URL(page.url()).pathname);
      const r = await page.evaluate(cityTypeFit, { viewport, tier: TIER, caps: HEADING_CAPS, fullWidthSpecimen });
      console.log(`city-type-fit @ ${viewport}px: examined ${r.examined}`);
      return r.examined ? r.defects : ['city-type-fit examined nothing'];
    },
  },
  // Learning loop 2026-09-27, L8: the current-section marker, under BOTH motion preferences.
  // Scroll the fourth section to the reading band and read which row is current, on the dial at
  // a desktop width and on the band's rail below it.
  'city-nav-current-section': {
    present: '[data-city-dial-photo-marker], [data-city-jump-stepper]',
    run: (page, viewport) => navCurrentSection(page, viewport >= 1024 ? '[data-city-dial-photo-marker]' : '[data-city-jump-stepper] .rail'),
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
      // Lazy images paint only once scrolled near: walk the page and wait for every image to
      // decode, so the design passes judge photographs, not empty boxes (Plan 2 Task 8).
      const unloaded = await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += window.innerHeight / 2) {
          window.scrollTo(0, y);
          await new Promise((r) => requestAnimationFrame(() => r(null)));
        }
        // A lazy image that is never painted (display:none below a tier) never loads, so each
        // wait is capped: the shot is for eyes, not a gate.
        const settle = (i: HTMLImageElement) => Promise.race([i.decode().catch(() => null),
          new Promise((r) => setTimeout(r, 3000))]);
        await Promise.all(Array.from(document.images).map((i) => (i.complete ? null : settle(i))));
        window.scrollTo(0, 0);
        // A painted image that never decoded is an empty box in the shot: say so (M8).
        return Array.from(document.images).filter((i) => (!i.complete || i.naturalWidth === 0)
          && i.getBoundingClientRect().width > 0).map((i) => i.currentSrc || i.src);
      });
      if (unloaded.length) {
        console.warn(`[shots] ${route} @ ${viewport}px: ${unloaded.length} painted image(s) never loaded: ${unloaded.slice(0, 3).join(', ')}`);
        testInfo.annotations.push({ type: 'shots', description: `${unloaded.length} image(s) never loaded` });
      }
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
    // CITY_CPU_THROTTLE=<n> slows the page's CPU n times for the component probes (Chrome
    // DevTools Protocol), to reproduce on demand the load under which a probe that waits on a
    // clock races its condition (Task 8b, M-new-1: four workers on a busy machine).
    if (process.env.CITY_CPU_THROTTLE) {
      const cdp = await page.context().newCDPSession(page);
      await cdp.send('Emulation.setCPUThrottlingRate', { rate: Number(process.env.CITY_CPU_THROTTLE) });
    }
    let probed = 0;
    for (const [id, probe] of Object.entries(PROBES)) {
      await scrollSettled(page, 0);
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
    const r = await page.evaluate(cityTypeFit, { viewport, tier: TIER, caps: HEADING_CAPS });
    expect(r.examined, 'the fixture must be examined').toBeGreaterThan(0);
    if (kind === 'broken') {
      // Each kind of defect fires on its own element, not merely "something fired".
      const kinds: [string, RegExp][] = [
        ['heading cap', /is [\d.]+px, over the \w+ cap/],
        ['heading lines', /wraps to \d+ lines/],
        ['75ch measure', /ch wide \(75 max\)/],
        // A form's text paragraph (the privacy note) is reading text; only a row holding a
        // control is layout (visual-intelligence audit 2026-10-04, rec 6).
        ['form note measure', /a paragraph "We reply by email[^"]*" is \d+ch wide \(75 max\)/],
        ['paragraph lines', /runs \d+ lines \(\d max/],
        ['heading measure', /^city-narrow-measure .*heading measure too narrow for its box/],
        // Answer board q06 (2026-09-29): a layout column that stacks the H2 to three lines is a
        // defect too; the takeaways' 5fr head column is no longer excused.
        ['heading column', /^city-narrow-column .*H2 .*wraps to 3 lines.*heading column too narrow for its box/],
        // London final fixes (2026-10-04): an image with no box until its file loads leaves the
        // height it sits in unmeasurable, at every width; the check reports it.
        ['unreserved image', /^city-chapters .*an image "pending-phone-infographic\.webp" holds no box until it loads/],
      ];
      // Section height is judged at a phone width and from 1280 only (the ruling's two caps).
      if (viewport < 768 || viewport >= 1280) kinds.push(['section height', /the section is \d+px tall/]);
      // q10 (a), 2026-10-04: one over-tall H3 answer, and one over-tall puppy card, still fail
      // when height is judged per answer and per card rather than per chapter.
      if (viewport < 768 || viewport >= 1280) {
        kinds.push(['answer height', /^city-chapters .*the H3 answer "An Answer That Runs On" is \d+px tall/]);
        kinds.push(['card height', /^city-ticket-strip .*a puppy card "Byrd" is \d+px tall/]);
      }
      // ...and the piece nested in that answer is not reported a second time as a section.
      expect(r.defects.some((d) => /^city-places-by-publisher .*the section is/.test(d)),
        `a nested component was judged as a section: ${r.defects.join(' | ')}`).toBe(false);
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
  const r = await page.evaluate(cityTypeFit, { viewport, tier: TIER, caps: HEADING_CAPS });
  for (const box of ['city-narrow', 'city-edge']) {
    expect(r.defects.some((d) => d.startsWith(box) && /over the tablet cap of 25px/.test(d)),
      `${box}: a 27px H2 was not judged against the tablet cap: ${r.defects.join(' | ')}`).toBe(true);
  }
});

// The price-scale check cannot pass a page with no price scale (Task 8b, M-new-2): the edge-width
// runs call it on every route, and an empty result there must mean "measured and clean".
test('priceScaleSpill fails a page with no price scale', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp1280', 'run once');
  await page.setContent('<main><p>No city section here.</p></main>');
  const r = await priceScaleSpill(page);
  expect(r.some((d) => /no price scale/.test(d)), r.join(' | ')).toBe(true);
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
    // 640 is the tablet edge itself and 667 a phone held landscape (iPhone SE), where the price
    // scale first lays its stops on one line (the Task 8 quality review, I1).
    for (const width of [640, 660, 667, 1160]) {
      await page.setViewportSize({ width, height: 900 });
      const res = await page.goto(route);
      expect(res?.status()).toBe(200);
      await page.evaluate(() => document.fonts.ready);
      const fullWidthSpecimen = FULL_WIDTH_SPECIMENS.has(route);
      const t = await page.evaluate(cityTypeFit, { viewport: width, tier: TIER, caps: HEADING_CAPS, fullWidthSpecimen });
      const l = await page.evaluate(cityLayoutFollowsBox, { viewport: width, tier: TIER, absent: absentOn(route) });
      console.log(`${route} @ ${width}px: city-type-fit examined ${t.examined}, city-layout-follows-box examined ${l.examined}`);
      expect(t.examined).toBeGreaterThan(0);
      // Each city's counter at the edge widths: London's price scale, Manchester's range sheet.
      const scale = routeCity(route) === 'manchester' ? await rangeSheetSpill(page) : await priceScaleSpill(page);
      expect([...t.defects, ...l.defects, ...scale], `${route} at ${width}px`).toEqual([]);
    }
  });
}

// The Task 10b review, items 3 and 4, as behaviour on the London page at a phone width.
// 3: an iOS fling past the bottom rubber-bands scrollY above its maximum and back; the band must
//    not read the bounce back as a scroll up. 4: a browser without :focus-visible (Safari before
//    15.4) throws on the selector; the band's frame must not throw, and the band still tucks.
test('the jump band ignores overscroll and survives a browser without :focus-visible', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp375', 'run once, at a phone width');
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.addInitScript(() => {
    for (const proto of [Element.prototype, Document.prototype] as const) {
      for (const fn of ['matches', 'querySelector', 'querySelectorAll'] as const) {
        const orig = (proto as any)[fn];
        if (!orig) continue;
        (proto as any)[fn] = function (sel: string, ...rest: unknown[]) {
          if (typeof sel === 'string' && sel.includes(':focus-visible')) throw new SyntaxError(`'${sel}' is not a valid selector`);
          return orig.call(this, sel, ...rest);
        };
      }
    }
  });
  const res = await page.goto('/uk-locations/blue-staffy-puppies-london/');
  expect(res?.status()).toBe(200);
  const tucked = () => page.evaluate(() => document.querySelector('[data-city-jump-stepper]')!.hasAttribute('data-tucked'));
  const frames = () => page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(null)))));
  // Scroll to the very bottom: the band tucks (and nothing throws on the missing selector).
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await page.waitForFunction(() => document.querySelector('[data-city-jump-stepper]')!.hasAttribute('data-tucked'), null, { timeout: 10_000, polling: 'raf' }).catch(() => {});
  expect(await tucked(), 'scrolling to the bottom tucks the band').toBe(true);
  // The rubber band: scrollY reads 120px past the maximum, then settles back on it.
  await page.evaluate(() => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    Object.defineProperty(window, 'scrollY', { configurable: true, get: () => max + 120 });
    window.dispatchEvent(new Event('scroll'));
  });
  await frames();
  await page.evaluate(() => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    Object.defineProperty(window, 'scrollY', { configurable: true, get: () => max });
    window.dispatchEvent(new Event('scroll'));
  });
  await frames();
  expect(await tucked(), 'the overscroll bounce brought the band back').toBe(true);
  expect(errors, 'the band threw on a browser without :focus-visible').toEqual([]);
});

// The Task 10b re-review, item 5: the :focus-visible guard itself. With a focus INSIDE the band
// the hold reads `activeElement.matches(':focus-visible')`, which throws before Safari 15.4. The
// try must swallow it: no page error, and (the hold unknowable there) the band still tucks.
test('a keyboard focus inside the band on a browser without :focus-visible throws nothing', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp375', 'run once, at a phone width');
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.addInitScript(() => {
    for (const proto of [Element.prototype, Document.prototype] as const) {
      for (const fn of ['matches', 'querySelector', 'querySelectorAll'] as const) {
        const orig = (proto as any)[fn];
        if (!orig) continue;
        (proto as any)[fn] = function (sel: string, ...rest: unknown[]) {
          if (typeof sel === 'string' && sel.includes(':focus-visible')) throw new SyntaxError(`'${sel}' is not a valid selector`);
          return orig.call(this, sel, ...rest);
        };
      }
    }
  });
  const res = await page.goto('/uk-locations/blue-staffy-puppies-london/');
  expect(res?.status()).toBe(200);
  // A keyboard focus on the sheet key: a key press first, so the focus is a keyboard one.
  await page.keyboard.press('Shift');
  await page.locator('[data-city-jump-stepper] [data-jump-open]').focus();
  expect(await page.evaluate(() => !!document.activeElement?.closest('[data-city-jump-stepper]'))).toBe(true);
  for (const y of [900, 1800, 2700]) {
    await page.evaluate((v) => window.scrollTo(0, v), y);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(null)))));
  }
  expect(errors, 'the hold threw on a browser without :focus-visible').toEqual([]);
  await page.waitForFunction(() => document.querySelector('[data-city-jump-stepper]')!.hasAttribute('data-tucked'),
    null, { timeout: 10_000, polling: 'raf' }).catch(() => {});
  expect(await page.evaluate(() => document.querySelector('[data-city-jump-stepper]')!.hasAttribute('data-tucked')),
    'with the hold unknowable, scrolling down still tucks the band').toBe(true);
});

// WHY THE PROBES SCROLL WITH scrollSettled (lessons entry 20, 2026-10-06). The jump band reads the
// scroll position once per frame and tucks on the way down from the last frame's reading, so two
// scrolls in one frame are one scroll to it. From 1200, the reset to the top and the probe's first
// scroll down (0, then 900) in one frame read as 1200 -> 900, a scroll up, and the band stayed on
// screen: the jump band probe's flake at 375. Both halves are held: the same-frame pair is still one
// scroll (if this ever changes, the helper is no longer what makes the probe deterministic), and
// with each scroll settled the band tucks.
test('two scrolls in one frame are one scroll to the jump band; settled, each is read', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp375', 'the band navigates below 1024px');
  const res = await page.goto('/kit-preview/city-page/');
  expect(res?.status()).toBe(200);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const tucked = () => page.evaluate(() => document.querySelector('[data-city-jump-stepper]')!.hasAttribute('data-tucked'));
  await scrollSettled(page, 600);
  await scrollSettled(page, 1200);
  expect(await tucked(), 'scrolling down to 1200 tucks the band').toBe(true);
  await page.evaluate(() => { window.scrollTo(0, 0); window.scrollTo(0, 900); });
  await scrollSettled(page, 900);
  expect(await tucked(), 'two scrolls in one frame were read as two').toBe(false);
  await scrollSettled(page, 1200);
  await scrollSettled(page, 0);
  await scrollSettled(page, 900);
  expect(await tucked(), 'with each scroll settled, 0 then 900 is a scroll down and tucks the band').toBe(true);
});

// THE CURRENT SECTION FOLLOWS THE READER AFTER A JUMP THAT LANDS A BOUNDARY IN THE BAND (lessons
// entry 20, 2026-10-06). src/lib/scrollSpy.ts read the current section from the observer's last
// batch, which holds only the targets whose state changed: a jump putting the boundary between two
// sections inside the reading band (40-45%) reports both entering and the upper one wins; the next
// scroll, which fills the band with the lower one, reports only the upper one leaving, so the row
// stayed on the section the reader had left. city-nav-current-section met it only when an earlier
// probe happened to leave the page at such a boundary and no frame was painted at the top between
// (one run in several on four workers: "section pg-city-video-panel in the reading band, current is
// [pg-city-takeaways-ledger]"). Here it is met on purpose, for every pair of touching sections, on
// the dial (1280) and on the band's rail (375). Each read waits on the state it judges.
for (const route of ['/kit-preview/city-page/', LONDON]) {
  test(`the current section follows a jump that lands a boundary in the band on ${route}`, async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'vp375' && testInfo.project.name !== 'vp1280', 'the rail at a phone width, the dial at a desktop one');
    const scope = testInfo.project.name === 'vp1280' ? '[data-city-dial-photo-marker]' : '[data-city-jump-stepper] .rail';
    const res = await page.goto(route);
    expect(res?.status()).toBe(200);
    await page.evaluate(() => document.fonts.ready);
    await page.emulateMedia({ reducedMotion: 'reduce' });
    const pairs = await page.evaluate((s) => {
      const rows = Array.from(document.querySelectorAll<HTMLAnchorElement>(`${s} [data-spy]`))
        .map((a) => { const r = document.getElementById(a.dataset.spy!)!.getBoundingClientRect(); return { id: a.dataset.spy!, top: r.top + scrollY, bottom: r.bottom + scrollY }; });
      // Touching sections, the lower one tall enough to fill the band from 30% of the viewport.
      return rows.slice(1).map((b, i) => ({ a: rows[i].id, b: b.id, boundary: b.top, fits: rows[i].bottom >= b.top - 2 && b.bottom - b.top >= innerHeight * 0.2 }))
        .filter((x) => x.fits);
    }, scope);
    console.log(`spy after a boundary jump on ${route} @ ${testInfo.project.name}: examined ${pairs.length} pair(s)`);
    expect(pairs.length, 'no two touching sections to jump between').toBeGreaterThan(1);
    const vh = page.viewportSize()!.height;
    const current = () => page.evaluate((s) => Array.from(document.querySelectorAll<HTMLAnchorElement>(`${s} [aria-current="location"]`)).map((a) => a.dataset.spy), scope);
    const becomes = (want: string) => page.waitForFunction(({ s, w }) => {
      const cur = Array.from(document.querySelectorAll<HTMLAnchorElement>(`${s} [aria-current="location"]`));
      return cur.length === 1 && cur[0].dataset.spy === w;
    }, { s: scope, w: want }, { timeout: 10_000, polling: 'raf' }).then(() => true, () => false);
    const stuck: string[] = [];
    for (const { a, b, boundary } of pairs) {
      // The boundary at 42.5%, inside the band: both sections are in it, the upper one is current.
      await scrollSettled(page, Math.round(boundary - vh * 0.425));
      if (!(await becomes(a))) stuck.push(`${a}|${b}: with the boundary in the band, current is [${await current()}], not ${a}`);
      // The lower section's top at 30%: only it is in the band, and it must become current.
      await scrollSettled(page, Math.round(boundary - vh * 0.3));
      if (!(await becomes(b))) stuck.push(`${a}|${b}: with ${b} filling the band, current is [${await current()}]`);
    }
    expect(stuck).toEqual([]);
  });
}

// THE DIAL SHOWS THE ROW IT MARKS (impeccable Harden pass, 2026-10-06b, F1). The dial is sticky and
// scrolls inside its own box (`max-height: 100vh - header`, `overflow-y: auto`). On a laptop-height
// screen its last rows sit below that box's edge, so in the last sections (everyday health, the
// enquiry at 1280x800; the breed section too at 1024x768) "Where you are on the page" showed no
// current row at all. Every row, once current, must be inside the dial's visible box.
for (const route of ['/kit-preview/city-page/', LONDON]) {
  test(`the dial keeps its current row in view on ${route}`, async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'vp1280', 'the dial shows from 1024');
    const hidden: string[] = [];
    let examined = 0;
    for (const vp of [{ width: 1280, height: 800 }, { width: 1024, height: 720 }]) {
      await page.setViewportSize(vp);
      const res = await page.goto(route);
      expect(res?.status()).toBe(200);
      await page.evaluate(() => document.fonts.ready);
      await page.emulateMedia({ reducedMotion: 'reduce' });
      const ids = await page.evaluate(() => Array.from(document.querySelectorAll<HTMLAnchorElement>('[data-city-dial-photo-marker] [data-spy]')).map((a) => a.dataset.spy!));
      for (const id of ids) {
        // The section's top at 30%: it fills the reading band (or, for the last one, the page ends).
        const y = await page.evaluate((i) => Math.round(document.getElementById(i)!.getBoundingClientRect().top + scrollY - innerHeight * 0.3), id);
        await scrollSettled(page, y);
        const ok = await page.waitForFunction((i) => {
          const d = document.querySelector<HTMLElement>('[data-city-dial-photo-marker]')!;
          const cur = d.querySelector<HTMLAnchorElement>('[aria-current="location"]');
          if (!cur || cur.dataset.spy !== i) return false;
          const a = d.getBoundingClientRect(), r = cur.getBoundingClientRect();
          return r.top >= a.top - 1 && r.bottom <= a.bottom + 1;
        }, id, { timeout: 5_000, polling: 'raf' }).then(() => true, () => false);
        examined++;
        if (!ok) hidden.push(await page.evaluate((i) => {
          const d = document.querySelector<HTMLElement>('[data-city-dial-photo-marker]')!;
          const cur = d.querySelector<HTMLAnchorElement>('[aria-current="location"]');
          const a = d.getBoundingClientRect(), r = cur?.getBoundingClientRect();
          return `${innerWidth}x${innerHeight} ${i}: current [${cur?.dataset.spy}] at ${r ? `${Math.round(r.top)}-${Math.round(r.bottom)}` : '-'}, dial shows ${Math.round(a.top)}-${Math.round(a.bottom)}`;
        }, id));
      }
    }
    console.log(`dial row in view on ${route}: examined ${examined} row(s)`);
    expect(examined).toBeGreaterThan(5);
    expect(hidden).toEqual([]);
  });
}

// city-layout-follows-box's `absent` (2026-10-04): London's approved board mounts no puppy sheet
// and no video panel, and the check reported both "matches no section on the page" at every width.
// A declared-absent key is not demanded; every other key still is; and a key declared absent that
// the page carries is a defect (a stale declaration).
test('city-layout-follows-box honours a declared-absent key, demands the rest, refuses a stale one', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp1280', 'run once');
  await page.setContent('<main><p>No city section here.</p></main>');
  const r = await page.evaluate(cityLayoutFollowsBox, { viewport: 1280, tier: TIER, absent: { '.city-sheet': 'not on this board' } });
  expect(r.defects.some((d) => d.startsWith('.city-sheet ')), r.defects.join(' | ')).toBe(false);
  expect(r.defects.some((d) => /^\.city-video matches no section on the page/.test(d)), r.defects.join(' | ')).toBe(true);
  await page.setContent('<section class="city-sheet" style="width:900px"></section>');
  const r2 = await page.evaluate(cityLayoutFollowsBox, { viewport: 1280, tier: TIER, absent: { '.city-sheet': 'not on this board' } });
  expect(r2.defects.some((d) => /^\.city-sheet is declared absent .* but the page carries it/.test(d)), r2.defects.join(' | ')).toBe(true);
});

// The declaration is derived from the board, never typed: London's is exactly the two components
// its board does not mount, and SPEC_COMPONENT names every SPEC key in the function's own source.
test("London's declared-absent keys are the components its board does not mount", async ({}, testInfo) => {
  test.skip(testInfo.project.name !== 'vp1280', 'run once');
  expect(Object.keys(absentFor(LONDON)).sort()).toEqual(['.city-sheet', '.city-video']);
  const keys = [...cityLayoutFollowsBox.toString().matchAll(/["'](\.city[^"']*)["']:\s*\{\s*tablet/g)].map((m) => m[1]).sort();
  expect(keys.length).toBeGreaterThan(5);
  expect(Object.keys(SPEC_COMPONENT).sort()).toEqual(keys);
});

// The city-chapters probe (tests/render/lib/cityChapterImageFirst.ts) against its own cases: the
// photo straight after the H3 as an `img.bl-img` or a `<picture>` holding one passes; prose first,
// or a `<picture>` with no `.bl-img`, fails (2026-10-04: the probe had read the art-directed
// infographics' `<picture>` as "no photo" on London at every width).
test('the city-chapters probe takes a picture wrapping a .bl-img and still fails prose first', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp1280', 'run once');
  await page.setContent(`<section class="city-chapters">
    <div class="ch"><h3>Good Img</h3><img class="bl-img" alt="a"><p>Prose.</p></div>
    <div class="ch"><h3>Good Picture</h3><picture><source media="(max-width: 639px)" srcset="x.webp"><img class="bl-img" alt="b"></picture><p>Prose.</p></div>
    <div class="ch"><h3>Prose First</h3><p>Prose.</p><img class="bl-img" alt="c"></div>
    <div class="ch"><h3>Bare Picture</h3><picture><img alt="d"></picture></div>
  </section>`);
  const r = await page.evaluate(cityChapterImageFirst);
  expect(r.examined).toBe(4);
  expect(r.bad).toEqual(['Prose First', 'Bare Picture']);
});

// A PHONE INFOGRAPHIC RESERVES ITS BOX BEFORE IT LOADS (London final fixes, 2026-10-04). Below
// 640px an art-directed infographic paints its `<source>`'s tall phone file (BodyImage `phone`),
// and src/styles/board-styles.css set `aspect-ratio: auto` on it so the box would take that file's
// ratio. An author `auto` also cancels the ratio the source's width and height attributes give
// the img, so until the lazy file arrived the box was 0px tall, and it then grew by up to 1,755px
// (the AmStaff standards chart at 375): a layout shift under the reader, and an answer whose
// measured height depended on whether an earlier probe had scrolled it into loading. The files are
// held unloaded here, so the box the page reserves is all there is to measure.
test('every phone infographic reserves its own box before its file loads', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp375', 'the phone layout paints below 640px');
  await page.route('**/*-phone.webp', () => { /* never fulfilled: the box must stand without the file */ });
  const res = await page.goto(LONDON, { waitUntil: 'domcontentloaded' });
  expect(res?.status()).toBe(200);
  const boxes = await page.evaluate(() => Array.from(document.querySelectorAll<HTMLImageElement>('picture > img.art-phone'))
    .map((img) => {
      const src = img.parentElement!.querySelector('source')!;
      const r = img.getBoundingClientRect();
      // A cropped phone file (BodyImage `phone.crop`, London final fixes M1) reserves the cropped
      // box it paints, which its `data-art-crop` states as <w>x<h>; any other, the file's own.
      const [cw, ch] = (img.dataset.artCrop ?? `${src.getAttribute('width')}x${src.getAttribute('height')}`).split('x').map(Number);
      return { file: (src.getAttribute('srcset') ?? '').split(/[\s,]/)[0], loaded: img.complete && img.naturalWidth > 0,
        w: r.width, h: r.height, want: r.width * ch / cw };
    }));
  console.log(`phone infographic boxes @ 375px: examined ${boxes.length}`);
  expect(boxes.length, 'London carries its six art-directed infographics').toBe(6);
  for (const b of boxes) {
    expect(b.loaded, `${b.file} was held unloaded`).toBe(false);
    expect(Math.abs(b.h - b.want), `${b.file}: ${Math.round(b.h)}px reserved, ${Math.round(b.want)}px once it loads`).toBeLessThanOrEqual(1);
  }
});

// THE SAME BOX ONCE THE FILE HAS LOADED (London final fixes M1, answer board 2026-10-05 q04 (a)):
// a cropped phone file's box is an explicit ratio, not the source's `auto <w> / <h>` hint, which a
// loaded file would override and so grow the box back to the whole file. Every phone file is
// loaded here and each box must still be the one reserved for it: the crop's for a cropped file,
// the file's own for the rest, at 375 and in the 431-639px band (N360, q05 (a)), where the box is
// held at 360px, centred.
test('every phone infographic keeps its reserved box once its file loads', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp375', 'the phone layout paints below 640px');
  for (const width of [375, 600]) {
    await page.setViewportSize({ width, height: 900 });
    const res = await page.goto(LONDON, { waitUntil: 'domcontentloaded' });
    expect(res?.status()).toBe(200);
    const boxes = await page.evaluate(async () => {
      const imgs = Array.from(document.querySelectorAll<HTMLImageElement>('picture > img.art-phone'));
      imgs.forEach((i) => { i.loading = 'eager'; });
      await Promise.all(imgs.map((i) => (i.complete && i.naturalWidth ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
      return imgs.map((img) => {
        const src = img.parentElement!.querySelector('source')!;
        const r = img.getBoundingClientRect();
        const [cw, ch] = (img.dataset.artCrop ?? `${src.getAttribute('width')}x${src.getAttribute('height')}`).split('x').map(Number);
        return { file: img.currentSrc.split('/').pop(), loaded: img.complete && img.naturalWidth > 0, cropped: !!img.dataset.artCrop,
          w: r.width, h: r.height, want: r.width * ch / cw };
      });
    });
    console.log(`phone infographic boxes, loaded @ ${width}px: examined ${boxes.length}, cropped ${boxes.filter((b) => b.cropped).length}`);
    expect(boxes.length, 'London carries its six art-directed infographics').toBe(6);
    expect(boxes.filter((b) => b.cropped).length, 'the AmStaff phone file is cropped (M1)').toBe(1);
    for (const b of boxes) {
      expect(b.loaded, `${b.file} loaded`).toBe(true);
      expect(b.file, 'below 640px the phone file paints').toMatch(/-phone\.webp$/);
      expect(b.w, `${b.file} is held at 360px or less (N360)`).toBeLessThanOrEqual(360.5);
      expect(Math.abs(b.h - b.want), `${b.file}: ${Math.round(b.h)}px once loaded, ${Math.round(b.want)}px reserved`).toBeLessThanOrEqual(1);
    }
  }
});

// THE LONDON MAP (answer board 2026-10-06-london-map q01 (a) P1, q02 (a) S1; CityMapFacade, C20):
// a tap-to-load facade. Nothing is asked of any host but the site's own before the tap (the Known
// Issue 38 trade-off, met as working rule 14 meets it for video); the button is a real 44px
// control a keyboard reaches; and the tap puts the city-centre iframe into the reserved box, with
// its title, loading=lazy and referrerpolicy, without moving the answer that holds it. The query
// and the title are read from data/locations.json and data/settings.json, never typed here.
const LONDON_ROW = (JSON.parse(readFileSync(new URL('../../data/locations.json', import.meta.url), 'utf8')) as { slug: string; city: string }[])
  .find((r) => r.slug === 'blue-staffy-puppies-london')!;
const TOWN_NAME = (JSON.parse(readFileSync(new URL('../../data/settings.json', import.meta.url), 'utf8')) as { address: { city: string } }).address.city;
test('the London map asks nothing of Google until a tap, then loads the city centre in its own box', async ({ page, baseURL }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp375' && testInfo.project.name !== 'vp1280', 'a phone and a desktop width');
  const site = new URL(baseURL!).host;
  const offsite: string[] = [];
  page.on('request', (r) => { const u = new URL(r.url()); if (/^https?:$/.test(u.protocol) && u.host !== site) offsite.push(r.url()); });
  // The tap's request is answered here, so the test never depends on Google being reachable.
  await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, (route) => route.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><title>map</title>' }));
  const res = await page.goto(LONDON, { waitUntil: 'load' });
  expect(res?.status()).toBe(200);
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await page.waitForLoadState('networkidle');
  expect(offsite, 'a request left the site before the tap').toEqual([]);
  const offsiteAtLoad = offsite.length;
  const fig = page.locator('[data-city-map]');
  expect(await fig.count(), 'London carries one map').toBe(1);
  expect(await fig.evaluate((el) => !!el.closest('#delivery')), 'the map sits in the delivery section (P1)').toBe(true);
  const btn = fig.locator('[data-city-map-load]');
  await btn.scrollIntoViewIfNeeded();
  const box = await btn.boundingBox();
  expect(box && box.height >= 44, `the button is ${box?.height}px tall (44 min)`).toBe(true);
  expect(await btn.evaluate((b) => b.tagName === 'BUTTON' && (b as HTMLButtonElement).tabIndex >= 0 && !(b as HTMLButtonElement).disabled)).toBe(true);
  await btn.focus();
  expect(await btn.evaluate((b) => document.activeElement === b), 'a keyboard reaches the button').toBe(true);
  const stage = fig.locator('.stage');
  const answer = fig.locator('xpath=ancestor::*[contains(concat(" ", normalize-space(@class), " "), " ch ")][1]');
  const before = { stage: (await stage.boundingBox())!.height, answer: (await answer.boundingBox())!.height };
  expect(before.stage, 'the reserved box is at most 300px tall').toBeLessThanOrEqual(300.5);
  await btn.click();
  const frame = fig.locator('.stage iframe');
  await expect(frame).toHaveCount(1);
  const attrs = await frame.evaluate((f) => ({ src: f.getAttribute('src'), title: f.getAttribute('title'),
    loading: f.getAttribute('loading'), ref: f.getAttribute('referrerpolicy'), focused: document.activeElement === f }));
  console.log(`london map @ ${testInfo.project.name}: offsite before tap ${offsiteAtLoad}, after ${offsite.length}, button ${box?.height}px, box ${before.stage}px, after tap ${JSON.stringify(attrs)}`);
  expect(attrs.src).toBe(`https://maps.google.com/maps?q=${encodeURIComponent(`${LONDON_ROW.city}, UK`)}&z=10&hl=en&t=m&output=embed&iwloc=near`);
  expect(attrs.title).toBe(`${LONDON_ROW.city} — delivery from BlueStaffyUK in ${TOWN_NAME}`);
  expect(attrs.loading).toBe('lazy');
  expect(attrs.ref).toBe('no-referrer-when-downgrade');
  expect(attrs.focused, 'focus moves into the map').toBe(true);
  const after = { stage: (await stage.boundingBox())!.height, answer: (await answer.boundingBox())!.height };
  expect(Math.abs(after.stage - before.stage), 'the iframe takes the reserved box').toBeLessThanOrEqual(1);
  expect(Math.abs(after.answer - before.answer), 'nothing below the map moves').toBeLessThanOrEqual(1);
});

// THE MAP KEEPS A VISIBLE FOCUS AFTER A KEYBOARD TAP (impeccable Harden pass 2026-10-06, F1): the
// facade moves focus into the iframe it makes, and Chrome draws no ring on a programmatically
// focused iframe, so a keyboard reader lost sight of where they were (WCAG 2.4.7). A keyboard
// activation (a click with `detail` 0) marks the figure, and the live box draws the ring while the
// map holds focus. A mouse tap draws none.
test('a keyboard tap on the London map leaves a visible ring on the live map, a mouse tap none', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp375' && testInfo.project.name !== 'vp1280', 'a phone and a desktop width');
  await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, (route) => route.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><title>map</title>' }));
  const ring = () => page.evaluate(() => {
    const s = getComputedStyle(document.querySelector('[data-city-map] .stage')!);
    return { focused: document.activeElement?.tagName, style: s.outlineStyle, width: parseFloat(s.outlineWidth) };
  });
  await page.goto(LONDON, { waitUntil: 'load' });
  await page.locator('[data-city-map-load]').scrollIntoViewIfNeeded();
  await page.keyboard.press('Shift');
  await page.locator('[data-city-map-load]').focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-city-map] .stage iframe')).toHaveCount(1);
  const kbd = await ring();
  expect(kbd.focused).toBe('IFRAME');
  expect(kbd.style !== 'none' && kbd.width >= 2, `after a keyboard tap the map draws a ring: ${JSON.stringify(kbd)}`).toBe(true);
  await page.goto(LONDON, { waitUntil: 'load' });
  await page.locator('[data-city-map-load]').click();
  await expect(page.locator('[data-city-map] .stage iframe')).toHaveCount(1);
  const mouse = await ring();
  expect(mouse.style === 'none' || mouse.width === 0, `a mouse tap draws no ring: ${JSON.stringify(mouse)}`).toBe(true);
});

// THE COUNTER'S LABEL NEVER ENDS ON ONE WORD (frontend-design Harden pass 2026-10-06, F1): from an
// 840px viewport the count stands in a 14ch column beside the line, and "puppies available now"
// broke as "puppies available" / "now". Balanced, it reads "puppies" / "available now".
test("the price scale's count label ends on more than one word", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'vp1024' && testInfo.project.name !== 'vp1280', 'the count stands beside the line from 840px');
  await page.goto(LONDON, { waitUntil: 'load' });
  const r = await page.locator('.city-scale .count .l').first().evaluate((el) => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const rects = Array.from(range.getClientRects()).filter((x) => x.width > 0);
    const last = Math.max(...rects.map((x) => Math.round(x.bottom)));
    const lastText = (() => {
      const words = (el.textContent ?? '').trim().split(/\s+/);
      let n = 0;
      for (let i = words.length - 1; i >= 0; i--) {
        const sub = document.createRange();
        const t = el.firstChild as Text;
        const start = (el.textContent ?? '').lastIndexOf(words[i]);
        sub.setStart(t, start); sub.setEnd(t, start + words[i].length);
        if (Math.round(sub.getBoundingClientRect().bottom) !== last) break;
        n++;
      }
      return n;
    })();
    return { lines: new Set(rects.map((x) => Math.round(x.bottom))).size, wordsOnLast: lastText };
  });
  console.log(`count label @ ${testInfo.project.name}: ${JSON.stringify(r)}`);
  expect(r.lines === 1 || r.wordsOnLast >= 2, `the count label's last line holds ${r.wordsOnLast} word(s)`).toBe(true);
});
