"""scripts/check_city_canvas.py — the London component canvas contract (Plan 1, Task 3).

Every rule is proven twice: a good fragment passes, and the same fragment with one defect
injected fails naming that rule. The fixtures are built here, in code, so no fixture file in
the repo has to carry a reference-site word to prove the ban on one.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_city_canvas as C  # noqa: E402
import marker_check  # noqa: E402
from city_components import COMPONENT_IDS  # noqa: E402

IMG = "/images/ethical-staffy-puppy-london-delivery.webp"
OPEN = ("We deliver our blue Staffy puppies to London homes by approved transport, "
        "and you can collect from Carlisle instead.")

HERO = f"""<style>.h{{display:grid;background:var(--color-surface);color:var(--color-text)}}
@media (max-width:900px){{.h img{{order:1}}}}</style>
<section data-component="hero" data-variant="a" class="h">
  <img src="{IMG}" alt="A blue Staffy puppy ready for a London home" width="800" height="600">
  <h1>Where Can I Find a Blue Staffy Puppy for London?</h1>
  <p>{OPEN}</p>
  <a href="#puppies">See the puppies</a>
</section>"""

TABLE = f"""<section data-component="tables" data-variant="b">
  <h2>What Does Delivery to London Cost?</h2>
  <p>{OPEN} Delivery is £200 to £350, and the deposit is £500.</p>
  <table class="stack-table" data-table><thead><tr><th>Puppy</th><th>Price</th></tr></thead>
  <tbody><tr><td data-label="Puppy">Roman</td><td data-label="Price">£1,500</td></tr></tbody></table>
