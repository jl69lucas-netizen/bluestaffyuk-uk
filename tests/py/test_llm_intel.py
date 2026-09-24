# tests/py/test_llm_intel.py — the LLM citation intel files bsuk-llm-keyword-intel writes
# (docs/research/llm-intel/<slug>-<YYYY-MM-DD>.json) keep the shape the strategy synthesizer
# and the page builders read: schemas/llm-intel.schema.json plus the rules a schema cannot
# say (BSUK cited only from its own domain, the citation gap and tier-5 risks follow from the
# mapped sites, "high" only for a missing buying-safety entity, no format from a summary).
# The agent runs it on its file before hand-off: python3 tests/py/test_llm_intel.py <file>...
import copy
import datetime
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import jsonschema
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schemas/llm-intel.schema.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "docs/research/llm-intel"
sys.path.insert(0, str(ROOT / "scripts"))
from competitor_registry_check import own_domains  # noqa: E402  the agent's script uses the same helper

OWN = own_domains(ROOT)


def _band(words):
    return "short" if words < 100 else "medium" if words <= 300 else "long"


def problems(doc, name=None, own=None):
    """Every way `doc` breaks the contract; [] when it keeps it. `own`: BSUK's domains (default: this repo's)."""
    own_set = OWN if own is None else own
    errs = sorted(jsonschema.Draft202012Validator(SCHEMA).iter_errors(doc), key=lambda e: list(e.path))
    if errs:
        return [f"schema: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in errs]
    out = []
    if name is not None and name != f"{doc['slug']}-{doc['date']}.json":
        out.append(f"file name {name} is not <slug>-<date>.json ({doc['slug']}-{doc['date']}.json)")
    ok = doc["fetched"]["status"] == "ok"
    sites = doc["citations"] + doc["local_businesses"]
    if ok:
        if doc["raw"] != f"data/queries/raw/{doc['slug']}/ai_engines.response.json":
            out.append("raw must be this slug's data/queries/raw/<slug>/ai_engines.response.json")
        if doc["answer_text"] is None or doc["bsuk_cited"] is None:
            out.append("a fetched answer needs answer_text and bsuk_cited")
    else:
        if doc["bsuk_cited"] is not None or doc["answer_text"] is not None or sites or doc["entities"]:
            out.append("NOT FETCHED: bsuk_cited and answer_text are null, no sites and no entities")
        if doc["format"]["status"] != "NOT FETCHED":
            out.append("NOT FETCHED: format is NOT FETCHED")
        if doc["paid_this_run"] and not doc["fetched"]["reason"].startswith("connector error"):
            out.append("NOT FETCHED: paid_this_run only for a connector error after the call was billed")
    own = any(s["domain"] in own_set for s in sites)
    if ok and doc["bsuk_cited"] != own:
        out.append(f"bsuk_cited is {doc['bsuk_cited']} but a BSUK domain is {'' if own else 'not '}among the sites")
    for s in sites:
        if (s["registry_id"] is None) != (s["tier"] is None):
            out.append(f"{s['domain']}: registry_id and tier are both set or both null")
        if s["domain"] in own_set and s["registry_id"] is not None:
            out.append(f"{s['domain']}: BSUK's own domain has no registry id")
        if s["platform"] and s["registry_id"] is not None:
            out.append(f"{s['domain']}: a hosting platform is never a registry entry")
    gap = sorted({s["registry_id"] for s in sites if s["tier"] in (1, 2, 3, 4)}) if ok and not own else []
    if sorted(doc["citation_gap"]) != gap:
        out.append(f"citation_gap must be {gap} (registry tiers 1-4 cited while BSUK is not)")
    risky = sorted({(s["domain"], s["registry_id"]) for s in sites if s["tier"] == 5})  # once per domain
    if sorted((r["domain"], r["registry_id"]) for r in doc["risks"]) != risky:
        out.append(f"risks must list each tier-5 site cited exactly once: {risky}")
    qs = doc["query_source"]
    if qs["from"] == "question-file" and qs["gap_matrix"] is not None:
        out.append("query_source: a question file is used alone; the gap matrix only when there is none")
    if qs["gap_topics"] and qs["gap_matrix"] is None:
        out.append("query_source: gap_topics need the gap_matrix they came from")
    old = [] if not ok else [doc["fetched"]["fetched_on"]]
    old += [qs["gap_matrix"][-13:-3]] if qs["gap_matrix"] else []
    days = {}
    for d in [doc["date"]] + old:
        try:
            days[d] = datetime.date.fromisoformat(d)
        except ValueError:
            out.append(f"impossible date {d}")
    if all(d in days for d in [doc["date"]] + old) and \
            any((days[doc["date"]] - days[d]).days > 30 for d in old) and not doc["stale"]:
        out.append("stale: the answer or the gap matrix is older than 30 days, so stale must say so")
    seen = set()
    for e in doc["entities"]:
        if e["entity"] in seen:
            out.append(f"entity {e['entity']!r} twice")
        seen.add(e["entity"])
        want = "high" if e["kind"] == "safety" and not e["on_page"] else "medium"
        if e["band"] != want:
            out.append(f"entity {e['entity']!r}: band must be {want}")
    f = doc["format"]
    if f["status"] == "ok":
        if doc["answer_text"] != "verbatim":
            out.append("format is only read from a verbatim answer; a summary gives NOT FETCHED")
        elif f["length"] != _band(f["words"]):
            out.append(f"format length {f['length']} does not match {f['words']} words")
    ps = doc["page_source"]
    if ps["kind"] != "dist" and not ps["provisional"]:
        out.append("entities checked against anything but the built, indexable page are provisional")
    return out


def main(argv=None):
    """Check the named files: exit 0 clean, 1 with problems (each printed), 2 on usage."""
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python3 tests/py/test_llm_intel.py <llm-intel json>...")
        return 2
    bad = 0
    for a in args:
        p = pathlib.Path(a)
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"{a}: unreadable: {exc}")
            return 2
        for msg in problems(doc, p.name):
            print(f"{a}: {msg}")
            bad += 1
    print(f"llm-intel: {len(args)} file(s); {bad} problem(s)")
    return 1 if bad else 0


