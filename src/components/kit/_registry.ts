// src/components/kit/_registry.ts — the one place a page learns what a kit component is
// and how to demo it. It was written for the design canvas; Task 19 deleted that route and
// kept this file, because src/pages/kit-preview/ renders exactly the same way — walk
// data/design/components.json, look each id up here, render one copy per fixture — and
// scripts/build_design_canvas.py turns that page's built sections into the artboards.
// Nothing that reads it has a per-component branch.
//
// KIT CONVENTIONS — every component in this folder follows all ten.
//  1. No second `<main>`: BaseLayout already renders one, so a kit component and a page
//     that mounts one use `<div>`/`<section>`, never `<main>`.
//  2. Focus rings read `var(--kit-ring)`, never a fixed focus token: --color-focus is
//     steel-700, the same colour as the inverse surface, so a fixed ring vanishes on dark bands.
//  3. Colour comes from `currentColor` or a context variable with a default. A component that
//     can sit on both the bone surface and a dark band never hard-codes `--color-brand`.
//  4. `Props` extends `HTMLAttributes<'tag'>`, spreads `...rest` onto the root element, and
//     applies `class` with `class:list` — so no bare `class=""` or trailing space is emitted.
//  5. Multi-region components take content through named slots; size, mode and data come
//     through props.
//  6. Scoped `<style>` rules that a caller should be able to override live in
//     `@layer components { … }`, so a passed Tailwind utility wins over them.
//  7. Register the component here with demo fixtures; the preview renders one copy per fixture.
//  8. Add a dist assertion for it in tests/py/test_design_components.py.
//  9. A primitive needed by a SECOND component (card shell, medal, rule) moves to
//     src/styles/kit.css rather than being copied into another scoped style block.
//     That file exists as of Task 9 and holds `.kit-card`, `.kit-card--lift` and
//     `.kit-chip`; global.css imports it. Reach for a class from there before writing a
//     second copy of a shell into a scoped block.
// 10. A POSITIONAL check — one that judges an element against its previous sibling, its
//     offset from the chrome, or its place in the scroll — is INERT on a preview page: every
//     demo is the first child of its own section, so `previousElementSibling` is null and
//     the check examines zero and passes vacuously. Cover those with a fixture pair in
//     tests/render/fixtures/, and give the demo a `wrap` only to make the section LOOK
//     right for the eye reading it.
//
// Brass (--color-cta) is a FILL with --color-cta-ink text or an accent on a dark band. It is
// never the colour of small text on a light surface: it is 2.1:1 there.
import type { AstroComponentFactory } from 'astro/runtime/server/index.js';
import puppies from '../../../data/puppies.json';
import settings from '../../../data/settings.json';
import prices from '../../../data/price-matrix.json';
import Button from './Button.astro';
import SectionDivider from './SectionDivider.astro';
import SiteHeaderKit from './SiteHeaderKit.astro';
import PuppyCard from './PuppyCard.astro';
import Hero from './Hero.astro';
import { SITE, type PuppyRow } from '../../lib/site';
// The hero specimen's photograph. Named here, by the specimen, since Hero no longer falls back
// to it: the same master the component defaulted to, so the specimen renders what it always did.
import heroSpecimen from '../../assets/puppies/Cheryl1.jpeg';
import TrustStrip from './TrustStrip.astro';
import CounterStrip from './CounterStrip.astro';
import InfoCard from './InfoCard.astro';
import Testimonial from './Testimonial.astro';
import Faq from './Faq.astro';
import ContactFormKit from './ContactFormKit.astro';
import PageNav from './PageNav.astro';
import SiteFooterKit from './SiteFooterKit.astro';
import PageDial from './PageDial.astro';
import SectionSheet from './SectionSheet.astro';
import SectionStrip from './SectionStrip.astro';
import DataTable from './DataTable.astro';
import VideoEmbed from './VideoEmbed.astro';
import CityHeroFilmstrip from './CityHeroFilmstrip.astro';
import CityPriceScale from './CityPriceScale.astro';
import CityTrustLedger from './CityTrustLedger.astro';
import CityContentsPhotoIndex from './CityContentsPhotoIndex.astro';
import CityDialPhotoMarker from './CityDialPhotoMarker.astro';
import CityJumpStepper from './CityJumpStepper.astro';
import CityTakeawaysLedger from './CityTakeawaysLedger.astro';
import CityPuppySheet from './CityPuppySheet.astro';
import CityRoster from './CityRoster.astro';
import CityVideoPanel from './CityVideoPanel.astro';
import CityChapters from './CityChapters.astro';
import CityLetter from './CityLetter.astro';
import CityFaqLedger, { type CityFaqRow } from './CityFaqLedger.astro';
import CityNewsletterNotice from './CityNewsletterNotice.astro';
import CityContactLineup from './CityContactLineup.astro';
import CitySignedByline from './CitySignedByline.astro';
import CityTicketStrip from './CityTicketStrip.astro';
import CityLookListenChecklist from './CityLookListenChecklist.astro';
import CityPlacesByPublisher from './CityPlacesByPublisher.astro';
import CityMapFacade from './CityMapFacade.astro';
import CityFeatureAndThree from './CityFeatureAndThree.astro';
import CityRangeSheet from './CityRangeSheet.astro';
import CityPuppyFolder from './CityPuppyFolder.astro';
import CityIconRows from './CityIconRows.astro';
import CityNumeralRail from './CityNumeralRail.astro';
import CityQuestionBar from './CityQuestionBar.astro';
import CityTickCard from './CityTickCard.astro';
import CityPhotoShelf from './CityPhotoShelf.astro';
import CityOffsetSheet from './CityOffsetSheet.astro';
import componentsJson from '../../../data/design/components.json';
import locationRows from '../../../data/locations.json';
import { placeGroups, type PlaceRow } from '../../lib/cityPlaces';
import londonPlaces from '../../../data/city-places/blue-staffy-puppies-london.json';
import londonBoard from '../../../data/boards/blue-staffy-puppies-london.json';
import manchesterOutline from '../../../data/outlines/blue-staffy-puppies-manchester-uk.json';
import { BOY_PRICE, GIRL_PRICE, DELIVERY_BAND, DEPOSIT, TOWN, availablePuppies, deliveryLine, depositLine, depositTerms, guaranteeRow, pickAvailable } from '../../lib/cityKit';
import { numberWord } from '../../lib/recordText';
/** The guarantee, from data/settings.json (answer board q07, 2026-09-29); null if the data loses it. */
const GUARANTEE = guaranteeRow();
import type { CityIcon, SectionRef } from '../../lib/sections';

/** The counter specimen's availability figure, counted the way every page counts it. */
const availableNow = (puppies as PuppyRow[]).filter((p) => p.status === 'Available').length;

