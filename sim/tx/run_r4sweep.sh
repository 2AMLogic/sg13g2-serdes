#!/usr/bin/env bash
# run_r4sweep.sh -- R4 swing-shortfall sweep (issue #286) through `klt sim`; append-only record.
#
#   source scripts/env.sh && python3 -I sim/tx/make_sweep_r4.py <proc>... && sim/tx/run_r4sweep.sh <proc> [tag]
#
# One request per candidate (sim/tx/r4sweep_<cand>_<proc>.request.json), submitted as one
# batch set to the Spot fleet (KLT_SIM_BACKEND=batch; never a local fallback).
# R4_CANDS=a,b limits the set (stage-2 reruns). The record id
# is suffixed -r4sweep-<proc>[-tag]. Records are append-only.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${HERE}/../.." && pwd)"
# shellcheck source=../tools/record-dir.sh
. "${REPO_DIR}/sim/tools/record-dir.sh"
command -v klt >/dev/null 2>&1 || { echo "run_r4sweep.sh: klt not on PATH -- source scripts/env.sh" >&2; exit 3; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "run_r4sweep.sh: PDK_ROOT unset -- source scripts/env.sh" >&2; exit 3; }
PROC="${1:?usage: run_r4sweep.sh <typ|bcs|wcs> [tag]}"
TAG="${2:+-$2}"
mapfile -t CANDS < <(python3 -I -c "import json,sys;print('\n'.join(c['id'] for c in json.load(open(sys.argv[1]))))" "${HERE}/r4sweep_candidates.json")
REQS=()
for c in "${CANDS[@]}"; do
  [[ -n "${R4_CANDS:-}" && ",${R4_CANDS}," != *",${c},"* ]] && continue
  [[ -f "${HERE}/r4sweep_${c}_${PROC}.request.json" ]] && REQS+=("r4sweep_${c}_${PROC}.request.json")
done
[[ ${#REQS[@]} -gt 0 ]] || { echo "run_r4sweep.sh: no requests for ${PROC} -- run make_sweep_r4.py ${PROC}" >&2; exit 3; }
OUT="$(reserve_sim_record_dir "${HERE}/records" "-r4sweep-${PROC}${TAG}")" || exit 3
printf '%s\n' "${REQS[@]}" >"${OUT}/requests.txt"
( cd "${HERE}" && klt sim --format json --wait-for-capacity 600 --max-in-flight 2 \
    --batch-set "${REQS[@]}" -o "${OUT}/batch" >"${OUT}/envelope.json" 2>"${OUT}/stderr.txt" )
e=$?
echo "batch-set exit=${e}" | tee "${OUT}/exit-codes.txt"
python3 -I "${HERE}/make_record_r4sweep.py" "${OUT}" "${PROC}" || exit 1
[[ ${e} -eq 0 || ${e} -eq 3 ]]
