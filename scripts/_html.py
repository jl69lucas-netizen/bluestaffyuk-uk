"""Shared HTML-to-text helpers for the audit scripts.

One implementation, so two gates reading the same built page see the same text. The
entity table below is the UNION of the two tables that had drifted apart in
aeo_audit.py and evidence_audit.py (`&#39;` was only in one, `&middot;` only in the
other), which meant a page could satisfy one gate's regex and not the other's for no
reason but the decoder.

Deliberately regex-based rather than a parser: these helpers run over every built page
in dist/ on every gate run, and the checks they feed are text proxies, not DOM queries.
"""
import re

ENTITIES = (
    ("&amp;", "&"), ("&nbsp;", " "), ("&middot;", "·"), ("&ndash;", "–"),
    ("&mdash;", "—"), ("&rsquo;", "’"), ("&#8217;", "’"), ("&quot;", '"'),
    ("&#39;", "'"),
)


def strip_tags(html):
    """Visible-ish text: <script>/<style> bodies removed, every other tag dropped."""
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", html)


def unescape(t):
    """Decode the entity set the built pages actually emit. `&amp;` is decoded first,
    so `&amp;amp;` becomes `&amp;`, not `&`."""
    for a, b in ENTITIES:
        t = t.replace(a, b)
    return t


def text_of(html):
    """strip_tags + unescape + collapsed whitespace, trimmed."""
    return re.sub(r"\s+", " ", unescape(strip_tags(html))).strip()
