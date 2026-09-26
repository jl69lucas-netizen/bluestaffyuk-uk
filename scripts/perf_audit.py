#!/usr/bin/env python3
"""perf_audit.py — the PageSpeed gate: five categories, 100 each, mobile and desktop.

  python3 scripts/perf_audit.py <slug>                    # desktop, against dist/, 5 runs
  python3 scripts/perf_audit.py <slug> --mobile           # mobile, 5 runs
  python3 scripts/perf_audit.py <slug> --live --mobile    # the deployed URL (needs SITE_URL)
  python3 scripts/perf_audit.py <slug> --psi --mobile     # Google's own servers: THE record that counts
  python3 scripts/perf_audit.py --parse docs/reports/lh/lh--1.json   # judge a saved report, run nothing

Exit: 0 pass, 1 ran and failed the gate, 2 cannot run (no dist/, no lighthouse, refused).

`--psi` calls the PageSpeed Insights API (set PSI_API_KEY for more than the keyless daily
quota). It is authoritative because a local Mac cannot stand in for PSI: this machine's CPU
benchmark (~490) makes mobile Performance read far lower, and its fonts and cache timing
made CLS read 0 where PSI measured 0.266. Use local runs to find defects, PSI to judge.

Judges what PageSpeed Insights shows: Performance, Accessibility, Best Practices, SEO and
Agentic Browsing (Lighthouse 13.4.1, `agentic-browsing-config.js`). Every floor is 0.995,
the score PSI displays as 100.

THE RUN PROTOCOL (CAG §19b, measurement M7). Five runs by default. Run 1 is cold — a fresh
Chrome, empty caches — so the verdict is the WARM median, of runs 2–5, printed with the
spread of those runs and the cold run beside it; one run is its own warm set. CLS on this
site is bimodal, so a CLS verdict (warm median at or under 0.1) is given only on five or
more runs: on fewer, the record says `"verdict": null` and the output says so, and a CLS
FAIL on five runs fails the gate as `cumulative-layout-shift`.

WHY `--live` EXISTS. dist/ is not necessarily what visitors get. A host may edit the HTML
at the edge — inject its own analytics script, rewrite a font link into inline faces — and
those edits cost main-thread time while this gate, reading dist/, says PASS. `--live` lists
every script/font/stylesheet the live page loads that dist/ never references
(EDGE-INJECTED). An injected SCRIPT fails the gate. BSUK has no host and no domain until
project 6, so `--live`/`--psi` refuse until SITE_URL is real.

WHY LOCAL CLS CAN LIE. Local runs finish loading the preloaded hero photo before first
paint, so a box that only reaches its final size when the image arrives never shifts here.
A box that only reaches its final size when its image arrives never shifts here, and PSI
still measures it. When PSI and local disagree on CLS, delay each resource class in turn in
headless Chrome before you theorise.

Each run writes data/quality/perf/<slug>--<profile>[--live].json, which the Page Board
release gate reads (scripts/pageboard.py perf_findings).
"""
import argparse
import datetime
import functools
import http.server
import json
import pathlib
import socketserver
import statistics
import subprocess
import sys
import tempfile
import threading
import os
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PERF_DIR = ROOT / "data" / "quality" / "perf"
LIVE_ORIGIN = os.environ.get("SITE_URL", "https://SITE_URL_PLACEHOLDER")
LH_BIN = ROOT / "node_modules" / ".bin" / "lighthouse"
CONFIGS = {"mobile": ROOT / "scripts/lighthouse/agentic-mobile.mjs",
           "desktop": ROOT / "scripts/lighthouse/agentic-desktop.mjs"}

CATEGORIES = ("performance", "accessibility", "best-practices", "seo", "agentic-browsing")
THRESHOLDS = {c: 0.995 for c in CATEGORIES}
# Unscored and only ever caused by edge-injected third-party code; --live names the source.
IGNORE_AUDITS = {"valid-source-maps"}
# A host that injects its own scripts is a real class of defect; BSUK has no host yet
# (project 6), so this finds nothing today and is wired so it will.
EDGE_TYPES = {"Script", "Font", "Stylesheet"}
PORT = 4399
# One page, a few runs. Long enough for a cold Chrome start, short enough that a hung
# browser fails the command rather than the afternoon.
LH_TIMEOUT = 300
DEFAULT_RUNS = 5
CLS_MIN_RUNS = 5
CLS_GOOD = 0.1   # the "good" line of Core Web Vitals


