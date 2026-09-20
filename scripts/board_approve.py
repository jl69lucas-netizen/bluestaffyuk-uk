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
SHAPE_TUPLE_AXIS = {"hero": "hero", "faq": "faq", "dial": "dial", "sheet": "rail"}
# The mobile section sheet reuses the `rail` axis: both are the page's secondary
# navigation chrome, and the ledger has no eighth axis to give it.
SHAPE_TUPLE_SET = {"takeaways": "takeaway"}          # the one axis that holds a set
# `toc` is not a picked section on any board: every rebuilt page mounts the one kit page
# nav, so the axis records that fixed component instead of a sentinel.
FIXED_TOC = "pagenav-c"
# Shapes that render SECTION content rather than a page-level shell. They are deliberately
# not tuple axes — the ledger asks how a page's chrome is combined, and a review mode or a
# puppy grid is not chrome. `table` stays an axis with no shape feeding it: no board offers
# a table section yet, and the axis is kept so one can be added without a schema change.
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


def apply_approval(board, inbox, ont, ledger, canvas_dir=None):
    """The board, ledger and ontology as they stand after this approval. Pure: it reads
    nothing but its arguments and writes nothing — raise here and the files on disk are
    untouched."""
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
    return {"board": b, "ledger": led, "ontology": o, "changed": changed, "promoted": promoted}


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
    return p.parse_args(sys.argv[1:] if argv is None else argv)


def main():
    a = parse_args()                                  # argparse itself exits 2 on a bad invocation
    slug = a.slug
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
        out = apply_approval(PB.load_board(slug), inbox, PB.load_ontology(), PB.load_ledger(), canvas_dir)
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
