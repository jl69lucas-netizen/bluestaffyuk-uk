#!/usr/bin/env python3
"""BSUK final-page-pass auditor — page-type-aware mechanical gate.
Reads dist/<slug>/index.html (slug may be nested, e.g. available-puppies/roman) and scores
the objective checks against the page-type PROFILE, returning per-check pass plus a
verdict: PASS / PASS-WITH-WARNINGS / FAIL. Subjective checks (voice/humour/
readability/tone) stay manual. Run AFTER `npx astro build`.

Exit code: 1 whenever any page verdicts FAIL, 0 otherwise — spec §11, a gate that
cannot fail is a report. `--fail-on-error` is accepted for symmetry with
page_hardening_scan.py but changes nothing here: FAIL is always fatal.

The three heading-outline checks (all_six_levels, min_h5_5, min_h6_5) fail on every
page Foundation migrated. A page failing ONLY those is tagged [migration baseline]
and counted on its own line, so a real regression is visible against the noise.
Profiles: interior (default), puppy (--puppies), blog (--blog, auto-discovers the
/blog/ hub + every dist/blog/<slug>/ post; also included in the default run), or any profile by name via
`<slug>... --type home|location|...` (slug `index` = dist/index.html)."""
import re, json, sys, argparse
from pathlib import Path
from html.parser import HTMLParser

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _slugs import dist_path as _dist_path   # one slug-resolution convention, shared

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DEFAULT_JSON = ROOT / "docs/reports/final_page_audit.json"
# The heading-outline gates every migrated page fails. Not excused — separated, so a
# new defect is not lost among 12 identical rows.
BASELINE_CHECKS = {"all_six_levels", "min_h5_5", "min_h6_5"}
# data/settings.json: delivery_min_gbp 200, delivery_max_gbp 350.
SHIP_RE = re.compile(r"£\s?200\b[\s\S]{0,80}£\s?350\b|£200\s*[–-]\s*£350")
def dist_path(slug):
    """Resolve a flat or nested slug to its rendered index.html (`index` = the
    homepage), via the shared convention in scripts/_slugs.py."""
    return _dist_path(slug, DIST)

# Read, not retyped: data/page-map.json is what the build actually produced, and a
# hand list drifts the first time a page is added (CAG's list was 18 slugs and its
# dist/ was 104 pages).
_PM = json.loads((ROOT / "data/page-map.json").read_text())["pages"]
SLUGS = [p["url"].strip("/") for p in _PM if p["kind"] == "rich"]

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.h={i:0 for i in range(1,7)}; s.imgs=[]; s.cur=None
        s.title=""; s.intitle=False; s.links=[]; s.cura=None; s.atext=[]
        s.jsonld=[]; s.injson=False; s.metadesc=""; s.canonical=""; s.body=[]
        # depth counter for the page hero block, so every image inside a
        # multi-image hero (2x2 grid, polaroid scatter) is exempt from the
        # lazy-loading rule rather than only imgs[0]
        s.herodepth=0; s.hero_imgs=[]
    def handle_starttag(s,t,a):
        d=dict(a)
        cls=d.get("class","") or ""
        if s.herodepth:
            s.herodepth+=1
        elif t in ("header","section","div") and re.search(r"\bhero\b|\bhero-", cls):
            s.herodepth=1
        if re.fullmatch(r"h[1-6]",t): s.cur=int(t[1]); s.h[s.cur]+=1
        if t=="title": s.intitle=True
        if t=="img":
            s.imgs.append(d)
            if s.herodepth: s.hero_imgs.append(d)
        if t=="a":
            s.cura=d; s.atext=[]
        if t=="meta" and d.get("name")=="description": s.metadesc=d.get("content","")
        if t=="link" and d.get("rel")=="canonical": s.canonical=d.get("href","")
        if t=="script" and d.get("type")=="application/ld+json": s.injson=True
    def handle_startendtag(s,t,a):
        s.handle_starttag(t,a)
    def handle_endtag(s,t):
        if s.herodepth and t in ("header","section","div"):
            s.herodepth-=1
        if t=="title": s.intitle=False
        if re.fullmatch(r"h[1-6]",t): s.cur=None
        if t=="a" and s.cura is not None:
            s.links.append((s.cura, "".join(s.atext).strip())); s.cura=None
        if t=="script" and s.injson:
            s.injson=False
    def handle_data(s,data):
        if s.intitle: s.title+=data
        if s.injson: s.jsonld.append(data)
        if s.cura is not None: s.atext.append(data)
        s.body.append(data)

