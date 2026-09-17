import { defineConfig } from '@playwright/test';
import { SITE_PORT, FIXTURE_PORT, SITE_BASE } from './lib/servers.js';
import { readFileSync, existsSync } from 'node:fs';
// form.ts throws without PUBLIC_FORMSPREE_ID. Loading .env here rather than requiring every
// caller to `set -a; . ./.env` keeps `npm run test:render:*` working as documented.
const envFile = new URL('../../.env', import.meta.url);
if (existsSync(envFile)) {
  for (const line of readFileSync(envFile, 'utf8').split('\n')) {
    const m = /^([A-Z0-9_]+)=(.*)$/.exec(line.trim());
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
}

export default defineConfig({
  testDir: '.',
  testMatch: ['meta.spec.ts', 'pages.spec.ts'],
  // Fires for EVERY invocation of this config, meta-only included — see the long
  // comment in global-setup.ts for what deliberately does and doesn't live there.
  globalSetup: './global-setup.ts',
  fullyParallel: false,
  workers: 2,
  timeout: 120_000,
  reporter: [['list']],
  use: {
    baseURL: SITE_BASE,
    deviceScaleFactor: 1,
  },
  projects: [
    { name: 'vp375', use: { viewport: { width: 375, height: 812 } } },
    { name: 'vp768', use: { viewport: { width: 768, height: 1024 } } },
    { name: 'vp1280', use: { viewport: { width: 1280, height: 800 } } },
  ],
  webServer: [
    // The built site, served at its own root so absolute /images/... resolve.
    {
      command: `python3 -m http.server ${SITE_PORT} --bind 127.0.0.1`,
      cwd: '../../dist',
      port: SITE_PORT,
      reuseExistingServer: false,
      timeout: 60_000,
    },
    // The repo root, so tests/render/fixtures/... are reachable.
    {
      command: `python3 -m http.server ${FIXTURE_PORT} --bind 127.0.0.1`,
      cwd: '../../',
      port: FIXTURE_PORT,
      reuseExistingServer: false,
      timeout: 60_000,
    },
  ],
});
