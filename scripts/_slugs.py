"""Shared slug-resolution helpers for the audit scripts.

Convention (matches final_page_audit.py / evidence_audit.py): `index` (and
"" / "/") means EXACTLY dist/index.html; any other slug means EXACTLY
dist/<slug>/index.html (slug may be nested, e.g. available/roys — nested
slugs keep their full path). Deliberately NOT substring matching — see
tests/test_audit_slug_resolution.py for the history of each script's bug.
"""


def select_pages(paths, slugs, dist="dist"):
    """Resolve slugs to built page paths. `paths` is the list of candidate
    built page paths (as strings); `dist` is the dist-root prefix used to
    build the target paths."""
    if not slugs:
        return paths
    targets = set()
    for s in slugs:
        if s in ("index", "", "/"):
            targets.add(f"{dist}/index.html")
        else:
            targets.add(f"{dist}/{s.strip('/')}/index.html")
    return [p for p in paths if p in targets]


def page_key(path, dist):
    """Slug key for a built page: dist/index.html -> "index";
    dist/<slug>/index.html -> "<slug>" (nested slugs, e.g.
    dist/available/roys/index.html -> "available/roys", keep their full path).
    `path` and `dist` are pathlib.Path objects."""
    rel = path.relative_to(dist).as_posix()
    if rel == "index.html":
        return "index"
    return rel[: -len("/index.html")]
