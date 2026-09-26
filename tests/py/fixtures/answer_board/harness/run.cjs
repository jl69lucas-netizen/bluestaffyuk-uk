/* Answer board harness: node run.cjs <board.html> <fake.js>. Prints "RESULT {json}", or
   "SKIP <reason>" when Playwright or its browser is missing. Driven by
   tests/py/test_answer_board.py::test_the_client_in_a_browser_against_a_fake_db. */
const fs = require("fs");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) {
  try { ({ chromium } = require("@playwright/test")); } catch (e2) { console.log("SKIP no playwright"); process.exit(0); }
}
const [, , PAGE, FAKE] = process.argv;
const html = fs.readFileSync(PAGE, "utf8");
const DEMO = JSON.parse(html.split('<script type="application/json" id="demo-batch">')[1].split("</script>")[0]
  .replace(/<\\\//g, "</"));
const B1 = Object.assign({}, DEMO, { id: "b1" });
const answerWrites = (sets) => sets.filter((s) => s.p.indexOf("/answers/") >= 0);

async function open(browser, seed, draft, hash) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.addInitScript(({ seed, draft }) => {
    window.__seed = seed;
    if (draft) { try { localStorage.setItem("answer-board:v1", JSON.stringify(draft)); } catch (e) { /* none */ } }
  }, { seed, draft });
  await page.addInitScript({ path: FAKE });
  await page.goto("file://" + PAGE + (hash || ""));
  return { ctx, page, errors };
}

(async () => {
  let browser;
  try { browser = await chromium.launch(); } catch (e) { console.log("SKIP no browser"); process.exit(0); }
  const out = {};

  // 1. A 4 s typing burst: the debounce must hold even though the writer's own echoes arrive.
  {
    const { ctx, page } = await open(browser, { "batches/b1": B1 });
    const ta = page.locator("#b1--q01 textarea");
    await ta.click();
    await ta.type("ab"); await page.waitForTimeout(900);
    for (let i = 0; i < 40; i++) { await ta.type("x"); await page.waitForTimeout(100); }
    await page.waitForTimeout(1500);
    out.burstWrites = answerWrites(await page.evaluate(() => window.__sets)).length;
    await ctx.close();
  }

  // 2. A browser draft newer than the board is written up once.
  {
    const draft = { b1: { q01: { n: 1, text: "from draft", choice: "", status: "answered", updatedAt: Date.now() } } };
    const { ctx, page } = await open(browser, {
      "batches/b1": B1,
      "batches/b1/answers/q01": { n: 1, text: "old", choice: "", status: "answered", updatedAt: 1 },
    }, draft);
    await page.waitForSelector("#b1--q01");
    await page.waitForTimeout(1500);
    const w = answerWrites(await page.evaluate(() => window.__sets));
    out.draft = { writes: w.length, texts: w.map((s) => s.body.text), shown: await page.locator("#b1--q01 textarea").inputValue() };
    await ctx.close();
  }

  // 3. A load with nothing new writes nothing.
  {
    const seed = { "batches/b1": B1 };
    B1.questions.forEach((q, i) => {
      seed["batches/b1/answers/" + q.key] = { n: q.n, text: "t" + i, choice: q.kind === "choice" ? q.options[0].id : "",
        status: "answered", updatedAt: 5 };
    });
    const { ctx, page } = await open(browser, seed);
    await page.waitForSelector("#b1--q01");
    await page.waitForTimeout(1500);
    out.idleWrites = (await page.evaluate(() => window.__sets)).length;
    await ctx.close();
  }

  // 4. A snapshot while a textarea has focus: what Send submits is what the viewer sees.
  {
    const { ctx, page } = await open(browser, { "batches/b1": B1 });
    const ta = page.locator("#b1--q01 textarea");
    await ta.click();
    await ta.type("mine");
    await page.evaluate(() => window.__put("batches/b1/answers/q01",
      { n: 1, text: "theirs", choice: "", status: "answered", updatedAt: Date.now() + 1000 }));
    await page.waitForTimeout(100);
    const typedStill = await ta.inputValue();
    await page.locator("#b-b1 [data-send]").click();
    await page.waitForTimeout(1200);
    const sub = (await page.evaluate(() => window.__sets)).filter((s) => s.p.indexOf("/submissions/") >= 0);
    out.focus = { typedStill, shown: await ta.inputValue(), submitted: sub.length ? sub[0].body.answers[0].text : null };
    await ctx.close();
  }

  // 5. A malformed batch beside a good one: the good one still renders.
  {
    const bad = { title: "Bad", project: "x", askedAt: "2027-01-01T00:00:00Z", status: "open",
      sections: [{ title: "S", lead: "" }], questions: [{ n: 1, key: "q01", section: 0, question: "Q", kind: "choice" }] };
    const { ctx, page, errors } = await open(browser, { "batches/b1": B1, "batches/a0": bad });
    try { await page.waitForSelector("#b-b1", { timeout: 3000 }); } catch (e) { /* reported below */ }
    out.malformed = { good: await page.locator("#b-b1").count(), bad: await page.locator("#b-a0").count(), errors };
    await ctx.close();
  }

  // 6. Demo mode keeps the real batches' browser drafts.
  {
    const draft = { b9: { q01: { n: 1, text: "real", choice: "", status: "answered", updatedAt: 7 } } };
    const { ctx, page } = await open(browser, {}, draft, "#demo");
    await page.locator("#demo--q01 textarea").fill("demo text");
    await page.waitForTimeout(100);
    const stored = await page.evaluate(() => JSON.parse(localStorage.getItem("answer-board:v1")));
    out.demoDraft = { ids: Object.keys(stored).sort(), real: stored.b9 && stored.b9.q01.text };
    await ctx.close();
  }

  // 7. A newer record held during an edit is not overwritten when the pending save fires.
  {
    const { ctx, page } = await open(browser, { "batches/b1": B1 });
    const ta = page.locator("#b1--q01 textarea");
    await ta.click();
    await ta.type("mine");
    await page.evaluate(() => window.__put("batches/b1/answers/q01",
      { n: 1, text: "theirs", choice: "", status: "answered", updatedAt: Date.now() + 1000 }));
    await page.waitForTimeout(1200);  // the 800 ms save fires while the textarea still has focus
    const w = answerWrites(await page.evaluate(() => window.__sets));
    out.held = { texts: w.map((s) => s.body.text), shown: await ta.inputValue() };
    await ctx.close();
  }

  console.log("RESULT " + JSON.stringify(out));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
