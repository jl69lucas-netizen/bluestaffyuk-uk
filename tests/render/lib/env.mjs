import { readFileSync, existsSync } from 'node:fs';

// The harness's .env parser. `checks/form.ts` throws without PUBLIC_FORMSPREE_ID, so the
// Playwright config loads .env here rather than requiring every caller to
// `set -a; . ./.env` — that keeps `npm run test:render:*` working as documented.
//
// Plain .mjs, not .ts, so tests/py/test_env_loader.py can run this exact file under node
// with no compile step between the test and the shipped code. It handles secrets: it never
// logs, not even on a parse failure, and it never overrides a variable the caller already
// set — an explicit `FOO=bar npm run ...` must beat the file or debugging is impossible.
const LINE = /^(?:export\s+)?([A-Z0-9_]+)=(.*)$/;

export function parseEnv(text) {
  const out = new Map();
  for (const raw of text.split('\n')) {
    const m = LINE.exec(raw.trim());
    if (!m) continue;
    let value = m[2].trim();
    // One matching pair of quotes only. Mismatched quotes are not a pair, and a value that
    // genuinely contains a quote character keeps it.
    if (value.length >= 2 && (value[0] === '"' || value[0] === "'") && value[value.length - 1] === value[0]) {
      value = value.slice(1, -1);
    }
    out.set(m[1], value);
  }
  return out;
}

export function loadEnv(file, env = process.env) {
  if (!existsSync(file)) return env;
  for (const [key, value] of parseEnv(readFileSync(file, 'utf8'))) {
    if (env[key] === undefined) env[key] = value;
  }
  return env;
}
