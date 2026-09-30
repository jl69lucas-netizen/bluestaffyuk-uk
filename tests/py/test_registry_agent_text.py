# tests/py/test_registry_agent_text.py — pins bsuk-competitor-registry's approval rules and the
# candidate list it reads (Known Issue 50), the way test_strategy_example.py pins the
# synthesizer's. The agent is instructions, not code: these phrases are the rules a reviewer
# asked for, so a later edit that drops one fails here.
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
AGENT = REPO / ".claude/agents/bsuk-competitor-registry.md"
TRACKER = REPO / ".claude/agents/bsuk-rank-tracker.md"
CANDIDATES = REPO / "docs/research/competitor-registry-candidates.md"


def text(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_the_approval_path_allows_a_same_day_suffix():
    assert "`approved: docs/research/competitor-registry-proposal-<YYYY-MM-DD>[-<n>].md`" in text(AGENT)


def test_the_registry_changed_check_compares_a_hash_not_only_the_date():
    agent = text(AGENT)
    assert "its SHA-256" in agent
    assert "hashlib.sha256(open('data/competitors.json','rb').read()).hexdigest()" in agent
    assert "The hash, not the date" in agent
    assert "`_meta.last_discovery_run` (or its absence) no longer what the proposal recorded" not in agent


def test_a_tier_5_edit_replaces_the_old_notes():
    assert "replaces its `notes` with the tier-5 signals" in text(AGENT)
    assert "never the old tier's notes" in text(AGENT)


def test_the_agent_reads_the_candidate_list_and_adds_only_what_a_seed_result_holds():
    agent = text(AGENT)
    assert "`docs/research/competitor-registry-candidates.md`" in agent
    assert "registered only when one of this run's seed results holds its root domain" in agent
    assert '"candidates not in the seed results"' in agent


def test_dbrg_is_an_open_candidate_and_not_a_registry_row():
    rows = [ln for ln in CANDIDATES.read_text(encoding="utf-8").splitlines()
            if ln.startswith("| dbrg.uk |")]
    assert len(rows) == 1 and rows[0].rstrip().endswith("| open |"), rows
    reg = json.loads((REPO / "data/competitors.json").read_text(encoding="utf-8"))
    assert "dbrg.uk" not in {c["root_domain"] for c in reg["competitors"]}


def test_the_rank_tracker_names_no_registry_field_the_schema_lacks():
    tracker = TRACKER.read_text(encoding="utf-8")
    schema = json.loads((REPO / "schemas/competitors.schema.json").read_text(encoding="utf-8"))
    fields = set(schema["$defs"]["competitor"]["properties"])
    named = set(re.findall(r"\blast_[a-z_]+", tracker))
    assert named <= fields, named - fields
    assert "Leave data/competitors.json unchanged" in tracker
