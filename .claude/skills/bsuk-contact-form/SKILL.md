---
name: bsuk-contact-form
description: Audits, fixes and verifies every enquiry and newsletter form on BlueStaffyUK against the field contract and the single Formspree endpoint (`PUBLIC_FORMSPREE_ID`, read from the environment, never committed). Use for "add a field to the forms", "enquiries go to the wrong address", "check every contact form", or after any page build that renders a <form>.
allowed-tools: [Read, Write, Bash]
---

# BSUK Contact Form & Newsletter Skill

Re-based for BlueStaffyUK 2026-09-16. The shape is the source repo's; every field, file and
gate below is BSUK's own.

## Golden Rule
> Use Claude Code and the Playwright CLI first. Measure `dist/`, never source.
> A gate's PASS is only as good as its examined count — read it every time.

---

## The one endpoint

| Item | Value |
|---|---|
| Every form on the site (enquiry AND newsletter) | `action="https://formspree.io/f/${PUBLIC_FORMSPREE_ID}" method="POST"` |
| Where the id comes from | the `PUBLIC_FORMSPREE_ID` environment variable, read at call time — `scripts/form_contract_audit.py` refuses to run when it is unset, and Task 18 sets it. **Never** a committed file, never a report, never stdout |
| Pre-launch action | `#contact` — `src/components/kit/ContactFormKit.astro` renders `action="#contact"` (and `data-live="false"`) when `PUBLIC_FORMSPREE_ID` is unset, and the live endpoint only when it is set. A build without it must not POST anywhere |
| Honeypot | `<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">`, hidden off-screen |
| Success redirect | `<input type="hidden" name="_next" value="https://SITE_URL_PLACEHOLDER/thank-you-blue-staffy-puppies-journey/">` |
| Subject | `<input type="hidden" name="_subject" value="New Blue Staffy enquiry">` |

**Wrong on sight** — `scripts/form_contract_audit.py` fails the build on each:
- any endpoint that is not the one id — an enquiry that reaches somebody else's inbox is the
  worst possible defect on this site.
- `data-netlify="true"` / `netlify-honeypot` / `form-name` / `bot-field` — no handler exists
  (hosting is NOT FETCHED until project 6); the browser POSTs to the page and the mail vanishes.
- a `GET` form, or an `action` pointing at a route rather than the endpoint.

## The field contract

`REQUIRED` in `scripts/form_contract_audit.py` is the contract; the component is
`src/components/kit/ContactFormKit.astro`.

| # | Label | name | control |
|---|---|---|---|
| 1 | Your name | `name` | text, **required** |
| 2 | Email | `email` | email, **required** |
| 3 | Phone | `phone` | tel, optional |
| 4 | Town or postcode | `location` | text, optional |
| 5 | Which puppy? | `puppy` | select, **required** — options come from `data/puppies.json`, never typed |
| 6 | Message | `message` | textarea, **required** |

The pup list is data, not markup: a pup added to `data/puppies.json` appears in the select on
the next build, and a pup marked sold there is still selectable only if the page still offers
it. Never hardcode a name or a price into the form.

**Two optional additions (Manchester, Phase F Task 31; ContactFormKit `layout="compact"`)** — a
`handover` radio pair whose values are exactly `collect` and `delivery`, and, beside `waiting-list`,
the puppy options `any-boy` / `any-girl` (offered only while the litter has two or more of that sex).
`scripts/form_contract_audit.py` (`value_problems`, `HANDOVER_VALUES`, `puppy_values()`) and its
render twin hold these VALUES on every inquiry form, whatever the page's field contract: a handover
option that does not exist, or a puppy option that is no `data/puppies.json` slug and none of the
three named choices, is a problem.

**Delivery, where a form asks about it** — the two options are the only two that exist:
**UK home delivery £200–£350 by distance, by DEFRA-approved transport**, and **collection in
person from Carlisle**. It is a band, never a single figure, and the £500 deposit (`deposit_gbp`, never plainly "refundable") is stated
wherever the band is (`rules/puppies.md` `delivery-band-on-every-card`).

## Presentation layer

- **A one-line why above any screening question** — e.g. "A Staffordshire Bull Terrier lives
  12 to 14 years, so we ask every buyer the same few questions before we place a puppy."
  The lifespan figure is 12–14 and nothing else.
- **Sentence-case question legends** — never a 12 px uppercase label for a question. Short
  field labels (Name, Email) keep the page's own label style.
- **44 px targets** — every option pill or radio card has `min-height:44px`.
- **Native validation is the floor.** Any progressive enhancement must leave the form working,
  and every required control focusable, with JavaScript off.

## Traps this contract has already sprung

1. **A red `*` inside a grid label drops onto its own row.** A `display:grid` label that wraps
   its own input renders the text and the star as two rows. Wrap text + star in one span.
   Only a screenshot shows this — the audit and `checkValidity()` both pass it.
2. **`opacity` on description text** trips `scripts/page_hardening_scan.py`
   `opacity-dims-text-contrast`. Use an explicit colour on an explicit ground.
3. **A required control must be focusable.** `display:none` on a required radio blocks submit
   with no message ("An invalid form control … is not focusable"). Hide visually (1 px,
   opacity 0), never `display:none`.
4. **Radio/card inputs inherit the family's text-input rule** (width, padding, border). End
   every form's CSS with a reset: `width:auto;padding:0;border:0;background:none;box-shadow:none`.
5. **An input without an explicit width uses its `size` default** and overflows a narrow
   column. `ContactFormKit.astro` sets `width:100%` with `box-sizing:border-box` for exactly this.

## Gates — run them in this order

```bash
npm run -s build
python3 scripts/form_contract_audit.py --json /tmp/bsuk-forms.json   # every page in dist/, exit 1 on any miss
npm run test:render:pages                                            # harness, incl. the FORM family
```

The source repo's two browser probes (a real-browser submit proof and a group-title gap probe)
were **not ported — source repo only**. Until an equivalent exists here, open at least one
375 px screenshot per form family by hand: trap 1 is invisible to every mechanical gate.

Form text is UI copy shared by design, so the duplicate gate skips it:
`scripts/dup_content_audit.py` excludes `form`. Before that exclusion existed, the harness read
`<main>` with forms included and flagged the fixed contract questions as sibling crossovers —
two gates, one input, different verdicts.

Cross-check the audit's `forms examined` independently — if the numbers differ, the audit
skipped something:

```bash
echo $(( $(find dist -name index.html -exec cat {} + | grep -o '<form' | wc -l) - $(find dist -name index.html -exec cat {} + | grep -o 'action="/search/"' | wc -l) ))
```

## After a form change

Build → the gates → commit. There is no push and no deploy until project 6, and no URL is
submitted anywhere until then (`.claude/skills/bsuk-indexing/SKILL.md`).

## Reporting Format

```
FORM CONTRACT — https://SITE_URL_PLACEHOLDER
forms examined: N (enquiry I, in-scope S, newsletter L)   cross-check: N ✓
audit: PASS | FAIL (rows…)
screens eyeballed: <one per family>
endpoint: PUBLIC_FORMSPREE_ID (value never printed)
```
