"""The breeder's answer (answer board q01, 2026-09-29): she holds no DNA certificates for Maggie
and Jones, so a page may NAME the tests (L-2-HGA, HC-HSF4, eye and elbow screening) and never
state a RESULT. "Tested clear", "certified clear", "clear for", "clear DNA results", "results on
request", "a clear pair", "will not be genetically affected" and every other stated result are
gone from the built site (Known Issue 98). The evidence ledger's `parents-dna-clear` row stays at
proof NOT FETCHED, and now records why: the breeder confirms none is held.

This holds every built file in dist/ (HTML text, meta and alt attributes, JSON-LD, llms.txt,
sitemaps) and the FAQ data to it. Board previews render the approved board records, which stay
as history. One migrated page is named below with its reason; it is not a pattern exemption.
"""
import html
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

TEST = r"(?:L-?2-?HGA|L2HGA|HC-?HSF4|\bHC\b|PHPV)"
# Patterns that state a result on their own, whatever sentence they sit in.
RESULT = [
    # "DNA tested clear", "certified clear", "recorded clear", "screened and certified clear"
    r"\b(?:tested|certified|recorded|screened|cleared|proven|confirmed)\s+(?:and\s+certified\s+)?clear\b",
    # "clear of L-2-HGA", "clear for key hereditary conditions" (not "clear for both": a reader
    # keeps a lead "clear for both" of them, and the health context below catches the rest)
    r"\bclear\s+(?:of|for)\s+(?:" + TEST + r"|key|common|hereditary|inherited)",
    r"\bgenetically\s+affected\b",
    r"\bclear\s+(?:DNA\s+)?(?:test\s+)?results?\b",
    r"\bclearances?\b",
    r"\bcleared\s+for\b",
    r"\bclear\s+(?:parents?|pair|dam|sire)\b",
    r"\brecords?\s+(?:both\s+)?parents\s+clear\b",
    # "L-2-HGA clear", "HC-HSF4 Clear", "(…Aciduria): CLEAR"
    TEST + r"\)?\s*:?\s*clear\b",
    TEST + r"[^.:]{0,60}:\s*clear\b",
    r"\bclear\s+both\s+parents\b",
    r"\bnon-?carriers?\b",
    # review minor 1: "L-2-HGA: normal", "lists her as clear", "scored well on her eye screening"
    TEST + r"\)?\s*:?\s*normal\b",
    r"\blists?\s+(?:her|him|them|both|the\s+(?:dam|sire|parents?))\s+as\s+clear\b",
    r"\bscored\s+well\s+on\b",
    r"\bcame\s+back\s+clear\b",
    r"[‘'\"]clear[’'\"]\s+results?",
    r"\bclear\s+certificates?\b",
    # a result or certificate on offer implies one is held
    r"\b(?:results?|certificates?)\s+on\s+request\b",
    r"\bthe\s+results\s+we\s+hand\s+over\b",
    r"\boffers?\s+(?:you\s+)?the\s+results\b",
    r"\b(?:healthy|good|negative|normal)\s+results?\b",
    r"\bresults?\s+(?:on|for|of)\s+(?:both|the|our)\s+parents\b",
    r"\bthe\s+certificates\s+are\s+yours\b",
    r"\b(?:send|show)\s+(?:you\s+)?(?:the|our|both|its)\s+(?:two\s+|DNA\s+)?certificates?\b",
    r"\bask\s+us\s+(?:for|to\s+see)\s+the\s+certificates\b",
    r"\b(?:with\s+their|their\s+health)\s+results\b",
    r"\bwhat\s+the\s+results\s+were\b",
    # a hip or elbow score stated as a figure
    r"\b(?:hip|elbow)\s+(?:score|grade)s?\s+(?:of|is|are|was)\s+\d",
]
RESULT_RE = re.compile("(?i)" + "|".join(RESULT))

# A sentence about a health test (review C3, 2026-09-29): any result word in it is a stated
# result, a promised result or a pointer to a certificate the breeder does not hold. Tied to the
# context so "Keep both clear of the road" or "the vaccination certificates" pass.
HEALTH_CONTEXT = re.compile(
    r"(?i)\bDNA\b|" + TEST + r"|\bhealth[- ]test\w*|\btest(?:s|ed|ing)?\b|\bscreen(?:ing|ed|s)?\b"
    r"|\beyes?\b|\belbows?\b|\bgenetic\w*|\bhereditary\b|\binherited\b")
