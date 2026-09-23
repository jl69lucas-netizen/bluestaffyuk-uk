---
name: bsuk-competitive-keyword-gap-agent
description: Use after bsuk-competitor-intel has written competitor reports and the BSUK profile, to find the topics BlueStaffyUK's competitors have a dedicated page for that BSUK does not target — for every competitor, one competitor, or one page type — before planning new pages or a content calendar. Run @bsuk-competitive-keyword-gap-agent, <id>, or --type <city|comparison|care|price>.
model: inherit
effort: high
---

## Golden Rule
> **Bound by the site rules, not by a copy of them:** `CLAUDE.md` and the packs in `rules/`. One question: what does a competitor have a dedicated page for that BSUK does not? Topics, page types, coverage, points and bands come from the script below and nothing else — never a search volume, traffic, ranking, a "top pages" guess or a reading by eye. If the script errors, stop and report it; never finish the table by hand.
> **Summarise, never copy.** A topic is a lowercased keyword phrase; the reasons are your words. No competitor sentence, and no seller's contact details (phone, email, street, postcode, WhatsApp, a person's name) anywhere in the output.
> **Fetch tools:** Firecrawl **map and scrape only**, standard proxy — never crawl, agent, extract, interact or search — and Playwright (navigate, snapshot) for an empty scrape; only under **Freshness**. Tools are inherited: connector names differ per session. No paid call; DataForSEO is not this agent's.

## On Startup

1. Mode: all competitors (default), one `<id>`, or `--type <city|comparison|care|price>` (`care` = `care-guide`). "First line" means the first line of your hand-back and of the output header.
2. **BSUK's side:** the BSUK profile, docs/research/competitors/bsuk.json (`bsuk-competitor-intel --bsuk`; indexable pages only), used as it is — a rebuilt page at a formerly stubbed URL is coverage. Missing, or its `pages` `NOT FETCHED` → the fallback `data/page-map.json`, which the script names; say so in the first line and ask for `--bsuk`. With the page map as the source, its `stub-noindexed` entries never count as coverage. With the profile as the source, the page map is read once, read-only, for the `stub-noindexed` routes missing from the profile — to label a gap, never to cover one. Never read `src/` or `dist/` yourself.
3. **Competitors' side:** every docs/research/competitors/*.json but bsuk.json (the script lists them), or only `<id>.json` (none → stop, hand to `bsuk-competitor-intel`). data/competitors.json gives tiers; missing → "unknown", treated as tiers 1–4; say so.
4. The newest docs/research/gap-matrix-*.md holds the page-type and city counts: quote it, never recount; none → "none yet".

## Freshness

The script lists as `stale` each competitor whose `pages` is `NOT FETCHED` or more than 30 days old; tier 5 goes to `stale_tier5` — never re-fetched, never counted, left out. A stale report gives no gaps.

- **One stale:** re-fetch it — 1 `firecrawl_map` (`limit` 500), then up to 6 `firecrawl_scrape` (markdown only): the homepage and one each of `listing`, `price` or `faq`, `care-guide` or `breed-guide`, `city`, `about`, typed by the script's table. Ceiling 7.
- **More than one:** **STOP** before any fetch: the stale ids, tiers, `fetched_on`, N and the ceiling 7 × N. Resume only on `fetch approved: --all`, or `fetch declined` (run without them, listed as not used). A passing check, your summary, silence, "I trust you" or a hurry is not approval; for some of them, the controller runs one `<id>` at a time. While stopped, write nothing. Never fetch beyond the ceiling.

A re-fetch never edits the intel report: write a scratch copy in `${TMPDIR:-/tmp}` with `pages` = `{"status": "ok", "fetched_on": "<today>", "values": [...]}` (`url`, `title`, `h1`, `h2` per page), pass it in the report's place, and hand `bsuk-competitor-intel <id>` a re-run. Report the fetch count every run (0 when none).

## Find and score — by script

