#!/usr/bin/env python3
"""Query augmentation: merge, score and assign the questions a BSUK page must answer.

The bsuk-query-augmentation skill fetches (the DataForSEO connector, the research-recency
ladder) and writes NORMALISED candidate files under data/queries/raw/<slug>/. This script
never calls a paid service. It turns those files plus the offline bank (data/faq.json) into
data/queries/<slug>.json — the file the page builder writes from and
scripts/query_coverage_check.py gates.

  query_augment.py --preflight SLUG --source SOURCE [--refresh]
      exit 0 proceed · 3 cached, make no call · 4 a budget would be exceeded
  query_augment.py --record SLUG --source SOURCE --endpoint NAME --cost USD
  query_augment.py SLUG --page-type TYPE --keyword "..." --route /path/
      exit 0 written · 5 too few fact-backed questions to fill the FAQ blocks
      · 6 an input file is unparseable or the wrong shape (nothing written)
  Every mode: exit 2 for bad usage (a slug outside [a-z0-9-], a route not ending /SLUG/).

Spec: docs/superpowers/specs/2026-09-23-query-augmentation-design.md §3–§9.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

PAID_SOURCES = ("serp_google", "serp_bing", "ai_engines")
CANDIDATE_SOURCES = PAID_SOURCES + ("threads",)
PAGE_TYPES = ("location", "comparison", "blog", "puppy")
EXIT_OK, EXIT_USAGE, EXIT_CACHED, EXIT_BUDGET, EXIT_SHORT, EXIT_BAD_INPUT = 0, 2, 3, 4, 5, 6
DEFAULT_TYPICAL_CALL_USD = 0.05

BLOCKS = ("top", "middle", "bottom")
FAQ_MIN = {"top": 5, "middle": 5, "bottom": 7}
FAQ_MAX = {"top": 7, "middle": 7, "bottom": 10}
FAQ_TOTAL_MAX = 20
EXTRA_SECTIONS = 3
OUTLIER_RATIO = 1.5

# One spelling per thing, so "Staffie pups" and "staffy puppies" merge.
SYNONYMS = (
    (r"\bstaffordshire bull terriers?\b", "staffy"),
    (r"\bstaff(?:y|ie|ies|ys)\b", "staffy"),
    (r"\bpupp(?:ies|ys)\b", "puppy"),
    (r"\bpups?\b", "puppy"),
)

# Questions that are about the site, not the dog: never a page topic. Checked first.
SKIP = (r"\b(personal information|privacy|cookies?|gdpr|thank you page|reply|enquiry|enquiries"
        r"|(my|your|personal) data|data (protection|deleted|we hold)|what data)\b")

# First match wins, so order is precedence: a price question that mentions a blue coat is
# a price question. Patterns run on normalise()d text (which strips the pound sign).
TOPICS = (
    ("price", "top",
     r"\b(costs?|prices?|priced|deposit|pay|payment|paying|expensive|cheap\w*|afford\w*)\b"
     r"|\bhow much\b(?!.*\b(exercise|food|feed|eat|weigh\w*|sleep\w*|walk\w*)\b)"),
    ("delivery", "top",
     r"\b(deliver\w*|collect\w*|transport\w*|travel\w*|near me|distance|ship\w*|postage|post (a |the )?pupp\w*|courier)\b"),
    ("reserve", "top", r"\b(reserv\w*|waiting (list|time)|how long (do|will|would) i (need to |have to )?wait|is there a wait|book\w*|available|availability"
     r"|where (can|do|should) i (find|buy|get|start)|where should i start)\b"),
    ("age", "middle",
     r"\b(weeks old|how old|leave\w* (its|their|the) mother"
     r"|when (can|will|does) (my |the |a )?puppy (leave|go home|come home))\b"),
    ("paperwork", "middle",
     r"\b(paperwork|papers|microchip\w*|vaccin\w*|pedigree|regist\w*|kennel club|contract|included|comes? with"
     r"|before (it|they) comes? home)\b"),
    ("health", "middle",
     r"\b(health\w*|tests?|tested|testing|vets?|l2hga|l 2 hga|hereditary|cataract\w*|guarantee\w*"
     r"|prone to|scratch\w*)\b"),
    ("trust", "middle", r"\b(puppy farm\w*|ethical\w*|reputable|what (should|to) (i )?ask|support after)\b"),
    ("visit", "middle",
     r"\b(visit\w*|meet (the )?(mother|father|parents|mum|dad)|see (the )?(mother|father|parents|mum|dad|litter))\b"),
    ("home", "bottom", r"\b(flat|flats|apartment\w*|garden\w*|house|left alone|home alone)\b"),
    ("family", "bottom", r"\b(child\w*|kids?|family|families|cats?|other dogs|other pets)\b"),
    ("training", "bottom", r"\b(train\w*|potty|crate\w*)\b"),
    ("lifespan", "bottom",
     r"\bhow long (do|does|will|can) .*\blive\b|\blive (for|to)\b|\blifespan\b|\blife expectancy\b"),
    ("coat", "bottom", r"\b(coat\w*|colou?rs?|shed\w*|groom\w*)\b"),
    ("temperament", "bottom",
     r"\b(temperament|aggressive|dangerous|banned|friendly|energy|exercise|first time (dog )?owners?"
     r"|downsides?|male or female|attached)\b"),
    ("breed", "bottom", r"\b(pit ?bulls?|amstaff\w*|american|english staffy|two breeds|what breeds?)\b"),
    ("care", "bottom", r"\b(feed\w*|diet|food|sleep\w*)\b"),
)

# Page-type fit: how much a topic matters on this kind of page. Unlisted topics weigh 1.
FIT = {
    "location": {"delivery": 3, "price": 2, "reserve": 2, "visit": 2},
    "comparison": {"temperament": 2, "coat": 2, "health": 2, "breed": 2},
    "puppy": {"price": 3, "reserve": 3, "paperwork": 2},
    "blog": {},
}


def normalise(text):
    t = (text or "").lower().replace("’", "").replace("'", "")
    for pat, rep in SYNONYMS:
        t = re.sub(pat, rep, t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def topic_of(text):
    n = normalise(text)
    if re.search(SKIP, n):
        return None, None
    for topic, block, pat in TOPICS:
        if re.search(pat, n):
            return topic, block
    return None, None


def fact_exists(ref, root=ROOT):
    """True when `ref` ("path" or "path#dotted.key") names a real, non-null fact."""
    if not ref:
        return False
    path, _, key = ref.partition("#")
    pp = PurePosixPath(path)
    if pp.is_absolute() or ".." in pp.parts:
        return False
    p = Path(root) / path
    if not p.is_file():
        return False
    if not key:
        return True
    try:
        node = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return False
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return False
    return node is not None


class Short(Exception):
    """A FAQ block cannot reach its minimum from fact-backed questions."""

    def __init__(self, blocks):
        super().__init__(", ".join(f"{b}: {have}/{need}" for b, (have, need) in blocks.items()))
        self.blocks = blocks
        self.blocked = []   # (block, question) pairs, set by build()


def _bank_sources(root):
    """{faq.json row id: its source} under `root`; empty when the bank is missing or bad."""
    try:
        rows = json.loads((Path(root) / "data/faq.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    if not isinstance(rows, list):
        return {}
    return {r["id"]: r.get("source") for r in rows if isinstance(r, dict) and "id" in r}


def resolve_fact(fact, src, root=ROOT, bank=None):
    """The fact_source a candidate may contribute, or None.

    A bank candidate may cite a bare path (page copy backs it). Any other source must cite
    "path#key" or "bank:<id>" (resolved to that faq.json row's source); a bare path is ignored.
    """
    if not fact:
        return None
    if src != "bank":
        if fact.startswith("bank:"):
            fact = (bank if bank is not None else _bank_sources(root)).get(fact[5:])
        elif "#" not in fact:
            return None
    return fact if fact_exists(fact, root) else None


def merge(cands, root=ROOT):
    """cands: (text, source_type, detail, fact_source). Keyed by normalised text."""
    merged, bank = {}, None
    for text, src, detail, fact in cands:
        n = normalise(text)
        if not n:
            continue
        m = merged.setdefault(n, {"question": text.strip(), "types": set(),
                                  "found_in": [], "fact_source": None})
        m["types"].add(src)
        if detail not in m["found_in"]:
            m["found_in"].append(detail)
        if m["fact_source"] is None and fact:
            if bank is None and src != "bank" and fact.startswith("bank:"):
                bank = _bank_sources(root)
            m["fact_source"] = resolve_fact(fact, src, root, bank)
    return merged


def score(types, topic, page_type):
    return len(types) + FIT.get(page_type, {}).get(topic, 1)


# Headings that are page furniture, not content. Reviews and FAQ headings are removed too:
# ours are fixed frame and never counted, so theirs are not counted either.
NON_CONTENT_EXACT = re.compile(
    r"(share|share this|follow us|subscribe|newsletter|sign up|contact us|get in touch|"
    r"comments?|categories|tags|archives|search|menu|footer|sidebar|you may also like|"
    r"call now|call us now|enquire now|book now|apply now|reviews?|testimonials?)")
NON_CONTENT_PREFIX = re.compile(
    r"(related|recent|popular|latest) (posts|articles|puppy)\b|leave a (reply|comment)\b|"
    r"faqs?\b|frequently asked questions\b")
# Furniture wrapped in a few words ("Google Reviews", "Follow Us On Instagram"): at most two
# words before the phrase and three after, so a long content heading is never caught. A
# heading that names a page topic ("When to Contact a Vet") is content and is kept.
NON_CONTENT_AROUND = re.compile(
    r"^(\w+ ){0,2}(reviews?|testimonials?|what (our )?(customers|owners|families) say|contact( us)?"
    r"|get in touch|call us|enquire|follow us|share( this)?|sign up|newsletter"
    r"|(latest|recent) (news|posts)|(useful|quick) links)( \w+){0,3}$")


def clean_h2s(h2s):
    seen, out = set(), []
    for h in h2s:
        n = normalise(h)
        if (not n or n in seen or NON_CONTENT_EXACT.fullmatch(n) or NON_CONTENT_PREFIX.match(n)
                or (NON_CONTENT_AROUND.search(n) and topic_of(h)[0] is None)):
            continue
        seen.add(n)
        out.append(h)
    return out


MIN_USABLE_H2 = 3


def section_target(pages):
    """(target, rows): match the highest cleaned H2 count unless it is an outlier.

    Only usable pages (at least MIN_USABLE_H2 clean headings) set the number or count as the
    outlier's comparison; every page is still reported in rows. Ties on the top count go to
    the better Google position, then Bing, then URL.
    """
    rows = [{"url": p["url"], "google_pos": p.get("google_pos"), "bing_pos": p.get("bing_pos"),
             "h2_raw": len(p.get("h2", [])), "h2_clean": len(clean_h2s(p.get("h2", []))),
             "outlier": False} for p in pages]
    usable = [r for r in rows if r["h2_clean"] >= MIN_USABLE_H2]
    if not usable:
        return {"matched": 0, "set_by": None, "extra": EXTRA_SECTIONS, "total": EXTRA_SECTIONS}, rows
    ranked = sorted(usable, key=lambda r: (-r["h2_clean"], r["google_pos"] or 99,
                                           r["bing_pos"] or 99, r["url"]))
    setter = ranked[0]
    if len(ranked) > 1 and ranked[0]["h2_clean"] > OUTLIER_RATIO * ranked[1]["h2_clean"]:
        ranked[0]["outlier"] = True
        setter = ranked[1]
    matched = setter["h2_clean"]
    return {"matched": matched, "set_by": setter["url"], "extra": EXTRA_SECTIONS,
            "total": matched + EXTRA_SECTIONS}, rows


def covered_topics(pages):
    return {topic_of(h)[0] for p in pages for h in clean_h2s(p.get("h2", []))} - {None}


def _rank(q):
    return (-q["score"], q["id"])


def pick_faq(questions):
    """Sets q["faq"] in place: block minimums first, then by score up to FAQ_TOTAL_MAX."""
    by_block = {b: sorted((q for q in questions if q["fact_source"] and q["block"] == b), key=_rank)
                for b in BLOCKS}
    short = {b: (len(by_block[b]), FAQ_MIN[b]) for b in BLOCKS if len(by_block[b]) < FAQ_MIN[b]}
    if short:
        raise Short(short)
    picked = {b: by_block[b][:FAQ_MIN[b]] for b in BLOCKS}
    total = sum(len(v) for v in picked.values())
    for q in sorted((q for b in BLOCKS for q in by_block[b][FAQ_MIN[b]:]), key=_rank):
        if total >= FAQ_TOTAL_MAX:
            break
        if len(picked[q["block"]]) < FAQ_MAX[q["block"]]:
            picked[q["block"]].append(q)
            total += 1
    for b in BLOCKS:
        for q in picked[b]:
            q["faq"] = b


def pick_extra(questions, covered):
    """The strongest fact-backed topics the FAQ left questions for, uncovered ones first.

    A topic weighs the scores of its fact-backed questions not picked for the FAQ; a topic
    with none left sorts after every topic that has some. heading is filled by the builder.
    """
    weight, left = {}, {}
    for q in questions:
        if q["fact_source"] and q["topic"]:
            weight.setdefault(q["topic"], 0)
            left.setdefault(q["topic"], 0)
            if not q["faq"]:
                weight[q["topic"]] += q["score"]
                left[q["topic"]] += 1
    order = sorted(weight, key=lambda t: (not left[t], t in covered, -weight[t], t))
    extras = []
    for t in order[:EXTRA_SECTIONS]:
        ids = [q["id"] for q in sorted(questions, key=_rank)
               if q["topic"] == t and q["fact_source"] and not q["faq"]][:3]
        extras.append({"topic": t, "uncovered": t not in covered, "question_ids": ids,
                       "heading": None})
    return extras


def _read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def _write_json(path, data):
    """Write through a temp file in the same directory, then swap it in atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def load_settings(root=ROOT):
    return _read_json(Path(root) / "data/settings.json", {})


def load_spend(root=ROOT):
    return _read_json(Path(root) / "data/queries/spend.json", [])


def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def record(slug, source, endpoint, cost, root=ROOT, now=None):
    """Append one paid call. Refuses a bad cost; never overwrites a spend log it cannot read."""
    cost = float(cost)
    if not math.isfinite(cost) or cost < 0:
        raise ValueError(f"cost must be a finite amount of 0 or more, got {cost!r}")
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log = load_spend(root)   # a damaged log raises here, so it is left as it is
    if not isinstance(log, list):
        raise ValueError("data/queries/spend.json is not a list")
    log.append({"ts": now, "slug": slug, "source": source, "endpoint": endpoint,
                "cost_usd": cost})
    _write_json(Path(root) / "data/queries/spend.json", log)


def spend_for(slug, root=ROOT, day=None):
    return round(sum(e["cost_usd"] for e in load_spend(root)
                     if e["slug"] == slug and (day is None or e["ts"].startswith(day))), 6)


def _is_cached(slug, source, root):
    d = Path(root) / "data/queries/raw" / slug
    # a saved connector response means the call was already bought
    return (d / f"{source}.json").is_file() or (d / f"{source}.response.json").is_file()


def _budget_check(slug, source, root, today):
    s = load_settings(root)
    page_cap, total_cap = s.get("query_budget_usd"), s.get("query_total_budget_usd")
    if not (_finite(page_cap) and _finite(total_cap)):
        return EXIT_BUDGET, "query_budget_usd / query_total_budget_usd missing or not a number"
    log = load_spend(root)
    if not isinstance(log, list):
        raise TypeError("data/queries/spend.json is not a list")
    configured = s.get("query_typical_call_usd") or DEFAULT_TYPICAL_CALL_USD
    seen = [e["cost_usd"] for e in log if e["source"] == source]
    typical = max(seen + [configured])
    total = round(sum(e["cost_usd"] for e in log), 6)
    page = spend_for(slug, root, day=today)
    if not all(_finite(x) for x in (typical, total, page)):
        return EXIT_BUDGET, "a cost in the spend log or settings is not a finite number"
    if round(page + typical, 6) > page_cap or round(total + typical, 6) > total_cap:
        return EXIT_BUDGET, (f"budget: page {page} + {typical} vs {page_cap}, "
                             f"total {total} + {typical} vs {total_cap}")
    return EXIT_OK, None


def preflight(slug, source, root=ROOT, refresh=False, today=None):
    """0 proceed · 3 cached · 4 a budget would be exceeded, or the budget can't be read.

    `today` is the UTC date (YYYY-MM-DD) whose spend counts as this page's run.
    """
    today = today or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(today)):
        raise ValueError(f"today must be a YYYY-MM-DD UTC date, got {today!r}")
    if _is_cached(slug, source, root) and not refresh:
        return EXIT_CACHED
    if source not in PAID_SOURCES:
        return EXIT_OK
    try:
        code, reason = _budget_check(slug, source, root, today)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        code, reason = EXIT_BUDGET, f"cannot read settings or spend log: {exc}"
    if reason:
        print(f"preflight {slug}/{source}: {reason}", file=sys.stderr)
    return code


