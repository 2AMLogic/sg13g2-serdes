#!/usr/bin/env bash
# run_sizing.sh -- run the RX sizing grids through `klt sim` and write a record.
#
#   source scripts/env.sh && sim/rx/run_sizing.sh [vce]
#
# Each request is a 27-point HBT PVT grid, so `klt sim` routes it to the batch
# fleet (KLT_SIM_BACKEND=batch). This script never falls back to a local grid:
# a failed submit is recorded as-is. Records under sim/rx/records/<id>/ are
# append-only evidence -- never edit or delete an earlier record directory.
# The requests and bench bodies are generated: sim/rx/tools/gen_requests.py.
# `vce`: record id suffixed -vce (the R3 per-device Vce pass of issue #242); the
#        same four requests run, ctle_op and latch_regen now carrying per-HBT
#        vce_max cards.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${HERE}/../.." && pwd)"
# shellcheck source=../tools/record-dir.sh
. "${REPO_DIR}/sim/tools/record-dir.sh"
command -v klt >/dev/null 2>&1 || { echo "run_sizing.sh: klt not on PATH" >&2; exit 3; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "run_sizing.sh: PDK_ROOT unset -- 'source scripts/env.sh'" >&2; exit 3; }
"${REPO_DIR}/design/check-netlists.sh" >/dev/null || { echo "run_sizing.sh: netlists are stale or missing; run design/check-netlists.sh" >&2; exit 3; }

# `vce` suffix: the R3 per-device Vce pass (issue #242).
SUFFIX=""
[[ "${1:-}" == "vce" ]] && SUFFIX="-vce"

# Exclusive reservation: a same-second relaunch refuses instead of overwriting
# the saved record (issue #202).
OUT="$(reserve_record_dir "${HERE}/records" "${SUFFIX}")" || exit 3
rc=0
for req in ctle_ac ctle_op pad_ac latch_regen; do
  echo "run_sizing.sh: klt sim ${req}.request.json"
  ( cd "${HERE}" && klt sim --format json --wait-for-capacity 900 \
      --report-out "${OUT}/${req}.report.json" "${req}.request.json" \
      >/dev/null 2>"${OUT}/${req}.stderr.txt" )
  r=$?
  echo "${req} exit=${r}" | tee -a "${OUT}/exit-codes.txt"
  [[ ${r} -eq 0 ]] || rc=1
done
python3 -I "${HERE}/tools/make_record.py" "${OUT}" || rc=1
exit ${rc}
