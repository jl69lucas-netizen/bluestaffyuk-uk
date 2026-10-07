#!/usr/bin/env python3
"""
Evidence audit — the measurable half of .claude/skills/bsuk-evidence-pass/SKILL.md.

Asks of a built page: does it PROVE what it asserts, or merely repeat it?
Runs over dist/ (the rendered page, never the source).

Checks (ids are the rule-index ids):
  term-budget-per-page        trust-concept mentions in <main> vs data/quality/evidence-budgets.json
                               (per-slug override: budgets_by_slug; a location page's head terms
                               are densities, location_density, counted with board block 4c's
                               counter and scaled by the page's own word count)
  title-length-max            <title> length vs title_max_chars (per-slug override: title_max_chars_by_slug)
  review-attribution-unique   the same review text credited to two different names on one page
  claim-bound-to-proof        a ledger claim made 2+ times must link its proof object (ERROR);
                              a claim whose proof is NOT FETCHED is a WARN, never silently a pass
                              — except a `naming_only` row under a breeder `repeat_ruling`, whose
                              repeats are no finding while no repeating sentence states a result
  claim-unledgered            a sentence using the ledger's health/credential `vocabulary` that no
                              ledger claim matches (ERROR on a new location, comparison or blog
                              page — rebuilt, outside family_rules' frozen twelve; WARN elsewhere)
                              — a ledger row clears only the ids in its `covers`; preview pages
                              (board-preview/, kit-preview) are not checked
  statement-labels-present    sections carrying species/health/comparison facts carry a .stmt-label
  no-not-fetched-in-prose     the literal NOT FETCHED never ships in visible text
  no-unsourced-superlatives   "world's best" etc. without a link in the same sentence

Per .claude/skills/bsuk-gate-integrity/SKILL.md: term counts are exact; the label and superlative checks are
PROXIES (a regex cannot judge whether a sentence is a species fact). Read a flagged section
before rewriting it, and read the examined count: `0 pages matched` is not a pass.

Usage:
  python3 scripts/evidence_audit.py <slug> [<slug> ...] [--type home|for-sale|puppy|comparison|location|interior|blog|hub]
                                    [--rebuilt PATH]   (default data/facts/rebuilt.json)
  python3 scripts/evidence_audit.py --all
  python3 scripts/evidence_audit.py --all --json        # also write the JSON report

Exit code: 1 on any ERROR, when the slug filter matched nothing (0 pages matched is
never a pass), or when --fail-on-error is passed and any WARN was found; 0 otherwise.
Exit 2 when data/quality/evidence-budgets.json does not exist yet (Task 9 writes it) —
a missing budget file is a gate that cannot run, not a gate that passed.
"""
import re, sys, json, pathlib, argparse
from collections import defaultdict
from functools import lru_cache

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _slugs import dist_path as _dist_path, page_key  # noqa: E402
from _html import strip_tags, unescape, text_of  # noqa: E402  one shared decoder

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUDGETS_PATH = ROOT / "data" / "quality" / "evidence-budgets.json"
LEDGER_PATH = ROOT / "data" / "quality" / "evidence-ledger.json"
TARGETS_PATH = ROOT / "tests" / "render" / "targets.json"
REBUILT_PATH = ROOT / "data" / "facts" / "rebuilt.json"
LOCATIONS_PATH = ROOT / "data" / "locations.json"
# The `{city}` term (data/quality/evidence-budgets.json) is the page's OWN city, resolved per
# slug: a Glasgow-only city term left 27 of the 28 city pages with no ceiling at all.
CITY_TERM = "{city}"

CHECK_IDS = [
    {"id": "term-budget-per-page"},
    {"id": "title-length-max"},
    {"id": "review-attribution-unique"},
    {"id": "claim-bound-to-proof"},
    {"id": "claim-unledgered"},
    {"id": "statement-labels-present"},
    {"id": "no-not-fetched-in-prose"},
    {"id": "no-unsourced-superlatives"},
]

