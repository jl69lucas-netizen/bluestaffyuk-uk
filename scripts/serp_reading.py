#!/usr/bin/env python3
"""How Google reads this page — board block 1b, read from the saved Google SERP.

Every line this module prints is something the saved search result shows: the blocks on page
one and how many of each, who ranks and with what kind of page, what the AI Overview cites,
and which of our sections answers each People Also Ask question. What the saved response does
not carry is written `NOT FETCHED — <barrier>`, never inferred.

Inputs (data/queries/raw/<bare slug>/):
  serp_google.response.json  the raw DataForSEO serp_organic_live_advanced response, either the
                             API envelope (tasks[0].result[0].items) or the saved flat form
                             (items at the top level)
  serp_google.json           our processed file: fetched date, results, questions
                             (detail "serp_google_paa" / "serp_google_related")
  competitors.json           optional: measured pages, used to label a ranking page's type

    python3 scripts/serp_reading.py <slug>

Pure functions (read, block) are what the board builder will call; the CLI prints block().
Python 3.9 stdlib only.
"""
import json
import pathlib
import re
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
import query_augment as QA  # noqa: E402
import term_density as TD  # noqa: E402

ROOT = KM.ROOT

# What each page-one block rewards, in plain English. A type not listed is "shown on page one".
REWARDS = {
    "ai_overview": "A direct 40–60 word answer under a question heading; named entities; "
                   "a source an answer engine can quote.",
    "people_also_ask": "Question headings answered in their first sentence; FAQPage markup "
                       "that matches the visible questions and answers.",
    "local_pack": "The city named in the title, H1 and copy; true LocalBusiness facts.",
    "organic": "A page that matches the searcher's intent; the kinds of page that rank set "
               "the shape our page has to take.",
    "images": "Original photos with descriptive alt text and filenames.",
    "video": "A real video on the page, marked up with VideoObject.",
    "featured_snippet": "A list, table or 40–60 word paragraph directly under the matching "
                        "heading.",
    "related_searches": "Phrases Google links to this query; cover them as headings or copy "
                        "where they are true for us.",
}
UNKNOWN_REWARD = "shown on page one"

# The intent-synonym table: a question and a heading that share a concept are about the same
# thing even when they share no word ("How much are they?" / "What do they cost?"). Patterns run
# on the lower-cased raw text, so "£" survives. Pinned by tests/py/test_serp_reading.py.
INTENT_SYNONYMS = {
    "cost": (r"\bcosts?\b", r"\bprices?d?\b", r"£",
             r"\bhow much\b(?!.*\b(exercise|food|feed|eat|weigh\w*|sleep\w*|walk\w*|deposit)\b)"),
    "deposit": (r"\bdeposits?\b", r"\breserv(e|ed|es|ing|ation)\b"),
    "delivery": (r"\bdeliver(y|ed|s|ing)?\b", r"\btravel\w*\b", r"\bcollect(ion|ed|ing)?\b",
                 r"\btransport\w*\b"),
    "health": (r"\bhealth\w*\b", r"\btest(ed|s|ing)?\b", r"\bproblems?\b"),
    "temperament": (r"\baggress\w*\b", r"\btemperament\w*\b", r"\bbehaviou?r(al)?\b"),
    "breed_type": (r"\bpit ?bulls?\b", r"\bamerican\b"),
}

# Words every question and heading on a Blue Staffy page shares; they say nothing about which
# section answers. Removed before word overlap is counted (after QA.normalise and KM.STOP).
GENERIC = frozenset(
    "blue staffy puppy dog dogs london uk how what why when where which who do does did i my "
    "me your you can could will would should it its be get our we us there this that these "
    "they them much".split())

# Scoring a question against one heading or FAQ question (see _score).
EXACT, CONCEPT, WORD, HEADING_BONUS, THRESHOLD = 10, 2, 1, 1, 3

