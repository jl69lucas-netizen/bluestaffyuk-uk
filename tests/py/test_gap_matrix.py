# tests/py/test_gap_matrix.py — scripts/gap_matrix.py (spec 2026-09-23-competitor-intel §6).
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import gap_matrix as G  # noqa: E402

SCRIPT = REPO / "scripts" / "gap_matrix.py"
NF = {"status": "NOT FETCHED", "reason": "fetch blocked"}


def ok(values):
    return {"status": "ok", "values": values}


def report(rid, keywords=(), page_types=None, cities=(), schema_types=(), **over):
    r = {"id": rid, "root_domain": f"{rid}.co.uk", "analysed_on": "2026-09-24",
         "keywords": ok(list(keywords)), "page_types": ok(page_types or {}),
         "cities": ok(list(cities)), "schema_types": ok(list(schema_types)),
         "pages": {"status": "ok", "fetched_on": "2026-09-24", "values": []},
         "trust": ok({}), "content": ok({}), "blog": ok({}), "visual": ok({}),
         "conversion": ok({}), "technical": ok({}), "key_insight": ""}
    r.update(over)
    return r


def make_root(tmp_path, *reports):
    d = tmp_path / "docs/research/competitors"
    d.mkdir(parents=True, exist_ok=True)
    for r in reports:
        (d / f"{r['id']}.json").write_text(json.dumps(r))
    return tmp_path


def row(rows, value):
    return next(r for r in rows if r.value == value)


def test_only_fetched_competitors_count_toward_m(tmp_path):
    blocked = report("c")
    blocked["keywords"] = NF
    root = make_root(tmp_path, report("a", ["blue staffy"]), report("b", ["blue staffy"]), blocked)
    bsuk, comps = G.load_reports(root)
    r = row(G.rows(bsuk, comps, "keywords"), "blue staffy")
    assert (r.n, r.m, r.not_fetched) == (2, 2, 1)


@pytest.mark.parametrize("n,m,band", [(2, 5, "high"), (1, 5, "medium"), (1, 6, "low"),
                                      (4, 10, "high"), (3, 10, "medium")])
def test_priority_bands(n, m, band):
    assert G.priority(n, m) == band


def test_what_bsuk_already_has_gets_no_priority(tmp_path):
    root = make_root(tmp_path, report("bsuk", ["blue staffy"]), report("a", ["blue staffy", "kc registered"]))
    bsuk, comps = G.load_reports(root)
    rows = G.rows(bsuk, comps, "keywords")
    assert row(rows, "blue staffy").bsuk_has == "yes" and row(rows, "blue staffy").band == "—"
    assert row(rows, "kc registered").bsuk_has == "no" and row(rows, "kc registered").band == "high"


def test_a_missing_bsuk_profile_is_said_not_guessed(tmp_path):
    root = make_root(tmp_path, report("a", ["blue staffy"]))
    bsuk, comps = G.load_reports(root)
    assert bsuk is None
    assert row(G.rows(bsuk, comps, "keywords"), "blue staffy").bsuk_has == "not fetched"


def test_keywords_are_compared_case_and_space_blind(tmp_path):
    root = make_root(tmp_path, report("a", ["Blue  Staffy"]), report("b", ["blue staffy"]))
    bsuk, comps = G.load_reports(root)
    assert row(G.rows(bsuk, comps, "keywords"), "blue staffy").n == 2


def test_a_page_type_with_count_zero_is_absent(tmp_path):
    root = make_root(tmp_path, report("a", page_types={"city": 0, "faq": 2}))
    bsuk, comps = G.load_reports(root)
    assert [r.value for r in G.rows(bsuk, comps, "page_types")] == ["faq"]


def test_a_report_that_breaks_the_schema_is_bad_input(tmp_path):
    bad = report("a")
    del bad["trust"]
    with pytest.raises(G.BadReport):
        G.load_reports(make_root(tmp_path, bad))


