"""Turn a question sheet into an answer-board batch (spec §5 and §7).

The batch JSON is what Claude writes to the board's `db` as `batches/<id>` with the
ArtifactData tool (`set`, `file_path` = the file this writes). The file is kept in the repo
as the record of what was asked.

    python3 scripts/answer_board_batch.py <sheet.md> --project <name> [--date YYYY-MM-DD]
        [--batch-id <id>] [--out-dir <dir>]
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from answer_sheet import SheetError, parse_sheet  # noqa: E402

OUT_DIR = ROOT / "docs" / "reference" / "answer-board" / "batches"
MAX_BYTES = 256 * 1024  # the db's per-document cap
MAX_TITLE = 120  # the Send note carries the title and must stay well under 4 KiB


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60].rstrip("-") or "batch"


def make_batch(sheet, batch_id, project, asked_at):
    questions = [
        {"n": q["n"], "key": q["key"], "section": i, "question": q["question"],
         "context": q["context"], "where": q["where"], "kind": q["kind"], "options": q["options"]}
        for i, s in enumerate(sheet["sections"]) for q in s["questions"]]
    return {"id": batch_id, "title": sheet["title"], "project": project, "askedAt": asked_at,
            "intro": sheet["preamble"], "status": "open", "receivedAt": "", "receivedCommit": "",
            "sections": [{"title": s["title"], "lead": s["lead"]} for s in sheet["sections"]],
            "questions": questions}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Make an answer-board batch from a question sheet.")
    ap.add_argument("sheet")
    ap.add_argument("--project", required=True, help="e.g. site-content, project-5, tools")
    ap.add_argument("--date", help="YYYY-MM-DD; default today (UTC)")
    ap.add_argument("--batch-id")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    a = ap.parse_args(argv)
    if a.date:
        try:
            datetime.date.fromisoformat(a.date)
        except ValueError:
            ap.error(f"--date must be YYYY-MM-DD, got {a.date!r}")
    path = pathlib.Path(a.sheet)
    try:
        sheet = parse_sheet(path.read_text(encoding="utf-8"))
    except (SheetError, OSError) as e:
        print(f"{path}: {e}", file=sys.stderr)
        return 1
    if len(sheet["title"]) > MAX_TITLE:
        print(f"{path}: the sheet title is over {MAX_TITLE} characters; shorten it", file=sys.stderr)
        return 1
    if a.date:
        date, asked_at = a.date, f"{a.date}T12:00:00Z"
    else:
        now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        date, asked_at = now.date().isoformat(), now.strftime("%Y-%m-%dT%H:%M:%SZ")
    batch_id = a.batch_id or f"{date}-{slug(sheet['title'])}"
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", batch_id):
        ap.error("batch id must be a lowercase slug")
    batch = make_batch(sheet, batch_id, a.project, asked_at)
    body = json.dumps(batch, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if len(body.encode("utf-8")) >= MAX_BYTES:
        print(f"{path}: the batch is over 256 KiB; split the sheet", file=sys.stderr)
        return 1
    out = pathlib.Path(a.out_dir) / f"{batch_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    choice = sum(q["kind"] == "choice" for q in batch["questions"])
    print(f"{out} — {len(batch['questions'])} questions ({choice} choice), batch {batch_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