PAGE_TYPES = ("listing", "breeder", "guide", "other", "off-topic")
# The URL/title heuristic, used only when competitors.json has not measured the page:
#   listing  the URL or title says it sells: "for-sale", "for sale", "/sale/", "buy-sell",
#            "classified"
#   breeder  the domain or title names a breeder or kennel
#   guide    the URL path holds "guide", "blog", "advice" or "news", or the title asks a
#            question (starts how/what/why/are/is/do/can, or ends "?") or says "guide"
#   other    none of these (a video, an off-topic page)
_LISTING = re.compile(r"for[-_ ]sale|/sale/|buy-sell|classified", re.I)
_BREEDER = re.compile(r"breeders?|kennels?", re.I)
_GUIDE_URL = re.compile(r"/(?:[^/?#]*[-_])?(guide|blog|advice|news)s?(?:[-_/]|$)", re.I)
_GUIDE_TITLE = re.compile(r"^(how|what|why|are|is|do|does|can)\b|\?\s*$|\bguide\b", re.I)


# ── the saved response ──────────────────────────────────────────────────────────────────────
def items_of(resp):
    """The SERP items, from the API envelope or the saved flat form; [] when neither."""
    if not isinstance(resp, dict):
        return []
    if isinstance(resp.get("items"), list):
        return resp["items"]
    try:
        return resp["tasks"][0]["result"][0]["items"] or []
    except (KeyError, IndexError, TypeError):
        return []


def features(items):
    out = {}
    for it in items:
        t = it.get("type") or "unknown"
        out[t] = out.get(t, 0) + 1
    return out


def expectations(feats):
    return [{"signal": t, "count": n, "rewards": REWARDS.get(t, UNKNOWN_REWARD)}
            for t, n in feats.items()]


# ── matching a question to a section ────────────────────────────────────────────────────────
def concepts(text):
    low = (text or "").lower().replace("’", "'")
    return {c for c, pats in INTENT_SYNONYMS.items() if any(re.search(p, low) for p in pats)}


def content_words(text):
    """Normalised words that say what a text is about. A word that is itself a synonym-table
    term ("price", "deposit") is left to concepts(), so one shared word never scores twice."""
    return {w for w in QA.normalise(text).split()
            if w not in KM.STOP and w not in GENERIC and not concepts(w)}


def _faq_q(intent):
    """The visible question of an FAQ row node: its intent reads "Q: <question> — <note>"."""
    m = re.match(r"\s*Q:\s*(.*?)(?:\s+—|$)", intent or "")
    return m.group(1).strip() if m else ""


def section_texts(sec):
    """(text, is_heading) for a section's H2 and every node of its tree (any depth). An FAQ
    row's heading is a row id, so its question is read from the node's intent instead."""
    out = [(sec.get("heading") or "", True)]

    def walk(nodes):
        for n in nodes or []:
            q = _faq_q(n.get("intent"))
            out.append((q or n.get("heading") or "", False))
            walk(n.get("children"))
    walk(sec.get("tree"))
    return [(t, h) for t, h in out if t.strip()]


def _score(q, text, is_heading):
    """EXACT when the normalised texts are equal; else CONCEPT per shared intent concept plus
    WORD per shared content word, plus HEADING_BONUS when a scoring text is the section H2."""
    if QA.normalise(q) == QA.normalise(text):
        return EXACT
    s = CONCEPT * len(concepts(q) & concepts(text)) + WORD * len(content_words(q) & content_words(text))
    return s + HEADING_BONUS if s and is_heading else s


def answered_by(q, sections):
    """The id of the section that best answers `q`, or None when no text reaches THRESHOLD
    (an exact question scores EXACT, which is above it). One shared concept alone (2) is not
    enough: it needs a shared word or the section's own H2 behind it.
    Ties go to the section that comes first on the page."""
    best, best_id = 0, None
    for sec in sections or []:
        s = max((_score(q, t, h) for t, h in section_texts(sec)), default=0)
        if s > best:
            best, best_id = s, sec.get("id")
    return best_id if best >= THRESHOLD else None


