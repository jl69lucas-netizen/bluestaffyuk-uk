import { register, type CheckResult } from '../lib/registry.js';
import type { Page } from '@playwright/test';

/**
 * The SEM family: the four heading/structure rules that have lived in CLAUDE.md since
 * 2026-07-23 with no backing test. Each one was written after the breeder caught the
 * defect by hand — skipped levels, pages shipping 1 H6, sentence-case headings, and
 * headers with no opening paragraph — which is exactly the class of rule the learning
 * loop says must become a test or become a deletion candidate.
 *
 * All four scope to `<main>` when the page has one. Site chrome is not the page outline:
 * the footer carries four H3s on every page of this site, and counting them would let a
 * page with no H3 of its own pass `sem-all-six-levels` on furniture alone, while telling
 * the operator nothing about the page they are building. Where `<main>` is absent the
 * checks fall back to `<body>` rather than examining zero units, because a check that
 * silently examines nothing is the failure mode this harness exists to prevent.
 */

/** Serialized once into the page context by every check below that needs the heading list. */
const HEADING_SEL = 'h1, h2, h3, h4, h5, h6';

register({
  id: 'sem-heading-order',
  family: 'SEM',
  // Promoted 2026-08-02. Zero rows across all 15 corpus pages having examined 2,993
  // headings — the SAME denominator as sem-all-six-levels and sem-title-case-headings,
  // which fire 6 and 18 rows off it. That shared denominator is the evidence: a check
  // reporting zero from a population its siblings find defects in is clean, not silent.
  severity: 'blocking',
  describe: 'headings descend one level at a time — H2→H4 and H3→H6 are defects',
  minExamined: 6,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate((sel) => {
      const root = document.querySelector('main') || document.body;
      const heads = Array.from(root.querySelectorAll<HTMLElement>(sel)).filter(
        (h) => h.getClientRects().length > 0 && getComputedStyle(h).visibility !== 'hidden',
      );
      let examined = 0;
      let prev = 0;
      const bad: string[] = [];
      for (const h of heads) {
        examined++;
        const lvl = Number(h.tagName[1]);
        // Stepping back UP any distance is legal — that is how a new section starts.
        // Only a downward jump of more than one level is the axe defect
        // "Heading elements are not in a sequentially-descending order".
        if (prev && lvl > prev + 1) {
          bad.push(`H${prev}→H${lvl} at "${(h.textContent || '').trim().slice(0, 40)}"`);
        }
        prev = lvl;
      }
      return { examined, bad: bad.slice(0, 6), count: bad.length };
    }, HEADING_SEL);

    return {
      examined: r.examined,
      defects: r.count
        ? [
            {
              checkId: 'sem-heading-order',
              family: 'SEM' as const,
              viewport,
              count: r.count,
              message: `${r.count} skipped heading level(s): ${r.bad.join(' | ')}`,
            },
          ]
        : [],
    };
  },
});

register({
  id: 'sem-all-six-levels',
  family: 'SEM',
  severity: 'advisory',
  describe: 'every page carries all six heading levels, with at least 5 H5 and 5 H6',
  minExamined: 6,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate((sel) => {
      const root = document.querySelector('main') || document.body;
      const heads = Array.from(root.querySelectorAll<HTMLElement>(sel)).filter(
        (h) => h.getClientRects().length > 0 && getComputedStyle(h).visibility !== 'hidden',
      );
      const n = [0, 0, 0, 0, 0, 0, 0];
      for (const h of heads) n[Number(h.tagName[1])]++;
      return { examined: heads.length, n };
    }, HEADING_SEL);

    const missing = [1, 2, 3, 4, 5, 6].filter((l) => r.n[l] === 0);
    const short = ([5, 6] as const).filter((l) => r.n[l] > 0 && r.n[l] < 5);
    const defects = [];
    if (missing.length) {
      defects.push({
        checkId: 'sem-all-six-levels',
        family: 'SEM' as const,
        viewport,
        count: missing.length,
        message: `heading level(s) absent: ${missing.map((l) => `H${l}`).join(', ')} — inventory ${r.n
          .slice(1)
          .map((c, i) => `H${i + 1}:${c}`)
          .join(' ')}`,
      });
    }
    if (short.length) {
      defects.push({
        checkId: 'sem-all-six-levels',
        family: 'SEM' as const,
        viewport,
        count: short.reduce((s, l) => s + (5 - r.n[l]), 0),
        message: `below the 5-per-level floor: ${short.map((l) => `H${l}=${r.n[l]}`).join(', ')}`,
      });
    }
    return { examined: r.examined, defects };
  },
});

