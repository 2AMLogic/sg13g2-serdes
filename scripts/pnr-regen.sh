#!/usr/bin/env bash
# pnr-regen.sh -- re-run place-and-route on the committed gate-level netlist and
# write a NEW dated, append-only record under layout/digital/records/ (T1 item 2,
# Digital). Earlier records are never edited or removed.
#
#   scripts/pnr-regen.sh
#
# Input:  layout/digital/place-and-route.request.json (floorplan, IO layers, PDN
#         straps, clock, seed), which names rtl/synth/serdes_digital_top_synth.v.
# Output: layout/digital/records/<date>-<short-sha>/{report.json, *.gds, *.def,
#         *_postroute.v}; write record.md alongside. Run scripts/synth-regen.sh
#         first if the RTL changed. Single-unit local run (OpenROAD, about 10
#         minutes); the request is never fanned out as a grid.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/pnr-lib.sh
. "$ROOT/scripts/pnr-lib.sh"
pnr_env

TOP="$(jq -r .hdl_toplevel "$PNR_REQ")"
TMP="$(mktemp -d "$ROOT/.cache/pnr-regen.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
rm -rf "$ROOT/layout/digital/.klt"

(cd "$ROOT" && "${KLT[@]}" place-and-route "$PNR_REQ" --backend local --format json >"$TMP/report.json")
status="$(jq -r .status "$TMP/report.json")"
stage="$(jq -r .stage_reached "$TMP/report.json")"
[ "$status" = ok ] || { echo "pnr-regen.sh: status=$status stage_reached=$stage" >&2; exit 1; }

SHA="$(git -C "$ROOT" rev-parse --short=7 HEAD)"
DEST="$PNR_RECORDS/$(date -u +%Y-%m-%d)-$SHA"
[ ! -e "$DEST" ] || { echo "pnr-regen.sh: $DEST exists (records are append-only)" >&2; exit 1; }
mkdir -p "$DEST"
BUILD="$ROOT/layout/digital/.klt/place-and-route"
cp "$BUILD/$TOP.gds" "$DEST/$TOP.gds"
cp "$BUILD/$TOP.def" "$DEST/$TOP.def"
cp "$BUILD/$TOP.v" "$DEST/${TOP}_postroute.v"
jq . "$TMP/report.json" >"$DEST/report.json"
rm -rf "$ROOT/layout/digital/.klt"
echo "wrote ${DEST#"$ROOT"/} (stage_reached=$stage)"
jq -r '"  worst setup slack \(.worst_setup_slack_ns) ns (slowest corner)  route DRC \(.route_drc_violation_count)  antenna \(.antenna_violation_count)"' "$DEST/report.json"
echo "next: write record.md, then scripts/check-pnr-fresh.sh"
