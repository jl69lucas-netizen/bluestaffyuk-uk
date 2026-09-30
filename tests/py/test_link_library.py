"""scripts/link_library.py — the one strict reader of the external-link library's Rows table.

Both readers of the table use it: ontology_seed.library_rows (organisations and laws) and
link_diversity.library_source_types (the Source type column). A row is read by its header's
column NAMES, so a column added anywhere never shifts the read, and a row whose cell count is
not the header's stops the run instead of moving a value into the wrong cell.
"""
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import pageboard as PB         # noqa: E402
import link_library as LL      # noqa: E402
import link_diversity as LD    # noqa: E402

HEADER = ("| URL | Host | What it is | First page using it | Verified | Source type |\n"
          "|---|---|---|---|---|---|\n")
RSPCA = "| https://www.rspca.org.uk/a | rspca.org.uk | RSPCA advice | `/` | 2026-09-24 · 200 | welfare |\n"
PDSA_SHORT = "| https://www.pdsa.org.uk/b | pdsa.org.uk | PDSA advice | `/` | 2026-09-24 · 200 |\n"


def _lib(tmp_path, text, name="lib.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_rows_are_dicts_keyed_by_header_name(tmp_path):
    p = _lib(tmp_path, "# lib\n\n" + HEADER + RSPCA)
    assert LL.library_table(p) == [{
        "URL": "https://www.rspca.org.uk/a", "Host": "rspca.org.uk", "What it is": "RSPCA advice",
        "First page using it": "`/`", "Verified": "2026-09-24 · 200", "Source type": "welfare"}]


def test_a_column_added_anywhere_is_read_by_name(tmp_path):
    p = _lib(tmp_path, "| URL | Notes | Host | What it is | First page using it | Verified | Source type |\n"
                       "|---|---|---|---|---|---|---|\n"
                       "| https://www.rspca.org.uk/a | a note | rspca.org.uk | RSPCA advice | `/` | x | welfare |\n")
    (row,) = LL.library_table(p)
    assert (row["Host"], row["Source type"], row["Notes"]) == ("rspca.org.uk", "welfare", "a note")


def test_a_mixed_width_table_raises_naming_the_line(tmp_path):
    p = _lib(tmp_path, "# lib\n\n" + HEADER + RSPCA + PDSA_SHORT)
    with pytest.raises(PB.BoardError, match=r"line 6 has 5 cells.*header has 6"):
        LL.library_table(p)


def test_a_stray_pipe_in_the_prose_raises(tmp_path):
    p = _lib(tmp_path, HEADER + RSPCA.replace("RSPCA advice", "RSPCA | advice"))
    with pytest.raises(PB.BoardError, match=r"line 3 has 7 cells"):
        LL.library_table(p)


def test_a_url_row_with_no_header_raises(tmp_path):
    p = _lib(tmp_path, RSPCA)
    with pytest.raises(PB.BoardError, match="no header"):
        LL.library_table(p)


def test_the_header_ends_with_its_table(tmp_path):
    """A blank line ends the table; a URL row after it has no header in scope."""
    p = _lib(tmp_path, HEADER + RSPCA + "\n" + RSPCA)
    with pytest.raises(PB.BoardError, match="line 5.*no header"):
        LL.library_table(p)


def test_a_required_column_the_header_lacks_raises(tmp_path):
    p = _lib(tmp_path, "| URL | What it is |\n|---|---|\n| https://www.rspca.org.uk/a | RSPCA advice |\n")
    assert LL.library_table(p)[0]["What it is"] == "RSPCA advice"      # nothing required: fine
    with pytest.raises(PB.BoardError, match="line 1.*no Host column"):
        LL.library_table(p, required=("URL", "Host"))


def test_prose_and_non_url_table_lines_are_ignored(tmp_path):
    p = _lib(tmp_path, "See https://www.gov.uk/x in prose.\n\n| Code | Meaning |\n|---|---|\n| a | b |\n\n"
                       + HEADER + RSPCA)
    assert [r["URL"] for r in LL.library_table(p)] == ["https://www.rspca.org.uk/a"]


def test_a_missing_file_is_an_empty_table(tmp_path):
    assert LL.library_table(tmp_path / "absent.md") == []


def test_the_read_is_cached_by_mtime_and_picks_up_an_edit(tmp_path):
    p = _lib(tmp_path, HEADER + RSPCA)
    LL.library_table(p)
    hits = LL._table.cache_info().hits
    LL.library_table(p)
    assert LL._table.cache_info().hits == hits + 1
    p.write_text(HEADER + RSPCA + RSPCA.replace("/a", "/c"), encoding="utf-8")
    st = p.stat()
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 10_000_000))
    assert len(LL.library_table(p)) == 2


def test_a_caller_cannot_change_the_cached_rows(tmp_path):
    p = _lib(tmp_path, HEADER + RSPCA)
    LL.library_table(p)[0]["Host"] = "changed"
    assert LL.library_table(p)[0]["Host"] == "rspca.org.uk"


def test_the_default_is_resolved_at_call_time(tmp_path, monkeypatch):
    p = _lib(tmp_path, HEADER + RSPCA)
    monkeypatch.setattr(PB, "EXTERNAL_LIBRARY", p)
    assert [r["URL"] for r in LL.library_table()] == ["https://www.rspca.org.uk/a"]


def test_the_real_library_parses(tmp_path):
    rows = LL.library_table(required=("URL", "Host", "What it is", "First page using it", "Source type"))
    urls = [l.split("|")[1].strip() for l in PB.EXTERNAL_LIBRARY.read_text(encoding="utf-8").splitlines()
            if l.startswith("| http")]
    assert [r["URL"] for r in rows] == urls


def test_both_readers_share_the_strict_parser(tmp_path, monkeypatch):
    import ontology_seed as OS
    p = _lib(tmp_path, HEADER + RSPCA + PDSA_SHORT)
    with pytest.raises(PB.BoardError, match="has 5 cells"):
        LD.library_source_types(p)
    with pytest.raises(PB.BoardError, match="has 5 cells"):
        OS.library_rows(p)
