"""perf_audit.py judging logic — the parts that decide PASS/FAIL, tested without Lighthouse.

No test here runs a browser or touches a network: a real sweep is a Task 20 activity, and a
gate whose judging can only be checked by a ten-minute Lighthouse run is a gate nobody
checks. `LIVE_ORIGIN` comes from SITE_URL, so the PSI-URL tests read it from the module
rather than hard-coding a domain BSUK does not have.
"""
import importlib.util
import json
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
