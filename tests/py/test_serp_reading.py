import json
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import serp_reading as SR

RESP = {"tasks": [{"result": [{"items": [
    {"type": "ai_overview"}, {"type": "organic", "url": "https://a.example/x"},
    {"type": "people_also_ask"}, {"type": "organic", "url": "https://b.example/y"}]}]}]}
SERP = {"questions": [{"text": "How much are blue Staffy puppies?", "detail": "serp_google_paa"}]}


def test_features_and_expectations():
    r = SR.read(RESP, SERP, sections=[{"id": "litter-prices", "heading": "What Do They Cost?"}])
    assert r["features"] == {"ai_overview": 1, "organic": 2, "people_also_ask": 1}
    kinds = [e["signal"] for e in r["expect"]]
    assert "ai_overview" in kinds and "people_also_ask" in kinds
    assert r["paa"][0]["answered_by"] == "litter-prices"


# ── the intent-synonym table is pinned: a change here is a deliberate change ────────────────
def test_intent_synonym_table_is_pinned():
    assert set(SR.INTENT_SYNONYMS) == {"cost", "deposit", "delivery", "health", "temperament",
                                       "breed_type"}
    hits = {
        "cost": ["What do they cost?", "Price list", "How much is a puppy?", "From £1,500"],
        "deposit": ["How much is the deposit?", "Can I reserve one?"],
        "delivery": ["Do you deliver?", "How does the puppy travel?", "Can I collect?"],
        "health": ["Are the parents health tested?", "Common problems"],
        "temperament": ["Are they aggressive?", "Staffy temperament", "Behavioral issues"],
        "breed_type": ["Is it a pit bull?", "English or American?"],
    }
    for concept, texts in hits.items():
        for t in texts:
            assert concept in SR.concepts(t), (concept, t)
    # "how much" about exercise or food is not a cost question
    assert "cost" not in SR.concepts("How much exercise does a Staffy need?")


def test_flat_saved_response_is_read_too():
    flat = {"items": RESP["tasks"][0]["result"][0]["items"]}
    assert SR.items_of(flat) == SR.items_of(RESP)
    assert SR.items_of({}) == []


def test_paa_matches_through_plurals_and_h3_tree():
    secs = [{"id": "intro", "heading": "Welcome"},
            {"id": "temperament", "heading": "Are Blue Staffies Aggressive?",
             "tree": [{"level": 3, "heading": "What Behaviour Issues Should I Expect?"}]},
            {"id": "faq", "heading": "Questions",
             "tree": [{"level": 3, "heading": "row-1",
                       "intent": "Q: Is a Staffy a Good House Dog? — the row"}]}]
    serp = {"questions": [
        {"text": "What are common Staffie behavioral issues?", "detail": "serp_google_paa"},
        {"text": "Is a Staffy a good house dog?", "detail": "serp_google_paa"},
        {"text": "How rare are blue Staffies?", "detail": "serp_google_paa"},
        {"text": "Blue staffy puppies london price", "detail": "serp_google_related"}]}
    r = SR.read({"items": []}, serp, secs)
    got = {p["q"]: p["answered_by"] for p in r["paa"]}
    assert got == {"What are common Staffie behavioral issues?": "temperament",
                   "Is a Staffy a good house dog?": "faq",
                   "How rare are blue Staffies?": None}
    assert [x["q"] for x in r["related"]] == ["Blue staffy puppies london price"]


def test_paa_from_response_items_is_merged_without_duplicates():
    resp = {"items": [{"type": "people_also_ask", "items": [
        {"title": "How much are blue Staffy puppies?"}, {"title": "Are Staffies good with kids?"}]}]}
    r = SR.read(resp, SERP, [])
    assert [p["q"] for p in r["paa"]] == ["How much are blue Staffy puppies?",
                                          "Are Staffies good with kids?"]


