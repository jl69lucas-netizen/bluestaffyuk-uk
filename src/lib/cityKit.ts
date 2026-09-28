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
// (answer board, deposit wording Q4). So `depositLine` carries no refund clause, and this file
// carries no helper for one: the wording is being settled on the deposit-wording branch, and when
// it lands it will be the data's (data/settings.json), not a component's.
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

/** What the deposit does, in the user's ruling (2026-09-27). No refund wording: see the header. */
const DEPOSIT_DOES = 'books your viewing and reserves your puppy, and it comes off the price';
const sentence = (s: string) => `${s.charAt(0).toUpperCase()}${s.slice(1)}.`;

/** The deposit line: "£500 books your viewing …". */
export const depositLine = `${DEPOSIT} ${DEPOSIT_DOES}.`;
/** The same ruling without the figure, for a row whose label already carries it ("£500 deposit"). */
export const depositBrief = sentence(DEPOSIT_DOES);

/** How a puppy travels, from data/settings.json `delivery_note` ("UK home delivery by
 *  DEFRA-approved transport, priced by distance"): "By DEFRA-approved transport, priced by
 *  distance." A note without its "by …" clause stops the build rather than print a guess. */
export const transportLine = (() => {
  const m = settings.delivery_note.match(/\bby (.+)$/);
  if (!m) throw new Error(`cityKit: data/settings.json delivery_note has no "by …" clause: ${settings.delivery_note}`);
  return sentence(`by ${m[1]}`);
})();

/** The guarantee's length, or null while the breeder has not given one (rule 9). */
export const guaranteeDays = (): number | null => (settings as { guarantee_days: number | null }).guarantee_days;

/** A guarantee row ("<n>-day guarantee" over the breeder's own words), or null. It prints only
 *  when data/settings.json carries BOTH the length (`guarantee_days`) and the wording
 *  (`guarantee_note`): no component writes what a guarantee covers (working rule 9). */
export const guaranteeRow = (): { t: string; d: string } | null => {
  const s = settings as { guarantee_days: number | null; guarantee_note?: string };
  return s.guarantee_days && s.guarantee_note ? { t: `${s.guarantee_days}-day guarantee`, d: s.guarantee_note } : null;
};

/** The FAQPage node for a city page's questions: EXACTLY the rows its FAQ blocks render, in
 *  their file wording (the blocks Title Case the visible heading at render, as Faq.astro does). */
export const faqPageNode = (rows: { q: string; a: string }[]) => ({
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: rows.map((r) => ({ '@type': 'Question', name: r.q, acceptedAnswer: { '@type': 'Answer', text: r.a } })),
});

/** Where an in-body city component sits from a 1024px viewport, for its images' `sizes`, which
 *  can read only the viewport: `column` — beside the city dial, as on every real city page
 *  (src/layouts/CityShell.astro), the default — or `full`, the full-width specimen on
 *  /kit-preview/city/. The component's LAYOUT needs no such word: it is a container and follows
 *  its box; only an image's `sizes` has to be told (the Task 7b review, item 1). */
export type CityFit = 'column' | 'full';

/** The section's box on a city page from 1024px: --container less the shell's two 24px gutters,
 *  --city-dial-w (272px) and the 48px gap — 656px at 1024, 832px at 1280. */
const COLUMN = 'calc(min(100vw, 1200px) - 368px)';
/** The viewport at which that column reaches the desktop tier (a box of 800px). */
const COLUMN_DESKTOP_VW = 800 + 368;

/** A `sizes` list for an image whose painted width is a function of its section's box B at each
 *  tier the city components share — phone below a 640px box, tablet from 640, desktop from 800 —
 *  with B written as the CSS length it is at each viewport for `fit`. */
export function citySizes(fit: CityFit, at: { phone: (B: string) => string; tablet: (B: string) => string; desktop: (B: string) => string }): string {
  const vw = '100vw';
  const list = fit === 'column'
    ? [`(min-width: ${COLUMN_DESKTOP_VW}px) ${at.desktop(COLUMN)}`, `(min-width: 1024px) ${at.tablet(COLUMN)}`,
       `(min-width: 640px) ${at.tablet(vw)}`, at.phone(vw)]
    : [`(min-width: 800px) ${at.desktop(vw)}`, `(min-width: 640px) ${at.tablet(vw)}`, at.phone(vw)];
  return list.join(', ');
}
