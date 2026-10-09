// src/lib/ctas.ts — a board record's calls to action, as the breeder picked them (working rule 12,
// CTAs included, 2026-10-08; scripts/cta_rules.py is the record's side). A page renders
// <CtaButton {...cta('hero')} /> and never types a button's words or style: both come off the
// approved board. Like assets.ts, it THROWS on a slot the record lacks or the breeder has not
// picked, so a missing choice is a named build error rather than a default nobody approved.
import type { CtaStyle } from '../components/kit/CtaButton.astro';

export interface CtaOption {
  id: 'a' | 'b' | 'c';
  text: string;
  style: CtaStyle;
  sub?: string;
  tag?: string;
}
export interface CtaSlot {
  slot: string;
  section: string;
  type: 'browse' | 'ask' | 'ask-about-pup' | 'submit' | 'tool';
  target?: string;
  options: CtaOption[];
}
export interface CtaSource {
  meta?: { slug?: string } | null;
  ctas?: readonly CtaSlot[];
  approval?: { picks?: Record<string, string> } | null;
}

/** The CtaButton props for one slot: the picked option's text and style, the slot's target. */
export function pickedCtas(record: CtaSource) {
  const who = record.meta?.slug ?? 'board record';
  return (slot: string) => {
    const s = (record.ctas ?? []).find((x) => x.slot === slot);
    if (!s) throw new Error(`${who}: the board has no CTA slot ${slot}`);
    const pick = record.approval?.picks?.[`cta:${slot}`];
    const o = s.options.find((x) => x.id === pick);
    if (!o) throw new Error(`${who}: CTA slot ${slot} has no approved pick`);
    return {
      text: o.text,
      style: o.style,
      sub: o.sub,
      tag: o.tag,
      ...(s.type === 'submit' ? { submit: true } : { href: s.target }),
    };
  };
}
