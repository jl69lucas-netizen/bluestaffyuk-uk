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
import CityHero from './CityHero.astro';
import CityPriceScale from './CityPriceScale.astro';
import CityTrustLedger from './CityTrustLedger.astro';
import CityContents from './CityContents.astro';
import CityDial from './CityDial.astro';
import CityJumpBand from './CityJumpBand.astro';
import type { SectionRef } from '../../lib/sections';

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
  | 'city-hero' | 'city-price-scale' | 'city-trust-ledger' | 'city-contents' | 'city-dial'
  | 'city-jump-band';

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
}

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

/** The city nav set's demo sections: the city preview's OWN section anchors
 *  (`kit-<component id>`, which /kit-preview/city/ gives every section it renders), so every
 *  link resolves and the scroll-spy has real sections to observe — no stub block is needed. One
 *  list for all three nav components, for the reason DEMO_SECTIONS gives. Specimen wording: it
 *  names no city. */
export const CITY_DEMO_SECTIONS: SectionRef[] = [
  { id: 'kit-city-hero', label: 'Puppies', question: 'Where Can I Find a Blue Staffy Puppy Near Me?', icon: 'puppies' },
  { id: 'kit-city-price-scale', label: 'Prices', question: 'What Does Each Part of Buying a Puppy Cost?', icon: 'prices' },
  { id: 'kit-city-trust-ledger', label: 'Checks', question: 'What Should You Check Before Buying?', icon: 'health' },
  { id: 'kit-city-contents', label: 'Contents', question: 'Which Part of Buying a Puppy Do You Need First?', icon: 'list' },
  { id: 'kit-city-dial', label: 'Dial', question: 'Where Are You on the Page?', icon: 'home' },
  { id: 'kit-city-jump-band', label: 'Jump', question: 'How Do You Jump to a Section on a Phone?', icon: 'faq' },
];

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
  'city-hero': {
    C: CityHero,
    demo: [{
      as: 'h2',
      eyebrow: `Six puppies · ${SITE.address.city}`,
      title: 'Where Can I Find a Blue Staffy Puppy Near Me?',
      lede: `Three boys and three girls, raised by ${SITE.breeder_name} in ${SITE.address.city}, with UK home delivery priced by distance.`,
      cta: { label: 'Choose your puppy', href: '#kit-city-hero' },
      more: { label: 'How delivery works', href: '#kit-city-hero' },
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
  // Five claims the facts files and the breeder's answers back (the canvas's sixth, a
  // guarantee length, is not stated while data/settings.json `guarantee_days` is null).
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
        { icon: 'return', claim: 'We take a puppy back', detail: 'If the fault is ours, or you can no longer care for it' },
        { icon: 'delivery', claim: 'To your door', detail: 'DEFRA-approved transport, or collect in Carlisle' },
      ],
    }],
  },
  // The three nav components share CITY_DEMO_SECTIONS. On a real page PageShell mounts them
  // (`cityNav`); here the band is a picture (`chrome: false`), so it moves no anchor.
  'city-contents': {
    C: CityContents,
    demo: [{
      sections: CITY_DEMO_SECTIONS,
      heading: 'Which Part of Buying a Puppy Do You Need First?',
      lede: 'Start wherever your question is: the puppies and their prices, the delivery to your door or the health tests. Every part is one tap away.',
      photo: 'Christa.jpeg',
      photoAlt: 'Christa, a blue girl from the Carlisle litter',
    }],
  },
  'city-dial': {
    C: CityDial,
    demo: [{ sections: CITY_DEMO_SECTIONS, photo: 'Cheryl1.jpeg', photoAlt: 'Cheryl, a blue girl with a white blaze, one of the six puppies' }],
  },
  'city-jump-band': { C: CityJumpBand, demo: [{ sections: CITY_DEMO_SECTIONS, chrome: false }] },
};
