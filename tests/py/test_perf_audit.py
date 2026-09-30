"""perf_audit.py judging logic — the parts that decide PASS/FAIL, tested without Lighthouse.

No test here runs a browser or touches a network: a real sweep is a Task 20 activity, and a
gate whose judging can only be checked by a ten-minute Lighthouse run is a gate nobody
checks. `LIVE_ORIGIN` comes from SITE_URL, so the PSI-URL tests read it from the module
rather than hard-coding a domain BSUK does not have.
"""
import importlib.util
import json
import subprocess
import re
import statistics
import urllib.error

import pytest
import os
import pathlib

spec = importlib.util.spec_from_file_location(
    "perf_audit", pathlib.Path(__file__).resolve().parents[2] / "scripts/perf_audit.py")
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)

FULL = {"performance": 1, "accessibility": 1, "best-practices": 1, "seo": 1, "agentic-browsing": 1}


def rep(scores):
    return {"categories": {k: {"score": v} for k, v in scores.items()}, "audits": {}}


def test_five_categories_are_judged():
    assert set(pa.THRESHOLDS) == set(FULL)


def test_99_performance_fails_the_100_floor():
    assert pa.judge([rep(dict(FULL, performance=0.99))]) == ["performance"]


def test_995_is_what_psi_displays_as_100_and_passes():
    assert pa.judge([rep(dict(FULL, performance=0.995))]) == []


def test_missing_category_fails_rather_than_passing_on_nothing():
    scores = dict(FULL)
    scores.pop("agentic-browsing")
    assert pa.judge([rep(scores)]) == ["agentic-browsing"]


def test_null_score_counts_as_zero():
    assert pa.judge([rep(dict(FULL, seo=None))]) == ["seo"]


def test_median_of_runs_is_judged_not_the_worst():
    runs = [rep(dict(FULL, performance=p)) for p in (0.90, 1, 1)]
    assert pa.judge(runs) == []


def _net(*items):
    return {"audits": {"network-requests": {"details": {"items": list(items)}}}}


HOST = "https://example-host.test"


def test_edge_injected_resources_are_those_the_built_html_never_references():
    report = _net(
        {"url": "http://127.0.0.1:4399/_astro/a.js", "resourceType": "Script"},
        {"url": f"{HOST}/70de/", "resourceType": "Script"},
        {"url": f"{HOST}/cf-fonts/v/x/latin/wght/normal.woff2", "resourceType": "Font"},
        {"url": f"{HOST}/images/hero.webp", "resourceType": "Image"},
    )
    dist_html = '<script src="/_astro/a.js"></script><img src="/images/hero.webp">'
    assert pa.edge_injected(report, dist_html) == [
        f"{HOST}/70de/",
        f"{HOST}/cf-fonts/v/x/latin/wght/normal.woff2",
    ]


def test_scripts_our_own_code_loads_by_url_are_not_edge_injected():
    # A deferred analytics loader writes its URL into an inline script, not a <script src>.
    report = _net({"url": "https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX", "resourceType": "Script"})
    dist_html = "s.src='https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX'"
    assert pa.edge_injected(report, dist_html) == []


def test_edge_scripts_are_blocking_edge_fonts_are_not():
    urls = [f"{HOST}/70de/", f"{HOST}/cf-fonts/a.woff2"]
    report = _net({"url": urls[0], "resourceType": "Script"}, {"url": urls[1], "resourceType": "Font"})
    assert pa.edge_blocking(report, urls) == [urls[0]]


def test_psi_request_asks_for_all_five_categories_and_the_strategy():
    u = pa.psi_url(pa.LIVE_ORIGIN + "/x/", "mobile", key="K")
    for c in pa.CATEGORIES:
        assert f"category={c}" in u
    assert "strategy=mobile" in u and "key=K" in u


def test_psi_request_without_key_sends_no_key_param():
    assert "key=" not in pa.psi_url(pa.LIVE_ORIGIN + "/x/", "desktop")


def test_live_origin_comes_from_the_environment_and_defaults_to_the_placeholder():
    """BSUK has no domain until project 6. A hard-coded origin here would have `--live`
    silently measure somebody else's site."""
    assert pa.LIVE_ORIGIN == os.environ.get("SITE_URL", "https://SITE_URL_PLACEHOLDER")


def test_live_refuses_while_the_origin_is_still_the_placeholder(monkeypatch, capsys):
    monkeypatch.setattr(pa, "LIVE_ORIGIN", "https://SITE_URL_PLACEHOLDER")
    assert pa.main(["", "--live"]) == 2
    assert "REFUSED" in capsys.readouterr().err


