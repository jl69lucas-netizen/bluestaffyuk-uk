"""The review of the outline-stop work (2026-09-29): every way STOP 2 could be bypassed, and the
research-board and outline gaps against the source system's deliverables, each pinned here.

B1 a copied approval clears another page · B2 a stale research board reaches the gate ·
B3 the two approvals are separate answers files that name the slug and the stop ·
B4 board approval and the component previews wait for STOP 2 · B5 rule-9 evidence is a saved
fetch in the repo or a different, dated URL · B6 the Artifact cannot run injected markup ·
B7 a bare NOT FETCHED is refused everywhere, heading counts are integers · B8 malformed shapes
are problems, not crashes · B9 the research hash covers the query-file values it renders ·
B10 the copy/download heading carries no HTML entities · parity: AI Overview, heading types,
SERP schema, authority; the outline's census, framework, grounding, H1 and keyword rules.
"""
import copy
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests/py"))

import _md_artifact as MA  # noqa: E402
import _stop_kit as K  # noqa: E402
import board_approve as BA  # noqa: E402
import build_board_previews as BBP  # noqa: E402
import outline_matrix as OM  # noqa: E402
import pageboard as PB  # noqa: E402
import research_board as RB  # noqa: E402

NEW = "blue-staffy-puppies-for-sale-leeds"
OTHER = "blue-staffy-puppies-manchester-uk"
FIX = ROOT / "tests/py/fixtures"


def _rec():
    return json.loads((FIX / "research_board/record.json").read_text())


def _q():
    return json.loads((FIX / "research_board/queries.json").read_text())


def _load(p):
    return json.loads(pathlib.Path(p).read_text())


def _save(p, doc):
    pathlib.Path(p).write_text(json.dumps(doc))


# --- B1 ---------------------------------------------------------------------------------

def test_b1_a_copied_approval_does_not_clear_another_page(tmp_path):
    paths = K.lay_out(tmp_path, NEW)
    assert OM.approval_refusal(NEW, tmp_path) is None
    other = tmp_path / "data/outlines" / f"{OTHER}.json"
    other.write_text(paths["outline"].read_text())          # the same record, copied
    msg = OM.approval_refusal(OTHER, tmp_path) or ""
    assert "is for" in msg and NEW in msg, msg


# --- B2 ---------------------------------------------------------------------------------

def test_b2_a_research_board_edited_after_the_outline_approval_refuses(tmp_path):
    paths = K.lay_out(tmp_path, NEW)
    research = _load(paths["research"])
    research["how_we_win"].append("an edit after both approvals")
    research = RB.approve(dict(research, approval=None),
                          K.answers(tmp_path, NEW, "research-board", name="second"),
                          today="2026-09-30", root=tmp_path)          # re-approved, new hash
    _save(paths["research"], research)
    msg = OM.approval_refusal(NEW, tmp_path) or ""
    assert "research board" in msg and "changed" in msg, msg


def test_b2_an_unapproved_research_board_refuses_the_gate(tmp_path):
    paths = K.lay_out(tmp_path, NEW)
    research = _load(paths["research"])
    research["approval"] = None
    _save(paths["research"], research)
    assert "research board" in (OM.approval_refusal(NEW, tmp_path) or "")


# --- B3 ---------------------------------------------------------------------------------

def test_b3_a_file_that_is_not_an_answers_file_is_refused(tmp_path):
    rec = copy.deepcopy(_rec())
    (tmp_path / "README.md").write_text("# not answers\n")
    with pytest.raises(RB.RecordError, match="answers"):
        RB.approve(rec, "README.md", root=tmp_path, queries=_q())


def test_b3_the_answers_must_name_the_slug_and_the_stop(tmp_path):
    rec = copy.deepcopy(_rec())
    wrong_slug = K.answers(tmp_path, OTHER, "research-board")
    with pytest.raises(RB.RecordError, match="fixture-city"):
        RB.approve(rec, wrong_slug, root=tmp_path, queries=_q())
    wrong_stop = K.answers(tmp_path, "fixture-city", "outline")
    with pytest.raises(RB.RecordError, match="research-board"):
        RB.approve(rec, wrong_stop, root=tmp_path, queries=_q())


