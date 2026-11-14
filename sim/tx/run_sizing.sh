#!/usr/bin/env bash
# run_sizing.sh -- TX sizing grids through `klt sim`; commits an append-only record.
#
#   source scripts/env.sh && python3 -I sim/tx/make_tb.py && sim/tx/run_sizing.sh [mos|ckswing]
#
# `ckswing`: the mux clock-swing sweep (tx_mosck_*, issue #98), record id suffixed -ckswing.
# No argument: the six HBT requests (tx_sizing_*). `mos`: the three MOS-cell requests
# (tx_mos_*: mux2to1_cml, tx_lvl_cml2cmos, ffe_en; issue #80), record id suffixed -mos.
#
# The grid is multi-corner, so `klt sim` routes it to the batch fleet
# (KLT_SIM_BACKEND=batch). A failed batch submit is recorded as-is and the script
# exits non-zero; it never falls back to a local grid. Records are append-only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${HERE}/../.." && pwd)"
command -v klt >/dev/null 2>&1 || { echo "run_sizing.sh: klt not on PATH -- source scripts/env.sh" >&2; exit 3; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "run_sizing.sh: PDK_ROOT unset -- source scripts/env.sh" >&2; exit 3; }
SET="${1:-hbt}"
case "${SET}" in
  hbt) PREFIX=tx_sizing; SUFFIX=""; RECORD=make_record.py ;;
  mos) PREFIX=tx_mos; SUFFIX="-mos"; RECORD=make_record_mos.py ;;
  ckswing) PREFIX=tx_mosck; SUFFIX="-ckswing"; RECORD=make_record_ckswing.py ;;
  *) echo "run_sizing.sh: unknown set '${SET}' (hbt|mos|ckswing)" >&2; exit 2 ;;
esac
ID="$(date -u +%Y%m%d-%H%M%S)-$(git -C "${REPO_DIR}" rev-parse --short HEAD)${SUFFIX}"
OUT="${HERE}/records/${ID}"
mkdir -p "${OUT}"
r=0
: > "${OUT}/exit-codes.txt"
for req in "${HERE}"/${PREFIX}_*.request.json; do
  tag="$(basename "${req}" .request.json)"
  ( cd "${HERE}" && klt sim --format json --wait-for-capacity 900 \
      --report-out "${OUT}/${tag}.report.json" "${tag}.request.json" \
      >/dev/null 2>"${OUT}/${tag}.stderr.txt" )
  e=$?
  echo "${tag} exit=${e}" | tee -a "${OUT}/exit-codes.txt"
  # exit 3 = a declared limit failed: the report is still complete evidence
  [[ ${e} -eq 0 || ${e} -eq 3 ]] || r=1
done
python3 -I "${HERE}/${RECORD}" "${OUT}" || r=1
exit ${r}
