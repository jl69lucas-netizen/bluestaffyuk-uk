# tests/py/test_strategy_cite_check.py — scripts/strategy_cite_check.py (spec §9).
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import strategy_cite_check as S  # noqa: E402

SCRIPT = REPO / "scripts" / "strategy_cite_check.py"
SOURCE = "docs/research/gap-matrix-2026-09-24.md"


def make(tmp_path, recommendation, source_text="| city | 7/12 | 0 | no | high |\n1,200 words\n",
         sources=(SOURCE,), artifact=""):
    (tmp_path / "docs/research/competitors").mkdir(parents=True, exist_ok=True)
    (tmp_path / SOURCE).write_text(source_text)
    src = "\n".join(f"- `{s}`" for s in sources)
    doc = (f"# Strategy\n\n## Strategy A — Cities\n\nMost of the pages.\n\n"
           f"## Recommendation\n\n{recommendation}\n\n{artifact}"
           f"## Sources\n\n{src}\n")
    p = tmp_path / "strategy.md"
    p.write_text(doc)
    return p


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_figures_found_in_a_source_pass(tmp_path):
    p = make(tmp_path, "Pick A: 7/12 competitors have city pages; theirs run 1,200 words.")
    assert S.check(p, tmp_path) == []


def test_a_figure_in_no_source_fails_with_its_line(tmp_path):
    p = make(tmp_path, "Pick A: 9/12 competitors have city pages.")
    out = S.check(p, tmp_path)
    assert len(out) == 1 and "9/12" in out[0] and "line" in out[0]


def test_percentages_and_decimals_are_checked(tmp_path):
    out = S.check(make(tmp_path, "58% of them, a 0.75 share."), tmp_path)
    assert any("58%" in o for o in out) and any("0.75" in o for o in out)


def test_figures_outside_the_checked_sections_are_not_checked(tmp_path):
    # The preamble and a heading before the strategies are not checked (Known Issue 49 only
    # adds Strategy A and B).
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    (tmp_path / SOURCE).write_text("7/12")
    p = tmp_path / "s.md"
    p.write_text("99 pages in the preamble.\n\n# S\n\n## How the research was read\n\n98 rows.\n\n"
                 f"## Recommendation\n\n7/12\n\n## Sources\n\n- `{SOURCE}`\n")
    assert S.check(p, tmp_path) == []


def test_dates_code_single_digits_and_the_city_count_are_not_figures(tmp_path):
    p = make(tmp_path, "Pick A (`gap-matrix-2026-09-24.md`, 2026-09-24): 3 steps, all 28 cities.")
    assert S.check(p, tmp_path) == []


def test_the_artefact_table_is_checked_too(tmp_path):
    art = "## Concrete Artifact\n\n| topic | score |\n|---|---|\n| cities | 11 |\n\n"
    out = S.check(make(tmp_path, "Pick A: 7/12.", artifact=art), tmp_path)
    assert any("11" in o and "Concrete Artifact" in o for o in out)


