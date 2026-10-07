"""London's own page file and the city scaffold invariants (the London component design pass,
Plan 2; spec §3.2; rewritten at page-run row 12 when London's page was written).

src/pages/uk-locations/blue-staffy-puppies-london.astro mounts London's picked city components
on CityShell (PageShell with the city's own nav set). It began as a scaffold with placeholder
copy; London's page run has now written it (tests/py/test_london_page.py holds the page). What
must hold here:
  - one route, one source: the dynamic [slug].astro no longer builds London, and the other 27
    cities are still built by it;
  - any page that is still a scaffold is noindex and in no sitemap shard;
  - every component on London's page is one of London's picks, the city nav set is mounted and
    the kit's is not;
  - the FAQPage node carries exactly the visible questions, and no other heading repeats one
    (learning loop L11);
  - each served photo keeps its served alt (or the board's recorded `verbatim.changed` alt) on
    its first use, and a repeat carries a new alt.
The migrated body is gone from London's page: London is held by `check:facts` against
data/facts/blue-staffy-puppies-london.json instead of by a word-for-word copy here.
"""
import html as H
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SLUG = "blue-staffy-puppies-london"
PAGE = ROOT / "src/pages/uk-locations" / f"{SLUG}.astro"
BUILT = ROOT / "dist/uk-locations" / SLUG / "index.html"
PICKS = json.loads((ROOT / "data/design/city-picks" / f"{SLUG}.json").read_text())
LOCATIONS = json.loads((ROOT / "data/locations.json").read_text())

#: The kit root each picked canvas variant was built as (the London component design pass).
PICK_ROOTS = {
    "london/hero/b": 'class="city-kit kit-hero city-hero-filmstrip',
    "london/counter-strip/c": 'class="city-kit city-scale',
    "london/trust-strip/c": 'class="city-kit city-trust',
    "london/contents-list/c": 'class="city-kit city-contents-photo-index',
    "london/desktop-dial/c": "data-city-dial-photo-marker",
    "london/jump-links/a": "data-city-jump-stepper",
    "london/key-takeaways/a": 'class="city-kit city-takeaways-ledger',
    "london/puppy-cards/b": 'class="city-kit city-sheet',
    "london/tables/a": 'class="city-kit city-roster',
    "london/video/c": 'class="city-kit city-video',
    "london/image-text/c": 'class="city-kit city-chapters',
    "london/reviews/a": 'class="city-kit city-letter',
    "london/faq-blocks/a": 'class="city-kit city-faq',
    "london/newsletter/a": 'class="city-kit city-newsletter-notice',
    "london/contact-form/b": 'class="city-kit city-contact',
}


def built():
    if not BUILT.exists():
        pytest.skip("run npm run build first")
    return BUILT.read_text(encoding="utf-8")


def text(fragment):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def test_the_scaffold_file_exists():
    assert PAGE.is_file()


def test_the_template_builds_exactly_the_routes_the_date_map_gives_it():
    """One route, one source, as BEHAVIOUR (the quality review, M4): the city pages built
    without a scaffold are exactly the routes scripts/generate_page_dates.py assigns to
    src/pages/uk-locations/[slug].astro, so the template and the dates agree on which cities it
    builds, whichever form (<slug>.astro or <slug>/index.astro) a city's own page takes."""
    built()
    sys.path.insert(0, str(ROOT / "scripts"))
    import generate_page_dates as G
    static = [p for p in sorted(G._rel("src/pages/**/*.astro")) if p not in G.DYNAMIC and "[" not in p]
    template = {r for r, _ in G.expand("src/pages/uk-locations/[slug].astro",
                                        frozenset(G.route_for(p) for p in static))}
    # A city with its own page file (London; Manchester, rebuilt at its page run's row 12) is not
    # the template's: the scaffold mark used to stand in for "its own file" while Manchester was one.
    own = {p.stem for p in PAGE.parent.glob("*.astro") if "[" not in p.name} | \
          {p.parent.name for p in PAGE.parent.glob("*/index.astro")}
    plain = {f"/uk-locations/{d.name}/" for d in (ROOT / "dist/uk-locations").iterdir()
             if (d / "index.html").is_file() and d.name != SLUG and d.name not in own
             and "data-city-scaffold" not in (d / "index.html").read_text(encoding="utf-8")}
    assert template and plain == template


def test_london_has_its_own_file_and_every_other_city_the_template():
    html = built()
    assert "prose-migrated" not in html, "London is rebuilt; its migrated body is gone"
    # Every city without its own page file (Manchester has one too from its page run's Phase F
    # Task 32, a scaffold held by tests/py/test_manchester_scaffold.py).
    own = {p.stem for p in PAGE.parent.glob("*.astro") if "[" not in p.name}
    others = [l["slug"] for l in LOCATIONS if l["slug"] not in own]
    assert SLUG in own and len(others) == len(LOCATIONS) - len(own & {l["slug"] for l in LOCATIONS})
    for slug in others:
        page = ROOT / "dist/uk-locations" / slug / "index.html"
        assert page.is_file(), slug
        body = page.read_text(encoding="utf-8")
        assert "prose-migrated" in body and "data-city-scaffold" not in body, slug


