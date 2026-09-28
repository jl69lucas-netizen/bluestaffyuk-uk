// src/lib/cityKit.ts — the facts every city component prints, from the data files, once.
//
// The canvas mockups typed "£1,500", "£200–£350" and "£500 books your viewing" into each
// fragment because a mockup has no data. A kit component may not (working rule 9: never type
// a price by hand), and fifteen components that each spelled the deposit line would be fifteen
// places for the user's deposit ruling to drift. So the lines are built here from
// data/settings.json, data/price-matrix.json and data/puppies.json.
//
// THE DEPOSIT (the user's rulings, 2026-09-27): £500 books the viewing and reserves the puppy,
// and it comes off the price. It is never called plainly "refundable": the refund is partial
// and conditional, and where the condition does not fit, no refund wording is printed at all
// (answer board, deposit wording Q4). So `depositLine` carries no refund clause. When the
// deposit-wording branch adds the refund fields to data/settings.json, `depositRefundClause`
// prints them; until then it is null and nothing is printed.
import settings from '../../data/settings.json';
import prices from '../../data/price-matrix.json';
import puppiesJson from '../../data/puppies.json';
import { gbp, type PuppyRow } from './site';

export const money = (n: number) => `£${gbp(n)}`;

/** The puppies on sale today, in file order (data/puppies.json `status: Available`). */
export const availablePuppies = (): PuppyRow[] =>
  (puppiesJson as PuppyRow[]).filter((p) => p.status === 'Available');

/** Boy or Girl — the canvas's word for `sex`, which the user approved with the picks. */
export const sexWord = (p: PuppyRow) => (p.sex === 'male' ? 'Boy' : 'Girl');

export const BOY_PRICE = money(prices.male_gbp);
export const GIRL_PRICE = money(prices.female_gbp);
export const DEPOSIT = money(settings.deposit_gbp);
export const DELIVERY_BAND = `${money(settings.delivery_min_gbp)}–${money(settings.delivery_max_gbp)}`;
export const TOWN = settings.address.city;

/** rules/puppies.md `delivery-band-on-every-card`, in the pack's canonical words. */
export const deliveryLine = `UK home delivery ${DELIVERY_BAND} by distance · or collect in ${TOWN}`;

/** The deposit, in the user's ruling (2026-09-27). No refund wording: see the header. */
export const depositLine = `${DEPOSIT} books your viewing and reserves your puppy, and it comes off the price.`;

/** The refund clause, printed only when data/settings.json states both refund fields. */
export const depositRefundClause = (): string | null => {
  const s = settings as { deposit_refund_max_pct?: number; deposit_refund_condition?: string };
  return s.deposit_refund_max_pct && s.deposit_refund_condition
    ? `refundable up to ${s.deposit_refund_max_pct}% ${s.deposit_refund_condition}`
    : null;
};

/** The guarantee's length, or null while the breeder has not given one (rule 9). */
export const guaranteeDays = (): number | null => (settings as { guarantee_days: number | null }).guarantee_days;

/** The FAQPage node for a city page's questions: EXACTLY the rows its FAQ blocks render, in
 *  their file wording (the blocks Title Case the visible heading at render, as Faq.astro does). */
export const faqPageNode = (rows: { q: string; a: string }[]) => ({
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: rows.map((r) => ({ '@type': 'Question', name: r.q, acceptedAnswer: { '@type': 'Answer', text: r.a } })),
});
