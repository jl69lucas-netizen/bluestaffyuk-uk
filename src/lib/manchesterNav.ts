// src/lib/manchesterNav.ts — Manchester's nav set names, ONE list for the preview and the page (the
// Manchester page run, Phase F Tasks 29 and 32).
//
// /kit-preview/city-manchester/ (through src/components/kit/_registry.ts) and Manchester's own page
// (src/pages/uk-locations/blue-staffy-puppies-manchester-uk.astro) both read it, so the dial, the
// bar and the contents rows name each section the same way in both places. It lives here, not in
// the registry, because the registry imports every kit component: a page that imported it would
// ship every city's component CSS.
import outline from '../../data/outlines/blue-staffy-puppies-manchester-uk.json';
import locationRows from '../../data/locations.json';
import type { CityIcon } from './sections';

/** Manchester's city name, from data/locations.json. */
export const MANCHESTER = (locationRows as { slug: string; city: string }[]).find((r) => r.slug === outline.slug)!.city;

/** The questions Manchester's nav set lists: every H2 of its approved outline, word for word, in
 *  page order (thirteen; data/outlines/, approved at STOP 2). */
export const MANCHESTER_H2: string[] = (outline as { sections: { headings: { level: number; text: string }[] }[] }).sections
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
  throw new Error(`manchesterNav.ts: MANCHESTER_NAV names ${MANCHESTER_NAV.length} sections; the outline has ${MANCHESTER_H2.length} H2s`);
}
