# Structured data and freshness

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4). **The rule text is verbatim.**

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.


---
id: no-visible-date
enforced: test
family: SCHEMA
test: tests/render/checks/schema.ts::schema-no-visible-date
---

- **NEVER publish a visible date on any page (ALWAYS) — applies to every page, agent, and skill** — Freshness signals live **only in schema** (`dateModified` / `datePublished` in JSON-LD), **never as visible text** on the page. No "Updated June 2026", no "Last updated: …", no visible "Posted on …" anywhere in hero, eyebrow, byline, or body. (Decided by the breeder 2026-06-14, reversing an earlier visible-stamp attempt.) The `manual-auditor-check` auditor enforces this via the `no_visible_date` check (a visible date = FAIL). If you think a page needs a human-visible freshness cue, it does not — put the date in schema and stop.