FACT_SIGNAL = re.compile(
    r"Canis\s+(?:lupus\s+)?familiaris|\b1[0-9]\s*(?:to|–|-)\s*1[0-9]\s+years"
    r"|lifespan|hip\s*score|elbow\s*score|L2-?HGA|HC\b|PHPV|patella|KC[- ]registered", re.I)


def main_html(html):
    m = re.search(r"<main\b.*?</main>", html, flags=re.S | re.I)
    return m.group(0) if m else html


# ── term-budget-per-page ────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _location_cities():
    """{location slug: city} from data/locations.json; empty when the file is absent.
    Cached: a caller that changes LOCATIONS_PATH must call `_location_cities.cache_clear()`."""
    if not LOCATIONS_PATH.exists():
        return {}
    return {r["slug"]: r["city"] for r in json.loads(LOCATIONS_PATH.read_text(encoding="utf-8"))}


def city_for(slug):
    """The city a `uk-locations/<slug>` page is about, or None.

    A bracketed note is not part of the name (`Glasgow (breeding dogs)` is Glasgow), and a
    national row (`city` "UK") has no city term: the `uk` head term already budgets that word.
    Any page outside the city cluster has no city term either."""
    if not slug.startswith("uk-locations/"):
        return None
    city = _location_cities().get(slug.split("/", 1)[1])
    if not city:
        return None
    city = re.sub(r"\s*\(.*?\)\s*", " ", city).strip()
    return None if city.upper() == "UK" else city


def city_pattern(city):
    """`Newcastle-under-Lyme` also matches `Newcastle under Lyme`: any run of spaces or
    hyphens in the name matches any run of spaces or hyphens on the page."""
    words = [w for w in re.split(r"[\s-]+", city) if w]
    if not words:
        # r"\b\b" would match everywhere: a name with no words is a data error, not a term
        raise ValueError(f"city {city!r} has no words to match")
    return r"\b" + r"[\s-]+".join(re.escape(w) for w in words) + r"\b"


def _location_density(html, budgets, slug):
    """{term: (count, ceiling)} for the location head terms that have a density
    (`location_density.per_1000_words`, Known Issue 99 option (a), user 2026-10-07).

    Counted with board block 4c's own counter (term_density.count_terms: its <main> scope,
    its tokeniser), and each ceiling is that density x the page's own word count from the
    same counter, rounded as block 4c rounds its leader band. `{city}` is the page's own
    city; a page with no city (a national row) has no city ceiling."""
    per = (budgets.get("location_density") or {}).get("per_1000_words") or {}
    names = {t: (city_for(slug) if budgets["terms"].get(t) == CITY_TERM else t) for t in per}
    names = {t: n for t, n in names.items() if n}
    if not names:
        return {}
    import term_density   # lazy: only location pages need block 4c's counter
    r = term_density.count_terms(html, list(names.values()))
    return {t: (r["counts"][n], int(round(per[t] * r["words"] / 1000))) for t, n in names.items()}


