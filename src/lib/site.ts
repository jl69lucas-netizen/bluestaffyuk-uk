import settings from '../../data/settings.json';
import { guaranteeWords, guaranteePhraseOf, coverSentenceOf, type GuaranteeSettings } from './guarantee';

export const SITE = settings;

/** The health guarantee's words, from data/settings.json `guarantee_label` (the breeder's answer,
 *  answer board q07, 2026-09-29). A page reads it here and never types it; `lower` gives it
 *  mid-sentence ("our two-year health guarantee"). It runs src/lib/guarantee.ts's check, so a label
 *  that disagrees with `guarantee_days`, or names a cover, stops the build. */
export function guaranteeLabel(form: 'label' | 'lower' = 'label'): string {
  return guaranteeWords(settings as GuaranteeSettings, form);
}

/** What a guarantee sentence says after "our written" (src/lib/guarantee.ts guaranteePhraseOf):
 *  "health guarantee, which covers … comes home," from data/settings.json `guarantee_cover`
 *  (answer board q02, 2026-09-29), or the label alone when there is no cover. */
export function guaranteePhrase(): string {
  return guaranteePhraseOf(settings as GuaranteeSettings);
}

/** The sentence a section headed with the guarantee's label carries, "It covers … comes home.",
 *  or "" when data/settings.json has no cover (review I7 and M2, 2026-09-29). */
export function guaranteeCoverSentence(subject = 'It'): string {
  return coverSentenceOf(settings as GuaranteeSettings, subject);
}
export const SITE_URL = (import.meta.env.SITE ?? 'https://SITE_URL_PLACEHOLDER').replace(/\/$/, '');

export const NAV = [
  { href: '/', label: 'Home' },
  { href: '/buy-blue-staffy-puppies-uk/', label: 'Puppies for Sale' },
  { href: '/uk-staffordshire-bull-terrier-guide/', label: 'Staffy Guide' },
  { href: '/blue-staffy-health-uk/', label: 'Health' },
  { href: '/uk-locations/', label: 'UK Locations' },
  { href: '/blog/', label: 'Blog' },
  { href: '/uk-blue-staffy-breeders-contact/', label: 'Contact' },
];

export const abs = (path: string) => `${SITE_URL}${path}`;

/** The logo as a RASTER, for the two consumers that cannot take the SVG in `SITE.logo`:
 *  schema.org `image`, which Google's structured-data pipeline wants as a bitmap, and
 *  `og:image`, which every social card renderer wants the same way. It is the 512px favicon
 *  render — scripts/build_favicons.py writes it from public/brand/logo-icon.svg, so it is
 *  the same badge the visible lockups show and it cannot drift away from them. */
export const LOGO_RASTER = '/icon-512.png';

const TITLE_CASE_KEEP_LOWER = new Set(['uk', 'and', 'of', 'for', 'in', 'the']);

const titleCase = (slug: string) =>
  slug.split('-').map((w) => (w.toLowerCase() === 'uk' ? 'UK'
    : TITLE_CASE_KEEP_LOWER.has(w.toLowerCase()) ? w.toLowerCase()
    : w.charAt(0).toUpperCase() + w.slice(1))).join(' ');

export interface Crumb { label: string; href: string }

/** Home + one crumb per path segment; intermediate labels come from NAV when it knows
 *  the href, else Title Case of the slug. The last crumb is the page itself. */
export function crumbs(path: string, leafTitle: string): Crumb[] {
  const segments = path.split('/').filter(Boolean);
  const out: Crumb[] = [{ label: 'Home', href: '/' }];
  segments.forEach((segment, i) => {
    const href = '/' + segments.slice(0, i + 1).join('/') + '/';
    const label = i === segments.length - 1
      ? leafTitle
      : (NAV.find((n) => n.href === href)?.label ?? titleCase(segment));
    out.push({ label, href });
  });
  return out;
}

/** A row of data/locations.json, written by scripts/extract_writers.py:write_locations. */
export interface LocationRow {
  slug: string; city: string; title: string; h1: string; description: string;
  canonical: string; robots: string; og_type: string; body_html: string;
  word_count: number; schema: unknown[]; defects: string[];
}

/** A row of data/puppies.json. */
export interface PuppyRow {
  slug: string; name: string; sex: 'male' | 'female'; price_gbp: number;
  status: 'Available' | 'Reserved' | 'Sold'; colour: string;
  card_photo: string; gallery: string[];
}

/**
 * A GBP amount with its thousands separator, as `PuppyCard` writes a price: 1500 is a number
 * and £1,500 is money. The £ is NOT included — three pages interpolate the sign themselves,
 * inside a sentence or a table cell where the currency belongs to the sentence rather than to
 * the figure, and a helper that carried it would have those three stripping it back off.
 * `available-puppies/index.astro` keeps its own £-inclusive spelling for that reason.
 */
export const gbp = (n: number) => n.toLocaleString('en-GB');
