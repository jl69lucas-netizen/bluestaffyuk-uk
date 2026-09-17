#!/usr/bin/env python3
"""indexnow_submit.py — IndexNow submission for BlueStaffyUK: Bing, Yandex, and the
partner endpoints they proxy to.

  python3 scripts/indexnow_submit.py <slug>                 # one page
  python3 scripts/indexnow_submit.py <slug> <slug> ...      # several
  python3 scripts/indexnow_submit.py --changed              # pages changed vs origin/main
  python3 scripts/indexnow_submit.py --all                  # every sitemap URL
  python3 scripts/indexnow_submit.py --dry-run <slug>       # print the URLs, send nothing

Exit: 0 submitted (or dry run), 1 ran and the endpoint refused the payload, 2 cannot run
(release guard, placeholder host, missing key, nothing submittable).

INACTIVE UNTIL PROJECT 6. BSUK has no host and no domain, so the first statement of main()
refuses unless `BSUK_RELEASE=1` — before the key is read and before any socket is opened.
Submitting `SITE_URL_PLACEHOLDER` would tell Bing that a dead host is worth crawling, and
IndexNow treats junk submissions as a trust signal about the host. The flag alone is not
enough: `SITE_URL` must also be a real origin, not the placeholder.

The key is read from `INDEXNOW_KEY` in the environment (`.env`, see
`docs/reference/credentials.md`) and the host from `SITE_URL`. Neither is ever hardcoded,
and neither is ever printed — not by `--dry-run`, not on failure. The procedure this script
replaces is `.claude/skills/bsuk-indexing/SKILL.md` STEP 4.
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

HOST = os.environ.get("SITE_URL", "").replace("https://", "").replace("http://", "").rstrip("/")
ORIGIN = f"https://{HOST}"
ENDPOINT = "https://api.indexnow.org/indexnow"
PUBLIC = pathlib.Path("public")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"

# Never submit these. `/.astro/` is a build artifact that the sitemap generator can emit
# into page-sitemap.xml — submitting it would ask Bing to crawl a directory, not a page.
JUNK = ("/.astro/", "/admin/", "/form/", "/thank-you/", "/tag/", "/_preview/")


def die(msg: str, code: int = 2) -> None:
    print(f"REFUSED: {msg}", file=sys.stderr)
    sys.exit(code)


def find_key() -> str:
    """The key comes from the environment and nowhere else. An empty key is a bug, not a
    default (docs/reference/credentials.md), so an unset or blank INDEXNOW_KEY refuses."""
    key = os.environ.get("INDEXNOW_KEY", "").strip()
    if not key:
        die("INDEXNOW_KEY is unset or empty — see docs/reference/credentials.md")
    if not re.fullmatch(r"[0-9a-f]{32}", key):
        die("INDEXNOW_KEY is not 32 lowercase hex characters (value not printed)")
    return key


def http(url, data=None, method="GET"):
    req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": UA})
    if data is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")[:400]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:400]
    except Exception as e:  # noqa: BLE001 - network shape varies, all are equally fatal here
        return 0, str(e)


def verify_key_live(key: str) -> None:
    status, body = http(f"{ORIGIN}/{key}.txt")
    if status != 200:
        die(f"key file not reachable at {ORIGIN}/<key>.txt (HTTP {status}). Deploy it before submitting.")
    if body.strip() != key:
        die("live key file body does not match INDEXNOW_KEY (neither value printed)")
    print("key       reachable, HTTP 200, body matches (value not printed)")


def urls_from_sitemaps():
    """The three sitemap files BSUK's own generator writes, and only those: there is no
    sitemap-index following, no .gz support and no namespace handling, by design — this
    reads one repo's output, not the open web.

    URLs are pulled with a regex rather than an XML parser on purpose: a half-written
    sitemap must yield nothing and let the caller refuse, never raise a traceback. The
    `\s*` either side of the URL matters — a pretty-printed `<loc>` on its own indented
    line is valid, and a regex that missed it would report a clean 'nothing to submit'."""
    out = []
    for name in ("page-sitemap.xml", "post-sitemap.xml", "local-sitemap.xml"):
        p = PUBLIC / name
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            die(f"cannot read {p}: {e}")
        out += re.findall(rf"<loc>\s*({re.escape(ORIGIN)}/[^<\s]*)\s*</loc>", text)
    return sorted(set(out))


def changed_slugs(ref="origin/main"):
    """Page slugs whose source changed vs a git ref, plus anything uncommitted."""
    cmds = [
        ["git", "diff", "--name-only", f"{ref}...HEAD"],
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    files = set()
    for c in cmds:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode == 0:
            files.update(x for x in r.stdout.split("\n") if x.strip())
    slugs = set()
    for f in files:
        m = re.match(r"src/pages/(.+)/index\.(astro|html)$", f)
        if m:
            slugs.add(m.group(1))
        elif f == "src/pages/index.astro":
            slugs.add("")
    return sorted(slugs)


def to_url(token: str) -> str:
    if token.startswith(("http://", "https://")):
        return token
    return f"{ORIGIN}/" + token.strip("/") + "/" if token.strip("/") else f"{ORIGIN}/"


def main() -> int:
    ap = argparse.ArgumentParser(description="Submit BSUK URLs to IndexNow.")
    ap.add_argument("slugs", nargs="*", help="page slugs or full URLs")
    ap.add_argument("--changed", action="store_true", help="derive slugs from git changes vs origin/main")
    ap.add_argument("--all", action="store_true", help="every URL in the sitemaps")
    ap.add_argument("--dry-run", action="store_true", help="print the URLs, submit nothing")
    ap.add_argument("--skip-live-check", action="store_true",
                    help="do not verify each URL returns 200 first (NOT recommended)")
    a = ap.parse_args()

    # Both guards run before the key is read and before any socket is opened.
    if os.environ.get("BSUK_RELEASE") != "1":
        die("IndexNow is inactive until project 6. Set BSUK_RELEASE=1 only when the site is "
            "live at a real domain; submitting SITE_URL_PLACEHOLDER would publish a dead host.")
    if not HOST or "PLACEHOLDER" in HOST:
        die("SITE_URL is unset or still a placeholder — nothing to submit.")

    if not PUBLIC.is_dir():
        die("run from the repo root — public/ not found")

    if a.all:
        urls = urls_from_sitemaps()
    elif a.changed:
        slugs = changed_slugs()
        if not slugs:
            print("no changed page sources vs origin/main — nothing to submit")
            return 0
        urls = [to_url(s) for s in slugs]
    elif a.slugs:
        urls = [to_url(s) for s in a.slugs]
    else:
        ap.error("give slugs, or --changed, or --all")

    urls = [u for u in urls if not any(j in u for j in JUNK)]
    urls = sorted(set(urls))
    if not urls:
        die("no submittable URLs after filtering build artifacts")

    if a.dry_run:
        print(f"--dry-run: would submit {len(urls)} URL(s) to {ENDPOINT} for host {HOST}")
        for u in urls:
            print(f"  + {u}")
        print("nothing sent; the key is read from INDEXNOW_KEY at submit time and never printed")
        return 0

    key = find_key()
    verify_key_live(key)

    # A URL that 404s must never be submitted. IndexNow treats junk submissions as a trust
    # signal about the host, so this check is the point of the script.
    if not a.skip_live_check:
        print(f"\nchecking {len(urls)} URL(s) are live...")
        live, dead = [], []
        for u in urls:
            status, _ = http(u)
            (live if status == 200 else dead).append((u, status))
            print(f"  {status:>3}  {u}")
        if dead:
            print(f"\n{len(dead)} URL(s) are not 200 and will NOT be submitted:", file=sys.stderr)
            for u, s in dead:
                print(f"  HTTP {s}  {u}", file=sys.stderr)
        urls = [u for u, _ in live]
        if not urls:
            die("every URL failed the live check")

    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"{ORIGIN}/{key}.txt",
        "urlList": urls,
    }

    print(f"\nsubmitting {len(urls)} URL(s) to {ENDPOINT}")
    for u in urls:
        print(f"  + {u}")

    status, body = http(ENDPOINT, data=json.dumps(payload).encode(), method="POST")
    meaning = {
        200: "OK — URLs submitted",
        202: "Accepted — received, key validation pending",
        400: "Bad request — invalid payload",
        403: "Forbidden — key not valid for this host",
        422: "Unprocessable — URLs do not belong to the host, or key mismatch",
        429: "Too many requests — throttled, retry later",
    }.get(status, "unexpected response")
    print(f"\nIndexNow HTTP {status} — {meaning}")
    if body.strip():
        print(f"body: {body.strip()}")
    if status in (200, 202):
        print(f"\nSUBMITTED {len(urls)} URL(s).")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
