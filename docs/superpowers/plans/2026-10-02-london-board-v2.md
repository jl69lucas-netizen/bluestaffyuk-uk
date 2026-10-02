# London Page Board v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the breeder's 2026-10-02 asks to the London page board (STOP 3) so it can be approved once, with everything on it. The asks are term and entity density against competitors, a competitor term gap, a "how Google reads this page" block, the FAQ-placement method, infographic style trios and 4–5 OG image slots. Alongside the board, the plan ships the skill and handoff tooling and the decisions batch for the answer board.

**Architecture:** Each new board block is a pure Python module under `scripts/` that reads files already on disk and returns markdown. The modules read the board record, the saved competitor HTML in `data/queries/cache/<slug>/`, the SERP JSON in `data/queries/raw/<slug>/` and the ontology. `scripts/build_page_board.py` appends each module's markdown as a lettered block, gated on `PB.FR.applies(board)`, so the twelve pre-rule boards stay byte-identical; this is the existing pattern of blocks 4b and 7b. No module invents a term. Every term or entity it proposes is printed with the competitor pages it was counted on.

**Tech Stack:** Python 3.9 stdlib, pytest (`npm run test:py`), the existing `keyword_metrics` / `query_augment` parsers, the Artifact tool (the board is republished at the same URL), and `scripts/answer_board_batch.py` with ArtifactData.

---

## Brief restated (working rule 5)

- **Goal:** London page board v2, then a single breeder approval (STOP 3).
- **Scope:**
  - six new board blocks (1b, 4c, 4d, 5c, 7c, 7d);
  - the FAQ-placement rule;
  - one new skill that holds the competitor-parity method;
  - the session-handoff skill and today's handoff prompt;
  - the decision questions for the answer board.
- **Gates:**
  - `npm run test:py` is green;
  - `npm run -s build && npm run check:all` is green;
  - `python3 scripts/build_page_board.py blue-staffy-puppies-london` exits 0;
  - `python3 scripts/build_agent_registry.py --check` exits 0.
- **Done means:** board v2 is republished at https://claude.ai/artifact/CbemmwUeW5qGEmEFog7ezz, the batch is on the answer board, every task is committed and nothing is pushed.
- **Out of scope:**
  - building London's `.astro` (that is page-run Task 26+);
  - generating images, which waits for the infographic and OG picks (that is page-run Task 24, STOP 4);
  - writing any mod before the breeder picks one.

## Already done in the session that wrote this plan (2026-10-02)

- [x] The cloud branch `origin/london-components-98b173` was brought home. Its root snapshot `bfe350a7` has the same tree as local `5ece280`, so its 26 commits were cherry-picked onto `london-components`. HEAD `a23b2a4` has the same tree as the cloud branch.
- [x] `GEMINI_API_KEY` was appended to `.env`, which is gitignored and confirmed untracked. `genai.Client().models.list()` authenticates and lists six image models. The KI 70 smoke image runs separately; when it lands, close KI 70 in `docs/reference/session-log.md`.
- [x] Both boards are watched with ArtifactComments, with auto-replies armed.

## What already exists (do not rebuild it)