def _questions(serp, items, detail, item_type):
    """Question texts from serp_google.json (by detail), then any the raw response adds."""
    seen, out = set(), []

    def add(t):
        k = QA.normalise(t)
        if t and k not in seen:
            seen.add(k)
            out.append(t.strip())
    for q in (serp or {}).get("questions") or []:
        if q.get("detail") == detail:
            add(q.get("text") or "")
    for it in items:
        if it.get("type") == item_type:
            for sub in it.get("items") or []:
                add(sub if isinstance(sub, str) else (sub or {}).get("title") or "")
    return out


# ── who ranks ───────────────────────────────────────────────────────────────────────────────
def _domain(url):
    m = re.match(r"https?://([^/?#]+)", url or "")
    return m.group(1) if m else ""


_DROPPED = re.compile(r"\bDropped(?: as off-topic)?:\s*(.*?)(?:\.\s+(?=[A-Z0-9])|\.?$)", re.S)
_URL = re.compile(r"https?://[^\s)]+")


def dropped(competitors):
    """{url: reason} for the pages competitors.json's `note` says it dropped as off-topic. The
    file has no structured field for this: the pool note records it in prose, e.g. "Dropped as
    off-topic: Google #5, a TikTok video (https://…), which sells no puppy and …". The reason is
    the text after the URL's closing bracket, or "dropped as off-topic" when there is none."""
    out = {}
    for m in _DROPPED.finditer((competitors or {}).get("note") or ""):
        sent = m.group(1)
        for u in _URL.finditer(sent):
            after = sent[u.end():].lstrip(")").strip(" ,;")
            after = re.sub(r"^(which|that)\s+", "", after)
            out[u.group(0).rstrip(".,;")] = after or "dropped as off-topic"
    return out


def page_type(url, title, competitors=None):
    """(type, basis). A page competitors.json dropped as off-topic is "off-topic"; then its
    measurement wins; else the URL/title heuristic."""
    gone = dropped(competitors)
    if url in gone:
        return "off-topic", f"dropped in competitors.json: {gone[url]}"
    for p in (competitors or {}).get("pages") or []:
        if p.get("url") == url:
            m = p.get("metrics") or {}
            why = QA.listing_reason(m)
            if why:
                return "listing", f"measured: {why}"
            if "LocalBusiness" in (m.get("schema_types") or []):
                return "breeder", "measured: LocalBusiness markup"
            break
    path = re.sub(r"^https?://[^/?#]+", "", url or "")
    if _LISTING.search(url or "") or _LISTING.search(title or ""):
        return "listing", "URL or title says for sale"
    if _BREEDER.search(_domain(url)) or _BREEDER.search(title or ""):
        return "breeder", "domain or title names a breeder or kennel"
    if _GUIDE_URL.search(path) or _GUIDE_TITLE.search((title or "").strip()):
        return "guide", "URL or title reads as a guide"
    return "other", "no listing, breeder or guide signal in URL or title"


def ranking(items, competitors=None):
    out = []
    for i, it in enumerate(x for x in items if x.get("type") == "organic"):
        url = it.get("url") or ""
        t, basis = page_type(url, it.get("title") or "", competitors)
        out.append({"pos": it.get("rank_group") or i + 1, "domain": it.get("domain") or _domain(url),
                    "url": url, "title": it.get("title") or "", "type": t, "basis": basis,
                    "video": bool(it.get("is_video"))})
    return out


def _refs(node):
    if isinstance(node, dict):
        for r in node.get("references") or []:
            yield r
        for v in node.values():
            if isinstance(v, (list, dict)):
                yield from _refs(v)
    elif isinstance(node, list):
        for v in node:
            yield from _refs(v)


