#!/usr/bin/env python3
"""gemini_log.py — the Gemini API usage log: one JSON line per call, and no key ever written.

    python3 scripts/gemini_log.py summary [--path <log.jsonl>] [--today YYYY-MM-DD]

The breeder supplied a GEMINI_API_KEY for image work and will delete it when that work is
done; they asked for strong monitoring. Every generate call made by the bsuk-image-generation
skill is wrapped with `log_call` — on success and on every exception, recording the HTTP
status (402 when prepayment credits are depleted, 404 when a model is withdrawn).

Each line is {ts, model, slot, status, note}: an ISO UTC timestamp, the model id, the board
slot, the HTTP status and a short note. The log is committed (docs/reports/gemini-usage.jsonl)
because it holds no secret: the value of GEMINI_API_KEY from the environment is stripped from
every field, and any text shaped like a Google key (`AQ.…` or `AIza…`) is written
`[redacted]`.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "docs/reports/gemini-usage.jsonl"
KEY_PATTERN = re.compile(r"\bAQ\.\S+|\bAIza\S+")
REDACTED = "[redacted]"
USAGE = "usage: python3 scripts/gemini_log.py summary [--path <log.jsonl>] [--today YYYY-MM-DD]"


def _scrub(value) -> str:
    text = str(value)
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        text = text.replace(key, REDACTED)
        # A key logged without its "AQ." prefix is still the key.
        bare = key.split(".", 1)[1] if key.startswith("AQ.") else ""
        if len(bare) >= 8:
            text = text.replace(bare, REDACTED)
    return KEY_PATTERN.sub(REDACTED, text)


def log_call(model: str, slot: str, status, note: str = "", path=None, ts: str | None = None):
    """Append one line to the log. `status` is the HTTP status (200 on success)."""
    p = Path(path or LOG)
    p.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": ts or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "model": _scrub(model), "slot": _scrub(slot),
           "status": status if isinstance(status, int) else _scrub(status),
           "note": _scrub(note)}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def summary(path=None, today: str | None = None) -> dict:
    """Calls today, calls in total, counts by status (keys as strings) and lines that are not
    JSON (`malformed`). Every date is UTC: `ts` is written in UTC, and `today` (YYYY-MM-DD)
    defaults to the current UTC date, so a call late in a UK evening in summer counts on the
    next UTC day."""
    p = Path(path or LOG)
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows, malformed = [], 0
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if isinstance(row, dict):
                rows.append(row)
            else:
                malformed += 1
    by = Counter(str(r.get("status")) for r in rows)
    return {"today": sum(1 for r in rows if str(r.get("ts", "")).startswith(today)),
            "total": len(rows), "by_status": dict(by), "malformed": malformed}


def render(s: dict) -> str:
    statuses = ", ".join("%s: %d" % (k, v) for k, v in sorted(s["by_status"].items())) or "none"
    line = "Gemini usage (UTC): today %d, total %d; by status — %s" % (s["today"], s["total"],
                                                                       statuses)
    return line + ("; malformed lines %d" % s["malformed"] if s.get("malformed") else "")


def main(argv: list[str]) -> int:
    if not argv or argv[0] != "summary":
        print(USAGE, file=sys.stderr)
        return 2
    opts, rest = {}, argv[1:]
    while rest:
        flag = rest.pop(0)
        if flag in ("--path", "--today") and rest:
            opts[flag[2:]] = rest.pop(0)
        else:
            print(USAGE, file=sys.stderr)
            return 2
    print(render(summary(opts.get("path"), opts.get("today"))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
