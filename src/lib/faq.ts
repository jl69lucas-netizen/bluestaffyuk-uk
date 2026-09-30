// src/lib/faq.ts — the FAQ rows, with the money and the delivery wording interpolated from
// data/settings.json at load.
//
// Two reasons the answers are data rather than component copy. Rule 9: every row names in
// `source` the thing that backs it — a page path when the claim is page copy, or
// `data/settings.json` when the answer IS the setting — and tests/py/test_faq_data.py
// fails if that file has stopped saying it. And a price lives in exactly one place, so a
// deposit change is a data edit that reaches the FAQ, the counter strip and the schema
// together instead of leaving a stale number in prose nobody greps.
import settings from '../../data/settings.json';
import rows from '../../data/faq.json';

export interface FaqRow {
  id: string;
  q: string;
  /** May contain any TOKEN below in braces; loadFaq() resolves them. */
  a: string;
  /** The page path or data file that backs this answer. */
  source: string;
}

/** The only substitutions an answer may ask for. An unknown `{token}` is left alone and
 *  will show up in the rendered answer, which is the loudest way to report the typo. */
const TOKENS: Record<string, string> = {
  deposit_gbp: String(settings.deposit_gbp),
  delivery_min_gbp: String(settings.delivery_min_gbp),
  delivery_max_gbp: String(settings.delivery_max_gbp),
  delivery_note: settings.delivery_note,
  // Derived, not raw: the deposit's terms are a boolean in settings and a word in prose,
  // and spelling the word in the JSON would let the two drift apart silently.
  deposit_terms: settings.deposit_refundable ? 'refundable' : 'non-refundable',
};

export function loadFaq(): FaqRow[] {
  return (rows as FaqRow[]).map((r) => ({
    ...r,
    a: r.a.replace(/\{([a-z_]+)\}/g, (whole, key: string) => TOKENS[key] ?? whole),
  }));
}