def test_the_file_name_must_be_the_id(tmp_path):
    root = make_root(tmp_path)
    (root / "docs/research/competitors/other.json").write_text(json.dumps(report("a")))
    with pytest.raises(G.BadReport):
        G.load_reports(root)


def test_the_queue_is_the_ten_biggest_gaps(tmp_path):
    reps = [report(f"c{i}", [f"kw{j}" for j in range(i + 1)]) for i in range(12)]
    bsuk, comps = G.load_reports(make_root(tmp_path, *reps))
    queue = G.queue(bsuk, comps)
    assert len(queue) == 10
    assert [q.value for q in queue[:2]] == ["kw0", "kw1"]      # 12/12, then 11/12


def test_render_names_the_registry_entries_with_no_report(tmp_path):
    root = make_root(tmp_path, report("a", ["x"]))
    (root / "data").mkdir()
    (root / "data/competitors.json").write_text(json.dumps(
        {"_meta": {}, "competitors": [{"id": "a"}, {"id": "b"}]}))
    text = G.render(root, "2026-09-24")
    assert "No report yet: b" in text and "| x | 1/1 | 0 | not fetched | high |" in text


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_check_passes_after_write_and_fails_after_a_hand_edit(tmp_path):
    root = make_root(tmp_path, report("a", ["x"]))
    assert run("--write", "--date", "2026-09-24", "--root", str(root)).returncode == 0
    out = root / "docs/research/gap-matrix-2026-09-24.md"
    assert run("--check", "--root", str(root)).returncode == 0
    out.write_text(out.read_text().replace("1/1", "5/1"))
    r = run("--check", "--root", str(root))
    assert r.returncode == 1 and "gap-matrix-2026-09-24.md" in r.stdout


def test_check_with_nothing_written_passes(tmp_path):
    r = run("--check", "--root", str(tmp_path))
    assert r.returncode == 0 and "nothing to check" in r.stdout


def test_check_with_reports_but_no_matrix_fails(tmp_path):
    r = run("--check", "--root", str(make_root(tmp_path, report("a"))))
    assert r.returncode == 1 and "--write" in r.stdout


def test_a_bad_report_exits_6(tmp_path):
    bad = report("a")
    bad["keywords"] = {"status": "maybe"}
    r = run("--write", "--root", str(make_root(tmp_path, bad)))
    assert r.returncode == 6


def test_the_real_repo_passes():
    r = run("--check")
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("registry", [
    "[]",
    '{"competitors": {"a": 1}}',
    '{"competitors": ["a"]}',
    '{"competitors": [{"name": "a"}]}',
    '{"competitors": [{"id": 7}]}',
    "{not json",
])
def test_a_malformed_registry_is_reported_not_a_traceback(tmp_path, registry):
    root = make_root(tmp_path, report("a", ["x"]))
    (root / "data").mkdir()
    (root / "data/competitors.json").write_text(registry)
    with pytest.raises(G.BadReport):
        G.render(root, "2026-09-24")
    r = run("--write", "--date", "2026-09-24", "--root", str(root))
    assert r.returncode == 6 and "data/competitors.json" in r.stdout
    assert "Traceback" not in r.stderr


def test_a_report_that_is_not_an_object_is_bad_input(tmp_path):
    root = make_root(tmp_path)
    (root / "docs/research/competitors/a.json").write_text("[]")
    r = run("--write", "--root", str(root))
    assert r.returncode == 6 and "a.json" in r.stdout and "Traceback" not in r.stderr


def test_the_cli_says_how_many_reports_it_read(tmp_path):
    root = make_root(tmp_path, report("bsuk", ["x"]), report("a", ["x"]), report("b", ["y"]))
    w = run("--write", "--date", "2026-09-24", "--root", str(root))
    assert w.returncode == 0 and "3 reports" in w.stdout, w.stdout
    c = run("--check", "--root", str(root))
    assert c.returncode == 0 and "gap-matrix-2026-09-24.md matches 3 reports" in c.stdout, c.stdout


