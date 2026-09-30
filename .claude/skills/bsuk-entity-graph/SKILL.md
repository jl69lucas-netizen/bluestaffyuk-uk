---
name: bsuk-entity-graph
description: Use when a page, cluster, or the whole site must be modelled as a knowledge graph rather than as keywords — "what entities does this page own", "map the relationships", "build the knowledge graph", "why do answer engines cite competitors instead of us", entity gap analysis, predicate/relationship audit, schema-versus-prose drift, entity cannibalization between pages, orphan and missing-internal-link discovery, or preparing a page for LLM retrieval and AI citation. Also use before building a sibling page, to see which entities are already owned elsewhere.
---

# SKILL: BSUK Entity Relationship & Knowledge Graph Intelligence

Model the page as a **living knowledge graph**: typed entities, authorized relationships,
scored connectivity. Never keyword analysis — `keyword-cluster` and `@bsuk-keyword-verifier`
own that, and they answer a different question.

**Where this sits.** `.claude/skills/bsuk-entity-agent/SKILL.md` is the passive **catalog** (vocabulary).
`@bsuk-seo-content-writer` is the **writer** (injects entities into prose, `entity-4-move-loop`). This
skill is the **analyzer** — it builds and scores the graph, finds what is missing, and
hands both of the others a work list they can act on.

**Do not reimplement graph math.** `graphify` already ships extraction, community
detection, centrality, GraphRAG JSON, Neo4j and Obsidian export. This skill supplies the
**BSUK ontology and the authorization layer**; graphify does the math.

---

## 0. The Iron Rules

**0a. Every edge is authorized or it is not asserted.** An unbounded extractor will
happily emit `SCREENED_FOR(L-2-HGA)`, `CERTIFIED_BY(LICENCE_CLAIM_PLACEHOLDER)` and `IMPORTED_FROM(Africa)` with
identical confidence. Each edge carries a state:

| State | Meaning |
|---|---|
| `ASSERTED` | Backed by a proven row of `data/quality/evidence-ledger.json` or a `data/*.json` file |
| `PROPOSED` | Extracted from prose, not yet ledger-backed → a **finding**, never a fact |
| `BLOCKED` | Hits the §3c blacklist → hard FAIL on the page |

**0b. Schema is ground truth before prose is.** `dist/` JSON-LD is the most reliable
entity source on any BSUK page and a text-first extractor walks straight past it. On
`/blue-staffy-pup-sale-uk/` that is 15 typed nodes — 5 `Product`, 4 `Offer`,
`FAQPage`, `AggregateOffer`, `AggregateRating`, `ItemList`, `BreadcrumbList`, `WebPage`,
`Organization`, 2 `Review` — free, typed, and unambiguous. Extract schema first, prose
second, then **diff them** (§4).

**0c. A suspiciously high count means a broken extractor.** One checker on this site
reported 586 defects where there were 2. Print the extractor's own examined counts —
pages, nodes, edges — and refuse to report a run that examined zero. Read
`.claude/skills/bsuk-gate-integrity/SKILL.md` before acting on any number this skill produces.

**0d. Never fabricate a competitor's graph.** Un-fetched is `NOT FETCHED`, never inferred.
The fetch order is `curl` → WebFetch with a browser UA → a headless browser → Firecrawl last, because it spends the user's credits (`.claude/skills/bsuk-query-augmentation/SKILL.md`, Step 3).

**0e. Terminate deterministically.** The source spec says "continue until complete."
Use the closed type and predicate taxonomies below; genuinely new items go to
`UNCLASSIFIED` with a proposed taxonomy edit. Runs must diff week over week.

---

## 1. The BSUK ontology

Promote the catalog in `.claude/skills/bsuk-entity-agent/SKILL.md` into a typed ontology at
`data/bsuk-ontology.json` — reproducible, diffable, reviewable.

### 1a. Entity types

