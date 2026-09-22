# Query Augmentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every BSUK page builder a mechanical question-finding step. The step turns search, AI-engine, Reddit and bank questions into a per-page question file. A gate then holds the built page to that file, to the three-block FAQ, and to the rule "competitors' section count + 3".

**Architecture:** Two skills (`bsuk-query-augmentation`, `bsuk-reddit-threads`) do the fetching. The DataForSEO connector covers search results and AI-engine answers; the `research-recency` ladder covers Reddit. The skills write normalised candidate files under `data/queries/raw/<slug>/`. `scripts/query_augment.py` never calls a paid service: it merges and scores the candidates, caps spend, and writes `data/queries/<slug>.json`. `scripts/query_coverage_check.py` then reads the built `dist/` page against that file, as part of `npm run check:all`.

**Tech Stack:** Python 3 (stdlib `html.parser`, `jsonschema` 4.23), pytest, npm scripts, Claude Code skills (markdown), the DataForSEO + Firecrawl connectors.

**Spec:** `docs/superpowers/specs/2026-09-23-query-augmentation-design.md` (Artifact https://claude.ai/artifact/NQEi9YDH8oLsjtbMDsPFVj).

**Branch:** `query-augmentation` in `/Users/apple/Downloads/BSUK` (cut from `foundation` at `db37ca1`). Never push; there is no remote.

**Every commit ends with:**
```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
```
Subagents: use exactly this line and never substitute your own model name.

**Execution:** subagent-driven. Each task gets an Opus implementer, a spec reviewer and a quality reviewer, with re-review until both pass. Only one writer works in the worktree at a time.

---

## Execution notes (read before Task 1)

- **Plan refinement of spec §3, step 2.** The skill stores each connector response untouched as `raw/<slug>/<source>.response.json`, for audit only. It also writes a **normalised** `raw/<slug>/<source>.json`, and that normalised file is the only thing the script reads. This keeps the script independent of the connector's response shape, which we have not yet seen. Both formats are defined in Task 2.
- **The FAQ floor is effectively 17.** The template's block minimums (5 + 5 + 7) add up to more than its stated "15–20 total". The script fills every block minimum, so a page carries 17–20 questions. The gate still checks 15–20 in total and each block's own range, so both rules from the template are enforced.
- **The budget is per page per day and total.** Spec §8 says the cap applies to "one run". Here a run means that page's paid calls on one UTC day (`query_budget_usd`). A second cap, `query_total_budget_usd = 1.00`, reflects the $1 in the account.
- **Fact lint applies to every new skill and agent line.** Only locked £ amounts are allowed (£500, £1,500, £1,700, £200, £350, £200–£350, £1,500–£1,700). No year counts except 12–14. "DEFRA" only next to "transport". No US states. The words USDA, Glasgow and captive are banned. Dollar amounts such as "$0.50" are allowed because the lint reads only `£`.
- **Registries.** Any task that adds a script or a `data/` entry runs `python3 scripts/build_system_registry.py` before committing, or `npm run registry` fails.

## File map

| File | Responsibility | Task |
|---|---|---|
| `docs/reference/location-page-template.md` | The Illinois template converted to BSUK | 1 |
| `schemas/queries.schema.json` | Question-file contract | 2 |
| `scripts/query_augment.py` | Normalise, merge, score, pick FAQ/extras, section target, preflight, spend log, CLI | 2–5 |
| `tests/py/test_query_augment.py` | Its tests | 2–5 |
| `data/settings.json` | `query_budget_usd`, `query_total_budget_usd`, `query_typical_call_usd` | 4 |
| `scripts/query_coverage_check.py` | The gate | 6 |
| `tests/py/test_query_coverage_check.py` | Its tests | 6 |
| `package.json`, `tests/py/test_package_scripts.py` | `check:queries` in `check:all` | 6 |
| `data/queries/…` | Pilot output (Manchester) | 7 |
| `.claude/skills/bsuk-reddit-threads/SKILL.md` | Thread sourcing | 8 |
| `.claude/skills/bsuk-query-augmentation/SKILL.md` | The orchestrating skill | 9 |
| `.claude/skills/bsuk-location-page-builder/SKILL.md` | Steps 1 and 5 rewritten | 10 |
| `.claude/skills/bsuk-{comparison-page-builder,blog-post,puppy-page-builder}/SKILL.md` | Call the skill | 10 |
| `tests/py/test_agent_facts.py` + 3 residue files | Parrot-residue ban and scrub | 11 |
| `data/port-manifest.json`, `docs/reference/session-log.md`, registries | Housekeeping | 12 |
| `docs/reports/query-augmentation-gate-report.md` | Close-out | 13 |

---

### Task 1: Convert the Illinois template to BSUK

**Files:**
- Create: `docs/reference/location-page-template.md`
- Source (read only): `/Users/apple/Downloads/bluestaffyuk-cms/Illinois PAGE.txt`

This document is prose, so no pytest is written for it. It is guarded by the existing path guard (`tests/py/test_rules_index.py`, `tests/py/test_claude_md.py`) and the marker gate, and both must stay green.

- [ ] **Step 1: Read the source template in full**

Read `/Users/apple/Downloads/bluestaffyuk-cms/Illinois PAGE.txt` (793 lines) end to end. Then read `.claude/skills/bsuk-location-page-builder/SKILL.md` lines 28–50 for the fact table a city page may state.

- [ ] **Step 2: Write the converted template**

Create `docs/reference/location-page-template.md` with exactly this content:

````markdown
# Location page template (BSUK)

The user's location-page template (supplied as a Maltipoo/Maltese state-page brief for another
breeder), converted to BlueStaffyUK. `.claude/skills/bsuk-location-page-builder/SKILL.md` builds
from this document; where the two disagree, the skill's fact table wins for facts and this
document wins for structure, FAQ format and tone.

## What a city page is for

One UK city, one buyer: someone near that city deciding whether to buy a blue Staffordshire
Bull Terrier puppy from Lisa Bright in Carlisle · Cumbria. The page answers what that buyer
asks, in the order they ask it, with the city's own geography — not the same page with a new
city name.

## Section count — competitors decide, never a fixed number

1. Pool: the top-5 breeder or location pages for the city query on Google plus the top-5 on
   Bing, merged. Marketplaces and directories are excluded.
2. Strip non-content H2s: sidebar, footer, related posts, repeated calls to action, reviews
   and FAQ headings (ours are frame, so theirs are not counted either).
3. Match the highest cleaned H2 count in the pool. If it is more than 1.5× the next highest
   it is an outlier: record it and match the next highest.
4. Add three sections: the strongest topics in the page's question file that no pooled page
   covers (`extra_sections` in `data/queries/<slug>.json`).
5. Only body H2s count, on both sides. The fixed frame below is never counted.

`scripts/query_augment.py` computes this; `scripts/query_coverage_check.py` fails a built
page that falls short.

## The fixed frame

Hero (H1, image first) · counter strip · trust strip · table of contents · key takeaways
(3–5 bullets, `id="key-takeaways"`) · review top · review middle · review bottom · newsletter ·
enquiry form · FAQ top · FAQ middle · FAQ bottom. Body sections sit between them; the FAQ
blocks sit at the top, middle and bottom of the body as in the source template.

## FAQ format

- Three blocks: **top** 5–7 questions (buying and logistics — price, deposit, delivery to this
  city, reserving), **middle** 5–7 (process and trust — paperwork, health testing, visiting,
  age at collection), **bottom** 7–10 (breed and lifestyle — flats, children and other pets,
  training, the 12–14 year lifespan, coat). 17–20 questions in practice.
- Every question is an H3. A concise, direct answer follows it. Internal and external links
  sit inside answers, anchor first.
