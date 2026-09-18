// src/components/kit/_variant.ts — shared by every kit component during project 3.
// Task 19 (prune) deletes this file together with the `variant` prop.
export type Variant = 'a' | 'b' | 'c' | 'd' | 'e';
export const VARIANTS: readonly Variant[] = ['a', 'b', 'c', 'd', 'e'] as const;
export const isVariant = (v: unknown): v is Variant => typeof v === 'string' && (VARIANTS as readonly string[]).includes(v);
