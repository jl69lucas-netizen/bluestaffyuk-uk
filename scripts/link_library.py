"""link_library — the one strict reader of the Rows table in docs/reference/external-link-library.md.

Two scripts read the table: ontology_seed.library_rows (the organisation behind each host and
the laws some rows name) and link_diversity.library_source_types (the `Source type` column).
Both go through `library_table()`, so the table has one set of parsing rules:

- A table starts at a header line whose first cell is `URL` and ends at the first line that
  is not a table line (`|…`). A row is read by its header's column NAMES, so a column added
  anywhere in the table is ignored by a reader that does not ask for it.
- A URL-led row (`| http…`) whose cell count is not its header's — a stray `|` in its prose, a
  missing cell — raises BoardError naming the line, instead of moving a value into the wrong
  column. So does a URL row with no header in scope, and a header that lacks a column the
  caller names in `required`.
- Prose, the `|---|` rule line and any table whose header does not start with `URL` are
  ignored. `pageboard.library_urls()` still greps every URL in the file (prose included) for
  the allowlist; this module reads the table only.

Read once per (path, mtime), as pageboard.library_urls is, and the default path is resolved
at CALL time so a test can repoint `pageboard.EXTERNAL_LIBRARY`.

`pageboard` imports `family_rules`, which imports `link_diversity`, which imports this module,
so `pageboard` may be half-initialised while this file loads: every `PB.` reference is inside
a function.
"""
import functools
import pathlib
import re

import pageboard as PB

URL_ROW = re.compile(r"^\|\s*https?://")


def _cells(line):
    """The cells of a `| a | b |` table line, stripped; the outer pipes are not cells."""
    body = line.strip()
    body = body[1:-1] if body.endswith("|") else body[1:]
    return [c.strip() for c in body.split("|")]


@functools.lru_cache(maxsize=16)
def _table(path, _mtime):
    """((header line number, header), ((header index, row cells), …)) — or raises."""
    headers, rows, header = [], [], None
    for n, line in enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("|"):
            header = None
            continue
        cells = _cells(line)
        if cells[0] == "URL":
            headers.append((n, tuple(cells)))
            header = len(headers) - 1
            continue
        if not URL_ROW.match(line):
            continue
        if header is None:
            raise PB.BoardError(f"{path}: line {n} is a URL row with no header row above it")
        width = len(headers[header][1])
        if len(cells) != width:
            raise PB.BoardError(f"{path}: line {n} has {len(cells)} cells but the header has {width} "
                                "— a stray or missing `|`")
        rows.append((header, tuple(cells)))
    return tuple(headers), tuple(rows)


def library_table(path=None, required=("URL",)):
    """Every URL row of the library's table(s), in file order, as {column name: cell}.

    `required` names the columns every header must carry; a header without one raises. A
    missing file is an empty table (as library_urls treats it): the caller decides whether
    that is a fault. Each call returns fresh dicts, so a caller cannot change the cache."""
    p = pathlib.Path(PB.EXTERNAL_LIBRARY if path is None else path)
    if not p.exists():
        return []
    headers, rows = _table(str(p), p.stat().st_mtime_ns)
    for n, header in headers:
        lacking = [c for c in required if c not in header]
        if lacking:
            raise PB.BoardError(f"{p}: line {n}: the Rows-table header has no {', '.join(lacking)} column")
    return [dict(zip(headers[h][1], cells)) for h, cells in rows]
