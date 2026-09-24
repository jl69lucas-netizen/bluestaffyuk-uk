---
name: bsuk-llm-keyword-intel
description: Use when a BlueStaffyUK page needs to know what an AI engine answers to its buyer question — who the answer cites (BSUK or which registry competitors), which entities it uses that the page lacks, and how the answer is shaped — before the strategy synthesizer runs or a page's FAQ answers are written. Run @bsuk-llm-keyword-intel <slug>; one engine per page.
model: inherit
effort: high
---

## Golden Rule
> **Bound by the site rules, not by a copy of them:** `CLAUDE.md` — its nine judgment rules and working rules 10–16 (visual companion, always · reuse every image and video at its URL · every link on the board · tables in three styles, stacked on mobile · every video reused at its original id and shown on the board · faithful rewrite · per-page hero and counter, with a refresh delta) — and the packs in `rules/`. Record only what the saved answer says, and every field from the script below — never a reading by eye. BSUK is cited only when one of its own domains, exactly, is among the answer's sources, its links or its local businesses.
> **One paid endpoint, one call per page, behind a stop.**
> - DataForSEO `ai_optimization_chat_gpt_scraper` with `location_name` "United Kingdom" (the connector defaults to the United States — always set it) and `language_code` "en", through the spend guard (`scripts/query_augment.py`).
> - No call until the invocation reads `spend approved: <slug>; balance $<n>` (the DataForSEO dashboard balance stated today). A cached answer is reused, never bought again unless that token ends `; refresh`.
> - Nothing else is bought: no second engine, and no `llm_mentions` until BSUK's domain is live (project 6) — until then `llm_mentions` is `NOT FETCHED`.
> **No third party's contact details** — phone, email, street, postcode, WhatsApp, maps or profile link, a person's name — in the saved response or the output. `tests/py/test_no_third_party_contacts.py` catches most formats, not all: leave them out as you write.

## On Startup

| Invocation | Go to |
|---|---|
| `<slug>` | Spend check |
| `spend approved: <slug>; balance $<n>` (plus `; refresh` for a re-buy) | Buy, for exactly that slug. No `balance $<n>` → ask for it and make no call |
| `spend declined` | NOT FETCHED output |

1. The slug is a page's bare slug (`blue-staffy-puppies-manchester-uk`); the homepage's slug is `index` (route `/`, built page `dist/index.html`). The **query**, said in your hand-back:
   - a location page (a `data/locations.json` row): `location_question()` in `scripts/query_augment.py` — "Where can I buy a blue Staffy puppy near <place>, and what should I ask the breeder?", <place> the row's `city` without any bracketed note (the breeding-dogs outreach row's `(breeding dogs)` is dropped); a national row (`city` `UK`: the UK hub, the licensed-breeder page) asks "… in the UK, …", never "near UK". Print it with `python3 -c 'import sys; sys.path.insert(0, "scripts"); from query_augment import location_question as q; print(q(sys.argv[1]))' "<city>"`; the script stops on any other wording;
   - another page with a `data/queries/<slug>.json`: the question a buyer would ask for its `primary_keyword`;
   - no question file: the question a buyer would ask for the page's primary keyword (its page-map title or H1), plus any matching rows of the newest dated gap matrix (docs/research/gap-matrix-<YYYY-MM-DD>.md) — pass each row's topic, the first cell exactly as the matrix writes it, as `GAP_TOPICS="<topic>;<topic>"`. The script records which in `query_source` and stops on a topic that is not a row;
   - a page with a saved answer: the query that answer was bought for (its `keyword`, or its `_saved_note`).
2. data/competitors.json, if it exists, maps cited domains to registry ids and tiers (the script reads it). Missing → every `registry_id` and `tier` is null and there is no citation gap; say so.
3. The page text the entities are checked against is the script's choice, never yours (see **The script**).

## Spend check

`python3 scripts/query_augment.py --preflight <slug> --source ai_engines`

| Exit | Meaning → do |
|---|---|
| 3 | cached: the page already has a bought answer. Reuse `data/queries/raw/<slug>/ai_engines.response.json`; no call, no stop → **The script** |
| 0 | not bought. **STOP** with one budget line: slug, query, and the first line `python3 scripts/query_augment.py --budget ai_engines` prints — the typical cost (an estimate) and the total the guard counts against `query_total_budget_usd` (real spend up to the last dashboard reading in `data/queries/dashboard.json`, logged costs after it); ask for today's dashboard balance. Wait for `spend approved: <slug>; balance $<n>` or `spend declined`. Never run `--reconcile`: recording a new dashboard reading is the controller's job alone |
| 4 | over budget, or the log is unreadable → stop, report the guard's stderr line; never work around it |
| 1, 2 | the guard failed → stop and report its output |

