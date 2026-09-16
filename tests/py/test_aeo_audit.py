# tests/py/test_aeo_audit.py
#
# Ported from CAG tests/test_aeo_audit.py (Task 7). Every fixture is rewritten to BSUK's
# entities: Canis familiaris, Lisa Bright, Glasgow, KC-registered / microchipped.
# Fixtures are hand-built HTML strings — never counts read off the real dist/.
#
# Tests dropped in the port, each with its reason:
#   - test_labeled_method_detects_the_two_approved_names — LABELED_METHODS is empty by
#     design (spec §7 drops CAG's rule 12; BSUK owns no branded method label). Replaced
#     by test_labeled_method_check_is_inert_when_no_method_is_owned, which pins that the
#     empty list makes the check inert rather than making every page fail it.
import json, subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import aeo_audit as A


BLUF_GOOD = ("<h2>What Does a Blue Staffy Pup Cost?</h2><p>Blue Staffy pups from "
             "Lisa Bright cost £1,500 to £1,700.</p>")
BLUF_BAD = ("<h2>What Does a Blue Staffy Pup Cost?</h2><p>Before we get into numbers, it "
            "is worth stepping back and considering the long history of the "
            "Staffordshire Bull Terrier, which stretches back many generations and has "
            "changed a great deal over that time, so that context matters here.</p>")


def test_bluf_accepts_a_short_declarative_opener():
    assert A.bluf_violations(BLUF_GOOD) == []


def test_bluf_flags_a_long_wind_up_before_the_answer():
    bad = A.bluf_violations(BLUF_BAD)
    assert bad and "What Does a Blue Staffy Pup Cost?" in bad[0]


def test_bluf_ignores_headings_with_no_following_prose():
    assert A.bluf_violations("<h2>Standalone</h2><h3>Next</h3>") == []


def test_entity_audit_counts_the_binomial_and_the_breeder():
    r = A.entity_report("<p>Canis lupus familiaris pups from Lisa Bright "
                        "in Glasgow are KC-registered.</p>")
    assert r["binomial"] == 1
    assert r["breeder"] == 1
    assert r["place"] == 1
    assert r["credential"] == 1


def test_entity_audit_reports_zero_for_the_anonymous_page_case():
    """A page that names nobody: the shape the entity check exists to catch."""
    r = A.entity_report("<p>Our pups are home-raised and we deliver across the UK.</p>")
    assert r["binomial"] == 0 and r["breeder"] == 0


def test_pronoun_density_flags_we_our_heavy_copy():
    heavy = "<p>" + "We raise our pups and we love our pups. " * 6 + "</p>"
    assert A.pronoun_heavy(heavy) is True
    named = "<p>" + "Lisa Bright raises every Blue Staffy pup at home. " * 6 + "</p>"
    assert A.pronoun_heavy(named) is False


def test_labeled_method_check_is_inert_when_no_method_is_owned():
    """BSUK names no branded method, so LABELED_METHODS is empty and the audit must not
    emit a method finding — an empty list would otherwise fail every page forever."""
    assert A.LABELED_METHODS == []
    assert A.labeled_methods("<p>We socialize the pups at home.</p>") == []
    page = ('<script type="application/ld+json">{"dateModified":"2026-09-16"}</script>'
            "<h2>12 Years Breeding Blue Staffies</h2>"
            "<p>Lisa Bright breeds Canis familiaris pups in Glasgow.</p>")
    findings, _ = A.audit("index", page)
    assert not [x for x in findings if "method" in x[1]]


def test_freshness_reads_json_ld_only():
    assert A.has_freshness('<script type="application/ld+json">'
                           '{"dateModified":"2026-09-16"}</script>') is True
    assert A.has_freshness("<p>Updated July 2026</p>") is False, \
        "a VISIBLE date must never satisfy the freshness check — CLAUDE.md bans it"


def test_visible_date_is_reported_as_a_violation():
    assert A.visible_dates("<p>Last updated: June 2026</p>")
    assert A.visible_dates("<p>We whelped 6 pups in 2026.</p>") == []


def test_formatting_counts_tables_and_lists():
    r = A.formatting_report("<table><tr><td>a</td></tr></table><ul><li>x</li></ul>")
    assert r["tables"] == 1 and r["lists"] == 1


def test_stat_headers_are_detected():
    assert A.stat_headers("<h2>12 Years of Breeding Experience</h2>") == \
        ["12 Years of Breeding Experience"]
    assert A.stat_headers("<h2>6 Pups Available Now</h2>") == ["6 Pups Available Now"]
    assert A.stat_headers("<h2>Why Choose Us</h2>") == []


# --- the migration baseline (Task 6 convention) -------------------------------------
#
# 37 of the 49 built pages carry no dateModified. If every one of them fails the exit
# code, a NEW defect is indistinguishable from the backlog — so a page whose ONLY
# problems are baseline checks is tagged and counted separately, and does not fail the
# run. A page with any other ERROR still does.

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "aeo_audit.py"

BASELINE_ONLY = "<h2>6 Pups Available</h2><p>Lisa Bright breeds Canis familiaris pups in Glasgow.</p>"
REGRESSION = ('<script type="application/ld+json">{"dateModified":"2026-09-16"}</script>'
              "<h2>6 Pups Available</h2>"
              "<p>Lisa Bright breeds Canis familiaris pups in Glasgow. Last updated: June 2026</p>")


def test_freshness_is_the_only_baseline_check():
    assert A.BASELINE_CHECKS == {"freshness"}


def test_a_page_missing_only_datemodified_is_baseline_only():
    findings, _ = A.audit("index", BASELINE_ONLY)
    assert any(x[0] == "ERROR" for x in findings)
    assert A.baseline_only(findings) is True


def test_a_visible_date_is_a_real_regression_not_baseline():
    findings, _ = A.audit("index", REGRESSION)
    assert any("VISIBLE date" in x[1] for x in findings)
    assert A.baseline_only(findings) is False


def _dist(tmp_path, **pages):
    for slug, html in pages.items():
        d = tmp_path if slug == "index" else tmp_path / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")
    return tmp_path


def _run(tmp_path, *extra):
    return subprocess.run([sys.executable, str(SCRIPT), "--all", "--dist", str(tmp_path)]
                          + list(extra), capture_output=True, text=True)


def test_baseline_only_pages_do_not_fail_the_run(tmp_path):
    r = _run(_dist(tmp_path, index=BASELINE_ONLY))
    assert r.returncode == 0, r.stdout
    assert "[migration baseline]" in r.stdout
    assert "baseline-only FAIL pages: 1" in r.stdout


def test_a_real_regression_still_fails_the_run(tmp_path):
    r = _run(_dist(tmp_path, index=BASELINE_ONLY, **{"a-page": REGRESSION}))
    assert r.returncode == 1, r.stdout
    assert "baseline-only FAIL pages: 1" in r.stdout


def test_json_report_records_the_baseline_flag(tmp_path):
    out = tmp_path / "report.json"
    r = _run(_dist(tmp_path, index=BASELINE_ONLY), "--json", str(out))
    assert r.returncode == 0, r.stdout
    data = json.loads(out.read_text())
    assert data["baseline_only_pages"] == 1
    assert data["pages"][0]["baseline_only"] is True
    assert data["pages"][0]["slug"] == "index"


def test_json_ld_extraction_matches_schema_checks_pattern():
    """single quotes and extra attributes are valid JSON-LD; schema_check.py accepts
    them, and the freshness check must not silently disagree with it."""
    assert A.has_freshness("<script data-x type='application/ld+json'>"
                           '{"dateModified":"2026-09-16"}</script>') is True
