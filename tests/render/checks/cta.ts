import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { register, type CheckContext, type CheckResult, type Family } from '../lib/registry.js';
import { REPO } from '../lib/dupCorpus.js';
import type { Page } from '@playwright/test';

/**
 * CTA: every call to action on a page is its own button (bsuk-cta skill, the breeder's
 * request of 2026-10-08: "no near identical buttons on any page, each gets its own unique
 * buttons and styles"). Three checks share one collector:
 *
 *   cta-text-distinct   no two CTAs on a page say the same thing in near-identical words
 *   cta-style-distinct  no two CTAs on a page share one painted design
 *   cta-count-in-band   the page's body CTAs sit in its page type's band, never in two
 *                       neighbouring sections
 *
 * WHAT A CTA IS, measured rather than named: a visible <a>, <button> or submit inside <main>
 * whose painted background is --color-cta. A class list would miss the next component; the
 * paint is what the reader sees as a button. Nav and [data-cta-exempt] are not CTAs.
 *
 * A REPEATED SET (one CTA per card in a list, e.g. "Ask about Roman" on six puppy cards) is
 * one design used N times by construction, so its members are judged as one CTA: the set's
 * texts differ by the puppy's name and are never twins of each other, and the set counts once.
 *
 * The bands and the near-identical threshold live in data/design/cta-plan.json, read here and
 * by the skill, so the breeder can change a band without touching a check.
 */
interface Plan {
  near_identical: { jaccard: number; stop_words: string[] };
  bands: Record<string, { min: number; max: number }>;
}
let planCache: Plan | null = null;
function plan(): Plan {
  planCache ??= JSON.parse(readFileSync(join(REPO, 'data/design/cta-plan.json'), 'utf8')) as Plan;
  return planCache;
}

export interface Cta {
  text: string;
  kind: 'link' | 'submit' | 'tool';
  section: string;
  top: number;
  sig: string;
  set: string;
}

/** Every CTA on the painted page (see the file comment for what counts). */
export async function collectCtas(page: Page): Promise<Cta[]> {
  return page.evaluate(() => {
    const probe = document.createElement('span');
    probe.style.color = 'var(--color-cta)';
    document.body.appendChild(probe);
    const ctaRgb = getComputedStyle(probe).color;
    probe.remove();
    const main = document.querySelector('main') || document.body;
    const outer = (el: Element | null): Element | null => {
      let s = el ? el.closest('[data-section-label]') : null;
      while (s && s.parentElement?.closest('[data-section-label]')) s = s.parentElement.closest('[data-section-label]');
      return s;
    };
    const tops = Array.from(main.querySelectorAll('[data-section-label]')).filter(
      (s) => !s.parentElement?.closest('[data-section-label]'),
    );
    const out: { text: string; kind: 'link' | 'submit' | 'tool'; section: string; top: number; sig: string; set: string }[] = [];
    main.querySelectorAll<HTMLElement>('a, button, input[type=submit]').forEach((el) => {
      if (!el.getClientRects().length || el.closest('nav, [data-cta-exempt]')) return;
      const cs = getComputedStyle(el);
      if (cs.backgroundColor !== ctaRgb) return;
      const form = el.closest('form');
      const isSubmit = !!form && ((el as HTMLButtonElement).type === 'submit' || el.tagName === 'INPUT');
      const kind = isSubmit ? 'submit' : el.tagName === 'BUTTON' ? 'tool' : 'link';
      const sec = outer(el);
      const pseudo = (p: string) => {
        const c = getComputedStyle(el, p).content;
        return c === 'none' || c === 'normal' ? '' : c;
      };
      const parentW = el.parentElement ? el.parentElement.getBoundingClientRect().width : 0;
      const borderW = parseFloat(cs.borderTopWidth) || 0;
      // What a reader can SEE, coarsened (the bsuk-cta eval, 2026-10-08): a 1px font size, a
      // zero-width border or weight 600 against 700 told three identical gold pills apart.
      // Exact strings would call those three designs; the parts below are compared by
      // sameDesign() with a tolerance instead.
      const sig = JSON.stringify({
        bg: cs.backgroundColor, ink: cs.color,
        radius: parseFloat(cs.borderTopLeftRadius) >= 24 ? 'pill' : `${Math.round(parseFloat(cs.borderTopLeftRadius) || 0)}`,
        border: borderW >= 1 ? `${Math.round(borderW)} ${cs.borderTopStyle} ${cs.borderTopColor}` : '',
        face: cs.fontFamily.split(',')[0].trim(),
        size: parseFloat(cs.fontSize),
        bold: parseInt(cs.fontWeight, 10) >= 600,
        track: parseFloat(cs.letterSpacing) || 0,
        caps: cs.textTransform === 'uppercase',
        dir: cs.flexDirection === 'column' ? 'column' : 'row',
        width: Math.abs(el.getBoundingClientRect().width - parentW) < 1 ? 'full' : 'fit',
        shadow: cs.boxShadow === 'none' ? '' : cs.boxShadow,
        before: pseudo('::before'), after: pseudo('::after'),
        icon: !!el.querySelector('svg, img'),
        parts: el.children.length,
      });
      const item = el.closest('li, article, [data-card]');
      const sibs = item?.parentElement
        ? Array.from(item.parentElement.children).filter((c) => c !== item && c.tagName === item.tagName)
        : [];
      const set = item && sibs.length ? `${item.parentElement!.className || item.tagName}@${sec ? sec.id : ''}` : '';
      out.push({
        text: ((el as HTMLInputElement).value || el.textContent || '').trim().replace(/\s+/g, ' '),
        kind,
        section: sec ? sec.id || sec.getAttribute('data-section-label') || '?' : '(outside a section)',
        top: sec ? tops.indexOf(sec) : -1,
        sig,
        set,
      });
    });
    return out;
  });
}

