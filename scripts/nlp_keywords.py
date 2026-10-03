#!/usr/bin/env python3
"""Board block 4e: NLP keywords — the words a language model pulls out of a page as its topic,
context and meaning, read through three lenses.

  named entities      real-world things: a breed (Staffordshire Bull Terrier), an alias
                      (Staffy), an organisation (The Royal Kennel Club), a place (London,
                      Carlisle), a person (Lisa Bright), a condition or test (L-2-HGA)
  core concepts       the topics and actions the text is about (puppy socialisation, crate
                      training, health testing, deposit, delivery), each tagged with an
                      intent: buying, care, health, training or living
  semantic attributes descriptive modifiers of the dog's traits, health or look (blue coat,
                      muscular build, high energy), and an adjective written before the
                      breed name (loyal Staffy)

NO INVENTION (CLAUDE.md working rule 9). A row exists only when its term is ATTESTED:
written, as whole words, on at least MIN_DOMAINS distinct competitor DOMAINS of the page's
pool, or in one of our own data files (data/bsuk-ontology.json entities, data/faq.json,
data/settings.json, data/puppies.json, data/breed-standards.json, and the `questions` of the
page's data/queries/<slug>.json). Every row carries its evidence: the domains, and the data
file and key. Nothing is generated from a word list.

THE LEXICONS ONLY CLASSIFY. Each is a small closed list, and a lexicon entry alone never
makes a row — a lexicon word nobody wrote is never proposed:

  TOPIC_NOUNS     head words that make a phrase a concept without a process suffix
                  (deposit, contract, guarantee, microchip, delivery, insurance, …)
  NOT_CONCEPT     words that carry a process suffix but name no topic (thing, during,
                  including, question, section, moment, …)
  LEAD_VERBS      verbs that may not open a concept phrase ("use crate training" is
                  "crate training" said with a verb in front)
  TRAIT_NOUNS     the trait nouns an attribute closes on (coat, colour, build, temperament,
                  nature, size, weight, height, head, ears, eyes, nose, muzzle, chest, energy,
                  personality, lifespan), each typed look / temperament / health
  BREED_TOKENS, BREED_ADJ, COLOURS
                  the breed words, and the adjectives and colours that may stand before
                  them as an attribute ("loyal Staffy", "brindle Staffy")
  ORG_HEADS, TEST_TOKENS
                  how a capitalised name is typed (…Club → Organisation, …DNA test →
                  Condition / test); a name nothing types is "Other name"
  NER_TYPE        the ontology class → NER type map
  INTENT_EXTRA    three patterns for concepts query_augment.TOPICS has no topic for
                  (socialisation; grooming, exercise, walks; insurance, breeding, rehoming,
                  litters, viewing)

How a term is found and counted, reusing blocks 4c and 5c:

  pool        the board's `density_pool` pages exactly as block 4c picks them
              (term_density.competitor_pages), each read from the cache file block 5c
              reads it from. A competitor is a DOMAIN (term_gap.domain_of): five pages of
              one marketplace are one voice
  matching    keyword_metrics' tokeniser and small words, so matching is on WORD BOUNDARIES
              ("dog-walking" is "dog walking", and never matches "og walking"); UK and US
              spellings fold to one row (fold_tokens: -isation/-ise → -ization/-ize,
              -our → -or, grey → gray, centre → center, on words of six letters or more)
  phrases     1–3 key words inside one clause; a block element (heading, paragraph, list
              item, cell) ends a sentence, and a comma or dash ends a clause. No adverb,
              participle or LEAD_VERBS word opens a concept
  drops       block 5c's generic and site-chrome words, keyword_variants' BRAND_CLASH
              (marketplaces by name, cheap, rescue, free to a good home), and, on a location
              board, every other city of data/locations.json and every county or region
  names       a capitalised run of two to five words, of allowed inside, with the
              sentence's first word dropped (a sentence-initial capital is grammar, not a
              name) and the name written capitalised at least as often as in lower case
              (Title Case headings are not names). An ontology entity counts on a competitor
              by its name or a NAME-LIKE alias (one written with a capital: "Staffy", "KC");
              a lower-case alias ("the breeder", "deposit") is a description, not a name

Status, per row:
  on our page  the board's planned text carries it (the H1, title, description, every
               heading and intent in the outline tree, every keyword, every image alt), or,
               for an ontology entity, a section lists it
  gap          on MIN_DOMAINS+ competitor domains, not in our planned text
  ours only    in our data files, on fewer than MIN_DOMAINS competitor domains

A gap is a reading, not an instruction: it goes on the page only where a data file backs the
claim (rule 9). The block is derived from the board and is not part of the approved record.

    python3 scripts/nlp_keywords.py <slug> [--json]
"""
import json
import pathlib
import re
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
import keyword_variants as KV  # noqa: E402
import query_augment as QA  # noqa: E402
import term_density as TD  # noqa: E402
import term_gap as TG  # noqa: E402

