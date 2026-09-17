#!/usr/bin/env bash
# =============================================================================
# RELEASE GUARD — the one-line gate in front of every launch-only npm script.
#
# Usage:   bash scripts/release_guard.sh && <the release-only command>
#
# Exit code 0 = BSUK_RELEASE=1 is set (project 6 has started), 2 = refused.
#
# BSUK has no host and no domain until project 6. `npm run build:release` bakes a search
# index for a site that cannot be searched, so it is chained behind this guard rather than
# deleted: a script that exists and says REFUSED teaches more than a script that is missing.
# The same flag guards scripts/indexnow_submit.py and BSUK_RELEASE=1 check:placeholders.
# =============================================================================
set -uo pipefail

if [ "${BSUK_RELEASE:-}" != "1" ]; then
  echo "REFUSED: release-only command. Set BSUK_RELEASE=1 only when project 6 has a real domain and host." >&2
  exit 2
fi
exit 0
