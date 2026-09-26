#!/usr/bin/env python3
"""board_approve.py <slug> [--canvas-dir docs/design/board-<slug>]

1. Reads the approval the board wrote to its database. Operator step first, because a
   Python script cannot call the Artifact tool:
   Artifact read_db collection="boards" doc_id="<slug>" out_dir="data/boards/inbox"
   → data/boards/inbox/<slug>.json
2. Verifies record_hash against the record as it stands (refuses a stale approval).
3. Writes canvas TEXT tweaks back into the record (the breeder editing the outline), then
   re-hashes — the approval covers the record the breeder actually saw, choices included.
4. Copies the approval in, sets picks/notes/h1, status=approved.
5. Appends the tuple + the H6 prefixes the record actually spends to
   data/component-ledger.json, in the shape the existing pages use.
6. Promotes referenced PROPOSED entities that carry a source to ASSERTED.

One approval, three documents. apply_approval() is pure — it raises before anything is
written — and main() serialises all three before it replaces any of them, so a refused
approval leaves the tree exactly as it found it.

  python3 scripts/board_approve.py --reapprove <slug> --reason "<text>"

RE-APPROVAL is the second mode, and it is a different act. A build review finds wording
inside `record_hash` that has to move — a heading that collides with a page built after the
board was approved, a links block two rows short of the floor, a counter heading that says
"three" over four tiles — and the sanctioned route, editing the record and replaying
`data/boards/inbox/<slug>.json`, cannot work once an approval has been applied: the inbox
carries the PRE-approval hash and none of the four readings in `pre_approval_hashes()`
reproduces it after `approval`, `approval_previous` and `tuple.hero` have moved. Verified
on two records. The only alternatives were to hand-stamp a hash, which is forging an
approval, or to leave the defect on the page.

So the controller re-approves, with a reason, and the record says so. `--reapprove` keeps
every pick, the H1 index, the meta indices and the notes EXACTLY as the breeder left them,
recomputes `record_hash` over the record as it now stands, stamps `approval.reapproved_at`
and appends `{at, reason, changed_paths}` to `approval.reapprovals`. `changed_paths` is the
JSON-pointer diff between the record at HEAD and the record now, taken over the HASHED
projection — so it lists exactly what moved inside the hash and nothing that was always
outside it.

WHAT IT REFUSES, and why the list is what it is. A pick, a `styles` menu, a figure's `n` or
its `source`, a ledge source, a section id, a removed section: every one of those is a
question the breeder ANSWERED, and changing the answer with a stamp is the thing this mode
must never become. They need a real re-pick on the board. What is allowed is wording
(headings, intents, notes, titles), additions to a links block, and removing a whole row
from a hero ledge — none of which changes what was chosen, only what it says.
"""
import argparse
import html as _html
import json
import os
import pathlib
import re
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB
from pageboard import file_token       # one `#` → `_` spelling for the whole board system
import image_rules as IR               # the `img:<slot>` picks (system-gaps build, Task 10)

# The build-gate checks approval never waits on (family_rules owns the one copy).
APPROVAL_EXEMPT = PB.FR.APPROVAL_EXEMPT

H2 = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)
TAG = re.compile(r"<[^>]+>")


def artboard_names(section_id, pick, viewport="Desktop"):
    """The filename this pick was saved under. A list of one, because the caller walks it.

    One spelling on every surface outside the record (breeder ruling 2026-09-12): `#` is
    written `_` by PB.file_token() — it breaks a file:// path, and the design-canvas helper
    refuses `+` — so an artboard extracted from the published canvas comes back under the
    same name the writer emitted. A second name that can never exist would only pad the
    WARN line on a real miss."""
    return [f"{section_id}--{file_token(pick)}--{viewport}.dc.html"]



