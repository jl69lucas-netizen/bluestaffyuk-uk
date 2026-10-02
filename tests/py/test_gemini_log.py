"""Gemini usage log: one JSON line per call, a summary, and no key ever written."""
import json
import subprocess
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gemini_log as GL

SECRET = "AQ.testsecret123"


def _lines(p):
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def test_log_call_appends_one_json_line(tmp_path):
    p = tmp_path / "log.jsonl"
    GL.log_call("gemini-x", "slot-a", 200, path=p, ts="2026-10-02T10:00:00Z")
    GL.log_call("gemini-x", "slot-b", 402, note="credits", path=p, ts="2026-10-02T11:00:00Z")
    rows = _lines(p)
    assert len(rows) == 2
    assert rows[0] == {"ts": "2026-10-02T10:00:00Z", "model": "gemini-x", "slot": "slot-a",
                       "status": 200, "note": ""}
    assert list(rows[1]) == ["ts", "model", "slot", "status", "note"]
    assert rows[1]["note"] == "credits"


def test_default_ts_is_iso_utc(tmp_path):
    p = tmp_path / "log.jsonl"
    GL.log_call("m", "s", 200, path=p)
    ts = _lines(p)[0]["ts"]
    assert ts.endswith("Z") and "T" in ts and len(ts) == 20


def test_summary_counts(tmp_path):
    p = tmp_path / "log.jsonl"
    GL.log_call("m", "a", 402, path=p, ts="2026-10-01T09:00:00Z")
    GL.log_call("m", "b", 402, path=p, ts="2026-10-02T09:00:00Z")
    GL.log_call("m", "c", 200, path=p, ts="2026-10-02T10:00:00Z")
    s = GL.summary(p, today="2026-10-02")
    assert s["today"] == 2 and s["total"] == 3
    assert s["by_status"] == {"402": 2, "200": 1}


def test_missing_log_is_zero_summary(tmp_path):
    s = GL.summary(tmp_path / "nope.jsonl", today="2026-10-02")
    assert s == {"today": 0, "total": 0, "by_status": {}, "malformed": 0}


def test_key_never_written(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", SECRET)
    p = tmp_path / "log.jsonl"
    GL.log_call("m", "s", 401, note="bad key %s rejected" % SECRET, path=p)
    GL.log_call("m", "s", 401, note="old key AIzaSyFAKEFAKE123 rejected", path=p)
    GL.log_call("m", SECRET, 401, note="raw " + SECRET.replace("AQ.", ""), path=p)
    text = p.read_text()
    assert SECRET not in text and "AIzaSyFAKEFAKE123" not in text
    assert "testsecret123" not in text
    rows = _lines(p)
    assert rows[0]["note"] == "bad key [redacted] rejected"
    assert rows[1]["note"] == "old key [redacted] rejected"


def test_cli_summary(tmp_path):
    p = tmp_path / "log.jsonl"
    GL.log_call("m", "a", 402, path=p, ts="2026-10-02T09:00:00Z")
    r = subprocess.run([sys.executable, str(ROOT / "scripts/gemini_log.py"), "summary",
                        "--path", str(p)], capture_output=True, text=True)
    assert r.returncode == 0
    assert "total 1" in r.stdout and "402: 1" in r.stdout
    r = subprocess.run([sys.executable, str(ROOT / "scripts/gemini_log.py"), "bogus"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "usage" in r.stderr.lower()


def test_committed_log_is_clean():
    p = ROOT / "docs/reports/gemini-usage.jsonl"
    rows = _lines(p)
    assert len(rows) >= 3
    for r in rows:
        assert set(r) == {"ts", "model", "slot", "status", "note"}
    assert not GL.KEY_PATTERN.search(p.read_text())


def test_malformed_lines_are_counted_not_fatal(tmp_path):
    p = tmp_path / "log.jsonl"
    GL.log_call("m", "a", 200, path=p, ts="2026-10-02T09:00:00Z")
    with p.open("a") as f:
        f.write("{not json\n[1, 2]\n")
    s = GL.summary(p, today="2026-10-02")
    assert s["total"] == 1 and s["today"] == 1 and s["malformed"] == 2
    assert "malformed lines 2" in GL.render(s)


def test_redaction_spares_words_ending_in_aq(tmp_path):
    p = tmp_path / "log.jsonl"
    GL.log_call("m", "s", 200, note="see FAQ.md and AQ.realkey99", path=p)
    note = _lines(p)[0]["note"]
    assert note == "see FAQ.md and [redacted]"