def test_a_missing_dist_page_cannot_run_rather_than_failing(tmp_path, capsys):
    """Exit 2 is `cannot run`; exit 1 is `ran and failed`. Collapsing them would let an
    unbuilt tree read as a perf regression."""
    assert pa.main(["nope", "--dist", str(tmp_path)]) == 2
    assert "not built" in capsys.readouterr().err


def test_parse_only_judges_saved_reports_without_running_a_browser(tmp_path, capsys):
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"lighthouseVersion": "13.4.1",
                                "categories": {k: {"score": 1} for k in pa.CATEGORIES}}))
    assert pa.parse_only([str(good)]) == 0
    assert "PERF GATE PASS" in capsys.readouterr().out
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"categories": {k: {"score": 1 if k != "seo" else 0.4}
                                              for k in pa.CATEGORIES}}))
    assert pa.parse_only([str(bad)]) == 1


def test_parse_only_on_an_unreadable_report_cannot_run(tmp_path, capsys):
    assert pa.parse_only([str(tmp_path / "absent.json")]) == 2


# --- cannot-run paths: every way the gate fails to produce a measurement is exit 2 -------
# The distinction is the whole point of the two codes. A hung Lighthouse, a DNS failure or
# a PSI error page are all "no measurement was taken"; reporting any of them as exit 1
# would enter a regression in the record for a run that never happened.

def test_a_hung_lighthouse_cannot_run_rather_than_hanging_forever(monkeypatch, tmp_path):
    """Without a timeout the gate waits for a headless Chrome that may never exit."""
    def hang(cmd, **kw):
        assert kw.get("timeout"), "lighthouse must be given a timeout"
        raise subprocess.TimeoutExpired(cmd, kw["timeout"])
    monkeypatch.setattr(pa.subprocess, "run", hang)
    monkeypatch.setattr(pa, "LH_BIN", _touch(tmp_path / "lighthouse"))
    with pytest.raises(pa.CannotRun) as e:
        pa.run_lighthouse("http://127.0.0.1:4399/", str(tmp_path / "o.json"), "desktop")
    assert "timed out" in str(e.value)


def test_a_network_failure_on_psi_cannot_run(monkeypatch, tmp_path):
    def boom(*a, **kw):
        raise urllib.error.URLError("name or service not known")
    monkeypatch.setattr(pa.urllib.request, "urlopen", boom)
    with pytest.raises(pa.CannotRun):
        pa.run_psi("https://x.test/", str(tmp_path / "o.json"), "mobile")


def test_a_malformed_psi_body_cannot_run_rather_than_crashing(monkeypatch, tmp_path):
    class _R:
        def read(self):
            return b"<html>not json</html>"
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
    monkeypatch.setattr(pa.urllib.request, "urlopen", lambda *a, **kw: _R())
    with pytest.raises(pa.CannotRun):
        pa.run_psi("https://x.test/", str(tmp_path / "o.json"), "mobile")


def test_a_psi_body_without_a_lighthouse_result_cannot_run(monkeypatch, tmp_path):
    class _R:
        def read(self):
            return json.dumps({"error": {"message": "quota"}}).encode()
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
    monkeypatch.setattr(pa.urllib.request, "urlopen", lambda *a, **kw: _R())
    with pytest.raises(pa.CannotRun):
        pa.run_psi("https://x.test/", str(tmp_path / "o.json"), "mobile")


def test_parse_only_survives_a_report_with_no_categories_block(tmp_path, capsys):
    """A truncated or wrong-shaped report must read as 0 (FAIL), never as a KeyError.
    judge() was already defensive; the PRINT path was not, so the same report judged fine
    and then crashed on the way to saying so."""
    p = tmp_path / "r.json"
    p.write_text(json.dumps({"lighthouseVersion": "13.4.1"}))
    assert pa.parse_only([str(p)]) == 1
    assert "PERF GATE FAIL" in capsys.readouterr().out


def _touch(p):
    p.write_text("#!/bin/sh\n")
    return p


# --- the run protocol: five runs, the warm median of runs 2-5, no CLS verdict on fewer ----
# CAG parity audit 19b.5 / M7. CLS on this site is bimodal and the first Lighthouse run of a
# session is cold (Chrome start, empty caches), so one run proves nothing and a median that
# includes the cold run is not a warm number. The docstring already said `--runs 5`; the
# code defaulted to 1, the perf-gate skill said 3, and the release gate's hint said 3.

