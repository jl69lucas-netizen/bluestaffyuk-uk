// src/lib/formEndpoint.ts — the one form endpoint every enquiry and sign-up form posts to.
//
// Built from PUBLIC_FORMSPREE_ID, with a local '#contact' stub while the id is unset, so a dev
// build has no live endpoint and no id is ever committed (ContactFormKit.astro's note; spec §8).
// ContactFormKit and the city newsletter both read it here, so the two forms can never post to
// two places. `data-live` on a form carries the same fact to a client script.
export function formEndpoint(): { action: string; live: boolean } {
  const fid = import.meta.env.PUBLIC_FORMSPREE_ID || 'FORMSPREE_ID_PLACEHOLDER';
  const live = fid !== 'FORMSPREE_ID_PLACEHOLDER';
  return { action: live ? `https://formspree.io/f/${fid}` : '#contact', live };
}
