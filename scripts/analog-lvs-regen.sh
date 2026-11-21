#!/usr/bin/env bash
# analog-lvs-regen.sh -- per-cell DRC + LVS evidence for the routed analog cells
# (issue #199, first split of #127), written INTO the newest generator record
# for each partition (the record dirs are append-only; this script only adds
# files the generator did not write, and refuses to overwrite existing ones).
#
#   scripts/analog-lvs-regen.sh
#
# For each of (rx lvl_cml2cmos, tx tx_lvl_cml2cmos) in the newest
# layout/analog/{rx,tx}/records/*/<cell>/ dir:
#   drc.request.json + drc.report.json   klt drc --deck sg13g2 on the routed GDS
#   lvs.request.json + lvs.report.json   klt lvs, layout extracted inline from
#                                        the same GDS, reference = the cell's
#                                        standalone subckt (reference.form
#                                        subckt-call), anchor_top_level_pins on,
#                                        combine_devices on (the TX converter
#                                        folds ng=2 fingers and the rppd body)
# Single-unit local run (seconds per cell); exit 1 if any DRC is not clean or
# any LVS is not `match` -- the reports are still written so a first mismatch
# is kept for the record.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"
klt_env

latest_record() { ls -d "$ROOT/layout/analog/$1/records"/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::'; }

run_cell() {  # run_cell <partition> <cell> <reference-netlist> <combine_devices>
  local part="$1" cell="$2" ref="$3" combine="$4"
  local rec dir
  rec="$(latest_record "$part")"
  [ -n "$rec" ] || { echo "analog-lvs-regen: no $part record (run the $part regen script)" >&2; exit 1; }
  dir="$rec/$cell"
  [ -f "$rec/$cell.gds" ] || { echo "analog-lvs-regen: $rec/$cell.gds missing" >&2; exit 1; }
  [ ! -f "$dir/lvs.report.json" ] || { echo "analog-lvs-regen: $dir/lvs.report.json exists (records are append-only)" >&2; exit 1; }
  mkdir -p "$dir"

  cat >"$dir/drc.request.json" <<EOF
{
  "schema": "klt.drc.request/1",
  "deck": "sg13g2",
  "engine": "curated",
  "file": "../$cell.gds",
  "top": "$cell"
}
EOF
  "${KLT[@]}" drc "$dir/drc.request.json" --format json >"$dir/drc.report.json"

  cat >"$dir/lvs.request.json" <<EOF
{
  "schema": "klt.lvs.request/1",
  "engine": "klayout",
  "layout": {"file": "../$cell.gds", "deck": "sg13g2", "top": "$cell"},
  "reference": {"netlist": "$ref", "top": "$cell", "form": "subckt-call", "deck": "sg13g2"},
  "options": {"anchor_top_level_pins": true, "combine_devices": $combine}
}
EOF
  (cd "$dir" && "${KLT[@]}" lvs lvs.request.json --format json >lvs.report.json)

  local drcs lvs_s power
  drcs="$(jq -r .status "$dir/drc.report.json")"
  lvs_s="$(jq -r .status "$dir/lvs.report.json")"
  power="$(jq -r .power_connectivity.status "$dir/lvs.report.json")"
  echo "$cell: drc=$drcs lvs=$lvs_s power=$power (record ${rec#"$ROOT"/})"
  [ "$drcs" = clean ] || rc=1
  [ "$lvs_s" = match ] || rc=1
  [ "$power" != mismatch ] || rc=1
  return "${rc:-0}"
}

rc=0
run_cell rx lvl_cml2cmos "../../../../../../design/rx/netlists/lvl_cml2cmos.spice" false || rc=1
run_cell tx tx_lvl_cml2cmos "../../../../../../design/tx/netlists/tx_lvl_cml2cmos.spice" true || rc=1
exit "$rc"
