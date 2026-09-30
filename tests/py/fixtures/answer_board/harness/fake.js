/* Fake claude.ai runtime for the answer board harness: an in-memory db with a
   latency-compensated local echo on set() and a confirmed echo 150 ms later, like the real
   store. `window.__seed` (set by an earlier init script) preloads documents; every set() is
   logged in `window.__sets`; `window.__put(path, body)` writes as another viewer would;
   `window.__rejectSet` makes set() under a path prefix fail. */
window.__sets = [];
(function () {
  var store = {}, listeners = {};
  var seed = window.__seed || {};
  Object.keys(seed).forEach(function (p) { store[p] = JSON.parse(JSON.stringify(seed[p])); });
  function parent(p) { return p.slice(0, p.lastIndexOf("/")); }
  function snapOf(coll) {
    var meta = { fromCache: false, hasPendingWrites: false };
    var docs = Object.keys(store).filter(function (p) { return parent(p) === coll; }).sort()
      .map(function (p) {
        var d = store[p];
        return { id: p.slice(p.lastIndexOf("/") + 1), exists: true, metadata: meta,
          data: function () { return Object.freeze(JSON.parse(JSON.stringify(d))); } };
      });
    return { docs: docs, size: docs.length, empty: !docs.length, metadata: meta,
      docChanges: function () { return []; } };
  }
  function fire(coll) { (listeners[coll] || []).forEach(function (fn) { fn(snapOf(coll)); }); }
  window.__put = function (path, body) { store[path] = JSON.parse(JSON.stringify(body)); fire(parent(path)); };
  var db = { collection: function (coll) { return {
    onSnapshot: function (next) {
      (listeners[coll] = listeners[coll] || []).push(next);
      setTimeout(function () { next(snapOf(coll)); }, 0);
      return function () { listeners[coll] = (listeners[coll] || []).filter(function (f) { return f !== next; }); };
    },
    get: function () { return Promise.resolve(snapOf(coll)); },
    doc: function (id) { var p = coll + "/" + id; return { set: function (body) {
      // window.__rejectSet = "prefix": a set() on a path starting with it fails, unwritten.
      if (window.__rejectSet && p.indexOf(window.__rejectSet) === 0) return Promise.reject({ code: "permission_denied" });
      window.__sets.push({ p: p, t: performance.now(), body: JSON.parse(JSON.stringify(body)) });
      store[p] = JSON.parse(JSON.stringify(body)); fire(coll);            // local echo
      return new Promise(function (r) { setTimeout(function () { fire(coll); r(); }, 150); }); // confirmed
    } }; }
  }; } };
  // Optional comments (window.__withComments): canSendToClaude answers window.__can after a
  // 300 ms lag, so a cached value can be stale; sendToClaude logs to window.__sent or rejects
  // with window.__sendReject.
  window.__can = window.__can || "no_session";
  window.__sent = [];
  var comments = {
    canSendToClaude: function () { return new Promise(function (r) { setTimeout(function () { r(window.__can); }, 300); }); },
    anchorFor: function () { return Promise.resolve({ kind: "element" }); },
    sendToClaude: function (target) {
      if (window.__sendReject) return Promise.reject({ code: window.__sendReject });
      window.__sent.push(target.text);
      return Promise.resolve({ threadId: "t1", commentId: "c1" });
    }
  };
  window.claude = { use: function (n) {
    return Promise.resolve(n === "db" ? db : n === "comments" && window.__withComments ? comments : null);
  } };
})();
