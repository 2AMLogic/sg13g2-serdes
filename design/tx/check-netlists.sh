#!/usr/bin/env bash
# Export (default) or staleness-check (--check) the TX netlists with klt netlist.
#   design/tx/check-netlists.sh          regenerate every netlist from its schematic
#   design/tx/check-netlists.sh --check  exit 0 if all match, 3 if any drifted
# Netlists are exported as includable blocks (--block). Never calls raw xschem. Needs the repo env: scripts/setup-env.sh once, then this
# script sources scripts/env.sh itself.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=/dev/null
. "$ROOT/scripts/env.sh"
MODE=()
[ "${1:-}" = "--check" ] && MODE=(--check)
rc=0
for sch in "$ROOT"/design/tx/*.sch; do
  cell="$(basename "$sch" .sch)"
  klt netlist "$sch" -o "$ROOT/design/tx/netlists/$cell.spice" \
      --rcfile "$ROOT/design/xschemrc" --block "${MODE[@]}" >/dev/null 2>"${TMPDIR:-/tmp}/netlist-$cell.err"
  s=$?
  if [ $s -ne 0 ]; then
    echo "$cell: exit $s"; rc=$s
  else
    echo "$cell: ok"
  fi
done
exit $rc