export type ComponentId =
  | 'site-header' | 'hero' | 'buttons' | 'puppy-card' | 'trust-strip' | 'counter-strip'
  | 'info-card' | 'testimonial' | 'faq' | 'contact-form' | 'page-nav' | 'footer'
  | 'section-divider' | 'page-dial' | 'section-sheet' | 'section-strip' | 'data-table'
  | 'video-embed'
  // The city components (project 5): each city page's picks from its component design pass,
  // previewed on /kit-preview/city/ — never on /kit-preview/, because the city nav set is a
  // page singleton like the kit's. data/design/components.json rows with `"project": 5`.
  | 'city-hero-filmstrip' | 'city-price-scale' | 'city-trust-ledger' | 'city-contents-photo-index' | 'city-dial-photo-marker'
  | 'city-jump-stepper' | 'city-takeaways-ledger' | 'city-puppy-sheet' | 'city-roster' | 'city-video-panel'
  | 'city-chapters' | 'city-letter' | 'city-faq-ledger' | 'city-newsletter-notice' | 'city-contact-lineup'
  // The pieces inside a city section (a board's `subcomponents`): London's board revision of
  // 2026-10-03 (answer board 2026-10-03-london-board-revision q01-q04).
  | 'city-signed-byline' | 'city-ticket-strip' | 'city-look-listen-checklist' | 'city-places-by-publisher'
  // And the London map (answer board 2026-10-06-london-map q01-q02).
  | 'city-map-facade'
  // Manchester's own picks (the Manchester page run, Phase F Tasks 28-31), previewed on
  // /kit-preview/city-manchester/ and never on London's /kit-preview/city/.
  | 'city-feature-and-three' | 'city-range-sheet' | 'city-puppy-folder'
  | 'city-icon-rows' | 'city-numeral-rail' | 'city-question-bar'
  | 'city-tick-card' | 'city-photo-shelf' | 'city-offset-sheet';

export interface KitEntry {
  C: AstroComponentFactory;
  /** One rendering per fixture, inside one section. Omitted means a single bare copy. */
  demo?: Record<string, unknown>[];
  /** Extra chrome the preview wraps the demo in, for components that need a context to be
   *  judged BY EYE. It never makes a positional check work — see convention 10.
   *
   *  Three members, and every one of them is set by an entry below. There is still no
   *  `'inverse'`: the kit has no component that has to be judged on a dark band of the
   *  preview's making — the footer paints its own and the drawer panel is inside the header —
   *  and a branch in the preview page nobody can reach reads as a feature rather than as
   *  dead code. Add it back the day an entry needs it.
   *
   *  `'with-targets'` is the one member that is not purely cosmetic: the two in-page nav
   *  components link to section ids, and without real elements behind those ids the demo
   *  would ship dead anchors on a page the harness judges as a target. It DECLARES that
   *  dependency; the preview renders the stub sections ONCE for the whole page, because
   *  both entries name the same six ids and a copy per demo box would be a duplicate of
   *  every one of them. It supplies the ANCHORS, not positional coverage. */
  wrap?: 'sticky' | 'after-band' | 'with-targets';
}

/** The row in data/design/components.json, typed so a typo in an id fails the build. */
export interface ComponentRow {
  id: ComponentId;
  file: string;
  title: string;
  board_width: 640 | 1280;
  /** Which project added the component. The canvas, the picks board and the variant prune
   *  are records of project 3's closed five-option pick process and filter to `3`; the
   *  kit preview, this registry and the Design System artifact carry every row. */
  project: 3 | 4 | 5;
  /** A piece inside a city section rather than a section of its own: the board record's
   *  `subcomponents[].id` it builds (London's board revision, 2026-10-03). Not a canvas pick. */
  subcomponent?: string;
  /** The canvas pick the row builds (`<city>/<component>/<variant>`), and the root selector the
   *  side-by-side shoots (the Manchester page run, gap G10). London's rows are back-filled in
   *  Phase F Task 32; until then a row without it is London's (`cityOf`). */
  canvas_variant?: string;
  root_selector?: string;
}

/** The city a city row was built for: its `canvas_variant`'s city, or London for a row that
 *  predates the field. Each city's preview route renders its own rows only. */
export const cityOf = (row: ComponentRow): string => row.canvas_variant?.split('/')[0] ?? 'london';

/** The six sections the dial and the sheet both demo. One list, not two: the pair is one
 *  component split by viewport width, and two drifting fixtures would let the board show a
 *  dial and a sheet that disagree about what a page's sections are. The ids are rendered as
 *  stub `<section>`s once per page by the preview (see its `with-targets` note), so every
 *  link resolves and no id is rendered twice. */
export const DEMO_SECTIONS = [
  { id: 'd-a', label: 'Health' },
  { id: 'd-b', label: 'Delivery' },
  { id: 'd-c', label: 'Deposit' },
  { id: 'd-d', label: 'Puppies' },
  { id: 'd-e', label: 'FAQ' },
  { id: 'd-f', label: 'Contact' },
];

/** Every id, no exceptions — a `Partial` here would let a component be dropped from the kit
 *  by deleting its entry, and the preview would simply render one section fewer while every
 *  test that walks components.json went on passing. `Record` makes that a type error. */
/** The data table's demo rows, built from data rather than typed: `data/puppies.json` for
 *  the litter and `data/price-matrix.json` for the deposit every puppy carries. Four of the
 *  six, in file order, so the specimen shows both a £1,500 row and a £1,700 one. */
const money = (n: number) => `£${n.toLocaleString('en-GB')}`;
const PRICE_ROWS: (string | number)[][] = (puppies as { name: string; sex: string; price_gbp: number }[])
  .slice(0, 4)
  .map((p) => [p.name, p.sex === 'male' ? 'Male' : 'Female', money(p.price_gbp), money(prices.deposit_gbp)]);

/** The litter's counts in words, from the data ("six", "three"), for specimen copy. */
const WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve'];
const inWords = (n: number) => WORDS[n] ?? String(n);
const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const LITTER = inWords(availablePuppies().length);
const BOYS = inWords(availablePuppies().filter((p) => p.sex === 'male').length);
const GIRLS = inWords(availablePuppies().filter((p) => p.sex === 'female').length);
/** The city nav set's demo sections: the city preview's OWN section anchors
 *  (`kit-<component id>`, which /kit-preview/city/ gives every section it renders), so every
 *  link resolves and the scroll-spy has real sections to observe — no stub block is needed. One
 *  list for all three nav components, for the reason DEMO_SECTIONS gives. Specimen wording: it
 *  names no city. */
