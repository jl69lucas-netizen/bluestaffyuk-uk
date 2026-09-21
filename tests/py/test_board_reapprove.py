"""board_approve.py --reapprove — the controller's post-approval WORDING fix.

The ordinary route for an edit to a record is to re-board it, and that stays true. This mode
exists for the one case the ordinary route cannot reach: a record that has ALREADY been
approved, whose wording a build review has to move — a heading that collides with a page
built after the board was signed, a links block short of the floor, a counter heading that
says "three" over four tiles. Replaying `data/boards/inbox/<slug>.json` cannot re-approve
that record, because the inbox carries the PRE-approval hash and nothing reproduces it once
`approval`, `approval_previous` and `tuple.hero` have moved.

So the question these tests ask is not "does it stamp a hash" — anything can stamp a hash.
It is whether the mode can be used to change an ANSWER. Every test below is about the line
between wording, which it may move, and a pick, a menu, a figure or a section, which it may
not.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import pytest  # noqa: E402

import pageboard as PB  # noqa: E402
import board_approve as BA  # noqa: E402
from test_page_board import MIN_BOARD  # noqa: E402

NOW = "2026-09-21T09:00:00Z"
REASON = "post-approval wording fix from build review; picks unchanged"


def approved(**over):
    """A record in the state a re-approval starts from: approved, and matching its own hash."""
    b = json.loads(json.dumps(MIN_BOARD))
    b["meta"]["status"] = "approved"
    # MIN_BOARD's placeholder external link is not a row of the external-link library, and
    # `validate_board()` (which a re-approval runs) is right to refuse it. These tests are
    # about the hash and the diff, so the section starts with no external link and the one
    # test that needs one adds a real library row.
    b["sections"][0]["links"]["external"] = []
    b.update(over)
    b["approval"] = {"approved_at": "2026-09-20T12:00:00Z", "h1": 1, "picks": {}, "notes": {},
                     "canvas_version": None, "record_hash": ""}
    for s in b["sections"]:
        if s.get("options", {}).get("pick"):
            b["approval"]["picks"][s["id"]] = s["options"]["pick"]
    b["approval"]["record_hash"] = PB.record_hash(b)
    assert PB.approval_matches(b)
    return b


def edited(fn):
    """`old`, and a deep copy of it with `fn` applied — the pair a re-approval compares."""
    old = approved()
    new = json.loads(json.dumps(old))
    fn(new)
    return old, new


# ── what it is for ────────────────────────────────────────────────────────────────────────

def test_a_heading_rewording_is_re_approved_and_the_hash_follows_the_record():
    old, new = edited(lambda b: b["sections"][0].__setitem__("heading", "A Heading The Review Moved"))
    assert not PB.approval_matches(new), "the premise: an edit inside the hash breaks the approval"
    out = BA.apply_reapproval(new, REASON, old, NOW)
    assert PB.approval_matches(out["board"]), "and the re-approval is what makes it whole again"


def test_every_answer_the_breeder_gave_is_carried_through_untouched():
    """The whole safety argument: a re-approval may not become a way to change a pick."""
    old, new = edited(lambda b: b["sections"][0].__setitem__("heading", "Reworded"))
    out = BA.apply_reapproval(new, REASON, old, NOW)
    before, after = old["approval"], out["board"]["approval"]
    for field in ("approved_at", "h1", "picks", "notes", "canvas_version"):
        assert after[field] == before[field], field


def test_the_reapproval_row_records_the_reason_and_the_paths_that_moved():
    old, new = edited(lambda b: b["sections"][0].__setitem__("heading", "Reworded"))
    out = BA.apply_reapproval(new, REASON, old, NOW)
    rows = out["board"]["approval"]["reapprovals"]
    assert len(rows) == 1
    assert rows[0]["at"] == NOW and rows[0]["reason"] == REASON
    assert rows[0]["changed_paths"] == ["/sections/0/heading"]
    assert out["board"]["approval"]["reapproved_at"] == NOW


def test_a_second_reapproval_appends_rather_than_replacing_the_first():
    old, new = edited(lambda b: b["sections"][0].__setitem__("heading", "Once"))
    first = BA.apply_reapproval(new, REASON, old, NOW)["board"]
    again = json.loads(json.dumps(first))
    again["sections"][0]["heading"] = "Twice"
    rows = BA.apply_reapproval(again, "and again", first, "2026-09-22T09:00:00Z")["board"]["approval"]["reapprovals"]
    assert [r["reason"] for r in rows] == [REASON, "and again"]


def test_a_links_block_addition_is_wording_class():
    """Working rule 12 says every link is on the board. A review that finds a page two
    external references short fixes the RECORD, and this is how the record catches up."""
    def add_link(b):
        b["sections"][0]["links"]["external"].append(
            {"href": "https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/puppycare",
             "anchor": "The RSPCA on caring for a puppy",
             "library_row": "https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/puppycare"})
    old, new = edited(add_link)
    out = BA.apply_reapproval(new, REASON, old, NOW)
    assert out["changed_paths"] == ["/sections/0/links/external/0"]


def test_removing_a_whole_stats_row_is_wording_and_is_not_read_as_editing_the_others():
    """Index-wise, dropping row 0 of three "changes" every remaining `n`. Judged by row
    identity it is what it is: two rows removed, none edited."""
    def three_stats(b):
        b["sections"][0]["stats"] = [{"n": "1", "label": "first row", "source": "data/x.json#a"},
                                     {"n": "2", "label": "second row", "source": "data/x.json#b"},
                                     {"n": "3", "label": "third row", "source": "data/x.json#c"}]
    old = approved()
    three_stats(old)
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["stats"] = new["sections"][0]["stats"][:1]
    out = BA.apply_reapproval(new, REASON, old, NOW)
    assert out["board"]["sections"][0]["stats"] == [
        {"n": "1", "label": "first row", "source": "data/x.json#a"}]


# ── what it refuses ───────────────────────────────────────────────────────────────────────

def test_a_changed_pick_is_refused_and_the_message_names_the_pointer():
    old, new = edited(lambda b: b["sections"][0]["options"].__setitem__("pick", "avail-b"))
    with pytest.raises(PB.BoardError) as e:
        BA.apply_reapproval(new, REASON, old, NOW)
    assert "/sections/0/options/pick" in str(e.value)
    assert "re-board" in str(e.value)


def test_a_changed_styles_menu_is_refused():
    old, new = edited(lambda b: b["sections"][0].__setitem__("styles", ["S1", "S2"]))
    with pytest.raises(PB.BoardError, match="styles"):
        BA.apply_reapproval(new, REASON, old, NOW)


def test_an_edited_figure_is_refused_even_though_a_removed_one_is_allowed():
    old = approved()
    old["sections"][0]["stats"] = [{"n": "6", "label": "available", "source": "data/puppies.json#n"}]
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["stats"][0]["n"] = "7"
    with pytest.raises(PB.BoardError, match="added or edited"):
        BA.apply_reapproval(new, REASON, old, NOW)


def test_a_moved_figure_source_is_refused():
    old = approved()
    old["sections"][0]["stats"] = [{"n": "6", "label": "available", "source": "data/puppies.json#n"}]
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["stats"][0]["source"] = "data/settings.json#n"
    with pytest.raises(PB.BoardError, match="added or edited"):
        BA.apply_reapproval(new, REASON, old, NOW)


def test_a_moved_ledge_source_is_refused():
    """A hero ledge cites its data the same way a counter figure does, and it is the same
    answer: `/source` anywhere is a claim about where a number came from."""
    old = approved()
    old["sections"][0]["hero"] = {"ticks": [{"text": "3 males", "source": "data/puppies.json#m"}]}
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["hero"]["ticks"][0]["source"] = "data/settings.json#m"
    with pytest.raises(PB.BoardError, match="/source"):
        BA.apply_reapproval(new, REASON, old, NOW)


def test_a_removed_section_is_refused():
    old, new = edited(lambda b: b["sections"].pop())
    with pytest.raises(PB.BoardError, match="section list moved"):
        BA.apply_reapproval(new, REASON, old, NOW)


def test_a_renamed_section_id_is_refused():
    old, new = edited(lambda b: b["sections"][0].__setitem__("id", "renamed"))
    with pytest.raises(PB.BoardError, match="section list moved"):
        BA.apply_reapproval(new, REASON, old, NOW)


def test_no_reason_is_refused():
    old, new = edited(lambda b: b["sections"][0].__setitem__("heading", "Reworded"))
    with pytest.raises(PB.BoardError, match="reason"):
        BA.apply_reapproval(new, "   ", old, NOW)


def test_an_unchanged_record_is_refused_rather_than_re_stamped():
    old = approved()
    with pytest.raises(PB.BoardError, match="needs no re-approval"):
        BA.apply_reapproval(json.loads(json.dumps(old)), REASON, old, NOW)


def test_a_draft_is_refused_because_a_draft_is_approved_the_ordinary_way():
    old, new = edited(lambda b: b["sections"][0].__setitem__("heading", "Reworded"))
    new["meta"]["status"] = "boarded"
    with pytest.raises(PB.BoardError, match="already approved"):
        BA.apply_reapproval(new, REASON, old, NOW)


def test_a_baseline_that_never_matched_its_own_approval_is_refused():
    """The diff has to be taken against a record somebody actually signed. A baseline whose
    hash does not describe it is not one, and re-approving from it would launder an edit
    that was already outside the approval before this run began."""
    old, new = edited(lambda b: b["sections"][0].__setitem__("heading", "Reworded"))
    old["sections"][0]["intent"] = "moved after the hash was stamped"
    with pytest.raises(PB.BoardError, match="baseline"):
        BA.apply_reapproval(new, REASON, old, NOW)


def test_a_reworded_sections_fingerprint_is_refreshed_so_the_next_reboard_does_not_reask_it():
    """`locked_picks()` drops a carried pick when the section's fingerprint has moved, which
    is right for a re-board and wrong after a re-approval: the mode has already refused every
    edit that could change what was chosen, so a moved fingerprint means somebody fixed a
    heading. Left alone it would ask the breeder a question they have answered."""
    old = approved()
    old["approval"]["section_hashes"] = {s["id"]: PB.section_fingerprint(s) for s in old["sections"]}
    old["approval_previous"] = json.loads(json.dumps(old["approval"]))
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["heading"] = "A Heading The Review Moved"
    out = BA.apply_reapproval(new, REASON, old, NOW)["board"]
    sid = out["sections"][0]["id"]
    want = PB.section_fingerprint(out["sections"][0])
    assert out["approval"]["section_hashes"][sid] == want
    assert out["approval_previous"]["section_hashes"][sid] == want
    assert PB.approval_matches(out), "and the hash is taken AFTER the refresh, not before it"


def test_a_record_that_never_carried_fingerprints_does_not_grow_them():
    old, new = edited(lambda b: b["sections"][0].__setitem__("heading", "Reworded"))
    out = BA.apply_reapproval(new, REASON, old, NOW)["board"]
    assert "section_hashes" not in out["approval"]


# ── the diff itself ───────────────────────────────────────────────────────────────────────

def test_the_diff_is_taken_over_the_hashed_projection_only():
    """`dropped`, `verbatim`, `meta.status` and an asset's baked file are outside
    record_hash by design (spec §9 amendment 6d). They never needed a re-approval, so they
    are not reported by one — otherwise the row that matters is buried in churn."""
    old = approved()
    new = json.loads(json.dumps(old))
    new["sections"][0]["heading"] = "The One Thing That Moved"
    new["dropped"] = {"text": ["a claim the rebuild did not restate"]}
    new["verbatim"] = {"changed": [{"kind": "h1", "old": "an old h1", "new": "a new h1",
                                          "reason": "a rank claim measured against nothing"}]}
    out = BA.apply_reapproval(new, REASON, old, NOW)
    assert out["changed_paths"] == ["/sections/0/heading"]


def test_a_pointer_escapes_the_two_characters_rfc_6901_reserves():
    assert BA.json_pointer_diff({"a/b": 1}, {"a/b": 2}) == ["/a~1b"]
    assert BA.json_pointer_diff({"a~b": 1}, {"a~b": 2}) == ["/a~0b"]
