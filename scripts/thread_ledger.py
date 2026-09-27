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
                                           recomputed against --today; each row carries
                                           `seeded_from` (the read it was copied from)
  --root DIR, --today YYYY-MM-DD for tests.

A thread is keyed by its id: every Reddit spelling of one thread (host, subreddit case, slug,
comment permalink, redd.it, .json) is https://www.reddit.com/comments/<id>/; a forum thread
keeps its id parameter (t, topic, p, threadid, id). A row with `seeded_from` was copied from
the ledger, not opened, so it never moves the thread's read date or facts.
--known and --seed read the committed ledger; only --write and --check read the threads files.

Exit 0 · 1 stale or missing ledger (--check) · 2 a malformed threads file, a share link, a
missing ledger, or a URL --seed cannot find.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = pathlib.Path("data/queries/thread-ledger.json")
REUSE_DAYS = 180
STALE_MONTHS = 24          # bsuk-reddit-threads Step C: older than 24 months is stale
FORUM_ID_PARAMS = {"t", "topic", "p", "threadid", "id"}
# The seven keys of a threads.json row (bsuk-reddit-threads Step E); a row copied by --seed
# also carries SEEDED.
ROW_KEYS = ("permalink", "title", "subreddit", "posted", "replies", "score", "stale")
SEEDED = "seeded_from"
COMMENT = ("Derived by scripts/thread_ledger.py --write from every "
           "data/queries/raw/<slug>/threads.json; never hand-edited. `npm run check:threads` "
           "fails when it is stale. bsuk-reddit-threads reads it before opening a thread.")


class Malformed(Exception):
    """A threads file the ledger cannot read; str() is the reason."""


def _is_reddit(host):
    return host == "reddit.com" or host.endswith(".reddit.com")


def _reddit_id(p):
    host = (p.hostname or "").lower()
    if host == "redd.it":
        seg = p.path.strip("/").split("/")[0]
        return seg.lower() if re.fullmatch(r"[A-Za-z0-9]+", seg or "") else None
    if re.search(r"^/r/[^/]+/s/[^/]+", p.path):
        raise ValueError(f"{urlunsplit(p)}: share link — open it and use the resolved permalink")
    m = re.search(r"/comments/([A-Za-z0-9]+)", p.path)
    return m.group(1).lower() if m else None


def canonical(url):
    """The ledger key of a thread. Reddit: https://www.reddit.com/comments/<id>/ whatever the
    host, port, subreddit case, slug, comment or .json suffix. Anything else: https, lower-case
    host, one trailing slash (none after a file name such as viewtopic.php), only its id
    parameters (sorted; with `t` or `topic`, phpBB's post `p` and `id` go), no fragment.
    Raises ValueError for a Reddit share link or a Reddit URL with no thread id."""
    p = urlsplit(url.strip())
    host = (p.hostname or "").lower()
    if _is_reddit(host) or host == "redd.it":
        rid = _reddit_id(p)
        if not rid:
            raise ValueError(f"{url}: not a Reddit thread permalink (no /comments/<id>)")
        return f"https://www.reddit.com/comments/{rid}/"
    keep = [(k, v) for k, v in parse_qsl(p.query) if k.lower() in FORUM_ID_PARAMS]
    if any(k.lower() in ("t", "topic") for k, _ in keep):   # phpBB: the topic is the thread
        keep = [(k, v) for k, v in keep if k.lower() not in ("p", "id")]
    keep.sort()
    path = p.path.rstrip("/")
    if "." not in path.rsplit("/", 1)[-1]:      # a directory-style path ends in one slash;
        path += "/"                              # a script (viewtopic.php) never does
    return urlunsplit(("https", host, path, urlencode(keep), ""))


def display(url):
    """The permalink as people read it: Reddit hosts → www.reddit.com, no query, fragment,
    .json or comment segment (the thread, /r/<sub>/comments/<id>/<slug>/); other hosts are
    canonical()."""
    p = urlsplit(url.strip())
    host = (p.hostname or "").lower()
    if not _is_reddit(host):
        return canonical(url)
    path = re.sub(r"\.json$", "", p.path).rstrip("/")
    m = re.match(r"(.*?/comments/[^/]+(?:/[^/]+)?)", path)
    path = (m.group(1) if m else path) + "/"
    return urlunsplit(("https", "www.reddit.com", path, "", ""))


