#!/usr/bin/env python3
"""strategy_cite_check.py — a strategy may quote only figures its listed sources contain.

  python3 scripts/strategy_cite_check.py STRATEGY.md [--root DIR]
      exit 0 every figure found · 1 problems (listed) · 2 bad usage, or the strategy is
      missing, not a file, unreadable or not UTF-8. (Unlike gap_matrix.py, which keeps 2 for
      usage and 6 for bad input, this check has one input, so 2 covers both.)

Checked sections: `## Strategy A…` and `## Strategy B…`, `## Recommendation…` and
`## Concrete Artifact…` / `## Concrete Artefact…` (case-blind, `##` then a space or tab, an
optional `5.` number, any trailing text such as `:`, `— <name>` or `(Strategy A)`). `###`
subheadings stay inside their section. Between `## Recommendation` and `## Sources`, any
other `##` heading is a problem (and its figures are still checked), so checking cannot be
ended silently; any `##` heading after `## Sources` is a problem too (`## Sources` is last).
The preamble and other headings before the pick are not checked.

A figure is a whole number in one of these shapes, read the same way in the strategy and in
every source: an N/M count (`7/12`, `7/12-competitor`), a percentage (`58%`, `40 %`), a
decimal (`0.75`), a comma-thousands number (`1,200`), a whole number of two digits or more,
or any number with a `k` or `x` multiplier (`40k`, `£12k`, `2.5x`, `3x`), or a `top-N`
(`top-3`, `top-10`). A number glued to a unit or word gives its numeric core (`12-page`, `12th`, `40/mo`, `-12` → 12; the sign is
dropped); a hyphen or en-dash range gives both ends (`20-39%` → 20 and 39%).
Figures are compared as tokens, never as substrings: thousands commas are ignored
(`1,500` = `1500`), `%`, `k` and `x` must match (`40k` needs `40k`, `39%` needs `39%`),
other units are not compared (`12-page` needs only `12`). A source's N/M also supplies N and
M on their own, so "of 12 competitors" may cite `7/12`; digits are never split otherwise.

Not figures: single digits without %/k/x, 28 (the locked city count), a 19xx/20xx year
beside a year cue (in/by/since/until/from/before/after/during, Q1–Q4, H1/H2 or a month
name, with early/mid/late allowed between; or a month name right after) — a bare
`2000 searches` is still a figure, and when no source has it the message says to add a cue
("in 2000") or a comma ("2,000") — dates (`2026-09-24`, `24/09/2026`), clock times (`10:30`), ordered-list markers (`10.`),
anything in backticks or a fenced code block, link URLs (the link text is still checked)
and HTML comments. Dates, times and URLs are ignored on the source side too.

Each figure must be a token of at least one file listed under `## Sources` (case-blind,
trailing text allowed) — every backticked path (a span with a `/` or ending .md/.json; other
code spans are ignored) and every `[text](path)` link on a `-`, `*`, `+` or `1.` bullet.
Every listed file must exist, be readable UTF-8 text, not be the strategy itself, and
resolve under --root to a research output: docs/research/gap-matrix-*.md,
docs/research/keyword-gap-*.md, docs/research/competitors/*.json|*.md,
docs/research/llm-intel/*.json, data/competitors.json, data/page-map.json,
data/locations.json or data/queries/<slug>.json. Anything else is not a research source.
The strategy agent quotes a source's figure exactly as the source writes it.

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
RESEARCH_SOURCES = (  # (pattern, as the message names it)
    (r"docs/research/gap-matrix-[^/]+\.md", "docs/research/gap-matrix-*.md"),
    (r"docs/research/keyword-gap-[^/]+\.md", "docs/research/keyword-gap-*.md"),
    (r"docs/research/competitors/[^/]+\.(?:json|md)", "docs/research/competitors/*.json|*.md"),
    (r"docs/research/llm-intel/[^/]+\.json", "docs/research/llm-intel/*.json"),
    (r"data/(?:competitors|page-map|locations)\.json",
     "data/competitors.json, data/page-map.json, data/locations.json"),
    (r"data/queries/[^/]+\.json", "data/queries/<slug>.json"),
)
RESEARCH_SOURCE = re.compile("|".join(f"(?:{p})" for p, _ in RESEARCH_SOURCES))
ALLOWED = "; ".join(name for _, name in RESEARCH_SOURCES)
MONTH = (r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?"
         r"|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)")
YEAR_BEFORE = re.compile(
    r"(?:\b(?:in|by|since|until|from|before|after|during|q[1-4]|h[12]|" + MONTH + r")\.?"
    r"(?:\s+(?:early|mid|late))?|\b(?:early|mid|late))[\s-]+$", re.I)
YEAR_AFTER = re.compile(r"^\s+" + MONTH + r"\b", re.I)
ALWAYS_TRUE = {"28"}

HEADING = re.compile(r"^##[ \t]+(?:\d+[.)]?[ \t]+)?(.*?)[ \t#]*$")
TOP_HEADING = re.compile(r"^#[ \t]+(.*?)[ \t#]*$")  # a document-level heading
CHECKED = re.compile(r"(?:recommendation|concrete artifact|concrete artefact)", re.I)
STRATEGY = re.compile(r"strategy\s+[ab]\b", re.I)
BARE_YEAR = re.compile(r"(?:19|20)\d\d")
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
    r"(?<![\w.,/])(?:(?<=\b[Tt]op[-\u2013])|(?<![A-Za-z_][-\u2013]))"  # not glued to a word
                                                                     # (top-10 is), a decimal
                                                                     # or a path
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
        top_n = m.string[max(0, m.start() - 4):m.start()].lower() in ("top-", "top\u2013")
        figure = top_n or not (plain_int and (len(core) < 2 or core in ALWAYS_TRUE
                                              or _is_year(core, m)))
        yield core + suffix, figure, (), m.group(0)


def _is_year(core, m):
    """19xx/20xx is a year only beside a cue: in/by/since/until/from/before/after/during,
    Q1–Q4, H1/H2 or a month (early/mid/late may sit between), or a month right after."""
    if len(core) != 4 or not 1900 <= int(core) <= 2099:
        return False
    return bool(YEAR_BEFORE.search(m.string, 0, m.start())
                or YEAR_AFTER.match(m.string[m.end():]))


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
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            rel = None
        if rel is None or not RESEARCH_SOURCE.fullmatch(rel):
            return None, f"source {shown} is not a research source (allowed: {ALLOWED})"
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


def _source_paths(line):
    if not BULLET.match(line):
        return []
    paths = [x for x in BACKTICKED.findall(line)  # `city` or `7/12` is not a path
             if re.search(r"[A-Za-z]", x) and ("/" in x or x.endswith((".md", ".json")))]
    paths += [m.group(2).split("#")[0] for m in LINK.finditer(line)]
    return [x.strip() for x in paths if x.strip()]


def examine(path, root=ROOT):
    """Return (problems, sources listed, figures checked).

    Reading the strategy itself may raise OSError or UnicodeDecodeError; main() turns
    that into exit 2.
    """
    text = pathlib.Path(path).read_text(encoding="utf-8-sig")
    text = COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    section, sources, found = None, [], []
    has_sources = has_recommendation = in_pick = stray = False
    fence, structure = None, []
    for i, line in enumerate(text.splitlines(), 1):
        f = FENCE.match(line)
        if fence:
            if f and f.group(1)[0] == fence[0] and len(f.group(1)) >= len(fence):
                fence = None
            continue
        if f:
            fence = f.group(1)
            continue
        top = TOP_HEADING.match(line)
        if top and has_sources:  # a document-level heading cannot follow Sources either
            structure.append(f"line {i}: # {top.group(1).strip()} comes after ## Sources — "
                             "## Sources must be the last section; move it above "
                             "## Recommendation")
            section, in_pick, stray = None, False, False
            continue
        h = HEADING.match(line)
        if h:
            title, name, stray = h.group(1).strip("*_ \t"), h.group(1).strip(), False
            if has_sources:  # Sources is last; a pick section after it is still checked
                advice = ("merge it into the first ## Sources" if SOURCES.match(title)
                          else "move it above ## Sources" if CHECKED.match(title)
                          else "move it above ## Recommendation")
                structure.append(f"line {i}: ## {name} comes after ## Sources — ## Sources "
                                 f"must be the last section; {advice}")
            if SOURCES.match(title):
                section, has_sources, in_pick = "Sources", True, False
            elif CHECKED.match(title):
                section = name
                if title.lower().startswith("recommendation"):
                    has_recommendation = in_pick = True
            elif in_pick:  # checking must not end silently: flag it and keep checking
                section, stray = name, True
                structure.append(
                    f"line {i}: unrecognised section inside the pick: ## {name} — only "
                    "## Concrete Artifact may sit between ## Recommendation and ## Sources: "
                    "make it a ### subheading, or move it above ## Recommendation (a "
                    "strategy's risks go under its ## Strategy heading)")
            elif STRATEGY.match(title):
                section = name
            else:
                section = None
            continue
        if section == "Sources":
            for x in _source_paths(line):
                if x not in sources:
                    sources.append(x)
        elif section:
            clean = LIST_MARKER.sub(r"\1", CODE.sub(" ", line))
            found += [(i, section, stray, fig, raw) for fig, raw in _figures_written(clean)]
    out = []
    if not has_sources:
        out.append("no ## Sources section listing backticked or linked paths")
    elif not sources:
        out.append("## Sources lists no backticked or linked paths")
    if not has_recommendation:
        out.append("no ## Recommendation section")
    out += structure
    corpus = set()
    for s in sources:
        src, problem = _read_source(root, s, path)
        if problem:
            out.append(problem)
        else:
            corpus |= source_tokens(src)
    for i, section, stray, fig, raw in found:
        if fig not in corpus:
            out.append(f"line {i} ({section}): figure {raw} is in no listed source"
                       + _hint(section, stray, raw))
    return out, len(sources), len(found)


def _hint(section, stray, raw):
    """Why an unsourced figure failed, when the plain message would not say."""
    if BARE_YEAR.fullmatch(raw):  # a year the check could not see as one (no cue word)
        return (f' — if it is a year, put a cue word before it ("in {raw}", "by {raw}", '
                f'"Q3 {raw}"); if it is a quantity, write it "{raw[0]},{raw[1:]}" as a source '
                "prints it")
    if stray:
        return (f" — ## {section} is not a pick section, but every figure between "
                "## Recommendation and ## Sources is checked")
    return ""


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
