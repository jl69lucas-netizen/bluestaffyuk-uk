"""Stale instructions are wrong instructions (CAG parity audit, Wave 1 item 6).

The agents that build project 5 read CLAUDE.md, the rule packs, WORKFLOW.md and the gate
scripts' own messages as fact. The 2026-09-26 audit found seven places where those texts
had drifted from the repo. Each test below pins one of them to the thing it describes, so
the next drift fails here instead of misleading a builder:

  1. CLAUDE.md's `check:all` sentence lists the chain package.json really runs;
  2. a rule pack names no public asset that is not in public/;
  3. a WORKFLOW.md ledger row that says "empty today" is empty;
  4. a quality script or ledger names no script that does not exist, unless it says so;
  5. Sprint 6 writes the lessons where lessons are really kept, and every gate report has
     that section;
  6. (tests/py/test_rules_index.py) working rule 13's ledger row names its render check;
  7. nothing promises an LLM Visibility score out of 10 — the intel file has one engine
     and a `bsuk_cited` flag, not a score.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLAUDE_MD = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
WORKFLOW = (ROOT / "docs/reference/WORKFLOW.md").read_text(encoding="utf-8")
SCRIPTS = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]


# 1 ─────────────────────────────────────────────────────────────────────────────────────
CHAIN_SENTENCE = re.compile(r"`check:all`\s+chains\s+(.*?),\s+in\s+that\s+order", re.S)


def test_claude_md_lists_the_check_all_chain_package_json_runs():
    m = CHAIN_SENTENCE.search(CLAUDE_MD)
    assert m, "CLAUDE.md lost its `check:all` chains … in that order sentence"
    documented = re.findall(r"`([\w:-]+)`", m.group(1))
    # only the `npm run X` steps of check:all are read; a bare command in the chain is not listed
    chain = re.findall(r"npm run ([\w:-]+)", SCRIPTS["check:all"])
    assert documented == chain, (
        f"CLAUDE.md lists {documented}\n package.json check:all runs {chain}\n"
        "Adding a check to check:all updates package.json, tests/py/test_package_scripts.py "
        "(expected) and this CLAUDE.md sentence in the same commit.")


def test_the_chain_sentence_survives_any_re_wrap():
    for text in ("`check:all` chains `check:parity` and `agents`,\nin that order (pinned).",
                 "`check:all`\nchains `check:parity` and `agents`, in that order (pinned).",
                 "`check:all` chains `check:parity` and `agents`, in\nthat\norder (pinned)."):
        m = CHAIN_SENTENCE.search(text)
        assert m, text
        assert re.findall(r"`([\w:-]+)`", m.group(1)) == ["check:parity", "agents"], text


# 2 ─────────────────────────────────────────────────────────────────────────────────────
ASSET = re.compile(r"[\"'`( ](/[A-Za-z0-9_./-]+\.(?:png|webp|svg|jpe?g|avif|gif|ico))\b")


def test_no_rule_pack_names_a_public_asset_that_does_not_exist():
    bad = []
    for f in sorted((ROOT / "rules").glob("*.md")) + [ROOT / "CLAUDE.md"]:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for path in ASSET.findall(line):
                if not (ROOT / "public" / path.lstrip("/")).exists():
                    bad.append(f"{f.relative_to(ROOT)}:{n} {path}")
    assert bad == [], bad


# 3 ─────────────────────────────────────────────────────────────────────────────────────
LEDGER_ROW = re.compile(r"^\| `(data/quality/[\w-]+\.json)` \|.*\bempty today\b", re.M)


def _entries(doc):
    """The list a ledger file keeps its records in."""
    for key in ("claims", "windows", "entries", "rows"):
        if key in doc:
            return doc[key]
    raise AssertionError(f"no known record list in {sorted(doc)}")


#: A row that counts its records ("two windows since …") must count them right. The rework
#: ledger was the only row "empty today" until the 2026-09-27 learning loop appended two windows,
#: so the guard now reads both kinds and refuses only when it reads neither.
LEDGER_COUNTED = re.compile(r"^\| `(data/quality/[\w-]+\.json)` \|.*\b(one|two|three|four|five|six|"
                            r"seven|eight|nine|ten) (?:windows|claims|entries|rows)\b", re.M)
NUMBER = {w: i for i, w in enumerate("one two three four five six seven eight nine ten".split(), 1)}


def test_a_ledger_workflow_calls_empty_is_empty():
    rows = LEDGER_ROW.findall(WORKFLOW)
    counted = LEDGER_COUNTED.findall(WORKFLOW)
    assert rows or counted, "WORKFLOW.md describes no ledger's size — the guard would read nothing"
    full = [p for p in rows if _entries(json.loads((ROOT / p).read_text(encoding="utf-8")))]
    assert full == [], f"WORKFLOW.md calls these ledgers empty, and they are not: {full}"
    wrong = [(p, n) for p, n in counted
             if len(_entries(json.loads((ROOT / p).read_text(encoding="utf-8")))) != NUMBER[n]]
    assert wrong == [], f"WORKFLOW.md miscounts these ledgers: {wrong}"


# 4 ─────────────────────────────────────────────────────────────────────────────────────
SCRIPT_REF = re.compile(r"scripts/[a-z0-9_]+\.py")
HONEST = re.compile(r"(?i)not ported|did not cross|source repo")


def test_quality_files_name_only_scripts_that_exist():
    files = [ROOT / "scripts/quality_report.py"] + sorted((ROOT / "data/quality").glob("*.json"))
    bad = []
    for f in files:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for ref in SCRIPT_REF.findall(line):
                if not (ROOT / ref).exists() and not HONEST.search(line):
                    bad.append(f"{f.relative_to(ROOT)}:{n} {ref}")
    assert bad == [], ("these name a script that does not exist, as if it did — say it was "
                       "not ported, or point at what really does the job:\n  " + "\n  ".join(bad))


# 5 ─────────────────────────────────────────────────────────────────────────────────────
GATE_REPORTS = sorted((ROOT / "docs/reports").glob("*-gate-report.md"))
LESSONS_H2 = re.compile(r"^## (?:Open items|Known Issues open)", re.M)


def test_sprint_6_writes_the_lessons_into_the_gate_report():
    line = next((l for l in WORKFLOW.splitlines() if "Write the lessons" in l), None)
    assert line, "WORKFLOW.md Sprint 6 lost its lessons step"
    assert "docs/reports/" in line and "gate-report" in line, line


@pytest.mark.parametrize("report", GATE_REPORTS, ids=lambda p: p.stem)
def test_every_gate_report_keeps_its_lessons(report):
    assert LESSONS_H2.search(report.read_text(encoding="utf-8")), (
        f"{report.name} has neither a `## Open items` nor a `## Known Issues open` section — "
        "Sprint 6 writes the lessons there")


def test_there_are_gate_reports():
    assert len(GATE_REPORTS) >= 5


# 7 ─────────────────────────────────────────────────────────────────────────────────────
SCORE_OUT_OF_10 = re.compile(r"(?i)LLM Visibility[^\n]{0,60}?(?:\b0\s*[–-]\s*10\b|\d\s*/\s*10\b|\bX\s*/\s*10\b)")


def test_nothing_promises_an_llm_visibility_score_out_of_ten():
    files = (sorted((ROOT / ".claude").rglob("*.md")) + sorted((ROOT / "docs/reference").glob("*.md"))
             + sorted((ROOT / "rules").glob("*.md")) + [ROOT / "CLAUDE.md"])
    bad = [f"{f.relative_to(ROOT)}:{n}  {l.strip()[:100]}" for f in files
           for n, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1) if SCORE_OUT_OF_10.search(l)]
    assert bad == [], ("no script computes an LLM Visibility score: the intel file "
                       "(docs/research/llm-intel/<slug>-<date>.json) records one engine's answer and "
                       "`bsuk_cited`. Report cited / not cited / NOT FETCHED:\n  " + "\n  ".join(bad))


def test_the_score_lint_fires():
    for line in ('- FILE → report the score (e.g., "LLM Visibility: 3/10 — BSUK is cited")',
                 "- LLM Visibility: [0–10 score | \"not measured\"]",
                 "### LLM Visibility Score: [X/10 | \"not measured\"]"):
        assert SCORE_OUT_OF_10.search(line), line
    assert not SCORE_OUT_OF_10.search("- LLM Visibility: [cited | not cited | NOT FETCHED]")