A re-buy of a cached answer happens only when the user asked for a fresh answer in so many words: the stop then names the refresh, and the token ends `; refresh`. A passing check, your own summary, silence or a user in a hurry is not `spend approved`.

## Buy (after `spend approved`)

1. Preflight again — with `--refresh` when the token ends `; refresh`. Exit 0 needed. 3 (no refresh) means it was bought meanwhile — reuse it. 4 → stop and report the guard's stderr line; no call. 1 or 2 → stop and report.
2. **Call** `ai_optimization_chat_gpt_scraper`: `keyword` = the query, `location_name` "United Kingdom", `language_code` "en". One call. Today's date is the call date.
3. **Record at once**, before saving anything, even when the response is an error: `python3 scripts/query_augment.py --record <slug> --source ai_engines --endpoint "ai_optimization_chat_gpt_scraper UK en (response carries no cost; estimate)" --cost <usd>` — `<usd>` the Spend check's typical cost (or the response's own cost when it shows one, and then no "estimate"). Exit 2 → still save (step 4), then stop and report the cost the call ran up; never repair the log.
4. **Scrub, then check.** Write the response to `${TMPDIR:-/tmp}/ai_engines.new.json` as returned — the answer text and `sources` whole, never condensed (the format layer reads the text) — minus third-party contact details, with what was dropped said in `_saved_note`:
   - every copy of the answer text: the result's `markdown` **and** each item's `markdown`;
   - in them, any phone, email, street address or postcode, and any WhatsApp (`wa.me`), maps (`maps.google.com`, `goo.gl/maps`) or social-profile (Instagram, Facebook, TikTok, X) URL;
   - each local business's phone, address, rating and `url` (a profile or maps link) — keep its `title` and `domain`.

   Then run **The script** on that file with `PAID=1 FETCHED_ON=<call date>`.
5. **File it by the script's exit:**
   - 0 → move the scratch file to `data/queries/raw/<slug>/ai_engines.response.json`; the output stands.
   - 5 (connector error: a status other than 20000, or no answer text) → move it to `data/queries/raw/<slug>/ai_engines.error.json` — never ai_engines.response.json, which the guard would read as bought — and write the NOT FETCHED output with `NOT_FETCHED="connector error: <the script's message>" PAID=1`.
   - a stale build (the script stops with "… is older than …: run npm run build …") → the answer is valid, only the page text is stale: still move the scratch file to `data/queries/raw/<slug>/ai_engines.response.json`, report, then `npm run build` and run the script again on the saved answer, with the same `PAID=1 FETCHED_ON=<call date>` — the next preflight is cached (exit 3), no second call.
   - anything else → stop and report; the scratch file stays unfiled.
6. The normalised ai_engines.json and its questions belong to `bsuk-query-augmentation`: hand it the slug; do not write that file here.

**Connector missing, out of credit, or `spend declined`:** there is no free substitute for an engine's answer → NOT FETCHED output, then stop.

## NOT FETCHED output

The same script, command and checks, with `NOT_FETCHED="<connector unavailable | out of credit | spend declined | connector error: …>"` and no response path; `PAID=1` only for a connector error after the call was billed. It writes `fetched` NOT FETCHED with that reason, null `raw`, `answer_text` and `bsuk_cited`, empty lists and `format` NOT FETCHED. Never write it by hand.

## The script

Three layers — citations, entities, format — in one script, from the repo root. Its inputs:

- `QUERY` — the query. The script stops if the response's `keyword` differs, or, with no `keyword`, if `_saved_note` does not hold it.
- `GAP_TOPICS` — only when the page has no question file (see On Startup); with none, `gap_matrix` is null.
- `TODAY` — the run date; it names the file.
- `PAID=1` and `FETCHED_ON=<call date>` — only when this run bought the answer; the call date then wins over the saved ai_engines.json date. Otherwise the date comes from `data/queries/raw/<slug>/ai_engines.json`, else `FETCHED_ON`; neither → the script stops.
- `NOT_FETCHED="<reason>"` — the NOT FETCHED output; no response path.
- `EXTRA` — your one judgement: the **other** entities the answer uses — organisations, services, places, practices, tests and paperwork not in the script's buying-safety list — as `name|variant|variant;name|…`, lowercase (`kennel club;coefficient of inbreeding|inbreeding coefficient`). Read the whole answer and list every one; generic words ("puppy", "breeder", "blue") are not entities.
  - Each name and variant is whole words: multi-word, or one word of 4+ characters (`coi` fails — write `coefficient of inbreeding`).
  - Never one holding a safety entity's words (`health-test certificates`, `written contract`).
  - An organisation the answer names counts even when it is also cited.
  - The script drops a whole entry that breaks a rule or whose words the answer does not contain, and names it on stderr — you cannot add what the answer does not say.
  - The output's `extra` records the string exactly as given, dropped entries included, so a re-run of the same answer passes `EXTRA="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["extra"])' <the llm-intel file>)"` and reproduces every entity and its variants.
