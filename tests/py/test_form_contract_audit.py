# tests/py/test_form_contract_audit.py
#
# Ported from CAG tests/test_form_contract_audit.py (Task 7). Every fixture form is
# rewritten to BSUK's built contact form: two hidden fields (_next, _subject), the
# _gotcha honeypot, and six named controls (name, email, phone, location, puppy,
# message), of which name/email/puppy/message are required as built.
#
# PUBLIC_FORMSPREE_ID is set by an autouse fixture and never hard-coded as the real id:
# the module refuses to import without one, and the value itself lives only in .env.
#
# Tests dropped in the port, each with its reason:
#   - test_blog_short_contract_passes_without_experience_delivery_or_required_message —
#     the seven CAG screening fields (experience, delivery, resale_screening,
#     surrender_history, the two confirm fields) have no BSUK analogue; inventing dog
#     equivalents would invent a screening policy the breeder has not set. The blog
#     short contract is now name/email/message and is covered by
#     test_blog_short_contract_passes_with_the_three_named_controls.
#   - test_homepage_and_contact_us_now_carry_the_full_contract — rewritten as
#     test_contact_page_carries_the_full_contract against BSUK's contact slug.
# Added:
#   - test_unset_formspree_id_refuses_rather_than_matching_nothing
#   - test_optional_phone_is_not_a_missing_field
#   - test_missing_hidden_field_is_named
import json
import os
import subprocess
import sys, pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

TEST_ID = "test-form-id"
import form_contract_audit as F  # noqa: E402  imports with no id set — see below

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "form_contract_audit.py"
CONTACT = "uk-blue-staffy-breeders-contact"


@pytest.fixture(autouse=True)
def _formspree_id(monkeypatch):
    """Every test sets the id itself. The module reads it lazily in _endpoint(), so
    importing this module with no id set must never exit the interpreter."""
    monkeypatch.setenv("PUBLIC_FORMSPREE_ID", TEST_ID)
    yield


END = f"https://formspree.io/f/{TEST_ID}"


def test_importing_without_the_id_does_not_exit(monkeypatch):
    """A module-level sys.exit made --help, and any import of this module, impossible
    without the id."""
    monkeypatch.delenv("PUBLIC_FORMSPREE_ID", raising=False)
    import importlib
    importlib.reload(F)          # must not raise SystemExit
    monkeypatch.setenv("PUBLIC_FORMSPREE_ID", TEST_ID)


def test_help_works_without_the_id():
    env = {k: v for k, v in os.environ.items() if k != "PUBLIC_FORMSPREE_ID"}
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0
    assert "--fail-on-error" in r.stdout


def test_endpoint_is_read_lazily_from_the_environment(monkeypatch):
    monkeypatch.setenv("PUBLIC_FORMSPREE_ID", "another-id")
    assert F._endpoint() == "https://formspree.io/f/another-id"


def test_endpoint_refuses_when_unset(monkeypatch):
    monkeypatch.delenv("PUBLIC_FORMSPREE_ID", raising=False)
    with pytest.raises(SystemExit) as e:
        F._endpoint()
    assert e.value.code == 2

GOOD = f"""<form action="{END}" method="POST">
<input type="hidden" name="_next" value="/thank-you/"><input type="hidden" name="_subject" value="x">
<input type="text" name="_gotcha" style="display:none">
<input name="name" required><input type="email" name="email" required>
<input type="tel" name="phone"><input name="location">
<select name="puppy" required><option value="">-</option><option value="roman">Roman</option><option value="collection-glasgow">Collection in Glasgow after a refundable £500 deposit</option></select>
<textarea name="message" required></textarea></form>"""


PUPPY_SELECT = ('<select name="puppy" required><option value="">-</option>'
                '<option value="roman">Roman</option>'
                '<option value="collection-glasgow">Collection in Glasgow after a '
                'refundable £500 deposit</option></select>')


def page(*forms):
    return "<html><body>" + "".join(forms) + '<form action="/search/" method="get"><input name="q"></form></body></html>'


def problems(html, slug="blue-staffy-vs-staffordshire-bull-terrier"):
    return [p for row in F.audit_html(html, slug) for p in row["problems"]]


def _dist_with_contact_form(tmp_path, phone_required=False):
    body = GOOD if not phone_required else GOOD.replace('name="phone"', 'name="phone" required')
    d = tmp_path / CONTACT
    d.mkdir(parents=True)
    (d / "index.html").write_text(page(body), encoding="utf-8")
    return tmp_path


