#!/usr/bin/env python3
"""strategy_cite_check.py — a strategy may quote only figures its listed sources contain.

  python3 scripts/strategy_cite_check.py STRATEGY.md [--root DIR]
      exit 0 every figure found · 1 problems (listed) · 2 bad usage, or the strategy is
      missing, not a file, unreadable or not UTF-8. (Unlike gap_matrix.py, which keeps 2 for
      usage and 6 for bad input, this check has one input, so 2 covers both.)

Checked sections: `## Recommendation…` and `## Concrete Artifact…` / `## Concrete Artefact…`
(case-blind, `##` then a space or tab, an optional `5.` number, any trailing text such as
`:` or `(Strategy A)`). `###` subheadings stay inside their section.

A figure is a whole number in one of these shapes, read the same way in the strategy and in
every source: an N/M count (`7/12`, `7/12-competitor`), a percentage (`58%`, `40 %`), a
decimal (`0.75`), a comma-thousands number (`1,200`), a whole number of two digits or more,
or any number with a `k` or `x` multiplier (`40k`, `£12k`, `2.5x`, `3x`). A number glued to
a unit or word gives its numeric core (`12-page`, `12th`, `40/mo`, `-12` → 12; the sign is
dropped); a hyphen or en-dash range gives both ends (`20-39%` → 20 and 39%).
Figures are compared as tokens, never as substrings: thousands commas are ignored
(`1,500` = `1500`), `%`, `k` and `x` must match (`40k` needs `40k`, `39%` needs `39%`),
other units are not compared (`12-page` needs only `12`). A source's N/M also supplies N and
M on their own, so "of 12 competitors" may cite `7/12`; digits are never split otherwise.

Not figures: single digits without %/k/x, 28 (the locked city count), years 1900–2099,
dates (`2026-09-24`, `24/09/2026`), clock times (`10:30`), ordered-list markers (`10.`),
anything in backticks or a fenced code block, link URLs (the link text is still checked)
and HTML comments. Dates, times and URLs are ignored on the source side too.

Each figure must be a token of at least one file listed under `## Sources` (case-blind,
trailing text allowed) — every backticked path and every `[text](path)` link on a `-`, `*`,
`+` or `1.` bullet. Every listed file must exist, be readable UTF-8 text, resolve inside
`docs/research/` or `data/` under --root (research sources only) and not be the strategy
itself. The strategy agent quotes a source's figure exactly as the source writes it.

The last line says what was examined:
  cite-check: strategy.md: 2 sources, 5 figures checked, 0 problems

Spec: docs/superpowers/specs/2026-09-23-competitor-intel-design.md §9.
"""
import argparse
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXIT_OK, EXIT_FAIL, EXIT_BAD_INPUT = 0, 1, 2
RESEARCH_DIRS = ("docs/research", "data")
ALWAYS_TRUE = {"28"}

HEADING = re.compile(r"^##[ \t]+(?:\d+[.)]?[ \t]+)?(.*?)[ \t#]*$")
CHECKED = re.compile(r"(?:recommendation|concrete artifact|concrete artefact)", re.I)
SOURCES = re.compile(r"sources\b", re.I)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
COMMENT = re.compile(r"<!--.*?-->", re.S)
CODE = re.compile(r"(`+)(?:(?!\1).)+?\1|`+")
LINK = re.compile(r"\[([^\]]*)\]\(\s*<?([^)\s>]*)>?(?:\s+[\"'(][^)]*)?\)")
URL = re.compile(r"\b(?:https?|ftp)://\S+|\bwww\.\S+", re.I)
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")
TIME = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
LIST_MARKER = re.compile(r"^(\s*)\d+[.)](?=\s)")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
BACKTICKED = re.compile(r"`([^`]+)`")
_NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
TOKEN = re.compile(
    r"(?<![\w.,/])(?<![A-Za-z_][-\u2013])"      # not glued to a word, a decimal or a path
    r"(?:(?P<n>\d+)/(?P<m>\d+)(?![\d/]|[.,]\d)"  # N/M
    rf"|(?P<core>{_NUM})"
    r"(?:[ ]?(?P<pct>%)|(?P<mul>[kKxX\u00d7])(?![A-Za-z0-9]))?"
    r"(?![\d]|[.,]\d|/\d))",
    re.A)


def _ascii_digits(text):
    """Other scripts' decimal digits (full-width, Arabic-Indic…) become 0-9."""
    return "".join(str(unicodedata.decimal(c)) if c.isdecimal() and not c.isascii() else c
                   for c in text)


def _common(text):
    """The cleaning both sides share: link URLs, bare URLs, dates and clock times go."""
    text = LINK.sub(lambda m: m.group(1), _ascii_digits(text))
    return TIME.sub(" ", DATE.sub(" ", URL.sub(" ", text)))


def _tokens(text):
    """(canonical token, is it a figure, N/M parts, as written) for every number in text."""
    for m in TOKEN.finditer(text):
        if m.group("n"):
            yield (f"{m.group('n')}/{m.group('m')}", True, (m.group("n"), m.group("m")),
                   m.group(0))
            continue
        raw = m.group("core")
        core = raw.replace(",", "")
        suffix = "%" if m.group("pct") else ("x" if m.group("mul") in ("x", "X", "\u00d7")
                                             else "k" if m.group("mul") else "")
        plain_int = not suffix and "," not in raw and "." not in raw
        figure = not (plain_int and (len(core) < 2 or core in ALWAYS_TRUE
                                     or 1900 <= int(core) <= 2099 and len(core) == 4))
        yield core + suffix, figure, (), m.group(0)