def test_ranking_types_and_competitor_labels():
    resp = {"items": [
        {"type": "organic", "rank_group": 1, "domain": "a.example",
         "url": "https://a.example/staffies-for-sale/london", "title": "6 Puppies For Sale"},
        {"type": "organic", "rank_group": 2, "domain": "b.example",
         "url": "https://b.example/", "title": "Home"},
        {"type": "organic", "rank_group": 3, "domain": "c.example",
         "url": "https://c.example/blog/staffy-guide", "title": "A Staffy Guide"},
        {"type": "organic", "rank_group": 4, "domain": "d.example",
         "url": "https://d.example/x", "title": "Something"}]}
    comp = {"pages": [{"url": "https://b.example/", "metrics": {"schema_types": ["LocalBusiness"]}},
                      {"url": "https://d.example/x", "metrics": {"listing": "card grid holds 90%"}}]}
    r = SR.read(resp, {}, [], competitors=comp)
    assert [(x["pos"], x["type"]) for x in r["ranking"]] == [
        (1, "listing"), (2, "breeder"), (3, "guide"), (4, "listing")]
    assert "card grid" in r["ranking"][3]["basis"]


def test_unknown_type_and_aio_cites():
    resp = {"items": [{"type": "top_stories"},
                      {"type": "ai_overview", "items": [{"references": [
                          {"domain": "www.thekennelclub.org.uk", "url": "https://x"},
                          {"domain": "www.thekennelclub.org.uk", "url": "https://y"},
                          {"domain": "www.rspca.org.uk"}]}]}]}
    r = SR.read(resp, {}, [])
    rows = {e["signal"]: e["rewards"] for e in r["expect"]}
    assert rows["top_stories"] == "shown on page one"
    assert r["aio_cites"] == ["www.thekennelclub.org.uk", "www.rspca.org.uk"]


def test_async_aio_has_no_cites():
    r = SR.read({"items": [{"type": "ai_overview", "asynchronous_ai_overview": True}]}, {}, [])
    assert r["aio_cites"] is None and "NOT FETCHED" in r["aio_note"]


def _board(slug="uk-locations/test-city", sections=None):
    return {"meta": {"slug": slug}, "brief": {"primary_keyword": "blue staffy puppies test"},
            "sections": sections or [{"id": "litter-prices", "heading": "What Do They Cost?"}]}


def test_block_missing_files_is_not_fetched(tmp_path):
    out = SR.block(_board(), root=tmp_path)
    assert out == "NOT FETCHED — no data/queries/raw/test-city/serp_google*.json"


def test_block_renders_every_part(tmp_path):
    d = tmp_path / "data/queries/raw/test-city"
    d.mkdir(parents=True)
    resp = {"items": RESP["tasks"][0]["result"][0]["items"] + [
        {"type": "organic", "rank_group": 3, "domain": "c.example",
         "url": "https://c.example/sale/puppies", "title": "Puppies for sale"}]}
    serp = dict(SERP, fetched="2026-09-30", status="ok",
                questions=SERP["questions"] + [{"text": "How rare are blue Staffies?",
                                                "detail": "serp_google_paa"}])
    (d / "serp_google.response.json").write_text(json.dumps(resp))
    (d / "serp_google.json").write_text(json.dumps(serp))
    out = SR.block(_board(), root=tmp_path)
    assert "blue staffy puppies test" in out and "2026-09-30" in out
    assert "| On page one | Count | What it rewards |" in out
    assert "Who ranks, and with what kind of page" in out
    assert "What the AI Overview cites" in out and "NOT FETCHED" in out
    assert "People Also Ask → the section that answers it" in out
    assert "**none — gap**" in out
    tail = out.split("What this means for our page", 1)[1]
    bullets = [l for l in tail.splitlines() if l.startswith("- ")]
    assert 3 <= len(bullets) <= 5
    assert any("1 of 2" in b and "gap" in b for b in bullets)


def test_cli_usage(capsys):
    assert SR.main([]) == 2
    assert SR.main(["no-such-page-slug"]) == 2
    assert "usage" in capsys.readouterr().err
