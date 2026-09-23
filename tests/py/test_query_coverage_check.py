# tests/py/test_query_coverage_check.py — scripts/query_coverage_check.py (spec 2026-09-23 §10).
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import query_coverage_check as G  # noqa: E402

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "query_coverage_check.py"
ROUTE = "/uk-locations/blue-staffy-puppies-manchester-uk/"


def faq_block(questions, answers=True, h3=True):
    items = []
    for i, text in enumerate(questions):
        head = f'<h3 class="q">{text.title()}</h3>' if h3 else f"<b>{text}</b>"
        items.append(f'<details><summary><span class="num">{i + 1:02d}</span>{head}</summary>'
                     f'<p>{"An answer." if answers else ""}</p></details>')
    return f'<section id="faq-x" data-section-label="Questions"><h2>Questions</h2>' \
           f'<div class="kit-faq">{"".join(items)}</div></section>'


def qset(n, prefix):
    return [f"{prefix} question number {i}?" for i in range(n)]


def page_html(blocks=(5, 5, 7), body=5, extra=("Life in a Manchester Flat",), schema=True,
              answers=True, h3=True, form=True):
    top, mid, bot = qset(blocks[0], "top"), qset(blocks[1], "middle"), qset(blocks[2], "bottom")
    sections = [f'<section id="s{i}" data-section-label="S{i}"><h2>Body {i}</h2><p>Text.</p></section>'
                for i in range(body)]
    sections += [f'<section id="x{i}" data-section-label="X"><h2>{h}</h2><p>Text.</p></section>'
                 for i, h in enumerate(extra)]
    faq_names = top + mid + bot
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": n, "acceptedAnswer": {"@type": "Answer", "text": "An answer."}}
        for n in (faq_names if schema else faq_names[:-1])]})
    formsec = '<section id="enquiry" data-section-label="Ask"><h2>Ask</h2><form></form></section>' \
        if form else ""
    return ("<html><head><script type=\"application/ld+json\">" + ld + "</script></head><body><main>"
            '<section id="top" data-section-label="Hero"><h1>Blue Staffy Puppies Manchester</h1></section>'
            + faq_block(top, answers, h3) + "".join(sections[:3]) + faq_block(mid, answers, h3)
            + "".join(sections[3:]) + formsec + faq_block(bot, answers, h3)
            + "</main></body></html>")


def qfile(blocks=(5, 5, 7), total=6, extra_heading="Life in a Manchester Flat"):
    qs = []
    for name, n in zip(("top", "middle", "bottom"), blocks):
        for i in range(n):
            text = f"{name} question number {i}?"
            qs.append({"id": f"q-{name}-{i}", "question": text, "found_in": ["bank:x"], "score": 1,
                       "topic": "price", "block": name, "fact_source": "data/settings.json",
                       "must_answer": True, "faq": name, "blocked": None,
                       "covered_by": {"where": "faq", "text": text}})
    return {"slug": "m", "page_type": "location", "primary_keyword": "k", "route": ROUTE,
            "fetched": "2026-09-23", "spend_usd": 0.0, "sources": {}, "competitors": [],
            "section_target": {"matched": total - 3, "set_by": None, "extra": 3, "floor": 9,
                               "total": total},
            "extra_sections": [{"topic": "home", "uncovered": True, "question_ids": [],
                                "heading": extra_heading}],
            "questions": qs}


def test_a_complete_page_passes():
    assert G.check_page(qfile(), page_html()) == []


def test_two_faq_blocks_fail():
    html = page_html().replace('<div class="kit-faq">', '<div class="kit-other">', 1)
    assert any("FAQ blocks: 2" in p for p in G.check_page(qfile(), html))


def test_a_block_outside_its_range_fails():
    probs = G.check_page(qfile(blocks=(4, 5, 7)), page_html(blocks=(4, 5, 7)))
    assert any("FAQ top: 4 questions, want 5–7" in p for p in probs)


def test_a_question_that_is_not_an_h3_fails():
    probs = G.check_page(qfile(), page_html(h3=False))
    assert any("must be an H3" in p for p in probs)


def test_an_empty_answer_fails_even_though_the_next_number_follows():
    probs = G.check_page(qfile(), page_html(answers=False))
    assert any("has no answer under it" in p for p in probs)


