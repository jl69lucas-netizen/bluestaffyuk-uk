# Credentials

Every secret lives in `BSUK/.env`, which is gitignored and never committed. This file says
which keys exist and what reads them. **No value appears here, in any report, or in any
Artifact** — not a value, not a fragment of one, not a length hint. If you need a value,
read `.env`; if `.env` is missing, it is rebuilt from the source named in
`docs/superpowers/plans/2026-09-16-system-transfer.md` Task 18, which is the task that
populates these keys.

`.env.example` is committed and carries **key names with empty values only**. It is the
list; `.env` is the values.

| Key | Read by | Active? |
|---|---|---|
| `SITE_URL` | `astro.config.mjs`, `scripts/perf_audit.py`, `scripts/health-sweep.sh` | no — `SITE_URL_PLACEHOLDER` until project 6 |
| `PUBLIC_FORMSPREE_ID` | `src/components/ContactForm.astro`, `scripts/form_contract_audit.py`, `tests/render/checks/form.ts` | yes |
| `GSC_SITE_URL` | `.claude/agents/bsuk-gsc-analytics.md` | no — project 6 |
| `GSC_CLIENT_ID` | nothing yet — project 6 wires the GSC/GA4 pulls | no — project 6 |
| `GSC_CLIENT_SECRET` | nothing yet — project 6 wires the GSC/GA4 pulls | no — project 6 |
| `GSC_REFRESH_TOKEN` | nothing yet — project 6 wires the GSC/GA4 pulls | no — project 6 |
| `GA4_PROPERTY_ID` | nothing yet — project 6 wires the GSC/GA4 pulls | no — project 6 |
| `GA4_CLIENT_ID` | nothing yet — project 6 wires the GSC/GA4 pulls | no — project 6 |
| `GA4_CLIENT_SECRET` | nothing yet — project 6 wires the GSC/GA4 pulls | no — project 6 |
| `GA4_REFRESH_TOKEN` | nothing yet — project 6 wires the GSC/GA4 pulls | no — project 6 |

A "Read by" cell names a file only when that file actually contains the key name today.
`scripts/indexnow_submit.py` (deferred to project 6, see data/port-manifest.json) will
read `SITE_URL` too; it is not listed in the table until it exists.
`tests/py/test_credentials_doc.py` holds this table to `.env.example` in both directions and
greps every named file, so neither side can drift.

Ten keys. Nine of them are populated by Task 18; `SITE_URL` waits for the domain project 6
registers.

## The retired MCP server

Task 19 retires the `bluestaffyuk` MCP server and moves what it held into `.env`. Three of
its keys are **not** carried over: `GITHUB_TOKEN`, `GITHUB_OWNER` and `GITHUB_REPO` — this
repo has no remote and must not get one — and `ANTHROPIC_API_KEY`, because the session
supplies it and a copy in `.env` is a second thing to leak.

## An empty key is a bug, not a default

A key that is present but empty must make the reader refuse rather than match nothing.
`scripts/form_contract_audit.py` and `tests/render/checks/form.ts` both do; anything new
that reads a key must too. `scripts/placeholder_check.py` counts what is still a stand-in
and, under `BSUK_RELEASE=1`, refuses the build.

## Handling

- Never paste a value into a command, a file, a commit message, a report or a chat.
- Never echo `.env` or any key's value to stdout, including while debugging.
- Read a value in the process that needs it, from the environment, and nowhere else.
