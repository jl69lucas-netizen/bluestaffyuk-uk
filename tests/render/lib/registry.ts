import type { Page } from '@playwright/test';

// A11Y added 2026-08-07: rendered-contrast invariants. It is its own family rather than a
// CSS check because the failure it catches is a COMPOSITION defect (component re-themed,
// child not), not a stylesheet defect — neither declaration is wrong in isolation.
export type Family = 'IMG' | 'LAYOUT' | 'NAV' | 'CSS' | 'SEM' | 'SCHEMA' | 'DUP' | 'A11Y' | 'FORM';
export type Severity = 'blocking' | 'advisory';

export interface Defect {
  checkId: string;
  family: Family;
  viewport: number;
  /**
   * How many individual units failed.
   *
   * A defect ROW is one failure MODE of one check at one viewport. `count` carries the
   * magnitude. Without this split the first baseline mixed units: layout-min-font-size
   * folded 108 undersized text nodes into one row while nav-jump-target-lands emitted one
   * row per anchor, so NAV supplied 81% of the headline number by counting granularity
   * alone — and "which family produces the most defects", the whole point of the ledger,
   * was answering a question about aggregation style.
   */
  count: number;
  message: string;
}

export interface CheckResult {
  /**
   * The number of units this check's own pass/fail predicate was evaluated
   * AGAINST. Not the number of nodes in the document, and not the number of
   * nodes it could have looked at.
   *
   * This distinction is the whole guard. A check that returns
   * `querySelectorAll('*').length` reports ~1,100 "examined" on a page where
   * it evaluated exactly one expression — so if that one expression is wrong,
   * the check reports clean forever and every zero-examined guard downstream
   * still passes. Measured on the congo-pair page: the first draft of
   * `layout-no-horizontal-overflow` reported examined=1116 having box-tested 0
   * elements. Count what you actually judged.
   */
  examined: number;
  defects: Defect[];
}

/**
 * What the harness knows about the page being measured that the page itself does not say.
 *
 * Only `pageType` so far, and it exists because SCHEMA invariants are genuinely page-type
 * conditioned: a bird listing must carry EXACTLY ONE Product/Offer, while a hub legitimately
 * carries an ItemList of many, and a page cannot be trusted to self-declare which it is —
 * the defect this catches is precisely a page whose schema does not match its role. Every
 * other check ignores this argument.
 *
 * `targets.json` is the authority for the value; on fixtures the meta gate supplies the
 * strictest type so a check cannot pass its fixtures under a laxer branch than it will meet
 * on a real page.
 */
export interface CheckContext {
  pageType: string;
  /** The page's own slug, as written in targets.json. */
  slug: string;
  /**
   * The other pages this one must not read like — resolved by the CALLER, not the check.
   *
   * DUP is the one family that cannot be answered from a single painted page, and how the
   * sibling set is chosen is a policy decision (every other built page — see
   * siblingSlugsFor in lib/dupCorpus.ts) that belongs with the target list rather than
   * buried in a check.
   * Passing it as a callback also gives the meta gate a real corpus to fire against, so
   * the fixture pair tests the actual comparison rather than a mocked one.
   */
  siblings(): Promise<{ slug: string; text: string }[]>;
}

export interface Check {
  id: string;
  family: Family;
  severity: Severity;
  /** One-line statement of what a defect means, printed in reports. */
  describe: string;
  /**
   * Floor for `examined` on this check's fixtures. The meta gate asserts it.
   * Set it to the number of units the fixture genuinely contains, so a check
   * cannot pass the gate by inflating its own count.
   */
  minExamined: number;
  run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult>;
}

export const registry: Check[] = [];

export function register(check: Check): void {
  if (registry.some((c) => c.id === check.id)) {
    throw new Error(`duplicate check id: ${check.id}`);
  }
  registry.push(check);
}

/**
 * The cap on defect ROWS a single check may emit for one page at one viewport.
 *
 * Three is one row per failure mode, which is as many distinct modes as any check on this
 * site has. A check that wants a fourth is really asking to report instances, and instances
 * belong in `count`.
 */
export const MAX_DEFECT_ROWS = 3;
