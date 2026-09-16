#!/usr/bin/env python3
"""Gate: the JSON-LD of every built page.

Structured data is the one part of this migration a reviewer cannot eyeball: it ships in
`<script type="application/ld+json">` blocks, Google reads it, and a broken graph fails
silently. Five things are blocking, because each of them either breaks the rich result or
tells Google something untrue:

  parse           — a block that is not valid JSON is invisible to every consumer.
  telephone       — `PHONE_PLACEHOLDER` in a `telephone` value would publish a stand-in as
                    the business' phone number. The extractor drops those keys; if one
                    survives, the dropper missed a path.
  false InStock   — `https://schema.org/InStock` may only appear on `available-puppies/<s>`
                    where `<s>` is a pup whose data/puppies.json status is Available. A
                    sold pup (or any other page) claiming availability is a misrepresented
                    offer, which Merchant listings penalise.
  dangling @id    — a reference (`{"@id": X}`, or an id-shaped string X under
                    isPartOf/publisher/author/…)
                    whose X no node on the same page defines. Deduping the legacy Rank
                    Math graph is exactly the operation that can strand a reference, so
                    the gate checks the result rather than trusting it.
  Product/Offer   — a Product must carry `offers`; an Offer that states one of
                    price/priceCurrency must state both. A price with no currency is
                    ambiguous; an Offer with neither (a bare availability statement) is
                    legitimate and is left alone.

Advisory rows are reported and do not fail: more than one node of a sitewide type on one
page (harmless duplication, but it means a dedupe missed something), `url: ""`, and a
WebPage with no `name`.

Usage: python3 scripts/schema_check.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

LD_RE = re.compile(
    r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S)

PLACEHOLDER_PHONE = "PHONE_PLACEHOLDER"
IN_STOCK = "https://schema.org/InStock"
PUP_PREFIX = "available-puppies/"

# Keys whose value is another *node*, so a bare string there is an @id reference. Keys
# whose schema.org range includes URL — `mainEntityOfPage` above all, which the blog pages
# set to the page's own address — are deliberately absent: a URL string there is a value,
# not a reference, and only its `{"@id": …}` dict form is followed (by the rule below).
REF_KEYS = ("isPartOf", "publisher", "breadcrumb", "worksFor", "about",
            "seller", "provider", "author")
# A string under a REF_KEY is only an id when it looks like one; `"author": "Jane"` is a
# name, not a reference.
ID_LIKE_RE = re.compile(r"^(?:/|https?://)|#")

# One per page is the design; more means a dedupe left a duplicate behind.
SITEWIDE_TYPES = ("WebSite", "LocalBusiness", "Organization", "PetStore", "BreadcrumbList")


def _blocks(text):
    """(parsed blocks, parse errors) for every ld+json script in one page."""
    parsed, errors = [], []
    for i, raw in enumerate(LD_RE.findall(text), start=1):
        try:
            parsed.append(json.loads(raw))
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append("block %d failed to parse: %s" % (i, exc))
    return parsed, errors


def _nodes(block):
    """Flatten one block into its top-level nodes (`@graph` members, or the block)."""
    if isinstance(block, list):
        out = []
        for item in block:
            out.extend(_nodes(item))
        return out
    if isinstance(block, dict):
        if isinstance(block.get("@graph"), list):
            out = []
            for item in block["@graph"]:
                out.extend(_nodes(item))
            return out
        return [block]
    return []


def _walk(node):
    """Yield every dict nested anywhere inside `node`, itself included."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            for found in _walk(value):
                yield found
    elif isinstance(node, list):
        for value in node:
            for found in _walk(value):
                yield found


def _is_reference(d):
    """A dict that only points at a node defined elsewhere."""
    return set(d) == {"@id"} and isinstance(d.get("@id"), str)


def collect_ids(blocks):
    """(ids defined by a real node, references made) across one page's blocks."""
    defined, refs = set(), []
    for block in blocks:
        for d in _walk(block):
            if _is_reference(d):
                refs.append(d["@id"])
                continue
            if isinstance(d.get("@id"), str):
                defined.add(d["@id"])
            for key in REF_KEYS:
                value = d.get(key)
                if isinstance(value, str) and ID_LIKE_RE.search(value):
                    refs.append(value)
    return defined, refs


def _types(node):
    t = node.get("@type")
    return [t] if isinstance(t, str) else [x for x in (t or []) if isinstance(x, str)]


