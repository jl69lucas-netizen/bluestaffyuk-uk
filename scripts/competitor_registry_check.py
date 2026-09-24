#!/usr/bin/env python3
"""competitor_registry_check.py — data/competitors.json is well formed, and nothing links a
competitor the registry marks `link_allowed: false`.

  python3 scripts/competitor_registry_check.py [--root DIR]
      exit 0 ok, or no registry yet (says "nothing to check") · 1 problems (listed)

What a schema cannot say is checked here: at most 30 entries, `_meta.total` equals the count,
bare root domains, never the site's own domain, no duplicate id or domain, tier 5 never
linkable, cities only from data/locations.json, and a priority that matches the one derived
from `seed_hits` — the registry agent types it, this script re-derives it.

A bare root domain is the registrable domain: two labels (`example.com`), or three when a
UK-style second level sits under a two-letter country code (`pets4homes.co.uk`). Anything
longer is a subdomain; non-ASCII names go in punycode (`xn--…`).

The link guard bans every domain marked `link_allowed: false` — tier 5 always, and any other
the user marks — across src/, data/boards/ and the external link library, including links
JSON-escaped inside a string (`https:\\/\\/host`, `https:\\u002f\\u002fhost`). It runs only once
the registry itself has no problems, and a scan path that has gone missing is a problem.

Spec: docs/superpowers/specs/2026-09-23-competitor-intel-design.md §4, §12.
"""
import argparse
import json
import pathlib
import re
import sys
from urllib.parse import urlparse

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas/competitors.schema.json"
MAX_ENTRIES = 30
OWN_DOMAIN = "bluestaffyuk"
# lowercase labels separated by dots, nothing else: no scheme, path, port or upper case.
# A leading `www.` is refused separately so the message can say why.
LABEL = r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
BARE = re.compile(rf"(?:{LABEL}\.)+(?:[a-z]{{2,}}|xn--[a-z0-9-]+)")
# second levels under a two-letter country code that make a three-label registrable domain
CC_SECOND_LEVELS = {"co", "org", "me", "ltd", "plc", "ac", "gov", "net", "sch", "com"}
LINK_SCAN = ("src", "data/boards", "docs/reference/external-link-library.md")
LINK_SUFFIXES = {".astro", ".md", ".mdx", ".json", ".ts", ".js", ".html"}
# `https?://` anywhere; scheme-less `//host` only straight after href= or src=, so `//`
# code comments are not read as links. Group 1 is the authority (userinfo@host:port).
# Inside a JSON string a slash may be written `\/` or `\u002f` and a quote `\"`, so
# `https:\/\/host` and `href=\"\/\/host` are links too (Known Issue 47).
SLASH = r"(?:\\?/|\\u002[fF])"
URL = re.compile(r"""(?:https?:|\b(?:href|src)\s*=\s*\\?["']?)""" + SLASH + SLASH
                 + r"""([^/?#\s"'<>)\]\\]+)""", re.I)


def derived_priority(c):
    """high: 5+ distinct seed keywords, or a tier-1 breeder in the top 3 · medium: 2–4 · low: 1."""
    keywords = {h["keyword"] for h in c["seed_hits"]}
    if len(keywords) >= 5 or (c["tier"] == 1 and min(h["position"] for h in c["seed_hits"]) <= 3):
        return "high"
    return "medium" if len(keywords) >= 2 else "low"