class BadInput(Exception):
    """An input file the script reads is unparseable or the wrong shape. Nothing is written."""

    def __init__(self, path, reason):
        super().__init__(f"{path}: {reason}")


STATUSES = ("ok", "fallback", "NOT FETCHED")
SLUG_RE = re.compile(r"[a-z0-9-]+")
ROUTE_RE = re.compile(r"/([a-z0-9-]+/)*")
SCHEMA_PATH = ROOT / "schemas/queries.schema.json"


def _load(path, default):
    """_read_json, with a parse failure turned into BadInput naming the file."""
    try:
        return _read_json(path, default)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise BadInput(path, f"cannot parse ({exc})") from exc


def _opt_str(x):
    return x is None or isinstance(x, str)


def _opt_int(x):
    return x is None or (isinstance(x, int) and not isinstance(x, bool))


def _status(d, path):
    st = d.get("status", "ok")
    if st not in STATUSES:
        raise BadInput(path, f"status must be one of {', '.join(STATUSES)}, got {st!r}")
    return st


def load_candidates(slug, root=ROOT):
    raw = Path(root) / "data/queries/raw" / slug
    cands, status = [], {}
    for src in CANDIDATE_SOURCES:
        path = raw / f"{src}.json"
        d = _load(path, None)
        if d is None:
            status[src] = "NOT FETCHED"
            continue
        if not isinstance(d, dict):
            raise BadInput(path, "top level must be an object")
        status[src] = _status(d, path)
        items = d.get("questions", [])
        if not isinstance(items, list):
            raise BadInput(path, "questions must be a list")
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise BadInput(path, f"questions[{i}] must be an object")
            text = item.get("text")
            if not isinstance(text, str) or not text.strip():
                raise BadInput(path, f"questions[{i}].text must be a non-empty string")
            for k in ("detail", "fact_source"):
                if not _opt_str(item.get(k)):
                    raise BadInput(path, f"questions[{i}].{k} must be a string or null")
            cands.append((text, src, item.get("detail") or src, item.get("fact_source")))
    return cands, status


