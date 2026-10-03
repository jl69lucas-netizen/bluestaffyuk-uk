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
import { checkGuaranteeLabel, guaranteeRowParts, type GuaranteeSettings } from './guarantee';

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

/** THE GUARANTEE (the breeder's answers, answer board q07 and q02, 2026-09-29): data/settings.json
 *  `guarantee_days`, `guarantee_label`, `guarantee_cover` and `guarantee_note`, checked by
 *  src/lib/guarantee.ts. No component types it. */
const G = settings as unknown as GuaranteeSettings;
export { checkGuaranteeLabel };

/** The guarantee's length in days, or null while the breeder has not given one (rule 9). */
export const guaranteeDays = (): number | null => G.guarantee_days;

/** A guarantee row ({ t: its label, d: what it covers, then its note }), or null when the
 *  length, the label or the note is missing; a missing cover only leaves the cover sentence out
 *  (src/lib/guarantee.ts guaranteeRowParts). No component writes what a guarantee is or covers
 *  (working rule 9). */
export const guaranteeRow = (): { t: string; d: string } | null => guaranteeRowParts(G);

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

/** THE TIERS — one pair of edges for type AND layout, on the section's own box (the Task 7b
 *  quality review, I4): phone `width < 640px`, tablet `640px <= width < 800px`, desktop
 *  `width >= 800px`. src/styles/city.css mirrors these in its comment and its type-scale queries;
 *  every city component's container queries use them; tests/py/test_city_kit.py holds them equal. */
export const TIER = { tablet: 640, desktop: 800 } as const;

/** The city page's geometry, each mirroring a CSS value (tests/py/test_city_kit.py holds them
 *  equal): the dial's column (--city-dial-w, src/styles/city.css), PageShell's own-dial grid
 *  gutter (var(--space-5)) and gap (var(--space-8)), the site's --container (global.css), and the
 *  viewport the dial takes its column at (PageShell, CityDialPhotoMarker). */
export const DIAL_W = 272;
export const SHELL_GUTTER = 24;
export const DIAL_GAP = 48;
export const CONTAINER = 1200;
export const DIAL_FROM = 1024;
/** Everything the column gives up beside the dial: 2 gutters, the dial and the gap (368px). */
const BESIDE = 2 * SHELL_GUTTER + DIAL_W + DIAL_GAP;

/** The section's box on a city page from DIAL_FROM: 656px at 1024, 832px at 1280. */
const COLUMN = `calc(min(100vw, ${CONTAINER}px) - ${BESIDE}px)`;
/** The viewport at which that column reaches the desktop tier. */
const COLUMN_DESKTOP_VW = TIER.desktop + BESIDE;

/** A `sizes` list for an image whose painted width is a function of its section's box B at each
 *  tier the city components share — phone below a 640px box, tablet from 640, desktop from 800 —
 *  with B written as the CSS length it is at each viewport for `fit`. */
export function citySizes(fit: CityFit, at: { phone: (B: string) => string; tablet: (B: string) => string; desktop: (B: string) => string }): string {
  const vw = '100vw';
  const list = fit === 'column'
    ? [`(min-width: ${COLUMN_DESKTOP_VW}px) ${at.desktop(COLUMN)}`, `(min-width: ${DIAL_FROM}px) ${at.tablet(COLUMN)}`,
       `(min-width: ${TIER.tablet}px) ${at.tablet(vw)}`, at.phone(vw)]
    : [`(min-width: ${TIER.desktop}px) ${at.desktop(vw)}`, `(min-width: ${TIER.tablet}px) ${at.tablet(vw)}`, at.phone(vw)];
  return list.join(', ');
}

/** The `sizes` of CityChapters' full-width images (the photo under the H2, a wide chapter's
 *  infographic) and of anything in a wide chapter's text: the tray less its padding, at most 760px.
 *  The box less 64px on a phone (a 16px inset and 16px padding a side) and less 128px from a 640px
 *  box (32px and 32px), since the tray took its siblings' side inset (frontend-design D7,
 *  2026-10-03): 311 / 640 / 528 / 704px at 375 / 768 / 1024 / 1280 (it was 319 / 680 / 568 / 744 at a
 *  12px inset). The harden pass's first `- 120px` under-asked by 32px, so a 720w candidate would
 *  have painted upscaled. */
