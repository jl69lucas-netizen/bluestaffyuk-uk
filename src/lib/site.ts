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