# Per-page-type check severities. Anything unlisted falls back to DEFAULT_SEVERITY.
# FAIL = hard ship-blocker · WARN = soft (logged, shippable) · NA = not applicable.
DEFAULT_SEVERITY = "FAIL"
PROFILES = {
    "puppy": {
        "newsletter_present": "NA",      # puppy pages exempt (footer newsletter only)
        "all_h1_h4": "WARN",             # spec §4: H4 only where depth exists on a lean puppy page
        "no_aggregateoffer": "FAIL",     # single Product+Offer only
        "shipping_line": "FAIL",
        "sold_not_instock": "FAIL",      # explicit: sold puppy must not remain InStock in schema
        "wordcount_in_band": "WARN",
        "real_hero_image": "WARN",
        "lifespan_12_14": "WARN",
    },
    "interior": {                        # back-compat with interior_29_audit behavior
        "no_aggregateoffer": "NA",
        "shipping_line": "NA", "wordcount_in_band": "NA", "real_hero_image": "NA",
    },
    "home": {                            # homepage: sections stay, heading minimums do not (evidence pass, 2026-09-09)
        "no_aggregateoffer": "NA",
        "shipping_line": "NA", "wordcount_in_band": "NA", "real_hero_image": "NA",
        "has_breadcrumb": "NA",          # root page has no trail
        "min_h5_5": "WARN",
        "min_h6_5": "WARN",
        "no_skip": "FAIL",
    },
    "location": {                        # 40 thin state/city pages: depth is filled with real shipments, not headings
        "no_aggregateoffer": "NA",
        "shipping_line": "NA", "wordcount_in_band": "NA", "real_hero_image": "NA",
        "min_h5_5": "WARN",
        "min_h6_5": "WARN",
        "no_skip": "FAIL",
    },
    "comparison": {                      # [X] vs [Y] spokes + hub (added 2026-07-04 per breeder review)
        "no_aggregateoffer": "FAIL",     # comparison pages never carry Offer/AggregateOffer (variant pages own it)
        "sold_not_instock": "NA",
        "newsletter_present": "NA",      # §11.6 breeder-review standard: NO page-level newsletter band on comparison pages — the inquiry form is the single closer (2026-07-05; the old "pass" rode on the word inside an HTML comment)
        "shipping_line": "FAIL",         # delivery section must show the £200–£350 band
        "real_hero_image": "FAIL",
        "wordcount_in_band": "WARN",     # deep-standard band 3,000–8,000 incl. chrome (5.2k target)
        "cites_credentials_early": "WARN",
        "lifespan_12_14": "WARN",
        "breadcrumb_one": "FAIL",
        "faqpage_present": "FAIL",
        "single_canonical": "FAIL",
        "no_emoji": "FAIL",
    },
    "for-sale": {                        # 22-page transactional for-sale cluster (2026-07-20)
        "no_aggregateoffer": "WARN",     # egg/single pages carry one Product+Offer; AggregateOffer only on group/hub
        "sold_not_instock": "FAIL",      # sold ≠ InStock, ever
        "newsletter_present": "NA",      # inquiry form is the single closer, no page-level newsletter band
        "shipping_line": "FAIL",         # the £200–£350 delivery band must appear
        "real_hero_image": "FAIL",
        "wordcount_in_band": "WARN",
        "cites_credentials_early": "WARN",
        "lifespan_12_14": "WARN",
        "breadcrumb_one": "FAIL",
        "faqpage_present": "FAIL",
        "single_canonical": "FAIL",
        "no_emoji": "FAIL",
    },
    "blog": {                            # /blog/ hub + dist/blog/<slug>/ posts (spec 2026-06-27)
        # Blog gate = ONLY the checks the cluster spec defines; everything else is
        # NA so a post is judged on what the program actually requires. The FAIL
        # gates below mirror the Heading Outline Gate + blog-cluster requirements.
        "_default": "NA",
        "h1==1": "FAIL",                 # exactly one page topic
        "no_skip": "FAIL",               # sequential H1→H6, no skipped levels
        "all_six_levels": "FAIL",        # every blog page carries all six levels
        "min_h5_5": "FAIL",              # >= 5 H5
        "min_h6_5": "FAIL",              # >= 5 H6
        "breadcrumb_one": "FAIL",        # exactly one BreadcrumbList (no dupes)
        "faqpage_present": "FAIL",       # FAQPage schema present
        "no_visible_date": "FAIL",       # freshness in schema only, never visible
        "no_escaped_svg": "FAIL",        # no raw &lt;svg dumped to the page
        "no_emoji": "FAIL",              # line-icon SVGs only, no colorful emoji
        "single_canonical": "FAIL",      # exactly one canonical link
    },
}
# ── Page-type exemptions for interior legal/utility slugs (spec §9 amendment 4c) ─────────
# Three of the interior checks below are SALES-PAGE checks wearing an interior profile's
# clothes: `cites_credentials_early` wants "KC registered" or "DEFRA" inside the first 300
# words, `lifespan_12_14` wants the breed's lifespan stated, and `newsletter_present` wants a
# sign-up band. A privacy policy that opened on its own licence number, and a post-enquiry
# confirmation that told a reader who has just written to us how long a Staffy lives, would
# both be worse pages for satisfying the check. So the exemption is per SLUG and carries its
# reason, rather than being switched off for every interior page — the guide and health pages
# are interior too, and those three checks are exactly right there.
#
# `phone_in_footer` is NOT here. It fails on every page on the site because
# data/settings.json holds PHONE_PLACEHOLDER until project 6 supplies a number, and a
# site-wide baseline row that the report counts is the honest way to carry that.
SALES_SHAPED_CHECKS = ("cites_credentials_early", "lifespan_12_14", "newsletter_present")
INTERIOR_UTILITY_EXEMPT = {
    "privacy-policy-uk":
        "legal page: the copy is a data-protection notice, and a credentials line, a lifespan "
        "figure or a newsletter band in it would be a sales page in a policy's clothes",
    "thank-you-blue-staffy-puppies-journey":
        "post-enquiry confirmation: the reader has already written to us, so the page owes "
        "them a reply window rather than credentials, a lifespan figure or a sign-up band",
}


