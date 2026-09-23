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
  query_augment.py --extract-h2 FILE.html
      prints {"h2": [content H2s], "h2_all": N, "blocked": bool} (advert cards and
      navigation dropped; blocked = a bot challenge page) — how a competitors.json page's
      h2, h2_all and blocked are filled from a saved page, never by hand
      exit 0 printed (a blocked page also warns on stderr) · 6 the file is missing or unreadable
  query_augment.py SLUG --page-type TYPE --keyword "..." --route /path/
      exit 0 written · 5 too few fact-backed questions to fill the FAQ blocks
      · 6 an input file is unparseable or the wrong shape (nothing written)
  Every mode: exit 1 internal error (a bug; nothing written) · 2 bad usage (a slug outside
  [a-z0-9-], a route not ending /SLUG/, more than one mode).

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
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

PAID_SOURCES = ("serp_google", "serp_bing", "ai_engines")
CANDIDATE_SOURCES = PAID_SOURCES + ("threads",)
PAGE_TYPES = ("location", "comparison", "blog", "puppy")
EXIT_OK, EXIT_INTERNAL, EXIT_USAGE, EXIT_CACHED, EXIT_BUDGET, EXIT_SHORT, EXIT_BAD_INPUT = (
    0, 1, 2, 3, 4, 5, 6)
DEFAULT_TYPICAL_CALL_USD = 0.05

BLOCKS = ("top", "middle", "bottom")
FAQ_MIN = {"top": 5, "middle": 5, "bottom": 7}
FAQ_MAX = {"top": 7, "middle": 7, "bottom": 10}
FAQ_TOTAL_MAX = 20
FAQ_TOPIC_CAP = 2      # questions per topic per FAQ block, unless the block cannot fill
EXTRA_SECTIONS = 3
SECTION_FLOOR = 9      # a location page never has fewer body sections than this
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
    # Intent before delivery's collect/deliver words: aftercare is trust, treatments paperwork.
    ("trust", "middle", r"\b(support|advice|help)( \w+){0,2} after\b"),
    ("paperwork", "middle", r"\b(vaccin\w*|microchip\w*|worm\w*|flea)\b"),
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
     r"\b(visit\w*|meet (the )?(mother|father|parents|mum|dad)|see (the )?(mother|father|parents|mum|dad|litter)"
     r"|see (the )?puppy with (its|the) mother)\b"),
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


