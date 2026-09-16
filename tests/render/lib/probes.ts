import type { Page } from '@playwright/test';

/**
 * Scroll the full page in viewport-sized steps so lazy-loaded images fetch,
 * wait for every image to settle, then return to the top.
 * Required before any IMG check — below-fold images are otherwise unloaded.
 */
export async function settlePage(page: Page): Promise<{ pending: number }> {
  // Force every lazy image to fetch BEFORE scrolling.
  //
  // Scrolling alone does not do it: measured on /congo-african-grey-for-sale/,
  // a full-page scroll left 45 of 52 images with complete === false, zero HTTP
  // 4xx, and they stayed unloaded after a further 15 seconds. All 45 were
  // ordinary loading="lazy" images — visible, real widths, not inside <details>.
  // Chromium never commits a lazy load when the viewport passes that fast, and
  // returning to the top drops the pending ones. The consequence was that
  // img-srcset-within-2x examined 7 of 52 images and called the page clean.
  //
  // We measure the assets a page SHIPS, not the order a browser happens to
  // fetch them in, so eager is the honest setting here — and it is
  // deterministic, where the scroll race was not.
  await page.evaluate(() => {
    for (const img of Array.from(document.images)) {
      if (img.getAttribute('loading') === 'lazy') img.setAttribute('loading', 'eager');
    }
  });

  await page.evaluate(async () => {
    const step = window.innerHeight;
    // Re-read scrollHeight each iteration: the document GROWS while settling
    // (measured +611px on the corpus page), so a height cached up front stops
    // the loop short of the real bottom. Iteration cap guards a page that grows
    // faster than we scroll.
    for (let y = 0, i = 0; y < document.body.scrollHeight && i < 400; y += step, i++) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 30));
    }
    window.scrollTo(0, 0);
  });

  // BOUNDED. An image that never loads and never errors fires neither onload nor
  // onerror, so an unbounded Promise.all here hangs until the test timeout —
  // measured on /congo-african-grey-for-sale/, where it stalled both IMG checks
  // past 45s and killed the page's results entirely. A page whose results never
  // get written scores as absent rather than as failed, which is the worst
  // failure mode this harness has. Never let this wait be unbounded.
  const pending = await page.evaluate(async () => {
    const incomplete = Array.from(document.images).filter((i) => !i.complete);
    await Promise.race([
      Promise.all(
        incomplete.map(
          (i) =>
            new Promise((res) => {
              i.onload = i.onerror = () => res(null);
            }),
        ),
      ),
      new Promise((res) => setTimeout(res, 3000)),
    ]);
    return Array.from(document.images).filter((i) => !i.complete).length;
  });

  await page.waitForTimeout(150);
  // Callers may surface this; the IMG checks already report any image that
  // failed to decode, so a stuck image becomes a defect rather than a hang.
  return { pending };
}

export interface TopChrome {
  /** Height in px of the band of pinned chrome at the top of the viewport. */
  height: number;
  /** What was counted, for reports — a bare number hides why it is wrong. */
  parts: { tag: string; cls: string; height: number }[];
  /** True when chrome exceeds 40% of the viewport; the caller should treat this as a defect, not a measurement. */
  implausible: boolean;
}

/**
 * Height of the sticky/fixed chrome band pinned to the top of the viewport
 * (header + any jump rail). Measured, never assumed — one page had five
 * `var(--hdr, 72px)` fallbacks against a header that measures 96px.
 *
 * Two things this gets right that the obvious implementation does not, both
 * found by measuring the congo-pair page rather than by reading its CSS:
 *
 * 1. MUST SCROLL FIRST. A rail with `top: var(--hdr)` is not pinned at
 *    scrollY 0 — measured at rest it sits at top:1030, far down the document.
 *    Measuring without scrolling returns 96 (header only) and misses a 55px
 *    rail, so anchor targets landing *behind the rail* score as correct.
 * 2. MUST ACCUMULATE. Chrome stacks: the header pins at 0, the rail pins at
 *    the header's bottom. A `box.top <= 2` filter sees only the header. The
 *    band is grown iteratively — absorb anything whose top touches the band
 *    so far, and repeat until nothing more is absorbed.
 */