def bank_candidates(root=ROOT):
    """(candidates, status). A missing bank is "NOT FETCHED"; a malformed one is BadInput."""
    path = Path(root) / "data/faq.json"
    rows = _load(path, None)
    if rows is None:
        return [], "NOT FETCHED"
    if not isinstance(rows, list):
        raise BadInput(path, "top level must be a list")
    out = []
    for i, r in enumerate(rows):
        if not (isinstance(r, dict) and isinstance(r.get("q"), str)
                and isinstance(r.get("id"), str)):
            raise BadInput(path, f"row {i} must be an object with string q and id")
        if not _opt_str(r.get("source")):
            raise BadInput(path, f"row {i}: source must be a string or null")
        out.append((r["q"], "bank", f"bank:{r['id']}", r.get("source")))
    return out, "ok"


def load_competitors(slug, root=ROOT):
    path = Path(root) / "data/queries/raw" / slug / "competitors.json"
    d = _load(path, None)
    if d is None:
        return {"status": "NOT FETCHED", "pages": []}
    if not isinstance(d, dict):
        raise BadInput(path, "top level must be an object")
    _status(d, path)
    pages = d.get("pages")
    if not isinstance(pages, list):
        raise BadInput(path, "pages must be a list")
    for i, p in enumerate(pages):
        if not isinstance(p, dict) or not isinstance(p.get("url"), str):
            raise BadInput(path, f"pages[{i}] must be an object with a string url")
        for k in ("google_pos", "bing_pos"):
            if not _opt_int(p.get(k)):
                raise BadInput(path, f"pages[{i}].{k} must be an integer or null")
        h2 = p.get("h2", [])
        if not (isinstance(h2, list) and all(isinstance(h, str) for h in h2)):
            raise BadInput(path, f"pages[{i}].h2 must be a list of strings")
    return d


