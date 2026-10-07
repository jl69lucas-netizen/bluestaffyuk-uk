"""scripts/research_board.py — the research board (STOP 1) carries the whole research deliverable.

The user's ruling (2026-09-29): "i must see all angles, framework, keywords, why each
competitors rank, full distribution section by section". The board is built from its record
(`data/research-boards/<slug>.json`) and the page's query file; these tests pin that every
top-5 competitor has a why-it-ranks and a weakness grounded in a fetch or written
`NOT FETCHED — <barrier>` (working rule 9), that the other sections are all present, and that
the approval is recorded with the record's hash.
"""
import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests/py"))

import research_board as RB  # noqa: E402

FIX = ROOT / "tests/py/fixtures/research_board"


def _record():
    return json.loads((FIX / "record.json").read_text(encoding="utf-8"))


def _queries():
    return json.loads((FIX / "queries.json").read_text(encoding="utf-8"))


def test_the_fixture_is_complete_and_approved():
    rec = _record()
    assert RB.validate(rec, _queries()) == []
    assert RB.approval_state(rec) == "approved"


def test_every_top_competitor_needs_a_row():
    rec = _record()
    rec["serp"]["results"] = rec["serp"]["results"][:1]
    problems = RB.validate(rec, _queries())
    assert any("breeder-one.example" in p and "no row" in p for p in problems), problems
    # the competitor outside the top 5 on both engines is not required
    assert not any("deep.example" in p for p in problems), problems


@pytest.mark.parametrize("field", ["why_ranks", "weakness"])
def test_a_missing_why_or_weakness_is_refused(field):
    rec = _record()
    del rec["serp"]["results"][0][field]
    assert any(field in p and "missing" in p for p in RB.validate(rec, _queries()))


def test_a_finding_without_evidence_is_refused():
    rec = _record()
    del rec["serp"]["results"][1]["evidence"]
    assert any("evidence — a finding cites" in p for p in RB.validate(rec, _queries()))


def test_a_bare_not_fetched_is_refused():
    rec = _record()
    rec["serp"]["results"][2]["why_ranks"] = "NOT FETCHED"
    rec["reverse_engineering"][2]["tables"] = "NOT FETCHED — "
    problems = RB.validate(rec, _queries())
    assert sum("bare NOT FETCHED" in p for p in problems) == 2, problems


def test_the_query_file_supplies_words_and_h2s_never_retyped():
    rows = RB.merged(_record(), _queries())
    breeder = next(r for r in rows if "breeder-one" in r["url"])
    assert breeder["words"] == 1480
    assert breeder["headings"]["h2"] == 6 and breeder["headings"]["note"].startswith("NOT FETCHED — ")


def test_every_section_of_the_deliverable_is_required():
    for field in ("intent", "universal_gaps", "why_competitors_rank", "how_we_win",
                  "content_gap", "owner_language", "fanout", "entities", "angles",
                  "strategies", "frameworks", "keywords"):
        rec = _record()
        del rec[field]
        assert RB.validate(rec, _queries()), f"{field} removed and nothing was refused"


def test_one_recommended_option_per_choice_with_why_and_trade_off():
    rec = _record()
    rec["angles"][1]["recommended"] = True
    assert any("exactly one option" in p for p in RB.validate(rec, _queries()))
    rec = _record()
    del rec["strategies"][0]["trade_off"]
    assert any("trade_off" in p for p in RB.validate(rec, _queries()))
    rec = _record()
    rec["angles"] = rec["angles"][:2]
    assert any("angles: 3 options" in p for p in RB.validate(rec, _queries()))


def test_every_keyword_is_distributed_and_every_distributed_keyword_is_in_the_universe():
    rec = _record()
    rec["keywords"]["distribution"][1]["secondary"] = ["a keyword nobody researched"]
    problems = RB.validate(rec, _queries())
    assert any("not in the keyword universe" in p for p in problems)
    assert any("'blue staffy price' is placed in no section" in p for p in problems)


def test_owner_language_is_quotes_with_sources_or_not_fetched():
    rec = _record()
    rec["owner_language"] = [{"quote": "Mine is soft as butter"}]
    assert any("owner_language[0]" in p for p in RB.validate(rec, _queries()))


