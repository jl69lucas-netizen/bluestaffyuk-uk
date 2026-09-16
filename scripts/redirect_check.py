#!/usr/bin/env python3
"""Gate: the redirect map and every internal link in the built site.

Four things are checked, because an SEO migration loses ranking to any of them:

  one hop     — every concrete redirect must land on a live page in a single hop. A chain
                (/a/ → /b/ → /c/) leaks link equity and, on Cloudflare, costs a round trip
                per hop; a redirect to a 404 is worse than no redirect at all.
  targets     — the `to` of every rule, wildcard ones included, must exist under dist/.
  internal    — every root-relative href/src in every built page must resolve to a real
                file. A link that only works *through* a redirect is a warning, not a
                failure: Foundation deliberately keeps two legacy in-body links verbatim,
                and rewriting generated pages by hand is not the fix — the extractor's
                rewrite map is, which is a controller decision.
  WP leftovers— any surviving `wp-json`, in-href `/feed/`, `xmlrpc.php`,
                `wp-content/uploads`, the old phone number or its placeholder means a page
                still points at WordPress. `SITE_URL_PLACEHOLDER` is counted, not failed:
                it is expected until the launch domain is set.

Matching follows Cloudflare's own semantics: rules are evaluated top to bottom and the
first match wins, a trailing `*` is a prefix splat, and `/:name/` matches exactly one path
segment (so `/:slug/feed/` never swallows `/a/b/feed/`).

Usage: python3 scripts/redirect_check.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

ASSET_EXTS = {".xml", ".txt", ".webp", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".mp4",
              ".css", ".js", ".json", ".pdf", ".kml"}

# Root-relative references worth following. srcset needs its own pass (comma-separated
# candidates with descriptors), so it is collected separately below.
REF_RE = re.compile(r'(?:href|src|poster|data-src)\s*=\s*["\']([^"\']+)["\']', re.I)
SRCSET_RE = re.compile(r'srcset\s*=\s*["\']([^"\']+)["\']', re.I)
HREF_FEED_RE = re.compile(r'href\s*=\s*["\'][^"\']*/feed/[^"\']*["\']', re.I)

SKIP_PREFIXES = ("#", "mailto:", "tel:", "javascript:", "//", "data:")

# Strings that mean a page still talks to WordPress, or still carries a stand-in that
# should have been replaced before this gate ran.
LEFTOVERS = ("wp-json", "xmlrpc.php", "wp-content/uploads", "447490", "PHONE_PLACEHOLDER")
COUNT_ONLY = "SITE_URL_PLACEHOLDER"


def load_rules(root=ROOT):
    """The redirect map as ordered (from, to) pairs — order is the matching order."""
    data = json.loads((pathlib.Path(root) / "data" / "redirects.json")
                      .read_text(encoding="utf-8"))
    return [(r["from"], r["to"]) for r in data["redirects"]]


def is_concrete(src):
    """True when a rule's `from` is a literal path (no splat, no placeholder)."""
    return "*" not in src and ":" not in src


def _rule_re(src):
    """Compile one rule's `from` into a fullmatch regex.

    `*` is a trailing splat (prefix match on everything before it) and `/:name/` is one
    path segment. Everything else is literal.
    """
    if src.endswith("*"):
        return re.compile(re.escape(src[:-1]) + ".*")
    parts = []
    for seg in src.split("/"):
        parts.append("[^/]+" if seg.startswith(":") else re.escape(seg))
    return re.compile("/".join(parts))


def match_rule(path, rules):
    """The `to` of the first rule matching `path`, or None. First match wins."""
    for src, dest in rules:
        if _rule_re(src).fullmatch(path):
            return dest
    return None


def resolve(path, rules, limit=5):
    """Follow the map from `path`. Returns (hops, final path); stops at `limit` hops."""
    hops, current = 0, path
    while hops < limit:
        dest = match_rule(current, rules)
        if dest is None or dest == current:
            break
        current, hops = dest, hops + 1
    return hops, current


def is_asset(path):
    """True for a path whose extension names a file we serve as-is."""
    return pathlib.PurePosixPath(path).suffix.lower() in ASSET_EXTS


def exists(dist, path):
    """Whether `path` is served by the built site: a page directory or an asset file."""
    dist = pathlib.Path(dist)
    rel = path.strip("/")
    if not rel:
        return (dist / "index.html").is_file()
    if is_asset(path):
        return (dist / rel).is_file()
    return (dist / rel / "index.html").is_file() or (dist / rel).is_file()