def _norm(text):
    return " ".join(text.split()).casefold().rstrip("?")


def _date(v, what):
    if not isinstance(v, str):
        raise Malformed(f"{what} is missing (YYYY-MM-DD)")
    try:
        return datetime.date.fromisoformat(v)
    except ValueError:
        raise Malformed(f"{what} {v!r} is not a YYYY-MM-DD date") from None


def _month(v, what):
    if v is None:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})", v) if isinstance(v, str) else None
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise Malformed(f"{what} {v!r} is not a YYYY-MM month")
    return int(m.group(1)), int(m.group(2))


def validate(d):
    """Raise Malformed unless `d` is a readable threads.json. --seed output passes it."""
    if not isinstance(d, dict):
        raise Malformed("not a JSON object")
    if d.get("status") == "NOT FETCHED":
        return
    _date(d.get("fetched"), "`fetched`")
    for key in ("questions", "threads"):
        if not isinstance(d.get(key, []), list):
            raise Malformed(f"`{key}` is not a list")
    for i, qn in enumerate(d.get("questions", [])):
        if not isinstance(qn, dict) or not isinstance(qn.get("text"), str) or not qn["text"].strip():
            raise Malformed(f"questions[{i}] has no `text`")
        detail = qn.get("detail")
        if isinstance(detail, str) and detail.startswith("thread:"):
            try:
                canonical(detail[len("thread:"):])
            except ValueError as e:
                raise Malformed(f"questions[{i}] `detail`: {e}") from None
    for i, t in enumerate(d.get("threads", [])):
        if not isinstance(t, dict) or not isinstance(t.get("permalink"), str) or not t["permalink"]:
            raise Malformed(f"threads[{i}] has no `permalink`")
        extra = set(t) - set(ROW_KEYS) - {SEEDED}
        if extra:
            raise Malformed(f"threads[{i}] has unknown keys {sorted(extra)}")
        try:
            canonical(t["permalink"])
        except ValueError as e:
            raise Malformed(f"threads[{i}] `permalink`: {e}") from None
        _month(t.get("posted"), f"threads[{i}] `posted`")
        if SEEDED in t:
            _date(t[SEEDED], f"threads[{i}] `{SEEDED}`")


def _threads_files(root):
    return sorted((pathlib.Path(root) / "data/queries/raw").glob("*/threads.json"))


def _read(f, root):
    rel = f.relative_to(root).as_posix()
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        validate(d)
    except json.JSONDecodeError as e:
        raise Malformed(f"{rel}: not valid JSON ({e.msg}, line {e.lineno})") from None
    except Malformed as e:
        raise Malformed(f"{rel}: {e}") from None
    return d


def build(root=ROOT):
    """The ledger dict, from every threads.json whose status is not NOT FETCHED. Raises
    Malformed ("<file>: <reason>") for a file it cannot read."""
    root = pathlib.Path(root)
    reads, asked, files = {}, {}, 0
    for f in _threads_files(root):
        d = _read(f, root)
        files += 1
        if d.get("status") == "NOT FETCHED":
            continue
        slug, fetched = f.parent.name, d["fetched"]
        for t in d.get("threads", []):
            key = canonical(t["permalink"])
            seeded = SEEDED in t
            reads.setdefault(key, []).append({"date": t[SEEDED] if seeded else fetched,
                                              "slug": slug, "row": t, "seeded": seeded})
        for qn in d.get("questions", []):
            detail = qn.get("detail") or ""
            if detail.startswith("thread:"):
                asked.setdefault(canonical(detail[len("thread:"):]), []).append(qn)
    rows = {}
    for key, rs in reads.items():
        real = [r for r in rs if not r["seeded"]]
        # A seeded row was copied from the ledger, not opened: only a real read sets the facts
        # and the read date. The latest read wins; a same-date tie goes to the later slug.
        src = max(real or rs, key=lambda r: (r["date"], r["slug"]))
        t = src["row"]
        questions = {}
        for qn in asked.get(key, []):
            k = _norm(qn["text"])
            if k not in questions:
                questions[k] = {"text": qn["text"], "fact_source": qn.get("fact_source")}
            elif questions[k]["fact_source"] is None and qn.get("fact_source"):
                questions[k]["fact_source"] = qn["fact_source"]
        rows[key] = {"permalink": display(t["permalink"]), "title": t.get("title"),
                     "subreddit": t.get("subreddit"), "posted": t.get("posted"),
                     "replies": t.get("replies"),
                     "first_fetched": min(r["date"] for r in (real or rs)),
                     "last_fetched": src["date"],
                     "questions": list(questions.values()),
                     "used_by": sorted({r["slug"] for r in rs})}
    # A question whose `detail` names a thread missing from its file's `threads` list is
    # dropped: the ledger only holds threads some page listed.
    return {"_comment": COMMENT, "files": files, "threads": dict(sorted(rows.items()))}