export function chapterWideSizes(fit: CityFit = 'column'): string {
  return citySizes(fit, {
    phone: (B) => `calc(min(${B}, 1132px) - 64px)`,
    tablet: (B) => `min(760px, calc(min(${B}, 1164px) - 128px))`,
    desktop: (B) => `min(760px, calc(min(${B}, 1164px) - 128px))`,
  });
}

/** The `sizes` of a photograph in a CityChapters chapter's TEXT (a slot's own image under an H4),
 *  mirroring CityChapters.astro's grid: the tray less its padding on a phone, and from a 640px box
 *  the chapter's full width, at most the uniform box's 760px, because the prose runs UNDER the
 *  heading-and-photo row there (impeccable D1, 2026-10-03; it was the 1.3fr of 2.3fr, then the
 *  9fr of 21fr, of a three-column chapter). Without it BodyImage's uniform default (100vw to 800px,
 *  then 760px) served a 760-1024px file into a narrower box. */
export function chapterTextSizes(fit: CityFit = 'column'): string {
  return citySizes(fit, {
    phone: (B) => `calc(min(${B}, 1132px) - 64px)`,
    tablet: (B) => `min(760px, calc(min(${B}, 1164px) - 128px))`,
    desktop: (B) => `min(760px, calc(min(${B}, 1164px) - 128px))`,
  });
}

/** Words a full stop ends without ending the sentence (lower-cased, without the stop). */
const ABBREVIATIONS = new Set(['mr', 'mrs', 'ms', 'dr', 'st', 'mt', 'no', 'vs', 'etc', 'e.g', 'i.e']);

/** A review, split into paragraphs at its sentence breaks for reading (the Task 7b spec review;
 *  M1 of the quality review). Its words and their order are the quote's exactly: the paragraphs
 *  rejoined with single spaces ARE the quote. A break is a `.`, `!` or `?` (after any closing quote
 *  or ellipsis) followed by a space and a capital, digit or opening quote — never after an
 *  abbreviation (Mr., Dr., St., vs. …), and never inside a figure (£1.5k has no space). Sentences
 *  are joined greedily while a paragraph stays within `maxChars`; a single sentence longer than
 *  that stays whole, never cut (the type-fit check then reports it, and the break is the page's
 *  author's to find). */
export function splitReview(quote: string, maxChars: number): string[] {
  const sentences: string[] = [];
  const brk = /[.!?]["”’']?\s+(?=[A-Z0-9“"‘'])/g;
  let from = 0;
  for (let m = brk.exec(quote); m; m = brk.exec(quote)) {
    const upTo = m.index + m[0].trimEnd().length;
    const lastWord = quote.slice(from, upTo).split(/\s+/).pop() ?? '';
    if (ABBREVIATIONS.has(lastWord.replace(/[.!?]["”’']?$/, '').toLowerCase())) continue;
    sentences.push(quote.slice(from, upTo));
    from = m.index + m[0].length;
  }
  sentences.push(quote.slice(from));
  return sentences.reduce<string[]>((out, sentence) => {
    const last = out[out.length - 1];
    if (last !== undefined && last.length + 1 + sentence.length <= maxChars) out[out.length - 1] = `${last} ${sentence}`;
    else out.push(sentence);
    return out;
  }, []);
}

/** The most stops CityJumpStepper holds: every stop sits on ONE line at 375px with no sideways
 *  scroll, and past ten they overlap (the Task 7b review). */
export const MAX_STOPS = 10;

/** CityJumpStepper's build-time guard, as a function so its behaviour is testable
 *  (tests/py/test_city_kit.py): too many sections is a page-plan problem, stopped at build time
 *  as the takeaways and the trust ledger stop theirs, and every section needs its question and
 *  icon. Returns the sections unchanged. */
export function stepperStops<S extends { id: string; question?: string; icon?: string }>(sections: S[]): S[] {
  if (sections.length > MAX_STOPS) {
    throw new Error(`CityJumpStepper: ${sections.length} sections; the stepper holds ${MAX_STOPS} stops on a phone`);
  }
  const missing = sections.filter((s) => !s.question || !s.icon).map((s) => s.id);
  if (missing.length) {
    throw new Error(`CityJumpStepper: sections ${missing.join(', ')} need a question and an icon (src/lib/sections.ts)`);
  }
  return sections;
}
