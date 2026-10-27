#!/usr/bin/env bash
# check-netlists.sh -- netlist staleness gate for every design/<partition>/*.sch.
#
#   source scripts/env.sh && design/check-netlists.sh          # check: exit 0 match, 3 drifted
#   source scripts/env.sh && design/check-netlists.sh --write  # re-export after a schematic edit
#
# Netlists are exported only with `klt netlist` (never raw xschem). The
# committed netlist for design/<p>/<cell>.sch is design/<p>/netlists/<cell>.spice.
# Shared by every partition (RX, TX): the wrapper walks design/*/ and does not
# name a partition.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE=check; [[ "${1:-}" == "--write" ]] && MODE=write
command -v klt >/dev/null 2>&1 || { echo "check-netlists.sh: klt not on PATH" >&2; exit 1; }
[[ -n "${PDK_ROOT:-}" ]] || { echo "check-netlists.sh: PDK_ROOT unset -- 'source scripts/env.sh'" >&2; exit 1; }
rc=0
shopt -s nullglob
for sch in "${HERE}"/*/*.sch; do
  dir="$(dirname "${sch}")"; cell="$(basename "${sch}" .sch)"
  mkdir -p "${dir}/netlists"
  args=(--rcfile "${HERE}/xschemrc" --block -o "${dir}/netlists/${cell}.spice")
  [[ ${MODE} == check ]] && args+=(--check)
  klt netlist "${args[@]}" "${sch}" >/dev/null 2>&1
  r=$?
  echo "${cell}: exit ${r}"
  (( r > rc )) && rc=${r}
done
exit ${rc}
