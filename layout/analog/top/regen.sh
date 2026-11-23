#!/usr/bin/env bash
# Re-run the analog top assembly into a new dated, append-only record.
#   layout/analog/top/regen.sh [<sha>]
# Needs klayout.db only (no PDK): uses the repo-local .venv python
# (scripts/setup-env.sh) or $GEN_PYTHON.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/../../.." && pwd)"
py="${GEN_PYTHON:-$repo/.venv/bin/python}"
[ -x "$py" ] || { echo "regen.sh: $py missing; run scripts/setup-env.sh first" >&2; exit 3; }
sha="${1:-$(git -C "$here" rev-parse --short HEAD)}"
out="$here/records/$(date -u +%F)-$sha"
# shellcheck source=scripts/klt-lib.sh
. "$repo/scripts/klt-lib.sh"
reserve_record_dir "$out" "regen.sh" 2
exec "$py" -I "$here/gen_analog_top.py" "$out"
