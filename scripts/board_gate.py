#!/usr/bin/env python3
"""board_gate.py <slug> [--release]  |  board_gate.py --all
The Page Board gate: refuses to build (or release) a page whose board record is not
approved as it stands. Reads live headings from dist/ (build first). Exit 1 on any FAIL,
exit 2 when the record itself cannot be read or the invocation is wrong.
Prints its examined counts — a gate that examines nothing is not a pass
(.claude/skills/bsuk-gate-integrity/SKILL.md).

`--all` (`npm run check:boards`, in check:all) runs the build-stage gate over EVERY page in
data/facts/rebuilt.json — the Asset Gate and the approval hash stop being a step somebody
has to remember. A rebuilt page whose board record is missing or unreadable is a FAIL there
(`board-unreadable`), never a skip: no page is built without an approved board. dist/, the
ontology, the ledger and every record are read once for the whole run; an empty dist/ is a
precondition error (exit 2), so build first."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB
import outline_matrix as OM

USAGE = "usage: board_gate.py <slug> [--release]  |  board_gate.py --all"
FLAGS = {"--release", "--all"}


def outline_findings(slug):
    """STOP 2 (docs/reference/page-run.md row 9): a new page's outline record,
    data/outlines/<slug>.json, is approved as it stands before its page board counts. The
    twelve pages built before project 5 have none and are not judged on it."""
    if not PB.FR.is_new_page(slug):
        return []
    refusal = OM.approval_refusal(slug)
    return [{"sev": "FAIL", "check": "outline-unapproved", "msg": refusal}] if refusal else []


def judge(slug, stage, ont, ledger, live, boards):
    """(fail count, printed lines) for one record. Raises PB.BoardError when the record
    cannot be read."""
    board = PB.load_board(slug)
    # The page's own live headings are NOT popped here: header_hits() excludes them
    # with own_live_key(), and a caller-side pop mis-keyed the homepage (slug "").
    f = PB.gate_findings(board, ont, ledger, live, stage=stage)
    # Working rule 16's uniqueness half needs every other record, which gate_findings()
    # (pure over one record) never reads.
    f += PB.rule16_findings(board, boards)
    f += outline_findings(slug)
    judged = PB.rule16_judged(boards, board)
    n_head = len(PB.all_headings(board))
    # Every family says what it examined: an empty ledger or an empty asset list would
    # otherwise let the ledger-* checks and asset-required-missing pass on nothing.
    siblings = [p for p in ledger.get("pages", {}) if p != board["meta"]["slug"]]
    lines = [f"board-gate {slug} [{stage}] — {len(board['sections'])} sections, {n_head} headings, "
             f"{len(live)} live pages, {sum(len(s['entities']) for s in board['sections'])} entity refs, "
             f"{len(siblings)} ledger siblings, {len(board['assets'])} assets examined"]
    # Until the component ledger records a page, the five ledger-* checks have nothing to
    # compare against. Said out loud so an empty ledger cannot be read as a clean gate.
    if not ledger.get("pages"):
        lines.append("ledger: empty — ledger-* families examined 0, not a pass")
    # Rule 16 is judged across records, so its count is records, not this record's sections.
    lines.append(f"rule 16: {len(judged)} records judged" if judged
                 else "rule 16: 0 records judged — examined nothing, not a pass")
    for x in f:
        lines.append(f"  {x['sev']:4s} {x['check']:24s} {x['msg']}")
    fails = [x for x in f if x["sev"] == "FAIL"]
    lines.append(f"{len(fails)} FAIL · {len(f) - len(fails)} WARN")
    return len(fails), lines


def run_all():
    """Exit code of the build-stage gate over every rebuilt page."""
    slugs = sorted(PB.rebuilt_slugs())
    if not slugs:
        print("board-gate --all: examined 0 rebuilt pages — data/facts/rebuilt.json is empty "
              "or unreadable, which is not a pass")
        return 1
    try:
        ont, ledger = PB.load_ontology(), PB.load_ledger()
        live = PB.live_headings() if PB.DIST.exists() else {}
        boards = PB.load_all_boards()
    except PB.BoardError as e:
        print(f"board-gate ERROR {e}")
        return 2
    # An empty dist/ is a precondition error, not a verdict: header collisions and
    # min-h5-h6 would be judged against nothing.
    if not live:
        print("board-gate --all: dist/ has 0 live pages — run npm run -s build first")
        return 2
    failed = []
    for slug in slugs:
        try:
            n, lines = judge(slug, "build", ont, ledger, live, boards)
        except PB.BoardError as e:
            # Missing, schema-invalid or inconsistent: the record could not be judged.
            n, lines = 1, [f"board-gate {slug} [build]", f"  {'FAIL':4s} {'board-unreadable':24s} {e}"]
        if n:
            failed.append(slug)
            print("\n".join(lines))
        else:
            print(lines[0].replace(" examined", " examined — 0 FAIL", 1))
    print(f"board-gate --all: examined {len(slugs)} rebuilt pages against {len(live)} live pages; "
          f"{len(failed)} failed{': ' + ', '.join(failed) if failed else ''}")
    return 1 if failed else 0


def main():
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    unknown = [a for a in flags if a not in FLAGS]
    if flags == ["--all"] and not args:
        sys.exit(run_all())
    if unknown or len(args) != 1 or "--all" in flags:
        print(f"board-gate ERROR unknown option {unknown[0]}" if unknown else
              "board-gate ERROR --all takes no slug and no other option" if "--all" in flags else
              "board-gate ERROR one slug expected")
        print(USAGE)
        sys.exit(2)
    slug, stage = args[0], ("release" if "--release" in flags else "build")
    try:
        ont, ledger = PB.load_ontology(), PB.load_ledger()
        live = PB.live_headings() if PB.DIST.exists() else {}
        n, lines = judge(slug, stage, ont, ledger, live, PB.load_all_boards())
    except PB.BoardError as e:
        print(f"board-gate ERROR {e}")
        sys.exit(2)
    print("\n".join(lines))
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