def aio(items):
    """(cited domains | None, note). None when the AI Overview is there but its sources are not."""
    boxes = [it for it in items if it.get("type") == "ai_overview"]
    if not boxes:
        return [], "No AI Overview on page one."
    doms = []
    for b in boxes:
        for r in _refs(b):
            d = (r or {}).get("domain") or _domain((r or {}).get("url"))
            if d and d not in doms:
                doms.append(d)
    if doms:
        return doms, f"The AI Overview cites {len(doms)} domain{'s' if len(doms) != 1 else ''}."
    if any(b.get("asynchronous_ai_overview") for b in boxes):
        return None, ("NOT FETCHED — the AI Overview loads asynchronously, so the saved response "
                      "holds no answer text and no cited sources")
    return None, "NOT FETCHED — the saved AI Overview item carries no references"


def read(resp, serp, sections, competitors=None):
    items = items_of(resp)
    feats = features(items)
    cites, note = aio(items)
    return {
        "features": feats,
        "expect": expectations(feats),
        "paa": [{"q": q, "answered_by": answered_by(q, sections)}
                for q in _questions(serp, items, "serp_google_paa", "people_also_ask")],
        "related": [{"q": q, "answered_by": answered_by(q, sections)}
                    for q in _questions(serp, items, "serp_google_related", "related_searches")],
        "ranking": ranking(items, competitors),
        "aio_cites": cites,
        "aio_note": note,
    }


# ── the board block ─────────────────────────────────────────────────────────────────────────
def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _query(board):
    return KM.primary_of(board) or board.get("meta", {}).get("slug", "")


def _plural(n, one, many=None):
    return f"{n} {one if n == 1 else (many or one + 's')}"


def takeaways(r, sections):
    """Up to 6 bullets. Each is a count read from `r`, and any reading of it is labelled:
    "Reading:" for what the count suggests, "General guidance:" for advice that does not come
    from this search. No bullet without a number behind it."""
    out, rank = [], r["ranking"]
    if rank:
        n = len(rank)
        by_type = {t: sum(1 for x in rank if x["type"] == t) for t in PAGE_TYPES}
        # most_common keeps first-seen order on ties, and the ranking is in page order.
        top_dom, top_n = Counter(x["domain"] for x in rank).most_common(1)[0]
        if by_type["listing"] * 2 > n:
            out.append(f"{by_type['listing']} of {n} organic results are listing pages (URL, "
                       f"title or card grid says puppies for sale) and {by_type['breeder']} "
                       f"{'is a breeder page' if by_type['breeder'] == 1 else 'are breeder pages'}. "
                       "Reading: the pages ranking for this query are shopping pages, so ours "
                       "should put price and availability above the fold.")
        else:
            out.append(f"The {n} organic results are {by_type['listing']} listings, "
                       f"{by_type['breeder']} breeder, {by_type['guide']} guide and "
                       f"{by_type['other'] + by_type['off-topic']} other pages. Reading: no single page "
                       "type holds a majority.")
        if top_n > 1:
            out.append(f"{top_dom} holds {top_n} of the {n} organic results"
                       + ("; no breeder site ranks." if not by_type["breeder"] else "."))
    paa = r["paa"]
    if paa:
        gaps = [p["q"] for p in paa if not p["answered_by"]]
        if gaps:
            out.append(f"{len(paa) - len(gaps)} of {len(paa)} People Also Ask questions have a "
                       f"section that answers them; {_plural(len(gaps), 'gap')}: "
                       + "; ".join(f"“{g}”" for g in gaps) + ".")
        else:
            out.append(f"All {len(paa)} People Also Ask questions have a section that answers "
                       "them. General guidance: answer each one in the first sentence under its heading.")
    if "ai_overview" in r["features"]:
        what = (f"citing {', '.join(r['aio_cites'])}" if r["aio_cites"]
                else "its sources were not in the saved response")
        out.append(f"An AI Overview sits above the organic results ({what}). General guidance: "
                   "answer each question heading directly in its first 40–60 words.")
    vids = sum(1 for x in rank if x["video"])
    if vids and len(out) < 6:
        out.append(f"{vids} of {len(rank)} organic results are flagged as video. General "
                   "guidance: a real video with VideoObject markup is eligible for video results.")
    rel = r["related"]
    if rel and len(out) < 6:
        out.append(f"{_plural(len(rel), 'related search', 'related searches')}: "
                   + "; ".join(f"“{x['q']}” → " + (f"`{x['answered_by']}`" if x["answered_by"]
                                                     else "no section") for x in rel) + ".")
    return out[:6]


