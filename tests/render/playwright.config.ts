import { defineConfig } from '@playwright/test';
import { SITE_PORT, FIXTURE_PORT, SITE_BASE } from './lib/servers.js';
import { loadEnv } from './lib/env.mjs';
// checks/form.ts throws without PUBLIC_FORMSPREE_ID; loading .env here keeps
// `npm run test:render:*` working as documented. Parser + its tests: lib/env.mjs.
loadEnv(new URL('../../.env', import.meta.url));

export default defineConfig({
  testDir: '.',
  // kit-search.spec.ts drives the header combobox on the built kit-preview page. It is in
  // the suite, so `npm run test:render` covers it; `npm run test:render:search` filters to
  // it. Like the meta gate, it writes no scorecard partial — but globalSetup's resetRaw()
  // still fires for it, so it belongs BEFORE pages.spec.ts in any hand-run sequence.
  testMatch: ['meta.spec.ts', 'pages.spec.ts', 'kit-search.spec.ts'],
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
