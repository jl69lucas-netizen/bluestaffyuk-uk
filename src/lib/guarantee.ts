// src/lib/guarantee.ts — the health guarantee's words, checked once for every page that prints them.
//
// The breeder's answer (answer board q07, 2026-09-29) is two years. It is data: data/settings.json
// `guarantee_days` (the length) and `guarantee_label` (its words). The rebuilt pages read it through
// src/lib/site.ts `guaranteeLabel()`, the city components through src/lib/cityKit.ts
// `guaranteeRow()`; both run the check below, so a label that disagrees with its length, or that
// names a cover the breeder has not given, stops the build of any page that would print it
// (working rule 9). No imports but the number words, so site.ts and cityKit.ts can both use it.
import { numberWord } from './recordText';

export type GuaranteeSettings = { guarantee_days: number | null; guarantee_label?: string; guarantee_note?: string };

/** The length as its label must open: "Two-year" for 730 days, "<n>-day" for a length that is
 *  no whole number of years. */
function lengthWords(days: number): string {
  if (days % 365 !== 0) return `${days}-day`;
  const w = numberWord(days / 365);
  return `${w.charAt(0).toUpperCase()}${w.slice(1)}-year`;
}

/** Words that would name what the guarantee covers. The breeder has not said (rule 9). */
const COVER = /\b(?:cover(?:s|ing|ed|age)?|for|against|hips?|elbows?|eyes?|hereditary|genetic|congenital|conditions?|including|includes)\b/i;

/** The label check: a label opens with its length as whole words ("Two-year" then a space or the
 *  end, so "Two-years of cover" and "Two-year-old promise" are refused), in sentence case, ends at
 *  "guarantee" (nothing after it) and names no cover. Throws with the reason;
 *  tests/py/test_city_kit.py pins each refusal. */
export function checkGuaranteeLabel(days: number, label: string): void {
  const want = lengthWords(days);
  // `want` is letters, digits and a hyphen ("Two-year", "30-day"): nothing to escape.
  if (!new RegExp(`^${want}(?=\\s|$)`).test(label)) {
    throw new Error(`guarantee: data/settings.json guarantee_label "${label}" does not open with its length, "${want}" (guarantee_days ${days})`);
  }
  if (!/\bguarantee$/.test(label) || COVER.test(label)) {
    throw new Error(`guarantee: data/settings.json guarantee_label "${label}" names more than a length: it must end at "guarantee" and name no cover (rule 9)`);
  }
}

/** The label, checked, as a heading's words (`label`) or mid-sentence (`lower`). */
export function guaranteeWords(s: GuaranteeSettings, form: 'label' | 'lower' = 'label'): string {
  if (!s.guarantee_days || !s.guarantee_label) throw new Error('guarantee: data/settings.json has no guarantee_days or guarantee_label');
  checkGuaranteeLabel(s.guarantee_days, s.guarantee_label);
  return form === 'lower' ? s.guarantee_label.charAt(0).toLowerCase() + s.guarantee_label.slice(1) : s.guarantee_label;
}
