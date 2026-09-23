# tests/py/test_llm_intel.py — the LLM citation intel files bsuk-llm-keyword-intel writes
# (docs/research/llm-intel/<slug>-<YYYY-MM-DD>.json) keep the shape the strategy synthesizer
# and the page builders read: schemas/llm-intel.schema.json plus the rules a schema cannot
# say (BSUK cited only from its own domain, the citation gap and tier-5 risks follow from the
# mapped sites, "high" only for a missing buying-safety entity, no format from a summary).
# The agent runs it on its file before hand-off: python3 tests/py/test_llm_intel.py <file>...
import copy
import json
import pathlib
import re
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
    risky = sorted({(s["domain"], s["registry_id"]) for s in sites if s["tier"] == 5})
    if sorted({(r["domain"], r["registry_id"]) for r in doc["risks"]}) != risky:
        out.append(f"risks must list exactly the tier-5 sites cited: {risky}")
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
