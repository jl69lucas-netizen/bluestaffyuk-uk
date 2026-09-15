# BlueStaffyUK Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the dead WordPress site as an Astro 6.3.1 static site at `~/Downloads/BSUK` with every ranked page migrated verbatim, old pups removed, the phone number scrubbed, a working 301 map, sitemaps, a Formspree contact form and automated checks, without pushing anywhere.

**Architecture:** Hybrid content model. Eleven rich pages are one Astro file each (`src/pages/<slug>/index.astro`) wrapping extracted body HTML. 28 locations and 6 pups are data-driven from JSON via dynamic routes. Blog posts are a markdown content collection served at root slugs. A Python extractor produces all of it from the local clone at `~/bluestaffyuk-site`; Python check scripts and the ported CAG Playwright harness gate `dist/`.

**Tech Stack:** Astro 6.3.1, `@tailwindcss/vite` 4.3, `@astrojs/mdx`, `@astrojs/react` + React 19 (FadeIn island only), Playwright 1.60, Python 3 with `beautifulsoup4`, `lxml`, `Pillow`, `pytest`, `markdownify`.

**Spec:** `docs/superpowers/specs/2026-09-15-foundation-design.md`. Read it first.

**Conventions for every task:**
- Repo root is `/Users/apple/Downloads/BSUK`. Run every command from there.
- Source clone is `/Users/apple/bluestaffyuk-site` (read-only; never modify it).
- Python tests: `python3 -m pytest tests/py -q`. Node: `npm run build`.
- Commit after every task with the trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Never add a git remote. Never push.
- `PHONE_PLACEHOLDER` is the only allowed representation of the phone number anywhere in the repo.

---

## File map

| Path | Responsibility |
|---|---|
| `package.json`, `astro.config.mjs`, `tsconfig.json`, `src/styles/global.css` | scaffold (Task 1) |
| `data/settings.json`, `data/price-matrix.json`, `data/puppies.json` | hand-written site facts (Task 2) |
| `scripts/extract_wp.py` | old HTML → page-map, rich pages, locations.json, blog md (Tasks 3–6) |
| `scripts/bake_images.py` | WebP bake, 760 sibling, 800×800 pup cards, 4:5 portraits (Task 7) |
| `src/layouts/BaseLayout.astro`, `src/components/SiteHeader.astro`, `SiteFooter.astro`, `Breadcrumb.astro`, `Schema.astro` | shell (Task 8) |
| `src/pages/uk-locations/index.astro`, `src/pages/uk-locations/[slug].astro` | hub + locations (Task 9) |
| `src/pages/available-puppies/[slug].astro`, `src/components/PuppyList.astro` | pups (Task 10) |
| `src/content.config.ts`, `src/pages/[...post].astro`, `src/pages/blog/index.astro` | blog (Task 11) |
| `src/components/ContactForm.astro` | Formspree + Turnstile (Task 12) |
| `data/redirects.json`, `scripts/build_redirects.py`, `public/_headers`, `public/robots.txt`, `scripts/build_llms_txt.py` | redirects + robots + llms (Task 13) |
| `scripts/generate_sitemaps.py` | five sitemap shards + index (Task 14) |
| `scripts/migration_parity.py`, `redirect_check.py`, `schema_check.py`, `sitemap_check.py` | gates (Tasks 15–18) |
| `tests/render/**` | ported CAG Playwright harness (Task 19) |
| `docs/reports/foundation-migration.md`, `docs/reports/foundation-gate-report.md`, `docs/artifacts/bsuk-foundation-gate-report.html` | close-out (Task 20) |

---

### Task 1: Scaffold the Astro project

**Files:**
- Create: `package.json`, `astro.config.mjs`, `tsconfig.json`, `src/styles/global.css`, `src/env.d.ts`, `.env.example`, `tests/py/conftest.py`, `requirements.txt`

- [ ] **Step 1: Write package.json**

```json
{
  "name": "bsuk",
  "private": true,
  "type": "module",
  "version": "0.1.0",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "extract": "python3 scripts/extract_wp.py",
    "bake": "python3 scripts/bake_images.py",
    "sitemaps": "python3 scripts/generate_sitemaps.py",
    "redirects": "python3 scripts/build_redirects.py",
    "llms": "python3 scripts/build_llms_txt.py",
    "check:parity": "python3 scripts/migration_parity.py",
    "check:redirects": "python3 scripts/redirect_check.py",
    "check:schema": "python3 scripts/schema_check.py",
    "check:sitemaps": "python3 scripts/sitemap_check.py",
    "check:all": "npm run check:parity && npm run check:redirects && npm run check:schema && npm run check:sitemaps",
    "test:py": "python3 -m pytest tests/py -q",
    "test:render:meta": "playwright test -c tests/render/playwright.config.ts meta.spec.ts",
    "test:render:pages": "playwright test -c tests/render/playwright.config.ts pages.spec.ts"
  },
  "dependencies": {
    "@astrojs/mdx": "^5.0.4",
    "@astrojs/react": "^5.0.4",
    "@tailwindcss/vite": "^4.3.0",
    "react": "^19.2.6",
    "react-dom": "^19.2.6",
    "tailwindcss": "^4.3.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.60.0",
    "@types/react": "^19.2.14",
    "@types/react-dom": "^19.2.3",
    "astro": "^6.3.1",
    "lighthouse": "^13.4.1"
  }
}
```

- [ ] **Step 2: Write astro.config.mjs**

```js
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';

const site = process.env.SITE_URL || 'https://SITE_URL_PLACEHOLDER';

export default defineConfig({
  site,
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'always' },
  vite: { plugins: [tailwindcss()] },
  integrations: [react(), mdx()],
});
```

- [ ] **Step 3: Write tsconfig.json, env.d.ts, global.css, .env.example, requirements.txt**

`tsconfig.json`:
```json
{ "extends": "astro/tsconfigs/strict", "include": [".astro/types.d.ts", "src/**/*"], "exclude": ["dist"] }
```

`src/env.d.ts`:
```ts
/// <reference types="astro/client" />
```

`src/styles/global.css`:
```css
@import "tailwindcss";

:root {
  --hdr: 72px;
  --container: 1200px;
  --text-max: 760px;
}
html { scroll-behavior: auto; overflow-x: clip; }
body { margin: 0; font: 17px/1.65 system-ui, -apple-system, "Segoe UI", sans-serif; color: #1b2430; background: #fff; }
.container { max-width: var(--container); margin: 0 auto; padding: 0 24px; }
.container-text { max-width: var(--text-max); }
main p, main li { max-width: 70ch; }
[id] { scroll-margin-top: calc(var(--hdr) + 16px); }
img { max-width: 100%; height: auto; }
table { border-collapse: collapse; width: 100%; }
td, th { padding: 6px 10px; border-bottom: 1px solid #dad6cc; text-align: left; vertical-align: top; }
.table-wrap { overflow-x: auto; }
@media (max-width: 640px) {
  .stack-table, .stack-table thead, .stack-table tbody, .stack-table tr, .stack-table td, .stack-table th, .stack-table caption { display: block; }
  .stack-table thead { position: absolute; left: -9999px; }
  .stack-table td { border: 0; padding: 4px 0; }
  .stack-table td::before { content: attr(data-label) ": "; font-weight: 600; }
  .stack-table tr { border-bottom: 1px solid #dad6cc; padding: 8px 0; }
}
```

`.env.example`:
```
SITE_URL=https://SITE_URL_PLACEHOLDER
PUBLIC_FORMSPREE_ID=
PUBLIC_TURNSTILE_SITE_KEY=
```

`requirements.txt`:
```
beautifulsoup4==4.12.3
lxml==5.3.0
markdownify==0.13.1
Pillow==10.4.0
pytest==8.3.3
```

`tests/py/conftest.py`:
```python
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
```

- [ ] **Step 4: Install and prove an empty build works**

Create `src/pages/index.astro` as a stub (replaced in Task 8):
```astro
---
import '../styles/global.css';
---
<html lang="en-GB"><head><meta charset="utf-8"><title>BSUK scaffold</title></head><body><main class="container"><h1>Scaffold</h1></main></body></html>
```

Run:
```bash
cd /Users/apple/Downloads/BSUK && npm install && python3 -m pip install -r requirements.txt && npm run build && ls dist/index.html
```
Expected: `dist/index.html` exists, build log ends with `Complete!`.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "chore: scaffold Astro 6.3.1 + Tailwind 4.3 project

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Site facts data files

**Files:**
- Create: `data/settings.json`, `data/price-matrix.json`, `data/puppies.json`
- Test: `tests/py/test_data_files.py`

- [ ] **Step 1: Write the failing test**

```python
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]

def load(name):
    return json.loads((ROOT / "data" / name).read_text())

def test_settings_has_placeholder_phone_and_facts():
    s = load("settings.json")
    assert s["phone"] == "PHONE_PLACEHOLDER"
    assert s["breeder_name"] == "Lisa Bright"
    assert s["deposit_gbp"] == 500 and s["deposit_refundable"] is True
    assert s["delivery_min_gbp"] == 200 and s["delivery_max_gbp"] == 350
    assert s["socials"]["youtube"].startswith("https://www.youtube.com/@")

def test_price_matrix_matches_puppies():
    pm = load("price-matrix.json"); pups = load("puppies.json")
    assert pm["male_gbp"] == 1500 and pm["female_gbp"] == 1700
    assert len(pups) == 6
    for p in pups:
        assert p["price_gbp"] == (pm["male_gbp"] if p["sex"] == "male" else pm["female_gbp"])
        assert p["status"] == "Available"
        assert (ROOT / "assets" / "brand" / p["slug"] / p["card_photo"]).exists()
    assert {p["slug"] for p in pups} == {"roman","byrd","ince","vennie","christa","cheryl"}
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/py/test_data_files.py -q`
Expected: FAIL, `FileNotFoundError: data/settings.json`.

- [ ] **Step 3: Copy pup masters and write the three data files**

```bash
for p in roman byrd ince vennie christa cheryl; do mkdir -p assets/brand/$p; done
S=/Users/apple/Downloads/bluestaffyuk-cms/Assets/Images
cp "$S/Roman1.jpg" "$S/Roman2.jpg" assets/brand/roman/
cp "$S/Byrd1.jpg" assets/brand/byrd/
cp "$S/Ince1.jpg" assets/brand/ince/
cp "$S/Vennie.jpeg" assets/brand/vennie/
cp "$S/Christa.jpeg" assets/brand/christa/
cp "$S/Cheryl1.jpeg" assets/brand/cheryl/
```

`data/settings.json`:
```json
{
  "site_name": "Blue Staffy UK",
  "tagline": "Your Trusted UK Blue Staffy Breeders",
  "breeder_name": "Lisa Bright",
  "address": { "street": "40 Coltmuir Street", "city": "Glasgow", "postcode": "G22 6LU", "country": "GB", "lat": 55.891560, "lng": -4.256577 },
  "phone": "PHONE_PLACEHOLDER",
  "email": "staffies@bluestaffyuk.uk",
  "hours": "Mo-Su 09:00-23:00",
  "price_range": "£1500 - £1700",
  "deposit_gbp": 500,
  "deposit_refundable": true,
  "delivery_min_gbp": 200,
  "delivery_max_gbp": 350,
  "delivery_note": "UK home delivery by DEFRA-approved transport, priced by distance",
  "guarantee_days": null,
  "socials": {
    "x": "https://x.com/bluestaffyuk",
    "youtube": "https://www.youtube.com/@BlueStaffyUK-v2d",
    "instagram": "https://www.instagram.com/bluestaffyukingdom",
    "facebook": "https://www.facebook.com/bluestaffyuk"
  },
  "youtube_embeds": ["g9iV9RVr_Sk", "g88qOo9C94c", "fXhu9jDS6CA"],
  "logo": "/images/blue-staffy-uk-official-logo0.png"
}
```

`data/price-matrix.json`:
```json
{ "currency": "GBP", "male_gbp": 1500, "female_gbp": 1700, "deposit_gbp": 500, "deposit_refundable": true }
```

`data/puppies.json`:
```json
[
  { "slug": "roman",   "name": "Roman",   "sex": "male",   "price_gbp": 1500, "status": "Available", "colour": "Blue and white", "card_photo": "Roman2.jpg", "gallery": ["Roman1.jpg", "Roman2.jpg"] },
  { "slug": "byrd",    "name": "Byrd",    "sex": "male",   "price_gbp": 1500, "status": "Available", "colour": "White", "card_photo": "Byrd1.jpg", "gallery": ["Byrd1.jpg"] },
  { "slug": "ince",    "name": "Ince",    "sex": "male",   "price_gbp": 1500, "status": "Available", "colour": "Blue", "card_photo": "Ince1.jpg", "gallery": ["Ince1.jpg"] },
  { "slug": "vennie",  "name": "Vennie",  "sex": "female", "price_gbp": 1700, "status": "Available", "colour": "Blue and white", "card_photo": "Vennie.jpeg", "gallery": ["Vennie.jpeg"] },
  { "slug": "christa", "name": "Christa", "sex": "female", "price_gbp": 1700, "status": "Available", "colour": "Blue", "card_photo": "Christa.jpeg", "gallery": ["Christa.jpeg"] },
  { "slug": "cheryl",  "name": "Cheryl",  "sex": "female", "price_gbp": 1700, "status": "Available", "colour": "Blue with white blaze", "card_photo": "Cheryl1.jpeg", "gallery": ["Cheryl1.jpeg"] }
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/py/test_data_files.py -q` → `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat(data): site facts, price matrix, six new puppies with masters

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Extractor core — page inventory and body extraction

**Files:**
- Create: `scripts/extract_wp.py`, `tests/py/test_extract_core.py`, `tests/py/fixtures/birmingham.html` (copy of `~/bluestaffyuk-site/uk-locations/blue-staffy-puppies-birmingham/index.html`)

- [ ] **Step 1: Copy the fixture and write the failing tests**

```bash
mkdir -p tests/py/fixtures && cp /Users/apple/bluestaffyuk-site/uk-locations/blue-staffy-puppies-birmingham/index.html tests/py/fixtures/birmingham.html
```

`tests/py/test_extract_core.py`:
```python
import pathlib
from extract_wp import parse_page, classify, RICH_SLUGS
FIX = pathlib.Path(__file__).parent / "fixtures"