def _count_cell(e, r):
    """The box count, with the questions it holds for People Also Ask and related searches."""
    held = {"people_also_ask": len(r["paa"]), "related_searches": len(r["related"])}.get(e["signal"])
    return f"{e['count']} ({_plural(held, 'question' if e['signal'] == 'people_also_ask' else 'phrase')})" \
        if held else e["count"]


def render(r, query, fetched, sections):
    heads = {s.get("id"): s.get("heading") for s in sections or []}
    lines = [
        f"This is what Google's first page showed for **“{query}”** in the search result we "
        f"saved on {fetched}. Each block on that page is something Google chose to show for "
        "this search: the table counts them, the next tables show who "
        "ranks and what searchers ask, and the last list turns those counts into what our "
        "page has to do. The 'What it rewards' column is general guidance on what each kind "
        "of result tends to favour, not data from this search.",
        "",
        TD.md_table(["On page one", "Count", "What it rewards"],
               [[e["signal"].replace("_", " "), _count_cell(e, r), e["rewards"]]
                for e in r["expect"]]),
        "",
        "#### Who ranks, and with what kind of page",
        "",
    ]
    if r["ranking"]:
        lines.append(TD.md_table(["Pos", "Domain", "Page type"],
                            [[x["pos"], x["domain"], f"{x['type']} ({x['basis']})"]
                             for x in r["ranking"]]))
    else:
        lines.append("No organic results in the saved response.")
    lines += ["", "#### What the AI Overview cites", ""]
    if r["aio_cites"]:
        lines.append(TD.md_table(["Cited domain"], [[d] for d in r["aio_cites"]]))
    else:
        lines.append(r["aio_note"])
    lines += ["", "#### People Also Ask → the section that answers it", ""]
    if r["paa"]:
        lines.append(TD.md_table(["Question", "Answered by"], [
            [p["q"], f"`{p['answered_by']}` — {heads.get(p['answered_by'], '')}"
             if p["answered_by"] else "**none — gap**"] for p in r["paa"]]))
    else:
        lines.append("No People Also Ask box on page one.")
    lines += ["", "#### What this means for our page", ""]
    lines += [f"- {b}" for b in takeaways(r, sections)]
    return "\n".join(lines)


def block(board, root=ROOT):
    bare = KM._bare(board.get("meta", {}).get("slug", ""))
    d = pathlib.Path(root) / "data/queries/raw" / bare
    raw, proc = d / "serp_google.response.json", d / "serp_google.json"
    if not (raw.is_file() and proc.is_file()):
        return f"NOT FETCHED — no data/queries/raw/{bare}/serp_google*.json"
    serp = _load(proc)
    if serp.get("status", "ok") != "ok":
        msg = f"NOT FETCHED — data/queries/raw/{bare}/serp_google.json status {serp.get('status')}"
        note = (serp.get("note") or "").strip()
        return f"{msg}: {note}" if note else msg
    comp_p = d / "competitors.json"
    comp = _load(comp_p) if comp_p.is_file() else None
    sections = board.get("sections") or []
    r = read(_load(raw), serp, sections, competitors=comp)
    return render(r, _query(board), serp.get("fetched") or "an unrecorded date", sections)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    usage = "usage: python3 scripts/serp_reading.py <slug>"
    if len(argv) != 1:
        print(usage, file=sys.stderr)
        return 2
    path = ROOT / "data/boards" / f"{KM._bare(argv[0])}.json"
    if not path.is_file():
        print(f"{usage} — no board at {path.relative_to(ROOT)}", file=sys.stderr)
        return 2
    print(block(_load(path)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
