"""What the two-year health guarantee covers (answer board q02, 2026-09-29).

The breeder wrote "Against any heaalth issues and birth defects within two years of
ownershipping". The page wording, spelling corrected, is "covers health issues and birth defects
for two years from the day your puppy comes home" ("within two years of ownership" read as
starting when the owner takes the puppy). It is data: data/settings.json `guarantee_cover`, a
field of its own beside `guarantee_label`. The label stays a length and nothing else
(src/lib/guarantee.ts `checkGuaranteeLabel` still refuses a label that names a cover); the cover
has its own check, `checkGuaranteeCover`, which both src/lib/site.ts `guaranteeCover()` and
src/lib/cityKit.ts `guaranteeRow()` run, so a cover that disagrees with `guarantee_days` stops the
build. Pages add it only where a guarantee sentence already carries it: the home FAQ answer
(`home-health-guarantee`, through the `{guarantee_cover}` token) and the city components'
guarantee row.
"""
import html
import json
import pathlib
import re
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
WORDING = "covers health issues and birth defects for two years from the day your puppy comes home"
# The cover without its length, for a sentence whose heading or label already states the length
# (review M1: "two-year health guarantee, which covers … for two years" said it twice).
BARE = "covers health issues and birth defects from the day your puppy comes home"


def test_the_cover_is_its_own_field_worded_as_ruled():
    assert SETTINGS["guarantee_cover"] == WORDING
    assert "q02" in SETTINGS["guarantee_cover_source"] and "2026-09-29" in SETTINGS["guarantee_cover_source"]
    # The label is untouched: it still names a length and no cover.
    assert SETTINGS["guarantee_label"] == "Two-year health guarantee"


def _bundle(tmp_path, src):
    esbuild, node = ROOT / "node_modules/.bin/esbuild", shutil.which("node")
    if not esbuild.exists() or not node:
        pytest.skip("needs node and node_modules/.bin/esbuild (npm install)")
    out = tmp_path / (pathlib.Path(src).stem + ".mjs")
    subprocess.run([str(esbuild), str(ROOT / src), "--bundle", "--format=esm", "--platform=node",
                    "--define:import.meta.env={}", f"--outfile={out}", "--log-level=error"], check=True)
    return node, out


def test_the_cover_check_refuses_what_the_breeder_did_not_say(tmp_path):
    node, out = _bundle(tmp_path, "src/lib/guarantee.ts")
    cases = [[730, WORDING],
             [365, WORDING],                                               # length disagrees
             [730, "health issues and birth defects for two years"],       # not "covers …"
             [730, "covers health issues and birth defects"],              # no length
             [730, WORDING + "."],                                         # a sentence, not a clause
             [730, "covers everything for 24 months"],                     # length typed another way
             [730, ""],
             [365, "covers health issues for one year from the day your puppy comes home"]]
    driver = (f"const m = await import({json.dumps(out.as_uri())});"
              "const r = [];"
              f"for (const [d, c] of {json.dumps(cases)}) {{ try {{ m.checkGuaranteeCover(d, c); r.push('ok'); }} catch (e) {{ r.push('refused'); }} }}"
              "console.log(JSON.stringify(r));")
    res = subprocess.run([node, "--input-type=module", "-e", driver], check=True, capture_output=True, text=True)
    assert json.loads(res.stdout) == ["ok", "refused", "refused", "refused", "refused", "refused", "refused", "ok"]


def test_the_readers_run_the_check():
    site = (ROOT / "src/lib/site.ts").read_text(encoding="utf-8")
    kit = (ROOT / "src/lib/cityKit.ts").read_text(encoding="utf-8")
    faq = (ROOT / "src/lib/faq.ts").read_text(encoding="utf-8")
    assert "export function guaranteeCoverSentence" in site and "export function guaranteePhrase" in site
    assert "guaranteeRowParts(G)" in kit
    assert "guarantee_phrase: guaranteePhrase()" in faq