class CannotRun(RuntimeError):
    """The gate could not run at all (exit 2) — never the same thing as a failure (exit 1)."""


def judge(reports):
    """Categories whose median score is under the floor. A missing or null score is 0 —
    a category Lighthouse did not produce must not pass on nothing."""
    failed = []
    for cat, floor in THRESHOLDS.items():
        scores = [((r.get("categories") or {}).get(cat) or {}).get("score") or 0 for r in reports]
        if statistics.median(scores) < floor:
            failed.append(cat)
    return failed


def warm(reports):
    """The runs that are judged: every run after the cold first one. One run is its own set."""
    return list(reports[1:]) if len(reports) > 1 else list(reports)


def _scores(reports, cat):
    return [((r.get("categories") or {}).get(cat) or {}).get("score") or 0 for r in reports]


def _cls_values(reports):
    vals = [((r.get("audits") or {}).get("cumulative-layout-shift") or {}).get("numericValue") for r in reports]
    return [v for v in vals if isinstance(v, (int, float))]


def cls_verdict(reports):
    """{"verdict": PASS|FAIL|None, "median", "min", "max", "runs"} over the WARM runs.
    None on fewer than CLS_MIN_RUNS runs in total: CLS is bimodal, and a verdict on three
    runs is the kind that has already caused a confident wrong attribution here."""
    vals = _cls_values(warm(reports))
    out = {"verdict": None, "runs": len(reports), "runs_needed": CLS_MIN_RUNS,
           "median": round(statistics.median(vals), 4) if vals else None,
           "min": round(min(vals), 4) if vals else None, "max": round(max(vals), 4) if vals else None}
    if len(reports) >= CLS_MIN_RUNS and vals:
        out["verdict"] = "PASS" if statistics.median(vals) <= CLS_GOOD else "FAIL"
    return out


def _requests(report):
    return ((report.get("audits", {}).get("network-requests") or {}).get("details") or {}).get("items") or []


