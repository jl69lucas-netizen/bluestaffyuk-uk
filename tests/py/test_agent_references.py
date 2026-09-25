"""Every agent names only things this repo has.

`tests/py/test_rules_index.py` already checks every backticked repo path an agent cites, but
only a path whose first segment is a real top-level directory or that carries a source
extension. Everything else an agent can name slipped past it, and the project-5 readiness
audit (2026-09-23) found each kind in the 41 agents (the bare `sessions/` directory, Known
Issue 56, is the dead-root guard in `tests/py/test_rules_index.py`, shared with the skills
and the commands):

- a directory the source repo had and this one does not (`skills/`, `site/content`,
  `/tmp/bsuk-repo`, `content/`, `archive/`), written without backticks or as a command;
- an agent or skill that was never ported (`bsuk-case-study-agent`, `social-content skill`);
- a `(deferred to project 3)` promise that expired when project 3 closed without the file;
- a field `data/locations.json` does not have (`"live": true`, `gsc_clicks`);
- a route no page serves (`/contact/`, `/available/`, `/blue-staffy-breeder-standing/`).

Each is a builder sent looking for something nobody will create, and the first symptom is a
failed run rather than a failed test. A line that says why the thing is missing — the same
markers the path guard honours — is allowed.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = sorted((ROOT / ".claude/agents").glob("bsuk-*.md"))
AGENT_NAMES = {p.stem for p in AGENTS}
SKILL_NAMES = {p.parent.name for p in (ROOT / ".claude/skills").glob("*/SKILL.md")}
MARKERS = ("(arrives in", "(deferred", "(not ported", "(source repo only", "NOT FETCHED")


def lines(agent):
    return list(enumerate(agent.read_text(encoding="utf-8").splitlines(), 1))


def marked(line):
    return any(m in line for m in MARKERS)


def test_there_are_agents_to_check():
    assert len(AGENTS) >= 41


# ── directories the source repo had ─────────────────────────────────────────
# Written as a command or in prose these escape the backtick-only path guard. Each is named
# because a generic "any unknown directory" rule cannot tell `site/content` from a route.
DEAD_DIRS = re.compile(
    r"(?<![\w./-])(?:skills/|site/content|archive/|content/(?!word\b))"
    r"|(?<![\w.])/content/|/tmp/bsuk-repo|/path/to/")


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_cites_a_directory_this_repo_lacks(agent):
    bad = [f"{agent.name}:{n}  {l.strip()[:120]}" for n, l in lines(agent)
           if DEAD_DIRS.search(l) and not marked(l)]
    assert bad == [], ("these directories exist only in the source repo — skills live under "
                       ".claude/skills/, pages under src/pages/, builds in dist/:\n  "
                       + "\n  ".join(bad))


def test_the_dead_directory_detector_fires_and_spares_real_paths():
    for hit in ("ls skills/", "cd site/content", "find content/ -type f", "from `/content/`",
                "`archive/simply-static.zip`", "SITE=/tmp/bsuk-repo", "grep -r x /path/to/site"):
        assert DEAD_DIRS.search(hit), hit
    for ok in ("`.claude/skills/grill-me/SKILL.md`", "src/content/blog/<slug>.md",
               "docs/superpowers/sessions/", "`src/pages/<slug>/index.astro`"):
        assert not DEAD_DIRS.search(ok), ok


# ── files named in prose or commands ────────────────────────────────────────
# The path guard in test_rules_index.py reads backticked tokens and fenced interpreter
# commands. A script named inside a longer backticked command (`python3 scripts/route.py
# "<task>"`), or a data file named in plain prose ("Read data/image-specs.json"), slips past
# it. This reads every repo file name of the kinds agents cite, wherever it sits.
FILE_REF = re.compile(r"(?<![\w/.-])((?:scripts|data|docs/reference|src/components|src/layouts|tests/py)"
                      r"/[\w./-]+\.(?:py|sh|mjs|json|md|astro|ts))(?![\w/-])")


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_every_file_an_agent_names_exists_or_is_marked(agent):
    bad = [f"{agent.name}:{n}  {path}" for n, l in lines(agent) if not marked(l)
           for path in FILE_REF.findall(l) if not (ROOT / path).exists()]
    assert bad == [], ("an agent names a file this repo does not have and does not say why — "
                       "point at the file that replaced it, or mark the line '(not ported — "
                       "source repo only)':\n  " + "\n  ".join(bad))


def test_the_file_detector_reads_commands_and_prose():
    assert FILE_REF.findall('`python3 scripts/route.py "<task>"` prints the tier') == ["scripts/route.py"]
    assert FILE_REF.findall("Read data/image-specs.json first") == ["data/image-specs.json"]
    assert FILE_REF.findall("`data/boards/<slug>.json`") == []


# ── files this repo REPLACED ─────────────────────────────────────────────────
# A "(not ported)" marker is honest for a file nothing replaced. For these, something did,
# and an agent that still reads the dead name — even with the marker — skips the file that
# holds the rules today. The value is what to cite instead.
REPLACED = {
    "docs/reference/design-system.md": "src/styles/tokens.css and src/components/kit/",
    "data/image-specs.json": "rules/images.md and data/image-manifest.json",
    "data/case-studies.json": "data/reviews.json",
    "data/structure.json": "data/page-map.json (inventory) and a dated structure map in docs/superpowers/sessions/",
    "MANUAL INTERIOR-PAGE CHECKLIST.md": ".claude/skills/manual-auditor-check/SKILL.md",
    "bsuk-footer-logo.png": "src/components/kit/SectionDivider.astro",
}


def test_every_replacement_exists():
    for target in (".claude/skills/manual-auditor-check/SKILL.md", "src/styles/tokens.css",
                   "rules/images.md", "data/image-manifest.json", "data/reviews.json",
                   "data/page-map.json", "src/components/kit/SectionDivider.astro"):
        assert (ROOT / target).exists(), target


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_cites_a_file_this_repo_replaced(agent):
    bad = [f"{agent.name}:{n}  {dead} -> cite {REPLACED[dead]}" for n, l in lines(agent)
           for dead in REPLACED if dead in l]
    assert bad == [], "cite the file that replaced it:\n  " + "\n  ".join(bad)


# ── agents and skills an agent hands work to ────────────────────────────────
# An agent name is a `bsuk-` token ending in a role word; a bare `bsuk-` token is usually a
# CSS class (`bsuk-faq-item`) and is the business of the template guard, not this one.
ROLE = ("agent", "builder", "fixer", "manager", "tracker", "specialist", "strategist",
        "verifier", "architect", "synthesizer", "intel", "registry", "analytics", "pipeline",
        "rebuilder", "standardizer", "updater", "personality", "qa")
AGENT_REF = re.compile(r"(?<![\w/.-])@?(bsuk-[a-z0-9-]+-(?:%s))(?![\w-])" % "|".join(ROLE))
SKILL_REF = re.compile(r"(?<![\w/.-])`?([a-z][a-z0-9-]+)`? skill\b")


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_every_agent_an_agent_names_exists_or_is_marked(agent):
    bad = [f"{agent.name}:{n}  {name}" for n, l in lines(agent) if not marked(l)
           for name in AGENT_REF.findall(l) if name not in AGENT_NAMES | SKILL_NAMES]
    assert bad == [], ("an agent hands work to an agent that is not in .claude/agents/ — "
                       "remove the handoff or mark the line '(deferred to project 6, see "
                       "data/port-manifest.json)':\n  " + "\n  ".join(bad))


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_every_skill_an_agent_names_exists_or_is_marked(agent):
    words = {"master", "final", "the", "a", "this", "each", "every", "one", "that", "own",
             "system", "builder", "writing", "page-type"}
    bad = [f"{agent.name}:{n}  {name}" for n, l in lines(agent) if not marked(l)
           for name in SKILL_REF.findall(l)
           if name not in SKILL_NAMES and name not in words and "-" in name]
    assert bad == [], ("an agent sends work to a skill that is not in .claude/skills/:\n  "
                       + "\n  ".join(bad))


def test_the_name_detectors_fire():
    assert AGENT_REF.findall("route that to `bsuk-case-study-agent`") == ["bsuk-case-study-agent"]
    assert AGENT_REF.findall('<div class="bsuk-faq-item">') == []
    assert SKILL_REF.findall("| Social post | social-content skill |") == ["social-content"]


NPM = re.compile(r"npm run(?: -s)? ([a-z][a-z0-9:_-]*)")
SCRIPTS = set(json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"])


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_every_npm_script_an_agent_runs_exists(agent):
    bad = [f"{agent.name}:{n}  npm run {s}" for n, l in lines(agent)
           for s in NPM.findall(l) if s not in SCRIPTS]
    assert bad == [], "package.json has no such script:\n  " + "\n  ".join(bad)


# ── promises that expired ───────────────────────────────────────────────────
# Projects 1-4 are closed. "(deferred to project 3)" on a file project 3 never wrote is no
# longer a forward reference: it tells a builder to wait for something that is not coming,
# and it disarms the path guard for every other path on the line.
FINISHED = re.compile(r"deferred to project [1-4]\b")


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_defers_to_a_finished_project(agent):
    bad = [f"{agent.name}:{n}  {l.strip()[:120]}" for n, l in lines(agent) if FINISHED.search(l)]
    assert bad == [], ("projects 1-4 are closed; say what replaced the file, or '(not ported "
                       "— source repo only)':\n  " + "\n  ".join(bad))


# ── fields data/locations.json does not have ────────────────────────────────
LOCATION_KEYS = set().union(*(r.keys() for r in json.loads(
    (ROOT / "data/locations.json").read_text(encoding="utf-8"))))
DEAD_FIELD = re.compile(r"""["']live["']\s*:\s*(?:true|false)|get\(["']live["']\)|gsc_clicks|"status":\s*"planned\"""")


def test_the_fields_the_guard_calls_dead_really_are_absent():
    assert not {"live", "gsc_clicks", "status"} & LOCATION_KEYS


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_reads_a_locations_field_that_does_not_exist(agent):
    bad = [f"{agent.name}:{n}  {l.strip()[:120]}" for n, l in lines(agent) if DEAD_FIELD.search(l)]
    assert bad == [], ("data/locations.json rows carry %s — there is no live/status/gsc_clicks "
                       "field:\n  " % sorted(LOCATION_KEYS) + "\n  ".join(bad))


# ── routes ───────────────────────────────────────────────────────────────────
# One of two route guards over the agents. This one reads the routes off src/ and the data
# files, so it runs without a build; its dist-based twin, route_offenders() in
# tests/py/test_builder_skills.py, also reads every skill and command and skips without dist/.
def served_routes():
    routes = {"/"}
    pages = ROOT / "src/pages"
    for idx in pages.rglob("index.astro"):
        rel = idx.parent.relative_to(pages).as_posix()
        routes.add("/" if rel == "." else "/%s/" % rel)
    routes |= {"/uk-locations/%s/" % r["slug"] for r in json.loads(
        (ROOT / "data/locations.json").read_text(encoding="utf-8"))}
    for post in (ROOT / "src/content/blog").glob("*.md"):
        m = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", post.read_text(encoding="utf-8"), re.M)
        if m:
            routes.add("/%s/" % m.group(1).strip("/"))
    routes |= {r["from"] for r in json.loads(
        (ROOT / "data/redirects.json").read_text(encoding="utf-8"))["redirects"]}
    routes |= {p["url"] for p in json.loads(
        (ROOT / "data/page-map.json").read_text(encoding="utf-8"))["pages"]}
    return routes


ROUTE = re.compile(r"(?:href=\"|`|\(|\s|→\s?)(/[a-z0-9][a-z0-9-]*(?:/[a-z0-9-]+)*/)(?=[\"`)\s,.;#]|$)")
# The two intel agents describe COMPETITORS' URL shapes (`/2025/09/`, `/how-to-choose-a-puppy/`).
COMPETITOR_SHAPES = {"bsuk-competitor-intel", "bsuk-competitive-keyword-gap-agent"}


@pytest.mark.parametrize("agent", [a for a in AGENTS if a.stem not in COMPETITOR_SHAPES],
                         ids=lambda p: p.stem)
def test_every_route_an_agent_links_is_served(agent):
    routes = served_routes()
    bad = [f"{agent.name}:{n}  {r}" for n, l in lines(agent)
           if not marked(l) and "wrong on sight" not in l
           for r in ROUTE.findall(l) if r not in routes
           and not r.startswith(("/images/", "/videos/", "/tmp/"))]
    assert bad == [], ("no page serves these routes — use the real one "
                       "(/uk-blue-staffy-breeders-contact/, /available-puppies/, "
                       "/uk-locations/<slug>/) or a [slug] placeholder:\n  " + "\n  ".join(bad))