def writeback_text(board, canvas_dir):
    """A saved artboard's <h2> text becomes the section heading if it changed. Returns
    [(section id, field, old, new)]. Only the heading is written back: it is the one copy
    field an artboard shows verbatim; intents render as summaries, never as final prose.

    Strict on purpose. A named canvas directory that is not there is a typo, and an
    artboard the breeder split into two <h2>s has no single heading to write back —
    both raise rather than approve the record the breeder did not see. An artboard that is
    merely absent, heading-less, or carrying an <h2> that strips to nothing warns on
    stderr: the canvas is a subset of the record.

    The artboard is looked up under the one refresh-id spelling on disk (artboard_names):
    `_`, as PB.file_token() spells it and the published design canvas keeps it."""
    canvas_dir = pathlib.Path(canvas_dir)
    if not canvas_dir.exists():
        raise PB.BoardError(f"canvas directory {canvas_dir} does not exist")
    changed = []
    for s in board["sections"]:
        pick = s["options"].get("pick")
        if not pick:
            continue
        names = artboard_names(s["id"], pick)
        art = next((canvas_dir / n for n in names if (canvas_dir / n).exists()), None)
        if art is None:
            print(f"board-approve WARN no artboard for {s['id']} ({pick}): tried {', '.join(names)}", file=sys.stderr)
            continue
        found = H2.findall(art.read_text(encoding="utf-8"))
        if not found:
            print(f"board-approve WARN {art.name} has no <h2> — heading left as written", file=sys.stderr)
            continue
        if len(found) > 1:
            raise PB.BoardError(
                f"{art.name} carries {len(found)} <h2> headings — section {s['id']} has one heading, "
                "so which one to write back is not knowable; fix the artboard")
        new = re.sub(r"\s+", " ", _html.unescape(TAG.sub("", found[0]))).strip()
        if not new:
            print(f"board-approve WARN {art.name} has an <h2> that strips to empty — heading left as written",
                  file=sys.stderr)
            continue
        if new != s["heading"]:
            changed.append((s["id"], "heading", s["heading"], new))
            s["heading"] = new
    return changed


def spent_prefixes(board):
    """The H6 prefixes this record actually spends: the run up to and including the first
    colon of every H6 heading, in render order, deduplicated. Read from the headings rather
    than from tuple.h6_prefixes so a prefix the author declared and never used stays free
    for the next page — and so a prefix that IS used is spent even if it was never declared.
    The shape matches what spent_h6_prefixes() reads back out of the ledger."""
    out = []
    for level, text in PB.all_headings(board):
        if level != 6 or ":" not in text:
            continue
        prefix = text.split(":", 1)[0].strip() + ":"
        if prefix not in out:
            out.append(prefix)
    return out


# --- the tuple the picks imply -------------------------------------------------------
#
# Before this change the tuple was hand-authored, and the outline writer put the sentinel
# "kit" on every axis of every record — so the first three approved boards wore an
# IDENTICAL tuple and `ledger-tuple-identical` fired between each pair, although their
# style picks differed. The tuple is not authored any more: the seven component axes are
# READ OFF the approved picks, so the combo the ledger polices is the combo the breeder
# actually chose.
#
# A styled section contributes to the axis its SHAPE names. The style id is lowercased
# because a ledger component id is `^[a-z0-9-]+(#[a-z0-9-]+)?$`
# (schemas/component-ledger.schema.json) and the board spells its styles "S1".."S3".
SHAPE_TUPLE_AXIS = {"hero": "hero", "faq": "faq", "dial": "dial", "sheet": "rail",
                    "table": "table"}
# The mobile section sheet reuses the `rail` axis: both are the page's secondary
# navigation chrome, and the ledger has no eighth axis to give it.
SHAPE_TUPLE_SET = {"takeaways": "takeaway"}          # the one axis that holds a set
# `toc` is not a picked section on any board: every rebuilt page mounts the one kit page
# nav, so the axis records that fixed component instead of a sentinel.
FIXED_TOC = "pagenav-c"
# Shapes that render SECTION content rather than a page-level shell. They are deliberately
# not tuple axes — the ledger asks how a page's chrome is combined, and a review mode or a
# puppy grid is not chrome. `table` USED TO BE one of them, on the note that no board offered
# a table section yet; spec §9 amendment 5 (working rule 13) ended that condition — a table is
# a `table`-shaped section with three rendered styles and "tuple.table records the pick" — so
# the shape now feeds its axis like every other picked shell, and the homepage is the first
# record to fill it.
NON_TUPLE_SHAPES = {"standard", "reviews", "puppies", "form", "trust", "stats", "divider"}
DERIVED_ID_AXES = ("hero", "dial", "rail", "table", "faq")


# A component id is normally `<shape>-<style>`. `sheet` is the exception: it is recorded
# on the `rail` axis, and an id that named the shape would put `sheet-s3` in a pool called
# `rail` — two names for one component, which is the confusion the ledger exists to avoid.
SHAPE_ID_PREFIX = {"sheet": "rail"}


def component_id(shape, pick):
    """The ledger component id a (shape, style pick) pair names."""
    return f"{SHAPE_ID_PREFIX.get(shape, shape)}-{pick}".lower()


