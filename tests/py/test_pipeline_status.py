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