def test_parse_page_meta_and_body():
    page = parse_page(FIX / "birmingham.html", url_path="/uk-locations/blue-staffy-puppies-birmingham/")
    assert page.title == "Blue Staffy Puppies Birmingham"
    assert page.description == "Blue Staffy Puppies Birmingham"
    assert page.canonical == "/uk-locations/blue-staffy-puppies-birmingham/"
    assert page.robots.startswith("follow, index")
    assert page.h1 == ""                      # known defect, recorded not fixed
    assert "empty-h1" in page.defects
    assert "<script" not in page.body_html
    assert "wp-json" not in page.body_html and "/feed/" not in page.body_html
    assert page.word_count > 200

def test_classify():
    assert classify("/") == "rich"
    assert classify("/uk-locations/blue-staffy-puppies-birmingham/") == "location"
    assert classify("/blue-staffy-blog-guides/") == "blog"
    assert classify("/category/training/") == "skip"
    assert classify("/form/2029/") == "skip"
    assert classify("/bluestaffyuk-uk/iiashymongmail-com/") == "skip"
    assert "/buy-staffy-puppies-for-sale-uk/" in RICH_SLUGS
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/py/test_extract_core.py -q` → `ModuleNotFoundError: extract_wp`.

- [ ] **Step 3: Write scripts/extract_wp.py (core)**

```python
#!/usr/bin/env python3
"""Extract the old WordPress static export into Astro sources. Verbatim: no rewriting.

Usage: python3 scripts/extract_wp.py [--src /Users/apple/bluestaffyuk-site] [--out .]
"""
import argparse, dataclasses, html, json, pathlib, re
from bs4 import BeautifulSoup, Comment

SRC_DEFAULT = pathlib.Path("/Users/apple/bluestaffyuk-site")
ROOT = pathlib.Path(__file__).resolve().parent.parent

RICH_SLUGS = {
    "/", "/buy-blue-staffy-puppies-uk/", "/blue-staffy-pup-sale-uk/",
    "/buy-staffy-puppies-for-sale-uk/", "/uk-blue-staffy-puppy-buying-guide/",
    "/uk-staffordshire-bull-terrier-guide/", "/blue-staffy-health-uk/",
    "/blue-staffy-uk-breeders/", "/uk-blue-staffy-breeders-contact/",
    "/privacy-policy-uk/", "/thank-you-blue-staffy-puppies-journey/",
}
BLOG_SLUGS = {"/blue-staffy-blog-guides/"}
SKIP_PREFIXES = ("/category/", "/form/", "/bluestaffyuk-uk/", "/blog/",
                 "/buy-blue-staffy-puppies-for-sale-uk/", "/healthy-habits-exercises-for-your-pets/")
OLD_PUPS = ("kane", "kobe", "beth", "alis")
OLD_PUP_IMAGES = {
    "blue-staffy-pup-near-me-available.jpg", "blue-staffy-pup-near-me-available-1.jpg",
    "blue-staffy-puppy-uk-sale.jpg", "tan-white-staffy-puppy-uk.jpg", "white-grey-staffy-puppy-uk.jpg",
}
PHONE_RE = re.compile(r"(\+?44\s?7490\s?571\s?679|07490\s?571\s?679|\+447490571679|tel:\+?447490571679)")
DEAD_HREF_RE = re.compile(r"(/wp-json/|/feed/?$|/comments/feed|xmlrpc\.php|/wp-admin/|/wp-login)")


@dataclasses.dataclass
class Page:
    url_path: str
    kind: str
    title: str
    description: str
    canonical: str
    robots: str
    og_type: str
    h1: str
    body_html: str
    schema: list
    word_count: int
    images: list
    embeds: list
    headings: list
    defects: list
    phone_hits: int
    refresh_flags: list


def classify(url_path: str) -> str:
    if url_path in RICH_SLUGS: return "rich"
    if url_path in BLOG_SLUGS: return "blog"
    if url_path.startswith("/uk-locations/") and url_path != "/uk-locations/": return "location"
    if url_path.startswith(SKIP_PREFIXES): return "skip"
    return "skip"


def _meta(soup, name=None, prop=None):
    tag = soup.find("meta", attrs={"name": name}) if name else soup.find("meta", attrs={"property": prop})
    return html.unescape(tag["content"]).strip() if tag and tag.has_attr("content") else ""


def _strip_chrome(soup):
    for sel in ["script", "style", "noscript", "header.site-header", "footer.site-footer",
                "#ast-mobile-header", ".ast-breadcrumbs-wrapper", "link", "svg.ast-mobile-svg-icon"]:
        for t in soup.select(sel): t.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)): c.extract()


def extract_body(soup) -> BeautifulSoup:
    node = soup.select_one(".entry-content") or soup.select_one("#primary") or soup.body
    body = BeautifulSoup(str(node), "lxml").select_one(".entry-content, #primary, body")
    for a in body.find_all("a", href=True):
        if DEAD_HREF_RE.search(a["href"]): a.unwrap()
    for t in body.select("[style]"):
        if t.name in ("p", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6"): del t["style"]
    for t in body.find_all(True):
        for attr in list(t.attrs):
            if attr.startswith("data-") or attr in ("id",) and t.get("id", "").startswith("uagb"):
                del t[attr]
    for tbl in body.find_all("table"):
        heads = [th.get_text(" ", strip=True) for th in tbl.find_all("th")]
        tbl["class"] = (tbl.get("class") or []) + ["stack-table"]
        for tr in tbl.find_all("tr"):
            for i, td in enumerate(tr.find_all("td")):
                if i < len(heads): td["data-label"] = heads[i]
        tbl.wrap(soup.new_tag("div", attrs={"class": "table-wrap"}))
    return body


def scrub_phone(text: str):
    n = len(PHONE_RE.findall(text))
    return PHONE_RE.sub("PHONE_PLACEHOLDER", text), n


def parse_page(path: pathlib.Path, url_path: str) -> Page:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "lxml")
    schema = []
    for s in soup.find_all("script", type="application/ld+json"):
        try: schema.append(json.loads(s.string or "{}"))
        except json.JSONDecodeError: pass
    title = html.unescape((soup.title.string or "").strip()) if soup.title else ""
    description = _meta(soup, name="description")
    canon = soup.find("link", rel="canonical")
    canonical = re.sub(r"^https?://[^/]+", "", canon["href"]) if canon else url_path
    robots = _meta(soup, name="robots")
    og_type = _meta(soup, prop="og:type")
    _strip_chrome(soup)
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(" ", strip=True) if h1_tag else ""
    body = extract_body(soup)
    body_html, phone_hits = scrub_phone(body.decode_contents())
    title, n1 = scrub_phone(title); description, n2 = scrub_phone(description)
    phone_hits += n1 + n2
    text = BeautifulSoup(body_html, "lxml").get_text(" ", strip=True)
    b = BeautifulSoup(body_html, "lxml")
    images = [{"src": i.get("src", ""), "alt": i.get("alt", "")} for i in b.find_all("img")]
    embeds = [f.get("src", "") for f in b.find_all("iframe")]
    headings = [(t.name, t.get_text(" ", strip=True)) for t in b.find_all(re.compile("^h[1-6]$"))]
    defects, flags = [], []
    if not h1: defects.append("empty-h1")
    if re.search(r"\b\d+ (Sweet )?Blue Staffy Pupp", title): flags.append("count-in-title")
    for m in re.finditer(r"£\s?(850|1,?000|1,?100|1,?200|300)\b", text): flags.append(f"old-price:{m.group(0)}")
    return Page(url_path, classify(url_path), title, description, canonical, robots, og_type, h1,
                body_html, schema, len(text.split()), images, embeds, headings, defects, phone_hits, flags)


def inventory(src: pathlib.Path):
    for f in sorted(src.rglob("index.html")):
        rel = f.parent.relative_to(src).as_posix()
        url_path = "/" if rel == "." else f"/{rel}/"
        if rel.startswith(("wp-content", "wp-includes", "admin", ".git")): continue
        yield url_path, f


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--src", default=str(SRC_DEFAULT)); ap.add_argument("--out", default=str(ROOT))
    args = ap.parse_args()
    from extract_writers import run  # Task 4
    run(pathlib.Path(args.src), pathlib.Path(args.out))
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/py/test_extract_core.py -q` → `2 passed`. If `description` on the fixture differs from the assertion, read the fixture's `<meta name="description">` and correct the assertion to the real value; do not change the extractor.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat(extract): page parser, chrome stripping, phone scrub, table data-labels

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Extractor writers — rich pages, locations.json, page-map.json

**Files:**
- Create: `scripts/extract_writers.py`, `tests/py/test_extract_writers.py`

- [ ] **Step 1: Write the failing test**

```python
import json, pathlib
from extract_wp import parse_page
from extract_writers import write_rich_page, write_locations, write_page_map, astro_frontmatter
FIX = pathlib.Path(__file__).parent / "fixtures"

def test_write_rich_page_creates_astro_with_props(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    page.kind = "rich"; page.url_path = "/demo-page/"
    out = write_rich_page(page, tmp_path)
    assert out == tmp_path / "src/pages/demo-page/index.astro"
    text = out.read_text()
    assert text.startswith("---\nimport BaseLayout")
    assert 'title={meta.title}' in text
    assert "<Fragment set:html={body} />" in text
    assert "PHONE_PLACEHOLDER" in text or "07490" not in text

def test_write_locations_json(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    p = write_locations([page], tmp_path)
    data = json.loads(p.read_text())
    assert data[0]["slug"] == "blue-staffy-puppies-birmingham"
    assert data[0]["city"] == "Birmingham"
    assert data[0]["defects"] == ["empty-h1"]

def test_page_map_records_baseline_not_fetched(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    pm = json.loads(write_page_map([page], tmp_path).read_text())
    row = pm["pages"][0]
    assert row["baseline_gsc"] == "NOT FETCHED — GSC property unverified (domain expired); no exports on disk"
    assert row["kind"] == "location" and row["word_count"] > 200
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/py/test_extract_writers.py -q` → `ModuleNotFoundError: extract_writers`.

- [ ] **Step 3: Write scripts/extract_writers.py**

```python
import json, pathlib, re
from extract_wp import Page, inventory, parse_page, classify, OLD_PUPS, OLD_PUP_IMAGES
from bs4 import BeautifulSoup

NOT_FETCHED = "NOT FETCHED — GSC property unverified (domain expired); no exports on disk"
CITY_RE = re.compile(r"(?:puppies|staffies|staffy|breeder|dogs|puppy)\s*(?:for sale)?\s*(?:in )?(.+?)(?: uk| area)?$", re.I)

def city_from_slug(slug: str) -> str:
    words = slug.replace("-", " ")
    m = CITY_RE.search(words)
    city = (m.group(1) if m else words).strip()
    return " ".join(w if w.lower() in ("under", "de") else w.capitalize() for w in city.split())

def astro_frontmatter(page: Page, layout_rel: str) -> str:
    meta = {"title": page.title, "description": page.description, "canonical": page.canonical,
            "robots": page.robots or "index, follow", "ogType": page.og_type or "article", "schema": page.schema}
    return ("---\n" f"import BaseLayout from '{layout_rel}';\n"
            f"const meta = {json.dumps(meta, ensure_ascii=False)};\n"
            f"const body = {json.dumps(page.body_html, ensure_ascii=False)};\n---\n")

def strip_old_pups(body_html: str):
    """Remove the four sold pups' cards (uagb info-box / image blocks that name them or use their images)."""
    soup = BeautifulSoup(body_html, "lxml")
    removed = 0
    for box in soup.select(".wp-block-uagb-info-box, .wp-block-uagb-image, .wp-block-uagb-container, .wp-block-group"):
        txt = box.get_text(" ", strip=True).lower()
        imgs = {pathlib.Path(i.get("src", "")).name for i in box.find_all("img")}
        names_hit = any(re.search(rf"\bmeet {n}\b|\b{n}['’]s overview\b|\b{n} is\b", txt) for n in OLD_PUPS)
        if (names_hit or imgs & OLD_PUP_IMAGES) and len(txt) < 900:
            box.decompose(); removed += 1
    inner = soup.body.decode_contents() if soup.body else str(soup)
    return inner, removed

def write_rich_page(page: Page, out: pathlib.Path) -> pathlib.Path:
    rel = page.url_path.strip("/")
    d = out / "src/pages" / (rel if rel else "") ; d.mkdir(parents=True, exist_ok=True)
    f = d / "index.astro"
    depth = len([p for p in rel.split("/") if p]) + 1
    layout_rel = "../" * depth + "layouts/BaseLayout.astro"
    f.write_text(astro_frontmatter(page, layout_rel) +
                 "<BaseLayout title={meta.title} description={meta.description} canonical={meta.canonical} "
                 "robots={meta.robots} ogType={meta.ogType} schema={meta.schema}>\n"
                 "  <article class=\"container container-text prose-migrated\">\n    <Fragment set:html={body} />\n  </article>\n"
                 "</BaseLayout>\n")
    return f

def write_locations(pages, out: pathlib.Path) -> pathlib.Path:
    rows = []
    for p in pages:
        slug = p.url_path.strip("/").split("/")[-1]
        rows.append({"slug": slug, "city": city_from_slug(slug), "title": p.title, "h1": p.h1,
                     "description": p.description, "canonical": p.canonical, "robots": p.robots,
                     "body_html": p.body_html, "word_count": p.word_count, "schema": p.schema, "defects": p.defects})
    f = out / "data/locations.json"; f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rows, ensure_ascii=False, indent=2)); return f

def write_page_map(pages, out: pathlib.Path) -> pathlib.Path:
    rows = [{"url": p.url_path, "kind": p.kind, "title": p.title, "h1": p.h1, "word_count": p.word_count,
             "images": len(p.images), "embeds": len(p.embeds), "headings": p.headings, "defects": p.defects,
             "phone_hits": p.phone_hits, "refresh_flags": p.refresh_flags,
             "baseline_gsc": NOT_FETCHED, "baseline_bing": NOT_FETCHED} for p in pages]
    f = out / "data/page-map.json"; f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"generated_from": "/Users/apple/bluestaffyuk-site", "pages": rows}, ensure_ascii=False, indent=2))
    return f