/** One judged unit per CTA, a repeated set collapsed to its first member. */
function units(ctas: Cta[]): Cta[] {
  const seen = new Set<string>();
  return ctas.filter((c) => {
    if (!c.set) return true;
    if (seen.has(c.set)) return false;
    seen.add(c.set);
    return true;
  });
}

export function contentWords(text: string): string[] {
  const stop = new Set(plan().near_identical.stop_words);
  return [...new Set((text.toLowerCase().match(/[a-z0-9']+/g) ?? []).filter((w) => !stop.has(w)))];
}

export function nearIdentical(a: string, b: string): boolean {
  const x = new Set(contentWords(a));
  const y = new Set(contentWords(b));
  if (!x.size || !y.size) return a.trim().toLowerCase() === b.trim().toLowerCase();
  const inter = [...x].filter((w) => y.has(w)).length;
  return inter / (x.size + y.size - inter) >= plan().near_identical.jaccard;
}

/**
 * Two CTAs a reader sees as one design: every visible part equal, with a 2px tolerance on the
 * font size and half a pixel on the tracking. A colour, the pill against a squared corner, a
 * visible border, the case, an icon, a glyph, a second line or the full width each make a
 * design of its own (src/styles/cta.css).
 */
export function sameDesign(a: string, b: string): boolean {
  const x = JSON.parse(a) as Record<string, unknown>;
  const y = JSON.parse(b) as Record<string, unknown>;
  for (const k of Object.keys(x)) {
    if (k === 'size') { if (Math.abs((x.size as number) - (y.size as number)) > 2) return false; continue; }
    if (k === 'track') { if (Math.abs((x.track as number) - (y.track as number)) > 0.5) return false; continue; }
    if (x[k] !== y[k]) return false;
  }
  return true;
}

const defect = (id: string, family: Family, viewport: number, count: number, message: string) => ({
  checkId: id,
  family,
  viewport,
  count,
  message,
});

register({
  id: 'cta-text-distinct',
  family: 'SEM',
  severity: 'advisory',
  describe: 'no two CTAs on a page carry identical or near-identical text',
  minExamined: 2,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const all = await collectCtas(page);
    const us = units(all);
    const bad: string[] = [];
    for (let i = 0; i < us.length; i++)
      for (let j = i + 1; j < us.length; j++)
        if (nearIdentical(us[i].text, us[j].text))
          bad.push(`"${us[i].text}" (${us[i].section}) ~ "${us[j].text}" (${us[j].section})`);
    return {
      examined: all.length,
      defects: bad.length
        ? [defect('cta-text-distinct', 'SEM', viewport, bad.length,
            `${bad.length} near-identical CTA pair(s): ${bad.slice(0, 3).join(' | ')} — give each its own words (bsuk-cta)`)]
        : [],
    };
  },
});

register({
  id: 'cta-style-distinct',
  family: 'CSS',
  severity: 'advisory',
  describe: 'no two CTAs on a page share one painted design',
  minExamined: 2,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const all = await collectCtas(page);
    const us = units(all);
    const bad: Cta[][] = [];
    for (let i = 0; i < us.length; i++)
      for (let j = i + 1; j < us.length; j++) if (sameDesign(us[i].sig, us[j].sig)) bad.push([us[i], us[j]]);
    return {
      examined: all.length,
      defects: bad.length
        ? [defect('cta-style-distinct', 'CSS', viewport, bad.length,
            `${bad.length} CTA pair(s) a reader sees as one design: ` +
              bad.slice(0, 3).map((g) => g.map((c) => `"${c.text}"`).join(' = ')).join(' | ') +
              ' — give each CTA its own style from the catalog (bsuk-cta)')]
        : [],
    };
  },
});

register({
  id: 'cta-count-in-band',
  family: 'SEM',
  severity: 'advisory',
  describe: "the page's body CTAs sit in its page type's band, never in two neighbouring sections",
  minExamined: 1,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    const band = plan().bands[ctx.pageType];
    if (!band) return { examined: 0, defects: [] };
    const body = units(await collectCtas(page)).filter((c) => c.kind === 'link');
    const problems: string[] = [];
    if (body.length < band.min || body.length > band.max)
      problems.push(`${body.length} body CTA(s), band ${band.min}-${band.max} for ${ctx.pageType}`);
    const placed = body.filter((c) => c.top >= 0).sort((a, b) => a.top - b.top);
    for (let i = 1; i < placed.length; i++)
      if (placed[i].top - placed[i - 1].top <= 1)
        problems.push(`"${placed[i - 1].text}" (${placed[i - 1].section}) and "${placed[i].text}" (${placed[i].section}) are in neighbouring sections`);
    return {
      examined: 1,
      defects: problems.length
        ? [defect('cta-count-in-band', 'SEM', viewport, problems.length, `${problems.join(' | ')} (data/design/cta-plan.json)`)]
        : [],
    };
  },
});
