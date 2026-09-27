#!/usr/bin/env python3
"""thread_ledger.py — one ledger of the Reddit and forum threads every page has read.

Parity build, Task 22 (audit row 6.20). Each page's bsuk-reddit-threads run writes
data/queries/raw/<slug>/threads.json; many of the threads (the city-agnostic searches) are
the same across the 28 city pages. data/queries/thread-ledger.json is DERIVED from those
files — never hand-edited — and says, per thread: its title, forum, posted month, reply
count, the questions read from it, when it was read and by which pages. A thread read in
the last REUSE_DAYS days is reused from the ledger instead of being opened again.

  thread_ledger.py --write                 rebuild the ledger from every threads.json
  thread_ledger.py --check                 exit 1 when the ledger is missing or stale
                                           (npm run check:threads)
  thread_ledger.py --known URL [URL ...]   one line per URL: `reuse` (read in the last
                                           REUSE_DAYS days; prints who read it) or `fetch`
  thread_ledger.py --seed URL [URL ...]    prints {"questions", "threads"} for a new page's
                                           threads.json from the ledger — `score` is null:
                                           Step C is scored for THIS page; `stale` is
                                           recomputed against --today
  --root DIR, --today YYYY-MM-DD for tests.

Exit 0 · 1 stale or missing ledger (--check) · 2 bad usage or a URL --seed cannot find.
"""
import argparse
import datetime
import json
import pathlib
import sys
from urllib.parse import urlsplit, urlunsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = pathlib.Path("data/queries/thread-ledger.json")
REUSE_DAYS = 180
STALE_MONTHS = 24          # bsuk-reddit-threads Step C: older than 24 months is stale
REDDIT_HOSTS = {"reddit.com", "old.reddit.com", "np.reddit.com", "new.reddit.com",
                "m.reddit.com", "www.reddit.com"}
ROW_KEYS = ("permalink", "title", "subreddit", "posted", "replies", "score", "stale")
COMMENT = ("Derived by scripts/thread_ledger.py --write from every "
           "data/queries/raw/<slug>/threads.json; never hand-edited. `npm run check:threads` "
           "fails when it is stale. bsuk-reddit-threads reads it before opening a thread.")


def canonical(url):
    """One spelling per thread: https, lower-case host (every reddit host is www.reddit.com),
    no query or fragment, one trailing slash."""
    p = urlsplit(url.strip())
    host = p.netloc.lower()
    if host in REDDIT_HOSTS:
        host = "www.reddit.com"
    path = p.path.rstrip("/") + "/"
    return urlunsplit(("https", host, path, "", ""))


def _threads_files(root):
    return sorted((pathlib.Path(root) / "data/queries/raw").glob("*/threads.json"))


def build(root=ROOT):
    """The ledger dict, from every threads.json whose status is not NOT FETCHED."""
    rows, files = {}, 0
    for f in _threads_files(root):
        d = json.loads(f.read_text(encoding="utf-8"))
        files += 1
        if d.get("status") == "NOT FETCHED":
            continue
        slug, fetched = f.parent.name, d.get("fetched") or ""
        asked = {}
        for qn in d.get("questions", []):
            detail = qn.get("detail") or ""
            if detail.startswith("thread:"):
                asked.setdefault(canonical(detail[len("thread:"):]), []).append(
                    {"text": qn["text"], "fact_source": qn.get("fact_source")})
        for t in d.get("threads", []):
            key = canonical(t["permalink"])
            e = rows.setdefault(key, {"title": None, "subreddit": None, "posted": None,
                                      "replies": None, "first_fetched": fetched,
                                      "last_fetched": "", "questions": [], "used_by": []})
            if fetched >= e["last_fetched"]:     # the latest read's facts win
                e.update(title=t.get("title"), subreddit=t.get("subreddit"),
                         posted=t.get("posted"), replies=t.get("replies"), last_fetched=fetched)
            e["first_fetched"] = min(e["first_fetched"], fetched)
            if slug not in e["used_by"]:
                e["used_by"].append(slug)
            seen = {x["text"] for x in e["questions"]}
            e["questions"] += [x for x in asked.get(key, []) if x["text"] not in seen]
    for e in rows.values():
        e["used_by"].sort()
    return {"_comment": COMMENT, "files": files, "threads": dict(sorted(rows.items()))}


def _day(s):
    return datetime.date.fromisoformat(s)


def _months_between(posted, today):
    y, m = (int(x) for x in posted.split("-")[:2])
    return (today.year - y) * 12 + (today.month - m)


def known(ledger, urls, today):
    """[{"url", "action": "reuse"|"fetch", "last_fetched", "used_by"}] in the order given."""
    out, day = [], _day(today)
    for u in urls:
        e = ledger["threads"].get(canonical(u))
        recent = e is not None and e["last_fetched"] and \
            (day - _day(e["last_fetched"])).days <= REUSE_DAYS
        out.append({"url": canonical(u), "action": "reuse" if recent else "fetch",
                    "last_fetched": e["last_fetched"] if e else None,
                    "used_by": e["used_by"] if e else []})
    return out


def seed(ledger, urls, today):
    """{"questions", "threads"} in threads.json's shape for these ledger threads. Raises
    KeyError for a URL the ledger does not hold."""
    qs, rows, day = [], [], _day(today)
    for u in urls:
        key = canonical(u)
        e = ledger["threads"][key]
        rows.append({"permalink": key, "title": e["title"], "subreddit": e["subreddit"],
                     "posted": e["posted"], "replies": e["replies"], "score": None,
                     "stale": bool(e["posted"]) and _months_between(e["posted"], day) > STALE_MONTHS})
        qs += [{"text": x["text"], "detail": f"thread:{key}", "fact_source": x["fact_source"]}
               for x in e["questions"]]
    return {"questions": qs, "threads": rows}


def _dump(ledger):
    return json.dumps(ledger, indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--today", default=datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--known", nargs="+", metavar="URL")
    g.add_argument("--seed", nargs="+", metavar="URL")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root)
    path = root / LEDGER
    fresh = build(root)
    if a.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_dump(fresh), encoding="utf-8")
        print(f"thread-ledger: wrote {LEDGER} — {len(fresh['threads'])} threads from "
              f"{fresh['files']} threads files")
        return 0
    if a.check:
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != _dump(fresh):
            print(f"thread-ledger: STALE — {LEDGER} does not match the threads files; run "
                  "python3 scripts/thread_ledger.py --write")
            return 1
        print(f"thread-ledger: examined {fresh['files']} threads files, "
              f"{len(fresh['threads'])} threads; 0 problems")
        return 0
    ledger = json.loads(path.read_text(encoding="utf-8")) if path.exists() else fresh
    if a.known:
        for k in known(ledger, a.known, a.today):
            who = ", ".join(k["used_by"])
            print(f"{k['action']} {k['url']}" + (f" — read {k['last_fetched']} by {who}"
                                                  if k["last_fetched"] else " — not in the ledger"))
        return 0
    try:
        print(json.dumps(seed(ledger, a.seed, a.today), indent=2, ensure_ascii=False))
    except KeyError as e:
        print(f"thread-ledger: {e.args[0]} is not in the ledger — open it (Step D)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