| Class | Types |
|---|---|
| **Organism** | Species (*Canis lupus familiaris*) · Breed (Staffordshire Bull Terrier) · Coat colour (each pup's `colour` in `data/puppies.json`) · Individual Puppy (Roman, Byrd, Ince, Vennie, Christa, Cheryl) · Parents (Maggie, the dam; Jones, the sire) |
| **Organization** | Brand (BlueStaffyUK) · Breeder Person (Lisa Bright) · Registry (The Royal Kennel Club) · Transport (DEFRA-approved transport) · Regulator (LICENCE_CLAIM_PLACEHOLDER) |
| **Place** | Country (UK) · Region · City · Home (Carlisle, Cumbria) |
| **Commerce** | Price · Offer · Guarantee (`guarantee_days`, null today) · Delivery Option · Payment Term · Availability State |
| **Documentation** | LICENCE_CLAIM_PLACEHOLDER paperwork · DNA certificate (the parents' L-2-HGA and HC-HSF4 results, `NOT FETCHED`) · Health record · Whelp certificate · Vet record |
| **Health** | Condition (L-2-HGA, HC-HSF4 hereditary cataract, skin allergies) · Screening (DNA test on both parents) · Vet health check · Vaccination · Diet |
| **Behavior** | Temperament ability · Bonding · Bite inhibition · Socialization · Training method |
| **Method** | none on file — the breeder has not named a house method, so no Method node is asserted |
| **Concept** | Comparison topic · Educational concept · Buyer objection · Trust signal · Legal concept |
| **Buyer** | Customer · Family archetype (CLEO/REX/NOVA/SAGE/IRIS) · Review |

### 1b. Predicates, and which type-pairs may use them

Closed set: `IS_A · SUBSPECIES_OF · HAS · PART_OF · BELONGS_TO · LOCATED_IN · OWNED_BY ·
RAISED_BY · BRED_FROM · CREATED_BY · PROVIDED_BY · SUPPORTED_BY · TRAINED_WITH ·
PURCHASED_BY · SHIPS_TO · PRICED_AT · GUARANTEED_FOR (`guarantee_days`) · SCREENED_FOR · CERTIFIED_BY ·
DOCUMENTED_BY · RELATED_TO · SIMILAR_TO · DIFFERENT_FROM · BETTER_THAN · COMPARES_WITH ·
SUITABLE_FOR · INCLUDES · EXCLUDES · CAUSES · PREVENTS · DEPENDS_ON · LEADS_TO ·
DESCRIBES · EXPLAINS · MEASURES · UNCLASSIFIED`.

The ontology stores the **legal type-pair for each predicate**. `Puppy —SCREENED_FOR→
Condition` is legal; `Place —SCREENED_FOR→ Price` is an extractor bug and must be rejected
at extraction time rather than scored later. This single constraint kills most of the
noise that makes generic graph output unUKble.

### 1c. Attributes required per entity
`type · label · canonical_id · salience (0–1) · centrality · source (schema | prose |
alt | link | data-file) · authorization · first_seen_section · owning_page`.

---

## 2. Build the graph

### 2a. Extraction order (never reversed)
1. **JSON-LD** from `dist/<slug>/index.html` — typed nodes, free.
2. **Headings** H1–H6 — the page's own declared hierarchy; H1→H2→H3 nesting is a
   `PART_OF` skeleton.
3. **Tables** — the densest relationship source on comparison and pricing pages; each row
   is usually one predicate applied across two entities.
4. **Body prose** — subject–predicate–object triples.
5. **Image alts + captions** — often carry entities the prose omits (the source repo's
   visual-intelligence skill verbalized these; not ported — source repo only, Known Issue 44).
6. **Internal links** — realized `RELATED_TO` edges; anchor text names the relationship.
7. **`data/*.json`** — `price-matrix`, `puppies`, `settings`, `faq`, `reviews`,
   `locations`, `competitors` — the authorization source.

### 2b. Hand the graph to graphify

```bash
/graphify <corpus-path> --directed          # preserves source→target
/graphify <path> --mode deep                # richer inferred edges
/graphify query "which page owns LICENCE_CLAIM_PLACEHOLDER documentation?"
/graphify path "Blue Staffy" "L-2-HGA"
/graphify <path> --neo4j                    # cypher export
```

graphify computes density, modularity, centrality, communities and shortest paths. This
skill supplies the ontology, the authorization states and the interpretation. Where the
corpus is a single page, a direct extractor is fine — but the **metrics must still be
computed, not estimated**.

### 2c. Three tiers — the cluster tier is where the value is

| Tier | Corpus | Answers |
|---|---|---|
| **Page** | one slug | What does this page own? What is missing? |
| **Cluster** | 22 for-sale · 8 comparison · ~100 location · 9 blog · 9 puppy | Who owns which entity? Where is the cannibalization? Which links are missing? |
| **Site** | all ~108 pages | Topical authority shape, orphans, hub→spoke gaps |

---

## 3. Authorization

**3a. Ledger check.** Every health, credential, testing and outcome edge is checked
against the verified-claim ledger (`data/quality/evidence-ledger.json`). A parent
health-test claim (L-2-HGA, HC-HSF4) is assertable **only** where the ledger records the
certificate; every un-listed clinical claim, every licence and every statute is
LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER or NOT FETCHED.

**3b. The three fact predicates that have regressed before — check on sight:**

| Predicate | Correct value | Wrong value seen in the wild |
|---|---|---|
| `CERTIFIED_BY` | LICENCE_CLAIM_PLACEHOLDER — no licence or certification is on file until the breeder confirms it | a named licence, council permission or certificate written as fact |
| `PRICED_AT` | **£1,500** a male · **£1,700** a female (`data/price-matrix.json`) | a flat "NOT FETCHED", or one price for the litter |
| `GUARANTEED_FOR` | the length in `guarantee_days` (`data/settings.json`) — null today, so no length is written | "72-hour", "3-day" or a 24-hour window (the source repo's) |

**3c. Blacklist — any hit is a hard FAIL on the page, not a low score:**
`WILD_CAUGHT · IMPORTED_FROM · CAUGHT_IN · SMUGGLED · UNDOCUMENTED_SALE`, or any phrasing
implying wild capture or illegal trade. Every puppy is home-bred in the UK and goes home with
its paperwork (`data/faq.json` `whyus-paperwork`).

**3d. No Method node.** BSUK has no named house method (the breeder has never given one,
and `scripts/aeo_audit.py` keeps `LABELED_METHODS` empty). A page that describes how Lisa
raises the litter asserts `RAISED_BY` and `LOCATED_IN` triples, never a named Method entity;
a capitalised method name on a page is a finding, because it is a credential nobody made.

---

## 4. The four gap analyses that make this skill worth running

**4a. Schema ↔ prose drift.** Entities asserted in prose but absent from JSON-LD, and
vice versa. Nobody checks this today and it is directly actionable — a `Product` in prose
with no `Offer` node, a puppy sold in copy but still `InStock` in schema, an
`AggregateOffer` on a page that should carry a single `Product`+`Offer`.

**4b. Entity ownership + cannibalization.** For each entity, rank pages by salience. Two
pages both central on the same entity is the cannibalization signal
`@bsuk-site-hygiene-agent` wants — now with a number behind it. Output an **entity
ownership map**: one owning page per entity, everyone else links to it.

**4c. Unrealized edges = missing internal links.** A high-weight `RELATED_TO`,
`COMPARES_WITH` or `PART_OF` edge with no corresponding `<a>` is a missing link. Emit each
with a **Link-First anchor** (anchor at the START of the sentence, inside the first
clause — never mid-sentence, never at the end) and a diversified anchor from the Anchor
Diversity Ledger in `.claude/skills/internal-link-agent/SKILL.md`. Also report orphans: entities with in-degree 0.

**4d. Competitor delta.** The source repo's competitor list was **not ported — source
repo only**, and no BSUK competitor set has been fetched. When one exists, extract the entity set of the top-ranking competitor
pages for the same query and subtract ours. **Missing Entities becomes evidence-based.**
Un-fetched competitors are listed as `NOT FETCHED` — never inferred, never averaged in.

---

## 5. Metrics

Compute, never estimate. Every metric carries `examined:` counts.

**Entity:** count · type diversity (distinct types ÷ ontology types) · density (entities
per 1,000 words) · coverage (page entities ÷ expected set for the page type) ·
salience per entity · centrality (degree + betweenness, from graphify) · authorization
ratio · novelty (entities we own that competitors lack) · balance (no single type > 40%
of nodes — a page that is all Price and no Documentation is a thin page).

**Relationship:** count · density (edges ÷ nodes) · predicate diversity · hierarchy depth
(longest `PART_OF`/`IS_A` chain) · confidence distribution · **realization rate** (edges
with a corresponding link or schema property ÷ all edges).

**Graph:** density · connectivity (is it one component or several islands?) · diameter ·
cohesion · centralization · modularity/communities · **explainability** — can each
community be named in one phrase? An unnameable community is a section with no thesis.

**Semantic:** coverage · depth · breadth · ontology fit (share of edges using legal
type-pairs) · **LLM readiness** (typed + declarative + schema-backed) · retrieval
readiness (does each section survive being chunked alone?) · AI citation readiness
(feeds `bsuk-aeo-pass`).

---

## 6. Output contract

Save to `docs/superpowers/sessions/<date>-entity-graph-<slug>.md`, machine artifacts to
`data/graphs/<slug>.json` (or `graphify-out/`).

Executive summary (verdict first) · Entity inventory · Entity classification table (type ·
salience · centrality · authorization · source) · Relationship inventory · Predicate
inventory · Graph summary + community names · Semantic cluster analysis · Connectivity
report (orphans, islands) · **Schema↔prose drift** · **Entity ownership map** ·
**Missing internal links, Link-First ready** · Competitor delta (with `NOT FETCHED` rows) ·
Knowledge gaps · Recommendations with owners · Overall Entity Intelligence / Knowledge
Graph / Semantic scores.

**Verdict gates:** any `BLOCKED` edge = FAIL. Any of the three §3b fact predicates wrong =
FAIL. Ontology fit < 90% = the extractor is broken, not the page.

| Finding | Route to |
|---|---|
| Missing entities in copy | `@bsuk-seo-content-writer` (4-Move Loop) |
| Vocabulary/catalog additions | `.claude/skills/bsuk-entity-agent/SKILL.md` |
| Missing/incorrect schema | `bsuk-aeo-pass`, page builder for the type |
| Missing internal links | `internal-link-agent` (Link-First + Anchor Diversity Ledger) |
| Cannibalization | `@bsuk-site-hygiene-agent` |
| Competitor entity gaps | `@bsuk-competitive-keyword-gap-agent` → `@bsuk-content-architect` |
| Un-verbalized image entities | `.claude/skills/image-metadata/SKILL.md` (alt text and captions) |
| Thin/unnameable community | `section-auditor` |

---

## Common mistakes

| Mistake | Reality |
|---|---|
| Extracting from prose first | JSON-LD is typed and free. Schema first, always. |
| Emitting every extracted triple as fact | Un-ledgered = `PROPOSED` = a finding, not a claim. |
| Rebuilding centrality/community code | `graphify` already does it. Supply the ontology instead. |
| Reporting an entity count with no examined count | An extractor that examined 0 pages "passes" everything. |
| Inferring a competitor's entities from their title | `NOT FETCHED`. Fabricated competitor data has burned this site before. |
| Treating the graph as an end product | The deliverable is the **gap list with owners**, not the graph. |
| Counting keyword occurrences | That is `@bsuk-keyword-verifier`. Entities are things, not strings. |
| Letting one page own every entity | Ownership is distributed on purpose — that is what a cluster is for. |

## Red flags — stop, the extractor is wrong

- Node count far exceeding the page's noun count
- Ontology fit below 90% (illegal type-pairs everywhere)
- Every page in a cluster showing identical centrality
- A `NOT FETCHED` competitor quietly appearing in an averaged score
- A graph with zero orphans on a 108-page site — you almost certainly examined one page

---

## Portable core

§§1–2, 5 and the metric definitions are domain-agnostic — the ontology structure,
extraction order, tiering and metrics work on any site. The BSUK binding is the type
vocabulary (§1a), the authorization layer (§3), the four gap analyses (§4) and the routing
table (§6). Replace the ledger and the type list to port it.