From the repo root. Reports in scope after `"$B"`: none for all (the script lists them), `docs/research/competitors/<id>.json` for one, a scratch copy in a stale report's place. `TODAY=<YYYY-MM-DD>` sets today. `CUT="<name>[,<name>]"` is intel's name clause: no script can tell a name, so read the first run's topics and, when one holds a business, kennel or person's name, re-run with it (whole words, lowercase); the text is cut before it.

```bash
B=docs/research/competitors/bsuk.json; [ -f "$B" ] || B=data/page-map.json
python3 - "$B" > "${TMPDIR:-/tmp}/keyword-gap.json" <<'EOF'
import datetime, glob, json, os, re, sys
from urllib.parse import urlparse
src, reports = sys.argv[1], sys.argv[2:]
today = datetime.date.fromisoformat(os.environ.get("TODAY") or datetime.date.today().isoformat())
CUT = [c.split() for c in os.environ.get("CUT", "").lower().split(",") if c.strip()]  # names to cut before, whole words
# --- intel's page-type table, copied line for line (tests/py/test_agent_snippets.py keeps it so) ---
rows = json.load(open("data/locations.json"))
slugs = {r["city"].lower().replace(" ", "-") for r in rows if r["city"] != "UK" and "(" not in r["city"]}
w = lambda t: r"(^|[-/])" + t + r"([-/]|$)"
TABLE = [
    ("blog", [w("blog"), w("news"), w("articles"), w("posts"), r"/(19|20)\d\d/"]),
    ("city", [w(s) for s in slugs]),
    ("comparison", [r"-vs-", r"versus"]),
    ("price", [r"price", r"cost", r"fees"]),
    ("health", [r"health", w("dna"), r"testing"]),
    ("care-guide", [r"care", r"feeding", r"training", r"grooming"]),
    ("contact", [r"contact", r"enquir"]),
    ("about", [w("about"), r"our-story"]),
    ("breed-guide", [w("breed"), w("guide"), r"breed-guide", r"breed-info", r"temperament"]),
    ("faq", [r"faq", r"questions"]),
    ("reviews", [r"review", r"testimonial"]),
    ("listing", [r"puppies", r"puppy", w("pup"), r"litter", r"available", w("sale")]),
]
kind = lambda path: next((name for name, pats in TABLE if any(re.search(p, path) for p in pats)), None)
# --- end of intel's table ---
def words(t):  # lowercase word tokens; "versus" is written "vs"
    return ["vs" if x == "versus" else x for x in re.findall(r"[a-z0-9]+", (t or "").lower())]
def fold(x):  # singular, one spelling: puppies -> puppy, prices -> price, staffie -> staffy
    x = "staffy" if x in ("staffie", "staffies") else x
    return x[:-3] + "y" if x.endswith("ies") and len(x) > 4 else x[:-1] if x.endswith("s") and not x.endswith("ss") and len(x) > 3 else x
cities = {tuple(words(r["city"])) for r in rows if "(" not in r["city"]}
towns = {c for c in cities if c != ("uk",)}
# intel's keyword rule: breed terms, and intent or place words
BREED = {("staffy",), ("staffie",), ("staffies",), ("staffordshire", "bull", "terrier"), ("sbt",)}
PLACE = {("puppies",), ("puppy",), ("for", "sale"), ("breeder",), ("breeders",), ("price",), ("kc", "registered"), ("blue",)} | cities
UNITS = sorted(BREED | PLACE, key=len, reverse=True)
INTENT = [tuple(fold(x) for x in i) for i in [("puppy",), ("breeder",), ("price",), ("for", "sale"), ("kc", "registered")] + sorted(towns)]
HIGH = [("licence",), ("license",), ("licensed",), ("licensing",), ("health", "test"), ("health", "tested"),
        ("health", "testing"), ("tested",), ("l", "2", "hga"), ("hc",)]
STOP = {"a", "an", "the", "in", "for", "of", "to", "and", "with", "near", "our", "your", "how", "much", "is", "are", "what", "uk", "sale", "buy"}
KEY = {"listing", "price", "faq", "care-guide", "breed-guide", "city", "about"}
BY_TYPE = {"about", "contact", "faq"}  # a topic with no keyword run is covered by a BSUK page of the same type
has = lambda ws, phrase: any(tuple(ws[i:i + len(phrase)]) == phrase for i in range(len(ws)))
def runs(ws):  # maximal qualifying runs: 2-6 words, pattern unit to pattern unit, a breed term and an intent/place word
    units = []
    for i in range(len(ws)):
        u = next((u for u in UNITS if tuple(ws[i:i + len(u)]) == u), None)
        if u:
            units.append((i, i + len(u), u in BREED))
    found = {(a[0], b[1]) for a in units for b in units if b[1] > a[0] and 2 <= b[1] - a[0] <= 6
             and any(u[2] for u in units if a[0] <= u[0] and u[1] <= b[1])
             and any(not u[2] for u in units if a[0] <= u[0] and u[1] <= b[1])}
    return sorted(r for r in found if not any(o != r and o[0] <= r[0] and r[1] <= o[1] for o in found))
long_run = lambda ws: max((r for r in runs(ws) if r[1] - r[0] >= 3), key=lambda r: (r[1] - r[0], -r[0]), default=None)
content = lambda t: frozenset(fold(x) for x in words(t) if x not in STOP)
towns_in = lambda t: frozenset(c for c in towns if has(words(t), c))
route = lambda u: urlparse(u).path or "/"
def text(page):  # the H1, or the title cut at its first "|", " – ", " — " or " - "
    return (page.get("h1") or "").strip() or re.split(r"\||\s[–—-]\s", page.get("title") or "")[0].strip()
def topic(page, ptype):
    """(topic, dedicated) or (None, why skipped)."""
    t = text(page)
    ws = words(t)
    if not ws:
        return None, "no title or H1"
    ws = ws[:min([i for c in CUT for i in range(len(ws)) if ws[i:i + len(c)] == c], default=len(ws))]
    if not ws:
        return None, "name only"
    if not content(" ".join(ws)):
        return None, "no content words"
    if "vs" in ws and (ptype == "comparison" or ptype is None):  # the "X vs Y" core of the clause holding vs
        clause = words(next(c for c in re.split(r"[:?!|,(.]|\s[–—-]\s", t.lower().replace("versus", "vs")) if "vs" in words(c)))
        clause = clause[:min([i for c in CUT for i in range(len(clause)) if clause[i:i + len(c)] == c], default=len(clause))]
        i = clause.index("vs") if "vs" in clause else len(clause)
        core = clause[max(0, i - 3):i + 4]
        if core:
            return " ".join(core), 3 if long_run(core) else 0
    best = long_run(ws)
    if best is None and not runs(ws) and ptype in (None, "about", "contact", "listing") and not any(has(ws, h) for h in HIGH):
        return None, "no keyword topic"
    if best is None or any(has(ws, c) and not has(ws[best[0]:best[1]], c) for c in towns):
        return " ".join(ws), 3 if best else 0  # whole H1: no run of 3+ words, or the run would cut the city
    return " ".join(ws[best[0]:best[1]]), 3
def btype(x):  # a BSUK page's type: its route, else (not the homepage) its title words, as intel's --bsuk does
    r = route(x["url"]).lower()
    slug = "/" + re.sub(r"[^a-z0-9]+", "-", (x.get("title") or "").split("|")[0].lower()).strip("-") + "/"
    return kind(r) or (kind(slug) if r != "/" else None)
def covering(pages, c, cs, ptype):
    hits = [x for x in pages if any(c <= content(f) and towns_in(f) == cs for f in (x.get("title") or "", x.get("h1") or ""))]
    return min(hits, key=lambda x: (btype(x) != ptype, len(x.get("title") or ""), x["url"]))["url"] if hits else None
pmap = json.load(open("data/page-map.json"))["pages"]
noindex = [p for p in pmap if "stub-noindexed" in p.get("refresh_flags", []) + p.get("defects", [])]
b = json.load(open(src))
if "id" in b and b["pages"]["status"] != "ok":  # the profile holds no pages: fall back, and say so
    src, b = f"data/page-map.json (fallback: {src} pages NOT FETCHED)", {"pages": pmap}
if "id" in b:  # the profile: indexable pages only (intel), used as they are
    bsuk = b["pages"]["values"]
    noindex = [p for p in noindex if route(p["url"]) not in {route(x["url"]) for x in bsuk}]  # label lookup only
else:  # the page map: its noindex stubs never count as coverage
    bsuk = [x for x in b["pages"] if route(x["url"]) not in {route(p["url"]) for p in noindex}]
reg = json.load(open("data/competitors.json"))["competitors"] if os.path.exists("data/competitors.json") else []
tiers = {c["id"]: c.get("tier") for c in reg}
out = {"today": str(today), "bsuk_source": src, "bsuk_pages": len(bsuk), "registry": bool(reg),
       "cut": [" ".join(c) for c in CUT], "used": [], "stale": [], "stale_tier5": [], "skipped": []}
groups = {}
for path in reports or sorted(glob.glob("docs/research/competitors/*.json")):
    r = json.load(open(path))
    if r["id"] == "bsuk":
        continue
    tier = tiers.get(r["id"], "unknown")
    p = r["pages"]
    if p["status"] != "ok" or (today - datetime.date.fromisoformat(p["fetched_on"])).days > 30:
        out["stale_tier5" if tier == 5 else "stale"].append({"id": r["id"], "tier": tier, "fetched_on": p.get("fetched_on", "NOT FETCHED")})
        continue
    out["used"].append({"id": r["id"], "tier": tier, "fetched_on": p["fetched_on"]})
    for page in p["values"]:
        path_ = route(page["url"]).lower()
        ptype = kind(path_)
        t, how = topic(page, ptype)
        if t is None:
            out["skipped"].append({"url": page["url"], "why": how})
            continue
        fw = [fold(x) for x in words(t)]
        groups.setdefault(content(t), []).append({
            "topic": t, "type": ptype, "url": page["url"], "tier5": tier == 5, "dedicated": how,
            "key": 2 if ptype in KEY or path_ == "/" else 0, "intent": 2 if any(has(fw, i) for i in INTENT) else 0,
            "always_high": any(has(words(t), h) for h in HIGH)})
gaps, covered = [], []
for c, ps in groups.items():
    types = sorted({q["type"] for q in ps if q["type"]})
    ptype = min(types, key=lambda t: (t not in KEY, t)) if types else None
    t = min((q["topic"] for q in ps), key=lambda s: (len(s), s))
    row = {"topic": t, "type": ptype, "types": types,
           "urls": sorted({q["url"] for q in ps if not q["tier5"]}), "tier5_urls": sorted({q["url"] for q in ps if q["tier5"]})}
    dedicated = max(q["dedicated"] for q in ps)
    hit = covering(bsuk, c, towns_in(t), ptype)
    if hit is None and dedicated == 0 and ptype in BY_TYPE:
        same = [x for x in bsuk if btype(x) == ptype]
        hit = min(same, key=lambda x: (len(x.get("title") or ""), x["url"]))["url"] if same else None
    if hit:
        covered.append(dict(row, bsuk_page=hit))
        continue
    row.update(tier5_only=not row["urls"], bsuk_page=None, noindex_page=covering(noindex, c, towns_in(t), ptype),
               dedicated=dedicated, key=max(q["key"] for q in ps), no_bsuk_page=3, intent=max(q["intent"] for q in ps),
               always_high=any(q["always_high"] for q in ps))
    row["score"] = row["dedicated"] + row["key"] + row["no_bsuk_page"] + row["intent"]
    row["band"] = "high" if row["score"] >= 7 or row["always_high"] else "medium" if row["score"] >= 4 else "low"
    gaps.append(row)
for k in ("used", "stale", "stale_tier5"):
    out[k].sort(key=lambda s: s["id"])
out["skipped"].sort(key=lambda s: (s["url"], s["why"]))
out["gaps"] = sorted(gaps, key=lambda r: (-r["score"], r["topic"]))
out["covered"] = sorted(covered, key=lambda r: r["topic"])
print(json.dumps(out, indent=1))
EOF
```

