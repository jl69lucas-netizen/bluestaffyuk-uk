/* Board readability harness: node run.cjs <page.html>. Prints "RESULT {json}", or "SKIP <reason>"
   when Playwright or its browser is missing. Driven by tests/py/test_research_board_builder.py
   and tests/py/test_page_board_readability.py.
   The cdnjs scripts are blocked, so a block renders its markdown as text (the no-library path):
   what is measured is the summary layer (scripts/board_style.py) and the copy buttons, not the
   markdown renderer. The clipboard is a stub that records what each copy button hands over. */
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) {
  try { ({ chromium } = require("@playwright/test")); } catch (e2) { console.log("SKIP no playwright"); process.exit(0); }
}
const [, , PAGE] = process.argv;

function stub() {
  window.__copied = [];
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: { writeText: function (t) { window.__copied.push(t); return Promise.resolve(); } },
  });
}

(async () => {
  let browser;
  try { browser = await chromium.launch(); } catch (e) { console.log("SKIP no browser"); process.exit(0); }
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.route(/cdnjs\.cloudflare\.com|fonts\.googleapis\.com/, (r) => r.abort());
  await page.addInitScript(stub);
  await page.goto("file://" + PAGE);
  await page.waitForTimeout(300);
  const blocks = await page.evaluate(() => {
    return [].map.call(document.querySelectorAll(".md[data-title]"), function (b) {
      var plain = b.querySelector(":scope > .plain"), full = b.querySelector(":scope > details.full");
      var kids = [].slice.call(b.children);
      return {
        title: b.getAttribute("data-title"),
        plain: plain ? [].map.call(plain.querySelectorAll(":scope > ul > li"), function (li) { return li.textContent; }) : null,
        care: plain ? [].map.call(plain.querySelectorAll(".box.care li"), function (li) { return li.textContent; }) : [],
        plainFirst: !!plain && kids.indexOf(plain) === 0 && kids.indexOf(full) === 1,
        fullText: full ? full.textContent : null,
        fullOpen: full ? full.open : null,
        text: b.textContent,
      };
    });
  });
  const buttons = page.locator("button", { hasText: /^Copy (section|block)$/ });
  const n = await buttons.count();
  for (let i = 0; i < n; i++) {
    await buttons.nth(i).evaluate((b) => b.click());   // a closed card hides its button
  }
  await page.waitForTimeout(100);
  const copied = await page.evaluate(() => window.__copied);
  const legend = await page.locator(".legend").count();
  await browser.close();
  console.log("RESULT " + JSON.stringify({ errors, blocks, copied, legend }));
})().catch((e) => { console.error(e); process.exit(1); });