RESULT_WORD = re.compile(
    r"(?i)\bclear(?:ed)?\b(?!\s+(?:eyes|overview))|\bnegative\b|\bresults?\b|\bcertificates?\b|\bcertified\b"
    r"|(?<!one )\bpass(?:ed|es)?\b(?!\s+(?:the\s+gene|it\s+on|either|that\s+condition|them\s+on|on\b|down\b"
    r"|facts-preserved|link\s+parity|the\s+form|every\s+gate|the\s+gate))"
    r"|\bunaffected\b|\bfree\s+(?:of|from)\b")
# Denials and plain descriptions of what a test is are not results.
# A coordinated denial ("never a result or a DNA certificate") is one denial: London's board
# record (2026-10-03) read its second half as a certificate on offer (the gate cried wolf).
_DENIED = r"(?:(?:DNA|test|health)\s+)?(?:results?|certificates?)"
DENIAL = re.compile(r"(?i)\b(?:no|never\s+a|not\s+a|not\s+any)\s+" + _DENIED
                    + r"(?:\s+(?:or|nor)\s+(?:an?\s+|any\s+)?" + _DENIED + r")?\b")
SENTENCE = re.compile(r"[^.!?|“”\"]+")

# Migrated pages, by name, with their EXACT hits pinned (review C4, 2026-09-29). Both are the old
# WordPress body rendered verbatim from data/locations.json (a generated file, never hand-edited),
# and their only route to a fix without re-dating 26 unchanged location pages is their project 5
# rebuild. Known Issue 98 carries them as open. The pin is the list of hit texts in
# tests/py/fixtures/migrated_health_results.json: a new hit on either page fails, and so does a
# page that has come clean (drop it from the pin then).
MIGRATED_PIN = ROOT / "tests/py/fixtures/migrated_health_results.json"
MIGRATED_OPEN = set(json.loads(MIGRATED_PIN.read_text(encoding="utf-8")))

# General advice to a buyer about ANY breeder, which names no dog of ours and states no result of
# ours: what a good answer sounds like, and what an unbacked claim is worth. Exact sentences, by
# page, so a new sentence is never excused by a pattern.
GENERAL_ADVICE = {
    "uk-blue-staffy-puppy-buying-guide/index.html": [
        "Told the parents are clear but shown no certificate, you have been told nothing you can check.",
        # the registry's own test kit, described as the migrated opening describes it: no dog of ours
        "L-2-HGA DNA test kit details from The Kennel Club help owners and breeders ensure dogs are free from genetic conditions that could affect long-term quality of life.",
    ],
    "uk-staffordshire-bull-terrier-guide/index.html": [
        "A breeder who says the parents are clear and cannot produce the paper has told you nothing at all.",
    ],
}

# A sentence the breeder ruled on word for word, by page, with the ruling that allows it. The
# breeder's chat ruling of 2026-10-05 (docs/reference/answer-board/answers/
# chat-2026-10-05-certificates-on-request.md) corrects q01 of 2026-09-29: the certificates and DNA
# results exist and are shared on request, kept off the website. So this one sentence, which says
# so and states no result, is excused by its exact text; the patterns are unchanged, so "results
# on request" or a sentence that adds a result anywhere else still fails. Its ledger row is
# data/quality/evidence-ledger.json `certificates-on-request`.
RULED = {
    "uk-locations/blue-staffy-puppies-london/index.html": [
        ("We share the parents' health certificates and DNA test results with you directly when "
         "you get in touch.",
         "docs/reference/answer-board/answers/chat-2026-10-05-certificates-on-request.md"),
    ],
}

ATTR = re.compile(r'\b(?:content|alt|aria-label|title)="([^"]*)"')


def visible(raw):
    """Text of a built file as a reader or a crawler meets it: tags gone, attributes that carry
    words kept (meta descriptions, alts), entities decoded, whitespace folded. Style sheets are
    dropped; JSON-LD is kept (it is text inside a script tag)."""
    raw = re.sub(r"<style[^>]*>.*?</style>", " ", raw, flags=re.S)
    attrs = " | ".join(ATTR.findall(raw))
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(text + " | " + attrs))


def result_lines(text):
    out = [text[max(0, m.start() - 70):m.end() + 40] for m in RESULT_RE.finditer(text)]
    for m in SENTENCE.finditer(text):
        sentence = DENIAL.sub(" ", m.group(0))
        if HEALTH_CONTEXT.search(sentence) and RESULT_WORD.search(sentence) and not RESULT_RE.search(sentence):
            out.append(m.group(0).strip()[:220])
    return out