def load_previous(slug, root=ROOT):
    """The page's existing question file, or None. The builder's fills are carried from it."""
    path = Path(root) / "data/queries" / f"{slug}.json"
    d = _load(path, None)
    if d is None:
        return None
    if not (isinstance(d, dict) and isinstance(d.get("questions", []), list)
            and isinstance(d.get("extra_sections", []), list)
            and all(isinstance(q, dict) and isinstance(q.get("question"), str)
                    for q in d.get("questions", []))
            and all(isinstance(e, dict) and isinstance(e.get("topic"), str)
                    for e in d.get("extra_sections", []))):
        raise BadInput(path, "not a question file (questions / extra_sections malformed)")
    return d


def _question_id(norm):
    """A pure function of the normalised text, so an id never moves to another question."""
    base = ("q-" + "-".join(norm.split()[:8]))[:43].rstrip("-")
    return f"{base}-{hashlib.sha1(norm.encode()).hexdigest()[:6]}"


def _utc_today():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def _carry_fills(prev, questions, extras):
    """Copy covered_by (matched by normalised question text) and headings (by topic).

    Returns (kept, dropped): fills that found a home in this build, and fills that did not.
    """
    if not prev:
        return 0, 0
    covered = {normalise(q["question"]): q.get("covered_by") for q in prev.get("questions", [])
               if q.get("covered_by")}
    heads = {e["topic"]: e.get("heading") for e in prev.get("extra_sections", [])
             if e.get("heading")}
    kept = 0
    for q in questions:
        n = normalise(q["question"])
        if n in covered:
            q["covered_by"] = covered[n]
            kept += 1
    for e in extras:
        if e["topic"] in heads:
            e["heading"] = heads[e["topic"]]
            kept += 1
    return kept, len(covered) + len(heads) - kept


