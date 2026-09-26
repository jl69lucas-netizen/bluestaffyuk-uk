import type { Severity } from './registry.js';

/**
 * One row of targets.json `promotions`: the evidence that a check may fail a run.
 *
 * `all` — blocking everywhere; the check's registered severity is `blocking`.
 * `new-pages` — the check stays `advisory` in the registry and blocks on the project 5 pages
 * only (see isNewPage), so the twelve frozen pages and the migrated bodies keep reporting
 * without failing while every new page is held to the rule from its first build.
 */
export interface Promotion {
  scope: 'all' | 'new-pages';
  since: string;
  cluster_cleared: string;
  false_reports: number;
}

/** targets.json `new_page_rule` — scripts/family_rules.py's own two constants, pinned by pytest. */
export interface NewPageRule {
  page_types: string[];
  built_before: string[];
}

interface TargetLike {
  slug: string;
  page_type: string;
}

/**
 * A project 5 page: a new-family page type, rebuilt from its board (data/facts/rebuilt.json)
 * and not one of the twelve pages built before the system-gaps build. A city target's slug is
 * its route (`uk-locations/<key>`) while rebuilt.json holds the bare key, so both are tried.
 * A migrated page that has not been rebuilt is not new: its body is still WordPress markup.
 */
export function isNewPage(target: TargetLike, rule: NewPageRule, rebuilt: Set<string>): boolean {
  if (!rule.page_types.includes(target.page_type)) return false;
  const keys = [target.slug, target.slug.split('/').pop() ?? target.slug];
  return keys.some((k) => rebuilt.has(k)) && !keys.some((k) => rule.built_before.includes(k));
}

/** The severity a check carries on one target page. */
export function severityFor(
  check: { id: string; severity: Severity },
  target: TargetLike,
  promotions: Record<string, Promotion>,
  rule: NewPageRule,
  rebuilt: Set<string>,
): Severity {
  if (check.severity === 'blocking') return 'blocking';
  return promotions[check.id]?.scope === 'new-pages' && isNewPage(target, rule, rebuilt)
    ? 'blocking'
    : 'advisory';
}