ROOT = KM.ROOT
MIN_DOMAINS = TG.MIN_DOMAINS
MAX_N = 3
MAX_NAME = 5
ON_PAGE, GAP, OURS_ONLY = "on our page", "gap", "ours only"
STATUS_ORDER = {GAP: 0, ON_PAGE: 1, OURS_ONLY: 2}
#: How many rows of each status a board table shows; the CLI's --json lists every row.
SHOW = {GAP: 12, ON_PAGE: 8, OURS_ONLY: 6}
LENSES = (("entities", "Named entities (NER)", "Type"),
          ("concepts", "Core concepts and intent", "Intent"),
          ("attributes", "Semantic attributes", "Type"))
METHOD_NOTE = ("Attested on 2+ competitor domains or in our data files; lexicons only classify, "
               "they never create a row.")
USE_NOTE = ("A gap goes on the page only where a data file backs the claim (working rule 9); the "
            "median-band and ceiling caution of block 4c applies to every count here.")
NOT_FETCHED = "NOT FETCHED — no cached competitor page"
ONT = "data/bsuk-ontology.json"

# ── lexicons (classification only) ──────────────────────────────────────────────────────────
TOPIC_NOUNS = frozenset("""deposit deposits contract contracts guarantee guarantees vaccine vaccines
microchip microchips registration delivery deliveries collection insurance pedigree paperwork
papers aftercare health diet exercise price prices cost costs transport litter litters care food
worming payment visit visits""".split())
NOT_CONCEPT = frozenset("""thing things something anything everything nothing morning evening during
including according following being bring string spring ceiling king ring wing sibling siblings
darling pudding amazing stunning interesting exciting outstanding existing upcoming ongoing missing
remaining looking going coming getting having making taking giving saying using wanting willing
working leading loving seeing listing listings rating ratings advertising question questions
section sections option options version mention position location locations addition edition
caption description attention information comment comments moment moments element elements
department segment sentence reference instance audience circumstance circumstances situation
situations""".split())
LEAD_VERBS = frozenset("""use uses start starts offer offers provide provides include includes give
gives take takes help helps keep keeps ensure ensures require requires begin begins love loves
recommend recommends raise raises raised want wants cover covers available""".split())
OPENERS_OK = frozenset({"puppy", "puppies", "dog", "dogs"})
PROCESS_SUFFIXES = ("ing", "tion", "sion", "ment", "ance", "ence")
#: trait noun (folded spelling) -> attribute type
TRAIT_TYPE = {
    "coat": "look", "color": "look", "build": "look", "size": "look", "weight": "look",
    "height": "look", "head": "look", "ears": "look", "eyes": "look", "nose": "look",
    "muzzle": "look", "chest": "look",
    "temperament": "temperament", "nature": "temperament", "energy": "temperament",
    "personality": "temperament",
    "lifespan": "health",
}
TRAIT_NOUNS = frozenset(TRAIT_TYPE)
BREED_TOKENS = frozenset("staffy staffie staffies staffys stafford staffords terrier terriers".split())
COLOURS = frozenset("blue red fawn black white brindle brown liver pied merle lilac champagne gray".split())
BREED_ADJ = {**{w: "temperament" for w in """loyal affectionate friendly loving gentle playful
energetic intelligent clever smart brave bold fearless courageous tenacious reliable calm confident
sweet cuddly stubborn sociable happy""".split()},
             **{w: "look" for w in """muscular stocky compact powerful strong athletic sturdy
chunky""".split()},
             "healthy": "health"}
ORG_HEADS = frozenset("""club association society council trust charity government office agency
institute college foundation league federation""".split())
TEST_TOKENS = frozenset("""dna test tests testing scheme syndrome disease cataract cataracts hga
phpv screening score scores""".split())
NER_TYPE = {"Organism": "Breed / animal", "People": "Person", "Organization": "Organisation",
            "Place": "Place", "Health": "Condition / test", "Documentation": "Product / document",
            "Regulation": "Product / document", "Commerce": "Product / document",
            "Logistics": "Product / document", "Method": "Product / document"}
