#!/usr/bin/env bash
# run_sizing.sh -- TX HBT sizing grid through `klt sim`; commits an append-only record.
#
#   source scripts/env.sh && python3 -I sim/tx/make_tb.py && sim/tx/run_sizing.sh
#
# The grid is multi-corner, so `klt sim` routes it to the batch fleet
# (KLT_SIM_BACKEND=batch). A failed batch submit is recorded as-is and the script
# exits non-zero; it never falls back to a local grid. Records are append-only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${HERE}/../.." && pwd)"
command -v klt >/dev/null 2>&1 || { echo "run_sizing.sh: klt not on PATH -- source scripts/env.sh" >&2; exit 3; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "run_sizing.sh: PDK_ROOT unset -- source scripts/env.sh" >&2; exit 3; }
ID="$(date -u +%Y%m%d-%H%M%S)-$(git -C "${REPO_DIR}" rev-parse --short HEAD)"
OUT="${HERE}/records/${ID}"
mkdir -p "${OUT}"
r=0
: > "${OUT}/exit-codes.txt"
for req in "${HERE}"/tx_sizing_*.request.json; do
  tag="$(basename "${req}" .request.json)"
  ( cd "${HERE}" && klt sim --format json --wait-for-capacity 900 \
      --report-out "${OUT}/${tag}.report.json" "${tag}.request.json" \
      >/dev/null 2>"${OUT}/${tag}.stderr.txt" )
  e=$?
  echo "${tag} exit=${e}" | tee -a "${OUT}/exit-codes.txt"
  # exit 3 = a declared limit failed: the report is still complete evidence
  [[ ${e} -eq 0 || ${e} -eq 3 ]] || r=1
done
python3 -I "${HERE}/make_record.py" "${OUT}" || r=1
exit ${r}
