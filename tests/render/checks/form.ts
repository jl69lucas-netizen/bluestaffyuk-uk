import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { register, type CheckResult, type CheckContext, type Defect } from '../lib/registry.js';
import type { Page } from '@playwright/test';

/**
 * FORM family. Ported from the source project 2026-09-16, where it was added after the
 * breeder found inquiries "still going to the MFS email": 14 forms carried data-netlify
 * with no action (a Netlify handler that does not exist on Cloudflare Pages — the browser
 * POSTed to the page itself and the mail vanished), two POSTed to a /thank-you/ page that
 * did not exist, one GET to /contact-us/, one to a retired Formspree ID. No invariant
 * covered any of it. It is judged in the browser, not from source: `checkValidity()` on the
 * untouched form is the one honest test that `required` is live on every control the
 * contract names.
 *
 * `examined === 0` is a legitimate, silent state on a page that carries no inquiry form BY
 * DESIGN — on BSUK that is every page except the contact page, because ContactForm.astro
 * renders on `uk-blue-staffy-breeders-contact` alone (verified against dist/ 2026-09-16:
 * 1 of 17 targets contains a <form> at all). On a page that IS supposed to carry one, zero
 * forms examined is itself the defect (the page lost its form, or the form is a `/search/`
 * form in disguise), and this check reports it as one row instead of passing silently — a
 * check that returns clean on zero is indistinguishable from a check that never ran.
 *
 * Two different questions, two different sources, deliberately:
 *   - WHICH CONTRACT a page's inquiry forms must satisfy is routed by data/page-map.json's
 *     `kind` (rich → full, blog → short, location → none), read at module load, with the
 *     same slug fallback the Python uses for a page absent from the map. scripts/
 *     form_contract_audit.py routes identically; a hand-kept slug list here would drift
 *     from it the first time a page is added, and the two gates would then judge the same
 *     form by different contracts.
 *   - WHETHER A PAGE MUST CARRY A FORM AT ALL is `INQUIRY_FORM_SLUGS`, which has no Python
 *     equivalent because zero-examined is a harness-only concept (the Python audit reads
 *     whatever forms exist). It is a fact about today's page inventory, not a property of
 *     any slug pattern — the day a second page grows an inquiry form it must be added here
 *     or the zero-examined defect will stop firing for it. It is an explicit allow-list
 *     rather than a regex because a regex would have to enumerate the 16 pages that DON'T
 *     carry a form, and would silently exempt the 17th.
 *
 * The contract below is BSUK's own, read off the built contact page and held in lock-step
 * with scripts/form_contract_audit.py: same six controls, same required/optional split,
 * same `puppy` <select> with the `collection-glasgow` option, same two hidden fields, same
 * `_gotcha` exclusion. Two gates that disagree about what an inquiry form is would give
 * different verdicts on the same page, which is the one failure this pair exists to refuse.
 */
/**
 * Read from the environment, never hard-coded. The id is a credential-adjacent fact that
 * lives in .env (spec §8). Throwing on unset is the point: an empty id makes `action !==
 * endpoint` true on every form, which reads as "every form is broken", or — worse, if the
 * comparison were relaxed — as "every form is fine". A gate that cannot tell those apart
 * must refuse to run. scripts/form_contract_audit.py refuses identically.
 */
const FORMSPREE_ID = process.env.PUBLIC_FORMSPREE_ID;
if (!FORMSPREE_ID) {
  throw new Error(
    'PUBLIC_FORMSPREE_ID is unset — the FORM family cannot judge an endpoint it does not ' +
      'know. Set it in .env (see .env.example) and re-run.',
  );
}
const FORM_ENDPOINT = `https://formspree.io/f/${FORMSPREE_ID}`;

