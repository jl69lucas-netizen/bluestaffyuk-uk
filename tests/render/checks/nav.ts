import { register, type CheckResult, type Defect } from '../lib/registry.js';
import {
  forceInstantRootScroll,
  measureTopChrome,
  resetScrollInstant,
  waitForScrollSettle,
} from '../lib/probes.js';
import type { Page } from '@playwright/test';

register({
  id: 'nav-anchors-resolve',
  family: 'NAV',
  severity: 'blocking',
  describe: 'every in-page #anchor points at an element that exists',
  minExamined: 2,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]')).filter(
        (a) => (a.getAttribute('href') || '').length > 1,
      );
      const dead: string[] = [];
      for (const a of links) {
        const raw = a.getAttribute('href') as string;
        const id = decodeURIComponent(raw.slice(1));
        const byId = document.getElementById(id);
        const byName = document.querySelector(`[name="${CSS.escape(id)}"]`);
        if (!byId && !byName) dead.push(raw);
      }
      return { examined: links.length, dead: Array.from(new Set(dead)).slice(0, 10) };
    });

    return {
      examined: r.examined,
      defects: r.dead.length
        ? [
            {
              checkId: 'nav-anchors-resolve',
              family: 'NAV' as const,
              viewport,
              count: 1,
              message: `dead in-page anchor(s): ${r.dead.join(', ')}`,
            },
          ]
        : [],
    };
  },
});

/**
 * Names the ONE page-level thing most likely to be producing the landings we measured.
 * Returns null rather than guessing — a wrong root cause is worse than none, because it
 * sends the next person to edit a file that was never the problem.
 *
 * Takes `targets`, `lo` and `hi` FROM THE CALLER rather than re-deriving them. Two
 * separate defects came out of the old self-service version:
 *
 * 1. It rebuilt its own id set from every `a[href^="#"]` with NO box or visibility
 *    filter, while the headline counted the box-filtered `targets`. The scorecards read
 *    "18 of 18 in-page links ... 1 of 19 targets" — two counts over two different
 *    populations printed side by side, which reads as "1 of the 19 failures".
 * 2. It recomputed `chromeH ± 8/60` inline, so the diagnostic's idea of the band could
 *    silently drift from the band that actually DECIDES a failure. One source now.
 *
 * Every branch names the measured quantity — what a target DECLARES — never a landing,
 * because that is what this function inspects. And when both cohorts exist it reports
 * BOTH: naming only the majority silently drops the targets that need the opposite fix,
 * which is a milder form of the misattribution this function was rewritten to remove.
 *
 * It no longer names `html{scroll-behavior:smooth}`. The landings are measured with the
 * root forced to instant scrolling (see forceInstantRootScroll), so the page's smooth
 * scrolling cannot move a measured landing. Before that, the smooth-scroll branch was the
 * cause printed on the 2026-09-13 flake. It was right that the animation mattered and
 * wrong about whose defect it was: the race belonged to the harness, not the page.
 */
async function diagnoseLandingCause(
  page: Page,
  targets: string[],
  lo: number,
  hi: number,
): Promise<string | null> {
  return page.evaluate(
    ({ hrefs, lo, hi }: { hrefs: string[]; lo: number; hi: number }) => {
      let seen = 0;
      let short = 0;
      let long = 0;
      for (const href of hrefs) {
        const el = document.getElementById(decodeURIComponent(href.slice(1)));
        if (!el) continue;
        seen++;
        const smt = parseFloat(getComputedStyle(el).scrollMarginTop || '0');
        if (smt < lo) short++;
        else if (smt > hi) long++;
      }

      const over = `declare scroll-margin-top past the ${hi}px far edge`;
      const under = `declare scroll-margin-top under the ${lo}px near edge`;

      // Every branch requires its own cohort to be NON-EMPTY, so a zero count can never
      // be printed. The old `long > short` form returned "0 of 19 targets overshoot"
      // whenever both were zero — reachable in practice, because the last anchor on a page often cannot
      // reach its offset at the document end and so lands outside the band while every
      // scroll-margin-top on the page is correct.
      if (long && short) {
        return `${long} of ${seen} targets ${over} and ${short} ${under} — the two need opposite fixes`;
      }
      if (long && long === seen) return `all ${seen} targets ${over}`;
      if (short && short === seen) return `all ${seen} targets ${under}`;
      if (long) return `${long} of ${seen} targets ${over}`;
      if (short) return `${short} of ${seen} targets ${under}`;
      return null;
    },
    { hrefs: targets, lo, hi },
  );
}

