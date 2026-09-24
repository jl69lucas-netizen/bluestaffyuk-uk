"""The project-5 builder skills say what the code does (Known Issue 40).

A builder skill is the instruction a page is built from, and four of Known Issue 40's items
were places where the location builder said something the repo contradicts: its precedence
table stopped at rule 10 while rule 15 governs every city page with a body; it said "no
variant prop" while `Hero` takes four arrangement props; its worked example handed variant
letters to components and gave every city the same counter; and it told the builder to
hand-record a competitor table in a board block the schema does not have. Each test below
reads the skill for the sentence that was wrong and for the one that replaced it, so the fix
cannot quietly revert. The comparison builder gets the same treatment for its section count.
"""
import copy
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pageboard  # noqa: E402
LOCATION = (ROOT / ".claude/skills/bsuk-location-page-builder/SKILL.md").read_text(encoding="utf-8")
COMPARISON = (ROOT / ".claude/skills/bsuk-comparison-page-builder/SKILL.md").read_text(encoding="utf-8")
BLOG = (ROOT / ".claude/skills/bsuk-blog-post/SKILL.md").read_text(encoding="utf-8")
CHECKLIST = (ROOT / ".claude/skills/bsuk-seo-master-checklist/SKILL.md").read_text(encoding="utf-8")
MD_LINK = re.compile(r"\]\((https?://[^)\s]+)\)")


def norm(text):
    """Whitespace-collapsed, so a phrase a line wrap splits still matches."""
    return " ".join(text.split())


def section(text, heading):
    """The body of the `## heading` section, up to the next `## `."""
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    return text[start:nxt if nxt != -1 else len(text)]


def test_the_precedence_table_cites_rules_15_and_16():
    table = section(LOCATION, "## What wins when this file and something else disagree")
    assert "judgment rules 1–10" not in table
    assert re.search(r"faithful rewrite \(15\)", table), table
    assert re.search(r"per-page hero and counter, and a refresh delta on every section \(16\)",
                     norm(table)), table


def test_the_hero_wording_matches_hero_astro():
    hero = (ROOT / "src/components/kit/Hero.astro").read_text(encoding="utf-8")
    for prop in ("layout", "align", "media", "ledge"):
        assert re.search(r"\b%s\?:" % prop, hero), "Hero.astro no longer declares %s" % prop
        assert "`%s`" % prop in LOCATION, "the builder does not name Hero's `%s` prop" % prop
    assert "pickedStyle" in LOCATION, "the arrangement props come from the board pick"


def test_the_worked_example_hands_no_letter_to_a_component():
    example = section(LOCATION, "## Worked example")
    letter = re.compile(r"`(?:Hero|CounterStrip|TrustStrip|PageNav|InfoCard|Faq|PuppyCard|"
                        r"ContactFormKit|Testimonial)`\s+[a-d]\b")
    assert not letter.findall(example), letter.findall(example)
    assert "pups available · £500 refundable · £200–£350 delivery" not in example, (
        "a counter set written into the example is a counter every city page would share")


def arrangement_paragraph():
    """The paragraph that says which props come from the board pick."""
    start = LOCATION.index("**No `variant` prop and no letter")
    return norm(LOCATION[start:LOCATION.index("\n\n", start)])


def test_the_board_pick_arranges_hero_and_counter_but_never_a_city_review():
    para = arrangement_paragraph()
    assert "Testimonial" not in para.replace('Testimonial mode="single"', ""), (
        "a board-picked review style can be a grid; a city review is always single")
    assert 'Testimonial mode="single"' in para and "`S1`" in para and "styles: []" not in para
    assert "layout={pick.layout.hero}" in para, "the hero's layout is the style's `hero` axis"
    for axis in ("align", "media", "ledge", "tiles", "label"):
        assert "%s={pick.layout.%s}" % (axis, axis) in para, axis