class _NoServer:
    def shutdown(self):
        pass


def _fake_runs(monkeypatch, tmp_path, reports):
    """Run main() against canned Lighthouse reports; returns (calls, perf_dir, dist)."""
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html></html>")
    perf_dir = tmp_path / "perf"
    calls = []

    def fake(url, out, profile):
        calls.append(url)
        return reports[len(calls) - 1]
    monkeypatch.setattr(pa, "serve", lambda root: _NoServer())
    monkeypatch.setattr(pa, "run_lighthouse", fake)
    monkeypatch.setattr(pa, "PERF_DIR", perf_dir)
    return calls, perf_dir, dist


def lh(perf=1, cls=0.0):
    return {"lighthouseVersion": "13.4.1",
            "categories": {k: {"score": perf if k == "performance" else 1} for k in pa.CATEGORIES},
            "audits": {"cumulative-layout-shift": {"numericValue": cls}}}


def test_the_default_is_five_runs(monkeypatch, tmp_path):
    calls, _, dist = _fake_runs(monkeypatch, tmp_path, [lh()] * 5)
    assert pa.main(["", "--dist", str(dist)]) == 0
    assert len(calls) == 5


def test_the_cold_first_run_is_not_judged():
    runs = [lh(perf=0.5), lh(perf=0.99), lh(perf=1), lh(perf=1), lh(perf=0.99)]
    assert pa.judge(runs) == ["performance"]           # all five: median 0.99
    assert pa.warm(runs) == runs[1:]
    assert pa.judge(pa.warm(runs)) == []               # runs 2-5: median 0.995


def test_one_run_is_its_own_warm_set():
    one = [lh()]
    assert pa.warm(one) == one


def test_the_record_carries_the_warm_median_and_its_spread(monkeypatch, tmp_path, capsys):
    reports = [lh(perf=0.5), lh(perf=0.99), lh(perf=1), lh(perf=1), lh(perf=0.99)]
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, reports)
    assert pa.main(["", "--dist", str(dist)]) == 0
    out = capsys.readouterr().out
    assert "warm median of runs 2–5" in out
    rec = json.loads((perf_dir / "home--desktop.json").read_text())
    assert rec["runs"] == 5 and rec["warm_runs"] == 4
    assert rec["median"]["performance"] == 0.995
    assert rec["spread"]["performance"] == [0.99, 1]
    assert rec["cold"]["performance"] == 0.5


def test_fewer_than_five_runs_gives_no_cls_verdict(monkeypatch, tmp_path, capsys):
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, [lh(cls=0.3)] * 3)
    assert pa.main(["", "--dist", str(dist), "--runs", "3"]) == 0
    assert "no CLS verdict" in capsys.readouterr().out
    rec = json.loads((perf_dir / "home--desktop.json").read_text())
    assert rec["cls"]["verdict"] is None


# Values where the warm median and the all-five median fall on opposite sides of 0.1, so a
# CLS verdict that quietly included the cold run would give the other answer.
CLS_FAIL_WARM = [lh(cls=0.0), lh(cls=0.05), lh(cls=0.05), lh(cls=0.2), lh(cls=0.2)]   # all 0.05, warm 0.125
CLS_PASS_WARM = [lh(cls=0.9)] + [lh(cls=0.02)] * 4                                     # all 0.02, cold 0.9


def test_five_runs_judge_cls_on_the_warm_median(monkeypatch, tmp_path, capsys):
    # the all-five median (0.05) would PASS; the warm median of runs 2-5 (0.125) FAILS
    assert statistics.median(pa._cls_values(CLS_FAIL_WARM)) <= pa.CLS_GOOD
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, CLS_FAIL_WARM)
    assert pa.main(["", "--dist", str(dist)]) == 1
    rec = json.loads((perf_dir / "home--desktop.json").read_text())
    assert rec["cls"]["verdict"] == "FAIL" and rec["cls"]["median"] == 0.125
    assert "cumulative-layout-shift" in rec["failed"]


def test_five_warm_runs_under_the_cls_line_pass(monkeypatch, tmp_path):
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, CLS_PASS_WARM)
    assert pa.main(["", "--dist", str(dist)]) == 0
    cls = json.loads((perf_dir / "home--desktop.json").read_text())["cls"]
    assert cls["verdict"] == "PASS" and cls["max"] < 0.9 and cls["min"] == 0.02