def test_compliant_inquiry_form_has_no_problems():
    assert problems(page(GOOD)) == []


def test_search_form_is_not_examined():
    rows = F.audit_html(page(GOOD), "blue-staffy-vs-staffordshire-bull-terrier")
    assert [r["kind"] for r in rows] == ["inquiry"]


def test_missing_puppy_select_is_named():
    html = page(GOOD.replace('<select name="puppy" required><option value="">-</option><option value="roman">Roman</option><option value="collection-glasgow">Collection in Glasgow after a refundable £500 deposit</option></select>', ""))
    assert any("puppy absent" in p for p in problems(html))


def test_optional_message_is_named():
    html = page(GOOD.replace('<textarea name="message" required>', '<textarea name="message">'))
    assert any("message not required" in p for p in problems(html))


def test_optional_phone_is_not_a_missing_field(tmp_path):
    """As built, phone and location are optional. A contract that demanded them would
    report the shipped page as broken and teach the next agent to add `required`."""
    rows = F.audit_dist(_dist_with_contact_form(tmp_path, phone_required=False))
    assert rows
    assert not [p for r in rows for p in r["problems"] if "phone" in p]


def test_missing_hidden_field_is_named():
    html = page(GOOD.replace('<input type="hidden" name="_next" value="/thank-you/">', ""))
    assert any("_next absent" in p for p in problems(html))


# --- spec §5: the puppy control is a <select> carrying the collection option ------

def test_puppy_select_with_the_collection_option_is_clean():
    assert not [p for p in problems(page(GOOD)) if "puppy" in p]


def test_puppy_select_without_the_collection_option_is_a_problem():
    stripped = PUPPY_SELECT.replace(
        '<option value="collection-glasgow">Collection in Glasgow after a '
        'refundable £500 deposit</option>', "")
    ps = problems(page(GOOD.replace(PUPPY_SELECT, stripped)))
    assert any("puppy select missing the collection-glasgow option" in p for p in ps)


def test_puppy_as_a_text_input_is_a_problem():
    ps = problems(page(GOOD.replace(PUPPY_SELECT, '<input name="puppy" required>')))
    assert any("puppy must be a <select>" in p for p in ps)
    assert not any("puppy absent" in p for p in ps)


def test_netlify_form_fails_on_endpoint():
    html = page(GOOD.replace(f'action="{END}" method="POST"', 'name="x" method="POST" data-netlify="true"'))
    ps = problems(html)
    assert any("endpoint" in p for p in ps) and any("netlify" in p for p in ps)


def test_newsletter_box_needs_endpoint_and_name():
    html = page(f'<form action="/{CONTACT}/"><input type="email" required></form>')
    ps = problems(html)
    assert any("endpoint" in p for p in ps) and any("email input has no name" in p for p in ps)


def test_locations_and_hubs_skip_field_checks_but_not_endpoint():
    optional_msg = GOOD.replace('<textarea name="message" required>', '<textarea name="message">')
    for slug in ("uk-locations/glasgow", "uk-locations/edinburgh", "available-puppies", "blog"):
        assert problems(page(optional_msg), slug) == []
        assert any("endpoint" in p for p in problems(page(optional_msg.replace(END, "/thank-you/")), slug))


def test_contact_page_carries_the_full_contract():
    optional_msg = GOOD.replace('<textarea name="message" required>', '<textarea name="message">')
    for slug in ("index", CONTACT):
        assert problems(page(GOOD), slug) == []
        assert any("message not required" in p for p in problems(page(optional_msg), slug))


SHORT_BLOG = f"""<form action="{END}" method="POST">
<input type="hidden" name="_next" value="/thank-you/"><input type="hidden" name="_subject" value="x">
<input type="text" name="_gotcha" style="display:none">
<input name="name" required><input type="email" name="email" required>
<textarea name="message" required></textarea></form>"""


def test_blog_short_contract_passes_with_the_three_named_controls():
    assert problems(page(SHORT_BLOG), "blog/blue-staffy-puppy-facts") == []


def test_blog_short_contract_still_names_a_missing_control():
    html = page(SHORT_BLOG.replace('<input type="email" name="email" required>', ""))
    assert any("email absent" in p for p in problems(html, "blog/blue-staffy-puppy-facts"))


