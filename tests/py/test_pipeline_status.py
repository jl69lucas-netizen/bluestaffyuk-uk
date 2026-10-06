"""pipeline_status.py: a row is done only when its file proves it; the first unproved row is now."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import pipeline_status as PS  # noqa: E402

SLUG = "demo-city"


def _write(root, rel, obj):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj) if not isinstance(obj, str) else obj, encoding="utf-8")


def _tree(tmp_path, upto_stop):
    _write(tmp_path, f"data/page-runs/{SLUG}.json", {"slug": SLUG, "session_open": {}})
    _write(tmp_path, f"data/queries/{SLUG}.json", {"route": "/x/"})
    _write(tmp_path, f"data/queries/raw/{SLUG}/serp_google.json", {})
    rb = {"keywords": [1], "entities": [1], "approval": {"approved_on": "d"} if upto_stop >= 1 else None}
    _write(tmp_path, f"data/research-boards/{SLUG}.json", rb)
    _write(tmp_path, f"data/outlines/{SLUG}.json", {"approval": {"approved_on": "d"} if upto_stop >= 2 else None})
    _write(tmp_path, f"data/boards/{SLUG}.json", {"approval": {"approved_at": "d"} if upto_stop >= 3 else None})
    _write(tmp_path, "data/facts/rebuilt.json", [])
    _write(tmp_path, f"src/pages/x/{SLUG}.astro", "<div data-city-scaffold></div>")
    (tmp_path / "docs/reference/answer-board/answers").mkdir(parents=True)
    (tmp_path / "docs/reference/answer-board/batches").mkdir(parents=True)
    if upto_stop >= 4:
        _write(tmp_path, f"docs/reference/answer-board/answers/b-asset-gate-{SLUG}-d.md", "x")


def test_each_stop_moves_now_one_row(tmp_path):
    for stop, now in ((0, 8), (1, 9), (2, 10), (3, 11), (4, 12)):
        root = tmp_path / str(stop)
        _tree(root, stop)
        s = PS.status(SLUG, root)
        assert s["now"] == now, (stop, s["now"])
        assert s["stops_done"] == stop
        assert [r["state"] for r in s["rows"]].count("now") == 1


def test_a_proved_row_after_now_is_still_todo(tmp_path):
    _tree(tmp_path, 1)
    _write(tmp_path, f"data/page-runs/{SLUG}.json", {"session_open": {}, "impeccable": {}})
    s = PS.status(SLUG, tmp_path)
    assert s["now"] == 9
    assert s["rows"][13]["state"] == "todo"


def test_a_posted_batch_without_answers_needs_you(tmp_path):
    _tree(tmp_path, 4)
    _write(tmp_path, "docs/reference/answer-board/batches/2026-10-03-q.json", {})
    assert PS.status(SLUG, tmp_path)["needs_you"] == ["answer board: 2026-10-03-q"]


def _built(tmp_path):
    """A tree proved through row 12: every stop approved and the page written and registered."""
    _tree(tmp_path, 4)
    _write(tmp_path, "data/facts/rebuilt.json", [SLUG])
    _write(tmp_path, f"src/pages/x/{SLUG}.astro", "<main>built</main>")


def test_a_scorecard_named_by_route_proves_the_render_row(tmp_path):
    _built(tmp_path)
    assert PS.status(SLUG, tmp_path)["now"] == 13
    _write(tmp_path, f"data/quality/scorecards/uk-locations__{SLUG}-2026-10-05.json", {})
    assert PS.status(SLUG, tmp_path)["now"] == 14


def test_a_scorecard_for_another_slug_does_not(tmp_path):
    _built(tmp_path)
    _write(tmp_path, f"data/quality/scorecards/uk-locations__{SLUG}-north-2026-10-05.json", {})
    assert PS.status(SLUG, tmp_path)["now"] == 13


def test_the_close_rows_read_the_gate_report_and_the_verification_key(tmp_path, monkeypatch):
    _built(tmp_path)
    _write(tmp_path, f"data/quality/scorecards/uk-locations__{SLUG}-2026-10-05.json", {})
    run = {"session_open": {}, "impeccable": {}, "frontend_design": {}}
    _write(tmp_path, f"data/page-runs/{SLUG}.json", run)
    steps = [{"step": "hardening", "ok": [True, True]}, {"step": "aeo", "ok": [True, True]}]
    _write(tmp_path, f"docs/reports/gate-page/{SLUG}.json",
           {"verdict": "PASS", "identical": True, "head": "abc", "steps": steps})
    monkeypatch.setattr(PS, "_git", lambda root, *a: "abc" if a[:1] == ("rev-parse",) else "")
    assert PS.status(SLUG, tmp_path)["now"] == 18          # the old "verification" key never matched
    _write(tmp_path, f"data/page-runs/{SLUG}.json", {**run, "verification_before_completion": {}})
    assert PS.status(SLUG, tmp_path)["now"] == 19
    _write(tmp_path, "docs/reports/p5-ledger.json", {"pages": [SLUG]})
    assert PS.status(SLUG, tmp_path)["now"] == 21
    _write(tmp_path, f"docs/reference/answer-board/answers/final-approval-{SLUG}-2026-10-06.md", "yes")
    assert PS.status(SLUG, tmp_path)["now"] is None


def test_a_gate_report_from_an_older_commit_does_not_prove_the_gates(tmp_path, monkeypatch):
    _built(tmp_path)
    _write(tmp_path, f"data/quality/scorecards/uk-locations__{SLUG}-2026-10-05.json", {})
    _write(tmp_path, f"data/page-runs/{SLUG}.json", {"session_open": {}, "impeccable": {}, "frontend_design": {}})
    steps = [{"step": "hardening", "ok": [True, True]}, {"step": "aeo", "ok": [True, True]}]
    _write(tmp_path, f"docs/reports/gate-page/{SLUG}.json",
           {"verdict": "PASS", "identical": True, "head": "old", "steps": steps})
    monkeypatch.setattr(PS, "_git", lambda root, *a: "new" if a[:1] == ("rev-parse",) else "")
    s = PS.status(SLUG, tmp_path)
    assert s["now"] == 17
    assert "(not HEAD)" in s["rows"][16]["evidence"]


def _gated_tree(tmp_path, monkeypatch, *, base, changed):
    _built(tmp_path)
    _write(tmp_path, f"data/quality/scorecards/uk-locations__{SLUG}-2026-10-05.json", {})
    _write(tmp_path, f"data/page-runs/{SLUG}.json", {"session_open": {}, "impeccable": {}, "frontend_design": {}})
    steps = [{"step": "hardening", "ok": [True, True]}, {"step": "aeo", "ok": [True, True]}]
    _write(tmp_path, f"docs/reports/gate-page/{SLUG}.json",
           {"verdict": "PASS", "identical": True, "head": "old", "steps": steps})

    def git(root, *a):
        if a[:1] == ("rev-parse",):
            return "new"
        if a[:1] == ("merge-base",):
            return base
        if a[:1] == ("diff",):
            return "\n".join(changed)
        return ""
    monkeypatch.setattr(PS, "_git", git)
    return PS.status(SLUG, tmp_path)


def test_a_docs_only_commit_after_gating_keeps_the_gate_current(tmp_path, monkeypatch):
    s = _gated_tree(tmp_path, monkeypatch, base="old", changed=["docs/reports/london-gate-report.md"])
    assert s["rows"][16]["state"] == "done"


def test_a_page_change_after_gating_makes_the_gate_stale(tmp_path, monkeypatch):
    s = _gated_tree(tmp_path, monkeypatch, base="old",
                    changed=["docs/reports/x.md", "src/pages/uk-locations/demo-city.astro"])
    assert s["now"] == 17


def test_a_gate_from_another_branch_is_never_current(tmp_path, monkeypatch):
    s = _gated_tree(tmp_path, monkeypatch, base="elsewhere", changed=["docs/a.md"])
    assert s["now"] == 17
