#!/usr/bin/env bash
# Re-run the TX core cell generator into a new dated, append-only record.
#   source scripts/env.sh && layout/analog/tx/scripts/tx-core-regen.sh [outdir]
# Default outdir: layout/analog/tx/records/<date>-<short sha>/ (refuses to overwrite).
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
OUT="${1:-${R}/layout/analog/tx/records/$(date -u +%F)-$(git -C "${R}" rev-parse --short HEAD)}"
[[ -e "${OUT}" ]] && { echo "tx-core-regen: ${OUT} exists (records are append-only)" >&2; exit 2; }
"${R}/.venv/bin/python" -I "${R}/layout/analog/tx/gen_tx_core.py" "${R}/design/tx/netlists/tx_top.spice" "${OUT}" --klt "${R}/.venv/bin/klt"
echo "wrote ${OUT}"
