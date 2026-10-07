// src/lib/formErrors.ts — ties each required control of a form to its error line for assistive
// technology (Manchester's postmarked note and photo-at-the-edge form, Phase F Task 31).
//
// Native validation still decides; this only tells a screen reader what it decided. A control that
// fails is marked aria-invalid and described by its error line (the id its `data-err` names); once
// it is valid again both go. Pointing aria-describedby at a hidden line from the start would make
// every field announce an error it does not have (hardening log, Task 25), so the description is
// added only on failure. The error lines themselves are painted by CSS (`:user-invalid`, or the
// control's aria-invalid), so a reader without scripting still sees them.
export function wireFieldErrors(form: HTMLFormElement): void {
  form.querySelectorAll<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>('[data-err]').forEach((el) => {
    const mark = (bad: boolean) => {
      if (bad) {
        el.setAttribute('aria-invalid', 'true');
        el.setAttribute('aria-describedby', el.dataset.err!);
      } else {
        el.removeAttribute('aria-invalid');
        el.removeAttribute('aria-describedby');
      }
    };
    el.addEventListener('invalid', () => mark(true));
    const recheck = () => { if (el.hasAttribute('aria-invalid')) mark(!el.checkValidity()); };
    el.addEventListener('input', recheck);
    el.addEventListener('change', recheck);
  });
}
