#!/usr/bin/env bash
# run_smoke.sh -- run the toolchain smoke grid through `klt sim` and commit a record.
#
#   source scripts/env.sh && sim/smoke/run_smoke.sh
#
# The grids are multi-corner, so `klt sim` routes them to the batch fleet when
# KLT_SIM_BACKEND=batch (the shared worker host exports it). This script never
# falls back to a local grid: a failed batch submit is recorded as-is and the
# script exits non-zero. Reports go to sim/smoke/records/<id>/ and are
# append-only evidence -- never edit or delete an earlier record directory.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${HERE}/../.." && pwd)"
command -v klt >/dev/null 2>&1 || { echo "run_smoke.sh: klt not on PATH -- 'source scripts/env.sh' after scripts/setup-env.sh" >&2; exit 3; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "run_smoke.sh: PDK_ROOT unset -- 'source scripts/env.sh'" >&2; exit 3; }

ID="$(date -u +%Y%m%d-%H%M%S)-$(git -C "${REPO_DIR}" rev-parse --short HEAD)"
OUT="${HERE}/records/${ID}"
mkdir -p "${OUT}"

rc=0
for req in hbt_gummel mos_inv_dc mixed_tran; do
  echo "run_smoke.sh: klt sim ${req}.request.json"
  ( cd "${HERE}" && klt sim --format json --wait-for-capacity 900 \
      --report-out "${OUT}/${req}.report.json" "${req}.request.json" \
      >/dev/null 2>"${OUT}/${req}.stderr.txt" )
  r=$?
  echo "${req} exit=${r}" | tee -a "${OUT}/exit-codes.txt"
  [[ ${r} -eq 0 ]] || rc=1
done

python3 -I "${HERE}/make_record.py" "${OUT}" || rc=1
exit ${rc}