def derive_tuple(board, base):
    """The tuple `board`'s picks imply, laid over `base` (the tuple as the author wrote it).

    Only the seven component axes move. `stepper`, `newsletter` and the declared
    `h6_prefixes` are authored content and are carried through untouched."""
    t = json.loads(json.dumps(base))
    for key in DERIVED_ID_AXES:
        t[key] = ""
    t["takeaway"] = []
    t["toc"] = FIXED_TOC
    for s in board["sections"]:
        shape, pick = s["shape"], s["options"].get("pick")
        if not pick or shape in NON_TUPLE_SHAPES:
            continue
        if shape in SHAPE_TUPLE_AXIS:
            t[SHAPE_TUPLE_AXIS[shape]] = component_id(shape, pick)
        elif shape in SHAPE_TUPLE_SET:
            cid = component_id(shape, pick)
            if cid not in t[SHAPE_TUPLE_SET[shape]]:
                t[SHAPE_TUPLE_SET[shape]].append(cid)
    return t


def ledger_entry(board):
    """The row this page takes in data/component-ledger.json — the same eight keys every
    existing page carries, never a bare copy of the tuple (which would record the DECLARED
    prefixes instead of the spent ones)."""
    t = board["tuple"]
    entry = {k: t.get(k, "") for k in ("hero", "dial", "rail", "toc", "table", "faq")}
    entry["takeaway"] = list(t.get("takeaway", []))
    entry["h6_prefixes"] = spent_prefixes(board)
    return entry


#: Note keys that are the PAGE's and not a section's. They are kept in `approval.notes`
#: verbatim and are never written into a section's `options.note`. One member today:
#: `navigation`, the answer to the board's "Navigation on this page" block.
PAGE_NOTE_KEYS = frozenset({"navigation"})


def refuse_on_new_page_rules(b, ont):
    """The rules for new pages (scripts/family_rules.py) are answered at approval and at
    re-approval, on the record as approved, not first at the build gate: a record the build
    would refuse must never be approved, because fixing it afterwards moves the hash and forces
    a second approval. Board block 7b shows the same findings. A no-op for every page
    applies() leaves out, so the twelve built pages approve exactly as before."""
    fails = [(c, m) for c, sev, m in PB.FR.findings(b, ont)
             if sev == "FAIL" and c not in APPROVAL_EXEMPT]
    if fails:
        raise PB.BoardError(
            "this record breaks the rules for new pages — fix the record and board it again:\n"
            + "\n".join(f"  - {c}: {m}" for c, m in fails))


#: The pure API's explicit opt-out of the header pre-check. Only this skips it: `None` or `{}`
#: means "no live pages were read" and a new page is refused against that.
SKIP_LIVE = object()


def unbuilt_sibling_headings(b, live, boards):
    """{label: [heading, ...]} for every OTHER board that is approved (or was, and is being
    re-boarded) but is not in dist/ yet — so two city pages approved in one batch cannot both
    claim one heading before either is built. The label names the board, so the refusal says
    which page to reword against."""
    out = {}
    me = (b.get("meta") or {}).get("slug")
    my_key = PB.own_live_key(b)
    for slug, o in sorted((boards or {}).items()):
        if slug == me or not (o.get("approval") or o.get("approval_previous")):
            continue
        try:
            key = PB.own_live_key(o)
            if key == my_key:
                continue                              # this page under another slug spelling
            if key in live:
                continue                              # built: its live headings already count
            out[f"{key} (approved board {slug}, not built yet)"] = \
                [t for _, t in PB.all_headings(o)]
        except (KeyError, TypeError, IndexError, ValueError) as e:
            raise PB.BoardError(f"cannot read the headings of approved board {slug}: {e!r} "
                                f"— fix or re-board {slug}; approvals resume once it reads") from None
    return out


def refuse_header_collisions(b, live, boards=None):
    """A new page (family_rules.applies) whose headings collide with a live page is refused
    at approval and at re-approval, with the same `pageboard.header_hits()` the build gate
    FAILs on as `header-collision`. Otherwise the colliding record is approved, refused at
    board_gate, and the reword moves the hash and forces a second approval. `live` is
    {page: [heading, ...]} (pageboard.live_headings()); only SKIP_LIVE skips the check (the
    pure API's opt-out) — main() and reapprove_main() always read the live pages. A new page
    is never approved against an EMPTY live set (or None): that is a pre-check of nothing.
    `boards` (pageboard.load_all_boards()) adds the approved boards not yet built, judged by
    the same header_hits() comparison."""
    if live is SKIP_LIVE or not PB.FR.applies(b):
        return
    if not live:
        raise PB.BoardError(
            "header pre-check examined 0 live pages — run npm run build first; a new page is "
            "not approved against nothing")
    hits = PB.header_hits(b, {**live, **unbuilt_sibling_headings(b, live, boards)})
    if hits:
        raise PB.BoardError(
            "this record's headings collide with live pages — reword them and board it again:\n"
            + "\n".join(f"  - header-collision: {h['kind']}: {h['heading']!r} vs {h['page']} {h['with']!r}"
                        for h in hits)
            + "\n(if a listed page changed since the last build, run npm run build and retry)")


