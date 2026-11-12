#!/usr/bin/env bash
# lvs-regen.sh -- gate-level LVS of the routed digital partition and a NEW dated,
# append-only record under layout/digital/lvs-records/ (T1 item 4, Digital).
# Earlier records are never edited or removed.
#
#   scripts/lvs-regen.sh
#
# Input:  the newest layout/digital/records/*/ place-and-route record (routed GDS
#         and *_postroute.v) and layout/digital/lvs.request.json (template).
# Steps:  klt extract --abstract-cells (layout side, every stdcell a pin-only
#         black box, LEF pins, DEF net names) -> klt lvs against the post-route
#         gate-level Verilog (reference.form gate-level-verilog), with
#         power_connectivity.expected_nets declared.
# Output: layout/digital/lvs-records/<date>-<sha>/{lvs.report.json,
#         lvs.request.json, <top>.gate.spice}; write record.md alongside.
#         Single-unit local run: the extraction alone takes about 15 minutes
#         (one process, never fanned out as a grid). Exit 1 if the compare is
#         not `match`; the report is still written so the first mismatch is kept.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/pnr-lib.sh
. "$ROOT/scripts/pnr-lib.sh"
pnr_env

REC="$(pnr_latest_record)"
[ -n "$REC" ] || { echo "lvs-regen: no place-and-route record (run scripts/pnr-regen.sh)" >&2; exit 1; }
TOP="$(jq -r .hdl_toplevel "$PNR_REQ")"
LEF="$PDK_ROOT/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef"
[ -f "$LEF" ] || { echo "lvs-regen: $LEF missing" >&2; exit 3; }

SHA="$(git -C "$ROOT" rev-parse --short=7 HEAD)"
DEST="$ROOT/layout/digital/lvs-records/$(date -u +%Y-%m-%d)-$SHA"
[ ! -e "$DEST" ] || { echo "lvs-regen: $DEST exists (records are append-only)" >&2; exit 1; }
mkdir -p "$DEST"

"${KLT[@]}" extract "$REC/$TOP.gds" --deck sg13g2 --abstract-cells 'sg13g2_*' \
  --abstract-cell-lef "$LEF" --def-net-names -o "$DEST/$TOP.gate.spice" --format json >"$DEST/extract.json"
rm -f "$DEST/extract.json"   # large; the netlist hash is carried by the LVS report

# Paths in the request resolve relative to the request file.
jq --arg g "$TOP.gate.spice" --arg v "../../records/$(basename "$REC")/${TOP}_postroute.v" \
  'del(._comment) | .layout.netlist = $g | .reference.netlist = $v' \
  "$ROOT/layout/digital/lvs.request.json" >"$DEST/lvs.request.json"

rc=0
(cd "$ROOT" && "${KLT[@]}" lvs "${DEST#"$ROOT"/}/lvs.request.json" --format json >"$DEST/lvs.report.json") || rc=$?
jq . "$DEST/lvs.report.json" >"$DEST/lvs.report.json.tmp" && mv "$DEST/lvs.report.json.tmp" "$DEST/lvs.report.json"
echo "wrote ${DEST#"$ROOT"/} (klt lvs exit $rc)"
jq -r '"  status \(.status)  engine \(.engine) \(.environment.engine_version)  power_connectivity \(.power_connectivity.status)  mismatches \(.mismatch_count)"' "$DEST/lvs.report.json"
[ "$(jq -r .status "$DEST/lvs.report.json")" = match ] || exit 1
echo "next: write record.md, then scripts/check-lvs-fresh.sh"
