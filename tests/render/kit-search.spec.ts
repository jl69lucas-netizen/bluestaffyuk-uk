import { test, expect, type Page } from '@playwright/test';
import { checkDistFreshness } from './lib/freshness.js';

/**
 * The header search combobox, DRIVEN — in a browser, against the built page.
 *
 * Everything else that covers this widget reads text. `tests/py/test_design_components.py`
 * greps the built HTML for the roles and the component source for the key names, which
 * cannot tell a handler that moves the highlight from one that names the key and returns;
 * `meta.spec.ts` never loads a real page at all. So the two failures this widget has
 * actually had — a mouse-chosen result vanishing before the click landed, and
 * `aria-expanded="true"` over a panel with nothing in it — were both invisible to the
 * committed tests. This file types, arrows, presses Enter and clicks.
 *
 * SERVED LIKE THE REST OF THE SUITE. playwright.config.ts already stands `dist/` up on
 * SITE_PORT as the default `baseURL` for pages.spec.ts, so the page here is reached by the
 * relative path `/kit-preview/` and no server is started by this file.
 *
 * BROWSER COVERAGE: chromium only. The config's three projects (vp375/vp768/vp1280) differ
 * in VIEWPORT, not in engine, and no webkit project is installed — so the Safari focusout
 * path this file exists to protect is exercised here only in the shape every engine shares
 * (pointerdown, then a deferred focusout that asks the document where focus went). Add a
 * webkit project to playwright.config.ts and this file runs there unchanged.
 *
 * WHY kit-preview: no real page mounts the kit until project 4 (build 4). kit-preview is
 * the only built page carrying SiteHeaderKit, and it is noindex.
 */

const PREVIEW = '/kit-preview/';
const QUERY = 'rom';
/** `rom` matches exactly one row in the built index: the Roman puppy page. */
const FIRST_HREF = '/available-puppies/roman/';
const NO_MATCH = 'zzzz';

test.beforeAll(() => {
  // Same refusal as pages.spec.ts, same reason: a green run against yesterday's dist/ is a
  // measurement of nothing. Read-only, so re-running it per worker is harmless.
  const f = checkDistFreshness();
  if (!f.fresh) throw new Error(`RENDER HARNESS REFUSES TO MEASURE: ${f.reason}`);
});

/**
 * Below 768px the single form is hidden until the drawer is open — one form moved by CSS,
 * never a second copy (spec §11 amendment 3b). So on the narrow projects the drawer is
 * opened first, which also means this file proves the drawer search is reachable at all,
 * not merely that it exists in the markup.
 */
async function openSearch(page: Page, viewport: number) {
  await page.goto(PREVIEW);
  if (viewport < 768) await page.locator('details.drawer > summary').click();
  const input = page.locator('#site-search-q');
  await expect(input, 'the one search input must be reachable at this width').toBeVisible();
  return input;
}

const vp = (testInfo: { project: { use: { viewport?: { width: number } | null } } }) =>
  testInfo.project.use.viewport!.width;

test.describe('the header search combobox, driven in a browser', () => {
  test('typing opens a listbox and says so in aria-expanded', async ({ page }, testInfo) => {
    const input = await openSearch(page, vp(testInfo));
    await input.fill(QUERY);

    const list = page.locator('#site-search-results');
    await expect(list, 'the results panel must be shown').toBeVisible();
    await expect(input).toHaveAttribute('aria-expanded', 'true');
    await expect(list).toHaveAttribute('role', 'listbox');
    await expect(list.locator('[role="option"]')).toHaveCount(1);
    await expect(page.locator('#site-search-status')).toHaveText('1 result.');
  });

  test('ArrowDown points aria-activedescendant at the first option', async ({ page }, testInfo) => {
    const input = await openSearch(page, vp(testInfo));
    await input.fill(QUERY);
    await expect(page.locator('#site-search-results [role="option"]')).toHaveCount(1);

    // Nothing is active until a key is pressed: the first Enter must submit the form and
    // reach /search/, not open whichever result happened to be first.
    await expect(input, 'no option is active before ArrowDown').not.toHaveAttribute(
      'aria-activedescendant',
      /./,
    );

    await input.press('ArrowDown');
    const first = page.locator('#site-search-results [role="option"]').first();
    const id = await first.getAttribute('id');
    expect(id, 'the option must carry the id the input will point at').toBe('site-search-option-0');
    await expect(input).toHaveAttribute('aria-activedescendant', id!);
    await expect(first).toHaveAttribute('aria-selected', 'true');
  });

  test('Enter on the highlighted option navigates to its href', async ({ page }, testInfo) => {
    const input = await openSearch(page, vp(testInfo));
    await input.fill(QUERY);
    await expect(page.locator('#site-search-results [role="option"]')).toHaveCount(1);
    await input.press('ArrowDown');
    await input.press('Enter');

    await page.waitForURL(`**${FIRST_HREF}`);
    expect(new URL(page.url()).pathname).toBe(FIRST_HREF);
  });

  /**
   * THE SAFARI PATH, in the shape every engine shares.
   *
   * A pointer going down inside the panel used to move focus off the input; the focusout
   * that followed emptied the list, and the click arrived at nothing. The fix is two-sided
   * — `preventDefault()` on the list's pointerdown so focus never moves, and a focusout
   * deferred one tick so the decision is taken from `document.activeElement` rather than
   * from a `relatedTarget` Safari reports as null. A real mouse click is the only thing
   * that exercises either, which is why this is not `link.click()` in page script.
   */
  test('clicking a result with the mouse navigates', async ({ page }, testInfo) => {
    const input = await openSearch(page, vp(testInfo));
    await input.fill(QUERY);
    const link = page.locator('#site-search-results [role="option"] a').first();
    await expect(link).toBeVisible();

    await link.click();

    await page.waitForURL(`**${FIRST_HREF}`);
    expect(new URL(page.url()).pathname).toBe(FIRST_HREF);
  });

  test('a query with no matches hides the panel and says so politely', async ({ page }, testInfo) => {
    const input = await openSearch(page, vp(testInfo));
    await input.fill(NO_MATCH);

    const status = page.locator('#site-search-status');
    await expect(status).toHaveText(`No results for ${NO_MATCH}.`);
    // `aria-expanded` describes the PANEL. An expanded combobox over an empty listbox
    // promises a reader somewhere to arrow into and hands them nothing.
    await expect(page.locator('#site-search-results')).toBeHidden();
    await expect(input).toHaveAttribute('aria-expanded', 'false');
    await expect(input).not.toHaveAttribute('aria-activedescendant', /./);
  });

  test('dropping back below the minimum clears the count as well as the panel', async ({ page }, testInfo) => {
    const input = await openSearch(page, vp(testInfo));
    await input.fill(QUERY);
    await expect(page.locator('#site-search-status')).toHaveText('1 result.');

    await input.fill('r');
    await expect(page.locator('#site-search-results')).toBeHidden();
    await expect(input).toHaveAttribute('aria-expanded', 'false');
    // A stale "1 result." in a polite region is re-announced the next time it changes.
    await expect(page.locator('#site-search-status')).toHaveText('');
  });
});