def test_the_home_faq_answer_carries_the_cover_from_the_token():
    row = next(r for r in json.loads((ROOT / "data/faq.json").read_text(encoding="utf-8"))
               if r["id"] == "home-health-guarantee")
    assert "{guarantee_phrase}" in row["a"] and "{guarantee_cover}" not in row["a"]
    assert "birth defects" not in row["a"], "the cover is read from data, never typed into the row"


def _built(rel):
    f = ROOT / "dist" / rel
    if not f.exists():
        pytest.skip("run npm run -s build first")
    return re.sub(r"\s+", " ", html.unescape(f.read_text(encoding="utf-8")))


def test_the_built_home_page_states_the_cover_in_the_faq_and_its_schema():
    page = _built("index.html")
    sentence = f"our written health guarantee, which {WORDING}, alongside"
    assert page.count(sentence) == 2, "the visible FAQ answer and the FAQPage JSON-LD, once each"
    assert "two-year health guarantee, which covers" not in page, "M1: the length is said once"


def test_the_city_guarantee_row_states_the_cover():
    page = _built("uk-locations/blue-staffy-puppies-london/index.html")
    assert f"It {BARE}." in page and f"It {WORDING}." not in page


# Review I7: every section headed with the guarantee states its cover, read from data.
HEADED = {
    "index.html": "Our Two-Year Health Guarantee",
    "blue-staffy-pup-sale-uk/index.html": "Not an Item, a Promise: Our Two-Year Health Guarantee",
    "buy-staffy-puppies-for-sale-uk/index.html": "Our Two-Year Health Guarantee, in Writing",
    "blue-staffy-health-uk/index.html": "Ask Us About Our Two-Year Health Guarantee",
}


@pytest.mark.parametrize("rel", sorted(HEADED))
def test_each_section_headed_with_the_guarantee_states_its_cover(rel):
    page = _built(rel)
    heading = HEADED[rel]
    i = page.index(heading)
    assert f"It {BARE}." in page[i:i + 600], page[i:i + 600]


def test_a_missing_cover_omits_the_clause_everywhere(tmp_path):
    """Review M2: without `guarantee_cover`, every reader leaves the clause out (none throws):
    the FAQ phrase falls back to the label, the city row to its note, a section to nothing."""
    node, out = _bundle(tmp_path, "src/lib/guarantee.ts")
    base = {"guarantee_days": 730, "guarantee_label": "Two-year health guarantee",
            "guarantee_note": "Ask us for the full terms before you pay a deposit."}
    driver = (f"const m = await import({json.dumps(out.as_uri())});"
              f"const a = {json.dumps(base)}; const b = {{...a, guarantee_cover: {json.dumps(WORDING)}}};"
              "console.log(JSON.stringify([m.guaranteePhraseOf(a), m.guaranteePhraseOf(b),"
              " m.guaranteeRowParts(a), m.guaranteeRowParts(b), m.coverSentenceOf(a), m.coverSentenceOf(b)]));")
    res = subprocess.run([node, "--input-type=module", "-e", driver], check=True, capture_output=True, text=True)
    pa, pb, ra, rb, sa, sb = json.loads(res.stdout)
    assert pa == "two-year health guarantee"
    assert pb == f"health guarantee, which {WORDING},"
    assert ra == {"t": "Two-year health guarantee", "d": base["guarantee_note"]}
    assert rb == {"t": "Two-year health guarantee", "d": f"It {BARE}. " + base["guarantee_note"]}
    assert sa == "" and sb == f"It {BARE}."


def test_no_other_built_page_types_a_cover_of_its_own():
    """The cover appears only where the two readers put it; no page grows a new sentence."""
    dist = ROOT / "dist"
    if not dist.exists():
        pytest.skip("run npm run -s build first")
    carriers = sorted(str(p.relative_to(dist)) for p in dist.rglob("*.html")
                      if "birth defects" in p.read_text(errors="ignore") and "board-preview" not in p.parts)
    assert set(carriers) <= {"index.html", "uk-locations/blue-staffy-puppies-london/index.html",
                             "kit-preview/city/index.html", "kit-preview/city-page/index.html",
                             "kit-preview/index.html", *HEADED}, carriers
    assert "index.html" in carriers