def built_files():
    dist = ROOT / "dist"
    if not dist.exists():
        pytest.skip("run npm run -s build first")
    return dist, [p for p in dist.rglob("*") if p.suffix in (".html", ".txt", ".xml", ".json")
                  and "board-preview" not in p.parts]


def test_no_built_page_states_a_dna_or_health_test_result():
    dist, files = built_files()
    assert len(files) > 50, "examined too few built files to be a pass"
    bad = []
    for p in files:
        rel = str(p.relative_to(dist))
        if rel in MIGRATED_OPEN:
            continue
        text = visible(p.read_text(errors="ignore"))
        for sentence in GENERAL_ADVICE.get(rel, []):
            assert sentence in text, f"{rel}: the excused sentence is gone, drop it: {sentence}"
            text = text.replace(sentence, " ")
        for sentence, ruling in RULED.get(rel, []):
            assert (ROOT / ruling).is_file(), f"{rel}: the ruling {ruling} is not in the repository"
            assert sentence in text, f"{rel}: the ruled sentence is gone, drop it: {sentence}"
            text = text.replace(sentence, " ")
        bad += [f"{rel}: …{l}…" for l in result_lines(text)]
    assert bad == [], "\n".join(bad)


def test_the_migrated_pages_state_exactly_their_pinned_hits():
    """A named page is excused only for the hits pinned for it, by count and by text. A new hit
    fails; a page whose rebuild has landed fails too, until its name comes out of the pin."""
    dist, _ = built_files()
    pinned = json.loads(MIGRATED_PIN.read_text(encoding="utf-8"))
    for rel, want in pinned.items():
        f = dist / rel
        assert f.exists(), rel
        got = result_lines(visible(f.read_text(errors="ignore")))
        assert got, f"{rel} is clean: drop it from {MIGRATED_PIN.name}"
        assert len(got) == len(want) and sorted(got) == sorted(want), (rel, len(got), len(want))


def test_the_pin_catches_a_new_hit_on_a_migrated_page():
    dist, _ = built_files()
    rel = "uk-locations/staffy-breeding-dogs-glasgow/index.html"
    want = json.loads(MIGRATED_PIN.read_text(encoding="utf-8"))[rel]
    text = visible((dist / rel).read_text(errors="ignore")) + " Jones came back clear on every test."
    assert len(result_lines(text)) == len(want) + 1


def test_no_faq_row_states_a_result():
    rows = json.loads((ROOT / "data/faq.json").read_text(encoding="utf-8"))
    bad = [(r["id"], l) for r in rows for l in result_lines(r["q"] + " " + r["a"])]
    assert bad == [], bad


def test_the_patterns_fire_on_the_old_lines_and_spare_the_test_names():
    for old in ["Both parents are DNA tested clear of L-2-HGA and HC-HSF4.",
                "are extensively DNA tested and certified clear for key hereditary conditions",
                "Maggie and Jones carry clear DNA results for L-2-HGA and HC-HSF4",
                "your KC registered Staffy puppies will not be genetically affected",
                "Dam and sire clear of L-2-HGA and HC-HSF4, results on request.",
                "Both are screened and certified clear of L-2-HGA",
                "Which genetic tests are the parents cleared for?",
                "including clearances for common Staffy conditions (HC, L2HGA)",
                "Responsible breeders of blue Staffies L-2-HGA clear.",
                "L-2-HGA (Hereditary L-2-Hydroxyglutaric Aciduria): CLEAR",
                "and a clear pair cannot hand either one down",
                "Both ours are recorded clear of both.",
                "we send the certificates on request",
                "The first the table above records both parents clear of.",
                "Ask us to send the two certificates before you travel.",
                "Clear both parents, L-2-HGA",
                "A ‘clear’ result means your puppy will not develop it.",
                "Each claim above names a document: a registration, two DNA results, a vaccination card",
                "Four documents stand behind that: both parents' DNA screening results",
                "Both live here and both are on the health page with their results beside their names.",
                "Ask us for the certificates whenever you would like to see them.",
                "Our health page sets out every test we run and what the results were",
                # review C3 (2026-09-29): each escaped the first version of this harness
                "As KC-registered blue Staffy breeders with clear health tests, we encourage you",
                "clear health tests", "showing the screening results", "Both parents tested negative",
                "Maggie passed her L-2-HGA test", "Both parents passed their DNA tests",
                "healthy results on both parents", "certificate on request",
                "Jones has a clear L-2-HGA result", "came back clear", "ask to see a clear certificate",
                "Ask to see the certificate for each test before you pay a deposit.",
                "A good breeder offers the results before you ask, lets you meet the mother",
                # review minor 1 (2026-09-29)
                "L-2-HGA: normal", "HC-HSF4 normal on both parents", "The registry lists her as clear",
                "The Kennel Club database lists him as clear for HC-HSF4", "Maggie scored well on her eye screening"]:
        assert result_lines(old), old
    for named in ["Maggie and Jones are DNA tested for L-2-HGA and HC-HSF4, and both have their eyes and elbows screened.",
                  "it is not a test result and not a grade",
                  "We quote no score or grade.",
                  "A puppy needs two copies of the gene to be affected.",
                  "Neither condition shows in a puppy unless both parents pass the gene on, which is why both are tested.",
                  # review C3: false positives the first version fired on
                  "We hold no DNA certificates, so we name the tests and quote no result.",
                  "Keep both clear of the road", "Make the rules clear for both",
                  "Ask whether the dam is clear", "We will show you the vaccination certificates",
                  "Bright, clear eyes, no discharge or redness.",
                  # review minor 1: "one pass" and a gate that "passes" are not results
                  "so a family can see, in one pass, what was tested",
                  "it passes facts-preserved and link parity", "a normal day with a Staffy"]:
        assert result_lines(named) == [], named


