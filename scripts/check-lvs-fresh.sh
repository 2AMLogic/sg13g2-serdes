#!/usr/bin/env bash
# check-lvs-fresh.sh -- fail when the committed digital LVS record is stale.
#
#   scripts/check-lvs-fresh.sh [--rerun]
#
# Exit 0: the newest layout/digital/lvs-records/*/lvs.report.json is `match`, its
#         power_connectivity is not mismatch/unchecked, and the layout netlist
#         and reference hashes still match (`klt lvs --check`).
# Exit 3: drift -- the routed GDS/post-route netlist changed after the record
#         (new place-and-route record); run scripts/lvs-regen.sh and commit.
# Exit 1: the record is missing, not a match, or inconsistent.
# Cheap mode (default) re-hashes only; --rerun re-runs the compare (the layout
# netlist is the committed extraction, so this does not repeat the extraction).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"
klt_env
# Cheap mode re-hashes only and reads nothing under PDK_ROOT. A --rerun compare
# re-runs the gate-level-Verilog conversion, which reads the stdcell SPICE pin
# orders, so that sentinel is required in --rerun mode alone. Neither mode
# invokes openroad or reads the stdcell LEF.
if [ "${1:-}" = "--rerun" ]; then
  require_pdk_file ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice \
    "check-lvs-fresh: SG13G2 stdcell SPICE not found under PDK_ROOT=$PDK_ROOT (run scripts/setup-env.sh)"
fi

LREC="$(latest_record_dir "$ROOT/layout/digital/lvs-records")"
[ -n "$LREC" ] && [ -f "$LREC/lvs.report.json" ] || { echo "check-lvs-fresh: no committed record (run scripts/lvs-regen.sh)" >&2; exit 1; }
R="$LREC/lvs.report.json"
[ "$(jq -r .status "$R")" = match ] || { echo "check-lvs-fresh: committed report status is not match" >&2; exit 1; }
pc="$(jq -r .power_connectivity.status "$R")"
[ "$pc" = match ] || { echo "check-lvs-fresh: power_connectivity.status is '$pc', not match" >&2; exit 1; }

# The reference must be the newest place-and-route record's netlist, and the
# extraction must be of that record's GDS (a newer pnr record makes this stale).
PREC="$(latest_record_dir "$ROOT/layout/digital/records")"; TOP="$(jq -r .hdl_toplevel "$ROOT/layout/digital/place-and-route.request.json")"
want="$(sha256sum "$PREC/${TOP}_postroute.v" | awk '{print $1}')"
[ "$want" = "$(jq -r .environment.reference_sha256 "$R")" ] || { echo "check-lvs-fresh: STALE -- newest place-and-route record's netlist is not the one LVS compared; run scripts/lvs-regen.sh" >&2; exit 3; }

# Run from the record dir: `klt lvs --check` resolves the report's relative reference
# path against the cwd, while the run resolved it against the request file (same dir).
args=(--check lvs.report.json)
[ "${1:-}" = "--rerun" ] && args+=(--rerun)
(cd "$LREC" && "${KLT[@]}" lvs "${args[@]}")
rc=$?
case $rc in
  0) echo "check-lvs-fresh: OK -- ${LREC#"$ROOT"/} matches its inputs" ;;
  3) echo "check-lvs-fresh: STALE -- run scripts/lvs-regen.sh and commit" >&2 ;;
  *) echo "check-lvs-fresh: klt lvs --check failed (exit $rc)" >&2 ;;
esac
exit $rc