#: query_augment.TOPICS topic -> intent
TOPIC_INTENT = {"price": "buying", "reserve": "buying", "delivery": "buying", "visit": "buying",
                "paperwork": "buying", "trust": "buying", "age": "buying",
                "health": "health", "lifespan": "health", "training": "training",
                "home": "living", "family": "living", "temperament": "living", "breed": "living",
                "care": "care", "coat": "care"}
INTENT_EXTRA = ((re.compile(r"\bsociali[sz]"), "training"),
                (re.compile(r"\b(groom|exercis|walk)"), "care"),
                (re.compile(r"\b(insur|breeding|rehom|litters?\b|viewing)"), "buying"))

BLOCK_TAGS = frozenset("""p div li ul ol h1 h2 h3 h4 h5 h6 td th tr table br section article header
main dt dd dl blockquote figcaption figure button label option summary details""".split())
CASED = re.compile(r"[A-Za-z0-9£]+(?:'[A-Za-z]+)?")
PLACEHOLDER = re.compile(r"\{[^}]*\}|https?://\S+|\S+@\S+")
_FOLD = ((re.compile(r"isation(s?)$"), r"ization\1"), (re.compile(r"is(e|ed|es|ing)$"), r"iz\1"),
         (re.compile(r"our(s?)$"), r"or\1"), (re.compile(r"^centre(s?)$"), r"center\1"))


# ── matching ────────────────────────────────────────────────────────────────────────────────
def fold_tokens(toks):
    """UK and US spellings to one form, on words of six letters or more (so "our" stays)."""
    out = []
    for t in toks:
        if t == "grey":
            t = "gray"
        elif len(t) >= 6:
            for pat, rep in _FOLD:
                new = pat.sub(rep, t)
                if new != t:
                    t = new
                    break
        out.append(t)
    return out


def key(text):
    """`text` as folded key words: keyword_metrics' tokeniser and small words, then the fold."""
    return fold_tokens(KM.key_words(text))


def mentions(term, text):
    """Whole-word occurrences of `term` in `text` (case, small words and UK/US spelling
    ignored)."""
    toks = key(text)
    return len(KM._starts(key(term), toks, KM._index(toks)))


def _count(ptoks, toks, idx):
    return len(KM._starts(list(ptoks), toks, idx)) if ptoks else 0


def _contains(big, small):
    return TG._contains(list(big), list(small))


# ── bodies ──────────────────────────────────────────────────────────────────────────────────
class _Blocks(KM._Page):
    """keyword_metrics' page parser with a line break at every block element, so a heading
    and the paragraph under it are two sentences, not one."""

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK_TAGS:
            self.handle_data("\n")
        super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag in BLOCK_TAGS:
            self.handle_data("\n")
        super().handle_endtag(tag)


def _sentences(text):
    return [s.strip() for s in TG.SPLIT.split(text or "") if s.strip()]


CLAUSE = re.compile(r",|\s[-–—]\s|[–—]")


def _chunk(sentence):
    """(surface key words, folded key words) for one sentence."""
    raw = KM.key_words(sentence)
    return raw, fold_tokens(raw)


def _chunks(sentences):
    """Phrase chunks: sentences cut again at commas and dashes, since a noun phrase never
    crosses one ("Kennel Club registered, health tested" holds no "registered health")."""
    return [_chunk(c) for s in sentences for c in CLAUSE.split(s) if c.strip()]


def body(html, listing=False, **extra):
    """One competitor body: domain (from extra["url"]), listing flag, cased sentences, folded
    key-word tokens with their index, and per-sentence chunks."""
    p = _Blocks()
    p.feed(html)
    p.close()
    text = " ".join(r[0] for r in p.body())
    sents = _sentences(text)
    toks = key(text)
    return dict(extra, listing=bool(listing), domain=TG.domain_of(extra.get("url", "")),
                sentences=sents, tokens=toks, index=KM._index(toks),
                chunks=_chunks(sents))


def _bodies(pages):
    out = []
    for i, p in enumerate(pages):
        b = p if isinstance(p, dict) else body(p)
        if not b.get("domain"):
            b = dict(b, domain=f"page-{i + 1}")
        out.append(b)
    return out


