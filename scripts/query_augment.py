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
    (r"\bpupp(?:ies|ys)\b", "puppy"),
    (r"\bpups?\b", "puppy"),
)

# Questions that are about the site, not the dog: never a page topic. Checked first.
SKIP = r"\b(personal information|privacy|cookies?|data protection|gdpr|thank you page|reply|enquiry|enquiries|data)\b"

# First match wins, so order is precedence: a price question that mentions a blue coat is
# a price question. Patterns run on normalise()d text (which strips the pound sign).
TOPICS = (
    ("price", "top",
     r"\b(costs?|prices?|priced|deposit|pay|payment|paying|expensive|cheap\w*|afford\w*)\b"
     r"|\bhow much\b(?!.*\b(exercise|food|feed|eat|weigh\w*|sleep\w*|walk\w*)\b)"),
    ("delivery", "top",
     r"\b(deliver\w*|collect\w*|transport\w*|travel\w*|near me|distance|ship\w*|postage|post (a |the )?pupp\w*|courier)\b"),
    ("reserve", "top", r"\b(reserv\w*|waiting (list|time)|how long (do|will|would) i (have to )?wait|book\w*|available|availability"
     r"|where (can|do|should) i (find|buy|get|start)|where should i start)\b"),
    ("age", "middle",
     r"\b(weeks old|how old|leave\w* (its|their|the) mother|when can (a |the )?puppy (leave|go home|come home)"
     r"|when will (my|the) puppy come home)\b"),
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
