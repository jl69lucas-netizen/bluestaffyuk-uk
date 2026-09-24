#!/usr/bin/env python3
"""pageboard — the Page Board library. Every board CLI imports this; it reads files and
computes, it never writes a board or publishes anything (the CLIs do).
Spec: docs/superpowers/specs/2026-09-12-page-board-system-design.md
"""
import functools, hashlib, json, pathlib, re, sys
import jsonschema

# The header pre-check must judge a heading the way `dup_content_audit.py --headers`
# will judge it after the build, so it borrows that module's chrome rules rather than
# growing a second copy that drifts. It lives beside this file in scripts/.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import dup_content_audit as DUP
HEADER_WHITELIST = DUP.HEADER_WHITELIST   # phrases the dup gate already forgives
PUPPY_CARD_HEADINGS = DUP.PUPPY_CARD_HEADINGS  # whole headings: a puppy card's name
HEAD_TERMS = DUP.HEAD_TERMS               # and the phrases every for-sale page must be free to write

# `dropped-vs-verbatim` reads the front of a `dropped` line, and it must read it the SAME way
# the gate that EXCUSES a claim with that line reads it — a fragment split differently in two
# places is a record that is dropped over here and carried over there. So the splitter is
# borrowed rather than copied, exactly as the header rules above are.
import facts_preserved_check as FACTS
import family_rules as FR
_DROP_SPLIT = FACTS._DROP_SPLIT

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
ONTOLOGY = ROOT / "data" / "bsuk-ontology.json"
LEDGER = ROOT / "data" / "component-ledger.json"
BUDGETS = ROOT / "data" / "quality" / "evidence-budgets.json"
EXTERNAL_LIBRARY = ROOT / "docs" / "reference" / "external-link-library.md"
_LIB_URL = re.compile(r"https?://[^\s`|)>\"']+")
DIST = ROOT / "dist"
DESC_MIN, DESC_MAX = 140, 160
DEFAULT_TITLE_MAX = 70


class BoardError(Exception):
    """A record that does not describe a buildable page."""


def _read_json(path):
    """Read a JSON file, reporting a malformed one as a BoardError like every other fault."""
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BoardError(f"{path}: {e}") from None


def _validate(doc, schema_name):
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    try:
        jsonschema.validate(doc, schema)
    except jsonschema.ValidationError as e:
        path = "/".join(str(p) for p in e.absolute_path) or "(root)"
        raise BoardError(f"{schema_name}: {path}: {e.message}") from None


def normalise_url(url):
    """One spelling for comparing a recorded href against a library row: scheme and host
    lowercased, a leading `www.` dropped, trailing slash and punctuation trimmed. `www.`
    goes because the library records `https://www.cites.org/eng/app/appendices.php` while
    the live pages link `https://cites.org/...` — one row, and a checker calling them two
    would send an author to add a row that is already there."""
    u = url.strip().rstrip(".,;")
    m = re.match(r"^(https?)://([^/]+)(.*)$", u, re.I)
    if not m:
        return u.lower()
    host = m.group(2).lower()
    host = host[4:] if host.startswith("www.") else host
    return f"{m.group(1).lower()}://{host}{m.group(3).rstrip('/')}"


@functools.lru_cache(maxsize=8)
def _library_urls(path, _mtime):
    p = pathlib.Path(path)
    return frozenset(normalise_url(u) for u in _LIB_URL.findall(p.read_text(encoding="utf-8")))


def library_urls(path=None):
    """Every URL docs/reference/external-link-library.md records, normalised. Grepped, not
    parsed: the library is three table shapes plus a prose citation block, and all of them
    write the URL plainly. Missing file → empty set, and validate_board then skips the
    membership rule: an absent library is a tooling fault, not a bad record.

    Read once per (path, mtime): validate_board asks for the whole set on every record, and
    the near-me grid alone would otherwise re-read an 87-line file 30 times. Keying on the
    mtime rather than the path alone means an edited library is picked up in-process, which
    is what the link agent does while it is adding a row.

    The default is resolved at CALL time, not bound at import, so a caller (the board tests)
    can repoint `PB.EXTERNAL_LIBRARY` at a fixture and have it take effect."""
    p = pathlib.Path(EXTERNAL_LIBRARY if path is None else path)
    if not p.exists():
        return frozenset()
    return _library_urls(str(p), p.stat().st_mtime_ns)


def validate_board(board):
    _validate(board, "board.schema.json")
    ids, ns = [], []
    for sec in board["sections"]:
        if sec["words"]["min"] > sec["words"]["max"]:
            raise BoardError(f"section {sec['id']}: words.min {sec['words']['min']} > words.max {sec['words']['max']}")
        if sec["category"] == "C" and sec["group"] != "SUGGESTED-RECOMMENDED":
            # The pipeline review defines C as "the sections that are ours alone" — the one
            # letter with a written meaning, so the one mapping the record may not contradict.
            raise BoardError(f"section {sec['id']}: category C is a section that is ours alone, so its group is "
                             f"SUGGESTED-RECOMMENDED, not {sec['group']}")
        if sec["group"] == "COMPETITOR-BASED" and not re.search(r"https?://[^\s/]+\.[^\s/]+", sec["why_source"]):
            raise BoardError(f"section {sec['id']}: a COMPETITOR-BASED section cites the competitor it answers — "
                             "why_source carries no URL")
        # A table is the one section whose CONTENT has a shape the schema cannot state: JSON
        # Schema can hold every row to 2-6 cells, but not to the same count as THIS table's
        # own columns. A short row is a cell DataTable never renders and a reader never sees;
        # an over-long one is a cell with no column name to put in its `data-label`, which is
        # an unlabelled block once the table stacks. Both are a silently truncated table
        # rather than a refused record.
        tbl = sec.get("table")
        if tbl:
            width = len(tbl["columns"])
            bad = [i for i, row in enumerate(tbl["rows"]) if len(row) != width]
            if bad:
                raise BoardError(f"section {sec['id']}: table row(s) {', '.join(str(i) for i in bad)} do not carry "
                                 f"{width} cells, one per column ({', '.join(tbl['columns'])})")
            over = [i for i in tbl.get("numeric", []) if i >= width]
            if over:
                raise BoardError(f"section {sec['id']}: table.numeric names column "
                                 f"{', '.join(str(i) for i in over)} — there are only {width}")
        ids.append(sec["id"])
        ns.append(sec["n"])
    for label, values in (("id", ids), ("n", ns)):
        dupes = sorted({v for v in values if values.count(v) > 1})
        if dupes:
            raise BoardError(f"duplicate section {label}: {', '.join(str(d) for d in dupes)}")
    nl = board["tuple"]["newsletter"]
    if bool(nl["after"]) != bool(nl["variant"]):
        raise BoardError("tuple.newsletter: `after` and `variant` are set together or not at all "
                         f"(after={nl['after']!r}, variant={nl['variant']!r})")
    if nl["after"] and nl["after"] not in ids:
        raise BoardError(f"tuple.newsletter.after {nl['after']!r} is not a section id ({', '.join(ids)})")
    brief = board["brief"]
    names = [a["name"] for a in brief["angles"]]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise BoardError(f"duplicate angle name: {', '.join(dupes)}")
    chosen = brief["strategy"]["name"]
    if chosen not in names:
        # The two fields are one decision written twice. Left free to disagree, the table
        # becomes decoration: still rendered, still read as considered, still describing a
        # page nobody is building.
        raise BoardError(f"brief.strategy.name {chosen!r} is not one of the angles considered "
                         f"({', '.join(names)})")
    for a in brief["angles"]:
        if a["name"] != chosen and not a["why_not"].strip():
            raise BoardError(f"angle {a['name']!r} was not taken and records no why_not")
    cad = brief["cta"]["cadence"]
    if cad["min"] > cad["max"]:
        raise BoardError(f"brief.cta.cadence: min {cad['min']} > max {cad['max']}")
    if not any(s.get("cta", 0) for s in board["sections"]):
        raise BoardError("no section carries a CTA — a transactional page with a CTA plan places at least one")
    tool = brief["tool"]
    if tool["pick"].strip().lower() != "none" and not tool["trade_off"].strip():
        raise BoardError(f"brief.tool: {tool['pick']!r} is a real tool and records no trade_off (§14)")
    sch = brief["schema"]
    types = set(sch["types"])
    need = {"product-offer-per-puppy": {"Product", "Offer"}, "aggregate-offer": {"AggregateOffer"}, "none": set()}[sch["offer_model"]]
    if not need <= types:
        raise BoardError(f"brief.schema: offer_model {sch['offer_model']} needs {', '.join(sorted(need - types))} in types")
    if sch["offer_model"] == "none" and types & {"Offer", "AggregateOffer"}:
        raise BoardError("brief.schema: offer_model none, but types name an Offer — a page that sells nothing marks up no offer")
    lib = library_urls()
    if lib:
        for sec in board["sections"]:
            for l in sec["links"]["external"]:
                if normalise_url(l["href"]) not in lib:
                    raise BoardError(f"section {sec['id']}: external href {l['href']} is not in "
                                     "docs/reference/external-link-library.md — add the row and verify 200 first")


def validate_ontology(ont):
    _validate(ont, "ontology.schema.json")


TUPLE_ID_KEYS = ("hero", "dial", "rail", "toc", "table", "faq")


def tuple_component_ids(t):
    """Every component id a ledger/board tuple names, in a fixed order."""
    return [t[k] for k in TUPLE_ID_KEYS if t.get(k)] + list(t.get("takeaway", []))


def validate_ledger(ledger):
    _validate(ledger, "component-ledger.schema.json")
    # `#refresh` is the board's placeholder for "reuse this shell along an axis you have
    # not named yet". It may appear in a candidate list; recording one in the ledger would
    # claim a delta that does not exist, so the author must rename it before it lands.
    for page, t in ledger.get("pages", {}).items():
        for cid in tuple_component_ids(t):
            if cid.endswith("#refresh"):
                raise BoardError(
                    f"{page}: {cid} is the unnamed refresh placeholder — rename it to base#<delta> before recording it")


# Mirrors schemas/board.schema.json's meta.slug pattern. BSUK routes nest
# (`available-puppies/roman`), so a slug is one or more `[a-z0-9-]` segments joined by
# single slashes: no leading or trailing slash, no empty segment, no traversal.
#
# A leading underscore on the FIRST segment marks a record that is not a page: `_demo` is
# the fixture the board-preview route, the cutter and their tests render, and no real slug
# has ever started with one. It is inside the pattern rather than special-cased at the call
# sites, so such a record still flattens to a filename, still validates, and still may not
# contain `--`.
SLUG = re.compile(r"^_?[a-z0-9-]+(/[a-z0-9-]+)*$")


