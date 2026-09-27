/* Component canvas harness: node run.cjs <canvas.html> <fake.js>. Prints "RESULT {json}", or
   "SKIP <reason>" when Playwright or its browser is missing. Reuses the answer board's fake
   runtime (tests/py/fixtures/answer_board/harness/fake.js). Driven by
   tests/py/test_build_component_canvas.py::test_the_client_in_a_browser_against_a_fake_db. */
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) {
  try { ({ chromium } = require("@playwright/test")); } catch (e2) { console.log("SKIP no playwright"); process.exit(0); }
}
const [, , PAGE, FAKE] = process.argv;

async function open(browser, seed, noRuntime) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.addInitScript(({ seed }) => { window.__seed = seed; window.__withComments = true; window.__can = "ok"; }, { seed });
  if (!noRuntime) await page.addInitScript({ path: FAKE });
  await page.goto("file://" + PAGE);
  return { ctx, page, errors };
}

(async () => {
  let browser;
  try { browser = await chromium.launch(); } catch (e) { console.log("SKIP no browser"); process.exit(0); }
  const out = { errors: [] };
  {
    const { ctx, page, errors } = await open(browser, {});
    await page.waitForTimeout(300);
    out.framesBefore = await page.evaluate(() =>
      Array.from(document.querySelectorAll("#c-video iframe")).filter((f) => f.srcdoc).length);
    await page.locator("#c-video").scrollIntoViewIfNeeded();
    await page.waitForTimeout(600);
    out.framesAfter = await page.evaluate(() =>
      Array.from(document.querySelectorAll("iframe")).filter((f) => f.srcdoc).length);
    await page.check('input[name="pick-hero"][value="b"]');
    await page.fill("#note-hero", "keep the band");
    await page.waitForTimeout(1200);
    const sets = await page.evaluate(() => window.__sets);
    const last = sets.filter((s) => s.p === "picks/hero").pop();
    out.pickDoc = last ? { pick: last.body.pick, note: last.body.note } : null;
    out.picked = await page.textContent("#picked");
    await page.click("#send-picks");
    await page.waitForTimeout(800);
    out.sent = (await page.evaluate(() => window.__sent)).length;
    const sub = (await page.evaluate(() => window.__sets)).filter((s) => s.p.indexOf("submissions/") === 0).pop();
    out.submission = sub ? sub.body : null;
    out.status = await page.textContent("#send-status");
    out.errors = out.errors.concat(errors);
    await ctx.close();
  }
  {
    const { ctx, page, errors } = await open(browser, {}, true);
    await page.waitForTimeout(300);
    out.readOnly = {
      disabled: await page.isDisabled('input[name="pick-hero"][value="a"]'),
      status: await page.textContent("#status"),
    };
    out.errors = out.errors.concat(errors);
    await ctx.close();
  }
  {
    const { ctx, page, errors } = await open(browser, { "picks/tables": { pick: "c", note: "", updatedAt: 5 } });
    await page.waitForTimeout(500);
    out.seeded = await page.evaluate(() => {
      const i = document.querySelector('input[name="pick-tables"]:checked');
      return i ? i.value : null;
    });
    out.errors = out.errors.concat(errors);
    await ctx.close();
  }
  await browser.close();
  console.log("RESULT " + JSON.stringify(out));
})().catch((e) => { console.error(e); process.exit(1); });
