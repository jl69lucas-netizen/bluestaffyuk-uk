# BSUK Claude Code mods

Two mods for Claude Code. Each is a plugin of function hooks.

| Mod | What it draws | Open it |
|---|---|---|
| `bsuk-route` | The Route Map: all 21 page-run rows and the four STOPs for the page in progress, plus a status-line summary. It draws what `scripts/pipeline_status.py` prints, and that script proves every row from a file on disk. | `/bsuk-route` |
| `bsuk-agents` | Agent Cards: one card per background agent, running agents first. Each card shows the job, the agent type and model, the time it has run, its tool-call count, its current work type (Research / Reading / Writing / Testing / Committing, read from its last tool call) with the exact command or file, and a strip of its last 20 actions. A fleet card on top shows running/done counts and the fleet's effort by work type. It reads only what the engine reports. | `/bsuk-agents` |
| `bsuk-gauges` | Session gauges: context fill, the 1-hour prompt cache countdown, the 5-hour and 7-day plan limits, session cost, and Gemini calls today from `docs/reports/gemini-usage.jsonl`. It never reads the key. | `/bsuk-gauges` |

The breeder picked the Route Map on the answer board on 2026-10-03 (q01 a), and Agent Cards (design A) in chat the same day. The mockup is `docs/artifacts/claude-mods-preview.html`.

Load both in a new session from the repo root:

```bash
claude --plugin-dir tools/claude-mods/bsuk-route --plugin-dir tools/claude-mods/bsuk-agents --plugin-dir tools/claude-mods/bsuk-gauges
```

Check either one with `claude plugin validate tools/claude-mods/<mod>`.