- Questions are written the way buyers ask them aloud ("Do you deliver Staffy puppies to
  Manchester?"), taken from the page's question file, never invented.
- FAQPage schema carries exactly the visible questions.

## Headers and paragraphs

- Every H1–H6 has a one-to-two-sentence opening paragraph that restates what the heading
  promises.
- Subheaders are long-form, conversational, Reddit-style questions where the topic allows.
- Short paragraphs (two to four sentences), bullets for scanning, bold for the one fact a
  skimmer must not miss, a subheader every 200–300 words.

## Links

- Anchors start the sentence or paragraph, never trail it.
- Vary anchor text: exact, partial, descriptive. Never "click here".
- Internal: every relevant BSUK page at least once — available puppies, the buying guide,
  the breed guide, health, delivery and pricing wording, about, contact, 3–5 nearby city
  pages — then varied repeats where they genuinely help. The source template's "50+ internal
  links" assumed a larger site; BSUK has 11 pages plus 28 cities.
- External: breed and health authorities only (The Kennel Club, the breed's DNA-test bodies,
  UK government pages for the law sections). Never a competitor, a marketplace, or a local
  business BSUK has not verified.

## Topics carried over from the source, converted

| Source topic | BSUK version |
|---|---|
| Why choose the breeder | Lisa Bright, home-raised litters, Carlisle · Cumbria — only facts in the skill's fact table |
| Available puppies by type | The litter in `data/puppies.json`: £1,500 and £1,700 pups, deposit £500 refundable |
| Temperament | Staffordshire Bull Terrier temperament, sourced from the breed guide page |
| Health and wellness | DNA tests the breed is screened for, only where the evidence ledger records them |
| Grooming | Short coat, nail, ear and teeth care |
| Training | Positive-reinforcement basics, socialisation |
| Delivery to the state, airports | Delivery to the city: £200–£350 priced by distance by DEFRA-approved transport, or collection from Carlisle; the main roads and stations that link the city to Cumbria |
| Cities served | Nearby BSUK city pages from `data/locations.json` |
| Dog-friendly activities, parks | Real local walks and parks the page can name and link |
| Climate | The city's weather and what it means for a short-coated dog |
| Pricing and payment | Locked prices and deposit only |
| Testimonials | The three real reviews in `data/reviews.json`, rotated; `REVIEW_PLACEHOLDER` slots otherwise |
| Regulations | UK law a buyer asks about: the Dangerous Dogs Act (the Staffordshire Bull Terrier is not a banned breed), microchipping; any licence line is `LICENCE_CLAIM_PLACEHOLDER` |
| Preparing your home | Puppy-proofing and the first week |
| Newsletter | The site's real newsletter form; no subscriber count |
| Final call to action | Enquiry form, email, `PHONE_PLACEHOLDER` until launch |

## Dropped from the source, and why

The source's breeder claims belong to another business: its years in business, its
multi-year health guarantee, its neurological-stimulation and puppy-culture programmes, its
US DNA-testing provider, its US federal licence, its subscriber count, its business-bureau
rating and its invented-format testimonials. None is a BSUK fact. The fixed 22-section
structure is replaced by the competitor rule above; the 4,500-word target and "150+
entities" become "as many real local entities as the city supports, none invented".
````

- [ ] **Step 3: Run the guards**

Run: `python3 -m pytest tests/py/test_rules_index.py tests/py/test_claude_md.py -q && python3 scripts/marker_check.py`
Expected: all pass; marker check prints `0 problems`.

If the path guard flags `data/queries/<slug>.json` as a cited path that does not exist, change it in the document to `data/queries/` plus the words "one file per page". The directory is created in Task 7; rerun the guards after Task 7.

- [ ] **Step 4: Commit**

```bash
git add docs/reference/location-page-template.md
git commit -m "reference: the location page template, converted from the user's brief to BSUK

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Question-file schema and the normalise/topic/fact helpers

**Files:**
- Create: `schemas/queries.schema.json`
- Create: `scripts/query_augment.py`
- Create: `tests/py/test_query_augment.py`

Normalised candidate file format (`data/queries/raw/<slug>/<source>.json`, where source is one of `serp_google`, `serp_bing`, `ai_engines`, `threads`), written by the skills:

```json
{
  "source": "serp_google",
  "status": "ok",
  "fetched": "2026-09-23",
  "questions": [ { "text": "How much is a blue Staffy puppy?", "detail": "serp_google_paa", "fact_source": null } ]
}
```

Competitors file (`data/queries/raw/<slug>/competitors.json`):

```json
{ "status": "ok", "pages": [ { "url": "https://…", "google_pos": 1, "bing_pos": null, "h2": ["…"] } ] }
```

- [ ] **Step 1: Write the schema**

Create `schemas/queries.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bluestaffyuk.local/schemas/queries.schema.json",
  "title": "BSUK page question file",
  "description": "data/queries/<slug>.json — written by scripts/query_augment.py, completed by the page builder (covered_by, extra_sections[].heading), gated by scripts/query_coverage_check.py.",
  "type": "object",
  "additionalProperties": false,
  "required": ["slug", "page_type", "primary_keyword", "route", "fetched", "spend_usd", "sources",
               "competitors", "section_target", "extra_sections", "questions"],
  "properties": {
    "slug": {"type": "string", "pattern": "^[a-z0-9-]+$"},
    "page_type": {"enum": ["location", "comparison", "blog", "puppy"]},
    "primary_keyword": {"type": "string", "minLength": 1},
    "route": {"type": "string", "pattern": "^/([a-z0-9-]+/)*$"},
    "fetched": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
    "spend_usd": {"type": "number", "minimum": 0},
    "sources": {"type": "object", "additionalProperties": {"type": "string"}},
    "competitors": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["url", "google_pos", "bing_pos", "h2_raw", "h2_clean", "outlier"],
        "properties": {
          "url": {"type": "string"},
          "google_pos": {"type": ["integer", "null"]},
          "bing_pos": {"type": ["integer", "null"]},
          "h2_raw": {"type": "integer", "minimum": 0},
          "h2_clean": {"type": "integer", "minimum": 0},
          "outlier": {"type": "boolean"}
        }
      }
    },
    "section_target": {
      "type": "object", "additionalProperties": false,
      "required": ["matched", "set_by", "extra", "total"],
      "properties": {
        "matched": {"type": "integer", "minimum": 0},
        "set_by": {"type": ["string", "null"]},
        "extra": {"type": "integer", "minimum": 0},
        "total": {"type": "integer", "minimum": 0}
      }
    },
    "extra_sections": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["topic", "uncovered", "question_ids", "heading"],
        "properties": {
          "topic": {"type": "string"},
          "uncovered": {"type": "boolean"},
          "question_ids": {"type": "array", "items": {"type": "string"}},
          "heading": {"type": ["string", "null"]}
        }
      }
    },
    "questions": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["id", "question", "found_in", "score", "topic", "block", "fact_source",
                     "must_answer", "faq", "blocked", "covered_by"],
        "properties": {
          "id": {"type": "string", "pattern": "^q-[a-z0-9-]+$"},
          "question": {"type": "string", "minLength": 1},
          "found_in": {"type": "array", "items": {"type": "string"}, "minItems": 1},
          "score": {"type": "integer", "minimum": 0},
          "topic": {"type": ["string", "null"]},
          "block": {"enum": ["top", "middle", "bottom", null]},
          "fact_source": {"type": ["string", "null"]},
          "must_answer": {"type": "boolean"},
          "faq": {"enum": ["top", "middle", "bottom", null]},
          "blocked": {"type": ["string", "null"]},
          "covered_by": {
            "oneOf": [
              {"type": "null"},
              {"type": "object", "additionalProperties": false, "required": ["where", "text"],
               "properties": {"where": {"enum": ["faq", "heading"]}, "text": {"type": "string", "minLength": 1}}}
            ]
          }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Write the failing tests for the helpers**

Create `tests/py/test_query_augment.py`:

```python
# tests/py/test_query_augment.py — scripts/query_augment.py (spec 2026-09-23 §4, §6, §8).
# Every test builds its own repo root under tmp_path; nothing here calls a paid service.
import json
import pathlib
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import query_augment as Q  # noqa: E402

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "query_augment.py"

SETTINGS = {"delivery_min_gbp": 200, "guarantee_days": None,
            "query_budget_usd": 0.5, "query_total_budget_usd": 1.0,
            "query_typical_call_usd": 0.05}

TOP = ["How much does a puppy cost?", "How much is the deposit?",
       "Do you deliver across the UK?", "Can I collect my puppy?",
       "How do I reserve a puppy?", "Is there a waiting list?", "What payment do you take?"]
MIDDLE = ["What paperwork comes with the puppy?", "Is the puppy microchipped?",
          "Are the parents health tested?", "Can I visit before buying?",
          "How many weeks old is the puppy when it leaves?", "Can I meet the mother?"]
BOTTOM = ["Is a Staffy good in a flat?", "Are Staffies good with children?",
          "Are Staffies easy to train?", "What is the Staffy lifespan?", "Do Staffies shed?",
          "Are Staffies good with cats?", "Is a Staffy an aggressive dog?",
          "Do Staffies need a garden?"]


def make_root(tmp_path, bank=None, settings=None):
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data/settings.json").write_text(json.dumps(settings or SETTINGS))
    rows = bank if bank is not None else TOP + MIDDLE + BOTTOM
    faq = [{"id": f"b{i}", "q": q, "a": "…", "source": "data/settings.json"}
           for i, q in enumerate(rows)]
    (tmp_path / "data/faq.json").write_text(json.dumps(faq))
    return tmp_path


def write_raw(root, slug, name, payload):
    d = root / "data/queries/raw" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps(payload))


# --- normalise / topic / fact -------------------------------------------------------

def test_normalise_merges_staffy_spellings_and_punctuation():
    assert Q.normalise("How much are Staffie pups?") == Q.normalise("how much are staffy puppies")
    # the apostrophe goes before the synonyms run, so "terrier's" is "terriers" -> "staffy"
    assert Q.normalise("Staffordshire Bull Terrier's coat") == "staffy coat"


@pytest.mark.parametrize("text,topic,block", [
    ("How much does a blue Staffy cost?", "price", "top"),
    ("Do you deliver to Manchester?", "delivery", "top"),
    ("Is the puppy microchipped?", "paperwork", "middle"),
    ("Are the parents health tested?", "health", "middle"),
    ("Is a Staffy good in a flat?", "home", "bottom"),
    ("What is the Staffy lifespan?", "lifespan", "bottom"),
])
def test_topic_of_assigns_topic_and_block(text, topic, block):
    assert Q.topic_of(text) == (topic, block)


def test_topic_of_unknown_is_none():
    assert Q.topic_of("What is your favourite film?") == (None, None)


def test_fact_exists_resolves_file_and_json_key(tmp_path):
    root = make_root(tmp_path)
    assert Q.fact_exists("data/settings.json", root)
    assert Q.fact_exists("data/settings.json#delivery_min_gbp", root)
    assert not Q.fact_exists("data/settings.json#guarantee_days", root)   # null is not a fact
    assert not Q.fact_exists("data/settings.json#nope", root)
    assert not Q.fact_exists("data/missing.json", root)
    assert not Q.fact_exists("../etc/passwd", root)
    assert not Q.fact_exists("/etc/passwd", root)
    assert not Q.fact_exists(None, root)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m pytest tests/py/test_query_augment.py -q`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'query_augment'`.

- [ ] **Step 4: Write the helpers**

Create `scripts/query_augment.py`:

```python
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
    (r"\bpuppies\b", "puppy"),
    (r"\bpups?\b", "puppy"),
)

# First match wins, so order is precedence: a price question that mentions a blue coat is
# a price question. Patterns run on normalise()d text.
TOPICS = (
    ("price", "top", r"\b(costs?|prices?|how much|deposit|pay|payment|paying)\b"),
    ("delivery", "top", r"\b(deliver\w*|collect\w*|transport\w*|travel\w*|near me|distance)\b"),
    ("reserve", "top", r"\b(reserv\w*|waiting list|book\w*|available|availability)\b"),
    ("paperwork", "middle", r"\b(paperwork|papers|microchip\w*|vaccin\w*|pedigree|regist\w*|kennel club|contract)\b"),
    ("health", "middle", r"\b(health\w*|test\w*|vets?|l2hga|l 2 hga|hereditary|cataract\w*|guarantee\w*)\b"),
    ("visit", "middle", r"\b(visit\w*|meet|mother|father|parents)\b"),
    ("age", "middle", r"\b(weeks old|how old|leave\w* (its|their|the) mother)\b"),
    ("home", "bottom", r"\b(flat|flats|apartment\w*|garden\w*|house|left alone|home alone)\b"),
    ("family", "bottom", r"\b(child\w*|kids?|family|families|cats?|other dogs|other pets)\b"),
    ("training", "bottom", r"\b(train\w*|potty|crate\w*)\b"),
    ("lifespan", "bottom", r"\b(lifespan|life expectancy|how long do)\b"),
    ("coat", "bottom", r"\b(coat\w*|colou?rs?|shed\w*|groom\w*)\b"),
    ("temperament", "bottom", r"\b(temperament|aggressive|dangerous|banned|friendly|energy|exercise)\b"),
)

