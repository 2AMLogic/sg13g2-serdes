#!/usr/bin/env bash
# Re-run the RX core analog layout generator into a new dated, append-only record.
#   . scripts/env.sh; export PDK_ROOT PDK; layout/analog/rx/regen.sh [<sha>]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/../../.." && pwd)"
py="$repo/.venv/bin/python"
[ -x "$py" ] || { echo "regen.sh: $py missing; run scripts/setup-env.sh first" >&2; exit 3; }
sha="${1:-$(git -C "$here" rev-parse --short HEAD)}"
out="$here/records/$(date -u +%F)-$sha"
[ -e "$out" ] && { echo "regen.sh: $out exists (records are append-only)" >&2; exit 2; }
mkdir -p "$out"
exec "$py" -I "$here/gen_rx_cells.py" "$out"