def term_budget(html, page_type, budgets, slug=""):
    """[(term, count, ceiling)] for every term over its ceiling. Owner pages are exempt for their term.
    Per-slug override: budgets_by_slug — a number replaces the page-type ceiling, null removes it.
    A location page's head terms with a `location_density` are counted and capped by
    _location_density(); every other term keeps its fixed count and its regex."""
    text = text_of(main_html(html))
    density = _location_density(html, budgets, slug) if page_type == "location" else {}
    ceilings = dict(budgets["budgets"].get(page_type, {}))
    ceilings.update({t: c for t, (_, c) in density.items()})
    # a density term a page cannot resolve (no city on a national row) is still a capped term
    per = (budgets.get("location_density") or {}).get("per_1000_words") or {}
    capped = set(ceilings) | (set(per) if page_type == "location" else set())
    # Per-slug override (breeder, 2026-09-10): a number replaces the page-type ceiling, null removes it.
    overrides = {t: c for t, c in budgets.get("budgets_by_slug", {}).get(slug, {}).items() if not t.startswith("_")}
    for t in overrides:
        if t not in capped:
            print(f"WARN budgets_by_slug[{slug!r}] names {t!r}, which budgets[{page_type!r}] never caps — ignored", file=sys.stderr)
    ceilings = {t: overrides.get(t, c) for t, c in ceilings.items()}
    ceilings = {t: c for t, c in ceilings.items() if c is not None}
    out = []
    for term, ceiling in ceilings.items():
        if term == "scam" and slug in budgets.get("scam_owner", []):
            continue
        if term == "legit" and slug in budgets.get("legit_owner", []):
            continue
        if term in density:
            n = density[term][0]
        else:
            pat = budgets["terms"].get(term, re.escape(term))
            if pat == CITY_TERM:
                city = city_for(slug)
                if city is None:
                    continue
                pat = city_pattern(city)
            n = len(re.findall(pat, text, flags=re.I))
        if n > ceiling:
            out.append((term, n, ceiling))
    return out


# ── title-length-max ────────────────────────────────────────────────────────
def title_too_long(html, budgets, slug=""):
    m = re.search(r"<title>(.*?)</title>", html, flags=re.S | re.I)
    if not m:
        return None
    t = text_of(m.group(1))
    # Per-slug override (breeder, 2026-09-10): the homepage keeps its five-part Rule-21 title.
    limit = budgets.get("title_max_chars_by_slug", {}).get(slug, budgets.get("title_max_chars", 70))
    return (len(t), limit) if len(t) > limit else None


# ── review-attribution-unique ───────────────────────────────────────────────
# Lookahead so nested blocks overlap: a wrapper <div> matching up to the first inner </div> must not
# swallow the <article> that opens inside it (the first grid card on the homepage was skipped that way).
QUOTE_BLOCK = re.compile(r"(?=(<(blockquote|figure|article|li|div)\b[^>]*>(.*?)</\2>))", re.S | re.I)
# The class token must END at a word boundary (`cites-good` / `cites-cross` are not <cite>), and
# `puppy-name` / `inq-price-name` are puppy-card labels, never a reviewer — two cards sharing a paragraph
# with different puppy names produced a fabricated finding.
CITE = re.compile(
    r"<(?:cite|footer|p|span)\b[^>]*class=\"(?![^\"]*(?:puppy-name|price-name))[^\"]*(?:name|author|cite)(?![a-z])[^\"]*\"[^>]*>(.*?)</"
    r"|<cite\b[^>]*>(.*?)</cite>"
    # a testimonial component (project 3) prints the buyer name in a <div class="font-display font-bold|font-semibold …">
    r"|<div\b[^>]*class=\"[^\"]*font-display font-(?:bold|semibold)[^\"]*\"[^>]*>(.*?)</div>", re.S | re.I)
QUOTE_TEXT = re.compile(r"<(blockquote|p)\b[^>]*>(.*?)</\1>", re.S | re.I)
BLOCKQUOTE = re.compile(r"<blockquote\b[^>]*>(.*?)</blockquote>", re.S | re.I)
# how far past a name-less <blockquote> to look for its sibling name element: a Testimonials card's
# rating row + name/location div is a few hundred bytes; 1500 covers it without reaching the next section
FOLLOW_ON_NAME_WINDOW = 1500


def _name(groups):
    # the grid card prints "Name, City, ST" in one element; keep everything before the first comma
    return re.sub(r"\s*,.*$", "", text_of("".join(g or "" for g in groups)))


def _fingerprint(inner, names):
    """The quote is the longest <p>/<blockquote> in the block (a grid card also carries a headline);
    fall back to the whole block text minus any <cite>."""
    quotes = [text_of(q) for _, q in QUOTE_TEXT.findall(inner)]
    body = max(quotes, key=len) if quotes else text_of(re.sub(r"<cite\b.*?</cite>", " ", inner, flags=re.S | re.I))
    body = re.sub(r"\s*(?:" + "|".join(re.escape(n) for n in names) + r")\s*$", "", body)
    return re.sub(r"[^a-z]", "", body.lower())[:80]