def test_b3_the_outline_cannot_reuse_the_research_boards_answers(tmp_path):
    paths = K.lay_out(tmp_path, NEW, outline_approved=False)
    research = _load(paths["research"])
    out = _load(paths["outline"])
    with pytest.raises(OM.OutlineError, match="same answers"):
        OM.approve(out, research["approval"]["answers"], root=tmp_path)


def test_b3_an_unanswered_batch_is_refused(tmp_path):
    rel = K.answers(tmp_path, "fixture-city", "research-board")
    doc = _load(tmp_path / rel)
    doc["data"]["answers"][0]["status"] = "not_yet"
    _save(tmp_path / rel, doc)
    with pytest.raises(RB.RecordError, match="answered"):
        RB.approve(copy.deepcopy(_rec()), rel, root=tmp_path, queries=_q())


# --- B4 ---------------------------------------------------------------------------------

def test_b4_board_approval_refuses_a_new_page_without_stop_2(monkeypatch, tmp_path):
    monkeypatch.setattr(OM, "ROOT", tmp_path)
    monkeypatch.setattr(PB.FR, "findings", lambda b, o: [])
    monkeypatch.setattr(PB, "authorization_check", lambda b, o: {"blocked": []})
    board = {"meta": {"slug": NEW, "page_type": "location"}, "sections": []}
    with pytest.raises(PB.BoardError, match="outline-unapproved"):
        BA.refuse_on_new_page_rules(board, {})
    K.lay_out(tmp_path, NEW)
    BA.refuse_on_new_page_rules(board, {})                      # STOP 2 recorded: no refusal


def test_b4_component_previews_wait_for_stop_2(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(OM, "ROOT", tmp_path)

    def reached(slug):
        raise SystemExit("reached load_board")
    monkeypatch.setattr(PB, "load_board", reached)
    assert BBP.main([NEW]) == 2
    assert "outline-unapproved" in capsys.readouterr().out
    K.lay_out(tmp_path, NEW)
    with pytest.raises(SystemExit, match="reached load_board"):
        BBP.main([NEW])


# --- B5 ---------------------------------------------------------------------------------

def _evidence_problems(ev, root, fetched=None, url=None):
    rec, q = _rec(), _q()
    row = rec["serp"]["results"][0]
    row["evidence"] = ev
    if url:
        row["url"] = url
    row.pop("fetched", None)
    if fetched:
        row["fetched"] = fetched
    return [p for p in RB.validate(rec, q, root) if "serp.results[0]" in p and "evidence" in p]


def test_b5_evidence_rules(tmp_path):
    (tmp_path / "data/queries/cache").mkdir(parents=True)
    (tmp_path / "data/queries/cache/marketplace.html").write_text("<html></html>")
    (tmp_path / "docs/research").mkdir(parents=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src/x.html").write_text("x")
    ok = "data/queries/cache/marketplace.html"
    assert _evidence_problems(ok, tmp_path) == []
    for bad in (".", "data/queries/cache", "docs/research", "/etc/hosts",
                "../outside.html", "src/x.html", "data/queries/cache/missing.html"):
        assert _evidence_problems(bad, tmp_path), bad
    own = _rec()["serp"]["results"][0]["url"]
    assert _evidence_problems(own, tmp_path, fetched="2026-09-29"), "its own URL is not evidence"
    other = "https://web.archive.org/web/2026/https://marketplace.example/fixture-city/"
    assert _evidence_problems(other, tmp_path), "a URL needs its fetched date"
    assert _evidence_problems(other, tmp_path, fetched="2026-09-29") == []


# --- B6 and B10 -------------------------------------------------------------------------

def test_b6_injected_markup_is_escaped_and_sanitised():
    body = 'He said "<img src=x onerror=alert(1)>" and </SCRIPT><script>alert(2)</script>'
    page = MA.page("T", "E", "Head & Tail", "s", "d", "r", [("Owner Language", body)], "t.md")
    assert not re.search(r"</script\s*>\s*<script>alert", page, re.I)
    assert "</SCRIPT>" not in page and "</script><script>alert(2)" not in page
    purify = page.index("dompurify")
    assert re.search(r"cdnjs\.cloudflare\.com/ajax/libs/dompurify/\d+\.\d+\.\d+/purify\.min\.js", page)
    assert purify < page.index("DOMPurify.sanitize")
    assert "body.textContent=md" in page          # no library: shown as text, never innerHTML


def test_b10_the_copy_heading_carries_no_entities():
    page = MA.page("T", "E", "Fish & Chips <b>", "s", "d", "r", [("A", "b")], "t.md")
    head = re.search(r'<script type="text/plain" id="md-head">(.*?)</script>', page, re.S).group(1)
    assert head == "Fish & Chips <b>", head


# --- B7 ---------------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    ("intent", "local"), ("why_competitors_rank",), ("serp", "structural_read"),
    ("fanout", "llm_intel"), ("owner_language",), ("universal_gaps", 0),
])
def test_b7_a_bare_not_fetched_is_refused_everywhere(path):
    rec = _rec()
    cur = rec
    for k in path[:-1]:
        cur = cur[k]
    cur[path[-1]] = "NOT FETCHED"
    assert any("bare NOT FETCHED" in p for p in RB.validate(rec, _q())), path


