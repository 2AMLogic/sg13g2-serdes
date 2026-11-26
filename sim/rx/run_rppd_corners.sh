#!/usr/bin/env bash
# run_rppd_corners.sh -- RX termination rppd resistor-corner run (issue #240,
# R9 gate G1 of #238) through `klt sim`, written as an append-only record.
#
#   source scripts/env.sh && sim/rx/run_rppd_corners.sh
#
# Two requests, one record: the 27-point grid over the RES library corners
# (ganged with the same-index HBT/CAP/DIO sections) and the two p.11 window
# members whose rsh_rppd override traces to spec/sources/rppd-tolerance-window.md.
# Both are multi-corner requests, so `klt sim` routes them to the batch fleet
# (KLT_SIM_BACKEND=batch). This script never falls back to a local grid: a
# failed submit is recorded as-is. Records under sim/rx/records/<id>/ are
# append-only evidence -- never edit or delete an earlier record directory.
# The requests and bench bodies are generated: sim/rx/tools/gen_requests.py.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${HERE}/../.." && pwd)"
# shellcheck source=../tools/record-dir.sh
. "${REPO_DIR}/sim/tools/record-dir.sh"
command -v klt >/dev/null 2>&1 || { echo "run_rppd_corners.sh: klt not on PATH" >&2; exit 3; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "run_rppd_corners.sh: PDK_ROOT unset -- 'source scripts/env.sh'" >&2; exit 3; }
"${REPO_DIR}/design/check-netlists.sh" >/dev/null || { echo "run_rppd_corners.sh: netlists are stale or missing; run design/check-netlists.sh" >&2; exit 3; }

# Exclusive reservation: a same-second relaunch refuses instead of overwriting
# the saved record (issue #202). The -rppd-corners suffix names this run family.
OUT="$(reserve_record_dir "${HERE}/records" -rppd-corners)" || exit 3
rc=0
for req in pad_ac_rppd pad_ac_rppd_p11win; do
  echo "run_rppd_corners.sh: klt sim ${req}.request.json"
  ( cd "${HERE}" && klt sim --format json --wait-for-capacity 900 \
      --report-out "${OUT}/${req}.report.json" "${req}.request.json" \
      >/dev/null 2>"${OUT}/${req}.stderr.txt" )
  r=$?
  echo "${req} exit=${r}" | tee -a "${OUT}/exit-codes.txt"
  [[ ${r} -eq 0 ]] || rc=1
done
python3 -I "${HERE}/tools/make_record_rppd.py" "${OUT}" || rc=1
exit ${rc}