# --- quality-review fix round -------------------------------------------------------------

def locations(root, *cities):
    (root / "data").mkdir(exist_ok=True)
    (root / "data/locations.json").write_text(json.dumps([{"city": c} for c in cities]))


def cells(line):
    """The cells of a markdown table row, splitting only on unescaped pipes."""
    import re
    parts = re.split(r"(?<!\\)\|", line.strip())
    assert parts[0] == "" and parts[-1] == "", line
    return parts[1:-1]


def table_rows(text):
    return [ln for ln in text.splitlines() if ln.startswith("| ") and not ln.startswith("| Value")]


def test_table_cells_survive_pipes_backticks_and_newlines(tmp_path):
    root = make_root(tmp_path, report("a", ["a|b", "a`b"], cities=["Stoke\non Trent"]))
    locations(root, "Stoke\non Trent")
    text = G.render(root, "2026-09-24")
    rows_ = table_rows(text)
    assert len(rows_) == 3
    assert all(len(cells(r)) == 5 for r in rows_), rows_
    assert "| a\\|b | 1/1 |" in text and "| a`b | 1/1 |" in text
    assert "| Stoke on Trent | 1/1 |" in text


def test_queue_code_spans_survive_backticks_and_newlines(tmp_path):
    root = make_root(tmp_path, report("a", ["a`b"], cities=["Stoke\non Trent"]))
    locations(root, "Stoke\non Trent")
    text = G.render(root, "2026-09-24")
    queue_lines = [ln for ln in text.splitlines() if ln[:3] in ("1. ", "2. ", "3. ")]
    assert len(queue_lines) == 2, queue_lines
    assert "keywords `` a`b `` — 1/1" in text
    assert "cities `Stoke on Trent` — 1/1" in text


def test_a_city_not_in_locations_is_bad_input(tmp_path):
    root = make_root(tmp_path, report("a", cities=["Atlantis"]))
    locations(root, "Manchester")
    with pytest.raises(G.BadReport, match=r"a\.json.*Atlantis"):
        G.load_reports(root)
    r = run("--write", "--root", str(root))
    assert r.returncode == 6 and "Atlantis" in r.stdout and "a.json" in r.stdout


def test_a_city_in_the_wrong_case_points_at_the_canonical_spelling(tmp_path):
    root = make_root(tmp_path, report("a", cities=["manchester"]))
    locations(root, "Manchester")
    r = run("--write", "--root", str(root))
    assert r.returncode == 6 and "'manchester'" in r.stdout and "'Manchester'" in r.stdout


@pytest.mark.parametrize("content", [None, "{not json", '{"city": "Leeds"}', '[{"town": "Leeds"}]'])
def test_fetched_cities_with_no_readable_locations_file_is_bad_input(tmp_path, content):
    root = make_root(tmp_path, report("a", cities=["Leeds"]))
    if content is not None:
        (root / "data").mkdir()
        (root / "data/locations.json").write_text(content)
    r = run("--write", "--root", str(root))
    assert r.returncode == 6 and "data/locations.json" in r.stdout
    assert "Traceback" not in r.stderr


def test_a_stray_matrix_name_is_ignored(tmp_path):
    root = make_root(tmp_path, report("a", ["x"]))
    assert run("--write", "--date", "2026-09-24", "--root", str(root)).returncode == 0
    (root / "docs/research/gap-matrix-draft.md").write_text("scratch notes\n")
    r = run("--check", "--root", str(root))
    assert r.returncode == 0 and "gap-matrix-2026-09-24.md" in r.stdout, r.stdout


def test_an_impossible_date_is_refused(tmp_path):
    root = make_root(tmp_path, report("a", ["x"]))
    r = run("--write", "--date", "2026-13-45", "--root", str(root))
    assert r.returncode == 2 and "2026-13-45" in r.stdout
    assert not (root / "docs/research/gap-matrix-2026-13-45.md").exists()


