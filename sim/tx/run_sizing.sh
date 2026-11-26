#!/usr/bin/env bash
# run_sizing.sh -- TX sizing grids through `klt sim`; commits an append-only record.
#
#   source scripts/env.sh && python3 -I sim/tx/make_tb.py && sim/tx/run_sizing.sh [mos|vce|ckswing]
#
# `ckswing`: the mux clock-swing sweep (tx_mosck_*, issue #98), record id suffixed -ckswing.
# No argument: the six HBT requests (tx_sizing_*). `mos`: the three MOS-cell requests
# (tx_mos_*: mux2to1_cml, tx_lvl_cml2cmos, ffe_en; issue #80), record id suffixed -mos.
# `vce`: the R3 per-device Vce pass (issue #242) -- the six HBT requests plus the
# mux2to1_cml and ffe_en requests (every TX bench with an HBT in it), record id
# suffixed -vce; tx_lvl_cml2cmos is not run (no HBT, R3 Vce n/a).
#
# The grid is multi-corner, so `klt sim` routes it to the batch fleet
# (KLT_SIM_BACKEND=batch). A failed batch submit is recorded as-is and the script
# exits non-zero; it never falls back to a local grid. Records are append-only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${HERE}/../.." && pwd)"
# shellcheck source=../tools/record-dir.sh
. "${REPO_DIR}/sim/tools/record-dir.sh"
command -v klt >/dev/null 2>&1 || { echo "run_sizing.sh: klt not on PATH -- source scripts/env.sh" >&2; exit 3; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "run_sizing.sh: PDK_ROOT unset -- source scripts/env.sh" >&2; exit 3; }
SIZING=(tx_sizing_ffe0_bcs tx_sizing_ffe0_typ tx_sizing_ffe0_wcs
        tx_sizing_ffe1_bcs tx_sizing_ffe1_typ tx_sizing_ffe1_wcs)
SET="${1:-hbt}"
case "${SET}" in
  hbt) REQS=("${SIZING[@]}"); SUFFIX=""; RECORD=make_record.py ;;
  mos) REQS=(tx_mos_mux2to1_cml tx_mos_tx_lvl_cml2cmos tx_mos_ffe_en); SUFFIX="-mos"; RECORD=make_record_mos.py ;;
  vce) REQS=("${SIZING[@]}" tx_mos_mux2to1_cml tx_mos_ffe_en); SUFFIX="-vce"; RECORD=make_record_vce.py ;;
  ckswing) REQS=(tx_mosck_mux2to1_cml_sw{100,200,300}); SUFFIX="-ckswing"; RECORD=make_record_ckswing.py ;;
  *) echo "run_sizing.sh: unknown set '${SET}' (hbt|mos|vce|ckswing)" >&2; exit 2 ;;
esac
# Exclusive reservation: a same-second relaunch refuses instead of overwriting
# the saved record (issue #202).
OUT="$(reserve_sim_record_dir "${HERE}/records" "${SUFFIX}")" || exit 3
r=0
: > "${OUT}/exit-codes.txt"
for tag in "${REQS[@]}"; do
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
