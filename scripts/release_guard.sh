#!/usr/bin/env bash
# =============================================================================
# RELEASE GUARD — the one-line gate in front of every launch-only npm script.
#
# Usage:   bash scripts/release_guard.sh && <the release-only command>
#
# Exit code 0 = BSUK_RELEASE=1 is set (project 6 has started) AND the build will have a form
# endpoint, 2 = refused.
#
# BSUK has no host and no domain until project 6. `npm run build:release` bakes a search
# index for a site that cannot be searched, so it is chained behind this guard rather than
# deleted: a script that exists and says REFUSED teaches more than a script that is missing.
# The same flag guards scripts/indexnow_submit.py and BSUK_RELEASE=1 check:placeholders.
#
# PUBLIC_FORMSPREE_ID. The pup-sale and listing forms read it at BUILD time, and a build
# without it does not fail — each form quietly falls back to `#contact`, which submits
# nowhere. That was found on a worktree with no `.env`: every page built green and no
# enquiry could have been sent. So a release build refuses unless the id is set, either in
# the environment or as a non-empty `PUBLIC_FORMSPREE_ID=` line in `.env` (the file Astro
# itself loads). The value is never printed.
# =============================================================================
set -euo pipefail

if [ "${BSUK_RELEASE:-}" != "1" ]; then
  echo "REFUSED: release-only command. Set BSUK_RELEASE=1 only when project 6 has a real domain and host." >&2
  exit 2
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
formspree_id="${PUBLIC_FORMSPREE_ID:-}"
if [ -z "$formspree_id" ] && [ -f "$ROOT/.env" ]; then
  formspree_id="$(sed -n 's/^[[:space:]]*PUBLIC_FORMSPREE_ID[[:space:]]*=[[:space:]]*//p' "$ROOT/.env" | tail -n 1 | tr -d "\"' \r")"
fi
if [ -z "$formspree_id" ]; then
  echo "REFUSED: PUBLIC_FORMSPREE_ID is unset (environment and .env) — every enquiry form would build with a #contact fallback that submits nowhere." >&2
  exit 2
fi
exit 0