def test_b7_heading_counts_are_whole_numbers():
    rec = _rec()
    rec["reverse_engineering"][0]["headings"] = {"h1": "one", "h2": 1.5}
    problems = RB.validate(rec, _q())
    assert sum("headings.h" in p and "whole number" in p for p in problems) == 2, problems


# --- B8 ---------------------------------------------------------------------------------

MALFORMED = [
    ("serp", "a string"), ("serp", {"results": "x"}), ("serp", {"results": ["x"]}),
    ("intent", ["x"]), ("reverse_engineering", "x"), ("reverse_engineering", ["x"]),
    ("universal_gaps", "x"), ("owner_language", [1]), ("fanout", "x"), ("entities", ["x"]),
    ("angles", ["x"]), ("strategies", "x"), ("frameworks", ["x"]),
    ("frameworks", [{"group": "g", "options": "QAB"}]),
    ("keywords", "x"), ("keywords", {"universe": ["x"], "distribution": ["x"]}),
    ("keywords", {"universe": [{"keyword": "k", "intent": "local", "volume": 1}],
                  "distribution": [{"section": "s", "primary": "k"}]}),
    ("ai_overview", ["x"]), ("heading_types", "x"), ("serp_schema", {"x": 1}),
    ("authority", ["x"]),
]


@pytest.mark.parametrize("field, value", MALFORMED)
def test_b8_a_malformed_field_is_a_problem_not_a_crash(field, value):
    rec = _rec()
    rec[field] = value
    assert RB.validate(rec, _q()), (field, value)


@pytest.mark.parametrize("queries", [{"competitors": "x"}, {"competitors": ["x"]},
                                     {"competitors": [{"url": 1}]}, []])
def test_b8_a_malformed_query_file_is_a_problem_not_a_crash(queries):
    assert RB.validate(_rec(), queries)


def test_b8_the_cli_exits_1_on_a_malformed_record_and_2_on_an_unreadable_query_file(tmp_path, capsys):
    rec = _rec()
    rec["serp"] = "a string"
    p = tmp_path / "r.json"
    p.write_text(json.dumps(rec))
    assert RB.main(["fixture-city", "--record", str(p), "--queries",
                    str(FIX / "research_board/queries.json"), "--check"]) == 1
    bad_q = tmp_path / "q.json"
    bad_q.write_text("[not json")
    assert RB.main(["fixture-city", "--record", str(FIX / "research_board/record.json"),
                    "--queries", str(bad_q), "--check"]) == 2


