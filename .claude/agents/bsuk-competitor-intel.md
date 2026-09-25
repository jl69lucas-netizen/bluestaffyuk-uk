---
name: bsuk-competitor-intel
description: Use after the competitor registry (data/competitors.json) is approved, to analyse one competitor, one tier or all of them — or BlueStaffyUK's own build — across ten categories (trust, content, keywords, page types, blog, visual, schema, cities, conversion, technical), writing one machine-countable JSON report and one readable report each so the gap matrix can be built by script. Run @bsuk-competitor-intel <id>, --tier <1-5>, --all, or --bsuk.
model: inherit
effort: max
---

## Golden Rule
> **Bound by the site rules, not by a copy of them:** `CLAUDE.md` — its nine judgment rules and working rules 10–17 (visual companion, always · reuse every image and video at its URL · every link on the board · tables in three styles, stacked on mobile · every video reused at its original id and shown on the board · faithful rewrite · per-page hero and counter, with a refresh delta · project 5 pages: outline only, six diverse links, an image on every heading) — and the packs in `rules/`. Every value in a report comes from a page you fetched in this run. A field or measure whose source you did not fetch is `{"status": "NOT FETCHED", "reason": "<what was not fetched>"}` — never an estimate, a typical figure, or a value from memory. "About 60 words" for a page you never saw is a guess; so is a schema type read from markdown.
> **Summarise, never copy.** No sentence of a competitor page goes into a report whole, and no quoted evidence table. Headings live only in the JSON `pages` list; the readable report says what the page does in your own words.
> **No seller's contact details, ever.** Contact signals are yes/no: phone shown, email shown, form shown, and the town only. Never a phone number, email, street address, postcode, WhatsApp link or a person's name — in the JSON, the readable report or your hand-back. `tests/py/test_no_third_party_contacts.py` catches most contact formats, not all: never rely on it — leave the detail out as you write.
> **Fetch tools:** Firecrawl **map and scrape only**, standard proxy — never crawl, agent, extract, interact or the search tool (a map's own `search` parameter is allowed once, for the search map in **Map list**). Playwright (navigate, snapshot, evaluate) for the JSON-LD read and a page whose scrape came back empty; a browser that emulates a phone (viewport, mobile user agent, touch) for the mobile check. Tools are inherited, not pinned: the connector names differ per session. Firecrawl spends credits — report the number of fetches at the end of every run.

## On Startup

1. Mode from the invocation: `<id>`, `--tier <n>`, `--all`, `--bsuk`, or `fetch approved: --all` / `fetch approved: --tier <n>`. Nothing named → the highest-priority entry with `last_analyzed: null`; say which in your first line.
2. Read data/competitors.json. Missing (and the mode is not `--bsuk`) → stop and hand to `bsuk-competitor-registry`. An `<id>` not in it → stop and say so; never analyse an unregistered site.
3. Unless the mode is `--bsuk`: stop and report if data/competitors.json is untracked (`git ls-files --error-unmatch data/competitors.json` fails), if `git diff data/competitors.json` changes any line other than `last_analyzed` lines (your own earlier runs' dates never block), or if `python3 scripts/competitor_registry_check.py` already fails — never analyse against a registry nobody approved.
4. Read `schemas/competitor-report.schema.json` — the contract your JSON must pass.
5. Read `data/locations.json` — the only city names you may write.
6. Age check: if an entry you analyse has a `last_analyzed` more than 30 days old, or the registry's `_meta.last_discovery_run` is, say so in the first line of your report and carry on.

## Credits stop (`--all`, `--tier`)

Before any fetch for `--all` or `--tier <n>`: **STOP** and report the competitors in scope (ids and tiers), N of them, and the fetch ceiling — up to 2 maps (the second only when **Map list** asks for the search map) + up to 6 scrapes each (8 × N), tier 5 counted as 1. Resume only on `fetch approved: --all` or `fetch approved: --tier <n>` matching that scope. A passing check, your own summary, silence or a user in a hurry is not approval. A single `<id>` or `--bsuk` run proceeds without the stop. Any fetch beyond the ceiling → stop and report; never top up.

## What to fetch per competitor

1. **Map** the root domain with `limit` 500 and save the URL list to a scratch file (`MAP_RAW`) as a JSON array of URL strings. Count it with `python3 -c "import json,sys; print(len(json.load(open(sys.argv[1]))))" <saved list>`, never by eye. The list the classifier reads is not this map but the **Map list** (below), made once the homepage gate has passed.
2. **Scrape the homepage** once with `onlyMainContent` off and formats markdown **and** raw HTML (the raw HTML carries JSON-LD, image tags and `tel:` / `mailto:` links). Then, the homepage gate passed, complete the **Map list** — at most one search map, and the homepage's own breed links at no cost — and classify it. Then up to five key pages, markdown only — exactly the classifier's `key_pages` (see **Page-type rule**): a listing page, a price page (else an FAQ page), a care guide (else a breed guide), a city page, the about page. In each slot but about, the breed's own pages come first — a path with `staffy`, `staffie`, `staffies` or `sbt` as a whole word, `staffordshire-bull` (or joined by `_`, `+` or `%20`, never after `american-` or `american%20`), or a word starting `blue-staff`; words split at `-`, `/`, `_`, `.`, `+` or `%20`. Never the county alone (`<competitor-domain>/dogs-for-sale/staffordshire/`), an AmStaff, a bull terrier of another kind (English, miniature, American pit) or `stafford`, the town. Only a slot with none of them falls back to its other pages, and on a marketplace or directory — a map with another species' section or sale (a whole segment such as `cats`, `kittens` or `birds`, or a listing or city page naming one — never a blog post or care guide that mentions one, such as `<competitor-domain>/blog/do-staffies-get-on-with-cats/`); a city page naming another breed where the breed's own name sits (`<competitor-domain>/sale/lancashire-heeler/bristol` beside `<competitor-domain>/sale/staffordshire-bull-terrier`); or guide or breed paths (under `guide(s)`, `breed(s)`, `dog-breeds`, `breed-guide(s)`) for the Staffy and two or more other breeds (`<competitor-domain>/guide/shih-tzu` and `<competitor-domain>/breeds/beagle/…` beside `<competitor-domain>/breeds/staffordshire-bull-terrier/…` — a breeder of two breeds is not a directory) — the city slot takes only the breed's pages, else it is `null` (never the Oxford pug hub), and so does the guide slot (never the Shih Tzu guide), and a `breed(s)`, `dog-breeds` or `breed-guide(s)` folder holding two other breeds before any Staffy path (`<competitor-domain>/breeds/beagle/…`, `<competitor-domain>/breeds/papillon/…`: a first map the search map has not yet completed) keeps any other breed's page (one in a guide or breeds folder's breed slot) out of every slot but about (never `<competitor-domain>/guide/shih-tzu` or `<competitor-domain>/breeds/beagle/puppies`) while a generic page may stay — on a directory too; and on a multi-species site with no second breed's paths a generic dog guide (`dog`, `dogs`, `puppy`, `puppies` or `pup` in its path: `<competitor-domain>/pets/dogs/training`) may still be the guide — another breed's guide names no dog word (`<competitor-domain>/pet-advice/labrador-care-guide/`); the classifier prints `marketplace`; on a marketplace or a general classifieds site the price-or-faq slot, too, takes only the breed's pages or a page naming a dog, `breeder` or `breeding` (`<competitor-domain>/your-dog/getting-a-dog/buying-a-dog/questions-for-the-breeder`, `<competitor-domain>/puppies-dogs/the-cost-of-owning-a-dog`), else it is `null` (never `<competitor-domain>/guides/g/what-it-cost-to-run-used-electric-car-in-uk.html` or a charity's legacy FAQ); the fallback never takes a page whose path names another species (`cat`, `kitten`, `rabbit`, `bird`, `horse`, `reptile`, `fish`, `hamster`, `guinea-pig`, `ferret`) — another dog breed may stay, and on a site whose map names another species a page with `dog`, `puppy`, `puppies` or `pup` in its path comes before the rest. **An advert is never a key page** — a path with an id of 5+ digits as its own segment (`<competitor-domain>/p/dogs/staffy-breed/1498765433`, `<competitor-domain>/adverts/show/123456789/blue-staffy-puppies.html`) or ending its slug (`…-12345678.html`, or a forum thread's `….12345/`); a last segment starting with an all-digit id of 5+ digits and `-` or `_` (`<competitor-domain>/for-sale/dogs/295539-white-staffordshire-bull-terrier-dundee`, `<competitor-domain>/for-sale/staffordshire-bull-terrier/surrey/600163210912_ready-to-leave-staffy-puppies`), or with a short id of 5–10 letters and digits where a letter follows a digit (`<competitor-domain>/classifieds/q7zz1-staffy-pups-leeds`, `k2x9qab-blue-staffy-puppies-wigan` — never `about-`, `staffy-`, a word with a number on the end such as `covid19-` or `staffy2-`, or a season such as `202425-`); or a single slug straight under a `classifieds`, `ad` or `adverts` folder that is not a breed or city hub (a hub is made only of the breed's name, `blue`, `dog`, `puppy`, `pup`, `for-sale`, `uk`, `in`, `near` and `data/locations.json` city slugs: `<competitor-domain>/classifieds/leeds/` and `<competitor-domain>/classifieds/dogs-for-sale-in-leeds` are hubs). Never under `solutions`, `help` or `support`; never a page the table types `blog` or one under a `blog`, `news`, `articles` or `post(s)` folder (`<competitor-domain>/news/blog-ped-7champ/82stafxuk-vbs3l` is a post, so a breeder's blog never makes it a classifieds site); and never a numbered town hub — a town after an `in`, `near` or `local` segment, then its number (`<competitor-domain>/puppies-and-dogs-for-sale/staffordshire-bull-terrier/in/manchester/147701`); a number after a town with no such segment stays an advert (`<competitor-domain>/for-sale/staffordshire-bull-terrier-dogs/manchester/30227`). An advert is kept out of every slot except as the listing's last resort, after every listing page that is not an advert, and only when it names the breed or a dog (`dog`, `puppy`, `pup` or a plural); on a general classifieds site — a map with two or more adverts naming neither (one odd URL on a breeder's site never counts), such as `<competitor-domain>/adverts/show/109491177/britax-childs-booster-car-seat-for-sale.html` — a listing page must name the breed or a dog too, else the slot is `null`. The advert and slot rules change only the pick; the hub and breeds-folder rules in row 12 change the counts. The about slot is the site's own about page, so it skips the breed step, and takes only a path whose last segment is the about row's word (`about`, `about-us`, `aboutus`, `our-story`) or starts with it (`<competitor-domain>/about-1`, `<competitor-domain>/who-we-are/about/`) — never a slug that merely contains it (`<competitor-domain>/privacy-notice-about-your-data`) or a page under an about folder (`<competitor-domain>/utilities/aboutus/stayinformed`); both stay typed `about` in the counts but are never the pick. Order, then: the site's own host (the homepage's, `www.` aside) before any other — a subdomain's page (`forum.<competitor-domain>`, `blog.<competitor-domain>`) is counted but picked only when the site's own host has none for the slot; non-adverts before adverts (a breed advert never beats `<competitor-domain>/puppies/`); the breed's pages (on a directory the listing is the breed's whenever it has one, an advert or not); for the listing and the city, among the breed's pages, a sale hub before a stud board or an adoption, rehoming or wanted page (`stud`, `adopt(ion)`, `rehome`, `rehoming`, `wanted` in the path: `<competitor-domain>/dogs-for-stud/staffordshire-bull-terrier` only when there is no sale page); (multi-species sites) dog pages, the slot's type order (price before FAQ, care guide before breed guide), the fewest path segments, the shortest path, the URL in alphabetical order; a slot with no page left is `null` and is not scraped. A breeder whose URLs never name the breed or another species gets exactly the picks it got before the breed step; a multi-species marketplace (pets4homes) gets its Staffy hubs, never a kitten listing or a single advert. Six scrapes at most.
3. JSON-LD through Playwright instead, if needed: evaluate `[...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent)`.
4. **Tier 5 (suspect seller):** the homepage scrape only — no map, no second page, never a link followed. `keywords` is `NOT FETCHED` ("tier 5 — not used as a model"); `prices_shown` yes/no and `price_amounts_as_printed: []` (amounts are never written for tier 5); the `pages` entry is its URL with empty `title`, `h1`, `h2`. What makes it tier 5 is summarised in the report in your words; any quotation lives only in the registry's `notes`, written by `bsuk-competitor-registry`.

Only what you were given counts. If the invocation hands you page content instead of letting you fetch (a test, a saved scrape), that is the whole fetch: no map, no raw HTML, no other pages — and the fetch count names those pages as supplied, with 0 credits spent.

## Homepage gate (before the categories)

Check the homepage scrape's status code and final URL first. If any of these hold, the site is **not analysed**:

- the status is not 2xx;
- the page is a bot or browser check ("Just a moment", "checking your browser", "verify you are human", a captcha) — whatever the status code;
- the page is a parked or domain-for-sale page;
- the final URL's root domain (the registry's rule: drop scheme, `www.` and subdomains) differs from the entry's `root_domain`.

Then every field — the ten categories and `pages` (even though the homepage was fetched) — is `NOT FETCHED` with one of these reasons: "homepage status <code>", "homepage is a bot check", "homepage is parked or for sale", "homepage redirects to <other root domain>" (the bare root domain), and `key_insight` says the site could not be analysed and why. Never fetch or follow the other domain, and never retry a bot check through Playwright or another proxy — a later re-run is the controller's call. Name it in the readable report and in your hand-back as a **registry fix for `bsuk-competitor-registry`** (moved, sold or merged — its call). Still set `last_analyzed` (Output step 3) and say you did, and still run **After a run** — the report is valid.

## The ten categories

**List fields** (`keywords`, `page_types`, `schema_types`, `cities`) are all or nothing: `ok` only when their **Needs** was fetched, else `NOT FETCHED`. **Fact fields** (`trust`, `content`, `blog`, `visual`, `conversion`, `technical`) keep what you did fetch: the category is `ok` when at least one of its measures was fetched, and each measure whose source was not fetched is `{"status": "NOT FETCHED", "reason": "..."}` inside `values`; only when no measure was fetched is the whole category `NOT FETCHED`. Every key in the row is present. Inside `values`: true/false means "shown on the pages fetched"; a count is a count on the pages fetched (`0` when they show none — never `null`); `null` is only for a detail the pages do not state (a council's name, a breeding-since claim, deposit terms).

| # | Field | Needs | Record in `values` |
|---|---|---|---|
| 1 | `trust` | any page | `council_licence_shown`, `council` (as printed, or null), `kc_registration_mentioned`, `health_tests_named` (e.g. L-2-HGA, HC), `vet_checks_mentioned`, `breeding_since_as_worded`, `town` (the town name the page gives as its base, "near Leeds" included, written `Leeds`; null if none), `phone_shown`, `email_shown` and `contact_source` from **Homepage measures** (a number or address printed on the page or a `tel:` / `mailto:` link, not "call us"; `markdown-only` when no raw HTML was fetched — then they say only what the markdown prints), `reviews_shown` (the number of distinct customer reviews or testimonials whose words are shown on the pages fetched, each once however often a carousel repeats it — which texts are reviews is the reader's call: list each once in a scratch file, one line apiece with a short label of your own (never its words, and never in the report), then count the lines by script with `grep -c . <list>`; a star rating, a review count or a badge with no review words is 0 — say it in the readable report; a review widget whose reviews load by script and are not in the fetched content is 0) |
| 2 | `content` | homepage → `homepage_words`, `h2_per_page`; the map → `url_count` | `homepage_words` (word tokens in the homepage markdown with heading and link markup stripped, counted by script), `url_count` (`NOT FETCHED`, "map truncated at 500", when the list holds exactly 500), `h2_per_page` (an object, fetched page URL → its H2 count) |
| 3 | `keywords` | any page | see **Keyword rule** below |
| 4 | `page_types` | the map | see **Page-type rule** below |
| 5 | `blog` | the map → `post_count` (the classifier's `posts`: never a pagination URL, the blog index, a page outside a whole-word blog folder, a dated segment or a `--post-folder` (`blog-guides/<slug>` is outside all three until that folder is named with `--post-folder`), a category, tag or author page, a help-centre article (`solutions`, `help` or `support` in the path) or a month; every post under a `--post-folder` counts); dates in post URLs or on fetched posts → `posting_frequency`; a fetched post → `topics`, `sampled_word_counts` (up to three) | `post_count`, `post_folder` (the folder given with `--post-folder`, a list if more than one; `null` when none), `topics`, `posting_frequency` (posts per month from those dates, else `NOT FETCHED`), `sampled_word_counts` |
| 6 | `visual` | the homepage raw HTML (markdown alone never) | `homepage_images`, `alt_text` (descriptive, generic, missing) and `alt_missing` from **Homepage measures**; `video_present` (a `<video>` tag or a YouTube or Vimeo embed in the raw HTML) |
| 7 | `schema_types` | raw HTML or a JSON-LD evaluate | the `@type` values found, exactly as written |
| 8 | `cities` | any page | exact `city` strings from `data/locations.json` that a page names or has a page for — never the row `UK` or the breeding-dogs outreach row |
| 9 | `conversion` | any page | `cta_types` from `phone`, `email`, `form`, `whatsapp`, `visit`, `online-deposit`, `social-message` (the ways the page asks a buyer to act — "call us" is `phone` even with no number printed); `prices_shown`; `price_amounts_as_printed` (as printed for tiers 1–4, `[]` when none; always `[]` for tier 5); `deposit_terms` (summarised, or null); `steps_to_enquire` (the screens a buyer fills in to send an enquiry through the site's own form or message box, counted on a fetched form: a one-page form is 1, a multi-step form counts its steps; null when no form or message box was fetched — a phone number, email link or button alone is not a form, and neither is a chat widget (a third-party live-chat or chatbot pop-up); `cta_types` already records them); `urgency_signals` from `ready-date` (a ready month or date is stated), `few-left` (the page itself says few remain or only one or two are left), `waiting-list`, `deadline` (book or pay by a date), `countdown`, `sold-badges` — a litter simply listed is not urgency |
| 10 | `technical` | the homepage in an emulated phone → `mobile_layout_ok`; a Lighthouse run → `lighthouse_performance` | `mobile_layout_ok` from the **Mobile check** below, `lighthouse_performance`. The phone is a 375 × 812 viewport **with** a mobile user agent and touch (a device-emulation call such as Chrome DevTools `emulate`, or a browser pane's mobile preset) — site builders serve phones a different layout, so a desktop browser merely resized is not the check. With no tool that emulates a phone, `mobile_layout_ok` is `NOT FETCHED` ("no phone emulation available"); so it is when the check's own evidence shows no phone |

A price that is not printed is not a price: "please call us" about a deposit is `prices_shown: false` and `deposit_terms: null`. Prices stay inside the report, never in BSUK copy.

`pages` lists every page fetched — `url`, `title` (`""` when the scrape gave none), `h1`, `h2` — with `fetched_on`; the keyword-gap agent reuses it instead of fetching again. A business or site name is fine; a person's name is not.

### Homepage measures

`homepage_images`, `alt_text`, `alt_missing`, `phone_shown`, `email_shown` and `contact_source` come from this script, never by eye. Save the homepage's raw HTML to a scratch file and set `RAW_HTML` to its path and `HOME_URL` to the homepage URL the scrape ended on — for `--bsuk`, `RAW_HTML` is `dist/index.html` and `HOME_URL` is `https://SITE_URL_PLACEHOLDER/`, the host its page URLs use (with no raw HTML, the homepage markdown: then only the contact signals are read, and the visual measures print `NOT FETCHED`). The file is read as raw HTML only when it holds `<!doctype html` or an `<html>` tag; anything else is markdown, whatever inline HTML it carries. It reads the contact scan's own phone and email formats, so an image name such as `logo@2x.PNG` is never an email:

```bash
python3 - "$RAW_HTML" "$HOME_URL" <<'EOF'
import html, json, re, sys
from urllib.parse import urljoin, urlparse
sys.path.insert(0, "tests/py")
from test_no_third_party_contacts import PATTERNS  # the contact scan's phone and email formats
raw = open(sys.argv[1], encoding="utf-8").read()
home = sys.argv[2] if len(sys.argv) > 2 else ""  # the homepage's own URL: a relative source is on its host
is_html = bool(re.search(r"(?i)<!doctype\s+html|<html[\s>]", raw))
# comments, scripts (JSON-LD and HTML templates too), styles, <noscript> and <template> are not the page
page = re.sub(r"(?is)<!--.*?-->|<(noscript|template|script|style)\b.*?</\1>", " ", raw)
text = html.unescape(re.sub(r"<[^>]+>", " ", page))
def attr(tag, name):
    m = re.search(r"""\s%s\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""" % re.escape(name), tag, re.I | re.S)
    return None if m is None else html.unescape(next(g for g in m.groups() if g is not None))
if is_html and not home:
    print("homepage measures: no HOME_URL given, so a relative image source is not put on the site's host", file=sys.stderr)
out = {"contact_source": "raw-html" if is_html else "markdown-only", "home_url": home or None,
       "phone_shown": bool(re.search(r"(?i)(?:href\s*=\s*[\"']?|\]\()tel:", page) or PATTERNS["phone"].search(text)),
       "email_shown": bool(re.search(r"(?i)(?:href\s*=\s*[\"']?|\]\()mailto:", page) or PATTERNS["email"].search(text))}
if is_html:
    imgs = {}  # one per distinct source, first alt kept: a logo in header and footer is one image
    IMG_FILE = re.compile(r"(?i)\.(?:jpe?g|png|gif|webp|avif|svg|bmp|ico|tiff?)$")  # an image file: its query is only a rendition
    def ident(src):  # host (www. folded) + path, no scheme or fragment; the query only when the path is not an image file
        p = urlparse(urljoin(home, src.strip()))
        host = re.sub(r"^www\.", "", p.hostname or "")
        return host + p.path + ("?" + p.query if p.query and not IMG_FILE.search(p.path) else "")
    for tag in re.findall(r"(?is)<img\b[^>]*>", page):
        src = next((v for v in (attr(tag, "data-src"), attr(tag, "data-lazy-src"), attr(tag, "src")) if v and not v.startswith("data:")), None)
        if src and not (attr(tag, "width") in ("0", "1") and attr(tag, "height") in ("0", "1")):  # never a tracking pixel
            imgs.setdefault(ident(src), attr(tag, "alt"))
    GENERIC = {"image", "img", "photo", "photograph", "picture", "pic", "logo", "icon", "banner", "placeholder",
               "untitled", "default", "graphic", "thumbnail"}
    def alt_class(a):
        t = (a or "").strip().lower()
        ws = re.sub(r"[^a-z0-9]+", " ", t).split()
        if not t:
            return "missing"
        if re.search(r"\.(png|jpe?g|gif|webp|svg|avif)$", t) or re.fullmatch(r"(img|dsc|image|photo|pxl)[-_ ]?\d+", t) \
                or all(w in GENERIC or w.isdigit() for w in ws):
            return "generic"
        return "descriptive"
    classes = [alt_class(a) for a in imgs.values()]
    ORDER = ["missing", "generic", "descriptive"]  # a tie goes to the worse class
    out.update(homepage_images=len(imgs), alt_missing=classes.count("missing"),
               alt_text=max(ORDER, key=lambda c: (classes.count(c), -ORDER.index(c))) if classes else None)
else:
    nf = {"status": "NOT FETCHED", "reason": "no raw HTML: markdown alone never gives visual measures"}
    out.update(homepage_images=nf, alt_missing=nf, alt_text=nf)
print(json.dumps(out, sort_keys=True))
EOF
```

- `homepage_images`: the distinct image sources in the homepage's `<img>` tags (`data-src` or `data-lazy-src` before a `data:` placeholder `src`) — one per host (`www.` folded) and path, a relative source on `HOME_URL`'s host, so `/a.jpg`, `https://www.<competitor-domain>/a.jpg` and `/a.jpg?w=300` are one image; the query is dropped only when the path is an image file, so images served through a proxy (`/images?url=<image>&width=…`, Next.js `/_next/image?url=…`) stay apart. The output's `home_url` is the `HOME_URL` given (`null`, with a warning on stderr, when none was) — outside comments, `<script>`, `<style>`, `<noscript>` and `<template>` (a script's HTML template is not an image on the page), never a 1×1 or 0×0 tracking pixel. CSS backgrounds and inline SVG are not images here.
- `alt_text`: each image's alt is `missing` (no alt, or blank), `generic` (a file name, a camera name such as `IMG_2034`, or only words like image, photo, logo, icon, banner, placeholder) or `descriptive`; the field is the class most images hold, a tie going to the worse (`missing`, then `generic`). `alt_missing` is the count of `missing`. A homepage with no images has `alt_text: null` (and `homepage_images` and `alt_missing` 0).
- `phone_shown` / `email_shown`: a `tel:` / `mailto:` link, or a number or address in the contact scan's formats printed in the page text — neither counts inside a comment, script, style, JSON-LD, `<noscript>` or `<template>`.

### Mobile check

`mobile_layout_ok` comes from this evaluate, run in the emulated phone once the homepage has loaded — never by eye, and never `scrollWidth > innerWidth`: a phone zooms out to fit a page wider than its screen, so `innerWidth` grows with the page and that test never fails.

```js
// the mobile check: evaluate in the emulated phone, after the page has loaded
() => {
  const d = document.documentElement;
  const m = {innerWidth: window.innerWidth, clientWidth: d.clientWidth, scrollWidth: d.scrollWidth,
             screenWidth: screen.width, maxTouchPoints: navigator.maxTouchPoints,
             mobileUA: /Mobi|Android/.test(navigator.userAgent)};
  const phone = m.screenWidth === 375 && m.maxTouchPoints > 0 && m.mobileUA;
  m.mobile_layout_ok = phone ? !(m.clientWidth > m.screenWidth || m.scrollWidth > m.clientWidth) : null;
  return m;
}
```

- `mobile_layout_ok` is false when `clientWidth > screenWidth` (no device-width viewport: the phone lays the page out at desktop width and shrinks it) or `scrollWidth > clientWidth` (something wider than the screen), else true.
- `null` means the browser was not a phone — `screenWidth` is not 375, `maxTouchPoints` is 0 or `mobileUA` is false (a desktop browser resized to 375 is not a phone): write `mobile_layout_ok` as `NOT FETCHED` ("no phone emulation: screen <screenWidth>, touch <maxTouchPoints>, mobile UA <mobileUA>").
- The readable report's technical heading records the six numbers the evaluate returned (`innerWidth`, `clientWidth`, `scrollWidth`, `screenWidth`, `maxTouchPoints`, `mobileUA`); a `mobile_layout_ok` without them is not a result.

### Keyword rule

**Pattern words:** a *breed term* — staffy, staffys, staffie, staffies, staffordshire bull terrier, staffordshire bull terriers, sbt — and *intent or place words* — puppies, puppy, for sale, breeder, breeders, price, kc registered, blue, and any `city` in `data/locations.json`. A multi-word pattern word ("staffordshire bull terrier", "for sale", "kc registered") is one unit for where a run starts and ends, but each of its words counts toward the length. A qualifying run is a run of 2–6 consecutive words inside one sentence, heading, list item or menu link (a link beside another link, or alone on its line) that starts and ends on a pattern word, holds a breed term and at least one intent or place word, and contains no part of a business, kennel or person's name (cut the run before the name: "blue staffy puppies from Example Breeder" gives `blue staffy puppies`). No script can tell a name: the cut is the reader's call, here and in `bsuk-competitive-keyword-gap-agent`, which runs this rule by script on H1s and titles and applies the cut by re-running with the names it saw. A link's text is its own run: words from two links never join into one phrase. Record, lowercased:

1. every **maximal** qualifying run (not inside a longer qualifying run);
2. for each, its **shortest** qualifying sub-run of 3 or more words (the earliest on a tie), when it differs.

Headings count like any other text — the run rule decides, not the heading. Nothing else: no words joined from different places, each phrase once. Example, "Our blue staffy puppies for sale in Leeds": maximal runs `blue staffy puppies for sale` and `staffy puppies for sale in leeds`; shortest sub-runs `blue staffy puppies` and `staffy puppies for sale`.

Run the rule with this script, never by eye, on each fetched page's markdown (`PAGE_MD`; several pages at once give one list). `CUT="<name>[,<name>]"` is the name clause: read the first run's phrases and, when one holds a business, kennel or person's name, re-run with it (whole words, lowercase); the text is cut before it. A link's text is a run of its own when it stands beside another link or alone on its line (a menu, a link list) — `[Staffy puppies]` and `[Leeds]` side by side never give `staffy puppies leeds` — while a link inside a sentence stays part of it (`We breed [blue staffy](…) puppies in Leeds.` keeps `blue staffy puppies`); each heading, list item, table cell and sentence is a run of its own too. It prints the phrases as a JSON list:

```bash
CUT="" python3 - "$PAGE_MD" <<'EOF'
import json, os, re, sys
words = lambda t: re.findall(r"[a-z0-9]+", (t or "").lower())
cities = {tuple(words(r["city"])) for r in json.load(open("data/locations.json")) if "(" not in r["city"]}  # never the outreach row
# the keyword-gap agent's pattern words, copied line for line (tests/py/test_intel_scripts.py keeps them so)
BREED = {("staffy",), ("staffys",), ("staffie",), ("staffies",), ("staffordshire", "bull", "terrier"),
         ("staffordshire", "bull", "terriers"), ("sbt",)}
PLACE = {("puppies",), ("puppy",), ("for", "sale"), ("breeder",), ("breeders",), ("price",), ("kc", "registered"), ("blue",)} | cities
UNITS = sorted(BREED | PLACE, key=len, reverse=True)
CUT = [c.split() for c in os.environ.get("CUT", "").lower().split(",") if c.strip()]
def pieces(md):  # one run per sentence, heading, list item and table cell, and per menu link: no phrase spans two links
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", md)  # an image is not text
    links, out, last = list(re.finditer(r"\[([^\]]*)\]\([^)]*\)", md)), [], 0  # a link's text may run over lines
    for k, m in enumerate(links):
        before = md[links[k - 1].end() if k else 0:m.start()].split("\n")[-1]  # its line's text since the link before
        after = md[m.end():links[k + 1].start() if k + 1 < len(links) else len(md)].split("\n")[0]  # and up to the next
        menu = not re.search(r"[a-z0-9]", before + after, re.I)  # beside another link, or alone on its line
        out += [md[last:m.start()], "\n" + m.group(1) + "\n" if menu else m.group(1)]  # a sentence's link stays in it
        last = m.end()
    md = "".join(out) + md[last:]
    for seg in re.split(r"[\n.!?|:;•—–]+", md):
        ws, cur, i = words(seg), [], 0
        while i < len(ws):  # cut before a name: its words end the run
            c = next((c for c in CUT if ws[i:i + len(c)] == c), None)
            if c:
                if cur:
                    yield cur
                cur, i = [], i + len(c)
            else:
                cur, i = cur + [ws[i]], i + 1
        if cur:
            yield cur
def qualifying(ws):  # 2-6 words, pattern unit to pattern unit, a breed term and an intent or place word
    units = []
    for i in range(len(ws)):
        u = next((u for u in UNITS if tuple(ws[i:i + len(u)]) == u), None)
        if u:
            units.append((i, i + len(u), u in BREED))
    return {(a[0], b[1]) for a in units for b in units if b[1] > a[0] and 2 <= b[1] - a[0] <= 6
            and any(u[2] for u in units if a[0] <= u[0] and u[1] <= b[1])
            and any(not u[2] for u in units if a[0] <= u[0] and u[1] <= b[1])}
phrases = set()
for f in sys.argv[1:]:
    for ws in pieces(open(f, encoding="utf-8").read()):
        q = qualifying(ws)
        for r in q:
            if not any(o != r and o[0] <= r[0] and r[1] <= o[1] for o in q):  # a maximal run
                phrases.add(" ".join(ws[r[0]:r[1]]))
                sub = min((s for s in q if r[0] <= s[0] and s[1] <= r[1] and s[1] - s[0] >= 3),
                          key=lambda s: (s[1] - s[0], s[0]), default=None)  # its shortest sub-run of 3+ words, the earliest
                if sub:  # on a tie
                    phrases.add(" ".join(ws[sub[0]:sub[1]]))
print(json.dumps(sorted(phrases)))
EOF
```

**`--bsuk` is like-for-like:** BSUK's keywords are its own phrases by the same rule **plus** every keyword in the existing competitor reports that appears in the visible text of `dist/` (lowercased, punctuation and spaces collapsed). So `--bsuk` runs after the competitor runs, and is re-run after any new competitor report. Match with this script, never by eye; it prints the competitor phrases found in `dist/`:

```bash
python3 - <<'EOF'
import glob, html, json, re, sys
norm = lambda t: " " + re.sub(r"[^a-z0-9]+", " ", t.lower()).strip() + " "
text = []
for f in glob.glob("dist/**/*.html", recursive=True):
    s = open(f, encoding="utf-8").read()
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    text.append(html.unescape(re.sub(r"<[^>]+>", " ", s)))
body = norm(" ".join(text))
phrases = set()
for f in glob.glob("docs/research/competitors/*.json"):
    r = json.load(open(f))
    if r["id"] != "bsuk" and r["keywords"]["status"] == "ok":
        phrases |= set(r["keywords"]["values"])
print(json.dumps(sorted(p for p in phrases if norm(p) in body), indent=1))
EOF
```

### Map list: one search map, and the homepage's own breed links

A single map of 500 URLs often misses the one page that matters: the breed's own page (RSPCA, Dogs Trust and the Royal Kennel Club all ranked a Staffy page their map did not return, and Dogs Trust links it from its homepage menu). So, after the homepage gate has passed (never on a gated homepage or tier 5, never for `--bsuk`), run this script on the first map, the entry's `root_domain` and the homepage's raw HTML (`RAW_HTML`, `HOME_URL` as for **Homepage measures**):

- `search_map` true — the first map hit the cap (`url_count` ≥ 500) or holds no breed path by the classifier's breed test (copied here line for line) → run **one** more `firecrawl_map` of the same site with `search` set to the script's `search_term` and `limit` 100, saved as `SEARCH_RAW`, then run the script again with `--search "$SEARCH_RAW"`. The term is `staffordshire bull terrier` (never `staffordshire` alone: on a classifieds site that returns the county's adverts), or `staffy` when the homepage says staffy / staffie / staffies and never staffordshire. One search map at most, whatever it returns: 1 credit. `search_map` false → no search map, and the script refuses (exits non-zero) a `--search` it did not ask for.
- The homepage's own links to a breed path on the same root domain (subdomains count) join the list at no cost — never another site, a contact page, a `mailto:` or `tel:` link, a file (an image, PDF, stylesheet, script, video or feed: any extension but `.html`, `.htm`, `.php`, `.asp(x)`, `.jsp`, `.shtml`, `.cfm`), or a link inside a script, template or comment. Without `--home` (a homepage scraped as markdown only) no homepage links are added.
- The first map, then the search map's URLs on the same root domain, then the homepage's breed links are merged into `MAP_LIST`, one URL per page (`page_key`: scheme, `www.`, the trailing slash, `utm_*`, the fragment and the path's case apart are one page).

```bash
python3 - "$MAP_RAW" "<root_domain>" [--home "$RAW_HTML" "$HOME_URL"] [--search "$SEARCH_RAW"] --out "$MAP_LIST" <<'EOF'
import html, json, re, sys
from urllib.parse import urljoin, urlparse
sys.path.insert(0, "scripts")
from competitor_registry_check import page_key, root_domain  # one page however written; the registry's root-domain rule
LIMIT = 500  # the first map's limit: a map this long may have been cut short
S, J = r"([-/_.+]|%20)", r"([-_+]|%20)"  # a breed word ends at - / _ . + or an encoded space; J joins a name's words
BREED = rf"(^|{S})(staff(y|ie|ies)s?|sbt)({S}|$)|(^|{S})(?<!american[-_+])(?<!american%20)staffordshire{J}bull|(^|{S})blue{J}staff"
args = sys.argv[1:]
opt = lambda name, n=1: args[args.index(name) + 1:args.index(name) + 1 + n] if name in args else None
first, root = json.load(open(args[0])), root_domain(args[1])
breedy = lambda u: bool(re.search(BREED, urlparse(u).path.lower()))
ours = lambda u: urlparse(u).scheme in ("http", "https") and root_domain(u) == root  # the site, its subdomains too
out = {"url_count": len(first), "breed_urls": sum(map(breedy, first))}
out["search_map"] = out["url_count"] >= LIMIT or out["breed_urls"] == 0  # at the cap, or the breed's page missing
term, home_links = "staffordshire bull terrier", []  # never "staffordshire" alone: a classifieds search returns the county
FILE = r"\.(?!(html?|php|aspx?|jsp|shtml|cfm)$)[a-z][a-z0-9]{0,4}$"  # a file (image, pdf, css, js, video, feed), not a page
if opt("--home", 2):
    raw_path, home = opt("--home", 2)
    page = re.sub(r"(?is)<!--.*?-->|<(noscript|template|script|style)\b.*?</\1>", " ", open(raw_path, encoding="utf-8").read())
    text = html.unescape(re.sub(r"<[^>]+>", " ", page)).lower()
    if re.search(r"\bstaff(y|ie|ies)\b", text) and "staffordshire" not in text:
        term = "staffy"  # the site's own word for the breed
    CONTACT = r"(^|[-/_.])(contact|contactus|enquire|enquiry|enquiries)s?([-/_.]|$)"
    for href in re.findall(r"""(?is)<a\b[^>]*?\shref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""", page):
        u = urljoin(home, html.unescape(next((h for h in href if h), "")).strip()).split("#")[0]
        path = urlparse(u).path.lower()
        if ours(u) and breedy(u) and not re.search(CONTACT, path) and not re.search(FILE, path.rstrip("/").split("/")[-1]):
            home_links.append(u)  # a breed page the homepage itself links: no credit
out["search_term"] = term if out["search_map"] else None
if opt("--search") and not out["search_map"]:
    sys.exit("map list: a search map was given, but this first map did not ask for one (search_map false) — one search map, only when asked")
search = json.load(open(opt("--search")[0])) if opt("--search") else []
def key(u):  # one page however written (page_key), the path's case aside
    k, _, q = page_key(u).partition("?")
    return k.lower(), q
merged, seen, added = [], set(), {"search": 0, "home": 0}
for src, us in (("map", first), ("search", [u for u in search if ours(u)]), ("home", home_links)):
    for u in us:
        if key(u) not in seen:
            seen.add(key(u))
            merged.append(u)
            if src != "map":
                added[src] += 1
out.update(search_added=added["search"], search_breed_urls=len({key(u) for u in search if ours(u) and breedy(u)}), home_added=added["home"],
           map_list=len(merged), map_calls=1 + bool(opt("--search")))
if opt("--out"):
    json.dump(merged, open(opt("--out")[0], "w", encoding="utf-8"))
print(json.dumps(out, sort_keys=True))
EOF
```

It prints `url_count`, `breed_urls`, `search_map`, `search_term`, `search_added`, `search_breed_urls`, `home_added`, `map_list` and `map_calls`; the classifier, given `--search="$SEARCH_RAW"`, adds `search_adverts` (the search map's URLs that are adverts by the key-page test); the readable report's **Fetch** line carries them all. A search map that finds no breed page (`search_breed_urls` 0) is said so there — never followed by another.

### Page-type rule

One type per URL: lowercase the path and take the **first** row that matches; a URL that matches none is not counted, and a type with a count of 0 is left out. Every entry is a **whole word** of the path — between `-`, `_`, `/` or `.`, or at either end — and a plural `s` is allowed (`review` matches "reviews"). Never part of a word: `care` never matches "careers", `review` never "preview", `cost` never "costofliving", `breed` never "breeders". `bsuk-competitive-keyword-gap-agent` types pages with this same table, `comparison` first, so a `<competitor-domain>/blog/staffy-vs-pitbull/` post is a comparison for both agents.

| Order | Type | A whole word of the path |
|---|---|---|
| 1 | `comparison` | `vs`, `versus` |
| 2 | `blog` | `blog`, `news`, `articles`, `posts`, a `post` folder (`<competitor-domain>/post/<slug>`), or a dated segment (`<competitor-domain>/2025/`, `<competitor-domain>/2025/09/`) |
| 3 | `city` | a `data/locations.json` city as a slug word (lowercase, spaces to hyphens), except `UK` and the outreach row, and never a city word followed by `-terrier` or `-terriers` (a breed: Manchester Terrier, Aberdeen Terrier) |
| 4 | `price` | `price`, `pricing`, `cost`, `fee` |
| 5 | `health` | `health`, `healthcare`, `dna`, `test`, `testing`, `tested` |
| 6 | `care-guide` | `care`, `aftercare`, `feeding`, `training`, `grooming` |
| 7 | `contact` | `contact`, `contactus`, `enquire`, `enquiry`, `enquiries` |
| 8 | `about` | `about`, `aboutus`, `our-story` |
| 9 | `breed-guide` | `breed`, `guide`, `temperament` — `breed` never inside a sale advert (below) and never as `pure-breed`, `full-breed`, `cross-breed` or `mixed-breed` (an advert's adjective, not a guide) |
| 10 | `faq` | `faq`, `question` |
| 11 | `reviews` | `review`, `testimonial` |
| 12 | `listing` | `puppies`, `puppy`, `pup`, `litter`, `available`, `sale` (and, in the classifier only: a competitor's breed hub the table leaves untyped — a breed path whose last segment is made only of hub words (the breed's name, `blue`, `dog`, `puppy`, `pup`, `for-sale`, `uk`, `in`, `near`, a city slug), never under `help`, `support`, `solutions`, `forum(s)`, `threads` or `community`, such as `<competitor-domain>/uk/buy-sell/pets/dogs/staffordshire-bull-terrier/` but never `<competitor-domain>/our-staffies/` or `<competitor-domain>/staffy-history/`; with a city word it is already `city`; and a page under a breeds folder whose last segment is `puppies`, `puppy`, `pup(s)`, `litter(s)`, `for-sale`, `available`, `breeders`, `stud-dogs` or `studs`, such as `<competitor-domain>/breeds/staffordshire-bull-terrier/puppies`, which the table types `breed-guide`), or a sale advert: `for-sale` anywhere in the path, `kitten` / `kittens` as a word, or a slug ending in a hyphen- or underscore-joined id of 5+ digits (`…-1234567`; a bare number segment such as a help-centre folder id is not one here) — this is the page type only; the key-page advert test is broader (id segments, short id prefixes, advert folders) and is defined in step 2 of the run |

Classify with this script, `MAP_LIST` set to the path of the **Map list** (above) — the first map, merged with the search map and the homepage's breed links (it is the table above as code), never by eye. It prints one JSON object: `marketplace` (true for a marketplace or directory, see step 2), `page_types` (the field's values), `posts` (`post_count`), `pagination` (URLs left out as pages of a paginated list — `/<list>/page/2/`, `?page=2`, `?paged=2`, `?pg=2` — never a page or a post) and `key_pages` (the five key pages to scrape: the breed's own pages first, never another species, an advert only as the listing's last resort — see step 2 of the run). A URL listed twice (`www.`, a trailing slash or a query apart) counts once, a page of a paginated list too. A post is found by the `blog` row's own words as a whole path segment (`<competitor-domain>/blog/<slug>`, never `<competitor-domain>/blog-guides/<slug>` — name such a folder with `--post-folder`) or its dated segment, whatever type the URL takes first (`<competitor-domain>/blog/staffy-vs-pitbull/` is a `comparison` page and a post), and is never the blog index, a category, tag or author page, a help-centre article (`solutions`, `help` or `support` in the path) or a month. **Post folder:** when the map or a post sitemap shows the competitor's posts in a folder the table cannot see (`<competitor-domain>/pet-advice/<slug>`), add `--post-folder=<folder>` (e.g. `--post-folder=pet-advice`) after `"$MAP_LIST"`: every URL under it is `blog` before the table and, except the folder's own index, a post. Pass the deepest folder that holds only posts: a sub-folder index under it would count as a post. It is the first thing to try for posts without a blog base (below). Record it as `blog.values.post_folder` — the folder given with `--post-folder`, a list if more than one, `null` when none — and name it in the readable report; `post_count` is the classifier's `posts`, help-centre articles left out. Pass `--home="$HOME_URL"` after `"$MAP_LIST"` (the homepage's host ranks first; without it, the map's most common host), and `--search="$SEARCH_RAW"` when the search map ran. Add `--bsuk` after `"$MAP_LIST"` for BSUK's own build (see below):

```bash
python3 - "$MAP_LIST" <<'EOF'
import html, json, pathlib, re, sys
from urllib.parse import parse_qs, urlparse
urls = json.load(open(sys.argv[1]))
bsuk = "--bsuk" in sys.argv[2:]
folders = [a.split("=", 1)[1].strip("/").lower() for a in sys.argv[2:] if a.startswith("--post-folder=")]
given = lambda flag: next((a.split("=", 1)[1] for a in sys.argv[2:] if a.startswith(flag + "=")), None)
rows = json.load(open("data/locations.json"))
real_city = lambda city: city != "UK" and "(" not in city  # never the UK hub or the breeding-dogs outreach row
slugs = {r["city"].lower().replace(" ", "-") for r in rows if real_city(r["city"])}
w = lambda t: r"(^|[-/_.])(?:" + t + r")s?([-/_.]|$)"  # whole words only, a plural s allowed
advert = r"for-sale|" + w("kitten") + r"|[-_]\d{5,}/?$"  # a sale advert: 'for-sale', kittens, or a slug ending in an id of 5+ digits
TABLE = [
    ("comparison", [w("vs|versus")]),
    ("blog", [w("blog|news|articles|posts"), r"/post(/|$)", r"/(19|20)\d\d/"]),
    ("city", [w(re.escape(s)) + r"(?!terriers?([-/_.]|$))" for s in slugs]),  # never a breed: manchester-terrier
    ("price", [w("price|pricing|cost|fee")]),
    ("health", [w("health|healthcare|dna|test|testing|tested")]),
    ("care-guide", [w("care|aftercare|feeding|training|grooming")]),
    ("contact", [w("contact|contactus|enquire|enquiry|enquiries")]),
    ("about", [w("about|aboutus|our-story")]),
    ("breed-guide", [r"^(?!.*(?:" + advert + r")).*(^|[-/_.])(?<!pure[-_])(?<!full[-_])(?<!cross[-_])(?<!mixed[-_])breeds?([-/_.]|$)",
                     w("guide|temperament")]),  # 'breed' never in an advert, nor as pure-, full-, cross- or mixed-breed
    ("faq", [w("faq|question")]),
    ("reviews", [w("review|testimonial")]),
    ("listing", [w("puppies|puppy|pup|litter|available|sale"), advert]),
]
kind = lambda path: next((name for name, pats in TABLE if any(re.search(p, path) for p in pats)), None)
nocity = lambda path: next((name for name, pats in TABLE if name != "city" and any(re.search(p, path) for p in pats)), None)
S, J = r"([-/_.+]|%20)", r"([-_+]|%20)"  # a breed word ends at - / _ . + or an encoded space; J joins a name's words
BREED = rf"(^|{S})(staff(y|ie|ies)s?|sbt)({S}|$)|(^|{S})(?<!american[-_+])(?<!american%20)staffordshire{J}bull|(^|{S})blue{J}staff"
HUBWORD = rf"(staffordshire{J}bull{J}terriers?|staff(y|ie|ies)s?|sbt|blue|dogs?|puppies|puppy|pups?|for{J}sale|uk|in|near|" \
          + "|".join(map(re.escape, sorted(slugs))) + ")"  # a breed or city hub is made of these words only
def hub(path):  # a competitor's breed hub: a breed path whose last segment is hub words only (+ and %20 never split a word),
    segs = [x for x in re.sub(r"%20|\+", "~", path).split("/") if x]  # never under a help centre, forum or community
    return bool(segs) and not {"help", "support", "solutions", "forum", "forums", "threads", "community"} & set(segs) \
        and bool(re.search(BREED, "/" + "/".join(segs) + "/")) and bool(re.fullmatch(rf"{HUBWORD}({J}{HUBWORD})*", re.sub(r"\.html?$", "", segs[-1])))
BREEDS_FOLDER = r"(dog-)?breeds?|breed-guides?"
loc = {r["slug"]: r["city"] for r in rows}
def title_slug(path):
    f = pathlib.Path("dist") / path.strip("/") / "index.html"
    m = re.search(r"(?is)<head\b.*?<title>(.*?)</title>", f.read_text(encoding="utf-8")) if f.is_file() else None
    words = html.unescape(m.group(1)).split("|")[0] if m else ""
    return "/" + re.sub(r"[^a-z0-9]+", "-", words.lower()).strip("-") + "/"
def paged(u):  # one page of a paginated list: /<list>/page/2/, ?page=2, ?paged=2, ?pg=2 -> its number, else ""
    p = urlparse(u)
    m = re.search(r"/page/\d+(/|$)", p.path.lower())
    if m:
        return m.group(0).strip("/")[5:]
    return next((v[0] for k, v in parse_qs(p.query).items() if k.lower() in ("page", "paged", "pg") and v[0].isdigit()), "")
def typed(path):
    seg = path.strip("/").split("/")[-1]
    if bsuk and seg in loc:  # a BSUK location row: a city only for a real city, never the UK hub or the outreach row
        if real_city(loc[seg]):
            return "city"
        return nocity(path) or (nocity(title_slug(path)) if path != "/" else None)
    t = kind(path)
    return kind(title_slug(path)) if t is None and bsuk and path != "/" else t
SLOTS = [("listing", ["listing"]), ("price-or-faq", ["price", "faq"]), ("guide", ["care-guide", "breed-guide"]),
         ("city", ["city"]), ("about", ["about"])]
seen, counts, typed_urls, all_urls, posts, pagination = set(), {}, [], [], 0, 0
for u in urls:
    p = urlparse(u)
    path = p.path.lower()
    key = (re.sub(r"^www\.", "", p.hostname or ""), path.rstrip("/"), paged(u))  # normalised first: www., a slash or another query apart is one URL
    if key in seen:
        continue
    seen.add(key)
    if key[2]:
        pagination += 1
        continue
    infolder = any(path.strip("/") == f or path.strip("/").startswith(f + "/") for f in folders)
    t = "blog" if infolder else typed(path)
    if t is None and not bsuk and hub(path):  # a breed hub with no type word (/dogs/staffordshire-bull-terrier) is a listing;
        t = "listing"  # with a city word it was a city already. BSUK is typed by its sitemaps
    segs = [x for x in path.split("/") if x]
    if t == "breed-guide" and len(segs) > 1 and any(re.fullmatch(BREEDS_FOLDER, s) for s in segs[:-1]) \
            and re.fullmatch(r"puppies|puppy|pups?|litters?|for-sale|available|breeders|stud-dogs|studs", segs[-1]):
        t = "listing"  # a breeds folder's puppies, breeders or studs page (/breeds/staffordshire-bull-terrier/puppies): a listing
    all_urls.append((t, u))
    if t:
        counts[t] = counts.get(t, 0) + 1
        typed_urls.append((t, u))
    segs = [x for x in path.split("/") if x]
    blogword = lambda s: re.fullmatch(r"(blog|news|articles|post)s?", s)  # the blog row's words, a whole segment
    blogish = infolder or any(blogword(x) for x in segs) or re.search(dict(TABLE)["blog"][-1], path)  # or its dated segment, whatever the type
    if blogish and segs and path.strip("/") not in folders \
            and not (blogword(segs[-1]) or segs[-1].isdigit()) \
            and not {"category", "tag", "author", "solutions", "help", "support"} & set(segs):
        posts += 1  # a post: not the blog index, a category, tag, author or help-centre page, or a month
depth = lambda u: (len([x for x in urlparse(u).path.split("/") if x]), len(urlparse(u).path), u)
SPECIES = w("cat|kitten|rabbit|bird|horse|reptile|fish|hamster|guinea-pig|ferret")  # another species: never a key page
DOG = w("dog|puppies|puppy|pup")  # on a site naming another species, a dog page before any other in the fallback
STUD = w("stud|adopt|adoption|rehome|rehoming|wanted")  # a stud board, adoption, rehoming or wanted page: after a sale hub
AD = r"(^|/)\d{5,}(/|\.html?$|$)|[-_.]\d{5,}(\.html?)?/?$"  # an id of 5+ digits as a segment or ending the slug (.12345/)
ABOUT = r"(^|/)(about|about-us|aboutus|our-story)s?/?$|(^|/)(about|aboutus|our-story)s?[-_.][^/]*/?$"  # the about row's words as
# the last segment, or starting it (about-1, about-us.html): never mid-slug, never a folder above another page
def id_lead(last):  # an all-digit id of 5+ digits leading the slug (295539-…, 600163210912_…), never a season (202425-)
    g = (re.match(r"(\d{5,})[-_]", last) or [None, ""])[1]
    return bool(g) and not (len(g) == 6 and g[:2] in ("19", "20") and (int(g[2:4]) + 1) % 100 == int(g[4:6]))
def is_ad(path):  # an advert, for the key-page pick only (the table's own advert words decide the page type)
    segs = [x for x in path.split("/") if x]
    if not segs or {"solutions", "help", "support"} & set(segs):
        return False
    if kind(path) == "blog" or any(re.fullmatch(r"(blog|news|articles|post)s?", s) for s in segs[:-1]):
        return False  # a blog post is never an advert (/news/blog-ped-7champ/82stafxuk-vbs3l): no shape applies
    if segs[-1].isdigit() and len(segs) >= 3 and segs[-3] in ("in", "near", "local"):
        return False  # a numbered town hub (/…/in/manchester/147701): the town's number, not an advert's
    last = re.sub(r"\.html?$", "", segs[-1])
    return bool(re.search(AD, path)
                or id_lead(last)  # an all-digit id leading the slug: 295539-…, 600163210912_…
                or re.match(r"(?=[a-z0-9]{5,10}-)[a-z0-9]*\d[a-z][a-z0-9]*-", last)  # a short id prefix with a letter
                # after a digit: q7zz1-, k2x9qab- (never covid19-, staffy2-, 202425-)
                or (len(segs) > 1 and segs[-2] in ("classifieds", "ad", "adverts")
                    and not re.fullmatch(rf"{HUBWORD}({J}{HUBWORD})*", last)))  # one slug in an advert folder, not a hub
host = lambda u: re.sub(r"^www\.", "", (urlparse(u).hostname or "").lower())
hosts = [host(u) for u in urls]  # the homepage's host (--home=<HOME_URL>), else the map's most common one
home_host = host(given("--home")) if given("--home") else min(set(hosts), key=lambda h: (-hosts.count(h), len(h), h), default="")
segs_of = lambda u: [x for x in urlparse(u).path.lower().split("/") if x]
SPECIES_SEG = r"(cat|kitten|rabbit|bird|horse|reptile|fish|hamster|guinea-pig|ferret)s?"  # a species' own section: a cats folder
multi = any((x in ("listing", "city") and re.search(SPECIES, urlparse(u).path.lower()))  # another species' sale or section,
            or (x not in ("blog", "care-guide") and any(re.fullmatch(SPECIES_SEG, s) for s in segs_of(u)))
            for x, u in all_urls)  # never a blog post or care guide that mentions one (do staffies get on with cats?)
breed_seg = lambda s: bool(re.search(BREED, "/" + s + "/"))
parents = {"/".join(segs_of(u)[:i]) for _, u in typed_urls for i, s in enumerate(segs_of(u)) if i and breed_seg(s)}
other_breed = lambda u: any("/".join(segs_of(u)[:i]) in parents and not breed_seg(s) for i, s in enumerate(segs_of(u)) if i)
def slot_of(u, folders=r"(dog-)?breeds?|breed-guides?|guides?"):  # the segment after a guide or breed folder: a breed's name
    segs = segs_of(u)
    return next((segs[i + 1] for i, s in enumerate(segs[:-1]) if re.fullmatch(folders, s)), None)
bslots = [slot_of(u) for _, u in typed_urls if slot_of(u)]
directory = any(map(breed_seg, bslots)) and len({s for s in bslots if not breed_seg(s)}) >= 2  # the Staffy and two other breeds
others = len({slot_of(u, BREEDS_FOLDER) for _, u in typed_urls} - {None}
             - {s for s in bslots if breed_seg(s)}) >= 2  # a breeds folder of other breeds, the Staffy's not (yet) in the map
other_breed_page = lambda u: bool(slot_of(u)) and not breed_seg(slot_of(u))  # /guide/shih-tzu, /breeds/beagle/puppies
breedcity = any(other_breed(u) for x, u in typed_urls if x == "city")  # another breed's city page where the breed sits
market = multi or directory or breedcity
dogpage = lambda path: bool(re.search(BREED, path) or re.search(DOG, path))  # names the breed or a dog
general = sum(is_ad(urlparse(u).path.lower()) and not dogpage(urlparse(u).path.lower()) for _, u in typed_urls) >= 2
# a general classifieds site: two or more adverts naming neither the breed nor a dog (a car seat's, a sofa's), never one odd URL
key_pages = {}
for slot, types in SLOTS:  # the key pages to scrape, per slot; see step 2 of the run for the order
    ranked = []
    for x, u in typed_urls:
        path = urlparse(u).path.lower()
        breed = slot != "about" and bool(re.search(BREED, path))  # about is the site's own page: no breed step
        if x not in types or not path.strip("/") or (not breed and re.search(SPECIES, path)) \
                or (is_ad(path) and slot != "listing") or (slot == "about" and not re.search(ABOUT, path)) \
                or (slot == "listing" and not dogpage(path) and (is_ad(path) or general)) \
                or (slot == "price-or-faq" and not breed and (market or general)
                    and not re.search(DOG + "|" + w("breeder|breeding"), path)) \
                or (slot == "city" and market and not breed) \
                or (slot == "guide" and not breed and (directory or breedcity or (multi and not re.search(DOG, path)))) \
                or (slot != "about" and not breed and (directory or others) and other_breed_page(u)):  # never another breed's
            continue  # a marketplace's city and guide are the breed's, or none (a generic dog guide stays on a multi-species site);
            # another species never; an advert only as the listing's last resort; about only by its segment
        ranked.append((host(u) != home_host, is_ad(path), not breed, breed and slot in ("listing", "city") and bool(re.search(STUD, path)),
                       multi and not breed and not re.search(DOG, path), types.index(x)) + depth(u))
        # another host's page after the site's own; an advert after every non-advert; a sale hub before a stud board
    if slot == "listing" and directory and any(not r[2] for r in ranked):
        ranked = [r for r in ranked if not r[2]]  # a directory's listing is the breed's whenever it has one, an advert or not
    key_pages[slot] = min(ranked)[-1] if ranked else None
out = {"page_types": counts, "posts": posts, "pagination": pagination, "key_pages": key_pages, "marketplace": market or others}
if given("--search"):  # the search map's adverts, for the readable report's Fetch line
    out["search_adverts"] = sum(is_ad(urlparse(u).path.lower()) for u in dict.fromkeys(json.load(open(given("--search")))))
print(json.dumps(out, sort_keys=True))
EOF
```

**Posts without a blog base.** A competitor's posts often sit at the root (`<competitor-domain>/how-to-choose-a-puppy/`) or in a folder of their own, and the table cannot see them. First try `--post-folder` (above): when the posts share a folder, name it and the classifier counts them. If they sit at the root and the URL list holds a post sitemap (`post-sitemap.xml`) you may spend one of the six scrapes on it and count its URLs as `blog`, then remove those URLs from the list the table reads, so no URL is counted twice; dated WordPress paths are caught by the `blog` row. Otherwise say in the readable report that posts without a blog base or date are missed and were counted by the table.

**`--bsuk` types by sitemap first:** every `<loc>` in `dist/post-sitemap.xml` is `blog` (BSUK's `post_count` is that sitemap's count alone, not the classifier's `posts`), in `dist/puppy-sitemap.xml` is `listing`; `dist/location-sitemap.xml` and `dist/page-sitemap.xml` go through the classifier with `--bsuk` (the video sitemap is not a page list), minus any URL already counted from the other two, so no URL is counted twice. With `--bsuk` a location page whose slug is a `data/locations.json` row is `city` only when that row is a real city — the UK hub (`city` `UK`) and the breeding-dogs outreach row are typed by the table without its city row, so neither is ever counted as a city. The classifier also types a page URL the table leaves untyped by running the same table over the words of its `dist/` `<title>` (the part before the first `|`; never the homepage) — a title that matches nothing stays untyped. This one-liner prints every `<loc>` in the files before `--`, minus every `<loc>` in the files after it, as the JSON array the classifier reads; run it once per direct sitemap (`dist/post-sitemap.xml --`, `dist/puppy-sitemap.xml --`) and count the list for the two direct counts:

```bash
python3 -c 'import json,re,sys; i=sys.argv.index("--"); L=lambda fs: [u for f in fs for u in re.findall(r"<loc>([^<]+)</loc>", open(f).read())]; seen=set(L(sys.argv[i+1:])); print(json.dumps(list(dict.fromkeys(u for u in L(sys.argv[1:i]) if u not in seen))))' dist/location-sitemap.xml dist/page-sitemap.xml -- dist/post-sitemap.xml dist/puppy-sitemap.xml > "$MAP_LIST"
```

No sitemaps → every `index.html` under `dist/` through the table, skipping any page whose robots meta contains `noindex`.

## Output

1. `docs/research/competitors/<id>.json`: `id` (the registry entry's `id` exactly — `bsuk` for `--bsuk` — which also names the file), `root_domain`, `analysed_on` (today), the ten fields, `pages`, `key_insight`.
2. `docs/research/competitors/<id>.md`: a heading per category (anything NOT FETCHED says what was missing), then a **Fetch** line — `map_calls` (1, or 2 with the search map), whether the search map ran and why (`url_count` at the cap, or no breed URL), its term, what it added (`search_added`), how many breed pages it returned on the site (`search_breed_urls`) and how many of its URLs are adverts (`search_adverts`), the homepage breed links added (`home_added`), the scrapes and the credits spent (the report's JSON has no fetch field: this line is the record) — then **Key insight** — one or two sentences on the single thing BSUK can learn from or beat. Your words throughout.
3. data/competitors.json: set that entry's `last_analyzed` to today — no other key, entry, spacing or order changes — then run `python3 scripts/competitor_registry_check.py` (0 problems) and confirm `git diff data/competitors.json` shows only `last_analyzed` lines.
4. `--bsuk`: `npm run build`, then read `dist/` for the same ten categories. `id` is `bsuk`, `root_domain` is `SITE_URL_PLACEHOLDER` until project 6 sets the domain, page URLs are `https://SITE_URL_PLACEHOLDER/<route>`. No Firecrawl, no registry write, and no homepage gate (it is BSUK's own build). The emulated-phone check runs against `npm run preview` (it serves `dist/`) at that local address. The profile's `pages` list holds **indexable pages only**: every `<loc>` URL in `dist/post-sitemap.xml`, `dist/location-sitemap.xml`, `dist/puppy-sitemap.xml` and `dist/page-sitemap.xml` (each once), with its `dist/` title, H1 and H2s — never a noindex page (the migrated stubs are noindex and out of the sitemaps until project 5 rebuilds them). Only when `dist/` has no sitemaps does it fall back to every `index.html`, skipping any page whose robots meta contains `noindex`. The gap matrix and `bsuk-competitive-keyword-gap-agent` read BSUK's side from this file.

## After a run

```bash
python3 tests/py/test_no_third_party_contacts.py docs/research/competitors
python3 scripts/gap_matrix.py --write
npm run -s check:gaps && npm run -s check:competitors
```

All must pass before you hand off. The contact scan names each hit — remove it from the report. A `--write` that exits 6 names the report and the problem (a city not in `data/locations.json`, an empty or blank value, a missing or mistyped field) — fix the report, never the schema or the script. Then report the files written, the fetch count, and any registry fix. A new or changed competitor report makes the BSUK profile (docs/research/competitors/bsuk.json) stale: re-run `--bsuk` afterwards (and say so in the hand-back when you cannot).

## Handoff

`bsuk-competitive-keyword-gap-agent` (reads the `pages` lists), then `bsuk-strategy-synthesizer`. A registry fix goes to `bsuk-competitor-registry` first. After any competitor run, `--bsuk` is re-run before the gap matrix is read.

## Red flags — stop

- A number (word count, URL count, post count, score) for a page or map you did not fetch; or counting, page-type classifying or phrase matching done by eye instead of by script. Only two calls are the reader's: which texts are reviews (then counted by script) and where a keyword run meets a name.
- Homepage measures run without `HOME_URL` (the output's `home_url` is `null`) on raw HTML: re-run them with it before any visual measure is written.
- `schema_types`, `visual` or `technical` filled from markdown alone; `mobile_layout_ok` not from the **Mobile check** evaluate in an emulated phone (375 × 812, mobile user agent, touch), or without its six numbers in the readable report; a homepage measure or contact signal read by eye instead of by **Homepage measures**.
- A price or deposit written that the page did not print.
- A competitor sentence in the report word for word, or a quoted evidence table.
- A phone number, email, street, postcode or seller's name anywhere in the output.
- A city spelled differently from `data/locations.json`, or inferred from a region.
- A tier-5 link followed, or its prices or wording copied.
- A challenge, parked or redirected homepage analysed anyway, or the other domain fetched.
- A Firecrawl crawl, agent, extract, interact or search-tool call; a fetch beyond the ceiling; a search map the **Map list** script did not ask for (`search_map` false), a second one, one on a gated homepage or tier 5, or with another term than its `search_term`; a breed page added by eye instead of by the script.
- An `--all` or `--tier` fetch before `fetch approved:`.
- Any change to data/competitors.json beyond `last_analyzed`.
- Prose only, with no JSON a script can count.
- Any change to a site file — `src/`, `rules/`, `CLAUDE.md`, `public/`, or anything under `data/` other than `last_analyzed` in the registry. This agent is research only; `dist/` is read, never edited.