def apply_approval(board, inbox, ont, ledger, canvas_dir=None, live=SKIP_LIVE, boards=None):
    """The board, ledger and ontology as they stand after this approval. Pure: it reads
    nothing but its arguments and writes nothing — raise here and the files on disk are
    untouched. `live` is the built site's headings and `boards` every board record, for
    refuse_header_collisions()."""
    # Either the record as it stands, or the record as it stood before an approval wrote
    # picks/notes/h1 into it: applying one approval twice (a rerun, a retry after a failed
    # write) is idempotent, while a heading edited after the fact moves BOTH hashes and is
    # still refused.
    if inbox.get("record_hash") not in PB.pre_approval_hashes(board):
        raise PB.BoardError(
            "approval hash does not match the record — the record changed after the board was approved")
    b = json.loads(json.dumps(board))
    by_id = {s["id"]: s for s in b["sections"]}

    for sid, pick in inbox.get("picks", {}).items():
        if sid.startswith(IR.PICK_PREFIX):
            continue                                  # an image pick, validated below
        if sid not in by_id:
            raise PB.BoardError(f"approval picks section {sid!r}, which is not in the record")
        # The pick has to come off the menu the board offered. It is matched on the BASE,
        # because renaming an offered `base` (or the `base#refresh` placeholder) to the axis
        # it actually varies — `toc-t2-chip-cloud#state-chips` — IS the documented workflow.
        # A styled section (project 4: `styles` = ["S1","S2","S3"]) offers its styles as
        # the menu instead of component candidates; the pick is the style id verbatim.
        styles = by_id[sid].get("styles") or []
        if styles:
            if pick not in styles:
                raise PB.BoardError(f"section {sid}: pick {pick!r} is not one of its styles {styles}")
            by_id[sid]["options"]["pick"] = pick
            continue
        menu = {PB.base_of(c) for c in by_id[sid]["options"]["candidates"]}
        if PB.base_of(pick) not in menu:
            raise PB.BoardError(
                f"section {sid}: pick {pick!r} is not one of its candidates "
                f"({', '.join(by_id[sid]['options']['candidates']) or 'none offered'})")
        by_id[sid]["options"]["pick"] = pick
    # Image picks name a slot, not a section, and live only in `approval.picks`. The one read
    # this function makes outside its arguments is here: a picked file must exist on disk.
    bad = IR.validate_image_picks(b, inbox.get("picks", {}))
    if bad:
        raise PB.BoardError("image picks refused: " + "; ".join(bad))
    for sid, note in inbox.get("notes", {}).items():
        # PAGE notes are not section notes. The board's "Navigation on this page" block
        # (spec §9 amendment 7) asks about furniture the SHELL mounts — the dial, the strip,
        # the sheet and the TOC — which belongs to no section and therefore has no
        # `options.note` to be written into. Its answer lives in `approval.notes` and
        # nowhere else, so it is skipped here rather than refused: refusing it would make
        # the one page-level question on the board the one question that cannot be answered.
        if sid in PAGE_NOTE_KEYS:
            continue
        if sid not in by_id:
            raise PB.BoardError(f"approval notes section {sid!r}, which is not in the record")
        by_id[sid]["options"]["note"] = note          # "" is the breeder clearing the note
    b["h1"]["pick"] = inbox.get("h1", b["h1"]["recommended"])
    meta = inbox.get("meta")
    if meta is not None:
        # Range-checked here as well as in the schema: a database document written by hand
        # reaches this function without passing through the button that made it.
        for field in ("title", "description"):
            i, variants = meta.get(field), b["meta_set"][field + "s"]
            if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < len(variants):
                raise PB.BoardError(f"approval meta.{field}={i!r} is not one of the three {field} variants")
            b["meta_set"]["pick"][field] = i

    # The Approve button already refuses an incomplete set of picks; trusting it would make
    # a half-picked board approvable by anyone who wrote the database document by hand.
    missing = [s["id"] for s in b["sections"] if s["shape"] != "standard" and not s["options"]["pick"]]
    if missing:
        raise PB.BoardError(f"no component pick for signature section(s): {', '.join(missing)}")

    changed = writeback_text(b, canvas_dir) if canvas_dir else []

    # The tuple is derived from the picks above. `tuple_before` carries the authored tuple
    # forward in the approval so a RE-RUN can undo the derivation before it hashes: without
    # it the second run would hash a record whose tuple the first run had already rewritten,
    # and the inbox's hash — taken against the record as the breeder saw it — would never
    # match again. On a re-run the base comes from the stamp, not from the rewritten tuple.
    prior = board.get("approval") or {}
    tuple_before = prior.get("tuple_before") or json.loads(json.dumps(board["tuple"]))
    b["tuple"] = derive_tuple(b, tuple_before)

    approval = dict(inbox)
    approval["tuple_before"] = tuple_before
    # Picks, notes and the H1 index are hashed CONTENT, and so are the canvas tweaks above,
    # so the stamped hash is the record with the breeder's choices in it — which is exactly
    # the record the gate will hash when it asks whether this page is still approved.
    approval["record_hash"] = PB.record_hash(b)
    b["approval"] = approval
    b["meta"]["status"] = "approved"
    PB.validate_board(b)

    led = json.loads(json.dumps(ledger))
    led.setdefault("pages", {})[b["meta"]["slug"]] = ledger_entry(b)
    PB.validate_ledger(led)

    o = json.loads(json.dumps(ont))
    was = {e["id"]: e["authorization"] for e in o["entities"]}
    used = {e for s in b["sections"] for e in s["entities"]}
    for e in o["entities"]:
        if e["id"] in used and e["authorization"] == "PROPOSED" and e["source"]:
            e["authorization"] = "ASSERTED"
    PB.validate_ontology(o)
    promoted = [e["id"] for e in o["entities"] if e["authorization"] != was[e["id"]]]

    refuse_on_new_page_rules(b, o)
    refuse_header_collisions(b, live, boards)
    return {"board": b, "ledger": led, "ontology": o, "changed": changed, "promoted": promoted}


