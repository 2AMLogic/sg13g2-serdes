#!/usr/bin/env bash
# check-analog-lvs-fresh.sh -- fail when the committed per-cell analog LVS
# evidence is stale or not a match (issue #199; the analog counterpart of
# scripts/check-lvs-fresh.sh, which gates the digital partition).
#
#   scripts/check-analog-lvs-fresh.sh [--rerun]
#
# For each routed cell (rx lvl_cml2cmos, tx tx_lvl_cml2cmos), in the NEWEST
# layout/analog/<part>/records/*/<cell>/ that carries an lvs.report.json:
#   Exit 0: DRC clean, LVS match, power_connectivity not mismatch, engine
#           named, and `klt lvs --check` (cheap mode; --rerun re-compares)
#           exits 0 against the same GDS + standalone reference.
#   Exit 3: stale -- a newer generator record exists whose cells carry no LVS
#           evidence; run scripts/analog-lvs-regen.sh and commit.
#   Exit 1: the newest evidence is not a match / not clean / inconsistent.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"
klt_env

check_cell() {  # check_cell <partition> <cell>
  local part="$1" cell="$2" rec dir
  rec="$(ls -d "$ROOT/layout/analog/$part/records"/*/"$cell" 2>/dev/null | sort | tail -1)"
  if [ -z "$rec" ] || [ ! -f "$rec/lvs.report.json" ]; then
    echo "check-analog-lvs-fresh: no $cell LVS record (run scripts/analog-lvs-regen.sh)" >&2
    FAIL=1
    return
  fi
  dir="${rec#"$ROOT"/}"
  if [ ! -f "$rec/drc.report.json" ] || [ "$(jq -r .status "$rec/drc.report.json")" != clean ]; then
    echo "check-analog-lvs-fresh: $dir DRC report missing or not clean" >&2
    FAIL=1
    return
  fi
  # a newer generator record without LVS evidence makes this stale
  local newest
  newest="$(ls -d "$ROOT/layout/analog/$part/records"/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::')"
  if [ "$newest" -nt "$rec" ] && [ ! -f "$newest/$cell/lvs.report.json" ]; then
    echo "check-analog-lvs-fresh: STALE -- newer $part record $newest has no $cell LVS evidence; run scripts/analog-lvs-regen.sh" >&2
    STALE=1
    return
  fi
  local power engine
  [ "$(jq -r .status "$rec/lvs.report.json")" = match ] || { echo "check-analog-lvs-fresh: $dir lvs.report.json is not a match" >&2; FAIL=1; return; }
  power="$(jq -r .power_connectivity.status "$rec/lvs.report.json")"
  [ "$power" != mismatch ] || { echo "check-analog-lvs-fresh: $dir power_connectivity.status is mismatch" >&2; FAIL=1; return; }
  engine="$(jq -r .engine "$rec/lvs.report.json")"
  [ -n "$engine" ] && [ "$engine" != null ] || { echo "check-analog-lvs-fresh: $dir names no engine" >&2; FAIL=1; return; }

  local args=(--check lvs.report.json)
  [ "${1:-}" = "--rerun" ] && args+=(--rerun)
  (cd "$rec" && "${KLT[@]}" lvs "${args[@]}") >/dev/null 2>&1
  case $? in
    0) echo "check-analog-lvs-fresh: OK -- $dir matches its inputs (engine $engine, power $power)" ;;
    3) echo "check-analog-lvs-fresh: STALE -- $dir inputs drifted; run the $part regen script + scripts/analog-lvs-regen.sh" >&2; STALE=1 ;;
    *) echo "check-analog-lvs-fresh: klt lvs --check failed on $dir" >&2; FAIL=1 ;;
  esac
}

FAIL=0 STALE=0
check_cell rx lvl_cml2cmos "$@"
check_cell tx tx_lvl_cml2cmos "$@"
[ "$STALE" = 0 ] || exit 3
[ "$FAIL" = 0 ] || exit 1
exit 0