def test_the_board_renders_every_section_with_copy_buttons_and_a_md_download(tmp_path):
    html_path, md_path = RB.build(_record(), _queries(), tmp_path)
    md = md_path.read_text(encoding="utf-8")
    for head in ("## 1. SERP Snapshot", "## 2. Search Intent", "## 3. Competitor Reverse Engineering",
                 "## 4. Owner Language", "## 5. Query Fan-Out", "## 6. Why Competitors Rank",
                 "## 7. How We Win", "## 8. Content Gap (build list)", "## 9. Entities",
                 "## 10. Angles", "## 11. Strategy Directions", "## 12. Frameworks per Section Group",
                 "## 13. Keyword Universe", "## 14. Keyword Distribution",
                 "## 15. AI Overview", "## 16. Heading-Type Analysis", "## 17. SERP Schema Audit",
                 "## 18. Authority and Links", "## 19. What Is NOT FETCHED and How to Fetch It"):
        assert head in md, head
    for col in ("Why it ranks", "Weakness (our wedge)", "Words", "Headings", "Tables", "FAQ",
                "Byline", "Schema / notes", "Universal competitor gaps"):
        assert col in md, col
    assert "**Structural read:**" in md and "**(Recommended)**" in md
    assert "Status: **APPROVED" in md
    page = html_path.read_text(encoding="utf-8")
    assert "Copy section" in page and 'id="dl-md" hidden' in page and "text/markdown" in page
    assert "downloads.save(" in page and "createObjectURL" not in page   # viewer-only download
    assert page.count('type="text/markdown" data-title=') == 20


def test_the_fetch_plan_names_a_command_for_every_not_fetched():
    plan = RB.fetch_plan(_record(), _queries())
    fields = {row[0] for row in plan}
    assert "owner_language" in fields and "fanout.llm_intel" in fields
    assert all(row[2] for row in plan)
    assert any(row[0].startswith("reverse_engineering[2]") for row in plan)


def test_approval_needs_an_answers_file_and_goes_stale_on_an_edit(tmp_path):
    rec = copy.deepcopy(_record())
    rec["approval"] = None
    assert RB.approval_state(rec) == "unapproved"
    with pytest.raises(RB.RecordError):
        RB.approve(rec, "docs/reference/answer-board/answers/no-such-file.json")
    import _stop_kit as K
    rec = RB.approve(rec, K.answers(tmp_path, "fixture-city", "research-board"), today="2026-09-29",
                     root=tmp_path, queries=_queries())
    assert RB.approval_state(rec, _queries()) == "approved"
    rec["how_we_win"].append("an edit after approval")
    assert RB.approval_state(rec, _queries()) == "stale"


def test_the_cli_exits_1_on_an_incomplete_record_and_writes_nothing(tmp_path, capsys):
    rec = _record()
    del rec["serp"]["results"][0]["why_ranks"]
    path = tmp_path / "rec.json"
    path.write_text(json.dumps(rec))
    code = RB.main(["fixture-city", "--record", str(path), "--queries", str(FIX / "queries.json"),
                    "--out", str(tmp_path / "out")])
    assert code == 1
    assert "FAIL" in capsys.readouterr().out
    assert not (tmp_path / "out").exists()


# --- readability (plan 2026-10-07-board-readability.md, Task 3) ---------------------------
# Layout A and paragraph Option 2: the board embeds scripts/board_style.py, and the record's
# `summaries` (plain bullets per section title, per record path) render above the original,
# which folds into <details class="full">. The markdown, and so every copy button, is unchanged.

import re  # noqa: E402

import board_style as BS  # noqa: E402
import _board_harness as BH  # noqa: E402

STATUS_BULLETS = ["The research was read on two dates, from free and paid tools.",
                  "Three competitor pages were saved and measured."]


def _summed():
    rec = _record()
    rec["summaries"] = {
        "sections": {"Status": {"bullets": STATUS_BULLETS,
                                "care": ["One read is not proof of every searcher's view."]}},
        "items": {"serp.results[0]": {"bullets": ["Ranks on a strong domain."]},
                  "angles[1]": {"bullets": ["Lead with the scam fear."]}},
    }
    return rec


def _md_blocks(page):
    return re.findall(r'<script type="text/markdown" data-title="[^"]*">\n(.*?)\n</script>', page, re.S)


def test_summaries_are_keyed_by_the_titles_the_board_renders():
    assert [t for t, _ in RB.sections(_record(), _queries())] == list(RB.SECTION_TITLES)


def test_the_board_embeds_the_shared_style_layer(tmp_path):
    page = RB.build(_record(), _queries(), tmp_path)[0].read_text(encoding="utf-8")
    assert BS.CSS in page and BS.SCRIPT in page and BS.READING_CSS in page


def test_a_missing_summaries_key_renders_as_today(tmp_path):
    rec = _record()
    assert "summaries" not in rec
    html_path, md_path = RB.build(rec, _queries(), tmp_path)
    page = html_path.read_text(encoding="utf-8")
    assert 'id="board-summaries"' not in page
    assert md_path.read_text(encoding="utf-8") == RB.MA.markdown(
        f"Research board — {rec['route']}", RB.sections(rec, _queries()))