def test_check_reports_a_bad_report_even_with_no_matrix(tmp_path):
    bad = report("a")
    bad["keywords"] = {"status": "maybe"}
    r = run("--check", "--root", str(make_root(tmp_path, bad)))
    assert r.returncode == 6 and "a.json" in r.stdout


def test_an_unreadable_matrix_is_bad_input_not_a_traceback(tmp_path):
    root = make_root(tmp_path, report("a", ["x"]))
    (root / "docs/research/gap-matrix-2026-09-24.md").write_bytes(b"\xff\xfe\x00bad")
    r = run("--check", "--root", str(root))
    assert r.returncode == 6 and "gap-matrix-2026-09-24.md" in r.stdout
    assert "Traceback" not in r.stderr


@pytest.mark.parametrize("mode", [["--write", "--date", "2026-09-24"], ["--check"]])
def test_reports_are_loaded_once_per_run(tmp_path, monkeypatch, mode):
    root = make_root(tmp_path, report("a", ["x"]))
    G.main(["--write", "--date", "2026-09-24", "--root", str(root)])
    calls = []
    real = G.load_reports
    monkeypatch.setattr(G, "load_reports", lambda r=G.ROOT: calls.append(r) or real(r))
    assert G.main([*mode, "--root", str(root)]) == 0
    assert len(calls) == 1


def test_a_whitespace_only_value_breaks_the_schema(tmp_path):
    with pytest.raises(G.BadReport):
        G.load_reports(make_root(tmp_path, report("a", ["  "])))


def test_schema_types_keep_their_case(tmp_path):
    root = make_root(tmp_path, report("a", schema_types=[" LocalBusiness "]),
                     report("b", schema_types=["LocalBusiness"]))
    text = G.render(root, "2026-09-24")
    assert "| LocalBusiness | 2/2 |" in text and "localbusiness" not in text


def test_registry_ids_are_deduped_and_bsuk_is_not_missing(tmp_path):
    root = make_root(tmp_path, report("a", ["x"]))
    (root / "data").mkdir()
    (root / "data/competitors.json").write_text(json.dumps(
        {"competitors": [{"id": "a"}, {"id": "b"}, {"id": "b"}, {"id": "bsuk"}]}))
    text = G.render(root, "2026-09-24")
    assert "\nNo report yet: b\n" in text and "Registry entries: 2\n" in text


def test_help_exits_0():
    r = run("--help")
    assert r.returncode == 0 and "gap matrix" in r.stdout


def test_a_differing_matrix_shows_the_first_difference(tmp_path):
    root = make_root(tmp_path, report("a", ["x"]))
    run("--write", "--date", "2026-09-24", "--root", str(root))
    out = root / "docs/research/gap-matrix-2026-09-24.md"
    out.write_text(out.read_text().replace("1/1", "5/1"))
    r = run("--check", "--root", str(root))
    assert r.returncode == 1
    assert "-| x | 1/1 | 0 | not fetched | high |" in r.stdout
    assert "+| x | 5/1 | 0 | not fetched | high |" in r.stdout


def test_the_agent_fixture_report_is_schema_valid(tmp_path):
    # The keyword-gap agent's RED/GREEN fixture must pass the same load the real reports do:
    # the schema, the file-name id and the cities checked against data/locations.json.
    fixture = REPO / "tests/py/fixtures/competitors/report-example-breeder.json"
    d = tmp_path / "docs/research/competitors"
    d.mkdir(parents=True)
    (d / "example-breeder.json").write_text(fixture.read_text())
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text((REPO / "data/locations.json").read_text())
    bsuk, comps = G.load_reports(tmp_path)
    assert bsuk is None
    assert list(comps) == ["example-breeder"]
    assert comps["example-breeder"]["pages"]["status"] == "ok"