def run(src: pathlib.Path, out: pathlib.Path):
    from extract_blog import write_blog_post  # Task 6
    from extract_images import rewrite_image_srcs  # Task 7
    pages, locs = [], []
    for url_path, f in inventory(src):
        kind = classify(url_path)
        if kind == "skip": continue
        page = parse_page(f, url_path)
        page.body_html, removed = strip_old_pups(page.body_html)
        if removed: page.refresh_flags.append(f"old-pup-cards-removed:{removed}")
        page.body_html = rewrite_image_srcs(page.body_html)
        if kind == "rich": write_rich_page(page, out)
        elif kind == "location": locs.append(page)
        elif kind == "blog": write_blog_post(page, out)
        pages.append(page)
    write_locations(locs, out); write_page_map(pages, out)
    print(f"extracted {len(pages)} pages ({len(locs)} locations)")
```

- [ ] **Step 4: Run tests** → `3 passed` (Task 3 tests still pass too: `python3 -m pytest tests/py -q`).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat(extract): writers for rich pages, locations.json, page-map.json; old pup card removal

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Old pup removal — verify against the real homepage

**Files:**
- Test: `tests/py/test_old_pups.py`, fixture `tests/py/fixtures/home.html` (copy of `~/bluestaffyuk-site/index.html`)

- [ ] **Step 1: Copy fixture, write the failing test**

```bash
cp /Users/apple/bluestaffyuk-site/index.html tests/py/fixtures/home.html
```

```python
import pathlib, re
from extract_wp import parse_page, OLD_PUP_IMAGES
from extract_writers import strip_old_pups
FIX = pathlib.Path(__file__).parent / "fixtures"

def test_homepage_old_pups_gone_but_prose_kept():
    page = parse_page(FIX / "home.html", "/")
    before = page.word_count
    body, removed = strip_old_pups(page.body_html)
    assert removed >= 4
    low = body.lower()
    assert "meet kane" not in low and "kobe’s overview" not in low and "meet beth" not in low and "meet alis" not in low
    assert not any(img in body for img in OLD_PUP_IMAGES)
    assert "Meet Our Affordable Blue Staffy Puppies" in body       # section heading kept
    assert "Maggie" in body and "Jones" in body                    # parents kept
    assert len(body.split()) > before * 0.85
    assert page.phone_hits >= 1 and "07490" not in body and "447490" not in body
```

- [ ] **Step 2: Run** → FAIL on whichever assertion the current selector misses (expected: `removed >= 4` or a name still present).

- [ ] **Step 3: Tune `strip_old_pups`**

Inspect what survived: `python3 -c "from extract_wp import *; from extract_writers import *; p=parse_page(pathlib.Path('tests/py/fixtures/home.html'),'/'); b,_=strip_old_pups(p.body_html); import re; print([m.start() for m in re.finditer('(?i)kane|kobe|beth|alis',b)][:10])"`. Widen the selector list in `strip_old_pups` (add the exact `uagb-block-*` container class that wraps each card, e.g. `.wp-block-uagb-columns` holding the image + info box) until all four cards and their images are gone while the `<h2>` section heading and the parents' section remain. Keep the `len(txt) < 900` guard so a whole section cannot be removed.

- [ ] **Step 4: Run** → `1 passed`, and `python3 -m pytest tests/py -q` all green.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "test(extract): old pups Kane/Kobe/Beth/Alis removed from homepage, prose kept

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Blog post writer (markdown)

**Files:**
- Create: `scripts/extract_blog.py`, `tests/py/test_extract_blog.py`, fixture `tests/py/fixtures/blog-guides.html`

- [ ] **Step 1: Fixture + failing test**

```bash
cp /Users/apple/bluestaffyuk-site/blue-staffy-blog-guides/index.html tests/py/fixtures/blog-guides.html
```

```python
import pathlib
from extract_wp import parse_page
from extract_blog import write_blog_post, faqs_from_body
FIX = pathlib.Path(__file__).parent / "fixtures"

def test_blog_post_markdown(tmp_path):
    page = parse_page(FIX / "blog-guides.html", "/blue-staffy-blog-guides/")
    f = write_blog_post(page, tmp_path)
    assert f == tmp_path / "src/content/blog/blue-staffy-blog-guides.md"
    md = f.read_text()
    assert md.startswith("---\n") and "slug: blue-staffy-blog-guides" in md
    assert 'title: "How To Choose The Right Blue Staffy Puppy' in md
    assert "author: Blue Staffy UK Team" in md
    assert "## " in md or "# " in md
    assert "<script" not in md

def test_faqs_extracted():
    page = parse_page(FIX / "home.html", "/")
    faqs = faqs_from_body(page.body_html)
    assert len(faqs) >= 5 and all(q["question"] and q["answer"] for q in faqs)
```

- [ ] **Step 2: Run** → `ModuleNotFoundError: extract_blog`.

- [ ] **Step 3: Write scripts/extract_blog.py**

```python
import json, pathlib, re
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from extract_wp import Page

def faqs_from_body(body_html: str):
    soup = BeautifulSoup(body_html, "lxml"); out = []
    for item in soup.select(".uagb-faq-item"):
        q = item.select_one(".uagb-question, .uagb-faq-questions")
        a = item.select_one(".uagb-faq-content")
        if q and a: out.append({"question": q.get_text(" ", strip=True), "answer": a.get_text(" ", strip=True)})
    return out

def _date_from_schema(schema):
    for block in schema:
        for node in (block.get("@graph", [block]) if isinstance(block, dict) else []):
            for k in ("datePublished", "dateModified"):
                if isinstance(node, dict) and node.get(k): return node[k][:10]
    return "2025-01-01"

def write_blog_post(page: Page, out: pathlib.Path) -> pathlib.Path:
    slug = page.url_path.strip("/")
    soup = BeautifulSoup(page.body_html, "lxml")
    img = soup.find("img")
    for f in soup.select(".wp-block-uagb-faq"): f.decompose()
    body_md = md(str(soup), heading_style="ATX", strip=["span"])
    fm = {"title": page.title, "slug": slug, "date": _date_from_schema(page.schema), "author": "Blue Staffy UK Team",
          "description": page.description, "canonical": page.canonical,
          "featured_image": img.get("src") if img else "", "featured_image_alt": img.get("alt", "") if img else "",
          "schema_type": "BlogPosting", "faqs": faqs_from_body(page.body_html), "refresh_flags": page.refresh_flags}
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}" if not isinstance(v, str) else f'{k}: "{v.replace(chr(34), chr(39))}"')
    lines += ["---", "", body_md.strip(), ""]
    f = out / "src/content/blog" / f"{slug}.md"; f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("\n".join(lines).replace('author: "Blue Staffy UK Team"', "author: Blue Staffy UK Team").replace(f'slug: "{slug}"', f"slug: {slug}"))
    return f
```

- [ ] **Step 4: Run** → `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat(extract): blog post markdown writer with FAQ frontmatter

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Image pipeline — copy, bake, rewrite srcs

**Files:**
- Create: `scripts/extract_images.py`, `scripts/bake_images.py`, `tests/py/test_images.py`

- [ ] **Step 1: Failing tests**

```python
import pathlib
from PIL import Image
from extract_images import rewrite_image_srcs, stem_for
from bake_images import bake_body_image, bake_puppy_card, MAX_KB

def test_rewrite_srcs_points_to_images_webp():
    html = '<img src="/wp-content/uploads/blue-staffy-puppies-uk-litter1.jpg" srcset="/wp-content/uploads/x.jpg 780w" sizes="(max-width:480px) 150px" alt="a" width="576" height="350">'
    out = rewrite_image_srcs(html)
    assert 'src="/images/blue-staffy-puppies-uk-litter1.webp"' in out
    assert 'srcset="/images/blue-staffy-puppies-uk-litter1-760.webp 760w, /images/blue-staffy-puppies-uk-litter1.webp 1408w"' in out
    assert "wp-content" not in out and 'loading="lazy"' in out and 'alt="a"' in out

def test_stem_for_strips_wp_size_suffix():
    assert stem_for("/wp-content/uploads/foo-768x776.png") == "foo"
    assert stem_for("/wp-content/uploads/cropped-blue-staffy-uk-official-logo0.png") == "cropped-blue-staffy-uk-official-logo0"

def test_bake_body_image_under_budget(tmp_path):
    src = tmp_path / "big.jpg"; Image.new("RGB", (3000, 2000), (40, 80, 120)).save(src, quality=95)
    full, sib = bake_body_image(src, tmp_path / "out", "big")
    assert Image.open(full).size == (1408, 768) and Image.open(sib).size == (760, 415)
    assert full.stat().st_size <= MAX_KB * 1024

def test_bake_puppy_card_square_and_portrait(tmp_path):
    src = tmp_path / "pup.jpg"; Image.new("RGB", (1080, 1350), (90, 90, 90)).save(src)
    card, tall = bake_puppy_card(src, tmp_path / "out", "christa")
    assert Image.open(card).size == (800, 800) and Image.open(tall).size == (800, 1000)
```

- [ ] **Step 2: Run** → `ModuleNotFoundError`.

- [ ] **Step 3: Write scripts/extract_images.py**

```python
import re, pathlib
from bs4 import BeautifulSoup
LOGO_STEMS = {"blue-staffy-uk-official-logo0", "cropped-blue-staffy-uk-official-logo0", "cropped-blue-staffy-uk-official-logo0-1", "cropped-blue-staffy-uk-logo-1"}

def stem_for(src: str) -> str:
    name = pathlib.Path(src.split("?")[0]).stem
    return re.sub(r"-\d{2,4}x\d{2,4}$", "", name)

def rewrite_image_srcs(body_html: str) -> str:
    soup = BeautifulSoup(body_html, "lxml")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "/wp-content/uploads/" not in src: continue
        stem = stem_for(src)
        if stem in LOGO_STEMS:
            img["src"] = f"/images/{stem}.png"; img.attrs.pop("srcset", None); img.attrs.pop("sizes", None); continue
        img["src"] = f"/images/{stem}.webp"
        img["srcset"] = f"/images/{stem}-760.webp 760w, /images/{stem}.webp 1408w"
        img["sizes"] = "(max-width: 800px) 100vw, 760px"
        img.setdefault("loading", "lazy"); img.setdefault("decoding", "async")
        for a in ("title", "role", "class"): img.attrs.pop(a, None)
    return soup.body.decode_contents() if soup.body else str(soup)

def referenced_uploads(body_html: str):
    """(original_path, stem) pairs for every wp-content image in the body."""
    soup = BeautifulSoup(body_html, "lxml")
    return sorted({(i["src"].split("?")[0], stem_for(i["src"])) for i in soup.find_all("img", src=True) if "/wp-content/uploads/" in i["src"]})
```

- [ ] **Step 4: Write scripts/bake_images.py**

