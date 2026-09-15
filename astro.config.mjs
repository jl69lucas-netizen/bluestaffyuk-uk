import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';

const site = process.env.SITE_URL || 'https://SITE_URL_PLACEHOLDER';

export default defineConfig({
  site,
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'always' },
  vite: { plugins: [tailwindcss()] },
  integrations: [react(), mdx()],
});
