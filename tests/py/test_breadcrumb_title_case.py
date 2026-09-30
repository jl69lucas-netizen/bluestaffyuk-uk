"""The last breadcrumb is the page's name in the site's Title Case (the design-polish pick 4(a),
the user in chat 2026-09-30; preview docs/artifacts/bsuk-design-polish-preview.html, item 4).

src/layouts/BaseLayout.astro passes the page's crumb title through `titleCase()` from
src/lib/headings.ts, the caser the H1 already goes through, so the trail and the heading name the
page in one case ("How to Choose the Right Blue Staffy Puppy for Your Family", not "How To Choose
The Right ..."). The visible leaf and the BreadcrumbList's last `name` both read that crumb title,
so they must also agree with each other.

The caser is the compiled src/lib/headings.ts, never a Python port: a second caser is a caser that
drifts (tests/py/test_design_components.py says the same). Reads dist/, so it skips until
`npm run build` has run.
"""
import json
import pathlib
import re
import shutil
import subprocess
from html import unescape
from html.parser import HTMLParser

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"


class _Page(HTMLParser):
    """The aria-current crumb's text inside the FIRST Breadcrumb nav (the site's trail, which
    BaseLayout renders before <main>; the kit preview also shows a specimen trail inside <main>),
    and every JSON-LD block."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_nav = 0
        self.leaf_depth = 0
        self.leaf = None
        self.ld_open = False
        self.ld = []
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "nav" and (a.get("aria-label") or "").lower() == "breadcrumb":
            self.in_nav += 1
        elif self.in_nav and self.leaf is None and a.get("aria-current") == "page":
            self.leaf_depth, self.leaf = 1, ""
        elif self.leaf_depth:
            self.leaf_depth += 1
        if tag == "script" and a.get("type") == "application/ld+json":
            self.ld_open, self._buf = True, []

    def handle_endtag(self, tag):
        if tag == "script" and self.ld_open:
            self.ld.append("".join(self._buf))
            self.ld_open = False
        elif self.leaf_depth:
            self.leaf_depth -= 1
        elif tag == "nav" and self.in_nav:
            self.in_nav -= 1

    def handle_data(self, data):
        if self.ld_open:
            self._buf.append(data)
        elif self.leaf_depth:
            self.leaf += data


def _pages():
    out = []
    for f in sorted(DIST.rglob("*.html")):
        p = _Page()
        p.feed(f.read_text())
        if p.leaf is None:
            continue
        lists = [b for b in (json.loads(x) for x in p.ld) if isinstance(b, dict) and b.get("@type") == "BreadcrumbList"]
        out.append((str(f.relative_to(DIST)), re.sub(r"\s+", " ", p.leaf).strip(), lists))
    return out


def _title_case(tmp_path, texts):
    esbuild, node = ROOT / "node_modules/.bin/esbuild", shutil.which("node")
    if not esbuild.exists() or not node:
        pytest.skip("needs node and node_modules/.bin/esbuild (npm install)")
    out = tmp_path / "headings.mjs"
    subprocess.run([str(esbuild), str(ROOT / "src/lib/headings.ts"), "--bundle", "--format=esm",
                    "--platform=node", f"--outfile={out}", "--log-level=error"], check=True)
    driver = (f"const m = await import({json.dumps(out.as_uri())});"
              f"console.log(JSON.stringify({json.dumps(texts)}.map(m.titleCase)));")
    res = subprocess.run([node, "--input-type=module", "-e", driver], check=True, capture_output=True, text=True)
    return json.loads(res.stdout)


def test_every_last_crumb_is_title_cased_and_matches_the_breadcrumb_list(tmp_path):
    if not (DIST / "index.html").exists():
        pytest.skip("run npm run build first")
    pages = _pages()
    # Every routed page but the home page carries a trail; a parser that found none would pass
    # having judged nothing.
    assert len(pages) >= 40, f"only {len(pages)} built pages carry a breadcrumb leaf"
    cased = _title_case(tmp_path, [leaf for _, leaf, _ in pages])
    bad = []
    for (path, leaf, lists), want in zip(pages, cased):
        if leaf != want:
            bad.append(f"{path}: crumb {leaf!r}, titleCase() gives {want!r}")
        if len(lists) != 1:
            bad.append(f"{path}: {len(lists)} BreadcrumbList blocks, expected 1")
            continue
        name = unescape(lists[0]["itemListElement"][-1]["name"])
        if name != leaf:
            bad.append(f"{path}: BreadcrumbList's last name {name!r} is not the visible crumb {leaf!r}")
    assert not bad, f"{len(bad)} crumb(s) off:\n" + "\n".join(bad)
