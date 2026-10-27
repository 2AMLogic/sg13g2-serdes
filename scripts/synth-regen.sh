#!/usr/bin/env bash
# synth-regen.sh -- regenerate the committed synthesis evidence for the digital
# partition (T1 item 1, Digital): the gate-level netlist and the synthesis
# envelope under rtl/synth/, from rtl/synth/request.json and the RTL it lists.
#
#   scripts/synth-regen.sh
#
# Runs the PINNED klt (layout/toolchain.json) through a throwaway uvx
# environment, never a host-wide install. The PDK comes from $PDK_ROOT, else
# from the repo-local fetch .cache/pdk/IHP-Open-PDK-<release> (sim/pdk.json,
# scripts/setup-env.sh). Run it after ANY edit under rtl/*.v or to the request,
# then commit rtl/synth/; scripts/check-synth-fresh.sh fails until you do.
# Single-unit, local, a few minutes at most.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/synth-lib.sh
. "$ROOT/scripts/synth-lib.sh"
synth_env

OUT="$ROOT/rtl/synth"
REQ="$OUT/request.json"
TMP="$(mktemp -d "$ROOT/.cache/synth-regen.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
rm -rf "$OUT/.klt"

"${KLT[@]}" synthesize "$REQ" --format json >"$TMP/report.json"
status="$(jq -r .status "$TMP/report.json")"
crit="$(jq -r .structural.has_critical "$TMP/report.json")"
[ "$status" = ok ] && [ "$crit" = false ] || { echo "synth-regen.sh: synthesis status=$status has_critical=$crit" >&2; exit 1; }

NETLIST="$ROOT/$(jq -r .netlist_path.path "$TMP/report.json")"
TOP="$(jq -r .hdl_toplevel "$TMP/report.json")"
cp "$NETLIST" "$OUT/${TOP}_synth.v"
got="$(sha256sum "$OUT/${TOP}_synth.v" | awk '{print $1}')"
[ "$got" = "$(jq -r .netlist_sha256 "$TMP/report.json")" ] || { echo "synth-regen.sh: netlist hash differs from the report" >&2; exit 1; }
jq . "$TMP/report.json" >"$OUT/${TOP}.synth.json"
rm -rf "$OUT/.klt"
echo "regenerated: rtl/synth/${TOP}_synth.v and rtl/synth/${TOP}.synth.json"
jq -r '"  cells \(.instance_count)  area \(.area_um2) um2  abc critical path \(.timing.critical_path_ps) ps"' "$OUT/${TOP}.synth.json"
