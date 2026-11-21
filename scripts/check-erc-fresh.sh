#!/usr/bin/env bash
# check-erc-fresh.sh -- fail when the committed digital ERC record is stale.
#
#   scripts/check-erc-fresh.sh [--rerun]
#
# Exit 0: the newest layout/digital/erc-records/*/erc.report.json has
#         erc_status clean, it checked the newest place-and-route record's
#         GDS and the canonical supply spec, and `klt erc --check` verifies
#         its archived inputs and deck.
# Exit 3: the P&R record, GDS, supply spec or deck has drifted since the run.
# Exit 1: the record is missing or not clean.
# Cheap mode (default) re-hashes only; --rerun re-runs the ERC and diffs the
# verdict-bearing fields (about one minute, same flags as erc-regen.sh).
# Like erc-regen.sh this sources klt-lib.sh, not pnr-lib.sh: no openroad, no
# PDK_ROOT file checks -- `klt erc` needs neither.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"
# shellcheck source=scripts/erc-fresh-lib.sh
. "$ROOT/scripts/erc-fresh-lib.sh"
klt_env
cd "$ROOT" || exit 1

EREC="$(ls -d layout/digital/erc-records/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::')"
[ -n "$EREC" ] && [ -f "$EREC/erc.report.json" ] || { echo "check-erc-fresh: no committed record (run scripts/erc-regen.sh)" >&2; exit 1; }
TOP="$(jq -r .hdl_toplevel layout/digital/place-and-route.request.json)"
PREC="$(ls -d layout/digital/records/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::')"
erc_check_inputs "$EREC/erc.report.json" "$PREC/$TOP.gds" || exit $?

# Run from the record dir: `klt erc --check` resolves the report's spec path
# against the report, while the GDS is echoed repo-scoped.
args=(--check erc.report.json)
[ "${1:-}" = "--rerun" ] && args+=(--rerun)
(cd "$EREC" && "${KLT[@]}" erc "${args[@]}")
rc=$?
case $rc in
  0) echo "check-erc-fresh: OK -- $EREC matches its inputs" ;;
  3) echo "check-erc-fresh: STALE -- run scripts/erc-regen.sh and commit" >&2 ;;
  *) echo "check-erc-fresh: klt erc --check failed (exit $rc)" >&2 ;;
esac
exit $rc
