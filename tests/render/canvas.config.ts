import { defineConfig } from '@playwright/test';

// The London component canvas smoke (docs/superpowers/plans/2026-09-27-london-component-design-pass.md
// Task 5). A config of its own, so `npm run test:render` and the meta gate never pick the canvas
// up, and no scorecard partial is written: the frames are mockups, not pages.
// `npm run test:render:canvas` first emits every variant as a standalone frame under
// docs/artifacts/canvas/london-frames/ (git-ignored), with scripts/build_component_canvas.py
// --emit-frames, then serves the repo root so the frames' /public/images/ and
// /src/assets/puppies/ URLs resolve. RENDER_CANVAS_PORT moves the server off 4331.
const PORT = Number(process.env.RENDER_CANVAS_PORT ?? 4331);

export default defineConfig({
  testDir: '.',
  testMatch: ['canvas.spec.ts'],
  fullyParallel: true,
  workers: 4,
  timeout: 60_000,
  reporter: [['list']],
  use: { baseURL: `http://127.0.0.1:${PORT}`, deviceScaleFactor: 1 },
  projects: [
    { name: 'vp375', use: { viewport: { width: 375, height: 812 } } },
    { name: 'vp768', use: { viewport: { width: 768, height: 1024 } } },
    // 1024 is where rules/design.md rule 10's 390–450px hero band starts; measuring only at
    // 1280 let a hero that is too tall at the narrowest desktop width pass (review, Task 5).
    { name: 'vp1024', use: { viewport: { width: 1024, height: 768 } } },
    { name: 'vp1280', use: { viewport: { width: 1280, height: 800 } } },
  ],
  webServer: [{
    command: `python3 -m http.server ${PORT} --bind 127.0.0.1`,
    cwd: '../../',
    port: PORT,
    reuseExistingServer: false,
    timeout: 60_000,
  }],
});
