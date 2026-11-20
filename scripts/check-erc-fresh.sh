#!/usr/bin/env bash
# check-erc-fresh.sh -- fail when the committed digital ERC record is stale.
#
#   scripts/check-erc-fresh.sh [--rerun]
#
# Exit 0: the newest layout/digital/erc-records/*/erc.report.json has
#         erc_status clean, it checked the newest place-and-route record's
#         GDS, and `klt erc --check` re-hashes its layout, spec and deck
#         consistently.
# Exit 3: drift -- a newer place-and-route record exists than the one the ERC
#         report checked; run scripts/erc-regen.sh and commit.
# Exit 1: the record is missing or not clean.
# Cheap mode (default) re-hashes only; --rerun re-runs the ERC and diffs the
# verdict-bearing fields (about one minute, same flags as erc-regen.sh).
# Like erc-regen.sh this sources klt-lib.sh, not pnr-lib.sh: no openroad, no
# PDK_ROOT file checks -- `klt erc` needs neither.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"
klt_env

EREC="$(ls -d "$ROOT"/layout/digital/erc-records/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::')"
[ -n "$EREC" ] && [ -f "$EREC/erc.report.json" ] || { echo "check-erc-fresh: no committed record (run scripts/erc-regen.sh)" >&2; exit 1; }
R="$EREC/erc.report.json"
[ "$(jq -r .erc_status "$R")" = clean ] || { echo "check-erc-fresh: committed report erc_status is not clean" >&2; exit 1; }

# The checked GDS must be the newest place-and-route record's routed layout
# (a newer pnr record makes this stale).
TOP="$(jq -r .hdl_toplevel "$ROOT/layout/digital/place-and-route.request.json")"
PREC="$(ls -d "$ROOT"/layout/digital/records/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::')"
want="$(sha256sum "$PREC/$TOP.gds" | awk '{print $1}')"
[ "$want" = "$(jq -r .provenance.input.content_hash "$R" | sed 's#^sha256:##')" ] || { echo "check-erc-fresh: STALE -- newest place-and-route record's GDS is not the one ERC checked; run scripts/erc-regen.sh" >&2; exit 3; }

# Run from the record dir: `klt erc --check` resolves the report's spec path
# against the report, while the GDS is echoed repo-scoped.
args=(--check erc.report.json)
[ "${1:-}" = "--rerun" ] && args+=(--rerun)
(cd "$EREC" && "${KLT[@]}" erc "${args[@]}")
rc=$?
case $rc in
  0) echo "check-erc-fresh: OK -- ${EREC#"$ROOT"/} matches its inputs" ;;
  3) echo "check-erc-fresh: STALE -- run scripts/erc-regen.sh and commit" >&2 ;;
  *) echo "check-erc-fresh: klt erc --check failed (exit $rc)" >&2 ;;
esac
exit $rc
