// src/lib/statement.ts — the statement-label vocabulary, in one place.
//
// `tests/render/checks/sem.ts::sem-statement-label-visible` accepts exactly three values in
// a `.stmt-label`'s `data-kind`, and anything else is a defect. The list therefore belongs
// somewhere both the kit and the pages that ship after it can import, rather than inside
// any one kit component: the pages project 4 builds need the same three words, and a
// vocabulary owned by a component is a vocabulary that moves when the component does.
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

/** A statement label a city component sets on its own line beside the text it labels
 *  (src/components/kit/StatementLine.astro): the kind, and a few words on what it rests on. */
export interface Statement {
  kind: StatementKind;
  note?: string;
}
