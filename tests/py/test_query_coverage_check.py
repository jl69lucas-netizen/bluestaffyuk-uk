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
            "section_target": {"matched": total - 3, "set_by": None, "extra": 3, "total": total},
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
    assert any("body sections: 6, want at least 7" in p for p in probs)


def test_review_and_counter_sections_are_frame_not_body():
    extra = ('<section id="rev" data-section-label="Reviews"><h2>Reviews</h2>'
             '<section class="kit-quote"><p>Lovely pup.</p></section></section>'
             '<section id="stats" data-section-label="At a glance" class="kit-counter"><h2>Stats</h2></section>')
    html = page_html().replace("</main>", extra + "</main>")
    assert G.check_page(qfile(total=6), html) == []
    assert any("body sections: 6, want at least 7" in p for p in G.check_page(qfile(total=7), html))


def test_a_newsletter_section_without_a_form_is_frame_not_body():
    extra = '<section id="newsletter" data-section-label="Newsletter"><h2>Stay in Touch</h2><p>Text.</p></section>'
    html = page_html().replace("</main>", extra + "</main>")
    assert G.check_page(qfile(total=6), html) == []
    assert any("body sections: 6, want at least 7" in p for p in G.check_page(qfile(total=7), html))

def test_main_skips_unbuilt_pages_and_reports(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps(qfile()))
    (tmp_path / "data/queries/spend.json").write_text("[]")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "examined 0 pages (1 not built); 0 problems" in r.stdout


def test_main_fails_a_built_page_with_problems(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps(qfile(total=9)))
    out = tmp_path / "dist" / ROUTE.strip("/")
    out.mkdir(parents=True)
    (out / "index.html").write_text(page_html())
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert "examined 1 pages (0 not built); 1 problems" in r.stdout


def test_main_rejects_an_invalid_question_file(tmp_path):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/queries/m.json").write_text(json.dumps({"slug": "m"}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "invalid question file" in r.stdout