@pytest.mark.parametrize("field, value", [
    ("sections", "x"), ("sections", ["x"]), ("word_target", "x"),
    ("sections", [{"n": "1", "headings": "x"}]), ("sections", [{"n": "1", "headings": ["x"]}]),
    ("sections", [{"n": "1", "keywords": "x", "headings": []}]),
])
def test_b8_a_malformed_outline_is_a_problem_not_a_crash(field, value):
    rec = _load(FIX / "outline_matrix/good.json")
    rec[field] = value
    assert OM.validate(rec, OM.research_for(_load(FIX / "outline_matrix/good.json")))


# --- B9 ---------------------------------------------------------------------------------

def test_b9_the_research_hash_covers_the_query_file_values():
    rec, q = _rec(), _q()
    before = RB.record_hash(rec, q)
    q["competitors"][1]["words"] += 1
    assert RB.record_hash(rec, q) != before
    q = _q()
    q["competitors"][2]["h2_clean"] += 1
    assert RB.record_hash(rec, q) != before


# --- parity: research board -------------------------------------------------------------

@pytest.mark.parametrize("field", ["ai_overview", "heading_types", "serp_schema", "authority"])
def test_parity_the_research_board_requires_the_serp_extras(field):
    rec = _rec()
    del rec[field]
    assert any(field in p for p in RB.validate(rec, _q())), field
    rec[field] = "NOT FETCHED — the SERP was fetched from a region with no AI Overview"
    assert not any(p.startswith(field) for p in RB.validate(rec, _q())), field


def test_parity_the_extras_are_rendered(tmp_path):
    _, md = RB.build(_rec(), _q(), tmp_path)
    text = md.read_text()
    for head in ("AI Overview", "Heading-Type Analysis", "SERP Schema Audit", "Authority and Links"):
        assert f". {head}" in text, head


# --- parity: outline --------------------------------------------------------------------

def _outline():
    return _load(FIX / "outline_matrix/good.json")


def _research():
    return OM.research_for(_outline())


def test_parity_all_six_levels_are_required_and_the_h5_h6_floor_follows_bsuk():
    rec = _outline()
    rec["sections"][2]["headings"][0]["children"][0]["children"] = []      # drop H4–H6
    assert any("all six levels" in p for p in OM.validate(rec, _research()))
    good = _outline()
    assert OM.validate(good, _research()) == []                           # location: WARN only
    assert any("H5" in w for w in OM.warnings(good))
    blog = dict(_outline(), page_type="blog")
    assert any("at least 5 H5" in p for p in OM.validate(blog, _research()))
    _md = "\n".join(b for _, b in OM.sections(good, _research()))
    assert "advisory" in _md and "source system" in _md


def test_parity_framework_is_a_research_pick_or_a_standard_framework():
    rec = _outline()
    rec["sections"][3]["framework"] = "Vibes"
    assert any("framework 'Vibes'" in p for p in OM.validate(rec, _research()))
    rec["sections"][3]["framework"] = "PAS"                                # a framework-* skill
    assert OM.validate(rec, _research()) == []


def test_parity_a_c_row_cites_a_research_finding():
    for bad in ("slug", "date", "intent.local", "serp.results[0].why_ranks"):
        rec = _outline()
        rec["sections"][2]["why_source"] = bad
        assert any("a C row" in p for p in OM.validate(rec, _research())), bad
    rec = _outline()
    rec["sections"][2]["why_source"] = "serp.results[0].weakness"
    assert OM.validate(rec, _research()) == []


def test_parity_a_b_row_cites_a_competitor_whose_why_ranks_was_fetched():
    rec = _outline()
    rec["sections"][3]["why_source"] = "serp.results[2]"                  # NOT FETCHED
    assert any("fetched why-it-ranks" in p for p in OM.validate(rec, _research()))


def test_parity_the_h1_field_equals_the_trees_h1():
    rec = _outline()
    rec["h1"] = "Something Else"
    assert any("h1" in p and "tree" in p for p in OM.validate(rec, _research()))


def test_parity_placed_keywords_sit_in_the_section_they_were_placed_in():
    rec = _outline()
    rec["sections"][2]["keywords"]["secondary"] = []                       # 'blue staffy price'
    assert any("'blue staffy price'" in p and "Delivery" in p
               for p in OM.validate(rec, _research()))
