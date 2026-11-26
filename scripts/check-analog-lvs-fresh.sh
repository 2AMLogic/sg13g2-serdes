#!/usr/bin/env bash
# check-analog-lvs-fresh.sh -- fail when the committed per-cell analog LVS
# evidence is stale or not a match (issue #199; the analog counterpart of
# scripts/check-lvs-fresh.sh, which gates the digital partition).
#
#   scripts/check-analog-lvs-fresh.sh [--rerun]
#
# For each routed cell (rx lvl_cml2cmos, tx tx_lvl_cml2cmos) the NEWEST
# generator record layout/analog/<part>/records/*/ is selected first and must
# carry the cell's evidence (scripts/analog-cell-evidence-lib.sh, the one
# verdict for statuses, power rule and hash binding -- issue #281):
#   Exit 0: DRC clean and LVS match, both reports' input hashes name that
#           record's <cell>.gds (and LVS the standalone reference), power
#           connectivity not mismatch, engine named, and `klt lvs --check`
#           (cheap mode; --rerun re-compares) exits 0.
#   Exit 3: stale -- the newest record lacks the cell's DRC/LVS evidence, or
#           klt reports the inputs drifted; run scripts/analog-lvs-regen.sh
#           <part> and commit.
#   Exit 1: the newest evidence is not a match / not clean / power connectivity
#           mismatch / bound to a different GDS or reference.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"
klt_env
# shellcheck source=scripts/analog-cell-evidence-lib.sh
. "$ROOT/scripts/analog-cell-evidence-lib.sh"

RERUN=()
for a in "$@"; do
  case "$a" in
    --rerun) RERUN=(--rerun) ;;
    *) echo "usage: check-analog-lvs-fresh.sh [--rerun]" >&2; exit 2 ;;
  esac
done

check_cell() {  # check_cell <partition> <cell> <reference-netlist>
  local part="$1" cell="$2" ref="$3" rec dir rc=0 power engine
  rec="$(latest_record_dir "$ROOT/layout/analog/$part/records")"
  analog_cell_verify "$ROOT" "$rec" "$cell" "$ref" "check-analog-lvs-fresh" || rc=$?
  case $rc in
    0) ;;
    3) STALE=1; return ;;
    *) FAIL=1; return ;;
  esac
  dir="${rec#"$ROOT"/}/$cell"
  power="$(jq -r .power_connectivity.status "$ROOT/$dir/lvs.report.json")"
  engine="$(jq -r .engine "$ROOT/$dir/lvs.report.json")"
  [ -n "$engine" ] && [ "$engine" != null ] || { echo "check-analog-lvs-fresh: $dir names no engine" >&2; FAIL=1; return; }

  (cd "$ROOT/$dir" && "${KLT[@]}" lvs --check lvs.report.json "${RERUN[@]}") >/dev/null 2>&1
  case $? in
    0) echo "check-analog-lvs-fresh: OK -- $dir matches its inputs (engine $engine, power $power)" ;;
    3) echo "check-analog-lvs-fresh: STALE -- $dir inputs drifted; run the $part regen script + scripts/analog-lvs-regen.sh $part" >&2; STALE=1 ;;
    *) echo "check-analog-lvs-fresh: klt lvs --check failed on $dir" >&2; FAIL=1 ;;
  esac
}

FAIL=0 STALE=0
check_cell rx lvl_cml2cmos design/rx/netlists/lvl_cml2cmos.spice
check_cell tx tx_lvl_cml2cmos design/tx/netlists/tx_lvl_cml2cmos.spice
# a hard failure outranks a stale verdict
[ "$FAIL" = 0 ] || exit 1
[ "$STALE" = 0 ] || exit 3
exit 0