def test_an_uncovered_must_answer_question_fails():
    q = qfile(); q["questions"][0]["covered_by"] = None
    assert any("has no covered_by" in p for p in G.check_page(q, page_html()))


def test_covered_text_missing_from_the_page_fails():
    q = qfile(); q["questions"][0]["covered_by"]["text"] = "A question nobody wrote?"
    assert any("not found" in p for p in G.check_page(q, page_html()))


def test_schema_that_differs_from_the_visible_faq_fails():
    assert any("FAQPage schema" in p for p in G.check_page(qfile(), page_html(schema=False)))


def test_an_extra_section_without_a_heading_fails():
    assert any("no heading recorded" in p
               for p in G.check_page(qfile(extra_heading=None), page_html()))


def test_an_extra_section_heading_missing_from_the_page_fails():
    q = qfile(extra_heading="A Section We Never Built")
    assert any("not an H2 on the page" in p for p in G.check_page(q, page_html()))


def test_too_few_body_sections_fails_and_frame_is_not_counted():
    # body 5 + 1 extra = 6 counted; hero (#top), the FAQ sections and the form are frame
    assert G.check_page(qfile(total=6), page_html()) == []
    probs = G.check_page(qfile(total=7), page_html())
    assert any("body sections with an H2: 6, want at least 7" in p for p in probs)


def test_review_and_counter_sections_are_frame_not_body():
    extra = ('<section id="rev" data-section-label="Reviews"><h2>Reviews</h2>'
             '<section class="kit-quote"><p>Lovely pup.</p></section></section>'
             '<section id="stats" data-section-label="At a glance" class="kit-counter"><h2>Stats</h2></section>')
    html = page_html().replace("</main>", extra + "</main>")
    assert G.check_page(qfile(total=6), html) == []
    assert any("body sections with an H2: 6, want at least 7" in p for p in G.check_page(qfile(total=7), html))


def test_a_newsletter_section_without_a_form_is_frame_not_body():
    extra = '<section id="newsletter" data-section-label="Newsletter"><h2>Stay in Touch</h2><p>Text.</p></section>'
    html = page_html().replace("</main>", extra + "</main>")
    assert G.check_page(qfile(total=6), html) == []
    assert any("body sections with an H2: 6, want at least 7" in p for p in G.check_page(qfile(total=7), html))


def blank_last_answer(html):
    head, _, tail = html.rpartition("<p>An answer.</p>")
    return head + "<p></p>" + tail


def test_an_answer_ends_at_its_details_and_trailing_text_is_not_an_answer():
    html = blank_last_answer(page_html()).replace(
        "</main>", '<p>Trailing text.</p><a href="/">A link</a></main>')
    assert any("q-bottom-6" in p and "has no answer under it" in p
               for p in G.check_page(qfile(), html))


def test_script_text_is_never_an_answer():
    html = blank_last_answer(page_html()).replace("</main>", "</main><script>console.log(1)</script>")
    assert any("q-bottom-6" in p and "has no answer under it" in p
               for p in G.check_page(qfile(), html))


def test_a_question_in_the_wrong_block_fails_naming_both():
    html = page_html()
    a, b = "Top Question Number 0?", "Middle Question Number 0?"
    html = html.replace(a, "@@").replace(b, a).replace("@@", b)
    probs = G.check_page(qfile(), html)
    assert any("q-top-0" in p and "middle" in p for p in probs), probs
    assert any("q-middle-0" in p and "top" in p for p in probs), probs


def test_an_faq_question_is_looked_up_among_faq_h3s_only():
    # an H2 with the same text earlier on the page must not stand in for the FAQ H3
    q = qfile(); q["questions"][0]["covered_by"]["text"] = "Life in a Manchester Flat"
    assert any("q-top-0" in p and "not found as an FAQ H3" in p for p in G.check_page(q, page_html()))
    # and an H2 carrying an FAQ question's text (nothing under it) does not shadow the H3
    html = page_html().replace(
        "</h1></section>",
        '</h1></section><section id="dup" data-section-label="Dup"><h2>Top Question Number 0?</h2></section>', 1)
    assert G.check_page(qfile(), html) == []


def test_headings_outside_main_do_not_count():
    q = qfile(extra_heading="Our Footer Links")
    html = page_html().replace("</main>", "</main><footer><h2>Our Footer Links</h2></footer>")
    assert any("not an H2 on the page" in p for p in G.check_page(q, html))