</section>"""


def ctx(**over):
    base = dict(banned_words=C.banned_words(), allowed_pounds=C.allowed_pounds(),
                must_differ={}, ideas={})
    base.update(over)
    return C.Context(**base)


def probs(component, variant, text, c=None):
    return C.validate_fragment(component, variant, text, c or ctx())


def test_the_good_hero_and_table_pass():
    assert probs("hero", "a", HERO) == []
    assert probs("tables", "b", TABLE) == []


@pytest.mark.parametrize("bad,needle", [
    (HERO.replace("var(--color-surface)", "#F4F1EA"), "hex colour"),
    (HERO.replace("var(--color-text)", "rgb(27,36,48)"), "colour function"),
    (HERO.replace("var(--color-surface)", "grey"), "named colour"),
    (HERO.replace("<a href", '<svg><path fill="#000" d="M0 0"/></svg><a href'), "use currentColor"),
    (HERO.replace("Blue Staffy Puppy for London?", "Blue Staffy Puppy for London"), "not a question"),
    (HERO.replace(f"<p>{OPEN}</p>", "<p>Short line.</p>"), "fewer than 12"),
    (HERO.replace(f"<p>{OPEN}</p>", f"<ul><li>{OPEN}</li></ul>"), "not followed by an opening <p>"),
    (HERO.replace(f'<img src="{IMG}" alt="A blue Staffy puppy ready for a London home" width="800" height="600">', "")
         .replace("<a href", f'<img src="{IMG}" alt="x" width="1" height="1"><a href'), "must come before"),
    (HERO.replace(IMG, "https://example.com/a.jpg"), "not a repo image"),
    (HERO.replace(IMG, "/images/no-such-file.webp"), "no such file"),
    (HERO.replace('width="800" ', ""), "numeric width and height"),
    (HERO.replace('alt="A blue Staffy puppy ready for a London home"', 'alt=""'), "no alt text"),
    (HERO.replace('href="#puppies"', 'href="https://example.com/"'), "links to #"),
    (HERO.replace("</section>", '<form action="https://example.com/f"></form></section>'), "posts nowhere"),
    (HERO.replace("</section>", "<script>1</script></section>"), "<script> is not allowed"),
    (HERO.replace('data-variant="a"', 'data-variant="b"'), "data-variant"),
    (HERO + "<section></section>", "one root <section>"),
    (HERO.replace("London", "Leeds"), "no mention of London"),
    (HERO.replace("See the puppies", "From £999"), "£999"),
    (HERO.replace("See the puppies", "Call 07700 900123"), "phone number"),
])
def test_each_rule_fires_on_its_own_defect(bad, needle):
    out = probs("hero", "a", bad)
    assert any(needle in x for x in out), out


def test_an_unlabelled_cell_is_refused():
    out = probs("tables", "b", TABLE.replace('<td data-label="Price">', "<td>"))
    assert any("data-label" in x for x in out), out


def test_a_source_project_marker_and_a_reference_host_are_refused():
    marker = marker_check.MARKERS[0]
    assert any("source-project" in x for x in probs("hero", "a", HERO.replace("See the puppies", marker)))
    # marker_check's own matcher, not a bare substring: WCAG-AA is not the `cag-` prefix.
    assert probs("hero", "a", HERO.replace("See the puppies", "WCAG-AA contrast")) == []
    hosts = [w for w in C.banned_words() if "." in w]
    assert hosts, "the sources doc should name at least one reference host"
    assert any("reference-site" in x for x in probs("hero", "a", HERO.replace("See the puppies", hosts[0])))


def test_a_review_is_a_marked_placeholder_or_a_real_one_word_for_word():
    real = C.real_reviews()[0]
    rev = f"""<section data-component="reviews" data-variant="a">
      <h2>What Do London Owners Say About Their Puppy?</h2><p>{OPEN}</p>
      <figure data-review-slot><blockquote data-placeholder="review"><p>Placeholder review for London.</p></blockquote></figure>
      <figure data-review-slot><blockquote data-review="0"><p>{real}</p></blockquote></figure>
    </section>"""
    c = ctx(reviews=C.real_reviews())
    assert probs("reviews", "a", rev, c) == []
    out = probs("reviews", "a", rev.replace(' data-placeholder="review"', ""), c)
    assert any("never invent a review" in x for x in out), out
    out = probs("reviews", "a", rev.replace(real[:30], "An invented line about London "), c)
    assert any("word for word" in x for x in out), out


def test_a_puppy_name_heading_may_be_exempt_only_on_puppy_cards():
    card = f"""<section data-component="puppy-cards" data-variant="a">
      <h2>Which Puppies Can Come Home to London?</h2><p>{OPEN}</p>
      <article><h3 data-heading-exempt="puppy-name">Roman</h3><span>£1,500</span></article>
    </section>"""
    assert [x for x in probs("puppy-cards", "a", card) if x.startswith("heading")] == []
    other = card.replace('"puppy-cards"', '"image-text"')
    assert any("not a question" in x for x in probs("image-text", "a", other))


def _meta(**over):
    rows = {
        "a": {"name": "Ticket stub", "description": "Photo top, copy in a ticket.",
              "idea_sources": ["hero-idea00.png"], "differs_from": "No built page uses a ticket stub layout.",
              "axes": {"layout": "ticket", "media": "top", "density": "airy", "framing": "inset"}},
        "b": {"name": "Postcard", "description": "Photo left, copy right on a card.",
              "idea_sources": ["hero-idea00.png"], "differs_from": "A postcard, not a split hero or a panel.",
              "axes": {"layout": "postcard", "media": "left", "density": "regular", "framing": "rule"}},
        "c": {"name": "Poster", "description": "Photo as the background.",
              "idea_sources": ["hero-idea00.png"], "differs_from": "The photo is the whole ground, never a column.",
              "axes": {"layout": "poster", "media": "background", "density": "compact", "framing": "bleed"}},
    }
    for k, v in over.items():
        rows[k] = v
    return {"component": "hero", "variants": rows}


IDEAS = {"hero": "- `hero-idea00.png` — a band"}


def test_a_good_meta_passes():
    assert C.validate_meta("hero", _meta(), ctx(ideas=IDEAS))[0] == []


def test_siblings_one_axis_apart_are_refused():
    m = _meta()
    m["variants"]["b"]["axes"] = dict(m["variants"]["a"]["axes"], density="compact")
    out = C.validate_meta("hero", m, ctx(ideas=IDEAS))[0]
    assert any("siblings a and b" in x for x in out), out


def test_a_variant_one_axis_from_an_existing_style_is_refused():
    row = {"id": "H-GD2", "name": "Magazine", "axes": {"layout": "ticket", "media": "top",
                                                      "density": None, "framing": "card"}}
    out = C.validate_meta("hero", _meta(), ctx(ideas=IDEAS, must_differ={"hero": [row]}))[0]
    assert any("H-GD2" in x for x in out), out


@pytest.mark.parametrize("field,value,needle", [
    ("idea_sources", ["not-in-the-index.png"], "not cited"),
    ("description", "two\nlines", "one line"),
    ("differs_from", "short", "20+"),
    ("axes", {"layout": "Ticket Stub", "media": "top", "density": "airy", "framing": "inset"}, "short slug"),
    ("axes", {"layout": "ticket", "media": "sideways", "density": "airy", "framing": "inset"}, "axes.media"),
])
def test_meta_fields_are_checked(field, value, needle):
    m = _meta()
    m["variants"]["a"][field] = value
    out = C.validate_meta("hero", m, ctx(ideas=IDEAS))[0]
    assert any(needle in x for x in out), out


def _write_component(root, cid, texts, meta):
    d = root / cid
    d.mkdir(parents=True)
    for v, t in texts.items():
        (d / f"{v}.html").write_text(t, encoding="utf-8")
    (d / "meta.json").write_text(json.dumps(meta), encoding="utf-8")


def test_the_canvas_walk_counts_and_requires_all_fifteen(tmp_path):
    texts = {v: HERO.replace('data-variant="a"', f'data-variant="{v}"') for v in "abc"}
    _write_component(tmp_path, "hero", texts, _meta())
    problems, n_frag, n_meta = C.validate_canvas(tmp_path, ctx(ideas=IDEAS), only=["hero"])
    assert (problems, n_frag, n_meta) == ([], 3, 1)
    problems, _n, _m = C.validate_canvas(tmp_path, ctx(ideas=IDEAS))
    missing = [x for x in problems if "missing" in x]
    assert len(missing) == len(COMPONENT_IDS) - 1, problems


def test_a_stray_file_and_a_stray_component_are_refused(tmp_path):
    texts = {v: HERO.replace('data-variant="a"', f'data-variant="{v}"') for v in "abc"}
    _write_component(tmp_path, "hero", texts, _meta())
    (tmp_path / "hero" / "d.html").write_text("x", encoding="utf-8")
    (tmp_path / "carousel").mkdir()
    problems, _n, _m = C.validate_canvas(tmp_path, ctx(ideas=IDEAS))
    assert any("hero: holds" in x for x in problems), problems
    assert any("carousel: not one of" in x for x in problems), problems


def test_the_cli_says_when_it_examined_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(C, "CANVAS_ROOT", tmp_path)
    assert C.main(["--city", "nowhere", "--only", "hero"]) == 1
    assert "examined 0 fragments — not a pass" in capsys.readouterr().out


def test_the_cli_refuses_an_unknown_component():
    with pytest.raises(SystemExit) as e:
        C.main(["--only", "carousel"])
    assert e.value.code == 2


def test_a_component_that_drops_one_of_its_parts_is_refused():
    six = "".join(f'<article data-puppy><h3 data-heading-exempt="puppy-name">P{i}</h3></article>'
                  for i in range(6))
    card = f"""<section data-component="puppy-cards" data-variant="a">
      <h2>Which Puppies Can Come Home to London?</h2><p>{OPEN}</p>{six}</section>"""
    assert probs("puppy-cards", "a", card) == []
    five = card.replace("<article data-puppy>", "<article>", 1)
    assert any("5 element(s) carry data-puppy, puppy-cards needs 6" in x
               for x in probs("puppy-cards", "a", five))


def test_a_form_field_without_a_label_is_refused():
    form = f"""<section data-component="newsletter" data-variant="a">
      <h2>Can I Hear When a London Litter Is Due?</h2><p>{OPEN}</p>
      <form data-newsletter><label for="nl-email">Email</label>
      <input id="nl-email" type="email" name="email"><button type="submit">Join</button></form>
    </section>"""
    assert probs("newsletter", "a", form) == []
    out = probs("newsletter", "a", form.replace('<label for="nl-email">Email</label>', ""))
    assert any("no <label for>" in x for x in out), out


def test_an_image_between_an_h3_and_its_opening_is_allowed():
    """Rule 17 puts the image first under an H3; the opening paragraph follows it."""
    sec = f"""<section data-component="image-text" data-variant="a">
      <h2>How Do Our Puppies Travel to London?</h2><p>{OPEN}</p>
      <h3>What Happens on Delivery Day in London?</h3>
      <figure data-media><img src="{IMG}" alt="Delivery to a London home" width="4" height="3"></figure>
      <p>{OPEN}</p></section>"""
    assert probs("image-text", "a", sec) == []


MAGGIE = "/images/maggie-blue-staffy-dam-with-pups.webp"
MAGGIE_ALT = ("A heartwarming photo of Maggie, a beautiful 2-year-old blue Staffy Dam, "
              "lovingly tending to her pups.")


def _maggie(alt, extra=""):
    return HERO.replace(f'<img src="{IMG}" alt="A blue Staffy puppy ready for a London home"',
                        f'<img src="{MAGGIE}" alt="{alt}"{extra}')


def test_a_served_image_keeps_its_served_alt_word_for_word():
    """Working rule 11 (learning loop 2026-09-27, L2): Tasks 5–8 rewrote the alt of a served
    file four times and only a reviewer caught it. The served alts are data, so the canvas
    gate compares against them."""
    c = ctx(served_alts=C.served_alts())
    assert MAGGIE_ALT in c.served_alts["maggie-blue-staffy-dam-with-pups.webp"]
    assert probs("hero", "a", _maggie(MAGGIE_ALT), c) == []
    out = probs("hero", "a", _maggie("Maggie, our blue Staffy dam, with her London-bound litter"), c)
    assert any("served alt" in x and "maggie-blue-staffy-dam-with-pups.webp" in x for x in out), out
    # a file the old site never served carries whatever alt the variant gives it
    assert "no-such-served-file.webp" not in c.served_alts


def test_the_parents_are_read_from_the_faq():
    assert C.parent_names() == frozenset({"Maggie", "Jones"})


@pytest.mark.parametrize("line,needle", [
    # the parents' names, reversed by the user in 7ce341a after 5793200 wrote them as fact
    ("The parents, Angie and Lays, are both health tested in Carlisle.", "'angie'"),
    ("Angie and Lays, both parents, live with us in Carlisle.", "'lays'"),
    ("Angie, our dam, raises every litter at home.", "'angie'"),
    ("Our sire (Lays) is calm around children.", "'lays'"),
    # audience and promise claims no file confirms (fc23018, 447cdfd, 62df243 review rounds)
    ("Plenty of London families find us between litters.", "plenty of london families"),
    ("Most London buyers collect in Carlisle.", "most london buyers"),
    ("Every term is agreed in writing before you pay.", "in writing"),
    ("Each puppy is handled daily from birth.", "handled daily"),
    ("One litter a year, raised at home.", "one litter"),
])
def test_a_canonical_fact_is_never_contradicted_or_invented(line, needle):
    """Learning loop 2026-09-27 (L3 i–ii): parent names must be data/faq.json's; audience
    and promise claims are refused until a file records them."""
    c = ctx(parents=C.parent_names())
    bad = HERO.replace("<a href", f"<p>{line}</p><a href")
    out = probs("hero", "a", bad, c)
    assert any(needle in x.lower() and x.startswith("copy:") for x in out), out


def test_the_real_parents_pass():
    c = ctx(parents=C.parent_names())
    ok = HERO.replace("<a href", "<p>The parents, Maggie and Jones, live with us. Maggie, our dam, "
                                 "and Jones, our sire, are both tested.</p><a href")
    assert probs("hero", "a", ok, c) == []


def test_a_title_case_question_is_not_a_parent_name():
    """Task 25 (Manchester): the approved outline's FAQ H3 "Should I See the Mother With Her Puppy
    Before Money Changes Hands?" read "With" as the mother's name (the `mother <Name>` pattern
    on a Title Case heading). A false positive, charged to the harness: "With" joins NOT_NAMES."""
    c = ctx(parents=C.parent_names())
    ok = HERO.replace("<a href", "<p>Should I See the Mother With Her Puppy Before Money Changes "
                                 "Hands?</p><a href")
    assert probs("hero", "a", ok, c) == []


DECOR = f'<img src="{IMG}" alt="" width="44" height="44"'


@pytest.mark.parametrize("marks", [' aria-hidden="true"', ' role="presentation"', ' role="none"'])
def test_a_decorative_image_may_carry_an_empty_alt(marks):
    """Learning loop 2026-09-27 (L9, shortlist #8b): jump b's decorative 44px thumbnail had to
    become a CSS background on an aria-hidden span because the validator refused alt="" — the
    gate pushed the author off the correct markup. Empty alt marked decorative is accepted."""
    ok = HERO.replace("<a href", f"{DECOR}{marks}><a href")
    assert probs("hero", "a", ok) == []


def test_an_empty_alt_not_marked_decorative_is_still_refused():
    bad = HERO.replace("<a href", f"{DECOR}><a href")
    assert any("no alt text" in x for x in probs("hero", "a", bad))


# ---- Task 18 (Manchester plan, Phase F, gap G1): the canvas tools take any city ----

SHEETS = "/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Components-Ideas/"
MAN_HERO = HERO.replace("London", "Manchester")


def test_the_copy_rule_names_the_canvas_city_not_london():
    """G1: the copy rule read the word "London" into every canvas, so no other city could pass."""
    c = ctx(city="manchester")
    assert probs("hero", "a", MAN_HERO, c) == []
    out = probs("hero", "a", MAN_HERO.replace("Manchester", "Leeds"), c)
    assert any(x.startswith("copy: no mention of Manchester") for x in out), out
    # a London canvas keeps its own rule and its own message
    assert any(x.startswith("copy: no mention of London")
               for x in probs("hero", "a", MAN_HERO, ctx(city="london")))


def test_the_ideas_index_is_per_city():
    assert C.ideas_index("manchester") == ROOT / "docs/research/manchester-components/ideas-index.md"
    assert C.ideas_index("london") == ROOT / "docs/research/london-components/ideas-index.md"


def _sheet_meta(component, src):
    m = _meta()
    m["component"] = component
    for v in "abc":
        m["variants"][v]["idea_sources"] = [src]
    return m


@pytest.mark.parametrize("component", ["hero", "counter-strip"])
def test_a_hero_or_counter_cites_a_breeder_idea_sheet(component):
    """Working rule 16 / Phase F ruling 3: each hero and counter variant takes its idea from at
    least one sheet in Assets/Components-Ideas/. London's counters cited none of them."""
    ref = "/Users/apple/Downloads/BSUK/BSUK-refs/manchester/hero/ref-1280-01.png"
    ideas = {component: f"- `{ref}` — a reference\n- `{SHEETS}hero-idea-3.png` — a sheet"}
    c = ctx(city="manchester", ideas=ideas)
    out = C.validate_meta(component, _sheet_meta(component, ref), c)[0]
    assert "meta a: hero/counter cite a breeder idea sheet (working rule 16)" in out, out
    ok = C.validate_meta(component, _sheet_meta(component, f"{SHEETS}hero-idea-3.png"), c)[0]
    assert not [x for x in ok if "idea sheet" in x], ok


def test_the_idea_sheet_rule_binds_only_hero_and_counter():
    ref = "/Users/apple/Downloads/BSUK/BSUK-refs/manchester/trust/ref-1280-01.png"
    c = ctx(city="manchester", ideas={"trust-strip": f"- `{ref}` — a reference"})
    out = C.validate_meta("trust-strip", _sheet_meta("trust-strip", ref), c)[0]
    assert not [x for x in out if "idea sheet" in x], out


def test_a_manchester_variant_one_axis_from_londons_pick_is_refused():
    """G2: London's picks are rows of the must-differ table, so a Manchester variant one axis
    from london/hero/b fails on the canvas, not at the gate after the user picked it."""
    import pageboard as PB
    md = json.loads(C.MUST_DIFFER.read_text(encoding="utf-8"))["components"]
    m = _meta()
    m["variants"]["a"]["axes"] = dict(PB.canvas_axes("london/hero/b"))
    out = C.validate_meta("hero", m, ctx(city="manchester", ideas=IDEAS, must_differ=md))[0]
    assert any("within one axis of existing style london/hero/b" in x for x in out), out


def test_a_london_variant_is_never_compared_with_londons_own_picks():
    m = _meta()
    row = {"shape": "city", "id": "london/hero/a", "name": "Its own pick",
           "axes": dict(m["variants"]["a"]["axes"]), "used_by": ["blue-staffy-puppies-london"]}
    out = C.validate_meta("hero", m, ctx(city="london", ideas=IDEAS, must_differ={"hero": [row]}))[0]
    assert not [x for x in out if "london/hero/a" in x], out
    out = C.validate_meta("hero", m, ctx(city="manchester", ideas=IDEAS, must_differ={"hero": [row]}))[0]
    assert any("london/hero/a" in x for x in out), out


def test_with_no_arguments_every_city_with_a_picks_record_is_validated(tmp_path, monkeypatch, capsys):
    """G1: `check:canvas` in check:all validated London only. With no arguments it walks
    data/design/city-picks/ and judges each city's canvas against its non-`none` picks."""
    canvases, picks = tmp_path / "canvas", tmp_path / "picks"
    canvases.mkdir()
    picks.mkdir()
    (canvases / "london").symlink_to(C.CANVAS_ROOT / "london")
    served = ("An ethical blue Staffy puppy, delivered professionally by BlueStaffyUK, happily "
              "with its new owners Mark and Emma P. in London.")   # working rule 11 keeps it
    texts = {v: MAN_HERO.replace("Manchester", "Testville")
             .replace("A blue Staffy puppy ready for a Testville home", served)
             .replace('data-variant="a"', f'data-variant="{v}"') for v in "abc"}
    meta = _meta()
    for v in "abc":
        meta["variants"][v]["idea_sources"] = [f"{SHEETS}hero-idea-5.png"]
    _write_component(canvases / "testville", "hero", texts, meta)
    (tmp_path / "ideas.md").write_text(f"## hero — Hero\n\n- `{SHEETS}hero-idea-5.png` — a sheet\n",
                                       encoding="utf-8")
    real = json.loads((C.PICKS_DIR / "blue-staffy-puppies-london.json").read_text(encoding="utf-8"))
    (picks / "blue-staffy-puppies-london.json").write_text(json.dumps(real), encoding="utf-8")
    rec = {"slug": "blue-staffy-puppies-testville", "canvas": "testville",
           "picks": {c: ("testville/hero/a" if c == "hero" else "none") for c in COMPONENT_IDS}}
    (picks / "blue-staffy-puppies-testville.json").write_text(json.dumps(rec), encoding="utf-8")
    real_index = C.ideas_index
    monkeypatch.setattr(C, "CANVAS_ROOT", canvases)
    monkeypatch.setattr(C, "PICKS_DIR", picks)
    monkeypatch.setattr(C, "ideas_index",
                        lambda city: tmp_path / "ideas.md" if city == "testville" else real_index(city))
    assert C.main([]) == 0, capsys.readouterr().out
    out = capsys.readouterr().out
    assert "check-city-canvas london: examined 45 fragments, 15 meta files; 0 problems" in out, out
    assert "check-city-canvas testville: examined 3 fragments, 1 meta files; 0 problems" in out, out


def test_the_real_no_argument_run_judges_london_and_passes(capsys):
    assert C.main([]) == 0, capsys.readouterr().out
    assert "check-city-canvas london: examined 45 fragments, 15 meta files; 0 problems" \
        in capsys.readouterr().out


def test_a_variant_is_never_compared_with_a_later_citys_pool_copy_of_itself():
    """Phase F ruling 4 (pool variants) meets G2 (every city's picks are must-differ rows): a pool
    variant (`london/key-takeaways/b`) is copied onto a later city's canvas with ONE refresh delta
    and recorded `from_pool`; when that copy is picked it becomes a must-differ row, and London's
    closed canvas then failed against its own refreshed copy ("b is within one axis of existing
    style manchester/key-takeaways/c"; check:all red after 30a23536). A row that is a pool copy of
    the very variant being judged is skipped; any other city's pick is still judged."""
    m = _meta()
    copy = {"shape": "city", "id": "manchester/key-takeaways/c", "name": "Tick card",
            "axes": dict(m["variants"]["a"]["axes"]), "used_by": ["blue-staffy-puppies-manchester-uk"]}
    md = {"key-takeaways": [copy]}
    # The live copy's source is london/key-takeaways/b: judging London's variant b skips it ...
    out = C.validate_meta("key-takeaways", {**m, "variants": {"b": m["variants"]["a"]}},
                          ctx(city="london", ideas={"key-takeaways": IDEAS.get("hero", "")}, must_differ=md))[0]
    assert not [x for x in out if "manchester/key-takeaways/c" in x], out
    # ... and London's variant a, which is not its source, is still judged against it.
    out = C.validate_meta("key-takeaways", m, ctx(city="london", ideas={"key-takeaways": IDEAS.get("hero", "")}, must_differ=md))[0]
    assert any("within one axis of existing style manchester/key-takeaways/c" in x for x in out), out
    assert C.pool_source("manchester/key-takeaways/c") == "london/key-takeaways/b"
    assert C.pool_source("manchester/tables/a") is None
