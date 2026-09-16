# tests/py/test_evidence_audit.py
#
# Ported from CAG tests/test_evidence_audit.py (Task 7). Only the fixture prose changes —
# every assertion stands, because each check is domain-neutral. No test is dropped.
# BUDGETS and LEDGER below are inline fixtures, never the real
# data/quality/evidence-budgets.json (Task 9 writes that file): a gate test must not
# depend on the repo's live counts.
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import evidence_audit as E

BUDGETS = {
    "title_max_chars": 70,
    "scam_owner": ["how-to-avoid-blue-staffy-puppy-scams"],
    "legit_owner": ["trusted-blue-staffy-breeders-uk"],
    "superlatives": ["world's best", "britain's trusted"],
    "terms": {"KC": "KC", "scam": "scam", "legit": "legit"},
    "budgets": {"home": {"KC": 2, "scam": 1, "legit": 0}},
}
LEDGER = {"claims": [
    {"id": "kc-registered", "pattern": "KC[- ]registered", "proof": "/proof/kc-redacted.webp", "anchor": "trust", "confirmed": "2026-09-16"},
    {"id": "hip-scored", "pattern": "hip[- ]scored", "proof": "NOT FETCHED", "anchor": "health", "confirmed": None},
]}

def page(main, title="Short Title"):
    return f"<html><head><title>{title}</title></head><body><main>{main}</main></body></html>"


def test_term_budget_flags_overrun_and_names_the_term():
    html = page("<p>KC KC KC</p>")
    f = E.term_budget(html, "home", BUDGETS)
    assert f == [("KC", 3, 2)]


def test_term_budget_is_silent_within_budget():
    assert E.term_budget(page("<p>KC once. KC twice.</p>"), "home", BUDGETS) == []


def test_scam_owner_page_is_exempt_from_the_scam_ceiling():
    html = page("<p>scam scam scam scam</p>")
    assert E.term_budget(html, "interior", BUDGETS, slug="how-to-avoid-blue-staffy-puppy-scams") == []
    assert E.term_budget(html, "home", BUDGETS, slug="index") == [("scam", 4, 1)]


def test_title_length_flags_the_233_char_style():
    long = "A | " * 60
    assert E.title_too_long(page("<p>x</p>", title=long), BUDGETS) is not None
    assert E.title_too_long(page("<p>x</p>", title="Blue Staffy Breeder in Glasgow, Scotland"), BUDGETS) is None


def test_review_attribution_flags_same_quote_two_names():
    html = page(
        '<blockquote><p>I searched for months before finding BlueStaffyUK. Truly top notch.</p><cite>Clifford Hutter</cite></blockquote>'
        '<blockquote><p>I searched for months before finding BlueStaffyUK. Truly top notch.</p><cite>Archie Obrien</cite></blockquote>')
    bad = E.review_attribution(html)
    assert len(bad) == 1 and {"Clifford Hutter", "Archie Obrien"} <= set(bad[0][1])


def test_review_attribution_accepts_same_quote_same_name_twice():
    html = page(
        '<blockquote><p>Flawless from start to finish.</p><cite>Richard Woodard</cite></blockquote>'
        '<blockquote><p>Flawless from start to finish.</p><cite>Richard Woodard</cite></blockquote>')
    assert E.review_attribution(html) == []


def test_claim_binding_flags_repeated_claim_without_proof_link():
    html = page("<p>KC-registered.</p><p>KC-registered again.</p>")
    unbound = E.claim_binding(html, LEDGER)
    assert [u[0] for u in unbound] == ["kc-registered"]


def test_claim_binding_accepts_repeated_claim_when_proof_is_linked():
    html = page('<p>KC-registered.</p><p>KC-registered. <a href="/proof/kc-redacted.webp">See the paperwork</a></p>')
    assert E.claim_binding(html, LEDGER) == []


def test_claim_binding_reports_not_fetched_proof_as_warn_not_error():
    html = page("<p>hip-scored.</p><p>hip-scored.</p>")
    out = E.claim_binding(html, LEDGER)
    assert out == [("hip-scored", 2, "NOT FETCHED")]


