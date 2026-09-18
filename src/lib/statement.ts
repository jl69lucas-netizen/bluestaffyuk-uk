// src/lib/statement.ts — the statement-label vocabulary, in one place.
//
// `tests/render/checks/sem.ts::sem-statement-label-visible` accepts exactly three values in
// a `.stmt-label`'s `data-kind`, and anything else is a defect. The list therefore belongs
// somewhere both the kit and the pages that ship after it can import, not inside a kit
// component: src/components/kit/ is deleted by Task 19's prune, and the vocabulary is not.
//
// Adding a kind here is not enough on its own — the check's own array has to learn it too.
export type StatementKind = 'fact' | 'observed' | 'recommendation';

export const STATEMENT_KINDS: readonly StatementKind[] = ['fact', 'observed', 'recommendation'] as const;

/** The word a reader sees for each kind. */
export const LABELS: Record<StatementKind, string> = {
  fact: 'Fact',
  observed: 'Observed here',
  recommendation: 'Our recommendation',
};