What decides a row (to explain it, never to redo it):

- **Type:** intel's page-type table — the block between the `---` comments is intel's code line for line (`tests/py/test_agent_snippets.py` fails on drift; change intel first).
- **Topic:** from the H1 (else the title cut at `|`, ` – `, ` - `) by intel's keyword rule: the longest qualifying run of 3+ words; the whole text when there is none or the run would cut a `data/locations.json` city; a comparison's "X vs Y" core. Skipped (header count): no title or H1, a name only, stop words only, or no keyword run on an untyped, about, contact or listing page (licence and health-testing words excepted).
- **Covered:** every topic word (stop words out, plurals folded) in one BSUK page's title or H1, naming the same cities; an about, contact or FAQ topic with no run is covered by a BSUK page of that type. Same words = one row.
- **Points** (uncovered only): dedicated +3 (the topic holds a keyword run of 3+ words; a whole-text topic gets 0) · key page +2 (intel's key types or the homepage) · BSUK has no page +3 · buyer intent +2 (puppy, breeder, price, "for sale", "kc registered" or a city; not "blue"). 7+ = **high**, 4–6 = medium, under 4 = low; licence, licensed, licensing or health test(ed/ing), tested, L-2-HGA, HC in the topic = **always high**.

## Output

docs/research/keyword-gap-<YYYY-MM-DD>.md:

1. Header: mode; gap matrix or "none yet"; BSUK source and page count; competitors used (tier, `fetched_on`); stale ones and what happened; names cut; skipped count; fetch count; one line per forbidden request declined (a "top page" point, search volumes, skipping the script).
2. **Gaps**, in the script's order — Topic · Score with parts (`10 (3+2+3+2)`) · Band ("always high" when that set it) · Competitor URLs · BSUK page · Suggested page type (`type`, else `untyped`). BSUK page is "none", or "exists, not indexed — project 5 rebuild: <noindex_page>". Tier-5 URLs are plain text marked "(tier 5 — never link)".
3. **Already covered** — Topic · Competitor URL · BSUK page.
4. **High gaps** — one line each on why; "None" when none.
5. **Handoff** lines.

URLs as their source gives them. With `--type`, only that type's rows. Then `python3 tests/py/test_no_third_party_contacts.py docs/research/keyword-gap-<YYYY-MM-DD>.md` must print 0 — remove a hit, never change the test; it misses some formats, so leave contacts out as you write.

## Handoff

High gaps → `bsuk-content-architect` (topic, competitor URL, page type); a row with a `noindex_page` goes as "rebuild the stub <noindex_page>" (project 5), never a new page; a `tier5_only` row goes with no URL, marked "tier-5 only"; with the page-map fallback all are "provisional" until `--bsuk` and a re-run. The file → `bsuk-strategy-synthesizer` (medium gaps to the content calendar). Stale report → `bsuk-competitor-intel <id>`; no profile → `bsuk-competitor-intel --bsuk`.

## Red flags — stop

- A gap with no competitor URL from a `pages` list or this run's re-fetch (a tier-5-only row excepted, sent without one).
- A `stub-noindexed` page counted as coverage, or the page map used for coverage while the profile exists.
- A fetch for a fresh report or a tier-5 one; more than one re-fetched before `fetch approved: --all`.
- An intel report, data/competitors.json or any site file (`src/`, `rules/`, `CLAUDE.md`, `public/`, `data/`) edited: this agent writes only its keyword-gap file.
