// src/components/kit/cityIcons.ts — the line icons a city page's nav set draws.
//
// One path each on the same 24 grid, stroked in `currentColor` at 2px, so they read as one set
// (the icons the London canvas's stepper band used, jump-links A). Kept in the kit folder beside
// markShapes.ts because they are shapes, not data; `CityIcon` in src/lib/sections.ts names them.
import type { CityIcon } from '../../lib/sections';

export const CITY_ICONS: Record<CityIcon, string> = {
  list: 'M4 7h16M4 12h16M4 17h10',
  puppies: 'M8.5 9.5a1.8 2.3 0 1 0 0-.01zM15.5 9.5a1.8 2.3 0 1 0 0-.01zM5 13a1.6 2 0 1 0 0-.01zM19 13a1.6 2 0 1 0 0-.01zM12 13.5c-2.6 0-4.5 2.4-4.5 4.2 0 1.4 1.2 2 2.4 1.7 1-.3 1.4-.6 2.1-.6s1.1.3 2.1.6c1.2.3 2.4-.3 2.4-1.7 0-1.8-1.9-4.2-4.5-4.2z',
  prices: 'M16 6.5A4 4 0 0 0 9 9v9M6.5 13h7M6 18h12',
  deposit: 'M3 8h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4zM10 8v10',
  delivery: 'M1 6h13v10H1zM14 10h4l3 3v3h-7M3.5 18.5a2 2 0 1 0 4 0 2 2 0 1 0-4 0M15.5 18.5a2 2 0 1 0 4 0 2 2 0 1 0-4 0',
  health: 'M12 2 4 5v6c0 5 3.5 9 8 11 4.5-2 8-6 8-11V5zM9 12l2 2 4-4',
  home: 'M3 11 12 4l9 7M5 10v10h14V10M10 20v-6h4v6',
  play: 'M4 5h16v14H4zM10 9v6l5-3z',
  faq: 'M2 12a10 10 0 1 0 20 0 10 10 0 1 0-20 0M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01',
  enquire: 'M3 5h18v14H3zM3 6l9 7 9-7',
  // Manchester's contents rows (contents-list B, "Icon rows"; Phase F Task 29), on the same grid:
  // a ruled paper, a heart, two people and a drop for the coat.
  papers: 'M14 3H6v18h12V7zM14 3v4h4M9 12h6M9 16h6',
  guarantee: 'M20.8 5.6a5 5 0 0 0-7.1 0L12 7.3l-1.7-1.7a5 5 0 0 0-7.1 7.1L12 21.5l8.8-8.8a5 5 0 0 0 0-7.1z',
  family: 'M6 8a3 3 0 1 0 6 0 3 3 0 1 0-6 0M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M14.5 9a2.5 2.5 0 1 0 5 0 2.5 2.5 0 1 0-5 0M15.5 14.2A5 5 0 0 1 21 19',
  coat: 'M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z',
};

/** The trust ledger's line icons (city component 3), on the same grid and stroke. */
export type TrustIcon = 'dna' | 'eye' | 'shield' | 'heart' | 'return' | 'delivery' | 'chip';
export const TRUST_ICONS: Record<TrustIcon, string> = {
  dna: 'M8 2c0 5 8 5 8 10s-8 5-8 10M16 2c0 5-8 5-8 10s8 5 8 10M9 6h6M9 18h6',
  eye: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM9 12a3 3 0 1 0 6 0 3 3 0 1 0-6 0',
  shield: 'M12 2 4 5v6c0 5 3.5 9 8 11 4.5-2 8-6 8-11V5zM9 12l2 2 4-4',
  heart: 'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z',
  return: 'M3 12a9 9 0 1 0 3-6.7L3 8M3 3v5h5',
  delivery: CITY_ICONS.delivery,
  // A microchip: the die, its core and two pins a side (London final fixes B1, 2026-10-05).
  chip: 'M7 7h10v10H7zM10 10h4v4h-4zM10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4',
};
