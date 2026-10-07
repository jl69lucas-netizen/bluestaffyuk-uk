// src/lib/manchesterFaq.ts — Manchester's three FAQ blocks (outline rows 7, 12 and 21), as rows a
// FAQ component and the page's FAQPage node read alike (src/lib/cityKit.ts `faqPageNode`).
//
// THE QUESTIONS ARE THE APPROVED OUTLINE'S, word for word: each block is an outline section that
// carries `faq`, its H2 the block's heading and its H3s the questions in order (the page wordings of
// `faq_rewordings`, STOP 2, 2026-10-07). An answer is keyed by its question, so a question that moves
// in the outline (the three thin wordings Task 34 re-proposes at STOP 3) stops the build here until
// its answer is keyed to the new words: never a stale pairing.
//
// THE ANSWERS ARE THE FAQ BANK AND THE DATA (rule 9). Each names its `source`: a data/faq.json row
// read through src/lib/faq.ts `loadFaq` (tokens resolved), used word for word wherever the row
// answers the question as asked, or composed from that row's own words and data/settings.json keys
// read through src/lib/cityKit.ts where it does not. No price, deposit, band, town, test name or puppy
// name is typed here. Never plainly "refundable": the deposit is `deposit_refund_clause`, whole, as a
// clause of the deposit sentence (Phase F ruling 10), and the bank's `{deposit_terms}` rows are not
// used. No em dash in our copy, no result for a DNA test (the tests are named and the certificates are
// shared on request; ledger parents-dna-clear holds no proof of a result).
import outline from '../../data/outlines/blue-staffy-puppies-manchester-uk.json';
import { loadFaq } from './faq';
import { BOY_PRICE, DEPOSIT, DEPOSIT_HOLDS, GIRL_PRICE, PARENT_DNA_TESTS, TOWN, availablePuppies, refundClause } from './cityKit';

export interface CityFaqItem { q: string; a: string; source: string }
export interface CityFaqBlock { key: 'first' | 'health' | 'life'; heading: string; items: CityFaqItem[] }

const BANK = new Map(loadFaq().map((r) => [r.id, r]));
/** A bank row's answer, tokens resolved; a missing row stops the build. */
const bank = (id: string): string => {
  const row = BANK.get(id);
  if (!row) throw new Error(`manchesterFaq: data/faq.json has no row ${id}`);
  return row.a;
};
/** One sentence of a bank answer (0-based), with its full stop. */
const sentence = (id: string, n: number): string => {
  const s = bank(id).split(/(?<=[.!?])\s+(?=[A-Z])/)[n];
  if (!s) throw new Error(`manchesterFaq: data/faq.json ${id} has no sentence ${n + 1}`);
  return s;
};
/** The bank row's words with one phrase replaced; a phrase the row no longer carries stops the build. */
const edit = (text: string, from: string, to: string): string => {
  if (!text.includes(from)) throw new Error(`manchesterFaq: "${from}" is no longer in the bank answer "${text}"`);
  return text.replace(from, to);
};
const lcFirst = (s: string) => s.charAt(0).toLowerCase() + s.slice(1);
const list = (xs: string[]) => (xs.length > 1 ? `${xs.slice(0, -1).join(', ')} and ${xs[xs.length - 1]}` : xs[0] ?? '');

// ── the litter, as the cost answer names it ─────────────────────────────────────────────────────
const pups = availablePuppies();
const names = (sex: 'male' | 'female') => pups.filter((p) => p.sex === sex).map((p) => p.name);
const priced = (sex: 'male' | 'female', price: string, word: string) => {
  const n = names(sex);
  if (!n.length) return null;
  return n.length === 1 ? `${price} for ${n[0]}, our one ${word}` : `${price} for each of our ${word}s, ${list(n)}`;
};
const litterPrices = [priced('male', BOY_PRICE, 'boy'), priced('female', GIRL_PRICE, 'girl')].filter(Boolean).join(', and ');
const [TEST_A, TEST_B] = PARENT_DNA_TESTS;

