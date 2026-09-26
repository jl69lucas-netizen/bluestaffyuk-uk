"""`scripts/render_baseline.py` — the per-family baseline table must be derived, not typed.

The scorecard JSON in `data/quality/scorecards/` records `details` rows by check id and
carries NO severity field, so blocking-vs-advisory can only be resolved by reading the
`severity:` literal out of `tests/render/checks/*.ts`. That coupling is exactly why the table
was hand-typed once and exactly why it needs a test: the script must keep agreeing with both
sources, and the committed report must keep agreeing with the script.
"""
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/render_baseline.py"
REAL_SCORECARDS = ROOT / "data/quality/scorecards"
# The LIVE baseline — the one the script defaults to and `npm run baseline` checks. Project
# 2's and project 3's reports are published records of finished runs and are never
# regenerated, so neither is what "the committed report matches the real scorecards" can mean
# any more (Known Issue 25).
REAL_REPORT = ROOT / "docs/reports/render-baseline-project4.md"
START = "<!-- generated:start -->"
END = "<!-- generated:end -->"


def _generated_block(report):
    """The text between the markers, stripped — empty for a report whose run has not happened."""
    text = report.read_text(encoding="utf-8")
    return text.split(START, 1)[1].split(END, 1)[0].strip()


# A project's baseline file is opened with an EMPTY generated block and filled by that
# project's close-out run (project 4: Task 19). Until then there is no table to compare, and
# failing on "stale" would be failing on a report nobody has written yet — which is exactly
# the second-run failure Known Issue 25 recorded. Once the block is filled, both tests below
# hold it to the scorecards on every run.
NOT_YET_GENERATED = pytest.mark.skipif(
    not REAL_REPORT.is_file() or not _generated_block(REAL_REPORT),
    reason=f"{REAL_REPORT.name} has no generated block yet — its close-out run fills it",
)


def run(*args, expect=None):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )
    if expect is not None:
        assert proc.returncode == expect, f"exit {proc.returncode}\n{proc.stdout}\n{proc.stderr}"
    return proc


def _scorecard(slug, date, rows):
    return {
        "slug": slug,
        "date": date,
        "page_type": "interior",
        "run": "first",
        "harness_version": "2.0.0",
        "details": [
            {"viewport": 1280, "checkId": cid, "count": n, "message": "x"} for cid, n in rows
        ],
    }


@pytest.fixture
def fake(tmp_path):
    """Two dates, three checks across three families, two of them blocking."""
    cards = tmp_path / "scorecards"
    cards.mkdir()
    checks = tmp_path / "checks"
    checks.mkdir()
    (checks / "img.ts").write_text(
        "export const a = {\n  id: 'img-alt',\n  family: 'IMG',\n  severity: 'blocking',\n};\n"
    )
    (checks / "css.ts").write_text(
        "export const b = {\n  id: 'css-resolves',\n  family: 'CSS',\n  severity: 'advisory',\n};\n"
        "export const c = {\n  id: 'css-dead',\n  family: 'CSS',\n  severity: 'blocking',\n};\n"
    )
    for slug, rows in (
        ("alpha", [("img-alt", 2), ("css-resolves", 1)]),
        ("beta", [("css-resolves", 3), ("css-dead", 1)]),
    ):
        (cards / f"{slug}-2026-09-17.json").write_text(
            json.dumps(_scorecard(slug, "2026-09-17", rows))
        )
    (cards / "alpha-2026-09-16.json").write_text(
        json.dumps(_scorecard("alpha", "2026-09-16", [("img-alt", 2), ("css-resolves", 1)] * 2))
    )
    return cards, checks


def args(fake, *rest):
    cards, checks = fake
    return ["--scorecards-dir", str(cards), "--checks-dir", str(checks), *rest]


def test_the_script_exists_and_is_runnable():
    assert SCRIPT.is_file()
    assert run("--help", expect=0).stdout


def test_severity_comes_from_the_checks_dir_not_the_json(fake):
    out = run(*args(fake), expect=0).stdout
    # img-alt is blocking on one page; css-resolves advisory on two; css-dead blocking on one.
    assert "| IMG | 1 | 0 | 1 |" in out
    assert "| CSS | 1 | 2 | 2 |" in out


def test_totals_row_sums_every_family(fake):
    out = run(*args(fake), expect=0).stdout
    assert "| **Total** | **2** | **2** | **2** |" in out


def test_rows_by_check_lists_every_check_that_reported(fake):
    out = run(*args(fake), expect=0).stdout
    assert "`css-resolves` 2" in out
    assert "`img-alt` 1" in out
    assert "`css-dead` 1" in out


