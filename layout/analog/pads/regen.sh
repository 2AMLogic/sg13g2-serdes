#!/usr/bin/env bash
# Re-run the pad/ESD layout generator into a new dated, append-only record.
#   source scripts/env.sh; layout/analog/pads/regen.sh [<sha>]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
sha="${1:-$(git -C "$here" rev-parse --short HEAD)}"
out="$here/records/$(date -u +%F)-$sha"
[ -e "$out" ] && { echo "regen.sh: $out exists (records are append-only)" >&2; exit 2; }
mkdir -p "$out"
exec python3 -I "$here/gen_pad_cells.py" "$out"