def _bank_rows(root):
    """{faq.json row id: (its question, its source)}; empty when the bank is missing or bad."""
    try:
        rows = json.loads((Path(root) / "data/faq.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    if not isinstance(rows, list):
        return {}
    return {r["id"]: (r.get("q") if isinstance(r.get("q"), str) else "", r.get("source"))
            for r in rows if isinstance(r, dict) and "id" in r}


def _bank_sources(root):
    """{faq.json row id: its source} under `root`; empty when the bank is missing or bad."""
    return {k: src for k, (_, src) in _bank_rows(root).items()}


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


def merge(cands, root=ROOT, keyword=""):
    """cands: (text, source_type, detail, fact_source). Keyed by normalised text.

    A non-bank candidate citing "bank:<id>" that resolves joins that bank row's entry (keyed
    on the row's normalised text). An entry's question is its first non-bank phrasing, so
    buyer wording wins over the bank's; types and found_in are the union. Once a bank-linked
    entry holds buyer wording, a further buyer question citing the same row joins only if it
    has the same topic and is a near-duplicate of that wording (_near_duplicate); otherwise
    it stays its own entry, still backed by the row's fact. Every entry linked to a bank row
    carries that row's text as bank_text, so entry_topic() can fall back to its topic.
    """
    merged, buyer, rows = {}, set(), None
    for text, src, detail, fact in cands:
        n = normalise(text)
        if not n:
            continue
        key, resolved, bank_text = n, None, text.strip() if src == "bank" else None
        if fact:
            if src != "bank" and fact.startswith("bank:"):
                if rows is None:
                    rows = _bank_rows(root)
                resolved = resolve_fact(fact, src, root, {k: v[1] for k, v in rows.items()})
                row_text = rows[fact[5:]][0] if resolved else ""
                if normalise(row_text):
                    bank_text, key = row_text, normalise(row_text)
                    if key in buyer and not _joins(merged[key], text, bank_text, keyword):
                        key = n
            else:
                resolved = resolve_fact(fact, src, root)
        m = merged.setdefault(key, {"question": text.strip(), "types": set(),
                                    "found_in": [], "fact_source": None, "bank_text": None})
        if m["bank_text"] is None and bank_text:
            m["bank_text"] = bank_text
        if src != "bank" and key not in buyer:
            buyer.add(key)
            m["question"] = text.strip()
        m["types"].add(src)
        if detail not in m["found_in"]:
            m["found_in"].append(detail)
        if m["fact_source"] is None and resolved:
            m["fact_source"] = resolved
    return merged


def entry_topic(m):
    """(topic, block) of a merged entry: its question's, else its linked bank row's."""
    topic = topic_of(m["question"])
    if topic[0] is None and m.get("bank_text"):
        return topic_of(m["bank_text"])
    return topic


def _joins(m, text, bank_text, keyword):
    """A second buyer question on a bank row joins that row's entry only as a near-duplicate."""
    mine = entry_topic({"question": text, "bank_text": bank_text})[0]
    return mine is not None and mine == entry_topic(m)[0] and _near_duplicate(
        content_words(m["question"], keyword), content_words(text, keyword))


# Near-duplicate collapse: content words are normalised tokens minus these stop words and the
# page's primary-keyword tokens (so the city never counts as overlap), through a tiny stem map
# ("delivery"/"deliver", "tested"/"test"), then a trailing "s" is stripped from words longer
# than three letters (not "ss": "across", "less").
STOP_WORDS = frozenset(
    "a an the is are do does can i you your we our my of to for in on with and or it its be "
    "how what when where which who why will would should there this that these those any have "
    "has had get got from at by as than then so if puppy puppies staffy staffies blue uk dog "
    "dogs much more better near been was both now sale".split())
STEMS = {"delivery": "deliver", "delivered": "deliver", "delivering": "deliver",
         "delivers": "deliver", "tested": "test", "testing": "test", "tests": "test",
         "owners": "owner", "owner": "owner", "trained": "train", "training": "train",
         "trains": "train", "vaccinated": "vaccin", "vaccinations": "vaccin",
         "vaccination": "vaccin"}
DUPLICATE_JACCARD = 0.5
DUPLICATE_SHARED = 2     # and at least this many content words in common


def content_words(text, keyword=""):
    skip = STOP_WORDS | set(normalise(keyword).split())
    out = set()
    for t in normalise(text).split():
        if t in skip:
            continue
        t = STEMS.get(t, t)
        if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.add(t)
    return out


def _near_duplicate(a, b):
    return len(a & b) >= DUPLICATE_SHARED and _jaccard(a, b) >= DUPLICATE_JACCARD


def _jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def collapse_near_duplicates(merged, keyword=""):
    """Fold entries of the same topic that are near-duplicates: content words (with the
    page's keyword stripped) overlapping at Jaccard >= 0.5 and sharing at least two words.

    Linked pairs join one group (transitively, so the result never depends on input order).
    Each group is led by its first entry in the order: fact-backed first, then more source
    types, then longer found_in, then normalised text. The lead's phrasing and fact are the
    group's, so a lead's visible question is always answerable by its own fact: an unbacked
    phrasing leads only a group with no fact-backed member, and that group stays unbacked.
    types and found_in are unioned in that order. Untopicked entries never collapse.
    """
    order = sorted(merged, key=lambda k: (merged[k]["fact_source"] is None,
                                          -len(merged[k]["types"]),
                                          -len(merged[k]["found_in"]), k))
    info = {k: (entry_topic(merged[k])[0], content_words(merged[k]["question"], keyword))
            for k in order}
    root = {k: k for k in order}

    def find(k):
        while root[k] != k:
            root[k] = root[root[k]]
            k = root[k]
        return k

    for i, a in enumerate(order):
        ta, wa = info[a]
        if ta is None:
            continue
        for b in order[i + 1:]:
            tb, wb = info[b]
            if tb == ta and _near_duplicate(wa, wb):
                ra, rb = find(a), find(b)
                if ra != rb:   # the earlier key in `order` stays the group's head
                    hi, lo = sorted((ra, rb), key=order.index)
                    root[lo] = hi
    out = {}
    for k in order:
        head = find(k)
        m = merged[k]
        if head not in out:
            out[head] = {"question": merged[head]["question"], "types": set(),
                         "found_in": [], "fact_source": merged[head]["fact_source"],
                         "bank_text": merged[head].get("bank_text")}
        g = out[head]
        g["types"] |= m["types"]
        g["found_in"] += [d for d in m["found_in"] if d not in g["found_in"]]
    return out


def score(types, topic, page_type):
    """2 per distinct non-bank source type, 1 if the bank has it, plus the page-type fit: a
    buyer question also in the bank outranks a bank-only row."""
    return (2 * len(set(types) - {"bank"}) + (1 if "bank" in types else 0)
            + FIT.get(page_type, {}).get(topic, 1))


# Headings that are page furniture, not content. Reviews and FAQ headings are removed too:
# ours are fixed frame and never counted, so theirs are not counted either.
NON_CONTENT_EXACT = re.compile(
    r"(share|share this|follow us|subscribe|newsletter|sign up|contact us|get in touch|"
    r"comments?|categories|tags|archives|search|menu|footer|sidebar|you may also like|"
    r"call now|call us now|enquire now|book now|apply now|reviews?|testimonials?|other pets)")
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
# Marketplace and directory furniture: search filters, result counts, grid headers.
# Anchored, so a content heading that merely contains the words is kept. A leading year
# ("2024 Litter: ... for sale in Salford") is a litter, not a result count.
NON_CONTENT_LISTING = re.compile(
    r"^refine your results$|^you might also like\b|^(latest )?featured ads\b"
    r"|^results from outside your search$|^recommended for you$|^nearest towns( and cities)?$"
    r"|\bjoin(ing)? our pack\b|^(\d+ )?puppy found$"
    r"|^(?!(19|20)\d\d )\d+ (\w+ ){0,4}for sale in\b")


def clean_h2s(h2s):
    seen, out = set(), []
    for h in h2s:
        n = normalise(h)
        if (not n or n in seen or NON_CONTENT_EXACT.fullmatch(n) or NON_CONTENT_PREFIX.match(n)
                or ((NON_CONTENT_AROUND.search(n) or NON_CONTENT_LISTING.search(n))
                    and topic_of(h)[0] is None)):
            continue
        seen.add(n)
        out.append(h)
    return out


MIN_USABLE_H2 = 3

# An H2 under one of these is an advert card or navigation, never a section. An <article> is
# a card only when it holds an H2, holds no H2-bearing article of its own, and the page has
# two or more such articles; an H2 is a card title only when its NEAREST article is a card.
# So a WordPress/Squarespace page-wrapper article keeps its H2s even when it holds a block of
# summary cards, and related-post articles titled in H3s never make a grid. An <li> is a card only when its list has three or more items that each hold an H2
# (a two-question accordion is content). A <header> is furniture only outside
# main/section/article (inside one it is a section's own heading).
CARD_ANCESTORS = {"a", "nav", "footer", "aside", "form", "button", "template"}
# Consent and cookie dialogs (vendor lists are full of H2s): an ancestor whose id or class
# names one, or any dialog. "cmp" counts only as its own segment ("qc-cmp2-container"), so a
# "cmpt-text" component is not caught.
CONSENT = re.compile(r"consent|cookie|onetrust|gdpr|didomi|qc-cmp|(^|[-_\s])cmp(\d|[-_\s]|$)",
                     re.I)
HEADER_HOSTS = {"main", "section", "article"}
MIN_CARD_ARTICLES = 2
MIN_CARD_ITEMS = 3
RAW_TAGS = {"script", "style", "template"}   # their text is never page text
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
             "source", "track", "wbr"}
# Inside a heading these separate words: "Blue<br>Staffy" reads "Blue Staffy".
BREAK_TAGS = {"br", "hr", "p", "div", "li", "ul", "ol", "dl", "dt", "dd", "section", "article",
              "header", "footer", "aside", "nav", "main", "figure", "figcaption", "blockquote",
              "pre", "table", "tr", "td", "th", "address", "fieldset", "h1", "h3", "h4", "h5",
              "h6"}
# A challenge page is named by its title or carries Cloudflare's own markers. Weaker signals
# (the "enable JavaScript" line, a small page with no <main> or <h1>) count only on a page
# with no H2 at all: a real page can say either.
CHALLENGE_TITLE = re.compile(r"^\s*(just a moment|attention required|access denied)", re.I)
CHALLENGE_MARKERS = ("_cf_chl_opt", "cf-browser-verification")
# Ordinary protected pages also load the challenge-platform script, so it is weak.
CHALLENGE_WEAK = re.compile(r"enable javascript and cookies|/cdn-cgi/challenge-platform/", re.I)
SMALL_PAGE_BYTES = 10 * 1024


class _H2s(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        # open elements: {"tag", "parent", "h2", "nested"}; parent is the entry below it;
        # nested marks an article that holds an H2-bearing article
        self.stack = []
        self.found = []   # (ancestor entries, text, has text outside links)
        self.h2_all = 0
        self.has_main_or_h1 = False
        self.title = None
        self._title = None
        self._h2 = None   # {"depth", "ancestors", "parts", "bare"}: bare = text outside links

    def _space(self):
        if self._h2 is not None:
            self._h2["parts"].append(" ")

    def handle_starttag(self, tag, attrs):
        if tag in BREAK_TAGS:
            self._space()
        if tag in VOID_TAGS:
            return
        if tag in ("main", "h1"):
            self.has_main_or_h1 = True
        if tag == "title" and self.title is None and self._title is None \
                and not any(e["tag"] == "svg" for e in self.stack):
            self._title = []
        if tag == "li":
            self._close_open_item()
        if tag == "h2":
            self.h2_all += 1
            self._close_h2()
            for e in self.stack:
                e["h2"] = True
            articles = [e for e in self.stack if e["tag"] == "article"]
            for e in articles[:-1]:
                e["nested"] = True
            self._h2 = {"depth": len(self.stack), "ancestors": list(self.stack),
                        "parts": [], "bare": []}
        a = dict(attrs)
        consent = (a.get("role") or "").lower() == "dialog" \
            or (a.get("aria-modal") or "").lower() == "true" \
            or bool(CONSENT.search(f"{a.get('id') or ''} {a.get('class') or ''}"))
        self.stack.append({"tag": tag, "parent": self.stack[-1] if self.stack else None,
                           "h2": False, "nested": False, "consent": consent})

    def _close_open_item(self):
        """A new <li> closes an open <li> of the same list, as a browser does."""
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] in ("ul", "ol", "menu"):
                return
            if self.stack[i]["tag"] == "li":
                del self.stack[i:]
                if self._h2 is not None and len(self.stack) <= self._h2["depth"]:
                    self._close_h2()
                return

    def handle_endtag(self, tag):
        if tag in BREAK_TAGS:
            self._space()
        if tag == "title" and self._title is not None:
            self.title, self._title = "".join(self._title), None
        tags = [e["tag"] for e in self.stack]
        if tag not in tags:
            return          # a stray end tag closes nothing
        del self.stack[len(tags) - 1 - tags[::-1].index(tag):]
        if self._h2 is not None and len(self.stack) <= self._h2["depth"]:
            self._close_h2()

    def handle_data(self, data):
        if self._title is not None:
            self._title.append(data)
            return
        if self._h2 is None or any(e["tag"] in RAW_TAGS for e in self.stack):
            return
        self._h2["parts"].append(data)
        if "a" not in [e["tag"] for e in self.stack[self._h2["depth"] + 1:]]:
            self._h2["bare"].append(data)

    def _close_h2(self):
        h, self._h2 = self._h2, None
        if h is not None:
            self.found.append((h["ancestors"], " ".join("".join(h["parts"]).split()),
                               bool("".join(h["bare"]).strip())))

    def close(self):
        super().close()
        self._close_h2()

    def content_h2s(self):
        seen = {id(e): e for anc, _, _ in self.found for e in anc}.values()
        leaves = [e for e in seen if e["tag"] == "article" and e["h2"] and not e["nested"]]
        card_articles = {id(e) for e in leaves} if len(leaves) >= MIN_CARD_ARTICLES else set()
        items = Counter(id(e["parent"]) for e in seen
                        if e["tag"] == "li" and e["h2"] and e["parent"] is not None)
        out = []
        for ancestors, text, bare in self.found:
            tags = [e["tag"] for e in ancestors]
            # A heading that is nothing but links is a card title, not a section.
            if not text or not bare or CARD_ANCESTORS & set(tags) \
                    or any(e["consent"] for e in ancestors):
                continue
            nearest = [e for e in ancestors if e["tag"] == "article"][-1:]
            if nearest and id(nearest[0]) in card_articles:
                continue
            if any(e["tag"] == "li" and e["parent"] is not None
                   and items[id(e["parent"])] >= MIN_CARD_ITEMS for e in ancestors):
                continue
            if any(t == "header" and not HEADER_HOSTS & set(tags[:i])
                   for i, t in enumerate(tags)):
                continue
            out.append(text)
        return out


def page_report(html):
    """{"h2": content H2s, "h2_all": every <h2> before filtering, "blocked": bool}.

    blocked: a bot challenge or interstitial — the <title> starts "Just a moment",
    "Attention Required" or "Access Denied", or the page carries a Cloudflare challenge
    marker (_cf_chl_opt, cf-browser-verification). On a page with no <h2> at all,
    "Enable JavaScript and cookies", the /cdn-cgi/challenge-platform/ script, or being under
    10 KB with neither <main> nor <h1>, also counts.
    """
    p = _H2s()
    p.feed(html)
    p.close()
    blocked = bool(CHALLENGE_TITLE.match(p.title or "")) \
        or any(m in html for m in CHALLENGE_MARKERS) \
        or (p.h2_all == 0 and (bool(CHALLENGE_WEAK.search(html)) or (
            not p.has_main_or_h1 and len(html.encode("utf-8")) < SMALL_PAGE_BYTES)))
    return {"h2": p.content_h2s(), "h2_all": p.h2_all, "blocked": blocked}


def extract_h2s(html):
    """The text of every content <h2> in `html`, in page order.

    Dropped: an H2 under a link, nav, footer, aside, form, button or template; whose
    nearest <article> is a card (an H2-bearing article holding no H2-bearing article, on a
    page with two or more such); under an
    <li> whose list has three or more H2-bearing items (a card grid); under a <header>
    that is not inside main/section/article; and an H2 whose text is entirely inside links (a card
    title). Text inside script/style/template is ignored; block tags and <br> separate
    words; whitespace is collapsed; empty headings are dropped.
    """
    return page_report(html)["h2"]


META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?([A-Za-z0-9._:-]+)""", re.I)


def decode_html(raw):
    """Decode by the page's <meta charset> when it names a known codec, else UTF-8 with
    replacement characters."""
    m = META_CHARSET.search(raw[:4096])
    if m:
        try:
            return raw.decode(m.group(1).decode("ascii"), errors="replace")
        except LookupError:
            pass
    return raw.decode("utf-8", errors="replace")


def section_target(pages):
    """(target, rows): match the highest cleaned H2 count unless it is an outlier.

    Only usable pages (not blocked, at least MIN_USABLE_H2 clean headings) set the number or count as the
    outlier's comparison; every page is still reported in rows. Ties on the top count go to
    the better Google position, then Bing, then URL.
    """
    rows = [{"url": p["url"], "google_pos": p.get("google_pos"), "bing_pos": p.get("bing_pos"),
             "h2_raw": p.get("h2_all", len(p.get("h2", []))),
             "h2_clean": len(clean_h2s(p.get("h2", []))), "outlier": False,
             "blocked": bool(p.get("blocked", False))} for p in pages]
    # A blocked page (a bot challenge) is never usable: it neither sets the number nor
    # makes another page an outlier.
    usable = [r for r in rows if r["h2_clean"] >= MIN_USABLE_H2 and not r["blocked"]]
    if not usable:
        return {"matched": 0, "set_by": None, "extra": EXTRA_SECTIONS, "floor": SECTION_FLOOR,
                "total": max(EXTRA_SECTIONS, SECTION_FLOOR)}, rows
    ranked = sorted(usable, key=lambda r: (-r["h2_clean"], r["google_pos"] or 99,
                                           r["bing_pos"] or 99, r["url"]))
    setter = ranked[0]
    if len(ranked) > 1 and ranked[0]["h2_clean"] > OUTLIER_RATIO * ranked[1]["h2_clean"]:
        ranked[0]["outlier"] = True
        setter = ranked[1]
    matched = setter["h2_clean"]
    return {"matched": matched, "set_by": setter["url"], "extra": EXTRA_SECTIONS,
            "floor": SECTION_FLOOR, "total": max(matched + EXTRA_SECTIONS, SECTION_FLOOR)}, rows


def covered_topics(pages):
    return {topic_of(h)[0] for p in pages for h in clean_h2s(p.get("h2", []))} - {None}


def _rank(q):
    """Score, then more evidence, then a settings-backed fact (the file every figure comes
    from), then id."""
    return (-q["score"], -len(q["found_in"]),
            not (q["fact_source"] or "").startswith("data/settings.json"), q["id"])


def pick_faq(questions):
    """Sets q["faq"] in place: block minimums first, then by score up to FAQ_TOTAL_MAX.

    At most FAQ_TOPIC_CAP questions per topic per block, in the minimum fill and the top-up.
    A block that cannot reach its minimum under the cap has the cap lifted for that block
    only: the cap never makes a block Short; too few fact-backed questions does.
    """
    by_block = {b: sorted((q for q in questions if q["fact_source"] and q["block"] == b), key=_rank)
                for b in BLOCKS}
    short = {b: (len(by_block[b]), FAQ_MIN[b]) for b in BLOCKS if len(by_block[b]) < FAQ_MIN[b]}
    if short:
        raise Short(short)
    picked, per, lifted = {}, {}, set()
    for b in BLOCKS:
        picked[b], per[b] = [], Counter()
        for q in by_block[b]:
            if len(picked[b]) < FAQ_MIN[b] and per[b][q["topic"]] < FAQ_TOPIC_CAP:
                picked[b].append(q)
                per[b][q["topic"]] += 1
        if len(picked[b]) < FAQ_MIN[b]:
            lifted.add(b)
            for q in by_block[b]:
                if len(picked[b]) < FAQ_MIN[b] and not any(q is x for x in picked[b]):
                    picked[b].append(q)
                    per[b][q["topic"]] += 1
    total = sum(len(v) for v in picked.values())
    rest = [q for b in BLOCKS for q in by_block[b] if not any(q is x for x in picked[b])]
    for q in sorted(rest, key=_rank):
        if total >= FAQ_TOTAL_MAX:
            break
        b = q["block"]
        if len(picked[b]) < FAQ_MAX[b] and (b in lifted or per[b][q["topic"]] < FAQ_TOPIC_CAP):
            picked[b].append(q)
            per[b][q["topic"]] += 1
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
    """A saved connector response means the call was already bought. A normalised file
    counts only when its status is "ok": a "fallback" or "NOT FETCHED" file never blocks the
    paid call. A normalised file that cannot be read fails closed (cached: no spend)."""
    d = Path(root) / "data/queries/raw" / slug
    if (d / f"{source}.response.json").is_file():
        return True
    f = d / f"{source}.json"
    if not f.is_file():
        return False
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return True
    return not isinstance(data, dict) or data.get("status") not in ("fallback", "NOT FETCHED")


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
        n = p.get("h2_all", 0)
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise BadInput(path, f"pages[{i}].h2_all must be a non-negative integer")
        if not isinstance(p.get("blocked", False), bool):
            raise BadInput(path, f"pages[{i}].blocked must be true or false")
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
    for i, q in enumerate(d.get("questions", [])):
        if not _valid_covered_by(q.get("covered_by")):
            raise BadInput(path, f"questions[{i}].covered_by must be null or "
                                 '{"where": "faq"|"heading", "text": non-empty string}')
    for i, e in enumerate(d.get("extra_sections", [])):
        if not _opt_str(e.get("heading")):
            raise BadInput(path, f"extra_sections[{i}].heading must be a string or null")
    return d


def _valid_covered_by(c):
    return c is None or (isinstance(c, dict) and set(c) == {"where", "text"}
                         and c["where"] in ("faq", "heading")
                         and isinstance(c["text"], str) and c["text"].strip() != "")


def _question_id(norm):
    """A pure function of the entry's normalised key, so an id never moves to another question.

    Ids are stable while a group's lead is unchanged: a collapsed group's id follows its lead
    (a bank-linked entry's key is the bank row's text). If a re-run changes a lead, the id
    changes with it; the builder's fills still carry, because they are matched by question
    text (_carry_fills), not by id.
    """
    base = ("q-" + "-".join(norm.split()[:8]))[:43].rstrip("-")
    return f"{base}-{hashlib.sha1(norm.encode()).hexdigest()[:6]}"


def _utc_today():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def _carry_fills(prev, questions, extras):
    """Copy covered_by (matched by normalised question text) and headings (by topic).

    Returns {"kept", "dropped", "kept_covered_by", "kept_headings"}: kept is the fills that
    found a home in this build (covered_by + headings), dropped the ones that did not.
    """
    if not prev:
        return {"kept": 0, "dropped": 0, "kept_covered_by": 0, "kept_headings": 0}
    covered = {normalise(q["question"]): q.get("covered_by") for q in prev.get("questions", [])
               if q.get("covered_by")}
    heads = {e["topic"]: e.get("heading") for e in prev.get("extra_sections", [])
             if e.get("heading")}
    kept_c = kept_h = 0
    for q in questions:
        n = normalise(q["question"])
        if n in covered:
            q["covered_by"] = covered[n]
            kept_c += 1
    for e in extras:
        if e["topic"] in heads:
            e["heading"] = heads[e["topic"]]
            kept_h += 1
    return {"kept": kept_c + kept_h, "dropped": len(covered) + len(heads) - kept_c - kept_h,
            "kept_covered_by": kept_c, "kept_headings": kept_h}


def build(slug, page_type, keyword, route, root=ROOT, today=None, prev=None):
    """(data, fills): the question file as a dict, and the fill counts from _carry_fills.

    Raises Short (with .blocked = [(block, question)]) when a FAQ block cannot be filled, and
    BadInput when an input file is unparseable or the wrong shape.
    """
    today = today or _utc_today()
    cands, status = load_candidates(slug, root)
    bank, status["bank"] = bank_candidates(root)
    cands += bank   # buyer phrasing first, so it wins the merge
    merged = collapse_near_duplicates(merge(cands, root, keyword), keyword)
    questions = []
    for n in sorted(merged):
        m = merged[n]
        topic, block = entry_topic(m)
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
    data = {"slug": slug, "page_type": page_type, "primary_keyword": keyword, "route": route,
            "fetched": today, "spend_usd": spend_for(slug, root), "sources": status,
            "competitors": rows, "section_target": target, "extra_sections": extras,
            "questions": questions}
    return data, fills


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
    ap.add_argument("--extract-h2", metavar="FILE")
    a = ap.parse_args(argv)
    root = Path(a.root)
    modes = [m for m in (a.preflight, a.record, a.slug, a.extract_h2) if m is not None]
    if len(modes) != 1:
        ap.error("give exactly one of --preflight SLUG, --record SLUG, --extract-h2 FILE "
                 "or a build SLUG")
    if a.extract_h2 is not None:
        try:
            html = decode_html(Path(a.extract_h2).read_bytes())
        except OSError as e:
            print(f"query_augment.py: bad input: {a.extract_h2}: cannot read "
                  f"({e.strerror or e})", file=sys.stderr)
            return EXIT_BAD_INPUT
        rep = page_report(html)
        if rep["blocked"]:
            print(f"query_augment.py: warning: {a.extract_h2} looks blocked (a bot challenge "
                  "or interstitial) — record it as blocked; it cannot set the section count",
                  file=sys.stderr)
        print(json.dumps(rep))   # ASCII-escaped: safe on any stdout
        return EXIT_OK
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
        data, fills = build(slug, a.page_type, a.keyword, a.route, root, a.today)
    except BadInput as e:
        print(f"query_augment.py: bad input: {e}", file=sys.stderr)
        return EXIT_BAD_INPUT
    except Short as e:
        kept = f"; existing data/queries/{slug}.json left unchanged" if out.exists() else ""
        print(f"SHORT: too few fact-backed questions — {e}{kept}")
        for block, question in e.blocked:
            print(f"  blocked ({block}): {question}")
        return EXIT_SHORT
    import jsonschema   # only build needs it, so preflight/record work without it
    try:
        check_schema(data)
    except jsonschema.ValidationError as e:   # a bug in this script, not in the inputs
        print(f"query_augment.py: internal error: the built file breaks "
              f"schemas/queries.schema.json ({e.message}); nothing written", file=sys.stderr)
        return EXIT_INTERNAL
    _write_json(out, data)
    faq = sum(1 for q in data["questions"] if q["faq"])
    print(f"wrote data/queries/{slug}.json — {len(data['questions'])} questions, {faq} FAQ, "
          f"section target {data['section_target']['total']}; "
          f"kept {fills.get('kept_covered_by', 0)} covered_by and "
          f"{fills.get('kept_headings', 0)} headings, dropped {fills['dropped']}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