def review_attribution(html):
    """[(quote_fingerprint, [names])] where one quote text is credited to 2+ different names."""
    seen = defaultdict(set)
    body_html = main_html(html)
    for blk in QUOTE_BLOCK.finditer(body_html):
        inner = blk.group(3)
        names = [_name(m) for m in CITE.findall(inner)]
        if not names:
            continue
        fp = _fingerprint(inner, names)
        if len(fp) < 20:
            continue
        seen[fp].add(names[0])
    # A <blockquote> with no name inside it (the feature / mosaic testimonial variants keep the
    # name in a sibling element): credit it to the first name element that follows, before the next quote.
    for m in BLOCKQUOTE.finditer(body_html):
        if CITE.search(m.group(1)):
            continue
        # stop at the next quote OR the end of this card: a name-first card (figure > name, blockquote)
        # must not be credited to the NEXT card's name
        tail = re.split(r"<blockquote\b|</(?:figure|article|li)>", body_html[m.end(): m.end() + FOLLOW_ON_NAME_WINDOW], 1)[0]
        nxt = CITE.search(tail)
        if not nxt:
            continue
        name = _name(nxt.groups())
        fp = _fingerprint(m.group(0), [name])
        if not name or len(fp) < 20:
            continue
        seen[fp].add(name)
    return [(fp, sorted(n)) for fp, n in seen.items() if len(n) > 1]


# ── claim-bound-to-proof ────────────────────────────────────────────────────
# A result word in a sentence makes it a RESULT claim, whatever else it does: the words the
# `tests-named-no-result` pattern's own lookahead refuses, plus "certified/certificate" and
# "free of", read over the WHOLE sentence (the pattern's lookahead only reads after its match).
RESULT_WORDS = re.compile(r"\b(?:clear|cleared|clears|passed|negative|normal|unaffected|came\s+back"
                          r"|results?|certified|certificates?|free\s+of)\b", re.I)


def accepted_repeat_rulings(claim, root=ROOT):
    """The rulings that let a NAMING-ONLY ledger row repeat with no proof object, or [].

    A row earns it only with `naming_only: true` AND a non-empty `repeat_ruling` list whose
    every entry is a rulings file in the repository (`path` or `path#qNN`). The breeder's
    rulings for `tests-named-no-result`: answer board 2026-09-29 q01 (name the tests, never
    state a result) and 2026-10-05 london-gate-findings q04 (a) (the check accepts the
    repeats). A ruling path that does not exist voids the acceptance: a typo must not
    silently switch a check off."""
    rulings = claim.get("repeat_ruling") or []
    if claim.get("naming_only") is not True or not rulings:
        return []
    for r in rulings:
        if not (pathlib.Path(root) / r.split("#", 1)[0]).is_file():
            print(f"WARN evidence-ledger row {claim.get('id')!r}: repeat_ruling {r!r} is not a "
                  "file in the repository — the repeat is NOT accepted", file=sys.stderr)
            return []
    return list(rulings)


def _states_result(sentence, ledger):
    dna_clear = (ledger.get("vocabulary") or {}).get("dna-clear")
    return bool(RESULT_WORDS.search(sentence)
                or (dna_clear and re.search(dna_clear, sentence, flags=re.I)))