| Ask | Already there | Gap this plan fills |
|---|---|---|
| Density | `keyword_metrics.py` block 4b gives aggregates per page (unique terms, mentions, exact counts per tag) for us and the top five | per-term counts per competitor, min/median/mean/max, and a target per term |
| Competitor entities | `board_entities.py` block 5 shows *our* entities by class; `ontology_seed.py` | terms and entities competitors carry that our board does not, by keyword type, with relationships |
| FAQ placement | `query_augment.py` splits top/middle/bottom; the query-augmentation skill says location pages get three blocks and comparison, blog and puppy pages "may" use one | a decision procedure for every page type, shown on the board |
| Infographics | IG-1…IG-5 in `.claude/skills/bsuk-infographic/SKILL.md`; one London slot, `deposit-steps` (IG-2) | a per-section need test, and three rendered styles per needing section for the breeder to pick from |
| OG images | IMAGE-DESIGNS.md §1 says one share card per page; framing styles A–H | 4–5 OG slots per page (after the breeder's interpretation pick, Task 9) |
| Components | the London city-kit picks (`city-*`, 2026-09-27) | recording "new or refreshed component per section, every remaining page" as a standing rule |

## File map

| File | Responsibility |
|---|---|
| `scripts/term_density.py` (new) | per-term counts on us and each competitor, stats, the two target options |
| `scripts/term_gap.py` (new) | competitor terms and entities missing from the board, grouped by keyword type, with relationships |
| `scripts/serp_reading.py` (new) | block 1b, "How Google reads this page", built from the SERP JSON |
| `scripts/faq_layout.py` (new) | the FAQ-placement decision for a page |
| `scripts/infographic_plan.py` (new) | which sections need an infographic, which IG type, and three style previews each |
| `scripts/og_slots.py` (new) | the 4–5 OG slot proposals |
| `scripts/build_page_board.py` (modify, around 940–1010) | append blocks 1b, 4c, 4d, 5c, 7c and 7d; add the infographic picks to the signature list |
| `tests/py/test_term_density.py`, `test_term_gap.py`, `test_serp_reading.py`, `test_faq_layout.py`, `test_infographic_plan.py`, `test_og_slots.py` (new) | one test file per module |
| `tests/py/test_page_board.py` (modify) | assert the new block titles on a new-family board, and their absence on a pre-rule board |
| `.claude/skills/bsuk-competitor-parity/SKILL.md` (new) | the "match them type by type, beat them on evidence" method |
| `.claude/skills/session-handoff/SKILL.md` (new) + `scripts/session_handoff.py` (new) | the new-chat handoff prompt |
| `rules/copy.md`, `.claude/skills/bsuk-query-augmentation/SKILL.md`, `docs/reference/page-run.md` (modify) | the FAQ-placement rule text and the component rule in row 10 |
| `docs/reference/answer-board/batches/2026-10-02-london-board-v2.{md,json}` (new) | the decisions batch |

Shared fixture: `tests/py/fixtures/competitor-pages/breeder-sections.html` already exists. Each task below adds its own tiny inline HTML and does not depend on that file.

---

### Task 1: Per-term density against each competitor (`term_density.py`)

**Files:**
- Create: `scripts/term_density.py`
- Test: `tests/py/test_term_density.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/py/test_term_density.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import term_density as TD

PAGE_A = "<html><body><main><p>Blue staffy puppies in London. Blue staffy puppies are kind.</p>" \
         "<p>Kennel Club papers.</p></main></body></html>"
PAGE_B = "<html><body><main><p>Blue staffy puppies here. Kennel Club registered.</p></main></body></html>"

def test_counts_each_term_on_each_page():
    c = TD.count_terms(PAGE_A, ["blue staffy puppies", "kennel club", "pedigree"])
    assert c["counts"] == {"blue staffy puppies": 2, "kennel club": 1, "pedigree": 0}
    assert c["words"] > 0

def test_stats_and_two_targets():
    pages = [TD.count_terms(PAGE_A, ["kennel club"]), TD.count_terms(PAGE_B, ["kennel club"])]
    row = TD.term_row("kennel club", pages, our_words=2000)
    assert row["min"] == 1 and row["max"] == 1 and row["median"] == 1
    # targets scale each competitor's per-1,000-word density to our word target
    assert row["target_median"][0] <= row["target_median"][1]
    assert row["target_leader"][0] >= row["target_median"][0]
    assert row["seen_on"] == 2

def test_zero_competitor_pages_is_not_fetched():
    row = TD.term_row("x", [], our_words=2000)
    assert row["note"].startswith("NOT FETCHED")
```

- [ ] **Step 2: Run to confirm it fails**

Run: `python3 -m pytest tests/py/test_term_density.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'term_density'`.

- [ ] **Step 3: Implement**

```python
#!/usr/bin/env python3
"""term_density.py — how often each board keyword and entity appears on us and on each competitor.

Board block 4c. For every term on the board (keyword_metrics.board_terms) plus every entity name
the board names (ontology `name`), count matches in each of the top five competitor bodies
(data/queries/cache/<slug>/<n>.html, the same five keyword_metrics measures) and give min, median,
mean and max. Two targets, each scaled to OUR word target per 1,000 words:

  median band  [p25, p75] of competitor density x our words — what already ranks, no outlier
  leader band  [p75, max] of competitor density x our words — at or above the densest ranker

Counts use keyword_metrics' own matching (case, small words ignored, longest match wins), so a
number here and a number in block 4b mean the same thing. A competitor with no cache file is
NOT FETCHED, never zero.
"""
import json
import math
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
import query_augment as QA    # noqa: E402

ROOT = KM.ROOT


def _body_tokens(html):
    p = KM._Page()
    p.feed(html)
    p.close()
    return KM.key_words(" ".join(r[0] for r in p.body()))


def count_terms(html, terms):
    toks = _body_tokens(html)
    idx = KM._index(toks)
    counts = {}
    for t in terms:
        tt = KM.key_words(t)
        counts[t] = len(KM._starts(tt, toks, idx)) if tt else 0
    words = QA.page_metrics(html).get("word_count") or len(toks)
    return {"counts": counts, "words": words}


def _pct(vals, q):
    s = sorted(vals)
    k = (len(s) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def term_row(term, pages, our_words):
    if not pages:
        return {"term": term, "note": "NOT FETCHED — no cached competitor page"}
    counts = [p["counts"].get(term, 0) for p in pages]
    dens = [c * 1000 / p["words"] if p["words"] else 0 for c, p in zip(counts, pages)]
    scale = our_words / 1000
    return {"term": term, "min": min(counts), "max": max(counts),
            "median": statistics.median(counts), "mean": round(statistics.mean(counts), 1),
            "seen_on": sum(1 for c in counts if c), "of": len(counts),
            "target_median": (round(_pct(dens, .25) * scale), round(_pct(dens, .75) * scale)),
            "target_leader": (round(_pct(dens, .75) * scale), round(max(dens) * scale)),
            "note": ""}


def competitor_pages(slug, terms, root=ROOT):
    bare = KM._bare(slug)
    raw = pathlib.Path(root) / "data/queries/raw" / bare / "competitors.json"
    try:
        listed = json.loads(raw.read_text(encoding="utf-8"))["pages"]
    except (OSError, ValueError, KeyError):
        return []
    ranked = sorted(((n, p) for n, p in enumerate(listed, 1) if not p.get("blocked")), key=KM._rank)
    out = []
    for n, p in ranked[:KM.TOP]:
        f = pathlib.Path(root) / "data/queries/cache" / bare / f"{n}.html"
        if f.exists():
            html = f.read_text(encoding="utf-8", errors="replace")
            if QA.listing_reason(QA.page_metrics(html)):
                continue                       # a card grid is not a competitor's prose
            out.append(dict(count_terms(html, terms), url=p["url"]))
    return out


def board_entity_names(board, ont):
    names = {e["id"]: e["name"] for e in ont.get("entities", [])}
    ids = [i for s in board["sections"] for i in (s.get("entities") or [])]
    return [names[i] for i in dict.fromkeys(ids) if i in names]


def rows(board, ont, root=ROOT):
    terms, _ = KM.board_terms(board)
    terms = list(dict.fromkeys(terms + board_entity_names(board, ont)))
    our_words = sum(s.get("words") or 0 for s in board["sections"])
    pages = competitor_pages(board["meta"]["slug"], terms, root)
    return [term_row(t, pages, our_words) for t in terms], pages


def table(board, ont, root=ROOT):
    rs, pages = rows(board, ont, root)
    head = ["Term", "Seen on", "Min", "Median", "Mean", "Max",
            "Target · median band", "Target · leader band"]
    body = [[r["term"], f'{r.get("seen_on","–")}/{r.get("of","–")}', r.get("min", "–"),
             r.get("median", "–"), r.get("mean", "–"), r.get("max", "–"),
             "–".join(map(str, r["target_median"])) if "target_median" in r else r["note"],
             "–".join(map(str, r["target_leader"])) if "target_leader" in r else ""]
            for r in rs]
    src = ", ".join(p["url"] for p in pages) or "NOT FETCHED"
    return f"Counted on {len(pages)} competitor bodies: {src}\n\n" + _md(head, body)


def _md(head, body):
    line = lambda r: "| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |"
    return "\n".join([line(head), line(["---"] * len(head))] + [line(r) for r in body])


if __name__ == "__main__":
    slug = sys.argv[1]
    board = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text())
    ont = json.loads((ROOT / "data/bsuk-ontology.json").read_text())
    print(table(board, ont))
```

Note for the implementer: Check that `KM._rank` and `KM._bare` exist with `grep -n "def _rank\|def _bare" scripts/keyword_metrics.py`. If `_rank` is not there, use the same `key=` that `competitor_rows` uses at line 362.

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/py/test_term_density.py -q` → expect 3 passed.
Then run `python3 scripts/term_density.py blue-staffy-puppies-london | head -20` and check that the counts are non-zero for "blue staffy puppies"-type terms.

- [ ] **Step 5: Commit**

```bash
git add scripts/term_density.py tests/py/test_term_density.py
git commit -m "feat(board): per-term density on us and each competitor, two target bands (block 4c)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The competitor term and entity gap (`term_gap.py`)

The method answers "how do we beat them". It matches their terms type by type, then adds what at least two competitors carry and we lack. Every proposal carries its evidence, and nothing is proposed from thin air.

**Files:**
- Create: `scripts/term_gap.py`
- Test: `tests/py/test_term_gap.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/py/test_term_gap.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import term_gap as TG

A = "<html><body><main><p>Our puppies are microchipped and vaccinated. Kennel Club registered.</p></main></body></html>"
B = "<html><body><main><p>Each pup is microchipped, wormed and vaccinated by our vet.</p></main></body></html>"
C = "<html><body><main><p>Puppies leave at eight weeks with a puppy pack.</p></main></body></html>"

def test_ngram_needs_two_competitors():
    gaps = TG.phrase_gaps([A, B, C], board_terms=["kennel club"], min_pages=2)
    terms = {g["term"] for g in gaps}
    assert "microchipped" in terms and "vaccinated" in terms
    assert "puppy pack" not in terms            # only one page carries it
    assert "kennel club" not in terms           # already on the board

def test_entity_gap_uses_ontology_names_only():
    ont = {"entities": [{"id": "ont:kc", "name": "Kennel Club", "aliases": [], "class": "Organization"},
                        {"id": "ont:dogs-trust", "name": "Dogs Trust", "aliases": [], "class": "Organization"}]}
    gaps = TG.entity_gaps([A, B], ont, board_entity_ids=[])
    assert [g["id"] for g in gaps] == ["ont:kc"]
    assert gaps[0]["seen_on"] == 1
```

- [ ] **Step 2: Run to confirm it fails**

Run: `python3 -m pytest tests/py/test_term_gap.py -q` → FAIL, module missing.

- [ ] **Step 3: Implement**

```python
#!/usr/bin/env python3
"""term_gap.py — what the competitors say that our board does not (board block 5c).

Three lists, each with its evidence, none invented:
  phrase gaps  1-3 word phrases (stop words and numbers out) found on >= min_pages competitor
               bodies and absent from every board keyword; sorted by pages then total count
  entity gaps  ontology entities (name or alias) that any competitor body names and no board
               section lists; an entity not in data/bsuk-ontology.json is never proposed here —
               ontology_seed.py adds it first, with a source
  by type      the board's own keyword types against the competitor phrases, so the breeder
               sees "they have N transactional phrases, we have M"
Relationships come from the ontology's `relations` (subject, predicate, object) where both ends
are on the board or in the gap list. With no `relations` key the block says so.
"""
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
import term_density as TD     # noqa: E402

ROOT = KM.ROOT
GENERIC = frozenset("we our you your puppy puppies dog dogs page here more can will very also "
                    "all one two get any".split())


def _phrases(toks, n_max=3):
    out = collections.Counter()
    for n in range(1, n_max + 1):
        for i in range(len(toks) - n + 1):
            g = toks[i:i + n]
            if any(w.isdigit() for w in g) or g[0] in GENERIC or g[-1] in GENERIC:
                continue
            out[" ".join(g)] += 1
    return out


def phrase_gaps(htmls, board_terms, min_pages=2, limit=60):
    have = {" ".join(KM.key_words(t)) for t in board_terms}
    per_page = [_phrases(TD._body_tokens(h)) for h in htmls]
    pages, total = collections.Counter(), collections.Counter()
    for c in per_page:
        for k, v in c.items():
            pages[k] += 1
            total[k] += v
    keep = [k for k in pages if pages[k] >= min_pages and k not in have
            and not any(k in h for h in have)]
    keep.sort(key=lambda k: (-pages[k], -total[k], k))
    return [{"term": k, "seen_on": pages[k], "total": total[k]} for k in keep[:limit]]


def entity_gaps(htmls, ont, board_entity_ids):
    bodies = [" ".join(TD._body_tokens(h)) for h in htmls]
    out = []
    for e in ont.get("entities", []):
        if e["id"] in board_entity_ids:
            continue
        names = [" ".join(KM.key_words(x)) for x in [e["name"], *e.get("aliases", [])]]
        names = [n for n in names if n]
        seen = sum(1 for b in bodies if any(f" {n} " in f" {b} " for n in names))
        if seen:
            out.append({"id": e["id"], "name": e["name"], "class": e.get("class"), "seen_on": seen})
    return sorted(out, key=lambda g: (-g["seen_on"], g["name"]))


def relations(ont, ids):
    rel = ont.get("relations")
    if rel is None:
        return None
    return [r for r in rel if r.get("subject") in ids and r.get("object") in ids]


def block(board, ont, root=ROOT):
    terms, _ = KM.board_terms(board)
    pages = TD.competitor_pages(board["meta"]["slug"], [], root)
    bare = KM._bare(board["meta"]["slug"])
    htmls = [(pathlib.Path(root) / "data/queries/cache" / bare /
              f'{n}.html').read_text(errors="replace") for n in _cache_ns(bare, pages, root)]
    board_ids = [i for s in board["sections"] for i in (s.get("entities") or [])]
    pg, eg = phrase_gaps(htmls, terms), entity_gaps(htmls, ont, board_ids)
    rel = relations(ont, set(board_ids) | {g["id"] for g in eg})
    md = [f"Measured on {len(htmls)} competitor bodies (the same five as block 4b).",
          "", "**Phrases two or more competitors use and our board does not**", "",
          TD._md(["Phrase", "Pages", "Mentions"], [[g["term"], g["seen_on"], g["total"]] for g in pg])
          if pg else "None.",
          "", "**Entities competitors name that no section lists (ontology only)**", "",
          TD._md(["Entity", "Class", "Pages"], [[g["name"], g["class"], g["seen_on"]] for g in eg])
          if eg else "None.",
          "", "**Entity relationships on this page**", "",
          "NOT FETCHED — data/bsuk-ontology.json carries no `relations` key yet" if rel is None
          else TD._md(["Subject", "Relation", "Object"],
                      [[r["subject"], r["predicate"], r["object"]] for r in rel]) or "None."]
    return "\n".join(md)


def _cache_ns(bare, pages, root):
    """The cache numbers TD.competitor_pages used, recovered by URL order."""
    listed = json.loads((pathlib.Path(root) / "data/queries/raw" / bare /
                         "competitors.json").read_text())["pages"]
    urls = [p["url"] for p in pages]
    return [n for n, p in enumerate(listed, 1) if p["url"] in urls]


if __name__ == "__main__":
    slug = sys.argv[1]
    b = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text())
    o = json.loads((ROOT / "data/bsuk-ontology.json").read_text())
    print(block(b, o))
```

- [ ] **Step 4: Run tests**, then `python3 scripts/term_gap.py blue-staffy-puppies-london | head -60`. Read the phrase list by eye. If boilerplate dominates (cookie text, nav), add those words to `GENERIC`, add a test that pins the case, and re-run.

- [ ] **Step 5: Commit** — `feat(board): competitor phrase and entity gap with evidence (block 5c)` (Opus 5.5 trailer as in Task 1).

---

### Task 3: "How Google reads this page" (`serp_reading.py`, block 1b)

This is the deliverable that explains, from London's own SERP, what Google expects to see. It covers result types, PAA questions, the AI Overview, who ranks and with what page type, and maps each expectation to the board section that answers it.

**Files:** Create `scripts/serp_reading.py`; Test `tests/py/test_serp_reading.py`

- [ ] **Step 1: Failing test**

```python
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import serp_reading as SR

RESP = {"tasks": [{"result": [{"items": [
    {"type": "ai_overview"}, {"type": "organic", "url": "https://a.example/x"},
    {"type": "people_also_ask"}, {"type": "organic", "url": "https://b.example/y"}]}]}]}
SERP = {"questions": [{"text": "How much are blue Staffy puppies?", "detail": "serp_google_paa"}]}

def test_features_and_expectations():
    r = SR.read(RESP, SERP, sections=[{"id": "litter-prices", "heading": "What Do They Cost?"}])
    assert r["features"] == {"ai_overview": 1, "organic": 2, "people_also_ask": 1}
    kinds = [e["signal"] for e in r["expect"]]
    assert "ai_overview" in kinds and "people_also_ask" in kinds
    assert r["paa"][0]["answered_by"] == "litter-prices"
```

- [ ] **Step 2: Run, confirm FAIL.**

- [ ] **Step 3: Implement**

```python
#!/usr/bin/env python3
"""serp_reading.py — what Google's own results page for this query asks a page to be (block 1b).

Reads data/queries/raw/<slug>/serp_google.response.json (DataForSEO items) and serp_google.json
(the PAA questions). Every line is something the SERP shows, never a guess about the algorithm:
  features   count of each item type on page one (ai_overview, people_also_ask, local_pack, ...)
  expect     one row per feature present: what it rewards, and the board section that answers it
  paa        each PAA question with the section whose heading shares the most key words
"""
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402

ROOT = KM.ROOT
REWARDS = {
    "ai_overview": "a direct 40–60 word answer under a question heading; named entities; a source "
                   "an answer engine can quote",
    "people_also_ask": "question headings answered in the first sentence; FAQPage that matches "
                       "the visible Q&A",
    "local_pack": "a place: city named in title, H1 and copy; LocalBusiness facts that are true",
    "organic": "intent match: which page types rank (breeder, listing, guide) sets the page shape",
    "images": "original photos with descriptive alts and filenames",
    "video": "a real video with VideoObject",
    "featured_snippet": "a list, table or 40–60 word paragraph directly under the matching heading",
}


def _items(resp):
    try:
        return resp["tasks"][0]["result"][0]["items"] or []
    except (KeyError, IndexError, TypeError):
        return []


def _best(q, sections):
    qk = set(KM.key_words(q))
    score = lambda s: len(qk & set(KM.key_words(s.get("heading", ""))))
    best = max(sections, key=score, default=None)
    return best["id"] if best and score(best) else None


def read(resp, serp, sections):
    feats = dict(collections.Counter(i.get("type") for i in _items(resp)))
    expect = [{"signal": t, "count": n, "rewards": REWARDS.get(t, "shown on page one")}
              for t, n in feats.items()]
    paa = [{"q": q["text"], "answered_by": _best(q["text"], sections)}
           for q in serp.get("questions", []) if q.get("detail", "").endswith("paa")]
    return {"features": feats, "expect": expect, "paa": paa}


def block(board, root=ROOT):
    bare = KM._bare(board["meta"]["slug"])
    d = pathlib.Path(root) / "data/queries/raw" / bare
    try:
        resp = json.loads((d / "serp_google.response.json").read_text())
        serp = json.loads((d / "serp_google.json").read_text())
    except (OSError, ValueError):
        return f"NOT FETCHED — no data/queries/raw/{bare}/serp_google*.json"
    r = read(resp, serp, board["sections"])
    from term_density import _md
    return "\n".join([
        "What page one of Google shows for this query, and what each part rewards.", "",
        _md(["On page one", "Count", "What it rewards"],
            [[e["signal"], e["count"], e["rewards"]] for e in r["expect"]]), "",
        "**People Also Ask → the section that answers it**", "",
        _md(["Question", "Answered by"], [[p["q"], p["answered_by"] or "**none — gap**"]
                                         for p in r["paa"]]) if r["paa"] else "No PAA."])


if __name__ == "__main__":
    b = json.loads((ROOT / "data/boards" / f"{sys.argv[1]}.json").read_text())
    print(block(b))
```

- [ ] **Step 4: Run the tests and the London CLI.** Any PAA row reading **none — gap** is an outline gap. List it in the batch (Task 10), and do not silently add a section.
- [ ] **Step 5: Commit** — `feat(board): how Google reads this page, from the SERP (block 1b)`.

---

### Task 4: The FAQ-placement method (`faq_layout.py`, block 4d, rule text)

**The rule proposed for the breeder (two options on the batch, Task 10):**
- **Option A (Recommended): decide by intent spread.** Three blocks (top, middle, bottom) when the page's PAA and question file span three or more `query_augment.TOPICS` blocks *and* the word target is at least 2,000. Otherwise one bottom block. *Why:* London's question file already spans price, deposit, delivery, health and living. One bottom block would push the price and deposit answers, the first PAA questions on London's SERP, below 2,000 words of copy. A short blog post with one intent gains nothing from three blocks. *Trade-off:* the layout depends on data, so two blog posts can differ.
- **Option B: by page type.** Location and buy pages always get three blocks; blog, comparison, puppy and utility pages get one bottom block. *Why:* it's simple to audit. *Trade-off:* a long, multi-intent blog post loses the early answers.

**Files:** Create `scripts/faq_layout.py`; Test `tests/py/test_faq_layout.py`; Modify `rules/copy.md` (a new bullet after line 52) and `.claude/skills/bsuk-query-augmentation/SKILL.md` lines 191–194 (after the breeder's pick).

- [ ] **Step 1: Failing test**

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import faq_layout as FL

def test_option_a_three_blocks_when_intents_spread_and_long():
    qs = [{"block": "top"}, {"block": "middle"}, {"block": "bottom"}]
    assert FL.decide(qs, words=2400, page_type="blog", method="A")["layout"] == "top-middle-bottom"

def test_option_a_bottom_only_when_short():
    qs = [{"block": "top"}, {"block": "middle"}, {"block": "bottom"}]
    assert FL.decide(qs, words=1200, page_type="location", method="A")["layout"] == "bottom"

def test_option_b_by_type():
    assert FL.decide([], words=0, page_type="location", method="B")["layout"] == "top-middle-bottom"
    assert FL.decide([], words=5000, page_type="blog", method="B")["layout"] == "bottom"
```

- [ ] **Step 2: Run, FAIL.**
- [ ] **Step 3: Implement**

```python
#!/usr/bin/env python3
"""faq_layout.py — one bottom FAQ block, or top / middle / bottom (block 4d).

method A (intent spread): three blocks when the page's FAQ questions cover >= SPREAD distinct
intent groups (a question's `topic`, else its query_augment `block`) and the word target is
>= MIN_WORDS; otherwise one bottom block.
method B (page type): THREE_BLOCK_TYPES get three blocks, every other type one.
"""
MIN_WORDS = 2000
SPREAD = 3
THREE_BLOCK_TYPES = frozenset({"location", "buy"})


def decide(questions, words, page_type, method="A"):
    if method == "B":
        three = page_type in THREE_BLOCK_TYPES
        why = f"page type {page_type!r}"
    else:
        spread = len({q.get("topic") or q.get("block") for q in questions if q.get("faq", True)})
        three = spread >= SPREAD and words >= MIN_WORDS
        why = f"{spread} intent groups, {words} words (needs >= {SPREAD} and >= {MIN_WORDS})"
    return {"layout": "top-middle-bottom" if three else "bottom", "why": why, "method": method}
```

Before writing the final code, check whether `data/queries/blue-staffy-puppies-london.json` questions carry a topic key (`grep -o '"topic"' data/queries/blue-staffy-puppies-london.json | head -1`). If they do, spread uses `topic`. If not, it uses the TOPICS-assigned `block`, which spans at most 3. In that case set `SPREAD` against the TOPICS names by re-deriving them with `QA.TOPICS` regexes on the question text, and add that branch with its own test.

- [ ] **Step 4: Board block 4d** shows both methods' result for this page side by side, with method A marked *(Recommended)* and its why. It also says which layout the current London outline already has (three blocks: `faq-top`, `faq-middle`, `faq-bottom`).
- [ ] **Step 5: Commit** — `feat(board): FAQ placement decided by intent spread or page type (block 4d)`. The rule text in `rules/copy.md` and the skill goes in a separate commit **after** the breeder's pick (Task 12).

---

### Task 5: Infographic need and three styles per section (`infographic_plan.py`, block 7c)

**Rule:** the 4–5 OG photo slots (Task 6) are decided first. A body H2 or H3 then gets an infographic slot when its heading or its outline `why` matches an IG trigger:

- IG-1: price, cost, how much, £;
- IG-2: deposit, steps, how to, process, timeline;
- IG-3: vs, versus, difference, or;
- IG-4: checklist, what to check, paperwork, health test;
- IG-5: delivery, collection, from Carlisle to.

That trigger list is the one in `.claude/skills/bsuk-infographic/SKILL.md`. Each needing section shows three style variants of its IG type, rendered with the site tokens (Plate, Ruled and Card), at 1280, 768 and 375, as radio `pick-ig:<slot>`.

**Files:** Create `scripts/infographic_plan.py`, `tests/py/test_infographic_plan.py`; previews are written to `docs/artifacts/boards/ig/<slug>/<slot>-<style>.html`.

- [ ] **Step 1: Failing test**

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import infographic_plan as IP

SECS = [{"id": "delivery", "heading": "How Will My Puppy Get From Carlisle to London?", "tree": []},
        {"id": "litter-prices", "heading": "What Do They Cost?", "tree": []},
        {"id": "london-life", "heading": "Will a Blue Staffy Be Happy Living in London?", "tree": []}]

def test_triggers_pick_ig_type():
    plan = IP.plan({"sections": SECS, "assets": []})
    got = {p["section"]: p["ig"] for p in plan}
    assert got == {"delivery": "IG-5", "litter-prices": "IG-1"}

def test_three_styles_each():
    for p in IP.plan({"sections": SECS, "assets": []}):
        assert [s["id"] for s in p["styles"]] == ["plate", "ruled", "card"]

def test_existing_slot_kept():
    assets = [{"slot": "deposit-steps", "kind": "infographic", "infographic_style": "IG-2",
               "section": "deposit-viewing"}]
    plan = IP.plan({"sections": [{"id": "deposit-viewing", "heading": "Deposit", "tree": []}],
                    "assets": assets})
    assert plan[0]["slot"] == "deposit-steps" and plan[0]["ig"] == "IG-2"
```

- [ ] **Step 2: Run, FAIL.**
- [ ] **Step 3: Implement**

```python
#!/usr/bin/env python3
"""infographic_plan.py — which sections need an infographic, which IG type, three styles each.

Triggers are the bsuk-infographic skill's type table; first match wins in IG order 5,1,3,2,4 (a
delivery heading that also says "cost" is a route, not a price panel). Headings are the section
heading and every H3 in its `tree`. An infographic slot already on the board keeps its slot id
and IG type. Styles are visual treatments of the same content on the same tokens:
  plate  steel band, figures large, bone text          (pairs with city-price-scale)
  ruled  hairline rules on bone, ledger rhythm          (pairs with city-faq-ledger)
  card   white card, iris accent rail, icon per item    (pairs with city-chapters)
"""
import re

TRIGGERS = [
    ("IG-5", r"\bdeliver|\bcollect|\bfrom carlisle\b|\btravel"),
    ("IG-1", r"\bcost|\bprice|\bhow much\b|£"),
    ("IG-3", r"\bvs\b|\bversus\b|\bdifference\b|\bor (american|pit)"),
    ("IG-2", r"\bdeposit\b|\bsteps?\b|\bhow to\b|\bprocess\b|\btimeline\b"),
    ("IG-4", r"\bchecklist\b|\bwhat to check\b|\bpaperwork\b|\bhealth test"),
]
STYLES = [{"id": "plate", "label": "Plate"}, {"id": "ruled", "label": "Ruled"},
          {"id": "card", "label": "Card"}]


def _headings(sec):
    out = [sec.get("heading", "")]
    stack = list(sec.get("tree") or [])
    while stack:
        n = stack.pop(0)
        out.append(n.get("text") or n.get("heading") or "")
        stack[:0] = n.get("children") or []
    return out


def _ig(text):
    for ig, rx in TRIGGERS:
        if re.search(rx, text, re.I):
            return ig
    return None


def plan(board):
    existing = {a.get("section"): a for a in board.get("assets", []) if a.get("kind") == "infographic"}
    out = []
    for s in board["sections"]:
        if s["id"] in existing:
            a = existing[s["id"]]
            out.append({"section": s["id"], "slot": a["slot"], "ig": a.get("infographic_style"),
                        "styles": STYLES})
            continue
        if s["id"].startswith(("faq-", "review-")) or s.get("shape") in ("hero", "form"):
            continue
        ig = next((g for g in map(_ig, _headings(s)) if g), None)
        if ig:
            out.append({"section": s["id"], "slot": f'{s["id"]}-ig', "ig": ig, "styles": STYLES})
    return out
```

Before running against London, confirm the real shape of an asset's section link. The `deposit-steps` asset may name its section under another key; check with `python3 -c "import json;print([a for a in json.load(open('data/boards/blue-staffy-puppies-london.json'))['assets'] if a['kind']=='infographic'])"`, and match `existing` to the key the record actually uses. Likewise check the `tree` node keys (`text` vs `heading`) on section 8.

- [ ] **Step 4: Previews.** Add `render_preview(slot_plan, style, facts) -> html`, which writes one standalone HTML per (slot, style) using `src/styles/tokens.css` values inlined. The content comes only from the section's outline facts and the `data/*.json` keys the section already cites: prices from `data/price-matrix.json`, the delivery band from `data/settings.json`. The route map is schematic, Carlisle to London, never map tiles. Test that a preview contains the section's figures and no `£` value absent from the data files.
- [ ] **Step 5:** Invoke the `frontend-design:frontend-design` skill on the three styles for one slot, then the rest (working rule 10: shown in the browser, never described). Use `mcp__Claude_Browser__preview_start` with the file URL at 375 / 768 / 1280.
- [ ] **Step 6: Commit** — `feat(board): infographic need per section, three styles each (block 7c)`.

---

### Task 6: 4–5 OG image slots per page (`og_slots.py`, block 7d)

The breeder wrote "OG images: 4-5 per page". IMAGE-DESIGNS.md §1 says one share card per page, so this changes a locked rule. The plan builds the slot proposal and puts the interpretation to the breeder on the batch (Task 10), with two options:

- **(a) Recommended:** 4–5 *generated* photo slots per page (Gemini, IMAGE-DESIGNS framing styles A/C/D/E/H; B stays social-only). Slot 1 is the share card (`og:image`, 1200×630) recomposed from the hero subject; slots 2–5 go on the highest-intent body H2s that have no photo of their own. *Why:* London's 28 photo slots are all reused photos, none of London (board batch 2026-09-30), and Google Images ranks original images. *Trade-off:* each one is a STOP 4 approval and a Gemini call.
- **(b):** 4–5 `og:image` meta tags. *Trade-off:* Google and most social platforms read only the first, so slots 2–5 would do nothing.

**Files:** Create `scripts/og_slots.py`, `tests/py/test_og_slots.py`.

- [ ] **Step 1: Failing test**

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import og_slots as OG

def test_four_to_five_slots_share_card_first():
    secs = [{"id": f"s{i}", "heading": f"H{i}", "intent": "transactional" if i < 3 else "info"}
            for i in range(8)]
    slots = OG.propose({"sections": secs, "assets": []}, n=5)
    assert slots[0]["slot"] == "og-share" and slots[0]["w"] == 1200 and slots[0]["h"] == 630
    assert 4 <= len(slots) <= 5
    assert all(s["og_style"] in "ACDEH" for s in slots)
```

- [ ] **Step 2: Run, FAIL.**
- [ ] **Step 3: Implement** `propose(board, n=5)`:
  - Slot 0 is `og-share`, 1200×630, `og_style` "C" (Editorial Split), with the subject taken from the hero asset's alt.
  - The remaining `n-1` slots go to sections in board order, transactional intent first. Skip FAQ, review, newsletter and form sections, and skip any section whose image slot is the page's own migrated image.
  - Each slot gets `source: "generate"`, `og_style` cycled through A/E/D/H, `status: "proposed"`, and a `prompt_brief` taken from the section heading plus IMAGE-DESIGNS' negative list (natural ears, no chains or spiked collars, no bully-XL build).
- [ ] **Step 4: Board block 7d** renders the slots with radio `pick-og:<slot>` (values `use` / `skip`). Do **not** add these to `SIGNATURE_SECTIONS` until the breeder answers the interpretation question.
- [ ] **Step 5: Commit** — `feat(board): 4–5 OG slot proposals, share card first (block 7d)`.

---

### Task 6b: Gemini usage log and the key-deletion reminder (user, 2026-10-02)

The breeder supplied a key for this project and will delete it at the end. They asked for "strong monitoring and logging" of its use.

**Files:** Create `scripts/gemini_log.py`, `tests/py/test_gemini_log.py`. Modify `.claude/skills/bsuk-image-generation/SKILL.md` (every generate call goes through the logger). Modify `.claude/skills/session-closer/SKILL.md` and `.claude/skills/session-handoff/SKILL.md` (Task 9), adding the reminder. Modify `.gitignore` if the log should stay local.

- [ ] **Step 1: Failing tests.**
  - `log_call(model, slot, status, note="", path=tmp)` appends one JSON line `{ts, model, slot, status, note}`.
  - `summary(path)` returns calls today, calls in total, and failures by status code.
  - A line never contains the value of `GEMINI_API_KEY` (set a fixture env value and assert it is absent from the file), nor any token matching `AQ\.|AIza`.
- [ ] **Step 2:** Implement. The log is `docs/reports/gemini-usage.jsonl`. The CLI is `python3 scripts/gemini_log.py summary`.
- [ ] **Step 3:**
  - The image-generation skill wraps every call: `log_call(...)` on success and on every exception, recording the status code (e.g. 402).
  - session-closer and session-handoff print `summary` plus the line "GEMINI_API_KEY is set in .env: delete it when image work is done (breeder's instruction, 2026-10-02)", whenever `.env` holds the key. They check without printing it.
- [ ] **Step 4:** Back-fill three lines for today's calls: the two 402s on gemini-3-pro-image-preview and gemini-2.5-flash-image, and the 404 on gemini-2.5-flash. The model names and status codes are as reported in this session.
- [ ] **Step 5: Commit** with the message `feat: Gemini usage log (no key ever written) and the delete-the-key reminder`.

A status-line mod showing "Gemini: N calls today" is one of the mod options on the decisions batch (Task 10, Q5).

---

### Task 7: Wire the blocks into the board

**Files:** Modify `scripts/build_page_board.py` (imports at the top; `render()` around lines 896, 949–960 and 1001–1008; `SIGNATURE_SECTIONS` around line 1081). Modify `tests/py/test_page_board.py`.

- [ ] **Step 1: Failing test** in `tests/py/test_page_board.py`:

```python
def test_v2_blocks_on_new_family_only():
    import build_page_board as BPB, pageboard as PB
    london = json.loads((ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())
    ont = json.loads((ROOT / "data/bsuk-ontology.json").read_text())
    html = BPB.render(london, ont, LEDGER_EMPTY, live={}, thumbs={}, slug="blue-staffy-puppies-london")
    for t in ["1b. How Google reads this page", "4c. Term density against competitors",
              "4d. FAQ placement", "5c. What competitors say that we do not",
              "7c. Infographics", "7d. OG images"]:
        assert f'data-title="{t}"' in html
    old = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "4c. Term density" not in old
```

(Use the `ROOT` and `json` names that the file already imports. If the London render needs the `previews`, `routes` or `images` arguments, pass what `main()` passes.)

- [ ] **Step 2: Run, FAIL.**
- [ ] **Step 3: Implement.** Inside `render()`, after block 1 (line ~894):
```python
    if new_family:
        parts.append(("1b. How Google reads this page", SR.block(board)))
```
After block 4b (line ~956):
```python
        parts.append(("4c. Term density against competitors", TD.table(board, ont)))
        parts.append(("4d. FAQ placement", FL.block(board)))
```
After block 5 (line ~960):
```python
    if new_family:
        parts.append(("5c. What competitors say that we do not", TG.block(board, ont)))
```
After block 7b (line ~1008):
```python
        parts.append(("7c. Infographics", IP.block(board)))
        parts.append(("7d. OG images", OG.block(board)))
```
Add `import serp_reading as SR, term_density as TD, faq_layout as FL, term_gap as TG, infographic_plan as IP, og_slots as OG` beside the existing `import keyword_metrics as KM`, and give `faq_layout`, `infographic_plan` and `og_slots` a `block(board)` that returns markdown. Then add `[f"ig:{p['slot']}" for p in IP.plan(board)]` to the list `SIGNATURE_SECTIONS` is built from, so the approve button refuses until every infographic style is picked.
- [ ] **Step 3b: Items carried from the Task 1–5 reviews.**
  - **Block 4c:** print the "this differs from block 4b's five" clause only when a listing page was actually skipped.
  - **Block 1b:** "no breeder site ranks" becomes "no page classed as a breeder page".
  - **Block 7c fonts:** publish `public/fonts/*.woff2` once as Artifact `files` and pass the matching `font_base` to the infographic previews.
  - **Infographic placement:** each new infographic slot (litter-prices, delivery, health-tests, paperwork, breed) sits *beside* the H2's existing photo slot, never in place of it; the breeder can overrule this on the batch.
  - **Signature section:** the breed-split slot is not added to `SIGNATURE_SECTIONS` until the breeder answers the batch question on it.
- [ ] **Step 4:** Run `npm run test:py`. Every pre-rule board test must stay byte-identical.
- [ ] **Step 5: Commit** — `feat(board): v2 blocks 1b, 4c, 4d, 5c, 7c, 7d on project 5 boards`.

---

### Task 8: Home for the method: skill `bsuk-competitor-parity`

**Recommendation (working rule 4).** Make one new skill and no new agent.
- **Why:** the counting is now in scripts (Tasks 1–3). What's missing is the *method*: match each keyword type, close the 2+-page gaps, then beat them on evidence they lack, such as our parents, our paperwork and our video. That is a judgment workflow, which is a skill's job. `bsuk-entity-incorporation-agent` already runs the per-section entity loop and only needs a pointer.
- **Trade-off:** one more skill to keep in the registry.

**Files:** Create `.claude/skills/bsuk-competitor-parity/SKILL.md`. Modify `.claude/skills/bsuk-entity-agent/SKILL.md`, `.claude/agents/bsuk-keyword-verifier.md` and `.claude/agents/bsuk-entity-incorporation-agent.md` (add one "See also" line each). Modify `docs/reference/system-registry.md`.

- [ ] **Step 1:** Write the SKILL.md with frontmatter `name: bsuk-competitor-parity` and a description starting "Use when a BSUK board or page must match or beat competitors on keywords and entities…". It has these sections:
  - When: page-run rows 6, 7 and 10.
  - Run: `term_density.py`, `term_gap.py`, `serp_reading.py`.
  - Read the numbers: median band vs leader band, and the breeder's pick.
  - Beat them: type-by-type table; a gap enters a section only when it is true for us and sourced (`data/*.json`, ontology, evidence ledger), otherwise `NOT FETCHED`; never stuff past the band's upper bound.
  - Entity relationships: only ontology `relations`.
  - What fails: a term with no competitor page behind it; a count above the band.
- [ ] **Step 2:** `python3 scripts/build_agent_registry.py --check` and `npm run check:markers` must both be green.
- [ ] **Step 3: Commit** — `skill: bsuk-competitor-parity — match type by type, close 2+-page gaps, beat on evidence`.

---

### Task 9: Session handoff skill and today's prompt

There is no handoff skill today. `session-closer` fills the brief's "What's Next", and `grill-me --resume` resumes an interview. Neither one produces a paste-ready prompt for a new chat.

**Files:** Create `scripts/session_handoff.py`, `tests/py/test_session_handoff.py` and `.claude/skills/session-handoff/SKILL.md`. Output goes to `docs/reference/handoff/<date>-<branch>.md`.

- [ ] **Step 1: Failing test:** `build(root, branch)` returns markdown containing:
  - the branch and HEAD sha;
  - the worktree path;
  - each `## Open Flags` line of the newest `docs/superpowers/sessions/*-session-brief.md`;
  - the newest plan's first unchecked `- [ ]` task heading;
  - every `https://claude.ai/artifact/` URL in the last 5 answer-board batch files;
  - the six standing working-rule numbers.

  Use a tmp_path fixture with a fake brief, plan and batch.
- [ ] **Step 2: Run, FAIL.**
- [ ] **Step 3: Implement** with `subprocess` git calls (`rev-parse`, `worktree list`, `log --oneline -10`) and pathlib globbing. Print to stdout and write the file. Never read `.env`, and never print anything matching `KEY|TOKEN|SECRET`. Add a test that a fixture `.env` value never appears in the output.
- [ ] **Step 4:** Write SKILL.md. Trigger: "handoff", "continue in a new chat", "session handoff". Steps:
  1. Run `session-closer` if the brief's What's Next is empty.
  2. Run `python3 scripts/session_handoff.py`.
  3. Publish the output as the handoff Artifact (update in place if one exists), with copy buttons.
  4. Paste the prompt in chat.
- [ ] **Step 5:** Run it now and publish. Today's prompt is below; the script must reproduce its facts.
- [ ] **Step 6: Commit** — `skill: session-handoff — paste-ready new-chat prompt from git, brief, plan and boards`.

**Today's handoff prompt (hand-written; Task 9 automates it):**

```text
Continue BlueStaffyUK project 5, London page. Work locally in the worktree
/Users/apple/Downloads/BSUK/BSUK-london on branch london-components (do not cd elsewhere;
commit after each task; do not push unless I say so).

State: London is at STOP 3 (page board), not approved. Board v2 is being built from
docs/superpowers/plans/2026-10-02-london-board-v2.md — open it and continue at the first
unchecked task. The page-run plan this sits inside is
docs/superpowers/plans/2026-09-30-london-page-run.md (Task 23 = STOP 3).

Boards: answer board https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf ·
London page board https://claude.ai/artifact/CbemmwUeW5qGEmEFog7ezz.
Watch both with ArtifactComments at session start.

Read first: CLAUDE.md, docs/reference/page-run.md, the newest
docs/superpowers/sessions/*-session-brief.md, and memory MEMORY.md.
GEMINI_API_KEY is set in .env (load with set -a; . ./.env; set +a).
Cloud history: origin/london-components-98b173 was merged home 2026-10-02 (cherry-pick).
```

---

### Task 10: The decisions batch on the answer board

**Files:** Create `docs/reference/answer-board/batches/2026-10-02-london-board-v2.md` (the sheet). The `.json` is generated from it.

- [ ] **Step 1:** Write the sheet in the README format (`# Title`, `## Section`, `N. **Question?** context`, `- (a)` options). Each question marks one option **(Recommended)** with a Why and a trade-off (working rule 4). The questions:
  1. **Density target (4c):**
     - (a) median band (Recommended): matches what ranks, with no stuffing risk under Google's spam policies;
     - (b) leader band.
  2. **FAQ placement method (4d):**
     - (a) intent spread (Recommended), with the Why and trade-off from Task 4;
     - (b) page type.
  3. **"OG images 4–5 per page" means:**
     - (a) 4–5 generated photo slots, share card first (Recommended);
     - (b) 4–5 og:image tags.
  4. **Components going forward:** "every remaining page gets new or refreshed components per section, from its outline's section count":
     - (a) yes, recorded in page-run row 10 and as a standing rule (Recommended);
     - (b) London only.
  5. **Claude mods: which first?** Mods are small plugins that hot-reload inside this Claude Code session. They can add a status-line entry, a band above the prompt, a side pane, a toast, a slash command, or a hook that blocks or reacts to a tool call.
     - (a) a BSUK status line: branch · page · STOP n · last `check:all` result (Recommended: always visible, read-only, the lowest risk);
     - (b) a toast plus a band when an answer-board batch is received;
     - (c) a hook that refuses `git commit` while `check:all` last failed;
     - (d) a STOP-tracker side pane.
  6. **What else the board should carry** (multi-select):
     - (a) a SERP snippet preview (title and meta as Google shows them, at desktop and mobile widths);
     - (b) a schema preview (the JSON-LD nodes the page will emit);
     - (c) an internal-link map (in and out, with anchors);
     - (d) a page-weight and LCP budget per section.

     Recommended: (a) and (b). The SERP data and the schema builder already exist, so these are cheap. Trade-off: (c) and (d) wait for the build.
  7. **PAA gap from block 1b: "How rare are blue Staffies?"** has no section.
     - (a) answer it in the bottom FAQ block, from the coat facts we already hold (Recommended);
     - (b) add an H3 under the breed section.
     - (c) leave it.
  8. **Density pool (block 4c):** only 2 of London's 9 competitors are prose pages; the other 7 are listing grids.
     - (a) keep listings out of the density bands, flagged as a thin pool (Recommended): listing card text isn't prose a page should copy;
     - (b) count listings too.
  9. **Breed-split infographic (IG-3, "Pit Bulls or American Staffies?"):** no data file holds breed-standard figures, so it would render as NOT FETCHED.
     - (a) drop the slot (Recommended);
     - (b) supply a breed-standard data file with sources first.
  10. **Infographic beside or instead of the H2 photo:**
      - (a) beside it (Recommended): working rule 11 keeps the served photos and their alts;
      - (b) instead of it.
  11. **Competitor words to adopt (block 5c):** tick the phrases that are true for us. The candidates are the 2–3 word phrases found on three or more competitor domains, e.g. vet checked, KC registered, mum & dad, ready to leave, family home, microchipped, wormed, vaccinated. Each one goes into a section's keywords only when a data file backs it.
- [ ] **Step 2:** `python3 scripts/answer_board_batch.py docs/reference/answer-board/batches/2026-10-02-london-board-v2.md --project "London page board v2" --date 2026-10-02`
- [ ] **Step 3:** ArtifactData `set`: collection `batches`, doc_id = the printed batch id, file_path = the JSON, url https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf.
- [ ] **Step 4: Commit** both files. Chat says only "N new questions on the board: <link>".

---

### Task 11: Rebuild and republish board v2 (same URL)

- [ ] **Step 1:** Run, in order: `npm run -s build`, then `python3 scripts/build_board_previews.py blue-staffy-puppies-london`, then `python3 scripts/build_page_board.py blue-staffy-puppies-london`. Each must exit 0.
- [ ] **Step 2:** Open the HTML in the browser pane at 1280 and 375. Check that every new block renders, that the infographic iframes load, and that the approve button refuses with no infographic picks.
- [ ] **Step 3:** Run the Artifact tool's `read` on https://claude.ai/artifact/CbemmwUeW5qGEmEFog7ezz first (rule: read before republish). Then `publish` with `url` set to that, `file_path` set to the HTML, and the existing capabilities kept (omit `capabilities`). Confirm that the approval db is still empty, or that its `record_hash` mismatch is shown as "the record changed since this pick".
- [ ] **Step 4:** Commit the regenerated `docs/artifacts/boards/*.html` and the IG previews.

### Task 12: Gates, close and memory

- [ ] **Step 1:** Run `npm run test:py`, `npm run -s build && npm run check:all`, and `npm run test:render:meta`. Paste the counts into the commit message. Invoke `superpowers:verification-before-completion` before saying "done".
- [ ] **Step 2:** Close KI 70 in `docs/reference/session-log.md`, citing the smoke image's report path and the `og:B:<sha12>` it printed.
- [ ] **Step 3:** After the breeder answers, write the picked FAQ rule into `rules/copy.md` and the query-augmentation skill, and add a `data/quality/rule-index.json` row (`enforced: test`, test `tests/py/test_faq_layout.py`). Record the component rule in page-run row 10. If OG (a) is picked, amend IMAGE-DESIGNS.md §1 and add `pick-og:*` to `SIGNATURE_SECTIONS`.
- [ ] **Step 4:** Run the `session-closer` skill, then `session-handoff`. Update memory `bsuk-london-components-status.md`.
