# BlueStaffyUK System Transfer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the C.A.Gs site operating system — the rules, the Page Board, the gate scripts, and the curated agents and skills that run them — from `~/Downloads/CAG` into `~/Downloads/BSUK`, re-based from an African Grey parrot breeder to a Glasgow Staffordshire Bull Terrier breeder, with a zero-tolerance marker gate proving the re-base complete; re-base the render harness's form contract and DUP whitelist onto BSUK's own built pages; and retire the `bluestaffyuk` MCP server into a gitignored `.env`.

**Architecture:** Manifest-driven port. `data/port-manifest.json` is the single record of every file that crosses from CAG to BSUK (`src`, `dst`, `mode`, `notes`). `scripts/port_from_cag.py` applies it — overwriting `copy`/`rename` rows on every run, never overwriting `rebase` rows, because the hand edits are the deliverable. `scripts/marker_check.py` proves the result: it scans every manifest `dst` plus `CLAUDE.md`, `rules/`, `docs/reference/`, `package.json` and `tests/render/` for twelve parrot markers with no allowlist, and is wired into `npm run check:all`. Gates keep Foundation's shape: `examined N …; 0 problems`, non-zero exit on problems.

**Tech Stack:** Python 3.9 (`python3`) with `beautifulsoup4`, `lxml`, `pytest`, and newly `jsonschema`; pytest in `tests/py/` via `npm run test:py`; Playwright 1.60 render harness at `tests/render/`; Astro 6.3.8 / Tailwind 4.3 producing `dist/`. Node is used only by the harness and the Astro build.

**Spec:** `docs/superpowers/specs/2026-09-16-system-transfer-design.md`. Read it first; §9 is the definition of done.

**Conventions for every task:**
- Repo root is `/Users/apple/Downloads/BSUK`. Run every command from there.
- Source repo is `/Users/apple/Downloads/CAG` (read-only; never modify it, never `git` in it).
- Python tests: `python3 -m pytest tests/py -q`. Gates: `npm run check:all`.
- Commit after every task with the trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Branch is `system-transfer` (cut from `foundation`). Never add a git remote. Never push.
- No credential value may appear in any committed file, report, Artifact, or on stdout.
- A parrot marker anywhere in a scanned root is a defect to fix, never an exception to record. The one structural exception is `data/port-manifest.json` itself, which necessarily carries `cag-` source paths.

---

## File structure

| Path | Responsibility | Task |
|---|---|---|
| `schemas/port-manifest.schema.json` | JSON Schema for the manifest: unique `dst`, four known modes | 1 |
| `data/port-manifest.json` | the record of every ported file: `src`, `dst`, `mode`, `notes` | 1, 3, 4, 6–9, 11–13 |
| `scripts/port_from_cag.py` | applies the manifest; overwrite `copy`/`rename`, never `rebase` | 1 |
| `tests/py/test_port_manifest.py` | schema rejection, never-overwrite, overwrite, missing-source exit | 1 |
| `scripts/marker_check.py` | zero-tolerance marker gate over manifest dsts + fixed roots | 2 |
| `tests/py/test_marker_check.py` | one fixture per marker, the manifest self-exception, exit codes | 2 |
| `package.json` | `check:markers`, `check:all` chain, `board:*`, `quality`, release-guarded scripts | 2, 17 |
| `schemas/board.schema.json`, `component-ledger.schema.json`, `ontology.schema.json` | ported schemas | 3, 4 |
| `.claude/commands/opsx/{propose,explore,apply,archive}.md` | openspec commands, copied | 3 |
| `.claude/skills/<name>/SKILL.md` | curated skills — generic copied (3), system re-based (12) | 3, 12 |
| `requirements.txt` | adds `jsonschema` | 4 |
| `scripts/pageboard.py` | board library; imports `HEADER_WHITELIST`/`HEAD_TERMS` from `dup_content_audit` | 4 |
| `scripts/board_gate.py`, `board_approve.py`, `build_page_board.py` | board gate, approval, Artifact builder | 4 |
| `tests/py/test_page_board.py` | ported board tests | 4 |
| `data/boards/index.json` | the homepage proving board | 5 |
| `docs/artifacts/boards/index.html` | the proving board's Artifact source | 5 |
| `scripts/final_page_audit.py`, `page_hardening_scan.py` | page gates, group A | 6 |
| `scripts/aeo_audit.py`, `evidence_audit.py`, `form_contract_audit.py` | page gates, group B | 7 |
| `scripts/perf_audit.py`, `quality_report.py`, `generate_page_dates.py`, `health-sweep.sh` | reporting gates, group C | 8 |
| `tests/py/test_{final_page_audit,page_hardening,aeo_audit,evidence_audit,form_contract_audit,perf_audit,quality_report}.py` | one pytest per ported gate | 6–8 |
| `rules/{headings,images,schema,links,copy,design,gates,deploy,puppies}.md`, `rules/README.md` | 10 re-based rule packs | 9 |
| `data/quality/rule-index.json` | ported rule ledger with `test`/`judgment`/`untested` tags | 9 |
| `data/quality/{rework-ledger,evidence-ledger}.json`, `data/component-ledger.json` | empty ledgers | 9 |
| `data/quality/evidence-budgets.json` | ported budgets | 9 |
| `CLAUDE.md` | rewritten from CAG's skeleton with BSUK facts; deploy inactive | 10 |
| `.claude/agents/bsuk-*.md` | ~25 curated agents, re-based in three batches | 11 |
| `data/agent-registry.json` | regenerated from the agents actually present | 11 |
| `scripts/build_agent_registry.py` | regenerator | 11 |
| `docs/reference/{system-registry,quick-start,WORKFLOW,seo-rules,session-log}.md` | re-based reference docs | 13 |
| `docs/reference/credentials.md` | which env key exists and what reads it; no values | 13 |
| `tests/render/checks/form.ts` | reads `PUBLIC_FORMSPREE_ID`; BSUK's field contract | 14 |
| `tests/render/fixtures/{known_good,known_broken}/form-inquiry-contract.html` | regenerated from the built contact page | 14 |
| `scripts/dup_content_audit.py` | whitelist re-measured against BSUK chrome | 15 |
| `tests/render/fixtures/dup_corpus/sibling-*.html` | three BSUK location siblings | 15 |
| `tests/render/fixtures/**` (remaining marker-carrying fixtures and check comments) | re-based to BSUK vocabulary | 14, 15 |
| `tests/render/lib/dupCorpus.ts` | floor assertion at the new whitelist count | 15 |
| `tests/render/targets.json` | `for-sale`/`puppy` page types; every family examines ≥1 page | 16 |
| `scripts/indexnow_submit.py` | release-guarded (`BSUK_RELEASE=1`) | 17 |
| `.env`, `.env.example`, `.gitignore` | the nine credentials; keys only in the example | 18 |
| `~/Library/Application Support/Claude/claude_desktop_config.json` | `bluestaffyuk` block removed, backup beside it | 19 |
| `docs/reports/system-transfer-gate-report.md` | close-out report, spec §9 checklist | 20 |
| `docs/artifacts/bsuk-system-transfer-gate-report.html` | the report's Artifact source | 20 |

---

### Task 1: Port manifest schema and `port_from_cag.py`

**Files:**
- Create: `schemas/port-manifest.schema.json`, `data/port-manifest.json` (first rows), `scripts/port_from_cag.py`, `tests/py/test_port_manifest.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add `jsonschema` to requirements and install**

Append to `requirements.txt` (keep the existing five lines, add one):
```
jsonschema==4.23.0
```
Run: `python3 -m pip install -r requirements.txt`

- [ ] **Step 2: Failing test — `tests/py/test_port_manifest.py`**

```python
import json
import pytest

from port_from_cag import apply_manifest, load_manifest, validate


def _row(src, dst, mode="copy", notes="n"):
    return {"src": src, "dst": dst, "mode": mode, "notes": notes}


def _src_tree(tmp_path, *names):
    cag = tmp_path / "cag"
    for n in names:
        p = cag / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("source %s\n" % n, encoding="utf-8")
    return cag


def test_validate_rejects_unknown_mode(tmp_path):
    with pytest.raises(ValueError, match="mode"):
        validate([_row("a.md", "b.md", mode="teleport")])


def test_validate_rejects_duplicate_dst(tmp_path):
    with pytest.raises(ValueError, match="duplicate dst"):
        validate([_row("a.md", "same.md"), _row("b.md", "same.md")])


def test_validate_rejects_absolute_or_escaping_paths():
    with pytest.raises(ValueError, match="relative"):
        validate([_row("/etc/passwd", "b.md")])
    with pytest.raises(ValueError, match="relative"):
        validate([_row("a.md", "../outside.md")])


def test_copy_overwrites_every_run(tmp_path):
    cag = _src_tree(tmp_path, "a.md")
    bsuk = tmp_path / "bsuk"
    rows = [_row("a.md", "x/a.md", mode="copy")]
    apply_manifest(rows, cag, bsuk)
    (bsuk / "x/a.md").write_text("hand edit\n", encoding="utf-8")
    stats = apply_manifest(rows, cag, bsuk)
    assert (bsuk / "x/a.md").read_text() == "source a.md\n"
    assert stats["applied"] == 1 and stats["skipped_existing"] == 0


def test_rename_overwrites_and_renames(tmp_path):
    cag = _src_tree(tmp_path, ".claude/agents/cag-faq-agent.md")
    bsuk = tmp_path / "bsuk"
    rows = [_row(".claude/agents/cag-faq-agent.md", ".claude/agents/bsuk-faq-agent.md", mode="rename")]
    apply_manifest(rows, cag, bsuk)
    assert (bsuk / ".claude/agents/bsuk-faq-agent.md").exists()
    stats = apply_manifest(rows, cag, bsuk)
    assert stats["applied"] == 1


def test_rebase_never_overwrites(tmp_path):
    """The hand edits ARE the deliverable. A second run that re-copied the parrot source
    would silently undo the whole re-base, and the marker gate would only notice afterwards."""
    cag = _src_tree(tmp_path, "rules/for-sale.md")
    bsuk = tmp_path / "bsuk"
    rows = [_row("rules/for-sale.md", "rules/puppies.md", mode="rebase")]
    first = apply_manifest(rows, cag, bsuk)
    assert first["applied"] == 1
    (bsuk / "rules/puppies.md").write_text("re-based by hand\n", encoding="utf-8")
    second = apply_manifest(rows, cag, bsuk)
    assert second["applied"] == 0 and second["skipped_existing"] == 1
    assert (bsuk / "rules/puppies.md").read_text() == "re-based by hand\n"


def test_deferred_writes_nothing(tmp_path):
    cag = _src_tree(tmp_path, ".claude/skills/cag-logo-generator/SKILL.md")
    bsuk = tmp_path / "bsuk"
    rows = [_row(".claude/skills/cag-logo-generator/SKILL.md",
                 ".claude/skills/bsuk-logo-generator/SKILL.md", mode="deferred")]
    stats = apply_manifest(rows, cag, bsuk)
    assert stats["deferred"] == 1 and not (bsuk / ".claude/skills/bsuk-logo-generator/SKILL.md").exists()


def test_missing_source_is_counted_not_raised(tmp_path):
    cag = _src_tree(tmp_path, "a.md")
    bsuk = tmp_path / "bsuk"
    stats = apply_manifest([_row("a.md", "a.md"), _row("gone.md", "gone.md")], cag, bsuk)
    assert stats["missing"] == 1 and stats["applied"] == 1


def test_deferred_source_may_be_absent(tmp_path):
    """A deferred row records a decision, not a file. Requiring its source to exist would
    make the manifest unable to record anything CAG later deletes."""
    stats = apply_manifest([_row("nope.md", "nope.md", mode="deferred")], tmp_path / "cag", tmp_path / "bsuk")
    assert stats["missing"] == 0 and stats["deferred"] == 1


def test_real_manifest_validates():
    rows = load_manifest()
    validate(rows)
    assert len(rows) > 0
```

- [ ] **Step 3: Run** → `ModuleNotFoundError: No module named 'port_from_cag'`.

- [ ] **Step 4: Write `schemas/port-manifest.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bluestaffyuk.local/schemas/port-manifest.schema.json",
  "title": "CAG → BSUK port manifest",
  "description": "Every file that crosses from ~/Downloads/CAG into ~/Downloads/BSUK, and how. This file is the record; scripts/port_from_cag.py applies it; scripts/marker_check.py proves the result. A file that is not in this manifest did not cross.",
  "type": "array",
  "minItems": 1,
  "items": {
    "type": "object",
    "additionalProperties": false,
    "required": ["src", "dst", "mode", "notes"],
    "properties": {
      "src": {
        "type": "string",
        "minLength": 1,
        "description": "Path relative to ~/Downloads/CAG. Never absolute, never containing '..'.",
        "pattern": "^(?!/)(?!.*(^|/)\\.\\.(/|$)).+$"
      },
      "dst": {
        "type": "string",
        "minLength": 1,
        "description": "Path relative to ~/Downloads/BSUK. Unique across the whole manifest.",
        "pattern": "^(?!/)(?!.*(^|/)\\.\\.(/|$)).+$"
      },
      "mode": {
        "enum": ["copy", "rename", "rebase", "deferred"],
        "description": "copy = byte-identical at the same relative path; rename = byte-identical at a new path; rebase = first copy then hand-edited, never overwritten again; deferred = recorded, not written."
      },
      "notes": {
        "type": "string",
        "minLength": 1,
        "description": "For rebase: what must change. For deferred: which project picks it up. For copy/rename: why it needs no edit."
      }
    }
  }
}
```

- [ ] **Step 5: Write `scripts/port_from_cag.py`**

```python
#!/usr/bin/env python3
"""Apply data/port-manifest.json: copy files from ~/Downloads/CAG into this repo.

The manifest is the record of the port, not a convenience. Four modes:

  copy      byte-identical, same relative path. Rewritten on every run.
  rename    byte-identical, new path (cag-x.md -> bsuk-x.md). Rewritten on every run.
  rebase    copied ONCE, then hand-edited. NEVER overwritten. The hand edits are the
            deliverable; a second run that re-copied the parrot source would undo the
            entire re-base silently, and scripts/marker_check.py would only find
            out afterwards. `skipped-existing` on a second run is the expected result.
  deferred  recorded, not written. The file exists in CAG and belongs to a later project;
            listing it keeps the manifest a complete account of the source tree. Its src
            is not required to exist, because the manifest must be able to record a
            decision about a file CAG later deletes.

Usage:
  python3 scripts/port_from_cag.py                 # apply every row
  python3 scripts/port_from_cag.py --dry-run       # report, write nothing
  python3 scripts/port_from_cag.py --only rules/   # rows whose dst starts with this prefix
  python3 scripts/port_from_cag.py --cag /path     # override the source root

Exits non-zero when any non-deferred row's src is missing, so a manifest that drifts
from CAG fails loudly instead of half-applying.
"""
import argparse
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAG = pathlib.Path("/Users/apple/Downloads/CAG")
MANIFEST = ROOT / "data/port-manifest.json"
SCHEMA = ROOT / "schemas/port-manifest.schema.json"
MODES = ("copy", "rename", "rebase", "deferred")


def load_manifest(path=MANIFEST):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def validate(rows, schema_path=SCHEMA):
    """Schema first, then the two rules a JSON Schema cannot express on its own."""
    import jsonschema

    schema = json.loads(pathlib.Path(schema_path).read_text(encoding="utf-8"))
    try:
        jsonschema.validate(rows, schema)
    except jsonschema.ValidationError as e:
        field = "/".join(str(p) for p in e.absolute_path) or "(root)"
        raise ValueError("manifest invalid at %s: %s" % (field, e.message))
    seen = {}
    for i, r in enumerate(rows):
        for key in ("src", "dst"):
            p = r[key]
            if p.startswith("/") or ".." in pathlib.PurePosixPath(p).parts:
                raise ValueError("row %d %s must be relative and inside the repo: %r" % (i, key, p))
        if r["dst"] in seen:
            raise ValueError("duplicate dst %r (rows %d and %d)" % (r["dst"], seen[r["dst"]], i))
        seen[r["dst"]] = i
        if r["mode"] not in MODES:
            raise ValueError("row %d unknown mode %r" % (i, r["mode"]))
    return rows


