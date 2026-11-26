#!/usr/bin/env bash
# run_sizing.sh -- run the RX sizing grids through `klt sim` and write a record.
#
#   source scripts/env.sh && sim/rx/run_sizing.sh [vce]    # the five HBT grids
#   source scripts/env.sh && sim/rx/run_sizing.sh mos      # lvl_cml2cmos (MOS set)
#
# Each request runs on the batch fleet via `klt sim --backend batch`.
# A failed submission is recorded as-is. Records under sim/rx/records/<id>/ are
# append-only evidence -- never edit or delete an earlier record directory.
# The requests and bench bodies are generated: sim/rx/tools/gen_requests.py.
# `vce`: record id suffixed -vce (the R3 per-device Vce pass of issue #242); the
#        same five HBT requests run.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${HERE}/../.." && pwd)"
# shellcheck source=../tools/record-dir.sh
. "${REPO_DIR}/sim/tools/record-dir.sh"
command -v klt >/dev/null 2>&1 || { echo "run_sizing.sh: klt not on PATH" >&2; exit 3; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "run_sizing.sh: PDK_ROOT unset -- 'source scripts/env.sh'" >&2; exit 3; }
"${REPO_DIR}/design/check-netlists.sh" >/dev/null || { echo "run_sizing.sh: netlists are stale or missing; run design/check-netlists.sh" >&2; exit 3; }

# `mos`: the lvl_cml2cmos bench (PSP103 via osdi_preload, 45-corner MOS set,
# record id suffixed -mos), issue #241. No argument: the five HBT grids.
SET="${1:-hbt}"
case "${SET}" in
  hbt|vce)
    REQS=(ctle_ac ctle_op ctle_tran pad_ac latch_regen)
    SUFFIX=""
    [[ "${SET}" == "vce" ]] && SUFFIX="-vce"
    RECORD=make_record.py ;;
  mos) REQS=(lvl_cml2cmos); SUFFIX="-mos"; RECORD=make_record_mos.py ;;
  *) echo "run_sizing.sh: unknown set '${SET}' (hbt|vce|mos)" >&2; exit 2 ;;
esac

# Exclusive reservation: a same-second relaunch refuses instead of overwriting
# the saved record (issue #202).
OUT="$(reserve_sim_record_dir "${HERE}/records" "${SUFFIX}")" || exit 3
rc=0
for req in "${REQS[@]}"; do
  echo "run_sizing.sh: klt sim ${req}.request.json"
  ( cd "${HERE}" && klt sim --backend batch --format json --wait-for-capacity 900 \
      --report-out "${OUT}/${req}.report.json" "${req}.request.json" \
      >/dev/null 2>"${OUT}/${req}.stderr.txt" )
  r=$?
  echo "${req} exit=${r}" | tee -a "${OUT}/exit-codes.txt"
  [[ ${r} -eq 0 ]] || rc=1
done
python3 -I "${HERE}/tools/${RECORD}" "${OUT}" || rc=1
exit ${rc}