```python
#!/usr/bin/env python3
"""Bake every image the migrated pages reference, plus the six pup masters.
Usage: python3 scripts/bake_images.py [--src /Users/apple/bluestaffyuk-site]"""
import argparse, json, pathlib, re, shutil
from PIL import Image, ImageOps, ImageFilter
ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_KB = 95
BOX = (1408, 768)

def _walk(im, out, max_kb=MAX_KB):
    for q in range(82, 39, -3):
        im.save(out, "WEBP", quality=q, method=6)
        if out.stat().st_size <= max_kb * 1024: return q
    return q

def bake_body_image(src, dst_dir, stem, centering=(0.5, 0.5)):
    dst_dir.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if im.width < BOX[0]:  # never upscale small photos; keep native ratio at native width
        full_im = im
    else:
        full_im = ImageOps.fit(im, BOX, Image.LANCZOS, centering=centering)
    full = dst_dir / f"{stem}.webp"; _walk(full_im, full)
    sib_im = full_im.resize((760, round(full_im.height * 760 / full_im.width)), Image.LANCZOS)
    sib = dst_dir / f"{stem}-760.webp"; _walk(sib_im, sib)
    return full, sib

def bake_puppy_card(src, dst_dir, slug, centering=(0.5, 0.4)):
    dst_dir.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    card = dst_dir / f"{slug}-card-800.webp"; _walk(ImageOps.fit(im, (800, 800), Image.LANCZOS, centering=centering), card)
    # 4:5 blur-fill: never crop heads; pad the master onto a blurred copy of itself
    W, H = 800, 1000
    bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    fg = im.copy(); fg.thumbnail((W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    tall = dst_dir / f"{slug}-portrait-4x5.webp"; _walk(bg, tall)
    return card, tall

def main(src_site: pathlib.Path):
    from extract_images import referenced_uploads, LOGO_STEMS
    out = ROOT / "public/images"; out.mkdir(parents=True, exist_ok=True)
    stems = {}
    for f in [*ROOT.glob("src/pages/**/*.astro"), ROOT / "data/locations.json", *ROOT.glob("src/content/blog/*.md")]:
        text = f.read_text()
        for m in re.finditer(r"/images/([a-z0-9._-]+?)(?:-760)?\.(?:webp|png)", text):
            stems.setdefault(m.group(1), None)
    uploads = src_site / "wp-content/uploads"
    for stem in stems:
        masters = [p for p in uploads.rglob(f"{stem}.*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
        if not masters: print(f"MISSING master for {stem}"); continue
        m = max(masters, key=lambda p: p.stat().st_size)
        if stem in LOGO_STEMS: shutil.copy(m, out / f"{stem}.png"); continue
        full, sib = bake_body_image(m, out, stem)
        print(f"{stem}: {full.stat().st_size//1024}KB / {sib.stat().st_size//1024}KB")
    for p in json.loads((ROOT / "data/puppies.json").read_text()):
        bake_puppy_card(ROOT / "assets/brand" / p["slug"] / p["card_photo"], out / "puppies", p["slug"])
        for g in p["gallery"]:
            bake_body_image(ROOT / "assets/brand" / p["slug"] / g, out / "puppies", f"{p['slug']}-{pathlib.Path(g).stem.lower()}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--src", default="/Users/apple/bluestaffyuk-site")
    main(pathlib.Path(ap.parse_args().src))
```

- [ ] **Step 5: Run tests** → `4 passed`. Then run the full extraction and bake for real:

```bash
npm run extract && npm run bake | tail -20 && ls public/images | wc -l && ls public/images/puppies
```
Expected: `extracted 40 pages (28 locations)`, no `MISSING master` lines (if any appear, the stem regex in `stem_for` needs the size suffix handled; fix and re-run), `public/images/puppies` holds 6 `-card-800.webp` + 6 `-portrait-4x5.webp` + gallery files.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat(images): bake pipeline (WebP <95KB, 760 sibling, pup cards + 4:5 portraits); run extraction

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: BaseLayout, header, footer, schema, breadcrumb

**Files:**
- Create: `src/layouts/BaseLayout.astro`, `src/components/SiteHeader.astro`, `src/components/SiteFooter.astro`, `src/components/Breadcrumb.astro`, `src/components/Schema.astro`, `src/lib/site.ts`
- Delete: stub `src/pages/index.astro` (the extractor already wrote the real one)

- [ ] **Step 1: Write src/lib/site.ts**

```ts
import settings from '../../data/settings.json';
export const SITE = settings;
export const SITE_URL = (import.meta.env.SITE ?? 'https://SITE_URL_PLACEHOLDER').replace(/\/$/, '');
export const NAV = [
  { href: '/', label: 'Home' },
  { href: '/buy-blue-staffy-puppies-uk/', label: 'Puppies for Sale' },
  { href: '/uk-staffordshire-bull-terrier-guide/', label: 'Staffy Guide' },
  { href: '/blue-staffy-health-uk/', label: 'Health' },
  { href: '/uk-locations/', label: 'UK Locations' },
  { href: '/blog/', label: 'Blog' },
  { href: '/uk-blue-staffy-breeders-contact/', label: 'Contact' },
];
export const abs = (path: string) => `${SITE_URL}${path}`;
```

- [ ] **Step 2: Write Schema.astro**

```astro
---
import { SITE, SITE_URL, abs } from '../lib/site';
interface Props { extra?: unknown[]; path: string; title: string }
const { extra = [], path, title } = Astro.props;
const org = {
  '@context': 'https://schema.org', '@type': 'LocalBusiness', '@id': `${SITE_URL}/#business`,
  name: SITE.site_name, url: SITE_URL, email: SITE.email, priceRange: SITE.price_range,
  address: { '@type': 'PostalAddress', streetAddress: SITE.address.street, addressLocality: SITE.address.city,
             postalCode: SITE.address.postcode, addressCountry: SITE.address.country },
  geo: { '@type': 'GeoCoordinates', latitude: SITE.address.lat, longitude: SITE.address.lng },
  openingHours: SITE.hours, sameAs: Object.values(SITE.socials), image: abs(SITE.logo),
  ...(SITE.phone !== 'PHONE_PLACEHOLDER' ? { telephone: SITE.phone } : {}),
};
const website = { '@context': 'https://schema.org', '@type': 'WebSite', '@id': `${SITE_URL}/#website`, url: SITE_URL, name: SITE.site_name };
const crumbs = path.split('/').filter(Boolean);
const breadcrumb = { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [
  { '@type': 'ListItem', position: 1, name: 'Home', item: `${SITE_URL}/` },
  ...crumbs.map((c, i) => ({ '@type': 'ListItem', position: i + 2, name: i === crumbs.length - 1 ? title : c.replace(/-/g, ' '),
                              item: abs('/' + crumbs.slice(0, i + 1).join('/') + '/') })) ] };
const blocks = [org, website, ...(crumbs.length ? [breadcrumb] : []), ...extra.filter((b) => b && typeof b === 'object')];
---
{blocks.map((b) => <script type="application/ld+json" set:html={JSON.stringify(b)} />)}
```

Note: migrated pages carry their old Rank Math `@graph` blocks in `meta.schema`; they are passed as `extra` verbatim. `scripts/schema_check.py` (Task 17) flags duplicate types so project 4 can consolidate; Foundation only guarantees they parse and contain no false `InStock`.

- [ ] **Step 3: Write SiteHeader.astro, SiteFooter.astro, Breadcrumb.astro**

`SiteHeader.astro`:
```astro
---
import { SITE, NAV } from '../lib/site';
---
<header class="site-header" style="position:sticky;top:0;z-index:50;background:#fff;border-bottom:1px solid #dad6cc;height:var(--hdr)">
  <div class="container" style="display:flex;align-items:center;justify-content:space-between;gap:16px;height:100%">
    <a href="/" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;font-weight:600">
      <img src={SITE.logo} alt={`${SITE.site_name} logo`} width="44" height="44" />
      <span>{SITE.site_name}</span>
    </a>
    <nav aria-label="Main"><ul style="display:flex;gap:18px;list-style:none;margin:0;padding:0;flex-wrap:wrap">
      {NAV.map((n) => <li><a href={n.href}>{n.label}</a></li>)}
    </ul></nav>
  </div>
</header>
```

`SiteFooter.astro`:
```astro
---
import { SITE, NAV } from '../lib/site';
import locations from '../../data/locations.json';
---
<footer class="site-footer" style="margin-top:64px;padding:40px 0;background:#1b2430;color:#e9ecf0">
  <div class="container" style="display:grid;gap:32px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">
    <div><h3>{SITE.site_name}</h3><p>{SITE.tagline}</p>
      <p>{SITE.address.street}, {SITE.address.city} {SITE.address.postcode}<br /><a href={`mailto:${SITE.email}`} style="color:inherit">{SITE.email}</a></p>
      <p><a href={SITE.socials.facebook} rel="noopener" target="_blank" style="color:inherit">Facebook</a> · <a href={SITE.socials.instagram} rel="noopener" target="_blank" style="color:inherit">Instagram</a> · <a href={SITE.socials.youtube} rel="noopener" target="_blank" style="color:inherit">YouTube</a> · <a href={SITE.socials.x} rel="noopener" target="_blank" style="color:inherit">X</a></p></div>
    <div><h3>Quick Pages</h3><ul style="list-style:none;padding:0">{NAV.map((n) => <li><a href={n.href} style="color:inherit">{n.label}</a></li>)}<li><a href="/privacy-policy-uk/" style="color:inherit">Privacy Policy</a></li></ul></div>
    <div><h3>Cities We Serve</h3><ul style="list-style:none;padding:0;columns:2">{locations.map((l) => <li><a href={`/uk-locations/${l.slug}/`} style="color:inherit">{l.city}</a></li>)}</ul></div>
  </div>
  <div class="container" style="margin-top:24px;font-size:13px;opacity:.8">© {new Date().getFullYear()} {SITE.site_name}. All rights reserved.</div>
</footer>
```

`Breadcrumb.astro`:
```astro
---
interface Props { path: string; title: string }
const { path, title } = Astro.props;
const crumbs = path.split('/').filter(Boolean);
---
{crumbs.length > 0 && <nav aria-label="Breadcrumb" class="container" style="font-size:14px;padding-top:12px"><ol style="display:flex;gap:8px;list-style:none;padding:0;margin:0;flex-wrap:wrap">
  <li><a href="/">Home</a></li>
  {crumbs.map((c, i) => <li>› {i === crumbs.length - 1 ? <span aria-current="page">{title}</span> : <a href={'/' + crumbs.slice(0, i + 1).join('/') + '/'}>{c.replace(/-/g, ' ')}</a>}</li>)}
</ol></nav>}
```

- [ ] **Step 4: Write BaseLayout.astro**

```astro
---
import '../styles/global.css';
import SiteHeader from '../components/SiteHeader.astro';
import SiteFooter from '../components/SiteFooter.astro';
import Breadcrumb from '../components/Breadcrumb.astro';
import Schema from '../components/Schema.astro';
import { SITE, abs } from '../lib/site';
interface Props { title: string; description: string; canonical?: string; robots?: string; ogType?: string; ogImage?: string; schema?: unknown[]; h1?: string }
const { title, description, canonical = Astro.url.pathname, robots = 'index, follow', ogType = 'website', ogImage = SITE.logo, schema = [] } = Astro.props;
const path = canonical.replace(/^https?:\/\/[^/]+/, '');
---
<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content={description} />
  <meta name="robots" content={robots} />
  <link rel="canonical" href={abs(path)} />
  <meta property="og:type" content={ogType} /><meta property="og:title" content={title} /><meta property="og:description" content={description} /><meta property="og:url" content={abs(path)} /><meta property="og:image" content={abs(ogImage)} /><meta property="og:locale" content="en_GB" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="/images/cropped-blue-staffy-uk-official-logo0-1.png" />
  <Schema extra={schema} path={path} title={title} />
</head>
<body>
  <a href="#main" style="position:absolute;left:-9999px">Skip to content</a>
  <SiteHeader />
  <Breadcrumb path={path} title={title} />
  <main id="main"><slot /></main>
  <SiteFooter />
</body>
</html>
```

- [ ] **Step 5: Build and inspect**

```bash
rm -f src/pages/index.astro.bak; npm run build 2>&1 | tail -5 && grep -c "application/ld+json" dist/index.html && grep -o "<title>[^<]*" dist/buy-blue-staffy-puppies-uk/index.html && grep -c PHONE_PLACEHOLDER dist/index.html; grep -c "447490" dist/index.html
```
Expected: build `Complete!`; ≥ 3 ld+json blocks; the real old title; phone count `0` for `447490`. If the extractor's `index.astro` was overwritten by the Task 1 stub, re-run `npm run extract`.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat(layout): BaseLayout with header, footer, breadcrumb and JSON-LD; rich pages build

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: Location pages and the /uk-locations/ hub

**Files:**
- Create: `src/pages/uk-locations/[slug].astro`, `src/pages/uk-locations/index.astro`

- [ ] **Step 1: Write [slug].astro**

```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
import locations from '../../../data/locations.json';
export function getStaticPaths() { return locations.map((l) => ({ params: { slug: l.slug }, props: { loc: l } })); }
const { loc } = Astro.props;
---
<BaseLayout title={loc.title} description={loc.description} canonical={`/uk-locations/${loc.slug}/`} robots={loc.robots || 'index, follow'} ogType="article" schema={loc.schema}>
  <article class="container container-text prose-migrated"><Fragment set:html={loc.body_html} /></article>
</BaseLayout>
```

- [ ] **Step 2: Write index.astro (hub)**

```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
import locations from '../../../data/locations.json';
const sorted = [...locations].sort((a, b) => a.city.localeCompare(b.city));
---
<BaseLayout title="Blue Staffy Puppies by UK Location | Blue Staffy UK" description="Find Blue Staffy puppies for sale near you. Blue Staffy UK delivers KC-registered Staffordshire Bull Terrier puppies from Glasgow to every UK city and county." canonical="/uk-locations/">
  <section class="container container-text">
    <h1>Blue Staffy Puppies by UK Location</h1>
    <p>We are based in Glasgow and deliver across the whole of the UK. Choose your nearest city for local details.</p>
    <ul style="columns:2;gap:24px">{sorted.map((l) => <li><a href={`/uk-locations/${l.slug}/`}>{l.h1 || l.title}</a></li>)}</ul>
  </section>