def _scaffolds():
    """{route: html} for every built page that carries `data-city-scaffold`."""
    out = {}
    for f in (ROOT / "dist").rglob("index.html"):
        html = f.read_text(encoding="utf-8")
        if "data-city-scaffold" in html:
            rel = f.parent.relative_to(ROOT / "dist").as_posix()
            out["/" if rel == "." else f"/{rel}/"] = html
    return out


def test_every_scaffold_is_noindex_and_in_no_sitemap():
    """The invariant, for any city (the quality review, M6). Once London is rebuilt there may
    be no scaffold at all, and that is a pass, not a skip."""
    built()
    shards = [s.read_text(encoding="utf-8") for s in (ROOT / "dist").glob("*sitemap*.xml")]
    assert shards
    for route, html in _scaffolds().items():
        assert re.search(r'<meta name="robots" content="noindex[^"]*"', html), route
        assert not [s for s in shards if f"{route}<" in s or f"{route}\"" in s], route


def test_no_rebuilt_page_carries_a_scaffold():
    """A page in data/facts/rebuilt.json is a finished page; placeholder copy on it is a
    scaffold that shipped (the quality review, M6)."""
    built()
    rebuilt = json.loads((ROOT / "data/facts/rebuilt.json").read_text())
    routes = {"/" if s == "index" else f"/{s}/" for s in rebuilt}
    assert not routes & set(_scaffolds())


def test_every_component_on_the_page_is_a_london_pick_and_the_nav_set_is_the_citys():
    """The kit is a menu (rules/gates.md outline-before-components): the approved outline
    decides which picks are used, so the page may use fewer than fifteen, never another's."""
    html = built()
    assert set(PICK_ROOTS) == set(PICKS["picks"].values())
    used = [key for key, root in PICK_ROOTS.items() if root in html]
    assert "london/hero/b" in used and "london/faq-blocks/a" in used
    assert html.count('data-faq-block="') == 3, "the three FAQ blocks"
    for kit in ('class="kit-dial', 'class="kit-strip', 'class="kit-sheet'):
        assert kit not in html, kit
    band = re.search(r"<div[^>]*data-city-jump-stepper[^>]*>", html).group(0)
    assert "data-strip" in band, "on a real page the band is the top chrome"


def test_every_nav_link_names_a_section_on_the_page():
    html = built()
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    spies = re.findall(r'data-spy="([^"]+)"', html)
    assert len(set(spies)) >= 6
    assert not [s for s in spies if s not in ids]