def build(slug, page_type, keyword, route, root=ROOT, today=None, prev=None):
    """The question file as a dict, with "_fills": (kept, dropped) for the caller to pop.

    Raises Short (with .blocked = [(block, question)]) when a FAQ block cannot be filled, and
    BadInput when an input file is unparseable or the wrong shape.
    """
    today = today or _utc_today()
    cands, status = load_candidates(slug, root)
    bank, status["bank"] = bank_candidates(root)
    cands += bank   # buyer phrasing first, so it wins the merge
    merged = merge(cands, root)
    questions = []
    for n in sorted(merged):
        m = merged[n]
        topic, block = topic_of(m["question"])
        questions.append({
            "id": _question_id(n), "question": m["question"], "found_in": m["found_in"],
            "score": score(m["types"], topic, page_type), "topic": topic, "block": block,
            "fact_source": m["fact_source"], "must_answer": False, "faq": None,
            "blocked": None if m["fact_source"] else "unverified fact", "covered_by": None})
    assert len({q["id"] for q in questions}) == len(questions), "question id collision"
    comp = load_competitors(slug, root)
    status["competitors"] = comp.get("status", "ok")
    target, rows = section_target(comp["pages"])
    if prev is None:
        prev = load_previous(slug, root)
    try:
        pick_faq(questions)
    except Short as e:
        e.blocked = [(q["block"], q["question"]) for q in questions
                     if q["block"] in e.blocks and not q["fact_source"]]
        raise
    extras = pick_extra(questions, covered_topics(comp["pages"]))
    extra_ids = {i for e in extras for i in e["question_ids"]}
    for q in questions:
        q["must_answer"] = bool(q["faq"]) or q["id"] in extra_ids
    fills = _carry_fills(prev, questions, extras)
    return {"slug": slug, "page_type": page_type, "primary_keyword": keyword, "route": route,
            "fetched": today, "spend_usd": spend_for(slug, root), "sources": status,
            "competitors": rows, "section_target": target, "extra_sections": extras,
            "questions": questions, "_fills": fills}