def _months_between(posted, today):
    y, m = _month(posted, "`posted`")
    return (today.year - y) * 12 + (today.month - m)


def known(ledger, urls, today):
    """[{"url", "action": "reuse"|"fetch", "last_fetched", "used_by"}] in the order given."""
    out, day = [], datetime.date.fromisoformat(today)
    for u in urls:
        e = ledger["threads"].get(canonical(u))
        recent = e is not None and bool(e["last_fetched"]) and \
            (day - datetime.date.fromisoformat(e["last_fetched"])).days <= REUSE_DAYS
        out.append({"url": e["permalink"] if e else display(u),
                    "action": "reuse" if recent else "fetch",
                    "last_fetched": e["last_fetched"] if e else None,
                    "used_by": e["used_by"] if e else []})
    return out


def seed(ledger, urls, today):
    """{"questions", "threads"} in threads.json's shape for these ledger threads; each row's
    `seeded_from` is the ledger read it was copied from. Raises KeyError for a URL the ledger
    does not hold."""
    qs, rows, day = [], [], datetime.date.fromisoformat(today)
    for u in urls:
        key = canonical(u)
        if key not in ledger["threads"]:
            raise KeyError(u)
        e = ledger["threads"][key]
        rows.append({"permalink": e["permalink"], "title": e["title"],
                     "subreddit": e["subreddit"], "posted": e["posted"],
                     "replies": e["replies"], "score": None,
                     "stale": bool(e["posted"]) and _months_between(e["posted"], day) > STALE_MONTHS,
                     SEEDED: e["last_fetched"]})
        qs += [{"text": x["text"], "detail": f"thread:{e['permalink']}",
                "fact_source": x["fact_source"]} for x in e["questions"]]
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
    if a.write or a.check:
        try:
            fresh = build(root)
        except Malformed as e:
            print(f"thread-ledger: {e}")
            return 2
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
    if not path.exists():
        print(f"thread-ledger: {LEDGER} is missing — run python3 scripts/thread_ledger.py --write",
              file=sys.stderr)
        return 2
    try:
        ledger = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(ledger, dict) or not isinstance(ledger.get("threads"), dict):
            raise ValueError("not a ledger object with a `threads` map")
    except (OSError, UnicodeDecodeError, ValueError) as e:
        reason = f"not valid JSON ({e.msg})" if isinstance(e, json.JSONDecodeError) else str(e)
        print(f"thread-ledger: {LEDGER.as_posix()}: {reason} — run "
              "python3 scripts/thread_ledger.py --write", file=sys.stderr)
        return 2
    try:
        if a.known:
            for k in known(ledger, a.known, a.today):
                who = ", ".join(k["used_by"])
                print(f"{k['action']} {k['url']}" + (f" — read {k['last_fetched']} by {who}"
                                                      if k["last_fetched"] else " — not in the ledger"))
            return 0
        print(json.dumps(seed(ledger, a.seed, a.today), indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"thread-ledger: {e}", file=sys.stderr)
        return 2
    except KeyError as e:
        print(f"thread-ledger: {e.args[0]} is not in the ledger — open it (Step D)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
