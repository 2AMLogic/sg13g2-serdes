#!/usr/bin/env bash
# analog-cell-evidence-lib.sh -- sourced by scripts/check-ci.sh (the `fresh`
# axes 7-8) and scripts/check-analog-lvs-fresh.sh. PDK-free: jq + sha256sum.
#
#   analog_cell_verify <repo-root> <partition> <cell> <reference-netlist> [tag]
#
# Selects the NEWEST generator record of the partition first
# (layout/analog/<part>/records/*/, lexical = date order), then requires that
# record to carry the evidence for the cell and binds it to that record:
#   - <rec>/<cell>.gds exists (the routed GDS the generator wrote);
#   - <rec>/<cell>/drc.report.json: status clean, and its
#     .provenance.input.content_hash == sha256 of <rec>/<cell>.gds;
#   - <rec>/<cell>/lvs.report.json: status match, .environment.layout_sha256
#     == sha256 of <rec>/<cell>.gds, .environment.reference_sha256 == sha256 of
#     the standalone reference subcircuit netlist.
# An older record's evidence never stands in for a newer record's GDS.
# Return: 0 verified, 3 stale (newest record lacks evidence for the cell),
# 1 evidence present but not clean / not a match / bound to other inputs.
# Errors go to stderr as `::error file=...::<tag>: ...` annotations.

analog_cell_verify() {
  local root="$1" part="$2" cell="$3" ref="$4" tag="${5:-analog}"
  local rec drc lvs gds want got rc=0
  rec=$(ls -d "$root/layout/analog/$part/records"/*/ 2>/dev/null | sort | tail -1)
  rec=${rec%/}
  [ -n "$rec" ] || { echo "::error::$tag: no $part generator record" >&2; return 3; }
  rec=${rec#"$root"/}
  gds="$root/$rec/$cell.gds"
  drc="$root/$rec/$cell/drc.report.json"
  lvs="$root/$rec/$cell/lvs.report.json"
  [ -f "$gds" ] || { echo "::error file=$rec::$tag: newest $part record has no $cell.gds" >&2; return 3; }
  if [ ! -f "$drc" ] || [ ! -f "$lvs" ]; then
    echo "::error file=$rec::$tag: STALE -- newest $part record has no $cell DRC/LVS evidence (run scripts/analog-lvs-regen.sh $part)" >&2
    return 3
  fi
  want=$(sha256sum "$gds" | awk '{print $1}')
  [ "$(jq -r .status "$drc")" = clean ] \
    || { echo "::error file=$rec/$cell/drc.report.json::$tag: DRC status is not clean" >&2; rc=1; }
  got=$(jq -r '.provenance.input.content_hash // empty' "$drc")
  [ "${got#sha256:}" = "$want" ] \
    || { echo "::error file=$rec/$cell/drc.report.json::$tag: DRC input hash '${got}' is not $rec/$cell.gds (sha256:$want)" >&2; rc=1; }
  [ "$(jq -r .status "$lvs")" = match ] \
    || { echo "::error file=$rec/$cell/lvs.report.json::$tag: LVS status is not match" >&2; rc=1; }
  got=$(jq -r '.environment.layout_sha256 // empty' "$lvs")
  [ "$got" = "$want" ] \
    || { echo "::error file=$rec/$cell/lvs.report.json::$tag: LVS layout hash '${got}' is not $rec/$cell.gds ($want)" >&2; rc=1; }
  want=$(sha256sum "$root/$ref" 2>/dev/null | awk '{print $1}')
  got=$(jq -r '.environment.reference_sha256 // empty' "$lvs")
  { [ -n "$want" ] && [ "$got" = "$want" ]; } \
    || { echo "::error file=$rec/$cell/lvs.report.json::$tag: LVS reference hash '${got}' is not $ref ($want)" >&2; rc=1; }
  return "$rc"
}