def test_the_faq_schema_carries_exactly_the_visible_questions():
    html = built()
    visible = [text(q) for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", html, re.S)]
    # The approved board's three FAQ trees set the count (21 since the breeder's q04 of
    # 2026-10-02 added the rarity question); tests/py/test_london_page.py holds them question
    # by question.
    board = json.loads((ROOT / "data/boards" / f"{SLUG}.json").read_text())
    approved = sum(len(s["tree"]) for s in board["sections"] if s.get("shape") == "faq")
    assert len(visible) == approved, (len(visible), approved)
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    nodes = [n for b in blocks for n in (b if isinstance(b, list) else [b]) if n.get("@type") == "FAQPage"]
    assert len(nodes) == 1
    named = [q["name"] for q in nodes[0]["mainEntity"]]
    assert [n.lower() for n in named] == [v.lower() for v in visible]


def test_no_section_heading_repeats_an_faq_question():
    """Learning loop 2026-09-27, L11: a real heading that is also an FAQ question."""
    html = built()
    faq = {text(q).lower() for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", html, re.S)}
    assert faq, "the page's FAQ questions are found"
    heads = [text(h) for h in re.findall(r"<h[1-3](?![^>]*data-faq-q)[^>]*>(.*?)</h[1-3]>", html, re.S)]
    assert not [h for h in heads if h.lower() in faq]


def scaffold_alt_defects(main, served, changed=None):
    """The body's served photos: the first use of each keeps its served alt (working rule 11),
    or the board's recorded `verbatim.changed` alt for it (working rule 15), and each repeat
    carries a new alt, never a copy of one already used for it (the user's ruling, answer board
    q02, 2026-09-29: "No repeated alt, same photo use new alt"). A file the old site never
    served (a puppy card, an infographic published after the migration) has no served alt to
    keep and is not judged here."""
    out, used, changed = [], {}, changed or {}
    for name, alt in re.findall(r'<img [^>]*src="/images/([^"?]+)"[^>]*alt="([^"]*)"', main):
        alt = H.unescape(alt)
        if alt == "" or name not in served:
            continue  # decorative, or never served: neither claims the first-use slot
        if name not in used:
            if alt not in served[name] and alt not in changed.get(name, ()):
                out.append(f"{name}: its first use does not carry its served alt")
        elif alt in used[name]:
            out.append(f"{name}: a repeat copies the alt {alt!r}")
        used.setdefault(name, set()).add(alt)
    return out


def test_a_repeat_with_a_new_alt_is_allowed_on_the_scaffold():
    """The user's ruling (answer board q02, 2026-09-29): a photo shown twice keeps its served
    alt on its first use, and the repeat carries a new alt."""
    served = {"Christa.jpeg": frozenset({"Christa"})}
    ok = '<img src="/images/Christa.jpeg" alt="Christa"><img src="/images/Christa.jpeg" alt="Christa, sitting up">'
    assert scaffold_alt_defects(ok, served) == []
    copy = '<img src="/images/Christa.jpeg" alt="Christa"><img src="/images/Christa.jpeg" alt="Christa">'
    assert scaffold_alt_defects(copy, served) == ["Christa.jpeg: a repeat copies the alt 'Christa'"]
    decorative_first = '<img src="/images/Christa.jpeg" alt=""><img src="/images/Christa.jpeg" alt="Brand new">'
    assert scaffold_alt_defects(decorative_first, served) == ["Christa.jpeg: its first use does not carry its served alt"]
    # A decorative alt="" never claims the first-use slot: the served alt after it IS the first use.
    decorative_then_served = '<img src="/images/Christa.jpeg" alt=""><img src="/images/Christa.jpeg" alt="Christa">'
    assert scaffold_alt_defects(decorative_then_served, served) == []


def test_each_served_photo_keeps_its_served_alt_first_and_a_new_alt_on_a_repeat():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_city_canvas import served_alts
    served = served_alts()
    html = built()
    found = re.findall(r'<img [^>]*src="/images/([^"?]+)"[^>]*>', html)
    main = html.split("<main", 1)[1].split("</main>", 1)[0]
    assert re.search(r'<img [^>]*src="/images/', main), "the page reuses served photographs"
    board = json.loads((ROOT / "data/boards" / f"{SLUG}.json").read_text())
    changed = {}
    for r in (board.get("verbatim") or {}).get("changed", []):
        if r.get("kind") == "alt" and r.get("src"):
            changed.setdefault(r["src"].rsplit("/", 1)[-1], set()).add(r["new"])
    assert scaffold_alt_defects(main, served, changed) == []
    assert found


def primary_keyword_alt_defects(main, primary_keyword, primary_alts):
    """Rule 50b (rules/images.md image-keyword-distribution): the page's primary keyword goes in
    the PRIMARY image's alt only; every other image rotates a different keyword type. The alts in
    `main` (other than the primary image's own) that carry the keyword, compared on words alone
    (case, punctuation and spacing ignored), so "Blue Staffy puppies London" is a hit and
    "blue Staffy puppy ... in London" is not."""
    def norm(s):
        return " ".join(re.sub(r"[^a-z0-9]+", " ", s.lower()).split())
    kw = norm(primary_keyword)
    return [H.unescape(alt) for alt in re.findall(r'<img [^>]*alt="([^"]*)"', main)
            if f" {kw} " in f" {norm(H.unescape(alt))} " and H.unescape(alt) not in primary_alts]


def test_the_primary_keyword_check_finds_it_only_outside_the_primary_image():
    kw = "blue staffy puppies london"
    hit = '<img src="/images/a.webp" alt="Maggie, the dam behind our blue Staffy puppies London families meet">'
    assert primary_keyword_alt_defects(hit, kw, set()) == [
        "Maggie, the dam behind our blue Staffy puppies London families meet"]
    assert primary_keyword_alt_defects(hit, kw, {"Maggie, the dam behind our blue Staffy puppies London families meet"}) == []
    near = '<img src="/images/b.webp" alt="Mark with their healthy blue Staffy puppy from BlueStaffyUK.uk in London.">'
    assert primary_keyword_alt_defects(near, kw, set()) == []


def test_london_carries_its_primary_keyword_in_no_alt_but_the_primary_images():
    """London's primary (hero) image is the Maggie photo's FIRST use, which keeps its served alt
    (working rule 11), so the primary keyword sits in no alt; the repeat (slot litter-parents-dam)
    carried it in the hero's place until 2026-10-04, which 50b's "only" forbids."""
    board = json.loads((ROOT / "data/boards" / f"{SLUG}.json").read_text())
    queries = json.loads((ROOT / "data/queries" / f"{SLUG}.json").read_text())
    primary = {a["alt"] for a in board["assets"] if a.get("slot") == "london-hero"}
    assert primary, "the board names its primary image"
    main = built().split("<main", 1)[1].split("</main>", 1)[0]
    assert re.search(r'<img [^>]*alt="', main), "the page's images are read"
    assert primary_keyword_alt_defects(main, queries["primary_keyword"], primary) == []


def test_london_keeps_the_date_its_url_was_first_published():
    """The URL has existed since the migration (2026-09-16); moving it from the template to its
    own file changes its source, not its publication (Plan 2 Task 8 spec review)."""
    dates = json.loads((ROOT / "data/page-dates.json").read_text())["routes"]
    row = dates[f"/uk-locations/{SLUG}/"]
    assert row["datePublished"] == "2026-09-16"
    assert row["dateModified"] >= row["datePublished"]
