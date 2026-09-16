import { register, type CheckResult, type CheckContext, type Defect } from '../lib/registry.js';
import type { Page } from '@playwright/test';

/**
 * FORM family. Ported from CAG 2026-09-16, where it was added after the breeder found
 * inquiries "still going to the MFS email": 14 forms carried data-netlify with no action
 * (a Netlify handler that does not exist on Cloudflare Pages — the browser POSTed to the
 * page itself and the mail vanished), two POSTed to a /thank-you/ page that did not exist,
 * one GET to /contact-us/, one to a retired Formspree ID. No invariant covered any of it.
 * It is judged in the browser, not from source: `checkValidity()` on the untouched form is
 * the one honest test that `required` is live on every control the contract names.
 *
 * `examined === 0` is a legitimate, silent state on a page that carries no inquiry form BY
 * DESIGN — on BSUK that is every page except the contact page, because ContactForm.astro
 * renders on `uk-blue-staffy-breeders-contact` alone (verified against dist/ 2026-09-16:
 * 1 of 17 targets contains a <form> at all). On a page that IS supposed to carry one, zero
 * forms examined is itself the defect (the page lost its form, or the form is a `/search/`
 * form in disguise), and this check reports it as one row instead of passing silently — a
 * check that returns clean on zero is indistinguishable from a check that never ran.
 *
 * `INQUIRY_FORM_SLUGS` is a fact about today's page inventory, not a permanent property of
 * any slug pattern — the day a second page grows an inquiry form it must be added here or
 * this check will silently stop looking at it. It is the reason the exemption is written as
 * an explicit allow-list rather than a regex: a regex over BSUK's slugs would have to
 * enumerate the 16 pages that DON'T carry a form, and would silently exempt the 17th.
 *
 * NOT changed in the port, deliberately: FORM_ENDPOINT and the seven-field screening
 * contract below are CAG's, and tests/render/fixtures/{known_good,known_broken}/
 * form-inquiry-contract.html are built against exactly them. BSUK's own screening contract
 * has not been decided (ContactForm.astro ships name/email/phone/location/puppy/message and
 * posts to `#contact` until PUBLIC_FORMSPREE_ID is set), so every row this check emits on
 * the real contact page is Foundation BASELINE, not a regression. Rewriting the contract
 * here without rewriting the fixtures would leave the new branch fixture-untested, which is
 * the one thing this harness exists to refuse.
 */
const FORM_ENDPOINT = 'https://formspree.io/f/xrejpnvn';

/** Slugs whose built page carries a real (non-search) inquiry form. See the note above. */
const INQUIRY_FORM_SLUGS = new Set(['uk-blue-staffy-breeders-contact']);

export function fieldChecksSkipped(slug: string): boolean {
  return !INQUIRY_FORM_SLUGS.has(slug);
}
export function contractFor(slug: string): 'full' | 'short' | 'none' {
  if (fieldChecksSkipped(slug)) return 'none';
  return slug.startsWith('blog/') ? 'short' : 'full';
}
export function formExpected(slug: string, _pageType: string): boolean {
  return INQUIRY_FORM_SLUGS.has(slug);
}

register({
  id: 'form-inquiry-contract',
  family: 'FORM',
  severity: 'advisory',
  describe:
    'every non-search form POSTs to the one Formspree endpoint; every in-scope inquiry form carries the seven screening fields, each required, and refuses to submit empty',
  // known_good carries one inquiry form + one newsletter (the search form is skipped) → 2.
  minExamined: 2,
  async run(page: Page, viewport: number, ctx: CheckContext): Promise<CheckResult> {
    const r = await page.evaluate(
      ({ endpoint, contract }) => {
        const ALL: [string, RegExp][] = [
          ['confirm number', /^(phone|cell|mobile)[_-]?confirm$/],
          ['confirm email', /^email[_-]?confirm$/],
          ['resale screening', /^resale_screening$/],
          ['surrender history', /^surrender_history$/],
          ['experience', /^experience$/],
          ['delivery', /^delivery(_method)?$/],
          ['message', /^(message|msg)$/],
        ];
        const SHORT = ['confirm number', 'confirm email', 'resale screening', 'surrender history'];
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
            const hits = controls.filter((c) => rx.test(c.name));
            if (!hits.length || !hits.some((c) => c.required)) formIssues.push(name);
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
    if (r.examined === 0 && formExpected(ctx.slug, ctx.pageType)) {
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
