# `rules/` — the rule packs

`CLAUDE.md` used to carry ~37 rules in 88,000 characters. It now carries the nine that
have no mechanical decision procedure, plus a router to these packs. Everything else is
here, **verbatim** — the move rewrote nothing.

## Reading a rule

Each rule is preceded by front-matter:

```yaml
id: title-case-headings
enforced: test
family: SEM
test: tests/render/checks/sem.ts::sem-title-case-headings
```

`enforced` is the only field that matters at a glance:

| value | meaning |
|---|---|
| `test` | a committed check fails when the rule is broken |
| `judgment` | no mechanical decision procedure exists; `data/quality/rule-index.json` records why, and the class is capped at 9 |
| `untested` | **deletion candidate** — asserted, and nothing holds it up |

`python3 scripts/quality_report.py` §5 prints every `untested` rule on every run. That
list is the Phase-5 backlog: each one either earns a test or gets deleted. A rule that
sits there indefinitely is documentation pretending to be enforcement.

## The two-copy problem

Seven `scripts/add_*_rule.py` injectors write rule text into all 68 agent Golden Rules.
Moving a rule out of `CLAUDE.md` did **not** remove it from those agents, so several
rules now exist in two places: the pack (the source) and 68 injected copies. Editing a
rule means editing the pack **and** re-running its injector. Nothing detects the drift —
that is a known gap, recorded here rather than left to be discovered.

| Injector | Pack |
|---|---|
| `add_write_from_outline_rule.py` | `rules/copy.md` |
| `add_first_person_golden_rule.py` | `rules/copy.md` |
| `add_heading_outline_gate_rule.py` | `rules/headings.md` |
| `add_title_case_rule.py` | `rules/headings.md` |
| `add_header_style_rule.py` | `rules/headings.md` |
| `add_link_first_rule.py` | `rules/links.md` |
| `add_clarification_checkpoint_rule.py` | `rules/gates.md` |
