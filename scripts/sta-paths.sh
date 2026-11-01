#!/usr/bin/env bash
# sta-paths.sh -- gate-level static timing of the committed digital-partition
# netlist: `klt sta` aggregate (JSON) plus per-module worst setup paths.
#
#   scripts/sta-paths.sh [OUTDIR]     # default OUTDIR=.cache/sta
#
# Netlist-estimate timing: OpenSTA, ideal clock, no wire load, no placement
# (geometry_source "netlist_estimate"). It is a pre-layout figure, never a
# post-route one. Uses the pinned klt (layout/toolchain.json) through uvx and
# the host openroad; installs nothing. PDK from $PDK_ROOT or .cache/pdk.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/synth-lib.sh
. "$ROOT/scripts/synth-lib.sh"
synth_env
OUT="${1:-$ROOT/.cache/sta}"; mkdir -p "$OUT"
REQ="$ROOT/rtl/synth/request.json"
TOP="$(jq -r .hdl_toplevel "$REQ")"
PERIOD="$(jq -r .constraints.clock_period_ns "$REQ")"
CORNER="$(jq -r .pdk.corner "$REQ")"
cat >"$OUT/sta_request.json" <<J
{"schema":"klt.sta.request/1","verilog":"$ROOT/rtl/synth/${TOP}_synth.v","hdl_toplevel":"$TOP",
 "pdk":{"cell_library":"sg13g2_stdcell","corner":"$CORNER"},
 "constraints":{"clock_port":"clk","clock_period_ns":$PERIOD}}
J
"${KLT[@]}" sta "$OUT/sta_request.json" --format json >"$OUT/klt_sta.json"
S="$PDK_ROOT/ihp-sg13g2/libs.ref/sg13g2_stdcell"
sed -e "s|@LIB@|$S/lib/sg13g2_stdcell_$CORNER.lib|" -e "s|@LEF_TECH@|$S/lef/sg13g2_tech.lef|" \
    -e "s|@LEF_CELL@|$S/lef/sg13g2_stdcell.lef|" -e "s|@NETLIST@|$ROOT/rtl/synth/${TOP}_synth.v|" \
    -e "s|@TOP@|$TOP|" -e "s|@PERIOD@|$PERIOD|" "$ROOT/scripts/sta-paths.tcl" >"$OUT/sta-paths.run.tcl"
openroad -no_init -exit "$OUT/sta-paths.run.tcl" >"$OUT/paths.txt" 2>&1
jq -r '"worst setup slack \(.worst_slack_ns) ns at \(.hdl_toplevel) period '"$PERIOD"' ns; fmax \(.fmax_mhz) MHz; \(.setup_violation_count) violating endpoints"' "$OUT/klt_sta.json"
grep -E '^== |slack \(' "$OUT/paths.txt"