register({
  id: 'nav-jump-target-lands',
  family: 'NAV',
  severity: 'blocking',
  describe: 'clicking an in-page link must leave its target visible below the sticky chrome',
  minExamined: 2,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const chrome = await measureTopChrome(page);

    if (chrome.implausible) {
      return {
        examined: 0,
        defects: [
          {
            checkId: 'nav-jump-target-lands',
            family: 'NAV' as const,
            viewport,
            count: 1,
            message: `pinned chrome measures ${chrome.height}px, over 40% of the viewport — refusing to judge landings against a number that is probably wrong. Parts: ${JSON.stringify(chrome.parts)}`,
          },
        ],
      };
    }

    // One entry per unique target, and only targets reachable from a link with a
    // real box. 0x0 duplicates and sr-only skip links are not user-facing chips;
    // clicking them via a synthetic pointer event hangs for 30s and then throws.
    const targets: string[] = await page.evaluate(() => {
      const byHref = new Map<string, boolean>();
      for (const a of Array.from(document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]'))) {
        const href = a.getAttribute('href') || '';
        if (href.length < 2) continue;
        if (!document.getElementById(decodeURIComponent(href.slice(1)))) continue;
        const box = a.getBoundingClientRect();
        const cs = getComputedStyle(a);
        if (cs.visibility === 'hidden' || cs.display === 'none') continue;
        if (box.width < 8 || box.height < 8) continue; // 0x0 dupes and sr-only
        byHref.set(href, true);
      }
      return Array.from(byHref.keys());
    });

    const lo = chrome.height - 8;
    const hi = chrome.height + 60;

    // Three buckets, three rows. Never one row per anchor: NAV supplied 81% of the
    // first baseline's headline number by counting granularity alone, which made the
    // family totals incomparable and pointed the next-action list at the wrong family.
    //
    // `unsettled` is partitioned but NOT split into two rows, because the split it
    // encodes is a claim about WHOSE defect it is, not a second failure mode: a target
    // still travelling when the budget expired is probably OUR budget being short,
    // while one that never moved at all is the page's. Both belong in one row that
    // says which is which — splitting them would make "at most 3 rows" a lie the very
    // first time a page produced both.
    const missed: string[] = [];
    const unsettledMoving: string[] = [];
    const unsettledStuck: string[] = [];
    const untestable: string[] = [];

    // Extension budget for a scroll still in flight at the base budget. 5000ms is ~3x the
    // 1494ms Chromium was measured taking for 23,284px, and the cap of 4 keeps the worst
    // case (4 * 5000 = 20s of extension) well inside the 120s this page+viewport gets for
    // ALL of its checks. In practice one target per page has needed it, never four.
    const SETTLE_EXTENSION_MS = 5000;
    const MAX_SETTLE_EXTENSIONS = 4;
    let extensionsUsed = 0;

    // Measure geometry, not animation timing. Every page on this site declares
    // html{scroll-behavior:smooth}, and a smooth fragment scroll can stall mid-flight
    // for longer than the settle probe's equal-read window. That is what produced the
    // one-off `#mt-dallas@7373px` on 2026-09-13. The reasoning and the measurement are
    // in forceInstantRootScroll.
    const instant = await forceInstantRootScroll(page);
    if (!instant.applied) {
      await instant.restore();
      return {
        examined: 0,
        defects: [
          {
            checkId: 'nav-jump-target-lands',
            family: 'NAV' as const,
            viewport,
            count: 1,
            message:
              'the harness could not force scroll-behavior:auto on <html>, so landings would depend on smooth-scroll timing; refusing to measure. This is a harness defect, not a page defect',
          },
        ],
      };
    }

    try {
      for (const href of targets) {
        try {
          await resetScrollInstant(page);

          // Click the first link for this href that has a real box, in the page itself.
          // This triggers the browser's own fragment navigation — the behaviour a user
          // gets — without requiring viewport visibility.
          const clicked = await page.evaluate((h: string) => {
            const links = Array.from(
              document.querySelectorAll<HTMLAnchorElement>(`a[href="${h.replace(/"/g, '\\"')}"]`),
            );
            const el = links.find((a) => {
              const b = a.getBoundingClientRect();
              return b.width >= 8 && b.height >= 8;
            });
            if (!el) return false;
            el.click();
            return true;
          }, href);

          if (!clicked) {
            untestable.push(`${href} (no clickable box)`);
            continue;
          }

          let settle = await waitForScrollSettle(page);

          // A scroll that is STILL MOVING when the budget expires is not evidence of a page
          // defect, and this check's own message says so ("PROBABLY A BUDGET DEFECT, NOT A
          // PAGE DEFECT; raise maxMs before touching the page"). Failing a BLOCKING gate on
          // that verdict is incoherent, and it was measured doing exactly that on 2026-08-02:
          // three consecutive runs of the same commit against the same dist/ failed on three
          // different page/viewport pairs — adoption-cost@375, then timneh@375 and
          // hand-raised@768 — each time one link out of eighteen.
          //
          // So keep waiting instead of guessing. The scroll is already in flight, so a second
          // wait simply continues it; only a target that is STILL unsettled after the
          // extension is reported, which turns "probably the budget" into "definitely not".
          // Bounded twice over — a per-target extension and a per-page cap on how many
          // targets may use one — because pages.spec runs every check for one page+viewport
          // inside a single 120s test, and an unbounded extension would trade false failures
          // for pages that write no partial at all. A page with no partial scores ABSENT,
          // which probes.ts already calls the worst failure mode this harness has.
          if (!settle.settled && settle.lastDeltaPx > 0 && extensionsUsed < MAX_SETTLE_EXTENSIONS) {
            extensionsUsed++;
            settle = await waitForScrollSettle(page, { maxMs: SETTLE_EXTENSION_MS });
          }

          if (!settle.settled) {
            const detail = `${href} (gave up at ${settle.ms}ms, y=${settle.y}, last tick ${settle.lastDeltaPx}px)`;
            if (settle.lastDeltaPx > 0) unsettledMoving.push(detail);
            else unsettledStuck.push(detail);
            continue;
          }

          const top = await page.evaluate((h: string) => {
            const el = document.getElementById(decodeURIComponent(h.slice(1)));
            return el ? Math.round(el.getBoundingClientRect().top) : NaN;
          }, href);

          if (Number.isNaN(top)) {
            untestable.push(`${href} (target vanished after navigation)`);
          } else if (top < lo || top > hi) {
            missed.push(`${href}@${top}px`);
          }
        } catch (err) {
          // A thrown check drops the page from the scorecard silently. Never throw.
          untestable.push(`${href} (${(err as Error).message.split('\n')[0]})`);
        }
      }
    } finally {
      // Restore BEFORE diagnosing and before any later check runs: both must read the
      // page as it ships.
      await instant.restore();
    }

    const defects: Defect[] = [];
    const chromeDesc = `${chrome.height}px = ${chrome.parts.map((p) => `${p.tag}:${p.height}`).join('+')}`;

    if (missed.length) {
      const cause = await diagnoseLandingCause(page, targets, lo, hi);
      defects.push({
        checkId: 'nav-jump-target-lands',
        family: 'NAV' as const,
        viewport,
        count: missed.length,
        message:
          `${missed.length} of ${targets.length} in-page links land outside ${lo}-${hi}px ` +
          `(measured chrome ${chromeDesc})` +
          (cause ? ` — ROOT CAUSE: ${cause}` : ' — no single page-level cause identified') +
          `; first: ${missed.slice(0, 5).join(', ')}`,
      });
    }

    const unsettled = unsettledMoving.length + unsettledStuck.length;
    if (unsettled) {
      defects.push({
        checkId: 'nav-jump-target-lands',
        family: 'NAV' as const,
        viewport,
        count: unsettled,
        message:
          `${unsettled} of ${targets.length} links never stopped scrolling inside the harness's own settle budget` +
          (unsettledMoving.length
            ? ` — ${unsettledMoving.length} were STILL MOVING when it expired, which is PROBABLY A BUDGET DEFECT, NOT A PAGE DEFECT; raise maxMs before touching the page (first: ${unsettledMoving.slice(0, 3).join(', ')})`
            : '') +
          (unsettledStuck.length
            ? ` — ${unsettledStuck.length} never moved at all, so the click produced no scroll, which is a page defect (first: ${unsettledStuck.slice(0, 3).join(', ')})`
            : ''),
      });
    }

    if (untestable.length) {
      defects.push({
        checkId: 'nav-jump-target-lands',
        family: 'NAV' as const,
        viewport,
        count: untestable.length,
        message: `${untestable.length} of ${targets.length} links could not be tested; first: ${untestable.slice(0, 3).join(', ')}`,
      });
    }

    return { examined: targets.length, defects };
  },
});