def rule16_refusals(old_board, new_board, boards):
    """Working rule 16 at the moment a pick becomes the approval: one message for each hero or
    counter arrangement the approved record would share that the record did not already share.
    A share that was already there is left to board_gate.py to FAIL — refusing it here would
    make re-running an approval impossible for a reason the new pick did not cause.

    "Already there" means under a LIVE approval. A re-boarded record has `approval: null` and
    carries its old picks in `approval_previous`; its carried share is the one the re-board
    exists to end, so re-picking it is a new share and is refused."""
    before = (set() if old_board.get("approval") is None
              else {(shape, pick) for shape, pick, _ in PB.rule16_shares(old_board, boards)})
    return [PB.rule16_message(shape, pick, others)
            for shape, pick, others in PB.rule16_shares(new_board, boards)
            if (shape, pick) not in before]


# ── re-approval (a controller's post-approval wording fix) ─────────────────────────────────
#
# The hashed projection is what a re-approval reports on, because it is what a re-approval
# is FOR: a field outside the hash (`dropped`, `verbatim`, `meta.status`, an asset's baked
# file) never needed one in the first place, and listing its churn would bury the one line
# that matters.
def _hashed_body(board):
    """The record as `PB.record_hash()` hashes it — same exclusions, one source of truth."""
    skip = ("approval", "dropped", "verbatim")
    body = {k: v for k, v in board.items() if k not in skip}
    meta = body.get("meta")
    if isinstance(meta, dict):
        body["meta"] = {k: v for k, v in meta.items() if k != "status"}
    assets = body.get("assets")
    if isinstance(assets, list):
        body["assets"] = [{k: v for k, v in a.items() if k not in PB.LIFECYCLE_ASSET_KEYS}
                          if isinstance(a, dict) else a for a in assets]
    return body


def _esc(token):
    """RFC 6901: `~` is `~0` and `/` is `~1`, so a pointer segment is unambiguous."""
    return str(token).replace("~", "~0").replace("/", "~1")


def json_pointer_diff(old, new, at="", out=None):
    """Every JSON pointer at which `old` and `new` differ, deepest leaf first.

    A list is compared BY INDEX, deliberately: a pointer the reader can paste into the
    record is worth more than a minimal edit script, and the one list whose rows move —
    `stats` — is judged by identity in `stats_change()` instead, before this ever runs."""
    out = [] if out is None else out
    if isinstance(old, dict) and isinstance(new, dict):
        for k in sorted(set(old) | set(new)):
            if k not in old:
                out.append(f"{at}/{_esc(k)}")
            elif k not in new:
                out.append(f"{at}/{_esc(k)}")
            else:
                json_pointer_diff(old[k], new[k], f"{at}/{_esc(k)}", out)
    elif isinstance(old, list) and isinstance(new, list):
        for i in range(max(len(old), len(new))):
            if i >= len(old) or i >= len(new):
                out.append(f"{at}/{i}")
            else:
                json_pointer_diff(old[i], new[i], f"{at}/{i}", out)
    elif old != new:
        out.append(at or "/")
    return out