def test_default_date_is_the_latest_present(fake):
    cards, _ = fake
    out = run(*args(fake), expect=0).stdout
    assert "2026-09-17" in out
    assert "2026-09-16" not in out.split("Rows by check")[0]


def test_an_explicit_date_selects_that_run(fake):
    out = run(*args(fake, "--date", "2026-09-16"), expect=0).stdout
    assert "Scorecard run 2026-09-16" in out
    # the 09-16 fixture doubles alpha's rows: 2 blocking + 2 advisory on its one page
    assert "| **Total** | **2** | **2** | **1** |" in out


def test_an_unknown_date_is_an_error_not_an_empty_table(fake):
    proc = run(*args(fake, "--date", "1999-01-01"))
    assert proc.returncode != 0
    assert "1999-01-01" in proc.stdout + proc.stderr


def test_compare_prints_per_check_deltas(fake):
    full = run(*args(fake, "--compare", "2026-09-16"), expect=0).stdout
    out = full.split("per-check row deltas", 1)[1]
    assert "img-alt 2 -> 1" in out
    assert "css-dead 0 -> 1" in out
    assert "css-resolves" not in out, "a check whose count did not move is not a delta"


def test_write_replaces_only_the_generated_block(tmp_path, fake):
    report = tmp_path / "report.md"
    report.write_text(f"# Title\n\nhand prose\n\n{START}\nSTALE\n{END}\n\ntrailing prose\n")
    run(*args(fake, "--write", str(report)), expect=0)
    text = report.read_text()
    assert "hand prose" in text and "trailing prose" in text
    assert "STALE" not in text
    assert "| **Total** | **2** | **2** | **2** |" in text
    assert text.count(START) == 1 and text.count(END) == 1


def test_write_refuses_a_report_with_no_markers(tmp_path, fake):
    report = tmp_path / "bare.md"
    report.write_text("# Title\n\nno markers here\n")
    proc = run(*args(fake, "--write", str(report)))
    assert proc.returncode != 0
    assert "no markers here" in report.read_text()


def test_check_is_green_right_after_a_write(tmp_path, fake):
    report = tmp_path / "report.md"
    report.write_text(f"# t\n\n{START}\nSTALE\n{END}\n")
    run(*args(fake, "--write", str(report)), expect=0)
    run(*args(fake, "--check", "--write", str(report)), expect=0)


def test_out_creates_a_report_that_does_not_exist(tmp_path, fake):
    report = tmp_path / "nested" / "render-baseline-new.md"
    run(*args(fake, "--out", str(report)), expect=0)
    text = report.read_text()
    assert text.count(START) == 1 and text.count(END) == 1
    assert "| **Total** | **2** | **2** | **2** |" in text
    run(*args(fake, "--check", "--out", str(report)), expect=0)


def test_check_on_a_missing_report_is_stale_not_a_crash(tmp_path, fake):
    report = tmp_path / "absent.md"
    proc = run(*args(fake, "--check", "--out", str(report)))
    assert proc.returncode == 1, proc.stderr
    assert "does not exist" in proc.stdout
    assert not report.exists(), "--check must never create the report"


def test_the_default_report_is_project_4s():
    src = SCRIPT.read_text(encoding="utf-8")
    assert 'REPORT = ROOT / "docs/reports/render-baseline-project4.md"' in src


def test_check_exits_one_when_the_block_is_stale(tmp_path, fake):
    report = tmp_path / "report.md"
    report.write_text(f"# t\n\n{START}\nSTALE\n{END}\n")
    proc = run(*args(fake, "--check", "--write", str(report)))
    assert proc.returncode == 1
    assert "STALE" in report.read_text(), "--check must not rewrite the report"


@pytest.mark.skipif(
    not REAL_SCORECARDS.is_dir() or not any(REAL_SCORECARDS.glob("*.json")),
    reason="no scorecards built",
)
@NOT_YET_GENERATED
def test_the_committed_report_matches_the_real_scorecards():
    run("--check", expect=0)


@pytest.mark.skipif(
    not REAL_SCORECARDS.is_dir() or not any(REAL_SCORECARDS.glob("*.json")),
    reason="no scorecards built",
)
@NOT_YET_GENERATED
def test_the_reports_total_row_equals_the_real_scorecard_sums():
    latest = sorted(p.stem[-10:] for p in REAL_SCORECARDS.glob("*.json"))[-1]
    total = 0
    for card in REAL_SCORECARDS.glob(f"*-{latest}.json"):
        total += len(json.loads(card.read_text())["details"])
    body = REAL_REPORT.read_text()
    row = [ln for ln in body.splitlines() if ln.startswith("| **Total**")]
    assert len(row) == 1, "the report must carry exactly one generated Total row"
    blocking, advisory = (int(c.strip().strip("*")) for c in row[0].split("|")[2:4])
    assert blocking + advisory == total, (
        f"report Total {blocking}+{advisory} != {total} detail rows in the {latest} scorecards"
    )