register({
  id: 'sem-title-case-headings',
  family: 'SEM',
  severity: 'advisory',
  describe: 'every H1–H6 is AP-style Title Case',
  minExamined: 5,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate((sel) => {
      // Ported from scripts/page_hardening_scan.py::check_title_case rather than
      // rewritten, because that caser has already been tuned against this site's real
      // headings: acronyms (C.A.Gs, CITES, PCR), prices, hyphenated compounds, and the
      // binomial genus/epithet pair (`Psittacus erithacus`), where capitalising the
      // epithet would BE the defect. A fresh implementation would rediscover each of
      // those as a false positive on a live page instead of on a fixture.
      //
      // FAQ questions live in <summary>, which is not a heading tag, so they are
      // exempt by construction — the selector never sees them. That is the intended
      // scope (CLAUDE.md: "Scope is HEADINGS ONLY"), not an oversight.
      const MINOR = new Set([
        'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
        'at', 'by', 'in', 'of', 'on', 'to', 'as', 'vs', 'per', 'via',
      ]);
      const GENERA = new Set(['Psittacus', 'Ara', 'Amazona', 'Cacatua', 'Eclectus', 'Poicephalus']);
      const core = (w: string) => w.replace(/[^\w'-]/g, '');

      const root = document.querySelector('main') || document.body;
      const heads = Array.from(root.querySelectorAll<HTMLElement>(sel)).filter(
        (h) => h.getClientRects().length > 0 && getComputedStyle(h).visibility !== 'hidden',
      );
      let examined = 0;
      const bad: string[] = [];
      for (const h of heads) {
        const text = (h.textContent || '').replace(/\s+/g, ' ').trim();
        if (!text) continue;
        examined++;
        const words = text.split(' ');
        let force = true; // first word, and any word after : ? !
        for (let i = 0; i < words.length; i++) {
          const w = words[i];
          const c = core(w);
          const prev = i ? core(words[i - 1]) : '';
          if (GENERA.has(prev) && c === c.toLowerCase() && c !== '') {
            force = /[:?!]$/.test(w);
            continue;
          }
          // acronyms, brands, domains, numbers, prices, camelCase
          if (!c || /^\d/.test(c) || w.includes('.') || c === c.toUpperCase() || /[a-z][A-Z]/.test(c)) {
            force = /[:?!]$/.test(w);
            continue;
          }
          const mustCap = force || i === 0 || i === words.length - 1 || !MINOR.has(c.toLowerCase());
          if (mustCap && c[0] === c[0].toLowerCase() && c[0] !== c[0].toUpperCase()) {
            bad.push(`${h.tagName} "${w}" in "${text.slice(0, 46)}"`);
            break;
          }
          force = /[:?!]$/.test(w);
        }
      }
      return { examined, bad: bad.slice(0, 8), count: bad.length };
    }, HEADING_SEL);

    return {
      examined: r.examined,
      defects: r.count
        ? [
            {
              checkId: 'sem-title-case-headings',
              family: 'SEM' as const,
              viewport,
              count: r.count,
              message: `${r.count} heading(s) not in Title Case: ${r.bad.join(' | ')}`,
            },
          ]
        : [],
    };
  },
});

register({
  id: 'sem-section-opening-paragraph',
  family: 'SEM',
  severity: 'advisory',
  describe: 'a heading is followed by prose, never straight into the next heading',
  minExamined: 3,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const root = document.querySelector('main') || document.body;
      const all = Array.from(root.querySelectorAll<HTMLElement>('*'));

      // ONE pass, precomputed. The first version tested visibility inside the inner
      // forward-scan, so every heading re-tested every following element and each test
      // called getClientRects(), which flushes layout. On a 96-heading page with a few
      // thousand elements that is O(n^2) forced reflows: the check did not merely run
      // slowly, it HUNG the page run past its timeout, and a hung check makes a page
      // score ABSENT rather than fail — the worst outcome this harness has.
      //
      // An element "carries text" only if it has its OWN text node. Testing textContent
      // would make every wrapping <div> the first text-bearing element after a heading
      // and the check would never see anything else.
      const visible: boolean[] = [];
      const carries: boolean[] = [];
      const owner: (Element | null)[] = [];
      for (let i = 0; i < all.length; i++) {
        const el = all[i];
        const v = el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
        visible[i] = v;
        carries[i] =
          v &&
          Array.from(el.childNodes).some(
            (n) => n.nodeType === 3 && (n.textContent || '').trim().length > 0,
          );
        owner[i] = carries[i] ? el.closest('h1, h2, h3, h4, h5, h6') : null;
      }

      let examined = 0;
      const bad: string[] = [];
      for (let i = 0; i < all.length; i++) {
        const h = all[i];
        if (!/^H[1-6]$/.test(h.tagName)) continue;
        if (!visible[i] || !(h.textContent || '').trim()) continue;

        // Walk forward in document order to the next element bearing its own visible
        // text, skipping the heading's own descendants. `contains` is cheap and does not
        // touch layout; everything expensive was precomputed above.
        let nextIdx = -1;
        for (let j = i + 1; j < all.length; j++) {
          if (!carries[j]) continue;
          if (h.contains(all[j])) continue;
          nextIdx = j;
          break;
        }
        if (nextIdx < 0) continue; // the last heading on the page has nothing to judge
        examined++;

        // The defect is deliberately NARROW: heading immediately followed by another
        // heading. A heading followed by a <ul> is NOT flagged, because on this site
        // that is a bird card (name, then the spec list) and a hero (H1, then the trust
        // badge row) — both correct. Measured before choosing the predicate: the wider
        // "must be a <p>" form fired 9 times on available/roys and 9 on
        // congo-vs-timneh, and every one of those was a card, not a missing paragraph.
        const nextOwner = owner[nextIdx];
        if (nextOwner) {
          bad.push(
            `${h.tagName}→${nextOwner.tagName} "${(h.textContent || '').trim().slice(0, 40)}"`,
          );
        }
      }
      return { examined, bad: bad.slice(0, 8), count: bad.length };
    });

    return {
      examined: r.examined,
      defects: r.count
        ? [
            {
              checkId: 'sem-section-opening-paragraph',
              family: 'SEM' as const,
              viewport,
              count: r.count,
              message: `${r.count} heading(s) with no opening paragraph: ${r.bad.join(' | ')}`,
            },
          ]
        : [],
    };
  },
});