/** Every answer, keyed by its outline question. */
const ANSWERS: Record<string, { a: string; source: string }> = {
  // ── top (outline row 7) ──
  'How Much Does Each Blue Staffy Puppy Cost?': {
    // listing-cost's first sentence (its second carries `{deposit_terms}`, plainly "refundable"),
    // then the litter's prices by sex from data/price-matrix.json and the names from data/puppies.json.
    a: `${edit(sentence('listing-cost', 0), 'Every puppy is listed with its own price on its card, so', 'Each puppy is listed with its own price, so').replace(/\.$/, '')}: in this litter ${litterPrices}.`,
    source: 'data/faq.json listing-cost; data/price-matrix.json; data/puppies.json',
  },
  'Where Do I Find Blue Staffy Puppies to Buy Near Manchester?': {
    a: `Here. ${sentence('home-find-breeders', 1)}`,
    source: 'data/faq.json home-find-breeders',
  },
  'Can My Blue Staffy Puppy Be Delivered to My Home?': {
    // about-delivery-home's two sentences as one, its "safe and reliable" and "services" left out
    // (a claim beyond the delivery note; answer board q06 is fixing the bank rows that over-reach).
    a: `Yes. ${edit(edit(sentence('about-delivery-home', 0), 'safe and reliable ', ''), ' services.', ',')} so ${lcFirst(
      edit(edit(sentence('about-delivery-home', 1), 'This means wherever you are in the UK, ', 'wherever you are in the UK '), 'new de-wormed Staffy pup', 'de-wormed puppy'))}`,
    source: 'data/faq.json about-delivery-home',
  },
  'Do You Deliver Puppies Across the UK?': {
    // The `delivery` row (delivery_note and the band), then collection in the town (home-safe-delivery:
    // "you can collect in person instead").
    a: `${bank('delivery').replace(/\.$/, '')}, and you can collect your puppy from us in ${TOWN} instead.`,
    source: 'data/faq.json delivery, home-safe-delivery; data/settings.json delivery_note, delivery_min_gbp, delivery_max_gbp, address.city',
  },
  'How Do I Know Which Puppies Are Still Available?': { a: bank('listing-availability'), source: 'data/faq.json listing-availability' },
  'How Much Is Your Deposit?': {
    a: `${DEPOSIT}, which ${DEPOSIT_HOLDS}. It comes off the price, and it is ${refundClause()}.`,
    source: 'data/settings.json deposit_gbp, deposit_refund_clause (the deposit ruling, src/lib/cityKit.ts)',
  },
  // ── middle (outline row 12) ──
  'Are the Parents of Every Blue Staffy Puppy You Breed Health-Tested?': {
    // about-health-tests, its "KC-registered with full pedigrees" in the ledger's words
    // (parents-kc-registered: "Maggie and Jones are both Kennel Club registered").
    a: `Yes. Maggie, our dam, and Jones, our sire, are both Kennel Club registered and fully vaccinated, and both have had DNA tests for ${TEST_A} and ${TEST_B} and eye and elbow screening.`,
    source: 'data/faq.json about-health-tests; data/bsuk-ontology.json (the two test names)',
  },
  'Should I See the Mother With Her Puppy Before Money Changes Hands?': {
    // The answer board's q04 (a), 2026-10-07, as approved, every figure read: the deposit ruling and
    // deposit_refund_clause, then whyus-evidence's last sentence ("You can see both parents …").
    a: `See them together before you commit to a puppy. With us the ${DEPOSIT} deposit comes first: it ${DEPOSIT_HOLDS}, it comes off the price, and it is ${refundClause()}. At the viewing ${edit(
      sentence('whyus-evidence', 3), 'You can see ', 'you see ')}`,
    source: 'answer board 2026-10-07 outline q04 (a); data/settings.json deposit_gbp, deposit_refund_clause; data/faq.json whyus-evidence',
  },
  "Can I Contact You for Advice for the Dog's Whole Life?": {
    a: `Yes. You are welcome to write to us before or after your puppy is home, and ${lcFirst(sentence('home-after-support', 1))}`,
    source: 'data/faq.json home-after-support',
  },
  'How Do I Spot a Bad Staffy Breeder?': {
    // buying-puppy-farm, without "puts the terms in writing" (an unconfirmed promise; Task 25).
    a: edit(edit(bank('buying-puppy-farm'), 'An ethical breeder', 'A good breeder'), ', puts the terms in writing', ''),
    source: 'data/faq.json buying-puppy-farm',
  },
  'Has the Puppy Been Microchipped and Vet Checked?': {
    a: `Yes. Each puppy goes home with ${edit(bank('puppy-package'), 'A comprehensive puppy package: ', '').replace('help them settle', 'help it settle')}`,
    source: 'data/faq.json puppy-package',
  },
  'What Vaccinations, Worming and Flea Treatments Has the Puppy Had?': { a: bank('health-vaccinations'), source: 'data/faq.json health-vaccinations' },
  'Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?': {
    // health-dna-tests' first sentence (the tests and what each is), then the certificates on request
    // (the breeder's rulings, answer board 2026-09-29 q01 and chat 2026-10-05). Never a result.
    a: `${edit(sentence('health-dna-tests', 0), 'Both parents are', 'Maggie and Jones are both').replace(/\.$/, '')}, and we share their certificates on request.`,
    source: 'data/faq.json health-dna-tests; the certificates-on-request ruling',
  },
  // ── bottom (outline row 21) ──
  'Is Blue Staffy Aggressive?': { a: bank('listing-aggressive'), source: 'data/faq.json listing-aggressive' },
  'Do Blue Staffies Suit First-Time Dog Owners?': { a: bank('listing-first-time-owners'), source: 'data/faq.json listing-first-time-owners' },
  'Can a Staffy Be Left Alone for Hours?': { a: bank('listing-left-alone'), source: 'data/faq.json listing-left-alone' },
  'Are Blue Staffies Good Pets?': {
    a: edit(bank('listing-family-dog'), 'Yes — the', 'Yes. The'),
    source: 'data/faq.json listing-family-dog (its dash a full stop)',
  },
  'What Food Is the Puppy Eating Now?': {
    a: 'The high-quality puppy food it has been raised on here, and we provide a starter pack so it can stay on that food at first. Your vet can advise on the long-term diet after that.',
    source: 'data/faq.json health-puppy-diet',
  },
  'Do Blue Staffies Make Good Family Pets for Homes With Children?': { a: bank('home-family-children'), source: 'data/faq.json home-family-children' },
  'Is a Staffordshire Bull Terrier Able to Live in a Flat?': { a: bank('guide-flat-living'), source: 'data/faq.json guide-flat-living' },
};
// The food answer is the bank row's facts in plain words; hold it to them.
for (const w of ['high-quality puppy food', 'raised on', 'starter pack', 'vet']) {
  if (!bank('health-puppy-diet').includes(w)) throw new Error(`manchesterFaq: data/faq.json health-puppy-diet no longer says "${w}"`);
}

type Heading = { level: number; text: string; children?: Heading[] };
const SECTIONS = (outline as unknown as { sections: { faq?: boolean; headings: Heading[] }[] }).sections.filter((s) => s.faq);
const KEYS = ['first', 'health', 'life'] as const;
if (SECTIONS.length !== KEYS.length) throw new Error(`manchesterFaq: the outline has ${SECTIONS.length} FAQ blocks, not ${KEYS.length}`);

/** The three blocks, in page order: the outline's H2 and H3s, each answered from ANSWERS. */
export const MANCHESTER_FAQ: CityFaqBlock[] = SECTIONS.map((sec, i) => {
  const h2 = sec.headings.find((h) => h.level === 2)!;
  return {
    key: KEYS[i],
    heading: h2.text,
    items: (h2.children ?? []).filter((h) => h.level === 3).map((h) => {
      const hit = ANSWERS[h.text];
      if (!hit) throw new Error(`manchesterFaq: no answer keyed to the outline question "${h.text}"`);
      return { q: h.text, ...hit };
    }),
  };
});
