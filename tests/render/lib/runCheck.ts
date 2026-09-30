import type { Page } from '@playwright/test';
import { MAX_DEFECT_ROWS, type Check, type CheckContext, type CheckResult } from './registry.js';

/**
 * The single call site for every check, in both meta.spec and pages.spec.
 *
 * Validating here rather than inside each check means the contract binds on real pages,
 * where a check meets sixty-two anchors, and not only on fixtures, where it meets two.
 * Every violation throws with the check id in the message, because a malformed result that
 * merely warns becomes a permanent skew in the ledger nobody can see.
 */
export async function runCheck(
  check: Check,
  page: Page,
  viewport: number,
  ctx: CheckContext,
): Promise<CheckResult> {
  const result = await check.run(page, viewport, ctx);

  if (!Number.isInteger(result.examined) || result.examined < 0) {
    throw new Error(
      `${check.id}: examined must be a non-negative integer, got ${JSON.stringify(result.examined)}`,
    );
  }

  if (result.defects.length > MAX_DEFECT_ROWS) {
    throw new Error(
      `${check.id}: emitted ${result.defects.length} defect rows, cap is ${MAX_DEFECT_ROWS}. ` +
        `A row is one failure MODE; instances belong in \`count\`. Reporting per-instance makes ` +
        `this family's total incomparable with every other family's.`,
    );
  }

  for (const d of result.defects) {
    if (d.checkId !== check.id) {
      throw new Error(`${check.id}: emitted a row with checkId "${d.checkId}"`);
    }
    if (d.family !== check.family) {
      throw new Error(`${check.id}: emitted a row with family "${d.family}", expected ${check.family}`);
    }
    if (!Number.isInteger(d.count) || d.count < 1) {
      throw new Error(
        `${check.id}: every defect row needs an integer count >= 1, got ${JSON.stringify(d.count)}`,
      );
    }
    if (!d.message || !d.message.trim()) {
      throw new Error(`${check.id}: emitted a row with an empty message`);
    }
  }

  return result;
}