def clean_ref(ref):
    """Strip query and fragment; return None for a reference we do not follow."""
    ref = ref.strip()
    if not ref or ref.startswith(SKIP_PREFIXES) or "://" in ref:
        return None
    ref = ref.split("#", 1)[0].split("?", 1)[0]
    if not ref.startswith("/"):
        return None                      # relative links: not root-relative, skip
    return ref


def page_refs(html_text):
    """Every root-relative reference in one built page, de-duplicated, in order."""
    found = []
    for raw in REF_RE.findall(html_text):
        ref = clean_ref(raw)
        if ref:
            found.append(ref)
    for value in SRCSET_RE.findall(html_text):
        for candidate in value.split(","):
            ref = clean_ref(candidate.strip().split()[0] if candidate.strip() else "")
            if ref:
                found.append(ref)
    seen, out = set(), []
    for ref in found:
        if ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


def check_rules(rules, dist):
    """Per-rule verdicts. Returns (problems, examined).

    A concrete `from` must reach its target in exactly one hop; a wildcard or placeholder
    rule only has its target existence checked, because its `from` stands for many paths.
    Chain detection is the same test stated the other way round, and is reported
    explicitly so the offending pair is named.
    """
    problems = []
    for src, dest in rules:
        if not exists(dist, dest):
            problems.append("FAIL target missing: %s -> %s" % (src, dest))
        if not is_concrete(src):
            continue
        hops, final = resolve(src, rules)
        if hops != 1:
            problems.append("FAIL %d hops: %s -> %s" % (hops, src, final))
        onward = match_rule(dest, rules)
        if onward is not None:
            problems.append("FAIL chain: %s -> %s -> %s" % (src, dest, onward))
    return problems, len(rules)


def check_pages(dist, rules):
    """Walk built pages. Returns (problems, refs_examined, redirected, placeholders)."""
    dist = pathlib.Path(dist)
    problems, redirected, placeholders = [], [], 0
    refs_seen = 0
    for path in sorted(dist.rglob("*.html")):
        rel = "/" + str(path.relative_to(dist))
        text = path.read_text(encoding="utf-8", errors="ignore")
        for ref in page_refs(text):
            refs_seen += 1
            if exists(dist, ref):
                continue
            dest = match_rule(ref, rules)
            if dest is not None:
                redirected.append((rel, ref, dest))
            else:
                problems.append("FAIL dead link: %s in %s" % (ref, rel))
        for token in LEFTOVERS:
            if token in text:
                problems.append("FAIL WP leftover %s in %s" % (token, rel))
        if HREF_FEED_RE.search(text):
            problems.append("FAIL WP leftover /feed/ href in %s" % rel)
        placeholders += text.count(COUNT_ONLY)
    return problems, refs_seen, redirected, placeholders


HEADER = [
    "# Redirects and internal links", "",
    "Every concrete redirect must reach a live page in exactly one hop; wildcard and",
    "placeholder rules have only their target checked. Every root-relative reference in",
    "every built page must resolve; one that resolves only *through* a redirect is",
    "reported as a warning, since Foundation keeps two legacy in-body links verbatim and",
    "the fix belongs in the extractor's rewrite map, not in generated HTML. WordPress",
    "leftovers fail outright; `SITE_URL_PLACEHOLDER` is counted only, as it is expected",
    "until the launch domain is set.", "",
]


def main(root=ROOT, dist=None):
    root = pathlib.Path(root)
    dist = pathlib.Path(dist) if dist else root / "dist"
    rules = load_rules(root)

    rule_problems, examined = check_rules(rules, dist)
    page_problems, refs, redirected, placeholders = check_pages(dist, rules)
    problems = rule_problems + page_problems

    summary = ("examined %d redirects, %d internal refs; %d redirected refs; %d problems"
               % (examined, refs, len(redirected), len(problems)))

    lines = list(HEADER)
    lines += ["## Problems", ""]
    lines += ["- %s" % p for p in problems] if problems else ["None.", ""]
    lines += ["", "## Redirected references (warning)", ""]
    if redirected:
        lines += ["| page | reference | redirects to |", "| --- | --- | --- |"]
        lines += ["| %s | %s | %s |" % r for r in redirected]
    else:
        lines.append("None.")
    lines += ["", "SITE_URL_PLACEHOLDER occurrences: %d (expected until launch)"
              % placeholders, "", summary, ""]

    out = root / "docs" / "reports" / "redirects.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(summary)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
