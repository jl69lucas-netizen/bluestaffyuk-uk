/* Fake claude.ai runtime for the answer board harness: an in-memory db with a
   latency-compensated local echo on set() and a confirmed echo 150 ms later, like the real
   store. `window.__seed` (set by an earlier init script) preloads documents; every set() is
   logged in `window.__sets`; `window.__put(path, body)` writes as another viewer would. */
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
      window.__sets.push({ p: p, t: performance.now(), body: JSON.parse(JSON.stringify(body)) });
      store[p] = JSON.parse(JSON.stringify(body)); fire(coll);            // local echo
      return new Promise(function (r) { setTimeout(function () { fire(coll); r(); }, 150); }); // confirmed
    } }; }
  }; } };
  window.claude = { use: function (n) { return Promise.resolve(n === "db" ? db : null); } };
})();