def test_short_form_on_a_non_blog_page_fails_the_full_contract():
    ps = problems(page(SHORT_BLOG), "how-to-avoid-blue-staffy-puppy-scams")
    assert any("puppy absent" in p for p in ps) and any("phone absent" in p for p in ps)


# --- the id must come from the environment ----------------------------------------

def test_unset_formspree_id_refuses_rather_than_matching_nothing(monkeypatch, tmp_path):
    monkeypatch.delenv("PUBLIC_FORMSPREE_ID", raising=False)
    with pytest.raises(SystemExit) as e:
        F.audit_html(page(GOOD), CONTACT)
    assert e.value.code == 2


def test_the_id_is_never_a_literal_in_the_script():
    src = SCRIPT.read_text(encoding="utf-8")
    assert 'os.environ.get("PUBLIC_FORMSPREE_ID"' in src
    assert src.count('formspree.io/f/{') == 1


# --- routing comes from data/page-map.json ------------------------------------------

def _page_map(tmp_path, pages):
    p = tmp_path / "page-map.json"
    p.write_text(json.dumps({"pages": pages}), encoding="utf-8")
    return p


def test_contract_routing_reads_kinds_from_the_page_map(tmp_path, monkeypatch):
    pm = _page_map(tmp_path, [
        {"url": "/a-rich-page/", "kind": "rich"},
        {"url": "/a-blog-post/", "kind": "blog"},
        {"url": "/a-location/", "kind": "location"},
    ])
    monkeypatch.setattr(F, "PAGE_MAP", pm)
    F.contract_keys.cache_clear() if hasattr(F.contract_keys, "cache_clear") else None
    F._kinds.cache_clear()
    assert [k[0] for k in F.contract_keys("a-rich-page")] == [k[0] for k in F.KEYS]
    assert [k[0] for k in F.contract_keys("a-blog-post")] == list(F.SHORT)
    assert F.contract_keys("a-location") == []


def test_pages_absent_from_the_map_fall_back_to_the_slug_heuristic(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "PAGE_MAP", _page_map(tmp_path, []))
    F._kinds.cache_clear()
    assert F.contract_keys("uk-locations/glasgow") == []
    assert F.contract_keys("blog") == []
    assert [k[0] for k in F.contract_keys("blog/a-post")] == list(F.SHORT)
    assert [k[0] for k in F.contract_keys("some-interior-page")] == [k[0] for k in F.KEYS]


def test_the_kit_preview_route_is_excluded_from_the_field_contract(tmp_path, monkeypatch):
    """Project 3's kit-preview route mounts each kit component once, the enquiry form
    among them; that copy is a specimen, not a reachable enquiry form. The exclusion is by
    NAME, so it survives the route being added to the page map later, and it must not leak
    to any other slug."""
    monkeypatch.setattr(F, "PAGE_MAP", _page_map(tmp_path, []))
    F._kinds.cache_clear()
    assert "kit-preview" in F.NON_CONTENT_ROUTES
    assert F.contract_keys("kit-preview") == []
    # An unknown CONTENT slug still falls to the full contract: this is one named route,
    # not a loosening of the fallback.
    assert [k[0] for k in F.contract_keys("kit-preview-notes")] == [k[0] for k in F.KEYS]
    assert [k[0] for k in F.contract_keys("some-interior-page")] == [k[0] for k in F.KEYS]


def test_every_excluded_route_still_exists_as_a_page(monkeypatch):
    """The exclusion EXPIRES. Each name in NON_CONTENT_ROUTES has to be a real route in
    src/pages/, so the day the preview route is deleted the name has to go with it —
    otherwise a future page could be built at that slug and be silently unaudited. It is
    what made Task 19 move the name off `design-canvas` in the commit that deleted it."""
    root = pathlib.Path(__file__).resolve().parents[2]
    for name in F.NON_CONTENT_ROUTES:
        assert (root / "src/pages" / name).is_dir(), (
            f"{name} is excluded from the form contract but src/pages/{name}/ is gone — "
            f"delete the name from NON_CONTENT_ROUTES in the same commit as the route")


