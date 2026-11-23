#!/usr/bin/env bash
# Re-run the pad/ESD layout generator into a new dated, append-only record.
#   source scripts/env.sh; layout/analog/pads/regen.sh [<sha>]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/../../.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$repo/scripts/klt-lib.sh"
sha="${1:-$(git -C "$here" rev-parse --short HEAD)}"
out="$here/records/$(date -u +%F)-$sha"
reserve_record_dir "$out" "regen.sh" 2
exec python3 -I "$here/gen_pad_cells.py" "$out"
