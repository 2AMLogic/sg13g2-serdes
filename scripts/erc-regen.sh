#!/usr/bin/env bash
# erc-regen.sh -- klt erc supply-spec run on the routed digital GDS and a NEW
# dated, append-only record under layout/digital/erc-records/ (T1 item 11,
# Digital, cited as 11.digital). Earlier records are never edited or removed.
#
#   scripts/erc-regen.sh
#
# Input:  the newest layout/digital/records/*/ place-and-route record (routed
#         GDS) and layout/erc/digital.erc.json (the supply spec).
# Steps:  klt erc --validate-spec on the spec, then klt erc --findings-only
#         --omit-antenna-tables --deck sg13g2 run from the new record dir, so
#         the spec copy committed beside the report is the document klt
#         signoff re-reads (the report records "erc.spec.json", resolved
#         relative to the report, per docs/cli/signoff.md item 11).
# Output: layout/digital/erc-records/<date>-<sha>/{erc.report.json,
#         erc.spec.json}; write record.md alongside. The antenna half is
#         skipped on purpose (findings-only): item 11 grades the connectivity
#         rules, not the antenna ratios, and the per-gate accumulation
#         dominates runtime on a dense layout (docs/cli/erc.md, #2219);
#         --omit-antenna-tables keeps the committed report small. Exit 1 if
#         erc_status is not clean; the report is still written so a first
#         failure is kept. Single-unit local run: about one minute measured
#         (one process, never fanned out as a grid). No PDK install and no
#         openroad are needed -- unlike lvs-regen.sh this must NOT source
#         pnr-lib.sh, whose require_tool openroad would refuse on a runner.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"
klt_env

ERC_RECORDS="$ROOT/layout/digital/erc-records"
SPEC="$ROOT/layout/erc/digital.erc.json"
TOP="$(jq -r .hdl_toplevel "$ROOT/layout/digital/place-and-route.request.json")"
REC="$(ls -d "$ROOT"/layout/digital/records/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::')"
[ -n "$REC" ] || { echo "erc-regen: no place-and-route record (run scripts/pnr-regen.sh)" >&2; exit 1; }
GDS="$REC/$TOP.gds"
[ -f "$GDS" ] || { echo "erc-regen: $GDS missing" >&2; exit 1; }
[ -f "$SPEC" ] || { echo "erc-regen: $SPEC missing" >&2; exit 1; }

"${KLT[@]}" erc --validate-spec "$SPEC" --format json >/dev/null

SHA="$(git -C "$ROOT" rev-parse --short=7 HEAD)"
DEST="$ERC_RECORDS/$(date -u +%Y-%m-%d)-$SHA"
[ ! -e "$DEST" ] || { echo "erc-regen: $DEST exists (records are append-only)" >&2; exit 1; }
mkdir -p "$DEST"
cp -p "$SPEC" "$DEST/erc.spec.json"

rc=0
(cd "$DEST" && "${KLT[@]}" erc "$GDS" erc.spec.json --top "$TOP" \
    --deck sg13g2 --findings-only --omit-antenna-tables --format json \
    > erc.report.json) || rc=$?
jq . "$DEST/erc.report.json" >"$DEST/erc.report.json.tmp" && mv "$DEST/erc.report.json.tmp" "$DEST/erc.report.json"
echo "wrote ${DEST#"$ROOT"/} (klt erc exit $rc)"
jq -r '"  erc_status \(.erc_status)  findings \(.erc_findings | length)  islands VDD=\(.nets[] | select(.name == "VDD") | .matched_islands) VSS=\(.nets[] | select(.name == "VSS") | .matched_islands)  ties checked \(.erc_coverage.checked | map(select(startswith("erc.missing_tie"))) | length) skipped \(.erc_coverage.skipped | length)  undeclared_layers \(.erc_coverage.layers_in_stream_without_declaration | length)"' "$DEST/erc.report.json"
[ "$(jq -r .erc_status "$DEST/erc.report.json")" = clean ] || exit 1
echo "next: write record.md, then scripts/check-erc-fresh.sh"