export async function measureTopChrome(page: Page): Promise<TopChrome> {
  // Sample the pinned band at several ABSOLUTE depths and keep the largest.
  //
  // Two defects are fixed by doing it this way, both measured on the live site
  // 2026-08-01 (plan Task 2), and both invisible to the previous single-sample form:
  //
  // 1. ONE SAMPLE AT 1.5 VIEWPORTS IS NOT DEEP ENOUGH. The jump rails on the for-sale
  //    pages sit 1300-2000px down the document, past 1.5 viewports at 375 and 768.
  //    dna-tested and hand-raised measured 96px (header only) while their real chrome
  //    is 147px and 158px — so every landing was judged against a band 51-62px too
  //    high, and two pages were reported as defective when their CSS was correct.
  //    This is the second time this probe has been too shallow: it originally measured
  //    at scrollY 0, and 1.5 viewports was the fix. A fixed offset is the wrong shape.
  //
  // 2. `scrollBy` MADE THE ANSWER DEPEND ON CHECK ORDER. pages.spec shares ONE page
  //    object across every check, so this probe ran from whatever scroll position the
  //    previous check left behind and added 1.5 viewports to it. The same page measured
  //    96 or 158 depending purely on what ran before it, which made the band that judges
  //    every NAV landing non-deterministic across runs. `scrollTo` is absolute, so the
  //    incoming scroll position cannot influence the result.
  //
  // The maximum is the right reducer, not the last or the deepest sample: the band-grow
  // below only admits elements contiguous from the viewport top, so a band of 158 means
  // header AND rail were pinned SIMULTANEOUSLY at that depth. Chrome is "the most that
  // can be pinned at once". Neither a fixed offset nor scroll-to-bottom can find that —
  // at the document end a sticky element whose parent has ended has already un-stuck.
  const depths: number[] = await page.evaluate(() => {
    const vh = window.innerHeight;
    const maxScroll = Math.max(0, document.documentElement.scrollHeight - vh);
    const wanted = [0, 0.75, 1.5, 2.5, 4, 6, 9].map((m) => Math.round(vh * m));
    return Array.from(new Set(wanted.map((y) => Math.min(y, maxScroll)))).sort((a, b) => a - b);
  });

  let result: TopChrome = { height: 0, parts: [], implausible: false };

  for (const y of depths) {
    await page.evaluate((top: number) => {
      // `instant`, never `auto`: in ScrollOptions `auto` MEANS "use the computed style",
      // and this site sets html{scroll-behavior:smooth}. An animated scroll here would
      // have us measuring mid-flight, which is the bug that produced 337 phantom NAV
      // rows on the 2026-07-31 baseline.
      window.scrollTo({ top, behavior: 'instant' as ScrollBehavior });
    }, y);
    await page.waitForTimeout(80);

    const sample = await page.evaluate(() => {
    const candidates: { tag: string; cls: string; top: number; bottom: number }[] = [];
    for (const el of Array.from(document.body.querySelectorAll<HTMLElement>('*'))) {
      const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
      if (cs.visibility === 'hidden' || cs.display === 'none') continue;
      if (parseFloat(cs.opacity) === 0) continue;
      const box = el.getBoundingClientRect();
      if (box.height === 0 || box.width === 0) continue;
      // must actually span the viewport horizontally — excludes off-canvas drawers
      if (box.right <= 0 || box.left >= window.innerWidth) continue;

      // ...and must span MOST of it. Top chrome is a full-width band; a sticky
      // sidebar or sticky card in a content column is not, however close to the
      // viewport top it happens to pin. Without this, vertical adjacency alone pulled
      // aside.availB-rail (287px) and div.dial-card (672px) into the band on
      // hand-raised at 1280, reported "chrome measures 784px", tripped the
      // implausible guard, and left nav-jump-target-lands examining ZERO units on
      // that page-viewport — a strictly worse failure than the too-low band it
      // replaced, because an unjudged page reports no defects rather than wrong ones.
      // 0.8 rather than 1.0: real rails carry container padding and inset borders.
      if (box.width < window.innerWidth * 0.8) continue;
      candidates.push({
        tag: el.tagName.toLowerCase(),
        cls: (el.className || '').toString().trim().split(/\s+/).slice(0, 2).join(' '),
        top: box.top,
        bottom: box.bottom,
      });
    }

    // Grow the band: start at the viewport top, absorb anything touching it, repeat.
    let band = 0;
    const parts: { tag: string; cls: string; height: number }[] = [];
    const used = new Set<number>();
    let grew = true;
    while (grew) {
      grew = false;
      candidates.forEach((c, i) => {
        if (used.has(i)) return;
        if (c.top <= band + 2 && c.bottom > band) {
          parts.push({ tag: c.tag, cls: c.cls, height: Math.round(c.bottom - c.top) });
          band = c.bottom;
          used.add(i);
          grew = true;
        }
      });
    }

    return {
      height: Math.round(band),
      parts,
      implausible: band > window.innerHeight * 0.4,
    };
    });

    if (sample.height > result.height) result = sample;
  }

  // Instant, not `scrollTo(0, 0)`. That plain form is smooth-ANIMATED under the site's
  // global `html{scroll-behavior:smooth}` — the exact shape of the bug removed from
  // nav.ts. It happened to be harmless here only because this animation's destination is
  // also 0, so it was safe by coincidence rather than by design. Left as-is it is the
  // nearest wrong pattern for the next reader to copy, one function above its own fix.
  await resetScrollInstant(page);
  return result;
}