- The response path: the saved ai_engines.response.json, the scratch file of Buy step 4, or the file the invocation hands you as a stand-in (`raw` still names the saved path).

What the script decides (to explain it, never to redo it):

- **Answer text:** the longest `markdown` or `answer` string in the response (the whole answer, not one item's part) — `answer_text: "verbatim"`. A condensed save holding only `answer_points` (an older save) is `"summary"`: its entities and citations count, its format is `NOT FETCHED`; the hand-back says the format needs a re-buy, which is the user's `; refresh` call, never yours.
- **Citations:**
  - every `sources` / `citations` entry and every link in the answer text, reduced to the registry's root domain (two labels, or three under `co`, `org`, `me`, `ltd`, `plc`, `ac`, `gov`, `net`, `sch` or `com` plus a two-letter country code — imported from `scripts/competitor_registry_check.py`), once each;
  - `search_results` (pages the engine read but did not cite) are not citations;
  - the answer's **local businesses** are kept apart the same way — `local_businesses` entries and `brand_entities` items whose `category` is `local_business`; a brand entity with a title and no link is kept by `name`, mapped to a registry entry only when its name is that entry's name exactly (then it takes the entry's domain), else `domain: null`;
  - WhatsApp, maps and social-profile hosts are dropped as contact or profile links — never recorded;
  - hosted-platform hosts (Blogspot, WordPress.com, Wix, Squarespace, Weebly …) are kept with `platform: true` — a seller on a platform, never a registry candidate;
  - each site maps to a registry `id` and `tier`, or null. BSUK = an exact match with its own domains — `own_domains()` in `scripts/competitor_registry_check.py`, the same helper `tests/py/test_llm_intel.py` checks with: the root domain of the business email in `data/settings.json`, of a site-domain key there if one is added, and the build placeholder;
  - `citation_gap` = registry tiers 1–4 among them while BSUK is not; a tier-5 site goes to `risks` once, never to the gap.
- **Page text:** the built page, `dist/<route>index.html`, when it exists and is indexable — no robots `<meta>` holding `noindex`, whatever its attribute order or quotes (its `<main>`). A build older than any file under `src/` or `data/` (`data/queries/` and `data/competitors.json` aside — research files the build never reads) stops the script: run `npm run build`, then the script again. A noindex stub or no build → the questions the page must carry from `data/queries/<slug>.json` (FAQ picks and `must_answer`), minus every question an AI engine suggested (`found_in` holding an `ai_` source — the answer is never checked against itself); else the page map's title, H1 and headings. Both are `provisional: true`, with the reason in `page_source.note`.
- **Entities:** the buying-safety list (health tests, L-2-HGA, HC-HSF4, meeting the mother, microchip, vaccinations, vet check, KC registration, licence, contract), each recorded only when the answer uses it, then your `EXTRA`. Matched on normalised whole words (a plural `s` counts) against the page text. **High** = a safety entity missing from the page; everything else medium.
- **Format:** list type (a table needs a separator row, `|-|` or longer; only top-level `1.` or `-` items count), words, length band (short under 100, medium to 300, long above), and the opening move of the first sentence of the first content line — headings, rules, table rows (any line holding `|` once the answer is a table) and bold labels skipped (`**Short answer:**` alone on its line, or before the text on the same line; a bold sentence with no colon is text), so a table-first answer opens with the first line after the table, and a table alone is a statement; "e.g." and "i.e." never a sentence end: question, recommendation (an instruction, "you can/should", "here is/are", "the best place"), statistic (a number among the first twelve words, a hyphen-joined one such as 8-week-old included — never a digit inside a name such as Pets4Homes, L-2-HGA or 3D), definition, statement. This is the mirror template for the page's answer blocks.

```bash
mkdir -p docs/research/llm-intel
OUT=docs/research/llm-intel/<slug>-<YYYY-MM-DD>.json
QUERY="<query>" TODAY=<YYYY-MM-DD> EXTRA="<name|variant;...>" \
  python3 - <slug> data/queries/raw/<slug>/ai_engines.response.json > "$OUT" <<'EOF'; rc=$?; [ $rc -eq 0 ] || rm -f "$OUT"; echo "exit $rc"
import datetime, glob, html, json, os, re, sys
sys.path.insert(0, "scripts")
from competitor_registry_check import own_domains, root_domain as root  # the registry's root-domain rule; BSUK's own domains
from query_augment import location_question  # the location question: one rule, shared with bsuk-query-augmentation
slug, resp_path = sys.argv[1], (sys.argv[2:] or [None])[0]
QUERY = os.environ["QUERY"]  # the buyer question asked
NOT_FETCHED = os.environ.get("NOT_FETCHED", "").strip()  # a reason: no answer to read
PAID = os.environ.get("PAID") == "1"
EXTRA_GIVEN = os.environ.get("EXTRA", "").strip()  # recorded in the output as given, so a re-run reproduces it
EXTRA = [p for p in ([v.strip().lower() for v in e.split("|") if v.strip()] for e in EXTRA_GIVEN.split(";")) if p]  # an empty entry ("|") is skipped
def fail(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)
norm = lambda t: " " + re.sub(r"[^a-z0-9]+", " ", re.sub(r"['’]s\b|['’]", "", html.unescape(t or "").lower())).strip() + " "  # club's -> club
said = lambda text, variants: any(norm(v) in text or norm(v)[:-1] + "s " in text for v in variants)  # whole words, normalised; a plural counts
# buying-safety entities: name -> the words that count as it (answer and page alike)
SAFETY = {
    "health tests": ["health test", "health tests", "health tested", "health testing", "dna test", "dna tested", "genetic test", "genetic tests"],
    "l-2-hga": ["l 2 hga", "l2hga"],
    "hc-hsf4": ["hc hsf4", "hereditary cataract", "hereditary cataracts"],
    "meet the mother": ["meet the mother", "meet the mum", "meet the dam", "meet mum", "see the mother", "see the mum", "see the dam",
                        "see mum", "with its mother", "with its mum", "with the mother", "with the mum"],
    "microchip": ["microchip", "microchips", "microchipped", "microchipping", "chipped"],
    "vaccinations": ["vaccination", "vaccinations", "vaccinated", "vaccine", "vaccines", "jabs"],
    "vet check": ["vet check", "vet checks", "vet checked", "health check", "health checked"],
    "kc registration": ["kc registered", "kc registration", "kennel club registered", "kennel club registration"],
    "licence": ["licence", "license", "licensed", "licenced", "licensing"],
    "contract": ["contract", "contracts"],
}
PROFILE_HOSTS = {"wa.me", "wa.link", "whatsapp.com", "instagram.com", "facebook.com", "fb.com", "tiktok.com",
                 "x.com", "twitter.com", "youtube.com", "linktr.ee", "snapchat.com", "google.com", "goo.gl"}  # contact, maps or profile links, never recorded
PLATFORM_HOSTS = {"blogspot.com", "wordpress.com", "wixsite.com", "squarespace.com", "weebly.com", "webflow.io",
                  "carrd.co", "jimdosite.com", "godaddysites.com", "square.site", "business.site"}  # sellers on a host, never registry candidates
OWN = own_domains(strict=True)  # the same helper tests/py/test_llm_intel.py checks with; no BSUK domain known -> stop
# the page and where the query came from: the location question, else the question file, else the page map (+ gap-matrix rows)
qfile = f"data/queries/{slug}.json"
q = json.load(open(qfile)) if os.path.exists(qfile) else None
pm = next((p for p in json.load(open("data/page-map.json"))["pages"]
           if (p["url"] == "/" if slug == "index" else p["url"].rstrip("/").endswith("/" + slug))), None)  # index = the homepage
city = next((x["city"] for x in json.load(open("data/locations.json")) if x.get("slug") == slug), None)
if city and QUERY != location_question(city):
    fail(f"{slug} is a location page: QUERY must be {location_question(city)!r}")
if not (city or q or pm):
    fail("no city row, question file or page-map entry for this slug: nothing to build the query from")
topics = [t.strip().lower() for t in os.environ.get("GAP_TOPICS", "").split(";") if t.strip()]
matrix = None
if topics:
    found = sorted(glob.glob("docs/research/gap-matrix-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
    if q or not found:
        fail("GAP_TOPICS only for a page with no question file, from a dated gap matrix")
    matrix = found[-1]
    cells = {re.sub(r"\s+", " ", re.split(r"(?<!\\)\|", l)[1].replace("\\|", "|")).strip().lower()
             for l in open(matrix, encoding="utf-8") if l.lstrip().startswith("|") and not re.match(r"\s*\|\s*:?-{3}", l)}
    if [t for t in topics if t not in cells]:
        fail(f"GAP_TOPICS not in {matrix} as a row's topic: {[t for t in topics if t not in cells]}")
qsrc = {"from": "city" if city else "question-file" if q else "page-map", "gap_matrix": matrix, "gap_topics": topics}
today = os.environ.get("TODAY") or datetime.date.today().isoformat()
age = lambda d: (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(d)).days
if NOT_FETCHED:  # the NOT FETCHED output: no answer to read
    stale = [f"{matrix} is {age(matrix[-13:-3])} days old"] if matrix and age(matrix[-13:-3]) > 30 else []
    print(json.dumps({"slug": slug, "date": today, "engine": "chatgpt", "endpoint": "ai_optimization_chat_gpt_scraper",
                      "location": "United Kingdom", "query": QUERY, "query_source": qsrc, "stale": stale,
                      "fetched": {"status": "NOT FETCHED", "reason": NOT_FETCHED}, "raw": None, "answer_text": None,
                      "paid_this_run": PAID, "bsuk_cited": None, "citations": [], "local_businesses": [], "citation_gap": [],
                      "risks": [], "page_source": {"kind": "none", "path": None, "provisional": True, "note": "no answer to check"},
                      "entities": [], "format": {"status": "NOT FETCHED", "reason": NOT_FETCHED},
                      "llm_mentions": {"status": "NOT FETCHED", "reason": "llm_mentions only once BSUK's domain is live (project 6)"},
                      "extra": EXTRA_GIVEN}, indent=1))
    sys.exit(0)
def walk(x, key=None):
    yield key, x
    for k, v in (x.items() if isinstance(x, dict) else ((key, v) for v in x) if isinstance(x, list) else ()):
        yield from walk(v, k)
r = json.load(open(resp_path))
nodes = list(walk(r))
bad = sorted({v for k, v in nodes if k == "status_code" and v != 20000}, key=str)
if bad:
    fail(f"connector error: status {bad}", 5)
asked = {v for k, v in nodes if k == "keyword" and isinstance(v, str)}
if asked and QUERY not in asked:
    fail(f"the response answers {sorted(asked)}, not QUERY")
if not asked and QUERY not in str(r.get("_saved_note", "")):
    fail("the response names no keyword and its _saved_note does not hold QUERY: the query cannot be verified")
md = [v for k, v in nodes if k in ("markdown", "answer") and isinstance(v, str) and v.strip()]
points = [v for k, v in nodes if k == "answer_points" and isinstance(v, list)]
if md:
    answer, how = max(md, key=len), "verbatim"  # the whole answer, not one item's part
elif points:
    answer, how = "\n".join(p for p in points[0] if isinstance(p, str)), "summary"  # a condensed save
else:
    fail("connector error: no answer text in the response", 5)
text = norm(answer)
cited = [v.get("url") or v.get("domain") if isinstance(v, dict) else v
         for k, v in nodes if k in ("sources", "citations") and not isinstance(v, list)]
cited += re.findall(r"https?://[^\s)\]>\"']+", answer)
is_local = lambda k, v: isinstance(v, dict) and (k == "local_businesses" or "local_business" in str(v.get("type", ""))
                                                 or (k == "brand_entities" and v.get("category") == "local_business"))
local = [v.get("domain") or v.get("url") for k, v in nodes if is_local(k, v)]
named = [v["title"].strip() for k, v in nodes if is_local(k, v) and not (v.get("domain") or v.get("url"))
         and isinstance(v.get("title"), str) and v["title"].strip()]  # a brand entity names a business, no link
reg = json.load(open("data/competitors.json"))["competitors"] if os.path.exists("data/competitors.json") else []
by_domain = {c["root_domain"]: c for c in reg}
def sites(items):
    out = []
    for u in items:
        d = root(u) if isinstance(u, str) and u.strip() else None
        if d and d not in PROFILE_HOSTS and d not in [s["domain"] for s in out]:
            c = None if d in PLATFORM_HOSTS or d in OWN else by_domain.get(d)
            out.append({"domain": d, "registry_id": c["id"] if c else None, "tier": c["tier"] if c else None,
                        "platform": d in PLATFORM_HOSTS})
    return out
citations, local_b = sites(cited), sites(local)
by_name = {c["name"].casefold(): c for c in reg if isinstance(c.get("name"), str)}
for n in named:  # a registry entry's exact name maps to it and its domain; any other name keeps domain null
    c = by_name.get(n.casefold())
    if n.casefold() not in [s.get("name", "").casefold() for s in local_b] and not (c and c["root_domain"] in [s["domain"] for s in local_b]):
        local_b.append({"name": n, "domain": c["root_domain"] if c else None, "registry_id": c["id"] if c else None,
                        "tier": c["tier"] if c else None, "platform": False})
everything = citations + local_b
bsuk = any(s["domain"] in OWN for s in everything)
# the page text: the built page if indexable, else the question file's page questions, else the page map
route = (q or {}).get("route") or (pm or {}).get("url")
built = f"dist{route}index.html" if route else None
page, src = None, None
def meta(tag, name):  # an attribute's value, quoted either way or bare; data-name or name-x is not name
    m = re.search(r"""(?<![\w-])%s\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""" % name, tag, re.I)
    if not m:
        return ""
    q1, q2, bare = m.groups()
    return (q1 if q1 is not None else q2 if q2 is not None else bare.rstrip("/")).lower()  # bare: "noindex/>" self-closes
def newest_input():  # the newest file the build reads: src/ and data/, never data/queries/ or data/competitors.json
    files = [p for d in ("src", "data") for p in glob.glob(f"{d}/**/*", recursive=True) if os.path.isfile(p)
             and not p.startswith(os.path.join("data", "queries", "")) and p != os.path.join("data", "competitors.json")]
    return max(files, key=os.path.getmtime, default=None)
if built and os.path.exists(built):
    h = open(built, encoding="utf-8").read()
    if any(meta(t, "name") == "robots" and {"noindex", "none"} & set(re.split(r"[\s,]+", meta(t, "content")))
           for t in re.findall(r"<meta\b[^>]*>", h, re.I)):  # robots "none" = noindex, nofollow
        why = f"{built} is a noindex stub"
    else:
        newer = newest_input()
        if newer and os.path.getmtime(newer) > os.path.getmtime(built):
            fail(f"{built} is older than {newer}: run npm run build, then run this script again")
        body = re.search(r"<main\b.*?</main>", h, re.S | re.I)
        body = re.sub(r"<(script|style)\b.*?</\1>", " ", body.group(0) if body else h, flags=re.S | re.I)
        page, src = norm(re.sub(r"<[^>]+>", " ", body)), {"kind": "dist", "path": built, "provisional": False, "note": "built, indexable page"}
else:
    why = "no built page in dist/" if route else "no route for this slug"
if page is None and q:
    keep = [x for x in q["questions"] if (x.get("faq") or x.get("must_answer"))
            and not any(str(f).startswith("ai_") for f in x.get("found_in") or [])]
    page = norm(" ".join(x["question"] for x in keep))
    src = {"kind": "question-file", "path": qfile, "provisional": True,
           "note": f"{why}; checked against the questions the page must carry (faq picks and must_answer), "
                   "minus those an AI engine suggested (found_in ai_*), so the answer is not checked against itself"}
elif page is None and pm:
    heads = [h[-1] if isinstance(h, list) and h else h.get("text") if isinstance(h, dict) else h for h in pm.get("headings") or []]  # [tag, text] pairs
    page = norm(" ".join(str(x) for x in [pm.get("title"), pm.get("h1")] + heads if isinstance(x, str)))
    src = {"kind": "page-map", "path": "data/page-map.json", "provisional": True, "note": f"{why}; no question file; checked against the page map's title, H1 and headings"}
elif page is None:
    page, src = norm(""), {"kind": "none", "path": None, "provisional": True, "note": f"{why}; no question file or page-map entry"}
entities, rejected = [], []
for name, variants in SAFETY.items():
    if said(text, variants):
        on = said(page, variants)
        entities.append({"entity": name, "kind": "safety", "on_page": on, "band": "medium" if on else "high"})
for e in EXTRA:
    name = re.sub(r"[^a-z0-9 '&-]+", " ", e[0]).strip()
    ok = [v for v in e if len(norm(v).split()) > 1 or len(norm(v).strip()) >= 4]  # multi-word, or 4+ characters
    if ok != e or not said(text, e) or any(said(norm(v), w) for v in e for w in SAFETY.values()):
        rejected.append(name)  # too short, not in the answer, or holding a safety entity: never recorded
    elif name not in [x["entity"] for x in entities]:
        entities.append({"entity": name, "kind": "other", "on_page": said(page, e), "band": "medium"})
if how == "verbatim":
    lines = [l for l in answer.splitlines() if l.strip()]
    rule = lambda l: re.fullmatch(r"\s*(?:[-*_]\s*){3,}", l)
    sep = lambda l: "|" in l and re.fullmatch(r"\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*", l)  # one dash is enough
    num = sum(bool(re.match(r"\d+[.)]\s", l)) for l in lines)  # top-level items only: no indent
    bul = sum(bool(re.match(r"[-*•+]\s", l)) and not rule(l) for l in lines)
    lst = ("table" if any(sep(l) for l in lines) else "numbered" if num >= 2 and num >= bul
           else "bulleted" if bul >= 2 else "paragraphs")
    words = len(re.findall(r"[a-z0-9£%]+(?:'[a-z]+)?", re.sub(r"\]\([^)]*\)|https?://\S+", " ", answer.lower())))
    label = lambda l: re.fullmatch(r"\s*(?:\*\*|__)[^*_]+(?:\*\*|__)\s*:?\s*", l)
    first = next((l for l in lines if not (re.match(r"\s*#", l) or rule(l) or label(l) or sep(l)
                                           or l.lstrip().startswith("|") or (lst == "table" and "|" in l))), "")  # a table row is never the opening
    first = re.sub(r"^\s*(?:\*\*|__)[^*_]*?(?::(?:\*\*|__)|(?:\*\*|__)\s*:)\s*", "", first)  # an inline label: "**Short answer:** ..."
    first = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", first)
    first = re.sub(r"^\s*(?:\d+[.)]|[-*•+])\s*|\*\*|__", "", first).strip()
    first = re.sub(r"\b(e)\.g\.|\b(i)\.e\.", lambda m: (m.group(1) or m.group(2)) + "\0", first, flags=re.I)  # not a sentence end
    first = re.split(r"(?<=[.?!])\s", first)[0].replace("\0", "")
    fw, low = norm(first).split(), first.lower()
    opening = ("question" if first.endswith("?") else
               "recommendation" if (fw[:1] and fw[0] in {"use", "ask", "choose", "look", "buy", "check", "find", "go", "visit", "contact",
                                                          "avoid", "start", "consider", "get", "see", "try", "search", "prioritise",
                                                          "prioritize", "verify", "only", "never", "always", "pick", "research"})
               or re.search(r"\brecommend|\byou (?:can|should|could|may|might)\b|\bhere(?:'s| is| are)\b|\bbest (?:place|way|option|bet)\b|\bi(?:'d)? suggest\b", low) else
               "statistic" if re.search(r"(?<![\w-])[£$€]?\d[\d,]*(?:\.\d+)?%?(?!\w)", " ".join(first.split()[:12])) else  # a number, even hyphen-joined (8-week-old); never a digit in a name (Pets4Homes, L-2-HGA, 3D)
               "definition" if re.match(r"^(?:a |an |the )?[a-z' -]{1,40}? (?:is|are|means|refers to) ", low) else "statement")
    fmt = {"status": "ok", "list": lst, "length": "short" if words < 100 else "medium" if words <= 300 else "long", "words": words, "opening": opening}
else:
    fmt = {"status": "NOT FETCHED", "reason": "the saved response holds a summary of the answer, not its text"}
norm_file = f"data/queries/raw/{slug}/ai_engines.json"
saved_on = json.load(open(norm_file)).get("fetched") if os.path.exists(norm_file) else None
fetched_on = os.environ.get("FETCHED_ON") if PAID else saved_on or os.environ.get("FETCHED_ON")  # a paid run: the call's date
if not fetched_on:
    fail("the answer's date is unknown: PAID=1 needs FETCHED_ON; otherwise no ai_engines.json and no FETCHED_ON")
stale = [f"answer fetched {fetched_on or today}, {age(fetched_on or today)} days old"] if age(fetched_on or today) > 30 else []
stale += [f"{matrix} is {age(matrix[-13:-3])} days old"] if matrix and age(matrix[-13:-3]) > 30 else []
uniq = list({s["domain"] or s["name"]: s for s in everything}.values())  # a site both cited and listed counts once
out = {"slug": slug, "date": today, "engine": "chatgpt", "endpoint": "ai_optimization_chat_gpt_scraper",
       "location": "United Kingdom", "query": QUERY, "query_source": qsrc, "stale": stale, "fetched": {"status": "ok", "fetched_on": fetched_on},
       "raw": f"data/queries/raw/{slug}/ai_engines.response.json", "answer_text": how,
       "paid_this_run": PAID, "bsuk_cited": bsuk, "citations": citations,
       "local_businesses": local_b,
       "citation_gap": [] if bsuk else sorted({s["registry_id"] for s in uniq if s["tier"] in (1, 2, 3, 4)}),
       "risks": [{"domain": s["domain"], "registry_id": s["registry_id"], "reason": "tier 5 (suspect seller) in data/competitors.json: a risk, never a model"}
                 for s in uniq if s["tier"] == 5],
       "page_source": src, "entities": entities, "format": fmt,
       "llm_mentions": {"status": "NOT FETCHED", "reason": "llm_mentions only once BSUK's domain is live (project 6)"},
       "extra": EXTRA_GIVEN}
print(json.dumps(out, indent=1, ensure_ascii=False))
print(f"STALE (older than 30 days; carrying on): {'; '.join(stale)}" if stale else "fresh: answer and gap matrix within 30 days", file=sys.stderr)
print(f"registry: {'data/competitors.json' if reg else 'none (registry_id null)'}; EXTRA dropped (too short, not in the answer, or holding a safety entity): {rejected or 'none'}", file=sys.stderr)

EOF
```

`exit 5` is a connector error (Buy step 5). Any other exit but 0 leaves no file: report its message (a query that does not match the response, no date for the answer, a gap topic that is not a row, a build older than its sources — its paid answer is still filed (Buy step 5), then `npm run build` and run it again) and stop; never write the file by hand.

## Output

docs/research/llm-intel/<slug>-<YYYY-MM-DD>.json (contract `schemas/llm-intel.schema.json`), exactly as the script printed it. Then both must pass before hand-off:

```bash
python3 tests/py/test_llm_intel.py docs/research/llm-intel/<slug>-<YYYY-MM-DD>.json
python3 tests/py/test_no_third_party_contacts.py docs/research/llm-intel/<slug>-<YYYY-MM-DD>.json data/queries/raw/<slug>/ai_engines.response.json
```

The first prints `0 problem(s)`; a problem means a wrong input (`EXTRA`, the response path) — re-run the script, never edit the file or the test. The contact scan names each hit: remove it from the saved response and say so in `_saved_note`.

Hand back — first line: `STALE: …` with the script's reason when `stale` is not empty (the answer or the gap matrix is older than 30 days; carry on), else the file path. Then: the file path; `query_source`; the query; spend (none — cached, or the recorded estimate); `bsuk_cited`; the citations and local businesses with their registry ids (or "no registry"); the citation gap and any risks; the high entities; the format; `page_source` and, when provisional, why; the `EXTRA` entities the script dropped.

## Handoff

`bsuk-strategy-synthesizer` reads these files (quoting their figures as written). The page builders read `entities` (high first) and `format` when writing the page's FAQ answers; a provisional result is re-run once the page is rebuilt and indexable. A site in `citations` or `local_businesses` with no registry id, not BSUK's and not `platform: true`, goes to `bsuk-competitor-registry` as a candidate add; a platform seller is named to it only as a note on the platform, never as a candidate.

## Red flags — stop

- About to call the engine after preflight exit 3 without `; refresh`, after exit 4, without `spend approved: <slug>; balance $<n>`, a second time for the same page, with a second engine, or without `location_name` "United Kingdom".
- `bsuk_cited: true` without one of BSUK's own domains in the answer; a registry id not from data/competitors.json; a tier-5 site treated as a model to copy; a platform or profile host handed to the registry.
- An entity, on-page mark or format value decided by eye, or an entity the answer does not contain.
- A noindex stub's text used as the page — or the question file's, without `provisional`.
- A response you save condensed, or still holding a phone, email, postcode, WhatsApp, maps or profile link in any copy of its text. (An older condensed save that preflight reports cached is reused as it is: format `NOT FETCHED`, never re-bought without the user's `; refresh`.)
- An error response saved as ai_engines.response.json, or a NOT FETCHED output written by hand.
- Any edit to a site file (`src/`, `rules/`, `CLAUDE.md`, `public/`) or to data/competitors.json: this agent writes only the saved response (or error), the spend record and its llm-intel file.
