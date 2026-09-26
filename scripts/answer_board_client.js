/* Answer board client (spec docs/superpowers/specs/2026-09-26-answer-board-design.md §5–§6).
   Inlined by scripts/build_answer_board.py. Batches (the questions) come from the board's db;
   answers save one document per question with a browser draft as backup. Every capability is
   optional: claude.use() may resolve null. `#demo` renders the embedded demo batch locally. */
(function () {
  "use strict";
  var DEMO = JSON.parse(document.getElementById("demo-batch").textContent);
  var DRAFT_KEY = "answer-board:v1";
  var CHIPS = ["not_yet", "skip"];
  var STATUSES = ["answered", "not_yet", "skip", "empty"];
  var batches = {};     // id -> batch document
  var answers = {};     // id -> { qNN -> {n, text, choice, status, updatedAt} }
  var subs = {};        // id -> unsubscribe for that batch's answers
  var rendered = {};    // id -> signature of the rendered batch
  var isNew = {};       // id -> true until the batch is scrolled into view
  var written = {}, timers = {}, inflight = {}, again = {};
  var later = {};       // id::key -> newest board record held back while that question is being edited
  var drafted = {};     // id -> true once the browser draft was written up (first answers snapshot)
  var observers = {};   // id -> IntersectionObserver clearing the New badge
  var sending = {};     // id -> status text while a Send is in progress
  var db = null, comments = null, downloads = null, demo = false, firstBatches = true, batchesLoaded = false;
  var canSend = "off";  // cached comments.canSendToClaude(), so the click goes straight to the send
  var DOWNLOAD_OFF = ["unavailable", "not_granted", "capability_disabled", "capability_removed"];

  function $(id) { return document.getElementById(id); }
  function setText(el, s) { if (typeof el === "string") el = $(el); if (el) el.textContent = s; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function inline(s) { s = esc(s);
    return s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  }
  function paras(md) {
    return String(md || "").split(/\n\s*\n/).filter(function (b) { return b.trim(); })
      .map(function (b) { return "<p>" + inline(b.split(/\s+/).join(" ").trim()) + "</p>"; }).join("");
  }
  function k(id, key) { return id + "::" + key; }
  function sig(a) { return JSON.stringify([a.text, a.choice, a.status]); }
  function skipLabel(b) { return b.project === "site-content" ? "Leave it off the site" : "Skip"; }
  function questionOf(id, key) {
    var qs = batches[id].questions;
    for (var i = 0; i < qs.length; i++) if (qs[i].key === key) return qs[i];
    return null;
  }
  function derive(q, a, chip) {
    if (chip) return chip;
    if (q.kind === "choice") return a.choice ? "answered" : "empty";
    return a.text.trim() ? "answered" : "empty";
  }
  function blank(q) { return { n: q.n, text: "", choice: "", status: "empty", updatedAt: 0 }; }

  // Browser draft: a per-viewer convenience that can be unavailable.
  function readDraft() {
    try { return JSON.parse(localStorage.getItem(DRAFT_KEY) || "{}") || {}; } catch (e) { return {}; }
  }
  function writeDraft() {
    // Keep only open batches once the board's batches have loaded; demo mode rewrites only
    // "demo" and keeps every other stored draft.
    var keep = demo ? Object.assign({}, readDraft()) : batchesLoaded ? {} : Object.assign({}, draft);
    Object.keys(answers).forEach(function (id) {
      if (demo ? id === "demo" : !batchesLoaded || (batches[id] && batches[id].status !== "received")) keep[id] = answers[id];
    });
    try { localStorage.setItem(DRAFT_KEY, JSON.stringify(keep)); } catch (e) { /* storage blocked */ }
  }
  var draft = readDraft();
  function adopt(id, key, rec) {
    var a = answers[id][key];
    if (!a || !rec || typeof rec.updatedAt !== "number" || rec.updatedAt <= a.updatedAt) return false;
    a.text = typeof rec.text === "string" ? rec.text : "";
    a.choice = typeof rec.choice === "string" ? rec.choice : "";
    a.status = STATUSES.indexOf(rec.status) >= 0 ? rec.status : derive(questionOf(id, key), a, null);
    a.updatedAt = rec.updatedAt;
    return true;
  }
  // A batch from db is checked before it is used; a bad one is skipped, never the whole snapshot.
  function str(v) { return typeof v === "string" ? v : ""; }
  function cleanBatch(raw, id) {
    if (!raw || !Array.isArray(raw.questions) || !Array.isArray(raw.sections)) return null;
    var b = JSON.parse(JSON.stringify(raw)), keys = {};
    b.id = id;
    ["title", "askedAt", "intro", "project", "status", "receivedAt", "receivedCommit"].forEach(function (f) { b[f] = str(b[f]); });
    for (var i = 0; i < b.sections.length; i++) {
      var s = b.sections[i];
      if (!s || typeof s !== "object") return null;
      b.sections[i] = { title: str(s.title), lead: str(s.lead) };
    }
    for (var j = 0; j < b.questions.length; j++) {
      var q = b.questions[j];
      if (!q || typeof q !== "object" || typeof q.key !== "string" || !/^q\d{2,}$/.test(q.key) || keys[q.key]) return null;
      if (typeof q.question !== "string" || (q.kind !== "text" && q.kind !== "choice")) return null;
      if (!Number.isInteger(q.section) || q.section < 0 || q.section >= b.sections.length) return null;
      if (q.kind === "choice" && !(Array.isArray(q.options) && q.options.length && q.options.every(function (o) {
        return o && typeof o.id === "string" && typeof o.label === "string";
      }))) return null;
      keys[q.key] = true;
      q.options = q.kind === "choice" ? q.options.map(function (o) { return { id: o.id, label: o.label }; }) : [];
      q.context = str(q.context); q.where = str(q.where);
      q.n = Number.isInteger(q.n) ? q.n : parseInt(q.key.slice(1), 10);
    }
    return b;
  }
  function ensureAnswers(id) {
    // Also run when a batch is re-posted: a question new to this view gets a blank record.
    if (!answers[id]) answers[id] = {};
    var d = draft[id] || {};
    batches[id].questions.forEach(function (q) {
      if (answers[id][q.key]) return;
      answers[id][q.key] = blank(q);
      adopt(id, q.key, d[q.key]);
    });
  }

  // ---------- rendering ----------
  function cardHtml(b, q) {
    var id = b.id, dom = id + "--" + q.key;
    var h = '<article class="q" id="' + esc(dom) + '" data-batch="' + esc(id) + '" data-key="' + esc(q.key) + '" data-state="empty">' +
      '<h4 id="h-' + esc(dom) + '"><span class="qn">' + esc(q.n) + "</span>" + inline(q.question) + "</h4>" +
      '<div class="ctx">' + paras(q.context) + "</div>" +
      (q.where ? '<p class="where"><strong>Where it goes:</strong> ' + inline(q.where) + "</p>" : "");
    if (q.kind === "choice") {
      h += '<div class="opts" role="group" aria-labelledby="h-' + esc(dom) + '">' + q.options.map(function (o) {
        return '<button type="button" class="opt" data-choice="' + esc(o.id) + '" aria-pressed="false"><b>' +
          esc(o.id.toUpperCase()) + "</b>" + inline(o.label) + "</button>";
      }).join("") + "</div>" +
        '<label class="lab" for="a-' + esc(dom) + '">Note (optional)</label>' +
        '<textarea class="notefield" id="a-' + esc(dom) + '" rows="2" autocomplete="off" placeholder="Add a note…"></textarea>';
    } else {
      h += '<label class="lab" for="a-' + esc(dom) + '">Your answer</label>' +
        '<textarea id="a-' + esc(dom) + '" rows="3" autocomplete="off" placeholder="Type your answer…"></textarea>';
    }
    return h + '<div class="row" role="group" aria-labelledby="h-' + esc(dom) + '">' +
      '<button type="button" class="chip" data-status="not_yet" aria-pressed="false">Not yet</button>' +
      '<button type="button" class="chip" data-status="skip" aria-pressed="false">' + esc(skipLabel(b)) + "</button>" +
      '<span class="tick"></span></div></article>';
  }
  function batchHtml(b) {
    var h = '<section class="batch" id="b-' + esc(b.id) + '" data-batch="' + esc(b.id) + '">' +
      '<div class="bhead"><h2>' + esc(b.title) + '</h2><span><span class="pill">' + esc(b.project) +
      '</span> <span class="pill">asked ' + esc(String(b.askedAt).slice(0, 10)) + "</span></span></div>" +
      (b.intro ? '<section class="sec intro">' + paras(b.intro) + "</section>" : "");
    b.sections.forEach(function (s, i) {
      var qs = b.questions.filter(function (q) { return q.section === i; });
      h += '<section class="sec"><h3 class="st">' + esc(s.title) + "</h3>" +
        '<div class="lead">' + paras(s.lead) + "</div>" + qs.map(function (q) { return cardHtml(b, q); }).join("") + "</section>";
    });
    return h + '<section class="sec send" data-send-card="' + esc(b.id) + '"><div class="sendrow"><div>' +
      "<h3 class=\"st\">Ready to send?</h3><p class=\"muted\" data-counts></p></div>" +
      '<button type="button" class="btn big" data-send>Send to Claude Code →</button></div>' +
      '<p class="sendstatus" role="status" data-send-status></p>' +
      '<div class="row"><span>No Claude session watching?</span>' +
      '<button type="button" class="chip" data-copy>Copy answers</button>' +
      '<button type="button" class="chip" data-download hidden>Download .md</button>' +
      "<span data-fallback aria-live=\"polite\"></span></div></section></section>";
  }
  function openIds() {
    return Object.keys(batches).filter(function (id) { return batches[id].status !== "received"; })
      .sort(function (x, y) {
        var a = batches[x].askedAt || "", b = batches[y].askedAt || "";
        return a < b ? 1 : a > b ? -1 : (x < y ? -1 : 1);
      });
  }
  function hasFocusIn(el) { return el && document.activeElement && el.contains(document.activeElement); }
  function batchSig(b) { return JSON.stringify([b.title, b.project, b.askedAt, b.intro, b.sections, b.questions]); }
  function renderBatches() {
    var host = $("batches"), ids = openIds();
    Object.keys(rendered).forEach(function (id) {
      if (ids.indexOf(id) < 0) { var gone = $("b-" + id); if (gone) gone.remove(); delete rendered[id]; }
    });
    ids.forEach(function (id, i) {
      var b = batches[id], s = batchSig(b);
      var el = $("b-" + id);
      if (!el || (rendered[id] !== s && !hasFocusIn(el))) {
        var wrap = document.createElement("div");
        wrap.innerHTML = batchHtml(b);
        var fresh = wrap.firstChild;
        if (el) el.replaceWith(fresh); else host.appendChild(fresh);
        rendered[id] = s;
        wire(fresh, id);
        el = fresh;
      }
      if (host.children[i] !== el) host.insertBefore(el, host.children[i] || null);
      Object.keys(answers[id]).forEach(function (key) { paintCard(id, key); });
    });
    renderRail();
    renderDone();
    paintTotals();
    refreshCanSend();
    if (!ids.length) setText("status-line", demo ? "Demo batch" : "No open questions right now. New batches appear here as soon as Claude posts them.");
    else setText("status-line", demo ? "Demo mode: answers are saved in this browser only." : "");
    $("status-line").hidden = !$("status-line").textContent;
  }
  function paintCard(id, key, force) {
    var a = answers[id][key], card = $(id + "--" + key);
    if (!card) return;
    var ta = card.querySelector("textarea");
    if (ta && (force || document.activeElement !== ta) && ta.value !== a.text) { ta.value = a.text; grow(ta); }
    card.querySelectorAll("[data-status]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.getAttribute("data-status") === a.status));
    });
    card.querySelectorAll("[data-choice]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.getAttribute("data-choice") === a.choice));
    });
    card.setAttribute("data-state", a.status);
    var nav = document.querySelector('.navq[href="#' + cssId(id + "--" + key) + '"]');
    if (nav) nav.setAttribute("data-state", a.status);
  }
  function cssId(s) { return window.CSS && CSS.escape ? CSS.escape(s) : s; }
  function counts(id) {
    var c = { answered: 0, skip: 0, not_yet: 0, empty: 0 };
    (batches[id] ? batches[id].questions : []).forEach(function (q) { c[answers[id][q.key].status] += 1; });
    return c;
  }
  function renderRail() {
    var nav = $("rail-batches");
    nav.innerHTML = openIds().map(function (id) {
      var b = batches[id], c = counts(id), total = b.questions.length;
      return '<a class="navbatch" href="#b-' + esc(id) + '"><span>' + esc(b.title) +
        (isNew[id] ? '<span class="new">New</span>' : "") + "</span><small>" + (total - c.empty) + " / " + total + "</small></a>" +
        b.questions.map(function (q) {
          return '<a class="navq" href="#' + esc(id + "--" + q.key) + '" data-state="' + esc(answers[id][q.key].status) +
            '"><span class="dot"></span><b>' + esc(q.n) + "</b><span>" + esc(q.question.length > 42 ? q.question.slice(0, 41) + "…" : q.question) + "</span></a>";
        }).join("");
    }).join("");
  }
  function paintTotals() {
    var done = 0, all = 0, open = openIds();
    open.forEach(function (id) {
      var c = counts(id), n = batches[id].questions.length;
      all += n; done += n - c.empty;
      var card = document.querySelector('[data-send-card="' + cssId(id) + '"]');
      if (card) setText(card.querySelector("[data-counts]"), c.answered + " answered · " + c.not_yet + " not yet · " + c.skip + " skipped · " + c.empty + " empty");
    });
    setText("total-done", String(done));
    setText("total-all", String(all));
    $("bar").style.width = (all ? Math.round(done * 100 / all) : 0) + "%";
    setText("total-detail", open.length + (open.length === 1 ? " open batch" : " open batches"));
  }
  function renderDone() {
    var ids = Object.keys(batches).filter(function (id) { return batches[id].status === "received"; })
      .sort(function (x, y) { return (batches[y].receivedAt || "") < (batches[x].receivedAt || "") ? -1 : 1; });
    $("done").hidden = !ids.length;
    $("done-list").innerHTML = ids.map(function (id) {
      var b = batches[id];
      return '<div class="donerow" data-done="' + esc(id) + '"><strong>' + esc(b.title) + "</strong> " +
        '<span class="muted">received ' + esc(String(b.receivedAt).slice(0, 10)) +
        (b.receivedCommit ? " · commit " + esc(b.receivedCommit) : "") + "</span> " +
        '<button type="button" class="chip" data-show>Show answers</button><div data-answers></div></div>';
    }).join("");
    $("done-list").querySelectorAll("[data-show]").forEach(function (btn) {
      btn.addEventListener("click", function () { showDone(btn.closest("[data-done]")); });
    });
  }
  function showDone(row) {
    var id = row.getAttribute("data-done"), out = row.querySelector("[data-answers]");
    if (!db) return;
    db.collection("batches/" + id + "/answers").get().then(function (snap) {
      var got = {};
      snap.docs.forEach(function (d) { got[d.id] = d.data() || {}; });
      out.innerHTML = "<ol>" + batches[id].questions.map(function (q) {
        var a = got[q.key] || {}, opt = (q.options || []).filter(function (o) { return o.id === a.choice; })[0];
        return "<li><strong>" + inline(q.question) + "</strong> — " + esc(a.status || "empty") +
          (opt ? ": " + inline(opt.label) : "") + (a.text ? "<br>" + esc(a.text) : "") + "</li>";
      }).join("") + "</ol>";
    }, function (e) { setText(out, "Could not load (" + ((e && e.code) || "error") + ")"); });
  }
  function grow(ta) { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + 2 + "px"; }

  // ---------- saving ----------
  function touch(id, key) {
    answers[id][key].updatedAt = Date.now();
    writeDraft(); paintCard(id, key); renderRail(); paintTotals();
    var tick = document.getElementById(id + "--" + key).querySelector(".tick");
    if (!db) { setText("saved", "Saved in this browser"); setText(tick, "✓ saved here"); return; }
    setText("saved", "Saving…"); setText(tick, "");
    clearTimeout(timers[k(id, key)]);
    timers[k(id, key)] = setTimeout(function () { flush(id, key); }, 800);
  }
  function busy(id, key) {
    var card = $(id + "--" + key), ta = card && card.querySelector("textarea");
    return !!timers[k(id, key)] || !!(ta && document.activeElement === ta);
  }
  // A board record that arrived while the viewer was editing this question is applied when
  // they leave it (focusout) or once the pending save settles, if it is still the newer one.
  function applyLater(id, key, leaving) {
    var t = k(id, key), rec = later[t];
    if (!rec || (!leaving && busy(id, key))) return;
    delete later[t];
    if (adopt(id, key, rec)) { paintCard(id, key, true); writeDraft(); renderRail(); paintTotals(); }
    if (!timers[t]) flush(id, key);
  }
  function flush(id, key) {
    var t = k(id, key);
    clearTimeout(timers[t]); delete timers[t];
    var a = answers[id] && answers[id][key];
    // A newer board record held during the edit wins over the older local text.
    if (a && later[t] && later[t].updatedAt > a.updatedAt) {
      var rec = later[t];
      delete later[t];
      if (adopt(id, key, rec)) { paintCard(id, key, true); writeDraft(); renderRail(); paintTotals(); }
    }
    if (!db || !a || a.updatedAt === 0 || written[t] === sig(a)) return inflight[t] || Promise.resolve();
    if (inflight[t]) { again[t] = true; return inflight[t]; }
    var body = { n: a.n, text: a.text, choice: a.choice, status: a.status, updatedAt: a.updatedAt };
    var p = db.collection("batches/" + id + "/answers").doc(key).set(body).then(function () {
      written[t] = sig(body);
      setText("saved", "Saved to the board " + new Date().toLocaleTimeString());
      var card = document.getElementById(id + "--" + key);
      if (card) setText(card.querySelector(".tick"), "✓ saved");
    }, function (e) {
      setText("saved", "Not saved to the board (" + ((e && e.code) || "error") + "). Kept in this browser.");
    }).then(function () {
      delete inflight[t];
      if (again[t]) { delete again[t]; return flush(id, key); }
      if (later[t] && !busy(id, key)) applyLater(id, key, false);
    });
    inflight[t] = p;
    return p;
  }
  function flushBatch(id) { return Promise.all(Object.keys(answers[id]).map(function (key) { return flush(id, key); })); }

  // ---------- send, copy, download ----------
  function answersMarkdown(id) {
    var b = batches[id], out = ["# " + b.title + ": answers", "", "Batch " + id, ""];
    b.questions.forEach(function (q) {
      var a = answers[id][q.key], opt = (q.options || []).filter(function (o) { return o.id === a.choice; })[0];
      out.push("## " + q.n + ". " + q.question, "", "Status: " + a.status + (opt ? " — picked (" + opt.id + ") " + opt.label : ""), "");
      if (a.text.trim()) out.push(a.text.trim(), "");
    });
    return out.join("\n");
  }
  function flash(el, msg) { setText(el, msg); setTimeout(function () { setText(el, ""); }, 2500); }
  function refreshCanSend() {
    if (!comments) { canSend = "off"; return; }
    comments.canSendToClaude().then(function (v) { canSend = v; }, function () { canSend = "off"; });
  }
  function sendCard(id) { return document.querySelector('[data-send-card="' + cssId(id) + '"]'); }
  function showSending(id) {
    var card = sendCard(id);
    if (!card) return;
    card.querySelector("[data-send]").setAttribute("aria-disabled", String(!!sending[id]));
    if (sending[id]) setText(card.querySelector("[data-send-status]"), sending[id]);
  }
  function sendResult(id, msg) {
    delete sending[id];
    showSending(id);
    var card = sendCard(id);  // the card may have been re-rendered while sending
    if (card) setText(card.querySelector("[data-send-status]"), msg);
  }
  function onSend(id, card) {
    if (sending[id]) return;
    if (!db) { setText(card.querySelector("[data-send-status]"), "This view cannot send. Use Copy answers."); return; }
    sending[id] = "Sending…";
    showSending(id);
    var sid = "s-" + new Date().toISOString().replace(/[:.]/g, "-"), c = counts(id), b = batches[id];
    var note = "Answers submitted — " + b.title.slice(0, 120) + " (" + id + "). Snapshot " + sid + ": " + c.answered + " answered, " +
      c.skip + " skip, " + c.not_yet + " not yet, " + c.empty + " empty. Read db batches/" + id + "/submissions/" + sid + ".";
    // The send must start inside this click (it needs the viewer's recent gesture), so it runs
    // beside the saves and uses the cached canSendToClaude(); Claude reads the snapshot seconds later.
    var sendingP = (canSend !== "available" ? Promise.resolve(canSend) : comments.anchorFor(card).then(function (anchor) {
      return comments.sendToClaude({ anchor: anchor, text: note });
    }).then(function () { return "sent"; })).catch(function (e) { return (e && e.code) || "error"; })
      .then(function (how) { refreshCanSend(); return how; });
    var saving = flushBatch(id).then(function () {
      return db.collection("batches/" + id + "/submissions").doc(sid).set({
        at: new Date().toISOString(), id: sid, batchId: id, counts: c,
        answers: b.questions.map(function (q) {
          var a = answers[id][q.key], opt = (q.options || []).filter(function (o) { return o.id === a.choice; })[0];
          return { n: q.n, key: q.key, question: q.question, kind: q.kind, choice: a.choice,
            choiceLabel: opt ? opt.label : "", status: a.status, text: a.text };
        })
      });
    });
    Promise.all([saving, sendingP]).then(function (r) {
      var how = r[1];
      if (how === "sent") sendResult(id, "Sent to Claude Code (copy " + sid + "). Claude's reply will appear in the comment thread.");
      else if (how === "rate_limited") sendResult(id, "Saved as copy " + sid + ". Sending is limited for a moment; wait, then press Send again.");
      else if (how === "consent_required") sendResult(id, "Saved as copy " + sid + ". You didn't allow comments from this page. Press Send again to allow it.");
      else if (how === "forbidden" || how === "writers_only") sendResult(id, "Saved as copy " + sid + ". Only an editor of this board can send to Claude.");
      else if (how === "claude_unavailable") sendResult(id, "Saved on the board as copy " + sid + ", but Claude Code couldn't receive it right now. Tell Claude Code \"read my answers\", or use Copy answers.");
      else if (how === "no_session") sendResult(id, "Saved on the board as copy " + sid + ", but no Claude Code session is watching this board right now. Tell Claude Code \"read my answers\", or use Copy answers.");
      else sendResult(id, "Saved on the board as copy " + sid + ", but sending to Claude isn't available here. Tell Claude Code \"read my answers\", or use Copy answers.");
    }, function (e) {
      sendResult(id, "The copy could not be saved (" + ((e && e.code) || "error") + "). Your answers are still here. Press Send again.");
    });
  }
  function copyText(text, el) {
    if (!navigator.clipboard) { flash(el, "Copy is blocked in this view"); return; }
    navigator.clipboard.writeText(text).then(function () { flash(el, "Copied"); }, function () { flash(el, "Copy is blocked in this view"); });
  }

  // ---------- wiring ----------
  function wire(section, id) {
    section.querySelectorAll("article.q").forEach(function (card) {
      var key = card.getAttribute("data-key"), q = questionOf(id, key), ta = card.querySelector("textarea");
      ta.addEventListener("input", function () {
        var a = answers[id][key], was = a.text;
        a.text = ta.value;
        // Typing an answer into an empty "Not yet" question answers it; Skip stays until un-chipped.
        if (q.kind === "text" && a.status === "not_yet" && !was.trim() && a.text.trim()) a.status = "answered";
        else a.status = derive(q, a, CHIPS.indexOf(a.status) >= 0 ? a.status : null);
        grow(ta); touch(id, key);
      });
      card.addEventListener("focusout", function () { applyLater(id, key, true); });
      card.querySelectorAll("[data-choice]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var a = answers[id][key], c = btn.getAttribute("data-choice");
          a.choice = a.choice === c ? "" : c;
          a.status = derive(q, a, null);
          touch(id, key);
        });
      });
      card.querySelectorAll("[data-status]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var a = answers[id][key], chip = btn.getAttribute("data-status");
          a.status = a.status === chip ? derive(q, a, null) : chip;
          touch(id, key);
        });
      });
    });
    var card = section.querySelector("[data-send-card]");
    var sendBtn = card.querySelector("[data-send]");
    sendBtn.disabled = !db;  // disabled only when this view cannot send at all
    if (!db) setText(card.querySelector("[data-send-status]"), demo ? "Demo: sending is off. Copy answers works." : "");
    showSending(id);
    card.addEventListener("pointerenter", refreshCanSend);
    card.addEventListener("focusin", refreshCanSend);
    sendBtn.addEventListener("click", function () { onSend(id, card); });
    card.querySelector("[data-copy]").addEventListener("click", function () {
      copyText(answersMarkdown(id), card.querySelector("[data-fallback]"));
    });
    var dl = card.querySelector("[data-download]");
    dl.hidden = !downloads;
    dl.addEventListener("click", function () {
      if (!downloads) return;
      downloads.save({ filename: id + "-answers.md", data: answersMarkdown(id) }).then(function (r) {
        flash(card.querySelector("[data-fallback]"), r && r.status === "saved" ? "Downloaded" : "");
      }, function (e) {
        if (e && DOWNLOAD_OFF.indexOf(e.code) >= 0) {
          downloads = null;
          document.querySelectorAll("[data-download]").forEach(function (x) { x.hidden = true; });
        }
        flash(card.querySelector("[data-fallback]"), "Download didn't happen (" + ((e && e.code) || "error") + ")");
      });
    });
    if (observers[id]) { observers[id].disconnect(); delete observers[id]; }
    if (isNew[id] && "IntersectionObserver" in window) {
      var io = observers[id] = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { delete isNew[id]; io.disconnect(); delete observers[id]; renderRail(); }
      });
      io.observe(section);
    }
  }

  // ---------- db ----------
  function subscribeAnswers(id) {
    if (subs[id]) return;
    subs[id] = db.collection("batches/" + id + "/answers").onSnapshot(function (snap) {
      if (!answers[id]) return;
      snap.docs.forEach(function (d) {
        var rec = d.data(), a = answers[id][d.id], t = k(id, d.id);
        if (!rec || !a) return;
        written[t] = sig({ text: rec.text || "", choice: rec.choice || "", status: rec.status });
        if (busy(id, d.id)) {
          // Never change a question under the viewer's hands; keep the newest record for later.
          if (typeof rec.updatedAt === "number" && rec.updatedAt > a.updatedAt &&
              (!later[t] || rec.updatedAt > later[t].updatedAt)) later[t] = rec;
          return;
        }
        if (adopt(id, d.id, rec)) paintCard(id, d.id);
      });
      // A browser draft newer than the board is written up once, on the batch's first snapshot.
      if (!drafted[id]) {
        drafted[id] = true;
        Object.keys(answers[id]).forEach(function (key) {
          var a = answers[id][key], t = k(id, key);
          if (a.updatedAt && !timers[t] && !inflight[t] && written[t] !== sig(a)) flush(id, key);
        });
      }
      writeDraft(); renderRail(); paintTotals();
    }, function (e) {
      setText("saved", "Answers for one batch stopped syncing (" + ((e && e.code) || "error") + "). Reload the page.");
    });
  }
  function onBatches(snap) {
    var seen = {};
    snap.docs.forEach(function (d) {
      var b = cleanBatch(d.data(), d.id);
      if (!b) {
        console.warn("answer board: skipped malformed batch " + d.id);
        if (batches[d.id]) seen[d.id] = true;  // keep the last good version on screen
        return;
      }
      seen[d.id] = true;
      if (!batches[d.id] && !firstBatches) isNew[d.id] = true;
      batches[d.id] = b;
      ensureAnswers(d.id);
      if (b.status === "received") { if (subs[d.id]) { subs[d.id](); delete subs[d.id]; } }
      else subscribeAnswers(d.id);
    });
    Object.keys(batches).forEach(function (id) {
      if (!seen[id]) { if (subs[id]) { subs[id](); delete subs[id]; } delete batches[id]; }
    });
    if (!(snap.metadata && snap.metadata.fromCache)) { firstBatches = false; batchesLoaded = true; }
    renderBatches();
  }
  function noBoard() {
    setText("status-line", "");
    $("status-line").innerHTML = 'Open this board on claude.ai to see your questions. <a href="#demo" id="demo-link">Preview a demo batch</a>';
    $("status-line").hidden = false;
    $("demo-link").addEventListener("click", function () { setTimeout(function () { location.reload(); }, 0); });
  }
  function startDemo() {
    demo = true;
    batches.demo = cleanBatch(DEMO, "demo");
    ensureAnswers("demo");
    renderBatches();
  }
  function connect() {
    var use = window.claude && window.claude.use;
    if (typeof use !== "function") { noBoard(); return; }
    use.call(window.claude, "comments").then(function (ns) { if (!ns) return; comments = ns; refreshCanSend(); }, function () {});
    use.call(window.claude, "downloads").then(function (ns) {
      if (!ns) return;
      downloads = ns;
      document.querySelectorAll("[data-download]").forEach(function (b) { b.hidden = false; });
    }, function () {});
    use.call(window.claude, "db").then(function (ns) {
      if (!ns) { noBoard(); return; }
      db = ns;
      db.collection("batches").onSnapshot(onBatches, function (e) {
        setText("status-line", "The board's storage stopped (" + ((e && e.code) || "error") + "). Reload the page.");
        $("status-line").hidden = false;
      });
    }, function () { noBoard(); });
  }

  // A re-render deferred because focus was inside a batch happens once focus leaves it.
  $("batches").addEventListener("focusout", function () {
    setTimeout(function () {
      if (openIds().some(function (id) { return rendered[id] !== batchSig(batches[id]); })) renderBatches();
    }, 0);
  });
  if (location.hash === "#demo") startDemo(); else connect();
})();