</BaseLayout>
```

- [ ] **Step 3: Build and verify**

```bash
npm run build 2>&1 | tail -3 && ls dist/uk-locations | wc -l && test -f dist/uk-locations/blue-staffy-puppies-york/index.html && echo york-ok
```
Expected: `29` (28 cities + index.html), `york-ok`.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat(locations): 28 data-driven location pages plus /uk-locations/ hub

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: Puppy pages and PuppyList component

**Files:**
- Create: `src/pages/available-puppies/[slug].astro`, `src/pages/available-puppies/index.astro`, `src/components/PuppyList.astro`
- Modify: `src/pages/buy-blue-staffy-puppies-uk/index.astro`, `src/pages/index.astro` (insert `<PuppyList />` after the article; data, not prose)

- [ ] **Step 1: Write PuppyList.astro**

```astro
---
import puppies from '../../data/puppies.json';
import { SITE } from '../lib/site';
const avail = puppies.filter((p) => p.status === 'Available');
---
<section id="available-puppies" class="container" aria-labelledby="avail-h2">
  <h2 id="avail-h2">Available Blue Staffy Puppies</h2>
  <p>{avail.length} puppies available now. Males £{SITE.price_range.split(' - ')[0].slice(1)}, females £{SITE.price_range.split(' - ')[1].slice(1)}. {SITE.delivery_note}, £{SITE.delivery_min_gbp}–£{SITE.delivery_max_gbp}, or collect in Glasgow after a refundable £{SITE.deposit_gbp} deposit.</p>
  <ul style="display:grid;gap:20px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));list-style:none;padding:0">
    {avail.map((p) => <li style="border:1px solid #dad6cc;border-radius:8px;overflow:hidden">
      <a href={`/available-puppies/${p.slug}/`}><img src={`/images/puppies/${p.slug}-card-800.webp`} alt={`${p.name}, ${p.colour.toLowerCase()} ${p.sex} Blue Staffy puppy for sale`} width="800" height="800" loading="lazy" decoding="async" /></a>
      <div style="padding:12px 14px"><h3 style="margin:0 0 4px"><a href={`/available-puppies/${p.slug}/`}>{p.name}</a></h3>
        <p style="margin:0">{p.sex === 'male' ? 'Male' : 'Female'} · {p.colour} · <strong>£{p.price_gbp.toLocaleString('en-GB')}</strong></p></div>
    </li>)}
  </ul>
</section>
```

- [ ] **Step 2: Write available-puppies/[slug].astro**

```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
import puppies from '../../../data/puppies.json';
import { SITE, abs } from '../../lib/site';
export function getStaticPaths() { return puppies.map((p) => ({ params: { slug: p.slug }, props: { p } })); }
const { p } = Astro.props;
const title = `${p.name} – ${p.sex === 'male' ? 'Male' : 'Female'} Blue Staffy Puppy for Sale | Blue Staffy UK`;
const description = `${p.name} is a ${p.colour.toLowerCase()} ${p.sex} Staffordshire Bull Terrier puppy, £${p.price_gbp.toLocaleString('en-GB')}, available now from Blue Staffy UK in Glasgow with UK-wide delivery.`;
const schema = [{ '@context': 'https://schema.org', '@type': 'Product', name: `${p.name} – Blue Staffy puppy`, image: abs(`/images/puppies/${p.slug}-card-800.webp`), description,
  brand: { '@type': 'Brand', name: SITE.site_name },
  offers: { '@type': 'Offer', price: p.price_gbp, priceCurrency: 'GBP', availability: p.status === 'Available' ? 'https://schema.org/InStock' : 'https://schema.org/SoldOut', url: abs(`/available-puppies/${p.slug}/`), seller: { '@id': `${abs('')}/#business` } } }];
---
<BaseLayout title={title} description={description} canonical={`/available-puppies/${p.slug}/`} ogType="product" ogImage={`/images/puppies/${p.slug}-card-800.webp`} schema={schema}>
  <article class="container" style="display:grid;gap:32px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
    <div><img src={`/images/puppies/${p.slug}-portrait-4x5.webp`} alt={`${p.name}, ${p.colour.toLowerCase()} ${p.sex} Blue Staffy puppy`} width="800" height="1000" fetchpriority="high" />
      {p.gallery.length > 1 && <ul style="display:flex;gap:8px;list-style:none;padding:0">{p.gallery.map((g) => <li><img src={`/images/puppies/${p.slug}-${g.split('.')[0].toLowerCase()}-760.webp`} alt={`${p.name} photo`} width="120" height="65" loading="lazy" /></li>)}</ul>}</div>
    <div><h1>{p.name}: {p.colour} {p.sex === 'male' ? 'Male' : 'Female'} Blue Staffy Puppy</h1>
      <p><strong>£{p.price_gbp.toLocaleString('en-GB')}</strong> · {p.status}</p>
      <dl><dt>Sex</dt><dd>{p.sex}</dd><dt>Colour</dt><dd>{p.colour}</dd><dt>Deposit</dt><dd>£{SITE.deposit_gbp}, refundable</dd><dt>Delivery</dt><dd>{SITE.delivery_note}, £{SITE.delivery_min_gbp}–£{SITE.delivery_max_gbp}; or collect in Glasgow</dd></dl>
      <p><a href="/uk-blue-staffy-breeders-contact/" style="display:inline-block;padding:10px 20px;background:#2c4a6b;color:#fff;border-radius:50px;text-decoration:none">Enquire about {p.name}</a></p></div>
  </article>
</BaseLayout>
```

- [ ] **Step 3: Write available-puppies/index.astro**

```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
import PuppyList from '../../components/PuppyList.astro';
---
<BaseLayout title="Available Blue Staffy Puppies | Blue Staffy UK" description="Six KC-registered Blue Staffy puppies available now from Blue Staffy UK in Glasgow: three males at £1,500 and three females at £1,700, with UK-wide delivery." canonical="/available-puppies/">
  <PuppyList />
</BaseLayout>
```

- [ ] **Step 4: Insert PuppyList into the two sale surfaces**

In `src/pages/buy-blue-staffy-puppies-uk/index.astro` and `src/pages/index.astro`: add `import PuppyList from '../../components/PuppyList.astro';` (homepage: `'../components/PuppyList.astro'`) to the frontmatter and place `<PuppyList />` immediately before `</BaseLayout>`. Do not edit `body`.

- [ ] **Step 5: Build and verify**

```bash
npm run build 2>&1 | tail -3 && ls dist/available-puppies && grep -c '"@type":"Product"' dist/available-puppies/roman/index.html && grep -c "available-puppies/christa" dist/index.html
```
Expected: 7 entries (6 pups + index.html), `1`, `≥1`.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat(puppies): six pup pages with Product schema, PuppyList on sale page and homepage

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 11: Blog collection, root-slug posts and /blog/ index

**Files:**
- Create: `src/content.config.ts`, `src/pages/[...post].astro`, `src/pages/blog/index.astro`

- [ ] **Step 1: content.config.ts**

```ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(), slug: z.string(), date: z.string(), author: z.string(), description: z.string(),
    canonical: z.string(), featured_image: z.string().optional(), featured_image_alt: z.string().optional(),
    schema_type: z.string().default('BlogPosting'),
    faqs: z.array(z.object({ question: z.string(), answer: z.string() })).default([]),
    refresh_flags: z.array(z.string()).default([]),
  }),
});
export const collections = { blog };
```

- [ ] **Step 2: [...post].astro**

```astro
---
import { getCollection, render } from 'astro:content';
import BaseLayout from '../layouts/BaseLayout.astro';
import { abs, SITE } from '../lib/site';
export async function getStaticPaths() {
  const posts = await getCollection('blog');
  return posts.map((post) => ({ params: { post: post.data.slug }, props: { post } }));
}
const { post } = Astro.props;
const { Content } = await render(post);
const d = post.data;
const schema = [
  { '@context': 'https://schema.org', '@type': d.schema_type, headline: d.title, datePublished: d.date, author: { '@type': 'Organization', name: d.author }, publisher: { '@id': `${abs('')}/#business` }, image: d.featured_image ? abs(d.featured_image) : abs(SITE.logo), mainEntityOfPage: abs(`/${d.slug}/`) },
  ...(d.faqs.length ? [{ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: d.faqs.map((f) => ({ '@type': 'Question', name: f.question, acceptedAnswer: { '@type': 'Answer', text: f.answer } })) }] : []),
];
---
<BaseLayout title={d.title} description={d.description} canonical={`/${d.slug}/`} ogType="article" ogImage={d.featured_image || SITE.logo} schema={schema}>
  <article class="container container-text"><Content />
    {d.faqs.length > 0 && <section><h2>Frequently Asked Questions</h2>{d.faqs.map((f) => <details><summary>{f.question}</summary><p>{f.answer}</p></details>)}</section>}
  </article>
</BaseLayout>
```

- [ ] **Step 3: blog/index.astro**

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
const posts = (await getCollection('blog')).sort((a, b) => b.data.date.localeCompare(a.data.date));
---
<BaseLayout title="Blue Staffy Blog & Guides | Blue Staffy UK" description="Guides from Blue Staffy UK on choosing, buying and raising a Blue Staffordshire Bull Terrier puppy in the UK." canonical="/blog/">
  <section class="container container-text"><h1>Blue Staffy Blog and Guides</h1>
    <ul style="list-style:none;padding:0;display:grid;gap:24px">{posts.map((p) => <li><h2><a href={`/${p.data.slug}/`}>{p.data.title}</a></h2><p>{p.data.description}</p></li>)}</ul>
  </section>
</BaseLayout>
```

- [ ] **Step 4: Build and verify**

```bash
npm run build 2>&1 | tail -3 && test -f dist/blue-staffy-blog-guides/index.html && test -f dist/blog/index.html && echo blog-ok
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat(blog): content collection, root-slug posts, /blog/ index

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 12: Contact form (Formspree + Turnstile)

**Files:**
- Create: `src/components/ContactForm.astro`
- Modify: `src/pages/uk-blue-staffy-breeders-contact/index.astro` (append `<ContactForm />` before `</BaseLayout>`)

- [ ] **Step 1: Write ContactForm.astro**

```astro
---
import puppies from '../../data/puppies.json';
import { SITE, abs } from '../lib/site';
const fid = import.meta.env.PUBLIC_FORMSPREE_ID || 'FORMSPREE_ID_PLACEHOLDER';
const tsk = import.meta.env.PUBLIC_TURNSTILE_SITE_KEY || '';
const action = fid === 'FORMSPREE_ID_PLACEHOLDER' ? '#contact' : `https://formspree.io/f/${fid}`;
---
<section id="contact" class="container container-text">
  <h2>Enquire About a Puppy</h2>
  <form method="POST" action={action} data-form="contact" style="display:grid;gap:14px;max-width:560px">
    <input type="hidden" name="_next" value={abs('/thank-you-blue-staffy-puppies-journey/')} />
    <input type="hidden" name="_subject" value="New Blue Staffy enquiry" />
    <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off" />
    <label>Your name <input name="name" required autocomplete="name" /></label>
    <label>Email <input type="email" name="email" required autocomplete="email" /></label>
    <label>Phone <input type="tel" name="phone" autocomplete="tel" /></label>
    <label>Town or postcode <input name="location" autocomplete="postal-code" /></label>
    <label>Which puppy? <select name="puppy" required>
      <option value="">Choose…</option>
      {puppies.filter((p) => p.status === 'Available').map((p) => <option value={p.slug}>{p.name} · {p.sex === 'male' ? 'Male' : 'Female'} · £{p.price_gbp.toLocaleString('en-GB')}</option>)}
      <option value="collection-glasgow">Collection in Glasgow after a refundable £{SITE.deposit_gbp} deposit</option>
      <option value="waiting-list">Join the waiting list for the next litter</option>
    </select></label>
    <label>Message <textarea name="message" rows="5" required></textarea></label>
    {tsk && <div class="cf-turnstile" data-sitekey={tsk}></div>}
    <button type="submit" style="padding:12px 22px;border-radius:12px;border:0;background:#2c4a6b;color:#fff;font-weight:600">Send enquiry</button>
    <p style="font-size:13px">We reply by email. Your details are used only to answer your enquiry. See our <a href="/privacy-policy-uk/">privacy policy</a>.</p>
  </form>
  {tsk && <script is:inline src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>}
  <script is:inline>
    document.querySelector('form[data-form="contact"]')?.addEventListener('submit', (e) => {
      const f = e.target; if (f.getAttribute('action') === '#contact') { e.preventDefault(); console.log('contact form (stub):', Object.fromEntries(new FormData(f))); alert('Form stub: set PUBLIC_FORMSPREE_ID to post for real.'); }
    });
  </script>
