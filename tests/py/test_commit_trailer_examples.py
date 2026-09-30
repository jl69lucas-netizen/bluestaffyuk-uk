"""Every commit example an agent or skill tells a model to run carries the project trailer.

Subagents copy these examples verbatim, so an example without the trailer produces commits
without it (the user's standing rule: `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`).

A commit example is any `git commit` (also `git -C <dir> commit`) that gives its message with
`-m`, a combined flag ending in `m` (`-am`), `-F`, `--message` or `--file`. Its scope runs from
the command to the next commit example or to the end of its fenced block (a line starting with
```), whichever comes first, so a neighbouring example's trailer never counts for it and a long
multi-line message may put its trailer any number of lines down.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TRAILER = "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
SCOPES = [ROOT / ".claude", ROOT / "docs/reference", ROOT / "CLAUDE.md"]

COMMIT = re.compile(r"\bgit(?:\s+-[cC]\s+\S+)*\s+commit\b")
MESSAGE = re.compile(r"\s(?:-[a-zA-Z]*[mF]\b|--(?:message|file)\b)")


def _files():
    for scope in SCOPES:
        if scope.is_file():
            yield scope
        else:
            yield from sorted(p for p in scope.rglob("*.md") if p.is_file())


def _examples(line):
    """(start, end) of each commit command on the line that gives a message."""
    starts = [m.start() for m in COMMIT.finditer(line)]
    spans = zip(starts, starts[1:] + [len(line)])
    return [(s, e) for s, e in spans if MESSAGE.search(line[s:e])]


def _missing(text):
    lines = text.split("\n")
    hits = [(i, s, e) for i, line in enumerate(lines) for s, e in _examples(line)]
    out = []
    for k, (i, s, e) in enumerate(hits):
        nxt = hits[k + 1][0] if k + 1 < len(hits) else len(lines)
        if nxt == i:  # another example later on the same line
            scope = lines[i][s:e]
        else:
            scope = [lines[i][s:]]
            for line in lines[i + 1:nxt]:
                if line.lstrip().startswith("```"):
                    break
                scope.append(line)
            scope = "\n".join(scope)
        if TRAILER not in scope:
            out.append((i + 1, lines[i].strip()))
    return out


def test_detector_flags_a_bare_example_and_passes_a_trailed_one():
    assert _missing('git commit -m "fix: x"') == [(1, 'git commit -m "fix: x"')]
    assert _missing(f'git commit -m "fix: x" -m "{TRAILER}"') == []
    assert _missing(f'git commit -m "fix: x\n\n{TRAILER}"') == []


def test_a_neighbouring_examples_trailer_does_not_count():
    text = f'git commit -m "a"\n\n\ngit commit -m "b" -m "{TRAILER}"'
    assert _missing(text) == [(1, 'git commit -m "a"')]
    same_line = f'git commit -m "a" && git commit -m "b" -m "{TRAILER}"'
    assert _missing(same_line) == [(1, same_line)]
    next_block = f'```bash\ngit commit -m "a"\n```\n\n```bash\n# {TRAILER}\n```'
    assert _missing(next_block) == [(2, 'git commit -m "a"')]


FORMS = [
    ('git commit -am "x"', f'git commit -am "x" -m "{TRAILER}"'),
    ('git commit -a -m "x"', f'git commit -a -m "x" -m "{TRAILER}"'),
    ('git commit --amend -m "x"', f'git commit --amend -m "x" -m "{TRAILER}"'),
    ('git -C <dir> commit -m "x"', f'git -C <dir> commit -m "x" -m "{TRAILER}"'),
    ('git commit --no-verify -m "x"', f'git commit --no-verify -m "x" -m "{TRAILER}"'),
    ("git commit -F - <<'EOF'\nx\nEOF", f"git commit -F - <<'EOF'\nx\n\n{TRAILER}\nEOF"),
    ("git commit -F msg.txt", f"git commit -F msg.txt   # msg.txt ends with:\n# {TRAILER}"),
    ('git commit --message="x"', f'git commit --message="x" --message="{TRAILER}"'),
]


@pytest.mark.parametrize("bare,trailed", FORMS, ids=[b.split("\n")[0] for b, _ in FORMS])
def test_every_commit_form_is_caught(bare, trailed):
    first = bare.split("\n")[0]
    assert _missing(bare) == [(1, first)]
    assert _missing(trailed) == []


def test_commands_without_a_message_are_not_examples():
    for text in ("never run git commit -a blindly", "git commit --amend --no-edit",
                 "git commit", "git log -m", "git commit -s"):
        assert _missing(text) == [], text


def test_a_long_message_may_put_its_trailer_far_down_its_block():
    body = "\n".join(f"line {n} of the body" for n in range(12))
    inside = f'```bash\ngit commit -m "subject\n\n{body}\n\n{TRAILER}"\n```'
    assert _missing(inside) == []
    outside = f'```bash\ngit commit -m "subject\n\n{body}"\n```\n{TRAILER}'
    assert _missing(outside) == [(2, 'git commit -m "subject')]


@pytest.mark.parametrize("path", list(_files()), ids=lambda p: str(p.relative_to(ROOT)))
def test_every_commit_example_carries_the_trailer(path):
    bad = _missing(path.read_text(encoding="utf-8"))
    assert not bad, f"{path.relative_to(ROOT)}: commit example(s) without the trailer: {bad}"
