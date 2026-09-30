#!/usr/bin/env python3
"""Regenerate data/agent-registry.json from the agents that actually exist.

CAG's registry was hand-maintained and drifted to 68 entries over 67 files — an entry for
an agent nobody could dispatch, and no gate that noticed. Here the directory is the source
of truth and the registry is derived, so the two cannot disagree.

Usage:  python3 scripts/build_agent_registry.py           # write
        python3 scripts/build_agent_registry.py --check   # exit 1 if stale
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENTS = ROOT / ".claude/agents"
OUT = ROOT / "data/agent-registry.json"
TIERS = {"max": "tier_max", "high": "tier_high", "medium": "tier_medium", "low": "tier_low"}


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError("%s has no YAML frontmatter" % path.name)
    # Scalar keys only. A block sequence (`tools:` written as a `-` list over several
    # lines) is not parsed, because nothing here reads `tools` — every agent writes it
    # inline. If that changes, this needs a real YAML parser rather than a wider regex.
    fm = dict(re.findall(r"^([a-z_]+):[ \t]*(.+)$", m.group(1), re.M))
    # `effort: "high"` and `effort: high` are the same declaration; a quoted value must not
    # become an unknown tier.
    fm = {k: v.strip().strip('"\'') for k, v in fm.items()}
    if "name" not in fm or "effort" not in fm:
        raise ValueError("%s frontmatter needs name and effort" % path.name)
    if fm["name"] != path.stem:
        raise ValueError("%s declares name: %s" % (path.name, fm["name"]))
    return fm["name"], fm["effort"].strip()


def build():
    agents = {}
    for p in sorted(AGENTS.glob("bsuk-*.md")):
        name, effort = parse(p)
        if effort not in TIERS:
            raise ValueError("%s: unknown effort %r" % (p.name, effort))
        agents[name] = {"tier": TIERS[effort]}
    return {
        "_meta": {
            "description": "BSUK agent tier registry, GENERATED from .claude/agents/bsuk-*.md "
                           "by scripts/build_agent_registry.py. Never hand-edit: edit the "
                           "agent's frontmatter and regenerate. All agents use model: inherit; "
                           "effort is the only per-agent cost lever.",
            "generated_by": "scripts/build_agent_registry.py",
            "tiers": {v: {"model": "inherit", "effort": k} for k, v in TIERS.items()},
        },
        "agents": agents,
    }


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        reg = build()
    except ValueError as e:
        # A malformed agent is a defect in the agent, not in this script: say which file and
        # what is wrong, and exit non-zero. A traceback here reads as a broken gate and
        # sends the reader to the wrong file.
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    text = json.dumps(reg, indent=2) + "\n"
    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("STALE — %d agents on disk, registry disagrees. Run: "
                  "python3 scripts/build_agent_registry.py" % len(reg["agents"]))
            return 1
        print("examined %d agents; 0 problems" % len(reg["agents"]))
        return 0
    OUT.write_text(text, encoding="utf-8")
    print("wrote %s — %d agents" % (OUT.relative_to(ROOT), len(reg["agents"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