def stats_change(old_board, new_board):
    """(removed, other) for every section's `stats` list, compared by ROW rather than index.

    Removing the two figures a hero ledge no longer prints is an allowed wording-class fix;
    changing a figure or its source is not. Index-wise those look the same — drop row 0 of
    four and every remaining `n` "changes" — so the rows are matched as values and the
    verdict is taken from what is actually gone. `other` holds the sections where a row was
    ADDED or EDITED, which is what the caller refuses on."""
    old_by, new_by = _sections_by_id(old_board), _sections_by_id(new_board)
    removed, other = [], []
    for sid in sorted(set(old_by) & set(new_by)):
        o = old_by[sid].get("stats") or []
        n = new_by[sid].get("stats") or []
        okeys = [json.dumps(r, sort_keys=True) for r in o]
        nkeys = [json.dumps(r, sort_keys=True) for r in n]
        rest = list(okeys)
        added = []
        for k in nkeys:
            if k in rest:
                rest.remove(k)
            else:
                added.append(k)
        if added:
            other.append(sid)
        elif rest:
            removed.append(sid)
    return removed, other


def _sections_by_id(board):
    return {s["id"]: s for s in board.get("sections", []) if isinstance(s, dict) and "id" in s}


#: A pointer touching one of these is an answer the breeder gave, not wording. Matched on
#: the pointer text because that is what the refusal has to print: a reviewer who is told
#: `/sections/3/options/pick` can open the record at it.
REAPPROVE_REFUSED = (
    ("/options/pick", "a component or style pick"),
    ("/styles", "the menu of styles a section offered"),
    ("/source", "the data path a figure or a ledge entry cites"),
)


_MISSING = object()


def _at(doc, pointer):
    """The value at a JSON pointer, or `_MISSING` when nothing is there."""
    node = doc
    for raw in pointer.split("/")[1:]:
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if key not in node:
                return _MISSING
            node = node[key]
        elif isinstance(node, list):
            if not key.isdigit() or int(key) >= len(node):
                return _MISSING
            node = node[int(key)]
        else:
            return _MISSING
    return node


def _source_is_purely_added(old_board, new_board, pointer):
    """True when this `/source` pointer is a citation that did not exist before.

    THE REFUSAL IS ABOUT A SOURCE THAT MOVES, not about one that arrives. A `source` the
    breeder approved is an answer — "this figure came from that file" — and re-pointing it
    with a stamp is what this mode must never become. But a ledge row that carried NO source
    is a row whose claim was never cited at all, and adding the path it was always derived
    from changes nothing the breeder chose: the label and the value are untouched, the gate
    that reads sources gains a row it could not see before, and the record gets stricter
    rather than looser. Found on /blue-staffy-health-uk/, whose hero aside states the two
    test names and both parents' status with no citation between them, and where the only
    other routes were to re-board an approved page over two additions or to leave two claims
    uncited for ever. An added source that does not resolve is still refused — by
    `validate_board()`, which every re-approval runs.
    """
    return _at(old_board, pointer) is _MISSING and _at(new_board, pointer) is not _MISSING


def reapprove_refusals(old_board, new_board, paths):
    """Why this diff may not be re-approved, as printable lines. Empty means it may."""
    bad = []
    old_ids = [s.get("id") for s in old_board.get("sections", [])]
    new_ids = [s.get("id") for s in new_board.get("sections", [])]
    if old_ids != new_ids:
        gone = [i for i in old_ids if i not in new_ids]
        fresh = [i for i in new_ids if i not in old_ids]
        bad.append("the section list moved" + (f" — removed {', '.join(gone)}" if gone else "")
                   + (f", added {', '.join(fresh)}" if fresh else "")
                   + ": a section is a question on the board, not wording")
    _, edited = stats_change(old_board, new_board)
    for sid in edited:
        bad.append(f"section {sid}: a `stats` row was added or edited — a figure and its source "
                   "are what the breeder approved; only removing a whole row is wording")
    for p in paths:
        # A `stats` pointer that survived stats_change() is a row REMOVAL reported by index,
        # which is the one allowed shape; anything real about stats was caught just above.
        if "/stats/" in p or p.endswith("/stats"):
            continue
        for frag, what in REAPPROVE_REFUSED:
            if frag not in p:
                continue
            if frag == "/source" and _source_is_purely_added(old_board, new_board, p):
                continue
            bad.append(f"{p}: {what} may not move in a re-approval — re-board the page")
    return bad


