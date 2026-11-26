#!/usr/bin/env bash
# check-synth-fresh.sh -- fail when the committed gate-level netlist is stale.
#
#   scripts/check-synth-fresh.sh
#
# Exit 0: the committed report still matches the RTL listed in
#         rtl/synth/request.json and the standard-cell liberty, and the
#         committed netlist is the one the report describes.
# Exit 3: drift -- an RTL source, the request or the liberty changed since the
#         report was generated. Run scripts/synth-regen.sh and commit rtl/synth/.
# Exit 1: the committed netlist does not match the report's recorded hash.
#
# Uses `klt synthesize --check` (content hashes of the sources and liberty; no
# Yosys run) with the pinned klt from layout/toolchain.json. Cheap enough for CI.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"
klt_env
# No yosys check: `klt synthesize --check` hashes the sources and the liberty,
# it never runs the synthesizer. The liberty sentinel is the one PDK file the
# hash walk reads.
REQ="$ROOT/rtl/synth/request.json"
require_request_liberty "$REQ" check-synth-fresh
TOP="$(jq -r .hdl_toplevel "$REQ")"
REPORT="$ROOT/rtl/synth/${TOP}.synth.json"
NETLIST="$ROOT/rtl/synth/${TOP}_synth.v"
[ -f "$REPORT" ] && [ -f "$NETLIST" ] || { echo "check-synth-fresh: committed report/netlist missing (run scripts/synth-regen.sh)" >&2; exit 1; }

want="$(jq -r .netlist_sha256 "$REPORT")"
got="$(sha256sum "$NETLIST" | awk '{print $1}')"
if [ "$want" != "$got" ]; then
  echo "check-synth-fresh: STALE -- ${TOP}_synth.v hash $got != report $want" >&2
  exit 1
fi

"${KLT[@]}" synthesize "$REQ" --check "$REPORT" --netlist "$NETLIST"
rc=$?
case $rc in
  0) echo "check-synth-fresh: OK -- netlist and envelope match the RTL" ;;
  3) echo "check-synth-fresh: STALE -- RTL/request/liberty changed; run scripts/synth-regen.sh and commit rtl/synth/" >&2 ;;
  *) echo "check-synth-fresh: klt --check failed (exit $rc)" >&2 ;;
esac
exit $rc
