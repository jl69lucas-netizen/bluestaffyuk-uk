/* Markdown Artifact harness: node run.cjs <page.html>. Prints "RESULT {json}", or "SKIP <reason>"
   when Playwright or its browser is missing. Driven by tests/py/test_md_artifact.py.
   Each scenario stands in for the claude.ai viewer with a fake `window.claude.use`: the
   downloads namespace is absent, null, saving, or rejecting with a given code. The cdnjs
   scripts are blocked, so the page renders its markdown as text (its no-library path). */
const fs = require("fs");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) {
  try { ({ chromium } = require("@playwright/test")); } catch (e2) { console.log("SKIP no playwright"); process.exit(0); }
}
const [, , PAGE] = process.argv;

// mode: "none" (no window.claude, a saved copy), "null" (use() resolves null), "save", or an
// error code that save() rejects with.
function fake(mode) {
  window.__saves = [];
  if (mode === "none") return;
  var ns = mode === "null" ? null : Object.freeze({
    save: function (req) {
      window.__saves.push({ filename: req.filename, data: req.data });
      return mode === "save" ? Promise.resolve({ status: "saved" })
        : Promise.reject({ code: mode, message: mode });
    },
  });
  window.claude = Object.freeze({
    use: function (name) {
      return new Promise(function (r) { setTimeout(function () { r(name === "downloads" ? ns : null); }, 50); });
    },
  });
}

async function run(browser, mode, click) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.route(/cdnjs\.cloudflare\.com|fonts\.googleapis\.com/, (r) => r.abort());
  await page.addInitScript(fake, mode);
  await page.goto("file://" + PAGE);
  await page.waitForTimeout(300);
  const btn = page.locator("#dl-md");
  const out = { hiddenBefore: await btn.isHidden() };
  if (click) {
    await btn.click();
    await page.waitForTimeout(150);
    out.saves = await page.evaluate(() => window.__saves);
    out.status = await page.locator("#all-status").textContent();
    out.hiddenAfter = await btn.isHidden();
  }
  out.copyAllVisible = await page.locator("#copy-all").isVisible();
  out.sections = await page.locator("section.sec").count();
  out.errors = errors;
  await ctx.close();
  return out;
}

(async () => {
  let browser;
  try { browser = await chromium.launch(); } catch (e) { console.log("SKIP no browser"); process.exit(0); }
  const out = {};
  out.none = await run(browser, "none", false);
  out.nullNs = await run(browser, "null", false);
  out.save = await run(browser, "save", true);
  out.declined = await run(browser, "declined", true);
  out.unavailable = await run(browser, "unavailable", true);
  await browser.close();
  console.log("RESULT " + JSON.stringify(out));
})().catch((e) => { console.error(e); process.exit(1); });
