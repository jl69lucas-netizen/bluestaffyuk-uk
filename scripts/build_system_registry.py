#!/usr/bin/env python3
"""Regenerate the generated block of docs/reference/system-registry.md from the repo.

The registry is a list of what exists: agents, skills, scripts, data files, gates and the
port manifest's deferred rows. A hand-typed list of those is a list that is wrong by the
next commit — the source repo's registry claimed 68 agents over 67 files, and no gate
noticed. So the same rule as `scripts/build_agent_registry.py`: the filesystem is the
source of truth and the document is derived.

Only the span between `<!-- generated:start -->` and `<!-- generated:end -->` is written.
Everything outside it is hand-written prose — the explanation of what the registry is for,
and why a count here can never be authoritative — and is preserved byte for byte.

Usage:  python3 scripts/build_system_registry.py           # write
        python3 scripts/build_system_registry.py --check   # exit 1 if stale
"""
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs/reference/system-registry.md"
START = "<!-- generated:start -->"
END = "<!-- generated:end -->"
TIER_ORDER = ("tier_max", "tier_high", "tier_medium", "tier_low")
SCRIPT_SUFFIXES = (".py", ".sh", ".mjs")

# The gate table is the one list the filesystem cannot derive: `ls scripts/` says which
# files exist, not which of them is a gate or what it proves. It is hand-maintained HERE,
# inside the generator, so it lives next to the lists it sits beside and a new gate is one
# edit rather than two. Every left-hand path is checked against disk on every run.
GATES = [
    ("scripts/marker_check.py", "no source-repo marker survives anywhere in the scanned roots"),
    ("scripts/placeholder_check.py", "counts launch placeholders; fails only under `BSUK_RELEASE=1`"),
    ("scripts/final_page_audit.py", "headings, six levels, the H5/H6 minimums"),
    ("scripts/schema_check.py", "structured data on every built page"),
    ("scripts/sitemap_check.py", "sitemap shards and what is excluded from them"),
    ("scripts/redirect_check.py", "`data/redirects.json` against the built routes"),
    ("scripts/dup_content_audit.py", "duplicate stems across siblings"),
    ("scripts/form_contract_audit.py", "the contact form's field contract"),
    ("scripts/evidence_audit.py", "term budgets and claim binding"),
    ("scripts/quality_report.py", "the rule ledger: enforced, judgment, untested"),
    ("scripts/build_agent_registry.py", "`data/agent-registry.json` matches `.claude/agents/`"),
    ("scripts/build_system_registry.py", "this document matches the repo"),
    ("scripts/port_from_cag.py", "applies `data/port-manifest.json`; never overwrites a rebase"),
]


def agent_description(root, name):
    text = (root / ".claude/agents" / (name + ".md")).read_text(encoding="utf-8")
    m = re.search(r"^description:\s*(.+)$", text, re.M)
    d = (m.group(1).strip().strip("\"'") if m else "").split(". ")[0].rstrip(".")
    d = d.replace("|", r"\|")
    if len(d) >= 140:
        d = d[:140].rstrip(", ")
        d = d[:d.rfind(" ")].rstrip(", ") + " …"
    return d