def pool_bodies(board, root=ROOT):
    """The block 4c pool (the board's density_pool, term_density.competitor_pages), as body()
    dicts in rank order. Each page's cache file is found by its url's 1-based index in
    data/queries/raw/<slug>/competitors.json, the numbering block 5c's loader uses."""
    slug = board["meta"]["slug"]
    picked = TD.competitor_pages(slug, [], root,
                                 include_listings=TD.density_pool(board) == "all")
    bare = KM._bare(slug)
    raw = (_load(pathlib.Path(root) / "data/queries/raw" / bare / "competitors.json") or {})
    index = {}
    for n, p in enumerate(raw.get("pages") or [], 1):
        if not p.get("blocked"):
            index.setdefault(p.get("url", ""), n)
    out = []
    for p in picked:
        n = index.get(p["url"])
        cached = pathlib.Path(root) / "data/queries/cache" / bare / f"{n}.html"
        if n is None or not cached.exists():
            continue
        html = cached.read_text(encoding="utf-8", errors="replace")
        out.append(body(html, p["kind"] == "listing", n=n, rank=p["rank"], url=p["url"]))
    return out


# ── our side ────────────────────────────────────────────────────────────────────────────────
def _doc(label, text):
    text = PLACEHOLDER.sub(" ", text or "")
    toks = key(text)
    return {"label": label, "tokens": toks, "index": KM._index(toks),
            "chunks": _chunks(_sentences(text))}


def _docs(docs):
    return [d if isinstance(d, dict) else _doc(*d) for d in docs or ()]


def _load(path):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def data_docs(slug, ont, root=ROOT):
    """(label, text) for every attesting string of our data files. Keys that hold sources,
    dates, urls, file names or contact details are not text and are skipped."""
    root = pathlib.Path(root)
    out = []
    for f in _load(root / "data/faq.json") or []:
        for k in ("q", "a"):
            if f.get(k):
                out.append((f"data/faq.json#{f.get('id')}.{k}", f[k]))
    skip = re.compile(r"source|fetched|url|path|photo|gallery|logo|email|phone|socials|youtube"
                      r"|hours|slug|budget|usd|^id$")

    def walk(prefix, label, node):
        if isinstance(node, dict):
            for k, v in node.items():
                if not skip.search(str(k)):
                    walk(prefix, f"{label}.{k}" if label else str(k), v)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(prefix, f"{label}.{i}", v)
        elif isinstance(node, str) and node.strip():
            out.append((f"{prefix}#{label}", node))

    settings = _load(root / "data/settings.json") or {}
    walk("data/settings.json", "", settings)
    for p in _load(root / "data/puppies.json") or []:
        if p.get("colour"):
            out.append((f"data/puppies.json#{p.get('slug')}.colour", p["colour"]))
    bs = _load(root / "data/breed-standards.json") or {}
    for bid, b in (bs.get("breeds") or {}).items():
        for field, v in (b or {}).items():
            if isinstance(v, dict):
                for k in ("value", "quote"):
                    if isinstance(v.get(k), str):
                        out.append((f"data/breed-standards.json#breeds.{bid}.{field}.{k}", v[k]))
            elif isinstance(v, str) and field == "name":
                out.append((f"data/breed-standards.json#breeds.{bid}.name", v))
    q = _load(root / "data/queries" / f"{KM._bare(slug)}.json") or {}
    for row in q.get("questions") or []:
        if row.get("question"):
            out.append((f"data/queries/{KM._bare(slug)}.json#questions.{row.get('id')}",
                        row["question"]))
    for e in (ont or {}).get("entities", []):
        for n in TG._names(e):
            out.append((f"{ONT}#{e.get('id')}", n))
    return out


def our_text(board):
    """The board's planned text: picked H1, title and description, every section heading,
    every heading and intent in the outline tree, every keyword, every image alt."""
    import pageboard as PB   # lazy: pageboard imports family_rules, which imports keyword_metrics
    parts = [PB.picked_h1(board)] + list(PB.meta_pick(board))

    def tree(nodes):
        for n in nodes or []:
            parts.extend([n.get("heading") or "", n.get("intent") or ""])
            tree(n.get("children"))

    for s in board.get("sections", []):
        parts.append(s.get("heading") or "")
        tree(s.get("tree"))
        for vals in (s.get("keywords") or {}).values():
            parts.extend(vals)
    parts.extend(a.get("alt") or "" for a in board.get("assets") or [])
    return "\n".join(p for p in parts if p)


def _board_entity_ids(board):
    ids = [i for s in board.get("sections", []) for i in (s.get("entities") or [])]
    return list(dict.fromkeys(ids))


def _research_entity_ids(board, root=ROOT):
    rb = _load(pathlib.Path(root) / "data/research-boards" / f"{KM._bare(board['meta']['slug'])}.json")
    return [e["id"] for e in (rb or {}).get("entities") or [] if isinstance(e, dict) and e.get("id")]


# ── shared row machinery ────────────────────────────────────────────────────────────────────
def _drop(gram, surface, places):
    if KV.brand_clash(surface):
        return True
    return any(_contains(gram, p) for p in places)


