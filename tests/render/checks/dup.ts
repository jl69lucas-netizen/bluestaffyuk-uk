import { register, type CheckContext, type CheckResult } from '../lib/registry.js';
import { loadWhitelist, normalise } from '../lib/dupCorpus.js';
import type { Page } from '@playwright/test';

/** The Python auditor's window. Changing it here without changing it there splits the gate. */
const MIN_WORDS = 12;

/**
 * A sibling's 12-word shingle set, cached by the sibling's TEXT (not its slug, so a fixture
 * corpus and dist/ can never collide on a name). The corpus is every built page, so without
 * this each of the 57 page-viewports would re-shingle the same ~104 pages.
 */
const shingleCache = new Map<string, Set<string>>();
function shinglesOf(text: string): Set<string> {
  let set = shingleCache.get(text);
  if (!set) {
    const w = normalise(text);
    set = new Set<string>();
    for (let i = 0; i + MIN_WORDS <= w.length; i++) set.add(w.slice(i, i + MIN_WORDS).join(' '));
    shingleCache.set(text, set);
  }
  return set;
}

/**
 * The stretches of a shared run that no whitelisted stem covers.
 *
 * The whitelist exempts LINES, not the runs they sit in. Growth fuses a whitelisted line
 * with any shared passage touching it, and skipping a run that merely CONTAINED a stem
 * exempted the passage along with it (found 2026-09-11: a 17-word <legend> right after the
 * shipping line never fired). So every stem occurrence is cut out and each side is judged on
 * its own. Re-joining the sides instead would glue two short shared phrases into one false
 * 12-word passage. Mirrors `unwhitelisted_segments` in scripts/dup_content_audit.py.
 */
function unwhitelistedSegments(run: string[], stems: string[][]): string[][] {
  const covered = new Array<boolean>(run.length).fill(false);
  for (const stem of stems) {
    for (let k = 0; k + stem.length <= run.length; k++) {
      if (stem.every((w, n) => run[k + n] === w)) covered.fill(true, k, k + stem.length);
    }
  }
  const segments: string[][] = [];
  let start = -1;
  for (let k = 0; k <= run.length; k++) {
    if (k < run.length && !covered[k]) {
      if (start < 0) start = k;
    } else if (start >= 0) {
      segments.push(run.slice(start, k));
      start = -1;
    }
  }
  return segments;
}

/**
 * DUP: no page may share a run of copy with a sibling.
 *
 * Chosen over reimplementing the whole auditor in TypeScript: the SHINGLING is fifteen
 * lines and reimplementing it costs nothing, but the WHITELIST is the tuned artefact —
 * it encodes exactly which lines CLAUDE.md mandates as identical across siblings, and a
 * second copy of it would drift the first time either was tuned. So the comparison is
 * local (fast, and its failure messages are the harness's own) while the whitelist is
 * read out of `scripts/dup_content_audit.py` at run time. One list, two readers.
 *
 * Rejected: shelling out to the Python auditor per page. It is inherently cross-page, so
 * every one of the 45 page-viewport runs would re-run the whole pairwise comparison, and
 * the meta gate would have nothing to fire against — a fixture page is not in `dist/`.
 */
register({
  id: 'dup-no-sibling-crossover',
  family: 'DUP',
  severity: 'advisory',
  describe: 'no run of 12+ words is shared with a sibling page outside the mandated whitelist',
  minExamined: 1,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    const siblings = await ctx.siblings();
    // examined counts SIBLING PAGES COMPARED AGAINST, which is the unit actually judged.
    // Counting shingles instead would report thousands while possibly comparing against
    // nothing — a page with no siblings must read as "0 examined", not as a pass.
    if (siblings.length === 0) return { examined: 0, defects: [] };

    // Form text (labels, legends, option copy) is component UI shared by design, not prose.
    // scripts/dup_content_audit.py never reads it (SKIP_TAGS has "form"); before 2026-09-11 this
    // check did, and flagged the seven-field contract's fixed questions as sibling crossovers.
    // Hide forms for the read and restore them, so later checks on this page see it unchanged.
    const own = normalise(
      await page.evaluate(() => {
        const root = document.querySelector('main') || document.body;
        const forms = Array.from(root.querySelectorAll('form')) as HTMLElement[];
        const prev = forms.map((f) => f.style.display);
        forms.forEach((f) => (f.style.display = 'none'));
        const text = root.innerText || '';
        forms.forEach((f, i) => (f.style.display = prev[i]));
        return text;
      }),
    );
    const whitelist = loadWhitelist().map(normalise);

    const ownShingles = new Map<string, number>();
    for (let i = 0; i + MIN_WORDS <= own.length; i++) {
      const key = own.slice(i, i + MIN_WORDS).join(' ');
      if (!ownShingles.has(key)) ownShingles.set(key, i);
    }

    const ordered = [...ownShingles.entries()].sort((a, b) => a[1] - b[1]);
    const findings: { sibling: string; words: number; run: string }[] = [];
    for (const sib of siblings) {
      const sibShingles = shinglesOf(sib.text);
      const reported: string[] = [];
      for (const [key, i] of ordered) {
        if (!sibShingles.has(key)) continue;
        if (reported.some((r) => r.includes(key))) continue;
        // Grow the match to its maximal run, so one long shared passage is ONE finding
        // rather than one per sliding window. Without this a 60-word crossover reports
        // 49 times and DUP outvotes every other family by counting style alone.
        let j = i + MIN_WORDS;
        while (j < own.length && sibShingles.has(own.slice(j - MIN_WORDS + 1, j + 1).join(' '))) j++;
        const run = own.slice(i, j);
        reported.push(run.join(' '));
        for (const seg of unwhitelistedSegments(run, whitelist)) {
          if (seg.length >= MIN_WORDS) findings.push({ sibling: sib.slug, words: seg.length, run: seg.join(' ') });
        }
      }
    }

    if (!findings.length) return { examined: siblings.length, defects: [] };
    findings.sort((a, b) => b.words - a.words);
    return {
      examined: siblings.length,
      defects: [
        {
          checkId: 'dup-no-sibling-crossover',
          family: 'DUP' as const,
          viewport,
          count: findings.length,
          message:
            `${findings.length} passage(s) shared with a sibling: ` +
            findings
              .slice(0, 3)
              .map((f) => `${f.words}w vs /${f.sibling}/ "${f.run.slice(0, 90)}"`)
              .join(' | '),
        },
      ],
    };
  },
});