def test_the_metrics_are_the_warm_runs(monkeypatch, tmp_path):
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, CLS_FAIL_WARM)
    pa.main(["", "--dist", str(dist)])
    rec = json.loads((perf_dir / "home--desktop.json").read_text())
    assert rec["metrics"]["cumulative-layout-shift"] == 0.125      # all five would say 0.05


def test_two_runs_judge_run_two_and_keep_run_one_as_cold(monkeypatch, tmp_path, capsys):
    runs = [lh(perf=0.5), lh(perf=1)]
    assert pa.warm(runs) == [runs[1]]
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, runs)
    assert pa.main(["", "--dist", str(dist), "--runs", "2"]) == 0
    assert "warm median of runs 2–2" in capsys.readouterr().out
    rec = json.loads((perf_dir / "home--desktop.json").read_text())
    assert rec["warm_runs"] == 1 and rec["median"]["performance"] == 1 and rec["cold"]["performance"] == 0.5


def test_zero_runs_is_refused(monkeypatch, tmp_path):
    _, _, dist = _fake_runs(monkeypatch, tmp_path, [])
    with pytest.raises(SystemExit) as e:
        pa.main(["", "--dist", str(dist), "--runs", "0"])
    assert e.value.code == 2


def test_warm_runs_without_cls_values_say_so(monkeypatch, tmp_path, capsys):
    bare = {"lighthouseVersion": "13.4.1",
            "categories": {k: {"score": 1} for k in pa.CATEGORIES}, "audits": {}}
    assert pa.cls_verdict([bare] * 5)["verdict"] is None
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, [bare] * 5)
    assert pa.main(["", "--dist", str(dist)]) == 0
    out = capsys.readouterr().out
    assert "no CLS values in the warm runs" in out
    assert json.loads((perf_dir / "home--desktop.json").read_text())["cls"]["verdict"] is None


@pytest.mark.parametrize("reports", [CLS_FAIL_WARM, CLS_PASS_WARM,
                                     [lh(perf=0.5), lh(perf=0.99), lh(perf=1), lh(perf=1), lh(perf=0.99)]])
def test_parse_judges_saved_reports_exactly_as_a_run_does(monkeypatch, tmp_path, capsys, reports):
    """--parse takes the files in run order (the first is the cold run) and gives the same
    verdict, category lines and CLS verdict as the run that produced them."""
    _, _, dist = _fake_runs(monkeypatch, tmp_path, reports)
    live_code = pa.main(["", "--dist", str(dist)])
    live = [l for l in capsys.readouterr().out.splitlines() if l.startswith("    ")]
    files = []
    for i, r in enumerate(reports):
        f = tmp_path / f"lh-{i}.json"
        f.write_text(json.dumps(r))
        files.append(str(f))
    parse_code = pa.main(["--parse", *files])
    parsed = [l for l in capsys.readouterr().out.splitlines() if l.startswith("    ")]
    assert parse_code == live_code
    verdict_lines = lambda ls: [l for l in ls if "CLS" in l or "floor 100" in l]
    assert verdict_lines(parsed) == verdict_lines(live) and verdict_lines(live)


def test_psi_defaults_to_one_run_and_local_to_five(monkeypatch, tmp_path):
    calls, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, [lh()] * 5)
    psi_calls = []
    monkeypatch.setattr(pa, "LIVE_ORIGIN", "https://example.test")
    monkeypatch.setattr(pa, "run_psi", lambda url, out, profile: psi_calls.append(url) or lh())
    assert pa.main(["", "--dist", str(dist), "--psi"]) == 0
    assert len(psi_calls) == 1 and calls == []
    assert json.loads((perf_dir / "home--desktop--psi.json").read_text())["runs"] == 1
    assert pa.main(["", "--dist", str(dist)]) == 0
    assert len(calls) == 5


ROOT = pathlib.Path(__file__).resolve().parents[2]
FEW_RUNS = re.compile(r"--runs[ =]+[1-4]\b")


def test_no_instruction_or_hint_asks_for_fewer_than_five_runs():
    files = ([ROOT / "CLAUDE.md", ROOT / "scripts/pageboard.py", ROOT / "scripts/perf_audit.py"]
             + sorted((ROOT / ".claude").rglob("*.md")) + sorted((ROOT / "docs/reference").glob("*.md"))
             + sorted((ROOT / "rules").glob("*.md")))
    bad = [f"{p.relative_to(ROOT)}:{n}" for p in files
           for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if FEW_RUNS.search(line)]
    assert bad == [], bad
