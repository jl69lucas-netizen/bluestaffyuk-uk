#!/usr/bin/env python3
"""board_gate.py <slug> [--release]
The Page Board gate: refuses to build (or release) a page whose board record is not
approved as it stands. Reads live headings from dist/ (build first). Exit 1 on any FAIL,
exit 2 when the record itself cannot be read or the invocation is wrong.
Prints its examined counts — a gate that examines nothing is not a pass
(.claude/skills/bsuk-gate-integrity/SKILL.md)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB

USAGE = "usage: board_gate.py <slug> [--release]"
FLAGS = {"--release"}


def main():
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    unknown = [a for a in flags if a not in FLAGS]
    if unknown or len(args) != 1:
        print(f"board-gate ERROR unknown option {unknown[0]}" if unknown else "board-gate ERROR one slug expected")
        print(USAGE)
        sys.exit(2)
    slug, stage = args[0], ("release" if "--release" in flags else "build")
    try:
        board = PB.load_board(slug)
        ont, ledger = PB.load_ontology(), PB.load_ledger()
        # The page's own live headings are NOT popped here: header_hits() excludes them
        # with own_live_key(), and a caller-side pop mis-keyed the homepage (slug "").
        live = PB.live_headings() if PB.DIST.exists() else {}
        f = PB.gate_findings(board, ont, ledger, live, stage=stage)
        # Working rule 16's uniqueness half needs every other record, which gate_findings()
        # (pure over one record) never reads.
        boards = PB.load_all_boards()
        f += PB.rule16_findings(board, boards)
        judged = PB.rule16_judged(boards, board)
    except PB.BoardError as e:
        print(f"board-gate ERROR {e}")
        sys.exit(2)
    n_head = len(PB.all_headings(board))
    # Every family says what it examined: an empty ledger or an empty asset list would
    # otherwise let the ledger-* checks and asset-required-missing pass on nothing.
    siblings = [p for p in ledger.get("pages", {}) if p != board["meta"]["slug"]]
    print(f"board-gate {slug} [{stage}] — {len(board['sections'])} sections, {n_head} headings, "
          f"{len(live)} live pages, {sum(len(s['entities']) for s in board['sections'])} entity refs, "
          f"{len(siblings)} ledger siblings, {len(board['assets'])} assets examined")
    # Until the component ledger records a page, the five ledger-* checks have nothing to
    # compare against. Said out loud so an empty ledger cannot be read as a clean gate.
    if not ledger.get("pages"):
        print("ledger: empty — ledger-* families examined 0, not a pass")
    # Rule 16 is judged across records, so its count is records, not this record's sections.
    print(f"rule 16: {len(judged)} records judged" if judged
          else "rule 16: 0 records judged — examined nothing, not a pass")
    for x in f:
        print(f"  {x['sev']:4s} {x['check']:24s} {x['msg']}")
    fails = [x for x in f if x["sev"] == "FAIL"]
    print(f"{len(fails)} FAIL · {len(f) - len(fails)} WARN")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