def slug_file(slug):
    """A slug -> the filename stem that holds its record, `/` flattened to `--`.

    Written once and used by every caller that names a per-slug file, so the board, its
    inbox and its canvas directory can never disagree about the spelling.

    The slug is validated first: a path built from an unchecked slug (`../x`, `/abs`)
    reads a file the caller never named. A segment may not itself contain `--`, because
    `a--b` and `a/b` would then flatten to the same file — the mapping has to be
    collision-free in both directions for `--` to be readable as a path separator."""
    if not isinstance(slug, str) or not SLUG.match(slug):
        raise BoardError(f"not a slug: {slug!r} — expected [a-z0-9-] segments joined by '/'")
    if "--" in slug:
        raise BoardError(f"not a slug: {slug!r} — a segment may not contain '--', which is "
                         "how a nested slug is spelled in a filename")
    return slug.replace("/", "--")


def board_path(slug):
    return ROOT / "data" / "boards" / (slug_file(slug) + ".json")


def load_board(slug):
    p = board_path(slug)
    if not p.exists():
        raise BoardError(f"no board for {slug}: {p} does not exist")
    board = _read_json(p)
    validate_board(board)
    return board


def save_board(slug, board):
    validate_board(board)
    if board["meta"]["slug"] != slug:
        raise BoardError(f"slug mismatch: saving as {slug} but the record says {board['meta']['slug']}")
    p = board_path(slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_ontology():
    if not ONTOLOGY.exists():
        raise BoardError(f"no ontology: {ONTOLOGY} does not exist")
    ont = _read_json(ONTOLOGY)
    validate_ontology(ont)
    return ont


def load_ledger():
    if not LEDGER.exists():
        raise BoardError(f"no component ledger: {LEDGER} does not exist")
    ledger = _read_json(LEDGER)
    validate_ledger(ledger)
    return ledger


LIFECYCLE_ASSET_KEYS = ("status", "file")


def record_hash(board, legacy_dropped=False):
    """sha256 of the record's CONTENT, keys sorted. Five fields are excluded because they
    are lifecycle state rather than content, and they move after approval by design:
    the top-level `approval`, `meta.status` (board_approve.py flips it to "approved"
    the moment it stamps the hash), every asset's `status` and `file` (baking a photo
    fills them in), and the top-level `dropped`. Hashing any of them would make every
    legitimate approval, every later bake, and every completed drop-list read as a
    post-approval edit. An edit anywhere else DOES change the hash, which is how a real
    post-approval edit sends the page back to the board.

    WHY `dropped` IS LIFECYCLE AND NOT CONTENT (project 4, 2026-09-20 review). It is the
    accounting of what the rebuild did NOT carry, and it cannot be complete before the
    rebuild exists — which is after approval, by construction. The breeder approves an
    OUTLINE: headings, styles, links, an H1 and a meta set. Nothing on the board asks them
    which sentence of the migrated body the writer will find no room for; that is discovered
    at P5 and reported by scripts/facts_preserved_check.py, and `dropped` is where the answer
    is written down with its reason. Hashing it made the `text` kind unusable on every
    approved record — the only way to record a dropped claim would have been to re-board a
    page the breeder had already signed off, or to re-stamp the hash by hand, which is
    forging an approval. `assets[].status` and `.file` are excluded on exactly this argument
    and have been since the first board: a field the pipeline fills in after approval is not
    a choice the approval covered. The drop list is still content in every other sense —
    board_gate and facts_preserved_check both read it, the schema requires a reason on every
    line, and the gate report prints it per page.

    `verbatim` (working rule 15) is excluded on the identical argument and named separately
    only so the reasoning is not inherited by accident: it is the list of verbatim-set
    elements the rewrite could not carry word for word, which is discovered while the prose
    is being written — after approval, by construction — and hashing it would make recording
    one reworded heading read as a post-approval edit of the outline. It is not in the
    `legacy_dropped` reading because no record approved before rule 15 has the key at all,
    so both readings of an old record are unchanged by its exclusion."""
    skip = ("approval", "verbatim") if legacy_dropped else ("approval", "dropped", "verbatim")
    body = {k: v for k, v in board.items() if k not in skip}
    meta = body.get("meta")
    if isinstance(meta, dict):
        body["meta"] = {k: v for k, v in meta.items() if k != "status"}
    assets = body.get("assets")
    if isinstance(assets, list):
        body["assets"] = [
            {k: v for k, v in a.items() if k not in LIFECYCLE_ASSET_KEYS} if isinstance(a, dict) else a
            for a in assets
        ]
    blob = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def record_hash_bare(board, clear_notes=True):
    """The hash the record carried BEFORE an approval wrote the breeder's choices into it:
    every `sections[].options.pick` back to null, every `.note` back to "", `h1.pick` back
    to null. board_approve.py accepts an inbox that matches this, the same with the notes
    left alone, or the record as it stands, so re-running one approval twice is idempotent
    instead of reading as a post-approval edit. Nothing else is reset: a heading the breeder
    changed after the fact moves every hash, which is the edit the gate exists to catch.

    `clear_notes=False` is the second reading, and it is not optional dressing: an outline
    may SHIP with notes (the thank-you and contact records do — the note explaining which
    review fills the single slot was written by the outline author, not the breeder), and
    an approval that carries those notes back unchanged left them exactly as it found them.
    Clearing them invents a record that never existed, and re-approving either of those two
    records was refused as a post-approval edit because of it."""
    b = json.loads(json.dumps(board))
    # The tuple is one of those choices from project 4 on: board_approve.py reads the seven
    # component axes off the picks. It stamps the authored tuple into `approval.tuple_before`
    # so the derivation can be undone here — restoring it is what keeps re-approving an
    # already-approved record idempotent. A record whose approval predates the stamp has no
    # derived tuple to undo, so the tuple it carries IS the authored one.
    prior = b.get("approval")
    if isinstance(prior, dict) and isinstance(prior.get("tuple_before"), dict):
        b["tuple"] = prior["tuple_before"]
    for s in b.get("sections", []):
        if isinstance(s.get("options"), dict):
            s["options"]["pick"] = None
            if clear_notes:
                s["options"]["note"] = ""
    if isinstance(b.get("h1"), dict):
        b["h1"]["pick"] = None
    ms = b.get("meta_set")
    if isinstance(ms, dict) and isinstance(ms.get("pick"), dict):
        ms["pick"] = {"title": None, "description": None}
    return record_hash(b)


def pre_approval_hashes(board):
    """Every hash an approval of THIS record may legitimately carry: the record as it
    stands (an approval already applied), and the two readings of the record as it stood
    before one was — notes cleared, and notes left as the outline author wrote them.
    One source of truth for board_approve.py's acceptance test and its tests."""
    return {record_hash(board),
            record_hash(board, legacy_dropped=True),
            record_hash_bare(board, clear_notes=True),
            record_hash_bare(board, clear_notes=False)}


def approval_matches(board):
    """True when the approval on the record covers the record as it stands.

    `legacy_dropped` is a ONE-TIME compatibility reading, not a loosening. The three records
    approved before 2026-09-20 carry a hash computed when `dropped` was still inside it, so
    every one of them would read as edited the moment the exclusion above landed — and the
    fix for that cannot be "re-stamp the hash", which is the one thing this function exists
    to make impossible. Accepting the old formula keeps those three stamps exactly as the
    breeder left them and changes nothing about what a POST-approval edit does: an edit to
    any hashed field still moves both hashes and still fails. It can be deleted once every
    record has been approved under the new formula."""
    a = board.get("approval")
    if not isinstance(a, dict):
        return False
    return a.get("record_hash") in (record_hash(board), record_hash(board, legacy_dropped=True))


def base_of(component_id):
    """The shell an id names: `base` itself, or the `base` of a `base#delta` refresh."""
    return component_id.strip().split("#", 1)[0]


# A ledger page "owns" every component named anywhere in its tuple. A hero, dial, rail,
# TOC, table, FAQ shell or takeaway a sibling owns is removed from the pool; the record
# keeps who owned it so the board can say so. The page itself never excludes itself.
# A spent shell is not gone, it is refreshed: an owned base comes back as `base#refresh`,
# a placeholder the board author renames to the axis it actually varies, and a refreshed
# id owns its base as well as itself, so a non-empty pool never offers an empty menu.
def owned_components(ledger, exclude_slug=None):
    owned = {}

    def claim(component_id, page):
        for key in dict.fromkeys((component_id, base_of(component_id))):
            if page not in owned.setdefault(key, []):
                owned[key].append(page)

    for page, t in ledger.get("pages", {}).items():
        if page == exclude_slug:
            continue
        for cid in tuple_component_ids(t):
            claim(cid, page)
    return owned


# A section shape normally draws from the pool of its own name. `nav` is the exception:
# a nav-shaped section is a table of contents, and the TOC shells live in the `toc` pool
# (the `nav` pool is the dials and rails, which are page chrome, not section options).
SHAPE_POOL = {"nav": "toc"}


def candidates_for(shape, ledger, slug):
    """The options a section of this shape may be offered.

    Most pools are SHARED: dial-1-clay is on nine pages by design, and the ledger's
    discipline is that the COMBO differs, not the component. Only the pools listed in
    `refresh_pools` are scarce enough that a sibling's claim costs the shell — there a
    spent base comes back as `base#refresh` for the author to rename."""
    if shape == "standard":
        return [], []
    pool_name = SHAPE_POOL.get(shape, shape)
    pool = list(ledger.get("pools", {}).get(pool_name, []))
    if pool_name not in ledger.get("refresh_pools", []):
        return pool, []
    owned = owned_components(ledger, exclude_slug=slug)
    cands, excluded = [], []
    for c in pool:
        base = base_of(c)
        owners = owned.get(base)
        if owners:
            cands.append(f"{base}#refresh")
            excluded.append({"component": base, "owner": owners[0], "owners": list(owners)})
        else:
            cands.append(c)
    return cands, excluded


def spent_h6_prefixes(ledger, exclude_slug=None):
    """{prefix: [owner, ...]} in ledger order. Owner LISTS, like owned_components(): two
    pages can already spend one prefix, and a report that named only the first would
    understate what a third page has to rename."""
    out = {}
    for page, t in ledger.get("pages", {}).items():
        if page == exclude_slug:
            continue
        for p in t.get("h6_prefixes", []):
            if page not in out.setdefault(p, []):
                out[p].append(page)
    return out


TOKEN = re.compile(r"[a-z0-9$']+")
# Tokens a heading template swaps between otherwise-identical siblings, so that
# "Blue Staffy Puppies in Leeds" and "Blue Staffy Puppies in Hull" are caught as a
# template-for-template collision, not just as exact matches. On CAG this was the
# species list; here it is coat colour and sex, which are the only words that vary
# across the puppy and location clusters.
COAT = re.compile(r"\b(blue|black|brindle|red|fawn|white|lilac)\b")
SEX = re.compile(r"\b(male|female|dog|bitch)\b")
SPECIES = re.compile("|".join((COAT.pattern, SEX.pattern)))
SHINGLE = 5
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


def tokens(text):
    """The dup auditor's tokeniser, plus one normalisation it does not need: a curly
    apostrophe is folded to a straight one, so "Staffy’s" and "Staffy's" are one token."""
    return TOKEN.findall(text.replace("’", "'").lower())


def picked_h1(board):
    """The H1 the page will actually render: the breeder's pick, else the recommendation."""
    h1 = board["h1"]
    i = h1["recommended"] if h1.get("pick") is None else h1["pick"]
    return h1["variants"][i]


def title_ceiling(slug):
    """The evidence audit's sitewide `title_max_chars`, unless `title_max_chars_by_slug`
    raises it for this page. Read from the budgets file so the number moves in one place;
    falls back rather than raising, because a missing budgets file must not be the reason a
    board cannot be gated."""
    try:
        b = _read_json(BUDGETS)
    except (BoardError, OSError):
        return DEFAULT_TITLE_MAX
    return int(b.get("title_max_chars_by_slug", {}).get(slug, b.get("title_max_chars", DEFAULT_TITLE_MAX)))


def meta_pick(board):
    """(title, description) the page will actually render: the breeder's picks, else the
    recommendations — the same fallback picked_h1() uses, so the board, the gate and the
    build all read one pair of strings."""
    ms = board["meta_set"]
    ti = ms["recommended"]["title"] if ms["pick"]["title"] is None else ms["pick"]["title"]
    di = ms["recommended"]["description"] if ms["pick"]["description"] is None else ms["pick"]["description"]
    return ms["titles"][ti], ms["descriptions"][di]


def all_headings(board):
    """(level, text) in render order: the picked H1, then each H2 and its tree, depth-first."""
    out = [(1, picked_h1(board))]

    def walk(nodes):
        for n in nodes:
            out.append((n["level"], n["heading"]))
            walk(n.get("children", []))
    for s in board["sections"]:
        out.append((2, s["heading"]))
        walk(s["tree"])
    return out


#: The shortest `dropped` fragment that may be reported as colliding with carried wording.
#: The same floor, and the same reasoning, as `facts_preserved_check.MIN_DROP_PHRASE`: below
#: about twelve characters a fragment stops naming one sentence and starts matching any
#: sentence with those words in it, and a gate that fires on "the puppy" is a gate nobody can
#: act on. The two constants are kept equal deliberately — a fragment too short to EXCUSE a
#: claim over there is too short to ACCUSE a record over here.
MIN_DROP_FRAGMENT = 12

#: A `dropped` line may quote MORE THAN ONE run of the migrated body, joined by an ellipsis —
#: the records' own convention for "these two sentences go together and the words between them
#: are not the point". Each quoted run is judged on its own, because a line whose FIRST run is
#: carried and whose second is not is exactly the defect this check exists to find: the whole
#: fragment matches nothing, every gate is satisfied, and the page renders the first sentence
#: under a board that says it was struck. Both the real ellipsis and three full stops count.
_DROP_ELLIPSIS = re.compile(r"\s*(?:…|\.\.\.)\s*")

#: `dropped` kinds whose lines quote page PROSE. `links`, `prices` and `names` quote a url, an
#: amount and a proper noun, all of which legitimately appear in wording the page carries —
#: a record drops the £850 band and still prints "£1,500", and it drops a location page's url
#: and still names the town. Only `text` lines quote sentences, so only `text` is judged.
_DROP_PROSE_KINDS = ("text",)


def carried_wording(board):
    """[(where, text)] — every string on this record that the page must render word for word.

    Working rule 15's set as the RECORD holds it: each section's heading and its carried
    opening, and the same pair on every tree node at every depth. The FAQ rows are not here
    and are not this function's business — they live in data/faq.json, a different record with
    its own review, and a `dropped` line quoting one would be quoting somebody else's file.
    """
    out = []

    def walk(sid, nodes, path):
        for i, n in enumerate(nodes):
            at = f"{path}[{i}]"
            if n.get("heading"):
                out.append((f"{sid} {at} heading", n["heading"]))
            if n.get("verbatim_opening"):
                out.append((f"{sid} {at} opening", n["verbatim_opening"]))
            walk(sid, n.get("children") or [], f"{at}.children")
    for s in board["sections"]:
        if s.get("heading"):
            out.append((f"{s['id']} heading", s["heading"]))
        if s.get("verbatim_opening"):
            out.append((f"{s['id']} opening", s["verbatim_opening"]))
        walk(s["id"], s.get("tree") or [], "tree")
    return out


def dropped_vs_verbatim(board):
    """[{kind, fragment, where}] — every `dropped.text` fragment the record ALSO carries.

    A `dropped` line is "<the fact> — <the reason it is not carried>", so the fragment judged
    is the front of the line, the same reading `facts_preserved_check.drop_facts` takes; the
    reason is prose about the record and may quote anything it likes. A line whose fragment is
    a substring of a heading or of a carried opening is a record that has struck a sentence and
    kept it, which is not a wording decision anybody made — it is two passes over one record
    that never met.

    Found on /uk-blue-staffy-puppy-buying-guide/ (2026-09-21 review): `dropped.text` struck
    "We handle everything for you, from a supported reservation to a safe, DEFRA-approved
    transport", which is a sentence of `delivery`'s own first tree node's `verbatim_opening`
    and renders on the page. Both gates were satisfied and the page contradicted its board.
    """
    carried = carried_wording(board)
    out = []
    seen = set()
    for kind in _DROP_PROSE_KINDS:
        for line in (board.get("dropped") or {}).get(kind, []) or []:
            if not isinstance(line, str):
                continue
            head = _DROP_SPLIT.split(line.strip(), 1)[0].strip()
            for fragment in (q.strip() for q in _DROP_ELLIPSIS.split(head)):
                if len(fragment) < MIN_DROP_FRAGMENT:
                    continue
                for where, text in carried:
                    if fragment in text and (kind, fragment, where) not in seen:
                        seen.add((kind, fragment, where))
                        out.append({"kind": kind, "fragment": fragment, "where": where})
    return out


def faq_questions(board):
    """The enumerated FAQ questions, or [] when the record has no FAQ section. Deliberately
    NOT in all_headings(): a question renders inside a <summary>, and counting it as a
    heading would inflate h_counts and let a page clear the H5/H6 floor on its FAQ alone."""
    for s in board["sections"]:
        if s["id"] == "faq" and s["shape"] == "standard":
            return list(s.get("questions", []))
    return []


def image_gaps(board):
    """Signature sections (shape ≠ standard) that plan no image. The brief puts an image
    under every H2 (§15b); a standard section — the FAQ, the form — wears its shell and no
    in-body image by design, so it is exempt rather than reported as a gap nobody will fill."""
    return [s["id"] for s in board["sections"] if s["shape"] != "standard" and not s["images"]]


def duplicate_alts(board):
    """{normalised alt: [slot, ...]} for every non-empty asset alt used twice (Rule 50b: no two
    images on a page share an alt). Compared on tokens, so a trailing full stop or a capital
    letter is not a second alt. An empty alt is an unwritten one, not a duplicate."""
    seen = {}
    for a in board["assets"]:
        key = " ".join(tokens(a["alt"]))
        if key:
            seen.setdefault(key, []).append(a["slot"])
    return {k: v for k, v in seen.items() if len(v) > 1}


def cta_findings(board):
    """[(check, message)] for the CTA plan, read on word-band MIDPOINTS. Bands are estimates,
    so both findings are prompts to look rather than proof: `cta-cadence` when the page's
    words per CTA exceed the plan's maximum, `cta-gap` for each run of consecutive CTA-free
    sections longer than that maximum. A section's `cta` is a count, not a flag: a long FAQ
    can carry two. A CTA section's own words close the run rather than join it, so one long
    section that carries a CTA never reports a gap on its own."""
    cap = board["brief"]["cta"]["cadence"]["max"]
    mid = lambda s: (s["words"]["min"] + s["words"]["max"]) // 2
    total = sum(mid(s) for s in board["sections"])
    n = sum(s.get("cta", 0) for s in board["sections"])
    out = []
    if n == 0 or total / n > cap:
        out.append(("cta-cadence", f"{n} CTA(s) across ~{total} words is one per ~{total // max(n, 1)} — "
                                   f"the plan allows at most {cap}"))
    run, ids = 0, []
    for s in board["sections"] + [None]:
        if s is not None and not s.get("cta", 0):
            run += mid(s); ids.append(s["id"]); continue
        if run > cap:
            out.append(("cta-gap", f"sections {', '.join(ids)} run ~{run} words with no CTA — the plan allows at most {cap}"))
        run, ids = 0, []
    return out


_LD_JSON = re.compile(
    r"""<script[^>]+type\s*=\s*["']application/ld\+json[^"']*["'][^>]*>(.*?)</script>""",
    re.S | re.I,
)


def _schema_type_name(t):
    """`Product`, `https://schema.org/Product` and `schema:Product` are one type; anything that is
    not a string names no type."""
    if not isinstance(t, str):
        return None
    return re.sub(r"^(?:https?://schema\.org/|schema:)", "", t.strip()) or None


def dist_schema_types(slug, dist=None):
    """(types, unparsed) for the built page: every @type anywhere in its JSON-LD, nested
    offers and @graph members included, and the count of blocks that do not parse. None when
    the page is not built. DIST is read at call time, so a test can point it elsewhere."""
    root = pathlib.Path(DIST if dist is None else dist)
    page = root / "index.html" if slug == "index" else root / slug / "index.html"
    if not page.exists():
        return None
    types, unparsed = set(), 0

    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            names = t if isinstance(t, list) else [t]
            types.update(n for n in map(_schema_type_name, names) if n)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for blk in _LD_JSON.findall(page.read_text(encoding="utf-8", errors="ignore")):
        try:
            walk(json.loads(blk))
        except json.JSONDecodeError:
            unparsed += 1
    return types, unparsed


class _Headings(DUP.Text):
    """The dup gate's chrome-skipping walker, narrowed to the text of h1-h6.

    Inheriting it is the point: a heading is collected only where
    `dup_content_audit.py --headers` would see it, so a nav link, a read-card title or a
    footer heading never enters the corpus the pre-check compares a new page against.
    Two copies of that rule would drift, and the drifted one would cry wolf."""

    def __init__(self):
        super().__init__()
        self.headings = []
        self.levelled = []                  # (level, text), the same rows with their tag
        self._buf = None
        self._level = None

    def _visible(self):
        return bool(self.stack) and not self.stack[-1][1]

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        if self._buf is None and tag in HEADING_TAGS and self._visible():
            self._buf = []
            self._level = int(tag[1])

    def handle_endtag(self, tag):
        if self._buf is not None and tag in HEADING_TAGS:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if text:
                self.headings.append(text)
                self.levelled.append((self._level, text))
            self._buf = None
            self._level = None
        super().handle_endtag(tag)

    def handle_data(self, data):
        super().handle_data(data)
        if self._buf is not None and self._visible():
            self._buf.append(data)


REBUILT = ROOT / "data" / "facts" / "rebuilt.json"


def rebuilt_slugs(path=None):
    """The slugs whose page is written fresh from an approved board rather than migrated.
    Same list `migration_parity.py` skips and `facts_preserved_check.py` gates. Missing or
    unreadable reads as empty: a gate must not pass a page because a list went absent.

    The default is resolved at CALL time, not bound at import: the gate's tests repoint
    `PB.REBUILT` at a tmp_path, and a default argument would have pinned the real file."""
    path = REBUILT if path is None else path
    try:
        rows = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return {r for r in rows if isinstance(r, str)} if isinstance(rows, list) else set()


def page_h_counts(path):
    """{h1..h6: n} for one built page, counted the way the dup gate sees headings: site
    chrome (nav, read-cards, footer) does not count toward a page's own structure."""
    p = _Headings()
    p.feed(pathlib.Path(path).read_text(encoding="utf-8", errors="ignore"))
    p.close()
    counts = {f"h{n}": 0 for n in range(1, 7)}
    for level, _ in p.levelled:
        counts[f"h{level}"] += 1
    return counts


def page_headings(path):
    """Every visible h1-h6 on one built page, tag-stripped, unescaped, collapsed."""
    p = _Headings()
    p.feed(pathlib.Path(path).read_text(encoding="utf-8", errors="ignore"))
    p.close()
    return p.headings


class _SectionProse(DUP.Text):
    """Per-section prose word counts on one built page, counted the way spec §9 amendment
    4a defines a word band.

    Three things are outside a band and so outside this count:

    * **Headings.** A band counts prose. The outline is what the breeder approved at H2/H3,
      and re-counting it as body words would pay a section for its own table of contents.
    * **The H4-H6 ladder.** It is written at P5 to meet `min-h5-h6`, roughly 25-30 words a
      section, and the bands were not set against it. A ladder opens at the first h4/h5/h6
      and runs to the next h1-h3 or to the end of the section, so its paragraphs leave the
      count along with its headings.
    * **`<details>`.** The FAQ accordion's answers come from `data/faq.json`, a different
      record with its own review.

    Inherits the dup gate's chrome rules for the reason `_Headings` does: a nav link, a
    read-card title or a footer line is not a section's prose, and a second copy of that
    rule would drift from the one the dup gate enforces."""

    def __init__(self):
        super().__init__()
        self.counts = {}
        self._sec = None        # (section id, len(self.stack) the <section> opened at)
        self._ladder = False
        self._head_at = None    # the same depth mark, for a heading and for <details>
        self._det_at = None

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        depth, a = len(self.stack), dict(attrs)
        # Top-level only: a nested <section> is part of its parent's prose, and the record
        # has no band for it.
        if tag == "section" and a.get("id") and self._sec is None:
            self._sec = (a["id"], depth)
            self.counts.setdefault(a["id"], 0)
            self._ladder = False
        if tag in HEADING_TAGS and self._head_at is None:
            self._head_at = depth
            if self._sec is not None:
                self._ladder = tag in ("h4", "h5", "h6")
        if tag == "details" and self._det_at is None:
            self._det_at = depth

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        # DUP.Text truncates its stack to the matched tag, so a depth that is no longer
        # reachable is the close of whatever opened at it — unclosed tags included.
        depth = len(self.stack)
        if self._head_at is not None and depth < self._head_at:
            self._head_at = None
        if self._det_at is not None and depth < self._det_at:
            self._det_at = None
        if self._sec is not None and depth < self._sec[1]:
            self._sec, self._ladder = None, False

    def handle_data(self, data):
        super().handle_data(data)
        if self._sec is None or self._ladder or self._head_at is not None or self._det_at is not None:
            return
        if self.stack and self.stack[-1][1]:
            return
        self.counts[self._sec[0]] += len([w for w in data.split() if re.search(r"[0-9A-Za-z]", w)])


def page_section_words(path):
    """{section id: prose words} for one built page — see `_SectionProse`."""
    p = _SectionProse()
    p.feed(pathlib.Path(path).read_text(encoding="utf-8", errors="ignore"))
    p.close()
    return p.counts


def word_band_findings(board, dist=None):
    """[(check, sev, msg)] comparing each section's prose on the BUILT page against the band
    its record sets, plus one page-level row when the total leaves the summed bands.

    WARN, never FAIL (spec §9 amendment 4a). A band is the length a section was planned at;
    a section that reads well twenty words short is not a page that may not ship. An
    unbuilt page measures nothing and says nothing — `min-h5-h6` already fails a rebuilt
    slug with no build — but a section the built page does not carry IS reported, because a
    band measured against nothing is not a band that passed.

    NOT YET REBUILT MEANS NOT YET MEASURABLE, the same rule and the same list `min-h5-h6`
    reads (spec §9 amendment 2.1). Before P5 the built page is still the MIGRATED body, which
    holds none of the record's section ids and none of its prose, so every band would report
    "not on the built page" — ten rows saying only that the page has not been written yet, on
    the board the author is still drafting. A rebuilt slug's page is the record's page, and
    that is the only page whose prose a band describes."""
    root = pathlib.Path(DIST if dist is None else dist)
    slug = board["meta"]["slug"]
    if slug not in rebuilt_slugs():
        return []
    page = root / "index.html" if slug == "index" else root / slug / "index.html"
    if not page.exists():
        return []
    got, out = page_section_words(page), []
    total = lo = hi = 0
    for sec in board["sections"]:
        sid, w = sec["id"], sec["words"]
        lo, hi = lo + w["min"], hi + w["max"]
        if sid not in got:
            out.append(("words-out-of-band", "WARN",
                        f"section {sid} is not on the built page — its {w['min']}-{w['max']} band examined nothing"))
            continue
        n = got[sid]
        total += n
        if not w["min"] <= n <= w["max"]:
            out.append(("words-out-of-band", "WARN",
                        f"section {sid}: {n} prose words against the record's {w['min']}-{w['max']}"))
    if not lo <= total <= hi:
        out.append(("words-out-of-band", "WARN",
                    f"page: {total} prose words against {lo}-{hi} (the section bands summed; "
                    "the H4-H6 ladder and the FAQ answers are outside both)"))
    return out


# The specimen routes are DUP's list, not a second copy of it: `dup_content_audit.py`
# excludes them from the duplicate-content corpus for the same reason the heading
# pre-check excludes them here, and two lists would drift. See the note beside
# DUP.SPECIMEN_PREFIXES. Left in this corpus they made every board collide with its own
# preview — 31 of the 33 FAILs on the first three approved records.
SPECIMEN_PREFIXES = DUP.SPECIMEN_PREFIXES


def _is_specimen(rel):
    """True for the specimen routes' pages, at any depth. `rel` is the dist-relative
    directory ("." for the homepage); DUP.is_specimen takes the same shape as a page key."""
    return DUP.is_specimen("" if rel == "." else rel)


def live_headings(dist=DIST):
    """{page: [heading text, ...]} from every built page, minus the specimen routes.
    Empty when dist/ is absent."""
    out = {}
    for page in sorted(pathlib.Path(dist).glob("**/index.html")):
        rel = page.parent.relative_to(dist).as_posix()
        if _is_specimen(rel):
            continue
        out["/" if rel == "." else "/" + rel + "/"] = page_headings(page)
    return out


def own_live_key(board):
    """The key this board's own page holds in live_headings(). The homepage is "/", not
    "/index/" — excluding the wrong key would let the homepage collide with itself and
    fail its own gate on every rebuild."""
    meta = board["meta"]
    if meta["page_type"] == "home" or meta["slug"] == "index":
        return "/"
    return "/" + meta["slug"] + "/"


def header_precheck(proposed, live, exclude_page=None):
    """Every proposed heading that collides with a live one: exact, template (species
    swapped) or 5-token shingle. `live` is {page: [heading, ...]}. `exclude_page` drops
    the page being rebuilt, which would otherwise collide with its own live headings —
    the same convention as owned_components() and spent_h6_prefixes()."""
    exact, templ, shingles = {}, {}, {}
    for page, hs in live.items():
        if page == exclude_page:
            continue
        for h in hs:
            t = " ".join(tokens(h))
            if not t:
                continue
            exact.setdefault(t, page)
            templ.setdefault(SPECIES.sub("{species}", t), page)
            ws = tokens(h)
            for i in range(len(ws) - SHINGLE + 1):
                shingles.setdefault(" ".join(ws[i:i + SHINGLE]), (page, h))
    hits = []
    for h in proposed:
        ws = tokens(h)
        t = " ".join(ws)
        if t in exact:
            hits.append({"heading": h, "kind": "exact", "page": exact[t], "with": h}); continue
        tt = SPECIES.sub("{species}", t)
        if tt in templ:
            hits.append({"heading": h, "kind": "template", "page": templ[tt], "with": tt}); continue
        # EVERY matching window, not the first: a heading may open on the head term the
        # page is allowed to rank for and still copy a real run further along, and a
        # break here would let the second hide behind the first.
        matched = [" ".join(ws[i:i + SHINGLE]) for i in range(len(ws) - SHINGLE + 1)
                   if " ".join(ws[i:i + SHINGLE]) in shingles]
        if matched:
            page, with_ = shingles[matched[0]]
            hits.append({"heading": h, "kind": "shingle", "page": page, "with": with_,
                         "shingle": matched[0], "shingles": matched})
    return hits


def authorization_check(board, ont):
    by_id = {e["id"]: e for e in ont["entities"]}
    used = []
    for s in board["sections"]:
        for eid in s["entities"]:
            if eid not in used:
                used.append(eid)
    return {
        "blocked": [e for e in used if e in by_id and by_id[e]["authorization"] == "BLOCKED"],
        "proposed": [e for e in used if e in by_id and by_id[e]["authorization"] == "PROPOSED"],
        "unknown": [e for e in used if e not in by_id],
    }


KEYWORD_TYPES = ("primary", "lsi", "longtail", "brand", "geo",
                 "conversational", "comparison", "solution", "transactional")
KEYWORD_LABELS = {"primary": "Primary", "lsi": "LSI", "longtail": "Long-tail", "brand": "Brand", "geo": "Geo",
                  "conversational": "Voice", "comparison": "Compare", "solution": "Solution", "transactional": "Transact"}


def distribution(board):
    rows, totals = [], {**{k: 0 for k in KEYWORD_TYPES}, "words_min": 0, "words_max": 0}
    for s in board["sections"]:
        row = {"section": s["id"], "heading": s["heading"]}
        for k in KEYWORD_TYPES:
            row[k] = len(s["keywords"][k]); totals[k] += row[k]
        row["words_min"], row["words_max"] = s["words"]["min"], s["words"]["max"]
        totals["words_min"] += row["words_min"]; totals["words_max"] += row["words_max"]
        rows.append(row)
    counts = {f"h{n}": 0 for n in range(1, 7)}
    for lvl, _ in all_headings(board):
        counts[f"h{lvl}"] += 1
    return {"rows": rows, "totals": totals, "h_counts": counts}


ADVISORY_MIN_H5H6 = {"home", "location"}          # rules/headings.md, 2026-09-09
LIBRARY_LINK_MIN = 3
LINK_FLOOR_TYPES = {"for-sale", "hub"}            # the transactional cluster and its hub
# ── working rule 16: a counter figure resolves to a file on disk ───────────────────────────
#
# Every row of a section's `stats` carries the PATH its figure came from. Rule 9 says no number
# is typed from memory, and a `source` string nobody resolves is a citation format, not a
# citation — so the gate resolves each one and refuses the record when one does not.
#
#   data/settings.json#deposit_gbp                     a dotted path into the file
#   data/puppies.json#count(status=Available)          array items carrying that field value
#   data/puppies.json#len                              the top level's length
#   data/boards/x.json#len(sections[costs].table.rows) the length of anything a path reaches
#   data/boards/x.json#cell(sections[breed-facts].table.rows, Lifespan)
#                                                      the LAST cell of the row whose first
#                                                      cell starts with that label
#   src/content/blog#files(*.md)                       how many files match, for a collection
#
# A row may cite a LIST of sources instead of one, and a figure that is a range has to: the
# string "£200–£350" is two facts, and a row citing only `delivery_min_gbp` had a source for
# the 200 and none at all for the 350 — a half-sourced figure that reads as a sourced one.
#
# THE TERMINAL VALUE MUST BE A SCALAR. A path that lands on a list or an object resolves
# "successfully" and proves nothing: `facts/<slug>.json#tests` is a five-item array, and it was
# cited by a row printing "2". Every such source is refused here by name, so the row is either
# repointed at something that really yields the figure or the tile is dropped.
#
# A bracket step is an INDEX when it is a number and an ID LOOKUP otherwise, so
# `sections[costs]` finds the section whose `id` is `costs` and survives a section being
# inserted above it. An index that silently shifted would resolve to a different fact and
# report green, which is the one failure a source check cannot afford.
#
# The gate does NOT insist the rendered figure equals the resolved one CHARACTER FOR CHARACTER:
# "£500" is the honest rendering of `500`, and "11–17 kg" of a sentence that says "11 to 17 kg
# (24 to 38 lbs), males generally at the higher end". What it does insist on is weaker than
# equality and much stronger than nothing: every NUMBER the figure prints must appear in the
# resolved text, in the order it prints them (`figure_mismatch`). "11–17 kg" against that
# sentence passes; "12–17 kg" does not, and neither does "2" against a five-item list of test
# names — which is the defect this rule was written for.
_SOURCE = re.compile(r"^([A-Za-z0-9_./*-]+)#(.+)$")
_STEP = re.compile(r"([A-Za-z0-9_-]*)((?:\[[^\]]+\])*)")


class SourceError(Exception):
    """A `stats` row whose `source` does not resolve to anything on disk."""


def _walk(node, path, spec):
    """Follow a dotted path with `[index]` / `[id]` steps. Raises SourceError, never None."""
    for step in path.split("."):
        m = _STEP.fullmatch(step.strip())
        if not m:
            raise SourceError(f"{spec}: {step!r} is not a path step")
        key, brackets = m.group(1), re.findall(r"\[([^\]]+)\]", m.group(2))
        if key:
            if not isinstance(node, dict) or key not in node:
                raise SourceError(f"{spec}: no key {key!r} at that point")
            node = node[key]
        for b in brackets:
            if not isinstance(node, list):
                raise SourceError(f"{spec}: [{b}] needs a list, found {type(node).__name__}")
            if b.lstrip("-").isdigit():
                i = int(b)
                if i >= len(node) or i < -len(node):
                    raise SourceError(f"{spec}: index {i} is past the end")
                node = node[i]
            else:
                hit = next((x for x in node
                            if isinstance(x, dict) and str(x.get("id")) == b), None)
                if hit is None:
                    raise SourceError(f"{spec}: no item with id {b!r} in that list")
                node = hit
    return node


def resolve_stat_source(spec, root=None):
    """The value a `source` string names, or SourceError with the reason it did not resolve."""
    root = ROOT if root is None else pathlib.Path(root)
    m = _SOURCE.match(spec or "")
    if not m:
        raise SourceError(f"{spec!r} is not <path>#<selector>")
    rel, sel = m.group(1), m.group(2).strip()

    if sel.startswith("files(") and sel.endswith(")"):
        pattern = sel[len("files("):-1].strip() or "*"
        d = root / rel
        if not d.is_dir():
            raise SourceError(f"{spec}: {rel} is not a directory")
        return len(sorted(d.glob(pattern)))

    f = root / rel
    if not f.is_file():
        raise SourceError(f"{spec}: {rel} is not a file")
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except ValueError as e:
        raise SourceError(f"{spec}: {rel} is not readable JSON ({e})")

    if sel == "len":
        try:
            return len(data)
        except TypeError:
            raise SourceError(f"{spec}: the file's top level has no length")

    if sel.startswith("len(") and sel.endswith(")"):
        node = _walk(data, sel[len("len("):-1].strip(), spec)
        try:
            return len(node)
        except TypeError:
            raise SourceError(f"{spec}: that path reaches a {type(node).__name__}, which has no length")

    if sel.startswith("cell(") and sel.endswith(")"):
        inner = sel[len("cell("):-1]
        if "," not in inner:
            raise SourceError(f"{spec}: cell() takes <path to rows>, <row label>")
        path, label = (x.strip() for x in inner.split(",", 1))
        rows = _walk(data, path, spec)
        if not isinstance(rows, list):
            raise SourceError(f"{spec}: cell() needs a list of rows")
        for row in rows:
            if isinstance(row, list) and row and str(row[0]).startswith(label):
                return row[-1]
        raise SourceError(f"{spec}: no row whose first cell starts with {label!r}")

    if sel.startswith("count(") and sel.endswith(")"):
        inner = sel[len("count("):-1]
        if not isinstance(data, list):
            raise SourceError(f"{spec}: count() needs a JSON array at the top level")
        if "=" not in inner:
            raise SourceError(f"{spec}: count() takes <field>=<value>")
        field, want = (x.strip() for x in inner.split("=", 1))
        return sum(1 for row in data if isinstance(row, dict) and str(row.get(field)) == want)

    value = _walk(data, sel, spec)
    _scalar(value, spec)
    return value


def _scalar(value, spec):
    """Refuse a terminal that is not a single fact.

    A path landing on a list or an object resolves without error and proves nothing: the
    why-us and about records both cited a `tests` ARRAY for a row printing "2", and the array
    happened to hold five entries on one page and three on the other. A source whose value
    cannot be compared to the figure beside it is not a source."""
    if value is None or isinstance(value, (list, dict, tuple, set)):
        kind = "nothing" if value is None else type(value).__name__
        raise SourceError(
            f"{spec}: that path reaches {kind}, not a single value — a figure cannot be "
            "checked against a list, so cite something that resolves to the figure itself "
            "(count(...), len(...), cell(...)) or drop the tile")
    return value


def sources_of(row):
    """The source list a `stats` row carries, whether it wrote one string or several."""
    src = (row or {}).get("source")
    if isinstance(src, str):
        return [src]
    return list(src or [])


def resolve_stat_sources(row, root=None):
    """[value, …] for every source a row cites, in the order it cites them."""
    srcs = sources_of(row)
    if not srcs:
        raise SourceError("a stats row cites no source at all")
    return [resolve_stat_source(s, root) for s in srcs]


#: A STANDALONE run of digits: one not glued to a letter or to another digit-bearing token.
#: `£1,500` is one number once the comma is gone, `11–17` is two, and `L-2-HGA` / `HC-HSF4`
#: are none — those digits are parts of a test's NAME, and a rule that read them as
#: quantities would demand a source for the name of a DNA test.
_DIGITS = re.compile(r"(?<![A-Za-z0-9-])(\d+)(?![A-Za-z0-9])")


def figure_numbers(text):
    """Every number a string prints, in order, as digit strings with separators removed."""
    # Commas go (a thousands separator is not a boundary), spaces STAY: stripping them glued
    # the unit to the number and "11–17 kg" became "11–17kg", whose 17 then read as part of
    # an identifier and vanished from the check.
    return _DIGITS.findall(str(text).replace(",", ""))


def figure_matches(n, values):
    """True when every number the figure prints appears, in order, in the resolved text.

    Deliberately weaker than equality and deliberately stronger than "it resolved". `cell()`
    returns prose — "12 to 14 years with good care and good genetics" — and the tile prints
    "12–14 years"; insisting on equality would ban the one selector that reads a breed table,
    and insisting on nothing is what let a five-item array stand behind a "2". So the rule is
    ORDER: 12 then 14, both present. A figure that prints no number at all ("Clear") has
    nothing to check and passes — its source still has to resolve to a scalar."""
    # A value that is not a single fact can never stand behind a figure, and stringifying a
    # list would let "2" match the 2 in "L-2-HGA". `resolve_stat_source` refuses those
    # already; this is the second lock, because `figure_matches` is called directly by the
    # tests and by anything that resolves its own values.
    if any(v is None or isinstance(v, (list, dict, tuple, set)) for v in values):
        return False
    want = figure_numbers(n)
    if not want:
        return True
    hay = " ".join(str(v) for v in values).replace(",", "")
    at = 0
    for num in want:
        i = hay.find(num, at)
        if i < 0:
            return False
        at = i + len(num)
    return True


def stat_source_problems(board, root=None):
    """[(section id, source, reason)] for every `stats` row that does not hold up.

    Two failures, reported the same way: a source that does not resolve to a single value,
    and a figure whose numbers are not in what the sources resolved to."""
    out = []
    for sec in board.get("sections", []):
        for row in sec.get("stats") or []:
            srcs = sources_of(row)
            try:
                values = resolve_stat_sources(row, root)
            except SourceError as e:
                out.append((sec["id"], row.get("source"), str(e)))
                continue
            if not figure_matches(row.get("n"), values):
                out.append((sec["id"], row.get("source"),
                            f"the figure {row.get('n')!r} prints "
                            f"{'/'.join(figure_numbers(row.get('n')))}, which is not what "
                            f"{', '.join(srcs)} resolves to ({', '.join(repr(v) for v in values)})"))
    return out


# ── working rule 16: the hero's LEDGE states figures too ───────────────────────────────────
#
# The counter strip was sourced and the hero's ledge was not, which is the same claim in a
# different box: "£500 deposit, refundable" under a lede and "£500 / refundable deposit" in a
# counter tile are one fact, and only one of them was carrying its path. So a ledge entry is
# either a plain STRING, when it states no figure, or `{text, source}`, when it does — and the
# same two checks apply: the sources resolve to single values, and the standalone numbers the
# entry prints are in what they resolved to, in order.
#
# An entry that prints a number and cites nothing is the defect, and it is reported as loudly
# as an unresolvable path: an unsourced figure that reads like a sourced one is worse than an
# obviously missing citation.

def ledge_entries(sec):
    """[(where, text, [source, …]), …] for every figure-bearing part of a hero's ledge."""
    hero = sec.get("hero") or {}
    out = []

    def add(where, entry):
        if isinstance(entry, dict):
            out.append((where, entry.get("text", ""), sources_of(entry)))
        else:
            out.append((where, entry, []))

    for key in ("chips", "ticks"):
        for i, e in enumerate(hero.get(key) or []):
            add(f"{key}[{i}]", e)
    aside = hero.get("aside") or {}
    for i, e in enumerate(aside.get("items") or []):
        add(f"aside.items[{i}]", e)
    for i, r in enumerate(aside.get("rows") or []):
        out.append((f"aside.rows[{i}]", r.get("value", ""), sources_of(r)))
    # `title` and `quote` are prose, and prose with a standalone number in it is still a
    # claim — the quote is checked for the same reason a tick is.
    for key in ("title", "quote"):
        if aside.get(key):
            out.append((f"aside.{key}", aside[key], []))
    return out


def ledge_problems(board, root=None):
    """[(section id, where, reason)] for every ledge entry that states an unbacked figure."""
    out = []
    for sec in board.get("sections", []):
        for where, text, srcs in ledge_entries(sec):
            nums = figure_numbers(text)
            if not nums and not srcs:
                continue
            if nums and not srcs:
                out.append((sec["id"], where,
                            f"{text!r} prints {'/'.join(nums)} and cites nothing — a figure "
                            "under a lede is a claim, so it carries the path it came from"))
                continue
            try:
                values = [resolve_stat_source(x, root) for x in srcs]
            except SourceError as e:
                out.append((sec["id"], where, str(e)))
                continue
            if not figure_matches(text, values):
                out.append((sec["id"], where,
                            f"{text!r} prints {'/'.join(nums) or 'no number'}, which is not "
                            f"what {', '.join(srcs)} resolves to "
                            f"({', '.join(repr(v) for v in values)})"))
    return out


# ── working rule 16: the picks a re-boarded record carries forward ─────────────────────────
#
# Four approved records went back to the board for ONE question: their hero and their counter
# strip, which rule 16 makes per-page. Their other picks were already agreed, so the old
# approval is kept under `approval_previous` and every pick in it for a section that is NOT
# being re-asked is shown on the board already answered and locked. The breeder answers the
# two that changed.
#
# A locked pick still has to be on the menu. A section whose style set was replaced under it
# has no valid carried answer, and pre-filling one would put an id on the board that
# `board_approve.py` would then refuse — so it is dropped here and asked again.
PER_PAGE_SHAPES = ("hero", "stats")

#: What a section's fingerprint is NOT taken over.
#:
#: `options` holds the pick and the note, which is the ANSWER rather than the question. `n` is
#: the section's position, which moves when a section is inserted above it and says nothing
#: about this one. `refresh` is the judgement call: a delta is a NOTE to whoever builds the
#: section — which sibling it departs from, on which of the five axes — and the arrangement it
#: departs INTO is the style pick itself, unchanged. Counting it would have unlocked all
#: forty-three carried picks the day working rule 16 gave every section a delta, which is a
#: board asking the breeder to re-answer forty-three questions to record forty-three notes.
#:
#: This is NOT the guard against a record changing under its approval: `approval_matches()`
#: hashes the whole record and fails on any edit at all. This decides, once that has already
#: failed and the record is being re-boarded, which questions are worth asking again.
FINGERPRINT_SKIPS = ("options", "n", "refresh")


def section_fingerprint(section):
    """A stable hash of everything about a section except the answer to it."""
    body = {k: v for k, v in section.items() if k not in FINGERPRINT_SKIPS}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def locked_picks(board):
    """{section id: style id} the board shows answered and locked, from `approval_previous`.

    THREE reasons a carried pick is dropped and the question asked again:

      the section is gone        — an answer to a question nobody is asking
      the section is per-page    — the hero and the counter are what the re-board is FOR
      the pick is off the menu   — its style set was replaced under it, and pre-filling an id
                                   `board_approve.py` would refuse is worse than asking
      the section CHANGED        — `approval_previous.section_hashes` records what each
                                   section looked like when it was answered; a section whose
                                   fingerprint has moved is a different proposal, and carrying
                                   the old answer forward would put the breeder's name on a
                                   decision they were never shown. Absent hashes lock nothing:
                                   an approval with no record of what it approved cannot prove
                                   anything stayed still.
    """
    prev = board.get("approval_previous") or {}
    picks = prev.get("picks") or {}
    hashes = prev.get("section_hashes") or {}
    by_id = {s["id"]: s for s in board.get("sections", [])}
    out = {}
    for sid, pick in picks.items():
        s = by_id.get(sid)
        if not s or s["shape"] in PER_PAGE_SHAPES:
            continue
        if pick not in (s.get("styles") or []):
            continue
        if hashes.get(sid) != section_fingerprint(s):
            continue
        out[sid] = pick
    return out


GATE_STAGES = ("build", "release")
_WHITELIST_TOKENS = [t for t in (tokens(w) for w in HEADER_WHITELIST) if t]
_CARD_TOKENS = {tuple(t) for t in (tokens(w) for w in PUPPY_CARD_HEADINGS) if t}


def _whitelisted(heading):
    """True when this heading is exempt from the collision gate.

    Both lists are matched EXACTLY, on the normalised token list. Two failures got us here:
    substring matching read the puppy name "evie" out of "Review", so the match moved to whole
    tokens; then sub-run matching over whole tokens still let the one-word card heading
    "roman" exempt "Roman Roads of Glasgow", clearing collisions the dup gate flags after the
    build. A whitelisted heading is a whole heading, so equality is the right test, and the two
    lists stay separate so a future relaxation for phrases cannot reach the card names.
    """
    ws = tuple(tokens(heading))
    return ws in _CARD_TOKENS or any(ws == tuple(p) for p in _WHITELIST_TOKENS)


def _head_term_shingle(shingle, primary_keyword):
    """True when the shared run is a contiguous sub-run of the board's own primary keyword
    or of a head term — the exemption applies to SHINGLE hits only. An exact or template
    match is a copied heading whatever it is made of, and is never exempt."""
    ws = tokens(shingle)
    if not ws:
        return False
    for phrase in [primary_keyword or ""] + HEAD_TERMS:
        p = tokens(phrase)
        if any(p[i:i + len(ws)] == ws for i in range(len(p) - len(ws) + 1)):
            return True
    return False


def header_hits(board, live):
    """The header collisions THIS board is answerable for — one source of truth, so the
    board artifact flags exactly what the gate will fail on and never a heading more.

    Three filters, in order: the page's own live headings are dropped (`own_live_key`),
    a heading whose collision is a whitelisted phrase is dropped (whole tokens, not
    substrings), and a shingle hit is dropped only when EVERY matching window is a sub-run
    of the board's own primary keyword or of a head term — one real copied run anywhere in
    the heading keeps the hit."""
    pk = board.get("brief", {}).get("primary_keyword", "")
    return [h for h in header_precheck([t for _, t in all_headings(board)], live,
                                       exclude_page=own_live_key(board))
            if not _whitelisted(h["heading"])
            and not (h["kind"] == "shingle"
                     and all(_head_term_shingle(w, pk) for w in h["shingles"]))]


def faq_hits(board, live):
    """FAQ questions that collide with a live heading. Same three kinds and whitelist as
    header_hits(), minus the head-term exemption: a question is a whole sentence, not a
    keyword-bearing heading, so a shared five-token run is worth a look every time."""
    return [h for h in header_precheck(faq_questions(board), live, exclude_page=own_live_key(board))
            if not _whitelisted(h["heading"])]


PERF_DIR = ROOT / "data" / "quality" / "perf"
PERF_PROFILES = ("mobile", "desktop")


def perf_findings(slug, stage, perf_dir=None, dist_page=None):
    """PageSpeed at release: 100 in all five categories (scripts/perf_audit.py records).

    Local records (`<slug>--<profile>.json`, measured on dist/) gate the release and must be
    newer than the build. Mobile Performance is NOT judged locally: this Mac's CPU cannot
    stand in for PageSpeed's, so the PSI record (`<slug>--<profile>--psi.json`) judges it.
    A PSI record can only exist after deploy, so a missing or superseded one is pending
    (WARN); a PSI record that reads under 100, or saw an edge-injected script, FAILS the
    next release — the breeder's 2026-09-13 report is exactly that case."""
    if stage != "release":
        return []
    perf_dir = pathlib.Path(perf_dir) if perf_dir else PERF_DIR
    dist_page = pathlib.Path(dist_page) if dist_page else (DIST / slug / "index.html" if slug else DIST / "index.html")
    f = []
    add = lambda check, sev, msg: f.append({"check": check, "sev": sev, "msg": msg})
    read = lambda name: json.loads((perf_dir / f"{name}.json").read_text()) if (perf_dir / f"{name}.json").exists() else None
    for prof in PERF_PROFILES:
        local, psi = read(f"{slug}--{prof}"), read(f"{slug}--{prof}--psi")
        if local is None:
            add("perf-record-missing", "FAIL", f"no {prof} perf record — python3 scripts/perf_audit.py {slug}{' --mobile' if prof == 'mobile' else ''} --runs 3")
        else:
            if dist_page.exists() and local.get("dist_mtime", 0) < dist_page.stat().st_mtime:
                add("perf-record-stale", "FAIL", f"{prof} perf record predates the current build — re-run perf_audit.py")
            judged = [c for c in local.get("failed", []) if not (prof == "mobile" and c == "performance")]
            if judged:
                add("perf-below-100", "FAIL", f"{prof} (dist) under 100: {', '.join(judged)}")
        if psi is None or (local is not None and psi.get("measured_at", "") < local.get("measured_at", "")):
            add("perf-psi-pending", "WARN", f"{prof}: confirm on PageSpeed after deploy — perf_audit.py {slug} --psi{' --mobile' if prof == 'mobile' else ''}")
            continue
        if psi.get("failed"):
            got = ", ".join(f"{c} {round((psi.get('median') or {}).get(c, 0) * 100)}" for c in psi["failed"])
            add("perf-psi-below-100", "FAIL", f"{prof} on PageSpeed under 100: {got}")
        if psi.get("edge_blocking"):
            add("perf-edge-injected", "FAIL", f"{prof}: Cloudflare injects scripts dist/ never ships: {', '.join(psi['edge_blocking'])}")
    return f


# ── is dist/ a build, or a build in progress? ──────────────────────────────────────────────
#
# `min-h5-h6` reads the BUILT page when one exists, and once read a half-written `dist/` gives
# a real number about a page nobody shipped: the check flipped from PASS to FAIL and back on
# the same record, because it ran while `astro build` was still writing. A file existing is not
# a build having finished.
#
# So: the built page is only believed when it is NEWER than everything that produces it. The
# comparison is the same one the render harness makes in TypeScript (`checkDistFreshness`),
# kept here in the same shape rather than shared, because a gate that imported the harness
# would not run without it.
#
# A stale or mid-flight `dist/` is a WARN and a FALLBACK, never a FAIL: the record's own tree
# is what the check read before the page was built, and reading it again says "not measurable
# yet", which is true. A FAIL would be the gate asserting a defect it cannot see.
FRESHNESS_ROOTS = ("src", "data/boards")
#: Files the build itself writes back into a watched root. Counting them makes every build
#: instantly stale against itself.
FRESHNESS_SKIP = ("data/boards/previews",)
#: What a page's dist actually depends on, when the caller can name the page.
#:
#: The whole-tree sweep above is right when nobody can say which page is being judged, and
#: WRONG the moment two agents work the same tree: agent A writing
#: `data/boards/<other>.json` made every other page's `dist/` read as stale, and
#: `min-h5-h6` fell back to the record tree and failed a page whose built file was perfectly
#: current. Freshness is a question about ONE page, so it is answered from that page's own
#: sources — its `src/pages/<slug>/` (or `src/pages/index.astro` for the root), its own
#: record — plus the shared shell every page renders through and the data files every page
#: reads. A sibling's record is not among them, because no page renders a sibling's record.
FRESHNESS_SHARED = ("src/layouts", "src/components", "src/lib", "src/styles")


def _relpath(path):
    """The path as the repo spells it, or absolute when it is outside (a test's tmp_path)."""
    try:
        return str(pathlib.Path(path).relative_to(ROOT))
    except ValueError:
        return str(path)


def freshness_inputs(root, slug=None):
    """The files a built page's freshness is measured against.

    `slug` None keeps the whole-tree sweep, which is what a caller that cannot name a page
    has to do. Naming one narrows it to that page's own sources, the shared shell and the
    top-level data files — see FRESHNESS_SHARED for why that is not a loosening."""
    root = pathlib.Path(root)
    if slug is None:
        for rel in FRESHNESS_ROOTS:
            base = root / rel
            if base.exists():
                yield from (f for f in base.rglob("*") if f.is_file()
                            and not any(str(f.relative_to(root)).startswith(k) for k in FRESHNESS_SKIP))
        return
    # The root slug's page is `src/pages/index.astro`, not `src/pages/index/index.astro` —
    # the same spelling verbatim_set_check.dist_html and the min-h5-h6 reader use.
    own = [root / "src" / "pages" / (f"{slug}.astro" if slug == "index" else slug),
           root / "data" / "boards" / f"{slug_file(slug)}.json"]
    for base in own:
        if base.is_file():
            yield base
        elif base.is_dir():
            yield from (f for f in base.rglob("*") if f.is_file())
    for rel in FRESHNESS_SHARED:
        base = root / rel
        if base.exists():
            yield from (f for f in base.rglob("*") if f.is_file())
    data = root / "data"
    if data.exists():
        yield from (f for f in data.glob("*.json") if f.is_file())


def newest_input_mtime(root=None, slug=None):
    """The newest mtime among the sources a built page is produced from."""
    root = ROOT if root is None else pathlib.Path(root)
    return max((f.stat().st_mtime for f in freshness_inputs(root, slug)), default=0.0)


def dist_page_is_fresh(built, root=None, slug=None):
    """True when `built` is newer than every source that produces it."""
    built = pathlib.Path(built)
    return built.exists() and built.stat().st_mtime >= newest_input_mtime(root, slug)


def gate_findings(board, ont, ledger, live, stage="build"):
    """Every reason this record may not be built (or released). Pure: no printing."""
    if stage not in GATE_STAGES:
        raise BoardError(f"unknown gate stage {stage!r}: expected one of {', '.join(GATE_STAGES)}")
    f = []
    slug = board["meta"]["slug"]
    add = lambda check, sev, msg: f.append({"check": check, "sev": sev, "msg": msg})

    if not approval_matches(board):
        add("approval-hash", "FAIL", "no approval, or the record changed after it was approved — board it again")

    # A section that offered three rendered styles and carries no pick would be built by
    # someone guessing at which arrangement the breeder meant. DRAFTS SKIP IT: a record is
    # boarded before it is picked, and failing the gate for not yet having been answered
    # would make the board unreachable. Once the record says `approved`, every styled
    # section owes an answer.
    if board["meta"]["status"] == "approved":
        picks = (board.get("approval") or {}).get("picks") or {}
        for s in board["sections"]:
            if s.get("styles") and s["id"] not in picks:
                add("style-unpicked", "FAIL",
                    f"section {s['id']} offers {'/'.join(s['styles'])} and the approval names no style for it")

    # Working rule 16 and rule 9: a figure with a source nobody can resolve is a figure with
    # no source. FAIL rather than WARN — the whole point of carrying the path is that it is
    # checked, and a warning here is a number that ships.
    for sid, spec, why in stat_source_problems(board):
        add("stat-source-unresolved", "FAIL",
            f"section {sid}: stats source {spec!r} does not hold up — {why}")
    for sid, where, why in ledge_problems(board):
        add("ledge-source-unresolved", "FAIL", f"section {sid} {where}: {why}")

    # Working rule 16's second half: EVERY section carries a refresh delta, not the three to
    # five a page felt like writing. The hero and the counter strip are exempt because they are
    # per-page by construction — their delta IS the style set — and a draft is exempt because a
    # record is drafted before it is differentiated. From `boarded` on, a section with no
    # recorded delta is a section that will be built as a sibling's twin.
    # Scoped to records that name their LAYOUT FAMILY, which is what says a record has been
    # brought under working rule 16. The four pages built before it still name S1/S2/S3 and
    # have no `layout_type`; the later task that refreshes them adds one, and the check starts
    # asking them then. A slug list here would be an allowlist nobody would remember to edit.
    if (board["meta"]["status"] in ("boarded", "approved", "built", "released")
            and board["meta"].get("layout_type")):
        missing = [s["id"] for s in board["sections"]
                   if s["shape"] not in PER_PAGE_SHAPES and not s.get("refresh")]
        if missing:
            add("refresh-missing", "FAIL",
                f"{len(missing)} section(s) carry no refresh delta: {', '.join(missing)} — "
                "working rule 16 asks every section for one, and "
                ".claude/skills/bsuk-component-refresh/SKILL.md names the five axes")

    auth = authorization_check(board, ont)
    for e in auth["blocked"]:
        add("entity-blocked", "FAIL", f"{e} is BLOCKED (CLAUDE.md rule 2)")
    for e in auth["unknown"]:
        add("entity-unknown", "WARN", f"{e} is not in data/bsuk-ontology.json")
    for e in auth["proposed"]:
        add("entity-proposed", "WARN", f"{e} is PROPOSED — needs a source before it can be asserted")

    # The ledger's discipline is that COMBOS differ, not components: dial-1-clay is on
    # nine pages by design, so a per-component rule would fail every page on the site.
    # Four rules, narrowest first.
    t = board["tuple"]
    siblings = {p: s for p, s in ledger.get("pages", {}).items() if p != slug}
    tw = set(t.get("takeaway", []))
    # The narrow signature. It used to be hero+dial+rail, on the reading that those three
    # are the page's chrome and a page that wears all three the same way is the same page.
    # Project 4 retired that: the breeder picked ONE dial style and ONE sheet style on the
    # contact board and they are baked into the kit, so every rebuilt page carries the same
    # two — the triple degenerated to "no two pages may share a hero style", which failed
    # privacy-policy-uk against thank-you-blue-staffy-puppies-journey on a hero pick alone.
    # The signature is now the tuple MINUS the two baked axes: what a page is made of that
    # the breeder can still choose differently. `toc` is outside it on the same argument —
    # every rebuilt page mounts the one kit page nav — while `table` is INSIDE it as of spec
    # §9 amendment 5 (working rule 13): a table is a picked shell with three rendered styles
    # and "tuple.table records the pick", so two pages that differ by carrying one are not
    # the same page. It was left out only while no board offered a table section.
    signature = (t.get("hero") or "", t.get("faq") or "", t.get("table") or "",
                 tuple(sorted(tw)))

    identical = [p for p, s in siblings.items()
                 if all((s.get(k) or "") == (t.get(k) or "") for k in TUPLE_ID_KEYS)
                 and set(s.get("takeaway", [])) == tw]
    for p in identical:
        add("ledger-tuple-identical", "FAIL",
            f"every tuple axis matches {p} — the combo is what has to differ")
    rest = {p: s for p, s in siblings.items() if p not in identical}

    trip = []
    if any(signature[:3]) or tw:
        trip = [p for p, s in rest.items()
                if (s.get("hero") or "", s.get("faq") or "", s.get("table") or "",
                    tuple(sorted(set(s.get("takeaway", []))))) == signature]
        if trip:
            shown = "+".join(x or "—" for x in
                             (signature[0], signature[1], signature[2],
                              ", ".join(signature[3]) or ""))
            add("ledger-tuple-owned", "FAIL",
                f"hero+faq+table+takeaway {shown} is the same signature as {', '.join(trip)}")
    # A SET, and only a set. The rule is about a page copying another page's COMBINATION of
    # takeaway shells; it degenerates the way hero+dial+rail did in spec §9 amendment 2.2 the
    # moment a page carries exactly one. Project 4 gives a `takeaways` section three styles
    # and most pages carry one such section, so a singleton set is a pick from a pool of
    # three — under a set rule the fourth page to want a takeaway block could not have one,
    # whatever it said. The combination is still policed: `takeaway` is one of the four axes
    # of the signature above, so two pages that agree on it must differ somewhere else.
    if len(tw) > 1:
        sets = [p for p, s in rest.items() if set(s.get("takeaway", [])) == tw]
        if sets:
            add("ledger-takeaway-set-owned", "FAIL",
                f"takeaway set {{{', '.join(sorted(tw))}}} is the same set as {', '.join(sets)}")
    # The scarce shells — the tuple axes the ledger itself lists as refresh pools, so the
    # rule follows the data rather than a second hardcoded list (takeaway is a refresh pool
    # too, but it is a set, and the set rule above already covers it). A bare base a sibling
    # uses (bare or refreshed) must be refreshed here too; a `base#delta` passes unless it
    # is a sibling's exact id, which owned_components records under the full id.
    owned = owned_components({"pages": rest})          # an identical sibling is already reported
    for key in [k for k in TUPLE_ID_KEYS if k in ledger.get("refresh_pools", [])]:
        v = t.get(key)
        if key == "hero" and trip:
            continue                                   # the triple finding already names it
        if v and owned.get(v):
            add("ledger-shell-owned", "FAIL",
                f"tuple.{key}={v} is owned by {', '.join(owned[v])} — refresh it as {base_of(v)}#<delta>")
    if not siblings:
        add("ledger-examined-zero", "WARN",
            f"the component ledger records {len(ledger.get('pages', {}))} page(s) and no sibling of {slug} — "
            "the five ledger-* checks examined nothing")
    spent = spent_h6_prefixes(ledger, exclude_slug=slug)
    for p in t.get("h6_prefixes", []):
        if p in spent:
            add("ledger-spent-prefix", "FAIL", f"H6 prefix {p!r} is spent by {', '.join(spent[p])}")

    # A RECORD MAY NOT BOTH DROP A SENTENCE AND RENDER IT. `dropped` is the accounting of
    # what the rebuild did NOT carry and the verbatim set is the accounting of what it MUST
    # carry word for word, so a fragment in both is the record contradicting itself — and the
    # contradiction is invisible to every other gate, because each of the two reads only its
    # own field. `facts_preserved_check.py` sees the claim excused and stops looking;
    # `verbatim_set_check.py` sees the opening present and passes; the page ships a paragraph
    # its own board says was struck, with a reason underneath explaining why it is not there.
    for d in dropped_vs_verbatim(board):
        add("dropped-vs-verbatim", "FAIL",
            f"dropped.{d['kind']} strikes {d['fragment']!r}, which {d['where']} carries word for "
            "word — a record cannot both drop a sentence and render it")

    if not live:
        add("header-precheck-examined-zero", "FAIL",
            "header pre-check examined 0 live pages — run npx astro build first")
    for h in header_hits(board, live):
        add("header-collision", "FAIL", f"{h['kind']}: {h['heading']!r} vs {h['page']} {h['with']!r}")
    # WARN, never FAIL. Two pages may legitimately answer the same buyer question, and the
    # dup gate judges the ANSWER after the build; a repeated question is a sign to look.
    for h in faq_hits(board, live):
        add("faq-collision", "WARN", f"{h['kind']}: FAQ question {h['heading']!r} vs {h['page']} {h['with']!r}")

    # The floor is a property of the PAGE, and where the page exists that is what to count.
    # A board record's tree stops at the H3/H4 the breeder approved — the outline is a plan
    # for sections, not a transcript of every sub-point — so counting it would force H5 and
    # H6 rows into an approved outline purely to satisfy an arithmetic check. A rebuilt page
    # earns the floor the way the migrated pages did: H4/H5 sub-points and the "<prefix>:"
    # H6 lines are written inside the sections at build time. A record NOT yet rebuilt has
    # no built page to read, so it keeps the tree reading and the floor stays a planning
    # constraint. `source` is named in the message: a floor met two ways must say which.
    # The homepage's built file is dist/index.html, not dist/index/index.html: `index` is
    # the slug this repo gives "/", and a path built the ordinary way would never exist, so
    # the one page that is the site's front door would silently keep the record-tree reading
    # for ever. Same spelling as verbatim_set_check.dist_html and word_band_findings.
    built = DIST / ("" if slug == "index" else slug) / "index.html"
    fresh = dist_page_is_fresh(built, slug=slug)
    if slug in rebuilt_slugs() and built.exists() and fresh:
        counts, source = page_h_counts(built), "built page"
    else:
        counts, source = distribution(board)["h_counts"], "record tree"
        if slug in rebuilt_slugs() and built.exists() and not fresh:
            add("dist-stale", "WARN",
                f"{_relpath(built)} is older than the sources that produce it — the heading "
                "floor was read from the record tree instead. Run npm run build and re-run "
                "this gate; a page read mid-build gives a real number about a page nobody "
                "shipped.")
    if counts["h5"] < 5 or counts["h6"] < 5:
        sev = "WARN" if board["meta"]["page_type"] in ADVISORY_MIN_H5H6 else "FAIL"
        add("min-h5-h6", sev,
            f"H5 {counts['h5']} / H6 {counts['h6']} ({source}) — floor is 5 each")

    ms = board["meta_set"]
    # A recommendation is a draft, not a choice. At build the page can be written against
    # it; by release an unanswered meta set is a page shipping someone's guess.
    sev = "FAIL" if stage == "release" else "WARN"
    for field in ("title", "description"):
        if ms["pick"][field] is None:
            add("meta-no-pick", sev, f"meta {field} has no pick — the recommendation is a draft, not a choice")
    cap = title_ceiling(slug)
    for i, t_ in enumerate(ms["titles"]):
        if len(t_) > cap:
            add("meta-length", "FAIL", f"title variant {i} is {len(t_)} chars — ceiling is {cap} "
                                       "(data/quality/evidence-budgets.json)")
    for i, d_ in enumerate(ms["descriptions"]):
        if not DESC_MIN <= len(d_) <= DESC_MAX:
            add("meta-length", "FAIL", f"description variant {i} is {len(d_)} chars — band is {DESC_MIN}–{DESC_MAX}")

    # Measured from the built page, not from the record: the record carries the plan and
    # only the page carries the prose. WARN at both stages (spec §9 amendment 4a).
    for check, sev, msg in word_band_findings(board):
        add(check, sev, msg)

    for sid in image_gaps(board):
        add("image-coverage", "WARN", f"section {sid} plans no image slot — the brief puts one under every H2 (§15b)")
    for key, slots in duplicate_alts(board).items():
        add("asset-alt-duplicate", "FAIL",
            f"slots {', '.join(slots)} share one alt ({key!r}) — no two images on a page share an alt (Rule 50b)")
    for check, msg in cta_findings(board):
        add(check, "WARN", msg)

    picks = (board.get("approval") or {}).get("picks", {})
    for s in board["sections"]:
        pick = s["options"]["pick"] or picks.get(s["id"])
        if s["shape"] != "standard" and not pick:
            add("signature-no-pick", "FAIL", f"section {s['id']} ({s['shape']}) has no component pick")
        # A nav-shaped section IS the page's table of contents, so its pick and tuple.toc
        # are two names for one component. A mismatch means one of them is stale — a WARN,
        # because which one is right is the author's call, not the gate's.
        if s["shape"] == "nav" and pick and pick != t.get("toc"):
            add("pick-tuple-mismatch", "WARN",
                f"section {s['id']} picks {pick} but tuple.toc is {t.get('toc') or '(empty)'}")

    internal, external, anchors = [], [], {}
    for s in board["sections"]:
        internal += [(s["id"], l) for l in s["links"]["internal"]]
        external += [(s["id"], l) for l in s["links"]["external"]]
    # Anchor Diversity is a page-level rule, so the comparison is on tokens: "Our Blue
    # listings" and "our blue listings," are one anchor twice, and a raw string compare
    # would pass them.
    # A nav anchor is exempt (breeder, 2026-09-13): a grid, a boarding pass and a
    # breadcrumb repeat their destinations by nature, and a tile that reads like a prose
    # anchor elsewhere on the page is not a second use of it. An anchor that tokenises to
    # nothing — a glyph, a dash — is skipped too: it would group every other such anchor
    # under one empty key and report a duplicate nobody wrote.
    for sid, l in internal + external:
        if l.get("nav"):
            continue
        key = " ".join(tokens(l["anchor"]))
        if key:
            anchors.setdefault(key, []).append((sid, l["anchor"]))
    for uses in anchors.values():
        if len(uses) > 1:
            add("links-anchor-duplicate", "FAIL",
                f"anchor {uses[0][1]!r} is used {len(uses)} times ({', '.join(s for s, _ in uses)}) "
                "— one anchor, one destination, one place")
    if board["meta"]["page_type"] in LINK_FLOOR_TYPES and len(external) < LIBRARY_LINK_MIN:
        # WARN at build so a page can be written while a library row is still being
        # verified; FAIL at release because a transactional page with no outside citation
        # is the thin-page pattern the cluster was rebuilt to leave behind.
        add("links-external-missing", "FAIL" if stage == "release" else "WARN",
            f"{len(external)} external library link(s) recorded — a {board['meta']['page_type']} page "
            f"carries at least {LIBRARY_LINK_MIN}")
    # Reuses the live map the gate already loaded for the header pre-check. When it is
    # empty the gate has already FAILed on header-precheck-examined-zero, and guessing at
    # dead links from an unbuilt tree would only add noise to that.
    for sid, l in (internal if live else []):
        path = l["href"].split("#", 1)[0].split("?", 1)[0]
        target = path if path.endswith("/") else path + "/"
        if target not in live:
            add("links-internal-dead", "FAIL",
                f"section {sid}: {l['href']} has no built page (dist{target}index.html)")

    f.extend(perf_findings(slug, stage))

    if stage == "release":
        for a in board["assets"]:
            if a["required"] and a["status"] != "baked":
                add("asset-required-missing", "FAIL", f"required slot {a['slot']} ({a['kind']} {a['w']}x{a['h']}) is {a['status']}")
        got = dist_schema_types(slug)
        if got is None:
            add("schema-examined-zero", "FAIL", f"no built page for {slug} — the schema plan examined nothing")
        else:
            found, unparsed = got
            for tname in board["brief"]["schema"]["types"]:
                if tname not in found:
                    add("schema-planned-missing", "FAIL", f"{tname} is in the schema plan but not in the built page's JSON-LD")
            if unparsed:
                add("schema-unparsed", "FAIL", f"{unparsed} JSON-LD block(s) on the built page do not parse")

    # The rules that bind project 5's pages only (scripts/family_rules.py, system-gaps build).
    for check, sev, msg in FR.findings(board, ont):
        add(check, sev, msg)
    return f


# Inlined from CAG's board_canvas.py, which is not ported (spec §2: canvas and thumbnail
# scripts are out of scope). Only these two functions were used outside that module: a
# candidate id may carry a '#' delta, which is not legal in a filename, so the artboard
# and thumbnail filenames spell it '_' and these two convert between the spellings.
def file_token(candidate: str) -> str:
    """Candidate id -> the spelling used inside an artboard or thumbnail filename."""
    return candidate.replace("#", "_")


def unfile_token(token: str) -> str:
    """The filename spelling -> the candidate id. Inverse of file_token().

    One-way-safe only for ids that carry no `_` of their own: every `_` comes back as a
    `#`, so `file_token()` round-trips but an id spelled with an underscore does not. No
    component id in any pool uses `_`, and the schema's `^[a-z][a-z0-9-]*$` keeps it that
    way — the delta suffix after `#` is the only place the spelling ever differs."""
    return token.replace("_", "#")