def _place_grams(places):
    return [g for g in (tuple(key(p)) for p in places or ()) if g]


def _status(ours, domains, listed=False):
    if ours or listed:
        return ON_PAGE
    return GAP if domains >= MIN_DOMAINS else OURS_ONLY


def _sort(rows):
    rows.sort(key=lambda r: (STATUS_ORDER[r["status"]], -r["domains"], -r["mentions"],
                             -r["data_mentions"], r["term"].lower()))
    return rows


def _surface(st):
    """Display spelling: our data's, else a UK spelling, else the commonest competitor one."""
    if st["data_surface"]:
        return st["data_surface"].most_common(1)[0][0]
    uk = [s for s, _ in st["surface"].most_common() if " ".join(key(s)) != s]
    return uk[0] if uk else st["surface"].most_common(1)[0][0]


def _grams(bodies, docs, places, ok):
    """{folded gram: stats} for every 1–MAX_N gram `ok(gram)` accepts, from competitor sentences
    and our data sentences; `ok` returns the gram's type or None."""
    seen = {}

    def stat(g):
        return seen.setdefault(g, {"domains": set(), "pages": 0, "mentions": 0, "data": [],
                                   "data_mentions": 0, "surface": Counter(),
                                   "data_surface": Counter(), "type": None})

    def scan(chunks):
        local = {}
        for raw, fold in chunks:
            for n in range(1, MAX_N + 1):
                for i in range(len(fold) - n + 1):
                    g = tuple(fold[i:i + n])
                    entry = local.setdefault(g, [0, Counter()])
                    entry[0] += 1
                    entry[1][" ".join(raw[i:i + n])] += 1
        return local

    verdict = {}

    def accept(g, surface):
        if g not in verdict:
            t = ok(g)
            verdict[g] = t if t and not _drop(g, surface, places) else None
        return verdict[g]

    for b in bodies:
        for g, (c, surf) in scan(b["chunks"]).items():
            t = accept(g, surf.most_common(1)[0][0])
            if not t:
                continue
            st = stat(g)
            st["type"] = t
            st["domains"].add(b["domain"])
            st["pages"] += 1
            st["mentions"] += c
            st["surface"].update(surf)
    for d in docs:
        for g, (c, surf) in scan(d["chunks"]).items():
            t = accept(g, surf.most_common(1)[0][0])
            if not t:
                continue
            st = stat(g)
            st["type"] = t
            st["data"].append(d["label"])
            st["data_mentions"] += c
            st["data_surface"].update(surf)
    return seen


def _rows(seen, lens, our_toks, exclude, min_domains):
    our_idx = KM._index(our_toks)
    rows = []
    for g, st in seen.items():
        if g in exclude or (len(st["domains"]) < min_domains and not st["data"]):
            continue
        ours = _count(g, our_toks, our_idx)
        rows.append({"term": _surface(st), "lens": lens, "type": st["type"],
                     "domains": len(st["domains"]), "domain_list": sorted(st["domains"]),
                     "pages": st["pages"], "mentions": st["mentions"], "ours": ours,
                     "data_sources": list(dict.fromkeys(st["data"])),
                     "data_mentions": st["data_mentions"],
                     "status": _status(ours, len(st["domains"])), "_gram": g})
    # block 5c's dedupe: a shorter phrase inside a longer row with the same evidence adds nothing
    subs = set()
    for r in rows:
        g = r["_gram"]
        for n in range(1, len(g)):
            for i in range(len(g) - n + 1):
                subs.add((g[i:i + n], tuple(r["domain_list"]), r["mentions"], r["data_mentions"]))
    rows = [r for r in rows
            if (r["_gram"], tuple(r["domain_list"]), r["mentions"], r["data_mentions"]) not in subs]
    return _sort(rows)


def public(rows):
    return [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]


# ── lens 2: core concepts ───────────────────────────────────────────────────────────────────
def _base(t):
    return t[:-1] if len(t) > 4 and t.endswith("s") and not t.endswith("ss") else t


def _process(t):
    """True when `t` names a process or topic by its suffix (not the TOPIC_NOUNS list)."""
    b = _base(t)
    if t in NOT_CONCEPT or b in NOT_CONCEPT or t in TRAIT_NOUNS or b in TRAIT_NOUNS:
        return False
    return len(b) >= 6 and b.endswith(PROCESS_SUFFIXES)


def is_concept_head(t):
    if t in NOT_CONCEPT or _base(t) in NOT_CONCEPT:
        return False
    return t in TOPIC_NOUNS or _base(t) in TOPIC_NOUNS or _process(t)