def apply_reapproval(board, reason, old_board, now, ont, live=SKIP_LIVE, boards=None):
    """The record after a controller's re-approval. Pure, like apply_approval(): it writes
    nothing and raises before anything moves. `ont`, the ontology the new-page rules read, is
    passed in rather than loaded; reapprove_main() passes the committed one, which a
    re-approval never moves. (On a new-family page those rules may still read sibling boards
    and image files, exactly as they do in apply_approval().)

    `old_board` is the record as of the commit whose hash the approval currently carries —
    the baseline the diff is taken against and the proof that this record WAS approved as it
    stood. Everything the breeder answered is copied through untouched; only the hash, the
    stamp and the log move."""
    approval = board.get("approval")
    if not isinstance(approval, dict) or not approval.get("record_hash"):
        raise PB.BoardError("no approval on this record — there is nothing to re-approve")
    if board["meta"]["status"] not in ("approved", "built"):
        raise PB.BoardError(
            f"meta.status is {board['meta']['status']!r} — re-approval is for a record that was "
            "already approved; a draft is approved the ordinary way")
    if not (reason or "").strip():
        raise PB.BoardError("--reason is required: a re-approval nobody explained is a hand-stamped hash")
    if not PB.approval_matches(old_board):
        raise PB.BoardError(
            "the baseline record does not match its own approval — the diff would be taken "
            "against a record that was never approved as it stood")
    paths = json_pointer_diff(_hashed_body(old_board), _hashed_body(board))
    if not paths:
        raise PB.BoardError("nothing inside record_hash has changed — this record needs no re-approval")
    refusals = reapprove_refusals(old_board, board, paths)
    if refusals:
        raise PB.BoardError("this diff is not a wording fix:\n  - " + "\n  - ".join(refusals))

    b = json.loads(json.dumps(board))
    # A carried ANSWER whose question was reworded is still the answer. `section_hashes`
    # records what a section looked like when it was picked, and `locked_picks()` re-asks a
    # section whose fingerprint has moved — which is right for a re-board and wrong here: a
    # re-approval has already refused every edit that could change what was chosen, so all a
    # moved fingerprint says is that somebody fixed a heading. Left alone it would make the
    # next re-board ask a question the breeder has answered, for a reason nobody could see.
    # Refreshed where a hash already exists, never invented: a record that never carried
    # fingerprints does not start now.
    fresh = {sec["id"]: PB.section_fingerprint(sec) for sec in b["sections"]}
    for holder in (b.get("approval"), b.get("approval_previous")):
        hashes = (holder or {}).get("section_hashes")
        if isinstance(hashes, dict):
            for sid in list(hashes):
                if sid in fresh:
                    hashes[sid] = fresh[sid]
    a = b["approval"]
    a["reapproved_at"] = now
    a.setdefault("reapprovals", []).append({"at": now, "reason": reason.strip(), "changed_paths": paths})
    # LAST, because `approval_previous` is inside the hash and the refresh above moved it.
    a["record_hash"] = PB.record_hash(b)
    PB.validate_board(b)
    refuse_on_new_page_rules(b, ont)
    refuse_header_collisions(b, live, boards)
    return {"board": b, "changed_paths": paths}