/** Slugs whose built page carries a real (non-search) inquiry form. See the note above. */
const INQUIRY_FORM_SLUGS = new Set(['uk-blue-staffy-breeders-contact']);

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
/** Mirrors KIND_CONTRACT in scripts/form_contract_audit.py. */
const KIND_CONTRACT: Record<string, 'full' | 'short' | 'none'> = {
  rich: 'full',
  blog: 'short',
  location: 'none',
};
const HUBS = ['available-puppies', 'uk-locations', 'blog'];
/** {slug: kind} from data/page-map.json; empty when the map is unreadable, in which case
 *  every page falls back to the slug heuristic — same degradation as the Python. */
const PAGE_KINDS: Record<string, string> = (() => {
  try {
    const pages = JSON.parse(
      readFileSync(join(REPO, 'data/page-map.json'), 'utf8'),
    ).pages as { url: string; kind: string }[];
    return Object.fromEntries(
      pages.map((p) => [p.url.replace(/^\/+|\/+$/g, '') || 'index', p.kind]),
    );
  } catch {
    return {};
  }
})();

export function contractFor(slug: string): 'full' | 'short' | 'none' {
  const kind = PAGE_KINDS[slug];
  if (kind && kind in KIND_CONTRACT) return KIND_CONTRACT[kind];
  // Fallback for a page absent from the map (a hub, or a page built after the map was last
  // generated): today's slug heuristic, character for character the Python's.
  if (/^uk-locations\//.test(slug) || HUBS.includes(slug)) return 'none';
  if (slug.startsWith('blog/')) return 'short';
  return 'full';
}
export function fieldChecksSkipped(slug: string): boolean {
  return contractFor(slug) === 'none';
}
export function formExpected(slug: string): boolean {
  return INQUIRY_FORM_SLUGS.has(slug);
}

register({
  id: 'form-inquiry-contract',
  family: 'FORM',
  severity: 'advisory',
  describe:
    'every non-search form POSTs to the one Formspree endpoint; every in-scope inquiry form carries the six BSUK fields with name/email/puppy/message required, the honeypot and both hidden fields, and refuses to submit empty',
  // known_good carries one inquiry form + one newsletter (the search form is skipped) → 2.
  minExamined: 2,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    const r = await page.evaluate(
      ({ endpoint, contract }) => {
        const ALL: [string, RegExp][] = [
          ['name', /^name$/],
          ['email', /^email$/],
          ['phone', /^phone$/],
          ['location', /^location$/],
          ['puppy', /^puppy$/],
          ['message', /^(message|msg)$/],
        ];
        // As BUILT (dist/uk-blue-staffy-breeders-contact/index.html, 2026-09-16): name,
        // email, puppy and message carry `required`; phone and location do not, by design.
        // Demanding `required` on all six would report the shipped page as broken and teach
        // the next agent to add a constraint the breeder did not ask for.
        const REQUIRED = ['name', 'email', 'puppy', 'message'];
        const HIDDEN = ['_next', '_subject'];
        // Spec §5: the puppy control is a <select> carrying the Glasgow collection choice.
        const PUPPY_OPTION = 'collection-glasgow';
        const SHORT = ['name', 'email', 'message'];
        const KEYS = contract === 'short' ? ALL.filter(([n]) => SHORT.includes(n)) : ALL;
        const fieldsApply = contract !== 'none';
        const wrongEndpoint: string[] = [];
        const missing: string[] = [];
        let missingCount = 0;
        const submitsEmpty: string[] = [];
        let examined = 0;
        Array.from(document.querySelectorAll('form')).forEach((f, i) => {
          const action = f.getAttribute('action') || '';
          if (action.startsWith('/search')) return;
          examined++;
          const subject = f.querySelector('input[name="_subject"]') as HTMLInputElement | null;
          const label = `form#${i + 1}(${
            f.getAttribute('id') ||
            f.getAttribute('aria-label') ||
            subject?.value ||
            f.getAttribute('name') ||
            f.className.split(' ')[0] ||
            'unnamed'
          })`;
          const netlify =
            f.hasAttribute('data-netlify') ||
            f.hasAttribute('netlify-honeypot') ||
            !!f.querySelector('[name="form-name"],[name="bot-field"]');
          if (action !== endpoint || netlify || (f.getAttribute('method') || 'get').toLowerCase() !== 'post') {
            wrongEndpoint.push(`${label} action="${action || '(none)'}"${netlify ? ' +netlify' : ''}`);
          }
          // Same classification as scripts/form_contract_audit.py: a NEWSLETTER is a form whose
          // visible controls are exactly one email box; anything else is an inquiry form. Two
          // gates must agree on what an inquiry form is (reference_same_input_different_verdict).
          const controls = Array.from(f.querySelectorAll('input,select,textarea')) as HTMLInputElement[];
          const visible = controls.filter((c) => c.type !== 'hidden' && c.name !== '_gotcha');
          const isInquiry = !(visible.length === 1 && visible[0].type === 'email');
          if (!isInquiry) {
            // Same parity check as form_contract_audit.py: a newsletter's one real control
            // must carry a `name`, or Formspree receives an unlabeled value and drops it.
            if (!visible[0].name) {
              wrongEndpoint.push(`${label}: email input has no name — Formspree receives nothing`);
            }
            return;
          }
          if (!fieldsApply) return;
          const formIssues: string[] = [];
          for (const [name, rx] of KEYS) {
            const hits = controls.filter((c) => c.name && rx.test(c.name));
            if (!hits.length) {
              formIssues.push(`${name} absent`);
              continue;
            }
            if (REQUIRED.includes(name) && !hits.some((c) => c.required)) {
              formIssues.push(`${name} not required`);
            }
            if (name === 'puppy') {
              const sels = hits.filter(
                (c) => c.tagName.toLowerCase() === 'select',
              ) as unknown as HTMLSelectElement[];
              if (!sels.length) formIssues.push('puppy must be a <select> (spec §5)');
              else if (
                !sels.some((sel) =>
                  Array.from(sel.options).some((o) => o.value === PUPPY_OPTION),
                )
              ) {
                formIssues.push(`puppy select missing the ${PUPPY_OPTION} option (spec §5)`);
              }
            }
          }
          // Without _next and _subject Formspree has no redirect and no reply subject.
          for (const h of HIDDEN) {
            if (!controls.some((c) => c.name === h)) formIssues.push(`hidden field ${h} absent`);
          }
          if (formIssues.length) {
            missingCount += formIssues.length;
            missing.push(`${label}: ${formIssues.length} missing/optional (${formIssues.join(', ')})`);
          }
          if (f.checkValidity()) submitsEmpty.push(label);
        });
        return { examined, wrongEndpoint, missing, missingCount, submitsEmpty };
      },
      { endpoint: FORM_ENDPOINT, contract: contractFor(ctx.slug) },
    );
    const defects: Defect[] = [];
    if (r.examined === 0 && formExpected(ctx.slug)) {
      defects.push({
        checkId: 'form-inquiry-contract', family: 'FORM' as const, viewport, count: 1,
        message: `no non-search form on ${ctx.slug} (${ctx.pageType}) — nothing to judge`,
      });
    }
    if (r.wrongEndpoint.length) {
      defects.push({ checkId: 'form-inquiry-contract', family: 'FORM' as const, viewport, count: r.wrongEndpoint.length,
        message: `not posting to ${FORM_ENDPOINT}: ${r.wrongEndpoint.slice(0, 4).join(' | ')}` });
    }
    if (r.missing.length) {
      defects.push({ checkId: 'form-inquiry-contract', family: 'FORM' as const, viewport, count: r.missingCount,
        message: `screening fields: ${r.missing.slice(0, 6).join(' | ')}` });
    }
    if (r.submitsEmpty.length) {
      defects.push({ checkId: 'form-inquiry-contract', family: 'FORM' as const, viewport, count: r.submitsEmpty.length,
        message: `checkValidity() is true on the untouched form (no live required constraint, or a control is pre-filled/pre-checked): ${r.submitsEmpty.join(' | ')}` });
    }
    return { examined: r.examined, defects };
  },
});