def _bad_token(t):
    return t in TG.STOP_UI or bool(TG.JUNK.match(t))


def intent_of(term):
    """buying / care / health / training / living, from query_augment.TOPICS, then
    INTENT_EXTRA; "—" when neither knows the term."""
    topic, _ = QA.topic_of(term)
    if topic in TOPIC_INTENT:
        return TOPIC_INTENT[topic]
    low = term.lower()
    for pat, intent in INTENT_EXTRA:
        if pat.search(low):
            return intent
    return "—"


def _concept_ok(g):
    if not is_concept_head(g[-1]) or any(_bad_token(t) for t in g):
        return None
    generic = TG.STOP_GENERIC - OPENERS_OK
    # an adverb or a participle never opens a concept: "registered health" is "registered and
    # health checked" with keyword_metrics' small word dropped
    if g[0] in generic or g[0] in LEAD_VERBS or (len(g) > 1 and g[0].endswith(("ly", "ed"))):
        return None
    if any(t in generic or _process(t) for t in g[:-1]):
        return None
    return intent_of(" ".join(g))


def core_concepts(pages, our_text="", data_docs=(), places=(), exclude=(),
                  min_domains=MIN_DOMAINS):
    """Concept rows: 1–3 key-word phrases whose head (last word) is a process or topic noun,
    attested on `min_domains`+ competitor domains or in `data_docs`. `exclude` holds folded
    grams another lens owns (a proper name)."""
    seen = _grams(_bodies(pages), _docs(data_docs), _place_grams(places), _concept_ok)
    return public(_rows(seen, "concept", key(our_text), set(exclude), min_domains))


# ── lens 3: semantic attributes ─────────────────────────────────────────────────────────────
def _attribute_ok(g):
    if len(g) != 2 or any(_bad_token(t) for t in g):
        return None
    mod, head = g
    if head in TRAIT_TYPE:
        if (mod in TG.STOP_GENERIC or mod in BREED_TOKENS or mod in LEAD_VERBS
                or is_concept_head(mod) or (mod in TRAIT_TYPE and mod != "coat")):
            return None
        return TRAIT_TYPE[head]
    if head in BREED_TOKENS:
        if mod in COLOURS:
            return "look"
        return BREED_ADJ.get(mod)
    return None


def semantic_attributes(pages, our_text="", data_docs=(), places=(), exclude=(),
                        min_domains=MIN_DOMAINS):
    """Attribute rows: modifier + trait noun (TRAIT_NOUNS), or an adjective or colour before
    the breed name, attested on `min_domains`+ competitor domains or in `data_docs`."""
    seen = _grams(_bodies(pages), _docs(data_docs), _place_grams(places), _attribute_ok)
    return public(_rows(seen, "attribute", key(our_text), set(exclude), min_domains))


# ── lens 1: named entities ──────────────────────────────────────────────────────────────────
def _name_like(form):
    return bool(form) and (form[0].isupper() or any(c.isdigit() for c in form))


def _forms(e):
    """The forms an entity is counted by: its name, and every alias written as a name."""
    names = TG._names(e)
    return [names[0]] + [a for a in names[1:] if _name_like(a)] if names else []


def _capital_runs(sentence):
    """Capitalised runs of 2–MAX_NAME words in one sentence, its first word dropped."""
    toks = CASED.findall(sentence.replace("’", "'"))
    out, run = [], []

    def flush(end):
        r = list(run)
        if r and r[0][1] == 0:
            r = r[1:]
        words = [t for t, _ in r]
        small = KM.STOP | TG.STOP_GENERIC | {"of"}
        while words and words[0].lower() in small:
            words.pop(0)
        while words and words[-1].lower() in small:
            words.pop()
        if 2 <= len(words) <= MAX_NAME and not all(w.isupper() and len(w) > 1 for w in words):
            out.append(" ".join(words))

    for i, t in enumerate(toks):
        if t[0].isupper() or (t == "of" and run):
            run.append((t, i))
        else:
            flush(i)
            run = []
    flush(len(toks))
    return out


def _name_type(g, place_words):
    if any(t in place_words for t in g):
        return "Place"
    if any(t in BREED_TOKENS or t == "bull" for t in g):
        return "Breed / animal"
    if any(t in TEST_TOKENS for t in g):
        return "Condition / test"
    if g[-1] in ORG_HEADS:
        return "Organisation"
    return "Other name"