</section>
```

- [ ] **Step 2: Wire into the contact page and build**

Add `import ContactForm from '../../components/ContactForm.astro';` and `<ContactForm />` before `</BaseLayout>` in `src/pages/uk-blue-staffy-breeders-contact/index.astro`.

```bash
npm run build 2>&1 | tail -3 && grep -c 'name="puppy"' dist/uk-blue-staffy-breeders-contact/index.html && grep -o 'Collection in Glasgow[^<]*' dist/uk-blue-staffy-breeders-contact/index.html
```
Expected: `1` and `Collection in Glasgow after a refundable £500 deposit`.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat(contact): Formspree form with puppy select, Turnstile slot and local stub

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 13: Redirects, headers, robots, llms.txt

**Files:**
- Create: `data/redirects.json`, `scripts/build_redirects.py`, `scripts/build_llms_txt.py`, `public/_headers`, `public/robots.txt`, `public/404.html`, `tests/py/test_redirects_build.py`

- [ ] **Step 1: Failing test**

```python
import json, pathlib
from build_redirects import render
ROOT = pathlib.Path(__file__).resolve().parents[2]

def test_render_redirects_lines():
    rows = json.loads((ROOT / "data/redirects.json").read_text())["redirects"]
    text = render(rows)
    assert "/uk-locations/staffordshire-bull-terrier-puppies-for-sale-essex/ /uk-locations/staffy-puppies-for-sale-essex/ 301" in text
    assert "/form/* /uk-blue-staffy-breeders-contact/ 301" in text
    assert "/wp-json/* / 301" in text
    assert "/admin/* / 301" in text
    assert not any(l.startswith("/sitemap") for l in text.splitlines())   # sitemaps are static files, never redirected

def test_no_chains():
    rows = json.loads((ROOT / "data/redirects.json").read_text())["redirects"]
    froms = {r["from"] for r in rows}
    assert not [r for r in rows if r["to"] in froms], "a redirect target is itself redirected"
```

- [ ] **Step 2: Run** → `ModuleNotFoundError: build_redirects`.

- [ ] **Step 3: Write data/redirects.json**

```json
{ "redirects": [
  { "from": "/uk-locations/staffordshire-bull-terrier-puppies-for-sale-essex/", "to": "/uk-locations/staffy-puppies-for-sale-essex/", "type": 301, "reason": "typo slug linked from 32 pages" },
  { "from": "/legal/privacy-policy/", "to": "/privacy-policy-uk/", "type": 301, "reason": "dead legal link" },
  { "from": "/privacy-policy/", "to": "/privacy-policy-uk/", "type": 301, "reason": "dead legal link" },
  { "from": "/form/*", "to": "/uk-blue-staffy-breeders-contact/", "type": 301, "reason": "WP form pages" },
  { "from": "/category/training/", "to": "/blog/", "type": 301, "reason": "WP category" },
  { "from": "/category/puppy-buying-guide-uk/", "to": "/blog/", "type": 301, "reason": "WP category" },
  { "from": "/category/*", "to": "/blog/", "type": 301, "reason": "any other WP category" },
  { "from": "/healthy-habits-exercises-for-your-pets/", "to": "/uk-staffordshire-bull-terrier-guide/", "type": 301, "reason": "redirect stub, care intent" },
  { "from": "/bluestaffyuk-uk/iiashymongmail-com/", "to": "/blue-staffy-uk-breeders/", "type": 301, "reason": "WP author page" },
  { "from": "/bluestaffyuk-uk/*", "to": "/blue-staffy-uk-breeders/", "type": 301, "reason": "WP author namespace" },
  { "from": "/buy-blue-staffy-puppies-for-sale-uk/", "to": "/buy-blue-staffy-puppies-uk/", "type": 301, "reason": "kept from old map" },
  { "from": "/feed/", "to": "/", "type": 301, "reason": "WP feed" },
  { "from": "/comments/feed/", "to": "/", "type": 301, "reason": "WP feed" },
  { "from": "/*/feed/", "to": "/", "type": 301, "reason": "WP per-page feeds" },
  { "from": "/wp-json/*", "to": "/", "type": 301, "reason": "WP API" },
  { "from": "/xmlrpc.php", "to": "/", "type": 301, "reason": "WP xmlrpc" },
  { "from": "/wp-admin/*", "to": "/", "type": 301, "reason": "WP admin" },
  { "from": "/wp-login.php", "to": "/", "type": 301, "reason": "WP login" },
  { "from": "/admin", "to": "/", "type": 301, "reason": "Decap CMS not carried over" },
  { "from": "/admin/*", "to": "/", "type": 301, "reason": "Decap CMS not carried over" }
] }
```

- [ ] **Step 4: Write scripts/build_redirects.py and scripts/build_llms_txt.py**

`build_redirects.py`:
```python
#!/usr/bin/env python3
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

def render(rows):
    lines = ["# Generated from data/redirects.json — do not edit by hand"]
    lines += [f'{r["from"]} {r["to"]} {r["type"]}' for r in rows]
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    rows = json.loads((ROOT / "data/redirects.json").read_text())["redirects"]
    (ROOT / "public/_redirects").write_text(render(rows)); print(f"wrote {len(rows)} redirects")
```

`build_llms_txt.py`:
```python
#!/usr/bin/env python3
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
pm = json.loads((ROOT / "data/page-map.json").read_text())["pages"]
s = json.loads((ROOT / "data/settings.json").read_text())
lines = [f"# {s['site_name']}: {s['tagline']}", "", f"> Glasgow-based Staffordshire Bull Terrier breeder. {s['address']['street']}, {s['address']['city']} {s['address']['postcode']}.", "", "## Sitemaps", "- [XML sitemap](/sitemap_index.xml)", "", "## Pages"]
for p in sorted(pm, key=lambda r: r["url"]):
    if "noindex" in (p.get("robots") or "") or p["url"].startswith("/thank-you"): continue
    lines.append(f"- [{p['title']}]({p['url']}): {p['word_count']} words")
lines += ["", "## Available puppies", "- [Available Blue Staffy Puppies](/available-puppies/)", "", "## Locations", "- [UK locations hub](/uk-locations/)"]
(ROOT / "public/llms.txt").write_text("\n".join(lines) + "\n"); print("wrote llms.txt")
```

`public/_headers`:
```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
```

`public/robots.txt`:
```
User-agent: *
Allow: /

Sitemap: https://SITE_URL_PLACEHOLDER/sitemap_index.xml
```
(`generate_sitemaps.py` in Task 14 rewrites the Sitemap line from `SITE_URL`.)

`public/404.html`:
```html
<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>Page not found | Blue Staffy UK</title><meta name="robots" content="noindex"></head><body style="font-family:system-ui;padding:40px"><h1>Page not found</h1><p>Try the <a href="/">homepage</a>, <a href="/buy-blue-staffy-puppies-uk/">puppies for sale</a> or <a href="/uk-locations/">UK locations</a>.</p></body></html>
```

- [ ] **Step 5: Run tests and generators**

```bash
python3 -m pytest tests/py/test_redirects_build.py -q && npm run redirects && npm run llms && head -5 public/_redirects && head -12 public/llms.txt
```

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat(seo): 301 map, _headers, robots, llms.txt, 404

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 14: Sitemaps (five shards + index)

**Files:**
- Create: `scripts/generate_sitemaps.py`, `tests/py/test_sitemaps_gen.py`

- [ ] **Step 1: Failing test**

```python
import pathlib
from generate_sitemaps import shard_for, build_shards

def test_shard_routing():
    assert shard_for("/") == "page"
    assert shard_for("/uk-locations/") == "page"
    assert shard_for("/uk-locations/blue-staffy-puppies-york/") == "location"
    assert shard_for("/available-puppies/roman/") == "puppy"
    assert shard_for("/available-puppies/") == "page"
    assert shard_for("/blue-staffy-blog-guides/") == "post"
    assert shard_for("/blog/") == "page"
    assert shard_for("/thank-you-blue-staffy-puppies-journey/") is None

def test_video_shard_from_embeds(tmp_path):
    d = tmp_path / "dist"; (d / "x").mkdir(parents=True)
    (d / "x/index.html").write_text('<html><head><title>T</title><meta name="description" content="D"></head><body><iframe src="https://www.youtube.com/embed/g9iV9RVr_Sk"></iframe></body></html>')
    (d / "index.html").write_text("<html><head><title>H</title></head><body></body></html>")
    shards = build_shards(d, "https://example.test", blog_slugs={"x"})
    assert [u for u, _ in shards["video"]] == ["https://example.test/x/"]
    assert shards["video"][0][1][0]["id"] == "g9iV9RVr_Sk"
```

- [ ] **Step 2: Run** → `ModuleNotFoundError`.

- [ ] **Step 3: Write scripts/generate_sitemaps.py**

```python
#!/usr/bin/env python3
"""Five shards + index from dist/. Every page in exactly one shard; noindex excluded.
Run after `astro build`: python3 scripts/generate_sitemaps.py"""
import datetime, html, json, os, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BASE = (os.environ.get("SITE_URL") or "https://SITE_URL_PLACEHOLDER").rstrip("/")
TODAY = datetime.date.today().isoformat()
SHARDS = ("page", "post", "location", "puppy", "video")

def blog_slugs_from_content():
    return {re.search(r'^slug:\s*"?([^"\n]+)"?', f.read_text(), re.M).group(1) for f in (ROOT / "src/content/blog").glob("*.md")}

def shard_for(url_path: str, blog_slugs=frozenset()):
    if url_path.startswith("/thank-you"): return None
    if url_path.startswith("/uk-locations/") and url_path != "/uk-locations/": return "location"
    if url_path.startswith("/available-puppies/") and url_path != "/available-puppies/": return "puppy"
    if url_path.strip("/") in blog_slugs: return "post"
    return "page"

def _pages(dist):
    for f in sorted(dist.rglob("index.html")):
        rel = f.parent.relative_to(dist).as_posix()
        yield ("/" if rel == "." else f"/{rel}/"), f.read_text(encoding="utf-8", errors="ignore")

def build_shards(dist, base, blog_slugs):
    out = {s: [] for s in SHARDS}
    for url_path, text in _pages(dist):
        if re.search(r'<meta name="robots" content="[^"]*noindex', text): continue
        s = shard_for(url_path, blog_slugs)
        if s is None: continue
        out[s].append((base + url_path, TODAY))
        vids = re.findall(r'youtube\.com/embed/([A-Za-z0-9_-]{6,})', text)
        if vids:
            title = html.unescape((re.search(r"<title>(.*?)</title>", text, re.S) or [None, ""])[1]).strip()
            desc = html.unescape((re.search(r'<meta name="description" content="([^"]*)"', text) or [None, ""])[1])
            out["video"].append((base + url_path, [{"id": v, "title": title, "description": desc} for v in dict.fromkeys(vids)]))
    return out

