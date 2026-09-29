"""Test helper: lay out one page's STOP 1 and STOP 2 records under a temporary repo root.

Writes, for `slug`, the query file, the research-board record and its own answers file
(batch id naming the slug and `research-board`), the outline record and its own answers file
(batch id naming the slug and `outline`), approving each stop when asked. Every path in the
records is relative to that root, as it is in the repo.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import outline_matrix as OM  # noqa: E402
import research_board as RB  # noqa: E402

FIX = ROOT / "tests/py/fixtures"


def answers(root, slug, stop, name=None):
    """An answer-board answers file for `stop` ('research-board' or 'outline')."""
    batch = f"2026-09-29-{stop}-{slug}"
    rel = f"docs/reference/answer-board/answers/{name or batch}-2026-09-29.json"
    doc = {"id": "s-fixture", "data": {"batchId": batch, "at": "2026-09-29T00:00:00Z",
           "answers": [{"key": "q01", "n": 1, "kind": "choice", "choice": "a",
                        "question": f"Approve the {stop} for {slug}?", "status": "answered",
                        "text": ""}]}}
    p = pathlib.Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc))
    return rel


def lay_out(root, slug, research_approved=True, outline_approved=True):
    root = pathlib.Path(root)
    q = json.loads((FIX / "research_board/queries.json").read_text())
    q["slug"] = slug
    qrel = f"data/queries/{slug}.json"
    (root / "data/queries").mkdir(parents=True, exist_ok=True)
    (root / qrel).write_text(json.dumps(q))
    rec = json.loads((FIX / "research_board/record.json").read_text())
    rec.update(slug=slug, queries_file=qrel, approval=None)
    if research_approved:
        rec = RB.approve(rec, answers(root, slug, "research-board"), today="2026-09-29", root=root)
    rrel = f"data/research-boards/{slug}.json"
    (root / "data/research-boards").mkdir(parents=True, exist_ok=True)
    (root / rrel).write_text(json.dumps(rec))
    out = json.loads((FIX / "outline_matrix/good.json").read_text())
    out.update(slug=slug, research_board=rrel, approval=None)
    if outline_approved:
        out = OM.approve(out, answers(root, slug, "outline"), today="2026-09-29", root=root)
    orel = f"data/outlines/{slug}.json"
    (root / "data/outlines").mkdir(parents=True, exist_ok=True)
    (root / orel).write_text(json.dumps(out))
    return {"queries": root / qrel, "research": root / rrel, "outline": root / orel}
