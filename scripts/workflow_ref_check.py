#!/usr/bin/env python3
"""workflow_ref_check.py — the workflow docs may only name what exists.

Reads docs/reference/WORKFLOW.md, docs/reference/quick-start.md and docs/reference/page-run.md
(the ordered per-page run) and resolves, on every line (prose, tables and fenced blocks alike):

  - every `bsuk-*` agent or skill name  -> .claude/agents/<name>.md or .claude/skills/<name>/
  - every `scripts/...` path            -> a file or directory on disk
  - every `npm run <name>`              -> a key in package.json "scripts"

A line may name one that does not exist only when it carries a parenthesised
"not ported" marker, e.g. `(not ported — deferred to project 6)` or
`(not ported — source repo only)`, or an `(arrives in Task N)` marker for a script a later
task of the running plan writes. The phrase outside parentheses is prose, not a marker. The
arrival marker expires on its own: tests/py/test_claude_md.py fails on a line that still
carries it once every backticked path on the line exists.
A `bsuk-*` name inside a path (`.claude/skills/bsuk-x/SKILL.md`, `data/bsuk-ontology.json`)
is a path, which tests/py/test_rules_index.py already guards, and is skipped here.

Usage:  python3 scripts/workflow_ref_check.py      # exit 1 on any unmarked missing name
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ("docs/reference/WORKFLOW.md", "docs/reference/quick-start.md",
        "docs/reference/page-run.md")
# The arrival marker, defined once: tests/py/test_claude_md.py imports it to expire a marker
# whose paths exist. A task is a number with an optional letter (`18b`) or a ruling (`R3`).
ARRIVES = re.compile(r"\(arrives in Task (?:\d+[a-z]?|R\d+)\)")
MARKER = re.compile(r"\([^()]*\bnot ported\b[^()]*\)|" + ARRIVES.pattern)
AGENT = re.compile(r"(?<![\w./-])@?(bsuk-[a-z0-9_-]*[a-z0-9])(?![\w-])(?!\.\w|/)")
SCRIPT = re.compile(r"(?<![\w./-])(scripts/[\w./-]+)")
NPM = re.compile(r"\bnpm run (?:(?:-s|--silent) )?([\w:-]+)")


def known(root):
    """(agent and skill names, npm script names) as they exist under `root`."""
    names = {p.stem for p in (root / ".claude/agents").glob("*.md")}
    names |= {p.name for p in (root / ".claude/skills").iterdir() if (p / "SKILL.md").is_file()}
    scripts = json.loads((root / "package.json").read_text(encoding="utf-8"))["scripts"]
    return names, set(scripts)


def check(root=ROOT):
    """([`<doc>:<line>  <ref>` for each unmarked missing reference], references examined)."""
    names, npm = known(root)
    problems, examined = [], 0
    for rel in DOCS:
        doc = root / rel
        for lineno, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            marked = bool(MARKER.search(line))
            found = [(n, n in names) for n in AGENT.findall(line)]
            found += [(p, (root / p).exists())
                      for p in (s.rstrip(".,;:") for s in SCRIPT.findall(line))]
            found += [("npm run " + n, n in npm) for n in NPM.findall(line)]
            examined += len(found)
            problems += [f"{doc.name}:{lineno}  {ref}" for ref, ok in found
                         if not ok and not marked]
    return problems, examined


def main(root=ROOT):
    problems, examined = check(root)
    for p in problems:
        print(f"  MISSING {p}")
    print(f"workflow-ref-check: examined {examined} references in {len(DOCS)} files; "
          f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
