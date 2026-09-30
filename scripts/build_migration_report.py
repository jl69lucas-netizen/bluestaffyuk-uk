#!/usr/bin/env python3
"""Writes docs/reports/foundation-migration.md — what came across from WordPress.

Generated rather than hand-written, because every number in it is already on disk and a
hand-copied count is a number that silently stops being true. The inputs are
`data/page-map.json` (the extractor's own record of every old URL it read: kind, word
count, images, embeds, the defects it found and the phone numbers it removed) and
`docs/reports/parity.md` (the gate that compares old body against built body). The parity
table is EMBEDDED rather than re-derived, so this report and the gate can never disagree.

The last table is the handover: every page carrying a defect or a refresh flag, which is
the work queue for projects 4 and 5 rather than anything Foundation was meant to fix.

Usage: python3 scripts/build_migration_report.py
"""
import collections
import datetime
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_CLONE = pathlib.Path("/Users/apple/bluestaffyuk-site")


def source_sha(clone=SOURCE_CLONE):
    """Short SHA of the WordPress export clone, or an honest note if it cannot be read."""
    try:
        out = subprocess.run(["git", "-C", str(clone), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return "UNREADABLE — %s" % exc
    if out.returncode != 0:
        return "UNREADABLE — %s" % (out.stderr.strip() or "git exited %d" % out.returncode)
    return out.stdout.strip()


def built_page_count(dist):
    return sum(1 for _ in pathlib.Path(dist).rglob("index.html"))


def build(root=ROOT, dist=None, today=None):
    root = pathlib.Path(root)
    dist = pathlib.Path(dist) if dist else root / "dist"
    today = today or datetime.date.today().isoformat()

    page_map = json.loads((root / "data" / "page-map.json").read_text(encoding="utf-8"))
    pages = page_map["pages"]
    puppies = json.loads((root / "data" / "puppies.json").read_text(encoding="utf-8"))
    locations = json.loads((root / "data" / "locations.json").read_text(encoding="utf-8"))
    posts = sorted((root / "src" / "content" / "blog").glob("*.md"))

    kinds = collections.Counter(p.get("kind") for p in pages)
    phone_total = sum(p.get("phone_hits", 0) or 0 for p in pages)
    built = built_page_count(dist) if dist.is_dir() else 0

    # The three pages WordPress never had. Named, not counted: "3 new index pages" invites
    # the reader to guess which, and the guess is what goes into the next project's plan.
    new_indexes = ["/uk-locations/", "/blog/", "/available-puppies/"]

    parity_path = root / "docs" / "reports" / "parity.md"
    if parity_path.exists():
        # Demoted TWO levels on the way in: parity.md is a standalone document with its own
        # H1. Pasting that under this report's "## Parity" would put a second H1 mid-page,
        # and demoting it only one level makes it an H2 — which build_report_artifact.py
        # splits on, so the artifact grew a second "Parity" card holding the same table.
        parity = "\n".join(
            ("##" + line) if line.startswith("#") else line
            for line in parity_path.read_text(encoding="utf-8").strip().splitlines())
    else:
        parity = "_docs/reports/parity.md is not on disk — run `npm run check:parity`._"

    lines = [
        "# Foundation migration report", "",
        "| | |", "| --- | --- |",
        "| Source clone | `%s` @ `%s` |" % (SOURCE_CLONE, source_sha()),
        "| Generated | %s |" % today,
        "| Generator | `scripts/build_migration_report.py` |", "",
        "Every number below is read from `data/page-map.json`, `data/*.json` and `dist/` at",
        "generation time. Nothing here is typed by hand.", "",
        "## Counts", "",
        "| What | Count |", "| --- | ---: |",
        "| Rich pages migrated | %d |" % kinds.get("rich", 0),
        "| Location pages | %d |" % len(locations),
        # `robots`, not `word_count`: ten of the seventeen stubs carry three to seven words
        # of legacy body, so a word-count test reports 7 where the site actually noindexes 17.
        # locations.json's own robots field is what the built page emits, so it is the
        # authority — the number in this report has to match what Google will be told.
        "| — of which are indexed (migrated body) | %d |"
        % sum(1 for loc in locations if "noindex" not in loc.get("robots", "")),
        "| — of which are noindexed stubs awaiting project 5 | %d |"
        % sum(1 for loc in locations if "noindex" in loc.get("robots", "")),
        "| Blog posts | %d |" % len(posts),
        "| Individual puppy pages | %d |" % len(puppies),
        "| New index pages (no WordPress original) | %d — %s |"
        % (len(new_indexes), ", ".join("`%s`" % u for u in new_indexes)),
        "| Old URLs read by the extractor | %d |" % len(pages),
        "| **Total pages built** | **%d** |" % built, "",
        "## Phone numbers removed", "",
        "The old body text published a phone number the new site does not have yet. The",
        "extractor strips every occurrence and records the count per page; `PHONE_PLACEHOLDER`",
        "stands in until project 6 provisions a number, and `scripts/placeholder_check.py`",
        "refuses to let that placeholder reach a release build.", "",
        "**%d occurrence(s) removed across %d page(s).**"
        % (phone_total, sum(1 for p in pages if p.get("phone_hits", 0))), "",
    ]

    by_kind = collections.Counter()
    for p in pages:
        if p.get("phone_hits", 0):
            by_kind[p.get("kind")] += p["phone_hits"]
    if by_kind:
        lines += ["| Page kind | Occurrences removed |", "| --- | ---: |"]
        lines += ["| %s | %d |" % (k, n) for k, n in sorted(by_kind.items())]
        lines += [""]

    lines += ["## Parity", "",
              "Embedded verbatim from `docs/reports/parity.md`, the gate that produced it.",
              "", parity, "",
              "## Flags for projects 4 and 5", "",
              "Pages the extractor flagged. These are properties of the WordPress content,",
              "not defects introduced by the migration: Foundation's job was to carry them",
              "across unchanged, and fixing them is the content work projects 4 and 5 own.",
              "A page with neither a defect nor a refresh flag is omitted.", ""]

    flagged = [p for p in pages if p.get("defects") or p.get("refresh_flags")]
    if flagged:
        lines += ["| URL | Kind | Words | Defects | Refresh flags |",
                  "| --- | --- | ---: | --- | --- |"]
        for p in sorted(flagged, key=lambda p: p["url"]):
            lines.append("| `%s` | %s | %d | %s | %s |" % (
                p["url"], p.get("kind", "?"), p.get("word_count", 0) or 0,
                ", ".join("`%s`" % d for d in p.get("defects", [])) or "—",
                ", ".join("`%s`" % f for f in p.get("refresh_flags", [])) or "—"))
        lines += ["", "%d of %d pages flagged." % (len(flagged), len(pages)), ""]
    else:
        lines += ["No page carries a defect or a refresh flag.", ""]

    # PAGES, not occurrences. `old-price` appears once per price found, so counting the
    # list entries said "61 pages" for a flag that is on 12 — and the handover table is
    # read as a work queue, where the unit is the page somebody has to open.
    counts = collections.Counter()
    for p in flagged:
        for name in {"defect: %s" % d for d in p.get("defects", [])} | \
                    {"flag: %s" % f.split(":")[0] for f in p.get("refresh_flags", [])}:
            counts[name] += 1
    if counts:
        lines += ["### Flags by kind", "",
                  "Counted in PAGES carrying the flag, not occurrences.", "",
                  "| Flag | Pages |", "| --- | ---: |"]
        lines += ["| `%s` | %d |" % (k, n) for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
        lines += [""]

    return "\n".join(lines)


def main(root=ROOT):
    root = pathlib.Path(root)
    out = root / "docs" / "reports" / "foundation-migration.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    text = build(root)
    out.write_text(text, encoding="utf-8")
    print("%s — %d bytes, %d lines" % (out, len(text), text.count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