export const CITY_DEMO_SECTIONS: SectionRef[] = [
  { id: 'kit-city-hero-filmstrip', label: 'Puppies', question: 'Where Can I Find a Blue Staffy Puppy Near Me?', icon: 'puppies' },
  { id: 'kit-city-price-scale', label: 'Prices', question: 'What Does Each Part of Buying a Puppy Cost?', icon: 'prices' },
  { id: 'kit-city-trust-ledger', label: 'Checks', question: 'What Should You Check Before Buying?', icon: 'health' },
  { id: 'kit-city-contents-photo-index', label: 'Contents', question: 'Which Part of Buying a Puppy Do You Need First?', icon: 'list' },
  { id: 'kit-city-dial-photo-marker', label: 'Dial', question: 'Where Are You on the Page?', icon: 'home' },
  { id: 'kit-city-jump-stepper', label: 'Jump', question: 'How Do You Jump to a Section on a Phone?', icon: 'faq' },
  { id: 'kit-city-takeaways-ledger', label: 'In short', question: 'What Should a Buyer Take From This Page?', icon: 'deposit' },
  { id: 'kit-city-puppy-sheet', label: `The ${LITTER}`, question: 'Which Puppy Will You Ask About First?', icon: 'delivery' },
];

/** The FAQ specimen's eighteen rows, in three blocks of six (the user's ruling for a city page:
 *  three blocks, 15 to 20 questions). Every answer is a fact the data files or the breeder's
 *  confirmed answers back (2026-09-27): the prices, the six by name, the deposit ruling, the
 *  delivery band and collection, Maggie and Jones, the two DNA tests, eye and elbow screening
 *  with no score, the vet, the take-back terms, Puppy Culture and ENS, and the breed facts
 *  data/faq.json already carries. The guarantee is the rail's, from data/settings.json; no licence, no
 *  refund clause, no age. The figures and names are read from the data, never typed. */
const pupsBySex = (sex: 'male' | 'female') => {
  const names = availablePuppies().filter((p) => p.sex === sex).map((p) => `${p.name} (${p.colour.toLowerCase()})`);
  return names.length > 1 ? `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}` : names.join('');
};
const FAQ_BUY: CityFaqRow[] = [
  { q: 'How much does one of your blue Staffy puppies cost?', a: `${BOY_PRICE} for each of our boys and ${GIRL_PRICE} for each of our girls, and the price is the same wherever in the UK you live.` },
  { q: 'Which puppies can I ask about right now?', a: `Every one on our list: ${pupsBySex('male')} are the boys, and ${pupsBySex('female')} are the girls.` },
  { q: 'What does the deposit do?', a: depositLine },
  { q: 'Do you deliver a puppy to my door?', a: `Yes. We use DEFRA-approved transport anywhere in the UK, and delivery costs ${DELIVERY_BAND}, priced by distance.` },
  { q: 'Can I collect my puppy myself?', a: `Yes. You are welcome to collect your puppy from us in ${TOWN} instead of paying for delivery.` },
  { q: 'How do I reserve a puppy?', a: `Send us the enquiry form with the name of the puppy you like. We reply by email, and the ${DEPOSIT} deposit then books your viewing and holds that puppy for you.` },
];
const FAQ_TRUST: CityFaqRow[] = [
  { q: 'Who are the parents of your puppies?', a: 'Maggie is our dam and Jones is our sire. Both are our own dogs.' },
  { q: 'Which DNA tests have Maggie and Jones had?', a: 'Both are DNA tested for L-2-HGA and HC-HSF4. Each condition is recessive, so it takes a copy of the gene from the dam and another from the sire for a puppy to be affected.' },
  { q: 'Are the parents screened for eye and elbow problems?', a: 'Yes. Both are screened for hereditary cataracts and other inherited eye diseases, and their elbows are screened as well. We quote no score or grade; our health page sets out what each check covers.' },
  { q: 'Can I speak to your vet before I decide?', a: 'Yes. You are welcome to contact our vet about the parents and the litter before you commit to anything.' },
  { q: 'What happens if I can no longer keep my puppy?', a: 'We take the puppy back, and we do the same if a fault is ours; both are set out in our written contract. Tell us as soon as you know and we will talk it through with you.' },
  { q: 'What has a puppy had before it comes home?', a: 'A veterinary health check, its first vaccination, a microchip, and worming and flea treatment, all written on a vet-signed health card that travels with it.' },
];
const FAQ_LIFE: CityFaqRow[] = [
  { q: 'How are your puppies raised?', a: 'In our home, not in a kennel, on Puppy Culture with early neurological stimulation (ENS), and among the everyday sounds of a family house.' },
  { q: 'Can a Staffy live happily in a flat?', a: 'Yes, given its daily exercise and something to think about. The breed is medium-sized and people-focused, so regular walks matter more than a big garden.' },
  { q: 'How much exercise does a Staffy need each day?', a: 'At least an hour of vigorous exercise, ideally split into two outings, plus play or training that works the mind as well as the legs.' },
  { q: 'Can a Staffy be left alone while I am at work?', a: 'Not for long stretches. Staffies want company, so a puppy is built up to short spells alone a little at a time.' },
  { q: 'Is a Staffy a good first dog?', a: 'Yes, for a household ready to socialise the puppy early and train it consistently with rewards. Staffies are eager to please but strong-willed, and they need company.' },
  { q: 'How long does a Staffordshire Bull Terrier live?', a: 'Twelve to fourteen years is the figure the Staffordshire Bull Terrier Club gives for a healthy, well-cared-for dog.' },
];

/** Manchester's city name, from data/locations.json, and the four puppies its hero shows (the
 *  picked canvas variant's, feature first; src/lib/cityKit.ts pickAvailable passes over a sold one). */
const MANCHESTER = (locationRows as { slug: string; city: string }[]).find((r) => r.slug === manchesterOutline.slug)!.city;
const MANCHESTER_HERO_PUPS = pickAvailable(['Roman', 'Cheryl', 'Ince', 'Vennie'], 4).map((p) => p.name);

/** The questions Manchester's nav set lists: every H2 of its approved outline, word for word, in
 *  page order (thirteen; data/outlines/, approved at STOP 2). */
const MANCHESTER_H2: string[] = (manchesterOutline as { sections: { headings: { level: number; text: string }[] }[] }).sections
  .flatMap((sec) => sec.headings.filter((h) => h.level === 2).map((h) => h.text));
/** The short name (the dial and the bar's readout), the contents row's fuller name and its icon for
 *  each of those thirteen sections, in the same order: the picked canvas variants' own words
 *  (design/city-canvas/manchester/{contents-list/b,desktop-dial/a,jump-links/b}.html). The page
 *  (Phase F Task 32) gives each its section's anchor; the preview gives each one of its own. */