def write(shards):
    def url(loc, lastmod, extra=""): return f"  <url><loc>{html.escape(loc)}</loc><lastmod>{lastmod}</lastmod>{extra}</url>"
    files = []
    for name in ("page", "post", "location", "puppy"):
        if not shards[name]: continue
        body = "\n".join(url(l, m) for l, m in shards[name])
        (DIST / f"{name}-sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'); files.append(f"{name}-sitemap.xml")
    if shards["video"]:
        rows = []
        for loc, vids in shards["video"]:
            ex = "".join(f'<video:video><video:thumbnail_loc>https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg</video:thumbnail_loc><video:title>{html.escape(v["title"])}</video:title><video:description>{html.escape(v["description"])}</video:description><video:player_loc>https://www.youtube.com/embed/{v["id"]}</video:player_loc></video:video>' for v in vids)
            rows.append(url(loc, TODAY, ex))
        (DIST / "video-sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n' + "\n".join(rows) + "\n</urlset>\n"); files.append("video-sitemap.xml")
    idx = "\n".join(f"  <sitemap><loc>{BASE}/{f}</loc><lastmod>{TODAY}</lastmod></sitemap>" for f in files)
    (DIST / "sitemap_index.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{idx}\n</sitemapindex>\n')
    for target in (DIST / "robots.txt", ROOT / "public/robots.txt"):
        if target.exists(): target.write_text(re.sub(r"Sitemap: .*", f"Sitemap: {BASE}/sitemap_index.xml", target.read_text()))
    return files

if __name__ == "__main__":
    shards = build_shards(DIST, BASE, blog_slugs_from_content()); files = write(shards)
    print({k: len(v) for k, v in shards.items()}, files)
```

- [ ] **Step 4: Run tests, build, generate**

```bash
python3 -m pytest tests/py/test_sitemaps_gen.py -q && npm run build 2>&1 | tail -1 && npm run sitemaps
```
Expected: `{'page': 15, 'post': 1, 'location': 28, 'puppy': 6, 'video': 5}` (page = 11 rich minus thank-you = 10, plus `/uk-locations/`, `/available-puppies/`, `/blog/` = 13; adjust the expected number to what the run prints if the blog index or hub counts differ, and confirm each URL by eye).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat(seo): sitemap generator (page/post/location/puppy/video + index)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 15: Gate — migration parity

**Files:**
- Create: `scripts/migration_parity.py`, `tests/py/test_parity.py`

- [ ] **Step 1: Failing test**

```python
from migration_parity import visible_stats, compare

def test_visible_stats_counts():
    st = visible_stats('<html><body><h1>A</h1><p>one two three</p><img src="x"><iframe src="y"></iframe><script>zzz</script></body></html>')
    assert st["words"] == 4 and st["headings"] == ["h1:A"] and st["images"] == 1 and st["embeds"] == 1

def test_compare_flags_big_drop():
    old = {"words": 1000, "headings": ["h1:A", "h2:B"], "images": 3, "embeds": 1}
    ok = compare(old, {"words": 985, "headings": ["h1:A", "h2:B"], "images": 3, "embeds": 1}, allowance=0)
    bad = compare(old, {"words": 900, "headings": ["h1:A"], "images": 2, "embeds": 1}, allowance=0)
    assert ok["pass"] and not bad["pass"] and "words" in bad["failures"] and "headings" in bad["failures"]
```

- [ ] **Step 2: Run** → `ModuleNotFoundError`.

- [ ] **Step 3: Write scripts/migration_parity.py**

```python
#!/usr/bin/env python3
"""Old page vs built page: words, headings, images, embeds. Fails on >2% word drop beyond allowance."""
import json, pathlib, re, sys
from bs4 import BeautifulSoup
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path("/Users/apple/bluestaffyuk-site")
PHONE_RE = re.compile(r"\+?44\s?7490\s?571\s?679|07490\s?571\s?679")

def visible_stats(html_text: str, scope=None):
    soup = BeautifulSoup(html_text, "lxml")
    for t in soup(["script", "style", "noscript", "header", "footer", "nav"]): t.decompose()
    node = soup.select_one(scope) if scope else soup
    node = node or soup
    return {"words": len(node.get_text(" ", strip=True).split()),
            "headings": [f"{h.name}:{h.get_text(' ', strip=True)}" for h in node.find_all(re.compile("^h[1-6]$"))],
            "images": len(node.find_all("img")), "embeds": len(node.find_all("iframe"))}

def compare(old, new, allowance=0):
    fails = {}
    if new["words"] < (old["words"] - allowance) * 0.98: fails["words"] = (old["words"], new["words"])
    if new["headings"] != old["headings"]: fails["headings"] = (len(old["headings"]), len(new["headings"]))
    if new["images"] < old["images"]: fails["images"] = (old["images"], new["images"])
    if new["embeds"] < old["embeds"]: fails["embeds"] = (old["embeds"], new["embeds"])
    return {"pass": not fails, "failures": fails}

def main():
    pm = json.loads((ROOT / "data/page-map.json").read_text())["pages"]
    rows, bad = [], 0
    for p in pm:
        old_html = (SRC / p["url"].strip("/") / "index.html").read_text(encoding="utf-8", errors="ignore")
        new_f = ROOT / "dist" / p["url"].strip("/") / "index.html"
        old = visible_stats(old_html, ".entry-content"); new = visible_stats(new_f.read_text(), "article.prose-migrated, main")
        allowance = len(PHONE_RE.findall(old_html)) * 2 + (120 if any(f.startswith("old-pup-cards-removed") for f in p["refresh_flags"]) else 0)
        old_h = [h for h in old["headings"] if not re.search(r"(?i)meet (kane|kobe|beth|alis)|(kane|kobe|beth|alis)['’]s overview", h)]
        old["headings"] = old_h
        new["headings"] = [h for h in new["headings"] if h not in ("h2:Available Blue Staffy Puppies", "h2:Enquire About a Puppy") and not h.startswith("h3:")] if any(f.startswith("old-pup-cards-removed") for f in p["refresh_flags"]) else new["headings"]
        r = compare(old, new, allowance); rows.append((p["url"], old, new, r)); bad += not r["pass"]
    lines = ["| URL | words old→new | headings | images | embeds | result |", "|---|---|---|---|---|---|"]
    for u, o, n, r in rows:
        lines.append(f"| {u} | {o['words']}→{n['words']} | {len(o['headings'])}→{len(n['headings'])} | {o['images']}→{n['images']} | {o['embeds']}→{n['embeds']} | {'PASS' if r['pass'] else 'FAIL ' + ','.join(r['failures'])} |")
    (ROOT / "docs/reports").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/reports/parity.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines)); print(f"examined {len(rows)} pages, {bad} failing")
    sys.exit(1 if bad else 0)

if __name__ == "__main__": main()
```

- [ ] **Step 4: Run tests, then the gate**

```bash
python3 -m pytest tests/py/test_parity.py -q && npm run check:parity | tail -8
```
Expected: `examined 40 pages, 0 failing`. If a page fails on headings, the heading filter in `main()` must be widened for the specific removed pup heading (never for any other heading); if it fails on words, inspect the extractor for dropped content before touching the allowance.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "gate: migration parity (words, headings, images, embeds per page)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 16: Gate — redirects and internal links

**Files:**
- Create: `scripts/redirect_check.py`, `tests/py/test_redirect_check.py`

- [ ] **Step 1: Failing test**

```python
from redirect_check import match_rule, resolve

RULES = [("/form/*", "/uk-blue-staffy-breeders-contact/"), ("/a/", "/b/"), ("/b/", "/c/")]

def test_match_wildcard():
    assert match_rule("/form/2029/", RULES) == "/uk-blue-staffy-breeders-contact/"
    assert match_rule("/nope/", RULES) is None

def test_resolve_detects_chain():
    hops, final = resolve("/a/", RULES)
    assert hops == 2 and final == "/c/"
```

- [ ] **Step 2: Run** → `ModuleNotFoundError`.

- [ ] **Step 3: Write scripts/redirect_check.py**

```python
#!/usr/bin/env python3
"""Every redirect resolves in one hop to a page that exists in dist/; every internal href in dist/ resolves; no WP leftovers."""
import json, pathlib, re, sys
from bs4 import BeautifulSoup
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

def match_rule(path, rules):
    for frm, to in rules:
        if frm.endswith("*"):
            if path.startswith(frm[:-1]): return to
        elif frm.startswith("/*/"):
            if re.fullmatch("/[^/]+" + re.escape(frm[2:]), path): return to
        elif path == frm: return to
    return None

def resolve(path, rules, limit=5):
    hops = 0
    while hops < limit:
        nxt = match_rule(path, rules)
        if nxt is None or nxt == path: return hops, path
        path, hops = nxt, hops + 1
    return hops, path

def exists(path):
    if path == "/": return (DIST / "index.html").exists()
    p = DIST / path.strip("/")
    return (p / "index.html").exists() or p.exists()

def main():
    rules = [(r["from"], r["to"]) for r in json.loads((ROOT / "data/redirects.json").read_text())["redirects"]]
    problems = []
    for frm, to in rules:
        hops, final = resolve(frm, rules)
        if hops != 1: problems.append(f"chain {frm} -> {final} in {hops} hops")
        if not exists(to): problems.append(f"target missing {frm} -> {to}")
    examined = 0
    for f in DIST.rglob("index.html"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"wp-json|/feed/|xmlrpc\.php|wp-content/uploads", text): problems.append(f"WP leftover in {f.relative_to(DIST)}")
        for a in BeautifulSoup(text, "lxml").find_all("a", href=True):
            href = a["href"].split("#")[0].split("?")[0]
            if not href.startswith("/") or href.startswith("//"): continue
            examined += 1
            if href.endswith((".xml", ".txt", ".pdf", ".jpg", ".png", ".webp")): continue
            if not exists(href) and match_rule(href, rules) is None: problems.append(f"dead link {href} in {f.relative_to(DIST)}")
    print(f"examined {len(rules)} redirects, {examined} internal links")
    for p in sorted(set(problems)): print("FAIL", p)
    sys.exit(1 if problems else 0)

if __name__ == "__main__": main()
```

- [ ] **Step 4: Run tests and gate**

```bash
python3 -m pytest tests/py/test_redirect_check.py -q && npm run check:redirects
```
Expected: `examined 20 redirects, N internal links` and no `FAIL` lines. Any `dead link` found in migrated bodies (for example `/blue/#contact-us` seen on the old homepage) is fixed **at the extractor** by adding a body-link rewrite map in `extract_wp.extract_body` (`/blue/` → `/buy-blue-staffy-puppies-uk/`), then re-run `npm run extract && npm run build`. Record each rewrite in the migration report.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "gate: redirect one-hop and internal link check

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 17: Gate — schema

**Files:**
- Create: `scripts/schema_check.py`, `tests/py/test_schema_check.py`

- [ ] **Step 1: Failing test**

```python
from schema_check import audit_html
GOOD = '<script type="application/ld+json">{"@type":"LocalBusiness","name":"x"}</script><script type="application/ld+json">{"@type":"Product","offers":{"@type":"Offer","availability":"https://schema.org/InStock"}}</script>'
def test_audit_ok():
    r = audit_html(GOOD, available_slugs={"roman"}, slug="available-puppies/roman")
    assert r["parsed"] == 2 and r["problems"] == []
def test_audit_flags_bad_json_phone_and_false_instock():
    bad = '<script type="application/ld+json">{oops}</script><script type="application/ld+json">{"@type":"LocalBusiness","telephone":"PHONE_PLACEHOLDER"}</script><script type="application/ld+json">{"@type":"Offer","availability":"https://schema.org/InStock"}</script>'
    r = audit_html(bad, available_slugs=set(), slug="x")
    assert any("parse" in p for p in r["problems"]) and any("telephone" in p for p in r["problems"]) and any("InStock" in p for p in r["problems"])
```

- [ ] **Step 2: Run** → `ModuleNotFoundError`.

- [ ] **Step 3: Write scripts/schema_check.py**

```python
#!/usr/bin/env python3
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

def _types(node, acc):
    if isinstance(node, dict):
        t = node.get("@type")
        if t: acc.append(t if isinstance(t, str) else "/".join(t))
        for v in node.values(): _types(v, acc)
    elif isinstance(node, list):
        for v in node: _types(v, acc)

def audit_html(text, available_slugs, slug):
    problems, parsed, alltypes = [], 0, []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
        try: data = json.loads(m.group(1))
        except json.JSONDecodeError as e: problems.append(f"parse error: {e}"); continue
        parsed += 1; _types(data, alltypes)
        raw = m.group(1)
        if '"telephone"' in raw and "PHONE_PLACEHOLDER" in raw: problems.append("telephone carries placeholder")
        if "InStock" in raw and not (slug.startswith("available-puppies/") and slug.split("/")[-1] in available_slugs):
            problems.append("InStock outside an available puppy page")
    dup = {t for t in alltypes if alltypes.count(t) > 1 and t in ("LocalBusiness", "WebSite", "BreadcrumbList", "Organization", "PetStore")}
    if dup: problems.append(f"duplicate top-level types (consolidate in project 4): {sorted(dup)}")
    return {"parsed": parsed, "problems": problems}

def main():
    avail = {p["slug"] for p in json.loads((ROOT / "data/puppies.json").read_text()) if p["status"] == "Available"}
    hard, advisory, examined = [], [], 0
    for f in sorted(DIST.rglob("index.html")):
        slug = f.parent.relative_to(DIST).as_posix(); examined += 1
        r = audit_html(f.read_text(encoding="utf-8", errors="ignore"), avail, slug)
        for p in r["problems"]: (advisory if p.startswith("duplicate") else hard).append(f"{slug or '/'}: {p}")
    print(f"examined {examined} pages; {len(hard)} blocking, {len(advisory)} advisory")
    for p in hard: print("FAIL", p)
    for p in advisory: print("ADVISORY", p)
    sys.exit(1 if hard else 0)

if __name__ == "__main__": main()
```

- [ ] **Step 4: Run tests and gate**

```bash
python3 -m pytest tests/py/test_schema_check.py -q && npm run check:schema | head -20
```
Expected: `examined 47 pages; 0 blocking, N advisory` (advisory duplicates are expected on migrated pages that carry old Rank Math graphs; they are reported, not fixed, in Foundation).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "gate: schema parse, placeholder telephone, false InStock, duplicate types (advisory)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 18: Gate — sitemaps

**Files:**
- Create: `scripts/sitemap_check.py`, `tests/py/test_sitemap_check.py`

- [ ] **Step 1: Failing test**

```python
from sitemap_check import audit
def test_audit(tmp_path):
    d = tmp_path; (d / "a").mkdir(); (d / "a/index.html").write_text("<html></html>"); (d / "index.html").write_text("<html></html>")
    (d / "b").mkdir(); (d / "b/index.html").write_text('<html><head><meta name="robots" content="noindex"></head></html>')
    (d / "page-sitemap.xml").write_text('<urlset><url><loc>https://x.test/</loc></url><url><loc>https://x.test/a/</loc></url><url><loc>https://x.test/b/</loc></url><url><loc>https://x.test/ghost/</loc></url></urlset>')
    (d / "post-sitemap.xml").write_text('<urlset><url><loc>https://x.test/a/</loc></url></urlset>')
    (d / "sitemap_index.xml").write_text('<sitemapindex><sitemap><loc>https://x.test/page-sitemap.xml</loc></sitemap><sitemap><loc>https://x.test/post-sitemap.xml</loc></sitemap></sitemapindex>')
    r = audit(d, "https://x.test")
    assert "/a/ in 2 shards" in r and "/b/ is noindex but listed" in r and "/ghost/ not built" in r
```

- [ ] **Step 2: Run** → `ModuleNotFoundError`.

- [ ] **Step 3: Write scripts/sitemap_check.py**

```python
#!/usr/bin/env python3
import os, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

def audit(dist, base):
    problems, seen = [], {}
    idx = (dist / "sitemap_index.xml").read_text()
    shards = [pathlib.Path(l).name for l in re.findall(r"<loc>(.*?)</loc>", idx)]
    for sh in shards:
        f = dist / sh
        if not f.exists(): problems.append(f"{sh} listed in index but missing"); continue
        for loc in re.findall(r"<loc>(.*?)</loc>", f.read_text()):
            path = loc.replace(base, "") or "/"
            seen.setdefault(path, []).append(sh)
            page = dist / path.strip("/") / "index.html" if path != "/" else dist / "index.html"
            if not page.exists(): problems.append(f"{path} not built")
            elif re.search(r'content="[^"]*noindex', page.read_text()): problems.append(f"{path} is noindex but listed")
    for path, shs in seen.items():
        if len(shs) > 1: problems.append(f"{path} in {len(shs)} shards")
    for f in dist.rglob("index.html"):
        rel = f.parent.relative_to(dist).as_posix(); path = "/" if rel == "." else f"/{rel}/"
        text = f.read_text()
        if path not in seen and not re.search(r'content="[^"]*noindex', text) and "thank-you" not in path: problems.append(f"{path} built but in no shard")
    return problems

if __name__ == "__main__":
    base = (os.environ.get("SITE_URL") or "https://SITE_URL_PLACEHOLDER").rstrip("/")
    probs = audit(DIST, base)
    print(f"examined {len(list(DIST.rglob('index.html')))} built pages")
    for p in probs: print("FAIL", p)
    sys.exit(1 if probs else 0)
```

- [ ] **Step 4: Run tests and gate**

```bash
python3 -m pytest tests/py/test_sitemap_check.py -q && npm run check:sitemaps
```
Expected: `examined 47 built pages` and no FAIL lines. (`404.html` is not an `index.html`, so it is not counted.)

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "gate: sitemap coverage (one shard each, no noindex, nothing unlisted)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 19: Port the CAG Playwright render harness

**Files:**
- Create: `tests/render/**` (copied from `/Users/apple/Downloads/CAG/tests/render/`), `tests/render/targets.json` (rewritten), `scripts/build_scorecard.mjs` (copied), `data/quality/` (created by the harness)

- [ ] **Step 1: Copy the harness**

```bash
cp -R /Users/apple/Downloads/CAG/tests/render tests/render
cp /Users/apple/Downloads/CAG/scripts/build_scorecard.mjs scripts/
mkdir -p data/quality
npx playwright install chromium
```

- [ ] **Step 2: Rewrite targets.json for BSUK page types**

```json
{
  "_comment": "Ported from CAG 2026-09-15. Same families, BSUK page types. IMG/LAYOUT/NAV blocking; SEM/SCHEMA/CSS/DUP/A11Y/FORM advisory until zero false reports across one full cluster (Foundation is a verbatim migration; the old markup is expected to fail many checks — that is the baseline for project 3/4, not a Foundation gate).",
  "families_by_page_type": {
    "home": ["IMG", "LAYOUT", "NAV", "SEM", "SCHEMA", "CSS", "DUP", "A11Y", "FORM"],
    "for-sale": ["IMG", "LAYOUT", "NAV", "SEM", "SCHEMA", "CSS", "DUP", "A11Y", "FORM"],
    "puppy": ["IMG", "LAYOUT", "NAV", "SEM", "SCHEMA", "CSS", "DUP", "A11Y", "FORM"],
    "interior": ["IMG", "LAYOUT", "NAV", "SEM", "SCHEMA", "CSS", "DUP", "A11Y", "FORM"],
    "location": ["IMG", "LAYOUT", "NAV", "SEM", "SCHEMA", "CSS", "DUP", "A11Y", "FORM"],
    "hub": ["IMG", "LAYOUT", "NAV", "SEM", "SCHEMA", "CSS", "DUP", "A11Y", "FORM"],
    "blog": ["IMG", "LAYOUT", "NAV", "SEM", "SCHEMA", "CSS", "DUP", "A11Y", "FORM"]
  },
  "pages": [
    { "slug": "index", "page_type": "home", "corpus": true },
    { "slug": "buy-blue-staffy-puppies-uk", "page_type": "for-sale", "corpus": true },
    { "slug": "blue-staffy-pup-sale-uk", "page_type": "for-sale", "corpus": false },
    { "slug": "buy-staffy-puppies-for-sale-uk", "page_type": "for-sale", "corpus": false },
    { "slug": "available-puppies/roman", "page_type": "puppy", "corpus": true },
    { "slug": "uk-blue-staffy-puppy-buying-guide", "page_type": "interior", "corpus": true },
    { "slug": "uk-staffordshire-bull-terrier-guide", "page_type": "interior", "corpus": false },
    { "slug": "blue-staffy-health-uk", "page_type": "interior", "corpus": false },
    { "slug": "blue-staffy-uk-breeders", "page_type": "interior", "corpus": false },
    { "slug": "uk-blue-staffy-breeders-contact", "page_type": "interior", "corpus": false },
    { "slug": "privacy-policy-uk", "page_type": "interior", "corpus": false },
    { "slug": "uk-locations", "page_type": "hub", "corpus": true },
    { "slug": "uk-locations/blue-staffy-puppies-birmingham", "page_type": "location", "corpus": true },
    { "slug": "uk-locations/blue-staffy-puppies-uk", "page_type": "location", "corpus": false },
    { "slug": "blue-staffy-blog-guides", "page_type": "blog", "corpus": true },
    { "slug": "blog", "page_type": "hub", "corpus": false }
  ]
}
```

- [ ] **Step 3: Fix CAG-specific paths in the copied lib**

Search and edit: `grep -rn "congoafricangreys\|cag-\|/emoji/\|site/content" tests/render/lib tests/render/checks | head`. Replace any hard-coded CAG asset path (e.g. the seam logo filename in `layout.ts`) with the BSUK equivalent or make the check skip when the selector is absent, keeping the `examined` count honest (an absent element is `examined: 0` for that check, never a PASS). Do not delete any check family.

- [ ] **Step 4: Run the meta gate, then pages**

```bash
npm run build && npm run test:render:meta 2>&1 | tail -15
npm run test:render:pages 2>&1 | tail -25
```
Expected for meta: all fixtures pass and the wiring guard reports every family in `families_by_page_type` registered and every registered family wired (symmetric difference empty). Expected for pages: the run completes for 16 pages × 3 viewports; blocking families IMG/LAYOUT/NAV may fail on migrated markup. For Foundation, record the failures in the gate report as the baseline; if a blocking failure is caused by the shell (header/footer/breadcrumb) rather than migrated content, fix the shell. Use `RENDER_OVERRIDE` only with a reason naming the migrated-content cause, and list every override in the report.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "test(render): port CAG Playwright harness, BSUK targets, meta gate wired

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 20: Close-out — run everything twice, reports, Artifact

**Files:**
- Create: `docs/reports/foundation-migration.md`, `docs/reports/foundation-gate-report.md`, `docs/artifacts/bsuk-foundation-gate-report.html`, `scripts/build_report_artifact.py`

- [ ] **Step 1: Full run, twice**

```bash
for i in 1 2; do echo "=== RUN $i ==="; npm run extract && npm run bake >/dev/null && npm run redirects && npm run llms && npm run build 2>&1 | tail -1 && npm run sitemaps && npm run check:all && npm run test:py; done 2>&1 | tee docs/reports/foundation-run.log | grep -E "RUN|examined|failing|FAIL|passed|error" 
```
Expected: both runs identical, `0 failing`, no `FAIL`, all pytest green. Then `npm run test:render:meta && npm run test:render:pages` twice; `node scripts/build_scorecard.mjs --run first` after each pages run.

- [ ] **Step 2: Lighthouse baseline (warm median of 3 per page type)**

```bash
npx astro preview --port 4321 & sleep 3
for p in "" buy-blue-staffy-puppies-uk available-puppies/roman uk-locations/blue-staffy-puppies-birmingham blue-staffy-blog-guides; do for i in 1 2 3; do npx lighthouse "http://localhost:4321/$p" --quiet --only-categories=performance,seo,accessibility --output=json --output-path="docs/reports/lh-${p//\//_}-$i.json" --chrome-flags="--headless"; done; done
kill %1
python3 - <<'EOF'
import json,glob,statistics,collections
by=collections.defaultdict(lambda:collections.defaultdict(list))
for f in glob.glob('docs/reports/lh-*.json'):
    d=json.load(open(f)); k=f.split('lh-')[1].rsplit('-',1)[0]
    for c in ('performance','seo','accessibility'): by[k][c].append(round(d['categories'][c]['score']*100))
for k,v in by.items(): print(k, {c:statistics.median(s) for c,s in v.items()})
EOF
```

- [ ] **Step 3: Write the migration report**

`docs/reports/foundation-migration.md` is assembled from `docs/reports/parity.md` plus, per page from `data/page-map.json`: phone occurrences replaced, refresh flags (count-in-title, old prices with values, old-pup-cards-removed), defects (empty-h1), and the body-link rewrites made in Task 16. Header: source commit of `~/bluestaffyuk-site` (`git -C /Users/apple/bluestaffyuk-site rev-parse --short HEAD`), date, page counts (11 rich, 28 locations, 1 post, 6 pups, 3 new index pages).

Generate it:
```python
# scripts/build_migration_report.py
import json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
pm = json.loads((ROOT/"data/page-map.json").read_text())["pages"]
src = subprocess.run(["git","-C","/Users/apple/bluestaffyuk-site","rev-parse","--short","HEAD"],capture_output=True,text=True).stdout.strip()
out = ["# Foundation migration report", "", f"Source: ~/bluestaffyuk-site @ {src}. Pages: {len(pm)} migrated ({sum(p['kind']=='rich' for p in pm)} rich, {sum(p['kind']=='location' for p in pm)} locations, {sum(p['kind']=='blog' for p in pm)} posts) + 6 puppy pages + /uk-locations/, /available-puppies/, /blog/.", "",
       f"Phone occurrences replaced with PHONE_PLACEHOLDER: {sum(p['phone_hits'] for p in pm)}", "", "## Parity", "", (ROOT/"docs/reports/parity.md").read_text(), "## Flags for project 4", "", "| URL | defects | refresh flags |", "|---|---|---|"]
out += [f"| {p['url']} | {', '.join(p['defects']) or '—'} | {', '.join(p['refresh_flags']) or '—'} |" for p in pm]
(ROOT/"docs/reports/foundation-migration.md").write_text("\n".join(out)+"\n"); print("ok")
```
Run: `python3 scripts/build_migration_report.py`.

- [ ] **Step 4: Write the gate report**

`docs/reports/foundation-gate-report.md` — by hand from the run outputs, with these sections and real numbers: Build (page count in dist), Parity (examined, failing), Redirects (rules, internal links examined, problems), Schema (examined, blocking, advisory list), Sitemaps (examined, shard counts), Pytest (count), Render meta (families registered vs wired), Render pages (pages × viewports, blocking failures by family with the migrated-content cause, overrides used), Lighthouse table (median of 3 per page type), Second-run confirmation (both runs identical: yes/no), Definition of done checklist from spec §5 ticked, Out of scope restated.

- [ ] **Step 5: Publish both reports as one Artifact**

Copy `scripts/build_spec_artifact.py`'s pattern (already in the repo's history; source at `/private/tmp/.../build_spec_artifact.py` or rewrite from `docs/artifacts/bsuk-foundation-spec.html`) into `scripts/build_report_artifact.py`, pointing at the two report files, title `BSUK Foundation Gate Report`, output `docs/artifacts/bsuk-foundation-gate-report.html`. Publish with the Artifact tool (favicon 🐾, description "Foundation close-out: migration parity, redirects, schema, sitemaps, render harness and Lighthouse baseline for the BlueStaffyUK rebuild.").