def test_a_review_section_cannot_offer_no_styles():
    """Why the skill says S1 and not `styles: []`: the board schema makes every kit shape,
    reviews included, offer three styles, so an empty list is not a way out of the grid."""
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "schemas/board.schema.json").read_text(encoding="utf-8"))
    board = json.loads((ROOT / "data/boards/blue-staffy-health-uk.json").read_text(encoding="utf-8"))
    jsonschema.validate(copy.deepcopy(board), schema)
    review = next(s for s in board["sections"] if s["shape"] == "reviews")
    review["styles"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(board, schema)


def test_every_review_slot_is_a_single_block():
    assert 'Testimonial mode="grid"' not in LOCATION
    assert "never uses one" in norm(section(LOCATION, "## Step 2")), "the grid ruling must be stated"


def test_the_competitor_record_is_the_question_file_not_a_board_block():
    step1 = section(LOCATION, "## Step 1")
    assert "competitor block" not in norm(LOCATION).replace("no competitor block", "")
    assert "| sections | its H2 list, verbatim |" not in step1
    assert "`competitors`" in step1 and "`why_source`" in step1


def test_body_sections_are_labelled_sections():
    assert "data-section-label" in section(LOCATION, "## Step 2")


def test_a_health_test_result_is_not_a_city_page_fact():
    facts = section(LOCATION, "## The facts a city page may state")
    assert "parents-dna-clear" in facts and "NOT FETCHED" in facts


def test_the_comparison_builder_derives_its_section_count():
    assert not re.search(r"22[–-]25|\b22[- ]section", COMPARISON)
    assert "section_target" in COMPARISON


def test_the_comparison_builder_has_no_source_site_polish_leftovers():
    for leftover in ("cvt-", "CvT", "CvM", "CvC", "MvF", "blue-brindle", "Blue-Brindle",
                     "vs-french", "map-pin"):
        assert leftover not in COMPARISON, leftover
    polish = section(COMPARISON, "## 12.") + section(COMPARISON, "## 13.")
    for route in ("/blue-staffy-uk-breeders/", "/buy-blue-staffy-puppies-uk/"):
        assert route not in polish, route


def test_the_comparison_layout_rules_name_no_fixed_header_or_toc_size():
    layout = section(COMPARISON, "## 11.")
    for fixed in ("96px", "200px"):
        assert fixed not in layout, fixed


def test_the_blog_builder_uses_the_link_library_and_the_registry():
    assert "docs/reference/external-link-library.md" in BLOG
    assert "data/competitors.json" in BLOG
    assert "This file governs in any conflict" not in BLOG


def test_the_blog_builder_has_no_source_site_leftovers():
    for leftover in ("best-place", "crate-setup", "Batch-2", "assets/BSUK-BLOG-POSTS",
                     "quality=82", "1408×768", "media=print", "interaction-deferred",
                     "/blog/uk-staffordshire", "FAQ / 3 zones", "all 9 posts",
                     "the other 8 posts"):
        assert leftover not in BLOG, leftover
    assert "`/<slug>/`" in BLOG
    assert "sources.serp_google" not in BLOG
    assert "data/queries/raw/<slug>/serp_google.json" in BLOG
    for fact in ("src/content.config.ts", "SiteFooterKit", "POST_EXEMPT_CHECKS"):
        assert fact in BLOG, fact
    assert "confirm ≥5 H5 / ≥5 H6 still hold" not in BLOG
    delivery = ("UK home delivery by DEFRA-approved transport, priced by distance, "
                "£200–£350 · or collect in Carlisle")
    assert BLOG.count(delivery) >= 2


def test_the_checklist_external_links_are_library_rows():
    """Known Issue 40: the checklist's external-link list was the source site's US set (AVMA,
    AAHA, ASPCA, the FTC, Chewy). Every URL it lists now must be a row of
    docs/reference/external-link-library.md, the list scripts/pageboard.py enforces on boards."""
    start = CHECKLIST.index("#### B. External Links")
    block = CHECKLIST[start:CHECKLIST.index("#### C.", start)]
    urls = MD_LINK.findall(block)
    assert len(urls) >= 10, urls
    library = pageboard.library_urls()
    assert library, "docs/reference/external-link-library.md is missing"
    missing = [u for u in urls if pageboard.normalise_url(u) not in library]
    assert missing == [], "not rows of the external-link library: %s" % missing


def test_the_checklist_has_no_source_site_quotas_or_us_sources():
    """Known Issue 40, the rest of it: the checklist still carried the source site's fixed
    quotas (50+ internal and external links, a 22+-section page, a 5,000–6,000-word total, three
    newsletter signups), a US source (petmd, .edu) and a founding year BSUK has not given. No BSUK
    rule sets those numbers: rules/links.md sets placement, Rule 62 the targets, the page's
    question file the section count, and the location template one newsletter block."""
    leftovers = ["petmd", ".edu", "Since 2014", "since 2014", "22+ sections", "50+ external",
                 "50+ validated", "50+ Required", "50+ contextual", "newsletter signups",
                 "5,000–6,000", "Customer Case Study", "Related Blue Staffy Varieties"]
    assert [s for s in leftovers if s.lower() in CHECKLIST.lower()] == []
    assert not re.search(r"(?<![\d,.])50\+", CHECKLIST), "a 50+ quota is left"
    start = CHECKLIST.index("### Step 5: Page Structure Planning")
    step5 = CHECKLIST[start:CHECKLIST.index("### Step 6", start)]
    assert "Candidate topics" in step5 and "section_target.total" in step5
    assert 'Testimonial mode="single"' in step5
    assert 'label="Newsletter"' in CHECKLIST


def test_the_checklist_invents_no_route_or_guarantee_and_seo_rules_derive_the_count():
    """Rule 62: /testimonials/ is not a route. data/settings.json has guarantee_days null, so
    every line that says "guarantee" names the setting that gates it. Rules 59 and 60 in
    docs/reference/seo-rules.md took the source site's 22+ sections; the count is derived."""
    assert "/testimonials/" not in CHECKLIST
    ungated = [line for line in CHECKLIST.splitlines()
               if "guarantee" in line.lower() and "guarantee_days" not in line]
    assert ungated == [], ungated
    seo_rules = (ROOT / "docs/reference/seo-rules.md").read_text(encoding="utf-8")
    assert "22+" not in seo_rules
    assert seo_rules.count("section_target.total") >= 2


SITE_ROUTE = re.compile(r"(?<![\w./~>…-])/[a-z0-9-]+(?:/[a-z0-9-]+)*/(?![\w<\[{])")

#: Paths that are not pages and never will be, each for a stated reason. Every other
#: site-root path a skill writes must be a page (see known_routes()).
NOT_PAGES = (
    "/70de/",        # the edge host's Google tag gateway script (bsuk-perf-gate, --live only)
    "/cf-fonts/",    # the edge host's rewrite of a Google Fonts link (same)
    "/wp-content/",  # the legacy WordPress site's upload folder: a migrated body may still link it
    "/tag/",         # the legacy WordPress site's tag archive (same)
    "/cdn-cgi/",     # the edge host's own script path (email obfuscation; bsuk-performance-fixer)
)


def known_routes():
    """Every route a page may link: built (dist/**/index.html), mapped (data/page-map.json),
    redirected (a source in data/redirects.json — `*` and `:param` sources are patterns), or a
    path under a public/ folder (an asset, not a page) or in NOT_PAGES."""
    dist = ROOT / "dist"
    built = {"/%s/" % p.parent.relative_to(dist).as_posix() for p in dist.rglob("index.html")}
    built |= {p["url"] for p in json.loads((ROOT / "data/page-map.json").read_text(encoding="utf-8"))["pages"]}
    sources = [r["from"] for r in json.loads((ROOT / "data/redirects.json").read_text(encoding="utf-8"))["redirects"]]
    patterns = [re.escape(s).replace(r"\*", ".*") for s in sources]
    patterns = [re.sub(r":[a-z]+", "[^/]+", s) for s in patterns]
    prefixes = tuple(NOT_PAGES) + tuple("/%s/" % d.name for d in (ROOT / "public").iterdir() if d.is_dir())
    return built, re.compile("(?:%s)$" % "|".join(patterns)), prefixes


def is_known(route, known):
    built, redirected, prefixes = known
    return route in built or bool(redirected.match(route)) or route.startswith(prefixes)


def route_offenders(text, known):
    """Rule 62: never invent an internal URL. Every site-root route the text writes (in
    backticks, links or plain text) must be known. External URLs are left out; a generic route
    is written `/<slug>/`, `/[slug]/` or `/{slug}/`, which SITE_ROUTE does not read. A line that
    says it is the source repo's history ("source repo" on the line) is not an instruction."""
    text = re.sub(r"https?://\S+", " ", text.replace("https://SITE_URL_PLACEHOLDER", ""))
    return sorted({(route, n) for n, line in enumerate(text.splitlines(), 1)
                   if "source repo" not in line
                   for route in SITE_ROUTE.findall(line) if not is_known(route, known)})


@pytest.mark.skipif(not (ROOT / "dist/index.html").is_file(), reason="no dist/ — run the build first")
def test_every_route_the_checklist_names_is_built_or_redirected():
    offenders = route_offenders(CHECKLIST, known_routes())
    assert offenders == [], "routes that are neither built nor redirected: %s" % offenders


# The same guard over every skill and slash command (the residue lint's set in
# tests/py/test_agent_facts.py). The agents follow below, with two exemptions of their own.
ROUTE_TARGETS = (sorted((ROOT / ".claude/skills").glob("*/SKILL.md"))
                 + sorted((ROOT / ".claude/commands").rglob("*.md")))


@pytest.mark.skipif(not (ROOT / "dist/index.html").is_file(), reason="no dist/ — run the build first")
@pytest.mark.parametrize("path", ROUTE_TARGETS,
                         ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem)
def test_every_route_a_skill_or_command_names_is_built_or_redirected(path):
    offenders = route_offenders(path.read_text(encoding="utf-8"), known_routes())
    assert offenders == [], "%s names routes that are neither built nor redirected: %s" % (
        path.relative_to(ROOT), offenders)


# The agents too (Task 18 follow-up, 2026-09-24). Two things an agent writes that are not
# BSUK routes: another site's path on a line that names that site's domain (the intel agents
# describe competitors' URL shapes), and a `/tmp/` scratch path. Everything else is a page.
AGENT_ROUTE_TARGETS = sorted((ROOT / ".claude/agents").glob("bsuk-*.md"))
COMPETITOR_DOMAINS = tuple(sorted({c["root_domain"] for c in json.loads(
    (ROOT / "data/competitors.json").read_text(encoding="utf-8"))["competitors"]}))


def agent_route_offenders(text, known):
    kept = "\n".join("" if any(d in line for d in COMPETITOR_DOMAINS) else line
                     for line in text.splitlines())
    return [(route, n) for route, n in route_offenders(kept, known) if not route.startswith("/tmp/")]


@pytest.mark.skipif(not (ROOT / "dist/index.html").is_file(), reason="no dist/ — run the build first")
@pytest.mark.parametrize("path", AGENT_ROUTE_TARGETS, ids=lambda p: p.stem)
def test_every_route_an_agent_names_is_built_or_redirected(path):
    offenders = agent_route_offenders(path.read_text(encoding="utf-8"), known_routes())
    assert offenders == [], ("%s names routes that are neither built nor redirected — a placeholder "
                             "is written `/<slug>/`, a real page by its real route: %s" % (
                                 path.relative_to(ROOT), offenders))


def test_the_agent_route_guard_spares_competitor_paths_and_scratch_files():
    known = ({"/available-puppies/"}, re.compile(r"(?:/wp-admin/.*)$"), ("/images/",))
    domain = COMPETITOR_DOMAINS[0]
    text = ("posts at %s/how-to-choose-a-puppy/\n" % domain
            + "cp x /tmp/img-staging/y\n"
            + "a dated segment (`/2025/09/`)\n"
            + "CTA → /contact/\n")
    assert agent_route_offenders(text, known) == [("/2025/09/", 3), ("/contact/", 4)]


def test_the_route_guard_reads_links_and_skips_placeholders_and_source_repo_history():
    known = ({"/available-puppies/", "/uk-locations/"}, re.compile(r"(?:/wp-admin/.*)$"),
             ("/images/", "/70de/"))
    text = ("- Our Puppies → /available/\n"
            "[About](/about/) and `/contact/`\n"
            "/uk-locations/<slug>/ and /available-puppies/[slug]/ and /{slug}/\n"
            "https://SITE_URL_PLACEHOLDER/blog/ and https://example.com/testimonials/\n"
            "Same bug found on `/available/` in the source repo.\n"
            "`src/pages/search/index.astro` and dist/available/index.html\n"
            "/wp-admin/ is redirected; `/images/…` and `/70de/` are not pages\n"
            "`openspec/changes/<name>/specs/` and www.reddit.com/r/…/comments/…\n")
    # a SITE_URL_PLACEHOLDER link is a site route (/blog/ is read); an outside URL is not
    assert route_offenders(text, known) == [("/about/", 2), ("/available/", 1), ("/blog/", 4),
                                            ("/contact/", 2)]


def test_the_checklist_newsletter_links_reviews_and_claims_match_the_builders():
    """One newsletter block (frame part 10), Link-First links with no per-section count, reviews
    only in their own three sections, no claim a data file does not back (a reply time, a named
    socialisation programme, a teacup or champion pup), FAQ counts from the question file, and
    Rules 26/27 in docs/reference/seo-rules.md derived from the competitor scan."""
    low = CHECKLIST.lower()
    banned = ["3 per full hub page", "newsletter signup", "5–8 per section", "5–8 internal links",
              "5–8 total", "beginning or middle", "testimonial quote", "testimonial box",
              "24 hours", "30+ faq", "30+ questions", "teacup", "champion bloodline"]
    assert [b for b in banned if b in low] == []
    unconfirmed = [line for line in CHECKLIST.splitlines()
                   if re.search(r"(?i:puppy.culture|neonatal|neurological)|\bEN[HS]\b", line)
                   and "NOT FETCHED" not in line]
    assert unconfirmed == [], unconfirmed
    assert 'label="Newsletter"' in CHECKLIST and 'id="newsletter"' in CHECKLIST
    start = CHECKLIST.index("## APPENDIX B")
    appendix_b = CHECKLIST[start:CHECKLIST.index("## APPENDIX C", start)]
    library = pageboard.library_urls()
    assert [u for u in MD_LINK.findall(appendix_b) if pageboard.normalise_url(u) not in library] == []
    seo_rules = (ROOT / "docs/reference/seo-rules.md").read_text(encoding="utf-8")
    assert [s for s in ("22–24", "22-24", "5,000–6,000", "5–8 internal") if s in seo_rules] == []
    rule_27 = seo_rules[seo_rules.index("**Rule 27"):seo_rules.index("**Rule 28")]
    assert "median" in rule_27 and "NOT FETCHED" in rule_27
    rule_26 = seo_rules[seo_rules.index("**Rule 26"):seo_rules.index("**Rule 27")]
    assert "section_target.total" in rule_26


RULE_CITE = re.compile(r"\bRules?\s+(\d{1,2}[a-z]?\b(?:\s*(?:,|and|–)\s*\d{1,2}[a-z]?\b(?![-\d]))*)")


def test_the_checklist_full_sweep_no_unbacked_claims_and_every_cited_rule_exists():
    """The sweep: no credential, award, founding length, promise or kennel description BSUK's
    data does not back; no quota the rule packs do not set; and every "Rule NN" the checklist
    cites is a heading of docs/reference/seo-rules.md (Rules 44–50b were the source site's
    wildlife regime, deleted in the port, and 28b never existed)."""
    low = CHECKLIST.lower()
    banned = ["decade", "lifetime", "canine vet certified", "registered kennel", "+ 1,000",
              "(20+", "(15+", "(10+", "250+", "15+ form", "(80+", "100+ required",
              "first 300 words", "aggregaterating schema", "image-specs.json",
              "bluestaffyuk kennel", "visit the kennel", "kennel specialists", "licenced kennel",
              "kennel location", "blue staffy kennel", "kennel puppy", "ultimate choice for [",
              "learn more about [", "read more about [", "max 275", "extended 290"]
    assert [b for b in banned if b in low] == []
    seo_rules = (ROOT / "docs/reference/seo-rules.md").read_text(encoding="utf-8")
    exists = set(re.findall(r"^\*\*Rule (\d+[a-z]?) —", seo_rules, re.M))
    cited = {n for group in RULE_CITE.findall(CHECKLIST) for n in re.findall(r"\d{1,2}[a-z]?\b", group)}
    assert cited and sorted(cited - exists) == [], sorted(cited - exists)
    counters = CHECKLIST[CHECKLIST.index("**Counter Snippets"):CHECKLIST.index("**Contact/Inquiry Forms")]
    for counter in ("£500 Refundable Deposit", "12–14 Year Lifespan", "28 UK Cities Covered",
                    "Home-Reared in Carlisle"):
        assert counter in counters, counter
    step5 = CHECKLIST[CHECKLIST.index("**Header count targets"):CHECKLIST.index("**Two-Keyword Header")]
    for level in ("H2: 25–35", "H3: 40–50", "H4: 10–20", "H5: minimum 5", "H6: minimum 5"):
        assert level in step5, level


# ── the board gate and the per-page audits (Task 11 review) ──────────────────
GRILL_ME = (ROOT / ".claude/skills/grill-me/SKILL.md").read_text(encoding="utf-8")
PAGE_AUDITS = ("final_page_audit.py", "evidence_audit.py", "aeo_audit.py")


def test_grill_me_gate_one_is_the_approved_board_not_the_page_map():
    # All 28 city pages are in data/page-map.json and none has a board, so a gate that asked
    # "is the page in the map?" passed every city and never said "board first".
    gate = norm(GRILL_ME[GRILL_ME.index("WORKFLOW GATE CHECK"):GRILL_ME.index("2. Has @bsuk-content-audit-agent")])
    assert "1. Is this page in data/page-map.json" not in gate
    for needle in ("board_gate.py <slug>", "data/boards/<slug>.json", "board_approve.py <slug>",
                   "data/boards/inbox"):
        assert needle in gate, needle
    # build_page_board.py raises on a slug with no record: never the first step.
    assert gate.index("data/boards/<slug>.json") < gate.index("build_page_board.py")
    for block in ("**If there is no approved board", "> **If there is no approved board"):
        assert block in GRILL_ME, block
    assert "board_gate.py" in GRILL_ME[GRILL_ME.index("**If there is no approved board"):][:600]


def test_the_location_builder_audits_the_city_page_it_builds():
    # A bare final_page_audit.py audits 14 flat pages and never a city page; a bare
    # evidence_audit.py matches 0 pages and exits 1; a bare aeo_audit.py exits 2.
    step6 = section(LOCATION, "## Step 6 — gates")
    for line in step6.splitlines():
        for script in PAGE_AUDITS:
            if script in line and line.strip().startswith("python3"):
                assert line.split(script, 1)[1].strip(), f"bare page audit: {line.strip()}"
    assert "python3 scripts/final_page_audit.py uk-locations/<slug> --type location" in step6
    assert "python3 scripts/evidence_audit.py uk-locations/<slug> --type location" in step6
    assert "report only by default" not in norm(step6)


def test_no_skill_says_a_page_audit_only_fails_with_fail_on_error():
    # final_page_audit exits 1 on any FAIL whatever the flag; --fail-on-error only adds WARNs
    # (aeo, evidence) or changes nothing (final, dup).
    manual = (ROOT / ".claude/skills/manual-auditor-check/SKILL.md").read_text(encoding="utf-8")
    assert "--fail-on-error to exit non-zero" not in manual
    assert "npx astro build" not in manual
    sitemap = (ROOT / ".claude/skills/sitemap-agent/SKILL.md").read_text(encoding="utf-8")
    assert "BSUK_RELEASE=1 python3 scripts/placeholder_check.py" in sitemap