def check_schema(data):
    """A built dict that breaks schemas/queries.schema.json is a bug in this script: raise."""
    import jsonschema   # only build needs it, so preflight/record work without it
    jsonschema.validate(data, json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--preflight", metavar="SLUG")
    ap.add_argument("--record", metavar="SLUG")
    ap.add_argument("--source")
    ap.add_argument("--endpoint")
    ap.add_argument("--cost", type=float)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--page-type")
    ap.add_argument("--keyword")
    ap.add_argument("--route")
    ap.add_argument("--today")
    a = ap.parse_args(argv)
    root = Path(a.root)
    modes = [m for m in (a.preflight, a.record, a.slug) if m is not None]
    if len(modes) != 1:
        ap.error("give exactly one of --preflight SLUG, --record SLUG or a build SLUG")
    slug = modes[0]
    if not SLUG_RE.fullmatch(slug):
        ap.error(f"slug must match ^[a-z0-9-]+$, got {slug!r}")
    if a.today is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.today):
        ap.error(f"--today must be a YYYY-MM-DD UTC date, got {a.today!r}")
    if a.preflight:
        if a.source not in CANDIDATE_SOURCES:
            ap.error("--source must be one of " + ", ".join(CANDIDATE_SOURCES))
        code = preflight(slug, a.source, root, a.refresh, a.today)
        print({EXIT_OK: "proceed", EXIT_CACHED: "cached — make no call",
               EXIT_BUDGET: "budget would be exceeded — stop and report"}[code])
        return code
    if a.record:
        if a.source not in PAID_SOURCES or not a.endpoint or a.cost is None:
            ap.error("--record needs a paid --source, --endpoint and --cost")
        try:
            record(slug, a.source, a.endpoint, a.cost, root)
        except ValueError as e:   # a bad cost or an unreadable spend log; nothing written
            print(f"query_augment.py: --record refused: {e}", file=sys.stderr)
            return EXIT_USAGE
        print(f"recorded {a.cost} for {slug}; page total {spend_for(slug, root)}")
        return EXIT_OK
    if a.page_type not in PAGE_TYPES or not a.keyword or not a.route:
        ap.error("build needs SLUG, --page-type (" + "/".join(PAGE_TYPES) + "), --keyword, --route")
    if not ROUTE_RE.fullmatch(a.route) or a.route.rstrip("/").rsplit("/", 1)[-1] != slug:
        ap.error(f"--route must match ^/([a-z0-9-]+/)*$ and end in /{slug}/, got {a.route!r}")
    out = root / "data/queries" / f"{slug}.json"
    try:
        data = build(slug, a.page_type, a.keyword, a.route, root, a.today)
    except BadInput as e:
        print(f"query_augment.py: bad input: {e}", file=sys.stderr)
        return EXIT_BAD_INPUT
    except Short as e:
        kept = f"; existing data/queries/{slug}.json left unchanged" if out.exists() else ""
        print(f"SHORT: too few fact-backed questions — {e}{kept}")
        for block, question in e.blocked:
            print(f"  blocked ({block}): {question}")
        return EXIT_SHORT
    kept, dropped = data.pop("_fills", (0, 0))
    check_schema(data)
    _write_json(out, data)
    faq = sum(1 for q in data["questions"] if q["faq"])
    print(f"wrote data/queries/{slug}.json — {len(data['questions'])} questions, {faq} FAQ, "
          f"section target {data['section_target']['total']}; "
          f"kept {kept} fills, dropped {dropped}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