def test_a_listed_source_that_does_not_exist_fails(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.", sources=(SOURCE, "docs/research/competitors/nope.md"))
    assert any("nope.md" in o and "does not exist" in o for o in S.check(p, tmp_path))


def test_no_sources_section_fails(tmp_path):
    p = tmp_path / "s.md"
    p.write_text("# S\n\n## Recommendation\n\nPick A.\n")
    assert any("## Sources" in o for o in S.check(p, tmp_path))


def test_no_recommendation_fails(tmp_path):
    p = tmp_path / "s.md"
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    (tmp_path / SOURCE).write_text("x")
    p.write_text(f"# S\n\n## Sources\n\n- `{SOURCE}`\n")
    assert any("## Recommendation" in o for o in S.check(p, tmp_path))


def test_cli_exit_codes(tmp_path):
    good = make(tmp_path, "Pick A: 7/12.")
    r = run(str(good), "--root", str(tmp_path))
    assert r.returncode == 0
    bad = make(tmp_path, "Pick A: 8/12.")
    r = run(str(bad), "--root", str(tmp_path))
    assert r.returncode == 1 and "8/12" in r.stdout
    r = run(str(tmp_path / "missing.md"))
    assert r.returncode == 2


# --- review-driven hardening: no tracebacks, a summary, --help, sources stay in root ---

def test_the_summary_says_what_was_examined(tmp_path):
    p = make(tmp_path, "Pick A: 7/12 competitors; theirs run 1,200 words.")
    r = run(str(p), "--root", str(tmp_path))
    assert r.returncode == 0
    assert "cite-check: strategy.md: 1 source, 2 figures checked, 0 problems" in r.stdout


def test_the_summary_counts_problems(tmp_path):
    p = make(tmp_path, "Pick A: 8/12 and 9/12.")
    r = run(str(p), "--root", str(tmp_path))
    assert r.returncode == 1
    assert "cite-check: strategy.md: 1 source, 2 figures checked, 2 problems" in r.stdout


def test_help_exits_0():
    r = run("--help")
    assert r.returncode == 0 and "may quote only" in r.stdout
    assert "Traceback" not in r.stderr


def test_bad_usage_exits_2():
    r = run()
    assert r.returncode == 2 and "Traceback" not in r.stderr


def test_a_strategy_that_is_a_directory_exits_2(tmp_path):
    r = run(str(tmp_path), "--root", str(tmp_path))
    assert r.returncode == 2 and "Traceback" not in r.stderr and "cite-check:" in r.stdout


def test_a_strategy_that_is_not_utf8_exits_2(tmp_path):
    p = tmp_path / "s.md"
    p.write_bytes(b"## Recommendation\n\n\xff\xfe 7/12\n")
    r = run(str(p), "--root", str(tmp_path))
    assert r.returncode == 2 and "Traceback" not in r.stderr and "cite-check:" in r.stdout


def test_a_strategy_that_cannot_be_read_exits_2(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.")
    p.chmod(0)
    try:
        if os.access(p, os.R_OK):
            return  # running as root: permissions are not enforced
        r = run(str(p), "--root", str(tmp_path))
        assert r.returncode == 2 and "Traceback" not in r.stderr and "cite-check:" in r.stdout
    finally:
        p.chmod(0o644)


def test_a_source_that_is_a_directory_is_a_problem(tmp_path):
    (tmp_path / "docs/research/competitors/adir.md").mkdir(parents=True)
    p = make(tmp_path, "Pick A: 7/12.", sources=(SOURCE, "docs/research/competitors/adir.md"))
    out = S.check(p, tmp_path)
    assert len(out) == 1 and "docs/research/competitors/adir.md" in out[0] and "not a file" in out[0]


def test_a_source_that_is_not_utf8_is_a_problem(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.", sources=(SOURCE, "docs/research/competitors/bin.md"))
    (tmp_path / "docs/research/competitors/bin.md").write_bytes(b"\xff\xfe 8/12")
    out = S.check(p, tmp_path)
    assert len(out) == 1 and "bin.md" in out[0] and "UTF-8" in out[0]


def test_a_source_that_cannot_be_read_is_a_problem(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.", sources=(SOURCE, "docs/research/competitors/locked.md"))
    locked = tmp_path / "docs/research/competitors/locked.md"
    locked.write_text("7/12")
    locked.chmod(0)
    try:
        if os.access(locked, os.R_OK):
            return  # running as root
        out = S.check(p, tmp_path)
        assert len(out) == 1 and "locked.md" in out[0] and "cannot be read" in out[0]
    finally:
        locked.chmod(0o644)


def test_an_absolute_source_path_is_a_problem(tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("8/12")
    root = tmp_path / "root"
    root.mkdir()
    p = make(root, "Pick A: 8/12.", sources=(SOURCE, str(outside)))
    out = S.check(p, root)
    assert any(str(outside) in o and "not a research source" in o for o in out)
    assert any("8/12" in o for o in out)  # its figures do not count


def test_a_source_that_escapes_the_root_is_a_problem(tmp_path):
    (tmp_path / "outside.md").write_text("8/12")
    root = tmp_path / "root"
    root.mkdir()
    p = make(root, "Pick A: 8/12.", sources=(SOURCE, "../outside.md"))
    out = S.check(p, root)
    assert any("../outside.md" in o and "not a research source" in o for o in out)
    assert any("8/12" in o for o in out)


def test_a_dotdot_path_that_stays_inside_the_root_is_fine(tmp_path):
    p = make(tmp_path, "Pick A: 7/12.", sources=("docs/research/../research/gap-matrix-2026-09-24.md",))
    assert S.check(p, tmp_path) == []


# --- fix round: token matching, wider extraction, headings, source scope, no tracebacks ---

def doc(tmp_path, body, source_text, sources="- `docs/research/competitors/src.md`"):
    """A strategy whose whole Recommendation body is `body`, and one research source."""
    (tmp_path / "docs/research/competitors").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/research/competitors/src.md").write_text(source_text)
    p = tmp_path / "s.md"
    p.write_text(f"# S\n\n## Recommendation\n\n{body}\n\n## Sources\n\n{sources}\n")
    return p


def fails(tmp_path, body, source_text, fig):
    out = S.check(doc(tmp_path, body, source_text), tmp_path)
    return any(f"figure {fig} " in o for o in out)


def passes(tmp_path, body, source_text):
    return S.check(doc(tmp_path, body, source_text), tmp_path) == []


# C1: a figure matches a whole figure in the source, never part of one
def test_c1_12_is_not_found_inside_2012(tmp_path):
    assert fails(tmp_path, "Pick A: 12 competitors.", "Founded 2012.", "12")


def test_c1_40_is_not_found_inside_1400(tmp_path):
    assert fails(tmp_path, "Pick A: 40 pages.", "1,400 words", "40")


def test_c1_7_12_is_not_found_inside_17_120(tmp_path):
    assert fails(tmp_path, "Pick A: 7/12.", "17/120", "7/12")


def test_c1_a_date_in_the_source_is_not_a_figure(tmp_path):
    assert fails(tmp_path, "Pick A: 24 cities.", "# Gap matrix — 2026-09-24\n", "24")


def test_c1_the_parts_of_a_source_count_may_be_cited(tmp_path):
    assert passes(tmp_path, "Pick A: 12 competitors, 7 with city pages; 7/12.", "| city | 7/12 |")


def test_c1_50pct_is_not_found_inside_150pct(tmp_path):
    assert fails(tmp_path, "Pick A: 50% gain.", "150%", "50%")


def test_c1_thousands_commas_do_not_matter(tmp_path):
    assert passes(tmp_path, "Pick A: 1,500 words.", "1500 words")


# C2: numbers glued to units or words are still figures
def test_c2_glued_shapes_are_extracted():
    got = S.figures("1,200-word 12-page 40k £12k 2.5x 3x 12th 40/mo -12 20-39% 7/12-competitor")
    assert got == ["1200", "12", "40k", "12k", "2.5x", "3x", "12", "40", "12", "20", "39%", "7/12"]


def test_c2_glued_shapes_are_checked(tmp_path):
    body = "1,200-word pages, 12-page cluster, 40k searches, £12k, 2.5x, 3x, 12th, 40/mo, -12, 20-39%, 7/12-competitor"
    out = S.check(doc(tmp_path, body, "nothing"), tmp_path)
    assert len(out) == 12


def test_c2_glued_shapes_pass_when_the_source_has_them(tmp_path):
    body = "1,200-word pages, 12-page cluster, 40k searches, £12k, 2.5x, 3x, 12th, 40/mo, -12, 20-39%, 7/12-competitor"
    src = "1200 words; 12 pages; 40k; 12k; 2.5x; 3x; 40; 20 to 39%; 7/12"
    assert passes(tmp_path, body, src)


def test_c2_a_k_or_x_figure_needs_its_suffix_in_the_source(tmp_path):
    assert fails(tmp_path, "Pick A: 40k searches.", "40 searches", "40k")
    assert fails(tmp_path, "Pick A: 3x faster.", "3 times", "3x")


def test_c2_a_percentage_needs_its_percent_sign(tmp_path):
    assert fails(tmp_path, "Pick A: 39% of them.", "39 of them", "39%")
    assert passes(tmp_path, "Pick A: 40% share.", "share 40 %")


def test_c2_units_are_not_compared(tmp_path):
    assert passes(tmp_path, "Pick A: a 12-page cluster.", "12 pages")


# I1: heading variants
def test_i1_concrete_artefact_is_checked(tmp_path):
    p = doc(tmp_path, "Pick A.\n\n## Concrete Artefact\n\n| cities | 11 |", "nothing")
    assert any("figure 11 " in o and "Concrete Artefact" in o for o in S.check(p, tmp_path))


def test_i1_heading_variants_are_recognised(tmp_path):
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    (tmp_path / "docs/research/competitors/src.md").write_text("x")
    for heading in ("## recommendation", "##\tRecommendation", "## 5. Recommendation",
                    "## Recommendation:", "## Recommendation (Strategy A)",
                    "## CONCRETE ARTIFACT"):
        p = tmp_path / "s.md"
        p.write_text(f"{heading}\n\n99 pages\n\n## Sources\n\n- `docs/research/competitors/src.md`\n")
        out = S.check(p, tmp_path)
        assert any("figure 99 " in o for o in out), heading


# I2: sources are research files
def test_i2_a_source_outside_research_and_data_is_a_problem(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src/page.md").write_text("99")
    p = doc(tmp_path, "Pick A: 99 pages.", "x", sources="- `docs/research/competitors/src.md`\n- `src/page.md`")
    out = S.check(p, tmp_path)
    assert any("src/page.md" in o and "not a research source" in o for o in out)
    assert any("figure 99 " in o for o in out)


def test_i2_a_data_source_is_fine(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/competitors.json").write_text('{"n": 99}')
    p = doc(tmp_path, "Pick A: 99 pages.", "x", sources="- `docs/research/competitors/src.md`\n- `data/competitors.json`")
    assert S.check(p, tmp_path) == []


def test_i2_the_strategy_cannot_cite_itself(tmp_path):
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    p = tmp_path / "docs/research/competitors/strategy.md"
    p.write_text("## Recommendation\n\n99 pages\n\n## Sources\n\n- `docs/research/competitors/strategy.md`\n")
    out = S.check(p, tmp_path)
    assert any("docs/research/competitors/strategy.md" in o and "itself" in o for o in out)
    assert any("figure 99 " in o for o in out)


# I3: bad source paths are problems, not tracebacks
def test_i3_a_nul_byte_in_a_source_path_is_a_problem(tmp_path):
    p = doc(tmp_path, "Pick A: 7/12.", "7/12", sources="- `docs/research/competitors/src.md`\n- `docs/research/competitors/a\x00b.md`")
    out = S.check(p, tmp_path)
    assert len(out) == 1 and "cannot be read" in out[0]


def test_i3_an_over_long_source_path_is_a_problem(tmp_path):
    long = "docs/research/competitors/" + "a" * 5000 + ".md"
    p = doc(tmp_path, "Pick A: 7/12.", "7/12", sources=f"- `docs/research/competitors/src.md`\n- `{long}`")
    out = S.check(p, tmp_path)
    assert len(out) == 1 and "cannot be read" in out[0]
    r = run(str(p), "--root", str(tmp_path))
    assert r.returncode == 1 and "Traceback" not in r.stderr


# I4: years and clock times are not figures
def test_i4_years_and_times_are_not_figures(tmp_path):
    assert passes(tmp_path, "Ship in Q3 2027, by 2027, at 10:30.", "nothing")


# Minor: code fences, links, comments, BOM, Sources parsing
def test_fenced_code_is_skipped_and_cannot_switch_sections(tmp_path):
    body = "Pick A.\n\n```\n99 pages\n## Sources\n- `docs/research/competitors/src.md`\n```\n\n~~~\n98\n~~~"
    p = tmp_path / "s.md"
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    (tmp_path / "docs/research/competitors/src.md").write_text("x")
    p.write_text(f"## Recommendation\n\n{body}\n\n77 pages\n")
    out = S.check(p, tmp_path)
    assert any("figure 77 " in o for o in out)  # still in Recommendation after the fence
    assert not any("99" in o or "98" in o for o in out)
    assert any("no ## Sources" in o for o in out)


def test_link_urls_and_html_comments_are_not_figures(tmp_path):
    assert passes(tmp_path, "See [the matrix](https://x.test/p/99) <!-- 98 --> now.", "nothing")
    assert fails(tmp_path, "See [99 pages](https://x.test/p/1).", "nothing", "99")


def test_ordered_list_markers_are_not_figures(tmp_path):
    assert passes(tmp_path, "10. Build the page.\n11) Link it.", "nothing")


def test_a_bom_is_ignored(tmp_path):
    p = doc(tmp_path, "Pick A: 7/12.", "7/12")
    p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
    assert S.check(p, tmp_path) == []


def test_sources_heading_and_bullet_variants(tmp_path):
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    for name in ("a.md", "b.md", "c.md", "d.md", "e.md"):
        (tmp_path / "docs/research/competitors" / name).write_text(f"{name} 7/12")
    lists = ["* `docs/research/competitors/a.md`", "+ `docs/research/competitors/a.md`", "1. `docs/research/competitors/a.md`",
             "- Gap matrix: `docs/research/competitors/a.md`", "- [gap matrix](docs/research/competitors/a.md)",
             "- [`docs/research/competitors/a.md`](docs/research/competitors/a.md)"]
    for heading in ("## Sources", "## sources:", "## Sources (3)"):
        for item in lists:
            p = tmp_path / "s.md"
            p.write_text(f"## Recommendation\n\n7/12\n\n{heading}\n\n{item}\n")
            assert S.examine(p, tmp_path)[:2] == ([], 1), (heading, item)
    p = tmp_path / "s.md"
    p.write_text("## Recommendation\n\n99\n\n## Sources\n\n- `docs/research/competitors/a.md`, `docs/research/competitors/b.md`\n")
    (tmp_path / "docs/research/competitors/b.md").write_text("99")
    assert S.examine(p, tmp_path)[:2] == ([], 2)


def test_a_sources_heading_with_no_paths_says_so(tmp_path):
    p = tmp_path / "s.md"
    p.write_text("## Recommendation\n\nPick A.\n\n## Sources\n\n- the gap matrix\n")
    assert S.check(p, tmp_path) == ["## Sources lists no backticked or linked paths"]


# --- second fix round ---

def test_r2_a_year_needs_a_cue(tmp_path):
    assert fails(tmp_path, "Pick A: 2000 monthly searches.", "nothing", "2000")
    assert fails(tmp_path, "Pick A: 1950 words.", "nothing", "1950")
    assert passes(tmp_path, "Ship in Q3 2027, by 2027, in September 2027, Sept 2027, "
                            "from early 2027, H2 2026, since 2019, in mid-2027.", "nothing")


def test_r2_only_research_outputs_are_sources(tmp_path):
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    ok = ["docs/research/gap-matrix-2026-09-24.md", "docs/research/keyword-gap-2026-09-24.md",
          "docs/research/competitors/a.json", "docs/research/competitors/a.md",
          "docs/research/llm-intel/q.json", "data/competitors.json", "data/page-map.json",
          "data/locations.json", "data/queries/dog-transport.json"]
    bad = ["docs/research/notes.md", "docs/research/strategy-2026-09-24.md",
           "docs/research/llm-intel/q.md", "docs/research/competitors/x/y.json",
           "data/other.json", "data/queries/x/y.json", "src/page.md"]
    for rel in ok + bad:
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("7/12")
    for rel in ok:
        p = tmp_path / "s.md"
        p.write_text(f"## Recommendation\n\n7/12\n\n## Sources\n\n- `{rel}`\n")
        assert S.check(p, tmp_path) == [], rel
    for rel in bad:
        p = tmp_path / "s.md"
        p.write_text(f"## Recommendation\n\n7/12\n\n## Sources\n\n- `{rel}`\n")
        out = S.check(p, tmp_path)
        assert any(rel in o and "not a research source (allowed:" in o for o in out), rel


def test_r2_top_n_is_a_figure(tmp_path):
    assert S.figures("a top-10 spot, Top-3, top–20") == ["10", "3", "20"]
    assert fails(tmp_path, "Pick A: a top-10 spot.", "nothing", "10")


def test_r2_an_unrecognised_heading_inside_the_pick_is_a_problem(tmp_path):
    body = "Pick A.\n\n## Why A\n\n99 pages.\n\n## Concrete Artifact\n\n| 7/12 |"
    out = S.check(doc(tmp_path, body, "7/12"), tmp_path)
    assert any("unrecognised section inside the pick: ## Why A" in o for o in out)
    assert any("figure 99 " in o for o in out)  # still checked, never silently skipped


def test_r2_headings_before_the_pick_are_fine(tmp_path):
    assert S.check(make(tmp_path, "Pick A: 7/12."), tmp_path) == []  # has ## Strategy A


def test_r2_only_path_like_code_spans_are_sources(tmp_path):
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    (tmp_path / "docs/research/competitors/a.md").write_text("7/12")
    p = tmp_path / "s.md"
    p.write_text("## Recommendation\n\n7/12\n\n## Sources\n\n"
                 "- `docs/research/competitors/a.md` — the `city` rows, `7/12` of them\n")
    assert S.examine(p, tmp_path)[:2] == ([], 1)


# --- Known Issue 49 -------------------------------------------------------------------------

def test_ki49_a_bare_year_says_to_put_a_cue_before_it(tmp_path):
    out = S.check(doc(tmp_path, "Pick A: the 2027 plan.", "nothing"), tmp_path)
    assert len(out) == 1 and "figure 2027 is in no listed source" in out[0], out
    assert 'put a cue word before it ("in 2027"' in out[0], out
    assert 'write it "2,027"' in out[0], out


def test_ki49_the_year_hint_is_only_for_a_bare_19xx_or_20xx(tmp_path):
    out = S.check(doc(tmp_path, "Pick A: 1500 words, 2,050 words, 2100 words.", "nothing"),
                  tmp_path)
    assert len(out) == 3 and not any("cue word" in o for o in out), out


def test_ki49_a_heading_after_sources_is_a_problem(tmp_path):
    p = doc(tmp_path, "Pick A: 7/12.", "7/12",
            sources="- `docs/research/competitors/src.md`\n\n## Notes\n\nLater thoughts.")
    out = S.check(p, tmp_path)
    assert out == ["line 11: ## Notes comes after ## Sources — ## Sources must be the last "
                   "section; move it above ## Recommendation"], out


def test_ki49_a_pick_section_after_sources_is_flagged_and_still_checked(tmp_path):
    p = doc(tmp_path, "Pick A: 7/12.", "7/12",
            sources="- `docs/research/competitors/src.md`\n\n## Concrete Artifact\n\n| 11 |")
    out = S.check(p, tmp_path)
    assert any("## Concrete Artifact comes after ## Sources" in o for o in out), out
    assert any("figure 11 " in o for o in out), out


def test_ki49_a_pick_section_after_sources_is_told_to_move_above_sources(tmp_path):
    # the Concrete Artifact belongs to the pick: "above ## Recommendation" would take it out
    p = doc(tmp_path, "Pick A: 7/12.", "7/12",
            sources="- `docs/research/competitors/src.md`\n\n## Concrete Artifact\n\n7/12")
    out = S.check(p, tmp_path)
    assert any("## Concrete Artifact comes after ## Sources" in o
               and "move it above ## Sources" in o for o in out), out


def test_ki49_a_second_sources_heading_is_told_to_merge(tmp_path):
    p = doc(tmp_path, "Pick A: 7/12.", "7/12",
            sources="- `docs/research/competitors/src.md`\n\n## Sources (cont.)\n\n"
                    "- `docs/research/competitors/src.md`")
    out = S.check(p, tmp_path)
    assert any("## Sources (cont.) comes after ## Sources" in o
               and "merge it into the first ## Sources" in o for o in out), out


def test_ki49_a_top_level_heading_after_sources_is_a_problem_too(tmp_path):
    p = doc(tmp_path, "Pick A: 7/12.", "7/12",
            sources="- `docs/research/competitors/src.md`\n\n# Appendix\n\nMore.")
    out = S.check(p, tmp_path)
    assert any("# Appendix comes after ## Sources" in o for o in out), out


def test_ki49_bullets_under_a_heading_after_sources_are_not_sources(tmp_path):
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    (tmp_path / "docs/research/competitors/b.md").write_text("7/12")
    p = doc(tmp_path, "Pick A: 7/12.", "nothing",
            sources="- `docs/research/competitors/src.md`\n\n## More\n\n"
                    "- `docs/research/competitors/b.md`")
    out, n_sources, _ = S.examine(p, tmp_path)
    assert n_sources == 1 and any("figure 7/12 " in o for o in out), out


def test_ki49_a_risks_heading_inside_the_pick_names_the_rule(tmp_path):
    out = S.check(doc(tmp_path, "Pick A: 7/12.\n\n## Risks\n\n99 pages.", "7/12"), tmp_path)
    assert out == [
        "line 7: unrecognised section inside the pick: ## Risks — only ## Concrete Artifact may "
        "sit between ## Recommendation and ## Sources: make it a ### subheading, or move it "
        "above ## Recommendation (a strategy's risks go under its ## Strategy heading)",
        "line 9 (Risks): figure 99 is in no listed source — ## Risks is not a pick section, but "
        "every figure between ## Recommendation and ## Sources is checked"], out


def strategies(tmp_path, a_text, b_text, source_text="7/12"):
    (tmp_path / "docs/research/competitors").mkdir(parents=True, exist_ok=True)
    (tmp_path / SOURCE).write_text(source_text)
    p = tmp_path / "s.md"
    p.write_text(f"# S\n\n## Strategy A — Cities first\n\n{a_text}\n\n"
                 f"## Strategy B: guides first\n\n### Risks\n\n{b_text}\n\n"
                 f"## Recommendation\n\nPick A: 7/12.\n\n## Sources\n\n- `{SOURCE}`\n")
    return p


def test_ki49_figures_in_strategy_a_and_b_are_checked(tmp_path):
    out = S.check(strategies(tmp_path, "About 99 pages.", "Around 58% of them."), tmp_path)
    assert len(out) == 2, out
    assert out[0].startswith("line 5 (Strategy A — Cities first): figure 99 "), out
    assert out[1].startswith("line 11 (Strategy B: guides first): figure 58% "), out


def test_ki49_sourced_figures_in_strategy_a_and_b_pass(tmp_path):
    p = strategies(tmp_path, "7/12 have city pages.", "Of 12 competitors.")
    assert S.examine(p, tmp_path) == ([], 1, 3)


def test_ki49_a_strategy_heading_inside_the_pick_is_still_a_problem(tmp_path):
    out = S.check(doc(tmp_path, "Pick A: 7/12.\n\n## Strategy A again\n\nMore.", "7/12"),
                  tmp_path)
    assert any("unrecognised section inside the pick: ## Strategy A again" in o for o in out)


def test_ki49_the_committed_strategy_still_passes():
    r = run(str(REPO / "docs/superpowers/sessions/2026-09-23-location-pages-strategy.md"))
    assert r.returncode == 0, r.stdout


def test_ki49_any_spacing_of_strategy_a_is_checked(tmp_path):
    (tmp_path / "docs/research/competitors").mkdir(parents=True)
    (tmp_path / SOURCE).write_text("7/12")
    p = tmp_path / "s.md"
    p.write_text("# S\n\n## Strategy  A\n\nAbout 99 pages.\n\n## Strategy\tB\n\n58% of them.\n\n"
                 f"## Recommendation\n\n7/12\n\n## Sources\n\n- `{SOURCE}`\n")
    out = S.check(p, tmp_path)
    assert len(out) == 2, out
    assert out[0].startswith("line 5 (Strategy  A): figure 99 "), out
    assert out[1].startswith("line 9 (Strategy\tB): figure 58% "), out