def test_the_ledger_row_records_that_no_certificate_is_held():
    """The evidence ledger's schema (tests/py/test_rules_index.py) allows a proof that is a site
    path or the literal NOT FETCHED, and a NOT FETCHED row has no `confirmed` date. "No proof;
    the breeder confirms none is held" is therefore NOT FETCHED with `confirmed` null, and the
    row's `barrier` says why, so nobody goes looking for a certificate that does not exist."""
    ledger = json.loads((ROOT / "data/quality/evidence-ledger.json").read_text(encoding="utf-8"))
    row = next(c for c in ledger["claims"] if c["id"] == "parents-dna-clear")
    assert row["proof"] == "NOT FETCHED" and row["confirmed"] is None, row
    assert "answer board q01" in row["barrier"] and "no DNA certificates" in row["barrier"], row


def test_the_review_m6_lines_are_reworded():
    """Review M6: a verbatim claim that only follows from a result ("actively preventing …"), an
    unproven one ("free from any other underlying health issues"), a heading that implies the
    puppies were tested ("…L-2-HGA Tested Staffies?"), and a missing comma."""
    dist, _ = built_files()
    health = visible((dist / "blue-staffy-health-uk/index.html").read_text(errors="ignore"))
    why_us = visible((dist / "buy-staffy-puppies-for-sale-uk/index.html").read_text(errors="ignore"))
    assert "actively preventing" not in health
    assert "free from any other underlying health issues" not in health
    assert "L-2-HGA Tested Staffies?" not in why_us and "From L-2-HGA Tested Parents?" in why_us
    assert "Write to us and ask for the health paperwork , and the registration papers" in health


# ── the board records' plan text (review follow-up, 2026-09-29) ──────────────────────────────
# A record is the plan a rebuild follows. Plan text that asks for "what the result was", a table
# "a buyer can hold against a certificate" or "DNA tested clear" would steer the next rebuild back
# to stating results. Every rebuilt record's plan fields are held to the page's rule; the
# history (`verbatim`, `dropped`) and the competitor fetches (`meta.sources`) are not plan text.
REBUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))
# One plan line is a list of things the page must NOT restate, and names a clearance only as one.
PLAN_EXCUSED = {("blue-staffy-pup-sale-uk", "/brief/done"):
                "lists 'the DM clearance' among what the page may not restate (out of scope)",
                ("buy-blue-staffy-puppies-uk", "/sections/10/options/note"):
                "names the FAQ row id `listing-health-clearances`, an identifier; its question and answer are reworded",
                ("blue-staffy-puppies-london", "/sections/11/options/note"):
                "names the evidence-ledger row id `parents-dna-clear`, an identifier, to say no certificate is held",
                ("blue-staffy-puppies-london", "/sections/12/options/note"):
                "quotes a seller's 'DNA clear' line with no certificate as the buyer warning the H5 carries"}


