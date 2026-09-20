// src/lib/headings.ts — AP-style Title Case for a rendered heading (spec §9 amendment 4b).
//
// WHY A FUNCTION AND NOT A HAND-TYPED HEADING. The breeder approves heading WORDING on the
// board; the CASE is presentation, and `rules/headings.md` fixes it for every H1–H6 on the
// site. A page that retyped its record's heading in Title Case would hold two spellings of
// one approved string, and the two would drift the first time a heading is re-approved. So
// the record keeps the wording it was signed off with and the page renders it through
// `titleCase()` — one caser, applied at the point of render.
//
// IT IS THE CHECKER'S OWN RULES, INVERTED. `scripts/page_hardening_scan.py::check_title_case`
// and `tests/render/checks/sem.ts::sem-title-case-headings` decide whether a heading passes;
// this decides what to write. The two must agree, so the small-word list, the acronym /
// number / domain / camelCase exemptions, the "force a capital after : ? !" rule and the
// binomial-genus exemption are transcribed from that checker rather than re-derived. An
// em dash does NOT force a capital (rules/headings.md), which falls out of the same test:
// only `:`, `?` and `!` set `force`.
//
// The checker never objects to a word that is capitalised where it need not be — it only
// reports a word that is lowercase where it must be capital. This caser is stricter than
// that in one direction on purpose: it also LOWERCASES a small word mid-title, because
// "Questions People Ask After Writing To Us" is the defect AP-style Title Case exists to
// avoid and nothing mechanical would catch it.

/** Lowercase mid-title, per rules/headings.md. Same list as the two checkers. */
const MINOR = new Set([
  'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
  'at', 'by', 'in', 'of', 'on', 'to', 'as', 'vs', 'per', 'via',
]);

/** A binomial's epithet is correctly lowercase — "Canis familiaris". Mirrors
 *  SPECIES_GENERA in scripts/page_hardening_scan.py; keep the two in step. */
const GENERA = new Set(['Canis']);

/** The word with its surrounding punctuation stripped, exactly as the checker reads it. */
const core = (w: string) => w.replace(/[^\w'-]/g, '');

/** True for a token the caser must not touch: empty, a number or price, a domain, an
 *  acronym or brand already in caps (UK, KC, DEFRA, BVA, DNA, SBT), or camelCase. */
const untouchable = (w: string) => {
  const c = core(w);
  return !c || /^\d/.test(c) || w.includes('.') || c === c.toUpperCase() || /[a-z][A-Z]/.test(c);
};

/** Upper-case the token's FIRST letter, leaving any leading punctuation in place. It is the
 *  first letter and not the first lowercase one: "Thank" would otherwise become "THank". */
const upperFirst = (s: string) => s.replace(/\p{L}/u, (m) => m.toUpperCase());

/** Hyphenated compounds capitalise EACH part — "Home-Raised", "KC-Registered" — and a part
 *  that is itself untouchable ("24" in "24-48", "KC" in "KC-registered") is left alone. */
const capitalise = (w: string) =>
  w.split('-').map((part) => (untouchable(part) ? part : upperFirst(part))).join('-');

/**
 * `text` rendered in AP-style Title Case.
 *
 * Whitespace is normalised to single spaces, because a heading written across two lines of
 * JSX is one heading and the checker reads it that way too.
 */
export function titleCase(text: string): string {
  const words = text.replace(/\s+/g, ' ').trim().split(' ');
  let force = true; // the first word, and any word following one that ends in : ? !
  return words
    .map((w, i) => {
      const c = core(w);
      const prev = i ? core(words[i - 1]) : '';
      const nextForce = /[:?!]$/.test(w);
      // A species epithet after its genus, and every untouchable token, pass through whole.
      if ((GENERA.has(prev) && c !== '' && c === c.toLowerCase()) || untouchable(w)) {
        force = nextForce;
        return w;
      }
      const mustCap = force || i === 0 || i === words.length - 1 || !MINOR.has(c.toLowerCase());
      force = nextForce;
      return mustCap ? capitalise(w) : w.toLowerCase();
    })
    .join(' ');
}