/**
 * Return to the top with NO animation, whatever `scroll-behavior` the page declares.
 *
 * `window.scrollTo(0, 0)` is itself smooth-animated under `html{scroll-behavior:smooth}`,
 * which every page on this site sets. The previous NAV check reset that way and clicked
 * 80ms later — starting a fragment navigation while a full-document smooth scroll was
 * still in flight. `behavior:'instant'` overrides the computed style; `'auto'` does not
 * (in ScrollOptions, 'auto' means "use the computed style", which is the trap).
 */
export async function resetScrollInstant(page: Page): Promise<void> {
  // An instant scroll sets scrollY to 0 SYNCHRONOUSLY but does not CANCEL an animation
  // already in flight. Measured: a smooth scroll toward 20000 interrupted at y=1213 read
  // 0 immediately, then resurrected to 485 one frame later and stayed there. So the wait
  // below is not decoration — it is the window in which a surviving animation reveals
  // itself, and re-asserting afterwards is what stops one slow target from contaminating
  // the next one's landing measurement.
  for (let attempt = 0; attempt < 3; attempt++) {
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior }));
    await page.waitForTimeout(50);
    if ((await page.evaluate(() => window.scrollY)) === 0) return;
  }
}

/**
 * Force `scroll-behavior:auto` on the root for the duration of a measurement, then put
 * back exactly what the page declared.
 *
 * Why waiting cannot fix it: the settle probe calls a scroll settled after five equal
 * reads (160ms). On 2026-09-13, with four browsers competing for the CPU on
 * /african-grey-parrots-for-sale-near-me/ @1280, a smooth fragment scroll was measured
 * stalling mid-flight for 221ms after it had already started (p95 40ms). A stall that
 * long passes the equal-read test, and the 400ms start grace no longer applies once the
 * page has moved. The blocking NAV check then recorded `#mt-dallas@7373px`, about 21px
 * short of its ~7394px document offset, and passed twice on the same dist/. A longer
 * budget only makes that less likely. An instant fragment scroll lands synchronously
 * inside the click, so there is no animation left to race.
 *
 * Detection is unchanged. Where a fragment scroll ends up is set by the target's
 * scroll-margin-top and the chrome above it. Animation only changes when it gets there.
 * JS that asks for `behavior:'smooth'` explicitly still animates, and
 * waitForScrollSettle still covers it.
 *
 * Why an inline `!important` on <html> rather than emulating reduced motion: that media
 * query flips every reduced-motion rule on the page, not just this one, so the check
 * would measure a different page. An inline `!important` outranks any author stylesheet,
 * `!important` rules included.
 *
 * Returns false when the override did not take. The caller must refuse to measure
 * rather than report timing noise as a landing defect.
 */
export async function forceInstantRootScroll(page: Page): Promise<{ applied: boolean; restore: () => Promise<void> }> {
  const prev = await page.evaluate(() => {
    const root = document.documentElement;
    const s = root.style;
    const saved = {
      hadStyleAttr: root.hasAttribute('style'),
      value: s.getPropertyValue('scroll-behavior'),
      priority: s.getPropertyPriority('scroll-behavior'),
    };
    s.setProperty('scroll-behavior', 'auto', 'important');
    return { ...saved, applied: getComputedStyle(root).scrollBehavior === 'auto' };
  });

  const restore = async () => {
    try {
      await page.evaluate((p) => {
        const root = document.documentElement;
        if (p.value) root.style.setProperty('scroll-behavior', p.value, p.priority);
        else root.style.removeProperty('scroll-behavior');
        // Leave no empty `style=""` behind: a later check that reads attributes should
        // see the markup as shipped.
        if (!p.hadStyleAttr && !root.getAttribute('style')) root.removeAttribute('style');
      }, prev);
    } catch {
      // The document went away (a link navigated off-page). The override went with it.
    }
  };

  return { applied: prev.applied, restore };
}

