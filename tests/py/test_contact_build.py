import pathlib, re
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAGE = ROOT / "dist/uk-blue-staffy-breeders-contact/index.html"


@pytest.fixture(scope="module")
def html():
    if not PAGE.exists():
        pytest.skip("dist not built; run `npm run build` first")
    return PAGE.read_text(encoding="utf-8")


def test_exactly_one_contact_form(html):
    # Count <form> elements only: the inline enhancement script also mentions the
    # selector string, which is not a second form.
    forms = re.findall(r"<form[^>]*data-form=\"contact\"", html)
    assert len(forms) == 1, forms


def test_puppy_select_has_six_pups_plus_the_waiting_list(html):
    """The kit form's option set, built from the same data (project 4 Task 6).

    The collection option that used to follow the litter named a collection point the
    breeder has left (Known Issue 16); dropping it is what lets this form and
    src/components/kit/ContactFormKit.astro pass the same `full` form contract.
    """
    select = re.search(r"<select[^>]*name=\"puppy\".*?</select>", html, re.S).group(0)
    options = re.findall(r"<option[^>]*value=\"([^\"]*)\"", select)
    assert options[0] == "", "first option should be the empty 'Choose…' prompt"
    assert options[-1] == "waiting-list"
    assert "collection-glasgow" not in options
    assert len(options) == 1 + 6 + 1, options


def test_next_points_at_thank_you(html):
    m = re.search(r"name=\"_next\" value=\"([^\"]+)\"", html)
    assert m, "_next hidden field missing"
    assert m.group(1).endswith("/thank-you-blue-staffy-puppies-journey/"), m.group(1)


def test_no_turnstile(html):
    assert "cf-turnstile" not in html
    assert "challenges.cloudflare.com" not in html
