import { readFileSync } from 'node:fs';

/**
 * The city tiers, read from src/lib/cityKit.ts `TIER` (the one source: src/styles/city.css
 * mirrors it, the components' container queries use it), so the two city checks that judge a
 * section by its tier — cityTypeFit and city-layout-follows-box — read the SAME edges of the
 * SAME box (the section root's content box) as the CSS they judge (the Task 7b quality review, I4).
 */
const src = readFileSync(new URL('../../../src/lib/cityKit.ts', import.meta.url), 'utf8');
const m = /export const TIER = \{\s*tablet:\s*(\d+),\s*desktop:\s*(\d+)\s*\}/.exec(src);
if (!m) throw new Error('src/lib/cityKit.ts has no TIER = { tablet, desktop } to read');
export const TIER = { tablet: Number(m[1]), desktop: Number(m[2]) };
export type Tier = typeof TIER;