export interface ScrollSettle {
  y: number;
  /** False means it was still moving when the budget ran out — that is a finding, not a landing. */
  settled: boolean;
  ms: number;
  /**
   * Pixels moved over the final tick. Only meaningful when `settled` is false, where it
   * separates "the page never started scrolling" (0, at y=0 — a real page defect) from
   * "the page is still travelling and our budget was too short" (non-zero — OUR defect).
   * Without it both look identical in the scorecard, which is the confusion this whole
   * check was rewritten to remove.
   */
  lastDeltaPx: number;
}

/**
 * Poll until `scrollY` stops changing, or give up and say so.
 *
 * Replaces a fixed 1200ms wait, which is simultaneously too long for an instant jump and
 * too short for a smooth scroll across 26,000px — so it reported false failures on slow
 * pages and wasted 20 minutes per run on fast ones.
 *
 * Polls with setTimeout, not requestAnimationFrame: rAF is throttled to a stop in a page
 * that is not painting, and a probe that silently never ticks reports `settled:false` on a
 * page that is perfectly fine. See MEMORY reference_intersectionobserver_needs_painting_page.
 */
export async function waitForScrollSettle(
  page: Page,
  opts: { maxMs?: number; stableTicks?: number; tickMs?: number; startGraceMs?: number } = {},
): Promise<ScrollSettle> {
  // 3000ms, not 5000. Chromium caps programmatic smooth-scroll DURATION rather than
  // scaling it with distance — measured on this harness's own fixture, 23,284px took
  // 1494ms and 11,984px took 1496ms. 3000 is ~2x the observed worst case, and the ceiling
  // matters because pages.spec runs every check for one page+viewport inside a single
  // 120s test: at 5000ms, 18 targets could spend 90s in NAV alone, blow the test timeout,
  // and write no partial — and a page with no partial scores ABSENT rather than failed,
  // which probes.ts already calls the worst failure mode this harness has.
  // `startGraceMs`: a scroll that has NOT STARTED is indistinguishable from one that has
  // FINISHED, and without this the difference decided a blocking check at random.
  //
  // Measured 2026-08-02 on /african-grey-parrot-adoption-cost/ @375: two runs of the same
  // commit against the same dist/, one clean, one failing `nav-jump-target-lands` with
  // `#reserve@26059px` — the target's raw document offset, i.e. the page had never moved.
  // `el.click()` requests a smooth scroll, but the first animation frame can land later
  // than stableTicks*tickMs (5*32 = 160ms) on a 36,359px document under main-thread load.
  // scrollY then equals its pre-click value for five straight ticks, `stable` reaches the
  // threshold, and the probe reports `settled: true` at y=0 having never moved at all.
  // `lastDeltaPx` stays 0, so the caller's moving-vs-stuck partition cannot tell either.
  //
  // The grace applies ONLY while the position is unchanged from where the click left it,
  // so it costs nothing on the common path (a scroll that starts promptly settles exactly
  // as before) and does not slow a legitimately no-op click beyond the grace itself.
  const { maxMs = 3000, stableTicks = 5, tickMs = 32, startGraceMs = 400 } = opts;
  return page.evaluate(
    ({ maxMs, stableTicks, tickMs, startGraceMs }) =>
      new Promise<{ y: number; settled: boolean; ms: number; lastDeltaPx: number }>((resolve) => {
        const t0 = Date.now();
        const y0 = window.scrollY;
        let last = window.scrollY;
        let stable = 0;
        let lastDeltaPx = 0;
        let everMoved = false;
        const tick = () => {
          const y = window.scrollY;
          if (y === last) stable++;
          else {
            stable = 0;
            everMoved = true;
            lastDeltaPx = Math.abs(y - last);
            last = y;
          }
          const ms = Date.now() - t0;
          // Withhold the "settled" verdict while the page still sits exactly where the
          // click left it and the grace has not expired — that is the un-started case.
          const mayBeUnstarted = !everMoved && y === y0 && ms < startGraceMs;
          if (stable >= stableTicks && !mayBeUnstarted) {
            return resolve({ y, settled: true, ms, lastDeltaPx });
          }
          if (ms >= maxMs) return resolve({ y, settled: false, ms, lastDeltaPx });
          setTimeout(tick, tickMs);
        };
        setTimeout(tick, tickMs);
      }),
    { maxMs, stableTicks, tickMs, startGraceMs },
  );
}