def _strings(o, p):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from _strings(v, f"{p}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _strings(v, f"{p}/{i}")
    elif isinstance(o, str):
        yield p, o


def plan_text(rec):
    brief = rec.get("brief") or {}
    for k in ("goal", "done", "angles"):
        if k in brief:
            yield from _strings(brief[k], f"/brief/{k}")
    yield from _strings(((brief.get("cta") or {}).get("anchors")) or [], "/brief/cta/anchors")

    def tree(nodes, p):
        for j, n in enumerate(nodes or []):
            if isinstance(n, dict):
                if isinstance(n.get("intent"), str):
                    yield f"{p}/{j}/intent", n["intent"]
                yield from tree(n.get("children"), f"{p}/{j}/children")

    for i, sec in enumerate(rec.get("sections", [])):
        at = f"/sections/{i}"
        for k in ("intent", "why"):
            if isinstance(sec.get(k), str):
                yield f"{at}/{k}", sec[k]
        yield from tree(sec.get("tree"), at + "/tree")
        for kind in ("internal", "external"):
            for j, link in enumerate(((sec.get("links") or {}).get(kind)) or []):
                for k in ("anchor", "why"):
                    if isinstance(link, dict) and isinstance(link.get(k), str):
                        yield f"{at}/links/{kind}/{j}/{k}", link[k]
        note = (sec.get("options") or {}).get("note")
        if isinstance(note, str):
            yield f"{at}/options/note", note
        for k in ("questions", "keywords"):
            if k in sec:
                yield from _strings(sec[k], f"{at}/{k}")


def test_rebuilt_board_records_plan_no_result():
    bad, examined = [], 0
    for slug in REBUILT:
        rec = json.loads((ROOT / f"data/boards/{slug}.json").read_text(encoding="utf-8"))
        for where, text in plan_text(rec):
            examined += 1
            if (slug, where) in PLAN_EXCUSED:
                continue
            for hit in result_lines(text):
                bad.append(f"{slug} {where}: …{hit[:120]}…")
    assert examined > 500, f"examined only {examined} plan strings"
    assert bad == [], "\n".join(bad)


def test_a_coordinated_denial_is_not_a_result_and_an_offer_still_is():
    """Known-broken case from London's board record (2026-10-03): the second half of a
    coordinated denial was read as a certificate on offer."""
    assert result_lines("Tests named, never a result or a DNA certificate (plan Ruling 4).") == []
    assert result_lines("Tests named, and a DNA certificate is on file for both parents.")
    assert result_lines("Never a result, but the DNA certificate is yours on request.")


def test_the_plan_excusal_is_still_needed():
    for (slug, where), why in PLAN_EXCUSED.items():
        rec = json.loads((ROOT / f"data/boards/{slug}.json").read_text(encoding="utf-8"))
        text = dict(plan_text(rec))[where]
        assert result_lines(text), f"{slug} {where} is clean: drop it ({why})"


def test_the_follow_up_minor_lines():
    """Review follow-up minors 3-5 (2026-09-29): only documents are "checkable"; no orphaned
    reference to health certificates; the buying guide's H6 is about papers we do hand over; the
    health guarantee line opens "Our guarantee covers"; a sentence that mentions the video call
    says it is offered before the deposit."""
    dist, _ = built_files()
    page = lambda rel: visible((dist / rel).read_text(errors="ignore"))
    why_us, guide, health = (page("buy-staffy-puppies-for-sale-uk/index.html"),
                             page("uk-blue-staffy-puppy-buying-guide/index.html"),
                             page("blue-staffy-health-uk/index.html"))
    assert "names the document or the test it rests on, which is what you can check" not in why_us
    assert "names the document you can check before you travel" in why_us
    assert "Beyond health certificates" not in guide and "Beyond the health tests, what to look for" in guide
    assert "A Certificate Belongs to a Dog" not in guide
    assert "Our guarantee covers health issues and birth defects from the day your puppy comes home." in health
    for rel in ("index.html", "blue-staffy-pup-sale-uk/index.html", "buy-blue-staffy-puppies-uk/index.html"):
        text = page(rel)
        calls = [m.start() for m in re.finditer(r"(?i)video call", text)]
        assert calls, rel
        for i in calls:
            assert "before the deposit" in text[max(0, i - 80):i + 80], (rel, text[max(0, i - 80):i + 80])


def test_the_ruled_sentence_is_excused_by_its_text_only():
    """The excuse is the exact sentence: the same words with a result added, or "results on
    request", still fail."""
    (sentence, _), = RULED["uk-locations/blue-staffy-puppies-london/index.html"]
    assert result_lines(sentence), "without the excuse the patterns still catch it"
    for worse in (sentence.replace("DNA test results", "clear DNA test results"),
                  "We share the parents' DNA results on request.",
                  sentence.replace("health certificates", "clear certificates")):
        assert worse != sentence and result_lines(worse), worse