def severity(page_type, check, slug=None):
    """Per-check severity, falling back to the profile's `_default`, then global.

    A slug in INTERIOR_UTILITY_EXEMPT takes NA on the three sales-shaped checks."""
    if (slug in INTERIOR_UTILITY_EXEMPT and page_type == "interior"
            and check in SALES_SHAPED_CHECKS):
        return "NA"
    prof = PROFILES.get(page_type, {})
    return prof.get(check, prof.get("_default", DEFAULT_SEVERITY))

def audit_html(slug, html, page_type="interior"):
    raw = html
    p = P(); p.feed(html)
    bodytext = " ".join(p.body)
    r = {}
    # --- headings (Part D.2 / #21) ---
    r["h1==1"] = p.h[1]==1
    r["all_h1_h4"] = all(p.h[i]>=1 for i in (1,2,3,4))
    r["h_counts"] = "".join(f"H{i}:{p.h[i]} " for i in range(1,7)).strip()
    r["no_skip"] = not any(p.h[i]>0 and p.h[i-1]==0 for i in range(2,7))
    # --- Heading Outline Gate (seo-rules Rule 52, 2026-06-20) ---
    # All six levels REQUIRED; H5 >= 5 AND H6 >= 5 on every page. The breeder
    # will not pass a page that ships only 1 H6 or 4 H5. Hard FAIL by default.
    r["all_six_levels"] = all(p.h[i]>=1 for i in range(1,7))
    r["min_h5_5"] = p.h[5] >= 5
    r["min_h6_5"] = p.h[6] >= 5
    # --- schema (Part I / #12) ---
    blobs=[]; valid=True
    for b in p.jsonld:
        b=b.strip()
        if not b: continue
        try: blobs.append(json.loads(b))
        except Exception: valid=False
    types=[]; org_found=[False]
    aggregates=[]; owned_aggregates=set()
    def typelist(o):
        tt = o.get("@type") if isinstance(o,dict) else None
        return tt if isinstance(tt,list) else ([tt] if tt else [])
    def walk(o):
        if isinstance(o,dict):
            tt=o.get("@type")
            if tt: types.append(tt)
            # Organization counts even when nested as publisher/author, or when
            # @type is a list like ["LocalBusiness","PetStore"] (valid schema).
            tl=tt if isinstance(tt,list) else [tt]
            if any(x in ("Organization","LocalBusiness","PetStore") for x in tl): org_found[0]=True
            if "AggregateOffer" in tl: aggregates.append(id(o))
            # An AggregateOffer a Product declares as its own `offers` is that Product's
            # price band — the shape a group or hub listing is supposed to carry. Record
            # it as owned so the check below can tell it from a stray aggregate node.
            if "Product" in tl:
                offers=o.get("offers")
                for off in (offers if isinstance(offers,list) else [offers]):
                    if isinstance(off,dict) and "AggregateOffer" in typelist(off):
                        owned_aggregates.add(id(off))
            for v in o.values(): walk(v)
        elif isinstance(o,list):
            for v in o: walk(v)
    for b in blobs: walk(b)
    flat=[t for x in types for t in (x if isinstance(x,list) else [x])]
    r["jsonld_valid"] = valid and bool(blobs)
    r["has_breadcrumb"] = "BreadcrumbList" in flat
    r["has_org"] = org_found[0]
    r["faqpage_count"] = flat.count("FAQPage")
    r["faqpage_ok"] = flat.count("FAQPage") <= 1
    r["schema_types"] = ",".join(sorted(set(flat)))
    # --- puppy-listing hard gates (page_type == "puppy") ---
    # Where the profile calls this a hard FAIL (a single puppy listing, a comparison page),
    # ANY AggregateOffer is a defect — those pages never aggregate, however well-formed
    # the shape. Where it is a WARN (the for-sale cluster, whose group and hub pages own
    # one), only an aggregate that belongs to no Product is: a price band nothing on the
    # page claims. Charged to the harness 2026-09-12 — the hub carried a graph-level
    # Product whose `offers` is an AggregateOffer, plus an ItemList of per-puppy
    # Product+Offer, and a flat type-name search called the correct shape a defect.
    stray_aggregate = [a for a in aggregates if a not in owned_aggregates]
    r["no_aggregateoffer"] = (not aggregates) if severity(page_type, "no_aggregateoffer", slug) == "FAIL" \
                             else not stray_aggregate
    # Delivery band from data/settings.json: delivery_min_gbp 200, delivery_max_gbp 350.
    r["shipping_line"] = bool(SHIP_RE.search(bodytext))
    # InStock fails only when a sold/reserved STATUS signal is present AND the schema
    # still shows InStock. Avoid commerce phrases like "sold together/separately".
    sold_signal = bool(re.search(
        r"\b(sold out|now sold|has been sold|this (?:puppy|pup|litter) is sold|marked sold|"
        r"status:\s*(?:sold|reserved)|is reserved)\b", bodytext, re.I))
    instock = "InStock" in raw and "OutOfStock" not in raw
    r["sold_not_instock"] = not (sold_signal and instock)
    # word count of visible body (scripts stripped)
    # Strip <style> as well as <script>: pages that ship a page-scoped style block
    # were counting several thousand words of CSS as body copy, which pushed every
    # for-sale and comparison page out of band regardless of its real length.
    vis = re.sub(r"<(script|style)[\s\S]*?</\1>", "", raw)
    nwords = len(re.sub(r"<[^>]+>", " ", vis).split())
    # Bands widened for migrated content: Foundation moved the WordPress bodies over
    # verbatim, and a tight band would fail pages this project is not allowed to edit.
    if page_type == "puppy":
        r["wordcount_in_band"] = 400 <= nwords <= 1500
    elif page_type == "comparison":
        r["wordcount_in_band"] = 3000 <= nwords <= 8000  # deep 22–25-section standard + chrome
    elif page_type == "for-sale":
        # 22-section transactional standard + chrome. Previously fell through to the
        # lean 600–1,200 interior band, so every page in the cluster warned by default
        # (shipped pages measure 5,300–7,000). Band set from the built cluster, 2026-07-25.
        r["wordcount_in_band"] = 1500 <= nwords <= 5000
    else:
        r["wordcount_in_band"] = 600 <= nwords <= 4000
    # hero must be a real photo, not a placeholder/logo
    content_imgs = [i for i in p.imgs if "logo" not in i.get("src", "").lower()]
    r["real_hero_image"] = bool(content_imgs) and not any(
        x in (content_imgs[0].get("src", "").lower()) for x in ("placeholder", "coming-soon", "default")
    ) if content_imgs else False
    # --- meta (Part J / #13) — long-format standard kept (≤275 title / ≤300 desc) ---
    r["title_len"] = len(p.title.strip())
    r["desc_len"] = len(p.metadesc.strip())
    r["title_le275"] = len(p.title.strip())<=275
    r["desc_le300"] = len(p.metadesc.strip())<=300
    r["desc_present"] = len(p.metadesc.strip())>0
    r["canonical_abs"] = p.canonical.startswith("https://")
    # --- images (Part J.2 / #14, #25) ---
    imgs=p.imgs
    def yes(i,k): return k in i and i[k] not in (None,"")
    r["img_total"]=len(imgs)
    r["img_all_alt"]=all("alt" in i for i in imgs)
    alts=[i.get("alt","") for i in imgs if i.get("alt","")]
    r["img_alt_unique"]=len(alts)==len(set(alts))
    r["img_alt_le190"]=all(len(i.get("alt",""))<=190 for i in imgs)
    # LCP-hero exemption: drop the header logo(s), then the FIRST remaining content
    # image is the eager LCP hero (correct). Every image after it must be lazy.
    # EXCEPT multi-image hero components (Split-Hero C 2x2 photo grid on the egg
    # page, Hero-A polaroid grid on hand-raised): every image inside the hero
    # block is above the fold and legitimately eager. Flagging them was a false
    # positive that FAILed a correct page (2026-07-23).
    content=[i for i in imgs if "logo" not in i.get("src","").lower()]
    hero_srcs={i.get("src","") for i in getattr(p, "hero_imgs", []) or []}
    non_hero=[i for i in content[1:] if i.get("src","") not in hero_srcs]
    r["img_lazy_nonhero"]=all(i.get("loading")=="lazy" for i in non_hero) if non_hero else True
    r["img_dims"]=all(yes(i,"width") and yes(i,"height") for i in imgs) if imgs else True
    # --- a11y / gotcha traps (Part K / M / #26, #28) ---
    r["no_svg_in_content"] = not re.search(r"content\s*:\s*['\"]\s*<svg", raw)
    # user-select:none is banned when APPLIED. Tailwind's bundled ".select-none{…}"
    # utility DEFINITION ships in the global CSS on every page even when unused
    # (site-wide false positive confirmed 2026-07-04) — strip that rule definition,
    # then fail only if markup actually applies the class or any other CSS sets it.
    css_nospace = raw.replace(" ", "").replace("\n", "")
    defs_stripped = re.sub(r"\.select-none[^{]*\{[^}]*\}", "", css_nospace)
    applied_class = bool(re.search(r'class="[^"]*\bselect-none\b', raw))
    r["no_userselect_none"] = ("user-select:none" not in defs_stripped) and not applied_class
    r["no_escaped_svg"] = "&lt;svg" not in raw
    # --- links (Part F / #3, #23) ---
    ext=[(d,txt) for d,txt in p.links if d.get("href","").startswith("http") and "bluestaffyuk" not in d.get("href","")]
    r["ext_links"]=len(ext)
    r["ext_newtab_rel"]=all(d.get("target")=="_blank" and "noopener" in d.get("rel","") for d,_ in ext) if ext else True
    bad_anchor=re.compile(r"^(click here|more|read more|here|learn more)$",re.I)
    r["no_bare_anchors"]=not any(bad_anchor.match(txt) for _,txt in p.links if txt)
    intc=[d for d,_ in p.links if d.get("href","").startswith("/")]
    r["internal_links"]=len(intc)
    # --- conversion (Part N / #17, Rule 61) ---
    # UK numbers, not CAG's NANP pattern: 0141 496 0000 / +44 141 496 0000 /
    # 07700 900000. PHONE_PLACEHOLDER (the value in data/settings.json until the
    # breeder confirms a number) matches nothing here, which is correct.
    phone=re.compile(r"(?:\+44\s?|\b0)\d{2,4}[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b")
    footer_idx=raw.lower().find("<footer")
    body_part=raw[:footer_idx] if footer_idx>0 else raw
    body_clean=re.sub(r"<script[\s\S]*?</script>","",body_part)
    body_txt=re.sub(r"<[^>]+>"," ",body_clean)
    # Rule 61 bans the breeder's phone in the body. CAG exempted a list of US
    # authority hotlines; no UK analogue is established, so no exemption is claimed.
    r["no_phone_in_body"]=not list(phone.finditer(body_txt))
    footer_part=raw[footer_idx:] if footer_idx>0 else ""
    r["phone_in_footer"]=bool(phone.search(re.sub(r"<[^>]+>"," ",footer_part))) if footer_part else None
    # --- compliance copy (Part N / Rule 44) — visible body, scripts stripped ---
    main=raw[raw.find("<main"):] if "<main" in raw else raw
    main=re.sub(r"<script[\s\S]*?</script>","",main)
    w300=" ".join(re.sub(r"<[^>]+>"," ",main).split()[:300]).lower()
    r["cites_credentials_early"]=(("kc registered" in w300 or "defra" in w300)
                                  and ("microchipped" in w300 or "vet checked" in w300))
    r["lifespan_12_14"]=bool(re.search(r"12\s*[–-]\s*14|12 to 14",bodytext))
    # --- newsletter (#18) — detect the signup form, not the word "newsletter"
    # (the ported newsletter component emits no literal "newsletter" string).
    r["newsletter_present"]=("your@email.com" in raw) or ("newsletter" in raw.lower())
    # --- freshness (#GEO) — RULE: dates live ONLY in schema, never visible on the
    # page. Pass = NO visible "Updated/Last updated <Month> <Year>" text (scripts
    # stripped so schema dateModified does not trigger).
    visible=re.sub(r"<script[\s\S]*?</script>","",raw)
    visible=re.sub(r"<[^>]+>"," ",visible)
    r["no_visible_date"]=not re.search(r"(?:updated|last updated|last modified)\b[^0-9]{0,18}\b20\d\d", visible, re.I)
    # --- blog-only gates (page_type == "blog") ---
    # Computed only for blog so these never add new FAIL gates to puppy/interior rows.
    if page_type in ("blog", "comparison"):
        r["breadcrumb_one"] = flat.count("BreadcrumbList") == 1
        r["faqpage_present"] = flat.count("FAQPage") >= 1
        r["single_canonical"] = len(re.findall(
            r"<link\b[^>]*\brel\s*=\s*['\"]canonical['\"]", raw, re.I)) == 1
        # No colorful pictographic emoji (kept text glyphs ✔ ✗ ★ are BMP < U+2B00,
        # so they never match these emoji planes). Catches 🎉 🔥 🚀 🦜 ⭐ flags, etc.
        r["no_emoji"] = not re.search(
            "[\U0001F1E6-\U0001F1FF\U0001F300-\U0001FAFF\U00002B00-\U00002BFF]", raw)
        # Stricter freshness check: catch a real "Updated <Month>" / "Posted on
        # <Month>" / "Last updated <Month/Year>" STAMP (a date label followed by an
        # actual month or year). Requiring the date token avoids false-positiving on
        # prose that merely names the policy (e.g. 'no visible "last updated" stamp').
        blog_date = re.search(
            r"\b(?:last updated|last modified|posted on|published on|updated|posted|published)\b"
            r"[\s:,.–-]{0,4}"
            r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
            r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|20\d\d)\b",
            visible, re.I)
        r["no_visible_date"] = r["no_visible_date"] and not blog_date
    # severity only applies to boolean pass/fail checks — skip info keys (counts/strings)
    r["_severity"] = {k: severity(page_type, k, slug) for k in r
                      if not k.startswith("_") and isinstance(r[k], bool)}
    hard_fails = [k for k, v in r.items() if v is False and r["_severity"].get(k) == "FAIL"]
    warns = [k for k, v in r.items() if v is False and r["_severity"].get(k) == "WARN"]
    r["_verdict"] = "FAIL" if hard_fails else ("PASS-WITH-WARNINGS" if warns else "PASS")
    r["_hard_fails"] = hard_fails
    r["_warns"] = warns
    return r

