#!/usr/bin/env python3
"""pull_design_picks.py — picks-board database rows → data/design/picks.json.

Operator step first (a Python script cannot call the Artifact tool): read every
`picks/<component>` doc and the `picks/mark` doc from the picks board's database with the
ArtifactData tool into data/design/inbox/picks.json as {"picks/<id>": {...}, ...}.
Then: python3 scripts/pull_design_picks.py
Refuses (exit 2) unless all thirteen components and the mark are present.
"""
import argparse, datetime as dt, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default=str(ROOT / "data/design/inbox/picks.json"))
    ap.add_argument("--out", default=str(ROOT / "data/design/picks.json"))
    a = ap.parse_args(argv)
    ids = [r["id"] for r in json.loads((ROOT / "data/design/components.json").read_text())]
    rows = json.loads(pathlib.Path(a.inbox).read_text())
    picks, bad = {}, []
    for i in ids:
        r = rows.get(f"picks/{i}")
        if not r or r.get("variant") not in list("abcde"):
            bad.append(i); continue
        picks[i] = {"variant": r["variant"], "note": (r.get("note") or "").strip(), "at": r.get("at"), "by": r.get("by")}
    mark = (rows.get("picks/mark") or {}).get("variant")
    if mark not in list("abcde"):
        bad.append("mark")
    if bad:
        print(f"missing or invalid picks: {', '.join(bad)}")
        return 2
    out = {"pulled_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "mark": mark, "picks": picks}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {len(picks)} picks + mark {mark} to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
