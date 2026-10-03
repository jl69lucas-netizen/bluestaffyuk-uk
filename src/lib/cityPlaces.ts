// src/lib/cityPlaces.ts — a city's places file (data/city-places/<slug>.json, written by the
// bsuk-city-places skill) grouped by who sets the rules, for CityPlacesByPublisher (the London
// board revision, answer board 2026-10-03-london-board-revision q04 (c)).
//
// NOTHING IS REWORDED. Each fact is the file's `value` as the file words it; each place's `where`
// is the file's `area` with only its bracketed aside dropped, and it is left out where the file
// names no borough (an area that opens "London:" or reads NOT FETCHED). Each publisher's source
// pages are the facts' own `source` URLs, each once, in the order the facts first cite them, and
// each anchor is the board's (`anchorOf`): a source the board does not list stops the build
// (working rule 12).
//
// LEFT OUT ON PURPOSE (the board record, subcomponents[london-places].note): facts that are not
// about dogs, namely a park's size, its toilets and its postal address. A source that only such a
// fact cites is therefore not linked.

export interface PlaceFact { value: string; source: string }
export interface PlaceRow { name: string; area?: string; managed_by: string; facts: PlaceFact[] }
export type FactKind = 'no' | 'lead' | 'note';
export interface PlaceGroup {
  publisher: string;
  sources: { href: string; anchor: string }[];
  places: { name: string; where: string | null; facts: { kind: FactKind; text: string }[] }[];
}

/** A fact about something other than dogs: a size, toilets or an address. */
const NOT_ABOUT_DOGS = /\bhectares?\b|\btoilets\b|^Address\b/i;

/** The chip a fact carries: dog-free, on a lead, or anything else worth knowing. It is read from
 *  the fact's main clause, its bracketed asides dropped: Greenwich's Rose Garden rule is "on a
 *  lead", and its aside only records that an older leaflet called the garden dog-free. */
export function factKind(value: string): FactKind {
  const main = value.replace(/\([^)]*\)/g, '');
  if (/\bnot permitted\b|\bdog-free\b/i.test(main)) return 'no';
  if (/\bon (?:a (?:short )?lead|leads)\b|\bkept on a lead\b/i.test(main)) return 'lead';
  return 'note';
}

/** The file's `area`, its bracketed aside dropped; null where the file names no borough. */
export function placeWhere(area: string | undefined): string | null {
  if (!area || /^London:/.test(area) || /NOT FETCHED/.test(area)) return null;
  return area.replace(/\s*\([^)]*\)\s*$/, '').trim() || null;
}

/** `omit` drops a fact the page has its own reason to leave out (the caller names the reason). */
export function placeGroups(places: PlaceRow[], anchorOf: (href: string) => string,
  omit: (value: string) => boolean = () => false): PlaceGroup[] {
  const groups: PlaceGroup[] = [];
  for (const p of places) {
    const facts = p.facts.filter((f) => !NOT_ABOUT_DOGS.test(f.value) && !omit(f.value));
    if (!facts.length) continue;
    let g = groups.find((x) => x.publisher === p.managed_by);
    if (!g) groups.push((g = { publisher: p.managed_by, sources: [], places: [] }));
    for (const f of facts) {
      if (!g.sources.some((s) => s.href === f.source)) g.sources.push({ href: f.source, anchor: anchorOf(f.source) });
    }
    g.places.push({ name: p.name, where: placeWhere(p.area), facts: facts.map((f) => ({ kind: factKind(f.value), text: f.value })) });
  }
  return groups;
}