GOOD = {
    "slug": "blue-staffy-puppies-manchester-uk", "date": "2026-09-23", "engine": "chatgpt",
    "endpoint": "ai_optimization_chat_gpt_scraper", "location": "United Kingdom",
    "query": "Where can I buy a blue Staffy puppy near Manchester, and what should I ask the breeder?",
    "query_source": {"from": "city", "gap_matrix": None, "gap_topics": []}, "stale": [],
    "fetched": {"status": "ok", "fetched_on": "2026-09-23"},
    "raw": "data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.response.json",
    "answer_text": "verbatim", "paid_this_run": False, "bsuk_cited": False,
    "citations": [{"domain": "pets4homes.co.uk", "registry_id": "pets4homes", "tier": 2, "platform": False},
                  {"domain": "thekennelclub.org.uk", "registry_id": None, "tier": None, "platform": False}],
    "local_businesses": [{"domain": "cheap-pups-example.com", "registry_id": "cheap-pups-example", "tier": 5,
                          "platform": False}],
    "citation_gap": ["pets4homes"],
    "risks": [{"domain": "cheap-pups-example.com", "registry_id": "cheap-pups-example",
               "reason": "tier 5 in the registry"}],
    "page_source": {"kind": "question-file", "path": "data/queries/blue-staffy-puppies-manchester-uk.json",
                    "provisional": True, "note": "the built page is a noindex stub"},
    "entities": [{"entity": "health tests", "kind": "safety", "on_page": False, "band": "high"},
                 {"entity": "pets4homes", "kind": "other", "on_page": False, "band": "medium"}],
    "format": {"status": "ok", "list": "numbered", "length": "short", "words": 58, "opening": "recommendation"},
    "llm_mentions": {"status": "NOT FETCHED", "reason": "no BSUK domain live until project 6"},
}


def _bad(edit):
    doc = copy.deepcopy(GOOD)
    edit(doc)
    return doc


def test_a_good_file_passes():
    assert problems(GOOD, "blue-staffy-puppies-manchester-uk-2026-09-23.json") == []


def test_a_not_fetched_file_passes():
    doc = _bad(lambda d: d.update(fetched={"status": "NOT FETCHED", "reason": "connector unavailable"},
                                  raw=None, answer_text=None, bsuk_cited=None, citations=[],
                                  local_businesses=[], citation_gap=[], risks=[], entities=[],
                                  format={"status": "NOT FETCHED", "reason": "no answer"}))
    assert problems(doc) == []


@pytest.mark.parametrize("edit,needle", [
    (lambda d: d.update(engine="perplexity"), "schema: engine"),
    (lambda d: d.update(location="United States"), "schema: location"),
    (lambda d: d.pop("llm_mentions"), "schema"),
    (lambda d: d.update(bsuk_cited=True), "bsuk_cited"),
    (lambda d: d["citations"].append({"domain": "bluestaffyuk.uk", "registry_id": None, "tier": None, "platform": False}), "bsuk_cited"),
    (lambda d: d["citations"].append({"domain": "blogspot.com", "registry_id": "blogspot", "tier": 1, "platform": True}), "hosting platform"),
    (lambda d: d["fetched"].update(fetched_on="2026-02-30"), "impossible date"),
    (lambda d: d.update(date="2026-13-01"), "impossible date"),
    (lambda d: d.update(citation_gap=[]), "citation_gap"),
    (lambda d: d.update(risks=[]), "risks"),
    (lambda d: d["risks"].append(dict(d["risks"][0])), "exactly once"),
    (lambda d: d["query_source"].update(gap_topics=["staffy price uk"]), "gap_topics need"),
    (lambda d: d["query_source"].update({"from": "question-file", "gap_matrix": "docs/research/gap-matrix-2026-09-01.md"}), "used alone"),
    (lambda d: d["fetched"].update(fetched_on="2026-07-01"), "stale must say so"),
    (lambda d: d["query_source"].update(gap_matrix="docs/research/gap-matrix-2026-08-01.md"), "stale must say so"),
    (lambda d: d["citations"][1].update(registry_id="thekennelclub"), "both set or both null"),
    (lambda d: d["entities"][0].update(on_page=True), "band must be medium"),
    (lambda d: d["entities"][1].update(band="high"), "band must be medium"),
    (lambda d: d.update(answer_text="summary"), "summary gives NOT FETCHED"),
    (lambda d: d["format"].update(words=150), "does not match"),
    (lambda d: d["page_source"].update(provisional=False), "provisional"),
    (lambda d: d.update(raw="data/queries/raw/other-slug/ai_engines.response.json"), "raw must be"),
    (lambda d: d["citations"][0].update(domain="https://www.pets4homes.co.uk/"), "schema: citations"),
    (lambda d: d["entities"].append(dict(d["entities"][0])), "twice"),
])
def test_a_broken_file_fails(edit, needle):
    assert any(needle in p for p in problems(_bad(edit))), problems(_bad(edit))