def _atomic_write(path, text):
    """Write through a sibling temp file and rename over the target. A half-written
    component ledger is worse than an unwritten one: the next page reads it to learn what
    it may not claim."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # A unique temp name per write: two runs (or two approvals in one tree) sharing one
    # `<name>.tmp` would have the second clobber the first mid-write.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=path.name + ".", suffix=".tmp", delete=False) as fh:
        fh.write(text)
        tmp = pathlib.Path(fh.name)
    try:
        os.replace(tmp, path)
    except OSError:
        tmp.unlink(missing_ok=True)          # a failed write leaves no orphan beside the target
        raise


def _json_text(doc):
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="board_approve.py", description="apply a board approval")
    p.add_argument("slug")
    p.add_argument("--canvas-dir", default=None,
                   help="artboard directory (default: docs/design/board-<slug> when it exists)")
    p.add_argument("--reapprove", action="store_true",
                   help="re-approve an already-approved record after a post-approval WORDING fix: "
                        "keeps every pick, recomputes record_hash, logs the reason and the "
                        "JSON-pointer diff. Refuses a diff that touches a pick, a menu, a figure "
                        "or a section id.")
    p.add_argument("--reason", default="",
                   help="required with --reapprove: why the record was edited after approval")
    return p.parse_args(sys.argv[1:] if argv is None else argv)


def baseline_board(slug, ref="HEAD"):
    """The record as `ref` has it — the state whose hash the current approval carries.

    Read from git rather than from a backup file: the committed record is the only copy
    whose approval is known to have covered it, and a re-approval that took its diff against
    anything else would be measuring against a record nobody signed."""
    import subprocess
    rel = f"data/boards/{PB.slug_file(slug)}.json"
    try:
        raw = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=PB.ROOT, check=True,
                             capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise PB.BoardError(f"cannot read {rel} at {ref}: {getattr(e, 'stderr', e)}") from None
    return json.loads(raw)


def reapprove_main(slug):
    """`--reapprove`: stamp, log, write. One document — the ledger and the ontology cannot
    move, because the picks and the entities they are derived from cannot."""
    import datetime
    a = parse_args()
    board = PB.load_board(slug)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = apply_reapproval(board, a.reason, baseline_board(slug), now, PB.load_ontology(),
                           live=PB.live_headings(), boards=PB.load_all_boards())
    # The ledger records what the TUPLE and the H6 prefixes spend. Neither can move under a
    # wording fix — but a heading edit is how an H6 prefix WOULD move, so it is checked
    # rather than assumed: a re-approval that silently desynced the ledger would hand the
    # next page a component the ledger still thinks is free.
    ledger = PB.load_ledger()
    was = (ledger.get("pages") or {}).get(slug)
    if was is not None and ledger_entry(out["board"]) != was:
        raise PB.BoardError(
            "this edit moves the page's ledger row (its tuple or its spent H6 prefixes) — "
            "that is a component claim, not wording; re-board the page")
    _atomic_write(PB.board_path(slug), _json_text(out["board"]))
    print(f"re-approved {slug} at {now} — {len(out['changed_paths'])} hashed path(s) moved:")
    for path in out["changed_paths"]:
        print(f"  {path}")
    print(f"  reason: {a.reason.strip()}")


def main():
    a = parse_args()                                  # argparse itself exits 2 on a bad invocation
    slug = a.slug
    if a.reapprove:
        try:
            PB.slug_file(slug)
            reapprove_main(slug)
        except (PB.BoardError, OSError) as e:
            print(f"board-approve ERROR {e}")
            sys.exit(2)
        return
    try:
        # Before any path is built: a slug that is not a slug names a file the caller
        # never asked for, and the gate refuses it the same way.
        stem = PB.slug_file(slug)
    except PB.BoardError as e:
        print(f"board-approve ERROR {e}")
        sys.exit(2)
    if a.canvas_dir is not None:
        canvas_dir = pathlib.Path(a.canvas_dir)       # named but absent is a BoardError, not a skip
    else:
        default = PB.ROOT / "docs" / "design" / ("board-" + stem)
        canvas_dir = default if default.exists() else None

    inbox_path = PB.ROOT / "data" / "boards" / "inbox" / (stem + ".json")
    if not inbox_path.exists():
        print(f"board-approve ERROR no approval at {inbox_path} — run the Artifact read_db step first")
        sys.exit(2)
    try:
        inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
        inbox = inbox.get("data", inbox) if isinstance(inbox, dict) else inbox   # read_db may wrap it
        before = PB.load_board(slug)
        boards = PB.load_all_boards()
        out = apply_approval(before, inbox, PB.load_ontology(), PB.load_ledger(), canvas_dir,
                             live=PB.live_headings(), boards=boards)
        shares = rule16_refusals(before, out["board"], boards)
        if shares:
            raise PB.BoardError("this approval would give two pages one arrangement:\n  - "
                                + "\n  - ".join(shares))
        # PB.save_board() guards this, but the board's write has to be ordered with the
        # other two, so the guard is restated here and the write is done below.
        if out["board"]["meta"]["slug"] != slug:
            raise PB.BoardError(f"slug mismatch: approving {slug} but the record says {out['board']['meta']['slug']}")
        PB.validate_board(out["board"])
        # Serialise all three BEFORE replacing any of them, then replace ledger → ontology
        # → board: the board is stamped approved only once the claims it makes are recorded.
        writes = [(PB.LEDGER, _json_text(out["ledger"])),
                  (PB.ONTOLOGY, _json_text(out["ontology"])),
                  (PB.board_path(slug), _json_text(out["board"]))]
        for path, text in writes:
            _atomic_write(path, text)
    except (PB.BoardError, OSError) as e:
        print(f"board-approve ERROR {e}")
        sys.exit(2)

    for sid, field, old, new in out["changed"]:
        print(f"  write-back {sid}.{field}: {old!r} → {new!r}")
    print(f"approved {slug} at {out['board']['approval']['approved_at']} — "
          f"{len(out['board']['approval']['picks'])} picks, {len(out['changed'])} text write-backs, "
          f"ledger row {out['ledger']['pages'][slug]}, {len(out['promoted'])} PROPOSED→ASSERTED")


if __name__ == "__main__":
    main()
