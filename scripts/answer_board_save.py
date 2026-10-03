#!/usr/bin/env python3
"""The answer-board receive step's marker pass: saved answers carry no source-repo vocabulary.

The breeder writes answers in her own words, and those words can name the sibling site or
paste its URLs. Saved verbatim under docs/reference/answer-board/answers/, such a file trips
`npm run check:markers` (docs/reference/ is a scanned root, and the gate has no allowlist).
The original text stays in the board's database, so the saved copy may carry a neutral label
in its place.

    python3 scripts/answer_board_save.py --neutralise <saved file>...
    python3 scripts/answer_board_save.py --check <saved file>...

`--neutralise` rewrites each file in place. Every whitespace-delimited token that carries a
marker is replaced whole: a URL by "[sibling-site page]", any other word by
"[sibling-site term]", so no half-URL is left behind. A JSON file keeps its exact layout (only
the tokens change; a token never spans a quote or a backslash, and the result must still
parse, or the file is left untouched and the run fails). A changed .md file gains one note
line saying so and where the original is. `--check` reports and changes nothing.

The markers are scripts/marker_check.py's own (imported, never copied), and every file is
re-scanned with its `hits_in()` afterwards: exit 0 only when every file is clean.

Exit: 0 clean · 1 a marker survives (or, with --check, any hit) · 2 usage, a missing file, or
a JSON file the rewrite would break.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import marker_check as MC  # noqa: E402

PAGE_LABEL = "[sibling-site page]"
TERM_LABEL = "[sibling-site term]"
NOTE = ("> {n} source-repo marker hit(s) were replaced with neutral labels so this file passes "
        "`check:markers`; the original text stays in the answer-board db.")

# A URL, with JSON's escaped `\/` slashes allowed inside it. It never crosses whitespace, a
# quote, a bracket or any other backslash, so a JSON string's syntax is never consumed.
URL = re.compile(r"""(?i)(?:https?:(?:\\?/){2}|www\.)(?:\\/|[^\s"'<>()\[\]{}\\])+""")
# Any other word: never crosses whitespace, a quote, a backslash or a bracket.
TOKEN = re.compile(r"""[^\s"'\\<>()\[\]{}]+""")
TRAIL = ".,;:!?"


def _has_marker(text):
    return MC.has_marker(text.replace("\\/", "/"))


def neutralise_text(text):
    """(new text, replacements). URLs first, whole: a URL carrying a marker becomes one
    PAGE_LABEL, so no fragment of it is left for the word rules to half-replace. Then, only
    in the text outside URLs, the spelled two-word markers (marker_check.SPELLED, its own
    flags plus re.I), then every other word that carries a marker."""
    count = 0
    out = []
    pos = 0

    def words(seg):
        nonlocal count

        def sub_term(_m):
            nonlocal count
            count += 1
            return TERM_LABEL
        for rx in MC.SPELLED.values():
            seg = re.compile(rx.pattern, rx.flags | re.I).sub(sub_term, seg)

        def sub_token(m):
            nonlocal count
            tok = m.group(0)
            core = tok.rstrip(TRAIL)
            if not _has_marker(core):
                return tok
            count += 1
            return (PAGE_LABEL if "/" in core else TERM_LABEL) + tok[len(core):]
        return TOKEN.sub(sub_token, seg)

    for m in URL.finditer(text):
        url = m.group(0)
        core = url.rstrip(TRAIL)
        out.append(words(text[pos:m.start()]))
        if _has_marker(core):
            count += 1
            out.append(PAGE_LABEL + url[len(core):])
        else:
            out.append(url)
        pos = m.end()
    out.append(words(text[pos:]))
    return "".join(out), count


def neutralise_file(path):
    """Replacements made in `path` (rewritten in place). Raises ValueError when a JSON file
    would stop parsing; the file is then left as it was."""
    path = pathlib.Path(path)
    old = path.read_text(encoding="utf-8")
    new, n = neutralise_text(old)
    if not n:
        return 0
    if path.suffix.lower() == ".json":
        try:
            json.loads(new)
        except ValueError as e:
            raise ValueError(f"{path}: the rewrite would not parse ({e}); left unchanged") from e
    elif path.suffix.lower() == ".md":
        new = new.rstrip("\n") + "\n\n" + NOTE.format(n=n) + "\n"
    path.write_text(new, encoding="utf-8")
    return n


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2 or argv[0] not in ("--neutralise", "--check"):
        print("usage: answer_board_save.py --neutralise|--check <saved file>...")
        return 2
    mode, files = argv[0], [pathlib.Path(f) for f in argv[1:]]
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        print(f"missing: {', '.join(missing)}")
        return 2
    code = 0
    for f in files:
        if mode == "--neutralise":
            try:
                n = neutralise_file(f)
            except ValueError as e:
                print(f"REFUSED {e}")
                code = 2
                continue
            print(f"{f}: {n} replaced")
        left = MC.hits_in(f)
        for line, marker, _ in left:
            print(f"  {f}:{line}  [{marker}]")
        if left:
            code = max(code, 1)
    print(f"examined {len(files)} file(s); "
          + ("clean" if code == 0 else "markers remain" if code == 1 else "refused"))
    return code


if __name__ == "__main__":
    sys.exit(main())