- [ ] **Step 6: Final commit**

```bash
git add -A && git commit -m "docs: Foundation migration and gate reports, artifact source

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git log --oneline | head -25
```

Confirm: no remote (`git remote -v` prints nothing), the old MCP untouched, the old clone untouched (`git -C /Users/apple/bluestaffyuk-site status --short | wc -l` unchanged from before).

---

## Self-review

**Spec coverage.** §1 repo layout → Tasks 1, 8–12. §2 verbatim migration, phone scrub, pup removal, puppies.json, settings → Tasks 2–7, 10. §3 redirects, hub, sitemaps, robots, llms → Tasks 9, 13, 14. §4 form, images, base layout, data-labels → Tasks 1 (CSS), 3 (data-labels), 7, 8, 12. §5 six checks, meta gate first, run twice, Lighthouse, reports + Artifact → Tasks 15–20. §6 flags → settings.json fields (breeder name, delivery, `guarantee_days: null` until confirmed), NOT FETCHED baselines in page-map.

**Gaps closed inline.** The blog index and puppies index needed sitemap routing (Task 14 `shard_for`). Old-homepage internal link `/blue/#contact-us` is dead; Task 16 routes it to an extractor rewrite map. The `prose-migrated` class is what parity scopes on (Task 8 and 15 agree).

**Type consistency.** `Page` dataclass fields used by writers: `url_path, kind, title, description, canonical, robots, og_type, h1, body_html, schema, word_count, images, embeds, headings, defects, phone_hits, refresh_flags` — matches Tasks 3, 4, 6. `bake_body_image(src, dst_dir, stem)` and `bake_puppy_card(src, dst_dir, slug)` signatures match their tests. `settings.json` keys used in components (`price_range`, `delivery_note`, `delivery_min_gbp`, `delivery_max_gbp`, `deposit_gbp`, `logo`, `socials`, `address`) all exist in Task 2.
