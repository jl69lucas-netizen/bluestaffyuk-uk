# `rules/` — the rule packs

`CLAUDE.md` carries the nine judgment rules — the ones with no
mechanical decision procedure — plus a router to these packs. Everything else lives here.
In the source repo the same split reduced a 37-rule, 88,000-character `CLAUDE.md`; the rule
text crossed **verbatim** except where a source fact did not survive the re-base.

## Reading a rule

Each rule is preceded by front-matter:

```yaml
id: sem-title-case-headings
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

## The injectors — not ported

In the source repo, seven `scripts/add_*_rule.py` injectors wrote rule text into every
agent's Golden Rules, so each of those rules existed twice: once in its pack and once per
agent. **They are not ported (spec §2).** In BSUK the packs are the only source, and an
agent cites a pack rule by its id rather than carrying a copy of its text. There is
therefore no drift to detect, which is why the table below is history and not a checklist.

| Injector (source repo only — not ported) | Pack |
|---|---|
| add_write_from_outline_rule.py | `rules/copy.md` |
| add_first_person_golden_rule.py | `rules/copy.md` |
| add_heading_outline_gate_rule.py | `rules/headings.md` |
| add_title_case_rule.py | `rules/headings.md` |
| add_header_style_rule.py | `rules/headings.md` |
| add_link_first_rule.py | `rules/links.md` |
| add_clarification_checkpoint_rule.py | `rules/gates.md` |