def claim_binding(html, ledger):
    """[(claim_id, mentions, proof)] for ledger claims made 2+ times whose proof is not linked.

    proof == "NOT FETCHED" rows are returned so the caller can WARN; a linked proof clears the row.
    "Linked" is a substring test on the <main> HTML, not href-only: the proof path appearing in an
    href, src, or data attribute all count.

    A NAMING-ONLY row under a breeder ruling (`accepted_repeat_rulings`) is not a finding when
    every sentence that repeats it only names the tests: naming a test is not a claim that has
    a proof object, by her ruling. The moment one of those sentences states a result (a result
    word anywhere in it, or the ledger's `dna-clear` vocabulary), the acceptance is void and the
    row is judged like any other: a repeated unproven RESULT claim still warns. A row with no
    such ruling, `parents-dna-clear` included, is never excused.
    """
    body = main_html(html)
    text = text_of(body)
    out = []
    for c in ledger["claims"]:
        n = len(re.findall(c["pattern"], text, flags=re.I))
        if accepted_repeat_rulings(c):
            hits = [s for s in sentences(html) for _ in re.finditer(c["pattern"], s, flags=re.I)]
            n = max(n, len(hits))
            if not any(_states_result(s, ledger) for s in hits):
                continue
        if n < 2:
            continue
        proof = c.get("proof") or "NOT FETCHED"
        if proof != "NOT FETCHED" and (proof in body):
            continue
        out.append((c["id"], n, proof))
    return out


# ── claim-unledgered ───────────────────────────────────────────────────────
# A placeholder excuses only the vocabulary it stands in for. No legal vocabulary id exists
# yet, so LEGAL_CLAIM_PLACEHOLDER excuses none of today's ids.
PLACEHOLDER_COVERS = {"LICENCE_CLAIM_PLACEHOLDER": {"licensed-breeder"},
                      "LEGAL_CLAIM_PLACEHOLDER": set()}
# A block ends a sentence even without a full stop: a heading never runs into its paragraph,
# two card <div>s never run together, and an unclosed <li> or a <br> still breaks the line.
BLOCK_BREAK = re.compile(
    r"</(?:p|h[1-6]|li|td|th|dt|dd|figcaption|blockquote|caption|summary|div|section|article)\s*>"
    r"|<br\s*/?>|<(?:li|p|h[1-6]|div)\b[^>]*>", re.I)
CLOSERS = "\"'”’)]"
# A full stop after one of these does not end the sentence.
ABBREVIATIONS = re.compile(r"(?:\b(?:Dr|Mr|Mrs|Ms|St|approx)|\be\.g|\bi\.e)\.$", re.I)
SENTENCE_END = re.compile(r"[.!?][" + re.escape(CLOSERS) + r"]*\s+")
# Not a claim: a denial just before the hit, advice to the buyer, a reference to a page about it.
# Each is judged inside the hit's own clause, so "KC registered — want to know why?" and
# "Ask for details: every pup is KC registered" still claim.
# `without` is not a denial: "No puppy leaves without being vet checked" is a claim; nor is
# "not only" ("Not only KC registered, …").
DENIAL = re.compile(r"\b(?:not|never|no)\b", re.I)
NOT_ONLY = re.compile(r"\bnot\s+only\b", re.I)
ADVICE = re.compile(r"^\W*ask\s+(?:to\s+see|for)\b", re.I)
REFERENCE = re.compile(r"\b(?:page\s+(?:on|for|about)\s+the|results\s+for|more\s+about\s+the)\b", re.I)
QUESTION_WORDS = r"(?:why|how|what|who|when|where|want|is|are|do|does|can|should|would|will)"
# A clause ends at a dash, ; or :, at a question mark (closing quotes allowed), and at a comma
# that opens a question ("…, want to know why?").
CLAUSE_END = re.compile(r"[\u2014\u2013;:]|\?[" + re.escape(CLOSERS) + r"]*"
                        r"|,(?=\s*" + QUESTION_WORDS + r"\b)", re.I)


def _split_sentences(text):
    out, start = [], 0
    for m in SENTENCE_END.finditer(text):
        head = text[start:m.start() + 1]
        if m.group(0)[0] == "." and ABBREVIATIONS.search(head):
            continue
        out.append(text[start:m.end()].strip())
        start = m.end()
    out.append(text[start:].strip())
    return [s for s in out if s]