def _cities(root):
    """The known cities, or a problem string when data/locations.json cannot be read."""
    try:
        rows = json.loads((root / "data/locations.json").read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError("expected a list of rows")
        return {row["city"] for row in rows}
    except (OSError, ValueError, UnicodeDecodeError, KeyError, TypeError) as exc:
        return f"data/locations.json unreadable: {type(exc).__name__}: {exc}"


def _registrable(d):
    labels = d.split(".")
    if len(labels) == 2:
        return True
    return (len(labels) == 3 and len(labels[2]) == 2 and labels[2].isalpha()
            and labels[1] in CC_SECOND_LEVELS)


PLACEHOLDER = "site_url_placeholder"  # the build's stand-in for BSUK's domain until project 6


def root_domain(url):
    """The registrable domain of a URL or bare host, by the rule above: two labels, or three under a
    CC_SECOND_LEVELS second level and a two-letter country code. The build placeholder is its own
    root; a bare label is None. One helper for the keyword-gap and llm-intel agents' scripts and
    tests/py/test_llm_intel.py."""
    h = (urlparse(url if "//" in url else "//" + url).hostname or "").lower().rstrip(".")
    try:
        h = h.encode("idna").decode()
    except UnicodeError:
        pass
    if h == PLACEHOLDER:
        return h
    labels = h.split(".")
    if len(labels) < 2 or not all(labels):
        return None
    keep = 3 if len(labels) >= 3 and _registrable(".".join(labels[-3:])) else 2
    return ".".join(labels[-keep:])


def problems(reg, root=ROOT):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(reg), key=lambda e: list(e.path))
    if errors:
        return [f"schema: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in errors]
    out, comps = [], reg["competitors"]
    if len(comps) > MAX_ENTRIES:
        out.append(f"{len(comps)} competitors; the registry holds 30 at most")
    if reg["_meta"]["total"] != len(comps):
        out.append(f"_meta.total is {reg['_meta']['total']} but there are {len(comps)} entries")
    known, ids, domains = _cities(root), set(), set()
    if isinstance(known, str):
        out.append(known)
        known = None
    all_domains = [c["root_domain"] for c in comps]
    for c in comps:
        cid, d = c["id"], c["root_domain"]
        if d.startswith("www.") or not BARE.fullmatch(d):
            out.append(f"{cid}: root_domain {d!r} is not a bare root domain "
                       "(lowercase, no scheme, path, port or www.; "
                       "use the punycode xn-- form for a non-ASCII name)")
        elif not _registrable(d):
            out.append(f"{cid}: root_domain {d} is a subdomain; use the registrable domain "
                       "(example.com or example.co.uk)")
        for other in all_domains:
            if d.endswith("." + other):
                out.append(f"{cid}: root_domain {d} overlaps another entry's {other}")
        if OWN_DOMAIN in d:
            out.append(f"{cid}: {d} is the site's own domain")
        if d in domains:
            out.append(f"{cid}: duplicate root_domain {d}")
        if cid in ids:
            out.append(f"duplicate id {cid}")
        ids.add(cid)
        domains.add(d)
        if c["tier"] == 5 and c["link_allowed"]:
            out.append(f"{cid}: tier 5 (suspect seller) must have link_allowed false")
        for city in c["cities"] if known is not None else ():
            if city not in known:
                out.append(f"{cid}: city {city!r} is not in data/locations.json")
        want = derived_priority(c)
        if c["priority"] != want:
            out.append(f"{cid}: priority {c['priority']} but seed_hits give {want}")
    return out


def _host(authority):
    """userinfo@Host:port. → host"""
    return authority.rsplit("@", 1)[-1].split(":")[0].lower().rstrip(".")


def _host_is(host, domain):
    host = _host(host)
    return host == domain or host.endswith("." + domain)


def _banned(reg):
    return sorted({c["root_domain"] for c in reg["competitors"] if not c["link_allowed"]})


def suspect_links(reg, root=ROOT):
    """(problems, files scanned). Nothing is scanned when no domain is banned."""
    banned = _banned(reg)
    if not banned:
        return [], 0
    out, scanned = [], 0
    for rel in LINK_SCAN:
        base = root / rel
        if base.is_file():
            files = [base]
        elif base.is_dir():
            files = sorted(p for p in base.rglob("*") if p.is_file() and p.suffix in LINK_SUFFIXES)
        else:
            out.append(f"{rel} does not exist; the link guard cannot scan it")
            continue
        scanned += len(files)
        for f in files:
            text = f.read_text(encoding="utf-8", errors="replace")
            for n, line in enumerate(text.splitlines(), 1):
                for authority in URL.findall(line):
                    for d in banned:
                        if _host_is(authority, d):
                            out.append(f"{f.relative_to(root).as_posix()}:{n}: links "
                                       f"{_host(authority)} ({d} is link_allowed false)")
    return out, scanned


def _plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    root = ap.parse_args(argv).root
    path = root / "data/competitors.json"
    if not path.is_file():
        print("competitors: no data/competitors.json yet — nothing to check")
        return 0
    try:
        reg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"competitors: data/competitors.json is not valid JSON: {exc}")
        return 1
    out = problems(reg, root)
    comps = reg.get("competitors") if isinstance(reg, dict) else None
    count = len(comps) if isinstance(comps, list) else "?"
    if out:
        summary = f"{count} entries; link check not run; {len(out)} problems"
    else:
        out, scanned = suspect_links(reg, root)
        summary = (f"{count} entries; {_plural(len(_banned(reg)), 'banned domain')}; "
                   f"{scanned} files scanned; {len(out)} problems")
    for p in out:
        print(f"competitors: {p}")
    print(f"competitors: {summary}")
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