def _place_words(ont, root=ROOT):
    words = set()
    for e in (ont or {}).get("entities", []):
        if e.get("class") == "Place":
            for n in TG._names(e):
                words.update(key(n))
    rows = _load(pathlib.Path(root) / "data/locations.json") or []
    for r in rows if isinstance(rows, list) else []:
        words.update(key(re.sub(r"\(.*?\)", "", r.get("city") or "")))
    words.discard("uk")
    return words


def named_entities(pages, ont, our_text="", data_docs=(), board_entity_ids=(), places=(),
                   min_domains=MIN_DOMAINS, also_ids=(), root=ROOT):
    """Entity rows. (1) Ontology entities, typed by NER_TYPE, counted on competitors by their
    name-like forms, kept when on `min_domains`+ domains or named on the board
    (`board_entity_ids`, which also makes them "on our page") or in `also_ids` (the research
    board). An ontology Place that is another city, county or region (`places`) is left out.
    (2) Capitalised multi-word names on `min_domains`+ domains that no ontology form covers."""
    bodies = _bodies(pages)
    docs = _docs(data_docs)
    our_toks = key(our_text)
    our_idx = KM._index(our_toks)
    listed = set(board_entity_ids or ())
    wanted = listed | set(also_ids or ())
    others = {p.lower() for p in places or ()}
    pgrams = _place_grams(places)
    rows, ont_grams = [], set()
    for e in (ont or {}).get("entities", []):
        if not e.get("id"):
            continue
        for n in TG._names(e):
            ont_grams.add(tuple(key(n)))
        row = {"class": e.get("class", ""), "name": e.get("name", ""),
               "place_type": e.get("place_type", "")}
        if TG._is_other_place(row, others):
            continue
        forms = [f for f in (tuple(key(x)) for x in _forms(e)) if f]
        domains, pages_n, total = set(), 0, 0
        for b in bodies:
            c = max((_count(f, b["tokens"], b["index"]) for f in forms), default=0)
            if c:
                domains.add(b["domain"])
                pages_n += 1
                total += c
        if len(domains) < min_domains and e["id"] not in wanted:
            continue
        ours = max((_count(f, our_toks, our_idx) for f in forms), default=0)
        rows.append({"term": e.get("name", e["id"]), "lens": "entity",
                     "type": NER_TYPE.get(e.get("class"), "Other name"), "id": e["id"],
                     "domains": len(domains), "domain_list": sorted(domains), "pages": pages_n,
                     "mentions": total, "ours": ours,
                     "data_sources": [f"{ONT}#{e['id']}"], "data_mentions": 1,
                     "status": _status(ours, len(domains), e["id"] in listed),
                     "listed": e["id"] in listed,
                     "forms": [" ".join(f) for f in forms], "_proper": _name_like(e.get("name", "")),
                     "_grams": forms})

    # (2) capitalised names on the competitor pages
    pwords = _place_words(ont, root)
    caps = {}
    for b in bodies:
        local = Counter()
        for s in b["sentences"]:
            for name in _capital_runs(s):
                local[name] += 1
        for name, c in local.items():
            g = tuple(key(name))
            if not g or g in ont_grams or any(_bad_token(t) for t in g):
                continue
            if _drop(g, name.lower(), pgrams):
                continue
            st = caps.setdefault(g, {"domains": set(), "pages": 0, "caps": 0, "surface": Counter()})
            st["domains"].add(b["domain"])
            st["pages"] += 1
            st["caps"] += c
            st["surface"][name] += c
    for g, st in caps.items():
        if len(st["domains"]) < min_domains:
            continue
        total = sum(_count(g, b["tokens"], b["index"]) for b in bodies)
        if st["caps"] < total - st["caps"]:      # written lower case more often: not a name
            continue
        data = [d["label"] for d in docs if _count(g, d["tokens"], d["index"])]
        ours = _count(g, our_toks, our_idx)
        rows.append({"term": st["surface"].most_common(1)[0][0], "lens": "entity",
                     "type": _name_type(g, pwords), "id": None,
                     "domains": len(st["domains"]), "domain_list": sorted(st["domains"]),
                     "pages": st["pages"], "mentions": total, "ours": ours,
                     "data_sources": list(dict.fromkeys(data)), "data_mentions": len(data),
                     "status": _status(ours, len(st["domains"])),
                     "forms": [" ".join(g)], "_proper": True, "_grams": [g]})
    return _sort(rows) if rows else rows


def proper_grams(entity_rows_internal):
    return {g for r in entity_rows_internal if r.get("_proper") for g in r.get("_grams", [])}