def sentences(html):
    """The sentences of <main>, split at block boundaries and at . ! ? (a closing quote or
    bracket may follow; Dr. / e.g. / approx. and the like do not end one) — script/style dropped."""
    body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", main_html(html), flags=re.S | re.I)
    # An inline <span> breaks no word: the city components wrap a test name or a price in one so it
    # never breaks across a line (src/lib/cityKit.ts `keepRuns`), and a reader meets "HC-HSF4," with
    # no space before the comma. Read as a space, a ledger row spelled to the sentence never matched
    # it (Manchester, Phase F Task 32 follow-up).
    body = re.sub(r"</?span\b[^>]*>", "", body, flags=re.I)
    out = []
    for block in BLOCK_BREAK.split(body):
        out += _split_sentences(text_of(block))
    return out


def _clause(s, pos):
    """(start, clause text) of the clause of sentence `s` holding position `pos`."""
    start = 0
    for m in CLAUSE_END.finditer(s):
        if m.end() > pos:
            return start, s[start:m.end()]
        start = m.end()
    return start, s[start:]


def _is_claim(s, m):
    """A vocabulary match `m` in sentence `s` is a claim unless, within its own clause, it sits
    in a question, is buyer advice, follows a denial within three words (not across a comma;
    "not only" is no denial), or is the object of a reference to a page about it."""
    start, clause = _clause(s, m.start())
    if clause.rstrip().rstrip(CLOSERS).endswith("?") or ADVICE.search(clause):
        return False
    before = s[start:m.start()]
    if REFERENCE.search(" ".join(before.split()[-6:])):
        return False
    near = NOT_ONLY.sub(" ", before.rsplit(",", 1)[-1])
    return not DENIAL.search(" ".join(near.split()[-3:]))


def unledgered_claims(html, ledger):
    """[(vocabulary id, sentence)] — one row per vocabulary id a sentence claims that no ledger
    row covers. A ledger row clears a hit only when its pattern matches the same sentence AND its
    `covers` list names that vocabulary id. A placeholder excuses only its own id. A ledger with
    no `vocabulary` checks nothing."""
    vocab = ledger.get("vocabulary") or {}
    if not vocab:
        return []
    out = []
    for s in sentences(html):
        covered = set()
        for c in ledger.get("claims", []):
            if c.get("covers") and re.search(c["pattern"], s, flags=re.I):
                covered.update(c["covers"])
        for ph, ids in PLACEHOLDER_COVERS.items():
            if ph in s:
                covered |= ids
        for vid, pat in vocab.items():
            if vid in covered:
                continue
            if any(_is_claim(s, m) for m in re.finditer(pat, s, flags=re.I)):
                out.append((vid, s))
    return out


PREVIEW_PREFIXES = ("board-preview", "kit-preview")


def is_preview(slug):
    """board-preview/* and kit-preview render fixtures and board demos, not site copy."""
    first = slug.strip("/").split("/", 1)[0]
    return first in PREVIEW_PREFIXES


def is_new_page(slug, page_type, rebuilt):
    """A page project 5 builds: a location, comparison or blog page whose bare slug is in
    data/facts/rebuilt.json and is not one of family_rules' twelve frozen pages. The type
    list and the frozen test are family_rules' own (NEW_FAMILY_PAGE_TYPES, is_new_page), so
    the audit and the board gate answer the same question."""
    import family_rules as FR   # lazy: only the audit's main path needs it
    bare = slug.strip("/").rsplit("/", 1)[-1]
    return (page_type in FR.NEW_FAMILY_PAGE_TYPES and bare in rebuilt
            and FR.is_new_page(bare))


def rebuilt_slugs(path=REBUILT_PATH):
    """The bare slugs in data/facts/rebuilt.json; empty when the file is absent or unreadable
    (no page is then new, so claim-unledgered only WARNs)."""
    try:
        rows = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"WARN evidence-audit: rebuilt list unreadable at {path} ({e.__class__.__name__}) — "
              "no page counts as new, so claim-unledgered only WARNs", file=sys.stderr)
        return set()
    return {r for r in rows if isinstance(r, str)} if isinstance(rows, list) else set()