def test_statement_labels_required_where_species_claims_appear():
    html = page("<section id='breed'><h2>The Breed</h2><p>Canis familiaris lives 12 to 14 years.</p></section>")
    assert E.missing_statement_labels(html) == ["breed"]
    labelled = page("<section id='breed'><h2>The Breed</h2><p><span class='stmt-label' data-kind='fact'>Fact</span> Canis familiaris lives 12 to 14 years.</p></section>")
    assert E.missing_statement_labels(labelled) == []


def test_not_fetched_never_reaches_prose():
    assert E.not_fetched_in_prose(page("<p>Licence number: NOT FETCHED</p>")) == 1
    assert E.not_fetched_in_prose(page("<p>Licence on file.</p>")) == 0


def test_superlatives_are_flagged_unless_sourced_in_the_same_sentence():
    assert E.unsourced_superlatives(page("<p>The world's best family dog.</p>"), BUDGETS) == ["world's best"]
    sourced = page("<p>The world's best family dog, per <a href='https://example.org/study'>a breed study</a>.</p>")
    assert E.unsourced_superlatives(sourced, BUDGETS) == []


def test_audit_returns_error_on_budget_breach_and_exit_code_follows():
    html = page("<p>KC KC KC</p>")
    findings = E.audit("index", html, "home", BUDGETS, LEDGER)
    assert any(sev == "ERROR" and "KC" in msg for sev, msg in findings)


def test_review_attribution_ignores_puppy_name_and_cites_class_spans():
    # CITE class-substring false positive: `puppy-name` / `inq-price-name` / `cites-good` / `cites-cross`
    # are not reviewer names. Two puppy cards sharing a paragraph must not be reported.
    html = page(
        '<li><p>Home-raised from three weeks and weaned onto a complete puppy food.</p><span class="puppy-name">Roman</span></li>'
        '<li><p>Home-raised from three weeks and weaned onto a complete puppy food.</p><span class="puppy-name">Byrd</span></li>')
    assert E.review_attribution(html) == []
    html = page(
        '<li><p>Home-raised from three weeks and weaned onto a complete puppy food.</p><span class="inq-price-name">Roman</span></li>'
        '<li><p>Home-raised from three weeks and weaned onto a complete puppy food.</p><span class="inq-price-name">Byrd</span></li>')
    assert E.review_attribution(html) == []
    html = page(
        '<li><p>Home-raised from three weeks and weaned onto a complete puppy food.</p><span class="cites-good">KC papers</span></li>'
        '<li><p>Home-raised from three weeks and weaned onto a complete puppy food.</p><span class="cites-cross">Vet record</span></li>')
    assert E.review_attribution(html) == []


def test_superlatives_ignore_script_blocks_and_catch_curly_apostrophe():
    html = page('<script type="application/ld+json">{"description":"Bred in Glasgow. The world\'s best family dog."}</script>'
                '<p>Bred in Glasgow.</p>')
    assert E.unsourced_superlatives(html, BUDGETS) == []
    assert E.unsourced_superlatives(page("<p>The world’s best family dog.</p>"), BUDGETS) == ["world's best"]
    assert E.unsourced_superlatives(page("<p>The world&rsquo;s best family dog.</p>"), BUDGETS) == ["world's best"]


def test_review_attribution_reads_name_from_sibling_div_and_trims_location():
    # a testimonial component's 'grid' variant (project 3): name sits in a sibling <div class="font-display font-semibold">, as "Name, City, ST"
    html = page(
        '<article><blockquote><p>I searched for months before finding BlueStaffyUK. Truly top notch.</p></blockquote>'
        '<div class="font-display font-semibold text-[14px]">Ann Lee, Glasgow, Scotland</div></article>'
        '<article><blockquote><p>I searched for months before finding BlueStaffyUK. Truly top notch.</p></blockquote>'
        '<div class="font-display font-semibold text-[14px]">Bob Ray, Paisley, Scotland</div></article>')
    bad = E.review_attribution(html)
    assert len(bad) == 1 and bad[0][1] == ["Ann Lee", "Bob Ray"]   # location trimmed, names sorted