# Page-type fit: how much a topic matters on this kind of page. Unlisted topics weigh 1.
FIT = {
    "location": {"delivery": 3, "price": 2, "reserve": 2, "visit": 2},
    "comparison": {"temperament": 2, "coat": 2, "health": 2},
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
    except (ValueError, UnicodeDecodeError):
        return False
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return False
    return node is not None
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python3 -m pytest tests/py/test_query_augment.py -q`
Expected: all pass.

- [ ] **Step 6: Regenerate the registry and commit**

```bash
python3 scripts/build_system_registry.py
python3 scripts/build_system_registry.py --check
git add schemas/queries.schema.json scripts/query_augment.py tests/py/test_query_augment.py docs/reference/system-registry.md
git commit -m "queries: the question-file schema and the normalise, topic and fact helpers

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Merge, score, section target, FAQ and extra picks

**Files:**
- Modify: `scripts/query_augment.py` (append below `fact_exists`)
- Modify: `tests/py/test_query_augment.py` (append)

- [ ] **Step 1: Append the failing tests**

Append to `tests/py/test_query_augment.py`:

```python
# --- merge / score ------------------------------------------------------------------

def test_merge_keeps_every_source_and_the_first_phrasing(tmp_path):
    root = make_root(tmp_path)
    cands = [("How much are Staffie pups?", "serp_google", "serp_google_paa", None),
             ("how much are staffy puppies", "threads", "thread:r/x/1", None),
             ("How much are staffy puppies?", "bank", "bank:b0", "data/settings.json")]
    m = Q.merge(cands, root)
    assert len(m) == 1
    (only,) = m.values()
    assert only["question"] == "How much are Staffie pups?"
    assert only["types"] == {"serp_google", "threads", "bank"}
    assert only["found_in"] == ["serp_google_paa", "thread:r/x/1", "bank:b0"]
    assert only["fact_source"] == "data/settings.json"


def test_merge_ignores_a_fact_source_that_does_not_resolve(tmp_path):
    root = make_root(tmp_path)
    m = Q.merge([("Is there a guarantee?", "serp_google", "serp_google_paa",
                  "data/settings.json#guarantee_days")], root)
    assert next(iter(m.values()))["fact_source"] is None


def test_score_is_distinct_source_types_plus_page_fit():
    assert Q.score({"serp_google", "bank"}, "delivery", "location") == 2 + 3
    assert Q.score({"bank"}, "coat", "location") == 1 + 1
    assert Q.score({"bank"}, None, "blog") == 1 + 1


# --- competitors ----------------------------------------------------------------------

def test_clean_h2s_strips_non_content_and_duplicates():
    h2 = ["Our Puppies", "Related Posts", "Frequently Asked Questions About Staffies",
          "Reviews", "Contact Us", "Our Puppies", "Health Testing", ""]
    assert Q.clean_h2s(h2) == ["Our Puppies", "Health Testing"]


def page(url, n, g=None, b=None):
    return {"url": url, "google_pos": g, "bing_pos": b, "h2": [f"Section {i}" for i in range(n)]}


def test_section_target_matches_the_highest_clean_count():
    target, rows = Q.section_target([page("a", 8, g=1), page("b", 11, b=2), page("c", 14, g=3)])
    assert target == {"matched": 14, "set_by": "c", "extra": 3, "total": 17}
    assert [r["h2_clean"] for r in rows] == [8, 11, 14]
    assert not any(r["outlier"] for r in rows)


def test_section_target_outlier_matches_the_next_highest():
    target, rows = Q.section_target([page("a", 10, g=1), page("b", 30, g=2)])
    assert target["matched"] == 10 and target["set_by"] == "a" and target["total"] == 13
    assert [r["outlier"] for r in rows] == [False, True]


def test_section_target_with_no_pages_is_zero_plus_three():
    target, rows = Q.section_target([])
    assert target == {"matched": 0, "set_by": None, "extra": 3, "total": 3} and rows == []


def test_covered_topics_reads_competitor_headings():
    pages = [{"url": "a", "h2": ["Delivery Across the North West", "Our Prices"]}]
    assert Q.covered_topics(pages) == {"delivery", "price"}


# --- picks --------------------------------------------------------------------------

def q(qid, text, sc, fact="data/settings.json"):
    topic, block = Q.topic_of(text)
    return {"id": qid, "question": text, "score": sc, "topic": topic, "block": block,
            "fact_source": fact, "faq": None}


def bank_questions():
    out = []
    for i, t in enumerate(TOP + MIDDLE + BOTTOM):
        out.append(q(f"q-{i:02d}", t, 10 - (i % 5)))
    return out


def test_pick_faq_fills_minimums_then_by_score_to_twenty():
    qs = bank_questions()
    Q.pick_faq(qs)
    counts = {b: sum(1 for x in qs if x["faq"] == b) for b in Q.BLOCKS}
    assert sum(counts.values()) == 20
    for b in Q.BLOCKS:
        assert Q.FAQ_MIN[b] <= counts[b] <= Q.FAQ_MAX[b]


def test_pick_faq_never_picks_an_unbacked_question():
    qs = bank_questions() + [q("q-zz", "How much is a puppy in Leeds?", 99, fact=None)]
    Q.pick_faq(qs)
    assert next(x for x in qs if x["id"] == "q-zz")["faq"] is None


def test_pick_faq_raises_short_naming_the_block():
    qs = [x for x in bank_questions() if x["block"] != "middle"][:] + \
         [q("q-m1", MIDDLE[0], 5), q("q-m2", MIDDLE[1], 5)]
    with pytest.raises(Q.Short) as e:
        Q.pick_faq(qs)
    assert e.value.blocks == {"middle": (2, 5)}


def test_pick_extra_prefers_topics_no_competitor_covers():
    qs = bank_questions()
    Q.pick_faq(qs)
    extras = Q.pick_extra(qs, covered={"price", "delivery", "reserve", "home", "family"})
    assert len(extras) == 3
    assert all(e["uncovered"] for e in extras)
    assert not {e["topic"] for e in extras} & {"price", "delivery", "reserve", "home", "family"}
    assert all(e["heading"] is None for e in extras)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/py/test_query_augment.py -q`
Expected: FAIL with `AttributeError: module 'query_augment' has no attribute 'merge'` (and similar for the others).

- [ ] **Step 3: Implement**

Append to `scripts/query_augment.py`:

```python
class Short(Exception):
    """A FAQ block cannot reach its minimum from fact-backed questions."""

    def __init__(self, blocks):
        super().__init__(", ".join(f"{b}: {have}/{need}" for b, (have, need) in blocks.items()))
        self.blocks = blocks


def merge(cands, root=ROOT):
    """cands: (text, source_type, detail, fact_source). Keyed by normalised text."""
    merged = {}
    for text, src, detail, fact in cands:
        n = normalise(text)
        if not n:
            continue
        m = merged.setdefault(n, {"question": text.strip(), "types": set(),
                                  "found_in": [], "fact_source": None})
        m["types"].add(src)
        if detail not in m["found_in"]:
            m["found_in"].append(detail)
        if m["fact_source"] is None and fact_exists(fact, root):
            m["fact_source"] = fact
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


def clean_h2s(h2s):
    seen, out = set(), []
    for h in h2s:
        n = normalise(h)
        if not n or n in seen or NON_CONTENT_EXACT.fullmatch(n) or NON_CONTENT_PREFIX.match(n):
            continue
        seen.add(n)
        out.append(h)
    return out


def section_target(pages):
    """(target, rows): match the highest cleaned H2 count unless it is an outlier."""
    rows = [{"url": p["url"], "google_pos": p.get("google_pos"), "bing_pos": p.get("bing_pos"),
             "h2_raw": len(p.get("h2", [])), "h2_clean": len(clean_h2s(p.get("h2", []))),
             "outlier": False} for p in pages]
    if not rows:
        return {"matched": 0, "set_by": None, "extra": EXTRA_SECTIONS, "total": EXTRA_SECTIONS}, rows
    ranked = sorted(rows, key=lambda r: -r["h2_clean"])
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
    """The strongest fact-backed topics, uncovered ones first. heading is filled by the builder."""
    weight = {}
    for q in questions:
        if q["fact_source"] and q["topic"]:
            weight[q["topic"]] = weight.get(q["topic"], 0) + q["score"]
    order = sorted(weight, key=lambda t: (t in covered, -weight[t], t))
    extras = []
    for t in order[:EXTRA_SECTIONS]:
        ids = [q["id"] for q in sorted(questions, key=_rank)
               if q["topic"] == t and q["fact_source"] and not q["faq"]][:3]
        extras.append({"topic": t, "uncovered": t not in covered, "question_ids": ids,
                       "heading": None})
    return extras
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/py/test_query_augment.py -q`
Expected: all pass.

In `test_pick_extra_prefers_topics_no_competitor_covers`, the uncovered fact-backed topics in the fixture bank are paperwork, health, visit, age, training, lifespan, coat and temperament, so three uncovered topics always exist.

- [ ] **Step 5: Commit**

```bash
git add scripts/query_augment.py tests/py/test_query_augment.py
git commit -m "queries: merge, score, the competitor section target and the FAQ and extra picks

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Spend log, preflight and settings

**Files:**
- Modify: `scripts/query_augment.py` (append)
- Modify: `tests/py/test_query_augment.py` (append)
- Modify: `data/settings.json`

- [ ] **Step 1: Append the failing tests**

```python
# --- spend / preflight --------------------------------------------------------------

NOW = "2026-09-23T10:00:00Z"


def test_record_appends_to_the_spend_log(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "serp_google", "serp_organic_live_advanced", 0.002, root, now=NOW)
    Q.record("m", "ai_engines", "llm_response", 0.01, root, now=NOW)
    log = json.loads((root / "data/queries/spend.json").read_text())
    assert [e["cost_usd"] for e in log] == [0.002, 0.01]
    assert log[0] == {"ts": NOW, "slug": "m", "source": "serp_google",
                      "endpoint": "serp_organic_live_advanced", "cost_usd": 0.002}


def test_preflight_cached_makes_no_call(tmp_path):
    root = make_root(tmp_path)
    write_raw(root, "m", "serp_google", {"source": "serp_google", "status": "ok", "questions": []})
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_CACHED
    assert Q.preflight("m", "serp_google", root, refresh=True, today="2026-09-23") == Q.EXIT_OK


def test_preflight_refuses_over_the_page_budget(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "ai_engines", "llm_response", 0.46, root, now=NOW)
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET
    # another day is another run
    assert Q.preflight("m", "serp_google", root, today="2026-09-24") == Q.EXIT_OK


def test_preflight_refuses_over_the_total_budget(tmp_path):
    root = make_root(tmp_path)
    for slug in ("a", "b", "c"):
        Q.record(slug, "ai_engines", "llm_response", 0.32, root, now=NOW)
    assert Q.preflight("d", "serp_google", root, today="2026-09-30") == Q.EXIT_BUDGET


def test_preflight_uses_the_largest_observed_cost_for_that_source(tmp_path):
    root = make_root(tmp_path)
    Q.record("x", "ai_engines", "llm_response", 0.30, root, now=NOW)
    # page m has spent nothing, but one ai_engines call has been seen to cost 0.30
    Q.record("m", "serp_google", "serp", 0.25, root, now=NOW)
    assert Q.preflight("m", "ai_engines", root, today="2026-09-23") == Q.EXIT_BUDGET


def test_preflight_free_source_is_never_budget_limited(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "ai_engines", "llm_response", 0.9, root, now=NOW)
    assert Q.preflight("m", "threads", root, today="2026-09-23") == Q.EXIT_OK


def test_preflight_without_a_budget_setting_fails_closed(tmp_path):
    root = make_root(tmp_path, settings={"delivery_min_gbp": 200})
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/py/test_query_augment.py -q -k "record or preflight"`
Expected: FAIL with `AttributeError: module 'query_augment' has no attribute 'record'`.

- [ ] **Step 3: Implement**

Append to `scripts/query_augment.py`:

```python
def _read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_settings(root=ROOT):
    return _read_json(Path(root) / "data/settings.json", {})


def load_spend(root=ROOT):
    return _read_json(Path(root) / "data/queries/spend.json", [])


def record(slug, source, endpoint, cost, root=ROOT, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log = load_spend(root)
    log.append({"ts": now, "slug": slug, "source": source, "endpoint": endpoint,
                "cost_usd": float(cost)})
    _write_json(Path(root) / "data/queries/spend.json", log)


def spend_for(slug, root=ROOT, day=None):
    return round(sum(e["cost_usd"] for e in load_spend(root)
                     if e["slug"] == slug and (day is None or e["ts"].startswith(day))), 6)


def preflight(slug, source, root=ROOT, refresh=False, today=None):
    """0 proceed · 3 cached · 4 a budget would be exceeded. Fails closed without a budget."""
    today = today or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    if (Path(root) / "data/queries/raw" / slug / f"{source}.json").is_file() and not refresh:
        return EXIT_CACHED
    if source not in PAID_SOURCES:
        return EXIT_OK
    s = load_settings(root)
    page_cap, total_cap = s.get("query_budget_usd"), s.get("query_total_budget_usd")
    if page_cap is None or total_cap is None:
        return EXIT_BUDGET
    log = load_spend(root)
    seen = [e["cost_usd"] for e in log if e["source"] == source]
    typical = max(seen) if seen else s.get("query_typical_call_usd", DEFAULT_TYPICAL_CALL_USD)
    total = sum(e["cost_usd"] for e in log)
    if spend_for(slug, root, day=today) + typical > page_cap or total + typical > total_cap:
        return EXIT_BUDGET
    return EXIT_OK
```

- [ ] **Step 4: Add the settings keys**

In `data/settings.json`, insert these three keys after `"delivery_note"`:

```json
  "query_budget_usd": 0.5,
  "query_total_budget_usd": 1.0,
  "query_typical_call_usd": 0.05,
```

- [ ] **Step 5: Run the tests**

Run: `python3 -m pytest tests/py/test_query_augment.py tests/py/test_data_files.py -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/query_augment.py tests/py/test_query_augment.py data/settings.json
git commit -m "queries: the spend log, preflight and the per-page and total budgets

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: build() and the CLI

**Files:**
- Modify: `scripts/query_augment.py` (append)
- Modify: `tests/py/test_query_augment.py` (append)

- [ ] **Step 1: Append the failing tests**

```python
# --- build / CLI --------------------------------------------------------------------

import jsonschema  # noqa: E402

SCHEMA = json.loads((pathlib.Path(__file__).resolve().parents[2]
                     / "schemas/queries.schema.json").read_text())
ROUTE = "/uk-locations/blue-staffy-puppies-manchester-uk/"


def run(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args],
                          capture_output=True, text=True)


def seed(root, slug="m"):
    write_raw(root, slug, "serp_google", {"source": "serp_google", "status": "ok", "questions": [
        {"text": "Do you deliver Staffy puppies to Manchester?", "detail": "serp_google_paa",
         "fact_source": "data/settings.json#delivery_min_gbp"},
        {"text": "Is there a Staffy puppy guarantee?", "detail": "serp_google_paa",
         "fact_source": "data/settings.json#guarantee_days"}]})
    write_raw(root, slug, "competitors", {"status": "ok", "pages": [
        {"url": "https://a.example", "google_pos": 1, "bing_pos": None,
         "h2": ["Our Prices", "Delivery to Manchester", "Reviews"]}]})


def test_build_writes_a_schema_valid_file(tmp_path):
    root = make_root(tmp_path); seed(root)
    r = run(root, "m", "--page-type", "location", "--keyword", "blue staffy puppies manchester",
            "--route", ROUTE, "--today", "2026-09-23")
    assert r.returncode == 0, r.stderr
    data = json.loads((root / "data/queries/m.json").read_text())
    jsonschema.validate(data, SCHEMA)
    assert data["sources"]["serp_google"] == "ok"
    assert data["sources"]["serp_bing"] == "NOT FETCHED"
    assert data["sources"]["bank"] == "ok"
    assert data["section_target"] == {"matched": 2, "set_by": "https://a.example",
                                      "extra": 3, "total": 5}
    faq = [x for x in data["questions"] if x["faq"]]
    assert 17 <= len(faq) <= 20
    assert all(x["must_answer"] for x in faq)


def test_build_never_makes_an_unbacked_question_must_answer(tmp_path):
    root = make_root(tmp_path); seed(root)
    run(root, "m", "--page-type", "location", "--keyword", "k", "--route", ROUTE,
        "--today", "2026-09-23")
    data = json.loads((root / "data/queries/m.json").read_text())
    g = next(x for x in data["questions"] if "guarantee" in x["question"].lower())
    assert g["must_answer"] is False and g["blocked"] == "unverified fact"


def test_build_carries_over_covered_by_and_headings(tmp_path):
    root = make_root(tmp_path); seed(root)
    args = ("m", "--page-type", "location", "--keyword", "k", "--route", ROUTE,
            "--today", "2026-09-23")
    run(root, *args)
    f = root / "data/queries/m.json"
    data = json.loads(f.read_text())
    first = next(x for x in data["questions"] if x["faq"])
    first["covered_by"] = {"where": "faq", "text": first["question"]}
    data["extra_sections"][0]["heading"] = "A Heading We Wrote"
    f.write_text(json.dumps(data))
    run(root, *args)
    again = json.loads(f.read_text())
    assert next(x for x in again["questions"] if x["id"] == first["id"])["covered_by"] == \
        first["covered_by"]
    assert again["extra_sections"][0]["heading"] == "A Heading We Wrote"


def test_build_short_exits_5_and_lists_what_is_blocked(tmp_path):
    root = make_root(tmp_path, bank=TOP + BOTTOM)          # no middle questions at all
    seed(root)
    r = run(root, "m", "--page-type", "location", "--keyword", "k", "--route", ROUTE,
            "--today", "2026-09-23")
    assert r.returncode == Q.EXIT_SHORT
    assert "middle: 0/5" in r.stdout
    assert not (root / "data/queries/m.json").exists()


def test_cli_preflight_and_record(tmp_path):
    root = make_root(tmp_path)
    assert run(root, "--preflight", "m", "--source", "serp_google",
               "--today", "2026-09-23").returncode == 0
    assert run(root, "--record", "m", "--source", "serp_google", "--endpoint", "serp",
               "--cost", "0.002").returncode == 0
    assert json.loads((root / "data/queries/spend.json").read_text())[0]["cost_usd"] == 0.002


def test_cli_rejects_an_unknown_page_type(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "m", "--page-type", "hub", "--keyword", "k", "--route", ROUTE)
    assert r.returncode == 2
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/py/test_query_augment.py -q -k "build or cli"`
Expected: FAIL. The subprocess exits non-zero because `--root` is unknown and there is no `main`.

- [ ] **Step 3: Implement**

Append to `scripts/query_augment.py`:

```python
def load_candidates(slug, root=ROOT):
    raw = Path(root) / "data/queries/raw" / slug
    cands, status = [], {}
    for src in CANDIDATE_SOURCES:
        d = _read_json(raw / f"{src}.json", None)
        if d is None:
            status[src] = "NOT FETCHED"
            continue
        status[src] = d.get("status", "ok")
        for item in d.get("questions", []):
            cands.append((item["text"], src, item.get("detail") or src, item.get("fact_source")))
    return cands, status


def bank_candidates(root=ROOT):
    rows = _read_json(Path(root) / "data/faq.json", [])
    return [(r["q"], "bank", f"bank:{r['id']}", r.get("source")) for r in rows]


def _question_id(norm, taken):
    base = ("q-" + "-".join(norm.split()[:8]))[:50].rstrip("-")
    qid, i = base, 2
    while qid in taken:
        qid, i = f"{base}-{i}", i + 1
    return qid


def build(slug, page_type, keyword, route, root=ROOT, today=None):
    """The question file as a dict. Raises Short when a FAQ block cannot be filled."""
    today = today or datetime.date.today().isoformat()
    cands, status = load_candidates(slug, root)
    cands += bank_candidates(root)   # buyer phrasing first, so it wins the merge
    status["bank"] = "ok"
    merged = merge(cands, root)
    questions, taken = [], set()
    for n in sorted(merged):
        m = merged[n]
        topic, block = topic_of(m["question"])
        qid = _question_id(n, taken)
        taken.add(qid)
        questions.append({
            "id": qid, "question": m["question"], "found_in": m["found_in"],
            "score": score(m["types"], topic, page_type), "topic": topic, "block": block,
            "fact_source": m["fact_source"], "must_answer": False, "faq": None,
            "blocked": None if m["fact_source"] else "unverified fact", "covered_by": None})
    comp = _read_json(Path(root) / "data/queries/raw" / slug / "competitors.json",
                      {"status": "NOT FETCHED", "pages": []})
    status["competitors"] = comp.get("status", "ok")
    target, rows = section_target(comp["pages"])
    pick_faq(questions)
    extras = pick_extra(questions, covered_topics(comp["pages"]))
    extra_ids = {i for e in extras for i in e["question_ids"]}
    for q in questions:
        q["must_answer"] = bool(q["faq"]) or q["id"] in extra_ids
    prev = _read_json(Path(root) / "data/queries" / f"{slug}.json", None)
    if prev:
        covered = {q["id"]: q.get("covered_by") for q in prev.get("questions", [])}
        heads = {e["topic"]: e.get("heading") for e in prev.get("extra_sections", [])}
        for q in questions:
            q["covered_by"] = covered.get(q["id"])
        for e in extras:
            e["heading"] = heads.get(e["topic"])
    return {"slug": slug, "page_type": page_type, "primary_keyword": keyword, "route": route,
            "fetched": today, "spend_usd": spend_for(slug, root), "sources": status,
            "competitors": rows, "section_target": target, "extra_sections": extras,
            "questions": questions}


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
    if a.preflight:
        if a.source not in CANDIDATE_SOURCES:
            ap.error("--source must be one of " + ", ".join(CANDIDATE_SOURCES))
        code = preflight(a.preflight, a.source, root, a.refresh, a.today)
        print({EXIT_OK: "proceed", EXIT_CACHED: "cached — make no call",
               EXIT_BUDGET: "budget would be exceeded — stop and report"}[code])
        return code
    if a.record:
        if a.source not in PAID_SOURCES or not a.endpoint or a.cost is None:
            ap.error("--record needs a paid --source, --endpoint and --cost")
        record(a.record, a.source, a.endpoint, a.cost, root)
        print(f"recorded {a.cost} for {a.record}; page total {spend_for(a.record, root)}")
        return EXIT_OK
    if not a.slug or a.page_type not in PAGE_TYPES or not a.keyword or not a.route:
        ap.error("build needs SLUG, --page-type (" + "/".join(PAGE_TYPES) + "), --keyword, --route")
    try:
        data = build(a.slug, a.page_type, a.keyword, a.route, root, a.today)
    except Short as e:
        print(f"SHORT: too few fact-backed questions — {e}")
        cands, _ = load_candidates(a.slug, root)
        for n, m in sorted(merge(cands + bank_candidates(root), root).items()):
            _, block = topic_of(m["question"])
            if block in e.blocks and not m["fact_source"]:
                print(f"  blocked ({block}): {m['question']}")
        return EXIT_SHORT
    _write_json(root / "data/queries" / f"{a.slug}.json", data)
    faq = sum(1 for q in data["questions"] if q["faq"])
    print(f"wrote data/queries/{a.slug}.json — {len(data['questions'])} questions, {faq} FAQ, "
          f"section target {data['section_target']['total']}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the whole file**

Run: `python3 -m pytest tests/py/test_query_augment.py -q`
Expected: all pass. `argparse`'s `ap.error` exits 2, which is what `test_cli_rejects_an_unknown_page_type` checks.

In `test_build_writes_a_schema_valid_file`, the competitor's cleaned headings are "Our Prices" and "Delivery to Manchester" ("Reviews" is removed), so `matched` is 2.

- [ ] **Step 5: Commit**

```bash
git add scripts/query_augment.py tests/py/test_query_augment.py
git commit -m "queries: build the question file, carry the builder's fills across re-runs, stop when short

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: The coverage gate

**Files:**
- Create: `scripts/query_coverage_check.py`
- Create: `tests/py/test_query_coverage_check.py`
- Modify: `package.json` (`check:queries`, `check:all`)
- Modify: `tests/py/test_package_scripts.py:104-106` (expected list)

Built markup the gate relies on:
- `src/components/kit/Faq.astro` renders `<div class="kit-faq">` → `<details>` → `<summary><span class="num">01</span><h3 class="q">Title Cased Question</h3></summary><p>answer</p>`. The H3 is title-cased at render, so the gate compares `normalise()`d text.
- Body sections are `<section id="…" data-section-label="…">`. A section that holds a frame part — a kit hero (`kit-hero`), counter (`kit-counter`), trust strip (`kit-trust`), page nav (`kit-nav`), review (`kit-quote`), FAQ block (`kit-faq`) or any `<form>` — is frame, never body (Task 1's template, "The fixed frame").

- [ ] **Step 1: Write the failing tests**

Create `tests/py/test_query_coverage_check.py`:

```python
# tests/py/test_query_coverage_check.py — scripts/query_coverage_check.py (spec 2026-09-23 §10).
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import query_coverage_check as G  # noqa: E402

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "query_coverage_check.py"
ROUTE = "/uk-locations/blue-staffy-puppies-manchester-uk/"


def faq_block(questions, answers=True, h3=True):
    items = []
    for i, text in enumerate(questions):
        head = f'<h3 class="q">{text.title()}</h3>' if h3 else f"<b>{text}</b>"
        items.append(f'<details><summary><span class="num">{i + 1:02d}</span>{head}</summary>'
                     f'<p>{"An answer." if answers else ""}</p></details>')
    return f'<section id="faq-x" data-section-label="Questions"><h2>Questions</h2>' \
           f'<div class="kit-faq">{"".join(items)}</div></section>'


def qset(n, prefix):
    return [f"{prefix} question number {i}?" for i in range(n)]


def page_html(blocks=(5, 5, 7), body=5, extra=("Life in a Manchester Flat",), schema=True,
              answers=True, h3=True, form=True):
    top, mid, bot = qset(blocks[0], "top"), qset(blocks[1], "middle"), qset(blocks[2], "bottom")
    sections = [f'<section id="s{i}" data-section-label="S{i}"><h2>Body {i}</h2><p>Text.</p></section>'
                for i in range(body)]
    sections += [f'<section id="x{i}" data-section-label="X"><h2>{h}</h2><p>Text.</p></section>'
                 for i, h in enumerate(extra)]
    faq_names = top + mid + bot
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": n, "acceptedAnswer": {"@type": "Answer", "text": "An answer."}}
        for n in (faq_names if schema else faq_names[:-1])]})
    formsec = '<section id="enquiry" data-section-label="Ask"><h2>Ask</h2><form></form></section>' \
        if form else ""
    return ("<html><head><script type=\"application/ld+json\">" + ld + "</script></head><body><main>"
            '<section id="top" data-section-label="Hero"><h1>Blue Staffy Puppies Manchester</h1></section>'
            + faq_block(top, answers, h3) + "".join(sections[:3]) + faq_block(mid, answers, h3)
            + "".join(sections[3:]) + formsec + faq_block(bot, answers, h3)
            + "</main></body></html>")


def qfile(blocks=(5, 5, 7), total=6, extra_heading="Life in a Manchester Flat"):
    qs = []
    for name, n in zip(("top", "middle", "bottom"), blocks):
        for i in range(n):
            text = f"{name} question number {i}?"
            qs.append({"id": f"q-{name}-{i}", "question": text, "found_in": ["bank:x"], "score": 1,
                       "topic": "price", "block": name, "fact_source": "data/settings.json",
                       "must_answer": True, "faq": name, "blocked": None,
                       "covered_by": {"where": "faq", "text": text}})
    return {"slug": "m", "page_type": "location", "primary_keyword": "k", "route": ROUTE,
            "fetched": "2026-09-23", "spend_usd": 0.0, "sources": {}, "competitors": [],
            "section_target": {"matched": total - 3, "set_by": None, "extra": 3, "total": total},
            "extra_sections": [{"topic": "home", "uncovered": True, "question_ids": [],
                                "heading": extra_heading}],
            "questions": qs}


def test_a_complete_page_passes():
    assert G.check_page(qfile(), page_html()) == []


def test_two_faq_blocks_fail():
    html = page_html().replace('<div class="kit-faq">', '<div class="kit-other">', 1)
    assert any("FAQ blocks: 2" in p for p in G.check_page(qfile(), html))


def test_a_block_outside_its_range_fails():
    probs = G.check_page(qfile(blocks=(4, 5, 7)), page_html(blocks=(4, 5, 7)))
    assert any("FAQ top: 4 questions, want 5–7" in p for p in probs)


def test_a_question_that_is_not_an_h3_fails():
    probs = G.check_page(qfile(), page_html(h3=False))
    assert any("must be an H3" in p for p in probs)


def test_an_empty_answer_fails_even_though_the_next_number_follows():
    probs = G.check_page(qfile(), page_html(answers=False))
    assert any("has no answer under it" in p for p in probs)


def test_an_uncovered_must_answer_question_fails():
    q = qfile(); q["questions"][0]["covered_by"] = None
    assert any("has no covered_by" in p for p in G.check_page(q, page_html()))


def test_covered_text_missing_from_the_page_fails():
    q = qfile(); q["questions"][0]["covered_by"]["text"] = "A question nobody wrote?"
    assert any("not found" in p for p in G.check_page(q, page_html()))


def test_schema_that_differs_from_the_visible_faq_fails():
    assert any("FAQPage schema" in p for p in G.check_page(qfile(), page_html(schema=False)))


def test_an_extra_section_without_a_heading_fails():
    assert any("no heading recorded" in p
               for p in G.check_page(qfile(extra_heading=None), page_html()))


def test_an_extra_section_heading_missing_from_the_page_fails():
    q = qfile(extra_heading="A Section We Never Built")
    assert any("not an H2 on the page" in p for p in G.check_page(q, page_html()))


def test_too_few_body_sections_fails_and_frame_is_not_counted():
    # body 5 + 1 extra = 6 counted; hero (#top), the FAQ sections and the form are frame
    assert G.check_page(qfile(total=6), page_html()) == []
    probs = G.check_page(qfile(total=7), page_html())
    assert any("body sections: 6, want at least 7" in p for p in probs)


def test_review_and_counter_sections_are_frame_not_body():
    extra = ('<section id="rev" data-section-label="Reviews"><h2>Reviews</h2>'
             '<section class="kit-quote"><p>Lovely pup.</p></section></section>'
             '<section id="stats" data-section-label="At a glance" class="kit-counter"><h2>Stats</h2></section>')
    html = page_html().replace("</main>", extra + "</main>")
    assert G.check_page(qfile(total=6), html) == []
    assert any("body sections: 6, want at least 7" in p for p in G.check_page(qfile(total=7), html))


def test_main_skips_unbuilt_pages_and_reports(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps(qfile()))
    (tmp_path / "data/queries/spend.json").write_text("[]")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "examined 0 pages (1 not built); 0 problems" in r.stdout


def test_main_fails_a_built_page_with_problems(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps(qfile(total=9)))
    out = tmp_path / "dist" / ROUTE.strip("/")
    out.mkdir(parents=True)
    (out / "index.html").write_text(page_html())
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert "examined 1 pages (0 not built); 1 problems" in r.stdout


def test_main_rejects_an_invalid_question_file(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps({"slug": "m"}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "invalid question file" in r.stdout
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/py/test_query_coverage_check.py -q`
Expected: collection ERROR `No module named 'query_coverage_check'`.

- [ ] **Step 3: Implement the gate**

Create `scripts/query_coverage_check.py`:

```python
#!/usr/bin/env python3
"""Query coverage gate over dist/ (spec 2026-09-23 §10).

For every data/queries/<slug>.json whose route is built in dist/, the page must carry:
  1. three FAQ blocks (kit-faq, in document order top/middle/bottom) of 5–7, 5–7 and 7–10
     questions, 15–20 in total, every question an H3;
  2. every must-answer question at its covered_by text, with an answer under it;
  3. FAQPage schema naming exactly the visible FAQ questions;
  4. every extra section's recorded heading as an H2;
  5. on location pages, at least section_target.total body sections — a body section is a
     <section data-section-label> that is not #top or #key-takeaways and holds no frame part:
     no kit hero, counter, trust strip, page nav, review, FAQ block and no form
     (docs/reference/location-page-template.md, "The fixed frame" — frame is never counted).

A question file whose route is not built is skipped and counted: an unbuilt page ships
nothing. Exit 1 on any problem, 0 otherwise.

  python3 scripts/query_coverage_check.py
"""
import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
from query_augment import BLOCKS, FAQ_MAX, FAQ_MIN, FAQ_TOTAL_MAX, normalise  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FAQ_TOTAL_MIN = 15
FRAME_IDS = {"top", "key-takeaways"}
# The kit components that make up the fixed frame. A section holding one is frame, not body.
FRAME_CLASSES = {"kit-hero", "kit-counter", "kit-trust", "kit-nav", "kit-quote", "kit-faq"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [tag, section_index|None, faq_index|None]
        self.sections = []       # {"id", "frame"}
        self.faq_blocks = []     # {"h3": [text], "details": n}
        self.headings = []       # {"level", "text", "answer", "faq"}
        self.ld = []
        self._heading = None     # [level, [text], faq_index]
        self._ld = None

    def _open(self, kind):
        return [e[kind] for e in self.stack if e[kind] is not None]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in VOID:
            return
        sec = faq = None
        classes = set((a.get("class") or "").split())
        if tag == "section" and "data-section-label" in a:
            self.sections.append({"id": a.get("id") or "", "frame": False})
            sec = len(self.sections) - 1
        if tag == "form" or classes & FRAME_CLASSES:
            for i in self._open(1) + ([sec] if sec is not None else []):
                self.sections[i]["frame"] = True
        if tag == "div" and "kit-faq" in classes:
            self.faq_blocks.append({"h3": [], "details": 0})
            faq = len(self.faq_blocks) - 1
        if tag == "details" and self._open(2):
            self.faq_blocks[self._open(2)[-1]]["details"] += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            inside = self._open(2)
            self._heading = [int(tag[1]), [], inside[-1] if inside and tag == "h3" else None]
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = []
        self.stack.append([tag, sec, faq])

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading:
            level, parts, faq = self._heading
            text = " ".join("".join(parts).split())
            self.headings.append({"level": level, "text": text, "answer": "", "faq": faq})
            if faq is not None:
                self.faq_blocks[faq]["h3"].append(text)
            self._heading = None
        if tag == "script" and self._ld is not None:
            self.ld.append("".join(self._ld))
            self._ld = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._ld is not None:
            self._ld.append(data)
        elif self._heading is not None:
            self._heading[1].append(data)
        elif self.headings and not any(e[0] == "summary" for e in self.stack):
            self.headings[-1]["answer"] += data


def faq_schema_names(blobs):
    names = []

    def walk(node):
        if isinstance(node, list):
            for x in node:
                walk(x)
        elif isinstance(node, dict):
            t = node.get("@type")
            if t == "FAQPage" or (isinstance(t, list) and "FAQPage" in t):
                for q in node.get("mainEntity", []):
                    if isinstance(q, dict) and q.get("name"):
                        names.append(q["name"])
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)

    for b in blobs:
        try:
            walk(json.loads(b))
        except ValueError:
            continue
    return names


def check_page(q, html):
    p = Page()
    p.feed(html)
    p.close()
    problems = []
    blocks = p.faq_blocks
    if len(blocks) != 3:
        problems.append(f"FAQ blocks: {len(blocks)}, want 3 (top, middle, bottom)")
    else:
        for name, b in zip(BLOCKS, blocks):
            n = len(b["h3"])
            if b["details"] != n:
                problems.append(f"FAQ {name}: {b['details']} questions but {n} H3s — "
                                "every question must be an H3")
            if not FAQ_MIN[name] <= n <= FAQ_MAX[name]:
                problems.append(f"FAQ {name}: {n} questions, want {FAQ_MIN[name]}–{FAQ_MAX[name]}")
    total = sum(len(b["h3"]) for b in blocks)
    if not FAQ_TOTAL_MIN <= total <= FAQ_TOTAL_MAX:
        problems.append(f"FAQ total: {total}, want {FAQ_TOTAL_MIN}–{FAQ_TOTAL_MAX}")
    faq_h3 = {normalise(t) for b in blocks for t in b["h3"]}
    heads = {}
    for h in p.headings:
        heads.setdefault(normalise(h["text"]), h)
    for item in q["questions"]:
        if not item["must_answer"]:
            continue
        cov = item.get("covered_by")
        if not cov:
            problems.append(f"{item['id']}: must-answer question has no covered_by")
            continue
        key = normalise(cov["text"])
        h = heads.get(key) if (cov["where"] == "heading" or key in faq_h3) else None
        if h is None:
            where = "an FAQ H3" if cov["where"] == "faq" else "a heading"
            problems.append(f"{item['id']}: '{cov['text']}' not found as {where}")
        elif not h["answer"].strip():
            problems.append(f"{item['id']}: '{cov['text']}' has no answer under it")
    schema = {normalise(n) for n in faq_schema_names(p.ld)}
    if schema != faq_h3:
        problems.append(f"FAQPage schema: {len(faq_h3 - schema)} visible questions missing, "
                        f"{len(schema - faq_h3)} not visible")
    h2s = {normalise(h["text"]) for h in p.headings if h["level"] == 2}
    for e in q.get("extra_sections", []):
        if not e.get("heading"):
            problems.append(f"extra section '{e['topic']}': no heading recorded")
        elif normalise(e["heading"]) not in h2s:
            problems.append(f"extra section '{e['topic']}': '{e['heading']}' is not an H2 on the page")
    if q["page_type"] == "location":
        body = [s for s in p.sections if s["id"] not in FRAME_IDS and not s["frame"]]
        t = q["section_target"]
        if len(body) < t["total"]:
            problems.append(f"body sections: {len(body)}, want at least {t['total']} "
                            f"(competitors {t['matched']} + {t['extra']})")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    schema = json.loads((ROOT / "schemas/queries.schema.json").read_text(encoding="utf-8"))
    examined = unbuilt = 0
    problems = []
    for f in sorted((root / "data/queries").glob("*.json")):
        if f.name == "spend.json":
            continue
        q = json.loads(f.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(q, schema)
        except jsonschema.ValidationError as e:
            problems.append(f"{f.stem}: invalid question file — {e.message}")
            continue
        page = root / "dist" / q["route"].strip("/") / "index.html"
        if not page.is_file():
            unbuilt += 1
            continue
        examined += 1
        problems += [f"{q['slug']}: {p}" for p in check_page(q, page.read_text(encoding="utf-8"))]
    for p in problems:
        print(p)
    print(f"examined {examined} pages ({unbuilt} not built); {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the gate tests**

Run: `python3 -m pytest tests/py/test_query_coverage_check.py -q`
Expected: all pass.

In `test_main_fails_a_built_page_with_problems`, the only problem is the body count (6 < 9). If a second problem appears, the fixture and the parser disagree: print the problem list and fix the parser. Do not change the fixture.

- [ ] **Step 5: Wire into check:all, test first**

In `tests/py/test_package_scripts.py`, change the `expected` list to:

```python
    expected = ["check:parity", "check:facts", "check:links", "check:verbatim",
                "check:redirects", "check:schema", "check:queries",
                "check:sitemaps", "check:placeholders", "check:markers", "agents"]
```

Run: `python3 -m pytest tests/py/test_package_scripts.py -q`
Expected: FAIL on the `check:all` assertion.

In `package.json`, add `"check:queries": "python3 scripts/query_coverage_check.py",` after `"check:schema"`. Then change `check:all` so that `&& npm run check:queries` follows `npm run check:schema`.

Run: `python3 -m pytest tests/py/test_package_scripts.py -q && npm run check:queries`
Expected: tests pass. The gate prints `examined 0 pages (0 not built); 0 problems` (no question files exist yet). If `data/queries/` does not exist, `glob` on a missing directory returns nothing, which is correct.

- [ ] **Step 6: Regenerate registries, run the full Python suite, commit**

```bash
python3 scripts/build_system_registry.py
npm run test:py
git add scripts/query_coverage_check.py tests/py/test_query_coverage_check.py package.json tests/py/test_package_scripts.py docs/reference/system-registry.md
git commit -m "gate: query coverage — three FAQ blocks, every must-answer question answered, the section target

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

Expected from `npm run test:py`: every test passes, and the count rises by the number of new tests.

---

### Task 7: Live pilot on Manchester (controller-run)

**Files:**
- Create: `data/queries/raw/blue-staffy-puppies-manchester-uk/*.json`, `data/queries/spend.json`, `data/queries/blue-staffy-puppies-manchester-uk.json`
- Modify: `data/settings.json` (`query_typical_call_usd`, possibly `query_budget_usd`)

The controller runs this task, not a subagent, because it spends real money through the connector. **Ask the user before the first paid call and wait for a yes.**

- [ ] **Step 1: Load the connector tools**

Use ToolSearch `select:` to load the DataForSEO `serp_organic_live_advanced`, `ai_optimization_llm_response` (or `ai_optimization_chat_gpt_scraper`), and the Firecrawl `firecrawl_scrape` and `firecrawl_search` tools. Read each schema. In particular, record whether `serp_organic_live_advanced` accepts a Bing search engine, or whether a separate Bing endpoint exists.

- [ ] **Step 2: Preflight, then Google**

Run: `python3 scripts/query_augment.py --preflight blue-staffy-puppies-manchester-uk --source serp_google`
Expected: `proceed`.

Ask the user for approval. Then call the SERP tool with keyword `blue staffy puppies manchester`, location United Kingdom, language English, depth 10.
- Save the response unchanged as `data/queries/raw/blue-staffy-puppies-manchester-uk/serp_google.response.json`.
- Write `serp_google.json` in the normalised format. Its questions come from the People Also Ask items and the related searches, and each `detail` is `serp_google_paa` or `serp_google_related`.
- Record the response's reported cost:

`python3 scripts/query_augment.py --record blue-staffy-puppies-manchester-uk --source serp_google --endpoint serp_organic_live_advanced --cost <reported cost>`

- [ ] **Step 3: Bing, AI engines, competitors, threads**

Repeat the preflight → call → save → normalise → record sequence for `serp_bing` and `ai_engines`. The AI-engine prompt is: `Where can I buy a blue Staffy puppy near Manchester, and what should I ask the breeder?` Its normalised questions are the questions the answer raises or implies, and each `detail` is `ai_<engine>`.
- If Bing is not available through DataForSEO, get the Bing top 10 with `firecrawl_search` (query plus `bing`), or else with the browser. Write `serp_bing.json` with `"status": "fallback"`. If neither source works, write nothing, so the file stays `NOT FETCHED`.
- **Competitors:** from the Google and Bing top 10, keep the first five breeder or location pages from each engine; drop marketplaces and directories. For each kept page, `firecrawl_scrape` the URL with the markdown format and list its `## ` headings. Write `competitors.json`.
- **Threads:** leave `threads.json` for Task 8, which pilots the thread skill on the same slug.

- [ ] **Step 4: Build, then look at the output**

Run: `python3 scripts/query_augment.py blue-staffy-puppies-manchester-uk --page-type location --keyword "blue staffy puppies manchester" --route /uk-locations/blue-staffy-puppies-manchester-uk/`
Expected: `wrote …` with a section target, or exit 5 with the blocked list. On exit 5, report the blocked list to the user and stop the task. The user decides which facts to add.

Read the file. Check that the must-answer questions read like buyer questions and that none needs an unbacked claim.

- [ ] **Step 5: Set the costs from what was measured**

- Set `query_typical_call_usd` in `data/settings.json` to the largest single cost recorded.
- If one full page (all three paid sources) cost more than 0.5, tell the user the measured figure and ask whether to raise `query_budget_usd`. Do not raise it without a yes.
- Report the total spent against the $1 account.

- [ ] **Step 6: Commit**

```bash
python3 scripts/build_system_registry.py
npm run check:queries
git add data/queries data/settings.json docs/reference/system-registry.md
git commit -m "queries: the Manchester pilot — measured cost, Bing source confirmed, first question file

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

Expected from `npm run check:queries`: `examined 0 pages (1 not built); 0 problems`.

Record the pilot's findings as an execution note at the top of Task 9, for the skill to encode: the tool names, whether Bing came from DataForSEO, and the cost per source.

---

### Task 8: `bsuk-reddit-threads` skill (writing-skills: RED → GREEN → REFACTOR)

**Files:**
- Create: `.claude/skills/bsuk-reddit-threads/SKILL.md`
- Create: `data/queries/raw/blue-staffy-puppies-manchester-uk/threads.json` (the GREEN run's output)
- Read: `/Users/apple/Downloads/CAG/.claude/skills/reddit-strategy/SKILL.md` lines 63–121 (Thread Sourcing Protocol, Standing rules), `.claude/skills/research-recency/SKILL.md`

**REQUIRED SUB-SKILL:** `superpowers:writing-skills`.

- [ ] **Step 1: RED — a baseline without the skill**

Dispatch a subagent (general-purpose) with only this prompt:

> In /Users/apple/Downloads/BSUK, find real Reddit or forum threads where UK buyers ask about buying a blue Staffordshire Bull Terrier puppy near Manchester. Write the questions they ask to data/queries/raw/blue-staffy-puppies-manchester-uk/threads.baseline.json as {"source":"threads","status":"ok","questions":[{"text","detail","fact_source"}]}. Report what you did.

Record its failures verbatim in the task report. Look for: invented or unverified threads or quotes; not climbing the fetch ladder when Reddit blocks; no permalinks; quoting more than 15 words; US threads; taking health, price or licence facts from threads; missing the format. Then delete `threads.baseline.json`.

- [ ] **Step 2: GREEN — write the skill against those failures**

Create `.claude/skills/bsuk-reddit-threads/SKILL.md`. Start from this draft, then add a line to "Common mistakes" for each baseline failure it does not already cover:

````markdown
---
name: bsuk-reddit-threads
description: Use when a BSUK page needs the real questions UK Staffy buyers ask on Reddit and dog forums, or a genuine thread worth citing — derives the searches from the page, climbs the research-recency fetch ladder, scores and opens every thread before using it, and writes data/queries/raw/<slug>/threads.json for bsuk-query-augmentation. Never invents a thread, a quote or a vote count.
---

# Reddit and forum threads for a BSUK page

## Golden rule

A thread you have not opened does not exist. Every question you record comes from a thread
you loaded and read, with its permalink. Blocked after the whole ladder = `NOT FETCHED`.

## Step A — derive the searches from the page, not the topic

From the page's slug, primary keyword and page type, write 4–6 searches:

- `<primary keyword> reddit`
- `site:reddit.com <breed phrase> <city or UK>` — e.g. `site:reddit.com blue staffy puppy manchester`
- `site:reddit.com staffy breeder uk what to ask`
- one per page intent: delivery or collection, price, first-time owner, flat living
- for comparison pages, the two things compared plus `reddit`

## Step B — search through the ladder

Use `.claude/skills/research-recency/SKILL.md`, in order: Firecrawl search → WebFetch or
WebSearch → headless browser (Playwright or chrome-devtools) → `/last30days` when installed.
Reddit often blocks the first rung; that is a reason to climb, not to stop.

Where to look: r/StaffordshireBullTerrier, r/DogAdvice, r/dogs, r/puppy101, r/AskUK,
r/unitedkingdom, and UK dog forums that search turns up.

## Step C — score each candidate (keep 5 or more with a score of 5+)

| Signal | Points |
|---|---|
| It asks what our page answers | 0–3 |
| Posted in the last 24 months | 0–2 |
| Replies (10+ = 2, 3–9 = 1) | 0–2 |
| UK signal (UK place, £, UK law, UK subreddit) | 0–1 |

A US-only thread scores 0 for UK, and it cannot be the page's only source for a question.

## Step D — open and verify

Load each kept thread. Confirm the title, the subreddit and that it is live. From the opening
post and the top replies, write each buyer question as a plain question in your own words
(a paraphrase, never a quote over 15 words). Record the permalink.

## Step E — write the file

`data/queries/raw/<slug>/threads.json`:

```json
{
  "source": "threads",
  "status": "ok",
  "fetched": "YYYY-MM-DD",
  "questions": [
    {"text": "How do I know a Staffy breeder is not a puppy farm?",
     "detail": "thread:r/StaffordshireBullTerrier/<post id>", "fact_source": null}
  ],
  "threads": [
    {"permalink": "https://www.reddit.com/r/…/comments/<id>/…/", "title": "…",
     "subreddit": "r/…", "posted": "YYYY-MM", "replies": 0, "score": 0}
  ]
}
```

`status` is `ok`, `fallback` (only the lower rungs worked) or `NOT FETCHED` (write the file
with an empty `questions` list and say which rungs failed).

## Standing rules

- Threads give QUESTIONS and LANGUAGE, never facts. A price, a health claim, a licence or a
  law comes from the data files and the evidence ledger, never from a thread.
- `fact_source` stays `null` here; bsuk-query-augmentation matches questions to facts.
- Never link or name another breeder, a marketplace listing or a poster.
- Citing a thread on a page is allowed only when it is on-topic, civil, UK, and adds
  something the page cannot say itself — and the link is anchor-first like every link.

## Common mistakes

- Reporting `NOT FETCHED` after the first rung.
- Recording a question from a search snippet without opening the thread.
- Quoting a poster at length instead of paraphrasing the question.
- Treating a thread's advice as a fact for the page.
````

- [ ] **Step 3: GREEN run**

Dispatch a fresh subagent with the same prompt as Step 1, plus: `Use the bsuk-reddit-threads skill.` The output goes to `threads.json`, not the baseline file.

It must comply with every rule in the skill. Where it doesn't, go to Step 4.

- [ ] **Step 4: REFACTOR**

For each new rationalisation the GREEN run shows, add an explicit counter-rule to "Common mistakes" or "Standing rules". Re-run Step 3 until it complies.

- [ ] **Step 5: Guards and commit**

Run: `python3 -m pytest tests/py/test_skills_frontmatter.py tests/py/test_agent_facts.py -q && python3 scripts/build_system_registry.py`
Expected: pass.

Rebuild the pilot file so the threads are counted:

`python3 scripts/query_augment.py blue-staffy-puppies-manchester-uk --page-type location --keyword "blue staffy puppies manchester" --route /uk-locations/blue-staffy-puppies-manchester-uk/`

```bash
git add .claude/skills/bsuk-reddit-threads data/queries docs/reference/system-registry.md
git commit -m "skill: bsuk-reddit-threads — thread sourcing re-based from the source repo, tested against a baseline

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: `bsuk-query-augmentation` skill (writing-skills: RED → GREEN → REFACTOR)

**Files:**
- Create: `.claude/skills/bsuk-query-augmentation/SKILL.md`

**REQUIRED SUB-SKILL:** `superpowers:writing-skills`. Before writing, read Task 7's execution note (tool names, the Bing source, cost per source).

- [ ] **Step 1: RED — a baseline without the skill**

Dispatch a subagent with only this prompt:

> In /Users/apple/Downloads/BSUK, before we write the Leeds location page (slug blue-staffy-puppies-leeds-uk if it exists in data/locations.json, else the first slug there), work out the questions the page must answer, how many sections it needs compared with competitors, and what goes in its FAQ. Do not spend money on paid APIs; you may read files and use free web search. Report your answer.

Record its failures. Look for: a fixed section count; one FAQ block; fewer than 17 FAQ questions; invented questions; facts with no source; no Bing; ignoring `data/faq.json`; no competitor numbers; claiming research it did not do. The prompt forbids paid calls, so the baseline tests judgement, not spending.

- [ ] **Step 2: GREEN — write the skill**

Create `.claude/skills/bsuk-query-augmentation/SKILL.md` from this draft. Replace the tool names in "Paid sources" with the ones Task 7 recorded, and add a "Common mistakes" line for each baseline failure:

````markdown
---
name: bsuk-query-augmentation
description: Use before writing any BSUK location, comparison, blog or puppy page — finds the real questions buyers and AI answer engines ask (DataForSEO Google/Bing results and AI-engine answers, Reddit threads, the FAQ bank), sets the competitor section target, picks the three FAQ blocks, and writes data/queries/<slug>.json, which the page builder fills and scripts/query_coverage_check.py enforces.
---

# Query augmentation

Run this before a page's outline. Its output decides the page's FAQ, three of its sections,
and (for location pages) how many body sections it needs.

## Inputs

`<slug>` · `<page type>`: location, comparison, blog or puppy · `<primary keyword>` · `<route>`.

## Step 1 — preflight before EVERY paid call

```bash
python3 scripts/query_augment.py --preflight <slug> --source <serp_google|serp_bing|ai_engines>
```

- exit 0 → make the call · exit 3 → a saved copy exists, make NO call · exit 4 → stop and
  tell the user the spend (`data/queries/spend.json`); never work around it.
- `--refresh` only when the user asked for fresh data.

## Step 2 — paid sources (DataForSEO connector)

For each paid source: preflight → call → save the response untouched as
`data/queries/raw/<slug>/<source>.response.json` → write the normalised
`data/queries/raw/<slug>/<source>.json` → record the cost the response reports:

```bash
python3 scripts/query_augment.py --record <slug> --source <source> --endpoint <tool> --cost <cost>
```

| Source | Call | Normalised questions |
|---|---|---|
| `serp_google` | organic SERP, UK, English, depth 10 | People Also Ask (`serp_google_paa`) and related searches (`serp_google_related`) |
| `serp_bing` | the Bing source recorded by the pilot | Bing's related questions (`serp_bing`) |
| `ai_engines` | an AI-engine answer to "Where can I buy a <breed phrase> near <city>, and what should I ask the breeder?" (location) or the page's core question | every question the answer raises (`ai_<engine>`) |

Normalised file: `{"source", "status": "ok|fallback", "fetched", "questions": [{"text", "detail", "fact_source"}]}`.
Set `fact_source` only when you can name the data file (and key) whose content answers the
question — e.g. `data/settings.json#delivery_min_gbp`. If you are unsure, leave it `null`;
the bank supplies fact-backed wording.

Connector missing or out of credit: say so, then use the free fallback — the
`bsuk-paa-agent` browser People-Also-Ask protocol and Firecrawl search — with
`"status": "fallback"`. Nothing reachable = no file (the script records `NOT FETCHED`).

## Step 3 — competitors (location pages; optional elsewhere)

From the Google and Bing top 10, keep the first five breeder or location pages from each
(never marketplaces or directories). Open each (Firecrawl scrape, markdown) and list its H2s:

`data/queries/raw/<slug>/competitors.json` = `{"status", "pages": [{"url", "google_pos", "bing_pos", "h2": [...]}]}`.

Do not clean or count them yourself — the script does, the same way every time.

## Step 4 — threads

Run `bsuk-reddit-threads` for the slug. It writes `raw/<slug>/threads.json`.

## Step 5 — build the question file

```bash
python3 scripts/query_augment.py <slug> --page-type <type> --keyword "<primary keyword>" --route <route>
```

- exit 0 → `data/queries/<slug>.json` holds the questions, the FAQ picks (`faq`: top, middle or
  bottom), `extra_sections` and `section_target`.
- exit 5 → too few fact-backed questions for a FAQ block. Show the user the blocked list and
  stop. Never pad, never invent a fact to unblock a question.

## Step 6 — hand to the page builder

The builder writes the page from the file:

- FAQ: three `Faq` blocks (top, middle, bottom) with exactly the picked questions, in score order;
  each answer drawn from its `fact_source`.
- Body: at least `section_target.total` body sections; one H2 per `extra_sections` topic.
- Every `must_answer` question gets `covered_by` filled — `{"where": "faq", "text": <the question
  as written on the page>}` or `{"where": "heading", "text": <the heading that answers it>}` —
  and every extra section gets its `heading`.

Re-running Step 5 keeps those fills. Then `npm run build && npm run check:queries`.

## Common mistakes

- Making a paid call without preflight, or after exit 3 or 4.
- Counting competitor sections by hand, or using a fixed section number.
- One FAQ block, or fewer than the picked questions.
- Setting `fact_source` to a file that does not answer the question.
- Rewording a question on the page and not updating `covered_by.text`.
````

- [ ] **Step 3: GREEN run**

Dispatch a fresh subagent with the Step 1 prompt, plus: `Use the bsuk-query-augmentation skill. Paid calls are NOT allowed in this run: run preflight, and where a paid source would be called, stop and report what you would call and why.` It must follow every step, stop correctly at the paid boundary, and build from the free and bank sources. Any exit 5 must be handled by the rule.

- [ ] **Step 4: REFACTOR**

Close every loophole the GREEN run shows. Re-run until it complies. Delete any files it wrote for the Leeds slug unless they are correct and wanted, and ask the controller.

- [ ] **Step 5: Guards and commit**

Run: `python3 -m pytest tests/py/test_skills_frontmatter.py tests/py/test_agent_facts.py -q && python3 scripts/build_system_registry.py`
Expected: pass.

```bash
git add .claude/skills/bsuk-query-augmentation docs/reference/system-registry.md
git commit -m "skill: bsuk-query-augmentation — the question step every page builder runs first

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: Point the four page builders at the skill

**Files:**
- Modify: `.claude/skills/bsuk-location-page-builder/SKILL.md` (Step 1 procedure item 4, the "Query augmentation" paragraph at lines ~173–179, Step 5 at lines ~215–220, "Before you write anything" item 2)
- Modify: `.claude/skills/bsuk-comparison-page-builder/SKILL.md` (§3, first line), `.claude/skills/bsuk-blog-post/SKILL.md` (§3, first line), `.claude/skills/bsuk-puppy-page-builder/SKILL.md` (§0, end)

- [ ] **Step 1: Location builder, Step 1, item 4**

Replace item 4 of Step 1's procedure (from `4. **Derive the section list**` to `Drop a topic rather than pad it with a claim.`) with:

```markdown
4. **Set the section count** with `/bsuk-query-augmentation` (it runs this scan with Bing
   included and writes `data/queries/<slug>.json`): the pool is the top-5 breeder/location
   pages on Google plus the top-5 on Bing; non-content H2s are stripped; the page matches the
   highest cleaned count (an outlier over 1.5× the next is recorded and skipped), then adds
   the three `extra_sections` the question pool suggests. `section_target.total` is the
   minimum number of body sections; `scripts/query_coverage_check.py` fails a page below it.
   Body topics come from what the pooled pages cover plus the gaps, minus anything BSUK cannot
   state from the fact table above. Drop a topic rather than pad it with a claim.
   `docs/reference/location-page-template.md` is the full rule and the page's structure.
```

Also change the frontmatter `description`. It currently says the skill "derives the section list from a live competitor scan rather than a fixed template". Add after that phrase: `(competitors' section count + 3, via bsuk-query-augmentation)`.

- [ ] **Step 2: The query-augmentation paragraph**

Replace the whole paragraph that starts with `**Query augmentation (before writing).**` and ends with `this paragraph is the whole procedure until one exists.` with:

```markdown
**Query augmentation (before writing).** Run `/bsuk-query-augmentation <slug> location
"<primary keyword>" /uk-locations/<slug>/` before the outline. Its question file decides the
FAQ picks, the three extra sections and the section target; answer every `must_answer`
question on the page and record where in `covered_by`.
```

- [ ] **Step 3: Step 5, FAQ**

Replace the body of `## Step 5 — FAQ` (from `` `data/faq.json` supplies the base questions. `` to `schema, no visible date.`) with:

```markdown
Three `Faq` blocks — **top** (5–7: price, deposit, delivery to this city, reserving),
**middle** (5–7: paperwork, health testing, visiting, age at collection) and **bottom**
(7–10: flats, children and other pets, training, lifespan, coat) — carrying
exactly the questions `data/queries/<slug>.json` picked for each block, 17–20 in all. Each
question renders as an H3 with a short, direct answer drawn from its `fact_source`; links sit
inside answers, anchor first. An answer that introduces a new fact is a fabricated claim with
extra steps. FAQPage schema carries exactly the visible questions, no visible date.
`scripts/query_coverage_check.py` holds all of this.
```

- [ ] **Step 4: "Before you write anything", item 2**

Replace `2. Run the competitor scan and record it in the board.` with:

```markdown
2. Run `/bsuk-query-augmentation` for the slug (competitor scan, questions, FAQ picks, section
   target), and record the competitor block and section target in the board.
```

- [ ] **Step 5: The worked example**

In the Manchester worked example table:
- Replace the row `| 19 | Manchester Buyer Questions | …` with three rows: FAQ top, middle and bottom. Put them after rows 5, 12 and 18 respectively, and renumber the rows.
- Replace the two `Competitor-gap section | NOT FETCHED — step 1 supplies the topic` rows with three rows reading `Extra section (question pool) | extra_sections[n] in data/queries/blue-staffy-puppies-manchester-uk.json`.

Keep every other row unchanged.

- [ ] **Step 5b: The spine, the precedence table and the fact table**

- **Step 2 spine:** replace the rows of the table under `## Step 2 — the page spine` with the 13-part frame order in `docs/reference/location-page-template.md` ("The fixed frame"). Keep the table's three columns. Each frame row keeps the component and checks it has today; FAQ top, middle and bottom each use `Faq`; the form uses `ContactFormKit`. Mark the three body gaps as rows reading `Body sections (derived, step 1)`. Change the sentence above the table to say that the body sections fill the three gaps, split roughly evenly.
- **Precedence table:** add a row to the table under `## What wins when this file and something else disagree`: `docs/reference/location-page-template.md` wins for structure, FAQ format and tone; this file's fact table wins for facts.
- **Fact table:** add "home-raised: every puppy is raised in our home, not a kennel" with its source, the `data/faq.json` row whose answer says so. Add it only if that row exists; quote its `id`.

- [ ] **Step 6: The other three builders**

Insert this paragraph as the first paragraph under each of these headings: `## 3. Per-Page Research Protocol` in the comparison builder, `### 3. Tiered Sprint 0.5 Research Method` in the blog skill, and the end of `## 0. The board comes first` in the puppy builder. Use the page type `comparison`, `blog` or `puppy` respectively:

```markdown
**First, run `/bsuk-query-augmentation <slug> <page type> "<primary keyword>" <route>`.** Its
file (`data/queries/<slug>.json`) supplies the page's FAQ blocks and three extra sections, and
every `must_answer` question must be answered on the page with `covered_by` recorded —
`npm run check:queries` fails the page otherwise. The research below builds on that file; it
does not replace it.
```

- [ ] **Step 7: Guards and commit**

Run: `python3 -m pytest tests/py/test_skills_frontmatter.py tests/py/test_agent_facts.py tests/py/test_rules_index.py -q`
Expected: pass. The fact lint's lifespan rule reads a window around every "year": keep other numbers out of any sentence that states the lifespan. The table lint in `test_skills_frontmatter.py` must also pass after the worked-example table edit. If it fails, fix the table's column count.

```bash
git add .claude/skills/bsuk-location-page-builder .claude/skills/bsuk-comparison-page-builder .claude/skills/bsuk-blog-post .claude/skills/bsuk-puppy-page-builder
git commit -m "skills: every page builder runs query augmentation first; location pages take the three-block FAQ and the competitor-plus-three rule

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 11: Ban and scrub the parrot residue

**Files:**
- Modify: `tests/py/test_agent_facts.py` (`BANNED`)
- Modify: `.claude/skills/bsuk-comparison-page-builder/SKILL.md`, `.claude/skills/bsuk-seo-master-checklist/SKILL.md`, `.claude/agents/bsuk-content-audit-agent.md`

The automatic CAG → BSUK word swap left parrot terms in three instruction files, and the fact lint did not catch them. Examples: "Blue-Brindle Staffy (*Psittacus blue-brindle*)", "Amazon Puppy", "closed leg band", "cloacal papilloma", "powder-down dander", "psittacosis", "Google US", and the garbled "UKge" (from "usage"). Found 2026-09-23: 27 hits.

- [ ] **Step 1: Write the failing lint**

In `tests/py/test_agent_facts.py`, add this line to the `BANNED` tuple, after the `"Glasgow",` entry and its comment:

```python
    # Parrot residue from the source repo's species (found 2026-09-23 in the comparison
    # builder, the SEO checklist and the content-audit agent). A dog page that promises a
    # leg band or warns about psittacosis tells the reader nobody checked it.
    "Psittac", "psittac", "leg band", "powder-down", "cloacal", "proventricular",
    "Amazon Puppy", "Amazon puppy", "amazons =", "Google US", "UKge",
```

- [ ] **Step 2: Run the lint to verify it fails**

Run: `python3 -m pytest tests/py/test_agent_facts.py -q`
Expected: FAIL, naming lines in the three files.

- [ ] **Step 3: Fix every hit**

Run `grep -rnE "Psittac|psittac|leg band|powder-down|cloacal|proventricular|Amazon Puppy|Amazon puppy|amazons =|Google US|UKge" .claude` to list the hits. Fix each one by this rule:
- **The comparison builder's §2 conversion-map rows:**
  - `Maltese` → `Blue-Brindle Staffy` (no Latin name).
  - `Poodle` → delete the row (no BSUK analogue).
  - The OFA/Embark row → `L-2-HGA and HC-HSF4 DNA screening of the parents, where the evidence ledger records the certificate · vet health check · microchip`.
  - The "Species-appropriate risks" row → `Staffordshire Bull Terrier: the hereditary conditions the breed is DNA-tested for (L-2-HGA, HC-HSF4); any other health claim needs an evidence-ledger entry`.
  - The shedding row → `short single coat, moderate shedding — no allergy or "hypoallergenic" claim`.
- **"Google US"** → "Google UK". **"UKge"** → "usage".
- **Any other sentence built on a parrot fact** (psittacosis, leg bands, proventricular dilatation, cloacal papilloma, powder-down): delete the sentence, or replace it with the Staffy fact above when the paragraph needs one. Never keep a parrot claim reworded.

- [ ] **Step 4: Run the lint and the suite**

Run: `python3 -m pytest tests/py/test_agent_facts.py -q && npm run test:py`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add tests/py/test_agent_facts.py .claude/skills/bsuk-comparison-page-builder .claude/skills/bsuk-seo-master-checklist .claude/agents/bsuk-content-audit-agent.md
git commit -m "lint: ban the parrot residue the port left in three instruction files, and scrub it

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 12: Housekeeping — manifest, session log, registries

**Files:**
- Modify: `data/port-manifest.json`
- Modify: `docs/reference/session-log.md`
- Regenerate: `docs/reference/system-registry.md`, `data/agent-registry.json`

- [ ] **Step 1: Manifest — re-file reddit-strategy**

In `data/port-manifest.json`, change the `notes` of the row whose `src` is `.claude/skills/reddit-strategy/SKILL.md` to:

`"thread-sourcing half rebuilt for BSUK as .claude/skills/bsuk-reddit-threads/SKILL.md (2026-09-23, not a port — written against a baseline test); the reddit-modifier page playbook stays deferred — open item in docs/reference/session-log.md"`

Keep `mode` as `deferred`: the file itself still has not crossed.

- [ ] **Step 2: Manifest — the ten rows never recorded**

Append these rows at the end of the array (the manifest is chronological, so never sort it). Each has `"mode": "deferred"`:

```json
  {"src": ".claude/skills/cag-bird-listing-page/SKILL.md", "dst": ".claude/skills/bsuk-bird-listing-page/SKILL.md", "mode": "deferred", "notes": "parrot-only (species listing page); no BSUK analogue — recorded 2026-09-23, never ported"},
  {"src": ".claude/skills/cag-bird-page-build/SKILL.md", "dst": ".claude/skills/bsuk-bird-page-build/SKILL.md", "mode": "deferred", "notes": "parrot-only page build; bsuk-puppy-page-builder covers the puppy pages — recorded 2026-09-23, never ported"},
  {"src": ".claude/skills/cag-bird-page-excellence/SKILL.md", "dst": ".claude/skills/bsuk-bird-page-excellence/SKILL.md", "mode": "deferred", "notes": "parrot-only page polish; bsuk-final-page-pass covers the gate — recorded 2026-09-23, never ported"},
  {"src": ".claude/agents/cag-bird-personality.md", "dst": ".claude/agents/bsuk-bird-personality.md", "mode": "deferred", "notes": "parrot-only temperament writer — recorded 2026-09-23, never ported"},
  {"src": ".claude/agents/cag-clutch-manager.md", "dst": ".claude/agents/bsuk-clutch-manager.md", "mode": "deferred", "notes": "parrot clutch records; BSUK litters live in data/puppies.json — recorded 2026-09-23, never ported"},
  {"src": ".claude/agents/cag-timneh-specialist.md", "dst": ".claude/agents/bsuk-timneh-specialist.md", "mode": "deferred", "notes": "parrot subspecies specialist; no BSUK analogue — recorded 2026-09-23, never ported"},
  {"src": ".claude/agents/cag-species-guide-builder.md", "dst": ".claude/agents/bsuk-species-guide-builder.md", "mode": "deferred", "notes": "parrot species guide; the BSUK breed guide is built — recorded 2026-09-23, never ported"},
  {"src": ".claude/agents/cag-variant-specialist.md", "dst": ".claude/agents/bsuk-variant-specialist.md", "mode": "deferred", "notes": "variant pages; a coat-colour version for Staffies is possible later — recorded 2026-09-23, not ported"},
  {"src": ".claude/agents/cag-competitor-pricing-alert-agent.md", "dst": ".claude/agents/bsuk-competitor-pricing-alert-agent.md", "mode": "deferred", "notes": "needs a live site and a competitor list; project 6 at the earliest — recorded 2026-09-23"},
  {"src": ".claude/agents/cag-competitor-registry.md", "dst": ".claude/agents/bsuk-competitor-registry.md", "mode": "deferred", "notes": "a stored competitor list; BSUK records competitors per page in data/queries/<slug>.json instead — recorded 2026-09-23, not ported"}
```

- [ ] **Step 3: Validate the manifest**

Run: `python3 -m pytest tests/py/test_port_manifest.py -q && python3 scripts/marker_check.py`
Expected: pass; `0 problems`.

- [ ] **Step 4: Session log**

In `docs/reference/session-log.md`:
- Mark Known Issue 17 closed. Append to its paragraph: `**Closed 2026-09-23** by `.claude/skills/bsuk-query-augmentation/SKILL.md`, `scripts/query_augment.py` and the gate `scripts/query_coverage_check.py` (in `npm run check:all`).`
- Add two new Known Issues, numbered after the current last one:
  - `**Reddit-modifier pages are a recorded option, not built.** Short pages aimed at "<keyword> reddit" searches (the source repo's playbook). Decide with search-volume data in project 5 or later; the thread half is `.claude/skills/bsuk-reddit-threads/SKILL.md`.`
  - `**No page-communication audit.** The source repo's visual-intelligence skill (does the page communicate, what job is it doing, why do two pages feel the same) was filed with the design system in project 2 and never ported. The 28 city pages in project 5 are where it would pay.`

- [ ] **Step 5: Registries and the full suite**

```bash
python3 scripts/build_system_registry.py
python3 scripts/build_agent_registry.py
npm run registry
npm run agents
npm run test:py
npm run check:all
```
Expected: every command exits 0. `check:all` includes `check:queries`, which prints `examined 0 pages (1 not built); 0 problems`.

- [ ] **Step 6: Commit**

```bash
git add data/port-manifest.json docs/reference/session-log.md docs/reference/system-registry.md data/agent-registry.json
git commit -m "record: reddit-strategy re-filed, the ten source files the manifest never named, Known Issue 17 closed

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 13: Close-out

**Files:**
- Create: `docs/reports/query-augmentation-gate-report.md`, `docs/artifacts/bsuk-query-augmentation-report.html`
- Modify: `docs/reference/session-log.md` (session entry)

- [ ] **Step 1: Whole-branch review**

Dispatch `superpowers:code-reviewer` over `git diff foundation...query-augmentation`, with the spec as the requirements. Fix every Critical and Important finding, with a re-review for each.

- [ ] **Step 2: Two clean runs**

Run twice: `npm run test:py && npm run build && npm run check:all`
Expected: both runs exit 0 with identical counts.

- [ ] **Step 3: Gate report**

Write `docs/reports/query-augmentation-gate-report.md`. It must cover:
- the spec's definition, section by section (§1–§13), with PASS, PASS-WITH-DEVIATION or FAIL and the evidence for each;
- the pilot's measured cost per source and the spend against the $1;
- the Bing source that was used;
- the RED baseline failures and how each skill closes them;
- open items.

Publish it:

`python3 scripts/build_report_artifact.py docs/reports/query-augmentation-gate-report.md docs/artifacts/bsuk-query-augmentation-report.html`

Check the script's argv defaults before running. If it takes more arguments, mirror the spec call's argument order. Then publish the HTML with the Artifact tool.

- [ ] **Step 4: Session log and merge**

Add a session-log entry for this build: dates, commits, what shipped, and next = project 5.

```bash
git add docs/reports/query-augmentation-gate-report.md docs/artifacts/bsuk-query-augmentation-report.html docs/reference/session-log.md
git commit -m "report: query augmentation gate report

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git switch foundation
git merge --ff-only query-augmentation
git branch -d query-augmentation
```

If `--ff-only` refuses, stop and ask the user. Never force a merge.

- [ ] **Step 5: Session closer**

Run `/session-closer`. Name the next build: **project 5, location, comparison and blog pages**. It starts with brainstorming, and each page begins with `/bsuk-query-augmentation`.