def test_a_tier5_site_both_cited_and_listed_is_one_risk():
    def both(d):
        d["citations"].append(dict(d["local_businesses"][0]))
    assert problems(_bad(both)) == []
    def twice(d):
        both(d)
        d["risks"].append(dict(d["risks"][0]))
    assert any("exactly once" in p for p in problems(_bad(twice)))


def test_a_stale_answer_passes_when_it_says_so():
    doc = _bad(lambda d: d.update(fetched={"status": "ok", "fetched_on": "2026-07-01"},
                                  stale=["answer fetched 2026-07-01, 84 days old"]))
    assert problems(doc) == []


def _agent_script():
    text = (ROOT / ".claude/agents/bsuk-llm-keyword-intel.md").read_text(encoding="utf-8")
    return re.search(r"<<'EOF'; rc=.*?\n(.*?)\nEOF\n", text, re.S).group(1)


def test_the_agent_script_uses_the_page_map_and_gap_matrix_without_a_question_file(tmp_path):
    (tmp_path / "scripts").mkdir()
    shutil.copy(ROOT / "scripts/competitor_registry_check.py", tmp_path / "scripts")
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text("[]", encoding="utf-8")
    (tmp_path / "data/page-map.json").write_text(json.dumps({"pages": [
        {"url": "/staffy-price-guide/", "title": "Staffy Price Guide", "h1": "Staffy Price Guide",
         "headings": [["h2", "How much is a Staffy?"], ["h2", "Why health tested litters cost more"]]}]}), encoding="utf-8")
    (tmp_path / "data/competitors.json").write_text(json.dumps({"competitors": [
        {"id": "cheap-pups", "root_domain": "cheap-pups.com", "tier": 5}]}), encoding="utf-8")
    shutil.copy(ROOT / "data/settings.json", tmp_path / "data")  # BSUK's domains: the script stops without one
    (tmp_path / "docs/research").mkdir(parents=True)
    (tmp_path / "docs/research/gap-matrix-2026-07-01.md").write_text("| staffy puppy price uk | 3 |\n", encoding="utf-8")
    (tmp_path / "docs/research/gap-matrix-2026-08-01.md").write_text("| staffy puppy price uk | 4 |\n", encoding="utf-8")
    resp = tmp_path / "resp.json"
    resp.write_text(json.dumps({"tasks": [{"result": [{"keyword": "How much is a Staffy puppy in the UK?",
        "markdown": "A Staffy puppy costs more from a health tested litter. Avoid cheap sellers.",
        "sources": [{"url": "https://cheap-pups.com/a"}],
        "items": [{"type": "chat_gpt_local_businesses", "items": [
            {"type": "chat_gpt_local_business_element", "domain": "www.cheap-pups.com"},
            {"type": "chat_gpt_local_business_element", "domain": "www.instagram.com"}]}]}]}]}), encoding="utf-8")
    env = dict(os.environ, QUERY="How much is a Staffy puppy in the UK?", TODAY="2026-09-23", FETCHED_ON="2026-09-23",
               GAP_TOPICS="staffy puppy price uk", EXTRA="")
    run = subprocess.run([sys.executable, "-", "staffy-price-guide", str(resp)], input=_agent_script(), cwd=tmp_path,
                         env=env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    doc = json.loads(run.stdout)
    assert doc["query_source"] == {"from": "page-map", "gap_matrix": "docs/research/gap-matrix-2026-08-01.md",
                                   "gap_topics": ["staffy puppy price uk"]}
    assert doc["stale"] == ["docs/research/gap-matrix-2026-08-01.md is 53 days old"]
    assert run.stderr.startswith("STALE")
    assert doc["page_source"]["kind"] == "page-map" and doc["page_source"]["provisional"]
    assert {"entity": "health tests", "kind": "safety", "on_page": True, "band": "medium"} in doc["entities"]  # from an H2 pair
    assert [s["domain"] for s in doc["local_businesses"]] == ["cheap-pups.com"]  # instagram is a profile link
    assert doc["risks"] == [{"domain": "cheap-pups.com", "registry_id": "cheap-pups",
                             "reason": doc["risks"][0]["reason"]}]
    assert problems(doc, "staffy-price-guide-2026-09-23.json") == []
    env["GAP_TOPICS"] = "staffy training"
    run = subprocess.run([sys.executable, "-", "staffy-price-guide", str(resp)], input=_agent_script(), cwd=tmp_path,
                         env=env, capture_output=True, text=True)
    assert run.returncode != 0 and "GAP_TOPICS not in" in run.stderr


def test_the_agent_script_reads_the_real_page_map_entry_with_no_build(tmp_path):
    # data/page-map.json headings are [tag, text] pairs; a page with no question file and no dist/
    # build falls back to its entry. Run against a copy of the real entry for the buying guide.
    slug = "uk-blue-staffy-puppy-buying-guide"
    entry = next(p for p in json.loads((ROOT / "data/page-map.json").read_text(encoding="utf-8"))["pages"]
                 if p["url"] == f"/{slug}/")
    assert entry["headings"] and all(isinstance(h, list) for h in entry["headings"])
    (tmp_path / "scripts").mkdir()
    shutil.copy(ROOT / "scripts/competitor_registry_check.py", tmp_path / "scripts")
    (tmp_path / "data").mkdir()
    shutil.copy(ROOT / "data/locations.json", tmp_path / "data")
    (tmp_path / "data/page-map.json").write_text(json.dumps({"pages": [entry]}), encoding="utf-8")
    query = "How do I buy a blue Staffy puppy in the UK?"
    shutil.copy(ROOT / "data/settings.json", tmp_path / "data")  # BSUK's domains: the script stops without one
    resp = tmp_path / "resp.json"
    resp.write_text(json.dumps({"tasks": [{"result": [{"keyword": query,
        "markdown": "Choose a breeder who shows the puppy with its mother and shares health test results.",
        "sources": [{"url": "https://www.thekennelclub.org.uk/"}]}]}]}), encoding="utf-8")
    env = dict(os.environ, QUERY=query, TODAY="2026-09-23", FETCHED_ON="2026-09-23", EXTRA="", GAP_TOPICS="")
    run = subprocess.run([sys.executable, "-", slug, str(resp)], input=_agent_script(), cwd=tmp_path,
                         env=env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    doc = json.loads(run.stdout)
    assert doc["page_source"]["kind"] == "page-map" and doc["page_source"]["provisional"]
    assert "no built page in dist/" in doc["page_source"]["note"]
    assert doc["query_source"]["from"] == "page-map"
    assert problems(doc, f"{slug}-2026-09-23.json") == []


# --- the agent's script, run end to end on saved responses ------------------------------------
MAN = "blue-staffy-puppies-manchester-uk"
MAN_Q = "Where can I buy a blue Staffy puppy near Manchester, and what should I ask the breeder?"
FIX = ROOT / "tests/py/fixtures/competitors"
REGISTRY = {"competitors": [{"id": "pets4homes", "root_domain": "pets4homes.co.uk", "tier": 2},
                            {"id": "cheap-pups", "root_domain": "cheap-pups.com", "tier": 5},
                            {"id": "ukstaffypups", "root_domain": "ukstaffypups.uk", "tier": 4},
                            {"id": "kc", "root_domain": "thekennelclub.org.uk", "tier": 1}]}


def _root(tmp, registry=None, saved_on="2026-09-23", dist=None, qfile=True):
    """A scratch repo root the script can run in: the real locations, page map, settings and
    Manchester question file; a registry, the normalised ai_engines.json date and a dist page
    when asked."""
    (tmp / "scripts").mkdir(exist_ok=True)
    shutil.copy(ROOT / "scripts/competitor_registry_check.py", tmp / "scripts")
    (tmp / "data/queries/raw" / MAN).mkdir(parents=True, exist_ok=True)
    for f in ("locations.json", "page-map.json", "settings.json"):
        shutil.copy(ROOT / "data" / f, tmp / "data")
    if qfile:
        shutil.copy(ROOT / f"data/queries/{MAN}.json", tmp / "data/queries")
    if registry:
        (tmp / "data/competitors.json").write_text(json.dumps(registry), encoding="utf-8")
    if saved_on:
        (tmp / f"data/queries/raw/{MAN}/ai_engines.json").write_text(
            json.dumps({"source": "ai_engines", "status": "ok", "fetched": saved_on, "questions": []}), encoding="utf-8")
    if dist is not None:
        page = tmp / f"dist/uk-locations/{MAN}/index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(dist, encoding="utf-8")
    return tmp


def _run(root, resp=None, slug=MAN, **env):
    """(exit code, output doc or None, stderr) for the script run in `root` on `resp`."""
    args = [sys.executable, "-", slug]
    if resp is not None:
        path = root / "resp.json"
        path.write_text(json.dumps(resp) if not isinstance(resp, pathlib.Path) else resp.read_text(encoding="utf-8"),
                        encoding="utf-8")
        args.append(str(path))
    e = {k: v for k, v in os.environ.items() if k not in ("PAID", "FETCHED_ON", "NOT_FETCHED", "GAP_TOPICS", "EXTRA")}
    e.update({"QUERY": MAN_Q, "TODAY": "2026-09-23"}, **env)
    run = subprocess.run(args, input=_agent_script(), cwd=root, env=e, capture_output=True, text=True)
    return run.returncode, (json.loads(run.stdout) if run.returncode == 0 else None), run.stderr


def _answer(markdown, keyword=MAN_Q, **extra):
    return {"status_code": 20000, "tasks": [{"status_code": 20000, "result": [dict(keyword=keyword, markdown=markdown, **extra)]}]}


def _site(domain, rid=None, tier=None, platform=False):
    return {"domain": domain, "registry_id": rid, "tier": tier, "platform": platform}


def _ent(name, kind, on):
    return {"entity": name, "kind": kind, "on_page": on, "band": "high" if kind == "safety" and not on else "medium"}


CASES = {
    "fixture": dict(
        resp=FIX / "chatgpt-manchester.json", registry=None, extra="pets4homes;kennel club;find a puppy",
        bsuk=False,
        citations=[_site("pets4homes.co.uk"), _site("thekennelclub.org.uk")], local=[],
        entities=[_ent("health tests", "safety", True), _ent("meet the mother", "safety", True),
                  _ent("microchip", "safety", False), _ent("pets4homes", "other", False),
                  _ent("kennel club", "other", True), _ent("find a puppy", "other", False)],
        format={"status": "ok", "list": "numbered", "length": "short", "words": 46, "opening": "recommendation"},
        gap=[], risks=[]),
    "synthetic full response": dict(
        resp=FIX / "chatgpt-synthetic-full.json", registry=REGISTRY,
        extra="kennel club;coefficient of inbreeding;pets4homes;rspca;written contract;coi|coefficient of inbreeding",
        bsuk=True,
        citations=[_site("pets4homes.co.uk", "pets4homes", 2), _site("thekennelclub.org.uk", "kc", 1),
                   _site("bluestaffyuk-scam.com"), _site("bluestaffyuk.uk"), _site("ukstaffypups.uk", "ukstaffypups", 4)],
        local=[_site("cheap-pups.com", "cheap-pups", 5), _site("pets-direct.co.uk"), _site("blogspot.com", platform=True)],
        entities=[_ent("health tests", "safety", True), _ent("l-2-hga", "safety", True),
                  _ent("meet the mother", "safety", True), _ent("licence", "safety", False),
                  _ent("contract", "safety", False), _ent("kennel club", "other", True),
                  _ent("coefficient of inbreeding", "other", False), _ent("pets4homes", "other", False)],
        format={"status": "ok", "list": "table", "length": "short", "words": None, "opening": "recommendation"},
        gap=[], risks=["cheap-pups.com"]),
}


@pytest.mark.parametrize("case", CASES, ids=list(CASES))
def test_the_agent_script_reads_a_saved_response_exactly(tmp_path, case):
    c = CASES[case]
    code, doc, err = _run(_root(tmp_path, registry=c["registry"]), c["resp"], EXTRA=c["extra"])
    assert code == 0, err
    assert doc["bsuk_cited"] is c["bsuk"]
    assert doc["citations"] == c["citations"]
    assert doc["local_businesses"] == c["local"]  # social profiles dropped; a blog host flagged as a platform
    assert doc["entities"] == c["entities"]
    fmt = dict(c["format"], words=c["format"]["words"] or doc["format"]["words"])
    assert doc["format"] == fmt
    assert doc["citation_gap"] == c["gap"]
    assert [r["domain"] for r in doc["risks"]] == c["risks"]
    assert doc["page_source"]["kind"] == "question-file" and "ai_" in doc["page_source"]["note"]
    assert problems(doc, f"{MAN}-2026-09-23.json") == []


def test_the_synthetic_answer_drops_extra_entities_it_cannot_hold(tmp_path):
    code, doc, err = _run(_root(tmp_path, registry=REGISTRY), FIX / "chatgpt-synthetic-full.json",
                          EXTRA="rspca;written contract;coi|coefficient of inbreeding;xl breed|xl")
    assert code == 0, err
    dropped = err.splitlines()[-1]
    for name in ("rspca", "written contract", "coi", "xl breed"):
        assert name in dropped
    assert all(e["kind"] == "safety" for e in doc["entities"])


def test_ai_sourced_questions_are_not_page_text(tmp_path):
    # the Manchester question file carries "Has the puppy been microchipped and vet checked?" only
    # because ChatGPT's answer suggested it: checking the answer against it would check it against itself
    code, doc, err = _run(_root(tmp_path), _answer("1. Check the puppy is microchipped.\n2. Ask for a vet check."))
    assert code == 0, err
    assert {e["entity"]: e["on_page"] for e in doc["entities"]} == {"microchip": False, "vet check": True}


def test_a_query_that_does_not_match_the_response_stops(tmp_path):
    code, _, err = _run(_root(tmp_path), _answer("Ask to meet the mother.", keyword="Another question?"))
    assert code != 0 and "not QUERY" in err


def test_a_city_page_takes_only_the_city_question(tmp_path):
    q = "Staffy puppies in Manchester?"
    code, _, err = _run(_root(tmp_path), _answer("Meet the mother.", keyword=q), QUERY=q)
    assert code != 0 and "city page" in err


def test_a_plural_on_the_page_matches_a_singular_in_the_answer(tmp_path):
    page = ('<html><head><meta name="robots" content="index, follow"></head><body>'
            "<main><p>Every puppy has had its flea treatments.</p></main></body></html>")
    code, doc, err = _run(_root(tmp_path, dist=page), _answer("Ask about flea treatment."), EXTRA="flea treatment")
    assert code == 0, err
    assert doc["entities"] == [_ent("flea treatment", "other", True)]


def test_a_saved_response_without_a_keyword_is_checked_against_its_note(tmp_path):
    resp = {"_saved_note": f"Request: keyword '{MAN_Q}'.", "answer_points": ["Meet the mother."]}
    assert _run(_root(tmp_path), resp)[0] == 0
    resp["_saved_note"] = "Request: another question."
    code, _, err = _run(_root(tmp_path), resp)
    assert code != 0 and "cannot be verified" in err


@pytest.mark.parametrize("robots,kind", [("noindex, follow", "question-file"), ("index, follow", "dist")])
def test_a_noindex_build_is_not_the_page(tmp_path, robots, kind):
    html_ = (f'<html><head><meta name="robots" content="{robots}"></head><body><nav>licence</nav>'
             '<main><h1>Blue Staffy Puppies Manchester</h1><p>We never sell without a written contract.</p></main></body></html>')
    code, doc, err = _run(_root(tmp_path, dist=html_), _answer("Ask for a contract and see the licence."))
    assert code == 0, err
    assert doc["page_source"]["kind"] == kind and doc["page_source"]["provisional"] is (kind != "dist")
    on = {e["entity"]: e["on_page"] for e in doc["entities"]}
    assert on == ({"licence": False, "contract": True} if kind == "dist" else {"licence": False, "contract": False})


@pytest.mark.parametrize("saved_on,stale", [("2026-08-23", True), ("2026-08-24", False)])
def test_an_answer_older_than_30_days_is_stale(tmp_path, saved_on, stale):
    code, doc, err = _run(_root(tmp_path, saved_on=saved_on), _answer("Meet the mother."))
    assert code == 0, err
    assert bool(doc["stale"]) is stale and err.startswith("STALE") is stale
    assert problems(doc) == []


def test_a_paid_run_dates_the_answer_by_the_call(tmp_path):
    code, doc, err = _run(_root(tmp_path, saved_on="2026-06-01"), _answer("Meet the mother."), PAID="1", FETCHED_ON="2026-09-23")
    assert code == 0, err
    assert doc["fetched"]["fetched_on"] == "2026-09-23" and doc["stale"] == [] and doc["paid_this_run"]
    code, _, err = _run(_root(tmp_path), _answer("Meet the mother."), PAID="1")
    assert code != 0 and "FETCHED_ON" in err


def test_no_date_for_the_answer_stops(tmp_path):
    code, _, err = _run(_root(tmp_path, saved_on=None), _answer("Meet the mother."))
    assert code != 0 and "FETCHED_ON" in err


@pytest.mark.parametrize("resp", [
    {"status_code": 40501, "tasks": [{"status_code": 40501, "status_message": "Invalid Field"}]},
    _answer(""),
])
def test_a_connector_error_exits_5(tmp_path, resp):
    code, _, err = _run(_root(tmp_path), resp)
    assert code == 5 and "connector error" in err


def test_the_not_fetched_output_comes_from_the_script(tmp_path):
    code, doc, err = _run(_root(tmp_path), None, NOT_FETCHED="spend declined")
    assert code == 0, err
    assert doc["fetched"] == {"status": "NOT FETCHED", "reason": "spend declined"}
    assert doc["format"]["status"] == "NOT FETCHED" and doc["citations"] == [] and not doc["paid_this_run"]
    assert problems(doc) == []
    code, doc, err = _run(_root(tmp_path), None, NOT_FETCHED="connector error: status 40501", PAID="1")
    assert code == 0 and doc["paid_this_run"] and problems(doc) == []


def test_bsuk_is_its_own_domain_only(tmp_path):
    code, doc, _ = _run(_root(tmp_path), _answer("See https://bluestaffyuk-scam.com/ and https://www.bluestaffyuk.uk.evil.com/"))
    assert code == 0 and doc["bsuk_cited"] is False
    code, doc, _ = _run(_root(tmp_path), _answer("See https://www.bluestaffyuk.uk/ for puppies."))
    assert code == 0 and doc["bsuk_cited"] is True


@pytest.mark.parametrize("markdown,want", [
    ("**Short answer:**\nUse a licensed breeder near you.", ("paragraphs", "recommendation")),
    ("---\nA blue Staffy is a Staffordshire Bull Terrier with a dilute coat.", ("paragraphs", "definition")),
    ("# Where to buy\n\nHere are the best places to look for a puppy.", ("paragraphs", "recommendation")),
    ("You can find breeders through the Kennel Club.", ("paragraphs", "recommendation")),
    ("Prices vary, e.g. by region, and 60 percent of buyers pay a deposit first.", ("paragraphs", "statistic")),
    ("| a | b |\n| c | d |", ("paragraphs", "statement")),
    ("| Question | Why |\n|---|---|\n| Health tests? | Disease |", ("table", "statement")),
    ("1. Visit the litter.\n   - see the mother\n   - see the father\n   - see the kennel\n2. Ask for tests.", ("numbered", "recommendation")),
    ("- Visit the litter.\n- Ask for tests.\n\n---\n", ("bulleted", "recommendation")),
    ("Is a blue Staffy right for you? It depends.", ("paragraphs", "question")),
])
def test_the_answer_format(tmp_path, markdown, want):
    code, doc, err = _run(_root(tmp_path), _answer(markdown))
    assert code == 0, err
    assert (doc["format"]["list"], doc["format"]["opening"]) == want


def test_gap_topics_must_be_a_matrix_row_and_the_matrix_is_named_only_with_them(tmp_path):
    root = _root(tmp_path, qfile=False)
    (root / "docs/research").mkdir(parents=True)
    (root / "docs/research/gap-matrix-2026-09-20.md").write_text(
        "| Value | Competitors |\n|---|---|\n| staffy puppy price uk | 3/5 |\n| blue staffy \\\\| health | 2/5 |\n", encoding="utf-8")
    q = "How much is a Staffy puppy in the UK?"
    resp = _answer("A Staffy puppy from a health tested litter costs more.", keyword=q)
    slug = "uk-blue-staffy-puppy-buying-guide"
    code, doc, err = _run(root, resp, slug=slug, QUERY=q, FETCHED_ON="2026-09-23")
    assert code == 0, err
    assert doc["query_source"] == {"from": "page-map", "gap_matrix": None, "gap_topics": []}
    code, doc, err = _run(root, resp, slug=slug, QUERY=q, FETCHED_ON="2026-09-23", GAP_TOPICS="staffy puppy price uk")
    assert code == 0, err
    assert doc["query_source"]["gap_matrix"] == "docs/research/gap-matrix-2026-09-20.md"
    code, _, err = _run(root, resp, slug=slug, QUERY=q, FETCHED_ON="2026-09-23", GAP_TOPICS="staffy puppy price")
    assert code != 0 and "GAP_TOPICS" in err  # part of a row is not a row


def test_a_file_named_for_another_slug_or_date_fails():
    assert any("file name" in p for p in problems(GOOD, "blue-staffy-puppies-leeds-uk-2026-09-23.json"))


def test_every_llm_intel_file_on_disk_keeps_the_contract():
    files = sorted(OUT_DIR.glob("*.json")) if OUT_DIR.is_dir() else []
    bad = [f"{f.name}: {p}" for f in files for p in problems(json.loads(f.read_text(encoding="utf-8")), f.name)]
    assert bad == []


def test_the_cli_checks_named_files(tmp_path, capsys):
    good = tmp_path / "blue-staffy-puppies-manchester-uk-2026-09-23.json"
    good.write_text(json.dumps(GOOD), encoding="utf-8")
    assert main([str(good)]) == 0
    broken = tmp_path / "blue-staffy-puppies-manchester-uk-2026-09-24.json"
    broken.write_text(json.dumps(GOOD), encoding="utf-8")
    assert main([str(broken)]) == 1
    assert "file name" in capsys.readouterr().out
    assert main([]) == 2
    assert main([str(tmp_path / "missing.json")]) == 2


if __name__ == "__main__":
    sys.exit(main())


def test_brand_entities_in_the_local_business_category_are_local_businesses(tmp_path):
    # the connector's current shape (the Leeds response): items[].brand_entities[] with
    # category "local_business" and a title, no domain. A name that is a registry entry's name
    # maps to that entry (and its domain); any other name is kept with domain null.
    reg = {"competitors": REGISTRY["competitors"] + [{"id": "stormnoir", "name": "StormNoir Staffordshire Bull Terriers",
                                                       "root_domain": "stormnoir.co.uk", "tier": 5}]}
    resp = _answer("Ask to see the mother and the health tests.", items=[{"type": "chat_gpt_text", "brand_entities": [
        {"type": "chat_gpt_brand_entity", "title": "English Blue Staffies For Rehoming", "category": "local_business"},
        {"type": "chat_gpt_brand_entity", "title": "stormnoir staffordshire bull terriers", "category": "local_business"},
        {"type": "chat_gpt_brand_entity", "title": "Pets4Homes", "category": "marketplace"},
        {"type": "chat_gpt_brand_entity", "title": "English Blue Staffies For Rehoming", "category": "local_business"}]}])
    code, doc, err = _run(_root(tmp_path, registry=reg), resp)
    assert code == 0, err
    assert doc["local_businesses"] == [
        {"name": "English Blue Staffies For Rehoming", "domain": None, "registry_id": None, "tier": None, "platform": False},
        {"name": "stormnoir staffordshire bull terriers", "domain": "stormnoir.co.uk", "registry_id": "stormnoir",
         "tier": 5, "platform": False}]
    assert [r["domain"] for r in doc["risks"]] == ["stormnoir.co.uk"]
    assert doc["bsuk_cited"] is False
    assert problems(doc, f"{MAN}-2026-09-23.json") == []


def test_the_script_and_this_contract_share_one_own_domain_rule(tmp_path):
    # Known Issue 53: one helper, scripts/competitor_registry_check.py own_domains(), in both places
    sys.path.insert(0, str(ROOT / "scripts"))
    from competitor_registry_check import own_domains as shared
    root = _root(tmp_path)
    (root / "data/settings.json").write_text(json.dumps(
        {"site_url": "https://www.shop.bluestaffyuk.co.uk/puppies/", "email": "hello@mail.bluestaffyuk.uk"}), encoding="utf-8")
    own = shared(root)
    assert own == {"site_url_placeholder", "bluestaffyuk.co.uk", "bluestaffyuk.uk"}
    code, doc, err = _run(root, _answer("See https://blog.bluestaffyuk.co.uk/ for puppies."))
    assert code == 0, err
    assert doc["bsuk_cited"] is True and doc["citations"][0]["domain"] == "bluestaffyuk.co.uk"
    assert problems(doc, f"{MAN}-2026-09-23.json", own=own) == []
    assert "def root(" not in _agent_script() and "own_domains" in _agent_script()


def test_the_paid_script_refuses_to_judge_bsuk_cited_without_a_bsuk_domain(tmp_path, monkeypatch):
    # settings.json with no email and no site-domain key: the lenient helper still gives the placeholder
    # set, but the agent's script (own_domains(strict=True)) exits non-zero and its OUT file is removed
    sys.path.insert(0, str(ROOT / "scripts"))
    from competitor_registry_check import own_domains as shared
    monkeypatch.delenv("SITE_URL", raising=False)
    root = _root(tmp_path)
    (root / "data/settings.json").write_text(json.dumps({"phone": "PHONE_PLACEHOLDER"}), encoding="utf-8")
    assert shared(root) == {"site_url_placeholder"}
    with pytest.raises(SystemExit, match="names no BSUK domain"):
        shared(root, strict=True)
    assert "OWN = own_domains(strict=True)" in _agent_script()
    (root / "resp.json").write_text(json.dumps(_answer("See https://www.thekennelclub.org.uk/.")), encoding="utf-8")
    out = root / "out.json"
    env = {k: v for k, v in os.environ.items() if k not in ("PAID", "FETCHED_ON", "NOT_FETCHED", "GAP_TOPICS", "EXTRA")}
    env.update(QUERY=MAN_Q, TODAY="2026-09-23", OUT=str(out))
    run = subprocess.run(  # the agent's own pattern: > "$OUT"; rc=$?; [ $rc -eq 0 ] || rm -f "$OUT"
        ["bash", "-c", 'python3 - "$@" > "$OUT"; rc=$?; [ $rc -eq 0 ] || rm -f "$OUT"; exit $rc', "_", MAN, "resp.json"],
        input=_agent_script(), cwd=root, env=env, capture_output=True, text=True)
    assert run.returncode != 0 and "refusing to judge bsuk_cited" in run.stderr
    assert not out.exists()


def test_a_real_site_url_counts_as_a_bsuk_domain(tmp_path, monkeypatch):
    # project 6 sets the live domain in SITE_URL; the build placeholder there adds nothing
    sys.path.insert(0, str(ROOT / "scripts"))
    from competitor_registry_check import own_domains as shared
    (tmp_path / "data").mkdir()
    (tmp_path / "data/settings.json").write_text(json.dumps({"phone": "PHONE_PLACEHOLDER"}), encoding="utf-8")
    monkeypatch.setenv("SITE_URL", "https://SITE_URL_PLACEHOLDER")
    assert shared(tmp_path) == {"site_url_placeholder"}
    with pytest.raises(SystemExit):
        shared(tmp_path, strict=True)
    monkeypatch.setenv("SITE_URL", "https://www.example.co.uk")
    assert shared(tmp_path, strict=True) == {"site_url_placeholder", "example.co.uk"}


@pytest.mark.parametrize("meta", ['<meta content="noindex, follow" name="robots">',
                                  "<meta name='robots' content='noindex'>",
                                  '<meta data-x="1" content="NOINDEX" name="ROBOTS" />'])
def test_a_noindex_build_is_found_in_any_attribute_order(tmp_path, meta):
    html_ = f"<html><head>{meta}</head><body><main><p>We always microchip.</p></main></body></html>"
    code, doc, err = _run(_root(tmp_path, dist=html_), _answer("Check the microchip."))
    assert code == 0, err
    assert doc["page_source"]["kind"] == "question-file" and "noindex" in doc["page_source"]["note"]


def test_the_homepage_is_slug_index(tmp_path):
    root = _root(tmp_path, qfile=False)
    (root / "dist").mkdir(exist_ok=True)
    (root / "dist/index.html").write_text('<html><head><meta name="robots" content="index, follow"></head>'
                                          "<body><main><p>Every puppy is microchipped.</p></main></body></html>", encoding="utf-8")
    q = "Where can I buy a blue Staffy puppy in the UK?"
    code, doc, err = _run(root, _answer("Check the puppy is microchipped.", keyword=q), slug="index", QUERY=q,
                          FETCHED_ON="2026-09-23")
    assert code == 0, err
    assert doc["page_source"] == {"kind": "dist", "path": "dist/index.html", "provisional": False, "note": "built, indexable page"}
    assert doc["query_source"]["from"] == "page-map" and doc["raw"] == "data/queries/raw/index/ai_engines.response.json"
    assert problems(doc, "index-2026-09-23.json") == []


def test_a_build_older_than_its_sources_stops(tmp_path):
    page = '<html><head><meta name="robots" content="index, follow"></head><body><main><p>Microchipped.</p></main></body></html>'
    root = _root(tmp_path, dist=page)
    built = root / f"dist/uk-locations/{MAN}/index.html"
    (root / "src/pages").mkdir(parents=True)
    newer = root / "src/pages/index.astro"
    newer.write_text("---\n---\n", encoding="utf-8")
    later = root / "data/queries/raw" / MAN / "later.json"
    later.write_text("{}", encoding="utf-8")
    os.utime(built, (4_000_000_000, 4_000_000_000))       # every copied file is older than the build ...
    os.utime(newer, (5_000_000_000, 5_000_000_000))       # ... but this source file is newer
    code, _, err = _run(root, _answer("Check the microchip."))
    assert code != 0 and "older than src/pages/index.astro" in err and "npm run build" in err
    os.utime(newer, (3_000_000_000, 3_000_000_000))       # the build is newer: it stands
    os.utime(later, (4_500_000_000, 4_500_000_000))       # research files under data/queries/ never count
    assert _run(root, _answer("Check the microchip."))[0] == 0
