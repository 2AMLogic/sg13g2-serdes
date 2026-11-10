#!/usr/bin/env bash
# check-pnr-fresh.sh -- fail when the committed place-and-route record is stale.
#
#   scripts/check-pnr-fresh.sh [--rerun]
#
# Exit 0: the newest layout/digital/records/*/report.json still matches the
#         committed netlist and standard-cell liberty, and the committed GDS,
#         DEF and post-route netlist exist.
# Exit 3: drift -- the synthesized netlist (RTL edit) or liberty changed; run
#         scripts/synth-regen.sh, then scripts/pnr-regen.sh, and commit.
# Exit 1: the record is missing or internally inconsistent.
#
# Cheap mode (default) is `klt place-and-route --check`: re-hashes the netlist and
# liberty against the report's provenance; no OpenROAD run. --rerun re-runs the
# flow and diffs verdict-bearing fields (about 10 minutes; not for CI).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/pnr-lib.sh
. "$ROOT/scripts/pnr-lib.sh"
pnr_env

REC="$(pnr_latest_record)"
[ -n "$REC" ] && [ -f "$REC/report.json" ] || { echo "check-pnr-fresh: no committed record (run scripts/pnr-regen.sh)" >&2; exit 1; }
TOP="$(jq -r .hdl_toplevel "$PNR_REQ")"
for f in "$TOP.gds" "$TOP.def" "${TOP}_postroute.v"; do
  [ -s "$REC/$f" ] || { echo "check-pnr-fresh: $REC/$f missing or empty" >&2; exit 1; }
done
[ "$(jq -r .status "$REC/report.json")" = ok ] || { echo "check-pnr-fresh: committed report status is not ok" >&2; exit 1; }

# The input netlist must be the one the synthesis record describes.
want="$(jq -r .netlist_sha256 "$ROOT/rtl/synth/$TOP.synth.json")"
got="$(sha256sum "$ROOT/rtl/synth/${TOP}_synth.v" | awk '{print $1}')"
[ "$want" = "$got" ] || { echo "check-pnr-fresh: synth netlist does not match rtl/synth/$TOP.synth.json" >&2; exit 1; }

args=(--check "$REC/report.json")
[ "${1:-}" = "--rerun" ] && args+=(--rerun)
(cd "$ROOT" && "${KLT[@]}" place-and-route "$PNR_REQ" "${args[@]}")
rc=$?
case $rc in
  0) echo "check-pnr-fresh: OK -- ${REC#"$ROOT"/} matches the netlist and liberty" ;;
  3) echo "check-pnr-fresh: STALE -- run scripts/synth-regen.sh then scripts/pnr-regen.sh and commit" >&2 ;;
  *) echo "check-pnr-fresh: klt --check failed (exit $rc)" >&2 ;;
esac
exit $rc