# ── the board block ─────────────────────────────────────────────────────────────────────────
def rows(board, ont, root=ROOT):
    """{"pool": [body dicts], "entities", "concepts", "attributes"} for the board."""
    slug = board["meta"]["slug"]
    bodies = pool_bodies(board, root)
    location = (board["meta"].get("page_type") or "") == "location"
    places = TG.place_names(ont, TG.other_cities(slug, root)) if location else []
    ours = our_text(board)
    docs = _docs(data_docs(slug, ont, root))
    ents = named_entities(bodies, ont, ours, docs, _board_entity_ids(board), places,
                          also_ids=_research_entity_ids(board, root), root=root)
    exclude = proper_grams(ents)
    return {"pool": bodies,
            "entities": public(ents),
            "concepts": core_concepts(bodies, ours, docs, places, exclude),
            "attributes": semantic_attributes(bodies, ours, docs, places, exclude)}


def _sources(r):
    parts = list(r["domain_list"])
    data = r.get("data_sources") or []
    parts += data[:2] + ([f"+{len(data) - 2} more"] if len(data) > 2 else [])
    return ", ".join(f"`{p}`" if "#" in p else p for p in parts) or "—"


def _ours(r):
    """The planned-text count; an entity a section lists but no planned text names yet reads
    "0 (listed)", so "on our page" never sits beside a bare 0 unexplained."""
    return f"{r['ours']} (listed)" if r.get("listed") and not r["ours"] else r["ours"]


def _shown(rs):
    out, cut = [], 0
    by = Counter()
    for r in rs:
        if by[r["status"]] < SHOW[r["status"]]:
            out.append(r)
            by[r["status"]] += 1
        else:
            cut += 1
    return out, cut


def render(by_lens, pool_line="", slug="<slug>"):
    """Block 4e as markdown: the pool line, the method note, one table per lens."""
    out = [pool_line] if pool_line else []
    out.append(METHOD_NOTE + " " + USE_NOTE)
    hidden = 0
    for k, title, col in LENSES:
        rs = by_lens.get(k) or []
        n = Counter(r["status"] for r in rs)
        out.append(f"**{title}** — {len(rs)} rows: {n[GAP]} gap, {n[ON_PAGE]} on our page, "
                   f"{n[OURS_ONLY]} ours only")
        shown, cut = _shown(rs)
        hidden += cut
        out.append(TD.md_table(["Term", col, "Competitor domains", "Ours (planned)", "Status",
                                "Sources"],
                               [[r["term"], r["type"], r["domains"], _ours(r), r["status"],
                                 _sources(r)] for r in shown])
                   if shown else "None attested.")
    if hidden:
        out.append(f"{hidden} more rows are not shown (each table shows up to {SHOW[GAP]} gaps, "
                   f"{SHOW[ON_PAGE]} on our page and {SHOW[OURS_ONLY]} ours only): "
                   f"`python3 scripts/nlp_keywords.py {slug} --json` lists every row.")
    return "\n\n".join(out)


def pool_line(bodies):
    if not bodies:
        return f"Measured on 0 competitor pages: {NOT_FETCHED}."
    n_dom, line = TG._domain_line(bodies)
    prose = sum(1 for b in bodies if not b["listing"])
    out = (f"Measured on block 4c's pool: {len(bodies)} competitor pages ({prose} prose, "
           f"{len(bodies) - prose} listing) on {n_dom} domains — {line}. A competitor is a "
           "domain, counted once however many of its pages are in the pool.")
    if n_dom < 3:
        out += " **Thin pool:** fewer than three domains — read the gaps as hints."
    return out


def block(board, ont, root=ROOT):
    r = rows(board, ont, root)
    return render(r, pool_line(r["pool"]), board["meta"]["slug"])


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    usage = "usage: python3 scripts/nlp_keywords.py <slug> [--json]"
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    if len(args) != 1:
        print(usage, file=sys.stderr)
        return 2
    path = ROOT / "data/boards" / f"{KM._bare(args[0])}.json"
    if not path.is_file():
        print(f"{usage} — no board at {path.relative_to(ROOT)}", file=sys.stderr)
        return 2
    board = json.loads(path.read_text(encoding="utf-8"))
    ont = json.loads((ROOT / "data/bsuk-ontology.json").read_text(encoding="utf-8"))
    if as_json:
        r = rows(board, ont)
        pool = [{"url": b.get("url"), "rank": b.get("rank"), "domain": b["domain"],
                 "listing": b["listing"]} for b in r.pop("pool")]
        print(json.dumps({"slug": board["meta"]["slug"], "pool": pool, **r}, indent=2,
                         ensure_ascii=False))
    else:
        print(block(board, ont))
    return 0


if __name__ == "__main__":
    sys.exit(main())
