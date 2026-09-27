import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
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

/**
 * targets.json `new_page_rule`. `page_types`, `built_before` and `excluded_prefix` are
 * scripts/family_rules.py's own NEW_FAMILY_PAGE_TYPES, BUILT_BEFORE_SYSTEM_GAPS and `_`
 * fixture prefix, pinned by tests/py/test_targets_coverage.py. `or_board_approved` is the one
 * condition this side adds (see isNewPage).
 */
export interface NewPageRule {
  page_types: string[];
  built_before: string[];
  excluded_prefix: string;
  or_board_approved: boolean;
}

interface TargetLike {
  slug: string;
  page_type: string;
}

/**
 * The board files (data/boards/<slug_file>.json stems) that carry an `approval` or an
 * `approval_previous`. pageboard.slug_file flattens `/` to `--`, so a city board is
 * `uk-locations--<key>`. A missing directory is an empty set; a file that does not parse is
 * not an approved board.
 */
export function approvedBoards(boardsDir: string): Set<string> {
  const out = new Set<string>();
  if (!existsSync(boardsDir)) return out;
  for (const f of readdirSync(boardsDir)) {
    if (!f.endsWith('.json')) continue;
    try {
      const b = JSON.parse(readFileSync(join(boardsDir, f), 'utf8')) as {
        approval?: unknown;
        approval_previous?: unknown;
      };
      if (b.approval || b.approval_previous) out.add(f.slice(0, -'.json'.length));
    } catch {
      /* not a board */
    }
  }
  return out;
}

/**
 * A project 5 page: a new-family page type, not one of the twelve pages built before the
 * system-gaps build, not a `_` fixture, AND either rebuilt from its board
 * (data/facts/rebuilt.json) or — when `or_board_approved` — carrying an approved board, so
 * the four promoted checks block from board approval on, i.e. on the page's very first build.
 * A migrated city page with neither (no board, not rebuilt) is not new: its body is still
 * WordPress markup, and it stays advisory.
 *
 * Key spellings: a city target's slug is its route (`uk-locations/<key>`); rebuilt.json holds
 * the bare key, and a board file is the route with `/` as `--` (pageboard.slug_file). The
 * route, its board-file spelling and the bare last segment are all tried.
 */
export function isNewPage(
  target: TargetLike,
  rule: NewPageRule,
  rebuilt: Set<string>,
  boards: Set<string> = new Set(),
): boolean {
  if (!rule.page_types.includes(target.page_type)) return false;
  const bare = target.slug.split('/').pop() ?? target.slug;
  const keys = [target.slug, bare];
  if (keys.some((k) => rule.built_before.includes(k))) return false;
  if (rule.excluded_prefix && keys.some((k) => k.startsWith(rule.excluded_prefix))) return false;
  if (keys.some((k) => rebuilt.has(k))) return true;
  return rule.or_board_approved && [target.slug.replace(/\//g, '--'), bare].some((k) => boards.has(k));
}

/** The severity a check carries on one target page. */
export function severityFor(
  check: { id: string; severity: Severity },
  target: TargetLike,
  promotions: Record<string, Promotion>,
  rule: NewPageRule,
  rebuilt: Set<string>,
  boards: Set<string> = new Set(),
): Severity {
  if (check.severity === 'blocking') return 'blocking';
  return promotions[check.id]?.scope === 'new-pages' && isNewPage(target, rule, rebuilt, boards)
    ? 'blocking'
    : 'advisory';
}
