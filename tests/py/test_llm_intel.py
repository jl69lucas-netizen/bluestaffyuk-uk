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
OWN = "bluestaffyuk"


def _band(words):
    return "short" if words < 100 else "medium" if words <= 300 else "long"


def problems(doc, name=None):
    """Every way `doc` breaks the contract; [] when it keeps it."""
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
        if doc["format"]["status"] != "NOT FETCHED" or doc["paid_this_run"]:
            out.append("NOT FETCHED: format is NOT FETCHED and nothing was paid")
    own = any(OWN in s["domain"] for s in sites)
    if ok and doc["bsuk_cited"] != own:
        out.append(f"bsuk_cited is {doc['bsuk_cited']} but a BSUK domain is {'' if own else 'not '}among the sites")
    for s in sites:
        if (s["registry_id"] is None) != (s["tier"] is None):
            out.append(f"{s['domain']}: registry_id and tier are both set or both null")
        if OWN in s["domain"] and s["registry_id"] is not None:
            out.append(f"{s['domain']}: BSUK's own domain has no registry id")
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
    day = datetime.date.fromisoformat
    old = [] if not ok else [doc["fetched"]["fetched_on"]]
    old += [qs["gap_matrix"][-13:-3]] if qs["gap_matrix"] else []
    if any((day(doc["date"]) - day(d)).days > 30 for d in old) and not doc["stale"]:
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
    "citations": [{"domain": "pets4homes.co.uk", "registry_id": "pets4homes", "tier": 2},
                  {"domain": "thekennelclub.org.uk", "registry_id": None, "tier": None}],
    "local_businesses": [{"domain": "cheap-pups-example.com", "registry_id": "cheap-pups-example", "tier": 5}],
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
    (lambda d: d["citations"].append({"domain": "bluestaffyuk.uk", "registry_id": None, "tier": None}), "bsuk_cited"),
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
        {"url": "/staffy-price-guide/", "title": "Staffy Price Guide", "h1": "Staffy Price Guide", "headings": []}]}), encoding="utf-8")
    (tmp_path / "data/competitors.json").write_text(json.dumps({"competitors": [
        {"id": "cheap-pups", "root_domain": "cheap-pups.com", "tier": 5}]}), encoding="utf-8")
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
    assert [s["domain"] for s in doc["local_businesses"]] == ["cheap-pups.com"]  # instagram is a profile link
    assert doc["risks"] == [{"domain": "cheap-pups.com", "registry_id": "cheap-pups",
                             "reason": doc["risks"][0]["reason"]}]
    assert problems(doc, "staffy-price-guide-2026-09-23.json") == []
    env["GAP_TOPICS"] = "staffy training"
    run = subprocess.run([sys.executable, "-", "staffy-price-guide", str(resp)], input=_agent_script(), cwd=tmp_path,
                         env=env, capture_output=True, text=True)
    assert run.returncode != 0 and "GAP_TOPICS not in" in run.stderr


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
