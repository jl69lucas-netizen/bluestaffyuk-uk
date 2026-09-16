import settings from '../../data/settings.json';

export const SITE = settings;
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
