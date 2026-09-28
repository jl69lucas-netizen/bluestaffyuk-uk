import { defineConfig } from '@playwright/test';
import { loadEnv } from './lib/env.mjs';
loadEnv(new URL('../../.env', import.meta.url));

// The city-kit render spec (tests/render/city-kit.spec.ts): the built city components on
// dist/, at the four widths the canvas smoke paints (tests/py/test_city_kit.py pins
// them — 1024 is rule 10's and the dial's boundary). Serves dist/ itself on RENDER_CITY_PORT
// (default 4351) so it can run beside the page harness and the canvas smoke. Build first.
const PORT = Number(process.env.RENDER_CITY_PORT ?? 4351);

export default defineConfig({
  testDir: '.',
  testMatch: ['city-kit.spec.ts'],
  fullyParallel: true,
  workers: 4,
  timeout: 90_000,
  reporter: [['list']],
  use: { baseURL: `http://127.0.0.1:${PORT}`, deviceScaleFactor: 1 },
  projects: [
    { name: 'vp375', use: { viewport: { width: 375, height: 812 } } },
    { name: 'vp768', use: { viewport: { width: 768, height: 1024 } } },
    { name: 'vp1024', use: { viewport: { width: 1024, height: 768 } } },
    { name: 'vp1280', use: { viewport: { width: 1280, height: 800 } } },
  ],
  webServer: [{
    command: `python3 -m http.server ${PORT} --bind 127.0.0.1`,
    cwd: '../../dist',
    port: PORT,
    reuseExistingServer: false,
    timeout: 60_000,
  }],
});