def apply_manifest(rows, cag=CAG, root=ROOT, dry_run=False):
    cag, root = pathlib.Path(cag), pathlib.Path(root)
    stats = {"applied": 0, "skipped_existing": 0, "deferred": 0, "missing": 0}
    missing = []
    for r in rows:
        if r["mode"] == "deferred":
            stats["deferred"] += 1
            continue
        src, dst = cag / r["src"], root / r["dst"]
        if not src.is_file():
            stats["missing"] += 1
            missing.append(r["src"])
            continue
        if r["mode"] == "rebase" and dst.exists():
            stats["skipped_existing"] += 1
            continue
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            if src.suffix == ".sh" or src.stat().st_mode & 0o111:
                dst.chmod(dst.stat().st_mode | 0o111)
        stats["applied"] += 1
    stats["missing_paths"] = missing
    return stats


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="report, write nothing")
    ap.add_argument("--only", default="", help="apply only rows whose dst starts with this prefix")
    ap.add_argument("--cag", default=str(CAG), help="source repo root (default %s)" % CAG)
    a = ap.parse_args(argv)
    rows = validate(load_manifest())
    if a.only:
        rows = [r for r in rows if r["dst"].startswith(a.only)]
    stats = apply_manifest(rows, cag=a.cag, dry_run=a.dry_run)
    for p in stats["missing_paths"]:
        print("MISSING SOURCE: %s" % p)
    print("examined %d rows; applied %d, skipped-existing %d, deferred %d, missing %d"
          % (len(rows), stats["applied"], stats["skipped_existing"], stats["deferred"], stats["missing"]))
    return 1 if stats["missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Write the first manifest rows — `data/port-manifest.json`**

The manifest is built up across Tasks 1, 3, 4, 6–9 and 11–13; each task appends its own
rows before it runs the port. Start it with the schema and board rows, verbatim:

```json
[
  { "src": "schemas/board.schema.json", "dst": "schemas/board.schema.json", "mode": "copy", "notes": "structure only; no site vocabulary" },
  { "src": "schemas/component-ledger.schema.json", "dst": "schemas/component-ledger.schema.json", "mode": "copy", "notes": "structure only; ledger stays empty until project 3" },
  { "src": "schemas/ontology.schema.json", "dst": "schemas/ontology.schema.json", "mode": "copy", "notes": "structure only" },
  { "src": ".claude/commands/opsx/propose.md", "dst": ".claude/commands/opsx/propose.md", "mode": "copy", "notes": "openspec command, site-agnostic" },
  { "src": ".claude/commands/opsx/explore.md", "dst": ".claude/commands/opsx/explore.md", "mode": "copy", "notes": "openspec command, site-agnostic" },
  { "src": ".claude/commands/opsx/apply.md", "dst": ".claude/commands/opsx/apply.md", "mode": "copy", "notes": "openspec command, site-agnostic" },
  { "src": ".claude/commands/opsx/archive.md", "dst": ".claude/commands/opsx/archive.md", "mode": "copy", "notes": "openspec command, site-agnostic" },
  { "src": ".claude/skills/anti-ai-writing/SKILL.md", "dst": ".claude/skills/anti-ai-writing/SKILL.md", "mode": "copy", "notes": "generic writing skill, no site vocabulary" },
  { "src": ".claude/skills/keyword-cluster/SKILL.md", "dst": ".claude/skills/keyword-cluster/SKILL.md", "mode": "copy", "notes": "generic" },
  { "src": ".claude/skills/internal-link-agent/SKILL.md", "dst": ".claude/skills/internal-link-agent/SKILL.md", "mode": "copy", "notes": "generic" },
  { "src": ".claude/skills/sitemap-agent/SKILL.md", "dst": ".claude/skills/sitemap-agent/SKILL.md", "mode": "copy", "notes": "generic" },
  { "src": ".claude/skills/section-auditor/SKILL.md", "dst": ".claude/skills/section-auditor/SKILL.md", "mode": "copy", "notes": "generic" },
  { "src": ".claude/skills/manual-auditor-check/SKILL.md", "dst": ".claude/skills/manual-auditor-check/SKILL.md", "mode": "copy", "notes": "generic" },
  { "src": ".claude/skills/research-recency/SKILL.md", "dst": ".claude/skills/research-recency/SKILL.md", "mode": "copy", "notes": "generic" },
  { "src": ".claude/skills/image-metadata/SKILL.md", "dst": ".claude/skills/image-metadata/SKILL.md", "mode": "copy", "notes": "generic" }
]
```

Each of those 15 rows is verbatim. Every remaining row in the manifest is generated by the
rule for its category — exact globs and destination patterns, applied in the task named:

| Category | Source glob (relative to CAG) | Destination pattern | Mode | Added in |
|---|---|---|---|---|
| Generic skills, copied unchanged | `.claude/skills/{framework-aida,framework-aio-geo,framework-bab,framework-ebp,framework-eeat,framework-eebp,framework-fab,framework-heading-hierarchy,framework-library,framework-pas,framework-pdb,framework-qab,image-prompt-generator,caption-writer,grill-me,session-closer,openspec-propose,openspec-explore,openspec-apply-change,openspec-archive-change}/SKILL.md` | same path | `copy` | 3 |
| Board scripts | `scripts/{pageboard,board_gate,board_approve,build_page_board}.py` | same path | `rebase` | 4 |
| Board test | `tests/test_page_board.py` | `tests/py/test_page_board.py` | `rebase` | 4 |
| Gate scripts A | `scripts/{final_page_audit,page_hardening_scan}.py` | same path | `rebase` | 6 |
| Gate scripts B | `scripts/{aeo_audit,evidence_audit,form_contract_audit}.py` | same path | `rebase` | 7 |
| Gate scripts C | `scripts/{perf_audit,quality_report,generate_page_dates,indexnow_submit}.py`, `scripts/health-sweep.sh` | same path | `rebase` | 8, 17 |
| Gate tests | `tests/test_<gate>.py` for each of the above | `tests/py/test_<gate>.py` | `rebase` | 6–8 |
| Rule packs | `rules/{headings,images,schema,links,copy,design,gates,deploy,README}.md` | same path | `rebase` | 9 |
| Rule pack, renamed | `rules/for-sale.md` | `rules/puppies.md` | `rebase` | 9 |
| Rule ledger | `data/quality/rule-index.json`, `data/quality/evidence-budgets.json` | same path | `rebase` | 9 |
| Project guide | `CLAUDE.md` | `CLAUDE.md` | `rebase` | 10 |
| Curated agents | `.claude/agents/cag-<n>.md` for each `<n>` in the §3 list | `.claude/agents/bsuk-<n>.md` | `rebase` | 11 |
| System skills | `.claude/skills/cag-<n>/SKILL.md` for each `<n>` in the §3 system list | `.claude/skills/bsuk-<n>/SKILL.md` | `rebase` | 12 |
| Renamed skill | `.claude/skills/cag-for-sale-page-builder/SKILL.md` | `.claude/skills/bsuk-puppy-page-builder/SKILL.md` | `rebase` | 12 |
| Audit-system skill | `.claude/skills/cags-comprehensive-page-audit-system/SKILL.md` | `.claude/skills/bsuk-comprehensive-page-audit-system/SKILL.md` | `rebase` | 12 |
| Reference docs | `docs/reference/{system-registry,quick-start,WORKFLOW,seo-rules,session-log}.md` | same path | `rebase` | 13 |
| Design-system skills (spec §3) | `.claude/skills/{cag-component-refresh,cag-component-variations,cag-multi-agent-design,cag-design-rebuild,cag-direction-d-theme,cag-visual-intelligence,cag-image-generation,cag-photo-ingest,cag-infographic,cag-logo-generator}/SKILL.md` | `.claude/skills/bsuk-<n>/SKILL.md` | `deferred` | 3 |
| Marketing / competitor agents (spec §10) | `.claude/agents/cag-{ab-test-agent,backlink-outreach-agent,branded-search-monitor-agent,case-study-agent,competitive-keyword-gap-agent,competitor-intel,conversion-tracker,directory-submission-agent,email-lead-nurture-agent,email-newsletter-agent,entity-incorporation-agent,external-link-agent,financial-strategist,funnel-analysis-agent,heatmap-analyst-agent,llm-keyword-intel,nap-citation-agent,performance-monitor-agent,review-collection-agent,scam-specialist,seasonal-content-agent,social-strategist,strategy-synthesizer,video-seo-agent,google-map-agent}.md` | `.claude/agents/bsuk-<n>.md` | `deferred` | 3 |
| Marketing skills (spec §10) | `.claude/skills/{cag-branded-hybrid-keywords,cag-branded-search-skill,cag-header-search,reddit-strategy,social-content,youtube-script}/SKILL.md` | `.claude/skills/<n>/SKILL.md` | `deferred` | 3 |

Rows the manifest never carries, by rule: everything spec §2 names under "Not ported, by
name" — the seven parrot-specific agents, the three bird-page skills, all of `CAG/data/`
except the two `data/quality/` files above, `CAG/src/`, `CAG/site/`, `CAG/sessions/`,
`CAG/skills/` (the flat mirror the single tree replaces), `CAG/docs/` beyond the five
reference docs, the one-off `add_*`/`patch_*`/`migrate_*`/`slim_golden_rule`/
`apply_model_tiers`/`scaffold_amie_from_roys`/`process_amie_images` scripts and
`scripts/oneoff/`, the canvas and thumbnail scripts, and `CAG/.google-key`. Out of scope
means absent from the record, not `deferred` in it — `deferred` means "a later BSUK project
will port this".

- [ ] **Step 7: Run the tests and the port**

```bash
python3 -m pytest tests/py/test_port_manifest.py -q && python3 scripts/port_from_cag.py
```
Expected: `10 passed`, then `examined 15 rows; applied 15, skipped-existing 0, deferred 0, missing 0`.

Then prove the rebase rule by running it a second time (no rebase rows yet, so this run
only confirms `copy` is idempotent):
```bash
python3 scripts/port_from_cag.py
```
Expected: the same line, `applied 15`.

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "port: manifest schema, port_from_cag.py, first 15 rows

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: The parrot marker gate

The gate that makes every later re-base task checkable. Written before the re-basing starts,
so each task can end by proving itself.

**Files:**
- Create: `scripts/marker_check.py`, `tests/py/test_marker_check.py`
- Modify: `package.json`

- [ ] **Step 1: Failing test — `tests/py/test_marker_check.py`**

```python
import json

import pytest

from marker_check import MARKERS, hits_in, main, scan_roots


def _repo(tmp_path, manifest_rows=(), files=()):
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data/port-manifest.json").write_text(json.dumps(list(manifest_rows)), encoding="utf-8")
    for rel, text in files:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def test_marker_list_is_exactly_the_spec_list():
    assert MARKERS == (
        "parrot", "african grey", "african-grey", "timneh", "congo", "clutch",
        "c.a.gs", "cags", "congoafricangreys", "agcare", "xrejpnvn", "cag-",
    )


@pytest.mark.parametrize("marker,line", [
    ("parrot", "The parrot is weaned."),
    ("african grey", "An African Grey needs space."),
    ("african-grey", "See /african-grey-care/."),
    ("timneh", "Timneh greys run smaller."),
    ("congo", "Congo range is wide."),
    ("clutch", "The clutch was candled."),
    ("c.a.gs", "Here at C.A.Gs we answer."),
    ("cags", "cags-comprehensive-page-audit-system"),
    ("congoafricangreys", "https://congoafricangreys.com/"),
    ("agcare", "google-agcare-snapshot"),
    ("xrejpnvn", "https://formspree.io/f/xrejpnvn"),
    ("cag-", "run cag-hub-builder first"),
])
def test_every_marker_fires(tmp_path, marker, line):
    repo = _repo(tmp_path, files=[("CLAUDE.md", line + "\n")])
    assert hits_in(repo / "CLAUDE.md") == [(1, marker, line)]


def test_matching_is_case_insensitive(tmp_path):
    repo = _repo(tmp_path, files=[("CLAUDE.md", "AFRICAN GREY PARROT\n")])
    found = {m for _, m, _ in hits_in(repo / "CLAUDE.md")}
    assert "african grey" in found and "parrot" in found


def test_clean_file_has_no_hits(tmp_path):
    repo = _repo(tmp_path, files=[("CLAUDE.md", "Blue Staffy puppies from a Glasgow kennel.\n")])
    assert hits_in(repo / "CLAUDE.md") == []


def test_manifest_itself_is_never_scanned(tmp_path):
    """Structural, not an allowlist: every manifest src path begins `cag-` or names CAG's
    tree, so scanning the record of the port would make a complete record unrepresentable."""
    rows = [{"src": ".claude/agents/cag-hub-builder.md", "dst": ".claude/agents/bsuk-hub-builder.md",
             "mode": "rebase", "notes": "bird -> puppy"}]
    repo = _repo(tmp_path, rows, files=[(".claude/agents/bsuk-hub-builder.md", "Blue Staffy hubs.\n")])
    roots = scan_roots(repo)
    assert (repo / "data/port-manifest.json") not in roots
    assert main(repo) == 0


def test_a_dirty_manifest_dst_fails(tmp_path):
    rows = [{"src": ".claude/agents/cag-hub-builder.md", "dst": ".claude/agents/bsuk-hub-builder.md",
             "mode": "rebase", "notes": "n"}]
    repo = _repo(tmp_path, rows, files=[(".claude/agents/bsuk-hub-builder.md", "Our African Grey hubs.\n")])
    assert main(repo) == 1


def test_deferred_rows_are_not_scanned(tmp_path):
    """A deferred row writes no dst; scanning a path that does not exist would be a crash,
    and scanning one that happens to exist for another reason would be a false attribution."""
    rows = [{"src": ".claude/skills/cag-logo-generator/SKILL.md",
             "dst": ".claude/skills/bsuk-logo-generator/SKILL.md", "mode": "deferred", "notes": "project 3"}]
    repo = _repo(tmp_path, rows)
    assert main(repo) == 0


def test_fixed_roots_are_scanned_even_when_not_in_the_manifest(tmp_path):
    repo = _repo(tmp_path, files=[("rules/puppies.md", "Never imply a wild-caught parrot.\n")])
    assert main(repo) == 1


def test_binary_and_non_text_files_are_skipped(tmp_path):
    repo = _repo(tmp_path, files=[("CLAUDE.md", "clean\n")])
    (repo / "tests/render/fixtures/assets").mkdir(parents=True)
    (repo / "tests/render/fixtures/assets/x.png").write_bytes(b"\x89PNG\r\n\x1a\ncongo")
    assert main(repo) == 0


def test_the_real_repo_is_clean():
    """The gate this project exists to satisfy. Red until Task 16."""
    assert main() == 0
```

- [ ] **Step 2: Run** → `ModuleNotFoundError: No module named 'marker_check'`.

- [ ] **Step 3: Write `scripts/marker_check.py`** — see the module below.

```python
#!/usr/bin/env python3
"""Gate: no C.A.Gs parrot vocabulary survives anywhere the port touched.

The port copies a parrot breeder's operating system into a dog breeder's repo. Every ported
file is either rewritten by hand or judged not to need it, and the only honest proof that
the judgement was right is a scan that cannot be argued with.

So: twelve markers, case-insensitive, NO ALLOWLIST. A legitimate-looking hit is a design
error to fix, not an exception to record — the moment this gate grows an allowlist it stops
being evidence and becomes a list of the places nobody re-based.

Scanned: every `dst` the manifest names that was actually written (deferred rows write
nothing), plus CLAUDE.md, rules/, docs/reference/, package.json, tests/render/ and
scripts/dup_content_audit.py — the last because its whitelist is re-measured in Task 15 and
nothing else would catch a parrot stem left in it.

ONE path is excluded, and the exclusion is structural rather than an allowlist:
`data/port-manifest.json` itself. Every `src` in it is a CAG path, most beginning `cag-`;
a manifest that could pass this gate would be a manifest that failed to record the port.

Output shape matches the Foundation gates: `examined N files; 0 problems`.

Usage:  python3 scripts/marker_check.py   |   npm run check:markers
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

MARKERS = (
    "parrot", "african grey", "african-grey", "timneh", "congo", "clutch",
    "c.a.gs", "cags", "congoafricangreys", "agcare", "xrejpnvn", "cag-",
)

FIXED_ROOTS = (
    "CLAUDE.md", "rules", "docs/reference", "package.json", "tests/render",
    "scripts/dup_content_audit.py",
)

# The record of the port cannot describe the port without naming CAG. Structural, not an
# allowlist: exactly one path, and it is the only file in the repo whose CONTENT IS the list
# of parrot-named sources.
EXCLUDED = ("data/port-manifest.json",)

TEXT_SUFFIXES = {
    ".md", ".json", ".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".html", ".css",
    ".sh", ".txt", ".yml", ".yaml", ".xml", ".astro",
}


def hits_in(path):
    """[(line_number, marker, line_text)] for every marker occurrence in a text file."""
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for m in MARKERS:
            if m in low:
                out.append((n, m, line.strip()))
    return out


def _walk(p):
    if p.is_file():
        return [p] if p.suffix.lower() in TEXT_SUFFIXES else []
    return sorted(f for f in p.rglob("*")
                  if f.is_file() and f.suffix.lower() in TEXT_SUFFIXES
                  and "__pycache__" not in f.parts and "node_modules" not in f.parts)


def scan_roots(root=ROOT):
    """Every file this gate judges: written manifest dsts + the fixed roots, deduped."""
    root = pathlib.Path(root)
    excluded = {(root / e).resolve() for e in EXCLUDED}
    files = []
    manifest = root / "data/port-manifest.json"
    if manifest.is_file():
        for r in json.loads(manifest.read_text(encoding="utf-8")):
            if r["mode"] == "deferred":
                continue
            files += _walk(root / r["dst"])
    for rel in FIXED_ROOTS:
        p = root / rel
        if p.exists():
            files += _walk(p)
    seen, out = set(), []
    for f in files:
        rp = f.resolve()
        if rp in excluded or rp in seen:
            continue
        seen.add(rp)
        out.append(f)
    return out


def main(root=ROOT):
    root = pathlib.Path(root)
    files = scan_roots(root)
    problems = 0
    for f in files:
        for n, marker, line in hits_in(f):
            problems += 1
            if problems <= 60:
                print("  %s:%d  [%s]  %s" % (f.relative_to(root), n, marker, line[:140]))
    if problems > 60:
        print("  … and %d more" % (problems - 60))
    print("examined %d files; %d problems" % (len(files), problems))
    if problems:
        print("FAIL — a parrot marker is a re-base that did not happen. There is no allowlist.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Wire it into `check:all`**

In `package.json` `"scripts"`, add the marker script and put it at the end of the chain (so a
broken build still reports parity first):
```json
    "check:markers": "python3 scripts/marker_check.py",
    "check:all": "npm run check:parity && npm run check:redirects && npm run check:schema && npm run check:sitemaps && npm run check:placeholders && npm run check:markers",
```

- [ ] **Step 5: Run**

```bash
python3 -m pytest tests/py/test_marker_check.py -q
npm run check:markers | tail -3
```
Expected: every test passes except `test_the_real_repo_is_clean`, which FAILS today —
`tests/render/` carries CAG's fixtures and check comments, and `scripts/dup_content_audit.py`
carries CAG's whitelist. That failure is the work list for Tasks 14–16. The gate prints
roughly `examined 70 files; <several hundred> problems`; record the exact number in the
commit message, it is the baseline Task 16 drives to zero.

- [ ] **Step 6: Mark the known-red test**

Add `@pytest.mark.xfail(reason="tests/render/ and dup_content_audit.py are re-based in Tasks 14-16", strict=True)`
above `test_the_real_repo_is_clean`, so the suite is green and the xfail turns into a hard
failure the moment the repo goes clean — at which point Task 16 removes the marker.
`strict=True` is the point: a non-strict xfail would stay quiet forever and this gate would
never be proven to have flipped.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "gate: marker_check.py, wired into check:all (baseline non-zero until task 16)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Schemas, opsx commands and the generic skills

The `copy` rows: files that cross byte-identical because they carry no site vocabulary at
all. Doing them first proves the port script on the easy case before any hand editing.

**Files:**
- Modify: `data/port-manifest.json`
- Create (by the port script): `schemas/*.json`, `.claude/commands/opsx/*.md`, `.claude/skills/<generic>/SKILL.md`

- [ ] **Step 1: Append the remaining generic-skill `copy` rows**

Append 20 rows to `data/port-manifest.json`, one per name in this list, each of the form
`{ "src": ".claude/skills/<n>/SKILL.md", "dst": ".claude/skills/<n>/SKILL.md", "mode": "copy", "notes": "generic" }`:

`framework-aida`, `framework-aio-geo`, `framework-bab`, `framework-ebp`, `framework-eeat`,
`framework-eebp`, `framework-fab`, `framework-heading-hierarchy`, `framework-library`,
`framework-pas`, `framework-pdb`, `framework-qab`, `image-prompt-generator`,
`caption-writer`, `grill-me`, `session-closer`, `openspec-propose`, `openspec-explore`,
`openspec-apply-change`, `openspec-archive-change`.

That is 20 rows; with the 7 generic skills already in Task 1's block the generic-skill set
is 27, and spec §3's "14 `framework-*` skills" is satisfied by the 12 `framework-*`
directories CAG actually holds plus `framework-agent` and `framework-heading-hierarchy`
(see the deviation note at the end of this plan).

- [ ] **Step 2: Append the `deferred` rows**

Append one row per entry in the three `deferred` categories in the Task 1 table (10
design-system skills, 25 marketing/competitor agents, 6 marketing skills = 41 rows), each
of the form
`{ "src": "<glob-expanded src>", "dst": "<dst pattern>", "mode": "deferred", "notes": "<project that picks it up>" }`.
Notes text by category: design-system skills → `"project 3 brings the design system"`;
marketing and competitor agents → `"spec §10 out of scope; project 6 at the earliest"`;
marketing skills → `"spec §10 out of scope"`.

- [ ] **Step 3: Run the port**

```bash
python3 scripts/port_from_cag.py
```
Expected: `examined 76 rows; applied 35, skipped-existing 0, deferred 41, missing 0`.

- [ ] **Step 4: Prove the copies are clean and byte-identical**

```bash
python3 - <<'PY'
import json, pathlib, filecmp
CAG = pathlib.Path("/Users/apple/Downloads/CAG"); ROOT = pathlib.Path(".")
rows = json.loads(pathlib.Path("data/port-manifest.json").read_text())
n = 0
for r in rows:
    if r["mode"] in ("copy", "rename"):
        assert filecmp.cmp(CAG / r["src"], ROOT / r["dst"], shallow=False), r["dst"]
        n += 1
print("examined %d copied files; 0 differences" % n)
PY
npm run check:markers | tail -3
```
Expected: `examined 35 copied files; 0 differences`, and the marker count unchanged from
Task 2's baseline. If any of the 35 raises a marker hit, it was misclassified as `copy`:
change its mode to `rebase` in the manifest, delete the written file, and re-run — a copy
row that needs editing is a wrong row, not a gate to argue with.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "port: schemas, opsx commands, 27 generic skills (copy rows); 41 deferred rows recorded

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: The Page Board system

CAG's board library is 897 lines and almost entirely domain-neutral. Four things carry
parrot DNA and three CAG paths must move; everything else ports as-is.

**Files:**
- Modify: `data/port-manifest.json`, `requirements.txt` (already has `jsonschema` from Task 1)
- Create (ported then re-based): `scripts/pageboard.py`, `scripts/board_gate.py`, `scripts/board_approve.py`, `scripts/build_page_board.py`, `tests/py/test_page_board.py`
- Create by hand: `data/bsuk-ontology.json`, `data/component-ledger.json`

- [ ] **Step 1: Append the board rows**

```json
  { "src": "scripts/pageboard.py", "dst": "scripts/pageboard.py", "mode": "rebase", "notes": "SPECIES regex -> coat colours; ONTOLOGY/LEDGER paths; board_path -> data/boards/<slug>.json; inline file_token/unfile_token (board_canvas is not ported)" },
  { "src": "scripts/board_gate.py", "dst": "scripts/board_gate.py", "mode": "rebase", "notes": "no CAG literals; re-based only for the board_path change" },
  { "src": "scripts/board_approve.py", "dst": "scripts/board_approve.py", "mode": "rebase", "notes": "drop the board_canvas import and the --canvas-dir write-back; approvals arrive from the Artifact db" },
  { "src": "scripts/build_page_board.py", "dst": "scripts/build_page_board.py", "mode": "rebase", "notes": "masthead literal; drop the thumbs block (board_thumbs.mjs is not ported)" },
  { "src": "schemas/board.schema.json", "dst": "schemas/board.schema.json", "mode": "rebase", "notes": "already copied in task 3 as copy; change that row to rebase — page_type enum and offer_model need BSUK values" },
  { "src": "tests/test_page_board.py", "dst": "tests/py/test_page_board.py", "mode": "rebase", "notes": "183 tests; port the schema/hash/ledger/gate/render core, drop the tests bound to CAG's real data files" }
```

`schemas/board.schema.json` is already in the manifest as `copy` from Task 1. Change that
row's `mode` to `"rebase"` and delete the file the Task 3 run wrote, so the port script
re-seeds it and then leaves the hand edits alone:
```bash
rm schemas/board.schema.json
```

- [ ] **Step 2: Run the port to seed the five files**

```bash
python3 scripts/port_from_cag.py --only scripts/ && python3 scripts/port_from_cag.py
```
Expected final line: `examined 82 rows; applied 40, skipped-existing 0, deferred 41, missing 0`.

- [ ] **Step 3: Re-base `schemas/board.schema.json`**

Three edits, everything else byte-identical to CAG's 188 lines:

1. `meta.page_type` enum — replace
   `["hub", "for-sale", "location", "comparison", "blog", "interior", "home"]` with
   `["home", "hub", "location", "puppy", "blog", "about", "contact", "comparison", "interior", "for-sale"]`
   (spec §7's eight page types plus `interior` and `for-sale`, which `targets.json` already uses).
2. `brief.schema.offer_model` enum — replace
   `["product-offer-per-bird", "aggregate-offer", "none"]` with
   `["product-offer-per-puppy", "aggregate-offer", "none"]`.
3. `title` — replace `"CAG Page Board record"` with `"BSUK Page Board record"`.

Apply the same `title` edit to `schemas/component-ledger.schema.json`
(`"CAG component ledger"` → `"BSUK component ledger"`) and `schemas/ontology.schema.json`
(`"CAG ontology"` → `"BSUK ontology"`), and change both of their manifest rows from `copy`
to `rebase` for the same reason.

- [ ] **Step 4: Re-base `scripts/pageboard.py`**

Five edits, by line landmark rather than line number (the numbers shift as you edit):

1. The ontology path. Replace
   `ONTOLOGY = ROOT / "data" / "cag-ontology.json"` with
   `ONTOLOGY = ROOT / "data" / "bsuk-ontology.json"`.
2. The board path. Replace the body of `board_path()` —
   `return ROOT / "data" / "pages" / slug / "board.json"` — with
   `return ROOT / "data" / "boards" / (slug.replace("/", "--") + ".json")`.
   Spec §2 puts boards at `data/boards/<slug>.json`; the slug replacement is needed because
   BSUK has nested slugs (`available-puppies/roman`) and CAG did not carry one into a
   filename. Do the same in `board_approve.py`'s inbox path:
   `ROOT / "data" / "boards" / "inbox" / (slug.replace("/", "--") + ".json")`.
3. The species regex. Replace
   ```python
   SPECIES = re.compile(r"\b(congo|timneh|macaw|cockatoo|amazon(?: parrot)?|eclectus|african greys?|greys?)\b")
   ```
   with the BSUK equivalent — the tokens a heading template legitimately swaps on this site
   are coat colour and sex, not species:
   ```python
   # Tokens a heading template swaps between otherwise-identical siblings, so that
   # "Blue Staffy Puppies in Leeds" and "Blue Staffy Puppies in Hull" are caught as a
   # template-for-template collision, not just as exact matches. On CAG this was the
   # species list; here it is coat colour and sex, which are the only words that vary
   # across the puppy and location clusters.
   COAT = re.compile(r"\b(blue|black|brindle|red|fawn|white|lilac)\b")
   SEX = re.compile(r"\b(male|female|dog|bitch)\b")
   SPECIES = re.compile("|".join((COAT.pattern, SEX.pattern)))
   ```
   Keep the name `SPECIES` so no call site changes; the comment explains why the name stayed.
4. `LINK_FLOOR_TYPES = {"for-sale", "hub"}` — leave as-is. BSUK's `targets.json` still uses
   `for-sale` for the three buy pages, so the floor applies to the same cluster.
5. Inline the two token helpers. `board_approve.py` imports `file_token` and
   `build_page_board.py` imports `unfile_token` from `board_canvas.py`, which spec §2 does
   not port. Add both to the bottom of `pageboard.py` and change the two imports to
   `from pageboard import file_token` / `unfile_token`:
   ```python
   # Inlined from CAG's board_canvas.py, which is not ported (spec §2: canvas and thumbnail
   # scripts are out of scope). Only these two functions were used outside that module: a
   # candidate id may carry a '#' delta, which is not legal in a filename, so the artboard
   # and thumbnail filenames spell it '_' and these two convert between the spellings.
   def file_token(candidate: str) -> str:
       """Candidate id -> the spelling used inside an artboard or thumbnail filename."""
       return candidate.replace("#", "_")

   def unfile_token(token: str) -> str:
       """The filename spelling -> the candidate id. Inverse of file_token()."""
       return token.replace("_", "#")
   ```

- [ ] **Step 5: Re-base `board_approve.py` and `build_page_board.py`**

`board_approve.py`:
- Replace `from board_canvas import file_token` with `from pageboard import file_token`.
- Replace the default canvas dir `PB.ROOT / "docs" / "design" / f"board-{slug}"` with
  `PB.ROOT / "docs" / "design" / ("board-" + slug.replace("/", "--"))`.
- Update the inbox path as in Step 4.2, and the error message's path with it.

`build_page_board.py`:
- Replace the masthead literal
  `<p class="eyebrow">CongoAfricanGreys.com · Page Board</p>` with
  `<p class="eyebrow">BlueStaffyUK · Page Board</p>`.
- Replace `from board_canvas import unfile_token` with `from pageboard import unfile_token`.
- Delete the thumbs block (the `tdir = OUT / slug / "thumbs"` glob and the
  `warning: thumbs/... — skipped` print). `board_thumbs.mjs` is not ported, so the glob
  would always be empty and the Artifact would advertise a thumbnail capability it has not
  got. Change the final print to
  `print("wrote %s — %d sections, %d live pages checked" % (out.relative_to(PB.ROOT), n_sections, n_live))`.
- Replace `OUT / f"{slug}.html"` with `OUT / (slug.replace("/", "--") + ".html")`.

- [ ] **Step 6: Write the two data files the library reads**

`data/bsuk-ontology.json` — the minimum that validates against `ontology.schema.json`,
seeded with the facts Foundation locked:
```json
{
  "entities": [
    { "id": "ont:staffordshire-bull-terrier", "name": "Staffordshire Bull Terrier", "aliases": ["Staffy", "Staffie", "Stafford", "SBT"], "class": "Organism", "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "uk-staffordshire-bull-terrier-guide" },
    { "id": "ont:blue-coat", "name": "Blue coat", "aliases": ["blue staffy", "blue Staffordshire Bull Terrier"], "class": "Organism", "authorization": "ASSERTED", "source": "data/puppies.json", "owner_page": "index" },
    { "id": "ont:lisa-bright", "name": "Lisa Bright", "aliases": ["the breeder"], "class": "People", "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "blue-staffy-uk-breeders" },
    { "id": "ont:glasgow", "name": "Glasgow", "aliases": ["G22", "Coltmuir Street"], "class": "Place", "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "uk-locations/staffy-puppies-for-sale-glasgow" },
    { "id": "ont:refundable-deposit", "name": "£500 refundable deposit", "aliases": ["deposit"], "class": "Commerce", "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "uk-blue-staffy-puppy-buying-guide" },
    { "id": "ont:defra-approved-transport", "name": "DEFRA-approved pet transport", "aliases": ["home delivery", "UK delivery"], "class": "Logistics", "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "index" },
    { "id": "ont:health-guarantee", "name": "Health guarantee", "aliases": [], "class": "Health", "authorization": "PROPOSED", "source": null, "owner_page": null }
  ]
}
```
`ont:health-guarantee` is `PROPOSED`, not `ASSERTED`, because `data/settings.json` carries
`"guarantee_days": null` — Foundation recorded that the guarantee length is unconfirmed, and
an ontology that asserted it would let a page claim a number nobody has given.

`data/component-ledger.json` — empty until project 3, but schema-valid:
```json
{ "refresh_pools": [], "pools": {}, "pages": {} }
```

- [ ] **Step 7: Port and cut `tests/py/test_page_board.py`**

CAG's file is 2432 lines / 183 tests. Port the tests whose subject is the library, and drop
the tests whose subject is CAG's own data. Concretely:

**Keep** (rewriting the `MIN_BOARD` fixture to BSUK values, below): every test under
*Schema validation*, *Hashing / approval identity*, *Ledger / component pools* except the
four named `..._real_ledger_...`, *Headings & duplicate pre-check*, *Gate behaviour* except
`test_gate_against_the_real_ledger_treats_a_refresh_id_as_unspent` and
`test_gate_against_the_real_dist_whitelists_faq_but_flags_current_pricing`, *Approval
application* in full, and *Sections / keywords / CTA / tool / schema* in full.

**Drop**, with a comment block at the top of the file recording why: the four
`..._real_ledger_...` tests and the two `..._real_dist_...` tests (they assert against CAG's
104-page `dist/` and its twelve-page ledger, neither of which exists here); every test in
the *canvas* group (`test_canvas_*`, `test_board_maps_a_thumb_*`, the canvas index/manifest
group) because `board_canvas.py` and `board_thumbs.mjs` are not ported; the `perf` block
(`test_perf_*`, 9 tests) because `perf_audit.py` arrives in Task 8 and its records do not
exist until a page is measured — re-add them there; and `test_ontology_file_validates_and_has_the_blocked_family`
plus `test_every_asserted_source_resolves_to_a_real_heading_or_data_key`, which assert
against CAG's ontology contents. Replace the last two with BSUK equivalents:

```python
def test_ontology_file_validates_and_marks_the_unconfirmed_guarantee_proposed():
    """data/settings.json has guarantee_days: null (Foundation, unconfirmed). An ontology
    that ASSERTED a guarantee would let a page publish a number nobody has given."""
    ont = PB.load_ontology()
    by_id = {e["id"]: e for e in ont["entities"]}
    assert by_id["ont:health-guarantee"]["authorization"] == "PROPOSED"
    assert by_id["ont:health-guarantee"]["source"] is None


def test_every_asserted_entity_names_a_source_that_exists():
    for e in PB.load_ontology()["entities"]:
        if e["authorization"] == "ASSERTED":
            assert e["source"], e["id"]
            assert (PB.ROOT / e["source"]).exists(), (e["id"], e["source"])
```

The `MIN_BOARD` fixture is rewritten wholesale to BSUK: `primary_keyword`
`"blue staffy puppies for sale uk"`; titles such as
`"Blue Staffy Puppies for Sale UK | Glasgow Breeder | BlueStaffyUK"`; entity
`"ont:staffordshire-bull-terrier"`; headings `"Our Blue Staffy Puppies"` and
`"Kennel Note: Read the Card"`; `h6_prefixes` `["Kennel Note:", "From the Book:", "Ask Us:"]`;
internal href `/uk-locations/staffy-puppies-for-sale-glasgow/`; external href
`https://www.gov.uk/guidance/dog-breeding-licence` (verify it returns 200 before writing it
— `rules/links.md`'s external-library rule applies to fixtures too).

The `live_dist` session fixture keeps its shape, with the skip reason rewritten:
`pytest.skip("dist/ is not built — run npm run build")`.

- [ ] **Step 8: Run**

```bash
python3 -m pytest tests/py/test_page_board.py -q
```
Expected: `<N> passed` where N is the ported count (roughly 140). Any failure here is a
re-base that missed a path, not a test to weaken.

```bash
python3 scripts/board_gate.py index
```
Expected: `board-gate ERROR no board at data/boards/index.json` and exit 2. That is the
right answer today; Task 5 writes the board.

- [ ] **Step 9: Commit**

```bash
git add -A && git commit -m "port: Page Board library, gate, approve, artifact builder, schemas, tests

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: The homepage proving board

One worked example so project 4 starts from a board that passed, not from a schema.

**Files:**
- Create: `data/boards/index.json`, `data/boards/inbox/index.json`, `docs/artifacts/boards/index.html`

- [ ] **Step 1: Build, so the gate has live headings to read**

```bash
npm run build 2>&1 | tail -2
```

- [ ] **Step 2: Write `data/boards/index.json`**

The board's `sections` mirror the migrated homepage's H2s exactly — read them from the
built page, do not invent them:
```bash
python3 - <<'PY'
import re, pathlib
h = pathlib.Path("dist/index.html").read_text()
for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", h, re.S):
    print(re.sub(r"<[^>]+>", "", m.group(1)).strip())
PY
```
Expected 14 H2s, beginning `Key Takeaways: The BluestaffyUK Promise` and ending
`Available Blue Staffy Puppies` (the last three — `Blue Staffy UK`, `Quick Pages`,
`Cities We Serve` — are the footer's column headings, which `live_headings()` skips as site
chrome; do not put them in the board).

Write one `sections[]` entry per remaining H2, `heading` copied verbatim from the built
page, `n` in document order from 1, `id` the slugified heading, `intent` one sentence
describing what the section does today, `category` `"A"` and `group` `"MANDATORY"` (this
board records the migrated page, it does not propose a rebuild), `why` /`why_source`
`"present on the migrated WordPress page"` / `"dist/index.html (Foundation, verbatim
migration)"`, `framework` `"EEBP"`, `shape` `"standard"` (so no component options are
offered), `words` `{"min": 0, "max": 0}`, all nine `keywords` arrays empty, `entities` `[]`,
`tree` `[]`, `images` `[]`, `links` `{"internal": [], "external": []}`, and `options`
`{"candidates": [], "excluded": [], "pick": null, "note": "standard shape — no component choice"}`.

`meta`: `{"slug": "index", "page_type": "home", "status": "draft", "research_as_of": "2026-09-16", "sources": [{"path": "dist/index.html", "fetched": "2026-09-16"}]}`.

`h1`: five variants, the first being the built page's exact H1
(`Secure Your blue Staffy puppies for sale UK: Safe Delivery & Verified Papers`),
`recommended: 0`, `pick: null`.

`meta_set`: three titles ≤70 chars and three descriptions in the 140–160 band, `recommended`
`{"title": 0, "description": 0}`, `pick` `{"title": null, "description": null}`.

`brief`: `goal` "record the migrated homepage as a board so project 4 has a worked example";
`scope` "no content is rewritten"; `gates` `["board_gate.py index", "npm run check:all"]`;
`done` "board approved, gate passes, Artifact built"; `out_of_scope` `["any content edit"]`;
`primary_keyword` `"blue staffy puppies for sale uk"`; two `angles`; `strategy`;
`cta` `{"cadence": {"min": 400, "max": 1200}, "destination": "#contact", "anchors": ["Reserve a puppy"], "global_cta": "shown"}`;
`tool` `{"pick": "none", "evidence": "this board records an existing page and introduces no interactive tool; a tool pick here would be a change project 2 is not making", "trade_off": "project 4 revisits it"}`;
`schema` `{"types": ["LocalBusiness", "WebSite", "BreadcrumbList"], "offer_model": "none"}`
— matching what `Schema.astro` actually emits (Foundation's "Organization node not emitted
separately" decision), not what a puppy page will emit.

`tuple`: every slot `""` and `h6_prefixes` `["Kennel Note:"]`, because project 3 owns the
component kit and this page uses none of it yet.

`assets`: `[]`. `approval`: `null`.

- [ ] **Step 3: Approve it**

`board_approve.py` reads an inbox file. Write `data/boards/inbox/index.json` by hand with
the picks, then approve:
```bash
python3 - <<'PY'
import json, pathlib, sys
sys.path.insert(0, "scripts")
import pageboard as PB
b = PB.load_board("index")
inbox = {"slug": "index", "h1": 0, "meta": {"title": 0, "description": 0},
         "picks": {}, "notes": {}, "canvas_version": "none",
         "record_hash": PB.record_hash(b)}
p = pathlib.Path("data/boards/inbox/index.json"); p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(inbox, indent=2) + "\n")
print("wrote", p)
PY
python3 scripts/board_approve.py index
```
Expected: `approved index at <timestamp> — 0 picks, 0 text write-backs, ledger row index, 0 PROPOSED→ASSERTED`.
`0 picks` is correct: every section is `standard` shape, which offers no component choice.

- [ ] **Step 4: Pass the gate**

```bash
python3 scripts/board_gate.py index
```
Expected: `board-gate index [build] — 14 sections, N headings, 49 live pages, 0 entity refs, 0 ledger siblings, 0 assets examined` then `0 FAIL · <n> WARN`, exit 0.

> Execution note (2026-09-16): on the migrated homepage the gate reports five `header-collision` FAILs, exit 1. Two are chrome cleared by Task 15's whitelist re-base; three are genuine cross-page duplicates carried to project 4 (spec §11). Task 16 re-runs this gate after Task 15 and expects exactly those three FAILs remaining; Task 20 lists them in the gate report.
A `header-collision` FAIL here means a homepage H2 also appears on another built page — that
is a real Foundation finding, so record it in the gate report rather than editing the page;
this project rewrites no content. If it blocks the gate, add the colliding heading to
`HEADER_WHITELIST` in Task 15 only if it is genuine site chrome, and note the decision.

- [ ] **Step 5: Build the Artifact**

```bash
python3 scripts/build_page_board.py index
```
Expected: `wrote docs/artifacts/boards/index.html — 14 sections, 49 live pages checked`.
Publish it with the Artifact tool: `file_path` `docs/artifacts/boards/index.html`,
`capabilities` `{"db": {}}`, favicon 🐾, title from the page's own `<title>`, description
"The BlueStaffyUK homepage recorded as a Page Board — the worked example project 4 starts from."

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "board: homepage proving board, approved, gate green, artifact built

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Gate scripts, group A — `final_page_audit.py` and `page_hardening_scan.py`

The two that read `dist/` directly and share `_slugs.py`, which BSUK already has.

**Files:**
- Modify: `data/port-manifest.json`
- Create: `scripts/final_page_audit.py`, `scripts/page_hardening_scan.py`, `tests/py/test_final_page_audit.py`, `tests/py/test_page_hardening.py`

- [ ] **Step 1: Append four `rebase` rows**

```json
  { "src": "scripts/final_page_audit.py", "dst": "scripts/final_page_audit.py", "mode": "rebase", "notes": "SLUGS/BIRDS/COMPARISONS/FORSALE lists; $185/$350 shipping; PBFD; method labels; emoji; word bands; airport codes; add a non-zero exit" },
  { "src": "scripts/page_hardening_scan.py", "dst": "scripts/page_hardening_scan.py", "mode": "rebase", "notes": "SPECIES_GENERA; skills/ citations -> .claude/skills/; cag-library component paths; GA4 gateway id" },
  { "src": "tests/test_final_page_audit.py", "dst": "tests/py/test_final_page_audit.py", "mode": "rebase", "notes": "22 tests; bird->puppy fixtures, GBP shipping, no PBFD" },
  { "src": "tests/test_page_hardening_new_checks.py", "dst": "tests/py/test_page_hardening.py", "mode": "rebase", "notes": "45 tests; only the fixture HTML changes, every check is domain-neutral" }
```
Then `python3 scripts/port_from_cag.py --only scripts/ && python3 scripts/port_from_cag.py --only tests/`.

- [ ] **Step 2: Re-base `scripts/final_page_audit.py`**

1. Docstring line 2: `"""C.A.Gs final-page-pass auditor` → `"""BSUK final-page-pass auditor`.
2. `SLUGS` (18 CAG interior slugs) → BSUK's ten interior pages, read from `data/page-map.json`
   rather than retyped:
   ```python
   # Read, not retyped: data/page-map.json is what the build actually produced, and a
   # hand list drifts the first time a page is added (CAG's list was 18 slugs and its
   # dist/ was 104 pages).
   import json as _json
   _PM = _json.loads((Path(__file__).resolve().parents[1] / "data/page-map.json").read_text())["pages"]
   SLUGS = [p["url"].strip("/") for p in _PM if p["kind"] == "rich"]
   TRANSACTIONAL = {"buy-blue-staffy-puppies-uk", "blue-staffy-pup-sale-uk", "buy-staffy-puppies-for-sale-uk"}
   ```
3. `BIRDS` → `PUPPIES`, read from `data/puppies.json`:
   `PUPPIES = ["available-puppies/" + p["slug"] for p in _json.loads((...ROOT/"data/puppies.json").read_text())["puppies"]]`.
   Rename the `--birds` flag to `--puppies` and the page type `"bird"` to `"puppy"`
   throughout (nine call sites; `grep -n '"bird"' scripts/final_page_audit.py`).
4. `COMPARISONS` → `[]` with the comment
   `# BSUK has no comparison cluster yet; project 5 writes it. An empty list is honest; a list of pages that do not exist would make every run print MISSING.`
   `FORSALE` → the three `for-sale` slugs in `tests/render/targets.json`.
5. The shipping-line checks. Replace the `$185 airport / $350 home` message and both regexes
   with BSUK's delivery facts from `data/settings.json` (`delivery_min_gbp` 200,
   `delivery_max_gbp` 350):
   ```python
   SHIP_RE = re.compile(r"£\s?200\b[\s\S]{0,80}£\s?350\b|£200\s*[–-]\s*£350")
   ```
   and the message `"delivery section must show the £200–£350 DEFRA-approved transport band"`.
6. Delete the PBFD / polyoma regex and its finding entirely, and the
   `"no_emoji_parrot"` check (BSUK's homepage ships 🚚 and 🐾 by design — replacing one banned
   emoji with another would be inventing a rule Foundation never had). Delete the
   `AUTH=("APHIS","USDA","FTC","IC3",...)` tuple and its check: no UK analogue is established,
   and an authority list nobody agreed is a fabricated claim.
7. `"congoafricangreys.com" not in d.get("href","")` → `"bluestaffyuk" not in d.get("href","")`.
8. The method-label regex and the `"C.A.Gs" in p.title` check: delete both (spec §7 drops
   CAG's rule 12, brand-owned method labels).
9. Airport codes `r"\b(DEN|LAX|MIA|ORD|LAR)\b"` → delete; BSUK delivers by road.
10. `"appendix i"`, `"captive-bred"`, `"usda"`, `"awa"` credential tokens →
    `"kc registered"`, `"defra"`, `"microchipped"`, `"vet checked"`.
11. Lifespan `r"40\s*[–-]\s*60|40 to 60"` → `r"12\s*[–-]\s*14|12 to 14"` (Staffordshire Bull
    Terrier life expectancy).
12. Word bands: puppy pages `400 <= nwords <= 1500`, for-sale `1500 <= nwords <= 5000`,
    interior `600 <= nwords <= 4000`. Widen rather than narrow — Foundation migrated
    WordPress bodies verbatim and a tight band would fail pages this project may not edit.
13. **The exit code.** CAG's `main()` never calls `sys.exit`, so the script always returns 0
    even on FAIL. Replace the tail with:
    ```python
        print(f"\nexamined {len(rows)} pages; {nfail} problems  ({npass} PASS · {nwarn} PASS-WITH-WARNINGS · {nfail} FAIL)")
        print("\nSubjective (voice/humour/readability/tone) = manual spot-check.")
        return 1 if nfail else 0

    if __name__ == "__main__":
        sys.exit(main())
    ```
    Spec §4 fixes the output shape as `examined N …; 0 problems` and Foundation's gates exit
    non-zero on problems; a gate that cannot fail is not a gate.

- [ ] **Step 3: Re-base `scripts/page_hardening_scan.py`**

Every one of its 23 checks is domain-neutral CSS/HTML analysis. Six edits:
1. Docstring line 3 `CAG Page-Hardening Scanner` → `BSUK Page-Hardening Scanner`, and the
   final print `f"CAG page-hardening scan — …"` → `f"BSUK page-hardening scan — …"`.
2. Every `skills/cag-<n>.md` citation → `.claude/skills/bsuk-<n>/SKILL.md`
   (`grep -n 'skills/cag-' scripts/page_hardening_scan.py` finds five: `cag-page-hardening`
   ×3, `cag-gate-integrity` ×2).
3. `SPECIES_GENERA = {"Psittacus", "Ara", "Amazona", "Cacatua", "Eclectus", "Poicephalus"}` →
   `SPECIES_GENERA = {"Canis"}`, and `"Psittacus erithacus", "Psittacus timneh"` →
   `"Canis familiaris"`. The check italicises binomials; BSUK uses one.
4. `SRC_GLOBS` — keep as written, they match BSUK's tree. `src/components/cag-library/`,
   `cag-inquiry-compact.astro`, `cag-inquiry-form.astro` → `src/components/`,
   `ContactForm.astro` (BSUK's only form component; project 3 brings the kit).
5. `src/components/MobileTabBar.astro` / `TABBAR_Z` / `TABBAR_H`: BSUK ships no tab bar, so
   the `bottom-bar-under-tabbar` check examines nothing. Keep the check and add it to
   `targets.json`'s `deferred_checks` in Task 16 rather than deleting it — the pattern
   Foundation established for a registered check with no page to judge.
6. The GA4 block: `/70de/`, `G-MEWJ9GVC4T`, `~327 KiB` are CAG's. BSUK ships no analytics
   until project 6, so replace the container id with `os.environ.get("GA4_MEASUREMENT_ID", "")`
   and make `analytics-double-load` skip when it is unset, with the comment
   `# BSUK ships no analytics until project 6; the check stays wired so the day a tag lands it is already judged.`
   Every prose reference to a CAG page (`/hand-raised-.../`, `/african-greys-for-sale-with-health-guarantee/`)
   becomes `a for-sale page` — the finding text explains a class of defect, and naming a page
   that does not exist here helps nobody.

- [ ] **Step 4: Re-base the two test files**

`tests/py/test_page_hardening.py` (45 tests): only the inline fixture HTML changes — swap
bird nouns for puppy nouns and the CAG component paths for BSUK's. Every assertion stands.

`tests/py/test_final_page_audit.py` (22 tests): rewrite the fixtures as puppy pages; drop
`test_bird_pbfd_claim_fails` and `test_pbfd_denial_not_a_false_fail` (the check is gone);
rename `bird`→`puppy` in the eleven test names that carry it; replace the two shipping tests'
`$185/$350` strings with `£200–£350`. Add one new test the port introduces:
```python
def test_main_exits_non_zero_when_a_page_fails(tmp_path, monkeypatch, capsys):
    """CAG's final_page_audit could not fail. Foundation's gates exit non-zero on problems,
    and a gate that always returns 0 is a report, not a gate."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "dist").mkdir()
    assert A.main() != 0 or "0 problems" in capsys.readouterr().out
```

- [ ] **Step 5: Run**

```bash
python3 -m pytest tests/py/test_final_page_audit.py tests/py/test_page_hardening.py -q
python3 scripts/final_page_audit.py | tail -3
python3 scripts/page_hardening_scan.py | tail -3
```
Expected: pytest green; `final_page_audit` prints `examined <n> pages; <n> problems` (a
non-zero problem count is the migrated-content baseline — record it, do not edit pages);
`page_hardening_scan` prints `<n> ERROR · <n> WARN` and exits 0 without `--fail-on-error`.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "port: final_page_audit and page_hardening_scan, re-based, with tests

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Gate scripts, group B — `aeo_audit.py`, `evidence_audit.py`, `form_contract_audit.py`

**Files:**
- Modify: `data/port-manifest.json`
- Create: the three scripts, `tests/py/test_aeo_audit.py`, `tests/py/test_evidence_audit.py`, `tests/py/test_evidence_per_slug_overrides.py`, `tests/py/test_form_contract_audit.py`

- [ ] **Step 1: Append seven `rebase` rows**

`scripts/{aeo_audit,evidence_audit,form_contract_audit}.py` → same path; and
`tests/test_aeo_audit.py`, `tests/test_evidence_audit.py`,
`tests/test_evidence_per_slug_overrides.py`, `tests/test_form_contract_audit.py` →
`tests/py/` under the same basenames. Notes: for `aeo_audit` —
`"LABELED_METHODS, BINOMIAL, BREEDER, PLACE, CREDENTIAL regexes; skills/ citations"`;
for `evidence_audit` — `"FACT_SIGNAL regex; page-type heuristics; evidence-budgets"`;
for `form_contract_audit` — `"ENDPOINT from the environment; LOCATION regex; the seven-field contract becomes BSUK's"`.
Run the port.

- [ ] **Step 2: Re-base `scripts/aeo_audit.py`**

```python
LABELED_METHODS = []        # spec §7 drops CAG's rule 12; BSUK owns no method label.
BINOMIAL = r"Canis\s+(?:lupus\s+)?familiaris"
BREEDER = r"Lisa\s+Bright|Bright['’]s"
PLACE = re.compile(r"Glasgow|Scotland", re.I)
CREDENTIAL = r"KC[- ]registered|DEFRA|microchipp?ed|vet[- ]checked|BVA|Kennel Club"
```
`PRONOUNS`, `VISIBLE_DATE` and `HEDGE_OPENERS` are unchanged. `STAT_HEADER`'s `birds?` /
`states?` become `puppies?|pups?` / `regions?|cities?`. The three finding messages:
`"no binomial (Canis familiaris) anywhere"`,
`"breeder-name entity absent — 'we' instead of 'Lisa Bright'"`, and delete the
method-name finding with `LABELED_METHODS` now empty (guard it:
`if LABELED_METHODS and not ...`). Citations `skills/cag-aeo-pass.md` and
`skills/cag-gate-integrity.md` → `.claude/skills/bsuk-aeo-pass/SKILL.md` and
`.claude/skills/bsuk-gate-integrity/SKILL.md`. Change the final summary to the Foundation
shape: `print(f"\nexamined {len(pages)} pages; {errs} problems")`.

- [ ] **Step 3: Re-base `scripts/evidence_audit.py`**

```python
FACT_SIGNAL = (r"Canis\s+(?:lupus\s+)?familiaris|\b1[0-9]\s*(?:to|–|-)\s*1[0-9]\s+years"
               r"|lifespan|hip\s*score|elbow\s*score|L2-?HGA|HC\b|PHPV|patella|KC[- ]registered")
```
`BUDGETS_PATH`, `LEDGER_PATH`, `TARGETS_PATH` are unchanged (BSUK uses the same layout).
The `CHECK_IDS` list is unchanged — every one is domain-neutral. The page-type heuristics
(L264–276) are rewritten to BSUK's slugs:
```python
if slug == "index": return "home"
if slug.startswith("available-puppies/"): return "puppy"
if slug in ("available-puppies", "uk-locations", "blog"): return "hub"
if slug.startswith("uk-locations/"): return "location"
if "-vs-" in slug or slug.endswith("-comparison"): return "comparison"
if slug.startswith("blue-staffy-blog") or slug.startswith("blog/"): return "blog"
if slug in ("buy-blue-staffy-puppies-uk", "blue-staffy-pup-sale-uk", "buy-staffy-puppies-for-sale-uk"): return "for-sale"
return "interior"
```
`CITE` class exclusions `bird-name` / `price-name` → `puppy-name` / `price-name`; the
`cag-library/Testimonials.astro` comment → `a testimonial component (project 3)`. Then write
`data/quality/evidence-budgets.json` in Task 9 — until it exists the script raises, which is
why its tests use tmp fixtures and its live run waits for Task 9.

- [ ] **Step 4: Re-base `scripts/form_contract_audit.py`**

This is the Python half of the same contract `tests/render/checks/form.ts` enforces, and the
two must agree or they will give different verdicts on the same page — CAG's own
`reference_same_input_different_verdict` note. Both are rewritten to BSUK's built form in
one movement; this step and Task 14 Step 2 must produce identical field sets.

```python
# Read from the environment, never hard-coded. The id is a credential-adjacent fact that
# lives in .env (spec §8); a literal here would be a second source of truth that goes stale
# the day the form moves, and would put a real endpoint in a committed file.
import os
_FID = os.environ.get("PUBLIC_FORMSPREE_ID", "")
if not _FID:
    sys.exit("REFUSED: PUBLIC_FORMSPREE_ID is unset — a form audit that matches nothing "
             "would report every form clean. Set it in .env (see .env.example).")
ENDPOINT = f"https://formspree.io/f/{_FID}"

# BSUK's contract, read off the built contact page (dist/uk-blue-staffy-breeders-contact/
# index.html, 2026-09-16). CAG's seven screening questions were written for a US parrot
# resale market and have no BSUK analogue; inventing dog equivalents would be inventing a
# screening policy the breeder has not set. What IS true today is the six named controls,
# the honeypot and the two hidden fields, and that is what this gate holds.
KEYS = [
    ("name",     r"^name$"),
    ("email",    r"^email$"),
    ("phone",    r"^phone$"),
    ("location", r"^location$"),
    ("puppy",    r"^puppy$"),
    ("message",  r"^(message|msg)$"),
]
REQUIRED = ("name", "email", "puppy", "message")   # phone and location are optional as built
HIDDEN = ("_next", "_subject")
SHORT = ("name", "email", "message")
LOCATION = re.compile(r"^uk-locations/")
```
`contract_keys()` keeps its three-way shape: `full` for the contact page, `short` for
`blog/*`, `none` for `uk-locations/*` and the hubs. The required check becomes
`hits and (name not in REQUIRED or any(c.required for c in hits))` so an optional `phone`
is not reported as a defect. Add a hidden-field check (`_next` and `_subject` must be
present on the inquiry form, or Formspree has no reply-to subject and no redirect) and
keep the `_gotcha` exclusion from the visible-control count exactly as written.

- [ ] **Step 5: Re-base the four test files**

- `test_aeo_audit.py` (10 tests): swap the two `Psittacus` tests for `Canis familiaris`;
  delete `test_labeled_method_detects_the_two_approved_names` (the list is empty by design)
  and add `test_labeled_method_check_is_inert_when_no_method_is_owned`.
- `test_evidence_audit.py` (19) and `test_evidence_per_slug_overrides.py` (7): only the
  fixture prose changes, plus the homepage slug `"index"` stays `"index"`. Every assertion
  stands.
- `test_form_contract_audit.py` (17): rewrite every fixture form to BSUK's six fields;
  replace the three `location cluster` tests' slugs with `uk-locations/...`; delete
  `test_blog_short_contract_passes_without_experience_delivery`; add:
  ```python
  def test_unset_formspree_id_refuses_rather_than_matching_nothing(monkeypatch):
      monkeypatch.delenv("PUBLIC_FORMSPREE_ID", raising=False)
      with pytest.raises(SystemExit) as e:
          importlib.reload(F)
      assert "PUBLIC_FORMSPREE_ID" in str(e.value)

  def test_optional_phone_is_not_a_missing_field(tmp_path):
      """As built, phone and location are optional. A contract that demanded them would
      report the shipped page as broken and teach the next agent to add `required`."""
      rows = F.audit_dist(_dist_with_contact_form(tmp_path, phone_required=False))
      assert not [p for r in rows for p in r["problems"] if "phone" in p]
  ```
  Every test in this file sets `PUBLIC_FORMSPREE_ID` via `monkeypatch.setenv` in a fixture.

- [ ] **Step 6: Run**

```bash
PUBLIC_FORMSPREE_ID=xqegrzka python3 -m pytest tests/py/test_aeo_audit.py tests/py/test_evidence_audit.py tests/py/test_evidence_per_slug_overrides.py tests/py/test_form_contract_audit.py -q
```
Expected: `<N> passed`. Do not put the id in the committed pytest config; Task 18 writes it
to `.env` and Task 17 adds `set -a; . ./.env; set +a` to the npm scripts that need it.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "port: aeo, evidence and form-contract audits, re-based to BSUK's facts

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: Gate scripts, group C — `perf_audit.py`, `quality_report.py`, `generate_page_dates.py`, `health-sweep.sh`

**Files:**
- Modify: `data/port-manifest.json`
- Create: the four scripts, `scripts/lighthouse/agentic-{mobile,desktop}.mjs`, `tests/py/test_perf_audit.py`, `tests/py/test_quality_report.py`

- [ ] **Step 1: Append six `rebase` rows**

`scripts/{perf_audit,quality_report,generate_page_dates}.py` and `scripts/health-sweep.sh`
→ same paths; `tests/test_perf_audit.py` and `tests/test_quality_report.py` → `tests/py/`.
Add two more rows for the Lighthouse configs `perf_audit.py` requires and spec §2 does not
list — they are not optional, the script exits without them:
```json
  { "src": "scripts/lighthouse/agentic-mobile.mjs", "dst": "scripts/lighthouse/agentic-mobile.mjs", "mode": "copy", "notes": "Lighthouse config perf_audit.py requires; site-agnostic" },
  { "src": "scripts/lighthouse/agentic-desktop.mjs", "dst": "scripts/lighthouse/agentic-desktop.mjs", "mode": "copy", "notes": "as above" }
```
Run the port. If either config is absent from CAG, `perf_audit.py` must be re-based to fall
back to Lighthouse's built-in mobile/desktop presets rather than exiting — record which
happened in the commit message.

- [ ] **Step 2: Re-base `scripts/perf_audit.py`**

One literal and one guard:
- `LIVE_ORIGIN = "https://congoafricangreys.com"` →
  `LIVE_ORIGIN = os.environ.get("SITE_URL", "https://SITE_URL_PLACEHOLDER")`, and make
  `--live` / `--psi` refuse when it is still the placeholder:
  ```python
  if a.live and "PLACEHOLDER" in LIVE_ORIGIN:
      sys.exit("REFUSED: --live/--psi needs a real SITE_URL. BSUK has no domain until "
               "project 6; measure dist/ instead (drop --live).")
  ```
- The `/70de/` edge-injected-script note and the `181 KB` figure are CAG's Cloudflare
  gateway. Keep the `EDGE_TYPES` machinery — it is the general check — and rewrite the
  comment to `# A host that injects its own scripts is a real class of defect; BSUK has no host yet (project 6), so this finds nothing today and is wired so it will.`
- `PERF_DIR = ROOT / "data" / "quality" / "perf"` is unchanged; add `data/quality/perf/` to
  `.gitignore` beside `data/quality/raw/` — the records are per-machine measurements.

- [ ] **Step 3: Re-base `scripts/quality_report.py`**

Two literals: `"CAG QUALITY REPORT"` → `"BSUK QUALITY REPORT"`, and
`"run scripts/rework_ledger.py --last-30-days"` → `"run scripts/rework_ledger.py --last-30-days (arrives with project 4)"`,
because `rework_ledger.py` is not in the port (spec §2 ports the empty ledger, not the
writer). Everything else — the five sections, `CHECK_ID_RE`, the `scripts/*_audit.py` id
scan, `judgment_cap` — is domain-neutral and stands. Its test file needs only the two
string changes.

- [ ] **Step 4: Re-base `scripts/generate_page_dates.py`**

No CAG literals at all beyond the deploy-workflow comment. Two edits: change the comment's
`.github/workflows/deploy.yml` reference to
`# BSUK has no deploy workflow until project 6; the honest-date problem this solves is the same one Foundation recorded for sitemap lastmod.`,
and change `glob.glob("src/pages/**/*.astro")` to also walk `src/content/blog/*.md`, since
BSUK's posts are a content collection and would otherwise carry no date at all. This closes
Foundation gate-report open item 8 (`schema-date-modified-present`, 18 rows) and open item
"sitemap `lastmod` is TODAY" — note both in the Task 20 report; wiring the dates into the
pages themselves is project 4's work, not this project's.

- [ ] **Step 5: Re-base `scripts/health-sweep.sh`**

- `DOMAIN="https://congoafricangreys.com"` → `DOMAIN="${SITE_URL:-}"`, and wrap the live
  block in `if [ -n "$DOMAIN" ]; then … else warn "no SITE_URL — skipping live checks (project 6)"; fi`.
  The three live paths become `"/" "/buy-blue-staffy-puppies-uk/" "/available-puppies/"`.
- `bash scripts/verify_model_tiers.sh` → delete the block. That script is not ported and the
  registry it verifies is regenerated in Task 11, which is where the check belongs.
- `python3 scripts/register_skills.py --check` and the `--copy` recovery → delete both. Spec
  §1 retires the flat `skills/*.md` mirror; a check that the mirror is in sync is a check for
  a thing that no longer exists. Replace the block with
  `python3 scripts/marker_check.py || FAIL=1`.
- The `skills/*.md` and `skills/*/SKILL.md` glob → `.claude/skills/*/SKILL.md`.
- `.claude/agents/*.md` frontmatter check: keep, and change `^model:` to accept `inherit`.
- Header comment `# CAG FULL SYSTEM HEALTH SWEEP` → `# BSUK FULL SYSTEM HEALTH SWEEP`, and
  the Astro/Cloudflare line → `# Designed for BlueStaffyUK (Astro -> static dist/; no host until project 6).`
- The `/tmp/cag-build.log` and `/tmp/cag-skillreg.log` paths → `/tmp/bsuk-build.log`; the
  skillreg log is deleted with its block.

- [ ] **Step 6: Re-base the two tests, and restore the board perf tests**

`test_perf_audit.py` (11 tests, loaded via `importlib.util`): unchanged except the PSI URL
assertions, which now read `LIVE_ORIGIN` from the environment. `test_quality_report.py`
(17 tests): unchanged. Then move the nine `test_perf_*` tests deferred in Task 4 Step 7
back into `tests/py/test_page_board.py` — `perf_audit.py` now exists, so
`pageboard.perf_findings()` has something to read.

- [ ] **Step 7: Run**

```bash
python3 -m pytest tests/py -q
python3 scripts/quality_report.py | tail -6
bash scripts/health-sweep.sh --no-build | tail -5
```
Expected: pytest green; `quality_report` prints its five sections (§5's untested list will be
long until Task 9 writes the re-based `rule-index.json`); `health-sweep` ends
`ALL CRITICAL CHECKS PASSED` or names exactly which check failed.

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "port: perf, quality-report, page-dates and health-sweep, re-based

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: Rule packs, the rule ledger and the empty ledgers

**Files:**
- Modify: `data/port-manifest.json`
- Create: `rules/{README,headings,images,schema,links,copy,design,gates,deploy,puppies}.md`, `data/quality/{rule-index,evidence-budgets,rework-ledger,evidence-ledger}.json`

- [ ] **Step 1: Append eleven `rebase` rows**

Nine `rules/<n>.md` → same path; `rules/for-sale.md` → `rules/puppies.md`;
`data/quality/rule-index.json` → same path; `data/quality/evidence-budgets.json` → same path.
Run the port, then create the two empty ledgers by hand (they are not ported — spec §1 says
they start empty):
```bash
echo '{ "entries": [] }' > data/quality/rework-ledger.json
echo '{ "claims": [] }'  > data/quality/evidence-ledger.json
```
Verify each against what `quality_report.py` and `evidence_audit.py` actually read; if
either expects a different top-level key, match the ported script, not this plan.

- [ ] **Step 2: Re-base the eight packs that keep their name**

Substitutions per the table in "Re-base substitutions" below, plus these pack-specific
deletions and rewrites:

| Pack | Delete | Rewrite |
|---|---|---|
| `copy.md` | the `AEO facts + brand-owned method names` rule (CITES Appendix I, the $1,500–$3,500 range, the two method labels) and the `CITES Awareness` rule — both are parrot-regulation facts with no dog analogue | `Write-From-Outline`'s examples become `puppy page → location page → buying guide`; `First-Person Brand Voice` becomes Lisa Bright's voice; `Entity 4-Move Loop` keeps its shape with `.claude/skills/bsuk-entity-agent/SKILL.md` and the health claims become hip/elbow scores and L2-HGA/HC/PHPV DNA tests, each marked `NOT FETCHED` until a certificate is on file |
| `for-sale.md` → `puppies.md` | the `$185 airport / $350 home` shipping-cost rule body | H1 becomes `# The puppy and buy cluster`; the shipping rule becomes the £200–£350 DEFRA band on every card and in the delivery section; add the three rules spec §7 names: Product schema per pup, `InStock` only on an available pup, no head-cropped portraits |
| `headings.md` | — | acronym exempt list `C.A.Gs, CITES, USDA, DNA, PCR, IATA` → `UK, KC, DEFRA, BVA, DNA, SBT`; `Hand-Raised`/`Captive-Bred` → `Home-Raised`/`KC-Registered`; "the 6 `/available/` bird pages" → "the 6 `/available-puppies/` pages" |
| `images.md` | — | "so the bird isn't cropped out of the 16:9 strip" → "so the puppy isn't cropped out"; the CvT/CvM/CvC/MvF comparison-page references → "the comparison cluster (project 5)"; `/african-grey-breeding-pair-for-sale/` → `/buy-blue-staffy-puppies-uk/` |
| `deploy.md` | — | rewritten in full per spec §7: work on `foundation`, commit, **never push until project 6**; IndexNow and deploy are release-guarded; drop the `Skills are registered & Skill-invokable` rule (the flat mirror is retired) |
| `design.md` | — | the `order`-swap example's "pushes the birds below the fold" → "pushes the puppy cards below the fold" |
| `links.md` | — | the "Congo care guide" example → "the Staffordshire Bull Terrier guide" |
| `gates.md`, `schema.md`, `README.md` | — | no rule changes; only `C.A.Gs`→`BlueStaffyUK` and `skills/cag-<n>.md`→`.claude/skills/bsuk-<n>/SKILL.md` citations |

- [ ] **Step 3: Re-base `data/quality/rule-index.json`**

65 rows, `judgment_cap: 12`. Three edits:
1. Delete the two parrot-specific `judgment` rows: `cites-appendix-i-framing` and
   `brand-owned-method-labels` (spec §7 drops CAG's rules 2 and 12). Also delete
   `verified-claim-ledger` (spec §7 drops rule 11). That leaves **9** judgment rules; set
   `"judgment_cap": 9` so the cap still binds — a cap of 12 with 9 rules under it would
   silently license three new ungated rules.
2. Rename every rule id whose file moved: `for-sale-extended-meta` → `puppies-extended-meta`,
   `shipping-cost-on-every-card` → `delivery-band-on-every-card`, and every `pack` value
   `rules/for-sale.md` → `rules/puppies.md`.
3. Every `test` value pointing at a check that does not exist in BSUK's
   `tests/render/checks/` must be re-pointed or re-classed. Find them mechanically —
   `quality_report.py` §5 is exactly this check:
   ```bash
   python3 scripts/quality_report.py | sed -n '/RULES WITH NO BACKING TEST/,$p'
   ```
   Re-point where the check exists under another id; re-class to `untested` where it does
   not; delete the row only where the rule itself was deleted above. Do not invent a test
   path to silence the report — `no-test-no-rule` is one of the ported rules.

- [ ] **Step 4: Re-base `data/quality/evidence-budgets.json`**

The budgets are per-term repetition caps. Replace CAG's terms with BSUK's head terms
(`blue staffy`, `staffy puppies`, `staffordshire bull terrier`, `puppies for sale`,
`glasgow`, `uk`), keep the structure, and keep `title_max_chars` at 70 with a per-slug
override only where a built page already exceeds it — measure, do not guess:
```bash
python3 - <<'PY'
import pathlib, re
for p in sorted(pathlib.Path("dist").rglob("index.html")):
    m = re.search(r"<title>(.*?)</title>", p.read_text(), re.S)
    if m and len(m.group(1)) > 70:
        print(len(m.group(1)), p.parent.relative_to("dist") or "index")
PY
```
Add a `title_max_chars_by_slug` entry for each slug printed, set to its measured length, with
a `_note` saying these are Foundation baselines that project 4 brings back under 70.

- [ ] **Step 5: Run**

```bash
python3 scripts/quality_report.py | tail -8
npm run check:markers | tail -3
PUBLIC_FORMSPREE_ID=xqegrzka python3 scripts/evidence_audit.py --all | tail -3
```
Expected: `quality_report` §5 prints `none. <n> checks registered, 9 judgment rules within cap.`;
the marker count drops by the `rules/` contribution; `evidence_audit` prints
`examined <n> pages; <n> problems` — a non-zero count is the migrated-content baseline.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "rules: 10 packs re-based, rule-index at 9 judgment rules, ledgers empty

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: Rewrite `CLAUDE.md`

**Files:**
- Modify: `data/port-manifest.json`
- Create: `CLAUDE.md`

- [ ] **Step 1: Append the row and seed the file**

```json
  { "src": "CLAUDE.md", "dst": "CLAUDE.md", "mode": "rebase", "notes": "rewritten from CAG's 169-line skeleton; same structure, BSUK facts, deploy inactive, rules 2/11/12 dropped" }
```
Run the port. It writes CAG's file once; Step 2 replaces its contents entirely.

- [ ] **Step 2: Write `CLAUDE.md`, verbatim**

```markdown
# BlueStaffyUK — Project Guide

BlueStaffyUK is a Glasgow breeder of Staffordshire Bull Terriers, Blue Staffies in
particular (Lisa Bright, 40 Coltmuir Street, G22 6LU). The site is transactional +
informational: the buy and location pages take enquiries, the care and guide pages earn
the traffic.

## Paths and deploy model

- **`src/pages/<slug>/index.astro` is what ships.** Eleven rich pages are one Astro file
  each; 28 locations and 6 puppies are data-driven from `data/locations.json` and
  `data/puppies.json`; blog posts are a markdown content collection.
- Build `npm run build` → `dist/`. Every gate measures `dist/`, never source.
- **Work on `foundation`. Commit after every task. Never push until project 6** — this
  repo has no remote and must not get one. `git remote -v` printing nothing is a gate, not
  an accident.
- After adding or removing a page: `npm run sitemaps` (the build's postbuild already does it).
- Generated files are never hand-edited: the eleven rich pages, `data/page-map.json`,
  `data/locations.json`, `data/image-manifest.json`, `public/_redirects`, `public/llms.txt`,
  `public/images/**`, `src/content/blog/*.md`. `README.md` carries the full list.

## Deploy — inactive until project 6

There is no host, no domain and no deploy. `SITE_URL_PLACEHOLDER`, `PHONE_PLACEHOLDER` and
an unset `PUBLIC_FORMSPREE_ID` are the correct state today and catastrophic on launch day,
so the launch tooling is ported but refuses to run:

- `python3 scripts/indexnow_submit.py <slug>` and `bash scripts/health-sweep.sh`'s live
  block require `BSUK_RELEASE=1` and a real `SITE_URL`. Without both they print `REFUSED`
  and exit non-zero.
- `BSUK_RELEASE=1 npm run check:placeholders` is the gate that will refuse to ship a
  placeholder. Pre-launch it counts and prints and passes.
- `python3 scripts/perf_audit.py <slug> --live` and `--psi` refuse for the same reason.

## The rules live in `rules/`, not here

The pixel-level rules are enforced by `tests/render/`, not by this file — a check that
fails the build is worth more than a paragraph that asks nicely.

| Pack | Covers |
|---|---|
| [`rules/headings.md`](rules/headings.md) | H1–H6 outline gate, Title Case, header style |
| [`rules/images.md`](rules/images.md) | uniform in-body sizing, alt-text keyword spread, further-reading thumbs = the target's own hero |
| [`rules/schema.md`](rules/schema.md) | structured data, schema-only freshness |
| [`rules/links.md`](rules/links.md) | Link-First anchor placement |
| [`rules/copy.md`](rules/copy.md) | voice, originality, entity method, claims |
| [`rules/design.md`](rules/design.md) | the nine non-negotiable visual rules + hero/counter separation, H3-image-first |
| [`rules/gates.md`](rules/gates.md) | pre/post-build process gates |
| [`rules/deploy.md`](rules/deploy.md) | where work lands and how it ships |
| [`rules/puppies.md`](rules/puppies.md) | the puppy and buy cluster's own rules |

`data/quality/rule-index.json` is the machine-readable index: every rule is `test`,
`judgment`, or `untested`. **`untested` means deletion candidate** —
`python3 scripts/quality_report.py` §5 prints the list on every run.

### Page type → what to read first

| Building… | Skill | Extra rule packs |
|---|---|---|
| home | `bsuk-site-patterns` | headings, images, copy |
| buy / for-sale | `bsuk-puppy-page-builder` | puppies, images, headings |
| puppy `/available-puppies/<slug>/` | `bsuk-puppy-page-builder` | puppies, schema, images |
| hub | `bsuk-site-patterns` | links, headings |
| location | `bsuk-location-page-builder` | copy, links |
| blog | `bsuk-blog-post` | headings, images |
| about / contact | `bsuk-contact-form`, `bsuk-trust-signals` | copy, links |
| comparison | `bsuk-comparison-page-builder` | images, headings, copy |

Full task→entry-point table: [`docs/reference/quick-start.md`](docs/reference/quick-start.md).

## The ten rules that stay here

These ten have **no mechanical decision procedure**, which is exactly why they cannot be
delegated to a test and must stay in context. Every other rule moved to a pack. Full text
and the recorded reason for each: `data/quality/rule-index.json` + the packs.

1. **First-person brand voice.** Write as Lisa Bright: *we / us / our / here at
   BlueStaffyUK*. Our puppies, our kennel and our credentials are framed as ours, never
   described from outside. Neutral register is correct only for breed facts and cited
   research.
2. **Work on `foundation`; commit after every task; never push.** There is no remote and
   project 6 owns the launch. Finished work that is unpushed is finished; finished work
   that is uncommitted is lost.
3. **Recommend + Why.** Whenever you present options, mark exactly one
   **(Recommended)**, justify it from real data (GSC, competitors, the codebase — never
   taste), and name the trade-off of the recommended pick.
4. **Restate the brief before you build.** Goal · scope · gates · what "done" means · what
   is out of scope. Improve the prompt where it is ambiguous so it can be corrected before
   work is spent on it.
5. **Preview before apply.** Any page redesign is previewed and approved before it is
   written to site files. A redesign never adds or removes content — visual layer only.
6. **Confidence gate, 97%.** Below that, do not dead-stop: write finished work to disk, log
   the open question to the session brief's `## Open Flags`, ask exactly ONE narrow
   question, and keep building everything that is not blocked.
7. **Write from the outline, never from a sibling.** Reuse components, CSS and structure
   freely; write every page's PROSE fresh from its own outline. Never open a sibling's file
   to copy paragraphs. Only the whitelist may match verbatim. Enforced *after* the fact by
   `dup-no-sibling-crossover`, but the rule is about method: a page copied and then reworded
   passes the test and still breaks the rule.
8. **No fabricated claims.** Never invent credentials, prices, reviews, test results or
   competitor metrics. Un-fetched data is written `NOT FETCHED`, never inferred. The
   guarantee length is `NOT FETCHED` — `data/settings.json` has `guarantee_days: null` and
   no page may state a number until the breeder gives one.
9. **No parrot vocabulary, ever.** This system came from a Congo African Grey breeder. The
   twelve markers `scripts/marker_check.py` scans for are not a style preference;
   a hit is a re-base that did not happen. There is no allowlist, and
   `npm run check:markers` is in `check:all`.
10. **Every deliverable ships as an Artifact with copy buttons, plus `.md`.** Research docs,
    outlines, keyword tables, meta sets, gate reports, lessons docs — the deliverable is a
    published Artifact whose sections each carry a copy button and which downloads as `.md`,
    not prose in the chat the breeder has to select by hand. Update the existing Artifact in
    place (pass its `url`) when one already covers the topic; mint a new URL only for
    genuinely new work. Keep the HTML source in `docs/artifacts/` so it is versioned and
    re-publishable. **Author the content once as markdown inside the page and render it** —
    that is what makes a section's copy button emit exact markdown.

## Gates — run these, do not re-derive them

```bash
npm run check:all
```
```bash
npm run test:py
```
```bash
npm run test:render:meta
```
```bash
npm run test:render:pages
```

`check:all` chains parity, redirects, schema, sitemaps, placeholders and the parrot marker
gate. `test:render:meta` is the gate that checks the checkers — run it **before** trusting
any page result. `test:render:pages` measures the target pages at 375/768/1280 in a real
browser.

Also: `python3 scripts/board_gate.py <slug>` · `python3 scripts/final_page_audit.py` ·
`python3 scripts/page_hardening_scan.py <slug>` · `python3 scripts/dup_content_audit.py [--headers]` ·
`python3 scripts/aeo_audit.py <slug>` · `python3 scripts/evidence_audit.py --all` ·
`python3 scripts/form_contract_audit.py` · `python3 scripts/quality_report.py` ·
`bash scripts/health-sweep.sh`.

**No page is built without an approved board.** `python3 scripts/board_gate.py <slug>`
refuses when `data/boards/<slug>.json` is missing or unapproved. The homepage board
(`data/boards/index.json`) is the worked example.

**A gate's output is a hypothesis about the page, not a fact about it.** Before editing
anything in response to a gate, confirm the defect on the built page; before believing a
PASS, read the gate's own examined count. `.claude/skills/bsuk-gate-integrity/SKILL.md`.

**When a defect escapes, charge it to the harness, not to a new rule.** If an invariant
already covered it and stayed quiet, the tool is broken: add the case to
`tests/render/fixtures/known_broken/`, watch the meta gate fail, fix the check, and write no
new rule.

**Foundation's render baseline is not a defect list.** Project 1 migrated WordPress markup
verbatim, so the harness is measuring the old site's body HTML through a new shell. Those
rows are the starting line for projects 3 and 4, and are recorded in
`docs/reports/foundation-gate-report.md`.

## Brand context — read before any design or content work

`data/settings.json` is the source of truth for the breeder's name, address, hours, socials
and the delivery band. `data/puppies.json` and `data/price-matrix.json` carry the current
litter and the prices. The locked facts, from the Foundation spec:

- Breeder **Lisa Bright**, Glasgow (40 Coltmuir Street, G22 6LU).
- Prices **£1,500** (male) and **£1,700** (female). Deposit **£500, refundable**.
- Delivery **£200–£350**, by DEFRA-approved transport, priced by distance.
- Phone is `PHONE_PLACEHOLDER` until project 6 provisions a number. It is the only allowed
  representation of the phone number anywhere in this repo.
- Guarantee length is **not established**. Do not write one.

The design system is project 3. Until then there is no component kit and no locked palette;
`src/layouts/BaseLayout.astro` and `src/styles/global.css` are the whole shell.

## Where everything else went

- [`docs/reference/system-registry.md`](docs/reference/system-registry.md) — every agent, skill, script and data file
- [`docs/reference/quick-start.md`](docs/reference/quick-start.md) — task → entry point, and the reference-doc index
- [`docs/reference/session-log.md`](docs/reference/session-log.md) — build history and **Known Issues**
- [`docs/reference/WORKFLOW.md`](docs/reference/WORKFLOW.md) — the sprint model
- [`docs/reference/seo-rules.md`](docs/reference/seo-rules.md) — the numbered SEO rules
- [`docs/reference/credentials.md`](docs/reference/credentials.md) — which env key exists and what reads it
- `docs/superpowers/specs/` and `docs/superpowers/plans/` — the six projects' specs and plans
```

- [ ] **Step 3: Run**

```bash
npm run check:markers | tail -3 && wc -l CLAUDE.md
```
Expected: `CLAUDE.md` contributes zero problems, and roughly 175 lines.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "docs: rewrite CLAUDE.md for BSUK — ten judgment rules, deploy inactive, board gate

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Re-base substitutions

Tasks 9, 11, 12 and 13 re-base prose documents that are too long to write verbatim here.
This table is the substitution contract for all of them. It is mechanical where it can be
and named judgement where it cannot.

| Find (case-insensitive) | Replace with |
|---|---|
| African Grey, African Grey Parrot, Grey(s) as a noun | Blue Staffy, Staffordshire Bull Terrier |
| parrot, bird, chick | puppy, pup, dog |
| clutch | litter |
| aviary | kennel |
| hand-raised, hand-reared | home-raised |
| C.A.Gs, CAG, CAGs | BlueStaffyUK, BSUK |
| congoafricangreys.com, https://congoafricangreys.com | `SITE_URL` (the env var) or `SITE_URL_PLACEHOLDER` in built output |
| Midland, Texas; any US state name | Glasgow; a UK region (Scotland, the Midlands, the North West, Wales …) |
| Congo, Timneh (as a variant) | blue, black, brindle (as a coat colour) |
| Mark & Teri Benjamin | Lisa Bright |
| `cag-<n>` (agent, skill, file or identifier prefix) | `bsuk-<n>` |
| `skills/<n>.md` | `.claude/skills/<n>/SKILL.md` |
| `data/clutch-inventory.json` | `data/puppies.json` |
| USD prices ($1,500–$3,500, $185, $350, $200 deposit) | the locked GBP facts: £1,500 / £1,700, £200–£350 delivery, £500 refundable deposit |
| USDA, APHIS, AWA, CITES, IATA, PBFD, APV, psittacosis | KC (Kennel Club), DEFRA, BVA, microchipped, vet-checked, hip/elbow score, L2-HGA / HC / PHPV |
| 40–60 years (lifespan) | 12–14 years |

**What to delete rather than substitute.** A section that only makes sense for parrots has
no dog equivalent, and inventing one is a fabricated claim (CLAUDE.md rule 8). Delete:
any section about CITES, import/export permits, wild-caught status, or Appendix listings;
any section about eggs, incubation, candling, hatch records, weaning or closed banding;
species-comparison sections (Congo vs Timneh, vs Macaw / Cockatoo / Amazon) and the pages
they name; air-cargo and airport-collection logistics; the two brand-owned method labels and
the Verified-Claim Ledger; and any credential list whose UK analogue has not been
established. Where deleting leaves a document shorter, that is the right outcome — padding
it back out with invented UK content is worse than a shorter honest document.

**Acceptance test for every re-base task**, run over the paths that task touched:
```bash
python3 scripts/marker_check.py
```
Expected: `examined N files; 0 problems` for those paths (the repo-wide count stays non-zero
until Task 16).

---

### Task 11: The curated agents

Spec §3 names about 25. Do them in three batches so a mistake in the substitution approach
is caught on eight files, not twenty-five.

**Files:**
- Modify: `data/port-manifest.json`
- Create: `.claude/agents/bsuk-*.md`, `scripts/build_agent_registry.py`, `data/agent-registry.json`, `tests/py/test_agent_registry.py`

- [ ] **Step 1: Append 26 `rename`-shaped `rebase` rows**

One row per name, `{ "src": ".claude/agents/cag-<n>.md", "dst": ".claude/agents/bsuk-<n>.md", "mode": "rebase", "notes": "<what must change>" }`:

- **Batch A — page builders (13):** `homepage-builder`, `hub-builder`, `location-builder`,
  `comparison-builder`, `purchase-guide`, `section-builder`, `structure-architect`,
  `content-architect`, `batch-rebuilder`, `framework-agent`, `interactive-component`,
  `infographic-builder`, `about-builder`.
- **Batch B — content (9):** `seo-content-writer`, `blog-post-agent`, `angle-agent`,
  `non-commodity-content-agent`, `content-audit-agent`, `image-pipeline`, `faq-agent`,
  `paa-agent`, `meta-description-agent`.
- **Batch C — ops, QA and analytics (14):** `agent-system-qa`, `self-update`,
  `deploy-verifier`, `accessibility-fixer`, `performance-fixer`, `site-hygiene-agent`,
  `canonical-fixer`, `redirect-manager`, `contact-form-updater`, `trust-signals-agent`,
  `footer-standardizer`, `gsc-analytics`, `keyword-verifier`, `rank-tracker`.

That is 36, not 25 — spec §3's "about 25 agents" undercounts its own list. Port every name
it prints; the count in the prose is the approximation, the list is the requirement.

Run the port after each batch's rows are added, so the batch's files appear together.

- [ ] **Step 2: Re-base each batch**

Per file, in this order:
1. Apply the substitution table. `cag-performance-fixer.md` needs none of it (it is the one
   agent with zero bird vocabulary) — change only its `name:` frontmatter field.
2. Rewrite the `description:` frontmatter field: it is what the dispatcher matches on, so a
   description still describing `/african-grey-parrot-for-sale-[state]/` routes work at the
   wrong agent. Name BSUK's real routes (`/uk-locations/<slug>/`, `/available-puppies/<slug>/`,
   `/buy-blue-staffy-puppies-uk/`).
3. Delete every GSC figure quoted in a description (`28 clicks, 14,915 impressions,
   position 45.6`) — those are CAG's numbers and BSUK has pulled none. Replace with
   `NOT FETCHED until project 6`.
4. Delete every reference to a data file that does not exist here
   (`data/competitors.json`, `data/clutch-inventory.json`, `data/reviews.json`,
   `data/financial-entities.json`, `data/cag-ontology.json` → `data/bsuk-ontology.json`).
   An agent that reads a missing file fails on first use; an agent whose prompt names one
   teaches the next agent to create it.
5. Keep `model: inherit` and the `effort:` tier exactly as CAG set them.
6. **Release-guard `bsuk-deploy-verifier.md`.** Its whole job is post-deploy verification and
   IndexNow. Add, as its first body paragraph:
   `> **Inactive until project 6.** BSUK has no host and no domain. Every command in this agent refuses without `BSUK_RELEASE=1` and a real `SITE_URL`. Do not run it, and do not remove this notice — the day it is removed is the day someone submits SITE_URL_PLACEHOLDER to IndexNow.`
   Add the same notice to `bsuk-gsc-analytics.md`, `bsuk-keyword-verifier.md` and
   `bsuk-rank-tracker.md`, worded for data rather than deploy (`no GSC or GA4 data has been
   pulled; every figure is NOT FETCHED until project 6`).

After each batch:
```bash
python3 scripts/marker_check.py 2>&1 | grep '\.claude/agents/' | head -20
```
Expected: no lines. Fix and re-run before starting the next batch.

- [ ] **Step 3: Write `scripts/build_agent_registry.py`**

CAG's registry is hand-maintained and has drifted (68 entries, 67 files). Spec §2 says BSUK's
is *regenerated from the agents actually present*, so it gets a generator:

```python
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
    fm = dict(re.findall(r"^([a-z_]+):\s*(.+)$", m.group(1), re.M))
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
    reg = build()
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
```

`tests/py/test_agent_registry.py`:
```python
import pytest
from build_agent_registry import build, main, parse


def test_registry_matches_the_directory():
    """The drift CAG had (68 entries, 67 files) cannot happen if the registry is derived."""
    assert main(["--check"]) == 0


def test_every_agent_is_named_bsuk(tmp_path):
    for name in build()["agents"]:
        assert name.startswith("bsuk-"), name


def test_parse_rejects_a_name_that_disagrees_with_its_filename(tmp_path):
    p = tmp_path / "bsuk-x.md"
    p.write_text("---\nname: bsuk-y\neffort: high\n---\nbody\n")
    with pytest.raises(ValueError, match="declares name"):
        parse(p)


def test_parse_rejects_a_file_with_no_frontmatter(tmp_path):
    p = tmp_path / "bsuk-x.md"
    p.write_text("no frontmatter here\n")
    with pytest.raises(ValueError, match="frontmatter"):
        parse(p)
```

- [ ] **Step 4: Run**

```bash
python3 scripts/build_agent_registry.py && python3 -m pytest tests/py/test_agent_registry.py -q
python3 scripts/marker_check.py 2>&1 | grep -c '\.claude/agents/'
```
Expected: `wrote data/agent-registry.json — 36 agents`, pytest green, and `0` agent lines
from the marker gate. Add `"agents": "python3 scripts/build_agent_registry.py --check"` to
`package.json` scripts and append `&& npm run agents` to `check:all` in Task 17.

- [ ] **Step 5: Commit (once per batch, three commits)**

```bash
git add -A && git commit -m "agents: batch A re-based to BSUK (13 page builders)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 12: The system skills

**Files:**
- Modify: `data/port-manifest.json`
- Create: `.claude/skills/bsuk-*/SKILL.md`

- [ ] **Step 1: Append 25 `rebase` rows**

`{ "src": ".claude/skills/cag-<n>/SKILL.md", "dst": ".claude/skills/bsuk-<n>/SKILL.md", "mode": "rebase", "notes": "…" }` for:
`gate-integrity`, `learning-loop`, `final-page-pass`, `page-hardening`, `perf-gate`,
`duplicate-content-gate`, `evidence-pass`, `aeo-pass`, `seo-master-checklist`,
`website-health`, `broken-links`, `indexing`, `contact-form`, `footer-agent`,
`site-patterns`, `cta-strategy`, `entity-agent`, `entity-graph`, `youtube`, `google-map`,
`blog-post`, `location-page-builder`, `comparison-page-builder`;
plus the two renames:
`.claude/skills/cags-comprehensive-page-audit-system/SKILL.md` →
`.claude/skills/bsuk-comprehensive-page-audit-system/SKILL.md`, and
`.claude/skills/cag-for-sale-page-builder/SKILL.md` →
`.claude/skills/bsuk-puppy-page-builder/SKILL.md`.
Run the port.

- [ ] **Step 2: Re-base each skill**

Apply the substitution table, then per skill:
1. Rewrite the frontmatter `name:` to `bsuk-<n>` and the `description:` to name BSUK's routes.
2. Every command line the skill tells an agent to run must be a command that exists here.
   Check each one mechanically:
   ```bash
   grep -ho 'python3 scripts/[a-z_]*\.py\|bash scripts/[a-z-]*\.sh\|npm run [a-z:]*' .claude/skills/bsuk-*/SKILL.md | sort -u
   ```
   Every line printed must resolve — `ls scripts/` and `package.json` are the answer. A
   skill that names `scripts/register_skills.py`, `scripts/rebuild_footer.py`,
   `scripts/board_canvas.py` or `scripts/rework_ledger.py` is naming something this port
   did not carry: delete the step and say what replaced it, or say the step arrives with a
   named later project. Do not leave the command in "for later".
3. Cross-skill citations `skills/cag-<n>.md` → `.claude/skills/bsuk-<n>/SKILL.md`.
4. `bsuk-indexing/SKILL.md` and `bsuk-perf-gate/SKILL.md` get the project-6 notice from
   Task 11 Step 2.6 — IndexNow and live PageSpeed are both release-guarded.
5. `bsuk-puppy-page-builder/SKILL.md`: the largest rewrite. Its section order, schema block
   and card contract are written for bird listings. Keep the skill's *shape* (board first,
   then sections, then gates) and replace its content requirements with `rules/puppies.md`'s
   three rules, referencing the pack rather than restating it.

- [ ] **Step 3: Run**

```bash
python3 scripts/marker_check.py 2>&1 | grep -c '\.claude/skills/'
ls .claude/skills | wc -l
```
Expected: `0`, and 52 skill directories (27 generic + 25 system).

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "skills: 25 system skills re-based into the single .claude/skills tree

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 13: Reference docs and `credentials.md`

**Files:**
- Modify: `data/port-manifest.json`
- Create: `docs/reference/{system-registry,quick-start,WORKFLOW,seo-rules,session-log,credentials}.md`

- [ ] **Step 1: Append five `rebase` rows** for the five docs at their same paths, and run
the port. `credentials.md` is written fresh, not ported — CAG's names CAG's secrets.

- [ ] **Step 2: Re-base the five**

| Doc | Lines in | What changes |
|---|---|---|
| `system-registry.md` | 205 | Regenerate the agent list from `data/agent-registry.json` rather than retyping it; the "68 agents" claims become the real count; the script table becomes `ls scripts/`; the data-file table becomes `ls data/`; drop every CAG-only data file |
| `quick-start.md` | 79 | The task→entry-point table is rewritten against BSUK's page types (CLAUDE.md's table is the source); "62 rules" becomes the real `rule-index.json` count; the reference-doc index lists only the six docs that exist here |
| `WORKFLOW.md` | 855 | The 7-sprint model is domain-neutral and stands. H1 → `# BlueStaffyUK — Master Workflow`; the agent count; Sprint 5 "Ship" becomes "Ship — inactive until project 6" with the `BSUK_RELEASE=1` guard; the data-file dependency table is cut to files that exist; the post-deploy checklist keeps its shape under the same inactive notice |
| `seo-rules.md` | 560 | The heaviest re-base (84 bird hits). Delete the whole `## Extended Rules — African Grey–Specific` section — it has no dog analogue and inventing one is a fabricated claim. Delete the dated `## Quick Reference — GSC Priority Pages (2026-04-28)` table (CAG's GSC data). Re-base categories A–J. Fix the count in the H1 to the number of rules that survive, and make `quick-start.md` and CLAUDE.md agree with it — CAG had a three-way disagreement (50 / 62 / 62) and carrying it over would import a known defect |
| `session-log.md` | 47 | Replace the body entirely: two entries, "Project 1 — Foundation (2026-09-15/16) — COMPLETE" pointing at `docs/reports/foundation-gate-report.md`, and "Project 2 — System transfer (2026-09-16)". `## Known Issues` is seeded from the Foundation gate report's "Open items" list, with items 1 and 2 marked closed by this project and 3–8 carried forward |

- [ ] **Step 3: Write `docs/reference/credentials.md`**

Keys only. No value, no fragment of a value, no length hint.
```markdown
# Credentials

Every secret lives in `BSUK/.env`, which is gitignored and never committed. This file says
which keys exist and what reads them. **No value appears here, in any report, or in any
Artifact.** If you need a value, read `.env`; if `.env` is missing, it is rebuilt from the
source named in `docs/superpowers/plans/2026-09-16-system-transfer.md` Task 18.

| Key | Read by | Active? |
|---|---|---|
| `SITE_URL` | `astro.config.mjs`, `scripts/perf_audit.py`, `scripts/health-sweep.sh`, `scripts/indexnow_submit.py` | no — placeholder until project 6 |
| `PUBLIC_FORMSPREE_ID` | `src/components/ContactForm.astro`, `scripts/form_contract_audit.py`, `tests/render/checks/form.ts` | yes |
| `GSC_CLIENT_ID` | `bsuk-gsc-analytics`, `bsuk-keyword-verifier` | no — project 6 |
| `GSC_CLIENT_SECRET` | as above | no — project 6 |
| `GSC_REFRESH_TOKEN` | as above | no — project 6 |
| `GSC_SITE_URL` | as above | no — project 6 |
| `GA4_PROPERTY_ID` | `bsuk-gsc-analytics` | no — project 6 |
| `GA4_CLIENT_ID` | as above | no — project 6 |
| `GA4_CLIENT_SECRET` | as above | no — project 6 |
| `GA4_REFRESH_TOKEN` | as above | no — project 6 |

Not carried over from the retired `bluestaffyuk` MCP server: `GITHUB_TOKEN`,
`GITHUB_OWNER`, `GITHUB_REPO` (this repo has no remote and must not get one) and
`ANTHROPIC_API_KEY` (the session supplies it; a copy in `.env` is a second thing to leak).

A key that is present but empty is a bug, not a default: `scripts/form_contract_audit.py`
and `tests/render/checks/form.ts` both refuse rather than matching nothing.
```

- [ ] **Step 4: Run and commit**

```bash
python3 scripts/marker_check.py 2>&1 | grep -c 'docs/reference/'
git add -A && git commit -m "docs: five reference docs re-based, credentials.md written (keys only)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```
Expected: `0`.

---

### Task 14: Harness — the form contract

**Files:** Modify `tests/render/checks/form.ts`, `tests/render/fixtures/{known_good,known_broken}/form-inquiry-contract.html`, `tests/render/fixtures/form-inquiry-contract-noform.html`

- [ ] **Step 1: Read the endpoint from the environment**

Replace `const FORM_ENDPOINT = 'https://formspree.io/f/xrejpnvn';` with:
```ts
/**
 * Read from the environment, never hard-coded. The id is a credential-adjacent fact that
 * lives in .env (spec §8). Throwing on unset is the point: an empty id makes `action !==
 * endpoint` true on every form, which reads as "every form is broken", or — worse, if the
 * comparison were relaxed — as "every form is fine". A gate that cannot tell those apart
 * must refuse to run. scripts/form_contract_audit.py refuses identically.
 */
const FORMSPREE_ID = process.env.PUBLIC_FORMSPREE_ID;
if (!FORMSPREE_ID) {
  throw new Error(
    'PUBLIC_FORMSPREE_ID is unset — the FORM family cannot judge an endpoint it does not ' +
      'know. Set it in .env (see .env.example) and re-run.',
  );
}
const FORM_ENDPOINT = `https://formspree.io/f/${FORMSPREE_ID}`;
```

- [ ] **Step 2: Replace the seven-field contract with BSUK's, in lock-step with Task 7 Step 4**

```ts
        const ALL: [string, RegExp][] = [
          ['name', /^name$/],
          ['email', /^email$/],
          ['phone', /^phone$/],
          ['location', /^location$/],
          ['puppy', /^puppy$/],
          ['message', /^(message|msg)$/],
        ];
        // As BUILT (dist/uk-blue-staffy-breeders-contact/index.html, 2026-09-16): name,
        // email, puppy and message carry `required`; phone and location do not, by design.
        // Demanding `required` on all six would report the shipped page as broken and teach
        // the next agent to add a constraint the breeder did not ask for.
        const REQUIRED = ['name', 'email', 'puppy', 'message'];
        const SHORT = ['name', 'email', 'message'];
```
and in the field loop, replace `if (!hits.length || !hits.some((c) => c.required))` with
`if (!hits.length || (REQUIRED.includes(name) && !hits.some((c) => c.required)))`.
Add a hidden-field check after it (`_next` and `_subject` must exist, or Formspree has no
redirect and no subject line), and keep the `_gotcha` exclusion exactly as written.
Update `describe:` to `'every non-search form POSTs to the one Formspree endpoint; every in-scope inquiry form carries the six BSUK fields with name/email/puppy/message required, the honeypot and both hidden fields, and refuses to submit empty'`.

- [ ] **Step 3: Rewrite the docstring**

`INQUIRY_FORM_SLUGS`, `fieldChecksSkipped`, `contractFor` and `formExpected` keep their
current BSUK bodies — Foundation already re-based those. Rewrite only the prose: the
"Ported from CAG 2026-09-16" paragraph keeps the finding (14 forms with `data-netlify` and
no action, two POSTing to a missing thank-you page, one retired endpoint) but says "the
source project" instead of naming it, and the "NOT changed in the port, deliberately"
paragraph is deleted — it described exactly the state this task ends.

- [ ] **Step 4: Regenerate the three fixtures from the built contact page**

`known_good/form-inquiry-contract.html`: a search form (skipped), the real contact form
copied out of `dist/uk-blue-staffy-breeders-contact/index.html` with the `data-astro-cid-*`
attributes stripped and `action` set to `https://formspree.io/f/xqegrzka`, and one
newsletter form (`<input type="email" name="email" required>` only). Two examined, zero
defects — the `minExamined: 2` floor stands unchanged.

`known_broken/form-inquiry-contract.html`: the same form with four seeded defects, one per
branch the check reports — `data-netlify` with no `action`; `required` stripped from
`puppy`; `_next` and `_subject` deleted; and a second newsletter whose email input has no
`name`. Comment each defect with the branch it proves.

`fixtures/form-inquiry-contract-noform.html`: replace its parrot H1 and prose with BSUK
copy; it carries no form by design, so nothing else changes.

- [ ] **Step 5: Run and commit**

```bash
npm run build && set -a && . ./.env 2>/dev/null; set +a
PUBLIC_FORMSPREE_ID=xqegrzka npm run test:render:meta 2>&1 | tail -5
```
Expected: the two `form-inquiry-contract` meta tests pass. (Before Task 18, pass the id
inline as shown; after it, `.env` supplies it.)
```bash
git add -A && git commit -m "harness: FORM contract reads PUBLIC_FORMSPREE_ID and holds BSUK's six fields

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 15: Harness — the DUP whitelist and the remaining fixtures

> Execution note (Task 12 quality review): `scripts/dup_content_audit.py` still holds CAG stems (`reserve your bird`, `shipping & delivery`, `shop african greys`, `mark & teri benjamin`), and its header whitelist match at ~line 214 is a substring test, so `contact` whitelists every heading containing it. Re-base the stems to BSUK chrome measured from `dist/` (expected: FAQ, Delivery & Collection, Reserve, Get in Touch, Blue Staffy News) AND switch to exact (normalised) match with a test for the substring trap. Also give the script argparse so `--help` no longer runs a full audit. Then remove the "(arrives in Task 15)" marker in `.claude/skills/bsuk-duplicate-content-gate/SKILL.md` and make its stem list match.

> Execution note (2026-09-16): re-basing `HEADER_WHITELIST`/`HEAD_TERMS` changes the homepage board's `record_hash`. After this task, rerun `python3 scripts/build_page_board.py index` and hand the controller `docs/artifacts/boards/index.html` to republish at the same Artifact URL; expect `board_gate.py index` to drop from 5 to 3 FAILs (the three carried duplicates).

**Files:** Modify `scripts/dup_content_audit.py`, `tests/render/lib/dupCorpus.ts`, `tests/render/fixtures/dup_corpus/*`, and the ~45 remaining marker-carrying files under `tests/render/`

- [ ] **Step 1: Measure BSUK's real chrome, do not guess**

The whitelist exempts the lines that *legitimately* repeat. Derive them from `dist/`:
```bash
python3 - <<'PY'
import collections, itertools, pathlib, re, sys
sys.path.insert(0, "scripts")
from dup_content_audit import words, shingles, norm, MIN_WORDS
pages = {p.parent.name or "index": words(p) for p in pathlib.Path("dist").rglob("index.html")}
c = collections.Counter()
for (a, wa), (b, wb) in itertools.combinations(pages.items(), 2):
    sa, sb = shingles(wa), shingles(wb)
    for s in set(sa) & set(sb):
        c[s] += 1
for s, n in c.most_common(60):
    print("%4d  %s" % (n, s))
PY
```
Every shingle appearing on a large share of the 49 pages is chrome: the header nav, the
footer's five columns, the breadcrumb, the CTA band, the delivery line, the deposit line.
Those become `WHITELIST_SNIPPETS`. A shingle appearing on two or three pages is a real
crossover and must NOT be whitelisted — it is Foundation's migrated-content baseline and
belongs in the gate report, not in the exemption list.

- [ ] **Step 2: Rewrite the four symbol blocks in `scripts/dup_content_audit.py`**

- `WHITELIST_SNIPPETS` (line 29): replace all of CAG's entries with the measured BSUK stems.
  Keep the comment convention — one comment per group naming *why* that group may repeat.
  **The list must hold at least 10 entries** or `dupCorpus.ts`'s floor throws; if the
  measurement yields fewer, that is a real finding (BSUK's chrome is thinner than CAG's) and
  Step 4 lowers the floor rather than padding the list with invented lines.
- `WHITELIST_STEMS` (line 116): no edit — it is derived from `WHITELIST_SNIPPETS`.
- `HEAD_TERMS` (line 171): replace the five African Grey variants with BSUK's:
  `"blue staffy puppies for sale"`, `"blue staffy puppies for sale uk"`,
  `"staffy puppies for sale"`, `"staffordshire bull terrier puppies for sale"`,
  `"blue staffy puppies"`, `"blue staffy"`.
- `HEADER_WHITELIST` (line 180): replace with BSUK's repeated headings — the footer's three
  column headings read off `dist/index.html` (`Blue Staffy UK`, `Quick Pages`,
  `Cities We Serve`), plus `"frequently asked questions"`, `"get in touch"`,
  `"join our newsletter"`, `"lisa bright"`, and the six puppy-name card headings
  `roman`, `byrd`, `ince`, `vennie`, `christa`, `cheryl` — read from `data/puppies.json`,
  with the comment `# sync with data/puppies.json when the litter changes`.
  Also update the module docstring, which names "the CITES notice" and "$185 airport".

- [ ] **Step 3: Replace the three `dup_corpus` siblings with BSUK location pages**

Each sibling exists to collide with a specific `known_broken` fixture, so rewrite them as a
pair. Rename:
- `sibling-congo-african-grey-for-sale.html` → `sibling-blue-staffy-puppies-leeds.html`
- `sibling-hand-raised-african-grey-texas.html` → `sibling-staffy-puppies-glasgow.html`
- `sibling-contraction.html` keeps its name (it exists for the tokeniser, not the content)

and rewrite each body in BSUK voice, preserving the exact property it proves:
`sibling-contraction.html` must still carry `we'd` as a plain apostrophe in one paragraph and
`we&#39;ve` as an entity in another, with the shared runs sitting at 11 and 12 tokens
respectively — count them, do not eyeball them, using the snippet in
`meta.spec.ts`'s `pythonCrossovers()` helper. `sibling-staffy-puppies-glasgow.html` must
carry the whitelisted delivery line between two non-shared lines, and
`known_broken/dup-adjacent-to-whitelist.html` must place two real crossovers (18 and 17
words) directly against it, one on each side, in the same order on both pages.

- [ ] **Step 4: Update `dupCorpus.ts`**

Rewrite the `loadWhitelist()` docstring: the "CITES notice, real reviews" example becomes
"the delivery band, the deposit line, the footer columns, the breadcrumb". Set the floor to
the measured count:
```ts
  const FLOOR = 10;                          // ← the count measured in Task 15 Step 1
  if (out.length < FLOOR) {
```
Rewrite the `siblingSlugsFor()` docstring: the "481 crossovers on 70 pages — bird-card copy"
sentence becomes the measured BSUK figure from Step 1.

- [ ] **Step 5: Re-base every remaining marker-carrying file under `tests/render/`**

```bash
python3 scripts/marker_check.py 2>&1 | grep 'tests/render/' | cut -d: -f1 | sort -u
```
About 45 files. Two classes:
- **Fixture HTML** (~35): the marker is page copy. Rewrite the copy in BSUK voice, keeping
  the fixture's geometry, class names and defect exactly. `schema-sold-not-instock.html` and
  `schema-single-product-offer.html` are regenerated from a real puppy page
  (`dist/available-puppies/roman/index.html`), with GBP prices and `availability` values
  preserved.
- **Check source and lib comments** (~10: `css.ts`, `img.ts`, `layout.ts`, `nav.ts`,
  `schema.ts`, `sem.ts`, `form.ts`, `dupCorpus.ts`, `probes.ts`, `registry.ts`,
  `scorecard.ts`, `global-setup.ts`, `meta.spec.ts`). These carry the *reasoning record* —
  "measured on dist/ between the eggs and congo for-sale pages". Do not delete the record:
  rewrite each to cite the measurement without naming the parrot page, e.g. "measured on the
  source project's two for-sale pages, 2026-09-11". A comment that loses the measurement is
  worse than a marker; a comment that keeps it in BSUK's vocabulary loses nothing.

- [ ] **Step 6: Run and commit**

```bash
python3 scripts/dup_content_audit.py | tail -3
python3 scripts/dup_content_audit.py --headers | tail -3
python3 scripts/marker_check.py | tail -3
```
Expected: the DUP gate prints its BSUK crossover count (non-zero — the migrated baseline);
the marker gate reports `0 problems` for `tests/render/` and `scripts/dup_content_audit.py`.
```bash
git add -A && git commit -m "harness: DUP whitelist re-measured on BSUK chrome; every fixture and comment re-based

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 16: `targets.json`, and the marker gate goes green

**Files:** Modify `tests/render/targets.json`, `tests/py/test_marker_check.py`

- [ ] **Step 1: Rename the page type and check family coverage**

`for-sale` and `puppy` both already exist in `families_by_page_type`; spec §5's "`bird` →
`puppy`" was already done in Foundation. The remaining work is the guard: every family must
examine at least one page.
```bash
python3 - <<'PY'
import json
t = json.load(open("tests/render/targets.json"))
used = {p["page_type"] for p in t["pages"]}
declared = set(t["families_by_page_type"])
print("page types with no target page:", sorted(declared - used))
print("target page types not mapped:", sorted(used - declared))
fam = {f for pt in used for f in t["families_by_page_type"][pt]}
print("families reachable from a real page:", sorted(fam))
PY
```
Expected: both difference sets empty. If `for-sale` were to end up with no target page, the
meta gate fails — that is the rule, not a bug.

- [ ] **Step 2: Add the newly deferred checks**

Add to `deferred_checks`, each with its promotion condition (Task 8 Step 3.5):
```json
    "bottom-bar-under-tabbar": "BSUK ships no mobile tab bar; the check examines zero nodes. Remove this entry when project 3's kit introduces one, i.e. when the scorecard shows this check examining more than zero nodes.",
    "analytics-double-load": "BSUK loads no analytics until project 6 (GA4_MEASUREMENT_ID is unset). Remove this entry when a tag ships, i.e. when the scorecard shows this check examining more than zero nodes."
```
Update `_comment`'s "Ported from CAG 2026-09-16" opening to say "Ported 2026-09-16 from the
source project" — `_comment` is inside `tests/render/`, which the marker gate scans.

- [ ] **Step 3: Flip the marker gate green**

```bash
npm run check:markers
```
Expected: `examined <n> files; 0 problems`. If not, the remaining lines are the work — fix
them, do not add an allowlist. Then delete the `@pytest.mark.xfail` from
`test_the_real_repo_is_clean` (Task 2 Step 6); `strict=True` means the suite goes red the
moment the repo is clean, which is the signal to remove it.

- [ ] **Step 4: Run both render gates**

```bash
set -a; . ./.env 2>/dev/null; set +a
npm run build && npm run test:render:meta 2>&1 | tail -6
npm run test:render:pages 2>&1 | tail -8
node scripts/build_scorecard.mjs --run first
```
Expected: meta green (every registered check fires on its `known_broken` fixture and is
silent on its `known_good`, every family examines ≥1 page, every deferred check still
passes both fixtures and still examines zero). The pages run reports its baseline; compare
it to `docs/reports/foundation-gate-report.md`'s tables and record every row that *moved* —
a DUP count that fell because the whitelist was re-measured is the intended change; a
blocking row that appeared is a regression this task introduced.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "harness: targets.json deferrals, marker gate green, both render gates re-run

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 17: The release guard and the npm scripts

**Files:** Modify `package.json`, `scripts/indexnow_submit.py`, `.gitignore`

- [ ] **Step 1: Guard `indexnow_submit.py`**

Append a `rebase` row for it (Task 8 listed it), run the port, then edit:
- Docstring line 2 → `"""IndexNow submission for BlueStaffyUK — Bing, Yandex, and Google-via-proxy.`
  Delete the `INDEXNOW_KEY = "a1b2c3d4…african grey parrots"` example and the
  `https://african grey parrotsforsale.com/` and `/Users/apple/Downloads/MFS/site2` lines
  from the docstring (they are a previous port's scar tissue, not documentation).
- `HOST = "congoafricangreys.com"` → `HOST = os.environ.get("SITE_URL", "").replace("https://", "").rstrip("/")`.
- First statement of `main()`:
  ```python
  if os.environ.get("BSUK_RELEASE") != "1":
      die("IndexNow is inactive until project 6. Set BSUK_RELEASE=1 only when the site is "
          "live at a real domain; submitting SITE_URL_PLACEHOLDER would publish a dead host.")
  if not HOST or "PLACEHOLDER" in HOST:
      die("SITE_URL is unset or still a placeholder — nothing to submit.")
  ```
- Citation `.claude/skills/cag-indexing/SKILL.md` → `.claude/skills/bsuk-indexing/SKILL.md`.

- [ ] **Step 2: Rewrite `package.json` scripts**

Keep Foundation's eleven entries and add:

```json
    "dates": "python3 scripts/generate_page_dates.py",
    "port": "python3 scripts/port_from_cag.py",
    "agents": "python3 scripts/build_agent_registry.py --check",
    "board:gate": "python3 scripts/board_gate.py",
    "board:approve": "python3 scripts/board_approve.py",
    "board:build": "python3 scripts/build_page_board.py",
    "quality": "python3 scripts/quality_report.py",
    "audit:final": "python3 scripts/final_page_audit.py",
    "audit:harden": "python3 scripts/page_hardening_scan.py",
    "audit:dup": "python3 scripts/dup_content_audit.py",
    "audit:aeo": "python3 scripts/aeo_audit.py",
    "audit:evidence": "python3 scripts/evidence_audit.py --all",
    "audit:form": "python3 scripts/form_contract_audit.py",
    "audit:perf": "python3 scripts/perf_audit.py",
    "sweep": "bash scripts/health-sweep.sh",
    "indexnow": "python3 scripts/indexnow_submit.py",
    "check:markers": "python3 scripts/marker_check.py",
    "check:all": "npm run check:parity && npm run check:redirects && npm run check:schema && npm run check:sitemaps && npm run check:placeholders && npm run check:markers && npm run agents",
```

`indexnow`, `audit:perf --live` and `sweep`'s live block are the only release-guarded
entries; they are listed so they are findable, and each refuses on its own rather than being
hidden from `package.json` — a script that exists and says `REFUSED` teaches more than a
script that is missing.

`tests/render/playwright.config.ts` must load `.env` so `PUBLIC_FORMSPREE_ID` reaches
`form.ts`. Add at the top:
```ts
import { readFileSync, existsSync } from 'node:fs';
// form.ts throws without PUBLIC_FORMSPREE_ID. Loading .env here rather than requiring every
// caller to `set -a; . ./.env` keeps `npm run test:render:*` working as documented.
const envFile = new URL('../../.env', import.meta.url);
if (existsSync(envFile)) {
  for (const line of readFileSync(envFile, 'utf8').split('\n')) {
    const m = /^([A-Z0-9_]+)=(.*)$/.exec(line.trim());
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
}
```

- [ ] **Step 3: `.gitignore`** — add `data/quality/perf/` and `data/boards/inbox/` beside the
existing `data/quality/raw/`. Confirm `.env` is already listed (it is, line 5).

- [ ] **Step 4: Run and commit**

```bash
npm run check:all 2>&1 | grep -E 'examined|problems|FAIL'
python3 scripts/indexnow_submit.py index; echo "exit $?"
```
Expected: every gate `0 problems`; IndexNow prints `REFUSED: IndexNow is inactive…` and
`exit 1`.
```bash
git add -A && git commit -m "scripts: release guard on indexnow, full npm script surface, check:all chain

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 18: Credentials into `.env`

Spec §8, ordered. Nothing in this task may print a secret value.

**Files:** Create `.env` (gitignored); modify `.env.example`

- [ ] **Step 1: Copy the nine values without ever showing one**

```bash
python3 - <<'PY'
import json, pathlib
src = pathlib.Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
env = json.loads(src.read_text())["mcpServers"]["bluestaffyuk"]["env"]
# MCP key -> .env key. Only these nine cross; GITHUB_* and ANTHROPIC_API_KEY do not (spec §8).
MAP = [("GSC_CLIENT_ID_BSUK", "GSC_CLIENT_ID"), ("GSC_CLIENT_SECRET_BSUK", "GSC_CLIENT_SECRET"),
       ("GSC_REFRESH_TOKEN_BSUK", "GSC_REFRESH_TOKEN"), ("GSC_SITE_URL_BSUK", "GSC_SITE_URL"),
       ("GA4_PROPERTY_ID_BSUK", "GA4_PROPERTY_ID"), ("GA4_CLIENT_ID_BSUK", "GA4_CLIENT_ID"),
       ("GA4_CLIENT_SECRET_BSUK", "GA4_CLIENT_SECRET"), ("GA4_REFRESH_TOKEN_BSUK", "GA4_REFRESH_TOKEN"),
       ("FORMSPREE_ENDPOINT_BSUK", "PUBLIC_FORMSPREE_ID")]
out = pathlib.Path(".env")
lines = ["# BSUK credentials. Gitignored. Never commit, never print, never paste.",
         "# Keys are documented in docs/reference/credentials.md. Values live only here.",
         "SITE_URL=https://SITE_URL_PLACEHOLDER"]
missing = []
for mcp_key, env_key in MAP:
    v = env.get(mcp_key, "")
    if not v:
        missing.append(mcp_key)
    lines.append("%s=%s" % (env_key, v))
out.write_text("\n".join(lines) + "\n")
out.chmod(0o600)
# Report the KEYS only. Printing a value here would put it in the terminal scrollback,
# the session transcript, and anything that reads either.
print("wrote .env — %d keys" % (len(MAP) + 1))
print("missing in the MCP block: %s" % (missing or "none"))
PY
```

- [ ] **Step 2: Verify, still without printing a value**

```bash
python3 - <<'PY'
import pathlib
rows = [l.split("=", 1) for l in pathlib.Path(".env").read_text().splitlines()
        if l.strip() and not l.startswith("#")]
need = {"SITE_URL", "GSC_CLIENT_ID", "GSC_CLIENT_SECRET", "GSC_REFRESH_TOKEN", "GSC_SITE_URL",
        "GA4_PROPERTY_ID", "GA4_CLIENT_ID", "GA4_CLIENT_SECRET", "GA4_REFRESH_TOKEN",
        "PUBLIC_FORMSPREE_ID"}
have = {k: bool(v.strip()) for k, v in rows}
assert set(have) == need, ("key mismatch", sorted(set(have) ^ need))
empty = sorted(k for k, ok in have.items() if not ok)
print("examined %d keys; %d empty %s" % (len(have), len(empty), empty or ""))
assert have["PUBLIC_FORMSPREE_ID"], "PUBLIC_FORMSPREE_ID is the one key that must be live now"
PY
git status --porcelain | grep -c '\.env$'; git check-ignore -v .env
```
Expected: `examined 10 keys; 1 empty ['SITE_URL']` (SITE_URL is the placeholder until project
6 — the other nine are non-empty); `0` from the status grep; and `.gitignore:5:.env  .env`
from `check-ignore`. If `.env` appears in `git status`, stop and fix `.gitignore` before
anything else.

- [ ] **Step 3: `.env.example`** — keys with empty values, no hints:
```
SITE_URL=https://SITE_URL_PLACEHOLDER
PUBLIC_FORMSPREE_ID=
GSC_CLIENT_ID=
GSC_CLIENT_SECRET=
GSC_REFRESH_TOKEN=
GSC_SITE_URL=
GA4_PROPERTY_ID=
GA4_CLIENT_ID=
GA4_CLIENT_SECRET=
GA4_REFRESH_TOKEN=
```

- [ ] **Step 4: Re-run the two gates that read the id, and commit**

```bash
npm run audit:form | tail -2 && npm run test:render:meta 2>&1 | tail -3
git add .env.example && git commit -m "env: .env.example lists the nine carried keys; values live only in the gitignored .env

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git show --stat HEAD | grep -c '\.env$'
```
Expected: the form gate now runs without an inline id; the last command prints `0`.

---

### Task 19: Retire the old MCP server

Last, and irreversible. Do not start it until Task 18's verification passed.

- [ ] **Step 1: Back up, then remove the block**

```bash
CFG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
cp "$CFG" "$CFG.bak-$(date +%Y%m%d-%H%M%S)" && ls -1 "$HOME/Library/Application Support/Claude/" | grep bak-
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
d = json.loads(p.read_text())
before = sorted(d["mcpServers"])
assert "bluestaffyuk" in before, "already removed"
del d["mcpServers"]["bluestaffyuk"]
p.write_text(json.dumps(d, indent=2) + "\n")
after = sorted(json.loads(p.read_text())["mcpServers"])   # re-read: proves it still parses
print("servers before:", before)
print("servers after: ", after)
assert after == [s for s in before if s != "bluestaffyuk"], "another server was lost"
print("examined %d servers; 0 problems" % len(after))
PY
```
Expected: `servers after:` lists every server from `servers before:` except `bluestaffyuk`, and the final line reads `examined N servers; 0 problems` with N one less than before. If the assert
about another server fires, restore from the `.bak-` file and investigate before retrying.

- [ ] **Step 2: Delete the server**

```bash
du -sh ~/bsuk-mcp-server && rm -rf ~/bsuk-mcp-server && ls -d ~/bsuk-mcp-server 2>&1
```
Expected: the size (about 59M), then `ls: /Users/apple/bsuk-mcp-server: No such file or directory`.

- [ ] **Step 3: Record it**

Nothing in the repo changes, so there is nothing to commit here — note the timestamped
backup's filename in Task 20's report, and add a line to `docs/reference/session-log.md`'s
project-2 entry. Commit that with Task 20.

---

### Task 20: Close-out — run everything twice, the gate report, the Artifacts

> Execution note (2026-09-16): report the proving board's approval state from `data/boards/index.json` `approval`, not from ledger slot emptiness (the ledger row is all-empty by design until project 3). List the three carried header duplicates by heading and page.

- [ ] **Step 1: Full run, twice**

```bash
set -a; . ./.env; set +a
for i in 1 2; do echo "=== RUN $i ==="; \
  npm run build 2>&1 | tail -1 && npm run check:all && npm run test:py && \
  python3 scripts/port_from_cag.py && python3 scripts/board_gate.py index && \
  npm run quality | tail -4; \
done 2>&1 | tee docs/reports/system-transfer-run.log | grep -E 'RUN|examined|problems|FAIL|passed|error'
npm run test:render:meta && npm run test:render:pages && node scripts/build_scorecard.mjs --run first
npm run test:render:meta && npm run test:render:pages && node scripts/build_scorecard.mjs --run first
```
Expected, identical on both runs: every gate `0 problems`; pytest green;
`port_from_cag.py` reporting `missing 0` and — this is the spec §9 line to check by eye —
`skipped-existing <the number of rebase rows>` with `applied` equal only to the `copy` and
`rename` count, never re-copying a re-based file; `board_gate.py index` at `0 FAIL`.

- [ ] **Step 2: Write `docs/reports/system-transfer-gate-report.md`**

By hand from the run outputs, mirroring `docs/reports/foundation-gate-report.md`'s
structure: a header naming the project, date, branch and spec; a paragraph telling the
reader how to read the two severities; then, with real numbers —

`## Port` (rows by mode; applied / skipped-existing / deferred / missing; the second-run
confirmation that no `rebase` row was re-applied) · `## Marker gate` (files examined,
problems, and the Task 2 baseline it came down from) · `## Board` (the homepage board's
counts, FAIL/WARN, and Artifact URL) · `## Python gates` (parity, redirects, schema,
sitemaps, placeholders, markers, agents — examined and problems each) · `## Ported gate
scripts` (final_page_audit, page_hardening_scan, aeo, evidence, form_contract, dup,
quality_report, health-sweep — examined, problems, and whether the count is a
migrated-content baseline) · `## Pytest` (count, and the new files' share) ·
`## Render meta` (families registered vs wired; deferred checks and their promotion
conditions) · `## Render pages` (blocking and advisory by check id, **as a diff against the
Foundation baseline** — every row that moved, with its cause) · `## Rules and ledger`
(10 packs, rule counts by `enforced`, judgment cap) · `## Agents and skills` (36 agents,
52 skills, 41 deferred rows) · `## Credentials and MCP` (nine keys present, `.env`
gitignored and absent from `git status`, the backup filename, the server deleted — **no
values**) · `## Second-run confirmation` (identical: yes/no) · `## Definition of done —
spec §9` (the nine bullets, ticked line by line) · `## Out of scope` (restate spec §10) ·
`## Open items for later projects` (carry forward Foundation's items 3–8, mark its items 1
and 2 closed by this project, and add anything this port deferred).

- [ ] **Step 3: Publish the three Artifacts**

```bash
python3 scripts/build_spec_artifact.py docs/superpowers/specs/2026-09-16-system-transfer-design.md docs/artifacts/bsuk-system-transfer-spec.html "BSUK System Transfer Spec" "BlueStaffyUK rebuild · Project 2 of 6" "System transfer design spec" "BlueStaffyUK Rebuild — Project 2 of 6: System Transfer"
python3 scripts/build_spec_artifact.py docs/superpowers/plans/2026-09-16-system-transfer.md docs/artifacts/bsuk-system-transfer-plan.html "BSUK System Transfer Plan" "BlueStaffyUK rebuild · Project 2 of 6" "System transfer implementation plan" "BlueStaffyUK Rebuild — Project 2 of 6: Implementation Plan"
python3 scripts/build_spec_artifact.py docs/reports/system-transfer-gate-report.md docs/artifacts/bsuk-system-transfer-gate-report.html "BSUK System Transfer Gate Report" "BlueStaffyUK rebuild · Project 2 of 6" "System transfer gate report" "BlueStaffyUK Rebuild — Project 2 of 6: Gate Report"
```
Publish each with the Artifact tool, favicon 🐾. Before publishing the gate report, read it
end to end and confirm no credential value, no fragment of one, and no path under
`~/Library/` containing a secret appears anywhere in it.

- [ ] **Step 4: Final commit and the invariants**

```bash
git add -A && git commit -m "docs: system transfer gate report and artifact sources

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git remote -v                       # must print nothing
git log --oneline | head -25
git log --format=%B -n 25 | grep -c 'Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>'
git status --porcelain | grep -c '\.env$'   # must print 0
ls -d ~/bsuk-mcp-server 2>&1                # must say No such file or directory
python3 -c "import json,pathlib; json.loads((pathlib.Path.home()/'Library/Application Support/Claude/claude_desktop_config.json').read_text()); print('desktop config parses')"
```

---

## Self-review

**Spec coverage.** §1 decisions → Tasks 1 (manifest method), 3/12 (single skill tree),
9 (rule ledger), 17 (deploy inactive), 18 (credentials), 14 (Formspree), 19 (old MCP).
§2 layout → every task's file list; the "not ported by name" list is the manifest's absence
rule in Task 1 Step 6. §3 curated agents and skills → Tasks 11, 12, with the deferred rows in
Task 3. §4 manifest, port script and gate → Tasks 1, 2. §5 harness re-base → Tasks 14, 15,
16. §6 board → Tasks 4, 5. §7 CLAUDE.md and rules → Tasks 10, 9. §8 credentials and MCP →
Tasks 18, 19. §9 definition of done → Task 20 Steps 1 and 2.

**Ordering.** The gate (2) precedes every re-base so each task can prove itself. `copy` rows
(3) precede `rebase` rows so the port script is exercised on the easy case first. The board
(4) precedes the proving board (5), which needs `dist/`. Gate scripts (6–8) precede the rule
ledger (9), because `quality_report.py` §5 is what finds the broken `test:` links. CLAUDE.md
(10) precedes the agents and skills (11, 12) that cite it. The harness (14–16) comes after
the scripts because `form_contract_audit.py` and `form.ts` must be written to the same
contract, and `dupCorpus.ts` reads `dup_content_audit.py`. Credentials (18) precede the MCP
removal (19) so the values are safe before the source is destroyed, and both come after
everything that might need to be re-run.

## Deviations from the spec, recorded

1. **`board_canvas.py` is an undeclared dependency.** Spec §2 excludes it, but
   `board_approve.py` imports `file_token` from it and `build_page_board.py` imports
   `unfile_token`. Task 4 Step 4.5 inlines both into `pageboard.py` (eight lines) rather than
   porting the 
   canvas module.
2. **`perf_audit.py` needs `scripts/lighthouse/agentic-{mobile,desktop}.mjs`**, which spec §2
   does not list. Task 8 Step 1 adds two `copy` rows, with a fallback if they are absent.
3. **`health-sweep.sh` calls two unported scripts** (`register_skills.py`, which spec §1
   explicitly retires, and `verify_model_tiers.sh`). Task 8 Step 5 deletes both blocks and
   substitutes the marker gate and the registry `--check`.
4. **`final_page_audit.py` cannot fail.** CAG's `main()` never calls `sys.exit`, so it returns
   0 on FAIL. Spec §4 fixes the gate output shape and Foundation's gates exit non-zero; Task 6
   Step 2.13 adds the exit.
5. **Board path.** Spec §2 says `data/boards/<slug>.json`; CAG uses
   `data/pages/<slug>/board.json`. Task 4 Step 4.2 re-bases to the spec's path and adds a
   `/`→`--` slug transform CAG never needed, because BSUK has nested slugs.
6. **Spec §5 under-counts the harness re-base.** It names six fixtures; the marker gate's
   scan of `tests/render/` finds markers in about 57 files, including ten check-source and
   lib comment blocks that carry the harness's reasoning record. Task 15 Step 5 re-bases all
   of them and rewrites — rather than deletes — the provenance comments.
7. **`scripts/dup_content_audit.py` is not in spec §4's scan roots**, yet Task 15 re-measures
   its whitelist and nothing else would catch a parrot stem left in it. Task 2 adds it to
   `FIXED_ROOTS`. This strictly widens the gate, which is safe; narrowing it would not be.
8. **Spec §3's agent count.** The prose says "about 25 agents"; the list it prints names 36.
   Task 11 ports all 36. Similarly "the 14 `framework-*` skills": CAG has 12 `framework-*`
   directories, so Task 3 ports 12 and counts `framework-agent` (an agent, not a skill) and
   `framework-heading-hierarchy` toward the 14.
9. **`test_page_board.py` cannot be ported whole.** 183 of CAG's tests assert against its
   104-page `dist/`, its twelve-page component ledger, its ontology contents, and
   `board_canvas.py`. Task 4 Step 7 names exactly which groups are kept, which are dropped
   and why, and which two are replaced by BSUK equivalents.
10. **CAG's own inconsistencies are not carried over.** Its agent registry had 68 entries over
    67 files (Task 11 Step 3 derives the registry so this cannot recur) and its SEO rule count
    disagreed three ways, 50 / 62 / 62 (Task 13 Step 2 fixes the count and makes the three
    citations agree).
11. **`judgment_cap` drops from 12 to 9.** Spec §7 drops three judgment rules (CAG's 2, 11 and
    12). Task 9 Step 3 lowers the cap with them; leaving it at 12 would silently license three
    new ungated rules.