def render(root=ROOT):
    """The generated block's body, without the marker comments."""
    registry = json.loads((root / "data/agent-registry.json").read_text(encoding="utf-8"))
    agents = registry["agents"]
    by_tier = collections.OrderedDict((t, []) for t in TIER_ORDER)
    for name in sorted(agents):
        by_tier.setdefault(agents[name]["tier"], []).append(name)

    skills = sorted(p.parent.name for p in (root / ".claude/skills").glob("*/SKILL.md"))
    scripts = sorted(p.name for p in (root / "scripts").glob("*")
                     if p.is_file() and p.suffix in SCRIPT_SUFFIXES)
    data = sorted((root / "data").glob("*"))

    L = []
    L.append("## Agents — %d" % len(agents))
    L.append("")
    L.append("Every agent carries `model: inherit`; effort is the only per-agent cost lever, and")
    L.append("`data/agent-registry.json` is GENERATED from the agents' own frontmatter by")
    L.append("`scripts/build_agent_registry.py`. To change an agent's effort, edit its frontmatter")
    L.append("and regenerate — never the other way round.")
    L.append("")
    for tier, names in by_tier.items():
        if not names:
            continue
        L.append("### `%s` — %d" % (tier, len(names)))
        L.append("")
        L.append("| Agent | Does |")
        L.append("|---|---|")
        for n in names:
            L.append("| `.claude/agents/%s.md` | %s |" % (n, agent_description(root, n)))
        L.append("")

    L.append("## Skills — %d" % len(skills))
    L.append("")
    L.append("One SKILL.md per directory under `.claude/skills/`. The `bsuk-*` set is the ported")
    L.append("system; the rest are the generic writing, research and framework skills.")
    L.append("")
    L += ["- `.claude/skills/%s/SKILL.md`" % s for s in skills]
    L.append("")

    L.append("## Scripts — %d" % len(scripts))
    L.append("")
    L.append("Every `.py`, `.sh` and `.mjs` in `scripts/`. A script the source repo had and this")
    L.append("list does not was not ported; `data/port-manifest.json` records the decision.")
    L.append("")
    L += ["- `scripts/%s`" % s for s in scripts]
    L.append("")

    L.append("## Data files — %d" % len(data))
    L.append("")
    L += ["- `data/%s%s`" % (p.name, "/" if p.is_dir() else "") for p in data]
    L.append("")

    L.append("## Gates")
    L.append("")
    L.append("`npm run check:all` runs the mechanical gates. Each prints `examined N …; 0 problems`")
    L.append("and exits non-zero on a problem.")
    L.append("")
    L.append("| Gate | Proves |")
    L.append("|---|---|")
    for path, proves in GATES:
        if not (root / path).exists():
            raise ValueError("the gate table names %s, which does not exist" % path)
        L.append("| `%s` | %s |" % (path, proves))
    L.append("| `tests/py/` | the Python suite, via `npm run test:py` |")
    L.append("| `tests/render/` | the Playwright render harness |")
    L.append("")

    rows = json.loads((root / "data/port-manifest.json").read_text(encoding="utf-8"))
    deferred = [r for r in rows if r["mode"] == "deferred"]
    groups = collections.defaultdict(list)
    for r in deferred:
        m = re.search(r"project (\d)", r.get("notes", ""))
        groups[m.group(1) if m else None].append(r["dst"])

    L.append("## Deferred — recorded, not written")
    L.append("")
    L.append("`data/port-manifest.json` records every file that crossed and every file that")
    L.append("deliberately did not. %d rows are `deferred`." % len(deferred))
    L.append("")
    for key in sorted(k for k in groups if k is not None):
        L.append("- **project %s** — %d rows (deferred to project %s, see data/port-manifest.json)"
                 % (key, len(groups[key]), key))
    if None in groups:
        L.append("- **no project** — %d rows the spec rules out of the transfer entirely; they stay"
                 % len(groups[None]))
        L.append("  in the source repo (not ported — source repo only)")
    L.append("")
    L.append("Deferred paths are not listed here by name: a name is a path, and a path this repo")
    L.append("does not have is exactly what the forward-reference guard exists to catch. Read the")
    L.append("manifest for the list.")
    L.append("")
    L += guards_table()
    return "\n".join(L)