def test_a_labelled_section_with_no_h2_is_not_body():
    html = page_html().replace(
        "</main>", '<section id="aside" data-section-label="Aside"><p>Text.</p></section></main>')
    assert G.check_page(qfile(total=6), html) == []
    assert any("body sections with an H2: 6, want at least 7" in p
               for p in G.check_page(qfile(total=7), html))


def test_a_nested_labelled_section_is_not_counted_separately():
    html = page_html().replace(
        "</main>", '<section id="outer" data-section-label="Outer"><h2>Outer</h2>'
        '<section id="inner" data-section-label="Inner"><h2>Inner</h2><p>Text.</p></section>'
        "</section></main>")
    assert G.check_page(qfile(total=7), html) == []
    assert any("body sections with an H2: 7, want at least 8" in p
               for p in G.check_page(qfile(total=8), html))


def test_a_duplicated_visible_question_is_reported():
    html = page_html().replace("Top Question Number 1?", "Top Question Number 0?")
    q = qfile(); q["questions"][1]["covered_by"]["text"] = "top question number 0?"
    assert any("FAQPage schema" in p and "duplicate" in p for p in G.check_page(q, html))


def test_main_entity_may_be_a_single_object():
    ld = {"@type": "FAQPage", "mainEntity": {"@type": "Question", "name": "Only one?"}}
    assert G.faq_schema_names([json.dumps(ld)]) == ["Only one?"]


def test_only_direct_child_details_count_as_questions():
    html = page_html().replace("<p>An answer.</p>",
                               "<p>An answer.</p><div><details><summary>More</summary>x</details></div>", 1)
    assert G.check_page(qfile(), html) == []

def test_main_skips_unbuilt_pages_and_reports(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps(qfile()))
    (tmp_path / "data/queries/spend.json").write_text("[]")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "examined 0 pages (1 not built, 0 awaiting rebuild); 0 problems" in r.stdout


def build(tmp_path, q, rebuilt=True):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps(q))
    out = tmp_path / "dist" / ROUTE.strip("/")
    out.mkdir(parents=True)
    (out / "index.html").write_text(page_html())
    (tmp_path / "data/facts").mkdir(parents=True)
    keys = ["index", ROUTE.strip("/")] if rebuilt else ["index"]
    (tmp_path / "data/facts/rebuilt.json").write_text(json.dumps(keys))


def run(tmp_path):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                          capture_output=True, text=True)


def test_main_skips_a_built_page_that_is_not_rebuilt_yet(tmp_path):
    # the old site's page is still in dist/ — its question file waits for the rebuild
    build(tmp_path, qfile(total=9), rebuilt=False)
    r = run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "examined 0 pages (0 not built, 1 awaiting rebuild); 0 problems" in r.stdout


def test_main_skips_when_rebuilt_json_is_missing(tmp_path):
    build(tmp_path, qfile(total=9))
    (tmp_path / "data/facts/rebuilt.json").unlink()
    r = run(tmp_path)
    assert r.returncode == 0 and "(0 not built, 1 awaiting rebuild)" in r.stdout


def test_main_checks_a_built_and_rebuilt_page(tmp_path):
    build(tmp_path, qfile())
    r = run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "examined 1 pages (0 not built, 0 awaiting rebuild); 0 problems" in r.stdout


def test_page_key_follows_the_shared_slug_convention():
    assert G.page_key_for(ROUTE) == "uk-locations/blue-staffy-puppies-manchester-uk"
    assert G.page_key_for("/") == "index"


def test_main_fails_a_built_page_with_problems(tmp_path):
    build(tmp_path, qfile(total=9))
    r = run(tmp_path)
    assert r.returncode == 1
    assert "examined 1 pages (0 not built, 0 awaiting rebuild); 1 problems" in r.stdout


def test_main_rejects_an_invalid_question_file(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps({"slug": "m"}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "invalid question file" in r.stdout


def test_main_reports_a_question_file_that_is_not_json(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text("{not json")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "invalid question file" in r.stdout and "Traceback" not in r.stderr


def test_the_body_count_message_names_competitors_and_the_floor():
    probs = G.check_page(qfile(total=7), page_html())
    assert "body sections with an H2: 6, want at least 7 (competitors 4 + 3, floor 9)" in probs