def test_review_attribution_name_first_card_is_not_credited_to_next_card():
    # regression for 1d0d7775: 'mosaic'/'feature' testimonial variants print the name BEFORE the blockquote;
    # the follow-on search must stop at </figure>, not run into the next card's name
    html = page(
        '<figure><div class="font-display font-bold text-xl">Ann Lee</div>'
        '<blockquote><p>I searched for months before finding BlueStaffyUK. Truly top notch.</p></blockquote></figure>'
        '<figure><div class="font-display font-bold text-xl">Bob Ray</div>'
        '<blockquote><p>I searched for months before finding BlueStaffyUK. Truly top notch.</p></blockquote></figure>')
    bad = E.review_attribution(html)
    assert len(bad) == 1 and bad[0][1] == ["Ann Lee", "Bob Ray"]


def test_review_attribution_wrapper_div_does_not_swallow_first_card():
    # the homepage bug the QUOTE_BLOCK lookahead fixed: a grid wrapper <div> whose first inner </div>
    # is the first card's name must not hide that card from the scan
    html = page(
        '<div class="grid"><article><blockquote><p>I searched for months before finding BlueStaffyUK. Truly top notch.</p></blockquote>'
        '<div class="font-display font-semibold">Ann Lee</div></article>'
        '<article><blockquote><p>I searched for months before finding BlueStaffyUK. Truly top notch.</p></blockquote>'
        '<div class="font-display font-semibold">Bob Ray</div></article></div>')
    assert E.review_attribution(html)[0][1] == ["Ann Lee", "Bob Ray"]


def test_statement_labels_section_regex_ignores_data_id():
    html = page("<section data-id='zz'><p>Canis familiaris lives 12 to 14 years.</p></section>")
    assert E.missing_statement_labels(html) == []


# --- the script's own entry point ---------------------------------------------------

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "evidence_audit.py"


def _run(tmp_path, *extra):
    import subprocess
    return subprocess.run([sys.executable, str(SCRIPT), "--all", "--dist", str(tmp_path)]
                          + list(extra), capture_output=True, text=True)


def _quality(tmp_path, budgets=None, ledger=None):
    """A tmp repo-shaped tree: data/quality/{evidence-budgets,evidence-ledger}.json."""
    q = tmp_path / "data" / "quality"
    q.mkdir(parents=True)
    if budgets is not None:
        (q / "evidence-budgets.json").write_text(json.dumps(budgets), encoding="utf-8")
    if ledger is not None:
        (q / "evidence-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
    return q


def test_main_exits_2_when_the_budgets_file_is_missing(tmp_path):
    """Task 9 writes data/quality/evidence-budgets.json. Until it exists the gate
    cannot run — exit 2, never a silent 0."""
    dist = tmp_path / "dist"
    (dist).mkdir()
    r = _run(dist, "--budgets", str(tmp_path / "nope.json"))
    assert r.returncode == 2
    assert "evidence budgets missing" in r.stdout


def test_main_writes_a_json_report(tmp_path):
    q = _quality(tmp_path, BUDGETS, LEDGER)
    dist = tmp_path / "dist"
    (dist).mkdir()
    (dist / "index.html").write_text(page("<p>KC KC KC</p>"), encoding="utf-8")
    out = tmp_path / "report.json"
    r = _run(dist, "--budgets", str(q / "evidence-budgets.json"),
             "--ledger", str(q / "evidence-ledger.json"), "--json", str(out))
    assert r.returncode == 1, r.stdout          # the term breach is an ERROR
    data = json.loads(out.read_text())
    assert data["errors"] == 1
    assert data["pages"][0]["slug"] == "index"
    assert any("KC" in f["message"] for f in data["pages"][0]["findings"])