def audit_html(text, available_slugs, slug):
    """Audit one built page's JSON-LD.

    Returns {"parsed": n, "blocking": [...], "advisory": [...]}. `slug` is the page's
    path without leading or trailing slashes; `available_slugs` the pups whose status is
    Available, which is what licenses an InStock claim.
    """
    blocks, blocking = _blocks(text)
    advisory = []

    pup = slug.strip("/")[len(PUP_PREFIX):] if slug.strip("/").startswith(PUP_PREFIX) else None
    may_be_in_stock = pup is not None and pup in set(available_slugs)

    for block in blocks:
        for d in _walk(block):
            phone = d.get("telephone")
            if isinstance(phone, str) and PLACEHOLDER_PHONE in phone:
                blocking.append("placeholder telephone: %r" % phone)
            if isinstance(d.get("url"), str) and d["url"] == "":
                advisory.append('empty url on %s node' % (",".join(_types(d)) or "untyped"))

    if not may_be_in_stock and IN_STOCK in json.dumps(blocks):
        blocking.append("InStock claimed on a page that is not an available puppy (%s)" % slug)

    defined, refs = collect_ids(blocks)
    for ref in sorted(set(refs)):
        if ref not in defined:
            blocking.append("dangling @id reference: %s" % ref)

    counts = {}
    for block in blocks:
        for node in _nodes(block):
            for t in _types(node):
                counts[t] = counts.get(t, 0) + 1
            if "Product" in _types(node) and "offers" not in node:
                blocking.append("Product without offers")
            if "WebPage" in _types(node) and not node.get("name"):
                advisory.append("WebPage without name")
    for block in blocks:
        for d in _walk(block):
            if "Offer" not in _types(d):
                continue
            has_price, has_cur = "price" in d, "priceCurrency" in d
            if has_price != has_cur:
                blocking.append("Offer states %s without %s"
                                % ("price" if has_price else "priceCurrency",
                                   "priceCurrency" if has_price else "price"))
    for t in SITEWIDE_TYPES:
        if counts.get(t, 0) > 1:
            advisory.append("%d %s nodes on one page" % (counts[t], t))

    return {"parsed": len(blocks), "blocking": blocking, "advisory": advisory}


def available_slugs(root=ROOT):
    """Slugs of the pups data/puppies.json marks Available."""
    data = json.loads((pathlib.Path(root) / "data" / "puppies.json")
                      .read_text(encoding="utf-8"))
    return {p["slug"] for p in data if p.get("status") == "Available"}


def page_slug(path, dist):
    """The url path of a built index.html, without leading or trailing slashes."""
    rel = pathlib.Path(path).parent.relative_to(dist).as_posix()
    return "" if rel == "." else rel


HEADER = [
    "# Structured data", "",
    "Every `application/ld+json` block in every built page. Blocking: a block that does",
    "not parse, a `telephone` still holding PHONE_PLACEHOLDER, `InStock` on anything but",
    "an available puppy's page, an `@id` reference no node on the page defines, a Product",
    "with no `offers`, and an Offer stating price without priceCurrency (or the reverse).",
    "An Offer stating neither is a bare availability statement and is left alone.",
    "Advisory: duplicate sitewide nodes, empty `url`, a WebPage with no `name`.", "",
]


def main(root=ROOT, dist=None):
    root = pathlib.Path(root)
    dist = pathlib.Path(dist) if dist else root / "dist"
    avail = available_slugs(root)

    pages, blocking, advisory = 0, [], []
    for path in sorted(dist.rglob("index.html")):
        slug = page_slug(path, dist)
        url = "/%s" % (slug + "/" if slug else "")
        result = audit_html(path.read_text(encoding="utf-8", errors="ignore"), avail, slug)
        pages += 1
        blocking += [(url, m) for m in result["blocking"]]
        advisory += [(url, m) for m in result["advisory"]]

    summary = "examined %d pages; %d blocking, %d advisory" % (pages, len(blocking),
                                                              len(advisory))
    lines = list(HEADER) + ["## Blocking", ""]
    lines += ["- `%s` — %s" % r for r in blocking] if blocking else ["None.", ""]
    lines += ["", "## Advisory", ""]
    lines += ["- `%s` — %s" % r for r in advisory] if advisory else ["None.", ""]
    lines += ["", summary, ""]

    out = root / "docs" / "reports" / "schema.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(summary)
    if blocking:
        sys.exit(1)


if __name__ == "__main__":
    main()