# ── Per-page severity: a `new-pages` promotion (tests/render/targets.json) blocks on a
# project 5 page, so the baseline must classify it there as blocking, exactly as
# tests/render/pages.spec.ts does through tests/render/lib/promotions.ts. ────────────────────

sys.path.insert(0, str(ROOT / "scripts"))
import family_rules as FR  # noqa: E402
import render_baseline as RB  # noqa: E402

RULE = {
    "page_types": list(FR.NEW_FAMILY_PAGE_TYPES),
    "built_before": sorted(FR.BUILT_BEFORE_SYSTEM_GAPS),
    "excluded_prefix": "_",
    "or_board_approved": True,
}


def test_the_python_mirror_agrees_with_family_rules_wherever_there_is_evidence():
    """With rebuilt/board evidence present, the mirror answers family_rules' own question."""
    slugs = sorted(FR.BUILT_BEFORE_SYSTEM_GAPS) + ["_demo", "blue-staffy-puppies-york", "blue-staffy-vs-pitbull"]
    for slug in slugs:
        for page_type in ("location", "comparison", "blog", "home", "interior"):
            want = page_type in FR.NEW_FAMILY_PAGE_TYPES and FR.is_new_page(slug)
            assert RB.is_new_page(slug, page_type, RULE, {slug}, set()) is want, (slug, page_type)
            assert RB.is_new_page(slug, page_type, RULE, set(), {slug}) is want, (slug, page_type)


def test_the_mirror_needs_rebuilt_or_an_approved_board():
    york = "uk-locations/blue-staffy-puppies-york"
    assert RB.is_new_page(york, "location", RULE, set(), {"uk-locations--blue-staffy-puppies-york"})
    assert RB.is_new_page(york, "location", RULE, set(), {"blue-staffy-puppies-york"})
    assert RB.is_new_page(york, "location", RULE, {"blue-staffy-puppies-york"}, set())
    # a legacy city page: no board, not rebuilt
    assert not RB.is_new_page(york, "location", RULE, set(), set())
    assert not RB.is_new_page(york, "location", {**RULE, "or_board_approved": False}, set(),
                              {"uk-locations--blue-staffy-puppies-york"})


def test_approved_boards_reads_approval_or_approval_previous(tmp_path):
    (tmp_path / "uk-locations--a.json").write_text(json.dumps({"approval": {"approved_at": "x"}}))
    (tmp_path / "b.json").write_text(json.dumps({"approval": None, "approval_previous": {"x": 1}}))
    (tmp_path / "c.json").write_text(json.dumps({"approval": None}))
    assert RB.approved_boards(tmp_path) == {"uk-locations--a", "b"}
    assert RB.approved_boards(tmp_path / "missing") == set()


@pytest.fixture
def promoted(tmp_path):
    """One advisory check promoted to `new-pages`, reported on a new city page (approved
    board) and on a legacy city page (no board)."""
    cards = tmp_path / "scorecards"
    cards.mkdir()
    checks = tmp_path / "checks"
    checks.mkdir()
    (checks / "layout.ts").write_text(
        "export const a = {\n  id: 'layout-promoted',\n  family: 'LAYOUT',\n  severity: 'advisory',\n};\n"
    )
    boards = tmp_path / "boards"
    boards.mkdir()
    (boards / "uk-locations--blue-staffy-puppies-york.json").write_text(json.dumps({"approval": {"a": 1}}))
    rebuilt = tmp_path / "rebuilt.json"
    rebuilt.write_text("[]")
    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps({
        "new_page_rule": RULE,
        "promotions": {"layout-promoted": {"scope": "new-pages", "since": "2026-09-26",
                                           "cluster_cleared": "x", "false_reports": 0}},
    }))
    for slug in ("uk-locations/blue-staffy-puppies-york", "uk-locations/blue-staffy-puppies-leeds"):
        card = _scorecard(slug, "2026-09-26", [("layout-promoted", 1)])
        card["page_type"] = "location"
        (cards / f"{slug.replace('/', '__')}-2026-09-26.json").write_text(json.dumps(card))
    return ["--scorecards-dir", str(cards), "--checks-dir", str(checks), "--targets", str(targets),
            "--rebuilt", str(rebuilt), "--boards-dir", str(boards)]


def test_a_promoted_check_on_a_new_page_is_counted_blocking(promoted):
    out = run(*promoted, expect=0).stdout
    # york (approved board) -> blocking; leeds (legacy, no board) -> advisory
    assert "| LAYOUT | 1 | 1 | 2 |" in out