# ── statement-labels-present ────────────────────────────────────────────────
# `\sid=` not `\bid=`: `\b` also matches inside `data-id=`
SECTION = re.compile(r"<section\b[^>]*\sid=[\"']([^\"']+)[\"'][^>]*>(.*?)</section>", re.S | re.I)


def missing_statement_labels(html):
    """Section ids whose text carries a species/health fact signal but no .stmt-label. PROXY."""
    out = []
    for sid, inner in SECTION.findall(main_html(html)):
        if FACT_SIGNAL.search(text_of(inner)) and "stmt-label" not in inner:
            out.append(sid)
    return out


# ── no-not-fetched-in-prose ─────────────────────────────────────────────────
def not_fetched_in_prose(html):
    return len(re.findall(r"NOT FETCHED", text_of(main_html(html))))


# ── no-unsourced-superlatives ───────────────────────────────────────────────
def unsourced_superlatives(html, budgets):
    """Superlatives from budgets["superlatives"] with no link in the same sentence. PROXY: any href in
    the sentence clears it, whether or not that link is the source. <script>/<style> are stripped
    first so JSON-LD descriptions do not count as prose."""
    out = []
    body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", main_html(html), flags=re.S | re.I)
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", unescape(body)))
    for s in sentences:
        plain = text_of(s).lower().replace("\u2019", "'")
        for sup in budgets.get("superlatives", []):
            if sup in plain and "href=" not in s:
                out.append(sup)
    return out


# ── the audit ───────────────────────────────────────────────────────────────
def audit(slug, html, page_type, budgets, ledger, new_page=False):
    f = []
    for term, n, cap in term_budget(html, page_type, budgets, slug):
        f.append(("ERROR", f"term budget: {term} x{n} in <main>, ceiling {cap} for {page_type}"))
    t = title_too_long(html, budgets, slug)
    if t:
        f.append(("ERROR", f"<title> is {t[0]} chars, ceiling {t[1]}"))
    for fp, names in review_attribution(html):
        f.append(("ERROR", f"same review text credited to {' / '.join(names)} (fingerprint {fp[:24]}…)"))
    for cid, n, proof in claim_binding(html, ledger):
        if proof == "NOT FETCHED":
            f.append(("WARN", f"claim '{cid}' made {n}x; proof object NOT FETCHED — say it once and link the trust section"))
        else:
            f.append(("ERROR", f"claim '{cid}' made {n}x without linking its proof {proof}"))
    for vid, sentence in ([] if is_preview(slug) else unledgered_claims(html, ledger)):
        f.append(("ERROR" if new_page else "WARN",
                  f"un-ledgered claim ({vid}): \"{sentence[:120]}\" — add its row to "
                  "data/quality/evidence-ledger.json (proof NOT FETCHED until the document is "
                  "on file) or write the claim placeholder"))
    for sid in missing_statement_labels(html):
        f.append(("WARN", f"section #{sid} carries species/health facts with no statement label (PROXY — read it)"))
    nf = not_fetched_in_prose(html)
    if nf:
        f.append(("ERROR", f"'NOT FETCHED' appears {nf}x in visible text"))
    for sup in unsourced_superlatives(html, budgets):
        f.append(("WARN", f"unsourced superlative: '{sup}' (source it in the same sentence or cut it)"))
    return f


