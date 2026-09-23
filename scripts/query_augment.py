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

Spec: docs/superpowers/specs/2026-09-23-query-augmentation-design.md §3–§9.
"""
import argparse
import datetime
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
EXIT_OK, EXIT_USAGE, EXIT_CACHED, EXIT_BUDGET, EXIT_SHORT = 0, 2, 3, 4, 5
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