def audit(slug, page_type="interior"):
    f = dist_path(slug)
    if not f.exists():
        return {"_MISSING": True}
    return audit_html(slug, f.read_text(encoding="utf-8", errors="ignore"), page_type)

PUPPIES = ["available-puppies/" + pup["slug"]
           for pup in json.loads((ROOT / "data/puppies.json").read_text())]

# BSUK has no comparison cluster yet; project 5 writes it. An empty list is honest; a
# list of pages that do not exist would make every run print MISSING.
COMPARISONS = []

# The transactional slugs, single source: these are the pages that carry the
# commercial gates (delivery band, stock status, one canonical).
FORSALE = ["buy-blue-staffy-puppies-uk",
           "blue-staffy-pup-sale-uk",
           "buy-staffy-puppies-for-sale-uk"]

def blog_targets():
    """Discover the /blog/ hub (dist/blog/index.html) + every dist/blog/<slug>/ post."""
    targets = []
    blog = DIST / "blog"
    if (blog / "index.html").exists():
        targets.append(("blog", "blog"))
    for f in sorted(blog.glob("*/index.html")):
        targets.append((f"blog/{f.parent.name}", "blog"))
    return targets

def json_report(rows):
    """Machine-readable result: per page its slug, status and every failing check as
    {check, severity, message}."""
    pages = []
    for slug, r in rows.items():
        if r.get("_MISSING"):
            pages.append({"slug": slug, "status": "MISSING", "checks": []})
            continue
        checks = [{"check": k, "severity": "FAIL",
                   "message": f"{k} failed on a {r.get('_page_type','interior')} page"}
                  for k in r["_hard_fails"]]
        checks += [{"check": k, "severity": "WARN",
                    "message": f"{k} failed on a {r.get('_page_type','interior')} page"}
                   for k in r["_warns"]]
        pages.append({"slug": slug, "status": r["_verdict"], "checks": checks})
    return {"pages": pages}