def edge_injected(report, dist_html):
    """Script/font/stylesheet URLs the page loaded that the built HTML never references."""
    out = []
    for item in _requests(report):
        if item.get("resourceType") not in EDGE_TYPES:
            continue
        url = item["url"]
        parts = urllib.parse.urlsplit(url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        if url in dist_html or (parts.path not in ("", "/") and path in dist_html):
            continue
        if parts.hostname in ("127.0.0.1", "localhost") and parts.path in dist_html:
            continue
        out.append(url)
    return out


def edge_blocking(report, injected):
    """The injected URLs that are scripts — those cost main-thread time and fail the gate.
    A font a stylesheet we ship pulls in (its url() is in CSS, not HTML) is reported only."""
    scripts = {i["url"] for i in _requests(report) if i.get("resourceType") == "Script"}
    return [u for u in injected if u in scripts]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(root):
    handler = functools.partial(QuietHandler, directory=str(root))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def psi_url(url, profile, key=""):
    q = [("url", url), ("strategy", profile)] + [("category", c) for c in CATEGORIES]
    if key:
        q.append(("key", key))
    return f"{PSI_ENDPOINT}?{urllib.parse.urlencode(q)}"


def run_psi(url, out, profile):
    """The PSI record, or CannotRun. Every failure here — HTTP error, DNS, timeout, an
    error page where JSON was expected, a body with no lighthouseResult — means no
    measurement was taken, which is exit 2 and never a perf regression."""
    try:
        with urllib.request.urlopen(psi_url(url, profile, os.environ.get("PSI_API_KEY", "")), timeout=180) as r:
            body = json.load(r)
        report = body["lighthouseResult"]
    except urllib.error.HTTPError as e:
        raise CannotRun(f"PSI API {e.code}: {e.read()[:300].decode(errors='replace')}\n"
                        "Keyless quota is per day; set PSI_API_KEY, or run pagespeed.web.dev by hand.")
    except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
        raise CannotRun(f"PSI request to {url} produced no usable report: {e!r}\n"
                        "Keyless quota is per day; set PSI_API_KEY, or run pagespeed.web.dev by hand.")
    pathlib.Path(out).write_text(json.dumps(report))
    return report


def run_lighthouse(url, out, profile):
    if not LH_BIN.exists():
        raise CannotRun("node_modules/.bin/lighthouse missing — `npm i` (devDependency lighthouse@13.4.1).")
    cmd = [str(LH_BIN), url, "--quiet", "--output=json", f"--output-path={out}",
           f"--config-path={CONFIGS[profile]}", "--chrome-flags=--headless=new --no-sandbox"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=LH_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise CannotRun(f"lighthouse timed out after {LH_TIMEOUT}s on {url} — a headless Chrome "
                        "that never exits is not a failing page; nothing was measured.")
    if res.returncode != 0 or not pathlib.Path(out).exists():
        raise CannotRun(f"lighthouse failed:\n{res.stderr[-1500:]}")
    return json.loads(pathlib.Path(out).read_text())


def parse_only(paths):
    """Judge saved Lighthouse JSON without running anything. Returns the exit code.

    The gate has to be readable offline: docs/reports/lh/ already holds Foundation's
    reports, and a judging change must be checkable against them without a sweep."""
    reports = []
    for path in paths:
        try:
            reports.append(json.loads(pathlib.Path(path).read_text()))
        except (OSError, json.JSONDecodeError) as e:
            print(f"cannot read {path}: {e}", file=sys.stderr)
            return 2
    failed = judge(reports)
    print(f"  --parse {len(reports)} report(s) · Lighthouse {reports[0].get('lighthouseVersion', '?')}")
    for cat in THRESHOLDS:
        scores = [((r.get("categories") or {}).get(cat) or {}).get("score") or 0 for r in reports]
        print(f"    {'FAIL' if cat in failed else 'PASS'}  {cat:17s} {round(statistics.median(scores) * 100):3d}  floor 100")
    if failed:
        print(f"\nPERF GATE FAIL: {', '.join(failed)}")
        return 1
    print("\nPERF GATE PASS")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="PageSpeed gate: five categories, 100 each.")
    ap.add_argument("slug", nargs="?", help="page slug; omit only with --parse")
    ap.add_argument("--mobile", action="store_true")
    ap.add_argument("--live", action="store_true", help="audit the deployed URL, not dist/")
    ap.add_argument("--psi", action="store_true", help="PageSpeed Insights API on the deployed URL (implies --live)")
    ap.add_argument("--runs", type=int, default=DEFAULT_RUNS,
                    help=f"Lighthouse runs (default {DEFAULT_RUNS}); run 1 is cold and is not judged")
    ap.add_argument("--dist", default=None, help="directory to serve and diff against (default dist/)")
    ap.add_argument("--parse", nargs="+", metavar="REPORT.json",
                    help="judge saved Lighthouse JSON and exit; runs no browser")
    a = ap.parse_args(argv)
    if a.parse:
        return parse_only(a.parse)
    if a.slug is None:
        ap.error("slug is required unless --parse is given (use '' for the home page)")
    if a.runs < 1:
        ap.error("--runs must be at least 1")
    a.live = a.live or a.psi
    if a.live and "PLACEHOLDER" in LIVE_ORIGIN:
        print("REFUSED: --live/--psi needs a real SITE_URL. BSUK has no domain until "
              "project 6; measure dist/ instead (drop --live).", file=sys.stderr)
        return 2

    dist = pathlib.Path(a.dist) if a.dist else DIST
    slug = a.slug.strip("/")
    page = dist / slug / "index.html" if slug else dist / "index.html"
    if not page.exists():
        print(f"{page} not built — `npx astro build` first. The edge diff and the record both need dist/.",
              file=sys.stderr)
        return 2
    dist_html = page.read_text()
    profile = "mobile" if a.mobile else "desktop"
    path = f"/{slug}/" if slug else "/"

    httpd = None
    if a.live:
        url = LIVE_ORIGIN + path
    else:
        httpd = serve(dist)
        url = f"http://127.0.0.1:{PORT}{path}"

    reports = []
    tag = f"{slug or 'home'}--{profile}{'--psi' if a.psi else '--live' if a.live else ''}"
    # Raw Lighthouse output is scratch: the judged record is what PERF_DIR keeps. A fixed
    # /tmp name would collide between concurrent runs and outlive them either way.
    try:
        with tempfile.TemporaryDirectory(prefix="perf-audit-") as scratch:
            for i in range(a.runs):
                runner = run_psi if a.psi else run_lighthouse
                reports.append(runner(url, str(pathlib.Path(scratch) / f"lh-{tag}-{i}.json"), profile))
                if a.runs > 1:
                    print(f"  run {i + 1}/{a.runs} done")
    except CannotRun as e:
        print(e, file=sys.stderr)
        return 2
    finally:
        if httpd:
            httpd.shutdown()

    lh_version = reports[0].get("lighthouseVersion", "?")
    judged = warm(reports)
    basis = "one run" if len(reports) == 1 else f"warm median of runs 2–{len(reports)}"
    print(f"\n  {path}  [{profile}{' · PSI' if a.psi else ' · LIVE' if a.live else ' · dist'}]  {a.runs} run(s) · {basis} · Lighthouse {lh_version}")
    failed = judge(judged)
    median, spread, cold = {}, {}, {}
    for cat, floor in THRESHOLDS.items():
        scores = _scores(judged, cat)
        median[cat] = statistics.median(scores)
        spread[cat] = [min(scores), max(scores)]
        note = ""
        if len(reports) > 1:
            cold[cat] = _scores(reports[:1], cat)[0]
            note = (f"  (warm runs: {', '.join(str(round(s * 100)) for s in sorted(scores))};"
                    f" cold run 1: {round(cold[cat] * 100)})")
        print(f"    {'FAIL' if cat in failed else 'PASS'}  {cat:17s} {round(median[cat] * 100):3d}  floor 100{note}")

    metrics = {}
    for m in ("cumulative-layout-shift", "largest-contentful-paint", "total-blocking-time"):
        vals = [v for v in (((r.get("audits") or {}).get(m) or {}).get("numericValue") for r in judged)
                if isinstance(v, (int, float))]
        if vals:
            metrics[m] = round(statistics.median(vals), 4)
            print(f"    {m}: median {metrics[m]}  min {round(min(vals), 4)}  max {round(max(vals), 4)}")

    cls = cls_verdict(reports)
    if cls["verdict"] is None:
        print(f"    CLS: no CLS verdict on {len(reports)} run(s) — CLS is bimodal; "
              f"run {CLS_MIN_RUNS} (the default) for one")
    else:
        print(f"    {cls['verdict']}  CLS warm median {cls['median']}  line {CLS_GOOD}")
        if cls["verdict"] == "FAIL":
            failed.append("cumulative-layout-shift")

    injected, blocking = [], []
    if a.live:
        injected = sorted({u for r in reports for u in edge_injected(r, dist_html)})
        blocking = sorted({u for r in reports for u in edge_blocking(r, injected)})
        print("\n  EDGE-INJECTED (loaded live, never referenced by dist/):")
        for u in injected:
            print(f"    {'FAIL' if u in blocking else 'note'}  {u}")
        if not injected:
            print("    none")
        if blocking:
            print("    → a script the host adds at the edge, not something dist/ ships. Turn the "
                  "feature off in the host's dashboard and purge the cache; it is a toggle, not code.")

    print("\n  Failing audits (worst run):")
    worst = min(reports, key=lambda r: sum(((r.get("categories") or {}).get(k) or {}).get("score") or 0
                                           for k in THRESHOLDS))
    shown = 0
    for aid, aud in (worst.get("audits") or {}).items():
        if aid in IGNORE_AUDITS:
            continue
        score = aud.get("score")
        if score is not None and score < 1 and aud.get("scoreDisplayMode") not in ("informative", "manual", "notApplicable"):
            items = (aud.get("details") or {}).get("items") or []
            print(f"    - {aid}: {aud.get('title', '')} ({len(items)} item(s)) {aud.get('displayValue', '')}")
            shown += 1
    if not shown:
        print("    none")

    PERF_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "slug": slug, "profile": profile, "live": a.live, "psi": a.psi, "lighthouse": lh_version, "runs": a.runs,
        "warm_runs": len(judged), "median": median, "spread": spread, "cold": cold,
        "metrics": metrics, "cls": cls, "failed": failed,
        "edge_injected": injected, "edge_blocking": blocking,
        "dist_mtime": page.stat().st_mtime,
        "measured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    (PERF_DIR / f"{tag}.json").write_text(json.dumps(record, indent=2) + "\n")

    if failed or blocking:
        print(f"\nPERF GATE FAIL: {', '.join(failed + (['edge-injected-script'] if blocking else []))}")
        return 1
    print("\nPERF GATE PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