def page_type_for(slug):
    """targets.json first; then a path heuristic; 'interior' as the fallback."""
    try:
        for p in json.loads(TARGETS_PATH.read_text(encoding="utf-8"))["pages"]:
            if p["slug"] == slug:
                return p["page_type"]
    except Exception:
        pass
    if slug == "index":
        return "home"
    if slug.startswith("available-puppies/"):
        return "puppy"
    if slug in ("available-puppies", "uk-locations", "blog"):
        return "hub"
    if slug.startswith("uk-locations/"):
        return "location"
    if "-vs-" in slug or slug.endswith("-comparison"):
        return "comparison"
    if slug.startswith("blue-staffy-blog") or slug.startswith("blog/"):
        return "blog"
    if slug in ("buy-blue-staffy-puppies-uk", "blue-staffy-pup-sale-uk",
                "buy-staffy-puppies-for-sale-uk"):
        return "for-sale"
    return "interior"


PAGE_TYPES = ["home", "for-sale", "puppy", "comparison", "location", "interior",
              "blog", "hub"]
DEFAULT_JSON = ROOT / "docs/reports/evidence_audit.json"
DIST = ROOT / "dist"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1])
    ap.add_argument("slugs", nargs="*", help="audit these slugs (`index` = the homepage)")
    ap.add_argument("--all", action="store_true", help="audit every built page")
    ap.add_argument("--dist", default=str(DIST), help="dist root to audit")
    ap.add_argument("--budgets", default=str(BUDGETS_PATH),
                    help=f"evidence budgets JSON (default {BUDGETS_PATH})")
    ap.add_argument("--ledger", default=str(LEDGER_PATH),
                    help=f"verified-claim ledger JSON (default {LEDGER_PATH})")
    ap.add_argument("--type", default=None, choices=PAGE_TYPES,
                    help="override the page type for every slug given")
    ap.add_argument("--rebuilt", default=str(REBUILT_PATH),
                    help="data/facts/rebuilt.json: which pages are new (claim-unledgered ERRORs there)")
    ap.add_argument("--fail-on-error", action="store_true",
                    help="also exit non-zero when only WARN-level findings were made")
    ap.add_argument("--json", nargs="?", const=str(DEFAULT_JSON), default=None,
                    metavar="PATH",
                    help=f"write the machine-readable result (default {DEFAULT_JSON})")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    for path, what in ((pathlib.Path(a.budgets), "evidence budgets"),
                       (pathlib.Path(a.ledger), "claim ledger")):
        if not path.exists():
            print(f"evidence-audit: {what} missing at {path} — Task 9 writes it. "
                  "A gate with no budget file cannot run; that is not a pass.")
            return 2
    budgets = json.loads(pathlib.Path(a.budgets).read_text(encoding="utf-8"))
    ledger = json.loads(pathlib.Path(a.ledger).read_text(encoding="utf-8"))
    dist = pathlib.Path(a.dist)
    if a.all:
        paths = sorted(dist.glob("**/index.html"))
    else:
        paths = [_dist_path(s, dist) for s in a.slugs]
    paths = [p for p in paths if p.exists()]
    if not paths:
        print("evidence-audit: 0 pages matched — that is not a pass")
        return 1
    rebuilt = rebuilt_slugs(a.rebuilt)
    errs = warns = 0
    report = []
    for p in paths:
        slug = page_key(p, dist)
        pt = a.type or page_type_for(slug)
        html = p.read_text(encoding="utf-8", errors="ignore")
        f = audit(slug, html, pt, budgets, ledger, new_page=is_new_page(slug, pt, rebuilt))
        e = sum(1 for s, _ in f if s == "ERROR")
        errs += e
        warns += len(f) - e
        print(f"\n== {slug}  [{pt}]  {e} ERROR / {len(f) - e} WARN")
        for sev, msg in f:
            print(f"  {sev:5s} {msg}")
        report.append({"slug": slug, "page_type": pt,
                       "findings": [{"severity": s, "message": m} for s, m in f]})
    print(f"\nexamined {len(paths)} pages; {errs} problems ({warns} WARN)")
    if a.json:
        out = pathlib.Path(a.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"pages": report, "errors": errs, "warns": warns},
                                  indent=2) + "\n", encoding="utf-8")
        print(f"JSON report → {out}")
    return 1 if errs or (a.fail_on_error and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