def test_summaries_ride_beside_the_markdown_and_never_in_it(tmp_path):
    # The summaries are part of the record, so they are in its hash: an approval does not
    # survive adding them. Compare both unapproved, so only the summaries differ.
    plain, summed = _record(), _summed()
    plain["approval"] = summed["approval"] = None
    plain_html, plain_md = RB.build(plain, _queries(), tmp_path / "a")
    summed_html, summed_md = RB.build(summed, _queries(), tmp_path / "b")
    # the copy buttons copy these blocks and the .md download is this file: both unchanged
    assert summed_md.read_text(encoding="utf-8") == plain_md.read_text(encoding="utf-8")
    page = summed_html.read_text(encoding="utf-8")
    assert _md_blocks(page) == _md_blocks(plain_html.read_text(encoding="utf-8"))
    for b in STATUS_BULLETS:
        assert b not in "".join(_md_blocks(page))
    data = json.loads(re.search(r'<script type="application/json" id="board-summaries">(.*?)</script>',
                                page, re.S).group(1))
    assert data["sections"]["Status"]["bullets"] == STATUS_BULLETS
    assert {"section": "1. SERP Snapshot", "kind": "row", "index": 0,
            "bullets": ["Ranks on a strong domain."]} in data["items"]
    assert {"section": "10. Angles", "kind": "li", "index": 1,
            "bullets": ["Lead with the scam fear."]} in data["items"]
    # the data sits before the script that renders it
    assert page.index('id="board-summaries"') < page.index(BS.SCRIPT)


def test_in_a_browser_the_bullets_come_first_and_the_original_folds_under_them(tmp_path):
    rec = _summed()
    html_path, _ = RB.build(rec, _queries(), tmp_path)
    res = BH.run(html_path)
    assert res["errors"] == [], res["errors"]
    status = next(b for b in res["blocks"] if b["title"] == "Status")
    assert status["plain"] == STATUS_BULLETS and status["plainFirst"], status
    assert status["care"] == rec["summaries"]["sections"]["Status"]["care"]
    assert status["fullOpen"] is False and "Research method:" in status["fullText"], status
    other = next(b for b in res["blocks"] if b["title"] == "6. Why Competitors Rank")
    assert other["plain"] is None
    assert res["legend"] == 1
    # every copy button copies its section's markdown exactly, summaries or not
    want = [f"## {t}\n\n{b.strip()}" for t, b in RB.sections(rec, _queries())]
    assert res["copied"] == want


def test_the_validator_holds_the_summaries_to_their_shape():
    assert RB.validate(_summed(), _queries()) == []
    long = " ".join(["word"] * 26)
    for why, bullets in (("over 25 words", [long]),
                         ("more than 6", ["Short plain line."] * 7),
                         ("a file path", ["It was read from docs/research/x.md first."]),
                         ("a backticked field", ["The `deposit_gbp` field sets it."])):
        rec = _summed()
        rec["summaries"]["sections"]["Status"]["bullets"] = bullets
        assert any("summaries" in p for p in RB.validate(rec, _queries())), why
    rec = _summed()
    rec["summaries"]["sections"]["No Such Section"] = {"bullets": ["x y"]}
    assert any("No Such Section" in p for p in RB.validate(rec, _queries()))
    rec = _summed()
    rec["summaries"]["items"]["angles[7]"] = {"bullets": ["x y"]}
    assert any("angles[7]" in p for p in RB.validate(rec, _queries()))


def test_section_15_prints_the_session_note_and_implication():
    rec = _record()
    rec["ai_overview"] = {"present": False, "fetched": "2026-10-07",
                          "evidence": rec["ai_overview"]["evidence"],
                          "session": "Signed out, placed in another city.",
                          "note": "One session is not proof.",
                          "implication": "Build the page to be quotable anyway."}
    aio = dict(RB.sections(rec, _queries()))["15. AI Overview"]
    assert aio.startswith("No AI Overview is shown for this query.")
    for label, text in (("**Session:**", "Signed out, placed in another city."),
                        ("**Note:**", "One session is not proof."),
                        ("**GEO implication:**", "Build the page to be quotable anyway.")):
        assert f"{label} {text}" in aio, label
    assert aio.index("**Session:**") < aio.index("**Note:**") < aio.index("**GEO implication:**")
    present = dict(RB.sections(_record(), _queries()))["15. AI Overview"]
    assert "**Session:**" not in present and "**GEO implication:**" in present
