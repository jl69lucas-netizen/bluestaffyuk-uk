// src/lib/guarantee.ts — the health guarantee's words, checked once for every page that prints them.
//
// The breeder's answer (answer board q07, 2026-09-29) is two years. It is data: data/settings.json
// `guarantee_days` (the length) and `guarantee_label` (its words). The rebuilt pages read it through
// src/lib/site.ts `guaranteeLabel()`, the city components through src/lib/cityKit.ts
// `guaranteeRow()`; both run the check below, so a label that disagrees with its length, or that
// names a cover, stops the build of any page that would print it (working rule 9).
//
// WHAT IT COVERS is the breeder's answer to q02 (2026-09-29), and it is a field of its own,
// `guarantee_cover` ("covers health issues and birth defects for two years from the day your
// puppy comes home"), with its own check below. The label stays a length and nothing else, so a
// heading that prints the label never grows a clause. No imports but the number words, so
// site.ts and cityKit.ts can both use it.
import { numberWord } from './recordText';

export type GuaranteeSettings = { guarantee_days: number | null; guarantee_label?: string; guarantee_note?: string; guarantee_cover?: string };

/** The length as its label must open: "Two-year" for 730 days, "<n>-day" for a length that is
 *  no whole number of years. */
function lengthWords(days: number): string {
  if (days % 365 !== 0) return `${days}-day`;
  const w = numberWord(days / 365);
  return `${w.charAt(0).toUpperCase()}${w.slice(1)}-year`;
}

/** Words that would name what the guarantee covers. The cover has its own field,
 *  `guarantee_cover`, so the LABEL may not carry one (rule 9). */
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

/** The length as a cover clause states it: "for two years" for 730 days, "for one year" for 365,
 *  "for 30 days" for a length that is no whole number of years. */
function coverLength(days: number): string {
  if (days % 365 !== 0) return `for ${days} days`;
  const n = days / 365;
  return `for ${numberWord(n)} ${n === 1 ? 'year' : 'years'}`;
}

/** The cover check (answer board q02, 2026-09-29): a cover is a clause a guarantee sentence
 *  carries ("…, which covers …"), so it opens with "covers ", ends without a full stop, and states
 *  the length `guarantee_days` holds, once, in words ("for two years") and in no other unit.
 *  Throws with the reason; tests/py/test_guarantee_cover.py pins each refusal. */
export function checkGuaranteeCover(days: number, cover: string): void {
  if (!cover || !/^covers\s\S/.test(cover)) {
    throw new Error(`guarantee: data/settings.json guarantee_cover "${cover}" must open with "covers " (a clause a guarantee sentence carries)`);
  }
  if (/[.!?;:,]$/.test(cover.trim())) {
    throw new Error(`guarantee: data/settings.json guarantee_cover "${cover}" ends in punctuation; it is a clause, not a sentence`);
  }
  const want = coverLength(days);
  // Every duration the clause states: a count (digits or a number word) then a unit. "the day your
  // puppy comes home" is a moment, not a duration, and is not counted.
  const units = cover.match(/\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+(?:years?|months?|weeks?|days?)\b/gi) ?? [];
  if (!new RegExp(`\\b${want}\\b`).test(cover) || units.length !== 1) {
    throw new Error(`guarantee: data/settings.json guarantee_cover "${cover}" does not state its length once as "${want}" (guarantee_days ${days})`);
  }
}

/** The cover, checked, as a clause ("covers … comes home"). */
export function guaranteeCoverWords(s: GuaranteeSettings): string {
  if (!s.guarantee_days || !s.guarantee_cover) throw new Error('guarantee: data/settings.json has no guarantee_days or guarantee_cover');
  checkGuaranteeCover(s.guarantee_days, s.guarantee_cover);
  return s.guarantee_cover;
}
