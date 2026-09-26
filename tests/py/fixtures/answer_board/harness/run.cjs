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

async function open(browser, seed, draft, hash, withComments, noRuntime) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.addInitScript(({ seed, draft, withComments }) => {
    window.__seed = seed;
    window.__withComments = !!withComments;
    if (draft) { try { localStorage.setItem("answer-board:v1", JSON.stringify(draft)); } catch (e) { /* none */ } }
  }, { seed, draft, withComments });
  if (!noRuntime) await page.addInitScript({ path: FAKE });
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

  // 8. A stale cached "no_session" never blocks a send: the click always tries.
  {
    const { ctx, page } = await open(browser, { "batches/b1": B1 }, null, "", true);
    await page.waitForSelector("#b-b1 [data-send]");
    await page.waitForTimeout(800);                       // the cache now says no_session
    await page.evaluate(() => { window.__can = "available"; });
    await page.locator("#b-b1 [data-send]").click();      // before any re-check can answer
    await page.waitForTimeout(800);
    out.staleCache = { sent: (await page.evaluate(() => window.__sent)).length,
      status: await page.locator("#b-b1 [data-send-status]").textContent() };
    await ctx.close();
  }

  // 9. claude_unavailable: the snapshot is still written and the message says so.
  {
    const { ctx, page } = await open(browser, { "batches/b1": B1 }, null, "", true);
    await page.waitForSelector("#b-b1 [data-send]");
    await page.evaluate(() => { window.__can = "available"; window.__sendReject = "claude_unavailable"; });
    await page.waitForTimeout(800);
    await page.locator("#b-b1 [data-send]").click();
    await page.waitForTimeout(800);
    const subs = (await page.evaluate(() => window.__sets)).filter((x) => x.p.indexOf("/submissions/") >= 0);
    out.unavailable = { snapshots: subs.length, status: await page.locator("#b-b1 [data-send-status]").textContent() };
    await ctx.close();
  }

  // 10–16. The "Any additional questions" section.
  const ADD = "#additional-text", ADD_SEND = "#additional-send";
  const addWrites = (sets) => sets.filter((s) => s.p === "drafts/additional");
  const addSnaps = (sets) => sets.filter((s) => s.p.indexOf("additional/") === 0);

  // (a) A 4 s typing burst: one or two writes to drafts/additional.
  {
    const { ctx, page } = await open(browser, {});
    await page.waitForSelector(ADD, { state: "visible" });
    const ta = page.locator(ADD);
    await ta.click();
    await ta.type("ab"); await page.waitForTimeout(900);
    for (let i = 0; i < 40; i++) { await ta.type("x"); await page.waitForTimeout(100); }
    await page.waitForTimeout(1500);
    out.addBurst = addWrites(await page.evaluate(() => window.__sets)).length;
    await ctx.close();
  }

  // (b) A reload keeps the text (browser draft; the fake db starts empty again).
  {
    const { ctx, page } = await open(browser, {});
    await page.waitForSelector(ADD, { state: "visible" });
    await page.locator(ADD).fill("keep me\nand me");
    await page.waitForTimeout(100);
    await page.reload();
    await page.waitForSelector(ADD, { state: "visible" });
    await page.waitForTimeout(300);
    out.addReload = await page.locator(ADD).inputValue();
    await ctx.close();
  }

  // (c) Send: one snapshot with the typed text, one note naming it, the field cleared.
  {
    const { ctx, page } = await open(browser, {}, null, "", true);
    await page.evaluate(() => { window.__can = "available"; });
    await page.waitForSelector(ADD, { state: "visible" });
    const typed = "1. Also check the footer?\n2. Sub-task: resize the logo.";
    await page.locator(ADD).fill(typed);
    await page.locator(ADD_SEND).click();
    await page.waitForTimeout(1200);
    const sets = await page.evaluate(() => window.__sets);
    const snaps = addSnaps(sets), drafts = addWrites(sets), sent = await page.evaluate(() => window.__sent);
    const sid = snaps.length ? snaps[0].body.id : "";
    out.addSend = { snaps: snaps.length, textOk: snaps.length === 1 && snaps[0].body.text === typed,
      pathOk: snaps.length === 1 && snaps[0].p === "additional/" + sid && /^s-[0-9T-]+Z$/.test(sid),
      sent: sent.length, noteOk: sent.length === 1 && sent[0].indexOf(sid) >= 0 && sent[0].indexOf("additional/" + sid) >= 0,
      noteBytes: sent.length ? Buffer.byteLength(sent[0]) : 0,
      field: await page.locator(ADD).inputValue(),
      lastDraft: drafts.length ? drafts[drafts.length - 1].body.text : null,
      stored: await page.evaluate(() => (JSON.parse(localStorage.getItem("answer-board:v1") || "{}")._additional || {}).text),
      status: await page.locator("#additional-status").textContent() };
    await ctx.close();
  }

  // (d) Send with nothing typed: disabled, no writes, no send.
  {
    const { ctx, page } = await open(browser, {}, null, "", true);
    await page.evaluate(() => { window.__can = "available"; });
    await page.waitForSelector(ADD, { state: "visible" });
    await page.locator(ADD_SEND).click({ force: true });
    await page.waitForTimeout(800);
    const disabled = await page.locator(ADD_SEND).isDisabled();
    const hint = await page.locator("#additional-hint").textContent();
    const writes = (await page.evaluate(() => window.__sets)).length, sent = (await page.evaluate(() => window.__sent)).length;
    await page.locator(ADD).fill("   \n  ");
    const blankDisabled = await page.locator(ADD_SEND).isDisabled();
    out.addEmpty = { disabled, hint, writes, sent, blankDisabled };
    await ctx.close();
  }

  // (e) The snapshot save fails: the field is not cleared and the error shows.
  {
    const { ctx, page } = await open(browser, {}, null, "", true);
    await page.evaluate(() => { window.__can = "available"; window.__rejectSet = "additional/"; });
    await page.waitForSelector(ADD, { state: "visible" });
    await page.locator(ADD).fill("do not lose me");
    await page.locator(ADD_SEND).click();
    await page.waitForTimeout(1200);
    const drafts = addWrites(await page.evaluate(() => window.__sets));
    out.addReject = { field: await page.locator(ADD).inputValue(),
      cleared: drafts.some((s) => s.body.text === ""),
      status: await page.locator("#additional-status").textContent() };
    await ctx.close();
  }

  // (f) #demo shows the section with Send off.
  {
    const { ctx, page } = await open(browser, {}, null, "#demo");
    await page.waitForSelector("#demo--q01");
    out.addDemo = { visible: await page.locator("#additional").isVisible(),
      disabled: await page.locator(ADD_SEND).isDisabled(),
      status: await page.locator("#additional-status").textContent() };
    await ctx.close();
  }

  // (g) Outside claude.ai (no runtime): the section stays hidden.
  {
    const { ctx, page } = await open(browser, {}, null, "", false, true);
    await page.waitForTimeout(300);
    out.addNoBoard = { visible: await page.locator("#additional").isVisible(),
      status: await page.locator("#status-line").textContent() };
    await ctx.close();
  }

  console.log("RESULT " + JSON.stringify(out));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
