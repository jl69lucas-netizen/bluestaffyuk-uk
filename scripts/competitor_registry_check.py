#!/usr/bin/env python3
"""competitor_registry_check.py — data/competitors.json is well formed, and nothing links a
competitor the registry marks `link_allowed: false`.

  python3 scripts/competitor_registry_check.py [--root DIR]
      exit 0 ok, or no registry yet (says "nothing to check") · 1 problems (listed)

What a schema cannot say is checked here: at most 30 entries, `_meta.total` equals the count,
bare root domains, never the site's own domain, no duplicate id or domain, tier 5 never
linkable, cities only from data/locations.json, and a priority that matches the one derived
from `seed_hits` — the registry agent types it, this script re-derives it.

Spec: docs/superpowers/specs/2026-09-23-competitor-intel-design.md §4, §12.
"""
import argparse
import json
import pathlib
import re
import sys

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas/competitors.schema.json"
MAX_ENTRIES = 30
OWN_DOMAIN = "bluestaffyuk"
# lowercase labels separated by dots, at least two labels, nothing else: no scheme, path,
# port or upper case. A leading `www.` is refused separately so the message can say why.
BARE = re.compile(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+")
LINK_SCAN = ("src", "data/boards", "docs/reference/external-link-library.md")
LINK_SUFFIXES = {".astro", ".md", ".mdx", ".json", ".ts", ".js", ".html"}
URL = re.compile(r"https?://([^/\s\"'<>)\]]+)", re.I)


def derived_priority(c):
    """high: 5+ distinct seed keywords, or a tier-1 breeder in the top 3 · medium: 2–4 · low: 1."""
    keywords = {h["keyword"] for h in c["seed_hits"]}
    if len(keywords) >= 5 or (c["tier"] == 1 and min(h["position"] for h in c["seed_hits"]) <= 3):
        return "high"
    return "medium" if len(keywords) >= 2 else "low"


def _cities(root):
    return {row["city"] for row in json.loads((root / "data/locations.json").read_text(encoding="utf-8"))}


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
    for c in comps:
        cid, d = c["id"], c["root_domain"]
        if d.startswith("www.") or not BARE.fullmatch(d):
            out.append(f"{cid}: root_domain {d!r} is not a bare root domain "
                       "(lowercase, no scheme, path, port or www.)")
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
        for city in c["cities"]:
            if city not in known:
                out.append(f"{cid}: city {city!r} is not in data/locations.json")
        want = derived_priority(c)
        if c["priority"] != want:
            out.append(f"{cid}: priority {c['priority']} but seed_hits give {want}")
    return out


def _host_is(host, domain):
    host = host.lower().split(":")[0]
    return host == domain or host.endswith("." + domain)


def suspect_links(reg, root=ROOT):
    banned = {c["root_domain"] for c in reg["competitors"] if not c["link_allowed"]}
    if not banned:
        return []
    out = []
    for rel in LINK_SCAN:
        base = root / rel
        if base.is_file():
            files = [base]
        elif base.is_dir():
            files = sorted(p for p in base.rglob("*") if p.is_file() and p.suffix in LINK_SUFFIXES)
        else:
            files = []
        for f in files:
            text = f.read_text(encoding="utf-8", errors="replace")
            for n, line in enumerate(text.splitlines(), 1):
                for host in URL.findall(line):
                    for d in sorted(banned):
                        if _host_is(host, d):
                            out.append(f"{f.relative_to(root).as_posix()}:{n}: links {host} "
                                       f"({d} is link_allowed false)")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
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
    if not out:
        out = suspect_links(reg, root)
    for p in out:
        print(f"competitors: {p}")
    print(f"competitors: {len(reg.get('competitors', []))} entries; {len(out)} problems")
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