register({
  id: 'sem-statement-label-visible',
  family: 'SEM',
  severity: 'advisory',
  describe: 'every .stmt-label (Fact / Observed here / Our recommendation) is painted, with a data-kind',
  // `examined` is the number of labels the page carries. A page with none reports 0 and
  // is nothing-to-check, the same convention schema-sold-not-instock uses on pages out of
  // its scope — NOT a padded 1, which would be the examined-inflation the registry
  // comment forbids. minExamined binds only on the fixtures (meta.spec.ts); pages.spec.ts
  // never compares against it. Until a targets.json page ships a label, this check
  // examines 0 across the whole corpus and build_scorecard.mjs Guard 2 will name it.
  minExamined: 2,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      const labels = Array.from(document.querySelectorAll<HTMLElement>('main .stmt-label'));
      const bad: string[] = [];
      for (const l of labels) {
        const rect = l.getBoundingClientRect();
        const cs = getComputedStyle(l);
        const painted =
          rect.width > 0 && rect.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none';
        const kind = l.dataset.kind || '';
        if (!painted) bad.push(`hidden: "${l.textContent?.trim()}"`);
        else if (!['fact', 'observed', 'recommendation'].includes(kind)) bad.push(`bad data-kind "${kind}"`);
      }
      return { examined: labels.length, bad };
    });
    return {
      examined: r.examined,
      defects: r.bad.length
        ? [
            {
              checkId: 'sem-statement-label-visible',
              family: 'SEM' as const,
              viewport,
              count: r.bad.length,
              message: r.bad.join(' | '),
            },
          ]
        : [],
    };
  },
});
