import { defineConfig } from 'astro/config';
import { loadEnv } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';

const env = loadEnv(process.env.NODE_ENV ?? 'production', process.cwd(), '');
const site = env.SITE_URL || process.env.SITE_URL || 'https://SITE_URL_PLACEHOLDER';

export default defineConfig({
  site,
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'always' },
  vite: { plugins: [tailwindcss()] },
  integrations: [react(), mdx()],
});