export const MANCHESTER_NAV: { label: string; row: string; icon: CityIcon }[] = [
  { label: 'Asked first', row: 'First questions answered', icon: 'faq' },
  { label: 'Deposit and visit', row: 'The deposit and your visit', icon: 'deposit' },
  { label: 'Parents\' tests', row: "The parents' health tests", icon: 'health' },
  { label: 'The litter', row: 'The litter and its prices', icon: 'puppies' },
  { label: 'Health and viewing', row: 'Health and viewing questions', icon: 'faq' },
  { label: 'Travel', row: `Travel to Greater ${MANCHESTER}`, icon: 'delivery' },
  { label: 'Papers', row: 'Papers that come home', icon: 'papers' },
  { label: 'Health and guarantee', row: 'Health and the guarantee', icon: 'guarantee' },
  { label: 'Busy household', row: 'Life in a busy home', icon: 'home' },
  { label: 'Favourite person', row: 'One person or the whole family', icon: 'family' },
  { label: 'Coat comes last', row: 'Why the coat comes last', icon: 'coat' },
  { label: 'Everyday life', row: 'Everyday questions', icon: 'faq' },
  { label: 'Ask about a puppy', row: 'Ask about a puppy', icon: 'enquire' },
];
if (MANCHESTER_NAV.length !== MANCHESTER_H2.length) {
  throw new Error(`_registry.ts: MANCHESTER_NAV names ${MANCHESTER_NAV.length} sections; the outline has ${MANCHESTER_H2.length} H2s`);
}
/** The nav set's demo sections on /kit-preview/city-manchester/: the preview's OWN Manchester
 *  anchors (`kit-<component id>`, in file order, so every link resolves and the spy has real
 *  sections to observe), each carrying the outline's question and the canvas's names in order. The
 *  list grows as Tasks 30-31 add rows, up to the outline's thirteen. */
const MANCHESTER_DEMO_SECTIONS: SectionRef[] = (componentsJson as ComponentRow[])
  .filter((r) => r.project === 5 && cityOf(r) === 'manchester')
  .slice(0, MANCHESTER_H2.length)
  .map((r, i) => ({ id: `kit-${r.id}`, question: MANCHESTER_H2[i], ...MANCHESTER_NAV[i] }));
/** The question bar's small decorative puppy: Christa while she is available (pickAvailable). */
const MANCHESTER_BAR_PUP = pickAvailable(['Christa'], 1)[0].card_photo;

/** Manchester's in-body specimens (Task 30), each in the outline's own words. The family photo
 *  the old site served for Manchester heads the takeaways (its first use: the served alt) and the
 *  deposit section (a repeat: its own alt, working rule 11, 2026-09-29). The table sits under the
 *  outline's H4 with its caption; every face in it was painted above by the hero or the counter
 *  (the counter shows the whole litter), so each row's photo is a repeat. */
const MANCHESTER_FAMILY = 'victoria-family-blue-staffy-manchester.webp';
type OutlineHeading = { level: number; text: string; children?: OutlineHeading[] };
const MANCHESTER_SECTIONS = (manchesterOutline as unknown as {
  sections: { headings: OutlineHeading[]; table?: { under: string; caption: string } }[];
}).sections;
const MANCHESTER_TABLE = MANCHESTER_SECTIONS.find((s) => s.table)!.table!;
/** The outline's "H4 <heading>": the level and the words the table sits under. */
const MANCHESTER_TABLE_UNDER = /^H([2-4]) (.+)$/.exec(MANCHESTER_TABLE.under)!;
const MANCHESTER_DEPOSIT_H2 = MANCHESTER_H2.find((h) => /\bDeposit\b/.test(h))!;