def test_the_excluded_route_still_owes_the_endpoint_and_the_method():
    """The exclusion drops the FIELD checks only. A specimen form that posted somewhere
    else, or by GET, would be a real defect and is still reported."""
    stray = ('<form action="https://example.invalid/f/x" method="GET">'
             '<input name="name" required><textarea name="message" required></textarea></form>')
    rows = [r for r in F.audit_html(page(stray), "kit-preview") if r["action"] != "/search/"]
    assert len(rows) == 1
    probs = rows[0]["problems"]
    assert any("endpoint is" in p for p in probs), probs
    assert any("method is GET" in p for p in probs), probs
    assert not any("absent" in p for p in probs), probs


def test_a_contract_free_specimen_form_passes_on_the_excluded_route():
    """The positive half: the kit's own shape — the one endpoint, POST, no netlify
    residue — is clean on kit-preview without the per-page field contract."""
    specimen = (f'<form action="{END}" method="POST">'
                '<input name="name" required><input type="email" name="email" required>'
                '<textarea name="message" required></textarea></form>')
    assert problems(page(specimen), slug="kit-preview") == []


def test_the_real_page_map_routes_the_contact_page_to_the_full_contract():
    F._kinds.cache_clear()
    assert [k[0] for k in F.contract_keys(CONTACT)] == [k[0] for k in F.KEYS]


# --- Finding 1: CRITICAL zero-page PASS -------------------------------------------

def test_audit_dist_empty_returns_no_rows(tmp_path):
    assert F.audit_dist(tmp_path) == []


def test_main_fails_loud_on_zero_forms_examined(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--dist", str(tmp_path)],
        capture_output=True, text=True,
        env={**os.environ, "PUBLIC_FORMSPREE_ID": TEST_ID},
    )
    assert result.returncode == 2
    assert "no forms examined" in result.stdout


def test_main_refuses_without_the_id(tmp_path):
    """Exit 2 = cannot run, the same code board_gate.py and evidence_audit.py use;
    exit 1 would read as 'ran, found one problem'."""
    env = {k: v for k, v in os.environ.items() if k != "PUBLIC_FORMSPREE_ID"}
    result = subprocess.run([sys.executable, str(SCRIPT), "--dist", str(tmp_path)],
                            capture_output=True, text=True, env=env)
    assert result.returncode == 2
    assert "PUBLIC_FORMSPREE_ID is unset" in result.stderr


# --- Finding 2: conservative inquiry/newsletter classification --------------------

def test_no_textarea_inquiry_form_is_still_classed_inquiry():
    html = page(
        f'<form action="{END}" method="POST">'
        '<input type="hidden" name="_next" value="/t/"><input type="hidden" name="_subject" value="x">'
        '<input name="name" required><input type="tel" name="phone">'
        '<input type="email" name="email" required></form>'
    )
    rows = F.audit_html(html, "blue-staffy-vs-staffordshire-bull-terrier")
    assert rows[0]["kind"] == "inquiry"
    assert any("message absent" in p for p in rows[0]["problems"])


# --- Finding 3: parser alignment with document.forms ------------------------------

def test_nested_form_does_not_add_a_row_or_shift_n():
    nested = GOOD.replace(
        '<input type="tel" name="phone">',
        '<form action="/x" method="post"></form><input type="tel" name="phone">',
        1,
    )
    rows = F.audit_html(page(nested), "blue-staffy-vs-staffordshire-bull-terrier")
    assert len(rows) == 1
    assert rows[0]["n"] == 1


def test_form_inside_template_is_not_counted():
    html = "<html><body><template>" + GOOD + "</template><p>after</p></body></html>"
    rows = F.audit_html(html, "blue-staffy-vs-staffordshire-bull-terrier")
    assert rows == []


# --- Finding 4: pin the n contract -------------------------------------------------

def test_n_is_1_based_over_all_forms_document_order_search_included():
    html = page('<form action="/search/" method="get"><input name="q"></form>' + GOOD)
    rows = F.audit_html(html, "blue-staffy-vs-staffordshire-bull-terrier")
    assert len(rows) == 1
    assert rows[0]["n"] == 2
    assert rows[0]["in_scope"] is True
    assert "puppy" in rows[0]["fields"]


def test_required_empty_string_attribute_counts_as_required():
    html = GOOD.replace('name="name" required', 'name="name" required=""')
    rows = F.audit_html(page(html), "blue-staffy-vs-staffordshire-bull-terrier")
    assert not any("name" in p for p in rows[0]["problems"])