def figures(text):
    """The figures a line of strategy text quotes, as canonical tokens, in order."""
    return [t for t, _ in _figures_written(text)]


def _figures_written(text):
    return [(t, raw) for t, is_figure, _, raw in _tokens(_common(text)) if is_figure]


def source_tokens(text):
    """Every token a source supplies; an N/M also supplies N and M."""
    out = set()
    for t, _, parts, _ in _tokens(_common(text)):
        out.add(t)
        out.update(parts)
    return out


def _plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _show(s, limit=300):
    """A listed path as a message shows it: printable, and cut if absurdly long."""
    s = s.encode("unicode_escape").decode("ascii") if not s.isprintable() else s
    return s if len(s) <= limit else s[:limit] + "…"


def _read_source(root, s, strategy):
    """Return (text, None) for a good source, or (None, problem). Never raises."""
    shown = _show(s)
    try:
        root = pathlib.Path(root).resolve()
        p = (root / s).resolve()  # an absolute s replaces root and lands outside it
        if not any(_inside(p, root / d) for d in RESEARCH_DIRS):
            return None, (f"source {shown} is not under docs/research/ or data/ in the root "
                          "— research sources only")
        if p == pathlib.Path(strategy).resolve():
            return None, f"source {shown} is the strategy itself"
        if not p.exists():
            return None, f"source {shown} does not exist"
        if not p.is_file():
            return None, f"source {shown} is not a file"
        return p.read_text(encoding="utf-8-sig"), None
    except UnicodeDecodeError:
        return None, f"source {shown} is not UTF-8 text"
    except (OSError, ValueError) as exc:
        return None, f"source {shown} cannot be read: {getattr(exc, 'strerror', None) or exc}"


def _inside(p, d):
    try:
        p.relative_to(d.resolve())
        return True
    except ValueError:
        return False


def _source_paths(line):
    if not BULLET.match(line):
        return []
    paths = BACKTICKED.findall(line) + [m.group(2).split("#")[0] for m in LINK.finditer(line)]
    return [x.strip() for x in paths if x.strip()]


def examine(path, root=ROOT):
    """Return (problems, sources listed, figures checked).

    Reading the strategy itself may raise OSError or UnicodeDecodeError; main() turns
    that into exit 2.
    """
    text = pathlib.Path(path).read_text(encoding="utf-8-sig")
    text = COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    section, sources, found = None, [], []
    has_sources = has_recommendation = False
    fence = None
    for i, line in enumerate(text.splitlines(), 1):
        f = FENCE.match(line)
        if fence:
            if f and f.group(1)[0] == fence[0] and len(f.group(1)) >= len(fence):
                fence = None
            continue
        if f:
            fence = f.group(1)
            continue
        h = HEADING.match(line)
        if h:
            title = h.group(1).strip("*_ \t")
            if SOURCES.match(title):
                section, has_sources = "Sources", True
            elif CHECKED.match(title):
                section = h.group(1).strip()
                has_recommendation |= title.lower().startswith("recommendation")
            else:
                section = None
            continue
        if section == "Sources":
            for x in _source_paths(line):
                if x not in sources:
                    sources.append(x)
        elif section:
            clean = LIST_MARKER.sub(r"\1", CODE.sub(" ", line))
            found += [(i, section, fig, raw) for fig, raw in _figures_written(clean)]
    out = []
    if not has_sources:
        out.append("no ## Sources section listing backticked or linked paths")
    elif not sources:
        out.append("## Sources lists no backticked or linked paths")
    if not has_recommendation:
        out.append("no ## Recommendation section")
    corpus = set()
    for s in sources:
        src, problem = _read_source(root, s, path)
        if problem:
            out.append(problem)
        else:
            corpus |= source_tokens(src)
    for i, section, fig, raw in found:
        if fig not in corpus:
            out.append(f"line {i} ({section}): figure {raw} is in no listed source")
    return out, len(sources), len(found)


def check(path, root=ROOT):
    """The problems with a strategy file; [] when every figure is found."""
    return examine(path, root)[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("strategy", type=pathlib.Path)
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    try:
        a = ap.parse_args(argv)
    except SystemExit as exc:
        return EXIT_OK if exc.code == 0 else EXIT_BAD_INPUT
    try:
        if not a.strategy.exists():
            print(f"cite-check: {a.strategy} does not exist")
            return EXIT_BAD_INPUT
        if not a.strategy.is_file():
            print(f"cite-check: {a.strategy} is not a file")
            return EXIT_BAD_INPUT
        out, n_sources, n_figures = examine(a.strategy, a.root)
    except UnicodeDecodeError:
        print(f"cite-check: {a.strategy} is not UTF-8 text")
        return EXIT_BAD_INPUT
    except (OSError, ValueError) as exc:
        print(f"cite-check: {a.strategy} cannot be read: {getattr(exc, 'strerror', None) or exc}")
        return EXIT_BAD_INPUT
    for p in out:
        print(f"cite-check: {p}")
    print(f"cite-check: {a.strategy.name}: {_plural(n_sources, 'source')}, "
          f"{_plural(n_figures, 'figure')} checked, {_plural(len(out), 'problem')}")
    return EXIT_FAIL if out else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