export const REGISTRY: Record<ComponentId, KitEntry> = {
  // `wrap: 'sticky'` — the header is position: sticky, so on a preview page it needs a
  // positioned box with room in it; without one the bar docks to the page's own scroll
  // container and the artboard captures a collapsed strip. The preview additionally makes
  // this one copy `position: static` (see its own style block): a page has one set of top
  // chrome, and a second sticky site header is measured as part of it by the render
  // harness's chrome probe, which no `scroll-margin-top` can then satisfy at every width.
  'site-header': { C: SiteHeaderKit, wrap: 'sticky' },
  // `as: 'h2'` — the preview page already owns an <h1>. The prop exists for exactly this:
  // on a real page the default 'h1' is correct.
  // The chips and the CTA row are PROPS now and default to none (project 4, 2026-09-20
  // review): a component may not assert a page's credentials or invent its links. The board
  // is where those weights are judged, so the specimen passes the set the homepage carries.
  // The eyebrow, the headline and the lede are PROPS with no default now (the 2026-09-20
  // review's last hiding place: a component that defaults to "KC registered · Carlisle" is a
  // component asserting a page's credentials for it). The specimen therefore states its own,
  // which is the honest arrangement — a board specimen shows what a caller passes, and every
  // figure in these three is in data/settings.json.
  hero: {
    C: Hero,
    demo: [{
      as: 'h2',
      eyebrow: `KC registered · ${SITE.location_label}`,
      title: 'Blue Staffy puppies raised in a family home',
      lede: `Health-tested parents, Kennel Club paperwork, UK delivery from £${SITE.delivery_min_gbp}.`,
      chips: ['KC registered', 'DNA-tested parents', 'Raised in the home'],
      image: heroSpecimen,
      imageAlt: 'A blue Staffordshire Bull Terrier puppy resting in a family home',
      ctas: [
        { label: 'Meet the puppies', href: '/available-puppies/' },
        { label: 'Ask a question', href: '/uk-blue-staffy-breeders-contact/', kind: 'outline' },
      ],
      // THE SPECIMEN STATES ITS OWN BOX, because it is not inside `PageShell`. Every real page
      // mounts the hero in the shell, which reserves the dial a 196px column at 1024 and above,
      // and `Hero`'s own `sizes` is measured there — 315px at 1024, 408px at 1280. This board
      // has the full width, so the same hero paints 419px and 503px and the component's default
      // would under-promise by 23%: a soft photograph on the one page whose job is showing what
      // the component looks like. Measured at 375, 768, 900, 901, 1024, 1100, 1199, 1280 and
      // 1600; `img-sizes-matches-box` reads it back against the box at each viewport.
      imageSizes: '(max-width: 900px) calc(100vw - 96px), (max-width: 1199px) calc(47.5vw - 68px), 503px',
    }],
  },
  // All five button KINDS on one board, because a page uses more than one of them and the
  // board is where their weights are judged against each other.
  buttons: {
    C: Button,
    demo: [
      { kind: 'primary', label: 'Meet the puppies', href: '/available-puppies/' },
      { kind: 'outline', label: 'Ask a question', href: '/uk-blue-staffy-breeders-contact/' },
      { kind: 'inverse', label: 'Meet the puppies', href: '/available-puppies/' },
      { kind: 'text', label: 'Read the guide', href: '/uk-staffordshire-bull-terrier-guide/' },
      { kind: 'submit', label: 'Send enquiry', type: 'submit' },
    ],
  },
  // Two pups, not one: the price/status chips differ between them, so a board that showed
  // only Roman would hide how the row wraps behind a longer colour name.
  'puppy-card': { C: PuppyCard, demo: [{ slug: 'roman' }, { slug: 'christa' }] },
  'trust-strip': { C: TrustStrip },
  // `wrap: 'after-band'` paints a steel band above the strip so the seam is judgeable BY
  // EYE — a strip floating on bone shows nothing to be separated from. It does NOT make
  // `layout-hero-counter-separation` judge the preview: convention 10. The real coverage is
  // the fixture pair
  // tests/render/fixtures/{known_good/kit-counter-separated,known_broken/kit-counter-flush}.html,
  // which pins the shipped component's own resolved geometry.
  // THE SPECIMEN STATES ITS OWN FIGURES, because the component no longer has any. The three it
  // used to fall back to, derived the same way from the same two files, so the board shows the
  // same strip: the available count, the deposit and its terms, and the delivery band.
  'counter-strip': {
    C: CounterStrip,
    wrap: 'after-band',
    demo: [{
      stats: [
        { n: String(availableNow),
          label: availableNow === 1 ? 'puppy available now' : 'puppies available now',
          source: 'data/puppies.json#count(status=Available)' },
        { n: `£${settings.deposit_gbp}`,
          label: settings.deposit_refundable ? 'refundable deposit' : 'deposit',
          source: 'data/settings.json#deposit_gbp' },
        { n: `£${settings.delivery_min_gbp}–£${settings.delivery_max_gbp}`,
          label: 'UK delivery by distance',
          source: 'data/settings.json#delivery_min_gbp|data/settings.json#delivery_max_gbp' },
      ],
    }],
  },
  // Two fixtures, not one: the card's statement label is the deferred
  // sem-statement-label-visible check's only subject in the kit, and a board showing a
  // single `fact` label would hide whether the other kinds paint at all.
  'info-card': {
    C: InfoCard,
    demo: [
      {},
      {
        kind: 'recommendation',
        heading: 'Ask to see the paperwork',
        body: 'Every puppy leaves with a comprehensive puppy package: the first vaccination, a microchip, a full veterinary health check and the relevant paperwork.',
      },
    ],
  },
  // The quotes are data — the component reads data/reviews.json so that a new review is a
  // data edit. What the two fixtures demo is the API: `mode` (spec §11 amendment 3e).
  // `single` is one review given room, `grid` is the multi-review strip. Both are on the
  // board, so the eye judges the two together rather than one of them.
  testimonial: { C: Testimonial, demo: [{ mode: 'single' }, { mode: 'grid' }] },
  // No demo props: the three answers are the component's own defaults, and two of the
  // three are read out of data/settings.json so a price change never becomes a copy edit.
  faq: { C: Faq },
  // No demo props: the six controls, the honeypot and the two hidden fields are the form
  // CONTRACT, not a fixture, and the puppy options are read from data/puppies.json. The
  // preview route is named in form_contract_audit.py's NON_CONTENT_ROUTES, so this copy is
  // audited for endpoint and method but not as a reachable enquiry form.
  'contact-form': { C: ContactFormKit },
  // The four sections are DEMO DATA and live here, not in the component: PageNav defaults
  // to no sections and renders the breadcrumb alone, because the component has no way of
  // knowing what a page's sections are. The path and title are the guide page's own, so
  // crumbs() produces the trail a real page would show.
  // THE IDS MUST RESOLVE ON THE PAGE THAT MOUNTS THIS. `nav-anchors-resolve` is BLOCKING,
  // and a demo pointing at #temperament on a page with no such element is a dead in-page
  // anchor like any other — the preview does not get a pass for being a preview. So the
  // four demo sections name kit-preview's own `kit-<component-id>` section anchors, which
  // that page gives every section it renders. A real page passes its real sections.
  'page-nav': {
    C: PageNav,
    demo: [{
      sections: [
        { id: 'kit-hero', label: 'Hero' },
        { id: 'kit-puppy-card', label: 'Puppy Card' },
        { id: 'kit-faq', label: 'FAQ' },
        { id: 'kit-footer', label: 'Footer' },
      ],
    }],
  },
  // No demo props: every link and contact row is NAV and data/settings.json. `wrap` would
  // be wrong here — the footer paints its own dark band and is full-bleed by nature.
  footer: { C: SiteFooterKit },
  'section-divider': { C: SectionDivider },
  // `wrap: 'with-targets'` — the dial IS a scroll-spy over six section ids, so a demo with
  // no such elements is a dial whose every link is a dead anchor (`nav-anchors-resolve`,
  // blocking) and whose observer has nothing to observe. The wrap declares that dependency;
  // the preview renders the six stub sections once for the page. That is a CONTEXT for the
  // eye and for the anchors; it is still not coverage for a positional check (convention 10).
  //
  // The ids are the demo's own `d-a`…`d-f`, prefixed so they cannot collide with the
  // preview's `kit-<component-id>` section anchors that the PageNav demo points at.
  'page-dial': {
    C: PageDial,
    demo: [{ sections: DEMO_SECTIONS }],
    wrap: 'with-targets',
  },
  // The same six sections and the same wrap, for the same two reasons: the sheet's links
  // must resolve, and its scroll-spy must have something to observe — and because BOTH
  // entries name DEMO_SECTIONS, the preview renders those stubs once rather than once per
  // box, or `d-a`…`d-f` would each appear twice on the page. The bar is
  // `position: fixed`, so on the preview it docks to the viewport rather than to this
  // section — which is exactly how it behaves on a real page, and what makes the preview
  // a fair place to look at it.
  'section-sheet': {
    C: SectionSheet,
    demo: [{ sections: DEMO_SECTIONS }],
    wrap: 'with-targets',
  },
  // The third member of the in-page nav set, and the same six sections for the same two
  // reasons as the pair above: its links must resolve, and its scroll-spy must have
  // something to observe. Because all THREE entries name DEMO_SECTIONS, the preview renders
  // those stubs once for the page, not three times.
  //
  // `chrome: false`, like the specimen site header's `position: static` in the preview's own
  // stylesheet, and for the same reason. A demo box is `position: relative` and a few hundred
  // pixels tall, so the strip has nothing to pin to — but it was still publishing its height
  // as the offset every anchor on `/kit-preview/` had to clear, which put all eleven targets
  // 77px below a band measured off 75px of real chrome. The prop says out loud what the
  // preview is showing: a picture of the component, not this page's top chrome.
  'section-strip': {
    C: SectionStrip,
    demo: [{ sections: DEMO_SECTIONS, chrome: false }],
    wrap: 'with-targets',
  },
  // Component 17, the data table (working rule 13; spec §9 amendment 5). THE NUMBERS ARE
  // DATA: the four rows are data/puppies.json and the price column is `price_gbp`, which is
  // data/price-matrix.json's male/female pair per puppy — rule 9 forbids a specimen from
  // typing a price by hand, and a demo that did would be the one place in the repo where a
  // price could drift. Four rows of a six-puppy litter, because the board width is 640 and
  // the question the eye is asked here is what a row looks like, not how long the list is.
  //
  // The deposit column is one figure repeated, and that is the point: it is per puppy, not
  // per litter, and a table that showed it once in a caption would read as the other way.
  //
  // Only ONE fixture, unlike the multi-state entries above: the three board arrangements
  // are a `chrome` CLASS axis (src/lib/boardStyles.ts), so they exist on
  // /board-preview/<slug>/ and not here. What this copy demos is the component's own
  // default — S1, ruled rows under a brand header band — and its stacking, which is the
  // half of the component that is not a choice.
  'data-table': {
    C: DataTable,
    demo: [{
      caption: 'This litter — price and deposit',
      columns: ['Puppy', 'Sex', 'Price', 'Deposit'],
      rows: PRICE_ROWS,
      numeric: [2, 3],
    }],
  },
  // Component 18, the video embed (working rule 14; spec §9 amendment 7). THE ID IS DATA:
  // it is the first entry of `data/settings.json`'s `youtube_embeds`, which is the list of
  // videos the old site already carries — rule 9 forbids a specimen from inventing one, and
  // an invented eleven-character id is a 404 nobody would notice on a hidden preview.
  //
  // ONE fixture, and it is the DEFAULT `play` mode — the click-to-play facade, which is
  // what a rebuilt page mounts. The two eager arrangements are the `play` and `frame` axes
  // of src/lib/boardStyles.ts, so they live on /board-preview/<slug>/ like the table's
  // chrome and not here.
  'video-embed': {
    C: VideoEmbed,
    demo: [{
      id: (settings as { youtube_embeds: string[] }).youtube_embeds[0],
      title: 'Blue Staffy puppies at home with us',
      caption: 'One of the videos the site already carries, reused at its original id.',
    }],
  },
  // ── the city components (project 5), previewed on /kit-preview/city/ ──────────────────────
  // ONE SERVED PHOTOGRAPH, ONCE PER PAGE. A served file keeps its served alt word for word
  // (working rule 11) and `img-alt-present-and-unique` (blocking) refuses a repeated alt, so a
  // served photo appears once on a page: the canvas gave Maggie's photo to five components, and
  // here each takes a different one (data/image-focus.json lists them).
  // THE SPECIMENS STATE PLACEHOLDER COPY, AND SAY SO. A city page's words come from its own
  // research board and outline (docs/reference/page-run.md row 8); a specimen shows the
  // component's shape, so its copy names no city and claims nothing the data files do not.
  'city-hero-filmstrip': {
    C: CityHeroFilmstrip,
    demo: [{
      as: 'h2',
      eyebrow: `${cap(LITTER)} puppies · ${SITE.address.city}`,
      title: 'Where Can I Find a Blue Staffy Puppy Near Me?',
      lede: `${cap(BOYS)} boys and ${GIRLS} girls, raised by ${SITE.breeder_name} in ${SITE.address.city}, with UK home delivery priced by distance.`,
      cta: { label: 'Choose your puppy', href: '#kit-city-hero-filmstrip' },
      more: { label: 'How delivery works', href: '#kit-city-hero-filmstrip' },
    }],
  },
  // The figures are the component's own reading of the data files; only the words are passed.
  'city-price-scale': {
    C: CityPriceScale,
    demo: [{
      labels: {
        count: 'puppies. What each part costs',
        delivery: 'UK home delivery, priced by distance',
        deposit: 'deposit: books your viewing and reserves your puppy',
        price: 'the price of one puppy',
      },
    }],
  },
  // Six claims the facts files and the breeder's answers back; the sixth, the canvas's guarantee,
  // is data/settings.json's (two years, answer board q07, 2026-09-29) through `guaranteeRow()`.
  'city-trust-ledger': {
    C: CityTrustLedger,
    demo: [{
      heading: 'What Should You Check Before Buying a Blue Staffy Puppy?',
      intro: 'The health of the parents, how the litter was raised and what happens if something goes wrong. Here is where each of ours stands.',
      photo: 'jones-magnificent-blue-staffy-sire.webp',
      caption: 'Jones, the sire',
      items: [
        { icon: 'dna', claim: 'DNA-tested parents', detail: 'Maggie and Jones, tested for L-2-HGA and HC-HSF4' },
        { icon: 'eye', claim: 'Eye and elbow screening', detail: 'Both parents screened before the litter' },
        { icon: 'heart', claim: 'Puppy Culture and ENS', detail: 'Early neurological stimulation, raised in the home' },
        { icon: 'return', claim: 'We take a puppy back', detail: 'If the fault is ours, or you can no longer care for it, as our written contract sets out' },
        ...(GUARANTEE ? [{ icon: 'shield' as const, claim: GUARANTEE.t, detail: GUARANTEE.d }] : []),
        { icon: 'delivery', claim: 'To your door', detail: 'DEFRA-approved transport, or collect in Carlisle' },
      ],
    }],
  },
  // The three nav components share CITY_DEMO_SECTIONS. On a real page the city layout
  // (src/layouts/CityShell.astro) mounts them in PageShell's nav slots; here the band is a
  // picture (`chrome: false`), so it moves no anchor.
  'city-contents-photo-index': {
    C: CityContentsPhotoIndex,
    demo: [{
      sections: CITY_DEMO_SECTIONS,
      heading: 'Which Part of Buying a Puppy Do You Need First?',
      lede: 'Start wherever your question is: the puppies and their prices, the delivery to your door or the health tests. Every part is one tap away.',
      photo: 'Christa.jpeg',
      photoAlt: 'Christa, a blue girl from the Carlisle litter',
    }],
  },
  'city-dial-photo-marker': {
    C: CityDialPhotoMarker,
    demo: [{ sections: CITY_DEMO_SECTIONS, photo: 'Cheryl1.jpeg', photoAlt: `Cheryl, a blue girl with a white blaze, one of the ${LITTER} puppies` }],
  },
  'city-jump-stepper': { C: CityJumpStepper, demo: [{ sections: CITY_DEMO_SECTIONS, chrome: false }] },
  // Each row states a fact the data files back; the figures are read from them.
  'city-takeaways-ledger': {
    C: CityTakeawaysLedger,
    demo: [{
      fit: 'full',
      heading: 'What Should a Buyer Take From This Page?',
      lede: `${cap(numberWord(5 + (GUARANTEE ? 1 : 0)))} plain answers, one sentence each, so you can decide whether a puppy from ${SITE.breeder_name}'s home in ${SITE.address.city} is right for you.`,
      photo: 'jones-strong-staffy-sire-temperament.webp',
      caption: `Jones, the sire, at home in ${SITE.address.city}`,
      rows: [
        { label: `The ${LITTER}`, text: `${cap(BOYS)} boys at ${BOY_PRICE} and ${GIRLS} girls at ${GIRL_PRICE}, all available now.` },
        { label: 'The deposit', text: depositLine },
        { label: 'The route', text: `DEFRA-approved transport for ${DELIVERY_BAND}, priced by distance, or collection in ${SITE.address.city}.` },
        { label: 'The parents', text: 'Maggie and Jones are DNA-tested for L-2-HGA and HC-HSF4, with eyes and elbows screened.' },
        { label: 'The raising', text: 'Raised in the home with Puppy Culture and ENS, and you may speak to our vet.' },
        ...(GUARANTEE ? [{ label: 'The guarantee', text: `${GUARANTEE.t}. ${GUARANTEE.d}` }] : []),
      ],
    }],
  },
  // The prints are data/puppies.json; the demo passes only the words around them.
  'city-puppy-sheet': {
    C: CityPuppySheet,
    demo: [{
      fit: 'full',
      heading: 'Which Puppy Will You Ask About First?',
      lede: `Maggie and Jones's ${LITTER} are laid out here like family prints, ${BOYS} boys at ${BOY_PRICE} and ${GIRLS} girls at ${GIRL_PRICE}, so you can pick a favourite before you ask.`,
      photo: 'maggie-blue-staffy-dam-with-pups.webp',
      caption: `Maggie, the dam, with her puppies in ${SITE.address.city}`,
    }],
  },
  'city-roster': {
    C: CityRoster,
    demo: [{
      heading: `How Do the ${cap(LITTER)} Puppies Compare Side by Side?`,
      lede: "Here is the whole litter on one sheet, so you can weigh up a boy against a girl: every puppy's sex, colour and price, taken straight from our list.",
      caption: `The ${LITTER} puppies, as listed`,
    }],
  },
  // The id is the site's own (data/settings.json youtube_embeds); the component refuses any other.
  'city-video-panel': {
    C: CityVideoPanel,
    demo: [{
      fit: 'full',
      heading: 'How Lively Is a Blue Staffy Puppy at Home?',
      lede: `Very, and our short film of puppies from one of our litters shows it better than we can say it; watch it before you choose between the ${LITTER}.`,
      videoId: (settings as { youtube_embeds: string[] }).youtube_embeds[0],
      videoTitle: 'Staffordshire Bull Terrier puppies: a litter of ours on film',
      caption: `A litter of ours, on film; it loads from YouTube only when you press play. Poster photo: Christa, one of the ${LITTER} available now.`,
      poster: 'Christa.jpeg',
      side: { photo: 'Ince1.jpg', alt: 'Ince standing by the garden fence at home', name: 'Ince', text: `A solid blue boy, one of the ${LITTER} available now.` },
      facts: [
        { label: 'Parents', text: 'Maggie and Jones, DNA-tested for L-2-HGA and HC-HSF4' },
        { label: 'Price', text: `${BOY_PRICE} for a boy, ${GIRL_PRICE} for a girl` },
        { label: 'Getting home', text: deliveryLine },
      ],
    }],
  },
  // Chapter one is a puppy photo with the page's own alt; chapter two a served file, whole.
  'city-chapters': {
    C: CityChapters,
    demo: [{
      fit: 'full',
      heading: 'Where Does Your Puppy Start, and How Does It Reach You?',
      lede: `In our home in ${SITE.address.city}, with its mother close by, and then at your door or in your arms at collection, whichever suits you.`,
      chapters: [
        { place: SITE.address.city, question: 'Who Raises Your Puppy Before It Leaves Home?', photo: 'Byrd1.jpg',
          photoAlt: `Byrd, one of the ${LITTER}, out on the garden decking`,
          text: 'We do, in our own home. Every litter is raised with Puppy Culture and ENS, and both parents, Maggie and Jones, are DNA-tested for L-2-HGA and HC-HSF4 with their eyes and elbows screened.' },
        { place: 'Your door', question: 'How Does Your Puppy Get From Us to Your Door?', photo: 'ethical-staffy-puppy-london-delivery.webp',
          text: `By DEFRA-approved transport, for ${DELIVERY_BAND} priced by distance, or you collect from us in ${SITE.address.city}. ${depositLine}` },
      ],
    }],
  },
  // The review is data/reviews.json by name; the photo is the one the homepage pairs with it.
  'city-letter': {
    C: CityLetter,
    demo: [{
      fit: 'full',
      heading: 'What Did a Family Say After Their Puppy Came Home?',
      lede: 'Mark J wrote this review of the blue Staffy puppy he had from us, and these are his words exactly as he sent them.',
      name: 'Mark J',
      photo: 'mark-blue-staffy-london.webp',
    }],
  },
  // `fit: 'full'` on every in-body specimen: /kit-preview/city/ paints each full width, as the
  // canvas did, so its images' `sizes` describe the full page; a city page's copy sits in the
  // column beside the dial (the default, 'column'; src/lib/cityKit.ts `citySizes`).
  // Three blocks, as a city page mounts them: numbering runs on through `start`, and only the
  // top block carries the rail. The rows are the specimen questions above. On a city page the
  // FAQPage node is the page's (src/lib/cityKit.ts `faqPageNode`, fed these same rows); the
  // preview is noindex and carries none.
  'city-faq-ledger': {
    C: CityFaqLedger,
    demo: [
      {
        block: 'buy', start: 1, fit: 'full',
        heading: 'What Do Buyers Ask Before Reserving a Puppy?',
        lede: 'The first questions are nearly always about money and the journey, so here are our straight answers on the prices, the deposit, delivery and collection.',
        rail: { photo: 'blue-staffy-testimonial-london-happy-owner.webp', caption: 'One of our puppies with its new owner.' },
        items: FAQ_BUY,
      },
      {
        block: 'trust', start: FAQ_BUY.length + 1, fit: 'full',
        heading: 'How Can You Check Us Before You Travel?',
        lede: 'You may live hours away, so we put the checks in your hands: the parents, their tests, our vet and what happens if something goes wrong.',
        items: FAQ_TRUST,
      },
      {
        block: 'life', start: FAQ_BUY.length + FAQ_TRUST.length + 1, fit: 'full',
        heading: 'Will a Staffy Suit Your Home and Your Days?',
        lede: 'Flats, long working days and first dogs come up again and again, so these answers cover space, exercise, time alone and how long a Staffy shares your home.',
        items: FAQ_LIFE,
      },
    ],
  },
  'city-newsletter-notice': {
    C: CityNewsletterNotice,
    demo: [{
      fit: 'full',
      eyebrow: 'Litter notes',
      heading: 'Want a Note When Our Next Litter Is Due?',
      lede: 'Leave your email and we will write to you when our next litter is on the way. It is one short note, and that is all this list is for.',
      photo: 'Christa.jpeg',
      // Its own words: the page's other Christa photos already say `short`, `scene` and the
      // contents alt, and img-alt-present-and-unique refuses a repeat.
      photoAlt: 'Christa, a blue Staffy girl with a white chest, sitting up and looking at the camera',
    }],
  },
  // The form is ContactFormKit's contract, laid out on the band; the line-up is data/puppies.json.
  'city-contact-lineup': {
    C: CityContactLineup,
    demo: [{
      fit: 'full',
      heading: `Which of Our ${cap(LITTER)} Puppies Would You Like to Ask About?`,
      lede: `Here are all ${LITTER} as they are today. Choose one in the form, tell us where you live, and we reply by email with the answers to everything you asked.`,
    }],
  },
  // ── the pieces inside a city section (London's board revision, 2026-10-03) ──────────────────
  // The byline sits on the hero's steel band on a page; here it paints on the bone surface, so its
  // ink is the surface's (convention 3). No read date is passed: the second line renders only when
  // a page-run record holds the breeder's read, and a specimen claims none.
  'city-signed-byline': {
    C: CitySignedByline,
    demo: [{ name: SITE.breeder_name, href: '#kit-city-signed-byline', town: SITE.address.city }],
  },
  // The tickets are data/puppies.json's available rows; the component reads them itself.
  'city-ticket-strip': { C: CityTicketStrip },
  // Each item states what the data files or the breeder's answers back; the tests are named only.
  'city-look-listen-checklist': {
    C: CityLookListenChecklist,
    demo: [{
      panes: [
        { title: 'Ask to see, on camera', hint: 'Tick each one as we show it', icon: 'look', items: [
          { label: 'The puppy with its mother', detail: 'Ask us to turn the camera to Maggie, our dam, with her puppies.' },
          { label: 'The paperwork', detail: 'The Kennel Club registration paperwork, the vaccination records and the microchipping details.' },
        ] },
        { title: 'Ask to hear, out loud', hint: 'Tick each one as we answer it', icon: 'listen', items: [
          { label: 'The health tests, by name', detail: 'L-2-HGA, HC-HSF4, eye screening and elbow screening.' },
          { label: 'The deposit', detail: depositLine },
          ...(GUARANTEE ? [{ label: GUARANTEE.t, detail: GUARANTEE.d }] : []),
        ] },
      ],
    }],
  },
  // A places file is a city's own data, so the specimen is London's: the file grouped by who sets
  // the rules, with the board's anchors, as the London page mounts it.
  'city-places-by-publisher': {
    C: CityPlacesByPublisher,
    demo: [{
      groups: placeGroups(londonPlaces.places as PlaceRow[], (href) => {
        const s = londonBoard.sections.find((x) => x.id === 'london-life') as { links?: { external?: { href: string; anchor: string }[] } };
        const hit = s?.links?.external?.find((l) => l.href === href);
        if (!hit) throw new Error(`the London board lists no link to ${href}`);
        return hit.anchor;
      }, (value) => /\blicen[cs]e\b/i.test(value)),
    }],
  },
  // The map's place is a city row's own `city` (data/locations.json), so the specimen is London's,
  // with the caption the London page builds from data/settings.json. Nothing loads until a tap.
  'city-map-facade': {
    C: CityMapFacade,
    demo: [{
      city: (locationRows as { slug: string; city: string }[]).find((r) => r.slug === 'blue-staffy-puppies-london')!.city,
      caption: `We deliver from ${TOWN} for ${DELIVERY_BAND}, priced by distance, by DEFRA-approved transport, or you collect your puppy from us in ${TOWN}.`,
    }],
  },
  // ── Manchester's own picks, previewed on /kit-preview/city-manchester/ (Phase F Tasks 28-31) ──
  // The copy is the picked canvas variants' (design/city-canvas/manchester/), about Manchester and
  // stating only data facts (Phase F ruling 10); the H1 is the approved outline's, and the hero
  // mounts it as the preview's one H1, as the page will. The links point at the preview's own sections.
  // The hero shows four of the litter and the counter all of them: the counter's repeats take a
  // new alt (`shownAbove`), its first uses keep the served one (working rule 11).
  'city-feature-and-three': {
    C: CityFeatureAndThree,
    demo: [{
      as: 'h1',
      title: manchesterOutline.h1,
      lede: `Not on its own. Our ${LITTER} ${SITE.address.city} puppies are priced by boy or girl, not by coat, and each can travel to ${MANCHESTER} or be collected.`,
      cta: { label: 'Ask about a puppy', href: '#kit-city-puppy-folder' },
      more: { label: `See all ${LITTER} puppies`, href: '#kit-city-range-sheet' },
      photos: MANCHESTER_HERO_PUPS,
    }],
  },
  'city-range-sheet': { C: CityRangeSheet, demo: [{ city: MANCHESTER, shownAbove: MANCHESTER_HERO_PUPS }] },
  'city-puppy-folder': { C: CityPuppyFolder, demo: [{ city: MANCHESTER }] },
  // Manchester's nav set (Task 29) shares MANCHESTER_DEMO_SECTIONS, as London's shares
  // CITY_DEMO_SECTIONS. On the page src/layouts/CityShell.astro mounts them in PageShell's nav
  // slots; here the bar is a picture (`chrome: false`), so it moves no anchor.
  'city-icon-rows': {
    C: CityIconRows,
    demo: [{ sections: MANCHESTER_DEMO_SECTIONS, city: MANCHESTER, photo: 'reputable-blue-staffy-breeder-manchester-pup.webp' }],
  },
  'city-numeral-rail': { C: CityNumeralRail, demo: [{ sections: MANCHESTER_DEMO_SECTIONS, city: MANCHESTER }] },
  'city-question-bar': {
    C: CityQuestionBar,
    demo: [{ sections: MANCHESTER_DEMO_SECTIONS, city: MANCHESTER, photo: MANCHESTER_BAR_PUP, chrome: false }],
  },
  // Manchester's in-body components (Task 30): full-width specimens, so `fit: 'full'`.
  'city-tick-card': {
    C: CityTickCard,
    demo: [{ fit: 'full', city: MANCHESTER, photo: MANCHESTER_FAMILY, cta: { label: 'Ask about a puppy', href: '#kit-city-puppy-folder' } }],
  },
  'city-photo-shelf': {
    C: CityPhotoShelf,
    demo: [{
      fit: 'full', heading: MANCHESTER_TABLE_UNDER[2], as: `h${MANCHESTER_TABLE_UNDER[1]}`, caption: MANCHESTER_TABLE.caption,
      city: MANCHESTER, shownAbove: availablePuppies().map((p) => p.name),
    }],
  },
  'city-offset-sheet': {
    C: CityOffsetSheet,
    demo: [{
      fit: 'full',
      heading: MANCHESTER_DEPOSIT_H2,
      lede: `Because the deposit is what books your viewing and holds your puppy for you, and all of it comes off the price, so a ${MANCHESTER} family making the trip to ${TOWN} knows the puppy will still be there.`,
      photo: MANCHESTER_FAMILY,
      photoAlt: 'A new owner holding her blue Staffy puppy in a pink collar, cheek to cheek in the garden',
      rows: depositTerms(),
      cta: { label: 'Ask about a viewing', href: '#kit-city-puppy-folder' },
    }],
  },
};
