/* Component canvas client (spec docs/superpowers/specs/2026-09-27-london-component-design-pass-design.md §2).
   Inlined by scripts/build_component_canvas.py. Frames are built lazily from the #frames blob,
   one section at a time, and scaled to fit at their true width. Picks save to the canvas db:
   picks/<component> {pick, note, updatedAt} and notes/general {text, updatedAt}; Send writes
   submissions/<s-time> and posts a comment, the way scripts/answer_board_client.js does. Every
   capability is optional: claude.use() may resolve null, and without a db the page is read-only. */
(function () {
  "use strict";
  var FRAMES = JSON.parse(document.getElementById("frames").textContent);
  var FINAL = document.body.getAttribute("data-final") === "true";
  var DRAFT_KEY = "component-canvas:v1";
  var PICKS = ["a", "b", "c", "redesign"];
  var db = null, comments = null, sending = false;
  var state = { picks: {}, notes: "" };   // picks: component -> {pick, note, updatedAt}
  var timers = {};

  function $(id) { return document.getElementById(id); }
  function setText(el, s) { if (typeof el === "string") el = $(el); if (el) el.textContent = s; }
  function comps() { return Array.prototype.slice.call(document.querySelectorAll("section.comp[data-component]")); }
  function ids() { return comps().map(function (s) { return s.getAttribute("data-component"); }); }
  function nameOf(cid) { var h = $("h-" + cid); return h ? h.textContent.replace(/^\d+\.\s*/, "") : cid; }

  // ---------- frames ----------
  function fit(frame) {
    var inner = frame.parentNode, stage = inner.parentNode;
    var w = Number(frame.getAttribute("width")) || 375;
    var avail = Math.max(120, stage.clientWidth - 24);
    var scale = Math.min(1, avail / w);
    var h = frame.__h || 480;
    frame.style.width = w + "px";
    frame.style.height = h + "px";
    frame.style.transform = scale < 1 ? "scale(" + scale + ")" : "none";
    inner.style.width = Math.round(w * scale) + "px";
    inner.style.height = Math.round(h * scale) + "px";
  }
  var DEVICE_H = { 375: 812, 768: 1024, 1280: 800 };
  function measure(frame) {
    if (frame.closest('[data-frame="device"]')) {   // scrolls inside itself, like a phone
      frame.__h = DEVICE_H[Number(frame.getAttribute("width"))] || 812;
      fit(frame);
      return;
    }
    try {
      var d = frame.contentDocument;
      if (d && d.documentElement) frame.__h = Math.max(120, d.documentElement.scrollHeight);
    } catch (e) { /* a frame we cannot read keeps its last height */ }
    fit(frame);
  }
  function load(section) {
    section.querySelectorAll("iframe[data-key]").forEach(function (frame) {
      if (frame.__loaded) return;
      frame.__loaded = true;
      frame.addEventListener("load", function () {
        var p = frame.parentNode.querySelector(".loading");
        if (p) p.remove();
        measure(frame);
        setTimeout(function () { measure(frame); }, 400);  // fonts and images settle
      });
      frame.srcdoc = FRAMES[frame.getAttribute("data-key")] || "<p>Missing preview.</p>";
    });
  }
  function setWidth(section, w) {
    section.setAttribute("data-width", String(w));
    section.querySelectorAll(".comp-head .seg button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-width") === String(w)));
    });
    section.querySelectorAll("iframe[data-key]").forEach(function (frame) {
      frame.setAttribute("width", String(w));
      fit(frame);
      setTimeout(function () { measure(frame); }, 150);
    });
  }
  function wireFrames() {
    var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { load(e.target); io.unobserve(e.target); } });
    }, { rootMargin: "600px 0px" }) : null;
    comps().forEach(function (s) {
      if (io) io.observe(s); else load(s);
      s.querySelectorAll(".comp-head .seg button").forEach(function (b) {
        b.addEventListener("click", function () { setWidth(s, Number(b.getAttribute("data-width"))); });
      });
    });
    $("all-widths").querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        $("all-widths").querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        comps().forEach(function (s) { setWidth(s, Number(b.getAttribute("data-width"))); });
      });
    });
    var t = null;
    window.addEventListener("resize", function () {
      clearTimeout(t);
      t = setTimeout(function () { document.querySelectorAll("iframe[data-key]").forEach(fit); }, 120);
    });
  }

  // ---------- picks ----------
  function readDraft() {
    try { var d = JSON.parse(localStorage.getItem(DRAFT_KEY) || "null"); if (d && typeof d === "object") return d; } catch (e) { /* none */ }
    return null;
  }
  function writeDraft() { try { localStorage.setItem(DRAFT_KEY, JSON.stringify(state)); } catch (e) { /* none */ } }
  function row(cid) { return state.picks[cid] || (state.picks[cid] = { pick: "", note: "", updatedAt: 0 }); }
  function paint(cid, force) {
    var r = row(cid), fs = document.querySelector('fieldset[data-pick="' + cid + '"]');
    if (!fs) return;
    fs.querySelectorAll('input[type="radio"]').forEach(function (i) { i.checked = i.value === r.pick; });
    var ta = fs.querySelector("textarea");
    if (ta && (force || document.activeElement !== ta) && ta.value !== r.note) ta.value = r.note;
    var a = document.querySelector('[data-toc="' + cid + '"]');
    if (a) a.setAttribute("data-picked", String(PICKS.indexOf(r.pick) >= 0));
  }
  function paintAll(force) {
    ids().forEach(function (cid) { paint(cid, force); });
    var gn = $("general-notes");
    if (gn && (force || document.activeElement !== gn) && gn.value !== state.notes) gn.value = state.notes;
    setText("picked", String(ids().filter(function (cid) { return PICKS.indexOf(row(cid).pick) >= 0; }).length));
  }
  function save(key, ref, body) {
    clearTimeout(timers[key]);
    timers[key] = setTimeout(function () {
      delete timers[key];
      if (!db) return;
      setText("status", "Saving…");
      ref().set(body()).then(function () { setText("status", "Saved on the canvas"); },
        function (e) { setText("status", "Could not save (" + ((e && e.code) || "error") + "). Your picks are kept in this browser; try again."); });
    }, 600);
  }
  function savePick(cid) {
    writeDraft(); paintAll(false);
    save("pick:" + cid, function () { return db.collection("picks").doc(cid); },
      function () { var r = row(cid); return { pick: r.pick, note: r.note, updatedAt: r.updatedAt }; });
  }
  function saveNotes() {
    writeDraft();
    save("notes", function () { return db.collection("notes").doc("general"); },
      function () { return { text: state.notes, updatedAt: Date.now() }; });
  }
  function wirePicks() {
    ids().forEach(function (cid) {
      var fs = document.querySelector('fieldset[data-pick="' + cid + '"]');
      fs.querySelectorAll('input[type="radio"]').forEach(function (i) {
        i.addEventListener("change", function () {
          if (!i.checked) return;
          var r = row(cid); r.pick = i.value; r.updatedAt = Date.now(); savePick(cid);
        });
      });
      fs.querySelector("textarea").addEventListener("input", function (e) {
        var r = row(cid); r.note = e.target.value; r.updatedAt = Date.now(); savePick(cid);
      });
    });
    $("general-notes").addEventListener("input", function (e) { state.notes = e.target.value; saveNotes(); });
    $("send-picks").addEventListener("click", onSend);
    $("copy-picks").addEventListener("click", function () {
      var el = $("send-status");
      if (!navigator.clipboard) { setText(el, "Copy is blocked in this view."); return; }
      navigator.clipboard.writeText(picksMarkdown()).then(function () { setText(el, "Copied."); },
        function () { setText(el, "Copy is blocked in this view."); });
    });
  }
  function adoptPick(cid, rec) {
    if (!rec || PICKS.concat([""]).indexOf(rec.pick) < 0) return;
    var r = row(cid);
    if ((rec.updatedAt || 0) < r.updatedAt) return;       // a newer local edit wins
    if (timers["pick:" + cid]) return;                    // an edit in flight wins
    r.pick = rec.pick; r.note = typeof rec.note === "string" ? rec.note : ""; r.updatedAt = rec.updatedAt || 0;
  }
  function subscribe() {
    db.collection("picks").onSnapshot(function (snap) {
      snap.docs.forEach(function (d) { if (ids().indexOf(d.id) >= 0) adoptPick(d.id, d.data()); });
      writeDraft(); paintAll(false);
    }, function (e) { setText("status", "The canvas storage stopped (" + ((e && e.code) || "error") + "). Reload the page."); });
    db.collection("notes").onSnapshot(function (snap) {
      snap.docs.forEach(function (d) {
        var rec = d.data() || {};
        if (d.id === "general" && typeof rec.text === "string" && !timers.notes) state.notes = rec.text;
      });
      paintAll(false);
    }, function () { /* the picks listener reports */ });
  }
  function picksMarkdown() {
    var lines = ["# London component picks", ""];
    ids().forEach(function (cid, i) {
      var r = row(cid);
      lines.push((i + 1) + ". " + nameOf(cid) + " — " + (r.pick ? (r.pick === "redesign" ? "none, redesign" : r.pick.toUpperCase()) : "not picked") +
        (r.note ? " — " + r.note.replace(/\s+/g, " ") : ""));
    });
    if (state.notes) lines.push("", "Notes: " + state.notes.replace(/\s+/g, " "));
    return lines.join("\n");
  }

  // ---------- send ----------
  function snapshotId() { return "s-" + new Date().toISOString().replace(/[:.]/g, "-"); }
  function sendMessage(how, sid) {
    var tell = "Tell Claude Code \"read my picks\", or use Copy picks.";
    if (how === "sent") return "Sent to Claude Code (copy " + sid + "). Claude's reply will appear in the comment thread.";
    if (how === "rate_limited") return "Saved as copy " + sid + ". Sending is limited for a moment; wait, then press Send again.";
    if (how === "consent_required") return "Saved as copy " + sid + ". You didn't allow comments from this page. Press Send again to allow it.";
    if (how === "forbidden" || how === "writers_only") return "Saved as copy " + sid + ". Only an editor of this canvas can send to Claude.";
    if (how === "claude_unavailable") return "Saved on the canvas as copy " + sid + ", but Claude Code couldn't receive it right now. " + tell;
    if (how === "no_session") return "Saved on the canvas as copy " + sid + ", but no Claude Code session is watching this canvas right now. " + tell;
    return "Saved on the canvas as copy " + sid + ", but sending to Claude isn't available here. " + tell;
  }
  function onSend() {
    var el = $("send-status");
    if (sending) return;
    if (!db) { setText(el, "This view cannot send. Use Copy picks."); return; }
    sending = true;
    $("send-picks").setAttribute("aria-disabled", "true");
    setText(el, "Sending…");
    var sid = snapshotId(), all = ids();
    var picked = all.filter(function (cid) { return PICKS.indexOf(row(cid).pick) >= 0; });
    var redo = all.filter(function (cid) { return row(cid).pick === "redesign"; });
    var note = "London canvas picks — " + picked.length + " of " + all.length + " picked, " + redo.length +
      " to redesign. Read db submissions/" + sid + ".";
    // The send starts inside the click (it needs the viewer's gesture), beside the save.
    var sendingP = (!comments ? Promise.resolve("off") : comments.anchorFor($("send")).then(function (anchor) {
      return comments.sendToClaude({ anchor: anchor, text: note });
    }).then(function () { return "sent"; })).catch(function (e) { return (e && e.code) || "error"; });
    var body = { at: new Date().toISOString(), id: sid, notes: state.notes, picks: {} };
    all.forEach(function (cid) { var r = row(cid); body.picks[cid] = { pick: r.pick, note: r.note }; });
    var saving = db.collection("submissions").doc(sid).set(body);
    Promise.all([saving, sendingP]).then(function (r) { setText(el, sendMessage(r[1], sid)); }, function (e) {
      setText(el, "The copy could not be saved (" + ((e && e.code) || "error") + "). Your picks are still here. Press Send again.");
    }).then(function () { sending = false; $("send-picks").setAttribute("aria-disabled", "false"); });
  }

  // ---------- start ----------
  function readOnly(why) {
    db = null;
    document.querySelectorAll("fieldset.pick input, fieldset.pick textarea, #general-notes, #send-picks").forEach(function (x) { x.disabled = true; });
    setText("status", why);
  }
  function connect() {
    var draft = readDraft();
    if (draft && draft.picks) { state.picks = draft.picks; state.notes = typeof draft.notes === "string" ? draft.notes : ""; }
    paintAll(true);
    if (FINAL) { readOnly("Final — the picks are frozen; this page is the record of what was offered."); return; }
    var use = window.claude && window.claude.use;
    if (typeof use !== "function") { readOnly("Read-only view: open the canvas on claude.ai to save picks."); return; }
    use.call(window.claude, "comments").then(function (ns) { if (!ns) return; comments = ns; }, function () {});
    use.call(window.claude, "db").then(function (ns) {
      if (!ns) { readOnly("Read-only view: this canvas has no storage here, so picks cannot be saved."); return; }
      db = ns;
      setText("status", "Connected — picks save as you make them.");
      subscribe();
    }, function () { readOnly("Read-only view: the canvas storage did not answer."); });
  }
  wireFrames();
  wirePicks();
  connect();
})();