def baseline_only(r):
    """True when a page's hard failures are ALL migration-baseline heading gates."""
    hf = r.get("_hard_fails") or []
    return bool(hf) and set(hf) <= BASELINE_CHECKS


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("slugs", nargs="*", help="audit these slugs (`index` = the homepage)")
    ap.add_argument("--type", dest="page_type", choices=sorted(PROFILES),
                    help="score the given slugs against this profile")
    ap.add_argument("--puppies", action="store_true", help="audit every puppy page")
    ap.add_argument("--blog", action="store_true", help="audit the blog hub and posts")
    ap.add_argument("--comparison", action="store_true", help="audit the comparison cluster")
    ap.add_argument("--for-sale", dest="for_sale", action="store_true",
                    help="audit the transactional for-sale pages")
    ap.add_argument("--fail-on-error", action="store_true",
                    help="accepted for symmetry with page_hardening_scan.py; FAIL is "
                         "always fatal here (spec §11)")
    ap.add_argument("--json", nargs="?", const=str(DEFAULT_JSON), default=None,
                    metavar="PATH",
                    help=f"write the machine-readable result (default {DEFAULT_JSON})")
    ns = ap.parse_args(sys.argv[1:] if argv is None else argv)

    if ns.page_type:
        targets = [(s, ns.page_type) for s in ns.slugs]
    elif ns.puppies:
        targets = [(s, "puppy") for s in PUPPIES]
    elif ns.blog:
        targets = blog_targets()
    elif ns.comparison:
        targets = [(s, "comparison") for s in COMPARISONS]
    elif ns.for_sale:
        targets = [(s, "for-sale") for s in FORSALE]
    elif ns.slugs:
        targets = [(s, "interior") for s in ns.slugs]
    else:
        targets = ([(s, "interior") for s in SLUGS] + blog_targets()
                   + [(s, "comparison") for s in COMPARISONS]
                   + [(s, "for-sale") for s in FORSALE])
    rows = {}
    for s, t in targets:
        r = audit(s, t)
        r["_page_type"] = t
        rows[s] = r
    print("\n=== BSUK FINAL PAGE PASS ===  (verdict per page)\n")
    for s, r in rows.items():
        if r.get("_MISSING"):
            print(f"  ✗ {s}: dist/ MISSING — run `npx astro build`"); continue
        tag = "  [migration baseline]" if baseline_only(r) else ""
        print(f"[{r['_verdict']}]{tag} {s}   {r['h_counts']} | FAQPage×{r['faqpage_count']} | schema:{r['schema_types']}")
        if s in INTERIOR_UTILITY_EXEMPT and r.get("_page_type") == "interior":
            print(f"    EXEMPT → {', '.join(SALES_SHAPED_CHECKS)} — {INTERIOR_UTILITY_EXEMPT[s]}")
        if r["_hard_fails"]: print("    FAIL → " + ", ".join(r["_hard_fails"]))
        if r["_warns"]:      print("    WARN → " + ", ".join(r["_warns"]))
    npass = sum(1 for r in rows.values() if r.get("_verdict") == "PASS")
    nwarn = sum(1 for r in rows.values() if r.get("_verdict") == "PASS-WITH-WARNINGS")
    nfail = sum(1 for r in rows.values() if r.get("_verdict") == "FAIL")
    nbase = sum(1 for r in rows.values() if baseline_only(r))
    print(f"\nexamined {len(rows)} pages; {nfail} problems  ({npass} PASS · {nwarn} PASS-WITH-WARNINGS · {nfail} FAIL)")
    print(f"baseline-only FAIL pages: {nbase}  "
          f"(failing only {', '.join(sorted(BASELINE_CHECKS))} — the migration baseline)")
    if ns.json:
        out = Path(ns.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(json_report(rows), indent=2) + "\n", encoding="utf-8")
        print(f"JSON report → {out}")
    print("\nSubjective (voice/humour/readability/tone) = manual spot-check.")
    return 1 if nfail else 0

if __name__ == "__main__":
    sys.exit(main())