# Guard, what it scans, how a root is added, which pytest fails. Generated into the block so
# it cannot drift from the code: a guard whose row is wrong is a guard nobody will trust.
GUARDS = (
    ("`scripts/marker_check.py`",
     "every written manifest `dst` plus CLAUDE.md, rules/, docs/reference/, package.json, "
     "tests/render/, scripts/dup_content_audit.py",
     "add a non-`deferred` row to `data/port-manifest.json`, or a path to `FIXED_ROOTS`",
     "`tests/py/test_marker_check.py`"),
    ("`scripts/placeholder_check.py`",
     "`dist/` plus the union of its literal floor (.claude/skills, .claude/agents, "
     "docs/reference) with `marker_check.scan_roots()`",
     "inherited — anything the marker gate judges is scanned automatically",
     "`tests/py/test_placeholder_check.py`"),
    ("fact lint",
     "`.claude/agents` and `.claude/skills`: locked £ amounts, banned tokens, DEFRA only "
     "beside transport, no stand-in inside a heading or path segment, lifespan 12–14",
     "drop a file into either tree",
     "`tests/py/test_agent_facts.py`"),
    ("path guard + stale-marker",
     "every repo path cited in a `docs/reference` doc, and every `(arrives in Task N)` "
     "marker whose path now exists",
     "cite a path in a reference doc",
     "`tests/py/test_rules_index.py`, `tests/py/test_claude_md.py`"),
    ("table lint + frontmatter",
     "every skill's frontmatter and every markdown table in the skill tree",
     "add a skill directory under `.claude/skills`",
     "`tests/py/test_skills_frontmatter.py`"),
    ("harness vocabulary",
     "`tests/render/` check ids, families and the deferred-check register",
     "register a check in the harness",
     "`tests/render/meta.spec.ts` via `npm run test:render:meta`"),
    ("credentials doc + secret scan",
     "`docs/reference/credentials.md` key table; every `.env` value against all tracked "
     "files, the run log and `docs/artifacts/*.html`; credential SHAPES across "
     "`marker_check.scan_roots()` plus docs/reports, docs/artifacts, "
     "data/quality/scorecards, tests/py/fixtures",
     "inherited from the marker gate; add a key to `.env` and `.env.example`",
     "`tests/py/test_credentials_doc.py`, `tests/py/test_no_env_value_committed.py`, `tests/py/test_secret_shapes.py`"),
    ("agent + system registries",
     "`.claude/agents` frontmatter against `data/agent-registry.json`; this document "
     "against the repo",
     "add an agent, a skill, a script or a `data/` file",
     "`npm run agents`, `npm run registry` (both `--check`)"),
    ("render baseline",
     "the generated table in `docs/reports/render-baseline-project2.md` against the "
     "scorecards",
     "regenerate with `scripts/render_baseline.py --write`",
     "`npm run baseline`"),
    ("parity / redirects / schema / sitemaps",
     "the built `dist/` against the migration record, the redirect map, JSON-LD and the "
     "sitemap shards",
     "build a page — coverage follows `dist/`",
     "`npm run check:all`"),
)


def guards_table():
    L = ["## Mechanical guards — %d" % len(GUARDS), ""]
    L.append("Every rule in this repo that is actually enforced is enforced by one of these. A")
    L.append("guard that is not in this table is not a guard; a rule with no row here is a")
    L.append("convention. \"How a root is added\" is the column that matters when a later project")
    L.append("brings new files: most guards inherit their scope from the marker gate, so the")
    L.append("answer is usually \"add the manifest row and it is covered\".")
    L.append("")
    L.append("| Guard | What it scans | How a root is added | Which pytest fails |")
    L.append("|---|---|---|---|")
    for guard, scans, adds, fails in GUARDS:
        L.append("| %s | %s | %s | %s |" % (guard, scans, adds, fails))
    return L


def compose(root=ROOT):
    """The full document text this generator would write."""
    doc = (root / "docs/reference/system-registry.md")
    text = doc.read_text(encoding="utf-8") if doc.exists() else ""
    if START not in text or END not in text:
        raise ValueError("docs/reference/system-registry.md has no %s / %s markers" % (START, END))
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    return head + START + "\n\n" + render(root) + "\n\n" + END + tail


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        text = compose()
    except ValueError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    if "--check" in argv:
        if DOC.read_text(encoding="utf-8") != text:
            print("STALE — docs/reference/system-registry.md disagrees with the repo. Run: "
                  "python3 scripts/build_system_registry.py")
            return 1
        print("examined docs/reference/system-registry.md; 0 problems")
        return 0
    DOC.write_text(text, encoding="utf-8")
    print("wrote %s" % DOC.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
