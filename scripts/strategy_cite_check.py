#!/usr/bin/env python3
"""strategy_cite_check.py — a strategy may quote only figures its listed sources contain.

  python3 scripts/strategy_cite_check.py STRATEGY.md [--root DIR]
      exit 0 every figure found · 1 problems (listed) · 2 the strategy cannot be read or bad usage

A figure is an N/M count, a percentage, a decimal, or a whole number of two digits or more,
in a `## Recommendation…` or `## Concrete Artifact…` section. Dates, anything in backticks,
single digits (step numbers, "3+ data points") and 28 (the locked city count) are not
figures. Each figure must appear literally in at least one file listed as a backticked path
under `## Sources`, and every listed file must exist, be readable UTF-8 and sit inside
--root (no absolute paths, no `..` escapes). The strategy agent quotes a source's figure
exactly as the source writes it.

The last line says what was examined:
  cite-check: strategy.md: 2 sources, 5 figures checked, 0 problems

Spec: docs/superpowers/specs/2026-09-23-competitor-intel-design.md §9.
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXIT_OK, EXIT_FAIL, EXIT_BAD_INPUT = 0, 1, 2
CHECKED = ("Recommendation", "Concrete Artifact")
ALWAYS_TRUE = {"28"}
CODE = re.compile(r"`[^`]*`")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
FIGURE = re.compile(r"(?<![\w.,/-])(\d+/\d+|\d+(?:\.\d+)?%|\d+\.\d+|\d{1,3}(?:,\d{3})+|\d{2,})(?![\w/-]|[.,]\d)")
SOURCE_LINE = re.compile(r"^\s*[-*]\s+`([^`]+)`")


def _plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _read_source(root, s):
    """Return (text, None) for a good source, or (None, problem)."""
    if pathlib.PurePath(s).is_absolute():
        return None, f"source {s} is outside the root (absolute path)"
    root = pathlib.Path(root).resolve()
    p = (root / s).resolve()
    if not p.is_relative_to(root):
        return None, f"source {s} is outside the root"
    if not p.exists():
        return None, f"source {s} does not exist"
    if not p.is_file():
        return None, f"source {s} is not a file"
    try:
        return p.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, f"source {s} is not UTF-8 text"
    except OSError as exc:
        return None, f"source {s} cannot be read: {exc.strerror or exc}"


def examine(path, root=ROOT):
    """Return (problems, sources listed, figures checked).

    Reading the strategy itself may raise OSError or UnicodeDecodeError; main() turns
    that into exit 2.
    """
    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    section, sources, found = None, [], []
    has_sources = has_recommendation = False
    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = line[3:].strip()
            has_sources |= section == "Sources"
            has_recommendation |= section.startswith("Recommendation")
            continue
        if section == "Sources":
            m = SOURCE_LINE.match(line)
            if m:
                sources.append(m.group(1))
        elif section and section.startswith(CHECKED):
            text = DATE.sub(" ", CODE.sub(" ", line))
            found += [(i, section, f) for f in FIGURE.findall(text) if f not in ALWAYS_TRUE]
    out = []
    if not has_sources or not sources:
        out.append("no ## Sources section listing backticked files")
    if not has_recommendation:
        out.append("no ## Recommendation section")
    corpus = []
    for s in sources:
        text, problem = _read_source(root, s)
        if problem:
            out.append(problem)
        else:
            corpus.append(text)
    for i, section, fig in found:
        if not any(fig in text for text in corpus):
            out.append(f"line {i} ({section}): figure {fig} is in no listed source")
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
    if not a.strategy.exists():
        print(f"cite-check: {a.strategy} does not exist")
        return EXIT_BAD_INPUT
    if not a.strategy.is_file():
        print(f"cite-check: {a.strategy} is not a file")
        return EXIT_BAD_INPUT
    try:
        out, n_sources, n_figures = examine(a.strategy, a.root)
    except UnicodeDecodeError:
        print(f"cite-check: {a.strategy} is not UTF-8 text")
        return EXIT_BAD_INPUT
    except OSError as exc:
        print(f"cite-check: {a.strategy} cannot be read: {exc.strerror or exc}")
        return EXIT_BAD_INPUT
    for p in out:
        print(f"cite-check: {p}")
    print(f"cite-check: {a.strategy.name}: {_plural(n_sources, 'source')}, "
          f"{_plural(n_figures, 'figure')} checked, {_plural(len(out), 'problem')}")
    return EXIT_FAIL if out else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
